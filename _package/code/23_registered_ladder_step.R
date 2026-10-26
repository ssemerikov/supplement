#!/usr/bin/env Rscript
# =============================================================================
# 23_registered_ladder_step.R -- fit and measure EXACTLY ONE rung of the
# REGISTERED invariance ladder: the three-factor M2 model over all 39 countries.
#
#   Rscript code/23_registered_ladder_step.R --step configural
#   Rscript code/23_registered_ladder_step.R --step metric
#   Rscript code/23_registered_ladder_step.R --step scalar
#   Rscript code/23_registered_ladder_step.R --step configural --countries 12   # validation
#   Rscript code/23_registered_ladder_step.R --step scalar --dry-run            # plan only
#
# WHY THIS EXISTS. This is the test the paper has had to report as never fitted.
# `06_cfa_invariance.R --stage ladder` can express it (`--subset-k 39`), but it
# CANNOT survive it: its loop accumulates every fitted object in `ifits` so the
# delta loop can reach consecutive pairs, so all three 39-group M2 fits are
# resident at once, and it writes its JSON only after all three finish. That is
# the exact design that produced three kills and no output on the per-dimension
# chain. One rung per process, written to disk the moment it exists.
#
# WHY IT IS NOW WORTH ATTEMPTING. The pooled 39-group configural fit was killed
# on 2026-08-10 at 8.5 GB resident + 2.9 GB swapped after 2 h 24 min of CPU, and
# recorded as "not estimable on this hardware". That inference was wrong, and the
# same wrong inference was drawn about the D1 scalar step. `systemd-oomd` kills
# on a PSI memory-pressure stall, not on exhaustion; with the daemon stopped and
# 32 GB of swap, D1 scalar completed in 2 h 51 min of CPU at a ~9.4 GB peak. The
# arithmetic here is larger -- 39 x ~258 = ~10,100 free parameters and a Delta
# Jacobian of (39 x 1,479) x 10,100 doubles, about 4.6 GB per copy -- but 4.6 GB
# per copy against 15 GB of RAM and 32 GB of swap is a slow fit, not an
# impossible one. It may still fail. That is a finding either way, and it will be
# reported as one rather than being converted into a claim about the model.
#
# EXACT PARITY WITH `06` IS THE WHOLE POINT, and every line of the preparation
# below is copied from it deliberately:
#   * reverse keying from `meta$reverse_keyed`, using the observed category range;
#   * category collapsing over EVERY country in the frame, filtering to the >=200
#     countries only afterwards (getting this backwards is a silent divergence --
#     see the note in `code/22`);
#   * `models$M2` built from the frozen item table, with F117's D2/D3
#     cross-loading taken literally under the default `--f117 both`;
#   * `estimator = "WLSMV"`, `missing = "pairwise"`, `std.lv = TRUE`,
#     `se = "none"`, `group.equal` per rung;
#   * a cache key byte-identical to `06`'s, so fits either script produced are
#     reused rather than recomputed, and the k12 fits already on disk let this
#     script be validated against a known published result before it is trusted
#     with a multi-day run.
#
# WHAT IT DOES NOT DO. It does not compute deltas. Each rung's measures go to
# JSON and the comparison is made downstream, because a delta between two rungs
# fitted days apart must be recomputed from stored unrounded values, never
# carried in a variable.
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
step    <- getarg("--step")
ncty    <- as.integer(getarg("--countries", "39"))
variant <- getarg("--variant", "primary")
f117    <- getarg("--f117", "both")
dry     <- "--dry-run" %in% args
if (is.null(step) || !step %in% c("configural", "metric", "scalar"))
  stop("usage: --step configural|metric|scalar [--countries 39|12] [--dry-run]", call. = FALSE)

dest <- file.path(ROOT, "supplement/analysis",
                  sprintf("registered-ladder-measures-%s.json", variant))

# --- refuse to redo ----------------------------------------------------------------------------
# Measures on a fit this size are hours. Recomputing them cannot change the number.
skey <- if (ncty < 39) sprintf("%s_k%d", step, ncty) else step
if (file.exists(dest) && !dry) {
  prev <- fromJSON(dest, simplifyVector = FALSE)
  if (!is.null(prev$steps[[skey]]$cfi.scaled)) {
    cat(sprintf("%s already measured (cfi.scaled = %.4f) in %s -- nothing to do\n",
                skey, prev$steps[[skey]]$cfi.scaled, basename(dest)))
    quit(status = 0)
  }
}

# --- data, prepared exactly as 06 does -----------------------------------------------------------
meta  <- fromJSON(file.path(ROOT, "data/derived", sprintf("pii-frame-%s.meta.json", variant)))
d     <- read.csv(file.path(ROOT, "data/derived", sprintf("pii-frame-%s.csv", variant)),
                  stringsAsFactors = FALSE)
items <- meta$items
for (v in meta$reverse_keyed) {
  if (!v %in% names(d)) next
  rng <- range(d[[v]], na.rm = TRUE)
  d[[v]] <- rng[1] + rng[2] - d[[v]]
}
ordvars <- unique(items$variable)
for (v in ordvars) d[[v]] <- ordered(d[[v]])

by_dim <- function(dd) items$variable[items$dimension == dd]
f      <- function(name, vs) paste0(name, " =~ ", paste(vs, collapse = " + "))
D1 <- by_dim("D1"); D2 <- by_dim("D2"); D3 <- by_dim("D3")
shared <- intersect(D2, D3)
if (length(shared)) {
  cat(sprintf("shared indicator(s) across D2/D3: %s  [assignment: %s]\n",
              paste(shared, collapse = ", "), f117))
  if (f117 == "d2only") D3 <- setdiff(D3, shared)
  if (f117 == "d3only") D2 <- setdiff(D2, shared)
}
M2 <- paste(f("D1", D1), f("D2", D2), f("D3", D3), sep = "\n")

# Category collapsing: scope is EVERY country in the frame, filter afterwards. See header.
MIN_PER_GROUP <- 1L
dinv <- d
n_collapsed <- 0L; n_merges <- 0L
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
    dinv[[v]] <- ordered(x); n_collapsed <- n_collapsed + 1L; n_merges <- n_merges + merges
  }
}
cat(sprintf("collapsed %d items, %d merges (min %d per group, scope = all %d countries)\n",
            n_collapsed, n_merges, MIN_PER_GROUP, length(unique(d$country))))

cnt  <- table(dinv$country)
keep <- names(cnt)[cnt >= 200]
if (ncty < length(keep)) {              # validation route: reproduce 06's seeded k12 draw exactly
  set.seed(20260810)
  keep <- sort(sample(keep, min(ncty, length(keep))))
  cat(sprintf("SUBSET (seed 20260810): %d countries: %s\n",
              length(keep), paste(keep, collapse = ", ")))
}
dg <- dinv[dinv$country %in% keep, ]

steps <- list(configural = NULL, metric = "loadings",
              scalar = c("loadings", "thresholds"))
CACHE <- file.path(ROOT, "supplement/analysis/.fitcache")
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)
key <- file.path(CACHE, sprintf("%s-%s-inv%s-%s.rds", variant, f117,
                                if (ncty < 39) paste0("-k", length(keep)) else "", step))

cat(sprintf("REGISTERED LADDER / %s : %d indicators, %d factors, %d countries, %d rows\n",
            step, length(ordvars), 3L, length(keep), nrow(dg)))
cat(sprintf("  cache key : %s  [%s]\n", basename(key),
            if (file.exists(key)) sprintf("EXISTS, %.0f MB", file.size(key) / 1e6) else "absent"))
cat(sprintf("  group.equal: %s\n",
            if (is.null(steps[[step]])) "(none)" else paste(steps[[step]], collapse = ", ")))
if (dry) { cat("  --dry-run: nothing fitted\n"); quit(status = 0) }

if (file.exists(key)) {
  cat("  reading cached fit ... "); flush.console()
  fit <- readRDS(key); cat("ok\n")
} else {
  cat("  fitting ... "); flush.console(); t0 <- Sys.time()
  fit <- tryCatch(
    cfa(M2, data = dg[, c("country", ordvars)], group = "country", estimator = "WLSMV",
        ordered = ordvars, missing = "pairwise", std.lv = TRUE, se = "none",
        group.equal = steps[[step]]),
    error = function(e) { cat("FAILED:", conditionMessage(e), "\n"); NULL })
  if (is.null(fit)) quit(status = 4)
  cat(sprintf("%.0f min\n", as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  saveRDS(fit, key)                      # before measures: the fit is the irreplaceable part
  cat(sprintf("  cached %.0f MB\n", file.size(key) / 1e6))
}

FITM <- c("chisq.scaled", "df.scaled", "pvalue.scaled", "cfi.scaled",
          "tli.scaled", "rmsea.scaled", "srmr")
cat("  measures ... "); flush.console(); t1 <- Sys.time()
conv <- isTRUE(tryCatch(lavInspect(fit, "converged"), error = function(e) FALSE))
m <- tryCatch(fitMeasures(fit, FITM),
              error = function(e) setNames(rep(NA_real_, length(FITM)), FITM))
mins <- as.numeric(difftime(Sys.time(), t1, units = "mins"))
cat(sprintf("%.0f min  converged=%s  cfi.scaled=%.4f\n", mins, conv,
            unname(m[["cfi.scaled"]])))

out <- if (file.exists(dest)) fromJSON(dest, simplifyVector = FALSE) else
  list(model = "M2 (three-factor, 51 indicators)",
       purpose = paste("the pre-registered invariance ladder, fitted one rung per process;",
                       "rungs at 39 countries ARE the registered test, rungs at fewer are the",
                       "subset diagnostic and are keyed separately"),
       forced_deviations = list(
         category_collapsing = paste("minimal merging until no category is empty in any country;",
                                     "required by lavaan, logged in preregistration Sec. 11"),
         se_none = paste("standard errors not computed; the invariance decision is a delta in",
                         "scaled CFI and no SE is consumed downstream")),
       variant = variant, f117 = f117, steps = list())
out$run_utc <- format(Sys.time(), tz = "UTC", usetz = TRUE)
out$steps[[skey]] <- c(
  list(step = step, registered = (ncty >= 39), converged = conv,
       n_countries = length(keep), n_indicators = length(ordvars),
       fit_minutes_measures = round(mins, 1), cache_file = basename(key)),
  as.list(round(m, 4)))
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
