"""
Tier 1 tests for ``scripts.rescore_conditions`` input-selector logic.

The 3b standardisation harness re-scores a worklist of conditions through
``evaluate_detections.py`` at the 14 uniform buffers + MCC. Each worklist entry
selects its detections with **exactly one** of two grains:

* ``detections`` — a single geojson path, or a list of replicate paths;
* ``detections_dir`` (+ optional ``glob``) — a condition directory whose
  ``run_*`` subdirs are replicates (the grain the Era-1 phase2 retests need).

These tests pin that selector contract (``_input_args``), its inclusion in the
assembled ``evaluate_detections.py`` command (``_eval_command``), and the
replicate-aware cost estimate (``_replicate_count`` / ``estimate``). They
exercise the helpers in isolation — they do NOT run any scoring subprocess,
load GeoJSON, or write output files.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.rescore_conditions import (  # noqa: E402
    BUFFERS_STANDARD,
    _eval_command,
    _input_args,
    _replicate_count,
    estimate,
)

# A minimal Era-1-340 (4-map regime) entry skeleton; tests add an input key.
_BASE_ENTRY = {
    "label": "phase2a-brief-text",
    "bounds": "inputs/vectors/bounds/full_evaluation_bounds.geojson",
    "ground_truth": "inputs/vectors/references/mounds-reference.geojson",
    "output_dir": "results/paper-eval/phase2/512px-14buf-mcc/phase2a-brief-text",
}


# =========================================================================
# _input_args — the mutually-exclusive selector
# =========================================================================

@pytest.mark.tier1
def test_input_args_single_file() -> None:
    """A scalar ``detections`` forwards a single ``--detections`` path."""
    assert _input_args({"detections": "a.geojson"}) == ["--detections", "a.geojson"]


@pytest.mark.tier1
def test_input_args_replicate_file_list() -> None:
    """A list ``detections`` forwards every path after one ``--detections``.

    ``evaluate_detections.py`` treats multiple ``--detections`` files as
    independent replicate runs of one condition (a replicate-mean summary).
    """
    out = _input_args({"detections": ["r1.geojson", "r2.geojson", "r3.geojson"]})
    assert out == ["--detections", "r1.geojson", "r2.geojson", "r3.geojson"]


@pytest.mark.tier1
def test_input_args_directory_default_glob() -> None:
    """``detections_dir`` without ``glob`` emits no ``--glob`` (scorer default)."""
    out = _input_args({"detections_dir": "outputs/retest/phase2a/brief-text"})
    assert out == ["--detections-dir", "outputs/retest/phase2a/brief-text"]
    assert "--glob" not in out


@pytest.mark.tier1
def test_input_args_directory_with_glob() -> None:
    """An explicit ``glob`` is forwarded as ``--glob``."""
    out = _input_args(
        {"detections_dir": "d", "glob": "*/detections_*.geojson"}
    )
    assert out == ["--detections-dir", "d", "--glob", "*/detections_*.geojson"]


@pytest.mark.tier1
def test_input_args_rejects_both_keys() -> None:
    """Setting both input keys is a worklist error, not a silent precedence."""
    with pytest.raises(ValueError, match="exactly one"):
        _input_args({"detections": "a", "detections_dir": "d"})


@pytest.mark.tier1
def test_input_args_rejects_neither_key() -> None:
    """An entry with no input selector is a worklist error."""
    with pytest.raises(ValueError, match="exactly one"):
        _input_args({"label": "orphan"})


# =========================================================================
# _eval_command — the assembled evaluate_detections.py invocation
# =========================================================================

@pytest.mark.tier1
def test_eval_command_dir_mode_is_well_formed() -> None:
    """Dir-mode command carries the dir selector, MCC, and all 14 buffers."""
    entry = {**_BASE_ENTRY, "detections_dir": "outputs/retest/phase2a/brief-text"}
    cmd = _eval_command(entry)

    assert "--detections-dir" in cmd
    assert "--detections" not in cmd  # the two selectors are exclusive
    assert "--mcc" in cmd
    assert cmd[cmd.index("--bounds") + 1] == _BASE_ENTRY["bounds"]
    assert cmd[cmd.index("--ground-truth") + 1] == _BASE_ENTRY["ground_truth"]
    assert cmd[cmd.index("--output-dir") + 1] == _BASE_ENTRY["output_dir"]

    # Every standard buffer appears, in order, after --buffers.
    start = cmd.index("--buffers") + 1
    passed = cmd[start:start + len(BUFFERS_STANDARD)]
    assert passed == [str(b) for b in BUFFERS_STANDARD]


@pytest.mark.tier1
def test_eval_command_single_file_mode_uses_detections() -> None:
    """Single-file mode keeps the legacy ``--detections`` selector."""
    entry = {**_BASE_ENTRY, "detections": "outputs/x/detections.geojson"}
    cmd = _eval_command(entry)
    assert "--detections" in cmd
    assert "--detections-dir" not in cmd
    assert cmd[cmd.index("--detections") + 1] == "outputs/x/detections.geojson"


# =========================================================================
# _replicate_count / estimate — replicate-aware cost
# =========================================================================

@pytest.mark.tier1
def test_replicate_count_grains() -> None:
    """Replicate count reflects each input grain."""
    assert _replicate_count({"detections": "a"}) == 1
    assert _replicate_count({"detections": ["a", "b", "c"]}) == 3
    assert _replicate_count({"detections_dir": "d", "replicates": 3}) == 3
    # Unknown directory replicate count defaults to 1 (no filesystem walk).
    assert _replicate_count({"detections_dir": "d"}) == 1


@pytest.mark.tier1
def test_estimate_scales_with_replicates() -> None:
    """A 3-replicate condition is estimated at ~3× its single-replicate cost."""
    one = estimate(
        [{**_BASE_ENTRY, "detections_dir": "d", "replicates": 1}], workers=12
    )
    three = estimate(
        [{**_BASE_ENTRY, "detections_dir": "d", "replicates": 3}], workers=12
    )
    assert three["serial_minutes"] > 2 * one["serial_minutes"]
    assert three["n_4map"] == 1 and three["n_55map"] == 0
