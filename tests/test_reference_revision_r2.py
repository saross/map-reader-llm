"""Tier-1 tests for the r2 reference revision (planning/reference-revision-2026-09-06.md).

The instruction set must reconcile with the adjudication files it is derived
from, and the materialised r2 reference must equal r1 minus the removals plus
the additions, with every removed record gone and every added record present.
"""

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.materialise_best_available_gt import R2_SYMBOL_MAP  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INSTR = ROOT / "results/reference-revision-r2/audit-revision-instructions.csv"
R1 = ROOT / "inputs/vectors/references/best-available-gt-55maps.csv"
R2 = ROOT / "inputs/vectors/references/best-available-gt-55maps-r2.csv"
REMOVED = ROOT / "inputs/vectors/references/best-available-gt-55maps-r2-removed.csv"


@pytest.mark.tier1
def test_instruction_set_reconciles_with_the_adjudications():
    """Removals = distinct flagged reference points; additions = the add classes."""
    instr = pd.read_csv(INSTR, dtype=str).fillna("")
    census = json.loads((ROOT / "results/cluster-audit/adjudication.json").read_text())
    empty = json.loads((ROOT / "results/empty-tile-audit/adjudication.json").read_text())
    flagged = {r["flagged_gt_id"] for r in census["per_mark"] if r["class"] == "gt-error-flag"
               and not str(r["flagged_gt_id"]).startswith("not-in-reference")}
    assert set(instr.loc[instr.action == "remove", "gt_id"]) == flagged
    n_add_census = sum(1 for r in census["per_mark"]
                       if r["class"] in ("detected", "true-double-miss", "proposed-but-filtered"))
    n_add_empty = sum(1 for r in empty["per_mark"] if r["class"] == "true-double-miss")
    assert (instr.action == "add").sum() == n_add_census + n_add_empty
    assert set(instr.loc[instr.action == "add", "symbol"]) <= set(R2_SYMBOL_MAP)


@pytest.mark.tier1
def test_r2_equals_r1_minus_removals_plus_additions():
    """Record arithmetic, identity of removals, and presence of additions."""
    instr = pd.read_csv(INSTR, dtype=str).fillna("")
    r1, r2, removed = (pd.read_csv(p, dtype=str) for p in (R1, R2, REMOVED))
    n_rem, n_add = (instr.action == "remove").sum(), (instr.action == "add").sum()
    assert len(r2) == len(r1) - n_rem + n_add
    assert set(removed.gt_id) == set(instr.loc[instr.action == "remove", "gt_id"])
    assert not set(removed.gt_id) & set(r2.gt_id)
    assert (r2.layer == "audit_reviewed").sum() == n_add
    assert r2.gt_id.is_unique
    kept = set(r1.gt_id) - set(removed.gt_id)
    assert kept <= set(r2.gt_id)
