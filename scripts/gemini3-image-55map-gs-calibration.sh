#!/usr/bin/env bash
# Gemini 3 image at 55-map scale: the Gold Standard CALIBRATION leg.
#
# The image proposer x verifier 2x2 at deployment scale has two proposer
# pools (3.7 image, Gemini 3 image; both 5 x 24,561) and two verifier arms
# (arm 1 Gemini 3 `minimal`, arm 2 3.7 `low`). The 3.7 row's carried
# operating points came from a GS calibration leg on the 3.7 GS image pool
# (`outputs/gemini37-image-gs-2026-09-01`, commit 30e36bcd1 for K = 3; the
# gemini37-image-gs run itself for K = 5). The Gemini 3 row needs the same
# leg on the Gemini 3 GS image pool, and `image-b-gs-2026-08-28` is a
# near-perfect source: Gemini 3, `minimal`, T = 0.7, the same g384_ov192
# geometry, ten passes. Its carried points therefore cost no proposer spend,
# only these small GS verifier legs.
#
# Mirrors the 3.7 leg stage for stage:
#   unions   first-N K = 3 and K = 5 built by scripts/merge_passes.py
#            (`--threshold 1`), the builder that reproduces the committed 3.7
#            GS K = 5 union byte-identically (deltas report B2). NOT the
#            stride builder, which is the 55-map union rule; the two differ
#            (683 vs 622 on the 3.7 GS pool at K = 3).
#   crops    scripts/run_pv.py extract, padding 75, from the GS rasters.
#   arms     scripts/run_pv.py verify, realtime flex, T = 0.0, both arms per
#            rung — four legs. Idempotent: a leg whose probabilities.json
#            exists is skipped, so a resumed run never re-spends.
#   sweeps   scripts/image_b_analysis.py at the GS-primary 20 m buffer, the
#            tool that wrote results/gemini37-image-55map-2026-09-13/
#            gs-calibration/ (its anchor gate re-scores text-B at 0.8961).
#            One results directory per rung per arm; the carried point is
#            `image_best` in each analysis.json.
#
# Runbook:
#   Precondition: unions and crops exist (built by the S155 free-builds job;
#     this script refuses to run without them rather than building them
#     itself, so the union rule is chosen once, deliberately).
#   Artefacts:  outputs/image-b-gs-2026-08-28/verifier/g384_ov192_image/
#                 verify_k{3,5}_arm{1,2}/probabilities.json + run.meta.json
#               results/gemini3-image-55map-2026-09-16/gs-calibration/
#                 k{3,5}/arm{1,2}/{analysis.json,sweep_20m.csv,
#                 verified_best_20m.geojson}
#   Finished:   "GS CALIBRATION DONE" on stdout; four analysis.json present.
#   Stop:       set -e — any stage's failure stops the script.
#   Verify:     the operator reads each arm's run.meta.json items_processed
#               against its union count, and each analysis.json image_best,
#               before any 55-map leg is launched with those points.
#
# Usage (from ~/Code/map-reader-llm on sapphire):
#     bash scripts/gemini3-image-55map-gs-calibration.sh
#     WORKERS=50 bash scripts/gemini3-image-55map-gs-calibration.sh
#
# Created: 2026-09-18 (S155)
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0

set -euo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
OUTROOT=outputs/image-b-gs-2026-08-28
CELL=g384_ov192_image
VROOT=$OUTROOT/verifier/$CELL
RESULTS=results/gemini3-image-55map-2026-09-16/gs-calibration
VERIFIER_CONFIG=prompts/configs/verify_adversarial-text.json
WORKERS=${WORKERS:-50}
KS=${KS:-"3 5"}

# The two verifier arms, exactly as the 3.7 campaign card section 2 fixes
# them (scripts/gemini37-image-55map-unions-and-arms.sh).
ARM1_MODEL=gemini-3-flash-preview
ARM1_THINKING=minimal
ARM2_MODEL=gemini-3.7-flash
ARM2_THINKING=low

echo "=== stage 0: inputs present $(date -Is)"
for k in $KS; do
  test -f "$VROOT/union_k$k.geojson" || { echo "missing $VROOT/union_k$k.geojson"; exit 2; }
  test -f "$VROOT/crops_k$k/candidate_manifest.json" || { echo "missing crops_k$k manifest"; exit 2; }
  n=$($PY -c "import json,sys; print(len(json.load(open(sys.argv[1]))['features']))" "$VROOT/union_k$k.geojson")
  m=$($PY -c "import json,sys; d=json.load(open(sys.argv[1])); print(len(d if isinstance(d,list) else d.get('candidates', d)))" "$VROOT/crops_k$k/candidate_manifest.json")
  echo "union_k$k: $n candidates; crops_k$k manifest: $m"
  [ "$n" = "$m" ] || { echo "union/crops count mismatch for k=$k"; exit 2; }
done

echo "=== stage 1: four verifier arms, sequentially $(date -Is)"
for k in $KS; do
  for arm in arm1 arm2; do
    dest=$VROOT/verify_k${k}_${arm}
    if [ -f "$dest/probabilities.json" ]; then
      echo "verify_k${k}_${arm} already done, skipping"
      continue
    fi
    if [ "$arm" = "arm1" ]; then
      model=$ARM1_MODEL; thinking=$ARM1_THINKING
    else
      model=$ARM2_MODEL; thinking=$ARM2_THINKING
    fi
    echo "--- verify_k${k}_${arm}: $model / $thinking $(date -Is)"
    $PY scripts/run_pv.py verify \
      --crops-dir "$VROOT/crops_k$k" \
      --verifier-config "$VERIFIER_CONFIG" \
      --output-dir "$dest" \
      --mode realtime \
      --model "$model" \
      --thinking-level "$thinking" \
      --temperature 0.0 \
      --service-tier flex \
      --workers "$WORKERS"
  done
done

echo "=== stage 2: sweeps at 20 m, carried points $(date -Is)"
for k in $KS; do
  for arm in arm1 arm2; do
    out=$RESULTS/k$k/$arm
    if [ -f "$out/analysis.json" ]; then
      echo "$out already swept, skipping"
      continue
    fi
    $PY scripts/image_b_analysis.py \
      --cell "$CELL" --outputs-root "$OUTROOT" --k "$k" --no-ladder \
      --union-name "union_k$k.geojson" --verify-dir "verify_k${k}_${arm}" \
      --out-dir "$out"
    $PY -c "
import json, sys
d = json.load(open(sys.argv[1]))['image_best']
print(f'  k{sys.argv[2]} {sys.argv[3]}: carried (prob_t {d[\"prob_t\"]:.2f}, k{d[\"min_votes\"]}) F1@20 {d[\"f1\"]:.4f} P {d[\"precision\"]:.4f} R {d[\"recall\"]:.4f} n {d[\"n_detections\"]}')
" "$out/analysis.json" "$k" "$arm"
  done
done

echo "GS CALIBRATION DONE $(date -Is)"
