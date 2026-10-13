"""The consensus library copies keep each detection's contributing tiles.

PI ruling D62 (1), 2026-10-13 (``planning/pi-decisions-2026-09-20.md``):
the fix D60 (3) made to ``analyse_consensus_sweep.consensus_to_gdf`` and
``evaluate_pv_results.build_candidate_gdf`` (keep ``source_tiles``) is
carried to the other copies of those builders:

* ``lib_consensus.generate_consensus_gdf`` wrote the alphabetically first
  member into ``source_tile`` and dropped the member list, so a cluster
  seen on two sheets and lying on the second sheet's tiles only was
  dropped as out of frame for the first;
* ``lib_consensus.build_pv_gdf`` dropped each candidate's
  ``properties.source_tiles`` the same way;
* ``analyse_diversity.consensus_to_gdf`` (a copy of the D60 (3) function)
  chose ``source_tile`` by location and dropped the list, so a detection
  in the overlap of two sheets' padded tiles could be scored on the sheet
  it was never seen on.

Each test below fails on the pre-fix code (the list is missing, and the
scorer gives the location answer) and passes on the fix. Synthetic
two-sheet fixtures only.

Usage:
    python -m pytest tests/test_library_copies_origins.py -q
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Package-free imports, as the scripts import one another, so the scorer
# module the builders call is the module these tests call.
import analyse_diversity as ad  # noqa: E402
import lib_advanced_metrics as lam  # noqa: E402
import lib_consensus as lc  # noqa: E402
from merge_passes import apply_threshold  # noqa: E402

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"

# Two sheets whose padded tiles overlap by 100 m along x (sheet B listed
# first in the bounds), in the study area's UTM zone.
_X0, _Y0 = 397_000.0, 4_705_000.0
SHEET_A = "K-35-001-1_32635"
SHEET_B = "K-35-001-2_32635"
TILE_A = f"{SHEET_A}_x0_y0.png"
TILE_B = f"{SHEET_B}_x0_y0.png"

# Members of a two-sheet cluster: one reported on A's tile (inside it),
# one on B's tile; their mean (x0 + 1003) lies on B's tile only, east of
# A's tile edge at x0 + 1000. They are 18 m apart, within the 20 m radius.
_MEMBER_A = (_X0 + 994.0, _Y0 + 500.0)
_MEMBER_B = (_X0 + 1012.0, _Y0 + 500.0)
_MEAN_AB = (_X0 + 1003.0, _Y0 + 500.0)
# A point in the overlap of both tiles, nearer B's centre than A's.
_OVERLAP_PT = (_X0 + 960.0, _Y0 + 500.0)


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


def _write_pass(run_dir: Path, n: int, xy: tuple[float, float], tile: str) -> None:
    """Write a one-detection pass file under the Batch API naming convention.

    Args:
        run_dir: The ``run_<N>`` directory to create.
        n: Run number, for the file name.
        xy: The detection's position (EPSG:32635).
        tile: Its proposer tile.
    """
    run_dir.mkdir(parents=True)
    (run_dir / f"detections_test_run{n:02d}.geojson").write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(xy)},
            "properties": {"source_tile": tile, "subtype": "burial_mound"},
        }],
    }))


# --------------------------------------------------------------------------
# lib_consensus.generate_consensus_gdf
# --------------------------------------------------------------------------


def test_generate_consensus_gdf_keeps_member_tiles(tmp_path):
    """The cluster keeps both members' tiles; source_tile stays the first."""
    _write_pass(tmp_path / "pool" / "run_1", 1, _MEMBER_A, TILE_A)
    _write_pass(tmp_path / "pool" / "run_2", 2, _MEMBER_B, TILE_B)
    gdf = lc.generate_consensus_gdf(
        [tmp_path / "pool" / "run_1", tmp_path / "pool" / "run_2"], 2)
    assert len(gdf) == 1
    assert gdf["source_tile"].tolist() == [TILE_A]
    assert gdf["source_tiles"].tolist() == [[TILE_A, TILE_B]]


def test_generate_consensus_gdf_cluster_is_scored_where_it_lies(tmp_path):
    """Seen on both sheets, lying on B's tile only: scored on B, not dropped."""
    _write_pass(tmp_path / "pool" / "run_1", 1, _MEMBER_A, TILE_A)
    _write_pass(tmp_path / "pool" / "run_2", 2, _MEMBER_B, TILE_B)
    gdf = lc.generate_consensus_gdf(
        [tmp_path / "pool" / "run_1", tmp_path / "pool" / "run_2"], 2)
    ref = _reference(SHEET_B, _MEAN_AB)
    scope = lam.scope_detections_to_frame(gdf, _bounds())
    assert scope.diagnostics["n_origin_switched"] == 1
    assert scope.diagnostics["n_out_of_frame"] == 0
    assert lam.calculate_f1_internal(gdf, ref, _bounds(), buffer_metres=20) == (1.0, 1.0, 1.0)


def test_generate_consensus_gdf_empty_has_origin_column(tmp_path):
    """No pass files: an empty frame that still names the origin column."""
    (tmp_path / "run_1").mkdir()
    gdf = lc.generate_consensus_gdf([tmp_path / "run_1"], 1)
    assert gdf.empty
    assert "source_tiles" in gdf.columns


# --------------------------------------------------------------------------
# lib_consensus.build_pv_gdf
# --------------------------------------------------------------------------


def _pv_dirs(tmp_path: Path, candidates: list[dict], probs: dict) -> tuple[Path, Path, Path]:
    """Write a minimal PV results, manifest, and sweep trio.

    Args:
        tmp_path: Root directory.
        candidates: Manifest ``candidates`` entries.
        probs: ``probabilities.json`` ``results`` mapping.

    Returns:
        ``(pv_results_dir, manifest_dir, sweep_dir)``.
    """
    pv, man, sw = tmp_path / "pv", tmp_path / "manifest", tmp_path / "sweep"
    for d in (pv, man, sw):
        d.mkdir()
    (sw / "threshold_sweep.json").write_text(json.dumps({"optimal": {"threshold": 0.5}}))
    (pv / "probabilities.json").write_text(json.dumps({"results": probs}))
    (man / "candidate_manifest.json").write_text(json.dumps({"candidates": candidates}))
    return pv, man, sw


def test_build_pv_gdf_keeps_candidate_tiles(tmp_path):
    """A union candidate keeps its member list; a bare one gets an empty list."""
    pv, man, sw = _pv_dirs(
        tmp_path,
        [
            {"candidate_id": 0, "centroid_x": _MEAN_AB[0], "centroid_y": _MEAN_AB[1],
             "source_tile": TILE_A, "properties": {"source_tiles": [TILE_A, TILE_B]}},
            {"candidate_id": 1, "centroid_x": _X0 + 300.0, "centroid_y": _Y0 + 500.0,
             "source_tile": TILE_A},
        ],
        {"candidate_00000": {"mound_probability": 0.9},
         "candidate_00001": {"mound_probability": 0.8}},
    )
    gdf = lc.build_pv_gdf(pv, man, sw)
    assert gdf["source_tiles"].tolist() == [[TILE_A, TILE_B], []]
    ref = _reference(SHEET_B, _MEAN_AB)
    # The union candidate is switched to B and matched; the bare one is an
    # A-sheet false positive, exactly as before the fix.
    p, r, f1 = lam.calculate_f1_internal(gdf, ref, _bounds(), buffer_metres=20)
    assert (p, r) == (0.5, 1.0)


def test_build_pv_gdf_empty_has_origin_column(tmp_path):
    """Nothing above threshold: an empty frame that names the origin column."""
    pv, man, sw = _pv_dirs(
        tmp_path,
        [{"candidate_id": 0, "centroid_x": _MEAN_AB[0], "centroid_y": _MEAN_AB[1],
          "source_tile": TILE_A}],
        {"candidate_00000": {"mound_probability": 0.1}},
    )
    gdf = lc.build_pv_gdf(pv, man, sw)
    assert gdf.empty
    assert "source_tiles" in gdf.columns


# --------------------------------------------------------------------------
# analyse_diversity.consensus_to_gdf
# --------------------------------------------------------------------------


def _cluster(xy: tuple[float, float], tiles: list[str]) -> dict:
    """A cluster as ``merge_passes.cluster_across_passes`` returns it.

    Args:
        xy: Centroid (EPSG:32635).
        tiles: Contributing tiles.

    Returns:
        A cluster dict accepted by ``apply_threshold``.
    """
    return {
        "centroid": xy, "label": "burial_mound", "vote_count": 3,
        "contributing_passes": ["run_1", "run_2", "run_3"],
        "source_tiles": list(tiles), "cluster_size": 3,
    }


def test_diversity_consensus_to_gdf_keeps_member_tiles():
    """The diversity copy keeps the origin list, one list per row."""
    fc = apply_threshold(
        [_cluster(_OVERLAP_PT, [TILE_A]), _cluster(_MEAN_AB, [TILE_A, TILE_B])], 1, 3)
    gdf = ad.consensus_to_gdf(fc, _bounds())
    assert sorted(map(tuple, gdf["source_tiles"].tolist())) == [
        (TILE_A,), (TILE_A, TILE_B)]


def test_diversity_consensus_to_gdf_scores_on_the_origin_sheet():
    """Seen on B only, in the overlap: matched on B whatever tile location picks.

    The location rule (first intersecting tile of a spatial join) picked
    sheet A's tile for this point when the test was written (sapphire,
    geopandas as pinned on 2026-10-13), so the pre-fix route scored it on
    A, a false positive and a false negative; the origin restores it to B.
    """
    fc = apply_threshold([_cluster(_OVERLAP_PT, [TILE_B])], 1, 3)
    gdf = ad.consensus_to_gdf(fc, _bounds())
    ref = _reference(SHEET_B, _OVERLAP_PT)
    # apply_threshold's 4326 round trip moves the point by far less than a
    # millimetre, so the 20 m match is unaffected.
    assert lam.calculate_f1_internal(gdf, ref, _bounds(), buffer_metres=20) == (1.0, 1.0, 1.0)
    scope = lam.scope_detections_to_frame(gdf, _bounds())
    assert scope.diagnostics["origin_columns"] == ["source_tiles"]
