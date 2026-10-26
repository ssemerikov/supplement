#!/usr/bin/env python3
"""Summarise the Tier-2 synthetic-panel forecast.

    python3 code/04_tier2_summarise.py supplement/tier2-forecast/tier2-forecast-wave1-*.json \
                                       supplement/tier2-forecast/tier2-forecast-wave1-topup-*.json

Reads one or more forecast artefacts, merges them by CELL (a cell already accepted in an earlier
file is never replaced by a later draw), and reports the DISTRIBUTION of each forecast across the
perturbation grid. Pre-registration §7.2 check 1 requires the distribution, not a point estimate,
so no grand mean is printed anywhere in this script's output.

Reads only. Writes nothing, calls nothing, and does not touch the real survey data — running it
before the CFA cannot compromise the Tier-2 timing claim.

ON THE HOMOGENISATION CHECK (§7.2 check 3). As filed, the registration asks for a "variance ratio
against the human comparison distribution". Decision 1 in docs/design/DECISIONS.md had already
taken the human panel off the critical path, so no human distribution exists for this study and
the ratio is not computable as worded. That conditional was explicit in the pre-filing design
document (delphi-design.md §9.8: "VR is only computable where a human distribution exists. Where
it does not, report the entropy distribution alone and say so — do not fabricate a comparison")
and was lost when the check was compressed for filing. This script therefore reports the
between-model / within-model dispersion decomposition, which is informative about homogenisation
but is NOT the registered VR, and labels it as a deviation rather than passing it off as the check.
See docs/osf-registration-update-02.md.
"""

from __future__ import annotations

import glob
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Explicit, not inferred from the model string: two of the six endpoints are the same developer,
# and the registered floor is on FAMILIES, so a heuristic that miscounts them overstates coverage.
FAMILY = {
    "gpt-oss:120b-cloud": "OpenAI (gpt-oss)",
    "gemma4:31b-cloud": "Google (Gemma)",
    "kiro/claude-sonnet-4.5": "Anthropic (Claude)",
    "kiro/claude-haiku-4.5": "Anthropic (Claude)",
    "kiro/glm-5": "Zhipu (GLM)",
    "kiro/deepseek-3.2": "DeepSeek",
}

# The registered floors, §7.2 check 1.
FLOORS = {"phrasings": 3, "persona detail levels": 2, "temperatures": 2, "model families": 3}


def cell_key(d: dict) -> tuple:
    return (d["model"], d["phrasing"], d["persona_detail"], d["temperature"], d["part"])


def load(paths: list[Path]) -> tuple[dict, list[dict]]:
    """Merge artefacts in argument order; first accepted draw for a cell wins."""
    merged, provenance = {}, []
    for p in paths:
        obj = json.loads(p.read_text())
        kept = 0
        for d in obj["draws"]:
            if not d["accepted"]:
                continue
            k = cell_key(d)
            if k in merged:
                continue
            d["_source"] = p.name
            merged[k] = d
            kept += 1
        provenance.append({
            "file": p.name, "elicited_utc": obj["elicited_utc"],
            "run": obj.get("run", "primary"),
            "item_table_sha256": obj["item_table_sha256"],
            "instrument_sha256": obj["instrument_sha256"],
            "n_attempted": obj["n_attempted"], "n_complete": obj["n_complete"],
            "contributed": kept,
        })
    return merged, provenance


def iqr(xs: list[float]) -> float:
    if len(xs) < 4:
        return float("nan")
    q = st.quantiles(xs, n=4)
    return q[2] - q[0]


def main() -> int:
    args = sys.argv[1:]
    if not args:
        # Wave 1 only. Merging is by cell, so a bare glob over `wave*` would pool the temporal
        # replication into the primary distribution and report the two as one panel. Wave 2 is a
        # COMPARISON against wave 1 (check 2), never an addition to it. Name the files to summarise
        # a different wave: `... tier2-forecast-wave2-*.json`.
        args = sorted(glob.glob(str(ROOT / "supplement/tier2-forecast/tier2-forecast-wave1*.json")))
    paths = [Path(a) if Path(a).is_absolute() else ROOT / a for a in args]
    paths = [p for p in paths if "smoke" not in p.name]
    if not paths:
        raise SystemExit("no forecast artefacts found")

    waves = sorted({json.loads(p.read_text()).get("wave") for p in paths}, key=str)
    if len(waves) > 1:
        raise SystemExit(
            f"REFUSING to summarise waves {waves} together.\n"
            "  Merging is by cell: pooling two waves would present a thirty-day temporal\n"
            "  replication as one panel and silently let the earlier wave win every contested\n"
            "  cell. Pre-registration §7.2 check 2 asks whether the waves AGREE, which requires\n"
            "  summarising them separately and comparing the two distributions.\n"
            f"  Run once per wave: {' | '.join(f'--wave {w}' if w is None else str(w) for w in waves)}")

    merged, prov = load(paths)
    print(f"wave {waves[0]}")

    print("=" * 78)
    print("TIER-2 FORECAST — DISTRIBUTION SUMMARY")
    print("=" * 78)
    print("\nProvenance")
    for p in prov:
        print(f"  {p['file']}")
        print(f"    {p['run']:8} elicited {p['elicited_utc']}   "
              f"complete {p['n_complete']}/{p['n_attempted']}   contributed {p['contributed']}")
    tables = {p["item_table_sha256"] for p in prov}
    insts = {p["instrument_sha256"] for p in prov}
    print(f"\n  item table sha256 : {'IDENTICAL across files' if len(tables) == 1 else 'DIFFERS — STOP'}"
          f"  {list(tables)[0][:16]}…")
    print(f"  instrument sha256 : {'IDENTICAL across files' if len(insts) == 1 else 'DIFFERS — STOP'}"
          f"  {list(insts)[0][:16]}…")

    draws = list(merged.values())
    # --- grid coverage against the registered floors -------------------------------------
    print("\n" + "-" * 78)
    print("GRID COVERAGE (pre-registration §7.2 check 1)")
    print("-" * 78)
    got = {
        "phrasings": {d["phrasing"] for d in draws},
        "persona detail levels": {d["persona_detail"] for d in draws},
        "temperatures": {d["temperature"] for d in draws},
        "model families": {FAMILY[d["model"]] for d in draws},
    }
    all_pass = True
    for dim, floor in FLOORS.items():
        n = len(got[dim])
        ok = n >= floor
        all_pass &= ok
        print(f"  {dim:22} {n} (floor {floor})  {'PASS' if ok else 'FAIL'}   "
              f"{', '.join(sorted(str(x) for x in got[dim]))}")
    print(f"  personas               {len({d['persona_key'] for d in draws})}   "
          f"{', '.join(sorted({d['persona_key'] for d in draws}))}")
    print(f"\n  registered grid: {'SATISFIED' if all_pass else 'NOT SATISFIED — report as such'}")

    print("\n  accepted draws per endpoint (A + B of a possible 12 + 12):")
    for m in sorted(FAMILY, key=lambda x: FAMILY[x]):
        a = sum(1 for d in draws if d["model"] == m and d["part"] == "A")
        b = sum(1 for d in draws if d["model"] == m and d["part"] == "B")
        flag = "" if a and b else "   <- CONTRIBUTES NOTHING" if not (a or b) else "   <- PARTIAL"
        print(f"    {m:24} A {a:2}/12   B {b:2}/12{flag}")

    # --- the forecasts -------------------------------------------------------------------
    probs: dict[str, list[tuple[str, float]]] = {}
    params: dict[str, list[tuple[str, float]]] = {}
    for d in draws:
        r = d["response"]
        if not isinstance(r, dict):
            continue
        for e in r.get("probabilities", []):
            if isinstance(e, dict) and isinstance(e.get("p"), (int, float)):
                probs.setdefault(e["id"], []).append((d["model"], float(e["p"])))
        for e in r.get("parameters", []):
            if isinstance(e, dict) and isinstance(e.get("point"), (int, float)):
                params.setdefault(e["id"], []).append((d["model"], float(e["point"])))

    print("\n" + "-" * 78)
    print("HYPOTHESIS-LEVEL AND INVARIANCE FORECASTS  (blocks B and C)")
    print("-" * 78)
    print(f"  {'id':12} {'n':>3}  {'med':>5} {'IQR':>5} {'min':>5} {'max':>5}   distribution")
    for pid in sorted(k for k in probs if k[0] in "BC"):
        xs = [v for _, v in probs[pid]]
        bars = "".join("▁▂▃▄▅▆▇█"[min(7, int(x * 8))] for x in sorted(xs))
        print(f"  {pid:12} {len(xs):3}  {st.median(xs):5.2f} {iqr(xs):5.2f} "
              f"{min(xs):5.2f} {max(xs):5.2f}   {bars}")

    if params:
        print("\n  parameter forecasts (point estimates)")
        print(f"  {'id':12} {'n':>3}  {'med':>6} {'IQR':>5} {'min':>6} {'max':>6}")
        for pid in sorted(params):
            xs = [v for _, v in params[pid]]
            print(f"  {pid:12} {len(xs):3}  {st.median(xs):6.2f} {iqr(xs):5.2f} "
                  f"{min(xs):6.2f} {max(xs):6.2f}")

    print("\n" + "-" * 78)
    print("ITEM-LOADING FORECASTS  (block A) — spread across the grid")
    print("-" * 78)
    aids = sorted(k for k in probs if k.startswith("A-"))
    spreads = [(max(v for _, v in probs[k]) - min(v for _, v in probs[k]), k) for k in aids]
    spreads.sort(reverse=True)
    print(f"  {len(aids)} item propositions forecast")
    print("  widest disagreement across the grid:")
    for s, k in spreads[:8]:
        xs = [v for _, v in probs[k]]
        print(f"    {k:12} range {s:.2f}   median {st.median(xs):.2f}  n={len(xs)}")
    print("  tightest agreement:")
    for s, k in spreads[-5:]:
        xs = [v for _, v in probs[k]]
        print(f"    {k:12} range {s:.2f}   median {st.median(xs):.2f}  n={len(xs)}")

    # --- dispersion decomposition ---------------------------------------------------------
    print("\n" + "-" * 78)
    print("DISPERSION DECOMPOSITION  (NOT the registered VR — see module docstring)")
    print("-" * 78)
    within, between = [], []
    for pid, obs in probs.items():
        bym: dict[str, list[float]] = {}
        for m, v in obs:
            bym.setdefault(m, []).append(v)
        w = [st.pvariance(v) for v in bym.values() if len(v) > 1]
        means = [st.mean(v) for v in bym.values()]
        if w:
            within.append(st.mean(w))
        if len(means) > 1:
            between.append(st.pvariance(means))
    if within and between:
        mw, mb = st.mean(within), st.mean(between)
        print(f"  mean within-model variance  (same model, different prompt cell) : {mw:.4f}")
        print(f"  mean between-model variance (model means)                       : {mb:.4f}")
        print(f"  ratio between/within                                            : {mb / mw:.2f}")
        print("\n  Reading: a ratio well below 1 means the endpoints agree with each other more")
        print("  than each agrees with itself under reworded prompts — the forecast would then be")
        print("  a property of the prompt, not of the model. A ratio well above 1 means the")
        print("  endpoints hold distinguishable positions that survive rewording.")
    print("\n  The registered variance ratio against a human comparison distribution is NOT")
    print("  computed: no human panel was run (DECISIONS.md Decision 1), so no such distribution")
    print("  exists. Reported as an executed-with-deviation check, never as a satisfied one.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
