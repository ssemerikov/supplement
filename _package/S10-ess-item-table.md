# ESS replication item table — FROZEN 2026-09-08, before any ESS model was fitted

**This table is NOT registered.** The pre-registration (`preregistration.md` §4.2) commits to "an
independent replication of model structure, not of parameter values, for the politics and morality
spheres only" and **names no ESS items**. The only ESS variables in the filed text are `ipcrtiva`
and `impricha`, cited as examples of ESS11's `a` suffix. The mapping below is taken from
`docs/design/measurement-design.md`, which was last modified 2026-08-10 10:50:43 UTC — *after* the
registration was filed at 07:45:39 UTC and after the analytic gate cleared at 09:11:17 UTC.

Consequently the ESS analysis **cannot be reported as the registered replication** and is reported
as an unregistered exploratory replication. This file exists so that the item selection is fixed,
hashed and timestamped *before* any ESS model is estimated, which is the strongest guarantee still
available once a registered one is not.

## Selection rules, fixed here and applied mechanically

1. **Politics and morality spheres only** — as registered. Drops `stfedu` (D3-E2, Education).
2. **Present in all three rounds** — a cross-round replication cannot use single-round items.
   Drops six ESS9-only items: `frprtpl` (D1-P7), `sofrpr` (D2-P1), `sofrwrk` (D2-P2),
   `sofrdst` (D2-P3), `gvintcz` (D3-P11), `poltran` (D3-P12).
3. **No item is added, and none is dropped for fit.** The rules above are the only filters.
4. **ESS11 `a` suffix.** All 14 PVQ items appear bare in ESS9/10 and `a`-suffixed in ESS11
   (`ipcrtiv` → `ipcrtiva`). Verified against the three `.sav` files, and consistent with the
   registered note at `preregistration.md:123`. Non-PVQ items carry no suffix in any round.

## Keying, fixed here

Verified from the `.sav` value labels, not assumed:

- **PVQ items, 1–6**, `1 = "Very much like me"` … `6 = "Not like me at all"` — **descending** in the
  named content. Missing: 7, 8, 9.
- **Agree/disagree items, 1–5**, `1 = "Agree strongly"` … `5 = "Disagree strongly"` — **descending**.
  Missing: 7, 8, 9.
- **Trust items, 0–10**, `0 = "No trust at all"` … `10 = "Complete trust"` — **ascending**.

The transformation is mechanical: `flip = descending XOR reverse_keyed`, where `reverse_keyed` is
the `R` marker carried over from `measurement-design.md`. Factor sign is arbitrary under
`std.lv = TRUE`, so only *within-dimension relative* keying affects the model; the rule is stated in
full anyway so it cannot be adjusted later.

## The table — 20 items

| ID | Dim | Sphere | Variable | ESS11 name | Scale | R | Net flip |
|---|---|---|---|---|---|---|---|
| D1-P5  | D1 | Politics | `freehms` | `freehms` | 1–5 desc | — | yes |
| D1-P6  | D1 | Politics | `hmsacld` | `hmsacld` | 1–5 desc | — | yes |
| D1-M6  | D1 | Morality | `impfree` | `impfreea` | 1–6 desc | — | yes |
| D1-M7  | D1 | Morality | `ipcrtiv` | `ipcrtiva` | 1–6 desc | — | yes |
| D1-M8  | D1 | Morality | `ipfrule` | `ipfrulea` | 1–6 desc | R | no |
| D1-M9  | D1 | Morality | `imptrad` | `imptrada` | 1–6 desc | R | no |
| D1-M10 | D1 | Morality | `ipbhprp` | `ipbhprpa` | 1–6 desc | R | no |
| D2-P4  | D2 | Politics | `gincdif` | `gincdif`  | 1–5 desc | — | yes |
| D2-M1  | D2 | Morality | `iphlppl` | `iphlppla` | 1–6 desc | — | yes |
| D2-M2  | D2 | Morality | `ipudrst` | `ipudrsta` | 1–6 desc | — | yes |
| D2-M3  | D2 | Morality | `ipeqopt` | `ipeqopta` | 1–6 desc | — | yes |
| D2-M4  | D2 | Morality | `impenv`  | `impenva`  | 1–6 desc | — | yes |
| D2-M5  | D2 | Morality | `iplylfr` | `iplylfra` | 1–6 desc | — | yes |
| D2-M6  | D2 | Morality | `imprich` | `impricha` | 1–6 desc | R | no |
| D2-M7  | D2 | Morality | `ipsuces` | `ipsucesa` | 1–6 desc | R | no |
| D2-M8  | D2 | Morality | `ipshabt` | `ipshabta` | 1–6 desc | R | no |
| D2-M9  | D2 | Morality | `iprspot` | `iprspota` | 1–6 desc | R | no |
| D3-P9  | D3 | Politics | `trstprl` | `trstprl`  | 0–10 asc | — | no |
| D3-P10 | D3 | Politics | `trstlgl` | `trstlgl`  | 0–10 asc | — | no |
| D3-M2  | D3 | Morality | `trstplc` | `trstplc`  | 0–10 asc | — | no |

**D1 = 7, D2 = 10, D3 = 3.**

## What this table cannot support, stated before fitting

- **D3 has exactly three indicators**, the bare identification minimum, and all three are
  institutional-trust items. It carries none of the anti-institutional-personalism content
  (strong-leader preference, confidence in persons over rules) that D3 is defined by in the primary
  model. The ESS D3 is therefore **a narrower construct than the paper's D3**, and a structural
  replication of it is weak evidence about the paper's third dimension. This is a property of the
  ESS instrument, not a choice, and it must be reported as a limitation rather than smoothed over.
- **No education and no science sphere** — as registered, and in any case unavailable.
- **Parameter values are not comparable** to the primary model: disjoint respondents, different
  items, different response formats. Only model *structure* replicates, exactly as registered.
