#!/usr/bin/env python3
"""Replay one committed evaluation for its POINTS only (S9 staleness sweep, S164).

Purpose
-------
The full replay (``replay_cell.py``, D57 (4)) re-runs a cell's recorded
bootstrap, which dominates its cost (14 buffers × 10,000 BCa resamples).
Point estimates (F1, precision, recall, counts, the tile confusion and its
MCC point) do not depend on the bootstrap. This wrapper therefore replays the
cell with the same scorer and the same recorded recipe in every other
respect, but with ``--bootstrap`` replaced by ``--bootstrap-n`` (default 50),
so every live evaluation can be scanned for point moves cheaply. Its
intervals are NOT comparable and ``compare.py --points-only`` ignores them.

On the 55-map frame the bootstrap count is not the cost: a BCa interval
needs a jackknife over every tile (8,541 leave-one-out evaluations per
metric and buffer), and the per-tile table behind it is rebuilt for every
buffer. With ``--stub-intervals`` (the default) two routines are replaced in
this process: the scorer's ``bootstrap_ci`` (per-buffer F1, P and R
intervals) by a stub returning empty interval blocks of the same shape, and
the library's ``_bca_ci_from_indices`` (which the tile-MCC interval uses) by
a stub that evaluates the statistic once on the full tile set (method
``points-only-stub``). Point estimates are computed before, and independently
of, both (``calculate_f1_internal``, ``calculate_tile_classification``), so
they are unaffected; the stub was checked against unstubbed replays.

It reuses ``replay_cell.build_argv``, ``Spy`` and ``mean_point`` unchanged
(``reports/d57-4-rescore-2026-10-09-scripts/``), so the argv and the
unrounded-point sidecar are built exactly as in the full replay.

Usage (one fresh interpreter per cell)::

    OMP_NUM_THREADS=1 python points_cell.py --repo <wt> --eval <rel> \\
        --sidecar <out>/sidecars/<slug>.json --output-dir <out>/cells/<cell dir>

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any


def _stub_ci(indices: Any, statistic: Any, n_iterations: int = 1000,
             random_seed: int | None = None, confidence_level: float = 0.95,
             skip_undefined: bool = False) -> dict[str, Any]:
    """Stand-in for ``_bca_ci_from_indices``: the statistic once, no resampling."""
    import numpy as np  # noqa: PLC0415

    value = float(statistic(np.asarray(indices)))
    if skip_undefined and not np.isfinite(value):
        return {"mean": None, "ci_lower": None, "ci_upper": None, "method": "undefined",
                "n_valid": 0, "bootstrap_distribution": np.array([])}
    return {"mean": value, "ci_lower": value, "ci_upper": value,
            "method": "points-only-stub", "n_valid": 1,
            "bootstrap_distribution": np.array([value])}


def _stub_bootstrap_ci(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Stand-in for ``bootstrap_ci``: no per-tile table, no resampling.

    ``evaluate_single_run`` reads only ``ci[metric]`` bounds and method and
    ``ci.get("coverage", {})`` from this result; it takes its F1, precision
    and recall from ``calculate_f1_internal``, called before this.
    """
    blk = {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "method": "points-only-stub"}
    return {"f1": dict(blk), "precision": dict(blk), "recall": dict(blk), "coverage": {}}


def stub_intervals(ed: Any) -> list[str]:
    """Replace the interval routines: the per-buffer one in the scorer, the BCa helper in
    every loaded copy of the metrics library."""
    ed.bootstrap_ci = _stub_bootstrap_ci
    patched = ["scripts.evaluate_detections.bootstrap_ci"]
    for name, mod in list(sys.modules.items()):
        if name.endswith("lib_advanced_metrics") and hasattr(mod, "_bca_ci_from_indices"):
            mod._bca_ci_from_indices = _stub_ci
            patched.append(name)
    if len(patched) < 2:
        raise RuntimeError("lib_advanced_metrics not loaded; nothing to stub")
    return patched


def main() -> int:
    """Replay one cell with a reduced bootstrap and write its sidecar."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--eval", required=True)
    ap.add_argument("--sidecar", type=Path, required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--bootstrap-n", type=int, default=50)
    ap.add_argument("--no-stub-intervals", dest="stub", action="store_false",
                    help="Run the real interval routine (slow on 55-map frames).")
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    sys.path.insert(0, str(repo / "reports/d57-4-rescore-2026-10-09-scripts"))
    import d57_common as dc  # noqa: PLC0415
    import replay_cell as rc_mod  # noqa: PLC0415

    t0 = time.time()
    side: dict[str, Any] = {"eval": args.eval, "repo": str(repo), "mode": "points-only",
                            "bootstrap_n": args.bootstrap_n, "stub_intervals": args.stub}
    try:
        ev = dc.committed_eval(repo, args.eval, "HEAD")
        if ev is None:
            raise FileNotFoundError(args.eval)
        cli = dict((ev.get("_metadata") or {}).get("cli_args") or {})
        side["recorded_bootstrap"] = cli.get("bootstrap")
        cli["bootstrap"] = args.bootstrap_n
        argv, notes = rc_mod.build_argv(repo, cli, args.output_dir, False)
        side.update({"argv": argv, "notes": notes})
        os.chdir(repo)
        sys.path.insert(0, str(repo))
        logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
        import scripts.evaluate_detections as ed  # noqa: PLC0415

        if not Path(ed.__file__).resolve().is_relative_to(repo):
            raise RuntimeError(f"scorer imported from {ed.__file__}, not {repo}")
        if args.stub:
            side["stubbed_modules"] = stub_intervals(ed)
        spy = rc_mod.Spy()
        ed.evaluate_single_run = spy.wrap_run(ed.evaluate_single_run)
        ed.calculate_f1_internal = spy.wrap_f1(ed.calculate_f1_internal)
        ed.calculate_tile_classification = spy.wrap_tc(ed.calculate_tile_classification)
        sys.argv = ["scripts/evaluate_detections.py", *argv]
        try:
            rc = ed.main()
        except SystemExit as exc:
            rc = exc.code if isinstance(exc.code, int) else 1
        side["rc"] = rc
        side["runs"] = spy.runs
        side["point"] = rc_mod.mean_point(spy.runs, [int(b) for b in cli.get("buffers") or []])
    except Exception as exc:  # noqa: BLE001 - recorded; the rc says so
        side["rc"] = 99
        side["error"] = f"{type(exc).__name__}: {exc}"
    side["wall_seconds"] = round(time.time() - t0, 2)
    args.sidecar.parent.mkdir(parents=True, exist_ok=True)
    args.sidecar.write_text(json.dumps(side, indent=1, default=str) + "\n")
    return 0 if side.get("rc") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
