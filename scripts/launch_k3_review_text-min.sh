#!/usr/bin/env bash
# Pass-1 (genuinely-new) k3-shell review for 55maps-text-min-generalisation — 55-map deployment oracle.
# Renders context crops live from the local rasters; pass-2 auto-fills are in
# results/deployment-oracle-2026-06-06/k3-review/55maps-text-min-generalisation/pass2-autofill.csv (confirm separately).
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/streamlit run scripts/review_candidates.py -- \
    --crops-dir results/deployment-oracle-2026-06-06/k3-review/55maps-text-min-generalisation/pass1-new/crops \
    --probabilities results/deployment-oracle-2026-06-06/k3-review/55maps-text-min-generalisation/pass1-new/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --output results/deployment-oracle-2026-06-06/k3-review/55maps-text-min-generalisation/pass1-new/human-review.csv \
    --prev-review "" \
    --threshold 0.15 \
    --buffer 50
