#!/usr/bin/env bash
# W2-1 inheritance replays: move the inheritance replay tree to COMMIT,
# re-apply the ONE-line root patch to that commit's own
# inheritance_ladder.py (hard-coded "/home/shawn/Code/map-reader-llm" ->
# Path(__file__).resolve().parents[3], exactly 55ff8a02e's later fix, so
# the replay reads and writes only its own tree), then run the listed
# stages in order, each as "stage[:campaign]". Workers fixed at 2.
# Usage: run-inherit.sh <commit> <tag> ladder separation ladder:g3 ...
# Zero API (the ladder, separation and tests stages read local JSON and
# GeoJSON only; the score stage is never invoked here).
set -euo pipefail
COMMIT=$1; TAG=$2; shift 2
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-inherit
OUT=~/scratch/s164-fw-recheck-2026-10-14/w2-1-out
REC=~/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w2-1
PY=~/Code/map-reader-llm/.venv/bin/python
S=results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/inheritance_ladder.py
cd "$TREE"
git checkout -- results/
git checkout --detach "$COMMIT"
sed -i "s#^PROJECT_ROOT = Path(\"/home/shawn/Code/map-reader-llm\")\$#PROJECT_ROOT = Path(__file__).resolve().parents[3]#" "$S"
git diff -- "$S" > "$REC/patch-inheritance_ladder-root-$TAG.diff"
echo "start $(date -u +%FT%TZ) HEAD $(git rev-parse HEAD) patch lines $(grep -c "^[-+]PROJECT_ROOT" "$REC/patch-inheritance_ladder-root-$TAG.diff")"
for spec in "$@"; do
  stage=${spec%%:*}; camp=""
  [[ "$spec" == *:* ]] && camp="--campaign ${spec#*:}"
  echo "== stage $stage $camp $(date -u +%FT%TZ)"
  if [[ "$stage" == ladder ]]; then
    "$PY" "$S" --stage ladder --workers 2 $camp
  else
    "$PY" "$S" --stage "$stage" $camp
  fi
done
echo "== git status (only the patched driver should be listed if all outputs reproduce)"
git status --porcelain
echo "end $(date -u +%FT%TZ)"
