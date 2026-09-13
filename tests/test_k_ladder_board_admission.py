"""Tier-1 tests for the K-ladder admission of 2026-09-13 (PI ruling, route (a)).

Three mechanisms are pinned here, each of which a rebuild of the signed GS
Era-2 board depends on:

1. ``build_gs_era2_board.derive_membership`` DEFERS to
   ``k-ladder/membership.json`` by condition id, and does so BEFORE its frame
   and ``scope_override`` refusal rules — while keeping both rules for every
   condition the file does not name.
2. ``build_gs_era2_board.finalise`` carries ``signature_history`` forward. The
   close-out report found that a rebuild would otherwise have destroyed the
   array recording the board's original 2026-09-10 signature.
3. ``build_board_tiering_input.membership_condition_ids`` names a K-ladder
   member by its OWN condition id, because no ``-era2b`` row is minted for it.

Everything is exercised over synthetic registers and a temporary board
directory: no committed artefact is read and nothing is written outside
``tmp_path``.
"""

from __future__ import annotations

import json

import pytest

from scripts import build_board_tiering_input as ti
from scripts import build_gs_era2_board as b

pytestmark = pytest.mark.tier1

BOARD_FRAME_EVAL = {
    "_metadata": {"cli_args": {
        "bounds": "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson",
        "ground_truth": "inputs/vectors/references/mounds-reference.geojson",
        "buffers": [20], "bootstrap": 10000, "seed": 42}},
    "summary": {"n_detections": 435,
                "buffers": [{"buffer_metres": 20, "f1": 0.8905}]},
}
ERA2_FRAME_EVAL = {
    "_metadata": {"cli_args": {
        "bounds": "inputs/vectors/bounds/full_evaluation_bounds.geojson",
        "ground_truth": "inputs/vectors/references/mounds-reference.geojson",
        "buffers": [20], "bootstrap": 10000, "seed": 42}},
    "summary": {"n_detections": 400,
                "buffers": [{"buffer_metres": 20, "f1": 0.8500}]},
}


@pytest.fixture()
def register(tmp_path, monkeypatch):
    """A two-condition register: one K-ladder cell and one ordinary cell.

    Both are verified 4-map-GS 384 px rows. The K-ladder cell carries a
    board-frame evaluation AND a ``scope_override``, so both refusal rules
    would refuse it; the ordinary cell carries an Era-2-frame evaluation and no
    override, so both rules admit it.
    """
    (tmp_path / "det").mkdir()
    for name in ("kl.geojson", "plain.geojson"):
        (tmp_path / "det" / name).write_text('{"type":"FeatureCollection","features":[]}')
    (tmp_path / "evals").mkdir()
    (tmp_path / "evals/kl.json").write_text(json.dumps(BOARD_FRAME_EVAL))
    (tmp_path / "evals/plain.json").write_text(json.dumps(ERA2_FRAME_EVAL))
    conditions = {"decomposition": {"runx": {"conditions": [
        {"label": "kl-n5-opmax", "aggregation": "verified", "n_passes": 5,
         "detections": "det/kl.geojson", "eval_path": "evals/kl.json",
         "scope_override": {"test_set_id": "era2-b-487"}},
        {"label": "plain-n5", "aggregation": "verified", "n_passes": 5,
         "detections": "det/plain.geojson", "eval_path": "evals/plain.json"},
    ]}}}
    facts = {"facts": {"runx": {"corpus": "4-map-gs", "tile_size_px": 384}}}
    (tmp_path / "run-conditions.json").write_text(json.dumps(conditions))
    (tmp_path / "run-facts.json").write_text(json.dumps(facts))
    monkeypatch.setattr(b, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(b, "RUN_CONDITIONS", tmp_path / "run-conditions.json")
    monkeypatch.setattr(b, "RUN_FACTS", tmp_path / "run-facts.json")
    monkeypatch.setattr(b, "OPMAX_MEMBERSHIP", "absent/opmax.json")
    monkeypatch.setattr(b, "K_LADDER_MEMBERSHIP", "k-ladder/membership.json")
    return tmp_path


def _write_k_ladder(root, *condition_ids):
    path = root / "k-ladder/membership.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"members": [
        {"condition_id": cid, "reason": "tier E: admitted by the PI ruling"}
        for cid in condition_ids]}))


def test_without_the_membership_file_both_refusal_rules_still_refuse(register):
    """The baseline: the K-ladder cell is refused, and for both reasons."""
    membership = b.derive_membership()
    assert [m["condition_id"] for m in membership["members"]] == ["runx::plain-n5"]
    refusal = next(e for e in membership["excluded"]
                   if e["condition_id"] == "runx::kl-n5-opmax")
    assert "neither the Era-2 frame nor grid-common" in refusal["reason"]


def test_the_deferral_admits_the_named_cell_before_those_rules(register):
    """Named in the file, the same cell joins — and is flagged as K-ladder."""
    _write_k_ladder(register, "runx::kl-n5-opmax")
    membership = b.derive_membership()
    ids = [m["condition_id"] for m in membership["members"]]
    assert sorted(ids) == ["runx::kl-n5-opmax", "runx::plain-n5"]
    member = next(m for m in membership["members"]
                  if m["condition_id"] == "runx::kl-n5-opmax")
    assert member["k_ladder"] is True
    assert member["admitted_via"] == "k-ladder/membership.json"
    assert "PI ruling" in member["admission_reason"]
    # Admitted with its board-frame evaluation as-is: the member's eval_path is
    # the committed one, not a re-scored cells/<slug>/evaluation.json.
    assert member["eval_path"] == "evals/kl.json"
    assert member["committed_f1_20"] == pytest.approx(0.8905)
    assert not membership["excluded"]


def test_the_deferral_does_not_relax_the_rules_for_anything_else(register):
    """A cell the file does not name is still refused on the frame rule."""
    _write_k_ladder(register, "runx::some-other-cell")
    membership = b.derive_membership()
    assert [m["condition_id"] for m in membership["members"]] == ["runx::plain-n5"]
    assert any("neither the Era-2 frame nor grid-common" in e["reason"]
               for e in membership["excluded"])


def test_a_named_cell_with_no_detections_file_is_refused_not_admitted(register):
    """The deferral waives the frame rules, not the existence of the data."""
    (register / "det/kl.geojson").unlink()
    _write_k_ladder(register, "runx::kl-n5-opmax")
    membership = b.derive_membership()
    assert [m["condition_id"] for m in membership["members"]] == ["runx::plain-n5"]
    assert any("detections file is missing" in e["reason"]
               for e in membership["excluded"])


def test_k_ladder_members_get_no_scoring_jobs(register, tmp_path):
    """They are already scored on the frame, so ``jobs`` writes none for them."""
    _write_k_ladder(register, "runx::kl-n5-opmax")
    membership = b.derive_membership()
    board = tmp_path / "board"
    board.mkdir()
    b.write_jobs(board, membership)
    script = (board / "score-commands.sh").read_text()
    assert "NO JOBS" in script
    assert script.count("run python scripts/evaluate_detections.py") == 2
    assert "det/kl.geojson" not in script


def test_k_ladder_members_mint_no_era2b_row(register):
    """No second scoring means no second row: the cell joins under its own id."""
    _write_k_ladder(register, "runx::kl-n5-opmax")
    membership = b.derive_membership()
    new_ids = b.register(membership, write=False)
    assert "runx::kl-n5-opmax" in new_ids
    assert "runx::kl-n5-opmax-era2b" not in new_ids
    assert "runx::plain-n5-era2b" in new_ids


def test_tiering_input_names_a_k_ladder_member_by_its_own_id(tmp_path):
    """``-era2b`` is appended to every member EXCEPT a K-ladder one."""
    board = tmp_path / "board"
    (board / "opmax").mkdir(parents=True)
    (board / "membership.json").write_text(json.dumps({"members": [
        {"condition_id": "runx::plain-n5"},
        {"condition_id": "runx::kl-n5-opmax", "k_ladder": True}]}))
    (board / "opmax/membership.json").write_text(json.dumps({"members": [
        {"condition_id": "runy::opmax-cell", "on_board": True}]}))
    ids, counts = ti.membership_condition_ids(board)
    assert ids == ["runx::plain-n5-era2b", "runx::kl-n5-opmax",
                   "runy::opmax-cell"]
    assert counts == {"era2b": 1, "k_ladder": 1, "opmax": 1}


def _finalise_fixture(tmp_path, monkeypatch, prior_provenance):
    """A board directory minimal enough for ``finalise`` to run over."""
    board = tmp_path / "board"
    board.mkdir()
    (board / "tiering_20m.json").write_text(json.dumps({
        "ranking": [{"rank": 1, "ref": "runx::plain-n5-era2b",
                     "label": "plain-n5-era2b", "eval_f1": 0.85, "mcc": 0.7,
                     "tier": 1}],
        "tiers": [{"tier": 1, "members": ["runx::plain-n5-era2b"]}],
        "pairwise": [], "n_tiles": 487, "git_commit": "deadbeef",
        "generated_at_utc": "2026-09-13T00:00:00+00:00",
    }))
    (board / "gates.json").write_text(json.dumps({
        "G2_reproduction_failures": 0, "G3_frame_failures": 0,
        "G4_cells": 1, "G4_members": 1,
        "cells": [{"condition_id": "runx::plain-n5", "committed_f1_20": 0.85,
                   "delta_board_minus_committed": 0.0}],
    }))
    (board / "provenance.json").write_text(json.dumps(prior_provenance))
    analyses = tmp_path / "run-analyses.json"
    analyses.write_text(json.dumps({"analyses": [{
        "analysis_id": b.BOARD_ID, "outcome": "the signed outcome",
        "conditions_compared": ["runx::plain-n5-era2b"]}]}))
    monkeypatch.setattr(b, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(b, "RUN_ANALYSES", analyses)
    monkeypatch.setattr(b, "BOARD_DIR", "board")
    return board


def test_finalise_carries_signature_history_forward(tmp_path, monkeypatch):
    """The close-out's blocker: a rebuild must not erase the signature trail."""
    history = [{"signed_at": "2026-09-10T12:34:56Z", "n_conditions_compared": 79,
                "note": "original signature"}]
    board = _finalise_fixture(tmp_path, monkeypatch, {
        "signed_at": "2026-09-12T06:04:30Z", "signed_by": "the PI",
        "signature_history": history,
        "re_sign_pending": {"status": "RE-SIGNED 2026-09-12T06:04:30Z"},
        "gates": {"G1": {"pi_ruling": {"ruling": "satisfied"}}},
    })
    b.finalise(board, {"n_members": 1, "members": [
        {"condition_id": "runx::plain-n5", "k_ladder": False}]},
        skip_analysis_row=True, re_sign_reason="the membership changed")
    out = json.loads((board / "provenance.json").read_text())
    assert out["signature_history"] == history
    assert out["signed_at"] == "2026-09-12T06:04:30Z"
    assert out["gates"]["G1"]["pi_ruling"] == {"ruling": "satisfied"}
    assert "signature_history" in out["_carried_forward"]["fields"]
    # The fresh block is PENDING again, and the resolved one it replaces is
    # nested inside it rather than dropped.
    assert out["re_sign_pending"]["status"].startswith("PENDING")
    assert out["re_sign_pending"]["previous_resolved"]["status"].startswith("RE-SIGNED")
    assert out["re_sign_pending"]["signed_outcome"] == "the signed outcome"


def test_finalise_does_not_touch_the_signed_analysis_row(tmp_path, monkeypatch):
    """``--no-analysis-row``: the register's signed text is left exactly as-is."""
    board = _finalise_fixture(tmp_path, monkeypatch, {"signed_at": "x"})
    before = (tmp_path / "run-analyses.json").read_text()
    b.finalise(board, {"n_members": 1, "members": [
        {"condition_id": "runx::plain-n5", "k_ladder": False}]},
        skip_analysis_row=True, re_sign_reason="r")
    assert (tmp_path / "run-analyses.json").read_text() == before


# --- The MCC withhold path (scripts/era1_leaderboard_tiering.py) -------------
# A cell the tile-join invariant refuses must be withheld and listed, never
# allowed to abort the board: before 2026-09-13 the ``ConfusionGateError`` was
# uncaught, so three Gemini 3.7 rungs would have killed the whole re-tiering.

def test_mcc_family_splits_testable_cells_from_withheld_ones():
    from scripts import era1_leaderboard_tiering as t

    cells = [
        {"ref": "a", "label": "cell-a", "tp_c": [1], "mcc": 0.80},
        {"ref": "b", "label": "cell-b", "mcc": None,
         "mcc_withheld": {"recorded_mcc": 0.1337,
                          "reason": "tile join lost 454 of 475 in-frame detections",
                          "ruling": "PI ruling 2026-09-13"}},
        {"ref": "c", "label": "cell-c", "tp_c": [0], "mcc": 0.79},
    ]
    indices, withheld = t.mcc_family(cells)
    assert indices == [0, 2]
    assert [w["ref"] for w in withheld] == ["b"]
    assert withheld[0]["label"] == "cell-b"
    assert withheld[0]["recorded_mcc"] == 0.1337
    assert "tile join lost" in withheld[0]["reason"]


def test_mcc_family_is_the_whole_board_when_nothing_is_refused():
    from scripts import era1_leaderboard_tiering as t

    cells = [{"ref": "a", "label": "a", "tp_c": [1]},
             {"ref": "b", "label": "b", "tp_c": [1]}]
    assert t.mcc_family(cells) == ([0, 1], [])


def test_confusion_gate_error_is_the_type_the_withhold_path_catches():
    """The catch is on ``ConfusionGateError``; the gate must still raise it."""
    from scripts import era1_leaderboard_tiering as t

    with pytest.raises(t.ConfusionGateError, match="lost 3 of 4 in-frame"):
        t.check_confusion_gate(
            "refused-cell", {"tp": 1, "tn": 1, "fp": 0, "fn": 0},
            {"tp": 1, "tn": 1, "fp": 0, "fn": 0}, 0.5, 0.5,
            geometry_check={"detections": {"n_assigned": 1, "n_inside_union": 4,
                                           "n_outside_union": 0},
                            "references": {}})


def test_a_tile_join_refusal_is_told_apart_from_every_other_value_error():
    """The F1 arm raises a plain ValueError, so the reason CODE is the signal.

    Discovered on 2026-09-13: the invariant refuses the per-tile F1 table as
    well as the tile classification, and it does so with a ``ValueError`` from
    ``lib_advanced_metrics``. Catching ``ValueError`` broadly would have
    swallowed a missing detections set or an un-scoreable cell, so the withhold
    path tests the stamped reason code instead.
    """
    from scripts import era1_leaderboard_tiering as t

    assert t.is_tile_join_refusal(ValueError(
        "per-tile TP/FP/FN table refused: 22 of 526 in-frame detections ... "
        "(tile_join_detection_shortfall) ..."))
    assert t.is_tile_join_refusal(t.ConfusionGateError("tile join refused"))
    assert not t.is_tile_join_refusal(ValueError(
        "cli_args declare neither a detections set nor a detections_dir"))
    assert not t.is_tile_join_refusal(FileNotFoundError("detections set missing"))


def test_finalise_publishes_the_withheld_list_from_the_tiering(tmp_path, monkeypatch):
    """``finalise`` lifts ``mcc_permutation.withheld`` into provenance and README."""
    board = _finalise_fixture(tmp_path, monkeypatch, {"signed_at": "x"})
    tiering = json.loads((board / "tiering_20m.json").read_text())
    tiering["mcc_permutation"] = {"withheld": [
        {"ref": "runz::refused", "label": "refused-cell",
         "recorded_mcc": 0.1337, "reason": "tile join lost 454 of 475"}]}
    (board / "tiering_20m.json").write_text(json.dumps(tiering))
    b.finalise(board, {"n_members": 1, "members": [
        {"condition_id": "runx::plain-n5", "k_ladder": False}]},
        skip_analysis_row=True, re_sign_reason="r")
    prov = json.loads((board / "provenance.json").read_text())
    assert prov["tiering"]["n_mcc_withheld"] == 1
    assert prov["tiering"]["mcc_withheld"][0]["label"] == "refused-cell"
    readme = (board / "README.md").read_text()
    assert "tile-MCC withheld" in readme and "refused-cell" in readme
