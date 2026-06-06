"""
Tier 1 tests for ``scripts.consensus_vs_baseline_tiering`` — the new pieces
added on top of the (already-tested) n1 leaderboard machinery for the
diversity-dividend test.

The permutation, BH-FDR and greedy-clique tiering are imported verbatim from
``n1_baseline_leaderboard_tiering`` and covered by its own tier-1 suite. What
is new here, and pinned below, is:

1. ``read_tile_mcc`` — must read ``summary.tile_classification.mcc.point``
   (the buffer-agnostic field), returning ``None`` when absent, NOT the
   always-null per-buffer ``mcc``.
2. ``_uniform_cell`` — must compute ``observed_micro_f1`` from the per-tile
   arrays consistently with the cells' eval-reported F1, and carry MCC.
3. ``extract_named_contrasts`` — must pull exactly the headline pairs that
   answer the two named claims (diversity dividend; consensus vs matched
   single-pass; consensus vs the Pro single-pass leader) and attach each
   pair's p-value and BH-significance.

All tests use synthetic in-memory data — no network, and only a tmp_path
JSON for the MCC reader. The geopandas-I/O paths (``consensus_per_tile``, the
board/consensus cell loaders, ``run_round_robin``, and ``main()``'s bounds /
ground-truth resolution) need real GeoJSON fixtures and are deferred to a
tier-2 suite.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.consensus_vs_baseline_tiering import (  # noqa: E402
    PRO_LEADER_REF,
    _uniform_cell,
    extract_named_contrasts,
    read_tile_mcc,
)


# --------------------------------------------------------------------------- #
# 1. read_tile_mcc — the buffer-agnostic tile_classification field
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_read_tile_mcc_reads_tile_classification_point(tmp_path: Path) -> None:
    """MCC is read from summary.tile_classification.mcc.point."""
    eval_doc = {
        "summary": {
            "buffers": [{"buffer_metres": 20, "f1": 0.8, "mcc": None}],
            "tile_classification": {"mcc": {"point": 0.6204, "mean": 0.6204}},
        }
    }
    p = tmp_path / "evaluation.json"
    p.write_text(json.dumps(eval_doc))
    assert read_tile_mcc(p) == pytest.approx(0.6204)


@pytest.mark.tier1
def test_read_tile_mcc_absent_returns_none(tmp_path: Path) -> None:
    """A cell with no tile_classification block yields None, not a crash."""
    p = tmp_path / "evaluation.json"
    p.write_text(json.dumps({"summary": {"buffers": []}}))
    assert read_tile_mcc(p) is None


@pytest.mark.tier1
def test_read_tile_mcc_intermediate_missing_returns_none(tmp_path: Path) -> None:
    """tile_classification present but without an mcc.point still yields None."""
    p = tmp_path / "evaluation.json"
    p.write_text(json.dumps({"summary": {"tile_classification": {"confusion": {}}}}))
    assert read_tile_mcc(p) is None


# --------------------------------------------------------------------------- #
# 2. _uniform_cell — observed micro-F1 from arrays + MCC carried
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_uniform_cell_computes_observed_micro_f1() -> None:
    """observed_micro_f1 is the micro-F1 of the summed per-tile arrays."""
    tp = np.array([2.0, 3.0, 0.0])
    fp = np.array([0.0, 1.0, 0.0])
    fn = np.array([1.0, 0.0, 2.0])
    # totals: tp=5, fp=1, fn=3 -> P=5/6, R=5/8, F1 = 2PR/(P+R).
    p, r = 5 / 6, 5 / 8
    expected = 2 * p * r / (p + r)
    cell = _uniform_cell(
        ref="x", label="x", kind="champion", tp=tp, fp=fp, fn=fn,
        eval_f1=0.7, mcc=0.62, meta={"modality": "text", "thinking": "high"},
    )
    assert cell["observed_micro_f1"] == pytest.approx(round(expected, 6))
    assert cell["mcc"] == 0.62
    assert cell["modality"] == "text"


@pytest.mark.tier1
def test_uniform_cell_handles_none_mcc() -> None:
    """A None MCC is preserved as None (not coerced to 0.0)."""
    z = np.zeros(3)
    cell = _uniform_cell(
        ref="x", label="x", kind="single-pass", tp=z, fp=z, fn=z,
        eval_f1=0.0, mcc=None, meta={},
    )
    assert cell["mcc"] is None


# --------------------------------------------------------------------------- #
# 3. extract_named_contrasts — the headline pairs
# --------------------------------------------------------------------------- #


def _cell(ref: str, kind: str, f1: float, mcc: float, *,
          modality: str | None = None, thinking: str | None = None,
          matched: str | None = None) -> dict:
    """Build a tiered-cell dict mirroring _uniform_cell's real key set.

    Champion cells carry modality/thinking/matched_single_pass_ref in their
    meta; single-pass (board) cells do NOT (their meta is n_passes +
    operating_point_provenance only). Only attach the champion-only keys when
    provided, so a test single-pass cell realistically lacks them — that way
    the kind-guarded access in extract_named_contrasts is genuinely exercised
    (a regression that dropped the ``kind == "champion"`` guard would then
    KeyError here instead of passing silently).
    """
    cell = {"ref": ref, "label": ref, "kind": kind, "eval_f1": f1, "mcc": mcc}
    if modality is not None:
        cell["modality"] = modality
    if thinking is not None:
        cell["thinking"] = thinking
    if matched is not None:
        cell["matched_single_pass_ref"] = matched
    return cell


def _pair(ref_a: str, ref_b: str, p: float, bh: float, sig: bool) -> dict:
    """Build a pairwise-result entry."""
    return {"ref_a": ref_a, "ref_b": ref_b, "p_value": p,
            "bh_adjusted_p": bh, "significant": sig}


@pytest.mark.tier1
def test_extract_contrasts_pulls_diversity_dividend_and_matched() -> None:
    """The diversity-dividend, matched-baseline and Pro-leader pairs appear."""
    cells = [
        _cell("c-th", "champion", 0.814, 0.620,
              modality="text", thinking="high", matched="sp-th"),
        _cell("c-tm", "champion", 0.661, 0.381,
              modality="text", thinking="minimal", matched="sp-tm"),
        _cell("sp-th", "single-pass", 0.387, 0.10),
        _cell("sp-tm", "single-pass", 0.488, 0.20),
        _cell(PRO_LEADER_REF, "single-pass", 0.804, 0.381),
    ]
    pairs = [
        _pair("c-th", "c-tm", 0.0001, 0.0004, True),     # diversity dividend
        _pair("c-th", "sp-th", 0.0001, 0.0004, True),    # consensus vs matched
        _pair("c-tm", "sp-tm", 0.02, 0.04, True),        # consensus vs matched
        _pair("c-th", PRO_LEADER_REF, 0.61, 0.61, False),  # vs Pro leader: tie
    ]
    significant = {frozenset({p["ref_a"], p["ref_b"]}): p["significant"] for p in pairs}
    lookup = {frozenset({p["ref_a"], p["ref_b"]}): p for p in pairs}

    contrasts = extract_named_contrasts(cells, significant, lookup)
    claims = {c["claim"]: c for c in contrasts}

    # Diversity dividend (text): HIGH 0.814 vs minimal 0.661, significant.
    dd = next(c for k, c in claims.items() if k.startswith("diversity-dividend (text)"))
    assert dd["f1_a"] == 0.814 and dd["f1_b"] == 0.661
    assert dd["f1_diff"] == pytest.approx(0.153)
    assert dd["significant"] is True
    # Full contrast contract: the pair's p/BH-p and both cells' MCC are wired in.
    assert dd["p_value"] == 0.0001
    assert dd["bh_adjusted_p"] == 0.0004
    assert dd["mcc_a"] == 0.620 and dd["mcc_b"] == 0.381

    # Pro-leader contrast: the 0.814 vs 0.804 tie is carried as non-significant.
    pro = next(c for k, c in claims.items() if "Pro single-pass leader" in k)
    assert pro["significant"] is False
    assert pro["f1_a"] == 0.814 and pro["f1_b"] == 0.804
    assert pro["p_value"] == 0.61 and pro["bh_adjusted_p"] == 0.61

    # Each champion's matched single-pass contrast is present.
    matched = [c for k, c in claims.items() if k.startswith("consensus vs matched")]
    assert len(matched) == 2


@pytest.mark.tier1
def test_extract_contrasts_skips_missing_pairs() -> None:
    """A named contrast whose pair is absent from the lookup is dropped, not faked."""
    cells = [
        _cell("c-th", "champion", 0.8, 0.6,
              modality="text", thinking="high", matched="sp-missing"),
    ]
    # No pairs at all -> nothing extractable.
    contrasts = extract_named_contrasts(cells, {}, {})
    assert contrasts == []
