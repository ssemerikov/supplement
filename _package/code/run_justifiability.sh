#!/usr/bin/env bash
# Fits the two justifiability-battery specifications, one R process each, sequentially.
# UNREGISTERED EXPLORATORY -- see the header of 26_justifiability_method_factor.R.
# One process per spec so memory is released between them; each fit is cached, so a killed
# run resumes where it stopped.
set -u
cd "$(dirname "$0")/.."
LOG=supplement/analysis/justifiability-run.log
: > "$LOG"
for spec in mf excl; do
  echo "=== $spec | started $(date -u '+%Y-%m-%d %H:%M:%S UTC') ===" | tee -a "$LOG"
  Rscript code/26_justifiability_method_factor.R --spec "$spec" >>"$LOG" 2>&1
  echo "--- $spec exit=$? finished $(date -u '+%Y-%m-%d %H:%M:%S UTC') ---" | tee -a "$LOG"
done
echo "BOTH SPECS DONE $(date -u '+%Y-%m-%d %H:%M:%S UTC')" | tee -a "$LOG"
