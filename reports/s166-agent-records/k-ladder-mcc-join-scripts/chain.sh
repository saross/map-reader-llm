#!/usr/bin/env bash
# =============================================================================
# chain.sh -- the K-ladder tile-MCC instruments under three tile joins
# =============================================================================
# Part of the S166 K-ladder tile-join job
# (reports/s166-agent-records/k-ladder-mcc-join.md). $0: no model API call.
#
# Runs in a whole-tree clone of the branch commit (every tracked file present;
# ladder_files.py checks the 235 inputs the 29 ladders name). Two waves, every
# job single-threaded, at most 12 at once:
#
#   wave A (12 jobs; for J in id, geometric-primary, geometric-contains)
#     p1_J  k_ladder_mcc_test.py, the 8 Phase 1 ladders (ladders.json)
#     p2_J  k_ladder_mcc_test.py, the 13 Phase 2 ladders (the compatibility
#           inventory the committed Phase 2 test read, 326181bcd)
#     te_J  era1_leaderboard_tiering.py on tier E as evaluated (the command
#           scripts/tier_e_ladder_tiering.py runs)
#     cl_J  k_ladder_mcc_test.py, the 7 D51-clipped ladders
#   wave B (8 jobs)
#     mcb_J, mcbc_J  k_ladder_mcb.py on the 22 ladders and the 7 clipped ones;
#                    id runs both metrics, a geometric join MCC only
#     consensus      consensus_joins.py: § 8.6's consensus-only side
#     mechanism      mechanism.py: the id-join FN-tile diagnostic, per rung
#
# The id jobs are the gate: run with no --tile-join flag (the committed
# commands), they must reproduce the committed artefacts (summarise.py).
#
# Each job writes <name>.pid from inside itself and <name>.rc when it ends;
# the chain writes chain.pid and chain.state (RUNNING A / RUNNING B / DONE /
# FAILED <jobs>).
#
# Usage: chain.sh <clone_dir> <log_dir>
# =============================================================================
set -uo pipefail
CLONE=$1; LOGDIR=$2
PY=$HOME/Code/map-reader-llm/.venv/bin/python
TOOLS=$(cd "$(dirname "$0")" && pwd)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg
unset MAP_READER_VERIFY_DIRS
mkdir -p "$LOGDIR"
echo $$ > "$LOGDIR/chain.pid"; echo "RUNNING A" > "$LOGDIR/chain.state"
cd "$CLONE" || { echo "FAILED cd" > "$LOGDIR/chain.state"; exit 9; }

K=results/k-ladder-2026-09-12
CLIP=$K/clipped-mcc-2026-10-30
R=$K/mcc-join-2026-10-30
OUT=$CLONE/$R
BB=inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson
COMPAT=$R/inputs/phase2-ladders-compat-326181bcd.json
JOINS="id geometric-primary geometric-contains"

# job <name> <command...>: one job in the background, its own pid and rc
# files, all three descriptors redirected.
job() {
  local name=$1; shift
  (
    echo "$BASHPID" > "$LOGDIR/$name.pid"
    echo "=== $(date -u +%FT%TZ) START $name"
    "$@"
    rc=$?
    echo "=== $(date -u +%FT%TZ) END $name rc=$rc"
    echo "$rc" > "$LOGDIR/$name.rc"
  ) > "$LOGDIR/$name.log" 2>&1 < /dev/null &
}

# joinflag <join>: nothing for the published join (the committed command),
# --tile-join <join> otherwise.
joinflag() { [ "$1" = id ] || printf -- '--tile-join\n%s\n' "$1"; }

# check <names...>: every named job ended with rc 0.
check() {
  local failed=""
  for name in "$@"; do
    rc=$(cat "$LOGDIR/$name.rc" 2>/dev/null || echo missing)
    [ "$rc" = 0 ] || failed="$failed $name($rc)"
  done
  printf '%s' "$failed"
}

# ---- wave A -----------------------------------------------------------------
A=""
for J in $JOINS; do
  mapfile -t F < <(joinflag "$J")
  job "p1_$J" "$PY" scripts/k_ladder_mcc_test.py "${F[@]}" \
    --output-dir "$OUT/$J/mcc-test"
  job "p2_$J" "$PY" scripts/k_ladder_mcc_test.py "${F[@]}" \
    --ladders "$COMPAT" --bounds "$BB" --output-dir "$OUT/$J/phase2-mcc-test"
  job "te_$J" "$PY" scripts/era1_leaderboard_tiering.py \
    --analysis-id k-ladder-tier-e-2026-09-12 \
    --conditions $K/tier-e/tiering-input/run-conditions.json \
    --analyses $K/tier-e/tiering-input/run-analyses.json \
    --bounds "$BB" --output-dir "$OUT/$J/tier-e" --buffer 20 \
    --n-permutations 10000 --seed 42 --permute-mcc "${F[@]}"
  job "cl_$J" "$PY" scripts/k_ladder_mcc_test.py "${F[@]}" \
    --ladders $CLIP/ladders-clipped.json \
    --conditions $CLIP/tiering-input/run-conditions.json \
    --bounds "$BB" --output-dir "$OUT/$J/clipped-mcc-test"
  A="$A p1_$J p2_$J te_$J cl_$J"
done
wait
# shellcheck disable=SC2086
failed=$(check $A)
if [ -n "$failed" ]; then echo "FAILED A:$failed" > "$LOGDIR/chain.state"; exit 1; fi

# ---- wave B -----------------------------------------------------------------
echo "RUNNING B" > "$LOGDIR/chain.state"
"$PY" "$TOOLS/make_registries.py" "$CLONE" "$COMPAT" "$R" "$OUT/registries" \
  > "$LOGDIR/registries.log" 2>&1 < /dev/null \
  || { echo "FAILED registries" > "$LOGDIR/chain.state"; exit 1; }
job mcb_id "$PY" scripts/k_ladder_mcb.py --registry "$OUT/registries/id-registry.json" \
  --output-dir "$OUT/id/mcb"
job mcbc_id "$PY" scripts/k_ladder_mcb.py --registry $CLIP/mcb-registry.json \
  --output-dir "$OUT/id/clipped-mcb"
B="mcb_id mcbc_id"
for J in geometric-primary geometric-contains; do
  job "mcb_$J" "$PY" scripts/k_ladder_mcb.py --tile-join "$J" --metrics mcc \
    --registry "$OUT/registries/$J-registry.json" --output-dir "$OUT/$J/mcb"
  job "mcbc_$J" "$PY" scripts/k_ladder_mcb.py --tile-join "$J" --metrics mcc \
    --registry "$OUT/registries/$J-clipped-registry.json" \
    --output-dir "$OUT/$J/clipped-mcb"
  B="$B mcb_$J mcbc_$J"
done
job consensus "$PY" "$TOOLS/consensus_joins.py" "$CLONE" \
  "$OUT/consensus/grid-overlap-joins.json"
job mechanism "$PY" "$TOOLS/mechanism.py" "$CLONE" "$COMPAT" \
  "$OUT/mechanism/id-join-mechanism.json"
wait
# shellcheck disable=SC2086
failed=$(check $B consensus mechanism)
if [ -n "$failed" ]; then echo "FAILED B:$failed" > "$LOGDIR/chain.state"; exit 1; fi
echo DONE > "$LOGDIR/chain.state"
