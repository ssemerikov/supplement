#!/usr/bin/env Rscript
# =============================================================================
# 14_perdim_step_measures.R -- fit measures for ONE cached per-dimension step.
#
#   Rscript code/14_perdim_step_measures.R --dim D1 --step metric [--variant primary]
#
# WHY THIS EXISTS. `06_cfa_invariance.R --stage perdim` runs configural -> metric
# -> scalar for a dimension and writes its JSON only after all three finish. D1
# scalar at 39 countries defeated three attempts: `systemd-oomd` killed it each
# time, most recently at a 12.7 GB peak after 3 h 45 min of CPU. The consequence
# was that a run which successfully fitted configural (25 min) and metric
# (33 min) produced **no output at all**, because it died on the third step.
#
# It was NOT unfittable, and an earlier version of this comment said it was.
# `systemd-oomd` kills on a PSI memory-pressure stall, not on exhaustion, so it
# was terminating a job that still had somewhere to go. With the daemon stopped
# and 32 GB of swap the same step completed on 2026-08-11 in 132 min of fitting
# plus 91 min of measures (`code/22`). The all-or-nothing failure mode this
# script guards against was real; the impossibility it cited was not.
#
# That is a bad failure mode. The configural -> metric delta is the rung the
# paper's argument turns on -- if loadings are not common across countries, the
# question of common intercepts does not arise -- and both fits it needs are
# cached. This script extracts the measures for exactly one step, in its own
# process, and merges the result into a small JSON.
#
# ONE FIT PER PROCESS, DELIBERATELY. `fitMeasures()` on a cached 39-group WLSMV
# fit is expensive -- measured at ~34 min / 11.8 GB for D1 configural and ~44 min
# / 12.2 GB for D1 metric. Two of those in one process is what pushes this machine
# over. Exiting between steps returns the memory to the OS in a way `gc()` does
# not reliably manage, so the caller runs this once per step, sequentially.
#
# WHY IT IS EXPENSIVE IS NOT ESTABLISHED, and an earlier version of this comment
# asserted a reason that is false. It claimed `fitMeasures()` must refit the
# baseline independence model. It does not: `cfa()` populates the `@baseline`
# slot eagerly, that slot survives `saveRDS`, and three consecutive
# `fitMeasures(fit, "cfi.scaled")` calls on a small multi-group ordinal fit --
# built with the same `se = "none"` these fits use -- cost 0.15 s each, with no
# first-call penalty (checked 2026-08-11). A deferred Delta matrix was the next
# candidate and is not observable at small scale either. So the cost is real,
# reproducible and measured, and its mechanism is open. The discipline below
# rests on the measurement, which is what matters here; it does not rest on the
# explanation, which is why the wrong explanation went unnoticed for a day.
#
# It fits NOTHING and reads only the cache, so it cannot alter an estimate. If a
# step's cache is absent it says so and exits 3, rather than fitting it.
# =============================================================================

suppressWarnings(suppressMessages({
  .lib <- path.expand("~/R/x86_64-pc-linux-gnu-library/4.6")
  if (dir.exists(.lib)) .libPaths(c(.lib, .libPaths()))
  library(lavaan); library(jsonlite)
}))

ROOT <- normalizePath(file.path(dirname(sub("--file=", "",
        grep("--file=", commandArgs(FALSE), value = TRUE)[1])), ".."))
args <- commandArgs(trailingOnly = TRUE)
getarg <- function(flag, default = NULL) {
  i <- match(flag, args)
  if (!is.na(i) && length(args) > i) args[i + 1] else default
}
dd      <- getarg("--dim")
step    <- getarg("--step")
variant <- getarg("--variant", "primary")
f117    <- getarg("--f117", "both")
if (is.null(dd) || is.null(step))
  stop("usage: --dim D1|D2|D3 --step configural|metric|scalar", call. = FALSE)

CACHE <- file.path(ROOT, "supplement/analysis/.fitcache")
key   <- file.path(CACHE, sprintf("%s-%s-pd%s-%s.rds", variant, f117, dd, step))
if (!file.exists(key)) {
  cat(sprintf("no cached fit for %s/%s at %s\n", dd, step, basename(key)))
  quit(status = 3)
}

FITM <- c("chisq.scaled", "df.scaled", "pvalue.scaled", "cfi.scaled",
          "tli.scaled", "rmsea.scaled", "srmr")

cat(sprintf("%s / %s : reading %s (%.0f MB on disk)\n", dd, step, basename(key),
            file.size(key) / 1e6))
t0  <- Sys.time()
fit <- readRDS(key)
conv <- isTRUE(tryCatch(lavInspect(fit, "converged"), error = function(e) FALSE))
m <- tryCatch(fitMeasures(fit, FITM),
              error = function(e) setNames(rep(NA_real_, length(FITM)), FITM))
mins <- as.numeric(difftime(Sys.time(), t0, units = "mins"))
cat(sprintf("  converged=%s  cfi.scaled=%.4f  rmsea.scaled=%.4f  (%.0f min)\n",
            conv, unname(m[["cfi.scaled"]]), unname(m[["rmsea.scaled"]]), mins))

dest <- file.path(ROOT, "supplement/analysis",
                  sprintf("perdim-step-measures-%s.json", variant))
out <- if (file.exists(dest)) fromJSON(dest, simplifyVector = FALSE) else
  list(registered = FALSE,
       purpose = paste("fit measures for individually cached per-dimension invariance steps,",
                       "extracted one per process because the full --stage perdim run cannot",
                       "complete on this hardware"),
       variant = variant, steps = list())
out$run_utc <- format(Sys.time(), tz = "UTC", usetz = TRUE)
out$steps[[paste(dd, step, sep = "_")]] <- c(
  list(dimension = dd, step = step, converged = conv,
       extraction_minutes = round(mins, 1),
       cache_file = basename(key)),
  as.list(round(m, 4)))
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
