#!/usr/bin/env Rscript
# Admissibility audit of the ESS replication's single-group fits.
#
#   Rscript code/31_ess_admissibility.R
#
# Exactly the job code/07 does for the primary, on the ESS cache, and for the same reason: the ESS
# run emitted three "covariance matrix of latent variables is not positive definite" warnings with
# no indication of which models produced them, and an unattributed warning is not a disclosable
# fact. Reads only cached fits; estimates nothing.

suppressWarnings(suppressMessages({
  .lib <- path.expand("~/R/x86_64-pc-linux-gnu-library/4.6")
  if (dir.exists(.lib)) .libPaths(c(.lib, .libPaths()))
  library(lavaan); library(jsonlite)
}))

ROOT <- normalizePath(file.path(dirname(sub("--file=", "",
        grep("--file=", commandArgs(FALSE), value = TRUE)[1])), ".."))
CACHE  <- file.path(ROOT, "supplement/analysis/.essfitcache")
MODELS <- c("M0", "M0_12", "M1", "M1b", "M2", "M2b")
# phi fixed to 1 makes the latent covariance matrix rank-deficient whatever the data say.
BY_DESIGN <- c("M1b", "M2b")

out <- list()
for (m in MODELS) {
  f <- file.path(CACHE, paste0(m, ".rds"))
  if (!file.exists(f)) { cat(sprintf("%-6s  not fitted\n", m)); next }
  fit <- readRDS(f)
  msg <- NULL
  ok  <- withCallingHandlers(lavInspect(fit, "post.check"),
           warning = function(cond) {
             msg <<- c(msg, trimws(gsub("\\s+", " ", conditionMessage(cond))))
             invokeRestart("muffleWarning") })
  cv <- lavInspect(fit, "cov.lv"); ev <- eigen(cv, only.values = TRUE)$values
  theta <- diag(lavInspect(fit, "theta")); lam <- lavInspect(fit, "std")$lambda
  out[[m]] <- list(post_check_passed = unname(ok),
                   warning = if (is.null(msg)) NA else paste(msg, collapse = " | "),
                   n_latent = nrow(cv), min_eigenvalue_covlv = round(min(ev), 6),
                   latent_correlations = round(cov2cor(cv), 4),
                   min_residual_var = round(min(theta), 6),
                   heywood_negative_var = sum(theta < 0),
                   max_abs_std_loading = round(max(abs(lam)), 4),
                   singular_by_design = m %in% BY_DESIGN)
  cat(sprintf("%-6s  post.check=%-5s  min.eigen=% .6f  min.resid.var=% .4f  heywood=%d  %s\n",
              m, ok, min(ev), min(theta), sum(theta < 0),
              if (!ok && m %in% BY_DESIGN) "<- inadmissible BY CONSTRUCTION (phi fixed to 1)"
              else if (!ok) "<- INADMISSIBLE, NOT BY DESIGN: do not report quantities from it" else ""))
  rm(fit, cv, theta, lam); invisible(gc())
}
failed <- names(out)[!vapply(out, function(x) x$post_check_passed, logical(1))]
res <- list(run_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
            analysis = "ESS structural replication", registered = FALSE,
            R_version = R.version.string, lavaan = as.character(packageVersion("lavaan")),
            models = out, failed = failed,
            failed_by_design = intersect(failed, BY_DESIGN),
            failed_unexpectedly = setdiff(failed, BY_DESIGN))
write(toJSON(res, auto_unbox = TRUE, digits = 8, na = "null", pretty = TRUE),
      file.path(ROOT, "supplement/analysis/ess-admissibility.json"))
cat("\nfailed:", paste(failed, collapse = ", "),
    "| unexpected:", paste(setdiff(failed, BY_DESIGN), collapse = ", "), "\n")
