"""
Tier 1 unit tests for scripts/probe_verifier_independence.py.

Covers union-find correctness, cross-config spatial clustering, set-overlap
counts, pairwise correlation, ICC(2,1) absolute agreement against a known
analytical answer, and the verdict logic for each of H-A / H-B / H-C and the
inconclusive branch.
"""

import math

import numpy as np
import pandas as pd
import pytest

from scripts.probe_verifier_independence import (
    UnionFind,
    cluster_across_configs,
    cluster_membership_table,
    complete_case_stats,
    icc_2_1_absolute,
    overlap_summary,
    pairwise_correlations,
    render_verdict,
)

pytestmark = pytest.mark.tier1


# ----------------------------------------------------------------------------
# UnionFind
# ----------------------------------------------------------------------------


def test_union_find_basic_merging():
    uf = UnionFind(5)
    uf.union(0, 1)
    uf.union(1, 2)
    uf.union(3, 4)
    assert uf.find(0) == uf.find(2)
    assert uf.find(3) == uf.find(4)
    assert uf.find(0) != uf.find(3)


def test_union_find_idempotent_union():
    uf = UnionFind(3)
    uf.union(0, 1)
    uf.union(0, 1)  # repeated union must be a no-op
    uf.union(1, 0)
    assert uf.find(0) == uf.find(1)
    assert uf.find(2) != uf.find(0)


# ----------------------------------------------------------------------------
# Cross-config spatial clustering
# ----------------------------------------------------------------------------


def _pooled_fixture() -> pd.DataFrame:
    """Three physical points; configs A and B share two of them.

    Point P1 at (0,0), P2 at (100,0), P3 at (200,0). Config A has all three;
    config B has P1 and P2 only (with a small offset within the buffer).
    """
    return pd.DataFrame(
        [
            {"config": "A", "candidate_id": 0, "x": 0.0, "y": 0.0,
             "vote_count": 5, "mound_probability": 0.9},
            {"config": "A", "candidate_id": 1, "x": 100.0, "y": 0.0,
             "vote_count": 4, "mound_probability": 0.6},
            {"config": "A", "candidate_id": 2, "x": 200.0, "y": 0.0,
             "vote_count": 3, "mound_probability": 0.2},
            {"config": "B", "candidate_id": 0, "x": 1.0, "y": 0.0,
             "vote_count": 5, "mound_probability": 0.85},
            {"config": "B", "candidate_id": 1, "x": 101.0, "y": 0.0,
             "vote_count": 4, "mound_probability": 0.55},
        ]
    )


def test_cluster_across_configs_links_within_buffer():
    pooled = _pooled_fixture()
    clustered = cluster_across_configs(pooled, buffer_m=20.0)
    a_p1 = clustered[(clustered.config == "A") & (clustered.candidate_id == 0)]
    b_p1 = clustered[(clustered.config == "B") & (clustered.candidate_id == 0)]
    assert a_p1.iloc[0]["cluster_id"] == b_p1.iloc[0]["cluster_id"]
    a_p3 = clustered[(clustered.config == "A") & (clustered.candidate_id == 2)]
    assert a_p3.iloc[0]["cluster_id"] != a_p1.iloc[0]["cluster_id"]


def test_cluster_across_configs_respects_buffer():
    pooled = _pooled_fixture()
    clustered = cluster_across_configs(pooled, buffer_m=0.5)
    a_p1 = clustered[(clustered.config == "A") & (clustered.candidate_id == 0)]
    b_p1 = clustered[(clustered.config == "B") & (clustered.candidate_id == 0)]
    assert a_p1.iloc[0]["cluster_id"] != b_p1.iloc[0]["cluster_id"]


# ----------------------------------------------------------------------------
# Membership and overlap
# ----------------------------------------------------------------------------


def test_membership_and_overlap_counts():
    pooled = _pooled_fixture()
    clustered = cluster_across_configs(pooled, buffer_m=20.0)
    membership = cluster_membership_table(clustered, configs=["A", "B"])
    assert len(membership) == 3
    overlap = overlap_summary(membership, configs=["A", "B"])
    assert overlap["n_clusters"] == 3
    assert overlap["n_pooled_candidates"] == 5
    assert overlap["n_shared_by_all"] == 2
    assert overlap["n_unique_to_one"] == 1
    # 2 clusters in full overlap × 2 configs = 4 of 5 pooled rows
    assert overlap["fraction_pooled_in_full_overlap"] == pytest.approx(4 / 5)
    assert overlap["clusters_by_sharing"] == {1: 1, 2: 2}


# ----------------------------------------------------------------------------
# Pairwise correlations
# ----------------------------------------------------------------------------


def test_pairwise_correlations_perfect_agreement():
    membership = pd.DataFrame(
        {
            "cluster_id": [0, 1, 2, 3],
            "A": [0.1, 0.4, 0.7, 0.9],
            "B": [0.1, 0.4, 0.7, 0.9],
            "n_configs": [2, 2, 2, 2],
        }
    )
    out = pairwise_correlations(membership, configs=["A", "B"])
    stats = out["A__vs__B"]
    assert stats["n"] == 4
    assert stats["pearson_r"] == pytest.approx(1.0)
    assert stats["mean_abs_diff"] == pytest.approx(0.0)


def test_pairwise_correlations_handles_partial_overlap():
    membership = pd.DataFrame(
        {
            "cluster_id": [0, 1, 2],
            "A": [0.2, 0.5, np.nan],
            "B": [0.3, np.nan, 0.8],
            "n_configs": [2, 1, 1],
        }
    )
    out = pairwise_correlations(membership, configs=["A", "B"])
    # Only cluster 0 has both values; n=1 -> NaN correlation
    assert out["A__vs__B"]["n"] == 1
    assert math.isnan(out["A__vs__B"]["pearson_r"])


# ----------------------------------------------------------------------------
# ICC(2,1)
# ----------------------------------------------------------------------------


def test_icc_2_1_perfect_agreement_is_one():
    matrix = np.array([[0.1, 0.1], [0.5, 0.5], [0.9, 0.9]])
    assert icc_2_1_absolute(matrix) == pytest.approx(1.0)


def test_icc_2_1_shrout_fleiss_canonical():
    """Validate against the Shrout & Fleiss (1979) canonical 6x4 example.

    Their published ICC(2,1) absolute-agreement value is 0.290.
    """
    matrix = np.array(
        [
            [9.0, 2.0, 5.0, 8.0],
            [6.0, 1.0, 3.0, 2.0],
            [8.0, 4.0, 6.0, 8.0],
            [7.0, 1.0, 2.0, 6.0],
            [10.0, 5.0, 6.0, 9.0],
            [6.0, 2.0, 4.0, 7.0],
        ]
    )
    icc = icc_2_1_absolute(matrix)
    assert icc == pytest.approx(0.290, abs=2e-3)


def test_icc_2_1_degenerate_returns_nan():
    assert math.isnan(icc_2_1_absolute(np.array([[0.5, 0.5]])))


# ----------------------------------------------------------------------------
# Complete-case stats
# ----------------------------------------------------------------------------


def test_complete_case_stats_uses_only_full_overlap():
    membership = pd.DataFrame(
        {
            "cluster_id": [0, 1, 2],
            "A": [0.1, 0.4, np.nan],
            "B": [0.1, 0.4, 0.6],
            "n_configs": [2, 2, 1],
        }
    )
    stats = complete_case_stats(membership, configs=["A", "B"])
    assert stats["n_complete_clusters"] == 2
    assert stats["icc_2_1"] == pytest.approx(1.0)
    assert stats["per_config_mean"]["A"] == pytest.approx(0.25)


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------


def _optima(*pairs):
    return {f"c{i}": {"vote_t": v, "prob_t": p, "f1": 0.88, "p": 0.9, "r": 0.86}
            for i, (v, p) in enumerate(pairs)}


def test_verdict_h_b_pointwise_equivalence():
    overlap = {"fraction_pooled_in_full_overlap": 0.85}
    complete = {"icc_2_1": 0.95}
    optima = _optima((6, 0.15), (6, 0.15), (6, 0.15))
    out = render_verdict(overlap, complete, optima)
    assert out["verdict"] == "H-B"
    assert out["thresholds_identical"] is True


def test_verdict_h_c_compensation():
    overlap = {"fraction_pooled_in_full_overlap": 0.85}
    complete = {"icc_2_1": 0.75}
    optima = _optima((6, 0.15), (6, 0.20), (5, 0.15))
    out = render_verdict(overlap, complete, optima)
    assert out["verdict"] == "H-C"
    assert out["thresholds_identical"] is False


def test_verdict_h_a_set_divergence():
    overlap = {"fraction_pooled_in_full_overlap": 0.40}
    complete = {"icc_2_1": 0.95}
    optima = _optima((6, 0.15), (6, 0.15), (6, 0.15))
    out = render_verdict(overlap, complete, optima)
    assert out["verdict"] == "H-A"


def test_verdict_inconclusive():
    overlap = {"fraction_pooled_in_full_overlap": 0.85}
    complete = {"icc_2_1": 0.30}
    optima = _optima((6, 0.15), (6, 0.15))
    out = render_verdict(overlap, complete, optima)
    assert out["verdict"] == "INCONCLUSIVE"


def test_verdict_h_b_blocks_when_thresholds_differ():
    """High ICC + high shared fraction but divergent thresholds -> H-C, not H-B."""
    overlap = {"fraction_pooled_in_full_overlap": 0.85}
    complete = {"icc_2_1": 0.95}
    optima = _optima((6, 0.15), (5, 0.15))
    out = render_verdict(overlap, complete, optima)
    assert out["verdict"] == "H-C"
