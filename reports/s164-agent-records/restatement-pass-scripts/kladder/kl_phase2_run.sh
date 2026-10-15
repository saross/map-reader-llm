#!/usr/bin/env bash
# =============================================================================
# kl_phase2_run.sh — K-ladder lane step 5: the Phase 2 tables on the D51 clip
# =============================================================================
# Part of the S164 restatement pass (reports/s164-agent-records/
# restatement-pass.md § 1.4, step 5, run after the Era-2 board lane). Builds a
# disposable real-file copy of REF (code, results/, inputs/vectors and the
# Gemini 3.7 screen's outputs, which the builder reads for the 3.7 ladder's
# unions), then runs scripts/build_k_ladder_phase2_tables.py with
# --clip-to-common-area --allow-undetermined-area (D57 (2), (3); D67 (5)),
# writing phase2/{ladders.json, ladder-tables.md, ladders-compat.json} and
# figures/k-ladder-pareto-phase2.png in the copy. Single-threaded; no API call.
#
# Usage: kl_phase2_run.sh <ref> <dest> <log_dir> <tag>
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
git -C "$REPO" archive "$REF" -- scripts config.py pyproject.toml pytest.ini inputs/vectors \
  results outputs/gemini37-screen-2026-08-28 | tar -x -C "$DEST"
# The whole venv is linked: a linked interpreter alone loses its site-packages.
ln -s "$SHARED/.venv" "$DEST/.venv"
printf 'ref %s\n' "$(git -C "$REPO" rev-parse "$REF")" > "$DEST/.source-commit"
cd "$DEST" || exit 9
.venv/bin/python scripts/build_k_ladder_phase2_tables.py --clip-to-common-area \
  --allow-undetermined-area > "$LOGDIR/$TAG.log" 2>&1
rc=$?
echo "$(date -u +%FT%TZ) rc=$rc" >> "$LOGDIR/$TAG.times"
if [ $rc -eq 0 ]; then echo DONE > "$LOGDIR/$TAG.state"; else echo "FAILED $rc" > "$LOGDIR/$TAG.state"; fi
