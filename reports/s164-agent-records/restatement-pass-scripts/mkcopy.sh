#!/usr/bin/env bash
# =============================================================================
# mkcopy.sh — one disposable, real-file copy of what the GS chain reads
# =============================================================================
# Part of the S164 restatement pass (reports/s164-agent-records/
# restatement-pass.md § 1.2). Code and data both come from REF of the pass's
# worktree (its branch head after the D65 (3) code and the dated constants).
# The gitignored prepared passes of the Gemini 3.7 image cell are copied, read
# only, from sapphire's shared checkout (the chain's row-for-row union gate
# checks them against the committed unions). The venv's interpreter is
# linked, not copied; nothing under scripts/ or tests/ is linked.
#
# Usage: mkcopy.sh <ref> <dest>
# =============================================================================
set -euo pipefail
REF=$1; DEST=$2
REPO=$HOME/scratch/s164-restate-2026-10-15/wt
SHARED=$HOME/Code/map-reader-llm
[ -e "$DEST" ] && { echo "refusing: $DEST exists" >&2; exit 2; }
mkdir -p "$DEST"
git -C "$REPO" archive "$REF" -- scripts config.py pyproject.toml pytest.ini \
  inputs/vectors inputs/grid-2026-08-18 inputs/stride-phaseb-2026-08-25 \
  inputs/image-b-gs-2026-08-28 \
  outputs/grid-2026-08-18 outputs/stride-phaseb-2026-08-25 outputs/stride-phasec-2026-08-25 \
  outputs/image-b-gs-2026-08-28 outputs/era1-pv-stage-d/384-consensus-text-high \
  outputs/gemini37-screen-2026-08-28 outputs/gemini37-image-gs-2026-09-01 \
  results/run-conditions.json \
  results/grid-2026-08-18 results/stride-2026-08-25 results/image-b-gs-2026-08-28 \
  results/verifier-robustness results/gemini37-screen-2026-08-28 \
  results/gemini37-image-gs-2026-09-01 results/gemini37-fourth-cell \
  results/gemini38-screen-2026-09-04 results/selection-aware \
  results/sensitivity-mde-2026-08-28 results/h8-v2/permutation-t4 \
  results/era1-leaderboard/tiering_20m.json \
  results/55map-final-board-2026-08-27/final_board_50m.json \
  results/55map-final-board-r2-2026-09-06/final_board_50m.json \
  | tar -x -C "$DEST"
d=outputs/gemini37-image-gs-2026-09-01/scoring
mkdir -p "$DEST/$d"; cp -a "$SHARED/$d/." "$DEST/$d/"
mkdir -p "$DEST/.venv/bin"
ln -sf "$SHARED/.venv/bin/python" "$DEST/.venv/bin/python"
printf 'ref %s\n' "$(git -C "$REPO" rev-parse "$REF")" > "$DEST/.source-commit"
