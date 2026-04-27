#!/usr/bin/env bash
# Launch the 55-map text-MINIMAL human-review session (Streamlit UI).
#
# Scope: multi-buffer re-review on the text-track MINIMAL-thinking
# generalisation run's VLM-only candidates, drawn as concentric
# "bullseye" rings (50 / 75 / 100 / 125 / 150 m) around each candidate.
# This is a FRESH review — no prior text-MIN review exists, so
# `--prev-review ""` disables the image-track pre-population default
# built into `scripts/review_candidates.py`.
#
# Sibling of `launch_55maps_text_high_review.sh` (T=0.7 HIGH-thinking)
# and `launch_55maps_text_high_t0.3_review.sh` (T=0.3 HIGH-thinking).
# Schema is identical, so downstream
# `scripts/compute_corrected_f1_multi_buffer.py` consumes the output via
# a `--review-today` override.
#
# Output: results/55maps-text-min-generalisation/human-review-multi-buffer.csv
#
# Ground truth: inputs/vectors/references/student-mounds-55maps-reviewed.geojson
#   (deduped 55-map student GT; same source as the T=0.7 and T=0.3 reviews).
#
# Usage:
#   bash scripts/launch_55maps_text_min_review.sh
#
# Then open the Streamlit URL printed in the terminal (default
# http://localhost:8501). Progress is saved on every decision; closing
# the browser does not lose work, and re-running the script resumes
# from the last reviewed candidate.

set -euo pipefail

# Run from the repo root so relative paths resolve correctly.
cd "$(dirname "$0")/.."

mkdir -p results/55maps-text-min-generalisation

exec .venv/bin/streamlit run scripts/review_candidates.py -- \
    --crops-dir outputs/55maps-text-min-generalisation/crops \
    --probabilities outputs/55maps-text-min-generalisation/verified/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --output results/55maps-text-min-generalisation/human-review-multi-buffer.csv \
    --prev-review "" \
    --threshold 0.15 \
    --buffer 50
