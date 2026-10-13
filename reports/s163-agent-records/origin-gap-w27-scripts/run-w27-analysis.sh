#!/usr/bin/env bash
# run-w27-analysis.sh <run label> -- the floors-v2 analysis chain on this
# run's § 6b cells (mirrors PR #38's tools/run_analysis.sh; one process).
# The gold-standard slice cells (outgs) are PR #38's, copied read-only:
# floors2_gs.py does not call cluster_subset and its clustering
# (cluster_votes_fast) is unchanged on this branch. § 6's subset_pairs.csv
# is read from the clone, where it is byte-identical to this run's § 6.
set -u
R=$1
S=~/scratch/origin-gap-h13-copies-2026-10-13/w27
CLONE=~/scratch/d60-w27-fastscorer-2026-10-12/repo
F=$CLONE/reports/w27-replicate-floors-2026-10-06-scripts/floors-v2
PY=~/Code/map-reader-llm/.venv/bin/python
echo $$ > "$S/pids/$R-analysis.pid"
export REPO=$CLONE PYTHONPATH=$CLONE PYTHONPYCACHEPREFIX=$S/pyc-$R
cd "$CLONE" || exit 1
RES=$S/$R/results; mkdir -p "$RES"
echo "START $R analysis $(date -u +%FT%TZ) head $(git rev-parse HEAD)"
$PY $F/floors2_analyse.py --out55 "$S/$R/out55" --outgs "$S/outgs-pr38" --res "$RES" \
  || { echo 1 > "$S/pids/$R-analysis.rc"; exit 1; }
cp -a $F/results/gs_validation_summary.csv $F/results/gs_k10_summary.csv "$RES/"
$PY $F/floors2_rescreen.py "$RES" > "$S/$R/rescreen.out" || { echo 2 > "$S/pids/$R-analysis.rc"; exit 1; }
$PY $F/floors2_tables.py "$RES" > "$RES/tables.md" || { echo 3 > "$S/pids/$R-analysis.rc"; exit 1; }
echo 0 > "$S/pids/$R-analysis.rc"
echo "EXIT $R analysis 0 $(date -u +%FT%TZ)"
