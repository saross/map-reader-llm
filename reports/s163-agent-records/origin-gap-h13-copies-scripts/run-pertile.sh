#!/usr/bin/env bash
# Two independent runs of pertile_diversity.py (new1 = clone code, new2 = archive of the head).
B=~/scratch/origin-gap-h13-copies-2026-10-13
PY=~/Code/map-reader-llm/.venv/bin/python
C=~/scratch/d60-1-input-vintage-2026-10-12/repo
echo $$ > $B/pids/pertile.pid
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
$PY $B/bin/pertile_diversity.py --code $C --data $C --summary $B/diffs/copies-summary.json --out $B/copies/pertile-new1.json > $B/logs/pertile-new1.log 2>&1 < /dev/null; echo $? > $B/pids/pertile-new1.rc
$PY $B/bin/pertile_diversity.py --code $B/trees/code-new2 --data $C --summary $B/diffs/copies-summary.json --out $B/copies/pertile-new2.json > $B/logs/pertile-new2.log 2>&1 < /dev/null; echo $? > $B/pids/pertile-new2.rc
