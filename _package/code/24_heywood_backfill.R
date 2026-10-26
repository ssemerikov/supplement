#!/usr/bin/env Rscript
# =============================================================================
# 24_heywood_backfill.R -- add the admissibility census to per-dimension steps
# that were measured BEFORE the census existed. Reads exactly one cached fit,
# writes exactly one JSON field pair, changes no estimate and no fit statistic.
#
#   Rscript code/24_heywood_backfill.R --dim D1 --step configural
#
# WHY THIS EXISTS. The census in `code/22` (negative estimated residual
# variances, per group, per variable) was added on 2026-08-11, after D1's three
# rungs and D2's configural and metric rungs had already been measured. Their
# JSON entries therefore have no `heywood_negative_var` field at all, and the
# preregistration's deviation log records that the absence means "not checked
# mechanically", NOT "clean". That is an honest but unsatisfying state to submit
# in: a reviewer cannot tell an unchecked rung from an admissible one. The fits
# are on disk, so the check costs a read and an `lavInspect`, not a refit.
#
# WHY IT IS SAFE. `lavInspect(fit, "est")` reads the stored parameter table. It
# does not re-estimate, does not touch the data, and cannot change chisq, df,
# CFI, RMSEA, TLI or SRMR. The script refuses to write into an entry that has no
# fit statistics (it must not manufacture a record), and refuses to overwrite a
# census that is already there (idempotent, so a re-run cannot silently differ).
#
# WHY ONE PER PROCESS. Same reason as `22` and `23`: `primary-both-pdD1-scalar.rds`
# is 332 MB on disk and expands to several GB in memory. Two of these resident at
# once is how the earlier chain got killed.
# =============================================================================

suppressWarnings(suppressMessages({
  .lib <- path.expand("~/R/x86_64-pc-linux-gnu-library/4.6")
  if (dir.exists(.lib)) .libPaths(c(.lib, .libPaths()))
  library(lavaan); library(jsonlite)
}))

ROOT <- normalizePath(file.path(dirname(sub("--file=", "",
        grep("--file=", commandArgs(FALSE), value = TRUE)[1])), ".."))

args <- commandArgs(TRUE)
getarg <- function(flag, default = NULL) {
  i <- match(flag, args); if (is.na(i) || i == length(args)) default else args[i + 1L]
}
dd      <- getarg("--dim")
step    <- getarg("--step")
variant <- getarg("--variant", "primary")
f117    <- getarg("--f117", "both")
if (is.null(dd) || is.null(step) || !dd %in% c("D1", "D2", "D3") ||
    !step %in% c("configural", "metric", "scalar"))
  stop("usage: --dim D1|D2|D3 --step configural|metric|scalar", call. = FALSE)

dest <- file.path(ROOT, "supplement/analysis",
                  sprintf("perdim-step-measures-%s.json", variant))
skey <- paste(dd, step, sep = "_")
key  <- file.path(ROOT, "supplement/analysis/.fitcache",
                  sprintf("%s-%s-pd%s-%s.rds", variant, f117, dd, step))

if (!file.exists(dest)) stop("no measures file at ", dest, call. = FALSE)
out <- fromJSON(dest, simplifyVector = FALSE)

if (is.null(out$steps[[skey]]))
  stop(skey, " has no entry in ", basename(dest),
       " -- this script backfills, it does not create records", call. = FALSE)
if (is.null(out$steps[[skey]]$cfi.scaled))
  stop(skey, " has no fit statistics -- measure it with code/22 first", call. = FALSE)
if (!is.null(out$steps[[skey]]$heywood_negative_var) &&
    !is.na(out$steps[[skey]]$heywood_negative_var)) {
  cat(sprintf("%s already has a census (heywood_negative_var = %s) -- nothing to do\n",
              skey, out$steps[[skey]]$heywood_negative_var))
  quit(status = 0)
}
if (!file.exists(key))
  stop("cached fit absent: ", basename(key),
       " -- cannot backfill without the fit it was measured from", call. = FALSE)

cat(sprintf("%s / %s : reading %s (%.0f MB) ... ", dd, step, basename(key),
            file.info(key)$size / 1e6)); flush.console()
fit <- readRDS(key)
cat("ok\n")

# Byte-identical to the census in code/22, deliberately: the two must not drift.
heywood <- tryCatch({
  est <- lavInspect(fit, "est"); gl <- lavInspect(fit, "group.label"); acc <- list()
  for (i in seq_along(est)) {
    dv <- diag(est[[i]]$theta); b <- dv[dv < 0]
    for (vn in names(b))
      acc[[length(acc) + 1L]] <- list(country = gl[i], variable = vn,
                                      theta = round(unname(b[[vn]]), 6))
  }
  acc
}, error = function(e) NULL)
if (is.null(heywood)) stop("census failed on ", basename(key), call. = FALSE)

if (length(heywood)) {
  cat(sprintf("  ADMISSIBILITY: %d negative residual variance(s) in %d group(s): %s\n",
              length(heywood), length(unique(vapply(heywood, `[[`, "", "country"))),
              paste(sprintf("%s/%s=%.3f",
                            vapply(heywood, `[[`, "", "country"),
                            vapply(heywood, `[[`, "", "variable"),
                            vapply(heywood, function(h) h$theta, 0)), collapse = ", ")))
} else {
  cat("  ADMISSIBILITY: clean -- no negative residual variances in any group\n")
}

# Insert the census next to the existing statistics; touch nothing else. The
# fit statistics already in the entry are preserved exactly as written.
e <- out$steps[[skey]]
e$heywood_negative_var <- length(heywood)
e$heywood_cases        <- if (length(heywood)) heywood else list()
e$heywood_backfilled   <- format(Sys.time(), tz = "UTC", usetz = TRUE)
out$steps[[skey]] <- e
out$heywood_backfill_note <- paste(
  "Entries carrying `heywood_backfilled` had their admissibility census added by",
  "code/24_heywood_backfill.R from the cached fit, after the fit statistics in the",
  "same entry were written by code/22. No estimate or fit statistic was recomputed.")

write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
