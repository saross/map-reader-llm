#!/usr/bin/env bash
# Launch the precise-location (point-marking) app — step 1 of ruling 20(d),
# the gate for every reference-tainted re-analysis under ruling 21.
#
# Scope: ruling 21c set this at the 773 promoted phantoms. The PI widened it
# on 2026-08-05 to sweep up every possible conflation in the same pass, at a
# 50 m cut. The queue is 906 items — 773 phantoms plus 133 corrected-student
# points that conflate with a phantom, sit near another student point, or are
# one of the 26 merged centroids / 2 curator additions separating layer 2
# from layer 1.
#
# The queue is rebuilt here on every launch: it is derived entirely from
# committed inputs, takes under a second, and rebuilding removes any chance
# of reviewing a stale queue.
#
# Imagery note: the 55-map deployment corpus lives in
# inputs/rasters/Russian1981_32635/ (55 sheets, covering 55/55 of the
# phantom map_names). The four sheets directly under inputs/rasters/ are the
# 4-map GS corpus, which ruling 21 puts OUT of scope and which covers 0/55
# of these phantoms.
#
# Output goes to a NEW file; no source layer is ever mutated. Marks are saved
# after every decision, so re-running resumes at the first unmarked item.
set -euo pipefail
cd "$(dirname "$0")/.."

GT_DIR="results/deployment-oracle-2026-06-06/canonical-gt"

.venv/bin/python scripts/build_marking_queue.py \
    --extra-items "${GT_DIR}/extra-review-items.csv" \
    --output "${GT_DIR}/marking-queue.csv"

exec .venv/bin/streamlit run scripts/mark_mound_centres.py -- \
    --queue-csv "${GT_DIR}/marking-queue.csv" \
    --superseded-csv "${GT_DIR}/superseded-marking-queue.csv" \
    --phantom-csv "${GT_DIR}/canonical-review.csv" \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --student-gt \
        inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --output "${GT_DIR}/marked-centres.csv" \
    --marked-by "Shawn Ross"
