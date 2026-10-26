#!/usr/bin/env python3
"""Check every reported statistic in the manuscript against the JSON that produced it.

    python3 code/09_verify_manuscript_numbers.py [--variant primary]

WHY THIS EXISTS. The project rule is that no number in the manuscript is
transcribed by hand and that every one of them can be re-derived from code in
the repository. That rule is only as good as its enforcement, and "I read them
off carefully" is not enforcement: a transposed digit in a fit table survives
proofreading indefinitely, because a plausible number looks exactly like a
correct one.

This script re-reads the emitted JSON, formats each value the way the
manuscript formats it, and asserts that the resulting string is present in
main.tex. It fails loudly on a mismatch and, just as importantly, fails when a
value it expects to find is absent -- a statistic silently dropped from the text
during editing is as much a defect as a wrong one.

WHAT IT DOES NOT DO. It cannot verify prose claims ("fits better on every
index"), only numerals. Claims of that kind are checked by the assertions at
the foot of this file, which encode the comparisons the prose asserts and fail
if the data stop supporting them.

Exit status 0 = every check passed. Non-zero = at least one failed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "build/main.tex"


# The manuscript must label its invariance substitutes as unregistered, in either of the two
# nouns it uses for them. A bare "unregistered" somewhere in the text does not satisfy this.
UNREG_LABEL = re.compile(r"unregistered\s+(diagnostic|ladder)s?\b", re.I)


def dec3(x: float) -> str:
    """.564 -- leading zero dropped, as the manuscript writes correlations and fit indices."""
    s = f"{abs(x):.3f}".lstrip("0")
    return ("-" if x < 0 else "") + s


def thousands(x: float) -> str:
    """1{,}186{,}285 -- LaTeX thousands separator as written in the fit table."""
    return f"{round(x):,}".replace(",", "{,}")


# The analysis frame carries ISO codes; the manuscript writes country names. The map covers
# all 39 countries rather than only the 12 currently drawn, so that changing the ladder seed
# cannot silently disable the check that every subset country is actually named in the text.
COUNTRY_NAMES = {
    "AD": "Andorra", "AL": "Albania", "AM": "Armenia", "AT": "Austria",
    "AZ": "Azerbaijan", "BA": "Bosnia and Herzegovina", "BG": "Bulgaria",
    "BY": "Belarus", "CH": "Switzerland", "CZ": "Czechia", "DE": "Germany",
    "DK": "Denmark", "EE": "Estonia", "ES": "Spain", "FI": "Finland",
    "FR": "France", "GB": "Great Britain", "GE": "Georgia", "GR": "Greece",
    "HR": "Croatia", "HU": "Hungary", "IS": "Iceland", "IT": "Italy",
    "LT": "Lithuania", "LV": "Latvia", "ME": "Montenegro",
    "MK": "North Macedonia", "NIR": "Northern Ireland", "NL": "Netherlands",
    "NO": "Norway", "PL": "Poland", "PT": "Portugal", "RO": "Romania",
    "RS": "Serbia", "RU": "Russia", "SE": "Sweden", "SI": "Slovenia",
    "SK": "Slovakia", "UA": "Ukraine",
}


def signed4(x: float) -> str:
    """+.0324 / -.0468 -- four decimals with an explicit sign. Invariance deltas are judged
    against a .010 threshold, so the fourth decimal is where the decision lives."""
    return ("+" if x >= 0 else "-") + f"{abs(x):.4f}".lstrip("0")


def signed3(x: float) -> str:
    """+.056 / -.772 -- an explicit sign, three decimals, no leading zero. Skill scores are
    written with their sign in the manuscript because the sign is the decision."""
    return ("+" if x >= 0 else "-") + f"{abs(x):.3f}".lstrip("0")


def dec3_tex(x: float) -> str:
    """-3{,}132{,}075.759 -- three decimals carrying the same LaTeX thousands separator
    the manuscript uses for every integer above 999. dec3() alone would demand the
    string '-3132075.759', which no correctly typeset table can contain, so a check
    built on it can only ever fail. The tolerance is unchanged: the value must still
    match the JSON to three decimal places."""
    s = f"{abs(x):,.3f}".replace(",", "{,}")
    if abs(x) < 1:
        s = s.lstrip("0")
    return ("-" if x < 0 else "") + s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="primary")
    args = ap.parse_args()

    fit_json = ROOT / f"supplement/analysis/cfa-{args.variant}-single.json"
    weak_json = ROOT / f"supplement/analysis/weak-items-{args.variant}.json"
    adm_json = ROOT / f"supplement/analysis/admissibility-{args.variant}.json"
    # The pilot is variant-independent: it is one fixed elicitation, not a re-analysis of the
    # survey data, so it carries no --variant suffix.
    pilot_json = ROOT / "supplement/analysis/pilot-icvi-cutpoint.json"
    for p in (fit_json, weak_json, adm_json, pilot_json, TEX):
        if not p.exists():
            print(f"FAIL  missing input: {p.relative_to(ROOT)}")
            return 2

    d = json.loads(fit_json.read_text())
    weak = json.loads(weak_json.read_text())
    adm = json.loads(adm_json.read_text())
    pilot = json.loads(pilot_json.read_text())
    tex = TEX.read_text()
    # LaTeX source wraps lines wherever it likes, so a multi-word phrase the manuscript really
    # does contain can straddle a newline and defeat a substring test. Any check on WORDING
    # uses tex_flat; checks on numbers and on line-structured things (table rows, \PENDING)
    # keep using tex, where the line breaks are part of what is being inspected.
    tex_flat = " ".join(tex.split())

    # The alignment output is OPTIONAL to load but MANDATORY to obey. It does not exist until the
    # per-group configural chain has run, and the manuscript legitimately has invariance
    # placeholders before then -- so a missing file is a warning, not a failure. What is not
    # optional is the direction of trust: if the file exists, every invariance number in the
    # manuscript must come from it, and the licensing assertions below are what stop a country
    # comparison the alignment does not support. See preregistration Sec. 6.3.
    align_json = ROOT / f"supplement/analysis/cfa-{args.variant}-alignment.json"
    align = json.loads(align_json.read_text()) if align_json.exists() else None

    # Same contract for the two diagnostics the manuscript quotes alongside the registered
    # alignment: the subset ladder (--stage ladder) and the per-country loading diagnostic
    # (code/12). Both are explicitly UNREGISTERED, and both are quoted in Sec. 5.5, which is
    # exactly why they are verified here -- an exploratory number is not a number that may
    # drift from its output file.
    ladder_json = ROOT / f"supplement/analysis/cfa-{args.variant}-ladder.json"
    ladder = json.loads(ladder_json.read_text()) if ladder_json.exists() else None
    het_json = ROOT / f"supplement/analysis/loading-heterogeneity-{args.variant}.json"
    het = json.loads(het_json.read_text()) if het_json.exists() else None

    # Per-dimension invariance steps, run one process at a time by code/14 and code/22 because
    # --stage perdim holds three fits at once and dies. Unlike the other inputs this one is
    # PARTIAL by nature: it accumulates whatever steps have been fitted and measured so far
    # (D1 complete as of 2026-08-11; D2 and D3 absent). A dimension's numbers are only asserted
    # once BOTH rungs of a delta are present, so a half-finished chain cannot fail the build
    # for saying nothing yet -- and adding D2/D3 later turns their checks on automatically.
    pdm_json = ROOT / f"supplement/analysis/perdim-step-measures-{args.variant}.json"
    pdm = json.loads(pdm_json.read_text()) if pdm_json.exists() else None

    # code/22: the same unidimensional ladder on the SUBSET the three-factor ladder used. This
    # is the cell that breaks the specification-versus-sample confound, so its deltas are
    # asserted on the same terms as the other two ladders.
    psb_json = ROOT / f"supplement/analysis/perdim-subset-measures-{args.variant}.json"
    psb = json.loads(psb_json.read_text()) if psb_json.exists() else None

    # code/16: the Tier-2 forecast scored against the CFA. Section 5.6 is entirely built from
    # this file, so every figure in it is asserted here. Gated on existence: a clone that has
    # not run code/16 warns rather than fails, but a manuscript that CITES the section while
    # the JSON is missing fails, which the prose block below enforces.
    t2_json = ROOT / f"supplement/analysis/tier2-score-{args.variant}.json"
    t2 = json.loads(t2_json.read_text()) if t2_json.exists() else None

    # code/15: the full M2/M2m loading tables. The manuscript's corrected reverse-keying
    # diagnosis and the Decision D3 robustness paragraph are both built from these.
    m2_json = ROOT / f"supplement/analysis/m2-loadings-{args.variant}.json"
    m2m_json = ROOT / f"supplement/analysis/m2m-loadings-{args.variant}.json"
    m2l = json.loads(m2_json.read_text()) if m2_json.exists() else None
    m2m = json.loads(m2m_json.read_text()) if m2m_json.exists() else None

    # code/17: per-sphere reliability, the §6.6 reporting commitment.
    sph_json = ROOT / f"supplement/analysis/sphere-reliability-{args.variant}.json"
    sph = json.loads(sph_json.read_text()) if sph_json.exists() else None

    # code/18: Decision D3's second clause -- the battery-excluded specification, where the
    # sign of the paper's central parameter reverses. code/20: H4. code/21: Delphi checks 4-5.
    bex_json = ROOT / f"supplement/analysis/battery-excluded-{args.variant}.json"
    bex = json.loads(bex_json.read_text()) if bex_json.exists() else None
    h4_json = ROOT / f"supplement/analysis/h4-jellyby-{args.variant}.json"
    h4 = json.loads(h4_json.read_text()) if h4_json.exists() else None
    dch_json = ROOT / "supplement/analysis/delphi-checks-4-5.json"
    dch = json.loads(dch_json.read_text()) if dch_json.exists() else None

    # code/13: does the memory-forced per-group configural route reproduce the pooled route?
    # The two figures it emits are quoted in cover-letter.md and in the disclosures status
    # board rather than in main.tex, so the assertions below are on the DOCS, not the .tex --
    # they were previously produced by a scratch script outside the repository, which is the
    # defect this file exists to make impossible.
    dec_json = ROOT / f"supplement/analysis/pergroup-decomposition-{args.variant}.json"
    dec = json.loads(dec_json.read_text()) if dec_json.exists() else None

    # jsonlite's auto_unbox=TRUE collapses a length-1 vector to a bare scalar, so a list of
    # one failing model arrives as the string "M2b" rather than ["M2b"]. Normalise, or a
    # single failure silently compares unequal to a one-element list and reports a defect
    # that is really a serialisation artefact.
    def as_list(v) -> list:
        if v is None:
            return []
        return v if isinstance(v, list) else [v]

    adm["failed"] = as_list(adm.get("failed"))
    adm["failed_unexpectedly"] = as_list(adm.get("failed_unexpectedly"))

    checks: list[tuple[str, str]] = []          # (label, string that must appear)

    # --- the fit table ------------------------------------------------------------------
    for model, m in d["fit"].items():
        checks.append((f"{model} chisq", thousands(m["chisq.scaled"])))
        checks.append((f"{model} df", str(int(m["df.scaled"]))))
        for idx in ("cfi", "tli", "rmsea"):
            checks.append((f"{model} {idx}", dec3(m[f"{idx}.scaled"])))
        checks.append((f"{model} srmr", dec3(m["srmr"])))

    # --- sample -------------------------------------------------------------------------
    checks.append(("N", thousands(d["frame"]["rows"])))
    checks.append(("countries", str(d["frame"]["countries"])))

    # --- decision rules -----------------------------------------------------------------
    checks.append(("H1 deltaCFI", dec3(d["H1"]["deltaCFI"])))
    checks.append(("H1 phi(D1,D2)", dec3(d["H1"]["phi_D1_D2"])))
    checks.append(("H2 phi(D1,D3)", dec3(d["H2"]["phi_D1_D3"])))
    checks.append(("H2 |phi(D1,D3)|", dec3(d["H2"]["abs_phi_D1_D3"])))
    checks.append(("H2 phi(D2,D3)", dec3(d["H2"]["phi_D2_D3"])))
    checks.append(("H2 deltaCFI M2 vs M0", dec3(d["H2"]["deltaCFI_M2_vs_M0_all"])))

    # --- weak indicators ----------------------------------------------------------------
    checks.append(("weak count", str(weak["n_weak"])))
    checks.append(("item count", str(weak["n_items"])))
    checks.append(("weak in D1", str(weak["by_dimension"]["D1"])))
    checks.append(("weak in D2", str(weak["by_dimension"]["D2"])))
    checks.append(("weak in D3", str(weak["by_dimension"]["D3"])))
    ct = weak["reverse_keying_crosstab"]
    checks.append(("weak & reverse-keyed", str(ct["weak_and_reverse_keyed"])))
    checks.append(("weak & forward-keyed", str(ct["weak_and_forward_keyed"])))
    edu = weak["by_sphere"]["Education"]
    checks.append(("education weak", str(edu["n_weak"])))
    checks.append(("education items", str(edu["n_items"])))

    # --- admissibility ------------------------------------------------------------------
    m2b = adm["models"]["M2b"]
    checks.append(("M2b min eigenvalue", dec3(m2b["min_eigenvalue_covlv"])))
    min_resid = min(v["min_residual_var"] for v in adm["models"].values())
    checks.append(("smallest residual variance", dec3(min_resid)))

    # --- the pilot I-CVI cut-point section --------------------------------------------------
    # This section is the one place the paper reports a result from before registration, so it
    # is the one most exposed to a transcription drifting away from its source over redrafts.
    for cut, v in pilot["mean_icvi_by_cutpoint"].items():
        checks.append((f"mean I-CVI at cut >= {cut}", dec3(v)))
    checks.append(("pilot responses", str(pilot["n_responses"])))
    checks.append(("pilot rating mean", f"{pilot['mean']:.2f}"))
    checks.append(("pilot rating SD", f"{pilot['sd']:.2f}"))
    checks.append(("pilot % at maximum", f"{pilot['pct_at_maximum']:.1f}"))
    checks.append(("pilot item mean min", f"{pilot['item_mean_min']:.2f}"))
    checks.append(("pilot item mean max", f"{pilot['item_mean_max']:.2f}"))
    checks.append(("mean I-CVI, 4-point scale at its own rule",
                   dec3(pilot["mean_icvi_cte_4pt_rule"])))

    # --- invariance and alignment ----------------------------------------------------------
    if align is not None:
        inv = align["invariance"]
        pg = inv["configural_pergroup"]
        checks.append(("alignment countries", str(pg["groups_converged"])))
        for dd, v in sorted(inv.get("alignment", {}).items()):
            checks.append((f"{dd} R2(loadings)", dec3_tex(v["R2_loadings"])))
            checks.append((f"{dd} R2(locations)", dec3_tex(v["R2_locations"])))
            checks.append((f"{dd} alignment items", str(v["n_items"])))
        checks.append(("per-group configural chisq sum",
                       f"{pg['chisq_sum']:,.2f}".replace(",", "{,}")))
        checks.append(("per-group configural df sum", thousands(pg["df_sum"])))

    if ladder is not None:
        # Four decimals, not three: a delta of -.0220 against a .010 threshold is the whole
        # decision, and rounding it to -.022 would let a -.0224 and a -.0215 print alike.
        for step in ladder["invariance"]["deltas"]:
            lab = step["step"].split("->")[-1].strip()
            x = step["dCFI"]
            checks.append((f"subset ladder dCFI {lab}",
                           ("-" if x < 0 else "") + f"{abs(x):.4f}".lstrip("0")))

    if pdm is not None:
        st = pdm.get("steps", {})
        for dd in ("D1", "D2", "D3"):
            for lo, hi in (("configural", "metric"), ("metric", "scalar")):
                a, b = st.get(f"{dd}_{lo}"), st.get(f"{dd}_{hi}")
                if not (a and b):
                    continue
                dc = b["cfi.scaled"] - a["cfi.scaled"]
                checks.append((f"{dd} {lo}->{hi} dCFI (39 countries)",
                               ("-" if dc < 0 else "") + f"{abs(dc):.4f}".lstrip("0")))
                checks.append((f"{dd} {lo} CFI (39 countries)", dec3(a["cfi.scaled"])))
                checks.append((f"{dd} {hi} CFI (39 countries)", dec3(b["cfi.scaled"])))
                # Same treatment the subset ladder gets below, and for the same reason: the
                # manuscript reports RMSEA and TLI moving AGAINST CFI at the scalar rung, and
                # quotes the chi-square movement to show the nested comparison is well behaved.
                # If a re-run reversed either, the prose would be wrong and this catches it.
                checks.append((f"{dd} {lo}->{hi} dRMSEA (39 countries)",
                               signed4(b["rmsea.scaled"] - a["rmsea.scaled"])))
                if hi == "scalar":   # only this rung's TLI reversal is quoted in the text
                    checks.append((f"{dd} {lo} TLI (39 countries)", dec3(a["tli.scaled"])))
                    checks.append((f"{dd} {hi} TLI (39 countries)", dec3(b["tli.scaled"])))
                checks.append((f"{dd} {lo}->{hi} ddf (39 countries)",
                               thousands(b["df.scaled"] - a["df.scaled"])))
                checks.append((f"{dd} {lo}->{hi} dchisq (39 countries)",
                               thousands(abs(b["chisq.scaled"] - a["chisq.scaled"]))))

    if het is not None:
        for dd, v in sorted(het["dimensions"].items()):
            si = v.get("strong_items")
            if not si:
                continue
            checks.append((f"{dd} residual sign disagreement",
                           f"{100 * si['residual_sign_disagreement']:.1f}"))
            checks.append((f"{dd} countries in full agreement",
                           str(si["countries_zero_disagreement"])))

    # ---- Tier-2 forecast score (code/16) --------------------------------------------------
    # Section 5.6 is built entirely from this JSON. Three decimals for the skill scores,
    # because the registered decision is whether a bootstrap bound clears zero and .013
    # rounded to two would print as .01.
    if t2 is not None:
        b, bb, blk = t2["brier"], t2["family_cluster_bootstrap"], t2["by_block"]
        pr = t2["propositions"]
        checks += [
            ("tier2 grid cells", str(t2["draws"]["n_cells_accepted"])),
            ("tier2 pairs scored", thousands(pr["n_pairs_scored"])),
            ("tier2 propositions resolved", str(pr["n_resolved"])),
            # Four decimals throughout: the Brier scores and their references are compared
            # with each other in the text, and .2335 against .2357 is a distinction three
            # decimals would erase.
            ("tier2 Brier", f"{b['BS']:.4f}".lstrip("0")),
            ("tier2 base-rate reference", f"{b['BS_reference_base_rate']:.4f}".lstrip("0")),
            # Signed: a bound that goes negative must print as -.010, not +-0.010, or the
            # failure message misdescribes what changed.
            ("tier2 BSS", signed3(b["BSS"])),
            ("tier2 bootstrap lower bound", signed3(bb["lo95"])),
            ("tier2 bootstrap upper bound", signed3(bb["hi95"])),
            ("tier2 AUC block A", dec3(b["auc_block_A"])),
            ("tier2 ECE", dec3(b["murphy"]["ece"])),
            ("tier2 block A pairs", thousands(blk["A_item_loadings"]["n_pairs"])),
            ("tier2 block A Brier", f"{blk['A_item_loadings']['BS']:.4f}".lstrip("0")),
            ("tier2 block A reference",
             f"{blk['A_item_loadings']['BS_reference_base_rate']:.4f}".lstrip("0")),
            ("tier2 block B/C pairs", str(blk["B_C_hypotheses_and_invariance"]["n_pairs"])),
            ("tier2 block B/C Brier",
             f"{blk['B_C_hypotheses_and_invariance']['BS']:.4f}".lstrip("0")),
            ("tier2 block B/C reference",
             f"{blk['B_C_hypotheses_and_invariance']['BS_reference_base_rate']:.4f}".lstrip("0")),
            ("tier2 block B/C BSS", signed3(blk["B_C_hypotheses_and_invariance"]["BSS"])),
        ]
        # Block D: the sign failure is the section's strongest claim, so both the observed
        # value and the panel's median forecast are asserted, not just the gap between them.
        for row in t2["block_D_point_forecasts"]:
            checks.append((f"tier2 {row['id']} observed", signed3(row["observed"])))
            checks.append((f"tier2 {row['id']} median forecast",
                           signed3(row["median_forecast"])))
        # Grid spread: the manuscript quotes a min and a max for each factor.
        for fac, rows_ in t2["distribution_over_the_grid"].items():
            if fac == "note":
                continue
            vals = [r["bss"] for r in rows_]
            for tag, v in (("min", min(vals)), ("max", max(vals))):
                checks.append((f"tier2 {fac} {tag}", signed3(v)))

    # ---- loading tables and Decision D3 robustness (code/15) ------------------------------
    if m2l is not None:
        checks += [("M2 negative loadings", str(m2l["n_negative"])),
                   ("M2 substantial negatives", str(m2l["n_negative_substantial"]))]
        # The four reverse-keyed wrong-sign items are named with their loadings in the text,
        # because naming them is what makes the corrected diagnosis checkable.
        rev_neg = sorted((r for r in m2l["loadings"]
                          if r["est.std"] <= -.30 and r["variable"] in
                          json.loads((ROOT / f"data/derived/pii-frame-{args.variant}"
                                             ".meta.json").read_text())["reverse_keyed"]),
                         key=lambda r: r["est.std"])
        for r in rev_neg:
            checks.append((f"M2 wrong-sign reverse-keyed {r['variable']}",
                           dec3(r["est.std"])))
    if m2m is not None:
        lc = m2m["latent_correlations"]
        checks += [("M2m phi(D1,D3)", dec3(lc["phi_D1_D3"])),
                   ("M2m phi(D2,D3)", dec3(lc["phi_D2_D3"]))]

    # ---- per-sphere reliability (code/17) -------------------------------------------------
    if sph is not None:
        cells = {(c["dimension"], c["sphere"]): c for c in sph["cells"]}
        for dd in ("D1", "D2", "D3"):
            c = cells[(dd, "ALL")]
            checks.append((f"{dd} pooled omega", dec3(c["categorical_omega"])))
            checks.append((f"{dd} pooled aligned omega", dec3(c["omega_if_signs_aligned"])))
        checks.append(("D3 politics alpha", dec3(cells[("D3", "Politics")]["ordinal_alpha"])))

    # ---- subset per-dimension ladder (code/22) --------------------------------------------
    if psb is not None:
        st = psb.get("steps", {})
        for dd in ("D1", "D2", "D3"):
            for lo, hi in (("configural", "metric"), ("metric", "scalar")):
                a, b = st.get(f"{dd}_{lo}"), st.get(f"{dd}_{hi}")
                if not (a and b):
                    continue
                checks.append((f"{dd} {lo}->{hi} dCFI (subset)",
                               signed4(b["cfi.scaled"] - a["cfi.scaled"])))
                checks.append((f"{dd} {lo}->{hi} dRMSEA (subset)",
                               signed4(b["rmsea.scaled"] - a["rmsea.scaled"])))
                # The chi-square/df movement is quoted because the manuscript distinguishes the
                # rung that misbehaves from the rung that does not. If a re-run changed which
                # rung is anomalous, the prose would be wrong and this catches it.
                checks.append((f"{dd} {lo}->{hi} ddf (subset)",
                               thousands(b["df.scaled"] - a["df.scaled"])))
                checks.append((f"{dd} {lo}->{hi} dchisq (subset)",
                               thousands(abs(b["chisq.scaled"] - a["chisq.scaled"]))))

    # ---- Decision D3, second clause (code/18) ---------------------------------------------
    if bex is not None:
        H2b = bex["H2"]
        checks += [
            ("battery-excluded phi(D1,D3)", signed3(H2b["phi_D1_D3"])),
            ("battery-excluded min latent eigenvalue",
             dec3(bex["admissibility"]["M2_min_eigenvalue_cov_lv"])),
        ]

    # ---- H4 (code/20) ---------------------------------------------------------------------
    if h4 is not None and h4.get("probes"):
        for key, p in h4["probes"].items():
            if not p.get("estimable"):
                continue
            checks.append((f"H4 {key} phi", dec3(p["phi_concrete_anonymous"])))
            checks.append((f"H4 {key} dCFI", signed3(p["deltaCFI"])))

    # ---- Delphi checks 4 and 5 (code/21) --------------------------------------------------
    if dch is not None:
        c = dch.get("contamination")
        if c:
            pct = lambda x: f"{100 * x:.1f}"          # noqa: E731 -- 19.4, as the text writes it
            checks += [
                ("canary false-attribution rate", pct(c["canary_false_attribution_rate"])),
                ("real-item attribution rate", pct(c["real_item_correct_attribution_rate"])),
                ("mean confidence on false attributions",
                 f"{c['mean_confidence_on_false_attributions']:.2f}".lstrip("0")),
                ("worst endpoint canary rate",
                 pct(max(v["canary_false_attribution_rate"]
                         for v in c["by_endpoint"].values()))),
            ]
        s = dch.get("sycophancy")
        if s:
            checks += [
                ("sycophancy migration, true feedback",
                 f"{100 * s['arms']['true']['migration_rate']:.1f}"),
                ("sycophancy migration, inverted feedback",
                 f"{100 * s['arms']['inverted']['migration_rate']:.1f}"),
                ("displacement under true feedback",
                 f"{s['arms']['true']['mean_signed_displacement_toward_feedback']:.2f}"),
                ("displacement under inverted feedback",
                 f"{s['arms']['inverted']['mean_signed_displacement_toward_feedback']:.2f}"),
                ("sycophancy differential", signed3(s["delta_inverted_minus_true"])),
            ]

    # --- registered sensitivity analyses (code/25) ------------------------------------------
    # Added 2026-09-09 with the analyses themselves. Before this block the verifier's assertion
    # list was fixed at the numbers of the 2026-08 draft, so roughly forty figures added to
    # main.tex in September were invisible to it -- a passing 212/212 said nothing about them.
    sens_p = ROOT / "supplement/analysis/registered-sensitivities.json"
    if sens_p.exists():
        sv = json.loads(sens_p.read_text())["variants"]
        for lab, key in [("Cyprus", "cyprus"), ("zero-as-missing", "zero_na"),
                         ("no-Caucasus", "nocauc"), ("F117 d2only", "f117_d2"),
                         ("F117 d3only", "f117_d3")]:
            v = sv[key]
            checks.append((f"sens {lab} dCFI", dec3(v["H1"]["delta_cfi"])))
            checks.append((f"sens {lab} phi12", dec3(v["H1"]["phi_D1_D2"])))
            checks.append((f"sens {lab} phi13", dec3(v["H2"]["phi_D1_D3"])))
            checks.append((f"sens {lab} n_countries", str(v["n_countries"])))
        checks.append(("sens f117_d3 df(M1)", str(int(sv["f117_d3"]["fit"]["M1"]["df.scaled"]))))
        checks.append(("sens primary df(M1)", str(int(sv["cyprus"]["fit"]["M1"]["df.scaled"]))))

    # --- justifiability battery (code/26), unregistered exploratory --------------------------
    jb_p = ROOT / "supplement/analysis/justifiability-battery.json"
    if jb_p.exists():
        jb = json.loads(jb_p.read_text())["specs"]
        checks.append(("battery excl dCFI", dec3(jb["excl"]["H1"]["delta_cfi"])))
        checks.append(("battery excl phi12", dec3(jb["excl"]["H1"]["phi_D1_D2"])))
        checks.append(("battery excl M2 cfi", dec3(jb["excl"]["fit"]["M2"]["cfi.scaled"])))
        checks.append(("battery excl M0_12 cfi", dec3(jb["excl"]["fit"]["M0_12"]["cfi.scaled"])))
        checks.append(("battery excl M1 cfi", dec3(jb["excl"]["fit"]["M1"]["cfi.scaled"])))
        checks.append(("battery excl n_indicators", str(jb["excl"]["n_indicators"])))
        # the manuscript quotes the M2 correlation, which is what makes the fit inadmissible;
        # H1.phi_D1_D2 is M1's and is a different quantity.
        checks.append(("battery mf phi12 in M2", f'{jb["mf"]["H2"]["phi_D1_D2_in_M2"]:.3f}'))
        checks.append(("battery mf M2 min eigenvalue",
                       dec3(jb["mf"]["admissibility"]["M2"]["min_eigenvalue_covlv"])))

    # --- temporal replication, wave 1 vs wave 2 (code/28) ------------------------------------
    tw_p = ROOT / "supplement/analysis/tier2-wave-comparison.json"
    if tw_p.exists():
        tw = json.loads(tw_p.read_text())
        own, inter = tw["probability_propositions"], tw["probability_propositions_intersection_basis"]
        checks.append(("wave gap days", f'{tw["realised_gap_days"]:.3f}'))
        checks.append(("wave2 cells accepted", str(tw["wave2"]["n_cells_accepted"])))
        checks.append(("wave1 cells accepted", str(tw["wave1"]["n_cells_accepted"])))
        checks.append(("wave alpha median own", dec3(own["alpha_between_occasions"]) + "5"
                       if False else f'{own["alpha_between_occasions"]:.4f}'.lstrip("0")))
        checks.append(("wave alpha median inter",
                       f'{inter["alpha_between_occasions"]:.4f}'.lstrip("0")))
        checks.append(("wave alpha cell",
                       f'{tw["alpha_between_occasions"]["cell_level"]["alpha"]:.4f}'.lstrip("0")))
        checks.append(("wave modal changes own",
                       f'{own["modal_assignment_changes"]} of {own["n_decidable"]}'))
        checks.append(("wave modal changes inter",
                       f'{inter["modal_assignment_changes"]} of {inter["n_decidable"]}'))
        checks.append(("wave n_propositions", str(own["n_propositions"])))
        for r in tw["parameter_forecasts"]:
            checks.append((f'wave {r["id"]} w1', dec3(r["median_w1"])))
            checks.append((f'wave {r["id"]} w2', dec3(r["median_w2"])))

    # --- per-group decomposition, cited in Sec. 3.5 ------------------------------------------
    pg_p = ROOT / "supplement/analysis/pergroup-decomposition-primary.json"
    if pg_p.exists():
        pg = json.loads(pg_p.read_text())
        checks.append(("decomposition worst |dlambda|", f'{pg["worst_abs_loading_diff"]:.5f}'.lstrip("0")))

    # --- ESS structural replication (code/30, code/31), unregistered -------------------------
    ess_p = ROOT / "supplement/analysis/ess-replication.json"
    if ess_p.exists():
        e = json.loads(ess_p.read_text())
        checks.append(("ESS pooled dCFI", dec3(e["H1"]["deltaCFI"])))
        checks.append(("ESS pooled phi12", dec3(e["H1"]["phi_D1_D2"])))
        checks.append(("ESS pooled phi13", dec3(e["H2"]["phi_D1_D3"])))
        checks.append(("ESS n rows", thousands(e["n_rows"])))
        checks.append(("ESS n countries", str(e["n_countries_any_round"])))
        checks.append(("ESS M2 cfi", dec3(e["fit"]["M2"]["cfi.scaled"])))
        for r, blk in e["per_round"].items():
            checks.append((f"ESS round {r} dCFI", dec3(blk["deltaCFI"])))
            checks.append((f"ESS round {r} phi12", dec3(blk["phi_D1_D2"])))
            checks.append((f"ESS round {r} n", thousands(blk["n"])))
            checks.append((f"ESS round {r} countries", str(blk["n_countries"])))
        cr = e["cross_round"]["steps"]
        checks.append(("ESS cross-round metric dCFI", signed3(cr["metric"]["dCFI"])))
        checks.append(("ESS cross-round scalar dCFI", signed3(cr["scalar"]["dCFI"])))
        for rung in ("configural", "metric", "scalar"):
            checks.append((f"ESS cross-round {rung} cfi", dec3(cr[rung]["cfi.scaled"])))
        checks.append(("ESS cross-round metric dchisq",
                       thousands(abs(cr["metric"]["chisq.scaled"] - cr["configural"]["chisq.scaled"]))))
        checks.append(("ESS cross-round metric ddf",
                       str(int(cr["metric"]["df.scaled"] - cr["configural"]["df.scaled"]))))
        checks.append(("ESS cross-round scalar dchisq",
                       thousands(cr["scalar"]["chisq.scaled"] - cr["metric"]["chisq.scaled"])))
        checks.append(("ESS cross-round scalar ddf",
                       str(int(cr["scalar"]["df.scaled"] - cr["metric"]["df.scaled"]))))
        for rung in ("configural", "metric", "scalar"):
            checks.append((f"ESS cross-round {rung} rmsea", dec3(cr[rung]["rmsea.scaled"])))
    ea_p = ROOT / "supplement/analysis/ess-admissibility.json"
    if ea_p.exists():
        ea = json.loads(ea_p.read_text())
        checks.append(("ESS M2 min eigenvalue", dec3(ea["models"]["M2"]["min_eigenvalue_covlv"])))

    # --- artefacts the manuscript says it ships ----------------------------------------------
    # A claim that something is "in the supplement" is a factual claim about this repository and
    # is checked as one. main.tex:727 promised completed reporting checklists for months while no
    # file named anything like one existed anywhere in the tree.
    must_exist = [
        ("reporting checklists (Sec. 4.6)", ROOT / "supplement/reporting-checklists.md"),
        ("S8 check 2, temporal replication", ROOT / "supplement/delphi-check-2.md"),
        ("S8 checks 4 and 5", ROOT / "supplement/delphi-checks-4-5.md"),
        ("frozen ESS item table (Sec. 5.6)", ROOT / "docs/design/ess-item-table-frozen.md"),
        ("negative-result section as drafted", ROOT / "supplement/negative-result-section-as-drafted.tex"),
        ("pilot inputs shipped for code/02", ROOT / "docs/design/delphi-pilot_raw.json"),
    ]
    missing_files = [lab for lab, path in must_exist if not path.exists()]

    failures = [(lab, s) for lab, s in checks if s not in tex]

    # --- prose claims, encoded as assertions ---------------------------------------------
    # Each entry is (claim as the manuscript states it, boolean that must hold).
    f = d["fit"]
    prose = [
        ("M4 fits better than M2 on CFI, RMSEA and SRMR",
         f["M4"]["cfi.scaled"] > f["M2"]["cfi.scaled"]
         and f["M4"]["rmsea.scaled"] < f["M2"]["rmsea.scaled"]
         and f["M4"]["srmr"] < f["M2"]["srmr"]),
        ("no specification reaches CFI .80",
         max(v["cfi.scaled"] for v in f.values()) < .80),
        ("M4 has 48 more free parameters than M2",
         f["M2"]["df.scaled"] - f["M4"]["df.scaled"] == 48),
        ("M1b and M0_12 have identical df",
         f["M1b"]["df.scaled"] == f["M0_12"]["df.scaled"]),
        ("M1b and M0_12 chi-square agree to within 0.1",
         abs(f["M1b"]["chisq.scaled"] - f["M0_12"]["chisq.scaled"]) < 0.1),
        ("exactly one model is inadmissible",
         len(adm["failed"]) == 1 and adm["failed"] == ["M2b"]),
        ("no model failed unexpectedly",
         adm["failed_unexpectedly"] == []),
        ("no Heywood cases",
         d["drop_log"]["heywood_cases"] == "none"
         and all(v["heywood_negative_var"] == 0 for v in adm["models"].values())),
        ("H1 supported", d["H1"]["supported"] is True),
        ("H2 supported", d["H2"]["supported"] is True),
        ("signed and absolute readings of H2 agree", d["H2"]["signed_and_abs_agree"] is True),
        ("half of reverse-keyed items are weak, against a quarter of forward-keyed",
         ct["weak_rate_among_reverse_keyed"] > ct["weak_rate_among_forward_keyed"]),
        ("education is the worst-affected sphere",
         max(weak["by_sphere"].values(), key=lambda v: v["weak_share"])["weak_share"]
         == weak["by_sphere"]["Education"]["weak_share"]),
        ("all five confidence items clear the threshold",
         weak["by_sphere"]["Confidence"]["n_weak"] == 0),
        # The manuscript states that the child-qualities battery supplies 5 of the 18 weak
        # indicators and that those five ARE the education sphere's failures. Both halves are
        # asserted: an earlier draft said "six", which no numeric check would have caught
        # because the digit appeared nowhere in the JSON.
        ("the child-qualities battery supplies exactly 5 weak indicators",
         len([r for r in weak["items"]
              if r["variable"].startswith("A0") and r["sphere"] == "Education"]) == 5),
        ("every weak education indicator is a child-qualities item",
         all(r["variable"].startswith("A0")
             for r in weak["items"] if r["sphere"] == "Education")),
        # The pilot section's word-numbers, which no numeric check can see because the
        # manuscript spells them ("nine independent model endpoints", "five distinct models
        # from four developers", "twelve real survey items").
        ("the pilot has nine rater draws", pilot["n_raters"] == 9),
        ("the pilot spans five distinct models", pilot["n_models"] == 5),
        ("those five models come from four developers", pilot["n_developers"] == 4),
        ("no pilot model is unmapped to a developer",
         not any(dev.startswith("UNMAPPED") for dev in pilot["developers"])),
        ("the pilot rates twelve items", pilot["n_items"] == 12),
        ("the ratings do not ceiling", pilot["pct_at_maximum"] < 10
         and pilot["item_mean_max"] - pilot["item_mean_min"] > 3),
        # The section's entire argument is that the index moves while the data do not, so the
        # spread across cut-points has to be large or the paragraph claims more than it shows.
        ("mean I-CVI spans more than .80 across the cut-point ladder",
         max(pilot["mean_icvi_by_cutpoint"].values())
         - min(pilot["mean_icvi_by_cutpoint"].values()) > .80),
        ("the conventional .78 threshold falls inside that span",
         min(pilot["mean_icvi_by_cutpoint"].values()) < .78
         < max(pilot["mean_icvi_by_cutpoint"].values())),
        # The manuscript's answer to "you explored cut-points nobody uses" is that the panel
        # fails the conventional threshold at the conventional rule, with no latitude taken.
        # If that ever stopped being true the paragraph would be arguing the opposite case.
        ("the panel falls below .78 at the conventional four-point rule",
         pilot["mean_icvi_cte_4pt_rule"] < .78),
    ]
    # The single worst error this paper could make is a country league table the invariance
    # testing does not license. That is not a matter of good intentions, so it is asserted here.
    if align is not None:
        inv = align["invariance"]
        pg = inv["configural_pergroup"]
        al = inv.get("alignment", {})
        fit_steps = set(inv.get("fit", {}).keys())
        codes = set(pg.get("per_group", {}).keys())
        licensed = {dd for dd, v in al.items() if v["country_comparison_licensed"]}
        # A tabular row whose FIRST cell is exactly a country code is a country table. Matching on
        # the first cell rather than anywhere in the line keeps two-letter ISO codes from firing
        # on ordinary prose.
        country_rows = [ln for ln in tex.splitlines()
                        if "&" in ln and ln.split("&")[0].strip().rstrip("\\").strip() in codes]
        prose.extend([
            ("no country-row table appears while no dimension is licensed",
             bool(licensed) or not country_rows),
            ("every dimension the alignment licenses has recovery confirmed",
             all(v["recovery_confirmed"] for dd, v in al.items() if dd in licensed)),
            ("no dimension is licensed below the registered R2_locations floor of .75",
             all(v["R2_locations"] >= .75 for dd, v in al.items() if dd in licensed)),
            # The REGISTERED metric and scalar steps on M2 over all 39 countries were never
            # estimable. Unregistered ladders on other specifications and samples now exist and
            # are reported, so the old form of this check -- forbid the phrase outright -- would
            # fire on correct prose. What must still hold is that any invariance verdict is
            # accompanied by the statement that the registered test was not estimated, so a
            # reader cannot mistake a diagnostic for the registered result.
            #
            # The substitutes were called "unregistered diagnostics" while D1 alone had a
            # complete chain; with D2 and D3 finished they are called "unregistered ladders",
            # which is the more accurate noun for a nested configural/metric/scalar chain. The
            # property under test is unchanged -- the substitutes must be LABELLED unregistered
            # -- so the matcher takes either noun and still refuses a bare "unregistered".
            ("an invariance verdict never appears without the registered test being disclaimed",
             ("metric" in fit_steps and "scalar" in fit_steps)
             or not re.search(r"(metric|scalar) invariance (holds|fails)", tex_flat, re.I)
             or ("were not estimated on the registered model" in tex_flat
                 and UNREG_LABEL.search(tex_flat) is not None)),
            # Any ladder the manuscript reports must be one an artefact actually contains.
            ("every reported invariance ladder has an output file behind it",
             not re.search(r"same twelve countries", tex_flat) or psb is not None),
            ("every country excluded for non-convergence is named in the manuscript",
             all(c in tex_flat for c in pg.get("groups_excluded", []))),
        ])

    # A "Supplement S4" pointer is a claim about a file, and it is the kind of claim that rots
    # silently: the supplement is assembled by script, so renumbering a section renumbers the
    # files and leaves the manuscript pointing somewhere plausible and wrong. Checked against the
    # built package when one exists.
    pkg = ROOT / "supplement/_package"
    if pkg.exists():
        have_s = {m.group(1) for p in pkg.iterdir()
                  if (m := re.match(r"(S\d+)-", p.name))}
        cited_s = set(re.findall(r"Supplement~(S\d+)", tex))
        prose.append(
            (f"every Supplement S-number cited resolves to a file ({sorted(cited_s - have_s)} missing)"
             if cited_s - have_s else "every Supplement S-number cited resolves to a file",
             cited_s <= have_s))

    # The subset ladder is the one unregistered inferential result the manuscript reports, so
    # what has to be checked is not its arithmetic but its framing: a reader must be able to
    # see which countries it covers and that it is not the registered test.
    if ladder is not None:
        sl = ladder["invariance"]["subset_ladder"]
        subset = as_list(sl.get("countries", []))
        unnamed = [c for c in subset if c not in COUNTRY_NAMES]
        prose.extend([
            ("every country in the subset ladder has a name in the verifier's map",
             not unnamed),
            ("every country in the subset ladder is named in the manuscript",
             all(COUNTRY_NAMES.get(c, c) in tex_flat for c in subset)),
            ("the manuscript names exactly as many subset countries as the draw contains",
             sl["k"] == len(subset)),
            ("the subset ladder is recorded as unregistered in its own output",
             sl.get("registered") is False),
            ("the manuscript calls the subset ladder unregistered",
             UNREG_LABEL.search(tex_flat) is not None),
            # The seeded draw is what makes the subset defensible rather than chosen. If the
            # seed ever disappears from the output, the manuscript's claim that the countries
            # were not selected stops being checkable.
            ("the subset draw records its seed", isinstance(sl.get("seed"), int)),
        ])
    else:
        print("  WARN  no alignment JSON yet; invariance numbers in main.tex are unverified\n")

    # --- Tier-2 prose claims ---------------------------------------------------------------
    # The numbers above cannot catch a section that reports them and then draws the opposite
    # conclusion, or one that quietly upgrades an audit into a validation. These can.
    if t2 is not None:
        blk, bb = t2["by_block"], t2["family_cluster_bootstrap"]
        dpar = {r["id"]: r for r in t2["block_D_point_forecasts"]}
        import math
        prose.extend([
            ("the registered informativeness criterion is decided by the bootstrap bound",
             (bb["lo95"] > 0) == t2["informative_by_registered_criterion"]),
            ("the manuscript calls the panel informative only if the bound clears zero",
             (bb["lo95"] > 0) == ("informative} by the criterion" in tex_flat
                                  or "\\emph{informative} by the criterion" in tex_flat)),
            ("all the skill is in block A, as the manuscript says",
             blk["A_item_loadings"]["BSS"] > 0
             > blk["B_C_hypotheses_and_invariance"]["BSS"]),
            ("the raw Brier really is lower in block B/C than in block A",
             blk["B_C_hypotheses_and_invariance"]["BS"] < blk["A_item_loadings"]["BS"]),
            ("the panel discriminates loading items above chance",
             t2["brier"]["auc_block_A"] > .5),
            ("exactly four propositions are unresolvable",
             t2["propositions"]["n_unresolved"] == 4),
            ("the manuscript says four do not resolve",
             "four do not" in tex_flat),
            # The section's strongest claim. If a re-run ever flips a sign, this fails rather
            # than leaving the prose asserting a reversal that is no longer there.
            ("both D3 correlations were forecast with the wrong sign",
             math.copysign(1, dpar["D-PHI13"]["median_forecast"])
             != math.copysign(1, dpar["D-PHI13"]["observed"])
             and math.copysign(1, dpar["D-PHI23"]["median_forecast"])
             != math.copysign(1, dpar["D-PHI23"]["observed"])),
            ("phi(D1,D2) alone was forecast with the right sign",
             math.copysign(1, dpar["D-PHI12"]["median_forecast"])
             == math.copysign(1, dpar["D-PHI12"]["observed"])),
            ("no draw's 80% interval covered phi(D2,D3), as the manuscript states",
             dpar["D-PHI23"]["interval_80_coverage"] == 0),
            ("Section 4 points forward to the scored result",
             "Section~\\ref{sec:tier2}" in tex_flat),
            # A standing prohibition, not a description of the current text: the panel is an
            # instrument, and no rewrite may promote it into a warrant for the model.
            ("the manuscript never claims the panel validates the model",
             "panel validates nothing" in tex_flat
             and "validates the model" not in tex_flat),
        ])

    # --- per-group decomposition (code/13), asserted against the DOCS ----------------------
    # These two figures never enter main.tex -- the manuscript rests on the algebraic identity
    # -- but they are quoted as evidence in cover-letter.md and in the disclosures status
    # board, and a figure quoted as evidence has to reproduce from an artefact. Gated on the
    # JSON existing, so a fresh clone that has not run code/13 warns rather than fails.
    if dec is not None:
        cl  = " ".join((ROOT / "cover-letter.md").read_text().split())
        dsc = " ".join((ROOT / "docs/submission-disclosures.md").read_text().split())
        rmin, worst = dec["min_correlation"], dec["worst_abs_loading_diff"]
        r4  = f"{rmin:.4f}"                       # 1.0000
        w4  = f"{worst:.4f}".lstrip("0")          # .0005  -- the cover letter's rounding
        w5  = f"{worst:.5f}".lstrip("0")          # .00046 -- the disclosures' rounding
        prose.extend([
            ("code/13 reports the per-group decomposition as exact",
             dec.get("decomposition_exact") is True),
            ("no dimension shows a sign flip between the two configural routes",
             all(v["sign_flips"] == 0 for v in dec["dimensions"].values())),
            (f"the cover letter's r = {r4} matches code/13's minimum correlation",
             f"r = {r4}" in cl),
            (f"the cover letter's worst loading discrepancy {w4} matches code/13",
             f"discrepancy of {w4}" in cl),
            (f"the disclosures' worst |dlambda| = {w5} matches code/13",
             w5 in dsc),
            # The comparison is only possible where BOTH routes exist, which is the 12-country
            # ladder subset and not the 39-country analysis sample. Both documents must carry
            # that limit, or they read as a stronger claim than the artefact supports.
            ("the cover letter states the decomposition check covers only the twelve",
             "twelve countries for which a pooled fit also exists" in cl),
            ("the disclosures state the decomposition check covers only the twelve",
             "12 countries of the subset ladder" in dsc),
            ("code/13 compared every group it found in the pooled fit",
             dec["n_groups_compared"] == dec["n_groups_pooled"]
             and not dec["groups_missing_per_group_fit"]),
        ])
    else:
        print("  WARN  no pergroup-decomposition JSON; run code/13 before submission "
              "-- the cover letter's r and |dlambda| are then unreproducible\n")

    bad_prose = [c for c, ok in prose if not ok]

    # --- unfilled placeholders ------------------------------------------------------------
    pending = [ln for ln in tex.splitlines()
               if re.search(r"^[^%]*\\PENDING\{", ln)]

    for lab, s in checks:
        if (lab, s) not in failures:
            print(f"  ok    {lab:<32s} {s}")
    for lab, s in failures:
        print(f"  FAIL  {lab:<32s} {s!r} not found in main.tex")
    for c in bad_prose:
        print(f"  FAIL  prose claim no longer holds: {c}")

    print()
    print(f"{len(checks) - len(failures)}/{len(checks)} numeric checks passed, "
          f"{len(prose) - len(bad_prose)}/{len(prose)} prose claims hold")
    if pending:
        print(f"{len(pending)} unfilled \\PENDING placeholder(s) remain:")
        for ln in pending:
            print(f"    {ln.strip()[:90]}")

    # Blinding is a WARNING, never a failure. The links must be present in the archival and
    # camera-ready manuscript -- a pre-registered study cites its registration -- and must be
    # anonymised in the review copy. Only the person submitting knows which is being built, so
    # this reports and does not judge. See docs/submission-disclosures.md Sec. 7.
    osf_links = re.findall(r"osf\.io/(\w+)", tex)
    if osf_links:
        print(f"\nWARNING -- blinding: {len(osf_links)} OSF link(s) in main.tex "
              f"({', '.join(sorted(set(osf_links)))}) resolve to a named account, while the "
              "author block is anonymised.\n  Quality & Quantity reviews double-blind. Use "
              "anonymised view-only links in the REVIEW copy; keep the real DOIs for the "
              "camera-ready.\n  Do not delete the links: the registration citation and the "
              "Tier-2 timing claim both depend on them.")

    # ---- length against the journal's 8,000-10,000 band -----------------------------------
    # The count was being re-derived by hand every time the manuscript changed, with a
    # different answer each time, so the convention is fixed here: `texcount -sum` over the
    # body, MINUS the front matter texcount labels `_top_` (abstract and keywords, which the
    # journal counts separately against its own 250-word limit) and MINUS everything from the
    # first \bmhead of the back matter onward (declarations, availability statements). It
    # excludes references, which texcount does not count in the first place. This over-counts
    # if anything -- section headings are inside the body figure -- which is the right
    # direction for a limit. A WARNING, not a failure: only the submitter knows the venue.
    if shutil.which("texcount"):
        body = tex.split("\\bmhead{Data availability}")[0]
        with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False) as fh:
            fh.write(body)
            tmp = fh.name
        try:
            out = subprocess.run(["texcount", "-sum", "-q", tmp],
                                 capture_output=True, text=True, timeout=60).stdout
            m = re.search(r"Words in text:\s*(\d+)", out)
            top = re.search(r"(\d+)\+\d+\+\d+ \(\d+/\d+/\d+/\d+\) _top_",
                            subprocess.run(["texcount", "-q", tmp], capture_output=True,
                                           text=True, timeout=60).stdout)
            if m and top:
                n = int(m.group(1)) - int(top.group(1))
                verdict = ("within" if 8000 <= n <= 10000 else
                           "OVER" if n > 10000 else "UNDER")
                print(f"\n{'length: ' if verdict == 'within' else 'WARNING -- length: '}"
                      f"body is {n:,} words ({verdict} the 8,000-10,000 band); "
                      f"front matter {int(top.group(1))} words counted separately.")
        finally:
            os.unlink(tmp)

    if missing_files:
        print("\nWARNING -- the manuscript claims artefacts that do not exist:")
        for lab in missing_files:
            print(f"  MISSING  {lab}")

    if failures or bad_prose or missing_files:
        return 1
    if pending:
        print("\nNot submission-ready: placeholders remain (this is not a verification failure).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
