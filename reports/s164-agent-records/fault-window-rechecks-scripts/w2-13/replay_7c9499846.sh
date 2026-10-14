#!/usr/bin/env bash
# replay_7c9499846.sh -- W2-13 fault-window re-check (Session 164, 2026-10-14).
# Replays the register regeneration committed in 7c9499846 (rulings D19-D23)
# at that commit, in a detached replay worktree, single process.  Zero API.
#   1. C3 re-derivation: rederive_manifest_fields.py --out <out> (pristine tree)
#   2. register .md views: generate_post_run_report.py --check-renderings
#   3. post-run reports:   generate_run_reports.py --all --check
#   4. generated-file registry: build_generated_file_registry.py --check
#   5. the manifests themselves: generate_post_run_report.py --all --write,
#      which keeps generated_at / last_extracted_at stable when no row's
#      content changed, so an exact rebuild leaves the JSONs byte-identical.
# Usage: replay_7c9499846.sh <replay-tree> <out-dir>
set -uo pipefail
TREE="$1"; OUT="$2"
PY=~/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$TREE"
git checkout -q --force --detach 7c9499846
echo "HEAD $(git rev-parse --short HEAD)"
mkdir -p "$OUT"
echo "== 1 rederive_manifest_fields $(date -u +%FT%TZ)"
$PY scripts/rederive_manifest_fields.py --out "$OUT/rederivation-report.json"
echo "exit=$?"
echo "== 2 --check-renderings $(date -u +%FT%TZ)"
$PY scripts/generate_post_run_report.py --check-renderings
echo "exit=$?"
echo "== 3 generate_run_reports --all --check $(date -u +%FT%TZ)"
$PY scripts/generate_run_reports.py --all --check
echo "exit=$?"
echo "== 4 build_generated_file_registry --check $(date -u +%FT%TZ)"
$PY scripts/build_generated_file_registry.py --check
echo "exit=$?"
echo "== 5 generate_post_run_report --all --write $(date -u +%FT%TZ)"
$PY scripts/generate_post_run_report.py --all --write
echo "exit=$?"
echo "== done $(date -u +%FT%TZ)"
for f in results/passes-manifest.json results/runs-manifest.json results/conditions-manifest.json \
         results/analyses-manifest.json; do
  cp "$f" "$OUT/$(basename "$f")"
done
echo "== git status after --write"
git status --short | head -40
