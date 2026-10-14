#!/usr/bin/env python3
"""
List the files one register-driven board reads: members' evaluations and their inputs.

Part of the S164 re-score (the two gold-standard K ladders the wrong-sheet
legs feed: ``k-ladder-gs-stride-a-2026-09-12`` and ``k-ladder-tier-e-2026-09-12``).
For an analysis row in a tiering-input ``run-analyses.json``, prints every
member's ``eval_path`` (from the paired ``run-conditions.json``) and the
detections, bounds, and ground truth its ``evaluate_detections.py``
arguments name, one path per line.

Usage: python ladder_files.py <repo_root> <run-analyses.json> <run-conditions.json> <analysis_id>

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import json
import sys
from pathlib import Path

root, ana, cond, aid = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
rows = json.loads((root / ana).read_text())
rows = rows["analyses"] if isinstance(rows, dict) else rows
row = next(r for r in rows if r["analysis_id"] == aid)
rc = json.loads((root / cond).read_text())["decomposition"]
paths = {ana, cond}
for cid in row["conditions_compared"]:
    run, label = cid.split("::")
    c = next(x for x in rc[run]["conditions"] if x["label"] == label)
    paths.add(c["eval_path"])
    doc = json.loads((root / c["eval_path"]).read_text())
    args = (doc.get("_metadata") or doc.get("metadata"))["cli_args"]
    for p in args.get("detections") or []:
        paths.add(p)
    for k in ("bounds", "ground_truth", "detections_dir"):
        if args.get(k):
            paths.add(args[k])
for p in sorted(paths):
    print(p)
