#!/usr/bin/env bash
# =============================================================================
# compare_gs.sh — the GS lane's integrity and prediction checks
# =============================================================================
# Part of the S164 restatement pass (reports/s164-agent-records/
# restatement-pass.md § 1.2). After gs_chain.sh has run in copyA and copyB:
#   1. run A against run B, every file under results/ (cmp_tree.py: timestamps,
#      run roots, and evaluation.md "Generated" lines normalised);
#   2. the files run A wrote, against the committed tree (tree_vs_commit.py);
#   3. run A against the 2026-10-13 re-score's REPAIRED copy (the prediction),
#      directory by directory.
# Writes everything to <out_dir>.
#
# Usage: compare_gs.sh <copyA> <copyB> <repaired_copy> <worktree> <out_dir>
# =============================================================================
set -uo pipefail
A=$1; B=$2; P=$3; WT=$4; OUT=$5
PY=$HOME/Code/map-reader-llm/.venv/bin/python
TOOLS=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
DIRS="grid-2026-08-18 stride-2026-08-25 image-b-gs-2026-08-28 gemini37-screen-2026-08-28
gemini37-image-gs-2026-09-01 gemini37-fourth-cell gemini38-screen-2026-09-04 selection-aware
sensitivity-mde-2026-08-28 verifier-robustness"
"$PY" "$TOOLS/cmp_tree.py" "$A/results" "$B/results" --roots "$A" "$B" > "$OUT/runA-vs-runB.txt" 2>&1
echo "A vs B exit $?" >> "$OUT/runA-vs-runB.txt"
args=(); for d in $DIRS; do args+=("results/$d"); done
"$PY" "$TOOLS/tree_vs_commit.py" "$A" "$WT" "${args[@]}" > "$OUT/runA-vs-commit.tsv" 2>&1
: > "$OUT/runA-vs-prediction.txt"
for d in $DIRS; do
  echo "### $d" >> "$OUT/runA-vs-prediction.txt"
  "$PY" "$TOOLS/cmp_tree.py" "$A/results/$d" "$P/results/$d" --roots "$A" "$P" \
    >> "$OUT/runA-vs-prediction.txt" 2>&1
done
echo done
