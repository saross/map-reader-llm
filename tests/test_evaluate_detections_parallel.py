"""Tier 1 tests for parallel batch evaluation in ``scripts.evaluate_detections``.

These tests guard the multi-core batch path added to ``_run_batch_mode``.
The non-negotiable contract is that running a batch with ``--workers 1``
(the serial, legacy path) and with ``--workers 2`` (a process pool) must
produce *identical* per-condition summaries and an identical
``batch_summary.json``. Each condition uses a fixed per-condition seed, so
results are deterministic and independent of execution order; the only thing
parallelism changes is wall-clock time.

The fixtures construct tiny synthetic GeoJSON inputs in ``tmp_path`` that
mirror the shapes the scorer expects:

- **Bounds**: polygons with a ``tile_name`` column whose values match the
  tiling regex ``^(.+?)_x\\d+_y\\d+(?:\\.png)?$`` (see
  ``lib_advanced_metrics.get_map_name``), so the map name resolves correctly.
- **Ground truth**: points with a ``Map`` column equal to that map name (the
  column ``calculate_f1_internal`` auto-detects for the gold-standard set).
- **Detections**: points whose ``source_tile`` column is injected by
  ``_evaluate_condition`` via a spatial join against the bounds — mirroring
  the real pipeline, the fixtures deliberately omit ``source_tile`` so the
  injection path is exercised.

All geometry is authored directly in the evaluation CRS (EPSG:32635, metres),
so buffer distances in metres behave intuitively. Bootstrap iterations are
kept low (100) so the whole suite runs in a couple of seconds.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest
import yaml
from shapely.geometry import Point, box

# Add project root to path for imports.
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import main  # noqa: E402

# Evaluation CRS used throughout the scorer (UTM Zone 35N, metres).
_CRS = "EPSG:32635"

# A single synthetic map name. Tile names must end in the ``_x{N}_y{N}``
# offset suffix so ``get_map_name`` strips it back to this value.
_MAP_NAME = "TESTMAP_32635"

# A 2x2 grid of 1000 m tiles. Two tiles will carry a ground-truth mound (and
# matching detections), the others stay empty — this gives a non-trivial mix
# of populated and empty tiles so MCC/specificity are well defined.
_TILE_SIZE = 1000.0


def _tile_grid() -> gpd.GeoDataFrame:
    """Build a 2x2 grid of square tile boundaries in the evaluation CRS.

    Returns:
        A GeoDataFrame with a ``tile_name`` column (matching the tiling
        regex) and square ``geometry`` polygons, in EPSG:32635.
    """
    records = []
    for ix in range(2):
        for iy in range(2):
            x0 = ix * _TILE_SIZE
            y0 = iy * _TILE_SIZE
            records.append(
                {
                    "tile_name": f"{_MAP_NAME}_x{ix}_y{iy}.png",
                    "geometry": box(x0, y0, x0 + _TILE_SIZE, y0 + _TILE_SIZE),
                }
            )
    return gpd.GeoDataFrame(records, crs=_CRS)


def _ground_truth() -> gpd.GeoDataFrame:
    """Build a small ground-truth point set with a ``Map`` column.

    Two mounds, placed near the centres of the (0,0) and (1,1) tiles so
    they sit unambiguously inside one tile each.

    Returns:
        A GeoDataFrame with a ``Map`` column and point ``geometry``.
    """
    records = [
        {"Map": _MAP_NAME, "geometry": Point(500.0, 500.0)},
        {"Map": _MAP_NAME, "geometry": Point(1500.0, 1500.0)},
    ]
    return gpd.GeoDataFrame(records, crs=_CRS)


def _write_geojson(gdf: gpd.GeoDataFrame, path: Path) -> None:
    """Write a GeoDataFrame to a GeoJSON file, creating parent dirs.

    Args:
        gdf: The GeoDataFrame to serialise.
        path: Destination ``.geojson`` path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(path, driver="GeoJSON")


def _write_detections(points: list[Point], path: Path) -> None:
    """Write a detection GeoJSON of bare points (no ``source_tile``).

    The ``source_tile`` column is intentionally omitted so the scorer's
    spatial-join injection path is exercised, exactly as in production.

    Args:
        points: Detection point geometries (evaluation CRS).
        path: Destination ``.geojson`` path.
    """
    gdf = gpd.GeoDataFrame({"geometry": points}, crs=_CRS)
    _write_geojson(gdf, path)


@pytest.fixture
def synthetic_batch(tmp_path: Path) -> tuple[Path, Path]:
    """Build a 3-condition synthetic batch on disk.

    Each condition's detection set is slightly different so the resulting
    per-condition summaries genuinely differ — making the
    parallel-equals-serial assertion meaningful rather than vacuous:

    - ``cond-perfect``: detections on both mounds (two true positives).
    - ``cond-miss``: a detection on only one mound (one TP, one FN).
    - ``cond-fp``: detections on both mounds plus a spurious point in an
      empty tile (two TPs and one false positive).

    The bounds and ground truth are shared across all three conditions.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        A ``(config_path, output_dir)`` tuple. ``config_path`` is the
        batch YAML; ``output_dir`` does not yet exist (the batch run
        creates it).
    """
    bounds_path = tmp_path / "bounds.geojson"
    gt_path = tmp_path / "ground_truth.geojson"
    _write_geojson(_tile_grid(), bounds_path)
    _write_geojson(_ground_truth(), gt_path)

    # Per-condition detection points (matched within 20 m of the mounds).
    condition_points: dict[str, list[Point]] = {
        "cond-perfect": [Point(505.0, 505.0), Point(1495.0, 1495.0)],
        "cond-miss": [Point(505.0, 505.0)],
        "cond-fp": [
            Point(505.0, 505.0),
            Point(1495.0, 1495.0),
            Point(1500.0, 500.0),  # spurious detection in the empty (1,0) tile
        ],
    }

    conditions = []
    for label, points in condition_points.items():
        det_dir = tmp_path / "dets" / label
        # Convention-A pass filename. The earlier "detections_001.geojson"
        # was a shape no writer in this project emits: convention A is
        # detections_<config>_run<NN>.geojson and convention B is
        # detections-<config>-<model>-<date>.geojson (see
        # scripts/lib_detection_paths). A fixture inventing its own shape
        # tests the pipeline against an object that cannot exist, and it
        # broke when the resolver started matching the real conventions
        # strictly (Session 136 audit, defect D6).
        _write_detections(points, det_dir / "run_1" / f"detections_{label}_run01.geojson")
        conditions.append(
            {
                "label": label,
                "detections_dir": str(det_dir),
                "bounds": str(bounds_path),
                "buffers": [20, 30],
                "bootstrap": 100,
                "seed": 42,
            }
        )

    config = {
        "defaults": {"ground_truth": str(gt_path)},
        "metadata": {"description": "synthetic parallel-equals-serial fixture"},
        "conditions": conditions,
    }
    config_path = tmp_path / "batch.yaml"
    with open(config_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(config, handle)

    return config_path, tmp_path / "out"


def _run_batch(config_path: Path, output_dir: Path, workers: int, *, mcc: bool) -> int:
    """Invoke ``main()`` in batch mode with a given worker count.

    Drives the real CLI entry point (via ``sys.argv``) so the argument
    parser, default resolution, and dispatch are all exercised.

    Args:
        config_path: Path to the batch YAML.
        output_dir: Output directory for batch artefacts.
        workers: Value passed to ``--workers``.
        mcc: Whether to add ``--mcc`` (tile-level MCC).

    Returns:
        The process exit code returned by ``main()`` (0 on success).
    """
    argv = [
        "evaluate_detections.py",
        "--batch", str(config_path),
        "--output-dir", str(output_dir),
        "--workers", str(workers),
    ]
    if mcc:
        argv.append("--mcc")
    old_argv = sys.argv
    sys.argv = argv
    try:
        return main()
    finally:
        sys.argv = old_argv


def _load_summary_json(output_dir: Path) -> dict:
    """Read the written ``batch_summary.json`` from an output directory.

    Args:
        output_dir: The batch output directory.

    Returns:
        The parsed JSON document.
    """
    with open(output_dir / "batch_summary.json", encoding="utf-8") as handle:
        return json.load(handle)


def _parse_cli(argv: list[str]) -> object:
    """Parse a CLI invocation through the *production* argument parser.

    Drives ``main()`` only as far as ``parser.parse_args`` by patching
    ``argparse.ArgumentParser.parse_args`` to capture the namespace and
    short-circuit the rest of ``main`` with a sentinel exception. This keeps
    the test bound to the real parser definition (so it cannot drift from a
    hand-rolled copy) without running the full evaluation.

    Args:
        argv: Argument list excluding the program name.

    Returns:
        The parsed argparse namespace produced by the production parser.
    """
    import argparse

    captured: dict[str, object] = {}
    real_parse = argparse.ArgumentParser.parse_args

    class _Stop(Exception):
        pass

    def _capturing_parse(self, args=None, namespace=None):  # type: ignore[no-untyped-def]
        ns = real_parse(self, args=argv, namespace=namespace)
        captured["ns"] = ns
        raise _Stop

    old_argv = sys.argv
    sys.argv = ["evaluate_detections.py", *argv]
    argparse.ArgumentParser.parse_args = _capturing_parse  # type: ignore[assignment]
    try:
        try:
            main()
        except _Stop:
            pass
    finally:
        argparse.ArgumentParser.parse_args = real_parse  # type: ignore[assignment]
        sys.argv = old_argv
    return captured["ns"]


@pytest.mark.tier1
class TestWorkersArg:
    """The ``--workers`` CLI argument parses and defaults correctly."""

    def test_default_is_one(self) -> None:
        """Omitting ``--workers`` yields the integer default of 1."""
        ns = _parse_cli(["--batch", "x.yaml", "--output-dir", "out"])
        assert ns.workers == 1
        assert isinstance(ns.workers, int)

    def test_parses_int(self) -> None:
        """``--workers`` parses its value as an int."""
        ns = _parse_cli(
            ["--batch", "x.yaml", "--output-dir", "out", "--workers", "4"]
        )
        assert ns.workers == 4
        assert isinstance(ns.workers, int)


@pytest.mark.tier1
class TestParallelEqualsSerial:
    """Parallel batch evaluation must match the serial path byte for byte."""

    def test_summaries_equal(self, synthetic_batch: tuple[Path, Path]) -> None:
        """``--workers 1`` and ``--workers 2`` produce identical summaries.

        Runs the same synthetic 3-condition batch twice (serial and a
        2-process pool) into separate output directories, then asserts the
        written ``batch_summary.json`` ``rows`` are equal. Determinism of
        the per-condition seed plus the explicit reorder-by-index step in
        ``_run_batch_mode`` guarantee equality regardless of completion
        order.
        """
        config_path, base_out = synthetic_batch
        serial_out = base_out / "serial"
        parallel_out = base_out / "parallel"

        rc_serial = _run_batch(config_path, serial_out, workers=1, mcc=True)
        rc_parallel = _run_batch(config_path, parallel_out, workers=2, mcc=True)

        assert rc_serial == 0
        assert rc_parallel == 0

        serial_json = _load_summary_json(serial_out)
        parallel_json = _load_summary_json(parallel_out)

        # The metric rows (the load-bearing content) must be identical. The
        # top-level ``timestamp`` differs between runs by design, so compare
        # only the deterministic parts.
        assert serial_json["n_conditions"] == parallel_json["n_conditions"]
        assert serial_json["n_rows"] == parallel_json["n_rows"]
        assert serial_json["rows"] == parallel_json["rows"]

    def test_condition_order_preserved(
        self, synthetic_batch: tuple[Path, Path]
    ) -> None:
        """Per-condition row order is independent of worker count.

        The batch summary sorts rows by F1 internally, but the set of
        ``(label, buffer_metres)`` keys and their associated metrics must be
        identical between serial and parallel runs. This guards the
        reorder-by-index contract in ``_run_batch_mode``.
        """
        config_path, base_out = synthetic_batch
        serial_out = base_out / "serial"
        parallel_out = base_out / "parallel"

        _run_batch(config_path, serial_out, workers=1, mcc=False)
        _run_batch(config_path, parallel_out, workers=2, mcc=False)

        def _keyed(rows: list[dict]) -> dict[tuple[str, int], dict]:
            return {(r["label"], r["buffer_metres"]): r for r in rows}

        serial_rows = _keyed(_load_summary_json(serial_out)["rows"])
        parallel_rows = _keyed(_load_summary_json(parallel_out)["rows"])

        assert serial_rows.keys() == parallel_rows.keys()
        for key in serial_rows:
            assert serial_rows[key] == parallel_rows[key]

        # Sanity: the three conditions are present and genuinely differ, so
        # the equality assertions above are not vacuous.
        labels = {label for label, _ in serial_rows}
        assert labels == {"cond-perfect", "cond-miss", "cond-fp"}

    def test_auto_workers_matches_serial(
        self, synthetic_batch: tuple[Path, Path]
    ) -> None:
        """``--workers 0`` (auto) yields the same rows as the serial path."""
        config_path, base_out = synthetic_batch
        serial_out = base_out / "serial"
        auto_out = base_out / "auto"

        _run_batch(config_path, serial_out, workers=1, mcc=False)
        _run_batch(config_path, auto_out, workers=0, mcc=False)

        serial_rows = _load_summary_json(serial_out)["rows"]
        auto_rows = _load_summary_json(auto_out)["rows"]
        assert serial_rows == auto_rows


@pytest.mark.tier1
def test_batch_mode_smoke_parallel(synthetic_batch: tuple[Path, Path]) -> None:
    """A 2-condition-or-more parallel run writes the expected artefacts.

    Confirms ``_run_batch_mode`` actually drives the process pool and writes
    both the consolidated summary and the per-condition output directories.
    """
    config_path, base_out = synthetic_batch
    out = base_out / "smoke"

    rc = _run_batch(config_path, out, workers=2, mcc=False)
    assert rc == 0

    # Consolidated summary artefacts.
    assert (out / "batch_summary.json").exists()
    assert (out / "batch_summary.csv").exists()
    assert (out / "batch_summary.md").exists()

    # Per-condition output directories (slugified labels).
    for label in ("cond-perfect", "cond-miss", "cond-fp"):
        cond_dir = out / label
        assert cond_dir.is_dir(), f"missing per-condition dir for {label}"
        assert (cond_dir / "evaluation.json").exists()
