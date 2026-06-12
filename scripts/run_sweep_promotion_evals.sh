#!/usr/bin/env bash
# ============================================================================
# run_sweep_promotion_evals.sh
# ----------------------------------------------------------------------------
# Session 113 ($0): standard 14-buffer + MCC evaluations for the 16
# promotable completeness-sweep cells (Shawn, 2026-06-12). Detection sets
# from scripts/materialise_sweep_cells.py under
# results/verifier-robustness/sweep-sets/<label>.geojson; each cell writes
# results/verifier-robustness/evals/<label>/evaluation.json (the eval home
# the S111/S113 pv-diag-384 additions use). All 16 launched concurrently
# (zbook, within the 14-worker etiquette: evals are I/O-light).
#
# Usage (zbook):  bash scripts/run_sweep_promotion_evals.sh
# ============================================================================
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
VR=results/verifier-robustness
B384=inputs/vectors/bounds/384/full_evaluation_bounds.geojson

LABELS="
verified-adv-image-min-3of5
verified-adv-image-min-6of10
verified-adv-image-baseline
verified-adv-image-baseline-medium-vf
verified-adv-image-baseline-pro-vf
verified-adv-text-baseline
verified-adv-text-baseline-medium-vf
verified-adv-text-baseline-pro-vf
verified-adv-pro-text-medium-vf-3of5
verified-adv-pro-image-pro-vf-3of5
verified-adv-pro-text-baseline
verified-adv-pro-text-baseline-medium-vf
verified-adv-pro-text-baseline-pro-vf
verified-adv-pro-image-baseline
verified-adv-pro-image-baseline-medium-vf
verified-adv-pro-image-baseline-pro-vf
"

pids=()
for label in $LABELS; do
    out="$VR/evals/$label"
    mkdir -p "$out"
    echo "launching $label"
    $PY scripts/evaluate_detections.py \
        --detections "$VR/sweep-sets/$label.geojson" --bounds "$B384" \
        --buffers 5 10 15 20 25 30 35 40 45 50 75 100 125 150 \
        --mcc --label "$label" --output-dir "$out" \
        > "$out/eval.log" 2>&1 &
    pids+=($!)
done

fail=0
for pid in "${pids[@]}"; do
    wait "$pid" || fail=1
done

echo "--- F1@20m per cell ---"
for label in $LABELS; do
    f1=$($PY -c "import json; s=json.load(open('$VR/evals/$label/evaluation.json'))['summary']; print([b['f1'] for b in s['buffers'] if b['buffer_metres']==20][0], s['n_detections'])" 2>/dev/null || echo "MISSING")
    echo "$label: $f1"
done
exit $fail
