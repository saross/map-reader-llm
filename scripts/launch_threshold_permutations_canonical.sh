#!/usr/bin/env bash
# ===========================================================================
# T2d — k3-vs-k4 paired permutations against the CANONICAL extended GT
# ===========================================================================
# Session 105. Moves the threshold-axis claim (3-of-5 beats the carried 4-of-5)
# from findings §1's PER-RUN extended GTs onto the single canonical adjudicated
# GT used for the config-axis and joint-oracle (§§3-4b). For each of the three
# text configs, runs a tile-swap paired permutation (corrected-F1, fixed-union)
# of the carried k4 vs the looser k3, full 14-buffer sweep.
#
# Uses the SAME script + canonical review (`canonical-review.csv` as
# review-today for BOTH conditions; empty review-yesterday) that produced §4b.
# $0 — no API. Run on zbook.
#
# Usage:  bash scripts/launch_threshold_permutations_canonical.sh
# ===========================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
SCRIPT=scripts/paired_permutation_corrected_55maps.py
REVIEW=results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv
EMPTY=results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv
OUTBASE=results/55maps-extended-gt-2026-06-07/threshold-permutations
BUFFERS="5 10 15 20 25 30 35 40 45 50 75 100 125 150"

K3DIR=results/deployment-oracle-2026-06-06/k3-scoring

# config : k4-detections : k3-detections
declare -A K4 K3
K4[TH7]=outputs/55maps-text-high-generalisation/verified/verified_detections.geojson
K3[TH7]=$K3DIR/55maps-text-high-generalisation/k3_verified.geojson
K4[T03]=outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson
K3[T03]=$K3DIR/55maps-text-high-t0.3-generalisation/k3_verified.geojson
K4[TM]=outputs/55maps-text-min-generalisation/verified/verified_detections.geojson
K3[TM]=$K3DIR/55maps-text-min-generalisation/k3_verified.geojson

for cfg in TH7 T03 TM; do
    echo "=== ${cfg}: k4 vs k3 (canonical GT) ==="
    $PY "$SCRIPT" \
        --label-a "${cfg}-k4" --detections-a "${K4[$cfg]}" \
        --review-yesterday-a "$EMPTY" --review-today-a "$REVIEW" \
        --label-b "${cfg}-k3" --detections-b "${K3[$cfg]}" \
        --review-yesterday-b "$EMPTY" --review-today-b "$REVIEW" \
        --buffers $BUFFERS \
        --output-dir "${OUTBASE}/${cfg}_k4_vs_k3"
done
echo "=== threshold permutations complete ==="
