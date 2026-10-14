#!/usr/bin/env bash
# =============================================================================
# W2-11 fault-window re-check (2026-10-14): compare and summarise.
#
# Reads the regenerations under $O2 (w2_11_sequence.sh, w2_11_wbf.sh) and
# writes compact results into this script's directory:
#   w2-11-compare.json       every regenerated file against its committed one
#   w2-11-carried-rows.json  f8e0eb600 K = 1 / K = 3 carried rows vs the harness
#   w2-11-archive-copies.json the "archive, never delete" copies of the
#                            2026-09-08 rebuilds, by blob equality with the
#                            source at the parent; and e7ebc1695's vote-4 claim
#   w2-11-cup.json           check_union_provenance classifications (e9d1db0d0)
#   w2-11-reparse.json, w2-11-remerge.json, w2-11-c053f5a41.json
# Reads only; runs no model and no API.
# =============================================================================
set -uo pipefail
D=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w1-8-w2-11
R=$HOME/scratch/s164-fw-recheck-2026-10-14/wt
O2=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-out/w2-11
PY=$HOME/Code/map-reader-llm/.venv/bin/python
$PY "$D/w2_11_spec.py" "$R" "$O2" "$O2/spec.json"
$PY "$D/compare_files.py" --repo "$R" --spec "$O2/spec.json" --out "$D/w2-11-compare.json" \
  --head 90294a283
V=outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37
$PY "$D/check_carried_rows.py" "$R" "$D/w2-11-carried-rows.json" \
  "k1=$O2/f8e0eb600/k1/carry/probabilities.json=$V/verify_k1_recovery-fixed/probabilities.json" \
  "k3=$O2/f8e0eb600/k3/carry/probabilities.json=$V/verify_k3_recovery-fixed/probabilities.json"
# Archive copies: blob equality with the source at the parent (a rename test
# limited to archive/ cannot see the pairs), plus e7ebc1695's vote-4 claim.
$PY "$D/check_archive_copies.py" "$R" "$O2/e7ebc1695/wbf/wbf_candidates.geojson" \
  "$D/w2-11-archive-copies.json"
$PY - "$O2/e9d1db0d0/check_union_provenance.json" "$D/w2-11-cup.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
rows = d.get("results") or d.get("unions") or d
out = []
for r in (rows if isinstance(rows, list) else []):
    out.append({k: r.get(k) for k in ("union_path", "classification", "detail",
                                      "committed_features", "rederived_features",
                                      "max_match_distance_m") if k in r})
json.dump({"n": len(out), "rows": out}, open(sys.argv[2], "w"), indent=1)
print(json.dumps([(r.get("union_path") or r.get("path"), r.get("classification")) for r in out], indent=0))
EOF
$PY - "$O2" "$D" <<'EOF'
import json, sys, glob, os
o2, d = sys.argv[1], sys.argv[2]
rp = {os.path.basename(f): json.load(open(f)) for f in sorted(glob.glob(f"{o2}/reparse/*.json"))}
json.dump(rp, open(f"{d}/w2-11-reparse.json", "w"), indent=1)
rm = {os.path.basename(f): json.load(open(f)) for f in sorted(glob.glob(f"{o2}/remerge/*.json"))}
json.dump(rm, open(f"{d}/w2-11-remerge.json", "w"), indent=1)
for k, v in rp.items():
    print(k, "probs", v["probabilities_byte_identical"], "meta", v["meta_all_equal"],
          {m: (x if not isinstance(x, list) else None) for m, x in v["meta_mismatches"].items()} if v["meta_mismatches"] else "")
for k, v in rm.items():
    print(k, [(f["path"].split("/")[-1], f["commit"], f["byte_identical"]) for f in v["files"]])
EOF
cp "$O2/c053f5a41.json" "$D/w2-11-c053f5a41.json"
