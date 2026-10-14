#!/usr/bin/env bash
# run-w27.sh <run label> <stage> -- D62 (1) step 3: one stage of the W2.7
# regeneration in the W2.7 clone, writing to a scratch tree.
#   s6   w27_55map_subset_replicates.py (§ 6), with a fresh, empty pass cache
#   gate floors2_scorer_gate.py against this run's § 6 cells
#   s6b  floors2_55map.py (§ 6b) with this run's gate and --sims 200
# WORKERS workers (default four). The job writes its pid file and exit code; the log goes
# beside them. Launch with all three descriptors redirected.
set -u
R=$1; STAGE=$2
S=~/scratch/origin-gap-h13-copies-2026-10-13/w27
CLONE=~/scratch/d60-w27-fastscorer-2026-10-12/repo
PY=~/Code/map-reader-llm/.venv/bin/python
F=$CLONE/reports/w27-replicate-floors-2026-10-06-scripts
mkdir -p "$S/$R" "$S/pids" "$S/logs"
echo $$ > "$S/pids/$R-$STAGE.pid"
export REPO=$CLONE PYTHONPATH=$CLONE PYTHONPYCACHEPREFIX=$S/pyc-$R W27_CACHE=$S/cache-$R
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$CLONE" || exit 1
echo "START $R $STAGE $(date -u +%FT%TZ) head $(git rev-parse HEAD) lib $(git hash-object scripts/lib_advanced_metrics.py) dirty $(git status --porcelain --untracked-files=no | wc -l)"
case $STAGE in
  s6) $PY $F/w27_55map_subset_replicates.py --workers "${WORKERS:-4}" --out "$S/$R/w27" ;;
  gate) $PY $F/floors-v2/floors2_scorer_gate.py --workers "${WORKERS:-4}" \
          --w27-cells "$S/$R/w27/subset_cells.json" --out "$S/$R/gate" ;;
  s6b) $PY $F/floors-v2/floors2_55map.py --workers "${WORKERS:-4}" --sims 200 \
          --scorer-gate "$S/$R/gate" --out "$S/$R/out55" ;;
  *) echo "unknown stage $STAGE"; false ;;
esac
rc=$?
echo "EXIT $R $STAGE $rc $(date -u +%FT%TZ)"
echo $rc > "$S/pids/$R-$STAGE.rc"
