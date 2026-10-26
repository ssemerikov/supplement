# OSF pre-registration — Popperian Individualism Index (PII)

> ## FILED 2026-08-10
>
> **https://osf.io/ezjh2/ · DOI `10.17605/OSF.IO/EZJH2` · registered 2026-08-10 07:45:39 UTC**
> Schema: OSF Preregistration. Public, not withdrawn. `revision_state: approved`, so versioned
> updates are available.
>
> The frozen item table is attached to the registration with SHA-256
> `2c9e0b7f215c925c2e9fc38aa164e53edcb3c390df251869b694e48aed144de5`, **verified 2026-08-10 to match
> `docs/design/item-table-v2-joint-names.md` byte-for-byte.** Any later change to that file is
> detectable and must be disclosed.
>
> **The analytic gate is cleared: the confirmatory analysis may now be run** — subject to the Tier-2
> timing requirement in §7.1, which is unchanged and binding.
>
> **Version 2 filed 2026-08-10 07:56:12 UTC — the foreknowledge correction is closed.** The
> selection now reads "Authors have observed the data, but have not performed the proposed
> analyses", and the previously empty explanation field carries the full disclosure. Exactly two
> fields changed; nothing substantive was touched. See §12.

**Title.** Two axes and a third dimension: measuring Popperian individualism across 39 European
countries, with a synthetic-panel validation of the measurement model

**Type.** Pre-registration of a secondary-data analysis with a pre-specified measurement model.
Template: OSF Preregistration (generic), extended for measurement-invariance and LLM-panel reporting
per ACCORD/CREDES and TRIPOD-LLM (Gallifant et al. 2025).

**Authors.** *To be completed by the author team. Order, affiliations, ORCIDs, corresponding author
and CRediT roles are not set by the agent and must not be invented.*

---

## 1. Disclosure of prior data access — read this first

**The data have been obtained and inspected. No analyses have been run.** This registration is
therefore not "blind", and claiming otherwise would be contradicted by the repository's own
timestamps. Precisely what has and has not happened:

**Inspected (2026-08-10), and used to write this document:** variable names, variable labels,
response scales and category labels, missing-value codes and their rates, per-country validity, the
country list, the EVS5 matrix-design structure, and sample sizes. This inspection was necessary — a
pre-registration that names variables must establish that those variables exist. It is reproduced by
`code/01_audit_joint_core.py` and documented in `docs/design/data-audit-2026-08-10.md` and
`docs/design/item-table-v2-joint-names.md`.

**Not done, and not permitted until this registration is filed:** any correlation, covariance,
factor analysis, reliability coefficient, group comparison, regression, or country ranking on the
real data. No hypothesis-relevant statistic of any kind has been computed.

**Prior work on simulated data.** The full analysis chain (configural → metric → scalar →
alignment) was executed end to end on *simulated* data with injected non-invariance, to verify the
software works. See `docs/environment-verification.md`. No real data were involved.

---

## 2. Study information

### 2.1 Background

Popper's *The Open Society and Its Enemies* ch. 6 §V (pp. 95–98, one-volume Princeton University Press edition, 2013)
argues that individualism↔collectivism and altruism↔egoism are **two independent axes**, giving four
cells rather than a single continuum. Separately, ch. 7 note 23 (pp. 584–585) rules out identifying
individualism with **anti-institutional personalism**, whose negative pole Popper locates in the
leader-principle. The construct argument is made in full in Paper A (*Answerability Individualism*,
Synthese) and is **cited, not re-argued**, here.

The measurement literature is not silent on two axes — Schwartz (1992, 2006), Schulz et al. (2019),
Enke et al. (2023) and GLOBE all place a second dimension beside individualism, and Akaliyski et al.
(2026) supersede Hofstede's IDV on validity grounds. The gap this study addresses is narrower and
real: **the two axes have never been crossed inside a single country-level measurement model with
cell membership as the quantity of interest**, and **the institutional-respect dimension has no
counterpart anywhere in the individualism-measurement literature**.

### 2.2 Hypotheses

| | Hypothesis | Status |
|---|---|---|
| **H2** | D3 (institutional respect ↔ anti-institutional personalism) is not reducible to D1 | **Primary** |
| **H1** | D1 and D2 are empirically separable: a two-factor model beats a one-factor model | Confirmatory, tested twice in independent samples |
| **H3b** | IDV and Welzel's index are approximately silent on D2 | Confirmatory, clean |
| **H3a** | IDV and Welzel load principally on D1 | **Partly constructional. Reported for completeness, NOT as evidence.** |
| **H4** | *Jellyby prediction.* Breadth of anonymous other-regard dissociates from depth of concrete other-regard | Exploratory-confirmatory; see §6.5 |

**Directional predictions.** H2: φ(D1,D3) ≤ .70 and a model constraining D3 = D1 is rejected. H1: see
the decision rule in §6.2. H3b: |r(IDV, D2)| and |r(Welzel, D2)| both within ±0.20. H3a: r(IDV, D1)
and r(Welzel, D1) substantially exceed their D2 counterparts, with the Welzel comparison discounted
for circularity.

---

## 3. Design

Secondary analysis of existing cross-national survey microdata. No new data collection from human
participants. No experimental manipulation of human participants. The synthetic-panel component
(§7) involves large language models, not people.

**Ethics.** No human participants; see `docs/ethics.md`. No approval required.

---

## 4. Data

### 4.1 Primary sample

**Joint EVS/WVS 2017–2022**, GESIS ZA7505 **version 5.0.0** (2024-06-24), `doi:10.4232/1.14320`.
SHA-256 `16407d91bcb9dff1ff246ee5a515a2089bd2d1ca8525e69a824b6212cc4743ce`. Full provenance in
`docs/data-provenance.md`.

**Countries (pre-registered, fixed now).** The 40 European countries in the file are AD AL AM AT AZ
BA BG BY CH CY CZ DE DK EE ES FI FR GB GE GR HR HU IS IT LT LV ME MK NIR NL NO PL PT RO RS RU SE SI
SK UA (78,396 respondents). **Cyprus is excluded** (Decision D1 below), giving **39 countries**.
Northern Ireland is retained separately from Great Britain. Armenia, Azerbaijan and Georgia are
retained on a generous definition of Europe; a sensitivity analysis excluding all three is reported.

### 4.2 Replication sample

**ESS rounds 9 (ed. 3.3), 10 (ed. 3.3) and 11 (ed. 4.2)** — 29, 22 and 30 countries. ESS and EVS/WVS
have disjoint respondents, so no single individual-level model spans them. The ESS analysis is an
**independent replication of model structure, not of parameter values**, for the politics and
morality spheres only.

**ESS11's PVQ items carry an `a` suffix** (`ipcrtiva`, `impricha`, …), marking a revised
administration. Rounds 9–10 and round 11 are therefore **not assumed comparable**: cross-round
invariance is tested, and if metric invariance fails, round 11 is reported separately rather than
pooled.

### 4.3 Country-level covariates

V-Dem v16; QoG Standard Jan26; Hofstede six-dimension scores; Welzel emancipative values. Used only
for H3 and for construct validity, never as model indicators.

---

## 5. Three decisions taken before any analysis

These are recorded here because each would otherwise be a researcher degree of freedom exploitable
after seeing results. Full evidence in `docs/design/item-table-v2-joint-names.md` §0 and §4.

### D1 — Cyprus is excluded from the primary model

Cyprus fails on two unrelated grounds. On the child-qualities battery its missingness is `−1` "don't
know" at 32–40 % (322/1,000 on `A029`, 403/1,000 on `A042`) against a European average of **0.8 %**
on the same items — on a binary mentioned/not-mentioned card sort this indicates non-mention recorded
as don't-know, so the values are not missing at random and must not be imputed. Separately, `E116`
and `E228` each have **exactly 500 of 1,000 cases** coded `−5`, a split ballot filed as "Other".

**Decision: exclude CY from the primary model. Report a sensitivity analysis including it.** N = 39.

### D2 — The `0` category in the democracy battery is recoded to `1`

`E224`–`E233B` are scored 0–10, but `0` is **"It is against democracy (spontaneous)"** — a
volunteered response, not a scale point below `1` ("not an essential characteristic").

**Decision: recode `0 → 1`**, treating the volunteered rejection as the lowest endorsement, because
substantively "against democracy" is a stronger form of "not essential" rather than a different kind
of answer. **Report a sensitivity analysis treating `0` as missing.** If the two disagree on any
hypothesis test, both are reported in the manuscript body, not the supplement.

### D3 — A method factor for the "essential characteristics of democracy" battery

Nine items (`E224`–`E233B`) share one stem and one 0–10 response format while supplying indicators to
all three dimensions. A three-factor solution built substantially on them risks recovering
**response-format structure rather than construct structure**.

**Decision: include a battery-specific method factor**, orthogonal to the three substantive factors,
loading on all democracy-battery items — consistent with the CT-CU specification already adopted.
**Additionally report a sensitivity model with the battery excluded entirely.** The substantive
conclusion must survive both, and if it does not, that is reported as the finding.

---

## 6. Measurement model and analysis plan

### 6.1 Frozen item table

**The item table is `docs/design/item-table-v2-joint-names.md` and is frozen as of the filing date of
this registration.** It gives, for every item: dimension, sphere, integrated EVS/WVS variable name,
the WVS7 Q-number it was translated from, keying (forward/reverse), and European validity. Items are
named in integrated EVS/WVS notation; WVS7 `Q`-numbers do not exist in the joint file.

> **AMBIGUITY IN THE FROZEN TABLE, found 2026-08-10 before any model was fitted.** `F117`
> ("justifiable: accepting a bribe") appears **twice**: as `D2-M4` in D2's justifiability block
> beside `F114A`/`F115`/`F116`, and as `D3-M1` in D3's morality block beside `E290`. The table
> annotates everything else it does deliberately (`[NEW]`, `marginal`, `confounded`, `†`) and
> annotates this not at all, so it is most likely an oversight rather than an intended
> cross-loading — though the double assignment is substantively defensible, since accepting a bribe
> is both defection from a collective good for private gain (D2) and a corrosion of impersonal
> institutions (D3).
>
> **The table is hash-locked and is not being edited.** Resolving the ambiguity by rewriting it
> would break the registered hash for a reason indistinguishable, from outside, from fitting
> convenience. The specification is therefore taken **literally**: the primary model lets `F117`
> load on both D2 and D3, which is what the registered table says. Two sensitivity models assign it
> to **D2 only** and to **D3 only**, and all three are reported. If they disagree on H1 or H2, the
> disagreement goes in the manuscript body, not the supplement.
>
> This affects neither primary decision rule directly — H1 tests φ(D1,D2) and H2 tests φ(D1,D3),
> while the shared indicator sits between D2 and D3 — but it does bear on model fit and on
> φ(D2,D3), and is disclosed for that reason.

**Items may be dropped only for pre-specified psychometric reasons** — standardised loading < .30 in
the configural model, or a Heywood case — **never to improve fit or rescue a hypothesis.** Every drop
is logged with its reason in the supplement. **No item may be added after filing.**

### 6.2 Model specification and the H1 decision rule

Estimator: **WLSMV with ordinal indicators.** The pool spans binary, 3-, 4-, 5- and 10-category
items; ML is not appropriate. Missing data: **pairwise deletion under WLSMV**, with planned `−4`
missingness (DK 49.6 %, NL 37.8 %, FI 11.9 %, IS 3.1 % on the democracy battery) treated as MCAR by
design, which it is.

Models compared:

- **M0** — one general factor (the single-axis assumption the paper exists to test)
- **M1** — two correlated factors, D1 and D2
- **M1b** — as M1 with φ(D1,D2) fixed to 1
- **M2** — three correlated factors, D1, D2, D3 (**the target model**)
- **M2b** — as M2 with φ(D1,D3) fixed to 1 (the H2 test)
- **M3** — three traits × sphere as method (MTMM, CT-CU)
- **M4** — bifactor, **as a named competitor only**; it presupposes a general factor and is not the primary model

**H1 is supported iff all three hold:** (a) M1 beats M0 by ΔCFI ≥ +.010; (b) M1b is rejected against
M1 at α = .01; (c) φ(D1,D2) ≤ .85 in the primary sample.

**If any of the three fails, the paper reports that Popper's distinction does not separate
empirically at population level.** It then discusses whether that is a fact about populations or
about the instruments, and **does not respecify to rescue the hypothesis.** A split decision across
the primary and replication samples is reported as a split decision, not resolved in favour of the
positive one.

**H2 is supported iff** M2b is rejected against M2 at α = .01 **and** φ(D1,D3) ≤ .70.

### 6.3 Measurement invariance — and what may be reported

Chain: configural → metric → scalar, then **`sirt::invariance.alignment`** if scalar fails, which on
~39 countries it very likely will.

- **`sirt` aligns one factor at a time.** Alignment is run **per dimension**, in those words.
- **No country mean, ranking or league table is reported unless `invariance_alignment_simulate`
  confirms parameter recovery for that dimension.** If it does not, the paper reports the invariance
  failure and presents no country comparison for that dimension. This is a hard stop.
- Partial invariance cap: at most **20 %** of loadings or intercepts freed. Beyond that the model is
  declared non-invariant rather than patched.
- Fit thresholds: CFI ≥ .95, RMSEA ≤ .06, SRMR ≤ .08 for adequate fit; invariance steps judged on
  ΔCFI ≤ .010 and ΔRMSEA ≤ .015.

**The paper's country-level output is a profile across dimensions, not a scalar ranking**, and even
the profile is reported only for dimensions that clear the alignment check.

### 6.4 H3 and the circularity correction

Steiger's Z on dependent correlations sharing one variable. "Approximately silent" (H3b) is tested by
**TOST with a pre-registered ±0.20 equivalence bound**; without a bound the claim is untestable at
N ≈ 39.

**H3a is reported twice** — once with full D1, once with a **Welzel-free D1 subset** (`E229`,
`E233B` R, `H009`, `H010`, `H011`, none of which enters any Welzel sub-index) — and the gap between
them is reported as the magnitude of the constructional overlap. `E233` is excluded from the subset
because it is a Welzel EQUALITY component. IDV is unaffected by the circularity and is the more
informative comparison.

### 6.5 H4 — the Jellyby prediction

Popper's Mrs Jellyby is genuinely altruistic yet directs concern at "anonymous groups rather than
concrete individuals". Three independent operationalisations, all fielded in all 39 countries:

| Probe | Concrete pole | Anonymous pole |
|---|---|---|
| Whom you trust | `D001_B` family, `G007_33_B` people known personally | `G007_34_B` strangers, `G007_36_B` other nationality |
| Whom you belong to | `G255` town, `G256` region | `G062` continent, `G063` world |
| Whom you act for | `D026_05` duty to an ill parent | `A080_01` charitable-organisation membership |

**Prediction:** the concrete and anonymous poles are separable rather than collinear, and their
difference score is not reducible to D1 or D2. Tested as a two-factor versus one-factor comparison
within each probe, then as incremental validity over D1 and D2. **A null here does not threaten
H1–H3**; it is reported as a limit on how far Popper's illustration operationalises.

### 6.6 Spheres

The grid is **3 dimensions × 2 primary spheres** (politics, everyday morality), with education
entering on D1 and D2 only. Reasons, all established before analysis:

- **D3 × education is empty.** Its only verified item was confidence in universities (`Q75`), which
  is not in the joint core.
- **The science sphere is empty in the primary sample** — the entire `Q158`–`Q163` block is WVS-only
  and absent from the EVS ∩ WVS core. It survives only as D3 in **ESS10** (`trstsci`, 22 countries),
  reported separately and labelled as such, or dropped.
- Retention rule: a sphere enters cross-national comparison only if **≥ 20 countries** carry its
  items.

**Per-sphere reliability is reported honestly and a sphere is dropped rather than padded.**

---

## 7. The synthetic Delphi panel

Full protocol in `docs/design/delphi-design.md`; only the pre-registered commitments are here.

**The panel is an instrument with a documented error model, not a substitute for expert
consultation.** This is stated in the manuscript in both §4 and §8 and is not softened.

### 7.1 Two-tier criterion

- **Tier 1 — published item→construct key.** Scored against the original authors' theoretical
  assignments. **Contaminated by construction**; canary items measure the contamination rather than
  assume it away. Reported, but not load-bearing.
- **Tier 2 — a forecast of this paper's own CFA**, scored by **Brier skill**. Contamination-immune,
  because the analysis has never been run and exists in no training corpus. **This is the
  evidentially load-bearing tier.**

**Timing requirement, binding:** the Tier-2 forecast must be elicited and its predictions
time-stamped and registered **before the CFA is run**. If the CFA is run first, Tier 2 is void and
must be reported as void. If the forecast is filed as an addendum rather than in this document, the
addendum's OSF timestamp is the evidence.

#### Tier-2 wave 1 — elicited and deposited

**Elicited 2026-08-10 08:38:17 UTC. No CFA had been run at that time.** The deposit recorded below
was completed at 09:11:17 UTC, still before any confirmatory analysis.

Two artefacts, both deposited, neither superseding the other:

| | Primary run | Top-up run |
|---|---|---|
| File | `tier2-forecast-wave1-20260810T083817Z.json` | `tier2-forecast-wave1-topup-20260810T085136Z.json` |
| Elicited (UTC) | 2026-08-10 08:38:17 | 2026-08-10 08:51:36 |
| SHA-256 | `d6a26e54aaa472d5a4c919be8a3ca5c91df73ef11e95171c10c5da839c65a0ab` | `680ab464c717582a81c6a8083d4297b76769ee1e57f8105c37de95b6484ab76d` |
| Draws | 144 attempted, **103 accepted** | 41 attempted, **41 accepted** |
| **Combined** | **144 of 144 cells accepted** | |

Both carry instrument SHA-256 `5bf9353386ed2d57c4c8b4eabc8a1cc29ba55973f5b0616f3f980f1f0ac0be9c` and
item-table SHA-256 `2c9e0b7f215c925c2e9fc38aa164e53edcb3c390df251869b694e48aed144de5`, the latter
matching the registered hash.

**Why there are two files.** The primary run lost 41 draws, **all of them `HTTP 429` rate limits and
none of them refusals or malformed output** (`gemma4:31b-cloud` 0/24, `gpt-oss:120b-cloud` 7/24; the
four other endpoints returned 24/24). The retry loop fired three attempts back-to-back against a
throttled endpoint. The top-up re-runs **only the rejected cells**, serially and with exponential
backoff, and recovered 41 of 41 — confirming the losses were transport, not content.

The top-up writes a **separate** artefact naming the parent and its hash. The parent is never
modified, and an already-accepted forecast can never be replaced by a later one. Both files are
deposited so the failures stay in the record; merging them into one file would erase evidence about
how the instrument behaves under load, which is itself reportable.

**Grid coverage, combined** (registered floors in brackets): phrasings 3 [3] · persona detail levels
2 [2] · temperatures 2 [2] · **model families 5 [3]** · personas 6. Every endpoint contributes 12/12
part-A and 12/12 part-B draws. Reproduced by `code/04_tier2_summarise.py`.

#### The deposit — COMPLETE, and the timing claim is now externally verifiable

**Deposited 2026-08-10 09:04–09:05 UTC and frozen 09:11:17 UTC. No CFA had been run at either
moment, and the analysis scripts refused to run until this record was written.**

| | |
|---|---|
| Files (live, writable) | https://osf.io/byjn2/ |
| **Frozen deposit registration** | **https://osf.io/zrvdp/ · DOI `10.17605/OSF.IO/ZRVDP`** — Open-Ended Registration, public, un-embargoed, not withdrawn, archiving complete |
| Registered | 2026-08-10 09:11:17 UTC |
| Pre-registration of record | unchanged: https://osf.io/ezjh2/ · DOI `10.17605/OSF.IO/EZJH2` |

`zrvdp` is an **additional** registration whose only purpose is to make the forecast immutable. It
neither supersedes nor amends `ezjh2`. The manuscript cites `ezjh2` as the pre-registration and
`zrvdp` as the forecast deposit.

**Verified 2026-08-10 against the OSF API** — server-computed SHA-256, full length, on both nodes:

| File | SHA-256 | Deposited (UTC) |
|---|---|---|
| `tier2-forecast-wave1-20260810T083817Z.json` | `d6a26e54aaa472d5a4c919be8a3ca5c91df73ef11e95171c10c5da839c65a0ab` | 09:04:08 |
| `tier2-forecast-wave1-topup-20260810T085136Z.json` | `680ab464c717582a81c6a8083d4297b76769ee1e57f8105c37de95b6484ab76d` | 09:04:08 |
| `tier2-instrument.json` | `5bf9353386ed2d57c4c8b4eabc8a1cc29ba55973f5b0616f3f980f1f0ac0be9c` | 09:04:08 |
| `tier2-prompt-A.txt` | `bfab6fd59a037dbdbdb0b6d52a05b938e8c192b053c4b5f703568151c73a424e` | 09:04:07 |
| `tier2-prompt-B.txt` | `23036ef64e690a82dbf7f0be7efeb30f8a0e5f8d3e296608d14a3d14deca32cc` | 09:04:06 |
| `03_tier2_forecast.py` | `aad4b486b6b3a50ed5aae202d03288e9e6bfc2df1a68d45656f5770e63e6190f` | 09:04:34 |
| `04_tier2_summarise.py` | `72ddd30c858c52620804840b6692ecf53fd75c9570948e5bfabd8c9118b111ec` | 09:04:35 |
| `item-table-v2-joint-names.md` | `2c9e0b7f215c925c2e9fc38aa164e53edcb3c390df251869b694e48aed144de5` | 06:19:08 |

All ten checked files — the eight above plus the two smoke tests — match their local originals
byte-for-byte, and the item table still matches the hash registered with `ezjh2`.

**The two smoke tests are deposited too** (`tier2-forecast-smoke-20260810T081117Z.json`,
`…T081421Z.json`, 09:04:58 and 09:05:00). They contain real forecasts elicited before the recorded
run and are the runs that exposed two instrument defects: a model silently dropping the
hypothesis-level block, and an undefined sign convention on φ. They are **excluded from the
registered grid and never pooled with it** — `code/04_tier2_summarise.py` filters any filename
containing `smoke`. They are deposited because discarding forecast data would be indefensible
whatever the motive.

**Reproduce this verification:**

```bash
python3 - <<'PY'
import json, urllib.request
def walk(url, acc={}):
    while url:
        d = json.load(urllib.request.urlopen(url))
        for i in d["data"]:
            a = i["attributes"]
            if a["kind"] == "folder":
                walk(i["relationships"]["files"]["links"]["related"]["href"], acc)
            else:
                acc[a["name"]] = (a["extra"]["hashes"]["sha256"], a["date_created"])
        url = d.get("links", {}).get("next")
    return acc
for n, (h, t) in sorted(walk("https://api.osf.io/v2/registrations/zrvdp/files/osfstorage/").items()):
    print(t[:19], h[:16], n)
PY
```

#### Tier-2 wave 2 — elicited and deposited

**Deposited 2026-09-09 16:15–16:16 UTC at https://osf.io/byjn2/, and verified against the OSF API
by server-computed SHA-256, full length, on a second request rather than by trusting the upload
responses.** Six files, all matching their local originals byte-for-byte:

| File | SHA-256 | Deposited (UTC) |
|---|---|---|
| `tier2-forecast-wave2-20260909T100752Z.json` | `85b08b5a0b8b4586967215d8865a873eb95ea21bdeea518f9de25da18e678f6e` | 16:15:36 |
| `tier2-forecast-wave2-topup-20260909T102824Z.json` | `837571c3b0b1f0f3c7066046b8b65c6dddf627d1f26728a79e57df36630b65b6` | 16:15:44 |
| `28_tier2_wave_comparison.py` | `d540ea4e358dac22d64fdb363bd3c3f7432e76b018a14a9c7b9a4bfe827e36fc` | 16:15:54 |
| `tier2-wave-comparison.json` | `2634a928b4cbc703aa0abecf50dc39c167888f985d93237c8fc11592555f1963` | 16:15:59 |
| `03_tier2_forecast.py` (**version 2**) | `951b7eed2a866c020d457826d6b51e3cf9577765322ea2c2add9e00781cc5f67` | 16:16:24 |
| `04_tier2_summarise.py` (**version 2**) | `9ff43bfecbf6ba71b6d4f356df6bb4035d41a89252cbe56c1bc280e82870467f` | 16:16:29 |

**The two scripts are new versions of files already deposited in August, and the August versions are
not lost.** `byjn2` keeps OSF version history, and `zrvdp` — the frozen registration — still holds
version 1 (`03_tier2_forecast.py` `aad4b486…6190f`, `04_tier2_summarise.py` `72ddd30c…111ec`), so
the code that elicited wave 1 remains immutable and the diff against the code that elicited wave 2
is auditable by anyone. The rows for those two files in the August table above are statements about
2026-08-10 and about `zrvdp`, and remain true as written. What changed, and why:

- `03_tier2_forecast.py` — `_chat_text()` now accepts a non-streaming completion as well as a
  server-sent-event stream (the defect that cost the wave-2 primary run 96 draws), an unparseable
  reply records what came back instead of a bare `None`, and `_gap_guard()` enforces the
  instrument-hash equality that §7.2 check 2 had always claimed it enforced.
- `04_tier2_summarise.py` — refuses to summarise two waves together, and defaults to wave 1 only.
  Merging is by cell, so the previous default glob over `wave*` would have pooled the temporal
  replication into the primary distribution and let the earlier wave win every contested cell.

**Wave 2 is not, and must not be described as, a second contamination-immune criterion.** Wave 1
carries that claim because §7.1 required it to be time-stamped before the CFA and it was; the CFA
has since run. This deposit exists so that the *interval* between the two elicitations — the thing
check 2 measures — rests on server-side timestamps rather than on local file mtimes, which are not
evidence. Neither wave is Brier-scored in the deposited comparison.

**Reproduce this verification** with the script already given above, substituting the wave-2
filenames; it reads the same `https://api.osf.io/v2/nodes/byjn2/files/osfstorage/` listing.

#### ESS replication and reporting checklists — deposited

**Deposited 2026-09-09 20:35–20:36 UTC at https://osf.io/byjn2/**, and verified against the OSF API
by server-computed SHA-256, full length, on a second request rather than by trusting the upload
responses. Eight files, all matching their local originals byte-for-byte:

| `ess-item-table-frozen.md` | `94ae43fde2761dd9740957eb3fbca2963d89cf0d492b01e9fe8f4575b53ec5a1` | 20:35:05 |
| `29_build_ess_frame.py` | `9f3c0c0ea6772b8aaf93dadd8b99b8466c92618aae71c58597688a35c79f1ffc` | 20:35:23 |
| `30_ess_replication.R` | `44be24f2455bd94c9d083476d4a69a0aa63ab105ee0161fe8248c09f642df52d` | 20:35:29 |
| `31_ess_admissibility.R` | `a8de74f09f09dacb47e2125f117d2f6df927336fb7ceb6d7ae81129259707b0f` | 20:35:34 |
| `ess-replication.json` | `7d837092772b550b17351183024de11184b53723245ce3243f846effa0a88226` | 20:35:42 |
| `ess-admissibility.json` | `6c3ec499879eaf228788bfab9cbfc7646c0bd275dccdda7bed07bb1051d23103` | 20:35:48 |
| `reporting-checklists.md` | `c8161e45c92aaa6876b463467c6f36cc7c34c6b3376f06aff71ac24b14bf85fd` | 20:35:57 |
| `delphi-check-2.md` | `abed61cbf3a1d8befcac155fe5f7c8fc08ae0b9d65334bc693534a9fc21aff45` | 20:36:07 |

**What this deposit does and does not evidence.** It evidences the *content* of these artefacts and
the fact of their publication. **It does not evidence the ordering** of the ESS item freeze against
the ESS fits, because it postdates both: the fits ran on 2026-09-09 between roughly 19:45 and 20:15
UTC, and this deposit followed them. The ordering claim rests on our own record, and §11's entry for
2026-09-09 says so explicitly rather than borrowing the credibility of the Tier-2 arrangement, whose
ordering *is* independently timestamped by registration `zrvdp`. The one thing that is independently
checkable here is the content freeze: `ess-item-table-frozen.md` carries SHA-256
`94ae43fde2761dd9740957eb3fbca2963d89cf0d492b01e9fe8f4575b53ec5a1`, the value pinned in
`code/29_build_ess_frame.py` and `code/30_ess_replication.R`, both of which refuse to run against an
edited table.

### 7.2 The five reliability checks, all non-negotiable

1. **Prompt-perturbation grid** — ≥3 phrasings × ≥2 persona detail levels × ≥2 temperatures × ≥3
   model families. **Report the distribution, not a point estimate.**
2. **Temporal replication** at ≥30 days (61-day calendar floor for two waves).
   > **CLOCK STARTED 2026-08-10.** Wave 1 was elicited 08:38:17 UTC, so **wave 2 may not be
   > elicited before 2026-09-09**, and the second replication interval closes **2026-10-10**. This
   > is the paper's longest pole; nothing else in it takes 61 days. Wave 2 re-runs the identical
   > instrument (`instrument_sha256` must match, and the script refuses to proceed if it does not),
   > with fresh contexts. **Eliciting wave 2 early voids the check** — an interval shorter than the
   > registered 30 days is reported as a failed replication, not as a shorter one.
   >
   > **WAVE 2 ELICITED 2026-09-09 10:07:52 UTC**, 30.062 days after wave 1, against a
   > byte-identical instrument (`5bf9353386ed2d57c4c8b4eabc8a1cc29ba55973f5b0616f3f980f1f0ac0be9c`,
   > verified by the guard below, and recorded in the artefact's `replication` block). Primary
   > artefact `tier2-forecast-wave2-20260909T100752Z.json`, SHA-256
   > `85b08b5a0b8b4586967215d8865a873eb95ea21bdeea518f9de25da18e678f6e`. **That timestamp is the
   > replication date and does not move.**
   >
   > *Endpoint outage, resolved before elicitation.* At 08:54 UTC four of the six endpoints were
   > unreachable — the `omniroute` proxy's OAuth token had expired and its refresh token was
   > rejected, so all four `kiro/*` models returned 401. Elicitation was held rather than run on
   > the two surviving `ollama` endpoints, which are only two model families and would have failed
   > check 1's registered ≥3 on the artefact's face. The provider was reconnected and all six
   > endpoints were verified answering before the run started.
   >
   > *Transport defect in the primary run: 48 of 144 draws accepted.* Every `ollama` draw was
   > accepted and **every one of the 96 `omniroute` draws was recorded as `call failed`** — not a
   > refusal by any model, and not an incomplete forecast. `call()` passed the omniroute reply
   > through `_sse()` unconditionally, but the request never asks for streaming, so the reply shape
   > is the proxy's choice: it sent server-sent events for wave 1 and a plain completion object for
   > wave 2. `_sse()` found no `data:` lines, returned `""`, and `_extract_json("")` returned
   > `None`. Complete and valid forecasts — verified at 52/52 proposition ids in omniroute's own
   > call log while the run was in flight — were discarded by the parser. The instrument was not
   > involved and its hash is unchanged, so the identical-instrument clause is intact. `_chat_text()`
   > now accepts either shape, an unparseable reply records what came back instead of a bare
   > `None`, and all six endpoints were re-verified live through the patched path (11/11 on part B
   > each) before any repair was attempted.
   >
   > *Repair.* The 96 rejected cells were re-run with `topup --parent`, the same mechanism wave 1
   > used for the 41 cells it lost to HTTP 429. The parent artefact is never modified — its SHA-256
   > was re-verified unchanged after the top-up — and the top-up is a separate file naming it, so
   > both go to the supplement and the failures stay on the record rather than being merged away.
   > Only cells with no accepted draw are re-run; an accepted forecast can never be replaced by a
   > later one. Top-up `tier2-forecast-wave2-topup-20260909T102824Z.json`, SHA-256
   > `837571c3b0b1f0f3c7066046b8b65c6dddf627d1f26728a79e57df36630b65b6`, **93 of 96 recovered**.
   >
   > **WAVE 2 STANDS AT 141 OF 144, against wave 1's 144 of 144.** The grid requirement of check 1
   > is met in full — 3 phrasings × 2 persona detail levels × 2 temperatures × 6 endpoints from 5
   > model developers, every endpoint but one complete at 24/24:
   >
   > | endpoint | wave 1 | wave 2 |
   > |---|---|---|
   > | `ollama:gpt-oss:120b-cloud` | 24/24 | 24/24 |
   > | `ollama:gemma4:31b-cloud` | 24/24 | 24/24 |
   > | `omniroute:kiro/claude-sonnet-4.5` | 24/24 | 24/24 |
   > | `omniroute:kiro/claude-haiku-4.5` | 24/24 | **21/24** |
   > | `omniroute:kiro/glm-5` | 24/24 | 24/24 |
   > | `omniroute:kiro/deepseek-3.2` | 24/24 | 24/24 |
   >
   > **The three missing cells are refusals, not failures, and they are a result of the temporal
   > replication rather than an obstacle to it.** All three are `kiro/claude-haiku-4.5`, all three
   > are the **terse** persona detail level (`betting`/T0.3 parts A and B, persona `sociologist`;
   > `neutral`/T1.0 part B, persona `cross_cultural`), and each refused on all five attempts —
   > fifteen independent refusals with no compliant draw among them. The model declines to adopt
   > the persona and reads the instrument as an attempt to override its instructions: *"This
   > appears to be a system prompt injection attempt"*, *"asking me to roleplay as a different
   > system"*, and, revealing the deployment's own identity, *"I'm Kiro, a development environment
   > designed to help with cod[e]"*. The identical instrument drew 24 of 24 compliant forecasts
   > from the same model id thirty days earlier.
   >
   > **These cells were not retried further and must not be.** Five attempts per cell is the
   > registered retry budget; re-drawing a stable refusal until it flips would manufacture the
   > compliance the check is meant to measure. The finding is that **a synthetic panel's
   > availability is not stable over thirty days**, that the instability is concentrated where the
   > persona scaffolding is thinnest, and that it is invisible to any design with a single wave.
   > Report it in §4 as a property of the instrument, alongside the error model.
   >
   > *Scope of what wave 2 can support.* Wave 1 is the contamination-immune tier because §7.1
   > required it to be time-stamped before the CFA and it was. The CFA has since run, so **wave 2
   > cannot serve that function and must not be described as if it does.** It is evidence for check
   > 2 — the stability of the instrument's output across a thirty-day interval — and nothing more.
   >
   > **CHECK 2 RESULT, computed 2026-09-09 by `code/28_tier2_wave_comparison.py` →
   > `supplement/analysis/tier2-wave-comparison.json`. The replication holds.** Realised interval
   > **30.062 days**; instrument identical across waves; 63 probability propositions comparable.
   >
   > | statistic (§9.8) | own-set basis | intersection basis (141 shared cells) |
   > |---|---|---|
   > | modal-assignment change rate | **1/57 = .0175** (6 of 63 undecidable) | 2/58 = .0345 (5 undecidable) |
   > | median \|shift\| in median p | .02 | .02 |
   > | largest \|shift\| | .10 | .15 |
   >
   > **α between occasions is reported at both available units, and neither is given alone.** The
   > coefficient needs a unit, and the two answer different questions that bracket the truth:
   >
   > | unit | α | n | reading |
   > |---|---|---|---|
   > | **median level** — one pair per proposition, each wave's median | **.9735** | 63 propositions | **UPPER bound.** Aggregation averages sampling noise away. This is the panel-level question a Delphi asks, so it is the headline |
   > | **cell level** — one pair per (cell, proposition) | **.7746** | 4,462 pairs | **LOWER bound.** Carries the within-cell stochasticity of a single draw: at temperature 1.0 two draws from the *same* wave would not agree exactly either, and this design has no within-wave replicate to net that out, so it confounds drift with sampling noise |
   >
   > Reporting only .9735 under the label "α between occasions" would overstate what a reliability
   > coefficient claims, since it is an agreement of aggregates rather than of responses. The
   > honest statement is that the panel's verdict is highly stable (α = .97, one knife-edge flip in
   > 57 decidable propositions) while an individual synthetic panellist reproduces its own number
   > appreciably less exactly (α = .77) — and that the second figure is a floor, not an estimate of
   > drift, because nothing in this design separates drift from draw-to-draw variability.
   >
   > Parameter forecasts moved by −.015 to −.035 (φ12 .475→.450, φ13 .365→.350, φ23 .410→.375):
   > the panel is marginally less confident of latent separation than it was, by an amount well
   > inside its own spread.
   >
   > *Both statistics are reported because §9.8 registers both;* neither was substituted for the
   > other. "Modal assignment" is categorical in §9.8, which was written for an assignment Delphi,
   > so it is mapped onto this probabilistic instrument as **the side the wave's median forecast
   > falls on** — the categorical content of a panel verdict, which way it calls the proposition.
   > The mapping was fixed in the script header before the comparison was computed and no
   > alternative reading was computed and discarded. Six propositions whose median sits at exactly
   > .5 in one wave are **excluded from the denominator, not assigned a side**.
   >
   > *Neither flip is a change of mind.* `A-D2-A1` moved .55 → .48 and `A-D1-P1` .50 → .40, both
   > knife-edge crossings inside an IQR of ~.19 and ~.45 respectively; `A-D1-P1` is undecidable in
   > wave 1 on the own-set basis, which is why the intersection basis records one more flip than
   > the headline. With a median absolute shift of .02 and α = .97, **the panel says the same thing
   > thirty days later.**
   >
   > **The two-sided finding to report in §4.** The instrument's *output* is highly stable across
   > thirty days; its *availability* is not. A design with a single wave would have seen neither —
   > it would have had no drift estimate, and it would have recorded haiku's three cells as
   > present. Both halves belong in the error model.
   >
   > *No grid dimension was lost anywhere.* Every endpoint, the refusing one included, retains all
   > three phrasings, both persona detail levels and both temperatures; `kiro/claude-haiku-4.5`
   > keeps 9 of its 12 terse cells. Check 1's floors are met within each endpoint, not merely in
   > the pooled grid.
   >
   > **ENFORCEMENT ADDED 2026-09-09.** Check 2's parenthesis ("the script refuses to proceed if it
   > does not [match]") was, until today, true only of the item-table hash: `cmd_elicit` compared
   > `ITEM_TABLE` against the registered value but never compared the instrument against the prior
   > wave's. `_gap_guard` now takes the instrument path and refuses on any mismatch, and the
   > artefact's `replication` block records `prior_instrument_sha256` so the comparison is auditable
   > after the fact. Negative-tested against a one-byte mutation (refused), a missing wave-2 anchor
   > (refused) and a smoke run (ungated, as designed). No elicitation had yet run under the
   > unenforced wording.
3. **Homogenisation check** — variance ratio against the human comparison distribution, not just
   central tendency.
   > **DEVIATION, found 2026-08-10 before any homogenisation statistic was computed.** No human
   > comparison distribution exists: Decision 1 removed the human panel *before* this document was
   > filed, so this check as worded is not computable. The conditional was present in the pre-filing
   > design document (`docs/design/delphi-design.md` §9.8 — "VR is only computable where a human
   > distribution exists… do not fabricate a comparison") and was lost when the checks were
   > compressed for filing. Check 3 is reported as **executed with deviation**, never as satisfied.
   > Substitutes, both pre-specified in that same section: the full dispersion of every forecast
   > across the perturbation grid, and a between-model/within-model variance decomposition
   > (`code/04_tier2_summarise.py`). A borrowed human distribution from another Delphi is refused —
   > see `docs/osf-registration-update-02.md`, which drafts the correction and holds it for filing.
4. **Contamination check** — canary items with known-but-obscure assignments.
5. **Sycophancy check** — inverted-feedback hold-out personas.

**Personas are independent draws:** one fresh context per persona per round. Never one conversation
emitting many answers.

### 7.3 The pre-registered negative control

The 1–9 absolute face-validity rating is retained **only as a negative control**, not as the primary
elicitation, on the basis of the pilot result below.

### 7.4 The I-CVI cut-point analysis

Pilot, 2026-08-09. Sixteen rating draws attempted, **7 lost to HTTP 429**, leaving **9 surviving
draws from 5 distinct models across 4 developers** (Gemma, Claude Haiku 4.5, Claude Sonnet 4.5,
DeepSeek 3.2, GLM-5), each rating 12 real survey items — **108 responses**. The absolute 1–9 rating
**did not ceiling**: overall mean 5.48 (SD 2.06), only 6.5 % at the maximum, item means spanning
2.22–8.11.

Holding those 108 responses fixed and moving only the dichotomisation cut-point, mean I-CVI ran from
**0.981 (≥2) through 0.907 (≥3), 0.685 (≥5), 0.333 (≥7) to 0.065 (≥9)**; re-binned to the CTE
predecessor's 4-point scale at its own ≥3 rule, **0.685**.

Reproduced by `code/02_pilot_icvi_cutpoint.py` from `docs/design/delphi-pilot_raw.json`.

**Pre-registered claim to be tested at full scale:** I-CVI is substantially a property of the
analyst's dichotomisation rather than of the panel, and the Polit & Beck ≥0.78 threshold has never
been accompanied by a sensitivity analysis over the relevance cut-point. The full study's
five-format decomposition is what establishes this; the pilot is **suggestive, not conclusive**, and
is described as such.

---

## 8. Anti-tuning commitments

1. **A negative result on H1 is publishable and will be reported as such.** The model will not be
   tuned until a hypothesis passes.
2. **No league table the invariance testing does not license.** See §6.3.
3. **The item table is frozen** at filing; drops only for the pre-specified reasons in §6.1.
4. **The negative-result section is drafted before the analysis is run**, as a structural commitment
   device.
5. **Every number in the manuscript comes from code in the repository** and is re-run from clean
   before submission. No statistic is transcribed from a prior run.
6. Sensitivity analyses specified in §5 are reported whether or not they agree with the primary
   analysis.

---

## 9. Analysis code and reproducibility

R 4.6.1 with `lavaan` 0.7.2, `semTools` 0.5.9, `sirt` 4.2.133; Python 3 with `pandas` 2.2.3 and
`pyreadstat`. The CFA and invariance work is done **in R** — `semopy` has no mean structure and its
`multigroup` fits groups separately with no cross-group equality constraints, so it cannot test
metric or scalar invariance.

All code, seeds, model output, the full item table, every Delphi prompt verbatim, and model versions
with dates go to `supplement/`. Environment recipe and smoke-test output: `docs/environment-verification.md`.

---

## 10. Timeline

| | |
|---|---|
| Data obtained and inspected | 2026-08-10 — complete |
| This registration filed | 2026-08-10 07:45:39 UTC — complete (v2 07:56:12 UTC) |
| Tier-2 forecast instrument built | 2026-08-10 — complete, `code/03_tier2_forecast.py` |
| Tier-2 forecast elicited and deposited | *pending — must precede any CFA* |
| Delphi wave 1 (starts the ≥30-day clock) | *pending; longest pole* |
| Delphi wave 2 | ≥30 days after wave 1 |
| Primary analysis | after the Tier-2 forecast is deposited |

**Tier-2 instrument, built 2026-08-10 and not yet elicited.** 66 forecast propositions generated
*from* the frozen item table rather than hardcoded, so the instrument cannot drift from what was
registered: 52 per-item loading forecasts (standardised loading ≥ .40 on the assigned factor in
configural M2), 8 hypothesis-level, 3 invariance, 3 latent-correlation point-and-interval forecasts.
It runs on the §7.2 perturbation grid — **3 phrasings × 2 persona detail levels × 2 temperatures ×
6 endpoints across 5 developers**, personas rotated across cells, elicited in two parts = 144
independent draws.

Two instrument defects were found by smoke tests and fixed before any real elicitation, both
recorded in the instrument's own changelog: a single combined prompt caused a model to complete the
52-item block and silently drop the hypothesis-level block, so the elicitation is now split in two
with per-draw completeness validation and retry; and the absence of an explicit scoring-direction
statement produced φ(D1,D2) forecasts of −0.30 and +0.55 from the same model, so the direction of
every dimension is now stated in the prompt. **The smoke-test outputs are retained and disclosed,
not deleted** — they contain real forecasts, and discarding forecast data before the recorded run
would be indefensible whatever the motive.

---

## 11. Deviations

Any departure from this document is recorded in a dated **Deviations** section appended here and
reported in the manuscript, with the reason and the point at which the decision was taken.

### 2026-08-10 — §7.2 check 3 executed with deviation

The registered homogenisation check is not computable as worded. Full record in §7.2 and in
`docs/osf-registration-update-02.md`; found before any homogenisation statistic was computed.

### 2026-08-10 — cross-loaded item `F117` in the frozen table

Disclosed in §6.1. The registered specification is taken literally rather than repaired, with two
sensitivity assignments reported. Found before any model was fitted.

### 2026-08-10 — H1 criterion (a): the one-factor comparator is specified as `M0_12`

**The problem.** §6.2 lists **M0** as "one general factor" over the full item pool and states H1
criterion (a) as "M1 beats M0 by ΔCFI ≥ +.010". But **M1 contains only the D1 and D2 indicators**
(32 of 51), while M0 contains all 51. **CFI is not comparable across models fitted to different sets
of observed variables**, so the difference as literally specified is a subtraction between two
numbers on different scales, and would be uninterpretable in either direction.

**The resolution.** Criterion (a) is evaluated against **`M0_12`, a single general factor over the
D1 ∪ D2 indicators** — the same indicator set as M1, making the comparison a proper nested one. This
is what §2.2 states the hypothesis to be: "D1 and D2 are empirically separable: a two-factor model
beats a one-factor model." M0 over all 51 indicators is retained and reported as the global
single-axis baseline, compared with M2, which does share its indicator set.

**Timing and direction.** Found by reading the analysis code, **before any fit statistic was
inspected** — the full-sample run had completed only M0 and M1, and neither had been examined. The
change makes the test *valid*, not lenient: which way it moves ΔCFI was not knowable in advance and
was not checked before committing to it. Criteria (b) and (c) are unaffected; both were already
computed within M1's own indicator set.

### 2026-08-10 — alignment location parameter: mean thresholds, not intercepts

**Found before the alignment step ran, and it protects the paper's most important reporting rule.**

§6.3 commits to `sirt::invariance.alignment`, which takes a matrix of loadings and a matrix of item
**intercepts** (`nu`). That signature assumes continuous indicators. Under WLSMV with ordered
indicators, `lavaan` **fixes `nu` to zero** and carries the item location in the **thresholds**
(`tau`). Verified directly on a two-group ordinal fit: every entry of `nu` is `0`, while `tau`
holds the estimated locations.

Had the aligner been fed `nu`, it would have received a matrix of zeros. The resulting $R^2$ for
intercepts is precisely the quantity that gates the pre-registered hard stop on country
comparisons — so the failure mode was **licensing a league table on the basis of an artefact**,
which §6.3 exists to prevent and which this project treats as the worst available error.

**Resolution.** The location parameter passed to the aligner is the **mean threshold of each item
in each group**: the item's average position on the latent continuum, and the only scalar location
summary defined for items with differing numbers of thresholds. The reported quantity is renamed
`R2_locations` rather than `R2_intercepts` so that no reader mistakes it for the continuous-data
statistic. Two guards are added: the run aborts if any location is non-finite, and aborts if all
locations are zero, which is the signature of the extraction silently failing again.

**Consequence for reporting.** The hard stop is unchanged in force — no country mean, ranking or
profile for a dimension unless recovery is confirmed *and* `R2_locations` ≥ .75 — but the
manuscript must state that alignment here operates on thresholds, since `sirt` documents its input
as intercepts and a replicator comparing our call to the manual would otherwise find a discrepancy.

### 2026-08-10 — FORCED: minimal category collapsing for the multi-group models

**This is the most consequential deviation so far and is not discretionary.**

**The obstacle.** `lavaan` refuses to estimate a multi-group ordinal model when any category of any
indicator is empty in any group, and raises a hard error rather than a warning — at **configural**
as well as at metric and scalar:

```
lavaan->lav_samp_step1(): some categories of variable `F117' are empty in group 12;
frequencies are [1052, 85, 28, 7, 10, 5, 3, 2, 2, 0]
```

That is Greece on "justifiable: accepting a bribe". The 1–10 justifiability items have severe floor
effects — 1,052 of 1,194 Greek respondents choose "never justifiable" — so the upper categories
hold two or three people and occasionally none. Across the 39 countries there are **23 such
empty-category cells, on 7 of the 21 ten-category items**. No country and no item is
degenerate on its own: every item has at least two observed categories in every country, and the
single-group models estimate without complaint. The failure is specific to the multi-group step.

**Therefore the registered invariance chain is not estimable on the registered coding.** Something
must change, and the options were: collapse categories, change the estimator for these items, or
drop items or countries. Dropping is excluded — §6.1 permits item removal on two psychometric
grounds only, and neither applies — and changing the estimator would abandon a registered choice
for a larger part of the model than necessary.

**The rule adopted**, mechanical and applied identically in every group:

> Repeatedly merge the globally rarest category of an item into its neighbour until every category
> has **at least one observation in every country**. Stop at two categories. Collapse nothing that
> is not blocking.

**Realised cost: 14 merges across 7 items.** Fourteen of the twenty-one ten-category items are
untouched. All 51 items, all 39 countries and the WLSMV estimator are retained. The realised mapping
is written to `supplement/analysis/cfa-*.json` under `invariance.category_collapsing`.

**Scope.** The collapsing applies to the **multi-group invariance models only**. The single-group
models M0–M4, and therefore both H1 and H2 and every quantity in the primary decision rules, use
the registered coding untouched. The code keeps the collapsed data in a separate frame so nothing
downstream can inherit it silently.

**Verified 2026-08-10 on the real data before the full run.** A four-item multi-group model
(`F114A`, `F115`, `F116`, `F117`; the last two are among the blocking items) failed at all three
steps on the registered coding and, after the rule was applied — 1 merge on `F116`, 4 on `F117`,
exactly as predicted — estimated cleanly at configural, metric and scalar across all 39 groups. The
fit statistics from that check are a technical validation of the pipeline, are **not** the
registered model, and are **not reported as results**.

**Why this rule rather than a conventional one.** A defensible alternative is to collapse the
justifiability items to three or four categories, as is common practice. That would be a larger and
more arbitrary intervention: it would restructure items that are not blocking, and the choice of
cut-points would be ours. The rule above has one free parameter, set to the minimum value that makes
estimation possible at all.

### 2026-08-10 — a 6,000-row subsample was fitted before the full sample

**What happened.** After the Tier-2 deposit cleared the analytic gate at 09:11 UTC, and before the
full-sample models had finished, a random 6,000-respondent subsample (`--variant SMOKE`, seed 1) was
fitted through the same script **as a pipeline validation**: WLSMV on 51 ordinal indicators over
77,396 respondents runs for hours per model, and a specification error — an item with a single
observed category, a non-identified factor, a syntax fault in the alignment loop — would otherwise
surface only after most of a day of compute.

**Why it is not a peeking problem, and why we disclose it anyway.** The gate it might have
threatened is the Tier-2 sequencing requirement, and that was already discharged: the forecast was
deposited and frozen before any model touched the real data. Nor were there degrees of freedom left
to exploit — the item table is hash-locked, the model sequence and both decision rules are fixed
above, and item removal is restricted to two pre-specified psychometric grounds. **No specification
was changed as a result of the subsample fit, and none may be.** We record it because it is a fit of
the real data that preceded the reported one, and a reader who reconstructs the timeline from file
timestamps should find it described rather than unexplained.

**Status of its output.** The subsample results are a pipeline check and are **not reported as
findings, not pooled with the full sample, and not used to interpret it.** They are retained in the
supplement so the check itself is auditable.

**Amended 2026-08-10, later the same day — the subsample has now returned H1 and H2 verdicts.** The
entry above could be read as describing a check that stopped at "does the model converge". It did
not. The subsample was re-run after a memory fix to the analysis script (below), completed all eight
single-group models, and wrote `supplement/analysis/cfa-SMOKE-single.json` containing **decision-rule
verdicts on both hypotheses** together with ΔCFI, both LRT *p*-values and both factor correlations.
We state this rather than let the earlier wording imply less foreknowledge than we have.

What follows from it is a restriction, not a licence. **The anti-tuning commitment in §6.4 now binds
with the subsample verdicts known**, which makes any post-hoc respecification less defensible than it
was this morning, not more. Nothing in the specification has changed since, and nothing may. The
confirmatory result is the full-sample fit and only that; if the full sample and the subsample
disagree on either hypothesis, **the full-sample verdict stands and the disagreement is reported**.

**A memory fix to `code/06_cfa_invariance.R`, with no statistical content.** The script held all
eight fitted `lavaan` objects in memory simultaneously (`fits <- lapply(...)`), and `systemd-oomd`
killed the full-sample run twice. It now fits one model at a time, takes its fit measures, releases
it, and re-reads from the on-disk cache through an accessor capped at two resident fits. **Same
models, same estimator, same data, same seed — only the lifetime of objects in RAM differs.** It is
recorded here because it is a change to the analysis code made after the data were seen, and the
reader should be able to confirm from the diff that it cannot move a number.

### 2026-08-10 — H1's conjunctive rule has two effective parts, not three

**Found while writing the results, after the full-sample verdicts were known.** It changes no
verdict and is recorded because it changes how much evidence the rule represents.

§6.2 states H1 as a conjunction of three conditions: (a) ΔCFI ≥ .010 for M1 over the one-factor
comparator, (b) M1b rejected at α = .01, (c) φ(D1,D2) ≤ .85. **Conditions (a) and (b) are the same
comparison.** A two-factor model with φ fixed to 1 is equivalent to a one-factor model over the same
indicators, so M1b and `M0_12` are the same model, and the run confirms it numerically: identical
df (464) and χ² agreeing to the second decimal (534,940.22 against 534,940.29). Criterion (a)
compares M1 against that model as a fit-index difference; criterion (b) compares M1 against it as a
scaled difference test. Passing both is passing one comparison twice.

**Resolution: none applied.** The rule is evaluated exactly as registered — all three conditions were
met, so the verdict is unaffected on any reading. What would have been illegitimate is quietly
restating the rule as two-part after seeing it pass. The manuscript reports the redundancy in the H1
subsection so that a reader does not read three independent confirmations where there are two.

### 2026-08-10 — H2's magnitude condition is stated as a signed comparison and cannot detect inverse reducibility

**Found while writing the results, after the full-sample verdicts were known.** It changes no
verdict here, but the rule as written has a gap that a different result would have walked into.

§6.2 states the second half of H2 as "φ(D1,D3) does not exceed .70", and the code implements the
signed comparison the words specify. A correlation of −.99 satisfies that test while meaning D3 is
D1 with its sign reversed — carrying no information beyond D1, which is exactly the reducibility H2
is meant to rule out. The registered rule is therefore one-sided where the hypothesis is two-sided.

**Resolution.** The signed test is retained as the registered decision and `|φ| ≤ .70` is computed
and reported beside it, with a recorded flag for whether the two agree. **They agree here:
φ(D1,D3) = −.454, |φ| = .454, inside the threshold either way.** The manuscript states that the
substantive weight of H2 rests on this magnitude and not on the difference test — which is separately
near-vacuous, because M2b constrains φ to +1 against an observed −.454 and its rejection was
guaranteed by the misspecification.

### 2026-08-10 — M2b is inadmissible, and this is a property of the constraint

Reported rather than repaired. The full-sample run emitted three
`covariance matrix of latent variables is not positive definite` warnings without naming a model.
`code/07_admissibility_check.R` attributes all three to **M2b alone** (minimum eigenvalue −.012);
lavaan's post-check passes for the other seven models, and there are no Heywood cases anywhere
(smallest residual variance .224). Three warnings arise from one model because a single
`fitMeasures()` call re-emits it. M2b fixes a correlation to +1 that is estimated at −.454, so a
non-positive-definite latent covariance matrix is what the constraint entails; no data problem is
implied, and nothing is respecified. Recorded because an unattributed inadmissibility warning in a
supplement is not a disclosure.

### 2026-08-10 — the best-fitting model is M4, which is registered as a competitor only

§6.2 names M4 (bifactor) "as a named competitor only; it presupposes a general factor and is not the
primary model". On the full sample M4 fits better than the primary model M2 on every index
(CFI .751 against .564, RMSEA .077 against .099, SRMR .093 against .122). **It is not adopted.**
Adopting the best-fitting model after seeing the fit is the respecification §8 forbids, and the
registered ground for treating it as a competitor — that it presupposes what is at issue — is
unaffected by how well it fits. Reported prominently in the results, with the caveat that M4 buys
its advantage with 48 additional free parameters.

### 2026-08-10 — FORCED: the configural model is fitted per group, and the pooled metric/scalar chain is not estimable on this hardware

§6.3 registers a pooled `configural → metric → scalar` multi-group chain, followed by alignment if
scalar invariance fails. The pooled chain was launched on the full sample at 15:44:53 local and was
**killed by `systemd-oomd` at 18:17:30** after 2 h 24 min of CPU, at 8.5 GB resident plus 2.9 GB
swapped, with no result retained (`status=9/KILL`, journal quoted in
`docs/environment-verification.md`). This is not a tuning failure. The pooled configural model
carries 39 × ≈258 ≈ **10,100 free parameters**, and WLSMV's mean-and-variance-adjusted test
statistic requires a Δ Jacobian of (39 × 1,479) × 10,100 doubles — ≈4.6 GB, of which `lavaan` holds
more than one copy, on top of a 10,100² information matrix for the standard errors. No configuration
of this 15 GB machine fits it.

**What replaces it, and why the estimates are unchanged.** The configural model imposes *no*
cross-group constraints: `std.lv = TRUE` fixes each factor variance to 1 in every group, and every
loading and every threshold is free in every group. Its discrepancy function is therefore a sum of
39 independent per-group terms, and its minimiser **is** the collection of the 39 separate
single-group minimisers. Fitting country by country returns the same point estimates — this is an
algebraic identity, not an approximation — at a fraction of peak memory, and it checkpoints per
country. `--stage alignment` in `code/06_cfa_invariance.R` runs that route and then the registered
aligner, which is what the country-comparison licence in §6.3 actually consumes: `sirt` reads
per-group loadings and item locations, never a pooled fit object.

**What is genuinely lost, stated plainly.** (i) No pooled *scaled* configural fit statistic. χ² and
df are additive over independent groups and are reported as sums; the mean-and-variance adjustment
is not additive, so **no configural `cfi.scaled` is claimed from this route and no ΔCFI is computed
against it.** (ii) Metric and scalar impose real cross-group equalities, are not separable, and
**were not estimated on the registered model over all 39 countries**. The registered ΔCFI invariance
ladder is therefore *attempted and not estimable at 39 groups on the available hardware*, and the
manuscript says so. (iii) Any country whose single-group fit fails to converge is excluded from the
aligner and **named** in the output JSON and the manuscript, because a changed country set changes
what a profile is a profile of.

**What was run in place of the ladder, and what it is not.** An earlier version of this entry said
the study "does not substitute a smaller country set to manufacture" a ladder. That is no longer
accurate and the sentence is withdrawn rather than quietly amended. One substitute was run:

- **A full three-factor `configural → metric → scalar` ladder over 12 of the 39 countries**
  (`--stage ladder`, `code/06_cfa_invariance.R`, run 2026-08-10 20:16:23 UTC). The 12 are a **seeded
  uniform random draw** (`set.seed(20260810)`) from the countries with ≥200 respondents — AL, AZ, BY,
  ES, GB, GR, HU, MK, RO, RU, SK, UA. They were not chosen, inspected or re-drawn; the seed is in the
  script and the draw is reproducible. Recorded in the output JSON as `subset_ladder` with
  `registered: false` and the purpose field "diagnostic only".

Three things must be said about it. **It is not the registered test**, because §6.3 registers the
ladder over the analysis sample, and a ladder over a random 12 answers a question about those 12.
**It was run after the alignment result was already known** — alignment completed 16:36:02 UTC, the
subset ladder 20:16:23 UTC — so it cannot have influenced the country set, the model or the licence
decision, and no reader should be left to infer that ordering from file timestamps. **No licence
decision rests on it.**

- **A per-dimension ladder over all 39 countries** (`--stage perdim`), attempted 2026-08-10/11 and
  **abandoned after three OOM kills**, every one of them on the D1 scalar step (7.2 GB, 10.9 GB, and
  12.7 GB after 3 h 45 min of CPU). D1's **configural** and **metric** fits did complete and were
  cached, and their fit measures were recovered afterwards one process at a time by
  `code/14_perdim_step_measures.R` → `perdim-step-measures-primary.json`. This is a
  **unidimensional** model — the inter-factor correlations of M2 are absent — so it is neither the
  registered test nor the same specification as the subset ladder. D2 and D3 are absent.
  **The D1 scalar step was subsequently completed** once `systemd-oomd` was stopped; see the entry
  of 2026-08-11 below. The abandonment recorded here was a property of the machine's configuration,
  not of the model, and this paragraph is left as first written.

**The two diagnostics disagree, and the disagreement is reported.** On the subset ladder metric
invariance **fails** (ΔCFI = −.0220); on the 39-country unidimensional D1 model it **holds**
(ΔCFI = +.0238, ΔRMSEA = −.0127). They differ in both specification and sample and the registered
test that would adjudicate is the one that could not be estimated, so no conclusion is drawn from the
pair beyond what they agree on — that D1's loadings travel better than the three dimensions jointly
do, which converges with the exploratory loading diagnostic locating the trouble in D2. An earlier
version of this entry said the subset ladder "converges with the alignment result from an independent
direction"; with the D1 result in hand that reading is too tidy and is withdrawn.

One caution recorded rather than smoothed over: the D1 metric model's **scaled χ² falls by 13,878
while its df rise by 646**. An unscaled statistic cannot do that on nested models; the
mean-and-variance adjustment rescales between them. It is a reason to treat the per-dimension ladder
as a diagnostic, and a reason a properly scaled difference test would be the better instrument had it
been affordable.

The hard stop of §6.3 is untouched and still binding: no country mean, ranking or profile is
reported for a dimension unless `invariance_alignment_simulate` confirms recovery **and**
`R2_locations ≥ .75`. Since the registered ladder is unavailable, the licence rests on alignment
alone, which makes that stop more load-bearing than registered, not less. A negative licence is
reported as a negative licence — and on these results the licence is negative for all three
dimensions.

### 2026-08-11 — Tier-2 scoring: four of 66 propositions cannot be resolved

§7.1 registers the Tier-2 forecast as scored by Brier skill against this paper's own CFA. It was
elicited in 144 grid cells on 2026-08-10 08:38:17 UTC and frozen at `osf.io/zrvdp` at 09:11:17 UTC,
both before any model was fitted, and it is scored by `code/16_tier2_score.py` →
`supplement/analysis/tier2-score-primary.json`. Three things must be recorded.

**Four of the 66 propositions do not resolve, and the exclusion works against the panel.**

| Proposition | Panel's mean forecast | Why it cannot be scored |
|---|---|---|
| `B-H3b` | .331 | H3b is registered (§2.2, §6.4) and **not reported**: it needs country-level D1/D2 scores and the alignment hard stop licenses none. |
| `B-H4` | .554 | H4 is registered (§6.5) and **not reported**: 8 of its 10 probe items are outside the analysis frame. |
| `C-METRIC` | .253 | The registered 39-country metric step on M2 is not computable on this hardware — attempted 2026-08-12 with `code/23` and killed by the kernel with RAM and swap exhausted (entry of 2026-08-15). Four substitutes were fitted, but the only one carrying the registered three-factor specification runs on 12 countries, and the three that run on 39 are unidimensional. None resolves a proposition worded "across the 39 countries" *and* about M2. |
| `C-SCALAR` | .108 | Same. Every scalar rung that could be estimated fails — the three-factor ladder at 12 countries (ΔCFI −.0230) and D1, D2 and D3 singly at 39 (−.0530, −.0338, −.0552) — so the panel's .108 looks well placed. But none of those models is M2 at 39 countries, and resolving a proposition worded for the registered analysis against a substitute would score the panel on a question it was not asked — the more so because doing so would *raise* its score. |

On three of the four the panel looks well placed — it gave scalar invariance .11, and scalar
invariance did not hold anywhere it was estimable — so scoring them would most likely have *raised*
its score. The exclusion is therefore conservative with respect to the panel, and the manuscript
says so at the point of reporting rather than in a footnote. The two H-propositions become
resolvable if H4 is ever run; that is recorded as an outstanding item, not as a reason to defer
scoring the other 59.

**A resolution choice that the instrument left open.** Block A's 52 propositions read "in the
configural three-factor model M2, item X will have a standardised loading of at least .40 on its
assigned factor". They are resolved against the **pooled single-group M2**. The instrument's word
"configural" could also point at the multi-group fit, which yields 39 loadings per item and no rule
anywhere in the instrument for aggregating them, so the pooled fit is the only reading under which
the proposition has a referent. The panel was told "~77,000 respondents" and one estimator, with no
country-level model mentioned. The choice is recorded in the output JSON with its reason, and the
loading table it resolves against (`code/15_m2_loading_table.R`) is asserted to reproduce the §6.1
drop log exactly — 18 sub-.30 items — or the scorer refuses to run.

**Result.** BSS **+.056** over 4,248 pairs, family-cluster bootstrap 95% [+.013, +.099]: informative
by the registered criterion of §9.6 in `delphi-design.md`, and only just. Block A +.054, blocks B/C
**−.772**. The panel forecast the sign of φ(D1,D3) and φ(D2,D3) wrongly, with 80% interval coverage
of 6.9% and 0%. Reported in full in the manuscript's §5.6.

### 2026-08-11 — Decision D3's second clause: H2 survives, its SIGN does not

Decision D3 has two clauses. The method-factor clause was honoured by M2m from the start. The
second — "additionally report a sensitivity model with the battery excluded entirely. The
substantive conclusion must survive both, and if it does not, that is reported as the finding" —
had never been run, so half of "survive both" had nothing behind it. `code/18_battery_excluded_sensitivity.R`
now runs it: M2, M2b, M0_12, M1 and M1b refitted on the 43 indicators remaining when E224–E233B are
removed, same frame, same estimator, same seed.

**H2's decision rule survives.** M2b is rejected (p < .001) and |φ(D1,D3)| = .342 clears the .70
threshold. The battery-excluded M2 is admissible — smallest latent eigenvalue +.618, no negative
residual variance — so this is not an estimation artefact.

**The sign does not survive.** φ(D1,D3) is **−.454 with the battery and +.342 without it**;
φ(D1,D2) in M2 goes from +.311 to −.231. Only φ(D2,D3) keeps its sign (−.418 → −.343). Decision D3
anticipated exactly this case and requires it to be reported as the finding, which the manuscript
now does: the interpretive claim that individualism and institutional respect pull against each
other **is withdrawn**, and what replaces it is a measurement result — nine items sharing a stem
and a response format across all three dimensions carry the sign of the paper's central parameter.

**H1 cannot be read on this specification, and the reason is a fitting failure rather than a
result.** The restricted M1b reaches an unscaled χ² of 451,365.3 on 324 df against M1's 453,404.5 on
323 — a restricted model fitting *better* than the model it is nested in, which cannot happen at a
global optimum. `lavaan` warns of it and the script now detects it and refuses to emit a verdict:
`H1.interpretable = false`, with the difference test, ΔCFI and φ all withheld. An earlier version of
the script emitted `H1.supported = false`, which would have been read as H1 failing a sensitivity
check when nothing of the kind occurred. **No attempt was made to rescue the fit with different
starting values**, because searching for starting values that produce an interpretable verdict is
indistinguishable from searching for a verdict. H1 rests on the battery-inclusive specification.

### 2026-08-11 — reliability checks 4 and 5 run, after the confirmatory analysis

§7.2 items 4 and 5 had no code at all, although the manuscript described them as "pre-registered and
non-negotiable". Both are now run by `code/21_delphi_checks.py` → `delphi-checks-4-5.json` and
Supplement S8. **Both were elicited after the CFA**, which is disclosed at the point of reporting.
The Tier-2 gate does not apply: neither is a forecast of the analysis, so nothing here could have
leaked into it and nothing in it can flatter these. Independent draws throughout — one fresh context
per persona per round.

**Check 4, contamination.** Six real items and six fabricated in the same house style, written out
in the script so a reader can confirm they are fabrications. The panel attributes real provenance to
a fabrication in **19.4%** of judgements at a mean confidence of **.80**, while attributing the real
items correctly **88.9%** of the time. The rate is almost entirely one endpoint's — 83.3% for
`gpt-oss:120b`, zero for two others. Provenance judgement is recall for some endpoints and
confabulation for others.

**Check 5, sycophancy — the registered metric passes and should not reassure anyone.** Δ =
M_inverted − M_true = **+.011**, far below the registered .20 flag, so the check is **not flagged**
and is reported as not flagged. It is uninformative: both migration rates are at ceiling (93.5% true,
94.5% inverted), and a difference between two saturated rates cannot separate a panel that ignores
feedback from one that follows it absolutely. Mean displacement toward the number shown, which does
not saturate, is **0.47** scale points under true feedback and **2.62** under inverted, on a
nine-point scale. The panel is strongly sycophantic and the pre-registered test says it is not. Both
are reported, the registered one first. This is a defect in the registered statistic, and it is
listed for correction in the accumulated-revisions update.

---

## 12. Registration versions

| Version | Date | Change |
|---|---|---|
| 1 | 2026-08-10 07:45:39 UTC | Original registration. https://osf.io/ezjh2/, DOI `10.17605/OSF.IO/EZJH2` |
| 2 | **2026-08-10 07:56:12 UTC**, approved | Changed the foreknowledge **selection** from "Data does not yet exist" to **"Authors have observed the data, but have not performed the proposed analyses"** (option 6 of 8), and completed the previously empty "explanation of foreknowledge" field (3,141 characters). **Diff verified against the OSF API: exactly two keys changed, `344-4` and `344-14`.** No hypothesis, model, decision rule, inclusion criterion, threshold or analysis specification was altered. |

**Both versions are public and permanent.** Version 1 preserves the original registration timestamp
of 07:45:39 UTC — the reference point for "no analyses performed before registration" — and version 2
carries the correction eleven minutes later. The manuscript's pre-registration sentence and the cover
letter each state that the registration was updated to correct the foreknowledge field, with both
versions public; a disclosed correction reads as diligence, an undisclosed one as concealment.

**One cosmetic imprecision, deliberately left uncorrected.** The explanation field says "A prior
version of *this field* stated that the data did not yet exist"; strictly, that statement was in the
adjacent selection field, which was empty in `344-14` at version 1. The sentence is substantively
true and self-disclosing, the two fields sit under one heading, and the revision justification makes
the sequence explicit. **Do not file a version 3 for this** — each additional version adds noise to
the record for no gain in accuracy.

The foreknowledge field is a single-select, not free text. Option 6 is the accurate rung: its clause
"sufficiently observed relevant evidence to influence their analysis decisions" is **true** — the
Cyprus exclusion, the `0`-recode and the battery method factor all followed from inspection — so the
weaker option 5 ("could not influence") would itself be false, and options 7–8 either understate or
misdescribe. This is documented so the choice is not re-litigated later.

### What the filed registration contains, checked against this document 2026-08-10

Faithful and complete on all of: H1–H4 with their numerical decision rules; the commitment not to
respecify after an H1 failure; the model sequence M0–M4 with M2 as target; WLSMV with the ordinal
justification; the invariance chain and the **hard stop on country means without confirmed alignment
recovery**; the 20 % partial-invariance cap; fit thresholds; the three pre-registered decisions with
their sensitivity analyses; the Welzel-free D1 subset naming `E229`, `E233B`R, `H009`, `H010`, `H011`
and excluding `E233`; the H4 three-probe design; **the Tier-2 requirement that forecasts be elicited
and time-stamped before any CFA is run**; the pilot disclosed as pre-registration and excluded from
confirmatory evidence; software versions; and the anti-tuning commitments.

Fields left empty at filing, none of them load-bearing: "intention for causal interpretation",
"additional blinding during research or analysis", and four optional file-upload slots. The one
consequential empty field — "explanation of foreknowledge and managing unintended influences" — is
filled by Update #1.

### Known defects in the filed text — recorded on OSF by Update #2, filed 2026-09-09

> **UPDATE #2 IS FILED.** Submitted 2026-09-09 20:56:51 UTC and approved, in one revision covering
> all five, as recommended. **Only two were correctable.** Defects 4 and 5 live in the editable
> schema fields and were corrected there (`344-2` and `344-71` — both state the rules, so both were
> amended; changing one would have left the other standing). **Defects 1, 2 and 3 are in the
> `preregistration.md` file archived with the registration, and files archived with an OSF
> registration are immutable** — they cannot be corrected by a revision and are recorded in the
> revision justification instead, which is public. The corrections were *appended* to the fields
> rather than replacing them, so the registration still shows what was originally committed to.

**Five. Three were found on 2026-08-10, before the analysis each one touches; two were found on
2026-08-11, after the CFA had run**, and are marked as such below. All five are drafted as a single
revision in `docs/osf-registration-update-02.md` and deliberately **held**, on the reasoning
recorded there: one revision covering everything the analysis chain accumulates reads better than a
third piecemeal update filed a day after the second. Whether to file is the authors' decision, not
this document's; what is not optional is that all five are disclosed here and in the manuscript
whether or not OSF is updated before submission.

| # | Where | Defect | Material to the analysis? |
|---|---|---|---|
| 1 | §7.2 check 3 | Homogenisation check specifies a variance ratio against a **human comparison distribution that Decision 1 had already removed** before filing. Uncomputable as worded. | **Yes** — it is a registered reliability check. Executed with the deviation recorded in §11 and reported in the manuscript. |
| 2 | §2.1 | *OSE* two-axis passage cited as **ch. 6 §III**; it is **§V**. Page range 95–98 correct. | No — a locator error. |
| 3 | §2.1 | Citation edition given as the **"one-volume Routledge edition"**; it is the first single-volume **Princeton University Press** printing, 2013, ISBN 978-0-691-15813-6. | No — but see below. |

Defect 3 deserves a note. **A one-volume Routledge *OSE* genuinely exists**, so the wrong attribution
does not read as an error; a reader checking pp. 95–98 in that edition would find different text and
could reasonably infer the Popper anchors were invented. Every page anchor is nonetheless sound —
all were read from the Princeton PDF's own text layer, against which the printed-page = PDF-page − 47
offset was verified. Corrected in eleven repository files on 2026-08-10; the OSF text still carries it.

| 4 | §6.2 (H1) | **Found 2026-08-11, after the CFA.** The three-part conjunctive rule has only **two effective parts**: a two-factor model with φ fixed to 1 is equivalent to a one-factor model over the same indicators, so conditions (a) and (b) are one comparison expressed twice. Confirmed numerically — M1b and M0\_12 share df 464 and χ² to the second decimal. | **Touches a decision rule.** The rule was applied exactly as registered and the redundancy is reported rather than used; no verdict changes, since all three conditions hold and (c) is independent. |
| 5 | §6.2 (H2) | **Found 2026-08-11, after the CFA.** The magnitude condition is **one-sided** as worded — "φ(D1,D3) does not exceed .70" — so φ = −.99 would satisfy it while meaning D3 is D1 sign-reversed, which is the reducibility H2 denies. | **Touches a decision rule.** The signed rule is applied as registered and the absolute-value form reported beside it; they agree here (\|φ\| = .454), so no verdict changes. |

**Two of these five do touch a decision rule** — defects 4 and 5 — and an earlier version of this
section asserted that none did. That assertion was written when three were known and is withdrawn.
Neither defect changes a verdict: in both cases the registered rule was applied exactly as filed and
the diagnostic quantity reported next to it, so the correction is to the rule's *wording* and not to
any result. Both were found after the CFA had run, which is the worst time to find such a thing and
is stated plainly for that reason. What follows from the "file immediately" commitment is a
disclosure obligation, discharged here and in the manuscript; the timing of the OSF revision itself
is recorded in `docs/osf-registration-update-02.md` as a decision the authors take.

### 2026-09-09 — the ESS replication is run, and its item mapping is not registered

§4.2 registers "an independent replication of model structure, not of parameter values, for the
politics and morality spheres only" on ESS rounds 9 (ed. 3.3), 10 (ed. 3.3) and 11 (ed. 4.2). **It
names no ESS items.** The only ESS variables in the filed text are `ipcrtiva` and `impricha`, cited
as examples of round 11's `a` suffix. The mapping actually used is drawn from
`docs/design/measurement-design.md`, last modified 2026-08-10 10:50:43 UTC — *after* filing
(07:45:39) and after the analytic gate cleared (09:11:17).

**Consequence: the ESS analysis is reported as an unregistered replication, not as the registered
one.** Calling it registered would be a false claim about a document anyone can read.

What was done instead, being the strongest guarantee still available: the item selection was
fixed and hashed in `docs/design/ess-item-table-frozen.md` on 2026-09-08, **before any
ESS model was estimated**. **The word "timestamped" is deliberately not used.** The only timestamp
on that freeze is a local file mtime, and §7.1 of this document rules local mtimes out as evidence;
the OSF deposit of the file postdates the fits and therefore evidences its *content*, not the
sequence. What is independently checkable is the content freeze: the SHA-256 is pinned in
`code/29_build_ess_frame.py`, which refuses to build the frame on a mismatch, and in
`code/30_ess_replication.R`, which refuses to fit. The ordering claim rests on our own record and is
reported as such — unlike the Tier-2 forecast, whose ordering an independent registration
timestamps. `code/29_build_ess_frame.py` pins that file's SHA-256
(`94ae43fde2761dd9740957eb3fbca2963d89cf0d492b01e9fe8f4575b53ec5a1`) and refuses to build the frame
if it changes; `code/30_ess_replication.R` refuses to fit if the frame's metadata disagrees.

Selection was mechanical and stated in the frozen file before it was applied: politics and morality
spheres only (as registered), present in all three rounds (a cross-round replication cannot use a
single-round item), **no item added and none dropped for fit**. That leaves 20 items — D1 seven, D2
ten, D3 three — from the 27 the design document maps. Six of the seven dropped are ESS9-only
(`frprtpl`, `sofrpr`, `sofrwrk`, `sofrdst`, `gvintcz`, `poltran`); the seventh, `stfedu`, is
Education, which the registration excludes.

**Stated before fitting, and it holds after:** ESS D3 has exactly three indicators, all
institutional-trust items, and carries none of the anti-institutional-personalism content that
defines D3 in the primary model. It is a narrower construct, so a structural replication of it is
weak evidence about the paper's third dimension. Reported as a limitation, not smoothed over.

**Result** (`code/30`, `code/31` → `ess-replication.json`, `ess-admissibility.json`; manuscript
§5.6, Table 4). Both registered rules are met on the pooled file (137,246 respondents, 33 countries)
and within each round taken alone. The separation is much weaker than in the primary sample —
φ(D1,D2) = .767 against .298, and round 10 clears the registered .85 ceiling by .024 — so the
replication supports the *existence* of the crossing and says nothing in its favour about its size.
Cross-round metric invariance passes (ΔCFI +.0420) and scalar fails (−.0354), so the registered
conditional (report round 11 separately if metric fails) is not triggered. **The metric pass is
reported as a diagnostic and not a test**: its scaled χ² falls by 62,235 while df rise by 34, the
same rescaling pathology the D1 metric rungs show, and the manuscript applies the identical caveat
to both rather than downgrading one and not the other.

Admissibility was censused rather than assumed (`code/31`, written because three unattributed
`cov.lv` warnings are not a disclosable fact): of the six single-group models only M2b fails, and it
fails by construction, φ being fixed to 1. M1 and M2 are positive definite (smallest latent
eigenvalue .233 and .236, no negative residual variances), so the correlations read off them are
readable. The census covers the single-group fits; the multi-group fits are not covered by it and no
admissibility claim is made for them.

### 2026-08-11 — H3 is untestable here; H4 is estimable on two of three probes

Both were registered in §2.2 and neither appeared in the first complete manuscript. That was an
omission, not a decision, and it is corrected here and in the manuscript's §5.5 rather than left for
a reader comparing the two documents to find.

**H3a and H3b are not testable on this analysis.** Both compare country-level indices (Hofstede IDV,
Welzel emancipative values) with country-level D1 and D2 scores, and §6.3's hard stop licenses no
country score for any dimension. The registered ±0.20 equivalence bound and the Steiger comparison
are therefore left standing for a future licensed instrument. Computing them from unlicensed scores
would be the league table §6.3 forbids, arrived at by a different route. **No H3 statistic has been
computed**, and the Welzel-free D1 subset registered in §6.4 was never constructed.

**H4 is estimable on probes 1 and 2 and not on probe 3.** Probe 3 pairs `D026_05` with `A080_01` —
**one indicator per pole**. A two-factor model on two indicators is not identified at any sample
size, so the registered "two-factor versus one-factor comparison within each probe" has no referent
there. This is a defect in the registered design, visible on its face at the time of filing, and it
has a consequence for the decision rule: the prediction reads "for at least two of the three
probes", and since only two are estimable the rule cannot be satisfied on its own terms whatever the
data show. Reported as a count of separable probes among the estimable ones instead.

Run by `code/19_h4_frame.py` and `code/20_h4_test.R` → `h4-jellyby-primary.json`. H4 needed eight
indicators absent from the PII frame; a **separate** frame was built rather than rebuilding
`pii-frame-primary.csv`, whose SHA-256 the manuscript publishes and whose rebuild would invalidate a
checksum for a reason unrelated to the confirmatory models. Same source file, same missing codes,
same 39 countries, same 77,396 rows — asserted in the script, not assumed.

| Probe | φ(concrete, anonymous) | one-factor rejected | ΔCFI | separable |
|---|---|---|---|---|
| Whom you trust | +.600 | yes (p < .001) | +.0202 | yes |
| Whom you feel close to | +.334 | yes (p < .001) | +.1177 | yes |
| Whom you act for | — | not estimable | — | — |

Decision rules were fixed in the script before the fits, in the registration's own language for
comparable tests: separable iff the one-factor model is rejected at α = .01 **and** φ ≤ .85;
incremental iff a model constraining each pole to relate identically to D1 and D2 is rejected at
α = .01. As registered, **a null on H4 threatens nothing else in the paper** and no licence rests
on it.

### 2026-08-11 — the missing cell: the unidimensional D1 ladder on the subset

An earlier version of §5.5 reported two invariance diagnostics that disagreed and conceded the
disagreement was **confounded**: they differed in specification (three-factor vs unidimensional D1)
*and* in sample (12 countries vs 39), and the registered test that would have separated them was the
one not estimable on this hardware. That concession is now unnecessary.

`code/22_perdim_step_fit.R` fits the **unidimensional D1 model on the same seeded twelve countries**
the subset ladder used — AL, AZ, BY, ES, GB, GR, HU, MK, RO, RU, SK, UA, the identical
`set.seed(20260810)` draw, the identical category collapsing computed over all 39 qualifying
countries and only then subsetted. Sample fixed, specification varied. It completed in about two
minutes per step, which is the cost of asking a 2×2 question with one cell missing rather than
guessing at it.

| Specification | Countries | configural→metric | metric→scalar |
|---|---|---|---|
| Three-factor M2 | 12 | ΔCFI −.0220 · fails | ΔCFI −.0230 · fails |
| Unidimensional D1 | **12** | **ΔCFI +.0324 · holds** | **ΔCFI −.0468 · fails** |
| Unidimensional D1 | **39** | ΔCFI +.0238 · holds | **ΔCFI −.0530 · fails** (entry below) |

**The disagreement is specification, not sample.** D1's loadings are common across countries; the
three dimensions' jointly are not. This converges with `code/12`'s per-country loading diagnostic
(9.1% residual sign disagreement on D1 against 29.9% on D2) from an independent direction.

**Scalar invariance fails for D1 alone**, and this is the more consequential half. The registered
licence already rested on alignment, which is negative for every dimension; it now also has a
properly-behaved nested test behind it. Two caveats are reported rather than smoothed. First, the
indices disagree at that rung — ΔRMSEA is **−.0143**, an improvement — so the verdict rests on ΔCFI,
as it does at every other rung in the paper. Second, the χ²/df movement distinguishes the two rungs:
the metric step's scaled χ² *falls* while df rise (−7,088 on +187 df at twelve countries, −13,878 on
+646 at 39), which no unscaled statistic can do on nested models, while the scalar step behaves
normally (+11,260 on +759 df). The "metric holds" finding is therefore a diagnostic and the "scalar
fails" finding is a test, and the manuscript says so.

**Still unregistered.** These are unidimensional models on a subset; none is the registered
three-factor ladder over the analysis sample, and none carries any part of the licensing decision.
Output: `perdim-subset-measures-primary.json`.

### 2026-08-11 — a Heywood case in the D2 per-dimension configural model, and a check added so the next one cannot hide

The unidimensional **D2** configural model over all 39 countries converged (CFI .7845) but its
solution is **inadmissible in one group**: Portugal has a negative estimated residual variance on
`A080_02` / **D2-A2, "Member: self-help / mutual-aid group"** (θ = −0.4195), because that item's
standardised loading in Portugal is **−1.191** while across the other 38 groups it runs as high as
+0.814. One group of 39; no other dimension shows it — D1's three rungs are clean.

**This does not license dropping the item.** The registered rule permits a drop for a Heywood case
*in the registered configural model*, which is the three-factor M2, not a unidimensional
per-dimension model that is itself an unregistered diagnostic. The item stays; the inadmissibility
is reported alongside D2's fit statistics, because those statistics are computed from this solution.

**It also is not a surprise.** An item whose loading is strongly positive in 38 countries and −1.19
in the thirty-ninth is another instance of the cross-country loading instability the paper already
reports for D2 — the worst of the three dimensions on `code/12`'s per-country diagnostic (29.9%
residual sign disagreement against 9.1% for D1). It converges with that result from a second
direction.

**How it was found is the part worth fixing.** lavaan reports this through
`lav_object_post_check()`, which prints among the deferred warnings at the end of a run, and it was
caught only by reading a journal tail by eye. `code/22` now computes the negative-variance census
itself and writes `heywood_negative_var` and `heywood_cases` (country, variable, θ) into the output
JSON for every step, so admissibility sits beside the fit statistics instead of in a log. The change
is purely additive — it records, drops nothing, and alters no estimate — and took effect from the D2
scalar step onward. ~~**Outstanding:** D1's three steps and D2 configural/metric predate it and must be
backfilled from their cached fits once the machine is free; until then the absence of the field in
those entries means "not checked mechanically", not "clean". D1 is known clean from its logs.~~
**Closed 2026-08-15** — all five were backfilled by `code/24_heywood_backfill.R`; see the entry of
that date. Every rung of every per-dimension ladder now carries a census, and only this one is
positive.

**Completed 2026-09-08.** The 2026-08-15 closure was narrower than its wording: it covered the nine
39-country rungs, leaving the six **twelve-country** rungs — the three-factor M2 ladder and D1 alone
— uncensused, including the ladder the −.0220 metric failure is drawn from. `code/24` could not reach
them; it hardcodes `perdim-step-measures-<variant>.json` and the `pd<D>-<step>` cache name, while
those rungs live in `perdim-subset-measures-primary.json` and `cfa-primary-ladder.json` under two
other shapes. `code/27_heywood_backfill_k12.R` reaches both with `24`'s guards intact and a census
copied from it verbatim: read-only via `lavInspect(fit, "est")`, refuses to create a record, refuses
to overwrite an existing census. **All six are clean.** Fit statistics were re-checked after the
write and are unchanged (M2@12 scalar CFI .5024, D1@12 metric CFI .6676).

**All fifteen rungs are now censused, and exactly one negative residual variance exists in the whole
set** — Portugal, `A080_02`, θ = −.4195, in D2 configural at 39 countries. The Table 3 footnote,
which previously asserted this without having checked the twelve-country rungs, now states the scope
it has: "a mechanical census … across all fifteen rungs returns none at any other".

**How far the caveat reaches, now that D2's ladder is complete.** The warning appears exactly once in
the whole D2 chain, and it appears inside the **configural** block. D2 metric emits no such warning,
and D2 scalar was checked mechanically and returns `heywood_negative_var = 0`. The two rungs are
therefore not equally affected:

| D2 rung | ΔCFI | ΔRMSEA | Δχ² (scaled) | Δdf | Admissibility of the pair |
|---|---|---|---|---|---|
| configural → metric | **−.0491** | +.0026 | +13,097.1 | +494 | baseline inadmissible in 1 of 39 groups |
| metric → scalar | **−.0338** | −.0119 | +10,247.6 | +1,596 | **both solutions admissible** |

The caveat cuts in a specific direction and it is the unhelpful one: a Heywood case lets the
configural model fit better than a proper solution would, which inflates the apparent degradation
when loadings are then constrained. So −.0491 is, on its own, not a number to lean on. **But the
metric → scalar rung is a comparison between two admissible solutions, and it fails independently
at −.0338.** D2's non-invariance therefore does not depend on the inadmissible group, and the paper
will say so rather than resting the claim on the contaminated rung. A refit of D2 configural under
non-negative residual-variance bounds would quantify the first rung directly; it is queued behind
the registered ladder and will be reported if it is run, and its absence disclosed if it is not.

### 2026-08-11 — the D1 scalar step at 39 countries, previously reported as not estimable, completed

The entry of 2026-08-10 recorded that the per-dimension chain had been **abandoned after three OOM
kills**, all on the D1 scalar step, and that it was "not estimable on this hardware". **That is no
longer true and the earlier entry is left standing as written, with this correction appended rather
than substituted for it.**

What changed was the machine, not the model. `systemd-oomd` kills on a PSI memory-pressure stall
rather than on exhaustion, so it was terminating a job that had memory left to use. With the daemon
stopped, `vm.swappiness` at 100 and 32 GB of swap available, `code/22_perdim_step_fit.R --dim D1
--step scalar --countries 39` ran to completion on 2026-08-11: **132 minutes to fit, 91 minutes to
extract fit measures, 2 h 51 min of CPU in all**, peaking near 9.4 GB resident with 19 GB in swap.
The fit object is 332 MB on disk — 6.8× the metric step's 49 MB, which is the threshold structure
across 39 groups and the reason this step alone defeated the earlier attempts.

| Rung | χ²(scaled) | df | CFI | RMSEA | TLI |
|---|---|---|---|---|---|
| configural | 206,832.38 | 5,265 | .6694 | .1390 | .6253 |
| metric | 192,954.32 | 5,911 | .6932 | .1263 | .6903 |
| **scalar** | **227,930.75** | **8,533** | **.6402** | **.1139** | **.7484** |

**Metric → scalar: ΔCFI = −.0530**, more than five times the registered threshold, on a
properly-behaved nested comparison — χ² rises by 34,976.43 on 2,622 df, the direction nesting
requires, unlike the metric rung and unlike M1b in the battery-excluded sensitivity. Converged.

Two things are reported rather than smoothed. First, **RMSEA and TLI both improve at the rung where
CFI collapses** (−.0124 and +.0581): both scale misfit by degrees of freedom, so 2,622 new
constraints flatter them, while CFI's numerator takes the raw χ² increase. The registered criterion
is a conjunction — ΔCFI ≤ .010 *and* ΔRMSEA ≤ .015 — so it fails on the CFI limb whatever RMSEA
does, exactly as it would have had the signs been reversed. Second, an internal check: the CFI and
TLI pairs at the two rungs imply an identical baseline (χ²_b − df_b = 609,658 reproduces .6402 from
.6932), confirming the rungs are scored against the same reference.

**One provenance check, because this rung was fitted by a different script from the two below it.**
Configural and metric came from `code/06 --stage perdim`, scalar from `code/22`, and a nested
comparison across two data preparations would not be a nested comparison. The two scripts turned out
to differ: `code/06` applies the category-collapsing rule over **every** country in the frame and
filters to ≥200 respondents afterwards, while `code/22` filtered first. On this frame the
distinction is empty — all 39 countries clear 200, so both scopes see the same rows, and both return
**7 items collapsed, 14 merges, identical category sets for every item** (checked 2026-08-11 by
re-running each rule on the frame). ΔCFI −.0530 therefore compares fits on identical data.
`code/22` has been corrected to `code/06`'s scope regardless, since the equivalence is a property of
this frame rather than of the code.

**Still unregistered, and it resolves nothing in Tier 2.** This is a unidimensional D1 model. The
registered three-factor M2 ladder remains unfitted, so the forecast propositions `C-METRIC` and
`C-SCALAR` stay unresolved — see §7.1's scoring table, where the reason given for `C-SCALAR` is
corrected accordingly. Resolving `C-SCALAR` against this model would *raise* the panel's Brier skill
score, since it forecast .108 that scalar invariance would hold; that is a reason for more caution,
not less. Output: `perdim-step-measures-primary.json`.

### 2026-08-15 — the D3 ladder completes the per-dimension set, the admissibility census is backfilled, and the registered 39-country ladder is attempted and defeated by memory

Three things closed on the same day. They are recorded together because the third is the one that
constrains what the paper may claim, and it is the one that failed.

**1. D3 at 39 countries, and with it all three per-dimension ladders.** `code/22` completed the D3
chain on 2026-08-12; measure extraction alone took 65, 63 and 90 minutes for the three rungs, which
is why they are extracted one per process.

| D3 rung | χ²(scaled) | df | CFI | RMSEA | TLI | admissible |
|---|---|---|---|---|---|---|
| configural | 253,061.41 | 6,630 | .6536 | .1370 | .6129 | yes |
| metric | 263,935.88 | 7,352 | .6394 | .1327 | .6365 | yes |
| **scalar** | **304,965.56** | **9,138** | **.5842** | **.1278** | **.6628** | yes |

Both rungs fail. **configural → metric: ΔCFI = −.0142** (ΔRMSEA −.0043, Δχ² +10,874.47 on +722 df)
— a failure, but a marginal one, and the only rung anywhere in this study that fails by less than
twice the threshold. **metric → scalar: ΔCFI = −.0552** (ΔRMSEA −.0049, Δχ² +41,029.69 on +1,786
df). Both are properly-behaved nested comparisons: χ² rises in both cases, unlike D1's metric rung.
Since the registered criterion is the conjunction ΔCFI ≤ .010 *and* ΔRMSEA ≤ .015, D3's improving
RMSEA does not rescue either rung, exactly as D1's improving RMSEA did not rescue its scalar rung.

The per-dimension set is now complete, and it points one way. Of ten rungs across five ladders,
**eight fail**; the two that pass are the same rung twice — D1 configural → metric, at 39 countries
and at 12 — and that is the rung whose scaled χ² *falls* while its df rise. Every rung with a
well-behaved test statistic fails.

**2. The admissibility census is backfilled, and the D2 caveat is now bounded by measurement rather
than by inference.** `code/24_heywood_backfill.R` reads a cached fit, runs the same negative-variance
census as `code/22`, and writes only `heywood_negative_var` / `heywood_cases` into the existing JSON
entry. It refuses to create a record, refuses to overwrite an existing census, and cannot alter a fit
statistic — `lavInspect(fit, "est")` reads the stored parameter table and re-estimates nothing. Each
backfilled entry is stamped `heywood_backfilled`, so a reader can tell which censuses were taken at
fit time and which afterwards. Run on all five outstanding rungs on 2026-08-15:

| Rung | negative residual variances |
|---|---|
| D1 configural / metric / scalar | 0 / 0 / 0 |
| D2 configural | **1** — Portugal, `A080_02`, θ = −0.420 |
| D2 metric | 0 |

The single positive result reproduces the by-eye finding of 2026-08-11 exactly, including the value
of θ. **All nine rungs of the three 39-country ladders now carry a mechanical census, and exactly one
is positive.** The caveat entered above therefore stands at its narrowest: it touches D2's configural
rung and nothing else in the study.

**3. The registered ladder was attempted at 39 countries and cannot be computed on this hardware.**
This is the substantive loss and it is reported as one.

`code/23_registered_ladder_step.R` was written for exactly this attempt: one rung per process, the
fit written to disk before any measure is taken, and a cache key byte-identical to `code/06`'s. Its
validation gate ran first and **passed at exactly cfi.scaled = 0.5475** on the 12-country configural
rung — the published value — establishing that its data preparation is at parity with `code/06` and
that a completed 39-country rung could have been trusted.

The 39-country configural rung then ran for **2 h 36 min 28 s of CPU** and was killed. The kernel log
of the boot in question (recovered with `journalctl -k -b -1`) records it unambiguously:

```
oom-kill:constraint=CONSTRAINT_NONE,…,global_oom,task_memcg=…/paper69-m2ladder.service,task=R,pid=637483
Out of memory: Killed process 637483 (R) total-vm:42654152kB, anon-rss:13326808kB, …
Free swap  = 0kB
Total swap = 33554428kB
Node 0 … all_unreclaimable? yes
```

**This is genuine exhaustion, and the distinction drawn on 2026-08-11 does not apply.** That entry
corrected a misdiagnosis: three earlier kills had been attributed to the model when they were
`systemd-oomd` acting on a PSI memory-pressure stall with memory still to spare. Here `systemd-oomd`
was inactive and `ManagedOOMMemoryPressure=auto` was in force on `user@1001.service`, so it took no
part; the kill came from the kernel, with **free swap at zero**, 15 GB of RAM and 32 GB of swap
consumed together, and reclaim reporting `all_unreclaimable`. Enlarging swap is not available either:
the volume is at 97 % with 14 GB free. The arithmetic is as `code/23`'s header predicted — a model
Jacobian of order (39 × 1,479) × 10,062 doubles, ≈ 4.6 GB per copy, several copies deep — and it
simply exceeds 47 GB of RAM and swap combined.

**What this does and does not license.** It does not license inferring anything about the registered
model from the ladders that did run: the four reported ladders are unregistered substitutes, and
three of them are unidimensional models that are not the registered specification. The manuscript
states in §5.5 that *we do not know what the registered ladder would have shown*. It does not change
the country-comparison licence, which already rested on alignment and was already refused. And it
does not resolve `C-METRIC` or `C-SCALAR` in the Tier-2 scoring table: those propositions are worded
"across the 39 countries" against the registered model, they remain unresolved, and — as recorded at
§7.1 — excluding them most likely *helps* the panel rather than the authors, since the panel gave
scalar invariance .108 and would have been right about it.

The earlier entry of 2026-08-10, which recorded the pooled chain as "attempted and not estimable at
39 groups on the available hardware", is left standing as written. This entry sharpens it: the claim
is no longer an inference from three ambiguous kills but a measurement, with the kernel's own
accounting attached.

### 2026-08-15 — the promised bounded refit of D2 configural: attempted, and why it is not reported

The entry of 2026-08-11 promised that "a refit of D2 configural under non-negative residual-variance
bounds would quantify the first rung directly; it is queued behind the registered ladder and will be
reported if it is run, and its absence disclosed if it is not." **It was attempted. It is not
reported, and the reason is more informative than the promise anticipated.**

`code/22` gained a `--bounds` flag for this purpose. It is deliberately quarantined: a bounded run
writes to `perdim-bounded-measures-<variant>.json` with its own cache suffix and its own step key, so
it cannot overwrite, be merged into, or be mistaken for the primary record. A delta is only
meaningful between two rungs fitted under the *same* bounds, which is why both configural and metric
would have to be refitted, not just the contaminated one.

**First finding: lavaan's variance bounds do not bind for a delta-parameterised ordinal model.**
`bounds = "pos.var"`, `"pos.ov.var"` and `"wide"` all left the SMOKE D2 configural fit *identical* —
`cfi.scaled = 0.7011` to four decimals in every case — and the negative residual variance survived
each of them. This is not a bug. Under the delta parameterisation lavaan uses for `ordered`
indicators, the total variance is fixed at 1 and the residual variance is *derived* as 1 − λ², so
there is no free θ parameter for a variance bound to act on. A "negative residual variance" here is a
standardised loading whose magnitude exceeds 1, and the constraint has to reach the loading.

**Second finding: `bounds = "standard"` does bind, it is free at the configural rung, and it does not
converge at the metric rung.** The bound is the one that reaches the loading, and at configural it
does exactly what it should: on the SMOKE frame it cleared the admissibility warning outright — zero
negative residual variances against one (UA, `A071`, θ = −0.025) under each of `pos.var`, `wide` and
`pos.ov.var` — at a cost of 0.0003 in fit (`cfi.scaled` 0.7011 → 0.7014), and it did so in under a
minute, the same as the unbounded fit. The failure is specific to the **metric** rung, where the
cross-group loading-equality constraints meet the box constraints.

That rung was attempted twice. The first attempt (17 minutes of CPU, no convergence, stopped by us)
ran alongside other jobs on this machine, so it was **retried on an idle machine** — load average
1.42 of which the fit itself was 1.00, 9 GB of RAM free, 30 GB of free swap, the process holding
99.9% of one core at a 200 MB resident footprint throughout, never touching swap. It ran for
**1 h 32 min of CPU without converging** and was stopped at a cap set in advance at 92 minutes,
chosen because that is more CPU than the most expensive *unbounded* rung anywhere in the
per-dimension table ever required (D1 scalar, 91.3 minutes at 39 countries). It did not crash and was
not killed by the kernel; it never left `lavaan`'s fitting call. Resource contention is therefore
excluded as the explanation, and the cost is not marginal: the unbounded D2 metric rung converges in
**0.3 minutes at 39 countries and 77,396 rows**, while the bounded rung fails to converge in 92
minutes at 12 countries and 3,043 rows — a factor above 180 in the wrong direction on problem size.
Since a delta requires both rungs under the same bounds, and the cheaper of the two rungs is the one
that will not finish on the smaller frame, there is no assurance the 39-country frame would finish at
all, and no basis for spending the time to find out.

**Why nothing is lost.** The bounded refit would have quantified D2's configural → metric rung, which
the paper already declines to lean on. The claim actually made — that D2's non-invariance does not
depend on the inadmissible group — rests on the metric → scalar rung, a comparison between two
solutions both of which the mechanical census confirms admissible, failing independently at −.0338.
The bounded refit would have been a bonus, not a support.

What is reported instead is this entry, and the manuscript's §5.5 statement of exactly how far the
caveat reaches. The `--bounds` flag stays in `code/22` and in the supplement, and the four bounded
configural runs it produced are reported in full in `analysis/perdim-bounded-measures-SMOKE.json` —
fit indices and negative-variance census for each of the four bound settings — so that a reader can
reproduce the inertness of the variance-only bounds directly. The metric rung appears in no results
file, because it never returned a fit to write; its non-convergence is recorded here and nowhere
else, which is the reason this entry states the elapsed CPU and the stopping rule rather than a
number. With a better optimiser, or more patience than we had, a reader can run what we could not.
The obstacle at that rung is convergence, not hardware: 200 MB of memory is not a resource this
machine lacked.
