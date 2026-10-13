"""The H13 chain's clusters carry their contributing tiles into scoring.

PI ruling D62 (1), 2026-10-13 (``planning/pi-decisions-2026-09-20.md``):
the H13 chain built bare cluster centroids
(``h13_k_sensitivity.cluster_votes``; ``h13_aggregation_sweep.write_cell``
dropped the ``source_tiles`` of ``cluster_across_passes``) and tiled them
with ``prepare_h13_scoring.assign_primary_tiles`` with no origin, so the
D50 never-re-key rule fell back to the legacy rule: the nearest tile
centroid among ALL frame tiles. Where two sheets' padded tiles overlap, a
centroid seen only on sheet A but nearer sheet B's tile centre was booked
to B and matched against B's references
(``reports/frames-blast-radius-2026-10-07.md`` § 5.4).

These tests pin the fix on synthetic two-sheet fixtures in which the
location rule and the origin rule disagree:

* ``cluster_votes_with_origins`` clusters exactly as ``cluster_votes``
  (which other chains import unchanged) and returns each cluster's
  contributing tiles;
* ``h13_k_sensitivity.score`` with origins scores a cluster on its own
  sheet, and leaves out one that lies on no tile of its own sheet;
* ``h13_aggregation_sweep.write_cell`` tiles each cluster on its own
  sheet, records ``origin_tiles`` in the frame and in the file, and the
  file read back scores as the frame does.

Usage:
    python -m pytest tests/test_h13_origin_route.py -q
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.h13_aggregation_sweep import cluster_origin, write_cell  # noqa: E402
from scripts.h13_k_sensitivity import (  # noqa: E402
    cluster_votes,
    cluster_votes_with_origins,
    score,
)
from scripts.lib_advanced_metrics import calculate_f1_internal  # noqa: E402

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"

# Two sheets whose padded tiles overlap by 100 m along x, in the study
# area's UTM zone. Sheet B's tile is listed first, so neither a join order
# nor a "first intersecting tile" rule can favour sheet A by accident.
_X0, _Y0 = 397_000.0, 4_705_000.0
SHEET_A = "K-35-001-1_32635"
SHEET_B = "K-35-001-2_32635"
TILE_A = f"{SHEET_A}_x0_y0.png"
TILE_B = f"{SHEET_B}_x0_y0.png"

# A point inside both tiles and nearer sheet B's tile centre (440 m) than
# sheet A's (460 m): the legacy rule books it to B.
_OVERLAP_PT = (_X0 + 960.0, _Y0 + 500.0)
# A point inside sheet A's tile only.
_A_ONLY_PT = (_X0 + 300.0, _Y0 + 500.0)


def _bounds() -> gpd.GeoDataFrame:
    """Two overlapping frame tiles on two sheets (sheet B listed first).

    Returns:
        A two-row bounds GeoDataFrame with a ``tile_name`` column.
    """
    return gpd.GeoDataFrame(
        {"tile_name": [TILE_B, TILE_A]},
        geometry=[
            box(_X0 + 900, _Y0, _X0 + 1900, _Y0 + 1000),
            box(_X0, _Y0, _X0 + 1000, _Y0 + 1000),
        ],
        crs=CRS,
    )


def _reference(sheet: str, xy: tuple[float, float]) -> gpd.GeoDataFrame:
    """One reference mound on ``sheet`` at ``xy``.

    Args:
        sheet: The sheet name recorded in the ``Map`` column.
        xy: Easting and northing.

    Returns:
        A one-row reference GeoDataFrame.
    """
    return gpd.GeoDataFrame(
        {"Map": [sheet], "Symbol": ["burial_mound"]},
        geometry=[Point(xy)],
        crs=CRS,
    )


def _det(xy: tuple[float, float], tiles: list[str], size: int = 1) -> dict:
    """One deduplicated detection as ``deduplicate_within_pass`` returns it.

    Args:
        xy: Centroid.
        tiles: The proposer tiles its members were seen on.
        size: Within-pass ``cluster_size``.

    Returns:
        A detection dict.
    """
    return {
        "centroid": xy, "label": "burial_mound",
        "source_tiles": list(tiles), "cluster_size": size,
    }


def _cluster(xy: tuple[float, float], tiles: list[str], votes: int = 3) -> dict:
    """One cluster as ``merge_passes.cluster_across_passes`` returns it.

    Args:
        xy: Centroid.
        tiles: Contributing tiles (``source_tiles``).
        votes: Vote count.

    Returns:
        A cluster dict accepted by ``write_cell``.
    """
    return {
        "centroid": xy, "label": "burial_mound", "vote_count": votes,
        "contributing_passes": [f"run_{i}" for i in range(1, votes + 1)],
        "source_tiles": list(tiles), "cluster_size": votes,
    }


# --------------------------------------------------------------------------
# cluster_votes_with_origins
# --------------------------------------------------------------------------


def test_cluster_votes_with_origins_matches_cluster_votes():
    """Centroids and votes are cluster_votes's exactly, at every corroboration."""
    rng = np.random.default_rng(20261013)
    passes = []
    for p in range(5):
        dets = []
        for i in range(120):
            # Points on a coarse grid with jitter, so many fall within 20 m
            # of a point in another pass and clusters of several form.
            gx, gy = rng.integers(0, 15, size=2)
            xy = (
                float(_X0 + 30.0 * gx + rng.normal(0, 6)),
                float(_Y0 + 30.0 * gy + rng.normal(0, 6)),
            )
            dets.append(_det(xy, [f"{SHEET_A}_x{p}_y{i}.png"], int(rng.integers(1, 4))))
        passes.append(dets)
    for c in (1, 2, 3):
        cents_old, votes_old = cluster_votes(passes, c)
        cents_new, votes_new, origins = cluster_votes_with_origins(passes, c)
        assert np.array_equal(cents_old, cents_new)
        assert np.array_equal(votes_old, votes_new)
        assert len(origins) == len(votes_new)
        # Every cluster records at least one member tile, and at least as
        # many distinct tiles as it has votes (one tile per pass here).
        assert all(len(o) >= v for o, v in zip(origins, votes_new.tolist()))


def test_cluster_votes_with_origins_unions_member_tiles():
    """Each cluster's origin is the sorted union of its members' tiles."""
    passes = [
        [_det(_OVERLAP_PT, [TILE_A]), _det(_A_ONLY_PT, [TILE_A], 2)],
        [_det((_OVERLAP_PT[0] + 5.0, _OVERLAP_PT[1]), [TILE_B, TILE_A])],
        # A raw-style detection with a single source_tile and an empty
        # source_tiles record ("".split(";") leaves [""]).
        [{"centroid": (_OVERLAP_PT[0], _OVERLAP_PT[1] + 5.0), "label": "m",
          "source_tiles": [""], "source_tile": TILE_A}],
    ]
    cents, votes, origins = cluster_votes_with_origins(passes, 1)
    assert votes.tolist() == [3, 1]
    assert origins == [[TILE_A, TILE_B], [TILE_A]]
    # The corroboration filter applies to members before clustering.
    _, votes2, origins2 = cluster_votes_with_origins(passes, 2)
    assert votes2.tolist() == [1]
    assert origins2 == [[TILE_A]]
    # Empty input gives three empty results.
    c0, v0, o0 = cluster_votes_with_origins([[], []], 1)
    assert c0.shape == (0, 2) and v0.size == 0 and o0 == []


# --------------------------------------------------------------------------
# h13_k_sensitivity.score
# --------------------------------------------------------------------------


def test_score_with_origins_keeps_cluster_on_its_sheet():
    """A cluster seen on sheet A, nearer B's tile centre, is matched on A."""
    bounds = _bounds()
    ref = _reference(SHEET_A, _OVERLAP_PT)
    cents = np.asarray([_OVERLAP_PT])
    votes = np.asarray([3])
    # The legacy route (no origins) books it to sheet B: one FP, one FN.
    assert score(cents, votes, 1, bounds, ref) == (0.0, 0.0, 0.0, 1)
    # The origin route scores it on sheet A: a true positive.
    p, r, f1, n = score(cents, votes, 1, bounds, ref, origins=[[TILE_A]])
    assert (p, r, f1, n) == (1.0, 1.0, 1.0, 1)


def test_score_with_origins_leaves_out_a_cluster_off_its_sheet():
    """A cluster seen only on sheet B, lying on sheet A's tiles only, is out of frame."""
    bounds = _bounds()
    ref = _reference(SHEET_A, _A_ONLY_PT)
    cents = np.asarray([_A_ONLY_PT])
    votes = np.asarray([2])
    # Legacy: the only tile holding it is A's, so it is a true positive.
    assert score(cents, votes, 1, bounds, ref)[2] == 1.0
    # Origin rule (D50): it intersects no tile of its own sheet.
    assert score(cents, votes, 1, bounds, ref, origins=[[TILE_B]]) == (0.0, 0.0, 0.0, 0)


def test_score_selects_origins_with_the_vote_threshold():
    """Origins are subset with the clusters the vote threshold keeps."""
    bounds = _bounds()
    ref = _reference(SHEET_A, _OVERLAP_PT)
    cents = np.asarray([_A_ONLY_PT, _OVERLAP_PT])
    votes = np.asarray([1, 3])
    # At k >= 2 only the overlap cluster survives, with ITS origin (A).
    p, r, f1, n = score(cents, votes, 2, bounds, ref, origins=[[TILE_B], [TILE_A]])
    assert (f1, n) == (1.0, 1)
    with pytest.raises(ValueError, match="origins has 1 entries for 2 clusters"):
        score(cents, votes, 1, bounds, ref, origins=[[TILE_A]])


# --------------------------------------------------------------------------
# h13_aggregation_sweep.write_cell and cluster_origin
# --------------------------------------------------------------------------


def test_cluster_origin_drops_empty_names():
    """An empty member record contributes no origin name."""
    assert cluster_origin({"source_tiles": ["", TILE_B, TILE_A, TILE_A]}) == [TILE_A, TILE_B]
    assert cluster_origin({"source_tiles": [""]}) == []
    assert cluster_origin({}) == []


def test_write_cell_tiles_on_origin_sheet_and_records_origin(tmp_path):
    """The cell is tiled on the origin sheet, in memory and in its file alike."""
    bounds = _bounds()
    ref = _reference(SHEET_A, _OVERLAP_PT)
    target = tmp_path / "cell.geojson"
    gdf = write_cell([_cluster(_OVERLAP_PT, ["", TILE_A])], bounds, target)

    assert gdf["source_tile"].tolist() == [TILE_A]
    assert gdf["origin_tiles"].tolist() == [TILE_A]
    assert calculate_f1_internal(gdf, ref, bounds, buffer_metres=20) == (1.0, 1.0, 1.0)

    written = json.loads(target.read_text())
    props = written["features"][0]["properties"]
    assert props["source_tile"] == TILE_A
    assert props["origin_tiles"] == TILE_A
    reread = gpd.read_file(target)
    assert calculate_f1_internal(reread, ref, bounds, buffer_metres=20) == (1.0, 1.0, 1.0)


def test_write_cell_null_tile_for_a_cluster_off_its_sheet(tmp_path):
    """A cluster with no tile on its own sheet is written with a null tile and not scored."""
    bounds = _bounds()
    ref = _reference(SHEET_A, _A_ONLY_PT)
    gdf = write_cell([_cluster(_A_ONLY_PT, [TILE_B])], bounds, tmp_path / "c.geojson")
    assert gdf["source_tile"].tolist() == [None]
    # Out of frame for its own sheet: no detection is scored, the A
    # reference is a false negative.
    assert calculate_f1_internal(gdf, ref, bounds, buffer_metres=20) == (0.0, 0.0, 0.0)


def test_write_cell_empty(tmp_path):
    """An empty cell keeps the origin column and writes no features."""
    gdf = write_cell([], _bounds(), tmp_path / "e.geojson")
    assert gdf.empty
    assert "origin_tiles" in gdf.columns
    assert json.loads((tmp_path / "e.geojson").read_text())["features"] == []
