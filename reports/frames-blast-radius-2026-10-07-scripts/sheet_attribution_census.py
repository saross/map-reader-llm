"""Census of detections scored on a different map sheet from the one they were seen on.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only.

``calculate_f1_internal`` matches detections to references PER SHEET: a detection is put on
sheet M when its ``source_tile`` begins with M, a reference when its ``Map`` attribute is M.
The tier E cells showed that a detection seen on sheet M can be scored on the neighbouring
sheet N when its ``source_tile`` was re-assigned geometrically (nearest or first frame tile
among ALL sheets), because the padded tiles of adjacent sheets overlap. Such a detection
cannot match its own sheet's reference, so one true positive becomes a false positive plus a
false negative.

For every scored cell (rows from ``rescore_evaluations.py``) whose detection files record
the proposer's own tiles (``source_tiles``, ``origin_source_tile`` or ``origin_tiles``), this
script counts detections whose scoring sheet (the ``source_tile`` the scorer sees,
synthesised by the evaluator's spatial join when absent) is not among their origin sheets.
Where any is found, it re-scores at the cell's 20 m and 50 m buffers with the origin sheet
restored, with and without the geometric frame scope.

Usage::

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python sheet_attribution_census.py \
        --repo ~/Code/map-reader-llm --rows out/evaluations.jsonl out/evaluations_rerun.jsonl \
        out/evaluations_nx.jsonl --out out/sheet_census.jsonl --workers 20
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blast_lib as bl  # noqa: E402

ORIGIN_COLUMNS = ("origin_source_tile", "origin_tiles", "source_tiles")


def as_list(value: Any) -> list[str]:
    """Normalise a tile-list property (list, JSON string, ";"-joined or scalar) to names."""
    if value is None:
        return []
    if isinstance(value, float) and value != value:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if v]
    text = str(value).strip()
    if text.startswith("["):
        try:
            return [str(v) for v in json.loads(text) if v]
        except json.JSONDecodeError:
            return [text]
    # The h13 scoring files join several origin tiles with ";".
    return [t.strip() for t in text.split(";") if t.strip()]


def origin_maps(row: Any, column: str) -> set[str]:
    """Origin sheets of one detection from its recorded proposer tile(s)."""
    return {bl.LIB.get_map_name(t) for t in as_list(row[column])} - {"Unknown"}


def process(repo_s: str, row: dict[str, Any]) -> dict[str, Any]:
    """Worker: count cross-sheet detections in one cell and re-score if any."""
    repo = Path(repo_s)
    bl.add_repo_to_path(repo)
    out: dict[str, Any] = {"eval": row["eval"], "family": row.get("family")}
    try:
        bounds = bl.load_geojson(repo / row["bounds"])
        frame = set(bl.frame_maps(bounds))
        ref = None
        total_cross = 0
        runs = []
        for d in row["detections"]:
            det = bl.load_detections(repo / d, bounds)
            column = next((c for c in ORIGIN_COLUMNS if c in det.columns), None)
            info = {"file": d, "origin_column": column, "n": len(det),
                    "source_tile_synthesised": bool(det.attrs.get("source_tile_synthesised"))}
            if column is None or det.empty:
                info["n_cross_sheet"] = None
                runs.append((det, None, info))
                continue
            scoring = det["source_tile"].map(
                lambda v: bl.LIB.get_map_name(v) if isinstance(v, str) and v else None)
            origins = det.apply(lambda r: origin_maps(r, column), axis=1)
            cross = [bool(s is not None and o and s not in o)
                     for s, o in zip(scoring, origins)]
            info["n_cross_sheet"] = int(sum(cross))
            info["n_multi_origin"] = int(sum(len(o) > 1 for o in origins))
            total_cross += info["n_cross_sheet"]
            restored = det.copy()
            # Keep the scoring name when it is one of the origins; otherwise put the
            # detection on its (first, sorted) origin sheet. Only the sheet prefix matters
            # to calculate_f1_internal, so a synthetic tile suffix is enough.
            restored["source_tile"] = [
                (v if (s in o or not o or s is None) else f"{sorted(o & frame or o)[0]}_x0_y0")
                for v, s, o in zip(det["source_tile"], scoring, origins)
            ]
            runs.append((det, restored, info))
        out["files"] = [r[2] for r in runs]
        out["n_cross_sheet"] = total_cross
        if total_cross > 0:
            ref = bl.load_geojson(repo / row["ground_truth"])
            buffers = [b for b in (20, 50) if str(b) in (row.get("committed") or {})] or [20]
            scores: dict[str, dict[str, float]] = {}
            for b in buffers:
                vals = {"as_scored": [], "origin_sheet": [], "origin_sheet_geometric": []}
                for det, restored, _ in runs:
                    if restored is None:
                        restored = det
                    vals["as_scored"].append(
                        bl.LIB.calculate_f1_internal(det, ref, bounds, buffer_metres=b)[2])
                    vals["origin_sheet"].append(
                        bl.LIB.calculate_f1_internal(restored, ref, bounds, buffer_metres=b)[2])
                    scoped, _ = bl.geometric_detection_scope(restored, bounds)
                    vals["origin_sheet_geometric"].append(
                        bl.LIB.calculate_f1_internal(scoped, ref, bounds, buffer_metres=b)[2])
                scores[str(b)] = {k: sum(v) / len(v) for k, v in vals.items()}
            out["f1"] = scores
        out["status"] = "ok"
    except Exception as exc:  # noqa: BLE001
        out["status"] = "error"
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def main() -> int:
    """Run the census over every scored cell."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rows", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=20)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    rows: dict[str, dict[str, Any]] = {}
    for path in args.rows:
        for line in path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                rows[r["eval"]] = r
    todo = [r for r in rows.values() if r.get("status") == "scored"]
    with args.out.open("w") as fh, ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(process, str(repo), r) for r in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            fh.write(json.dumps(fut.result()) + "\n")
            if i % 250 == 0:
                print(f"{i}/{len(futs)}", flush=True)
    print(f"DONE {len(todo)} cells -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
