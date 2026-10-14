#!/usr/bin/env bash
# =============================================================================
# ladders.sh — re-test the two gold-standard K ladders in a board copy
# =============================================================================
# After board.sh has re-scored the Era-2 board's moved members in board copy
# <name>: adds the K-ladder review's two gold-standard ladders' inputs
# (tools/ladder_files.py), copies in the chain copy's regenerated stride A
# rung sets, re-scores the four stride A rungs on the board frame with their
# committed arguments, then runs the review's own instruments on both ladders:
# era1_leaderboard_tiering.py --permute-mcc (the findings' § 6 command) and
# k_ladder_mcb.py --only gs-stride-a --only tier-e.
#
# Usage: ladders.sh <chain_copy> <fixed|repaired> <name>
# =============================================================================
set -uo pipefail
CHAIN=$1; POLICY=$2; NAME=$3
S=$HOME/scratch/s164-rescore-2026-10-13
WT=$HOME/scratch/s164-merges-2026-10-13/wt
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 MAP_READER_VERIFY_DIRS=$POLICY
K=results/k-ladder-2026-09-12
C=$S/copies/board-$NAME; L=$S/logs/board-$NAME; O=$S/board/$NAME
echo $$ > "$L/ladders.pid"; echo RUNNING > "$L/ladders.state"
fail() { echo "FAILED $1" > "$L/ladders.state"; echo "LADDERS FAILED at $1"; exit 1; }
{ "$PY" "$S/tools/ladder_files.py" "$WT" $K/tiering-input/gs-stride-a/run-analyses.json \
    $K/tiering-input/gs-stride-a/run-conditions.json k-ladder-gs-stride-a-2026-09-12
  "$PY" "$S/tools/ladder_files.py" "$WT" $K/tier-e/tiering-input/run-analyses.json \
    $K/tier-e/tiering-input/run-conditions.json k-ladder-tier-e-2026-09-12; } \
  | sort -u > "$L/ladder-files.txt" || fail files
# k_ladder_mcb.py also reads the three ladder inventories (label -> K).
git -C "$WT" archive HEAD -- $K/mcc-test/tiering/gs-stride-a $K/tier-e/tiering $K/mcb/gs-stride-a \
  $K/mcb/tier-e $K/ladders.json $K/phase2/ladders-compat.json $K/tier-e/ladder.json \
  $(cat "$L/ladder-files.txt") | tar -x -C "$C" || fail archive
cd "$C" || fail cd
# The archive above also re-extracted the grid 384/50 member's committed set
# (tier E's K = 10 rung reads the same file): put the chain copy's set back.
cp "$CHAIN/results/grid-2026-08-18/conditions-verified/g384_ov192/detections.geojson" \
   "results/grid-2026-08-18/conditions-verified/g384_ov192/detections.geojson" || fail "copy grid"
# The stride A rungs' sets, as the chain copy regenerated them.
for cell in g384_ov128 g384_ov128-ladder-n1 g384_ov128-ladder-n3 g384_ov128-ladder-n5; do
  cp "$CHAIN/results/stride-2026-08-25/conditions-verified/$cell/detections.geojson" \
     "results/stride-2026-08-25/conditions-verified/$cell/detections.geojson" || fail "copy $cell"
done
# Tier E's K = 10 rung has its own board-frame evaluation of that set.
for d in $K/board-frame/*/ $K/tier-e/cells/grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10-boardframe/; do
  ev=${d}evaluation.json
  "$PY" - "$ev" > "$L/args-bf-$(basename "$d").txt" <<'PYEOF' || fail "args $ev"
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
  mapfile -t ARGS < "$L/args-bf-$(basename "$d").txt"
  "$PY" scripts/evaluate_detections.py "${ARGS[@]}" > "$L/eval-bf-$(basename "$d").log" 2>&1 \
    || fail "eval $d"
done
"$PY" scripts/era1_leaderboard_tiering.py --analysis-id k-ladder-gs-stride-a-2026-09-12 \
  --conditions $K/tiering-input/gs-stride-a/run-conditions.json \
  --analyses $K/tiering-input/gs-stride-a/run-analyses.json \
  --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson --permute-mcc \
  --output-dir $K/mcc-test/tiering/gs-stride-a > "$L/tier-gs-stride-a.log" 2>&1 || fail "tier gs-stride-a"
"$PY" scripts/era1_leaderboard_tiering.py --analysis-id k-ladder-tier-e-2026-09-12 \
  --conditions $K/tier-e/tiering-input/run-conditions.json \
  --analyses $K/tier-e/tiering-input/run-analyses.json \
  --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson --permute-mcc \
  --output-dir $K/tier-e/tiering > "$L/tier-tier-e.log" 2>&1 || fail "tier tier-e"
"$PY" scripts/k_ladder_mcb.py --only gs-stride-a --only tier-e --output-dir "$O/ladder-mcb" \
  > "$L/ladder-mcb.log" 2>&1 || fail "mcb"
# Replace, never nest: `cp -r src dest` copies INTO an existing dest.
rm -rf "$O/ladders"; mkdir -p "$O/ladders"
cp -r $K/mcc-test/tiering/gs-stride-a "$O/ladders/gs-stride-a-tiering"
cp -r $K/tier-e/tiering "$O/ladders/tier-e-tiering"
cp -r $K/board-frame "$O/ladders/board-frame"
cp $K/tier-e/cells/grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10-boardframe/evaluation.json \
   "$O/ladders/tier-e-k10-boardframe-evaluation.json"
echo "=== $(date -u +%FT%TZ) LADDERS DONE"; echo DONE > "$L/ladders.state"
