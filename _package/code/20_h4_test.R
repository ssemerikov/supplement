#!/usr/bin/env Rscript
# =============================================================================
# 20_h4_test.R -- H4, the Jellyby prediction (preregistration.md Sec. 6.5).
#
#   Rscript code/20_h4_test.R --stage probes       [--variant primary]
#   Rscript code/20_h4_test.R --stage incremental  [--variant primary]
#
# THE HYPOTHESIS. Popper's Mrs Jellyby is genuinely altruistic yet directs her
# concern at "anonymous groups rather than concrete individuals". H4 predicts
# that concrete and anonymous other-regard are separable rather than collinear,
# and that their difference is not reducible to D1 or D2. The registration
# specifies three probes and two tests: a two-factor versus one-factor comparison
# within each probe, then incremental validity over D1 and D2.
#
# WHAT IS ESTIMABLE, AND WHAT IS NOT. Probes 1 and 2 have two indicators per
# pole; a two-factor model with a free inter-factor correlation is identified on
# four indicators and is fitted. **Probe 3 has ONE indicator per pole.** A
# two-factor model on two indicators is not identified -- there is no comparison
# to run, at any sample size -- so probe 3 is reported as not estimable rather
# than approximated by something else. That matters for the verdict: the
# registered prediction is "at least two of the three probes", and only two can
# be tested, so the strongest available outcome is 2 of 2 estimable and the rule
# cannot be satisfied on its own terms. Recorded here, not argued away.
#
# DECISION RULES, fixed before the fits and copied from the registration's own
# language for comparable tests elsewhere in the paper:
#   separable  <=>  the one-factor model is rejected against the two-factor at
#                   alpha = .01 AND phi(concrete, anonymous) <= .85
#   incremental <=> a model constraining each pole to relate identically to D1
#                   and to D2 is rejected against the free model at alpha = .01
#
# H4 IS EXPLICITLY NON-THREATENING TO H1-H3: "A null here does not threaten
# H1-H3; it is reported as a limit on how far Popper's illustration
# operationalises." Nothing below feeds a licence.
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
stage   <- getarg("--stage", "probes")
set.seed(20260810)

meta <- fromJSON(file.path(ROOT, "data/derived", sprintf("h4-frame-%s.meta.json", variant)),
                 simplifyVector = FALSE)
d <- read.csv(file.path(ROOT, "data/derived", sprintf("h4-frame-%s.csv", variant)),
              stringsAsFactors = FALSE)

for (v in unlist(meta$reverse_keyed)) {
  if (!v %in% names(d)) next
  rng <- range(d[[v]], na.rm = TRUE)
  d[[v]] <- rng[1] + rng[2] - d[[v]]
}

probes <- meta$probes
pv <- function(p, pole) unlist(probes[[p]][[pole]])
allprobe <- unique(unlist(lapply(names(probes),
                                 function(p) c(pv(p, "concrete"), pv(p, "anonymous")))))
d12 <- unlist(meta$d1_d2_variables)
for (v in unique(c(allprobe, d12))) d[[v]] <- ordered(d[[v]])

FITM <- c("chisq.scaled","df.scaled","pvalue.scaled","cfi.scaled",
          "tli.scaled","rmsea.scaled","srmr")
CACHE <- file.path(ROOT, "supplement/analysis/.fitcache")
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)
f <- function(name, vs) paste0(name, " =~ ", paste(vs, collapse = " + "))
fm <- function(fit) as.list(round(fitMeasures(fit, FITM), 4))
phi <- function(fit, x, y) {
  s <- standardizedSolution(fit)
  r <- s[s$op == "~~" & ((s$lhs == x & s$rhs == y) | (s$lhs == y & s$rhs == x)), "est.std"]
  if (length(r) == 1) round(r, 4) else NA_real_
}
fitmod <- function(nm, syntax, vs) {
  key <- file.path(CACHE, sprintf("%s-h4-%s.rds", variant, nm))
  if (file.exists(key)) { cat(sprintf("  %-18s cached\n", nm)); return(readRDS(key)) }
  cat(sprintf("  %-18s fitting ... ", nm)); t0 <- Sys.time()
  fit <- cfa(syntax, data = d, estimator = "WLSMV", ordered = vs,
             missing = "pairwise", std.lv = TRUE)
  cat(sprintf("%.1f min\n", as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  saveRDS(fit, key); fit
}

dest <- file.path(ROOT, "supplement/analysis", sprintf("h4-jellyby-%s.json", variant))
out <- if (file.exists(dest)) fromJSON(dest, simplifyVector = FALSE) else
  list(registered = TRUE,
       registered_in = "preregistration.md 6.5",
       variant = variant, seed = 20260810,
       R_version = R.version.string,
       source_sha256 = meta$source_sha256,
       decision_rules = list(
         separable = "one-factor rejected against two-factor at alpha = .01 AND phi <= .85",
         incremental = "equal-relations model rejected against the free model at alpha = .01"),
       note = paste("H4 is exploratory-confirmatory and threatens no other hypothesis.",
                    "Probe 3 has one indicator per pole and is not identified as a",
                    "two-factor model; it is reported as not estimable."))

if (stage == "probes") {
  res <- list()
  for (p in names(probes)) {
    cc <- pv(p, "concrete"); aa <- pv(p, "anonymous"); vs <- c(cc, aa)
    cat(sprintf("\nprobe %s: concrete %s | anonymous %s\n", p,
                paste(cc, collapse = ","), paste(aa, collapse = ",")))
    if (length(cc) < 2 || length(aa) < 2) {
      cat("  NOT ESTIMABLE: fewer than two indicators on a pole; a two-factor model on ",
          length(vs), " indicators is not identified\n", sep = "")
      res[[p]] <- list(probe = p, concrete = cc, anonymous = aa,
                       estimable = FALSE,
                       reason = paste("fewer than two indicators on a pole; a two-factor",
                                      "model is not identified at any sample size"))
      next
    }
    f1 <- fitmod(paste0(p, "-1f"), f("GEN", vs), vs)
    f2 <- fitmod(paste0(p, "-2f"),
                 paste(f("CONC", cc), f("ANON", aa), sep = "\n"), vs)
    lr <- lavTestLRT(f1, f2)
    pval <- lr[["Pr(>Chisq)"]][2]
    ph <- phi(f2, "CONC", "ANON")
    dcfi <- fm(f2)$cfi.scaled - fm(f1)$cfi.scaled
    sep <- isTRUE(pval < .01) && isTRUE(abs(ph) <= .85)
    cat(sprintf("  phi(concrete,anonymous) = %+.4f   p = %.3g   dCFI = %+.4f   separable: %s\n",
                ph, pval, dcfi, sep))
    res[[p]] <- list(probe = p, concrete = cc, anonymous = aa, estimable = TRUE,
                     fit_one_factor = fm(f1), fit_two_factor = fm(f2),
                     phi_concrete_anonymous = ph,
                     p_one_factor_rejected = signif(pval, 6),
                     deltaCFI = round(dcfi, 4),
                     one_factor_rejected_at_.01 = isTRUE(pval < .01),
                     phi_le_.85 = isTRUE(abs(ph) <= .85),
                     separable = sep)
  }
  out$probes <- res
  est <- Filter(function(r) isTRUE(r$estimable), res)
  out$n_probes_estimable <- length(est)
  out$n_probes_separable <- sum(vapply(est, function(r) isTRUE(r$separable), logical(1)))
  out$registered_rule_note <- paste(
    "The registered prediction is 'at least two of the three probes'.", length(est),
    "of 3 are estimable, so the rule cannot be met on its own terms whatever the result;",
    "the count of separable probes among the estimable ones is reported instead.")
  out$run_utc_probes <- format(Sys.time(), tz = "UTC", usetz = TRUE)
}

if (stage == "incremental") {
  est <- names(Filter(function(p) length(unlist(p$concrete)) >= 2 &&
                                  length(unlist(p$anonymous)) >= 2, probes))
  cc <- unlist(lapply(est, pv, pole = "concrete"))
  aa <- unlist(lapply(est, pv, pole = "anonymous"))
  D1 <- unlist(lapply(meta$d1_d2_variables, identity))
  # D1 and D2 membership comes from the PII frame's own item table, read back through the
  # H4 metadata, so the two analyses cannot disagree about what D1 is.
  pii <- fromJSON(file.path(ROOT, "data/derived",
                            sprintf("pii-frame-%s.meta.json", variant)), simplifyVector = FALSE)
  itv <- vapply(pii$items, function(i) i$variable, "")
  itd <- vapply(pii$items, function(i) i$dimension, "")
  v1 <- unique(itv[itd == "D1"]); v2 <- unique(itv[itd == "D2"])
  vs <- unique(c(cc, aa, v1, v2))
  cat(sprintf("incremental validity: %d probe indicators + D1 (%d) + D2 (%d) = %d\n",
              length(c(cc, aa)), length(v1), length(v2), length(vs)))
  base <- paste(f("CONC", cc), f("ANON", aa), f("D1", v1), f("D2", v2), sep = "\n")
  eq <- paste(base,
              "CONC ~~ a*D1", "ANON ~~ a*D1",
              "CONC ~~ b*D2", "ANON ~~ b*D2", sep = "\n")
  jf <- fitmod("joint-free", base, vs)
  je <- fitmod("joint-equal", eq, vs)
  lr <- lavTestLRT(je, jf)
  pval <- lr[["Pr(>Chisq)"]][2]
  inc <- isTRUE(pval < .01)
  cat(sprintf("  phi(CONC,D1)=%+.4f  phi(ANON,D1)=%+.4f  phi(CONC,D2)=%+.4f  phi(ANON,D2)=%+.4f\n",
              phi(jf, "CONC", "D1"), phi(jf, "ANON", "D1"),
              phi(jf, "CONC", "D2"), phi(jf, "ANON", "D2")))
  cat(sprintf("  equal-relations model rejected: p = %.3g   incremental: %s\n", pval, inc))
  out$incremental <- list(
    probes_pooled = est,
    fit_free = fm(jf), fit_equal = fm(je),
    phi_CONC_D1 = phi(jf, "CONC", "D1"), phi_ANON_D1 = phi(jf, "ANON", "D1"),
    phi_CONC_D2 = phi(jf, "CONC", "D2"), phi_ANON_D2 = phi(jf, "ANON", "D2"),
    phi_CONC_ANON = phi(jf, "CONC", "ANON"),
    p_equal_rejected = signif(pval, 6),
    incremental_over_D1_D2 = inc)
  out$run_utc_incremental <- format(Sys.time(), tz = "UTC", usetz = TRUE)
}

write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
