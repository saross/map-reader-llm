#!/usr/bin/env bash
# The per-tile check at the merged head, twice (clone code and an archive of the head).
B=~/scratch/origin-gap-h13-copies-2026-10-13
PY=~/Code/map-reader-llm/.venv/bin/python
C=~/scratch/d60-1-input-vintage-2026-10-12/repo
echo $$ > $B/pids/pertile-merged.pid
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
$PY $B/bin/pertile_diversity.py --code $C --data $C --summary $B/diffs/copies-summary.json --out $B/copies/pertile-new3.json > $B/logs/pertile-new3.log 2>&1 < /dev/null &
$PY $B/bin/pertile_diversity.py --code $B/trees/new4 --data $C --summary $B/diffs/copies-summary.json --out $B/copies/pertile-new4.json > $B/logs/pertile-new4.log 2>&1 < /dev/null &
wait
date -u +%FT%TZ > $B/pids/pertile-merged.done
