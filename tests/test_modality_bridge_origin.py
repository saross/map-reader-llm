"""
Tier-1 tests: Run B's floors and verifier SD read their unions and rungs on the origin route.

Why this exists
---------------
``image_b_analysis.py`` scores the bridge cells with every union row and every
ladder cluster booked to a carrier tile on the sheet its members were seen on
(PI decision D62 (1)). ``scripts/modality_bridge_floors.py`` and
``scripts/modality_bridge_verifier_sd.py`` rebuild those cells and gate on
them, but read each union with its stored nearest-carrier ``source_tile`` and
clustered their rungs as bare centroids. Near a sheet edge that books a row
to the neighbouring sheet. While the re-keyed rows held the probability of a
crop cut from the wrong sheet (at most 0.05) no point admitted them; once the
2026-10-13 re-verification gave them real probabilities, the verifier SD's
gate 1 refused every committed set (S164 restatement pass, D65 (6)).

What is pinned
--------------
* the floors' rung builder keeps each cluster on its origin sheet
  (``image_b_analysis``'s ladder mechanism);
* the shared union loader, the floors' arm loader, the floors' originals and
  the verifier SD's replicates all book a union row on its origin sheet and
  keep the record of the directory read;
* the D65 (6) record of the re-verified rows is read from the legs' own
  ``reverify-*.json`` records: rows, cost, and the run's booking date.

Red sentinel: on the scripts before the fix, the rung, originals and
replicate tests fail on the value (the overlap row lands on sheet B) and the
loader and record tests fail for want of the functions.

The frame is ``tests/test_lib_cluster_origins.py``'s: two one-tile sheets
whose padded tiles overlap, and three passes in which one cluster, seen only
on sheet A, lies nearer sheet B's tile centroid. All synthetic.
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

from scripts import image_b_analysis as iba  # noqa: E402
from scripts import modality_bridge_anchors as mba  # noqa: E402
from scripts import modality_bridge_floors as fl  # noqa: E402
from scripts import modality_bridge_verifier_sd as vsd  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.lib_verify_dirs import POLICY_ENV  # noqa: E402
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"
TILE_A = "K-35-001-1_32635_x0_y0.png"
TILE_B = "K-35-001-2_32635_x0_y0.png"
CELL = "detect_brief-text"
UNION = "union_k3.geojson"
#: The union row (candidate number) of the cluster seen only on sheet A but
#: nearer sheet B's tile centroid.
OVERLAP_ROW = 1


def _two_sheets() -> gpd.GeoDataFrame:
    """Two one-tile sheets whose padded tiles overlap on x in [90, 110]."""
    return gpd.GeoDataFrame(
        {"tile_name": [TILE_A, TILE_B]},
        geometry=[box(-10, 0, 110, 100), box(90, 0, 210, 100)], crs=CRS)


def _passes() -> list[list[dict]]:
    """Three passes (``test_lib_cluster_origins._passes``)."""
    return [
        [{"centroid": (10.0, 10.0), "cluster_size": 2, "source_tiles": [TILE_A]},
         {"centroid": (105.0, 50.0), "cluster_size": 1, "source_tiles": [TILE_A, ""]},
         {"centroid": (300.0, 300.0), "cluster_size": 1, "source_tiles": [""]}],
        [{"centroid": (12.0, 10.0), "cluster_size": 1, "source_tiles": [TILE_A]},
         {"centroid": (160.0, 60.0), "cluster_size": 3, "source_tiles": [TILE_B]}],
        [{"centroid": (11.0, 11.0), "cluster_size": 2, "source_tiles": [TILE_B]},
         {"centroid": (106.0, 51.0), "cluster_size": 1, "source_tiles": [TILE_A]},
         {"centroid": (40.0, 90.0), "cluster_size": 1, "source_tiles": [""]},
         {"centroid": (45.0, 90.0), "cluster_size": 1, "source_tiles": [TILE_A]}],
    ]


def _write_passes(scoring: Path) -> None:
    """The passes as prepared ``detections_dedup.geojson`` files (project CRS)."""
    for i, p in enumerate(_passes(), start=1):
        run = scoring / "common" / CELL / f"run_{i}"
        run.mkdir(parents=True, exist_ok=True)
        feats = [{"type": "Feature",
                  "geometry": {"type": "Point", "coordinates": list(d["centroid"])},
                  "properties": {"label": "mound", "cluster_size": d["cluster_size"],
                                 "origin_tiles": ";".join(t for t in d["source_tiles"] if t)}}
                 for d in p]
        (run / "detections_dedup.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": feats}))


def _write_union(vroot: Path, bounds: gpd.GeoDataFrame) -> None:
    """The legacy union: bare centroids on any tile, stored nearest-carrier tile."""
    centroids, votes = cluster_votes(_passes(), 1)
    gdf = gpd.GeoDataFrame({"vote_count": votes},
                           geometry=[Point(xy) for xy in centroids], crs=CRS)
    gdf = gdf[[bool(bounds.intersects(g).any()) for g in gdf.geometry]].reset_index(drop=True)
    gdf["source_tile"] = assign_primary_tiles(gdf, bounds)
    vroot.mkdir(parents=True, exist_ok=True)
    gdf.to_file(vroot / UNION, driver="GeoJSON")


def _write_probs(vdir: Path, n: int, prob: float = 0.9) -> None:
    """A ``probabilities.json`` with every candidate at ``prob``."""
    vdir.mkdir(parents=True, exist_ok=True)
    (vdir / "probabilities.json").write_text(json.dumps(
        {"results": {f"candidate_{i:05d}": {"mound_probability": prob} for i in range(n)}}))


def _campaign(root: Path, bounds: gpd.GeoDataFrame, legs: tuple[str, ...]) -> Path:
    """``<root>/verifier/<cell>/`` with the union and its legs; passes in ``<root>/scoring``."""
    vroot = root / "verifier" / CELL
    _write_union(vroot, bounds)
    n = len(gpd.read_file(vroot / UNION))
    for leg in legs:
        _write_probs(vroot / leg, n)
    _write_passes(root / "scoring")
    return vroot


@pytest.fixture
def frame(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> gpd.GeoDataFrame:
    """The two-sheet frame as the scripts' worker state; the repository is ``tmp_path``."""
    bounds = _two_sheets()
    monkeypatch.delenv(POLICY_ENV, raising=False)
    monkeypatch.setitem(fl._G, "bounds", bounds)
    monkeypatch.setattr(iba, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(fl, "PROJECT_ROOT", tmp_path)
    return bounds


def _overlap_tile(gdf: gpd.GeoDataFrame) -> str:
    """The tile the overlap cluster (seen on A, nearer B) is booked to."""
    xy = np.c_[gdf.geometry.x.to_numpy(), gdf.geometry.y.to_numpy()]
    pos = int(np.argmin(np.hypot(xy[:, 0] - 105.5, xy[:, 1] - 50.5)))
    return gdf.iloc[pos]["source_tile"]


# --------------------------------------------------------------------------- #
# Rungs.
# --------------------------------------------------------------------------- #


def test_rung_cluster_stays_on_its_origin_sheet(frame: gpd.GeoDataFrame) -> None:
    """The floors' rung builder books the overlap cluster on A, as the ladder does."""
    rung = fl.build_rung(_passes())
    assert _overlap_tile(rung) == TILE_A
    # Votes and row count are cluster_votes' (no row dropped here).
    _c, votes = cluster_votes(_passes(), 1)
    assert list(rung["vote_count"]) == list(votes)


# --------------------------------------------------------------------------- #
# Unions.
# --------------------------------------------------------------------------- #


def test_union_loader_books_rows_on_their_origin_sheet(
        frame: gpd.GeoDataFrame, tmp_path: Path) -> None:
    """``load_union_on_origin``: the stored B tile is gated, then the row moves to A."""
    vroot = _campaign(tmp_path / "camp", frame, ("verify",))
    stored = gpd.read_file(vroot / UNION)
    assert stored.loc[OVERLAP_ROW, "source_tile"] == TILE_B  # the legacy booking
    u = fl.load_union_on_origin(vroot, UNION, "verify", _passes(), 3, "t")
    assert u.loc[OVERLAP_ROW, "source_tile"] == TILE_A
    assert u.attrs["verifier_probabilities"]["dir"] == f"camp/verifier/{CELL}/verify"
    assert list(u.index) == list(range(len(stored)))


def test_floors_arm_state_is_on_origin(frame: gpd.GeoDataFrame, tmp_path: Path,
                                       monkeypatch: pytest.MonkeyPatch) -> None:
    """``load_arm``: the union the rungs inherit from is the origin union."""
    arm = fl.Arm("arm", CELL, 3, (("g3v", "verify_g3"),))
    vroot = _campaign(tmp_path / "arm", frame, ("verify_g3",))
    _write_probs(vroot / "verify_g3_repaired", len(gpd.read_file(vroot / UNION)), 0.95)
    monkeypatch.setattr(fl, "OUTPUTS", tmp_path)
    state, sha, legs = fl.load_arm("arm", arm, tmp_path, {})
    assert set(sha) == {"run_1", "run_2", "run_3"}
    assert legs["arm/g3v"]["dir"].endswith("verify_g3_repaired")
    assert list(state["probs"]["g3v"]) == [0.95] * len(state["union_votes"])
    expected = fl.load_union_on_origin(vroot, UNION, "verify_g3", _passes(), 3, "t")
    assert np.allclose(state["union_xy"][:, 0], expected.geometry.x.to_numpy())
    assert expected.loc[OVERLAP_ROW, "source_tile"] == TILE_A


def test_floors_originals_are_read_on_origin(frame: gpd.GeoDataFrame, tmp_path: Path,
                                             monkeypatch: pytest.MonkeyPatch) -> None:
    """``original_sets`` books an original's set on its origin sheet (the date component)."""
    _campaign(tmp_path / "orig", frame, ("verify",))
    cell = mba.AnchorCell("orig", "orig", CELL, UNION, "verify", 3, 0.0, 0.5, 1)
    monkeypatch.setattr(mba, "ORIGINAL_CELLS", (cell,))
    seen: list[gpd.GeoDataFrame] = []

    class Stop(Exception):
        pass

    def spy(gdf: gpd.GeoDataFrame) -> dict:
        seen.append(gdf)
        raise Stop

    monkeypatch.setattr(fl, "counts_of", spy)
    with pytest.raises(Stop):
        fl.original_sets()
    assert _overlap_tile(seen[0]) == TILE_A


def test_verifier_sd_replicates_are_read_on_origin(
        frame: gpd.GeoDataFrame, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``load_replicates``: replicate 1's union is the origin union, its record kept."""
    arm = fl.Arm("arm", CELL, 3, (("g3v", "verify_g3"),))
    vroot = _campaign(tmp_path / "arm", frame, ("verify_g3",))
    _write_probs(vroot / "verify_g3_repaired", len(gpd.read_file(vroot / UNION)), 0.95)
    monkeypatch.setattr(fl, "ARMS", {"arm": arm})
    monkeypatch.setattr(fl, "OUTPUTS", tmp_path)
    unions, prov, failures = vsd.load_replicates((1,))
    assert failures == []
    assert unions[("arm", "g3v", 1)].loc[OVERLAP_ROW, "source_tile"] == TILE_A
    assert prov["arm/g3v/rep1"]["dir"].endswith("verify_g3_repaired")


# --------------------------------------------------------------------------- #
# The D65 (6) record.
# --------------------------------------------------------------------------- #


def test_reverification_record_reads_the_legs_records(
        frame: gpd.GeoDataFrame, tmp_path: Path) -> None:
    """Rows, cost and the run's booking date come from the records; a leg as run has 0 rows."""
    leg = tmp_path / "out" / "v" / "verify_g3_repaired"
    leg.mkdir(parents=True)
    rec = leg / "reverify-wrong-sheet-2026-10-13.json"
    rec.write_text(json.dumps({
        "script": "scripts/reverify_wrong_sheet_crops.py book", "decision": "D62 (1) step 2",
        "run_dir": "outputs/wsr", "rows": [{"key": "candidate_00001", "cost_usd": 0.0006},
                                           {"key": "candidate_00002", "cost_usd": 0.0007}]}))
    run = tmp_path / "outputs" / "wsr"
    run.mkdir(parents=True)
    (run / "record.json").write_text(json.dumps({"booked_at": "2026-10-13T06:44:45+00:00"}))
    out = fl.reverification_record({
        "a/g3v/rep1": {"dir": "out/v/verify_g3_repaired",
                       "reverify_records": ["out/v/verify_g3_repaired/"
                                            "reverify-wrong-sheet-2026-10-13.json"]},
        "b/g3v/rep1": {"dir": "out/v/verify_g3", "reverify_records": []},
    })
    assert out["legs"]["a/g3v/rep1"]["rows"] == 2
    assert out["legs"]["a/g3v/rep1"]["cost_usd"] == pytest.approx(0.0013)
    assert out["legs"]["a/g3v/rep1"]["dates"] == ["2026-10-13"]
    assert out["legs"]["b/g3v/rep1"]["rows"] == 0
    assert out["runs"]["outputs/wsr/record.json"]["booked_at"] == "2026-10-13T06:44:45+00:00"
    assert (out["rows"], out["dates"]) == (2, ["2026-10-13"])
    assert out["cost_usd"] == pytest.approx(0.0013)


def test_reverification_date_falls_back_to_the_record_name(
        frame: gpd.GeoDataFrame, tmp_path: Path) -> None:
    """Without the run record, the date is the one in the leg record's file name."""
    rec = tmp_path / "reverify-wrong-sheet-2026-10-13.json"
    rec.write_text(json.dumps({"run_dir": "outputs/missing", "rows": [{"cost_usd": 0.001}]}))
    out = fl.reverification_record({"x": {"dir": "d", "reverify_records": [str(rec)]}})
    assert out["dates"] == ["2026-10-13"]
    assert out["runs"]["outputs/missing/record.json"]["booked_at"] is None
