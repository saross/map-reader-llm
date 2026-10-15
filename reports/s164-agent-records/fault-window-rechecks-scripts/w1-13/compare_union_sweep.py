#!/usr/bin/env python3
"""Compare a replayed union-provenance sweep with the committed one (W1-13).

Fault-window re-check, Session 164 (2026-10-14). The committed file is
reports/stale-register-notes-2026-10-07-union-sweep-2026-10-08.json (commit
da86896c4), written by scripts/check_union_provenance.py --all (v1.1.0). The
replay ran the same command with that commit's code on the fixed machine.

The only field ignored is each result's ``seconds`` (wall time of that union's
check). Everything else (classification, feature counts, unmatched counts,
match distances, pass lists, read_by, counts block) must be equal.

Usage::

    python compare_union_sweep.py <committed.json> <replay.json>

Prints a summary and exits 0 when the two agree on every compared leaf.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

IGNORED = {"seconds"}


def strip(obj):
    """Return ``obj`` with every ignored key removed, recursively."""
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k not in IGNORED}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def leaf_diff(a, b, path="", out=None):
    """Collect (path, a, b) for every differing leaf between ``a`` and ``b``."""
    if out is None:
        out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            leaf_diff(a.get(k, "<absent>"), b.get(k, "<absent>"), f"{path}/{k}", out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            leaf_diff(x, y, f"{path}[{i}]", out)
    elif a != b:
        out.append((path, a, b))
    return out


def main() -> int:
    """Compare and report."""
    committed = json.loads(Path(sys.argv[1]).read_text())
    replay = json.loads(Path(sys.argv[2]).read_text())
    diffs = leaf_diff(strip(committed), strip(replay))
    print(f"committed results: {len(committed.get('results', []))}; "
          f"replay results: {len(replay.get('results', []))}")
    print(f"committed counts: {committed.get('counts')}")
    print(f"replay counts:    {replay.get('counts')}")
    print(f"differing leaves (ignoring {sorted(IGNORED)}): {len(diffs)}")
    for p, x, y in diffs[:40]:
        print(f"  {p}: committed={x!r} replay={y!r}")
    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(main())
