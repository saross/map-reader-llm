#!/usr/bin/env bash
# ============================================================================
# finish_flash35_tranche.sh
# ----------------------------------------------------------------------------
# Session 112: finish the Flash 3.5 tranche after V1's strict-mode exit
# (1131/1132 verified; one candidate lost to a 503 burst). Stages P/U/E are
# complete on disk. This script: patches V1 via run_pv.py cleanup, runs V2
# and V3 with the same cleanup-on-strict-failure policy (aggressive
# failed-candidate pursuit, Shawn 2026-06-10), and gates E2 at 1,939
# candidates. Appends to the tranche log and emits the standard completion
# marker.
#
# Usage (on zbook): bash scripts/finish_flash35_tranche.sh
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/.."

WORKERS="${WORKERS:-14}"
PY=.venv/bin/python
OUT=outputs/flash35-pv-2x2
F35=gemini-3.5-flash
VF_CONFIG=prompts/configs/verify_adversarial-text.json
F3_PASSES=outputs/h11/pv-diag-384/text-n10/text-t0.7

verify_with_cleanup() {  # crops_dir out_dir [extra flags...]
    local crops="$1" outdir="$2"; shift 2
    if [ -f "$outdir/probabilities.json" ]; then
        echo "verify: $outdir exists — going straight to cleanup check"
    else
        $PY scripts/run_pv.py verify --crops-dir "$crops" \
            --verifier-config "$VF_CONFIG" --mode realtime --service-tier flex \
            --iterations 1 --workers "$WORKERS" --output-dir "$outdir" "$@" \
            && return 0
        echo "verify: strict-mode exit for $outdir — running cleanup"
    fi
    $PY scripts/run_pv.py cleanup --crops-dir "$crops" --verified-dir "$outdir" \
        --verifier-config "$VF_CONFIG" --service-tier flex --workers 4 "$@"
}

echo "=== Stage V1 (cleanup): patch the missing candidate ==="
verify_with_cleanup "$OUT/crops" "$OUT/verified-f3vf" || { echo "V1 cleanup FAILED"; exit 1; }

echo "=== Stage V2: F3.5 verifier over the F3.5 union ==="
verify_with_cleanup "$OUT/crops" "$OUT/verified-f35vf" --model "$F35" \
    || { echo "V2 FAILED after cleanup"; exit 1; }

echo "=== Stage E2: regenerate the F3 1-of-10 union WITH contributing_passes ==="
if [ ! -f "$OUT/min-f3-crops/candidate_manifest.json" ]; then
    $PY scripts/merge_passes.py --input-dir "$F3_PASSES" --threshold 1 \
        --passes 1,2,3,4,5,6,7,8,9,10 \
        --output "$OUT/consensus/f3-min-text-1of10-with-passes.geojson"
    $PY scripts/run_pv.py extract \
        --proposer "$OUT/consensus/f3-min-text-1of10-with-passes.geojson" \
        --output-dir "$OUT/min-f3-crops" --padding 75
fi
n_f3=$($PY -c "import json; print(len(json.load(open('$OUT/min-f3-crops/candidate_manifest.json'))['candidates']))")
if [ "$n_f3" != "1939" ]; then
    echo "GATE FAIL: F3 1of10 crops $n_f3 != 1939 — aborting stage V3"; exit 1
fi

echo "=== Stage V3: F3.5 verifier over the F3 1-of-10 union ==="
verify_with_cleanup "$OUT/min-f3-crops" "$OUT/min-f3-verified-f35vf" --model "$F35" \
    || { echo "V3 FAILED after cleanup"; exit 1; }

echo "=== Tranche API stages complete ==="
