#!/usr/bin/env python3
"""Re-score registered conditions whose detection sets were rebuilt after a recovery.

Companion to ``rebuild_recovered_consensus.py`` (S150). For each named
condition the driver re-runs ``evaluate_detections.py`` at the condition's
ORIGINAL protocol — ground truth, bounds and buffers read from the committed
evaluation's own ``_metadata.cli_args`` — with the project's standard
bootstrap (BCa 10,000, seed 42), ``--mcc`` and ``--require-clean-inputs``,
into ``results/recovery-reeval-2026-09-08/<run>/<label>/``. The committed
evaluation is left untouched as the pre-recovery record (the E71 pattern,
``f6116cba0``); ``--register`` then re-points the row's ``eval_path`` at the
new home and notes the refresh, idempotently.

Usage::

    python scripts/recovery_reeval.py --run n1-outstanding-384 \\
        --label pro-image-high-t0-consensus-1of3 ...          # plan
    python scripts/recovery_reeval.py ... --write               # score
    python scripts/recovery_reeval.py ... --register            # re-point rows

Zero API. Minutes per cell (BCa 10,000 over 14 buffers) — run on sapphire.

Created: 2026-09-08 (Session 150)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUN_CONDITIONS = REPO / "results/run-conditions.json"
HOME = REPO / "results/recovery-reeval-2026-09-08"
STAMP = "recovery-reeval-2026-09-08"


def load_rows(run_id: str, labels: list[str]) -> list[dict]:
    rc = json.loads(RUN_CONDITIONS.read_text())["decomposition"]
    by = {c["label"]: c for c in rc[run_id]["conditions"]}
    missing = [x for x in labels if x not in by]
    if missing:
        sys.exit(f"{run_id}: not registered: {missing}")
    return [by[x] for x in labels]


def protocol_of(row: dict) -> dict:
    """Ground truth, bounds and buffers the committed evaluation used."""
    meta = json.loads((REPO / row["eval_path"]).read_text())["_metadata"]
    cli = meta.get("cli_args") or {}
    gt = cli.get("ground_truth")
    bounds = cli.get("bounds")
    buffers = cli.get("buffers")
    if not (gt and bounds and buffers):
        sys.exit(f"{row['label']}: committed eval records no cli_args protocol")
    # strip any frozen-replay prefix: the in-repo file is the protocol
    def inrepo(p: str) -> str:
        return p.split("/frozen/", 1)[1] if "/frozen/" in p else p
    return {"ground_truth": inrepo(gt), "bounds": inrepo(bounds), "buffers": buffers}


def command(run_id: str, row: dict) -> list[str]:
    proto = protocol_of(row)
    out = HOME / run_id / row["label"]
    return [sys.executable, str(REPO / "scripts/evaluate_detections.py"),
            "--detections", row["detections"],
            "--ground-truth", proto["ground_truth"], "--bounds", proto["bounds"],
            "--buffers", *map(str, proto["buffers"]),
            "--bootstrap", "10000", "--seed", "42", "--mcc", "--require-clean-inputs",
            "--workers", "4", "--label", f"{row['label']}-{STAMP}",
            "--output-dir", str(out.relative_to(REPO))]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--label", action="append", required=True)
    ap.add_argument("--write", action="store_true", help="run the scorer")
    ap.add_argument("--register", action="store_true", help="re-point eval_path rows")
    args = ap.parse_args(argv)
    rows = load_rows(args.run, args.label)
    for row in rows:
        cmd = command(args.run, row)
        out = HOME / args.run / row["label"]
        if (out / "evaluation.json").exists():
            print(f"  scored  {args.run}::{row['label']} (exists)")
        elif args.write:
            print(f"  scoring {args.run}::{row['label']} ...", flush=True)
            subprocess.run(cmd, cwd=REPO, check=True)
        else:
            print(f"  would score {args.run}::{row['label']}: {' '.join(cmd[2:8])} ...")
    if args.register:
        raw = RUN_CONDITIONS.read_text()
        trailing = "\n" if raw.endswith("\n") else ""
        rc = json.loads(raw)
        n = 0
        for c in rc["decomposition"][args.run]["conditions"]:
            if c["label"] in args.label:
                new = str((HOME / args.run / c["label"] / "evaluation.json").relative_to(REPO))
                if not (REPO / new).exists():
                    sys.exit(f"{c['label']}: {new} not scored yet")
                if c.get("eval_path") != new:
                    c["_pre_recovery_eval_path"] = c.get("eval_path")
                    c["eval_path"] = new
                    c["notes"] = ((c.get("notes") + " " if c.get("notes") else "")
                                  + f"Re-scored {STAMP} on the consensus rebuilt from the "
                                    "recovered passes (S150; the E71 pattern, f6116cba0); the "
                                    "previous evaluation stands as the pre-recovery record at "
                                    "_pre_recovery_eval_path.")
                    n += 1
        RUN_CONDITIONS.write_text(json.dumps(rc, indent=1, ensure_ascii=False) + trailing)
        print(f"re-pointed {n} row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
