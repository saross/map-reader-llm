#!/usr/bin/env bash
# Run Stages 3, 4, 5 after Stage 2 (per-arch leaderboards) completes.
# Idempotent: re-run safely if interrupted.

set -e
cd /home/shawn/Code/map-reader-llm

LOG_DIR=logs/per-arch-leaderboards-rebuild-2026-04-25
mkdir -p "$LOG_DIR"

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
echo "=== Post-build pipeline complete ==="
date
