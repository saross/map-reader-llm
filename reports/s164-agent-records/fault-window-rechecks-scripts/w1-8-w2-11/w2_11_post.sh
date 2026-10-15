#!/usr/bin/env bash
# =============================================================================
# W2-11 fault-window re-check (2026-10-14): post-steps, run serially.
#   1. the e7ebc1695 WBF fusion rerun (w2_11_wbf.sh)
#   2. check_union_provenance.py --manifest on the three committed 3.7 image
#      crop manifests; the --manifest mode arrived in 9b1c6a760 (2026-09-20),
#      after these unions, so it runs at 69eb32132 (a check, not a rebuild)
#   3. the comparison and summaries (w2_11_summarise.sh)
# Zero API.
# =============================================================================
set -uo pipefail
D=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w1-8-w2-11
T=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-92b151058
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export GEMINI_API_KEY= GOOGLE_API_KEY= GOOGLE_GENAI_API_KEY=
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9
export https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 NO_PROXY= no_proxy=
bash "$D/w2_11_wbf.sh"
[ -z "$(git -C "$T" status --porcelain --untracked-files=no)" ] || { echo "REFUSED: dirty"; exit 1; }
git -C "$T" checkout -q --detach 69eb32132
V=outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img
for k in 1 3 5; do
  (cd "$T" && $PY scripts/check_union_provenance.py --manifest "$V/crops_k$k/candidate_manifest.json" \
    --json-out "$D/w2-11-image-manifest-provenance-k$k.json") > /dev/null 2>&1
  echo "manifest provenance k$k rc=$? $($PY -c 'import json,sys; r=json.load(open(sys.argv[1]))["manifest_results"][0]; print(r["classification"], r["detail"])' "$D/w2-11-image-manifest-provenance-k$k.json")"
done
bash "$D/w2_11_summarise.sh"
