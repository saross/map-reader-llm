#!/usr/bin/env bash
# =============================================================================
# Session 78 — Verifier Calibration Matrix (Overnight Pipeline)
# =============================================================================
#
# Purpose
# -------
# Run a 2-pool × 6-variant verifier calibration matrix against the frozen
# Session 78 candidate pools, then sweep thresholds and deep-evaluate each
# cell at its 20 m optimum. Produces 12 leaderboard-cell JSONs + 12 deep
# evaluation directories + a summary markdown.
#
# Pools
# -----
# * Image:  outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/
# * Text:   outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/
#
# Variants (6 per pool)
# ---------------------
# 1. verify_adversarial           (with-images)
# 2. verify_brief                 (with-images)
# 3. verify_brief-text            (no-images)
# 4. verify_checklist             (with-images)
# 5. verify_checklist-text        (no-images)
# 6. verify_comparative           (with-images, new Session 78)
#
# Excludes `verify_adversarial-text` (canonical baseline already run).
#
# Phases
# ------
# A. 12 verifier runs (6 variants × 2 pools) — image pool first, text pool
#    second. Within a pool, 6 variants run concurrently (--workers 35).
# B. 12 leaderboard-cell sweeps (score_leaderboard_cells.py).
# C. 12 deep evaluations at per-buffer-20m optimum (10 k bootstrap + MCC).
# D. Summary markdown with success/failure table and F1@20 m per cell.
# E. Git commit (no push).
#
# Logging
# -------
# * Top-level log (this script's nohup output):
#     logs/session-78-matrix-overnight.log
# * Per-variant API run logs:
#     logs/session-78-matrix/{image,text}-<variant>.log
# * Per-variant sweep logs:
#     logs/session-78-matrix/sweep-{image,text}-<variant>.log
# * Per-variant evaluation logs:
#     logs/session-78-matrix/eval-{image,text}-<variant>.log
#
# Safety
# ------
# * No `set -e`: a failed variant should not abort the pipeline. Each phase
#   records exit statuses and continues.
# * Missing canonical inputs are checked up front; script aborts if absent.
# * Does NOT push commits; leaves the local commit for human review.
#
# Author: Shawn Ross, Claude Code (Opus 4.7)
# Licence: Apache 2.0
# =============================================================================

set -u  # treat unset variables as errors; we do NOT use `set -e` (see above)
set -o pipefail

REPO="/home/shawn/Code/map-reader-llm"
cd "$REPO" || { echo "FATAL: repo not found at $REPO" >&2; exit 2; }

PYTHON="$REPO/.venv/bin/python"
LOG_ROOT="$REPO/logs/session-78-matrix"
mkdir -p "$LOG_ROOT"

# --- Configuration -----------------------------------------------------------

IMAGE_POOL="outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix"
TEXT_POOL="outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix"

IMAGE_CONSENSUS="outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/consensus-n5/consensus_t1.geojson"
TEXT_CONSENSUS="outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/consensus-n5/consensus_t1.geojson"

BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
GT="inputs/vectors/references/mounds-reference.geojson"

VARIANTS=(
    "verify_adversarial"
    "verify_brief"
    "verify_brief-text"
    "verify_checklist"
    "verify_checklist-text"
    "verify_comparative"
)

WORKERS=35
SERVICE_TIER="flex"

RESULTS_ROOT="results/verifier-calibration-matrix"
CELLS_ROOT="results/leaderboard/cells"
SUMMARY_MD="planning/session-78-verifier-calibration-matrix-summary.md"

mkdir -p "$RESULTS_ROOT" "$CELLS_ROOT" "$(dirname "$SUMMARY_MD")"

# --- Utility functions -------------------------------------------------------

# Timestamped log line to the main (stdout-captured) log.
log() {
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] $*"
}

# Short slug for a variant (strip the "verify_" prefix).
slug() {
    echo "${1#verify_}"
}

# --- Pre-flight --------------------------------------------------------------

log "=================================================================="
log "Session 78 Verifier Calibration Matrix — overnight pipeline"
log "=================================================================="
log "Repo commit: $(git rev-parse HEAD)"
log "Python:      $PYTHON"
log "Workers:     $WORKERS"
log "Tier:        $SERVICE_TIER"
log "Variants:    ${VARIANTS[*]}"
log ""

# Check all inputs up front.
for f in "$IMAGE_POOL/shared-crops/candidate_manifest.json" \
         "$TEXT_POOL/shared-crops/candidate_manifest.json" \
         "$IMAGE_CONSENSUS" "$TEXT_CONSENSUS" \
         "$BOUNDS" "$GT"; do
    if [[ ! -e "$f" ]]; then
        log "FATAL: required input missing: $f"
        exit 3
    fi
done

for v in "${VARIANTS[@]}"; do
    if [[ ! -e "prompts/configs/${v}.json" ]]; then
        log "FATAL: verifier config missing: prompts/configs/${v}.json"
        exit 3
    fi
done

log "Pre-flight input checks passed."
log ""

# Arrays to track exit statuses for the summary.
declare -A PHASE_A_RC
declare -A PHASE_B_RC
declare -A PHASE_C_RC

# =============================================================================
# PHASE A — Matrix API runs
# =============================================================================

run_phase_a_pool() {
    local pool_name="$1"      # "image" | "text"
    local pool_dir="$2"

    log "----------------------------------------------------------------"
    log "Phase A — $pool_name pool — launching ${#VARIANTS[@]} variants concurrently"
    log "----------------------------------------------------------------"
    local start_ts=$(date +%s)

    local pids=()
    local pid_variant=()

    for variant in "${VARIANTS[@]}"; do
        local s="$(slug "$variant")"
        local out_dir="${pool_dir}/verified-${s}"
        local var_log="$LOG_ROOT/${pool_name}-${s}.log"

        log "  launching: $pool_name / $variant -> $out_dir"

        "$PYTHON" scripts/run_pv.py verify \
            --crops-dir "${pool_dir}/shared-crops" \
            --verifier-config "prompts/configs/${variant}.json" \
            --output-dir "$out_dir" \
            --mode realtime \
            --workers "$WORKERS" \
            --service-tier "$SERVICE_TIER" \
            --no-strict \
            > "$var_log" 2>&1 &

        pids+=($!)
        pid_variant+=("$variant")
    done

    log "  all ${#pids[@]} variants launched; waiting on pool..."

    # Wait on each PID individually so we can record per-variant exit codes.
    for i in "${!pids[@]}"; do
        local pid="${pids[$i]}"
        local variant="${pid_variant[$i]}"
        local s="$(slug "$variant")"
        local key="${pool_name}-${s}"

        if wait "$pid"; then
            PHASE_A_RC[$key]=0
            log "  [OK] $key (pid=$pid) completed"
        else
            local rc=$?
            PHASE_A_RC[$key]=$rc
            log "  [FAIL] $key (pid=$pid) exit=$rc — see $LOG_ROOT/${key}.log"
        fi
    done

    local dur=$(( $(date +%s) - start_ts ))
    log "Phase A $pool_name pool done in ${dur}s"
    log ""
}

log "### PHASE A — VERIFIER API RUNS ###"
run_phase_a_pool "image" "$IMAGE_POOL"
run_phase_a_pool "text"  "$TEXT_POOL"

# =============================================================================
# PHASE B — Leaderboard cell sweeps
# =============================================================================

run_phase_b_cell() {
    local pool_name="$1"
    local pool_dir="$2"
    local variant="$3"
    local s="$(slug "$variant")"
    local key="${pool_name}-${s}"
    local out_dir="${pool_dir}/verified-${s}"
    local probs="${out_dir}/probabilities.json"
    local manifest="${pool_dir}/shared-crops/candidate_manifest.json"
    local cell_json="${CELLS_ROOT}/session-78-${key}-487tile.json"
    local sweep_log="$LOG_ROOT/sweep-${key}.log"

    if [[ ! -e "$probs" ]]; then
        log "  [SKIP] $key — probabilities.json missing ($probs)"
        PHASE_B_RC[$key]=100
        return
    fi

    log "  sweeping: $key -> $cell_json"

    "$PYTHON" scripts/score_leaderboard_cells.py \
        --manifest "$manifest" \
        --probs "$probs" \
        --bounds "$BOUNDS" \
        --gt "$GT" \
        --label "session-78-${key}" \
        --track "$pool_name" \
        --aggregation greedy \
        --verifier "session-78-${s}" \
        --vote-thresholds "1,2,3,4,5" \
        --prob-thresholds "0.0,0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50,0.60" \
        --buffers "20,30,40,50" \
        --output "$cell_json" \
        > "$sweep_log" 2>&1 &
}

log "### PHASE B — LEADERBOARD CELL SWEEPS ###"
phase_b_start=$(date +%s)

phase_b_keys=()
for pool_spec in "image $IMAGE_POOL" "text $TEXT_POOL"; do
    read -r pool_name pool_dir <<< "$pool_spec"
    for variant in "${VARIANTS[@]}"; do
        run_phase_b_cell "$pool_name" "$pool_dir" "$variant"
        phase_b_keys+=("${pool_name}-$(slug "$variant")")
    done
done

# Wait for all sweeps (all backgrounded). Record per-key RC via exit of wait.
log "  waiting on all Phase B sweeps..."
# We backgrounded with `&` inside run_phase_b_cell but did not capture PIDs.
# Use `wait` (no args) to wait for ALL children, then re-check output files.
wait

# Validate each cell JSON exists and record RC (0 if exists, 1 if not).
for key in "${phase_b_keys[@]}"; do
    if [[ -z "${PHASE_B_RC[$key]+x}" ]]; then
        if [[ -e "${CELLS_ROOT}/session-78-${key}-487tile.json" ]]; then
            PHASE_B_RC[$key]=0
            log "  [OK] sweep $key"
        else
            PHASE_B_RC[$key]=1
            log "  [FAIL] sweep $key — no cell JSON produced"
        fi
    fi
done

log "Phase B done in $(( $(date +%s) - phase_b_start ))s"
log ""

# =============================================================================
# PHASE C — Deep evaluation at per-buffer-20 m optimum
# =============================================================================

# Extract optimum (vote_t, prob_t) at 20 m from a cell JSON.
# Returns "VOTE_T PROB_T" on stdout, or empty string if not resolvable.
extract_opt_20m() {
    local cell_json="$1"
    "$PYTHON" - "$cell_json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
if not p.exists():
    sys.exit(1)
data = json.loads(p.read_text())
opt = data.get("optima_per_buffer", {}).get("20")
if not opt:
    # Some cell JSONs may key buffers as int or floats; try alternates.
    for k in ("20.0", 20, "20m"):
        opt = data.get("optima_per_buffer", {}).get(k)
        if opt:
            break
if not opt:
    sys.exit(1)
vt = opt.get("vote_t")
pt = opt.get("prob_t")
if vt is None or pt is None:
    sys.exit(1)
print(f"{vt} {pt}")
PY
}

run_phase_c_cell() {
    local pool_name="$1"
    local pool_dir="$2"
    local consensus="$3"
    local variant="$4"
    local s="$(slug "$variant")"
    local key="${pool_name}-${s}"
    local cell_json="${CELLS_ROOT}/session-78-${key}-487tile.json"
    local probs="${pool_dir}/verified-${s}/probabilities.json"
    local eval_dir="${RESULTS_ROOT}/${key}"
    local mat_geojson="${RESULTS_ROOT}/${key}-opt-20m.geojson"
    local eval_log="$LOG_ROOT/eval-${key}.log"

    if [[ "${PHASE_B_RC[$key]:-99}" -ne 0 ]]; then
        log "  [SKIP] $key — Phase B failed"
        PHASE_C_RC[$key]=101
        return
    fi

    local opt
    opt=$(extract_opt_20m "$cell_json")
    if [[ -z "$opt" ]]; then
        log "  [SKIP] $key — could not extract 20m optimum from $cell_json"
        PHASE_C_RC[$key]=102
        return
    fi
    local opt_vt opt_pt
    read -r opt_vt opt_pt <<< "$opt"
    log "  evaluating: $key @ vote_t=$opt_vt prob_t=$opt_pt -> $eval_dir"

    mkdir -p "$eval_dir"

    # Materialise geojson at optimum.
    {
        "$PYTHON" scripts/materialise_pv_geojson.py \
            --consensus "$consensus" \
            --probabilities "$probs" \
            --vote-t "$opt_vt" \
            --prob-t "$opt_pt" \
            --output "$mat_geojson" \
        && "$PYTHON" scripts/evaluate_detections.py \
            --detections "$mat_geojson" \
            --ground-truth "$GT" \
            --bounds "$BOUNDS" \
            --buffers 5 10 15 20 25 30 35 40 45 50 \
            --bootstrap 10000 --seed 42 --mcc \
            --output-dir "$eval_dir" \
            --label "session-78-${key}-opt"
    } > "$eval_log" 2>&1
    local rc=$?
    PHASE_C_RC[$key]=$rc
    if [[ $rc -eq 0 ]]; then
        log "  [OK] eval $key"
    else
        log "  [FAIL] eval $key exit=$rc"
    fi
}

log "### PHASE C — DEEP EVALUATIONS ###"
phase_c_start=$(date +%s)

# Run evaluations with limited concurrency (4 at a time) — each uses CPU
# for bootstrap. We use a simple job-slot pattern.
MAX_PARALLEL_C=4
c_pids=()

run_with_throttle() {
    # Wait if we already have MAX_PARALLEL_C jobs running.
    while [[ ${#c_pids[@]} -ge $MAX_PARALLEL_C ]]; do
        local new_pids=()
        for p in "${c_pids[@]}"; do
            if kill -0 "$p" 2>/dev/null; then
                new_pids+=("$p")
            fi
        done
        c_pids=("${new_pids[@]}")
        if [[ ${#c_pids[@]} -ge $MAX_PARALLEL_C ]]; then
            sleep 5
        fi
    done
}

for pool_spec in "image $IMAGE_POOL $IMAGE_CONSENSUS" "text $TEXT_POOL $TEXT_CONSENSUS"; do
    read -r pool_name pool_dir consensus <<< "$pool_spec"
    for variant in "${VARIANTS[@]}"; do
        run_with_throttle
        run_phase_c_cell "$pool_name" "$pool_dir" "$consensus" "$variant" &
        c_pids+=($!)
    done
done

# Wait on remaining Phase C jobs.
for p in "${c_pids[@]}"; do
    wait "$p" 2>/dev/null || true
done

log "Phase C done in $(( $(date +%s) - phase_c_start ))s"
log ""

# =============================================================================
# PHASE D — Summary markdown
# =============================================================================

log "### PHASE D — SUMMARY ###"

"$PYTHON" - <<PY > "$SUMMARY_MD"
"""Write Session 78 verifier calibration matrix summary."""
import json
from pathlib import Path
from datetime import datetime

REPO = Path("$REPO")
RESULTS_ROOT = REPO / "$RESULTS_ROOT"
CELLS_ROOT = REPO / "$CELLS_ROOT"
POOLS = [("image", "$IMAGE_POOL"), ("text", "$TEXT_POOL")]
VARIANTS = "${VARIANTS[*]}".split()

def slug(v: str) -> str:
    return v[len("verify_"):] if v.startswith("verify_") else v

lines = []
lines.append("# Session 78 — Verifier Calibration Matrix Summary")
lines.append("")
lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
lines.append("")
lines.append("## Scope")
lines.append("")
lines.append("* 2 candidate pools: image-T=0.7 (2 017 candidates), text-T=0.7 (3 736 candidates)")
lines.append("* 6 verifier prompt variants each = 12 total verifier runs")
lines.append("* Scope: 487-tile Era 2 full evaluation bounds")
lines.append("")
lines.append("## Results table — F1 @ 20 m at per-buffer optimum")
lines.append("")
lines.append("| Pool | Variant | vote_t | prob_t | F1 @ 20 m | Precision | Recall | MCC |")
lines.append("|------|---------|-------:|-------:|----------:|----------:|-------:|----:|")

rows = []
for pool_name, pool_dir in POOLS:
    for v in VARIANTS:
        s = slug(v)
        key = f"{pool_name}-{s}"
        cell = CELLS_ROOT / f"session-78-{key}-487tile.json"
        eval_json = RESULTS_ROOT / key / "evaluation.json"
        vt = pt = f1 = prec = rec = mcc = "—"
        if cell.exists():
            try:
                cdata = json.loads(cell.read_text())
                opt = cdata.get("optima_per_buffer", {}).get("20") or \
                      cdata.get("optima_per_buffer", {}).get("20.0") or \
                      cdata.get("optima_per_buffer", {}).get(20)
                if opt:
                    vt = str(opt.get("vote_t", "—"))
                    pt = str(opt.get("prob_t", "—"))
            except Exception as e:
                pass
        if eval_json.exists():
            try:
                edata = json.loads(eval_json.read_text())
                # evaluate_detections.py writes a results list keyed by buffer.
                # Walk a few likely structures.
                buf20 = None
                if isinstance(edata, dict):
                    for k in ("buffers", "results", "per_buffer"):
                        if k in edata:
                            for entry in edata[k]:
                                b = entry.get("buffer_m") or entry.get("buffer") or entry.get("buffer_distance_m")
                                if b in (20, 20.0, "20"):
                                    buf20 = entry
                                    break
                            if buf20:
                                break
                    if not buf20 and "20" in edata:
                        buf20 = edata["20"]
                if buf20:
                    f1 = f"{buf20.get('f1', buf20.get('f1_mean', 0)):.3f}" if buf20.get('f1') is not None or buf20.get('f1_mean') is not None else "—"
                    prec = f"{buf20.get('precision', buf20.get('precision_mean', 0)):.3f}" if buf20.get('precision') is not None or buf20.get('precision_mean') is not None else "—"
                    rec = f"{buf20.get('recall', buf20.get('recall_mean', 0)):.3f}" if buf20.get('recall') is not None or buf20.get('recall_mean') is not None else "—"
                    mcc_val = buf20.get('mcc') or buf20.get('mcc_mean')
                    mcc = f"{mcc_val:.3f}" if mcc_val is not None else "—"
            except Exception as e:
                pass
        rows.append(f"| {pool_name} | {s} | {vt} | {pt} | {f1} | {prec} | {rec} | {mcc} |")

lines.extend(rows)
lines.append("")
lines.append("## Artefact locations")
lines.append("")
lines.append("* Leaderboard cell sweeps: \`results/leaderboard/cells/session-78-*.json\`")
lines.append("* Deep evaluations: \`results/verifier-calibration-matrix/<pool>-<variant>/\`")
lines.append("* Materialised GeoJSONs at optima: \`results/verifier-calibration-matrix/<pool>-<variant>-opt-20m.geojson\`")
lines.append("* Logs: \`logs/session-78-matrix/\`")
lines.append("")
lines.append("## Canonical baseline (not re-run)")
lines.append("")
lines.append("\`verify_adversarial-text\` is the canonical verifier; its probabilities and downstream evaluations are preserved from prior sessions and remain the reference for cross-prompt comparison.")
lines.append("")

print("\n".join(lines))
PY

log "Wrote summary: $SUMMARY_MD"
log ""

# Also write a top-level status log.
{
    log "=== Phase A exit codes ==="
    for k in "${!PHASE_A_RC[@]}"; do log "  $k: ${PHASE_A_RC[$k]}"; done
    log "=== Phase B exit codes ==="
    for k in "${!PHASE_B_RC[@]}"; do log "  $k: ${PHASE_B_RC[$k]}"; done
    log "=== Phase C exit codes ==="
    for k in "${!PHASE_C_RC[@]}"; do log "  $k: ${PHASE_C_RC[$k]}"; done
} | tee "$LOG_ROOT/exit-codes.log"

# =============================================================================
# PHASE E — Git commit (no push)
# =============================================================================

log "### PHASE E — GIT COMMIT ###"

git add "$CELLS_ROOT"/session-78-*.json 2>/dev/null || true
git add "$RESULTS_ROOT" 2>/dev/null || true
git add "$SUMMARY_MD" 2>/dev/null || true
git add scripts/session-78-matrix-overnight.sh 2>/dev/null || true
git add "$LOG_ROOT" 2>/dev/null || true

if git diff --cached --quiet; then
    log "No staged changes to commit."
else
    git commit -m "$(cat <<'EOF'
data(session-78): verifier calibration matrix — 12 runs, sweeps, deep evals

6 verifier variants × 2 candidate pools (image T=0.7 N=5 1-of-5;
text T=0.7 N=5 1-of-5) at 487-tile Era 2 scope. Canonical
verify_adversarial-text baseline unchanged; 5 existing alternative
prompts + 1 new (verify_comparative) tested.

Artefacts:
* results/leaderboard/cells/session-78-*.json (12 sweep cells)
* results/verifier-calibration-matrix/<pool>-<variant>/ (12 deep evals)
* planning/session-78-verifier-calibration-matrix-summary.md (summary)

Service tier: flex (50% discount, 1-15 min latency).
Workers: 35 per variant. Concurrency: 6 variants per pool, pools
sequential (image first, text second) to avoid rate-limit contention.

See logs/session-78-matrix/exit-codes.log for per-variant status.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)" || log "git commit returned non-zero (see stderr)"
    log "Commit created: $(git rev-parse HEAD)"
fi

log ""
log "=================================================================="
log "Session 78 matrix pipeline complete."
log "=================================================================="
