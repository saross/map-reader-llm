#!/usr/bin/env bash
# =============================================================================
# W1-8 fault-window re-check (2026-10-14): collect the compact results.
#
# Copies the comparison outputs (never the regenerated bulk files) from the
# out tree into this directory, merged per kind:
#   w1-8-compare.json           79 regenerated files against committed ones
#   w1-8-reparse.json           ten verifier legs re-parsed from batch results
#   w1-8-remerge.json           five chunked g37-image passes re-merged
#   w1-8-cost-audit-summary.json  re-run audits against the quoted figures
#   w1-8-later-changes.json     the D62 (1) edits to the repaired copies
#   w1-8-replay-heads.txt       the commit each arm's steps ran at
#   w1-8-dedup-bonus.txt        regenerated dedup passes vs the W1 originals
# =============================================================================
set -uo pipefail
D=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w1-8-w2-11
O=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-out/runb
PY=$HOME/Code/map-reader-llm/.venv/bin/python
cp "$O/compare.json" "$D/w1-8-compare.json"
cp "$O/audit/summary.json" "$D/w1-8-cost-audit-summary.json"
cp "$O/later-changes.json" "$D/w1-8-later-changes.json"
$PY - "$O" "$D" <<'EOF'
import glob, json, os, sys
o, d = sys.argv[1], sys.argv[2]
for kind, pat in (("reparse", "reparse/*.json"), ("remerge", "remerge/*.json")):
    data = {os.path.basename(f): json.load(open(f)) for f in sorted(glob.glob(f"{o}/{pat}"))}
    json.dump(data, open(f"{d}/w1-8-{kind}.json", "w"), indent=1)
    print(kind, len(data))
EOF
for a in "$O"/regen/*/; do echo "$(basename "$a"): $(tr '\n' ' ' < "$a/replay.txt")"; done \
  > "$D/w1-8-replay-heads.txt"
ls -la "$D"/w1-8-*
