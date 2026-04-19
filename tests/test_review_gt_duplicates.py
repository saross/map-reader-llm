"""Tier-1 deterministic unit tests for ``scripts/review_gt_duplicates``.

Tests the clustering algorithm and the decision-apply logic on small
synthetic fixtures. Does not exercise Streamlit, rasterio, or PIL (those
would be tier-2 / integration tests).

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point

from scripts.review_gt_duplicates import (
    Cluster,
    DECISION_KEEP_ALL,
    DECISION_KEEP_ONLY,
    DECISION_MERGE,
    DECISION_UNCERTAIN,
    apply_decisions,
    build_clusters,
    decisions_index,
    detect_overlapping_decisions,
    find_subsumed_decisions,
    format_decision,
    load_decisions,
    save_decisions,
)


# =========================================================================
# Helpers
# =========================================================================


def _make_gt(rows: list[dict]) -> gpd.GeoDataFrame:
    """Build a minimal GT geodataframe matching the production schema."""
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32635")
    gdf = gdf.reset_index(drop=True)
    gdf["_gt_row_id"] = gdf.index.astype(int)
    return gdf


# =========================================================================
# Clustering
# =========================================================================


@pytest.mark.tier1
def test_build_clusters_pair_below_threshold() -> None:
    """Two points 10 m apart at threshold 50 m form a single 2-member cluster."""
    gt = _make_gt([
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(100.0, 200.0)},
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(110.0, 200.0)},
    ])
    clusters = build_clusters(gt, threshold_m=50.0)
    assert len(clusters) == 1
    c = clusters[0]
    assert c.n_points == 2
    assert c.map_id == "M1"
    assert sorted(c.point_ids) == [0, 1]
    assert c.pairwise_distances_m == [10.0]
    assert c.centroid == (105.0, 200.0)


@pytest.mark.tier1
def test_build_clusters_triplet_transitive() -> None:
    """A-B and B-C both <threshold → cluster {A,B,C}, even if A-C > threshold."""
    # A at 0, B at 40, C at 80 → A-B=40, B-C=40, A-C=80. Threshold 50.
    gt = _make_gt([
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(0.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(40.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(80.0, 0.0)},
    ])
    clusters = build_clusters(gt, threshold_m=50.0)
    assert len(clusters) == 1
    c = clusters[0]
    assert c.n_points == 3
    assert sorted(c.point_ids) == [0, 1, 2]
    # All three pairwise distances recorded
    assert sorted(c.pairwise_distances_m) == [40.0, 40.0, 80.0]


@pytest.mark.tier1
def test_build_clusters_separate_maps_never_merge() -> None:
    """Co-located points on different maps stay in separate clusters (trivially: no clusters)."""
    gt = _make_gt([
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(100.0, 200.0)},
        {"source_map": "M2", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(100.0, 200.0)},
    ])
    clusters = build_clusters(gt, threshold_m=50.0)
    # Each map has only one point → no multi-point clusters
    assert clusters == []


@pytest.mark.tier1
def test_build_clusters_isolated_points_excluded() -> None:
    """Points with no neighbour within threshold are not reported as clusters."""
    gt = _make_gt([
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(0.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(1000.0, 0.0)},  # 1 km from anything
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(10.0, 0.0)},  # forms a cluster with row 0
    ])
    clusters = build_clusters(gt, threshold_m=50.0)
    assert len(clusters) == 1
    # Cluster should contain rows 0 and 2, not row 1
    assert sorted(clusters[0].point_ids) == [0, 2]


@pytest.mark.tier1
def test_build_clusters_deterministic_ordering() -> None:
    """Clusters come back in stable (map_id, min_point_id) order."""
    gt = _make_gt([
        {"source_map": "B", "FeatureType": "M", "MapSymbol": "X",
         "geometry": Point(0.0, 0.0)},
        {"source_map": "B", "FeatureType": "M", "MapSymbol": "X",
         "geometry": Point(5.0, 0.0)},
        {"source_map": "A", "FeatureType": "M", "MapSymbol": "X",
         "geometry": Point(0.0, 0.0)},
        {"source_map": "A", "FeatureType": "M", "MapSymbol": "X",
         "geometry": Point(5.0, 0.0)},
    ])
    clusters = build_clusters(gt, threshold_m=20.0)
    assert len(clusters) == 2
    assert clusters[0].map_id == "A"
    assert clusters[1].map_id == "B"


@pytest.mark.tier1
def test_suggest_subtype_single_majority() -> None:
    """Consensus subtype = majority MapSymbol's mapped subtype."""
    cluster = Cluster(
        cluster_id="M1_c00001",
        map_id="M1",
        point_ids=[1, 2, 3],
        coords=[(0, 0), (5, 0), (10, 0)],
        feature_types=["Mound"] * 3,
        map_symbols=[
            "Hairy brown circle",  # → burial_mound
            "Hairy brown circle",  # → burial_mound
            "Hairy black triangle with a dot inside",  # → trig_point_on_mound
        ],
        pairwise_distances_m=[5.0, 5.0, 10.0],
        centroid=(5.0, 0.0),
    )
    assert cluster.suggest_subtype() == "burial_mound"


@pytest.mark.tier1
def test_suggest_subtype_tie_deterministic() -> None:
    """Ties resolve deterministically via cluster_id-seeded RNG."""
    cluster = Cluster(
        cluster_id="M1_c00042",
        map_id="M1",
        point_ids=[1, 2],
        coords=[(0, 0), (5, 0)],
        feature_types=["Mound", "Mound"],
        map_symbols=[
            "Hairy brown circle",
            "Hairy black diamond with a dot inside",
        ],
        pairwise_distances_m=[5.0],
        centroid=(2.5, 0.0),
    )
    # Two calls must agree (deterministic) and must return one of the two tied
    # subtypes.
    s1 = cluster.suggest_subtype()
    s2 = cluster.suggest_subtype()
    assert s1 == s2
    assert s1 in {"burial_mound", "bench_mark_on_mound"}


# =========================================================================
# Apply decisions
# =========================================================================


def _sample_gt() -> gpd.GeoDataFrame:
    return _make_gt([
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "uuid": "u0", "geometry": Point(100.0, 200.0)},
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "uuid": "u1", "geometry": Point(110.0, 200.0)},
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "uuid": "u2", "geometry": Point(500.0, 500.0)},  # isolated
    ])


@pytest.mark.tier1
def test_apply_keep_all_noop() -> None:
    """keep_all leaves both rows untouched."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    assert len(clusters) == 1
    d = format_decision(clusters[0], DECISION_KEEP_ALL)
    cleaned, counts = apply_decisions(gt, {d["cluster_id"]: d})
    assert len(cleaned) == 3
    assert counts == {"keep_all": 1, "merge": 0, "keep_only": 0,
                      "uncertain": 0}


@pytest.mark.tier1
def test_apply_merge_to_centroid() -> None:
    """merge drops cluster rows, appends one point at centroid."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    d = format_decision(
        clusters[0], DECISION_MERGE, merged_subtype="burial_mound",
    )
    cleaned, counts = apply_decisions(gt, {d["cluster_id"]: d})
    # Original 3 rows → 1 isolated + 1 merged = 2 rows
    assert len(cleaned) == 2
    assert counts["merge"] == 1
    merged = cleaned[cleaned["_merged"]]
    assert len(merged) == 1
    m = merged.iloc[0]
    assert m.geometry.x == pytest.approx(105.0)
    assert m.geometry.y == pytest.approx(200.0)
    assert m["_reviewed_subtype"] == "burial_mound"
    assert m["uuid"].startswith("merged-")


@pytest.mark.tier1
def test_apply_keep_only_single() -> None:
    """keep_only retains only the listed row ids from the cluster."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    d = format_decision(
        clusters[0], DECISION_KEEP_ONLY, kept_row_ids=[0],
    )
    cleaned, counts = apply_decisions(gt, {d["cluster_id"]: d})
    assert len(cleaned) == 2
    assert counts["keep_only"] == 1
    assert set(cleaned["_gt_row_id"].tolist()) == {0, 2}


@pytest.mark.tier1
def test_apply_uncertain_passthrough() -> None:
    """uncertain leaves all cluster rows present + counts increments."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    d = format_decision(clusters[0], DECISION_UNCERTAIN)
    cleaned, counts = apply_decisions(gt, {d["cluster_id"]: d})
    assert len(cleaned) == 3
    assert counts == {"keep_all": 0, "merge": 0, "keep_only": 0,
                      "uncertain": 1}


@pytest.mark.tier1
def test_apply_idempotent(tmp_path: Path) -> None:
    """Applying the same decisions twice produces identical outputs."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    d = format_decision(
        clusters[0], DECISION_MERGE, merged_subtype="burial_mound",
    )
    decisions = {d["cluster_id"]: d}

    out1, _ = apply_decisions(gt, decisions)
    out2, _ = apply_decisions(gt, decisions)

    # Row counts + geometry coords + subtype match
    assert len(out1) == len(out2)
    p1 = sorted((g.x, g.y) for g in out1.geometry)
    p2 = sorted((g.x, g.y) for g in out2.geometry)
    assert p1 == p2
    s1 = sorted(out1["_reviewed_subtype"].fillna("").tolist())
    s2 = sorted(out2["_reviewed_subtype"].fillna("").tolist())
    assert s1 == s2


@pytest.mark.tier1
def test_csv_roundtrip(tmp_path: Path) -> None:
    """save_decisions + load_decisions yield the same dict (string-typed)."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    d = format_decision(
        clusters[0], DECISION_MERGE, merged_subtype="burial_mound",
    )
    decisions = {d["cluster_id"]: d}
    csv_path = tmp_path / "decisions.csv"
    save_decisions(decisions, csv_path)
    loaded = load_decisions(csv_path)
    assert set(loaded.keys()) == set(decisions.keys())
    for cid in decisions:
        # All values round-trip as strings (CSV semantics)
        for k in decisions[cid]:
            assert str(decisions[cid][k]) == str(loaded[cid][k])


@pytest.mark.tier1
def test_apply_unknown_decision_raises() -> None:
    """Unknown decision codes raise ValueError rather than silent skip."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    d = format_decision(clusters[0], DECISION_KEEP_ALL)
    d["decision"] = "merrge"  # typo
    with pytest.raises(ValueError, match="unrecognised code"):
        apply_decisions(gt, {d["cluster_id"]: d})


@pytest.mark.tier1
def test_apply_merge_nan_centroid_raises() -> None:
    """Merge with non-finite centroid coordinates raises rather than writes NaN."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    d = format_decision(
        clusters[0], DECISION_MERGE, merged_subtype="burial_mound",
    )
    d["merged_centroid_x"] = ""
    d["merged_centroid_y"] = ""
    with pytest.raises(ValueError, match="non-finite centroid"):
        apply_decisions(gt, {d["cluster_id"]: d})


@pytest.mark.tier1
def test_apply_keep_only_empty_raises() -> None:
    """keep_only with no kept points raises."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    d = format_decision(clusters[0], DECISION_KEEP_ONLY, kept_row_ids=[])
    with pytest.raises(ValueError, match="point_ids_kept is empty"):
        apply_decisions(gt, {d["cluster_id"]: d})


@pytest.mark.tier1
def test_apply_keep_only_stranger_raises() -> None:
    """keep_only referencing a row_id outside the cluster raises."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    # Cluster's point_ids_in is [0, 1]; 999 is not in the cluster.
    d = format_decision(clusters[0], DECISION_KEEP_ONLY, kept_row_ids=[999])
    with pytest.raises(ValueError, match="not in the cluster"):
        apply_decisions(gt, {d["cluster_id"]: d})


# =========================================================================
# Multi-threshold workflow: subsumption + overlap detection
# =========================================================================


@pytest.mark.tier1
def test_decisions_index_maps_member_sets_to_cluster_ids() -> None:
    """decisions_index is keyed by frozenset of point_ids_in."""
    gt = _sample_gt()
    clusters = build_clusters(gt, threshold_m=50.0)
    d = format_decision(
        clusters[0], DECISION_MERGE, merged_subtype="burial_mound",
    )
    idx = decisions_index({d["cluster_id"]: d})
    assert idx == {frozenset({0, 1}): d["cluster_id"]}


@pytest.mark.tier1
def test_find_subsumed_decisions_proper_subset() -> None:
    """A cluster {A,B,C} finds the prior decision {A,B} as subsumed."""
    # Build GT with three nearby points: 0 @ 0m, 1 @ 10m, 2 @ 40m.
    gt = _make_gt([
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(0.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(10.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(40.0, 0.0)},
    ])
    # At 20 m: only {0, 1} are a cluster.
    tight = build_clusters(gt, threshold_m=20.0)
    assert len(tight) == 1
    tight_cluster = tight[0]
    tight_decision = format_decision(
        tight_cluster, DECISION_MERGE, merged_subtype="burial_mound",
    )
    decisions = {tight_decision["cluster_id"]: tight_decision}
    # At 50 m: all three form one cluster.
    wide = build_clusters(gt, threshold_m=50.0)
    assert len(wide) == 1
    wide_cluster = wide[0]
    assert wide_cluster.n_points == 3
    subsumed = find_subsumed_decisions(wide_cluster, decisions)
    assert len(subsumed) == 1
    subsumed_cid, subsumed_pts = subsumed[0]
    assert subsumed_cid == tight_decision["cluster_id"]
    assert subsumed_pts == {0, 1}


@pytest.mark.tier1
def test_find_subsumed_decisions_disjoint_is_empty() -> None:
    """A cluster with no common points returns no subsumed decisions."""
    gt = _make_gt([
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(0.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(10.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(1000.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(1010.0, 0.0)},
    ])
    clusters = build_clusters(gt, threshold_m=50.0)
    assert len(clusters) == 2
    # Decide on the first cluster
    d0 = format_decision(clusters[0], DECISION_KEEP_ALL)
    decisions = {d0["cluster_id"]: d0}
    # The second cluster has no common members with the first
    subsumed = find_subsumed_decisions(clusters[1], decisions)
    assert subsumed == []


@pytest.mark.tier1
def test_detect_overlapping_decisions_proper_overlap() -> None:
    """Two decisions sharing any point id are flagged as overlapping."""
    # Points at 0, 10, 40: pairwise distances 10, 30, 40.
    #   threshold 15 m → only {0, 1}
    #   threshold 35 m → {0, 1, 2} via transitive (0-1) + (1-2)
    gt = _make_gt([
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(0.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(10.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound", "MapSymbol": "X",
         "geometry": Point(40.0, 0.0)},
    ])
    tight = build_clusters(gt, threshold_m=15.0)
    wide = build_clusters(gt, threshold_m=35.0)
    assert tight[0].n_points == 2
    assert wide[0].n_points == 3
    d_tight = format_decision(
        tight[0], DECISION_MERGE, merged_subtype="burial_mound",
    )
    d_wide = format_decision(
        wide[0], DECISION_MERGE, merged_subtype="burial_mound",
    )
    # The two decisions' cluster_ids will collide under the normal
    # min-point-id convention, so override one to exercise the
    # overlap detection path (simulates a manually-edited CSV).
    d_wide_alt = dict(d_wide)
    d_wide_alt["cluster_id"] = "extended_cluster"
    overlaps = detect_overlapping_decisions({
        d_tight["cluster_id"]: d_tight,
        "extended_cluster": d_wide_alt,
    })
    assert len(overlaps) == 1
    c1, c2, shared = overlaps[0]
    assert {c1, c2} == {d_tight["cluster_id"], "extended_cluster"}
    assert shared == {0, 1}  # members common to both


@pytest.mark.tier1
def test_detect_overlapping_decisions_disjoint_empty() -> None:
    """Decisions with disjoint member sets produce no overlaps."""
    d1 = {"cluster_id": "a", "point_ids_in": "1;2"}
    d2 = {"cluster_id": "b", "point_ids_in": "3;4"}
    assert detect_overlapping_decisions({"a": d1, "b": d2}) == []


@pytest.mark.tier1
def test_apply_decisions_raises_on_overlapping_decisions() -> None:
    """apply_decisions refuses to run if the CSV contains overlapping entries."""
    gt = _sample_gt()
    # Two decisions both acting on point 0 — manually constructed to
    # simulate a stale CSV that missed subsumption cleanup.
    d1 = {
        "cluster_id": "c1", "map_id": "M1", "n_points": "2",
        "point_ids_in": "0;1", "pairwise_distances_m": "10.0",
        "decision": DECISION_KEEP_ALL,
        "point_ids_kept": "0;1",
        "merged_subtype": "", "merged_centroid_x": "",
        "merged_centroid_y": "", "timestamp": "2026-01-01T00:00:00+00:00",
    }
    d2 = dict(d1)
    d2["cluster_id"] = "c2"
    d2["point_ids_in"] = "0;2"  # shares point 0 with d1
    with pytest.raises(ValueError, match="Overlapping decisions"):
        apply_decisions(gt, {"c1": d1, "c2": d2})


@pytest.mark.tier1
def test_apply_decisions_raises_on_stale_in_ids() -> None:
    """apply_decisions refuses to run if a decision references row_ids
    that no longer exist in the GT."""
    gt = _sample_gt()  # has rows 0, 1, 2
    d = {
        "cluster_id": "c_stale", "map_id": "M1", "n_points": "2",
        "point_ids_in": "999;1000",  # neither exists in _sample_gt
        "pairwise_distances_m": "10.0", "decision": DECISION_KEEP_ALL,
        "point_ids_kept": "999;1000",
        "merged_subtype": "", "merged_centroid_x": "",
        "merged_centroid_y": "", "timestamp": "2026-01-01T00:00:00+00:00",
    }
    with pytest.raises(ValueError, match="no longer exist"):
        apply_decisions(gt, {"c_stale": d})


# =========================================================================
# Subsumption-save and multi-threshold round-trip
# =========================================================================


def _make_wide_gt() -> gpd.GeoDataFrame:
    """Three collinear points at 0, 10, 40 — threshold 15 → {0,1};
    threshold 35 → {0,1,2} via transitive closure."""
    return _make_gt([
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(0.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(10.0, 0.0)},
        {"source_map": "M1", "FeatureType": "Mound",
         "MapSymbol": "Hairy brown circle",
         "geometry": Point(40.0, 0.0)},
    ])


@pytest.mark.tier1
def test_save_decision_returns_subsumed_as_dict(tmp_path: Path) -> None:
    """_save_decision returns the removed decisions as a cid→dict map
    so the UI can stash them for Back-button restoration."""
    from scripts.review_gt_duplicates import _save_decision

    gt = _make_wide_gt()
    tight = build_clusters(gt, threshold_m=15.0)[0]
    wide = build_clusters(gt, threshold_m=35.0)[0]
    # Both have the same auto-generated cluster_id (both min 0).
    # Manually distinguish them so subsumption actually triggers.
    tight.cluster_id = f"{tight.cluster_id}_tight"
    wide.cluster_id = f"{wide.cluster_id}_wide"

    csv_path = tmp_path / "decisions.csv"
    decisions: dict[str, dict] = {}
    history: list[str] = []

    # Tight pass: save, nothing subsumed.
    removed_tight = _save_decision(
        tight, DECISION_MERGE, decisions, history, csv_path,
        merged_subtype="burial_mound",
    )
    assert removed_tight == {}
    assert tight.cluster_id in decisions
    assert history == [tight.cluster_id]

    # Wide pass: saves and subsumes the tight decision.
    removed_wide = _save_decision(
        wide, DECISION_MERGE, decisions, history, csv_path,
        merged_subtype="burial_mound",
    )
    assert set(removed_wide.keys()) == {tight.cluster_id}
    assert removed_wide[tight.cluster_id]["decision"] == DECISION_MERGE
    assert tight.cluster_id not in decisions
    assert tight.cluster_id not in history
    assert wide.cluster_id in decisions
    assert history == [wide.cluster_id]


@pytest.mark.tier1
def test_save_decision_dedupes_history_on_repeat(tmp_path: Path) -> None:
    """Re-deciding on the same cluster doesn't accumulate duplicate
    history entries — Back should be a single-press undo."""
    from scripts.review_gt_duplicates import _save_decision

    gt = _sample_gt()
    cluster = build_clusters(gt, threshold_m=50.0)[0]
    csv_path = tmp_path / "decisions.csv"
    decisions: dict[str, dict] = {}
    history: list[str] = []

    _save_decision(cluster, DECISION_KEEP_ALL, decisions, history, csv_path)
    _save_decision(cluster, DECISION_UNCERTAIN, decisions, history, csv_path)
    _save_decision(
        cluster, DECISION_MERGE, decisions, history, csv_path,
        merged_subtype="burial_mound",
    )
    # After three successive decisions on the same cluster, history
    # should contain its cid exactly once.
    assert history.count(cluster.cluster_id) == 1
    assert decisions[cluster.cluster_id]["decision"] == DECISION_MERGE


@pytest.mark.tier1
def test_multi_threshold_round_trip(tmp_path: Path) -> None:
    """Tight-then-wide workflow: save at tight, reload, verify
    exact-match auto-skip + superset detection on the wider pass."""
    from scripts.review_gt_duplicates import _save_decision

    gt = _make_wide_gt()
    csv_path = tmp_path / "decisions.csv"
    decisions: dict[str, dict] = {}
    history: list[str] = []

    # Tight pass at threshold 15: one cluster {0,1}, save merge.
    tight_clusters = build_clusters(gt, threshold_m=15.0)
    assert len(tight_clusters) == 1 and tight_clusters[0].n_points == 2
    _save_decision(
        tight_clusters[0], DECISION_MERGE, decisions, history, csv_path,
        merged_subtype="burial_mound",
    )
    # Simulate a fresh launch by reloading decisions from the CSV.
    loaded = load_decisions(csv_path)
    assert len(loaded) == 1

    # Wider pass at threshold 35: one cluster {0,1,2}.
    wide_clusters = build_clusters(gt, threshold_m=35.0)
    assert len(wide_clusters) == 1 and wide_clusters[0].n_points == 3
    wide_cluster = wide_clusters[0]

    # Exact-match index contains the tight set, not the wide set.
    idx = decisions_index(loaded)
    assert frozenset({0, 1}) in idx
    assert frozenset({0, 1, 2}) not in idx

    # find_subsumed on the wide cluster identifies the tight decision.
    subsumed = find_subsumed_decisions(wide_cluster, loaded)
    assert len(subsumed) == 1
    _, subsumed_pts = subsumed[0]
    assert subsumed_pts == {0, 1}


@pytest.mark.tier1
def test_find_subsumed_equal_set_different_cluster_id() -> None:
    """Two decisions with equal member sets but different cluster_ids
    (manually-edited CSV scenario) are caught by find_subsumed, so
    a re-decide replaces the stale entry rather than producing an
    overlap in --apply."""
    gt = _sample_gt()
    cluster = build_clusters(gt, threshold_m=50.0)[0]
    d_stale = format_decision(cluster, DECISION_KEEP_ALL)
    d_stale["cluster_id"] = "stale_cid"  # simulate renamed CSV entry
    decisions = {"stale_cid": d_stale}
    # find_subsumed on the current cluster should see stale_cid.
    subsumed = find_subsumed_decisions(cluster, decisions)
    assert len(subsumed) == 1
    assert subsumed[0][0] == "stale_cid"
