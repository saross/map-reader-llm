"""Tier-1 tests for scripts/annotate_retest_pairwise_permutation.py (D42).

The March retest pairwise file has no producer, so its permutation
annotation is the only way its contrasts reach the D42 test. These tests
pin the annotation against the committed W2 re-test: the three raw-alpha
flips, A[45]'s within-phase BH value, and that the H-family inputs read
from it are the re-test's.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from annotate_retest_pairwise_permutation import (  # noqa: E402
    RETEST,
    TARGET,
    build_annotations,
)

pytestmark = pytest.mark.tier1


def _committed() -> tuple[list[dict], list[dict]]:
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    return data["comparisons"], json.loads(RETEST.read_text(encoding="utf-8"))


def test_the_committed_file_carries_the_annotation():
    """Every comparison has its block, equal to a fresh build."""
    comparisons, retest = _committed()
    fresh = build_annotations(comparisons, retest)
    assert [c["permutation_retest"] for c in comparisons] == fresh


def test_the_w2_findings_are_reproduced():
    """Raw-alpha flips are rows 18, 45 and 60; A[45] BH is 0.588."""
    comparisons, retest = _committed()
    blocks = build_annotations(comparisons, retest)
    flips = [i for i, (c, b) in enumerate(zip(comparisons, blocks))
             if c["significant_raw"] != b["significant_raw"]]
    assert flips == [18, 45, 60]
    assert blocks[45]["f1_bh_within_phase"] == pytest.approx(0.588)
    assert blocks[45]["significant_bh_within_phase"] is False


def test_a_misaligned_retest_is_refused():
    """A re-test row that does not match its comparison stops the build."""
    comparisons, retest = _committed()
    bad = [dict(r) for r in retest]
    bad[3]["a"] = "not-the-arm"
    with pytest.raises(SystemExit, match="row 3"):
        build_annotations(comparisons, bad)
