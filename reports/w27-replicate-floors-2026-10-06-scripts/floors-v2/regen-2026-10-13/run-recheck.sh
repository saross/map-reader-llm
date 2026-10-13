#!/usr/bin/env bash
# run-recheck.sh -- floors2_integrity_recheck.py for the 2026-10-13 regeneration:
# run 1's § 6 against run 2's § 6 (every file), and a seeded 10 % of run 1's
# § 6b rows recomputed from the raw passes in a new process with a THIRD,
# empty pass cache. Writes its pid file and rc; log in logs/1013-recheck/.
# Launch detached with all three descriptors redirected.
set -u
S=/home/shawn/scratch/d60-w27-fastscorer-2026-10-12
CLONE=$S/repo
PY=/home/shawn/Code/map-reader-llm/.venv/bin/python
F=$CLONE/reports/w27-replicate-floors-2026-10-06-scripts/floors-v2
O=$S/out/1013-recheck
L=$S/logs/1013-recheck
P=$S/pids/1013-recheck
WORKERS=${WORKERS:-12}
mkdir -p "$O" "$L" "$P"
echo $$ > "$P/chain.pid"
export REPO=$CLONE PYTHONPATH=$CLONE PYTHONPYCACHEPREFIX=$S/pyc-1013-recheck
export W27_CACHE=$S/w27-cache-1013-recheck
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$CLONE" || { echo 90 > "$P/RC_CHAIN"; exit 90; }
if [ -e "$W27_CACHE" ] && [ -n "$(ls -A "$W27_CACHE")" ]; then
  echo "cache $W27_CACHE is not empty; refusing" > "$L/recheck.log"
  echo 91 > "$P/RC_CHAIN"; exit 91
fi
{
  echo "START recheck $(date -u +%FT%TZ) head $(git rev-parse HEAD)" \
    "lib $(git hash-object scripts/lib_advanced_metrics.py)" \
    "dirty $(git status --porcelain --untracked-files=no | wc -l) cache $W27_CACHE" \
    "workers $WORKERS"
  $PY $F/floors2_integrity_recheck.py --workers "$WORKERS" \
    --cells-csv $S/out/1013-r1/out55/subset_cells_all.csv \
    --w27-first $S/out/1013-r1/w27 --w27-second $S/out/1013-r2/w27 --out "$O"
  rc=$?
  echo "EXIT recheck $rc $(date -u +%FT%TZ)"
  echo $rc > "$P/RC_CHAIN"
} >> "$L/recheck.log" 2>&1
