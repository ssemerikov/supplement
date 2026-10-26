#!/usr/bin/env Rscript
# =============================================================================
# 27_heywood_backfill_k12.R -- extend the admissibility census to the two
# TWELVE-COUNTRY ladders, which `24` cannot reach.
#
#   Rscript code/27_heywood_backfill_k12.R --target subset|m2k12 --step configural
#
# WHY THIS EXISTS. The census footnote under Table 3 says a mechanical census of
# negative residual variances "returns none at any other rung of any ladder
# here". Table 3 has fifteen rungs; only the nine 39-country rungs in
# `perdim-step-measures-primary.json` carry `heywood_*` fields. The six
# twelve-country rungs -- the three-factor M2 ladder and D1 alone -- were never
# censused, and they include the ladder the −.0220 metric failure is drawn from.
# The footnote therefore claims more than it checked.
#
# `24` cannot do this. It hardcodes `perdim-step-measures-<variant>.json` and the
# `pd<D>-<step>` cache name. The twelve-country rungs live in two other files with
# two other shapes: `perdim-subset-measures-primary.json` under `steps`, and
# `cfa-primary-ladder.json` under `invariance$fit`. Rather than loosen `24`'s
# guards -- it is working and idempotent -- this reaches the other two shapes with
# the same guards and a census copied from it verbatim.
#
# WHY IT IS SAFE. `lavInspect(fit, "est")` reads the stored parameter table. No
# re-estimation, no data access; chisq, df, CFI, RMSEA, TLI and SRMR cannot move.
# Refuses to create a record, refuses to overwrite an existing census.
#
# WHY ONE PER PROCESS. `primary-both-inv-k12-scalar.rds` is 510 MB on disk and
# expands to several GB. One resident at a time, largest last.
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
target <- getarg("--target")
step   <- getarg("--step")
if (is.null(target) || is.null(step) || !target %in% c("subset", "m2k12") ||
    !step %in% c("configural", "metric", "scalar"))
  stop("usage: --target subset|m2k12 --step configural|metric|scalar", call. = FALSE)

if (target == "subset") {
  dest  <- file.path(ROOT, "supplement/analysis", "perdim-subset-measures-primary.json")
  key   <- file.path(ROOT, "supplement/analysis/.fitcache",
                     sprintf("primary-both-pdD1-k12-%s.rds", step))
  label <- paste0("D1@12 ", step)
} else {
  dest  <- file.path(ROOT, "supplement/analysis", "cfa-primary-ladder.json")
  key   <- file.path(ROOT, "supplement/analysis/.fitcache",
                     sprintf("primary-both-inv-k12-%s.rds", step))
  label <- paste0("M2@12 ", step)
}
if (!file.exists(dest)) stop("no measures file at ", dest, call. = FALSE)
out <- fromJSON(dest, simplifyVector = FALSE)

# The two files nest the rung differently; read and write through one accessor pair
# so the guards below are identical for both.
getE <- function(o) if (target == "subset") o$steps[[paste0("D1_", step)]] else o$invariance$fit[[step]]
setE <- function(o, e) { if (target == "subset") o$steps[[paste0("D1_", step)]] <- e
                         else o$invariance$fit[[step]] <- e; o }

e <- getE(out)
if (is.null(e))
  stop(label, " has no entry in ", basename(dest),
       " -- this script backfills, it does not create records", call. = FALSE)
if (is.null(e$cfi.scaled))
  stop(label, " has no fit statistics -- nothing to attach a census to", call. = FALSE)
if (!is.null(e$heywood_negative_var) && !is.na(e$heywood_negative_var)) {
  cat(sprintf("%s already has a census (heywood_negative_var = %s) -- nothing to do\n",
              label, e$heywood_negative_var))
  quit(status = 0)
}
if (!file.exists(key))
  stop("cached fit absent: ", basename(key),
       " -- cannot backfill without the fit it was measured from", call. = FALSE)

cat(sprintf("%s : reading %s (%.0f MB) ... ", label, basename(key),
            file.info(key)$size / 1e6)); flush.console()
fit <- readRDS(key)
cat("ok\n")

# Byte-identical to the census in code/22 and code/24, deliberately: they must not drift.
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

e$heywood_negative_var <- length(heywood)
e$heywood_cases        <- if (length(heywood)) heywood else list()
e$heywood_backfilled   <- format(Sys.time(), tz = "UTC", usetz = TRUE)
out <- setE(out, e)
out$heywood_backfill_note <- paste(
  "Entries carrying `heywood_backfilled` had their admissibility census added by",
  "code/27_heywood_backfill_k12.R from the cached fit, after the fit statistics in",
  "the same entry were written. No estimate or fit statistic was recomputed.")

write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
