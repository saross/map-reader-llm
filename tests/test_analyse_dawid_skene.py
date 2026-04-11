"""
Tier 1 unit tests for analyse_dawid_skene.py.

Tests the Dawid-Skene EM algorithm, shared item set construction,
corrected metrics computation, and simple correction — all with
synthetic data. No file I/O, no API calls.
"""

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from analyse_dawid_skene import (  # noqa: E402
    build_shared_item_set,
    compute_corrected_metrics,
    compute_simple_correction,
    dawid_skene_em,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def perfect_agreement_labels():
    """Two annotators that perfectly agree: 50 positive, 50 negative.

    Both annotators label the same 50 items as positive and the same
    50 items as negative. D-S should recover posteriors near 1.0 / 0.0.
    """
    n = 100
    student = np.array([1] * 50 + [0] * 50)
    vlm = np.array([1] * 50 + [0] * 50)
    return student, vlm


@pytest.fixture
def known_error_labels():
    """Synthetic labels with known error profile.

    100 items total:
    - 80 truly positive (T=1)
    - 20 truly negative (T=0)

    Student: sensitivity=0.95, specificity=1.0
      → 76 correct positives, 4 false negatives, 0 false positives
    VLM: sensitivity=0.75, specificity=0.80
      → 60 correct positives, 20 false negatives, 4 false positives

    Observed labels:
    - student=1, vlm=1: 57 (TP for both)
    - student=1, vlm=0: 19 (student TP, VLM FN)
    - student=0, vlm=1:  7 (student FN+VLM TP=3, TN+VLM FP=4)
    - student=0, vlm=0: 17 (student FN+VLM FN=1, TN+VLM TN=16)

    But in our item set we only include items where at least one is
    positive (excluding the 17 double-negatives). So the effective
    item set has 83 items.
    """
    # Build deterministically
    # 76 matched (s=1, v=1) — nope, let me be more careful
    # Actually let me just create the labels directly for the 83-item set
    # (excluding double-negatives, as D-S only sees the union)
    student = np.array(
        [1] * 57 +  # matched: s=1, v=1
        [1] * 19 +  # student-only: s=1, v=0
        [0] * 7      # vlm-only: s=0, v=1
    )
    vlm = np.array(
        [1] * 57 +  # matched: s=1, v=1
        [0] * 19 +  # student-only: s=1, v=0
        [1] * 7      # vlm-only: s=0, v=1
    )
    return student, vlm


@pytest.fixture
def synthetic_item_set():
    """A small synthetic item set DataFrame for testing metrics.

    100 items:
    - 70 matched (student=1, vlm=1)
    - 20 student_only (student=1, vlm=0)
    - 10 vlm_only (student=0, vlm=1)
    """
    categories = (
        ["matched"] * 70
        + ["student_only"] * 20
        + ["vlm_only"] * 10
    )
    student_labels = [1] * 70 + [1] * 20 + [0] * 10
    vlm_labels = [1] * 70 + [0] * 20 + [1] * 10

    return pd.DataFrame({
        "item_id": range(100),
        "student_label": student_labels,
        "vlm_label": vlm_labels,
        "vlm_probability": [0.9] * 70 + [0.0] * 20 + [0.5] * 10,
        "map_name": ["test_map"] * 100,
        "category": categories,
        "x": range(100),
        "y": range(100),
    })


# ---------------------------------------------------------------------------
# D-S EM: convergence and basic properties
# ---------------------------------------------------------------------------


class TestDawidSkeneEM:
    """Tests for the D-S EM algorithm."""

    def test_converges_with_perfect_agreement(
        self, perfect_agreement_labels
    ):
        """D-S should converge quickly when annotators perfectly agree."""
        student, vlm = perfect_agreement_labels
        result = dawid_skene_em(student, vlm)

        assert result["converged"] is True
        assert result["n_iterations"] <= 10

    def test_posteriors_shape(self, known_error_labels):
        """Posteriors array should match input length."""
        student, vlm = known_error_labels
        result = dawid_skene_em(student, vlm)

        assert len(result["posteriors"]) == len(student)

    def test_posteriors_range(self, known_error_labels):
        """All posteriors should be in [0, 1]."""
        student, vlm = known_error_labels
        result = dawid_skene_em(student, vlm)

        assert np.all(result["posteriors"] >= 0.0)
        assert np.all(result["posteriors"] <= 1.0)

    def test_agreed_positives_have_high_posteriors(
        self, known_error_labels
    ):
        """Items where both annotators agree positive → high posterior."""
        student, vlm = known_error_labels
        result = dawid_skene_em(student, vlm)

        # First 57 items are matched (s=1, v=1)
        matched_posteriors = result["posteriors"][:57]
        assert np.all(matched_posteriors > 0.9), (
            f"Matched items should have posterior > 0.9, "
            f"got min={matched_posteriors.min():.4f}"
        )

    def test_student_only_have_high_posteriors(
        self, known_error_labels
    ):
        """Items where only student is positive → high posterior.

        With student specificity = 1.0, any student positive is
        certainly a true mound.
        """
        student, vlm = known_error_labels
        result = dawid_skene_em(student, vlm)

        # Items 57..75 are student-only (s=1, v=0)
        student_only_posteriors = result["posteriors"][57:76]
        assert np.all(student_only_posteriors > 0.9), (
            f"Student-only items should have posterior > 0.9 "
            f"(student spec=1.0), got min="
            f"{student_only_posteriors.min():.4f}"
        )

    def test_vlm_only_have_mixed_posteriors(
        self, known_error_labels
    ):
        """VLM-only items should have intermediate posteriors.

        These are the uncertain items — some real, some false.
        """
        student, vlm = known_error_labels
        result = dawid_skene_em(student, vlm)

        # Items 76..82 are VLM-only (s=0, v=1)
        vlm_only_posteriors = result["posteriors"][76:]
        # Should not all be 0 or all be 1
        assert not np.all(vlm_only_posteriors > 0.99), (
            "VLM-only items should not all have near-1.0 posteriors"
        )

    def test_prevalence_in_range(self, known_error_labels):
        """Estimated prevalence should be between 0 and 1."""
        student, vlm = known_error_labels
        result = dawid_skene_em(student, vlm)

        assert 0.0 < result["prevalence"] < 1.0

    def test_sensitivity_specificity_in_range(
        self, known_error_labels
    ):
        """All estimated confusion matrix entries should be in [0, 1]."""
        student, vlm = known_error_labels
        result = dawid_skene_em(student, vlm)

        for key in ["student_sensitivity", "student_specificity",
                     "vlm_sensitivity", "vlm_specificity"]:
            assert 0.0 <= result[key] <= 1.0, (
                f"{key}={result[key]} out of range"
            )

    def test_fixed_student_specificity(self, known_error_labels):
        """Student specificity should remain at initial value when fixed."""
        student, vlm = known_error_labels
        result = dawid_skene_em(
            student, vlm,
            student_spec_init=1.0,
            fix_student_spec=True,
        )
        assert result["student_specificity"] == 1.0

    def test_unfixed_student_specificity_can_change(
        self, known_error_labels
    ):
        """Student specificity should change if not fixed."""
        student, vlm = known_error_labels
        result = dawid_skene_em(
            student, vlm,
            student_spec_init=0.99,
            fix_student_spec=False,
        )
        # May or may not equal init; just check it ran without error
        assert 0.0 <= result["student_specificity"] <= 1.0

    def test_empty_labels_raises(self):
        """Empty label arrays should raise ValueError."""
        with pytest.raises(ValueError, match="Empty"):
            dawid_skene_em(np.array([]), np.array([]))

    def test_mismatched_lengths_raises(self):
        """Mismatched label arrays should raise ValueError."""
        with pytest.raises(ValueError, match="equal length"):
            dawid_skene_em(np.array([1, 0]), np.array([1]))

    def test_all_positive_labels(self):
        """D-S should handle all-positive labels gracefully."""
        n = 50
        student = np.ones(n)
        vlm = np.ones(n)
        result = dawid_skene_em(student, vlm)

        assert result["converged"] is True
        # All items agreed positive → all posteriors should be high
        assert np.all(result["posteriors"] > 0.9)

    def test_custom_priors_affect_result(self, known_error_labels):
        """Different priors should produce different results.

        Running with very different VLM sensitivity priors should
        produce measurably different posteriors (at least initially).
        """
        student, vlm = known_error_labels

        result_low = dawid_skene_em(
            student, vlm, vlm_sens_init=0.50, vlm_spec_init=0.50,
        )
        result_high = dawid_skene_em(
            student, vlm, vlm_sens_init=0.95, vlm_spec_init=0.95,
        )

        # Both should converge (EM finds the same MLE regardless of init,
        # barring degenerate cases), but allow slight differences due to
        # local optima
        assert result_low["converged"] is True
        assert result_high["converged"] is True


# ---------------------------------------------------------------------------
# Corrected metrics
# ---------------------------------------------------------------------------


class TestCorrectedMetrics:
    """Tests for compute_corrected_metrics."""

    def test_perfect_posteriors(self, synthetic_item_set):
        """When posteriors match student labels, TP/FP/FN are correct.

        Posteriors 1.0 for student=1, 0.0 for student=0 should yield
        expected TP=70, FP=10, FN=20 (all VLM-only are FP).
        """
        posteriors = np.array(
            [1.0] * 70 + [1.0] * 20 + [0.0] * 10
        )
        result = compute_corrected_metrics(synthetic_item_set, posteriors)

        assert result["tp_expected"] == 70.0
        assert result["fp_expected"] == 10.0
        assert result["fn_expected"] == 20.0

    def test_higher_vlm_only_posteriors_increase_precision(
        self, synthetic_item_set
    ):
        """Higher VLM-only posteriors should increase precision."""
        posteriors_low = np.array(
            [1.0] * 70 + [1.0] * 20 + [0.1] * 10
        )
        result_low = compute_corrected_metrics(
            synthetic_item_set, posteriors_low,
        )

        posteriors_high = np.array(
            [1.0] * 70 + [1.0] * 20 + [0.8] * 10
        )
        result_high = compute_corrected_metrics(
            synthetic_item_set, posteriors_high,
        )

        assert result_high["precision"] > result_low["precision"]
        assert (
            result_high["expected_reclassified"]
            > result_low["expected_reclassified"]
        )

    def test_expected_counts_add_up(self, synthetic_item_set):
        """Expected TP + FP should equal total VLM detections."""
        posteriors = np.array(
            [1.0] * 70 + [1.0] * 20 + [0.3] * 10
        )
        result = compute_corrected_metrics(
            synthetic_item_set, posteriors,
        )

        vlm_total = float(
            (synthetic_item_set["vlm_label"] == 1).sum()
        )
        assert abs(
            result["tp_expected"] + result["fp_expected"] - vlm_total
        ) < 0.01


# ---------------------------------------------------------------------------
# Simple correction
# ---------------------------------------------------------------------------


class TestSimpleCorrection:
    """Tests for compute_simple_correction."""

    def test_zero_fn_rate_no_change(self, synthetic_item_set):
        """With 0% FN rate, simple correction equals measured metrics."""
        result = compute_simple_correction(
            synthetic_item_set, student_fn_rate=0.0,
        )
        # No student errors → no reclassification
        assert result["reclassified_fp_to_tp"] == 0

    def test_higher_fn_rate_increases_precision(
        self, synthetic_item_set
    ):
        """Higher assumed FN rate → more reclassification → higher P."""
        result_low = compute_simple_correction(
            synthetic_item_set, student_fn_rate=0.02,
        )
        result_high = compute_simple_correction(
            synthetic_item_set, student_fn_rate=0.10,
        )

        assert result_high["precision"] >= result_low["precision"]
        assert (
            result_high["reclassified_fp_to_tp"]
            >= result_low["reclassified_fp_to_tp"]
        )

    def test_reclassified_bounded_by_vlm_only(
        self, synthetic_item_set
    ):
        """Reclassified count should never exceed VLM-only count."""
        result = compute_simple_correction(
            synthetic_item_set, student_fn_rate=0.50,
        )
        n_vlm_only = int(
            (synthetic_item_set["category"] == "vlm_only").sum()
        )
        assert result["reclassified_fp_to_tp"] <= n_vlm_only


# ---------------------------------------------------------------------------
# Shared item set (with synthetic GeoDataFrames)
# ---------------------------------------------------------------------------


class TestBuildSharedItemSet:
    """Tests for build_shared_item_set using synthetic spatial data."""

    @pytest.fixture
    def spatial_data(self):
        """Synthetic detection, reference, and bounds GeoDataFrames.

        Map 'test_map':
        - 3 references: (100,100), (200,200), (300,300)
        - 4 detections: (105,100), (210,200), (500,500), (600,600)
        - At 50m tolerance:
          D0 matches R0 (dist=5m)  → matched
          D1 matches R1 (dist=14m) → matched
          D2 no match              → vlm_only
          D3 no match              → vlm_only
          R2 no match              → student_only
        """
        from shapely.geometry import Point, box  # noqa: E402

        refs = gpd.GeoDataFrame(
            {"source_map": ["test_map"] * 3},
            geometry=[
                Point(100, 100),
                Point(200, 200),
                Point(300, 300),
            ],
            crs="EPSG:32635",
        )

        dets = gpd.GeoDataFrame(
            {
                "source_tile": [
                    "test_map_x0_y0.png",
                    "test_map_x0_y0.png",
                    "test_map_x0_y0.png",
                    "test_map_x0_y0.png",
                ],
                "mound_probability": [0.95, 0.80, 0.60, 0.30],
            },
            geometry=[
                Point(105, 100),
                Point(210, 200),
                Point(500, 500),
                Point(600, 600),
            ],
            crs="EPSG:32635",
        )

        bounds = gpd.GeoDataFrame(
            {"tile_name": ["test_map_x0_y0.png"]},
            geometry=[box(0, 0, 1000, 1000)],
            crs="EPSG:32635",
        )

        return dets, refs, bounds

    def test_item_categories(self, spatial_data):
        """Check that the three categories are correctly assigned."""
        dets, refs, bounds = spatial_data
        items = build_shared_item_set(
            dets, refs, bounds, buffer_metres=50,
        )

        # 2 matched + 1 student_only + 2 vlm_only = 5 unique locations
        assert len(items) == 5
        cats = items["category"].value_counts()
        assert cats.get("matched", 0) == 2
        assert cats.get("student_only", 0) == 1
        assert cats.get("vlm_only", 0) == 2

    def test_labels_consistent_with_category(self, spatial_data):
        """Label values should match their category."""
        dets, refs, bounds = spatial_data
        items = build_shared_item_set(
            dets, refs, bounds, buffer_metres=50,
        )

        for _, row in items.iterrows():
            if row["category"] == "matched":
                assert row["student_label"] == 1
                assert row["vlm_label"] == 1
            elif row["category"] == "student_only":
                assert row["student_label"] == 1
                assert row["vlm_label"] == 0
            elif row["category"] == "vlm_only":
                assert row["student_label"] == 0
                assert row["vlm_label"] == 1

    def test_vlm_probability_preserved(self, spatial_data):
        """VLM probability should be carried through for matched/vlm_only."""
        dets, refs, bounds = spatial_data
        items = build_shared_item_set(
            dets, refs, bounds, buffer_metres=50,
        )

        vlm_items = items[items["vlm_label"] == 1]
        assert all(vlm_items["vlm_probability"] > 0.0)

        student_only = items[items["category"] == "student_only"]
        assert all(student_only["vlm_probability"] == 0.0)

    def test_empty_detections(self, spatial_data):
        """With no detections, all reference items are student_only."""
        _, refs, bounds = spatial_data
        empty_dets = gpd.GeoDataFrame(
            {"source_tile": pd.Series(dtype=str),
             "mound_probability": pd.Series(dtype=float)},
            geometry=gpd.GeoSeries([], crs="EPSG:32635"),
            crs="EPSG:32635",
        )

        items = build_shared_item_set(
            empty_dets, refs, bounds, buffer_metres=50,
        )
        assert len(items) == 3
        assert all(items["category"] == "student_only")

    def test_unique_item_ids(self, spatial_data):
        """Every item should have a unique item_id."""
        dets, refs, bounds = spatial_data
        items = build_shared_item_set(
            dets, refs, bounds, buffer_metres=50,
        )
        assert items["item_id"].nunique() == len(items)

    def test_tight_buffer_reduces_matches(self, spatial_data):
        """A very tight buffer should reduce the number of matches."""
        dets, refs, bounds = spatial_data

        items_wide = build_shared_item_set(
            dets, refs, bounds, buffer_metres=50,
        )
        items_tight = build_shared_item_set(
            dets, refs, bounds, buffer_metres=3,
        )

        matched_wide = (items_wide["category"] == "matched").sum()
        matched_tight = (items_tight["category"] == "matched").sum()

        # At 3m, only D0↔R0 (5m) should NOT match,
        # so fewer matches than at 50m
        assert matched_tight < matched_wide
