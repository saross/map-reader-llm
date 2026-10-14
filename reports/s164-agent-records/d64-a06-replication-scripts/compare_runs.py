#!/usr/bin/env python3
"""Compare two independent runs of d64_a06_replication.py (plan P10).

The two runs are fresh processes with separate output directories and
different ``PYTHONHASHSEED`` values. Every output must be identical apart
from timestamps: the results JSON after its ``generated_at`` field is
removed, the CSVs byte for byte, and the per-pass counts archive member by
member (a ``.npz`` is a zip whose container stamps write times, so its
members' bytes are compared, not the file's).

Usage::

    python compare_runs.py <run_dir_1> <run_dir_2>

Exits 0 when identical, 1 otherwise, printing one line per file.

Author: Shawn Ross & Claude (Anthropic), Session 164, 2026-10-14
Licence: Apache 2.0
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

TIMESTAMP_FIELDS = ("generated_at",)


def json_digest(path: Path) -> str:
    """SHA-256 of a JSON document with its timestamp fields removed."""
    doc = json.loads(path.read_text())
    for key in TIMESTAMP_FIELDS:
        doc.pop(key, None)
    return hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()


def npz_digest(path: Path) -> str:
    """SHA-256 over an npz archive's member names and member bytes."""
    h = hashlib.sha256()
    with zipfile.ZipFile(path) as zf:
        for name in sorted(zf.namelist()):
            h.update(name.encode())
            h.update(zf.read(name))
    return h.hexdigest()


def digest(path: Path) -> str:
    """Pick the comparison appropriate to the file type."""
    if path.suffix == ".json":
        return json_digest(path)
    if path.suffix == ".npz":
        return npz_digest(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    """Compare every file present in either run directory."""
    a, b = Path(sys.argv[1]), Path(sys.argv[2])
    names = sorted({p.name for p in a.iterdir()} | {p.name for p in b.iterdir()})
    ok = True
    for name in names:
        pa, pb = a / name, b / name
        if not (pa.exists() and pb.exists()):
            print(f"MISSING {name}")
            ok = False
            continue
        da, db = digest(pa), digest(pb)
        same = da == db
        ok &= same
        print(f"{'identical' if same else 'DIFFERENT'} {name} {da[:16]}")
    print("ALL IDENTICAL" if ok else "RUNS DIFFER")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
