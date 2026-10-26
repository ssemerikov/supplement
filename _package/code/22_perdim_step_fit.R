#!/usr/bin/env Rscript
# =============================================================================
# 22_perdim_step_fit.R -- fit and measure EXACTLY ONE per-dimension invariance
# step, in its own process, and never redo one already on disk.
#
#   Rscript code/22_perdim_step_fit.R --dim D1 --step scalar  [--countries 39]
#   Rscript code/22_perdim_step_fit.R --dim D1 --step metric  --countries 12
#
# WHY THIS EXISTS. `06_cfa_invariance.R --stage perdim` walks configural ->
# metric -> scalar for all three dimensions in one process and calls `fitrow()`
# on every step unconditionally. It reads a cached FIT but recomputes its
# MEASURES, and under WLSMV with `se = "none"` those measures are not cheap:
# the scaled test statistic needs the Delta matrix that `se = "none"` deferred,
# so `fitMeasures(cfi.scaled)` pays for it then. On 2026-08-11 a run spent
# 65 minutes of CPU recomputing D1 configural measures that
# `perdim-step-measures-primary.json` already contained (.6694), and would have
# spent as long again on D1 metric (.6932), before reaching the only step that
# has never been estimated at all.
#
# So: one step per invocation, skip anything already measured, exit. The caller
# drives the sequence. This is the same discipline `code/14` applies to
# extraction, extended to the fitting itself.
#
# EXACT PARITY WITH `06` IS THE WHOLE POINT. The frame, the reverse-keying rule,
# the >=200-respondent country filter, the category-collapsing rule, the seeded
# 12-country draw, the model syntax, the estimator, `se = "none"` and the cache
# key are all copied from it deliberately. Two consequences worth stating:
#   * Collapsing is computed over ALL qualifying countries and only then
#     subsetted, exactly as `--stage ladder` does. Collapsing within the subset
#     would give different categories and a ladder not comparable to the
#     39-country one.
#   * The 39-country cache key is byte-identical to `06`'s, so fits it already
#     produced are reused rather than refitted. The 12-country key carries `k12`
#     so the two cannot collide.
#
# It writes measures to a JSON keyed by dimension and step, merging rather than
# overwriting, so a sequence of invocations accumulates one file.
#
# `--bounds pos.var` IS A SEPARATE, NON-REGISTERED EXPERIMENT AND IS KEPT APART.
# The D2 configural solution has a negative residual variance in one group of 39
# (Portugal, A080_02), which lets that rung fit better than a proper solution
# would and so exaggerates the degradation when loadings are constrained. Refitting
# under non-negative residual-variance bounds quantifies the rung directly. It is
# a DIFFERENT estimation problem, not a correction of the registered one, so it
# writes to `perdim-bounded-measures-<variant>.json` and carries its own cache
# suffix: it cannot overwrite, and cannot be mistaken for, the primary record.
# A delta is only meaningful between two rungs fitted under the SAME bounds.
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
  i <- match(flag, args); if (!is.na(i) && length(args) > i) args[i + 1] else default
}
dd      <- getarg("--dim")
step    <- getarg("--step")
ncty    <- as.integer(getarg("--countries", "39"))
bnd     <- getarg("--bounds", "none")
if (!bnd %in% c("none", "standard", "wide", "pos.var", "pos.ov.var", "pos.lv.var"))
  stop("--bounds must be one of none|standard|wide|pos.var|pos.ov.var|pos.lv.var", call. = FALSE)
variant <- getarg("--variant", "primary")
f117    <- getarg("--f117", "both")
if (is.null(dd) || is.null(step) || !step %in% c("configural", "metric", "scalar"))
  stop("usage: --dim D1|D2|D3 --step configural|metric|scalar [--countries 39|12]",
       call. = FALSE)
set.seed(20260810)   # registered seed, and the one the subset draw depends on

sub12 <- ncty < 39
dest <- file.path(ROOT, "supplement/analysis",
                  if (bnd != "none") sprintf("perdim-bounded-measures-%s.json", variant)
                  else if (sub12) sprintf("perdim-subset-measures-%s.json", variant)
                  else sprintf("perdim-step-measures-%s.json", variant))
# The bound belongs in the key as well as in the filename: several bound types share one
# bounded-measures file, and without it the "refuse to redo" guard below would read the first
# one as an answer for all of them.
skey <- paste(c(dd, step, if (bnd != "none") sub("\\.", "", bnd)), collapse = "_")

# --- refuse to redo -----------------------------------------------------------------------
# The defect this script exists to fix. If the measures are already on disk, say so and stop:
# recomputing them cannot produce a different number and costs an hour.
if (file.exists(dest)) {
  prev <- fromJSON(dest, simplifyVector = FALSE)
  if (!is.null(prev$steps[[skey]]$cfi.scaled)) {
    cat(sprintf("%s / %s already measured (cfi.scaled = %.4f) in %s -- nothing to do\n",
                dd, step, prev$steps[[skey]]$cfi.scaled, basename(dest)))
    quit(status = 0)
  }
}

# --- data, prepared exactly as 06 does ------------------------------------------------------
meta <- fromJSON(file.path(ROOT, "data/derived", sprintf("pii-frame-%s.meta.json", variant)))
d <- read.csv(file.path(ROOT, "data/derived", sprintf("pii-frame-%s.csv", variant)),
              stringsAsFactors = FALSE)
items <- meta$items
for (v in meta$reverse_keyed) {
  if (!v %in% names(d)) next
  rng <- range(d[[v]], na.rm = TRUE)
  d[[v]] <- rng[1] + rng[2] - d[[v]]
}
ordvars <- unique(items$variable)
for (v in ordvars) d[[v]] <- ordered(d[[v]])

cnt  <- table(d$country)
keep <- names(cnt)[cnt >= 200]

# Category collapsing: identical rule, identical scope. `06` collapses over EVERY country in the
# frame and applies the >=200 filter afterwards, so the scope must be `d`, not `d[keep]`. An
# earlier version of this script collapsed over the filtered frame instead. On the present frame
# that is a distinction without a difference -- all 39 countries clear 200 respondents, so the two
# scopes see the same rows, and both rules return 7 items collapsed with 14 merges and identical
# category sets for every item (checked 2026-08-11). It is corrected anyway: the rule merges until
# no category is empty in ANY country, so a frame that ever contained a sub-200 country would make
# `06` collapse strictly more than this script, and the per-dimension rungs -- configural and
# metric from `06`, scalar from here -- would then be fitted to different data without anything
# saying so. A nested comparison across two data preparations is not a nested comparison.
MIN_PER_GROUP <- 1L
dinv <- d
ncol_before <- 0L
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
  if (merges > 0L) { dinv[[v]] <- ordered(x); ncol_before <- ncol_before + 1L }
}
cat(sprintf("collapsed %d items (min %d per group, scope = all %d countries in the frame; %d pass the >=200 filter)\n",
            ncol_before, MIN_PER_GROUP, length(cnt), length(keep)))

if (sub12) {
  set.seed(20260810)
  keep <- sort(sample(keep, min(ncty, length(keep))))
  cat(sprintf("SUBSET (seed 20260810): %d countries: %s\n",
              length(keep), paste(keep, collapse = ", ")))
}
dg <- dinv[dinv$country %in% keep, ]

vs  <- intersect(unique(items$variable[items$dimension == dd]), ordvars)
syn <- paste0(dd, " =~ ", paste(vs, collapse = " + "))
grp <- c(configural = list(NULL), metric = list("loadings"),
         scalar = list(c("loadings", "thresholds")))[[step]]
cat(sprintf("%s / %s : %d items, %d countries, %d rows\n",
            dd, step, length(vs), length(keep), nrow(dg)))

# --- fit (or reuse 06's cache) ---------------------------------------------------------------
CACHE <- file.path(ROOT, "supplement/analysis/.fitcache")
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)
key <- file.path(CACHE, sprintf("%s-%s-pd%s%s%s-%s.rds", variant, f117, dd,
                                if (sub12) sprintf("-k%d", ncty) else "",
                                if (bnd != "none") paste0("-b", sub("\\.", "", bnd)) else "",
                                step))
if (file.exists(key)) {
  cat(sprintf("  fit cached (%.0f MB), reading\n", file.size(key) / 1e6))
  fit <- readRDS(key)
} else {
  cat("  fitting ... "); flush.console(); t0 <- Sys.time()
  fit <- tryCatch(
    cfa(syn, data = dg[, c("country", vs)], group = "country", estimator = "WLSMV",
        ordered = vs, missing = "pairwise", std.lv = TRUE, se = "none",
        group.equal = grp, bounds = bnd),
    error = function(e) { cat("FAILED:", conditionMessage(e), "\n"); NULL })
  if (is.null(fit)) quit(status = 4)
  cat(sprintf("%.0f min\n", as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  saveRDS(fit, key)
}

FITM <- c("chisq.scaled", "df.scaled", "pvalue.scaled", "cfi.scaled",
          "tli.scaled", "rmsea.scaled", "srmr")

# ADMISSIBILITY, RECORDED RATHER THAN LEFT IN A LOG LINE. lavaan reports negative estimated
# variances through `lav_object_post_check()`, which prints among the deferred warnings at the end
# of a run and is trivially missed -- it was missed here until D2 configural was read by eye on
# 2026-08-11 (Portugal, A080_02, theta = -0.420, standardised loading -1.191 where the other 38
# groups run up to +0.814). A ladder whose configural solution is inadmissible in some group must
# carry that fact next to its fit statistics, because the fit statistics are computed from that
# solution. This only records; it drops nothing and changes no estimate. The registered drop rule
# names Heywood cases, but it names them in the REGISTERED configural model (M2), so a Heywood case
# in a unidimensional per-dimension model is a reporting obligation, not a licence to drop an item.
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
if (!is.null(heywood) && length(heywood))
  cat(sprintf("  ADMISSIBILITY: %d negative residual variance(s) in %d group(s)\n",
              length(heywood), length(unique(vapply(heywood, `[[`, "", "country")))))

cat("  measures ... "); flush.console(); t1 <- Sys.time()
conv <- isTRUE(tryCatch(lavInspect(fit, "converged"), error = function(e) FALSE))
m <- tryCatch(fitMeasures(fit, FITM),
              error = function(e) setNames(rep(NA_real_, length(FITM)), FITM))
mins <- as.numeric(difftime(Sys.time(), t1, units = "mins"))
cat(sprintf("%.0f min  converged=%s  cfi.scaled=%.4f\n", mins, conv,
            unname(m[["cfi.scaled"]])))

out <- if (file.exists(dest)) fromJSON(dest, simplifyVector = FALSE) else
  list(registered = FALSE,
       purpose = paste("per-dimension invariance steps fitted and measured one per process;",
                       "unidimensional models, so neither the registered three-factor ladder",
                       "nor the same specification as the subset ladder"),
       variant = variant, steps = list())
out$run_utc <- format(Sys.time(), tz = "UTC", usetz = TRUE)
out$n_countries <- length(keep)
if (sub12) out$countries <- keep
out$steps[[skey]] <- c(
  list(dimension = dd, step = step, converged = conv, n_countries = length(keep),
       n_items = length(vs), bounds = bnd,
       measure_minutes = round(mins, 1), cache_file = basename(key),
       heywood_negative_var = if (is.null(heywood)) NA else length(heywood),
       heywood_cases = if (is.null(heywood) || !length(heywood)) list() else heywood),
  as.list(round(m, 4)))
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
