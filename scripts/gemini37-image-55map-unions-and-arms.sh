#!/usr/bin/env bash
# Gemini 3.7 image, 55-map K = 3: unions, provenance sidecars, crops, arms.
#
# Card: planning/gemini37-image-55map-2026-09-13.md (section 5 steps 3-4).
# Rulings this script implements:
# reports/gemini37-image-55map-deltas-2026-09-13.md section 10.2 — the unions
# are built by stride55_prepare_and_union.py, for comparability with the 3.7
# TEXT arms whose deployment-scale modality contrast this campaign rests on,
# and the pass_provenance block is emitted as a sidecar over the same resolved
# fragment set.
#
# Runbook (the pre-run-review substance):
#   Precondition: all three proposer passes COMPLETE at 24,561/24,561 after the
#     recovery fold, and the pass-1 go/no-go gate PASSED (audited cost
#     <= US$110 and cached share >= 0.70, scripts/audit_proposer_cost.py).
#     This script does not check the gate; the operator does, once.
#   Artefacts:  verifier/<cell>/union_k{1,3}.geojson
#               verifier/<cell>/union_k{1,3}_pass_provenance.json
#               verifier/<cell>/crops_k{1,3}/candidate_manifest.json (+ PNGs,
#                 gitignored)
#               verifier/<cell>/verify_k{1,3}_arm{1,2}/probabilities.json
#                 and run.meta.json
#   Finished:   "ALL ARMS DONE" on stdout, four probabilities.json present.
#   Stop:       set -e — any stage's failure stops the script. The union
#               builder raises CoverageError unless every pass covers the
#               pinned manifest exactly, which is the coverage gate.
#   Partial:    idempotent per stage. A union that exists is rebuilt (cheap,
#               deterministic); an arm whose probabilities.json exists is
#               SKIPPED, so a resumed run never re-spends on a finished arm.
#   Verify:     the operator reads each union's feature count against the
#               sidecar's recorded fragment set, and each arm's run.meta.json
#               items_processed against the union count, before scoring.
#
# The two 3.7 arms run SEQUENTIALLY (PI rule 2026-08-30: never two concurrent
# Gemini 3.7 runs, which inflate each other's 503 retries in the flex queue).
# Arm 1 is Gemini 3 and could overlap, but sequencing all four keeps the
# retry counts per arm interpretable.
#
# Usage (from the campaign worktree on sapphire):
#     bash scripts/gemini37-image-55map-unions-and-arms.sh
#     WORKERS=50 bash scripts/gemini37-image-55map-unions-and-arms.sh
#
# Created: 2026-09-13
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0

set -euo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
OUT=outputs/gemini37-image-55map-2026-09-13
CELL=g384_ov192_55map_g37img
MANIFEST=inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json
TILES=inputs/tiles_384_ov192_55maps
VERIFIER_CONFIG=prompts/configs/verify_adversarial-text.json
VROOT=$OUT/verifier/$CELL
WORKERS=${WORKERS:-50}
PADDING=75

# The two verifier arms, exactly as card section 2 fixes them.
ARM1_MODEL=gemini-3-flash-preview
ARM1_THINKING=minimal
ARM2_MODEL=gemini-3.7-flash
ARM2_THINKING=low

# Stage 0 makes the coverage gate visible in the log rather than only implicit
# in the union builder's CoverageError. Every pass must reach 24,561 distinct
# tiles once its recovery fragments are folded in; a pass that does not is a
# pass whose union would silently under-cover the corpus.
echo "=== stage 0: pass coverage after the recovery fold $(date -Is)"
$PY - "$OUT/$CELL" "$MANIFEST" <<'EOF'
import glob
import json
import os
import sys

cell_dir, manifest_path = sys.argv[1], sys.argv[2]
pinned = set(json.load(open(manifest_path)))
runs = sorted({os.path.basename(d).split("_recovery")[0]
               for d in glob.glob(f"{cell_dir}/run_*")})
worst = 0
for run in runs:
    done: set[str] = set()
    frags = sorted(glob.glob(f"{cell_dir}/{run}/*.tiles.json")
                   + glob.glob(f"{cell_dir}/{run}_recovery*/*.tiles.json"))
    for tj in frags:
        done |= set(json.load(open(tj))["completed"])
    missing = len(pinned - done)
    worst = max(worst, missing)
    print(f"{run}: {len(done)}/{len(pinned)} tiles across {len(frags)} "
          f"fragment(s), {missing} missing")
if worst:
    sys.exit(f"COVERAGE GATE FAIL: {worst} tile(s) missing from some pass")
print("coverage gate OK")
EOF

echo "=== stage 1: unions (stride builder, first-N rule) $(date -Is)"
for k in 1 3; do
  $PY scripts/stride55_prepare_and_union.py \
    --root "$OUT" --cell "$CELL" --manifest "$MANIFEST" --k "$k" --write
done

echo "=== stage 2: provenance sidecars $(date -Is)"
for k in 1 3; do
  $PY scripts/emit_union_pass_provenance.py \
    --root "$OUT" --cell "$CELL" --k "$k" --write
done

echo "=== stage 3: union feature counts $(date -Is)"
for k in 1 3; do
  n=$($PY -c "import json,sys; print(len(json.load(open(sys.argv[1]))['features']))" \
        "$VROOT/union_k$k.geojson")
  echo "union_k$k: $n candidates"
done

echo "=== stage 4: crop extraction $(date -Is)"
for k in 1 3; do
  if [ -f "$VROOT/crops_k$k/candidate_manifest.json" ]; then
    echo "crops_k$k already extracted, skipping"
    continue
  fi
  $PY scripts/run_pv.py extract \
    --proposer "$VROOT/union_k$k.geojson" \
    --output-dir "$VROOT/crops_k$k" \
    --tiles-dir "$TILES" \
    --padding "$PADDING"
done

echo "=== stage 5: four verifier arms, sequentially $(date -Is)"
for k in 1 3; do
  for arm in arm1 arm2; do
    dest=$VROOT/verify_k${k}_${arm}
    if [ -f "$dest/probabilities.json" ]; then
      echo "verify_k${k}_${arm} already done, skipping"
      continue
    fi
    if [ "$arm" = "arm1" ]; then
      model=$ARM1_MODEL; thinking=$ARM1_THINKING
    else
      model=$ARM2_MODEL; thinking=$ARM2_THINKING
    fi
    echo "--- verify_k${k}_${arm}: $model / $thinking $(date -Is)"
    $PY scripts/run_pv.py verify \
      --crops-dir "$VROOT/crops_k$k" \
      --verifier-config "$VERIFIER_CONFIG" \
      --output-dir "$dest" \
      --mode realtime \
      --model "$model" \
      --thinking-level "$thinking" \
      --temperature 0.0 \
      --service-tier flex \
      --workers "$WORKERS"
  done
done

echo "ALL ARMS DONE $(date -Is)"
