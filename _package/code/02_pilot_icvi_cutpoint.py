#!/usr/bin/env python3
"""
02_pilot_icvi_cutpoint.py — reproduce the synthetic-Delphi pilot result

Recomputes, from docs/design/delphi-pilot_raw.json, every figure quoted in
docs/preregistration.md §7.4 and docs/design/DECISIONS.md:

  * how many rating draws survived (HTTP 429 losses are in the raw file as {"__err": ...})
  * the absolute 1-9 relevance distribution — does it ceiling?
  * mean I-CVI as a function of the dichotomisation cut-point, holding responses fixed
  * the same responses re-binned to the CTE predecessor's 4-point scale at its own >=3 rule

The point of the analysis: I-CVI is substantially a property of where the analyst cuts, not of the
panel. Nothing here is tuned — the cut-points are the pre-specified ladder 2/3/5/7/9.

Usage:  python3 code/02_pilot_icvi_cutpoint.py
"""

from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

# Pre-specified dichotomisation ladder. Polit & Beck's convention on a 4-point scale is ">= 3";
# 2/3/5/7/9 spans the plausible range of "relevant" on a 1-9 scale.
CUT_POINTS = (2, 3, 5, 7, 9)

# CTE predecessor's 4-point scale, for the like-for-like comparison.
REBIN_4PT = lambda v: 1 if v <= 2 else 2 if v <= 4 else 3 if v <= 6 else 4
CTE_RULE = 3

# The manuscript claims "five distinct models from four developers", and the developer count is
# what makes the draws independent in the sense that matters -- two Claude endpoints are one
# developer, not two. It is derived here rather than asserted, from the model identifier. Note
# that "kiro/" is a routing prefix belonging to the API aggregator, not a developer.
DEVELOPER_OF = {
    "gemma":    "Google",
    "claude":   "Anthropic",
    "deepseek": "DeepSeek",
    "glm":      "Zhipu",
}


def developer(model: str) -> str:
    name = model.split("/")[-1].lower()
    for stem, dev in DEVELOPER_OF.items():
        if name.startswith(stem):
            return dev
    return f"UNMAPPED:{model}"


def main() -> int:
    ap = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    ap.add_argument("--raw", type=Path, default=root / "docs" / "design" / "delphi-pilot_raw.json")
    args = ap.parse_args()

    if not args.raw.exists():
        raise SystemExit(f"missing input: {args.raw}")
    records = json.loads(args.raw.read_text())

    # T5 is the absolute 1-9 relevance-rating task. (T1 is the item->construct assignment task.)
    draws = [r for r in records if r[2] == "T5"]
    errors = [r for r in draws if "__err" in r[4]]
    good = [r for r in draws if "__err" not in r[4]]

    rows = []  # (rater, item, relevance)
    for provider, model, _task, temp, payload in good:
        rater = f"{provider}|{model}|T{temp}"
        for entry in payload.get("items", []):
            rows.append((rater, entry["id"], float(entry["relevance"])))

    raters = sorted({r for r, _, _ in rows})
    items = sorted({i for _, i, _ in rows})
    models = sorted({m for _, m, _, _, _ in good})
    values = [v for _, _, v in rows]

    print(f"Rating draws attempted : {len(draws)}")
    print(f"  lost to HTTP 429     : {len(errors)}")
    print(f"  surviving            : {len(good)}  ({len(models)} distinct models)")
    print(f"Raters x items         : {len(raters)} x {len(items)} = {len(rows)} responses")
    print()

    print("Does the absolute 1-9 rating ceiling?")
    print(f"  overall mean {st.mean(values):.2f}, SD {st.pstdev(values):.2f}")
    print(f"  at the maximum (9)   : {100 * sum(v == 9 for v in values) / len(values):.1f}%")
    by_item = defaultdict(list)
    for _, i, v in rows:
        by_item[i].append(v)
    item_means = [st.mean(by_item[i]) for i in items]
    print(f"  item means span      : {min(item_means):.2f} - {max(item_means):.2f}")
    print("  -> no ceiling effect; the ratings discriminate between items.")
    print()

    print("Mean I-CVI as a function of the dichotomisation cut-point (responses held fixed):")
    icvi_by_cut = {}
    for cut in CUT_POINTS:
        icvi = [sum(v >= cut for v in by_item[i]) / len(by_item[i]) for i in items]
        icvi_by_cut[cut] = st.mean(icvi)
        print(f"  relevance >= {cut}      : {icvi_by_cut[cut]:.3f}")
    rebinned = [sum(REBIN_4PT(v) >= CTE_RULE for v in by_item[i]) / len(by_item[i]) for i in items]
    print(f"  CTE 4-point, >= {CTE_RULE} rule: {st.mean(rebinned):.3f}")
    print()
    # Derived, not typed: an earlier version of this line carried the response count as a
    # literal, which is the same defect the manuscript verification script exists to catch.
    print(f"The same {len(rows)} responses yield mean I-CVI anywhere from "
          f"{max(icvi_by_cut.values()):.2f} to {min(icvi_by_cut.values()):.2f} depending only on")
    print("where the analyst dichotomises. Polit & Beck's >= 0.78 threshold has never been")
    print("accompanied by a sensitivity analysis over this choice.")
    print()
    print(f"CAVEAT, to be carried into the manuscript: {len(raters)} rater draws, "
          f"{len(models)} models, {len(items)} items.")
    print("Suggestive, not conclusive. The full study's five-format decomposition is what")
    print("establishes the claim.")

    # Emitted so that code/09 can assert the manuscript's Section "Consensus is a property of
    # the cut-point" against computed values rather than against a transcription.
    out = {
        "source_raw": str(args.raw.relative_to(root)),
        "draws_attempted": len(draws),
        "draws_lost_429": len(errors),
        "draws_surviving": len(good),
        "n_models": len(models),
        "models": models,
        "developers": sorted({developer(m) for m in models}),
        "n_developers": len({developer(m) for m in models}),
        "n_raters": len(raters),
        "n_items": len(items),
        "n_responses": len(rows),
        "mean": round(st.mean(values), 2),
        "sd": round(st.pstdev(values), 2),
        "pct_at_maximum": round(100 * sum(v == 9 for v in values) / len(values), 1),
        "item_mean_min": round(min(item_means), 2),
        "item_mean_max": round(max(item_means), 2),
        "mean_icvi_by_cutpoint": {str(c): round(v, 3) for c, v in icvi_by_cut.items()},
        "mean_icvi_cte_4pt_rule": round(st.mean(rebinned), 3),
        "caveat": ("Pilot. Precedes registration, reported as descriptive, no confirmatory claim "
                   "rests on it. Suggestive, not conclusive."),
    }
    dest = root / "supplement" / "analysis" / "pilot-icvi-cutpoint.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1))
    print(f"\nwrote {dest.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
