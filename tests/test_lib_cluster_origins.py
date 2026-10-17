"""Tier-1 tests for the cluster-origin route (PI ruling D62 (1), 2026-10-13).

``scripts/lib_cluster_origins.py`` carries each consensus cluster's
contributing tiles from the passes into the shared scorer, so a detection is
booked to a carrier tile on the sheet it was seen on rather than the nearest
tile on any sheet. These tests pin:

* the clustering is ``h13_k_sensitivity.cluster_votes`` exactly (centroids and
  votes), with the members' tiles as the only addition;
* a point in two sheets' tile overlap stays on its origin sheet, and a point
  on no tile of its own sheet is dropped;
* the committed-union rebuild gate refuses any union it cannot reproduce row
  for row;
* on the real artefacts: a rebuilt grid union equals its committed geometry
  and votes, and the plateau board's four incumbents score the recorded-sheet
  F1 the main session reproduced independently
  (``reports/s163-agent-records/plateau-recorded-sheet-check-2026-10-13/
  output.txt``), while the legacy bare-centroid path still gives the
  committed board's F1.
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
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.lib_cluster_origins import (  # noqa: E402
    ORIGIN_COLUMN,
    OriginGateError,
    attach_union_origins,
    cluster_votes_with_members,
    member_tiles,
    points_on_origin,
    recorded_origin,
    rekey_on_origin,
    union_on_origin,
)

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"

#: Two sheets whose padded tiles overlap on x in [90, 110]. Sheet A's tile
#: centroid is at x = 50 and sheet B's at x = 150, so a point at x = 105 is
#: nearer B's centroid: the legacy rule books it to B whatever it was seen on.
TILE_A = "K-35-001-1_32635_x0_y0.png"
TILE_B = "K-35-001-2_32635_x0_y0.png"


def _two_sheets() -> gpd.GeoDataFrame:
    """Two one-tile sheets whose padded tiles overlap by 20 m."""
    return gpd.GeoDataFrame(
        {"tile_name": [TILE_A, TILE_B]},
        geometry=[box(-10, 0, 110, 100), box(90, 0, 210, 100)], crs=CRS)


def _passes() -> list[list[dict]]:
    """Three passes: a three-vote cluster, a two-vote pair, and one-vote clusters.

    The last pass holds two detections 5 m apart, so one cluster has two
    members but one vote: votes count distinct passes, not members.
    """
    return [
        [{"centroid": (10.0, 10.0), "cluster_size": 2, "source_tiles": [TILE_A]},
         {"centroid": (105.0, 50.0), "cluster_size": 1, "source_tiles": [TILE_A, ""]},
         {"centroid": (300.0, 300.0), "cluster_size": 1, "source_tiles": [""]}],
        [{"centroid": (12.0, 10.0), "cluster_size": 1, "source_tiles": [TILE_A]},
         {"centroid": (160.0, 60.0), "cluster_size": 3, "source_tiles": [TILE_B]}],
        [{"centroid": (11.0, 11.0), "cluster_size": 2, "source_tiles": [TILE_B]},
         {"centroid": (106.0, 51.0), "cluster_size": 1, "source_tiles": [TILE_A]},
         {"centroid": (40.0, 90.0), "cluster_size": 1},
         {"centroid": (45.0, 90.0), "cluster_size": 1, "source_tiles": [TILE_A]}],
    ]


@pytest.mark.parametrize("min_corroboration", [1, 2, 3, 4])
def test_clustering_is_cluster_votes_exactly(min_corroboration):
    """Centroids and votes equal ``cluster_votes`` at every corroboration level."""
    centroids, votes, members = cluster_votes_with_members(_passes(), min_corroboration)
    ref_centroids, ref_votes = cluster_votes(_passes(), min_corroboration)
    assert np.array_equal(centroids, ref_centroids)
    assert np.array_equal(votes, ref_votes)
    assert len(members) == len(votes)


def test_members_are_the_union_of_member_tiles():
    """A cluster's origin is every tile any member was seen on, sorted, no blanks."""
    centroids, votes, members = cluster_votes_with_members(_passes(), 1)

    def members_at(x: float, y: float) -> list[str]:
        """The members of the cluster whose centroid lies at (x, y)."""
        pos = int(np.argmin(np.hypot(centroids[:, 0] - x, centroids[:, 1] - y)))
        assert np.hypot(centroids[pos, 0] - x, centroids[pos, 1] - y) < 1e-6
        return members[pos]

    assert members_at(11.0, 31.0 / 3.0) == sorted([TILE_A, TILE_B])
    assert members_at(105.5, 50.5) == [TILE_A]
    assert members_at(160.0, 60.0) == [TILE_B]
    assert members_at(300.0, 300.0) == []
    assert members_at(42.5, 90.0) == [TILE_A]
    assert list(votes) == [3, 2, 1, 1, 1]


def test_member_tiles_accepts_string_and_missing():
    """The loaders' shapes: a list with blanks, a ``;`` string, or nothing."""
    assert member_tiles({"source_tiles": [TILE_A, ""]}) == [TILE_A]
    assert member_tiles({"source_tiles": f"{TILE_A};{TILE_B}"}) == [TILE_A, TILE_B]
    assert member_tiles({}) == []


def test_point_in_the_overlap_stays_on_its_origin_sheet():
    """The legacy rule re-keys the overlap point to sheet B; the origin keeps A."""
    centroids = np.array([[105.0, 50.0], [105.0, 50.0], [150.0, 50.0]])
    origins = [[TILE_A], [], [TILE_A]]
    frame, diag = points_on_origin(centroids, _two_sheets(), origins, CRS)
    # Row 0: seen on A, nearer B's centroid, in A's tile -> stays on A.
    assert frame.loc[0, "source_tile"] == TILE_A
    # Row 1: no origin -> the legacy rule (nearest centroid) books it to B.
    assert frame.loc[1, "source_tile"] == TILE_B
    # Row 2: seen on A but on no tile of A -> dropped (the scorer would drop it).
    assert 2 not in frame.index
    assert frame.loc[0, ORIGIN_COLUMN] == TILE_A
    assert diag["n_cross_sheet_avoided"] == 1
    assert diag["n_outside_origin_sheet"] == 1
    assert diag["n_no_origin"] == 1


def test_points_on_origin_can_keep_unassigned_rows():
    """``drop_unassigned=False`` keeps an off-sheet row with a null tile."""
    frame, _ = points_on_origin(
        np.array([[150.0, 50.0]]), _two_sheets(), [[TILE_A]], CRS,
        drop_unassigned=False)
    assert len(frame) == 1
    assert frame.iloc[0]["source_tile"] is None


def test_points_on_origin_empty_input_is_scorable():
    """No clusters gives an empty frame with the columns the scorer reads."""
    frame, diag = points_on_origin(
        np.zeros((0, 2)), _two_sheets(), [], CRS, columns={"vote_count": []})
    assert frame.empty
    assert {"source_tile", ORIGIN_COLUMN, "vote_count"} <= set(frame.columns)
    assert diag["n_points"] == 0


def test_recorded_origin_keeps_the_files_own_tile():
    """A set that records ``source_tile`` keeps it as its origin."""
    gdf = gpd.GeoDataFrame(
        {"source_tile": [TILE_A, None]}, geometry=[Point(0, 0)] * 2, crs=CRS)
    assert recorded_origin(gdf) == [[TILE_A], []]
    with pytest.raises(KeyError):
        recorded_origin(gpd.GeoDataFrame(geometry=[Point(0, 0)], crs=CRS))


def _committed_union(passes: list[list[dict]], bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """The legacy materialiser's union: bare centroids, kept if on any tile."""
    centroids, votes = cluster_votes(passes, 1)
    gdf = gpd.GeoDataFrame(
        {"vote_count": votes}, geometry=[Point(xy) for xy in centroids], crs=CRS)
    on_tile = [bool(bounds.intersects(g).any()) for g in gdf.geometry]
    return gdf[on_tile].reset_index(drop=True)


def test_attach_union_origins_joins_members_row_for_row():
    """A union built the legacy way gets its members back, in its own row order."""
    bounds = _two_sheets()
    union = _committed_union(_passes(), bounds)
    out = attach_union_origins(union, _passes(), bounds, label="t")
    assert list(out.index) == list(union.index)
    assert out[ORIGIN_COLUMN].tolist() == [
        f"{TILE_A};{TILE_B}", TILE_A, TILE_B, TILE_A]
    rekeyed, diag = rekey_on_origin(out, bounds)
    # The overlap cluster (seen on A only) is booked on A, not B.
    assert rekeyed.loc[1, "source_tile"] == TILE_A
    assert diag["n_cross_sheet_avoided"] == 1


@pytest.mark.parametrize("damage", ["drop_row", "votes", "shift"])
def test_attach_union_origins_refuses_a_union_it_cannot_rebuild(damage):
    """Count, votes, or geometry off: the gate refuses rather than mis-join."""
    bounds = _two_sheets()
    union = _committed_union(_passes(), bounds)
    if damage == "drop_row":
        union = union.iloc[:-1]
    elif damage == "votes":
        union.loc[0, "vote_count"] = 1
    else:
        union.loc[0, "geometry"] = Point(11.0, 10.5)
    with pytest.raises(OriginGateError):
        attach_union_origins(union, _passes(), bounds, label="t")


def test_union_on_origin_needs_all_its_passes():
    """Fewer passes than the union was built from is refused."""
    bounds = _two_sheets()
    union = _committed_union(_passes(), bounds)
    with pytest.raises(OriginGateError):
        union_on_origin(union, _passes()[:2], bounds, label="t", n_passes=3)


# --- Real artefacts (tracked files; skipped only if a checkout lacks them) ---

GRID_SCORING = PROJECT_ROOT / "outputs/grid-2026-08-18/scoring"
GRID_UNION = PROJECT_ROOT / "outputs/grid-2026-08-18/verifier/g512_ov064/union_k10.geojson"
COMMON_BOUNDS = GRID_SCORING / "bounds/grid_common_bounds.geojson"
PLATEAU = PROJECT_ROOT / "results/stride-2026-08-25/plateau_analyses.json"


def _need(*paths: Path) -> None:
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        pytest.skip(f"artefacts not in this checkout: {missing}")


def test_rebuilt_grid_union_equals_its_committed_geometry():
    """g512_ov064's K = 10 union, rebuilt with members, is the committed one.

    ``union_with_votes`` now records members and books each cluster on its
    own sheet; its candidate set, order, votes, and centroids must still be
    the verified file's (1,402 rows), and exactly the rows the legacy rule
    re-keyed change tile (25, measured 2026-10-13).
    """
    _need(GRID_UNION, COMMON_BOUNDS)
    from scripts.grid_analysis import load_cell_passes
    from scripts.materialise_grid_unions import EXPECTED, union_with_votes

    bounds = gpd.read_file(COMMON_BOUNDS)
    committed = gpd.read_file(GRID_UNION).to_crs(CRS)
    passes = load_cell_passes(GRID_SCORING, "g512_ov064")
    rebuilt = union_with_votes(passes, bounds)
    assert len(rebuilt) == len(committed) == EXPECTED["g512_ov064"]
    assert np.array_equal(rebuilt["vote_count"].to_numpy(),
                          committed["vote_count"].to_numpy())
    shift = np.hypot(rebuilt.geometry.x.to_numpy() - committed.geometry.x.to_numpy(),
                     rebuilt.geometry.y.to_numpy() - committed.geometry.y.to_numpy())
    assert float(shift.max()) < 1e-6
    assert (rebuilt[ORIGIN_COLUMN] != "").all()
    moved = int((rebuilt["source_tile"].to_numpy()
                 != committed["source_tile"].to_numpy()).sum())
    assert moved == 25


#: The independent reproduction's recorded-sheet F1 @ 20 m per incumbent,
#: which the committed board (``board_13cell.f1``) holds since the restatement
#: pass of 2026-10-15.
RECORDED_SHEET_F1 = {"opmax": 0.895981, "headline": 0.891018,
                     "min11": 0.884236, "min6": 0.879042}


def test_plateau_incumbents_score_on_their_recorded_sheets():
    """The fix gives the committed F1; the legacy path does not.

    The red sentinel for D62 (1) on the signed plateau board: if the
    incumbents lose their recorded sheet again, the first or third assertion
    fails; if the scorer or the inputs drift, the second does. Until the
    restatement pass (2026-10-15, reports/s164-agent-records/
    restatement-pass.md) the committed board still held the legacy path's
    values, and this test pinned the legacy score to it instead.
    """
    import stride_plateau_analyses as sp
    from scripts.grid_analysis import as_gdf, score

    paths = [PROJECT_ROOT / rel for rel in sp.INCUMBENTS.values()]
    _need(COMMON_BOUNDS, PLATEAU, *paths)
    bounds = gpd.read_file(COMMON_BOUNDS)
    ref = gpd.read_file(sp.GROUND_TRUTH)
    committed = json.loads(PLATEAU.read_text())["board_13cell"]["f1"]
    for name, rel in sp.INCUMBENTS.items():
        fixed = score(sp.load_incumbent(rel, bounds), ref, bounds)["f1"]
        assert round(fixed, 6) == RECORDED_SHEET_F1[name], name
        assert abs(fixed - committed[name]) < 1e-12, name
        inc = gpd.read_file(PROJECT_ROOT / rel).to_crs(CRS)
        legacy = as_gdf(np.asarray([[g.x, g.y] for g in inc.geometry]), bounds)
        # The legacy path re-keys rows across sheets; it scored 0.0072 to
        # 0.0168 lower on these four sets (PI ruling D62 (1)).
        assert abs(score(legacy, ref, bounds)["f1"] - committed[name]) > 1e-3, name
