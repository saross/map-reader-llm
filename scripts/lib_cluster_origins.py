#!/usr/bin/env python3
"""
Carry each consensus cluster's contributing tiles into scoring (PI ruling D62 (1)).

**Why this module exists.** Ruling D50 (2026-10-07) stopped the shared scorer
from re-keying a detection across a sheet edge:
:func:`scripts.lib_advanced_metrics.assign_primary_tiles_on_origin_sheet`
chooses a detection's frame tile only among the tiles of the sheets the
detection was SEEN on (its *origin*). A row with no recorded origin keeps the
legacy rule, the nearest tile centroid among ALL frame tiles. Where two
sheets' padded tiles overlap, that tile can belong to the neighbouring sheet,
and the per-sheet matcher then scores the detection against the wrong sheet's
references (``reports/frames-blast-radius-2026-10-07.md`` § 5.4).

The gold-standard (GS) grid, stride, plateau, and Image-B chains cluster their
deduplicated passes with ``h13_k_sensitivity.cluster_votes``, which returns
bare centroids and vote counts, so no origin reached that function
(``reports/s163-agent-records/scorer-restatement-inventory.md`` § 3). This
module supplies the missing link without touching ``cluster_votes`` (another
workstream owns the H13 chain):

* :func:`cluster_votes_with_members` runs the same greedy star clustering as
  ``cluster_votes`` (identical centroids and votes, pinned by a tier-1 test)
  and also returns each cluster's member tiles: the union of its members'
  recorded ``source_tiles``.
* :func:`tile_on_origin` wraps points with their origin, tiles each on its
  origin sheet, and drops the rows that lie on no tile of their own sheet
  (the rows the D50 scorer removes as out of frame).
* :func:`attach_union_origins` serves the committed K-pass unions, the
  verifier inputs, which record no members. It rebuilds their clusters from
  the same passes, gates the rebuild against the committed file row for row
  (count, votes, geometry), and attaches the members to the committed rows,
  so the verifier probabilities keyed by row index stay joined.
* :func:`recorded_origin` serves sets that record their own ``source_tile``
  (the plateau's four incumbents): the recorded tile is kept as the origin
  rather than discarded.

* :func:`union_on_origin` is the one call a verified-union loader makes:
  attach, then re-tile.

Usage::

    from scripts.lib_cluster_origins import (
        cluster_votes_with_members, points_on_origin, union_on_origin,
    )
    centroids, votes, members = cluster_votes_with_members(passes, 1)
    frame, diag = points_on_origin(centroids, bounds, members, "EPSG:32635")
    union = union_on_origin(union, passes, bounds, label="g384_ov192",
                            n_passes=10)

Created: 2026-10-13 (Session 163, workstream ``origin-gap-grid-plateau``)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.h13_k_sensitivity import DEDUP_M  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    assign_primary_tiles_on_origin_sheet,
    parse_tile_list,
)

logger = logging.getLogger(__name__)

#: The column a scored frame carries its recorded origin in. ``origin_tiles``
#: is one of ``lib_advanced_metrics.ORIGIN_TILE_COLUMNS``, so the shared
#: scorer's ``scope_detections_to_frame`` reads it too; a ``;``-joined string
#: is the serialisation h13's prepared passes already use.
ORIGIN_COLUMN = "origin_tiles"

#: Largest centroid displacement (metres) a committed union may show against
#: its rebuild. The unions round-trip through EPSG:4326 GeoJSON; the measured
#: displacement on the grid, stride, and image unions is below a micrometre
#: (2026-10-13), so a millimetre separates a round trip from a different
#: clustering by orders of magnitude.
UNION_GEOMETRY_TOL_M = 1e-3


class OriginGateError(RuntimeError):
    """A rebuilt union does not reproduce the committed one; nothing may be scored."""


def member_tiles(detection: dict[str, Any]) -> list[str]:
    """Return one deduplicated detection's recorded proposer tiles.

    ``grid_analysis.load_cell_passes`` stores them as ``source_tiles`` (the
    prepared pass's ``origin_tiles`` split on ``;``), so an unrecorded value
    arrives as ``[""]``; empties are dropped.

    Args:
        detection: One pass detection (the loaders' dict shape).

    Returns:
        Tile names, possibly empty.

    Example:
        >>> member_tiles({"source_tiles": ["K-1_x0_y0.png", ""]})
        ['K-1_x0_y0.png']
    """
    raw = detection.get("source_tiles") or []
    if isinstance(raw, str):
        raw = raw.split(";")
    return [str(t) for t in raw if t]


def cluster_votes_with_members(
    passes: list[list[dict[str, Any]]], min_corroboration: int,
) -> tuple[np.ndarray, np.ndarray, list[list[str]]]:
    """Cluster passes exactly as ``cluster_votes`` does, keeping member tiles.

    The loop is ``h13_k_sensitivity.cluster_votes`` statement for statement
    (greedy star clustering at ``DEDUP_M`` in input order, centroid = member
    mean, votes = distinct passes), so its centroids and votes are the
    committed ones; ``tests/test_lib_cluster_origins.py`` pins the equality.
    The only addition is the third return value.

    Args:
        passes: Deduplicated detections per pass (the loaders' dict shape:
            ``centroid``, ``cluster_size`` and, where recorded,
            ``source_tiles``).
        min_corroboration: Minimum within-pass ``cluster_size`` to keep.

    Returns:
        ``(centroids, votes, members)``: an ``(n, 2)`` array, an integer
        array of vote counts, and per cluster the sorted, distinct tiles its
        members were seen on (empty where no member recorded one).
    """
    pts: list[tuple[float, float]] = []
    owner: list[int] = []
    tiles: list[list[str]] = []
    for idx, dets in enumerate(passes):
        for d in dets:
            if d.get("cluster_size", 1) >= min_corroboration:
                pts.append(d["centroid"])
                owner.append(idx)
                tiles.append(member_tiles(d))
    n = len(pts)
    if n == 0:
        return np.zeros((0, 2)), np.zeros(0, dtype=int), []

    arr = np.asarray(pts, dtype=float)
    own = np.asarray(owner, dtype=int)
    taken = np.zeros(n, dtype=bool)
    centroids: list[tuple[float, float]] = []
    votes: list[int] = []
    members_out: list[list[str]] = []

    for i in range(n):
        if taken[i]:
            continue
        d = np.hypot(arr[:, 0] - arr[i, 0], arr[:, 1] - arr[i, 1])
        members = np.flatnonzero((d <= DEDUP_M) & ~taken)
        members = np.union1d(members, [i])
        taken[members] = True
        centroids.append((arr[members, 0].mean(), arr[members, 1].mean()))
        votes.append(len(set(own[members].tolist())))
        members_out.append(sorted({t for m in members.tolist() for t in tiles[m]}))

    return np.asarray(centroids), np.asarray(votes, dtype=int), members_out


def tile_on_origin(
    gdf: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
    origins: Sequence[Sequence[str]], *, drop_unassigned: bool = True,
) -> tuple[gpd.GeoDataFrame, dict[str, int]]:
    """Record each row's origin, tile it on its origin sheet, drop the off-sheet rows.

    Args:
        gdf: Points in the frame's coordinate reference system (CRS); any
            other columns are carried through.
        bounds: Frame tile polygons with a ``tile_name`` column.
        origins: Per-row origin tile names, aligned with ``gdf``'s rows.
        drop_unassigned: Drop the rows that get no tile (on no tile of their
            own sheet, or on no frame tile at all), as ``as_gdf`` always
            has. ``False`` keeps them with a null ``source_tile`` for the one
            caller whose legacy loop never dropped them (the Image-B ladder,
            whose union counts include them); the scorer leaves such rows
            unattributed.

    Returns:
        ``(frame, diagnostics)``: ``gdf`` with :data:`ORIGIN_COLUMN` and
        ``source_tile`` set, index preserved; and the diagnostics of
        ``assign_primary_tiles_on_origin_sheet``.

    Raises:
        ValueError: If ``origins`` is not aligned with ``gdf``.
    """
    if len(origins) != len(gdf):
        raise ValueError(f"{len(origins)} origins for {len(gdf)} rows")
    out = gdf.copy()
    lists = [list(o) for o in origins]
    out[ORIGIN_COLUMN] = [";".join(o) for o in lists]
    tiles, diag = assign_primary_tiles_on_origin_sheet(out, bounds, origin=lists)
    out["source_tile"] = tiles
    if not drop_unassigned:
        return out, diag
    return out[out["source_tile"].notna()].copy(), diag


def points_on_origin(
    centroids: np.ndarray, bounds: gpd.GeoDataFrame,
    origins: Sequence[Sequence[str]], crs: str,
    columns: dict[str, Any] | None = None, *, drop_unassigned: bool = True,
) -> tuple[gpd.GeoDataFrame, dict[str, int]]:
    """Wrap cluster centroids with their origins and tile them on their sheet.

    Args:
        centroids: ``(n, 2)`` array in ``crs``.
        bounds: Frame tile polygons with a ``tile_name`` column.
        origins: Per-centroid origin tile names.
        crs: The project CRS.
        columns: Optional per-row columns (e.g. ``vote_count``).
        drop_unassigned: As :func:`tile_on_origin`.

    Returns:
        As :func:`tile_on_origin`; the index is the centroid's position, so a
        caller can recover per-row arrays by ``frame.index``.
    """
    if len(centroids) == 0:
        empty = gpd.GeoDataFrame(
            {**{k: [] for k in (columns or {})}, ORIGIN_COLUMN: [], "source_tile": []},
            geometry=[], crs=crs)
        diag = {"n_points": 0, "n_assigned": 0, "n_outside_frame": 0,
                "n_outside_origin_sheet": 0, "n_cross_sheet_avoided": 0,
                "n_no_origin": 0}
        return empty, diag
    gdf = gpd.GeoDataFrame(
        dict(columns or {}), geometry=[Point(xy) for xy in centroids], crs=crs)
    return tile_on_origin(gdf, bounds, origins, drop_unassigned=drop_unassigned)


def recorded_origin(gdf: gpd.GeoDataFrame) -> list[list[str]]:
    """Each row's recorded ``source_tile`` as its origin (sets with no member list).

    Args:
        gdf: A detection set that records ``source_tile``.

    Returns:
        One single-tile list per row (empty where the value is missing).

    Raises:
        KeyError: If the set records no ``source_tile``.
    """
    if "source_tile" not in gdf.columns:
        raise KeyError("the set records no source_tile to keep as its origin")
    return [parse_tile_list(v) for v in gdf["source_tile"]]


def legacy_carrier_keep(points: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame) -> np.ndarray:
    """Which points the pre-D62 materialisers kept: those on any frame tile.

    The committed unions were filtered by the legacy rule, under which a
    cluster is dropped only when it intersects no frame tile; rebuilding a
    union row for row needs that filter, not the origin rule.

    Args:
        points: Points in the frame's CRS.
        bounds: Frame tile polygons with a ``tile_name`` column.

    Returns:
        Boolean mask aligned with ``points``.
    """
    tiles, _ = assign_primary_tiles_on_origin_sheet(
        points, bounds, origin=[[] for _ in range(len(points))])
    return np.asarray([t is not None for t in tiles], dtype=bool)


def attach_union_origins(
    union: gpd.GeoDataFrame, passes: list[list[dict[str, Any]]],
    bounds: gpd.GeoDataFrame, *, label: str, min_corroboration: int = 1,
    tol_m: float = UNION_GEOMETRY_TOL_M,
) -> gpd.GeoDataFrame:
    """Attach member tiles to a committed union rebuilt from its passes.

    A committed union (``materialise_grid_unions.union_with_votes`` and its
    stride, winner-ladder, and Image-B copies) is ``cluster_votes`` at
    ``min_corroboration`` over its passes, filtered to clusters on any frame
    tile, in clustering order. Rebuilding it the same way with
    :func:`cluster_votes_with_members` gives the same rows in the same order;
    the gate asserts that (count, per-row ``vote_count`` and centroid within
    ``tol_m``) before the members are attached, so a union that was built
    any other way is refused rather than mis-joined.

    Args:
        union: The committed union in the project CRS, with ``vote_count``;
            row order is the file's (the verifier's ``candidate_NNNNN`` key).
        passes: The passes the union was built from, in the order used.
        bounds: The carrier frame the union was filtered to.
        label: Cell label, for error messages.
        min_corroboration: The corroboration level the union was built at.
        tol_m: Largest allowed centroid displacement (metres).

    Returns:
        A copy of ``union`` with :data:`ORIGIN_COLUMN` (``;``-joined member
        tiles); every other column and the row order are untouched.

    Raises:
        OriginGateError: If the rebuild does not reproduce the union.
    """
    centroids, votes, members = cluster_votes_with_members(passes, min_corroboration)
    probe = gpd.GeoDataFrame(
        geometry=[Point(xy) for xy in centroids], crs=union.crs)
    keep = legacy_carrier_keep(probe, bounds) if len(probe) else np.zeros(0, dtype=bool)
    kept = np.flatnonzero(keep)
    if len(kept) != len(union):
        raise OriginGateError(
            f"{label}: rebuild keeps {len(kept)} clusters, the committed union "
            f"holds {len(union)}")
    if "vote_count" in union.columns:
        stored = union["vote_count"].to_numpy(dtype=int)
        if not np.array_equal(stored, votes[kept]):
            n_bad = int((stored != votes[kept]).sum())
            raise OriginGateError(
                f"{label}: {n_bad} rows' vote_count differs from the rebuild")
    shift = np.hypot(
        union.geometry.x.to_numpy() - centroids[kept, 0],
        union.geometry.y.to_numpy() - centroids[kept, 1],
    )
    if len(shift) and float(shift.max()) > tol_m:
        raise OriginGateError(
            f"{label}: rebuilt centroid {int(shift.argmax())} lies "
            f"{float(shift.max()):.6f} m from the committed row (tolerance {tol_m} m)")
    out = union.copy()
    out[ORIGIN_COLUMN] = [";".join(members[i]) for i in kept]
    return out


def rekey_on_origin(
    gdf: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, dict[str, int]]:
    """Re-tile a frame that records :data:`ORIGIN_COLUMN` on each row's origin sheet.

    Args:
        gdf: Rows with :data:`ORIGIN_COLUMN` (e.g. from
            :func:`attach_union_origins`).
        bounds: Frame tile polygons with a ``tile_name`` column.

    Returns:
        As :func:`tile_on_origin`; the index (the union row, i.e. the
        verifier's candidate number) is preserved.

    Raises:
        KeyError: If the frame records no origin column.
    """
    if ORIGIN_COLUMN not in gdf.columns:
        raise KeyError(f"no {ORIGIN_COLUMN!r} column: attach the origins first")
    return tile_on_origin(
        gdf, bounds, [parse_tile_list(v) for v in gdf[ORIGIN_COLUMN]])


def union_on_origin(
    union: gpd.GeoDataFrame, passes: list[list[dict[str, Any]]],
    bounds: gpd.GeoDataFrame, *, label: str, n_passes: int,
) -> gpd.GeoDataFrame:
    """Attach a committed union's member tiles and re-tile it on their sheets.

    The one call every verified-union loader in the grid, stride, plateau,
    and Image-B chains makes after its join and round-trip gates:
    :func:`attach_union_origins` then :func:`rekey_on_origin`.

    Args:
        union: The committed union in the project CRS (row order = the
            verifier's candidate number).
        passes: The cell's prepared passes (``load_cell_passes``); the first
            ``n_passes`` are the union's.
        bounds: The carrier frame.
        label: Cell label, for error messages.
        n_passes: How many passes the union was built from.

    Returns:
        The union with :data:`ORIGIN_COLUMN`, ``source_tile`` on each row's
        origin sheet, and the off-sheet rows dropped (index kept).

    Raises:
        OriginGateError: If fewer than ``n_passes`` passes are supplied or
            the rebuild does not reproduce the union.
    """
    if len(passes) < n_passes:
        raise OriginGateError(
            f"{label}: {len(passes)} passes supplied, the union needs {n_passes}")
    attached = attach_union_origins(union, passes[:n_passes], bounds, label=label)
    out, diag = rekey_on_origin(attached, bounds)
    logger.info(
        "%s: %d of %d union rows kept on their origin sheet where the legacy "
        "rule re-keyed them; %d on no tile of their own sheet (dropped); "
        "%d with no recorded origin", label, diag["n_cross_sheet_avoided"],
        diag["n_points"], diag["n_outside_origin_sheet"], diag["n_no_origin"])
    return out
