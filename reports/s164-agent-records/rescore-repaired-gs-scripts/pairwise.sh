#!/usr/bin/env bash
# =============================================================================
# pairwise.sh — confirm today's main reproduces PR #37's NEW pairwise values
# =============================================================================
# Runs scripts/run_pairwise_tests.py (the 32 comparisons of
# configs/pairwise-comparisons.yaml, 10,000 permutations, seed 42) and
# apply_fdr_correction.py from the branch worktree (main plus the leg-rule
# routing, which touches no pairwise code) at one buffer, into
# pairwise/<name>-<buf>m/, with every config path made absolute onto the
# worktree. Then (name "probe" only) the arm probe of every committed
# run_pairwise_tests output #37 listed (leaderboards, factor analysis, e45),
# with #37's own probe script copied here (probe_sources.py).
# Writes its pid file and exit code.
#
# Usage: pairwise.sh <name> <buffer>   |   pairwise.sh probe
# =============================================================================
set -u
S=$HOME/scratch/s164-rescore-2026-10-13
WT=$HOME/scratch/s164-merges-2026-10-13/wt
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
mkdir -p "$S/pairwise" "$S/logs/pairwise"
cd "$S"
if [ "$1" = probe ]; then
  echo $$ > logs/pairwise/probe.pid
  "$PY" -I tools/probe_sources.py --tree "$WT" --root "$WT" \
    --files pairwise/rpt-output-files.txt \
    --bounds "$WT/inputs/vectors/bounds/384/full_evaluation_bounds.geojson" \
    --ref "$WT/inputs/vectors/references/mounds-reference.geojson" \
    > pairwise/sources-s164.json 2> logs/pairwise/probe.log
  echo $? > logs/pairwise/probe.rc
  exit 0
fi
name=$1; buf=$2; tag="$name-${buf}m"
echo $$ > "logs/pairwise/$tag.pid"
[ -f pairwise/abs-config.yaml ] || "$PY" -I tools/make_abs_config.py \
  "$WT/configs/pairwise-comparisons.yaml" "$WT" pairwise/abs-config.yaml
"$PY" -I "$WT/scripts/run_pairwise_tests.py" --config pairwise/abs-config.yaml \
  --buffer-metres "$buf" --n-permutations 10000 --seed 42 --quiet \
  --bounds "$WT/inputs/vectors/bounds/384/full_evaluation_bounds.geojson" \
  --ground-truth "$WT/inputs/vectors/references/mounds-reference.geojson" \
  --output-dir "pairwise/$tag" > "logs/pairwise/$tag.log" 2>&1
rc=$?
if [ $rc -eq 0 ]; then
  "$PY" -I "$WT/scripts/apply_fdr_correction.py" --results-dir "pairwise/$tag" \
    --output-dir "pairwise/$tag/fdr" > "logs/pairwise/$tag-fdr.log" 2>&1
  rc=$?
fi
echo $rc > "logs/pairwise/$tag.rc"
