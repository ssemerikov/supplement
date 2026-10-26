#!/bin/bash
# Runs the five registered sensitivity variants ONE PER PROCESS, sequentially.
# One per process because exiting returns memory to the OS in a way gc() does not, and
# sequentially because this machine has kernel-OOM'd on a second concurrent fit before.
set -u
cd "$(dirname "$0")/.."
LOG="supplement/analysis/sensitivities-run.log"
: > "$LOG"
run () {   # label frame f117
  echo "=== $1 | frame=$2 f117=$3 | started $(date -u '+%F %T UTC') ===" | tee -a "$LOG"
  /usr/bin/Rscript code/25_registered_sensitivities.R --label "$1" --frame "$2" --f117 "$3" \
    >> "$LOG" 2>&1
  echo "--- $1 exit=$? finished $(date -u '+%F %T UTC') ---" | tee -a "$LOG"
}
run cyprus  sens-cy      both
run zero_na sens-0na     both
run nocauc  sens-nocauc  both
run f117_d2 primary      d2only
run f117_d3 primary      d3only
echo "ALL FIVE DONE $(date -u '+%F %T UTC')" | tee -a "$LOG"
