#!/usr/bin/env bash
# Run extref_run.sh for A, then B (sequential: each run is already two
# processes with --workers 1). Lane-uplift, S164 restatement pass.
LANE=$HOME/scratch/s164-restate-2026-10-15/lane-uplift
"$LANE/bin/extref_run.sh" A "$1"; echo "A rc $?"
"$LANE/bin/extref_run.sh" B "$1"; echo "B rc $?"
echo BOTH_DONE
