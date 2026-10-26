#!/usr/bin/env Rscript
# =============================================================================
# 26_justifiability_method_factor.R -- UNREGISTERED EXPLORATORY.
#
#   Rscript code/26_justifiability_method_factor.R --spec mf|excl
#
# WHY. Decision D3 gives the nine-item democracy battery its own orthogonal
# method factor, on the stated ground that items sharing one response format can
# produce "method structure rather than construct structure", and additionally
# reports a battery-excluded sensitivity. That reasoning was never applied to the
# WVS/EVS justifiability battery -- which carries 59.8% of D1's and 45.8% of D2's
# summed |lambda| and all five of D1's strongest loadings, against 1.2% of D3's.
# The battery is known to split internally into a permissive-morality factor and a
# civic-honesty factor, and those are, item for item, D1's and D2's top markers.
# H1 may therefore be recovering the battery's internal structure rather than the
# two Popperian axes. This script applies D3's own logic to that battery.
#
# THIS IS NOT REGISTERED. It was conceived on 2026-09-08 after the registered
# sensitivities had been run and the M2 loadings inspected, so it is exploratory
# by construction and is labelled so in the output. It adds no item and drops no
# item for fit: `excl` removes a whole pre-identified battery, `mf` removes
# nothing. The decision rules are the pre-registration's own, unchanged, so the
# result is comparable with the registered run rather than scored on a new scale.
# A negative result here is reportable and must be reported.
#
# WHICH SPEC IS LOAD-BEARING. `excl` is, and `mf` is not, for a reason that has to be stated
# rather than discovered by a reviewer. The battery's known internal structure is TWO factors --
# permissive morality and civic honesty -- and those coincide with D1's and D2's strongest markers.
# A SINGLE orthogonal method factor cannot, in principle, explain away a two-factor split, so
# `mf` surviving is weak evidence: it tests only whether a common response-format factor exists,
# not whether the split is format. And the apparently obvious fix -- two method factors aligned
# with the permissive/civic halves -- is no test at all, because it is observationally equivalent
# to the substantive model it is supposed to challenge. The confound is not identifiable from
# within the battery. `excl` is therefore the decisive specification: if D1 and D2 stay separable
# on the 12 and 10 NON-battery indicators, the two axes are not an artefact of the battery; if
# they collapse, H1 was the battery. Read `excl` first and report `mf` as the weaker check.
#
# BATTERY MEMBERSHIP is taken from the frozen item table by question stem -- every
# item whose label begins "Justifiable:" -- not from its loadings. Defining the
# battery by the loadings it produces would make the test circular.
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
spec  <- getarg("--spec", NULL)
frame <- getarg("--frame", "primary")   # SMOKE only for pre-flight; results come from primary
if (is.null(spec) || !spec %in% c("mf", "excl"))
  stop("--spec must be mf (method factor) or excl (battery excluded)", call. = FALSE)
set.seed(20260810)

csv   <- file.path(ROOT, "data/derived", sprintf("pii-frame-%s.csv", frame))
meta  <- fromJSON(file.path(ROOT, "data/derived", sprintf("pii-frame-%s.meta.json", frame)))
d     <- read.csv(csv, stringsAsFactors = FALSE)
items <- meta$items

for (v in meta$reverse_keyed) {
  if (!v %in% names(d)) next
  rng <- range(d[[v]], na.rm = TRUE)
  d[[v]] <- rng[1] + rng[2] - d[[v]]
}

# ---------------------------------------------------------------- battery ----
JUST <- unique(items$variable[grepl("^justifiab", tolower(items$label))])
if (length(JUST) != 11)
  stop("expected 11 justifiability variables, found ", length(JUST), call. = FALSE)

keep <- items
if (spec == "excl") keep <- keep[!(keep$variable %in% JUST), ]

ordvars <- unique(keep$variable)
for (v in ordvars) d[[v]] <- ordered(d[[v]])

by_dim <- function(dd) unique(keep$variable[keep$dimension == dd])
f  <- function(name, vs) paste0(name, " =~ ", paste(vs, collapse = " + "))
D1 <- by_dim("D1"); D2 <- by_dim("D2"); D3 <- by_dim("D3")
u12 <- union(D1, D2)

cat(sprintf("spec=%s | battery = %d vars (%s)\n", spec, length(JUST),
            paste(sort(JUST), collapse = " ")))
cat(sprintf("%d indicators (D1 %d, D2 %d, D3 %d), %d rows, %d countries\n",
            length(ordvars), length(D1), length(D2), length(D3),
            nrow(d), length(unique(d$country))))
if (min(length(D1), length(D2), length(D3)) < 3)
  stop("a dimension falls below three indicators; the model is not identified", call. = FALSE)

# The method factor spans only the battery items PRESENT in the model at hand: all 11 in the
# three-factor models, and the 10 that sit in D1 or D2 in the H1 models, which contain no D3.
mfblock <- function(vs) {
  b <- intersect(JUST, vs)
  if (spec != "mf" || length(b) < 3) return(NULL)
  paste(f("JF", b), "JF ~~ 0*D1", "JF ~~ 0*D2", "JF ~~ 0*D3", sep = "\n")
}
mfblock1 <- function(vs, facs) {          # H1 models have no D3
  b <- intersect(JUST, vs)
  if (spec != "mf" || length(b) < 3) return(NULL)
  paste(c(f("JF", b), sprintf("JF ~~ 0*%s", facs)), collapse = "\n")
}
glue <- function(...) paste(Filter(Negate(is.null), list(...)), collapse = "\n")

FITM  <- c("chisq.scaled","df.scaled","pvalue.scaled","cfi.scaled",
           "tli.scaled","rmsea.scaled","srmr")
CACHE <- file.path(ROOT, "supplement/analysis/.fitcache")
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)

fitmod <- function(nm, syntax) {
  key <- file.path(CACHE, sprintf("just-%s-%s-%s.rds", frame, spec, nm))
  if (file.exists(key)) { cat(sprintf("  %-6s cached\n", nm)); return(readRDS(key)) }
  cat(sprintf("  %-6s fitting ... ", nm)); t0 <- Sys.time()
  fit <- cfa(syntax, data = d, estimator = "WLSMV", ordered = ordvars,
             missing = "pairwise", std.lv = TRUE)
  cat(sprintf("%.1f min\n", as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  saveRDS(fit, key)
  fit
}

three <- paste(f("D1", D1), f("D2", D2), f("D3", D3), sep = "\n")
m2   <- fitmod("M2",  glue(three, mfblock(ordvars)))
m2b  <- fitmod("M2b", glue(three, "D1 ~~ 1*D3", mfblock(ordvars)))
m012 <- fitmod("M0_12", glue(f("G", u12), mfblock1(u12, "G")))
m1   <- fitmod("M1",  glue(f("D1", D1), f("D2", D2), mfblock1(u12, c("D1","D2"))))
m1b  <- fitmod("M1b", glue(f("D1", D1), f("D2", D2), "D1 ~~ 1*D2",
                           mfblock1(u12, c("D1","D2"))))

phi <- function(fit, x, y) {
  s <- standardizedSolution(fit)
  r <- s[s$op == "~~" & ((s$lhs == x & s$rhs == y) | (s$lhs == y & s$rhs == x)), "est.std"]
  if (length(r) == 1) round(r, 4) else NA_real_
}
fm <- function(fit) as.list(round(fitMeasures(fit, FITM), 4))

# ADMISSIBILITY, computed here rather than left to `07`, because the whole point of `mf` is that the
# method factor may become a rotational alias of the D1/D2 contrast -- and when it does, the symptom
# is an out-of-bounds latent correlation, not a bad fit index. A model whose latent covariance matrix
# is not positive definite yields no interpretable phi, however good its CFI looks.
adm <- function(fit) {
  cv <- lavInspect(fit, "cov.lv")
  r  <- cov2cor(cv); diag(r) <- 0
  list(min_eigenvalue_covlv = round(min(eigen(cv, only.values = TRUE)$values), 6),
       max_abs_latent_cor   = round(max(abs(r)), 4),
       min_residual_var     = round(min(diag(lavInspect(fit, "theta"))), 6),
       admissible = isTRUE(min(eigen(cv, only.values = TRUE)$values) > 0) &&
                    isTRUE(max(abs(r)) <= 1))
}

# LOCAL-OPTIMUM GUARD, identical to `18` and `25`.
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

# Method-factor loadings are the substantive payload of spec=mf: how much of each battery item is
# format rather than construct, and what is left of the substantive loading once JF is in the model.
jf <- NULL
if (spec == "mf") {
  s <- standardizedSolution(m2)
  s <- s[s$op == "=~" & s$rhs %in% JUST, c("lhs","rhs","est.std")]
  jf <- lapply(split(s, seq_len(nrow(s))), function(r)
          list(factor = r$lhs, variable = r$rhs, est.std = round(r$est.std, 4)))
  names(jf) <- NULL
}

entry <- list(
  spec = spec,
  registered = FALSE,
  exploratory_note = paste(
    "UNREGISTERED EXPLORATORY. Conceived 2026-09-08, after the registered sensitivities were",
    "run and the M2 loadings inspected. Decision rules are the pre-registration's own and were",
    "not altered. Report as exploratory; a negative result is reportable."),
  run_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  seed = 20260810, R_version = R.version.string,
  frame = frame, f117 = "both",
  frame_sha256 = meta$source_sha256, item_table_sha256 = meta$item_table_sha256,
  battery = sort(JUST), battery_rule = "item label begins 'Justifiable:' in the frozen item table",
  n_rows = nrow(d), n_countries = length(unique(d$country)),
  n_indicators = length(ordvars),
  n_by_dimension = list(D1 = length(D1), D2 = length(D2), D3 = length(D3)),
  fit = list(M2 = fm(m2), M2b = fm(m2b), M0_12 = fm(m012), M1 = fm(m1), M1b = fm(m1b)),
  admissibility = list(M2 = adm(m2), M2b = adm(m2b), M0_12 = adm(m012),
                       M1 = adm(m1), M1b = adm(m1b)),
  H1 = list(interpretable = n1$ok, nested_check = n1, delta_cfi = round(dcfi1, 4),
            p_M1b = signif(p1b, 6), phi_D1_D2 = p12,
            dcfi_ge_.010 = isTRUE(dcfi1 >= .010), M1b_rejected_at_.01 = isTRUE(p1b < .01),
            abs_phi_le_.85 = isTRUE(abs(p12) <= .85), supported = h1ok),
  H2 = list(interpretable = n2$ok, nested_check = n2,
            phi_D1_D3 = p13, phi_D2_D3 = phi(m2, "D2", "D3"),
            phi_D1_D2_in_M2 = phi(m2, "D1", "D2"), p_M2b = signif(p, 6),
            M2b_rejected_at_.01 = isTRUE(p < .01), abs_phi_le_.70 = isTRUE(abs(p13) <= .70),
            supported = h2ok),
  method_factor_loadings = jf)

dest <- file.path(ROOT, "supplement/analysis",
                  sprintf("justifiability-battery%s.json",
                          if (frame == "primary") "" else paste0("-", frame)))
all <- if (file.exists(dest)) fromJSON(dest, simplifyVector = FALSE) else
  list(registered = FALSE,
       purpose = paste("Applies Decision D3's method-factor reasoning to the WVS/EVS",
                       "justifiability battery, which dominates D1 and D2. Exploratory."),
       specs = list())
all$specs[[spec]] <- entry
all$run_utc <- format(Sys.time(), tz = "UTC", usetz = TRUE)
write(toJSON(all, auto_unbox = TRUE, digits = 8, pretty = TRUE), dest)
cat(sprintf("\nwrote %s [%s]\n", sub(paste0(ROOT, "/"), "", dest), spec))
