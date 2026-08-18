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
        _row("board", ["H1", "H13"], "post-hoc", ["E25"]),
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
    assert records["H13"]["disposition"] == "not executed"  # synthetic fixture


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
    """A hypothesis with only post-hoc coverage aborts the projection.

    The fixture's post-hoc board row references H13, so removing the
    disposition row leaves H13 with post-hoc-only coverage — the named
    failure mode, not the zero-rows path (S134 audit finding M-5).
    """
    rows = _synthetic_manifest()
    rows = [r for r in rows if r["analysis_id"] != "h13-dispo"]
    with pytest.raises(ValueError, match="H13.*only post-hoc"):
        ghot.project(rows)


@pytest.mark.tier1
def test_unadjudicated_null_row_fails_loudly():
    """A preregistered-null row referencing a hypothesis aborts loudly.

    Null stubs are schema-legal mid-authoring, but the table must never
    silently render an incomplete register (S134 audit finding M-2).
    """
    rows = _synthetic_manifest()
    rows.append(_row("stub", ["H11"], None, ["E99"]))
    with pytest.raises(ValueError, match="H11.*unadjudicated.*stub"):
        ghot.project(rows)


@pytest.mark.tier1
def test_deviations_extracted_from_prose_entries():
    """E-numbers embedded in prose deviations entries are not dropped.

    diversity-dividend-384's real array carries "E49/E51 (…)" as one
    prose string; the union must surface both (S134 audit finding H-2).
    """
    rows = _synthetic_manifest()
    rows.append(_row("dd", ["H9"], "confirmatory-with-deviation",
                     ["E49/E51 (carry-forward context)",
                      "None for the operating-point selection."]))
    records = {r["hypothesis"]: r for r in ghot.project(rows)}
    assert "E49" in records["H9"]["deviations"]
    assert "E51" in records["H9"]["deviations"]


@pytest.mark.tier1
def test_exclusion_is_structural_not_prose():
    """Exclusion derives from the family row's hypothesis_refs.

    Rewording the outcome's exclusion prose must not flip H6 to
    'not rejected' (S134 audit finding H-1); an outright prose/refs
    contradiction must abort.
    """
    rows = _synthetic_manifest()
    family = next(r for r in rows
                  if r["analysis_id"] == "family-bh-fdr-confirmatory")
    # Reworded prose with no "H6 excluded" phrase at all: still excluded.
    family["outcome"] = "Rejection set {H2, H3, H7} at q=0.05 over m=7."
    records = {r["hypothesis"]: r for r in ghot.project(rows)}
    assert records["H6"]["family_fdr"] == "— (excluded: never run)"
    # A prose claim contradicting the refs aborts.
    family["outcome"] = ("Rejection set {H2, H3, H7} at q=0.05. "
                         "H5 excluded (never run).")
    with pytest.raises(ValueError, match="prose declares"):
        ghot.project(rows)


@pytest.mark.tier1
def test_family_parse_guards():
    """Multiple rejection clauses and non-confirmatory members abort."""
    rows = _synthetic_manifest()
    family = next(r for r in rows
                  if r["analysis_id"] == "family-bh-fdr-confirmatory")
    family["outcome"] = ("Rejection set {H2} primary; corrected "
                         "Rejection set {H2, H3} alongside.")
    with pytest.raises(ValueError, match="exactly one"):
        ghot.parse_rejection_set(rows)
    family["outcome"] = "Rejection set {H2, H10} at q=0.05."
    with pytest.raises(ValueError, match="non-confirmatory"):
        ghot.parse_rejection_set(rows)


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
    for h in ("H14", "H15"):
        assert records[h]["disposition"] == "not executed"
    # H13 became "executed" in Session 136: arms B and C were run and all three
    # registered analyses reported (row h13-overlap-2026-08-18). The former
    # not-executed disposition row was archived with PI approval to
    # archive/superseded-register-rows/ — while it remained, the projection
    # rendered H13 "partially executed", because that verdict fires whenever a
    # not-executed row coexists with an executed one.
    assert records["H13"]["disposition"] == "executed"
    # The committed outputs equal a regeneration (the --check contract,
    # asserted for real — S134 audit finding M-4): MD compared with the
    # commit-hash stamp neutralised on both sides, JSON compared exactly.
    def _neutralise(text: str) -> str:
        import re
        return re.sub(r"commit `[^`]+`", "commit `X`", text)

    analyses = ghot.load_analyses()
    ordered = ghot.project(analyses)
    assert _neutralise(ghot.OUT_MD.read_text()) == _neutralise(
        ghot.render_md(ordered, ghot.no_hypothesis_rows(analyses)))
    committed = ghot.OUT_JSON.read_text()
    import json
    assert json.loads(committed) == {"hypotheses": ordered}
