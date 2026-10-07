#!/usr/bin/env bash
# =============================================================================
# Run B, the modality bridging pair — Stage 2: unions, crops, verifier legs
# =============================================================================
#
# Card: planning/modality-bridge-2026-10-07-stage2.md (commands, costs, gate
# checks, validation, go/no-go). Stage 1 card and launcher:
# planning/modality-bridge-2026-10-07.md, scripts/modality-bridge-2026-10-07-stage1.sh.
# Stage 2 spends money only in `verify`; every other subcommand makes no API
# call. `verify` needs the PI's go (D49: Stage 2 returns to the PI with its
# final configuration and audit verdict).
#
# What it runs, per arm (card § 2; Stage 1 card §§ 2.2, 4.8, 8):
#
#   1. check      coverage gate: every pass of the arm landed (exactly
#                 run_1..run_K, each merged), each pass plus its recovery
#                 fragments covering exactly the 1,398 pinned tiles, no tile
#                 processed twice, no Stage 1 process of the arm alive, no
#                 residual file outstanding; and every pass file's meta
#                 records the arm's model, temperature, thinking level and
#                 cached share (scripts/modality_bridge_stage2_checks.py).
#   2. union      the originals' chain (E80 20 m within-pass dedup, E72 exact
#                 coverage, carrier clip, c = 1, vote_count, numeric pass
#                 order) through scripts/modality_bridge_union.py's batch
#                 layout adapter; validated byte-identical on the four
#                 original unions (`validate-chain`).
#   3. extract    run_pv.py extract (150 x 150 crops, padding 75,
#                 inputs/rasters, inputs/tiles_384_ov192), as the originals.
#   4. provenance scripts/check_union_provenance.py: the crop manifest must
#                 classify AGREES with its union (not merely "not DISAGREES").
#   5. rehearse   run_pv.py verify --mode batch --dry-run under the API-free
#                 harness: one request per candidate, no client constructed,
#                 the request signature the card rehearsed against the
#                 original legs' real-time requests, and the full-request
#                 signature pinned beside it.
#   6. verify     the union-size review band (±15 % of the guide), then
#                 run_pv.py verify --mode batch --temperature 0.0 with the
#                 Gemini 3 (gemini-3-flash-preview) or Gemini 3.7
#                 (gemini-3.7-flash, thinking low) verifier. SPENDS.
#   7. repair     after a leg lands: its PARSE_ERROR rows re-parsed from
#                 batch_results.jsonl with the real-time path's repair, into
#                 <leg>_repaired/ (the leg directory is not written).
#
# Operator overrides, each named in the refusal it lifts: BAND_OK=1 (a union
# outside its band), IMPLICIT_SHARE_OK=1 (g37-image's implicit cached share
# under 0.5; cost only), FORCE=1 (re-lodge a leg whose earlier jobs are
# recorded in batch_jobs.json; read the refusal first).
#
#   arm              K   version                  verifier legs
#   g3-text          10  detect_brief-text        g3
#   g3-image         10  detect_brief-text-image  g3
#   g37-text          5  detect_brief-text        g3, g37
#   g37-image         5  detect_brief-text-image  g3, g37
#   g37-image-cache   5  detect_brief-text-image  g3, g37
#   g3-text-temp1     5  detect_brief-text        g3
#   g3-image-temp1    5  detect_brief-text-image  g3
#
# The Gemini 3 K = 5 rung is INHERITED from the K = 10 legs (PI ruling D2,
# D52): no K = 5 union of g3-text or g3-image is verified.
#
# Usage (repository root on sapphire, after Stage 1 has landed):
#
#   bash scripts/modality-bridge-2026-10-07-stage2.sh plan
#   bash scripts/modality-bridge-2026-10-07-stage2.sh validate-chain
#   bash scripts/modality-bridge-2026-10-07-stage2.sh anchor-gate
#   bash scripts/modality-bridge-2026-10-07-stage2.sh check g3-text
#   bash scripts/modality-bridge-2026-10-07-stage2.sh prepare all
#   bash scripts/modality-bridge-2026-10-07-stage2.sh rehearse all
#   bash scripts/modality-bridge-2026-10-07-stage2.sh verify g37-image:g3
#   bash scripts/modality-bridge-2026-10-07-stage2.sh verify all
#   bash scripts/modality-bridge-2026-10-07-stage2.sh status
#   bash scripts/modality-bridge-2026-10-07-stage2.sh estimate
#   bash scripts/modality-bridge-2026-10-07-stage2.sh wait g37-image:g3
#   bash scripts/modality-bridge-2026-10-07-stage2.sh repair all
#
# Launch hygiene (docs/agent-guidance.md § Compute Location). A verifier leg
# starts detached under a wrapper shell that writes its OWN pid to the pid
# file, runs the leg with all three descriptors redirected and
# PYTHONUNBUFFERED=1, and appends "=== <time> EXIT <status>" when it ends;
# nothing follows the launch on its line. Legs are lodged one at a time: the
# next starts only after the previous has logged every chunk's "Submitted
# batch job" line, so each storage preflight sees the earlier uploads. A
# polling verifier logs an HTTP GET for its job about every 30 s (run_pv.py
# sets the root logger to INFO; corrected 2026-10-08, audit A3: this said
# "silent"), so `wait` treats an hour of log silence as a hang, beside the
# pid (kill -0, never pgrep -f) and the EXIT line. Never kill a polling leg:
# its job keeps running, and batch_jobs.json in the leg directory names it
# (run_pv.py batch-recover). `verify` refuses a leg whose directory holds
# batch_jobs.json without probabilities.json. A relaunch moves the earlier
# attempt's log aside (<log>.<UTC stamp>) and removes its pid file, so the
# launcher, `status` and `wait` read only the current attempt (audit A1).
# One writing subcommand runs at a time (flock on $ST2/stage2.lock; audit
# A4); a launched leg does not hold the lock.
#
# Logs, pids and check records go under $OUT/stage2/, never $OUT/logs/: the
# Stage 1 launcher's `status` parses every $OUT/logs/*.log name as
# <arm>-run<N>.
#
# Created: 2026-10-07
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0
# =============================================================================

set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

PY=${PY:-.venv/bin/python}
OUT=${OUT:-outputs/modality-bridge-2026-10-07}
ST2=${ST2:-$OUT/stage2}
# Dry-run request files (about 60 KB per candidate) are built here and
# deleted after summary; it must not lie under $OUT.
SCRATCH=${SCRATCH:-${TMPDIR:-/tmp}/runb-stage2}
MANIFEST=inputs/grid-2026-08-18/grid_384_ov192_manifest.json
WANT_TILES=1398
TILES=inputs/tiles_384_ov192
RASTERS=inputs/rasters
VCONFIG=prompts/configs/verify_adversarial-text.json
# Candidates per batch job (run_pv.py DEFAULT_MAX_BATCH_CANDIDATES).
PER_JOB=4000
LODGE_GAP=${LODGE_GAP:-60}
LODGE_TIMEOUT=${LODGE_TIMEOUT:-2400}

ARMS="g3-text g3-image g37-text g37-image g37-image-cache g3-text-temp1 g3-image-temp1"
LEGS="g3-text:g3 g3-image:g3 g37-text:g3 g37-text:g37 g37-image:g3 g37-image:g37"
LEGS="$LEGS g37-image-cache:g3 g37-image-cache:g37 g3-text-temp1:g3 g3-image-temp1:g3"

# Tile-elided request signatures rehearsed against the original legs'
# real-time requests (card § 4; planning/modality-bridge-2026-10-07-stage2-
# rehearsal.json): identical for every union under one verifier.
SIG_G3=3b48d7193dcf0165af68d3b283a3bc6ce884689e0c4cb0e7369f5d5f219f7d04
SIG_G37=51567e8e54f8fa3cb85262431460020de5e57ff8ea3e1d63f0523d19beb34c1e
# The same requests hashed whole, bar the key and the crop's bytes, so any
# generation-config field added to the builder moves it (audit nit; computed
# 2026-10-08, crop-independent by construction and checked on the original
# crops: planning/modality-bridge-2026-10-07-stage2-rehearsal.json).
SIGF_G3=5e9bb517e77f6ac2a19cdffa4c844c44485c69f82bd3a0e825617cfa7bc05c99
SIGF_G37=38834432d7fdd5dfcb2e440a501b4c175e0fcffe2bd343053b14a5cb07b5ed8e

# -----------------------------------------------------------------------------
# Per-arm and per-leg facts.
# -----------------------------------------------------------------------------
k_for() {
  case "$1" in
    g3-text|g3-image) echo 10 ;;
    g37-text|g37-image|g37-image-cache|g3-text-temp1|g3-image-temp1) echo 5 ;;
    *) echo "unknown arm: $1" >&2; return 1 ;;
  esac
}

version_for() {
  case "$1" in
    g3-text|g37-text|g3-text-temp1) echo "detect_brief-text" ;;
    g3-image|g37-image|g37-image-cache|g3-image-temp1) echo "detect_brief-text-image" ;;
    *) echo "unknown arm: $1" >&2; return 1 ;;
  esac
}

vroot() { echo "$OUT/$1/verifier/$(version_for "$1")"; }
union_path() { echo "$(vroot "$1")/union_k$(k_for "$1").geojson"; }
crops_dir() { echo "$(vroot "$1")/crops"; }

# leg_parts LEG — "ARM V" for ARM:V, refusing a leg the card does not plan.
leg_parts() {
  case " $LEGS " in
    *" $1 "*) echo "${1%%:*} ${1##*:}" ;;
    *) echo "REFUSED: $1 is not a planned leg ($LEGS)" >&2; return 1 ;;
  esac
}

leg_dir() { echo "$(vroot "$1")/verify_$2"; }

vflags() {
  case "$1" in
    g3) echo "--model gemini-3-flash-preview" ;;
    g37) echo "--model gemini-3.7-flash --thinking-level low" ;;
  esac
}

sig_for() { case "$1" in g3) echo "$SIG_G3" ;; g37) echo "$SIG_G37" ;; esac; }
sigf_for() { case "$1" in g3) echo "$SIGF_G3" ;; g37) echo "$SIGF_G37" ;; esac; }

# verify_args ARM V [OUTDIR] — the exact run_pv.py verify arguments, one per
# line. OUTDIR defaults to the leg directory; `rehearse` passes a scratch one.
verify_args() {
  local -a a
  # shellcheck disable=SC2207
  a=(--crops-dir "$(crops_dir "$1")" --verifier-config "$VCONFIG"
     --output-dir "${3:-$(leg_dir "$1" "$2")}" --mode batch --temperature 0.0
     $(vflags "$2"))
  printf '%s\n' "${a[@]}"
}

alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

json_field() {
  # json_field FILE EXPR — print a Python expression over the JSON as `d`.
  "$PY" -c 'import json, sys; d = json.load(open(sys.argv[1])); print(eval(sys.argv[2]))' "$1" "$2"
}

# -----------------------------------------------------------------------------
# check ARM — the coverage gate. No API, no writes outside $ST2/checks.
# -----------------------------------------------------------------------------
check() {
  local arm=$1 k v pidf rec
  k=$(k_for "$arm") || return 1
  v=$(version_for "$arm")
  for pidf in "$OUT"/pids/"$arm"-run*.pid; do
    [ -e "$pidf" ] || continue
    if alive "$pidf"; then
      echo "$arm: REFUSED — Stage 1 process $(cat "$pidf") ($pidf) is still running"
      return 1
    fi
  done
  if ls "$OUT/$arm"/residual_run_*.json >/dev/null 2>&1; then
    echo "$arm: REFUSED — residual file(s) outstanding: $(ls "$OUT/$arm"/residual_run_*.json |
      tr '\n' ' ')(run Stage 1 \`residuals\` after recovery lands)"
    return 1
  fi
  mkdir -p "$ST2/checks"
  rec="$ST2/checks/$arm-coverage.json"
  if ! "$PY" scripts/modality_bridge_union.py --layout batch --cell-dir "$OUT/$arm/$v" \
      --k "$k" --out-root "$OUT/$arm" --manifest "$MANIFEST" --json-out "$rec"; then
    echo "$arm: REFUSED — coverage gate failed (above)"
    return 1
  fi
  if [ "$(json_field "$rec" 'd["manifest_tiles"]')" != "$WANT_TILES" ] ||
     [ "$(json_field "$rec" 'all(p["processed_tiles"] == d["manifest_tiles"] for p in d["passes"])')" != True ] ||
     [ "$(json_field "$rec" 'len(d["passes"])')" != "$k" ]; then
    echo "$arm: REFUSED — the coverage record is not $k passes of $WANT_TILES tiles ($rec)"
    return 1
  fi
  echo "$arm: coverage OK — $k passes x $WANT_TILES tiles; files per pass" \
       "$(json_field "$rec" '[len(p["files"]) for p in d["passes"]]')"
  # What the passes were sent with (audit A5): model, temperature, thinking
  # level and cached share from every pass file's meta.
  local -a extra=()
  [ "${IMPLICIT_SHARE_OK:-0}" = 1 ] && extra=(--allow-low-implicit-share)
  if ! "$PY" scripts/modality_bridge_stage2_checks.py metas "$arm" --out "$OUT" \
      --json-out "$ST2/checks/$arm-metas.json" "${extra[@]}"; then
    echo "$arm: REFUSED — a pass meta does not record what the arm sends (above)"
    return 1
  fi
}

# -----------------------------------------------------------------------------
# union ARM — check, then build the union (refuses to overwrite one).
# -----------------------------------------------------------------------------
union() {
  local arm=$1 log
  check "$arm" || return 1
  mkdir -p "$ST2/logs"
  log="$ST2/logs/union-$arm.log"
  echo "=== $(date -Is) UNION $arm" >> "$log"
  "$PY" scripts/modality_bridge_union.py --layout batch --cell-dir "$OUT/$arm/$(version_for "$arm")" \
    --k "$(k_for "$arm")" --out-root "$OUT/$arm" --manifest "$MANIFEST" --write \
    >> "$log" 2>&1
  local rc=$?
  tail -3 "$log"
  [ $rc -eq 0 ] || { echo "$arm: UNION FAILED (exit $rc) — read $log"; return 1; }
  echo "$arm: union $(union_path "$arm") — $(json_field "$(vroot "$arm")/union_k$(k_for "$arm").build.json" 'd["union_features"]') candidates"
}

# -----------------------------------------------------------------------------
# extract ARM — crops from a current union (run_pv.py extract).
# -----------------------------------------------------------------------------
extract() {
  local arm=$1 u c log man
  check "$arm" || return 1
  u=$(union_path "$arm"); c=$(crops_dir "$arm")
  [ -f "$u" ] || { echo "$arm: REFUSED — no union yet ($u); run \`union $arm\`"; return 1; }
  "$PY" scripts/modality_bridge_union.py --check-record "$u" ||
    { echo "$arm: REFUSED — the union is stale against its passes"; return 1; }
  if [ -e "$c/candidate_manifest.json" ]; then
    echo "$arm: REFUSED — crops already extracted ($c); archive them to re-extract"
    return 1
  fi
  log="$ST2/logs/extract-$arm.log"
  echo "=== $(date -Is) EXTRACT $arm" >> "$log"
  "$PY" scripts/run_pv.py extract --proposer "$u" --output-dir "$c" \
    --tiles-dir "$TILES" --rasters-dir "$RASTERS" >> "$log" 2>&1
  local rc=$?
  [ $rc -eq 0 ] || { echo "$arm: EXTRACT FAILED (exit $rc) — read $log"; return 1; }
  man="$c/candidate_manifest.json"
  if [ "$(json_field "$man" 'd["failed_extractions"] == 0 and d["successful_extractions"] == d["total_detections"] == len(d["candidates"])')" != True ]; then
    echo "$arm: EXTRACT INCOMPLETE — $(json_field "$man" '{k: d[k] for k in ("total_detections", "successful_extractions", "failed_extractions", "tile_fallback_crops")}')"
    return 1
  fi
  echo "$arm: crops $(json_field "$man" 'd["successful_extractions"]'), raster" \
       "$(json_field "$man" 'd["raster_crops"]'), tile fallback $(json_field "$man" 'd["tile_fallback_crops"]')"
}

# -----------------------------------------------------------------------------
# provenance ARM — the crop manifest must classify AGREES with its union.
# -----------------------------------------------------------------------------
provenance() {
  local arm=$1 man rec cls
  man="$(crops_dir "$arm")/candidate_manifest.json"
  [ -f "$man" ] || { echo "$arm: REFUSED — no crop manifest ($man)"; return 1; }
  rec="$ST2/checks/$arm-provenance.json"
  mkdir -p "$ST2/checks"
  "$PY" scripts/check_union_provenance.py --manifest "$man" --json-out "$rec" > /dev/null 2>&1
  cls=$(json_field "$rec" 'd["manifest_results"][0]["classification"]' 2>/dev/null)
  if [ "$cls" != AGREES ]; then
    echo "$arm: REFUSED — provenance ${cls:-not run} (want AGREES); read $rec"
    return 1
  fi
  if [ "$(json_field "$man" 'len(d["candidates"])')" != \
       "$(json_field "$(vroot "$arm")/union_k$(k_for "$arm").build.json" 'd["union_features"]')" ]; then
    echo "$arm: REFUSED — candidate count differs from the union's"
    return 1
  fi
  echo "$arm: provenance AGREES — $(json_field "$rec" 'd["manifest_results"][0]["detail"]')"
}

# -----------------------------------------------------------------------------
# prepare ARM|all — check, union, extract, provenance. No API.
# -----------------------------------------------------------------------------
prepare_one() {
  local arm=$1
  if [ -f "$(union_path "$arm")" ]; then
    echo "$arm: union exists — skipping the build"
    check "$arm" || return 1
  else
    union "$arm" || return 1
  fi
  if [ -f "$(crops_dir "$arm")/candidate_manifest.json" ]; then
    echo "$arm: crops exist — skipping extraction"
    "$PY" scripts/modality_bridge_union.py --check-record "$(union_path "$arm")" || return 1
  else
    extract "$arm" || return 1
  fi
  provenance "$arm"
}

# -----------------------------------------------------------------------------
# rehearse LEG — the leg's batch request built API-free and checked.
# -----------------------------------------------------------------------------
rehearse() {
  local arm=$1 v=$2 name rec
  name="verify-$arm-$v"
  check "$arm" || return 1
  "$PY" scripts/modality_bridge_union.py --check-record "$(union_path "$arm")" || return 1
  provenance "$arm" || return 1
  rec="$ST2/checks/rehearse-$arm-$v.json"
  # The dry run writes its request files under SCRATCH, not the leg dir.
  mapfile -t ARGS < <(verify_args "$arm" "$v" "$SCRATCH/$name")
  mkdir -p "$SCRATCH"
  if ! "$PY" scripts/verifier_dryrun_harness.py batch --summary-json "$rec" --first 3 \
      -- "${ARGS[@]}" --dry-run > "$ST2/logs/rehearse-$arm-$v.log" 2>&1; then
    echo "$name: REHEARSAL FAILED — read $ST2/logs/rehearse-$arm-$v.log and $rec"
    return 1
  fi
  if [ "$(json_field "$rec" 'list(d["batch"]["elided_signatures"])')" != "['$(sig_for "$v")']" ]; then
    echo "$name: REFUSED — request signature $(json_field "$rec" 'list(d["batch"]["elided_signatures"])')" \
         "is not the rehearsed $(sig_for "$v")"
    return 1
  fi
  if [ "$(json_field "$rec" 'list(d["batch"]["full_elided_signatures"])')" != "['$(sigf_for "$v")']" ]; then
    echo "$name: REFUSED — full request signature" \
         "$(json_field "$rec" 'list(d["batch"]["full_elided_signatures"])') is not the" \
         "pinned $(sigf_for "$v") (a request field changed; generation-config keys" \
         "$(json_field "$rec" 'list(d["batch"]["generation_config_keys"])'))"
    return 1
  fi
  echo "$name: rehearsed — $(json_field "$rec" 'd["batch"]["n_lines"]') requests," \
       "0 clients, signature $(sig_for "$v" | cut -c1-12)…"
}

# -----------------------------------------------------------------------------
# verify_one LEG — gate, then launch one leg (launch_leg). SPENDS.
# -----------------------------------------------------------------------------
verify_one() {
  local arm=$1 v=$2 name pidf ld n rec
  name="verify-$arm-$v"
  pidf="$ST2/pids/$name.pid"; ld=$(leg_dir "$arm" "$v")
  mkdir -p "$ST2/logs" "$ST2/pids"
  if alive "$pidf"; then
    echo "$name: process $(cat "$pidf") still running — skipped"; return 0
  fi
  if [ -f "$ld/probabilities.json" ]; then
    echo "$name: already verified ($ld/probabilities.json) — skipped"; return 0
  fi
  if [ -f "$ld/batch_jobs.json" ] && [ "${FORCE:-0}" != 1 ]; then
    echo "$name: REFUSED — $ld/batch_jobs.json records job(s) lodged by an earlier" \
         "attempt, and no probabilities.json was written. Those jobs may still be" \
         "running and billing. Read their state first; a job that finished or was" \
         "lost while polling is retrieved with run_pv.py batch-recover (card § 7," \
         "short legs). FORCE=1 lodges the WHOLE leg again as new jobs, billed in" \
         "full on top of any earlier job: use it only once every job named in" \
         "batch_jobs.json is known to have failed, and move the leg directory to" \
         "archive/ first."
    return 1
  fi
  # The union-size review band (card § 3; audit A6): a union outside it is a
  # finding for the PI before any spend; the operator then decides.
  if ! "$PY" scripts/modality_bridge_stage2_checks.py band "$arm:$v" --out "$OUT"; then
    if [ "${BAND_OK:-0}" = 1 ]; then
      echo "$name: BAND_OK=1 — proceeding outside the band, as the operator decided"
    else
      echo "$name: REFUSED — outside the review band (BAND_OK=1 overrides)"
      return 1
    fi
  fi
  # The rehearsal is the gate: coverage and the pass metas, a current union,
  # AGREES, one request per candidate, no client, the rehearsed signatures.
  rehearse "$arm" "$v" || return 1
  rec="$ST2/checks/rehearse-$arm-$v.json"
  n=$(json_field "$rec" 'd["batch"]["n_lines"]')
  launch_leg "$arm" "$v" "$n"
}

# -----------------------------------------------------------------------------
# launch_leg ARM V N — start one leg detached and wait until every chunk is
# submitted. Each attempt has its own log: an earlier attempt's log is moved
# aside (renamed with a UTC stamp, never deleted) and its pid file removed
# before the launch, so this function, `status` and `wait` read only the
# current attempt (audit A1: a relaunch was judged by the previous
# attempt's "Batch verification failed", EXIT and pid). SPENDS.
# -----------------------------------------------------------------------------
launch_leg() {
  local arm=$1 v=$2 n=$3 name log pidf chunks waited=0 old
  name="verify-$arm-$v"
  log="$ST2/logs/$name.log"; pidf="$ST2/pids/$name.pid"
  chunks=$(( (n + PER_JOB - 1) / PER_JOB ))
  mkdir -p "$ST2/logs" "$ST2/pids"
  if alive "$pidf"; then
    echo "$name: REFUSED — process $(cat "$pidf") is still running; not relaunching"
    return 1
  fi
  if [ -f "$log" ]; then
    old="$log.$(date -u +%Y%m%dT%H%M%SZ)"
    [ -e "$old" ] && old="$old.$$"
    mv "$log" "$old"
    echo "$name: the earlier attempt's log is kept as $old"
  fi
  rm -f "$pidf"

  mapfile -t ARGS < <(verify_args "$arm" "$v")
  echo "=== $(date -Is) LAUNCH $name: $PY scripts/run_pv.py verify ${ARGS[*]}" >> "$log"
  # The wrapper writes its own pid, then runs the leg as its child and
  # records the exit status, so `status` and `wait` can read how it ended
  # (rc is taken first: $? read after $(date) would be date's status). The
  # job closes descriptor 9, the launcher's lock, so a polling leg does not
  # hold it for hours.
  PYTHONUNBUFFERED=1 nohup bash -c 'echo $$ > "$0"; "$@"; rc=$?; echo "=== $(date -Is) EXIT $rc"' \
    "$pidf" "$PY" scripts/run_pv.py verify "${ARGS[@]}" >> "$log" 2>&1 < /dev/null 9>&- &
  while [ ! -s "$pidf" ] && [ "$waited" -lt 30 ]; do sleep 1; waited=$((waited + 1)); done
  if [ ! -s "$pidf" ]; then
    echo "$name: no pid file after ${waited}s — read $log; verifying stops here"
    return 1
  fi
  echo "$name: started pid $(cat "$pidf"), log $log; $n candidates in $chunks job(s)"
  waited=0
  while :; do
    if [ "$(grep -cE 'Submitted batch job [0-9]+/[0-9]+:' "$log")" -ge "$chunks" ]; then
      echo "=== $(date -Is) SUBMITTED $name" >> "$log"
      echo "$name: submitted ($(grep -E 'Submitted batch job [0-9]+/[0-9]+:' "$log" |
        awk '{print $NF}' | tr '\n' ' '))"
      sleep "$LODGE_GAP"
      return 0
    fi
    if grep -qiE 'failed to lodge|storage cap|Refusing|Batch verification failed' "$log"; then
      echo "$name: LODGING FAILED — read $log; verifying stops here"
      return 1
    fi
    if ! alive "$pidf"; then
      echo "$name: EXITED before every chunk was submitted — read $log; verifying stops here"
      return 1
    fi
    if [ "$waited" -ge "$LODGE_TIMEOUT" ]; then
      echo "$name: not every chunk submitted after ${waited}s — verifying stops; the" \
           "process is left running (pid $(cat "$pidf"))"
      return 1
    fi
    sleep "${LODGE_POLL:-15}"
    waited=$((waited + ${LODGE_POLL:-15}))
  done
}

# -----------------------------------------------------------------------------
# status — per leg: process, log age, exit, chunks submitted, results, and
# failure lines (case-insensitive). No API.
# -----------------------------------------------------------------------------
status() {
  local leg arm v name log pidf live ld res perr exitl fails
  for leg in $LEGS; do
    read -r arm v < <(leg_parts "$leg")
    name="verify-$arm-$v"; log="$ST2/logs/$name.log"; pidf="$ST2/pids/$name.pid"
    ld=$(leg_dir "$arm" "$v")
    if [ ! -f "$log" ]; then
      printf '%-28s not launched; union %s, crops %s\n' "$name" \
        "$([ -f "$(union_path "$arm")" ] && echo yes || echo no)" \
        "$([ -f "$(crops_dir "$arm")/candidate_manifest.json" ] && echo yes || echo no)"
      continue
    fi
    live=-; [ -f "$pidf" ] && { alive "$pidf" && live=ALIVE || live=gone; }
    exitl=$(grep -E '^=== .* EXIT [0-9]+$' "$log" | tail -1 | awk '{print $NF}')
    res=-; perr=-
    if [ -f "$ld/probabilities.json" ]; then
      res="$(json_field "$ld/probabilities.json" 'len(d["results"])')/$(json_field "$(crops_dir "$arm")/candidate_manifest.json" 'len(d["candidates"])')"
      perr=$(json_field "$ld/probabilities.json" 'sum(str(r.get("reasoning", "")).startswith("PARSE_ERROR") for r in d["results"].values())')
    fi
    fails=$(grep -ciE 'failed|lost|partial|completeness gap|traceback|error|refus|storage cap' "$log")
    # Only the current attempt's log is read; earlier attempts' logs were
    # moved aside at relaunch (audit A1) and are only counted.
    printf '%-28s %-5s age %6ss exit %-2s submitted %s results %s parse-errors %s fail-lines %s earlier-attempts %s\n' \
      "$name" "$live" "$(( $(date +%s) - $(stat -c %Y "$log") ))" "${exitl:--}" \
      "$(grep -cE 'Submitted batch job [0-9]+/[0-9]+:' "$log")" "$res" "$perr" "$fails" \
      "$(find "$ST2/logs" -maxdepth 1 -name "$name.log.*" | wc -l)"
    grep -iE 'failed|lost|partial|completeness gap|traceback|error|refus|storage cap' "$log" |
      tail -2 | cut -c1-150 | sed 's/^/    | /'
  done
}

# -----------------------------------------------------------------------------
# wait_leg LEG — block until the leg is terminal; exit status as
# scripts/wait_for_run.py (0 success, 2 partial, 3 crashed, 5 stopped).
# -----------------------------------------------------------------------------
wait_leg() {
  local arm v name
  read -r arm v < <(leg_parts "$1") || return 1
  name="verify-$arm-$v"
  # A polling leg logs an HTTP GET for its job about every 30 s (run_pv.py
  # sets the root logger to INFO), so an hour of silence is a hang (audit A3;
  # first written here as "silent", with a 25 h window, which was wrong).
  # The log is the current attempt's only (launch_leg moves earlier ones).
  "$PY" scripts/wait_for_run.py --log "$ST2/logs/$name.log" --pidfile "$ST2/pids/$name.pid" \
    --stale-seconds 3600 --poll "${WAIT_POLL:-60}" --marker 'success=^=== .* EXIT 0$' \
    --marker 'partial=^=== .* EXIT [1-9][0-9]*$'
}

# -----------------------------------------------------------------------------
# estimate — per leg: candidates (the built union, else the guide), the
# review band and cost at the original legs' audited per-candidate rates
# (card § 3). Refuses (exit 1) when a built union lies outside its band,
# unless BAND_OK=1 (audit A6). No API.
# -----------------------------------------------------------------------------
estimate() {
  local -a extra=()
  [ "${BAND_OK:-0}" = 1 ] && extra=(--band-ok)
  "$PY" scripts/modality_bridge_stage2_checks.py estimate --out "$OUT" "${extra[@]}"
}

# -----------------------------------------------------------------------------
# repair LEG — re-parse the leg's PARSE_ERROR rows from batch_results.jsonl
# with the real-time path's repair, into <leg>_repaired/ (audit A2; card
# § 7). The leg directory is not written. No API.
# -----------------------------------------------------------------------------
repair() {
  local arm=$1 v=$2 ld
  ld=$(leg_dir "$arm" "$v")
  [ -f "$ld/probabilities.json" ] && [ -f "$ld/batch_results.jsonl" ] ||
    { echo "verify-$arm-$v: REFUSED — no probabilities.json and batch_results.jsonl in $ld"; return 1; }
  "$PY" scripts/modality_bridge_stage2_checks.py repair "$ld"
}

# -----------------------------------------------------------------------------
# plan — every step's command. No API.
# -----------------------------------------------------------------------------
plan() {
  local arm leg v
  for arm in $ARMS; do
    echo "# $arm (K = $(k_for "$arm"))"
    echo "$PY scripts/modality_bridge_union.py --layout batch --cell-dir $OUT/$arm/$(version_for "$arm") --k $(k_for "$arm") --out-root $OUT/$arm --manifest $MANIFEST --write"
    echo "$PY scripts/run_pv.py extract --proposer $(union_path "$arm") --output-dir $(crops_dir "$arm") --tiles-dir $TILES --rasters-dir $RASTERS"
    echo "$PY scripts/check_union_provenance.py --manifest $(crops_dir "$arm")/candidate_manifest.json"
  done
  for leg in $LEGS; do
    read -r arm v < <(leg_parts "$leg")
    echo "$PY scripts/run_pv.py verify $(verify_args "$arm" "$v" | tr '\n' ' ')"
  done
}

expand_arms() {
  local s
  for s in "$@"; do
    if [ "$s" = all ]; then echo $ARMS; continue; fi
    k_for "$s" >/dev/null || return 1
    echo "$s"
  done
}

expand_legs() {
  local s
  for s in "$@"; do
    if [ "$s" = all ]; then echo $LEGS; continue; fi
    leg_parts "$s" >/dev/null || return 1
    echo "$s"
  done
}

# take_lock — one writing subcommand at a time (audit A4: two `verify` runs
# could otherwise both pass the alive and batch_jobs.json checks and lodge
# one leg twice). Held on descriptor 9 until the command exits; a launched
# leg closes 9 (launch_leg), so a polling leg never holds it.
take_lock() {
  mkdir -p "$ST2"
  exec 9> "$ST2/stage2.lock"
  if ! flock -n 9; then
    echo "REFUSED: another Stage 2 command holds $ST2/stage2.lock" >&2
    exit 1
  fi
}

# Dispatch only when run, not when sourced (the tier-1 tests source this
# file to exercise launch_leg with a test double).
[[ "${BASH_SOURCE[0]}" == "$0" ]] || return 0

cmd=${1:-}
shift || true
case "$cmd" in
  union|extract|provenance|prepare|rehearse|verify|repair) take_lock ;;
esac
case "$cmd" in
  plan) plan ;;
  validate-chain)
    "$PY" scripts/modality_bridge_union.py --validate-originals "$SCRATCH/validate" \
      --json-out "$ST2/checks/validate-chain.json" ;;
  anchor-gate)
    "$PY" scripts/modality_bridge_anchors.py --json-out "$ST2/checks/anchor-gate.json" ;;
  check|union|extract|provenance|prepare)
    [ $# -gt 0 ] || { echo "$cmd needs: all | ARM ..." >&2; exit 2; }
    arms=$(expand_arms "$@") || exit 2
    fn=$cmd; [ "$cmd" = prepare ] && fn=prepare_one
    for arm in $arms; do
      # Every subcommand refuses a pass set short of exact coverage.
      if [ "$cmd" = provenance ]; then check "$arm" || exit 1; fi
      "$fn" "$arm" || exit 1
    done ;;
  estimate) estimate ;;
  rehearse|verify|repair)
    [ $# -gt 0 ] || { echo "$cmd needs: all | ARM:V ..." >&2; exit 2; }
    legs=$(expand_legs "$@") || exit 2
    fn=$cmd; [ "$cmd" = verify ] && fn=verify_one
    for leg in $legs; do
      read -r arm v < <(leg_parts "$leg")
      "$fn" "$arm" "$v" || exit 1
    done
    if [ "$cmd" = verify ]; then echo "LODGING DONE $(date -Is)"; fi ;;
  status) status ;;
  wait) [ $# -eq 1 ] || { echo "wait needs one ARM:V" >&2; exit 2; }; wait_leg "$1" ;;
  *)
    sed -n '2,102p' "$0"
    exit 2 ;;
esac
