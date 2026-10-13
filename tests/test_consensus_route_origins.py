"""The in-memory consensus and PV routes keep each detection's origin tiles.

PI ruling D60 (3), 2026-10-12 (``planning/pi-decisions-2026-09-20.md``):
``analyse_consensus_sweep.consensus_to_gdf`` dropped each consensus
cluster's contributing-tile list (``source_tiles``) and kept only one
``source_tile`` chosen by location, so the shared scorer
(``lib_advanced_metrics.scope_detections_to_frame``, ruling D50) had no
origin to restore. Every arm built in memory (``run_pairwise_tests.py``
and the other callers of ``consensus_to_gdf``) was therefore scored on the
location rule, while the same set read from its committed GeoJSON was
scored on its origins: H2's 26-of-30 arm read F1 0.814118, the re-scored
cell and H3 0.816471. ``evaluate_pv_results.build_candidate_gdf`` (the
PV loader's builder) dropped the candidates' ``properties.source_tiles``
in the same way.

These tests pin the fix:

* synthetic two-sheet fixtures in which the location rule and the origin
  rule disagree, so each test fails (red) on the pre-fix code and passes
  on the fixed code;
* the committed 26-of-30 consensus set, routed through
  ``consensus_to_gdf`` in memory, must score exactly as the file is
  scored by ``evaluate_detections.py`` (F1 0.816471 at 20 m), where the
  pre-fix route gave 0.814118.

Usage:
    python -m pytest tests/test_consensus_route_origins.py -q
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Package-free imports, as the scripts import one another: the scorer
# module consensus_to_gdf calls is then the module these tests call.
import analyse_consensus_sweep as acs  # noqa: E402
import lib_advanced_metrics as lam  # noqa: E402
from merge_passes import apply_threshold  # noqa: E402
from scripts.evaluate_pv_results import build_candidate_gdf  # noqa: E402

pytestmark = pytest.mark.tier1

TARGET_CRS = "EPSG:32635"

# Two sheets whose padded tiles overlap by 100 m along x, in the study
# area's UTM zone (the same easting/northing range as the real sheets).
_X0, _Y0 = 397_000.0, 4_705_000.0
SHEET_A = "K-35-001-1_32635"
SHEET_B = "K-35-001-2_32635"
TILE_A = f"{SHEET_A}_x0_y0.png"
TILE_B = f"{SHEET_B}_x0_y0.png"

# The committed set and frame of H2's 26-of-30 arm (D60 (3)).
_T26 = (
    PROJECT_ROOT / "outputs" / "h11" / "pv-diag-384" / "flash-high-text-n5"
    / "text-t0.7" / "consensus" / "consensus_t26.geojson"
)
_BOUNDS_384 = (
    PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "384"
    / "full_evaluation_bounds.geojson"
)
_REFERENCE = PROJECT_ROOT / "inputs" / "vectors" / "references" / "mounds-reference.geojson"


def _two_sheet_bounds() -> gpd.GeoDataFrame:
    """Two overlapping frame tiles on two sheets (B listed first).

    Returns:
        A two-row bounds GeoDataFrame with a ``tile_name`` column.
    """
    return gpd.GeoDataFrame(
        {"tile_name": [TILE_B, TILE_A]},
        geometry=[
            box(_X0 + 900, _Y0, _X0 + 1900, _Y0 + 1000),
            box(_X0, _Y0, _X0 + 1000, _Y0 + 1000),
        ],
        crs=TARGET_CRS,
    )


def _reference_on(sheet: str, x: float, y: float) -> gpd.GeoDataFrame:
    """One reference mound on ``sheet`` at (x, y).

    Args:
        sheet: The sheet name recorded in the ``Map`` column.
        x: Easting.
        y: Northing.

    Returns:
        A one-row reference GeoDataFrame.
    """
    return gpd.GeoDataFrame(
        {"Map": [sheet], "Symbol": ["burial_mound"]},
        geometry=[Point(x, y)],
        crs=TARGET_CRS,
    )


def _cluster(x: float, y: float, source_tiles: list[str] | None) -> dict:
    """A cluster dict as ``merge_passes.cluster_across_passes`` builds it.

    Args:
        x: Centroid easting (EPSG:32635).
        y: Centroid northing.
        source_tiles: The members' proposer tiles, or ``None`` to omit
            the key.

    Returns:
        A cluster accepted by ``apply_threshold``.
    """
    cluster = {
        "centroid": (x, y),
        "label": "burial_mound",
        "vote_count": 3,
        "contributing_passes": ["run_1", "run_2", "run_3"],
        "cluster_size": 3,
        "source_tiles": source_tiles if source_tiles is not None else [],
    }
    return cluster


def _location_tile(x: float, y: float, bounds: gpd.GeoDataFrame) -> str:
    """The tile ``consensus_to_gdf`` assigns to a point by location alone.

    Read from the function itself, so the fixtures below do not depend on
    geopandas' ordering of a point's several intersecting tiles.

    Args:
        x: Easting.
        y: Northing.
        bounds: The frame.

    Returns:
        The assigned ``source_tile``.
    """
    fc = apply_threshold([_cluster(x, y, ["placeholder_x0_y0.png"])], 3, 3)
    return str(acs.consensus_to_gdf(fc, bounds)["source_tile"].iloc[0])


class TestConsensusToGdfKeepsOrigins:
    """``consensus_to_gdf`` carries ``source_tiles`` to the scorer."""

    def test_source_tiles_column_is_kept_as_lists(self) -> None:
        """Each row keeps its cluster's contributing tiles, as a list."""
        bounds = _two_sheet_bounds()
        clusters = [
            _cluster(_X0 + 200, _Y0 + 500, [TILE_A]),
            _cluster(_X0 + 950, _Y0 + 500, [TILE_A, TILE_B]),
        ]
        gdf = acs.consensus_to_gdf(apply_threshold(clusters, 3, 3), bounds)
        assert "source_tiles" in gdf.columns
        assert gdf["source_tiles"].tolist() == [[TILE_A], [TILE_A, TILE_B]]
        assert gdf.crs == TARGET_CRS

    def test_missing_record_gives_empty_list(self) -> None:
        """A feature with no ``source_tiles`` gets ``[]`` (no origin)."""
        bounds = _two_sheet_bounds()
        fc = apply_threshold([_cluster(_X0 + 200, _Y0 + 500, None)], 3, 3)
        for feature in fc["features"]:
            del feature["properties"]["source_tiles"]
        gdf = acs.consensus_to_gdf(fc, bounds)
        assert gdf["source_tiles"].tolist() == [[]]
        assert gdf["source_tile"].tolist() == [TILE_A]

    def test_empty_collection_has_the_column(self) -> None:
        """An empty consensus set still advertises ``source_tiles``."""
        gdf = acs.consensus_to_gdf({"features": []}, _two_sheet_bounds())
        assert "source_tiles" in gdf.columns
        assert len(gdf) == 0

    def test_malformed_record_is_refused(self) -> None:
        """A record of a type no producer writes raises, not scored silently."""
        bounds = _two_sheet_bounds()
        fc = apply_threshold([_cluster(_X0 + 200, _Y0 + 500, [TILE_A])], 3, 3)
        fc["features"][0]["properties"]["source_tiles"] = {"tile": TILE_A}
        with pytest.raises(TypeError):
            acs.consensus_to_gdf(fc, bounds)

    def test_origin_sheet_wins_over_location(self) -> None:
        """A cluster seen on one sheet is scored there, wherever the join put it.

        The point lies in the overlap of two sheets' tiles. Whichever tile
        the location rule picks, the cluster's origin is set to the OTHER
        sheet and the reference is put on that sheet: the origin rule
        scores a true positive, the location rule a false positive plus a
        false negative (F1 0). Red on the pre-fix code.
        """
        bounds = _two_sheet_bounds()
        x, y = _X0 + 950, _Y0 + 500
        located = _location_tile(x, y, bounds)
        origin_tile = TILE_A if located == TILE_B else TILE_B
        origin_sheet = lam.get_map_name(origin_tile)
        assert lam.get_map_name(located) != origin_sheet  # the case under test

        fc = apply_threshold([_cluster(x, y, [origin_tile])], 3, 3)
        gdf = acs.consensus_to_gdf(fc, bounds)
        refs = _reference_on(origin_sheet, x + 5, y)

        scope = lam.scope_detections_to_frame(gdf, bounds)
        assert scope.diagnostics["n_origin_restored"] == 1
        assert scope.sheets.tolist() == [origin_sheet]
        precision, recall, f1 = lam.calculate_f1_internal(
            gdf, refs, bounds, buffer_metres=20,
        )
        assert (precision, recall, f1) == (1.0, 1.0, 1.0)

        table = lam.compute_per_tile_tp_fp_fn(gdf, refs, bounds, buffer_metres=20)
        assert (int(table["tp"].sum()), int(table["fp"].sum()),
                int(table["fn"].sum())) == (1, 0, 0)


class TestPvBuilderKeepsOrigins:
    """``build_candidate_gdf`` carries the candidates' ``source_tiles``."""

    @staticmethod
    def _manifest(candidates: list[dict]) -> dict:
        """Wrap candidates as a manifest."""
        return {"candidates": candidates}

    def test_properties_source_tiles_are_kept(self) -> None:
        """The union's member list survives; a bare candidate gets ``[]``."""
        manifest = self._manifest([
            {"candidate_id": 1, "centroid_x": _X0 + 200, "centroid_y": _Y0 + 500,
             "source_tile": TILE_A,
             "properties": {"source_tiles": [TILE_A, TILE_B]}},
            {"candidate_id": 2, "centroid_x": _X0 + 300, "centroid_y": _Y0 + 500,
             "source_tile": TILE_A},
        ])
        probs = {"candidate_00001": {"mound_probability": 0.9},
                 "candidate_00002": {"mound_probability": 0.9}}
        gdf = build_candidate_gdf(manifest, probs, threshold=0.5)
        assert gdf["source_tiles"].tolist() == [[TILE_A, TILE_B], []]
        assert gdf["source_tile"].tolist() == [TILE_A, TILE_A]

    def test_empty_selection_has_the_column(self) -> None:
        """No candidate above threshold still advertises ``source_tiles``."""
        gdf = build_candidate_gdf(self._manifest([]), {}, threshold=0.5)
        assert "source_tiles" in gdf.columns

    def test_two_sheet_candidate_scored_where_it_lies(self) -> None:
        """A candidate seen on two sheets is scored on the one holding it.

        ``extract_candidates.py`` writes the alphabetically first member
        (sheet A) into ``source_tile``; the point lies only in sheet B's
        tile, where the reference is. With the member list the scorer
        switches it to B (a true positive); without it the candidate is
        out of frame for A and dropped, leaving the reference a false
        negative (F1 0). Red on the pre-fix code.
        """
        bounds = _two_sheet_bounds()
        x, y = _X0 + 1500, _Y0 + 500  # inside B's tile only
        manifest = self._manifest([
            {"candidate_id": 7, "centroid_x": x, "centroid_y": y,
             "source_tile": TILE_A,
             "properties": {"source_tiles": [TILE_A, TILE_B]}},
        ])
        gdf = build_candidate_gdf(
            manifest, {"candidate_00007": {"mound_probability": 0.9}}, 0.5,
        )
        refs = _reference_on(SHEET_B, x + 5, y)
        scope = lam.scope_detections_to_frame(gdf, bounds)
        assert scope.diagnostics["n_origin_switched"] == 1
        assert lam.calculate_f1_internal(gdf, refs, bounds, buffer_metres=20) == (
            1.0, 1.0, 1.0,
        )


@pytest.mark.skipif(
    not (_T26.exists() and _BOUNDS_384.exists() and _REFERENCE.exists()),
    reason="committed 26-of-30 set or 384 px frame not present",
)
class TestH2ArmMatchesItsCommittedCell:
    """H2's 26-of-30 arm, routed in memory, scores as its committed file."""

    @staticmethod
    def _frame() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """The 384 px evaluation frame and the reference set."""
        bounds = gpd.read_file(_BOUNDS_384).to_crs(TARGET_CRS)
        refs = gpd.read_file(_REFERENCE).to_crs(TARGET_CRS)
        return bounds, refs

    def test_in_memory_route_gives_the_rescored_value(self) -> None:
        """F1 at 20 m is 0.816471 (pre-fix route: 0.814118)."""
        bounds, refs = self._frame()
        with open(_T26, encoding="utf-8") as f:
            fc = json.load(f)
        gdf = acs.consensus_to_gdf(fc, bounds)
        assert len(gdf) == 415
        _p, _r, f1 = lam.calculate_f1_internal(gdf, refs, bounds, buffer_metres=20)
        assert round(f1, 6) == 0.816471

    def test_in_memory_route_equals_file_route(self) -> None:
        """Same F1 and same per-tile table as ``evaluate_detections.py``'s read.

        ``evaluate_detections.py`` reads the GeoJSON with geopandas and,
        since the file carries no ``source_tile``, assigns the first
        intersecting tile; the shared scorer then reads ``source_tiles``.
        """
        bounds, refs = self._frame()
        with open(_T26, encoding="utf-8") as f:
            fc = json.load(f)
        mem = acs.consensus_to_gdf(fc, bounds)

        file_gdf = gpd.read_file(_T26).to_crs(TARGET_CRS)
        joined = gpd.sjoin(
            file_gdf, bounds[["tile_name", "geometry"]],
            how="left", predicate="intersects",
        )
        joined = joined[~joined.index.duplicated(keep="first")]
        file_gdf["source_tile"] = joined["tile_name"]

        for buf in (20, 30):
            assert lam.calculate_f1_internal(mem, refs, bounds, buffer_metres=buf) == (
                lam.calculate_f1_internal(file_gdf, refs, bounds, buffer_metres=buf)
            )
        t_mem = lam.compute_per_tile_tp_fp_fn(mem, refs, bounds, buffer_metres=20)
        t_file = lam.compute_per_tile_tp_fp_fn(file_gdf, refs, bounds, buffer_metres=20)
        pd.testing.assert_frame_equal(
            t_mem.sort_values("tile_name").reset_index(drop=True),
            t_file.sort_values("tile_name").reset_index(drop=True),
        )
