#!/usr/bin/env python3
"""Build the ESS replication frame from ESS rounds 9, 10 and 11.

    python3 code/29_build_ess_frame.py

Reads the three `.sav` files, selects exactly the twenty items in the FROZEN ESS item table
(`docs/design/ess-item-table-frozen.md`), applies that table's missing-code and keying rules
mechanically, and writes one tidy CSV that `30_ess_replication.R` consumes.

WHAT THIS IS AND IS NOT. The pre-registration (§4.2) commits to "an independent replication of
model structure, not of parameter values, for the politics and morality spheres only" and NAMES NO
ESS ITEMS. The item mapping therefore is not registered, and the analysis it feeds is reported as
an UNREGISTERED replication. The table was fixed and hashed on 2026-09-08 before any
ESS model was estimated, which is the strongest guarantee still available once a registered one is
not; this script records that hash in its output so the freeze is checkable after the fact.

It computes no association of any kind. The gate of `05_build_analysis_frame.py` does not apply
here -- that gate protects the Tier-2 sequencing claim, which concerns the confirmatory CFA on the
primary sample, and the deposit it demands has since been made and verified.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
ESS_TABLE = ROOT / "docs" / "design" / "ess-item-table-frozen.md"
OUT_DIR = ROOT / "data" / "derived"

# The freeze. Recorded on first run and asserted on every later one, so an edit to the table after
# a model has been fitted cannot pass silently.
FROZEN_ESS_TABLE_SHA256 = "94ae43fde2761dd9740957eb3fbca2963d89cf0d492b01e9fe8f4575b53ec5a1"

ROUNDS = [
    (9,  "ESS9e03_3.sav",  "ed. 3.3"),
    (10, "ESS10e03_3.sav", "ed. 3.3"),
    (11, "ESS11e04_2.sav", "ed. 4.2"),
]

# Verified against the .sav value labels, not assumed. Table section "Keying, fixed here".
MISSING = {"1-5 desc": [7, 8, 9], "1-6 desc": [7, 8, 9], "0-10 asc": [77, 88, 99]}
BOUNDS  = {"1-5 desc": (1, 5), "1-6 desc": (1, 6), "0-10 asc": (0, 10)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_ess_table(path: Path) -> list[dict]:
    """| ID | Dim | Sphere | Variable | ESS11 name | Scale | R | Net flip |"""
    rows = []
    for line in path.read_text().splitlines():
        if not line.startswith("| D"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) != 8 or not re.match(r"^D[123]-[PM]\d+$", c[0]):
            continue
        rows.append({
            "id": c[0], "dim": c[1], "sphere": c[2],
            "var9": c[3].strip("`"), "var11": c[4].strip("`"),
            "scale": c[5].replace("\u2013", "-").replace("\u2014", "-"), "reverse_keyed": c[6] == "R", "flip": c[7] == "yes",
        })
    return rows


def main() -> int:
    tab_sha = sha256(ESS_TABLE)
    items = parse_ess_table(ESS_TABLE)
    if len(items) != 20:
        print(f"FATAL: parsed {len(items)} items from the frozen table, expected 20", file=sys.stderr)
        return 1
    if FROZEN_ESS_TABLE_SHA256 != "@AUTOFILL@" and tab_sha != FROZEN_ESS_TABLE_SHA256:
        print("FATAL: the frozen ESS item table has changed since the freeze.\n"
              f"  expected {FROZEN_ESS_TABLE_SHA256}\n  found    {tab_sha}\n"
              "  Fitting a model against an edited 'frozen' table is exactly what the freeze exists\n"
              "  to prevent. Do not loosen this check; disclose the edit instead.", file=sys.stderr)
        return 1

    # The flip rule is stated in the table as `flip = descending XOR reverse_keyed`. Recompute it
    # rather than trusting the column, so a typo in the table is caught rather than propagated.
    for it in items:
        descending = it["scale"].endswith("desc")
        want = descending != it["reverse_keyed"]
        if want != it["flip"]:
            print(f"FATAL: {it['id']} flip column says {it['flip']}, rule gives {want}", file=sys.stderr)
            return 1

    frames, per_round = [], []
    for rnd, fname, edition in ROUNDS:
        src = ROOT / "data" / fname
        names = {it["id"]: (it["var11"] if rnd == 11 else it["var9"]) for it in items}
        usecols = ["cntry", "essround", "idno"] + sorted(set(names.values()))
        df, _ = pyreadstat.read_sav(str(src), usecols=usecols)
        out = pd.DataFrame({"cntry": df["cntry"].astype(str).str.strip(),
                            "essround": rnd,
                            "idno": df["idno"]})
        for it in items:
            v = df[names[it["id"]]].astype("float64")
            lo, hi = BOUNDS[it["scale"]]
            v = v.mask(v.isin(MISSING[it["scale"]]))
            v = v.mask((v < lo) | (v > hi))          # anything outside the labelled range is missing
            if it["flip"]:
                v = (lo + hi) - v
            out[it["id"]] = v
        frames.append(out)
        per_round.append({"round": rnd, "file": fname, "edition": edition,
                          "sha256": sha256(src), "n_rows": int(len(out)),
                          "n_countries": int(out["cntry"].nunique()),
                          "countries": sorted(out["cntry"].unique().tolist())})
        print(f"ESS{rnd}: {len(out):,} rows, {out['cntry'].nunique()} countries")

    frame = pd.concat(frames, ignore_index=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv = OUT_DIR / "ess-replication-frame.csv"
    frame.to_csv(csv, index=False)

    ids = [it["id"] for it in items]
    meta = {
        "registered": False,
        "registered_note": ("preregistration.md §4.2 registers an ESS replication of model "
                            "STRUCTURE for the politics and morality spheres only, and names no "
                            "ESS items. The mapping is therefore unregistered; it was frozen and "
                            "hashed before any ESS model was estimated."),
        "frozen_ess_table": str(ESS_TABLE.relative_to(ROOT)),
        "frozen_ess_table_sha256": tab_sha,
        "n_items": len(items),
        "n_by_dimension": {d: sum(1 for it in items if it["dim"] == d) for d in ("D1", "D2", "D3")},
        "items": items,
        "rounds": per_round,
        "n_rows": int(len(frame)),
        "n_countries_any_round": int(frame["cntry"].nunique()),
        "missing_codes": MISSING,
        "frame_csv": str(csv.relative_to(ROOT)),
        "frame_sha256": sha256(csv),
        "complete_cases_all_20": int(frame[ids].notna().all(axis=1).sum()),
        "item_missing_rate": {i: round(float(frame[i].isna().mean()), 4) for i in ids},
    }
    (OUT_DIR / "ess-frame-meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nwrote {csv.relative_to(ROOT)}  {len(frame):,} rows x {len(ids)} items")
    print(f"frozen table sha256 {tab_sha}")
    print(f"frame sha256        {meta['frame_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
