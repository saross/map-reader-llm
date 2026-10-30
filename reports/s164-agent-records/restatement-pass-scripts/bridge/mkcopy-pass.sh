#!/usr/bin/env bash
# =============================================================================
# mkcopy-pass.sh — disposable copy for the bridge lane's patched runs
# =============================================================================
# Code (scripts, config) from CODE_REF and data from DATA_REF of the pass
# worktree's repository (git archive, read only); the gitignored prepared
# passes copied read only from the shared checkout and SHA-checked against the
# committed floors' record; the candidate patch applied to the code with
# `git apply` (checked first). `.venv` is a symlink to the shared virtual
# environment directory, so `.venv/bin/python` finds its packages.
#
# Usage: mkcopy-pass.sh <code_ref> <data_ref> <patch> <dest>
# =============================================================================
set -euo pipefail
CODE_REF=$1; DATA_REF=$2; PATCH=$3; DEST=$4
WT=$HOME/scratch/s164-restate-2026-10-15/wt
SHARED=$HOME/Code/map-reader-llm
mkdir -p "$DEST"
git -C "$WT" archive "$CODE_REF" -- scripts tests config.py pyproject.toml pytest.ini ruff.toml \
  | tar -x -C "$DEST"
DATA_PATHS=()
for p in inputs/vectors inputs/grid-2026-08-18 inputs/stride-phaseb-2026-08-25 \
         inputs/image-b-gs-2026-08-28 outputs/grid-2026-08-18 outputs/image-b-gs-2026-08-28 \
         outputs/gemini37-screen-2026-08-28 outputs/gemini37-image-gs-2026-09-01 \
         outputs/modality-bridge-2026-10-07 outputs/wrong-sheet-reverify-2026-10-13 \
         results/grid-2026-08-18 results/modality-bridge-2026-10-07 \
         reports/w27-replicate-floors-2026-10-06-scripts/gs_consensus_pairs.csv; do
  # A path absent at DATA_REF (e.g. the 2026-10-13 re-verification run before
  # PR #43) is left out rather than failing the archive.
  if git -C "$WT" cat-file -e "$DATA_REF:$p" 2>/dev/null; then DATA_PATHS+=("$p");
  else echo "absent at $DATA_REF: $p"; fi
done
git -C "$WT" archive "$DATA_REF" -- "${DATA_PATHS[@]}" | tar -x -C "$DEST"
test -d "$DEST/outputs/modality-bridge-2026-10-07" || { echo "DATA ARCHIVE FAILED"; exit 3; }
for a in g3-text g3-image g37-text g37-image g37-image-cache g3-text-temp1 g3-image-temp1; do
  d=outputs/modality-bridge-2026-10-07/$a/scoring
  mkdir -p "$DEST/$d"; cp -a "$SHARED/$d/." "$DEST/$d/"
done
d=outputs/gemini37-image-gs-2026-09-01/scoring
mkdir -p "$DEST/$d"; cp -a "$SHARED/$d/." "$DEST/$d/"
# The prepared passes must be the ones the committed floors recorded.
"$SHARED/.venv/bin/python" - "$DEST" <<'PY'
import hashlib, json, sys
from pathlib import Path
dest = Path(sys.argv[1])
g = json.loads((Path.home() / "scratch/s164-restate-2026-10-15/wt/results/"
                "modality-bridge-2026-10-07/floors/gates.json").read_text())
bad = 0; n = 0
for arm, runs in g["scoring_passes_sha256"].items():
    cell = next((dest / "outputs/modality-bridge-2026-10-07" / arm / "scoring/common").iterdir())
    for run, sha in runs.items():
        n += 1
        bad += hashlib.sha256((cell / run / "detections_dedup.geojson").read_bytes()).hexdigest() != sha
print(f"pass SHA-256 against the committed floors record: {n - bad} of {n} equal")
sys.exit(1 if bad else 0)
PY
( cd "$DEST" && git apply --check "$PATCH" && git apply "$PATCH" )
ln -sfn "$SHARED/.venv" "$DEST/.venv"
printf 'code %s\ndata %s\npatch %s %s\n' "$(git -C "$WT" rev-parse "$CODE_REF")" \
  "$(git -C "$WT" rev-parse "$DATA_REF")" "$PATCH" "$(sha256sum "$PATCH" | cut -d' ' -f1)" \
  > "$DEST/.source-commits"
echo COPY-DONE
