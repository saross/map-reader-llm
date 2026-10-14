#!/usr/bin/env bash
# Fault-window re-check W2-11, S164 (2026-10-14), parent agent: complete the
# e7ebc1695 WBF check. The sub-agent's replay regenerated wbf_candidates.geojson
# byte for byte but not wbf_vote4.geojson, which e7ebc1695 made by filtering the
# candidates at vote_count >= 4 (commit body). This runs that commit's copy of
# scripts/filter_detections_by_vote.py (unchanged since 25feba238, 2026-07-28)
# on the regenerated candidates and compares the result with the committed file.
set -u
W=~/scratch/s164-fw-recheck-2026-10-14/wt
O=~/scratch/s164-fw-recheck-2026-10-14/w2-11-vote4-out
PY=~/Code/map-reader-llm/.venv/bin/python
REGEN=~/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-out/w2-11/e7ebc1695/wbf/wbf_candidates.geojson
P=outputs/h12-v2/wbf/r3-hp-heavy
mkdir -p "$O"
git -C "$W" show e7ebc1695:scripts/filter_detections_by_vote.py > "$O/filter_detections_by_vote.py"
git -C "$W" show "e7ebc1695:$P/wbf_vote4.geojson" > "$O/committed_wbf_vote4.geojson"
git -C "$W" show "e7ebc1695:$P/wbf_candidates.geojson" > "$O/committed_wbf_candidates.geojson"
echo "candidates regenerated vs committed: $(cmp -s "$REGEN" "$O/committed_wbf_candidates.geojson" && echo IDENTICAL || echo DIFFER)"
$PY "$O/filter_detections_by_vote.py" --input "$REGEN" --output "$O/wbf_vote4.geojson" --min-votes 4
echo "filter rc=$?"
echo "sha256 regenerated: $(sha256sum < "$O/wbf_vote4.geojson" | cut -d' ' -f1)"
echo "sha256 committed:   $(sha256sum < "$O/committed_wbf_vote4.geojson" | cut -d' ' -f1)"
echo "sha256 at 90294a283: $(git -C "$W" show "90294a283:$P/wbf_vote4.geojson" | sha256sum | cut -d' ' -f1)"
cmp -s "$O/wbf_vote4.geojson" "$O/committed_wbf_vote4.geojson" && echo "wbf_vote4.geojson: BYTE-IDENTICAL" || {
  echo "wbf_vote4.geojson: bytes differ; field comparison:"
  $PY - "$O/wbf_vote4.geojson" "$O/committed_wbf_vote4.geojson" <<'PYEOF'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
print("features regen/committed:", len(a["features"]), len(b["features"]))
print("equal as JSON:", a == b)
PYEOF
}
