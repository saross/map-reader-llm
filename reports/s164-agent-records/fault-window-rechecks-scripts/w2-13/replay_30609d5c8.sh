#!/usr/bin/env bash
# replay_30609d5c8.sh -- W2-13 fault-window re-check (Session 164, 2026-10-14).
# Replays the union-staleness retrospective committed in 30609d5c8: the
# `check_union_provenance.py --all` sweep over every union a registered
# condition reads, at 30609d5c8 (the checker is unchanged since 55ebfe6db, and
# merge_passes.py is the pre-75d7c8d4c merger the sweep used), in a detached
# replay worktree, ONE worker (the original used 16; results are sorted by
# union path before writing, so worker count cannot reorder them), with a
# FRESH scratch directory.  Zero API.
# Usage: replay_30609d5c8.sh <replay-tree> <out-dir>
set -uo pipefail
TREE="$1"; OUT="$2"
PY=~/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$TREE"
git checkout -q --force --detach 30609d5c8
echo "HEAD $(git rev-parse --short HEAD)"
rm -rf "$OUT"; mkdir -p "$OUT/scratch"
echo "== check_union_provenance --all $(date -u +%FT%TZ)"
$PY scripts/check_union_provenance.py --all --workers 1 \
  --scratch-dir "$OUT/scratch" \
  --json-out "$OUT/union-staleness-retrospective-2026-09-12.json"
echo "exit=$? (1 is expected: the sweep finds STALE unions)"
echo "== done $(date -u +%FT%TZ)"
git status --short | head
