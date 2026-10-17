#!/usr/bin/env bash
# =============================================================================
# kl_tension_run.sh — K-ladder lane step 7 again, after step 5
# =============================================================================
# Part of the S164 restatement pass (reports/s164-agent-records/
# restatement-pass.md § 1.4, step 7). The plan runs the tension analyses after
# the Phase 2 tables (step 5), which they read; the part-2 run had made them
# before step 5. This re-runs scripts/k_ladder_tension_analyses.py
# --grid-overlap --effect-sizes in a disposable real-file copy of REF (the
# whole tracked tree), writing tension/{grid-overlap.json, effect-sizes.json}
# in the copy. Single-threaded; no API call.
#
# Usage: kl_tension_run.sh <ref> <dest> <log_dir> <tag>
# =============================================================================
set -uo pipefail
REF=$1; DEST=$2; LOGDIR=$3; TAG=$4
REPO=$HOME/scratch/s164-restate-2026-10-15/wt
SHARED=$HOME/Code/map-reader-llm
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
export PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg
mkdir -p "$LOGDIR"; echo $$ > "$LOGDIR/$TAG.pid"; echo RUNNING > "$LOGDIR/$TAG.state"
[ -e "$DEST" ] && { echo "FAILED dest exists" > "$LOGDIR/$TAG.state"; exit 2; }
mkdir -p "$DEST"
git -C "$REPO" archive "$REF" | tar -x -C "$DEST"
ln -s "$SHARED/.venv" "$DEST/.venv"
printf 'ref %s\n' "$(git -C "$REPO" rev-parse "$REF")" > "$DEST/.source-commit"
cd "$DEST" || exit 9
.venv/bin/python scripts/k_ladder_tension_analyses.py --grid-overlap --effect-sizes \
  > "$LOGDIR/$TAG.log" 2>&1
rc=$?
echo "$(date -u +%FT%TZ) rc=$rc" >> "$LOGDIR/$TAG.times"
if [ $rc -eq 0 ]; then echo DONE > "$LOGDIR/$TAG.state"; else echo "FAILED $rc" > "$LOGDIR/$TAG.state"; fi
