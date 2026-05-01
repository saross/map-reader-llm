"""Tier-1 smoke tests for ``scripts/review_student_fp_candidates``.

Verifies:

- The module imports cleanly with no Streamlit / runtime side effects.
- ``build_fp_candidates`` agrees with the source analysis in
  ``scripts/analyse_student_gt_fn_rate_gs4.py`` on the real 17-feature
  GS-4 corpus (this is a one-off corpus, so a real-data smoke test is
  cheaper and more diagnostic than an artificial fixture).
- The FP-candidate CSV round-trips: write → read → identical content.
- The decisions CSV round-trips with a constructed in-memory dict.

Does not exercise the Streamlit UI (rendering depends on rasters and
Streamlit's session_state, neither of which is reproducible inside
pytest).

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from scripts.review_student_fp_candidates import (
    DECISION_GENUINE_FP,
    DECISION_HUNGARIAN_ARTEFACT,
    FPCandidate,
    MATCH_RADIUS_M,
    build_fp_candidates,
    format_decision,
    load_decisions,
    load_fp_candidates_csv,
    load_inputs,
    save_decisions,
    write_fp_candidates_csv,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Expected aggregate counts at the 50 m headline radius — these come
# from ``scripts/analyse_student_gt_fn_rate_gs4.py`` and must stay in
# lock-step with that script's output. If the underlying GeoJSONs are
# regenerated, both this test and the source analysis should be re-run.
EXPECTED_FP_TOTAL = 17
EXPECTED_FP_BY_MAP = {
    "K-35-052-4_32635": 4,
    "K-35-053-3_Elenovo": 2,
    "K-35-062-2_Rakovski": 9,
    "K-35-078-1_Lesovo": 2,
}


# =========================================================================
# Module-level smoke
# =========================================================================


@pytest.mark.tier1
def test_module_imports_cleanly() -> None:
    """Importing the script must not start Streamlit or read rasters."""
    import scripts.review_student_fp_candidates as mod

    # Sanity: a few key symbols are present.
    assert callable(mod.build_fp_candidates)
    assert callable(mod.load_inputs)
    assert MATCH_RADIUS_M == 50.0


# =========================================================================
# build_fp_candidates against the real 4-GS corpus
# =========================================================================


@pytest.mark.tier1
def test_build_fp_candidates_recovers_17() -> None:
    """The Hungarian re-run reproduces the 17 FPs from the source analysis.

    The brief specifies that the FP-review UI must show the *exact*
    same 17 unmatched student features that the FN/FP analysis script
    reported — otherwise the review and the analysis would disagree.
    """
    student, curator, bounds = load_inputs()
    candidates = build_fp_candidates(student, curator, bounds)

    assert len(candidates) == EXPECTED_FP_TOTAL

    by_map: dict[str, int] = {}
    for c in candidates:
        by_map[c.source_map] = by_map.get(c.source_map, 0) + 1
    assert by_map == EXPECTED_FP_BY_MAP


@pytest.mark.tier1
def test_fp_candidates_have_stable_indices_and_sort() -> None:
    """fp_index is 1..N and the list is sorted by (map, distance)."""
    student, curator, bounds = load_inputs()
    candidates = build_fp_candidates(student, curator, bounds)

    indices = [c.fp_index for c in candidates]
    assert indices == list(range(1, len(candidates) + 1))

    # Sort key: (source_map ascending, nearest_curator_distance_m ascending).
    sort_keys = [(c.source_map, c.nearest_curator_distance_m) for c in candidates]
    assert sort_keys == sorted(sort_keys)


# =========================================================================
# FP-candidate CSV round-trip
# =========================================================================


@pytest.mark.tier1
def test_fp_candidate_csv_round_trip(tmp_path: Path) -> None:
    """write → read → identical FPCandidate objects."""
    student, curator, bounds = load_inputs()
    candidates = build_fp_candidates(student, curator, bounds)
    csv_path = tmp_path / "fp-candidates.csv"
    write_fp_candidates_csv(candidates, csv_path)

    assert csv_path.is_file()
    loaded = load_fp_candidates_csv(csv_path)

    assert len(loaded) == len(candidates)
    for original, restored in zip(candidates, loaded, strict=True):
        assert restored.fp_index == original.fp_index
        assert restored.student_row_id == original.student_row_id
        assert restored.source_map == original.source_map
        assert restored.map_symbol == original.map_symbol
        # Float comparisons within CSV-format precision (4 dp on coords,
        # 2 dp on distances).
        assert abs(restored.student_x_m - original.student_x_m) < 0.01
        assert abs(
            restored.nearest_curator_distance_m
            - original.nearest_curator_distance_m
        ) < 0.01


# =========================================================================
# Decisions CSV round-trip
# =========================================================================


@pytest.mark.tier1
def test_decisions_csv_round_trip(tmp_path: Path) -> None:
    """save_decisions → load_decisions returns identical dict shape."""
    student, curator, bounds = load_inputs()
    candidates = build_fp_candidates(student, curator, bounds)
    assert len(candidates) >= 2  # need at least two for the test

    decisions = {
        candidates[0].fp_index: format_decision(
            candidates[0], DECISION_GENUINE_FP, notes="non-mound symbol",
        ),
        candidates[1].fp_index: format_decision(
            candidates[1], DECISION_HUNGARIAN_ARTEFACT, notes="adjacent mound",
        ),
    }
    csv_path = tmp_path / "fp-decisions.csv"
    save_decisions(decisions, csv_path)

    assert csv_path.is_file()
    loaded = load_decisions(csv_path)

    assert set(loaded.keys()) == set(decisions.keys())
    for fp_idx, row in decisions.items():
        assert loaded[fp_idx]["decision"] == row["decision"]
        assert loaded[fp_idx]["notes"] == row["notes"]
        assert loaded[fp_idx]["source_map"] == row["source_map"]


@pytest.mark.tier1
def test_load_decisions_returns_empty_for_absent_file(tmp_path: Path) -> None:
    """Starting a fresh review must not crash on a missing CSV."""
    csv_path = tmp_path / "does-not-exist.csv"
    assert load_decisions(csv_path) == {}


# =========================================================================
# Hungarian-artefact diagnostic
# =========================================================================


@pytest.mark.tier1
def test_is_hungarian_artefact_candidate_threshold() -> None:
    """The flag fires iff nearest curator < MATCH_RADIUS_M (50 m)."""
    base = dict(
        fp_index=1, student_row_id=0, student_uuid="u",
        map_symbol="Hairy brown circle", feature_type="Mound",
        source_map="K-35-052-4_32635",
        student_x_m=400000.0, student_y_m=4700000.0,
        student_lat=42.0, student_lon=25.0,
        nearest_curator_fid=1,
        nearest_within_200_fid=-1, nearest_within_200_distance_m=float("nan"),
        second_within_200_fid=-1, second_within_200_distance_m=float("nan"),
    )
    just_inside = FPCandidate(**{**base, "nearest_curator_distance_m": 49.9})
    just_outside = FPCandidate(**{**base, "nearest_curator_distance_m": 50.0})
    assert just_inside.is_hungarian_artefact_candidate is True
    # Boundary is strict (<, not ≤): a curator at exactly 50 m would still
    # have been matchable by Hungarian, so should not be flagged here.
    assert just_outside.is_hungarian_artefact_candidate is False


# =========================================================================
# format_decision schema
# =========================================================================


@pytest.mark.tier1
def test_format_decision_includes_all_columns() -> None:
    """The CSV row dict must carry every documented column."""
    student, curator, bounds = load_inputs()
    candidates = build_fp_candidates(student, curator, bounds)
    row = format_decision(candidates[0], DECISION_GENUINE_FP, notes="x")
    expected = {
        "fp_index", "student_row_id", "source_map",
        "decision", "notes", "timestamp",
    }
    assert set(row.keys()) == expected
    # Timestamp must parse as ISO 8601 UTC.
    parsed = datetime.fromisoformat(row["timestamp"])
    # Tolerate either naive or aware result depending on Python version.
    assert parsed.tzinfo is None or parsed.tzinfo == timezone.utc


# =========================================================================
# CSV header sanity (defends against silent column renames)
# =========================================================================


@pytest.mark.tier1
def test_fp_candidate_csv_header(tmp_path: Path) -> None:
    """The candidate CSV header is the documented schema, in order."""
    student, curator, bounds = load_inputs()
    candidates = build_fp_candidates(student, curator, bounds)
    csv_path = tmp_path / "fp-candidates.csv"
    write_fp_candidates_csv(candidates, csv_path)

    expected_header = [
        "fp_index", "student_row_id", "student_uuid",
        "MapSymbol", "FeatureType", "source_map",
        "student_x_m", "student_y_m", "student_lat", "student_lon",
        "nearest_curator_fid", "nearest_curator_distance_m",
        "nearest_within_200_fid", "nearest_within_200_distance_m",
        "second_within_200_fid", "second_within_200_distance_m",
    ]
    df = pd.read_csv(csv_path, nrows=0)
    assert list(df.columns) == expected_header
