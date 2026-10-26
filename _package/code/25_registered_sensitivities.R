#!/usr/bin/env Rscript
# =============================================================================
# 25_registered_sensitivities.R -- the registered sensitivity analyses that
# §4.1 and Decisions D1, D2 and the F117 ruling promise and that were never run.
#
#   Rscript code/25_registered_sensitivities.R --label cyprus   --frame sens-cy
#   Rscript code/25_registered_sensitivities.R --label zero_na  --frame sens-0na
#   Rscript code/25_registered_sensitivities.R --label nocauc   --frame sens-nocauc
#   Rscript code/25_registered_sensitivities.R --label f117_d2  --f117 d2only
#   Rscript code/25_registered_sensitivities.R --label f117_d3  --f117 d3only
#
# WHY. Four registered commitments were promised in the manuscript's reporting
# present tense and never discharged:
#
#   §4.1  "Armenia, Azerbaijan and Georgia are retained on a generous definition
#          of Europe; a sensitivity analysis excluding all three is reported."
#   D1    "Report a sensitivity analysis including [Cyprus]."
#   D2    "Report a sensitivity analysis treating `0` as missing. If the two
#          disagree on any hypothesis test, both are reported in the manuscript
#          body, not the supplement."
#   F117  "Two sensitivity models assign it to D2 only and to D3 only, and all
#          three are reported. If they disagree on H1 or H2, the disagreement
#          goes in the manuscript body, not the supplement."
#
# Note what the last two oblige: a DISAGREEMENT is a body-text obligation, not a
# supplement footnote. This script therefore emits the comparison explicitly
# rather than leaving a reader to diff two JSON files.
#
# WHAT COUNTS AS SURVIVAL is fixed before the fit, in the pre-registration's own
# terms, and is identical to `18_battery_excluded_sensitivity.R`:
#   H1  dCFI(M1 vs M0_12) >= .010 AND M1b rejected at .01 AND |phi(D1,D2)| <= .85
#   H2  M2b rejected at .01 AND |phi(D1,D3)| <= .70
#
# The estimator, seed, reverse-keying rule and local-optimum guard are copied
# from `06` and `18` exactly so every variant is comparable to the primary.
# This is a NEW FIT, not a cache read. The Tier-2 gate is already discharged and
# nothing here is a forecast target.
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
frame <- getarg("--frame", "primary")
f117  <- getarg("--f117",  "both")
label <- getarg("--label", NULL)
if (is.null(label)) stop("--label is required: it keys the output JSON", call. = FALSE)
if (!f117 %in% c("both", "d2only", "d3only"))
  stop("--f117 must be both, d2only or d3only", call. = FALSE)
set.seed(20260810)

csv  <- file.path(ROOT, "data/derived", sprintf("pii-frame-%s.csv", frame))
mpath <- file.path(ROOT, "data/derived", sprintf("pii-frame-%s.meta.json", frame))
if (!file.exists(csv)) stop("no such frame: ", csv, call. = FALSE)
meta <- fromJSON(mpath)
d    <- read.csv(csv, stringsAsFactors = FALSE)
items <- meta$items

for (v in meta$reverse_keyed) {
  if (!v %in% names(d)) next
  rng <- range(d[[v]], na.rm = TRUE)
  d[[v]] <- rng[1] + rng[2] - d[[v]]
}

# F117 loads on BOTH D2 and D3 in the registered table, which is why it has two rows. The
# sensitivity variants drop one of them. No item is added and none is dropped for fit.
keep <- items
if (f117 == "d2only") keep <- keep[!(keep$variable == "F117" & keep$dimension == "D3"), ]
if (f117 == "d3only") keep <- keep[!(keep$variable == "F117" & keep$dimension == "D2"), ]

ordvars <- unique(keep$variable)
for (v in ordvars) d[[v]] <- ordered(d[[v]])

by_dim <- function(dd) unique(keep$variable[keep$dimension == dd])
f  <- function(name, vs) paste0(name, " =~ ", paste(vs, collapse = " + "))
D1 <- by_dim("D1"); D2 <- by_dim("D2"); D3 <- by_dim("D3")
cat(sprintf("%s: frame=%s f117=%s | %d indicators (D1 %d, D2 %d, D3 %d), %d rows, %d countries\n",
            label, frame, f117, length(ordvars), length(D1), length(D2), length(D3),
            nrow(d), length(unique(d$country))))
if (min(length(D1), length(D2), length(D3)) < 3)
  stop("a dimension falls below three indicators; the model is not identified", call. = FALSE)

FITM  <- c("chisq.scaled","df.scaled","pvalue.scaled","cfi.scaled",
           "tli.scaled","rmsea.scaled","srmr")
CACHE <- file.path(ROOT, "supplement/analysis/.fitcache")
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)

fitmod <- function(nm, syntax) {
  key <- file.path(CACHE, sprintf("sens-%s-%s.rds", label, nm))
  if (file.exists(key)) { cat(sprintf("  %-6s cached\n", nm)); return(readRDS(key)) }
  cat(sprintf("  %-6s fitting ... ", nm)); t0 <- Sys.time()
  fit <- cfa(syntax, data = d, estimator = "WLSMV", ordered = ordvars,
             missing = "pairwise", std.lv = TRUE)
  cat(sprintf("%.1f min\n", as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  saveRDS(fit, key)
  fit
}

m2   <- fitmod("M2",  paste(f("D1", D1), f("D2", D2), f("D3", D3), sep = "\n"))
m2b  <- fitmod("M2b", paste(f("D1", D1), f("D2", D2), f("D3", D3), "D1 ~~ 1*D3", sep = "\n"))
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

# LOCAL-OPTIMUM GUARD, identical to `18`. A restricted model cannot reach a lower unscaled
# chi-square than the model it is nested in unless the freer fit is at a local optimum, in
# which case every quantity read off it is uninterpretable and no verdict may be emitted.
nested_ok <- function(restricted, free) {
  cr <- unname(fitMeasures(restricted, "chisq")); cf <- unname(fitMeasures(free, "chisq"))
  dr <- unname(fitMeasures(restricted, "df"));    df_ <- unname(fitMeasures(free, "df"))
  list(ok = (cr >= cf) && (dr > df_), chisq_restricted = round(cr, 2),
       chisq_free = round(cf, 2), gap = round(cr - cf, 2))
}

n2  <- nested_ok(m2b, m2)
p   <- lavTestLRT(m2b, m2)[["Pr(>Chisq)"]][2]
p13 <- phi(m2, "D1", "D3")
h2ok <- if (!n2$ok) NA else isTRUE(p < .01) && isTRUE(abs(p13) <= .70)

n1    <- nested_ok(m1b, m1)
p1b   <- lavTestLRT(m1b, m1)[["Pr(>Chisq)"]][2]
dcfi1 <- unname(fitMeasures(m1, "cfi.scaled") - fitMeasures(m012, "cfi.scaled"))
p12   <- phi(m1, "D1", "D2")
h1ok  <- if (!n1$ok) NA else
  isTRUE(dcfi1 >= .010) && isTRUE(p1b < .01) && isTRUE(abs(p12) <= .85)

if (!n1$ok) cat("\n*** H1 NOT INTERPRETABLE on this specification (local optimum on M1).\n")
if (!n2$ok) cat("*** H2 NOT INTERPRETABLE on this specification (local optimum on M2).\n")
cat(sprintf("\nH1: dCFI %+.4f  p(M1b) %.3g  phi(D1,D2) %+.4f  -> supported = %s\n",
            dcfi1, p1b, p12, h1ok))
cat(sprintf("H2: p(M2b) %.3g  phi(D1,D3) %+.4f  phi(D2,D3) %+.4f -> supported = %s\n",
            p, p13, phi(m2, "D2", "D3"), h2ok))

entry <- list(
  label = label, frame = frame, f117 = f117,
  run_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  registered = TRUE, seed = 20260810, R_version = R.version.string,
  frame_sha256 = meta$source_sha256, item_table_sha256 = meta$item_table_sha256,
  n_rows = nrow(d), n_countries = length(unique(d$country)),
  n_indicators = length(ordvars),
  n_by_dimension = list(D1 = length(D1), D2 = length(D2), D3 = length(D3)),
  fit = list(M2 = fm(m2), M2b = fm(m2b), M0_12 = fm(m012), M1 = fm(m1), M1b = fm(m1b)),
  H1 = list(interpretable = n1$ok, nested_check = n1, delta_cfi = round(dcfi1, 4),
            p_M1b = signif(p1b, 6), phi_D1_D2 = p12,
            dcfi_ge_.010 = isTRUE(dcfi1 >= .010), M1b_rejected_at_.01 = isTRUE(p1b < .01),
            abs_phi_le_.85 = isTRUE(abs(p12) <= .85), supported = h1ok),
  H2 = list(interpretable = n2$ok, nested_check = n2,
            phi_D1_D3 = p13, phi_D2_D3 = phi(m2, "D2", "D3"),
            phi_D1_D2_in_M2 = phi(m2, "D1", "D2"), p_M2b = signif(p, 6),
            M2b_rejected_at_.01 = isTRUE(p < .01), abs_phi_le_.70 = isTRUE(abs(p13) <= .70),
            supported = h2ok))

dest <- file.path(ROOT, "supplement/analysis/registered-sensitivities.json")
all <- if (file.exists(dest)) fromJSON(dest, simplifyVector = FALSE) else
  list(registered = TRUE,
       registered_in = "preregistration.md §4.1, Decisions D1 and D2, and the F117 ruling",
       purpose = paste("Registered sensitivity analyses promised in the manuscript and not",
                       "run before 2026-09-08. Decision rules are the pre-registration's own",
                       "and were fixed before these fits."),
       variants = list())
all$variants[[label]] <- entry
all$run_utc <- format(Sys.time(), tz = "UTC", usetz = TRUE)
write(toJSON(all, auto_unbox = TRUE, digits = 8, pretty = TRUE), dest)
cat(sprintf("\nwrote %s [%s]\n", sub(paste0(ROOT, "/"), "", dest), label))
