"""
Tests for ``scripts/carry_probabilities.py``.

Tier-1 unit tests over synthetic candidate manifests. The script re-keys a
committed verifier ``probabilities.json`` onto a rebuilt consensus union's
candidate numbering, and its job is to be right about **which candidates a
subsequent verifier run must pay for**. Two things therefore have to hold:

1. **Matching is positional, one-to-one, and tolerance-bounded.** A rebuilt
   union re-numbers everything, so identity comes from coordinates; a
   candidate beyond the tolerance is uncovered rather than mis-matched, and no
   old candidate is claimed twice.
2. **Coverage is judged on the integer crop window, not on metric distance.**
   This is the lesson the script was promoted to ``scripts/`` for
   (``reports/recovery-drop-fix-2026-09-13.md`` § 6.1): on 2026-09-13 a
   candidate whose centroid had moved 3.026 m was classified uncovered on a
   2 m tolerance and re-verified for US$0.000757, when its crop window was
   ``(3177, 3192)`` either side and the verifier was shown the same image and
   returned the same 0.95. ``window_identical`` is what a caller should read.

The window resolver is injected, so these tests need no GeoTIFF sheets.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.carry_probabilities import (
    DEFAULT_PADDING,
    CarryReport,
    build_provenance,
    build_seeded_probabilities,
    carry_probabilities,
    sheet_of,
)

pytestmark = pytest.mark.tier1

#: A pixel size close to the project's sheets (measured 5.0102–5.0315 m/px),
#: so "sub-pixel" in these tests means what it means in the corpus.
METRES_PER_PIXEL = 5.02


def _candidate(
    candidate_id: int,
    x: float,
    y: float,
    *,
    sheet: str = "K-35-052-4_32635",
    votes: int = 3,
) -> dict:
    """Build one ``candidate_manifest.json`` entry.

    Args:
        candidate_id: The manifest's own candidate number.
        x: Projected easting of the centroid.
        y: Projected northing of the centroid.
        sheet: Raster sheet stem, embedded in ``source_tile``.
        votes: Consensus vote count, carried in ``properties``.

    Returns:
        A manifest entry in the shape ``extract_candidates`` writes.
    """
    return {
        "candidate_id": candidate_id,
        "centroid_x": x,
        "centroid_y": y,
        "source_tile": f"{sheet}_x0_y0.png",
        "properties": {"vote_count": votes},
    }


def _floor_window(
    sheet: str | None, cx: float, cy: float,
) -> tuple[int, int] | None:
    """Stand in for the raster resolver: floor to whole pixels.

    Reproduces what ``rasterio.DatasetReader.index`` does to a projected
    centroid — floor to a whole (row, col) — without needing a GeoTIFF.

    Args:
        sheet: Sheet stem, or ``None`` when the tile name did not parse.
        cx: Projected easting.
        cy: Projected northing.

    Returns:
        ``(col_off, row_off)``, or ``None`` when ``sheet`` is ``None``.
    """
    if sheet is None:
        return None
    col = int(cx // METRES_PER_PIXEL) - DEFAULT_PADDING
    row = int(cy // METRES_PER_PIXEL) - DEFAULT_PADDING
    return (col, row)


# --------------------------------------------------------------------------
# 1. Matching
# --------------------------------------------------------------------------

def test_an_exact_match_carries_the_committed_result():
    """A candidate at the same coordinates carries its probability."""
    old = [_candidate(1, 1000.0, 2000.0)]
    new = [_candidate(42, 1000.0, 2000.0)]
    report = carry_probabilities(
        old, new, {"candidate_00001": {"mound_probability": 0.95}},
        window_resolver=_floor_window,
    )
    assert report.carried == {"candidate_00042": {"mound_probability": 0.95}}
    assert report.uncovered == []
    assert report.carry_log[0]["old_key"] == "candidate_00001"
    assert report.carry_log[0]["distance_m"] == 0.0
    assert report.carry_log[0]["window_identical"] is True
    assert report.displaced == []


def test_a_candidate_beyond_the_tolerance_is_uncovered_not_mismatched():
    """Better an uncovered candidate than a probability from another mound."""
    old = [_candidate(1, 1000.0, 2000.0)]
    new = [_candidate(1, 1050.0, 2000.0, votes=1)]
    report = carry_probabilities(
        old, new, {"candidate_00001": {"mound_probability": 0.95}},
        tolerance=2.0, window_resolver=_floor_window,
    )
    assert report.carried == {}
    assert len(report.uncovered) == 1
    entry = report.uncovered[0]
    assert entry["new_key"] == "candidate_00001"
    assert entry["vote_count"] == 1
    assert entry["source_tile"].startswith("K-35-052-4_32635")
    # The uncovered set is what a verifier run pays for, so it must carry
    # enough to price and audit that run.
    assert entry["centroid_x"] == 1050.0


def test_matching_is_one_to_one():
    """Two new candidates cannot both claim one old result."""
    old = [_candidate(1, 1000.0, 2000.0)]
    new = [
        _candidate(1, 1000.0, 2000.0),
        _candidate(2, 1000.5, 2000.0),
    ]
    report = carry_probabilities(
        old, new, {"candidate_00001": {"mound_probability": 0.95}},
        tolerance=2.0, window_resolver=_floor_window,
    )
    assert list(report.carried) == ["candidate_00001"]
    assert [e["new_key"] for e in report.uncovered] == ["candidate_00002"]


def test_the_nearest_old_candidate_wins():
    """Within the tolerance the closest unclaimed old candidate is chosen."""
    old = [
        _candidate(1, 1000.0, 2000.0),
        _candidate(2, 1001.5, 2000.0),
    ]
    new = [_candidate(9, 1001.4, 2000.0)]
    report = carry_probabilities(
        old, new,
        {
            "candidate_00001": {"mound_probability": 0.10},
            "candidate_00002": {"mound_probability": 1.0},
        },
        tolerance=2.0, window_resolver=_floor_window,
    )
    assert report.carried["candidate_00009"]["mound_probability"] == 1.0
    assert report.carry_log[0]["old_key"] == "candidate_00002"


def test_a_positional_match_without_a_committed_result_is_uncovered():
    """A matched old key absent from the probabilities is named, not carried."""
    old = [_candidate(1, 1000.0, 2000.0)]
    new = [_candidate(1, 1000.0, 2000.0)]
    report = carry_probabilities(
        old, new, {}, window_resolver=_floor_window,
    )
    assert report.carried == {}
    assert "absent from the committed probabilities" in (
        report.uncovered[0]["note"]
    )


def test_candidates_are_matched_across_bucket_boundaries():
    """The neighbourhood search spans buckets, so a boundary is not a wall.

    The bucket grid has side ``max(tolerance, 1.0)``, so two candidates 0.5 m
    apart routinely fall in different buckets. A bug that searched only the
    home bucket would pass every test above and fail here.
    """
    tolerance = 1.0
    # Straddle an exact multiple of the cell size.
    old = [_candidate(1, 999.9, 2000.0)]
    new = [_candidate(1, 1000.1, 2000.0)]
    report = carry_probabilities(
        old, new, {"candidate_00001": {"mound_probability": 0.5}},
        tolerance=tolerance, window_resolver=_floor_window,
    )
    assert list(report.carried) == ["candidate_00001"]
    assert report.carry_log[0]["distance_m"] == pytest.approx(0.2, abs=1e-6)


# --------------------------------------------------------------------------
# 2. Coverage is the integer crop window, not the metric distance
# --------------------------------------------------------------------------

def test_a_sub_pixel_shift_keeps_a_byte_identical_crop_window():
    """The § 6.1 lesson: a displaced candidate can still be exactly valid.

    The centroid moves 3.0 m — beyond the 2 m tolerance a coverage test on
    metric distance would use — but both centroids floor to the same pixel,
    so the verifier would be shown the same image and the carried probability
    is exact rather than merely close.
    """
    base = 1000.0
    # Stay inside one pixel: 1000.0 and 1003.0 both floor to pixel 199 at
    # 5.02 m/px, since 199 * 5.02 = 998.98 and 200 * 5.02 = 1004.0.
    old = [_candidate(1, base, 2000.0)]
    new = [_candidate(1, base + 3.0, 2000.0)]
    report = carry_probabilities(
        old, new, {"candidate_00001": {"mound_probability": 0.95}},
        tolerance=5.0, window_resolver=_floor_window,
    )
    entry = report.carry_log[0]
    assert entry["distance_m"] == pytest.approx(3.0, abs=1e-6)
    assert entry["old_window"] == entry["new_window"]
    assert entry["window_identical"] is True
    # Displaced, but NOT window-changed: the distinction the script exists for.
    assert len(report.displaced) == 1
    assert report.window_changed == []


def test_a_shift_across_a_pixel_boundary_is_flagged():
    """A carry whose crop moved by a pixel is surfaced for a judgement call."""
    # 1003.9 floors to pixel 199; 1004.1 floors to pixel 200.
    old = [_candidate(1, 1003.9, 2000.0)]
    new = [_candidate(1, 1004.1, 2000.0)]
    report = carry_probabilities(
        old, new, {"candidate_00001": {"mound_probability": 0.10}},
        tolerance=2.0, window_resolver=_floor_window,
    )
    entry = report.carry_log[0]
    assert entry["old_window"] != entry["new_window"]
    assert entry["window_identical"] is False
    assert len(report.window_changed) == 1
    # It is still carried — carrying is the caller's decision — but the
    # artefact says the image differs, which is what makes the decision
    # reviewable rather than invisible.
    assert list(report.carried) == ["candidate_00001"]


def test_sheet_of_parses_the_tiling_convention():
    """The sheet stem comes off the tile name, or is ``None``."""
    assert sheet_of("K-35-052-4_32635_x2880_y3072.png") == "K-35-052-4_32635"
    assert sheet_of("K-35-065-3_Glavan_4326_x0_y0.png") == "K-35-065-3_Glavan_4326"
    assert sheet_of("candidate.png") is None
    assert sheet_of(None) is None


def test_an_unresolvable_sheet_does_not_crash_the_carry():
    """A tile name that does not parse yields no window, and is recorded."""
    old = [_candidate(1, 1000.0, 2000.0)]
    new = [_candidate(1, 1000.0, 2000.0)]
    old[0]["source_tile"] = "not-a-tile.png"
    new[0]["source_tile"] = "not-a-tile.png"
    report = carry_probabilities(
        old, new, {"candidate_00001": {"mound_probability": 0.95}},
        window_resolver=_floor_window,
    )
    entry = report.carry_log[0]
    assert entry["old_window"] is None and entry["new_window"] is None
    # Both unresolved compare equal, so this is NOT reported as a changed
    # window — the honest reading is "not measured", and the None values in
    # the artefact say so.
    assert entry["window_identical"] is True


# --------------------------------------------------------------------------
# 3. The artefacts
# --------------------------------------------------------------------------

def test_the_seeded_probabilities_match_the_resume_filter_schema():
    """``run_pv.py``'s resume filter reads this shape, and the header carries."""
    report = CarryReport(carried={"candidate_00001": {"mound_probability": 1.0}})
    seeded = build_seeded_probabilities(
        report,
        {
            "mode": "realtime",
            "verifier_config": "verify_adversarial-text",
            "iterations": 1,
            "results": {},
        },
    )
    assert seeded["version"] == "1.0"
    assert seeded["total_results"] == 1
    assert list(seeded["results"]) == ["candidate_00001"]
    # Carried from the committed stage, never restated, so a seeded stage
    # cannot silently claim a different verifier.
    assert seeded["verifier_config"] == "verify_adversarial-text"
    assert seeded["mode"] == "realtime"


def test_the_provenance_counts_what_a_run_will_pay_for(tmp_path):
    """``uncovered`` is the number of API calls the next run makes."""
    old = [_candidate(i, 1000.0 + 100 * i, 2000.0) for i in range(1, 4)]
    new = old + [_candidate(99, 9999.0, 9999.0)]
    report = carry_probabilities(
        old, new,
        {f"candidate_{i:05d}": {"mound_probability": 0.5} for i in range(1, 4)},
        window_resolver=_floor_window,
    )
    provenance = build_provenance(
        report,
        label="k3",
        old_probs_path=tmp_path / "old" / "probabilities.json",
        old_manifest_path=tmp_path / "crops_old" / "candidate_manifest.json",
        new_manifest_path=tmp_path / "crops_new" / "candidate_manifest.json",
        old_manifest={"candidates": old, "source_geojson": "old.geojson"},
        new_manifest={"candidates": new, "source_geojson": "new.geojson"},
        tolerance=2.0,
    )
    assert provenance["schema"] == "verifier-stage-carry/1"
    assert provenance["old_candidates"] == 3
    assert provenance["new_candidates"] == 4
    assert provenance["carried"] == 3
    assert provenance["uncovered"] == 1
    assert provenance["carried_with_changed_pixel_window"] == 0
    assert provenance["uncovered_detail"][0]["new_key"] == "candidate_00099"
    assert provenance["old_union"] == "old.geojson"
    # The record must serialise: it is written as JSON.
    json.dumps(provenance)


def test_the_promoted_script_reproduces_the_committed_carry_provenance():
    """The committed carry records stay reproducible after the promotion.

    The script moved from the recovery-fix harness into ``scripts/`` with its
    matching and window logic unchanged. The committed
    ``carry_provenance.json`` files are the evidence of that: their headline
    counts are asserted here, so a future refactor that changes the matching
    fails rather than silently re-writing history.
    """
    stages = {
        "verify_k1_recovery-fixed": (640, 639, 1),
        "verify_k3_recovery-fixed": (759, 756, 3),
    }
    root = Path("outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37")
    for stage, (n_new, n_carried, n_uncovered) in stages.items():
        path = root / stage / "carry_provenance.json"
        if not path.exists():  # pragma: no cover - artefact not checked out
            pytest.skip(f"{path} not present in this checkout")
        record = json.loads(path.read_text())
        assert record["schema"] == "verifier-stage-carry/1"
        assert record["new_candidates"] == n_new
        assert record["carried"] == n_carried
        assert record["uncovered"] == n_uncovered
        assert len(record["uncovered_detail"]) == n_uncovered
