"""
Tests for empty_tile_audit_sample.py — nested-sample invariants.

The audit design depends on: determinism at a seed, per-sheet
proportional allocation, the inner (10 %) tier being a subset of the
outer (20 %) draw, and inner-tier tiles preceding every escalation
tile in the manifest order.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.empty_tile_audit_sample import map_of, nested_sample


def _empty_set() -> set[str]:
    """Synthetic empty tiles: three sheets of different sizes."""
    tiles = set()
    for sheet, n in (("K-35-001-1", 100), ("K-35-002-2", 40),
                     ("K-35-003-3", 10)):
        tiles |= {f"{sheet}_x{i * 384}_y0.png" for i in range(n)}
    return tiles


@pytest.mark.tier1
class TestNestedSample:
    def test_deterministic(self):
        a = nested_sample(_empty_set(), 0.20, 0.10, seed=42)
        b = nested_sample(_empty_set(), 0.20, 0.10, seed=42)
        assert a == b

    def test_proportional_per_sheet(self):
        rows = nested_sample(_empty_set(), 0.20, 0.10, seed=42)
        by_sheet = {}
        for r in rows:
            by_sheet.setdefault(r["map_name"], []).append(r)
        assert len(by_sheet["K-35-001-1"]) == 20  # 20% of 100
        assert len(by_sheet["K-35-002-2"]) == 8   # 20% of 40
        assert len(by_sheet["K-35-003-3"]) == 2   # 20% of 10
        inner = {s: sum(1 for r in rs if r["tier"] == "10pct")
                 for s, rs in by_sheet.items()}
        assert inner == {"K-35-001-1": 10, "K-35-002-2": 4,
                         "K-35-003-3": 1}

    def test_inner_tier_first_and_contiguous(self):
        rows = nested_sample(_empty_set(), 0.20, 0.10, seed=42)
        assert [r["order_index"] for r in rows] == list(range(len(rows)))
        tiers = [r["tier"] for r in rows]
        boundary = tiers.index("20pct")
        assert all(t == "10pct" for t in tiers[:boundary])
        assert all(t == "20pct" for t in tiers[boundary:])

    def test_no_duplicates_and_sheet_parse(self):
        rows = nested_sample(_empty_set(), 0.20, 0.10, seed=42)
        names = [r["tile_name"] for r in rows]
        assert len(names) == len(set(names))
        for r in rows:
            assert map_of(r["tile_name"]) == r["map_name"]
