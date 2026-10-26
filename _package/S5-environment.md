# Analysis environment — verified executable, 2026-08-09

`CLAUDE.md`, `README.md` and `plan-C…md` all state that `lavaan`, `sirt` and `semTools` are absent
and that alignment optimisation "has no ready implementation here". **That was true of the default R
library and is now false.** All three are installed and the paper's full analysis chain has been run
end to end on simulated data.

## What was done

The site library (`/usr/lib/R/site-library`) is root-owned and unwritable by this user, which is why
the packages appeared to be missing. A **user library** works fine, and the toolchain to build from
source (`gcc`, `g++`, `gfortran`, `make`) is present.

```r
install.packages(c("lavaan","semTools","RcppArmadillo","sirt"),
                 lib = "~/R/x86_64-pc-linux-gnu-library/4.6",
                 repos = "https://cloud.r-project.org")
```

`sirt` needs `RcppArmadillo` → `CDM` → `pbv` → `TAM`; installing `RcppArmadillo` first unblocks the
whole chain. Total build time a few minutes.

## Installed and confirmed loading

| Package | Version | Provides |
|---|---|---|
| `lavaan` | 0.7.2 | multi-group CFA with mean structure, ordinal estimators, LRT |
| `semTools` | 0.5.9 | `measEq.syntax()` for ordinal invariance, `permuteMeasEq()` for partial invariance |
| `sirt` | 4.2.133 | **`invariance.alignment()`** — the alignment optimisation the plan depends on |
| `RcppArmadillo` | 15.4.2.1 | build dependency |
| `psych`, `GPArotation` | — | EFA support |

Neither `lavaan` nor `semTools` exposes any alignment function — `sirt::invariance.alignment` is the
only route, which is why unblocking `sirt` mattered.

## Smoke test — the actual analysis chain, executed

20 simulated groups × n = 300, two correlated factors, six indicators, with non-invariance
deliberately injected into groups 1–2 (one loading pushed .75 → .35, one intercept 0 → .8).

**Step 1–3: MGCFA invariance ladder** (`lavaan::cfa` with `group.equal=`)

| Model | CFI | RMSEA | χ² | df |
|---|---|---|---|---|
| configural | 1.000 | 0.006 | 161.9 | 160 |
| metric | 0.993 | 0.035 | 323.8 | 236 |
| scalar | 0.958 | 0.075 | 842.4 | 312 |

LRT metric vs scalar: Δχ² = 518.65, Δdf = 76, *p* < 2.2e-16 — **scalar invariance rejected**, which
is exactly the outcome the plan predicts for ~30 real countries.

**Step 4: alignment optimisation** (`sirt::invariance.alignment`) ran on the group-wise loading and
intercept matrices and returned:

- R² absorbed: **loadings 0.984**, **intercepts 0.213** (the low intercept R² correctly reflects the
  injected intercept non-invariance)
- `lambda.resid` isolated the non-invariance in groups 1–2, recovering the injected perturbation
- aligned group means (`pars$alpha0`) and variances (`pars$psi0`) produced for all 20 groups

**Result object gotcha:** the effect-size field is `al$es.invariance`, **not** `es0.invariance`.
Fields available: `pars` (alpha0, psi0), `lambda.aligned`, `nu.aligned`, `lambda.resid`, `nu.resid`,
`es.invariance` (R2 / sqrtU2 / rbar), plus jackknife SEs (`LEjk`, `TEjk`).

Scripts: `smoke_align.R`, `align2.R` in the session scratchpad — to be moved into `supplement/` and
re-run from clean before any claim about the real data.

## What this changes for the plan

- §5's invariance strategy is **fully executable in R**, as originally written. It does not need to
  be rebuilt in Python.
- The plan's warning that alignment "has no ready implementation here, so budget for it" is
  discharged.
- The separate finding that **`semopy` cannot test metric or scalar invariance** (no mean structure;
  `semopy.multigroup` fits each group separately with no cross-group constraints and no pooled fit
  statistic) no longer blocks anything, since R is available. Do not use semopy for the invariance
  work.

## Still missing

`mirt` failed to build (via `splines2`/`dcurver`) and was not pursued — nothing in the plan needs it.
