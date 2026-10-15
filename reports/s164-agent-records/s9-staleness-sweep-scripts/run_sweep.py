#!/usr/bin/env python3
"""Replay a queue of committed evaluations on today's code, one fresh process per cell.

Purpose
-------
The S9 staleness sweep (S164, 2026-10-14; PI ruling D65 (2)) recomputes each
inventoried evaluation with the canonical scorer, ``scripts/evaluate_detections.py``,
exactly as its ``_metadata.cli_args`` record, by way of the D57 (4) wrapper
``reports/d57-4-rescore-2026-10-09-scripts/replay_cell.py`` (which runs the
scorer in process and keeps a sidecar of the unrounded points). Every output
goes under ``--out``; the repository's own cell directories are never written.

Safety (``docs/agent-guidance.md``, Compute Location):

* at most ``--workers`` cells at a time (the brief allows eight);
* ``MAP_READER_VERIFY_DIRS=fixed`` and one numerical thread per process;
* a kernel tripwire: ``journalctl -k -b`` is read for ``Bad page state``
  before the first cell and every ``--check-every`` completions; any increase
  over the starting count writes ``STOP`` and launches nothing further;
* a ``STOP`` file in ``--out`` halts new launches;
* the runner writes its own pid to ``--out/run.pid`` and a terminal line to
  ``--out/progress.log`` (``DONE``, ``STOPPED``, or ``TRIPWIRE``).

Usage (on sapphire, detached, nothing after the ``&``)::

    nohup ~/Code/map-reader-llm/.venv/bin/python run_sweep.py --repo <wt> \\
        --queue <queue.txt> --out <root>/runA --workers 8 \\
        > <root>/runA.log 2>&1 < /dev/null &

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPLAY = "reports/d57-4-rescore-2026-10-09-scripts/replay_cell.py"
POINTS = "reports/s164-agent-records/s9-staleness-sweep-scripts/points_cell.py"


def bad_pages() -> int:
    """Return the current boot's count of kernel ``Bad page state`` reports."""
    res = subprocess.run(["journalctl", "-k", "-b"], capture_output=True, text=True,
                         check=False)
    return sum("Bad page state" in ln for ln in res.stdout.splitlines())


def slug(rel: str) -> str:
    """A file-name-safe key for a repository-relative evaluation path."""
    return rel.replace("/", "__")


def replay(repo: Path, out: Path, rel: str, python: str,
           mode: str = "full") -> tuple[str, int, float]:
    """Replay one cell into ``out/cells/<cell dir>``; return (path, rc, seconds).

    ``mode`` ``full`` runs ``replay_cell.py`` (the recorded recipe, bootstrap
    included); ``points`` runs ``points_cell.py`` (the same recipe with a
    reduced bootstrap, for point estimates only).
    """
    t0 = time.time()
    cell_dir = out / "cells" / Path(rel).parent
    side = out / "sidecars" / f"{slug(rel)}.json"
    log = out / "logs" / f"{slug(rel)}.log"
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1",
               MAP_READER_VERIFY_DIRS="fixed")
    with log.open("w") as fh:
        script = REPLAY if mode == "full" else POINTS
        rc = subprocess.run([python, str(repo / script), "--repo", str(repo), "--eval", rel,
                             "--sidecar", str(side), "--output-dir", str(cell_dir)],
                            stdout=fh, stderr=subprocess.STDOUT, env=env, cwd=str(repo),
                            check=False).returncode
    return rel, rc, time.time() - t0


def main() -> int:
    """Run the queue and write the progress log."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--queue", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--check-every", type=int, default=25)
    ap.add_argument("--mode", choices=("full", "points"), default="full")
    args = ap.parse_args()
    if args.workers > 8:
        raise SystemExit("at most 8 workers (brief)")
    repo = args.repo.expanduser().resolve()
    out = args.out.expanduser().resolve()
    for sub in ("cells", "sidecars", "logs"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    (out / "run.pid").write_text(f"{os.getpid()}\n")
    queue = [ln.strip() for ln in args.queue.read_text().splitlines() if ln.strip()]
    prog = (out / "progress.log").open("a", buffering=1)
    start_bp = bad_pages()
    prog.write(f"START {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
               f"n={len(queue)} workers={args.workers} mode={args.mode} "
               f"bad_pages={start_bp}\n")
    done = failed = 0
    halted = None
    pending = list(queue)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = set()

        def launch() -> None:
            """Fill the pool up to the worker count unless halted."""
            while pending and len(futs) < args.workers and halted is None:
                if (out / "STOP").exists():
                    return
                futs.add(pool.submit(replay, repo, out, pending.pop(0), sys.executable,
                                     args.mode))

        launch()
        while futs:
            fut = next(as_completed(futs))
            futs.discard(fut)
            rel, rc, secs = fut.result()
            done += 1
            failed += rc != 0
            prog.write(f"{'ok' if rc == 0 else 'FAIL'} rc={rc} {secs:.1f}s {rel}\n")
            if done % args.check_every == 0:
                bp = bad_pages()
                if bp > start_bp:
                    halted = "TRIPWIRE"
                    (out / "STOP").write_text(f"bad pages {start_bp} -> {bp}\n")
            if (out / "STOP").exists() and halted is None:
                halted = "STOPPED"
            launch()
    end_bp = bad_pages()
    status = halted or "DONE"
    prog.write(f"{status} {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
               f"{done}/{len(queue)} ran; failed {failed}; not run {len(pending)}; "
               f"bad_pages {start_bp} -> {end_bp}\n")
    return 0 if status == "DONE" and failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
