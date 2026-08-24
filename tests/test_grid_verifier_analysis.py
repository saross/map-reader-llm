"""Tier-1 tests for the grid post-verifier scoring chain.

Covers the pure computational core of ``scripts/grid_verifier_analysis.py``:
the probability join and its gates (documented-count reproduction, contiguous
candidate keys), the carrier-tile reassignment gate, the union score
reproduction gate, the inclusive threshold semantics of ``verified_subset``,
best-row selection (including the pure-verifier k = 1 restriction), and the
per-tile count alignment the paired bootstrap consumes.

The live stages — the four committed 9,133-candidate unions, the full sweep,
and the B = 10,000 bootstraps — run against the real artefacts on sapphire
and are not simulated here.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import grid_verifier_analysis as gva  # noqa: E402

CRS = "EPSG:32635"


#: Tile names must match the tiling pipeline's ``<map>_x{N}_y{N}.png``
#: pattern or the scorer's per-map matching resolves them to 'Unknown'.
TILE_1 = "m1_x0_y0.png"
TILE_2 = "m1_x100_y0.png"


def _bounds() -> gpd.GeoDataFrame:
    """Two adjacent 100 m carrier tiles on one map."""
    return gpd.GeoDataFrame(
        {"tile_name": [TILE_1, TILE_2]},
        geometry=[box(0, 0, 100, 100), box(100, 0, 200, 100)], crs=CRS)


def _refs() -> gpd.GeoDataFrame:
    """One reference mound on tile t1 (the scorer requires a ``Map`` column)."""
    return gpd.GeoDataFrame(
        {"Map": ["m1"]}, geometry=[Point(52, 52)], crs=CRS)


def _union() -> gpd.GeoDataFrame:
    """Three candidates: two on tile 1 (one mound-probable), one on tile 2."""
    return gpd.GeoDataFrame(
        {
            "vote_count": [10, 2, 5],
            "mound_probability": [0.95, 0.05, 0.2],
            "source_tile": [TILE_1, TILE_1, TILE_2],
        },
        geometry=[Point(50, 50), Point(20, 20), Point(150, 50)], crs=CRS)


def _write_cell(root: Path, cell: str, probs: dict[str, float]) -> None:
    """Write a minimal union + probabilities pair for one cell."""
    coords = [[25.0, 42.0], [25.001, 42.001], [25.002, 42.002]]
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": coords[i]},
            "properties": {"vote_count": i + 1, "source_tile": f"t{i}"},
        }
        for i in range(len(probs))
    ]
    cell_dir = root / cell
    (cell_dir / "verify").mkdir(parents=True)
    (cell_dir / "union_k10.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "features": features}))
    (cell_dir / "verify" / "probabilities.json").write_text(json.dumps(
        {"results": {k: {"mound_probability": v} for k, v in probs.items()}}))


@pytest.mark.tier1
def test_verified_subset_thresholds_are_inclusive():
    union = _union()
    kept = gva.verified_subset(union, prob_t=0.2, min_votes=5)
    # 0.2 >= 0.2 keeps the tile-2 candidate; 0.05 < 0.2 drops the second.
    assert sorted(kept["source_tile"]) == [TILE_1, TILE_2]
    assert gva.verified_subset(union, 0.0, 1).shape[0] == 3
    assert gva.verified_subset(union, 0.96, 1).shape[0] == 0


@pytest.mark.tier1
def test_best_row_and_pure_verifier_restriction():
    rows = [
        {"cell": "c", "f1": 0.5, "min_votes": 1, "prob_t": 0.2},
        {"cell": "c", "f1": 0.7, "min_votes": 3, "prob_t": 0.2},
        {"cell": "c", "f1": 0.6, "min_votes": 1, "prob_t": 0.5},
        {"cell": "other", "f1": 0.9, "min_votes": 1, "prob_t": 0.0},
    ]
    assert gva.best_row(rows, "c")["f1"] == 0.7
    # Restricted to k = 1, the 0.7 row (k = 3) may not compete.
    assert gva.best_row(rows, "c", pure_verifier=True)["f1"] == 0.6


@pytest.mark.tier1
def test_load_verified_union_joins_by_index(tmp_path, monkeypatch):
    probs = {f"candidate_{i:05d}": p for i, p in enumerate([0.9, 0.1, 0.5])}
    _write_cell(tmp_path, "cellA", probs)
    monkeypatch.setattr(gva, "VERIFIER_DIR", tmp_path)
    monkeypatch.setattr(gva, "EXPECTED", {"cellA": 3})
    gdf = gva.load_verified_union("cellA")
    assert list(gdf["mound_probability"]) == [0.9, 0.1, 0.5]
    assert list(gdf["vote_count"]) == [1, 2, 3]
    assert gdf.crs.to_epsg() == 32635


@pytest.mark.tier1
def test_load_verified_union_count_gate(tmp_path, monkeypatch):
    probs = {f"candidate_{i:05d}": 0.5 for i in range(3)}
    _write_cell(tmp_path, "cellA", probs)
    monkeypatch.setattr(gva, "VERIFIER_DIR", tmp_path)
    monkeypatch.setattr(gva, "EXPECTED", {"cellA": 4})
    with pytest.raises(gva.JoinGateError, match="documented 4"):
        gva.load_verified_union("cellA")


@pytest.mark.tier1
def test_load_verified_union_key_gate(tmp_path, monkeypatch):
    # A gap in the id range (00000, 00002) must refuse to join.
    probs = {"candidate_00000": 0.5, "candidate_00002": 0.5}
    _write_cell(tmp_path, "cellA", probs)
    monkeypatch.setattr(gva, "VERIFIER_DIR", tmp_path)
    monkeypatch.setattr(gva, "EXPECTED", {"cellA": 2})
    with pytest.raises(gva.JoinGateError, match="contiguous"):
        gva.load_verified_union("cellA")


@pytest.mark.tier1
def test_reassignment_gate_detects_drift():
    bounds = _bounds()
    union = _union()
    ok = gva.reassignment_gate(union, bounds, "cell")
    assert list(ok["source_tile"]) == [TILE_1, TILE_1, TILE_2]
    drifted = union.copy()
    drifted.loc[0, "source_tile"] = TILE_2
    with pytest.raises(gva.JoinGateError, match="different carrier tile"):
        gva.reassignment_gate(drifted, bounds, "cell")


@pytest.mark.tier1
def test_union_reproduction_gate():
    bounds = _bounds()
    union = _union()
    refs = _refs()
    anchor = gva.score(union, refs, bounds)
    result = gva.union_reproduction_gate(union, bounds, refs, anchor, "cell")
    assert result["n_detections"] == 3
    bad = dict(anchor, f1=anchor["f1"] + 0.01)
    with pytest.raises(gva.JoinGateError, match="f1"):
        gva.union_reproduction_gate(union, bounds, refs, bad, "cell")
    short = dict(anchor, n_detections=2)
    with pytest.raises(gva.JoinGateError, match="detections"):
        gva.union_reproduction_gate(union, bounds, refs, short, "cell")


@pytest.mark.tier1
def test_per_tile_counts_align_with_bounds_order():
    bounds = _bounds()
    union = _union()
    refs = _refs()
    counts = gva.per_tile_counts(union, bounds, refs)
    # t1 holds the matched pair (TP) plus one unmatched detection (FP);
    # t2 holds one unmatched detection (FP) and no references.
    assert counts["tp"].tolist() == [1.0, 0.0]
    assert counts["fp"].tolist() == [1.0, 1.0]
    assert counts["fn"].tolist() == [0.0, 0.0]
