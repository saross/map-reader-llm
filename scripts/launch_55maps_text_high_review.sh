#!/usr/bin/env bash
# Launch the 55-map text-HIGH human-review session (Streamlit UI).
#
# Scope: multi-buffer re-review on the text-HIGH track's ~630 VLM-only
# candidates at the standard five tolerance rings (50 / 75 / 100 / 125 /
# 150 m). This is a FRESH review — no prior text-HIGH review exists, so
# `--prev-review ""` disables the image-track pre-population default
# built into `scripts/review_candidates.py`.
#
# Output: results/55maps-text-high-generalisation/human-review-multi-buffer.csv
#   — schema matches the image-track multi-buffer review CSV, so the
#     downstream `scripts/compute_corrected_f1_multi_buffer.py` can
#     consume it with a `--review-today` override.
#
# Ground truth: inputs/vectors/references/student-mounds-55maps-reviewed.geojson
#   — deduped student GT (commit 2026-04-19; already used by all 55-map
#     evaluations; re-dedup is NOT required for text-HIGH).
#
# Usage:
#   bash scripts/launch_55maps_text_high_review.sh
#
# Then open the Streamlit URL printed in the terminal (default
# http://localhost:8501) and begin reviewing. Progress is saved to the
# output CSV on every decision; closing the browser does not lose work.
#
# To resume an interrupted session, re-run the same command — the app
# automatically picks up from the last reviewed candidate.

set -euo pipefail

# Ensure we run from the repo root so relative paths resolve correctly.
cd "$(dirname "$0")/.."

mkdir -p results/55maps-text-high-generalisation

exec .venv/bin/streamlit run scripts/review_candidates.py -- \
    --crops-dir outputs/55maps-text-high-generalisation/crops \
    --probabilities outputs/55maps-text-high-generalisation/verified/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --output results/55maps-text-high-generalisation/human-review-multi-buffer.csv \
    --prev-review "" \
    --threshold 0.15 \
    --buffer 50
