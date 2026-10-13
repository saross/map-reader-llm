#!/usr/bin/env bash
# =============================================================================
# legacy_g37.sh — attribute the ORIGIN move of four Gemini 3.7 cells
# =============================================================================
# Re-runs image_b_analysis.py with the code of `main` just before PR #42
# (dddfcc0af^1: D50 scorer, no origin route) on the ORIGIN data, for the four
# cells whose best point moved under ORIGIN: the 3.7 screen K = 5 and K = 10
# and the two 3.7 image arms. If this legacy run reproduces the committed
# values, the move is PR #42's origin route; if not, it is the D50 scorer.
# Scripts are a real git-archive copy; the data directories are read through
# symlinks to the ORIGIN copy and never written (outputs go to results/legacy/
# in this directory).
#
# Usage: legacy_g37.sh
# =============================================================================
set -uo pipefail
S=$HOME/scratch/s164-rescore-2026-10-13
WT=$HOME/scratch/s164-merges-2026-10-13/wt
PY=$HOME/Code/map-reader-llm/.venv/bin/python
D=$S/copies/legacy-g37; O=$S/copies/originA
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
mkdir -p $S/logs/legacy; echo $$ > $S/logs/legacy/legacy.pid
rm -rf "$D"; mkdir -p "$D/results/grid-2026-08-18/conditions-verified/g384_ov192"
git -C "$WT" archive dddfcc0af^1 -- scripts config.py pyproject.toml | tar -x -C "$D"
git -C "$WT" rev-parse dddfcc0af^1 > "$D/.source-commit"
ln -s "$O/outputs" "$D/outputs"; ln -s "$O/inputs" "$D/inputs"
git -C "$WT" show dddfcc0af^1:results/grid-2026-08-18/conditions-verified/g384_ov192/detections.geojson \
  > "$D/results/grid-2026-08-18/conditions-verified/g384_ov192/detections.geojson"
cd "$D" || exit 9
G37=outputs/gemini37-screen-2026-08-28; G37I=outputs/gemini37-image-gs-2026-09-01
run() { local tag=$1; shift; "$PY" scripts/image_b_analysis.py "$@" --out-dir "results/legacy/$tag" \
  > "$S/logs/legacy/$tag.log" 2>&1; echo "$tag $?"; }
run g37_k5 --outputs-root $G37 --cell g384_ov192_g37 --k 5 --union-name union_k5.geojson --verify-dir verify --no-ladder
run g37_k10 --outputs-root $G37 --cell g384_ov192_g37 --k 10 --union-name union_k10.geojson --verify-dir verify_k10
run g37img_arm1 --outputs-root $G37I --cell g384_ov192_g37img --k 5 --union-name union_k5.geojson --verify-dir verify_arm1 --no-ladder
run g37img_arm2 --outputs-root $G37I --cell g384_ov192_g37img --k 5 --union-name union_k5.geojson --verify-dir verify_arm2 --no-ladder
echo LEGACY DONE
