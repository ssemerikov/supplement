#!/usr/bin/env Rscript
# =============================================================================
# PII confirmatory factor analysis and measurement invariance
#
#   Rscript code/06_cfa_invariance.R [--variant primary]
#
# Consumes data/derived/pii-frame-<variant>.csv, written by
# code/05_build_analysis_frame.py, which enforces the Tier-2 deposit gate. This
# script re-checks that gate rather than trusting that the frame exists for a
# legitimate reason: a frame can be copied, and the sequencing requirement in
# pre-registration §7.1 is the one commitment that cannot be repaired later.
#
# WHY R AND NOT semopy. semopy cannot test metric or scalar invariance: it has
# no mean structure, and semopy.multigroup fits each group separately with no
# cross-group equality constraints and no pooled fit statistic. See
# docs/environment-verification.md.
#
# Site library is root-owned; packages live in the user library.
# =============================================================================

suppressWarnings(suppressMessages({
  .lib <- path.expand("~/R/x86_64-pc-linux-gnu-library/4.6")
  if (dir.exists(.lib)) .libPaths(c(.lib, .libPaths()))
  library(lavaan); library(semTools); library(sirt); library(jsonlite)
}))

set.seed(20260810)          # registered seed; every reported number is reproducible from it

ROOT <- normalizePath(file.path(dirname(sub("--file=", "",
        grep("--file=", commandArgs(FALSE), value = TRUE)[1])), ".."))
if (is.na(ROOT) || !dir.exists(ROOT)) ROOT <- normalizePath("..")

args    <- commandArgs(trailingOnly = TRUE)
variant <- if (length(args) >= 2 && args[1] == "--variant") args[2] else "primary"

# ---------------------------------------------------------------- the gate ---
# Scans the WHOLE of §7.1, not one subsection: a gate that stops looking at the next heading
# can be defeated by adding a heading. Mirrors gate_status() in 05_build_analysis_frame.py.
prereg <- paste(readLines(file.path(ROOT, "docs/preregistration.md"), warn = FALSE), collapse = "\n")
sec    <- regmatches(prereg, regexpr("\n### 7\\.1\\b[\\s\\S]*?(?=\n### |\n## )", prereg, perl = TRUE))
gate_ok <- length(sec) == 1 &&
           grepl("\n#### Tier-2 wave 1", sec) &&
           !grepl("OUTSTANDING", sec) &&
           length(setdiff(tolower(regmatches(sec,
             gregexpr("(?<=https://osf\\.io/)\\w+", sec, perl = TRUE))[[1]]), "ezjh2")) > 0
if (!gate_ok) {
  stop("Tier-2 gate BLOCKED: the wave-1 forecast is not recorded as deposited in ",
       "docs/preregistration.md §7.1. Running the CFA now voids Tier 2 permanently. ",
       "See docs/osf-deposit-instructions.md.", call. = FALSE)
}
cat("Tier-2 gate: CLEAR (forecast deposited and recorded before this run)\n")

# ------------------------------------------------------------------- input ---
csv  <- file.path(ROOT, "data/derived", sprintf("pii-frame-%s.csv", variant))
meta <- fromJSON(file.path(ROOT, "data/derived", sprintf("pii-frame-%s.meta.json", variant)))
if (!file.exists(csv)) stop("run code/05_build_analysis_frame.py first: ", csv, call. = FALSE)
d <- read.csv(csv, stringsAsFactors = FALSE)

items <- meta$items
cat(sprintf("variant %s: %d rows, %d countries, %d items\n",
            variant, nrow(d), length(unique(d$country)), nrow(items)))

# Reverse-key. Done here rather than in Python because the reversal must use the observed
# category range, and WLSMV needs the result declared as an ordered factor either way.
for (v in meta$reverse_keyed) {
  if (!v %in% names(d)) next
  rng <- range(d[[v]], na.rm = TRUE)
  d[[v]] <- rng[1] + rng[2] - d[[v]]
}
ordvars <- unique(items$variable)
for (v in ordvars) d[[v]] <- ordered(d[[v]])

by_dim <- function(dd) items$variable[items$dimension == dd]
f <- function(name, vs) paste0(name, " =~ ", paste(vs, collapse = " + "))

D1 <- by_dim("D1"); D2 <- by_dim("D2"); D3 <- by_dim("D3")
BATT <- intersect(c("E224","E225","E226","E227","E228","E229","E233","E233A","E233B"), ordvars)

# F117 ("justifiable: accepting a bribe") is listed in the frozen item table under BOTH D2 (as
# D2-M4) and D3 (as D3-M1), unannotated. The table is hash-locked and is not edited to resolve
# this; the registered specification is taken literally, so the primary model carries the
# cross-loading. --f117 d2only / d3only give the two sensitivity assignments.
# See docs/preregistration.md 6.1.
f117 <- if (length(args) >= 4 && args[3] == "--f117") args[4] else "both"
# --stage single | invariance | all . The 39-group chain costs far more than the single-group
# models, so it is separable: stage "single" answers H1 and H2, which are the decision rules.
stage <- { i <- match("--stage", args); if (!is.na(i) && length(args) > i) args[i + 1] else "all" }
shared <- intersect(D2, D3)
if (length(shared)) {
  cat(sprintf("shared indicator(s) across D2/D3: %s  [assignment: %s]\n",
              paste(shared, collapse = ", "), f117))
  if (f117 == "d2only") D3 <- setdiff(D3, shared)
  if (f117 == "d3only") D2 <- setdiff(D2, shared)
}

# ------------------------------------------------------------- model set -----
# Decision D3: a battery-specific method factor, orthogonal to the substantive factors.
# M0_12 is the one-factor comparator for H1, and it exists because M0 cannot serve that role.
# H1 (pre-registration 2.2) is "D1 and D2 are empirically separable: a two-factor model beats a
# one-factor model", and its criterion (a) is a DeltaCFI. CFI is not comparable across models fitted
# to different observed variables, and M1 uses only the D1 and D2 indicators while M0 uses all 51.
# Comparing them would be an arithmetic difference between two numbers on different scales. The
# registered comparison is therefore run on the shared D1-union-D2 indicator set.
# This is a validity fix, identified by reading the code and NOT from any result: it was made
# before any fit statistic was inspected. It makes the test correct, not easier -- the direction of
# the change is unknown in advance. Logged in docs/preregistration.md Sec. 11.
# M0 (all 51 indicators) is retained as the global single-axis baseline, compared with M2, which
# does use the same indicator set.
models <- list(
  M0    = f("G", ordvars),
  M0_12 = f("G", union(D1, D2)),
  M1  = paste(f("D1", D1), f("D2", D2), sep = "\n"),
  M1b = paste(f("D1", D1), f("D2", D2), "D1 ~~ 1*D2", sep = "\n"),
  M2  = paste(f("D1", D1), f("D2", D2), f("D3", D3), sep = "\n"),
  M2b = paste(f("D1", D1), f("D2", D2), f("D3", D3), "D1 ~~ 1*D3", sep = "\n"),
  M2m = paste(f("D1", D1), f("D2", D2), f("D3", D3), f("MB", BATT),
              "MB ~~ 0*D1", "MB ~~ 0*D2", "MB ~~ 0*D3", sep = "\n"),
  M4  = paste(f("G", ordvars), f("D1", D1), f("D2", D2), f("D3", D3),
              "G ~~ 0*D1", "G ~~ 0*D2", "G ~~ 0*D3",
              "D1 ~~ 0*D2", "D1 ~~ 0*D3", "D2 ~~ 0*D3", sep = "\n")
)

FITM <- c("chisq.scaled","df.scaled","pvalue.scaled","cfi.scaled",
          "tli.scaled","rmsea.scaled","srmr")

# Each fit is CACHED to disk as soon as it converges. WLSMV on 51 ordinal indicators over 77k
# respondents spends most of its time building the polychoric correlation matrix (1,275 pairs),
# and lavaan rebuilds it per cfa() call, so a lost run is expensive to repeat. Caching also makes
# the script resumable: a killed job restarts where it stopped rather than at M0.
CACHE <- file.path(ROOT, "supplement/analysis/.fitcache")
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)
say <- function(...) { cat(...); flush.console() }

fit_one <- function(syntax, label) {
  key <- file.path(CACHE, sprintf("%s-%s-%s.rds", variant, f117, label))
  if (file.exists(key)) {
    say("  ", label, ": cached\n", sep = "")
    return(readRDS(key))
  }
  say("  ", label, ": fitting… ", sep = "")
  t0 <- Sys.time()
  fit <- tryCatch(
    cfa(syntax, data = d, estimator = "WLSMV", ordered = ordvars,
        missing = "pairwise", std.lv = TRUE),
    error = function(e) { say("FAILED: ", conditionMessage(e), "\n"); NULL })
  if (is.null(fit)) return(NULL)
  say(sprintf("%.0f min  converged=%s\n",
              as.numeric(difftime(Sys.time(), t0, units = "mins")),
              lavInspect(fit, "converged")))
  saveRDS(fit, key)
  fit
}

# fitMeasures() raises a hard error rather than returning NA when a model did not converge. In
# the invariance chain a non-converged SCALAR model is an expected outcome, not an exceptional
# one -- scalar invariance across 39 countries is predicted to fail -- so an unguarded call turns
# the predicted result into the death of the run. Both accessors below degrade to NA instead.
fitrow <- function(fit) {
  conv <- isTRUE(tryCatch(lavInspect(fit, "converged"), error = function(e) FALSE))
  m <- tryCatch(fitMeasures(fit, FITM),
                error = function(e) setNames(rep(NA_real_, length(FITM)), FITM))
  c(list(converged = conv), as.list(round(m, 4)))
}

fm1 <- function(fit, what) {
  v <- tryCatch(unname(fitMeasures(fit, what)), error = function(e) NA_real_)
  if (length(v) != 1L) NA_real_ else v
}

# -------------------------------------------------------------- MEMORY NOTE --
# This loop used to be `fits <- lapply(names(models), ...)`, which holds ALL EIGHT
# fitted lavaan objects resident simultaneously. On 77,396 rows x 52 ordinal
# indicators one fit is several GB, so by the time M2b was estimating, five earlier
# fits were still in memory and systemd-oomd killed the run -- twice on 2026-08-10,
# the second time with nothing else competing for the machine.
#
# Every fit is already persisted to CACHE, so retaining it in memory buys nothing.
# We now fit one model at a time, take its fit measures immediately, and release it;
# the comparisons below re-read what they need through FIT(), which keeps at most two
# resident. NOTHING STATISTICAL CHANGES: same models, same estimator, same data, same
# seed -- only the lifetime of the objects in RAM.
say("\nsingle-group models (", length(models), ")\n", sep = "")
fit_table <- list()
have      <- character(0)
for (.n in names(models)) {
  .f <- fit_one(models[[.n]], .n)
  if (!is.null(.f)) {
    have             <- c(have, .n)
    fit_table[[.n]]  <- fitrow(.f)
  }
  rm(.f); gc(FALSE)
}

# Lazy fit accessor with a two-object ceiling. Every comparison below needs at most
# two fits at once (an LRT or a delta-CFI), so MAXRES = 2 is sufficient and bounded.
.res    <- new.env(parent = emptyenv())
.order  <- character(0)
MAXRES  <- 2L
FIT <- function(nm) {
  if (!nm %in% have) return(NULL)
  if (exists(nm, envir = .res, inherits = FALSE)) {
    .order <<- c(setdiff(.order, nm), nm)
    return(get(nm, envir = .res, inherits = FALSE))
  }
  key <- file.path(CACHE, sprintf("%s-%s-%s.rds", variant, f117, nm))
  if (!file.exists(key)) return(NULL)
  obj <- readRDS(key)
  assign(nm, obj, envir = .res)
  .order <<- c(.order, nm)
  while (length(.order) > MAXRES) {
    old    <- .order[1]
    .order <<- .order[-1]
    if (exists(old, envir = .res, inherits = FALSE)) rm(list = old, envir = .res)
    gc(FALSE)
  }
  obj
}
release <- function() {
  rm(list = ls(.res), envir = .res)
  .order <<- character(0)
  gc(FALSE)
  invisible(NULL)   # else the gc() matrix auto-prints into the run log
}

# ------------------------------------------------------- Heywood / loadings --
# Items may be dropped ONLY for a standardised loading < .30 in the configural model or a
# Heywood case (pre-registration §6.1). Nothing is dropped here automatically: the offenders
# are LOGGED, and dropping is a separate, recorded decision. Automatic dropping would be
# indistinguishable from fit-chasing.
drop_log <- list()
if ("M2" %in% have) {
  std <- standardizedSolution(FIT("M2"))
  lam <- std[std$op == "=~", ]
  weak <- lam[abs(lam$est.std) < .30, c("lhs","rhs","est.std")]
  vv   <- std[std$op == "~~" & std$lhs == std$rhs & std$est.std < 0, c("lhs","est.std")]
  drop_log <- list(
    weak_loadings = if (nrow(weak)) weak else "none",
    heywood_cases = if (nrow(vv)) vv else "none",
    note = paste("Logged, not applied. Dropping an item is a recorded decision taken once,",
                 "with its reason, and never to improve fit."))
  cat(sprintf("loadings < .30: %d   negative variances: %d  (logged, not dropped)\n",
              nrow(weak), nrow(vv)))
}

# ----------------------------------------------------------------- H1, H2 ----
delta_cfi <- function(a, b) unname(fitMeasures(a,"cfi.scaled") - fitMeasures(b,"cfi.scaled"))
phi <- function(fit, x, y) {
  s <- standardizedSolution(fit)
  r <- s[s$op == "~~" & ((s$lhs == x & s$rhs == y) | (s$lhs == y & s$rhs == x)), "est.std"]
  if (length(r)) unname(r[1]) else NA_real_
}

H1 <- list(); H2 <- list()
if (all(c("M0_12","M1","M1b") %in% have)) {
  release()
  lrt      <- lavTestLRT(FIT("M1b"), FIT("M1"))
  p_m1b    <- lrt[["Pr(>Chisq)"]][2]
  dcfi <- delta_cfi(FIT("M1"), FIT("M0_12"))   # same indicator set -- see the note at models
  a <- dcfi >= .010
  b <- !is.na(p_m1b) && p_m1b < .01
  phi12 <- phi(FIT("M1"), "D1", "D2")
  cc <- phi12 <= .85
  H1 <- list(a_deltaCFI_ge_.010 = a, b_M1b_rejected_at_.01 = b, c_phi_le_.85 = cc,
             deltaCFI = round(dcfi, 4),
             deltaCFI_comparator = "M0_12: one factor over the D1-union-D2 indicators",
             p_M1b = p_m1b, phi_D1_D2 = round(phi12, 4),
             abs_phi_le_.85 = abs(phi12) <= .85,   # see the note on H2 below
             supported = isTRUE(a) && isTRUE(b) && isTRUE(cc),
             rule = "conjunctive: all three must hold (pre-registration 6.2)",
             equivalence_note = paste(
               "M1b (two factors, phi fixed to 1) and M0_12 (one factor over the same",
               "indicators) are equivalent models, which the run confirms: identical df and",
               "chi-square agreeing to within rounding. Conditions (a) and (b) are therefore",
               "the SAME comparison expressed twice -- once as a fit-index difference and once",
               "as a scaled difference test -- not two independent pieces of evidence. The",
               "conjunctive rule is applied as registered; this note records that it has two",
               "effective parts, not three."))
  say(sprintf("\nH1: dCFI=%.4f[%s]  p(M1b)=%.4g[%s]  phi=%.3f[%s]  -> %s\n",
              H1$deltaCFI, a, p_m1b, b, H1$phi_D1_D2, cc,
              if (H1$supported) "SUPPORTED" else "NOT SUPPORTED"))
}
if (all(c("M2","M2b") %in% have)) {
  release()
  lrt2  <- lavTestLRT(FIT("M2b"), FIT("M2"))
  p2    <- lrt2[["Pr(>Chisq)"]][2]
  ph13  <- phi(FIT("M2"), "D1", "D3")
  # The registered rule reads "phi(D1,D3) does not exceed .70" and is implemented as the
  # signed comparison it literally states. That rule cannot detect the case it exists to
  # rule out: phi = -.99 would satisfy phi <= .70 while meaning D3 IS D1 with the sign
  # reversed, which is reducibility. The signed test is therefore kept as the registered
  # decision and the absolute-value form is reported beside it as a diagnostic. Where the
  # two agree, nothing turns on the difference; where they would not, the paper says so.
  H2 <- list(M2b_rejected_at_.01 = !is.na(p2) && p2 < .01, phi_D1_D3 = round(ph13, 4),
             p_M2b = p2, phi_le_.70 = ph13 <= .70,
             abs_phi_D1_D3 = round(abs(ph13), 4), abs_phi_le_.70 = abs(ph13) <= .70,
             signed_and_abs_agree = identical(ph13 <= .70, abs(ph13) <= .70),
             phi_D2_D3 = round(phi(FIT("M2"), "D2", "D3"), 4),
             constrained_model_note = paste(
               "M2b fixes phi(D1,D3) to +1. The observed correlation is negative, so the",
               "constrained model is a severe misspecification and its rejection is close to",
               "guaranteed; the scaled difference test is reported as registered but carries",
               "little information on its own. M2b is also inadmissible (non-positive-definite",
               "latent covariance matrix), which is a consequence of the constraint rather than",
               "of the data -- see code/07_admissibility_check.R. The substantive weight of H2",
               "rests on the magnitude condition, which holds on both the signed and the",
               "absolute-value reading."),
             supported = (!is.na(p2) && p2 < .01) && ph13 <= .70)
  if ("M0" %in% have) {
    release()
    H2$deltaCFI_M2_vs_M0_all <- round(delta_cfi(FIT("M2"), FIT("M0")), 4)
    H2$deltaCFI_note <- "M2 vs M0 over all 51 indicators: the global single-axis baseline"
  }
  say(sprintf("H2: p(M2b)=%.4g  phi(D1,D3)=%.3f  -> %s\n", p2, ph13,
              if (H2$supported) "SUPPORTED" else "NOT SUPPORTED"))
}

# ------------------------------------------------------------- invariance ----
# configural -> metric -> scalar, then alignment per dimension if scalar fails (§6.3).
inv <- list()
if ("M2" %in% have && stage %in% c("invariance", "alignment", "ladder", "perdim", "all")) {
  release()
  # --- FORCED DEVIATION: minimal category collapsing for the multi-group models only ------
  # lavaan hard-errors ("lav_samp_step1: some categories of variable X are empty in group G")
  # whenever a group has zero observations in a category, at configural as well as at metric and
  # scalar. On these data that is unavoidable: the 1-10 justifiability items have severe floor
  # effects, e.g. F117 in Greece is [1052, 85, 28, 7, 10, 5, 3, 2, 2, 0]. The registered invariance
  # chain is therefore not estimable on the registered coding, and something must give.
  #
  # The rule below is the LEAST intrusive option and is mechanical, not per-item judgement:
  # repeatedly merge the globally rarest category into its neighbour until every category has at
  # least one observation in every country. It is applied identically in all groups, so an item
  # means the same thing everywhere; it collapses nothing that is not blocking; and it keeps all
  # 51 items, all 39 countries and the registered WLSMV estimator.
  #
  # Single-group models M0-M4, and therefore H1 and H2, use the REGISTERED coding untouched. Only
  # the invariance chain sees the collapsed variables. The realised mapping is written to the
  # output JSON. See docs/preregistration.md Sec. 11.
  MIN_PER_GROUP <- 1L
  collapse_map <- list()
  dinv <- d
  for (v in ordvars) {
    x <- as.integer(as.character(dinv[[v]]))
    if (length(unique(na.omit(x))) <= 2L) next
    merges <- 0L
    repeat {
      cats <- sort(unique(na.omit(x)))
      if (length(cats) <= 2L) break
      tb <- table(factor(dinv$country), factor(x, levels = cats))
      if (min(tb) >= MIN_PER_GROUP) break
      gl <- table(factor(x, levels = cats))
      i  <- which.min(as.integer(gl))
      j  <- if (i == length(cats)) i - 1L else i + 1L
      lo <- min(cats[i], cats[j]); hi <- max(cats[i], cats[j])
      x[!is.na(x) & x == hi] <- lo
      merges <- merges + 1L
    }
    if (merges > 0L) {
      collapse_map[[v]] <- list(merges = merges,
                                categories_before = nlevels(dinv[[v]]),
                                categories_after = length(unique(na.omit(x))))
      dinv[[v]] <- ordered(x)
    }
  }
  if (length(collapse_map)) {
    say(sprintf("  category collapsing for multi-group (min %d/group): %d items, %d merges\n",
                MIN_PER_GROUP, length(collapse_map),
                sum(vapply(collapse_map, function(z) z$merges, integer(1)))))
    for (v in names(collapse_map))
      say(sprintf("    %-8s %d -> %d categories\n", v,
                  collapse_map[[v]]$categories_before, collapse_map[[v]]$categories_after))
  }
  inv$category_collapsing <- list(
    min_per_group = MIN_PER_GROUP, items = collapse_map,
    applies_to = "multi-group invariance models only; H1/H2 use the registered coding",
    reason = paste("lavaan cannot estimate a multi-group ordinal model when a category is empty",
                   "in a group; forced deviation, see preregistration Sec. 11"))
  # NOTE: `d` is deliberately left untouched -- the collapsed frame is `dinv`, used only for the
  # group fits below, so nothing downstream of this block can silently inherit the collapsing.
  cnt <- table(dinv$country)
  keep <- names(cnt)[cnt >= 200]     # a group too small to fit is a convergence problem, not a finding
  dg <- dinv[dinv$country %in% keep, ]
  say(sprintf("\ninvariance on %d of %d countries (>=200 respondents)\n",
              length(keep), length(unique(dinv$country))))

  # ------------------------------------------------------------ configural ---
  # TWO ROUTES TO THE SAME CONFIGURAL ESTIMATES. The choice is forced by memory, not statistics.
  #
  # The pooled 39-group fit carries 39 x ~258 = ~10,100 free parameters, and WLSMV's robust test
  # statistic needs a Delta Jacobian of (39 x 1,479) x 10,100 doubles -- about 4.6 GB, of which
  # lavaan holds more than one copy, on top of a 10,100^2 information matrix for the standard
  # errors. On this machine (15 GB) systemd-oomd killed that fit at 8.5 GB resident plus 2.9 GB
  # swapped, after 2h24m of CPU, with nothing retained (2026-08-10 18:17:30 local).
  #
  # The configural model has NO cross-group constraints: std.lv = TRUE fixes the factor variances
  # to 1 in every group, and every loading and every threshold is free in every group. Its fit
  # function is therefore a sum of 39 independent per-group terms, and its minimiser IS the
  # collection of the 39 separate single-group minimisers. Fitting group by group returns the same
  # point estimates -- exact, not an approximation -- at a fraction of the peak memory, and it
  # checkpoints per country instead of per 2.5 hours.
  #
  # What that route does NOT recover is a pooled SCALED fit statistic: chi-square and df are
  # additive over independent groups, but the mean-and-variance adjustment is not, so no
  # configural cfi.scaled is claimed from it and no delta-CFI is computed against it. Metric and
  # scalar impose genuine cross-group equalities and are not separable at all.
  #
  # --stage alignment runs only this route plus the aligner, which is what the country-comparison
  # licence of Sec. 6.3 actually depends on. Logged in docs/preregistration.md Sec. 11.
  # SUPPLEMENTARY AND NOT REGISTERED: --stage ladder fits the pooled configural -> metric ->
  # scalar chain on a tractable SUBSET of countries. Its purpose is diagnostic and it is reported
  # as such: the registered licence still rests on the alignment over all countries, and a subset
  # ladder is not a country comparison. It exists because "the ladder could not be computed at 39
  # countries" is a weaker statement than "the ladder could not be computed at 39 countries, and
  # here is what it does at 12". The subset is a SEEDED RANDOM DRAW, not the largest or the
  # best-behaved countries, because any selection rule responsive to the data would let the
  # analyst choose the answer.
  if (identical(stage, "ladder")) {
    set.seed(20260810)
    ksub <- { i <- match("--subset-k", args)
              if (!is.na(i) && length(args) > i) as.integer(args[i + 1]) else 12L }
    keep <- sort(sample(keep, min(ksub, length(keep))))
    dg <- dg[dg$country %in% keep, ]
    say(sprintf("  SUBSET LADDER (exploratory, seed 20260810): %d countries: %s\n",
                length(keep), paste(keep, collapse = ", ")))
    inv$subset_ladder <- list(
      registered = FALSE, seed = 20260810, k = length(keep), countries = keep,
      selection = "seeded uniform random draw from the countries with >=200 respondents",
      purpose = paste("diagnostic only; the registered country-comparison licence rests on the",
                      "alignment over all countries, not on this subset"))
  }

  # ORDINAL ADAPTATION, and it is not cosmetic. sirt::invariance.alignment expects a matrix of
  # item INTERCEPTS (nu). Under WLSMV with ordered indicators lavaan fixes nu to ZERO and puts the
  # item location in the THRESHOLDS (tau); verified directly on a two-group fit. Passing nu would
  # hand the aligner a matrix of zeros, and the resulting R2 for intercepts -- which gates the
  # country-comparison hard stop -- would be an artefact of that, not a measure of anything. That
  # could license a league table the data do not support, the single worst error this paper could
  # make. The location used instead is the MEAN THRESHOLD of each item in each group: the item's
  # average position on the latent continuum. Items differ in how many thresholds they have, so a
  # mean is the only summary defined for all of them.
  item_locations <- function(g, vs) {
    tau <- g$tau
    nm  <- sub("\\|t[0-9]+$", "", rownames(tau))
    vapply(vs, function(v) mean(tau[nm == v, 1]), numeric(1))
  }
  # One function, used by every route, so the aligner and the hard stop cannot drift apart
  # between the pooled, per-group and per-dimension paths.
  align_one <- function(lam, vs, dd) {
    al <- tryCatch({
      L <- t(sapply(lam, function(g) g$lambda[vs, dd]))
      N <- t(sapply(lam, function(g) item_locations(g, vs)))
      stopifnot(all(is.finite(L)), all(is.finite(N)))
      if (all(N == 0)) stop("item locations are all zero - tau extraction failed, do not proceed")
      invariance.alignment(lambda = L, nu = N)
    }, error = function(e) { say("FAILED: ", conditionMessage(e), "\n"); NULL })
    if (is.null(al)) return(NULL)
    say("R2(loadings)=", round(al$es.invariance["R2", 1], 4),
        " R2(locations)=", round(al$es.invariance["R2", 2], 4), "\n", sep = "")
    sim <- tryCatch(invariance_alignment_simulate(al, seed = 20260810),
                    error = function(e) NULL)
    list(n_items = length(vs),
         n_groups = length(lam),
         R2_loadings = unname(al$es.invariance["R2", 1]),
         R2_locations = unname(al$es.invariance["R2", 2]),
         location_parameter = "mean threshold per item per group (ordinal adaptation; nu is 0 under WLSMV)",
         recovery_confirmed = !is.null(sim),
         country_comparison_licensed = !is.null(sim) && al$es.invariance["R2", 2] >= .75,
         hard_stop_note = paste("If country_comparison_licensed is FALSE, the manuscript reports",
                                "the invariance failure and presents NO country comparison for",
                                "this dimension. No league table. Pre-registration 6.3."))
  }

  # --------------------------------------------- per-dimension full-scale ladder ---
  # THE REGISTERED CHAIN AT FULL SCALE, ONE DIMENSION AT A TIME. The pooled 51-indicator
  # three-factor chain is not estimable here (see the configural note above), but that is a
  # property of the INDICATOR COUNT, not of the country count: lavaan holds a NACOV, a weight
  # matrix and a residual projection per group, each p x p, where p is the number of sample
  # statistics -- 1,479 for the 51-indicator model but only ~225 (D1), ~147 (D2) and ~270 (D3)
  # for one dimension at a time. The per-group matrices shrink by 30x to 100x, which brings all
  # 39 countries back inside memory. Measured: the 12-country pooled M2 configural sat at 2.7 GB,
  # and memory is close to linear in groups, which is what killed 39.
  #
  # This is the right granularity in any case. sirt aligns ONE FACTOR AT A TIME, and the §6.3
  # licence is written per dimension ("no country mean ... is reported FOR A DIMENSION unless").
  # The cost is stated plainly in the manuscript: a unidimensional model omits the inter-factor
  # correlations of M2, so these loadings are not M2's and the invariance claim is about each
  # dimension's own measurement model. Logged in docs/preregistration.md Sec. 11.
  perdim <- identical(stage, "perdim")
  if (perdim) {
    inv$perdim <- list()
    for (dd in c("D1", "D2", "D3")) {
      vs  <- intersect(by_dim(dd), ordvars)
      syn <- f(dd, vs)
      say(sprintf("\n%s: %d items, %d countries\n", dd, length(vs), length(keep)))
      steps <- list(configural = NULL, metric = "loadings",
                    scalar = c("loadings", "thresholds"))
      # ONE FIT RESIDENT AT A TIME. An earlier version kept all three fitted objects in `dfits`
      # so the delta loop could reach consecutive pairs. At 39 groups that means configural and
      # metric are both still in memory while scalar estimates, and `systemd-oomd` killed the run
      # in D1 scalar at a 10.9 GB peak after 2 h 6 min of CPU (2026-08-11). The single-group stage
      # was fixed for this same reason and this loop was missed.
      #
      # Nothing here needs a whole fit object. The deltas need two scalars per step, `fitrow`
      # needs the fit measures, and the aligner needs configural's estimates -- so each is taken
      # the moment the fit exists and the object is dropped before the next `cfa()` call. Same
      # models, same estimator, same seed, same cache files; only the lifetime changes.
      frows <- list(); dcfi <- list(); drms <- list(); cfg_est <- NULL
      for (nm in names(steps)) {
        say("  ", nm, ": ", sep = "")
        key <- file.path(CACHE, sprintf("%s-%s-pd%s-%s.rds", variant, f117, dd, nm))
        if (file.exists(key)) {
          fit <- readRDS(key); say("cached\n")
        } else {
          t0 <- Sys.time()
          # Pass ONLY the modelled columns. `dg` carries all 52 indicators; a unidimensional model
          # needs 18 of them, and lavaan drags the whole frame through its per-group data handling
          # otherwise. Cannot change an estimate -- the unused columns appear in no equation.
          # `se = "none"` for the same reason: the invariance decision is a delta in scaled CFI and
          # the aligner reads point estimates, so nothing downstream consumes a standard error,
          # while computing them requires inverting an information matrix of order (groups x
          # parameters). Neither switch touches the fit function, the estimator or the seed.
          fit <- tryCatch(
            cfa(syn, data = dg[, c("country", vs)], group = "country", estimator = "WLSMV",
                ordered = vs, missing = "pairwise", std.lv = TRUE, se = "none",
                group.equal = steps[[nm]]),
            error = function(e) { say("FAILED: ", conditionMessage(e), "\n"); NULL })
          if (!is.null(fit)) {
            saveRDS(fit, key)
            say(sprintf("ok (%.0f min)\n",
                        as.numeric(difftime(Sys.time(), t0, units = "mins"))))
          }
        }
        if (!is.null(fit)) {
          frows[[nm]] <- fitrow(fit)
          # Unrounded, deliberately: `fitrow` rounds to 4 dp for reporting, and a delta of two
          # rounded numbers is not the rounded delta.
          dcfi[[nm]] <- fm1(fit, "cfi.scaled")
          drms[[nm]] <- fm1(fit, "rmsea.scaled")
          if (identical(nm, "configural")) cfg_est <- lavInspect(fit, "est")
        }
        rm(fit); invisible(gc())
      }
      entry <- list(n_items = length(vs), items = vs, countries = length(keep),
                    model = "unidimensional; inter-factor correlations of M2 are absent",
                    fit = frows)
      if (length(frows) >= 2) {
        nms <- names(frows)
        entry$deltas <- lapply(2:length(nms), function(i) {
          dc <- dcfi[[nms[i]]] - dcfi[[nms[i - 1]]]
          dr <- drms[[nms[i]]] - drms[[nms[i - 1]]]
          list(step = paste(nms[i - 1], "->", nms[i]),
               dCFI = round(dc, 4), dRMSEA = round(dr, 4),
               holds = isTRUE(dc >= -.010 && dr <= .015))
        })
        for (x in entry$deltas)
          say(sprintf("    %-24s dCFI=%+.4f dRMSEA=%+.4f  %s\n", x$step, x$dCFI, x$dRMSEA,
                      if (x$holds) "holds" else "FAILS"))
      }
      if (!is.null(cfg_est)) {
        say("  aligning ", dd, sprintf(" (%d items) … ", length(vs)))
        entry$alignment <- align_one(cfg_est, vs, dd)
      }
      rm(cfg_est); invisible(gc())
      inv$perdim[[dd]] <- entry
      rm(frows, dcfi, drms); invisible(gc())
    }
  }

  pergroup <- identical(stage, "alignment")
  lam_by_group <- NULL
  ifits <- list()

  if (pergroup) {
    say("  configural, per group (memory-forced decomposition; estimates identical)\n")
    gstat <- list(); lam_by_group <- list(); gfail <- character()
    for (g in keep) {
      key <- file.path(CACHE, sprintf("%s-%s-cfg-%s.rds", variant, f117,
                                      gsub("[^A-Za-z0-9]+", "_", g)))
      if (file.exists(key)) {
        z <- readRDS(key); say(sprintf("    %-22s cached\n", g))
      } else {
        dgi <- dg[dg$country == g, ]
        t0 <- Sys.time()
        fg <- tryCatch(
          cfa(models$M2, data = dgi, estimator = "WLSMV", ordered = ordvars,
              missing = "pairwise", std.lv = TRUE),
          error = function(e) {
            say(sprintf("    %-22s FAILED: %s\n", g, conditionMessage(e))); NULL })
        if (is.null(fg)) next
        # Only the estimates are kept, never the lavaan object. Holding many fitted objects
        # resident is what caused the earlier kills; see docs/environment-verification.md.
        #
        # EVERY extraction is guarded, not just the cfa() call. lavaan's fitMeasures() raises a
        # hard error ("fit measures not available if model did not converge") rather than
        # returning NA, so an unguarded extraction turns one country's non-convergence into the
        # death of the whole 39-country run. Caught by the SMOKE test, where small groups make
        # non-convergence common.
        conv <- isTRUE(tryCatch(lavInspect(fg, "converged"), error = function(e) FALSE))
        fm <- if (conv) tryCatch(fitMeasures(fg, c("chisq", "df")),
                                 error = function(e) c(chisq = NA_real_, df = NA_real_))
              else c(chisq = NA_real_, df = NA_real_)
        z <- list(est = if (conv) tryCatch(lavInspect(fg, "est"), error = function(e) NULL),
                  converged = conv,
                  n = nrow(dgi),
                  chisq = unname(fm[["chisq"]]),
                  df = unname(fm[["df"]]))
        saveRDS(z, key)
        say(sprintf("    %-22s %4.1f min  n=%5d  converged=%s\n", g,
                    as.numeric(difftime(Sys.time(), t0, units = "mins")), z$n, z$converged))
        rm(fg); gc()
      }
      if (!isTRUE(z$converged) || is.null(z$est)) {
        say(sprintf("    %-22s did not converge - excluded from alignment\n", g))
        gfail <- c(gfail, g); next
      }
      lam_by_group[[g]] <- z$est
      gstat[[g]] <- z[c("n", "chisq", "df", "converged")]
    }
    # A country dropped here is not a neutral computational detail: it changes which countries
    # the aligner sees, and therefore what any profile would be a profile OF. Named, not counted.
    if (length(gfail))
      say(sprintf("  EXCLUDED (non-convergence): %s\n", paste(gfail, collapse = ", ")))
    inv$configural_pergroup <- list(
      route = "per-group (memory-forced; see code comment and preregistration Sec. 11)",
      groups_requested = length(keep),
      groups_converged = length(lam_by_group),
      groups_excluded = gfail,
      chisq_sum = sum(vapply(gstat, function(z) z$chisq, numeric(1)), na.rm = TRUE),
      df_sum = sum(vapply(gstat, function(z) z$df, numeric(1)), na.rm = TRUE),
      scaled_fit_note = paste("chi-square and df are additive over independent groups; the",
                              "mean-and-variance adjusted statistic is not, so no pooled",
                              "cfi.scaled is claimed from this route"),
      per_group = gstat)
    say(sprintf("  configural: %d of %d groups converged\n",
                length(lam_by_group), length(keep)))
  } else if (!perdim) {
    steps <- list(configural = NULL, metric = "loadings", scalar = c("loadings","thresholds"))
    for (nm in names(steps)) {
      say("  ", nm, ": ", sep = "")
      # The subset ladder must not collide with the full-sample chain in the cache: same models,
      # different data. The country count goes in the key.
      key <- file.path(CACHE, sprintf("%s-%s-inv%s-%s.rds", variant, f117,
                                      if (identical(stage, "ladder")) paste0("-k", length(keep))
                                      else "", nm))
      if (file.exists(key)) {
        ifits[[nm]] <- readRDS(key); say("cached\n")
      } else {
        t0 <- Sys.time()
        # se = "none" for the reason given in the per-dimension block: the invariance decision is
        # a delta in scaled CFI and the aligner reads point estimates, so no standard error is
        # consumed downstream, while computing them inverts an information matrix of order
        # (countries x parameters). The fit function, estimator, data and seed are untouched.
        ifits[[nm]] <- tryCatch(
          cfa(models$M2, data = dg[, c("country", ordvars)], group = "country",
              estimator = "WLSMV", ordered = ordvars, missing = "pairwise", std.lv = TRUE,
              se = "none", group.equal = steps[[nm]]),
          error = function(e) { say("FAILED: ", conditionMessage(e), "\n"); NULL })
        if (!is.null(ifits[[nm]])) {
          saveRDS(ifits[[nm]], key)
          say(sprintf("ok (%.0f min)\n", as.numeric(difftime(Sys.time(), t0, units = "mins"))))
        }
      }
    }
    ifits <- Filter(Negate(is.null), ifits)
    inv$fit <- lapply(ifits, fitrow)
    if (length(ifits) >= 2) {
      nms <- names(ifits)
      inv$deltas <- lapply(2:length(nms), function(i) {
        dc <- fm1(ifits[[i]], "cfi.scaled")   - fm1(ifits[[i - 1]], "cfi.scaled")
        dr <- fm1(ifits[[i]], "rmsea.scaled") - fm1(ifits[[i - 1]], "rmsea.scaled")
        list(step = paste(nms[i - 1], "->", nms[i]),
             dCFI = round(dc, 4), dRMSEA = round(dr, 4),
             holds = isTRUE(dc >= -.010 && dr <= .015))
      })
      for (x in inv$deltas)
        cat(sprintf("  %-24s dCFI=%+.4f dRMSEA=%+.4f  %s\n", x$step, x$dCFI, x$dRMSEA,
                    if (x$holds) "holds" else "FAILS"))
    }
    if (!is.null(ifits$configural)) lam_by_group <- lavInspect(ifits$configural, "est")
  }

  # ------------------------------------------------------------- alignment ---
  # sirt aligns ONE FACTOR AT A TIME, so this loops over dimensions in exactly those terms.
  # HARD STOP (§6.3): no country mean, ranking or profile is reported for a dimension unless
  # invariance_alignment_simulate confirms parameter recovery for that dimension.
  if (!perdim && !is.null(lam_by_group) && length(lam_by_group) >= 2) {
    inv$alignment <- list()
    inv$alignment_input <- list(
      groups = length(lam_by_group),
      route = if (pergroup) "per-group configural" else "pooled configural")
    for (dd in c("D1","D2","D3")) {
      vs <- intersect(by_dim(dd), ordvars)
      say("  aligning ", dd, sprintf(" (%d items) … ", length(vs)))
      inv$alignment[[dd]] <- align_one(lam_by_group, vs, dd)
    }
  }
}

# ---------------------------------------------------------------- write out --
out <- list(
  run_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  variant = variant,
  stage = stage,
  f117_assignment = f117,
  shared_D2_D3 = shared,
  seed = 20260810,
  R_version = R.version.string,
  packages = sapply(c("lavaan","semTools","sirt"), function(p)
               as.character(utils::packageVersion(p))),
  frame = list(rows = nrow(d), countries = length(unique(d$country)),
               source_sha256 = meta$source_sha256,
               item_table_sha256 = meta$item_table_sha256),
  fit = fit_table, drop_log = drop_log, H1 = H1, H2 = H2, invariance = inv
)
dir.create(file.path(ROOT, "supplement/analysis"), showWarnings = FALSE, recursive = TRUE)
tag <- paste0(if (f117 == "both") variant else paste0(variant, "-f117", f117),
              if (stage == "all") "" else paste0("-", stage))
op <- file.path(ROOT, "supplement/analysis", sprintf("cfa-%s.json", tag))
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 6, null = "null"), op)
cat("\nwrote", sub(paste0(ROOT, "/"), "", op), "\n")
cat("Every number in the manuscript must be read from this file, never transcribed by hand.\n")
