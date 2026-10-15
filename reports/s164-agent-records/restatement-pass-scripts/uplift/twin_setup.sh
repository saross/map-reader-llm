#!/usr/bin/env bash
# =============================================================================
# twin_setup.sh — a disposable sparse clone for the twin origin-route driver
# =============================================================================
# `git clone --shared` of the repository (objects read through alternates;
# nothing written to the source), a no-cone sparse checkout of the paths the
# grid, stride, and image chains' union loaders and evaluate_detections.py
# read, detached at REF. The Gemini 3.7 image cell's prepared passes are not
# tracked; they are copied read only from sapphire's shared checkout (the
# origin route's row-for-row union gate checks them against the committed
# union). Lane-uplift, S164 restatement pass. Zero API.
#
# Usage: twin_setup.sh <ref> <dest>
# =============================================================================
set -euo pipefail
REF=$1; DEST=$(realpath -m "$2")
SRC=$HOME/Code/map-reader-llm
[ -e "$DEST" ] && { echo "refusing: $DEST exists" >&2; exit 2; }
git clone -q --shared --no-checkout "$SRC" "$DEST"
cd "$DEST"
git sparse-checkout init --no-cone
cat > .git/info/sparse-checkout <<'EOF'
/scripts/
/config.py
/pyproject.toml
/inputs/vectors/
/inputs/grid-2026-08-18/
/inputs/stride-phaseb-2026-08-25/
/inputs/image-b-gs-2026-08-28/
/outputs/grid-2026-08-18/
/outputs/stride-phaseb-2026-08-25/
/outputs/stride-phasec-2026-08-25/
/outputs/image-b-gs-2026-08-28/
/outputs/gemini37-screen-2026-08-28/
/outputs/gemini37-image-gs-2026-09-01/
/results/uplift-supplement/
/results/run-conditions.json
/results/grid-2026-08-18/
/results/stride-2026-08-25/
/results/image-b-gs-2026-08-28/
EOF
git checkout -q --detach "$REF"
d=outputs/gemini37-image-gs-2026-09-01/scoring
mkdir -p "$d"; cp -a "$SRC/$d/." "$d/"
META=$(dirname "$DEST")
( cd "$SRC/$d" && find . -type f -exec sha256sum {} + | sort -k2 ) > "$META/setup-untracked-inputs.sha256"
git rev-parse HEAD > "$META/setup-source-commit.txt"
git status --porcelain --untracked-files=all > "$META/setup-status-before.txt"
