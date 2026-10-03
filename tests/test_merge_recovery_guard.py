"""Tier-1: merge_recovery_meta refuses a cumulative "recovery" meta.

The 2026-05-02 merge summed an already-cumulative meta into its backup and
doubled the TH7 and IM metas (token-load audit §§ 3.2, 3.4)."""

from __future__ import annotations

import pytest

from scripts.merge_recovery_meta import refuse_cumulative


def _meta(items):
    return {"execution_stats": {"completed_items": list(items)}}


@pytest.mark.tier1
def test_a_cumulative_meta_is_refused():
    original = _meta(f"t{i}" for i in range(100))
    cumulative = _meta(f"t{i}" for i in range(103))
    with pytest.raises(SystemExit, match="cumulative"):
        refuse_cumulative(original, cumulative)


@pytest.mark.tier1
def test_a_recovery_only_meta_passes():
    original = _meta(f"t{i}" for i in range(100))
    refuse_cumulative(original, _meta(["t100", "t101", "t102"]))
    refuse_cumulative(_meta([]), _meta(["t1"]))  # nothing to compare: allowed
