#!/usr/bin/env python3
"""
16_tier2_score.py -- score the Tier-2 synthetic-panel forecast against the CFA.

    python3 code/16_tier2_score.py [--variant primary] [--selftest]

WHAT THIS IS. The paper's second claim is that a synthetic Delphi panel can be
audited against a criterion it cannot have absorbed in training: before the
confirmatory analysis was run, the panel forecast that analysis's own results,
and the forecast was frozen with an independent timestamp (OSF `zrvdp`, DOI
10.17605/OSF.IO/ZRVDP, 2026-08-10 09:11:17 UTC). The CFA has since been run.
This script closes the loop. Until it existed, Section 4 of the manuscript
promised a Brier skill score that no artefact produced.

WHAT IS SCORED, AND WHAT IS NOT. Sixty-six propositions were elicited: 52
item-loading statements (block A), 8 hypothesis statements (B), 3 invariance
statements (C) and 3 point forecasts of latent correlations (D). Four of the
binary propositions are NOT resolvable and are excluded with the reason
recorded in the output rather than dropped quietly:

  B-H3b, B-H4   -- H3b and H4 are registered hypotheses the paper does not
                   report. The panel was asked to forecast results that were
                   never produced.
  C-METRIC,     -- the registered 39-country metric and scalar ladder on M2 was
  C-SCALAR         never fitted. Unidimensional per-dimension substitutes exist
                   for D1 at both rungs (metric holds, scalar fails), but a
                   one-factor D1 model is not M2, and Block C -- unlike Blocks A
                   and B, which name their models -- inherits its referent from
                   the registered analysis. Scoring it against a substitute
                   would answer a question the panel was not asked.

Excluding them is not free and the direction matters: all four are propositions
on which the panel could have been scored and now cannot be, and three of the
four are ones the panel was, on the face of its probabilities, likely to get
right. The exclusion therefore works against the panel's score, not for it, and
the output records enough per-proposition detail for a reader to see that.

SCORING, exactly as registered (`docs/design/delphi-design.md` Sec. 9.6):
  Brier score  BS  = mean over (draw, proposition) pairs of (f - o)^2
  Murphy       BS  = reliability - resolution + uncertainty, over 10 bins
  Skill        BSS = 1 - BS/BS_ref, BS_ref the base-rate reference
  Informative  iff the family-cluster bootstrap lower bound of BSS > 0
  plus calibration curve, ECE over 10 bins, and AUC for block A.

The bootstrap clusters on MODEL FAMILY, not on draw, because draws from one
family are not independent -- this is the Kish point in the design document,
and resampling draws would give a confidence interval far too narrow.

THIS SCRIPT FITS NOTHING. Every outcome is read from a JSON that a numbered
script wrote. `--selftest` checks the scoring functions against hand-computable
cases and exits.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SEED = 20260810
N_BOOT = 10000
N_BINS = 10

# Six endpoints, five developers: the two Anthropic models are one family, which is why the
# registered grid says five. Getting this wrong would inflate the bootstrap's effective
# cluster count and narrow the interval -- the exact error the clustering exists to avoid.
FAMILY = {
    "ollama:gpt-oss:120b-cloud":        "openai-oss",
    "ollama:gemma4:31b-cloud":          "google-gemma",
    "omniroute:kiro/claude-sonnet-4.5": "anthropic",
    "omniroute:kiro/claude-haiku-4.5":  "anthropic",
    "omniroute:kiro/glm-5":             "zhipu",
    "omniroute:kiro/deepseek-3.2":      "deepseek",
}

UNRESOLVED = {
    "B-H3b": "H3b is a registered hypothesis the paper does not report: it needs country-level "
             "D1/D2 scores, and the alignment hard stop licenses none.",
    "B-H4":  "H4 is a registered hypothesis the paper does not report: 8 of its 10 probe items "
             "are outside the analysis frame.",
    "C-METRIC": "The registered 39-country metric step on M2 was never fitted. The two "
                "diagnostics that stand in for it disagree and differ in both specification "
                "and sample, so neither resolves this proposition as worded.",
    "C-SCALAR": "The registered 39-country scalar step on M2 was never fitted. The "
                "unidimensional D1 scalar step at 39 countries was (dCFI -.0530, fails), but "
                "a one-factor D1 model is not M2; resolving against it would score the panel "
                "on a question it was not asked, and would raise its score.",
}


# --------------------------------------------------------------------------- scoring maths
def brier(f: np.ndarray, o: np.ndarray) -> float:
    return float(np.mean((f - o) ** 2))


def murphy(f: np.ndarray, o: np.ndarray, n_bins: int = N_BINS) -> dict:
    """Murphy decomposition: reliability - resolution + uncertainty, over n_bins.

    The identity is exact for the BINNED forecasts -- each f_i replaced by its bin mean --
    and only approximate for the raw ones, because the cross-term between within-bin forecast
    spread and within-bin outcome spread does not vanish. Both are reported, along with the
    gap between them, so the decomposition is not quietly asserted of a number it does not
    decompose. `bs_binned` is what `reliability - resolution + uncertainty` reproduces.
    """
    obar = float(np.mean(o))
    unc = obar * (1.0 - obar)
    # Right-closed bins so a forecast of exactly 1.0 lands in the top bin rather than
    # outside it; np.digitize's default would put it in an (n_bins+1)-th bin.
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(f, edges[1:-1], right=True), 0, n_bins - 1)
    rel = res = 0.0
    curve = []
    f_binned = np.empty_like(f)
    for k in range(n_bins):
        m = idx == k
        nk = int(m.sum())
        if nk == 0:
            continue
        fk, ok = float(np.mean(f[m])), float(np.mean(o[m]))
        f_binned[m] = fk
        rel += nk * (fk - ok) ** 2
        res += nk * (ok - obar) ** 2
        curve.append({"bin": f"[{edges[k]:.1f},{edges[k+1]:.1f}]", "n": nk,
                      "mean_forecast": round(fk, 4), "observed_rate": round(ok, 4)})
    n = len(f)
    rel, res = rel / n, res / n
    ece = sum(c["n"] * abs(c["mean_forecast"] - c["observed_rate"]) for c in curve) / n
    bs_binned = brier(f_binned, o)
    return {"reliability": rel, "resolution": res, "uncertainty": unc,
            "bs_binned": bs_binned, "identity_check": rel - res + unc,
            "binning_residual": brier(f, o) - bs_binned, "ece": ece, "curve": curve}


def auc(f: np.ndarray, o: np.ndarray) -> float | None:
    """Mann-Whitney AUC. Ties in f contribute 0.5, which is what the rank form gives."""
    pos, neg = f[o == 1], f[o == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    ranks = np.empty(len(order), dtype=float)
    ranks[order] = np.arange(1, len(order) + 1)
    # average ranks within ties
    allv = np.concatenate([pos, neg])[order]
    i = 0
    r_sorted = ranks[order]
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1] == allv[i]:
            j += 1
        if j > i:
            r_sorted[i:j + 1] = r_sorted[i:j + 1].mean()
        i = j + 1
    ranks[order] = r_sorted
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def skill(f: np.ndarray, o: np.ndarray) -> tuple[float, float, float]:
    """BSS against the base-rate reference: the constant forecast obar for every pair."""
    bs = brier(f, o)
    obar = float(np.mean(o))
    bs_ref = brier(np.full_like(f, obar), o)
    return bs, bs_ref, (1.0 - bs / bs_ref) if bs_ref > 0 else float("nan")


def cluster_bootstrap_bss(f, o, fam, n_boot=N_BOOT, seed=SEED) -> dict:
    """Resample MODEL FAMILIES with replacement; recompute BSS in each replicate."""
    rng = np.random.default_rng(seed)
    fams = sorted(set(fam))
    idx_by_fam = {g: np.flatnonzero(np.asarray(fam) == g) for g in fams}
    out = []
    for _ in range(n_boot):
        pick = rng.choice(len(fams), size=len(fams), replace=True)
        rows = np.concatenate([idx_by_fam[fams[p]] for p in pick])
        # A replicate that draws one family repeatedly can have zero outcome variance,
        # leaving BSS undefined. Skipped and counted, never silently treated as zero.
        oo = o[rows]
        if oo.min() == oo.max():
            continue
        out.append(skill(f[rows], oo)[2])
    a = np.asarray(out)
    return {"n_families": len(fams), "n_replicates": n_boot, "n_usable": int(a.size),
            "lo95": float(np.percentile(a, 2.5)), "hi95": float(np.percentile(a, 97.5)),
            "median": float(np.percentile(a, 50))}


# --------------------------------------------------------------------------- self-test
def selftest() -> int:
    ok = True

    def chk(name, got, want, tol=1e-9):
        nonlocal ok
        good = abs(got - want) < tol
        ok &= good
        print(f"  {'ok  ' if good else 'FAIL'} {name}: {got!r} (want {want!r})")

    # A perfect forecaster scores 0; the worst possible scores 1.
    chk("brier perfect", brier(np.array([1.0, 0.0]), np.array([1.0, 0.0])), 0.0)
    chk("brier worst", brier(np.array([0.0, 1.0]), np.array([1.0, 0.0])), 1.0)
    # Constant .5 on a balanced outcome set: BS = .25, and it IS the base rate, so BSS = 0.
    f, o = np.full(4, 0.5), np.array([1.0, 1.0, 0.0, 0.0])
    bs, ref, bss = skill(f, o)
    chk("brier constant .5", bs, 0.25)
    chk("bss of the reference itself", bss, 0.0)
    # Murphy identity must reproduce BS exactly on an arbitrary case.
    rng = np.random.default_rng(1)
    f2 = rng.random(500)
    o2 = (rng.random(500) < f2).astype(float)
    m = murphy(f2, o2)
    chk("murphy identity (binned)", m["identity_check"], m["bs_binned"], 1e-12)
    # And a case where binning is lossless -- forecasts already at bin centres -- so the
    # identity must reproduce the RAW Brier score too. If it does not, the binning is wrong.
    f3 = np.array([0.05, 0.05, 0.35, 0.35, 0.75, 0.75, 0.95, 0.95])
    o3 = np.array([0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0])
    m3 = murphy(f3, o3)
    chk("murphy identity (lossless binning)", m3["identity_check"], brier(f3, o3), 1e-12)
    chk("binning residual is zero there", m3["binning_residual"], 0.0, 1e-12)
    # AUC: perfectly separating forecasts give 1.0, reversed give 0.0, constant gives 0.5.
    chk("auc separating", auc(np.array([.9, .8, .2, .1]), np.array([1., 1., 0., 0.])), 1.0)
    chk("auc reversed", auc(np.array([.1, .2, .8, .9]), np.array([1., 1., 0., 0.])), 0.0)
    chk("auc constant", auc(np.full(4, .5), np.array([1., 1., 0., 0.])), 0.5)
    print("\nselftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# --------------------------------------------------------------------------- outcomes
READINGS = {
    # WHICH MODEL DID THE PANEL FORECAST? The instrument's block A says "the configural
    # three-factor model M2", but its prompt prose says "The target model M2 has three
    # correlated factors plus an orthogonal method factor for the nine 'essential
    # characteristics of democracy' items" -- which describes M2m, the specification
    # registration Decision D3 requires, not the M2 the manuscript reports as target.
    #
    # The panel saw the prose. M2m is therefore the primary reading, and it is chosen on
    # that ground and no other. DISCOVERY ORDER, recorded because it bears on how much the
    # choice can be trusted: block A was scored against M2 first, on 2026-08-11, and the
    # discrepancy was found afterwards while computing per-sphere reliability. Both readings
    # are scored and both are reported, so the choice moves nothing that a reader cannot see.
    "M2m": {"file": "m2m-loadings-{v}.json", "primary": True,
            "why": "The Tier-2 prompt describes the target model as carrying an orthogonal "
                   "method factor over the democracy battery. That is M2m. The panel "
                   "forecast the model it was described, not the model that shares its name."},
    "M2": {"file": "m2-loadings-{v}.json", "primary": False,
           "why": "The literal label in the block A proposition text. Reported as a "
                  "sensitivity because the instrument's own prose contradicts the label."},
}


def resolve_outcomes(variant: str, reading: str) -> tuple[dict, dict]:
    """Map every proposition id to an outcome, or to None with a recorded reason."""
    A = ROOT / "supplement/analysis"
    single = json.loads((A / f"cfa-{variant}-single.json").read_text())
    align = json.loads((A / f"cfa-{variant}-alignment.json").read_text())
    lt = json.loads((A / READINGS[reading]["file"].format(v=variant)).read_text())
    inst = json.loads((ROOT / "supplement/tier2-forecast/tier2-instrument.json").read_text())

    lam = {(r["variable"], r["factor"]): r["est.std"] for r in lt["loadings"]}
    if reading == "M2":
        # The M2 table must reproduce the pre-registered drop log exactly, or one of the two
        # is reading a different fit and every block A outcome is suspect. M2m has its own
        # loading structure and a different sub-.30 count, so the check does not apply there.
        n_sub30 = sum(1 for (v_, f_), x in lam.items() if abs(x) < .30)
        drop = single["drop_log"]["weak_loadings"]
        n_drop = len(drop) if isinstance(drop, list) else 0
        if n_sub30 != n_drop:
            raise SystemExit(
                f"loading table and drop log disagree: {n_sub30} vs {n_drop} sub-.30 items")

    thr = inst["loading_threshold"]
    out, why = {}, {}
    for p in inst["propositions"]["block_A"]:
        out[p["id"]] = float(lam[(p["variable"], p["assigned"])] >= thr)

    H1, H2, fit = single["H1"], single["H2"], single["fit"]
    out["B-H1"] = float(H1["supported"])
    out["B-H1a"] = float(H1["a_deltaCFI_ge_.010"])
    out["B-H1c"] = float(H1["c_phi_le_.85"])
    out["B-H2"] = float(H2["supported"])
    out["B-H2c"] = float(H2["phi_le_.70"])
    out["B-FIT"] = float(fit[reading]["cfi.scaled"] >= .95)
    out["C-ALIGN"] = float(any(not d["recovery_confirmed"]
                               for d in align["invariance"]["alignment"].values()))
    for pid, reason in UNRESOLVED.items():
        out[pid] = None
        why[pid] = reason

    # Block D asks for "the latent correlation between D1 and D2" in the model just described,
    # so it resolves against THAT model's phi. An earlier version resolved D-PHI12 against
    # M1's phi (.2984), which is the coefficient H1 is tested on and not the one the panel was
    # asked for; corrected here, and it moves the sign of nothing.
    lc = lt["latent_correlations"]
    params = {"D-PHI12": lc["phi_D1_D2"], "D-PHI13": lc["phi_D1_D3"],
              "D-PHI23": lc["phi_D2_D3"]}
    return {"binary": out, "unresolved_reasons": why, "parameters": params,
            "loading_threshold": thr,
            "m2_source": lt["source_fit"], "reading": reading,
            "reading_why": READINGS[reading]["why"],
            "configural_note": "The instrument's word 'configural' could also point at the "
                               "multi-group fit, which yields 39 loadings per item and no "
                               "aggregation rule anywhere in the instrument. The pooled fit is "
                               "the only reading under which the proposition has a referent."}, inst


# --------------------------------------------------------------------------- draws
def load_draws() -> list[dict]:
    """Accepted draws from wave 1 and its top-up, de-duplicated on the grid cell."""
    d = ROOT / "supplement/tier2-forecast"
    files = ["tier2-forecast-wave1-20260810T083817Z.json",
             "tier2-forecast-wave1-topup-20260810T085136Z.json"]
    seen, rows = set(), []
    for fn in files:
        blob = json.loads((d / fn).read_text())
        for dr in blob["draws"]:
            if not dr.get("accepted"):
                continue
            cell = (dr["model"], dr["phrasing"], dr["persona_detail"],
                    dr["temperature"], dr["persona_key"], dr["part"])
            # The top-up re-ran only the cells wave 1 lost to HTTP 429, so an overlap would
            # mean one cell contributing twice and being weighted double.
            if cell in seen:
                raise SystemExit(f"duplicate grid cell across artefacts: {cell}")
            seen.add(cell)
            att = dr["attempts"][-1]
            if not att.get("check", {}).get("ok"):
                raise SystemExit(f"accepted draw whose last attempt did not pass its check: {cell}")
            rows.append({"cell": cell, "source": fn, "instrument_sha256": blob["instrument_sha256"],
                         "endpoint": f"{dr['channel']}:{dr['model']}",
                         "family": FAMILY[f"{dr['channel']}:{dr['model']}"],
                         "phrasing": dr["phrasing"], "detail": dr["persona_detail"],
                         "temperature": dr["temperature"], "persona": dr["persona_key"],
                         "part": dr["part"], "response": att["response"]})
    return rows


def summarise_by(rows, key, f, o, owner) -> list[dict]:
    """BS and BSS within each level of one grid factor -- the distribution, not a point."""
    out = []
    for lvl in sorted({r[key] for r in rows}, key=str):
        m = np.array([owner[i][key] == lvl for i in range(len(f))])
        if m.sum() == 0 or o[m].min() == o[m].max():
            continue
        bs, ref, bss = skill(f[m], o[m])
        out.append({str(key): str(lvl), "n_pairs": int(m.sum()),
                    "brier": round(bs, 4), "bss": round(bss, 4)})
    return out


def score_one(res: dict, rows: list[dict]) -> dict:
    """Every statistic for one resolution reading. Called once per reading, so the primary
    and the sensitivity cannot diverge through a copied-and-edited code path."""
    outcomes = res["binary"]

    # ---- flatten to (draw, proposition) pairs -------------------------------------------
    f_list, o_list, owner = [], [], []
    per_prop: dict[str, list[float]] = {}
    n_skipped = 0
    for r in rows:
        for pr in r["response"].get("probabilities", []):
            pid, p = pr["id"], pr["p"]
            per_prop.setdefault(pid, []).append(float(p))
            if outcomes.get(pid) is None:
                n_skipped += 1
                continue
            f_list.append(float(p)); o_list.append(outcomes[pid]); owner.append(r)
    f, o = np.asarray(f_list, float), np.asarray(o_list, float)
    fam = [r["family"] for r in owner]

    bs, bs_ref, bss = skill(f, o)
    mur = murphy(f, o)
    boot = cluster_bootstrap_bss(f, o, fam)
    informative = boot["lo95"] > 0

    blockA = np.array([owner[i]["part"] == "A" for i in range(len(f))])
    a_bs, a_ref, a_bss = skill(f[blockA], o[blockA])
    b_bs, b_ref, b_bss = skill(f[~blockA], o[~blockA])

    # ---- block D: point forecasts of the three latent correlations ----------------------
    dpar = []
    for pid, truth in res["parameters"].items():
        pts = [q["point"] for r in rows for q in r["response"].get("parameters", [])
               if q["id"] == pid and q.get("point") is not None]
        cov = [1.0 for r in rows for q in r["response"].get("parameters", [])
               if q["id"] == pid and q.get("lo80") is not None and q.get("hi80") is not None
               and q["lo80"] <= truth <= q["hi80"]]
        n_int = sum(1 for r in rows for q in r["response"].get("parameters", [])
                    if q["id"] == pid and q.get("lo80") is not None and q.get("hi80") is not None)
        a = np.asarray(pts, float)
        dpar.append({"id": pid, "observed": round(truth, 4), "n_forecasts": int(a.size),
                     "median_forecast": round(float(np.median(a)), 4),
                     "mean_forecast": round(float(np.mean(a)), 4),
                     "sd_forecast": round(float(np.std(a, ddof=1)), 4),
                     "median_absolute_error": round(float(np.median(np.abs(a - truth))), 4),
                     "rmse": round(float(np.sqrt(np.mean((a - truth) ** 2))), 4),
                     "sign_correct_rate": round(float(np.mean(np.sign(a) == np.sign(truth))), 4),
                     "n_with_80_interval": n_int,
                     "interval_80_coverage": round(len(cov) / n_int, 4) if n_int else None})

    prop_rows = []
    for pid in sorted(per_prop):
        v = np.asarray(per_prop[pid], float)
        prop_rows.append({"id": pid, "n_draws": int(v.size),
                          "mean_forecast": round(float(v.mean()), 4),
                          "sd_forecast": round(float(v.std(ddof=1)), 4),
                          "outcome": outcomes.get(pid),
                          "resolved": outcomes.get(pid) is not None})

    out = {
        "reading": res["reading"],
        "reading_why": res["reading_why"],
        "outcome_sources": {"loadings": res["m2_source"],
                            "configural_note": res["configural_note"],
                            "loading_threshold": res["loading_threshold"]},
        "draws": {"n_cells_accepted": len(rows),
                  "n_part_A": sum(1 for r in rows if r["part"] == "A"),
                  "n_part_B": sum(1 for r in rows if r["part"] == "B"),
                  "families": sorted(set(FAMILY.values()))},
        "propositions": {"n_total": len(per_prop),
                         "n_resolved": sum(1 for p in prop_rows if p["resolved"]),
                         "n_unresolved": sum(1 for p in prop_rows if not p["resolved"]),
                         "unresolved_reasons": res["unresolved_reasons"],
                         "n_pairs_scored": int(f.size),
                         "n_pairs_skipped_unresolved": n_skipped,
                         "base_rate_true": round(float(o.mean()), 4)},
        "brier": {"BS": round(bs, 4), "BS_reference_base_rate": round(bs_ref, 4),
                  "BSS": round(bss, 4),
                  "murphy": {k: round(v, 6) for k, v in mur.items() if k != "curve"},
                  "calibration_curve": mur["curve"],
                  "auc_block_A": round(auc(f[blockA], o[blockA]), 4)},
        "by_block": {
            "A_item_loadings": {"n_pairs": int(blockA.sum()), "BS": round(a_bs, 4),
                                "BS_reference_base_rate": round(a_ref, 4),
                                "BSS": round(a_bss, 4),
                                "base_rate_true": round(float(o[blockA].mean()), 4)},
            "B_C_hypotheses_and_invariance": {
                "n_pairs": int((~blockA).sum()), "BS": round(b_bs, 4),
                "BS_reference_base_rate": round(b_ref, 4), "BSS": round(b_bss, 4),
                "base_rate_true": round(float(o[~blockA].mean()), 4),
                "caveat": "Only 7 of these 11 propositions resolve and 6 of the 7 came out TRUE, "
                          "so the base-rate reference is unusually strong here and a negative BSS "
                          "is easier to earn than it looks. The comparison worth making is not "
                          "block B/C against zero but block B/C against block A, where the same "
                          "panel, in the same cells, scored positively."},
        },
        "family_cluster_bootstrap": {k: (round(v, 4) if isinstance(v, float) else v)
                                     for k, v in boot.items()},
        "informative_by_registered_criterion": bool(informative),
        "registered_criterion": "BSS family-cluster bootstrap lower bound > 0",
        "distribution_over_the_grid": {
            "note": "Reported because the registered rule is to report the distribution, never a "
                    "point estimate. A configuration is not a finding.",
            "by_phrasing": summarise_by(rows, "phrasing", f, o, owner),
            "by_persona_detail": summarise_by(rows, "detail", f, o, owner),
            "by_temperature": summarise_by(rows, "temperature", f, o, owner),
            "by_family": summarise_by(rows, "family", f, o, owner),
            "by_persona": summarise_by(rows, "persona", f, o, owner),
        },
        "block_D_point_forecasts": dpar,
        "per_proposition": prop_rows,
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="primary")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    rows = load_draws()
    hashes = {r["instrument_sha256"] for r in rows}
    if len(hashes) != 1:
        raise SystemExit(f"artefacts carry different instrument hashes {hashes}; "
                         "wave 1 and its top-up did not ask the same questions")

    scored, inst = {}, None
    for reading in READINGS:
        res, inst = resolve_outcomes(args.variant, reading)
        scored[reading] = score_one(res, rows)
    primary = next(k for k, v in READINGS.items() if v["primary"])
    other = [k for k in READINGS if k != primary]

    out = dict(scored[primary])
    out.update({
        "run_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        "registered": True,
        "registered_in": "preregistration.md 7.1; scoring spec docs/design/delphi-design.md 9.6",
        "variant": args.variant,
        "seed": SEED,
        # Both artefacts must carry the same instrument hash, or wave 1 and its top-up asked
        # different questions and pooling them is illegitimate.
        "instrument_sha256": sorted(hashes),
        "instrument_version": inst.get("instrument_version"),
        "forecast_deposit": {"node": "https://osf.io/zrvdp/", "doi": "10.17605/OSF.IO/ZRVDP",
                             "frozen_utc": "2026-08-10T09:11:17Z",
                             "note": "Frozen before any CFA was run; the gate is enforced in "
                                     "code/05 and code/06."},
        "resolution_sensitivity": {
            "note": "The same forecast scored against the other reading of which model the "
                    "instrument described. Reported in full because the choice between them is "
                    "an interpretive one made by us after the forecast was frozen, and a reader "
                    "is entitled to see what it is worth.",
            "discovery_order": "Block A was first scored against M2 on 2026-08-11. The "
                               "discrepancy between the instrument's label (M2) and its prose "
                               "(a method factor, i.e. M2m) was found afterwards, while "
                               "computing per-sphere reliability. Both are reported.",
            **{k: {"BSS": scored[k]["brier"]["BSS"],
                   "BS": scored[k]["brier"]["BS"],
                   "block_A_BSS": scored[k]["by_block"]["A_item_loadings"]["BSS"],
                   "auc_block_A": scored[k]["brier"]["auc_block_A"],
                   "bootstrap_lo95": scored[k]["family_cluster_bootstrap"]["lo95"],
                   "informative": scored[k]["informative_by_registered_criterion"],
                   "block_D": {r["id"]: {"observed": r["observed"],
                                         "median_forecast": r["median_forecast"],
                                         "interval_80_coverage": r["interval_80_coverage"]}
                               for r in scored[k]["block_D_point_forecasts"]},
                   "why": READINGS[k]["why"]}
               for k in [primary] + other},
            "verdict_stable_across_readings": (
                (scored[primary]["informative_by_registered_criterion"]
                 == scored[other[0]]["informative_by_registered_criterion"])
                and (scored[primary]["by_block"]["A_item_loadings"]["BSS"] > 0)
                == (scored[other[0]]["by_block"]["A_item_loadings"]["BSS"] > 0)),
        },
    })

    dest = ROOT / f"supplement/analysis/tier2-score-{args.variant}.json"
    dest.write_text(json.dumps(out, indent=2))

    bs = out["brier"]["BS"]; bs_ref = out["brier"]["BS_reference_base_rate"]
    bss = out["brier"]["BSS"]; mur = out["brier"]["murphy"]
    boot = out["family_cluster_bootstrap"]
    a_bss = out["by_block"]["A_item_loadings"]["BSS"]
    b_bss = out["by_block"]["B_C_hypotheses_and_invariance"]["BSS"]
    dpar = out["block_D_point_forecasts"]
    informative = out["informative_by_registered_criterion"]
    n_skipped = out["propositions"]["n_pairs_skipped_unresolved"]

    print(f"primary reading: {primary} -- {READINGS[primary]['why'][:70]}...")
    for k in [primary] + other:
        s = scored[k]
        print(f"  {k:4s} BSS {s['brier']['BSS']:+.4f}  block A {s['by_block']['A_item_loadings']['BSS']:+.4f}"
              f"  AUC {s['brier']['auc_block_A']:.4f}  boot lo {s['family_cluster_bootstrap']['lo95']:+.4f}")
    print(f"verdict stable across readings: {out['resolution_sensitivity']['verdict_stable_across_readings']}")
    print(f"cells {len(rows)}  pairs scored {out['propositions']['n_pairs_scored']}  "
          f"skipped (unresolvable) {n_skipped}")
    print(f"propositions: {out['propositions']['n_resolved']} resolved, "
          f"{out['propositions']['n_unresolved']} not; base rate TRUE = "
          f"{out['propositions']['base_rate_true']:.4f}")
    print(f"BS {bs:.4f}   BS_ref {bs_ref:.4f}   BSS {bss:+.4f}")
    print(f"  block A {a_bss:+.4f}   blocks B/C {b_bss:+.4f}   AUC(A) {out['brier']['auc_block_A']}")
    print(f"  Murphy  rel {mur['reliability']:.4f}  res {mur['resolution']:.4f}  "
          f"unc {mur['uncertainty']:.4f}  ECE {mur['ece']:.4f}")
    print(f"family-cluster bootstrap BSS 95% [{boot['lo95']:+.4f}, {boot['hi95']:+.4f}] "
          f"over {boot['n_families']} families")
    print(f"informative by the registered criterion: {informative}")
    for d in dpar:
        print(f"  {d['id']}: observed {d['observed']:+.4f}  median forecast "
              f"{d['median_forecast']:+.4f}  MdAE {d['median_absolute_error']:.4f}  "
              f"80% coverage {d['interval_80_coverage']}")
    print(f"wrote {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
