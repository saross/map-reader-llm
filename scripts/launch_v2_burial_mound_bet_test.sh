#!/usr/bin/env bash
# Launch the v2 burial-mound bet-test re-review session (Streamlit UI).
#
# Scope: re-review of the 177 false-positive (FP) candidates that the
# v2 closed-list FP-classifier reclassified into a burial-mound category
# (burial-mound / settlement-mound / triangulation-point-on-burial-mound /
# benchmark-on-burial-mound) on the 2026-04-29 v2 run (commit ec21c8ef).
#
# Bet adjudication denominator: 1,675 (the not_mound corpus the user
# actually reviewed and the v2 classifier inspected). The 2 % review-error
# threshold equates to 34 ``real_mound_my_error`` verdicts (1,675 × 0.02
# rounded up) ≈ 19 % of the 177 reclassifications. See plan §7 for the
# full denominator rationale.
#
# Default crop view is the EXACT 150 m / 768 px window the v2 classifier
# saw (no rings) — the bet test is settled on "what could the model see?".
# A sidebar toggle exposes the 400 m ringed view for borderline calls.
#
# A blinded calibration sample (~20 v2-not_mound-agreed rows) is mixed in
# by default and excluded from the headline 177-row count. Toggle off via
# the sidebar if the reviewer wants to skip the noise-floor estimate.
#
# Output: results/55maps-fp-classification/v2-burial-mound-bet-test/
#         verdicts.csv
#   — columns: run, candidate_id, verdict, note, timestamp, is_calibration.
#   — resume key: (run, candidate_id) so the script is correct even on
#     extension to the full 1,119 FP set (where candidate_id alone is not
#     unique across runs).
#
# Usage:
#   bash scripts/launch_v2_burial_mound_bet_test.sh [extra streamlit args]
#
# Then open the Streamlit URL printed in the terminal (default
# http://localhost:8501) and begin reviewing. Progress is saved to the
# verdicts CSV on every decision; closing the browser does not lose work.
#
# To resume an interrupted session, re-run the same command — the app
# automatically picks up from the last reviewed candidate.
#
# References:
#   - Plan: archive/planning-completed-session-81-82/v2-burial-mound-bet-test-app-plan-2026-04-29.md
#           (commit 8d2f7f47)
#   - Bet motivation: docs/notes/reflections/working-notes.md (Obs 308,
#                     committed at 73b21b6b)
#   - App: scripts/v2_burial_mound_bet_test_app.py

set -euo pipefail

# Run from repo root so relative paths inside the app resolve correctly.
cd "$(dirname "$0")/.."

# Pre-create the output directory so the first verdict-write doesn't race
# on directory creation. The app will recreate this directory if missing,
# but pre-creating is the documented pre-launch checklist behaviour
# (plan §9 step 5).
mkdir -p results/55maps-fp-classification/v2-burial-mound-bet-test

# Pick the project venv's streamlit (matches review_candidates.py launchers
# in this repo). Falls back to system streamlit if the venv is absent —
# but warn so the operator knows they may be on the wrong toolchain.
if [[ -x .venv/bin/streamlit ]]; then
    STREAMLIT_BIN=".venv/bin/streamlit"
else
    echo "[warn] .venv/bin/streamlit not found; falling back to PATH" >&2
    STREAMLIT_BIN="streamlit"
fi

# --server.headless=false so the local browser auto-opens (default for a
# desktop dev workflow on amd-tower). Override with --server.headless true
# at the CLI if launching on a remote machine.
exec "${STREAMLIT_BIN}" run scripts/v2_burial_mound_bet_test_app.py \
    --server.headless false \
    --server.port 8501 \
    "$@"
