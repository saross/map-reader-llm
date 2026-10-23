#!/bin/bash
# TRIAL, not the pass's runs: one leaderboard round-robin of
# run_pairwise_tests.py in leaderboard mode, then apply_fdr_correction.py.
# Reads the pass worktree (CWD = worktree root, because the condition
# registry's paths are relative to the working directory); writes only
# under the lane scratch. Python runs with -B so no bytecode is written
# into the worktree.
# Usage: run_lb.sh <tag> <buffer> <top_n> <metrics csv> <quiet: yes|no>
set -u
L=~/scratch/s164-restate-2026-10-15/lane-pairwise
WT=~/scratch/s164-restate-2026-10-15/wt
P=~/Code/map-reader-llm/.venv/bin/python
tag=$1; buf=$2; topn=$3; metrics=$4; quiet=$5
echo $$ > "$L/pids/$tag.pid"
q=""; [ "$quiet" = yes ] && q="--quiet"
cd "$WT"
$P -I -B "$WT/scripts/run_pairwise_tests.py" \
  --leaderboard configs/condition-registry.yaml --metrics "$metrics" \
  --top-n "$topn" --buffer-metres "$buf" --n-permutations 10000 --seed 42 $q \
  --output-dir "$L/trial/$tag" > "$L/logs/$tag.log" 2>&1
rc=$?
if [ $rc -eq 0 ]; then
  $P -I -B "$WT/scripts/apply_fdr_correction.py" \
    --results-dir "$L/trial/$tag" --output-dir "$L/trial/$tag/fdr" > "$L/logs/$tag-fdr.log" 2>&1
  rc=$?
fi
echo $rc > "$L/pids/$tag.rc"
