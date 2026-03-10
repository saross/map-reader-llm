"""
Tests for Experiment E — High-Recall Text Proposer
====================================================

Tier 1 unit tests for the pure-logic functions in run_experiment_e.py.
Uses synthetic data with known outcomes. No API, file, or network
dependencies.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import sys
from pathlib import Path

import pytest

# Mark all tests in this module as tier1 (fast, no external dependencies)
pytestmark = pytest.mark.tier1

# ---------------------------------------------------------------------------
# Path setup — add scripts/ to sys.path for direct import
# ---------------------------------------------------------------------------

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "scripts")
)

from run_experiment_e import (  # noqa: E402
    find_optimal_threshold,
    format_comparison_table,
    threshold_sweep,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_candidate(cid: int, x: float, y: float) -> dict:
    """Build a minimal candidate dict for testing."""
    return {
        "candidate_id": cid,
        "centroid_x": x,
        "centroid_y": y,
    }


# Ground truth reference points for synthetic tests.
# Three mounds at known positions.
SYNTH_REFS = [
    (100.0, 200.0),
    (300.0, 400.0),
    (500.0, 600.0),
]

# Candidates: 5 candidates, 3 are true positives (within 20 m of a ref),
# 2 are false positives (far from any ref).
SYNTH_CANDIDATES = [
    make_candidate(0, 100.5, 200.5),   # TP — near ref (100, 200)
    make_candidate(1, 300.5, 400.5),   # TP — near ref (300, 400)
    make_candidate(2, 500.5, 600.5),   # TP — near ref (500, 600)
    make_candidate(3, 900.0, 900.0),   # FP — far from any ref
    make_candidate(4, 800.0, 800.0),   # FP — far from any ref
]

# Probabilities: TPs have high probability, FPs have lower
SYNTH_PROBS = {
    0: 0.95,   # TP
    1: 0.80,   # TP
    2: 0.60,   # TP
    3: 0.40,   # FP
    4: 0.20,   # FP
}

BUFFER_M = 20.0


# ===========================================================================
# TestThresholdSweep
# ===========================================================================

class TestThresholdSweep:
    """Tests for threshold_sweep()."""

    def test_all_pass_at_zero_threshold(self):
        """Threshold 0.0 keeps all candidates."""
        results = threshold_sweep(
            SYNTH_CANDIDATES, SYNTH_PROBS, SYNTH_REFS,
            BUFFER_M, [0.0],
        )
        assert len(results) == 1
        assert results[0]["n_kept"] == 5
        assert results[0]["tp"] == 3
        assert results[0]["fp"] == 2
        assert results[0]["fn"] == 0

    def test_none_pass_at_high_threshold(self):
        """Threshold above max probability keeps none."""
        results = threshold_sweep(
            SYNTH_CANDIDATES, SYNTH_PROBS, SYNTH_REFS,
            BUFFER_M, [0.99],
        )
        assert len(results) == 1
        assert results[0]["n_kept"] == 0
        assert results[0]["tp"] == 0
        assert results[0]["fn"] == 3  # All refs are missed

    def test_monotonic_n_kept(self):
        """N_kept is non-increasing as threshold rises."""
        thresholds = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        results = threshold_sweep(
            SYNTH_CANDIDATES, SYNTH_PROBS, SYNTH_REFS,
            BUFFER_M, thresholds,
        )
        n_values = [r["n_kept"] for r in results]
        for i in range(len(n_values) - 1):
            assert n_values[i] >= n_values[i + 1], (
                f"n_kept increased from {n_values[i]} to "
                f"{n_values[i+1]} at threshold {thresholds[i+1]}"
            )

    def test_correct_metrics_known_data(self):
        """Verify metrics at a threshold that filters out both FPs."""
        # At threshold 0.5: keep candidates 0 (0.95), 1 (0.80), 2 (0.60)
        # Exclude: 3 (0.40), 4 (0.20)
        results = threshold_sweep(
            SYNTH_CANDIDATES, SYNTH_PROBS, SYNTH_REFS,
            BUFFER_M, [0.5],
        )
        r = results[0]
        assert r["n_kept"] == 3
        assert r["tp"] == 3
        assert r["fp"] == 0
        assert r["fn"] == 0
        assert r["precision"] == 1.0
        assert r["recall"] == 1.0
        assert r["f1"] == 1.0

    def test_empty_candidates(self):
        """Empty candidates list returns zeros."""
        results = threshold_sweep(
            [], {}, SYNTH_REFS, BUFFER_M, [0.0, 0.5],
        )
        assert len(results) == 2
        for r in results:
            assert r["n_kept"] == 0
            assert r["tp"] == 0
            assert r["fn"] == 3

    def test_none_probabilities_excluded(self):
        """Candidates with None probabilities are excluded at all thresholds."""
        probs_with_none = {
            0: 0.95,
            1: None,   # Will be excluded
            2: 0.60,
            3: 0.40,
            4: None,   # Will be excluded
        }
        results = threshold_sweep(
            SYNTH_CANDIDATES, probs_with_none, SYNTH_REFS,
            BUFFER_M, [0.0],
        )
        # Only 3 candidates have non-None probabilities >= 0.0
        assert results[0]["n_kept"] == 3


# ===========================================================================
# TestFindOptimalThreshold
# ===========================================================================

class TestFindOptimalThreshold:
    """Tests for find_optimal_threshold()."""

    def test_selects_highest_f1(self):
        """Returns the threshold with highest F1."""
        sweep = [
            {"threshold": 0.1, "f1": 0.60, "tp": 3, "fp": 5, "fn": 1,
             "precision": 0.375, "recall": 0.75, "n_kept": 8},
            {"threshold": 0.3, "f1": 0.85, "tp": 3, "fp": 1, "fn": 1,
             "precision": 0.75, "recall": 0.75, "n_kept": 4},
            {"threshold": 0.5, "f1": 0.70, "tp": 2, "fp": 0, "fn": 2,
             "precision": 1.0, "recall": 0.50, "n_kept": 2},
        ]
        best = find_optimal_threshold(sweep)
        assert best["threshold"] == 0.3
        assert best["f1"] == 0.85

    def test_tiebreak_lower_threshold(self):
        """When F1 is tied, selects the lower threshold."""
        sweep = [
            {"threshold": 0.2, "f1": 0.80, "tp": 3, "fp": 1, "fn": 1,
             "precision": 0.75, "recall": 0.75, "n_kept": 4},
            {"threshold": 0.4, "f1": 0.80, "tp": 2, "fp": 0, "fn": 2,
             "precision": 1.0, "recall": 0.50, "n_kept": 2},
        ]
        best = find_optimal_threshold(sweep)
        assert best["threshold"] == 0.2

    def test_empty_results(self):
        """Empty input returns None."""
        assert find_optimal_threshold([]) is None


# ===========================================================================
# TestFormatComparisonTable
# ===========================================================================

class TestFormatComparisonTable:
    """Tests for format_comparison_table()."""

    @pytest.fixture
    def sample_optimal(self) -> dict:
        """Sample optimal threshold result."""
        return {
            "threshold": 0.15,
            "n_kept": 100,
            "precision": 0.820,
            "recall": 0.850,
            "f1": 0.835,
            "tp": 82,
            "fp": 18,
            "fn": 15,
        }

    @pytest.fixture
    def sample_baselines(self) -> dict:
        """Sample baselines dict."""
        return {
            "Text-only baseline": {
                "f1": 0.796, "precision": 0.809, "recall": 0.784,
                "n": 94, "threshold": 0.16,
            },
            "Cross-modal union": {
                "f1": 0.768, "precision": 0.711, "recall": 0.835,
                "n": 114, "threshold": 0.11,
            },
        }

    def test_contains_baseline_rows(
        self, sample_optimal, sample_baselines,
    ):
        """Both baselines appear in the table."""
        table = format_comparison_table(sample_optimal, sample_baselines)
        assert "Text-only baseline" in table
        assert "Cross-modal union" in table

    def test_contains_experiment_row(
        self, sample_optimal, sample_baselines,
    ):
        """Experiment E row appears in the table."""
        table = format_comparison_table(sample_optimal, sample_baselines)
        assert "Experiment E" in table
        assert "0.835" in table  # F1 value

    def test_delta_row_present(
        self, sample_optimal, sample_baselines,
    ):
        """Delta row vs text-only baseline is shown."""
        table = format_comparison_table(sample_optimal, sample_baselines)
        assert "Delta vs text-only" in table
        # Delta F1 = 0.835 - 0.796 = +0.039
        assert "+0.039" in table
