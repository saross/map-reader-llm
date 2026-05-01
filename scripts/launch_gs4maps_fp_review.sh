#!/usr/bin/env bash
# Launch the GS-4-maps student-vs-curator GT false-positive Streamlit reviewer.
#
# Approach A: a sibling script to ``scripts/review_gt_duplicates.py`` (the
# dedup reviewer) that imports its raster-rendering helpers but
# implements its own one-FP-per-page UI. See the docstring at the top
# of ``scripts/review_student_fp_candidates.py`` for the rationale.
#
# Workflow:
#
#   1. Pre-flight: build the FP-candidate CSV. The Streamlit app will
#      auto-build it if missing, but doing it here surfaces the
#      Hungarian-artefact diagnostic count to stdout immediately.
#
#   2. Launch the Streamlit reviewer (this script). Decisions persist
#      to ``results/student-gt-fp-review-gs4/fp-decisions.csv`` after
#      every click; closing the browser does not lose work, and a
#      relaunch reloads existing decisions.
#
# Outputs (post-build):
#
#   results/student-gt-fp-review-gs4/fp-candidates.csv  (17 rows)
#
# Outputs (during/after review):
#
#   results/student-gt-fp-review-gs4/fp-decisions.csv
#
# There is no apply step — the decisions CSV is the final artefact. A
# summary tally per category can be produced later via:
#
#   .venv/bin/python -c \
#     "import pandas as pd; print(pd.read_csv(
#         'results/student-gt-fp-review-gs4/fp-decisions.csv'
#     )['decision'].value_counts())"
#
# Usage:
#   bash scripts/launch_gs4maps_fp_review.sh           # build + launch
#   bash scripts/launch_gs4maps_fp_review.sh --rebuild # force CSV rebuild

set -euo pipefail

# Run from the repo root so relative paths resolve correctly.
cd "$(dirname "$0")/.."

mkdir -p results/student-gt-fp-review-gs4

REBUILD_FLAG=""
if [[ "${1:-}" == "--rebuild" ]]; then
    REBUILD_FLAG="--rebuild"
fi

echo "Pre-flight: building FP-candidate CSV…"
.venv/bin/python scripts/review_student_fp_candidates.py --build-only

echo
echo "Launching Streamlit reviewer…"
exec .venv/bin/streamlit run scripts/review_student_fp_candidates.py -- \
    ${REBUILD_FLAG}
