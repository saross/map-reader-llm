#!/usr/bin/env bash
# Stage 1 driver: per-buffer F1 re-tiering for the 7 populated
# per-architecture strata.
#
# Per the per-buffer F1 work plan (2026-04-26): for each populated
# stratum, re-run the tier builder at each non-primary buffer
# (30 / 40 / 50 / 100 m) using --threshold-buffer 20 (Option A
# semantics — fix per-cell thresholds at the primary buffer, re-tier
# at the chosen non-primary buffer). MCC is not re-run because the
# tile-level MCC permutation test is buffer-independent.
#
# Coverage: 7 strata x 4 non-primary buffers x 2 q levels = 56 runs.
# Per (stratum, buffer): one expensive q=0.05 pass that populates the
# F1 pairwise cache at that buffer, then a cheap q=0.01 pass that
# reuses the cache via --skip-pairwise --skip-evaluation.
#
# Eval cache from the original 12-stratum build (Session 79,
# 2026-04-25) is reused throughout (--skip-evaluation on every
# invocation).
#
# Outputs overwrite the existing leaderboard_tiers_f1_{30,40,50,100}m
# .{md,json} and leaderboard_tiers_f1_q01_{30,40,50,100}m.{md,json}
# files in each populated stratum directory. The 20 m tier files are
# unchanged because --primary-buffer 20 --threshold-buffer 20 is
# identical to the original default.

set -e

cd /home/shawn/Code/map-reader-llm

LOG_DIR=logs/per-arch-leaderboards-rebuild-2026-04-26-per-buffer-f1
mkdir -p "$LOG_DIR"

INVENTORY=planning/condition-inventory-with-s78.json
BOUNDS_512=inputs/vectors/bounds/full_evaluation_bounds.geojson
BOUNDS_384=inputs/vectors/bounds/384/full_evaluation_bounds.geojson
BOUNDS_327=inputs/vectors/bounds/384/h10_test_bounds.geojson
BUFFERS_ALL="20 30 40 50 100"
NON_PRIMARY_BUFFERS=(30 40 50 100)
WORKERS=8
BOOTSTRAP=1000
N_PERM=10000
SEED=42

STATUS_DEFAULT="--status READY"
STATUS_SINGLE_PASS="--status READY SINGLE_PASS_ONLY"
STATUS_PV="--status READY PV_READY"

# Strata definitions: era|architecture|bounds|status_args.
declare -a STRATA=(
    "1|single-pass|$BOUNDS_512|$STATUS_SINGLE_PASS"
    "1|consensus|$BOUNDS_512|$STATUS_DEFAULT"
    "2|single-pass|$BOUNDS_384|$STATUS_SINGLE_PASS"
    "2|consensus|$BOUNDS_384|$STATUS_DEFAULT"
    "2|single-pass+PV|$BOUNDS_384|$STATUS_PV"
    "2|pv|$BOUNDS_384|$STATUS_PV"
    "3|consensus|$BOUNDS_327|$STATUS_DEFAULT"
)

run_buffer_pass() {
    local era="$1"
    local arch="$2"
    local bounds="$3"
    local status_args="$4"
    local buffer="$5"
    local fdr_q="$6"
    local extra_args="$7"

    local out_dir="results/leaderboard/per-architecture/era${era}/${arch}"
    local tag
    tag="era${era}-${arch}-f1-q$(echo "$fdr_q" | tr -d '.')-buf${buffer}m"
    local log_file="${LOG_DIR}/${tag}.log"

    echo "[$(date -u +%H:%M:%S)] Building: $tag"
    .venv/bin/python scripts/build_tiered_leaderboard.py \
        --inventory "$INVENTORY" \
        --era "$era" \
        --architecture "$arch" \
        --bounds "$bounds" \
        $status_args \
        --buffers $BUFFERS_ALL \
        --primary-buffer "$buffer" \
        --threshold-buffer 20 \
        --metric f1 \
        --fdr-q "$fdr_q" \
        --workers $WORKERS \
        --bootstrap $BOOTSTRAP \
        --n-permutations $N_PERM \
        --seed $SEED \
        --top-n 0 \
        --skip-evaluation \
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
    for buffer in "${NON_PRIMARY_BUFFERS[@]}"; do
        # Pass 1 (q=0.05): computes pairwise at this buffer (cache
        # populated under .cache/pairwise_f1_${buffer}m/).
        run_buffer_pass "$era" "$arch" "$bounds" "$status_args" \
            "$buffer" "0.05" ""
        # Pass 2 (q=0.01): sensitivity rerun, reuses the pairwise
        # cache just written.
        run_buffer_pass "$era" "$arch" "$bounds" "$status_args" \
            "$buffer" "0.01" "--skip-pairwise"
    done
done

echo
echo "=== Stage 1 (per-buffer F1 re-tiering) complete ==="
date
