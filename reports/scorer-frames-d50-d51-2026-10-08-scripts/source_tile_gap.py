"""Count the materialised-``source_tile`` gap in the D50 scope, and score its fix.

D50/D51 addendum, 2026-10-08 (Session 163). Read-only with respect to every
repository: code from ``--code`` (a throwaway copy of the branch, or of the
branch with the draft fix applied), data from ``--data`` (a ``main``
checkout), output to ``--out``. No API call.

**The gap.** ``scope_detections_to_frame`` keeps a ``source_tile`` that names
one of the detection's origin sheets (the sheets its recorded member tiles lie
on), without asking whether that sheet's frame tiles hold the point. The
materialisers (``materialise_pv_geojson.py`` line 221,
``materialise_opmax_cells.py`` line 393) write the first, alphabetical,
member of ``source_tiles`` there. A cluster seen on two sheets, named on the
first and lying only in the second sheet's frame tiles, is therefore dropped
as out of frame, although it was seen on a sheet whose tiles hold it.

Subcommands:

``probe``
    The synthetic two-sheet case, scored with ``--code``'s scorer.
``census``
    For every cell the D50 measurement re-scored (the frames report's merged
    rows, as ``rescore_new.merged_rows`` reads them), every detection file is
    loaded exactly as the evaluator loads it (``meas_lib.load_detections``)
    and each row is classified independently of the library's scope: an
    *affected* row has its ``source_tile`` on an origin sheet whose frame tiles
    it does not intersect, and intersects another origin sheet's; a *stuck*
    row is the same but with no other origin sheet holding it (out of frame
    under either rule). The library's own diagnostics are summed beside the
    count (with the draft fix, ``n_origin_switched`` must equal it).
``score``
    For the cells the census marks affected, ``rescore_new.process`` (the D50
    measurement's own worker) re-scores F1, precision and recall at the row's
    buffers and tile MCC, with ``--code``'s scorer: run once with the branch
    (rule a) and once with the draft fix (rule b).
``sweeps``
    The same classification over the twelve sweep universes' candidate
    manifests. The sweep loader (``sweep_f1_wbf.load_candidates_as_gdf``)
    keeps ``source_tile`` and drops the member list, so the draft fix cannot
    reach these rows; the count says whether that matters.
``summarise``
    Joins the census, both score files, the D50 measurement's rows (rule a
    must reproduce them) and the frames report's register columns
    (``cells.csv``), and writes the record. Given full re-scores as the two
    score files, it also compares rule b with rule a over EVERY scored cell.

Usage (on sapphire, from the scratch directory; ``repo`` is a ``git archive``
of the branch at ``842f9e92a``, ``repo-alt`` the same with
``out/source-tile-gap/draft-fix.diff`` applied)::

    PY=~/Code/map-reader-llm/.venv/bin/python
    BLAST=~/scratch/frames-blast-radius-2026-10-07/out
    CELLS=~/Code/map-reader-llm/reports/frames-blast-radius-2026-10-07-scripts/out/summary
    ROWS="$BLAST/evaluations.jsonl $BLAST/evaluations_rerun.jsonl $BLAST/evaluations_nx.jsonl"
    $PY scripts/source_tile_gap.py probe --code repo --out out/probe_a.json
    $PY scripts/source_tile_gap.py probe --code repo-alt --out out/probe_b.json
    $PY scripts/source_tile_gap.py census --code repo-alt --data ~/Code/map-reader-llm \
        --rows $ROWS --out out/census.jsonl --workers 8
    $PY scripts/source_tile_gap.py sweeps --code repo-alt --data ~/Code/map-reader-llm \
        --jobs sweep_jobs_plus_stride.json --out out/sweeps_census.json
    # The census found no affected cell, so ``score`` had nothing to score;
    # the D50 run's own worker re-scored every row with each copy instead:
    $PY scripts/rescore_new.py --code repo --data ~/Code/map-reader-llm \
        --rows $ROWS --out out/rescore_a.jsonl --workers 12
    $PY scripts/rescore_new.py --code repo-alt --data ~/Code/map-reader-llm \
        --rows $ROWS --out out/rescore_b.jsonl --workers 12
    $PY scripts/source_tile_gap.py summarise --census out/census.jsonl \
        --scores-a out/rescore_a.jsonl --scores-b out/rescore_b.jsonl \
        --d50-rows ~/scratch/scorer-frames-d50-d51-2026-10-08/out/new_evaluations.jsonl \
        --cells $CELLS/cells.csv \
        --out out/source-tile-gap.json
"""

from __future__ import annotations

import argparse
import csv
import functools
import json
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pyogrio

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meas_lib as ml  # noqa: E402

METRICS = ("f1", "precision", "recall")
#: Smallest change the D50 report counts as a move.
MOVE = 0.001
#: Example rows recorded per cell.
N_EXAMPLES = 3


# ── Classification (independent of the library's scope) ──────────────────


def classify(gdf: Any, bounds: Any) -> dict[str, Any]:
    """Classify each detection against the gap, by the D50 attribution inputs.

    Uses only the library's naming helpers (``frame_sheets``,
    ``_sheet_of_tile_name``, ``_parse_origin_cell``, ``ORIGIN_TILE_COLUMNS``)
    and its own ``intersects`` join, not ``scope_detections_to_frame``, so the
    count is a check on the draft fix's counter rather than a copy of it.

    Args:
        gdf: Detections as the evaluator loads them.
        bounds: Frame tile polygons with ``tile_name``.

    Returns:
        Counts ``n_detections``, ``n_affected`` (named on an origin sheet whose
        tiles miss it, inside another origin sheet's), ``n_stuck`` (named on
        an origin sheet whose tiles miss it, inside no other origin sheet's),
        ``n_multi_origin`` (two or more origin sheets), ``source_tile_in_file``
        and ``origin_columns``, plus up to :data:`N_EXAMPLES` affected rows.
        The ``*_all_columns`` counts repeat ``n_multi_origin`` and
        ``n_affected`` with the origin sheets taken from EVERY origin column
        rather than the first with a value, in case a single-name
        ``origin_source_tile`` hides a two-sheet ``source_tiles`` list.
    """
    import geopandas as gpd  # noqa: PLC0415

    lib = ml.LIB
    n = len(gdf)
    out: dict[str, Any] = {"n_detections": n, "n_affected": 0, "n_stuck": 0,
                           "n_multi_origin": 0, "n_multi_origin_all_columns": 0,
                           "n_affected_all_columns": 0, "examples": []}
    if n == 0:
        return out
    sheets = lib.frame_sheets(bounds)
    longest = sorted(sheets, key=len, reverse=True)
    tile_sheet = {str(t): lib._sheet_of_tile_name(str(t), longest)
                  for t in bounds["tile_name"].unique()}
    points = gpd.GeoDataFrame(geometry=gdf.geometry.to_numpy(), crs=gdf.crs)
    joined = gpd.sjoin(points, bounds[["tile_name", "geometry"]], how="inner",
                       predicate="intersects")
    hit: list[set[str]] = [set() for _ in range(n)]
    for pos, tile in zip(joined.index.to_numpy(), joined["tile_name"]):
        sheet = tile_sheet.get(str(tile))
        if sheet is not None:
            hit[pos].add(sheet)
    columns = [c for c in lib.ORIGIN_TILE_COLUMNS if c in gdf.columns]
    out["origin_columns"] = columns
    if not columns or "source_tile" not in gdf.columns:
        return out
    names = gdf["source_tile"].tolist()
    values = [(c, gdf[c].tolist()) for c in columns]
    for pos in range(n):
        source_sheet = lib._sheet_of_tile_name(names[pos], longest)
        origin: list[str] = []
        every: list[str] = []
        for column, vals in values:
            parsed = lib._parse_origin_cell(vals[pos], column, pos)
            every.extend(parsed)
            if parsed and not origin:
                origin = parsed
        origin_frame = {s for s in (lib._sheet_of_tile_name(t, longest) for t in origin)
                        if s is not None}
        every_frame = {s for s in (lib._sheet_of_tile_name(t, longest) for t in every)
                       if s is not None}
        if len(origin_frame) >= 2:
            out["n_multi_origin"] += 1
        if len(every_frame) >= 2:
            out["n_multi_origin_all_columns"] += 1
        if (source_sheet in every_frame and source_sheet not in hit[pos]
                and every_frame & hit[pos]):
            out["n_affected_all_columns"] += 1
        if source_sheet is None or source_sheet not in origin_frame:
            continue
        if source_sheet in hit[pos]:
            continue
        others = sorted(origin_frame & hit[pos])
        if not others:
            out["n_stuck"] += 1
            continue
        out["n_affected"] += 1
        if len(out["examples"]) < N_EXAMPLES:
            geom = gdf.geometry.iloc[pos]
            out["examples"].append({
                "row": pos, "source_tile": names[pos], "origin_tiles": origin,
                "named_sheet": source_sheet, "sheets_holding": sorted(hit[pos]),
                "alternative_sheet": others[0],
                "x": round(float(geom.x), 1), "y": round(float(geom.y), 1),
            })
    return out


@functools.lru_cache(maxsize=64)
def _bounds(path: str) -> Any:
    """Load a frame once per worker."""
    return ml.load_geojson(Path(path))


def census_one(code: str, data: str, row: dict[str, Any]) -> dict[str, Any]:
    """Worker: classify every detection file of one cell, and sum the scope diagnostics."""
    ml.setup(Path(code))
    t0 = time.time()
    out: dict[str, Any] = {k: row.get(k) for k in ("eval", "family", "status")}
    if row.get("status") not in ("scored", "diagnostics-only (non-direct scorer)"):
        out["census_status"] = "skipped"
        return out
    try:
        data_repo = Path(data)
        bounds = _bounds(str(ml.resolve(data_repo, row["bounds"])))
        files = []
        diag_blocks = []
        for d in row["detections"]:
            path = ml.resolve(data_repo, d)
            # The file's own fields, before the evaluator synthesises a
            # missing source_tile by spatial join.
            raw_cols = list(pyogrio.read_info(path)["fields"])
            gdf = ml.load_detections(path, bounds)
            c = classify(gdf, bounds)
            c["file"] = d
            c["source_tile_in_file"] = "source_tile" in raw_cols
            files.append(c)
            diag_blocks.append(ml.LIB.scope_detections_to_frame(
                gdf, bounds, require_attribution=False).diagnostics)
        out["n_files"] = len(files)
        for k in ("n_detections", "n_affected", "n_stuck", "n_multi_origin",
                  "n_multi_origin_all_columns", "n_affected_all_columns"):
            out[k] = sum(f[k] for f in files)
        out["n_files_affected"] = sum(1 for f in files if f["n_affected"])
        out["source_tile_in_file"] = sorted({f["source_tile_in_file"] for f in files})
        out["origin_columns"] = sorted({c for f in files for c in f.get("origin_columns", [])})
        out["examples"] = [dict(e, file=f["file"]) for f in files
                           for e in f["examples"]][:N_EXAMPLES]
        keys = sorted({k for b in diag_blocks for k, v in b.items()
                       if k.startswith("n_") and isinstance(v, int)})
        out["lib_scope"] = {k: int(sum(int(b.get(k) or 0) for b in diag_blocks))
                            for k in keys}
        out["census_status"] = "ok"
    except Exception as exc:  # noqa: BLE001 - record and continue
        out["census_status"] = "error"
        out["error"] = f"{type(exc).__name__}: {exc}"
        out["traceback"] = traceback.format_exc()[-1500:]
    out["seconds"] = round(time.time() - t0, 2)
    return out


# ── Subcommands ───────────────────────────────────────────────────────────


def cmd_probe(args: argparse.Namespace) -> int:
    """The synthetic case: two sheets, a cluster seen on both, named on the first."""
    ml.setup(args.code)
    import geopandas as gpd  # noqa: PLC0415
    from shapely.geometry import Point, box  # noqa: PLC0415

    crs = "EPSG:32635"
    # Sheet A tiles x 0-200, sheet B tiles x 190-390 (10 m overlap), as in
    # tests/test_detection_scope.py's fixture.
    frame = gpd.GeoDataFrame(
        {"tile_name": ["A_x0_y0.png", "A_x100_y0.png", "B_x0_y0.png", "B_x100_y0.png"]},
        geometry=[box(0, 0, 100, 100), box(100, 0, 200, 100),
                  box(190, 0, 290, 100), box(290, 0, 390, 100)], crs=crs)
    # Members seen on A_x100 (x 100-200) and B_x0 (x 190-290); centroid at
    # x 205, inside B_x0 only. source_tile = source_tiles[0], as written by
    # materialise_pv_geojson.py.
    det = gpd.GeoDataFrame(
        {"source_tile": ["A_x100_y0.png"],
         "source_tiles": [["A_x100_y0.png", "B_x0_y0.png"]]},
        geometry=[Point(205, 50)], crs=crs)
    ref = gpd.GeoDataFrame({"Map": ["B"]}, geometry=[Point(206, 50)], crs=crs)
    scope = ml.LIB.scope_detections_to_frame(det, frame)
    p, r, f = ml.LIB.calculate_f1_internal(det, ref, frame, buffer_metres=20)
    tc = ml.LIB.calculate_tile_classification(det, ref, frame)
    rec = {
        "code": str(args.code), "lib": ml.LIB.__file__,
        "scored_on": [str(s) for s in scope.sheets],
        "diagnostics": {k: v for k, v in scope.diagnostics.items()
                        if k.startswith("n_")},
        "f1_20": {"precision": p, "recall": r, "f1": f},
        "tile_confusion": {k: tc.get(k) for k in ("tp", "fp", "fn", "tn", "mcc", "error")},
        "classify": classify(det, frame),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rec, indent=1, default=str))
    print(json.dumps(rec, indent=1, default=str))
    return 0


def _rows(args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    """The frames report's merged rows (``rescore_new.merged_rows``)."""
    from rescore_new import merged_rows  # noqa: PLC0415

    return merged_rows(args.rows)


def _fan_out(fn: Any, code: Path, data: Path, rows: list[dict[str, Any]], out: Path,
             workers: int) -> None:
    """Run ``fn(code, data, row)`` over rows in a process pool, one JSON line each."""
    code_s = str(code.expanduser().resolve())
    data_s = str(data.expanduser().resolve())
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh, ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(fn, code_s, data_s, r) for r in rows]
        for i, fut in enumerate(as_completed(futs), 1):
            fh.write(json.dumps(fut.result(), default=str) + "\n")
            fh.flush()
            if i % 200 == 0:
                print(f"{i}/{len(futs)} cells", flush=True)
    print(f"DONE {len(rows)} cells -> {out}", flush=True)


def cmd_census(args: argparse.Namespace) -> int:
    """Classify every cell's detections."""
    rows = list(_rows(args).values())
    _fan_out(census_one, args.code, args.data, rows, args.out, args.workers)
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    """Re-score the affected cells with ``--code``'s scorer (rescore_new.process)."""
    from rescore_new import process  # noqa: PLC0415

    census = [json.loads(x) for x in args.census.read_text().splitlines() if x.strip()]
    affected = {c["eval"] for c in census
                if c.get("census_status") == "ok" and c.get("n_affected")}
    rows = [r for e, r in _rows(args).items() if e in affected]
    print(f"{len(rows)} affected cells to score with {args.code}", flush=True)
    _fan_out(process, args.code, args.data, rows, args.out, args.workers)
    return 0


def cmd_sweeps(args: argparse.Namespace) -> int:
    """Classify the sweep universes' candidates as the sweep loader presents them."""
    ml.setup(args.code)
    import geopandas as gpd  # noqa: PLC0415
    from shapely.geometry import Point  # noqa: PLC0415

    data = args.data.expanduser().resolve()
    jobs = json.loads(args.jobs.read_text())
    results = []
    for job in jobs:
        manifest_path = data / job["crops_dir"] / "candidate_manifest.json"
        cands = json.loads(manifest_path.read_text())["candidates"]
        bounds = _bounds(str(data / job["bounds"]))
        recs = []
        for c in cands:
            props = c.get("properties") or {}
            recs.append({
                "source_tile": c.get("source_tile", ""),
                "source_tiles": props.get("source_tiles") or c.get("source_tiles") or [],
                "geometry": Point(float(c["centroid_x"]), float(c["centroid_y"])),
            })
        gdf = gpd.GeoDataFrame(recs, crs="EPSG:32635")
        with_members = classify(gdf, bounds)
        results.append({
            "name": job["name"], "bounds": job["bounds"],
            "n_candidates": len(gdf),
            "n_with_member_list": int(sum(1 for r in recs if len(r["source_tiles"]))),
            "manifest_source_tile_is_first_member": int(sum(
                1 for r in recs if r["source_tiles"]
                and r["source_tile"] == sorted(r["source_tiles"])[0])),
            "classify_with_members": {k: with_members[k] for k in (
                "n_affected", "n_stuck", "n_multi_origin")},
            "examples": with_members["examples"],
        })
        print(json.dumps(results[-1], default=str)[:400], flush=True)
    args.out.write_text(json.dumps(results, indent=1, default=str))
    return 0


# ── Summary ───────────────────────────────────────────────────────────────


def _load(path: Path) -> dict[str, dict[str, Any]]:
    """JSON lines keyed by evaluation path."""
    out = {}
    for line in path.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["eval"]] = r
    return out


def _deltas(b: dict[str, Any], a: dict[str, Any]) -> dict[str, Any]:
    """Signed b − a for every metric at every buffer, and MCC; with the largest |Δ|."""
    out: dict[str, Any] = {"per_buffer": {}, "mcc": None}
    worst = 0.0
    for buf, va in (a.get("per_buffer") or {}).items():
        vb = (b.get("per_buffer") or {}).get(buf)
        if not vb:
            continue
        out["per_buffer"][buf] = {m: vb[m] - va[m] for m in METRICS}
        worst = max(worst, *(abs(v) for v in out["per_buffer"][buf].values()))
    if isinstance(a.get("mcc"), (int, float)) and isinstance(b.get("mcc"), (int, float)):
        out["mcc"] = b["mcc"] - a["mcc"]
        worst = max(worst, abs(out["mcc"]))
    out["max_abs"] = worst
    out["mcc_state_changed"] = (a.get("mcc") is None) != (b.get("mcc") is None)
    return out


def _max_abs(a: dict[str, Any] | None, b: dict[str, Any] | None) -> float | None:
    """Largest |a − b| over buffers, metrics and MCC (summarise_new.max_abs_delta)."""
    if not a or not b:
        return None
    return _deltas(b, a)["max_abs"]


def cmd_summarise(args: argparse.Namespace) -> int:
    """Join census, scores, the D50 rows and the register; write the record."""
    census = _load(args.census)
    sa, sb = _load(args.scores_a), _load(args.scores_b)
    d50 = _load(args.d50_rows)
    register = {r["eval"]: r for r in csv.DictReader(args.cells.open())}

    ok = [c for c in census.values() if c.get("census_status") == "ok"]
    affected = [c for c in ok if c.get("n_affected")]
    errors = [{"eval": c["eval"], "error": c.get("error")}
              for c in census.values() if c.get("census_status") == "error"]
    # Cross-check 1: the draft fix's counter equals the independent count.
    counter_mismatch = [c["eval"] for c in ok
                        if (c.get("lib_scope") or {}).get("n_origin_switched", -1)
                        != c.get("n_affected")]
    # Cross-check 2: with the fix, out-of-frame falls by exactly the count,
    # against the D50 run's branch diagnostics.
    oof_mismatch = []
    for c in ok:
        prev = (d50.get(c["eval"]) or {}).get("new_scope") or {}
        if "n_out_of_frame" in prev and (prev["n_out_of_frame"] - c["n_affected"]
                                         != (c.get("lib_scope") or {}).get("n_out_of_frame")):
            oof_mismatch.append(c["eval"])

    cells = []
    for c in affected:
        ev = c["eval"]
        a, b = sa.get(ev) or {}, sb.get(ev) or {}
        prev = d50.get(ev) or {}
        reg = register.get(ev, {})
        rec: dict[str, Any] = {
            "eval": ev, "family": c.get("family"), "status": c.get("status"),
            "conditions": reg.get("conditions", ""), "analyses": reg.get("analyses", ""),
            "n_detections": c["n_detections"], "n_affected": c["n_affected"],
            "n_stuck": c["n_stuck"], "n_files": c["n_files"],
            "n_files_affected": c["n_files_affected"],
            "source_tile_in_file": c["source_tile_in_file"],
            "origin_columns": c["origin_columns"],
            "d50_origin_restored": ((prev.get("new_scope") or {}).get("n_origin_restored")),
            "examples": c.get("examples"),
        }
        if a.get("new_status") == "scored" and b.get("new_status") == "scored":
            rec["a"], rec["b"] = a["new"], b["new"]
            rec["delta_b_minus_a"] = _deltas(b["new"], a["new"])
            rec["a_reproduces_d50"] = (
                prev.get("new_status") == "scored"
                and (_max_abs(a["new"], prev["new"]) or 0.0) <= 1e-9)
            rec["delta_vs_off"] = _max_abs(b["new"], prev.get("blast_off"))
        else:
            rec["score_status"] = (a.get("new_status"), b.get("new_status"))
        cells.append(rec)

    # End to end: when ``--scores-a`` and ``--scores-b`` are full re-scores
    # (``rescore_new.py`` over every row), compare every scored cell, not
    # only the census's affected ones: rule b against rule a (the fix's
    # whole effect), and rule a against the D50 run (data or code drift
    # since that run).
    both = [ev for ev in sa if sa[ev].get("new_status") == "scored"
            and (sb.get(ev) or {}).get("new_status") == "scored"]
    e2e_b_a = {ev: _max_abs(sb[ev]["new"], sa[ev]["new"]) or 0.0 for ev in both}
    e2e_a_d50 = {ev: _max_abs(sa[ev]["new"], (d50.get(ev) or {}).get("new"))
                 for ev in both if (d50.get(ev) or {}).get("new_status") == "scored"}
    end_to_end = {
        "n_scored_in_both": len(both),
        "n_b_differs_from_a_gt_1e-9": sum(1 for v in e2e_b_a.values() if v > 1e-9),
        "n_b_moves_vs_a_ge_0.001": sum(1 for v in e2e_b_a.values() if v >= MOVE),
        "max_abs_b_minus_a": max(e2e_b_a.values(), default=None),
        "n_compared_with_d50": len(e2e_a_d50),
        "n_a_reproduces_d50_1e-9": sum(1 for v in e2e_a_d50.values()
                                       if v is not None and v <= 1e-9),
        "a_not_reproducing_d50": sorted(ev for ev, v in e2e_a_d50.items()
                                        if v is None or v > 1e-9),
        "status_counts_a": dict(Counter(r.get("new_status") for r in sa.values())),
        "status_counts_b": dict(Counter(r.get("new_status") for r in sb.values())),
    }

    scored = [r for r in cells if "delta_b_minus_a" in r]
    moved = [r for r in scored
             if r["delta_b_minus_a"]["max_abs"] >= MOVE
             or r["delta_b_minus_a"]["mcc_state_changed"]]
    f1_20 = [r["delta_b_minus_a"]["per_buffer"].get("20", {}).get("f1") for r in scored]
    f1_20 = [x for x in f1_20 if x is not None]
    registered = [r for r in moved if r["conditions"]]
    largest = max(scored, key=lambda r: r["delta_b_minus_a"]["max_abs"], default=None)
    summary = {
        "n_cells_census": len(census), "n_cells_classified": len(ok),
        "census_errors": errors,
        "n_cells_affected": len(affected),
        "n_detections_affected": sum(c["n_affected"] for c in affected),
        "n_detections_stuck_all_cells": sum(c["n_stuck"] for c in ok),
        "n_cells_with_stuck": sum(1 for c in ok if c["n_stuck"]),
        "n_cells_with_multi_origin": sum(1 for c in ok if c["n_multi_origin"]),
        "n_detections_multi_origin": sum(c["n_multi_origin"] for c in ok),
        "multi_origin_cells": [{"eval": c["eval"], "n": c["n_multi_origin"],
                                "source_tile_in_file": c["source_tile_in_file"]}
                               for c in ok if c["n_multi_origin"]],
        "all_columns": {
            "n_cells_affected": sum(1 for c in ok if c["n_affected_all_columns"]),
            "n_detections_affected": sum(c["n_affected_all_columns"] for c in ok),
            "n_cells_with_multi_origin": sum(
                1 for c in ok if c["n_multi_origin_all_columns"]),
            "n_detections_multi_origin": sum(c["n_multi_origin_all_columns"] for c in ok),
        },
        "written_source_tile_with_origin": {
            "n_cells": sum(1 for c in ok if True in c["source_tile_in_file"]
                           and c["origin_columns"]),
            "n_detections": sum(c["n_detections"] for c in ok
                                if True in c["source_tile_in_file"]
                                and c["origin_columns"]),
        },
        "stuck_cells": [{"eval": c["eval"], "n_stuck": c["n_stuck"],
                         "n_detections": c["n_detections"]}
                        for c in ok if c["n_stuck"]],
        "affected_by_family": dict(Counter(c.get("family") for c in affected)),
        "affected_by_status": dict(Counter(c.get("status") for c in affected)),
        "affected_source_tile_in_file": dict(Counter(
            str(c["source_tile_in_file"]) for c in affected)),
        "affected_origin_columns": dict(Counter(
            "|".join(c["origin_columns"]) for c in affected)),
        "affected_also_d50_origin_restored": sum(
            1 for r in cells if r.get("d50_origin_restored")),
        "check_counter_equals_census": not counter_mismatch,
        "check_counter_mismatches": counter_mismatch[:20],
        "check_out_of_frame_falls_by_count": not oof_mismatch,
        "check_out_of_frame_mismatches": oof_mismatch[:20],
        "n_affected_scored": len(scored),
        "n_a_reproduces_d50": sum(1 for r in scored if r.get("a_reproduces_d50")),
        "a_not_reproducing_d50": [r["eval"] for r in scored if not r.get("a_reproduces_d50")],
        "n_moved_ge_0.001": len(moved),
        "n_moved_f1_20_ge_0.001": sum(1 for x in f1_20 if abs(x) >= MOVE),
        "f1_20_delta": {
            "n_positive": sum(1 for x in f1_20 if x > 0),
            "n_negative": sum(1 for x in f1_20 if x < 0),
            "n_zero": sum(1 for x in f1_20 if x == 0),
            "min": min(f1_20, default=None), "max": max(f1_20, default=None),
        },
        "largest": None if largest is None else {
            "eval": largest["eval"], "max_abs": largest["delta_b_minus_a"]["max_abs"],
            "delta": largest["delta_b_minus_a"], "conditions": largest["conditions"]},
        "n_registered_moved": len(registered),
        "registered_moved": [{
            "eval": r["eval"], "conditions": r["conditions"], "analyses": r["analyses"],
            "n_affected": r["n_affected"],
            "f1_20_a": r["a"]["per_buffer"].get("20", {}).get("f1"),
            "f1_20_b": r["b"]["per_buffer"].get("20", {}).get("f1"),
            "delta": r["delta_b_minus_a"],
        } for r in registered],
        "analyses_moved": sorted({a for r in registered for a in r["analyses"].split(";")
                                  if a}),
        "end_to_end": end_to_end,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"summary": summary, "cells": cells}, indent=1,
                                   default=str))
    with (args.out.with_suffix(".csv")).open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["eval", "family", "conditions", "analyses", "n_detections",
                    "n_affected", "f1_20_a", "f1_20_b", "d_f1_20", "d_p_20", "d_r_20",
                    "d_mcc", "max_abs"])
        for r in sorted(scored, key=lambda r: -r["delta_b_minus_a"]["max_abs"]):
            d20 = r["delta_b_minus_a"]["per_buffer"].get("20", {})
            w.writerow([r["eval"], r["family"], r["conditions"], r["analyses"],
                        r["n_detections"], r["n_affected"],
                        r["a"]["per_buffer"].get("20", {}).get("f1"),
                        r["b"]["per_buffer"].get("20", {}).get("f1"),
                        d20.get("f1"), d20.get("precision"), d20.get("recall"),
                        r["delta_b_minus_a"]["mcc"], r["delta_b_minus_a"]["max_abs"]])
    print(json.dumps(summary, indent=1, default=str)[:6000])
    return 0


def main() -> int:
    """Parse the subcommand and run it."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe")
    p.add_argument("--code", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    for name in ("census", "score"):
        p = sub.add_parser(name)
        p.add_argument("--code", type=Path, required=True)
        p.add_argument("--data", type=Path, required=True)
        p.add_argument("--rows", type=Path, nargs="+", required=True)
        p.add_argument("--out", type=Path, required=True)
        p.add_argument("--workers", type=int, default=20)
        if name == "score":
            p.add_argument("--census", type=Path, required=True)
    p = sub.add_parser("sweeps")
    p.add_argument("--code", type=Path, required=True)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--jobs", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("summarise")
    for flag in ("--census", "--scores-a", "--scores-b", "--d50-rows", "--cells", "--out"):
        p.add_argument(flag, type=Path, required=True)
    args = ap.parse_args()
    return {"probe": cmd_probe, "census": cmd_census, "score": cmd_score,
            "sweeps": cmd_sweeps, "summarise": cmd_summarise}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
