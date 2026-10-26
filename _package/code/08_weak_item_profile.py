#!/usr/bin/env python3
"""Profile the weakly-loading indicators from the full-sample configural fit.

    python3 code/08_weak_item_profile.py [--variant primary]

WHY THIS EXISTS. code/06_cfa_invariance.R logs every standardised loading below
.30 but reports only a count. "18 of 51 indicators load below .30" is a fact
about the item pool that the paper must discuss, and a bare count cannot be
discussed: it does not say which items, in which dimension, in which response
format, or whether the weakness tracks anything systematic.

The specific question it answers is whether weakness tracks REVERSE KEYING.
Reverse-worded items are a well-documented source of method variance, and if
the weak items are disproportionately reversed then the count is partly an
artefact of wording rather than a verdict on the construct. The alternative
reading -- that a reversal is mis-specified in the item table -- would be a
coding error, and the two must be told apart before either is written up.

Reads only artefacts already written:
    supplement/analysis/cfa-<variant>-single.json   (drop_log.weak_loadings)
    data/derived/pii-frame-<variant>.meta.json      (item table + reverse flags)

Computes nothing new about the data and so needs no Tier-2 gate check.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THRESHOLD = 0.30


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="primary")
    args = ap.parse_args()

    fit_path = ROOT / f"supplement/analysis/cfa-{args.variant}-single.json"
    meta_path = ROOT / f"data/derived/pii-frame-{args.variant}.meta.json"
    for p in (fit_path, meta_path):
        if not p.exists():
            raise SystemExit(f"missing {p.relative_to(ROOT)}; run the CFA first")

    fit = json.loads(fit_path.read_text())
    meta = json.loads(meta_path.read_text())

    items = meta["items"]
    reverse = set(meta["reverse_keyed"])
    # meta["items"] is a list of dicts when written by pandas' to_dict("records");
    # index it by variable name, keeping the FIRST occurrence so that F117 -- which
    # the frozen table lists under both D2 and D3 -- does not silently overwrite.
    by_var: dict[str, dict] = {}
    for it in items:
        by_var.setdefault(it["variable"], it)

    weak = fit["drop_log"]["weak_loadings"]
    n_items = len({it["variable"] for it in items})

    rows = []
    for w in weak:
        v = w["rhs"]
        info = by_var.get(v, {})
        rows.append({
            "dimension": w["lhs"],
            "variable": v,
            "loading": round(w["est.std"], 3),
            "negative": w["est.std"] < 0,
            "reverse_keyed": v in reverse,
            "sphere": info.get("sphere", ""),
            "label": (info.get("label") or "").strip(),
        })
    rows.sort(key=lambda r: (r["dimension"], r["loading"]))

    # --- the cross-tabulation the discussion turns on -----------------------------------
    weak_vars = {r["variable"] for r in rows}
    all_vars = set(by_var)
    weak_rev = len(weak_vars & reverse)
    weak_fwd = len(weak_vars - reverse)
    ok_rev = len(reverse & all_vars) - weak_rev
    ok_fwd = len(all_vars - reverse) - weak_fwd

    def rate(a: int, b: int) -> float:
        return round(a / (a + b), 3) if (a + b) else float("nan")

    crosstab = {
        "weak_and_reverse_keyed": weak_rev,
        "weak_and_forward_keyed": weak_fwd,
        "adequate_and_reverse_keyed": ok_rev,
        "adequate_and_forward_keyed": ok_fwd,
        "weak_rate_among_reverse_keyed": rate(weak_rev, ok_rev),
        "weak_rate_among_forward_keyed": rate(weak_fwd, ok_fwd),
    }

    # --- per-sphere concentration -------------------------------------------------------
    # The paper commits to reporting per-sphere adequacy honestly and to dropping a sphere
    # rather than padding it. A sphere most of whose indicators are weak cannot carry a
    # sphere-level profile, and that has to be visible as a proportion, not inferred from a
    # list. Education is the pre-identified candidate; this neither assumes nor spares it.
    sphere_total = Counter(it.get("sphere", "") for it in by_var.values())
    sphere_weak = Counter(r["sphere"] for r in rows)
    by_sphere = {
        s: {
            "n_items": sphere_total[s],
            "n_weak": sphere_weak.get(s, 0),
            "weak_share": round(sphere_weak.get(s, 0) / sphere_total[s], 3),
        }
        for s in sorted(sphere_total)
    }

    out = {
        "source_fit": str(fit_path.relative_to(ROOT)),
        "run_utc": fit["run_utc"],
        "threshold": THRESHOLD,
        "n_items": n_items,
        "n_weak": len(rows),
        "n_negative": sum(r["negative"] for r in rows),
        "by_dimension": dict(Counter(r["dimension"] for r in rows)),
        "by_sphere": by_sphere,
        "reverse_keying_crosstab": crosstab,
        "items": rows,
        "note": (
            "Logged, not dropped. The pre-registration permits dropping an item for a "
            "standardised loading below .30, but the decision is taken once, recorded with "
            "its reason, and never taken to improve fit. Nothing here has been dropped."),
    }

    dest = ROOT / f"supplement/analysis/weak-items-{args.variant}.json"
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False))

    print(f"{len(rows)} of {n_items} indicators load below {THRESHOLD} "
          f"({out['n_negative']} negative)")
    print("  by dimension:", ", ".join(f"{k}={v}" for k, v in sorted(out["by_dimension"].items())))
    print(f"  weak among reverse-keyed: {weak_rev}/{weak_rev + ok_rev} "
          f"({crosstab['weak_rate_among_reverse_keyed']:.1%})")
    print(f"  weak among forward-keyed: {weak_fwd}/{weak_fwd + ok_fwd} "
          f"({crosstab['weak_rate_among_forward_keyed']:.1%})")
    print("\n  per sphere (weak / items):")
    for s, v in sorted(by_sphere.items(), key=lambda kv: -kv[1]["weak_share"]):
        print(f"    {s:<12s} {v['n_weak']:2d}/{v['n_items']:2d}  {v['weak_share']:.0%}")
    print()
    for r in rows:
        flag = "R" if r["reverse_keyed"] else " "
        print(f"  {r['dimension']:3s} {r['variable']:9s} {r['loading']:+.3f} {flag}  "
              f"{r['sphere']:<12s} {r['label'][:52]}")
    print(f"\nwrote {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
