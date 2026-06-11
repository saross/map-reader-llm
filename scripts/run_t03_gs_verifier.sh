#!/usr/bin/env bash
# ============================================================================
# run_t03_gs_verifier.sh
# ----------------------------------------------------------------------------
# GS characterisation of the deployment champion's proposer (Session 112;
# Shawn approved <= US$5, 2026-06-11): the text HIGH T=0.3 proposer was
# deployed on the 55 maps (T03-k3 oracle 0.8476, board Tier 1) but was never
# verifier-characterised on GS — the only gap in the transfer table
# (results/55map-leaderboard/gs-vs-55map-transfer.md).
#
# DESIGN: first-5 passes of the on-disk flash-high-text-n5/text-t0.3 study
# (10 complete passes; first-N rule) -> 1-of-5 union (current merge_passes,
# contributing_passes retained) -> crops -> carry-forward verifier
# (gemini-3-flash, adversarial text, minimal, T=0.0, n=1, realtime flex)
# with cleanup-on-strict-failure -> $0 post-hoc k x prob_t sweep.
#
# COST: union expected ~2,500-3,500 crops x $0.000697 ~= US$1.8-2.5 flex
# (cap $5). Stages U/E are $0 and run first so the approval sheet carries
# the EXACT crop count before any API call; stage V is gated on MODE=full.
#
# Usage (zbook):
#   bash scripts/run_t03_gs_verifier.sh prep   # merge + extract, $0
#   bash scripts/run_t03_gs_verifier.sh full   # the verifier leg (gated)
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/.."

MODE="${1:-prep}"
WORKERS="${WORKERS:-14}"
PY=.venv/bin/python
OUT=outputs/h11/pv-diag-384
VF_CONFIG=prompts/configs/verify_adversarial-text.json
UNION=$OUT/consensus/flash-high-text-t03-1of5.geojson

case "$MODE" in prep|full) ;; *) echo "usage: $0 prep|full"; exit 2 ;; esac

if [ ! -f "$UNION" ]; then
    echo "=== Stage U: first-5 T0.3 union (first-N rule) ==="
    $PY scripts/merge_passes.py --input-dir "$OUT/flash-high-text-n5/text-t0.3" \
        --passes 1,2,3,4,5 --threshold 1 --output "$UNION"
fi
if [ ! -f "$OUT/crops/flash-high-text-t03-1of5/candidate_manifest.json" ]; then
    echo "=== Stage E: crops ==="
    $PY scripts/run_pv.py extract --proposer "$UNION" \
        --output-dir "$OUT/crops/flash-high-text-t03-1of5" --padding 75
fi
n=$($PY -c "import json; print(len(json.load(open('$OUT/crops/flash-high-text-t03-1of5/candidate_manifest.json'))['candidates']))")
printf "union crops: %s -> est verifier cost ~\$%.2f flex\n" "$n" \
    "$(echo "$n * 0.000697" | bc -l)"

[ "$MODE" = prep ] && { echo "prep complete — no API calls made"; exit 0; }

echo "=== Stage V: carry-forward verifier (n=1, flex) ==="
$PY scripts/run_pv.py verify --crops-dir "$OUT/crops/flash-high-text-t03-1of5" \
    --verifier-config "$VF_CONFIG" --mode realtime --service-tier flex \
    --iterations 1 --workers "$WORKERS" \
    --output-dir "$OUT/verified/flash-high-text-t03-1of5" \
    || $PY scripts/run_pv.py cleanup \
        --crops-dir "$OUT/crops/flash-high-text-t03-1of5" \
        --verified-dir "$OUT/verified/flash-high-text-t03-1of5" \
        --verifier-config "$VF_CONFIG" --service-tier flex --workers 4
echo "=== done — next ($0): k x prob_t sweep + 50 m comparator for the transfer table ==="
