#!/usr/bin/env bash
# ============================================================================
# run_flash35_tranche1.sh
# ----------------------------------------------------------------------------
# Flash 3.5 exploratory tranche 1 (Session 111, Shawn-approved design:
# 2x2 proposer-model x verifier-model factorial, MINIMAL thinking).
#
# QUESTION: is gemini-3.5-flash a better bare proposer and/or verifier than
# gemini-3-flash, at the cost-optimal (minimal-thinking) operating point?
#
# DESIGN — the 2x2 (all text track, 384 px, 487-tile Era-2 manifest,
# T=0.7 proposer / T=0.0 verifier, MINIMAL thinking, n=1 verifier,
# detect_brief-text.json + verify_adversarial-text.json BYTE-IDENTICAL to
# the Flash 3 comparator; ONLY --model overrides differ):
#
#                      | F3 verifier        | F3.5 verifier
#   F3 proposer (min6) | 0.8708 (ON DISK)   | stage V3 (~$3.3)
#   F3.5 proposer      | stage V1 (~$1.1)   | stage V2 (~$3.3)
#
#   + stage P: 5 x F3.5 proposer passes (~$12.3) -> bare-consensus sweep free
#
# FLASH 3 REFERENCES: min6 PV 0.8708 (4of5/pt0.15, MCC 0.787); min11 0.8835;
# pool recall ceiling 0.920 (results/verifier-robustness/
# pool_recall_ceilings.json). Tranche 2 (pending results): +5 minimal passes
# -> the min11 analogue.
#
# COST (realtime FLEX, June 2026 rates: F3.5 $0.75/$4.50, F3 $0.25/$1.50
# per 1M in/out; verifier in/out 1792/163 tok/call measured from the opmax
# run.meta): ~2,435 + ~1,600 + ~1,600 + 1,593 = ~7,230 calls, ~US$20 total.
#
# MODEL STRING: gemini-3.5-flash (verified available via models.list,
# 2026-06-10; the driver's _resolve_model_name re-checks at launch).
# RISK: minimal thinking support on 3.5 unconfirmed -> run MODE=smoke first
# (10 tiles, ~$0.06); the launch-time intent guard prompts before spend.
#
# Usage (on zbook):
#   bash scripts/run_flash35_tranche1.sh dry     # validate configs, no calls
#   bash scripts/run_flash35_tranche1.sh smoke   # 10-tile proposer smoke
#   bash scripts/run_flash35_tranche1.sh full    # the real tranche (gated)
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-10 | Apache 2.0
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${1:-dry}"
WORKERS="${WORKERS:-14}"   # zbook cap: leave 2 of 16 cores free
PY=.venv/bin/python
OUT=outputs/flash35-pv-2x2
F35=gemini-3.5-flash
MANIFEST=inputs/tiles_384/full_evaluation_manifest.json
PROP_CONFIG=prompts/configs/detect_brief-text.json
VF_CONFIG=prompts/configs/verify_adversarial-text.json
MIN6_UNION=outputs/h11/pv-diag-384/consensus/flash-minimal-text-t07-1of5.geojson

case "$MODE" in dry|smoke|full) ;; *) echo "usage: $0 dry|smoke|full"; exit 2 ;; esac

DETECT_FLAGS=(--config "$PROP_CONFIG" --manifest "$MANIFEST"
              --tiles-dir inputs/tiles_384 --tile-size 384
              --model "$F35" --temperature 0.7 --thinking-level minimal
              --mode realtime --service-tier flex --workers "$WORKERS")
[ "$MODE" = dry ] && DETECT_FLAGS+=(--dry-run)
[ "$MODE" = smoke ] && DETECT_FLAGS+=(--limit 10)

echo "=== Stage P: 5 x F3.5 minimal T0.7 proposer passes ($MODE) ==="
PASSES=5
[ "$MODE" = smoke ] && PASSES=1
for n in $(seq 1 "$PASSES"); do
    echo "--- pass $n/$PASSES ---"
    $PY scripts/4_detect_mounds_batch.py "${DETECT_FLAGS[@]}" \
        --output-dir "$OUT/proposer/run_$n"
done

if [ "$MODE" != full ]; then
    echo "=== $MODE complete — stages U/E/V1/V2/V3 run only in full mode ==="
    exit 0
fi

echo "=== Stage U: 1-of-5 union (vote counts retained for the k x pt sweep) ==="
mkdir -p "$OUT/consensus"
$PY scripts/merge_passes.py --input-dir "$OUT/proposer" --threshold 1 \
    --output "$OUT/consensus/flash35-min-text-1of5.geojson"

echo "=== Stage E: candidate crops from the F3.5 union ==="
$PY scripts/run_pv.py extract --proposer "$OUT/consensus/flash35-min-text-1of5.geojson" \
    --output-dir "$OUT/crops" --padding 75

echo "=== Stage V1: F3 carry-forward verifier over the F3.5 union ==="
$PY scripts/run_pv.py verify --crops-dir "$OUT/crops" \
    --verifier-config "$VF_CONFIG" --mode realtime --service-tier flex \
    --iterations 1 --workers "$WORKERS" --output-dir "$OUT/verified-f3vf"

echo "=== Stage V2: F3.5 verifier over the F3.5 union ==="
$PY scripts/run_pv.py verify --crops-dir "$OUT/crops" \
    --verifier-config "$VF_CONFIG" --model "$F35" --mode realtime \
    --service-tier flex --iterations 1 --workers "$WORKERS" \
    --output-dir "$OUT/verified-f35vf"

echo "=== Stage E2: regenerate min6 crops (gate: expect 1,593 candidates) ==="
$PY scripts/run_pv.py extract --proposer "$MIN6_UNION" \
    --output-dir "$OUT/min6-crops" --padding 75
n_min6=$($PY -c "import json; print(len(json.load(open('$OUT/min6-crops/candidate_manifest.json'))['candidates']))")
if [ "$n_min6" != "1593" ]; then
    echo "GATE FAIL: min6 crops $n_min6 != 1593 — aborting stage V3"; exit 1
fi

echo "=== Stage V3: F3.5 verifier over the EXISTING F3 min6 union ==="
$PY scripts/run_pv.py verify --crops-dir "$OUT/min6-crops" \
    --verifier-config "$VF_CONFIG" --model "$F35" --mode realtime \
    --service-tier flex --iterations 1 --workers "$WORKERS" \
    --output-dir "$OUT/min6-verified-f35vf"

echo "=== Tranche 1 API stages complete ==="
echo "Next ($0 analysis): k x prob_t sweep per 2x2 cell + bare-consensus"
echo "sweep of the F3.5 pool (score_min_thinking_pv.py pattern)."
