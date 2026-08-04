#!/usr/bin/env bash
# Launch the precise-location (point-marking) app for the 773 promoted
# phantoms — step 1 of ruling 20(d), the gate for every reference-tainted
# re-analysis under ruling 21.
#
# Scope is the 773 phantoms only (ruling 21c); the 4,746 student mounds
# are NOT re-marked. Budget is roughly one hour of PI review.
#
# Imagery note: the 55-map deployment corpus lives in
# inputs/rasters/Russian1981_32635/ (55 sheets, covering 55/55 of the
# phantom map_names). The four sheets directly under inputs/rasters/ are
# the 4-map GS corpus, which ruling 21 puts OUT of scope and which covers
# 0/55 of these phantoms.
#
# Output goes to a NEW file; canonical-review.csv is never mutated.
# Marks are saved after every decision, so re-running this script resumes
# at the first unmarked row.
set -euo pipefail
cd "$(dirname "$0")/.."

exec .venv/bin/streamlit run scripts/mark_mound_centres.py -- \
    --review-csv \
        results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --student-gt \
        inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --output \
        results/deployment-oracle-2026-06-06/canonical-gt/marked-centres.csv \
    --marked-by "Shawn Ross"
