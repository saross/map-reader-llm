#!/usr/bin/env bash
# Run one lane of the per_map_counts consumers in one tree, sequentially.
#
# Usage: chain.sh <tree-dir> <lane: A|B> <log-dir>
#
# Lane A: stride55_sweep_oracle -> gemini37_sweep_oracle -> gemini37_grid_board
# Lane B: stride55_ladder (full sweep) -> stride55_ladder --reuse-oracles
#         (writes ladder_pairs.json) -> stride55_a5_vs_b5
#
# Every step runs whatever the previous step's exit code was; each exit code
# is appended to <log-dir>/<lane>.status, and the chain writes its own pid
# file first and a terminal line last, so a watcher can wait on a terminal
# state (pid gone or "CHAIN-END" present) rather than on a success string.
set -u
tree="$1"; lane="$2"; logs="$3"
mkdir -p "$logs"
echo $$ > "$logs/$lane.pid"
cd "$tree" || exit 90
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$tree"
py=/home/shawn/Code/map-reader-llm/.venv/bin/python
status="$logs/$lane.status"
: > "$status"

step() {
    local name="$1"; shift
    local t0; t0=$(date -u +%FT%TZ)
    "$py" "$@" > "$logs/$lane-$name.log" 2>&1 < /dev/null
    local rc=$?
    echo "$name rc=$rc start=$t0 end=$(date -u +%FT%TZ)" >> "$status"
}

if [ "$lane" = A ]; then
    step sweep scripts/stride55_sweep_oracle.py
    step g37sweep scripts/gemini37_sweep_oracle.py
    step g37board scripts/gemini37_grid_board.py
elif [ "$lane" = B ]; then
    step ladder scripts/stride55_ladder.py
    step pairs scripts/stride55_ladder.py --reuse-oracles \
        --output-dir results/k-ladder-2026-09-12/mcc-test/sign-swap/rebuild \
        --pairs-output-dir results/k-ladder-2026-09-12/mcc-test/sign-swap
    step a5b5 scripts/stride55_a5_vs_b5.py
fi
echo "CHAIN-END $(date -u +%FT%TZ)" >> "$status"
