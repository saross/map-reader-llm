"""
Tests for run_pv.py — cleanup subcommand.

Tests the cleanup logic (diff, retry, merge, audit trail) without
making API calls. The ``_verify_realtime()`` function is mocked.
"""

import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure project root is on sys.path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.run_pv import (
    _candidate_result_key,
    _compute_missing_candidates,
    cmd_cleanup,
)


# ── Fixtures ──────────────────────────────────────────────────────────


def _make_manifest(n_candidates: int = 10) -> dict:
    """Build a minimal candidate manifest with n candidates."""
    return {
        "version": "1.0",
        "candidates": [
            {"candidate_id": i, "source_tile": f"tile_{i}.png",
             "centroid_x": 400000.0 + i, "centroid_y": 4700000.0 + i}
            for i in range(n_candidates)
        ],
    }


def _make_probabilities(
    verified_ids: list[int],
    config_version: str = "test-v1",
) -> dict:
    """Build a minimal probabilities.json with results for given IDs."""
    return {
        "version": "1.0",
        "mode": "realtime",
        "verifier_config": config_version,
        "iterations": 1,
        "total_results": len(verified_ids),
        "results": {
            f"candidate_{cid:05d}": {"mound_probability": 0.5}
            for cid in verified_ids
        },
    }


def _setup_cleanup_dirs(
    tmp_path: Path,
    n_candidates: int = 10,
    verified_ids: list[int] | None = None,
) -> tuple[Path, Path, Path]:
    """Create crops-dir, verified-dir, and config for cleanup tests.

    Returns:
        Tuple of (crops_dir, verified_dir, config_path).
    """
    if verified_ids is None:
        verified_ids = list(range(n_candidates))

    # Crops dir with manifest
    crops_dir = tmp_path / "crops"
    crops_dir.mkdir()
    manifest = _make_manifest(n_candidates)
    with open(crops_dir / "candidate_manifest.json", "w") as f:
        json.dump(manifest, f)

    # Verified dir with partial probabilities
    verified_dir = tmp_path / "verified"
    verified_dir.mkdir()
    probs = _make_probabilities(verified_ids)
    with open(verified_dir / "probabilities.json", "w") as f:
        json.dump(probs, f)

    # Minimal verifier config
    config_path = tmp_path / "verifier.json"
    with open(config_path, "w") as f:
        json.dump({"version": "test-v1", "model": "gemini-3-flash",
                    "temperature": 0.0, "max_output_tokens": 8192,
                    "instruction_file": "test.md"}, f)

    return crops_dir, verified_dir, config_path


def _make_args(**kwargs):
    """Build a namespace mimicking parsed CLI arguments."""
    import argparse
    defaults = {
        "crops_dir": None,
        "verified_dir": None,
        "verifier_config": None,
        "service_tier": None,
        "workers": 5,
        "iterations": 1,
        "temperature": None,
        "model": None,
        "thinking_level": None,
        "max_attempts": 3,
        "safe_mode_tokens": None,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ── Tests ─────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestCleanupSubcommand:
    """Tests for the cleanup subcommand in run_pv.py."""

    def test_cleanup_identifies_missing(self, tmp_path):
        """Dry-run correctly identifies missing candidates."""
        crops_dir, verified_dir, config_path = _setup_cleanup_dirs(
            tmp_path, n_candidates=10, verified_ids=[0, 1, 2, 4, 5, 6, 8],
        )
        args = _make_args(
            crops_dir=crops_dir,
            verified_dir=verified_dir,
            verifier_config=config_path,
            dry_run=True,
        )

        exit_code = cmd_cleanup(args)
        assert exit_code == 0  # dry-run always exits 0

        # Verify the missing set is correct (IDs 3, 7, 9)
        missing, _ = _compute_missing_candidates(
            json.load(open(crops_dir / "candidate_manifest.json")),
            verified_dir / "probabilities.json",
        )
        assert missing == {
            "candidate_00003", "candidate_00007", "candidate_00009",
        }

    def test_cleanup_idempotent(self, tmp_path):
        """When all candidates are verified, cleanup reports nothing to do."""
        crops_dir, verified_dir, config_path = _setup_cleanup_dirs(
            tmp_path, n_candidates=5, verified_ids=[0, 1, 2, 3, 4],
        )
        args = _make_args(
            crops_dir=crops_dir,
            verified_dir=verified_dir,
            verifier_config=config_path,
        )

        exit_code = cmd_cleanup(args)
        assert exit_code == 0

    @patch("scripts.run_pv._verify_realtime")
    def test_cleanup_merges_in_place(self, mock_verify, tmp_path):
        """After cleanup, probabilities.json grows and has cleanup_history."""
        crops_dir, verified_dir, config_path = _setup_cleanup_dirs(
            tmp_path, n_candidates=10, verified_ids=[0, 1, 2, 3, 4, 5, 6],
        )

        # Mock _verify_realtime to simulate recovering 2 of 3 missing
        def side_effect(*, manifest, config, crops_base_dir, output_dir,
                        workers, iterations, temperature, model_override,
                        service_tier):
            probs_path = output_dir / "probabilities.json"
            probs = json.load(open(probs_path))
            # "Recover" candidates 7 and 9 (leave 8 missing)
            probs["results"]["candidate_00007"] = {"mound_probability": 0.3}
            probs["results"]["candidate_00009"] = {"mound_probability": 0.8}
            probs["total_results"] = len(probs["results"])
            with open(probs_path, "w") as f:
                json.dump(probs, f)
            return 0

        mock_verify.side_effect = side_effect

        args = _make_args(
            crops_dir=crops_dir,
            verified_dir=verified_dir,
            verifier_config=config_path,
            max_attempts=1,
        )

        exit_code = cmd_cleanup(args)
        assert exit_code == 1  # candidate_00008 still missing

        # Check final probabilities
        probs = json.load(open(verified_dir / "probabilities.json"))
        assert len(probs["results"]) == 9  # 7 original + 2 recovered
        assert "candidate_00007" in probs["results"]
        assert "candidate_00009" in probs["results"]
        assert "candidate_00008" not in probs["results"]

        # Check cleanup_history
        assert "cleanup_history" in probs
        history = probs["cleanup_history"]
        assert len(history) == 1
        assert history[0]["initial_missing"] == 3
        assert history[0]["recovered"] == 2
        assert history[0]["still_missing"] == 1
        assert "candidate_00008" in history[0]["still_missing_ids"]

    def test_cleanup_backup_created(self, tmp_path):
        """Cleanup creates a timestamped backup before modifying."""
        crops_dir, verified_dir, config_path = _setup_cleanup_dirs(
            tmp_path, n_candidates=5, verified_ids=[0, 1, 2],
        )

        # Mock verify to do nothing (candidates stay missing)
        with patch("scripts.run_pv._verify_realtime", return_value=0):
            args = _make_args(
                crops_dir=crops_dir,
                verified_dir=verified_dir,
                verifier_config=config_path,
                max_attempts=1,
            )
            cmd_cleanup(args)

        # Check backup exists
        backups = list(verified_dir.glob("*.backup"))
        assert len(backups) == 1
        assert "pre-cleanup" in backups[0].name

    @patch("scripts.run_pv._verify_realtime")
    def test_cleanup_safe_mode_applied(self, mock_verify, tmp_path):
        """On final attempt with --safe-mode-tokens, config is overridden."""
        crops_dir, verified_dir, config_path = _setup_cleanup_dirs(
            tmp_path, n_candidates=5, verified_ids=[0, 1, 2],
        )
        captured_configs = []

        def side_effect(*, manifest, config, crops_base_dir, output_dir,
                        workers, iterations, temperature, model_override,
                        service_tier):
            captured_configs.append(dict(config))
            return 0

        mock_verify.side_effect = side_effect

        args = _make_args(
            crops_dir=crops_dir,
            verified_dir=verified_dir,
            verifier_config=config_path,
            max_attempts=2,
            safe_mode_tokens=2048,
        )
        cmd_cleanup(args)

        # Attempt 1: normal tokens (8192 from config)
        assert captured_configs[0]["max_output_tokens"] == 8192
        # Attempt 2 (final): safe-mode tokens
        assert captured_configs[1]["max_output_tokens"] == 2048

    @patch("scripts.run_pv._verify_realtime")
    def test_cleanup_exit_code(self, mock_verify, tmp_path):
        """Exit code 1 when candidates remain missing after all attempts."""
        crops_dir, verified_dir, config_path = _setup_cleanup_dirs(
            tmp_path, n_candidates=5, verified_ids=[0, 1, 2],
        )
        mock_verify.return_value = 0  # verify "runs" but recovers nothing

        args = _make_args(
            crops_dir=crops_dir,
            verified_dir=verified_dir,
            verifier_config=config_path,
            max_attempts=2,
        )
        exit_code = cmd_cleanup(args)
        assert exit_code == 1  # 2 candidates still missing
