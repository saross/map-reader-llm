"""Tier-1 guards: analysis scripts must not overwrite hand-authored reports.

Session-75 guardrail 6, extended by the Phase 3 PI ruling (2026-07-31,
`reports/verification/phase3-rulings-2026-07-31.md` § 2): the two
scripts that historically wrote paths now holding hand-authored content
must target the ``_autogen`` sibling instead. Source-scan tests pin the
write targets so a refactor cannot silently reintroduce the clobber.
"""

from __future__ import annotations

from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent / "scripts"


@pytest.mark.tier1
def test_dawid_skene_v2_writes_autogen_not_report():
    src = (SCRIPTS / "analyse_dawid_skene_v2.py").read_text(encoding="utf-8")
    assert '"report_autogen.md"' in src
    assert '/ "report.md"' not in src, (
        "analyse_dawid_skene_v2.py must not write report.md — the "
        "hand-levelled report is the paper-citation source (G6)"
    )


@pytest.mark.tier1
def test_experiment_e_writes_autogen_not_results_doc():
    src = (SCRIPTS / "run_experiment_e.py").read_text(encoding="utf-8")
    assert "phase3d-experiment-e-results_autogen.md" in src
    assert '"phase3d-experiment-e-results.md"' not in src, (
        "run_experiment_e.py must not write the hand-authored "
        "phase3d-experiment-e-results.md (G6)"
    )
