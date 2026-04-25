#!/usr/bin/env bash
# Stage 2 driver: build the 12-stratum F1 + MCC tier matrix.
#
# Per the per-arch leaderboard 12-stratum redesign brief
# (Session 79, 2026-04-25): 7 populated strata x 2 metrics
# (F1, MCC) x 2 FDR levels (q=0.05 base, q=0.01 sensitivity).
#
# Stratum coverage:
#   Era 1 single-pass (21), Era 1 consensus (75)
#   Era 2 single-pass (~7), Era 2 consensus (~29),
#   Era 2 single-pass+PV (8 PV_READY), Era 2 pv (44)
#   Era 3 consensus (14)
#
# Empty strata (Era 1 single-pass+PV, Era 1 pv, Era 3 single-pass,
# Era 3 single-pass+PV, Era 3 pv) get stub READMEs separately.
#
# Workers per build: 8. Outer loop runs sequentially, but each build's
# evaluation cache is reused for the q=0.01 sensitivity rerun. The
# pairwise cache is metric-specific and reused across q levels.

set -e

cd /home/shawn/Code/map-reader-llm

LOG_DIR=logs/per-arch-leaderboards-rebuild-2026-04-25
mkdir -p "$LOG_DIR"

INVENTORY=planning/condition-inventory-with-s78.json
BOUNDS_512=inputs/vectors/bounds/full_evaluation_bounds.geojson
BOUNDS_384=inputs/vectors/bounds/384/full_evaluation_bounds.geojson
BOUNDS_327=inputs/vectors/bounds/384/h10_test_bounds.geojson
BUFFERS="20 30 40 50 100"
WORKERS=8
BOOTSTRAP=1000
N_PERM=10000
SEED=42

# Status filter per stratum. PV_READY conditions are the
# verifier-cleared subset; SINGLE_PASS_ONLY conditions are
# single-pass cells that use a different output layout.
STATUS_DEFAULT="--status READY"
STATUS_SINGLE_PASS="--status READY SINGLE_PASS_ONLY"
STATUS_PV="--status READY PV_READY"

# Strata definitions: era, architecture, bounds, status filter
# (cells matching this combination are built; empty strata are
# skipped here and get a stub README in Stage 5).
declare -a STRATA=(
    "1|single-pass|$BOUNDS_512|$STATUS_SINGLE_PASS"
    "1|consensus|$BOUNDS_512|$STATUS_DEFAULT"
    "2|single-pass|$BOUNDS_384|$STATUS_SINGLE_PASS"
    "2|consensus|$BOUNDS_384|$STATUS_DEFAULT"
    "2|single-pass+PV|$BOUNDS_384|$STATUS_PV"
    "2|pv|$BOUNDS_384|$STATUS_PV"
    "3|consensus|$BOUNDS_327|$STATUS_DEFAULT"
)

run_stratum_metric() {
    local era="$1"
    local arch="$2"
    local bounds="$3"
    local status_args="$4"
    local metric="$5"
    local fdr_q="$6"
    local extra_args="$7"

    local out_dir="results/leaderboard/per-architecture/era${era}/${arch}"
    mkdir -p "$out_dir"

    local tag
    tag="era${era}-${arch}-${metric}-q$(echo "$fdr_q" | tr -d '.')"
    local log_file="${LOG_DIR}/${tag}.log"

    echo "[$(date -u +%H:%M:%S)] Building: $tag"
    .venv/bin/python scripts/build_tiered_leaderboard.py \
        --inventory "$INVENTORY" \
        --era "$era" \
        --architecture "$arch" \
        --bounds "$bounds" \
        $status_args \
        --buffers $BUFFERS \
        --primary-buffer 20 \
        --metric "$metric" \
        --fdr-q "$fdr_q" \
        --workers $WORKERS \
        --bootstrap $BOOTSTRAP \
        --n-permutations $N_PERM \
        --seed $SEED \
        --top-n 0 \
        $extra_args \
        --output-dir "$out_dir" \
        > "$log_file" 2>&1
    local rc=$?
    if [ $rc -eq 0 ]; then
        echo "    OK ($log_file)"
    else
        echo "    FAILED (rc=$rc, see $log_file)"
    fi
    return $rc
}

for stratum in "${STRATA[@]}"; do
    IFS='|' read -r era arch bounds status_args <<< "$stratum"
    echo "=== Era $era $arch ==="
    # Pass 1: F1 at q=0.05. Caches were archived in
    # archive/leaderboard-caches/2026-04-25-pre-mcc-cache-fix/ before
    # this driver was launched, so the first pass starts fresh: it
    # populates the eval cache (with tile_classification, MCC) and
    # the F1 pairwise cache.
    run_stratum_metric "$era" "$arch" "$bounds" "$status_args" \
        "f1" "0.05" ""
    # Pass 2: F1 at q=0.01 (sensitivity, reuse caches just written).
    run_stratum_metric "$era" "$arch" "$bounds" "$status_args" \
        "f1" "0.01" "--skip-evaluation --skip-pairwise"
    # Pass 3: MCC at q=0.05 (eval cache reused; runs MCC pairwise
    # since pairwise cache is metric-specific).
    run_stratum_metric "$era" "$arch" "$bounds" "$status_args" \
        "mcc" "0.05" "--skip-evaluation"
    # Pass 4: MCC at q=0.01 (sensitivity, reuse caches).
    run_stratum_metric "$era" "$arch" "$bounds" "$status_args" \
        "mcc" "0.01" "--skip-evaluation --skip-pairwise"
done

echo "=== Stage 2 complete ==="

# Stage 3: tier-stability tables for each populated stratum + metric.
# Cheap (no permutation tests) — runs sequentially in <1 min total.
echo
echo "=== Stage 3: tier-stability tables ==="
for metric in f1 mcc; do
    .venv/bin/python scripts/build_tier_stability.py \
        --metric "$metric" --all \
        > "$LOG_DIR/tier-stability-$metric.log" 2>&1
    rc=$?
    if [ $rc -eq 0 ]; then
        echo "  OK: tier-stability $metric"
    else
        echo "  FAILED: tier-stability $metric (rc=$rc)"
    fi
done

# Stage 4: cross-architecture flat (4a) + paired (4b) + MC flags (4c).
echo
echo "=== Stage 4: cross-architecture tables + MC flags ==="
.venv/bin/python scripts/build_cross_architecture_tables.py \
    --metric both --stage all \
    > "$LOG_DIR/stage4.log" 2>&1
rc=$?
if [ $rc -eq 0 ]; then
    echo "  OK: Stage 4 (4a+4b+4c)"
else
    echo "  FAILED: Stage 4 (rc=$rc)"
fi

# Stage 5: per-stratum READMEs + top-level README + headlines.
echo
echo "=== Stage 5: documentation ==="
.venv/bin/python scripts/build_per_arch_documentation.py --what all \
    > "$LOG_DIR/stage5-docs.log" 2>&1
rc=$?
if [ $rc -eq 0 ]; then
    echo "  OK: Stage 5 docs"
else
    echo "  FAILED: Stage 5 docs (rc=$rc)"
fi

echo
echo "=== Pipeline complete ==="
date
