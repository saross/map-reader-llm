"""Task C, D57 (2): what the D51 clip costs the refused pv-diag-384 ladders.

The PI's question (ruling D57 (2)): clipping a ladder's larger-area rungs to
the common area while keeping the frame's reference set (D51 option 1)
"seems to lower F1 by building in 'misses' -- how severe is that effect?"

For every pv-diag-384 ladder the D51 gate refuses once Tasks A and B have
made its rungs determinable (the 3.7 GS ladder, already measured under D51,
is excluded), each rung is scored at its committed points (the opmax point
the ladder reports and its stride-shell carried point), on the board frame
(``era2_b_intersection_bounds``), at 20 m, with the branch's scorer
(D50 scoping), three ways:

(i)   ``unclipped`` — the rung's committed detections, as committed;
(ii)  ``clipped`` — detections outside the ladder's common assessed area
      removed, the frame and its reference set kept (D51 option 1, what
      ``build_k_ladder_phase2_tables.py --clip-to-common-area
      --allow-undetermined-area`` computes);
(iii) ``gap_removed`` — sensitivity: the gap removed from the frame itself,
      detections and references alike (every frame tile polygon intersected
      with the common area, detections clipped as in (ii)).

Per rung it records F1, precision, recall and tile MCC (tile join ``id``,
the evaluator's default), TP / FP / FN, how many board reference mounds lie
in the ladder's gap (the frame minus the common area), how many of them the
rung found in (i), how many of its false positives lie in the gap, and the
PI's estimate: each lost gap mound costs about (2 − F1) / (2TP + FP + FN)
and each removed gap false positive gains about F1 / (2TP + FP + FN).

Usage (sapphire; writes only to --out)::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python clip_cost.py \
        --code ~/worktrees/map-reader-llm/claude-d51-ladder-provenance \
        --survey out/gate_survey.json --out out/clip_cost.json

Created: 2026-10-08 (D57 (2), Session 163 follow-up)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import geopandas as gpd

BUFFER_M = 20
EXCLUDED = {"g384_ov192_g37"}  # measured under D51 already (PR #26 § 5.3)


def polygonal(geometry: Any) -> Any:
    """The polygonal part of an intersection (edge contacts dropped)."""
    from shapely.geometry import GeometryCollection, MultiPolygon, Polygon  # noqa: PLC0415

    if isinstance(geometry, (Polygon, MultiPolygon)):
        return geometry
    parts = [g for g in getattr(geometry, "geoms", []) if isinstance(g, Polygon)]
    return MultiPolygon(parts) if parts else GeometryCollection()


def frame_references(lam: Any, ref: gpd.GeoDataFrame,
                     bounds: gpd.GeoDataFrame) -> list[gpd.GeoDataFrame]:
    """The frame's references per sheet, scoped as ``iter_sheet_scopes`` scopes them."""
    column = lam.reference_map_column(ref)
    out = []
    for sheet in lam.frame_sheets(bounds):
        sheet_bounds = bounds[bounds["tile_name"].str.startswith(sheet)]
        rows = ref[ref[column] == sheet]
        if not rows.empty:
            out.append(lam.scope_references_to_tiles(rows, sheet_bounds))
    return out


def counts(lam: Any, det: gpd.GeoDataFrame, ref: gpd.GeoDataFrame,
           bounds: gpd.GeoDataFrame) -> dict[str, Any]:
    """TP / FP / FN and the matched geometry, by the scorer's own per-sheet loop.

    Replicates ``lib_advanced_metrics.calculate_f1_internal`` (the same
    ``iter_sheet_scopes`` and ``match_detections_to_references``) but keeps
    which references were matched and which detections were not, so gap
    mounds found and gap false positives can be counted.
    """
    tp = fp = fn = 0
    matched_refs, matched_dets, unmatched_dets = [], [], []
    if len(det) == 0:
        n_ref = sum(len(r) for r in frame_references(lam, ref, bounds))
        return {"tp": 0, "fp": 0, "fn": n_ref, "matched_refs": [], "matched_dets": [],
                "unmatched_dets": []}
    for _sheet, d, r, _b in lam.iter_sheet_scopes(det, ref, bounds):
        if d.empty and r.empty:
            continue
        if d.empty:
            fn += len(r)
            continue
        if r.empty:
            fp += len(d)
            unmatched_dets += list(d.geometry)
            continue
        dg, rg = list(d.geometry), list(r.geometry)
        md, mr, ud, ur = lam.match_detections_to_references(dg, rg, BUFFER_M)
        tp += len(md)
        fp += len(ud)
        fn += len(ur)
        matched_refs += [rg[i] for i in mr]
        matched_dets += [dg[i] for i in md]
        unmatched_dets += [dg[i] for i in ud]
    return {"tp": tp, "fp": fp, "fn": fn, "matched_refs": matched_refs,
            "matched_dets": matched_dets, "unmatched_dets": unmatched_dets}


def score(lam: Any, det: gpd.GeoDataFrame, ref: gpd.GeoDataFrame,
          bounds: gpd.GeoDataFrame, gap: Any, gap_tiles: list[str]) -> dict[str, Any]:
    """F1 / P / R / tile MCC and the gap counts for one detection set.

    ``gap_tile_confusion`` records how the tile confusion classed each tile
    that holds part of the gap (its reference and detection counts), so a
    tile-MCC move, or its absence, can be traced to those tiles.
    """
    c = counts(lam, det, ref, bounds)
    tp, fp, fn = c["tp"], c["fp"], c["fn"]
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    # Sanity: the scorer's own function must agree with the counts.
    if len(det):
        p2, r2, f2 = lam.calculate_f1_internal(det, ref, bounds, buffer_metres=BUFFER_M)
        if abs(f2 - f1) > 1e-12 or abs(p2 - p) > 1e-12 or abs(r2 - r) > 1e-12:
            raise SystemExit("counts disagree with calculate_f1_internal")
    mcc = None
    gap_confusion = []
    if len(det):
        tc = lam.calculate_tile_classification(det, ref, bounds, tile_join="id")
        mcc = None if "error" in tc else tc.get("mcc")
        gap_confusion = [{k: t[k] for k in ("tile_name", "n_references", "n_detections",
                                            "classification")}
                         for t in tc.get("tile_details", []) if t["tile_name"] in gap_tiles]
    denom = 2 * tp + fp + fn
    return {
        "f1": f1, "precision": p, "recall": r, "tile_mcc": mcc,
        "tp": tp, "fp": fp, "fn": fn, "n_detections": len(det), "denominator": denom,
        "gap_mounds_found": sum(1 for g in c["matched_refs"] if g.intersects(gap)),
        "gap_tp_detections": sum(1 for g in c["matched_dets"] if g.intersects(gap)),
        "gap_fp_detections": sum(1 for g in c["unmatched_dets"] if g.intersects(gap)),
        "gap_tile_confusion": gap_confusion,
    }


def main() -> int:
    """Score every refused ladder's rungs three ways and write the table."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--survey", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    code = args.code.expanduser().resolve()
    sys.path.insert(0, str(code))
    sys.path.insert(0, str(code / "reports" / "scorer-frames-d50-d51-2026-10-08-scripts"))
    import meas_lib as ml  # noqa: PLC0415

    ml.setup(code)
    lam = ml.LIB
    import scripts.build_k_ladder_phase2_tables as tables  # noqa: PLC0415
    import scripts.lib_assessed_area as laa  # noqa: PLC0415

    survey = json.loads(args.survey.read_text())["after"]
    refused = [s["pool"] for s in survey if s["status"] == "refused"
               and s["pool"] not in EXCLUDED]
    payload = tables.build()
    out: dict[str, Any] = {"buffer_m": BUFFER_M, "ladders": []}
    for ladder in payload["ladders"]:
        if ladder["proposer_pool"] not in refused:
            continue
        frame_path = ladder["frame_file"]
        bounds = ml.load_geojson(code / frame_path)
        ref = ml.load_geojson(code / ladder["reference_file"])
        areas = [laa.determine_assessed_area(r["pool"], label=f"K = {r['K']}")
                 for r in ladder["rungs"]]
        comparison = laa.compare_assessed_areas(areas, frame=frame_path,
                                                clip_to_common=True,
                                                allow_undetermined=True)
        common = comparison.common
        frame = laa.frame_union(frame_path)
        gap = frame.difference(common)
        # The sensitivity frame: every tile polygon intersected with the common area.
        shrunk = bounds.copy()
        shrunk["geometry"] = [polygonal(g.intersection(common)) for g in shrunk.geometry]
        shrunk = shrunk[~shrunk.geometry.is_empty]
        gap_refs = sum(int(r.geometry.intersects(gap).sum())
                       for r in frame_references(lam, ref, bounds))
        gap_tiles = sorted(set(bounds[bounds.geometry.intersects(gap) & (
            bounds.geometry.intersection(gap).area > 1.0)]["tile_name"]))
        entry: dict[str, Any] = {
            "pool": ladder["proposer_pool"], "family": ladder["family"],
            "gate_status": comparison.status,
            "common_area_km2": comparison.record["common_area_km2"],
            "gap_km2": round(gap.area / 1e6, 4), "gap_tiles": gap_tiles,
            "gap_reference_mounds": gap_refs,
            "area_removed_km2": (comparison.record.get("clip") or {}).get("area_removed_km2"),
            "rungs": [],
        }
        for rung in ladder["rungs"]:
            points = {"opmax": rung["opmax"]}
            shell = (rung.get("carried") or {}).get("stride-shell")
            if shell and shell.get("eval_path") != rung["opmax"].get("eval_path"):
                points["carried-stride-shell"] = shell
            row: dict[str, Any] = {"K": rung["K"], "points": {}}
            for label, point in points.items():
                ev = json.loads((code / point["eval_path"]).read_text())
                dets = (ev["_metadata"].get("input_files") or {}).get("detections")
                dets = dets if isinstance(dets, list) else [dets]
                if len(dets) != 1:
                    raise SystemExit(f"{point['eval_path']}: {len(dets)} detection files")
                det = ml.load_detections(ml.resolve(code, dets[0]), bounds)
                clipped, removed = laa.clip_points_to_area(det, common)
                committed = next((b.get("f1") for b in ev["summary"]["buffers"]
                                  if b.get("buffer_metres") == BUFFER_M), None)
                i = score(lam, det, ref, bounds, gap, gap_tiles)
                ii = score(lam, clipped, ref, bounds, gap, gap_tiles)
                iii = score(lam, clipped, ref, shrunk, gap, gap_tiles)
                d = i["denominator"]
                estimate = {
                    "per_lost_mound": (2 - i["f1"]) / d if d else None,
                    "per_removed_fp": i["f1"] / d if d else None,
                    "linear_delta_f1": ((-i["gap_tp_detections"] * (2 - i["f1"])
                                         + i["gap_fp_detections"] * i["f1"]) / d)
                    if d else None,
                }
                row["points"][label] = {
                    "vote_t": point.get("vote_t"), "prob_t": point.get("prob_t"),
                    "eval_path": point["eval_path"], "committed_f1_20": committed,
                    "detections_removed_by_clip": removed,
                    "unclipped": i, "clipped": ii, "gap_removed": iii,
                    "estimate": estimate,
                }
                print(ladder["proposer_pool"], rung["K"], label,
                      round(i["f1"], 4), round(ii["f1"], 4), round(iii["f1"], 4),
                      i["gap_mounds_found"], flush=True)
            entry["rungs"].append(row)
        out["ladders"].append(entry)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
