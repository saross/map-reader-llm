#!/usr/bin/env bash
# Pass-2 auto-fill spot-check for 55maps-text-min-generalisation. Inherited mound labels are
# pre-populated (enable the "confirmed mounds" sidebar toggle to walk them);
# inherited not_mound + any overrides flow through the normal FP queue.
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/streamlit run scripts/review_candidates.py -- \
    --crops-dir results/deployment-oracle-2026-06-06/k3-review/55maps-text-min-generalisation/pass2-review/crops \
    --probabilities results/deployment-oracle-2026-06-06/k3-review/55maps-text-min-generalisation/pass2-review/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --output results/deployment-oracle-2026-06-06/k3-review/55maps-text-min-generalisation/pass2-review/human-review.csv \
    --prev-review results/deployment-oracle-2026-06-06/k3-review/55maps-text-min-generalisation/pass2-review/prevreview-mounds.csv \
    --threshold 0.15 --buffer 50
