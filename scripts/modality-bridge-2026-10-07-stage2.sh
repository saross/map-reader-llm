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
#                 residual file outstanding.
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
#                 and the request signature the card rehearsed against the
#                 original legs' real-time requests.
#   6. verify     run_pv.py verify --mode batch --temperature 0.0 with the
#                 Gemini 3 (gemini-3-flash-preview) or Gemini 3.7
#                 (gemini-3.7-flash, thinking low) verifier. SPENDS.
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
#
# Launch hygiene (docs/agent-guidance.md § Compute Location). A verifier leg
# starts detached under a wrapper shell that writes its OWN pid to the pid
# file, runs the leg with all three descriptors redirected and
# PYTHONUNBUFFERED=1, and appends "=== <time> EXIT <status>" when it ends;
# nothing follows the launch on its line. Legs are lodged one at a time: the
# next starts only after the previous has logged every chunk's "Submitted
# batch job" line, so each storage preflight sees the earlier uploads. A
# polling verifier writes NOTHING between submission and its job's end, so
# the pid (kill -0, never pgrep -f) is the liveness signal, not log age;
# the poll itself gives up after 25 h. Never kill a polling leg: its job
# keeps running, and batch_jobs.json in the leg directory names it
# (run_pv.py batch-recover). `verify` refuses a leg whose directory holds
# batch_jobs.json without probabilities.json.
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
cd "$(dirname "$0")/.." || exit 1

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
  echo "$name: rehearsed — $(json_field "$rec" 'd["batch"]["n_lines"]') requests," \
       "0 clients, signature $(sig_for "$v" | cut -c1-12)…"
}

# -----------------------------------------------------------------------------
# verify_one LEG — gate, then launch one leg detached and wait for every
# chunk's submission. SPENDS.
# -----------------------------------------------------------------------------
verify_one() {
  local arm=$1 v=$2 name log pidf ld n chunks waited=0 rec
  name="verify-$arm-$v"
  log="$ST2/logs/$name.log"; pidf="$ST2/pids/$name.pid"; ld=$(leg_dir "$arm" "$v")
  mkdir -p "$ST2/logs" "$ST2/pids"
  if alive "$pidf"; then
    echo "$name: process $(cat "$pidf") still running — skipped"; return 0
  fi
  if [ -f "$ld/probabilities.json" ]; then
    echo "$name: already verified ($ld/probabilities.json) — skipped"; return 0
  fi
  if [ -f "$ld/batch_jobs.json" ] && [ "${FORCE:-0}" != 1 ]; then
    echo "$name: REFUSED — $ld/batch_jobs.json records job(s) lodged earlier and no" \
         "probabilities.json was written; a job may still be running. Recover it" \
         "with run_pv.py batch-recover (FORCE=1 overrides)."
    return 1
  fi
  # The rehearsal is the gate: coverage, a current union, AGREES, one
  # request per candidate, no client, the rehearsed signature.
  rehearse "$arm" "$v" || return 1
  rec="$ST2/checks/rehearse-$arm-$v.json"
  n=$(json_field "$rec" 'd["batch"]["n_lines"]')
  chunks=$(( (n + PER_JOB - 1) / PER_JOB ))

  mapfile -t ARGS < <(verify_args "$arm" "$v")
  echo "=== $(date -Is) LAUNCH $name: $PY scripts/run_pv.py verify ${ARGS[*]}" >> "$log"
  # The wrapper writes its own pid, then runs the leg as its child and
  # records the exit status, so `status` and `wait` can read how it ended
  # (rc is taken first: $? read after $(date) would be date's status).
  PYTHONUNBUFFERED=1 nohup bash -c 'echo $$ > "$0"; "$@"; rc=$?; echo "=== $(date -Is) EXIT $rc"' \
    "$pidf" "$PY" scripts/run_pv.py verify "${ARGS[@]}" >> "$log" 2>&1 < /dev/null &
  while [ ! -s "$pidf" ] && [ "$waited" -lt 30 ]; do sleep 1; waited=$((waited + 1)); done
  echo "$name: started pid $(cat "$pidf" 2>/dev/null), log $log; $n candidates in $chunks job(s)"
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
    sleep 15
    waited=$((waited + 15))
  done
}

# -----------------------------------------------------------------------------
# status — per leg: process, log age, exit, chunks submitted, results, and
# failure lines (case-insensitive). No API.
# -----------------------------------------------------------------------------
status() {
  local leg arm v name log pidf live ld res exitl fails
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
    res=-
    [ -f "$ld/probabilities.json" ] &&
      res="$(json_field "$ld/probabilities.json" 'len(d["results"])')/$(json_field "$(crops_dir "$arm")/candidate_manifest.json" 'len(d["candidates"])')"
    fails=$(grep -ciE 'failed|lost|partial|completeness gap|traceback|error|refus|storage cap' "$log")
    printf '%-28s %-5s age %6ss exit %-2s submitted %s results %s fail-lines %s\n' \
      "$name" "$live" "$(( $(date +%s) - $(stat -c %Y "$log") ))" "${exitl:--}" \
      "$(grep -cE 'Submitted batch job [0-9]+/[0-9]+:' "$log")" "$res" "$fails"
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
  # Staleness is not a signal here (a polling leg is silent), so the window
  # is the poll's own 25 h cap; the pid and the EXIT line decide.
  "$PY" scripts/wait_for_run.py --log "$ST2/logs/$name.log" --pidfile "$ST2/pids/$name.pid" \
    --stale-seconds 90000 --marker 'success=^=== .* EXIT 0$' \
    --marker 'partial=^=== .* EXIT [1-9][0-9]*$'
}

# -----------------------------------------------------------------------------
# estimate — per leg, candidates and cost at the register's per-candidate
# rates (the original legs' audited cost / candidates; card § 3). Legs whose
# union is not built yet are priced at the guide size given. No API.
# -----------------------------------------------------------------------------
estimate() {
  "$PY" - "$LEGS" "$OUT" <<'PYEOF'
import json
import sys
from pathlib import Path

legs, out = sys.argv[1].split(), Path(sys.argv[2])
# Audited cost / candidates of the original legs (results/passes-manifest.json
# via each leg's cost_audit.json): Gemini 3 verifier 2.271158/3319 to
# 0.478101/674; Gemini 3.7 verifier 0.737004/674 (card: 0.87/791).
rate = {"g3": (2.271158 / 3319, 0.478101 / 674), "g37": (0.737004 / 674, 0.87 / 791)}
# Guide sizes until a union exists: the originals' unions; for the temp1 and
# cache arms, their twins' through this chain (the T 0.7 passes 1-5: text
# 2,714, image 2,788; g37-image 674). The Stage 1 card's 2,932 for text is
# the merge_passes consensus-n5 union, not this chain (Stage 2 card § 3).
guide = {"g3-text": 3319, "g3-image": 4065, "g37-text": 791, "g37-image": 674,
         "g37-image-cache": 674, "g3-text-temp1": 2714, "g3-image-temp1": 2788}
version = {"g3-text": "detect_brief-text", "g37-text": "detect_brief-text",
           "g3-text-temp1": "detect_brief-text"}
k = {"g3-text": 10, "g3-image": 10}
lo_t = hi_t = 0.0
for leg in legs:
    arm, v = leg.split(":")
    build = (out / arm / "verifier" / version.get(arm, "detect_brief-text-image")
             / f"union_k{k.get(arm, 5)}.build.json")
    n, src = (json.loads(build.read_text())["union_features"], "union") \
        if build.exists() else (guide[arm], "guide")
    lo, hi = sorted(n * r for r in rate[v])
    lo_t += lo
    hi_t += hi
    print(f"{leg:22s} {n:6d} ({src:5s})  US${lo:6.2f} - {hi:6.2f}")
print(f"{'total':22s} {'':14s}  US${lo_t:6.2f} - {hi_t:6.2f}")
PYEOF
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

cmd=${1:-}
shift || true
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
  rehearse|verify)
    [ $# -gt 0 ] || { echo "$cmd needs: all | ARM:V ..." >&2; exit 2; }
    legs=$(expand_legs "$@") || exit 2
    fn=rehearse; [ "$cmd" = verify ] && fn=verify_one
    for leg in $legs; do
      read -r arm v < <(leg_parts "$leg")
      "$fn" "$arm" "$v" || exit 1
    done
    if [ "$cmd" = verify ]; then echo "LODGING DONE $(date -Is)"; fi ;;
  status) status ;;
  wait) [ $# -eq 1 ] || { echo "wait needs one ARM:V" >&2; exit 2; }; wait_leg "$1" ;;
  *)
    sed -n '2,75p' "$0"
    exit 2 ;;
esac
