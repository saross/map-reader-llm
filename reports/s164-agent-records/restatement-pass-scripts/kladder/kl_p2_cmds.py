#!/usr/bin/env python3
"""
kl_p2_cmds.py -- the recorded evaluation commands of the five board-frame cells.

Purpose:
    S164 restatement pass, K-ladder lane, part 2. Prints one line per cell,
    ``cell<TAB>argv`` (JSON), for the four GS stride A board-frame cells and
    tier E's K = 10 board-frame cell, each built from the cell's RECORDED
    ``_metadata.cli_args`` at HEAD (read with ``git show``) exactly as
    ``reports/d57-4-rescore-2026-10-09-scripts/replay_cell.py:build_argv``
    builds an argv (every recorded key replayed; output to the cell's own
    directory). The same builder as part 1's ``kl_s9_cmds.py``.

Usage:
    python kl_p2_cmds.py <clone_root>

Author: Claude (Opus 5.5) for Shawn Ross, S164 restatement pass, 2026-10-15.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
K = "results/k-ladder-2026-09-12"
CELLS = [
    f"{K}/board-frame/stride-phaseb__g384-ov128-ladder-n1",
    f"{K}/board-frame/stride-phaseb__g384-ov128-ladder-n3",
    f"{K}/board-frame/stride-phaseb__g384-ov128-ladder-n5",
    f"{K}/board-frame/stride-phaseb__g384-ov128-k10",
    f"{K}/tier-e/cells/grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10-boardframe",
]
KNOWN = {"detections", "detections_dir", "batch", "glob", "buffers", "ground_truth",
         "bounds", "bootstrap", "seed", "output_dir", "label", "mcc", "workers",
         "tile_join", "require_clean_inputs"}


def recorded(cell: str) -> dict:
    """The cell's recorded cli_args, read from HEAD."""
    text = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{cell}/evaluation.json"],
                          capture_output=True, text=True, check=True).stdout
    return json.loads(text)["_metadata"]["cli_args"]


def argv_for(cell: str, cli: dict) -> list[str]:
    """Assemble the argv as replay_cell.build_argv does, output to the cell."""
    unknown = set(cli) - KNOWN
    if unknown or cli.get("batch") or not cli.get("detections"):
        raise SystemExit(f"{cell}: unexpected recipe {sorted(unknown)}")
    dets = cli["detections"]
    dets = [dets] if isinstance(dets, str) else list(dets)
    if any(Path(d).is_absolute() for d in dets):
        raise SystemExit(f"{cell}: absolute input in {dets}")
    argv = ["--detections", *dets, "--buffers", *[str(int(b)) for b in cli["buffers"]],
            "--ground-truth", cli["ground_truth"], "--bounds", cli["bounds"],
            "--bootstrap", str(int(cli["bootstrap"])), "--seed", str(int(cli["seed"])),
            "--output-dir", cell]
    if cli.get("label") is not None:
        argv += ["--label", str(cli["label"])]
    if cli.get("mcc"):
        argv.append("--mcc")
    if cli.get("tile_join"):
        argv += ["--tile-join", str(cli["tile_join"])]
    if cli.get("require_clean_inputs"):
        argv.append("--require-clean-inputs")
    if cli.get("workers") is not None:
        argv += ["--workers", str(int(cli["workers"]))]
    return argv


for c in CELLS:
    print(c + "\t" + json.dumps(argv_for(c, recorded(c))))
