#!/usr/bin/env bash
# =============================================================================
# Session 78 — Verifier Calibration Matrix RE-RUN: Phases B, C, D (2026-04-25)
# =============================================================================
#
# Purpose
# -------
# Run Phase B (cell sweeps), Phase C (materialise + deep evaluation at 20 m
# optimum), and Phase D (calibration matrix) for the 14 verifier-calibration
# matrix cells, after Phase A re-run produces fresh probabilities.json files.
#
# Inputs (pre-existing, on origin/main after Stage 1):
# * outputs/h11/pv-diag-384/flash-high-{image,text}-n5/{image,text}-t0.7/
#     session-78-matrix/shared-crops/candidate_manifest.json
# * outputs/.../session-78-matrix/verified-{variant}/probabilities.json (14 of)
# * inputs/vectors/bounds/384/full_evaluation_bounds.geojson
# * inputs/vectors/references/mounds-reference.geojson
#
# Phases
# ------
# B. Re-run scripts/score_leaderboard_cells.py for all 14 cells with the same
#    threshold grid as the original (vote 1-5; prob 0.0/0.05/.../0.6;
#    buffers 20/30/40/50 m). Writes results/leaderboard/cells/session-78-*.json
#    overwriting the existing committed cells.
# C. Materialise geojson at the 20 m optimum (vote_t, prob_t) for each cell,
#    then run scripts/evaluate_detections.py with 10k bootstrap + MCC. Writes
#    results/verifier-calibration-matrix/{pool}-{variant}-opt-20m.geojson and
#    results/verifier-calibration-matrix/{pool}-{variant}/evaluation.{json,csv,md}.
# D. Patch scripts/compute_session78_calibration_matrix.py:resolve_prob_path
#    so the canonical variant resolves to session-78-matrix/verified-adversarial-text
#    (not verified-v1-n5), then run the script. Refreshes 14 calibration.json
#    files + planning/session-78-matrix-calibration-summary.md.
#
# Each phase commits + pushes its own atomic batch (one commit per phase).
#
# Author: Shawn Ross, Claude Opus 4.7 (1M context)
# Licence: Apache 2.0
# =============================================================================

set -u
set -o pipefail

REPO="/home/shawn/Code/map-reader-llm"
cd "$REPO" || { echo "FATAL: repo not found at $REPO" >&2; exit 2; }

PYTHON="$REPO/.venv/bin/python"
LOG_ROOT="$REPO/logs/session-78-matrix-rerun-bcd"
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
    "verify_adversarial-text"
    "verify_brief"
    "verify_brief-text"
    "verify_checklist"
    "verify_checklist-text"
    "verify_comparative"
)

CELLS_ROOT="results/leaderboard/cells"
RESULTS_ROOT="results/verifier-calibration-matrix"

mkdir -p "$CELLS_ROOT" "$RESULTS_ROOT"

# --- Utility functions -------------------------------------------------------

log() {
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] $*"
}

slug() {
    echo "${1#verify_}"
}

# Extract optimum (vote_t, prob_t) at 20 m from a cell JSON.
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

# --- Pre-flight --------------------------------------------------------------

log "=================================================================="
log "Session 78 verifier-calibration matrix RE-RUN — Phases B/C/D"
log "=================================================================="
log "Repo commit: $(git rev-parse HEAD)"
log "Python:      $PYTHON"
log "Variants:    ${VARIANTS[*]}"
log ""

# Verify all 14 probabilities.json files are present (i.e. Phase A done).
for pool_spec in "image $IMAGE_POOL" "text $TEXT_POOL"; do
    read -r pool_name pool_dir <<< "$pool_spec"
    for variant in "${VARIANTS[@]}"; do
        s="$(slug "$variant")"
        probs="${pool_dir}/verified-${s}/probabilities.json"
        if [[ ! -e "$probs" ]]; then
            log "FATAL: required probabilities.json missing: $probs"
            exit 3
        fi
    done
done

log "Pre-flight: all 14 probabilities.json files present."
log ""

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

for pool_spec in "image $IMAGE_POOL" "text $TEXT_POOL"; do
    read -r pool_name pool_dir <<< "$pool_spec"
    for variant in "${VARIANTS[@]}"; do
        run_phase_b_cell "$pool_name" "$pool_dir" "$variant"
    done
done

log "  waiting on all Phase B sweeps..."
wait
log "Phase B done in $(( $(date +%s) - phase_b_start ))s"

# Validate cell JSONs.
phase_b_ok=0
phase_b_fail=0
for pool_spec in "image" "text"; do
    for variant in "${VARIANTS[@]}"; do
        s="$(slug "$variant")"
        cell_json="${CELLS_ROOT}/session-78-${pool_spec}-${s}-487tile.json"
        if [[ -e "$cell_json" ]]; then
            phase_b_ok=$((phase_b_ok + 1))
        else
            phase_b_fail=$((phase_b_fail + 1))
            log "  [FAIL] missing: $cell_json"
        fi
    done
done
log "Phase B summary: $phase_b_ok ok / $phase_b_fail failed"

if [[ $phase_b_fail -gt 0 ]]; then
    log "FATAL: Phase B had failures; aborting before Phase C"
    exit 4
fi

# Phase B commit + push.
git add "$CELLS_ROOT"/session-78-*-487tile.json
if git diff --cached --quiet; then
    log "Phase B: no staged changes (skip commit)"
else
    git commit -m "data(s78-rerun): Phase B — 14 cell sweep tables regenerated

Re-derived from new Phase A probabilities (14 cells = 7 verifier prompt
variants x 2 candidate pools). Threshold grid matches original Session 78:
vote_t in {1,2,3,4,5}, prob_t in {0.0,0.05,...,0.6}, buffers {20,30,40,50}.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
    git push origin main
    log "Phase B: committed + pushed"
fi
log ""

# =============================================================================
# PHASE C — Deep evaluations at 20 m optimum (materialise + bootstrap)
# =============================================================================

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

    local opt
    opt=$(extract_opt_20m "$cell_json")
    if [[ -z "$opt" ]]; then
        log "  [SKIP] $key — no 20m optimum"
        return 102
    fi
    local opt_vt opt_pt
    read -r opt_vt opt_pt <<< "$opt"
    log "  evaluating: $key @ vote_t=$opt_vt prob_t=$opt_pt"

    mkdir -p "$eval_dir"

    "$PYTHON" scripts/materialise_pv_geojson.py \
        --consensus "$consensus" \
        --probabilities "$probs" \
        --vote-t "$opt_vt" \
        --prob-t "$opt_pt" \
        --output "$mat_geojson" \
        > "$eval_log" 2>&1 \
    && "$PYTHON" scripts/evaluate_detections.py \
        --detections "$mat_geojson" \
        --ground-truth "$GT" \
        --bounds "$BOUNDS" \
        --buffers 5 10 15 20 25 30 35 40 45 50 \
        --bootstrap 10000 --seed 42 --mcc \
        --output-dir "$eval_dir" \
        --label "session-78-${key}-opt" \
        >> "$eval_log" 2>&1
    local rc=$?
    if [[ $rc -eq 0 ]]; then
        log "  [OK] eval $key"
    else
        log "  [FAIL] eval $key exit=$rc"
    fi
    return $rc
}

log "### PHASE C — DEEP EVALUATIONS @ 20 M OPTIMUM ###"
phase_c_start=$(date +%s)

# 4-at-a-time concurrency for bootstrap-heavy work.
MAX_PARALLEL_C=4
c_pids=()

run_with_throttle() {
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

# Validate.
phase_c_ok=0
phase_c_fail=0
for pool_name in image text; do
    for variant in "${VARIANTS[@]}"; do
        s="$(slug "$variant")"
        ev="${RESULTS_ROOT}/${pool_name}-${s}/evaluation.json"
        if [[ -e "$ev" ]]; then
            phase_c_ok=$((phase_c_ok + 1))
        else
            phase_c_fail=$((phase_c_fail + 1))
            log "  [FAIL] missing: $ev"
        fi
    done
done
log "Phase C summary: $phase_c_ok ok / $phase_c_fail failed"

if [[ $phase_c_fail -gt 0 ]]; then
    log "WARN: Phase C had failures; continuing to commit what landed"
fi

# Phase C commit + push.
git add "$RESULTS_ROOT"/*-opt-20m.geojson "$RESULTS_ROOT"/*/evaluation.* 2>/dev/null
if git diff --cached --quiet; then
    log "Phase C: no staged changes (skip commit)"
else
    git commit -m "data(s78-rerun): Phase C — 14 materialised geojsons + deep evaluations

Materialised at each cell's per-buffer-20m optimum (vote_t, prob_t),
then evaluated at 5 m increments (5-50 m) with 10 000-iteration bootstrap
and tile-level MCC. 14 cells = 7 verifier prompt variants x 2 pools.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
    git push origin main
    log "Phase C: committed + pushed"
fi
log ""

# =============================================================================
# PHASE D — Calibration matrix
# =============================================================================

log "### PHASE D — CALIBRATION MATRIX ###"
phase_d_start=$(date +%s)

# Patch the canonical-path resolution so canonical variant resolves to
# the new shared-crops location (not legacy verified-v1-n5).
"$PYTHON" - <<'PY'
import re
from pathlib import Path
p = Path("scripts/compute_session78_calibration_matrix.py")
src = p.read_text()
# Replace the legacy canonical branch with the same path used for novel variants.
old = (
    "def resolve_prob_path(pool_dir: Path, variant: str) -> Path:\n"
    '    """Return path to probabilities.json for a given variant on a pool."""\n'
    "    if variant == CANONICAL_VARIANT:\n"
    '        return pool_dir / "verified-v1-n5" / "probabilities.json"\n'
    "    return (\n"
    "        pool_dir\n"
    '        / "session-78-matrix"\n'
    '        / f"verified-{variant}"\n'
    '        / "probabilities.json"\n'
    "    )"
)
new = (
    "def resolve_prob_path(pool_dir: Path, variant: str) -> Path:\n"
    '    """Return path to probabilities.json for a given variant on a pool.\n'
    "\n"
    "    After the 2026-04-25 re-run, canonical (adversarial-text) lives in\n"
    "    session-78-matrix alongside the novel variants — all share the same\n"
    "    shared-crops candidate set. The legacy verified-v1-n5 path is\n"
    "    no longer canonical for this matrix.\n"
    '    """\n'
    "    return (\n"
    "        pool_dir\n"
    '        / "session-78-matrix"\n'
    '        / f"verified-{variant}"\n'
    '        / "probabilities.json"\n'
    "    )"
)
if old not in src:
    raise SystemExit("Patch target not found in compute_session78_calibration_matrix.py")
p.write_text(src.replace(old, new))
print("Patched compute_session78_calibration_matrix.py:resolve_prob_path")
PY

# Run the calibration matrix script.
"$PYTHON" scripts/compute_session78_calibration_matrix.py \
    > "$LOG_ROOT/phase-d.log" 2>&1
phase_d_rc=$?
log "Phase D script exit: $phase_d_rc"

if [[ $phase_d_rc -ne 0 ]]; then
    log "FATAL: Phase D failed; see $LOG_ROOT/phase-d.log"
    exit 5
fi

log "Phase D done in $(( $(date +%s) - phase_d_start ))s"

# Phase D commit + push.
git add scripts/compute_session78_calibration_matrix.py \
        "$RESULTS_ROOT"/*/calibration.json \
        planning/session-78-matrix-calibration-summary.md 2>/dev/null
if git diff --cached --quiet; then
    log "Phase D: no staged changes (skip commit)"
else
    git commit -m "data(s78-rerun): Phase D — calibration matrix refreshed (canonical at shared-crops)

After the 2026-04-25 re-run, the canonical adversarial-text variant
shares the same candidate pool as the six alternatives. Patched
compute_session78_calibration_matrix.py so resolve_prob_path uses
session-78-matrix/verified-adversarial-text for the canonical variant
(previously verified-v1-n5). Refreshes all 14 calibration.json files +
planning/session-78-matrix-calibration-summary.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
    git push origin main
    log "Phase D: committed + pushed"
fi

log ""
log "=================================================================="
log "Session 78 Phases B/C/D re-run complete."
log "=================================================================="
