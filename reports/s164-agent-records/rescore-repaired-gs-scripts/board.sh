#!/usr/bin/env bash
# =============================================================================
# board.sh — re-tier the GS Era-2 verified board on one chain copy's sets
# =============================================================================
# Builds a disposable board copy (branch code, the board directory, and every
# file the board's 153 members' evaluations read; tools/board_files.py),
# copies in the ten detection sets the chain copy regenerated (the members
# downstream of the wrong-sheet legs), each at its REGISTERED operating point
# (tools/regsets.py writes verified_reg_20m.geojson beside the analysis's
# argmax set), re-scores those ten members on the board frame with each
# one's committed evaluate_detections.py arguments, then
# runs the board's own instruments: era1_leaderboard_tiering.py --permute-mcc
# (round-robin tile-swap, 10,000 draws, seed 42, BH q = 0.05, greedy clique,
# 20 m) and selection_aware_intervals.py --board (Hsu MCB, F1 and tile MCC).
# Nothing in the chain copy or the repository is written.
#
# Usage: board.sh <chain_copy> <fixed|repaired> <name>
# =============================================================================
set -uo pipefail
CHAIN=$1; POLICY=$2; NAME=$3
S=$HOME/scratch/s164-rescore-2026-10-13
WT=$HOME/scratch/s164-merges-2026-10-13/wt
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 MAP_READER_VERIFY_DIRS=$POLICY
B=results/leaderboard/era2/gs-era2-verified-board-2026-09-10
C=$S/copies/board-$NAME; L=$S/logs/board-$NAME; O=$S/board/$NAME
mkdir -p "$L" "$O"; echo $$ > "$L/board.pid"; echo RUNNING > "$L/board.state"
fail() { echo "FAILED $1" > "$L/board.state"; echo "BOARD FAILED at $1"; exit 1; }
rm -rf "$C"; mkdir -p "$C"
"$PY" "$S/tools/board_files.py" "$WT" > "$L/files.txt" || fail files
git -C "$WT" archive HEAD -- scripts config.py pyproject.toml inputs/vectors "$B" \
  $(cat "$L/files.txt") | tar -x -C "$C" || fail archive
mkdir -p "$C/.venv/bin"; ln -sf "$HOME/Code/map-reader-llm/.venv/bin/python" "$C/.venv/bin/python"
"$PY" "$S/tools/board_files.py" "$WT" --moved > "$L/moved.tsv" || fail moved
cd "$C" || fail cd
while IFS=$'\t' read -r cid ev det; do
  # The member at its REGISTERED point (tools/regsets.py), where the chain's
  # analysis wrote one; the grid member's file is already at its point.
  reg="$(dirname "$CHAIN/$det")/verified_reg_20m.geojson"
  if [ -f "$reg" ]; then cp "$reg" "$C/$det" || fail "copy $reg"
  else cp "$CHAIN/$det" "$C/$det" || fail "copy $det"; fi
  "$PY" - "$ev" > "$L/args-$(basename "$(dirname "$ev")").txt" <<'PYEOF' || fail "args $ev"
import json, sys
a = json.load(open(sys.argv[1]))["_metadata"]["cli_args"]
out = ["--detections", *a["detections"], "--buffers", *map(str, a["buffers"]),
       "--ground-truth", a["ground_truth"], "--bounds", a["bounds"],
       "--bootstrap", str(a["bootstrap"]), "--seed", str(a["seed"]),
       "--output-dir", a["output_dir"]]
if a.get("label"):
    out += ["--label", a["label"]]
if a.get("mcc"):
    out.append("--mcc")
print("\n".join(out))
PYEOF
  mapfile -t ARGS < "$L/args-$(basename "$(dirname "$ev")").txt"
  "$PY" scripts/evaluate_detections.py "${ARGS[@]}" > "$L/eval-$(basename "$(dirname "$ev")").log" 2>&1 \
    || fail "eval $ev"
  echo "re-scored $cid"
done < "$L/moved.tsv"
"$PY" scripts/era1_leaderboard_tiering.py --analysis-id gs-era2-verified-board-2026-09-10 \
  --analyses "$B/tiering-input/run-analyses.json" --permute-mcc --output-dir "$O/tiering" \
  > "$L/tiering.log" 2>&1 || fail tiering
for m in f1 mcc; do
  "$PY" scripts/selection_aware_intervals.py --board gs-era2-verified-board-2026-09-10 \
    --analyses "$B/tiering-input/run-analyses.json" --metric $m --bootstrap 10000 \
    --m-frac 1.0 --out "$O/mcb" > "$L/mcb-$m.log" 2>&1 || fail "mcb $m"
done
mkdir -p "$O/cells"
while IFS=$'\t' read -r cid ev det; do
  mkdir -p "$O/cells/$(basename "$(dirname "$ev")")"; cp "$C/$ev" "$O/cells/$(basename "$(dirname "$ev")")/"
done < "$L/moved.tsv"
echo "=== $(date -u +%FT%TZ) BOARD DONE"; echo DONE > "$L/board.state"
