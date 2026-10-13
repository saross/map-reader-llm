#!/usr/bin/env bash
# run-rows.sh <label> <cache dir> <probe json> -- one run of rows_w27_reattributed.py.
B=~/scratch/origin-gap-h13-copies-2026-10-13
C=~/scratch/d60-w27-fastscorer-2026-10-12/repo
echo $$ > $B/w27/pids/rows-$1.pid
cd $C || exit 1
export REPO=$C PYTHONPATH=$C PYTHONPYCACHEPREFIX=$B/w27/pyc-rows-$1 W27_CACHE=$2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "START $1 $(date -u +%FT%TZ) head $(git rev-parse HEAD)"
~/Code/map-reader-llm/.venv/bin/python $B/bin/rows_w27_reattributed.py --probe "$3" --out $B/w27/rows-$1.json
echo $? > $B/w27/pids/rows-$1.rc
echo "EXIT $1 $(date -u +%FT%TZ)"
