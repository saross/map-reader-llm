#!/usr/bin/env bash
# =============================================================================
# extref_run.sh — regenerate the eight 55-map extended-reference cells (D67 (6))
# =============================================================================
# One independent run of the committed generators in a disposable sparse clone
# of the repository at the pass commit, so the engine records a real
# git_commit. The clone is made with `git clone --shared` (objects read through
# alternates; nothing is written into the source repository) and a no-cone
# sparse checkout of exactly the paths the three generators read.
#
#   1. scripts/score_55maps_extended_gt_canonical.py   (seven cells; --workers 1)
#   2. scripts/score_uplift_canonical_gt.py            (TM-n10-k5)
#   3. scripts/adapt_track2_evals_for_manifest.py      (eight evaluation.json)
#
# Usage: extref_run.sh <label A|B> <commit>
# Writes: $LANE/extref/<label>/repo (the clone), $LANE/logs/extref-<label>-*.log
# Lane-uplift, S164 restatement pass. Zero API.
# =============================================================================
set -uo pipefail
LABEL=$1; REF=$2
SRC=$HOME/Code/map-reader-llm           # read only: objects via alternates
LANE=$HOME/scratch/s164-restate-2026-10-15/lane-uplift
PY=$HOME/Code/map-reader-llm/.venv/bin/python
DEST=$LANE/extref/$LABEL/repo
LOG=$LANE/logs/extref-$LABEL
rm -rf "$LANE/extref/$LABEL"; mkdir -p "$LANE/extref/$LABEL"
git clone -q --shared --no-checkout "$SRC" "$DEST" || exit 3
cd "$DEST" || exit 4
git sparse-checkout init --no-cone
cat > .git/info/sparse-checkout <<'EOF'
/scripts/
/config.py
/pyproject.toml
/inputs/vectors/
/results/55maps-extended-gt-2026-06-07/
/results/deployment-oracle-2026-06-06/
/results/55map-leaderboard/
/outputs/55maps-text-high-generalisation/verified/
/outputs/55maps-text-high-t0.3-generalisation/verified/
/outputs/55maps-text-min-generalisation/verified/
/outputs/55maps-image-generalisation/verified/
EOF
git checkout -q --detach "$REF" || exit 5
echo "head $(git rev-parse HEAD)" > "$LOG-steps.log"
git status --porcelain > "$LOG-status-before.txt"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
t0=$(date +%s)
"$PY" -B -u scripts/score_55maps_extended_gt_canonical.py \
  --output-base results/55maps-extended-gt-2026-06-07 --workers 1 \
  > "$LOG-driver.log" 2>&1
echo "driver_rc $? seconds $(( $(date +%s) - t0 ))" >> "$LOG-steps.log"
t1=$(date +%s)
"$PY" -B -u scripts/score_uplift_canonical_gt.py > "$LOG-uplift-cell.log" 2>&1
echo "uplift_cell_rc $? seconds $(( $(date +%s) - t1 ))" >> "$LOG-steps.log"
t2=$(date +%s)
"$PY" -B -u scripts/adapt_track2_evals_for_manifest.py > "$LOG-adapter.log" 2>&1
echo "adapter_rc $? seconds $(( $(date +%s) - t2 ))" >> "$LOG-steps.log"
git status --porcelain --untracked-files=all > "$LOG-status-after.txt"
echo "DONE total_seconds $(( $(date +%s) - t0 ))" >> "$LOG-steps.log"
