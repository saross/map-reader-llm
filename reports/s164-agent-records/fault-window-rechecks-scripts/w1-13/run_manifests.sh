#!/usr/bin/env bash
# Fault-window re-check W1-13 (S164, 2026-10-14): rebuild the register
# projections (runs/conditions/passes/analyses manifests and their five .md
# renderings) with scripts/generate_post_run_report.py --all --write in a
# disposable replay tree at origin/main 90294a283, then list what git sees as
# changed. The committed JSONs are compared field by field by
# compare_manifests.py (timestamps neutralised). Also runs the renderings drift
# guard and the manipulation gate. One process at a time.
set -u
TREE=~/scratch/s164-fw-recheck-2026-10-14/w1-13-90294a283
PY=~/Code/map-reader-llm/.venv/bin/python
cd "$TREE" || exit 2
echo "== check-renderings (before rebuild)"; $PY scripts/generate_post_run_report.py --check-renderings; echo "EXIT $?"
echo "== manipulation gate --all"; $PY scripts/check_manipulation.py --all > /dev/null 2>&1; echo "EXIT $?"
echo "== rebuild --all --write"; $PY scripts/generate_post_run_report.py --all --write; echo "EXIT $?"
echo "== git status after rebuild"; git status --porcelain
echo "== git diff --stat"; git diff --stat
