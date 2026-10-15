#!/usr/bin/env python3
"""Score drifted pre-D50 cells on their inputs AS SCORED, pre-D50 and today (S9 sweep, S164).

Purpose
-------
Some pre-D50 evaluations in a signed lineage no longer reproduce on today's
inputs because their detection files changed after scoring (input drift; the
D57 (4) census, ``reports/s163-agent-records/d57-4-rescore-census.md``). Drift
hides whether the scorer itself would move them. This driver recovers each
cell's inputs as scored and scores them twice, exactly as D58 Q2 Stage A did
(``reports/d57-4-rescore-2026-10-09-scripts/q2_stage_a.py``, whose ``prepare``
and ``run_cell`` it calls unchanged):

* OLD: the pre-D50 tree (``git archive b3c52591d`` of ``scripts/``), which
  must reproduce the committed cell;
* NEW: today's code (``--repo``).

NEW − OLD on the same inputs is the scorer's effect alone. Inputs are
materialised with ``git show`` under ``--scratch/blobs``; outputs go to
``--scratch``. Recipes are full (bootstrap as recorded).

Usage::

    python vintage_cells.py --repo <wt> --old-tree <root>/codes/b3c52591d \\
        --cells queue-vintage-pinned.txt --scratch <root>/runs/vintage-A --workers 2

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any


def main() -> int:
    """Prepare and score every listed cell; write ``vintage.json``."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--old-tree", type=Path, required=True)
    ap.add_argument("--cells", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    if args.workers > 8:
        raise SystemExit("at most 8 workers (brief)")
    repo = args.repo.expanduser().resolve()
    old = args.old_tree.expanduser().resolve()
    scratch = args.scratch.expanduser().resolve()
    sys.path.insert(0, str(repo / "reports/d57-4-rescore-2026-10-09-scripts"))
    import d57_common as dc  # noqa: PLC0415
    import q2_stage_a as qa  # noqa: PLC0415

    os.environ["MAP_READER_VERIFY_DIRS"] = "fixed"
    for sub in ("blobs", "logs", "old", "new"):
        (scratch / sub).mkdir(parents=True, exist_ok=True)
    (scratch / "run.pid").write_text(f"{os.getpid()}\n")
    cells = [ln.strip() for ln in args.cells.read_text().splitlines() if ln.strip()]
    recs: list[dict[str, Any]] = []
    for rel in cells:
        ev = dc.committed_eval(repo, rel)
        det = dc.strip_frozen(ev["_metadata"]["cli_args"]["detections"][0])
        today_n = dc.feature_count(repo / det) if (repo / det).is_file() else None
        cell = {"eval": rel, "group": "s9-vintage",
                "feature_count": {"files": [{"n": today_n}]}}
        recs.append(qa.prepare(repo, cell, {}, scratch / "blobs"))

    def go(rec: dict[str, Any]) -> dict[str, Any]:
        """Score one recovered cell under both trees."""
        return qa.run_cell(rec, repo, old, scratch) if rec.get("recoverable") else rec

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        recs = list(pool.map(go, recs))
    for r in recs:
        r.pop("cli", None)
    (scratch / "vintage.json").write_text(json.dumps(recs, indent=1, sort_keys=True,
                                                     default=str) + "\n")
    n_rep = sum(bool(r.get("old_reproduces")) for r in recs)
    (scratch / "progress.log").write_text(f"DONE {len(recs)} cells; OLD reproduces {n_rep}\n")
    print(f"{len(recs)} cells; OLD reproduces {n_rep}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
