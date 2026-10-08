"""Re-score every cell the frames blast-radius scored, with the D50 scorer.

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only with respect to
every repository: code from ``--code`` (the branch worktree), data from
``--data`` (a ``main`` checkout), output to ``--out``.

Input rows are the blast-radius per-cell rows (``evaluations.jsonl``, then
``evaluations_rerun.jsonl`` and ``evaluations_nx.jsonl``, later files
overriding earlier ones per evaluation, as that report's summary merged them).
Each row already names its resolved detection files, frame, references, tile
join, the buffers it was scored at, and its OFF and ON values. For every row:

1. the NEW scope diagnostics (``scope_detections_to_frame``) are computed for
   every detection file — for the corrected-F1 cells too, which the blast
   radius could only diagnose;
2. for every directly scored cell (``status == "scored"``), F1, P and R at the
   row's own buffers, and tile MCC where the cell commits one, are recomputed
   with the NEW scorer — for EVERY cell, not only those where the rule fires,
   so "unchanged by construction" is tested rather than assumed.

Usage::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python rescore_new.py \
        --code ~/worktrees/map-reader-llm/claude-scorer-d50 --data ~/Code/map-reader-llm \
        --rows BLAST/out/evaluations.jsonl BLAST/out/evaluations_rerun.jsonl \
               BLAST/out/evaluations_nx.jsonl \
        --out out/new_evaluations.jsonl --workers 20
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meas_lib as ml  # noqa: E402


def merged_rows(paths: list[Path]) -> dict[str, dict[str, Any]]:
    """Merge the blast-radius row files; a later file overrides an earlier one."""
    rows: dict[str, dict[str, Any]] = {}
    for path in paths:
        for line in path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                rows[row["eval"]] = row
    return rows


def process(code: str, data: str, row: dict[str, Any]) -> dict[str, Any]:
    """Worker: NEW diagnostics (and, for scored cells, NEW scores) for one row."""
    ml.setup(Path(code))
    data_repo = Path(data)
    t0 = time.time()
    out: dict[str, Any] = {k: row.get(k) for k in (
        "eval", "family", "status", "script", "tile_join", "committed_mcc",
        "n_out_of_frame", "n_null_source_tile")}
    out["blast_off"] = row.get("off")
    out["blast_on"] = row.get("on")
    try:
        if row.get("status") not in ("scored", "diagnostics-only (non-direct scorer)"):
            out["new_status"] = "skipped"
            return out
        bounds = ml.load_geojson(ml.resolve(data_repo, row["bounds"]))
        dets = [ml.load_detections(ml.resolve(data_repo, d), bounds)
                for d in row["detections"]]
        blocks = [ml.LIB.scope_detections_to_frame(d, bounds, require_attribution=False)
                  .diagnostics for d in dets]
        out["new_scope"] = ml.sum_diagnostics(blocks)
        out["new_scope_origin_columns"] = sorted(
            {c for b in blocks for c in b.get("origin_columns", [])})
        if row["status"] != "scored":
            out["new_status"] = "diagnostics-only"
            return out
        ref = ml.load_geojson(ml.resolve(data_repo, row["ground_truth"]))
        buffers = [int(b) for b in (row.get("off") or {}).get("per_buffer", {})]
        want_mcc = row.get("committed_mcc") is not None
        runs = [ml.score_point(d, ref, bounds, buffers, want_mcc=want_mcc,
                               tile_join=row.get("tile_join") or "id") for d in dets]
        out["new"] = ml.mean_runs(runs)
        out["new_status"] = "scored"
    except Exception as exc:  # noqa: BLE001 - record and continue
        out["new_status"] = "error"
        out["error"] = f"{type(exc).__name__}: {exc}"
        out["traceback"] = traceback.format_exc()[-1500:]
    out["seconds"] = round(time.time() - t0, 2)
    return out


def main() -> int:
    """Fan the merged rows out to workers and write one JSON line per cell."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--rows", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    rows = merged_rows(args.rows)
    if args.only:
        rows = {k: v for k, v in rows.items() if k in set(args.only)}
    code, data = str(args.code.expanduser().resolve()), str(args.data.expanduser().resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as fh, ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(process, code, data, r) for r in rows.values()]
        for i, fut in enumerate(as_completed(futs), 1):
            fh.write(json.dumps(fut.result(), default=str) + "\n")
            fh.flush()
            if i % 100 == 0:
                print(f"{i}/{len(futs)} cells", flush=True)
    print(f"DONE {len(rows)} cells -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
