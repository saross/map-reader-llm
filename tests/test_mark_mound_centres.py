"""
Tier 1 unit tests for mark_mound_centres.py.

Covers the three failure modes the app's specification calls out as
worth guarding (``planning/point-marking-app-spec.md`` § Build notes):

1. **The ``buffer_metres`` float-cast hazard.** The source CSV stores the
   column in two string formats (``'50'`` and ``'50.0'``). Anything that
   buckets on the raw text reports 410 at R = 50 m instead of the true
   415 — a plausible-looking number that is simply wrong.
2. **The coordinate round-trip.** Display pixel to raster CRS and back
   must be lossless, and — the point of the whole exercise — a click at
   the geometric centre of the image must NOT be assumed to be the
   recorded position. The crop window is framed on the pixel *corner*
   that ``src.index`` floors to, which sits up to one pixel diagonal
   (7.09 m at these sheets' 5.012 m/px) from the recorded point.
   Measured across the real 773: median 4.02 m, max 7.00 m, with 176
   rows (22.8%) exceeding the 5 m de-duplication tolerance.
3. **Resume from checkpoint.** An hour of clicking must survive a crash,
   so the saved file has to round-trip through save/load unchanged and
   the app must resume at the first unmarked row.

All synthetic — no rasters, no API calls, no reviewer input.
"""

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from affine import Affine

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from mark_mound_centres import (  # noqa: E402
    _OUTPUT_COLUMNS,
    CropGeometry,
    build_record,
    load_existing_marks,
    load_phantoms,
    nearby_student_points,
    save_marks,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def geometry() -> CropGeometry:
    """A crop geometry with the real corpus's 5.012 m/px resolution.

    North-up, square pixels, origin at a round easting/northing so the
    arithmetic in the assertions stays checkable by hand.
    """
    res = 5.011567404034814
    transform = Affine(res, 0.0, 300000.0, 0.0, -res, 4700000.0)
    return CropGeometry(
        transform_coeffs=tuple(transform)[:6],
        col_origin=1000,
        row_origin=2000,
        window_px=40,
        display_px=700,
    )


@pytest.fixture
def mixed_format_csv(tmp_path: Path) -> Path:
    """A review CSV reproducing the two-string-format buffer hazard.

    Mirrors the real file's shape at small scale: eight rows at R = 50 m,
    six of them written ``'50'`` and two written ``'50.0'``, plus two at
    other bands.
    """
    lines = ["candidate_id,human_label,buffer_metres,x,y,map_name"]
    for i in range(6):
        lines.append(f"{i},mound,50,300{i:03d}.5,4700000.25,K-35-050-4")
    for i in range(6, 8):
        lines.append(f"{i},mound,50.0,300{i:03d}.5,4700000.25,K-35-050-4")
    lines.append("8,mound,75,300100.5,4700000.25,K-35-050-4")
    lines.append("9,mound,150.0,300200.5,4700000.25,K-35-051-3")
    path = tmp_path / "canonical-review.csv"
    path.write_text("\n".join(lines) + "\n")
    return path


# ---------------------------------------------------------------------------
# 1. The buffer_metres float-cast hazard
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_raw_string_grouping_undercounts(mixed_format_csv: Path) -> None:
    """The hazard is real: raw-text grouping loses the ``'50.0'`` rows.

    This test asserts the *bug*, so that the guarantee the next test
    makes is demonstrably worth something.
    """
    raw = [
        line.split(",")[2]
        for line in mixed_format_csv.read_text().splitlines()[1:]
    ]
    assert raw.count("50") == 6, "fixture should hold six bare-'50' rows"
    assert raw.count("50.0") == 2, "fixture should hold two '50.0' rows"
    assert raw.count("50") != 8, "raw-text grouping undercounts R = 50 m"


@pytest.mark.tier1
def test_load_phantoms_normalises_buffer(mixed_format_csv: Path) -> None:
    """After loading, R = 50 m counts all eight rows, not six."""
    df = load_phantoms(mixed_format_csv)
    assert df["buffer_metres"].dtype == float
    assert (df["buffer_metres"] == 50.0).sum() == 8
    cumulative = [int((df["buffer_metres"] <= b).sum()) for b in (50, 75, 150)]
    assert cumulative == [8, 9, 10]


@pytest.mark.tier1
def test_load_phantoms_adds_stable_key(mixed_format_csv: Path) -> None:
    """``row_index`` is added, since ``candidate_id`` is not an identifier."""
    df = load_phantoms(mixed_format_csv)
    assert list(df["row_index"]) == list(range(len(df)))


@pytest.mark.tier1
def test_load_phantoms_rejects_missing_column(tmp_path: Path) -> None:
    """A CSV without the required columns fails loudly, not silently."""
    path = tmp_path / "bad.csv"
    path.write_text("candidate_id,human_label\n0,mound\n")
    with pytest.raises(ValueError, match="missing required column"):
        load_phantoms(path)


@pytest.mark.tier1
def test_load_phantoms_rejects_non_mound_rows(tmp_path: Path) -> None:
    """Scope is confirmed mounds only (ruling 21c); anything else errors."""
    path = tmp_path / "mixed.csv"
    path.write_text(
        "candidate_id,human_label,buffer_metres,x,y,map_name\n"
        "0,mound,50,300000,4700000,K-35-050-4\n"
        "1,not_mound,50,300010,4700000,K-35-050-4\n",
    )
    with pytest.raises(ValueError, match="non-mound rows"):
        load_phantoms(path)


# ---------------------------------------------------------------------------
# 2. The coordinate round-trip
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_world_display_round_trip_is_lossless(geometry: CropGeometry) -> None:
    """world -> display -> world returns the input to floating-point noise."""
    for world_x, world_y in [
        (305010.0, 4689990.0),
        (305012.7, 4689987.3),
        (305000.123456, 4690001.987654),
    ]:
        px, py = geometry.world_to_display(world_x, world_y)
        back_x, back_y = geometry.display_to_world(px, py)
        assert math.hypot(back_x - world_x, back_y - world_y) < 1e-6


@pytest.mark.tier1
def test_display_world_round_trip_is_lossless(geometry: CropGeometry) -> None:
    """display -> world -> display returns the input, including sub-pixels."""
    for px, py in [(0.0, 0.0), (350.0, 350.0), (699.0, 12.5), (123.4, 567.8)]:
        world_x, world_y = geometry.display_to_world(px, py)
        back_px, back_py = geometry.world_to_display(world_x, world_y)
        assert math.hypot(back_px - px, back_py - py) < 1e-6


@pytest.mark.tier1
def test_display_scale_matches_declared_resolution(
    geometry: CropGeometry,
) -> None:
    """One display pixel spans the advertised ground distance."""
    left = geometry.display_to_world(0.0, 0.0)
    right = geometry.display_to_world(1.0, 0.0)
    assert right[0] - left[0] == pytest.approx(
        geometry.metres_per_display_px,
    )
    # 40 raster px of 5.0116 m across 700 display px.
    assert geometry.metres_per_display_px == pytest.approx(
        40 * 5.011567404034814 / 700,
    )


@pytest.mark.tier1
def test_y_axis_is_not_inverted(geometry: CropGeometry) -> None:
    """Clicking higher on screen must yield a *larger* northing.

    A sign error here would be invisible in the UI (the mark lands under
    the cursor either way) but would mirror every displacement about the
    east-west axis.
    """
    top = geometry.display_to_world(350.0, 100.0)
    bottom = geometry.display_to_world(350.0, 600.0)
    assert top[1] > bottom[1]


@pytest.mark.tier1
def test_image_centre_is_not_the_recorded_position(
    geometry: CropGeometry,
) -> None:
    """The framing offset is real and must not be assumed away.

    The window spans ``col_origin`` to ``col_origin + window_px``, so its
    geometric centre lands on the pixel *corner* the recorded point was
    floored to — up to one pixel diagonal away. This test pins the
    behaviour that motivates converting clicks through the transform
    rather than treating the image centre as the recorded position.
    """
    res = 5.011567404034814
    # A point 0.9 px right and 0.8 px down from the window's centre corner.
    recorded_x = 300000.0 + (1000 + 20 + 0.9) * res
    recorded_y = 4700000.0 - (2000 + 20 + 0.8) * res

    centre_x, centre_y = geometry.display_to_world(350.0, 350.0)
    offset = math.hypot(centre_x - recorded_x, centre_y - recorded_y)

    expected = math.hypot(0.9, 0.8) * res
    assert offset == pytest.approx(expected, abs=1e-6)
    assert offset > 5.0, (
        "this configuration should exceed the 5 m de-duplication "
        "tolerance, which is exactly why the offset cannot be ignored"
    )
    assert offset <= res * math.sqrt(2) + 1e-9, (
        "offset must never exceed one pixel diagonal (7.09 m)"
    )


@pytest.mark.tier1
def test_geometry_survives_pickling(geometry: CropGeometry) -> None:
    """Streamlit's cache pickles the geometry; it must come back intact."""
    import pickle

    restored = pickle.loads(pickle.dumps(geometry))
    assert restored == geometry
    assert restored.display_to_world(123.0, 456.0) == (
        geometry.display_to_world(123.0, 456.0)
    )


# ---------------------------------------------------------------------------
# Nearby student points — the conflation judgement
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_nearby_student_points_finds_and_measures() -> None:
    """Points inside the radius are returned; the nearest distance is exact."""
    points = np.array([
        [300000.0, 4700000.0],   # 0 m — coincident
        [300012.0, 4700000.0],   # 12 m — borderline band
        [300400.0, 4700000.0],   # 400 m — outside the search radius
    ])
    nearby, nearest = nearby_student_points(
        points, 300012.0, 4700000.0, radius_m=250.0,
    )
    assert len(nearby) == 2
    assert nearest == pytest.approx(0.0)

    nearby, nearest = nearby_student_points(
        points, 300030.0, 4700000.0, radius_m=250.0,
    )
    assert nearest == pytest.approx(18.0)


@pytest.mark.tier1
def test_nearby_student_points_handles_empty_neighbourhood() -> None:
    """No student point within the radius yields ``None``, not an error."""
    points = np.array([[400000.0, 4700000.0]])
    nearby, nearest = nearby_student_points(points, 300000.0, 4700000.0)
    assert nearby == []
    assert nearest is None


@pytest.mark.tier1
def test_nearby_student_points_handles_empty_array() -> None:
    """An empty ground-truth layer degrades gracefully."""
    nearby, nearest = nearby_student_points(
        np.zeros((0, 2)), 300000.0, 4700000.0,
    )
    assert nearby == []
    assert nearest is None


# ---------------------------------------------------------------------------
# 3. Resume from checkpoint
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_build_record_derives_displacement(mixed_format_csv: Path) -> None:
    """``displacement_m`` is computed from the recorded/marked pair."""
    row = load_phantoms(mixed_format_csv).iloc[0]
    marked = (float(row["x"]) + 3.0, float(row["y"]) + 4.0)
    record = build_record(row, marked, "distinct", 12.5, "Tester")
    assert record["displacement_m"] == pytest.approx(5.0)
    assert record["verdict"] == "distinct"
    assert record["uncertain"] is False
    assert record["skipped"] is False
    assert set(record) == set(_OUTPUT_COLUMNS)


@pytest.mark.tier1
def test_build_record_allows_unmarked_skip(mixed_format_csv: Path) -> None:
    """A skipped row records no position and no displacement."""
    row = load_phantoms(mixed_format_csv).iloc[0]
    record = build_record(row, None, "skipped", None, "Tester")
    assert record["x_marked"] is None
    assert record["displacement_m"] is None
    assert record["skipped"] is True


@pytest.mark.tier1
def test_save_load_round_trip(tmp_path: Path, mixed_format_csv: Path) -> None:
    """Saved marks reload with their values and keys intact."""
    phantoms = load_phantoms(mixed_format_csv)
    out = tmp_path / "nested" / "marked-centres.csv"

    marks = {
        0: build_record(
            phantoms.iloc[0],
            (float(phantoms.iloc[0]["x"]) + 1.5,
             float(phantoms.iloc[0]["y"]) - 2.0),
            "distinct", 30.0, "Tester",
        ),
        2: build_record(
            phantoms.iloc[2], None, "skipped", None, "Tester",
        ),
    }
    save_marks(marks, out)
    assert out.exists(), "parent directories should be created"

    reloaded = load_existing_marks(out)
    assert set(reloaded) == {0, 2}
    assert reloaded[0]["verdict"] == "distinct"
    assert reloaded[0]["displacement_m"] == pytest.approx(2.5)
    assert reloaded[2]["skipped"] in (True, "True", np.True_)
    assert pd.isna(reloaded[2]["x_marked"])


@pytest.mark.tier1
def test_save_is_atomic_and_leaves_no_temp(
    tmp_path: Path, mixed_format_csv: Path,
) -> None:
    """No ``.tmp`` residue survives a successful save."""
    phantoms = load_phantoms(mixed_format_csv)
    out = tmp_path / "marked-centres.csv"
    save_marks(
        {0: build_record(phantoms.iloc[0], (1.0, 2.0), "distinct", None, "T")},
        out,
    )
    assert list(tmp_path.glob("*.tmp")) == []


@pytest.mark.tier1
def test_save_preserves_column_order(
    tmp_path: Path, mixed_format_csv: Path,
) -> None:
    """The output schema is stable, since downstream steps consume it."""
    phantoms = load_phantoms(mixed_format_csv)
    out = tmp_path / "marked-centres.csv"
    save_marks(
        {0: build_record(phantoms.iloc[0], (1.0, 2.0), "distinct", None, "T")},
        out,
    )
    assert list(pd.read_csv(out).columns) == _OUTPUT_COLUMNS


@pytest.mark.tier1
def test_load_existing_marks_on_missing_file(tmp_path: Path) -> None:
    """A first run starts from an empty mark set rather than failing."""
    assert load_existing_marks(tmp_path / "not-there.csv") == {}


@pytest.mark.tier2
@pytest.mark.integration
def test_app_renders_against_real_inputs(tmp_path: Path) -> None:
    """The Streamlit script executes end to end against the real corpus.

    The tier-1 tests above exercise every pure function, but not the UI
    wiring — session state, the resume rule, the widget layout. Streamlit's
    own ``AppTest`` harness runs the script body headlessly, which is the
    only way to catch a break in that layer without a browser.

    Skipped when the 2.4 GB raster corpus or the review CSV is absent, so
    the suite still runs on a machine holding only the code.
    """
    from streamlit.testing.v1 import AppTest

    review_csv = PROJECT_ROOT / (
        "results/deployment-oracle-2026-06-06/canonical-gt/"
        "canonical-review.csv"
    )
    rasters = PROJECT_ROOT / "inputs/rasters/Russian1981_32635"
    student_gt = PROJECT_ROOT / (
        "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
    )
    for required in (review_csv, rasters, student_gt):
        if not required.exists():
            pytest.skip(f"missing corpus input: {required}")

    original_argv = sys.argv
    sys.argv = [
        "mark_mound_centres.py",
        "--review-csv", str(review_csv),
        "--rasters-dir", str(rasters),
        "--student-gt", str(student_gt),
        "--output", str(tmp_path / "marked-centres.csv"),
        "--marked-by", "pytest",
    ]
    try:
        app = AppTest.from_file(
            str(PROJECT_ROOT / "scripts" / "mark_mound_centres.py"),
            default_timeout=180,
        ).run()
    finally:
        sys.argv = original_argv

    assert not app.exception, (
        f"app raised: {[e.message for e in app.exception]}"
    )
    # Every verdict and both navigation controls should be present.
    labels = [button.label for button in app.button]
    for expected in ("d: Distinct mound", "c: Same as student point",
                     "u: Uncertain", "s: Skip", "n: Next"):
        assert expected in labels, f"missing control: {expected}"
    # Progress metric reflects the full 773-row scope, starting empty.
    assert any("0 / 773" in str(m.value) for m in app.metric)


@pytest.mark.tier1
def test_resume_finds_first_unmarked_row(
    tmp_path: Path, mixed_format_csv: Path,
) -> None:
    """Resuming skips completed rows but stops at the first gap.

    Reproduces the app's resume rule: rows 0, 1 and 3 marked, so the
    session should resume at row 2 — not at row 4, and not at row 0.
    """
    phantoms = load_phantoms(mixed_format_csv)
    out = tmp_path / "marked-centres.csv"
    marks = {
        i: build_record(phantoms.iloc[i], (1.0, 2.0), "distinct", None, "T")
        for i in (0, 1, 3)
    }
    save_marks(marks, out)

    reloaded = load_existing_marks(out)
    remaining = [i for i in range(len(phantoms)) if i not in reloaded]
    assert remaining[0] == 2
