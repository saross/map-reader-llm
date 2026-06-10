#!/usr/bin/env bash
# ============================================================================
# run_vr_registration_evals.sh
# ----------------------------------------------------------------------------
# Session 111 ($0): standard 14-buffer + MCC evaluations (bootstrap 1000,
# seed 42 — the evaluate_detections.py defaults) for the 14 condition sets
# being registered for the verifier-robustness programme. One invocation per
# cell, all 14 launched concurrently (zbook 14-worker cap), each writing
# results/verifier-robustness/evals/<label>/evaluation.json.
#
# Usage (on zbook):  bash scripts/run_vr_registration_evals.sh
# ============================================================================
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
VR=results/verifier-robustness
B384=inputs/vectors/bounds/384/full_evaluation_bounds.geojson
B256=inputs/vectors/bounds/256/full_evaluation_bounds.geojson

# label|detections|bounds
CELLS="
verified-384-union-t0-0-n5|$VR/matrix-sets/min-T0.0.geojson|$B384
verified-256-union-t0-0-n5|$VR/condition-sets/vr-256-union-t0-0-n5.geojson|$B256
verified-256-ge3of5-t0-3-n5|$VR/condition-sets/vr-256-ge3of5-t0-3-n5.geojson|$B256
verified-384-ge3of5-t0-3-n5|$VR/matrix-sets/min-T0.3.geojson|$B384
verified-384-ge3of5-t0-7-n5|$VR/matrix-sets/min-T0.7.geojson|$B384
verified-384-ge3of5-t0-3-high-n5|$VR/matrix-sets/high-T0.3.geojson|$B384
verified-384-ge3of5-t0-7-high-n5|$VR/matrix-sets/high-T0.7.geojson|$B384
verified-384-16of30-t0-3-n5-opmax|$VR/opmax-sets/opmax-16of30-N5minT0.3-vt3-pt0.15.geojson|$B384
verified-adv-text-4of5|$VR/pareto/cheap6-4of5-n1-pt0.15.geojson|$B384
verified-adv-text-6of10|$VR/pareto/nof10-6of10-n1-pt0.2.geojson|$B384
verified-adv-text-high-vf-4of5|$VR/matrix-sets/high-T0.0.geojson|$B384
verified-adv-text-medium-vf-4of5|$VR/condition-sets/medium-vf-4of5.geojson|$B384
verified-adv-pro-text-flash-vf-3of5|$VR/condition-sets/pro-flash-vf-3of5.geojson|$B384
verified-adv-pro-text-pro-vf-3of5|$VR/condition-sets/pro-pro-vf-3of5.geojson|$B384
"

pids=()
for row in $CELLS; do
    label="${row%%|*}"; rest="${row#*|}"
    det="${rest%%|*}"; bounds="${rest#*|}"
    out="$VR/evals/$label"
    mkdir -p "$out"
    echo "launching $label"
    $PY scripts/evaluate_detections.py --detections "$det" --bounds "$bounds" \
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
