#!/usr/bin/env bash
# ============================================================================
# run-p12.sh <name> <hash-seed>
# ----------------------------------------------------------------------------
# One independent run for plan P12's integrity check (record § Integrity):
# a fresh process chain with its own output directory and PYTHONHASHSEED.
#   1. d64_a06_replication.py (extended 2026-10-15) into <name>/a06; on the
#      merged tree it must reproduce the 2026-10-14 outputs in out/.
#   2. posthoc_interaction.py on <name>/a06 (likewise).
#   3. d64_p12_replication.py into <name>/p12 (the P12 analysis).
# Writes its own pid file and, on exit, 0 if all three exited 0, else 1;
# nothing is written inside the repository.
#
# Usage (from anywhere on sapphire; launch detached, nothing after the &):
#   nohup bash run-p12.sh r3 0 > /dev/null 2>&1 < /dev/null &
#
# Author: Shawn Ross & Claude (Anthropic), Session 164, 2026-10-15
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/../../.."  # worktree root
BASE=${D64_SCRATCH:-$HOME/scratch/s164-d64-2026-10-14}
NAME=${1:?usage: run-p12.sh <name> <hash-seed>}
HASHSEED=${2:?usage: run-p12.sh <name> <hash-seed>}
PY=${D64_PYTHON:-$HOME/Code/map-reader-llm/.venv/bin/python}
D=reports/s164-agent-records/d64-a06-replication-scripts
mkdir -p "$BASE/$NAME/a06" "$BASE/$NAME/p12" "$BASE/logs" "$BASE/pids"
echo $$ > "$BASE/pids/$NAME.pid"
rc=0
PYTHONHASHSEED=$HASHSEED "$PY" "$D/d64_a06_replication.py" --out "$BASE/$NAME/a06" \
  > "$BASE/logs/$NAME-a06.log" 2>&1 < /dev/null || rc=1
PYTHONHASHSEED=$HASHSEED "$PY" "$D/posthoc_interaction.py" "$BASE/$NAME/a06" \
  > "$BASE/logs/$NAME-posthoc.log" 2>&1 < /dev/null || rc=1
PYTHONHASHSEED=$HASHSEED "$PY" "$D/d64_p12_replication.py" --out "$BASE/$NAME/p12" \
  > "$BASE/logs/$NAME-p12.log" 2>&1 < /dev/null || rc=1
echo $rc > "$BASE/pids/$NAME.exit"
rm -f "$BASE/pids/$NAME.pid"
