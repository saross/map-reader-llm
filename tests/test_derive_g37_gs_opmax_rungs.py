"""Tier-1 tests for the 3.7 GS opmax derivation's origin route (S164, 2026-10-15).

``scripts/derive_g37_gs_opmax_rungs.py`` derives the sweep-optimal point of
the Gemini 3.7 screen's committed K = 5 and K = 10 stages. Their unions record
one legacy ``source_tile`` per row and no member list, so a row is booked to
that tile's sheet unless its members are attached first. The gold-standard
chain attaches them (``lib_cluster_origins.union_on_origin``, PR #42, D62
(1)); before the 2026-10-15 fix this script did not, and the re-verified
wrong-sheet rows scored on the wrong sheet (0.8984 at (0.10, k5) against the
origin-routed board cell's 0.9165;
``reports/s164-agent-records/restatement-pass.md`` § 1.4).

These tests pin, on synthetic two-sheet data (no repository artefacts read):

* the stage's union goes through the chain's sequence (leg-rule join, carrier
  gate, the cell's first K prepared passes, the origin step) and comes back
  on its members' sheet;
* the sweep scores a row seen on sheet B as a true positive on B, where the
  bare union's legacy tile on sheet A would make it a false positive;
* the carried cross-check is keyed by the leg directory read, with the dated
  count for the re-verified leg.
"""

from __future__ import annotations

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from scripts import derive_g37_gs_opmax_rungs as derive
from scripts.lib_cluster_origins import ORIGIN_COLUMN

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"

#: Two study sheets, one padded tile each, overlapping on x in [90, 130].
#: Sheet A's tile centroid is at x = 60 and sheet B's at x = 150, so a point
#: at x = 100 is nearer A's centroid: the legacy carrier rule books it to A
#: even when every pass saw it on B.
SHEET_A = "K-35-052-4_32635"
SHEET_B = "K-35-053-3_Elenovo"
TILE_A = f"{SHEET_A}_x4032_y0.png"
TILE_B = f"{SHEET_B}_x0_y0.png"
K = 5


def _bounds() -> gpd.GeoDataFrame:
    """Two one-tile sheets whose padded tiles overlap by 40 m."""
    return gpd.GeoDataFrame({"tile_name": [TILE_A, TILE_B]},
                            geometry=[box(-10, 0, 130, 100), box(90, 0, 210, 100)],
                            crs=CRS)


def _reference() -> gpd.GeoDataFrame:
    """One reference mound on sheet B, in the tiles' overlap."""
    return gpd.GeoDataFrame({"Map": [SHEET_B]}, geometry=[Point(100.0, 50.0)], crs=CRS)


def _bare_union() -> gpd.GeoDataFrame:
    """The committed union's shape: one five-vote row, legacy tile on sheet A."""
    union = gpd.GeoDataFrame(
        {"source_tile": [TILE_A], "vote_count": [K], "mound_probability": [0.9]},
        geometry=[Point(100.0, 50.0)], crs=CRS)
    union.attrs["verifier_probabilities"] = {"dir": "verify_repaired"}
    return union


def _passes() -> list[list[dict]]:
    """Five prepared passes, each seeing the mound once, on sheet B's tile."""
    return [[{"centroid": (100.0, 50.0), "cluster_size": 1, "source_tiles": [TILE_B],
              "label": "mound"}] for _ in range(K)]


@pytest.fixture
def routed(monkeypatch: pytest.MonkeyPatch) -> tuple[gpd.GeoDataFrame, dict]:
    """The synthetic stage through ``origin_union``, with the calls recorded."""
    calls: dict = {}

    def fake_load(vroot, union_name, verify_dir, policy=None):
        calls["load"] = (vroot, union_name, verify_dir)
        return _bare_union()

    def fake_passes(scoring, cell, scope="common", n_passes=10):
        calls["passes"] = (scoring, cell, n_passes)
        return _passes()

    monkeypatch.setattr(derive, "load_image_union", fake_load)
    monkeypatch.setattr(derive, "common_bounds", _bounds)
    monkeypatch.setattr(derive, "load_cell_passes", fake_passes)
    stage = next(s for s in derive.STAGES if s["k"] == K)
    return derive.origin_union(stage, "verify"), calls


def test_origin_union_runs_the_chain_sequence(routed):
    """Leg-rule join, then the cell's first K passes, then the origin step."""
    union, calls = routed
    vroot, union_name, leg = calls["load"]
    assert vroot == derive.BASE_DIR / derive.VERIFIER_ROOT
    assert (union_name, leg) == ("union_k5.geojson", "verify")
    assert calls["passes"] == (derive.BASE_DIR / derive.SCORING, derive.CELL, K)
    # The row is re-tiled on the sheet its members were seen on.
    assert union.loc[0, "source_tile"] == TILE_B
    assert TILE_B in str(union.loc[0, ORIGIN_COLUMN])
    assert union.attrs["verifier_probabilities"] == {"dir": "verify_repaired"}


def _f1_at(rows: list[dict], vote_t: int, prob_t: float) -> float:
    """The 20 m F1 of one sweep row."""
    return next(r["f1"] for r in rows if r["buffer_m"] == 20 and r["vote_t"] == vote_t
                and abs(r["prob_t"] - prob_t) < 1e-9)


def test_sweep_scores_the_row_on_its_members_sheet(routed):
    """On the origin route the row is a TP on B; the bare union's is an FP on A."""
    union, _ = routed
    rows = derive.sweep_rows(union, _bounds(), _reference(), config="t", buffers=[20])
    assert _f1_at(rows, K, 0.10) == pytest.approx(1.0)
    # The schema argmax_at_headline reads, one row per (vote_t, prob_t).
    assert {"config", "vote_t", "prob_t", "n", "p", "r", "f1", "buffer_m"} <= set(rows[0])
    assert len(rows) == K * len(derive.PROB_THRESHOLDS)
    bare = derive.sweep_rows(_bare_union(), _bounds(), _reference(), config="t",
                             buffers=[20])
    assert _f1_at(bare, K, 0.10) == pytest.approx(0.0)


def test_materialised_cell_keeps_the_members(routed, tmp_path):
    """The written cell carries the member tiles the scorer attributes by."""
    union, _ = routed
    out = tmp_path / "cell.geojson"
    assert derive.materialise_origin(union, vote_t=K, prob_t=0.10, output=out) == 1
    written = gpd.read_file(out)
    assert TILE_B in str(written.loc[0, ORIGIN_COLUMN])
    assert written.crs.to_epsg() == 4326


def test_carried_crosscheck_is_keyed_by_the_leg_read():
    """443 on the leg as run; the dated 451 on the re-verified leg (D62 (1))."""
    check = derive.CARRIED_CROSSCHECK[5]
    assert (check["vote_t"], check["prob_t"]) == (5, 0.10)
    assert check["n_detections"] == {"verify": 443, "verify_repaired": 451}
