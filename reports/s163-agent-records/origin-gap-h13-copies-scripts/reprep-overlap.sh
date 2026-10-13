#!/usr/bin/env bash
# reprep-overlap.sh <label> <tree> -- rewrite the H13 prepared sets on the
# tree's code (reprep.py), then run the tree's overlap analysis on them.
set -eu
BASE=~/scratch/origin-gap-h13-copies-2026-10-13
PY=~/Code/map-reader-llm/.venv/bin/python
label=$1; tree=$2; out=$BASE/out/$label
cd "$tree"
$PY "$BASE/bin/reprep.py" --repo "$tree" --out "$out/reprep-scoring"
$PY scripts/h13_overlap_analysis.py --scoring-dir "$out/reprep-scoring" \
    --output-dir "$out/overlap-reprep"
