"""
Tests for the named tile joins in ``lib_advanced_metrics``.

Tier-1 unit tests over synthetic frames for the 2026-09-12 fix to the
name-versus-geometry defect in the tile confusion matrix behind tile-level
Matthews Correlation Coefficient (MCC). They cover the four things that
had to be got right:

1. **Two tile vocabularies.** A detection set produced on one grid,
   scored against an offset grid, is the failure the defect was found by.
   The ``id`` join books nothing and must be refused; the geometric joins
   book every point and give the right confusion.
2. **The shared-edge rule.** A point lying exactly on the boundary between
   two tiles is a candidate for both; ``geometric-primary`` resolves it to
   exactly one deterministically, ``geometric-contains`` books it to both.
3. **The no-tile rule.** A point inside no tile is excluded from the
   confusion and counted, never silently dropped and never booked.
4. **The invariant.** A shortfall between points booked and points
   geometrically inside the frame refuses the confusion with a named
   reason instead of returning a number.
"""

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from scripts.lib_advanced_metrics import (
    TILE_JOIN_GEOMETRIC_CONTAINS,
    TILE_JOIN_GEOMETRIC_PRIMARY,
    TILE_JOIN_ID,
    TILE_JOIN_REASON_DETECTION_SHORTFALL,
    TILE_JOIN_REASON_NO_SOURCE_TILE,
    TILE_JOINS,
    assign_points_to_tiles,
    calculate_tile_classification,
    check_tile_join_invariant,
    compute_per_tile_tp_fp_fn,
)

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"
ORIGIN_X = 500000.0
ORIGIN_Y = 4700000.0
TILE = 100.0


def _grid(n_tiles: int, offset: float = 0.0, prefix: str = "f") -> gpd.GeoDataFrame:
    """
    Build a row of ``n_tiles`` square, non-overlapping tiles.

    Args:
        n_tiles: How many tiles to lay out along x.
        offset: Shift of the whole grid along x, in metres. A non-zero
            offset produces a second tile vocabulary covering (mostly) the
            same ground — the situation the defect was found in.
        prefix: Name prefix, so two grids are distinguishable by name.

    Returns:
        GeoDataFrame with ``tile_name`` and ``geometry``.
    """
    names = []
    geometries = []
    for i in range(n_tiles):
        x0 = ORIGIN_X + offset + i * TILE
        names.append(f"{prefix}_x{int(x0 - ORIGIN_X)}_y0.png")
        geometries.append(box(x0, ORIGIN_Y, x0 + TILE, ORIGIN_Y + TILE))
    return gpd.GeoDataFrame(
        {"tile_name": names}, geometry=geometries, crs=CRS,
    )


def _overlapping_grid(n_tiles: int, stride: float = 80.0) -> gpd.GeoDataFrame:
    """
    Build a row of tiles that overlap, as the project's real frames do.

    Args:
        n_tiles: How many tiles to lay out along x.
        stride: Distance between successive tile origins; less than
            ``TILE`` makes neighbours overlap.

    Returns:
        GeoDataFrame with ``tile_name`` and ``geometry``.
    """
    names = []
    geometries = []
    for i in range(n_tiles):
        x0 = ORIGIN_X + i * stride
        names.append(f"o_x{int(i * stride)}_y0.png")
        geometries.append(box(x0, ORIGIN_Y, x0 + TILE, ORIGIN_Y + TILE))
    return gpd.GeoDataFrame(
        {"tile_name": names}, geometry=geometries, crs=CRS,
    )


def _points(
    coords: list[tuple[float, float]],
    source_tiles: list[str] | None = None,
    with_map: bool = False,
) -> gpd.GeoDataFrame:
    """
    Build a point GeoDataFrame, optionally carrying ``source_tile``.

    Args:
        coords: (x, y) pairs.
        source_tiles: Recorded tile name per point, for the ``id`` join.
        with_map: Add a ``Map`` column, needed by the per-tile TP/FP/FN
            table's per-map scoping.

    Returns:
        GeoDataFrame of points in :data:`CRS`.
    """
    data: dict[str, list] = {}
    if source_tiles is not None:
        data["source_tile"] = source_tiles
    if with_map:
        data["Map"] = ["f"] * len(coords)
    return gpd.GeoDataFrame(
        data or {"dummy": [0] * len(coords)},
        geometry=[Point(x, y) for x, y in coords],
        crs=CRS,
    )


# --------------------------------------------------------------------------
# 1. Two tile vocabularies: the string join mismatches, geometry does not
# --------------------------------------------------------------------------

def test_offset_grids_string_join_books_nothing():
    """A detection set named on one grid books nothing against another."""
    frame = _grid(4, offset=0.0, prefix="frame")
    proposer = _grid(4, offset=50.0, prefix="proposer")

    # Points at the centre of each frame tile, but labelled with the
    # proposer grid's names — every one of which is absent from the frame.
    coords = [(ORIGIN_X + 50 + i * TILE, ORIGIN_Y + 50) for i in range(4)]
    dets = _points(coords, source_tiles=list(proposer["tile_name"]))

    booked = assign_points_to_tiles(dets, frame, TILE_JOIN_ID)
    assert booked["n_assigned"] == 0
    assert booked["n_inside_union"] == 4, "all four points are inside the frame"

    for join in (TILE_JOIN_GEOMETRIC_PRIMARY, TILE_JOIN_GEOMETRIC_CONTAINS):
        booked = assign_points_to_tiles(dets, frame, join)
        assert booked["n_assigned"] == 4, join
        assert booked["tiles_with_point"] == set(frame["tile_name"]), join


def test_offset_grids_geometric_join_gives_the_right_confusion():
    """The geometric joins recover the confusion the string join loses."""
    frame = _grid(4, offset=0.0, prefix="frame")
    proposer = _grid(4, offset=50.0, prefix="proposer")

    # A reference and a detection in tiles 0 and 1; tiles 2 and 3 empty of
    # both. Truth: tp 2, tn 2, fp 0, fn 0.
    coords = [(ORIGIN_X + 50, ORIGIN_Y + 50), (ORIGIN_X + 150, ORIGIN_Y + 50)]
    dets = _points(coords, source_tiles=list(proposer["tile_name"])[:2])
    refs = _points(coords)

    legacy = calculate_tile_classification(
        dets, refs, frame, tile_join=TILE_JOIN_ID,
    )
    assert "error" in legacy, "the string join must be refused, not reported"

    for join in (TILE_JOIN_GEOMETRIC_PRIMARY, TILE_JOIN_GEOMETRIC_CONTAINS):
        result = calculate_tile_classification(dets, refs, frame, tile_join=join)
        assert "error" not in result, join
        assert (result["tp"], result["tn"], result["fp"], result["fn"]) == \
            (2, 2, 0, 0), join
        assert result["mcc"] == pytest.approx(1.0), join


def test_string_join_reproduces_geometry_when_vocabularies_agree():
    """On a matched, non-overlapping frame all three joins coincide."""
    frame = _grid(4, offset=0.0, prefix="frame")
    coords = [(ORIGIN_X + 50, ORIGIN_Y + 50), (ORIGIN_X + 150, ORIGIN_Y + 50)]
    names = list(frame["tile_name"])[:2]
    dets = _points(coords, source_tiles=names)
    refs = _points(coords)

    results = {
        join: calculate_tile_classification(dets, refs, frame, tile_join=join)
        for join in TILE_JOINS
    }
    confusions = {
        join: (r["tp"], r["tn"], r["fp"], r["fn"])
        for join, r in results.items()
    }
    assert len(set(confusions.values())) == 1, confusions


def test_overlapping_frame_makes_the_joins_disagree():
    """On an overlapping frame the joins are genuinely different metrics.

    This is why the geometric join could not simply be made the default:
    the project's real frames overlap (384 px tiles on a 336 px stride),
    so switching rules moves published numbers even where the vocabulary
    matches.
    """
    frame = _overlapping_grid(4, stride=80.0)
    # A point at x=590000+... inside the overlap of two tiles.
    overlap_x = ORIGIN_X + 95.0
    coords = [(overlap_x, ORIGIN_Y + 50)]
    dets = _points(coords, source_tiles=[frame["tile_name"].iloc[0]])

    by_id = assign_points_to_tiles(dets, frame, TILE_JOIN_ID)
    by_primary = assign_points_to_tiles(
        dets, frame, TILE_JOIN_GEOMETRIC_PRIMARY,
    )
    by_contains = assign_points_to_tiles(
        dets, frame, TILE_JOIN_GEOMETRIC_CONTAINS,
    )

    assert by_id["n_multi_tile"] == 1, "the point is inside two tiles"
    assert len(by_id["tiles_with_point"]) == 1
    assert len(by_primary["tiles_with_point"]) == 1
    assert len(by_contains["tiles_with_point"]) == 2, (
        "contains books the point to both tiles that hold it"
    )
    # The primary rule picks the nearer centroid, which is the SECOND
    # tile (centroid x = origin+130) rather than the recorded first one
    # (centroid x = origin+50) — so id and geometric-primary disagree.
    assert by_primary["tiles_with_point"] != by_id["tiles_with_point"]


# --------------------------------------------------------------------------
# 2. The shared-edge rule
# --------------------------------------------------------------------------

def test_edge_point_is_a_candidate_for_both_neighbours():
    """A point on a shared edge intersects both tiles, and is booked once."""
    frame = _grid(2, offset=0.0, prefix="frame")
    edge_x = ORIGIN_X + TILE  # exactly the boundary between tile 0 and 1
    dets = _points([(edge_x, ORIGIN_Y + 50)])

    contains = assign_points_to_tiles(
        dets, frame, TILE_JOIN_GEOMETRIC_CONTAINS,
    )
    assert contains["n_multi_tile"] == 1
    assert contains["tiles_with_point"] == set(frame["tile_name"]), (
        "an edge point is held by both neighbours under contains"
    )

    primary = assign_points_to_tiles(
        dets, frame, TILE_JOIN_GEOMETRIC_PRIMARY,
    )
    assert len(primary["tiles_with_point"]) == 1, (
        "primary books an edge point to exactly one tile"
    )
    assert sum(primary["counts"].values()) == 1


def test_edge_point_tie_break_is_deterministic_and_lexicographic():
    """Equidistant centroids resolve to the lexicographically first name."""
    frame = _grid(2, offset=0.0, prefix="frame")
    edge_x = ORIGIN_X + TILE
    # The edge point is exactly equidistant from both tile centroids.
    dets = _points([(edge_x, ORIGIN_Y + 50)])

    names = sorted(frame["tile_name"])
    for _ in range(5):
        primary = assign_points_to_tiles(
            dets, frame, TILE_JOIN_GEOMETRIC_PRIMARY,
        )
        assert primary["tiles_with_point"] == {names[0]}, (
            "the tie must resolve the same way every time"
        )


# --------------------------------------------------------------------------
# 3. The no-tile rule
# --------------------------------------------------------------------------

def test_point_in_no_tile_is_excluded_and_counted():
    """A point outside every tile is booked nowhere and reported."""
    frame = _grid(2, offset=0.0, prefix="frame")
    inside = (ORIGIN_X + 50, ORIGIN_Y + 50)
    outside = (ORIGIN_X + 10_000, ORIGIN_Y + 10_000)
    dets = _points([inside, outside])

    for join in (TILE_JOIN_GEOMETRIC_PRIMARY, TILE_JOIN_GEOMETRIC_CONTAINS):
        booked = assign_points_to_tiles(dets, frame, join)
        assert booked["n_points"] == 2, join
        assert booked["n_inside_union"] == 1, join
        assert booked["n_outside_union"] == 1, join
        assert booked["n_assigned"] == 1, join
        assert sum(booked["counts"].values()) == 1, join


def test_out_of_frame_points_do_not_trip_the_invariant():
    """Excluding an out-of-frame point is correct, not a shortfall."""
    frame = _grid(2, offset=0.0, prefix="frame")
    inside = (ORIGIN_X + 50, ORIGIN_Y + 50)
    outside = (ORIGIN_X + 10_000, ORIGIN_Y + 10_000)
    dets = _points([inside, outside], source_tiles=[
        frame["tile_name"].iloc[0], "somewhere_else.png",
    ])
    refs = _points([inside])

    result = calculate_tile_classification(
        dets, refs, frame, tile_join=TILE_JOIN_ID,
    )
    assert "error" not in result, (
        "the only unbooked detection is outside the frame, which is the "
        "documented exclusion rather than a lost point"
    )
    diagnostics = result["tile_join_diagnostics"]["detections"]
    assert diagnostics["n_outside_union"] == 1
    assert diagnostics["n_assigned"] == diagnostics["n_inside_union"] == 1


# --------------------------------------------------------------------------
# 4. The invariant
# --------------------------------------------------------------------------

def test_invariant_fires_on_a_detection_shortfall():
    """One in-frame detection booked nowhere is enough to refuse the MCC."""
    frame = _grid(3, offset=0.0, prefix="frame")
    coords = [
        (ORIGIN_X + 50, ORIGIN_Y + 50),
        (ORIGIN_X + 150, ORIGIN_Y + 50),
    ]
    dets = _points(coords, source_tiles=[
        frame["tile_name"].iloc[0], "not_a_frame_tile.png",
    ])
    refs = _points(coords)

    result = calculate_tile_classification(
        dets, refs, frame, tile_join=TILE_JOIN_ID,
    )
    assert "error" in result
    assert result["reason"] == TILE_JOIN_REASON_DETECTION_SHORTFALL
    assert "mcc" not in result, "no number may be emitted alongside a refusal"
    assert "1 of 2" in result["error"]


def test_invariant_names_the_missing_source_tile_column():
    """The ``id`` join over detections with no ``source_tile`` is refused."""
    frame = _grid(2, offset=0.0, prefix="frame")
    coords = [(ORIGIN_X + 50, ORIGIN_Y + 50)]
    dets = _points(coords)  # no source_tile column at all
    refs = _points(coords)

    result = calculate_tile_classification(
        dets, refs, frame, tile_join=TILE_JOIN_ID,
    )
    assert "error" in result
    assert result["reason"] == TILE_JOIN_REASON_NO_SOURCE_TILE


def test_invariant_passes_when_every_in_frame_point_is_booked():
    """The happy path returns numbers and records the join that made them."""
    frame = _grid(3, offset=0.0, prefix="frame")
    coords = [
        (ORIGIN_X + 50, ORIGIN_Y + 50),
        (ORIGIN_X + 150, ORIGIN_Y + 50),
    ]
    dets = _points(coords, source_tiles=list(frame["tile_name"])[:2])
    refs = _points(coords)

    result = calculate_tile_classification(
        dets, refs, frame, tile_join=TILE_JOIN_ID,
    )
    assert "error" not in result
    assert result["tile_join"] == TILE_JOIN_ID
    assert result["tile_join_diagnostics"]["reference_join"] == \
        TILE_JOIN_GEOMETRIC_CONTAINS, (
            "the legacy pairing keeps the geometric reference rule"
        )


def test_check_tile_join_invariant_is_directly_callable():
    """The invariant is a function of two assignments, testable on its own."""
    frame = _grid(2, offset=0.0, prefix="frame")
    coords = [(ORIGIN_X + 50, ORIGIN_Y + 50)]
    good = assign_points_to_tiles(
        _points(coords, source_tiles=[frame["tile_name"].iloc[0]]),
        frame, TILE_JOIN_ID,
    )
    bad = assign_points_to_tiles(
        _points(coords, source_tiles=["elsewhere.png"]), frame, TILE_JOIN_ID,
    )
    refs = assign_points_to_tiles(
        _points(coords), frame, TILE_JOIN_GEOMETRIC_CONTAINS,
    )

    assert check_tile_join_invariant(good, refs) is None
    refusal = check_tile_join_invariant(bad, refs)
    assert refusal is not None
    assert refusal["reason"] == TILE_JOIN_REASON_DETECTION_SHORTFALL


def test_per_tile_table_raises_on_the_same_shortfall():
    """The TP/FP/FN table the bootstrap resamples enforces the invariant too.

    This arm of the defect is wider than MCC: under the string join a
    vocabulary-mismatched cell loses every TP and FP and leaves a table of
    pure false negatives, which the per-tile bootstrap confidence
    intervals and the pairwise permutation tests would then resample.
    """
    frame = _grid(3, offset=0.0, prefix="f")
    coords = [
        (ORIGIN_X + 50, ORIGIN_Y + 50),
        (ORIGIN_X + 150, ORIGIN_Y + 50),
    ]
    refs = _points(coords, with_map=True)
    dets = _points(
        coords, source_tiles=["f_x0_y0.png", "f_x9999_y0.png"],
        with_map=True,
    )

    with pytest.raises(ValueError, match="per-tile TP/FP/FN table refused"):
        compute_per_tile_tp_fp_fn(
            dets, refs, frame, buffer_metres=20, tile_join=TILE_JOIN_ID,
        )

    # The geometric join books both detections and produces a table.
    table = compute_per_tile_tp_fp_fn(
        dets, refs, frame, buffer_metres=20,
        tile_join=TILE_JOIN_GEOMETRIC_PRIMARY,
    )
    assert int(table["tp"].sum()) == 2


def test_unknown_tile_join_is_rejected():
    """A typo in the rule name must fail loudly, not fall back silently."""
    frame = _grid(2, offset=0.0, prefix="frame")
    dets = _points([(ORIGIN_X + 50, ORIGIN_Y + 50)])
    with pytest.raises(ValueError, match="tile_join must be one of"):
        assign_points_to_tiles(dets, frame, "geometrical")
