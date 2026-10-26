#!/usr/bin/env python3
"""
01_audit_joint_core.py — reproduce every figure in docs/design/item-table-v2-joint-names.md

Reads the Joint EVS/WVS 2017-2022 file (GESIS ZA7505 v5.0.0, doi:10.4232/1.14320) and reports,
for the 40-country European sample:

  * the WVS7 Q-number -> integrated EVS/WVS name mapping for every item named in the design
  * per-item validity, treating EVS/WVS missing codes (-1 .. -5) as missing
  * which items are actually FIELDED in which countries (as against merely item-missing)
  * the EVS5 matrix-design structure that explains Denmark's and the Netherlands' ~50% blocks
  * the Cyprus anomaly, which is NOT matrix design

Nothing here loads the full 65 MB file: metadata reads plus one usecols pass.

Usage:  python3 code/01_audit_joint_core.py [--data DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

# The 40 European countries in the joint file. ISO 3166-1 alpha-2, plus NIR (Northern Ireland,
# carried separately from GB). AM/AZ/GE are included on a generous definition of Europe; that
# choice is pre-registered, not made after seeing fits.
EUROPE = sorted("""
AD AL AM AT AZ BA BG BY CH CY CZ DE DK EE ES FI FR GB GE GR HR HU IS IT LT LV ME MK NIR NL
NO PL PT RO RS RU SE SI SK UA
""".split())

# Every Q-number named in measurement-design.md §5, so the translation is auditable both ways.
DESIGN_Q_NUMBERS = [
    "Q246", "Q253", "Q249", "Q248", "Q8", "Q11", "Q17", "Q7", "Q30",
    "Q182", "Q184", "Q185", "Q186", "Q188", "Q241", "Q16", "Q12", "Q13",
    "Q177", "Q180", "Q178", "Q179", "Q235", "Q237", "Q238", "Q236", "Q291",
    "Q73", "Q75", "Q158", "Q159", "Q160", "Q161", "Q162", "Q163", "Q181",
    "Q69", "Q57", "Q58", "Q59", "Q60", "Q61", "Q62", "Q63",
]

# Candidate pool after retranslation. Grouped as in the item table.
CANDIDATES = {
    "D1": ["E229", "E233", "E233B", "H009", "H010", "H011",
           "A029", "A034", "A042", "A027", "D060",
           "F118", "F120", "F121", "F122", "F132", "F123", "A173"],
    "D2": ["A041", "A035", "A038", "F114A", "F115", "F116", "F117",
           "A080_01", "A080_02", "A071", "D026_05", "D026_03", "E224", "E233A"],
    "D3": ["E114", "E116", "E115", "E117", "E228", "E225", "E226", "E235", "E018",
           "E265_01", "E265_05", "E265_06", "E265_03",
           "E069_07", "E069_11", "E069_17", "E069_06", "E069_08", "E290"],
    "RADIUS": ["A165", "D001_B", "G007_18_B", "G007_33_B", "G007_34_B", "G007_35_B",
               "G007_36_B", "G255", "G256", "G257", "G062", "G063"],
    "AUX": ["E069_02", "E069_01", "E069_12", "E069_04", "E069_05", "E111_01", "E236",
            "E227", "E023", "E012", "G006", "Y002", "A124_09", "C002", "B008",
            "G052", "D081", "A030", "A032", "A039", "A066", "A067", "A068",
            "C038", "C039", "C041", "F119", "F144_02"],
}

# Item is treated as administered in a country if at least this share of rows is valid.
# Well below any plausible matrix-design share (which is ~50%), well above zero.
FIELDED_THRESHOLD = 0.20


def flat_candidates() -> list[str]:
    seen, out = set(), []
    for group in CANDIDATES.values():
        for v in group:
            if v not in seen:
                seen.add(v)
                out.append(v)
    return out


def load_correspondence(path: Path) -> pd.DataFrame:
    """WVS7 name -> joint name. Sheet has a two-row header; the real header is row 2."""
    d = pd.read_excel(path, sheet_name="EVS_WVS_Variable_Correspondence",
                      header=0, skiprows=1)
    if d.shape[1] != 8:
        raise SystemExit(f"correspondence sheet has {d.shape[1]} columns, expected 8")
    d.columns = ["joint", "joint_label", "_a", "evs", "evs_label", "_b", "wvs", "wvs_label"]
    return d[["joint", "joint_label", "evs", "wvs"]].assign(
        wvs=lambda x: x["wvs"].astype(str).str.strip()
    )


def report_translation(corr: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for q in DESIGN_Q_NUMBERS:
        hit = corr[corr["wvs"] == q]
        if hit.empty:
            hit = corr[corr["wvs"].str.startswith(q, na=False)]
        if hit.empty:
            rows.append({"wvs7": q, "joint": None, "joint_label": "*** ABSENT from joint core ***"})
        else:
            for _, r in hit.iterrows():
                rows.append({"wvs7": q, "joint": r["joint"], "joint_label": r["joint_label"]})
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "docs" / "design")
    args = ap.parse_args()

    dta = args.data / "ZA7505_v5-0-0.dta"
    xlsx = args.data / "ZA7505_VariableCorrespondence.xlsx"
    for f in (dta, xlsx):
        if not f.exists():
            raise SystemExit(f"missing input: {f}\nSee docs/data-provenance.md for access.")

    # ---- 1. translation -----------------------------------------------------------------
    corr = load_correspondence(xlsx)
    trans = report_translation(corr)
    lost = trans[trans["joint"].isna()]["wvs7"].tolist()
    print(f"[1] Translation: {len(trans) - len(lost)} of {len(DESIGN_Q_NUMBERS)} design Q-numbers "
          f"map into the joint core.")
    print(f"    ABSENT: {', '.join(lost)}")

    # ---- 2. sample ----------------------------------------------------------------------
    items = flat_candidates()
    meta_cols = ["cntry_AN", "study", "gwght", "mm_matrix_group_EVS5"]
    df, meta = pyreadstat.read_dta(str(dta), usecols=meta_cols + items)
    df["cntry_AN"] = df["cntry_AN"].astype(str).str.strip()
    eu = df[df["cntry_AN"].isin(EUROPE)].copy()
    print(f"\n[2] European sample: {len(eu):,} respondents, {eu['cntry_AN'].nunique()} countries "
          f"(of {df['cntry_AN'].nunique()} in the file).")

    # ---- 3. validity and fielding -------------------------------------------------------
    # EVS/WVS encode missingness as -1 .. -5. `notna()` returns 100% on every item and is WRONG.
    rows = []
    for v in items:
        ok = pd.to_numeric(eu[v], errors="coerce") >= 0
        per = eu.assign(_ok=ok).groupby("cntry_AN")["_ok"].mean()
        fielded = per[per >= FIELDED_THRESHOLD]
        rows.append({
            "var": v,
            "label": str(meta.column_names_to_labels.get(v, ""))[:60],
            "valid_pct": round(100 * ok.mean(), 1),
            "n_fielded": len(fielded),
            "not_fielded": ",".join(sorted(per[per < FIELDED_THRESHOLD].index)),
            "worst_cty": per.idxmin(),
            "worst_pct": round(100 * per.min(), 1),
        })
    val = pd.DataFrame(rows).sort_values("valid_pct")
    n_all = int((val["n_fielded"] == len(EUROPE)).sum())
    print(f"[3] {n_all} of {len(val)} candidate items are fielded in all {len(EUROPE)} countries.")
    for _, r in val[val["n_fielded"] < len(EUROPE)].iterrows():
        print(f"    NOT everywhere: {r['var']:10s} missing in {r['not_fielded']}")

    # ---- 4. matrix design ---------------------------------------------------------------
    mg = pd.to_numeric(eu["mm_matrix_group_EVS5"], errors="coerce")
    matrix_countries = sorted(eu.loc[mg > 0, "cntry_AN"].unique())
    print(f"\n[4] EVS5 matrix design used in: {', '.join(matrix_countries)}")
    dk = eu[eu["cntry_AN"] == "DK"]
    ct = pd.crosstab(pd.to_numeric(dk["mm_matrix_group_EVS5"], errors="coerce"),
                     pd.to_numeric(dk["E229"], errors="coerce") >= 0)
    print("    Denmark, matrix group x E229 valid — planned missingness, MCAR by design:")
    print("    " + ct.to_string().replace("\n", "\n    "))

    # ---- 5. Cyprus ----------------------------------------------------------------------
    cy = eu[eu["cntry_AN"] == "CY"]
    in_matrix = bool((pd.to_numeric(cy["mm_matrix_group_EVS5"], errors="coerce") > 0).any())
    print(f"\n[5] Cyprus (n={len(cy)}): in EVS5 matrix design? {in_matrix}")
    for v in ("A029", "A042", "A041", "E116", "E228"):
        counts = pd.to_numeric(cy[v], errors="coerce").value_counts().sort_index()
        pct = round(100 * (pd.to_numeric(cy[v], errors="coerce") >= 0).mean(), 1)
        print(f"    {v:6s} valid {pct:5.1f}%   codes {counts.to_dict()}")

    # ---- 6. write ------------------------------------------------------------------------
    args.out.mkdir(parents=True, exist_ok=True)
    trans.to_csv(args.out / "translation-wvs7-to-joint.csv", index=False)
    val.to_csv(args.out / "item-validity-europe.csv", index=False)
    print(f"\nWrote {args.out / 'translation-wvs7-to-joint.csv'}")
    print(f"Wrote {args.out / 'item-validity-europe.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
