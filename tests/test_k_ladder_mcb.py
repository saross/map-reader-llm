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
"""

from __future__ import annotations

import json
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

    Its committed tiering is on the board frame (K = 1 tile-MCC 0.7834) while
    `ladders.json` records the grid-common frame (0.7894). Gating against the
    inventory would refuse a correct run, so this pins the source.
    """
    ranking = mcb.committed_ranking(
        mcb.K_LADDER_DIR / "mcc-test/tiering/gs-stride-a/tiering_20m.json")
    k1 = ranking["g384-ov128-ladder-n1-verified-p0.15-k1"]
    assert k1["mcc"] == pytest.approx(0.7834, abs=1e-4)
    assert k1["f1"] == pytest.approx(0.8605, abs=1e-4)


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


def test_label_to_k_covers_every_committed_ranking_label() -> None:
    """An admissible set is only useful as a statement about K."""
    k_of = mcb.label_to_k()
    for entry in mcb.ladder_registry():
        for label in mcb.committed_ranking(entry["tiering"]):
            assert label in k_of, f"{entry['slug']}: no K for {label}"


def test_withheld_family_is_recorded_with_its_three_cells() -> None:
    """The withholding is reported, never silently dropped."""
    assert len(mcb.WITHHELD["cells_withheld"]) == 3
    assert mcb.WITHHELD["n_rungs_withheld"] == 2
    assert "tile-join invariant" in mcb.WITHHELD["why"]


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
