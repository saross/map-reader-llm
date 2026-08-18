"""
Tier 1 tests for the Session 136 deduplication metric-impact tooling.

Three properties carry the whole argument of
``results/dedup-metric-impact-2026-08-18/findings.md`` and are pinned here:

1. ``tile_confusion`` must agree with the committed scorer's own
   ``lib_advanced_metrics.calculate_tile_classification`` on the same inputs.
   The fast path replaces a per-tile geometry loop with set arithmetic, so if
   the two ever diverge, every reported Matthews Correlation Coefficient (MCC)
   movement becomes unverifiable.
2. ``dedup_with_provenance`` must attribute a deduplicated cluster to the
   lexicographically first contributing tile in ``source_tile`` while retaining
   the full contributing-tile list — the union of those lists is what makes the
   membership-preserving MCC rule exactly invariant, which is the finding's
   interpretive anchor.
3. ``resolve_from_manifest`` must expand a pass directory with BOTH pass-file
   naming conventions. Expanding with one alone is the defect that caused the
   Session 136 exposure survey to score
   ``pv-diag-384::baseline-pro-text-medium-t-0-0`` — a Tier-1 tie member — on 1
   of its 3 passes.

All tests use synthetic in-memory geometry and a tmp_path manifest; no network,
no committed artefacts, no API calls.
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

from scripts.dedup_metric_impact import (  # noqa: E402
    dedup_with_provenance,
    populated_tiles,
    resolve_from_manifest,
    tile_confusion,
)
from scripts.lib_advanced_metrics import (  # noqa: E402
    calculate_tile_classification,
)

CRS = "EPSG:32635"


def _bounds() -> gpd.GeoDataFrame:
    """Four 100 m tiles in a row, named as one map sheet.

    Returns:
        Tile bounds in the evaluation CRS.
    """
    return gpd.GeoDataFrame(
        {"tile_name": [f"MAP-A_r0_c{i}" for i in range(4)]},
        geometry=[box(i * 100, 0, i * 100 + 100, 100) for i in range(4)],
        crs=CRS,
    )


def _refs(xs: list[float]) -> gpd.GeoDataFrame:
    """Reference mounds at the given x positions, y = 50.

    Args:
        xs: Easting values in metres.

    Returns:
        Reference points with the ``Map`` column the scorer requires.
    """
    return gpd.GeoDataFrame(
        {"Map": ["MAP-A"] * len(xs)},
        geometry=[Point(x, 50) for x in xs],
        crs=CRS,
    )


def _dets(items: list[tuple[float, str]]) -> gpd.GeoDataFrame:
    """Detections at the given (x, source_tile) positions, y = 50.

    Args:
        items: Pairs of easting and source tile name.

    Returns:
        Detections in the evaluation CRS.
    """
    return gpd.GeoDataFrame(
        {"source_tile": [t for _, t in items], "subtype": ["mound"] * len(items)},
        geometry=[Point(x, 50) for x, _ in items],
        crs=CRS,
    )


# --------------------------------------------------------------------------- #
# 1. tile_confusion agrees with the committed scorer
# --------------------------------------------------------------------------- #

@pytest.mark.tier1
def test_tile_confusion_matches_calculate_tile_classification():
    """The fast set-based confusion must equal the committed per-tile loop."""
    bounds = _bounds()
    refs = _refs([50, 150])          # populates tiles c0 and c1
    dets = _dets([(50, "MAP-A_r0_c0"), (250, "MAP-A_r0_c2")])

    order, populated = populated_tiles(refs, bounds)
    fast = tile_confusion(set(dets["source_tile"]), order, populated)
    slow = calculate_tile_classification(dets, refs, bounds)

    for key in ("tp", "tn", "fp", "fn"):
        assert fast[key] == slow[key], key
    assert fast["mcc"] == pytest.approx(slow["mcc"], abs=1e-6)


@pytest.mark.tier1
def test_tile_confusion_is_degenerate_safe():
    """A confusion matrix with a zero row/column returns ``None``, not a crash.

    ``calculate_tile_classification`` returns ``None`` for an undefined MCC;
    the fast path must do the same rather than divide by zero.
    """
    bounds = _bounds()
    refs = _refs([50, 150, 250, 350])   # every tile populated -> tn + fp == 0
    order, populated = populated_tiles(refs, bounds)
    result = tile_confusion(set(order), order, populated)
    assert result["mcc"] is None
    assert result["tn"] == 0 and result["fp"] == 0


# --------------------------------------------------------------------------- #
# 2. dedup_with_provenance — attribution and the membership-preserving union
# --------------------------------------------------------------------------- #

@pytest.mark.tier1
def test_dedup_collapses_a_cross_tile_pair_and_keeps_both_tiles():
    """Two copies 10 m apart from adjacent tiles collapse to one cluster.

    The surviving cluster must take the lexicographically first contributing
    tile as its ``source_tile`` while both tiles remain in the returned
    contributing list — the two facts that make the first-source-tile MCC move
    and the union-contributing MCC stay put.
    """
    bounds = _bounds()
    dets = _dets([(105, "MAP-A_r0_c1"), (95, "MAP-A_r0_c0")])

    dedup, contributing, stats = dedup_with_provenance(dets, bounds)

    assert stats["n_raw"] == 2
    assert stats["n_dedup"] == 1
    assert stats["n_removed"] == 1
    assert stats["n_clusters_spanning_multiple_tiles"] == 1
    assert stats["n_clusters_spanning_multiple_map_sheets"] == 0
    assert contributing == [["MAP-A_r0_c0", "MAP-A_r0_c1"]]
    assert dedup["source_tile"].tolist() == ["MAP-A_r0_c0"]


@pytest.mark.tier1
def test_union_contributing_mcc_is_invariant_but_first_tile_mcc_is_not():
    """The finding's anchor: attribution, not false-positive removal, moves MCC.

    With a reference mound in each of two adjacent tiles and a duplicate pair
    straddling them, collapsing the pair empties one populated tile under the
    first-source-tile rule (turning a true positive tile into a false negative),
    while the membership-preserving union rule leaves the confusion matrix
    untouched.
    """
    bounds = _bounds()
    refs = _refs([95, 105])
    dets = _dets([(105, "MAP-A_r0_c1"), (95, "MAP-A_r0_c0")])
    order, populated = populated_tiles(refs, bounds)

    committed = tile_confusion(set(dets["source_tile"]), order, populated)
    dedup, contributing, _ = dedup_with_provenance(dets, bounds)
    first = tile_confusion(set(dedup["source_tile"]), order, populated)
    union = tile_confusion(
        {t for tiles in contributing for t in tiles}, order, populated
    )

    assert union == committed
    assert first["tp"] == committed["tp"] - 1
    assert first["fn"] == committed["fn"] + 1
    assert first["mcc"] < committed["mcc"]


# --------------------------------------------------------------------------- #
# 3. resolve_from_manifest — both pass-file naming conventions
# --------------------------------------------------------------------------- #

@pytest.mark.tier1
def test_resolve_from_manifest_unions_both_pass_globs(tmp_path, monkeypatch):
    """A directory holding both naming conventions must resolve every pass.

    The evaluation record states the CLI default glob
    (``*/detections_*.geojson``); run_2 is named with a hyphen. Resolving with
    the recorded glob alone would silently return 1 of 2 passes.
    """
    pool = tmp_path / "pool"
    (pool / "run_1").mkdir(parents=True)
    (pool / "run_2").mkdir(parents=True)
    (pool / "run_1" / "detections_text_run01.geojson").write_text("{}")
    (pool / "run_2" / "detections-detect-brief-text.geojson").write_text("{}")

    eval_path = tmp_path / "evaluation.json"
    eval_path.write_text(json.dumps({
        "summary": {"n_runs": 2, "buffers": []},
        "per_run": [{"label": "a"}, {"label": "b"}],
        "_metadata": {
            "cli_args": {"glob": "*/detections_*.geojson"},
            "input_files": {
                "detections": str(pool),
                "bounds": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
            },
        },
    }))

    manifest_index = {
        "run::cell": {
            "condition_id": "run::cell",
            "provenance": {"source_files": [str(eval_path)]},
        }
    }
    monkeypatch.chdir(tmp_path)
    found = resolve_from_manifest("run::cell", manifest_index)

    assert len(found["detections"]) == 2
    assert found["n_runs_expected"] == 2
    assert found["bounds"].endswith("full_evaluation_bounds.geojson")
