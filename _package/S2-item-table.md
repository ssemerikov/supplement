# Item table v2 — integrated EVS/WVS names

**2026-08-10.** This supersedes the item table in `measurement-design.md` §5, whose WVS7 `Q`-numbers do
not exist in `ZA7505_v5-0-0.dta` and return nothing on lookup. Every name below was read out of the
file; every validity figure was computed on the **40-country European sample (n = 78,396)** as the
proportion of rows with a value **≥ 0** (EVS/WVS encode missingness as −1 … −5; `notna()` returns 100 %
on every item and is wrong).

Mapping authority: `ZA7505_VariableCorrespondence.xlsx`, sheet `EVS_WVS_Variable_Correspondence`
(230 mapped variables), cross-checked against the `.dta` metadata.

Status codes: **[OK]** present and verified · **[LOST]** in the design, absent from the joint core ·
**[NEW]** not in the original design, found in this pass.

---

## 0. The three structural facts that govern everything below

**0.1 The joint core is an *intersection*, and that is why things are missing.** The 231 variables are
those with both an EVS5 and a WVS7 counterpart. Items the design wanted that were WVS-only (the
science block, `Q291`) are absent for that reason, not by oversight. The compensation is large:
**89 of the 91 candidate items are fielded in all 40 European countries.** The two exceptions are
`E069_02` (confidence in armed forces — not asked in Andorra or Iceland, neither of which has an army)
and `E012` (willingness to fight — not asked in Northern Ireland, and not asked of 59 % of the GB
sample either, which is a second reason to leave it out).

**0.2 Four countries have planned missingness on the democracy battery. It is MCAR by design.**
The joint file distinguishes missingness reasons: `−1` don't know, `−2` no answer, `−3` not
applicable, `−4` **not asked in survey**, `−5` other (`ZA7505_v5-0-0_missing.do`). Seven European
countries ran an EVS5 matrix design (CH, DE, DK, FI, IS, LV, NL); four of them drop part of the
democracy battery by design, coded `−4`:

| | share coded `−4` on `E224`–`E233B` | also on `E265_*` |
|---|---|---|
| DK | 49.6 % | yes, 49.6 % |
| NL | 37.8 % | no |
| FI | 11.9 % | no |
| IS | 3.1 % | no |

For Denmark the crosstab is exact: of 1,666 respondents in matrix group 7, **1,666 are missing
`E229`**; of 1,696 outside the matrix, 1,667 have it. This is planned, MCAR by construction, and
handled correctly by FIML or multiple imputation. It is **not** a reason to drop the items or the
countries — but reporting these items as "89 % valid" without the explanation invites a referee to
think the data are damaged. CH and DE have **no** `−4` at all; their matrix blocks fall elsewhere.
Latvia's lower figures are not matrix design either — they are a high don't-know rate (`−1` on 14 %
of `E229`), which is informative missingness, not planned.

**0.3 Cyprus is a genuine problem and needs a pre-registered decision — for two different reasons.**
CY is *not* in the EVS5 matrix group, yet it is the worst country on two separate blocks, and the
reason codes show these are unrelated failures:

- **The child-qualities battery is a coding artefact.** `A042` obedience 54 %, `A029` independence
  62 %, `A041` unselfishness 70 %. The missingness is `−1` "don't know" — 322 of 1,000 cases on
  `A029`, 403 on `A042` — against a European average don't-know rate of **0.8 %** on the same items.
  On a binary mentioned/not-mentioned card sort, a 32–40 % don't-know rate is not a respondent
  phenomenon; non-mention appears to have been recorded as don't-know. **These values are not
  missing-at-random and should not be imputed.**
- **The two army items are a split ballot in all but name.** `E116` army rule 46 %, `E228` army takes
  over 45 %, with **exactly 500 of 1,000 cases coded `−5` "Other"** on each. Exactly half the sample
  is a design, not an accident; the joint file simply files it under "Other" rather than "not asked".

**Recommendation: exclude CY from the primary model**, pre-registered, with a sensitivity analysis
including it. Do not decide this after seeing fits.

---

## 1. D1 — individualism ↔ collectivism

| ID | Sphere | Joint name | was | Label | Key | Valid % |
|---|---|---|---|---|---|---|
| D1-P1 | Politics | **`E229`** | Q246 | Democracy: civil rights protect people's liberty against oppression | + | 89.4 † |
| D1-P2 | Politics | **`E233`** | Q249 | Democracy: women have the same rights as men | + | 92.7 † |
| D1-P3 | Politics | **`E233B`** | Q248 | Democracy: people obey their rulers | **R** | 90.3 † |
| D1-P4 | Politics | **`H009`** | — | Government has the right: video surveillance in public areas | + **[NEW]** | 97.1 |
| D1-P5 | Politics | **`H010`** | — | Government has the right: monitor all e-mails | + **[NEW]** | 95.7 |
| D1-P6 | Politics | **`H011`** | — | Government has the right: collect information on anyone | + **[NEW]** | 96.4 |
| D1-E1 | Education | **`A029`** | Q8 | Child qualities: independence | + | 98.3 |
| D1-E2 | Education | **`A034`** | Q11 | Child qualities: imagination | + | 97.7 |
| D1-E3 | Education | **`A042`** | Q17 | Child qualities: obedience | **R** | 97.6 |
| D1-E4 | Education | **`A027`** | Q7 | Child qualities: good manners | **R** | 98.9 |
| D1-E5 | Education | **`D060`** | Q30 | University more important for a boy than a girl | **R** | 97.8 |
| D1-M1 | Morality | **`F118`** | Q182 | Justifiable: homosexuality | + | 95.3 |
| D1-M2 | Morality | **`F120`** | Q184 | Justifiable: abortion | + | 96.1 |
| D1-M3 | Morality | **`F121`** | Q185 | Justifiable: divorce | + | 97.1 |
| D1-M4 | Morality | **`F122`** | Q188 | Justifiable: euthanasia | + | 94.2 |
| D1-M5 | Morality | **`F132`** | — | Justifiable: having casual sex | + **[NEW]** | 95.5 |
| D1-M6 | Morality | **`F123`** | — | Justifiable: suicide | + **[NEW]** | 95.0 |
| D1-M7 | Morality | **`A173`** | — | How much freedom of choice and control (1–10) | + **[NEW]** | 98.4 |

† Planned `−4` missingness in DK/NL/FI/IS — see §0.2.

**[LOST] from the design:** `Q253` (respect for human rights in this country), `Q186` (sex before
marriage). `Q186` is adequately replaced by `F132`; `Q253` has no equivalent — it was flagged in the
design as a systemic-perception item for country level only, so the loss is small.

**`H009`–`H011` are the substantive gain here.** The design's D1-politics rested entirely on the
"essential characteristics of democracy" battery. These three ask whether the state *may* surveil the
individual — the rights-of-individuals-against-the-state reading, applied rather than abstract, and
on a different response format, which is exactly what §2 below says is needed.

---

## 2. D2 — altruism ↔ egoism

| ID | Sphere | Joint name | was | Label | Key | Valid % |
|---|---|---|---|---|---|---|
| D2-E1 | Education | **`A041`** | Q16 | Child qualities: **unselfishness** | + | 97.8 |
| D2-E2 | Education | **`A035`** | Q12 | Child qualities: tolerance and respect for others | + | 98.5 |
| D2-E3 | Education | **`A038`** | Q13 | Child qualities: thrift | **R**, marginal | 98.1 |
| D2-M1 | Morality | **`F114A`** | Q177 | Justifiable: claiming benefits you are not entitled to | **R** | 97.7 |
| D2-M2 | Morality | **`F115`** | Q178 | Justifiable: avoiding a fare on public transport | **R** | 98.3 |
| D2-M3 | Morality | **`F116`** | Q180 | Justifiable: cheating on taxes | **R** | 98.2 |
| D2-M4 | Morality | **`F117`** | Q181 | Justifiable: accepting a bribe | **R** | 98.5 |
| D2-A1 | Behaviour | **`A080_01`** | — | Member: humanitarian or charitable organisation | + **[NEW]** | 98.1 |
| D2-A2 | Behaviour | **`A080_02`** | — | Member: self-help / mutual-aid group | + **[NEW]** | 97.9 |
| D2-A3 | Behaviour | **`A071`** | — | Member: conservation / environment / animal rights | + **[NEW]** | 98.1 |
| D2-C1 | Concrete | **`D026_05`** | — | It is a child's duty to care for an ill parent | + **[NEW]** | 98.7 |
| D2-C2 | Concrete | **`D026_03`** | — | Duty towards society to have children | **R** **[NEW]** | 98.2 |
| D2-X1 | Politics | **`E224`** | Q241 | Democracy: governments tax the rich and subsidise the poor | + (confounded) | 90.3 † |
| D2-X2 | Politics | **`E233A`** | — | Democracy: the state makes people's incomes equal | + (confounded) **[NEW]** | 90.3 † |

† Planned `−4` missingness in DK/NL/FI/IS — see §0.2.

**[LOST]:** `Q179` (justifiable: stealing property). The design already predicted a floor effect for
it, so the loss costs little.

**D2 was the thin dimension and it is now materially less thin.** The design had two usable
education items plus the justifiability block. `A080_01` and `A080_02` add *behavioural* altruism on a
different response format, which breaks the common-method dependence that would otherwise make D2 a
single-battery artefact.

**The Jellyby operationalisation is stronger than the audit claimed.** `A080_01` is membership of an
organisation serving **anonymous, distant beneficiaries**; `D026_05` is obligation to a **concrete,
particular** person. Popper's Mrs Jellyby is precisely someone high on the first and low on the
second. That contrast is a direct test, and it does not depend on the trust-radius block — which
measures *whom you trust*, not *whom you act for*. Use both; they are independent probes of the same
prediction. See §5.

`E224`/`E233A` remain redistribution-preference items and carry the left–right confound the design
already identified. Keep them as discriminant checks, not as D2 markers.

---

## 3. D3 — institutional respect ↔ anti-institutional personalism

| ID | Sphere | Joint name | was | Label | Key | Valid % |
|---|---|---|---|---|---|---|
| D3-P1 | Politics | **`E114`** | Q235 | Political system: having a strong leader | **R** | 92.5 |
| D3-P2 | Politics | **`E116`** | Q237 | Political system: having the army rule | **R** | 92.1 |
| D3-P3 | Politics | **`E115`** | Q236 | Political system: experts, not government, decide | **R** | 90.6 |
| D3-P4 | Politics | **`E117`** | Q238 | Political system: having a democratic political system | + | 93.9 |
| D3-P5 | Politics | **`E228`** | — | Democracy: the army takes over when government is incompetent | **R** **[NEW]** | 87.7 † |
| D3-P6 | Politics | **`E225`** | — | Democracy: religious authorities interpret the laws | **R** **[NEW]** | 88.2 † |
| D3-P7 | Politics | **`E226`** | — | Democracy: people choose their leaders in free elections | + **[NEW]** | 91.9 † |
| D3-P8 | Politics | **`E235`** | — | Importance of democracy (1–10) | + **[NEW]** | 97.5 |
| D3-P9 | Politics | **`E018`** | — | Future change: greater respect for authority | **R**, 3-pt **[NEW]** | 93.2 |
| D3-Q1 | Performance | **`E265_01`** | — | Elections: votes are counted fairly | + **[NEW]** | 88.4 |
| D3-Q2 | Performance | **`E265_05`** | — | Elections: journalists provide fair coverage | + **[NEW]** | 87.4 |
| D3-Q3 | Performance | **`E265_06`** | — | Elections: election officials are fair | + **[NEW]** | 85.6 |
| D3-Q4 | Performance | **`E265_03`** | — | Elections: TV news favours the governing party | **R** **[NEW]** | 86.2 |
| D3-C1 | Confidence | **`E069_07`** | Q73 | Confidence: parliament | + | 96.1 |
| D3-C2 | Confidence | **`E069_11`** | — | Confidence: the government | + | 96.7 |
| D3-C3 | Confidence | **`E069_17`** | — | Confidence: justice system / courts | + | 95.8 |
| D3-C4 | Confidence | **`E069_06`** | Q69 | Confidence: the police | + | 98.2 |
| D3-C5 | Confidence | **`E069_08`** | — | Confidence: the civil services | + | 95.9 |
| D3-M1 | Morality | **`F117`** | Q181 | Justifiable: accepting a bribe | **R** | 98.5 |
| D3-M2 | Morality | **`E290`** | — | Justifiable: political violence | **R** **[NEW]** | 96.7 |

† Planned `−4` missingness in DK/NL/FI/IS — see §0.2.

**[LOST]:** `Q291` P3/G3/P6 (parliament/government "usually acts in the interest of citizens";
parliament's work is open and transparent) and `Q75` (confidence in universities). Both confirmed
absent by exhaustive label search.

### Correction to the data audit's conclusion on the D3 positive pole

`data-audit-2026-08-10.md` §1.2 concluded that with `Q291` gone the positive pole "must be carried by
the confidence battery", which measures trust rather than Popper's conditional commitment. **That was
too pessimistic, and it was my error** — it came from searching for the phrases `"interest of"` and
`"acts in"` rather than reading the variable list. Three better options exist:

- **`E235` importance of democracy** and **`E226`** free elections as an essential characteristic are
  *normative endorsements of an institutional arrangement*, which is nearer to Popper's "devotion to
  institutions" than any confidence rating.
- **The `E265_*` election-integrity block** asks whether institutions *actually perform their
  function* — votes counted fairly, officials fair, coverage fair. That is the antecedent of Popper's
  proviso ("provided that the humanitarian aims of these institutions are not lost sight of"),
  measured directly, on all 40 countries.
- **`E228`** is the conditional anti-institutional item — the army takes over *when government is
  incompetent* — and pairs with `E114`/`E116` to give the negative pole a graded structure rather than
  a single marker.

The positive pole is weaker than `Q291` would have made it, because none of these is the proviso in
one item. It is not the bare confidence battery. The manuscript should say this precisely: **D3's
negative pole is directly measured and its positive pole is assembled**, which is an asymmetry worth
stating rather than hiding.

---

## 4. Two traps in the response scales

**4.1 The `0` category in the democracy battery is not a scale point.** `E224`–`E233B` are scored
0–10, but **`0` = "It is against democracy (spontaneous)"** — a volunteered response, not one below
"not an essential characteristic" (`1`). Treating it as a continuum point is a substantive coding
decision that will move results. Pre-register one of: recode `0 → 1`, treat `0` as missing, or model
the battery as nominal-at-zero. Do not leave it to the default.

**4.2 Direction is not uniform, and three families run "backwards".** `E114`–`E117` are 1 = very good
… 4 = very bad, so *low* means endorsement; the trust (`D001_B`, `G007_*`) and confidence (`E069_*`)
families are 1 = complete … 4 = none. Every one of these needs reversing before the sign of a loading
means what the hypothesis says it means. `E265_*` is **mixed-keyed within the block** (`E265_01`
fair-counting is positive, `E265_03` TV bias is negative).

**4.3 Mixed measurement levels force the estimator.** The pool spans binary (`A0xx` child qualities),
3-point (`E018`), 4-point (trust, confidence, political systems), 5-point (`D026_05`) and 10-point
(`F1xx`, `E2xx`) items. This is **WLSMV with ordinal indicators, not ML** — and binary indicators
loading on the same factor as 10-point ones carry limited information, so the child-qualities battery
should not be a factor's only content.

---

## 5. The identity radius — a second Jellyby probe

**[NEW].** Alongside the trust radius the audit found, the joint core carries a complete concentric
**identity** gradient, fielded in all 40 countries:

`G255` village/town (98.9) → `G256` region (98.6) → `G257` country (98.7) → `G062` continent (97.3) →
`G063` world (96.1), all on the same 1–4 "how close do you feel" scale.

Two radius measures on identical response formats, plus the behavioural pair in §2, give the Jellyby
prediction three independent operationalisations — *whom you trust*, *whom you belong to*, *whom you
act for*. The prediction is that these dissociate: Jellyby-type profiles show wide anonymous
attachment with narrow concrete attachment. This should be a named construct-validity analysis, as
the audit recommended, and it is now considerably better resourced than a footnote.

---

## 6. A design warning the retranslation exposed

The "essential characteristics of democracy" battery (`E224`–`E233B`, nine items, one stem, one 0–10
scale) is currently supplying indicators to **D1** (`E229`, `E233`, `E233B`), **D2** (`E224`,
`E233A`) and **D3** (`E225`, `E226`, `E228`). A three-factor solution built substantially on one
battery risks recovering **stem and response-format structure rather than construct structure** — and
a psychometrician referee will say exactly that.

Mitigations, in order of preference: (i) model a battery-specific method factor, or correlated
uniquenesses across all nine, consistent with the CT-CU specification the design already adopts;
(ii) cap the battery's contribution so that no factor draws a majority of its indicators from it —
now feasible because `H009`–`H011` (D1), `A080_*`/`D026_05` (D2) and `E069_*`/`E265_*`/`E114`–`E117`
(D3) supply off-battery content to all three; (iii) report a sensitivity model with the battery
excluded entirely. **Pre-register (i) and (iii).**

---

## 7. Grid status after retranslation

| | Politics | Education | Science | Morality |
|---|---|---|---|---|
| **D1** | **FILLED** (6) | FILLED (5, one battery, binary) | **EMPTY** | **FILLED** (7) |
| **D2** | THIN (2, confounded) | THIN (3) | **EMPTY** | **FILLED** (4 + 5 off-battery) |
| **D3** | **FILLED** (13) | **EMPTY** — `Q75` lost | **EMPTY** in this sample | THIN (2) |

Changes against `DECISIONS.md` §3, which recorded a 3 × 2 primary grid:

1. **D3 × education is now empty, not thin.** Its one verified item was `Q75` (confidence in
   universities), which is not in the joint core. Education survives on D1 and D2 only.
2. **Science is empty in the primary sample** and available only as D3 in ESS10 (`trstsci`,
   22 countries). Report from ESS10 with an explicit label, or drop.
3. **D2 × politics remains the weakest cell** and both its items are ideology-confounded. The honest
   options are to model politics without D2 or to accept the confound and say so.

The **3 × 2 primary grid (D1, D2, D3 × politics, morality) stands**, with education entering on D1/D2
only. That is a reduction from the plan and should be stated in the abstract, per `DECISIONS.md`.

---

## 8. Reproduction

Every figure in this document is produced by **`code/01_audit_joint_core.py`**, which takes metadata
plus one `usecols` pass over `ZA7505_v5-0-0.dta` (no full 65 MB load) and writes
`translation-wvs7-to-joint.csv` and `item-validity-europe.csv` beside this file:

```bash
python3 code/01_audit_joint_core.py     # ~40 s, needs pyreadstat + pandas
```

Definitions it applies. The European sample is the 40 ISO alpha-2 codes in the script's `EUROPE`
constant (also listed in `data-audit-2026-08-10.md` §1.3). Validity = proportion of European rows with
value ≥ 0; EVS/WVS missing codes are `−1` don't know, `−2` no answer, `−3` not applicable, `−4` not
asked in survey, `−5` other, per `ZA7505_v5-0-0_missing.do`. "Fielded" = per-country validity ≥ 20 %.
Matrix-design status comes from `mm_matrix_group_EVS5`.

Expected output on the current data: 33 of 44 design Q-numbers map into the joint core; 78,396
European respondents in 40 of the file's 92 countries; 89 of 91 candidate items fielded in all 40.

## 9. Freeze status

**All three blocking decisions are now recorded** — as D1 (Cyprus exclusion), D2 (the `0`-category
recode) and D3 (the battery method factor) in **`docs/preregistration.md` §5**, each with its
evidence and a required sensitivity analysis.

**This table is therefore frozen as of the filing date of that registration.** From filing:

- items may be dropped **only** for a standardised loading < .30 in the configural model, or a
  Heywood case, each logged with its reason in the supplement;
- **no item may be added**;
- nothing may be dropped to improve fit or to rescue a hypothesis.

Until the registration is actually filed the table is *frozen-pending-filing*: changes are still
permissible but must be made now, before any analysis, and recorded here with a date and a reason.
