#!/usr/bin/env python3
"""
W2-3a comparison tool: regenerated files against committed git blobs.

For each line of a tab-separated pairs file (``regen_path``, ``commit``,
``repo_path``), the tool reads the regenerated file from disk and the
reference from ``git cat-file blob <commit>:<repo_path>``, compares SHA-256
first and, on a mismatch, falls back to a structured diff:

* JSON and GeoJSON: a recursive leaf diff (every differing leaf listed, key
  order reported separately); leaves whose KEY is named by ``--ignore-key``
  are set aside and reported as such.
* CSV: a cell diff.
* Other text: a line diff; lines matching an ``--ignore-line`` regular
  expression (in both files, at the same position) are set aside.

It also records, for every repo path, whether today's committed blob (at
``--today``, default ``origin/main``) is the same blob as the generating
commit's, so later edits can be followed up by a structured diff.

Usage::

    python compare_files.py --repo <git dir> --pairs pairs.tsv \
        --out result.json [--ignore-key generated_at_utc] \
        [--ignore-line '^> \\*\\*Last revised'] [--today origin/main]

Read-only on the repository; no network access; no API call.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def git_blob(repo: Path, commit: str, path: str) -> bytes | None:
    """Return the bytes of ``commit:path`` in ``repo``, or None when absent."""
    done = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "blob", f"{commit}:{path}"],
        capture_output=True, check=False,
    )
    return done.stdout if done.returncode == 0 else None


def blob_id(repo: Path, commit: str, path: str) -> str | None:
    """Return the blob id of ``commit:path``, or None when the path is absent."""
    done = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", "-q", f"{commit}:{path}"],
        capture_output=True, text=True, check=False,
    )
    return done.stdout.strip() if done.returncode == 0 else None


def leaf_diff(a: Any, b: Any, ignore: tuple[str, ...], path: str = "",
              out: list | None = None, ignored: list | None = None,
              limit: int = 500) -> tuple[list, list]:
    """Recursive leaf diff of two JSON values.

    Args:
        a: Regenerated value.
        b: Committed value.
        ignore: Key names whose differing values are set aside.
        path: JSON pointer-like path of ``a``/``b``.
        out: Accumulator of differences.
        ignored: Accumulator of set-aside differences.
        limit: Stop listing differences after this many.

    Returns:
        ``(differences, set_aside_differences)``.
    """
    out = [] if out is None else out
    ignored = [] if ignored is None else ignored
    if len(out) >= limit:
        return out, ignored
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b), key=str):
            sub = f"{path}/{key}"
            if key not in a or key not in b:
                rec = {"path": sub, "regen": a.get(key, "<missing>"),
                       "committed": b.get(key, "<missing>")}
                (ignored if key in ignore else out).append(rec)
            elif key in ignore:
                if a[key] != b[key]:
                    ignored.append({"path": sub, "regen": a[key], "committed": b[key]})
            else:
                leaf_diff(a[key], b[key], ignore, sub, out, ignored, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append({"path": path, "regen_len": len(a), "committed_len": len(b)})
        for index, (x, y) in enumerate(zip(a, b)):
            leaf_diff(x, y, ignore, f"{path}[{index}]", out, ignored, limit)
    elif a != b or type(a) is not type(b):
        rec = {"path": path, "regen": a, "committed": b}
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            rec["abs_diff"] = abs(a - b)
        out.append(rec)
    return out, ignored


def key_order_equal(a: Any, b: Any) -> bool:
    """True when every dict in the two values lists its keys in the same order."""
    if isinstance(a, dict) and isinstance(b, dict):
        return list(a) == list(b) and all(key_order_equal(a[k], b[k]) for k in a if k in b)
    if isinstance(a, list) and isinstance(b, list):
        return all(key_order_equal(x, y) for x, y in zip(a, b))
    return True


def compare_one(regen_path: Path, ref: bytes, repo_path: str,
                ignore: tuple[str, ...], ignore_lines: list[re.Pattern]) -> dict:
    """Compare one regenerated file with its committed bytes."""
    res: dict[str, Any] = {}
    regen = regen_path.read_bytes()
    res["sha256_regen"] = hashlib.sha256(regen).hexdigest()
    res["sha256_committed"] = hashlib.sha256(ref).hexdigest()
    res["bytes_regen"], res["bytes_committed"] = len(regen), len(ref)
    if regen == ref:
        res["verdict"] = "BYTE-IDENTICAL"
        return res
    if repo_path.endswith((".json", ".geojson")):
        a, b = json.loads(regen), json.loads(ref)
        diffs, set_aside = leaf_diff(a, b, ignore)
        res["n_leaf_diffs"] = len(diffs)
        res["leaf_diffs"] = diffs[:60]
        res["n_set_aside"] = len(set_aside)
        res["set_aside"] = set_aside[:20]
        res["key_order_equal"] = key_order_equal(a, b)
        res["verdict"] = "FIELD-IDENTICAL" if not diffs else "DIFFERS"
    elif repo_path.endswith(".csv"):
        ra = list(csv.reader(io.StringIO(regen.decode())))
        rb = list(csv.reader(io.StringIO(ref.decode())))
        cells: list[dict] = []
        if len(ra) != len(rb):
            cells.append({"rows_regen": len(ra), "rows_committed": len(rb)})
        for i, (x, y) in enumerate(zip(ra, rb)):
            for j, (u, v) in enumerate(zip(x, y)):
                if u != v:
                    cells.append({"row": i, "col": j, "regen": u, "committed": v})
        res["n_cell_diffs"] = len(cells)
        res["cell_diffs"] = cells[:50]
        res["verdict"] = "CELL-IDENTICAL" if not cells else "DIFFERS"
    else:
        la = regen.decode(errors="replace").splitlines()
        lb = ref.decode(errors="replace").splitlines()
        diffs = []
        set_aside = []
        if len(la) != len(lb):
            diffs.append({"lines_regen": len(la), "lines_committed": len(lb)})
        for i, (x, y) in enumerate(zip(la, lb)):
            if x == y:
                continue
            rec = {"line": i + 1, "regen": x, "committed": y}
            if any(p.search(x) and p.search(y) for p in ignore_lines):
                set_aside.append(rec)
            else:
                diffs.append(rec)
        res["n_line_diffs"] = len(diffs)
        res["line_diffs"] = diffs[:30]
        res["n_set_aside"] = len(set_aside)
        res["set_aside"] = set_aside[:10]
        res["verdict"] = "LINE-IDENTICAL" if not diffs else "DIFFERS"
    return res


def main() -> int:
    """Parse arguments, compare every pair, and write the JSON result."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--pairs", required=True, type=Path,
                        help="TSV: regen_path, commit, repo_path")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--ignore-key", action="append", default=[])
    parser.add_argument("--ignore-line", action="append", default=[])
    parser.add_argument("--today", default="origin/main")
    args = parser.parse_args()
    ignore = tuple(args.ignore_key)
    ignore_lines = [re.compile(p) for p in args.ignore_line]
    results = []
    for line in args.pairs.read_text().splitlines():
        if not line.strip():
            continue
        regen_path, commit, repo_path = line.split("\t")
        rec: dict[str, Any] = {"repo_path": repo_path, "commit": commit,
                               "regen_path": regen_path}
        ref = git_blob(args.repo, commit, repo_path)
        if ref is None:
            rec["verdict"] = "NO-COMMITTED-BLOB"
        elif not Path(regen_path).exists():
            rec["verdict"] = "MISSING-REGEN"
        else:
            rec.update(compare_one(Path(regen_path), ref, repo_path, ignore, ignore_lines))
        gen_blob = blob_id(args.repo, commit, repo_path)
        today_blob = blob_id(args.repo, args.today, repo_path)
        rec["today_same_blob"] = gen_blob is not None and gen_blob == today_blob
        rec["today_blob"] = today_blob
        results.append(rec)
    summary: dict[str, int] = {}
    for rec in results:
        summary[rec["verdict"]] = summary.get(rec["verdict"], 0) + 1
    n_today_changed = sum(1 for r in results if not r["today_same_blob"])
    out = {"ignore_keys": list(ignore), "ignore_lines": args.ignore_line,
           "today": args.today, "n_files": len(results), "summary": summary,
           "n_today_blob_differs": n_today_changed, "files": results}
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"n_files": len(results), "summary": summary,
                      "n_today_blob_differs": n_today_changed}))
    for rec in results:
        if rec["verdict"] not in ("BYTE-IDENTICAL",):
            print(f"{rec['verdict']:18s} {rec['commit'][:9]} {rec['repo_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
