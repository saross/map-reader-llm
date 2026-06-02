#!/usr/bin/env bash
#
# sync-crops.sh — replicate git-untracked crop binaries to another machine
# ========================================================================
# Crop PNGs were un-tracked from git (Session 95, item #6) because they are
# large reproducible binaries (regenerable from rasters by extract_candidates.py).
# git no longer carries them, so a `git pull` on another clone deletes them from
# that clone's working tree. Until durable object storage (Cloudflare R2) is set
# up, this keeps working copies on zbook / sapphire for the paper write-up by
# rsyncing the crop PNGs from THIS machine (which holds the canonical copy).
#
# Tiles (inputs/tiles_384/**) are still git-tracked and sync via push/pull — they
# are intentionally NOT handled here.
#
# Usage:
#     scripts/sync-crops.sh <ssh-host>        # e.g. zbook, sapphire
#
# Purely additive: no --delete, so it never removes files on the target.
#
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0

set -euo pipefail

TARGET="${1:?usage: scripts/sync-crops.sh <ssh-host>  (e.g. zbook)}"
REPO="${MAP_READER_REPO:-$HOME/Code/map-reader-llm}"

if [[ ! -d "$REPO" ]]; then
    echo "Repo not found: $REPO (set MAP_READER_REPO to override)" >&2
    exit 1
fi

# Sync only PNGs (+ the directory scaffolding to reach them) under the trees that
# hold crops. -m prunes empty directories on the receiver. No --delete.
for tree in archive outputs; do
    [[ -d "$REPO/$tree" ]] || continue
    echo "── syncing $tree/ crop PNGs → $TARGET ──"
    rsync -a -m --info=stats1 \
        --include='*/' --include='*.png' --exclude='*' \
        "$REPO/$tree/" "$TARGET:$REPO/$tree/"
done

echo "crop PNGs synced: $REPO → $TARGET"
