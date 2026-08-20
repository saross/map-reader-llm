"""Schema guards for the merged 55-map ground-truth references (D29).

Phase 3 of the Session 137 audit remediation: the `symbol_code` column was
renamed `source_id_lossy` after the audit falsified the symbol-code diagnosis
(finding F5) — the values are upstream record identifiers after float64
precision loss. These tests pin the committed artefacts' schema so the false
semantic cannot silently return, and the key invariants of both references.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

pytestmark = pytest.mark.tier1

REPO = Path(__file__).parent.parent
REFS = REPO / "inputs/vectors/references"


@pytest.mark.parametrize("stem,expected_records", [
    ("best-available-gt-55maps", 5010),
    ("canonical-gt-55maps-r50", 5161),
])
def test_reference_csv_schema_and_key(stem: str, expected_records: int):
    """The committed CSVs carry the honest column name and a unique key."""
    path = REFS / f"{stem}.csv"
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        assert "source_id_lossy" in header
        assert "symbol_code" not in header  # the falsified semantic (D29)
        assert "gt_id" in header
        gt_ids = [row["gt_id"] for row in reader]
    assert len(gt_ids) == expected_records
    assert len(set(gt_ids)) == expected_records  # gt_id IS the key (D21)
