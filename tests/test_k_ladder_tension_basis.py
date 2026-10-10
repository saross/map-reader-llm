"""
Tier-1 tests: the K-ladder effect-size table never pairs a clipped F1 with
unclipped inference (PI ruling D51; Astra's re-review of PR #30, 2026-10-10).

``scripts/k_ladder_tension_analyses.py::cmd_effect_sizes`` reads each Phase 2
ladder's F1@20 from ``phase2/ladders.json`` and joins the permutation p-value
and tier count from ``phase2/mcc-test/summary.json`` by family. When the
Phase 2 builder (``scripts/build_k_ladder_phase2_tables.py`` v1.4.0) runs with
``--clip-to-common-area``, a clipped ladder's ``ladders.json`` reports clipped
F1 values, but the summary can only hold inference on the unclipped cells:
the compatibility export the instrument reads withholds every clipped ladder.
Before v1.1.0 the table paired the two silently.

The contract exercised here, on the builder's own written ``ladders.json``
(its CLI runs on the synthetic ladders of ``tests/test_assessed_area.py``):

* **clipped** — the row keeps the clipped F1 values and names the clipped
  ``score_basis``; ``p_bh``, ``n_tiers`` and ``one_tier``, and the bootstrap
  intervals and tile-MCC of the unclipped cells, are ``null`` and listed with
  their reasons under ``withheld``;
* **same area under a clip request** — the row is as evaluated, keeps its
  inference, and names that basis;
* **unclipped build** — nothing names a basis, so every row has exactly the
  v1.0.0 keys, in order, and the output carries no basis or withholding text;
* **markers** — the basis names the table reads are the builder's own.

No permutation or bootstrap runs: the summaries are tiny synthetic files.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import k_ladder_tension_analyses as tension  # noqa: E402
from tests import test_assessed_area as area  # noqa: E402

pytestmark = pytest.mark.tier1

# The builder's synthetic world and ladders (one the gate must clip, one whose
# rungs searched the same area), reused rather than rebuilt.
world = area.world
two_ladders = area.two_ladders

#: The two Phase 2 families; the table reads only MINIMAL ladders.
CLIPPED = "Gemini 3 MINIMAL text, clipped"
SAME = "Gemini 3 MINIMAL text, same area"

#: The fields an effect-size row had in v1.0.0, in order. An unclipped build
#: must produce exactly these, so its output keeps its bytes.
PHASE2_ROW_KEYS_V1_0 = [
    "corpus", "ladder", "buffer_m", "thinking", "modality", "temperature",
    "K_low", "K_best", "f1_low", "f1_best", "delta_f1", "f1_low_ci",
    "f1_best_ci", "tile_mcc_low", "tile_mcc_best", "p_bh", "n_tiers",
    "one_tier", "source",
]
PHASE1_ROW_KEYS_V1_0 = [
    "corpus", "ladder", "buffer_m", "thinking", "modality", "K_low", "K_best",
    "f1_low", "f1_best", "delta_f1", "tile_mcc_low", "tile_mcc_best", "p_bh",
    "source",
]

#: What a clipped row withholds: every field computed on the unclipped cells.
WITHHELD = {"p_bh", "n_tiers", "one_tier", "f1_low_ci", "f1_best_ci",
            "tile_mcc_low", "tile_mcc_best"}


def write_json(path: Path, value: dict) -> None:
    """Write one synthetic input under the test's temporary root."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


@pytest.fixture()
def tension_root(world, two_ladders, monkeypatch) -> dict:
    """A temporary repository root holding everything ``cmd_effect_sizes`` reads.

    The Phase 2 summary carries old inference for both families — for the
    clipped one, the p-value and tier count of Astra's check (p = 0.0123,
    two tiers). The Phase 1 inventory holds one deployment ladder.
    """
    root = world["tmp"]
    k_ladder = root / "results" / "k-ladder-2026-09-12"
    two_ladders["ladders"][0]["family"] = CLIPPED
    two_ladders["ladders"][1]["family"] = SAME
    write_json(k_ladder / "phase2" / "mcc-test" / "summary.json", {"ladders": [
        {"family": CLIPPED, "n_tiers": 2, "f1_p_bh_k1_to_best": 0.0123},
        {"family": SAME, "n_tiers": 1, "f1_p_bh_k1_to_best": 0.04},
    ]})
    write_json(k_ladder / "ladders.json", {"ladders": [{
        "family": "Stride A (g384 ov128), 55-map [r2]",
        "family_base": "Stride A (g384 ov128), 55-map",
        "reference_file": "inputs/best-available-gt-55maps-r2.geojson",
        "r1_verifier": True, "headline_buffer_m": 50,
        "rungs": [{"K": 1, "f1_headline": 0.70, "tile_mcc": 0.60},
                  {"K": 10, "f1_headline": 0.75, "tile_mcc": 0.65}],
    }]})
    write_json(k_ladder / "mcc-test" / "summary.json", {"ladders": [
        {"ladder": "55map-stride-a-r2", "f1_p_bh_k1_to_best": 0.0},
    ]})
    monkeypatch.setattr(tension, "BASE_DIR", root)
    monkeypatch.setattr(tension, "OUT_DIR", root / "tension")
    return {"root": root, "k_ladder": k_ladder, "payload": two_ladders}


def build_phase2(monkeypatch, tension_root: dict, *flags: str) -> dict:
    """Run the Phase 2 builder's CLI, writing ``phase2/ladders.json`` in place."""
    return area.run_builder(monkeypatch, tension_root["k_ladder"],
                            tension_root["payload"], "--no-figure", *flags)


def effect_sizes() -> dict:
    """Run analysis (b) and check the written file is what it returned."""
    result = tension.cmd_effect_sizes(argparse.Namespace())
    written = json.loads((tension.OUT_DIR / "effect-sizes.json").read_text())
    assert written == result
    return result


def rows_by_ladder(result: dict) -> dict[str, dict]:
    """The table's rows keyed by ladder name."""
    return {row["ladder"]: row for row in result["rows"]}


def test_a_clipped_ladder_keeps_its_f1_and_withholds_unclipped_inference(
        tension_root, monkeypatch):
    """Astra's downstream case: clipped F1, historical inference withheld, basis named.

    The builder reports the clipped ladder at K = 1 0.5 -> K = 3 0.6667
    (as evaluated 0.8 -> 1.0), while the summary's p = 0.0123 and two tiers
    were computed on the unclipped cells. Before v1.1.0 the row carried both.
    """
    from scripts import build_k_ladder_phase2_tables as tables

    out = build_phase2(monkeypatch, tension_root, "--clip-to-common-area")
    assert out["ladders"]["ladders"][0]["score_basis"]["reported"] == tables.BASIS_CLIPPED
    result = effect_sizes()
    rows = rows_by_ladder(result)

    clipped = rows[CLIPPED]
    # The F1 values are the clipped re-scores the builder reports.
    assert (clipped["K_low"], clipped["K_best"]) == (1, 3)
    assert (clipped["f1_low"], clipped["f1_best"]) == (0.5, 0.6667)
    assert clipped["delta_f1"] == pytest.approx(0.1667, abs=1e-9)
    # Nothing computed on the unclipped cells is paired with them.
    for key in WITHHELD:
        assert clipped[key] is None, key
    assert set(clipped["withheld"]) == WITHHELD
    assert all(isinstance(why, str) and why for why in clipped["withheld"].values())
    assert "unclipped" in clipped["withheld"]["p_bh"]
    assert "n_tiers" in clipped["withheld"]["one_tier"]
    assert clipped["score_basis"] == tables.BASIS_CLIPPED

    # The same-area ladder is as evaluated: its inference is on its basis.
    same = rows[SAME]
    assert same["score_basis"] == tables.BASIS_AS_EVALUATED
    assert (same["f1_low"], same["f1_best"], same["K_best"]) == (0.8, 1.0, 3)
    assert (same["p_bh"], same["n_tiers"], same["one_tier"]) == (0.04, 1, True)
    assert same["f1_low_ci"] == [0.7, 0.8] and same["tile_mcc_low"] == 0.5
    assert "withheld" not in same

    # The deployment row's inventory has no clip: as evaluated, named.
    deployment = rows["Stride A (g384 ov128), 55-map [r2]"]
    assert deployment["score_basis"] == tables.BASIS_AS_EVALUATED
    assert deployment["p_bh"] == 0.0 and "withheld" not in deployment

    record = result["score_basis"]
    assert record["clip_requested"] is True
    assert record["clip"] == tables.BASIS_CLIPPED
    assert record["n_withheld"] == 1


def test_a_trimmed_payload_is_still_read_by_its_points(tension_root, monkeypatch):
    """A clipped point is recognised even when the ladder's basis record is gone."""
    from scripts import build_k_ladder_phase2_tables as tables

    build_phase2(monkeypatch, tension_root, "--clip-to-common-area")
    path = tension_root["k_ladder"] / "phase2" / "ladders.json"
    payload = json.loads(path.read_text())
    del payload["score_basis"]
    for ladder in payload["ladders"]:
        del ladder["score_basis"]
    path.write_text(json.dumps(payload))

    rows = rows_by_ladder(effect_sizes())
    assert rows[CLIPPED]["score_basis"] == tables.BASIS_CLIPPED
    assert rows[CLIPPED]["p_bh"] is None and rows[CLIPPED]["n_tiers"] is None
    assert set(rows[CLIPPED]["withheld"]) == WITHHELD
    # Nothing else names a basis: no clip request is recorded.
    assert "score_basis" not in rows[SAME]


def test_an_unclipped_build_names_no_basis(tension_root, monkeypatch):
    """Without a clip the table keeps v1.0.0's shape, field for field and in order."""
    payload = tension_root["payload"]
    # Unclipped, the mismatched ladder refuses (exit 3); the same-area one builds.
    payload["ladders"] = payload["ladders"][1:]
    payload["n_ladders"] = 1
    build_phase2(monkeypatch, tension_root)
    result = effect_sizes()

    assert list(result) == ["generated_at_utc", "scope", "n_rows", "rows"]
    text = json.dumps(result)
    assert "score_basis" not in text and "withheld" not in text
    phase2_row, phase1_row = result["rows"]
    assert list(phase2_row) == PHASE2_ROW_KEYS_V1_0
    assert list(phase1_row) == PHASE1_ROW_KEYS_V1_0
    assert (phase2_row["f1_low"], phase2_row["f1_best"]) == (0.8, 1.0)
    assert (phase2_row["p_bh"], phase2_row["n_tiers"], phase2_row["one_tier"]) == (
        0.04, 1, True)
    assert phase2_row["f1_low_ci"] == [0.7, 0.8]
    assert phase2_row["tile_mcc_low"] == 0.5


def test_the_basis_markers_are_the_builders():
    """The table reads the names the builder writes, and the fields it withholds."""
    from scripts import build_k_ladder_phase2_tables as tables

    assert tension.BASIS_CLIPPED == tables.BASIS_CLIPPED
    assert tension.BASIS_AS_EVALUATED == tables.BASIS_AS_EVALUATED
    # The row's interval and tile-MCC come from the point's f1_20_ci and
    # tile_mcc, which the builder itself withholds on a clipped point.
    assert {"f1_20_ci", "tile_mcc"} <= set(tables.NOT_REGENERATED_BY_CLIP)
    assert set(tension.NOT_ON_CLIPPED_BASIS) == WITHHELD
