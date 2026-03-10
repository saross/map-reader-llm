"""
Tier 1 unit tests for analyse_h2_pilot_extensions.py.

Tests core logic functions with synthetic data — no file dependencies,
no API calls. Verifies spatial matching, P-R sweep properties, AUC-PR
computation, ensemble scoring, and set operations for cross-modal overlap.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from analyse_h2_pilot_extensions import (  # noqa: E402
    compute_auc_pr,
    compute_agreement_statistics,
    compute_ensemble_scores,
    compute_pr_sweep,
    evaluate_detections_detailed,
    filter_candidates_by_threshold,
    find_optimal_f1,
)


# ---------------------------------------------------------------------------
# Fixtures: synthetic geometries for spatial matching
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_geometry():
    """
    Simple geometry: 3 detections, 3 references.

    Detections:
      D0 = (100, 100) → matches R0 at (105, 100), dist=5m
      D1 = (200, 200) → matches R1 at (210, 200), dist=10m
      D2 = (500, 500) → no match (nearest ref is >20m away)

    References:
      R0 = (105, 100) → matched by D0
      R1 = (210, 200) → matched by D1
      R2 = (300, 300) → unmatched (FN)

    Expected: TP=2, FP=1, FN=1
    """
    det_coords = [(100, 100), (200, 200), (500, 500)]
    ref_coords = [(105, 100), (210, 200), (300, 300)]
    return det_coords, ref_coords


@pytest.fixture
def overlapping_geometry():
    """
    Two detections competing for the same reference.

    D0 = (100, 100) → dist to R0 = 5m
    D1 = (110, 100) → dist to R0 = 5m (from other side)

    Only one reference: R0 = (105, 100)

    Greedy should match D0 first (same distance, but D0 has lower
    index so appears first in sort). D1 becomes FP.

    Expected: TP=1, FP=1, FN=0
    """
    det_coords = [(100, 100), (110, 100)]
    ref_coords = [(105, 100)]
    return det_coords, ref_coords


# ---------------------------------------------------------------------------
# Test: evaluate_detections_detailed
# ---------------------------------------------------------------------------

class TestEvaluateDetectionsDetailed:
    """Tests for the detailed greedy nearest-neighbour matcher."""

    def test_returns_correct_counts(self, simple_geometry):
        """Verify TP, FP, FN counts on known geometry."""
        det, ref = simple_geometry
        result = evaluate_detections_detailed(det, ref, buffer_m=20.0)
        assert result["tp"] == 2
        assert result["fp"] == 1
        assert result["fn"] == 1

    def test_returns_matched_pairs(self, simple_geometry):
        """Verify matched_pairs contains correct det→ref assignments."""
        det, ref = simple_geometry
        result = evaluate_detections_detailed(det, ref, buffer_m=20.0)
        pairs = result["matched_pairs"]
        assert len(pairs) == 2
        # D0 should match R0, D1 should match R1
        pair_set = set(pairs)
        assert (0, 0) in pair_set  # D0 → R0
        assert (1, 1) in pair_set  # D1 → R1

    def test_matched_ref_indices(self, simple_geometry):
        """Verify matched_ref_indices is correct set."""
        det, ref = simple_geometry
        result = evaluate_detections_detailed(det, ref, buffer_m=20.0)
        assert result["matched_ref_indices"] == {0, 1}

    def test_matched_det_indices(self, simple_geometry):
        """Verify matched_det_indices is correct set."""
        det, ref = simple_geometry
        result = evaluate_detections_detailed(det, ref, buffer_m=20.0)
        assert result["matched_det_indices"] == {0, 1}

    def test_precision_recall_f1(self, simple_geometry):
        """Verify precision, recall, F1 computation."""
        det, ref = simple_geometry
        result = evaluate_detections_detailed(det, ref, buffer_m=20.0)
        # P = 2/3, R = 2/3, F1 = 2/3
        assert abs(result["precision"] - 2 / 3) < 1e-9
        assert abs(result["recall"] - 2 / 3) < 1e-9
        assert abs(result["f1"] - 2 / 3) < 1e-9

    def test_competing_detections(self, overlapping_geometry):
        """Verify greedy matching with two detections near one ref."""
        det, ref = overlapping_geometry
        result = evaluate_detections_detailed(det, ref, buffer_m=20.0)
        assert result["tp"] == 1
        assert result["fp"] == 1
        assert result["fn"] == 0

    def test_empty_detections(self):
        """No detections → all FN."""
        result = evaluate_detections_detailed(
            [], [(100, 100), (200, 200)], buffer_m=20.0
        )
        assert result["tp"] == 0
        assert result["fp"] == 0
        assert result["fn"] == 2
        assert result["matched_pairs"] == []

    def test_empty_references(self):
        """No references → all FP."""
        result = evaluate_detections_detailed(
            [(100, 100), (200, 200)], [], buffer_m=20.0
        )
        assert result["tp"] == 0
        assert result["fp"] == 2
        assert result["fn"] == 0
        assert result["matched_pairs"] == []

    def test_both_empty(self):
        """Empty inputs → all zeros."""
        result = evaluate_detections_detailed([], [], buffer_m=20.0)
        assert result["tp"] == 0
        assert result["fp"] == 0
        assert result["fn"] == 0


# ---------------------------------------------------------------------------
# Test: P-R sweep properties
# ---------------------------------------------------------------------------

class TestPRSweep:
    """Tests for precision-recall threshold sweep."""

    def test_recall_monotonicity(self):
        """Recall must be non-increasing as threshold rises."""
        coords = [(i * 100, 0) for i in range(10)]
        ref_coords = [(i * 100 + 5, 0) for i in range(5)]
        # Assign probabilities: first 5 candidates high, rest low
        probs = {str(i): 0.9 if i < 5 else 0.1 for i in range(10)}
        thresholds = [0.0, 0.2, 0.5, 0.8, 1.0]

        sweep = compute_pr_sweep(coords, ref_coords, probs, thresholds)
        recalls = [row["recall"] for row in sweep]

        for i in range(1, len(recalls)):
            assert recalls[i] <= recalls[i - 1] + 1e-9, (
                f"Recall increased from {recalls[i-1]} to {recalls[i]} "
                f"at threshold {thresholds[i]}"
            )

    def test_n_kept_monotonicity(self):
        """n_kept must be non-increasing as threshold rises."""
        coords = [(i * 100, 0) for i in range(10)]
        ref_coords = [(0, 0)]
        probs = {str(i): i / 10 for i in range(10)}
        thresholds = [0.0, 0.3, 0.5, 0.7, 1.0]

        sweep = compute_pr_sweep(coords, ref_coords, probs, thresholds)
        n_kept = [row["n_kept"] for row in sweep]

        for i in range(1, len(n_kept)):
            assert n_kept[i] <= n_kept[i - 1], (
                f"n_kept increased from {n_kept[i-1]} to {n_kept[i]}"
            )

    def test_threshold_zero_keeps_all(self):
        """Threshold=0.0 should keep all candidates."""
        coords = [(100, 100), (200, 200)]
        ref_coords = [(105, 100)]
        probs = {"0": 0.0, "1": 0.5}

        sweep = compute_pr_sweep(coords, ref_coords, probs, [0.0])
        assert sweep[0]["n_kept"] == 2


# ---------------------------------------------------------------------------
# Test: AUC-PR computation
# ---------------------------------------------------------------------------

class TestAUCPR:
    """Tests for area under precision-recall curve."""

    def test_perfect_curve(self):
        """Perfect classifier: precision=1.0 at all recall levels."""
        # Simulate: as threshold drops, recall goes 0→1.0
        # with precision staying at 1.0 (no FPs)
        sweep = [
            {"n_kept": 1, "precision": 1.0, "recall": 0.2},
            {"n_kept": 2, "precision": 1.0, "recall": 0.4},
            {"n_kept": 3, "precision": 1.0, "recall": 0.6},
            {"n_kept": 4, "precision": 1.0, "recall": 0.8},
            {"n_kept": 5, "precision": 1.0, "recall": 1.0},
        ]
        auc = compute_auc_pr(sweep)
        # AUC = integral of 1.0 from recall=0.2 to 1.0 = 0.8
        assert abs(auc - 0.8) < 0.01

    def test_empty_sweep(self):
        """Empty sweep → AUC = 0."""
        assert compute_auc_pr([]) == 0.0

    def test_single_point(self):
        """Single point → AUC = 0 (can't integrate)."""
        sweep = [{"n_kept": 5, "precision": 0.8, "recall": 0.5}]
        assert compute_auc_pr(sweep) == 0.0

    def test_n_kept_zero_excluded(self):
        """Points with n_kept=0 should be excluded."""
        sweep = [
            {"n_kept": 0, "precision": 0.0, "recall": 0.0},
            {"n_kept": 5, "precision": 0.8, "recall": 0.5},
            {"n_kept": 3, "precision": 0.9, "recall": 0.3},
        ]
        auc = compute_auc_pr(sweep)
        # Two valid points: (0.3, 0.9) and (0.5, 0.8)
        # Trapezoidal: 0.2 * (0.9 + 0.8) / 2 = 0.17
        assert abs(auc - 0.17) < 0.01


# ---------------------------------------------------------------------------
# Test: Ensemble scoring
# ---------------------------------------------------------------------------

class TestEnsembleScores:
    """Tests for multi-verifier ensemble computations."""

    def test_average_computation(self):
        """Verify averaging of 3 probability dicts."""
        probs = {
            "standard": {"0": 0.9, "1": 0.0, "2": 0.6},
            "adversarial": {"0": 0.8, "1": 0.3, "2": 0.4},
            "checklist": {"0": 1.0, "1": 0.0, "2": 0.5},
        }
        scores = compute_ensemble_scores(probs, n_candidates=3)
        avg = scores["average"]
        assert abs(avg["0"] - 0.9) < 1e-9  # (0.9+0.8+1.0)/3
        assert abs(avg["1"] - 0.1) < 1e-9  # (0.0+0.3+0.0)/3
        assert abs(avg["2"] - 0.5) < 1e-9  # (0.6+0.4+0.5)/3

    def test_missing_candidate_defaults_to_zero(self):
        """Missing candidate IDs should be treated as 0.0."""
        probs = {
            "standard": {"0": 0.9},
            "adversarial": {"0": 0.8},
            "checklist": {},  # Candidate 0 missing
        }
        scores = compute_ensemble_scores(probs, n_candidates=1)
        # (0.9 + 0.8 + 0.0) / 3 = 0.567
        assert abs(scores["average"]["0"] - 0.567) < 0.01


class TestMajorityVote:
    """Tests for 2-of-3 majority vote logic via agreement statistics."""

    def test_full_agreement(self):
        """All verifiers agree → 100% 3-way agreement."""
        probs = {
            "standard": {"0": 0.9, "1": 0.1},
            "adversarial": {"0": 0.8, "1": 0.2},
            "checklist": {"0": 0.95, "1": 0.05},
        }
        stats = compute_agreement_statistics(probs, n_candidates=2)
        assert stats["three_way_agreement"] == 1.0

    def test_one_disagrees(self):
        """One verifier disagrees on one candidate."""
        probs = {
            "standard": {"0": 0.9, "1": 0.1},
            "adversarial": {"0": 0.3, "1": 0.1},  # Disagrees on cand 0
            "checklist": {"0": 0.95, "1": 0.05},
        }
        stats = compute_agreement_statistics(
            probs, n_candidates=2, decision_threshold=0.5
        )
        # Candidate 0: std=accept, adv=reject, chk=accept → not 3-way
        # Candidate 1: all reject → 3-way agree
        assert stats["three_way_agreement"] == 0.5
        assert stats["three_way_count"] == 1

    def test_ensemble_differs_from_adversarial(self):
        """Count candidates where majority differs from adversarial."""
        probs = {
            "standard": {"0": 0.9},
            "adversarial": {"0": 0.3},  # Adversarial rejects
            "checklist": {"0": 0.95},
        }
        stats = compute_agreement_statistics(
            probs, n_candidates=1, decision_threshold=0.5
        )
        # Majority: 2/3 accept → accept. Adversarial: reject.
        # → differs
        assert stats["ensemble_differs_from_adversarial"] == 1


# ---------------------------------------------------------------------------
# Test: Cross-modal overlap set operations
# ---------------------------------------------------------------------------

class TestOverlapSetOperations:
    """Tests for Venn diagram arithmetic."""

    def test_overlap_sums_to_total(self):
        """
        |both| + |A_only| + |B_only| + |neither| must equal total refs.
        """
        # Simulate two tracks matching against 10 references
        refs_a = {0, 1, 2, 3, 4}
        refs_b = {3, 4, 5, 6, 7}
        total = 10
        all_refs = set(range(total))

        both = refs_a & refs_b
        a_only = refs_a - refs_b
        b_only = refs_b - refs_a
        neither = all_refs - (refs_a | refs_b)

        assert len(both) + len(a_only) + len(b_only) + len(neither) == total

    def test_jaccard_index(self):
        """Verify Jaccard = |intersection| / |union|."""
        refs_a = {0, 1, 2, 3}
        refs_b = {2, 3, 4, 5}
        union = refs_a | refs_b
        intersection = refs_a & refs_b
        jaccard = len(intersection) / len(union)
        assert abs(jaccard - 2 / 6) < 1e-9

    def test_union_recall(self):
        """Verify union recall = |union| / |total|."""
        refs_a = {0, 1, 2}
        refs_b = {2, 3, 4}
        total = 10
        union = refs_a | refs_b
        recall = len(union) / total
        assert abs(recall - 0.5) < 1e-9

    def test_disjoint_sets(self):
        """Completely disjoint sets → Jaccard = 0, no overlap."""
        refs_a = {0, 1, 2}
        refs_b = {3, 4, 5}
        assert len(refs_a & refs_b) == 0
        jaccard = (
            len(refs_a & refs_b) / len(refs_a | refs_b)
            if refs_a | refs_b else 0
        )
        assert jaccard == 0.0

    def test_identical_sets(self):
        """Identical sets → Jaccard = 1, all in 'both'."""
        refs_a = {0, 1, 2, 3}
        refs_b = {0, 1, 2, 3}
        assert len(refs_a & refs_b) == 4
        jaccard = len(refs_a & refs_b) / len(refs_a | refs_b)
        assert jaccard == 1.0


# ---------------------------------------------------------------------------
# Test: filter_candidates_by_threshold
# ---------------------------------------------------------------------------

class TestFilterCandidates:
    """Tests for threshold-based candidate filtering."""

    def test_threshold_zero_keeps_all(self):
        """Threshold=0.0 keeps all candidates (probs are >= 0)."""
        coords = [(100, 100), (200, 200), (300, 300)]
        probs = {"0": 0.0, "1": 0.5, "2": 1.0}
        filtered = filter_candidates_by_threshold(coords, probs, 0.0)
        assert len(filtered) == 3

    def test_threshold_one_keeps_exact_ones(self):
        """Threshold=1.0 keeps only candidates with prob exactly 1.0."""
        coords = [(100, 100), (200, 200), (300, 300)]
        probs = {"0": 0.99, "1": 0.5, "2": 1.0}
        filtered = filter_candidates_by_threshold(coords, probs, 1.0)
        assert len(filtered) == 1
        assert filtered[0] == (300, 300)

    def test_intermediate_threshold(self):
        """Threshold=0.5 keeps candidates with prob >= 0.5."""
        coords = [(100, 100), (200, 200), (300, 300)]
        probs = {"0": 0.3, "1": 0.5, "2": 0.8}
        filtered = filter_candidates_by_threshold(coords, probs, 0.5)
        assert len(filtered) == 2


# ---------------------------------------------------------------------------
# Test: find_optimal_f1
# ---------------------------------------------------------------------------

class TestFindOptimalF1:
    """Tests for optimal F1 point identification."""

    def test_finds_maximum(self):
        """Returns the row with highest F1."""
        sweep = [
            {"threshold": 0.1, "f1": 0.5},
            {"threshold": 0.3, "f1": 0.8},
            {"threshold": 0.5, "f1": 0.7},
        ]
        best = find_optimal_f1(sweep)
        assert best["threshold"] == 0.3
        assert best["f1"] == 0.8
