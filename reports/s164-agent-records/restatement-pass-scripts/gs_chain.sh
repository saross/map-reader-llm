#!/usr/bin/env bash
# =============================================================================
# gs_chain.sh — the S164 restatement pass's GS chain in one disposable copy
# =============================================================================
# Part of the restatement pass (reports/s164-agent-records/
# restatement-pass.md § 1.2). The 2026-10-13 re-score's chain.sh
# (rescore-repaired-gs-scripts/) on the pass's branch head, with four
# changes: the 3.7 image carried arm also writes its registered set
# (--operating-point 0.10,5; PI ruling D65 (3)); the gap and Arm V tests run
# their own scripts (their constants carry the dated update); the text-B
# anchor F1 is the dated default (image_b_analysis.ANCHOR_F1_20); and the
# registered conditions, the grid selection-aware pilots, and the
# sensitivity table follow. Every leg is read under the default leg rule
# (MAP_READER_VERIFY_DIRS unset: the re-verified rows). Single-threaded,
# one process at a time.
#
# Usage: gs_chain.sh <copy_dir> <log_dir>
# Writes <log_dir>/chain.pid and <log_dir>/chain.state (RUNNING, DONE, or
# FAILED <step>); each step's output goes to <log_dir>/<step>.log.
# =============================================================================
set -uo pipefail
COPY=$1; LOGDIR=$2
PY=$HOME/Code/map-reader-llm/.venv/bin/python
TOOLS=$(cd "$(dirname "$0")" && pwd)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
unset MAP_READER_VERIFY_DIRS
mkdir -p "$LOGDIR"
echo $$ > "$LOGDIR/chain.pid"
echo RUNNING > "$LOGDIR/chain.state"
cd "$COPY" || exit 9
step() {
  local name=$1; shift
  echo "=== $(date -u +%FT%TZ) START $name: $*"
  "$@" > "$LOGDIR/$name.log" 2>&1 < /dev/null
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
step image_b_min "$PY" $IBA --union-name union_k10.geojson
step image_b_high "$PY" $IBA --cell g384_ov192_image_high --out-dir results/image-b-gs-2026-08-28/high
step image_b_pair "$PY" scripts/image_b_pair.py
step plateau "$PY" scripts/stride_plateau_analyses.py
G37=outputs/gemini37-screen-2026-08-28
step g37_k5 "$PY" $IBA --outputs-root $G37 --cell g384_ov192_g37 --k 5 --union-name union_k5.geojson --verify-dir verify --no-ladder --out-dir results/gemini37-screen-2026-08-28
step g37_k10 "$PY" $IBA --outputs-root $G37 --cell g384_ov192_g37 --k 10 --union-name union_k10.geojson --verify-dir verify_k10 --out-dir results/gemini37-screen-2026-08-28/k10
step g37_swap37 "$PY" $IBA --outputs-root $G37 --cell g384_ov192_g37 --k 5 --union-name union_k5.geojson --verify-dir verify_swap37 --no-ladder --out-dir results/gemini37-screen-2026-08-28/swap37
step g38_armv "$PY" $IBA --outputs-root $G37 --cell g384_ov192_g37 --k 5 --union-name union_k5.geojson --verify-dir verify_swap38 --out-dir results/gemini38-screen-2026-09-04/armV
step fourth_cell "$PY" $IBA --outputs-root outputs/grid-2026-08-18 --cell g384_ov192 --k 10 --union-name union_k10.geojson --verify-dir verify_37 --no-ladder --out-dir results/gemini37-fourth-cell/gs-leg
G37I=outputs/gemini37-image-gs-2026-09-01
step g37img_arm1 "$PY" $IBA --outputs-root $G37I --cell g384_ov192_g37img --k 5 --union-name union_k5.geojson --verify-dir verify_arm1 --no-ladder --out-dir results/gemini37-image-gs-2026-09-01/arm1 --operating-point 0.10,5
step g37img_arm2 "$PY" $IBA --outputs-root $G37I --cell g384_ov192_g37img --k 5 --union-name union_k5.geojson --verify-dir verify_arm2 --no-ladder --out-dir results/gemini37-image-gs-2026-09-01/arm2
step g37img_gap_test "$PY" scripts/gemini37_image_gap_test.py
step g38_armv_pair "$PY" scripts/gemini38_armv_pair_test.py
step gs_conditions "$PY" "$TOOLS/gs_conditions.py" "$COPY"
for cell in g384_ov048 g384_ov192 g512_ov064 g512_ov256; do
  step "sa_${cell}_m1" "$PY" scripts/selection_aware_intervals.py --cell $cell --K 10 --bootstrap 10000 --out results/selection-aware/
done
for m in 0.25 0.5; do
  step "sa_g512_ov064_m$m" "$PY" scripts/selection_aware_intervals.py --cell g512_ov064 --K 10 --bootstrap 10000 --m-frac $m --out results/selection-aware/
done
step sensitivity_mde "$PY" scripts/sensitivity_mde.py
step sensitivity_mde_r2 "$PY" scripts/sensitivity_mde.py --reference r2
echo "=== $(date -u +%FT%TZ) CHAIN DONE"
echo DONE > "$LOGDIR/chain.state"
