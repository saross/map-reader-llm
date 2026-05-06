#!/usr/bin/env bash
# =============================================================================
# Phase 3a Verifier Completeness — Recovery Campaign Driver (TEMPLATE)
# =============================================================================
#
# Purpose:
#     Operationalises the recovery procedure described in
#     planning/phase3a-verifier-recovery-runbook.md. Loops the 19 verifier-
#     output cells in tier order, calls `run_pv.py cleanup`, runs per-cell
#     re-evaluation, and pauses for operator confirmation at tier boundaries
#     and at the cost-validation cell within Tier 2.
#
#     The 11 derived cells are NOT cleaned up directly — they are regenerated
#     via `scripts/derive_vote_threshold_results.py` from their cleaned
#     sources.
#
# Status:
#     TEMPLATE / DRAFT. NOT executable as-is. Operator must:
#       1. Verify the software-fix sentinel landed and populate
#          `.phase3a-recovery-fix-landed` (see § "Sentinel check" below).
#       2. Audit each PER-CELL block before launching its tier.
#       3. Strip the .template suffix (`mv ... run-phase3a-recovery.sh`)
#          and `chmod +x` only after operator review.
#       4. Confirm cost approval at the API Call Review Gate.
#
# Invocation (after enabling):
#     bash planning/run-phase3a-recovery.sh [tier1|tier2|tier3|all]
#
# Author: Claude Opus 4.7 (1M context) / Shawn Ross (operator)
# Date:   2026-05-03 (Session 85 prep)
# Licence: Apache 2.0
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

LOG_DIR="logs/phase3a-recovery-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$LOG_DIR"

TIER="${1:-tier1}"  # tier1 | tier2 | tier3 | all

# Non-interactive bypass for unattended overnight runs.
# When NON_INTERACTIVE=1, skip operator-go `read -r` prompts at:
#   - tier-boundary checkpoints (tier_boundary_confirm)
#   - $5 cost-confirm-threshold soft prompt
#   - intra-Tier-2 image-t0.0 cost-validation pause
# All ABORT-on-error safeties remain in force:
#   - $10 hard cost cap (exit 3)
#   - sentinel check (exit 2)
#   - working-tree-clean check (exit 2)
#   - cleanup-failure handling (return 1, ledger logs FAILED)
#   - residual gap_after > 0 WARN (continues to next cell with logged failure)
# Approval for this bypass: user pre-authorised the campaign with $10 hard cap
# on 2026-05-03 night; see logs/phase3a-recovery-overnight/launch-summary.md.
NON_INTERACTIVE="${NON_INTERACTIVE:-0}"

CONFIG_DIR="prompts/configs"
COST_LOG="$LOG_DIR/cost-ledger.csv"
echo "tier,cell,gap_before,gap_after,recovered,cleanup_cost_usd,wall_clock_s,timestamp" > "$COST_LOG"

# Cost-budget thresholds (USD)
COST_CONFIRM_THRESHOLD=5.00
COST_HARD_CAP=10.00
CUMULATIVE_COST=0

# -----------------------------------------------------------------------------
# Skip list — cells whose crops are missing (gitignored bulk intermediates)
# and so cannot be cleaned up without first regenerating crops.
#
# These three cells were identified during the 2026-05-03 overnight run when
# `run_pv.py cleanup` reported "Crop file not found" for every candidate
# (see logs/phase3a-recovery-20260503T145815Z/tier1-e47-flash-high-text-1of5.log
# for the e47 case). They are skipped here so the rest of the campaign can
# complete unattended. Recovery requires a separate `extract_candidates.py`
# (or equivalent) pass to regenerate the crop PNGs before cleanup can succeed.
#
# When a cell is skipped, a `gap_after=$gap_before, recovered=0,
# reason=missing_crops_gitignored` row is written to the cost-ledger so the
# operator has an explicit record by morning.
# -----------------------------------------------------------------------------
SKIP_CELLS=(
    "e47-flash-high-text-1of5"
    "55maps-gen-verified-v2"
    "proposer-verifier-384-adversarial-text-v1-prompt"
)
declare -A SKIP_REASON
SKIP_REASON["e47-flash-high-text-1of5"]="missing_crops_gitignored"
SKIP_REASON["55maps-gen-verified-v2"]="missing_crops_gitignored"
SKIP_REASON["proposer-verifier-384-adversarial-text-v1-prompt"]="missing_crops_gitignored"

# Returns 0 (true) if the supplied cell name is in SKIP_CELLS.
is_cell_skipped() {
    local needle="$1"
    local c
    for c in "${SKIP_CELLS[@]}"; do
        if [[ "$c" == "$needle" ]]; then
            return 0
        fi
    done
    return 1
}

# -----------------------------------------------------------------------------
# Sentinel check — refuse to proceed if software fix has not landed
# -----------------------------------------------------------------------------

SENTINEL=".phase3a-recovery-fix-landed"
if [[ ! -s "$SENTINEL" ]]; then
    echo "ERROR: Software-fix sentinel '$SENTINEL' missing or empty." >&2
    echo "       The verifier-completeness pipeline-level guard must land" >&2
    echo "       on main before this campaign runs. To unblock:" >&2
    echo "         git log -1 --format=%H > $SENTINEL" >&2
    echo "       (after verifying the fix commit is on main)." >&2
    exit 2
fi
FIX_COMMIT=$(cat "$SENTINEL" | head -c 40)
echo "Software-fix commit: $FIX_COMMIT"

# Working tree clean?
if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree not clean. Commit or stash before recovery." >&2
    exit 2
fi

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

# Compute pre-cleanup gap for sanity record. Uses the audit's logic inline.
compute_gap() {
    local crops_dir="$1"
    local verified_dir="$2"
    python3 -c "
import json, sys
manifest = json.load(open('$crops_dir/candidate_manifest.json'))
expected = len(manifest.get('candidates', []))
probs = json.load(open('$verified_dir/probabilities.json'))
results = probs.get('results', {})
# Strip _iter<K> suffix for consensus-mode keys
seen = set()
for k in results:
    base = k.split('_iter')[0] if '_iter' in k else k
    seen.add(base)
gap = expected - len(seen)
print(gap)
"
}

# Run cleanup for one cell, capture cost from the freshly-written run.meta.json
recover_cell() {
    local tier="$1"
    local cell_name="$2"
    local crops_dir="$3"
    local verified_dir="$4"
    local config="$5"
    local extra_args="${6:-}"  # for --model / --thinking-level overrides

    local cell_log="$LOG_DIR/${tier}-${cell_name//\//_}.log"

    # Skip-list short-circuit: if a cell is in SKIP_CELLS (e.g. crops missing),
    # log a placeholder ledger row and return cleanly without invoking cleanup.
    if is_cell_skipped "$cell_name"; then
        local skip_reason="${SKIP_REASON[$cell_name]:-deferred}"
        echo ""
        echo "================================================================"
        echo "  [$tier] $cell_name  [SKIP]"
        echo "  reason: $skip_reason"
        echo "================================================================"
        local gap_skip="?"
        if [[ -d "$crops_dir" ]] && [[ -f "$crops_dir/candidate_manifest.json" ]] \
                && [[ -f "$verified_dir/probabilities.json" ]]; then
            gap_skip=$(compute_gap "$crops_dir" "$verified_dir" 2>/dev/null || echo "?")
        fi
        echo "$tier,$cell_name,$gap_skip,$gap_skip,0,0.000000,0,$(date -u +%FT%TZ),SKIP:${skip_reason}" >> "$COST_LOG"
        return 0
    fi

    local gap_before
    gap_before=$(compute_gap "$crops_dir" "$verified_dir")

    echo ""
    echo "================================================================"
    echo "  [$tier] $cell_name"
    echo "  gap_before=$gap_before"
    echo "  crops:    $crops_dir"
    echo "  verified: $verified_dir"
    echo "  config:   $config $extra_args"
    echo "================================================================"

    if [[ "$gap_before" == "0" ]]; then
        echo "  Already clean — skipping."
        echo "$tier,$cell_name,0,0,0,0.00,0,$(date -u +%FT%TZ)" >> "$COST_LOG"
        return 0
    fi

    local started_at
    started_at=$(date -u +%FT%TZ)
    local t0
    t0=$(date +%s)

    # Capture pre-recovery run.meta.json cost (if present) so we can subtract
    # later (cleanup overwrites run.meta.json — the backup-merge fix at
    # commit 7f05f529 handles this in the cost-manifest aggregator).
    local pre_meta_cost="0.0"
    if [[ -f "$verified_dir/run.meta.json" ]]; then
        pre_meta_cost=$(python3 -c "
import json
try:
    j=json.load(open('$verified_dir/run.meta.json'))
    print(j.get('cost_estimate', {}).get('total_cost_usd', 0.0))
except Exception:
    print(0.0)
")
    fi

    # Invoke run_pv.py cleanup
    if ! python scripts/run_pv.py cleanup \
        --crops-dir "$crops_dir" \
        --verified-dir "$verified_dir" \
        --verifier-config "$config" \
        --max-attempts 3 \
        --safe-mode-tokens 2048 \
        $extra_args \
        2>&1 | tee "$cell_log"; then
        echo "ERROR: cleanup failed on $cell_name — see $cell_log" >&2
        echo "$tier,$cell_name,$gap_before,?,?,?,?,$started_at,FAILED" >> "$COST_LOG"
        return 1
    fi

    local t1
    t1=$(date +%s)
    local wall=$((t1 - t0))

    # Re-audit
    local gap_after
    gap_after=$(compute_gap "$crops_dir" "$verified_dir")
    local recovered=$((gap_before - gap_after))

    # Capture cleanup cost — current run.meta.json reflects only the cleanup
    # batch (the cost-manifest aggregator handles backup-sibling merging at
    # aggregate time; for ledger purposes we record the cleanup cost only).
    local cleanup_cost
    cleanup_cost=$(python3 -c "
import json
try:
    j=json.load(open('$verified_dir/run.meta.json'))
    print(f'{j.get(\"cost_estimate\", {}).get(\"total_cost_usd\", 0.0):.6f}')
except Exception:
    print('0.000000')
")

    echo "  gap_after=$gap_after  recovered=$recovered  cost=\$${cleanup_cost}  wall=${wall}s"
    echo "$tier,$cell_name,$gap_before,$gap_after,$recovered,$cleanup_cost,$wall,$started_at" >> "$COST_LOG"

    # Update cumulative cost
    CUMULATIVE_COST=$(python3 -c "print(f'{$CUMULATIVE_COST + $cleanup_cost:.6f}')")

    # Cost-cap enforcement
    local over_hard
    over_hard=$(python3 -c "print(1 if $CUMULATIVE_COST > $COST_HARD_CAP else 0)")
    if [[ "$over_hard" == "1" ]]; then
        echo "ABORT: cumulative cost \$${CUMULATIVE_COST} exceeds hard cap \$${COST_HARD_CAP}" >&2
        exit 3
    fi
    local over_confirm
    over_confirm=$(python3 -c "print(1 if $CUMULATIVE_COST > $COST_CONFIRM_THRESHOLD else 0)")
    if [[ "$over_confirm" == "1" ]]; then
        echo "WARN: cumulative cost \$${CUMULATIVE_COST} exceeds confirm threshold \$${COST_CONFIRM_THRESHOLD}"
        if [[ "$NON_INTERACTIVE" == "1" ]]; then
            echo "      NON_INTERACTIVE=1 — auto-continuing (hard cap \$${COST_HARD_CAP} still enforced)."
        else
            echo "      Press Enter to continue, Ctrl-C to abort..."
            read -r
        fi
    fi

    # Sanity check — must be gap=0 after cleanup
    if [[ "$gap_after" != "0" ]]; then
        echo "WARN: residual gap=$gap_after on $cell_name. Continuing campaign;" >&2
        echo "      see $cell_log + run.meta.json::execution_stats.failed_items" >&2
        echo "      and the cleanup_history entry inside probabilities.json." >&2
    fi

    return 0
}

# Tier-boundary confirmation
tier_boundary_confirm() {
    local next_tier="$1"
    echo ""
    echo "==========================================================="
    echo "  Tier boundary: about to start $next_tier"
    echo "  Cumulative cost so far: \$${CUMULATIVE_COST}"
    if [[ "$NON_INTERACTIVE" == "1" ]]; then
        echo "  NON_INTERACTIVE=1 — auto-continuing to $next_tier."
        echo "==========================================================="
    else
        echo "  Press Enter to continue to $next_tier, Ctrl-C to halt."
        echo "==========================================================="
        read -r
    fi
}

# -----------------------------------------------------------------------------
# Tier 1 — paper-cited (8 cells; expected ~$0.43)
# -----------------------------------------------------------------------------

run_tier1() {
    echo ""
    echo "========================="
    echo "  TIER 1 — paper-cited"
    echo "========================="

    # Group 1A — Session 78 matrix (6 cells, batched)
    # Note: order is largest-gap first.
    recover_cell tier1 "session78-text-adversarial-text" \
        "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/shared-crops" \
        "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text" \
        "$CONFIG_DIR/verify_adversarial-text.json"

    recover_cell tier1 "session78-text-brief-text" \
        "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/shared-crops" \
        "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief-text" \
        "$CONFIG_DIR/verify_brief-text.json"

    recover_cell tier1 "session78-image-adversarial-text" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/shared-crops" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text" \
        "$CONFIG_DIR/verify_adversarial-text.json"

    recover_cell tier1 "session78-text-checklist-text" \
        "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/shared-crops" \
        "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist-text" \
        "$CONFIG_DIR/verify_checklist-text.json"

    recover_cell tier1 "session78-image-checklist-text" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/shared-crops" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist-text" \
        "$CONFIG_DIR/verify_checklist-text.json"

    recover_cell tier1 "session78-image-brief-text" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/shared-crops" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief-text" \
        "$CONFIG_DIR/verify_brief-text.json"

    # OPERATOR (manual): after the 6 Session-78 cleanups land, run the
    # propagation chain (see runbook § 6.1):
    #
    #   python scripts/materialise_session78_geojsons.py
    #   python scripts/compute_session78_calibration_matrix.py
    #   python scripts/build_tiered_leaderboard.py   # session-78 cells
    #   bash scripts/finalise_per_arch_leaderboard.sh
    #   bash scripts/build_combined_leaderboard.sh
    #   bash scripts/build_combined_tier_stability.sh
    #
    # Then commit the propagation as a separate logical group.
    # The script does NOT auto-trigger these because they are CPU-only and
    # benefit from operator review of the rebuilt leaderboard tier output.

    # Group 1B — e47-propose-brief (1 cell + 4 derivatives regenerate)
    # Path bug fixed (Session 87 — see planning/three-skipped-cells-investigation.md):
    # both --crops-dir and --verified-dir previously pointed at
    # `verified/flash-high-text-1of5/`, which has no PNGs. Canonical crops
    # directory is `crops/flash-high-text-1of5/` (with manifest + 4358 PNGs
    # under `crops/flash-high-text-1of5/crops/`).
    recover_cell tier1 "e47-flash-high-text-1of5" \
        "outputs/h11/e47-propose-brief/crops/flash-high-text-1of5" \
        "outputs/h11/e47-propose-brief/verified/flash-high-text-1of5" \
        "$CONFIG_DIR/verify_adversarial-text.json"

    # OPERATOR (manual): regenerate the 4 derivatives from the cleaned source:
    #
    #   python scripts/derive_vote_threshold_results.py \
    #       --consensus outputs/h11/e47-propose-brief/consensus/<...>.geojson \
    #       --probabilities outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/probabilities.json \
    #       --manifest outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/candidate_manifest.json \
    #       --pool-size 5 \
    #       --output-dir outputs/h11/e47-propose-brief/verified \
    #       --prefix flash-high-text
    #
    # The exact --consensus path must be confirmed from the existing
    # derived cells (their `source` and `derived_from` fields encode it).

    # Then propagation:
    #   python scripts/compare_wbf_vs_greedy_production.py
    #   python scripts/build_tiered_leaderboard.py
    #   bash scripts/finalise_per_arch_leaderboard.sh

    # Group 1C — h8-v2 WBF scale-4 (1 cell)
    recover_cell tier1 "h8v2-wbf-scale-4" \
        "outputs/h8-v2/wbf/scale-4/crops" \
        "outputs/h8-v2/wbf/scale-4/verified" \
        "$CONFIG_DIR/verify_adversarial-text.json"

    # OPERATOR (manual): re-evaluate + paired-permutation:
    #   python scripts/evaluate_detections.py \
    #       --detections outputs/h8-v2/wbf/scale-4/verified_detections.geojson \
    #       --ground-truth inputs/vectors/references/mounds-reference.geojson \
    #       <bounds + buffers per the existing cell config>
    #   python scripts/paired_permutation_consensus.py \
    #       <args for the s4-vs-s8 comparison>

    echo ""
    echo "TIER 1 COMPLETE. Cumulative cost: \$${CUMULATIVE_COST}"
}

# -----------------------------------------------------------------------------
# Tier 2 — sweep / smaller paper-cited / contamination-policy (7 cells)
# -----------------------------------------------------------------------------

run_tier2() {
    tier_boundary_confirm "Tier 2"
    echo ""
    echo "========================="
    echo "  TIER 2 — sweep / v2"
    echo "========================="

    # Cell 9 — gap=460, dominates Tier 2 cost. Stop-and-confirm internal
    # checkpoint after this cell.
    recover_cell tier2 "image-n5-t0.0-v1-n10" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/crops" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10" \
        "$CONFIG_DIR/verify_adversarial-text.json"
    echo ""
    echo "  CHECKPOINT: image-t0.0 cleanup complete. Cumulative: \$${CUMULATIVE_COST}"
    echo "  Confirm cost-per-call scaling matches estimate before continuing."
    if [[ "$NON_INTERACTIVE" == "1" ]]; then
        echo "  NON_INTERACTIVE=1 — auto-continuing Tier 2 (hard cap \$${COST_HARD_CAP} still enforced)."
    else
        echo "  Press Enter to continue Tier 2, Ctrl-C to halt."
        read -r
    fi

    recover_cell tier2 "image-n5-t0.3-v1-n5" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5/crops" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5" \
        "$CONFIG_DIR/verify_adversarial-text.json"

    recover_cell tier2 "55maps-gen-verified-v2" \
        "outputs/55maps-generalisation/crops" \
        "outputs/55maps-generalisation/verified-v2" \
        "$CONFIG_DIR/verify_adversarial-text_v2.json"

    recover_cell tier2 "image-n5-t1.0-v1-n5" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5/crops" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5" \
        "$CONFIG_DIR/verify_adversarial-text.json"

    recover_cell tier2 "image-n5-t0.7-v1-n5" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5/crops" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5" \
        "$CONFIG_DIR/verify_adversarial-text.json"

    recover_cell tier2 "session78-image-checklist" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/shared-crops" \
        "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist" \
        "$CONFIG_DIR/verify_checklist.json"

    recover_cell tier2 "scale-4-optimal-487-v1-n10" \
        "outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10/crops" \
        "outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10" \
        "$CONFIG_DIR/verify_adversarial-text.json"

    # OPERATOR (manual): batched Tier-2 propagation:
    #   python scripts/evaluate_detections.py  # for each cell
    #   python scripts/build_tiered_leaderboard.py
    #   bash scripts/finalise_per_arch_leaderboard.sh
    #   python scripts/analyse_secondary_effects.py
    #   python scripts/analyse_consensus_sd_shrinkage_v2.py
    #   python scripts/analyse_inter_pass_agreement.py
    #   python scripts/analyse_token_efficiency.py
    #   python scripts/analyse_proposer_vote_fraction.py
    # And separately for verified-v2:
    #   <threshold_sweep refresh — locate via grep -rln threshold_sweep>

    echo ""
    echo "TIER 2 COMPLETE. Cumulative cost: \$${CUMULATIVE_COST}"
}

# -----------------------------------------------------------------------------
# Tier 3 — legacy diagnostic (5 source cells; pro-medium pricing on 3 of 5)
# -----------------------------------------------------------------------------

run_tier3() {
    tier_boundary_confirm "Tier 3"
    echo ""
    echo "==============================="
    echo "  TIER 3 — legacy diagnostic"
    echo "==============================="

    # Pro-medium cells first (highest per-call cost; surface failures cheaply)
    recover_cell tier3 "text-baseline-pro-verifier" \
        "outputs/h11/pv-diag-384/crops/text-baseline" \
        "outputs/h11/pv-diag-384/verified/text-baseline-pro-verifier" \
        "$CONFIG_DIR/verify_adversarial-text.json" \
        "--model gemini-3.1-pro-preview --thinking-level medium"

    recover_cell tier3 "pro-medium-image-baseline-pro-verifier" \
        "outputs/h11/pv-diag-384/crops/pro-medium-image-baseline" \
        "outputs/h11/pv-diag-384/verified/pro-medium-image-baseline-pro-verifier" \
        "$CONFIG_DIR/verify_adversarial-text.json" \
        "--model gemini-3.1-pro-preview --thinking-level medium"

    recover_cell tier3 "pro-high-image-1of5-pro-verifier" \
        "outputs/h11/pv-diag-384/crops/pro-high-image-1of5" \
        "outputs/h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier" \
        "$CONFIG_DIR/verify_adversarial-text.json" \
        "--model gemini-3.1-pro-preview --thinking-level medium"

    # OPERATOR (manual): regenerate 5 derived pro-high-image-pro-vf-Nof5 cells
    # from the cleaned pro-high-image-1of5-pro-verifier source:
    #   python scripts/derive_vote_threshold_results.py \
    #       --consensus <consensus path from existing derived cells' `source`> \
    #       --probabilities outputs/h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier/probabilities.json \
    #       --manifest outputs/h11/pv-diag-384/crops/pro-high-image-1of5/candidate_manifest.json \
    #       --pool-size 5 \
    #       --output-dir outputs/h11/pv-diag-384/verified \
    #       --prefix pro-high-image-pro-vf

    # Flash legacy
    recover_cell tier3 "flash-high-text-1of5-flash-medium-verifier" \
        "outputs/h11/pv-diag-384/crops/flash-high-text-1of5" \
        "outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier" \
        "$CONFIG_DIR/verify_adversarial-text.json" \
        "--thinking-level medium"

    # OPERATOR (manual): regenerate flash-high-text-medium-vf-1of5 derivative
    # from the cleaned flash-high-text-1of5-flash-medium-verifier source.

    recover_cell tier3 "proposer-verifier-384-adversarial-text-v1-prompt" \
        "outputs/h11/proposer-verifier-384/candidates" \
        "outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt" \
        "$CONFIG_DIR/verify_adversarial-text.json"

    # OPERATOR (manual): Tier-3 propagation:
    #   - Re-run threshold-sweep scripts under sapphire-pro-verifier-analysis.sh
    #     for the 3 pro-medium cells.
    #   - Spot-check `results/h11-384-pv-diagnostic/` outputs for any consumers
    #     of the cleaned cells.

    echo ""
    echo "TIER 3 COMPLETE. Cumulative cost: \$${CUMULATIVE_COST}"
}

# -----------------------------------------------------------------------------
# Dispatch
# -----------------------------------------------------------------------------

case "$TIER" in
    tier1) run_tier1 ;;
    tier2) run_tier2 ;;
    tier3) run_tier3 ;;
    all)
        run_tier1
        run_tier2
        run_tier3
        ;;
    *)
        echo "Unknown tier: $TIER. Use tier1 | tier2 | tier3 | all" >&2
        exit 1
        ;;
esac

echo ""
echo "==========================================="
echo "  Recovery driver complete."
echo "  Cumulative cost: \$${CUMULATIVE_COST}"
echo "  Cost ledger:     $COST_LOG"
echo "  Per-cell logs:   $LOG_DIR/"
echo "==========================================="
echo ""
echo "Next steps (manual, per runbook § 6 + § 7):"
echo "  1. Re-evaluate affected cells (per-tier batched)."
echo "  2. Rebuild leaderboard / matrix / paired-permutation outputs."
echo "  3. Refresh paper-citation Markdown if any F1 movement > 0.001."
echo "  4. Append closure observation to docs/notes/reflections/working-notes.md."
echo "  5. Update planning/paper-writeup-continuity.md with a 'Session 85"
echo "     closure' arc."
echo "  6. Annotate reports/phase3a-verifier-completeness-audit-2026-05-03.md"
echo "     with the post-recovery status."
echo "  7. Commit + push at tier boundaries (per runbook § 9)."
