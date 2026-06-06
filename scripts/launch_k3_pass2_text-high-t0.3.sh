#!/usr/bin/env bash
# Pass-2 auto-fill review for 55maps-text-high-t0.3-generalisation. FULL-ACTIVE
# mode: no pre-fill, so EVERY auto-fill candidate (inherited mound AND
# not_mound) appears in the queue for active confirm/correct. Leave toggle OFF.
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/streamlit run scripts/review_candidates.py -- \
    --crops-dir results/deployment-oracle-2026-06-06/k3-review/55maps-text-high-t0.3-generalisation/pass2-review/crops \
    --probabilities results/deployment-oracle-2026-06-06/k3-review/55maps-text-high-t0.3-generalisation/pass2-review/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --output results/deployment-oracle-2026-06-06/k3-review/55maps-text-high-t0.3-generalisation/pass2-review/human-review.csv \
    --prev-review "" \
    --threshold 0.15 --buffer 50
