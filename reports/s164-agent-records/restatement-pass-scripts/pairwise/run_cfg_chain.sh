#!/bin/bash
# TRIAL, not the pass's runs: the 30 m leaderboard (pinned to the March
# metrics table), then the factor analysis and the e45 H2 re-run, in one
# sequential process. Reads the pass worktree; writes only under the lane
# scratch. Python runs with -B so no bytecode is written into the worktree.
set -u
L=~/scratch/s164-restate-2026-10-15/lane-pairwise
WT=~/scratch/s164-restate-2026-10-15/wt
P=~/Code/map-reader-llm/.venv/bin/python
echo $$ > "$L/pids/chain.pid"
bash "$L/bin/run_lb.sh" lb-30m 30 25 "$L/out/metrics_master@71d81cd5e.csv" yes
rc30=$(cat "$L/pids/lb-30m.rc")
cd "$WT"
$P -I -B "$WT/scripts/run_pairwise_tests.py" --config configs/factor-analysis-comparisons.yaml \
  --buffer-metres 20 --n-permutations 10000 --seed 42 \
  --output-dir "$L/trial/factor-20m" > "$L/logs/factor-20m.log" 2>&1
rcf=$?
$P -I -B "$WT/scripts/run_pairwise_tests.py" \
  --config results/e45-bootstrap-pairings/h2-rerun/comparison.yaml \
  --buffer-metres 20 --n-permutations 10000 --seed 42 \
  --output-dir "$L/trial/e45-h2-rerun" > "$L/logs/e45-h2-rerun.log" 2>&1
rce=$?
echo "lb30=$rc30 factor=$rcf e45rerun=$rce" > "$L/pids/chain.rc"
