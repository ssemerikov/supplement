#!/usr/bin/env python3
"""
03_tier2_forecast.py — build and elicit the Tier-2 synthetic-panel forecast

Tier 2 is the contamination-immune tier of the pre-registered two-tier criterion
(docs/preregistration.md §7.1): the synthetic panel forecasts the results of THIS paper's CFA
before that CFA is run, and is scored by Brier skill against the outcome. Because the analysis has
never been run, its results exist in no training corpus.

BINDING SEQUENCING: the forecast must be elicited and time-stamped BEFORE any CFA touches the real
data. If the CFA runs first, Tier 2 is void and must be reported as void.

The propositions are generated from the FROZEN item table, not hardcoded, so the instrument cannot
drift from what was registered. The table's SHA-256 is embedded in the output and checked against
the value registered at OSF.

Two stages, deliberately separated:

    python3 code/03_tier2_forecast.py build     # write the instrument; no network calls
    python3 code/03_tier2_forecast.py elicit    # call endpoints; writes the timestamped forecast

`build` is safe and idempotent. `elicit` is the irreversible step: it produces the artefact whose
timestamp is the evidence, and it should be followed immediately by uploading that artefact to the
OSF project for an independent timestamp.

WAVES AND THE REPLICATION GATE. `--wave` selects the elicitation wave (1 = original, 2 = the
registered temporal replication) and lands in both the artefact's filename and its `wave` field.
Wave 2 and above are REFUSED until REPLICATION_MIN_DAYS have elapsed since the previous wave's own
elicitation, measured from that wave's primary run and never from a top-up. The refusal happens
before any network call, so it costs nothing and elicits nothing, and there is no override flag:
the registration reports a short interval as a FAILED replication rather than a shorter one, so an
early run does not save time, it destroys the check. Re-running `--wave 1` once wave 1 exists is
refused for the same reason -- a second wave-1 artefact would corrupt the record. A replication
wave is also refused if the instrument is no longer byte-identical to the one the prior wave was
elicited with, since a re-run of a drifted instrument replicates nothing. On success the
artefact carries a `replication` block recording the anchor file, the prior timestamp, the
registered minimum and the realised gap, so the interval is auditable from the artefact alone.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEM_TABLE = ROOT / "docs" / "design" / "item-table-v2-joint-names.md"
OUT_DIR = ROOT / "supplement" / "tier2-forecast"

# The hash registered at OSF (https://osf.io/ezjh2/, registration v1, 2026-08-10 07:45:39 UTC).
REGISTERED_ITEM_TABLE_SHA256 = "2c9e0b7f215c925c2e9fc38aa164e53edcb3c390df251869b694e48aed144de5"

# Loading threshold the per-item forecasts resolve against. Fixed here, before elicitation,
# and distinct from the .30 item-retention rule in the pre-registration.
LOADING_THRESHOLD = 0.40

# Registered temporal-replication interval (docs/preregistration.md §7.2, check 2). Wave 2 may not
# be elicited until 30 days after wave 1. The registration's wording makes this a gate rather than
# a guideline: "Eliciting wave 2 early voids the check — an interval shorter than the registered
# 30 days is reported as a failed replication, not as a shorter one." There is deliberately NO
# override flag, per CLAUDE.md: the gate is enforced in code, not by memory, and must not be
# loosened to make a script run. A day short is not nearly enough; it is a void check.
REPLICATION_MIN_DAYS = 30

DEFS = """D1 individualism <-> collectivism: is the ultimate bearer of claims and responsibility the
individual person or the collective?
D2 altruism <-> egoism: is concern directed outward, to others, or inward, to the self?
D3 institutional respect <-> anti-institutional personalism: respect for impersonal rules and
democratic institutions, versus reliance on persons over institutions. Its negative pole is
leader-principle preference, not low institutional trust.

SCORING DIRECTION — this fixes the sign of every correlation you forecast:
  HIGH on D1 = individualist (low = collectivist)
  HIGH on D2 = altruistic    (low = egoistic)
  HIGH on D3 = institutional respect (low = anti-institutional personalism)
All reverse-keyed indicators are reverse-scored BEFORE estimation, so every item loads positively
on its assigned factor if it behaves as intended. A latent correlation is therefore positive when,
for example, more individualist countries are also more altruistic."""

# Independent draws: one fresh context per persona. Never one conversation emitting many answers.
#
# The pre-registration (§7.2) requires a perturbation grid of >=3 phrasings x >=2 persona detail
# levels x >=2 temperatures x >=3 model families, and requires the DISTRIBUTION to be reported
# rather than a point estimate. The three axes below supply the first two; TEMPERATURES and
# ENDPOINTS supply the rest.

# Axis 1 — persona, at two detail levels. "terse" is a bare role; "rich" adds standpoint and
# priors, which is the manipulation the grid is meant to detect.
PERSONAS = [
    {"key": "psychometrician",
     "terse": "a psychometrician",
     "rich": "a psychometrician specialising in confirmatory factor analysis and measurement "
             "invariance, who has seen many three-factor models collapse into one under scrutiny "
             "and expects cross-national scalar invariance to fail"},
    {"key": "comparativist",
     "terse": "a comparative political scientist",
     "rich": "a comparative political scientist working on European public opinion and democratic "
             "attitudes, familiar with how the EVS/WVS democracy battery behaves in "
             "post-communist versus Western European samples"},
    {"key": "methodologist",
     "terse": "a survey methodologist",
     "rich": "a survey methodologist specialising in cross-national item performance, who pays "
             "close attention to response format, item wording and battery position effects"},
    {"key": "cross_cultural",
     "terse": "a cross-cultural psychologist",
     "rich": "a cross-cultural psychologist working on values, individualism and collectivism, "
             "familiar with Schwartz's circumplex and Welzel's emancipative values"},
    {"key": "sociologist",
     "terse": "a sociologist of morality",
     "rich": "a sociologist of morality who works directly with EVS and WVS microdata and knows "
             "the justifiability battery's floor and ceiling behaviour in European samples"},
    {"key": "sceptic",
     "terse": "a quantitative methodologist",
     "rich": "a quantitative methodologist sceptical of latent-variable models, who thinks most "
             "reported factor structures are response-format artefacts and expects this one to be "
             "no different"},
]
PERSONA_DETAIL_LEVELS = ("terse", "rich")

# Axis 2 — three framings of the same request. Same propositions, same scoring direction; only the
# framing of the forecaster's task differs. If the forecasts move with framing, that is the finding.
PHRASINGS = {
    "neutral": (
        "You are {persona}, acting as an independent forecaster. You are being asked to predict the "
        "numerical results of a confirmatory factor analysis that has NOT yet been run. Nobody knows "
        "the answers, including the researchers. Forecast from your substantive expertise about how "
        "these survey items behave in European samples.\n"
        "Be calibrated, not agreeable. Probabilities near 0.5 are appropriate where you are genuinely "
        "uncertain, and confident probabilities are appropriate where you are not. A forecaster who "
        "says 0.9 to everything is useless. Some of these items will fail.\n"
        "Reply with exactly one fenced ```json block and nothing else."
    ),
    "adversarial": (
        "You are {persona}. A research team claims these survey items measure three separable "
        "dimensions. You are not on that team and you have no stake in their being right. Your task "
        "is to forecast what their analysis will actually show, not what they hope it will show.\n"
        "Measurement models fail often. Items cross-load, factors collapse into one, and invariance "
        "rarely holds across dozens of countries. Say so where you expect it, with low probabilities. "
        "Uniformly high probabilities would mean you are not thinking.\n"
        "Reply with exactly one fenced ```json block and nothing else."
    ),
    "betting": (
        "You are {persona}. Treat each statement below as a proposition you must price for a "
        "prediction market with real money at stake, resolving when the analysis is run. You are paid "
        "for accuracy and penalised for overconfidence in either direction.\n"
        "Give the probability you would actually bet at. Where the evidence genuinely does not "
        "discriminate, price near 0.5; where it does, commit.\n"
        "Reply with exactly one fenced ```json block and nothing else."
    ),
}




# ----------------------------------------------------------------------------- instrument


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_item_table(path: Path) -> list[dict]:
    """Extract the frozen item table. Format: | ID | Sphere | Joint name | was | Label | Key | Valid |"""
    items, dim = [], None
    for line in path.read_text().splitlines():
        m = re.match(r"^## \d+\. (D[123]) —", line)
        if m:
            dim = m.group(1)
            continue
        if line.startswith("|") and dim:
            c = [x.strip() for x in line.strip("|").split("|")]
            if len(c) == 7 and re.match(r"^D[123]-", c[0]):
                items.append({
                    "item_id": c[0],
                    "dimension": dim,
                    "sphere": c[1],
                    "variable": re.sub(r"[*`]", "", c[2]),
                    "label": re.sub(r"[*`\\]", "", c[4]),
                    "reverse": "R" in re.sub(r"[*`]", "", c[5]),
                })
    if not items:
        raise SystemExit(f"parsed 0 items from {path} — the table format changed; fix the parser")
    return items


def build_propositions(items: list[dict]) -> dict:
    """Every forecast target, each objectively resolvable from the pre-registered analysis."""
    a = [{
        "id": f"A-{it['item_id']}",
        "block": "A_item_loading",
        "text": (f"In the configural three-factor model M2, item {it['variable']} "
                 f"(\"{it['label']}\") will have a standardised loading of at least "
                 f"{LOADING_THRESHOLD:.2f} on its assigned factor {it['dimension']}."),
        "variable": it["variable"], "assigned": it["dimension"],
        "resolves_from": "M2 configural standardised loadings",
    } for it in items]

    b = [
        ("B-H1", "H1 will be supported: all three of (a) M1 beats M0 by dCFI >= .010, "
                 "(b) M1b rejected against M1 at alpha = .01, (c) phi(D1,D2) <= .85."),
        ("B-H1a", "M1 (two factors) will beat M0 (one factor) by dCFI >= .010."),
        ("B-H1c", "The estimated phi(D1,D2) will be <= .85."),
        ("B-H2", "H2 will be supported: M2b rejected against M2 at alpha = .01 AND phi(D1,D3) <= .70."),
        ("B-H2c", "The estimated phi(D1,D3) will be <= .70."),
        ("B-H3b", "IDV and Welzel's index will both fall inside the +/-0.20 equivalence bound on D2."),
        ("B-H4", "For at least two of the three Jellyby probes, a two-factor solution "
                 "(concrete vs anonymous) will beat a one-factor solution."),
        ("B-FIT", "The target model M2 will reach CFI >= .95 in the pooled configural model."),
    ]
    c = [
        ("C-METRIC", "Metric invariance will hold across the 39 countries (dCFI <= .010)."),
        ("C-SCALAR", "Scalar invariance will hold across the 39 countries (dCFI <= .010)."),
        ("C-ALIGN", "At least one dimension will fail the alignment recovery check and therefore "
                    "have NO country means reported."),
    ]
    return {
        "block_A": a,
        "block_B": [{"id": i, "block": "B_hypothesis", "text": t} for i, t in b],
        "block_C": [{"id": i, "block": "C_invariance", "text": t} for i, t in c],
        "block_D": [{"id": "D-PHI12", "block": "D_parameter",
                     "text": "Point forecast for phi(D1,D2), the latent correlation between D1 and D2."},
                    {"id": "D-PHI13", "block": "D_parameter",
                     "text": "Point forecast for phi(D1,D3)."},
                    {"id": "D-PHI23", "block": "D_parameter",
                     "text": "Point forecast for phi(D2,D3)."}],
    }


PREAMBLE = [
    "TASK. Forecast the results of a confirmatory factor analysis that has not yet been run.",
    "", "THE MODEL BEING FITTED", DEFS, "",
    "Data: Joint EVS/WVS 2017-2022, 39 European countries, ~77,000 respondents.",
    "Estimator: WLSMV with ordinal indicators. The target model M2 has three correlated",
    "factors plus an orthogonal method factor for the nine 'essential characteristics of",
    "democracy' items (E224-E233B).", "",
]


def render_prompts(props: dict) -> dict[str, str]:
    """Two prompts, elicited as separate independent calls.

    The smoke test showed why: asked for all 66 forecasts in one call, a model completed the
    52-item block A and silently dropped blocks B and C — the hypothesis-level forecasts, which
    are the ones that matter most. Splitting guarantees the short blocks are never crowded out by
    the long one.
    """
    a = PREAMBLE + [
        f"Give your probability (0.00-1.00) that each statement below will turn out TRUE.",
        f"There are {len(props['block_A'])} statements and you must answer every one.", "",
    ]
    a += [f"{p['id']}  {p['text']}" for p in props["block_A"]]
    a += ["", "Return ONLY:", '{"probabilities":[{"id":"A-D1-P1","p":0.00}]}',
          f"Exactly {len(props['block_A'])} entries, in the order listed."]

    short = props["block_B"] + props["block_C"]
    b = PREAMBLE + [
        "PART 1. Give your probability (0.00-1.00) that each statement will turn out TRUE.", "",
    ]
    b += [f"{p['id']}  {p['text']}" for p in short]
    b += ["", "PART 2. Give a point forecast and an 80% interval for each latent correlation.",
          "Correlations lie in [-1, 1]. Mind the scoring direction stated above when choosing signs.",
          ""]
    b += [f"{p['id']}  {p['text']}" for p in props["block_D"]]
    b += ["", "Return ONLY:", '{"probabilities":[{"id":"B-H1","p":0.00}],',
          ' "parameters":[{"id":"D-PHI12","point":0.00,"lo80":0.00,"hi80":0.00}]}',
          f"Exactly {len(short)} probabilities and {len(props['block_D'])} parameters."]
    return {"A": "\n".join(a), "B": "\n".join(b)}


def expected_ids(props: dict) -> dict[str, set]:
    return {
        "A": {p["id"] for p in props["block_A"]},
        "B": {p["id"] for p in props["block_B"] + props["block_C"]},
        "D": {p["id"] for p in props["block_D"]},
    }


def check_draw(part: str, response, exp: dict[str, set]) -> dict:
    """Completeness is data. An incomplete draw is recorded as incomplete, never silently used."""
    if not isinstance(response, dict) or "__err" in response:
        return {"ok": False, "reason": "call failed", "missing": []}
    got = {x["id"] for x in response.get("probabilities", [])
           if isinstance(x, dict) and "id" in x and isinstance(x.get("p"), (int, float))}
    want = exp["A"] if part == "A" else exp["B"]
    missing = sorted(want - got)
    extra = sorted(got - want)
    out = {"ok": not missing, "missing": missing, "extra": extra,
           "n_got": len(got), "n_want": len(want)}
    if part == "B":
        pars = {x["id"] for x in response.get("parameters", [])
                if isinstance(x, dict) and "id" in x}
        out["missing_parameters"] = sorted(exp["D"] - pars)
        out["ok"] = out["ok"] and not out["missing_parameters"]
    if not out["ok"]:
        out["reason"] = "incomplete"
    return out


# ----------------------------------------------------------------------------- endpoints

OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
OMNI = os.environ.get("OMNI_URL", "http://localhost:20128/v1/chat/completions")
OMNI_KEY = os.environ.get("OMNI_KEY", "")

ENDPOINTS = [
    ("ollama", "gpt-oss:120b-cloud"),
    ("ollama", "gemma4:31b-cloud"),
    ("omniroute", "kiro/claude-sonnet-4.5"),
    ("omniroute", "kiro/claude-haiku-4.5"),
    ("omniroute", "kiro/glm-5"),
    ("omniroute", "kiro/deepseek-3.2"),
]


def _post(url: str, payload: dict, headers: dict, timeout: int = 900) -> str:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode()


def _sse(raw: str) -> str:
    out = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        body = line[5:].strip()
        if body == "[DONE]":
            break
        try:
            chunk = json.loads(body)
        except json.JSONDecodeError:
            continue
        for ch in chunk.get("choices", []):
            piece = (ch.get("delta") or {}).get("content")
            if piece:
                out.append(piece)
    return "".join(out)


def _chat_text(raw: str) -> str:
    """The assistant's text from an OpenAI-compatible reply, streamed or not.

    The request never asks for streaming, so which shape comes back is a property of the proxy,
    not of this code: omniroute answered wave 1 in server-sent events and wave 2 in a plain
    completion object. Wave 2 lost all 96 of its omniroute draws because `_sse` was applied
    unconditionally and returned "" for a body with no `data:` lines -- a complete, valid forecast
    discarded by the parser. Accept whichever shape arrives.
    """
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError:
        return _sse(raw)                                  # SSE stream, or something unparseable
    if isinstance(doc, dict) and doc.get("choices"):
        ch = doc["choices"][0]
        return (ch.get("message") or ch.get("delta") or {}).get("content") or ""
    return _sse(raw)


def _extract_json(text: str):
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    cands = [m.group(1)] if m else []
    i = text.find("{")
    if i != -1:
        cands.append(text[i:text.rfind("}") + 1])
    for c in cands:
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            pass
    return None


def call(channel: str, model: str, system: str, prompt: str, temperature: float, seed: int):
    msgs = [{"role": "system", "content": system},
            {"role": "user", "content": prompt}]
    try:
        if channel == "ollama":
            # num_predict must be generous: reasoning models spend budget on the thinking channel
            # and return an empty message.content if it is too small.
            raw = _post(OLLAMA, {"model": model, "messages": msgs, "stream": False, "think": False,
                                 "options": {"temperature": temperature, "seed": seed,
                                             "num_predict": 8192}},
                        {"Content-Type": "application/json"})
            return _extract_json(json.loads(raw).get("message", {}).get("content", ""))
        hdr = {"Content-Type": "application/json"}
        if OMNI_KEY:
            hdr["Authorization"] = f"Bearer {OMNI_KEY}"
        raw = _post(OMNI, {"model": model, "messages": msgs,
                           "temperature": temperature, "max_tokens": 8192}, hdr)
        text = _chat_text(raw)
        got = _extract_json(text)
        if got is None:
            # Record what came back. A bare None reaches the artefact as "call failed", which is
            # indistinguishable from a dead endpoint and cost wave 2 an investigation to tell apart.
            return {"__err": "unparseable reply: " + repr((text or raw)[:160])}
        return got
    except Exception as e:  # noqa: BLE001 - failures are data and must be recorded, not raised
        return {"__err": f"{type(e).__name__}: {str(e)[:120]}"}


# ----------------------------------------------------------------------------- commands


def cmd_build(args) -> int:
    live = sha256(ITEM_TABLE)
    print(f"item table : {ITEM_TABLE.relative_to(ROOT)}")
    print(f"  sha256   : {live}")
    if live == REGISTERED_ITEM_TABLE_SHA256:
        print("  MATCHES the hash registered at OSF.")
    else:
        print("  *** DOES NOT MATCH the registered hash ***")
        print(f"  registered: {REGISTERED_ITEM_TABLE_SHA256}")
        print("  The frozen table has changed since registration. Stop and disclose this")
        print("  before eliciting any forecast.")
        return 1

    items = parse_item_table(ITEM_TABLE)
    props = build_propositions(items)
    n = sum(len(v) for v in props.values())
    by_dim = {d: sum(1 for i in items if i["dimension"] == d) for d in ("D1", "D2", "D3")}
    print(f"\nitems parsed: {len(items)}  {by_dim}")
    print(f"propositions: {n}  "
          f"(A {len(props['block_A'])}, B {len(props['block_B'])}, "
          f"C {len(props['block_C'])}, D {len(props['block_D'])})")

    prompts = render_prompts(props)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inst = {
        "instrument_version": 2,
        "built_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "item_table_sha256": live,
        "registered_item_table_sha256": REGISTERED_ITEM_TABLE_SHA256,
        "loading_threshold": LOADING_THRESHOLD,
        "osf": "https://osf.io/ezjh2/",
        "propositions": props,
        "prompts": prompts,
        "personas": PERSONAS,
        "persona_detail_levels": list(PERSONA_DETAIL_LEVELS),
        "phrasings": PHRASINGS,
        "temperatures": list(args.temperatures),
        "endpoints": [f"{c}:{m}" for c, m in ENDPOINTS],
        "perturbation_grid": {
            "phrasings": len(PHRASINGS),
            "persona_detail_levels": len(PERSONA_DETAIL_LEVELS),
            "temperatures": len(args.temperatures),
            "model_families": len({m.split("/")[-1].split("-")[0] for _, m in ENDPOINTS}),
            "registered_minimum": ">=3 phrasings x >=2 persona detail levels x "
                                  ">=2 temperatures x >=3 model families",
        },
        "changelog": [
            "v2: split into two prompts (A = 52 item loadings, B = 14 hypothesis/invariance/"
            "parameter forecasts). A v1 smoke test showed a model completing block A and silently "
            "dropping blocks B and C.",
            "v2: added an explicit scoring-direction statement. A v1 smoke test produced "
            "phi(D1,D2) forecasts of -0.30 and +0.55 from the same model, because the sign "
            "convention was undefined.",
            "v2: draws are validated for completeness and retried; incomplete draws are recorded "
            "as incomplete rather than silently averaged.",
        ],
    }
    p = OUT_DIR / "tier2-instrument.json"
    p.write_text(json.dumps(inst, indent=1, ensure_ascii=False))
    for k, v in prompts.items():
        (OUT_DIR / f"tier2-prompt-{k}.txt").write_text(v)
    print(f"\nwrote {p.relative_to(ROOT)}  (sha256 {sha256(p)[:16]}…)")
    print(f"wrote tier2-prompt-A.txt ({len(prompts['A'].splitlines())} lines), "
          f"tier2-prompt-B.txt ({len(prompts['B'].splitlines())} lines)")
    fams = sorted({m.split("/")[-1].split("-")[0] for _, m in ENDPOINTS})
    cells = len(PHRASINGS) * len(PERSONA_DETAIL_LEVELS) * len(args.temperatures) * len(ENDPOINTS)
    print(f"\nperturbation grid (registered minimum in brackets):")
    print(f"  phrasings             {len(PHRASINGS)}  [>=3]  {sorted(PHRASINGS)}")
    print(f"  persona detail levels {len(PERSONA_DETAIL_LEVELS)}  [>=2]  "
          f"{list(PERSONA_DETAIL_LEVELS)}")
    print(f"  temperatures          {len(args.temperatures)}  [>=2]  {args.temperatures}")
    print(f"  model families        {len(fams)}  [>=3]  {fams}")
    print(f"  personas rotated across cells: {len(PERSONAS)}")
    print(f"\nplanned draws at elicit: {cells} cells x 2 parts = {cells * 2}")
    print("No network calls were made. Run `elicit` when ready.")
    return 0


def _is_rate_limit(out) -> bool:
    return isinstance(out, dict) and "429" in str(out.get("__err", ""))


def _draw_runner(inst: dict, exp: dict, retries: int):
    """One independent draw, retried on incompleteness.

    Wave 1 lost 41 of 144 draws to HTTP 429 because the three attempts fired back to back
    against a rate-limited endpoint. A rate limit is a property of the transport, not of the
    model's forecast, so it is retried with exponential backoff and jitter rather than
    recorded as a refusal. Every attempt is still written to the artefact.
    """
    def run(job):
        c, m, ph, detail, persona, t, part = job
        system = PHRASINGS[ph].format(persona=persona[detail])
        attempts = []
        for k in range(retries):
            started = dt.datetime.now(dt.timezone.utc).isoformat()
            out = call(c, m, system, inst["prompts"][part], t,
                       seed=1000 + hash((persona["key"], ph, detail)) % 9000 + 97 * k)
            chk = check_draw(part, out, exp)
            attempts.append({"attempt": k + 1, "started_utc": started,
                             "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                             "check": chk, "response": out})
            if chk["ok"]:
                break
            if _is_rate_limit(out) and k + 1 < retries:
                time.sleep(min(60.0, 5.0 * 2 ** k) + random.uniform(0, 5))
        return {"channel": c, "model": m, "phrasing": ph, "persona_detail": detail,
                "persona_key": persona["key"], "persona_text": persona[detail],
                "temperature": t, "part": part,
                "accepted": attempts[-1]["check"]["ok"],
                "n_attempts": len(attempts), "attempts": attempts,
                "response": attempts[-1]["response"]}
    return run


def _prior_wave(wave: int) -> tuple[Path, dict]:
    """The primary elicitation of the wave before this one.

    Top-ups are excluded deliberately. A top-up repairs cells its parent lost and inherits the
    parent's wave number, so it is a repair of an elicitation rather than a new one; anchoring the
    interval on a top-up would silently move a date that is registered at OSF.
    """
    cands = []
    for path in sorted(OUT_DIR.glob("tier2-forecast-wave*.json")):
        try:
            d = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if d.get("wave") == wave - 1 and d.get("run") != "topup" and d.get("elicited_utc"):
            cands.append((d["elicited_utc"], path, d))
    if not cands:
        raise SystemExit(
            f"--wave {wave} measures its replication interval from wave {wave - 1}, and no "
            f"completed wave-{wave - 1} elicitation was found in {OUT_DIR.relative_to(ROOT)}")
    cands.sort()
    _, path, payload = cands[0]
    return path, payload


def _gap_guard(args, inst_path: Path) -> dict | None:
    """Refuse to elicit a replication wave early, or with an instrument that has changed.

    Two conditions, both registered in docs/preregistration.md §7.2 check 2: the interval since
    the prior wave must reach REPLICATION_MIN_DAYS, and the instrument must be byte-identical to
    the one that wave was elicited with. A replication run on a drifted instrument is not a
    temporal replication of anything.

    Returns a provenance block to embed in the artefact, or None for wave 1 and smoke runs.
    Called before any network request, so a refusal costs nothing and elicits nothing.
    """
    if args.smoke:
        return None                      # a smoke run is a connectivity check, not a wave
    if args.wave < 1:
        raise SystemExit("--wave must be 1 or greater")

    if args.wave == 1:
        existing = sorted(p.name for p in OUT_DIR.glob("tier2-forecast-wave1-*.json")
                          if "topup" not in p.name)
        if existing:
            raise SystemExit(
                f"wave 1 has already been elicited ({existing[0]}). Re-running it would put a "
                "second wave-1 artefact in the record. Use --wave 2 for the temporal "
                "replication, or `topup --parent <file>` to repair cells a run lost.")
        return None

    path, prev = _prior_wave(args.wave)
    t0 = dt.datetime.fromisoformat(prev["elicited_utc"])
    now = dt.datetime.now(dt.timezone.utc)
    elapsed = now - t0
    floor = t0 + dt.timedelta(days=REPLICATION_MIN_DAYS)
    if now < floor:
        short = floor - now
        raise SystemExit(
            f"REFUSING to elicit wave {args.wave}.\n"
            f"  registered interval : {REPLICATION_MIN_DAYS} days\n"
            f"  wave {args.wave - 1} elicited     : {t0:%Y-%m-%d %H:%M:%S UTC}  ({path.name})\n"
            f"  elapsed             : {elapsed.days} days, {elapsed.seconds // 3600} h\n"
            f"  earliest permitted  : {floor:%Y-%m-%d %H:%M:%S UTC}\n"
            f"  short by            : {short.days} days, {short.seconds // 3600} h, "
            f"{(short.seconds % 3600) // 60} min\n"
            "docs/preregistration.md §7.2: 'Eliciting wave 2 early voids the check — an interval "
            "shorter than the registered 30 days is reported as a failed replication, not as a "
            "shorter one.' There is no override flag. Waiting is the only correct action.")

    live_inst = sha256(inst_path)
    if live_inst != prev.get("instrument_sha256"):
        raise SystemExit(
            f"REFUSING to elicit wave {args.wave}.\n"
            f"  wave {args.wave - 1} instrument : {prev.get('instrument_sha256')}  ({path.name})\n"
            f"  instrument now     : {live_inst}\n"
            "docs/preregistration.md §7.2 check 2: 'Wave 2 re-runs the identical instrument\n"
            "(instrument_sha256 must match, and the script refuses to proceed if it does not).'\n"
            "Re-running `build` rewrites the instrument and is what usually causes this. Restore\n"
            "the prior instrument, or disclose the change and report the replication as void.")

    return {"prior_wave": args.wave - 1,
            "prior_file": path.name,
            "prior_elicited_utc": prev["elicited_utc"],
            "prior_instrument_sha256": prev.get("instrument_sha256"),
            "instrument_unchanged": True,
            "registered_min_days": REPLICATION_MIN_DAYS,
            "realised_gap_days": round(elapsed.total_seconds() / 86400, 3)}


def cmd_elicit(args) -> int:
    inst_path = OUT_DIR / "tier2-instrument.json"
    if not inst_path.exists():
        raise SystemExit("run `build` first")
    inst = json.loads(inst_path.read_text())

    live = sha256(ITEM_TABLE)
    if live != REGISTERED_ITEM_TABLE_SHA256:
        raise SystemExit("item table no longer matches the registered hash — stop and disclose")

    # Before any network call: a replication wave elicited early is a void check, not a short one.
    prov = _gap_guard(args, inst_path)
    if prov:
        print(f"replication interval OK: {prov['realised_gap_days']} days since wave "
              f"{prov['prior_wave']} (registered minimum {prov['registered_min_days']})")

    exp = expected_ids(inst["propositions"])
    jobs, cell = [], 0
    for c, m in ENDPOINTS:
        for ph in sorted(PHRASINGS):
            for detail in PERSONA_DETAIL_LEVELS:
                for t in args.temperatures:
                    # Personas rotate across cells so all six appear without multiplying the grid.
                    persona = PERSONAS[cell % len(PERSONAS)]
                    cell += 1
                    for part in ("A", "B"):
                        jobs.append((c, m, ph, detail, persona, t, part))
    if args.smoke:
        jobs = jobs[:args.smoke]
    print(f"eliciting {len(jobs)} independent draws "
          f"({'SMOKE TEST' if args.smoke else 'full run'}), up to {args.retries} attempts each…")

    run = _draw_runner(inst, exp, args.retries)
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(run, jobs))

    ok = [r for r in results if r["accepted"]]
    print(f"  complete draws: {len(ok)}/{len(results)}   "
          f"(retried: {sum(1 for r in results if r['n_attempts'] > 1)})")
    for r in results:
        if r["accepted"]:
            continue
        chk = r["attempts"][-1]["check"]
        print(f"  REJECTED {r['channel']}:{r['model']} {r['phrasing']}/{r['persona_detail']} "
              f"T{r['temperature']} part {r['part']} -> {chk.get('reason')} "
              f"({chk.get('n_got','?')}/{chk.get('n_want','?')}, "
              f"missing {chk.get('missing', [])[:5]})")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"tier2-forecast-{'smoke' if args.smoke else f'wave{args.wave}'}-{stamp}.json"
    payload = {
        "elicited_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "wave": "smoke" if args.smoke else args.wave,
        "instrument_sha256": sha256(inst_path),
        "item_table_sha256": live,
        "osf": "https://osf.io/ezjh2/",
        **({"replication": prov} if prov else {}),
        "n_attempted": len(results), "n_complete": len(ok),
        "n_retried": sum(1 for r in results if r["n_attempts"] > 1),
        "draws": results,
    }
    out_path = OUT_DIR / name
    out_path.write_text(json.dumps(payload, indent=1, ensure_ascii=False))
    digest = sha256(out_path)
    print(f"\nwrote {out_path.relative_to(ROOT)}")
    print(f"  sha256 {digest}")
    if not args.smoke:
        print("\n*** NEXT STEP, DO NOT SKIP ***")
        print("Upload this file to https://osf.io/byjn2/ now, to obtain an independent timestamp")
        print("(byjn2 is the writable parent project. ezjh2 is the REGISTRATION and is a frozen")
        print(" archive -- it has no upload control. See docs/osf-deposit-instructions.md.)")
        print("that precedes the CFA. Record the file's OSF URL and this SHA-256 in")
        print("docs/preregistration.md §7.1. Until that is done the Tier-2 timing claim rests")
        print("only on local filesystem timestamps, which are not evidence.")
    return 0


def cmd_topup(args) -> int:
    """Re-run only the cells a previous run failed to complete.

    The parent artefact is NEVER modified: it keeps its own timestamp and SHA-256, and this
    writes a separate file that names it as parent. Both go to the supplement, so the record
    shows what failed, when, and what the re-run returned. Merging them into one file would
    erase the failures, which are themselves reportable data about the instrument.

    This is not a second bite at the forecast: only cells with no accepted draw are re-run,
    and an already-accepted forecast can never be replaced by a later one.
    """
    parent = Path(args.parent)
    if not parent.is_absolute():
        parent = ROOT / parent
    prev = json.loads(parent.read_text())

    inst_path = OUT_DIR / "tier2-instrument.json"
    inst = json.loads(inst_path.read_text())
    if sha256(inst_path) != prev["instrument_sha256"]:
        raise SystemExit("instrument has changed since the parent run — a top-up would not be "
                         "the same instrument; disclose and start a new wave instead")
    live = sha256(ITEM_TABLE)
    if live != REGISTERED_ITEM_TABLE_SHA256:
        raise SystemExit("item table no longer matches the registered hash — stop and disclose")

    exp = expected_ids(inst["propositions"])
    personas = {p["key"]: p for p in PERSONAS}
    jobs = [(d["channel"], d["model"], d["phrasing"], d["persona_detail"],
             personas[d["persona_key"]], d["temperature"], d["part"])
            for d in prev["draws"] if not d["accepted"]]
    if args.only_model:
        jobs = [j for j in jobs if j[1] in args.only_model]
    if not jobs:
        print("nothing to top up — every cell in the parent was accepted")
        return 0

    print(f"parent   {parent.relative_to(ROOT)}")
    print(f"  sha256 {sha256(parent)}")
    print(f"re-running {len(jobs)} rejected cells with {args.workers} worker(s), "
          f"up to {args.retries} attempts each, backing off on 429…")

    run = _draw_runner(inst, exp, args.retries)
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(run, jobs))

    ok = [r for r in results if r["accepted"]]
    print(f"  recovered: {len(ok)}/{len(results)}")
    for r in results:
        if r["accepted"]:
            continue
        chk = r["attempts"][-1]["check"]
        err = r["attempts"][-1]["response"]
        err = err.get("__err", "") if isinstance(err, dict) else ""
        print(f"  STILL REJECTED {r['model']} {r['phrasing']}/{r['persona_detail']} "
              f"T{r['temperature']} part {r['part']} -> {chk.get('reason')} {err}")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "elicited_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "wave": prev["wave"], "run": "topup",
        "parent_file": parent.name, "parent_sha256": sha256(parent),
        "instrument_sha256": prev["instrument_sha256"],
        "item_table_sha256": live,
        "osf": "https://osf.io/ezjh2/",
        "n_attempted": len(results), "n_complete": len(ok),
        "n_retried": sum(1 for r in results if r["n_attempts"] > 1),
        "draws": results,
    }
    out_path = OUT_DIR / f"tier2-forecast-wave{prev['wave']}-topup-{stamp}.json"
    out_path.write_text(json.dumps(payload, indent=1, ensure_ascii=False))
    print(f"\nwrote {out_path.relative_to(ROOT)}")
    print(f"  sha256 {sha256(out_path)}")
    print("\nDeposit this file at https://osf.io/byjn2/ ALONGSIDE the parent file, not instead of it.")
    print("(byjn2, not ezjh2: the registration is frozen. docs/osf-deposit-instructions.md)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="write the instrument; no network calls")
    b.add_argument("--temperatures", type=float, nargs="+", default=[0.3, 1.0])
    b.set_defaults(func=cmd_build)
    e = sub.add_parser("elicit", help="call endpoints and write the timestamped forecast")
    e.add_argument("--temperatures", type=float, nargs="+", default=[0.3, 1.0])
    e.add_argument("--workers", type=int, default=8)
    e.add_argument("--retries", type=int, default=3,
                   help="attempts per draw before recording it as incomplete")
    e.add_argument("--wave", type=int, default=1,
                   help="which elicitation wave this is (1 = original, 2 = temporal "
                        "replication). Wave 2+ is refused until the registered 30-day "
                        "interval has elapsed; there is no override.")
    e.add_argument("--smoke", type=int, default=0,
                   help="run only the first N draws, as a connectivity check")
    e.set_defaults(func=cmd_elicit)
    t = sub.add_parser("topup", help="re-run only the cells a previous run failed to complete")
    t.add_argument("--parent", required=True,
                   help="the forecast JSON whose rejected cells are to be re-run")
    t.add_argument("--only-model", nargs="+", default=None,
                   help="restrict the re-run to these model ids")
    t.add_argument("--workers", type=int, default=2,
                   help="keep this low: wave 1's losses were all rate limits")
    t.add_argument("--retries", type=int, default=5)
    t.set_defaults(func=cmd_topup)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
