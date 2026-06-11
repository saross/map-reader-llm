#!/usr/bin/env bash
# ============================================================================
# run_second_wave_evals.sh
# ----------------------------------------------------------------------------
# Session 113 ($0): standard 14-buffer + MCC evaluations (bootstrap 1000,
# seed 42 — the evaluate_detections.py defaults) for the three GS-side
# second-wave registration cells that lack a committed evaluation.json
# (the min6/min11 and Flash 3.5 cells already have theirs under
# results/flash35-2x2/evals/). Each cell writes
# results/verifier-robustness/evals/<condition-label>/evaluation.json —
# the same eval home the S111 pv-diag-384 additions used.
#
# Usage (sapphire):  bash scripts/run_second_wave_evals.sh
# ============================================================================
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
VR=results/verifier-robustness
B384=inputs/vectors/bounds/384/full_evaluation_bounds.geojson

# condition label|detections
CELLS="
verified-adv-text-t03-4of5|$VR/condition-sets/t03-4of5-n1-pt0.2.geojson
verified-adv-image-3of5|$VR/condition-sets/image-3of5-n1-pt0.15.geojson
verified-adv-text-pro-vf-4of5|$VR/min-thinking-sets/high6-PRO-vf-4of5-pt0.25.geojson
"

pids=()
for row in $CELLS; do
    label="${row%%|*}"; det="${row#*|}"
    out="$VR/evals/$label"
    mkdir -p "$out"
    echo "launching $label"
    $PY scripts/evaluate_detections.py --detections "$det" --bounds "$B384" \
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
for row in $CELLS; do
    label="${row%%|*}"
    f1=$($PY -c "import json; s=json.load(open('$VR/evals/$label/evaluation.json'))['summary']; print([b['f1'] for b in s['buffers'] if b['buffer_metres']==20][0], s['n_detections'])" 2>/dev/null || echo "MISSING")
    echo "$label: $f1"
done
exit $fail
