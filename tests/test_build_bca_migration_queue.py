"""Recipe recovery in ``scripts/build_bca_migration_queue.py``.

Phase 7 of the Session 137 audit remediation (defect D33, audit finding
F9). The queue builder read two argparse DEFAULTS as if they were
measurements, so all 22 rows it emitted were unexecutable:

* ``cli_args.buffers`` is ``[20]`` for every batch-scored cell (the
  buffer grain came from the batch YAML, which argparse never saw), so
  the queue asked for a one-buffer re-score of 14-buffer cells;
* ``cli_args.detections`` / ``detections_dir`` are both null for those
  cells, so the detection-source columns were empty; and
* ``cli_args.glob`` is likewise a default — four cells recorded
  ``*/detections_*.geojson`` while their YAML supplied
  ``*/detections-*.geojson``, which resolves zero files.

The queue had never been executed when the audit found this, so no
committed artefact depends on the old rows.

Tests cover:

1. ``buffers_that_ran`` — the measured ``summary.buffers`` wins over the
   declared ``cli_args.buffers``.
2. ``recover_recipe`` — the D22 fallback chain mirrored from
   ``era1_leaderboard_tiering.load_cells``.
3. ``make_row`` — a recovered batch cell is rewritten as a per-cell
   invocation; a genuine per-cell row is left alone.
4. ``needs_migration`` — the skip labels say what is actually true.
5. A committed batch cell still round-trips into an executable row.

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

from scripts.build_bca_migration_queue import (  # noqa: E402
    REPO_ROOT,
    buffers_that_ran,
    make_row,
    needs_migration,
    recover_recipe,
)

pytestmark = pytest.mark.tier1

#: A committed batch-scored cell whose recorded ``cli_args`` carries the
#: defaults this fix works around. Relative to the repo root.
REAL_BATCH_CELL = Path(
    "results/paper-eval/n1/384px-14buf-mcc/flash-image-high-t-0-7/"
    "evaluation.json"
)

STANDARD_14 = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]


def _batch_document(**overrides: Any) -> dict[str, Any]:
    """A minimal batch-scored ``evaluation.json``, defaults and all."""
    document = {
        "summary": {
            "label": "Flash Image HIGH T=0.7",
            "n_runs": 10,
            "buffers": [{"buffer_metres": b, "f1": 0.5} for b in STANDARD_14],
        },
        "_metadata": {
            "script_path": "scripts/evaluate_detections.py",
            "bootstrap": {"n_iterations": 10000, "seed": 42},
            "cli_args": {
                "detections": None,
                "detections_dir": None,
                "batch": "configs/n1-eval-384px-14buf-mcc.yaml",
                "glob": "*/detections_*.geojson",
                "buffers": [20],
                "ground_truth": "inputs/vectors/references/gt.geojson",
                "bounds": "inputs/vectors/bounds/384/bounds.geojson",
                "bootstrap": 1000,
                "seed": 42,
                "output_dir": "results/paper-eval/n1/384px-14buf-mcc",
                "label": None,
                "mcc": True,
            },
            "input_files": {
                "detections": "outputs/h11/pool/image-t0.7",
                "ground_truth": "inputs/vectors/references/gt.geojson",
                "bounds": "inputs/vectors/bounds/384/bounds.geojson",
            },
        },
    }
    document.update(overrides)
    return document


# =============================================================================
# 1. buffers_that_ran — measured beats declared
# =============================================================================


def test_summary_buffers_beat_the_argparse_default() -> None:
    """The regression: [20] declared, 14 buffers actually scored."""
    document = _batch_document()
    cli = recover_recipe(document)
    assert cli["buffers"] == [20]           # what argparse saw
    assert buffers_that_ran(document, cli) == STANDARD_14  # what ran


def test_buffers_fall_back_to_cli_args_when_no_summary_rows() -> None:
    """A cell with no scored buffers still yields its declared list."""
    document = _batch_document(summary={"buffers": []})
    assert buffers_that_ran(document, {"buffers": [20, 30]}) == [20, 30]


def test_buffers_deduplicate_and_keep_recorded_order() -> None:
    document = {"summary": {"buffers": [
        {"buffer_metres": 50}, {"buffer_metres": 20}, {"buffer_metres": 50},
    ]}}
    assert buffers_that_ran(document, {}) == [50, 20]


def test_buffers_ignore_unusable_rows() -> None:
    """Booleans and non-numeric entries are metadata corruption."""
    document = {"summary": {"buffers": [
        {"buffer_metres": 20}, {"buffer_metres": True},
        {"buffer_metres": "20"}, "not-a-row", {},
    ]}}
    assert buffers_that_ran(document, {}) == [20]


def test_buffers_empty_when_nothing_is_recorded() -> None:
    assert buffers_that_ran({}, {}) == []


# =============================================================================
# 2. recover_recipe — the D22 fallback chain
# =============================================================================


def test_detections_dir_recovered_from_input_files_string() -> None:
    """The batch case: a directory string becomes ``detections_dir``."""
    cli = recover_recipe(_batch_document())
    assert cli["detections_dir"] == "outputs/h11/pool/image-t0.7"
    assert not cli["detections"]


def test_detections_list_recovered_from_input_files_list() -> None:
    """The adapter case: a list becomes ``detections``."""
    document = {"_metadata": {"input_files": {
        "detections": ["outputs/a.geojson", "outputs/b.geojson"],
    }}}
    cli = recover_recipe(document)
    assert cli["detections"] == ["outputs/a.geojson", "outputs/b.geojson"]
    assert not cli.get("detections_dir")


def test_recorded_detections_are_never_overwritten() -> None:
    """A cell that declares its own input keeps it."""
    document = {"_metadata": {
        "cli_args": {"detections_dir": "outputs/declared"},
        "input_files": {"detections": "outputs/fallback"},
    }}
    assert recover_recipe(document)["detections_dir"] == "outputs/declared"


def test_null_bounds_and_ground_truth_are_filled_from_input_files() -> None:
    """Hardened over the mirrored original: falsy, not merely absent."""
    document = {"_metadata": {
        "cli_args": {"bounds": None, "ground_truth": ""},
        "input_files": {"bounds": "b.geojson", "ground_truth": "gt.geojson"},
    }}
    cli = recover_recipe(document)
    assert cli["bounds"] == "b.geojson"
    assert cli["ground_truth"] == "gt.geojson"


def test_recover_recipe_does_not_mutate_the_document() -> None:
    document = _batch_document()
    before = json.dumps(document, sort_keys=True)
    recover_recipe(document)
    assert json.dumps(document, sort_keys=True) == before


def test_recover_recipe_is_empty_when_there_is_no_recipe() -> None:
    """The genuinely unqueueable cells (24 of them) return nothing."""
    assert recover_recipe({"_metadata": {"script_path": "x"}}) == {}


# =============================================================================
# 3. make_row — a recovered batch cell becomes a per-cell invocation
# =============================================================================


def _row_for(document: dict[str, Any], rel: str) -> dict[str, str]:
    return make_row(REPO_ROOT / rel, document)


def test_batch_cell_is_rewritten_as_a_per_cell_invocation() -> None:
    """The headline fix, all four columns at once."""
    rel = "results/paper-eval/n1/384px-14buf-mcc/flash-image-high-t-0-7"
    row = _row_for(_batch_document(), f"{rel}/evaluation.json")

    # Buffers: what ran, not the default.
    assert row["buffers"] == " ".join(str(b) for b in STANDARD_14)
    # Detection input: recovered, so the row has something to score.
    assert row["detections_dir"] == "outputs/h11/pool/image-t0.7"
    # ``batch`` dropped — a row carrying both inputs is ambiguous.
    assert row["batch"] == ""
    # Output dir is the CELL, not the batch parent (which appends the
    # label slug in batch mode and would write one level too high).
    assert row["output_dir"] == rel
    # Label recovered from the summary; its slug is the cell dir name.
    assert row["label"] == "Flash Image HIGH T=0.7"
    # Glob blanked so the canonical two-convention resolver applies (D6).
    assert row["glob"] == ""


def test_per_cell_row_is_left_alone() -> None:
    """A cell that recorded a real invocation is passed through."""
    document = {
        "summary": {"buffers": [{"buffer_metres": 20}, {"buffer_metres": 50}]},
        "_metadata": {
            "script_path": "scripts/evaluate_detections.py",
            "cli_args": {
                "detections_dir": "outputs/pool",
                "glob": "accepted_run*.geojson",
                "buffers": [20, 50],
                "bounds": "b.geojson",
                "ground_truth": "gt.geojson",
                "seed": 7,
                "label": "declared",
                "mcc": False,
                "output_dir": "results/cell",
            },
        },
    }
    row = _row_for(document, "results/cell/evaluation.json")
    assert row["glob"] == "accepted_run*.geojson"  # explicit, so preserved
    assert row["output_dir"] == "results/cell"
    assert row["label"] == "declared"
    assert row["buffers"] == "20 50"
    assert row["seed"] == "7"
    assert row["mcc"] == "0"
    assert row["batch"] == ""


def test_unrecovered_batch_row_keeps_its_batch_column() -> None:
    """No per-cell input recovered means the batch row is all there is.

    The rewrite is conditional on recovery succeeding — it must not
    strip the only detection source a row has.
    """
    document = {
        "summary": {"buffers": [{"buffer_metres": 20}]},
        "_metadata": {
            "script_path": "scripts/evaluate_detections.py",
            "cli_args": {
                "batch": "configs/batch.yaml",
                "glob": "*/detections_*.geojson",
                "buffers": [20],
                "bounds": "b.geojson",
                "ground_truth": "gt.geojson",
                "output_dir": "results/batch-parent",
            },
        },
    }
    row = _row_for(document, "results/batch-parent/cell/evaluation.json")
    assert row["batch"] == "configs/batch.yaml"
    assert row["glob"] == "*/detections_*.geojson"
    assert row["output_dir"] == "results/batch-parent"


def test_single_string_detections_is_normalised_to_the_pipe_field() -> None:
    """Older records store ``detections`` as a bare string."""
    document = {
        "summary": {"buffers": [{"buffer_metres": 20}]},
        "_metadata": {"cli_args": {
            "detections": "outputs/one.geojson",
            "bounds": "b.geojson", "ground_truth": "gt.geojson",
        }},
    }
    row = _row_for(document, "results/cell/evaluation.json")
    assert row["detections"] == "outputs/one.geojson"


# =============================================================================
# 4. needs_migration — truthful skip labels
# =============================================================================


def _write(tmp_path: Path, document: Any) -> Path:
    path = tmp_path / "evaluation.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_unrecorded_script_is_not_reported_as_another_script(
    tmp_path: Path,
) -> None:
    """40 committed cells record no script at all.

    Labelling them ``not_evaluate_detections`` asserted knowledge the
    artefact does not carry, and hid that they are also not known to be
    BCa. Both facts now appear in the label.
    """
    path = _write(tmp_path, {"_metadata": {
        "bootstrap": {"method": "percentile"},
        "input_files": {"detections": "outputs/pool"},
    }})
    in_scope, reason = needs_migration(path)
    assert in_scope is False
    assert reason.startswith("script_not_recorded")
    assert "bootstrap_method=percentile" in reason
    assert "recipe=yes" in reason


def test_unrecorded_script_without_a_recipe_says_so(tmp_path: Path) -> None:
    path = _write(tmp_path, {"_metadata": {"bootstrap": {}}})
    _, reason = needs_migration(path)
    assert "bootstrap_method=unrecorded" in reason
    assert "recipe=none" in reason


def test_a_different_recorded_script_keeps_the_old_label(
    tmp_path: Path,
) -> None:
    path = _write(tmp_path, {"_metadata": {
        "script_path": "scripts/score_55maps_standardised_reference.py",
    }})
    assert needs_migration(path) == (False, "not_evaluate_detections")


def test_already_bca_and_needs_migration(tmp_path: Path) -> None:
    bca = _write(tmp_path, {"_metadata": {
        "script_path": "scripts/evaluate_detections.py",
        "bootstrap": {"method": "BCa"},
    }})
    assert needs_migration(bca) == (False, "already_bca")
    (tmp_path / "sub").mkdir()
    pct = _write(tmp_path / "sub", {"_metadata": {
        "script_path": "scripts/evaluate_detections.py",
        "bootstrap": {"method": "percentile"},
    }})
    assert needs_migration(pct) == (True, "needs_migration")


def test_no_metadata_is_reported_as_such(tmp_path: Path) -> None:
    assert needs_migration(_write(tmp_path, {"summary": {}})) == (
        False, "no_metadata",
    )


# =============================================================================
# 5. A committed batch cell round-trips into an executable row
# =============================================================================


def test_committed_batch_cell_yields_an_executable_row() -> None:
    """End-to-end against the tracked corpus, no filesystem writes.

    Pins the three properties the audit found missing: a real buffer
    list, a real detection input, and a resolvable one.
    """
    eval_path = PROJECT_ROOT / REAL_BATCH_CELL
    if not eval_path.is_file():  # pragma: no cover - artefact absent
        pytest.skip(f"{REAL_BATCH_CELL} not present in this checkout")
    document = json.loads(eval_path.read_text(encoding="utf-8"))
    row = make_row(eval_path, document)

    scored = [b["buffer_metres"] for b in document["summary"]["buffers"]]
    assert row["buffers"] == " ".join(str(b) for b in scored)
    assert len(scored) > 1, "expected a multi-buffer cell to guard against"
    assert row["detections_dir"], "no detection input recovered"
    assert (PROJECT_ROOT / row["detections_dir"]).is_dir()
    assert row["output_dir"] == str(eval_path.parent.relative_to(REPO_ROOT))
    assert row["batch"] == ""
