#!/usr/bin/env bash
# W2-4 replay, the short steps: the r2 board post-hoc cells, the carried-k
# sweep record, and the relabel. Each step runs at sapphire's HEAD when the
# original ran (reflog of ~/Code/map-reader-llm, 2026-09-19/20), with the
# command recorded in the session archive 2026-09-19T07-27 (sub-agents
# a5d57a31f77266025 and a14cc0805c9dd5092):
#   cca6ccda5  at 3ced9749c  final_board_posthoc_cells.py --set carried-analogue      (09-19T23:51:19Z)
#   1ed3e54cb  at a1c4bf2c3  final_board_posthoc_cells.py --set mcc-oracle            (09-20T01:10:43Z)
#   539372938  at d7e0c741d  final_board_sweeps.py --reference r2 --record-carried-k  (07:17:46Z)
#   681b4e246  at 4a8d157cb  final_board_posthoc_cells.py --set mcc-oracle-at-carried-k
#                            --reference r2                                          (07:40:16Z)
#   1bbba2e21  at 182a414f2  build_tile_presence_board.py --stage relabel              (22:57:13Z)
# Each step gets a fresh detached worktree; every file it writes or changes
# is copied to <out>/<generating commit>/ and the tree is removed.
# Usage: replay_cells.sh <out dir> [step ...]
set -u
O=$1; shift
S=$HOME/scratch/s164-fw-recheck2-2026-10-15
source "$S/env.sh"
canary() { git -C "$HOME/Code/map-reader-llm" status --porcelain=v1 | sha256sum | cut -c1-16; }
run_step() {
  local gen=$1 head=$2; shift 2
  local T=$S/w2-4-$head
  echo "=== $(date -u +%FT%TZ) $gen at $head: $*"
  git -C "$HOME/Code/map-reader-llm" worktree add --detach "$T" "$head" > /dev/null 2>&1 \
    || { echo "worktree add failed"; return 1; }
  (cd "$T" && "$PY" "$@") > "$O/$gen.log" 2>&1
  echo "rc=$?"
  rm -rf "${O:?}/$gen"; mkdir -p "$O/$gen"
  (cd "$T" && git status --porcelain=v1 --untracked-files=all) > "$O/$gen.status.txt"
  # Copy every file the step wrote or changed (tracked changes and new files).
  cut -c4- "$O/$gen.status.txt" | while read -r p; do
    mkdir -p "$O/$gen/$(dirname "$p")"; cp -r "$T/$p" "$O/$gen/$p"
  done
  git -C "$HOME/Code/map-reader-llm" worktree remove --force "$T"
}
echo "=== start; live-checkout canary $(canary)"
steps=("$@")
[ ${#steps[@]} -eq 0 ] && steps=(cca6ccda5 1ed3e54cb 539372938 681b4e246 1bbba2e21)
for s in "${steps[@]}"; do
  case $s in
    cca6ccda5) run_step cca6ccda5 3ced9749c scripts/final_board_posthoc_cells.py \
                 --set carried-analogue ;;
    1ed3e54cb) run_step 1ed3e54cb a1c4bf2c3 scripts/final_board_posthoc_cells.py \
                 --set mcc-oracle ;;
    539372938) run_step 539372938 d7e0c741d scripts/final_board_sweeps.py --reference r2 \
                 --record-carried-k ;;
    681b4e246) run_step 681b4e246 4a8d157cb scripts/final_board_posthoc_cells.py \
                 --set mcc-oracle-at-carried-k --reference r2 ;;
    1bbba2e21) run_step 1bbba2e21 182a414f2 scripts/build_tile_presence_board.py \
                 --stage relabel ;;
  esac
done
echo "=== $(date -u +%FT%TZ) DONE; live-checkout canary $(canary)"
