#!/usr/bin/env bash
# =============================================================================
# mkclone_patterns.sh -- a disposable sparse clone from a list of paths
# =============================================================================
# As mkclone.sh, but the sparse checkout takes exact paths and directories
# from a file (non-cone patterns: "/<path>" for a file, "/<dir>/" for a tree),
# so single files deep in large trees can be checked out alone.
# Usage: mkclone_patterns.sh <ref> <dest> <paths-file>
# =============================================================================
set -euo pipefail
REF=$1; DEST=$2; LIST=$3
SRC=$(git -C "$HOME/scratch/s164-restate-2026-10-15/wt" rev-parse --git-common-dir)
[ -e "$DEST" ] && { echo "refusing: $DEST exists" >&2; exit 2; }
git clone --quiet --shared --no-checkout "$SRC" "$DEST"
sed -e 's#^#/#' "$LIST" | git -C "$DEST" sparse-checkout set --no-cone --stdin
git -C "$DEST" -c advice.detachedHead=false checkout --quiet "$REF"
printf 'ref %s\n' "$(git -C "$DEST" rev-parse HEAD)" > "$DEST/../$(basename "$DEST").source-commit"
