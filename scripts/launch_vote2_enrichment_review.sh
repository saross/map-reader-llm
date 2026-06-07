#!/usr/bin/env bash
# Review the cross-config-corroborated (>=3 of 4) vote=2 GT-enrichment
# candidates. All NEW (no re-checks). Leave the toggle OFF; label each
# mound/not_mound + ring. Context: results/.../vote2-enrichment/candidate-info.csv
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/streamlit run scripts/review_candidates.py -- \
    --crops-dir results/deployment-oracle-2026-06-06/vote2-enrichment/crops \
    --probabilities results/deployment-oracle-2026-06-06/vote2-enrichment/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --output results/deployment-oracle-2026-06-06/vote2-enrichment/human-review.csv \
    --prev-review "" \
    --threshold 0.15 --buffer 50
