"""
Tier 1 unit tests for mark_mound_centres.py and build_marking_queue.py.

Covers the failure modes the app's specification calls out as worth
guarding (``planning/point-marking-app-spec.md`` § Build notes), plus the
queue construction the PI's widened scope added:

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
   the app must resume at the first unmarked item.
4. **Queue construction.** The layer-1/layer-2 diff has to separate
   merged centroids from curator additions correctly, since misfiling one
   as the other would put the wrong overlay in front of the reviewer.

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

from build_marking_queue import classify_layer_diff  # noqa: E402
from mark_mound_centres import (  # noqa: E402
    _OUTPUT_COLUMNS,
    CropGeometry,
    build_record,
    load_existing_marks,
    load_queue,
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
def queue_csv(tmp_path: Path) -> Path:
    """A review queue mixing phantom and student items.

    Reproduces the real queue's shape at small scale, including the
    two-string-format buffer hazard on the phantom rows and the empty
    buffer cell on student rows.
    """
    header = (
        "queue_index,item_type,source_layer,source_index,candidate_id,"
        "map_name,buffer_metres,x,y,n_partners_within_threshold,"
        "nearest_partner_m,nearest_partner_layer"
    )
    lines = [header]
    for i in range(6):
        lines.append(
            f"{i},phantom,promoted_phantom,{i},{i},K-35-050-4,50,"
            f"300{i:03d}.5,4700000.25,0,120.0,corrected_student",
        )
    for i in range(6, 8):
        lines.append(
            f"{i},phantom,promoted_phantom,{i},{i},K-35-050-4,50.0,"
            f"300{i:03d}.5,4700000.25,0,120.0,corrected_student",
        )
    lines.append(
        "8,phantom,promoted_phantom,8,8,K-35-050-4,150,300100.5,"
        "4700000.25,1,12.0,corrected_student",
    )
    lines.append(
        "9,student_conflation+merge_site,corrected_student,412,,,,"
        "300100.5,4700012.25,1,12.0,promoted_phantom",
    )
    path = tmp_path / "marking-queue.csv"
    path.write_text("\n".join(lines) + "\n")
    return path


# ---------------------------------------------------------------------------
# 1. The buffer_metres float-cast hazard
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_raw_string_grouping_undercounts(queue_csv: Path) -> None:
    """The hazard is real: raw-text grouping loses the ``'50.0'`` rows.

    This test asserts the *bug*, so that the guarantee the next test
    makes is demonstrably worth something.
    """
    raw = [
        line.split(",")[6]
        for line in queue_csv.read_text().splitlines()[1:]
    ]
    assert raw.count("50") == 6, "fixture should hold six bare-'50' rows"
    assert raw.count("50.0") == 2, "fixture should hold two '50.0' rows"
    assert raw.count("50") != 8, "raw-text grouping undercounts R = 50 m"


@pytest.mark.tier1
def test_load_queue_normalises_buffer(queue_csv: Path) -> None:
    """After loading, R = 50 m counts all eight rows, not six."""
    queue = load_queue(queue_csv)
    assert (queue["buffer_metres"] == 50.0).sum() == 8


@pytest.mark.tier1
def test_load_queue_tolerates_empty_buffer(queue_csv: Path) -> None:
    """Student rows carry no buffer; the column stays nullable, not zero.

    Coercing a blank to 0.0 would silently place every student item in an
    R = 0 m band downstream.
    """
    queue = load_queue(queue_csv)
    student = queue[queue["source_layer"] == "corrected_student"].iloc[0]
    assert pd.isna(student["buffer_metres"])


@pytest.mark.tier1
def test_load_queue_rejects_missing_column(tmp_path: Path) -> None:
    """A queue without the required columns fails loudly, not silently."""
    path = tmp_path / "bad.csv"
    path.write_text("queue_index,item_type\n0,phantom\n")
    with pytest.raises(ValueError, match="missing required column"):
        load_queue(path)


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
# Nearby points — the conflation judgement
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_nearby_points_finds_and_measures() -> None:
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
def test_nearby_points_handles_empty_neighbourhood() -> None:
    """No point within the radius yields ``None``, not an error."""
    points = np.array([[400000.0, 4700000.0]])
    nearby, nearest = nearby_student_points(points, 300000.0, 4700000.0)
    assert nearby == []
    assert nearest is None


@pytest.mark.tier1
def test_nearby_points_handles_empty_array() -> None:
    """An empty layer degrades gracefully."""
    nearby, nearest = nearby_student_points(
        np.zeros((0, 2)), 300000.0, 4700000.0,
    )
    assert nearby == []
    assert nearest is None


# ---------------------------------------------------------------------------
# 3. Resume from checkpoint
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_build_record_derives_displacement(queue_csv: Path) -> None:
    """``displacement_m`` is computed from the recorded/marked pair."""
    row = load_queue(queue_csv).iloc[0]
    marked = (float(row["x"]) + 3.0, float(row["y"]) + 4.0)
    record = build_record(row, marked, "distinct", 12.5, "Tester")
    assert record["displacement_m"] == pytest.approx(5.0)
    assert record["verdict"] == "distinct"
    assert record["uncertain"] is False
    assert record["skipped"] is False
    assert set(record) == set(_OUTPUT_COLUMNS)


@pytest.mark.tier1
def test_build_record_carries_provenance(queue_csv: Path) -> None:
    """Item type and source layer survive into the output.

    Without these a student row and a phantom row are indistinguishable
    downstream, and the conflation verdicts become unattributable.
    """
    row = load_queue(queue_csv).iloc[9]
    record = build_record(row, (300100.0, 4700012.0), "distinct", 12.0, "T")
    assert record["source_layer"] == "corrected_student"
    assert record["item_type"] == "student_conflation+merge_site"
    assert record["source_index"] == 412
    assert record["buffer_metres"] is None


@pytest.mark.tier1
def test_symbol_type_change_is_flagged(queue_csv: Path) -> None:
    """A corrected symbol type is recorded as changed; a confirmation is not.

    This flag is the whole point of asking: it makes student
    classification error countable straight from the output file.
    """
    row = load_queue(queue_csv).iloc[9].copy()
    row["student_reviewed_subtype"] = "burial_mound"

    confirmed = build_record(
        row, (1.0, 2.0), "distinct", 12.0, "T", "burial_mound",
    )
    assert confirmed["symbol_type_prior"] == "burial_mound"
    assert confirmed["symbol_type_changed"] is False

    corrected = build_record(
        row, (1.0, 2.0), "distinct", 12.0, "T", "trig_point_on_mound",
    )
    assert corrected["symbol_type_changed"] is True
    assert corrected["symbol_type"] == "trig_point_on_mound"


@pytest.mark.tier1
def test_symbol_type_change_needs_a_prior(queue_csv: Path) -> None:
    """With no prior subtype, a call is recorded but not counted as a change.

    Most student features carry a null ``_reviewed_subtype``. Treating
    those as "changed" would inflate the student-error rate with rows
    where there was nothing to disagree with.
    """
    row = load_queue(queue_csv).iloc[9].copy()
    row["student_reviewed_subtype"] = ""
    record = build_record(
        row, (1.0, 2.0), "distinct", 12.0, "T", "burial_mound",
    )
    assert record["symbol_type"] == "burial_mound"
    assert record["symbol_type_prior"] == ""
    assert record["symbol_type_changed"] is False


@pytest.mark.tier1
def test_phantom_rows_carry_no_symbol_call(queue_csv: Path) -> None:
    """Phantoms have no student classification, so the fields stay empty."""
    row = load_queue(queue_csv).iloc[0]
    record = build_record(row, (1.0, 2.0), "distinct", None, "T")
    assert record["symbol_type"] == ""
    assert record["symbol_type_changed"] is False


@pytest.mark.tier1
def test_build_record_allows_unmarked_skip(queue_csv: Path) -> None:
    """A skipped row records no position and no displacement."""
    row = load_queue(queue_csv).iloc[0]
    record = build_record(row, None, "skipped", None, "Tester")
    assert record["x_marked"] is None
    assert record["displacement_m"] is None
    assert record["skipped"] is True


@pytest.mark.tier1
def test_save_load_round_trip(tmp_path: Path, queue_csv: Path) -> None:
    """Saved marks reload with their values and keys intact."""
    queue = load_queue(queue_csv)
    out = tmp_path / "nested" / "marked-centres.csv"

    marks = {
        0: build_record(
            queue.iloc[0],
            (float(queue.iloc[0]["x"]) + 1.5,
             float(queue.iloc[0]["y"]) - 2.0),
            "distinct", 30.0, "Tester",
        ),
        2: build_record(queue.iloc[2], None, "skipped", None, "Tester"),
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
    tmp_path: Path, queue_csv: Path,
) -> None:
    """No ``.tmp`` residue survives a successful save."""
    queue = load_queue(queue_csv)
    out = tmp_path / "marked-centres.csv"
    save_marks(
        {0: build_record(queue.iloc[0], (1.0, 2.0), "distinct", None, "T")},
        out,
    )
    assert list(tmp_path.glob("*.tmp")) == []


@pytest.mark.tier1
def test_save_preserves_column_order(
    tmp_path: Path, queue_csv: Path,
) -> None:
    """The output schema is stable, since downstream steps consume it."""
    queue = load_queue(queue_csv)
    out = tmp_path / "marked-centres.csv"
    save_marks(
        {0: build_record(queue.iloc[0], (1.0, 2.0), "distinct", None, "T")},
        out,
    )
    assert list(pd.read_csv(out).columns) == _OUTPUT_COLUMNS


@pytest.mark.tier1
def test_load_existing_marks_on_missing_file(tmp_path: Path) -> None:
    """A first run starts from an empty mark set rather than failing."""
    assert load_existing_marks(tmp_path / "not-there.csv") == {}


@pytest.mark.tier1
def test_resume_finds_first_unmarked_row(
    tmp_path: Path, queue_csv: Path,
) -> None:
    """Resuming skips completed items but stops at the first gap.

    Reproduces the app's resume rule: items 0, 1 and 3 marked, so the
    session should resume at item 2 — not at item 4, and not at item 0.
    """
    queue = load_queue(queue_csv)
    out = tmp_path / "marked-centres.csv"
    marks = {
        i: build_record(queue.iloc[i], (1.0, 2.0), "distinct", None, "T")
        for i in (0, 1, 3)
    }
    save_marks(marks, out)

    reloaded = load_existing_marks(out)
    remaining = [i for i in range(len(queue)) if i not in reloaded]
    assert remaining[0] == 2


# ---------------------------------------------------------------------------
# 4. Queue construction
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_classify_layer_diff_separates_merges_from_additions() -> None:
    """A merged centroid has two superseded points; an addition has none.

    Misfiling one as the other would put the wrong overlay in front of
    the reviewer — a merge site with no red points to check against, or
    an addition claiming to supersede something.
    """
    # Two originals 30 m apart, replaced by a centroid between them.
    original = np.array([
        [300000.0, 4700000.0],
        [300030.0, 4700000.0],
        [301000.0, 4700000.0],   # untouched survivor
    ])
    corrected = np.array([
        [300015.0, 4700000.0],   # the merged centroid
        [301000.0, 4700000.0],   # the survivor, unchanged
        [305000.0, 4700000.0],   # a curator addition, nothing nearby
    ])
    merges, additions, superseded = classify_layer_diff(original, corrected)
    assert merges == [0]
    assert additions == [2]
    assert len(superseded) == 2


@pytest.mark.tier1
def test_classify_layer_diff_treats_unchanged_points_as_unchanged() -> None:
    """Identical layers produce no merges, no additions, no superseded."""
    points = np.array([[300000.0, 4700000.0], [301000.0, 4700000.0]])
    merges, additions, superseded = classify_layer_diff(points, points.copy())
    assert merges == []
    assert additions == []
    assert len(superseded) == 0


@pytest.mark.tier2
@pytest.mark.integration
def test_queue_matches_the_recorded_layer_derivation() -> None:
    """The real layer diff reproduces ruling 19's recorded derivation.

    Layer 2 is documented as ``4770 - 52 + 28 = 4746``, of which 26 are
    merged centroids and 2 curator additions. Deriving that independently
    from the files is a check on both the layers and this code.
    """
    from audit_mound_proximity import (
        _LAYER_CORRECTED_STUDENT,
        _LAYER_FIXED_ORIGINAL,
        load_points_geojson,
    )

    original_path = PROJECT_ROOT / _LAYER_FIXED_ORIGINAL
    corrected_path = PROJECT_ROOT / _LAYER_CORRECTED_STUDENT
    for required in (original_path, corrected_path):
        if not required.exists():
            pytest.skip(f"missing GT layer: {required}")

    original = load_points_geojson(original_path)
    corrected = load_points_geojson(corrected_path)
    assert len(original) == 4770
    assert len(corrected) == 4746

    merges, additions, superseded = classify_layer_diff(original, corrected)
    assert len(superseded) == 52
    assert len(merges) + len(additions) == 28
    assert len(merges) == 26
    assert len(additions) == 2


@pytest.mark.tier2
@pytest.mark.integration
def test_jitter_sample_is_conflation_free_and_reproducible() -> None:
    """The jitter sample must be clean and stable across rebuilds.

    Clean: a point with an unresolved neighbour would measure conflation,
    not digitisation error, so every sampled point must sit further than
    the conflation threshold from any phantom and any other student mound.

    Stable: the seed is fixed because a re-draw mid-review would silently
    change the queue under a partially-completed marking session.
    """
    from build_marking_queue import _DEFAULT_THRESHOLD_M, build_queue

    gt_dir = PROJECT_ROOT / "results/deployment-oracle-2026-06-06/canonical-gt"
    if not (gt_dir / "canonical-review.csv").exists():
        pytest.skip("missing canonical-review.csv")

    from scipy.spatial import cKDTree

    from audit_mound_proximity import (
        _LAYER_CORRECTED_STUDENT,
        _LAYER_PROMOTED,
        load_points_csv,
        load_points_geojson,
    )

    queue, _ = build_queue()
    sample = queue[queue["item_type"] == "jitter_sample"]
    assert len(sample) == 100

    students = load_points_geojson(PROJECT_ROOT / _LAYER_CORRECTED_STUDENT)
    phantoms = load_points_csv(PROJECT_ROOT / _LAYER_PROMOTED)
    points = np.column_stack([
        sample["x"].to_numpy(float), sample["y"].to_numpy(float),
    ])

    to_phantom, _ = cKDTree(phantoms).query(points, k=1)
    # k=2: the closest student point to a sampled student *is* itself.
    to_student, _ = cKDTree(students).query(points, k=2)
    assert to_phantom.min() > _DEFAULT_THRESHOLD_M
    assert to_student[:, 1].min() > _DEFAULT_THRESHOLD_M

    rebuilt, _ = build_queue()
    rebuilt_sample = rebuilt[rebuilt["item_type"] == "jitter_sample"]
    assert list(sample["source_index"]) == list(rebuilt_sample["source_index"])


@pytest.mark.tier1
def test_jitter_sample_can_be_disabled() -> None:
    """``--jitter-sample 0`` leaves the queue at its conflation-only size."""
    from build_marking_queue import build_queue

    gt_dir = PROJECT_ROOT / "results/deployment-oracle-2026-06-06/canonical-gt"
    if not (gt_dir / "canonical-review.csv").exists():
        pytest.skip("missing canonical-review.csv")
    queue, _ = build_queue(jitter_sample=0)
    assert (queue["item_type"] == "jitter_sample").sum() == 0


@pytest.mark.tier2
@pytest.mark.integration
def test_app_renders_against_real_inputs(tmp_path: Path) -> None:
    """The Streamlit script executes end to end against the real corpus.

    The tier-1 tests above exercise every pure function, but not the UI
    wiring — session state, the resume rule, the widget layout. Streamlit's
    own ``AppTest`` harness runs the script body headlessly, which is the
    only way to catch a break in that layer without a browser.

    Skipped when the 2.4 GB raster corpus or the queue inputs are absent,
    so the suite still runs on a machine holding only the code.
    """
    from streamlit.testing.v1 import AppTest

    gt_dir = PROJECT_ROOT / "results/deployment-oracle-2026-06-06/canonical-gt"
    queue_path = gt_dir / "marking-queue.csv"
    phantom_path = gt_dir / "canonical-review.csv"
    rasters = PROJECT_ROOT / "inputs/rasters/Russian1981_32635"
    student_gt = PROJECT_ROOT / (
        "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
    )
    for required in (queue_path, phantom_path, rasters, student_gt):
        if not required.exists():
            pytest.skip(f"missing corpus input: {required}")

    original_argv = sys.argv
    sys.argv = [
        "mark_mound_centres.py",
        "--queue-csv", str(queue_path),
        "--phantom-csv", str(phantom_path),
        "--superseded-csv", str(gt_dir / "superseded-marking-queue.csv"),
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
    labels = [button.label for button in app.button]
    for expected in ("d: Distinct mound", "c: Same as a neighbour",
                     "u: Uncertain", "s: Skip", "n: Next"):
        assert expected in labels, f"missing control: {expected}"
    assert any("0 / 1006" in str(m.value) for m in app.metric)
