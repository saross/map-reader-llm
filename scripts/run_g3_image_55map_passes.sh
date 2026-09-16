#!/usr/bin/env bash
# Sequential driver for the Gemini 3 image 55-map pool, passes 2-5.
#
# Waits for pass 1 (already running) to exit, then runs each remaining pass to
# completion before starting the next. Sequential by design: concurrent passes
# contend for the same flex capacity and make per-pass token profiles
# uninterpretable.
#
# Liveness is judged by LOG STALENESS, not by a process check
# (docs/agent-guidance.md): a staleness test catches a hang as well as a death,
# where a process check catches only death. The pgrep fallback uses a bracketed
# pattern so it cannot match its own command line.
#
# Each pass is resumable -- the driver skips tiles already in its output -- so a
# flex outage leaves a partial pass that can be re-run, not a lost one.
set -u
cd ~/Code/map-reader-llm
ROOT=outputs/gemini3-image-55map-2026-09-16
POOL=$ROOT/g384_ov192_55map_g3img
STALE=900          # 15 min without a log write means pass 1 is done or wedged

echo "$(date -Is) driver start; waiting for pass 1"
while :; do
  if ! pgrep -f "[4]_detect_mounds_batch.py --config" > /dev/null; then
    echo "$(date -Is) pass 1 process gone"; break
  fi
  age=$(( $(date +%s) - $(stat -c %Y "$ROOT/pass1.log") ))
  if [ "$age" -gt "$STALE" ]; then
    echo "$(date -Is) pass 1 log stale ${age}s — treating as finished/wedged"; break
  fi
  sleep 30
done

done_1=$(tr "\r" "\n" < "$ROOT/pass1.log" | grep -oE "\| [0-9]+/24561" | tail -1 | grep -oE "^[0-9]+|[0-9]+" | head -1)
echo "$(date -Is) pass 1 completed=${done_1:-0}/24561"

for n in 2 3 4 5; do
  echo "$(date -Is) PASS $n start"
  .venv/bin/python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/detect_brief-text-image.json \
    --model gemini-3-flash-preview --temperature 0.7 --thinking-level minimal \
    --tiles-dir inputs/tiles_384_ov192_55maps \
    --output-dir "$POOL/run_$n" \
    --service-tier flex --workers 12 \
    > "$ROOT/pass$n.log" 2>&1
  rc=$?
  done_n=$(tr "\r" "\n" < "$ROOT/pass$n.log" | grep -oE "\| [0-9]+/24561" | tail -1 | grep -oE "[0-9]+" | head -1)
  echo "$(date -Is) PASS $n end rc=$rc completed=${done_n:-0}/24561"
  if [ "${done_n:-0}" -lt 20000 ]; then
    echo "$(date -Is) ABORT: pass $n completed only ${done_n:-0}/24561 — flex likely unavailable; not starting further passes"
    exit 1
  fi
done
echo "$(date -Is) ALL PASSES COMPLETE"
