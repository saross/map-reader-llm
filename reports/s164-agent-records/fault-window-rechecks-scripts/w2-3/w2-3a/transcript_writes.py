"""W2-3a: print every Write or Edit tool call whose file_path matches a regex.

Reads one session transcript (jsonl.gz); used to recover the original driver scripts.
"""
import gzip
import json
import re
import sys

path, rx = sys.argv[1], sys.argv[2]
with gzip.open(path, "rt") as fh:
    for line in fh:
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if c.get("type") != "tool_use" or c.get("name") not in ("Write", "Edit"):
                continue
            inp = c.get("input", {})
            fp = inp.get("file_path", "")
            if re.search(rx, fp):
                print("=====", rec.get("timestamp"), c["name"], fp)
                if c["name"] == "Write":
                    print(inp.get("content"))
                else:
                    print("--- OLD\n" + str(inp.get("old_string")))
                    print("--- NEW\n" + str(inp.get("new_string")))
