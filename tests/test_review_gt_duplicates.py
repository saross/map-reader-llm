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
