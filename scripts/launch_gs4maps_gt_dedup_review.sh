#!/usr/bin/env bash
# Launch the GS-4-maps student-GT duplicate-review Streamlit app.
#
# Approach A: reuses scripts/review_gt_duplicates.py without code edits.
# All path overrides are passed as CLI flags; the script's existing
# argparse interface accepts them as-is.
#
# Workflow:
#
#   1. (One-off, run before this script the first time)
#      .venv/bin/python scripts/build_student_mounds_gs4.py
#      — produces inputs/vectors/references/student-mounds-gs-4maps.geojson
#        (the pre-review input consumed below) and the reusable bounds
#        artefact at inputs/vectors/bounds/gs-4maps-sheet-bounds.geojson.
#
#   2. Launch the Streamlit reviewer (this script). Decisions persist
#      to results/gt-duplicate-review-gs4/gt-duplicate-decisions.csv;
#      closing the browser does not lose work.
#
#   3. Re-run with --apply (see APPLY_CMD below) to materialise
#      inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson
#      from the saved decisions.
#
# Output of step 2 (interactive review):
#   results/gt-duplicate-review-gs4/gt-duplicate-decisions.csv
#
# Output of step 3 (post-review apply):
#   inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson
#   results/gt-duplicate-review-gs4/gt-duplicate-diff.md
#
# The four GS rasters live directly under inputs/rasters/ (filenames:
# K-35-052-4_32635.tif, K-35-053-3_Elenovo.tif, K-35-062-2_Rakovski.tif,
# K-35-078-1_Lesovo.tif). The build script stores the raster filename
# stem as source_map so the reviewer's _resolve_raster glob
# ({map_id}.tif under --rasters-dir) matches without further code
# changes.
#
# Usage:
#   bash scripts/launch_gs4maps_gt_dedup_review.sh                # default 50 m
#   bash scripts/launch_gs4maps_gt_dedup_review.sh 100            # widen to 100 m
#
# Per the multi-threshold workflow documented in
# scripts/review_gt_duplicates.py, decisions persist across threshold
# changes, so re-launching at a wider threshold respects existing
# merge decisions and only surfaces additional candidates.
#
# To apply decisions after review is complete:
#   .venv/bin/python scripts/review_gt_duplicates.py --apply \
#       --ground-truth inputs/vectors/references/student-mounds-gs-4maps.geojson \
#       --decisions results/gt-duplicate-review-gs4/gt-duplicate-decisions.csv \
#       --clean-output inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson \
#       --diff-output results/gt-duplicate-review-gs4/gt-duplicate-diff.md

set -euo pipefail

# Run from the repo root so relative paths resolve correctly.
cd "$(dirname "$0")/.."

mkdir -p results/gt-duplicate-review-gs4

# First positional arg overrides the cluster threshold (metres). Default
# 50 m matches the canonical 55-map review pass; 100 m is the wider
# safety-net pass.
THRESHOLD_M="${1:-50}"

exec .venv/bin/streamlit run scripts/review_gt_duplicates.py -- \
    --ground-truth inputs/vectors/references/student-mounds-gs-4maps.geojson \
    --rasters-dir inputs/rasters \
    --threshold-m "${THRESHOLD_M}" \
    --output results/gt-duplicate-review-gs4/gt-duplicate-decisions.csv \
    --clean-output inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson \
    --diff-output results/gt-duplicate-review-gs4/gt-duplicate-diff.md
