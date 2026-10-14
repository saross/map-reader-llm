#!/usr/bin/env python3
"""
Compare regenerated files with committed ones (fault-window re-check, 2026-10-14).

Reads a JSON spec: a list of {"label", "regen", "commit", "path"} entries,
optionally with "ignore" (a list of JSON leaf paths, as dotted strings, to
skip in the field-by-field diff; only timestamps and machine paths are ever
listed) and "strip_re" (a regex whose matching LINES are dropped before a
text comparison, for log headers carrying a wall-clock time).

For each entry it:
1. compares the regenerated file byte for byte with ``git show
   <commit>:<path>`` (SHA-256 of both);
2. if they differ and both parse as JSON, walks every leaf and reports the
   first differing leaves with their values (``ignore`` applied);
3. if they differ and are text with ``strip_re``, compares the remaining lines;
4. reports whether origin/main (``--head``) holds the same bytes as the
   generating commit, and if not, which commits changed the path since.

Usage:
    python compare_files.py --repo REPO --spec spec.json --out result.json \
        [--head 90294a283]

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def git_bytes(repo: Path, commit: str, path: str) -> bytes | None:
    """Return the bytes of ``commit:path``, or None when the path is absent."""
    r = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def sha(b: bytes | None) -> str | None:
    """SHA-256 hex digest of bytes (None passes through)."""
    return None if b is None else hashlib.sha256(b).hexdigest()


def leaves(obj: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten a JSON value to {dotted path: leaf}; list indices become [i]."""
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        if not obj:
            out[prefix or "."] = {}
        for k, v in obj.items():
            out.update(leaves(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        if not obj:
            out[prefix or "."] = []
        for i, v in enumerate(obj):
            out.update(leaves(v, f"{prefix}[{i}]"))
    else:
        out[prefix or "."] = obj
    return out


def ignored(path: str, patterns: list[str]) -> bool:
    """True when a leaf path matches one of the regex patterns."""
    return any(re.fullmatch(p, path) for p in patterns)


def json_diff(a: bytes, b: bytes, ignore: list[str], limit: int = 12) -> dict[str, Any]:
    """Field-by-field diff of two JSON documents (``ignore`` = regexes on leaf paths)."""
    la, lb = leaves(json.loads(a)), leaves(json.loads(b))
    keys = sorted(set(la) | set(lb))
    diffs, skipped = [], []
    for k in keys:
        if la.get(k, "<absent>") != lb.get(k, "<absent>"):
            if ignored(k, ignore):
                skipped.append(k)
            else:
                diffs.append({"leaf": k, "regen": la.get(k, "<absent>"),
                              "committed": lb.get(k, "<absent>")})
    return {"n_leaves_regen": len(la), "n_leaves_committed": len(lb),
            "n_differing": len(diffs), "first": diffs[:limit],
            "ignored_differing": skipped,
            "equal_ignoring": not diffs}


def main() -> int:
    """Run the comparisons in a spec and write a summary JSON."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--head", default="90294a283")
    args = ap.parse_args()
    spec = json.loads(args.spec.read_text())
    results = []
    for e in spec:
        regen = Path(e["regen"]).read_bytes() if Path(e["regen"]).exists() else None
        comm = git_bytes(args.repo, e["commit"], e["path"])
        head = git_bytes(args.repo, args.head, e["path"])
        row: dict[str, Any] = {
            "label": e["label"], "path": e["path"], "commit": e["commit"],
            "regen_sha256": sha(regen), "committed_sha256": sha(comm),
            "byte_identical": regen is not None and regen == comm,
            "head_equals_generating": head == comm,
            "head_sha256": sha(head),
        }
        if not row["head_equals_generating"]:
            log = subprocess.run(
                ["git", "-C", str(args.repo), "log", "--format=%h %ad %s",
                 "--date=short", f"{e['commit']}..{args.head}", "--", e["path"]],
                capture_output=True, text=True).stdout.strip().splitlines()
            row["changed_since_by"] = log
        if regen is not None and comm is not None and not row["byte_identical"]:
            strip = e.get("strip_re")
            sub = e.get("sub_re")
            if strip or sub:
                def norm(b: bytes) -> list[str]:
                    """Drop strip_re lines; blank sub_re matches (timestamps only)."""
                    lines = b.decode().splitlines()
                    if strip:
                        lines = [ln for ln in lines if not re.search(strip, ln)]
                    if sub:
                        lines = [re.sub(sub, "<TS>", ln) for ln in lines]
                    return lines
                ra, rb = norm(regen), norm(comm)
                row["text_equal_after_strip"] = ra == rb
                row["strip_re"], row["sub_re"] = strip, sub
                if ra != rb:
                    row["first_text_diffs"] = [
                        {"i": i, "regen": x, "committed": y}
                        for i, (x, y) in enumerate(zip(ra, rb)) if x != y][:6]
                    row["n_lines"] = [len(ra), len(rb)]
            else:
                try:
                    row["json"] = json_diff(regen, comm, e.get("ignore", []))
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    row["json_error"] = str(exc)
        results.append(row)
    args.out.write_text(json.dumps(results, indent=1) + "\n")
    n_ok = sum(1 for r in results if r["byte_identical"]
               or r.get("text_equal_after_strip")
               or (r.get("json") or {}).get("equal_ignoring"))
    print(f"{len(results)} compared; byte-identical "
          f"{sum(r['byte_identical'] for r in results)}; equal after declared "
          f"ignores {n_ok}; head==generating "
          f"{sum(r['head_equals_generating'] for r in results)}")
    for r in results:
        flag = ("BYTES" if r["byte_identical"] else
                "TEXT-EQ" if r.get("text_equal_after_strip") else
                "JSON-EQ" if (r.get("json") or {}).get("equal_ignoring") else "DIFFERS")
        print(f"  {flag:8s} head={'same' if r['head_equals_generating'] else 'CHANGED'} "
              f"{r['label']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
