#!/usr/bin/env bash
# =============================================================================
# run-floors-vsd.sh — the patched floors, then the verifier SD, in one copy
# =============================================================================
# Usage: run-floors-vsd.sh <copy> <out_dir> <workers> <log_dir> <tag>
# Writes <log_dir>/<tag>.{pid,state}, <tag>-floors.log, <tag>-vsd.log.
# =============================================================================
set -uo pipefail
COPY=$1; OUT=$2; WORKERS=$3; LOGDIR=$4; TAG=$5
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
unset MAP_READER_VERIFY_DIRS
mkdir -p "$LOGDIR" "$OUT"; echo $$ > "$LOGDIR/$TAG.pid"; echo RUNNING > "$LOGDIR/$TAG.state"
cd "$COPY" || exit 9
date -u +%FT%TZ > "$LOGDIR/$TAG.start"
.venv/bin/python scripts/modality_bridge_floors.py --scoring-root outputs/modality-bridge-2026-10-07 \
  --workers "$WORKERS" --out-dir "$OUT/floors" > "$LOGDIR/$TAG-floors.log" 2>&1
rc=$?
if [ $rc -ne 0 ]; then echo "FAILED floors $rc" > "$LOGDIR/$TAG.state"; exit $rc; fi
.venv/bin/python scripts/modality_bridge_verifier_sd.py --floors-dir "$OUT/floors" \
  --scoring-root outputs/modality-bridge-2026-10-07 --out-dir "$OUT/verifier-sd" \
  > "$LOGDIR/$TAG-vsd.log" 2>&1
rc=$?
date -u +%FT%TZ > "$LOGDIR/$TAG.end"
if [ $rc -ne 0 ]; then echo "FAILED vsd $rc" > "$LOGDIR/$TAG.state"; exit $rc; fi
echo DONE > "$LOGDIR/$TAG.state"
