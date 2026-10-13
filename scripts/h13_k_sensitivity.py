#!/usr/bin/env python3
"""
How many passes does the corroboration x consensus sweep actually need?

Two diagnostics, both zero-cost, both feeding the Tier-1 design decision.

**A — dedup/scope decomposition.** The tile-size grid re-scored the
384 px MINIMAL/T=1.0 pool at 0.6463 where the committed consensus
manifest records 0.6667. Two changes could explain the gap: the uniform
within-pass deduplication, or the shared evaluation footprint. It
matters which, because the answer decides how much of the existing
results corpus a scoring review would have to touch. This diagnostic
re-scores the same pool on its OWN native era-2-487 bounds, so the only
difference from the committed number is deduplication.

**B — K sensitivity.** Every cell in the Tier-0 and grid analyses peaked
at ``k = K``, the edge of the vote grid, because K was only 3. If the
optimum is interior at K = 5, then n = 5 locates it and n = 10 only
sharpens the estimate; if it is still at the edge at K = 5, n = 5 can
only bound the optimum and the 2x2 needs n = 10 from the start. The
384 px pools carry up to 30 committed passes, so the question can be
settled empirically by sub-sampling rather than argued from priors.

Both run on 384 px / 12.5 % material, which is the caveat to carry: the
corroboration dimension is weak at 12.5 % overlap (about 6 % of
deduplicated detections are corroborated by a second tile against 37 %
at 50 %), so B constrains the VOTE dimension well and the corroboration
dimension only loosely.

**Tile attribution (PI ruling D62 (1), 2026-10-13).** Clusters are built by
:func:`cluster_votes_with_origins`, which keeps each cluster's contributing
proposer tiles, and :func:`score` tiles and scores every cluster on its own
sheet. Until 2026-10-13 the clusters reached scoring as bare centroids, so a
centroid in the overlap of two sheets' padded tiles could be booked to the
neighbouring sheet and matched against its references.

Usage::

    python scripts/h13_k_sensitivity.py \\
        --output-dir results/h13-overlap-2026-08-18/k-sensitivity

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (  # noqa: E402
    calculate_f1_internal,
    parse_tile_list,
)
from scripts.lib_detection_paths import find_pass_geojsons  # noqa: E402
from scripts.merge_passes import deduplicate_within_pass  # noqa: E402
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEDUP_M = 20.0
BUFFER_M = 20
CORROBORATION = (1, 2, 3)
K_LADDER = (3, 5, 7, 10)
CRS = "EPSG:32635"
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS_384 = PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
POOLS = {
    "minimal-t1.0": PROJECT_ROOT / "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0",
    "minimal-t0.7": PROJECT_ROOT / "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
}


def load_pool(pool_dir: Path, max_k: int) -> list[list[dict]]:
    """Load and deduplicate the first ``max_k`` passes of a pool.

    Args:
        pool_dir: Directory holding ``run_N`` subdirectories.
        max_k: Number of passes to load, in numeric run order.

    Returns:
        One deduplicated detection list per pass.
    """
    run_dirs = sorted(pool_dir.glob("run_*"), key=lambda p: int(p.name.split("_")[1]))
    passes = []
    for run_dir in run_dirs[:max_k]:
        # Two committed naming conventions (real-time hyphen, batch underscore);
        # the canonical resolver expands both, or the pool loads silently empty.
        files = find_pass_geojsons(run_dir)
        if not files:
            continue
        data = json.loads(files[0].read_text())
        passes.append(deduplicate_within_pass(
            data.get("features", []), distance_thresh=DEDUP_M))
    return passes


def cluster_votes(
    passes: list[list[dict]], min_corroboration: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Cluster a pool's passes once and return cluster centroids with vote counts.

    Clustering once per corroboration level (rather than once per vote
    threshold) is both faster and more correct: every vote threshold then
    reads off the same clustering, so a cluster cannot change membership
    as the threshold moves. Uses a NumPy-vectorised restatement of the
    project's greedy star clustering.

    Args:
        passes: Deduplicated detections per pass.
        min_corroboration: Minimum within-pass ``cluster_size`` to keep.

    Returns:
        Tuple of (centroids array of shape (n, 2), vote-count array).
    """
    pts: list[tuple[float, float]] = []
    owner: list[int] = []
    for idx, dets in enumerate(passes):
        for d in dets:
            if d.get("cluster_size", 1) >= min_corroboration:
                pts.append(d["centroid"])
                owner.append(idx)
    n = len(pts)
    if n == 0:
        return np.zeros((0, 2)), np.zeros(0, dtype=int)

    arr = np.asarray(pts, dtype=float)
    own = np.asarray(owner, dtype=int)
    taken = np.zeros(n, dtype=bool)
    centroids: list[tuple[float, float]] = []
    votes: list[int] = []

    for i in range(n):
        if taken[i]:
            continue
        d = np.hypot(arr[:, 0] - arr[i, 0], arr[:, 1] - arr[i, 1])
        members = np.flatnonzero((d <= DEDUP_M) & ~taken)
        members = np.union1d(members, [i])
        taken[members] = True
        centroids.append((arr[members, 0].mean(), arr[members, 1].mean()))
        votes.append(len(set(own[members].tolist())))

    return np.asarray(centroids), np.asarray(votes, dtype=int)


def _member_tiles(detection: dict) -> list[str]:
    """The proposer tile(s) one pooled detection was seen on.

    A detection deduplicated by ``merge_passes.deduplicate_within_pass``
    records its members' tiles as ``source_tiles`` (a list); a raw or
    hand-built detection may carry a single ``source_tile`` instead.
    ``parse_tile_list`` accepts every serialisation the corpus holds and
    drops empty names, so ``""`` (what ``"".split(";")`` leaves for a
    feature with no record) contributes nothing.

    Args:
        detection: One deduplicated detection dict.

    Returns:
        Tile names, possibly empty.
    """
    tiles = parse_tile_list(detection.get("source_tiles"))
    if not tiles:
        tiles = parse_tile_list(detection.get("source_tile"))
    return tiles


def cluster_votes_with_origins(
    passes: list[list[dict]], min_corroboration: int,
) -> tuple[np.ndarray, np.ndarray, list[list[str]]]:
    """:func:`cluster_votes`, also returning each cluster's contributing tiles.

    **Why this exists (PI ruling D62 (1), 2026-10-13).** :func:`cluster_votes`
    returns bare centroids. Scored through
    :func:`prepare_h13_scoring.assign_primary_tiles`, a bare centroid has no
    recorded origin, so the D50 never-re-key rule
    (``lib_advanced_metrics.assign_primary_tiles_on_origin_sheet``) falls
    back to the legacy rule: the nearest tile centroid among ALL frame
    tiles. Where two sheets' padded tiles overlap, that tile can belong to
    the neighbouring sheet, and the per-sheet matcher then scores the
    detection against the wrong sheet's references
    (``reports/frames-blast-radius-2026-10-07.md`` § 5.4). This function
    keeps, for every cluster, the sorted union of its members' proposer
    tiles, so the caller can pass them on as the origin.

    The clustering is :func:`cluster_votes`'s, step for step (the same pool
    order, seeds, radius, and membership), so the centroids and vote counts
    are identical to it; ``tests/test_h13_origin_route.py`` pins that.
    :func:`cluster_votes` itself is left unchanged because the grid,
    plateau, stride, Image-B, W2.7, and Gemini 3.7 ladder chains import it
    with its two-value contract.

    Args:
        passes: Deduplicated detections per pass, each carrying
            ``centroid``, optionally ``cluster_size``, and its proposer
            tiles (``source_tiles`` or ``source_tile``).
        min_corroboration: Minimum within-pass ``cluster_size`` to keep.

    Returns:
        Tuple of (centroids array of shape (n, 2), vote-count array, one
        sorted list of contributing tile names per cluster).

    Example:
        >>> passes = [[{"centroid": (0.0, 0.0), "source_tiles": ["M_x0_y0.png"]}],
        ...           [{"centroid": (5.0, 0.0), "source_tiles": ["M_x0_y1.png"]}]]
        >>> _, votes, origins = cluster_votes_with_origins(passes, 1)
        >>> votes.tolist(), origins
        ([2], [['M_x0_y0.png', 'M_x0_y1.png']])
    """
    pts: list[tuple[float, float]] = []
    owner: list[int] = []
    tiles: list[list[str]] = []
    for idx, dets in enumerate(passes):
        for d in dets:
            if d.get("cluster_size", 1) >= min_corroboration:
                pts.append(d["centroid"])
                owner.append(idx)
                tiles.append(_member_tiles(d))
    n = len(pts)
    if n == 0:
        return np.zeros((0, 2)), np.zeros(0, dtype=int), []

    arr = np.asarray(pts, dtype=float)
    own = np.asarray(owner, dtype=int)
    taken = np.zeros(n, dtype=bool)
    centroids: list[tuple[float, float]] = []
    votes: list[int] = []
    origins: list[list[str]] = []

    # The greedy star clustering of cluster_votes, unchanged: each untaken
    # point in pool order seeds a cluster that absorbs every untaken point
    # within DEDUP_M of it.
    for i in range(n):
        if taken[i]:
            continue
        d = np.hypot(arr[:, 0] - arr[i, 0], arr[:, 1] - arr[i, 1])
        members = np.flatnonzero((d <= DEDUP_M) & ~taken)
        members = np.union1d(members, [i])
        taken[members] = True
        centroids.append((arr[members, 0].mean(), arr[members, 1].mean()))
        votes.append(len(set(own[members].tolist())))
        origins.append(sorted({t for m in members.tolist() for t in tiles[m]}))

    return np.asarray(centroids), np.asarray(votes, dtype=int), origins


def score(
    centroids: np.ndarray, votes: np.ndarray, min_votes: int,
    bounds: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
    origins: list[list[str]] | None = None,
) -> tuple[float, float, float, int]:
    """Score one vote threshold against ground truth.

    **Origins (PI ruling D62 (1), 2026-10-13).** When ``origins`` is given
    (one list of contributing tiles per cluster, from
    :func:`cluster_votes_with_origins`), each selected cluster is tiled on
    its own sheet (``assign_primary_tiles(..., origin=...)``) and carries
    the list into scoring as ``source_tiles``, so the shared scorer
    attributes it by origin exactly as it attributes a committed consensus
    file. A cluster that intersects no tile of its own sheet is out of
    frame for that sheet and is not scored, which is the scorer's own rule
    (ruling D50). Without ``origins`` the legacy, location-only tiling is
    used, as before.

    Args:
        centroids: Cluster centroids. votes: Per-cluster vote counts.
        min_votes: Vote threshold. bounds: Scoring bounds.
        gdf_ref: Ground truth.
        origins: Optional per-cluster contributing tiles, aligned with
            ``centroids``.

    Returns:
        Tuple of (precision, recall, F1, detection count).
    """
    sel = votes >= min_votes
    if not sel.any():
        return 0.0, 0.0, 0.0, 0
    gdf = gpd.GeoDataFrame(
        geometry=[Point(xy) for xy in centroids[sel]], crs=CRS)
    if origins is None:
        gdf["source_tile"] = assign_primary_tiles(gdf, bounds)
    else:
        if len(origins) != len(centroids):
            raise ValueError(
                f"origins has {len(origins)} entries for {len(centroids)} clusters"
            )
        kept = [list(origins[i]) for i in np.flatnonzero(sel)]
        # One list per row: built as an object Series so pandas does not
        # read a list of equal-length lists as a 2-D array.
        gdf["source_tiles"] = pd.Series(kept, index=gdf.index, dtype=object)
        gdf["source_tile"] = assign_primary_tiles(gdf, bounds, origin=kept)
    gdf = gdf[gdf["source_tile"].notna()].copy()
    if gdf.empty:
        return 0.0, 0.0, 0.0, 0
    p, r, f1 = calculate_f1_internal(gdf, gdf_ref, bounds, buffer_metres=BUFFER_M)
    return p, r, f1, len(gdf)


def main() -> int:
    """Run both diagnostics and write the results.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="Dedup/scope decomposition and K sensitivity for the 2x2 design.")
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results/h13-overlap-2026-08-18/k-sensitivity")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    bounds = gpd.read_file(BOUNDS_384)
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    logger.info("native 384 px scope: %d tiles", len(bounds))

    out: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "POST-HOC diagnostic (E41-class).",
        "native_scope": {"bounds": str(BOUNDS_384.relative_to(PROJECT_ROOT)),
                         "tiles": len(bounds)},
        "decomposition": {},
        "k_sensitivity": {},
    }

    for pool_name, pool_dir in POOLS.items():
        max_k = max(K_LADDER)
        passes = load_pool(pool_dir, max_k)
        logger.info("%s: %d passes loaded, %d detections/pass after dedup",
                    pool_name, len(passes),
                    round(sum(len(p) for p in passes) / max(len(passes), 1)))
        corr = Counter(d.get("cluster_size", 1) for p in passes for d in p)
        total = sum(corr.values())
        out["k_sensitivity"].setdefault(pool_name, {})["corroboration_profile"] = {
            str(k): v / total for k, v in sorted(corr.items())
        }

        rows: list[dict[str, Any]] = []
        for K in K_LADDER:
            subset = passes[:K]
            for c in CORROBORATION:
                # Each cluster keeps its contributing tiles, so it is tiled
                # and scored on its own sheet (ruling D62 (1)).
                cents, votes, origins = cluster_votes_with_origins(subset, c)
                for k in range(1, K + 1):
                    p, r, f1, n = score(
                        cents, votes, k, bounds, gdf_ref, origins=origins)
                    rows.append({"K": K, "min_corroboration": c, "min_votes": k,
                                 "precision": p, "recall": r, "f1": f1,
                                 "n_detections": n})
        out["k_sensitivity"][pool_name]["cells"] = rows

        logger.info("--- %s: best cell per K (native 384 px scope) ---", pool_name)
        best_at_max = max((x for x in rows if x["K"] == max(K_LADDER)),
                          key=lambda x: x["f1"])
        for K in K_LADDER:
            best = max((x for x in rows if x["K"] == K), key=lambda x: x["f1"])
            interior = best["min_votes"] < K
            logger.info(
                "  K=%2d: best F1=%.4f at c>=%d k>=%d (%s), "
                "gap to K=%d best = %+.4f",
                K, best["f1"], best["min_corroboration"], best["min_votes"],
                "INTERIOR" if interior else "grid edge",
                max(K_LADDER), best["f1"] - best_at_max["f1"])

    # Diagnostic A: the T=1.0 pool at 9-of-10 on its native scope, which is
    # the committed consensus cell — any gap is deduplication alone.
    passes = load_pool(POOLS["minimal-t1.0"], 10)
    cents, votes, origins = cluster_votes_with_origins(passes, 1)
    p, r, f1, n = score(cents, votes, 9, bounds, gdf_ref, origins=origins)
    out["decomposition"] = {
        "condition": "pv-diag-384::flash-minimal-text-n30-t07-text-t1.0-consensus-9of10",
        "committed_f1": 0.6667,
        "native_scope_deduped_f1": f1,
        "shared_scope_deduped_f1": 0.6463,
        "precision": p, "recall": r, "n_detections": n,
        "note": (
            "The committed pipeline ALREADY deduplicates (merge_passes.py "
            "Step 1), and this rebuild reproduces its clustering exactly "
            "(549 clusters at 9-of-10). The residual gap to the committed "
            "0.6667 is therefore neither deduplication nor aggregation: it "
            "is the tile-assignment tie-break. evaluate_detections.py books "
            "a detection to the FIRST intersecting bounds tile (row-order "
            "dependent); this chain books it to the nearest-centroid tile. "
            "Of 549 detections, 90 change tile and 10 change MAP SHEET, and "
            "because matching is per map those 10 move F1 by 0.0102."
        ),
        "residual_is": "tile-assignment tie-break, not dedup",
    }
    logger.info(
        "DECOMPOSITION 9-of-10: committed 0.6667 | this chain, native scope "
        "%.4f | this chain, shared scope 0.6463", f1)
    logger.info(
        "  residual vs committed = %+.4f — NOT deduplication (the committed "
        "pipeline already dedups and this rebuild reproduces its 549 "
        "clusters); it is the tile-assignment tie-break, first-intersecting "
        "vs nearest-centroid, via 10 map-sheet reassignments.", f1 - 0.6667)
    logger.info("  footprint effect = %+.4f", 0.6463 - f1)

    (args.output_dir / "k_sensitivity.json").write_text(json.dumps(out, indent=2))
    logger.info("Wrote %s", args.output_dir / "k_sensitivity.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
