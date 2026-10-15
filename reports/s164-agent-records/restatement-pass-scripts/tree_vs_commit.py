#!/usr/bin/env python3
"""
List files in a copy's subtrees that differ from (or are absent in) a git tree.

Usage: python tree_vs_commit.py <copy_root> <repo_root> <subdir> [<subdir> ...]
Prints: STATUS<TAB>relpath, STATUS in {SAME, DIFF, NEW}; and DELETED for
tracked files under the subdirs that the copy lacks.

Part of the S164 restatement pass: it names the files a chain copy wrote,
which are the ones copied back into the worktree.

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import subprocess
import sys
from pathlib import Path

copy, repo = Path(sys.argv[1]), Path(sys.argv[2])
subdirs = sys.argv[3:]
tracked = set(subprocess.run(["git", "-C", str(repo), "ls-files", "--", *subdirs],
                             capture_output=True, text=True, check=True).stdout.split())
seen = set()
for sd in subdirs:
    for p in sorted((copy / sd).rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(copy))
        seen.add(rel)
        if rel not in tracked:
            print(f"NEW\t{rel}")
            continue
        a = p.read_bytes()
        b = (repo / rel).read_bytes()
        print(("SAME" if a == b else "DIFF") + "\t" + rel)
for rel in sorted(tracked - seen):
    print(f"DELETED\t{rel}")
