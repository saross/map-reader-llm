"""
Tier-1 tests for the pure logic of ``scripts/im_june_pool_grid.py``.

The script's measurement is gated at run time against the committed IM-k3
evaluation, which is a stronger check than a fixture could be and needs the
real reference frames. What is tested here is the logic no committed artefact
would catch: that the grid covers only the vote thresholds the June verifier
actually saw, that the carried point is forced into the ladder, that a cell
spec resolves to the operating point the grid records, that the reproduction
gate is a two-sided tolerance on both metrics, and that the CSV columns are
the 2x2 sweep file's own.
"""

from __future__ import annotations

import csv
import json
from unittest.mock import patch

import geopandas as gpd
import pytest
from shapely.geometry import Point

from scripts import im_june_pool_grid as june
from scripts.im_june_pool_grid import (
    CARRIED,
    COMMITTED_IM_K3,
    CSV_FIELDS,
    GATE_TOL,
    MIN_VOTES,
    PROJECT_ROOT,
    _gate_verdict,
    achievable_points,
    resolve_cell_points,
)

pytestmark = pytest.mark.tier1


@pytest.fixture
def frame() -> gpd.GeoDataFrame:
    """Four candidates spanning three probabilities and the three vote counts."""
    rows = [(1.0, 5), (0.35, 4), (0.35, 3), (0.05, 3)]
    return gpd.GeoDataFrame(
        {
            "mound_probability": [p for p, _ in rows],
            "vote_count": [v for _, v in rows],
            "source_tile": ["t.png"] * len(rows),
        },
        geometry=[Point(400000 + i, 4700000) for i in range(len(rows))],
        crs="EPSG:32635",
    )


def test_the_ladder_is_zero_plus_observed_probabilities(
    frame: gpd.GeoDataFrame,
) -> None:
    """The probability axis is the board's achievable ladder, not a lattice."""
    probs = sorted({p for p, _ in achievable_points(frame)})
    assert probs == [0.0, 0.05, 0.15, 0.35, 1.0], (
        "zero, the three observed values, and the forced carried threshold")


def test_the_grid_never_sweeps_an_unverified_vote_threshold(
    frame: gpd.GeoDataFrame,
) -> None:
    """Votes 1 and 2 were never verified in June, so they cannot be scored."""
    votes = sorted({v for _, v in achievable_points(frame)})
    assert votes == list(MIN_VOTES) == [3, 4, 5]


def test_the_carried_point_is_forced_into_the_ladder(
    frame: gpd.GeoDataFrame,
) -> None:
    """0.15 is not an observed probability here, but IM-k3's point must be swept."""
    assert 0.15 not in set(frame["mound_probability"])
    assert CARRIED in achievable_points(frame)


def test_forcing_is_idempotent_when_the_point_is_already_reachable() -> None:
    """A pool that happens to observe 0.15 gains no duplicate row."""
    reachable = gpd.GeoDataFrame(
        {"mound_probability": [0.15], "vote_count": [3], "source_tile": ["t.png"]},
        geometry=[Point(400000, 4700000)], crs="EPSG:32635")
    points = achievable_points(reachable)
    assert points.count(CARRIED) == 1
    assert len(points) == len(set(points))


def _grid(f1_p: float, mcc_p: float, k5_f1_p: float) -> dict:
    """A minimal sweep record carrying both argmaxes per vote count."""
    return {"per_min_votes": {
        "3": {"f1_oracle": {"prob_t": f1_p}, "mcc_argmax": {"prob_t": mcc_p}},
        "4": {"f1_oracle": {"prob_t": 0.5}, "mcc_argmax": {"prob_t": 0.5}},
        "5": {"f1_oracle": {"prob_t": k5_f1_p}, "mcc_argmax": {"prob_t": 0.9}},
    }}


def test_cell_specs_resolve_to_the_grid_s_own_oracles() -> None:
    """An oracle cell reads its threshold from the sweep, not from a constant."""
    cells = {c["label"]: c for c in resolve_cell_points(_grid(0.35, 0.65, 0.05))}
    assert cells["IM-5pass-k3-f1-oracle"]["prob_t"] == 0.35
    assert cells["IM-5pass-k5-f1-oracle"]["prob_t"] == 0.05
    assert {c["min_votes"] for c in cells.values()} == {3, 5}


def test_no_mcc_oracle_cell_is_materialised() -> None:
    """PI ruling 2026-09-21: the tile-MCC argmax is recorded, never a cell.

    The record still carries ``mcc_argmax`` per vote count (it is data the
    tile-presence presentation reads), but no spec resolves to it, and a spec
    that asked for the retired basis would be refused rather than silently
    mapped onto the F1 oracle.
    """
    cells = resolve_cell_points(_grid(0.35, 0.65, 0.05))
    assert not [c for c in cells if "mcc" in c["label"] or "mcc" in c["basis"]]
    assert {c["basis"] for c in cells} == {"f1-oracle", "carried"}
    assert not any(c["prob_t"] == 0.65 for c in cells)
    with pytest.raises(ValueError, match="mcc-oracle"):
        with patch.object(june, "CELL_SPECS", (
                {"label": "IM-5pass-k3-mcc-oracle", "min_votes": 3,
                 "basis": "mcc-oracle"},)):
            resolve_cell_points(_grid(0.35, 0.65, 0.05))


def test_the_k5_carried_cell_is_fixed_and_ignores_the_grid() -> None:
    """IM-k3's probability read at unanimity is a stated point, not an oracle."""
    a = resolve_cell_points(_grid(0.35, 0.65, 0.05))
    b = resolve_cell_points(_grid(0.9, 0.9, 0.9))
    carried = [next(c for c in cells if c["label"] == "IM-5pass-k5-carried")
               for cells in (a, b)]
    assert [c["prob_t"] for c in carried] == [0.15, 0.15]
    assert [c["min_votes"] for c in carried] == [5, 5]


@pytest.mark.parametrize("d_f1,d_mcc,expected", [
    (0.0, 0.0, True),
    (GATE_TOL - 1e-6, GATE_TOL - 1e-6, True),
    (GATE_TOL + 1e-4, 0.0, False),
    (0.0, -(GATE_TOL + 1e-4), False),
    (-(GATE_TOL - 1e-6), GATE_TOL - 1e-6, True),
])
def test_the_reproduction_gate_is_two_sided_on_both_metrics(
    d_f1: float, d_mcc: float, expected: bool,
) -> None:
    """Either metric drifting past the tolerance, in either direction, fails."""
    row = {"micro_f1_50": COMMITTED_IM_K3["micro_f1_50"] + d_f1,
           "tile_mcc": COMMITTED_IM_K3["tile_mcc"] + d_mcc}
    assert _gate_verdict(row) is expected


def test_the_csv_columns_are_the_2x2_sweep_file_s_own() -> None:
    """The grid must concatenate with the rebuilt pool's sweep without reordering."""
    committed = (PROJECT_ROOT
                 / "results/gemini3-image-55map-2026-09-16/sweep_G3IMG-ARM1-K5.csv")
    with committed.open() as fh:
        header = next(csv.reader(fh))
    assert list(CSV_FIELDS) == header


# --- The retained cell: archive, never delete -------------------------------
#
# PI ruling 2026-09-21 retired the mcc-oracle basis, but the cell built under
# it stays on disk and in the manifest. The merge that keeps it, and the score
# stage's skip, are the whole guarantee, so both are pinned here.

def test_cell_specs_are_three_with_unique_labels() -> None:
    assert len(june.CELL_SPECS) == 3
    assert len({s["label"] for s in june.CELL_SPECS}) == 3
    assert june.produced_bases() == {"f1-oracle", "carried"}


def test_a_retained_entry_survives_a_manifest_rewrite_in_place(tmp_path) -> None:
    """A label this run did not produce is kept at its original position."""
    manifest = tmp_path / "cells_manifest.json"
    retired = {"label": "IM-5pass-k3-mcc-oracle", "basis": "mcc-oracle at carried k — "
               "retained, not presented (PI ruling 2026-09-21)", "presentation": "kept"}
    manifest.write_text(json.dumps({"cells": [
        {"label": "IM-5pass-k3-f1-oracle", "basis": "f1-oracle", "point": "(0.15, k3)"},
        retired,
        {"label": "IM-5pass-k5-carried", "basis": "carried", "point": "(0.15, k5)"},
    ]}))
    produced = [
        {"label": "IM-5pass-k3-f1-oracle", "basis": "f1-oracle", "point": "(0.20, k3)"},
        {"label": "IM-5pass-k5-carried", "basis": "carried", "point": "(0.15, k5)"},
        {"label": "IM-5pass-k5-f1-oracle", "basis": "f1-oracle", "point": "(0.15, k5)"},
    ]
    merged = june.write_cells_manifest(manifest, produced)
    on_disk = json.loads(manifest.read_text())
    assert on_disk["cells"] == merged
    assert [c["label"] for c in merged] == [
        "IM-5pass-k3-f1-oracle", "IM-5pass-k3-mcc-oracle",
        "IM-5pass-k5-carried", "IM-5pass-k5-f1-oracle"]
    assert merged[1] == retired                       # untouched, in place
    assert merged[0]["point"] == "(0.20, k3)"         # replaced in place
    assert on_disk["rung"] == june.RUNG


def test_a_manifest_without_cells_or_labels_is_tolerated(tmp_path) -> None:
    manifest = tmp_path / "cells_manifest.json"
    manifest.write_text(json.dumps({"cells": [{"basis": "carried"}, "junk"]}))
    merged = june.write_cells_manifest(manifest, [{"label": "a", "basis": "carried"}])
    assert [c["label"] for c in merged] == ["a"]
    manifest.write_text("{}")
    assert [c["label"] for c in june.write_cells_manifest(manifest, [])] == []


def test_the_score_stage_skips_the_retained_cell() -> None:
    assert june.is_retained({"label": "x", "basis": "mcc-oracle at carried k — retained"})
    assert june.is_retained({"label": "x"})
    assert not june.is_retained({"label": "x", "basis": "f1-oracle"})
    assert not june.is_retained({"label": "x", "basis": "carried"})
    committed = json.loads((june.RESULTS_HOME / "cells_manifest.json").read_text())
    assert [c["label"] for c in committed["cells"] if june.is_retained(c)] == [
        "IM-5pass-k3-mcc-oracle"]
