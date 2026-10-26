# Data provenance — paper69 (PII / synthetic-Delphi)

**Maintained incrementally. Every row is written the moment a source is resolved, not at the end.**
Statuses used: `DOWNLOADED` · `REQUIRES USER ACCOUNT` · `PAYWALLED` · `LICENCE FORBIDS REDISTRIBUTION` ·
`NOT FOUND` · `PARTIAL`.

All access dates are **2026-08-09** unless stated otherwise. Every URL in this file was fetched or
HEAD-checked on that date; nothing here is quoted from memory. Byte counts are the actual bytes on disk
and were confirmed equal to the server's `Content-Length`.

Raw acquisition log with per-request HTTP statuses:
`docs/design/data-acquisition.PROTOCOL.md` (**closed 2026-08-10**; copy into `supplement/` before submission).

---

## 1. Summary table

| # | Dataset | Version | Status | Local path | Licence in one line |
|---|---|---|---|---|---|
| 1 | V-Dem country-year Full+Others | v16 (March 2026) | `DOWNLOADED` | `data/vdem/vdem.RData` | Free, open, citation requested |
| 2 | V-Dem European subset (derived) | derived from v16 | `DOWNLOADED` | `data/vdem/vdem-v16_country-year_2015-2025_selected.csv` | inherits #1 |
| 3 | QoG Standard cross-section | Jan26 (30 Jan 2026) | `DOWNLOADED` | `data/qog/qog_std_cs_jan26.csv` | Free for academic/non-commercial; **redistribution prohibited without consulting original sources** |
| 4 | Hofstede 6 dimensions (as-published) | 2015-08-16 file | `DOWNLOADED` / **licence unclear for redistribution** | `data/hofstede/6-dimensions-for-website-2015-08-16.csv` | Research use permitted without asking; redistribution not addressed |
| 5 | Hofstede 6 dimensions (0–100 rescaled) | 2015-12-08 file | `DOWNLOADED` / **licence unclear for redistribution** | `data/hofstede/6-dimensions-for-website-2015-12-08-0-100.csv` | as #4 |
| 6 | ESS rounds 9, 10, 11 microdata | R9 e3.3 / R10 e3.3 / R11 **e4.2** | `DOWNLOADED` 2026-08-10 | `data/ESS9e03_3.sav`, `ESS10e03_3.sav`, `ESS11e04_2.sav` | Free, but registration + acceptance of conditions of use |
| 7 | ESS multilevel data, round 9 | ESS9MDWe03.1 | `NOT DOWNLOADED — available, deferred on size` | — | Same ESS terms; file is served publicly |
| 8 | Joint EVS/WVS 2017–2022 (GESIS ZA7505) | v5.0.0 (2024-06-24), `doi:10.4232/1.14320` | `DOWNLOADED` 2026-08-10 | `data/ZA7505_v5-0-0.dta` + correspondence table, codebooks, questionnaires, errata | Free for academic use on registration; cite both EVS and WVS releases |
| 9 | Eurobarometer (GESIS) | *pending* | *pending* | — | *pending* |
| 10 | Welzel emancipative values | in QoG Standard **Jan22** | `PARTIAL — re-fetch in progress` | — | QoG terms + cite Welzel (2013) |

---

## 2. Full records

### 1. V-Dem country-year Full+Others, v16 — `DOWNLOADED`

- **File**: `data/vdem/vdem.RData`
- **Bytes**: 33,878,255 (equals server `Content-Length`; download complete)
- **SHA256**: `39b412d39a061c18f20c98e4ad4d6355b05a0441df31be4ee9aec420dc3d95ea`
- **Contents (verified in R 4.6.1)**: one object, `vdem`, a `data.frame` of **28,092 rows × 4,618 columns**,
  years **1789–2025**, **202 countries**. `v2x_liberal`, `v2x_civlib`, `v2x_libdem`, `v2x_clpol`,
  `v2x_clpriv` all present.
- **Version evidence**: `DESCRIPTION` of the distributing package reads `Version: 16.0`
  (https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/DESCRIPTION), and
  https://v-dem.net/data/the-v-dem-dataset/ states v16 was published March 2026.
- **Access date**: 2026-08-09
- **URL used**: `https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/data/vdem.RData`
- **Why this URL and not the website form**: the official page
  `https://v-dem.net/data/the-v-dem-dataset/country-year-v-dem-fullothers-v16/` serves the file only through
  a POST form requiring an **email address, a gender selection, a newsletter checkbox and a privacy-policy
  consent** (anti-bot is a honeypot field named `website`, not a CAPTCHA). Submitting a person's email
  address is not something an agent should do on their behalf, so the **V-Dem Institute's own R package
  repository** — which the dataset page itself recommends ("For R users, we recommend to install our
  vdemdata R package which includes the most recent V-Dem dataset") — was used instead. Same publisher,
  same version, no personal data disclosed.
- **Licence**: V-Dem FAQ (https://v-dem.net/about/faq/): all V-Dem data and graphs are open source and free
  for anyone to use; "You do not need to seek permission to use the data, but we kindly ask you to cite the
  data." **No redistribution restriction.** Note the `License: GPL-3` line in the package `DESCRIPTION`
  covers the **R package code**, not the data.
- **Required citation (v16, verbatim from the FAQ)**: Coppedge, Michael, John Gerring, Carl Henrik Knutsen,
  Staffan I. Lindberg, Jan Teorell, David Altman, Fabio Angiolillo, Michael Bernhard, Agnes Cornell,
  M. Steven Fish, Linnea Fox, Lisa Gastaldi, Haakon Gjerløw, Adam Glynn, Ana Good God, Allen Hicken,
  Katrin Kinzelbach, Joshua Krusell, Kyle L. Marquardt, Kelly McMann, Valeriya Mechkova, Juraj Medzihorsky,
  Anja Neundorf, Pamela Paxton, Daniel Pemstein, Josefine Pernes, Johannes von Römer, Brigitte Seim,
  Rachel Sigman, Svend-Erik Skaaning, Jeffrey Staton, Aksel Sundström, Marcus Tannenberg, Eitan Tzelgov,
  Yi-ting Wang, Tore Wig, Steven Wilson and Daniel Ziblatt. 2026. "V-Dem [Country-Year/Country-Date]
  Dataset v16" Varieties of Democracy (V-Dem) Project.

### 2. V-Dem selected-variable subset, 2015–2025 (derived) — `DOWNLOADED` (derived)

- **File**: `data/vdem/vdem-v16_country-year_2015-2025_selected.csv`
- **Bytes**: 367,976 · **SHA256**: `5253001c73d344277b4fdfe9c1b9e7a711b7b11d0335cf9168fec8a946deda7e`
- **Shape**: **1,969 data rows × 32 columns**, 179 countries, years 2015–2025 inclusive.
- **Produced by**: an R one-liner over record 1 (no network). The generating code must be committed to
  `supplement/` before submission; it is not yet in the repo.
- **Variables kept**: `country_name`, `country_text_id`, `country_id`, `year`, `COWcode`, `historical_date`,
  `v2x_polyarchy`, `v2x_libdem`, `v2x_liberal`, `v2x_civlib`, `v2x_clpol`, `v2x_clpriv`, `v2xcl_rol`,
  `v2x_freexp_altinf`, `v2x_frassoc_thick`, `v2xcl_dmove`, `v2clacjstm`, `v2clacjstw`, `v2xca_academ`,
  `v2x_egaldem`, `v2x_partipdem`, `v2x_delibdem`, `v2x_jucon`, `v2xlg_legcon`, `v2x_corr`, `v2x_rule`,
  `v2xeg_eqprotec`, `v2xeg_eqaccess`, `v2xeg_eqdr`, `e_regionpol_6C`, `e_gdppc`, `e_pop`.
- **Known gap**: `v2xcl_slavemv` was requested but **does not exist in v16** — recorded here so nobody
  looks for it again.
- **Coverage check**: `v2x_liberal` is non-missing for 179 countries in **every** year 2015–2025, so V-Dem
  will not be the binding constraint on the country intersection.

### 3. QoG Standard dataset, cross-section, Jan26 — `DOWNLOADED`

- **File**: `data/qog/qog_std_cs_jan26.csv`
- **Bytes**: 1,693,291 (= `Content-Length`; complete) · **SHA256**:
  `64adb3b0cfc7898b624a14d9cc1195dcd68721e5ffc15e8d79da12c985345843`
- **Shape**: **194 data rows × 1,487 columns**. First columns: `ccode`, `ccode_qog`, `ccodealp`, `ccodecow`,
  `cname`, `cname_qog`.
- **URL**: `https://www.qogdata.pol.gu.se/data/qog_std_cs_jan26.csv` (server `Last-Modified`: Thu, 05 Feb 2026)
- **Version**: Jan26; the QoG download page states the version was last modified **30 January 2026**.
  Source page: `https://www.gu.se/en/quality-government/qog-data/data-downloads/standard-dataset`
- **Codebook**: `https://www.qogdata.pol.gu.se/data/codebook_std_jan26.pdf` (not yet downloaded)
- **Sibling files, verified to exist (HEAD 200) but not downloaded**:
  `qog_std_ts_jan26.csv` (71,595,226 bytes, 1,813 columns),
  `qog_bas_cs_jan26.csv` (416,153 bytes, 320 columns),
  `qog_bas_ts_jan26.csv` (15,582,192 bytes, 266 columns).
- **Why it matters here**: it carries the V-Dem block (`vdem_*`) and a `wvs_*` block, giving a country-level
  cross-check without touching restricted microdata. **It does NOT carry Welzel's `wel_*` block** — see
  record 10.
- **Licence**: free of charge for academic and non-commercial purposes. **Redistribution, commercialisation
  and for-profit use are prohibited without consulting the original data sources.** → Do **not** ship this
  CSV in the supplement; ship the download script and the derived country-level extract only, and check
  each contributing source's own terms for anything reproduced in a table.
- **Required citation**: Teorell, Jan, Aksel Sundström, Sören Holmberg, Bo Rothstein, Natalia Alvarado
  Pachon, Victor Saidi Phiri, Chuwei Chen & Zhen Liu. 2026. *The Quality of Government Standard Dataset,
  version Jan26.* University of Gothenburg: The Quality of Government Institute.

### 4–5. Hofstede six-dimension country scores — `DOWNLOADED`, **licence unclear for redistribution**

- **Files and hashes**
  - `data/hofstede/6-dimensions-for-website-2015-08-16.csv` — 4,267 bytes —
    SHA256 `71bff58cf610ec44b870d5aa4b06bb36e3a573860d513ff802488764d6e029a6`
  - `data/hofstede/6-dimensions-for-website-2015-12-08-0-100.csv` — 4,264 bytes —
    SHA256 `4b2a63142090f69afcb99cb428358be5dcc386ee78fb4944ba278fa4f78aa96d`
  - Both byte counts equal the server `Content-Length`; both complete.
- **URLs** (re-verified live, HTTP 200, server `Last-Modified: Tue, 20 Sep 2016`):
  - `https://geerthofstede.com/wp-content/uploads/2016/08/6-dimensions-for-website-2015-08-16.csv`
  - `https://geerthofstede.com/wp-content/uploads/2016/08/6-dimensions-for-website-2015-12-08-0-100.csv`
- **Landing page**: `https://geerthofstede.com/research-and-vsm/dimension-data-matrix/`
- **Shape**: both are **111 data rows × 8 columns**, delimiter `;`, header
  `ctr;country;pdi;idv;mas;uai;ltowvs;ivr`. **Only 78 of the 111 rows have a non-empty `idv`** — the rest
  are `#NULL!`. `idv` is the variable H3 needs.
- **Why two files, and which to use.** The landing page explains it verbatim: the 2015-08-16 file is
  "the data as used in our books"; for the second, "For those that prefer to work with scales of 0 to 100,
  we have in 2014 brought some outlying values, obtained in replication studies, within the 0-100 range.
  they are: PDI of Malaysia and Slovakia 104 to 100; MAS of Slovakia 110 to 100; UAI of Greece 112 to 100,
  of Portugal 104 to 99, of Guatemala 101 to 98, of Uruguay 100 to 98." **None of the six adjustments
  touches `idv`**, so for H3 the two files are interchangeable. **Recommendation: use the as-published
  2015-08-16 file** and say so, because the rescaled file is a post-hoc convenience edit.
- **On the 2015 date being "stale" — it is not.** These are the scores "as presented in *Cultures and
  Organizations* 3rd edition 2010"; Hofstede's canonical country scores have not been re-estimated since,
  and the file timestamps (2016-09-20) are when they were uploaded to the current site. What has changed
  since is the *commercial* presentation layer (Hofstede Insights' country-comparison tool), not the
  academic score matrix. The site footer reads "© 2026 Geert Hofstede", i.e. the page is currently
  maintained. **Inferred, flagged as such**: any newer or expanded Hofstede country list circulating
  elsewhere is not from this canonical file and should not be mixed into it.
- **Licence — the honest position.** The page grants **use**, not redistribution: "Researchers can use them
  without asking for permission. Those who are considering commercial use should contact us." There is
  **no open licence, no CC designation, and no statement permitting redistribution**, and the material is
  under copyright ("© 2026 Geert Hofstede"). Practical consequence for this paper:
  1. Using `idv` in the analysis and reporting derived statistics is clearly covered.
  2. **Do not republish the score matrix in the supplement.** Ship the URL, the SHA256 above and the
     download script so a reader can re-fetch the identical file.
  3. If a table of country IDV values is needed in the manuscript, keep it to the countries actually
     analysed and cite Hofstede (2010) / geerthofstede.com as the source.
  4. The data-availability statement must say Hofstede scores are third-party data available from
     geerthofstede.com under the site's own terms, not redistributed by the authors.
- **Also on that page, not downloaded**: `.xls` twins of both CSVs, and
  `NonOfficial-VSM08-scores-2014-01-04.docx` (Nepal, Sri Lanka; explicitly *not* integrated into the model
  — do not use).

### 6. ESS rounds 9–11 microdata — `DOWNLOADED` 2026-08-10

Obtained by the author under an ESS account. Read directly with `pyreadstat`; counts below are from
the files, not the documentation.

| File | Round / edition | Rows × vars | Countries | SHA-256 |
|---|---|---|---|---|
| `data/ESS9e03_3.sav` | R9, ed. 3.3 | 49,519 × 575 | 29 | `a97000ced99d5e0b0ae59393963ccf3bc39e3f24b7312336176799a3ee9a1142` |
| `data/ESS10e03_3.sav` | R10, ed. 3.3 | 37,611 × 621 | 22 | `351aeac3e231bac977f1e6ba22c775108ce36fa43e8787b508e9ef4da8956f5e` |
| `data/ESS11e04_2.sav` | R11, ed. 4.2 | 50,116 × 691 | 30 | `35809b1883495d8e1cb3ed604f56c2ddf80c2666e9be11332a7d3502d3d631ae` |

Editions differ from the ones anticipated above: **round 11 is edition 4.2, not 4.0.** All three
codebooks (`ESS*e0*_* codebook.html`) are alongside the data.

Three facts established by reading these files, all consequential for analysis code:

- **`trstsci` ("trust in scientists") exists in ESS10 only**, together with `scidecpb`. It is absent
  from ESS9 and ESS11. The earlier finding that it does not exist in ESS9 was correct; the inference
  that ESS therefore has no science content was not.
- **ESS11 renames all 21 PVQ human-values items with an `a` suffix** (`ipcrtiva`, `impricha`, …). A
  lookup using round-9/10 names returns 0 of 21 and silently produces an empty D2 for round 11. The
  suffix marks a revised administration, so cross-round comparability is a measurement-invariance
  question, not an assumption.
- **The `sofrdst` / `sofrwrk` / `sofrpr` justice items — the best D2-in-politics indicators — are
  ESS9-only.**

Citation and conditions of use are unchanged from the ESS terms recorded below. **A file
`data/userID` holds the author's ESS API user identifier.** It is a personal credential: exclude it
from the supplement, from any repository upload, and from the replication package.

Original access evidence, retained because it documents the route:

- Distribution is by **Sikt** for ESS ERIC at `https://ess.sikt.no` (the old `ess-search.nsd.no` 301s there).
- The portal is a single-page app; `https://ess.sikt.no/env.js` exposes
  `VITE_API_URL='https://api.nsd.no/graphql'` and `VITE_AUTH_SERVER='https://sso.nsd.no'`.
- Its JS bundle contains a component named `LogInAndDownload` rendering the literal string
  `"(Requires login)"` next to the download button.
- There **is** a public REST API — `https://api.ess.sikt.no/docs`, OpenAPI at
  `https://api.ess.sikt.no/docs/openapi`, currently in beta, one endpoint:
  `GET /v1/data/dataFile/{doiPrefix}/{doiSuffix}` with **required** `userId`, optional
  `fileFormat` ∈ {`parquet`,`csv`,`sav`,`dta`} and `recodeMissingValues`. DOIs are per data file, e.g.
  `10.21338/ess11e01_0`; study-level DOIs (e.g. `10.21338/NSD-ESS10-2020`) are **not** accepted.
- Probed without credentials on 2026-08-09: no `userId` → **HTTP 400**
  `{"code":101,"message":"Query parameter userId missing"}`; `userId=invalid-probe` → **HTTP 400**.
  So the parameter is enforced even though the spec calls it a usage-statistics field, not authentication.
  **No ESS data were retrieved and no `userId` was fabricated.**
- Round 11 final release: **edition 4.0, 21 November 2025**, 30 countries (source:
  `https://www.europeansocialsurvey.org/news/article/final-release-round-11-data`). Czechia participated but
  is available **only as a country-specific file**, because it used self-completion rather than
  face-to-face — a real comparability problem for this paper, not a formality.

### 7. ESS Round 9 multilevel data — available without an account, **deliberately not downloaded yet**

- Public Azure blob, no login, HEAD 200 on 2026-08-09:
  - `https://stessrelpubprodwe.blob.core.windows.net/data/essmd/ESS9MDWe03.1.stata.zip` —
    **571,072,048 bytes**, `Last-Modified: Thu, 17 Feb 2022`
  - `https://stessrelpubprodwe.blob.core.windows.net/data/essmd/ESS9MDWe03.1.spss.zip` —
    **662,259,761 bytes**
  - SAS variant also listed. Rounds 4–9 only; guessed round-10/11 names return **HTTP 404**.
- Contents established **without downloading the file**, by an HTTP Range request for the last 70,000 bytes
  and parsing the zip central directory: exactly three members —
  `ESS9MDWe03.1_F1.dta` (**1,967,118,578 bytes uncompressed**), `ESS9MDWe03.1_F1.missRecode` (121,710),
  `ESS9MDWe03.1.pdf` (2,142,847).
- **This is genuine ESS Round 9 respondent-level data** (individual records merged with regional and
  national contextual variables), reachable with no account. It is the only ESS microdata obtainable
  without the user's credentials.
- Not fetched because ~0.6 GB compressed / ~2.0 GB extracted inside a **Dropbox-synced** directory is a side
  effect the user should choose, and because the same round arrives more cheaply and in the right shape
  once the user registers. **Decision deferred to the user** — see §3.
- Container listing is disabled (`?restype=container&comp=list` → `ResourceNotFound`), so file names cannot
  be enumerated; only names published on the ESS site are reachable.

### 8. Joint EVS/WVS 2017–2022, GESIS ZA7505 v5.0.0 — `DOWNLOADED` 2026-08-10

**The primary sample for this paper.** Obtained by the author under a GESIS account; access route and
the required verbatim citation are in §3 below.

| Item | Value |
|---|---|
| Study | GESIS ZA7505, Joint EVS/WVS 2017–2022 |
| Version | 5.0.0, released 2024-06-24 |
| DOI | `10.4232/1.14320` |
| File | `data/ZA7505_v5-0-0.dta`, 66,415,887 bytes |
| SHA-256 | `16407d91bcb9dff1ff246ee5a515a2089bd2d1ca8525e69a824b6212cc4743ce` |
| Contents | **156,658 respondents × 231 variables × 92 countries** |
| European subsample | **40 countries, 78,396 respondents** |

Accompanying documentation, all in `data/`: `ZA7505_VariableCorrespondence.xlsx` (SHA-256
`68f4629a2ae3957aacad46e1b1dbcd7ace5ecf88848eadd10c09c8fe155b4728`; 230 mapped variables — **the
authority for translating WVS7 `Q`-numbers into integrated names**), `ZA7505_cdb.pdf` and
`ZA7505_cdb_Tables.pdf` (codebook), `ZA7505_bq_EVS2017.pdf` and `ZA7505_bq_WVS7.pdf` (source
questionnaires), `ZA7505_Errata_v5-0-0.pdf`, `ZA7505_ParticipatingCountries.xlsx`, and
`ZA7505_v5-0-0_missing.do` (**the definition of the missing codes** `−1` don't know, `−2` no answer,
`−3` not applicable, `−4` not asked in survey, `−5` other).

Two properties of this file govern the analysis and are documented in
`docs/design/item-table-v2-joint-names.md`:

- **The 231 variables are the EVS5 ∩ WVS7 intersection.** Items fielded by only one of the two
  surveys — the whole `Q158`–`Q163` science block, `Q291`, `Q75` — are therefore absent. This is the
  design of the file, not an omission.
- **Missingness must be read from the negative codes, not from `notna()`.** A naive read reports
  100 % coverage on every item. Real European validity is 92–98 % on the key items, with planned
  `−4` missingness on the democracy battery in DK (49.6 %), NL (37.8 %), FI (11.9 %) and IS (3.1 %).

### 10. Welzel emancipative values — `PARTIAL`, route identified

- **Not in current QoG.** Header inspection (by HTTP Range, no full download) shows **zero `wel_*`
  columns** in `qog_std_cs_jan26.csv`, `qog_std_ts_jan26.csv`, `qog_bas_cs_jan26.csv`,
  `qog_bas_ts_jan26.csv`, and zero in `qog_std_ts_jan25.csv`.
- **Present in the Jan22 and Jan20 archives**: `https://www.qogdata.pol.gu.se/data/qog_std_ts_jan22.csv`
  (Content-Length **66,513,999**) has **24 `wel_*` columns including `wel_evi`**; `qog_std_ts_jan20.csv`
  likewise 24. `qog_std_ts_jan18.csv` → HTTP 404.
- So Welzel's *Freedom Rising* block was dropped from QoG Standard between Jan22 and Jan25. The archived
  file remains publicly served and is the cleanest machine-readable route to `wel_evi`.
- Variable definition (from `https://datafinder.qog.gu.se/variable/wel_evi`): "Protective-vs.-Emancipative
  Values", a 12-item index over reproductive choice, gender equality, people's voice and personal autonomy,
  0–1, country population means. Source dataset "Data from Freedom Rising by Christian Welzel",
  last updated by source **2014-03-01**, 104 countries.
- **Citation**: Welzel, C. (2013). *Freedom Rising: Human Empowerment and the Quest for Emancipation.*
  Cambridge University Press.
- **Caveat the paper must state**: `wel_evi` as distributed by QoG is anchored to WVS/EVS waves up to
  wave 6 (source last updated 2014). It is **not** contemporaneous with ESS 9–11 or WVS 7. For H3 that is
  tolerable — H3 asks whether the *existing single-axis measures* load on D1 and are silent on D2, and
  those measures are exactly these historical ones — but the temporal mismatch must be declared, not hidden.

---

## 3. What the user must do — ESS and EVS/WVS registration

> **Completed 2026-08-10.** Both registrations were done and all files are in `data/`. **There is no
> remaining external data gate on this paper.** The instructions below are kept because the
> replication package must tell a reader how to obtain the same files, and because the API route in
> the ESS subsection is how the download becomes scripted and reproducible.

This is one of the project's two long poles. Nothing below can be done by an agent.

### ESS (about five minutes)

1. Go to **https://ess.sikt.no/** and choose "Log in" (identity is handled by `https://sso.nsd.no`).
   Register if there is no existing account; academic email is fine.
2. Complete the ESS user profile and accept the conditions of use.
3. Download the **integrated cumulative or per-round files** for **rounds 9, 10 and 11** in `.dta` or `.sav`
   from the portal's three-step wizard (round/country → variables → download). Selecting only the variables
   the paper needs makes the files far smaller than the full round files.
4. **Also, for scripted and reproducible access**, visit **https://ess.sikt.no/en/api** while logged in and
   copy the **user ID** shown there. With it, the whole acquisition becomes one reproducible line per file:
   ```
   https://api.ess.sikt.no/v1/data/dataFile/10.21338/<datafile-doi-suffix>?userId=<USER_ID>&fileFormat=csv&recodeMissingValues
   ```
   e.g. suffix `ess11e01_0`. Put the user ID in an untracked env var, never in the repo.
   Note the spec's own warning: some larger data files are not available through the API.
5. Paste the user ID (or the downloaded files) where the analysis can reach them, and tell the agent.

### EVS / WVS — the Joint EVS/WVS 2017–2022 dataset (about five minutes)

**Verified 2026-08-10.** This is the paper's **primary individual-level backbone** (see
`design/DECISIONS.md` §4), so it matters more than ESS.

The dataset to get is **Joint EVS/WVS 2017–2022, GESIS study ZA7505, Dataset Version 5.0.0,
`doi:10.4232/1.14320`** — DOI resolved and confirmed against DataCite (publisher GESIS, issued 2024,
type dataset). The *identical* file is served from two access points; either is fine:

1. **GESIS** — https://search.gesis.org/research_data/ZA7505 → "Download". Requires a free GESIS
   account and acceptance of the usage terms. Formats: Stata, SPSS, CSV.
2. **WVS Association** — https://www.worldvaluessurvey.org/WVSDocumentationWV7.jsp (HTTP 200 as of
   today). Requires accepting the WVS conditions and completing a short form.

**Also download the two documentation files, which the item table depends on:**
- the **Joint EVS/WVS Variable Correspondence Table** — needed to resolve whether WVS7-only items
  (the `Q158`–`Q163` science block and the `Q291` parliament/government evaluation block) are present
  in the joint *common core* or only for WVS countries. Several `[U]`-tagged items in the design's
  item table cannot be frozen until this is checked, and the science sphere's fate depends on it.
- the **EVS 2017 Variable Report (ZA7500)** — for EVS-specific variable names and weight variables.

**Required citation** (use verbatim; note it is a dataset citation, and no Cyrillic issue arises):

> EVS/WVS (2024). *European Values Study and World Values Survey: Joint EVS/WVS 2017-2022 Dataset
> (Joint EVS/WVS)*. GESIS Data Archive, Cologne. ZA7505. Dataset Version 5.0.0.
> doi:10.4232/1.14320

### Eurobarometer — deferred, and probably unnecessary

Eurobarometer was in the plan to supply the science and education spheres. Given that D1×science and
D2×science are **empty cells** and science is demoted to a D3-only domain
(`design/DECISIONS.md` §3), the Eurobarometer requirement is much reduced. Do not spend author time
on GESIS Eurobarometer registration until the item table is frozen and it is clear whether anything
still depends on it.

---

## 4. Country coverage — confirmed 2026-08-10 from the files

**Primary sample (Joint EVS/WVS ZA7505 v5.0.0), 40 European countries, 78,396 respondents:**

AD AL AM AT AZ BA BG BY CH CY CZ DE DK EE ES FI FR GB GE GR HR HU IS IT LT LV ME MK NIR NL NO PL PT
RO RS RU SE SI SK UA

Notes on the list, all of which are pre-registration decisions rather than post-hoc ones:
**NIR** (Northern Ireland) is carried separately from **GB**; **AM, AZ and GE** are included only on a
generous definition of Europe; **CY is recommended for exclusion** from the primary model for the
data-quality reasons in `docs/design/item-table-v2-joint-names.md` §0.3, leaving **39**.

**Replication sample (ESS):** R9 = 29 countries, R10 = 22, R11 = 30.

Both comfortably clear the pre-registered ≥20-country threshold for retaining a sphere in
cross-national comparison. The plan's working assumption of "~30 countries" understated the primary
sample.
