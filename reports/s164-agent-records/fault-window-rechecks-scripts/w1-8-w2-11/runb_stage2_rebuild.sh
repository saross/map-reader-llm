#!/usr/bin/env bash
# =============================================================================
# W1-8 fault-window re-check (2026-10-14): Run B Stage 2 inputs, one arm.
#
# Replays, in the disposable replay worktree, the zero-API steps of
# scripts/modality-bridge-2026-10-07-stage2.sh for ONE arm, each at the commit
# that generated the committed file:
#   at UNION_COMMIT (the union's build.json git_head):
#     union       modality_bridge_union.py --layout batch --write
#     extract     run_pv.py extract   (crop manifest; PNG crops are gitignored)
#     provenance  check_union_provenance.py --manifest --json-out
#   at CHECK_COMMIT (the coverage record's git_head):
#     coverage    modality_bridge_union.py --layout batch --json-out (gates only)
#     metas       modality_bridge_stage2_checks.py metas
# Regenerated files are copied to $O/<arm>/ and the tree is left clean.
# No API: nothing here runs `verify` or builds a client; API-key variables
# are blanked (dotenv does not override a set variable) and HTTP(S) proxies
# point at a dead port, so any stray request would fail.
#
# Usage: runb_stage2_rebuild.sh ARM UNION_COMMIT CHECK_COMMIT
# =============================================================================
set -euo pipefail
ARM=$1; UC=$2; CC=$3
T=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-92b151058
O=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-out/runb/regen/$ARM
PY=$HOME/Code/map-reader-llm/.venv/bin/python
OUTD=outputs/modality-bridge-2026-10-07
MANIFEST=inputs/grid-2026-08-18/grid_384_ov192_manifest.json
case $ARM in g3-text|g3-image) K=10 ;; *) K=5 ;; esac
case $ARM in *image*) V=detect_brief-text-image ;; *) V=detect_brief-text ;; esac
VR=$OUTD/$ARM/verifier/$V
export GEMINI_API_KEY= GOOGLE_API_KEY= GOOGLE_GENAI_API_KEY=
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9
export https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 NO_PROXY= no_proxy=
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
rm -rf "$O"; mkdir -p "$O"
cd "$T"

clean_check() {
  # No tracked file may differ from the checked-out commit.
  if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "REFUSED: replay tree has tracked changes"; git status --short | head; exit 1
  fi
}

clean_check
git checkout -q --detach "$UC"
echo "HEAD $(git rev-parse HEAD) for union/extract/provenance" > "$O/replay.txt"
[ ! -e "$VR/union_k$K.geojson" ] || { echo "REFUSED: union already present at $UC"; exit 1; }
[ "$(git ls-files "$VR" "$OUTD/$ARM/scoring" | wc -l)" = 0 ] || { echo "REFUSED: tracked"; exit 1; }

echo "=== $(date -Is) UNION $ARM" >> "$O/union.log"
$PY scripts/modality_bridge_union.py --layout batch --cell-dir "$OUTD/$ARM/$V" --k "$K" \
  --out-root "$OUTD/$ARM" --manifest "$MANIFEST" --write >> "$O/union.log" 2>&1
echo "=== $(date -Is) EXTRACT $ARM" >> "$O/extract.log"
$PY scripts/run_pv.py extract --proposer "$VR/union_k$K.geojson" --output-dir "$VR/crops" \
  --tiles-dir inputs/tiles_384_ov192 --rasters-dir inputs/rasters >> "$O/extract.log" 2>&1
$PY scripts/check_union_provenance.py --manifest "$VR/crops/candidate_manifest.json" \
  --json-out "$O/provenance.json" > "$O/provenance.log" 2>&1 || echo "provenance rc=$?" >> "$O/provenance.log"
cp "$VR/union_k$K.geojson" "$VR/union_k$K.build.json" "$VR/crops/candidate_manifest.json" "$O/"
(cd "$VR/crops" && find . -name '*.png' | sort | xargs sha256sum) > "$O/crops.sha256"
mv "$OUTD/$ARM/scoring" "$O/scoring"
rm -rf "$VR"

clean_check
git checkout -q --detach "$CC"
echo "HEAD $(git rev-parse HEAD) for coverage/metas" >> "$O/replay.txt"
$PY scripts/modality_bridge_union.py --layout batch --cell-dir "$OUTD/$ARM/$V" --k "$K" \
  --out-root "$OUTD/$ARM" --manifest "$MANIFEST" --json-out "$O/coverage.json" > "$O/coverage.log" 2>&1
$PY scripts/modality_bridge_stage2_checks.py metas "$ARM" --out "$OUTD" \
  --json-out "$O/metas.json" > "$O/metas.log" 2>&1
clean_check
echo "DONE $ARM $(date -Is)" >> "$O/replay.txt"
