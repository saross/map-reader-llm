#!/usr/bin/env python3
"""
kl_s9_cmds.py -- S164 restatement pass, K-ladder lane, part 1 step 4.

Purpose:
    Write one ``evaluate_detections.py`` command line per S9 mover, built from
    the cell's RECORDED ``_metadata.cli_args`` as committed at HEAD of the
    given clone (read with ``git show``, so a re-run after the cell was
    regenerated replays the same recipe). The argv is assembled exactly as
    ``reports/d57-4-rescore-2026-10-09-scripts/replay_cell.py:build_argv``
    does (every recorded key replayed; output to the cell's own directory),
    with one override: the recovery-fix copy, whose recorded detections and
    output directory are absolute scratch paths, reads its committed
    ``recovery-fix-2026-09-13/materialised/k5.geojson`` (SHA-256 equal to the
    recorded scratch file) and writes to its own directory.

Usage:
    python kl_s9_cmds.py <clone_root> > cmds.tsv     # cell<TAB>argv (JSON)

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
    f"{K}/tier-e/cells/grid-2026-08-18__g384-ov192-k1-verified-opmax",
    f"{K}/tier-e/cells/grid-2026-08-18__g384-ov192-k1-verified-p0_15-k1",
    f"{K}/tier-e/cells/grid-2026-08-18__g384-ov192-k3-verified-opmax",
    f"{K}/tier-e/cells/grid-2026-08-18__g384-ov192-k5-verified-opmax",
    f"{K}/phase2/cells/gemini37-screen-2026-08-28__g37-text-k1-verified-carried-p0_10-k1",
    f"{K}/phase2/cells/gemini37-screen-2026-08-28__g37-text-k1-verified-opmax",
    f"{K}/phase2/cells/gemini37-screen-2026-08-28__g37-text-k3-verified-opmax",
    f"{K}/recovery-fix-2026-09-13/reproduced-k5-evaluation",
]
RECOVERY = f"{K}/recovery-fix-2026-09-13/reproduced-k5-evaluation"
RECOVERY_DETECTIONS = f"{K}/recovery-fix-2026-09-13/materialised/k5.geojson"
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
    if cell == RECOVERY:
        dets = [RECOVERY_DETECTIONS]
    for d in dets:
        if Path(d).is_absolute():
            raise SystemExit(f"{cell}: absolute input {d}")
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
