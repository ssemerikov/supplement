# Ethics record

**Paper C / paper69 — Popperian Individualism Index. Target: *Quality & Quantity* (Springer).**
Last updated 2026-08-10.

## Summary

**This study involves no human participants and requires no ethics approval.** It is a secondary
analysis of existing, de-identified, publicly archived survey microdata, plus an instrument-validation
exercise conducted with large language models rather than people.

## 1. Human participants — none

No participants were recruited, contacted, observed, surveyed or interviewed by the authors. The
original surveys analysed here obtained their own consent and approvals from their own respondents,
under the governance of the archives that distribute them:

| Source | Governance |
|---|---|
| Joint EVS/WVS 2017–2022 (GESIS ZA7505 v5.0.0, `doi:10.4232/1.14320`) | Fieldwork ethics, consent and anonymisation handled by the EVS and WVS national teams; the archived file is de-identified |
| European Social Survey rounds 9, 10, 11 (Sikt / ESS ERIC) | ESS ERIC research-ethics framework; archived files de-identified |

The authors received only the de-identified archived files. **No attempt was made, and none may be
made, to re-identify any respondent**, including by combining the microdata with the country-level
covariates (V-Dem, QoG, Hofstede, Welzel) used in this study.

An earlier design (`plan-C-quality-quantity-pii-delphi.md`) proposed recruiting a human criterion
panel of 8–12 experts, which *would* have required approval. **That component was removed** by
Decision 1 in `docs/design/DECISIONS.md`, in favour of a two-tier synthetic criterion whose
load-bearing tier is a contamination-immune forecast of this study's own analysis. If the authors
later choose to run a human panel, it becomes a **new study requiring its own approval before any
contact with participants**, and enters this paper only as supplementary confirmatory evidence.

## 2. Data protection

No personal data within the meaning of the GDPR are processed: the archived microdata are
de-identified and are distributed by the archives for exactly this purpose. Access is under the
registered-user terms of GESIS and Sikt, recorded with dates and checksums in
`docs/data-provenance.md`.

**One operational point.** `data/userID` holds the author's personal ESS API credential. It is
excluded from the supplement, from any repository upload and from the replication package. The
replication package tells readers how to obtain their own credential instead.

## 3. The synthetic panel — no human subjects, but disclosure obligations

The Delphi-style validation panel is composed of **large language models prompted to adopt expert
personas**. No people take part. Personas are fictional and are not modelled on, named after, or
designed to resemble any identifiable person.

This raises no human-subjects issue but does raise reporting obligations, which are met as follows:

- Every prompt is published **verbatim** in `supplement/`, together with model identifiers, versions,
  access dates, temperatures, seeds where available, and the full raw responses including failures.
- Reporting follows **ACCORD/CREDES** with LLM-specific extensions modelled on **TRIPOD-LLM**
  (Gallifant et al. 2025).
- **The panel is described throughout as an instrument with a documented error model, never as a
  substitute for expert consultation** — stated in the manuscript in both §4 and §8, and in
  `docs/preregistration.md` §7.
- Known failure modes are reported rather than suppressed, including the HTTP 429 losses in the pilot
  (7 of 16 rating draws) and the contamination of the Tier-1 criterion.

## 4. Use of LLMs in preparing the manuscript

**This is a separate obligation from the synthetic-panel method section and is not addressed here.**
The declaration of LLM use in the research and writing process is drafted in
`docs/submission-disclosures.md`. **It must not be inserted into the manuscript until all authors have
agreed its wording.**

## 5. Statements required at submission

- **Ethics approval:** not required; no human participants. Wording to be finalised against *Quality
  & Quantity*'s submission checklist.
- **Consent to participate / consent to publish:** not applicable.
- **Data availability:** third-party archived data, obtainable by any registered user from GESIS and
  Sikt; redistribution of the microdata is not permitted, so the statement points to the archives and
  the study DOIs rather than depositing the files. Draft in `docs/submission-disclosures.md`.
- **Code availability:** all analysis code deposited; see `code/` and `supplement/`.
- **Competing interests:** authors' declaration required; not drafted by the agent.

## 6. Status

| | |
|---|---|
| Ethics approval needed | **No** |
| Application filed | Not applicable |
| Human participants | None |
| Blocking submission | **No** — this was formerly "long pole 2" and was removed by Decision 1 |
