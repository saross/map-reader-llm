"""Update the tail manifest's status for one or more citekeys.

Usage: python3 state.py <status> <citekey> [<citekey> ...]
Statuses used: queued | drafting | drafted | verifying | verified:<overall> |
editing | edited | rendered | escalate:<reason>
"""
import datetime as dt
import json
import sys

M = "/home/shawn/Code/map-reader-llm/outputs/ab-plus/manifests/tail-2026-09-02.json"
status, keys = sys.argv[1], sys.argv[2:]
d = json.load(open(M))
found = 0
for row in d["sources"]:
    if row["citekey"] in keys:
        row["status"] = status
        row["status_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        found += 1
json.dump(d, open(M, "w"), indent=1, ensure_ascii=False)
missing = set(keys) - {r["citekey"] for r in d["sources"]}
print(f"{found} updated -> {status}" + (f"; UNKNOWN: {sorted(missing)}" if missing else ""))
