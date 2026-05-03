#!/usr/bin/env bash
# Launch the 55-map image-track human-review session (Streamlit UI).
#
# Scope: re-review pass after the 2026-05-03 image-recovery added 15
# new verified detections (18 missing verifier candidates recovered;
# 15 retained at prob_t=0.15). 14 of the 15 auto-match curator GT at
# R=50m (TP); only 1 (cand 2397, 1627m from any GT) is FP at 50m
# requiring human disambiguation.
#
# Resume: --output points at the existing multi-buffer review CSV;
# the app's resume logic skips already-reviewed candidates.
#
# --prev-review points at the comprehensive yesterday CSV
# (results/55maps-image-generalisation/human-review.csv, 1029 rows
# from 2026-04-20) so its decisions are honoured as the baseline.
#
# Output: results/55maps-image-generalisation/human-review-multi-buffer.csv
#   — schema matches the corrected-F1 multi-buffer pipeline's
#     "review_today" CSV (and the matching T=0.7 / text-MIN multi-buffer
#     CSVs).
#
# Ground truth: inputs/vectors/references/student-mounds-55maps-reviewed.geojson
#   — deduped student GT (Hairy filter applied; commit 2026-04-19).
#
# Usage:
#   bash scripts/launch_55maps_image_review.sh
#
# Open the Streamlit URL printed in the terminal (default
# http://localhost:8501). Decisions persist on every click; closing
# the browser does not lose work. To resume an interrupted session,
# re-run the same command.

set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p results/55maps-image-generalisation

exec .venv/bin/streamlit run scripts/review_candidates.py -- \
    --crops-dir outputs/55maps-image-generalisation/crops \
    --probabilities outputs/55maps-image-generalisation/verified/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --output results/55maps-image-generalisation/human-review-multi-buffer.csv \
    --prev-review results/55maps-image-generalisation/human-review.csv \
    --threshold 0.15 \
    --buffer 50
