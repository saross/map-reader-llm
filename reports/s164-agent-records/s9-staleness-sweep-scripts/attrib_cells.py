#!/usr/bin/env python3
"""Attribute a moved evaluation to a scorer change: replay its points under older trees.

Purpose
-------
The S9 staleness sweep (S164, 2026-10-14) finds committed evaluations whose
points differ under today's scorer. To say why, each mover is replayed, points
only, with its recorded recipe under the ``scripts/`` of several commits
(``git archive`` copies under ``--codes``), always reading TODAY's inputs from
``--repo``. If the pre-D50 tree reproduces the committed points and a later
tree does not, the first tree that moves them names the change; if no tree
reproduces them, the inputs have changed since the cell was scored.

Each replay is a fresh ``python <tree>/scripts/evaluate_detections.py``
process with ``--bootstrap 50`` (points do not depend on it) and every input
path made absolute into ``--repo``, so nothing is read from, or written to,
any checkout but scratch. Comparison: F1, P and R at every buffer, the
detection count, and the tile confusion and MCC point
(``compare.compare_cell(..., points_only=True)``).

Usage::

    python attrib_cells.py --repo <wt> --codes <root>/codes --revs b3c52591d 8988f3f17 \\
        --cells movers.txt --out <root>/attrib [--workers 4]

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def abs_argv(repo: Path, argv: list[str]) -> list[str]:
    """Make every input path in a built argv absolute into ``repo``."""
    out: list[str] = []
    path_flags = {"--detections", "--detections-dir", "--ground-truth", "--bounds"}
    in_paths = False
    for tok in argv:
        if tok.startswith("--"):
            in_paths = tok in path_flags
            out.append(tok)
            continue
        if in_paths and not tok.startswith("/"):
            out.append(str(repo / tok))
        else:
            out.append(tok)
    return out


def one(repo: Path, codes: Path, rev: str, out: Path, rel: str) -> dict[str, Any]:
    """Replay one cell under one tree and compare its points with the committed file."""
    sys.path.insert(0, str(repo / "reports/d57-4-rescore-2026-10-09-scripts"))
    sys.path.insert(0, str(HERE))
    import compare  # noqa: PLC0415
    import replay_cell  # noqa: PLC0415

    committed = json.loads((repo / rel).read_text())
    cli = dict((committed.get("_metadata") or {}).get("cli_args") or {})
    cli["bootstrap"] = 50
    cell_out = out / rev / "cells" / Path(rel).parent
    argv, _ = replay_cell.build_argv(repo, cli, str(cell_out), False)
    argv = abs_argv(repo, argv)
    tree = repo if rev == "today" else codes / rev
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", MAP_READER_VERIFY_DIRS="fixed")
    log = out / rev / "logs" / (rel.replace("/", "__") + ".log")
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as fh:
        rc = subprocess.run([sys.executable, str(tree / "scripts/evaluate_detections.py"),
                             *argv], cwd=str(tree), stdout=fh, stderr=subprocess.STDOUT,
                            env=env, check=False).returncode
    rec: dict[str, Any] = {"eval": rel, "rev": rev, "rc": rc}
    rep = cell_out / "evaluation.json"
    if rc == 0 and rep.is_file():
        cmp = compare.compare_cell(committed, json.loads(rep.read_text()), points_only=True)
        rec.update({"points_reproduce": cmp["identical"], "at20": cmp["at20"],
                    "mcc_point": cmp["mcc_point"], "n_det": cmp["n_det"],
                    "scope": cmp["scope"], "examples": cmp["examples"][:6]})
    return rec


def main() -> int:
    """Replay every listed cell under every listed tree; write ``attrib.json``."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--codes", type=Path, required=True)
    ap.add_argument("--revs", nargs="+", required=True,
                    help="Tree names under --codes, or 'today' for --repo.")
    ap.add_argument("--cells", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if args.workers > 8:
        raise SystemExit("at most 8 workers (brief)")
    repo = args.repo.expanduser().resolve()
    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.pid").write_text(f"{os.getpid()}\n")
    cells = [ln.strip() for ln in args.cells.read_text().splitlines() if ln.strip()]
    jobs = [(rev, rel) for rel in cells for rev in args.revs]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        recs = list(pool.map(lambda j: one(repo, args.codes.resolve(), j[0], out, j[1]), jobs))
    by_cell: dict[str, dict[str, Any]] = {}
    for r in recs:
        by_cell.setdefault(r["eval"], {})[r["rev"]] = r
    (out / "attrib.json").write_text(json.dumps({"revs": args.revs, "cells": by_cell},
                                                indent=1, sort_keys=True) + "\n")
    n_fail = sum(r["rc"] != 0 for r in recs)
    (out / "progress.log").write_text(f"DONE {len(recs)} replays; failed {n_fail}\n")
    print(f"{len(recs)} replays; failed {n_fail}")
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
