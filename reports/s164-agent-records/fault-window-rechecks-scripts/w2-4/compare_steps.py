#!/usr/bin/env python3
"""W2-4: compare every file a replayed step wrote with its generating commit.

For each ``<out>/<generating commit>/`` directory written by
``replay_cells.sh`` or ``replay_sweep.sh``, every regenerated file is
compared with ``git show <generating commit>:<path>`` by
``compare_json.compare`` (bytes, then JSON leaves or CSV cells). A file the
step wrote that the generating commit did not change is compared with that
commit's blob all the same, and flagged ``in_commit: false``. Files the
generating commit changed under the board home that the step did not write
are listed as ``not_regenerated``.

Usage: compare_steps.py <repo> <out dir> <commit> [<commit> ...]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compare_json import compare  # noqa: E402


def git(repo: Path, *args: str) -> bytes:
    """Run a git command in ``repo`` and return its stdout."""
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          check=True).stdout


def main() -> int:
    """Compare each step's outputs and print one JSON summary per step."""
    repo, out = Path(sys.argv[1]), Path(sys.argv[2])
    worst = 0
    for commit in sys.argv[3:]:
        base = out / commit
        changed = set(git(repo, "show", "--name-only", "--format=", commit).decode().split())
        written = sorted(str(p.relative_to(base)) for p in base.rglob("*") if p.is_file())
        rows = []
        for rel in written:
            try:
                old = git(repo, "show", f"{commit}:{rel}")
            except subprocess.CalledProcessError:
                rows.append({"path": rel, "in_commit": False, "committed": "absent"})
                continue
            rec = compare(old, (base / rel).read_bytes(), Path(rel).suffix, set())
            rec.pop("sha256_committed", None)
            rows.append({"path": rel, "in_commit": rel in changed, **rec})
        regenerated = {r["path"] for r in rows}
        summary = {
            "commit": commit,
            "files_written": len(rows),
            "bytes_equal": sum(bool(r.get("bytes_equal")) for r in rows),
            "in_commit_written": sum(bool(r.get("in_commit")) for r in rows),
            "commit_files": len(changed),
            "not_regenerated": sorted(changed - regenerated),
            "differing": [r for r in rows if not r.get("bytes_equal")],
        }
        worst = max(worst, len(summary["differing"]))
        print(json.dumps(summary, indent=1))
    return 1 if worst else 0


if __name__ == "__main__":
    sys.exit(main())
