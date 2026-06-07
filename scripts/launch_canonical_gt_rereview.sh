#!/usr/bin/env bash
# Adjudicate the 14 canonical-GT conflicts (5 label + 9 ring). See the
# conflict context in results/.../canonical-gt/re-review/conflict-info.csv.
# Leave the "Re-verify yesterday's mounds" toggle OFF (every cluster is active).
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/streamlit run scripts/review_candidates.py -- \
    --crops-dir results/deployment-oracle-2026-06-06/canonical-gt/re-review/crops \
    --probabilities results/deployment-oracle-2026-06-06/canonical-gt/re-review/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --output results/deployment-oracle-2026-06-06/canonical-gt/re-review/human-review.csv \
    --prev-review "" \
    --threshold 0.15 --buffer 50
