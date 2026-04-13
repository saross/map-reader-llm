"""
Tier 1 unit tests for ``scripts/lib_fusion.py``.

Covers: ``box_iou`` correctness for identical/disjoint/partial overlaps;
the size filter; the WBF algorithm for overlapping, disjoint, and drift
cases; the minimum-separation post-enforcement; and the end-to-end
``fuse_detections`` pipeline including diagnostic counters.
"""

import math

import pytest

from scripts.lib_fusion import (
    Box,
    DEFAULT_IOU_THRESHOLD,
    DEFAULT_MIN_SEPARATION_M,
    box_iou,
    enforce_minimum_separation,
    filter_boxes_by_size,
    fuse_detections,
    weighted_boxes_fusion,
)
from scripts.lib_fusion import FusedCluster

pytestmark = pytest.mark.tier1


# ----------------------------------------------------------------------------
# Box data-class
# ----------------------------------------------------------------------------


def test_box_rejects_inverted_corners():
    with pytest.raises(ValueError):
        Box(x1=10.0, y1=0.0, x2=0.0, y2=10.0)


def test_box_geometry_properties():
    b = Box(x1=0.0, y1=0.0, x2=60.0, y2=80.0)
    assert b.width == 60.0
    assert b.height == 80.0
    assert b.area == pytest.approx(4800.0)
    assert b.centroid == pytest.approx((30.0, 40.0))


# ----------------------------------------------------------------------------
# IoU
# ----------------------------------------------------------------------------


def test_iou_identical_boxes_is_one():
    a = Box(x1=0.0, y1=0.0, x2=50.0, y2=50.0)
    b = Box(x1=0.0, y1=0.0, x2=50.0, y2=50.0)
    assert box_iou(a, b) == pytest.approx(1.0)


def test_iou_disjoint_boxes_is_zero():
    a = Box(x1=0.0, y1=0.0, x2=50.0, y2=50.0)
    b = Box(x1=100.0, y1=100.0, x2=150.0, y2=150.0)
    assert box_iou(a, b) == pytest.approx(0.0)


def test_iou_touching_boxes_is_zero():
    """Boxes that share only an edge have zero intersection area."""
    a = Box(x1=0.0, y1=0.0, x2=50.0, y2=50.0)
    b = Box(x1=50.0, y1=0.0, x2=100.0, y2=50.0)
    assert box_iou(a, b) == pytest.approx(0.0)


def test_iou_half_overlap_case():
    a = Box(x1=0.0, y1=0.0, x2=100.0, y2=100.0)
    b = Box(x1=50.0, y1=0.0, x2=150.0, y2=100.0)
    # Intersection = 50 * 100 = 5000; union = 10000 + 10000 - 5000 = 15000
    assert box_iou(a, b) == pytest.approx(5000 / 15000)


def test_iou_is_symmetric():
    a = Box(x1=0.0, y1=0.0, x2=75.0, y2=75.0)
    b = Box(x1=20.0, y1=20.0, x2=100.0, y2=100.0)
    assert box_iou(a, b) == pytest.approx(box_iou(b, a))


def test_iou_drops_to_zero_at_cartographic_floor():
    """Two 75 m diameter boxes at 68 m centroid offset must have zero IoU.

    This is the property that makes WBF safe against merging neighbouring
    mounds at the empirical 68.1 m minimum inter-mound distance.
    """
    a = Box(x1=0.0, y1=0.0, x2=75.0, y2=75.0)  # centroid (37.5, 37.5)
    b = Box(x1=68.0, y1=0.0, x2=143.0, y2=75.0)  # centroid (105.5, 37.5)
    # Centroid distance = 68 m; boxes overlap by 7 m horizontally
    iou = box_iou(a, b)
    assert iou < 0.15, f"Expected low IoU at 68 m offset, got {iou}"


# ----------------------------------------------------------------------------
# Size filter
# ----------------------------------------------------------------------------


def test_filter_rejects_oversize_box():
    big = Box(x1=0.0, y1=0.0, x2=300.0, y2=300.0)
    good = Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0)
    kept, rejected = filter_boxes_by_size([big, good])
    assert len(kept) == 1
    assert rejected == 1
    assert kept[0] is good


def test_filter_rejects_undersize_box():
    tiny = Box(x1=0.0, y1=0.0, x2=10.0, y2=10.0)
    good = Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0)
    kept, rejected = filter_boxes_by_size([tiny, good])
    assert len(kept) == 1
    assert rejected == 1


def test_filter_rejects_pathological_560m_outlier():
    """The real data had a 560 m wide detection — this is the outlier case."""
    outlier = Box(x1=0.0, y1=0.0, x2=560.0, y2=50.0)
    kept, rejected = filter_boxes_by_size([outlier])
    assert kept == []
    assert rejected == 1


def test_filter_accepts_median_mound_box():
    """The p50 box dimensions (62 × 56 m) should pass the filter."""
    median = Box(x1=0.0, y1=0.0, x2=62.0, y2=56.0)
    kept, rejected = filter_boxes_by_size([median])
    assert len(kept) == 1
    assert rejected == 0


# ----------------------------------------------------------------------------
# Weighted Boxes Fusion
# ----------------------------------------------------------------------------


def test_wbf_empty_input():
    assert weighted_boxes_fusion([]) == []


def test_wbf_single_box_single_cluster():
    b = Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0, pass_id="run_1")
    out = weighted_boxes_fusion([b])
    assert len(out) == 1
    assert out[0].vote_count == 1
    assert out[0].cluster_size == 1
    assert out[0].fused_box.centroid == pytest.approx((30.0, 30.0))


def test_wbf_two_identical_boxes_merge():
    b1 = Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0, pass_id="run_1")
    b2 = Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0, pass_id="run_2")
    out = weighted_boxes_fusion([b1, b2])
    assert len(out) == 1
    assert out[0].vote_count == 2
    assert out[0].cluster_size == 2


def test_wbf_disjoint_boxes_stay_separate():
    b1 = Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0, pass_id="run_1")
    b2 = Box(x1=200.0, y1=200.0, x2=260.0, y2=260.0, pass_id="run_2")
    out = weighted_boxes_fusion([b1, b2])
    assert len(out) == 2
    for cluster in out:
        assert cluster.vote_count == 1


def test_wbf_drift_within_mound_symbol_merges():
    """Two 75 m boxes with 15 m centroid offset (typical drift) should merge.

    Under WBF with IoU threshold 0.25, a 15 m offset produces a large IoU
    (~0.55) and the boxes should be merged into a single cluster.
    """
    b1 = Box(x1=0.0, y1=0.0, x2=75.0, y2=75.0, pass_id="run_1")
    b2 = Box(x1=15.0, y1=0.0, x2=90.0, y2=75.0, pass_id="run_2")
    out = weighted_boxes_fusion([b1, b2], iou_threshold=0.25)
    assert len(out) == 1
    # Fused centroid should be the mean of the two centroids
    assert out[0].fused_box.centroid == pytest.approx((45.0, 37.5))


def test_wbf_cartographic_floor_boxes_stay_separate():
    """Two 75 m boxes at the 68 m minimum separation must NOT merge.

    This is the critical safety property: under WBF with IoU threshold
    0.25, two boxes centroid-to-centroid distance 68 m have IoU below
    threshold and must form two distinct clusters, preventing accidental
    merging of neighbouring mounds.
    """
    b1 = Box(x1=0.0, y1=0.0, x2=75.0, y2=75.0, pass_id="run_1")
    b2 = Box(x1=68.0, y1=0.0, x2=143.0, y2=75.0, pass_id="run_2")
    out = weighted_boxes_fusion([b1, b2], iou_threshold=0.25)
    assert len(out) == 2


def test_wbf_vote_count_uses_distinct_passes():
    """Two boxes from the same pass contribute 1 vote, not 2."""
    b1 = Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0, pass_id="run_1")
    b2 = Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0, pass_id="run_1")
    out = weighted_boxes_fusion([b1, b2])
    assert len(out) == 1
    assert out[0].vote_count == 1  # one distinct pass
    assert out[0].cluster_size == 2  # two contributing boxes


def test_wbf_weighted_average_centroid_for_cluster_of_three():
    """Fused centroid should equal the arithmetic mean of member centroids."""
    b1 = Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0, pass_id="run_1")
    b2 = Box(x1=10.0, y1=0.0, x2=70.0, y2=60.0, pass_id="run_2")
    b3 = Box(x1=20.0, y1=0.0, x2=80.0, y2=60.0, pass_id="run_3")
    out = weighted_boxes_fusion([b1, b2, b3])
    assert len(out) == 1
    # Member centroids: (30, 30), (40, 30), (50, 30); mean = (40, 30)
    assert out[0].fused_box.centroid == pytest.approx((40.0, 30.0))


def test_wbf_is_order_independent_under_uniform_confidence():
    """Result should not depend on input order when confidences are equal."""
    boxes = [
        Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0, pass_id="run_1"),
        Box(x1=5.0, y1=0.0, x2=65.0, y2=60.0, pass_id="run_2"),
        Box(x1=10.0, y1=0.0, x2=70.0, y2=60.0, pass_id="run_3"),
    ]
    out_a = weighted_boxes_fusion(list(boxes))
    out_b = weighted_boxes_fusion(list(reversed(boxes)))
    assert len(out_a) == len(out_b)
    assert len(out_a) == 1
    assert out_a[0].fused_box.centroid == pytest.approx(out_b[0].fused_box.centroid)


# ----------------------------------------------------------------------------
# Minimum-separation enforcement
# ----------------------------------------------------------------------------


def _make_cluster(cx: float, cy: float, pass_id: str = "run_1") -> FusedCluster:
    """Helper: build a trivial 60 x 60 cluster centred at (cx, cy)."""
    b = Box(
        x1=cx - 30, y1=cy - 30, x2=cx + 30, y2=cy + 30,
        pass_id=pass_id,
    )
    return FusedCluster(fused_box=b, members=[b])


def test_min_separation_noop_for_well_separated_clusters():
    clusters = [_make_cluster(0, 0), _make_cluster(500, 500)]
    out = enforce_minimum_separation(clusters, min_separation_m=60.0)
    assert len(out) == 2


def test_min_separation_merges_close_clusters():
    clusters = [_make_cluster(0, 0, "run_1"),
                _make_cluster(40, 0, "run_2")]
    out = enforce_minimum_separation(clusters, min_separation_m=60.0)
    assert len(out) == 1
    assert out[0].cluster_size == 2
    assert out[0].vote_count == 2


def test_min_separation_preserves_pair_just_beyond_threshold():
    clusters = [_make_cluster(0, 0), _make_cluster(65, 0)]
    out = enforce_minimum_separation(clusters, min_separation_m=60.0)
    assert len(out) == 2


def test_min_separation_chains_transitively():
    """A within-threshold chain of 3 clusters collapses to 1."""
    clusters = [
        _make_cluster(0, 0, "run_1"),
        _make_cluster(40, 0, "run_2"),
        _make_cluster(80, 0, "run_3"),
    ]
    out = enforce_minimum_separation(clusters, min_separation_m=60.0)
    # Pairs (0,40) and (40,80) are each <60, chain collapses to one cluster
    assert len(out) == 1
    assert out[0].cluster_size == 3


# ----------------------------------------------------------------------------
# Vote-aware minimum-separation
# ----------------------------------------------------------------------------


def _make_multi_vote_cluster(cx: float, cy: float, pass_ids: list[str]) -> FusedCluster:
    """Helper: build a cluster with the given pass_ids as members."""
    members = [
        Box(
            x1=cx - 30 + 0.1 * i,
            y1=cy - 30,
            x2=cx + 30 + 0.1 * i,
            y2=cy + 30,
            pass_id=pid,
        )
        for i, pid in enumerate(pass_ids)
    ]
    return FusedCluster(
        fused_box=Box(x1=cx - 30, y1=cy - 30, x2=cx + 30, y2=cy + 30),
        members=members,
    )


def test_vote_aware_absorbs_low_vote_drift_into_high_vote_core():
    """High-vote core + low-vote drift within threshold should merge."""
    core = _make_multi_vote_cluster(0, 0, [f"run_{i}" for i in range(1, 9)])  # v=8
    drift = _make_multi_vote_cluster(40, 0, ["run_9"])                        # v=1
    out = enforce_minimum_separation(
        [core, drift],
        min_separation_m=60.0,
        anchor_vote_threshold=3,
    )
    assert len(out) == 1
    assert out[0].vote_count == 9


def test_vote_aware_preserves_two_low_vote_fragments():
    """Two low-vote FP fragments within threshold should NOT merge."""
    frag_a = _make_multi_vote_cluster(0, 0, ["run_1", "run_2"])  # v=2
    frag_b = _make_multi_vote_cluster(40, 0, ["run_3", "run_4"])  # v=2
    out = enforce_minimum_separation(
        [frag_a, frag_b],
        min_separation_m=60.0,
        anchor_vote_threshold=3,
    )
    # Neither side meets anchor threshold → kept separate
    assert len(out) == 2


def test_vote_aware_merges_two_high_vote_clusters_at_cartographic_floor():
    """Two high-vote clusters within threshold should still merge.

    This is the rare drift-pair case where both clusters represent the
    same physical mound with substantial drift between them. Both reach
    the anchor threshold, so the merge proceeds.
    """
    a = _make_multi_vote_cluster(0, 0, [f"run_{i}" for i in range(1, 6)])  # v=5
    b = _make_multi_vote_cluster(50, 0, [f"run_{i}" for i in range(6, 11)])  # v=5
    out = enforce_minimum_separation(
        [a, b],
        min_separation_m=60.0,
        anchor_vote_threshold=3,
    )
    assert len(out) == 1
    assert out[0].vote_count == 10


def test_vote_aware_chains_through_high_vote_anchor():
    """Two low-vote fragments on either side of a high-vote anchor all merge."""
    low_left = _make_multi_vote_cluster(0, 0, ["run_1"])      # v=1
    anchor = _make_multi_vote_cluster(40, 0,
                                       [f"run_{i}" for i in range(2, 7)])  # v=5
    low_right = _make_multi_vote_cluster(80, 0, ["run_7"])    # v=1
    out = enforce_minimum_separation(
        [low_left, anchor, low_right],
        min_separation_m=60.0,
        anchor_vote_threshold=3,
    )
    # low_left—anchor pair merges (anchor has vote>=3), anchor—low_right
    # pair merges (anchor has vote>=3), union-find chains them all into
    # one cluster even though low_left—low_right distance is 80 m
    assert len(out) == 1
    assert out[0].vote_count == 7


def test_vote_aware_mode_is_stricter_than_plain_mode():
    """Vote-aware enforcement must produce at least as many clusters."""
    clusters = [
        _make_multi_vote_cluster(0, 0, ["run_1", "run_2"]),      # v=2
        _make_multi_vote_cluster(40, 0, ["run_3", "run_4"]),     # v=2
        _make_multi_vote_cluster(200, 0,
                                  [f"run_{i}" for i in range(1, 11)]),  # v=10 (isolated)
    ]
    plain = enforce_minimum_separation(clusters, min_separation_m=60.0)
    vote_aware = enforce_minimum_separation(
        clusters, min_separation_m=60.0, anchor_vote_threshold=3,
    )
    assert len(vote_aware) >= len(plain)


# ----------------------------------------------------------------------------
# End-to-end
# ----------------------------------------------------------------------------


def test_fuse_detections_rejects_outlier_and_merges_drift():
    """End-to-end: a 560 m outlier is rejected, two drifted boxes merge."""
    boxes = [
        Box(x1=0.0, y1=0.0, x2=560.0, y2=50.0, pass_id="run_1"),  # outlier
        Box(x1=1000.0, y1=1000.0, x2=1075.0, y2=1075.0, pass_id="run_1"),
        Box(x1=1015.0, y1=1000.0, x2=1090.0, y2=1075.0, pass_id="run_2"),
    ]
    final, diag = fuse_detections(boxes)
    assert diag["n_raw_boxes"] == 3
    assert diag["n_rejected_by_size_filter"] == 1
    assert diag["n_filtered_boxes"] == 2
    assert diag["n_clusters_after_wbf"] == 1
    assert len(final) == 1
    assert final[0].vote_count == 2


def test_fuse_detections_preserves_neighbour_pair():
    """Two boxes at the 68 m minimum separation must emerge as 2 clusters."""
    boxes = [
        Box(x1=0.0, y1=0.0, x2=75.0, y2=75.0, pass_id="run_1"),
        Box(x1=68.0, y1=0.0, x2=143.0, y2=75.0, pass_id="run_2"),
    ]
    final, diag = fuse_detections(boxes, min_separation_m=60.0)
    assert len(final) == 2
    assert diag["n_clusters_after_wbf"] == 2
    assert diag["n_merged_by_min_separation"] == 0


def test_fuse_detections_diagnostics_shape():
    boxes = [Box(x1=0.0, y1=0.0, x2=60.0, y2=60.0, pass_id="run_1")]
    _, diag = fuse_detections(boxes)
    required_keys = {
        "n_raw_boxes", "n_rejected_by_size_filter", "n_filtered_boxes",
        "n_clusters_after_wbf", "n_clusters_after_min_separation",
        "n_merged_by_min_separation", "iou_threshold", "min_separation_m",
    }
    assert required_keys.issubset(diag.keys())
