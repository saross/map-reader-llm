#!/bin/bash
# CANDIDATE run of the pairwise lane (S164 restatement pass, plan § 1.5) in
# one disposable copy (runs/<X>/repo, a clone of 91bcd7f96). Every generator
# runs from the copy's root and writes in place inside the copy, with the
# committed run's exact flags; the copy is later reduced to the L1 layout
# by make_candidate.py. Nothing outside runs/<X>/ and the lane logs is
# written. Python runs with -I -B.
# Usage: run_candidate.sh <A|B>
set -u
X=$1
L=~/scratch/s164-restate-2026-10-15/lane-pairwise
R=$L/runs/$X/repo
P=~/Code/map-reader-llm/.venv/bin/python
LOG=$L/logs/cand-$X
mkdir -p "$LOG"
echo $$ > "$L/pids/cand-$X.pid"
cd "$R" || exit 1
git show 71d81cd5e:results/paper-tables/metrics_master.csv > "$L/runs/$X/metrics_master@71d81cd5e.csv"
step() {
  name=$1; shift
  s=$(date +%s)
  echo "START $name $(date -u +%FT%TZ)" >> "$LOG/steps.txt"
  "$@" > "$LOG/$name.log" 2>&1
  rc=$?
  echo "END $name rc=$rc elapsed=$(( $(date +%s) - s ))s" >> "$LOG/steps.txt"
  return $rc
}
RPT="$P -I -B scripts/run_pairwise_tests.py --n-permutations 10000 --seed 42"
FDR="$P -I -B scripts/apply_fdr_correction.py"
H2J=results/e45-bootstrap-pairings/h2-rerun/group_1_architecture/pv-vs-consensus-flash-high-text-16-of-30-pv-vs-flash-high-text-26-of-30.json
step p20 $RPT --config configs/pairwise-comparisons.yaml --buffer-metres 20 --quiet --output-dir results/pairwise/20m &&
step p20-fdr $FDR --results-dir results/pairwise/20m --output-dir results/pairwise/20m/fdr &&
step p30 $RPT --config configs/pairwise-comparisons.yaml --buffer-metres 30 --quiet --output-dir results/pairwise/30m &&
step p30-fdr $FDR --results-dir results/pairwise/30m --output-dir results/pairwise/30m/fdr &&
step lb20 $RPT --leaderboard configs/condition-registry.yaml --metrics results/paper-tables/metrics_master.csv --top-n 26 --buffer-metres 20 --output-dir results/pairwise/leaderboard-20m &&
step lb20-fdr $FDR --results-dir results/pairwise/leaderboard-20m --output-dir results/pairwise/leaderboard-20m/fdr &&
step lb30 $RPT --leaderboard configs/condition-registry.yaml --metrics "$L/runs/$X/metrics_master@71d81cd5e.csv" --top-n 25 --buffer-metres 30 --quiet --output-dir results/pairwise/leaderboard-30m &&
step lb30-fdr $FDR --results-dir results/pairwise/leaderboard-30m --output-dir results/pairwise/leaderboard-30m/fdr &&
step factor $RPT --config configs/factor-analysis-comparisons.yaml --buffer-metres 20 --output-dir results/pairwise/factor-analysis-20m &&
step collect $P -I -B scripts/collect-factor-analysis.py &&
step h2rerun $RPT --config results/e45-bootstrap-pairings/h2-rerun/comparison.yaml --buffer-metres 20 --output-dir results/e45-bootstrap-pairings/h2-rerun &&
step h3tier $P -I -B scripts/consensus_vs_baseline_tiering.py --cells planning/diversity-dividend-cells-2026-06-06.json --kinds champion --output-dir results/diversity-dividend-384/tiering-champions &&
step e45 $P -I -B scripts/e45_bootstrap_pairings.py --h2-rerun-json $H2J
echo $? > "$L/pids/cand-$X.rc"
