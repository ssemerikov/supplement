#!/usr/bin/env Rscript
# =============================================================================
# 18_battery_excluded_sensitivity.R -- the second half of registration Decision D3.
#
#   Rscript code/18_battery_excluded_sensitivity.R [--variant primary]
#
# WHY. Decision D3 has two clauses. The first -- give the democracy battery its
# own orthogonal method factor -- is honoured by M2m in `06_cfa_invariance.R`.
# The second is "additionally report a sensitivity model with the battery
# excluded entirely. The substantive conclusion must survive both, and if it does
# not, that is reported as the finding." That model was never fitted, so the
# phrase "survive both" had nothing behind half of it.
#
# This fits it: M2 re-estimated on the 42 indicators that remain when
# E224-E233B are dropped, plus the H2 comparison model with phi(D1,D3) fixed to
# unity, so the registered decision rule can be applied in full rather than only
# its magnitude half.
#
# It is a NEW FIT, not a cache read, and that is why it is a separate script
# rather than a stage of `06`. `06` is the gated script; re-running it to add a
# model would re-run everything behind the Tier-2 gate for no reason. The gate is
# not bypassed -- it has already been discharged, and nothing here is a forecast
# target. The frame, the reverse-keying rule, the estimator and the seed are
# copied from `06` exactly so the two are comparable.
#
# WHAT COUNTS AS SURVIVAL is fixed here before the fit, in the same terms the
# pre-registration uses for H2: M2b rejected against M2 at alpha = .01 AND
# phi(D1,D3) <= .70.
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
set.seed(20260810)

csv  <- file.path(ROOT, "data/derived", sprintf("pii-frame-%s.csv", variant))
meta <- fromJSON(file.path(ROOT, "data/derived", sprintf("pii-frame-%s.meta.json", variant)))
d    <- read.csv(csv, stringsAsFactors = FALSE)
items <- meta$items

for (v in meta$reverse_keyed) {
  if (!v %in% names(d)) next
  rng <- range(d[[v]], na.rm = TRUE)
  d[[v]] <- rng[1] + rng[2] - d[[v]]
}

BATT <- c("E224","E225","E226","E227","E228","E229","E233","E233A","E233B")
keep <- items[!items$variable %in% BATT, ]
ordvars <- unique(keep$variable)
for (v in ordvars) d[[v]] <- ordered(d[[v]])

by_dim <- function(dd) unique(keep$variable[keep$dimension == dd])
f <- function(name, vs) paste0(name, " =~ ", paste(vs, collapse = " + "))
D1 <- by_dim("D1"); D2 <- by_dim("D2"); D3 <- by_dim("D3")
cat(sprintf("battery excluded: %d indicators remain (D1 %d, D2 %d, D3 %d) over %d rows\n",
            length(ordvars), length(D1), length(D2), length(D3), nrow(d)))
if (min(length(D1), length(D2), length(D3)) < 3)
  stop("a dimension falls below three indicators without the battery; the model is not ",
       "identified and the sensitivity check cannot be run as registered", call. = FALSE)

FITM <- c("chisq.scaled","df.scaled","pvalue.scaled","cfi.scaled",
          "tli.scaled","rmsea.scaled","srmr")
CACHE <- file.path(ROOT, "supplement/analysis/.fitcache")
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)

fitmod <- function(nm, syntax) {
  key <- file.path(CACHE, sprintf("%s-nobatt-%s.rds", variant, nm))
  if (file.exists(key)) { cat(sprintf("  %-6s cached\n", nm)); return(readRDS(key)) }
  cat(sprintf("  %-6s fitting ... ", nm)); t0 <- Sys.time()
  fit <- cfa(syntax, data = d, estimator = "WLSMV", ordered = ordvars,
             missing = "pairwise", std.lv = TRUE)
  cat(sprintf("%.0f min\n", as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  saveRDS(fit, key)
  fit
}

m2  <- fitmod("M2",  paste(f("D1", D1), f("D2", D2), f("D3", D3), sep = "\n"))
m2b <- fitmod("M2b", paste(f("D1", D1), f("D2", D2), f("D3", D3),
                           "D1 ~~ 1*D3", sep = "\n"))
# H1 as well as H2. "The substantive conclusion must survive both" is not restricted to one
# hypothesis, and the H1 rule has a DeltaCFI condition that a phi alone cannot answer.
u12  <- union(D1, D2)
m012 <- fitmod("M0_12", f("G", u12))
m1   <- fitmod("M1",   paste(f("D1", D1), f("D2", D2), sep = "\n"))
m1b  <- fitmod("M1b",  paste(f("D1", D1), f("D2", D2), "D1 ~~ 1*D2", sep = "\n"))

phi <- function(fit, x, y) {
  s <- standardizedSolution(fit)
  r <- s[s$op == "~~" & ((s$lhs == x & s$rhs == y) | (s$lhs == y & s$rhs == x)), "est.std"]
  if (length(r) == 1) round(r, 4) else NA_real_
}
fm <- function(fit) as.list(round(fitMeasures(fit, FITM), 4))

# LOCAL-OPTIMUM GUARD. For properly nested models at a global optimum the restricted model
# cannot achieve a LOWER unscaled chi-square than the less restricted one: its feasible set is
# a subset. When it does, the less restricted fit has landed somewhere other than the global
# optimum and every quantity read off it -- the difference test, the delta CFI and the factor
# correlation alike -- is uninterpretable. lavaan warns about this in prose; here it decides
# whether a verdict is emitted at all, because an unguarded `supported: FALSE` in a supplement
# JSON would be read as a hypothesis failing a sensitivity check when nothing of the kind
# happened.
nested_ok <- function(restricted, free) {
  cr <- unname(fitMeasures(restricted, "chisq")); cf <- unname(fitMeasures(free, "chisq"))
  dr <- unname(fitMeasures(restricted, "df"));    df_ <- unname(fitMeasures(free, "df"))
  list(ok = (cr >= cf) && (dr > df_), chisq_restricted = round(cr, 2),
       chisq_free = round(cf, 2), gap = round(cr - cf, 2))
}

n2 <- nested_ok(m2b, m2)
lrt <- lavTestLRT(m2b, m2)
p   <- lrt[["Pr(>Chisq)"]][2]
p13 <- phi(m2, "D1", "D3")
survives <- if (!n2$ok) NA else isTRUE(p < .01) && isTRUE(abs(p13) <= .70)

n1 <- nested_ok(m1b, m1)
lrt1  <- lavTestLRT(m1b, m1)
p1b   <- lrt1[["Pr(>Chisq)"]][2]
dcfi1 <- fitMeasures(m1, "cfi.scaled") - fitMeasures(m012, "cfi.scaled")
p12   <- phi(m1, "D1", "D2")
h1ok  <- if (!n1$ok) NA else
  isTRUE(dcfi1 >= .010) && isTRUE(p1b < .01) && isTRUE(abs(p12) <= .85)
if (!n1$ok) cat(sprintf(
  "\n*** H1 NOT INTERPRETABLE HERE: M1b (restricted, df %d) reaches chisq %.1f against M1's %.1f.\n",
  unname(fitMeasures(m1b, "df")), n1$chisq_restricted, n1$chisq_free),
  "    A restricted model cannot fit better at a global optimum, so M1 is at a local one and\n",
  "    no H1 quantity from this specification is reported.\n", sep = "")
if (!n2$ok) cat("\n*** H2 NOT INTERPRETABLE HERE: same local-optimum condition on M2.\n")

cat(sprintf("\nphi(D1,D3) = %+.4f   phi(D2,D3) = %+.4f   p(M2b) = %.3g\n",
            p13, phi(m2, "D2", "D3"), p))
cat(sprintf("H2 survives the battery-excluded specification: %s\n", survives))
cat(sprintf("phi(D1,D2) in M1 = %+.4f   dCFI(M1 vs M0_12) = %+.4f   p(M1b) = %.3g\n",
            p12, dcfi1, p1b))
cat(sprintf("H1 survives the battery-excluded specification: %s\n", h1ok))

# The SIGNS are not part of either decision rule, but the manuscript reads meaning off them,
# so whether they are stable across this specification is recorded explicitly rather than
# left for a reader to notice by comparing two JSON files.
sgn <- function(a, b) if (is.na(a) || is.na(b)) NA else sign(a) == sign(b)

out <- list(
  run_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  registered = TRUE,
  registered_in = "preregistration.md Decision D3, second clause",
  variant = variant, seed = 20260810,
  R_version = R.version.string,
  frame_sha256 = meta$source_sha256,
  item_table_sha256 = meta$item_table_sha256,
  excluded_items = BATT,
  n_indicators = length(ordvars),
  n_by_dimension = list(D1 = length(D1), D2 = length(D2), D3 = length(D3)),
  fit = list(M2 = fm(m2), M2b = fm(m2b), M0_12 = fm(m012), M1 = fm(m1), M1b = fm(m1b)),
  H2 = list(interpretable = n2$ok, nested_check = n2,
            phi_D1_D3 = p13, phi_D2_D3 = phi(m2, "D2", "D3"),
            phi_D1_D2_in_M2 = phi(m2, "D1", "D2"),
            p_M2b = signif(p, 6),
            M2b_rejected_at_.01 = isTRUE(p < .01),
            abs_phi_le_.70 = isTRUE(abs(p13) <= .70),
            supported = survives),
  H1 = list(interpretable = n1$ok,
            not_interpretable_because = if (n1$ok) NULL else paste(
              "M1b is nested within M1 but reaches a LOWER unscaled chi-square",
              sprintf("(%.1f on %d df against %.1f on %d df).", n1$chisq_restricted,
                      unname(fitMeasures(m1b, "df")), n1$chisq_free,
                      unname(fitMeasures(m1, "df"))),
              "That is impossible at a global optimum, so M1 is at a local one and no H1",
              "quantity from this specification -- difference test, delta CFI or phi --",
              "is reported. This is a fitting failure, not evidence about H1."),
            nested_check = n1,
            phi_D1_D2 = if (n1$ok) p12 else NULL,
            deltaCFI = if (n1$ok) round(unname(dcfi1), 4) else NULL,
            p_M1b = if (n1$ok) signif(p1b, 6) else NULL,
            supported = h1ok),
  # Admissibility is checked here because a sign read off an inadmissible model would be
  # worthless, and the whole point of this run is a comparison of signs.
  admissibility = list(
    M2_min_eigenvalue_cov_lv = round(min(eigen(lavInspect(m2, "cov.lv"),
                                               only.values = TRUE)$values), 5),
    M2_min_residual_variance = round(min(diag(lavInspect(m2, "theta"))), 4),
    M2_admissible = min(eigen(lavInspect(m2, "cov.lv"), only.values = TRUE)$values) > 0 &&
                    min(diag(lavInspect(m2, "theta"))) > 0,
    note = "M2b constrains phi(D1,D3) to +1 and is inadmissible by construction, exactly as in the battery-inclusive model. That does not bear on M2."),
  sign_stability = list(
    note = "Signs are not part of any registered decision rule, but the manuscript interprets them, so their stability across this specification is recorded.",
    phi_D1_D3_battery_inclusive = -0.4544, phi_D1_D3_battery_excluded = p13,
    phi_D1_D3_sign_stable = sgn(-0.4544, p13),
    phi_D1_D2_battery_inclusive = 0.2984,
    phi_D1_D2_battery_excluded = if (n1$ok) p12 else NULL,
    phi_D1_D2_sign_stable = if (n1$ok) sgn(0.2984, p12) else NULL,
    phi_D1_D2_note = if (n1$ok) NULL else
      "Not compared: the battery-excluded M1 is at a local optimum, so its phi is not a result.",
    phi_D2_D3_battery_inclusive = -0.4181, phi_D2_D3_battery_excluded = phi(m2, "D2", "D3"),
    phi_D2_D3_sign_stable = sgn(-0.4181, phi(m2, "D2", "D3"))),
  criterion = "as registered for H2: M2b rejected against M2 at alpha = .01 AND |phi(D1,D3)| <= .70; and for H1 the three-part conjunctive rule of 6.2",
  note = paste("Second clause of Decision D3. Fixed before the fit: survival means the H2",
               "decision rule holds on this specification too. A failure here would have been",
               "reported as the finding, not resolved in favour of the battery-inclusive model."))

dest <- file.path(ROOT, "supplement/analysis",
                  sprintf("battery-excluded-%s.json", variant))
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 8), dest)
cat("wrote", sub(paste0(ROOT, "/"), "", dest), "\n")
