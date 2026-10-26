# S9 · Completed reporting checklists

Three guidelines are named in the manuscript (§4.6) and completed here: **ACCORD** for consensus
methods, **CREDES** for Delphi conduct and reporting, and **TRIPOD-LLM** for the language-model
component. None was written with *synthetic* panellists in view. Where an item has no analogue the
response says so and states what was done instead; nothing is marked as met that was not.

**Item wording is paraphrased, not reproduced.** Each row gives the guideline's item identifier, a
short statement of what that item asks, and our response with its location. The authoritative
wording is in the cited source.

Sources: ACCORD — Gattrell et al. (2024), *PLOS Medicine* 21(1), e1004326, Table 4 (CC BY).
CREDES — Jünger et al. (2017), *Palliative Medicine* 31(8), 684–706. TRIPOD-LLM — Gallifant et al.
(2025), *Nature Medicine* 31(1), 60–69.

Manuscript section numbers refer to `build/main.tex`. "S*n*" refers to this supplement.

---

## The one adaptation that runs through all three

Every one of these guidelines assumes **human panellists**. Ours are language-model endpoints
sampled in independent contexts, so four recurring item families are reported as *adapted* rather
than met:

| Item family | Human meaning | What we report instead |
|---|---|---|
| Recruitment | how people were invited | how endpoints were selected and personas specified (§4.4, S8) |
| Attrition / response rate | who dropped out | draws refused or lost to rate limiting, per cell (§4.4–4.5, S8) |
| Sociodemographics | who the panellists were | model identifiers, version dates, sampling parameters (S8) |
| Consent / ethics | participant protection | no human participants; `docs/ethics.md` |

This is stated in the manuscript (§4.6) and is not hidden in the checklist.

---

## S9.1 · ACCORD (35 items)

| # | What the item asks | Response |
|---|---|---|
| T1 | Title identifies a consensus exercise and names the method | **Adapted.** The consensus exercise is one component of a measurement paper, so the title does not name it; the abstract and §1 do, as a *synthetic* Delphi panel. Titling the whole paper as a consensus exercise would misdescribe it. |
| I1 | Why consensus rather than another approach | §4.1. Construct validation conventionally requires expert consensus; the paper's question is what a synthetic panel can and cannot do in that role. |
| I2 | Aim, intended audience, geographical scope | §4.1, §4.3. Aim: validate a three-dimensional measurement model and characterise the instrument. Audience: cross-national survey methodologists. Scope: the 39-country European analytic sample. |
| I3 | If an update, why, and cite the original | Not an update. No prior consensus document exists for this construct. |
| M1 | Prospective registration, platform and link | §3, §4.3. OSF `ezjh2`, DOI `10.17605/OSF.IO/EZJH2`, filed 2026-08-10 07:45:39 UTC. The Tier-2 forecast is separately frozen at `zrvdp`, DOI `10.17605/OSF.IO/ZRVDP`. Registration Update #1 filed 2026-08-10 07:56:12 UTC and disclosed in the manuscript. |
| M2 | Roles and expertise of those directing the exercise | The authors designed and ran it; there was no steering committee separate from the author team. Author details are on the title page, withheld from the review copy. |
| M3 | Panelist inclusion criteria, rationale for numbers, who selected | §4.4, S8. Six endpoints from five developers, six expert personas, giving 144 cells. The floors (≥3 phrasings, ≥2 detail levels, ≥2 temperatures, ≥3 model families) were pre-registered; the realised grid exceeds each. |
| M4 | Recruitment process | **Adapted — no analogue.** Endpoints were not invited; they were called. Selection criteria and the full endpoint list are in S8. |
| M5 | Role of members of the public, patients or carers | None. No human participants at any stage (`docs/ethics.md`). |
| M6 | How information was obtained before generating items | §3.2, S2. The item pool is the frozen joint EVS/WVS item table, hash-locked to the registration before any model was fitted. |
| M7 | Systematic literature search detail | No systematic search was conducted, and none is claimed. The construct derives from a documented reading of two passages of Popper, with page references in `quotations.md`. |
| M8 | How existing evidence was summarised and whether given to panelists | §4.3, S8. Panellists received the item table and the model specification, not the results. What was withheld is the point of the design and is stated. |
| M9 | Methods and steps used to gather input and reach consensus | §4.2–4.5. A forecasting Delphi: each panellist forecasts the analysis's own results. Modifications from a classical Delphi are stated in §4.3 and S8. |
| M10 | How each question was presented, response options, free text, new items | S8 and `supplement/tier2-forecast/tier2-prompt-A.txt`, `tier2-prompt-B.txt` — every prompt verbatim. Panellists could not propose new items; the item table was frozen. |
| M11 | Objective of each step | §4.3–4.5. Wave 1: the contamination-immune forecast. Wave 2: temporal replication only (§4.5, Table 2). Checks 4 and 5 are separate elicitations with their own objectives (S8). |
| M12 | Definition of consensus and its rationale | §4.2. **This is a paper-length finding, not a footnote:** consensus is a property of the cut-point, and the I-CVI cut-point ladder (mean I-CVI .981 → .907 → .685 → .333 → .065 on one fixed set of responses) shows the choice doing the work. The forecast is scored by Brier skill against realised results, not by an agreement threshold. |
| M13 | Whether consensus items re-entered later rounds | Not applicable. There is no item-retirement mechanism; wave 2 re-elicits the identical instrument in full, enforced by hash. |
| M14 | How responses were collected, individually or in a group | §4.4. One fresh context per persona per cell — independent draws, never one conversation emitting many answers. |
| M15 | How responses were processed and synthesised | §4.4, §5.7, `code/04`, `code/16`, `code/28`. Distributions are reported, never a point estimate. |
| M16 | Piloting of materials | §4.2. A pilot on 2026-08-09 (`docs/design/delphi-pilot.py`, S8) refuted the planned absolute-rating elicitation and demoted it to a negative control. 7 of 16 draws were lost to rate limiting; pilot responses are not pooled with the main run. |
| M17 | Feedback provided to panelists at each step | §4.5. Feedback appears only in the sycophancy check, where hold-out personas are shown a panel median that is true in one arm and inverted in the other. The forecasting waves involve no feedback between draws. |
| M18 | Anonymity: planned, where applied, how guaranteed | Not applicable in the human sense. Draws are independent contexts and cannot identify one another. |
| M19 | Whether the steering committee voted | No separate steering committee; the authors did not vote. |
| M20 | Incentives | None. Not applicable. |
| M21 | Accessibility adaptations | Not applicable. All elicitation was in English. |
| R1 | When conducted; dates and duration of each step | §4.3–4.5. Pilot 2026-08-09. Wave 1 2026-08-10 08:38:17 UTC (top-up 08:51:36). Checks 4–5 2026-08-11. Wave 2 2026-09-09 10:07:52 UTC (top-up 10:28:24), a realised interval of 30.062 days against a registered minimum of 30. |
| R2 | Deviations from protocol and why | §4.5, and `docs/preregistration.md` §11 in full. The homogenisation check is reported as executed-with-deviation; the sycophancy metric's saturation is reported as a failure of our own metric; wave 2's transport defect and repair are documented. |
| R3 | Per step, panelist counts, response rates, sociodemographics | **Adapted.** Wave 1: 144 of 144 cells accepted. Wave 2: 141 of 144, with the three missing cells reported as stable refusals rather than losses (§4.5). Per-endpoint completion is tabulated in `docs/preregistration.md` §7.2. Model identifiers and version dates stand in for sociodemographics (S8). |
| R4 | Final outcome, qualitative and/or quantitative | §5.7, Table 2. Brier skill score +.064, family-cluster bootstrap [+.016, +.104]. |
| R5 | Items modified or removed during the process, why and when | None. The item table was frozen and hash-locked before elicitation and did not change; the wave-2 guard refuses to run on any instrument mismatch. |
| D1 | Methodological strengths and limitations | §4.5, §7.4, §8. Including the finding that rewording the prompt moves the forecast slightly more than changing the model family does. |
| D2 | Consistency with pre-existing literature | §4.1, §7.4. Positioned against both the substitution literature and the case against it. |
| O1 | Endorsing organisations and their role | None. |
| O2 | Conflicts of interest and how managed | **For the authors to complete at submission.** Drafted in `docs/submission-disclosures.md`; not inserted into the manuscript, because the wording needs all authors' agreement. |
| O3 | Funding and the funder's role | **For the authors to complete at submission.** Same file, same reason. |

---

## S9.2 · CREDES (4 domains, 16 recommendations)

| Domain / recommendation | Response |
|---|---|
| **Rationale** — Justification for choosing Delphi | §4.1. Construct validation conventionally requires expert consensus; the paper asks what a synthetic panel does in that slot, so the technique is the object of study as well as the method. |
| **Planning** — Planning and process; modifications justified and applied systematically | §4.2–4.4. The modifications are substantial and are stated as such: panellists are language models, the elicitation is a forecast of the study's own results, and there is no iteration toward agreement. |
| **Planning** — A priori definition of consensus, with rules for proceeding, terminating and handling non-consensus | §4.2 and S8. Registered before elicitation. The cut-point analysis reports what that definition costs. Termination is fixed at two waves by the registered 30-day interval, not by attainment of agreement. |
| **Conduct** — Informational input reviewed and piloted in advance | §4.2. Piloted 2026-08-09; the pilot changed the design (the absolute rating became a negative control). |
| **Conduct** — Prevention of bias | §4.3–4.5. The load-bearing tier is contamination-immune by construction: the forecast was frozen and independently time-stamped before the CFA ran, and the analysis code refuses to run until the deposit is recorded. The sycophancy and contamination checks measure the residual. |
| **Conduct** — Interpretation: consensus is not correctness; non-consensus is informative | §4.5, §5.7, §7.4. The panel's dispersion is reported as data. Both institutional-respect correlations were forecast with the wrong sign, and that is reported as the result. |
| **Conduct** — External validation of the resulting guidance before publication | **Not applicable and deliberately not claimed.** No guidance is issued. The panel is an instrument with an error model, not a source of recommendations — stated in §4, §7.4 and §8. |
| **Reporting** — Purpose and rationale, and appropriateness of the technique | §4.1. |
| **Reporting** — Expert panel: selection criteria and recruitment | **Adapted.** §4.4 and S8: endpoints, personas, and the grid. There is no recruitment. |
| **Reporting** — Comprehensible methods: preparation, piloting, instrument design, rounds, analysis | §4.2–4.5, S8, and `code/03`, `code/04`, `code/16`, `code/21`, `code/28`. |
| **Reporting** — Flow chart of the stages | S8 documents each stage with its timestamp and disposition. No figure is drawn; the paper carries no figures. |
| **Reporting** — How consensus was achieved, including non-consensus | §4.2, §5.7. |
| **Reporting** — Results reported per round, with changes between rounds | §4.5, Table 2 — the two waves side by side, with the modal-assignment change rate, both α units, and the shift distribution. |
| **Reporting** — Critical reflection on limitations | §4.5, §7.4, §8. |
| **Reporting** — Conclusions adequate to the outcomes | §8. The Brier skill score is reported as thin, and the panel is not presented as validating the model. |
| **Reporting** — Publication and dissemination, identifiability of the guidance | No guidance is produced, so there is nothing to disseminate as such. Code, prompts and the full elicitation record are archived. |

---

## S9.3 · TRIPOD-LLM (modular; items conditional on design and task)

TRIPOD-LLM is explicitly modular: each item is scoped to a research design (M model development,
D fine-tuning, E evaluation, H human interaction, EH patient/EHR data) and an LLM task. **This
study is an evaluation (E) of closed and open-weight models on a forecasting and classification
task, with no model development, no fine-tuning, no patient or EHR data and no human participants.**
Items scoped to M, D, EH and H are therefore out of scope, and are marked so rather than left blank.

| # | What the item asks | Response |
|---|---|---|
| 1 | Title identifies development / fine-tuning / evaluation, task, population, outcome | **Adapted.** The title is of a measurement paper; §1 and §4 identify the LLM component as an evaluation. |
| 2 | Abstract per TRIPOD-LLM for abstracts | Abstract reports the panel, its score, its interval and its limits. Not all abstract items apply to a non-clinical study. |
| 3a | Context and rationale, citing existing approaches | §4.1. |
| 3b | Intended use, users, care pathway | Out of scope (E, H — clinical deployment). No deployment is proposed. |
| 4 | Objectives, and which stage the study addresses | §4.1, §4.3. Evaluation only. |
| 5a | Sources of training, tuning and evaluation data, with rationale | §3.1, §4.3. No training or tuning. Evaluation inputs are the frozen item table and model specification. |
| 5b | Data items and dataset characteristics | §3.1–3.3, S2. |
| 5c | Earliest and latest dates of text used | Elicitation inputs are dated: the item table was frozen 2026-08-10 and is unchanged across waves (hash enforced). Model training-data dates are not disclosed by the providers and are not asserted. |
| 5d | Preprocessing and quality checks, and whether uniform | §4.4, S8. Identical instrument for every cell; parsing failures are recorded, not silently dropped. |
| 5e | Missing and unbalanced data, exclusion reasons | §4.4–4.5. Every failed draw's disposition is recorded: wave 1 lost 41 cells to HTTP 429 and recovered them by top-up; wave 2 lost 96 to a transport defect, recovered 93, and the remaining three are refusals, reported as a finding. |
| 6a | Model name, version, final training date | S8 lists every endpoint identifier and its access date. Final training dates are not published by the providers; this is stated rather than guessed. |
| 6b | Development details: architecture, training, alignment | Out of scope (M, D). No model was developed or fine-tuned. |
| 6c | Generation process, prompt engineering, inference settings | §4.4, S8. Three phrasings, two persona detail levels, two temperatures (0.3 / 1.0), seeds and the retry budget all recorded; every prompt verbatim in the supplement. |
| 6d | Initial and post-processed outputs | S8, `code/03`, `code/04`. Raw replies are archived alongside parsed values. |
| 6e | Classification details, probability derivation, thresholds | §4.2, §5.7. Probability forecasts are elicited directly; the modal-assignment mapping and the .5 rule are fixed in the script header before computation. |
| 7a | Quality metrics for generated output | §4.4–4.5. Dispersion decomposition, contamination, sycophancy, temporal replication. |
| 7b | Downstream task metric suitability and correlation with human evaluation | **Not met, and the gap is stated.** No human criterion panel exists — Decision 1 removed it — so no correlation with human evaluation can be reported. §4.1 and §8 say so explicitly; this is the paper's largest single limitation on the C2 claim. |
| 7c | Outcome definition, how predictions were produced, inference dates, metrics | §4.3, §5.7. Brier score and Brier skill score against the realised CFA results; wave-1 inference 2026-08-10, wave-2 2026-09-09. |
| 7d | Subjective assessment: rater qualifications, guidance, demographics, agreement | **Adapted.** The "raters" are personas; their specifications are in S8. Agreement between waves is Table 2. |
| 7e | Comparators for performance | §5.7. The registered comparator is a no-skill reference; the skill score is computed against it, with a family-cluster bootstrap. |
| 8a–8c | Annotation: labelling scheme, annotator counts and agreement, annotator background | Out of scope. No annotation task; the panel forecasts, it does not label a corpus. |
| 9a | Prompt design, selection and refinement | §4.4, S8. The perturbation grid *is* the prompt-variation report, and its result — rewording moves the forecast slightly more than changing model family — is reported. |
| 9b | Data used to develop prompts | S8. Prompts were drafted from the registered design document and piloted once (2026-08-09). |
| 10 | Summarisation preprocessing | Out of scope. Not a summarisation task. |
| 11 | Instruction tuning / alignment strategy | Out of scope (M, D). |
| 12 | Compute resources or proxies | S8 records wall-clock per run and the endpoint mix. Provider-side FLOPs are not observable and are not asserted. |
| 13 | Ethical approval, consent or waiver | No human participants, so no approval was required. `docs/ethics.md` is the no-participants record. |
| 14a | Funding and funder role | **For the authors to complete at submission.** |
| 14b | Conflicts of interest | **For the authors to complete at submission.** |
| 14c | Where the protocol is available | OSF `ezjh2`; the maintained version with all deviations is S3. |
| 14d | Registration details | OSF `ezjh2`, DOI `10.17605/OSF.IO/EZJH2`, 2026-08-10; forecast deposit `zrvdp`, DOI `10.17605/OSF.IO/ZRVDP`. |
| 14e | Data availability | Manuscript data-availability statement, and S4. |
| 14f | Code availability | Manuscript code-availability statement; all code in the supplement with a checksummed manifest. |
| 15 | Patient and public involvement | None; no human participants. |
| 16a–16d | Participant flow and characteristics (patient/EHR data) | Out of scope (EH). No patient or EHR data. |
| 17 | Performance against pre-specified metrics | §5.7. |
| 18 | Results of any model updating | Not applicable. No model was updated. The two waves use the identical instrument; any change in the underlying services is the object of measurement, not a modification by us. |
| 19a | Interpretation in context, including fairness | §7.4, §8. |
| 19b | Limitations, bias, uncertainty, generalisability | §4.5, §7.4, §8. Including that a result here would not transfer to another task or configuration range. |
| 19c–19f | Usability in context: representation, missingness, intended users, autonomy, low-quality input, required expertise | Out of scope (E, H — deployment). No deployment is proposed; §4 and §8 state that the panel is not a substitute for expert consultation. |
| 19g | Next steps, applicability, generalisability | §8. |
