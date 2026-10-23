#!/usr/bin/env bash
# =============================================================================
# mkcopy_board.sh — one disposable, real-file copy for the Era-2 board lane
# =============================================================================
# Part of the S164 restatement pass (reports/s164-agent-records/
# restatement-pass.md § 1.3). Code and data from REF of the pass's worktree:
# the code, the whole results/ tree (the board, every member's evaluation and
# the register), every non-results file the members' evaluations name
# (board_files.py), and the four GS campaigns' outputs the sweep-optimism runs
# read (unions, verifier legs and prepared passes). The gitignored prepared
# passes of the Gemini 3.7 image cell are copied, read only, from sapphire's
# shared checkout. The venv's interpreter is linked; nothing under scripts/
# or tests/ is linked.
#
# Usage: mkcopy_board.sh <ref> <dest>
# =============================================================================
set -euo pipefail
REF=$1; DEST=$2
REPO=$HOME/scratch/s164-restate-2026-10-15/wt
SHARED=$HOME/Code/map-reader-llm
PY=$SHARED/.venv/bin/python
TOOLS=$(cd "$(dirname "$0")" && pwd)
[ -e "$DEST" ] && { echo "refusing: $DEST exists" >&2; exit 2; }
mkdir -p "$DEST"
mapfile -t EXTRA < <("$PY" "$TOOLS/board_files.py" "$REPO" | grep -v '^results/' || true)
git -C "$REPO" archive "$REF" -- scripts config.py pyproject.toml pytest.ini \
  inputs/vectors results \
  outputs/grid-2026-08-18 outputs/gemini37-screen-2026-08-28 \
  outputs/gemini37-image-gs-2026-09-01 outputs/image-b-gs-2026-08-28 \
  "${EXTRA[@]}" | tar -x -C "$DEST"
d=outputs/gemini37-image-gs-2026-09-01/scoring
mkdir -p "$DEST/$d"; cp -a "$SHARED/$d/." "$DEST/$d/"
mkdir -p "$DEST/.venv/bin"
ln -sf "$SHARED/.venv/bin/python" "$DEST/.venv/bin/python"
printf 'ref %s\n' "$(git -C "$REPO" rev-parse "$REF")" > "$DEST/.source-commit"
