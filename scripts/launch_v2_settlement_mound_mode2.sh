#!/usr/bin/env bash
# Launch the v2 settlement-mound Mode 2 confirmation re-inspection app.
#
# Scope: re-inspection of the 117 false-positive (FP) candidates that
# the v2 closed-list FP-classifier reclassified as ``settlement-mound``
# during the 2026-04-29 v2 run (commit ec21c8ef). The bet-test (Obs
# 312, commit c4585f60) confirmed that 0/177 of the burial-mound
# reclassifications were review errors — i.e. all 177 are
# ``v2_overclaim``. This app confirms or rejects **Mode 2** of the
# resulting failure-mode taxonomy:
#
#   *Mode 2 (provisional): the dominant confound for*
#   ``settlement-mound`` *calls is closed topographic contour lines*
#   *(orange-brown, like settlement-mound ovals, but lacking the*
#   *diagnostic hachures that distinguish a mound from a contour*
#   *ring).*
#
# Verdict scheme (keyboard 1-4):
#
#   1. closed_topo_line_no_hachures   — Mode 2 confirmed
#   2. closed_topo_line_with_hachures — different feature
#   3. other_orange_brown_feature     — note recommended
#   4. not_orange_brown               — different failure mode
#
# Crop view: the EXACT 150 m / 768 px window the v2 classifier saw
# (displayed at 300 px, mirroring CLASSIFIER_VIEW_PX in the bet-test
# app). The Mode 2 inspection adjudicates on the same visual evidence
# the model used.
#
# Output:
#   results/55maps-fp-classification/v2-burial-mound-bet-test/
#     settlement-mound-mode2-verdicts.csv
#   — columns: run, candidate_id, mode2_verdict, note, timestamp.
#   — resume key: (run, candidate_id) so the script is correct even
#     across runs where candidate_id alone is not unique.
#
# Usage:
#   bash scripts/launch_v2_settlement_mound_mode2.sh \
#        [extra streamlit args]
#
# Then open the Streamlit URL printed in the terminal (default
# http://localhost:8502 — port 8502 is chosen to avoid collision with
# the bet-test app on 8501 if both are running). Progress is saved on
# every decision; closing the browser does not lose work. Re-run the
# same command to resume.
#
# References:
#   - App: scripts/v2_settlement_mound_mode2_app.py
#   - Sibling app: scripts/v2_burial_mound_bet_test_app.py
#                  (commits 3107d476 / d318c50c / 9a99ac68 / eae884ed)
#   - Obs 312: docs/notes/reflections/working-notes.md
#              (commit c4585f60 — bet-test resolved 0/177)

set -euo pipefail

# Run from repo root so relative paths inside the app resolve correctly.
cd "$(dirname "$0")/.."

# Pre-create the output directory so the first verdict-write does not
# race on directory creation. Re-uses the bet-test directory so all
# post-hoc inspections of the v2 reclassifications co-locate.
mkdir -p results/55maps-fp-classification/v2-burial-mound-bet-test

# Pick the project venv's streamlit (matches the bet-test launcher's
# convention). Falls back to system streamlit if the venv is absent —
# but warn so the operator knows they may be on the wrong toolchain.
if [[ -x .venv/bin/streamlit ]]; then
    STREAMLIT_BIN=".venv/bin/streamlit"
else
    echo "[warn] .venv/bin/streamlit not found; falling back to PATH" >&2
    STREAMLIT_BIN="streamlit"
fi

# --server.headless=false so the local browser auto-opens (default
# for a desktop dev workflow on amd-tower). Override with
# --server.headless true at the CLI if launching on a remote machine.
# Port 8502 avoids collision with the bet-test app on 8501.
exec "${STREAMLIT_BIN}" run scripts/v2_settlement_mound_mode2_app.py \
    --server.headless false \
    --server.port 8502 \
    "$@"
