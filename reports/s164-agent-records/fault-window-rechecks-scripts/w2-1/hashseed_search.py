#!/usr/bin/env python3
"""
W2-1: find a PYTHONHASHSEED under which a replicate driver's label set
iterates in the order the committed tests.json records.

The replicate drivers fill their cell cache with
``for label in {lbl for _, a, b, _ in tests for lbl in (a, b)}``, so the key
order of ``n_detections`` / ``tile_confusion`` in tests.json is the string-hash
iteration order of that set: it varies with PYTHONHASHSEED (random when
unpinned) and carries no computed value. The insertion sequence is recovered
from the committed file itself (the ``f1_tests`` rows, in order, are the
driver's ``tests`` list). For each candidate seed a bare interpreter
(``-S``; NOT ``-I``, which implies ``-E`` and would ignore
PYTHONHASHSEED -- the first version of this tool had that bug) rebuilds
the same set comprehension and reports its order; the
first seed matching the committed order is printed, so the stage can be
re-run under it and compared byte for byte.

Usage::

    python hashseed_search.py --tree <repo> --spec <commit>:<tests.json> [--max 20000]

Zero API; spawns only bare interpreters (no imports beyond json).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def main() -> int:
    """Search seeds; print the first match."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--max", type=int, default=20000)
    ap.add_argument("--show-seed", type=int, default=None,
                    help="Print the order under this one seed and exit (self-check)")
    args = ap.parse_args()
    doc = json.loads(subprocess.run(["git", "-C", args.tree, "show", args.spec],
                                    check=True, capture_output=True, text=True).stdout)
    pairs = [(r["a"], r["b"]) for r in doc["f1_tests"]]
    want = list(doc["n_detections"])
    code = ("import json,sys\npairs=json.loads(sys.argv[1])\n"
            "print(json.dumps(list({l for a, b in pairs for l in (a, b)})))")
    print("pairs", pairs)
    print("committed order", want)
    seeds = [args.show_seed] if args.show_seed is not None else range(args.max)
    for seed in seeds:
        env = dict(os.environ, PYTHONHASHSEED=str(seed))
        got = json.loads(subprocess.run([sys.executable, "-S", "-c", code,
                                         json.dumps(pairs)], env=env, check=True,
                                        capture_output=True, text=True).stdout)
        if args.show_seed is not None:
            print(f"seed {seed} order {got}")
            return 0
        if got == want:
            print(f"MATCH seed {seed}")
            return 0
    print("no match")
    return 1


if __name__ == "__main__":
    sys.exit(main())
