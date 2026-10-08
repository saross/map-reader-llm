"""
Tier-2 test: pv-diag-256's committed unions reproduce from their registered pool.

The PI's ruling of 2026-10-08 ("register pv-diag-256 in place") registered the
run's five N = 5, T = 0.7 proposer passes where 276e4ca80 archived them, at
``archive/outputs-non-production-tile-sizes/text-n5/text-t0.7/run_1..5``
(``results/run-conditions.json``, ``decomposition.pv-diag-256.proposer_pools``
``["text-n5-text-t0.7"]``), and moved the union directory from
``UNRESOLVABLE`` to ``POOL_OVERRIDES`` in ``scripts/check_union_provenance.py``.
Record: ``reports/stale-register-notes-2026-10-07.md`` section 10.

This test runs the checker itself on the committed unions
``outputs/h11/pv-diag-256/consensus/text-{1..5}of5.geojson``. Each must
classify REPRODUCES from all five passes, at the feature counts binding
``pv-diag-256-text-5of5-union`` (``results/manipulation-gate-bindings.json``)
records: 2,558 / 1,909 / 1,645 / 1,423 / 1,165.

Tier 2, not tier 1: each case clusters the five committed pass files (about
1,840 detections each) and took about 5 s on amd-tower on 2026-10-08, against
the tier-1 rule in ``tests/README.md`` (fast, no bulk committed data). The
resolution of the union to its registered pool, and the EPSG:32635 comparison
these unions need, are covered at tier 1 in
``tests/test_check_union_provenance.py``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_union_provenance import check_union

pytestmark = pytest.mark.tier2

REPO = Path(__file__).resolve().parents[1]

#: The registered pool, as ``repo_path``/``path`` in the register.
POOL = "archive/outputs-non-production-tile-sizes/text-n5/text-t0.7"

#: Committed feature count of ``text-{t}of5.geojson``, by vote threshold.
EXPECTED_FEATURES = {1: 2558, 2: 1909, 3: 1645, 4: 1423, 5: 1165}


@pytest.mark.parametrize("threshold", sorted(EXPECTED_FEATURES))
def test_pv_diag_256_union_reproduces_from_the_registered_pool(
    threshold: int, tmp_path: Path,
) -> None:
    """Each committed vote-threshold union reproduces exactly from the pool."""
    union = REPO / f"outputs/h11/pv-diag-256/consensus/text-{threshold}of5.geojson"
    if not union.is_file():
        pytest.skip("pv-diag-256's unions are not in this checkout")

    result = check_union(union, tmp_path / "scratch", repo_root=REPO)

    assert result.classification == "REPRODUCES", result.detail
    assert result.pool_dir == POOL
    assert result.threshold == threshold
    assert result.committed_features == result.rederived_features
    assert result.committed_features == EXPECTED_FEATURES[threshold]
    assert result.union_passes_used == [f"run_{n}" for n in range(1, 6)]
    assert result.passes_not_reflected == []
    assert result.unmatched_committed == result.unmatched_rederived == 0
