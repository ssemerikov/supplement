#!/usr/bin/env Rscript
# ESS structural replication of the PII measurement model. UNREGISTERED.
#
#   Rscript code/30_ess_replication.R [--stage single|rounds|all]
#
# preregistration.md §4.2 registers "an independent replication of model STRUCTURE, not of
# parameter values, for the politics and morality spheres only", and names no ESS items. The item
# mapping is therefore unregistered and was frozen, hashed and timestamped on 2026-09-08 before any
# ESS model was estimated (docs/design/ess-item-table-frozen.md). This script reports the
# replication as unregistered wherever it writes a verdict.
#
# WHAT REPLICATES AND WHAT CANNOT. ESS and EVS/WVS have disjoint respondents, different items and
# different response formats, so no parameter value here is comparable with the primary. What the
# model set below asks is the structural question only: on an independent instrument, do the same
# model comparisons come out the same way? The decision rules are the pre-registration's own,
# copied unaltered from 06_cfa_invariance.R so the two runs are read on one scale.
#
# ESS D3 HAS EXACTLY THREE INDICATORS, all institutional-trust items, and carries none of the
# anti-institutional-personalism content that defines D3 in the primary model. The frozen table
# says so before the fit; a D3 result here is weak evidence about the paper's third dimension and
# is reported as such, never as a clean replication of it.

suppressPackageStartupMessages({ library(lavaan); library(jsonlite) })

ROOT  <- normalizePath(file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE),
                                                                 value = TRUE)[1])), ".."))
args  <- commandArgs(TRUE)
stage <- { i <- match("--stage", args); if (!is.na(i) && length(args) > i) args[i + 1] else "all" }

FRAME <- file.path(ROOT, "data/derived/ess-replication-frame.csv")
META  <- file.path(ROOT, "data/derived/ess-frame-meta.json")
OUT   <- file.path(ROOT, "supplement/analysis/ess-replication.json")
CACHE <- file.path(ROOT, "supplement/analysis/.essfitcache")
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)

FROZEN_ESS_TABLE_SHA256 <- "94ae43fde2761dd9740957eb3fbca2963d89cf0d492b01e9fe8f4575b53ec5a1"

say <- function(...) { cat(..., sep = ""); flush.console() }

meta <- fromJSON(META, simplifyVector = TRUE)
if (!identical(meta$frozen_ess_table_sha256, FROZEN_ESS_TABLE_SHA256))
  stop("frozen ESS item table hash mismatch -- the table changed after the freeze. Disclose, do not loosen.")

set.seed(20260810)
d <- read.csv(FRAME, stringsAsFactors = FALSE, check.names = FALSE)
items <- meta$items
# The frozen table's IDs carry a hyphen (D1-P5); lavaan syntax needs syntactic names. The mapping
# is one to one and mechanical, and the JSON output carries both forms so nothing is lost.
safe  <- function(x) gsub("-", "_", x, fixed = TRUE)
names(d) <- safe(names(d))
D1 <- safe(items$id[items$dim == "D1"]); D2 <- safe(items$id[items$dim == "D2"])
D3 <- safe(items$id[items$dim == "D3"])
ordvars <- c(D1, D2, D3)
stopifnot(length(ordvars) == 20L, all(ordvars %in% names(d)))
for (v in ordvars) d[[v]] <- ordered(d[[v]])
say(sprintf("ESS frame: %d rows, %d countries, rounds %s\n", nrow(d),
            length(unique(d$cntry)), paste(sort(unique(d$essround)), collapse = "/")))
say(sprintf("D1=%d D2=%d D3=%d\n", length(D1), length(D2), length(D3)))

f <- function(nm, vs) paste0(nm, " =~ ", paste(vs, collapse = " + "))

# The same model set as the primary, minus M2m and M4: the ESS table contains no shared-stem
# battery, so Decision D3's method factor has nothing to load on, and M4's bifactor needs more
# indicators per factor than a three-item D3 supports.
models <- list(
  M0    = f("G", ordvars),
  M0_12 = f("G", union(D1, D2)),
  M1    = paste(f("D1", D1), f("D2", D2), sep = "\n"),
  M1b   = paste(f("D1", D1), f("D2", D2), "D1 ~~ 1*D2", sep = "\n"),
  M2    = paste(f("D1", D1), f("D2", D2), f("D3", D3), sep = "\n"),
  M2b   = paste(f("D1", D1), f("D2", D2), f("D3", D3), "D1 ~~ 1*D3", sep = "\n")
)

FITM <- c("chisq.scaled","df.scaled","pvalue.scaled","cfi.scaled",
          "tli.scaled","rmsea.scaled","srmr")

fit_cached <- function(nm, syntax, ...) {
  cf <- file.path(CACHE, paste0(nm, ".rds"))
  if (file.exists(cf)) { say("  ", nm, " (cached)\n"); return(readRDS(cf)) }
  t0 <- Sys.time()
  fit <- tryCatch(cfa(syntax, data = d, estimator = "WLSMV", ordered = ordvars,
                      missing = "pairwise", std.lv = TRUE, ...),
                  error = function(e) { say("  ", nm, " FAILED: ", conditionMessage(e), "\n"); NULL })
  if (is.null(fit) || !lavInspect(fit, "converged")) { say("  ", nm, " did not converge\n"); return(NULL) }
  say(sprintf("  %s  %.1f min\n", nm, as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  saveRDS(fit, cf); fit
}

fits <- list(); fit_table <- list()
if (stage %in% c("single", "all")) {
  say("\n-- single-group models (pooled over rounds and countries) --\n")
  for (nm in names(models)) {
    fit <- fit_cached(nm, models[[nm]])
    if (is.null(fit)) next
    fits[[nm]] <- fit
    fm <- fitMeasures(fit, FITM)
    fit_table[[nm]] <- as.list(round(fm, 4))
    say(sprintf("     cfi=%.4f rmsea=%.4f srmr=%.4f df=%.0f\n",
                fm[["cfi.scaled"]], fm[["rmsea.scaled"]], fm[["srmr"]], fm[["df.scaled"]]))
  }
}

# ------------------------------------------------------------------- H1, H2 --
# Identical code to 06_cfa_invariance.R. Copied, not re-derived, so the two runs cannot drift.
delta_cfi <- function(a, b) unname(fitMeasures(a,"cfi.scaled") - fitMeasures(b,"cfi.scaled"))
phi <- function(fit, x, y) {
  s <- standardizedSolution(fit)
  r <- s[s$op == "~~" & ((s$lhs == x & s$rhs == y) | (s$lhs == y & s$rhs == x)), "est.std"]
  if (length(r)) unname(r[1]) else NA_real_
}
# A restricted model reaching a LOWER unscaled chi-square than the model it nests in is impossible
# at a global optimum, and means the comparison is not interpretable. The primary run guards this
# and withholds a verdict rather than reporting one; so does this.
nested_ok <- function(restricted, full) {
  unname(fitMeasures(restricted, "chisq") >= fitMeasures(full, "chisq") - 1e-6)
}

H1 <- list(); H2 <- list()
if (all(c("M0_12","M1","M1b") %in% names(fits))) {
  lrt   <- lavTestLRT(fits$M1b, fits$M1)
  p_m1b <- lrt[["Pr(>Chisq)"]][2]
  dcfi  <- delta_cfi(fits$M1, fits$M0_12)
  phi12 <- phi(fits$M1, "D1", "D2")
  ok    <- nested_ok(fits$M1b, fits$M1) && nested_ok(fits$M0_12, fits$M1)
  a <- dcfi >= .010; b <- !is.na(p_m1b) && p_m1b < .01; cc <- phi12 <= .85
  H1 <- list(registered = FALSE, nested_ok = ok,
             a_deltaCFI_ge_.010 = a, b_M1b_rejected_at_.01 = b, c_phi_le_.85 = cc,
             deltaCFI = round(dcfi, 4), p_M1b = p_m1b, phi_D1_D2 = round(phi12, 4),
             abs_phi_le_.85 = abs(phi12) <= .85,
             supported = if (!ok) NA else (isTRUE(a) && isTRUE(b) && isTRUE(cc)),
             rule = "conjunctive: all three must hold (pre-registration 6.2), applied unaltered",
             interpretable = ok)
  say(sprintf("\nH1 (ESS): dCFI=%.4f[%s] p(M1b)=%.4g[%s] phi=%.3f[%s] nested_ok=%s -> %s\n",
              dcfi, a, p_m1b, b, phi12, cc, ok,
              if (!ok) "WITHHELD" else if (H1$supported) "SUPPORTED" else "NOT SUPPORTED"))
}
if (all(c("M2","M2b") %in% names(fits))) {
  lrt2 <- lavTestLRT(fits$M2b, fits$M2)
  p2   <- lrt2[["Pr(>Chisq)"]][2]
  ph13 <- phi(fits$M2, "D1", "D3")
  ok2  <- nested_ok(fits$M2b, fits$M2)
  H2 <- list(registered = FALSE, nested_ok = ok2,
             M2b_rejected_at_.01 = !is.na(p2) && p2 < .01, p_M2b = p2,
             phi_D1_D3 = round(ph13, 4), phi_le_.70 = ph13 <= .70,
             abs_phi_D1_D3 = round(abs(ph13), 4), abs_phi_le_.70 = abs(ph13) <= .70,
             signed_and_abs_agree = identical(ph13 <= .70, abs(ph13) <= .70),
             phi_D2_D3 = round(phi(fits$M2, "D2", "D3"), 4),
             supported = if (!ok2) NA else (!is.na(p2) && p2 < .01 && ph13 <= .70),
             d3_caveat = paste("ESS D3 is three institutional-trust items and carries none of the",
                               "anti-institutional-personalism content that defines D3 in the",
                               "primary model. Weak evidence about the paper's D3, by construction."),
             interpretable = ok2)
  say(sprintf("H2 (ESS): p(M2b)=%.4g phi13=%.3f nested_ok=%s -> %s\n", p2, ph13, ok2,
              if (!ok2) "WITHHELD" else if (H2$supported) "SUPPORTED" else "NOT SUPPORTED"))
}

# --------------------------------------------------------- cross-round chain --
# Registered at §4.2: "Rounds 9-10 and round 11 are NOT assumed comparable: cross-round invariance
# is tested, and if metric invariance fails, round 11 is reported separately rather than pooled."
# Judged on the same DeltaCFI <= .010 / DeltaRMSEA <= .015 the primary uses.
rounds <- list()
if (stage %in% c("rounds", "all")) {
  say("\n-- cross-round invariance, M2, group = essround --\n")
  steps <- list(configural = NULL, metric = "loadings", scalar = c("loadings", "thresholds"))
  rowsm <- list(); prev <- NULL
  for (nm in names(steps)) {
    cf <- file.path(CACHE, paste0("round_", nm, ".rds"))
    if (file.exists(cf)) { m <- readRDS(cf); say("  ", nm, " (cached)\n") } else {
      t0 <- Sys.time()
      fit <- tryCatch(cfa(models$M2, data = d, group = "essround", estimator = "WLSMV",
                          ordered = ordvars, missing = "pairwise", std.lv = TRUE,
                          group.equal = steps[[nm]]),
                      error = function(e) { say("  ", nm, " FAILED: ", conditionMessage(e), "\n"); NULL })
      if (is.null(fit) || !lavInspect(fit, "converged")) { say("  ", nm, " did not converge\n"); next }
      m <- as.list(fitMeasures(fit, FITM))
      say(sprintf("  %s  %.1f min  cfi=%.4f rmsea=%.4f\n", nm,
                  as.numeric(difftime(Sys.time(), t0, units = "mins")),
                  m$cfi.scaled, m$rmsea.scaled))
      saveRDS(m, cf); rm(fit); gc()
    }
    rowsm[[nm]] <- lapply(m, function(x) round(unname(x), 4))
    if (!is.null(prev)) {
      dc <- m$cfi.scaled - prev$cfi.scaled; dr <- m$rmsea.scaled - prev$rmsea.scaled
      rowsm[[nm]]$dCFI <- round(dc, 4); rowsm[[nm]]$dRMSEA <- round(dr, 4)
      rowsm[[nm]]$passes <- (dc >= -.010) && (dr <= .015)
      say(sprintf("     dCFI=%+.4f dRMSEA=%+.4f -> %s\n", dc, dr,
                  if (rowsm[[nm]]$passes) "PASS" else "FAIL"))
    }
    prev <- m
  }
  metric_ok <- isTRUE(rowsm$metric$passes)
  rounds <- list(
    groups = "essround 9 / 10 / 11", n_groups = 3L,
    criterion = "dCFI >= -.010 and dRMSEA <= .015, as in the primary",
    steps = rowsm,
    metric_invariance_holds = metric_ok,
    registered_consequence = paste(
      "§4.2: if metric invariance fails, round 11 is reported separately rather than pooled.",
      if (metric_ok) "Metric holds, so the pooled reading stands."
      else "Metric fails, so the pooled model is reported as not licensed across the a-suffixed round."),
    ess11_note = paste("ESS11's PVQ items carry the revised `a` administration; the frozen table",
                       "maps them one to one, and this chain is the test of whether that mapping",
                       "supports pooling."))
}

# ---------------------------------------------------- per-round replication ---
# The structural question, asked three times independently. If the model comparison comes out the
# same way in each round on its own, the pooled result is not an artefact of pooling.
perround <- list()
if (stage %in% c("rounds", "all")) {
  say("\n-- M1 vs M0_12 within each round --\n")
  for (r in sort(unique(d$essround))) {
    cf <- file.path(CACHE, paste0("perround_", r, ".rds"))
    if (file.exists(cf)) { perround[[as.character(r)]] <- readRDS(cf); say("  round ", r, " (cached)\n"); next }
    dr <- d[d$essround == r, ]
    fr <- lapply(c("M0_12","M1","M1b"), function(nm)
      tryCatch(cfa(models[[nm]], data = dr, estimator = "WLSMV", ordered = ordvars,
                   missing = "pairwise", std.lv = TRUE), error = function(e) NULL))
    names(fr) <- c("M0_12","M1","M1b")
    if (any(vapply(fr, is.null, logical(1)))) { say("  round ", r, " FAILED\n"); next }
    dcfi <- delta_cfi(fr$M1, fr$M0_12); p <- lavTestLRT(fr$M1b, fr$M1)[["Pr(>Chisq)"]][2]
    ph   <- phi(fr$M1, "D1", "D2")
    ok   <- nested_ok(fr$M1b, fr$M1) && nested_ok(fr$M0_12, fr$M1)
    res  <- list(round = r, n = nrow(dr), n_countries = length(unique(dr$cntry)),
                 deltaCFI = round(dcfi, 4), p_M1b = p, phi_D1_D2 = round(ph, 4),
                 nested_ok = ok,
                 supported = if (!ok) NA else (dcfi >= .010 && !is.na(p) && p < .01 && ph <= .85))
    saveRDS(res, cf); perround[[as.character(r)]] <- res
    say(sprintf("  round %d (n=%d, %d countries): dCFI=%.4f phi=%.3f -> %s\n",
                r, nrow(dr), res$n_countries, dcfi, ph,
                if (!ok) "WITHHELD" else if (res$supported) "SUPPORTED" else "NOT SUPPORTED"))
    rm(fr); gc()
  }
}

out <- list(
  analysis = "ESS structural replication of the PII model",
  registered = FALSE,
  registered_scope = paste("preregistration.md §4.2 registers a replication of model structure for",
                           "the politics and morality spheres only and names no ESS items; the item",
                           "mapping is unregistered and was frozen before any ESS model was fitted"),
  frozen_ess_table_sha256 = FROZEN_ESS_TABLE_SHA256,
  frame_sha256 = meta$frame_sha256,
  seed = 20260810,
  R_version = R.version.string,
  lavaan_version = as.character(packageVersion("lavaan")),
  run_utc = format(Sys.time(), "%Y-%m-%d %H:%M:%S", tz = "UTC"),
  estimator = "WLSMV, ordered indicators, pairwise-complete, std.lv = TRUE (as the primary)",
  n_rows = nrow(d), n_countries_any_round = length(unique(d$cntry)),
  n_by_dimension = list(D1 = length(D1), D2 = length(D2), D3 = length(D3)),
  item_ids = list(frozen_table = items$id, model = safe(items$id), dim = items$dim),
  parameter_comparability = paste("NONE. Disjoint respondents, different items, different response",
                                  "formats. Only the direction of the model comparisons replicates."),
  fit = fit_table, H1 = H1, H2 = H2, cross_round = rounds, per_round = perround
)
write(toJSON(out, auto_unbox = TRUE, digits = 8, na = "null", pretty = TRUE), OUT)
say("\nwrote ", OUT, "\n")
