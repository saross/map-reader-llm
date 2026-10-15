#!/usr/bin/env bash
# =============================================================================
# chain.sh — the S164 re-score of the GS boards in one disposable copy
# =============================================================================
# Runs every generator the 14 signed analyses and the listed claim rows read,
# in dependency order, single-threaded, one process at a time, inside COPY:
# the #42 chain (grid, stride, Image-B, plateau), then the Gemini 3.7 / 3.8
# screen cells, the fourth cell, the 3.7 image arms and their pair tests,
# then the registered conditions' re-materialisation and evaluation
# (conditions.py). POLICY is exported as MAP_READER_VERIFY_DIRS, so one copy
# is one reading: `fixed` (ORIGIN) or `repaired` (REPAIRED).
#
# Usage: chain.sh <copy_dir> <fixed|repaired> <log_dir>
# Writes <log_dir>/chain.pid and <log_dir>/chain.state (RUNNING, DONE, or
# FAILED <step>); every step's output goes to <log_dir>/<step>.log.
# =============================================================================
set -uo pipefail
COPY=$1; POLICY=$2; LOGDIR=$3
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
export MAP_READER_VERIFY_DIRS=$POLICY
TOOLS=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$LOGDIR"
echo $$ > "$LOGDIR/chain.pid"
echo RUNNING > "$LOGDIR/chain.state"
cd "$COPY" || exit 9
step() {
  local name=$1; shift
  echo "=== $(date -u +%FT%TZ) START $name: $*"
  "$@" > "$LOGDIR/$name.log" 2>&1
  local rc=$?
  echo "=== $(date -u +%FT%TZ) END $name rc=$rc"
  if [ $rc -ne 0 ]; then echo "CHAIN FAILED at $name"; echo "FAILED $name" > "$LOGDIR/chain.state"; exit $rc; fi
}
IBA=scripts/image_b_analysis.py
step grid_analysis "$PY" scripts/grid_analysis.py --bootstrap 10000
step grid_materialise_conditions "$PY" scripts/grid_materialise_conditions.py
step grid_verifier_analysis "$PY" scripts/grid_verifier_analysis.py --materialise-conditions
step stride_verifier_analysis "$PY" scripts/stride_verifier_analysis.py
step grid_incumbent_rescore "$PY" scripts/grid_incumbent_rescore.py
ANCHOR=$("$PY" -c "import json;print(repr(json.load(open('results/grid-2026-08-18/verifier_analysis.json'))['board_best']['g384_ov192']['f1']))")
echo "anchor F1 (text-B verified best) = $ANCHOR"
step image_b_min "$PY" $IBA --union-name union_k10.geojson --anchor-f1 "$ANCHOR"
step image_b_high "$PY" $IBA --cell g384_ov192_image_high --out-dir results/image-b-gs-2026-08-28/high --anchor-f1 "$ANCHOR"
step image_b_pair "$PY" scripts/image_b_pair.py
step plateau "$PY" scripts/stride_plateau_analyses.py
G37=outputs/gemini37-screen-2026-08-28
step g37_k5 "$PY" $IBA --outputs-root $G37 --cell g384_ov192_g37 --k 5 --union-name union_k5.geojson --verify-dir verify --no-ladder --out-dir results/gemini37-screen-2026-08-28 --anchor-f1 "$ANCHOR"
step g37_k10 "$PY" $IBA --outputs-root $G37 --cell g384_ov192_g37 --k 10 --union-name union_k10.geojson --verify-dir verify_k10 --out-dir results/gemini37-screen-2026-08-28/k10 --anchor-f1 "$ANCHOR"
step g37_swap37 "$PY" $IBA --outputs-root $G37 --cell g384_ov192_g37 --k 5 --union-name union_k5.geojson --verify-dir verify_swap37 --no-ladder --out-dir results/gemini37-screen-2026-08-28/swap37 --anchor-f1 "$ANCHOR"
step g38_armv "$PY" $IBA --outputs-root $G37 --cell g384_ov192_g37 --k 5 --union-name union_k5.geojson --verify-dir verify_swap38 --out-dir results/gemini38-screen-2026-09-04/armV --anchor-f1 "$ANCHOR"
step fourth_cell "$PY" $IBA --outputs-root outputs/grid-2026-08-18 --cell g384_ov192 --k 10 --union-name union_k10.geojson --verify-dir verify_37 --no-ladder --out-dir results/gemini37-fourth-cell/gs-leg --anchor-f1 "$ANCHOR"
G37I=outputs/gemini37-image-gs-2026-09-01
step g37img_arm1 "$PY" $IBA --outputs-root $G37I --cell g384_ov192_g37img --k 5 --union-name union_k5.geojson --verify-dir verify_arm1 --no-ladder --out-dir results/gemini37-image-gs-2026-09-01/arm1 --anchor-f1 "$ANCHOR"
step g37img_arm2 "$PY" $IBA --outputs-root $G37I --cell g384_ov192_g37img --k 5 --union-name union_k5.geojson --verify-dir verify_arm2 --no-ladder --out-dir results/gemini37-image-gs-2026-09-01/arm2 --anchor-f1 "$ANCHOR"
step g37img_gap_test "$PY" "$TOOLS/pair_tests.py" "$COPY" gap
step g38_armv_pair "$PY" "$TOOLS/pair_tests.py" "$COPY" armv
step conditions "$PY" "$TOOLS/conditions.py" "$COPY"
echo "=== $(date -u +%FT%TZ) CHAIN DONE"
echo DONE > "$LOGDIR/chain.state"
