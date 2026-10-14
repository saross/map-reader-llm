#!/usr/bin/env python3
"""Decide which gitignored detection inputs can be staged for replay (S9 sweep, S164).

Purpose
-------
Some pre-D50 evaluations score raw-pass directories under ``outputs/`` that
are gitignored, so a fresh worktree lacks them. Sapphire's shared checkout
usually still holds them. This script, read-only, checks for each such cell
(from ``inventory.json``) whether the shared checkout's copy resolves, with
the scorer's own resolver (``evaluate_detections.find_detection_files``), to
files whose per-run feature counts equal the committed evaluation's
``n_detections`` (summary, or per run). Only cells that match are staged
(copied into the sweep's worktree, where they stay ignored) and replayed.

An earlier version globbed the top level only and wrongly reported 22
directories as mismatched; the resolver is what the scorer uses.

Usage::

    python staged_inputs.py <scratch root> <shared checkout>
    # writes <root>/inventory/missing-inputs.json and prints counts

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path


def main() -> int:
    """Classify every pre-D50 replayable cell whose inputs are missing."""
    root = Path(sys.argv[1]).expanduser().resolve()
    shared = Path(sys.argv[2]).expanduser().resolve()
    sys.path.insert(0, str(root / "wt"))
    os.chdir(root)
    from scripts.evaluate_detections import find_detection_files  # noqa: PLC0415

    cells = json.loads((root / "inventory/inventory.json").read_text())["cells"]
    miss = [c for c in cells if not c["d50_scored"] and c["replayable"]
            and not c["inputs_present"]]
    out: Counter = Counter()
    rows = []
    for c in miss:
        ev = json.loads((root / "wt" / c["eval"]).read_text())
        cli = ev["_metadata"]["cli_args"]
        per_run = ev.get("per_run") or []
        committed_n = ([r.get("n_detections") for r in per_run]
                       or [ev["summary"].get("n_detections")])
        status = "absent"
        try:
            if cli.get("detections_dir"):
                d = shared / cli["detections_dir"].split("/map-reader-llm/")[-1]
                if d.is_dir():
                    files = find_detection_files(d, cli.get("glob"))
                    ns = [len(json.loads(Path(f).read_text()).get("features") or [])
                          for f in files]
                    status = ("counts-match" if ns == committed_n
                              else f"counts-differ {ns[:3]} vs {committed_n[:3]}")
            else:
                ps = [shared / p["path"] for p in c["detections"]]
                if all(p.is_file() for p in ps):
                    ns = [len(json.loads(p.read_text()).get("features") or []) for p in ps]
                    status = "counts-match" if ns == committed_n else "counts-differ"
        except Exception as exc:  # noqa: BLE001 - recorded per cell
            status = f"error {type(exc).__name__}"
        lineage = bool(c["signed_analyses"] or c["claim_rows"])
        out[("/".join(c["eval"].split("/")[:3]), lineage, status.split(" [")[0][:20])] += 1
        rows.append({"eval": c["eval"], "lineage": lineage, "status": status,
                     "detections_dir": cli.get("detections_dir")})
    for k, v in sorted(out.items()):
        print(v, k)
    (root / "inventory/missing-inputs.json").write_text(json.dumps(rows, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
