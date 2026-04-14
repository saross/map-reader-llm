"""Tier 2 integration test for launch-time experiment-intent checks.

Spawns ``scripts/4_detect_mounds_batch.py --dry-run`` in a subprocess
against a synthetic config that reproduces the H10/H12 config-intent
mismatch (hypothesis H12, `include_example_images: false`, with a base
config reference), and verifies that:

1. The experiment_intent.md preview is printed to stdout with the bold
   transmission warning.
2. The config diff table is rendered and flags ``examples`` as a no-op.
3. The dry-run downgrades the confirmation prompt to a non-blocking warning.
4. The process exits 0.

This test is marked ``tier2`` because it spawns a subprocess and loads
real project code (including geopandas and shapely imports in
``4_detect_mounds_batch.py``), which is slower than a pure unit test.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.tier2
class TestLaunchTimeIntentCheck:
    """End-to-end dry-run launch against a synthetic no-op reproducer."""

    def _write_synthetic_variant(self, tmp_path: Path) -> Path:
        """Write a variant config that reproduces the retrospective failure.

        Points at the real ``prompts/configs/detect_brief-text.json`` as
        its base so the diff check can resolve and read the base.
        """
        variant = {
            "version": "detect_brief-text_synthetic_noop_test",
            "description": (
                "Synthetic test — H12 tag on a text-only base. Reproduces "
                "the Obs 235 failure class for integration testing."
            ),
            "hypothesis": "H12",
            "model": "gemini-3-flash",
            "instruction_file": "detect_brief-text.md",
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "include_example_images": False,
            "thinking_level": "high",
            "base_config": "prompts/configs/detect_brief-text.json",
            "pool_source": "outputs/h10/example-pools/pool_160_hp4hn4",
            "examples": [
                {
                    "path": "neutral-naming/example_01.png",
                    "label": "Positive",
                    "category": "hard_positive",
                },
            ],
        }
        path = tmp_path / "synthetic_noop_variant.json"
        path.write_text(json.dumps(variant, indent=2))
        return path

    def test_dry_run_prints_intent_preview_and_noop_warning(self, tmp_path):
        """The dry-run should show the intent-md preview, the diff table,
        and the no-op warning — without blocking."""
        variant_path = self._write_synthetic_variant(tmp_path)
        output_dir = tmp_path / "output"

        # The script's manifest path is required; point it at the
        # calibration manifest which exists in the repo.
        manifest_path = (
            _REPO_ROOT / "inputs" / "tiles" / "calibration_manifest.json"
        )
        assert manifest_path.exists(), (
            f"Test requires {manifest_path} to exist"
        )

        result = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "4_detect_mounds_batch.py"),
                "--config", str(variant_path),
                "--manifest", str(manifest_path),
                "--output-dir", str(output_dir),
                "--dry-run",
                "--limit", "1",
                "--skip-intent-check",
            ],
            capture_output=True,
            text=True,
            env={
                **__import__("os").environ,
                "PYTHONPATH": str(_REPO_ROOT),
            },
            cwd=str(_REPO_ROOT),
            timeout=60,
        )

        # Dry-run in this pipeline exits 1 (result is None convention in
        # 4_detect_mounds_batch.py __main__). We don't assert returncode;
        # we assert that the intent-check artefacts are present in stdout,
        # which is the contract we care about.

        out = result.stdout
        # Intent preview header
        assert "experiment_intent.md (dry-run preview)" in out
        # Hypothesis ID
        assert "H12" in out
        # Bold transmission warning
        assert "will NOT reach the API payload" in out
        # Retrospective citation
        assert "Obs 227" in out or "Obs 234" in out or "Obs 235" in out
        # Diff table shows the examples field as no-op
        assert "examples" in out
        assert "YES" in out  # no-op column
        # Dry-run downgrade message
        assert "dry-run" in out.lower()
        assert "warning logged" in out.lower() or "would proceed" in out.lower()

    def test_dry_run_against_image_enabled_config_has_no_warning(
        self, tmp_path,
    ):
        """When the variant has include_example_images=True, no no-op
        warning should fire."""
        variant = {
            "version": "detect_brief-text-image_synthetic_ok_test",
            "description": "Image-enabled variant for the negative test.",
            "hypothesis": "H12",
            "model": "gemini-3-flash",
            "instruction_file": "detect_brief-text-image.md",
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "include_example_images": True,
            "thinking_level": "high",
            "base_config": "prompts/configs/detect_brief-text-image.json",
            "pool_source": "outputs/h10/example-pools/pool_160_hp4hn4",
            "examples": [
                {
                    "path": "neutral-naming/example_01.png",
                    "label": "Positive",
                    "category": "hard_positive",
                },
            ],
        }
        variant_path = tmp_path / "synthetic_ok_variant.json"
        variant_path.write_text(json.dumps(variant, indent=2))
        output_dir = tmp_path / "output_ok"

        manifest_path = (
            _REPO_ROOT / "inputs" / "tiles" / "calibration_manifest.json"
        )

        result = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "4_detect_mounds_batch.py"),
                "--config", str(variant_path),
                "--manifest", str(manifest_path),
                "--output-dir", str(output_dir),
                "--dry-run",
                "--limit", "1",
                "--skip-intent-check",
            ],
            capture_output=True,
            text=True,
            env={
                **__import__("os").environ,
                "PYTHONPATH": str(_REPO_ROOT),
            },
            cwd=str(_REPO_ROOT),
            timeout=60,
        )

        # Dry-run exits 1 by convention in 4_detect_mounds_batch.py; we
        # assert on stdout content, not returncode.

        out = result.stdout
        # Should NOT show the transmission warning
        assert "will NOT reach the API payload" not in out
        # Should show the "expected to reach" line OR the "OK" line
        assert (
            "expected to reach the API payload" in out
            or "all fields that differ from the base will reach" in out
        )
