#!/usr/bin/env bash
# =============================================================================
# W2-11 fault-window re-check (2026-10-14): e7ebc1695's WBF fusion, rerun.
#
# fuse_detections_wbf.py imports ``scripts.*`` without adding the repository
# root to sys.path, so it must run with the root on PYTHONPATH (as
# ``python -m`` from the root would). Parameters are those
# outputs/h12-v2/wbf/r3-hp-heavy/wbf_diagnostics.json records at e7ebc1695.
# Zero API.
# =============================================================================
set -uo pipefail
T=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-92b151058
O2=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-out/w2-11
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export GEMINI_API_KEY= GOOGLE_API_KEY= GOOGLE_GENAI_API_KEY=
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9
export https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 NO_PROXY= no_proxy=
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
[ -z "$(git -C "$T" status --porcelain --untracked-files=no)" ] || { echo "REFUSED: dirty"; exit 1; }
git -C "$T" checkout -q --detach e7ebc1695 && echo "HEAD $(git -C "$T" rev-parse --short=9 HEAD)"
rm -rf "$O2/e7ebc1695/wbf"
(cd "$T" && PYTHONPATH="$T" $PY scripts/fuse_detections_wbf.py --config h12v2-r3-hp-heavy \
  --output-dir "$O2/e7ebc1695/wbf" --iou-threshold 0.25 --min-separation-m 60 \
  --min-dim 20 --max-dim 200 --min-area 400 --max-area 40000) > "$O2/e7ebc1695/wbf.log" 2>&1
echo "wbf rc=$?"
git -C "$T" checkout -q --detach 69eb32132
