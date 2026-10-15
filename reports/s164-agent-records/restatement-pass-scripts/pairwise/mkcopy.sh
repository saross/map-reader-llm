#!/bin/bash
# Make one disposable real-file copy of the pass worktree's commit for the
# pairwise lane's CANDIDATE runs. Reads the source repository only:
# `git clone --shared` writes nothing to the source (objects via alternates),
# and the checkout lands under the lane scratch. Stops if free space on the
# scratch filesystem is below 20 GB before or after.
# Usage: mkcopy.sh <A|B> <commit>
set -u
L=~/scratch/s164-restate-2026-10-15/lane-pairwise
WT=~/scratch/s164-restate-2026-10-15/wt
name=$1; commit=$2
echo $$ > "$L/pids/copy-$name.pid"
free_gb() { df --output=avail -BG "$L" | tail -1 | tr -dc 0-9; }
if [ "$(free_gb)" -lt 20 ]; then echo "STOP: free space $(free_gb) GB < 20" ; echo 9 > "$L/pids/copy-$name.rc"; exit 9; fi
mkdir -p "$L/runs/$name"
git clone --quiet --shared --no-checkout "$WT" "$L/runs/$name/repo"
rc=$?
if [ $rc -eq 0 ]; then
  git -C "$L/runs/$name/repo" -c advice.detachedHead=false checkout --quiet --detach "$commit"
  rc=$?
fi
echo "free after: $(free_gb) GB; HEAD $(git -C "$L/runs/$name/repo" rev-parse --short HEAD)"
echo $rc > "$L/pids/copy-$name.rc"
