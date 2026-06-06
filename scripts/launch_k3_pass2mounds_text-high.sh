#!/usr/bin/env bash
# Pass-2 MOUNDS-ONLY active confirm for 55maps-text-high-generalisation (no pre-fill -> every inherited
# mound appears in the queue so you can eyeball the crop and confirm/correct).
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/streamlit run scripts/review_candidates.py -- \
    --crops-dir results/deployment-oracle-2026-06-06/k3-review/55maps-text-high-generalisation/pass2-mounds-confirm/crops \
    --probabilities results/deployment-oracle-2026-06-06/k3-review/55maps-text-high-generalisation/pass2-mounds-confirm/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --output results/deployment-oracle-2026-06-06/k3-review/55maps-text-high-generalisation/pass2-mounds-confirm/human-review.csv \
    --prev-review "" \
    --threshold 0.15 --buffer 50
