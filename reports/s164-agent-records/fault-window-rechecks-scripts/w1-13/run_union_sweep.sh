#!/usr/bin/env bash
# Fault-window re-check W1-13 (S164, 2026-10-14): replay the union-provenance
# sweep that produced reports/stale-register-notes-2026-10-07-union-sweep-2026-10-08.json
# (committed in da86896c4) with the checker code of that commit
# (scripts/check_union_provenance.py v1.1.0, last changed 303fbd3d2), on the
# fixed machine. Read-only apart from --json-out; re-derived unions go to a
# temporary directory the checker removes. One worker (CPU budget).
set -u
TREE=~/scratch/s164-fw-recheck-2026-10-14/w1-13-da86896c4
OUT=~/scratch/s164-fw-recheck-2026-10-14/w1-13-out
mkdir -p "$OUT"
cd "$TREE" || exit 2
~/Code/map-reader-llm/.venv/bin/python scripts/check_union_provenance.py --all --workers 1 \
    --json-out "$OUT/union-sweep-replay-${RUN_TAG:-run1}.json"
echo "EXIT $?"
