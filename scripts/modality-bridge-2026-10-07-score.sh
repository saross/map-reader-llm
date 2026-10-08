#!/usr/bin/env bash
# =============================================================================
# Run B, the modality bridging pair — scoring (offline, no API call)
# =============================================================================
#
# Scores every Run B cell and the gap tests after Stage 2 has landed, behind
# the six-cell anchor gate (each invocation refuses to write unless the six
# original cells reproduce). The six D49 cells follow the Stage 2 card's § 6
# (planning/modality-bridge-2026-10-07-stage2.md) at their original
# operating points; the four added-arm cells (Stage 1 card § 4.8) are scored
# at their swept best point, the two temperature-matched Gemini 3 cells having
# no original operating point. Three gap tests: the D49 pairs
# (`gap_test.json`), the inherited Gemini 3 K = 5 rung (`k5/`), and the
# additions with the D49 pairs at their best points for comparison
# (`additions/`). Run from the repository root on sapphire; about 1 h.
#
# Not built here (Stage 2 card § 6): the tile-level interaction permutation
# for the gap change, and the D45/D46 floors.
#
# Usage:
#   bash scripts/modality-bridge-2026-10-07-score.sh
#
# Created: 2026-10-07 (Session 163)
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0
# =============================================================================
set -u
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
O=outputs/modality-bridge-2026-10-07
R=results/modality-bridge-2026-10-07
cell() {  # name root cellver k union verify [op]
  local name=$1 root=$2 ver=$3 k=$4 union=$5 vdir=$6 op=${7:-}
  local extra=()
  [ "$k" = 5 ] && extra+=(--no-ladder) || extra+=(--write-rung-sets)
  [ -n "$op" ] && extra+=(--operating-point "$op")
  $PY scripts/image_b_analysis.py --six-cell-gate --outputs-root "$O/$root" --cell "$ver" \
    --k "$k" --union-name "$union" --verify-dir "$vdir" "${extra[@]}" --out-dir "$R/$name" \
    > "$R/logs/$name.log" 2>&1
  echo "cell $name exit $?"
}
mkdir -p $R/logs
TI=detect_brief-text-image; TX=detect_brief-text
cell g3-text-g3v          g3-text          $TX 10 union_k10.geojson verify_g3_repaired  0.15,10
cell g3-image-g3v         g3-image         $TI 10 union_k10.geojson verify_g3_repaired  0.15,9
cell g37-text-g3v         g37-text         $TX 5  union_k5.geojson  verify_g3_repaired  0.10,5
cell g37-text-g37v        g37-text         $TX 5  union_k5.geojson  verify_g37_repaired 0.80,5
cell g37-image-g3v        g37-image        $TI 5  union_k5.geojson  verify_g3_repaired  0.10,5
cell g37-image-g37v       g37-image        $TI 5  union_k5.geojson  verify_g37_repaired 0.90,5
cell g37-image-cache-g3v  g37-image-cache  $TI 5  union_k5.geojson  verify_g3_repaired  0.10,5
cell g37-image-cache-g37v g37-image-cache  $TI 5  union_k5.geojson  verify_g37_repaired 0.90,5
cell g3-text-temp1-g3v    g3-text-temp1    $TX 5  union_k5.geojson  verify_g3_repaired
cell g3-image-temp1-g3v   g3-image-temp1   $TI 5  union_k5.geojson  verify_g3_repaired
$PY scripts/gemini37_image_gap_test.py --six-cell-gate \
  --pair g3 $R/g3-text-g3v $R/g3-image-g3v \
  --pair carried-verifier $R/g37-text-g3v $R/g37-image-g3v \
  --pair all-3.7 $R/g37-text-g37v $R/g37-image-g37v \
  --reference-pair g3 --out-dir $R > $R/logs/gap-d49.log 2>&1; echo "gap d49 exit $?"
$PY scripts/gemini37_image_gap_test.py --six-cell-gate --set-name verified_ladder_n5_20m \
  --pair g3-k5 $R/g3-text-g3v $R/g3-image-g3v --out-dir $R/k5 > $R/logs/gap-k5.log 2>&1; echo "gap k5 exit $?"
$PY scripts/gemini37_image_gap_test.py --six-cell-gate --set-name verified_best_20m \
  --pair g3-t1-k5 $R/g3-text-temp1-g3v $R/g3-image-temp1-g3v \
  --pair fifth-leg-g3v $R/g37-text-g3v $R/g37-image-cache-g3v \
  --pair fifth-leg-g37v $R/g37-text-g37v $R/g37-image-cache-g37v \
  --pair g3-best $R/g3-text-g3v $R/g3-image-g3v \
  --pair carried-verifier-best $R/g37-text-g3v $R/g37-image-g3v \
  --pair all-3.7-best $R/g37-text-g37v $R/g37-image-g37v \
  --reference-pair g3-t1-k5 --out-dir $R/additions > $R/logs/gap-additions.log 2>&1; echo "gap additions exit $?"
echo SCORING-DONE
