#!/usr/bin/env bash
# Run the per_map_counts spy over each consumer in the spy worktree, then the
# cheap measurements in the full clone (read-only use). One process at a time.
#
# Usage: spy_chain.sh <scratch-root>
set -u
S="$1"
logs="$S/logs/spy"
mkdir -p "$logs" "$S/spy-out"
echo $$ > "$logs/chain.pid"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
py=/home/shawn/Code/map-reader-llm/.venv/bin/python
status="$logs/status"
: > "$status"

step() {
    local name="$1"; shift
    local t0; t0=$(date -u +%FT%TZ)
    "$py" "$@" > "$logs/$name.log" 2>&1 < /dev/null
    echo "$name rc=$? start=$t0 end=$(date -u +%FT%TZ)" >> "$status"
}

cd "$S/spy" || exit 90
export PYTHONPATH="$S/spy"
step board "$S/tools/spy_run.py" "$S/spy" gemini37_grid_board "$S/spy-out/board.json"
step ladder "$S/tools/spy_run.py" "$S/spy" stride55_ladder "$S/spy-out/ladder.json" \
    --reuse-oracles --output-dir "$S/spy-out/ladder-rebuild" \
    --pairs-output-dir "$S/spy-out/ladder-pairs"
step a5b5 "$S/tools/spy_run.py" "$S/spy" stride55_a5_vs_b5 "$S/spy-out/a5b5.json"
step sweep "$S/tools/spy_run.py" "$S/spy" stride55_sweep_oracle "$S/spy-out/sweep.json"
cd "$S/repo" || exit 91
export PYTHONPATH="$S/repo"
step misc "$S/tools/measure_misc.py" "$S/repo" "$S/spy-out/misc.json"
echo "CHAIN-END $(date -u +%FT%TZ)" >> "$status"
