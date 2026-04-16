#!/bin/bash
# Phase 3a: Post-analysis sync, commit, and push
# ================================================
# Run after run_phase3a_image_analysis.sh completes.
#
# Usage:
#   bash scripts/run_phase3a_overnight_sync.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "Phase 3a: Post-analysis sync, commit, and push"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# ===================================================================
# STEP 1: Rsync detection data from sapphire
# ===================================================================
echo "=== Step 1: Rsync detection data ==="

# HIGH thinking conditions
for temp in t0.0 t0.3 t1.0; do
    echo "  Syncing HIGH image-${temp}..."
    rsync -a --include='*/' --include='*.geojson' --include='*.meta.json' \
        --include='*.tiles.json' --include='voting_summary.json' --exclude='*' \
        sapphire:Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-${temp}/ \
        outputs/h11/pv-diag-384/flash-high-image-n5/image-${temp}/
done

# MINIMAL thinking conditions
for temp in t0.3 t1.0; do
    echo "  Syncing MINIMAL image-${temp}..."
    rsync -a --include='*/' --include='*.geojson' --include='*.meta.json' \
        --include='*.tiles.json' --include='voting_summary.json' --exclude='*' \
        sapphire:Code/map-reader-llm/outputs/h11/pv-diag-384/image-n5/image-${temp}/ \
        outputs/h11/pv-diag-384/image-n5/image-${temp}/
done

# Also sync existing T=0.7 consensus (may have been rebuilt)
echo "  Syncing HIGH T=0.7 consensus..."
rsync -a sapphire:Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/consensus/ \
    outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/consensus/ 2>/dev/null || true
rsync -a sapphire:Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/consensus-n5/ \
    outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/consensus-n5/ 2>/dev/null || true

echo "  Syncing MINIMAL T=0.7 consensus..."
rsync -a sapphire:Code/map-reader-llm/outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus/ \
    outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus/ 2>/dev/null || true
rsync -a sapphire:Code/map-reader-llm/outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus-n5/ \
    outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus-n5/ 2>/dev/null || true

echo ""

# ===================================================================
# STEP 2: Rsync analysis results from sapphire
# ===================================================================
echo "=== Step 2: Rsync analysis results ==="
rsync -av sapphire:Code/map-reader-llm/results/phase3a-image-matrix/ \
    results/phase3a-image-matrix/

echo ""

# ===================================================================
# STEP 3: Commit detection data
# ===================================================================
echo "=== Step 3: Commit detection data ==="

git add \
    outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/ \
    outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/ \
    outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/ \
    outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/consensus/ \
    outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/consensus-n5/ \
    outputs/h11/pv-diag-384/image-n5/image-t0.3/ \
    outputs/h11/pv-diag-384/image-n5/image-t1.0/ \
    outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus/ \
    outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus-n5/ \
    2>/dev/null || true

git commit -m "$(cat <<'EOF'
data(phase3a): image track 2×4 thinking × temperature matrix (384 px)

43 new detection runs completing the Flash × {HIGH, MINIMAL} ×
{T=0.0, T=0.3, T=0.7, T=1.0} matrix at 384 px (487 tiles).
T=0.7 data already existed; T=0.0 is K=3 baseline, others K=10.

Consensus GeoJSONs built for all conditions at N=10 (full sweep)
and N=5 (runs 1-5) using merge_passes.py --sweep.

Total API cost: ~$84 (Flex tier). Per erratum E53.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)" || echo "Nothing to commit (detection data)"

# ===================================================================
# STEP 4: Commit analysis results
# ===================================================================
echo "=== Step 4: Commit analysis results ==="

git add results/phase3a-image-matrix/ 2>/dev/null || true

git commit -m "$(cat <<'EOF'
data(analysis): Phase 3a image track consensus sweep evaluation

Comprehensive F1/P/R + bootstrap CI evaluation of the 2×4 thinking ×
temperature matrix at N=5 and N=10 consensus pool sizes, across 20/30/
40/50m spatial buffers. Summary tables in
results/phase3a-image-matrix/consensus-analysis-summary.md.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)" || echo "Nothing to commit (analysis)"

# ===================================================================
# STEP 5: Commit scripts
# ===================================================================
echo "=== Step 5: Commit scripts ==="

git add \
    scripts/build_tiered_leaderboard.py \
    scripts/run_phase3a_image_analysis.sh \
    scripts/run_phase3a_overnight_sync.sh \
    scripts/build_all_consensus.py \
    2>/dev/null || true

git commit -m "$(cat <<'EOF'
feat(analysis): leaderboard tiering script + Phase 3a analysis pipeline

- build_tiered_leaderboard.py: general-purpose orchestrator for
  statistically tiered leaderboards (evaluate → pairwise permutation →
  BH-FDR → tier grouping). FAIR4RS compliant, audited.
- run_phase3a_image_analysis.sh: overnight consensus sweep analysis
- run_phase3a_overnight_sync.sh: post-analysis sync/commit/push
- build_all_consensus.py: handler stacking fix (audit item)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)" || echo "Nothing to commit (scripts)"

# ===================================================================
# STEP 6: Push
# ===================================================================
echo "=== Step 6: Push ==="
git push

echo ""
echo "================================================================"
echo "  ALL DONE"
echo "  Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"
