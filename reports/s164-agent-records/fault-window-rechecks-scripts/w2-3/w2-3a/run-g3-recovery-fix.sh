#!/usr/bin/env bash
# W2-3a group 3: replay the 2026-09-13 recovery-fix measurement.
# Original (session transcript, agent-a41b647e2345bdb44, sapphire worktree
# ~/worktrees/map-reader-llm/claude-unions, harness copies in
# ~/scratch/recovery-drop-fix/ which are byte-identical to the harness
# committed at 63f4cac1c):
#   07:33:42Z rescore_recovery_fixed.py --only k5                     (with evaluation)
#   07:39:14Z rescore_recovery_fixed.py --no-evaluate --only k1-opmax
#             --only k1-carried --only k3-opmax                       (-> operating-points.json)
#   07:42:14Z/07:42:34Z f1_only.py x3                                 (-> f1-only/*.json)
#   -> 20c0a053f; then fix_op_points.py (-> 5166ddeda operating-points.json);
#   08:54:54Z claude-6a (at 3eeaf96f4): rescore --only k3-opmax, copied to
#             phase2/materialised/g37-text-k3-verified-opmax.geojson  (-> 987534c03)
# The rebuilt unions and *_recovery-fixed verifier stages were committed in
# e9d1db0d0 and f8e0eb600 minutes later; no script or input differs between
# f8e0eb600, 20c0a053f and 63f4cac1c, so the harness replays at 63f4cac1c.
# One process at a time; evaluate_detections.py runs with its default
# --workers 1.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
OUT=$ROOT/w2-3a-out/g3
source "$ROOT/env.sh"
export TMPDIR=$ROOT/w2-3a-out/tmp
mkdir -p "$OUT" "$TMPDIR"
H=results/k-ladder-2026-09-12/recovery-fix-2026-09-13/harness
R=results/k-ladder-2026-09-12/recovery-fix-2026-09-13

stage() { echo; echo "##### $* ($(date -u +%FT%TZ)) #####"; }
status() { echo "##### exit=$1 #####"; }

for c in 63f4cac1c 5166ddeda 987534c03; do
    t=$ROOT/w2-3a-$c
    if [ ! -d "$t" ]; then
        git -C "$HOME/Code/map-reader-llm" worktree add --detach "$t" "$c" 2>&1 | tail -1
    fi
done

T=$ROOT/w2-3a-63f4cac1c
cd "$T" || exit 1
git rev-parse HEAD

stage "1. k5 (tier E) with its evaluation"
$PY $H/rescore_recovery_fixed.py --repo "$T" --out-root "$OUT/rescore" --python "$PY" \
    --only k5 > "$OUT/rescore-k5.log" 2>&1
status $?
tail -3 "$OUT/rescore-k5.log"
cp -p "$OUT/rescore/operating-points.json" "$OUT/operating-points-k5-run.json"

stage "2. the three 3.7 cells, materialised only"
$PY $H/rescore_recovery_fixed.py --repo "$T" --out-root "$OUT/rescore" --python "$PY" \
    --no-evaluate --only k1-opmax --only k1-carried --only k3-opmax \
    > "$OUT/rescore-g37.log" 2>&1
status $?
tail -3 "$OUT/rescore-g37.log"

stage "3. F1 arm, before and after, for the three 3.7 cells"
P=results/k-ladder-2026-09-12/phase2/materialised
$PY $H/f1_only.py --repo "$T" --label g37-text-k1-verified-opmax \
    --set before=$P/g37-text-k1-verified-opmax.geojson \
    --set after="$OUT/rescore/k1-opmax.geojson" --out "$OUT/f1only-k1-opmax.json" \
    > "$OUT/f1only-k1-opmax.log" 2>&1
status $?
$PY $H/f1_only.py --repo . --label g37-text-k1-verified-carried-p0.10-k1 \
    --set before=$P/g37-text-k1-verified-carried-p0.10-k1.geojson \
    --set after="$OUT/rescore/k1-carried.geojson" --out "$OUT/f1only-k1-carried.json" \
    > "$OUT/f1only-k1-carried.log" 2>&1
status $?
$PY $H/f1_only.py --repo . --label g37-text-k3-verified-opmax \
    --set before=$P/g37-text-k3-verified-opmax.geojson \
    --set after="$OUT/rescore/k3-opmax.geojson" --out "$OUT/f1only-k3-opmax.json" \
    > "$OUT/f1only-k3-opmax.log" 2>&1
status $?
git status --porcelain > "$OUT/git-status-63f4cac1c.txt"

stage "4. fix_op_points.py at 5166ddeda, from the 20c0a053f file and from the regenerated one"
T2=$ROOT/w2-3a-5166ddeda
cd "$T2" || exit 1
git rev-parse HEAD
git show 20c0a053f:$R/operating-points.json > $R/operating-points.json
$PY $H/fix_op_points.py > "$OUT/fix-op-points-from-committed.log" 2>&1
status $?
cp -p $R/operating-points.json "$OUT/fixed-from-committed.json"
cp -p "$OUT/rescore/operating-points.json" $R/operating-points.json
$PY $H/fix_op_points.py > "$OUT/fix-op-points-from-regen.log" 2>&1
status $?
cp -p $R/operating-points.json "$OUT/fixed-from-regen.json"
git checkout -q -- $R/operating-points.json

stage "5. the K = 3 detection set at 987534c03 (3eeaf96f4's scripts)"
T3=$ROOT/w2-3a-987534c03
cd "$T3" || exit 1
git rev-parse HEAD
$PY $H/rescore_recovery_fixed.py --repo "$T3" --out-root "$OUT/rescore-987534c03" \
    --python "$PY" --no-evaluate --only k3-opmax > "$OUT/rescore-987534c03.log" 2>&1
status $?
git status --porcelain > "$OUT/git-status-987534c03.txt"

echo
echo "##### ALL STAGES ATTEMPTED ($(date -u +%FT%TZ)) #####"
