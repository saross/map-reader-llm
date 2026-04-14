"""Tier 1 unit tests for scripts.lib_experiment_intent.

Verifies the experiment_intent.md writer, rerun semantics (match and
mismatch), dry-run behaviour, and the run_launch_checks confirmation gate.
Fixes #2 and #3 from the 2026-04-14 Obs 235 retrospective.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import lib_experiment_intent as lei  # noqa: E402
from lib_experiment_intent import (  # noqa: E402
    run_launch_checks,
    write_experiment_intent,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _write_text_only_base_config(tmp_path: Path) -> Path:
    """Write a minimal text-only base config to a temp path."""
    base = {
        "version": "test-base-text",
        "description": "Test text-only base.",
        "hypothesis": "H1",
        "model": "gemini-3-flash",
        "instruction_file": "detect_brief-text.md",
        "temperature": 0.7,
        "max_output_tokens": 8192,
        "include_example_images": False,
        "thinking_level": "high",
        "examples": [{"path": f"e{i}.png"} for i in range(5)],
    }
    path = tmp_path / "test-base-text.json"
    path.write_text(json.dumps(base, indent=2))
    return path


def _write_variant_config(
    tmp_path: Path,
    base_rel: str,
    include_example_images: bool = False,
    examples: list | None = None,
) -> tuple[Path, dict]:
    variant = {
        "version": "test-variant",
        "description": "Test variant.",
        "hypothesis": "H12",
        "model": "gemini-3-flash",
        "instruction_file": "detect_brief-text.md",
        "temperature": 0.7,
        "max_output_tokens": 8192,
        "include_example_images": include_example_images,
        "thinking_level": "high",
        "examples": examples if examples is not None else [
            {"path": f"v{i}.png"} for i in range(17)
        ],
        "base_config": base_rel,
        "pool_source": "outputs/h10/example-pools/test",
    }
    path = tmp_path / "test-variant.json"
    path.write_text(json.dumps(variant, indent=2))
    return path, variant


@pytest.fixture
def dummy_repo(tmp_path, monkeypatch):
    """Point lib_experiment_intent's _REPO_ROOT at a temp dir.

    Also creates a text-only base config under the temp 'repo' and a
    matching variant that references it via ``base_config``.
    """
    # Lay out a pretend repo: base_config lives at prompts/configs/...
    configs_dir = tmp_path / "prompts" / "configs"
    configs_dir.mkdir(parents=True)
    base_path = _write_text_only_base_config(configs_dir)
    base_rel = str(base_path.relative_to(tmp_path))

    variant_path, variant = _write_variant_config(
        configs_dir, base_rel=base_rel, include_example_images=False,
    )

    monkeypatch.setattr(lei, "_REPO_ROOT", tmp_path)

    return {
        "repo_root": tmp_path,
        "base_path": base_path,
        "base_rel": base_rel,
        "variant_path": variant_path,
        "variant": variant,
        "experiment_root": tmp_path / "outputs" / "test_experiment",
    }


# ---------------------------------------------------------------------------
# write_experiment_intent
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestWriteExperimentIntent:
    """Tests for the intent markdown writer."""

    def test_writes_intent_md_to_experiment_root(self, dummy_repo):
        path, is_consistent, diffs = write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=False,
        )
        assert path is not None
        assert path.exists()
        assert path.name == "experiment_intent.md"
        assert is_consistent is True

    def test_intent_md_includes_transmission_warning_for_text_only(
        self, dummy_repo,
    ):
        """H12 variant on a text-only base must show the bold warning."""
        path, _, _ = write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=False,
        )
        text = path.read_text()
        assert "will NOT reach the API payload" in text
        assert "H12" in text
        assert "`examples`" in text  # listed as a no-op field

    def test_intent_md_omits_warning_when_modality_matches(
        self, dummy_repo, tmp_path,
    ):
        """Same variant but with include_example_images=True must not
        show the transmission warning."""
        # Rewrite the base to be image-enabled
        base = json.loads(dummy_repo["base_path"].read_text())
        base["include_example_images"] = True
        dummy_repo["base_path"].write_text(json.dumps(base, indent=2))
        dummy_repo["variant"]["include_example_images"] = True

        path, _, _ = write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=False,
        )
        text = path.read_text()
        assert "will NOT reach the API payload" not in text
        assert "expected to reach the API payload" in text

    def test_intent_md_not_overwritten_on_rerun_with_match(self, dummy_repo):
        path1, _, _ = write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=False,
        )
        original_mtime = path1.stat().st_mtime_ns
        path2, is_consistent, _ = write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=False,
        )
        assert path2 == path1
        # Mtime unchanged — not overwritten
        assert path2.stat().st_mtime_ns == original_mtime
        assert is_consistent is True

    def test_intent_md_mismatch_on_rerun_returns_inconsistent(self, dummy_repo):
        """Rerun with a different temperature must flag inconsistency."""
        write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=False,
        )
        # Second call with a modified temperature
        dummy_repo["variant"]["temperature"] = 1.3
        _, is_consistent, _ = write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=False,
        )
        assert is_consistent is False

    def test_dry_run_does_not_write_file(self, dummy_repo, capsys):
        path, is_consistent, diffs = write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=True,
        )
        assert path is None
        assert is_consistent is True
        captured = capsys.readouterr()
        assert "experiment_intent.md (dry-run preview)" in captured.out
        assert "Experiment Intent" in captured.out
        assert not (
            dummy_repo["experiment_root"] / "experiment_intent.md"
        ).exists()

    def test_legacy_variant_without_base_config_field(
        self, dummy_repo, capsys,
    ):
        """A variant without `base_config` should still get an intent-md,
        with the diff section skipped."""
        del dummy_repo["variant"]["base_config"]
        path, _, diffs = write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=False,
        )
        assert path.exists()
        text = path.read_text()
        assert "(not recorded)" in text
        assert "Diff skipped" in text
        assert diffs == []


# ---------------------------------------------------------------------------
# run_launch_checks
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestRunLaunchChecks:
    """Tests for the combined launch-time guard."""

    def test_no_op_detected_aborts_on_no_confirmation(
        self, dummy_repo, monkeypatch,
    ):
        """Stdin 'n' must abort when a no-op is detected."""
        monkeypatch.setattr("sys.stdin", io.StringIO("n\n"))
        result = run_launch_checks(
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            experiment_root=dummy_repo["experiment_root"],
            dry_run=False,
            skip_intent_check=False,
        )
        assert result is False

    def test_no_op_detected_proceeds_on_yes(
        self, dummy_repo, monkeypatch,
    ):
        """Stdin 'y' must proceed."""
        monkeypatch.setattr("sys.stdin", io.StringIO("y\n"))
        result = run_launch_checks(
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            experiment_root=dummy_repo["experiment_root"],
            dry_run=False,
            skip_intent_check=False,
        )
        assert result is True

    def test_no_op_detected_aborts_on_eof(
        self, dummy_repo, monkeypatch,
    ):
        """EOF (empty stdin) must abort."""
        monkeypatch.setattr("sys.stdin", io.StringIO(""))
        result = run_launch_checks(
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            experiment_root=dummy_repo["experiment_root"],
            dry_run=False,
            skip_intent_check=False,
        )
        assert result is False

    def test_skip_intent_check_never_prompts(self, dummy_repo, monkeypatch):
        """--skip-intent-check must proceed without reading stdin."""
        def _no_input(_prompt=""):
            pytest.fail("input() should not be called with skip_intent_check")
        monkeypatch.setattr("builtins.input", _no_input)
        result = run_launch_checks(
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            experiment_root=dummy_repo["experiment_root"],
            dry_run=False,
            skip_intent_check=True,
        )
        assert result is True

    def test_dry_run_never_blocks(self, dummy_repo, monkeypatch):
        """Dry-run must proceed without reading stdin, even with no-op."""
        def _no_input(_prompt=""):
            pytest.fail("input() should not be called in dry-run")
        monkeypatch.setattr("builtins.input", _no_input)
        result = run_launch_checks(
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            experiment_root=dummy_repo["experiment_root"],
            dry_run=True,
            skip_intent_check=False,
        )
        assert result is True

    def test_no_base_config_field_proceeds_with_notice(
        self, dummy_repo, capsys,
    ):
        """Legacy variant without base_config proceeds without prompting."""
        del dummy_repo["variant"]["base_config"]
        result = run_launch_checks(
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            experiment_root=dummy_repo["experiment_root"],
            dry_run=False,
            skip_intent_check=False,
        )
        assert result is True
        captured = capsys.readouterr()
        assert "no base_config recorded" in captured.out

    def test_image_enabled_variant_proceeds_without_prompt(
        self, dummy_repo, monkeypatch,
    ):
        """Variant with include_example_images=True passes all checks."""
        def _no_input(_prompt=""):
            pytest.fail("input() should not be called when no no-op found")
        monkeypatch.setattr("builtins.input", _no_input)

        # Rewrite base to be image-enabled
        base = json.loads(dummy_repo["base_path"].read_text())
        base["include_example_images"] = True
        dummy_repo["base_path"].write_text(json.dumps(base, indent=2))
        dummy_repo["variant"]["include_example_images"] = True

        result = run_launch_checks(
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            experiment_root=dummy_repo["experiment_root"],
            dry_run=False,
            skip_intent_check=False,
        )
        assert result is True

    def test_rerun_with_mismatch_prompts_even_without_no_op(
        self, dummy_repo, monkeypatch,
    ):
        """Rerun with modified config must prompt even if no no-op exists."""
        # First, write with image-enabled variant (no no-op case)
        base = json.loads(dummy_repo["base_path"].read_text())
        base["include_example_images"] = True
        dummy_repo["base_path"].write_text(json.dumps(base, indent=2))
        dummy_repo["variant"]["include_example_images"] = True

        write_experiment_intent(
            experiment_root=dummy_repo["experiment_root"],
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            dry_run=False,
        )
        # Then change temperature — same variant, different settings
        dummy_repo["variant"]["temperature"] = 1.3
        monkeypatch.setattr("sys.stdin", io.StringIO("n\n"))
        result = run_launch_checks(
            config=dummy_repo["variant"],
            config_path=dummy_repo["variant_path"],
            experiment_root=dummy_repo["experiment_root"],
            dry_run=False,
            skip_intent_check=False,
        )
        assert result is False  # aborted on 'n'
