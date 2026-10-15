#!/usr/bin/env bash
# W2-3a group 2: replay every offline stage of the K-ladder Phase 2 run
# (generating commit 326181bcd, 2026-09-12T08:56:49Z) in a disposable
# detached worktree at that commit. Stage order and commands follow the
# original /tmp/final_downstream.sh (recovered from the session transcript,
# agent-ae87367bcee3e0e5c, Write at 2026-09-12T07:22:36Z, launched 08:34:47Z)
# and the tile-vocabulary command of 08:44:33Z. Evaluation jobs (stage 3 of
# the original) are NOT re-run: the cell evaluations are census-verified; the
# collect stages read the committed evaluation.json files in the tree.
# No API call: run_pv.py is used for `extract` only; the network guard in
# env.sh refuses every internet socket. Worker cap 3 (two sweep workers here, so one more process may run beside it).
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
TREE=$ROOT/w2-3a-326181bcd
OUT=$ROOT/w2-3a-out/g2
source "$ROOT/env.sh"
mkdir -p "$OUT"
cd "$TREE" || exit 1

stage() { echo; echo "##### $* ($(date -u +%FT%TZ)) #####"; }
status() { echo "##### exit=$1 #####"; }

stage "0. inputs: real copies of the four GS rasters and the 192 px tile set"
mkdir -p inputs/rasters
cp -p "$HOME"/Code/map-reader-llm/inputs/rasters/K-35-0*.tif \
      "$HOME"/Code/map-reader-llm/inputs/rasters/K-35-0*.tif.aux.xml inputs/rasters/
if [ ! -d inputs/tiles_384_ov192 ]; then
    cp -rp "$HOME"/Code/map-reader-llm/inputs/tiles_384_ov192 inputs/
fi
ls -la inputs/rasters | head; echo "tiles_384_ov192: $(ls inputs/tiles_384_ov192 | wc -l)"
git -C "$TREE" rev-parse HEAD

touch "$OUT/start-marker"

stage "1. normalise the spend ledger from the committed metas"
$PY scripts/run_k_ladder_phase2_verifier.py --recompute-ledger; status $?

stage "2. sweep, choose operating points, materialise (all 28 rungs)"
$PY scripts/score_k_ladder_phase2_rungs.py prepare --fresh --sweep-workers 2; status $?

stage "4. collect the committed cells"
$PY scripts/score_k_ladder_phase2_rungs.py collect --strict; status $?

stage "5. re-derive the committed rungs' carried points"
$PY scripts/derive_k_ladder_committed_carried.py prepare; status $?
$PY scripts/derive_k_ladder_committed_carried.py collect; status $?

stage "6. re-derive the 3.7 family's opmax rungs"
$PY scripts/derive_g37_gs_opmax_rungs.py prepare; status $?
$PY scripts/derive_g37_gs_opmax_rungs.py collect; status $?

stage "6b. tile-vocabulary audit (original command of 08:44:33Z)"
$PY scripts/check_tile_vocabulary_match.py \
    --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \
    --glob "results/k-ladder-2026-09-12/phase2/materialised/*.geojson" \
    --json-out results/k-ladder-2026-09-12/phase2/tile-vocabulary-match.json \
    2>&1 | tail -15
status $?

stage "7. re-extract the 28 crop manifests into the out directory"
$PY - <<'PYEOF'
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, ".")
from scripts.run_k_ladder_phase2_verifier import resolve_paths, PADDING_PX
out = Path.home() / "scratch/s164-fw-recheck2-2026-10-15/w2-3a-out/g2/extract"
rungs = json.load(open("results/k-ladder-2026-09-12/phase2/unions.json"))["rungs"]
for rung in rungs:
    paths = resolve_paths(rung)
    dest = out / f"row{rung['row']:02d}"
    cmd = [sys.executable, "scripts/run_pv.py", "extract",
           "--proposer", f"{rung['consensus_dir']}/consensus_t1.geojson",
           "--output-dir", str(dest), "--padding", str(PADDING_PX),
           "--tiles-dir", paths["tiles_dir"]]
    done = subprocess.run(cmd, capture_output=True, text=True)
    (out / f"row{rung['row']:02d}.map").write_text(paths["crops_dir"] + "\n")
    print(rung["row"], paths["crops_dir"], "exit", done.returncode, flush=True)
    if done.returncode:
        print(done.stdout[-1500:], done.stderr[-1500:])
PYEOF
status $?

stage "8. copy regenerated files to the out directory"
git status --porcelain > "$OUT/git-status-after.txt"
git diff --stat > "$OUT/git-diff-stat.txt"
find outputs -name 'sweep_2d*.json' -newer "$OUT/start-marker" | sort > "$OUT/regen-sweeps.txt"
find results -type f -newer "$OUT/start-marker" | sort > "$OUT/regen-results.txt"
tar -cf "$OUT/tree-regenerated.tar" -T "$OUT/regen-sweeps.txt" -T "$OUT/regen-results.txt"
status $?
wc -l "$OUT/regen-sweeps.txt" "$OUT/regen-results.txt"
echo
echo "##### ALL STAGES ATTEMPTED ($(date -u +%FT%TZ)) #####"
