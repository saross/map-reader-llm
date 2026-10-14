#!/usr/bin/env python3
"""Replay the 55-map corrected-F1 engine behind each adapter evaluation (S9 sweep, S164).

Purpose
-------
Twenty-four committed ``evaluation.json`` files on the 55-map frame carry no
``cli_args``: each is a deterministic transform ("adapter") of a
``summary.json`` written by ``scripts/compute_corrected_f1_multi_buffer.py``
(the extended-GT Hungarian engine). That engine reads the shared sheet scope
(``lib_advanced_metrics.iter_sheet_scopes``), which the D50 commit
``f93935c18`` changed, and the D50 measurement of 2026-10-07/08 marked these
cells "diagnostics-only (non-direct scorer)" and did not score them. This
driver re-runs the engine from each summary's recorded metadata and compares
the per-buffer counts and points with the committed summary.

Recipe (from the committed ``summary.json``):

* inputs: ``metadata.input_paths`` (absolute paths into a checkout, re-rooted
  at ``--repo``); ``extension_csv`` selects the standardised mode, the two
  review CSVs the legacy ring-gated mode;
* buffers: the ``R_m`` of every ``results`` row; ``--compute-mcc`` when any
  row carries ``tile_classification``; seed ``metadata.seed``;
* bootstrap: ``--n-bootstrap`` (default 50: POINTS ONLY; counts, P, R, F1
  and the MCC point do not depend on it; intervals are not compared).

``--code`` names the tree whose ``scripts/`` runs (default ``--repo``), so
the same recipe can be replayed under an older scorer for attribution; the
inputs are always read from ``--repo``.

Usage::

    python engine_replay.py --repo <wt> --cells <adapters.txt> --out <root> \\
        [--code <archive of an older commit>] [--workers 4] [--dedup-tolerance-m 0]

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ENGINE = "scripts/compute_corrected_f1_multi_buffer.py"
POINT_KEYS = ("TP", "FP", "FN", "precision", "recall", "F1", "n_ref_extended",
              "n_reviewer_promoted_at_R", "n_ref_student_only")
TILE_KEYS = ("tp", "tn", "fp", "fn", "mcc", "sensitivity", "specificity")


def rerooted(repo: Path, path: str) -> str:
    """Re-root an absolute checkout path at ``repo`` (relative paths too)."""
    marker = "/map-reader-llm/"
    rel = path.split(marker, 1)[1] if marker in path else path
    return str(repo / rel)


def source_summary(repo: Path, eval_rel: str) -> str:
    """The engine summary an adapter evaluation was transformed from."""
    meta = json.loads((repo / eval_rel).read_text()).get("_metadata") or {}
    src = meta.get("source_summary") or meta.get("source")
    if not src:
        raise ValueError(f"{eval_rel}: no source summary recorded")
    return src


def build_argv(repo: Path, summary: dict[str, Any], out_dir: Path,
               n_boot: int) -> list[str]:
    """Build the engine argv from a committed summary's metadata and results."""
    md = summary["metadata"]
    ip = md["input_paths"]
    argv = ["--verified-detections", rerooted(repo, ip["detections"]),
            "--student-gt", rerooted(repo, ip["student_gt"]),
            "--bounds", rerooted(repo, ip["bounds"])]
    if ip.get("extension_csv"):
        argv += ["--extension-csv", rerooted(repo, ip["extension_csv"])]
    else:
        argv += ["--review-yesterday", rerooted(repo, ip["review_yesterday"]),
                 "--review-today", rerooted(repo, ip["review_today"])]
    res = summary["results"]
    argv += ["--buffers", *[str(int(r["R_m"])) for r in res]]
    argv += ["--n-bootstrap", str(n_boot), "--seed", str(int(md.get("seed", 42)))]
    if any("tile_classification" in r for r in res):
        argv.append("--compute-mcc")
    argv += ["--output-dir", str(out_dir)]
    return argv


def points(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Per-buffer point block of an engine summary."""
    out: dict[str, dict[str, Any]] = {}
    for r in summary.get("results") or []:
        rec = {k: r.get(k) for k in POINT_KEYS}
        tc = r.get("tile_classification") or {}
        rec.update({f"tile_{k}": tc.get(k) for k in TILE_KEYS})
        out[str(r["R_m"])] = rec
    return out


def run_one(repo: Path, code: Path, out: Path, eval_rel: str,
            n_boot: int, extra: list[str] | None = None) -> dict[str, Any]:
    """Replay one adapter's engine run and compare its points."""
    t0 = time.time()
    rec: dict[str, Any] = {"eval": eval_rel}
    try:
        src = source_summary(repo, eval_rel)
        committed = json.loads((repo / src).read_text())
        out_dir = out / "cells" / Path(src).parent
        out_dir.mkdir(parents=True, exist_ok=True)
        argv = build_argv(repo, committed, out_dir, n_boot) + list(extra or [])
        env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                   MKL_NUM_THREADS="1", MAP_READER_VERIFY_DIRS="fixed")
        log = out / "logs" / (eval_rel.replace("/", "__") + ".log")
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("w") as fh:
            rc = subprocess.run([sys.executable, str(code / ENGINE), *argv], cwd=str(repo),
                                stdout=fh, stderr=subprocess.STDOUT, env=env,
                                check=False).returncode
        rec.update({"source_summary": src, "argv": argv, "rc": rc,
                    "committed_engine_commit": committed["metadata"].get("git_commit")})
        if rc == 0:
            replay = json.loads((out_dir / "summary.json").read_text())
            pc, pr = points(committed), points(replay)
            diffs = {b: {k: [pc[b].get(k), (pr.get(b) or {}).get(k)] for k in pc[b]
                         if pc[b].get(k) != (pr.get(b) or {}).get(k)} for b in pc}
            diffs = {b: d for b, d in diffs.items() if d}
            rec.update({"identical_points": not diffs, "diffs": diffs,
                        "committed_20": pc.get("20"), "replay_20": pr.get("20"),
                        "committed_50": pc.get("50"), "replay_50": pr.get("50")})
    except Exception as exc:  # noqa: BLE001 - recorded
        rec.update({"rc": 99, "error": f"{type(exc).__name__}: {exc}"})
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def main() -> int:
    """Replay every listed adapter and write ``<out>/engine.json``."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--cells", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--code", type=Path, default=None)
    ap.add_argument("--n-bootstrap", type=int, default=50)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dedup-tolerance-m", type=float, default=None,
                    help="Pass --dedup-tolerance-m to the engine (0 reproduces the "
                         "pre-de-duplication engine; attribution only).")
    args = ap.parse_args()
    if args.workers > 8:
        raise SystemExit("at most 8 workers (brief)")
    args.extra = ([] if args.dedup_tolerance_m is None
                  else ["--dedup-tolerance-m", str(args.dedup_tolerance_m)])
    repo = args.repo.expanduser().resolve()
    code = (args.code or args.repo).expanduser().resolve()
    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.pid").write_text(f"{os.getpid()}\n")
    cells = [ln.strip() for ln in args.cells.read_text().splitlines() if ln.strip()]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        recs = list(pool.map(lambda c: run_one(repo, code, out, c, args.n_bootstrap,
                                               args.extra), cells))
    doc = {"repo": str(repo), "code": str(code), "n_bootstrap": args.n_bootstrap,
           "extra": args.extra,
           "n": len(recs), "n_identical": sum(bool(r.get("identical_points")) for r in recs),
           "n_failed": sum(r.get("rc") != 0 for r in recs), "cells": recs}
    (out / "engine.json").write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    (out / "progress.log").write_text(f"DONE {doc['n']} ran; identical {doc['n_identical']}; "
                                      f"failed {doc['n_failed']}\n")
    print(f"{doc['n']} ran; identical {doc['n_identical']}; failed {doc['n_failed']}")
    return 0 if doc["n_failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
