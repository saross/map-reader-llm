"""Tests for scripts/k_ladder_mcb.py — the per-family Hsu MCB driver.

Added 2026-09-13 with the driver, which supplies the K-ladder review's one
outstanding run-card requirement (findings § 6.1 / § 7.5: a Hsu
multiple-comparisons-with-the-best admissible set per family) by invoking the
Era-2 board's own MCB tool once per ladder per metric.

The driver reimplements no statistics, so these tests target what it does own:

* the admissible set expressed in pass counts K, on a SYNTHETIC four-rung
  ladder run through the real instrument — the empirical best rung is always
  admissible, a ladder of four indistinguishable rungs is admissible whole,
  and the ``contains_K3`` / ``excludes_K10`` / ``whole_ladder`` flags the
  findings quote are consistent with the set they summarise;
* ``recover_statistics``, which reads every rung's statistic back out of the
  tool's published ``apparent_f1`` and ``mcb_theta`` — the gate depends on it;
* the gate itself, which must refuse a changed label set and a drifted
  statistic rather than reporting an admissible set over the wrong cells;
* the registry, whose whole purpose is that every ladder is computed on its
  OWN frame and reference.

Added 2026-10-31 (S167, after the S166 K-ladder tile-join record § 4 item 6):

* the DEFAULT path, replayed. ``main`` with the committed registry runs end to
  end over the committed per-ladder artefacts, in place of the bootstrap
  subprocess, and reproduces the committed ``mcb/summary.json`` (all but its
  timestamp) and ``mcb/table.md`` byte for byte. Each replayed artefact must
  also record the call the default would make today: board, metric, buffer,
  bootstrap, seed and input paths;
* the red sentinel. An inventory cut the way ``0fc2d6389`` cut the compat
  export is refused at launch, before any bootstrap, with every missing label
  named;
* PI ruling D71's label: for the seven ladders now reported on D51's clipped
  basis, the default is the as-evaluated record. That label holds only while
  the clipped sets (S166) agree with it on every admissible K set and best K.

Red sentinel, run 2026-10-31: on the pre-fix script (a git worktree of
``86a6c19f9``, real files), 4 tests fail and 16 pass. The replay fails in
``summarise`` with ``KeyError: 'pv-min-text-t0.3-n1-opmax'``, the S166
defect. The label-join test fails with "no K for pv-min-text-t0.3-n5-opmax".
The slug and refusal tests fail because the functions they call do not
exist yet. On the fixed script all 20 pass. The D71 test was added after
that run, with its own sentinel. A copy of the clipped summary with K = 3
removed from tier E's F1 set turns it red on ``('tier-e', 'f1')``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import scripts.k_ladder_mcb as mcb
import scripts.selection_aware_intervals as sai

pytestmark = pytest.mark.tier1

#: A four-rung ladder's pass counts, in the order the synthetic candidates are
#: built. Matches every real ladder of the review that has four rungs.
RUNG_KS = (1, 3, 5, 10)
RUNG_LABELS = tuple(f"synthetic-ladder-n{k}-opmax" for k in RUNG_KS)
K_OF = dict(zip(RUNG_LABELS, RUNG_KS, strict=True))


def _separated_ladder(n_tiles: int = 120) -> np.ndarray:
    """A four-rung ladder whose rungs are cleanly ordered in F1.

    Rung K = 10 is best and K = 1 clearly worst, with K = 3 and K = 5 between
    them — the shape every HIGH-thinking ladder of § 7.1 has.

    Args:
        n_tiles: Tiles to spread the counts over.

    Returns:
        Per-tile TP/FP/FN counts shaped ``(4, n_tiles, 3)``.
    """
    counts = np.zeros((4, n_tiles, 3), dtype=float)
    # False positives and negatives fall as K rises; true positives climb.
    for index, (tp, fp, fn) in enumerate([(2, 4, 4), (3, 3, 3), (4, 2, 2),
                                          (5, 1, 1)]):
        counts[index, :, 0] = tp
        counts[index, :, 1] = fp
        counts[index, :, 2] = fn
    return counts


def _flat_ladder(n_tiles: int = 120) -> np.ndarray:
    """Four rungs that differ only by noise: K buys nothing detectable.

    This is the shape four of the six MINIMAL Phase 2 ladders have (§ 7.1,
    "greedy-clique into a single tier"), so the admissible set must be the whole
    ladder. The rungs differ tile by tile — as real rungs do — while holding the
    same aggregate rates, rather than being byte-identical, which is the
    degenerate case pinned separately below.

    Args:
        n_tiles: Tiles to spread the counts over.

    Returns:
        Per-tile TP/FP/FN counts shaped ``(4, n_tiles, 3)``.
    """
    rng = np.random.default_rng(11)
    counts = np.zeros((4, n_tiles, 3), dtype=float)
    for index in range(4):
        counts[index, :, 0] = rng.integers(2, 5, n_tiles)
        counts[index, :, 1] = rng.integers(1, 4, n_tiles)
        counts[index, :, 2] = rng.integers(1, 4, n_tiles)
    return counts


def _identical_ladder(n_tiles: int = 120) -> np.ndarray:
    """Four byte-identical rungs — the degenerate exact tie.

    Args:
        n_tiles: Tiles to spread the counts over.

    Returns:
        Per-tile TP/FP/FN counts shaped ``(4, n_tiles, 3)``.
    """
    counts = np.zeros((4, n_tiles, 3), dtype=float)
    counts[:, :, 0] = 3
    counts[:, :, 1] = 2
    counts[:, :, 2] = 2
    return counts


def _result(counts: np.ndarray, bootstrap: int = 400) -> dict[str, Any]:
    """Run the real instrument over synthetic counts and label the candidates.

    Args:
        counts: Per-tile TP/FP/FN counts shaped ``(4, n_tiles, 3)``.
        bootstrap: Bootstrap resamples; small, because the assertions are about
            set semantics rather than about a reportable critical width.

    Returns:
        An MCB artefact shaped as ``selection_aware_intervals.main`` writes it.
    """
    result = sai.run(counts, bootstrap, mcb.M_FRAC, mcb.SEED, metric="f1")
    result["candidates"] = [{"label": label, "eval_f1": None}
                            for label in RUNG_LABELS]
    return result


# ── the admissible set, in pass counts ────────────────────────────────


def test_separated_ladder_summary_is_consistent_with_its_own_set() -> None:
    """Every flag the findings quote must agree with the set it summarises."""
    entry = {"slug": "synthetic", "buffer_m": 20}
    block = mcb.summarise(entry, _result(_separated_ladder()), K_OF)

    admissible = block["hsu_admissible_K"]
    assert admissible == sorted(set(admissible)), "set must be sorted, unique"
    assert set(admissible) <= set(RUNG_KS)
    assert block["best_K"] == 10, "K = 10 holds the highest synthetic F1"
    # Hsu's construction cannot rule out the empirical best: its theta is
    # best - second > 0, so its upper bound is strictly positive.
    assert block["best_K"] in admissible
    assert block["contains_K3"] is (3 in admissible)
    assert block["excludes_K10"] is (10 not in admissible)
    assert block["whole_ladder"] is (len(admissible) == len(RUNG_KS))
    assert block["n_candidates"] == 4
    assert block["hsu_w_upper"] >= 0.0


def test_a_ladder_of_indistinguishable_rungs_is_admissible_whole() -> None:
    """Rungs that differ only by noise: K buys nothing, none is ruled out."""
    block = mcb.summarise({"slug": "flat", "buffer_m": 20},
                          _result(_flat_ladder()), K_OF)
    assert block["hsu_admissible_K"] == [1, 3, 5, 10]
    assert block["whole_ladder"] is True
    assert block["contains_K3"] is True
    assert block["excludes_K10"] is False
    assert block["degenerate_zero_width"] is False


def test_byte_identical_rungs_are_flagged_as_a_degenerate_tie() -> None:
    """An exact tie zeroes the critical width, so the empty set is legible.

    Hsu's rule admits a candidate only when ``theta_i + w_upper > 0``. Four
    byte-identical rungs give ``theta_i = 0`` on every resample, so
    ``w_upper = 0`` and the strict inequality rules out even the empirical best.
    No real ladder is byte-identical, but an empty admissible set must be
    readable as this artefact rather than as a finding.
    """
    block = mcb.summarise({"slug": "identical", "buffer_m": 20},
                          _result(_identical_ladder()), K_OF)
    assert block["hsu_w_upper"] == 0.0
    assert block["hsu_admissible_K"] == []
    assert block["degenerate_zero_width"] is True


def test_hsu_set_is_a_subset_of_the_two_sided_band() -> None:
    """The conservative two-sided band can only admit more rungs, never fewer."""
    block = mcb.summarise({"slug": "synthetic", "buffer_m": 20},
                          _result(_separated_ladder()), K_OF)
    assert set(block["hsu_admissible_K"]) <= set(block["two_sided_band_K"])


# ── recover_statistics, which the gate depends on ─────────────────────


def test_recover_statistics_reproduces_every_rung_statistic() -> None:
    """Reading statistics back out of theta must be exact, not approximate."""
    counts = _separated_ladder()
    result = _result(counts)
    expected = sai.f1_from_counts(counts)
    recovered = mcb.recover_statistics(result)
    assert np.allclose(recovered, expected, atol=1e-12)


# ── the gate ──────────────────────────────────────────────────────────


def _committed(counts: np.ndarray) -> dict[str, dict[str, float]]:
    """The per-rung statistics a real tiering artefact's ranking would record."""
    return {label: {"f1": round(float(value), 6), "mcc": 0.5}
            for label, value
            in zip(RUNG_LABELS, sai.f1_from_counts(counts), strict=True)}


def test_gate_passes_on_a_faithful_reproduction() -> None:
    """A run over the committed cells at the committed points must pass."""
    counts = _separated_ladder()
    record = mcb.gate({"slug": "synthetic"}, "f1", _result(counts),
                      _committed(counts))
    assert record["passed"] is True
    assert record["n_candidates_gated"] == 4
    assert all(row["abs_delta"] <= mcb.F1_GATE_TOL
               for row in record["candidates"])


def test_gate_refuses_a_changed_candidate_set() -> None:
    """An admissible set over the wrong cells is worse than none at all."""
    counts = _separated_ladder()
    committed = _committed(counts)
    committed["an-extra-rung-that-was-not-run"] = {"f1": 0.5, "mcc": 0.5}
    with pytest.raises(ValueError, match="do not match the committed tiering"):
        mcb.gate({"slug": "synthetic"}, "f1", _result(counts), committed)


def test_gate_refuses_a_drifted_statistic() -> None:
    """A rung scoring differently than its committed evaluation must abort."""
    counts = _separated_ladder()
    committed = _committed(counts)
    committed[RUNG_LABELS[0]]["f1"] += 0.01
    with pytest.raises(ValueError, match="against committed"):
        mcb.gate({"slug": "synthetic"}, "f1", _result(counts), committed)


def test_mcc_gate_reads_the_rankings_mcc_column() -> None:
    """The MCC arm is gated against tile-MCC, so a missing one must abort."""
    counts = _separated_ladder()
    result = _result(counts)
    result["metric"] = "mcc"
    committed = _committed(counts)
    for row in committed.values():
        del row["mcc"]
    with pytest.raises(ValueError, match="records no mcc"):
        mcb.gate({"slug": "synthetic"}, "mcc", result, committed)


def test_gate_reference_comes_from_the_tiering_not_the_inventory() -> None:
    """The gold-standard ladder's frames disagree on tile-MCC; the gate must
    read the frame the MCB actually runs on.

    Its committed tiering is on the board frame (K = 1 tile-MCC 0.7948) while
    `ladders.json` records the grid-common frame (0.8010). Gating against the
    inventory would refuse a correct run, so this pins the source.

    Dated update 2026-10-15 (S164 restatement pass, D58 Q6): the D62 (1)
    re-verified rows moved the board-frame rung (`f53f6e97c`); the pins were
    0.7834 (MCC) and 0.8605 (F1), and the grid-common reading was 0.7894.
    """
    ranking = mcb.committed_ranking(
        mcb.K_LADDER_DIR / "mcc-test/tiering/gs-stride-a/tiering_20m.json")
    k1 = ranking["g384-ov128-ladder-n1-verified-p0.15-k1"]
    assert k1["mcc"] == pytest.approx(0.7948, abs=1e-4)  # was 0.7834
    assert k1["f1"] == pytest.approx(0.8665, abs=1e-4)  # was 0.8605


# ── the registry ──────────────────────────────────────────────────────


def test_registry_covers_every_tiered_ladder_exactly_once() -> None:
    """Twenty-two tiered ladders: gold standard, tier E, thirteen, seven."""
    registry = mcb.ladder_registry()
    slugs = [entry["slug"] for entry in registry]
    assert len(slugs) == len(set(slugs)), "a ladder must not appear twice"
    assert len(registry) == 22
    groups = [entry["group"] for entry in registry]
    assert groups.count("Phase 2 (pv-diag-384)") == 13
    assert groups.count("55-map deployment") == 7
    assert groups.count("gold standard") == 1
    assert groups.count("tier E") == 1


def test_every_registry_entry_names_committed_inputs() -> None:
    """A ladder computed on a frame it was not tiered on answers nothing."""
    for entry in mcb.ladder_registry():
        for key in ("analyses", "tiering"):
            path = mcb.BASE_DIR / entry[key]
            assert path.exists(), f"{entry['slug']}: missing {key} {path}"
        if entry["conditions"]:
            assert (mcb.BASE_DIR / entry["conditions"]).exists()
        if entry["bounds"]:
            assert (mcb.BASE_DIR / entry["bounds"]).exists()
        assert entry["buffer_m"] in (20, 50)


def test_registry_analysis_ids_match_the_committed_tierings() -> None:
    """The MCB must read the same analysis row the committed tiering tiered."""
    for entry in mcb.ladder_registry():
        tiering = json.loads(
            (mcb.BASE_DIR / entry["tiering"]).read_text(encoding="utf-8"))
        assert tiering["analysis_id"] == entry["analysis_id"], entry["slug"]
        assert int(tiering["buffer_metres"]) == entry["buffer_m"], entry["slug"]


#: Dated 2026-10-15 (S164 restatement pass, record § 10): the Phase 2
#: builder now reports these six Gemini 3 ``pv-diag-384`` ladders on the D51
#: clipped basis (D57 (2), (3)) and withholds them from
#: ``phase2/ladders-compat.json`` "until the clipped cells exist", so their
#: committed MCB rankings (as evaluated, unclipped) no longer join to a K
#: through the inventory. Whether to re-run their MCB and MCC test on clipped
#: cells or keep them with a disclosure is for the PI; until then the gap is
#: pinned here, so any other unjoinable label still fails.
#:
#: Dated update 2026-10-31 (S167): pinning the gap hid a defect. The default
#: registry could not run (S166 K-ladder tile-join record § 4 item 6). The
#: driver now joins K through the canonical ``phase2/ladders.json``, which
#: keeps these six ladders, so their labels must join. They stay named here
#: so their join is asserted explicitly rather than by omission.
WITHHELD_ON_THE_CLIPPED_BASIS = frozenset({
    "phase2-flash-minimal-text-n30-t07-text-t0-3",
    "phase2-flash-minimal-text-n30-t07-text-t1-0",
    "phase2-flash-high-text-n5-text-t1-0",
    "phase2-image-n5-image-t0-3",
    "phase2-image-n5-image-t0-7",
    "phase2-image-n5-image-t1-0",
})


def test_label_to_k_covers_every_committed_ranking_label() -> None:
    """An admissible set is only useful as a statement about K.

    Every committed ranking label joins to a K. That includes the 24 labels
    of the six ladders the compat export withholds on the D51 clipped basis,
    because their committed as-evaluated MCB rankings are still in the
    registry (dated update 2026-10-31; the test previously asserted the
    opposite).
    """
    k_of = mcb.label_to_k()
    registry = mcb.ladder_registry()
    for entry in registry:
        labels = list(mcb.committed_ranking(entry["tiering"]))
        assert labels, entry["slug"]
        for label in labels:
            assert label in k_of, f"{entry['slug']}: no K for {label}"
    withheld = [label for entry in registry
                if entry["slug"] in WITHHELD_ON_THE_CLIPPED_BASIS
                for label in mcb.committed_ranking(entry["tiering"])]
    assert len(withheld) == 24, "six four-rung ladders"
    assert mcb.unjoined_labels(registry, k_of) == []


def test_phase2_slug_matches_the_builders_export() -> None:
    """The canonical inventory names no slugs, so the driver rebuilds them.

    The rebuilt slug must equal the one the builder writes into its export,
    on every ladder the export still carries. It must also cover every Phase
    2 ladder of the registry, so every row of the table gets its family name.
    """
    compat = json.loads(
        (mcb.BASE_DIR / mcb.K_LADDER_DIR / "phase2/ladders-compat.json")
        .read_text(encoding="utf-8"))
    assert compat["ladders"]
    for ladder in compat["ladders"]:
        assert mcb.phase2_slug(ladder["proposer_pool"]) == ladder["slug"]
    inventory = json.loads(
        (mcb.BASE_DIR / mcb.PHASE2_INVENTORY).read_text(encoding="utf-8"))
    slugs = {mcb.phase2_slug(ladder["proposer_pool"])
             for ladder in inventory["ladders"]}
    assert set(mcb.PHASE2_SLUGS) <= slugs
    names = mcb.display_names()
    for entry in mcb.ladder_registry():
        assert entry["slug"] in names, entry["slug"]


def test_withheld_family_is_recorded_with_its_three_cells() -> None:
    """The withholding is reported, never silently dropped."""
    assert len(mcb.WITHHELD["cells_withheld"]) == 3
    assert mcb.WITHHELD["n_rungs_withheld"] == 2
    assert "tile-join invariant" in mcb.WITHHELD["why"]


# ── the default path, replayed ────────────────────────────────────────

#: The committed default run's output directory (the CLI's default).
COMMITTED_MCB = mcb.K_LADDER_DIR / "mcb"


def _replay_committed_artefacts(calls: list[tuple[str, str]]) -> Any:
    """A stand-in for :func:`mcb.run_mcb` that reads the committed artefacts.

    The bootstrap is the board tool's, tested with the tool. What the driver
    owns is everything around it, so the replay hands each call the artefact
    the committed run wrote. It refuses the hand-off unless that artefact
    records the call the default makes today, so a registry that drifted from
    its committed inputs fails here rather than replaying the wrong file.

    Args:
        calls: Collects ``(slug, metric)`` for every call made.

    Returns:
        A function with :func:`mcb.run_mcb`'s signature.
    """
    def runner(entry: dict[str, Any], metric: str, out_dir: Path,
               bootstrap: int,
               tile_join: str = mcb.TILE_JOIN_DEFAULT) -> tuple[Path, dict[str, Any]]:
        calls.append((entry["slug"], metric))
        name = mcb.artefact_name(entry["analysis_id"], metric, entry["buffer_m"],
                                 tile_join)
        path = mcb.BASE_DIR / COMMITTED_MCB / entry["slug"] / name
        result = json.loads(path.read_text(encoding="utf-8"))
        assert result["board"] == entry["analysis_id"]
        assert result["metric"] == metric
        assert int(result["buffer_metres"]) == entry["buffer_m"]
        assert int(result["bootstrap"]) == bootstrap
        assert int(result["seed"]) == mcb.SEED
        assert float(result["m_frac"]) == mcb.M_FRAC
        # The committed artefacts record absolute paths on whichever machine
        # (or worktree) ran them, so the repo-relative tail is what must match.
        for key, rel in (("analyses_override", entry["analyses"]),
                         ("conditions_override", entry["conditions"]),
                         ("bounds_override", entry["bounds"])):
            recorded = result.get(key)
            if rel is None:
                assert recorded is None, f"{entry['slug']}: {key} {recorded}"
            else:
                assert Path(recorded).as_posix().endswith(
                    "/" + Path(rel).as_posix()), f"{entry['slug']}: {key}"
        return path, result
    return runner


def test_default_path_reproduces_the_committed_summary(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``main`` on the committed registry reproduces the committed outputs.

    Only ``--output-dir`` is passed (the default would overwrite the committed
    files). Every other setting is the default the 2026-10-15 run used: the
    committed registry, both metrics, 10,000 resamples and the published tile
    join.
    """
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(mcb, "run_mcb", _replay_committed_artefacts(calls))
    monkeypatch.setattr(sys, "argv",
                        ["k_ladder_mcb.py", "--output-dir", str(tmp_path)])
    assert mcb.main() == 0
    assert len(calls) == 44, "22 ladders, two metrics each"

    committed_dir = mcb.BASE_DIR / COMMITTED_MCB
    produced = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    committed = json.loads((committed_dir / "summary.json").read_text(encoding="utf-8"))
    for payload in (produced, committed):
        del payload["generated_at_utc"]
    assert produced == committed
    assert ((tmp_path / "table.md").read_text(encoding="utf-8")
            == (committed_dir / "table.md").read_text(encoding="utf-8"))


def test_default_path_refuses_an_inventory_that_lost_a_ladder(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    """Red sentinel: the S166 defect class is refused at launch.

    The canonical inventory is cut the way ``0fc2d6389`` cut the compat
    export, dropping the six Gemini 3 ladders reported clipped. The default
    run must then exit before any bootstrap, naming all 24 labels, rather
    than fail in ``summarise`` after the first ladder's bootstrap.
    """
    inventory = json.loads(
        (mcb.BASE_DIR / mcb.PHASE2_INVENTORY).read_text(encoding="utf-8"))
    inventory["ladders"] = [
        ladder for ladder in inventory["ladders"]
        if mcb.phase2_slug(ladder["proposer_pool"])
        not in WITHHELD_ON_THE_CLIPPED_BASIS]
    cut = tmp_path / "ladders-cut.json"
    cut.write_text(json.dumps(inventory), encoding="utf-8")
    # An absolute path replaces BASE_DIR when joined, so the driver reads the cut.
    monkeypatch.setattr(mcb, "PHASE2_INVENTORY", cut)

    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(mcb, "run_mcb", _replay_committed_artefacts(calls))
    monkeypatch.setattr(sys, "argv",
                        ["k_ladder_mcb.py", "--output-dir", str(tmp_path / "out")])
    with pytest.raises(SystemExit) as exit_info:
        mcb.main()
    assert exit_info.value.code == 2
    assert calls == [], "no bootstrap may run on an inventory that cannot join"
    stderr = capsys.readouterr().err
    assert "24 committed ranking label(s) have no K" in stderr
    assert "phase2-image-n5-image-t0-3: pv-min-image-t0.3-n1-opmax" in stderr
    assert not (tmp_path / "out" / "summary.json").exists()


def test_as_evaluated_record_has_the_clipped_sets() -> None:
    """The D71 label holds only while the two bases agree on every set.

    PI ruling D71 keeps the default as the as-evaluated record for the seven
    ladders now reported on D51's clipped basis, on the evidence that both
    bases give the same Hsu admissible K set and best K on both metrics. If a
    re-run of either side breaks that, the label "as-evaluated record" no
    longer describes a basis-free result, and the ruling must be revisited.
    This test turns red when that happens.
    """
    record = mcb.AS_EVALUATED_RECORD
    assert set(record["slugs"]) == WITHHELD_ON_THE_CLIPPED_BASIS | {"tier-e"}

    def ladders(path: Path, prefix: str = "") -> dict[str, dict[str, Any]]:
        data = json.loads((mcb.BASE_DIR / path).read_text(encoding="utf-8"))
        return {lad["slug"].removeprefix(prefix): lad for lad in data["ladders"]}

    as_evaluated = ladders(COMMITTED_MCB / "summary.json")
    clipped = ladders(record["clipped_summary"], record["clipped_slug_prefix"])
    assert set(clipped) == set(record["slugs"])
    for slug in record["slugs"]:
        for metric in ("f1", "mcc"):
            a, c = as_evaluated[slug][metric], clipped[slug][metric]
            assert a["hsu_admissible_K"] == c["hsu_admissible_K"], (slug, metric)
            assert a["best_K"] == c["best_K"], (slug, metric)


# ── the § 6.1 table ───────────────────────────────────────────────────


def test_markdown_table_renders_one_row_per_ladder() -> None:
    """The findings table is generated, so its shape is worth pinning."""
    block = mcb.summarise({"slug": "synthetic", "buffer_m": 20},
                          _result(_separated_ladder()), K_OF)
    table = mcb.markdown_table([
        {"family": "A synthetic ladder", "rungs": list(RUNG_KS),
         "f1": block, "mcc": block},
    ])
    lines = table.splitlines()
    assert len(lines) == 3, "header, separator, one ladder"
    assert lines[0].startswith("| ladder |")
    assert "A synthetic ladder" in lines[2]
    assert "1, 3, 5, 10" in lines[2]
    assert f"{block['hsu_w_upper']:.4f}" in lines[2]


def test_output_paths_stay_inside_the_repository() -> None:
    """A relative default keeps the artefacts beside the ladders they describe."""
    assert mcb.K_LADDER_DIR == Path("results/k-ladder-2026-09-12")
    assert mcb.BOOTSTRAP == 10000
    assert mcb.SEED == 42
    assert mcb.M_FRAC == 1.0
    assert mcb.SIMULTANEOUS_CONFIDENCE == 0.95
