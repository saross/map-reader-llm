#!/usr/bin/env python3
# ============================================================================
# lib_fusion.py
# ----------------------------------------------------------------------------
# Weighted Boxes Fusion (WBF) for multi-pass VLM detections.
#
# Background
# ----------
# The VLM detection pipeline runs K passes over each tile and produces a set
# of axis-aligned bounding-box detections per pass. The previous consensus
# step (``lib_consensus.cluster_across_passes``) reduced these to final
# candidates via greedy-ball clustering on centroids at a 20 m radius. That
# approach has two documented limitations (Obs 228):
#
#   1. It ignores the spatial extent of each detection (treats centroids
#      only). Two boxes at 40 m centroid distance may represent the same
#      visible symbol or two distinct features; centroid distance cannot
#      distinguish them, but IoU can.
#   2. The 20 m radius is too tight to capture the ~11 % of same-mound
#      duplicates that drift more than ~20 m from the mound centre, while
#      any larger radius risks merging genuinely-neighbouring mounds at the
#      empirical 68.1 m minimum separation.
#
# This library provides a Weighted Boxes Fusion (WBF) alternative following
# Solovyev et al. 2019 (arXiv:1910.13302). The algorithm operates directly
# on the raw per-pass bounding boxes, merges them by IoU overlap, and
# produces a fused output that preserves the vote-count semantics of the
# current pipeline. The key advantage over centroid-distance clustering is
# that IoU is spatially aware: two boxes that do not overlap cannot be
# merged, regardless of their centroid distance. For 75 m diameter mound
# symbols, IoU drops to zero well before the 68 m cartographic minimum
# mound separation, enforcing the "distinct mounds" prior automatically.
#
# Pipeline
# --------
# 1. ``filter_boxes_by_size``: reject boxes outside plausible mound
#    dimensions (e.g. widths below 20 m or above 200 m). This catches the
#    pathological 560 m outlier and keeps the downstream logic working on
#    sensible inputs.
# 2. ``weighted_boxes_fusion``: canonical Solovyev 2019 WBF with a fixed
#    IoU threshold. Confidence weights are uniform (the proposer returns
#    "high" for every detection, so a weighted average degenerates to an
#    arithmetic mean). The vote count emerges as a by-product of the
#    clustering step and is preserved in the output metadata.
# 3. ``enforce_minimum_separation``: post-fusion safety net that merges any
#    two fused clusters whose centroids are within a specified distance.
#    This encodes the empirical cartographic constraint that no two real
#    mounds are closer than ~68 m (minimum observed = 68.1 m in the
#    569-mound reference corpus).
#
# The output format is deliberately compatible with the downstream
# candidate-manifest consumer (``scripts/extract_verifier_crops.py``) so
# that WBF can serve as a drop-in replacement for the current
# ``cluster_across_passes`` output.
# ============================================================================

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
from scipy.spatial import cKDTree

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

#: Default IoU threshold for the WBF step. Chosen empirically: for 75 m
#: diameter mound symbols, IoU ~ 0.25 corresponds to ~40 m centroid offset,
#: which captures typical drift (p90 = 23 m, p99 = 37 m) without allowing
#: merges across the 68 m minimum inter-mound distance.
DEFAULT_IOU_THRESHOLD = 0.25

#: Default minimum-separation distance for the post-fusion safety net.
#: Sitting comfortably below the 68.1 m empirical minimum inter-mound
#: distance to provide a margin for measurement error and centroid drift.
DEFAULT_MIN_SEPARATION_M = 60.0

#: Per-box size filter defaults. A plausible mound symbol occupies a box
#: roughly 60 x 60 m; the tolerance here is deliberately generous so that
#: we only reject obviously-pathological detections.
DEFAULT_MIN_DIMENSION_M = 20.0
DEFAULT_MAX_DIMENSION_M = 200.0
DEFAULT_MIN_AREA_M2 = 400.0
DEFAULT_MAX_AREA_M2 = 40_000.0


# ----------------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------------


@dataclass
class Box:
    """An axis-aligned bounding box with metadata.

    Coordinates are stored in projected-CRS metres (EPSG:32635 for the
    burial-mound corpus) with ``(x1, y1)`` the south-west corner and
    ``(x2, y2)`` the north-east corner. Confidence is a non-negative
    scalar; for the current VLM pipeline all boxes have confidence 1.0
    because the proposer returns a categorical "high" label.
    """

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float = 1.0
    pass_id: str = ""
    source_tile: str = ""
    subtype: str = "burial_mound"

    def __post_init__(self) -> None:
        if self.x1 > self.x2 or self.y1 > self.y2:
            raise ValueError(
                f"Box corners out of order: "
                f"({self.x1},{self.y1})-({self.x2},{self.y2})"
            )

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def centroid(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x1, self.y1, self.x2, self.y2)


@dataclass
class FusedCluster:
    """A cluster of raw boxes merged into a single fused box.

    ``fused_box`` carries the arithmetic-mean corners of all member boxes
    (equivalent to Solovyev 2019 WBF's weighted average under uniform
    confidences). ``members`` is the list of original boxes contributing
    to the cluster. ``vote_count`` is the number of distinct passes that
    contributed at least one member box; ``cluster_size`` is the raw
    number of contributing boxes (which may exceed vote_count when a
    single pass contributes multiple boxes to the same cluster, usually
    across overlapping tiles).
    """

    fused_box: Box
    members: list[Box] = field(default_factory=list)

    @property
    def vote_count(self) -> int:
        return len({m.pass_id for m in self.members})

    @property
    def cluster_size(self) -> int:
        return len(self.members)

    @property
    def contributing_passes(self) -> list[str]:
        return sorted({m.pass_id for m in self.members})

    @property
    def source_tiles(self) -> list[str]:
        return sorted({m.source_tile for m in self.members if m.source_tile})

    @property
    def centroid(self) -> tuple[float, float]:
        return self.fused_box.centroid


# ----------------------------------------------------------------------------
# IoU and fusion primitives
# ----------------------------------------------------------------------------


def box_iou(a: Box, b: Box) -> float:
    """Compute Intersection-over-Union for two axis-aligned boxes.

    Returns 0.0 for non-overlapping boxes and 1.0 for identical boxes.
    """
    ix1 = max(a.x1, b.x1)
    iy1 = max(a.y1, b.y1)
    ix2 = min(a.x2, b.x2)
    iy2 = min(a.y2, b.y2)

    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0

    inter = (ix2 - ix1) * (iy2 - iy1)
    union = a.area + b.area - inter
    if union <= 0.0:
        return 0.0
    return inter / union


def _mean_box(boxes: list[Box]) -> Box:
    """Return the arithmetic-mean bounding box across the members.

    Under uniform confidences this is the weighted-average degenerate case.
    The returned box inherits ``subtype`` from the first member and uses a
    placeholder confidence of 1.0; pass/tile metadata is not retained on
    the fused box because it is tracked on the ``FusedCluster`` wrapper.
    """
    if not boxes:
        raise ValueError("Cannot compute mean of empty box list")
    x1 = float(np.mean([b.x1 for b in boxes]))
    y1 = float(np.mean([b.y1 for b in boxes]))
    x2 = float(np.mean([b.x2 for b in boxes]))
    y2 = float(np.mean([b.y2 for b in boxes]))
    return Box(
        x1=x1, y1=y1, x2=x2, y2=y2,
        confidence=1.0,
        subtype=boxes[0].subtype,
    )


# ----------------------------------------------------------------------------
# Size filtering
# ----------------------------------------------------------------------------


def filter_boxes_by_size(
    boxes: Iterable[Box],
    min_dim: float = DEFAULT_MIN_DIMENSION_M,
    max_dim: float = DEFAULT_MAX_DIMENSION_M,
    min_area: float = DEFAULT_MIN_AREA_M2,
    max_area: float = DEFAULT_MAX_AREA_M2,
) -> tuple[list[Box], int]:
    """Reject boxes with implausible dimensions.

    A mound symbol on these maps is approximately 75 m in diameter. Boxes
    with width or height below ``min_dim`` metres are likely to be noise
    or partial detections; boxes with dimensions above ``max_dim`` metres
    are likely to be spurious large regions the VLM has hallucinated. The
    area filter is a final sanity check against very elongated boxes.

    Returns the filtered list and the count of rejected boxes.
    """
    kept: list[Box] = []
    rejected = 0
    for b in boxes:
        if b.width < min_dim or b.height < min_dim:
            rejected += 1
            continue
        if b.width > max_dim or b.height > max_dim:
            rejected += 1
            continue
        if b.area < min_area or b.area > max_area:
            rejected += 1
            continue
        kept.append(b)
    return kept, rejected


# ----------------------------------------------------------------------------
# Weighted Boxes Fusion (Solovyev et al. 2019)
# ----------------------------------------------------------------------------


def _sort_key(b: Box) -> tuple[float, float, float, float, float, float]:
    """Deterministic sort key for WBF input ordering.

    Solovyev's algorithm sorts by confidence descending. Under uniform
    confidences all boxes tie, so we break ties by area (largest first,
    since a larger box gives the cluster a more stable initial anchor)
    and then by coordinates (for reproducibility across runs).
    """
    return (
        -b.confidence,
        -b.area,
        b.x1,
        b.y1,
        b.x2,
        b.y2,
    )


def weighted_boxes_fusion(
    boxes: Iterable[Box],
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
) -> list[FusedCluster]:
    """Fuse overlapping boxes using the Solovyev 2019 WBF algorithm.

    Pseudocode (matching Algorithm 1 in the paper):

        sort boxes by (confidence desc, area desc, coords)
        L, F = [], []  # L: per-cluster box lists; F: fused representatives
        for b in sorted_boxes:
            find index i maximising IoU(b, F[i]) subject to IoU > threshold
            if found:
                L[i].append(b); F[i] = weighted_mean(L[i])
            else:
                L.append([b]); F.append(b)
        return clusters

    Under uniform confidences the weighted mean degenerates to an
    arithmetic mean over all cluster members. The vote count (number of
    distinct pass_ids contributing) emerges as a by-product and is
    preserved on the returned ``FusedCluster`` objects.

    Parameters
    ----------
    boxes : iterable of Box
        Raw per-pass detections. Empty input returns an empty list.
    iou_threshold : float
        Minimum IoU required to merge a box into an existing cluster.
        Default 0.25 corresponds to roughly 40 m centroid offset for
        75 m diameter mound boxes.

    Returns
    -------
    list of FusedCluster
        One cluster per fused candidate, in processing order.
    """
    boxes = list(boxes)
    if not boxes:
        return []

    ordered = sorted(boxes, key=_sort_key)

    member_lists: list[list[Box]] = []
    fused_boxes: list[Box] = []

    for b in ordered:
        best_idx = -1
        best_iou = iou_threshold
        for i, f in enumerate(fused_boxes):
            iou = box_iou(b, f)
            if iou > best_iou:
                best_iou = iou
                best_idx = i

        if best_idx >= 0:
            member_lists[best_idx].append(b)
            fused_boxes[best_idx] = _mean_box(member_lists[best_idx])
        else:
            member_lists.append([b])
            fused_boxes.append(
                Box(
                    x1=b.x1, y1=b.y1, x2=b.x2, y2=b.y2,
                    confidence=b.confidence,
                    subtype=b.subtype,
                )
            )

    return [
        FusedCluster(fused_box=f, members=list(m))
        for f, m in zip(fused_boxes, member_lists)
    ]


# ----------------------------------------------------------------------------
# Minimum-separation enforcement
# ----------------------------------------------------------------------------


class _UnionFind:
    """Standard union-find with path compression and union by rank."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, i: int) -> int:
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


#: Default anchor vote threshold for vote-aware min-separation. A pair of
#: clusters within ``min_separation_m`` is merged only if at least one has
#: vote_count >= this threshold. Low-vote fragments (FP candidates that
#: happen to cluster nearby) are left separate, preserving precision.
DEFAULT_ANCHOR_VOTE_THRESHOLD = 3


def enforce_minimum_separation(
    clusters: list[FusedCluster],
    min_separation_m: float = DEFAULT_MIN_SEPARATION_M,
    anchor_vote_threshold: int | None = None,
) -> list[FusedCluster]:
    """Merge any two fused clusters whose centroids are within the threshold.

    This post-fusion safety net encodes the empirical cartographic prior
    that no two real mounds are within ~68 m of each other. Any pair of
    fused clusters whose centroids sit closer than ``min_separation_m``
    is a candidate for merging.

    Two modes
    ---------
    If ``anchor_vote_threshold`` is ``None`` (default), every pair within
    the distance is merged — equivalent to the original unconditional
    safety net. This fixes all residual drift but can also combine
    low-vote FP fragments whose vote counts accumulate on the merged
    cluster, hurting precision.

    If ``anchor_vote_threshold`` is set, a pair is merged only when
    ``max(vote_count_a, vote_count_b) >= anchor_vote_threshold``. This
    allows a high-vote core cluster to absorb nearby low-vote drift
    fragments, while two low-vote FP fragments are left as distinct
    clusters.

    The merge structure uses connected-component single-link on the
    centroid graph — so a high-vote anchor and any low-vote fragments
    within the threshold of it form a single merged cluster, even if the
    low-vote fragments are not all within the threshold of each other.
    """
    if len(clusters) <= 1:
        return list(clusters)

    centroids = np.array([c.centroid for c in clusters])
    tree = cKDTree(centroids)
    pairs = tree.query_pairs(r=min_separation_m, output_type="ndarray")

    if len(pairs) == 0:
        return list(clusters)

    votes = np.array([c.vote_count for c in clusters])

    uf = _UnionFind(len(clusters))
    for a, b in pairs:
        ai, bi = int(a), int(b)
        if anchor_vote_threshold is not None:
            if max(votes[ai], votes[bi]) < anchor_vote_threshold:
                continue
        uf.union(ai, bi)

    groups: dict[int, list[FusedCluster]] = defaultdict(list)
    for i, c in enumerate(clusters):
        groups[uf.find(i)].append(c)

    merged: list[FusedCluster] = []
    for group in groups.values():
        if len(group) == 1:
            merged.append(group[0])
            continue
        pooled_members: list[Box] = []
        for c in group:
            pooled_members.extend(c.members)
        merged.append(
            FusedCluster(
                fused_box=_mean_box(pooled_members),
                members=pooled_members,
            )
        )

    return merged


# ----------------------------------------------------------------------------
# End-to-end convenience
# ----------------------------------------------------------------------------


def fuse_detections(
    boxes: Iterable[Box],
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    min_separation_m: float = DEFAULT_MIN_SEPARATION_M,
    anchor_vote_threshold: int | None = None,
    min_dim: float = DEFAULT_MIN_DIMENSION_M,
    max_dim: float = DEFAULT_MAX_DIMENSION_M,
    min_area: float = DEFAULT_MIN_AREA_M2,
    max_area: float = DEFAULT_MAX_AREA_M2,
) -> tuple[list[FusedCluster], dict]:
    """End-to-end fusion: size filter -> WBF -> minimum-separation.

    When ``min_separation_m`` is zero or negative the minimum-separation
    post-step is skipped entirely. When ``anchor_vote_threshold`` is set,
    the min-separation step is vote-aware (only merges if at least one
    cluster in the pair has vote_count >= threshold).

    Returns the final cluster list and a diagnostics dict with stage
    counts for audit purposes.
    """
    raw = list(boxes)
    filtered, rejected = filter_boxes_by_size(
        raw,
        min_dim=min_dim,
        max_dim=max_dim,
        min_area=min_area,
        max_area=max_area,
    )
    fused = weighted_boxes_fusion(filtered, iou_threshold=iou_threshold)

    if min_separation_m and min_separation_m > 0:
        final = enforce_minimum_separation(
            fused,
            min_separation_m=min_separation_m,
            anchor_vote_threshold=anchor_vote_threshold,
        )
    else:
        final = fused

    diagnostics = {
        "n_raw_boxes": len(raw),
        "n_rejected_by_size_filter": rejected,
        "n_filtered_boxes": len(filtered),
        "n_clusters_after_wbf": len(fused),
        "n_clusters_after_min_separation": len(final),
        "n_merged_by_min_separation": len(fused) - len(final),
        "iou_threshold": iou_threshold,
        "min_separation_m": min_separation_m,
        "anchor_vote_threshold": anchor_vote_threshold,
    }
    return final, diagnostics
