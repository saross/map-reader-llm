"""Fan ``replay_cell.py`` out over a list of cells, one fresh interpreter per cell.

D57 (4) re-score, 2026-10-09 (Session 163). Each cell runs in its own Python
process (so no scorer state leaks between cells) with single-threaded numerical
libraries, ``--workers`` at a time. The driver writes its own pid file, one log
line per finished cell, and a final ``DONE`` or ``PARTIAL`` line, so a watcher
can wait on a terminal state rather than on a success string.

Cell list: a JSON file, a list of objects with ``eval`` (repository-relative)
and optional ``output_dir`` (an override; default the cell's own directory)
and ``add_require_clean`` (bool).

Resumable: a cell whose sidecar already records ``rc == 0`` is skipped.

Usage (on sapphire)::

    nohup ~/Code/map-reader-llm/.venv/bin/python run_replays.py \\
        --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --cells ~/scratch/d57-4-rescore-2026-10-09/out/phase2_cells.json \\
        --sidecars ~/scratch/d57-4-rescore-2026-10-09/out/sidecars \\
        --pidfile ~/scratch/d57-4-rescore-2026-10-09/out/phase2.pid \\
        --workers 18 > phase2.log 2>&1 < /dev/null &
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent

#: Pin every numerical library to one thread, so ``--workers`` bounds the cores.
THREAD_ENV = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
              "NUMEXPR_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def slug(rel: str) -> str:
    """A filesystem-safe name for a cell's sidecar and log."""
    return re.sub(r"[^A-Za-z0-9_.-]", "__", rel.removesuffix("/evaluation.json"))


def done(sidecar: Path) -> bool:
    """True when ``sidecar`` exists and records success."""
    try:
        return json.loads(sidecar.read_text()).get("rc") == 0
    except (OSError, ValueError):
        return False


def run_one(repo: Path, cell: dict[str, Any], sidecars: Path, logs: Path) -> tuple[str, int,
                                                                                   float]:
    """Replay one cell in a fresh interpreter; return (eval, returncode, seconds)."""
    rel = cell["eval"]
    side = sidecars / f"{slug(rel)}.json"
    cmd = [sys.executable, str(HERE / "replay_cell.py"), "--repo", str(repo),
           "--eval", rel, "--sidecar", str(side)]
    if cell.get("output_dir"):
        cmd += ["--output-dir", cell["output_dir"]]
    if cell.get("add_require_clean"):
        cmd.append("--add-require-clean")
    t0 = time.time()
    with (logs / f"{slug(rel)}.log").open("w") as fh:
        proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, env={**os.environ, **THREAD_ENV},
                              check=False)
    return rel, proc.returncode, time.time() - t0


def main() -> int:
    """Run every listed cell and report a terminal state."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--cells", type=Path, required=True)
    ap.add_argument("--sidecars", type=Path, required=True)
    ap.add_argument("--pidfile", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=18)
    args = ap.parse_args()
    if args.workers > 20:
        sys.exit("at most 20 workers on sapphire")
    args.pidfile.write_text(f"{os.getpid()}\n")
    repo = args.repo.expanduser().resolve()
    cells = json.loads(args.cells.read_text())
    sidecars = args.sidecars.expanduser().resolve()
    logs = sidecars.parent / (sidecars.name + "-logs")
    sidecars.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    todo = [c for c in cells if not done(sidecars / f"{slug(c['eval'])}.json")]
    print(f"START {len(cells)} cells, {len(cells) - len(todo)} already done, "
          f"{len(todo)} to run, {args.workers} workers", flush=True)
    t0 = time.time()
    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(run_one, repo, c, sidecars, logs) for c in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            rel, rc, secs = fut.result()
            if rc != 0:
                failed.append(rel)
            print(f"[{i}/{len(todo)}] rc={rc} {secs:.0f}s {rel}", flush=True)
    wall = time.time() - t0
    state = "DONE" if not failed else "PARTIAL"
    print(f"{state} {len(todo) - len(failed)}/{len(todo)} ok in {wall:.0f}s; "
          f"failed {len(failed)}: {failed[:20]}", flush=True)
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
