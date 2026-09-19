#!/usr/bin/env bash
# Image proposer at 55-map scale, any campaign: unions, sidecars, crops, arms.
#
# Generalised on 2026-09-19 (S155, PI request) from the 3.7-only
# scripts/gemini37-image-55map-unions-and-arms.sh so the Gemini 3 image pool
# (and any later family) runs through the same stages. A campaign is a
# proposer pool: its outputs root and cell directory. The two verifier arms
# are the 2x2's fixed columns and are the same for every campaign.
#
# Rulings this script implements:
#   - Unions by scripts/stride55_prepare_and_union.py (the 55-map union rule,
#     for comparability with the text arms; deltas report 2026-09-13
#     section 10.2), with the pass_provenance sidecar emitted over the same
#     resolved fragment set.
#   - Arm 1 (Gemini 3 `minimal`) on realtime flex, where that family is
#     prompt; arm 2 (3.7 `low`) on the Batch API — PI ruling 2026-09-18
#     (docs/agent-guidance.md section Experiment Execution). Batch legs are
#     chunked at 4,000 requests per job by run_pv.py (the 2 GB file limit).
#   - Never two concurrent Gemini 3.7 runs (PI rule 2026-08-30). Run the arms
#     as separate invocations (ARMS=arm2 first, then ARMS=arm1 alongside the
#     batch wait) — that is the PI's recommended order, and arm 1 is not 3.7.
#
# Runbook:
#   Precondition: every proposer pass COMPLETE at 24,561/24,561 after the
#     recovery fold (stage 0 checks it and stops otherwise), and the leg
#     approved through the phase gate.
#   Artefacts:  <root>/verifier/<cell>/union_k{K}.geojson
#               <root>/verifier/<cell>/union_k{K}_pass_provenance.json
#               <root>/verifier/<cell>/crops_k{K}/candidate_manifest.json
#                 (+ PNGs, gitignored)
#               <root>/verifier/<cell>/verify_k{K}_arm{1,2}/probabilities.json,
#                 run.meta.json (+ batch_results.jsonl for a batch arm)
#   Finished:   "ALL ARMS DONE" on stdout — printed ONLY when every requested
#               arm's run.meta.json books items_processed equal to its union
#               count. Otherwise "ARMS INCOMPLETE" and exit 2. (The earlier
#               script printed its success line unconditionally; audit lens B,
#               2026-09-19.)
#   Stop:       set -e — any stage's failure stops the script. The union
#               builder raises CoverageError unless every pass covers the
#               pinned manifest exactly.
#   Partial:    idempotent per stage. Unions and sidecars are rebuilt (cheap,
#               deterministic). Crops are skipped when the manifest exists.
#               An arm is skipped only when COMPLETE (see Finished); an
#               incomplete realtime arm resumes from its probabilities.json
#               (run_pv.py's own resume), an incomplete batch arm is re-run
#               whole, with a warning, because the batch path has no resume.
#   Verify:     the operator reads each union's feature count against the
#               sidecar, and each arm's run.meta.json items_processed against
#               the union count, before scoring — the script prints both.
#
# Usage (from ~/Code/map-reader-llm on sapphire):
#     CAMPAIGN=g3 bash scripts/image-55map-unions-and-arms.sh            # everything
#     CAMPAIGN=g3 STAGES=prepare bash scripts/image-55map-unions-and-arms.sh   # free stages only
#     CAMPAIGN=g3 STAGES=arms ARMS=arm2 bash scripts/image-55map-unions-and-arms.sh
#     CAMPAIGN=g3 STAGES=arms ARMS=arm1 WORKERS=50 bash scripts/image-55map-unions-and-arms.sh
#
# Environment:
#     CAMPAIGN   g37 | g3 (required)
#     KS         rungs, default per campaign (g37 "1 3 5", g3 "1 3 5")
#     ARMS       "arm1 arm2" (default) or one of them
#     STAGES     "prepare arms" (default), "prepare" or "arms"
#     ARM1_MODE  realtime (default) | batch;  ARM2_MODE  batch (default) | realtime
#     WORKERS    realtime workers (default 50)
#
# Created: 2026-09-19 (S155)
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0

set -euo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
MANIFEST=inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json
TILES=inputs/tiles_384_ov192_55maps
VERIFIER_CONFIG=prompts/configs/verify_adversarial-text.json
WORKERS=${WORKERS:-50}
ARMS=${ARMS:-"arm1 arm2"}
STAGES=${STAGES:-"prepare arms"}
ARM1_MODE=${ARM1_MODE:-realtime}
ARM2_MODE=${ARM2_MODE:-batch}
PADDING=75

# The campaign table: where each proposer pool lives. Mirrors
# scripts/gemini37_image_55map_r2.py's Campaign records.
case "${CAMPAIGN:-}" in
  g37) OUT=outputs/gemini37-image-55map-2026-09-13; CELL=g384_ov192_55map_g37img; KS=${KS:-"1 3 5"} ;;
  g3)  OUT=outputs/gemini3-image-55map-2026-09-16;  CELL=g384_ov192_55map_g3img;  KS=${KS:-"1 3 5"} ;;
  *)   echo "CAMPAIGN must be g37 or g3 (got '${CAMPAIGN:-}')"; exit 2 ;;
esac
VROOT=$OUT/verifier/$CELL

# The two verifier arms, exactly as the 3.7 campaign card section 2 fixes
# them; the same for every campaign.
ARM1_MODEL=gemini-3-flash-preview
ARM1_THINKING=minimal
ARM2_MODEL=gemini-3.7-flash
ARM2_THINKING=low

union_count() {
  $PY -c "import json,sys; print(len(json.load(open(sys.argv[1]))['features']))" "$1"
}

# An arm is complete when its run.meta.json books items_processed equal to
# the union count. Prints "complete", "partial" (probabilities.json present
# but not complete) or "absent".
arm_state() {
  local dest=$1 n_union=$2
  $PY - "$dest" "$n_union" <<'EOF'
import json, sys
from pathlib import Path
dest, n_union = Path(sys.argv[1]), int(sys.argv[2])
meta = dest / "run.meta.json"
if meta.exists():
    m = json.load(open(meta))
    n = int(m.get("execution_stats", {}).get("items_processed") or 0)
    if n == n_union:
        print("complete"); sys.exit(0)
print("partial" if (dest / "probabilities.json").exists() else "absent")
EOF
}

if [[ " $STAGES " == *" prepare "* ]]; then
  echo "=== campaign $CAMPAIGN: $OUT / $CELL, rungs [$KS]"
  echo "=== stage 0: pass coverage after the recovery fold $(date -Is)"
  $PY - "$OUT/$CELL" "$MANIFEST" "$KS" <<'EOF'
import glob, json, os, sys
cell_dir, manifest_path, ks = sys.argv[1], sys.argv[2], [int(k) for k in sys.argv[3].split()]
pinned = set(json.load(open(manifest_path)))
worst = 0
for i in range(1, max(ks) + 1):
    run = f"run_{i}"
    done: set[str] = set()
    frags = sorted(glob.glob(f"{cell_dir}/{run}/*.tiles.json")
                   + glob.glob(f"{cell_dir}/{run}_recovery*/*.tiles.json"))
    if not frags:
        sys.exit(f"COVERAGE GATE FAIL: {run} has no tiles.json under {cell_dir}")
    for tj in frags:
        done |= set(json.load(open(tj))["completed"])
    missing = len(pinned - done)
    worst = max(worst, missing)
    print(f"{run}: {len(done)}/{len(pinned)} tiles across {len(frags)} fragment(s), {missing} missing")
if worst:
    sys.exit(f"COVERAGE GATE FAIL: {worst} tile(s) missing from some pass")
print("coverage gate OK")
EOF

  echo "=== stage 1: unions (stride builder, first-N rule) $(date -Is)"
  for k in $KS; do
    $PY scripts/stride55_prepare_and_union.py \
      --root "$OUT" --cell "$CELL" --manifest "$MANIFEST" --k "$k" --write
  done

  echo "=== stage 2: provenance sidecars $(date -Is)"
  for k in $KS; do
    $PY scripts/emit_union_pass_provenance.py --root "$OUT" --cell "$CELL" --k "$k" --write
  done

  echo "=== stage 3: union feature counts vs sidecars $(date -Is)"
  for k in $KS; do
    n=$(union_count "$VROOT/union_k$k.geojson")
    m=$($PY -c "import json,sys; print(json.load(open(sys.argv[1])).get('union_feature_count'))" \
          "$VROOT/union_k${k}_pass_provenance.json")
    echo "union_k$k: $n candidates (sidecar says $m)"
    [ "$n" = "$m" ] || { echo "UNION/SIDECAR MISMATCH for k=$k"; exit 2; }
  done

  echo "=== stage 4: crop extraction $(date -Is)"
  for k in $KS; do
    if [ -f "$VROOT/crops_k$k/candidate_manifest.json" ]; then
      echo "crops_k$k already extracted, skipping"
    else
      $PY scripts/run_pv.py extract \
        --proposer "$VROOT/union_k$k.geojson" \
        --output-dir "$VROOT/crops_k$k" \
        --tiles-dir "$TILES" \
        --padding "$PADDING"
    fi
    n=$(union_count "$VROOT/union_k$k.geojson")
    m=$($PY -c "import json,sys; d=json.load(open(sys.argv[1])); print(len(d['candidates']))" \
          "$VROOT/crops_k$k/candidate_manifest.json")
    [ "$n" = "$m" ] || { echo "UNION/CROPS MISMATCH for k=$k: $n vs $m"; exit 2; }
  done
fi

if [[ " $STAGES " == *" arms "* ]]; then
  echo "=== stage 5: verifier arms [$ARMS] over rungs [$KS] $(date -Is)"
  incomplete=0
  for k in $KS; do
    n_union=$(union_count "$VROOT/union_k$k.geojson")
    for arm in $ARMS; do
      dest=$VROOT/verify_k${k}_${arm}
      if [ "$arm" = "arm1" ]; then
        model=$ARM1_MODEL; thinking=$ARM1_THINKING; mode=$ARM1_MODE
      else
        model=$ARM2_MODEL; thinking=$ARM2_THINKING; mode=$ARM2_MODE
      fi
      state=$(arm_state "$dest" "$n_union")
      if [ "$state" = complete ]; then
        echo "verify_k${k}_${arm}: complete ($n_union/$n_union), skipping"
        continue
      fi
      if [ "$state" = partial ] && [ "$mode" = batch ]; then
        echo "verify_k${k}_${arm}: partial probabilities.json but batch has no resume — re-running whole"
      elif [ "$state" = partial ]; then
        echo "verify_k${k}_${arm}: partial — resuming from probabilities.json"
      fi
      echo "--- verify_k${k}_${arm}: $model / $thinking / $mode, $n_union candidates $(date -Is)"
      $PY scripts/run_pv.py verify \
        --crops-dir "$VROOT/crops_k$k" \
        --verifier-config "$VERIFIER_CONFIG" \
        --output-dir "$dest" \
        --mode "$mode" \
        --model "$model" \
        --thinking-level "$thinking" \
        --temperature 0.0 \
        --service-tier flex \
        --workers "$WORKERS" || echo "verify_k${k}_${arm}: run_pv exited $? (completeness gap or error)"
      state=$(arm_state "$dest" "$n_union")
      echo "verify_k${k}_${arm}: $state after the run"
      [ "$state" = complete ] || incomplete=$((incomplete + 1))
    done
  done
  if [ "$incomplete" -gt 0 ]; then
    echo "ARMS INCOMPLETE: $incomplete arm(s) not at their union count $(date -Is)"
    exit 2
  fi
  echo "ALL ARMS DONE $(date -Is)"
fi
