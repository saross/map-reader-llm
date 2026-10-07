"""Re-score every committed ``evaluation.json`` with and without a geometric detection scope.

Frames blast-radius measurement (PI ruling 2026-10-07: "measure the blast radius first, then
decide"), Session 163. Read-only: reads the repository checkout, writes only to ``--out``.

For each committed ``*evaluation.json`` (``git ls-files``) whose metadata names its
detections, bounds and ground truth, the script:

1. loads the frame, the references and the detections exactly as
   ``scripts/evaluate_detections.py`` does (including the ``source_tile`` spatial join when
   the column is absent);
2. counts the detections the name-prefix scope books but the reference-side geometric rule
   would drop (``blast_lib.geometric_detection_scope``), plus null-``source_tile`` drops;
3. scores OFF (the project's ``calculate_f1_internal`` / ``calculate_tile_classification``
   unchanged) at the selected buffers, and ON (same functions on the geometrically scoped
   detections) wherever any detection is dropped (when none is, ON is identical to OFF by
   construction: the scorer receives the same rows);
4. records the committed values beside both, for the reproduction gate.

Cells scored by the corrected-F1 engine (55-map extended ground truth) are not re-scored
here (their references are built per buffer); they get the drop diagnostics only, and are
re-scored separately when any detection drops.

Usage::

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python rescore_evaluations.py \
        --repo ~/Code/map-reader-llm --out out/evaluations.jsonl --workers 20
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blast_lib as bl  # noqa: E402

#: Buffers scored for the reproduction gate on cells with no out-of-frame detection.
GATE_BUFFERS = (20, 50)

#: (old prefix, new prefix) pairs applied to recorded detection paths; set by ``--remap``.
#: Used to point the null-exemplar cells at rebuilt copies of their gitignored inputs.
REMAP: list[tuple[str, str]] = []

#: Scorer labels whose numbers ``calculate_f1_internal`` reproduces directly.
DIRECT_SCRIPTS = {"scripts/evaluate_detections.py"}


def family_of(bounds: str, eval_path: str) -> str:
    """Name the frame family of a cell from its bounds path.

    Args:
        bounds: Repository-relative bounds path recorded by the evaluation.
        eval_path: The evaluation's own path (archive cells are tagged).

    Returns:
        A short family label.
    """
    table = {
        "inputs/vectors/bounds/384/full_evaluation_bounds.geojson":
            "GS-487 Era-2 (full_evaluation)",
        "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson": "GS-487 board (era2_b)",
        "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson": "GS-487 grid-common",
        "inputs/vectors/bounds/384/h10_test_bounds.geojson": "GS-327 Era-3 (h10_test)",
        "inputs/vectors/bounds/full_evaluation_bounds.geojson": "GS-340 Era-1 (512 px)",
        "inputs/vectors/bounds/256/full_evaluation_bounds.geojson": "GS-1032 (256 px)",
        "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson": "55-map",
    }
    fam = table.get(bounds)
    if fam is None and "outputs/h13/scoring/bounds/" in bounds:
        fam = "GS h13 (" + Path(bounds).stem.replace("_bounds", "") + ")"
    if fam is None:
        fam = "other:" + bounds
    if eval_path.startswith("archive/"):
        fam = "[archive] " + fam
    return fam


def norm(p: str | None) -> str | None:
    """Map a frozen-snapshot path back to its repository-relative path."""
    if p is None:
        return None
    return p.split("/frozen/", 1)[1] if "/frozen/" in p else p


def committed_values(summary: dict[str, Any]) -> tuple[dict[int, dict[str, float]], Any]:
    """Pull committed per-buffer F1/P/R and the committed MCC from an evaluation summary."""
    per_buffer: dict[int, dict[str, float]] = {}
    for row in summary.get("buffers") or []:
        b = row.get("buffer_metres")
        if b is None:
            continue
        per_buffer[int(b)] = {
            k: row.get(k) for k in ("f1", "precision", "recall")
        }
    tc = summary.get("tile_classification")
    mcc: Any = None
    if isinstance(tc, dict):
        m = tc.get("mcc")
        if isinstance(m, dict):
            m = m.get("point", m.get("mean"))
        mcc = m
        if tc.get("withheld"):
            mcc = "withheld"
    return per_buffer, mcc


def parse_eval(repo: Path, rel: str) -> dict[str, Any]:
    """Turn one evaluation.json into a cell spec (or an unresolved record)."""
    e = json.loads((repo / rel).read_text())
    md = e.get("_metadata") or {}
    inp = md.get("input_files") or {}
    ca = md.get("cli_args") or {}
    dets = inp.get("detections") or ca.get("detections")
    bounds = norm(inp.get("bounds") or ca.get("bounds"))
    gt = norm(inp.get("ground_truth") or ca.get("ground_truth"))
    script = md.get("script_path") or md.get("adapter") or md.get("adapted_by")
    if md.get("adapted_by") or md.get("adapter"):
        script = (md.get("adapter") or md.get("adapted_by")) + (
            " <- " + md["script_path"] if md.get("script_path") else ""
        )
    summary = e.get("summary") or {}
    per_buffer, mcc = committed_values(summary)
    spec: dict[str, Any] = {
        "eval": rel,
        "script": script,
        "detections": [norm(d) for d in (dets if isinstance(dets, list) else [dets])]
        if dets else None,
        "bounds": bounds,
        "ground_truth": gt,
        "tile_join": ca.get("tile_join") or "id",
        "glob": ca.get("glob"),
        "committed": {str(k): v for k, v in per_buffer.items()},
        "committed_mcc": mcc,
        "committed_n_detections": summary.get("n_detections"),
        "family": family_of(bounds or "", rel),
    }
    return spec


def resolve_detection_files(repo: Path, spec: dict[str, Any]) -> list[str]:
    """Expand a recorded ``--detections-dir`` (+ ``--glob``) the way the evaluator did.

    Multi-run evaluations record a directory, not files; ``evaluate_detections`` expanded it
    with ``find_detection_files``. The same function is called here, so a directory whose
    contents have changed since the evaluation shows up as a reproduction failure rather
    than being silently re-read.
    """
    out: list[str] = []
    for d in spec["detections"]:
        for old, new in REMAP:
            if d.startswith(old):
                d = new + d[len(old):]
        path = repo / d
        if path.is_dir():
            import scripts.evaluate_detections as ed  # noqa: PLC0415

            for f in ed.find_detection_files(path, spec.get("glob")):
                f = Path(f).resolve()
                out.append(str(f.relative_to(repo)) if f.is_relative_to(repo) else str(f))
        else:
            out.append(d)
    return out


def process(repo_s: str, spec: dict[str, Any],
            remap: list[tuple[str, str]] | None = None) -> dict[str, Any]:
    """Worker: diagnostics, OFF and ON scores for one cell spec."""
    REMAP[:] = remap or []
    repo = Path(repo_s)
    bl.add_repo_to_path(repo)
    t0 = time.time()
    res = dict(spec)
    try:
        if not spec["detections"] or not spec["bounds"] or not spec["ground_truth"]:
            res["status"] = "unresolved-metadata"
            return res
        spec["detections"] = resolve_detection_files(repo, spec)
        res["detections"] = spec["detections"]
        if not spec["detections"]:
            res["status"] = "missing-input"
            res["missing"] = ["<no files matched detections_dir/glob>"]
            return res
        missing = [d for d in spec["detections"] if not (repo / d).exists()]
        res["remapped"] = bool(REMAP) and any(not d.startswith("outputs/") and
                                              not d.startswith("results/")
                                              for d in spec["detections"])
        for p in (spec["bounds"], spec["ground_truth"]):
            if not (repo / p).exists():
                missing.append(p)
        if missing:
            res["status"] = "missing-input"
            res["missing"] = missing
            return res
        bounds = bl.load_geojson(repo / spec["bounds"])
        ref = bl.load_geojson(repo / spec["ground_truth"])
        direct = (spec["script"] in DIRECT_SCRIPTS)
        committed_b = sorted(int(b) for b in spec["committed"])
        runs = []
        any_drop = False
        for d in spec["detections"]:
            det = bl.load_detections(repo / d, bounds)
            scoped, diag = bl.geometric_detection_scope(det, bounds)
            diag["source_tile_synthesised"] = bool(det.attrs.get("source_tile_synthesised"))
            runs.append((det, scoped, diag))
            any_drop = any_drop or diag["n_out_of_frame"] > 0
        res["diag_runs"] = [r[2] for r in runs]
        res["n_out_of_frame"] = sum(r[2]["n_out_of_frame"] for r in runs)
        res["n_null_source_tile"] = sum(r[2]["n_null_source_tile"] for r in runs)
        res["n_null_in_frame"] = sum(r[2]["n_null_in_frame"] for r in runs)
        res["n_unprefixed_in_frame"] = sum(r[2]["n_unprefixed_in_frame"] for r in runs)
        res["n_detections_loaded"] = [len(r[0]) for r in runs]
        if not direct:
            res["status"] = "diagnostics-only (non-direct scorer)"
            return res
        if any_drop:
            buffers = committed_b or [20]
        else:
            buffers = [b for b in committed_b if b in GATE_BUFFERS] or committed_b[:1] or [20]
        want_mcc = spec["committed_mcc"] is not None
        off_runs = [bl.score_point(r[0], ref, bounds, buffers, want_mcc=want_mcc,
                                   tile_join=spec["tile_join"]) for r in runs]
        res["off"] = mean_runs(off_runs, buffers)
        if any_drop:
            on_runs = [bl.score_point(r[1], ref, bounds, buffers, want_mcc=want_mcc,
                                      tile_join=spec["tile_join"]) for r in runs]
            res["on"] = mean_runs(on_runs, buffers)
        else:
            res["on"] = res["off"]
            res["on_identical_by_construction"] = True
        res["status"] = "scored"
    except Exception as exc:  # noqa: BLE001 - record and continue the sweep
        res["status"] = "error"
        res["error"] = f"{type(exc).__name__}: {exc}"
        res["traceback"] = traceback.format_exc()[-2000:]
    res["seconds"] = round(time.time() - t0, 2)
    return res


def mean_runs(runs: list[dict[str, Any]], buffers: list[int]) -> dict[str, Any]:
    """Average per-run point estimates as ``evaluate_multi_run_mean`` does (defined MCC only)."""
    if len(runs) == 1:
        r = runs[0]
        return {"per_buffer": {str(b): v for b, v in r["per_buffer"].items()},
                "mcc": r["mcc"], "mcc_refused": r["mcc_refused"]}
    out: dict[str, Any] = {"per_buffer": {}}
    for b in buffers:
        out["per_buffer"][str(b)] = {
            k: sum(r["per_buffer"][b][k] for r in runs) / len(runs)
            for k in ("f1", "precision", "recall")
        }
    defined = [r["mcc"] for r in runs if r["mcc"] is not None]
    out["mcc"] = sum(defined) / len(defined) if defined else None
    out["mcc_refused"] = next((r["mcc_refused"] for r in runs if r["mcc_refused"]), None)
    return out


def main() -> int:
    """Enumerate evaluations, fan out to workers, and write one JSON line per cell."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--limit", type=int, default=0, help="debug: first N evaluations only")
    ap.add_argument("--only", nargs="*", default=None, help="debug: these evaluation paths")
    ap.add_argument("--remap", nargs="*", default=[],
                    help="OLD=NEW prefix rewrites for recorded detection paths")
    ap.add_argument("--only-file", type=Path, default=None,
                    help="re-run only the evaluation paths listed (one per line) in this file")
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    files = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "*evaluation.json"], text=True,
    ).split()
    if args.only:
        files = [f for f in files if f in set(args.only)]
    if args.only_file:
        wanted = set(args.only_file.read_text().split())
        files = [f for f in files if f in wanted]
    if args.limit:
        files = files[: args.limit]
    specs = []
    for rel in files:
        try:
            specs.append(parse_eval(repo, rel))
        except Exception as exc:  # noqa: BLE001
            specs.append({"eval": rel, "status": "unparseable", "error": str(exc)})
    remap = [tuple(r.split("=", 1)) for r in args.remap]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    done = 0
    with args.out.open("w") as fh, ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = []
        for s in specs:
            if s.get("status") == "unparseable":
                fh.write(json.dumps(s) + "\n")
                continue
            futs.append(pool.submit(process, str(repo), s, remap))
        for fut in as_completed(futs):
            fh.write(json.dumps(fut.result(), default=str) + "\n")
            fh.flush()
            done += 1
            if done % 100 == 0:
                print(f"{done}/{len(futs)} cells", flush=True)
    print(f"DONE {done} cells -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
