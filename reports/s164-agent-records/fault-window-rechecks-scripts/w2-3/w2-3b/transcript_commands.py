#!/usr/bin/env python3
"""Print Bash commands (and optionally their results) from session transcripts.

Fault-window re-check W2-3, part B (sub-agent w2-3b), 2026-10-15. Used on
amd-tower to recover the original commands, run order and run trees from the
archived Session 153 transcripts
(``~/cc-archives/map-reader-llm/2026-09-11T04-35_reconcile-campaign-billing-and-complete-k``,
``session.jsonl.gz`` and ``subagents/*.jsonl.gz``).

Usage: transcript_commands.py <regex> [--results N] <jsonl.gz> [...]
Matches Bash tool-use commands against the regex; with --results N, also
prints the first N characters of each matching command's tool result.
"""

from __future__ import annotations

import gzip
import json
import re
import sys


def main() -> None:
    """Scan each transcript and print the matching commands."""
    args = sys.argv[1:]
    pattern = re.compile(args.pop(0))
    n_result = 0
    if args and args[0] == "--results":
        args.pop(0)
        n_result = int(args.pop(0))
    for path in args:
        pending: set[str] = set()
        with gzip.open(path, "rt") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                content = (record.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                stamp = record.get("timestamp", "")
                for item in content:
                    if item.get("type") == "tool_use" and item.get("name") == "Bash":
                        command = item.get("input", {}).get("command", "")
                        if pattern.search(command):
                            print(f"## {path.split('/')[-1]} {stamp}\n{command[:4000]}\n")
                            pending.add(item.get("id"))
                    elif (item.get("type") == "tool_result" and n_result
                          and item.get("tool_use_id") in pending):
                        body = item.get("content")
                        if isinstance(body, list):
                            body = "\n".join(x.get("text", "") for x in body
                                             if isinstance(x, dict))
                        print(f"-- result {stamp}\n{str(body)[:n_result]}\n")


if __name__ == "__main__":
    main()
