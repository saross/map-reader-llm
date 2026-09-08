#!/bin/bash
# Verifier-stage refresh on the E71-recovered candidate sets (S150, 2026-09-08)
# ===========================================================================
#
# Re-runs the three uncited text-only adversarial verifier stages whose
# candidate sets were built from pre-recovery passes (recovery-consistency
# audit, reports/recovery-consistency-audit-2026-09-08.md § 3), into NEW dated
# stage directories beside the originals (archive-never-delete; the originals
# stay as the pre-recovery record). Recipe = scripts/run_verifier_matrix.sh:
# extract crops (padding 75) -> verify (verify_adversarial-text: Flash,
# minimal thinking, T 0.0, one iteration per candidate; real-time, flex) ->
# completeness check -> 2D sweep at 20/30/40/50 m.
#
# Card: planning/verifier-stage-refresh-2026-09-08.md (gates, cost, stop states).
# PI budget ceiling: US$20 (approved 2026-09-08). Estimate: 6,357 candidates at
# the measured ~US$0.0014/crop ~= US$8.9.
#
# Usage (sapphire):
#   setsid -f bash -c "bash scripts/run_verifier_stage_refresh.sh > /tmp/vsr.log 2>&1" < /dev/null
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
PYTHON=".venv/bin/python"
PV="scripts/run_pv.py"
SWEEP="scripts/sweep_f1_greedy_pv.py"
VERIFIER_CONFIG="prompts/configs/verify_adversarial-text.json"
BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
BUDGET_USD="${BUDGET_USD:-20}"
export PYTHONUNBUFFERED=1

# label | candidate geojson | new stage directory | expected candidates
STAGES=(
  "pv-diag-image-t0.0-v1|outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/consensus/consensus_t1.geojson|outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10-recovery-2026-09-08|889"
  "pv-diag-text-t0.0-v1|outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/consensus/consensus_t1.geojson|outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/verified-v1-n3-recovery-2026-09-08|1319"
  "e47-1of5-v1|outputs/h11/e47-propose-brief/consensus/flash-high-text-1of5-recovery-2026-09-08.geojson|outputs/h11/e47-propose-brief/verified/flash-high-text-1of5-recovery-2026-09-08|4149"
)

spent=0
echo "Verifier-stage refresh — started $(date -u +%Y-%m-%dT%H:%M:%SZ) — budget US\$$BUDGET_USD"
for spec in "${STAGES[@]}"; do
  IFS='|' read -r label candidates stage expected <<< "$spec"
  crops="$stage/crops"
  echo ""; echo "=== $label  ($expected candidates)  $(date -u +%H:%M:%SZ)"
  n_cand=$($PYTHON -c "import json,sys;print(len(json.load(open(sys.argv[1]))['features']))" "$candidates")
  if [ "$n_cand" != "$expected" ]; then echo "STOP: $candidates has $n_cand candidates, card says $expected"; exit 2; fi

  if [ -f "$crops/candidate_manifest.json" ]; then echo "  [extract] cached"; else
    $PYTHON $PV extract --proposer "$candidates" --output-dir "$crops" --padding 75 || { echo "STOP: extract failed"; exit 2; }
  fi

  if [ -f "$stage/probabilities.json" ]; then echo "  [verify] cached"; else
    rc=0
    $PYTHON $PV verify --crops-dir "$crops" --verifier-config "$VERIFIER_CONFIG" --output-dir "$stage" \
      --mode realtime --workers 20 --service-tier flex --no-strict || rc=$?
    echo "  [verify] exit $rc"
  fi
  # completeness: every candidate verified, else one cleanup pass, then stop if still short
  got=$($PYTHON -c "import json,sys;print(json.load(open(sys.argv[1])).get('total_results') or 0)" "$stage/probabilities.json")
  if [ "$got" != "$expected" ]; then
    echo "  [verify] $got/$expected verified — running cleanup"
    $PYTHON $PV cleanup --crops-dir "$crops" --verified-dir "$stage" --verifier-config "$VERIFIER_CONFIG" --service-tier flex --workers 10 || true
    got=$($PYTHON -c "import json,sys;print(json.load(open(sys.argv[1])).get('total_results') or 0)" "$stage/probabilities.json")
    [ "$got" != "$expected" ] && { echo "STOP: $label incomplete after cleanup ($got/$expected)"; exit 3; }
  fi
  cost=$($PYTHON -c "import json,sys;print((json.load(open(sys.argv[1])).get('cost_estimate') or {}).get('total_cost_usd') or 0)" "$stage/run.meta.json")
  spent=$($PYTHON -c "print(round($spent + $cost, 4))")
  echo "  [verify] complete: $got/$expected, stage cost US\$$cost, cumulative US\$$spent"
  if $PYTHON -c "import sys; sys.exit(0 if $spent > $BUDGET_USD else 1)"; then echo "STOP: budget exceeded"; exit 4; fi

  if [ -f "$stage/sweep_2d.json" ]; then echo "  [sweep] cached"; else
    $PYTHON $SWEEP --config "$label" --crops-dir "$crops" --verified-dir "$stage" --output "$stage/sweep_2d.json" \
      --bounds "$BOUNDS" --buffer-m 20 30 40 50 || { echo "STOP: sweep failed"; exit 2; }
  fi
  echo "  DONE $label"
done
echo ""; echo "ALL DONE — cumulative US\$$spent — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
