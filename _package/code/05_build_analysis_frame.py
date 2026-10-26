#!/usr/bin/env python3
"""Build the analysis frame for the PII CFA from the joint EVS/WVS file.

    python3 code/05_build_analysis_frame.py            # refuses to run until the gate is cleared
    python3 code/05_build_analysis_frame.py --check    # report gate status only, build nothing

Reads `data/ZA7505_v5-0-0.dta`, applies the pre-registered recodes, and writes a tidy CSV that
`06_cfa_invariance.R` consumes. It computes NO association of any kind — no correlation, no
loading, no group difference — so it is not itself the confirmatory analysis. It exists so that
the R script has one documented input and the recodes live in exactly one place.

THE GATE. Pre-registration §7.1 makes the Tier-2 forecast deposit binding: the forecast must be
time-stamped independently BEFORE the CFA is run, or Tier 2 is void and must be reported as void.
Local filesystem timestamps are not evidence. This script therefore refuses to build the frame
until an OSF deposit URL for the wave-1 artefact is recorded in docs/preregistration.md §7.1.
That is deliberate friction: the sequencing requirement is the one thing in this paper that cannot
be repaired after the fact, and a note in a document is easier to walk past than a hard stop.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DTA = ROOT / "data" / "ZA7505_v5-0-0.dta"
ITEM_TABLE = ROOT / "docs" / "design" / "item-table-v2-joint-names.md"
PREREG = ROOT / "docs" / "preregistration.md"
OUT_DIR = ROOT / "data" / "derived"

REGISTERED_ITEM_TABLE_SHA256 = "2c9e0b7f215c925c2e9fc38aa164e53edcb3c390df251869b694e48aed144de5"

# §0.1 of the item table. 40 fielded; CY is dropped by Decision D1, leaving 39.
EUROPE = sorted("""AD AL AM AT AZ BA BG BY CH CY CZ DE DK EE ES FI FR GB GE GR HR HU IS IT LT LV
ME MK NIR NL NO PL PT RO RS RU SE SI SK UA""".split())
EXCLUDE_PRIMARY = ["CY"]           # Decision D1; sensitivity model puts it back
CAUCASUS = ["AM", "AZ", "GE"]      # §4.1; retained in the primary, dropped in its sensitivity

# Decision D2: 0 = "It is against democracy (spontaneous)" is a volunteered response, not a scale
# point below 1. Recoded to 1 in the primary model; the sensitivity model sets it missing instead.
DEMOCRACY_BATTERY = ["E224", "E225", "E226", "E227", "E228", "E229", "E233", "E233A", "E233B"]

# ZA7505_v5-0-0_missing.do: -1 don't know, -2 no answer, -3 not applicable,
# -4 not asked in survey, -5 other missing. All are missing; -4 is MISSING BY DESIGN
# (the EVS5 matrix design) and is retained as such rather than treated as attrition.
MISSING_CODES = [-1, -2, -3, -4, -5]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_item_table(path: Path) -> list[dict]:
    """Same parser as 03_tier2_forecast.py. Format: | ID | Sphere | Joint name | was | Label | Key | Valid |"""
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
                    "item_id": c[0], "dimension": dim, "sphere": c[1],
                    "variable": re.sub(r"[*`]", "", c[2]),
                    "label": re.sub(r"[*`\\]", "", c[4]),
                    "reverse": "R" in re.sub(r"[*`]", "", c[5]),
                })
    if not items:
        raise SystemExit(f"parsed 0 items from {path} — the table format changed; fix the parser")
    return items


# ----------------------------------------------------------------------------- the gate

def gate_status() -> tuple[bool, str]:
    """Has the Tier-2 wave-1 artefact been deposited somewhere that timestamps it independently?"""
    forecasts = sorted((ROOT / "supplement" / "tier2-forecast").glob("tier2-forecast-wave*.json"))
    if not forecasts:
        return False, "no Tier-2 forecast artefact exists — the forecast has not been elicited"

    text = PREREG.read_text()
    # Scan the whole of §7.1 (to the next same-level heading), not one subsection: the deposit
    # record grew its own #### heading, and a gate that silently stops looking is worse than no
    # gate. Anything shorter than the full section can be defeated by adding a heading.
    m = re.search(r"^### 7\.1\b.*?(?=^### |^## )", text, re.S | re.M)
    section = m.group(0) if m else ""
    if not section:
        return False, "docs/preregistration.md has no §7.1 section — cannot verify the deposit"
    if not re.search(r"^#### Tier-2 wave 1", section, re.M):
        return False, "§7.1 has no Tier-2 wave 1 record"
    if "OUTSTANDING" in section:
        return False, ("the wave-1 artefact is recorded in §7.1 but its OSF deposit is marked "
                       "OUTSTANDING — deposit it and replace that row with the deposit URL")
    # ezjh2 is the pre-registration itself and does not count as a deposit location.
    others = re.findall(r"https?://osf\.io/(\w+)", section)
    if not [o for o in others if o.lower() != "ezjh2"]:
        return False, "§7.1 records no OSF URL for the deposited artefact"
    where = sorted({o for o in others if o.lower() != "ezjh2"})
    return True, f"Tier-2 wave 1 deposited and recorded at osf.io/{', osf.io/'.join(where)}"


# ----------------------------------------------------------------------------- build

def build(args) -> int:
    items = parse_item_table(ITEM_TABLE)
    wanted = sorted({i["variable"] for i in items})
    # Verified names from code/01_audit_joint_core.py, which was run against this exact file.
    # This joint release does NOT use the SPSS-style S003/S017/S024 names.
    META = ["cntry_AN", "study", "gwght", "mm_matrix_group_EVS5"]
    keep = META + wanted
    print(f"item table : {len(items)} items, {len(wanted)} distinct variables")

    print(f"reading {DTA.name} …")
    df = pd.read_stata(DTA, columns=None, convert_categoricals=False)
    missing_vars = [c for c in keep if c not in df.columns]
    if missing_vars:
        raise SystemExit(f"variables absent from the file: {missing_vars} — STOP, do not substitute")
    df = df[keep].copy()

    # cntry_AN already carries the two-letter code; no numeric-to-label mapping is needed.
    df["country"] = df["cntry_AN"].astype(str).str.strip()

    print(f"rows: {len(df):,}   countries: {df['country'].nunique()}")

    # --- missing codes -------------------------------------------------------------------
    for v in wanted:
        df[v] = pd.to_numeric(df[v], errors="coerce")
    n_by_design = int((df[wanted] == -4).sum().sum())
    n_other_missing = int(df[wanted].isin([-1, -2, -3, -5]).sum().sum())
    df[wanted] = df[wanted].where(~df[wanted].isin(MISSING_CODES))
    print(f"missing set to NA: {n_by_design:,} by design (-4), {n_other_missing:,} other")

    # --- Decision D2 ---------------------------------------------------------------------
    batt = [v for v in DEMOCRACY_BATTERY if v in df.columns]
    n_zero = int((df[batt] == 0).sum().sum())
    if args.zero_as_missing:
        df[batt] = df[batt].where(df[batt] != 0)
        print(f"Decision D2 SENSITIVITY: {n_zero:,} zeros in the democracy battery set MISSING")
    else:
        df[batt] = df[batt].replace(0, 1)
        print(f"Decision D2 PRIMARY: {n_zero:,} zeros in the democracy battery recoded 0 -> 1")

    # --- reverse keying ------------------------------------------------------------------
    # Reversal is left to the R script, which needs the raw category counts to declare the
    # ordinal levels. Recording the flags here keeps one source of truth.
    rev = sorted({i["variable"] for i in items if i["reverse"]})
    print(f"reverse-keyed items flagged for R: {len(rev)}")

    return finish(df, items, rev, wanted, args)


def finish(df, items, rev, wanted, args) -> int:
    eu = df[df["country"].isin(EUROPE)].copy()
    print(f"European rows: {len(eu):,} in {eu['country'].nunique()} countries")
    if not args.include_cyprus:
        eu = eu[~eu["country"].isin(EXCLUDE_PRIMARY)]
        print(f"Decision D1 PRIMARY: Cyprus excluded -> {eu['country'].nunique()} countries")
    else:
        print(f"Decision D1 SENSITIVITY: Cyprus retained -> {eu['country'].nunique()} countries")

    # Registered §4.1: the three South Caucasus states are retained on a generous definition of
    # Europe, "and a sensitivity analysis excluding all three is reported". This is that variant.
    if args.exclude_caucasus:
        eu = eu[~eu["country"].isin(CAUCASUS)]
        print(f"Section 4.1 SENSITIVITY: AM/AZ/GE excluded -> "
              f"{eu['country'].nunique()} countries")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tag = ("primary"
           if not (args.include_cyprus or args.zero_as_missing or args.exclude_caucasus)
           else "sens" + ("-cy" if args.include_cyprus else "")
                       + ("-0na" if args.zero_as_missing else "")
                       + ("-nocauc" if args.exclude_caucasus else ""))
    csv = OUT_DIR / f"pii-frame-{tag}.csv"
    eu.to_csv(csv, index=False)

    meta = {
        "built_utc": pd.Timestamp.utcnow().isoformat(),
        "variant": tag,
        "source_file": DTA.name,
        "source_sha256": sha256(DTA),
        "item_table_sha256": sha256(ITEM_TABLE),
        "decisions": {
            "D1_cyprus_excluded": not args.include_cyprus,
            "D2_zero_recoded_to_one": not args.zero_as_missing,
        },
        "n_rows": int(len(eu)), "n_countries": int(eu["country"].nunique()),
        "countries": sorted(eu["country"].unique().tolist()),
        "variables": wanted,
        "reverse_keyed": rev,
        "items": items,
    }
    (OUT_DIR / f"pii-frame-{tag}.meta.json").write_text(json.dumps(meta, indent=1))
    print(f"\nwrote {csv.relative_to(ROOT)}  ({len(eu):,} rows)")
    print(f"      {(OUT_DIR / f'pii-frame-{tag}.meta.json').relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report gate status and exit")
    ap.add_argument("--include-cyprus", action="store_true",
                    help="Decision D1 sensitivity variant")
    ap.add_argument("--zero-as-missing", action="store_true",
                    help="Decision D2 sensitivity variant")
    ap.add_argument("--exclude-caucasus", action="store_true",
                    help="Section 4.1 sensitivity variant: drop AM, AZ and GE")
    args = ap.parse_args()

    live = sha256(ITEM_TABLE)
    if live != REGISTERED_ITEM_TABLE_SHA256:
        raise SystemExit(f"item table hash {live[:16]}… does not match the registered "
                         f"{REGISTERED_ITEM_TABLE_SHA256[:16]}… — stop and disclose")

    ok, why = gate_status()
    print(f"Tier-2 gate : {'CLEAR' if ok else 'BLOCKED'} — {why}")
    if args.check:
        return 0 if ok else 1
    if not ok:
        print("\nRefusing to build the analysis frame.\n"
              "  Pre-registration §7.1: the Tier-2 forecast must be independently time-stamped\n"
              "  BEFORE the CFA is run, or Tier 2 is void and must be reported as void. This is\n"
              "  the one commitment in this paper that cannot be repaired after the fact.\n"
              "  Deposit the artefact at https://osf.io/ezjh2/, record the URL in §7.1, re-run.", file=sys.stderr)
        return 2

    return build(args)


if __name__ == "__main__":
    raise SystemExit(main())
