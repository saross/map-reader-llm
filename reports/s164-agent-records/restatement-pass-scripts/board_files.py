#!/usr/bin/env python3
"""
List every committed file the Era-2 board's tiering and MCB read, and the cells that move.

Part of the S164 re-score. The board (``gs-era2-verified-board-2026-09-10``)
is tiered by ``era1_leaderboard_tiering.py`` from each member's evaluation
``cli_args`` (detections, bounds, ground truth), membership from the board's
``tiering-input/run-analyses.json``. This prints, one per line, every path a
disposable board copy needs, and (with --moved) the members whose detection
file one of the 14 signed analyses' generators rewrites in the chain copies.

Usage: python board_files.py <repo_root> [--moved]

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
BOARD = "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"
#: Detection files the chain regenerates (chain.sh, conditions.py).
REGENERATED = {
    "results/gemini37-image-gs-2026-09-01/arm1/verified_best_20m.geojson",
    "results/gemini37-image-gs-2026-09-01/arm2/verified_best_20m.geojson",
    "results/gemini37-screen-2026-08-28/verified_best_20m.geojson",
    "results/gemini37-screen-2026-08-28/k10/verified_best_20m.geojson",
    "results/gemini37-screen-2026-08-28/swap37/verified_best_20m.geojson",
    "results/gemini38-screen-2026-09-04/armV/verified_best_20m.geojson",
    "results/gemini37-fourth-cell/gs-leg/verified_best_20m.geojson",
    "results/grid-2026-08-18/conditions-verified/g384_ov192/detections.geojson",
    "results/image-b-gs-2026-08-28/verified_best_20m.geojson",
    "results/image-b-gs-2026-08-28/high/verified_best_20m.geojson",
}
rows = json.loads((ROOT / BOARD / "tiering-input/run-analyses.json").read_text())
rows = rows["analyses"] if isinstance(rows, dict) else rows
row = next(r for r in rows if r["analysis_id"] == "gs-era2-verified-board-2026-09-10")
rc = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
paths, moved = {"results/run-conditions.json", "results/run-analyses.json"}, []
for cid in row["conditions_compared"]:
    run, label = cid.split("::")
    cond = next(c for c in rc[run]["conditions"] if c["label"] == label)
    ev = cond["eval_path"]
    paths.add(ev)
    doc = json.loads((ROOT / ev).read_text())
    args = (doc.get("_metadata") or doc.get("metadata"))["cli_args"]
    dets = args.get("detections") or []
    for p in dets:
        paths.add(p)
    if args.get("detections_dir"):
        paths.add(args["detections_dir"])
    for k in ("bounds", "ground_truth"):
        if args.get(k):
            paths.add(args[k])
    if any(p in REGENERATED for p in dets):
        moved.append((cid, ev, dets))
if "--moved" in sys.argv:
    for cid, ev, dets in moved:
        print(cid, ev, *dets, sep="\t")
else:
    for p in sorted(paths):
        print(p)
