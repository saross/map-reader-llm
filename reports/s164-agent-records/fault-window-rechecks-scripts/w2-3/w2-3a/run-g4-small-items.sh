#!/usr/bin/env bash
# W2-3a group 4: the K-ladder Phase 1 small items.
# Original commands (session transcript, agent-a51feb87262e915a2):
#   2026-09-12T00:27:09Z sapphire, HEAD 75110d3b1: /tmp/probe_cmd.sh
#       (probe_subpool_verifier_coverage.py, six pairs) -> b949d5644
#       results/k-ladder-2026-09-12/subpool-coverage-probe.json
#   2026-09-12T00:49:16Z sapphire, HEAD 6750595bc: /tmp/union_sizes.sh
#       (probe_first_n_union_sizes.py, 14 pools, N = 1 and 3) -> 3013171cd
#       results/k-ladder-2026-09-12/first-n-union-sizes.json
#   2026-09-12T01:16Z amd-tower agent worktree: build_k_ladder_inventory.py
#       -> f4a1011a8 inventory.json, inventory-tables.md (inventory.md is the
#       hand-written narrative around them)
# Each replays at its committing commit (scripts unchanged from the run's HEAD;
# see the commit-identity check printed below). One process at a time.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
OUT=$ROOT/w2-3a-out/g4
source "$ROOT/env.sh"
export TMPDIR=$ROOT/w2-3a-out/tmp
mkdir -p "$OUT" "$TMPDIR"

stage() { echo; echo "##### $* ($(date -u +%FT%TZ)) #####"; }
status() { echo "##### exit=$1 #####"; }

for c in b949d5644 3013171cd f4a1011a8; do
    t=$ROOT/w2-3a-$c
    if [ ! -d "$t" ]; then
        git -C "$HOME/Code/map-reader-llm" worktree add --detach "$t" "$c" 2>&1 | tail -1
    fi
done
G=$ROOT/w2-3a-f4a1011a8
echo "script identity (empty = identical):"
git -C "$G" diff --stat 75110d3b1 b949d5644 -- scripts/probe_subpool_verifier_coverage.py \
    scripts/merge_passes.py
git -C "$G" diff --stat 6750595bc 3013171cd -- scripts/probe_first_n_union_sizes.py \
    scripts/merge_passes.py outputs/h11/pv-diag-384 outputs/gemini37-screen-2026-08-28/g384_ov192_g37

stage "1. b949d5644: sub-pool coverage probe"
cd "$ROOT/w2-3a-b949d5644" || exit 1
git rev-parse HEAD
B=outputs/h11/pv-diag-384
$PY scripts/probe_subpool_verifier_coverage.py \
  --pair "$B/flash-minimal-text-n30-t07/text-t0.3/consensus-n5/consensus_t1.geojson" \
         "$B/flash-minimal-text-n30-t07/text-t0.3/consensus/consensus_t1.geojson" \
  --label "Gemini 3 MINIMAL text T0.3: 5-pass sub-pool union vs 10-pass union" \
  --pair "$B/flash-minimal-text-n30-t07/text-t0.7/consensus-n5/consensus_t1.geojson" \
         "$B/flash-minimal-text-n30-t07/text-t0.7/consensus-n10/consensus_t1.geojson" \
  --label "Gemini 3 MINIMAL text T0.7: 5-pass sub-pool union vs 10-pass union" \
  --pair "$B/flash-minimal-text-n30-t07/text-t0.7/consensus-n10/consensus_t1.geojson" \
         "$B/flash-minimal-text-n30-t07/text-t0.7/consensus/consensus_t1.geojson" \
  --label "Gemini 3 MINIMAL text T0.7: 10-pass sub-pool union vs 30-pass union" \
  --pair "$B/flash-high-text-n5/text-t0.3/consensus-n5/consensus_t1.geojson" \
         "$B/flash-high-text-n5/text-t0.3/consensus/consensus_t1.geojson" \
  --label "Gemini 3 HIGH text T0.3: 5-pass sub-pool union vs 10-pass union" \
  --pair "$B/image-n5/image-t0.7/consensus-n5/consensus_t1.geojson" \
         "$B/image-n5/image-t0.7/consensus/consensus_t1.geojson" \
  --label "Gemini 3 MINIMAL image T0.7: 5-pass sub-pool union vs 10-pass union" \
  --pair "$B/flash-high-image-n5/image-t1.0/consensus-n5/consensus_t1.geojson" \
         "$B/flash-high-image-n5/image-t1.0/consensus/consensus_t1.geojson" \
  --label "Gemini 3 HIGH image T1.0: 5-pass sub-pool union vs 10-pass union" \
  --out results/k-ladder-2026-09-12/subpool-coverage-probe.json > "$OUT/probe.log" 2>&1
status $?
tail -3 "$OUT/probe.log"

stage "2. 3013171cd: first-N union sizes"
cd "$ROOT/w2-3a-3013171cd" || exit 1
git rev-parse HEAD
$PY scripts/probe_first_n_union_sizes.py \
  --n 1 --n 3 \
  --pool "$B/flash-minimal-text-n30-t07/text-t0.3" --label "Gemini 3 MINIMAL text 384 px, T 0.3" \
  --pool "$B/flash-minimal-text-n30-t07/text-t0.7" --label "Gemini 3 MINIMAL text 384 px, T 0.7" \
  --pool "$B/flash-minimal-text-n30-t07/text-t1.0" --label "Gemini 3 MINIMAL text 384 px, T 1.0" \
  --pool "$B/flash-high-text-n5/text-t0.3"         --label "Gemini 3 HIGH text 384 px, T 0.3" \
  --pool "$B/flash-high-text-n5/text-t0.7"         --label "Gemini 3 HIGH text 384 px, T 0.7" \
  --pool "$B/flash-high-text-n5/text-t1.0"         --label "Gemini 3 HIGH text 384 px, T 1.0" \
  --pool "$B/image-n5/image-t0.3"                  --label "Gemini 3 MINIMAL image 384 px, T 0.3" \
  --pool "$B/image-n5/image-t0.7"                  --label "Gemini 3 MINIMAL image 384 px, T 0.7" \
  --pool "$B/image-n5/image-t1.0"                  --label "Gemini 3 MINIMAL image 384 px, T 1.0" \
  --pool "$B/flash-high-image-n5/image-t0.3"       --label "Gemini 3 HIGH image 384 px, T 0.3" \
  --pool "$B/flash-high-image-n5/image-t0.7"       --label "Gemini 3 HIGH image 384 px, T 0.7" \
  --pool "$B/flash-high-image-n5/image-t1.0"       --label "Gemini 3 HIGH image 384 px, T 1.0" \
  --pool "$B/scale-4-optimal-487"                  --label "Gemini 3 scale-4-optimal 487" \
  --pool outputs/gemini37-screen-2026-08-28/g384_ov192_g37 --label "Gemini 3.7 text, GS B geometry" \
  --out results/k-ladder-2026-09-12/first-n-union-sizes.json > "$OUT/union-sizes.log" 2>&1
status $?
tail -3 "$OUT/union-sizes.log"

stage "3. f4a1011a8: the inventory"
cd "$ROOT/w2-3a-f4a1011a8" || exit 1
git rev-parse HEAD
$PY scripts/build_k_ladder_inventory.py > "$OUT/inventory.log" 2>&1
status $?
tail -3 "$OUT/inventory.log"

echo
echo "##### ALL STAGES ATTEMPTED ($(date -u +%FT%TZ)) #####"
