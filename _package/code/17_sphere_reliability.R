#!/usr/bin/env Rscript
# =============================================================================
# 17_sphere_reliability.R -- per-sphere reliability, reported honestly.
#
#   Rscript code/17_sphere_reliability.R [--variant primary]
#
# WHY THIS EXISTS. Pre-registration §6.6 commits to reporting per-sphere
# reliability and to "dropping a sphere rather than padding it", and CLAUDE.md
# repeats the commitment. The manuscript reports the education sphere's item
# failures but no reliability coefficient anywhere. That is a registered
# reporting obligation left unmet, and it is the cheapest of the outstanding
# ones to meet, because everything it needs already exists.
#
# WHAT IT COMPUTES, per (dimension x sphere) cell and per dimension:
#
#   ordinal alpha -- standardised alpha on the POLYCHORIC correlation matrix,
#     alpha = k*rbar / (1 + (k-1)*rbar). Polychoric rather than Pearson because
#     the indicators are ordinal with as few as two categories, and Pearson
#     alpha on binary items is attenuated by exactly the artefact the
#     child-qualities battery would introduce.
#
#   categorical omega -- (sum lambda)^2 / ((sum lambda)^2 + sum(1 - lambda^2)),
#     from the M2 standardised loadings in m2-loadings-primary.json. Omega is
#     reported alongside alpha because alpha assumes tau-equivalence, which the
#     loading spread in this pool plainly violates.
#
# BOTH ARE REPORTED, AND NEITHER IS SELECTED AFTER THE FACT. Where they
# disagree, the disagreement is the finding.
#
# A cell of one item has no internal consistency; it is reported as such with
# NA rather than omitted, so a reader can see the grid is sparse rather than
# infer it from absences. Reverse-keyed items are reversed first, using the same
# observed-range rule as code/06, or a reversed item would drag alpha down for a
# reason that has nothing to do with the sphere.
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
variant <- getarg("--variant", "primary")

csv  <- file.path(ROOT, "data/derived", sprintf("pii-frame-%s.csv", variant))
meta <- fromJSON(file.path(ROOT, "data/derived", sprintf("pii-frame-%s.meta.json", variant)))
lt   <- fromJSON(file.path(ROOT, "supplement/analysis", sprintf("m2-loadings-%s.json", variant)))
if (!file.exists(csv)) stop("run code/05_build_analysis_frame.py first", call. = FALSE)

d     <- read.csv(csv, stringsAsFactors = FALSE)
items <- meta$items
for (v in meta$reverse_keyed) {
  if (!v %in% names(d)) next
  rng <- range(d[[v]], na.rm = TRUE)
  d[[v]] <- rng[1] + rng[2] - d[[v]]
}

lam <- setNames(lt$loadings$est.std,
                paste(lt$loadings$factor, lt$loadings$variable, sep = "|"))

# alpha from a correlation matrix is the standardised form; with k items and mean off-diagonal
# correlation rbar it is exactly k*rbar/(1+(k-1)*rbar). Computing it from the matrix rather than
# from raw sums is what lets the polychoric version be used at all.
alpha_from_R <- function(R) {
  k <- ncol(R)
  if (k < 2) return(NA_real_)
  rbar <- mean(R[upper.tri(R)])
  k * rbar / (1 + (k - 1) * rbar)
}

omega_from_lambda <- function(l) {
  if (length(l) < 2) return(NA_real_)
  s <- sum(l)
  s^2 / (s^2 + sum(1 - l^2))
}

cells <- unique(items[, c("dimension", "sphere")])
cells <- cells[order(cells$dimension, cells$sphere), ]
rows <- list()

report <- function(tag, dim, sphere, vs) {
  vs <- unique(vs)
  k <- length(vs)
  l <- unname(lam[paste(dim, vs, sep = "|")])
  a <- NA_real_; rbar <- NA_real_
  if (k >= 2) {
    sub <- d[, vs, drop = FALSE]
    for (v in vs) sub[[v]] <- ordered(sub[[v]])
    R <- tryCatch(lavCor(sub, ordered = vs, missing = "pairwise"),
                  error = function(e) NULL)
    if (!is.null(R)) { a <- alpha_from_R(R); rbar <- mean(R[upper.tri(R)]) }
  }
  o <- omega_from_lambda(l)
  # MIXED SIGNS ARE THE HEADLINE, NOT A NUISANCE. Both coefficients assume the items are
  # keyed in one direction. Where a cell's loadings have both signs, omega collapses towards
  # zero because (sum lambda)^2 cancels, and alpha can go negative because the mean polychoric
  # correlation does. Neither number is then a reliability; both are evidence that the cell is
  # not a scale. Flagged explicitly so no reader can take a collapsed omega for a computed
  # low reliability, and so no future edit can quote one without the flag.
  mixed <- k >= 2 && any(l > 0) && any(l < 0)
  # A counterfactual, clearly labelled and never reported as the cell's reliability: what
  # omega would be if every negatively loading item were re-keyed. It separates "wrong sign"
  # from "no signal", which is the distinction the manuscript's own diagnostic rests on.
  o_aligned <- if (mixed) omega_from_lambda(abs(l)) else NA_real_
  cat(sprintf("  %-4s %-14s k=%2d  alpha=%7s  omega=%6s  mean|lambda|=%5.3f  weak=%d  neg=%d%s\n",
              dim, sphere, k,
              ifelse(is.na(a), "   --  ", sprintf("%.3f", a)),
              ifelse(is.na(o), "  --  ", sprintf("%.3f", o)),
              mean(abs(l)), sum(abs(l) < .30), sum(l < 0),
              ifelse(mixed, sprintf("  MIXED SIGNS (aligned omega %.3f)", o_aligned), "")))
  list(scope = tag, dimension = dim, sphere = sphere, n_items = k,
       variables = vs,
       ordinal_alpha = if (is.na(a)) NULL else round(a, 4),
       mean_polychoric_r = if (is.na(rbar)) NULL else round(rbar, 4),
       categorical_omega = if (is.na(o)) NULL else round(o, 4),
       mean_abs_loading = round(mean(abs(l)), 4),
       n_weak_items = sum(abs(l) < .30),
       n_negative_loadings = sum(l < 0),
       mixed_sign_loadings = mixed,
       omega_if_signs_aligned = if (is.na(o_aligned)) NULL else round(o_aligned, 4),
       single_item = k < 2)
}

cat("per dimension x sphere\n")
for (i in seq_len(nrow(cells))) {
  dd <- cells$dimension[i]; ss <- cells$sphere[i]
  vs <- items$variable[items$dimension == dd & items$sphere == ss]
  rows[[length(rows) + 1]] <- report("cell", dd, ss, vs)
}
cat("per dimension (all spheres pooled)\n")
for (dd in sort(unique(items$dimension))) {
  rows[[length(rows) + 1]] <- report("dimension", dd, "ALL",
                                     items$variable[items$dimension == dd])
}

# The retention rule of §6.6 is about country coverage, not reliability, and is checked
# elsewhere. What belongs here is the honest verdict per cell, on a threshold fixed before
# the numbers were seen: .70 is the conventional floor for a scale used comparatively.
THRESH <- .70
verdict <- lapply(rows, function(r) {
  if (isTRUE(r$single_item)) return("single item -- no internal consistency defined")
  a <- if (is.null(r$ordinal_alpha)) NA else r$ordinal_alpha
  o <- if (is.null(r$categorical_omega)) NA else r$categorical_omega
  if (is.na(a) || is.na(o)) return("not computable")
  # The mixed-sign verdict comes FIRST and overrides the numbers, because a coefficient
  # computed across items that load in opposite directions is not a reliability at all.
  if (isTRUE(r$mixed_sign_loadings))
    return("not a scale -- loadings run in both directions; neither coefficient is a reliability")
  if (a >= THRESH && o >= THRESH) "adequate on both"
  else if (a < THRESH && o < THRESH) "below .70 on both"
  else "disagreement between alpha and omega"
})
for (i in seq_along(rows)) rows[[i]]$verdict <- verdict[[i]]

out <- list(
  run_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  registered = TRUE,
  registered_in = "preregistration.md 6.6 -- per-sphere reliability reported honestly, a sphere dropped rather than padded",
  variant = variant,
  n_rows = nrow(d),
  threshold = THRESH,
  frame_sha256 = meta$source_sha256,
  item_table_sha256 = meta$item_table_sha256,
  loading_source = sprintf("m2-loadings-%s.json", variant),
  note = paste("Ordinal alpha is standardised alpha on the polychoric correlation matrix;",
               "categorical omega is computed from the M2 standardised loadings. Both are",
               "reported for every cell and neither is chosen after the fact."),
  cells = rows)

dest <- file.path(ROOT, "supplement/analysis", sprintf("sphere-reliability-%s.json", variant))
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")

# The JSON is the artefact the verifier checks; this is the same content as a table a reader
# can read, and it is what the manuscript cites as Supplement S7. Generated, never hand-kept,
# so the two cannot drift.
if (identical(variant, "primary")) {
  fmt <- function(x) if (is.null(x) || is.na(x)) "--" else sprintf("%.3f", x)
  md <- c(
    "# Supplement S7 — per-sphere reliability",
    "",
    sprintf("Generated by `code/17_sphere_reliability.R` on %s. Do not edit by hand.",
            out$run_utc),
    sprintf("Analysis frame SHA-256 `%s`; item table SHA-256 `%s`.",
            substr(out$frame_sha256, 1, 16), substr(out$item_table_sha256, 1, 16)),
    "",
    paste("Registered in `preregistration.md` §6.6: per-sphere reliability is reported honestly",
          "and a sphere is dropped rather than padded. Ordinal alpha is standardised alpha on the",
          "polychoric correlation matrix; categorical omega is computed from the M2 standardised",
          "loadings. **Where a cell's loadings run in both directions neither coefficient is a",
          "reliability**, and the verdict column says so instead of quoting the number as one.",
          "The aligned-omega column is a counterfactual — what omega would be if every negatively",
          "loading item were re-keyed — reported as a diagnostic and *not* adopted, because",
          "re-keying items after seeing their loadings is fit-chasing."),
    "",
    "| Scope | Dimension | Sphere | k | ordinal α | categorical ω | mean \\|λ\\| | weak | neg | aligned ω | Verdict |",
    "|---|---|---|--:|--:|--:|--:|--:|--:|--:|---|")
  for (r in rows) {
    md <- c(md, sprintf("| %s | %s | %s | %d | %s | %s | %.3f | %d | %d | %s | %s |",
                        r$scope, r$dimension, r$sphere, r$n_items,
                        fmt(r$ordinal_alpha), fmt(r$categorical_omega),
                        r$mean_abs_loading, r$n_weak_items, r$n_negative_loadings,
                        fmt(r$omega_if_signs_aligned), r$verdict))
  }
  mdest <- file.path(ROOT, "supplement/sphere-reliability-table.md")
  writeLines(md, mdest)
  cat("wrote", sub(paste0(ROOT, "/"), "", mdest), "\n")
}
