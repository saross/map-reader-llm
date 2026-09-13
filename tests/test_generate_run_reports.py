"""Tier-1 tests for ``scripts/generate_run_reports.py`` (the per-run report projector).

The reports are GENERATED PROJECTIONS, which under the PI ruling of 2026-09-11
(``docs/methodology/output-directory-standard.md`` § "Documents in Revision Policy
Scope") carry provenance and a tested drift guard instead of a hand changelog.
``test_no_drift_in_committed_reports`` IS that required guard: it is the thing that
answers "is this report current?", so it is the test the ruling asks for and the one
to keep green.

The remaining tests pin the properties that make the projection trustworthy rather
than merely present: every registered run is covered, the hand-authored reports are
never overwritten, the banner names the generator and a source commit, and a missing
figure is written as "not supplied" rather than guessed or zeroed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import generate_run_reports as grr

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def corpus() -> grr.Corpus:
    """Load the committed inputs once for the module."""
    return grr.Corpus()


@pytest.mark.tier1
def test_no_drift_in_committed_reports():
    """THE drift guard the generated-projection ruling requires.

    A committed report that no longer matches a fresh projection is stale, and a
    registered run with no report is missing one. Both fail here rather than
    surviving as a document that quietly disagrees with the manifests.
    """
    assert grr.main(["--check"]) == 0


@pytest.mark.tier1
def test_every_registered_run_has_a_report(corpus):
    """41 registered runs, 41 reports: 39 projected plus 2 hand-authored."""
    registry = json.loads(
        (REPO_ROOT / "results/run-registry.json").read_text(encoding="utf-8"))
    run_ids = [e["run_id"] for e in registry["registry"]]
    missing = [rid for rid in run_ids
               if not grr.target_path(rid, corpus).is_file()]
    assert not missing, missing
    assert len(grr.runs_to_project(corpus)) == len(run_ids) - len(grr.HAND_AUTHORED)


@pytest.mark.tier1
def test_hand_authored_reports_are_not_projections(corpus):
    """The two narrative reports must keep their own content and their changelog.

    They carry Dawid-Skene corrections, paired comparisons and per-map extrema that
    no projection of the manifests can re-derive. If a future change drops them from
    HAND_AUTHORED, the projector would overwrite irreplaceable analysis — so assert
    both that they are excluded and that what is on disk is still the hand-authored
    document.
    """
    for run_id in grr.HAND_AUTHORED:
        assert run_id not in grr.runs_to_project(corpus)
        text = grr.target_path(run_id, corpus).read_text(encoding="utf-8")
        assert "GENERATED FILE" not in text
        assert "Changelog" in text or "Last revised" in text


@pytest.mark.tier1
def test_projection_carries_banner_generator_and_source_commit(corpus):
    """Each of the three things the ruling asks a generated projection to carry."""
    text = grr.render_report("h13", corpus, "abc1234")
    assert text.startswith("<!-- GENERATED FILE")
    assert "**GENERATED FILE — do not hand-edit.**" in text
    assert "scripts/generate_run_reports.py" in text
    assert f"v{grr.GENERATOR_VERSION}" in text
    assert "source commit `abc1234`" in text
    assert "## 10. Provenance of this report" in text
    for rel in grr.INPUT_FILES:
        assert rel in text, rel


@pytest.mark.tier1
def test_absent_metric_is_not_supplied_not_zero(corpus):
    """h13's conditions were scored at the 20 m buffer ALONE.

    The 50 m column must therefore read "not supplied", never 0.0000 — a zero would
    assert a measured F1 of nothing at 50 m, which is the opposite of the truth. The
    report also has to say which buffers exist so a reader can tell the two apart.
    """
    text = grr.render_report("h13", corpus, "abc1234")
    assert "Buffers on file (metres)" in text
    assert "6 condition(s): 20" in text
    row = next(ln for ln in text.splitlines() if ln.startswith("| `arm-a-overlap-12-5`"))
    cells = [c.strip() for c in row.split("|")]
    assert cells[7].startswith("0.5580"), cells        # F1@20 m, measured
    assert cells[8] == grr.NOT_SUPPLIED, cells         # F1@50 m, never scored


@pytest.mark.tier1
def test_cost_is_labelled_recorded_not_audited(corpus):
    """The recorded cost must never be presented as the run's cost.

    ``cost_usd`` is each pass meta's own estimate, and the token-load audit showed
    those estimates price at standard rates on flex-tier runs and omit thinking
    tokens. A report that summed them without that caveat would publish a figure
    wrong in a known direction.
    """
    text = grr.render_report("h13", corpus, "abc1234")
    assert "The recorded cost is NOT this run's cost." in text
    assert "reports/token-load-audit-2026-06-12.md" in text
    assert "Sum of recorded `cost_usd`" in text


@pytest.mark.tier1
def test_double_counted_token_totals_are_disclosed(corpus):
    """The manifest's token totals are 2×/3× inflated on three of the 55-map runs.

    A pass's ``tokens`` come from the meta's ``usage_stats``
    (``generate_post_run_report.py`` → ``_tokens_from_usage``), and the token-load
    audit recomputed from ``per_item_metadata`` that the 2026-05 recovery merge
    doubled that block on the text-high and image runs. Printing those totals as
    plain fact would publish figures wrong by a known factor, so every run in
    TOKEN_AUDIT must carry its verdict, the trustworthy source and the audited
    clean per-pass figures.
    """
    text = grr.render_report("55maps-text-high-generalisation", corpus, "abc1234")
    assert "Audited: the token figures above are inflated by a measured factor." in text
    assert "2.0× inflated (factors 2.003–2.016 across axes)" in text
    assert "US$40.19/pass" in text
    assert "The trustworthy source is `per_item_metadata`" in text
    # and no derived run total is manufactured from a per-pass figure
    assert "No run total is derived here" in text
    # a clean run states that it is clean rather than staying silent
    clean = grr.render_report("55maps-text-high-t0-3-generalisation", corpus, "abc1234")
    assert "clean (factors 1.0001–1.0012; no recovery merge)" in clean
    # a run with no audit entry gets no audit block at all
    assert "Audited: the token figures" not in grr.render_report("h13", corpus, "abc")


@pytest.mark.tier1
def test_audit_citation_only_where_the_report_names_the_run(corpus):
    """A run with no audit mention says so; a run with one lists it.

    pv-diag-384 is named in three of the four audits; h13 in none. The negative case
    is the one that matters: it must state that an audited cost is not supplied
    rather than leave the section silent.
    """
    named = grr.render_report("pv-diag-384", corpus, "abc1234")
    assert "reports/token-load-audit-2026-06-12.md" in named
    assert "a mention is a pointer" in named
    unnamed = grr.render_report("h13", corpus, "abc1234")
    assert "No cost audit on file names this run" in unnamed


@pytest.mark.tier1
def test_errata_sources_are_kept_apart(corpus):
    """Registered deviations and textual mentions must not borrow each other's
    authority: h13 has three registered (E54/E66/E75) and two mention-only."""
    text = grr.render_report("h13", corpus, "abc1234")
    assert "### 8.1 Registered as deviations (3)" in text
    assert "### 8.2 Mentioning this run (2)" in text
    assert "not a claim that the erratum is about this run" in text
    reg = text.split("### 8.1")[1].split("### 8.2")[0]
    assert "**E75**" in reg and "**E54**" in reg and "**E66**" in reg


@pytest.mark.tier1
def test_prose_escaping_preserves_identifiers():
    """Literal underscores, asterisks and angle brackets in reproduced prose survive
    as characters rather than becoming markup (or vanishing as unknown tags)."""
    assert grr._prose("_ignored_evals") == "\\_ignored\\_evals"
    assert grr._prose("'-recovery-<date>'") == "'-recovery-&lt;date&gt;'"
    assert grr._prose(None) == grr.NOT_SUPPLIED
    assert grr._prose("") == grr.NOT_SUPPLIED


@pytest.mark.tier1
def test_grouping_is_deterministic_and_loses_nothing(corpus):
    """Caveats are grouped by identical text, so a family's shared qualification is
    printed once with every cell named. Every condition that has a caveat must appear
    in exactly one group, and the order must be stable for the drift guard."""
    conds = corpus.conditions["h13"]
    groups = grr._group_by_text(conds, lambda c: c.get("caveat"))
    assert groups == grr._group_by_text(conds, lambda c: c.get("caveat"))
    grouped = [lab for _text, labels in groups for lab in labels]
    expected = sorted(c["label"] for c in conds if c.get("caveat"))
    assert sorted(grouped) == expected
    assert len(grouped) == len(set(grouped))


@pytest.mark.tier1
def test_verifier_passes_separated_from_proposer_passes(corpus):
    """A verifier pass is identified by the manifest's own null-reason marker, never
    by a directory name — the E72/GAP-8 distinction that made verifier and proposer
    rows comparable in the first place."""
    text = grr.render_report("pv-diag-384", corpus, "abc1234")
    assert "### 3.1 Proposer passes" in text
    assert "### 3.2 Verifier passes" in text
    assert "Verifier rows report no tile count by design" in text
    assert "Candidates verified" in text
