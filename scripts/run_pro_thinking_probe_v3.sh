#!/usr/bin/env bash
# ============================================================================
# run_pro_thinking_probe_v3.sh
# ----------------------------------------------------------------------------
# V3 (2026-10-12, 13:10Z): v2's first arm showed what stopped v1. 17 of 20
# flex requests returned 503 UNAVAILABLE ("This model is currently
# experiencing high demand"), which the runner retries with backoff; none
# hit MAX_TOKENS, and the 3 that succeeded had zero thought tokens (as in
# June). 503s are not billed, so v1 and v2 cost cents, not the upper bound
# first estimated (the v2 note below reflects that wrong first reading).
# V3 changes only: the standard tier (the PI's original approval; the flex
# flag is dropped), --max-retries 3 (a 503 can recover, and any MAX_TOKENS
# retry stays bounded), output under v3-<arm>/, and a cost guard that
# stops before the next arm once the runner's own estimates pass US$14
# (worst case about US$20.60 against the PI's cap of US$21.25). Tier
# note: June's text passes ran on flex and its image passes, through the
# cached path, on standard.
#
# V2 (2026-10-12, 13:00Z): v1 (scripts/run_pro_thinking_probe.sh) was
# stopped at 12:53Z during its first arm. The runner retries a response
# whose finish reason is MAX_TOKENS, or that has no content parts, up to
# --max-retries (default 15) times; tonight Pro's thinking used up the
# 8,192-token output budget on most attempts, so 50 tiles took 273
# attempts (upper bound about US$13.84) and the per-request records were
# lost when the run was stopped. V2 changes only: one attempt per tile
# (--max-retries 1; the runner still records an exhausted attempt's tokens
# via log_response), 20 of the 50 tiles (a seeded sample, seed 42), and
# output under v2-<arm>/ beside v1's preserved partial arm. Budget: the
# PI's approval of about US$17 plus a 25 % overrun (US$21.25); v2 adds at
# most about US$5.30 (100 calls).
#
# What follows is v1's header, unchanged except for the file name above.
# ----------------------------------------------------------------------------
# Does Gemini 3.1 Pro think at thinking_level HIGH, and does temperature
# switch that thinking on or off?
#
# WHY: the genuine-Pro HIGH passes of 2026-06-03 (n1-pro-rerun-384,
# T = 0.0) record zero thought tokens, and the June 2026 invoice confirms
# the zeros are real (reports/manipulation-check-2026-10-05.md, section D,
# revised 2026-10-12). h6 A-06 reads "temperature is the driver" from a
# contrast of those T = 0.0 passes with March T = 0.7 Pro HIGH passes whose
# thinking was never recorded. This probe measures delivered thinking at
# each temperature on today's service (PI approval 2026-10-12, ruling D61
# (4) in planning/pi-decisions-2026-09-20.md).
#
# PARAMETER CONTROL: every flag below matches scripts/run_n1_pro_rerun.sh
# (the June run): same configs (detect_brief-text.json for text,
# library_plus-hp.json for image), same model override (gemini-3.1-pro,
# resolved to gemini-3.1-pro-preview), thinking HIGH, real-time on the
# flex tier, context caching on, 384 px tiles. Only temperature varies
# between arms within a modality. The tiles are a seeded sample of 50 of
# the 487 gold-standard 384 px tiles (random.Random(42).sample over the
# sorted manifest), the same 50 for every arm. --allow-inert-fields is
# the runner's documented switch for reproducing a historical run as sent:
# the text config lists examples that a text-only request never transmits
# (the guard postdates June); the payload is unchanged.
#
# LIMITS: this measures the model as served today (version
# 3.1-pro-preview-01-2026 on 2026-10-12), not as served in March or June;
# same-model drift is a standing condition (Obs 508). It can show whether
# temperature gates Pro's thinking now; it cannot prove what the March
# passes did.
#
# API: 5 arms x 50 tiles = 250 real-time flex calls. Worst case about
# US$8.50 if Pro thinks as much as Flash HIGH (about 4,100 thought tokens
# per request); well under US$3 if it does not.
#
# Usage (from the repository root; writes its own pid file and log):
#   nohup bash scripts/run_pro_thinking_probe.sh > /dev/null 2>&1 < /dev/null &
#
# Author: Shawn Ross & Claude (Anthropic), Session 163, 2026-10-12
# ============================================================================
set -uo pipefail

cd "$(dirname "$0")/.."  # repo root
PY=.venv/bin/python
MODEL=gemini-3.1-pro
BASE=outputs/pro-thinking-probe-2026-10-12
MANIFEST="$BASE/tiles-20-of-50-seed42.json"
TILES_DIR=inputs/tiles_384
WORKERS=10
LOG="$BASE/_run_log_v3.txt"
mkdir -p "$BASE"
echo $$ > "$BASE/probe-v3.pid"

echo "=== $(date -u +%FT%TZ) pro-thinking-probe v3 LAUNCH (model=$MODEL, standard tier, workers=$WORKERS) ===" >> "$LOG"

run_arm() {
  local arm=$1 config=$2 temp=$3
  local outdir="$BASE/v3-$arm"
  echo "=== $(date -u +%FT%TZ) START $arm (temp=$temp think=high) ===" >> "$LOG"
  "$PY" scripts/4_detect_mounds_batch.py \
    --config "prompts/configs/$config" \
    --model "$MODEL" --temperature "$temp" --thinking-level high \
    --manifest "$MANIFEST" --tiles-dir "$TILES_DIR" --tile-size 384 \
    --output-dir "$outdir" \
    --mode realtime --use-cache --skip-intent-check \
    --allow-inert-fields --max-retries 3 \
    --workers "$WORKERS" >> "$LOG" 2>&1 < /dev/null
  local rc=$?
  echo "=== $(date -u +%FT%TZ) END   $arm exit=$rc ===" >> "$LOG"
}

# arm        config                  temp
# Cost guard: sum the runner's own estimates over finished v3 arms.
spent() {
  "$PY" - "$BASE" <<'PYEOF'
import glob, json, sys
total = 0.0
for f in glob.glob(f"{sys.argv[1]}/v3-*/*.meta.json"):
    total += float((json.load(open(f)).get("cost_estimate") or {}).get("total_cost_usd") or 0)
print(f"{total:.4f}")
PYEOF
}
guarded_arm() {
  local s; s=$(spent)
  echo "=== $(date -u +%FT%TZ) cost so far (runner estimate) US\$$s ===" >> "$LOG"
  if awk -v s="$s" 'BEGIN{exit !(s > 14.0)}'; then
    echo "=== $(date -u +%FT%TZ) COST GUARD: stopping before $1 ===" >> "$LOG"
    rm -f "$BASE/probe-v3.pid"; exit 3
  fi
  run_arm "$@"
}

guarded_arm text-t0.0  detect_brief-text.json 0.0
guarded_arm text-t0.7  detect_brief-text.json 0.7
guarded_arm text-t1.0  detect_brief-text.json 1.0
guarded_arm image-t0.0 library_plus-hp.json   0.0
guarded_arm image-t0.7 library_plus-hp.json   0.7

echo "=== $(date -u +%FT%TZ) ALL 5 ARMS COMPLETE; cost (runner estimate) US\$$(spent) ===" >> "$LOG"
rm -f "$BASE/probe-v3.pid"
