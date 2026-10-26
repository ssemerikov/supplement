#!/usr/bin/env Rscript
# =============================================================================
# Admissibility audit of the fitted single-group models
#
#   Rscript code/07_admissibility_check.R [--variant primary] [--f117 both]
#
# WHY THIS EXISTS AS A SEPARATE SCRIPT. The full-sample run of
# code/06_cfa_invariance.R emitted three
#
#   lav_object_post_check(): covariance matrix of latent variables is not
#   positive definite
#
# warnings to stderr, with no indication of which models produced them. A
# warning that cannot be attributed to a model is not a disclosable fact, and
# "some model somewhere was inadmissible" is exactly the sentence a reviewer
# will not accept. This script attributes every one of them, from the cached
# fits, without refitting anything.
#
# It reads only supplement/analysis/.fitcache/*.rds. It therefore does not
# repeat the Tier-2 gate check in 06: it computes no new estimate, it only
# reports properties of estimates that already passed the gate.
#
# Loads one fit at a time and releases it: see the memory note in
# docs/environment-verification.md. Eight fits held at once is what killed the
# original run.
# =============================================================================

suppressWarnings(suppressMessages({
  .lib <- path.expand("~/R/x86_64-pc-linux-gnu-library/4.6")
  if (dir.exists(.lib)) .libPaths(c(.lib, .libPaths()))
  library(lavaan); library(jsonlite)
}))

ROOT <- normalizePath(file.path(dirname(sub("--file=", "",
        grep("--file=", commandArgs(FALSE), value = TRUE)[1])), ".."))
if (is.na(ROOT) || !dir.exists(ROOT)) ROOT <- normalizePath("..")

args    <- commandArgs(trailingOnly = TRUE)
getarg  <- function(flag, default) {
  i <- match(flag, args); if (!is.na(i) && length(args) > i) args[i + 1] else default
}
variant <- getarg("--variant", "primary")
f117    <- getarg("--f117", "both")

CACHE  <- file.path(ROOT, "supplement/analysis/.fitcache")
MODELS <- c("M0", "M0_12", "M1", "M1b", "M2", "M2b", "M2m", "M4")

# Models whose latent covariance matrix is singular BY CONSTRUCTION: phi is
# fixed to 1, so the matrix is rank-deficient whatever the data say. An
# inadmissibility warning from these is a property of the constraint, not a
# symptom of a problem, and is the whole point of fitting them.
BY_DESIGN <- c("M1b", "M2b")

out <- list()
for (m in MODELS) {
  f <- file.path(CACHE, sprintf("%s-%s-%s.rds", variant, f117, m))
  if (!file.exists(f)) { cat(sprintf("%-6s  not fitted\n", m)); next }
  fit <- readRDS(f)

  # lavInspect(fit, "post.check") re-runs lavaan's own admissibility test and
  # warns exactly as the fit did. Capturing the warning rather than the return
  # value alone keeps the attribution tied to lavaan's criterion, not to a
  # reimplementation of it that could drift.
  msg <- NULL
  ok  <- withCallingHandlers(lavInspect(fit, "post.check"),
           warning = function(cond) {
             msg <<- c(msg, trimws(gsub("\\s+", " ", conditionMessage(cond))))
             invokeRestart("muffleWarning")
           })

  cv       <- lavInspect(fit, "cov.lv")
  ev       <- eigen(cv, only.values = TRUE)$values
  theta    <- diag(lavInspect(fit, "theta"))
  loadings <- lavInspect(fit, "std")$lambda

  out[[m]] <- list(
    post_check_passed   = unname(ok),
    warning             = if (is.null(msg)) NA else paste(msg, collapse = " | "),
    n_latent            = nrow(cv),
    min_eigenvalue_covlv= round(min(ev), 6),
    latent_correlations = round(cov2cor(cv), 4),
    min_residual_var    = round(min(theta), 6),
    heywood_negative_var= sum(theta < 0),
    max_abs_std_loading = round(max(abs(loadings)), 4),
    singular_by_design  = m %in% BY_DESIGN
  )

  cat(sprintf("%-6s  post.check=%-5s  min.eigen(cov.lv)=% .6f  min.resid.var=%.4f  %s\n",
              m, ok, min(ev), min(theta),
              if (!ok && m %in% BY_DESIGN) "<- inadmissible BY CONSTRUCTION (phi fixed to 1)"
              else if (!ok) "<- INADMISSIBLE, NOT BY DESIGN: investigate before reporting"
              else ""))
  rm(fit, cv, theta, loadings); invisible(gc())
}

failed     <- names(out)[!vapply(out, function(x) x$post_check_passed, logical(1))]
unexpected <- setdiff(failed, BY_DESIGN)

res <- list(
  run_utc      = format(Sys.time(), tz = "UTC", usetz = TRUE),
  variant      = variant,
  f117         = f117,
  R_version    = R.version.string,
  lavaan       = as.character(packageVersion("lavaan")),
  models       = out,
  failed       = failed,
  failed_by_design = intersect(failed, BY_DESIGN),
  failed_unexpectedly = unexpected,
  interpretation = paste(
    "A model with phi fixed to 1 has a rank-deficient latent covariance matrix",
    "by construction, so an inadmissibility warning from M1b or M2b carries no",
    "information about the data. It does, however, mean the chi-square",
    "difference test that uses that model as the constrained comparison is",
    "taken against an inadmissible solution, which must be disclosed: the",
    "qualitative conclusion (the two factors cannot be one) is strengthened by",
    "the inadmissibility, while the exact p-value should not be read as an",
    "ordinary likelihood-ratio p-value.")
)

dest <- file.path(ROOT, sprintf("supplement/analysis/admissibility-%s.json", variant))
write(toJSON(res, auto_unbox = TRUE, digits = 6, pretty = TRUE, na = "null"), dest)
cat("\nfailed post-check:", if (length(failed)) paste(failed, collapse = ", ") else "none", "\n")
cat("failed unexpectedly:",
    if (length(unexpected)) paste(unexpected, collapse = ", ") else "none", "\n")
cat("wrote", sub(paste0(ROOT, "/"), "", dest, fixed = TRUE), "\n")
