"""Tier-1 tests for the Era-2 board's tile-MCC family (PI ruling 2026-09-13).

Two rulings of Session 153 reach the board through the code these tests pin:

* **Ruling 7** — the round-robin tile-swap carries tile-MCC on the same swap
  masks as F1, with Benjamini-Hochberg (BH) q = 0.05 within its own family, and
  the result is **reported beside** the preregistered F1 tiering rather than
  replacing it. So there are two tierings and two Multiple Comparisons with the
  Best (MCB) admissible sets in the artefacts, and the F1 pair must stay the
  board's.
* **Ruling 6** — the name-based (``id``) tile join is the published convention,
  and a cell the tile-join invariant refuses is DISCLOSED: its whole-frame F1
  point estimate, its interval WITHDRAWN rather than superseded, the shortfall
  counts, and both tile vocabularies.

Everything runs over synthetic tiering artefacts in ``tmp_path``; no committed
board artefact is read and nothing is written outside it.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from scripts import build_gs_era2_board as b
from scripts import era1_leaderboard_tiering as t

pytestmark = pytest.mark.tier1


# --- The MCC tiering instrument (scripts/era1_leaderboard_tiering.py) --------

def _cell(ref: str, mcc: float, f1: float) -> dict:
    """A loaded cell carrying one-hot arrays, as ``load_cells`` returns it."""
    return {
        "ref": ref, "label": ref.split("::")[-1], "mcc": mcc, "eval_f1": f1,
        "tp_c": np.array([1, 0]), "tn_c": np.array([0, 1]),
        "fp_c": np.array([0, 0]), "fn_c": np.array([0, 0]),
    }


def test_mcc_tiering_orders_by_mcc_not_by_f1():
    """The MCC family's ranking is its own: F1 order must not leak into it."""
    cells = [_cell("r::a", mcc=0.10, f1=0.99), _cell("r::b", mcc=0.90, f1=0.10)]
    ranking, tiers = t.mcc_tiering(
        cells, [0, 1],
        [{"ref_a": "r::a", "ref_b": "r::b", "significant": True}],
    )
    assert [row["ref"] for row in ranking] == ["r::b", "r::a"]
    assert [row["mcc_tier"] for row in ranking] == [1, 2]
    assert tiers == [["r::b"], ["r::a"]]


def test_mcc_tiering_cliques_on_the_mcc_familys_own_bh_verdicts():
    """An MCC-indistinguishable pair shares an MCC tier, whatever F1 said."""
    cells = [_cell("r::a", mcc=0.90, f1=0.90), _cell("r::b", mcc=0.88, f1=0.50)]
    _ranking, tiers = t.mcc_tiering(
        cells, [0, 1],
        [{"ref_a": "r::a", "ref_b": "r::b", "significant": False}],
    )
    assert tiers == [["r::a", "r::b"]], "not separable on MCC, so one tier"


def test_mcc_tiering_excludes_a_cell_with_no_mcc_at_all():
    """A cell outside the MCC family is outside the MCC ranking too."""
    cells = [_cell("r::a", mcc=0.90, f1=0.90),
             {"ref": "r::b", "label": "b", "mcc": None, "eval_f1": 0.5,
              "mcc_withheld": {"reason": "tile_join_detection_shortfall"}}]
    ranking, tiers = t.mcc_tiering(cells, [0], [])
    assert [row["ref"] for row in ranking] == ["r::a"]
    assert tiers == [["r::a"]]


def test_mcc_point_falls_back_to_the_rebuilt_arrays():
    """A cell whose evaluation records no tile MCC is still orderable."""
    cell = _cell("r::a", mcc=0.5, f1=0.9)
    assert t.mcc_point(cell) == 0.5
    cell["mcc"] = None
    assert t.mcc_point(cell) == pytest.approx(1.0)
    assert t.mcc_point({"ref": "x", "mcc": None}) is None


def test_the_interval_withdrawn_wording_names_the_resampling_unit():
    """"Withdrawn", and why: the bootstrap resamples tiles (Decision 10)."""
    assert t.INTERVAL_WITHDRAWN == "interval withdrawn (tile-resampled bootstrap)"
    assert "resamples tiles" in t.INTERVAL_WITHDRAWN_DETAIL
    assert "withdrawn rather than superseded" in t.INTERVAL_WITHDRAWN_DETAIL


def test_committed_interval_f1_reads_a_pre_invariant_interval(tmp_path):
    """The interval the board is retracting must be nameable, not just absent."""
    path = tmp_path / "evaluation.json"
    path.write_text(json.dumps({"summary": {"buffers": [
        {"buffer_metres": 20, "f1_ci_lower": 0.2712, "f1_ci_upper": 0.6667},
        {"buffer_metres": 30, "f1_ci_lower": 0.3, "f1_ci_upper": 0.7}]}}))
    assert t.committed_interval_f1(path, 20) == [0.2712, 0.6667]
    assert t.committed_interval_f1(path, 50) is None


def test_committed_interval_f1_is_none_for_a_re_scored_withheld_cell(tmp_path):
    """A cell re-scored under the invariant writes nulls; there is nothing to name."""
    path = tmp_path / "evaluation.json"
    path.write_text(json.dumps({"summary": {"buffers": [
        {"buffer_metres": 20, "f1": 0.886, "f1_ci_lower": None,
         "f1_ci_upper": None, "ci_withheld": True}]}}))
    assert t.committed_interval_f1(path, 20) is None


# --- The board builder's rendering (scripts/build_gs_era2_board.py) ----------

WITHHELD = {
    "ref": "gemini37-screen-2026-08-28::g37-text-k3-verified-opmax",
    "label": "g37-text-k3-verified-opmax",
    "eval_f1": 0.886, "recorded_mcc": 0.1337,
    "arm": "per-tile F1 (and therefore MCC)",
    "reason": "per-tile TP/FP/FN table refused: 20 of 468 in-frame detections "
              "were credited to a tile under the 'id' tile join, a shortfall "
              "of 448. (tile_join_detection_shortfall)",
    "interval_status": t.INTERVAL_WITHDRAWN,
    "interval_detail": t.INTERVAL_WITHDRAWN_DETAIL,
    "withdrawn_interval_f1": [0.3684, 0.7732],
    "disclosure": {
        "shortfall": {"axis": "detections", "n_booked": 20,
                      "n_inside_union": 468, "shortfall": 448},
        "vocabularies": {
            "frame": {"n_tiles": 487, "n_distinct_tile_names": 487,
                      "map_prefixes": ["K-35-052-4_32635"],
                      "sample_tile_names": ["K-35-052-4_32635_x0_y1008.png"]},
            "detections": {"n_detections": 495, "id_column": "source_tile",
                           "n_distinct_tile_names": 306,
                           "n_names_in_frame_vocabulary": 11,
                           "map_prefixes": ["K-35-052-4_32635"],
                           "sample_tile_names": ["K-35-052-4_32635_x0_y1152.png"]},
        },
    },
}

MCC_BLOCK = {
    "fdr_q": 0.05, "n_pairs": 3, "n_significant": 2, "n_tiers": 2,
    "n_cells_with_mcc": 3, "n_cells_withheld": 0, "withheld": [],
    "tie_set": ["runx::plain-n5-era2b"],
    "tiers": [{"tier": 1, "members": ["runx::plain-n5-era2b"]},
              {"tier": 2, "members": ["runy::other"]}],
    "ranking": [
        {"rank": 1, "ref": "runx::plain-n5-era2b", "label": "plain-n5-era2b",
         "mcc": 0.8264, "eval_f1": 0.85, "mcc_tier": 1, "f1_tier": 1},
        {"rank": 2, "ref": "runy::other", "label": "other", "mcc": 0.4313,
         "eval_f1": 0.47, "mcc_tier": 2, "f1_tier": 1},
    ],
    "pairwise": [], "gates": {},
}


def _board(tmp_path, monkeypatch, *, mcc_block=None, withheld=None,
           mcc_mcb=None, prior=None):
    """A board directory minimal enough for ``finalise`` to run over."""
    board = tmp_path / "board"
    (board / "mcb").mkdir(parents=True)
    tiering = {
        "ranking": [{"rank": 1, "ref": "runx::plain-n5-era2b",
                     "label": "plain-n5-era2b", "eval_f1": 0.85, "mcc": 0.8264,
                     "tier": 1}],
        "tiers": [{"tier": 1, "members": ["runx::plain-n5-era2b"]}],
        "tie_set": ["runx::plain-n5-era2b"],
        "pairwise": [], "n_tiles": 487, "git_commit": "deadbeef",
        "generated_at_utc": "2026-09-13T00:00:00+00:00",
    }
    if withheld is not None:
        tiering["withheld_cells"] = withheld
    if mcc_block is not None:
        tiering["mcc_permutation"] = mcc_block
    (board / "tiering_20m.json").write_text(json.dumps(tiering))
    (board / "gates.json").write_text(json.dumps({
        "G2_reproduction_failures": 0, "G3_frame_failures": 0,
        "G4_cells": 1, "G4_members": 1,
        "cells": [{"condition_id": "runx::plain-n5", "committed_f1_20": 0.85,
                   "delta_board_minus_committed": 0.0}],
    }))
    (board / "mcb" / f"{b.BOARD_ID}_b20_m1.json").write_text(json.dumps({
        "candidates": [{"ref": "runx::plain-n5-era2b"}, {"ref": "runy::other"}],
        "hsu_not_ruled_out": [0], "mcb_not_ruled_out": [0, 1],
    }))
    if mcc_mcb is not None:
        (board / "mcb" / f"{b.BOARD_ID}_mcc_b20_m1.json").write_text(
            json.dumps(mcc_mcb))
    (board / "provenance.json").write_text(json.dumps(prior or {"signed_at": "x"}))
    analyses = tmp_path / "run-analyses.json"
    analyses.write_text(json.dumps({"analyses": [{
        "analysis_id": b.BOARD_ID, "outcome": "the signed outcome",
        "conditions_compared": ["runx::plain-n5-era2b"]}]}))
    monkeypatch.setattr(b, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(b, "RUN_ANALYSES", analyses)
    monkeypatch.setattr(b, "BOARD_DIR", "board")
    return board


def _finalise(board):
    b.finalise(board, {"n_members": 1, "members": [
        {"condition_id": "runx::plain-n5", "k_ladder": False}]},
        skip_analysis_row=True, re_sign_reason="the MCC family was added")


def test_mcb_admissible_picks_the_metric_it_is_asked_for(tmp_path, monkeypatch):
    """Two admissible sets in one directory: the stamp decides, not sort order."""
    board = _board(tmp_path, monkeypatch, mcc_mcb={
        "candidates": [{"ref": "runy::other"}], "hsu_not_ruled_out": [0],
        "mcb_not_ruled_out": [0]})
    f1_set, f1_path = b._mcb_admissible(board)
    mcc_set, mcc_path = b._mcb_admissible(board, metric="mcc")
    assert f1_set == ["runx::plain-n5-era2b"] and "_mcc_" not in f1_path
    assert mcc_set == ["runy::other"] and "_mcc_" in mcc_path


def test_mcb_admissible_mcc_is_empty_when_the_file_is_absent(tmp_path, monkeypatch):
    """An MCC set is never inferred from the F1 artefact."""
    board = _board(tmp_path, monkeypatch)
    assert b._mcb_admissible(board, metric="mcc") == ([], None)


def test_finalise_renders_the_mcc_tiering_beside_the_f1_one(tmp_path, monkeypatch):
    """Two tables, and the README says which one is the board's tiering."""
    board = _board(tmp_path, monkeypatch, mcc_block=MCC_BLOCK, mcc_mcb={
        "candidates": [{"ref": "runx::plain-n5-era2b"}, {"ref": "runy::other"}],
        "hsu_not_ruled_out": [0, 1], "mcb_not_ruled_out": [0, 1]})
    _finalise(board)
    readme = (board / "README.md").read_text()
    assert "| rank | cell | tier | MCB | F1@20 (board frame) |" in readme
    assert "| MCC rank | cell | MCC tier | MCC MCB | tile-MCC |" in readme
    assert "REPORTED, not the tiering" in readme
    assert "does not replace it" in readme
    assert "the board's tiering, its ranks and its Tier 1 are the F1 ones" in readme
    # The MCC MCB column marks the MCC set, not the F1 set.
    assert "| 2 | `runy::other` | 2 | ● | 0.4313 |" in readme


def test_finalise_records_both_families_in_the_proposed_outcome(tmp_path, monkeypatch):
    """The text the PI signs must state both families and which one tiers."""
    board = _board(tmp_path, monkeypatch, mcc_block=MCC_BLOCK, mcc_mcb={
        "candidates": [{"ref": "runx::plain-n5-era2b"}, {"ref": "runy::other"}],
        "hsu_not_ruled_out": [0, 1], "mcb_not_ruled_out": [0, 1]})
    _finalise(board)
    prov = json.loads((board / "provenance.json").read_text())
    proposed = prov["re_sign_pending"]["proposed_outcome"]
    assert "pairs significant at BH q = 0.05" in proposed
    assert "REPORTED BESIDE, not replacing, the preregistered F1 tiering" in proposed
    assert "2/3 pairs significant" in proposed
    assert "MCC Tier 1 = 1 cell(s) (plain-n5-era2b MCC 0.8264)" in proposed
    assert "MCC MCB admissible set = 2, of which 1 also in the F1 admissible set" \
        in proposed
    assert proposed.endswith("The board's tiering remains the F1 one.")


def test_a_long_mcc_tie_set_is_counted_not_silently_elided():
    """The measured MCC tie set runs to 33 cells; the outcome must stay readable.

    Naming all of them turns a register field into a wall of labels, and
    dropping them without saying so hides the size of the tie. So the sentence
    names the leaders, counts the remainder, and points at the artefact.
    """
    ranking = [{"rank": i + 1, "ref": f"r::c{i}", "label": f"c{i}",
                "mcc": 0.9 - i / 100, "eval_f1": 0.5, "mcc_tier": 1}
               for i in range(9)]
    block = {"n_significant": 1, "n_pairs": 36, "n_tiers": 2,
             "tie_set": [r["ref"] for r in ranking], "ranking": ranking}
    sentence = b._mcc_family_sentence(block, ["r::c0"], ["r::c0", "r::c1"])
    assert "MCC Tier 1 = 9 cell(s)" in sentence
    assert sentence.count(" MCC 0.") == 5, "five leaders named"
    assert "and 4 more — full list in tiering_20m.json -> " \
        "mcc_permutation.tie_set" in sentence
    assert "MCC MCB admissible set = 1, of which 1 also in the F1 admissible " \
        "set" in sentence


def test_finalise_records_the_mcc_family_in_provenance(tmp_path, monkeypatch):
    """The MCC tie set and admissible set are provenance fields, not prose only."""
    board = _board(tmp_path, monkeypatch, mcc_block=MCC_BLOCK, mcc_mcb={
        "candidates": [{"ref": "runy::other"}], "hsu_not_ruled_out": [0],
        "mcb_not_ruled_out": [0]})
    _finalise(board)
    prov = json.loads((board / "provenance.json").read_text())["tiering"]
    assert prov["mcc_tie_set"] == ["runx::plain-n5-era2b"]
    assert prov["mcc_mcb_admissible_hsu"] == ["runy::other"]
    assert "_mcc_b20_m1.json" in prov["mcc_mcb"]
    assert prov["mcc_permutation"]["n_tiers"] == 2
    # The bulky arms stay in tiering_20m.json, not duplicated into provenance.
    for bulky in ("pairwise", "gates", "ranking", "tiers"):
        assert bulky not in prov["mcc_permutation"]
    # The F1 tiering is untouched by any of it.
    assert prov["tie_set"] == ["runx::plain-n5-era2b"]
    assert prov["mcb_admissible_hsu"] == ["runx::plain-n5-era2b"]


def test_finalise_omits_the_mcc_table_when_the_arm_did_not_run(tmp_path, monkeypatch):
    """An F1-only tiering must still finalise, with no MCC claims anywhere."""
    board = _board(tmp_path, monkeypatch)
    _finalise(board)
    readme = (board / "README.md").read_text()
    prov = json.loads((board / "provenance.json").read_text())
    assert "MCC rank" not in readme
    assert prov["tiering"]["mcc_permutation"] is None
    assert prov["tiering"]["mcc_mcb_admissible_hsu"] is None
    assert "REPORTED BESIDE" not in prov["re_sign_pending"]["proposed_outcome"]


def test_finalise_discloses_a_withheld_cells_shortfall_and_vocabularies(
        tmp_path, monkeypatch):
    """Ruling 6's five disclosures all reach the README."""
    board = _board(tmp_path, monkeypatch, withheld=[WITHHELD])
    _finalise(board)
    readme = (board / "README.md").read_text()
    # 1. the whole-frame F1 point estimate that survives the refusal
    assert "| `g37-text-k3-verified-opmax` | 0.8860 |" in readme
    # 2. the interval, withdrawn rather than superseded, and the one retracted
    assert "interval withdrawn (tile-resampled bootstrap) — was [0.3684, 0.7732]" \
        in readme
    assert "withdrawn, not superseded" in readme
    # 3. the shortfall counts
    assert "| 20 / 468 | 448 |" in readme
    # 4. both tile vocabularies
    assert "**The two tile vocabularies**" in readme
    assert "487 tiles, 487 distinct names" in readme
    assert "495 points naming 306 distinct tiles" in readme
    assert "only **11** are in the frame's vocabulary" in readme
    # 5. the published convention
    assert "**The name-based (`id`) tile join is the published convention**" in readme
    assert "neither BH family (F1 or tile-MCC)" in readme


def test_finalise_survives_a_withheld_cell_with_no_disclosure(tmp_path, monkeypatch):
    """A refusal whose detections cannot be rebuilt still lists its reason."""
    bare = {k: v for k, v in WITHHELD.items()
            if k not in ("disclosure", "withdrawn_interval_f1")}
    board = _board(tmp_path, monkeypatch, withheld=[bare])
    _finalise(board)
    readme = (board / "README.md").read_text()
    assert "| — | — |" in readme
    assert "tile_join_detection_shortfall" in readme


def test_finalise_nests_a_prior_pending_block_rather_than_erasing_it(
        tmp_path, monkeypatch):
    """A rebuild landing on a PENDING block keeps it as ``previous_pending``.

    Until 2026-09-13 ``finalise`` overwrote a pending block outright, which is
    why the recovery-fragment note had to keep a durable copy of its numbers in
    the README changelog. The trail is not a signature field and must survive.
    """
    prior = {
        "signed_at": "2026-09-12T06:04:30Z",
        "signature_history": [{"signed_at": "2026-09-10T12:34:56Z"}],
        "re_sign_pending": {
            "status": "PENDING — the PI re-signs",
            "proposed_outcome": "the 153-cell proposal",
            "previous_resolved": {"status": "RE-SIGNED 2026-09-12T06:04:30Z"},
        },
        "gates": {"G1": {"pi_ruling": {"ruling": "satisfied"}}},
    }
    board = _board(tmp_path, monkeypatch, prior=prior)
    _finalise(board)
    out = json.loads((board / "provenance.json").read_text())
    assert out["re_sign_pending"]["status"].startswith("PENDING")
    nested = out["re_sign_pending"]["previous_pending"]
    assert nested["proposed_outcome"] == "the 153-cell proposal"
    assert nested["previous_resolved"]["status"].startswith("RE-SIGNED")
    assert "previous_pending" in " ".join(out["_carried_forward"]["fields"])
    # And the signature fields themselves are carried, not rebuilt away.
    assert out["signed_at"] == "2026-09-12T06:04:30Z"
    assert out["signature_history"] == prior["signature_history"]
    assert out["gates"]["G1"]["pi_ruling"] == {"ruling": "satisfied"}
