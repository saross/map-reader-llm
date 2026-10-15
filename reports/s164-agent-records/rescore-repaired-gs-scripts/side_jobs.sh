#!/usr/bin/env bash
# =============================================================================
# side_jobs.sh — the S164 re-score's side checks that read no verifier leg
# =============================================================================
# Run A and run B (fresh processes, separate output directories) of:
#   a07   scripts/h6_registered_analyses.py in a small disposable copy of the
#         branch (today's code; D50 scorer) — A-07 under D50, report only;
#   h13   the H13 chain PR #41 re-scored (h13_aggregation_sweep, h13_k_sensitivity,
#         h13_tilesize_overlap_grid) from the branch worktree into scratch,
#         to confirm today's main reproduces #41's reported "after" values.
# At most two processes at a time. Writes a pid file and per-job .rc files.
#
# Usage: side_jobs.sh <a07|h13> <runA|runB>
# =============================================================================
set -u
S=$HOME/scratch/s164-rescore-2026-10-13
WT=$HOME/scratch/s164-merges-2026-10-13/wt
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
what=$1; run=$2
L=$S/logs/side; mkdir -p "$L"
echo $$ > "$L/$what-$run.pid"
if [ "$what" = a07 ]; then
  C=$S/copies/h6-$run
  rm -rf "$C"; mkdir -p "$C"
  git -C "$WT" archive HEAD -- scripts config.py pyproject.toml inputs/vectors \
    outputs/h11/n1-pro-rerun-384 outputs/h11/n1-outstanding-384 \
    outputs/h11/pv-diag-384/pro-high-image-n5 outputs/h11/pv-diag-384/pro-high-text-n5 \
    outputs/h11/pv-diag-384/pro-medium-image-baseline outputs/h11/pv-diag-384/pro-medium-text-baseline \
    results/passes-manifest.json results/conditions-manifest.json \
    results/verifier-robustness/pareto results/run-conditions.json \
    results/run-analyses.json results/h6-registered-analyses | tar -x -C "$C"
  ( cd "$C" && "$PY" scripts/h6_registered_analyses.py ) > "$L/a07-$run.log" 2>&1 < /dev/null
  echo $? > "$L/a07-$run.rc"
  exit 0
fi
O=$S/h13/$run; mkdir -p "$O"
cd "$WT" || exit 9
"$PY" scripts/h13_aggregation_sweep.py --scoring-dir "$WT/outputs/h13/scoring" \
  --output-dir "$O/tier0" > "$L/h13-tier0-$run.log" 2>&1 < /dev/null &
p1=$!
"$PY" scripts/h13_k_sensitivity.py --output-dir "$O/ksens" > "$L/h13-ksens-$run.log" 2>&1 < /dev/null
echo $? > "$L/h13-ksens-$run.rc"
"$PY" scripts/h13_tilesize_overlap_grid.py --output-dir "$O/tilesize" \
  > "$L/h13-tilesize-$run.log" 2>&1 < /dev/null
echo $? > "$L/h13-tilesize-$run.rc"
wait $p1; echo $? > "$L/h13-tier0-$run.rc"
