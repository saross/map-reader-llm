"""W2.7's subset frames carry each cluster's contributing tiles (PI ruling D62 (1)).

``reports/w27-replicate-floors-2026-10-06-scripts/w27_55map_subset_replicates.py``
builds every § 6 and § 6b rung with ``cluster_subset``, a restatement of the
board's ``stride55_ladder.cluster_first_n``: votes from the greedy star
clustering and one standard-grid ``source_tile`` from the nearest pooled
detection's first member tile. Until 2026-10-13 nothing else reached the
scorer, so a cluster seen on two sheets could only be scored on the sheet
that one tile names. Ruling D62 (1): each cluster carries its contributing
tiles into scoring. These tests pin that:

* ``floors2_lib.cluster_votes_fast_origins`` (the KD-tree restatement the
  floors-v2 scripts install) equals the committed
  ``h13_k_sensitivity.cluster_votes_with_origins`` exactly, and keeps the
  pass bitmasks ``cluster_votes_fast`` leaves for the propensity model;
* ``cluster_subset`` writes ``source_tiles`` (the union of the members'
  tiles) beside an unchanged ``source_tile``, and the shared scorer then
  scores a two-sheet cluster on the sheet whose tiles hold it;
* ``load_upl_frame`` keeps each union candidate's ``properties.source_tiles``.

Synthetic fixtures only: two sheets whose tiles overlap by 100 m.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from scipy.spatial import cKDTree
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
W27_DIR = PROJECT_ROOT / "reports/w27-replicate-floors-2026-10-06-scripts"
sys.path.insert(0, str(W27_DIR))

import w27_55map_subset_replicates as w27  # noqa: E402  (inserts REPO, REPO/scripts)

from scripts import lib_advanced_metrics as lam  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes_with_origins  # noqa: E402

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"
X0, Y0 = 397_000.0, 4_705_000.0
SHEET_A = "K-35-001-1"
SHEET_B = "K-35-001-2"
TILE_A = f"{SHEET_A}_x0_y0.png"
TILE_B = f"{SHEET_B}_x0_y0.png"


def _floors2_lib():
    """The floors-v2 library (not a package), loaded from its path."""
    spec = importlib.util.spec_from_file_location(
        "floors2_lib_origin_test", W27_DIR / "floors-v2/floors2_lib.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["floors2_lib_origin_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _bounds() -> gpd.GeoDataFrame:
    """Sheet A's tile (x 0-1000) and sheet B's (x 900-1900), B listed first."""
    return gpd.GeoDataFrame(
        {"tile_name": [TILE_B, TILE_A]},
        geometry=[box(X0 + 900, Y0, X0 + 1900, Y0 + 1000), box(X0, Y0, X0 + 1000, Y0 + 1000)],
        crs=CRS,
    )


def _index() -> dict:
    """A one-tile standard-grid index per sheet, as build_map_constrained_index builds it."""
    return {
        SHEET_A: {"tree": cKDTree([[X0 + 500, Y0 + 500]]), "names": [TILE_A]},
        SHEET_B: {"tree": cKDTree([[X0 + 1400, Y0 + 500]]), "names": [TILE_B]},
    }


def _ref(sheet: str, xy: tuple[float, float]) -> gpd.GeoDataFrame:
    """One reference mound on ``sheet``."""
    return gpd.GeoDataFrame({"Map": [sheet], "Symbol": ["burial_mound"]},
                            geometry=[Point(xy)], crs=CRS)


def _det(xy: tuple[float, float], tiles: list[str]) -> dict:
    """One deduplicated detection (as ``dedup_fast`` returns it)."""
    return {"centroid": xy, "label": "burial_mound", "source_tiles": tiles, "cluster_size": 1}


def test_fast_origins_equals_committed():
    """Centroids, votes, tiles and pass masks equal the committed functions'."""
    lib = _floors2_lib()
    rng = np.random.default_rng(20261013)
    passes = []
    for p in range(4):
        dets = []
        for i in range(150):
            gx, gy = rng.integers(0, 12, size=2)
            xy = (float(X0 + 30.0 * gx + rng.normal(0, 7)),
                  float(Y0 + 30.0 * gy + rng.normal(0, 7)))
            sheet = SHEET_A if gx < 6 else SHEET_B
            dets.append(_det(xy, [f"{sheet}_x{p}_y{i}.png"]))
        passes.append(dets)
    c0, v0, o0 = cluster_votes_with_origins(passes, 1)
    c1, v1, o1 = lib.cluster_votes_fast_origins(passes, 1)
    masks_origins = list(lib.LAST_MEMBERS["masks"])
    c2, v2 = lib.cluster_votes_fast(passes, 1)
    assert np.array_equal(c0, c1) and np.array_equal(v0, v1) and o0 == o1
    assert np.array_equal(c1, c2) and np.array_equal(v1, v2)
    assert masks_origins == list(lib.LAST_MEMBERS["masks"])
    # Some clusters straddle the sheet line, so the test exercises two-sheet origins.
    assert any(len({t.split("_x")[0] for t in o}) > 1 for o in o0)


def test_cluster_subset_carries_member_tiles_and_scores_where_it_lies():
    """A cluster seen on both sheets, lying on B's tile only, is matched on B."""
    # Three passes: two report it on A's tile (inside it), one on B's; the
    # mean (x0 + 1003) is east of A's tile edge (x0 + 1000). The pooled
    # detection nearest the mean is an A member (x0 + 998), so source_tile
    # names A.
    passes = [[_det((X0 + 996.0, Y0 + 500.0), [TILE_A])],
              [_det((X0 + 998.0, Y0 + 500.0), [TILE_A])],
              [_det((X0 + 1015.0, Y0 + 500.0), [TILE_B])]]
    gdf = w27.cluster_subset(passes, (0, 1, 2), _index())
    assert gdf["vote_count"].tolist() == [3]
    assert gdf["source_tile"].tolist() == [TILE_A]
    assert gdf["source_tiles"].tolist() == [[TILE_A, TILE_B]]
    ref = _ref(SHEET_B, (X0 + 1004.0, Y0 + 500.0))
    scope = lam.scope_detections_to_frame(gdf, _bounds())
    assert scope.diagnostics["n_origin_switched"] == 1
    assert lam.calculate_f1_internal(gdf, ref, _bounds(), buffer_metres=50) == (1.0, 1.0, 1.0)


def test_cluster_subset_uses_the_installed_clustering(monkeypatch):
    """The floors-v2 hook replaces the clustering and its tiles reach the frame."""
    lib = _floors2_lib()
    monkeypatch.setattr(w27, "cluster_votes_origins", lib.cluster_votes_fast_origins)
    passes = [[_det((X0 + 300.0, Y0 + 500.0), [TILE_A])],
              [_det((X0 + 305.0, Y0 + 500.0), [TILE_A]), _det((X0 + 1500.0, Y0 + 500.0), [TILE_B])]]
    gdf = w27.cluster_subset(passes, (0, 1), _index())
    assert gdf["source_tiles"].tolist() == [[TILE_A], [TILE_B]]
    assert lib.LAST_MEMBERS["masks"] == [0b11, 0b10]


def test_load_upl_frame_keeps_candidate_tiles(tmp_path, monkeypatch):
    """Each UPL candidate keeps its member list; a candidate without one gets []."""
    (tmp_path / "crops-3of10").mkdir()
    (tmp_path / "verified-3of10").mkdir()
    cands = [
        {"candidate_id": 0, "source_tile": TILE_A, "centroid_x": X0 + 1003.0,
         "centroid_y": Y0 + 500.0,
         "properties": {"contributing_passes": ["run_1", "run_2", "run_6"], "vote_count": 3,
                        "source_tiles": [TILE_A, TILE_B]}},
        {"candidate_id": 1, "source_tile": TILE_A, "centroid_x": X0 + 300.0,
         "centroid_y": Y0 + 500.0,
         "properties": {"contributing_passes": ["run_1", "run_2", "run_3"], "vote_count": 3}},
    ]
    (tmp_path / "crops-3of10/candidate_manifest.json").write_text(json.dumps({"candidates": cands}))
    from scripts.final_board_sweeps import prob_key
    probs = {prob_key(c["candidate_id"]): {"mound_probability": 0.9} for c in cands}
    (tmp_path / "verified-3of10/probabilities.json").write_text(json.dumps({"results": probs}))
    monkeypatch.setattr(w27, "UPL", tmp_path)
    gdf = w27.load_upl_frame()
    assert gdf["source_tiles"].tolist() == [[TILE_A, TILE_B], []]
    ref = _ref(SHEET_B, (X0 + 1004.0, Y0 + 500.0))
    p, r, _ = lam.calculate_f1_internal(gdf, ref, _bounds(), buffer_metres=50)
    # The two-sheet candidate is switched to B and matched; the other is an A-sheet FP.
    assert (p, r) == (0.5, 1.0)
