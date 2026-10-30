#!/usr/bin/env bash
# ============================================================================
# reproduce-march.sh — the reproduce gate of the E72 regeneration
# ----------------------------------------------------------------------------
# Builds the inputs the committed E72 board was built from (commit bc45133b4:
# results/pairwise/ and the factor-analysis artefact), adds the CURRENT
# scripts/ as real-file copies, runs the adapted scripts/regen_e43_board.py
# with --revision 2026-08-02, and compares its outputs with the ones committed
# in 2f3ef020a, ignoring timestamps and commit hashes. $0; no API calls; a few
# seconds of CPU.
#
# Usage (from a checkout of the branch):
#   reports/s166-agent-records/e72-group7-scripts/reproduce-march.sh <scratch> <python>
# ============================================================================
set -euo pipefail
repo=$(git rev-parse --show-toplevel)
scratch=$1
python=${2:-python}
here=$(cd "$(dirname "$0")" && pwd)

rm -rf "$scratch/march" "$scratch/expected" "$scratch/out"
mkdir -p "$scratch/march" "$scratch/expected"
git -C "$repo" archive bc45133b4 results/pairwise \
    results/factor-analysis/factor_analysis_results.json | tar -x -C "$scratch/march"
git -C "$repo" archive 2f3ef020a results/e43-board-regen | tar -x -C "$scratch/expected"
cp -r "$repo/scripts" "$scratch/march/scripts"          # real copies, not links
test "$(find "$scratch/march" -type l | wc -l)" -eq 0

# The tree is not a git checkout, so git_commit() records "unknown"; the
# comparison ignores commit hashes. Its stderr "not a git repository" is noise.
(cd "$scratch/march" && "$python" scripts/regen_e43_board.py --execute \
    --revision 2026-08-02 --output-dir "$scratch/out" 2>/dev/null)
"$python" "$here/compare_board_outputs.py" "$scratch/expected/results/e43-board-regen" "$scratch/out"
