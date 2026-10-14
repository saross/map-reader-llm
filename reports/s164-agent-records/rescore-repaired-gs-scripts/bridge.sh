#!/usr/bin/env bash
# =============================================================================
# bridge.sh — Run B's cells and gap tests (the modality bridge) in one copy
# =============================================================================
# The commands of scripts/modality-bridge-2026-10-07-score.sh at the branch
# head (the three Run B legs named `verify_g3`, read under the leg rule), run
# in COPY under POLICY, with one change: the text-B anchor F1 the anchor gate
# checks is this copy's re-scored value (rounded to 4 dp, as registered), not
# the hard-coded 0.8961, because under the repaired reading the anchor set
# itself is re-materialised. In an ORIGIN copy the value is 0.8961, so the
# commands equal the committed driver's.
#
# Usage: bridge.sh <copy_dir> <fixed|repaired> <log_dir>
# =============================================================================
set -uo pipefail
COPY=$1; POLICY=$2; LOGDIR=$3
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 MAP_READER_VERIFY_DIRS=$POLICY
mkdir -p "$LOGDIR"; echo $$ > "$LOGDIR/bridge.pid"; echo RUNNING > "$LOGDIR/bridge.state"
cd "$COPY" || exit 9
O=outputs/modality-bridge-2026-10-07
R=results/modality-bridge-2026-10-07
mkdir -p $R/logs
ANCHOR=$("$PY" -c "import json;print(round(json.load(open('results/grid-2026-08-18/verifier_analysis.json'))['board_best']['g384_ov192']['f1'],4))")
echo "anchor $ANCHOR"
FAILS=0
cell() {  # name root cellver k union verify [op]
  local name=$1 root=$2 ver=$3 k=$4 union=$5 vdir=$6 op=${7:-}
  local extra=()
  [ "$k" = 5 ] && extra+=(--no-ladder) || extra+=(--write-rung-sets)
  [ -n "$op" ] && extra+=(--operating-point "$op")
  "$PY" scripts/image_b_analysis.py --six-cell-gate --outputs-root "$O/$root" --cell "$ver" \
    --k "$k" --union-name "$union" --verify-dir "$vdir" "${extra[@]}" --out-dir "$R/$name" \
    --anchor-f1 "$ANCHOR" > "$LOGDIR/bridge-$name.log" 2>&1
  local rc=$?; echo "cell $name exit $rc"; [ $rc -ne 0 ] && FAILS=$((FAILS+1))
}
TI=detect_brief-text-image; TX=detect_brief-text
cell g3-text-g3v          g3-text          $TX 10 union_k10.geojson verify_g3           0.15,10
cell g3-image-g3v         g3-image         $TI 10 union_k10.geojson verify_g3           0.15,9
cell g37-text-g3v         g37-text         $TX 5  union_k5.geojson  verify_g3_repaired  0.10,5
cell g37-text-g37v        g37-text         $TX 5  union_k5.geojson  verify_g37_repaired 0.80,5
cell g37-image-g3v        g37-image        $TI 5  union_k5.geojson  verify_g3_repaired  0.10,5
cell g37-image-g37v       g37-image        $TI 5  union_k5.geojson  verify_g37_repaired 0.90,5
cell g37-image-cache-g3v  g37-image-cache  $TI 5  union_k5.geojson  verify_g3_repaired  0.10,5
cell g37-image-cache-g37v g37-image-cache  $TI 5  union_k5.geojson  verify_g37_repaired 0.90,5
cell g3-text-temp1-g3v    g3-text-temp1    $TX 5  union_k5.geojson  verify_g3
cell g3-image-temp1-g3v   g3-image-temp1   $TI 5  union_k5.geojson  verify_g3_repaired
gap() { local name=$1; shift; "$PY" scripts/gemini37_image_gap_test.py --six-cell-gate "$@" \
  > "$LOGDIR/bridge-gap-$name.log" 2>&1; local rc=$?; echo "gap $name exit $rc"; [ $rc -ne 0 ] && FAILS=$((FAILS+1)); }
gap d49 --pair g3 $R/g3-text-g3v $R/g3-image-g3v \
  --pair carried-verifier $R/g37-text-g3v $R/g37-image-g3v \
  --pair all-3.7 $R/g37-text-g37v $R/g37-image-g37v --reference-pair g3 --out-dir $R
gap k5 --set-name verified_ladder_n5_20m --pair g3-k5 $R/g3-text-g3v $R/g3-image-g3v --out-dir $R/k5
gap additions --set-name verified_best_20m \
  --pair g3-t1-k5 $R/g3-text-temp1-g3v $R/g3-image-temp1-g3v \
  --pair fifth-leg-g3v $R/g37-text-g3v $R/g37-image-cache-g3v \
  --pair fifth-leg-g37v $R/g37-text-g37v $R/g37-image-cache-g37v \
  --pair g3-best $R/g3-text-g3v $R/g3-image-g3v \
  --pair carried-verifier-best $R/g37-text-g3v $R/g37-image-g3v \
  --pair all-3.7-best $R/g37-text-g37v $R/g37-image-g37v \
  --reference-pair g3-t1-k5 --out-dir $R/additions
echo "=== $(date -u +%FT%TZ) BRIDGE DONE fails=$FAILS"
if [ $FAILS -eq 0 ]; then echo DONE > "$LOGDIR/bridge.state"; else echo "FAILED $FAILS" > "$LOGDIR/bridge.state"; fi
