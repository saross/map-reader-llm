#!/usr/bin/env python3
"""
Floors v2 shared library: exact fast restatements of the board's clustering and scorer.
======================================================================================

Two restatements, each gated for bit-exact equality with the committed function
before any result is used:

* ``cluster_votes_fast`` -- ``h13_k_sensitivity.cluster_votes`` (seed-order greedy
  star at 20 m, votes = distinct passes, centroid = numpy mean of members) with a
  KD-tree used only to shortlist neighbours; the membership test, member order and
  centroid arithmetic are the committed ones. It also records each cluster's
  contributing passes (a bitmask), which the vote-propensity model needs.
* ``FastScorer`` -- ``lib_advanced_metrics.compute_per_tile_tp_fp_fn`` under the
  default ``id`` tile join: per-map Hungarian matching on the SAME cost matrix
  (GEOS distances; the committed matcher builds the matrix with ``np.full`` on an
  integer fill when the buffer is an int, so distances are truncated to whole
  metres before assignment, and this restatement does the same), TP/FP booked to
  the detection's ``source_tile``, FN to the reference's primary tile. The
  reference-side work (scoping, primary tiles) is done once per frame.

Zero API. Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-07 | Apache 2.0
"""

from __future__ import annotations

import numpy as np
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


class FastScorer:
    """``compute_per_tile_tp_fp_fn`` (id tile join) with the reference side cached.

    Args:
        ref: Reference GeoDataFrame (``Map`` or ``source_map`` column).
        bounds: Tile bounds GeoDataFrame (``tile_name``).
        buffer: Match buffer in metres, passed with the SAME type the committed
            caller passes (an int buffer gives an integer cost matrix there).
    """

    def __init__(self, ref, bounds, buffer):
        from scripts.lib_advanced_metrics import (
            _assign_refs_to_primary_tiles,
            get_map_name,
            scope_references_to_tiles,
        )

        self.buffer = buffer
        self.tile_order = [str(t) for t in bounds["tile_name"]]
        self.tile_set = set(self.tile_order)
        self.tile_pos = {t: i for i, t in enumerate(dict.fromkeys(self.tile_order))}
        ref_to_tile = {}
        for tile, idxs in _assign_refs_to_primary_tiles(ref, bounds).items():
            for r in idxs:
                ref_to_tile[r] = tile
        col = "Map" if "Map" in ref.columns else "source_map"
        self.maps = []
        for map_name in {get_map_name(n) for n in bounds["tile_name"].unique()}:
            if map_name == "Unknown":
                continue
            mb = bounds[bounds["tile_name"].str.startswith(map_name)]
            rm = ref[ref[col] == map_name]
            rs = scope_references_to_tiles(rm, mb) if not rm.empty else rm.iloc[0:0]
            geoms = [g if g.geom_type == "Point" else g.centroid for g in rs.geometry]
            fn_tile = []
            for r in rs.index:
                t = ref_to_tile.get(r)
                fn_tile.append(t if (t and t in self.tile_set) else None)
            self.maps.append((map_name, np.asarray(geoms, dtype=object), fn_tile))
        self._maps_of: dict[str, list[int]] = {}

    def _maps_for(self, tile) -> list[int]:
        if not isinstance(tile, str):
            raise ValueError(f"non-string source_tile {tile!r}")
        m = self._maps_of.get(tile)
        if m is None:
            m = [i for i, (name, _, _) in enumerate(self.maps) if tile.startswith(name)]
            self._maps_of[tile] = m
        return m

    def per_tile(self, xy: np.ndarray, tiles) -> np.ndarray:
        """Per-tile [tp, fp, fn] over ``tile_pos`` order (unique tile names)."""
        out = np.zeros((len(self.tile_pos), 3), dtype=np.int64)
        by_map: dict[int, list[int]] = {}
        for i, t in enumerate(tiles):
            for m in self._maps_for(t):
                by_map.setdefault(m, []).append(i)
        pts = shapely.points(np.asarray(xy, dtype=float)) if len(xy) else np.zeros(0, dtype=object)
        buf = self.buffer
        for m, (_, ref_geoms, fn_tile) in enumerate(self.maps):
            di = by_map.get(m, [])
            if not di and len(ref_geoms) == 0:
                continue
            if not di:
                for t in fn_tile:
                    if t is not None:
                        out[self.tile_pos[t], 2] += 1
                continue
            if len(ref_geoms) == 0:
                for i in di:
                    if tiles[i] in self.tile_set:
                        out[self.tile_pos[tiles[i]], 1] += 1
                continue
            dist = shapely.distance(pts[di][:, None], ref_geoms[None, :])
            cost = np.full((len(di), len(ref_geoms)), buf * 1000)  # committed dtype rule
            ok = dist <= buf
            cost[ok] = dist[ok]
            r_d, r_r = linear_sum_assignment(cost)
            keep = cost[r_d, r_r] <= buf
            md, mr = set(r_d[keep].tolist()), set(r_r[keep].tolist())
            for j, i in enumerate(di):
                t = tiles[i]
                if t in self.tile_set:
                    out[self.tile_pos[t], 0 if j in md else 1] += 1
            for j, t in enumerate(fn_tile):
                if j not in mr and t is not None:
                    out[self.tile_pos[t], 2] += 1
        return out

    def totals(self, xy, tiles) -> tuple[int, int, int]:
        a = self.per_tile(xy, tiles).sum(axis=0)
        return int(a[0]), int(a[1]), int(a[2])


def f1_of(tp: int, fp: int, fn: int) -> float:
    """Micro F1 exactly as ``n1_baseline_leaderboard_tiering.micro_f1``."""
    from scripts.n1_baseline_leaderboard_tiering import micro_f1

    return micro_f1(tp, fp, fn)
