#!/usr/bin/env bash
# ============================================================================
# run_flash35_tranche1.sh
# ----------------------------------------------------------------------------
# Flash 3.5 exploratory tranche (Session 111, Shawn-approved 2026-06-10:
# single ~US$34 n=10-first design — "verify once at n=10, derive n=5
# post-hoc"; approval: "I approve this plan, ca. $34 single-tranche design
# unless the smoke test throws up a serious issue").
#
# QUESTION: is gemini-3.5-flash a better proposer and/or verifier than
# gemini-3-flash at the cost-optimal (minimal-thinking) operating point?
#
# DESIGN — 2 x 2 x 2 (proposer model x verifier model x n in {5,10});
# all text track, 384 px, 487-tile Era-2 manifest, T=0.7 proposer /
# T=0.0 verifier, MINIMAL thinking, n=1 verifier. Configs BYTE-IDENTICAL
# to the Flash 3 comparator (detect_brief-text.json +
# verify_adversarial-text.json); ONLY --model overrides differ.
#
# The n=5 cells are derived POST-HOC from each verified 10-pass union via
# contributing_passes (first-5 rule) — validated on the flash-high lineage
# (results/verifier-robustness/first5of10-validation/validation.json):
# geometry reproduces to 0.07 m, but the derivation carries a small
# systematic +0.005..+0.011 F1 effect vs a true 5-pass merge, so ALL n=5
# comparisons are METHOD-MATCHED (the F3 references are derived
# first-5-of-10 from their own verified 10-pools, $0, analysis stage).
#
#                      | F3 verifier            | F3.5 verifier
#   F3 proposer        | on disk (min11 0.8835; | stage V3 (~$4.0)
#   (text-n10 1of10)   |  derived-5 in analysis)|
#   F3.5 proposer      | stage V1 (~$1.4)       | stage V2 (~$4.2)
#   (new, 10 passes)   |                        |
#
# F3 references: min11 0.8835 (6of10/pt0.2); derived-first5 references
# computed in the analysis stage; F3 pool recall ceiling 0.920.
#
# COST (realtime FLEX, June 2026 rates: F3.5 $0.75/$4.50, F3 $0.25/$1.50
# per 1M in/out; verifier 1792 in / 163 out tok/call measured from the
# opmax run.meta): P 4,870 + V1 ~2,000 + V2 ~2,000 + V3 1,939 ~= 10,800
# calls, ~US$34 total (P ~$24.6, V1 ~$1.4, V2 ~$4.2, V3 ~$4.0).
#
# MODEL STRING: gemini-3.5-flash (verified available via models.list,
# 2026-06-10; the driver's _resolve_model_name re-checks at launch).
# RISK: minimal-thinking support on 3.5 unconfirmed -> MODE=smoke first
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
F3_PASSES=outputs/h11/pv-diag-384/text-n10/text-t0.7

case "$MODE" in dry|smoke|full) ;; *) echo "usage: $0 dry|smoke|full"; exit 2 ;; esac

DETECT_FLAGS=(--config "$PROP_CONFIG" --manifest "$MANIFEST"
              --tiles-dir inputs/tiles_384 --tile-size 384
              --model "$F35" --temperature 0.7 --thinking-level minimal
              --mode realtime --service-tier flex --workers "$WORKERS")
[ "$MODE" = dry ] && DETECT_FLAGS+=(--dry-run)
[ "$MODE" = smoke ] && DETECT_FLAGS+=(--limit 10)

echo "=== Stage P: 10 x F3.5 minimal T0.7 proposer passes ($MODE) ==="
PASSES=10
[ "$MODE" = smoke ] && PASSES=1
# Driver exit codes: 0 = clean, 1 = setup error (abort), 2 = partial failure
# (>=1 failed tile). AGGRESSIVE pursuit of failed tiles (Shawn, 2026-06-10):
# on exit 2, re-invoke up to FOUR more times — the incremental-write resume
# retries exactly the unprocessed/failed tiles, and T=0.7 re-rolls transient
# parse failures. A pass still partial after 5 attempts is tolerated down to
# a 485/487 floor (documented in the log); below the floor we abort.
tiles_done() {
    $PY - "$1" <<'PYEOF'
import json, sys, glob
gj = glob.glob(sys.argv[1] + "/detections-*.geojson")
print(len(json.load(open(gj[0])).get("processed_tiles", [])) if gj else 0)
PYEOF
}

for n in $(seq 1 "$PASSES"); do
    echo "--- pass $n/$PASSES ---"
    # Re-invoking the driver on a COMPLETE pass yields "0 remaining" ->
    # result None -> exit 1 (setup-error semantics) — so skip complete
    # passes up front (resume-safe re-entry after any interruption).
    if [ "$MODE" = full ] && [ "$(tiles_done "$OUT/proposer/run_$n")" -ge 487 ]; then
        echo "pass $n: already complete — skipping"
        continue
    fi
    rc=0
    for attempt in 1 2 3 4 5; do
        rc=0
        $PY scripts/4_detect_mounds_batch.py "${DETECT_FLAGS[@]}" \
            --output-dir "$OUT/proposer/run_$n" || rc=$?
        [ "$rc" != 2 ] && break
        [ "$MODE" != full ] && break
        echo "pass $n attempt $attempt: partial failure (exit 2) — resuming"
    done
    if [ "$rc" = 2 ] && [ "$MODE" = full ]; then
        n_done=$(tiles_done "$OUT/proposer/run_$n")
        if [ "$n_done" -ge 485 ]; then
            echo "pass $n: still partial after 5 attempts ($n_done/487) — accepted, documented"
            rc=0
        else
            echo "pass $n: only $n_done/487 tiles after 5 attempts — aborting"; exit 2
        fi
    fi
    if [ "$rc" != 0 ]; then
        echo "pass $n: fatal error (exit $rc) — aborting"; exit "$rc"
    fi
done

if [ "$MODE" != full ]; then
    echo "=== $MODE complete — stages U/E/V1/V2/V3 run only in full mode ==="
    exit 0
fi

echo "=== Stage U: 1-of-10 union (current merge_passes -> contributing_passes) ==="
mkdir -p "$OUT/consensus"
$PY scripts/merge_passes.py --input-dir "$OUT/proposer" --threshold 1 \
    --passes 1,2,3,4,5,6,7,8,9,10 \
    --output "$OUT/consensus/flash35-min-text-1of10.geojson"

echo "=== Stage E: candidate crops from the F3.5 1-of-10 union ==="
$PY scripts/run_pv.py extract \
    --proposer "$OUT/consensus/flash35-min-text-1of10.geojson" \
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

echo "=== Stage E2: regenerate the F3 1-of-10 union WITH contributing_passes ==="
# Geometry-validated identical to the committed text-1of10.geojson (0.07 m,
# one-to-one, 100% vote agreement) — see first5of10-validation/validation.json.
$PY scripts/merge_passes.py --input-dir "$F3_PASSES" --threshold 1 \
    --passes 1,2,3,4,5,6,7,8,9,10 \
    --output "$OUT/consensus/f3-min-text-1of10-with-passes.geojson"
$PY scripts/run_pv.py extract \
    --proposer "$OUT/consensus/f3-min-text-1of10-with-passes.geojson" \
    --output-dir "$OUT/min-f3-crops" --padding 75
n_f3=$($PY -c "import json; print(len(json.load(open('$OUT/min-f3-crops/candidate_manifest.json'))['candidates']))")
if [ "$n_f3" != "1939" ]; then
    echo "GATE FAIL: F3 1of10 crops $n_f3 != 1939 — aborting stage V3"; exit 1
fi

echo "=== Stage V3: F3.5 verifier over the F3 1-of-10 union ==="
$PY scripts/run_pv.py verify --crops-dir "$OUT/min-f3-crops" \
    --verifier-config "$VF_CONFIG" --model "$F35" --mode realtime \
    --service-tier flex --iterations 1 --workers "$WORKERS" \
    --output-dir "$OUT/min-f3-verified-f35vf"

echo "=== Tranche API stages complete ==="
echo "Next ($0 analysis): k x prob_t sweeps per 2x2 cell at n=10, plus the"
echo "method-matched n=5 derivation (contributing_passes, first-5 rule) for"
echo "BOTH models, plus the F3.5 bare-consensus sweep."
