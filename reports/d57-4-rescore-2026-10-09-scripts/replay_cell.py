"""Replay one committed evaluation cell exactly as recorded, capturing full-precision points.

D57 (4) re-score, 2026-10-09 (Session 163). Plan card:
``planning/d57-4-rescore-plan-2026-10-09.md`` § 3.1.

``evaluate_detections.py`` writes F1, precision and recall rounded to four
decimals, but the plan's inverted point gate compares every regenerated value
with the expected (``rescore_b.jsonl``) value to 1e-9. This wrapper therefore
runs the scorer IN PROCESS, with the cell's recorded ``_metadata.cli_args`` as
its argv, and installs passive spies on the three names the scorer's point
estimates flow through (``evaluate_single_run``, ``calculate_f1_internal`` and
``calculate_tile_classification`` in the ``evaluate_detections`` namespace).
The spies return exactly what the wrapped functions return; they only record
the unrounded values, which go to a sidecar JSON in scratch, never into the
repository. The files the scorer writes (``evaluation.json``, ``.csv``,
``.md``) are the scorer's own output, unchanged.

The recipe is read from ``HEAD`` (``git show``), never from the working tree,
so a re-run after the cell has been regenerated replays the same recipe.

Recipe rules (plan § 3.1):

* every recorded ``cli_args`` key is replayed as recorded (bootstrap, seed,
  buffers, label, MCC, tile join, workers);
* the output directory is the cell's own directory (or ``--output-dir``);
* ``--require-clean-inputs`` is added when ``--add-require-clean`` is given
  (every group except the null-exemplar twins, whose inputs are gitignored),
  and kept wherever the cell recorded it;
* recorded absolute paths into any checkout are re-rooted at ``--repo`` (see
  ``d57_common.to_repo_relative``), so nothing reads the shared checkout.

Usage (on sapphire; one fresh interpreter per cell)::

    OMP_NUM_THREADS=1 ~/Code/map-reader-llm/.venv/bin/python replay_cell.py \\
        --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --eval results/h8-v2/…/evaluation.json \\
        --sidecar ~/scratch/d57-4-rescore-2026-10-09/out/sidecars/<slug>.json \\
        --add-require-clean
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d57_common as dc  # noqa: E402


def build_argv(repo: Path, cli: dict[str, Any], output_dir: str,
               add_require_clean: bool) -> tuple[list[str], list[str]]:
    """Turn a recorded ``cli_args`` block into an ``evaluate_detections.py`` argv.

    Args:
        repo: Repository root (the replay's working directory).
        cli: The recorded ``_metadata.cli_args``.
        output_dir: Where the scorer writes.
        add_require_clean: Add ``--require-clean-inputs``.

    Returns:
        ``(argv, notes)``; ``argv`` excludes the program name.

    Raises:
        ValueError: on a batch-mode recipe or a key this wrapper does not know.
    """
    known = {"detections", "detections_dir", "batch", "glob", "buffers", "ground_truth",
             "bounds", "bootstrap", "seed", "output_dir", "label", "mcc", "workers",
             "tile_join", "require_clean_inputs"}
    unknown = set(cli) - known
    if unknown:
        raise ValueError(f"unknown cli_args keys: {sorted(unknown)}")
    if cli.get("batch"):
        raise ValueError("batch-mode recipe")
    notes: list[str] = []
    argv: list[str] = []
    if cli.get("detections"):
        dets = cli["detections"]
        dets = [dets] if isinstance(dets, str) else list(dets)
        paths = []
        for d in dets:
            rel, note = dc.to_repo_relative(repo, str(d))
            paths.append(rel)
            if note:
                notes.append(note)
        argv += ["--detections", *paths]
    elif cli.get("detections_dir"):
        rel, note = dc.to_repo_relative(repo, str(cli["detections_dir"]))
        if note:
            notes.append(note)
        argv += ["--detections-dir", rel]
        if cli.get("glob"):
            argv += ["--glob", str(cli["glob"])]
    else:
        raise ValueError("no detections recorded")
    if cli.get("buffers"):
        argv += ["--buffers", *[str(int(b)) for b in cli["buffers"]]]
    for key, flag in (("ground_truth", "--ground-truth"), ("bounds", "--bounds")):
        if cli.get(key):
            rel, note = dc.to_repo_relative(repo, str(cli[key]))
            if note:
                notes.append(note)
            argv += [flag, rel]
    if cli.get("bootstrap") is not None:
        argv += ["--bootstrap", str(int(cli["bootstrap"]))]
    if cli.get("seed") is not None:
        argv += ["--seed", str(int(cli["seed"]))]
    argv += ["--output-dir", output_dir]
    if cli.get("label") is not None:
        argv += ["--label", str(cli["label"])]
    if cli.get("mcc"):
        argv.append("--mcc")
    if cli.get("tile_join"):
        argv += ["--tile-join", str(cli["tile_join"])]
    if cli.get("require_clean_inputs") or add_require_clean:
        argv.append("--require-clean-inputs")
        if not cli.get("require_clean_inputs"):
            notes.append("--require-clean-inputs added (plan § 3.1)")
    if cli.get("workers") is not None:
        argv += ["--workers", str(int(cli["workers"]))]
    return argv, notes


class Spy:
    """Record the scorer's unrounded point estimates without altering them."""

    def __init__(self) -> None:
        """Start with no runs."""
        self.runs: list[dict[str, Any]] = []

    def wrap_run(self, fn: Any) -> Any:
        """Wrap ``evaluate_single_run``: open a run record per call."""
        def wrapped(gdf_det: Any, *args: Any, **kwargs: Any) -> Any:
            """Open a run record, then score the run unchanged."""
            self.runs.append({"n_det": int(len(gdf_det)), "label": kwargs.get("label"),
                              "per_buffer": {}, "f1_calls": 0, "mcc": None,
                              "mcc_refused": None, "mcc_calls": 0})
            return fn(gdf_det, *args, **kwargs)
        return wrapped

    def wrap_f1(self, fn: Any) -> Any:
        """Wrap ``calculate_f1_internal``: record (P, R, F1) per buffer."""
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            """Score one buffer unchanged; record its unrounded (P, R, F1)."""
            res = fn(*args, **kwargs)
            buf = kwargs.get("buffer_metres", args[3] if len(args) > 3 else None)
            run = self.runs[-1]
            p, r, f = res
            new = {"f1": float(f), "precision": float(p), "recall": float(r)}
            key = str(int(buf))
            prev = run["per_buffer"].get(key)
            if prev is not None and prev != new:
                run.setdefault("inconsistent", []).append(key)
            run["per_buffer"][key] = new
            run["f1_calls"] += 1
            return res
        return wrapped

    def wrap_tc(self, fn: Any) -> Any:
        """Wrap ``calculate_tile_classification``: record MCC or its refusal."""
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            """Classify tiles unchanged; record the MCC or its refusal."""
            res = fn(*args, **kwargs)
            run = self.runs[-1]
            run["mcc_calls"] += 1
            if "error" in res:
                run["mcc_refused"] = str(res.get("reason"))
            else:
                run["mcc"] = None if res.get("mcc") is None else float(res["mcc"])
            return res
        return wrapped


def mean_point(runs: list[dict[str, Any]], buffers: list[int]) -> dict[str, Any]:
    """Full-precision cell point: one run's values, or the per-run mean.

    Mirrors ``meas_lib.mean_runs`` (the expected values' own rule): F1, P and R
    are arithmetic means of the unrounded per-run values; MCC is the mean of
    the defined passes; the first refusal is carried.

    Args:
        runs: Spy run records.
        buffers: The recipe's buffers (an empty run scores zeros at each).

    Returns:
        ``{"per_buffer", "mcc", "mcc_refused"}``.
    """
    blocks = []
    for run in runs:
        pb = run["per_buffer"]
        if run["n_det"] == 0:
            pb = {str(b): {"f1": 0.0, "precision": 0.0, "recall": 0.0} for b in buffers}
        blocks.append({"per_buffer": pb, "mcc": run["mcc"], "mcc_refused": run["mcc_refused"]})
    if len(blocks) == 1:
        return blocks[0]
    keys = list(blocks[0]["per_buffer"])
    out: dict[str, Any] = {"per_buffer": {
        b: {m: sum(x["per_buffer"][b][m] for x in blocks) / len(blocks) for m in dc.METRICS}
        for b in keys}}
    defined = [x["mcc"] for x in blocks if x["mcc"] is not None]
    out["mcc"] = sum(defined) / len(defined) if defined else None
    out["mcc_refused"] = next((x["mcc_refused"] for x in blocks if x["mcc_refused"]), None)
    return out


def main() -> int:
    """Replay one cell and write its sidecar."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--eval", required=True, help="Repository-relative evaluation.json.")
    ap.add_argument("--sidecar", type=Path, required=True)
    ap.add_argument("--output-dir", default=None,
                    help="Override the output directory (default: the cell's own).")
    ap.add_argument("--add-require-clean", action="store_true")
    ap.add_argument("--rev", default="HEAD", help="Revision to read the recipe from.")
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    t0 = time.time()
    side: dict[str, Any] = {"eval": args.eval, "repo": str(repo), "rev": args.rev}
    try:
        ev = dc.committed_eval(repo, args.eval, args.rev)
        if ev is None:
            raise FileNotFoundError(f"{args.rev}:{args.eval}")
        cli = (ev.get("_metadata") or {}).get("cli_args") or {}
        cell_dir = str(Path(args.eval).parent)
        output_dir = args.output_dir or cell_dir
        argv, notes = build_argv(repo, cli, output_dir, args.add_require_clean)
        side.update({"argv": argv, "notes": notes,
                     "recorded_output_dir": cli.get("output_dir"),
                     "recorded_output_dir_is_cell_dir": cli.get("output_dir") == cell_dir})
        os.chdir(repo)
        sys.path.insert(0, str(repo))
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
        import scripts.evaluate_detections as ed  # noqa: PLC0415

        if not Path(ed.__file__).resolve().is_relative_to(repo):
            raise RuntimeError(f"scorer imported from {ed.__file__}, not {repo}")
        side["scorer_file"] = str(Path(ed.__file__).resolve())
        side["scope_count_keys"] = list(ed._DETECTION_SCOPE_COUNTS)
        spy = Spy()
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
        side["point"] = mean_point(spy.runs, [int(b) for b in cli.get("buffers") or []])
    except Exception as exc:  # noqa: BLE001 - recorded, and the rc says so
        side["rc"] = 99
        side["error"] = f"{type(exc).__name__}: {exc}"
    side["wall_seconds"] = round(time.time() - t0, 2)
    args.sidecar.parent.mkdir(parents=True, exist_ok=True)
    args.sidecar.write_text(json.dumps(side, indent=1, default=str) + "\n")
    return 0 if side.get("rc") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
