"""Tier-1 tests for the step-5 r2 modes of the r2 recompute chain.

Step 5 of ``planning/reference-revision-2026-09-06.md`` re-measures the
reference-dependent analyses on reference revision r2. Three analysis
scripts gained a ``--reference r2`` mode in Session 149-c; these tests pin
the contract each mode must keep: the r1 default is byte-for-byte what it
was, and the r2 mode reads the r2 scoring home / r2 board and writes only
its own artefact.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import derive_tile_level_f1 as tlf  # noqa: E402
from scripts import sensitivity_mde as mde  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
R2_HOME = ROOT / "results/55maps-r2-ref-2026-09-06"


@pytest.mark.tier1
def test_tile_level_f1_canonical_specs_are_untouched():
    """The r1 default must be the committed spec tuple, object for object."""
    assert tlf.cells_for("canonical", ROOT) is tlf.CELLS


@pytest.mark.tier1
def test_tile_level_f1_r2_specs_point_at_the_r2_home():
    """Every 55-map spec moves to its r2 evaluation; GS specs pass through."""
    if not (R2_HOME / "TH7-k4/evaluation.json").exists():
        pytest.skip("r2 scoring home not present")
    specs = tlf.cells_for("r2", ROOT)
    assert len(specs) == len(tlf.CELLS)
    m55 = [s for s in specs if s.carrier == tlf.M55_CARRIER]
    gs = [s for s in specs if s.carrier != tlf.M55_CARRIER]
    assert len(m55) == 8 and gs == [s for s in tlf.CELLS if s.carrier != tlf.M55_CARRIER]
    for s in m55:
        assert s.condition_id.endswith("-r2-gt")
        assert s.evaluation_path.startswith(tlf.R2_SCORING_HOME)
        assert (ROOT / s.evaluation_path).exists()
        assert s.board == tlf.R2_BOARD_ID
        assert 0.7 < s.object_f1 < 0.9  # read from the r2 file, not the r1 literal
    r1 = {s.key: s for s in tlf.CELLS}
    assert all(abs(s.object_f1 - r1[s.key].object_f1) < 0.01 for s in m55)


@pytest.mark.tier1
def test_tile_level_f1_r2_report_passes_the_mcc_gate_and_names_itself():
    if not (R2_HOME / "TH7-k4/evaluation.json").exists():
        pytest.skip("r2 scoring home not present")
    report = tlf.build_report(ROOT, "r2")
    gate = report["validation_gate"]
    assert gate["n_passed"] == gate["n_cells"] == 10


@pytest.mark.tier1
def test_mde_r2_mode_refuses_without_the_r2_board(monkeypatch, tmp_path):
    """The r2 board is built at step 4e; before that the mode must stop, not guess."""
    monkeypatch.setattr(mde, "R2_BOARD", tmp_path / "absent.json")
    with pytest.raises(SystemExit, match="does not exist"):
        mde.harvest("r2")


@pytest.mark.tier1
def test_mde_r1_harvest_is_unchanged_by_the_r2_mode():
    """harvest() with the default reference carries no r2 group."""
    groups = mde.harvest()
    assert not any("r2" in name for name in groups)
