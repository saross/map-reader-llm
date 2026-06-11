#!/usr/bin/env bash
# ============================================================================
# run_min11_uplift_55map.sh
# ----------------------------------------------------------------------------
# The min6 -> min11 production uplift (Session 112; Shawn agreed 2026-06-11,
# final approval pending): does PASS COUNT close the -0.030 thinking gap at
# deployment (Obs 362)? Adds 5 minimal T=0.7 passes to the existing
# 55maps-text-min-generalisation proposer (runs 1-5 on disk, 8,541 tiles
# each), then verifies the >=3-of-10 band of the 10-pass union once —
# the n-of-10 x prob_t sweep is free post hoc.
#
# CONFIG CONTROL: byte-identical detect_brief-text.json + the SAME CLI
# overrides as the original run (gemini-3-flash, minimal, T=0.7); only the
# pass indices are new (first-N lineage: runs 1-5 = TM, 6-10 = uplift).
#
# COST (measured basis — TM cost_manifest: 25.7M in / 1.95M out tokens per
# pass => ~$9.40/pass at FLEX rates; the manifest's $18.67/pass figure is
# STANDARD pricing):
#   P: 5 passes x ~$9.40            ~= $47
#   V: >=3of10 band ~19,000 crops    ~= $13   (full union ~34,000 ~= $24)
#   TOTAL                            ~= $60 flex (band) / ~$71 (full union)
#
# Resilience: pass-skip on re-entry, resume x4 per partial pass
# (8,524/8,541 floor = the TM run's own 0.3% failure-rate tolerance),
# cleanup-on-strict-failure for the verifier leg.
#
# Usage (zbook):
#   bash scripts/run_min11_uplift_55map.sh dry     # validate, no calls
#   bash scripts/run_min11_uplift_55map.sh smoke   # 20-tile pass smoke
#   bash scripts/run_min11_uplift_55map.sh full    # the real uplift (gated)
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/.."

MODE="${1:-dry}"
WORKERS="${WORKERS:-14}"
PY=.venv/bin/python
TM=outputs/55maps-text-min-generalisation/proposer/detect_brief-text
OUT=outputs/55maps-text-min-n10-uplift
MANIFEST=inputs/tiles_384_55maps/full_evaluation_manifest.json
PROP_CONFIG=prompts/configs/detect_brief-text.json
VF_CONFIG=prompts/configs/verify_adversarial-text.json

case "$MODE" in dry|smoke|full) ;; *) echo "usage: $0 dry|smoke|full"; exit 2 ;; esac

DETECT_FLAGS=(--config "$PROP_CONFIG" --manifest "$MANIFEST"
              --tiles-dir inputs/tiles_384_55maps --tile-size 384
              --temperature 0.7 --thinking-level minimal
              --mode realtime --service-tier flex --workers "$WORKERS")
[ "$MODE" = dry ] && DETECT_FLAGS+=(--dry-run)
[ "$MODE" = smoke ] && DETECT_FLAGS+=(--limit 20)

tiles_done() {
    $PY - "$1" <<'PYEOF'
import json, sys, glob
gj = glob.glob(sys.argv[1] + "/detections*.geojson")
print(len(json.load(open(gj[0])).get("processed_tiles", [])) if gj else 0)
PYEOF
}

echo "=== Stage P: passes 6-10 (minimal T0.7, $MODE) ==="
PASSES="6 7 8 9 10"
[ "$MODE" = smoke ] && PASSES="6"
for n in $PASSES; do
    echo "--- pass $n ---"
    if [ "$MODE" = full ] && [ "$(tiles_done "$OUT/proposer/run_$n")" -ge 8541 ]; then
        echo "pass $n: already complete — skipping"; continue
    fi
    rc=0
    for attempt in 1 2 3 4 5; do
        rc=0
        $PY scripts/4_detect_mounds_batch.py "${DETECT_FLAGS[@]}" \
            --output-dir "$OUT/proposer/run_$n" || rc=$?
        [ "$rc" != 2 ] && break
        [ "$MODE" != full ] && break
        echo "pass $n attempt $attempt: partial (exit 2) — resuming"
    done
    if [ "$rc" = 2 ] && [ "$MODE" = full ]; then
        nd=$(tiles_done "$OUT/proposer/run_$n")
        if [ "$nd" -ge 8524 ]; then
            echo "pass $n: partial after 5 attempts ($nd/8541) — accepted, documented"
        else
            echo "pass $n: only $nd/8541 — aborting"; exit 2
        fi
    elif [ "$rc" != 0 ]; then
        echo "pass $n: fatal (exit $rc) — aborting"; exit "$rc"
    fi
done
[ "$MODE" != full ] && { echo "=== $MODE complete ==="; exit 0; }

echo "=== Stage U: 10-pass union (TM runs 1-5 + uplift 6-10, first-N) ==="
mkdir -p "$OUT/proposer-all" "$OUT/consensus"
for n in 1 2 3 4 5; do ln -sfn "$(pwd)/$TM/run_$n" "$OUT/proposer-all/run_$n"; done
for n in 6 7 8 9 10; do ln -sfn "$(pwd)/$OUT/proposer/run_$n" "$OUT/proposer-all/run_$n"; done
$PY scripts/merge_passes.py --input-dir "$OUT/proposer-all" \
    --passes 1,2,3,4,5,6,7,8,9,10 --threshold 1 \
    --output "$OUT/consensus/text-min-1of10.geojson"
$PY scripts/merge_passes.py --input-dir "$OUT/proposer-all" \
    --passes 1,2,3,4,5,6,7,8,9,10 --threshold 3 \
    --output "$OUT/consensus/text-min-3of10.geojson"

echo "=== Stage E: crops for the >=3-of-10 band ==="
# 55-map sources (NOT the GS defaults): the original TM crops record
# rasters_dir inputs/rasters/Russian1981_32635 + tiles_384_55maps.
$PY scripts/run_pv.py extract --proposer "$OUT/consensus/text-min-3of10.geojson" \
    --output-dir "$OUT/crops-3of10" --padding 75 \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --tiles-dir inputs/tiles_384_55maps
n_band=$($PY -c "import json; print(len(json.load(open('$OUT/crops-3of10/candidate_manifest.json'))['candidates']))")
if [ "$n_band" -lt 10000 ]; then
    echo "GATE FAIL: band crops $n_band < 10000 (expected ~16,500) — aborting V"
    exit 1
fi
echo "band crops: $n_band (gate ok)"

echo "=== Stage V: carry-forward verifier over the band (n=1, flex) ==="
$PY scripts/run_pv.py verify --crops-dir "$OUT/crops-3of10" \
    --verifier-config "$VF_CONFIG" --mode realtime --service-tier flex \
    --iterations 1 --workers "$WORKERS" --output-dir "$OUT/verified-3of10" \
    || $PY scripts/run_pv.py cleanup --crops-dir "$OUT/crops-3of10" \
        --verified-dir "$OUT/verified-3of10" --verifier-config "$VF_CONFIG" \
        --service-tier flex --workers 4
echo "=== Uplift API stages complete ==="
echo "Next ($0): k(3..10) x prob_t sweep vs canonical GT @ 50 m; add the cell"
echo "to the 55-map board (does pass count close the -0.030 thinking gap?)."
