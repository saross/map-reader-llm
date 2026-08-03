"""
Tier 1 tests for ``scripts.paired_mcc_permutation``.

Background
----------
``results/e43-matched-temperature/findings.md`` § 11.2 reported that
tile-level Matthews Correlation Coefficient (MCC) separates the matched
T=0.7 and T=1.0 temperature arms with non-overlapping bias-corrected and
accelerated (BCa) 95 % bootstrap intervals, and flagged that comparison as
UNPAIRED. ``scripts/paired_mcc_permutation.py`` supplies the paired test.

Two properties have to hold for its output to be trustworthy:

1. **The permutation behaves like a paired test.** Two identical arms must
   produce a null result (ΔMCC exactly zero, p = 1); two arms that disagree
   on every discordant tile in one direction must produce a small p.
2. **The per-tile labels are the house labels.** The script must reproduce
   ``lib_advanced_metrics.calculate_tile_classification``'s confusion cells
   exactly, and its hard gate must refuse to test an arm whose recomputed
   cells disagree with the cells recorded in that cell's ``evaluation.json``.
   A silent disagreement would mean the p-value and the published MCC table
   describe different data.

Test layers
-----------
1. Synthetic-fixture geometry helpers (no filesystem or network beyond
   ``tmp_path``).
2. Confusion-cell reproduction — the "mirror" requirement, asserted against
   ``calculate_tile_classification`` itself.
3. Gate behaviour — passes on agreement, raises on each kind of
   disagreement (cells, MCC, detection count, missing reference).
4. Permutation behaviour — identical arms, disjoint arms, seed determinism,
   and buffer invariance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.lib_advanced_metrics import (  # noqa: E402
    calculate_tile_classification,
)
from scripts.paired_mcc_permutation import (  # noqa: E402
    ConfusionGateError,
    aggregate_confusion,
    check_confusion_gate,
    expected_from_evaluation,
    load_detections,
    run_pair,
)

TEST_CRS = "EPSG:32635"
TILE_SIZE_M = 100.0
N_MOUND_TILES = 20
N_EMPTY_TILES = 20
N_TILES = N_MOUND_TILES + N_EMPTY_TILES


# =============================================================================
# Synthetic fixtures
# =============================================================================

def _tile_name(index: int) -> str:
    """Return the canonical fixture tile name for a tile index."""
    return f"tile_{index:03d}"


def _tile_centre(index: int) -> Point:
    """Return a point at the centre of fixture tile ``index``."""
    return Point(index * TILE_SIZE_M + TILE_SIZE_M / 2, TILE_SIZE_M / 2)


@pytest.fixture
def gdf_bounds() -> gpd.GeoDataFrame:
    """Forty non-overlapping 100 m square tiles laid out in a row.

    Non-overlapping is deliberate: it removes the first-match tie-break of
    the spatial join from the tests, so a failure points at the statistics
    rather than at geometry bookkeeping.
    """
    return gpd.GeoDataFrame(
        {"tile_name": [_tile_name(i) for i in range(N_TILES)]},
        geometry=[
            box(
                i * TILE_SIZE_M, 0.0,
                (i + 1) * TILE_SIZE_M, TILE_SIZE_M,
            )
            for i in range(N_TILES)
        ],
        crs=TEST_CRS,
    )


@pytest.fixture
def gdf_ref() -> gpd.GeoDataFrame:
    """One ground-truth mound in each of the first 20 tiles.

    Tiles 0–19 are therefore mound-bearing and tiles 20–39 are empty, which
    fixes the row sums of every confusion table the tests build.
    """
    return gpd.GeoDataFrame(
        {"mound_id": list(range(N_MOUND_TILES))},
        geometry=[_tile_centre(i) for i in range(N_MOUND_TILES)],
        crs=TEST_CRS,
    )


def _detections(tile_indices: list[int]) -> gpd.GeoDataFrame:
    """Build a detection GeoDataFrame with one detection per named tile.

    Args:
        tile_indices: Indices of the tiles to place a detection in.

    Returns:
        GeoDataFrame with a ``source_tile`` column already populated.
    """
    return gpd.GeoDataFrame(
        {"source_tile": [_tile_name(i) for i in tile_indices]},
        geometry=[_tile_centre(i) for i in tile_indices],
        crs=TEST_CRS,
    )


@pytest.fixture
def gdf_strong() -> gpd.GeoDataFrame:
    """A good arm: detects in all 20 mound tiles and 5 empty tiles.

    Confusion: TP 20, FN 0, FP 5, TN 15.
    """
    return _detections(list(range(0, 20)) + list(range(20, 25)))


@pytest.fixture
def gdf_weak() -> gpd.GeoDataFrame:
    """A bad arm: detects in no mound tile and 15 empty tiles.

    Confusion: TP 0, FN 20, FP 15, TN 5. Paired against ``gdf_strong`` this
    is the maximally discordant design the fixture allows — the two arms
    disagree on all 40 tiles, with 35 favouring the strong arm and 5 (the
    empty tiles the strong arm hallucinates into) favouring the weak one.
    """
    return _detections(list(range(25, 40)))


def _write_evaluation(path: Path, confusion: dict, mcc: float, n_det: int) -> Path:
    """Write a minimal ``evaluation.json`` usable as a gate reference.

    Args:
        path: Destination file path.
        confusion: Dict with ``tp``, ``tn``, ``fp``, ``fn``.
        mcc: MCC point estimate, as ``evaluate_detections.py`` would round it.
        n_det: Recorded detection count.

    Returns:
        The path written, for convenient chaining.
    """
    payload = {
        "summary": {
            "n_detections": n_det,
            "tile_classification": {
                "confusion": confusion,
                "mcc": {"point": mcc},
            },
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# =============================================================================
# 1. Confusion-cell reproduction — the "mirror" requirement
# =============================================================================

@pytest.mark.tier1
def test_aggregate_confusion_mirrors_house_tile_classification(
    gdf_strong, gdf_ref, gdf_bounds,
):
    """Aggregated per-tile labels must equal ``calculate_tile_classification``.

    This is the property the production gate relies on: if it ever fails, the
    permutation test would be permuting labels the published MCC table does
    not recognise.
    """
    house = calculate_tile_classification(gdf_strong, gdf_ref, gdf_bounds)
    ours = aggregate_confusion(gdf_strong, gdf_ref, gdf_bounds)

    for cell in ("tp", "tn", "fp", "fn"):
        assert ours[cell] == house[cell], f"{cell} disagrees with the house"
    assert ours["n_tiles"] == N_TILES
    assert ours["mcc"] == pytest.approx(house["mcc"], abs=1e-12)


@pytest.mark.tier1
def test_confusion_cells_match_fixture_design(gdf_strong, gdf_weak, gdf_ref, gdf_bounds):
    """The fixtures produce the confusion tables their docstrings claim."""
    strong = aggregate_confusion(gdf_strong, gdf_ref, gdf_bounds)
    assert (strong["tp"], strong["fn"], strong["fp"], strong["tn"]) == (20, 0, 5, 15)

    weak = aggregate_confusion(gdf_weak, gdf_ref, gdf_bounds)
    assert (weak["tp"], weak["fn"], weak["fp"], weak["tn"]) == (0, 20, 15, 5)

    # Row sums are fixed by the shared ground truth, which is what makes the
    # comparison paired: both arms are scored over the same 20 mound-bearing
    # and 20 empty tiles.
    assert strong["tp"] + strong["fn"] == weak["tp"] + weak["fn"] == N_MOUND_TILES
    assert strong["tn"] + strong["fp"] == weak["tn"] + weak["fp"] == N_EMPTY_TILES


@pytest.mark.tier1
def test_load_detections_assigns_source_tile_by_spatial_join(
    tmp_path, gdf_ref, gdf_bounds,
):
    """A GeoJSON without ``source_tile`` gets one by spatial join.

    Consensus artefacts carry a plural ``source_tiles`` list and no singular
    ``source_tile``, so this join is the production path.
    """
    raw = _detections([0, 1, 21]).drop(columns=["source_tile"])
    path = tmp_path / "detections.geojson"
    raw.to_file(path, driver="GeoJSON")

    loaded = load_detections(path, gdf_bounds)

    assert "source_tile" in loaded.columns
    assert set(loaded["source_tile"]) == {
        _tile_name(0), _tile_name(1), _tile_name(21),
    }
    cells = aggregate_confusion(loaded, gdf_ref, gdf_bounds)
    assert (cells["tp"], cells["fp"]) == (2, 1)


# =============================================================================
# 2. The hard gate
# =============================================================================

@pytest.mark.tier1
def test_gate_passes_on_agreement(gdf_strong, gdf_ref, gdf_bounds, tmp_path):
    """A faithful reference passes all three checks."""
    observed = aggregate_confusion(gdf_strong, gdf_ref, gdf_bounds)
    eval_path = _write_evaluation(
        tmp_path / "evaluation.json",
        {"tp": 20, "tn": 15, "fp": 5, "fn": 0},
        round(observed["mcc"], 4),
        len(gdf_strong),
    )
    record = check_confusion_gate(
        observed, expected_from_evaluation(eval_path),
        "strong arm", n_detections=len(gdf_strong),
    )
    assert record["confusion_matched"] is True
    assert record["mcc_matched"] is True
    assert record["n_detections_matched"] is True


@pytest.mark.tier1
@pytest.mark.parametrize(
    ("mutation", "fragment"),
    [
        ({"tp": 19}, "TP"),
        ({"tn": 14}, "TN"),
        ({"fp": 6}, "FP"),
        ({"fn": 1}, "FN"),
    ],
)
def test_gate_raises_on_any_wrong_confusion_cell(
    gdf_strong, gdf_ref, gdf_bounds, tmp_path, mutation, fragment,
):
    """Each of the four cells is checked, and any disagreement is fatal."""
    observed = aggregate_confusion(gdf_strong, gdf_ref, gdf_bounds)
    confusion = {"tp": 20, "tn": 15, "fp": 5, "fn": 0} | mutation
    eval_path = _write_evaluation(
        tmp_path / "evaluation.json", confusion,
        round(observed["mcc"], 4), len(gdf_strong),
    )
    with pytest.raises(ConfusionGateError, match=fragment):
        check_confusion_gate(
            observed, expected_from_evaluation(eval_path), "strong arm",
        )


@pytest.mark.tier1
def test_gate_raises_on_wrong_mcc(gdf_strong, gdf_ref, gdf_bounds, tmp_path):
    """Matching cells with a mismatched recorded MCC still fails the gate."""
    observed = aggregate_confusion(gdf_strong, gdf_ref, gdf_bounds)
    eval_path = _write_evaluation(
        tmp_path / "evaluation.json",
        {"tp": 20, "tn": 15, "fp": 5, "fn": 0},
        round(observed["mcc"] + 0.01, 4),
        len(gdf_strong),
    )
    with pytest.raises(ConfusionGateError, match="MCC"):
        check_confusion_gate(
            observed, expected_from_evaluation(eval_path), "strong arm",
        )


@pytest.mark.tier1
def test_gate_raises_on_detection_count_mismatch(
    gdf_strong, gdf_ref, gdf_bounds, tmp_path,
):
    """A feature count that disagrees with the evaluation means wrong source.

    This is the cross-check that caught three wrong-source errors
    retrospectively in an earlier session: identical confusion cells do not
    prove the GeoJSON under test is the one the evaluation scored.
    """
    observed = aggregate_confusion(gdf_strong, gdf_ref, gdf_bounds)
    eval_path = _write_evaluation(
        tmp_path / "evaluation.json",
        {"tp": 20, "tn": 15, "fp": 5, "fn": 0},
        round(observed["mcc"], 4),
        len(gdf_strong) + 7,
    )
    with pytest.raises(ConfusionGateError, match="n_detections"):
        check_confusion_gate(
            observed, expected_from_evaluation(eval_path), "strong arm",
            n_detections=len(gdf_strong),
        )


@pytest.mark.tier1
def test_expected_from_evaluation_rejects_a_file_without_mcc(tmp_path):
    """An evaluation scored without ``--mcc`` cannot serve as a gate."""
    path = tmp_path / "evaluation.json"
    path.write_text(json.dumps({"summary": {"n_detections": 5}}), encoding="utf-8")
    with pytest.raises(ConfusionGateError, match="tile_classification"):
        expected_from_evaluation(path)


@pytest.mark.tier1
def test_run_pair_refuses_an_ungated_arm(
    tmp_path, gdf_strong, gdf_weak, gdf_ref, gdf_bounds,
):
    """The gate is mandatory: a job with no reference is refused, not skipped."""
    path_a = tmp_path / "a.geojson"
    path_b = tmp_path / "b.geojson"
    gdf_strong.to_file(path_a, driver="GeoJSON")
    gdf_weak.to_file(path_b, driver="GeoJSON")

    job = {
        "pair_id": "ungated", "label_a": "A", "geojson_a": str(path_a),
        "label_b": "B", "geojson_b": str(path_b),
    }
    with pytest.raises(ConfusionGateError, match="mandatory"):
        run_pair(job, gdf_ref, gdf_bounds, n_permutations=10)


# =============================================================================
# 3. Permutation behaviour
# =============================================================================

def _pair_job(tmp_path, gdf_a, gdf_b, gdf_ref, gdf_bounds, pair_id="pair"):
    """Write two arms to disk with faithful gate references and build a job."""
    jobs = {}
    for suffix, gdf in (("a", gdf_a), ("b", gdf_b)):
        geo_path = tmp_path / f"{pair_id}_{suffix}.geojson"
        gdf.to_file(geo_path, driver="GeoJSON")
        cells = aggregate_confusion(gdf, gdf_ref, gdf_bounds)
        eval_path = _write_evaluation(
            tmp_path / f"{pair_id}_{suffix}_evaluation.json",
            {k: cells[k] for k in ("tp", "tn", "fp", "fn")},
            round(cells["mcc"], 4), len(gdf),
        )
        jobs[f"geojson_{suffix}"] = str(geo_path)
        jobs[f"expect_{suffix}"] = [str(eval_path)]
        jobs[f"label_{suffix}"] = suffix.upper()
    jobs["pair_id"] = pair_id
    return jobs


@pytest.mark.tier1
def test_identical_arms_give_zero_delta_and_p_one(
    tmp_path, gdf_strong, gdf_ref, gdf_bounds,
):
    """Two identical arms: ΔMCC is exactly zero and p is 1.

    Every tile is concordant, so every permutation is a no-op and the whole
    null distribution collapses onto zero. Any p below 1 would mean the null
    is not respecting the pairing.
    """
    job = _pair_job(
        tmp_path, gdf_strong, gdf_strong.copy(), gdf_ref, gdf_bounds, "identical",
    )
    result = run_pair(job, gdf_ref, gdf_bounds, n_permutations=1000, seed=42)

    assert result["observed_mcc_diff"] == pytest.approx(0.0, abs=1e-12)
    assert result["permutation_test"]["p_value"] == pytest.approx(1.0)
    assert result["permutation_test"]["wins_a"] == 0
    assert result["permutation_test"]["losses_a"] == 0
    assert result["permutation_test"]["ties"] == N_TILES
    assert result["permutation_test"]["null_distribution"]["std"] == pytest.approx(0.0)


@pytest.mark.tier1
def test_disjoint_arms_give_a_small_p(
    tmp_path, gdf_strong, gdf_weak, gdf_ref, gdf_bounds,
):
    """Maximally discordant arms: large positive ΔMCC and p < 0.01.

    Every one of the 40 tiles is discordant (no ties), and the split is
    lopsided: the strong arm is the correct one on the 20 mound tiles and on
    the 15 empty tiles it leaves alone (35 wins), the weak arm only on the 5
    empty tiles the strong arm hallucinates into (5 losses). A sign-flip null
    over 40 discordant tiles cannot reach a 35/5 split by chance at these
    odds, so p must be small.
    """
    job = _pair_job(
        tmp_path, gdf_strong, gdf_weak, gdf_ref, gdf_bounds, "disjoint",
    )
    result = run_pair(job, gdf_ref, gdf_bounds, n_permutations=10_000, seed=42)

    assert result["arm_a"]["mcc"] > result["arm_b"]["mcc"]
    assert result["observed_mcc_diff"] > 0.5
    assert result["permutation_test"]["p_value"] < 0.01
    assert result["permutation_test"]["wins_a"] == 35
    assert result["permutation_test"]["losses_a"] == 5
    assert result["permutation_test"]["ties"] == 0


@pytest.mark.tier1
def test_permutation_is_deterministic_under_a_fixed_seed(
    tmp_path, gdf_strong, gdf_weak, gdf_ref, gdf_bounds,
):
    """The same seed reproduces the same p-value; a different seed need not."""
    job = _pair_job(tmp_path, gdf_strong, gdf_weak, gdf_ref, gdf_bounds, "seeded")
    first = run_pair(job, gdf_ref, gdf_bounds, n_permutations=2000, seed=42)
    second = run_pair(job, gdf_ref, gdf_bounds, n_permutations=2000, seed=42)
    assert (
        first["permutation_test"]["p_value"]
        == second["permutation_test"]["p_value"]
    )
    assert (
        first["permutation_test"]["null_distribution"]["std"]
        == second["permutation_test"]["null_distribution"]["std"]
    )


@pytest.mark.tier1
def test_dry_run_gates_without_permuting(
    tmp_path, gdf_strong, gdf_weak, gdf_ref, gdf_bounds,
):
    """``permute=False`` still gates and still reports the observed ΔMCC."""
    job = _pair_job(tmp_path, gdf_strong, gdf_weak, gdf_ref, gdf_bounds, "dry")
    result = run_pair(job, gdf_ref, gdf_bounds, permute=False)

    assert result["permutation_test"] is None
    assert result["observed_mcc_diff"] > 0.5
    assert result["arm_a"]["gate"][0]["confusion_matched"] is True


@pytest.mark.tier1
def test_delta_is_invariant_to_ground_truth_buffering(
    tmp_path, gdf_strong, gdf_weak, gdf_ref, gdf_bounds,
):
    """Tile-level MCC uses no spatial tolerance, so ΔMCC is buffer-invariant.

    Growing every ground-truth mound into a 10 m disc — a stand-in for a
    matching buffer — leaves each tile's mound-bearing flag unchanged, hence
    leaves every confusion cell and the ΔMCC unchanged. This is why the
    commissioned "20 m and 30 m" ΔMCC values are one number, not two.
    """
    job = _pair_job(tmp_path, gdf_strong, gdf_weak, gdf_ref, gdf_bounds, "buffer")
    unbuffered = run_pair(job, gdf_ref, gdf_bounds, n_permutations=1000, seed=42)

    gdf_ref_buffered = gdf_ref.copy()
    gdf_ref_buffered["geometry"] = gdf_ref_buffered.geometry.buffer(10.0)
    buffered = run_pair(
        job, gdf_ref_buffered, gdf_bounds, n_permutations=1000, seed=42,
    )

    assert (
        buffered["observed_mcc_diff"] == unbuffered["observed_mcc_diff"]
    )
    assert (
        buffered["permutation_test"]["p_value"]
        == unbuffered["permutation_test"]["p_value"]
    )
