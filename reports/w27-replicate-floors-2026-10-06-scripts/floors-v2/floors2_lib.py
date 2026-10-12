#!/usr/bin/env python3
"""
Floors v2 shared library: exact fast restatements of the board's clustering and scorer.
======================================================================================

Two restatements, each gated for exact equality with the committed function
before any result is used:

* ``cluster_votes_fast`` -- ``h13_k_sensitivity.cluster_votes`` (seed-order greedy
  star at 20 m, votes = distinct passes, centroid = numpy mean of members) with a
  KD-tree used only to shortlist neighbours; the membership test, member order and
  centroid arithmetic are the committed ones. It also records each cluster's
  contributing passes (a bitmask), which the vote-propensity model needs.
* ``FastScorer`` -- ``lib_advanced_metrics.compute_per_tile_tp_fp_fn`` under the
  default ``id`` tile join, built on the shared library's own attribution
  (PI rulings D50 and D60 (4)):

  - **Detections** are attributed once per frame by the library's
    ``scope_detections_to_frame``: each row goes to its origin sheet (a recorded
    origin in ``ORIGIN_TILE_COLUMNS`` wins over a re-keyed ``source_tile``),
    sheets are read by the library's longest-prefix resolver, and a row is
    scored only if it intersects one of its own sheet's frame tiles. The
    attribution is row by row, so any threshold cell of a prepared frame (a row
    mask) has exactly the attribution the library gives that cell; the frame
    is attributed once and every cell reuses it.
  - **References** are the library's own per-sheet scopes, read once from
    ``iter_sheet_scopes``; each reference's false-negative tile is
    ``_assign_refs_to_primary_tiles``'s nearest-centroid primary tile.
  - **Matching** is per sheet on the SAME cost matrix as
    ``match_detections_to_references`` (GEOS distances; the committed matcher
    builds the matrix with ``np.full`` on an integer fill when the buffer is an
    int, so distances are truncated to whole metres before assignment, and this
    restatement does the same), with each sheet's rows in frame order.
  - **Booking**: true and false positives to the detection's ``source_tile``,
    false negatives to the reference's primary tile; a scored detection whose
    ``source_tile`` is not a frame tile refuses the cell, as the library's
    tile-join invariant does.

  Until 2026-10-12 this class split detections by ``source_tile`` prefix alone:
  no geometric scope, no origin restoration, and a bare ``str.startswith``
  sheet match. That version reproduced the pre-D50 scorer, and is archived
  under ``archive/superseded-w27-floors-2026-10-12/`` for the red sentinel of
  ``floors2_scorer_gate.py``.

Zero API. Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-07 |
Rebuilt on the library's attribution: 2026-10-12 | Apache 2.0
"""

from __future__ import annotations

from dataclasses import dataclass, field

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

#: Side channel: contributing-pass bitmasks of the last ``cluster_votes_fast`` call.
LAST_MEMBERS: dict = {}


def cluster_votes_fast(
    passes: list[list[dict]], min_corroboration: int, radius: float = 20.0
) -> tuple[np.ndarray, np.ndarray]:
    """``h13_k_sensitivity.cluster_votes`` with a KD-tree neighbour shortlist.

    Args:
        passes: Deduplicated detections per pass (dicts with ``centroid``).
        min_corroboration: Minimum within-pass ``cluster_size`` to keep.
        radius: Clustering radius in metres (the committed ``DEDUP_M``).

    Returns:
        (centroids [m, 2], votes [m]); bitmasks of contributing passes are left in
        ``LAST_MEMBERS['masks']`` in the same order.
    """
    pts: list = []
    owner: list[int] = []
    for idx, dets in enumerate(passes):
        for d in dets:
            if d.get("cluster_size", 1) >= min_corroboration:
                pts.append(d["centroid"])
                owner.append(idx)
    n = len(pts)
    if n == 0:
        LAST_MEMBERS["masks"] = []
        return np.zeros((0, 2)), np.zeros(0, dtype=int)
    arr = np.asarray(pts, dtype=float)
    own = np.asarray(owner, dtype=int)
    # The shortlist radius carries a margin so that every point the committed
    # full-array test admits (hypot <= radius) is in the shortlist; the exact
    # committed test is then applied to the shortlist.
    neigh = cKDTree(arr).query_ball_point(arr, r=radius + 1e-6)
    taken = np.zeros(n, dtype=bool)
    cents, votes, masks = [], [], []
    for i in range(n):
        if taken[i]:
            continue
        cand = np.asarray(neigh[i], dtype=np.intp)
        cand = cand[~taken[cand]]
        d = np.hypot(arr[cand, 0] - arr[i, 0], arr[cand, 1] - arr[i, 1])
        members = np.union1d(cand[d <= radius], [i])
        taken[members] = True
        cents.append((arr[members, 0].mean(), arr[members, 1].mean()))
        ow = set(own[members].tolist())
        votes.append(len(ow))
        masks.append(sum(1 << o for o in ow))
    LAST_MEMBERS["masks"] = masks
    return np.asarray(cents), np.asarray(votes, dtype=int)


@dataclass(frozen=True)
class PreparedFrame:
    """One detection frame attributed by the library, ready for many threshold cells.

    Attributes:
        points: Matcher geometry per row (the row's point, or its centroid), in
            frame order, as ``match_detections_to_references`` reads it.
        sheet: Per row, the index of its attributed sheet in ``FastScorer.sheets``,
            or -1 when the library does not score the row (unattributed, or
            outside its own sheet's frame tiles).
        book: Per row, the tile position its true or false positive is booked to
            (``source_tile`` under the ``id`` join), or -1 when ``source_tile`` is
            not a frame tile name.
        has_source_tile: Whether the frame carries a ``source_tile`` column.
        diagnostics: The library's ``detection_scope`` counts for the whole frame.
    """

    points: np.ndarray
    sheet: np.ndarray
    book: np.ndarray
    has_source_tile: bool
    diagnostics: dict = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.sheet)


class FastScorer:
    """``compute_per_tile_tp_fp_fn`` (id tile join) with both sides cached.

    Usage::

        scorer = FastScorer(ref, bounds, 50)
        prep = scorer.prepare(frame)                  # attribute once per frame
        tp, fp, fn = scorer.totals(prep, mask)        # any row mask: one cell
        table = scorer.per_tile(prep, mask)           # [n_tiles, 3] in tile_pos order

    Args:
        ref: Reference GeoDataFrame (``Map`` or ``source_map`` column).
        bounds: Tile bounds GeoDataFrame (``tile_name``), in the frames' CRS.
        buffer: Match buffer in metres, passed with the SAME type the committed
            caller passes (an int buffer gives an integer cost matrix there).
    """

    def __init__(self, ref: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame, buffer) -> None:
        from scripts.lib_advanced_metrics import (
            _assign_refs_to_primary_tiles,
            iter_sheet_scopes,
        )

        self.buffer = buffer
        self.bounds = bounds
        # The library keys its per-tile table by ``tile_name`` (one entry per
        # distinct name, bounds order); positions follow the same keys.
        self.tile_pos = {t: i for i, t in enumerate(dict.fromkeys(bounds["tile_name"]))}
        ref_to_tile = {}
        for tile, idxs in _assign_refs_to_primary_tiles(ref, bounds).items():
            for r in idxs:
                ref_to_tile[r] = tile
        # Each sheet's in-scope references exactly as the library's per-sheet
        # loop yields them. On ``main`` the reference side does not depend on
        # the detections, so an empty detection set reads it once.
        empty = gpd.GeoDataFrame(
            {"source_tile": pd.Series([], dtype=object)},
            geometry=gpd.GeoSeries([], crs=bounds.crs),
        )
        self.sheets: list[tuple[str, np.ndarray, np.ndarray]] = []
        for sheet, _dets, ref_scope, _sheet_bounds in iter_sheet_scopes(empty, ref, bounds):
            geoms = [g if g.geom_type == "Point" else g.centroid for g in ref_scope.geometry]
            fn_pos = []
            for r in ref_scope.index:
                t = ref_to_tile.get(r)
                fn_pos.append(self.tile_pos[t] if (t and t in self.tile_pos) else -1)
            self.sheets.append(
                (sheet, np.asarray(geoms, dtype=object), np.asarray(fn_pos, dtype=np.int64))
            )
        self.sheet_index = {name: i for i, (name, _, _) in enumerate(self.sheets)}

    def prepare(self, frame: gpd.GeoDataFrame) -> PreparedFrame:
        """Attribute every row of ``frame`` once with the library's detection scope.

        Args:
            frame: Detections in the bounds' CRS (``source_tile`` and/or an origin
                column, as ``compute_per_tile_tp_fp_fn`` requires).

        Returns:
            A :class:`PreparedFrame` whose rows align with ``frame``'s rows.
        """
        from scripts.lib_advanced_metrics import scope_detections_to_frame

        n = len(frame)
        # Positions, not labels: the library's spatial join is keyed by position,
        # and a positional index makes the kept rows' positions read directly.
        f = frame.reset_index(drop=True)
        scope = scope_detections_to_frame(f, self.bounds)
        sheet = np.full(n, -1, dtype=np.int64)
        kept = scope.detections.index.to_numpy()
        if len(kept):
            sheet[kept] = [self.sheet_index[s] for s in scope.sheets]
        geoms = f.geometry.to_numpy()
        points = np.asarray(
            [g if g.geom_type == "Point" else g.centroid for g in geoms], dtype=object
        )
        has_st = "source_tile" in f.columns
        book = np.full(n, -1, dtype=np.int64)
        if has_st:
            for i, t in enumerate(f["source_tile"].tolist()):
                # ``recorded_tile in tile_counts``: the library's id-join test.
                if t in self.tile_pos:
                    book[i] = self.tile_pos[t]
        return PreparedFrame(points, sheet, book, has_st, dict(scope.diagnostics))

    def per_tile(self, prep: PreparedFrame, mask: np.ndarray | None = None) -> np.ndarray:
        """Per-tile [tp, fp, fn] of one cell, over ``tile_pos`` order.

        Args:
            prep: A prepared frame.
            mask: Boolean row mask selecting the cell (all rows when ``None``).

        Returns:
            Integer array [n_tiles, 3].

        Raises:
            KeyError: If a detection is scored but the frame has no ``source_tile``
                (the library reads ``det_row["source_tile"]`` there).
            ValueError: If a scored detection's ``source_tile`` is not a frame tile:
                the library's tile-join invariant refuses such a table.
        """
        out = np.zeros((len(self.tile_pos), 3), dtype=np.int64)
        scored = prep.sheet >= 0 if mask is None else (np.asarray(mask, bool) & (prep.sheet >= 0))
        rows = np.flatnonzero(scored)  # frame order, as each sheet's scope keeps it
        if len(rows) and not prep.has_source_tile:
            raise KeyError("source_tile: scored detections carry no source_tile column")
        if len(rows) and (prep.book[rows] < 0).any():
            short = int((prep.book[rows] < 0).sum())
            raise ValueError(
                f"per-tile table refused: {short} of {len(rows)} in-frame detections "
                "carry a source_tile that is not a frame tile (the library's "
                "tile_join_detection_shortfall)"
            )
        row_sheet = prep.sheet[rows]
        buf = self.buffer
        for s, (_name, ref_geoms, fn_pos) in enumerate(self.sheets):
            di = rows[row_sheet == s]
            if not len(di) and not len(ref_geoms):
                continue
            if not len(di):
                for p in fn_pos[fn_pos >= 0]:
                    out[p, 2] += 1
                continue
            if not len(ref_geoms):
                for p in prep.book[di]:
                    out[p, 1] += 1
                continue
            dist = shapely.distance(prep.points[di][:, None], ref_geoms[None, :])
            cost = np.full((len(di), len(ref_geoms)), buf * 1000)  # committed dtype rule
            ok = dist <= buf
            cost[ok] = dist[ok]
            r_d, r_r = linear_sum_assignment(cost)
            keep = cost[r_d, r_r] <= buf
            matched_det = np.zeros(len(di), dtype=bool)
            matched_det[r_d[keep]] = True
            matched_ref = np.zeros(len(ref_geoms), dtype=bool)
            matched_ref[r_r[keep]] = True
            np.add.at(out[:, 0], prep.book[di[matched_det]], 1)
            np.add.at(out[:, 1], prep.book[di[~matched_det]], 1)
            fn = fn_pos[~matched_ref]
            np.add.at(out[:, 2], fn[fn >= 0], 1)
        return out

    def totals(
        self, prep: PreparedFrame, mask: np.ndarray | None = None
    ) -> tuple[int, int, int]:
        """Micro totals (tp, fp, fn) of one cell; see :meth:`per_tile`."""
        a = self.per_tile(prep, mask).sum(axis=0)
        return int(a[0]), int(a[1]), int(a[2])


def f1_of(tp: int, fp: int, fn: int) -> float:
    """Micro F1 exactly as ``n1_baseline_leaderboard_tiering.micro_f1``."""
    from scripts.n1_baseline_leaderboard_tiering import micro_f1

    return micro_f1(tp, fp, fn)
