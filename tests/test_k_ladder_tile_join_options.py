"""Tier-1 tests for the tile-join options of the two K-ladder instruments.

**Revised for tile-join Wave 1 (2026-11-18, PI rulings D72 and D73).**
``TILE_JOIN_DEFAULT`` is retired. Both drivers now take ``--tile-join``
(classification, default ``sheet-contains``) and ``--count-table-join``
(default ``sheet-primary``) and pass BOTH explicitly to the instrument on
every run; a non-default rule is stamped into the artefact name; the
MCC-test driver adds a validation run under the committed recipe (``id``,
``id``) for its board gate whenever the count-table join is not ``id``; the
rung MCC values are the requested join's own unless it is ``id``; and no
published value is written beside them. The MCB gate reads a tiering only
under the classification join that tiering records. The 2026-10-30 text
below describes the superseded behaviour.

Added 2026-10-30 (S166 K-ladder tile-join job,
``reports/s166-agent-records/k-ladder-mcc-join.md``). The K-ladder tile-MCC
findings were computed under the published name join (``id``); this job reads
them again under the two geometric joins. ``scripts/k_ladder_mcc_test.py`` and
``scripts/k_ladder_mcb.py`` gained a ``--tile-join`` option that passes a
geometric join through to the instruments that already accept one
(``era1_leaderboard_tiering.py`` and ``selection_aware_intervals.py``).

Two properties are pinned:

1. **The default is the committed behaviour.** Under ``id`` the harness and
   tool commands carry no new flag, the artefacts keep their published names,
   the outputs carry no new key, the rung MCC values are the inventory's, and
   the MCB gate reads the ranking's ``mcc`` column as before.
2. **A geometric join is carried through and read back as itself.** The flag
   reaches the instrument, the join-stamped artefact is read, each pair's rung
   MCC values are the join's (with the published join's beside them), the
   MCB gate compares against the join's MCC and refuses a tiering written
   under any other join, and the option is refused where it would change
   nothing (the F1 metric) or could not be gated (no registry).

Everything runs on synthetic fixtures with the subprocess boundary
monkeypatched; no committed data file is read and no instrument is run.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import scripts.k_ladder_mcb as mcb
import scripts.k_ladder_mcc_test as kt
import scripts.selection_aware_intervals as sai
pytestmark = pytest.mark.tier1

PRIMARY = "geometric-primary"
CONTAINS = "geometric-contains"
SHEET = "sheet-contains"
SHEET_PRIMARY = "sheet-primary"

#: The keys a run of the MCC-test driver writes. Wave 1 added ``tile_join``
#: (always) and ``tile_joins`` (both rules) to the pre-Wave-1 key set.
PAYLOAD_KEYS = [
    "ladder", "family", "run_id", "proposer_pool", "corpus", "reference_file",
    "frame_file", "headline_buffer_m", "basis", "instrument", "gate", "pairs",
    "tiering_artefact", "tile_joins", "generated_at_utc", "tile_join",
]
LEGACY_MCC_KEYS = ["low", "high", "delta", "p_raw", "p_bh", "significant"]
SUMMARY_KEYS = [
    "generated_at_utc", "source_inventory", "conditions", "n_permutations",
    "seed", "n_ladders", "gate_all_passed", "ladders", "tile_joins",
]


# ── fixtures ──────────────────────────────────────────────────────────────

def _inventory(tmp_path: Path) -> Path:
    """A one-ladder, three-rung inventory shaped as ``ladders.json``.

    Args:
        tmp_path: Pytest's temporary directory.

    Returns:
        Path to the written inventory.
    """
    rungs = [
        {"K": k, "condition_id": f"run::rung-k{k}",
         "eval_path": f"results/synthetic/cells/rung-k{k}/evaluation.json",
         "f1_headline": f1, "tile_mcc": mcc}
        for k, f1, mcc in ((1, 0.80, 0.70), (3, 0.84, 0.69), (5, 0.85, 0.68))
    ]
    path = tmp_path / "ladders.json"
    path.write_text(json.dumps({"ladders": [{
        "slug": "synthetic-ladder", "family_base": "synthetic family",
        "run_id": "run", "proposer_pool": "pool", "corpus": "4-map-gs",
        "reference_file": "ref.geojson", "frame_file": "frame.geojson",
        "headline_buffer_m": 20, "rungs": rungs,
    }]}))
    return path


def _tiering(tile_join: str | None, count_table_join: str = SHEET_PRIMARY,
             ) -> dict[str, Any]:
    """A tiering result shaped as ``era1_leaderboard_tiering.py`` writes it.

    The requested join's MCC values (0.81 / 0.83 / 0.85, rising with K)
    differ from the inventory's ``id`` ones (0.70 / 0.69 / 0.68, falling), so
    a test can tell which source a reported rung value came from.

    Args:
        tile_join: The classification join the MCC arm ran under; ``None``
            builds a pre-Wave-1 (legacy ``id``) tiering, which records no join.
        count_table_join: The F1 arm's count-table join (Wave 1 tierings).

    Returns:
        The tiering dict.
    """
    refs = ["run::rung-k1", "run::rung-k3", "run::rung-k5"]
    legacy = tile_join in (None, "id")
    values = dict(zip(refs, (0.70, 0.69, 0.68) if legacy else (0.81, 0.83, 0.85),
                      strict=True))
    pairwise, pairwise_mcc = [], []
    for i, a in enumerate(refs):
        for b in refs[i + 1:]:
            pairwise.append({"ref_a": a, "ref_b": b, "observed_diff": -0.02,
                             "p_value": 0.01, "bh_adjusted_p": 0.02,
                             "significant": True, "f1_a": 0.8, "f1_b": 0.82,
                             "n_tiles": 10})
            pairwise_mcc.append({"ref_a": a, "ref_b": b,
                                 "observed_mcc_diff": values[a] - values[b],
                                 "p_value": 0.5, "bh_adjusted_p": 0.6,
                                 "significant": False})
    block: dict[str, Any] = {
        "pairwise": pairwise_mcc, "gates": {r: {"passed": True} for r in refs},
        "n_cells_withheld": 0,
        "ranking": [{"ref": r, "label": r.split("::")[1], "mcc": values[r]}
                    for r in refs],
    }
    out: dict[str, Any] = {
        "n_tiles": 10, "n_permutations": 100, "seed": 42, "fdr_q": 0.05,
        "n_cells_withheld": 0, "pairwise": pairwise,
        "ranking": [{"ref": r, "label": r.split("::")[1],
                     "observed_micro_f1": 0.8, "mcc": values[r]} for r in refs],
        "mcc_permutation": block}
    if tile_join is not None:
        block["tile_join"] = tile_join
        block["tile_join_note"] = "Wave 1 tiering"
        out["tile_joins"] = {"classification": tile_join,
                             "count_table": count_table_join}
        out["count_table_join"] = count_table_join
    return out


def _run_driver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                extra: list[str]) -> tuple[dict, dict, list[tuple[str, str]]]:
    """Run the MCC-test driver's ``main`` over the synthetic inventory.

    Args:
        tmp_path: Pytest's temporary directory.
        monkeypatch: Pytest's monkeypatch fixture.
        extra: Extra command-line arguments.

    Returns:
        ``(ladder_payload, summary, (classification, count_table) per run)``.
    """
    tmp_path.mkdir(parents=True, exist_ok=True)
    seen: list[tuple[str, str]] = []

    def fake_run_tiering(*args: Any, **kwargs: Any) -> dict:
        # The driver passes both joins positionally after the seed.
        tile_join = kwargs.get("tile_join", args[8] if len(args) > 8 else None)
        count_table = kwargs.get("count_table_join",
                                 args[9] if len(args) > 9 else None)
        seen.append((tile_join, count_table))
        return _tiering(tile_join, count_table)

    monkeypatch.setattr(kt, "run_tiering", fake_run_tiering)
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", [
        "k_ladder_mcc_test.py", "--ladders", str(_inventory(tmp_path)),
        "--output-dir", str(out), *extra])
    assert kt.main() == 0
    payload = json.loads((out / "synthetic-ladder.json").read_text())
    summary = json.loads((out / "summary.json").read_text())
    return payload, summary, seen


def _capture(monkeypatch: pytest.MonkeyPatch, module: Any,
             write: Path) -> list[list[str]]:
    """Capture the instrument command and write the file it would write.

    Args:
        monkeypatch: Pytest's monkeypatch fixture.
        module: The driver module whose ``subprocess.run`` is replaced.
        write: The artefact the fake instrument writes.

    Returns:
        A list that receives each captured command.
    """
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
        calls.append(list(cmd))
        write.parent.mkdir(parents=True, exist_ok=True)
        write.write_text(json.dumps({"written": write.name}))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    return calls


# ── k_ladder_mcc_test.py ─────────────────────────────────────────────────

def test_mcc_test_tiering_name_stamps_every_non_default_rule() -> None:
    """The defaults keep the plain name; any other rule is stamped in."""
    assert kt.tiering_name(20) == "tiering_20m.json"
    assert kt.tiering_name(50, "id", "id") == "tiering_50m_id_ct-id.json"
    assert kt.tiering_name(20, PRIMARY) == "tiering_20m_geometric-primary.json"
    assert kt.tiering_name(50, CONTAINS, "id") == \
        "tiering_50m_geometric-contains_ct-id.json"


def test_run_tiering_names_both_joins_explicitly(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The harness is always told both rules, defaults included."""
    calls = _capture(monkeypatch, kt, tmp_path / "tiering_20m.json")
    result = kt.run_tiering(Path("a.json"), Path("c.json"), "aid", tmp_path,
                            20, None, 100, 42)
    assert calls[0][-4:] == ["--tile-join", SHEET, "--count-table-join", SHEET_PRIMARY]
    assert "--permute-mcc" in calls[0]
    assert result == {"written": "tiering_20m.json"}


def test_run_tiering_passes_a_geometric_join_and_reads_its_file(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A geometric join reaches the harness and its stamped file is read."""
    calls = _capture(monkeypatch, kt,
                     tmp_path / "tiering_20m_geometric-primary.json")
    result = kt.run_tiering(Path("a.json"), Path("c.json"), "aid", tmp_path,
                            20, Path("b.geojson"), 100, 42, tile_join=PRIMARY)
    assert calls[0][-4:] == ["--tile-join", PRIMARY, "--count-table-join", SHEET_PRIMARY]
    assert "--permute-mcc" in calls[0]
    assert result == {"written": "tiering_20m_geometric-primary.json"}


def test_driver_default_validates_under_id_then_reports_the_new_rules(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Default run: the requested run, then the (id, id) board-gate run; the
    rung MCC values are the requested join's, with nothing of id's beside."""
    payload, summary, seen = _run_driver(tmp_path, monkeypatch, [])
    assert seen == [(SHEET, SHEET_PRIMARY), ("id", "id")]
    assert list(payload) == PAYLOAD_KEYS
    assert list(summary) == SUMMARY_KEYS
    first = payload["pairs"][0]
    assert (first["mcc"]["low"], first["mcc"]["high"]) == (0.81, 0.85)
    assert "low_published_join" not in first["mcc"]
    assert payload["tiering_artefact"].endswith("tiering_20m.json")
    assert payload["tile_join"]["board_gate_run"].endswith("tiering_20m_id_ct-id.json")
    assert payload["tile_joins"]["classification"] == SHEET


def test_driver_id_replay_is_the_committed_reading(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``--tile-join id --count-table-join id`` runs once and reads the
    inventory's rung values, as the committed runs did."""
    payload, _summary, seen = _run_driver(
        tmp_path, monkeypatch, ["--tile-join", "id", "--count-table-join", "id"])
    assert seen == [("id", "id")]
    first = payload["pairs"][0]
    assert list(first["mcc"]) == LEGACY_MCC_KEYS
    assert (first["mcc"]["low"], first["mcc"]["high"]) == (0.70, 0.68)
    assert payload["tiering_artefact"].endswith("tiering_20m_id_ct-id.json")


def test_driver_geometric_reports_the_joins_rung_values(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Under a join the rung values are the join's, and only the join's."""
    payload, summary, seen = _run_driver(tmp_path, monkeypatch,
                                         ["--tile-join", CONTAINS])
    assert seen == [(CONTAINS, SHEET_PRIMARY), ("id", "id")]
    headline = payload["pairs"][0]
    assert headline["pair"] == "K1-vs-K5"
    mcc = headline["mcc"]
    assert mcc["tile_join"] == CONTAINS
    assert (mcc["low"], mcc["high"]) == (0.81, 0.85)
    assert "low_published_join" not in mcc
    # The delta is oriented (higher K) - (lower K) and is the join's own.
    assert mcc["delta"] == pytest.approx(0.04, abs=1e-9)
    assert payload["tile_join"]["join"] == CONTAINS
    assert payload["tile_join"]["n_cells_withheld_mcc_arm"] == 0
    assert payload["tiering_artefact"].endswith(
        "tiering_20m_geometric-contains.json")
    assert summary["tile_joins"]["classification"] == CONTAINS
    assert summary["ladders"][0]["n_cells_withheld_mcc_arm"] == 0


def test_join_mcc_by_ref_refuses_a_tiering_that_records_no_join() -> None:
    """Reading join values out of a legacy tiering would mislabel them."""
    with pytest.raises(ValueError, match="records no classification join"):
        kt.join_mcc_by_ref(_tiering(None))
    values = kt.join_mcc_by_ref(_tiering(PRIMARY))
    assert values["run::rung-k1"] == 0.81


# ── k_ladder_mcb.py ──────────────────────────────────────────────────────

def test_mcb_artefact_name_stamps_every_non_default_rule() -> None:
    """The default names are plain; any other rule is stamped in."""
    assert mcb.artefact_name("aid", "f1", 20) == "aid_b20_m1.json"
    assert mcb.artefact_name("aid", "mcc", 50) == "aid_mcc_b50_m1.json"
    assert mcb.artefact_name("aid", "mcc", 20, PRIMARY) == \
        "aid_mcc_geometric-primary_b20_m1.json"
    assert mcb.artefact_name("aid", "f1", 20, "id", "id") == "aid_ct-id_b20_m1.json"
    assert mcb.artefact_name("aid", "mcc", 20, "id", "id") == \
        "aid_mcc_id_ct-id_b20_m1.json"


def test_run_mcb_names_both_joins_explicitly(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The tool is always told its rules; F1 gets no classification join."""
    entry = {"analysis_id": "aid", "analyses": Path("a.json"), "buffer_m": 20,
             "conditions": None, "bounds": None}
    calls = _capture(monkeypatch, mcb, tmp_path / "aid_mcc_b20_m1.json")
    path, _result = mcb.run_mcb(entry, "mcc", tmp_path, 100)
    assert calls[0][-4:] == ["--tile-join", SHEET, "--count-table-join", SHEET_PRIMARY]
    assert path.name == "aid_mcc_b20_m1.json"
    calls = _capture(monkeypatch, mcb, tmp_path / "aid_b20_m1.json")
    mcb.run_mcb(entry, "f1", tmp_path, 100)
    assert "--tile-join" not in calls[0]
    assert calls[0][-2:] == ["--count-table-join", SHEET_PRIMARY]


def test_run_mcb_passes_a_geometric_join_for_mcc_only(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A join reaches the tool on the MCC metric and is refused on F1."""
    entry = {"analysis_id": "aid", "analyses": Path("a.json"), "buffer_m": 20,
             "conditions": None, "bounds": "b.geojson"}
    calls = _capture(monkeypatch, mcb,
                     tmp_path / "aid_mcc_geometric-contains_b20_m1.json")
    path, _ = mcb.run_mcb(entry, "mcc", tmp_path, 100, tile_join=CONTAINS)
    assert calls[0][-4:] == ["--tile-join", CONTAINS, "--count-table-join", SHEET_PRIMARY]
    assert path.name == "aid_mcc_geometric-contains_b20_m1.json"
    with pytest.raises(ValueError, match="MCC metric only"):
        mcb.run_mcb(entry, "f1", tmp_path, 100, tile_join=CONTAINS)


def test_committed_ranking_reads_the_joins_mcc_under_its_join(
        tmp_path: Path) -> None:
    """The gate reference is read only under the join the tiering records."""
    path = tmp_path / "tiering_20m_geometric-primary.json"
    path.write_text(json.dumps(_tiering(PRIMARY)))
    joined = mcb.committed_ranking(path, PRIMARY)
    assert joined["rung-k1"] == {"f1": 0.8, "mcc": 0.81}
    labels_only = mcb.committed_ranking(path, SHEET, require_mcc_join=False)
    assert labels_only["rung-k1"] == {"f1": 0.8}
    legacy = tmp_path / "tiering_20m.json"
    legacy.write_text(json.dumps(_tiering(None)))
    assert mcb.committed_ranking(legacy, "id")["rung-k1"] == {"f1": 0.8, "mcc": 0.70}


def test_committed_ranking_refuses_another_joins_tiering(tmp_path: Path) -> None:
    """A tiering of another classification join is not a reference."""
    published = tmp_path / "tiering_20m.json"
    published.write_text(json.dumps(_tiering(None)))
    other = tmp_path / "tiering_20m_geometric-contains.json"
    other.write_text(json.dumps(_tiering(CONTAINS)))
    with pytest.raises(ValueError, match="not 'geometric-primary'"):
        mcb.committed_ranking(published, PRIMARY)
    with pytest.raises(ValueError, match="not 'geometric-primary'"):
        mcb.committed_ranking(other, PRIMARY)
    with pytest.raises(ValueError, match="not 'sheet-contains'"):
        mcb.committed_ranking(published)


def test_mcb_gate_under_a_join_refuses_the_published_values(
        tmp_path: Path) -> None:
    """An MCB statistic that equals the published MCC, not the join's, fails.

    This is the failure the join-aware reference exists to catch: indicators
    silently built under ``id`` while the run claims a geometric join.
    """
    path = tmp_path / "tiering_20m_geometric-primary.json"
    path.write_text(json.dumps(_tiering(PRIMARY)))
    committed = mcb.committed_ranking(path, PRIMARY)

    def result_with(stats: list[float]) -> dict[str, Any]:
        best = int(np.argmax(stats))
        others = [max(s for j, s in enumerate(stats) if j != i)
                  for i in range(len(stats))]
        return {"kept_indices": [0, 1, 2], "selected_index": best,
                "apparent_f1": stats[best],
                "mcb_theta": [s - o for s, o in zip(stats, others, strict=True)],
                "candidates": [{"label": f"rung-k{k}"} for k in (1, 3, 5)]}

    record = mcb.gate({"slug": "s"}, "mcc", result_with([0.81, 0.83, 0.85]),
                      committed)
    assert record["passed"] is True
    with pytest.raises(ValueError, match="against committed"):
        mcb.gate({"slug": "s"}, "mcc", result_with([0.70, 0.69, 0.68]),
                 committed)


@pytest.mark.parametrize("argv, message", [
    (["--count-table-join", CONTAINS], "invalid choice"),
    (["--tile-join", SHEET_PRIMARY], "invalid choice"),
])
def test_mcb_main_refuses_a_join_named_for_the_wrong_purpose(
        argv: list[str], message: str, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    """A containment join for the count table, or a count-table join for the
    classification, is refused at the command line (D72 (2))."""
    monkeypatch.setattr(sys, "argv", ["k_ladder_mcb.py", *argv])
    with pytest.raises(SystemExit):
        mcb.main()
    assert message in capsys.readouterr().err


def test_mcb_join_indicators_differ_from_the_published_ones() -> None:
    """Sanity: the tool's MCC statistic follows the indicators it is given.

    The geometric MCB path hands ``run`` the join's ``has_det``; if the tool
    ignored it, every join would return the published statistic.
    """
    # A six-tile pattern repeated twenty times, so the bootstrap is defined.
    counts = np.zeros((2, 120, 3))
    counts[:, :, 0] = np.tile([[1, 0, 0, 1, 0, 0], [1, 1, 0, 0, 0, 0]], 20)
    mounds = np.tile([True, True, False, True, False, False], 20)
    has_det = np.tile([[True, True, False, True, False, False],
                       [True, False, False, False, False, False]], 20)
    legacy = sai.run(counts, 50, 1.0, 42, has_mounds=mounds, metric="mcc")
    joined = sai.run(counts, 50, 1.0, 42, has_mounds=mounds, metric="mcc",
                     has_det=has_det)
    assert joined["apparent_f1"] != pytest.approx(legacy["apparent_f1"])
