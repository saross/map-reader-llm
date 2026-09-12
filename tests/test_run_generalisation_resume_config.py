"""
Resume-provenance tests for ``scripts/run_generalisation.py``.

Guards the Finding 3 fix of ``reports/name-keyed-cache-audit-2026-09-12.md``:
the generalisation pipeline's ``--resume`` was keyed by STAGE NAME alone, and
``_prepare_run`` overwrote ``resolved_config.yaml`` / ``experiment_intent.md``
from the current configuration *before* the resume decision was taken — so a
config edit plus ``--resume`` produced a mixed-configuration run whose
artefacts uniformly described the new configuration.

The three behaviours asserted here are the contract of the fix:

1. **Unchanged config** — a resume proceeds, and the launch-time snapshot and
   intent file are left byte-for-byte alone.
2. **Changed config** — the resume refuses, naming the differing fields.
3. **``--allow-config-change``** — the operator can proceed explicitly, and
   the change is logged.

Plus the ``.resume_state.json`` stage-level anchor: a recorded ``config_hash``
that disagrees refuses, and a legacy entry with no hash warns (unknown
provenance) rather than being read as a match.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_generalisation import (  # noqa: E402
    _check_resume_config,
    _load_resume_state,
    _prepare_run,
    _resolved_config_hash,
    _resolved_config_snapshot,
    _save_resume_state,
    _snapshot_diff,
    build_arg_parser,
)

pytestmark = pytest.mark.tier1


# ---------------------------------------------------------------------------
# Fixture scaffolding
# ---------------------------------------------------------------------------


def _write_run_config(
    run_dir: Path,
    *,
    run_name: str,
    output_root: Path,
    temperature: float = 0.3,
) -> Path:
    """Write a minimal, fully-resolvable YAML run-config and return its path.

    Mirrors ``tests/test_aggregate_cost_idempotency._write_minimal_run_config``
    — every field ``resolve_run_config`` validates, with auxiliary files that
    exist but are trivial.
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

    empty_fc = json.dumps({"type": "FeatureCollection", "features": []})
    ground_truth = run_dir / "gt.geojson"
    ground_truth.write_text(empty_fc, encoding="utf-8")
    bounds = run_dir / "bounds.geojson"
    bounds.write_text(empty_fc, encoding="utf-8")

    config = {
        "run_name": run_name,
        "output_root": str(output_root),
        "proposer": {
            "config": str(proposer_config),
            "manifest": str(manifest),
            "tiles_dir": str(tiles_dir),
            "temperature": temperature,
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


@pytest.fixture
def stub_git(monkeypatch) -> None:
    """Stub the dirty-tree check so the launcher never aborts in tests."""
    monkeypatch.setattr(
        "scripts.run_generalisation.git_status",
        lambda: {
            "commit_sha": "test", "branch": "main",
            "dirty": False, "untracked_file_count": 0,
        },
    )


def _args(config_path: Path, *extra: str):
    """Parse an ``all`` invocation against *config_path*."""
    parser = build_arg_parser()
    return parser.parse_args(
        ["all", "--run-config", str(config_path), "--yes", *extra],
    )


# ---------------------------------------------------------------------------
# _prepare_run: the resolved_config.yaml comparison
# ---------------------------------------------------------------------------


def test_fresh_launch_writes_snapshot_and_intent(tmp_path, stub_git) -> None:
    """A run that is NOT resumed behaves exactly as before: both files written."""
    output_root = tmp_path / "outputs"
    config_path = _write_run_config(
        tmp_path, run_name="gen-run", output_root=output_root,
    )
    _prepare_run(_args(config_path))

    out = output_root / "gen-run"
    assert (out / "resolved_config.yaml").is_file()
    assert (out / "experiment_intent.md").is_file()
    assert (out / "launch_manifest.json").is_file()


def test_resume_with_unchanged_config_preserves_launch_artefacts(
    tmp_path, stub_git,
) -> None:
    """Resuming an unchanged config proceeds and rewrites nothing."""
    output_root = tmp_path / "outputs"
    config_path = _write_run_config(
        tmp_path, run_name="gen-run", output_root=output_root,
    )
    _prepare_run(_args(config_path))

    out = output_root / "gen-run"
    snapshot_before = (out / "resolved_config.yaml").read_bytes()
    intent_before = (out / "experiment_intent.md").read_bytes()

    # A resume with no config edit must not raise and must not rewrite.
    _prepare_run(_args(config_path, "--resume"))

    assert (out / "resolved_config.yaml").read_bytes() == snapshot_before
    assert (out / "experiment_intent.md").read_bytes() == intent_before


def test_resume_with_changed_config_refuses_and_names_the_field(
    tmp_path, stub_git,
) -> None:
    """A changed config refuses the resume and prints the differing field."""
    output_root = tmp_path / "outputs"
    config_path = _write_run_config(
        tmp_path, run_name="gen-run", output_root=output_root, temperature=0.3,
    )
    _prepare_run(_args(config_path))
    snapshot_before = (output_root / "gen-run" / "resolved_config.yaml").read_bytes()

    with pytest.raises(SystemExit) as excinfo:
        _prepare_run(_args(config_path, "--resume", "--temperature", "0.7"))

    message = str(excinfo.value)
    assert "Refusing to resume" in message
    assert "proposer.temperature: 0.3 → 0.7" in message
    assert "--allow-config-change" in message
    # The refusal happens BEFORE the snapshot is overwritten.
    assert (
        output_root / "gen-run" / "resolved_config.yaml"
    ).read_bytes() == snapshot_before


def test_allow_config_change_proceeds_and_updates_the_snapshot(
    tmp_path, stub_git, caplog,
) -> None:
    """The explicit override proceeds, logs the change, and rewrites the snapshot."""
    output_root = tmp_path / "outputs"
    config_path = _write_run_config(
        tmp_path, run_name="gen-run", output_root=output_root, temperature=0.3,
    )
    _prepare_run(_args(config_path))

    with caplog.at_level("WARNING"):
        _prepare_run(_args(
            config_path, "--resume", "--allow-config-change",
            "--temperature", "0.7",
        ))

    snapshot = yaml.safe_load(
        (output_root / "gen-run" / "resolved_config.yaml").read_text(
            encoding="utf-8",
        ),
    )
    assert snapshot["proposer"]["temperature"] == 0.7
    assert "--allow-config-change" in caplog.text


def test_unreadable_snapshot_is_unknown_provenance_not_a_match(
    tmp_path, stub_git, caplog,
) -> None:
    """A snapshot that will not parse warns and is left in place."""
    output_root = tmp_path / "outputs"
    config_path = _write_run_config(
        tmp_path, run_name="gen-run", output_root=output_root,
    )
    out = output_root / "gen-run"
    out.mkdir(parents=True)
    (out / "resolved_config.yaml").write_text("[not, a, mapping]\n", encoding="utf-8")

    with caplog.at_level("WARNING"):
        _prepare_run(_args(config_path, "--resume"))

    assert "UNKNOWN" in caplog.text
    assert (out / "resolved_config.yaml").read_text(
        encoding="utf-8",
    ) == "[not, a, mapping]\n"


def test_resumed_intent_difference_is_logged_not_overwritten(
    tmp_path, stub_git, caplog,
) -> None:
    """An existing intent file survives a resume; the difference is logged.

    Mirrors ``lib_experiment_intent.write_experiment_intent``: the
    launch-time record of what the operator confirmed is never rewritten
    by a resume.
    """
    output_root = tmp_path / "outputs"
    config_path = _write_run_config(
        tmp_path, run_name="gen-run", output_root=output_root,
    )
    _prepare_run(_args(config_path))
    intent = output_root / "gen-run" / "experiment_intent.md"
    intent.write_text(
        intent.read_text(encoding="utf-8") + "\nHUMAN NOTE: keep me\n",
        encoding="utf-8",
    )

    with caplog.at_level("WARNING"):
        _prepare_run(_args(config_path, "--resume", "--allow-config-change",
                           "--temperature", "0.7"))

    assert "HUMAN NOTE: keep me" in intent.read_text(encoding="utf-8")
    assert "not overwriting" in caplog.text


# ---------------------------------------------------------------------------
# .resume_state.json: the per-stage content anchor
# ---------------------------------------------------------------------------


def test_save_resume_state_records_the_config_hash(tmp_path, stub_git) -> None:
    """Each completed stage records the hash of the config that ran it."""
    output_root = tmp_path / "outputs"
    config_path = _write_run_config(
        tmp_path, run_name="gen-run", output_root=output_root,
    )
    rcfg = _prepare_run(_args(config_path))
    cfg_hash = _resolved_config_hash(rcfg)

    _save_resume_state(
        rcfg.output_dir, "proposer", {"passes": 5},
        config_hash_value=cfg_hash,
        config_snapshot=_resolved_config_snapshot(rcfg),
    )

    state = _load_resume_state(rcfg.output_dir)
    assert state["proposer"]["config_hash"] == cfg_hash
    assert state["_config"]["hash"] == cfg_hash
    assert state["_config"]["snapshot"]["proposer"]["passes"] == 5
    # Stage-name membership — the behaviour cmd_all relies on — is unchanged.
    assert "proposer" in state


def test_check_resume_config_refuses_a_stale_stage_hash() -> None:
    """A completed stage whose config hash differs refuses the resume."""
    state = {
        "proposer": {"completed_at": "t", "summary": {}, "config_hash": "old"},
        "_config": {
            "hash": "old",
            "snapshot": {"proposer": {"temperature": 0.3}},
        },
    }
    with pytest.raises(SystemExit) as excinfo:
        _check_resume_config(
            state, "new", {"proposer": {"temperature": 0.7}},
            allow_config_change=False,
        )
    message = str(excinfo.value)
    assert "Refusing to resume" in message
    assert "proposer" in message
    assert "proposer.temperature: 0.3 → 0.7" in message


def test_check_resume_config_allows_with_the_override(caplog) -> None:
    """``--allow-config-change`` downgrades the refusal to a warning."""
    state = {
        "proposer": {"completed_at": "t", "summary": {}, "config_hash": "old"},
    }
    with caplog.at_level("WARNING"):
        _check_resume_config(
            state, "new", {"proposer": {"temperature": 0.7}},
            allow_config_change=True,
        )
    assert "--allow-config-change" in caplog.text


def test_check_resume_config_passes_when_hashes_agree(caplog) -> None:
    """Matching hashes are silent — no warning, no refusal."""
    state = {
        "proposer": {"completed_at": "t", "summary": {}, "config_hash": "same"},
    }
    with caplog.at_level("WARNING"):
        _check_resume_config(
            state, "same", {"proposer": {"temperature": 0.3}},
            allow_config_change=False,
        )
    assert caplog.text == ""


def test_legacy_state_without_hash_warns_but_proceeds(caplog) -> None:
    """A pre-fix state file is unknown provenance, never a verified match."""
    state = {"proposer": {"completed_at": "t", "summary": {}}}
    with caplog.at_level("WARNING"):
        _check_resume_config(
            state, "current", {"proposer": {"temperature": 0.3}},
            allow_config_change=False,
        )
    assert "UNKNOWN" in caplog.text
    assert "proposer" in caplog.text


# ---------------------------------------------------------------------------
# The diff helper
# ---------------------------------------------------------------------------


def test_snapshot_diff_reports_nested_and_absent_fields() -> None:
    """The diff is field-level, dotted, and marks absent fields explicitly."""
    lines = _snapshot_diff(
        {"verify": {"config": "a.json"}, "evaluate": {"prob_threshold": 0.5}},
        {"verify": {"config": "b.json", "mode": "batch"},
         "evaluate": {"prob_threshold": 0.5}},
    )
    assert lines == [
        "    - verify.config: a.json → b.json",
        "    - verify.mode: (absent) → batch",
    ]


def test_snapshot_diff_is_empty_for_identical_snapshots() -> None:
    """No differences means no lines — the unchanged-resume path."""
    snapshot = {"proposer": {"temperature": 0.3, "passes": 5}}
    assert _snapshot_diff(snapshot, dict(snapshot)) == []
