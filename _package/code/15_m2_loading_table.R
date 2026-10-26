#!/usr/bin/env Rscript
# =============================================================================
# 15_m2_loading_table.R -- the complete standardised loading table for M2.
#
#   Rscript code/15_m2_loading_table.R [--variant primary]
#
# WHY THIS EXISTS. `06_cfa_invariance.R` logs only the loadings BELOW .30, because
# that is the pre-registered drop criterion and the drop log is what §6.1 asks
# for. Tier-2 block A forecasts a different threshold -- 52 propositions of the
# form "item X will load at least .40 on its assigned factor" -- and cannot be
# resolved from a list of the sub-.30 offenders alone: an item at .34 is neither
# in the drop log nor above .40, and guessing which side it falls is exactly the
# kind of fabrication this repository forbids.
#
# So this script dumps the whole table. It fits NOTHING: it reads the cached
# single-group M2 and calls `standardizedSolution()`, the same function and the
# same fitted object `06` uses for the drop log, so the 18 sub-.30 rows here must
# reproduce that log exactly. `code/16` asserts that they do.
#
# WHICH M2. The pooled single-group fit over all 77,396 respondents -- the model
# §5 reports as primary. The Tier-2 instrument says "configural three-factor
# model M2", which could also be read as the multi-group configural, and the
# ambiguity is real, so the grounds for choosing are recorded rather than left
# implicit. The panel was told "~77,000 respondents" and one estimator, with no
# mention of a country-level model; and the multi-group configural yields 39
# loadings per item where the proposition asks after one, with no aggregation
# rule anywhere in the instrument. The pooled fit is the only reading under
# which the proposition has a referent at all. `code/16` records the choice and
# the reason in its output.
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
variant <- getarg("--variant", "primary")
f117    <- getarg("--f117", "both")
model   <- getarg("--model", "M2")

# --model M2m extracts the same table from the specification that HONOURS registration
# Decision D3 (a battery method factor orthogonal to the substantive factors). The two are
# both needed: M2 is the model the manuscript reports as target, M2m is the one Decision D3
# describes, and the Tier-2 instrument's own prose describes M2m while calling it M2.
key <- file.path(ROOT, "supplement/analysis/.fitcache",
                 sprintf("%s-%s-%s.rds", variant, f117, model))
if (!file.exists(key)) {
  cat(sprintf("no cached %s fit at %s -- run 06_cfa_invariance.R --stage single first\n",
              model, basename(key)))
  quit(status = 3)
}

cat(sprintf("reading %s (%.1f MB)\n", basename(key), file.size(key) / 1e6))
fit <- readRDS(key)
std <- standardizedSolution(fit)
lam <- std[std$op == "=~", c("lhs", "rhs", "est.std", "se", "pvalue")]
names(lam)[1:2] <- c("factor", "variable")

# The method factor (`MB`) carries no Tier-2 proposition: no item is "assigned" to it, and a
# battery item's own dimension loading is still the one the proposition asks after. Flagged
# rather than dropped, so the scorer's count of substantive rows is checkable, not assumed.
lam$is_method_factor <- lam$factor %in% c("MB", "METH", "MDEM", "M")

# Latent correlations. H2's magnitude condition is a statement about phi(D1,D3), and Decision
# D3 requires the substantive conclusion to survive the method-factor specification, so the
# same coefficient has to be readable from both models without refitting either.
phis <- list()
for (p in list(c("D1", "D2"), c("D1", "D3"), c("D2", "D3"))) {
  r <- std[std$op == "~~" & ((std$lhs == p[1] & std$rhs == p[2]) |
                             (std$lhs == p[2] & std$rhs == p[1])), "est.std"]
  if (length(r) == 1) phis[[paste0("phi_", p[1], "_", p[2])]] <- round(r, 4)
}
if (length(phis)) cat(sprintf("  %s\n", paste(names(phis), unlist(phis),
                                              sep = " = ", collapse = "   ")))

cat(sprintf("  %d loading rows over %d factors (%d method-factor rows)\n",
            nrow(lam), length(unique(lam$factor)), sum(lam$is_method_factor)))
sub30 <- lam[abs(lam$est.std) < .30 & !lam$is_method_factor, ]
cat(sprintf("  |lambda| < .30 : %d   (must equal the 18 in the drop log)\n", nrow(sub30)))
cat(sprintf("  lambda >= .40  : %d of %d substantive rows\n",
            sum(lam$est.std[!lam$is_method_factor] >= .40), sum(!lam$is_method_factor)))

neg <- lam[lam$est.std < 0 & !lam$is_method_factor, ]
cat(sprintf("  negative loadings: %d (of which |lambda| >= .30: %d)\n",
            nrow(neg), sum(abs(neg$est.std) >= .30)))

out <- list(
  run_utc      = format(Sys.time(), tz = "UTC", usetz = TRUE),
  variant      = variant,
  f117         = f117,
  source_fit   = basename(key),
  model        = model,
  model_note   = if (identical(model, "M2m"))
    "M2m -- three correlated factors plus an orthogonal method factor over the democracy battery. This is the specification registration Decision D3 describes, and the one the Tier-2 instrument's prose describes while calling it M2."
    else "M2 -- pooled single-group three-factor model, no method factor. The model the manuscript reports as target.",
  n_rows       = nrow(lam),
  n_substantive = sum(!lam$is_method_factor),
  n_negative   = nrow(neg),
  n_negative_substantial = sum(abs(neg$est.std) >= .30),
  latent_correlations = phis,
  note         = paste("Complete standardised loading table. Produced for Tier-2 block A,",
                       "whose 52 propositions use a .40 threshold that the .30 drop log",
                       "cannot resolve. Read-only: no model is fitted here."),
  loadings     = lam)

dest <- file.path(ROOT, "supplement/analysis",
                  if (identical(model, "M2")) sprintf("m2-loadings-%s.json", variant)
                  else sprintf("%s-loadings-%s.json", tolower(model), variant))
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
