#!/usr/bin/env bash
# =============================================================================
# Run B, the modality bridging pair — Stage 1: four proposer arms, Batch API
# =============================================================================
#
# Card: planning/modality-bridge-2026-10-07.md (commands, costs, gates,
# audit). Gate: planning/gate-2026-10-07-verifier-date-and-bridge.md § 2;
# design approved by PI ruling D49 (planning/pi-decisions-2026-09-20.md).
# Stage 1 spends money and needs the PI's own approval of the card's final
# commands and audit verdict. `print-args`, `plan`, `status` and
# `residuals` make no API call; `lodge` and `recover` do.
#
# What it runs. The four proposer arms of the modality claim (R7.3-22/23),
# each re-run with the original leg's configuration file, model, thinking
# level, temperature, tile manifest, tile tree, example library and K. The
# date differs, and so does the serving mode: the originals ran real-time
# (flex, or standard on the cached path), these run on the Batch API, as
# D49 approved (and the 2026-09-18 ruling makes the default for 3.7):
#
#   arm        config                   model                   thinking  K
#   g3-text    detect_brief-text        gemini-3-flash-preview  minimal   10
#   g3-image   detect_brief-text-image  gemini-3-flash-preview  minimal   10
#              (+ --use-cache: the original sent the examples through an
#              EXPLICIT context cache, so the request is two user turns)
#   g37-text   detect_brief-text        gemini-3.7-flash        low        5
#   g37-image  detect_brief-text-image  gemini-3.7-flash        low        5
#              (no --use-cache: the original sent the examples INLINE, one
#              user turn, with implicit caching; 17 inline example images
#              make each request about 2.7 MB, so a pass is cut into three
#              466-tile batch jobs to stay under the 2 GB per-file limit)
#
# Three further arms, approved by the PI on 2026-10-07 (card § 4.8; outside
# D49). Each differs from an original arm in the named levers only:
#
#   arm              like       differs in
#   g37-image-cache  g37-image  --use-cache (the explicit cache, two user
#                               turns, as g3-image), so no 466-tile chunking
#   g3-text-temp1    g3-text    T = 1.0 (the config's own value), K = 5
#   g3-image-temp1   g3-image   T = 1.0 (the config's own value), K = 5
#
# The two temp1 arms and g37-image-cache are temperature-, structure- and
# K-matched to the 3.7 arms (Gemini 3.7 samples at its default 1.0 whatever
# is sent: planning/temperature-probe-2026-10-07.md § 7).
#
# Original arms: T = 0.7 (CLI override of the config's 1.0, as every original
# leg), inputs/grid-2026-08-18/grid_384_ov192_manifest.json (1,398 tiles),
# inputs/tiles_384_ov192. Text arms pass --allow-inert-fields: their config
# lists 17 examples under include_example_images: false, which transmits
# nothing from the library (E90); the original runs predate the launch
# guard, and the flag reproduces them exactly as they were sent.
#
# Usage (from the repository root on sapphire, after the branch is merged):
#
#   bash scripts/modality-bridge-2026-10-07-stage1.sh print-args g3-image 3
#   bash scripts/modality-bridge-2026-10-07-stage1.sh plan
#   bash scripts/modality-bridge-2026-10-07-stage1.sh lodge g37-image:1
#   bash scripts/modality-bridge-2026-10-07-stage1.sh lodge all
#   bash scripts/modality-bridge-2026-10-07-stage1.sh status
#   bash scripts/modality-bridge-2026-10-07-stage1.sh residuals
#   bash scripts/modality-bridge-2026-10-07-stage1.sh recover
#
# Launch hygiene (docs/agent-guidance.md § Compute Location). Every pass is
# started detached with all three descriptors redirected and nothing after
# it on its line; its pid goes to a pid file. Passes are LODGED one at a
# time: the next starts only when the previous has logged "Submitted batch
# job" (or exited), so each storage preflight (lib_batch_api
# .preflight_file_storage) sees every earlier upload. All jobs then run
# concurrently on the service. Never kill a pass that is polling: its job
# keeps running and the job name lives only in its log. `lodge` refuses to
# re-lodge a pass whose log shows more submitted jobs than landed chunks.
#
# NOTE — `4_detect_mounds_batch.py --mode batch --dry-run` is NOT API-free:
# it creates a client and lists the models before the dry-run branch. This
# script therefore has no dry-run mode; the API-free rehearsal is the stub
# harness recorded in the card (§ 6).
#
# Created: 2026-10-07
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0
# =============================================================================

set -u
cd "$(dirname "$0")/.." || exit 1

PY=${PY:-.venv/bin/python}
OUT=${OUT:-outputs/modality-bridge-2026-10-07}
MANIFEST=inputs/grid-2026-08-18/grid_384_ov192_manifest.json
TILES=inputs/tiles_384_ov192
TEXT_CONFIG=prompts/configs/detect_brief-text.json
IMAGE_CONFIG=prompts/configs/detect_brief-text-image.json
# Seconds to wait between lodges, so the previous upload leaves PROCESSING
# (the preflight charges a PROCESSING file at a full 2 GB chunk).
LODGE_GAP=${LODGE_GAP:-60}
# Longest a lodge may take to reach "Submitted batch job" (JSONL build plus
# upload) before the loop stops and asks for a look.
LODGE_TIMEOUT=${LODGE_TIMEOUT:-2400}

# Lodging order: the D49 arms first (largest requests first), then the
# three added arms, so a storage refusal can only delay an addition.
ARMS="g37-image g37-text g3-image g3-text g37-image-cache g3-image-temp1 g3-text-temp1"

# -----------------------------------------------------------------------------
# passes_for ARM — the pass numbers of one arm (K = 10 or K = 5).
# -----------------------------------------------------------------------------
passes_for() {
  case "$1" in
    g3-text|g3-image) echo "1 2 3 4 5 6 7 8 9 10" ;;
    g37-text|g37-image|g37-image-cache|g3-text-temp1|g3-image-temp1)
      echo "1 2 3 4 5" ;;
    *) echo "unknown arm: $1" >&2; return 1 ;;
  esac
}

# -----------------------------------------------------------------------------
# version_for ARM — the config's version string (the batch writer's subdir).
# -----------------------------------------------------------------------------
version_for() {
  case "$1" in
    g3-text|g37-text|g3-text-temp1) echo "detect_brief-text" ;;
    g3-image|g37-image|g37-image-cache|g3-image-temp1)
      echo "detect_brief-text-image" ;;
    *) echo "unknown arm: $1" >&2; return 1 ;;
  esac
}

# -----------------------------------------------------------------------------
# temperature_for ARM — the temperature sent (0.7 on the D49 arms, as the
# originals; 1.0 on the matched Gemini 3 pair).
# -----------------------------------------------------------------------------
temperature_for() {
  case "$1" in
    g3-text-temp1|g3-image-temp1) echo "1.0" ;;
    *) echo "0.7" ;;
  esac
}

# -----------------------------------------------------------------------------
# uses_cache ARM — 0 when the arm sends its examples through an explicit
# context cache.
# -----------------------------------------------------------------------------
uses_cache() {
  case "$1" in
    g3-image|g37-image-cache|g3-image-temp1) return 0 ;;
    *) return 1 ;;
  esac
}

# -----------------------------------------------------------------------------
# cache_referenced PASSDIR — 0 when the newest request file the pass wrote
# (PASSDIR/batch_working/*.jsonl) sends its first request through a context
# cache, i.e. carries a top-level "cached_content".
# -----------------------------------------------------------------------------
cache_referenced() {
  local req
  req=$(ls -t "$1"/batch_working/*.jsonl 2>/dev/null | head -1)
  [ -n "$req" ] || return 1
  "$PY" -c 'import json, sys
line = json.loads(open(sys.argv[1]).readline())
sys.exit(0 if line.get("request", {}).get("cached_content") else 1)' "$req"
}

# -----------------------------------------------------------------------------
# arm_table — one line per arm: name, K, config version. The status and
# residuals readers take it, so they never hard-code the arm list.
# -----------------------------------------------------------------------------
arm_table() {
  local arm
  for arm in $ARMS; do
    echo "$arm $(passes_for "$arm" | wc -w) $(version_for "$arm")"
  done
}

# -----------------------------------------------------------------------------
# print_args ARM RUN [OUTDIR [MANIFEST]] — the exact detector arguments, one
# per line. OUTDIR and MANIFEST default to the main pass; `recover` passes a
# fragment directory and a residual manifest.
# -----------------------------------------------------------------------------
print_args() {
  local arm=$1 run=$2 outdir=${3:-$OUT/$1} manifest=${4:-$MANIFEST}
  local -a a
  case "$arm" in
    g3-text)
      # The grid's own flags (2026-08-18 launch, session archive): the
      # thinking level and tile size were passed explicitly; both equal
      # the effective values, and --tile-size is now an assertion only.
      a=(--config "$TEXT_CONFIG" --model gemini-3-flash-preview
         --thinking-level minimal --tile-size 384 --allow-inert-fields) ;;
    g3-image)
      a=(--config "$IMAGE_CONFIG" --model gemini-3-flash-preview
         --use-cache) ;;
    g37-text)
      a=(--config "$TEXT_CONFIG" --model gemini-3.7-flash
         --thinking-level low --allow-inert-fields) ;;
    g37-image)
      a=(--config "$IMAGE_CONFIG" --model gemini-3.7-flash
         --thinking-level low --max-batch-tiles 466) ;;
    g37-image-cache)
      # As g37-image, but through the explicit cache; a cached request
      # carries only the tile (about 0.33 MB), so one job per pass.
      a=(--config "$IMAGE_CONFIG" --model gemini-3.7-flash
         --thinking-level low --use-cache) ;;
    g3-text-temp1)
      a=(--config "$TEXT_CONFIG" --model gemini-3-flash-preview
         --thinking-level minimal --tile-size 384 --allow-inert-fields) ;;
    g3-image-temp1)
      a=(--config "$IMAGE_CONFIG" --model gemini-3-flash-preview
         --use-cache) ;;
    *) echo "unknown arm: $arm" >&2; return 1 ;;
  esac
  a+=(--manifest "$manifest" --tiles-dir "$TILES"
      --temperature "$(temperature_for "$arm")"
      --mode batch --service-tier flex --run "$run" --output-dir "$outdir"
      --skip-intent-check)
  printf '%s\n' "${a[@]}"
}

# -----------------------------------------------------------------------------
# pass_dir ARM RUN [OUTDIR] — where the batch writer puts one pass.
# -----------------------------------------------------------------------------
pass_dir() {
  local outdir=${3:-$OUT/$1}
  echo "$outdir/$(version_for "$1")/run_$2"
}

# -----------------------------------------------------------------------------
# landed ARM RUN [OUTDIR] — 0 when the pass's final (merged) geojson exists.
# -----------------------------------------------------------------------------
landed() {
  local d v
  d=$(pass_dir "$1" "$2" "${3:-}")
  v=$(version_for "$1")
  [ -f "$d/detections_${v}_run$(printf '%02d' "$2").geojson" ]
}

# -----------------------------------------------------------------------------
# alive PIDFILE — 0 when the pid file names a live process.
# -----------------------------------------------------------------------------
alive() {
  [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null
}

# -----------------------------------------------------------------------------
# lodge_one ARM RUN [OUTDIR [MANIFEST [TAG]]] — start one pass detached and
# wait until its first job is submitted. Returns non-zero when the loop
# should stop (the pass exited before submitting, or the lodge timed out).
# -----------------------------------------------------------------------------
lodge_one() {
  local arm=$1 run=$2 outdir=${3:-$OUT/$1} manifest=${4:-$MANIFEST} tag=${5:-}
  local name="${arm}-run${run}${tag}"
  local log="$OUT/logs/$name.log" pidf="$OUT/pids/$name.pid"
  local d submitted landed_chunks waited=0 base
  mkdir -p "$OUT/logs" "$OUT/pids"

  if alive "$pidf"; then
    echo "$name: process $(cat "$pidf") still running — skipped"
    return 0
  fi
  if landed "$arm" "$run" "$outdir"; then
    echo "$name: already landed — skipped"
    return 0
  fi
  d=$(pass_dir "$arm" "$run" "$outdir")
  submitted=$(grep -c "Submitted batch job" "$log" 2>/dev/null)
  submitted=${submitted:-0}
  landed_chunks=$(find "$d" -maxdepth 1 -name "*.tiles.json" 2>/dev/null | wc -l)
  if [ "$submitted" -gt "$landed_chunks" ] && [ "${FORCE:-0}" != 1 ]; then
    echo "$name: REFUSED — the log shows $submitted submitted job(s) but" \
         "$landed_chunks landed chunk(s); a job may still be running on the" \
         "service. Recover it by its job name before re-lodging (FORCE=1" \
         "overrides)."
    return 1
  fi

  mapfile -t ARGS < <(print_args "$arm" "$run" "$outdir" "$manifest")
  base=$(grep -c "Submitted batch job" "$log" 2>/dev/null)
  base=${base:-0}
  echo "=== $(date -Is) LODGE $name: $PY scripts/4_detect_mounds_batch.py ${ARGS[*]}" >> "$log"
  # Unbuffered, so "Submitted batch job" reaches the log the moment the job
  # exists: a buffered line lost to an early kill would let `lodge` lodge a
  # second, billed job for the same pass (audit F9).
  PYTHONUNBUFFERED=1 nohup "$PY" scripts/4_detect_mounds_batch.py "${ARGS[@]}" \
    >> "$log" 2>&1 < /dev/null &
  echo $! > "$pidf"
  echo "$name: started pid $(cat "$pidf"), log $log"

  # Wait for the first NEW submission, or for the process to end.
  while :; do
    if [ "$(grep -c "Submitted batch job" "$log" 2>/dev/null)" -gt "$base" ]; then
      local job
      job=$(grep "Submitted batch job" "$log" | tail -1 | awk '{print $NF}')
      # The batch meta records no job times, so the served window is read
      # from this stamp and the pass meta's write time.
      echo "=== $(date -Is) SUBMITTED $name $job" >> "$log"
      echo "$name: submitted ($job)"
      # A cached arm whose cache did not engage has fallen back to inline
      # requests, a different request shape: stop before lodging more. The
      # evidence is the request file just uploaded (batch_working/ keeps
      # it), not the log: lib_batch_api's INFO lines, including "batch
      # unit will reference cache", never reach a detector log (no handler
      # below WARNING; 0 INFO lines in every detector batch log checked).
      if uses_cache "$arm" && ! cache_referenced "$d"; then
        echo "$name: CACHE NOT ENGAGED (the newest request file under" \
             "$d/batch_working has no cached_content) — lodging stops;" \
             "read $log. The pass's job runs inline and must be" \
             "discarded: wait until \`status\` shows it gone with a" \
             "terminal state (the detector rewrites $d when its job" \
             "lands), then move $d, its log and its pid file to" \
             "archive/ and re-lodge it (FORCE=1 if the log stays)"
        return 1
      fi
      sleep "$LODGE_GAP"
      return 0
    fi
    if ! alive "$pidf"; then
      echo "$name: EXITED before submitting — read $log; lodging stops here"
      return 1
    fi
    if [ "$waited" -ge "$LODGE_TIMEOUT" ]; then
      echo "$name: no submission after ${waited}s — lodging stops; the" \
           "process is left running (pid $(cat "$pidf"))"
      return 1
    fi
    sleep 15
    waited=$((waited + 15))
  done
}

# -----------------------------------------------------------------------------
# expand SPEC... — "all", "ARM" or "ARM:RUN" to "ARM RUN" lines, in the
# lodging order (largest requests first).
# -----------------------------------------------------------------------------
expand() {
  local spec arm run
  for spec in "$@"; do
    case "$spec" in
      all) for arm in $ARMS; do for run in $(passes_for "$arm"); do
             echo "$arm $run"; done; done ;;
      *:*)
        arm=${spec%%:*}; run=${spec##*:}
        # Only a planned pass may be lodged: an unknown arm or a run
        # outside the arm's K is refused before anything starts (audit F6).
        if ! passes_for "$arm" >/dev/null 2>&1 \
            || ! passes_for "$arm" | tr ' ' '\n' | grep -qx "$run"; then
          echo "REFUSED: $spec is not a planned pass" >&2; return 1
        fi
        echo "$arm $run" ;;
      *)
        passes_for "$spec" >/dev/null 2>&1 \
          || { echo "REFUSED: unknown arm $spec" >&2; return 1; }
        for run in $(passes_for "$spec"); do echo "$spec $run"; done ;;
    esac
  done
}

# -----------------------------------------------------------------------------
# status — per pass: process, log age, terminal state (wait_for_run's
# classifier), failure lines (case-insensitive), coverage and cache share.
# No API call.
# -----------------------------------------------------------------------------
status() {
  "$PY" - "$OUT" "$MANIFEST" "$(arm_table)" <<'EOF'
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, "scripts")
from wait_for_run import classify_log  # noqa: E402

out, manifest = sys.argv[1], sys.argv[2]
versions = {ln.split()[0]: ln.split()[2] for ln in sys.argv[3].splitlines()}
want = len(json.load(open(manifest)))
fail = re.compile(r"failed|lost|partial|completeness gap|traceback|error|"
                  r"cache creation failed|refused", re.IGNORECASE)
benign = re.compile(r"Tiles failed: 0\b|0 failed|failed_extractions\": 0")
for log in sorted(glob.glob(f"{out}/logs/*.log")):
    name = os.path.basename(log)[:-4]
    pidf = f"{out}/pids/{name}.pid"
    live = "-"
    if os.path.exists(pidf):
        try:
            os.kill(int(open(pidf).read().strip()), 0)
            live = "ALIVE"
        except (ProcessLookupError, ValueError):
            live = "gone"
        except PermissionError:
            live = "ALIVE"
    text = open(log, errors="replace").read()
    state = classify_log(text)
    age = int(time.time() - os.path.getmtime(log))
    bad = [ln for ln in text.splitlines() if fail.search(ln) and not benign.search(ln)]
    arm, rest = name.split("-run")[0], name.split("-run")[1]
    run, _, rd = rest.partition("_")
    ver = versions[arm]
    # A recovery fragment's log (…_rd<R>) reports the fragment's own files.
    root = f"{out}/{arm}/recovery_{rd}" if rd else f"{out}/{arm}"
    tiles = glob.glob(f"{root}/{ver}/run_{run}/*.tiles.json")
    merged = [t for t in tiles if "_chunk" not in t]
    use = merged or tiles
    done = set()
    failed = set()
    for t in use:
        d = json.load(open(t))
        done |= set(d.get("completed", []))
        failed |= set(d.get("failed", []))
    metas = [m for m in glob.glob(f"{root}/{ver}/run_{run}/*.meta.json")
             if ("_chunk" not in m) == bool(merged)]
    tin = tca = 0
    for m in metas:
        u = json.load(open(m)).get("usage_stats", {})
        tin += u.get("total_input_tokens", 0) or 0
        tca += u.get("total_cached_tokens", 0) or 0
    share = f"{tca / tin:.3f}" if tin else "n/a"
    print(f"{name:22s} {live:6s} age {age:6d}s  state {state:8s} "
          f"tiles {len(done):4d}/{want} failed {len(failed):3d} "
          f"cached {share:>5s}  fail-lines {len(bad)}")
    for ln in bad[-3:]:
        print(f"    | {ln[:150]}")
EOF
}

# -----------------------------------------------------------------------------
# residuals — per pass, the manifest minus every tile the pass and its
# recovery fragments completed; writes $OUT/<arm>/residual_run_<N>.json when
# non-empty. No API call.
# -----------------------------------------------------------------------------
residuals() {
  "$PY" - "$OUT" "$MANIFEST" "$(arm_table)" <<'EOF'
import glob
import json
import os
import sys

out, manifest = sys.argv[1], sys.argv[2]
pinned = json.load(open(manifest))
table = [ln.split() for ln in sys.argv[3].splitlines()]
for arm, k, ver in ((a, int(k), v) for a, k, v in table):
    for run in range(1, k + 1):
        done = set()
        main = glob.glob(f"{out}/{arm}/{ver}/run_{run}/*.tiles.json")
        merged = [t for t in main if "_chunk" not in t]
        if not merged:
            # A pass with no final sidecar has not landed (a chunk failed and
            # the merge was withheld, or it never ran): resume it with
            # `lodge`, which skips its landed chunks. A recovery fragment
            # here would race the resumed chunk for the same tiles.
            print(f"{arm} run_{run}: NOT LANDED — resume with `lodge {arm}:{run}`")
            continue
        # A recovery fragment counts only through its merged sidecar. One
        # with chunk sidecars but no merged sidecar has not landed (a chunked
        # g37-image fragment that lost a chunk): resume it from its own
        # residual manifest, which must therefore not be rewritten (Stage 2
        # audit A8).
        frags, pending = [], None
        for fd in sorted(glob.glob(f"{out}/{arm}/recovery_rd*/{ver}/run_{run}")):
            sidecars = glob.glob(f"{fd}/*.tiles.json")
            merged_f = [t for t in sidecars if "_chunk" not in t]
            if sidecars and not merged_f:
                pending = fd
                break
            frags.extend(merged_f)
        if pending:
            print(f"{arm} run_{run}: FRAGMENT NOT LANDED ({pending}) - resume it "
                  f"with the same ROUND and its residual manifest; no new "
                  f"residual written")
            continue
        for t in merged + frags:
            done |= set(json.load(open(t)).get("completed", []))
        resid = [t for t in pinned if t not in done]
        path = f"{out}/{arm}/residual_run_{run}.json"
        if resid:
            json.dump(resid, open(path, "w"), indent=0)
        elif os.path.exists(path):
            # A cleared pass must not be re-lodged from a stale residual.
            os.remove(path)
        print(f"{arm} run_{run}: completed {len(done & set(pinned))}/{len(pinned)}, "
              f"residual {len(resid)}" + (f" -> {path}" if resid else ""))
EOF
}

# -----------------------------------------------------------------------------
# recover — lodge one additive fragment per pass with a residual manifest,
# into $OUT/<arm>/recovery_rd<R>/ (R = ROUND, default 1). Same invocation as
# the main pass; only --manifest and --output-dir differ.
# -----------------------------------------------------------------------------
recover() {
  local round=${ROUND:-1} arm run resid
  for arm in $ARMS; do
    for run in $(passes_for "$arm"); do
      resid="$OUT/$arm/residual_run_$run.json"
      [ -f "$resid" ] || continue
      lodge_one "$arm" "$run" "$OUT/$arm/recovery_rd$round" "$resid" "_rd$round" || return 1
    done
  done
}

# -----------------------------------------------------------------------------
# plan — print every pass's exact command. No API call.
# -----------------------------------------------------------------------------
plan() {
  local arm run
  for arm in $ARMS; do
    for run in $(passes_for "$arm"); do
      echo "$PY scripts/4_detect_mounds_batch.py $(print_args "$arm" "$run" | tr '\n' ' ')"
    done
  done
}

cmd=${1:-}
shift || true
case "$cmd" in
  print-args) print_args "$@" ;;
  plan) plan ;;
  status) status ;;
  residuals) residuals ;;
  recover) recover ;;
  lodge)
    [ $# -gt 0 ] || { echo "lodge needs: all | ARM | ARM:RUN ..." >&2; exit 2; }
    # Expand (and validate) every spec before the first lodge, so a bad
    # spec stops the whole command rather than part-way through it.
    specs=$(expand "$@") || exit 2
    while read -r arm run; do
      lodge_one "$arm" "$run" || exit 1
    done <<< "$specs"
    echo "LODGING DONE $(date -Is)" ;;
  *)
    sed -n '2,60p' "$0"
    exit 2 ;;
esac
