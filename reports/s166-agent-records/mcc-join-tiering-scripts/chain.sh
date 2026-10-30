#!/usr/bin/env bash
# =============================================================================
# chain.sh — the Era-2 board's MCC family and MCC MCB under three tile joins
# =============================================================================
# Part of the S166 MCC robustness job, part (b) (planning/paper-writeup-
# continuity.md, "Planned: one $0 MCC robustness job"; record:
# reports/s166-agent-records/mcc-join-tiering.md). $0: no model API call.
#
# In a whole-tree clone of the branch commit (mkclone.sh, every tracked file
# present; the board reads only tracked files), runs, in parallel and each
# single-threaded:
#   tier_id        era1_leaderboard_tiering.py --permute-mcc, DEFAULT join —
#                  the gate: must reproduce the committed tiering_20m.json
#   tier_primary   the same with --tile-join geometric-primary
#   tier_contains  the same with --tile-join geometric-contains
#   mcb_f1_id      selection_aware_intervals.py --board --metric f1 (gate)
#   mcb_mcc_id     the same, --metric mcc, DEFAULT join (gate)
#   mcb_mcc_primary, mcb_mcc_contains   --metric mcc under each geometric join
#   builder_id     builder_id_check.py: the join-aware MCB builder under `id`
#                  must give the default path's indicators exactly
# Commands mirror reports/s164-agent-records/restatement-pass-scripts/
# board_chain.sh (cwd = clone root, relative --analyses path, 10,000 draws,
# m-frac 1.0) so the default outputs can be compared byte for byte.
#
# Each job writes <name>.pid from inside itself and <name>.rc when it ends;
# the chain writes chain.pid and chain.state (RUNNING / DONE / FAILED <jobs>).
#
# Usage: chain.sh <clone_dir> <out_dir> <log_dir>
# =============================================================================
set -uo pipefail
CLONE=$1; OUT=$2; LOGDIR=$3
PY=$HOME/Code/map-reader-llm/.venv/bin/python
TOOLS=$(cd "$(dirname "$0")" && pwd)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
unset MAP_READER_VERIFY_DIRS
mkdir -p "$LOGDIR" "$OUT"
echo $$ > "$LOGDIR/chain.pid"; echo RUNNING > "$LOGDIR/chain.state"
cd "$CLONE" || { echo "FAILED cd" > "$LOGDIR/chain.state"; exit 9; }
B=results/leaderboard/era2/gs-era2-verified-board-2026-09-10
ID=gs-era2-verified-board-2026-09-10
A=$B/tiering-input/run-analyses.json

# job <name> <command...>: run one job in the background with its own pid
# and rc files and all three descriptors redirected.
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

job tier_id "$PY" scripts/era1_leaderboard_tiering.py --analysis-id $ID \
  --analyses $A --permute-mcc --output-dir "$OUT/tiering/id"
job tier_primary "$PY" scripts/era1_leaderboard_tiering.py --analysis-id $ID \
  --analyses $A --permute-mcc --tile-join geometric-primary \
  --output-dir "$OUT/tiering/geometric-primary"
job tier_contains "$PY" scripts/era1_leaderboard_tiering.py --analysis-id $ID \
  --analyses $A --permute-mcc --tile-join geometric-contains \
  --output-dir "$OUT/tiering/geometric-contains"
job mcb_f1_id "$PY" scripts/selection_aware_intervals.py --board $ID \
  --analyses $A --metric f1 --bootstrap 10000 --m-frac 1.0 --out "$OUT/mcb"
job mcb_mcc_id "$PY" scripts/selection_aware_intervals.py --board $ID \
  --analyses $A --metric mcc --bootstrap 10000 --m-frac 1.0 --out "$OUT/mcb"
job mcb_mcc_primary "$PY" scripts/selection_aware_intervals.py --board $ID \
  --analyses $A --metric mcc --tile-join geometric-primary --bootstrap 10000 \
  --m-frac 1.0 --out "$OUT/mcb"
job mcb_mcc_contains "$PY" scripts/selection_aware_intervals.py --board $ID \
  --analyses $A --metric mcc --tile-join geometric-contains --bootstrap 10000 \
  --m-frac 1.0 --out "$OUT/mcb"
job builder_id "$PY" "$TOOLS/builder_id_check.py" "$CLONE" "$ID" "$A" \
  "$OUT/builder-id-check.json"

wait
failed=""
for name in tier_id tier_primary tier_contains mcb_f1_id mcb_mcc_id \
            mcb_mcc_primary mcb_mcc_contains builder_id; do
  rc=$(cat "$LOGDIR/$name.rc" 2>/dev/null || echo missing)
  [ "$rc" = 0 ] || failed="$failed $name($rc)"
done
if [ -n "$failed" ]; then
  echo "FAILED$failed" > "$LOGDIR/chain.state"
else
  echo DONE > "$LOGDIR/chain.state"
fi
