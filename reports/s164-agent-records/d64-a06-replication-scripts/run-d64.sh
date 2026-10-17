#!/usr/bin/env bash
# ============================================================================
# run-d64.sh <name> <hash-seed>
# ----------------------------------------------------------------------------
# One independent run of d64_a06_replication.py (plan P10): a fresh process
# with its own output directory and PYTHONHASHSEED, so two runs under
# different hash seeds can be compared byte for byte. Writes its own pid
# file and, on exit, the driver's exit code; nothing is written inside the
# repository.
#
# Usage (from anywhere on sapphire; launch detached, nothing after the &):
#   nohup bash run-d64.sh r1 0 > /dev/null 2>&1 < /dev/null &
#
# Author: Shawn Ross & Claude (Anthropic), Session 164, 2026-10-14
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/../../.."  # worktree root
BASE=${D64_SCRATCH:-$HOME/scratch/s164-d64-2026-10-14}
NAME=${1:?usage: run-d64.sh <name> <hash-seed>}
HASHSEED=${2:?usage: run-d64.sh <name> <hash-seed>}
PY=${D64_PYTHON:-$HOME/Code/map-reader-llm/.venv/bin/python}
mkdir -p "$BASE/$NAME" "$BASE/logs" "$BASE/pids"
echo $$ > "$BASE/pids/$NAME.pid"
PYTHONHASHSEED=$HASHSEED "$PY" \
  reports/s164-agent-records/d64-a06-replication-scripts/d64_a06_replication.py \
  --out "$BASE/$NAME" > "$BASE/logs/$NAME.log" 2>&1 < /dev/null
echo $? > "$BASE/pids/$NAME.exit"
rm -f "$BASE/pids/$NAME.pid"
