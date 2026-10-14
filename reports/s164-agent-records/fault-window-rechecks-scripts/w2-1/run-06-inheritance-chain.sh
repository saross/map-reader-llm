#!/usr/bin/env bash
# W2-1 replay 06: the inheritance study, each file at its generating commit.
#   A 62b13e6fd ladder        -> 3.7 ladder.json, 4 sweep CSVs, 4 cells, manifest
#   B 3fc3f0751 tests         -> 3.7 tests.json
#   C 58500a739 ladder        -> 3.7 ladder.json (vote-gated counts)
#   D 2ba1914b6 ladder, separation (g37), ladder, separation (g3)
#                             -> 3.7 ladder.json + union_separation.json;
#                                G3 ladder.json, union_separation.json, CSVs,
#                                cells, manifest
#   E a14d218ee tests (g3)    -> G3 tests.json
# Each step: run-inherit.sh (checkout, one-line root patch, stages), then
# compare_files.py against the generating commit AND today's 90294a283,
# then copy the regenerated files aside so the next checkout cannot lose
# them. The Gemini 3 crop manifests were never committed; step D copies
# them (real copies, read-only source) from sapphire's main checkout,
# untracked, into the replay tree (see the report's caveat). Zero API.
set -uo pipefail
REC=~/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w2-1
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-inherit
OUT=~/scratch/s164-fw-recheck-2026-10-14/w2-1-out
PY=~/Code/map-reader-llm/.venv/bin/python
I37=results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20
I3=results/gemini3-image-55map-2026-09-16/inheritance-2026-09-20
cmpstep () {  # tag commit files...
  local tag=$1 commit=$2; shift 2
  local pairs=()
  for f in "$@"; do pairs+=(--pair "$commit:$f" --pair "90294a283:$f"); done
  "$PY" "$REC/compare_files.py" --tree "$TREE" --out "$REC/cmp-06$tag.json" "${pairs[@]}"
  echo "compare $tag rc=$?"
  mkdir -p "$OUT/inherit-$tag"
  (cd "$TREE" && cp --parents "$@" "$OUT/inherit-$tag/")
}
ladder_files () {  # home prefix
  local h=$1 p=$2
  echo "$h/ladder.json $h/cells_manifest.json"
  for a in ARM1 ARM2; do for k in K1 K3; do
    echo "$h/sweep_$p-$a-$k-inherited.csv $h/cells/$p-$a-$k-carried-inherited/detections.geojson"
  done; done
}
echo "chain start $(date -u +%FT%TZ)"
"$REC/run-inherit.sh" 62b13e6fd A ladder || echo "STEP A FAILED"
cmpstep A 62b13e6fd $(ladder_files $I37 IMG)
"$REC/run-inherit.sh" 3fc3f0751 B tests || echo "STEP B FAILED"
cmpstep B 3fc3f0751 $I37/tests.json
"$REC/run-inherit.sh" 58500a739 C ladder || echo "STEP C FAILED"
cmpstep C 58500a739 $(ladder_files $I37 IMG)
V=outputs/gemini3-image-55map-2026-09-16/verifier/g384_ov192_55map_g3img
for k in 1 3 5; do
  mkdir -p "$TREE/$V/crops_k$k"
  cp ~/Code/map-reader-llm/$V/crops_k$k/candidate_manifest.json "$TREE/$V/crops_k$k/"
done
sha256sum "$TREE/$V"/crops_k*/candidate_manifest.json
"$REC/run-inherit.sh" 2ba1914b6 D ladder separation ladder:g3 separation:g3 || echo "STEP D FAILED"
cmpstep D 2ba1914b6 $(ladder_files $I37 IMG) $I37/union_separation.json \
  $(ladder_files $I3 G3IMG) $I3/union_separation.json
"$REC/run-inherit.sh" a14d218ee E tests:g3 || echo "STEP E FAILED"
cmpstep E a14d218ee $I3/tests.json
echo "chain end $(date -u +%FT%TZ)"
