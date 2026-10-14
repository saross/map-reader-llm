#!/usr/bin/env bash
# =============================================================================
# W2-11 fault-window re-check (2026-10-14): inputs written on sapphire, W2.
#
# Serialised in ONE replay worktree (each stage checks out its generating
# commit; one CPU at a time). Every stage writes into $O2/<commit>/ and the
# tree is restored clean; nothing committed is modified.
#   e9d1db0d0  merge_passes.py --sweep --passes … (the three recorded commands)
#              + check_union_provenance.py --union on the nine rebuilt files
#   185681674  merge_passes.py --sweep over n1-outstanding-384's two pools
#   e01b8617a  … over e47-propose-brief::propose_brief-text
#   e7ebc1695  … over h12-v2::r3-hp-heavy, and fuse_detections_wbf.py at the
#              parameters wbf_diagnostics.json records
#   c053f5a41  meta completed_items against the GeoJSON's processed_tiles
#   43516df9a  run_pv.py extract + sweep_f1_greedy_pv.py for the 3 stages
#   f8e0eb600  run_pv.py extract (3), the committed carry harness (3), and
#              the harness's six sweeps
#   image      stride55 unions + provenance sidecars (b9d4032bb, bd5de9f80,
#              7d61f1ff9); crop manifests (b9d4032bb, bd5de9f80); the runs
#              4-5 pool passes re-merged from their chunks (bbdf4ba28 code);
#              six batch verifier legs re-parsed from batch_results.jsonl
#   7894b5b5a  final_board_sweeps.py --reference r2 --workers 1 and
#              final_board_n3_carried.py --reference r2 (long; last)
# Zero API: no verify, no lodge, no client; keys blanked, proxies dead.
# Usage: w2_11_sequence.sh [STAGE ...]   (default: all, in the order above)
# =============================================================================
set -uo pipefail
D=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w1-8-w2-11
T=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-92b151058
R=$HOME/scratch/s164-fw-recheck-2026-10-14/wt
O2=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-out/w2-11
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export GEMINI_API_KEY= GOOGLE_API_KEY= GOOGLE_GENAI_API_KEY=
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9
export https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 NO_PROXY= no_proxy=
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p "$O2"
step() { echo "=== $(date -Is) $*"; }
co() {
  if [ -n "$(git -C "$T" status --porcelain --untracked-files=no)" ]; then
    echo "REFUSED: tracked changes in replay tree"; git -C "$T" status --short | head; return 1
  fi
  git -C "$T" checkout -q --detach "$1" && echo "HEAD $(git -C "$T" rev-parse --short=9 HEAD)"
}
restore() { git -C "$T" checkout -q -- "$@"; }
pool_dir() {  # repo-relative pool dir, by rebuild_recovered_consensus.pool_dir_for
  (cd "$T" && $PY -c "import sys; sys.path.insert(0, 'scripts')
import rebuild_recovered_consensus as r
print(r.pool_dir_for(sys.argv[1], sys.argv[2]).relative_to(r.REPO))" "$1" "$2")
}

st_e9d1db0d0() {
  step "e9d1db0d0 consensus rebuilds at e9d1db0d0^"
  co e9d1db0d0^ || return 1
  local o=$O2/e9d1db0d0
  rm -rf "$o"; mkdir -p "$o"
  for spec in "outputs/gemini37-screen-2026-08-28/g384_ov192_g37|consensus-n1|1" \
              "outputs/gemini37-screen-2026-08-28/g384_ov192_g37|consensus-n3|1,2,3" \
              "outputs/grid-2026-08-18/g384_ov192|consensus-n5|1,2,3,4,5"; do
    IFS='|' read -r inp name passes <<< "$spec"
    (cd "$T" && $PY scripts/merge_passes.py --input-dir "$inp" --output-dir "$o/$(basename "$inp")-$name" \
      --sweep --passes "$passes") > "$o/$(basename "$inp")-$name.log" 2>&1
    echo "merge $inp $name rc=$?"
  done
  co e9d1db0d0 || return 1
  local args=()
  for f in $(git -C "$T" ls-files 'outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n[13]/consensus_t*.geojson' \
             'outputs/grid-2026-08-18/g384_ov192/consensus-n5/consensus_t*.geojson'); do
    args+=(--union "$f")
  done
  (cd "$T" && $PY scripts/check_union_provenance.py "${args[@]}" --scratch-dir "$o/cup-scratch" \
    --json-out "$o/check_union_provenance.json") > "$o/check_union_provenance.log" 2>&1
  echo "check_union_provenance rc=$?"
  rm -rf "$o/cup-scratch"
}

st_consensus_0908() {
  # 185681674, e01b8617a, e7ebc1695: rebuild_recovered_consensus.py's core step
  for spec in "185681674|n1-outstanding-384|pro-image-high-t0|" \
              "185681674|n1-outstanding-384|pro-text-high-t0|" \
              "e01b8617a|e47-propose-brief|propose_brief-text|" \
              "e7ebc1695|h12-v2|r3-hp-heavy|outputs/h12-v2/greedy/r3-hp-heavy"; do
    IFS='|' read -r c run pool cdir <<< "$spec"
    step "$c merge_passes --sweep $run::$pool"
    co "$c" || return 1
    local pd; pd=$(pool_dir "$run" "$pool") || { echo "pool_dir failed"; continue; }
    echo "pool dir $pd; consensus ${cdir:-$pd/consensus}"
    echo "${cdir:-$pd/consensus}" > "$O2/$c-$pool.consensus-dir"
    rm -rf "$O2/$c/$pool"; mkdir -p "$O2/$c"
    (cd "$T" && $PY scripts/merge_passes.py --sweep --input-dir "$T/$pd" \
      --output-dir "$O2/$c/$pool") > "$O2/$c/$pool.log" 2>&1
    echo "rc=$?"
  done
  step "e7ebc1695 WBF fusion"
  co e7ebc1695 || return 1
  rm -rf "$O2/e7ebc1695/wbf"
  # The fuse script imports scripts.* without adding the root to sys.path;
  # the first run here omitted PYTHONPATH and failed, and was redone by
  # w2_11_wbf.sh (2026-10-14T01:38Z).
  (cd "$T" && PYTHONPATH="$T" $PY scripts/fuse_detections_wbf.py --config h12v2-r3-hp-heavy \
    --output-dir "$O2/e7ebc1695/wbf" --iou-threshold 0.25 --min-separation-m 60 \
    --min-dim 20 --max-dim 200 --min-area 400 --max-area 40000) > "$O2/e7ebc1695/wbf.log" 2>&1
  echo "wbf rc=$?"
}

st_c053f5a41() {
  step "c053f5a41 meta completed_items vs GeoJSON processed_tiles"
  $PY "$D/check_c053f5a41.py" "$R" "$O2/c053f5a41.json"
}

st_43516df9a() {
  step "43516df9a extract + sweep for the three recovery stages"
  co 43516df9a || return 1
  git -C "$T" diff --stat 17a45830f 43516df9a -- scripts/run_pv.py scripts/extract_candidates.py \
    scripts/sweep_f1_greedy_pv.py > "$O2/43516df9a-code-diff.txt"
  for spec in "pv-diag-image-t0.0-v1|outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/consensus/consensus_t1.geojson|outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10-recovery-2026-09-08" \
              "pv-diag-text-t0.0-v1|outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/consensus/consensus_t1.geojson|outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/verified-v1-n3-recovery-2026-09-08" \
              "e47-1of5-v1|outputs/h11/e47-propose-brief/consensus/flash-high-text-1of5-recovery-2026-09-08.geojson|outputs/h11/e47-propose-brief/verified/flash-high-text-1of5-recovery-2026-09-08"; do
    IFS='|' read -r label cands stage <<< "$spec"
    local o=$O2/43516df9a/$label
    rm -rf "$o"; mkdir -p "$o"
    (cd "$T" && $PY scripts/run_pv.py extract --proposer "$cands" --output-dir "$o/crops" \
      --padding 75) > "$o/extract.log" 2>&1
    echo "$label extract rc=$?"
    cp "$o/crops/candidate_manifest.json" "$o/"; rm -rf "$o/crops"
    (cd "$T" && $PY scripts/sweep_f1_greedy_pv.py --config "$label" --crops-dir "$stage/crops" \
      --verified-dir "$stage" --output "$o/sweep_2d.json" \
      --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
      --buffer-m 20 30 40 50) > "$o/sweep.log" 2>&1
    echo "$label sweep rc=$?"
  done
}

st_f8e0eb600() {
  step "f8e0eb600 extracts, carries and sweeps"
  co f8e0eb600 || return 1
  local V=outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37
  local G=outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder
  local o=$O2/f8e0eb600
  rm -rf "$o"; mkdir -p "$o"
  git -C "$R" show 63f4cac1c:results/k-ladder-2026-09-12/recovery-fix-2026-09-13/harness/carry_probabilities.py \
    > "$o/carry_probabilities_harness.py"
  for spec in "k1|outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n1/consensus_t1.geojson|$V/crops_k1_recovery-fixed|$V/crops_k1|$V/verify_k1|k1" \
              "k3|outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n3/consensus_t1.geojson|$V/crops_k3_recovery-fixed|$V/crops_k3|$V/verify_k3|k3" \
              "k5|outputs/grid-2026-08-18/g384_ov192/consensus-n5/consensus_t1.geojson|$G/k5_recovery-fixed/crops|$G/k5/crops|$G/k5|k5-tier-e"; do
    IFS='|' read -r key prop newcrops oldcrops oldstage label <<< "$spec"
    mkdir -p "$o/$key"
    (cd "$T" && $PY scripts/run_pv.py extract --proposer "$prop" --output-dir "$o/$key/crops" \
      --padding 75 --rasters-dir inputs/rasters --tiles-dir inputs/tiles_384_ov192) > "$o/$key/extract.log" 2>&1
    echo "$key extract rc=$?"
    cp "$o/$key/crops/candidate_manifest.json" "$o/$key/"; rm -rf "$o/$key/crops"
    (cd "$T" && $PY "$o/carry_probabilities_harness.py" --old-manifest "$oldcrops/candidate_manifest.json" \
      --old-probs "$oldstage/probabilities.json" --new-manifest "$newcrops/candidate_manifest.json" \
      --out-dir "$o/$key/carry" --rasters-dir inputs/rasters --label "$label") > "$o/$key/carry.log" 2>&1
    echo "$key carry rc=$?"
  done
  for spec in "k1|g384_ov192_g37-n1|$V/crops_k1_recovery-fixed|$V/verify_k1_recovery-fixed|sweep_2d_era2b.json|sweep_2d.json" \
              "k3|g384_ov192_g37-n3|$V/crops_k3_recovery-fixed|$V/verify_k3_recovery-fixed|sweep_2d_era2b.json|sweep_2d.json" \
              "k5|brief-text-g384-ov192-k5|$G/k5_recovery-fixed/crops|$G/k5_recovery-fixed|sweep_board.json|sweep_era2.json"; do
    IFS='|' read -r key cfg crops ver board era2 <<< "$spec"
    for fr in "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson|$board" \
              "inputs/vectors/bounds/384/full_evaluation_bounds.geojson|$era2"; do
      IFS='|' read -r bounds name <<< "$fr"
      (cd "$T" && $PY scripts/sweep_f1_greedy_pv.py --config "$cfg" --crops-dir "$T/$crops" \
        --verified-dir "$T/$ver" --output "$o/$key/$name" --bounds "$bounds" \
        --buffer-m 20 30 40 50) > "$o/$key/$name.log" 2>&1
      echo "$key sweep $name rc=$?"
    done
  done
}

st_image_unions() {
  local MAN=inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json
  for spec in "b9d4032bb|outputs/gemini37-image-55map-2026-09-13|g384_ov192_55map_g37img|1 3" \
              "bd5de9f80|outputs/gemini37-image-55map-2026-09-13|g384_ov192_55map_g37img|5" \
              "7d61f1ff9|outputs/gemini3-image-55map-2026-09-16|g384_ov192_55map_g3img|1 3 5"; do
    IFS='|' read -r c out cell ks <<< "$spec"
    step "image unions $c $cell K=$ks"
    co "$c" || return 1
    local vr=$out/verifier/$cell o=$O2/image-unions/$c
    rm -rf "$o"; mkdir -p "$o"
    for k in $ks; do
      rm -f "$T/$vr/union_k$k.geojson" "$T/$vr/union_k${k}_pass_provenance.json"
      (cd "$T" && $PY scripts/stride55_prepare_and_union.py --root "$out" --cell "$cell" \
        --manifest "$MAN" --k "$k" --write) > "$o/union_k$k.log" 2>&1
      echo "union k$k rc=$?"
      (cd "$T" && $PY scripts/emit_union_pass_provenance.py --root "$out" --cell "$cell" \
        --k "$k" --write) > "$o/provenance_k$k.log" 2>&1
      echo "provenance k$k rc=$?"
      cp "$T/$vr/union_k$k.geojson" "$T/$vr/union_k${k}_pass_provenance.json" "$o/"
      restore "$vr/union_k$k.geojson" "$vr/union_k${k}_pass_provenance.json"
    done
    if [ "$cell" = g384_ov192_55map_g37img ]; then
      for k in $ks; do
        mkdir -p "$o/crops_k$k"
        (cd "$T" && $PY scripts/run_pv.py extract --proposer "$vr/union_k$k.geojson" \
          --output-dir "$o/crops_k$k/crops" --tiles-dir inputs/tiles_384_ov192_55maps \
          --padding 75) > "$o/crops_k$k/extract.log" 2>&1
        echo "extract k$k rc=$?"
        cp "$o/crops_k$k/crops/candidate_manifest.json" "$o/crops_k$k/"; rm -rf "$o/crops_k$k/crops"
        (cd "$T" && $PY scripts/check_union_provenance.py --manifest "$vr/crops_k$k/candidate_manifest.json" \
          --json-out "$o/crops_k$k/provenance.json") > "$o/crops_k$k/provenance.log" 2>&1
        echo "manifest provenance k$k rc=$?"
      done
    fi
  done
}

st_image_remerge() {
  step "image runs 4-5 re-merged from chunks at bbdf4ba28"
  co bbdf4ba28 || return 1
  local B=outputs/gemini37-image-55map-2026-09-13
  local P=$B/g384_ov192_55map_g37img
  local NAME=detections-detect_brief-text-image-3.7-flash-2026-09-17
  for n in 4 5; do
    $PY "$D/remerge_chunks.py" --tree "$T" --repo "$R" \
      --run-dir "$B/batch-staging-run$n/detect_brief-text-image/run_1" \
      --version detect_brief-text-image --run-number 1 --chunks-commit 21d1b497d \
      --merged-commit 1553a7b24 --scratch "$O2/remerge/run_$n" --out "$O2/remerge/run_$n.json" \
      --targets "{\".geojson\": [\"1553a7b24\", \"$P/run_$n/$NAME.geojson\"], \".meta.json\": [\"bbdf4ba28\", \"$P/run_$n/$NAME.meta.json\"], \".tiles.json\": [\"31d59a8af\", \"$P/run_$n/$NAME.tiles.json\"]}"
  done
}

st_image_reparse() {
  local G37=outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img
  local G3=outputs/gemini3-image-55map-2026-09-16/verifier/g384_ov192_55map_g3img
  for spec in "87b92878a|5778b5569|$G37/verify_k5_arm1_replicate-batch-2026-09-20|--manifest $G37/crops_k5/candidate_manifest.json" \
              "3ced9749c|3f8af3a65|$G37/verify_k5_arm2_replicate-batch-2026-09-20|--manifest $G37/crops_k5/candidate_manifest.json" \
              "460b168b9|cab5d1b91|$G37/probe-batch-vs-flex-2026-09-19/verify_batch|--manifest $G37/probe-batch-vs-flex-2026-09-19/crops/candidate_manifest.json" \
              "79a2afc0d|cda04a952|$G3/verify_k1_arm2|--expected-n 22785" \
              "7d587cf27|e21b5295a|$G3/verify_k3_arm2|--expected-n 36389" \
              "4d65c1f27|880c207f7|$G3/verify_k5_arm2|--expected-n 45786"; do
    IFS='|' read -r code added leg extra <<< "$spec"
    step "REPARSE $leg code@$code added@$added"
    co "$code" || return 1
    # shellcheck disable=SC2086
    $PY "$D/reparse_verifier_leg.py" --tree "$T" --repo "$R" --leg "$leg" --added "$added" \
      $extra --out "$O2/reparse/$(basename "$(dirname "$leg")")-$(basename "$leg").json"
  done
}

st_7894b5b5a() {
  # Worker count does not change the output: Pool.map returns rows in task
  # order, each point is scored independently, and rows are sorted before
  # writing (the original ran with 22 workers). R2_WORKERS defaults to 1.
  local W=${R2_WORKERS:-1}
  step "7894b5b5a r2 board sweep at 7894b5b5a^ (--workers $W)"
  co 7894b5b5a^ || return 1
  local H=results/55map-final-board-r2-2026-09-06
  echo "home tracked at parent: $(git -C "$T" ls-files "$H" | wc -l)"
  [ -e "$T/$H" ] && { echo "home exists at parent; refusing"; return 1; }
  (cd "$T" && $PY scripts/final_board_sweeps.py --reference r2 --workers "$W") > "$O2/r2-sweeps.log" 2>&1
  echo "final_board_sweeps rc=$?"
  (cd "$T" && $PY scripts/final_board_n3_carried.py --reference r2) > "$O2/r2-n3.log" 2>&1
  echo "final_board_n3_carried rc=$?"
  rm -rf "$O2/r2-home"; mv "$T/$H" "$O2/r2-home"
}

stages=("$@")
[ ${#stages[@]} -eq 0 ] && stages=(e9d1db0d0 consensus_0908 c053f5a41 43516df9a f8e0eb600 \
                                   image_unions image_remerge image_reparse 7894b5b5a)
for s in "${stages[@]}"; do "st_$s" || echo "STAGE $s FAILED rc=$?"; done
co 69eb32132
step "W2-11 SEQUENCE DONE"
