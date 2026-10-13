#!/usr/bin/env bash
# Re-score the GS grid, stride, plateau, and Image-B chain in one disposable
# copy, in dependency order, single-threaded, one process at a time.
# Usage: chain.sh <copy_dir> <fixed|legacy> <log_dir>
set -uo pipefail
COPY=$1; MODE=$2; LOGDIR=$3
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
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
if [ "$MODE" = fixed ]; then
  # Non-fatal: a mismatch is recorded (rc 3) and read before any number is used.
  echo "=== $(date -u +%FT%TZ) START legacy_extras"
  "$PY" "$TOOLS/legacy_extras.py" "$COPY" "$LOGDIR/legacy_extras.json" > "$LOGDIR/legacy_extras.log" 2>&1
  echo "=== $(date -u +%FT%TZ) END legacy_extras rc=$?"
fi
step grid_analysis "$PY" scripts/grid_analysis.py --bootstrap 10000
step grid_materialise_conditions "$PY" scripts/grid_materialise_conditions.py
step grid_verifier_analysis "$PY" scripts/grid_verifier_analysis.py --materialise-conditions
step stride_verifier_analysis "$PY" scripts/stride_verifier_analysis.py
step grid_incumbent_rescore "$PY" scripts/grid_incumbent_rescore.py
ANCHOR=$("$PY" -c "import json;print(repr(json.load(open('results/grid-2026-08-18/verifier_analysis.json'))['board_best']['g384_ov192']['f1']))")
echo "anchor F1 (text-B verified best) = $ANCHOR"
if [ "$MODE" = fixed ]; then
  step image_b_min "$PY" scripts/image_b_analysis.py --union-name union_k10.geojson --anchor-f1 "$ANCHOR"
  step image_b_high "$PY" scripts/image_b_analysis.py --cell g384_ov192_image_high --out-dir results/image-b-gs-2026-08-28/high --anchor-f1 "$ANCHOR"
  step image_b_pair "$PY" scripts/image_b_pair.py
else
  step image_b_min "$PY" scripts/image_b_analysis.py --union-name union_k10.geojson
  step image_b_high "$PY" scripts/image_b_analysis.py --cell g384_ov192_image_high --out-dir results/image-b-gs-2026-08-28/high
fi
step plateau "$PY" scripts/stride_plateau_analyses.py
echo "=== $(date -u +%FT%TZ) CHAIN DONE"
echo DONE > "$LOGDIR/chain.state"
