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
    evaluate_multi_run_mean,
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


# =========================================================================
# MULTI-RUN AGGREGATION ROLLUP TESTS
# =========================================================================


def _make_run(
    *,
    f1_points: list[float],
    coverage_status: str = "normal",
    ci_unreliable: bool = False,
    zero_fraction: float = 0.0,
    n_tiles: int = 100,
    buffers: list[int] | None = None,
) -> dict:
    """Build a minimal per-run result dict for ``evaluate_multi_run_mean``.

    Mirrors the per-run schema produced by ``evaluate_single_run``,
    populating only the fields the aggregator reads. Each buffer
    distance carries the same coverage flags so a single run is
    either uniformly normal or uniformly sparse — adequate for the
    rollup tests below.

    Args:
        f1_points: Per-buffer F1 point estimates. Treated as the
            canonical ``f1`` and ``f1_point`` value for that buffer;
            precision/recall mirror the same value to keep the
            fixture compact.
        coverage_status: Either ``"normal"`` or ``"sparse_cross_grid"``.
        ci_unreliable: Whether each buffer entry is flagged unreliable.
        zero_fraction: Per-run coverage zero-fraction (used for the
            max-rollup assertion).
        n_tiles: Per-run effective sample size (used for the
            min-rollup assertion).
        buffers: Buffer distances in metres; defaults to a single
            20 m buffer matching each ``f1_points`` entry.

    Returns:
        A dict shaped like one element of ``run_results``.
    """
    if buffers is None:
        buffers = [20] * len(f1_points)
    assert len(buffers) == len(f1_points), (
        "buffers and f1_points must align"
    )
    buf_entries = []
    for buf_m, f1 in zip(buffers, f1_points, strict=True):
        buf_entries.append({
            "buffer_metres": buf_m,
            "f1": f1,
            "f1_point": f1,
            "f1_ci_lower": max(0.0, f1 - 0.05),
            "f1_ci_upper": min(1.0, f1 + 0.05),
            "precision": f1,
            "p_point": f1,
            "p_ci_lower": max(0.0, f1 - 0.05),
            "p_ci_upper": min(1.0, f1 + 0.05),
            "recall": f1,
            "r_point": f1,
            "r_ci_lower": max(0.0, f1 - 0.05),
            "r_ci_upper": min(1.0, f1 + 0.05),
            "coverage": {
                "n_tiles": n_tiles,
                "zero_fraction": zero_fraction,
            },
            "coverage_status": coverage_status,
            "ci_unreliable": ci_unreliable,
        })
    return {
        "label": "synthetic-run",
        "n_detections": 10,
        "buffers": buf_entries,
        "ci_unreliable_any_buffer": ci_unreliable,
        "coverage_status": coverage_status,
    }


@pytest.mark.tier1
class TestMultiRunAggregationRollup:
    """Schema 1.1 parity rollups for ``evaluate_multi_run_mean``.

    The non-aggregated (single-pass) cells expose
    ``coverage_status``, ``ci_unreliable``, ``ci_zero_fraction``,
    ``ci_n_tiles``, and ``*_point`` fields at the per-buffer level
    and ``ci_unreliable_any_buffer`` / ``coverage_status`` at the
    cell level. After the BCa migration, aggregated cells lacked
    these summary-level rollups; the fields lived only at
    ``per_run[i].buffers[*]``. These tests assert the rollup
    behaviour: any-true for sparsity flags, max for zero-fraction,
    min for n_tiles, and arithmetic mean for ``*_point`` aliases.
    """

    def test_sparse_rollup_any_run_flags_summary(self) -> None:
        """A single sparse run flips the aggregated cell to sparse.

        Three-run synthetic cell where exactly one run carries
        ``coverage_status = "sparse_cross_grid"``. The conservative
        any-true rollup must surface that as the summary's coverage
        status and ``ci_unreliable`` flag, mirroring the cell-level
        any-buffer rule used for non-aggregated cells.
        """
        run_a = _make_run(f1_points=[0.50])
        run_b = _make_run(
            f1_points=[0.60],
            coverage_status="sparse_cross_grid",
            ci_unreliable=True,
            zero_fraction=0.62,
            n_tiles=40,
        )
        run_c = _make_run(f1_points=[0.55])

        summary = evaluate_multi_run_mean(
            [run_a, run_b, run_c], label="sparse-rollup",
        )
        buf = summary["buffers"][0]
        assert buf["coverage_status"] == "sparse_cross_grid"
        assert buf["ci_unreliable"] is True
        assert summary["ci_unreliable_any_buffer"] is True
        assert summary["coverage_status"] == "sparse_cross_grid"
        # Worst-case rollups: max zero-fraction across runs (only
        # run_b is non-zero), min n_tiles across runs (run_b at 40).
        assert buf["ci_zero_fraction"] == pytest.approx(0.62)
        assert buf["ci_n_tiles"] == 40

    def test_dense_pass_through_normal_status(self) -> None:
        """All-dense runs leave the summary normal and reliable.

        Three-run synthetic cell where every run reports normal
        coverage. The rollup must not spuriously promote any buffer
        to sparse, must keep ``ci_unreliable = False`` everywhere,
        and must produce a worst-case zero-fraction of 0.0 with the
        smallest run-level n_tiles.
        """
        runs = [
            _make_run(
                f1_points=[0.70],
                zero_fraction=0.0,
                n_tiles=120,
            ),
            _make_run(
                f1_points=[0.72],
                zero_fraction=0.0,
                n_tiles=110,
            ),
            _make_run(
                f1_points=[0.68],
                zero_fraction=0.0,
                n_tiles=115,
            ),
        ]
        summary = evaluate_multi_run_mean(runs, label="dense-pass")
        buf = summary["buffers"][0]
        assert buf["coverage_status"] == "normal"
        assert buf["ci_unreliable"] is False
        assert summary["ci_unreliable_any_buffer"] is False
        assert summary["coverage_status"] == "normal"
        assert buf["ci_zero_fraction"] == pytest.approx(0.0)
        # Min across runs is the 110-tile run.
        assert buf["ci_n_tiles"] == 110

    def test_point_equals_mean_of_per_run_points(self) -> None:
        """Summary ``f1_point`` equals the arithmetic mean of per-run F1s.

        Schema parity: non-aggregated cells expose
        ``f1_point`` / ``p_point`` / ``r_point`` at the per-buffer
        level. The aggregator must surface the same aliases at
        ``summary.buffers[*]``, computed as the mean of per-run
        point estimates. Because the synthetic fixture sets
        precision/recall equal to the F1 point, all three aliases
        share the same expected mean.
        """
        per_run_f1s = [0.40, 0.50, 0.60]
        runs = [_make_run(f1_points=[v]) for v in per_run_f1s]
        summary = evaluate_multi_run_mean(runs, label="point-mean")
        buf = summary["buffers"][0]
        # Mean of [0.40, 0.50, 0.60] = 0.50
        expected_mean = sum(per_run_f1s) / len(per_run_f1s)
        assert buf["f1_point"] == pytest.approx(expected_mean, abs=1e-6)
        assert buf["p_point"] == pytest.approx(expected_mean, abs=1e-6)
        assert buf["r_point"] == pytest.approx(expected_mean, abs=1e-6)
        # The canonical ``f1`` (already averaged in the legacy
        # aggregator) must agree with the new ``f1_point`` alias to
        # within float epsilon — they are conceptually identical.
        assert buf["f1"] == pytest.approx(buf["f1_point"], abs=1e-6)
