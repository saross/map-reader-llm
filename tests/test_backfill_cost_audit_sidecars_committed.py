"""Tier-2 drift test: the committed ``cost_audit.json`` sidecars match their generator.

``scripts/backfill_cost_audit_sidecars.py --check`` is the drift guard for the
WP4 § A sidecars (PI rulings D14, D28). This test runs the same comparison
against the committed artefacts, so a regenerated passes register, a changed
rate card or tier evidence file, or a changed meta that leaves its sidecar
behind fails the suite, not only an operator who remembers to run ``--check``.

Tier 2, not tier 1: it reads every meta under ``outputs/`` and ``results/``
(about 1,545 files) and the 3 MB register, and measured 23.1 s on amd-tower
on 2026-10-04, against the tier-1 rule in ``tests/README.md`` (fast, no bulk
committed data). Synthetic-fixture coverage of the same logic is tier 1, in
``tests/test_backfill_cost_audit_sidecars.py``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.backfill_cost_audit_sidecars import build_plan, drift, rel_path

pytestmark = pytest.mark.tier2

REPO = Path(__file__).resolve().parents[1]


def test_committed_sidecars_are_current() -> None:
    """No sidecar is missing, differs from its regeneration, or is stale."""
    if not (REPO / "results" / "passes-manifest.json").is_file():
        pytest.skip("no passes register in this checkout")
    plan = build_plan(REPO)
    missing, differing = drift(plan)
    found = {label: [rel_path(p, REPO) for p in paths[:10]]
             for label, paths in (("missing", missing), ("differing", differing),
                                  ("stale", plan.stale)) if paths}
    assert not found, (f"sidecar drift ({len(missing)} missing, {len(differing)} differing, "
                       f"{len(plan.stale)} stale; first ten each): {found}; refresh with "
                       "python scripts/backfill_cost_audit_sidecars.py --write")
