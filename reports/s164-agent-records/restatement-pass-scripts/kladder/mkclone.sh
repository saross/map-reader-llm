#!/usr/bin/env bash
# =============================================================================
# mkclone.sh -- a disposable, real-file, sparse git clone of the pass's branch
# =============================================================================
# K-ladder lane of the S164 restatement pass. `git clone --shared` reads the
# objects of the repository that owns the pass's worktree (no write to it);
# the sparse checkout holds only what the K-ladder cells read, so the scorer
# records a real script commit instead of "unknown". Nothing is linked.
#
# Usage: mkclone.sh <ref> <dest> <path> [<path> ...]
# =============================================================================
set -euo pipefail
REF=$1; DEST=$2; shift 2
SRC=$(git -C "$HOME/scratch/s164-restate-2026-10-15/wt" rev-parse --git-common-dir)
[ -e "$DEST" ] && { echo "refusing: $DEST exists" >&2; exit 2; }
git clone --quiet --shared --no-checkout "$SRC" "$DEST"
git -C "$DEST" sparse-checkout set "$@"
git -C "$DEST" -c advice.detachedHead=false checkout --quiet "$REF"
printf 'ref %s\n' "$(git -C "$DEST" rev-parse HEAD)" > "$DEST/../$(basename "$DEST").source-commit"
