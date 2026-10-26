#!/usr/bin/env Rscript
# =============================================================================
# 12_loading_heterogeneity.R -- where does the measurement model fail to travel?
#
#   Rscript code/12_loading_heterogeneity.R [--variant primary]
#
# EXPLORATORY AND NOT PRE-REGISTERED. This analysis was written after the
# registered invariance chain returned a divergent alignment, to answer a
# question the registration does not pose: *which* dimension fails to hold
# across countries, and is the failure structural or sampling noise?
# It is reported as exploratory in the manuscript and no confirmatory claim
# rests on it. See docs/preregistration.md Sec. 11.
#
# THE QUESTION. Fitted country by country, a large share of loadings are
# negative (D2 45%, D3 49%) while the pooled 77k fit has only 3 negative
# loadings in 51. Three explanations are compatible with that:
#
#   (a) sampling noise around loadings that are near zero everywhere;
#   (b) whole-factor orientation -- a latent factor is identified only up to
#       sign within a group, so a country's entire loading vector may be
#       reversed without anything substantive differing;
#   (c) genuine structural difference -- the same item relates to the latent
#       variable in opposite directions in different countries.
#
# Only (c) would license the claim that the construct does not travel, so the
# script eliminates (a) and (b) before reporting anything.
#
#   (a) is tested by banding items on their POOLED loading magnitude. Noise
#       around zero produces ~50% sign disagreement for near-zero loadings and
#       ~0% for strong ones; a flat or rising profile refutes it.
#   (b) is removed by flipping each country's whole factor when its loading
#       vector correlates negatively with the pooled vector, and reporting the
#       RESIDUAL disagreement that survives the flip.
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

pooled_f <- file.path(CACHE, sprintf("%s-both-M2.rds", variant))
if (!file.exists(pooled_f))
  stop("pooled M2 not cached; run 06_cfa_invariance.R --stage single first", call. = FALSE)
pool <- lavInspect(readRDS(pooled_f), "est")$lambda
invisible(gc())

lam <- list()
for (f in list.files(CACHE, pattern = sprintf("^%s-both-cfg-.*\\.rds$", variant),
                     full.names = TRUE)) {
  z <- readRDS(f)
  if (isTRUE(z$converged)) lam[[sub(".*cfg-(.*)\\.rds", "\\1", f)]] <- z$est
}
if (length(lam) < 2)
  stop("per-country configural fits not found; run --stage alignment first", call. = FALSE)
cat(sprintf("pooled M2 + %d per-country configural fits\n\n", length(lam)))

STRONG <- .40   # "strong" = pooled |loading| above this; the band edges are reported anyway
BANDS  <- c(-Inf, .20, .30, .40, Inf)
BANDLB <- c("lt.20", "20to30", "30to40", "gt.40")

out <- list(
  registered = FALSE,
  purpose = paste("exploratory: locate the dimension whose loading pattern fails to replicate",
                  "across countries, after removing per-country factor-orientation"),
  variant = variant,
  run_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  n_countries = length(lam),
  strong_threshold = STRONG,
  pooled_source = basename(pooled_f),
  dimensions = list())

for (dd in c("D1", "D2", "D3")) {
  vs <- intersect(items$variable[items$dimension == dd], rownames(pool))
  pl <- pool[vs, dd]
  L  <- t(sapply(lam, function(g) g$lambda[vs, dd]))
  r  <- apply(L, 1, function(x) cor(x, pl))
  Lf <- L * ifelse(r < 0, -1, 1)          # (b) removed: orientation fixed to the pooled vector

  # (a) tested: sign disagreement as a function of pooled loading magnitude.
  band <- cut(abs(pl), BANDS, labels = BANDLB)
  by_band <- list()
  for (b in BANDLB) {
    k <- which(band == b)
    if (!length(k)) next
    sub <- Lf[, k, drop = FALSE]
    by_band[[b]] <- list(
      n_items = length(k),
      sign_disagreement = round(mean(sweep(sign(sub), 2, sign(pl[k]), "!=")), 4),
      mean_abs_country_loading = round(mean(abs(sub)), 4))
  }

  strong <- which(abs(pl) > STRONG)
  ent <- list(
    n_items = length(vs),
    whole_factor_flips = sum(r < 0),
    abs_r_after_flip = list(lt_0.3 = sum(abs(r) < .3),
                            between = sum(abs(r) >= .3 & abs(r) <= .6),
                            gt_0.6  = sum(abs(r) > .6)),
    by_pooled_loading_band = by_band)
  if (length(strong)) {
    sub <- Lf[, strong, drop = FALSE]
    per <- apply(sweep(sign(sub), 2, sign(pl[strong]), "!="), 1, mean)
    ent$strong_items <- list(
      n_items = length(strong),
      residual_sign_disagreement = round(mean(sweep(sign(sub), 2, sign(pl[strong]), "!=")), 4),
      mean_abs_country_loading = round(mean(abs(sub)), 4),
      countries_zero_disagreement = sum(per == 0),
      countries_above_25pct = sum(per > .25))
  }
  out$dimensions[[dd]] <- ent

  cat(sprintf("%s (%d items)\n", dd, length(vs)))
  cat(sprintf("   whole-factor flips %d ; |r|>.6 after flip %d of %d\n",
              ent$whole_factor_flips, ent$abs_r_after_flip$gt_0.6, length(lam)))
  if (!is.null(ent$strong_items))
    cat(sprintf("   strong items (n=%d): residual disagreement %.1f%% ; %d of %d countries clean\n",
                ent$strong_items$n_items, 100 * ent$strong_items$residual_sign_disagreement,
                ent$strong_items$countries_zero_disagreement, length(lam)))
  cat("\n")
}

dest <- file.path(ROOT, "supplement/analysis",
                  sprintf("loading-heterogeneity-%s.json", variant))
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
