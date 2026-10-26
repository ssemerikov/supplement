#!/usr/bin/env python3
"""28_tier2_wave_comparison.py — Tier-2 temporal replication, wave 1 vs wave 2 (§7.2 check 2)

    python3 code/28_tier2_wave_comparison.py

Reads only. Writes one JSON summary. Calls nothing, touches no survey data.

WHAT IS REGISTERED. docs/design/delphi-design.md §9.8 registers temporal drift as two statistics,
and this script reports BOTH rather than substituting one for the other:

    (i)  "proportion of items whose modal assignment changes at t+30"
    (ii) "alpha between occasions"

MAPPING A CATEGORICAL SPEC ONTO A PROBABILISTIC INSTRUMENT. §9.8 was written for a Delphi in which
panellists ASSIGN items to dimensions, so "modal assignment" is a category. The Tier-2 instrument
emits a probability per proposition instead, so the spec needs a mapping, and the mapping is fixed
here before any comparison is computed:

    the panel's assignment for a proposition = the side its median forecast falls on,
    i.e. side = (median p across that wave's accepted draws) > 0.5,

which is the categorical content of a probabilistic panel verdict: which way it calls the
proposition. Drift is the proportion of propositions whose side differs between the waves.
Propositions whose median sits exactly at .5 in either wave are counted separately and never
silently assigned a side. This mapping is disclosed in the pre-registration deviation log; it is a
mapping, not a substitution, and no other reading of "modal assignment" was computed and discarded.

WHICH DRAWS EACH WAVE CONTRIBUTES. Wave 1 is 144/144; wave 2 is 141/144, having lost three
`kiro/claude-haiku-4.5` cells to stable model refusals. Each wave's median is therefore taken over
ITS OWN accepted set — what that wave actually says — and the per-proposition n of each wave is
reported beside every statistic so the asymmetry stays visible. The intersection basis is reported
too, as a robustness line, so a reviewer can see the drift is not an artefact of the missing cells.

TWO UNITS OF ANALYSIS FOR ALPHA, BOTH REPORTED. "Alpha between occasions" needs a unit, and the
two available ones answer different questions and bracket the truth:

    cell level   — one pair per (cell x proposition): does an individual synthetic panellist give
                   the same answer thirty days later? This carries the within-cell stochasticity of
                   the draw itself. At temperature 1.0 two draws from the SAME wave would not agree
                   exactly either, and this design has no within-wave replicate to net that out, so
                   cell-level alpha CONFOUNDS temporal drift with sampling noise and is a LOWER
                   BOUND on stability.
    median level — one pair per proposition, comparing each wave's median: does the PANEL say the
                   same thing thirty days later? Aggregation averages the sampling noise away, so
                   this is an UPPER BOUND.

The panel-level question is the one a Delphi asks, so the median-level figure is the headline; the
cell-level figure is reported beside it and neither is presented alone. Reporting only the median
figure as "alpha between occasions" would overstate the agreement a reliability coefficient claims.

NOT SCORED HERE. Wave 1 is the contamination-immune tier because §7.1 required it to be
time-stamped before the CFA and it was; the CFA has since run. Brier-scoring wave 2 against a known
outcome therefore measures something different from what wave 1's score measures, and mixing the
two in one file is exactly the blur the pre-registration warns against. This script does not score
either wave. Wave 1's Brier skill lives in `supplement/analysis/tier2-score-primary.json`.
"""

from __future__ import annotations

import glob
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FC = ROOT / "supplement" / "tier2-forecast"
OUT = ROOT / "supplement" / "analysis" / "tier2-wave-comparison.json"

# Same cell identity the summariser merges on, so the two scripts cannot disagree about what a
# cell is. Imported by value rather than by import to keep this script standalone in the package.
def cell_key(d: dict) -> tuple:
    return (d["model"], d["phrasing"], d["persona_detail"], d["temperature"], d["part"])


def wave_files(wave: int) -> list[Path]:
    got = sorted(Path(p) for p in glob.glob(str(FC / f"tier2-forecast-wave{wave}*.json")))
    got = [p for p in got if "smoke" not in p.name]
    if not got:
        raise SystemExit(f"no wave-{wave} artefacts in {FC.relative_to(ROOT)}")
    return got


def load_wave(wave: int) -> tuple[dict, list[dict]]:
    """Accepted draws for one wave, keyed by cell. First accepted draw for a cell wins."""
    merged, prov = {}, []
    for p in wave_files(wave):
        obj = json.loads(p.read_text())
        if obj.get("wave") != wave:
            raise SystemExit(f"{p.name} declares wave {obj.get('wave')}, not {wave}")
        kept = 0
        for d in obj["draws"]:
            if not d["accepted"] or cell_key(d) in merged:
                continue
            merged[cell_key(d)] = d
            kept += 1
        prov.append({"file": p.name, "run": obj.get("run", "primary"),
                     "elicited_utc": obj["elicited_utc"],
                     "instrument_sha256": obj["instrument_sha256"],
                     "item_table_sha256": obj["item_table_sha256"],
                     "n_complete": obj["n_complete"], "n_attempted": obj["n_attempted"],
                     "contributed": kept})
    return merged, prov


def forecasts(cells: dict) -> tuple[dict, dict]:
    """{proposition id: [p, ...]} and {parameter id: [point, ...]} over a wave's accepted cells."""
    probs, params = {}, {}
    for d in cells.values():
        r = d["response"]
        if not isinstance(r, dict):
            continue
        for e in r.get("probabilities", []):
            if isinstance(e, dict) and isinstance(e.get("p"), (int, float)):
                probs.setdefault(e["id"], []).append(float(e["p"]))
        for e in r.get("parameters", []):
            if isinstance(e, dict) and isinstance(e.get("point"), (int, float)):
                params.setdefault(e["id"], []).append(float(e["point"]))
    return probs, params


def krippendorff_alpha_interval(pairs: list[tuple[float, float]]) -> float:
    """Krippendorff's alpha, interval metric, two occasions, complete data.

    alpha = 1 - Do/De.  With exactly two values per unit the observed disagreement reduces to the
    mean squared difference between occasions, and the expected disagreement is the mean squared
    difference between every ordered pair of values in the pooled set:

        Do = (1/N) * sum_u (x_u1 - x_u2)^2
        De = 2 * [ n*sum(x^2) - (sum x)^2 ] / (n*(n-1)),   n = 2N

    De is the disagreement a panel with this marginal spread would produce by chance, so alpha is 0
    when the occasions agree no better than that and 1 when they agree exactly.
    """
    n_units = len(pairs)
    if n_units < 2:
        return float("nan")
    do = sum((a - b) ** 2 for a, b in pairs) / n_units
    vals = [v for pair in pairs for v in pair]
    n = len(vals)
    de = 2.0 * (n * sum(v * v for v in vals) - sum(vals) ** 2) / (n * (n - 1))
    return float("nan") if de == 0 else 1.0 - do / de


def cell_level_pairs(w1: dict, w2: dict) -> list[tuple[float, float]]:
    """One (wave 1, wave 2) pair per (cell, proposition) for cells accepted in both waves.

    The draw itself is the unit, so no aggregation stands between the two occasions. See the
    header: this is a lower bound, because it carries within-cell stochasticity that no
    within-wave replicate exists to remove.
    """
    pairs = []
    for k in sorted(set(w1) & set(w2)):
        r1, r2 = w1[k]["response"], w2[k]["response"]
        if not (isinstance(r1, dict) and isinstance(r2, dict)):
            continue
        def byid(r, field, val):
            return {e["id"]: float(e[val]) for e in r.get(field, [])
                    if isinstance(e, dict) and isinstance(e.get(val), (int, float))}
        a, b = byid(r1, "probabilities", "p"), byid(r2, "probabilities", "p")
        pairs.extend((a[i], b[i]) for i in sorted(set(a) & set(b)))
    return pairs


def side(med: float):
    """The panel's call. None at exactly .5 — never silently assigned."""
    return None if med == 0.5 else med > 0.5


def compare(p1: dict, p2: dict, label: str) -> dict:
    ids = sorted(set(p1) & set(p2))
    rows, flips, ties, pairs = [], [], [], []
    for pid in ids:
        m1, m2 = st.median(p1[pid]), st.median(p2[pid])
        s1, s2 = side(m1), side(m2)
        pairs.append((m1, m2))
        row = {"id": pid, "n_w1": len(p1[pid]), "n_w2": len(p2[pid]),
               "median_w1": round(m1, 4), "median_w2": round(m2, 4),
               "delta": round(m2 - m1, 4),
               "iqr_w1": round(_iqr(p1[pid]), 4), "iqr_w2": round(_iqr(p2[pid]), 4),
               "side_w1": s1, "side_w2": s2}
        rows.append(row)
        if s1 is None or s2 is None:
            ties.append(pid)
        elif s1 != s2:
            flips.append(pid)
    decidable = [r for r in rows if r["side_w1"] is not None and r["side_w2"] is not None]
    deltas = [abs(r["delta"]) for r in rows]
    return {
        "basis": label,
        "n_propositions": len(ids),
        "n_decidable": len(decidable),
        "n_at_exactly_.5_in_a_wave": len(ties),
        "ids_at_exactly_.5": ties,
        "modal_assignment_changes": len(flips),
        "modal_assignment_change_rate": round(len(flips) / len(decidable), 4) if decidable else None,
        "ids_changed": flips,
        "alpha_between_occasions": round(krippendorff_alpha_interval(pairs), 4),
        "median_abs_shift": round(st.median(deltas), 4) if deltas else None,
        "max_abs_shift": round(max(deltas), 4) if deltas else None,
        "rows": rows,
    }


def _iqr(xs: list[float]) -> float:
    if len(xs) < 4:
        return float("nan")
    q = st.quantiles(xs, n=4)
    return q[2] - q[0]


def main() -> int:
    w1, prov1 = load_wave(1)
    w2, prov2 = load_wave(2)
    insts = {p["instrument_sha256"] for p in prov1 + prov2}
    if len(insts) != 1:
        raise SystemExit(f"instrument differs across waves {insts} — the waves are not comparable")
    tables = {p["item_table_sha256"] for p in prov1 + prov2}
    if len(tables) != 1:
        raise SystemExit(f"item table differs across waves {tables} — stop and disclose")

    t1 = min(p["elicited_utc"] for p in prov1)
    t2 = min(p["elicited_utc"] for p in prov2)
    import datetime as dt
    gap = (dt.datetime.fromisoformat(t2) - dt.datetime.fromisoformat(t1)).total_seconds() / 86400

    pr1, pa1 = forecasts(w1)
    pr2, pa2 = forecasts(w2)

    # Own-set basis: what each wave actually says, over its own accepted draws.
    own = compare(pr1, pr2, "each wave's own accepted draws")

    # Intersection basis: identical cells in both waves, so the three refused cells cannot move
    # anything. Reported as a robustness line, not as the headline.
    shared = set(w1) & set(w2)
    ipr1, _ = forecasts({k: w1[k] for k in shared})
    ipr2, _ = forecasts({k: w2[k] for k in shared})
    inter = compare(ipr1, ipr2, f"cells accepted in both waves (n={len(shared)})")

    cpairs = cell_level_pairs(w1, w2)
    alpha_cell = round(krippendorff_alpha_interval(cpairs), 4)

    par_rows = []
    for pid in sorted(set(pa1) & set(pa2)):
        m1, m2 = st.median(pa1[pid]), st.median(pa2[pid])
        par_rows.append({"id": pid, "n_w1": len(pa1[pid]), "n_w2": len(pa2[pid]),
                         "median_w1": round(m1, 4), "median_w2": round(m2, 4),
                         "delta": round(m2 - m1, 4)})

    out = {
        "registered_check": "docs/preregistration.md §7.2 check 2; statistics per "
                            "docs/design/delphi-design.md §9.8 (modal-assignment change rate, "
                            "alpha between occasions)",
        "modal_assignment_mapping": "panel side per proposition = (median p over that wave's "
                                    "accepted draws) > 0.5; fixed before computing, medians at "
                                    "exactly .5 counted separately and never assigned a side",
        "not_scored_here": "neither wave is Brier-scored in this file; wave 2 postdates the CFA "
                           "and cannot carry wave 1's contamination-immune claim",
        "instrument_sha256": insts.pop(),
        "item_table_sha256": tables.pop(),
        "wave1": {"elicited_utc": t1, "n_cells_accepted": len(w1), "files": prov1},
        "wave2": {"elicited_utc": t2, "n_cells_accepted": len(w2), "files": prov2},
        "realised_gap_days": round(gap, 3),
        "registered_min_days": 30,
        "interval_satisfied": gap >= 30,
        "alpha_between_occasions": {
            "cell_level": {"alpha": alpha_cell, "n_pairs": len(cpairs),
                           "unit": "one (cell, proposition) pair over cells accepted in both waves",
                           "interpretation": "LOWER BOUND — confounds temporal drift with the "
                                             "within-cell stochasticity of a single draw; no "
                                             "within-wave replicate exists to net it out"},
            "median_level": {"alpha": own["alpha_between_occasions"],
                             "n_pairs": own["n_propositions"],
                             "unit": "one pair per proposition, each wave's median over its own "
                                     "accepted draws",
                             "interpretation": "UPPER BOUND — aggregation averages the sampling "
                                               "noise away; this is the panel-level question a "
                                               "Delphi asks, and is the headline"},
        },
        "probability_propositions": own,
        "probability_propositions_intersection_basis": inter,
        "parameter_forecasts": par_rows,
    }
    OUT.write_text(json.dumps(out, indent=2))

    print("=" * 78)
    print("TIER-2 TEMPORAL REPLICATION — wave 1 vs wave 2  (§7.2 check 2)")
    print("=" * 78)
    print(f"  wave 1 elicited {t1}   {len(w1)} cells accepted")
    print(f"  wave 2 elicited {t2}   {len(w2)} cells accepted")
    print(f"  realised gap    {gap:.3f} days (registered minimum 30)  "
          f"{'SATISFIED' if gap >= 30 else 'NOT SATISFIED'}")
    print(f"  instrument      IDENTICAL across waves  {out['instrument_sha256'][:16]}…")
    for blk in (own, inter):
        print(f"\n  basis: {blk['basis']}")
        print(f"    propositions compared          {blk['n_propositions']}")
        print(f"    modal assignment changed       {blk['modal_assignment_changes']}"
              f"/{blk['n_decidable']}  = {blk['modal_assignment_change_rate']}")
        print(f"    at exactly .5 in a wave        {blk['n_at_exactly_.5_in_a_wave']}")
        print(f"    alpha between occasions        {blk['alpha_between_occasions']}")
        print(f"    median |shift| in median p     {blk['median_abs_shift']}")
        print(f"    largest |shift|                {blk['max_abs_shift']}")
        if blk["ids_changed"]:
            print(f"    changed: {', '.join(blk['ids_changed'])}")
    print(f"\n  alpha between occasions (§9.8), both units:")
    print(f"    cell level   {alpha_cell:6.4f}   n = {len(cpairs)} (cell, proposition) pairs"
          f"   LOWER bound")
    print(f"    median level {own['alpha_between_occasions']:6.4f}   n = "
          f"{own['n_propositions']} propositions   UPPER bound, panel-level headline")

    if par_rows:
        print("\n  parameter forecasts (median point estimate)")
        for r in par_rows:
            print(f"    {r['id']:14} w1 {r['median_w1']:7.3f}  w2 {r['median_w2']:7.3f}  "
                  f"delta {r['delta']:+.3f}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")

    # Supplement S8, check-2 half. Generated rather than written by hand so it cannot drift from
    # the JSON, exactly as code/21 generates the checks 4-5 half. The manuscript promises
    # "protocols and full output" in S8 for all four checks; this is check 2's share of that.
    md = [
        "# Supplement S8 — reliability check 2, temporal replication", "",
        f"Generated by `code/28_tier2_wave_comparison.py` on {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}. "
        "Do not edit by hand.", "",
        "The identical instrument, re-elicited after the registered minimum interval. **Wave 2 "
        "postdates the CFA**, so it is not Brier-scored and carries no contamination-immune claim; "
        "wave 1 alone does. This check measures the stability of the instrument's output over "
        "thirty days, and nothing else.", "",
        "## Protocol", "",
        f"- Instrument SHA-256 `{out['instrument_sha256']}`, identical in both waves and enforced "
        "by `_gap_guard()`, which refuses to elicit on any mismatch.",
        f"- Item table SHA-256 `{out['item_table_sha256']}`, the value registered at OSF `ezjh2`.",
        f"- Wave 1 elicited {out['wave1']['elicited_utc']}, {out['wave1']['n_cells_accepted']} of 144 cells accepted.",
        f"- Wave 2 elicited {out['wave2']['elicited_utc']}, {out['wave2']['n_cells_accepted']} of 144 cells accepted.",
        f"- Realised interval **{gap:.3f} days** against a registered minimum of 30 — "
        f"{'satisfied' if gap >= 30 else 'NOT SATISFIED'}.",
        "- Every draw is an independent context: one fresh context per persona per cell.",
        "- Modal assignment = the side a proposition's median forecast falls on. The mapping was "
        "fixed in the script header before the comparison was computed; medians at exactly .5 are "
        "excluded from the denominator rather than assigned a side.", "",
        "## Result", "",
        "| statistic | own-set basis | intersection basis |",
        "|---|--:|--:|",
        f"| propositions compared | {own['n_propositions']} | {inter['n_propositions']} |",
        f"| decidable | {own['n_decidable']} | {inter['n_decidable']} |",
        f"| modal-assignment changes | {own['modal_assignment_changes']} | {inter['modal_assignment_changes']} |",
        f"| change rate | {own['modal_assignment_change_rate']} | {inter['modal_assignment_change_rate']} |",
        f"| median \\|shift\\| | {own['median_abs_shift']} | {inter['median_abs_shift']} |",
        f"| largest \\|shift\\| | {own['max_abs_shift']} | {inter['max_abs_shift']} |",
        f"| alpha, median level | {own['alpha_between_occasions']} | {inter['alpha_between_occasions']} |",
        "", f"Alpha at the **cell level** is **{alpha_cell:.4f}** over {len(cpairs)} (cell, "
        "proposition) pairs. It is a LOWER bound: with one draw per cell per wave and temperature "
        "up to 1.0, it confounds thirty-day drift with within-cell sampling noise that this design "
        "has no replicate to net out. The median-level figure is an UPPER bound, because "
        "aggregation averages that noise away. Neither is reported alone.", "",
        "## Parameter forecasts", "",
        "| id | wave 1 median | wave 2 median | delta |", "|---|--:|--:|--:|",
    ]
    for r in par_rows:
        md.append(f"| `{r['id']}` | {r['median_w1']:.3f} | {r['median_w2']:.3f} | {r['delta']:+.3f} |")
    md += ["", "## Draws not obtained", "",
           "Every cell without an accepted draw is recorded rather than dropped. Wave 2's three "
           "missing cells are **stable refusals**, not transport failures: all three are the same "
           "endpoint at the terse persona detail level, each refused on all five permitted "
           "attempts, and the model names its own deployment while declining the persona. They "
           "were not retried beyond the registered budget, because re-drawing a stable refusal "
           "manufactures the compliance the check measures. The same endpoint answered 24 of 24 "
           "thirty days earlier.", ""]
    md_path = ROOT / "supplement" / "delphi-check-2.md"
    md_path.write_text("\n".join(md))
    print(f"wrote {md_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
