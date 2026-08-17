"""Tier 1 tests for scripts/generate_hypothesis_outcome_table.py.

The table is a pure projection of the analyses manifest (D17 ruling,
S134 reconciliation block). Synthetic fixtures exercise the projection
rules; one live-data test pins the committed register's key dispositions.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location(
    "generate_hypothesis_outcome_table",
    REPO_ROOT / "scripts" / "generate_hypothesis_outcome_table.py")
ghot = importlib.util.module_from_spec(_SPEC)
sys.modules["generate_hypothesis_outcome_table"] = ghot
_SPEC.loader.exec_module(ghot)


def _row(analysis_id: str, hyps: list[str], label: str,
         deviations: list[str] | None = None, outcome: str = "") -> dict:
    """Build a minimal analysis row for projection tests."""
    return {
        "analysis_id": analysis_id,
        "hypothesis_refs": hyps,
        "preregistered": label,
        "deviations": deviations or [],
        "outcome": outcome,
    }


def _synthetic_manifest() -> list[dict]:
    """A minimal register covering all 15 hypotheses.

    H1–H8 hang off one family row (rejection set {H2, H3, H7}, H6
    excluded); H2 also carries a not-executed condition row (the partial
    case); H9–H12 have registered-exploratory rows; H13–H15 disposition
    rows; one post-hoc row references H1 (must not count as execution).
    """
    rows = [
        _row("family-bh-fdr-confirmatory",
             [f"H{i}" for i in range(1, 9) if i != 6],
             "confirmatory-with-deviation", ["E36"],
             "Rejection set {H2, H3, H7} at q=0.05 over m=7. H6 excluded "
             "(never run)."),
        _row("h6-dispo", ["H6"], "not-executed", ["E74"]),
        _row("h2-c-dispo", ["H2"], "not-executed", ["E59"]),
        _row("board", ["H1"], "post-hoc", ["E25"]),
    ]
    for i in (9, 10, 11, 12):
        rows.append(_row(f"h{i}-analysis", [f"H{i}"], "registered-exploratory"))
    for i in (13, 14, 15):
        rows.append(_row(f"h{i}-dispo", [f"H{i}"], "not-executed"))
    return rows


@pytest.mark.tier1
def test_projection_dispositions_and_family_verdicts():
    """The four disposition classes and family verdicts project correctly."""
    records = {r["hypothesis"]: r for r in ghot.project(_synthetic_manifest())}
    assert len(records) == 15
    # Partial: H2 has both the family (executed) row and a disposition row.
    assert records["H2"]["disposition"] == "partially executed"
    assert records["H2"]["family_fdr"] == "rejected (q=0.05)"
    # Excluded-never-run beats the rejection lookup for H6.
    assert records["H6"]["disposition"] == "not executed"
    assert records["H6"]["family_fdr"] == "— (excluded: never run)"
    # Plain executed + not rejected.
    assert records["H1"]["disposition"] == "executed"
    assert records["H1"]["family_fdr"] == "not rejected"
    # Exploratory hypotheses never enter the family.
    assert records["H9"]["family_fdr"] == "— (exploratory: not in family)"
    assert records["H13"]["disposition"] == "not executed"


@pytest.mark.tier1
def test_post_hoc_rows_never_count_as_execution():
    """A post-hoc row is listed as related, not as a registered analysis."""
    records = {r["hypothesis"]: r for r in ghot.project(_synthetic_manifest())}
    assert records["H1"]["related_post_hoc"] == ["board [post-hoc]"]
    assert all("board" not in a for a in records["H1"]["analyses"])
    # H1's deviations union excludes the post-hoc row's E25.
    assert "E25" not in records["H1"]["deviations"]


@pytest.mark.tier1
def test_uncovered_hypothesis_fails_loudly():
    """A hypothesis with only post-hoc coverage aborts the projection."""
    rows = _synthetic_manifest()
    rows = [r for r in rows if r["analysis_id"] != "h13-dispo"]
    with pytest.raises(ValueError, match="H13"):
        ghot.project(rows)


@pytest.mark.tier1
def test_missing_family_row_fails_loudly():
    """The confirmatory verdict must never be silently omitted."""
    rows = [r for r in _synthetic_manifest()
            if r["analysis_id"] != "family-bh-fdr-confirmatory"]
    with pytest.raises(ValueError, match="family"):
        ghot.parse_rejection_set(rows)


@pytest.mark.tier1
def test_live_register_projects_and_matches_committed_output():
    """The committed register covers 15/15 hypotheses with the known shape."""
    records = {r["hypothesis"]: r for r in ghot.project(ghot.load_analyses())}
    assert len(records) == 15
    assert records["H2"]["disposition"] == "partially executed"
    assert records["H6"]["disposition"] == "not executed"
    assert records["H6"]["family_fdr"] == "— (excluded: never run)"
    assert records["H3"]["disposition"] == "executed"
    assert records["H3"]["family_fdr"] == "rejected (q=0.05)"
    assert records["H10"]["analyses"] == ["h10-pool-size [registered-exploratory]"]
    assert records["H12"]["analyses"] == ["h12-v2-hp-hn-ratio [registered-exploratory]"]
    for h in ("H13", "H14", "H15"):
        assert records[h]["disposition"] == "not executed"
    # The committed outputs are current (same check the CLI --check runs).
    md = ghot.OUT_MD.read_text()
    for h in records:
        assert f"| {h} |" in md
