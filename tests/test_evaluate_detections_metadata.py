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
        """Schema version is pinned for downstream consumers.

        Bumped 2026-04-29 with the introduction of the BCa bootstrap
        method and the Mitigation 3 sparse-coverage flag (commit
        ``feat(bootstrap): replace percentile method with BCa``).
        Downstream consumers should treat 1.0 outputs as percentile-method
        and 1.1+ as BCa-requested.
        """
        meta = _build_metadata(_make_args())
        # 1.2 (2026-05-31) added the ``spatial`` block recording the evaluation CRS.
        # 1.3 (2026-08-20, defect D36) split ``bootstrap.method`` into the
        # requested method and a measured one added at write time.
        assert meta["metadata_version"] == "1.3"

    def test_script_path_is_relative(self) -> None:
        """Script path is the stable repo-relative location."""
        meta = _build_metadata(_make_args())
        assert meta["script_path"] == "scripts/evaluate_detections.py"

    def test_bootstrap_block(self) -> None:
        """Bootstrap block records iteration count, seed, unit, and intent.

        Schema 1.1 added ``method`` and ``library`` keys recording the
        BCa upgrade from the legacy percentile method. Schema 1.3
        (defect D36) renamed the literal to ``method_requested``: what
        the code asks the CI helper for is an intent, and the helper
        falls back to the percentile method per metric whenever the BCa
        acceleration is undefined. The observed ``method`` is added by
        ``write_outputs`` once the intervals exist, so it is deliberately
        ABSENT here.
        """
        args = _make_args(bootstrap=500, seed=7)
        meta = _build_metadata(args)
        assert meta["bootstrap"] == {
            "n_iterations": 500,
            "seed": 7,
            "resampling_unit": "tile_level",
            "method_requested": "BCa",
            "library": "scipy.stats.bootstrap",
        }
        assert "method" not in meta["bootstrap"]

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

    def test_input_files_paths_recorded_repo_relative(self) -> None:
        """Absolute paths under the repo are recorded repo-relative (portability).

        An absolute ``/home/<user>/.../map-reader-llm/...`` path embedded in an eval is
        non-portable across clones and trips the run-conditions audit verifier; the
        ``input_files``/``cli_args`` provenance must therefore be repo-relative. This
        guards the regression where batch mode (load_batch_yaml resolves to absolute)
        leaked absolute paths into the metadata.
        """
        from scripts.evaluate_detections import PROJECT_ROOT

        abs_det = PROJECT_ROOT / "outputs/run_1/detections.geojson"
        abs_bounds = PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
        meta = _build_metadata(_make_args(detections=[abs_det], bounds=abs_bounds))
        assert meta["input_files"]["detections"] == ["outputs/run_1/detections.geojson"]
        assert meta["input_files"]["bounds"] == (
            "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
        )
        # cli_args path keys are normalised too; non-path args pass through.
        assert meta["cli_args"]["bounds"] == (
            "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
        )
        assert meta["cli_args"]["glob"] == "*/detections_*.geojson"

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

    def test_sparse_rollup_reports_but_does_not_flag(self) -> None:
        """A sparse run surfaces in coverage but not in the flag (D42).

        Three-run synthetic cell where exactly one run carries
        ``coverage_status = "sparse_cross_grid"``. Under the measured
        rule (2026-08-19 policy, applied corpus-wide by the 2026-08-20
        migration and to fresh aggregates on 2026-08-23), sparseness is
        reported — worst-case ``coverage_status``, ``sparse_coverage``
        true — but ``ci_unreliable`` is measured on the aggregated row
        itself, whose intervals here contain their averaged points.
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
        assert buf["sparse_coverage"] is True
        assert buf["ci_unreliable"] is False
        assert buf["ci_excludes_point"] is False
        assert buf["ci_flag_basis"] == "measured-exclusion-or-partial-coverage"
        assert summary["ci_unreliable_any_buffer"] is False
        assert summary["coverage_status"] == "sparse_cross_grid"
        # Worst-case rollups: max zero-fraction across runs (only
        # run_b is non-zero), min n_tiles across runs (run_b at 40).
        assert buf["ci_zero_fraction"] == pytest.approx(0.62)
        assert buf["ci_n_tiles"] == 40

    def test_aggregated_rows_are_migration_invariant(self) -> None:
        """Fresh aggregate rows must satisfy the migration exactly (D42).

        The E82 campaign showed re-emitted multi-run cells left the
        reliability block null, so ``migrate_ci_flag_basis`` re-touched
        169 files after every re-score. The invariant that closes D42:
        ``migrate_buffer_row`` returns ``None`` (no change) for every
        summary buffer row the aggregator now writes.
        """
        from scripts.migrate_ci_flag_basis import migrate_buffer_row

        runs = [_make_run(f1_points=[0.50, 0.70], buffers=[20, 50]),
                _make_run(f1_points=[0.60, 0.72], buffers=[20, 50]),
                _make_run(f1_points=[0.55, 0.68], buffers=[20, 50])]
        summary = evaluate_multi_run_mean(runs, label="invariant")
        for row in summary["buffers"]:
            assert migrate_buffer_row(dict(row)) is None, row["buffer_metres"]

    def test_aggregated_exclusion_flags_the_summary(self) -> None:
        """An averaged CI excluding its averaged point sets the flag.

        Constructed so each run's own interval contains its own point
        but the averaged bounds exclude the averaged point: exclusion is
        measured on the aggregate row, not rolled up from the runs.
        """
        run_a = _make_run(f1_points=[0.50])
        run_b = _make_run(f1_points=[0.60])
        # Skew run_b's stored bounds upward so the averaged interval
        # [mean lower, mean upper] sits above the averaged point.
        row_b = run_b["buffers"][0]
        for key in ("f1_ci_lower", "p_ci_lower", "r_ci_lower"):
            row_b[key] = 0.62
        for key in ("f1_ci_upper", "p_ci_upper", "r_ci_upper"):
            row_b[key] = 0.70
        summary = evaluate_multi_run_mean([run_a, run_b], label="excl")
        buf = summary["buffers"][0]
        # averaged point 0.55; averaged lower (0.45 + 0.62)/2 = 0.535 —
        # contains. Tighten run_a too so the averaged lower excludes:
        row_a = run_a["buffers"][0]
        for key in ("f1_ci_lower", "p_ci_lower", "r_ci_lower"):
            row_a[key] = 0.50
        summary = evaluate_multi_run_mean([run_a, run_b], label="excl")
        buf = summary["buffers"][0]
        assert buf["f1_ci_lower"] == pytest.approx(0.56)
        assert buf["ci_excludes_point"] is True
        assert buf["ci_unreliable"] is True

    def test_partial_coverage_run_flags_the_aggregate(self) -> None:
        """One partial-coverage run flags the aggregate (E72 ground)."""
        runs = [_make_run(f1_points=[0.50]),
                _make_run(f1_points=[0.60],
                          coverage_status="partial_coverage")]
        summary = evaluate_multi_run_mean(runs, label="partial")
        buf = summary["buffers"][0]
        assert buf["coverage_status"] == "partial_coverage"
        assert buf["ci_unreliable"] is True
        assert buf["ci_excludes_point"] is False

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


# =========================================================================
# D40 INPUT-HYGIENE TESTS
# =========================================================================


def _temp_repo(tmp_path):
    """Initialise a throwaway git repo with one clean, one modified,
    one untracked, and one gitignored file."""
    import subprocess as sp

    def git(*argv):
        sp.run(["git", *argv], cwd=tmp_path, check=True,
               capture_output=True,
               env={"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
                    "HOME": str(tmp_path), "PATH": "/usr/bin:/bin"})

    git("init", "-q")
    (tmp_path / ".gitignore").write_text("ignored.geojson\n")
    (tmp_path / "clean.geojson").write_text("{}")
    (tmp_path / "modified.geojson").write_text("{}")
    git("add", ".gitignore", "clean.geojson", "modified.geojson")
    git("commit", "-q", "-m", "init")
    (tmp_path / "modified.geojson").write_text('{"changed": 1}')
    (tmp_path / "untracked.geojson").write_text("{}")
    (tmp_path / "ignored.geojson").write_text("{}")


@pytest.mark.tier1
class TestInputGitStates:
    """Classification of recipe inputs at scoring time (defect D40)."""

    def test_all_classes(self, tmp_path, monkeypatch) -> None:
        from scripts import evaluate_detections as ed

        _temp_repo(tmp_path)
        monkeypatch.setattr(ed, "PROJECT_ROOT", tmp_path)
        states = ed._input_git_states([
            tmp_path / "clean.geojson",
            tmp_path / "modified.geojson",
            tmp_path / "untracked.geojson",
            tmp_path / "ignored.geojson",
            tmp_path / "absent.geojson",
            "/tmp/somewhere-else.geojson",
            None,
        ])
        assert states["clean.geojson"] == "clean"
        assert states["modified.geojson"] == "modified"
        assert states["untracked.geojson"] == "untracked"
        assert states["ignored.geojson"] == "ignored"
        assert states["absent.geojson"] == "missing"
        assert states["/tmp/somewhere-else.geojson"] == "outside-repo"
        assert None not in states

    def test_build_metadata_stamps_states(self, tmp_path, monkeypatch) -> None:
        from scripts import evaluate_detections as ed

        _temp_repo(tmp_path)
        monkeypatch.setattr(ed, "PROJECT_ROOT", tmp_path)
        args = _make_args(
            detections=[tmp_path / "untracked.geojson"],
            ground_truth=tmp_path / "clean.geojson",
            bounds=tmp_path / "modified.geojson",
        )
        md = ed._build_metadata(args)
        block = md["input_git_state"]
        assert set(block) == {"head", "inputs"}
        assert block["inputs"]["untracked.geojson"] == "untracked"
        assert block["inputs"]["clean.geojson"] == "clean"
        assert block["inputs"]["modified.geojson"] == "modified"


@pytest.mark.tier1
class TestEnforceInputHygiene:
    """Warn by default; refuse under --require-clean-inputs (D40)."""

    @staticmethod
    def _md(states: dict) -> dict:
        return {"input_git_state": {"head": "abc123def", "inputs": states}}

    def test_clean_inputs_pass_silently(self, caplog) -> None:
        from scripts.evaluate_detections import enforce_input_hygiene

        enforce_input_hygiene(
            self._md({"a.geojson": "clean", "b": "ignored",
                      "/tmp/x": "outside-repo"}),
            require_clean=True)

    def test_dirty_input_warns_without_flag(self, caplog) -> None:
        import logging

        from scripts.evaluate_detections import enforce_input_hygiene

        with caplog.at_level(logging.WARNING):
            enforce_input_hygiene(
                self._md({"a.geojson": "modified"}), require_clean=False)
        assert any("D40" in r.message for r in caplog.records)

    def test_dirty_input_refuses_with_flag(self) -> None:
        from scripts.evaluate_detections import enforce_input_hygiene

        with pytest.raises(SystemExit) as exc:
            enforce_input_hygiene(
                self._md({"a.geojson": "untracked"}), require_clean=True)
        assert exc.value.code == 4
