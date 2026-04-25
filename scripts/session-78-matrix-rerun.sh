#!/usr/bin/env bash
# =============================================================================
# Session 78 — Verifier Calibration Matrix RE-RUN (2026-04-25)
# =============================================================================
#
# Purpose
# -------
# Re-run Phase A of the Session 78 verifier-calibration matrix after the
# 2026-04-25 confabulation-cascade data-loss event. Produces 14 verifier
# probabilities.json files (7 prompt variants × 2 candidate pools), with
# per-variant commit + push to provide protective intermediate checkpoints.
#
# Differences from the original session-78-matrix-overnight.sh
# ------------------------------------------------------------
# 1. All 7 variants (the original excluded `verify_adversarial-text` because
#    the canonical baseline used `verified-v1-n5/probabilities.json`; the
#    re-run includes it so canonical and alternatives share crops).
# 2. Per-variant commit + push after each verifier completes (data loss
#    mitigation — never lose more than one variant's worth of work).
# 3. Logs go to `logs/session-78-matrix-rerun/` to keep history distinct
#    from `logs/session-78-matrix/` (the original).
# 4. This script only runs Phase A. Phases B, C, D run in Stage 2 of the
#    re-derivation procedure (separate script invocations).
#
# Pools
# -----
# * Image:  outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/
# * Text:   outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/
#
# Variants (7 per pool)
# ---------------------
# 1. verify_adversarial           (with-images)
# 2. verify_adversarial-text      (canonical, no-images)
# 3. verify_brief                 (with-images)
# 4. verify_brief-text            (no-images)
# 5. verify_checklist             (with-images)
# 6. verify_checklist-text        (no-images)
# 7. verify_comparative           (with-images, new Session 78)
#
# Author: Shawn Ross, Claude Opus 4.7 (1M context)
# Licence: Apache 2.0
# =============================================================================

set -u  # treat unset variables as errors; we do NOT use `set -e` (see below)
set -o pipefail

REPO="/home/shawn/Code/map-reader-llm"
cd "$REPO" || { echo "FATAL: repo not found at $REPO" >&2; exit 2; }

PYTHON="$REPO/.venv/bin/python"
LOG_ROOT="$REPO/logs/session-78-matrix-rerun"
mkdir -p "$LOG_ROOT"

# --- Configuration -----------------------------------------------------------

IMAGE_POOL="outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix"
TEXT_POOL="outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix"

VARIANTS=(
    "verify_adversarial"
    "verify_adversarial-text"
    "verify_brief"
    "verify_brief-text"
    "verify_checklist"
    "verify_checklist-text"
    "verify_comparative"
)

WORKERS=35
SERVICE_TIER="flex"

# --- Utility functions -------------------------------------------------------

# Timestamped log line to the main (stdout-captured) log.
log() {
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] $*"
}

# Short slug for a variant (strip the "verify_" prefix).
slug() {
    echo "${1#verify_}"
}

# Read total_cost_usd from a run.meta.json (returns "0" if not found / unreadable).
cost_from_meta() {
    local meta="$1"
    "$PYTHON" - "$meta" <<'PY' 2>/dev/null || echo "0"
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
if not p.exists():
    print("0"); sys.exit(0)
try:
    d = json.loads(p.read_text())
    cost = d.get("total_cost_usd") or d.get("cost_usd") or 0
    print(f"{float(cost):.4f}")
except Exception:
    print("0")
PY
}

# --- Pre-flight --------------------------------------------------------------

log "=================================================================="
log "Session 78 Verifier Calibration Matrix — RE-RUN (Phase A only)"
log "=================================================================="
log "Repo commit: $(git rev-parse HEAD)"
log "Python:      $PYTHON"
log "Workers:     $WORKERS"
log "Tier:        $SERVICE_TIER"
log "Variants:    ${VARIANTS[*]}"
log ""

# Check all inputs up front.
for f in "$IMAGE_POOL/shared-crops/candidate_manifest.json" \
         "$TEXT_POOL/shared-crops/candidate_manifest.json"; do
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

# --- Cumulative-cost tracking ------------------------------------------------
TOTAL_COST="0"

bump_cost() {
    local meta="$1"
    local label="$2"
    local c
    c=$(cost_from_meta "$meta")
    TOTAL_COST=$("$PYTHON" -c "print(f'{${TOTAL_COST} + ${c}:.4f}')")
    log "  cost: ${label} = \$${c} | cumulative total = \$${TOTAL_COST}"
}

# --- Per-pool driver ---------------------------------------------------------

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
        local out_dir="${pool_dir}/verified-${s}"

        if wait "$pid"; then
            log "  [OK] ${pool_name}-${s} (pid=$pid) completed"
        else
            local rc=$?
            log "  [FAIL] ${pool_name}-${s} (pid=$pid) exit=$rc — see $LOG_ROOT/${pool_name}-${s}.log"
        fi

        # Per-variant commit + push (regardless of exit status — preserve any
        # partial output that did land).
        local probs="${out_dir}/probabilities.json"
        local meta="${out_dir}/run.meta.json"

        if [[ -e "$probs" ]]; then
            # Count entries + failures for the commit message.
            local n_probs n_fail
            n_probs=$("$PYTHON" -c "import json; print(len(json.loads(open('$probs').read())))" 2>/dev/null || echo "?")
            n_fail=$("$PYTHON" -c "
import json
d = json.loads(open('$probs').read())
print(sum(1 for k, v in d.items() if v is None or (isinstance(v, dict) and v.get('error'))))
" 2>/dev/null || echo "?")

            log "  ${pool_name}-${s}: ${n_probs} entries, ${n_fail} failed"
            bump_cost "$meta" "${pool_name}-${s}"

            git add "$out_dir/" 2>/dev/null || true
            if git diff --cached --quiet; then
                log "  ${pool_name}-${s}: no staged changes (skipping commit)"
            else
                if git commit -m "data(s78-rerun): Phase A — ${s} on ${pool_name} pool (${n_probs} candidates scored, ${n_fail} failed)" \
                    -m "Per-variant commit during Session 78 verifier-calibration matrix re-run." \
                    -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"; then
                    if git push origin main; then
                        log "  ${pool_name}-${s}: committed + pushed"
                    else
                        log "  ${pool_name}-${s}: commit OK but push FAILED — manual recovery required"
                    fi
                else
                    log "  ${pool_name}-${s}: git commit failed"
                fi
            fi
        else
            log "  ${pool_name}-${s}: probabilities.json MISSING — nothing to commit"
        fi
    done

    local dur=$(( $(date +%s) - start_ts ))
    log "Phase A $pool_name pool done in ${dur}s | cumulative total = \$${TOTAL_COST}"
    log ""
}

log "### PHASE A — VERIFIER API RUNS (RE-RUN) ###"
run_phase_a_pool "image" "$IMAGE_POOL"
run_phase_a_pool "text"  "$TEXT_POOL"

log ""
log "=================================================================="
log "Session 78 Phase A re-run complete."
log "Cumulative cost (sum of run.meta.json total_cost_usd): \$${TOTAL_COST}"
log "=================================================================="
