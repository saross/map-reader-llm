#!/usr/bin/env bash
# W2-4 replay, the long steps: the r2 board's tile-MCC re-sweeps.
#   a1c4bf2c3  at 835c2f3a0 (sapphire HEAD at launch, 2026-09-20T00:18:47Z):
#     final_board_sweeps.py --reference r2 --workers 20 --families ARM1-N1 ARM1-N3
#       ARM1-N5 ARM2-N1 ARM2-N3 ARM2-N5 FOURTH-N1 FOURTH-N3 FOURTH-N5 FOURTH-N10
#   03b8496ed  at c9131e757 (HEAD at launch, 02:31:18Z; committed on sapphire as
#     a9e4279cc and rebased onto f1b9b48ff before the push):
#     final_board_sweeps.py --reference r2 --workers 20 --families TH7 T03 TM IM UPL
#       A-N10 A-N1 A-N3 A-N5 B-N10 B-N1 B-N3 B-N5
# Commands from the session archive 2026-09-19T07-27 (sub-agent
# a5d57a31f77266025). Worker count cannot change the output: Pool.map with a
# fixed chunksize returns rows in task order and rows are sorted before
# writing. The board home's sweep CSVs and sweeps.json are copied to
# <out>/<generating commit>/ and the tree is removed.
# Usage: replay_sweep.sh <out dir> <run: 1|2> <workers>
set -u
O=$1; RUN=$2; W=$3
S=$HOME/scratch/s164-fw-recheck2-2026-10-15
H=results/55map-final-board-r2-2026-09-06
source "$S/env.sh"
canary() { git -C "$HOME/Code/map-reader-llm" status --porcelain=v1 | sha256sum | cut -c1-16; }
case $RUN in
  1) gen=a1c4bf2c3; head=835c2f3a0
     fams=(ARM1-N1 ARM1-N3 ARM1-N5 ARM2-N1 ARM2-N3 ARM2-N5 FOURTH-N1 FOURTH-N3 FOURTH-N5
           FOURTH-N10) ;;
  2) gen=03b8496ed; head=c9131e757
     fams=(TH7 T03 TM IM UPL A-N10 A-N1 A-N3 A-N5 B-N10 B-N1 B-N3 B-N5) ;;
  *) echo "run must be 1 or 2"; exit 2 ;;
esac
T=$S/w2-4-sweep-$head
echo "=== $(date -u +%FT%TZ) run $RUN: $gen at $head, $W workers; canary $(canary)"
git -C "$HOME/Code/map-reader-llm" worktree add --detach "$T" "$head" > /dev/null 2>&1 \
  || { echo "worktree add failed"; exit 1; }
(cd "$T" && "$PY" scripts/final_board_sweeps.py --reference r2 --workers "$W" \
   --families "${fams[@]}") > "$O/sweep-run$RUN.log" 2>&1
echo "rc=$?"
rm -rf "${O:?}/$gen"; mkdir -p "$O/$gen/$H"
(cd "$T" && git status --porcelain=v1 --untracked-files=all) > "$O/$gen.status.txt"
cp "$T/$H"/sweep_*.csv "$T/$H/sweeps.json" "$O/$gen/$H/"
git -C "$HOME/Code/map-reader-llm" worktree remove --force "$T"
echo "=== $(date -u +%FT%TZ) DONE; canary $(canary)"
