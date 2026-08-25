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
    """Write a minimal union + probabilities pair for one cell.

    The probability keys are written in REVERSED order deliberately: the
    real ``probabilities.json`` files record async completion order, not
    index order, so a positional (order-based) join would scramble ~60 %
    of the real candidates while passing an index-ordered fixture. This
    fixture must never be index-ordered.
    """
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
    scrambled = dict(reversed(list(probs.items())))
    (cell_dir / "verify" / "probabilities.json").write_text(json.dumps(
        {"results": {k: {"mound_probability": v} for k, v in scrambled.items()}}))


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


@pytest.mark.tier1
def test_sweep_cell_threshold_set_is_exact_observed_values():
    """The threshold grid is the exact observed probability set, unrounded.

    A rounded grid can mint a threshold no candidate attains (breaking the
    "loses nothing" guarantee); a 3-decimal probability pins the contract.
    """
    bounds = _bounds()
    refs = _refs()
    union = _union()
    union["mound_probability"] = [0.125, 0.05, 0.2]
    rows = gva.sweep_cell(union, bounds, refs, "g512_ov064")
    thresholds = sorted({r["prob_t"] for r in rows})
    assert thresholds == [0.0, 0.05, 0.125, 0.2]
    assert len(rows) == 4 * 10
    at_125 = next(r for r in rows if r["prob_t"] == 0.125 and r["min_votes"] == 1)
    # Probabilities >= 0.125 are 0.125 and 0.2 — the 3-dp candidate survives
    # its own threshold.
    assert at_125["n_detections"] == 2


@pytest.mark.tier1
def test_materialise_condition_coverage_record_and_provenance(tmp_path):
    """The written GeoJSON carries processed_tiles (E72) and candidate_id."""
    bounds = _bounds()
    union = _union()
    point = {"prob_t": 0.2, "min_votes": 5}
    target = tmp_path / "detections.geojson"
    n = gva.materialise_condition(union, point, target, bounds)
    doc = json.loads(target.read_text())
    assert doc["processed_tiles"] == sorted([TILE_1, TILE_2])
    assert n == 2
    # candidate_id is the union feature index — rows 0 and 2 survive the
    # (prob >= 0.2, votes >= 5) filter.
    assert [f["properties"]["candidate_id"] for f in doc["features"]] == [0, 2]
    assert all("vote_count" in f["properties"] for f in doc["features"])


def _smoke_tree(root: Path, monkeypatch) -> dict:
    """Build a full synthetic verifier tree and patch the module constants.

    Four cells share one 2-tile carrier and one reference mound. Probability
    files are written in reversed key order (async-completion realism). The
    committed-sweep anchor rows are computed by scoring the synthetic sets
    with the module's own scorer, so every gate passes by construction.
    """
    bounds = _bounds()
    refs = _refs()
    bounds_path = root / "grid_common_bounds.geojson"
    refs_path = root / "mounds-reference.geojson"
    bounds.to_file(bounds_path, driver="GeoJSON")
    refs.to_file(refs_path, driver="GeoJSON")

    verifier_dir = root / "verifier"
    baseline_dir = root / "conditions"
    cells = list(gva.CELL_ORDER)
    expected = {}
    sweep_rows = []
    for cell in cells:
        union = _union()
        union4326 = union.to_crs("EPSG:4326")
        cell_dir = verifier_dir / cell
        (cell_dir / "verify").mkdir(parents=True)
        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [g.x, g.y]},
                "properties": {"vote_count": int(v), "source_tile": t},
            }
            for g, v, t in zip(union4326.geometry, union4326["vote_count"],
                               union4326["source_tile"], strict=True)
        ]
        (cell_dir / "union_k10.geojson").write_text(json.dumps(
            {"type": "FeatureCollection", "features": features}))
        probs = {f"candidate_{i:05d}": p
                 for i, p in enumerate(union["mound_probability"])}
        scrambled = dict(reversed(list(probs.items())))
        (cell_dir / "verify" / "probabilities.json").write_text(json.dumps(
            {"results": {k: {"mound_probability": v}
                         for k, v in scrambled.items()}}))
        (cell_dir / "verify" / "run.meta.json").write_text(json.dumps({
            "cost_estimate": {"list_total_cost_usd": 2.0, "cost_basis": "list"},
            "usage_stats": {"total_input_tokens": 100,
                            "total_output_tokens": 10},
            "execution_stats": {"items_processed": 3, "items_failed": 0,
                                "retries_total": 1},
        }))
        expected[cell] = 3

        union_row = gva.score(union, refs, bounds)
        union_row.update({"cell": cell, "K": 10, "min_corroboration": 1,
                          "min_votes": 1})
        # The registered K = 10 best consensus point: the true positive alone.
        base = union[union["vote_count"] >= 10].copy()
        (baseline_dir / cell).mkdir(parents=True)
        base_row = gva.score(base, refs, bounds)
        base_row.update({"cell": cell, "K": 10, "min_corroboration": 1,
                         "min_votes": 8})
        base.to_file(baseline_dir / cell / "detections.geojson",
                     driver="GeoJSON")
        # A decoy K = 3 row with a higher F1: the comparator board must
        # ignore it (only K = 10 rows may compete).
        decoy = dict(base_row)
        decoy.update({"K": 3, "f1": base_row["f1"] + 0.5, "min_votes": 3})
        sweep_rows.extend([union_row, base_row, decoy])

    grid_analysis_path = root / "grid_analysis.json"
    grid_analysis_path.write_text(json.dumps({"sweep": sweep_rows}))

    monkeypatch.setattr(gva, "VERIFIER_DIR", verifier_dir)
    monkeypatch.setattr(gva, "COMMON_BOUNDS", bounds_path)
    monkeypatch.setattr(gva, "GRID_ANALYSIS", grid_analysis_path)
    monkeypatch.setattr(gva, "GROUND_TRUTH", refs_path)
    monkeypatch.setattr(gva, "CONSENSUS_CONDITIONS_DIR", baseline_dir)
    monkeypatch.setattr(gva, "EXPECTED", expected)
    return {"cells": cells}


@pytest.mark.tier1
def test_main_smoke_wires_gates_boards_baseline_and_billing(tmp_path, monkeypatch):
    """End-to-end main() on a synthetic tree: the wiring, not just helpers.

    Pins: the reassignment gate is actually CALLED per cell; the comparator
    board only admits K = 10 rows (a higher-F1 K = 3 decoy is present); the
    like-for-like baseline contrasts are computed; billing derives from the
    metas (flex = list / 2); and the verified board rows declare their c = 1
    restriction.
    """
    _smoke_tree(tmp_path, monkeypatch)

    calls = {"reassign": 0}
    real_gate = gva.reassignment_gate

    def counting_gate(gdf, bounds, cell):
        calls["reassign"] += 1
        return real_gate(gdf, bounds, cell)

    monkeypatch.setattr(gva, "reassignment_gate", counting_gate)
    out_dir = tmp_path / "out"
    monkeypatch.setattr(
        "sys.argv",
        ["grid_verifier_analysis.py", "--output-dir", str(out_dir),
         "--bootstrap", "50"])
    assert gva.main() == 0
    assert calls["reassign"] == 4

    payload = json.loads((out_dir / "verifier_analysis.json").read_text())
    assert payload["gates"]["union_counts_measured"] == {
        c: 3 for c in gva.CELL_ORDER}
    for cell, row in payload["board_best"].items():
        assert row["min_corroboration"] == 1
    for cell, row in payload["board_consensus_only_committed"].items():
        # The K = 3 decoy carries a higher F1; only K = 10 rows may compete.
        assert row["K"] == 10
    assert set(payload["bootstrap_contrasts_consensus_k10_baseline"]) == set(
        payload["bootstrap_contrasts"])
    bill = payload["billing"]
    assert bill["total_list_usd"] == 8.0
    assert bill["total_flex_usd"] == 4.0
    assert bill["flex_per_call_usd"] == round(4.0 / 12, 6)
    assert bill["total_requests_incl_retries"] == 16
    assert payload["verifier"]["failures"] == 0
    assert payload["verifier"]["retries_transient"] == 4
    assert (out_dir / "verifier_sweep.csv").exists()


@pytest.mark.tier1
def test_infer_tile_size_measured_is_authoritative(tmp_path):
    """The tiles' measured dimensions win; --tile-size only asserts.

    S142 stride-run incident (2026-08-25): a trusted-but-wrong tile_size
    corrupts coordinate conversion by 300-500 m. The contract is now:
    infer from the tile, error on explicit contradiction, error on
    non-square.
    """
    import importlib.util

    from PIL import Image

    spec = importlib.util.spec_from_file_location(
        "detect_mounds_batch",
        Path(__file__).resolve().parent.parent / "scripts/4_detect_mounds_batch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    infer_tile_size = mod.infer_tile_size

    tile = tmp_path / "m1_x0_y0.png"
    Image.new("L", (384, 384)).save(tile)
    assert infer_tile_size(tile) == 384
    assert infer_tile_size(tile, 384) == 384
    with pytest.raises(ValueError, match="contradicts the measured 384"):
        infer_tile_size(tile, 512)
    rect = tmp_path / "m1_x0_y1.png"
    Image.new("L", (384, 256)).save(rect)
    with pytest.raises(ValueError, match="Non-square"):
        infer_tile_size(rect)
