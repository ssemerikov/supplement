#!/usr/bin/env Rscript
# =============================================================================
# 13_verify_pergroup_decomposition.R -- is the per-group configural route exact?
#
#   Rscript code/13_verify_pergroup_decomposition.R [--variant primary]
#
# WHY THIS IS A REPO SCRIPT AND NOT A SCRATCH CHECK. The manuscript, the cover
# letter and preregistration.md Sec. 11 all rest on one claim: that fitting the
# configural model country by country returns the same estimates as fitting it
# as one multi-group model, so the memory-forced workaround is exact rather than
# approximate. The argument for it is algebraic -- the configural model imposes
# no cross-group constraints, so its discrepancy function is a sum of independent
# per-group terms -- but an algebraic argument about what lavaan does is a
# hypothesis about lavaan, and starting values, convergence criteria and the
# per-group orientation of a factor under std.lv=TRUE all bear on whether the two
# routes actually land in the same place.
#
# It was originally checked in a scratch script whose output was quoted in the
# cover letter and the deviation log. That is exactly the defect this project
# caught elsewhere and withdrew: a number quoted as evidence that nothing in the
# repository reproduces. The check now lives here and writes its result to
# supplement/analysis/, so the claim is auditable rather than reported.
#
# WHAT IT NEEDS. Both routes must already be cached, which they are once
#   --stage ladder     has run (pooled 12-country configural), and
#   --stage alignment  has run (per-country configural for all 39).
# It fits nothing itself; it reads two sets of cached estimates and compares
# them. Cheap, and safe to run beside a long fit.
# =============================================================================

suppressWarnings(suppressMessages({
  .lib <- path.expand("~/R/x86_64-pc-linux-gnu-library/4.6")
  if (dir.exists(.lib)) .libPaths(c(.lib, .libPaths()))
  library(lavaan); library(jsonlite)
}))

ROOT <- normalizePath(file.path(dirname(sub("--file=", "",
        grep("--file=", commandArgs(FALSE), value = TRUE)[1])), ".."))
args    <- commandArgs(trailingOnly = TRUE)
variant <- if (length(args) >= 2 && args[1] == "--variant") args[2] else "primary"

CACHE <- file.path(ROOT, "supplement/analysis/.fitcache")
items <- fromJSON(file.path(ROOT, "data/derived",
                            sprintf("pii-frame-%s.meta.json", variant)))$items

pooled_f <- file.path(CACHE, sprintf("%s-both-inv-k12-configural.rds", variant))
if (!file.exists(pooled_f))
  stop("pooled subset configural not cached; run 06_cfa_invariance.R --stage ladder first",
       call. = FALSE)
pooled <- lavInspect(readRDS(pooled_f), "est")
invisible(gc())

gnames <- names(pooled)
per <- list()
missing <- character(0)
for (g in gnames) {
  f <- file.path(CACHE, sprintf("%s-both-cfg-%s.rds", variant,
                                gsub("[^A-Za-z0-9]+", "_", g)))
  if (!file.exists(f)) { missing <- c(missing, g); next }
  z <- readRDS(f)
  if (isTRUE(z$converged)) per[[g]] <- z$est
}
common <- intersect(gnames, names(per))
cat(sprintf("pooled groups: %d ; per-group fits available: %d ; compared: %d\n\n",
            length(gnames), length(per), length(common)))

out <- list(
  registered = FALSE,
  purpose = paste("verify that the memory-forced per-group configural route reproduces the",
                  "pooled multi-group configural estimates exactly"),
  variant = variant,
  run_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  pooled_source = basename(pooled_f),
  n_groups_pooled = length(gnames),
  n_groups_compared = length(common),
  groups_missing_per_group_fit = missing,
  dimensions = list())

worst_overall <- 0
min_r_overall <- 1
for (dd in c("D1", "D2", "D3")) {
  vs <- intersect(items$variable[items$dimension == dd], rownames(pooled[[1]]$lambda))
  rs <- c(); mx <- c(); flips <- 0
  for (g in common) {
    a <- pooled[[g]]$lambda[vs, dd]
    b <- per[[g]]$lambda[vs, dd]
    r <- suppressWarnings(cor(a, b))
    # A whole-factor sign flip is an expected and harmless indeterminacy under std.lv=TRUE:
    # the factor is identified only up to sign within a group. Compare on the aligned
    # orientation, and report the flip count separately so it is not hidden.
    if (!is.na(r) && r < 0) { b <- -b; flips <- flips + 1; r <- -r }
    rs <- c(rs, r); mx <- c(mx, max(abs(a - b)))
  }
  out$dimensions[[dd]] <- list(
    n_items = length(vs), n_countries = length(common),
    r_min = round(min(rs, na.rm = TRUE), 6),
    r_median = round(median(rs, na.rm = TRUE), 6),
    r_max = round(max(rs, na.rm = TRUE), 6),
    max_abs_loading_diff_median = round(median(mx), 6),
    max_abs_loading_diff_worst = round(max(mx), 6),
    sign_flips = flips)
  worst_overall <- max(worst_overall, max(mx))
  min_r_overall <- min(min_r_overall, min(rs, na.rm = TRUE))

  cat(sprintf("%s (%d items, %d countries)\n", dd, length(vs), length(common)))
  cat(sprintf("   correlation pooled vs per-group : min %.4f  median %.4f  max %.4f\n",
              min(rs, na.rm = TRUE), median(rs, na.rm = TRUE), max(rs, na.rm = TRUE)))
  cat(sprintf("   max |loading difference|        : median %.4f  worst %.4f\n",
              median(mx), max(mx)))
  cat(sprintf("   sign flips (harmless)           : %d of %d countries\n\n",
              flips, length(common)))
}

# The threshold is deliberately strict. This is not a "close enough" test: the claim in the
# manuscript is that the routes are the SAME minimiser, so anything short of agreement to
# several decimals means the claim is wrong and the alignment must be redone on the pooled route.
out$decomposition_exact <- (min_r_overall > .999 && worst_overall < .01)
out$worst_abs_loading_diff <- round(worst_overall, 6)
out$min_correlation <- round(min_r_overall, 6)
out$reading <- paste(
  "Correlations at ~1.000 with differences near zero mean the decomposition is exact and the",
  "cross-country loading instability is a property of the data, not of the workaround.",
  "Correlations well below 1 would mean the per-group route lands in different optima and the",
  "alignment would have to be redone.")

dest <- file.path(ROOT, "supplement/analysis",
                  sprintf("pergroup-decomposition-%s.json", variant))
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat(sprintf("decomposition_exact: %s  (min r %.6f, worst |diff| %.6f)\n",
            out$decomposition_exact, min_r_overall, worst_overall))
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
if (!out$decomposition_exact) quit(status = 1)
