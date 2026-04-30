"""
Tier 1 tests for ``scripts.evaluate_detections._build_metadata``.

Asserts the schema of the ``_metadata`` block that future
``evaluation.json`` outputs will embed. The block makes each output
self-documenting so that reviewers can reproduce bootstrap confidence
intervals without reading the script source.

These tests exercise the helper in isolation — they do NOT run the
full evaluation pipeline, load GeoJSON, or write any output files.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import (  # noqa: E402
    _build_metadata,
    _git_short_hash,
    _git_status,
    _serialise_cli_args,
)


# =========================================================================
# FIXTURES
# =========================================================================


def _make_args(**overrides: object) -> argparse.Namespace:
    """Build a parsed-argparse-like namespace for ``_build_metadata``.

    Defaults mirror a typical single-mode invocation: one detections
    file, the canonical ground-truth and bounds paths, 1000 bootstrap
    iterations, seed 42.
    """
    base = {
        "detections": [Path("outputs/run_1/detections.geojson")],
        "detections_dir": None,
        "batch": None,
        "ground_truth": Path("inputs/vectors/references/mounds-reference.geojson"),
        "bounds": Path("inputs/vectors/bounds/384/full_evaluation_bounds.geojson"),
        "bootstrap": 1000,
        "seed": 42,
        "buffers": [20],
        "output_dir": Path("results/test"),
        "label": None,
        "glob": "*/detections_*.geojson",
        "mcc": False,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


# =========================================================================
# SCHEMA TESTS
# =========================================================================


@pytest.mark.tier1
class TestBuildMetadataSchema:
    """Ensure the returned dict matches the documented schema."""

    def test_top_level_keys(self) -> None:
        """The metadata block exposes all specified top-level keys."""
        args = _make_args()
        meta = _build_metadata(args)
        expected = {
            "metadata_version",
            "script_path",
            "script_git_commit",
            "script_git_status",
            "generated_at_utc",
            "cli_args",
            "bootstrap",
            "input_files",
        }
        assert expected.issubset(meta.keys())

    def test_metadata_version_literal(self) -> None:
        """Schema version is pinned at 1.1 for downstream consumers.

        Bumped 2026-04-29 with the introduction of the BCa bootstrap
        method and the Mitigation 3 sparse-coverage flag (commit
        ``feat(bootstrap): replace percentile method with BCa``).
        Downstream consumers should treat 1.0 outputs as percentile-method
        and 1.1+ as BCa.
        """
        meta = _build_metadata(_make_args())
        assert meta["metadata_version"] == "1.1"

    def test_script_path_is_relative(self) -> None:
        """Script path is the stable repo-relative location."""
        meta = _build_metadata(_make_args())
        assert meta["script_path"] == "scripts/evaluate_detections.py"

    def test_bootstrap_block(self) -> None:
        """Bootstrap block records iteration count, seed, unit, and method.

        Schema 1.1 adds ``method`` and ``library`` keys recording the
        BCa upgrade from the legacy percentile method.
        """
        args = _make_args(bootstrap=500, seed=7)
        meta = _build_metadata(args)
        assert meta["bootstrap"] == {
            "n_iterations": 500,
            "seed": 7,
            "resampling_unit": "tile_level",
            "method": "BCa",
            "library": "scipy.stats.bootstrap",
        }

    def test_input_files_single_mode(self) -> None:
        """Single-mode detections are captured as a list of strings."""
        args = _make_args()
        meta = _build_metadata(args)
        assert meta["input_files"]["detections"] == [
            "outputs/run_1/detections.geojson",
        ]
        assert meta["input_files"]["ground_truth"].endswith(
            "mounds-reference.geojson",
        )
        assert meta["input_files"]["bounds"].endswith(
            "full_evaluation_bounds.geojson",
        )

    def test_input_files_dir_mode(self) -> None:
        """``--detections-dir`` mode records the directory as a string."""
        args = _make_args(
            detections=None,
            detections_dir=Path("outputs/retest/h11"),
        )
        meta = _build_metadata(args)
        assert meta["input_files"]["detections"] == "outputs/retest/h11"

    def test_input_files_batch_mode(self) -> None:
        """Batch mode records the YAML spec path."""
        args = _make_args(
            detections=None,
            batch=Path("configs/batch/h11.yaml"),
        )
        meta = _build_metadata(args)
        assert meta["input_files"]["detections"] == "configs/batch/h11.yaml"

    def test_cli_args_are_json_safe(self) -> None:
        """Path values in cli_args are serialised to strings."""
        meta = _build_metadata(_make_args())
        args_dict = meta["cli_args"]
        assert isinstance(args_dict["ground_truth"], str)
        assert isinstance(args_dict["bounds"], str)
        assert isinstance(args_dict["detections"], list)
        assert all(isinstance(d, str) for d in args_dict["detections"])

    def test_generated_at_utc_iso_format(self) -> None:
        """Timestamp is an ISO-8601 string with timezone info."""
        meta = _build_metadata(_make_args())
        ts = meta["generated_at_utc"]
        assert isinstance(ts, str)
        # An ISO-8601 UTC timestamp includes a 'T' separator and +00:00.
        assert "T" in ts
        assert "+00:00" in ts or ts.endswith("Z")


# =========================================================================
# GIT HELPER TESTS
# =========================================================================


@pytest.mark.tier1
class TestGitHelpersFallback:
    """The git helpers must never raise, even when git is unavailable."""

    def test_short_hash_returns_unknown_when_git_missing(self) -> None:
        """FileNotFoundError (git absent) maps to the 'unknown' literal."""
        with patch(
            "scripts.evaluate_detections.subprocess.run",
            side_effect=FileNotFoundError,
        ):
            assert _git_short_hash(PROJECT_ROOT) == "unknown"

    def test_status_returns_unknown_when_git_missing(self) -> None:
        """FileNotFoundError (git absent) maps to the 'unknown' literal."""
        with patch(
            "scripts.evaluate_detections.subprocess.run",
            side_effect=FileNotFoundError,
        ):
            assert _git_status(PROJECT_ROOT) == "unknown"

    def test_status_clean_or_dirty(self) -> None:
        """Live git status returns one of the documented literals."""
        status = _git_status(PROJECT_ROOT)
        assert status in {"clean", "dirty", "unknown"}


# =========================================================================
# SERIALISATION TESTS
# =========================================================================


@pytest.mark.tier1
class TestSerialiseCliArgs:
    """Guarantee that Path values become strings for JSON output."""

    def test_path_becomes_string(self) -> None:
        """Scalar Path values are stringified."""
        ns = argparse.Namespace(p=Path("a/b"))
        assert _serialise_cli_args(ns) == {"p": "a/b"}

    def test_list_of_paths(self) -> None:
        """Each Path inside a list is individually stringified."""
        ns = argparse.Namespace(paths=[Path("a"), Path("b")])
        assert _serialise_cli_args(ns) == {"paths": ["a", "b"]}

    def test_primitives_pass_through(self) -> None:
        """Ints, strings, bools, and None are left untouched."""
        ns = argparse.Namespace(n=10, s="hi", flag=True, missing=None)
        assert _serialise_cli_args(ns) == {
            "n": 10, "s": "hi", "flag": True, "missing": None,
        }
