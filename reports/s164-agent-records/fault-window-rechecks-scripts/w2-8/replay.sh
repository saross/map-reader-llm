#!/usr/bin/env bash
# W2-8 replay: the E70 bootstrap-interval re-run of 8c89ccebb, at its
# parent c50bd5f19 (sapphire HEAD when the original ran, reflog
# 2026-09-12T05:15:40Z). Original command (session archive
# 2026-09-11T04-35, sub-agent a40f2383672669053, 2026-09-12T05:16:03Z):
#   scripts/repair_bootstrap_cis.py rerun --workers 16 \
#     results/all-bootstrap-cis.json results/pv/all-bootstrap-cis.json
# Worker count cannot change the output: ProcessPoolExecutor.map keeps
# job order and every entry is seeded (42) independently.
# Usage: replay.sh <replay tree> <out dir> <workers>
set -u
T=$1; O=$2; W=$3
source "$HOME/scratch/s164-fw-recheck2-2026-10-15/env.sh"
cd "$T" || exit 9
echo "=== $(date -u +%FT%TZ) HEAD $(git rev-parse --short HEAD) workers $W"
"$PY" scripts/repair_bootstrap_cis.py gate --n 5 --workers "$W" results/all-bootstrap-cis.json
echo "gate rc=$?"
"$PY" scripts/repair_bootstrap_cis.py rerun --workers "$W" results/all-bootstrap-cis.json results/pv/all-bootstrap-cis.json
echo "rerun rc=$?"
"$PY" scripts/check_bootstrap_cis.py --help > /dev/null 2>&1 && "$PY" scripts/check_bootstrap_cis.py --check results/all-bootstrap-cis.json
echo "check rc=$?"
cp results/all-bootstrap-cis.json "$O/all-bootstrap-cis.json"
cp results/pv/all-bootstrap-cis.json "$O/pv-all-bootstrap-cis.json"
echo "=== $(date -u +%FT%TZ) DONE"
