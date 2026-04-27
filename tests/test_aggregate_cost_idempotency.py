"""
Idempotency tests for ``cmd_aggregate_cost`` in ``scripts/run_generalisation.py``.

Regression guard for the bug where re-running the ``aggregate-cost``
subcommand clobbered ``launch_manifest.json`` (resetting ``started_at``,
dropping ``completed_at``, and toggling ``status`` back to
``"in_progress"``) and overwrote any human-edited content in
``experiment_intent.md`` / ``resolved_config.yaml``. The fix gates those
writes behind a ``write_manifests`` keyword flag on ``_prepare_run``;
``cmd_aggregate_cost`` passes ``write_manifests=False`` so the
read-only re-aggregation never mutates run-launch state.

These tests exercise the public CLI surface (``build_arg_parser`` →
``cmd_aggregate_cost``) and assert that:

1. An existing ``launch_manifest.json`` is preserved byte-for-byte.
2. An existing ``experiment_intent.md`` retains its human edits.
3. Re-invoking ``aggregate-cost`` is idempotent (sha256 unchanged).
4. ``cost_manifest.json`` is still produced (regression guard for
   the actual purpose of the subcommand).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
import yaml

# Make ``scripts.run_generalisation`` importable.
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_generalisation import (  # noqa: E402
    build_arg_parser,
    cmd_aggregate_cost,
)


# =============================================================================
# Helpers
# =============================================================================


def _sha256_path(path: Path) -> str:
    """Return the hex SHA256 digest of a file on disk."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_minimal_run_config(
    run_dir: Path,
    *,
    run_name: str,
    output_root: Path,
) -> Path:
    """Write a minimal YAML run-config to disk and return its path.

    Carries every field that ``resolve_run_config`` validates; the
    referenced auxiliary files (manifest, ground truth, …) only need to
    exist for ``aggregate_cost_manifest`` to read them — they may be
    empty / minimal JSON.
    """
    proposer_config = run_dir / "proposer_config.json"
    proposer_config.write_text(
        json.dumps({
            "include_example_images": False,
            "instruction_file": "detect_brief-text.md",
        }),
        encoding="utf-8",
    )
    verifier_config = run_dir / "verifier_config.json"
    verifier_config.write_text(json.dumps({}), encoding="utf-8")

    manifest = run_dir / "manifest.json"
    manifest.write_text(json.dumps([]), encoding="utf-8")

    tiles_dir = run_dir / "tiles"
    tiles_dir.mkdir(exist_ok=True)
    rasters_dir = run_dir / "rasters"
    rasters_dir.mkdir(exist_ok=True)

    ground_truth = run_dir / "gt.geojson"
    ground_truth.write_text(
        json.dumps({"type": "FeatureCollection", "features": []}),
        encoding="utf-8",
    )
    bounds = run_dir / "bounds.geojson"
    bounds.write_text(
        json.dumps({"type": "FeatureCollection", "features": []}),
        encoding="utf-8",
    )

    config = {
        "run_name": run_name,
        "output_root": str(output_root),
        "proposer": {
            "config": str(proposer_config),
            "manifest": str(manifest),
            "tiles_dir": str(tiles_dir),
            "temperature": 0.3,
            "thinking_level": "high",
            "passes": 5,
        },
        "consensus": {"vote_threshold": 3},
        "extract": {"padding": 50, "rasters_dir": str(rasters_dir)},
        "verify": {"config": str(verifier_config)},
        "evaluate": {
            "prob_threshold": 0.5,
            "buffers": [20, 30, 40, 50],
            "ground_truth": str(ground_truth),
            "bounds": str(bounds),
        },
    }
    config_path = run_dir / "run_config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def _seed_existing_run_outputs(
    output_dir: Path,
    *,
    intent_sentinel: str,
) -> tuple[Path, Path, Path]:
    """Pre-populate ``output_dir`` with the artefacts a successful run
    would have written.

    Returns ``(launch_manifest_path, intent_path, resolved_config_path)``.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    launch_manifest = output_dir / "launch_manifest.json"
    launch_manifest.write_text(
        json.dumps({
            "run_name": "test-run",
            "started_at": "2026-03-31T00:00:00Z",
            "completed_at": "2026-04-01T00:00:00Z",
            "status": "completed",
            "git": {
                "commit_sha": "deadbeef",
                "branch": "main",
                "dirty": False,
                "untracked_file_count": 0,
            },
            "expected_cost_usd": 68.52,
        }, indent=2),
        encoding="utf-8",
    )

    intent_path = output_dir / "experiment_intent.md"
    intent_path.write_text(
        "# Experiment intent: test-run\n\n"
        f"{intent_sentinel}\n\n"
        "Generated: 2026-03-31T00:00:00Z\n",
        encoding="utf-8",
    )

    resolved_config = output_dir / "resolved_config.yaml"
    resolved_config.write_text(
        yaml.safe_dump({
            "run_name": "test-run",
            "_human_note": "DO NOT OVERWRITE — tweaked by hand.",
        }),
        encoding="utf-8",
    )
    return launch_manifest, intent_path, resolved_config


@pytest.fixture
def aggregate_cost_args(tmp_path: Path, monkeypatch):
    """Build args for ``cmd_aggregate_cost`` against an isolated tmp run.

    Returns a tuple ``(args, output_dir, paths)`` where ``paths`` is a
    dict with keys ``launch_manifest``, ``intent``, ``resolved_config``
    pointing at the seeded sentinel files inside ``output_dir``.
    """
    output_root = tmp_path / "outputs"
    output_dir = output_root / "test-run"
    config_path = _write_minimal_run_config(
        tmp_path, run_name="test-run", output_root=output_root,
    )

    launch_manifest, intent_path, resolved_config = _seed_existing_run_outputs(
        output_dir, intent_sentinel="HUMAN-EDITED LINE",
    )

    # Stub git_status so the dirty-tree check never aborts the test.
    monkeypatch.setattr(
        "scripts.run_generalisation.git_status",
        lambda: {
            "commit_sha": "test", "branch": "main",
            "dirty": False, "untracked_file_count": 0,
        },
    )

    parser = build_arg_parser()
    args = parser.parse_args([
        "aggregate-cost",
        "--run-config", str(config_path),
        "--yes",
    ])

    paths = {
        "launch_manifest": launch_manifest,
        "intent": intent_path,
        "resolved_config": resolved_config,
    }
    return args, output_dir, paths


# =============================================================================
# Tests
# =============================================================================


@pytest.mark.tier1
def test_aggregate_cost_preserves_launch_manifest(aggregate_cost_args) -> None:
    """``aggregate-cost`` must not rewrite ``launch_manifest.json``.

    Specifically the operator-visible fields (``status``, ``started_at``,
    ``completed_at``) must survive the call unchanged.
    """
    args, _output_dir, paths = aggregate_cost_args
    pre = json.loads(paths["launch_manifest"].read_text(encoding="utf-8"))

    rc = cmd_aggregate_cost(args)
    assert rc == 0, f"cmd_aggregate_cost returned {rc}, expected 0."

    post = json.loads(paths["launch_manifest"].read_text(encoding="utf-8"))
    assert post["status"] == pre["status"] == "completed", (
        "launch_manifest 'status' was modified by aggregate-cost."
    )
    assert post["started_at"] == pre["started_at"] == "2026-03-31T00:00:00Z"
    assert post["completed_at"] == pre["completed_at"] == "2026-04-01T00:00:00Z"


@pytest.mark.tier1
def test_aggregate_cost_preserves_intent_md(aggregate_cost_args) -> None:
    """A sentinel string in ``experiment_intent.md`` must survive aggregate-cost."""
    args, _output_dir, paths = aggregate_cost_args

    rc = cmd_aggregate_cost(args)
    assert rc == 0

    post = paths["intent"].read_text(encoding="utf-8")
    assert "HUMAN-EDITED LINE" in post, (
        "Sentinel HUMAN-EDITED LINE was lost — intent.md was overwritten."
    )


@pytest.mark.tier1
def test_aggregate_cost_idempotent_sha(aggregate_cost_args) -> None:
    """Two consecutive ``aggregate-cost`` invocations leave launch_manifest
    and experiment_intent byte-identical (sha256 unchanged)."""
    args, _output_dir, paths = aggregate_cost_args

    pre_lm_sha = _sha256_path(paths["launch_manifest"])
    pre_int_sha = _sha256_path(paths["intent"])
    pre_rc_sha = _sha256_path(paths["resolved_config"])

    assert cmd_aggregate_cost(args) == 0
    assert cmd_aggregate_cost(args) == 0

    assert _sha256_path(paths["launch_manifest"]) == pre_lm_sha, (
        "launch_manifest.json sha256 changed after aggregate-cost."
    )
    assert _sha256_path(paths["intent"]) == pre_int_sha, (
        "experiment_intent.md sha256 changed after aggregate-cost."
    )
    assert _sha256_path(paths["resolved_config"]) == pre_rc_sha, (
        "resolved_config.yaml sha256 changed after aggregate-cost."
    )


@pytest.mark.tier1
def test_aggregate_cost_writes_cost_manifest(aggregate_cost_args) -> None:
    """Regression guard: aggregate-cost still produces a parseable
    cost_manifest.json — gating the launch-manifest writes must not
    have broken the subcommand's actual purpose."""
    args, output_dir, _paths = aggregate_cost_args

    rc = cmd_aggregate_cost(args)
    assert rc == 0

    cost_manifest = output_dir / "cost_manifest.json"
    assert cost_manifest.is_file(), (
        "cost_manifest.json was not produced by aggregate-cost."
    )
    # Parses as JSON — readable by downstream tooling.
    data = json.loads(cost_manifest.read_text(encoding="utf-8"))
    assert "totals" in data, "cost_manifest.json missing 'totals' section."
    assert "by_stage" in data, "cost_manifest.json missing 'by_stage' section."
