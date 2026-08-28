#!/usr/bin/env bash
# Gemini 3.7 Flash family screen — self-gating overnight driver.
#
# Card: planning/gemini37-screen-2026-08-28.md (PI go 2026-08-28:
# "run it overnight... if nothing untoward arises, go with the full
# run"). The first probe attempt hit sustained 503 UNAVAILABLE
# (launch-week congestion), so this driver GATES itself:
#
#   1. PROBE (5 tiles), up to 6 attempts spaced 30 min. Pass requires
#      5/5 processed AND implied all-in <= $25 (the card's clause;
#      thinking volume measured from the probe meta at 3.7 flex rates).
#      All attempts failing => exit 0 having spent ~nothing.
#   2. K=5 proposer (Phase-B pattern, .done markers, idempotent).
#   3. Union (image_b union chain is 55map-specific; this uses the
#      stride chain via stride_prepare-style flow — deferred to the
#      morning session UNLESS trivially mechanical: the driver stops
#      after the proposer; union+verifier run in the morning WITH the
#      documented ceiling (verifier <= 4,500 calls) — recorded here so
#      the morning launch is mechanical.
set -uo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
CONFIG=prompts/configs/detect_brief-text.json
MANIFEST=inputs/grid-2026-08-18/grid_384_ov192_manifest.json
TILES=inputs/tiles_384_ov192
OUTROOT=outputs/gemini37-screen-2026-08-28
MODEL_ARGS="--model gemini-3.7-flash --thinking-level low"

probe_ok=0
for attempt in 1 2 3 4 5 6; do
  pdir=$OUTROOT/probe-gate-$attempt
  echo "=== probe attempt $attempt $(date -Is)"
  $PY scripts/4_detect_mounds_batch.py \
      --config "$CONFIG" \
      --manifest inputs/image-b-gs-2026-08-28/probe_manifest.json \
      --tiles-dir "$TILES" \
      --output-dir "$pdir" \
      --mode realtime --service-tier flex --temperature 0.7 \
      $MODEL_ARGS --workers 5 >/dev/null 2>&1 || true
  if $PY - "$pdir" <<'PYEOF'
import glob, json, sys
pdir = sys.argv[1]
metas = glob.glob(pdir + "/*.meta.json")
if not metas:
    raise SystemExit(1)
d = json.loads(open(metas[0]).read())
per = d["per_item_metadata"]
items = per if isinstance(per, list) else list(per.values())
ok = [i for i in items if not i.get("response_empty")]
if len(ok) < 5:
    print(f"probe gate: only {len(ok)}/5 succeeded")
    raise SystemExit(1)
u = d["usage_stats"]
think_pt = u["total_thoughts_tokens"] / 5
inp_pt = u["total_input_tokens"] / 5
out_pt = u["total_output_tokens"] / 5
# 3.7 flex rates (fetched 2026-08-28): in $0.375/M, out+think $1.875/M
per_call = (inp_pt * 0.375 + (out_pt + think_pt) * 1.875) / 1e6
proposer = per_call * 6990
all_in = proposer + 3.1  # verifier ceiling allowance
print(f"probe gate: 5/5 ok; think/tile {think_pt:.0f}; "
      f"proposer est ${proposer:.2f}; all-in est ${all_in:.2f}")
if all_in > 35:
    print("probe gate: EXCEEDS the $35 clause (card $25 + PI +$10, 2026-08-28) — stopping")
    raise SystemExit(2)
PYEOF
  then probe_ok=1; break; fi
  [ "$attempt" -lt 6 ] && sleep 1800
done

if [ "$probe_ok" -ne 1 ]; then
  echo "PROBE GATE NOT PASSED — no full run tonight $(date -Is)"
  exit 0
fi

for run in 1 2 3 4 5; do
  out=$OUTROOT/g384_ov192_g37/run_$run
  if [ -f "$out/.done" ]; then
    echo "=== run_$run already done, skipping"
    continue
  fi
  echo "=== run_$run start $(date -Is)"
  if $PY scripts/4_detect_mounds_batch.py \
      --config "$CONFIG" \
      --manifest "$MANIFEST" \
      --tiles-dir "$TILES" \
      --output-dir "$out" \
      --mode realtime --service-tier flex --temperature 0.7 \
      $MODEL_ARGS --workers "${WORKERS:-12}"; then
    touch "$out/.done"
    echo "=== run_$run done $(date -Is)"
  else
    echo "FAILED run_$run $(date -Is)"
  fi
done
echo "ALL PASSES DONE $(date -Is)"
