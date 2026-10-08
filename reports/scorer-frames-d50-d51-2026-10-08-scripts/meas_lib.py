"""Shared helpers for the D50/D51 impact measurement (2026-10-08, Session 163).

Purpose
-------
The measurement scores committed cells with the NEW scorer (branch
``scorer-frames-d50-d51``) and compares the result with the two baselines the
frames blast-radius report recorded for every cell
(``reports/frames-blast-radius-2026-10-07.md``): OFF (the scorer on ``main``)
and ON (the same scorer with the report's geometric-scope wrapper). It never
writes to a repository: CODE is imported from the branch worktree, DATA is
read from a checkout of ``main`` (where the gitignored inputs live), and every
output goes to the scratch ``--out`` path.

The loaders replicate ``scripts/evaluate_detections.py`` exactly (CRS
handling, and the ``source_tile`` spatial join when the column is absent), as
the blast-radius wrapper did, so a cell's NEW and OFF numbers differ only by
the scorer.

Usage (library)::

    import meas_lib as ml
    ml.setup(code_repo=Path("~/worktrees/.../claude-scorer-d50"))
    det = ml.load_detections(path, bounds)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import geopandas as gpd

#: Evaluation CRS used by every project scorer (UTM zone 35N).
EVAL_CRS = "EPSG:32635"

#: The NEW library module, set by :func:`setup`.
LIB: Any = None


def setup(code_repo: Path) -> None:
    """Import the NEW scorer from the branch worktree.

    Args:
        code_repo: Root of the ``scorer-frames-d50-d51`` worktree.
    """
    global LIB
    root = str(code_repo.expanduser().resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    import scripts.lib_advanced_metrics as lam  # noqa: PLC0415

    if not hasattr(lam, "scope_detections_to_frame"):
        raise RuntimeError(f"{lam.__file__} is not the D50 scorer")
    LIB = lam


def resolve(data_repo: Path, path: str) -> Path:
    """Resolve a recorded path (repository-relative, absolute or frozen) in the data repo."""
    if "/frozen/" in path:
        path = path.split("/frozen/", 1)[1]
    p = Path(path)
    return p if p.is_absolute() else data_repo / p


def load_geojson(path: Path) -> gpd.GeoDataFrame:
    """Load a GeoJSON exactly as ``evaluate_detections.load_geojson`` does."""
    gdf = gpd.read_file(path)
    if gdf.empty:
        return gdf
    if gdf.crs is None:
        return gdf.set_crs(EVAL_CRS)
    if str(gdf.crs) != EVAL_CRS:
        return gdf.to_crs(EVAL_CRS)
    return gdf


def load_detections(path: Path, gdf_bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Load detections as ``evaluate_detections._evaluate_condition`` does.

    When the file has no ``source_tile`` column the evaluator assigns one by a
    left ``intersects`` spatial join to the frame (first tile per detection).
    """
    gdf = load_geojson(path)
    if "source_tile" not in gdf.columns and not gdf.empty:
        joined = gpd.sjoin(gdf, gdf_bounds[["tile_name", "geometry"]], how="left",
                           predicate="intersects")
        joined = joined[~joined.index.duplicated(keep="first")]
        gdf["source_tile"] = joined["tile_name"]
    return gdf


def score_point(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
    *,
    want_mcc: bool,
    tile_join: str,
) -> dict[str, Any]:
    """Point F1, P, R per buffer and tile MCC with the NEW scorer.

    Mirrors ``evaluate_detections.evaluate_single_run``'s point estimates (and
    the blast-radius ``score_point``): zeros for an empty set,
    ``calculate_f1_internal`` per buffer, ``calculate_tile_classification``
    with the cell's recorded tile join for MCC.
    """
    out: dict[str, Any] = {"per_buffer": {}, "mcc": None, "mcc_refused": None}
    for b in buffers:
        if len(gdf_det) == 0:
            out["per_buffer"][str(b)] = {"f1": 0.0, "precision": 0.0, "recall": 0.0}
            continue
        p, r, f = LIB.calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_metres=b)
        out["per_buffer"][str(b)] = {"f1": float(f), "precision": float(p),
                                     "recall": float(r)}
    if want_mcc and len(gdf_det) > 0:
        tc = LIB.calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds,
                                               tile_join=tile_join)
        if "error" in tc:
            out["mcc_refused"] = str(tc.get("reason"))
        else:
            out["mcc"] = None if tc.get("mcc") is None else float(tc["mcc"])
    return out


def mean_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Average per-run point estimates as ``evaluate_multi_run_mean`` does."""
    if len(runs) == 1:
        return runs[0]
    buffers = list(runs[0]["per_buffer"])
    out: dict[str, Any] = {"per_buffer": {
        b: {m: sum(r["per_buffer"][b][m] for r in runs) / len(runs)
            for m in ("f1", "precision", "recall")}
        for b in buffers
    }}
    defined = [r["mcc"] for r in runs if r["mcc"] is not None]
    out["mcc"] = sum(defined) / len(defined) if defined else None
    out["mcc_refused"] = next((r["mcc_refused"] for r in runs if r["mcc_refused"]), None)
    return out


def sum_diagnostics(blocks: list[dict[str, Any]]) -> dict[str, int]:
    """Sum the integer counts of several ``detection_scope`` blocks."""
    keys = ("n_detections", "n_in_scope", "n_out_of_frame", "n_out_of_frame_cross_sheet",
            "n_origin_restored", "n_origin_only", "n_origin_unrecognised",
            "n_unattributed", "n_unattributed_in_frame")
    return {k: int(sum(int(b.get(k) or 0) for b in blocks)) for k in keys}
