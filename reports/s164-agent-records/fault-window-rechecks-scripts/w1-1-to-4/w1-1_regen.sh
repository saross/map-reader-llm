#!/usr/bin/env bash
# W1-1 replay (fault-window re-check, Session 164). Re-runs the four D42
# producers behind results/grid-2026-08-18/{grid_analysis,verifier_analysis,
# incumbents_common_footprint}.json and results/stride-2026-08-25/
# stride_verifier_analysis.json (commit 5986316b5) in a detached replay tree
# at 7aef6d2ff, in place in THAT tree only. Adapted from
# reports/d42-implementation-2026-10-05-scripts/d42_regen.sh (group 1 steps
# grid, incumbents, stride, grid_verifier), with at most two processes at
# once. PYTHONHASHSEED is left unset, as in the original runner. The two
# carried-over blocks are spliced afterwards by w1-1_splice.py.
set -u
T=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-1-to-4-7aef6d2ff
O=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-1-to-4-out/w1-1${RUN_TAG:-}
S=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w1-1-to-4
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export PYTHONPATH=$S/netguard
cd "$T" || exit 1
[ "$(git rev-parse HEAD)" = 7aef6d2ffde8a287d55a18b1dbfc28eb2361b6da ] || { echo "wrong HEAD"; exit 1; }
mkdir -p "$O"; : > "$O/status.tsv"
step() {  # step <name> <command...>
    local name=$1; shift
    local t0=$(date +%s)
    "$@" > "$O/${name}.log" 2>&1 < /dev/null
    local rc=$?
    printf '%s\t%s\t%ss\n' "$name" "$rc" "$(( $(date +%s) - t0 ))" >> "$O/status.tsv"
}
step grid "$PY" scripts/grid_analysis.py --bootstrap 10000 &
step incumbents "$PY" scripts/grid_incumbent_rescore.py &
wait
# grid_verifier_analysis reads grid_analysis.json, so it runs after grid.
step grid_verifier "$PY" scripts/grid_verifier_analysis.py &
step stride "$PY" scripts/stride_verifier_analysis.py &
wait
echo ALL-DONE >> "$O/status.tsv"
