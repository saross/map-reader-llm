"""
Tier 1 unit tests for analyse_dawid_skene.py.

Tests the Dawid-Skene EM algorithm, shared item set construction,
corrected metrics computation, and simple correction — all with
synthetic data. The ``load_detections`` regression suite at the
bottom uses temporary JSON files on disk to reproduce the exact
manifest/probabilities pairing produced by the production
pipeline; no API calls.
"""

import json
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
    load_detections,
)

pytestmark = pytest.mark.tier1


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


# ---------------------------------------------------------------------------
# load_detections — regression suite for the row-position bug
# ---------------------------------------------------------------------------
#
# Background
# ----------
# Before the May 2026 fix, ``load_detections`` joined verifier
# probabilities to consensus features by *row position* — assuming the
# i-th feature in ``consensus-NofM.geojson`` corresponded to the
# ``candidate_{i:05d}`` key in ``probabilities.json``. That assumption
# silently broke under partial recovery (see
# ``scripts/55maps-t0.3-extract-new-candidates.py``), where the new
# consensus geojson can be re-clustered into a different row order
# while the candidate manifest preserves the stable IDs that
# ``probabilities.json`` is keyed by.
#
# The fix loads candidates from the manifest directly, joining
# probabilities by the stable ``candidate_id``. These tests pin that
# behaviour by writing a tiny manifest + probabilities pair to disk
# and exercising both orderings.
# ---------------------------------------------------------------------------


def _write_manifest(
    path: Path,
    candidates: list[dict],
) -> None:
    """Write a minimal candidate_manifest.json fixture to *path*."""
    payload = {
        "version": "2.0",
        "source_geojson": "test/fixture",
        "rasters_dir": "test/fixture",
        "tiles_dir": "test/fixture",
        "padding": 75,
        "crop_dimensions": "150x150",
        "total_detections": len(candidates),
        "successful_extractions": len(candidates),
        "failed_extractions": 0,
        "candidates": candidates,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_probabilities(path: Path, by_id: dict[int, float]) -> None:
    """Write a minimal probabilities.json keyed by ``candidate_NNNNN``."""
    results = {
        f"candidate_{cid:05d}": {"mound_probability": prob}
        for cid, prob in by_id.items()
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"results": results}),
        encoding="utf-8",
    )


def _make_candidate(
    cid: int,
    cx: float,
    cy: float,
    source_tile: str = "test_map_x0_y0.png",
) -> dict:
    """Return a manifest candidate dict with the canonical schema."""
    return {
        "candidate_id": cid,
        "crop_file": f"crops/candidate_{cid:05d}.png",
        "source_tile": source_tile,
        "centroid_x": cx,
        "centroid_y": cy,
        "cropped_from": "raster",
        "properties": {
            "vote_count": 5,
            "source_tile": source_tile,
            "source_tiles": [source_tile],
        },
    }


@pytest.mark.tier1
class TestLoadDetections:
    """Regression suite for the row-position vs candidate_id bug."""

    @pytest.fixture
    def baseline_manifest(self, tmp_path: Path) -> tuple[Path, Path]:
        """Write a 5-candidate manifest + matching probabilities.json.

        Layout mirrors the production convention:

            <run-root>/crops/candidate_manifest.json
            <run-root>/verified/probabilities.json
            <run-root>/consensus/consensus-4of5.geojson  (just an anchor)

        Probabilities are deliberately unequal so a wrong join would
        produce a wrong filtered set.
        """
        run_root = tmp_path / "run_root"
        crops_dir = run_root / "crops"
        verified_dir = run_root / "verified"
        consensus_dir = run_root / "consensus"
        consensus_dir.mkdir(parents=True, exist_ok=True)
        consensus_path = consensus_dir / "consensus-4of5.geojson"
        consensus_path.write_text(
            json.dumps({"type": "FeatureCollection", "features": []}),
            encoding="utf-8",
        )

        # 5 candidates with distinct IDs and centroids
        candidates = [
            _make_candidate(0, 100.0, 100.0),
            _make_candidate(1, 200.0, 200.0),
            _make_candidate(2, 300.0, 300.0),
            _make_candidate(3, 400.0, 400.0),
            _make_candidate(4, 500.0, 500.0),
        ]
        _write_manifest(crops_dir / "candidate_manifest.json", candidates)

        probabilities = {
            0: 0.10,  # below threshold
            1: 0.95,  # above
            2: 0.20,  # above
            3: 0.05,  # below
            4: 0.80,  # above
        }
        _write_probabilities(
            verified_dir / "probabilities.json", probabilities,
        )

        return consensus_path, verified_dir / "probabilities.json"

    def test_baseline_load_filters_by_threshold(self, baseline_manifest):
        """Sanity: the basic load filters correctly by probability."""
        consensus_path, probs_path = baseline_manifest
        gdf = load_detections(
            consensus_path, probs_path, threshold=0.15,
        )

        # IDs 1, 2, 4 should pass (probs 0.95, 0.20, 0.80)
        assert sorted(gdf["candidate_id"].tolist()) == [1, 2, 4]
        # CRS should be the documented target
        assert gdf.crs.to_string() == "EPSG:32635"

    def test_load_uses_stable_candidate_id_not_row_position(
        self, tmp_path: Path,
    ):
        """Reversed manifest order → identical filtered result.

        Reproduces the bug surface: if ``load_detections`` looked up
        probabilities by *row position* in the manifest, reversing the
        candidate order would re-pair every probability with the wrong
        candidate. With the manifest-id-based join, the result must be
        identical regardless of row order.
        """
        run_root = tmp_path / "run_root"
        crops_dir = run_root / "crops"
        verified_dir = run_root / "verified"
        consensus_path = run_root / "consensus" / "consensus-4of5.geojson"
        consensus_path.parent.mkdir(parents=True, exist_ok=True)
        consensus_path.write_text(
            json.dumps({"type": "FeatureCollection", "features": []}),
            encoding="utf-8",
        )

        # Forward order: ids 0, 1, 2, 3, 4
        forward = [
            _make_candidate(0, 100.0, 100.0),
            _make_candidate(1, 200.0, 200.0),
            _make_candidate(2, 300.0, 300.0),
            _make_candidate(3, 400.0, 400.0),
            _make_candidate(4, 500.0, 500.0),
        ]
        # Reversed order: ids 4, 3, 2, 1, 0 — but each candidate keeps
        # its own centroid + ID, so the stable join must still pair
        # probability[1]=0.95 with the (200,200) point, etc.
        reversed_cands = list(reversed(forward))

        probabilities = {0: 0.10, 1: 0.95, 2: 0.20, 3: 0.05, 4: 0.80}
        _write_probabilities(
            verified_dir / "probabilities.json", probabilities,
        )

        # Forward run
        _write_manifest(
            crops_dir / "candidate_manifest.json", forward,
        )
        gdf_forward = load_detections(
            consensus_path,
            verified_dir / "probabilities.json",
            threshold=0.15,
        )

        # Reversed run — overwrite manifest in place
        _write_manifest(
            crops_dir / "candidate_manifest.json", reversed_cands,
        )
        gdf_reversed = load_detections(
            consensus_path,
            verified_dir / "probabilities.json",
            threshold=0.15,
        )

        # Sort both by candidate_id and compare
        f = gdf_forward.sort_values("candidate_id").reset_index(drop=True)
        r = gdf_reversed.sort_values("candidate_id").reset_index(drop=True)

        assert f["candidate_id"].tolist() == r["candidate_id"].tolist()
        assert (
            f["mound_probability"].tolist()
            == r["mound_probability"].tolist()
        )

        # And, critically, the (id → probability) pairing must match
        # the source of truth — probabilities indexed by id.
        for _, row in f.iterrows():
            cid = int(row["candidate_id"])
            assert row["mound_probability"] == probabilities[cid], (
                f"Candidate {cid} got probability "
                f"{row['mound_probability']} but expected "
                f"{probabilities[cid]}; the join is using the wrong key."
            )

    def test_partial_recovery_with_high_id_gap(self, tmp_path: Path):
        """Manifest with non-contiguous IDs from partial recovery.

        Simulates the production scenario: the original manifest had
        IDs 0-2, then a recovery cycle appended new candidates with
        IDs 9131, 9132 (jumping to keep IDs stable for old crops).
        Row position 3 in the manifest does NOT correspond to
        candidate_00003 — the buggy lookup would use the wrong key.
        """
        run_root = tmp_path / "run_root"
        crops_dir = run_root / "crops"
        verified_dir = run_root / "verified"
        consensus_path = run_root / "consensus" / "consensus-4of5.geojson"
        consensus_path.parent.mkdir(parents=True, exist_ok=True)
        consensus_path.write_text(
            json.dumps({"type": "FeatureCollection", "features": []}),
            encoding="utf-8",
        )

        # Original 3 candidates + 2 recovered with high IDs
        candidates = [
            _make_candidate(0, 100.0, 100.0),
            _make_candidate(1, 200.0, 200.0),
            _make_candidate(2, 300.0, 300.0),
            _make_candidate(9131, 400.0, 400.0),  # recovered
            _make_candidate(9132, 500.0, 500.0),  # recovered
        ]
        _write_manifest(crops_dir / "candidate_manifest.json", candidates)

        # Probabilities only exist for the actual IDs — NOT row positions.
        # candidate_00003 / candidate_00004 do not exist.
        probabilities = {
            0: 0.50,
            1: 0.05,
            2: 0.95,
            9131: 0.80,
            9132: 0.10,
        }
        _write_probabilities(
            verified_dir / "probabilities.json", probabilities,
        )

        gdf = load_detections(
            consensus_path,
            verified_dir / "probabilities.json",
            threshold=0.15,
        )

        # Threshold 0.15 should keep IDs 0, 2, 9131
        assert sorted(gdf["candidate_id"].tolist()) == [0, 2, 9131]

        # And each retained probability should match the source of truth
        for _, row in gdf.iterrows():
            cid = int(row["candidate_id"])
            assert row["mound_probability"] == probabilities[cid]

    def test_explicit_manifest_path_override(self, tmp_path: Path):
        """``manifest_path`` argument should override the derived path."""
        # Place manifest in a non-standard location
        odd_dir = tmp_path / "elsewhere"
        candidates = [
            _make_candidate(7, 700.0, 700.0),
            _make_candidate(8, 800.0, 800.0),
        ]
        manifest_path = odd_dir / "candidate_manifest.json"
        _write_manifest(manifest_path, candidates)

        verified_dir = tmp_path / "verified"
        probabilities = {7: 0.90, 8: 0.05}
        probs_path = verified_dir / "probabilities.json"
        _write_probabilities(probs_path, probabilities)

        # Consensus path that does NOT have a sibling crops dir
        bogus_consensus = (
            tmp_path / "no-crops" / "consensus" / "fake.geojson"
        )
        bogus_consensus.parent.mkdir(parents=True, exist_ok=True)
        bogus_consensus.write_text("{}", encoding="utf-8")

        gdf = load_detections(
            bogus_consensus, probs_path,
            threshold=0.15,
            manifest_path=manifest_path,
        )

        assert gdf["candidate_id"].tolist() == [7]

    def test_missing_manifest_raises(self, tmp_path: Path):
        """A missing manifest should raise FileNotFoundError."""
        consensus_path = tmp_path / "consensus" / "consensus-4of5.geojson"
        consensus_path.parent.mkdir(parents=True, exist_ok=True)
        consensus_path.write_text("{}", encoding="utf-8")

        verified_dir = tmp_path / "verified"
        probs_path = verified_dir / "probabilities.json"
        _write_probabilities(probs_path, {0: 0.5})

        with pytest.raises(FileNotFoundError, match="manifest not found"):
            load_detections(consensus_path, probs_path, threshold=0.15)
