"""
Tests: seeded resampling does not depend on the string-hash seed (ruling D63).

CPython randomises ``str`` hashes per process unless ``PYTHONHASHSEED`` is
set, so a set of tile names iterates in a different order in every process.
Until D63 the paired bootstraps built their tile list from a set
(``list(tiles_a & tiles_b)``) and the seeded resampler indexed that list, so
the same ``random_seed`` gave a different interval in every process (Astra's
probe: a mean of -0.55 or -0.85 by hash seed, with identical TP/FP/FN).

Each test computes a function's result in two fresh interpreters under
different ``PYTHONHASHSEED`` values and requires byte-identical JSON. The
inputs are built from lists only, so they are the same in both processes;
on ``main`` before the fix every assertion here failed (red sentinel,
recorded in ``reports/s163-agent-records/bootstrap-hash-order.md``).

The synthetic tile names follow the tiling pipeline's
``<sheet>_x<N>_y<N>.png`` form so that the scorer attributes detections to
their sheet; other name forms are scoped out and leave every count at zero,
which would make the test pass vacuously.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.tier1

REPO_ROOT = Path(__file__).resolve().parent.parent

# Two hash seeds that order the synthetic tile set differently (checked on
# ``main`` before the fix: every case below differed between them).
HASH_SEEDS = ("1", "2")


def _synthetic() -> dict[str, Any]:
    """Fixed two-condition scoring problem on 2 sheets x 30 tiles.

    Built only by iterating lists, so it is identical under every hash seed.

    Returns:
        Dict with ``bounds`` (every tile), ``bounds_b`` (all but the last
        five tiles, in reversed order), ``ref``, ``det_a``, and ``det_b``.
    """
    import geopandas as gpd
    import numpy as np
    from shapely.geometry import Point, box

    rs = np.random.RandomState(7)
    crs = "EPSG:32635"
    tiles: list[dict[str, Any]] = []
    refs: list[dict[str, Any]] = []
    ref_xy: list[list[tuple[float, float]]] = []
    for m in range(2):
        sheet = f"K-35-{52 + m:03d}-4_32635"
        y0 = 4_700_000 + m * 10_000
        for i in range(30):
            x0 = 500_000 + i * 100
            tiles.append({"tile_name": f"{sheet}_x{i * 100}_y0.png",
                          "geometry": box(x0, y0, x0 + 100, y0 + 100)})
            pts = [(x0 + 25 + rs.uniform(0, 50), y0 + 25 + rs.uniform(0, 50))
                   for _ in range(rs.poisson(1.2))]
            ref_xy.append(pts)
            refs.extend({"geometry": Point(x, y), "Map": sheet,
                         "Symbol": "Burial Mound"} for x, y in pts)

    def detections(p_hit: float, fp_rate: float) -> gpd.GeoDataFrame:
        """One pass: each reference found with ``p_hit``; Poisson false alarms."""
        rows = []
        for tile, pts in zip(tiles, ref_xy):
            for x, y in pts:
                if rs.uniform() < p_hit:
                    dx, dy = rs.normal(0, 4, size=2)
                    rows.append({"source_tile": tile["tile_name"],
                                 "geometry": box(x + dx - 5, y + dy - 5,
                                                 x + dx + 5, y + dy + 5)})
            minx, miny, _, _ = tile["geometry"].bounds
            for _ in range(rs.poisson(fp_rate)):
                x, y = minx + 10 + rs.uniform(0, 80), miny + 10 + rs.uniform(0, 80)
                rows.append({"source_tile": tile["tile_name"],
                             "geometry": box(x - 5, y - 5, x + 5, y + 5)})
        return gpd.GeoDataFrame(rows, geometry="geometry", crs=crs)

    bounds = gpd.GeoDataFrame(tiles, crs=crs)
    return {
        "bounds": bounds,
        "bounds_b": bounds.iloc[: len(bounds) - 5].iloc[::-1].reset_index(drop=True),
        "ref": gpd.GeoDataFrame(refs, crs=crs),
        "det_a": detections(0.85, 0.35),
        "det_b": detections(0.70, 0.20),
    }


def _results() -> dict[str, Any]:
    """Run the three D63-fixed functions on the synthetic problem."""
    import warnings

    from scripts.lib_advanced_metrics import (
        bootstrap_effect_size_ci,
        bootstrap_interaction_ci,
        bootstrap_tile_effect_size_ci,
    )

    warnings.filterwarnings("ignore")
    s = _synthetic()
    pair = (s["det_a"], s["bounds"], s["det_b"], s["bounds_b"], s["ref"])
    conditions = {
        ("lo", "x"): (s["det_a"], s["bounds"]),
        ("lo", "y"): (s["det_b"], s["bounds_b"]),
        ("hi", "x"): (s["det_b"], s["bounds"]),
        ("hi", "y"): (s["det_a"], s["bounds_b"]),
    }
    return {
        "bootstrap_effect_size_ci": bootstrap_effect_size_ci(
            *pair, n_iterations=200, random_seed=42),
        "bootstrap_tile_effect_size_ci": bootstrap_tile_effect_size_ci(
            *pair, n_iterations=200, random_seed=42),
        "bootstrap_interaction_ci": bootstrap_interaction_ci(
            conditions, s["ref"], n_iterations=200, random_seed=42),
    }


def _emit() -> None:
    """Print the results as JSON (entry point for the child interpreters)."""
    sys.stdout.write(json.dumps(_results(), sort_keys=True, default=float))


@pytest.fixture(scope="module")
def per_seed_results() -> dict[str, dict[str, Any]]:
    """The results computed in one fresh interpreter per hash seed."""
    out: dict[str, dict[str, Any]] = {}
    for seed in HASH_SEEDS:
        proc = subprocess.run(
            [sys.executable, "-c",
             "import tests.test_hash_seed_determinism as t; t._emit()"],
            cwd=REPO_ROOT, env=dict(os.environ, PYTHONHASHSEED=seed),
            capture_output=True, text=True, check=False, timeout=600,
        )
        assert proc.returncode == 0, proc.stderr[-3000:]
        out[seed] = json.loads(proc.stdout)
    return out


@pytest.mark.parametrize("function", [
    "bootstrap_effect_size_ci",
    "bootstrap_tile_effect_size_ci",
    "bootstrap_interaction_ci",
])
def test_identical_across_hash_seeds(
    per_seed_results: dict[str, dict[str, Any]], function: str,
) -> None:
    """The same random_seed gives the same output under any hash seed."""
    first, second = (per_seed_results[s][function] for s in HASH_SEEDS)
    assert first == second, (
        f"{function} differs between PYTHONHASHSEED={HASH_SEEDS[0]} and "
        f"{HASH_SEEDS[1]}: its resampling order follows a set's hash order")


def test_synthetic_problem_is_not_degenerate(
    per_seed_results: dict[str, dict[str, Any]],
) -> None:
    """Guard against a vacuous pass: the intervals must have real width.

    If the scorer scoped every detection out (e.g. tile names it cannot
    attribute to a sheet), every count would be zero, every interval would
    be [0, 0], and the determinism tests above would pass whatever the
    resampling order.
    """
    res = per_seed_results[HASH_SEEDS[0]]
    f1 = res["bootstrap_effect_size_ci"]["f1_difference"]
    mcc = res["bootstrap_tile_effect_size_ci"]["mcc_difference"]
    dod = res["bootstrap_interaction_ci"]["interaction_contrasts"][0][
        "difference_of_differences"]
    for name, ci in (("f1", f1), ("mcc", mcc), ("interaction", dod)):
        assert ci["ci_upper"] - ci["ci_lower"] > 0.01, (name, ci)
