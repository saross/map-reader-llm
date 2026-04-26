#!/usr/bin/env bash
# Post-Stage-1 driver: refresh downstream artefacts after the
# per-buffer F1 re-tiering driver
# (scripts/rebuild_per_arch_f1_per_buffer.sh) completes.
#
# Sequence:
#   Stage 5 — F1 tier_stability refresh (real Spearman rho per
#             stratum + metric-aware methodology paragraph from the
#             generator updated 2026-04-26).
#   Stage 7 — MC-precision flags refresh (now walks F1 pairwise tier
#             JSONs at all 5 buffers per stratum).
#   Stage 6 — Per-arch top-level README + per-stratum READMEs +
#             headlines refresh (new per-buffer methodology paragraph
#             + headline F1 tier-stability summary injected).
#
# Idempotent: safe to re-run.

set -e

cd /home/shawn/Code/map-reader-llm

LOG_DIR=logs/per-arch-leaderboards-rebuild-2026-04-26-per-buffer-f1
mkdir -p "$LOG_DIR"

echo "=== Step 5: F1 tier_stability refresh ==="
.venv/bin/python scripts/build_tier_stability.py --metric f1 --all \
    > "$LOG_DIR/post-tier-stability-f1.log" 2>&1
echo "  OK (see $LOG_DIR/post-tier-stability-f1.log)"

echo
echo "=== Step 7: MC-precision flags refresh ==="
# Stage 4c only — re-run cross-architecture builder with --stage all
# is unnecessary (4a + 4b are buffer-20 only and unaffected); but the
# CLI does not expose 4c standalone. Run --stage all to be safe; the
# 4a + 4b regeneration is fast and idempotent.
.venv/bin/python scripts/build_cross_architecture_tables.py \
    --metric both --stage all \
    > "$LOG_DIR/post-cross-arch-tables.log" 2>&1
echo "  OK (see $LOG_DIR/post-cross-arch-tables.log)"

echo
echo "=== Step 6: Per-arch documentation refresh ==="
.venv/bin/python scripts/build_per_arch_documentation.py --what all \
    > "$LOG_DIR/post-docs.log" 2>&1
echo "  OK (see $LOG_DIR/post-docs.log)"

echo
echo "=== Post-Stage-1 refresh complete ==="
date
