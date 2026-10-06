import json
import sys
import statistics
from collections import Counter

rows = []
for p in open(sys.argv[1]).read().split():
    try:
        d = json.load(open(p))
    except Exception as e:
        print("ERR", p, e)
        continue
    c = d.get("configuration", {})
    if c.get("model") != "gemini-3-flash-preview":
        continue
    T = c.get("temperature")
    L = c.get("thinking_level")
    if not ((T == 0.3 and L == "minimal") or (T == 0.0 and L == "high")):
        continue
    pim = d.get("per_item_metadata", []) or []
    fs = c.get("full_config_snapshot", {})
    ex = [e.get("path") for e in fs.get("examples", [])]
    cached = Counter((i.get("tokens") or {}).get("cached_input_tokens") for i in pim)
    inp = Counter((i.get("tokens") or {}).get("input_tokens") for i in pim)
    th = [((i.get("tokens") or {}).get("thoughts_tokens") or 0) for i in pim]
    dates = sorted(Counter((i.get("request_timestamp") or "")[:10] for i in pim).items())
    rows.append(
        (
            d["timestamp"]["start"][:16],
            p,
            T,
            L,
            len(pim),
            dict(cached.most_common(2)),
            dict(inp.most_common(2)),
            statistics.median(th) if th else None,
            d.get("results_summary", {}).get("total_detections"),
            d.get("environment", {}).get("git_commit", "")[:9],
            fs.get("ordering_override"),
            len(ex),
            dates,
            "batch_api" in d,
        )
    )
rows.sort()
for r in rows:
    print(" | ".join(str(x) for x in r))
