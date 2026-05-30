#!/usr/bin/env bash
# =============================================================================
# score-unscored-conditions-2026-05-30.sh
#
# Back-fill canonical evaluations for the 11 aggregation/verification outputs
# that materialised on disk but were never scored with evaluate_detections.py.
# Surfaced while building the manifest generator (gold-standard-v2 vertical
# slice): the conditions schema requires a metrics block (per-buffer F1/P/R +
# a tile_classification MCC block), so an unscored detection set cannot become
# a valid condition. A repo-wide scan found 11 genuine unscored outputs across
# 6 runs (see reports / working-notes for the scan).
#
# PARAMETER CONTROL: each output is scored on ITS OWN run's protocol (bounds,
# ground truth, buffer set), copied verbatim from an evaluation that scored a
# sibling of the same run — NEVER guessed. Only the input detections vary.
# All evals use the project-standard bootstrap (BCa, 10000 iterations, seed 42,
# tile-level resampling) and --mcc (tile-level MCC), matching the source evals
# and the report-MCC-with-F1 convention.
#
# Two scopes apply to the 4-map gold-standard corpus and they are DIFFERENT
# tile pools — do not conflate:
#   * Era-2 487-tile pool  : inputs/vectors/bounds/384/full_evaluation_bounds.geojson
#   * h10-384 327-tile pool: inputs/vectors/bounds/384/h10_test_bounds.geojson
# gold-standard-v2 + its WBF candidate set were evaluated on 487 (buffers
# 5..50); h8-v2 + h10/evaluation-v2 verifier-stage outputs on 327 (buffer 20).
# The 55-map generalisation runs use the 55-map bounds + student-reviewed GT.
#
# CONFIDENCE: rows 1-9 HIGH (scope copied from an exact-path sibling eval or,
# for h8-v2, triangulated to the 327 pool via erratum E51 + the targets' own
# threshold_sweep metadata). Rows 10-11 MEDIUM: no exact-path sibling eval, so
# scope is inferred from the closest run (#10 = text sibling of #9; #11 = the
# gold-standard-v2 487 pool the WBF candidate set derives from).
#
# RUN ON SAPPHIRE (bootstrap CIs are compute-intensive). Activate the venv
# first. Outputs land under results/condition-scoring-backfill-2026-05-30/.
#
# Usage:  bash scripts/score-unscored-conditions-2026-05-30.sh
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."  # repo root

EVAL="python scripts/evaluate_detections.py"
GT_GS="inputs/vectors/references/mounds-reference.geojson"
GT_55="inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
B_487="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
B_327="inputs/vectors/bounds/384/h10_test_bounds.geojson"
B_55="inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
OUT="results/condition-scoring-backfill-2026-05-30"
COMMON="--bootstrap 10000 --seed 42 --mcc"
BUF_GS="5 10 15 20 25 30 35 40 45 50"   # gold-standard-v2 era-2 buffer set
BUF_20="20"                             # verifier-stage operating point
BUF_55="20 30 40 50"                    # 55-map canonical detection buffers

echo "=== gold-standard-v2 consensus thresholds — Era-2 487 pool [HIGH] (completes H3) ==="
# consensus-3of5 / -4of5 / -5of5 = the full H3 vote-threshold sweep on the GS
# corpus. (consensus-4of5 was added after the initial run: the unscored-output
# scan mis-classified it as "scored" because it is referenced elsewhere as a
# verifier provenance source — it has no standalone F1 eval, so it belongs here.)
$EVAL --detections outputs/gs/gold-standard-v2/consensus/consensus-3of5.geojson \
  --bounds "$B_487" --ground-truth "$GT_GS" --buffers $BUF_GS $COMMON \
  --output-dir "$OUT/gs-v2-consensus-3of5" --label gs-v2-consensus-3of5
$EVAL --detections outputs/gs/gold-standard-v2/consensus/consensus-4of5.geojson \
  --bounds "$B_487" --ground-truth "$GT_GS" --buffers $BUF_GS $COMMON \
  --output-dir "$OUT/gs-v2-consensus-4of5" --label gs-v2-consensus-4of5
$EVAL --detections outputs/gs/gold-standard-v2/consensus/consensus-5of5.geojson \
  --bounds "$B_487" --ground-truth "$GT_GS" --buffers $BUF_GS $COMMON \
  --output-dir "$OUT/gs-v2-consensus-5of5" --label gs-v2-consensus-5of5

echo "=== h10/evaluation-v2 verified — h10-384 327 pool, buffer 20 [HIGH] ==="
$EVAL --detections outputs/h10/evaluation-v2/pool_160_hp4hn4/verified/detections_t0.70.geojson \
  --bounds "$B_327" --ground-truth "$GT_GS" --buffers $BUF_20 $COMMON \
  --output-dir "$OUT/h10-evaluation-v2-t0.70" --label h10-evaluation-v2-t0.70
$EVAL --detections outputs/h10/evaluation-v2/pool_160_hp4hn4/verified/detections_vt4_pt0.05.geojson \
  --bounds "$B_327" --ground-truth "$GT_GS" --buffers $BUF_20 $COMMON \
  --output-dir "$OUT/h10-evaluation-v2-vt4-pt0.05" --label h10-evaluation-v2-vt4-pt0.05

echo "=== h8-v2 verifier-stage — h10-384 327 pool, buffer 20 [HIGH] (NOT the 487 pool) ==="
$EVAL --detections outputs/h8-v2/scale-4/verified/detections_t0.25.geojson \
  --bounds "$B_327" --ground-truth "$GT_GS" --buffers $BUF_20 $COMMON \
  --output-dir "$OUT/h8-v2-scale4-t0.25" --label h8-v2-scale4-t0.25
$EVAL --detections outputs/h8-v2/scale-4/verified/detections_vt4_pt0.10.geojson \
  --bounds "$B_327" --ground-truth "$GT_GS" --buffers $BUF_20 $COMMON \
  --output-dir "$OUT/h8-v2-scale4-vt4-pt0.10" --label h8-v2-scale4-vt4-pt0.10
$EVAL --detections outputs/h8-v2/wbf/scale-4/verified/detections_vt4_pt0.10.geojson \
  --bounds "$B_327" --ground-truth "$GT_GS" --buffers $BUF_20 $COMMON \
  --output-dir "$OUT/h8-v2-wbf-scale4-vt4-pt0.10" --label h8-v2-wbf-scale4-vt4-pt0.10
$EVAL --detections outputs/h8-v2/wbf/scale-8/verified/detections_vt4_pt0.15.geojson \
  --bounds "$B_327" --ground-truth "$GT_GS" --buffers $BUF_20 $COMMON \
  --output-dir "$OUT/h8-v2-wbf-scale8-vt4-pt0.15" --label h8-v2-wbf-scale8-vt4-pt0.15

echo "=== 55-map generalisation — 55-map bounds + student-reviewed GT, buffers 20..50 ==="
# #9 HIGH (exact-path sibling eval); #10 MEDIUM (text sibling of #9; no exact eval)
$EVAL --detections outputs/55maps-image-generalisation/consensus/consensus-3of5.geojson \
  --bounds "$B_55" --ground-truth "$GT_55" --buffers $BUF_55 $COMMON \
  --output-dir "$OUT/55maps-image-consensus-3of5" --label 55maps-image-consensus-3of5
$EVAL --detections outputs/55maps-generalisation/verified/verified_detections_paired.geojson \
  --bounds "$B_55" --ground-truth "$GT_55" --buffers $BUF_55 $COMMON \
  --output-dir "$OUT/55maps-gen-verified-paired" --label 55maps-gen-verified-paired

echo "=== wbf gold-standard-v2 candidate set — Era-2 487 pool [MEDIUM] ==="
# #11 MEDIUM: intermediate WBF candidate set; no exact eval. Scored on the
# gold-standard-v2 487 pool it derives from, for comparability with that run.
$EVAL --detections outputs/wbf/gold-standard-v2-detect/wbf_candidates_vote2plus.geojson \
  --bounds "$B_487" --ground-truth "$GT_GS" --buffers $BUF_GS $COMMON \
  --output-dir "$OUT/wbf-gs-v2-detect-vote2plus" --label wbf-gs-v2-detect-vote2plus

echo "=== DONE — 11 evaluations written under $OUT/ ==="