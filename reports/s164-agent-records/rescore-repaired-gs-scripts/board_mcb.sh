#!/usr/bin/env bash
# =============================================================================
# board_mcb.sh — re-run the Era-2 board's MCB sets on a restored board copy
# =============================================================================
# The first ladder stage (ladders.sh before its fix) re-extracted committed
# files into the board copy after board.sh's tiering had loaded its cells but
# before its two MCB runs read them: one of them was the grid 384/50 member's
# detection set. This restores every moved member's set from the chain copy
# (at its registered point, as board.sh copies it), checks each member's
# board-frame evaluation is the one board.sh wrote, and re-runs
# selection_aware_intervals.py --board for F1 and tile MCC into board/<name>/mcb.
#
# Usage: board_mcb.sh <chain_copy> <fixed|repaired> <name>
# =============================================================================
set -uo pipefail
CHAIN=$1; POLICY=$2; NAME=$3
S=$HOME/scratch/s164-rescore-2026-10-13
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 MAP_READER_VERIFY_DIRS=$POLICY
B=results/leaderboard/era2/gs-era2-verified-board-2026-09-10
C=$S/copies/board-$NAME; L=$S/logs/board-$NAME; O=$S/board/$NAME
echo $$ > "$L/mcb.pid"; echo RUNNING > "$L/mcb.state"
fail() { echo "FAILED $1" > "$L/mcb.state"; echo "MCB FAILED at $1"; exit 1; }
cd "$C" || fail cd
while IFS=$'\t' read -r cid ev det; do
  reg="$(dirname "$CHAIN/$det")/verified_reg_20m.geojson"
  if [ -f "$reg" ]; then cp "$reg" "$C/$det" || fail "copy $reg"
  else cp "$CHAIN/$det" "$C/$det" || fail "copy $det"; fi
  cmp -s "$C/$ev" "$O/cells/$(basename "$(dirname "$ev")")/evaluation.json" || fail "eval drift $ev"
done < "$L/moved.tsv"
rm -rf "$O/mcb"
for m in f1 mcc; do
  "$PY" scripts/selection_aware_intervals.py --board gs-era2-verified-board-2026-09-10 \
    --analyses "$B/tiering-input/run-analyses.json" --metric $m --bootstrap 10000 \
    --m-frac 1.0 --out "$O/mcb" > "$L/mcb2-$m.log" 2>&1 || fail "mcb $m"
done
echo "=== $(date -u +%FT%TZ) MCB DONE"; echo DONE > "$L/mcb.state"
