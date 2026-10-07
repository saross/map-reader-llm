"""
Tests for Run B's six-cell anchor gate and the parameterised analysis entry points.

``scripts/modality_bridge_anchors.py`` refuses to let a bridge number be
written unless the six original cells (and the three original gaps)
reproduce through the scoring path. The tier-1 tests pin the gate's decision
logic with the scorer stubbed, the registered values against the card and
the committed analyses, and the two new entry-point helpers
(``image_b_analysis.parse_operating_point``,
``gemini37_image_gap_test.pairs_from_dirs``). The tier-2 test runs the real
gate on the committed unions and probabilities (about three minutes on
sapphire).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import modality_bridge_anchors as mba  # noqa: E402
from scripts.gemini37_image_gap_test import pairs_from_dirs  # noqa: E402
from scripts.image_b_analysis import parse_operating_point  # noqa: E402

#: The card's six cells (planning/modality-bridge-2026-10-07.md § 2.2, § 8).
CARD = {
    "g3-text": (0.8961, 0.15, 10), "g3-image": (0.8412, 0.15, 9),
    "g37-text-g3v": (0.9139, 0.10, 5), "g37-text-g37v": (0.9265, 0.80, 5),
    "g37-image-g3v": (0.9254, 0.10, 5), "g37-image-g37v": (0.9308, 0.90, 5),
}


def _fake_score(offsets: dict[str, dict] | None = None):
    """A score_cell stand-in returning each cell's registered values (± offsets)."""
    offsets = offsets or {}
    by_root = {(c.outputs_root, c.verify_dir): c for c in mba.ORIGINAL_CELLS}

    def fake(vroot: Path, union_name: str, verify_dir: str, k: int, label: str) -> dict:
        root = str(vroot.parent.parent.relative_to(PROJECT_ROOT))
        c = by_root[(root, verify_dir)]
        off = offsets.get(c.label, {})
        best = {"f1": c.f1 + off.get("f1", 0.0), "prob_t": off.get("prob_t", c.prob_t),
                "min_votes": off.get("min_votes", c.min_votes), "precision": 0.9,
                "recall": 0.9, "mcc": 0.8, "n_detections": 400}
        counts = {k: np.zeros(3) for k in ("tp", "fp", "fn")}
        counts["tag"] = c.label
        return {"best": best, "union": [0] * 10, "counts": counts,
                "micro_f1": c.f1 + off.get("micro", off.get("f1", 0.0))}
    return fake


def _fake_perm(gap_offsets: dict[str, float] | None = None):
    """A permutation stand-in returning each registered gap (± offset)."""
    gap_offsets = gap_offsets or {}
    registered = {(t, i): g for t, i, g in mba.ORIGINAL_GAPS}

    def fake(tp_a, fp_a, fn_a, tp_b, fp_b, fn_b, n_permutations, seed):
        key = (tp_a.tag, tp_b.tag)
        return {"observed_diff": registered[key] + gap_offsets.get(key[0], 0.0),
                "p_value": 0.5}
    return fake


class _Tagged(np.ndarray):
    """An array that remembers which cell it came from (for the fake test)."""


@pytest.fixture
def stub_scorer(monkeypatch: pytest.MonkeyPatch):
    """Install the stubs; returns a function to set offsets."""
    import scripts.n1_baseline_leaderboard_tiering as n1

    def install(cell_offsets=None, gap_offsets=None):
        fake = _fake_score(cell_offsets)

        def tagged(*a, **kw):
            out = fake(*a, **kw)
            tag = out["counts"].pop("tag")
            for key in ("tp", "fp", "fn"):
                arr = out["counts"][key].view(_Tagged)
                arr.tag = tag
                out["counts"][key] = arr
            return out
        monkeypatch.setattr(mba, "score_cell", tagged)
        monkeypatch.setattr(n1, "permutation_test_float", _fake_perm(gap_offsets))
    return install


@pytest.mark.tier1
def test_registered_values_match_the_card() -> None:
    got = {c.label: (c.f1, c.prob_t, c.min_votes) for c in mba.ORIGINAL_CELLS}
    assert got == CARD
    assert [g for _, _, g in mba.ORIGINAL_GAPS] == [0.0549, -0.0115, -0.0043]


@pytest.mark.tier1
def test_registered_values_match_the_committed_analyses() -> None:
    """Where an image_b_analysis.py output was committed, it agrees to 1e-4."""
    committed = {
        "g3-image": "results/image-b-gs-2026-08-28/analysis.json",
        "g37-text-g3v": "results/gemini37-screen-2026-08-28/analysis.json",
        "g37-text-g37v": "results/gemini37-screen-2026-08-28/swap37/analysis.json",
        "g37-image-g3v": "results/gemini37-image-gs-2026-09-01/arm1/analysis.json",
        "g37-image-g37v": "results/gemini37-image-gs-2026-09-01/arm2/analysis.json",
    }
    cells = {c.label: c for c in mba.ORIGINAL_CELLS}
    for label, rel in committed.items():
        best = json.loads((PROJECT_ROOT / rel).read_text())["image_best"]
        c = cells[label]
        assert abs(best["f1"] - c.f1) < 1e-4, label
        assert (round(best["prob_t"], 4), best["min_votes"]) == (c.prob_t, c.min_votes)
    gap = json.loads((PROJECT_ROOT / "results/gemini37-image-gs-2026-09-01/"
                      "gap_test.json").read_text())["pairs"]
    assert abs(gap["carried-verifier"]["observed_diff"] - (-0.0115)) < 1e-4
    assert abs(gap["all-3.7"]["observed_diff"] - (-0.0043)) < 1e-4


@pytest.mark.tier1
def test_gate_passes_when_every_cell_reproduces(stub_scorer) -> None:
    stub_scorer()
    record = mba.run_six_cell_gate()
    assert record["passed"] and len(record["cells"]) == 6 and len(record["gaps"]) == 3


@pytest.mark.tier1
@pytest.mark.parametrize("offset", [
    {"f1": 0.0011}, {"micro": -0.0011}, {"prob_t": 0.2}, {"min_votes": 4}])
def test_gate_refuses_a_cell_that_moved(stub_scorer, offset: dict) -> None:
    stub_scorer({"g3-image": offset})
    with pytest.raises(mba.AnchorGateError, match="g3-image"):
        mba.run_six_cell_gate()


@pytest.mark.tier1
def test_gate_tolerates_a_move_inside_the_tolerance(stub_scorer) -> None:
    stub_scorer({"g37-image-g37v": {"f1": 0.0009}})
    assert mba.run_six_cell_gate()["passed"]


@pytest.mark.tier1
def test_gate_refuses_a_gap_that_moved(stub_scorer) -> None:
    stub_scorer(gap_offsets={"g37-text-g3v": 0.002})
    with pytest.raises(mba.AnchorGateError, match="gap g37-text-g3v"):
        mba.run_six_cell_gate()


@pytest.mark.tier1
def test_gate_cli_exit_status(stub_scorer, tmp_path: Path) -> None:
    stub_scorer({"g3-text": {"f1": 0.01}})
    out = tmp_path / "gate.json"
    assert mba.main(["--json-out", str(out)]) == 1
    assert json.loads(out.read_text())["passed"] is False


@pytest.mark.tier1
def test_parse_operating_point() -> None:
    assert parse_operating_point("0.15,9") == (0.15, 9)
    assert parse_operating_point("0.9,5") == (0.9, 5)
    with pytest.raises(ValueError):
        parse_operating_point("0.15")
    with pytest.raises(ValueError):
        parse_operating_point("0.15,0")


@pytest.mark.tier1
def test_pairs_from_dirs(tmp_path: Path) -> None:
    for name, best, op in (("text", 0.91, 0.90), ("image", 0.93, 0.92)):
        d = tmp_path / name
        d.mkdir()
        (d / "analysis.json").write_text(json.dumps(
            {"image_best": {"f1": best}, "operating_point": {"f1": op}}))
    pairs = pairs_from_dirs([["p", str(tmp_path / "text"), str(tmp_path / "image")]])
    assert pairs == [("p", tmp_path / "text" / "verified_best_20m.geojson", 0.91,
                      tmp_path / "image" / "verified_best_20m.geojson", 0.93)]
    op = pairs_from_dirs([["p", str(tmp_path / "text"), str(tmp_path / "image")]],
                         "verified_op_20m")
    assert op[0][2] == 0.90 and op[0][1].name == "verified_op_20m.geojson"


@pytest.mark.tier2
def test_real_six_cell_gate_on_committed_data() -> None:
    """The gate itself, on the committed unions and probabilities."""
    record = mba.run_six_cell_gate()
    assert record["passed"]
    for label, (f1, prob_t, votes) in CARD.items():
        cell = record["cells"][label]
        assert abs(cell["reproduced_f1"] - f1) <= 1e-3
        assert cell["reproduced_point"] == [pytest.approx(prob_t), votes]
