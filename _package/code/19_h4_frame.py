#!/usr/bin/env python3
"""
19_h4_frame.py -- the analysis frame for H4, the Jellyby prediction.

    python3 code/19_h4_frame.py [--variant primary]

WHY A SEPARATE FRAME. H4 is a registered hypothesis (`preregistration.md` §6.5)
that the manuscript does not report, and it is the only unreported one that is
actually runnable: it is a within-individual claim and needs no country-level
scores. But eight of its ten probe indicators are not in
`data/derived/pii-frame-primary.csv`, because that frame carries the 51 frozen
PII indicators and nothing else.

The obvious move -- add them to `code/05` -- would be wrong. The manuscript
quotes the SHA-256 of that frame, the Tier-2 deposit gate keys on `code/05`, and
every CFA in the paper was fitted from that exact file. Rebuilding it to add
variables for a side analysis would invalidate a checksum the paper publishes for
a reason that has nothing to do with the confirmatory models. So H4 gets its own
frame, built by the same rules, and the PII frame is not touched.

SAME RULES, DELIBERATELY: the same source file, the same missing codes, the same
European country list, and the same Cyprus exclusion, so that the H4 sample is
the H1/H2 sample and a difference between them cannot be a sampling artefact.
Decision D2 does not arise -- no democracy-battery item is a probe indicator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DTA = ROOT / "data" / "ZA7505_v5-0-0.dta"
OUT_DIR = ROOT / "data" / "derived"
MISSING_CODES = [-1, -2, -3, -4, -5]

# preregistration.md §6.5, verbatim. Three probes, each with a concrete and an anonymous pole.
PROBES = {
    "trust":   {"concrete": ["D001_B", "G007_33_B"],
                "anonymous": ["G007_34_B", "G007_36_B"]},
    "belong":  {"concrete": ["G255", "G256"],
                "anonymous": ["G062", "G063"]},
    "act_for": {"concrete": ["D026_05"],
                "anonymous": ["A080_01"]},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="primary")
    args = ap.parse_args()

    # The PII frame is the authority on which respondents are in the analysis sample and which
    # items D1 and D2 comprise. Reading it rather than re-deriving both keeps one source of
    # truth and makes the two frames provably the same sample.
    pii_meta = json.loads((OUT_DIR / f"pii-frame-{args.variant}.meta.json").read_text())
    pii = pd.read_csv(OUT_DIR / f"pii-frame-{args.variant}.csv")
    d12 = sorted({i["variable"] for i in pii_meta["items"] if i["dimension"] in ("D1", "D2")})
    countries = sorted(pii["country"].unique())
    print(f"PII frame: {len(pii):,} rows, {len(countries)} countries, "
          f"{len(d12)} D1/D2 indicators")

    probe_vars = [v for p in PROBES.values() for pole in p.values() for v in pole]
    keep = ["cntry_AN", "study", "gwght"] + sorted(set(probe_vars) | set(d12))

    print(f"reading {DTA.name} …")
    df = pd.read_stata(DTA, columns=None, convert_categoricals=False)
    absent = [c for c in keep if c not in df.columns]
    if absent:
        raise SystemExit(f"variables absent from the file: {absent} — STOP, do not substitute")
    df = df[keep].copy()
    df["country"] = df["cntry_AN"].astype(str).str.strip()

    num = sorted(set(probe_vars) | set(d12))
    for v in num:
        df[v] = pd.to_numeric(df[v], errors="coerce")
    df[num] = df[num].where(~df[num].isin(MISSING_CODES))

    df = df[df["country"].isin(countries)].copy()
    print(f"restricted to the PII country set: {len(df):,} rows, "
          f"{df['country'].nunique()} countries")
    if df["country"].nunique() != len(countries):
        raise SystemExit("the H4 frame lost a country the PII frame has; the samples differ")

    # Reverse keying: only PII indicators carry registered flags, and no probe item does.
    # Recorded rather than silently assumed, because a probe reversed by accident would
    # invert the very sign H4 is about.
    rev = [v for v in pii_meta["reverse_keyed"] if v in df.columns]

    cov = {v: {"n_valid": int(df[v].notna().sum()),
               "pct_valid": round(100 * df[v].notna().mean(), 2),
               "n_categories": int(df[v].nunique(dropna=True)),
               "min": None if df[v].isna().all() else float(df[v].min()),
               "max": None if df[v].isna().all() else float(df[v].max())}
           for v in probe_vars}
    print("\nprobe indicator coverage")
    for v in probe_vars:
        c = cov[v]
        print(f"  {v:<12} valid {c['n_valid']:>6,} ({c['pct_valid']:>5.1f}%)  "
              f"{c['n_categories']} categories  range {c['min']}-{c['max']}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv = OUT_DIR / f"h4-frame-{args.variant}.csv"
    df[["country", "gwght"] + num].to_csv(csv, index=False)

    meta = {
        "built_utc": pd.Timestamp.utcnow().isoformat(),
        "variant": args.variant,
        "purpose": "H4 (Jellyby prediction), preregistration.md 6.5. Separate from the PII "
                   "frame so that frame's published SHA-256 stays valid.",
        "source_file": DTA.name,
        "source_sha256": sha256(DTA),
        "pii_frame_sha256": pii_meta["source_sha256"],
        "same_sample_as_pii_frame": True,
        "n_rows": int(len(df)),
        "n_countries": int(df["country"].nunique()),
        "probes": PROBES,
        "d1_d2_variables": d12,
        "reverse_keyed": rev,
        "probe_coverage": cov,
    }
    (OUT_DIR / f"h4-frame-{args.variant}.meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nwrote {csv.relative_to(ROOT)} ({len(df):,} rows) and its metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
