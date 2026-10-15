#!/usr/bin/env bash
# =============================================================================
# run-pass.sh — the bridge's three generators, in order, in one patched copy
# =============================================================================
# 1. scripts/modality-bridge-2026-10-07-score.sh (ten cells, three gap tests);
# 2. scripts/modality_bridge_floors.py --workers 1 into the copy's floors/;
# 3. scripts/modality_bridge_verifier_sd.py --floors-dir that floors/.
# Outputs land where the committed ones live (results/modality-bridge-2026-10-07/
# in the COPY), with the floors' and verifier SD's logs at logs/floors.log and
# logs/verifier-sd.log as committed. Default leg rule; one busy process.
#
# Usage: run-pass.sh <copy> <log_dir> <tag>
# =============================================================================
set -uo pipefail
COPY=$1; LOGDIR=$2; TAG=$3
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
unset MAP_READER_VERIFY_DIRS
mkdir -p "$LOGDIR"; echo $$ > "$LOGDIR/$TAG.pid"; echo RUNNING > "$LOGDIR/$TAG.state"
cd "$COPY" || exit 9
R=results/modality-bridge-2026-10-07
stamp() { echo "$(date -u +%FT%TZ) $*" >> "$LOGDIR/$TAG.times"; }
stamp start
bash scripts/modality-bridge-2026-10-07-score.sh > "$LOGDIR/$TAG-score.out" 2>&1
stamp score-done
n_ok=$(grep -c "exit 0" "$LOGDIR/$TAG-score.out")
if [ "$n_ok" -ne 13 ] || ! grep -q SCORING-DONE "$LOGDIR/$TAG-score.out"; then
  echo "FAILED score ($n_ok of 13 exit 0)" > "$LOGDIR/$TAG.state"; exit 2; fi
.venv/bin/python scripts/modality_bridge_floors.py --scoring-root outputs/modality-bridge-2026-10-07 \
  --workers 1 --out-dir $R/floors > $R/logs/floors.log 2>&1
rc=$?; stamp "floors rc=$rc"
if [ $rc -ne 0 ]; then echo "FAILED floors $rc" > "$LOGDIR/$TAG.state"; exit $rc; fi
.venv/bin/python scripts/modality_bridge_verifier_sd.py --floors-dir $R/floors \
  --scoring-root outputs/modality-bridge-2026-10-07 --out-dir $R/verifier-sd \
  > $R/logs/verifier-sd.log 2>&1
rc=$?; stamp "vsd rc=$rc"
if [ $rc -ne 0 ]; then echo "FAILED vsd $rc" > "$LOGDIR/$TAG.state"; exit $rc; fi
echo DONE > "$LOGDIR/$TAG.state"
