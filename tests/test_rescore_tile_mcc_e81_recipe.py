"""Recipe recovery in ``scripts/rescore_tile_mcc_e81.py``.

Phase 7 of the Session 137 audit remediation (defect D33, audit finding
F9): the re-scorer subscripted ``_metadata.cli_args["ground_truth"]`` and
``["bounds"]`` directly, so it raised a bare ``KeyError`` on the 40
committed evaluations that carry no ``cli_args`` at all, and a
``ValueError`` naming only ``cli_args`` on the 22 batch-scored cells
whose per-cell detection input lives in ``_metadata.input_files``.
Neither message told an operator what to do.

Both are now read through the D22 fallback chain that
``scripts/era1_leaderboard_tiering.py`` ``load_cells`` established, and a
cell that genuinely records neither fails with an actionable message.

Measured against the committed corpus at the time of the fix: 16 adapter
cells and 22 batch cells become recoverable; 24 ``verifier-t-pilot``
cells record no recipe in either place and still fail — loudly, and by
design.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.rescore_tile_mcc_e81 import (  # noqa: E402
    _require_input,
    recover_recipe,
)

pytestmark = pytest.mark.tier1


# =============================================================================
# recover_recipe — the D22 fallback chain
# =============================================================================


def test_adapter_cell_with_no_cli_args_is_recovered() -> None:
    """The 40-cell family: ``input_files`` is the only recipe they have."""
    metadata = {"input_files": {
        "detections": "outputs/55maps/IM-k3",
        "ground_truth": "inputs/vectors/references/gt.geojson",
        "bounds": "inputs/vectors/bounds/bounds.geojson",
    }}
    cli = recover_recipe(metadata)
    assert cli["ground_truth"] == "inputs/vectors/references/gt.geojson"
    assert cli["bounds"] == "inputs/vectors/bounds/bounds.geojson"
    assert cli["detections_dir"] == "outputs/55maps/IM-k3"


def test_batch_cell_recovers_only_its_detection_input() -> None:
    """The 22-cell family: GT and bounds were recorded, detections not."""
    metadata = {
        "cli_args": {
            "detections": None, "detections_dir": None,
            "batch": "configs/batch.yaml",
            "ground_truth": "gt.geojson", "bounds": "b.geojson",
        },
        "input_files": {
            "detections": "outputs/h11/pool/image-t0.7",
            "ground_truth": "gt.geojson", "bounds": "b.geojson",
        },
    }
    cli = recover_recipe(metadata)
    assert cli["detections_dir"] == "outputs/h11/pool/image-t0.7"
    assert cli["batch"] == "configs/batch.yaml"  # untouched


def test_a_detections_list_is_recovered_as_a_list() -> None:
    metadata = {"input_files": {
        "detections": ["outputs/a.geojson", "outputs/b.geojson"],
    }}
    cli = recover_recipe(metadata)
    assert cli["detections"] == ["outputs/a.geojson", "outputs/b.geojson"]
    assert not cli.get("detections_dir")


def test_recorded_values_win_over_the_fallback() -> None:
    """A cell that recorded its own invocation is left alone."""
    metadata = {
        "cli_args": {
            "detections_dir": "outputs/declared",
            "ground_truth": "declared-gt.geojson",
            "bounds": "declared-bounds.geojson",
        },
        "input_files": {
            "detections": "outputs/fallback",
            "ground_truth": "fallback-gt.geojson",
            "bounds": "fallback-bounds.geojson",
        },
    }
    cli = recover_recipe(metadata)
    assert cli["detections_dir"] == "outputs/declared"
    assert cli["ground_truth"] == "declared-gt.geojson"
    assert cli["bounds"] == "declared-bounds.geojson"


def test_null_recorded_values_are_filled_from_input_files() -> None:
    """A recorded ``null`` is an absence, not a declaration."""
    metadata = {
        "cli_args": {"ground_truth": None, "bounds": ""},
        "input_files": {"ground_truth": "gt.geojson", "bounds": "b.geojson"},
    }
    cli = recover_recipe(metadata)
    assert cli["ground_truth"] == "gt.geojson"
    assert cli["bounds"] == "b.geojson"


def test_recover_recipe_does_not_mutate_its_input() -> None:
    metadata: dict[str, Any] = {
        "cli_args": {"ground_truth": None},
        "input_files": {"ground_truth": "gt.geojson"},
    }
    before = json.dumps(metadata, sort_keys=True)
    recover_recipe(metadata)
    assert json.dumps(metadata, sort_keys=True) == before


def test_empty_metadata_yields_an_empty_recipe() -> None:
    assert recover_recipe({}) == {}


# =============================================================================
# _require_input — a loud, actionable failure
# =============================================================================


def test_required_input_is_returned_when_present() -> None:
    assert _require_input(
        Path("results/cell/evaluation.json"),
        {"ground_truth": "gt.geojson"},
        "ground_truth",
    ) == "gt.geojson"


@pytest.mark.parametrize("recipe", [{}, {"bounds": None}, {"bounds": ""}])
def test_missing_input_raises_value_error_not_key_error(recipe: dict) -> None:
    """A ``KeyError`` told the operator nothing; this must not regress."""
    with pytest.raises(ValueError):
        _require_input(Path("results/cell/evaluation.json"), recipe, "bounds")


def test_the_failure_message_is_actionable() -> None:
    """It names the file, the field, both search sites, and the options."""
    eval_path = Path("results/verifier-t-pilot/T0.0/x/evaluation.json")
    with pytest.raises(ValueError) as excinfo:
        _require_input(eval_path, {}, "ground_truth")
    message = str(excinfo.value)
    assert str(eval_path) in message
    assert "_metadata.cli_args.ground_truth" in message
    assert "_metadata.input_files.ground_truth" in message
    assert "--ground-truth" in message  # the flag, hyphenated as typed
    assert "D33" in message
    assert "exclude this cell from the worklist" in message


# =============================================================================
# The committed corpus: which cells the fallback actually rescues
# =============================================================================


def test_committed_corpus_recipe_census() -> None:
    """Sweep every committed evaluation and pin the three outcomes.

    Recorded when the fix landed: 1,603 cells recorded a full recipe, 22
    needed the detections fallback, 16 needed the whole recipe from
    ``input_files``, and 24 have no recipe anywhere. The assertions are
    directional (``> 0``) rather than exact so ordinary corpus growth
    does not break the suite, but the three populations must all remain
    non-empty — each is a branch of the fallback.
    """
    results_dir = PROJECT_ROOT / "results"
    if not results_dir.is_dir():  # pragma: no cover - artefacts absent
        pytest.skip("results/ not present in this checkout")

    fully_recorded = rescued = unusable = 0
    for path in sorted(results_dir.rglob("evaluation.json")):
        try:
            metadata = json.loads(path.read_text(encoding="utf-8"))[
                "_metadata"
            ]
        except (json.JSONDecodeError, KeyError):  # pragma: no cover
            continue
        declared = metadata.get("cli_args") or {}
        declared_ok = bool(
            declared.get("ground_truth") and declared.get("bounds")
            and (declared.get("detections") or declared.get("detections_dir"))
        )
        cli = recover_recipe(metadata)
        recovered_ok = bool(
            cli.get("ground_truth") and cli.get("bounds")
            and (cli.get("detections") or cli.get("detections_dir"))
        )
        if declared_ok:
            fully_recorded += 1
        elif recovered_ok:
            rescued += 1
        else:
            unusable += 1
            # The unusable cells must fail loudly, never with a KeyError.
            with pytest.raises(ValueError):
                _require_input(path, cli, "ground_truth")

    assert fully_recorded > 0
    assert rescued > 0, "the D22 fallback rescues no committed cell"
    assert unusable > 0, "expected the known recipe-less cells to persist"
