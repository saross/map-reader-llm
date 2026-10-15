#!/usr/bin/env python3
"""Print Write/Edit tool inputs whose file path matches a regex, from transcripts.

Fault-window re-check W2-3, part B (sub-agent w2-3b), 2026-10-15. Used on
amd-tower to recover the original job scripts (``final_downstream.sh``,
``chain_bcd.sh``) that the Session 153 agents wrote to their scratchpads.

Usage: transcript_writes.py <regex> <jsonl.gz> [...]
"""

from __future__ import annotations

import gzip
import json
import re
import sys


def main() -> None:
    """Scan each transcript and print the matching Write/Edit inputs."""
    pattern = re.compile(sys.argv[1])
    for path in sys.argv[2:]:
        with gzip.open(path, "rt") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                content = (record.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for item in content:
                    if item.get("type") != "tool_use" or item.get("name") not in (
                            "Write", "Edit"):
                        continue
                    data = item.get("input", {})
                    if not pattern.search(data.get("file_path", "")):
                        continue
                    print(f"## {item['name']} {data.get('file_path')} "
                          f"{record.get('timestamp', '')}")
                    if item["name"] == "Write":
                        print(data.get("content", ""))
                    else:
                        print("OLD:", data.get("old_string", ""))
                        print("NEW:", data.get("new_string", ""))
                    print()


if __name__ == "__main__":
    main()
