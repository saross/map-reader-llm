"""Shared helpers for the frames blast-radius re-scoring (2026-10-07, Session 163).

Purpose
-------
The project's point scorer ``calculate_f1_internal`` (``scripts/lib_advanced_metrics.py``)
scopes REFERENCES geometrically (per map, a reference must intersect one of that map's tile
polygons, via ``scope_references_to_tiles``) but scopes DETECTIONS by map name only (every
detection whose ``source_tile`` starts with the map name is kept). This module supplies a
*wrapper* that gives detections the reference rule, without editing any library code:

* :func:`geometric_detection_scope` drops exactly those detections that the per-map
  reference rule would drop: a detection whose ``source_tile`` begins with frame map ``M``
  is kept only if it intersects at least one of ``M``'s tile polygons. It calls the
  library's own ``scope_references_to_tiles`` on the detections, so the tile geometries,
  the predicate (``intersects``) and the coordinate reference system (CRS) handling are
  the reference side's, by construction. Detections that the library already ignores
  (null ``source_tile``, or a name on no frame map) are left in place untouched, so the
  wrapper changes nothing but the defect under study.
* :func:`patched_scorers` is a context manager that monkeypatches
  ``calculate_f1_internal``, ``calculate_tile_classification`` and
  ``compute_per_tile_tp_fp_fn`` in every already-imported module namespace, so an
  unmodified sweep or tiering script runs with the geometric detection scope. It also
  supports a deliberately broken *red sentinel* mode (scope to an empty frame).

Everything here is read-only with respect to the repository: run with
``PYTHONDONTWRITEBYTECODE=1`` so no ``__pycache__`` lands in the checkout.

Usage (library)::

    import blast_lib as bl
    bl.add_repo_to_path(Path("~/Code/map-reader-llm").expanduser())
    det = bl.load_detections(path, bounds)
    scoped, diag = bl.geometric_detection_scope(det, bounds)
"""

from __future__ import annotations

import contextlib
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd

#: Evaluation CRS used by every project scorer (UTM zone 35N).
EVAL_CRS = "EPSG:32635"

#: Populated by :func:`add_repo_to_path`; the imported library module.
LIB: Any = None


def add_repo_to_path(repo: Path) -> None:
    """Make ``scripts.*`` importable from the read-only checkout and import the library.

    Args:
        repo: Repository root (the checkout is read, never written).
    """
    global LIB
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    import scripts.lib_advanced_metrics as lam  # noqa: PLC0415

    LIB = lam


def load_geojson(path: Path) -> gpd.GeoDataFrame:
    """Load a GeoJSON exactly as ``evaluate_detections.load_geojson`` does.

    Args:
        path: GeoJSON path.

    Returns:
        GeoDataFrame in :data:`EVAL_CRS` (set when the file has no CRS, reprojected otherwise).
    """
    gdf = gpd.read_file(path)
    if gdf.empty:
        return gdf
    if gdf.crs is None:
        gdf = gdf.set_crs(EVAL_CRS)
    elif str(gdf.crs) != EVAL_CRS:
        gdf = gdf.to_crs(EVAL_CRS)
    return gdf


def load_detections(path: Path, gdf_bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Load a detection file the way ``evaluate_detections._evaluate_condition`` does.

    When the file carries no ``source_tile`` column, the evaluator assigns one by a left
    ``intersects`` spatial join to the frame, keeping the first tile per detection; a
    detection outside the frame therefore receives a null ``source_tile`` and drops out of
    the per-map scope. The same is reproduced here so that OFF scores match the committed
    ones, and the returned frame records whether the column was synthesised.

    Args:
        path: Detection GeoJSON.
        gdf_bounds: Frame tile polygons (``tile_name`` column), in :data:`EVAL_CRS`.

    Returns:
        Detections with a unique RangeIndex and a ``source_tile`` column; ``attrs`` carries
        ``source_tile_synthesised`` (bool).
    """
    gdf = load_geojson(path)
    synthesised = False
    if "source_tile" not in gdf.columns and not gdf.empty:
        joined = gpd.sjoin(
            gdf, gdf_bounds[["tile_name", "geometry"]], how="left", predicate="intersects",
        )
        joined = joined[~joined.index.duplicated(keep="first")]
        gdf["source_tile"] = joined["tile_name"]
        synthesised = True
    gdf = gdf.reset_index(drop=True)
    gdf.attrs["source_tile_synthesised"] = synthesised
    return gdf


def frame_maps(gdf_bounds: gpd.GeoDataFrame) -> list[str]:
    """Return the frame's map names exactly as ``calculate_f1_internal`` derives them.

    Args:
        gdf_bounds: Frame tile polygons.

    Returns:
        Sorted map names, ``"Unknown"`` excluded (the scorer skips it).
    """
    names = {LIB.get_map_name(n) for n in gdf_bounds["tile_name"].unique()}
    names.discard("Unknown")
    return sorted(names)


def _prefix_mask(src: pd.Series, map_name: str) -> pd.Series:
    """Boolean mask of ``src.str.startswith(map_name)`` with nulls as False.

    pandas 3 already returns False on nulls; the explicit fill keeps the helper correct on
    older pandas too, matching how the library's mask behaves on the sapphire venv.
    """
    if src.empty:
        return pd.Series(False, index=src.index)
    return src.astype("object").where(src.notna(), None).map(
        lambda v: isinstance(v, str) and v.startswith(map_name)
    ).astype(bool)


def geometric_detection_scope(
    gdf_det: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    *,
    sentinel_empty: bool = False,
) -> tuple[gpd.GeoDataFrame, dict[str, int]]:
    """Apply the reference-side scope rule to detections and report what it removes.

    For every frame map ``M`` the library keeps detections whose ``source_tile`` starts with
    ``M``. Here, those detections are additionally required to intersect one of ``M``'s tile
    polygons, using the library's own ``scope_references_to_tiles`` (per-tile ``sjoin``,
    ``intersects``). Detections the library ignores anyway (no frame-map prefix, including a
    null ``source_tile``) are kept unchanged, so the only rows removed are the ones the
    defect books.

    Args:
        gdf_det: Detections with a unique index and a ``source_tile`` column, in
            :data:`EVAL_CRS`.
        gdf_bounds: Frame tile polygons, in :data:`EVAL_CRS`.
        sentinel_empty: Red sentinel. Scope every prefix-matched detection to an EMPTY tile
            set, so every one of them is dropped. Used only to prove the wrapper is live.

    Returns:
        ``(scoped_detections, diagnostics)``. Diagnostics (all counts of detections):
        ``n_total``; ``n_null_source_tile``; ``n_prefix_scoped`` (the library's per-map
        scope); ``n_out_of_frame`` (prefix-scoped but outside every tile of its own map:
        the rows removed); ``n_out_cross_map`` (of those, inside another frame map's
        tiles); ``n_null_in_frame`` (null ``source_tile`` but inside the frame union, which
        the library silently drops); ``n_unprefixed_in_frame`` (non-null name on no frame
        map but inside the union); ``n_multi_prefix`` (a name matching two map prefixes).
    """
    n = len(gdf_det)
    diag = {
        "n_total": n, "n_null_source_tile": 0, "n_prefix_scoped": 0, "n_out_of_frame": 0,
        "n_out_cross_map": 0, "n_null_in_frame": 0, "n_unprefixed_in_frame": 0,
        "n_multi_prefix": 0,
    }
    if n == 0:
        return gdf_det, diag
    if not gdf_det.index.is_unique:
        raise ValueError("detections need a unique index")
    src = gdf_det["source_tile"] if "source_tile" in gdf_det.columns else pd.Series(
        [None] * n, index=gdf_det.index,
    )
    null = src.isna() | (src.astype("object").map(lambda v: v == ""))
    prefix_any = pd.Series(False, index=gdf_det.index)
    prefix_hits = pd.Series(0, index=gdf_det.index)
    in_own = pd.Series(False, index=gdf_det.index)
    empty_bounds = gdf_bounds.iloc[0:0]
    for map_name in frame_maps(gdf_bounds):
        pm = _prefix_mask(src, map_name)
        prefix_hits = prefix_hits + pm.astype(int)
        if not pm.any():
            continue
        prefix_any |= pm
        map_bounds = gdf_bounds[gdf_bounds["tile_name"].str.startswith(map_name)]
        scoped = LIB.scope_references_to_tiles(
            gdf_det[pm], empty_bounds if sentinel_empty else map_bounds,
        )
        in_own.loc[scoped.index] = True
    drop = prefix_any & ~in_own
    # Union membership, for the diagnostics only (never used to decide a drop).
    in_union_idx = set(
        gpd.sjoin(
            gdf_det[["geometry"]], gdf_bounds[["tile_name", "geometry"]],
            how="inner", predicate="intersects",
        ).index
    )
    in_union = pd.Series(gdf_det.index.isin(list(in_union_idx)), index=gdf_det.index)
    diag.update({
        "n_null_source_tile": int(null.sum()),
        "n_prefix_scoped": int(prefix_any.sum()),
        "n_out_of_frame": int(drop.sum()),
        "n_out_cross_map": int((drop & in_union).sum()),
        "n_null_in_frame": int((null & in_union).sum()),
        "n_unprefixed_in_frame": int((~null & ~prefix_any & in_union).sum()),
        "n_multi_prefix": int((prefix_hits > 1).sum()),
    })
    return gdf_det[~drop].copy(), diag


def mcc_of(tile_class: dict[str, Any]) -> tuple[float | None, str | None]:
    """Extract (MCC, refusal reason) from a ``calculate_tile_classification`` result."""
    if "error" in tile_class:
        return None, str(tile_class.get("reason"))
    mcc = tile_class.get("mcc")
    return (None if mcc is None else float(mcc)), None


def score_point(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
    *,
    want_mcc: bool,
    tile_join: str,
) -> dict[str, Any]:
    """Point F1, precision and recall per buffer, plus tile MCC, as ``evaluate_single_run``.

    Mirrors ``evaluate_detections.evaluate_single_run``'s point estimates: zero metrics for
    an empty detection set, ``calculate_f1_internal`` per buffer, and
    ``calculate_tile_classification`` with the cell's recorded tile join for MCC.

    Args:
        gdf_det: Detections (already scoped or not, per the caller).
        gdf_ref: References.
        gdf_bounds: Frame tiles.
        buffers: Match radii in metres.
        want_mcc: Whether to compute tile MCC.
        tile_join: The cell's tile join (``id`` unless recorded otherwise).

    Returns:
        ``{"per_buffer": {b: {"f1", "precision", "recall"}}, "mcc", "mcc_refused"}``.
    """
    out: dict[str, Any] = {"per_buffer": {}, "mcc": None, "mcc_refused": None}
    for b in buffers:
        if len(gdf_det) == 0:
            out["per_buffer"][b] = {"f1": 0.0, "precision": 0.0, "recall": 0.0}
            continue
        p, r, f = LIB.calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_metres=b)
        out["per_buffer"][b] = {"f1": float(f), "precision": float(p), "recall": float(r)}
    if want_mcc and len(gdf_det) > 0:
        tc = LIB.calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds, tile_join=tile_join)
        out["mcc"], out["mcc_refused"] = mcc_of(tc)
    return out


@contextlib.contextmanager
def patched_scorers(mode: str = "geometric") -> Iterator[dict[str, int]]:
    """Monkeypatch the library scorers in every loaded module to pre-scope detections.

    Replaces ``calculate_f1_internal``, ``calculate_tile_classification`` and
    ``compute_per_tile_tp_fp_fn`` wherever a loaded module holds a reference to the
    library's original function (``from ... import`` copies included), so unmodified
    project scripts (sweeps, tiering) run with the geometric detection scope. The
    originals are restored on exit.

    Args:
        mode: ``"geometric"`` (the wrapper) or ``"sentinel"`` (red sentinel: every
            prefix-matched detection scoped to an empty tile set).

    Yields:
        A counter dict, ``{"calls": int, "dropped": int}``, accumulated over all calls.
    """
    counter = {"calls": 0, "dropped": 0}
    names = ("calculate_f1_internal", "calculate_tile_classification",
             "compute_per_tile_tp_fp_fn")
    originals = {name: getattr(LIB, name) for name in names}

    def make(name: str) -> Any:
        orig = originals[name]

        def wrapped(gdf_det: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
                    gdf_bounds: gpd.GeoDataFrame, *args: Any, **kwargs: Any) -> Any:
            det = gdf_det
            if not det.index.is_unique:
                det = det.reset_index(drop=True)
            scoped, diag = geometric_detection_scope(
                det, gdf_bounds, sentinel_empty=(mode == "sentinel"),
            )
            counter["calls"] += 1
            counter["dropped"] += diag["n_out_of_frame"]
            return orig(scoped, gdf_ref, gdf_bounds, *args, **kwargs)

        wrapped.__name__ = f"geo_scoped_{name}"
        return wrapped

    replacements = {name: make(name) for name in names}
    patched: list[tuple[Any, str, Any]] = []
    for mod in list(sys.modules.values()):
        if mod is None:
            continue
        for name in names:
            try:
                current = getattr(mod, name, None)
            except Exception:  # noqa: BLE001 - exotic modules may raise on getattr
                continue
            if current is originals[name]:
                patched.append((mod, name, current))
                setattr(mod, name, replacements[name])
    try:
        yield counter
    finally:
        for mod, name, current in patched:
            setattr(mod, name, current)
