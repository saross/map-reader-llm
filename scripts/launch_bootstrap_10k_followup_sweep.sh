#!/usr/bin/env bash
# Launch the 161-cell bootstrap-10K follow-up sweep on sapphire.
# Skips the 4 dry-run indices that have already been completed and verified.
#
# Usage (run on sapphire):
#   bash scripts/launch_bootstrap_10k_followup_sweep.sh
#
# Output: progress log at /tmp/bootstrap-10k-followup-progress.log
#         failures (if any) at /tmp/bootstrap-10k-followup-failures.log
#
# Author: Claude Code (Opus 4.7) for Shawn Ross's daylight follow-up sweep, 2026-04-29.
set -euo pipefail

REPO_ROOT="${HOME}/Code/map-reader-llm"
QUEUE_CSV="/tmp/bootstrap-10k-jobs.csv"
PROGRESS_LOG="/tmp/bootstrap-10k-followup-progress.log"
FAILURES_LOG="/tmp/bootstrap-10k-followup-failures.log"
PARALLEL_WORKERS=16

# 3 cells already completed and verified during dry-run (skip).
# Index 163 (55maps text-min) was killed mid-dry-run after 24 min single-thread —
# will be re-run as part of this sweep where it'll get its own core in -P 16.
COMPLETED_INDICES=(135 156 164)

cd "${REPO_ROOT}"
source .venv/bin/activate

# Build the list of indices to run (0..164 minus completed).
indices_to_run=()
for i in $(seq 0 164); do
    skip=0
    for c in "${COMPLETED_INDICES[@]}"; do
        if [[ "${i}" == "${c}" ]]; then skip=1; break; fi
    done
    if [[ "${skip}" == "0" ]]; then
        indices_to_run+=("${i}")
    fi
done

echo "Total cells to run: ${#indices_to_run[@]} (165 total - ${#COMPLETED_INDICES[@]} already done = 161)"
echo "Concurrency: -P ${PARALLEL_WORKERS}"
echo "Queue: ${QUEUE_CSV}"
echo "Progress log: ${PROGRESS_LOG}"
echo "Failures log: ${FAILURES_LOG}"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "---"

: > "${PROGRESS_LOG}"
: > "${FAILURES_LOG}"

# Use xargs -P for parallel execution. The runner returns non-zero on error;
# capture failed indices into the failures log without aborting the whole sweep.
printf '%s\n' "${indices_to_run[@]}" \
  | xargs -n 1 -P "${PARALLEL_WORKERS}" -I{} bash -c '
        i="$1"
        if python3 scripts/run_bootstrap_10k.py --index "${i}" >> "'"${PROGRESS_LOG}"'" 2>&1; then
            echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] OK   ${i}" >> "'"${PROGRESS_LOG}"'"
        else
            echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] FAIL ${i}" | tee -a "'"${FAILURES_LOG}"'" >> "'"${PROGRESS_LOG}"'"
        fi
    ' _ {}

echo "---"
echo "Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "OK   count: $(grep -c '^\[.*\] OK ' "${PROGRESS_LOG}" || echo 0)"
echo "FAIL count: $(grep -c '^\[.*\] FAIL ' "${PROGRESS_LOG}" || echo 0)"
if [[ -s "${FAILURES_LOG}" ]]; then
    echo "Failed indices:"
    cat "${FAILURES_LOG}"
fi
