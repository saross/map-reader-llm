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

The same ruling replaced two seeds derived from the built-in ``hash()`` of
strings (``analyse_consensus_sd_shrinkage.py`` and its v2), which are salted
per process in the same way; those are tested here too, with their file and
consensus steps stubbed so that only the seeded draws are exercised.

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

# Two hash seeds that order the synthetic tile set differently and give
# different hash-derived seeds (checked on ``main`` before the fix: every
# case below differed between them).
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


def _sd_v1_result() -> Any:
    """``compute_sd_per_cell_per_k`` (SD shrinkage v1) on fixed per-pass F1s."""
    import numpy as np
    import pandas as pd

    from scripts.analyse_consensus_sd_shrinkage import compute_sd_per_cell_per_k

    rs = np.random.RandomState(5)
    rows = []
    for track, k_max in (("text", 10), ("image", 5)):
        for thinking in ("HIGH", "MINIMAL"):
            for temperature in (0.0, 0.7):
                rows.extend({"track": track, "thinking": thinking, "T": temperature,
                             "K_max": k_max, "f1": float(rs.uniform(0.5, 0.8))}
                            for _ in range(k_max))
    out = compute_sd_per_cell_per_k(pd.DataFrame(rows))
    return out.to_dict(orient="records")


def _sd_v2_result() -> Any:
    """``_process_stratum`` (SD shrinkage v2) with its I/O and scoring stubbed.

    Eight passes and at most five subsamples per K', so K' = 2 to 6 are drawn
    at random from the stratum's seed; the stubbed F1 of a subsample is a
    fixed function of which passes it holds, so the output records the draw.
    """
    import scripts.analyse_consensus_sd_shrinkage_v2 as v2
    import evaluate_detections  # resolvable: v2 puts scripts/ on sys.path

    evaluate_detections.load_geojson = lambda _path: None
    v2.discover_run_dirs = lambda _root: [Path(f"run_{i}") for i in range(1, 9)]
    v2.load_run_features = lambda run_dir: [{"pass": run_dir.name}]
    v2.deduplicate_within_pass = lambda feats, distance_thresh: feats
    v2.consensus_f1_for_subsample = (
        lambda _dedup, subsample, k_used, *_args, **_kwargs:
        sum(int(name.split("_")[1]) ** 2 for name in subsample) / (64.0 * k_used))
    stratum = {"label": "text_HIGH_T0.7", "bounds": "unused", "run_dir": "unused",
               "K_max": 8, "track": "text", "thinking": "HIGH", "T": 0.7}
    return v2._process_stratum((stratum, "unused", 5, 20.0, 20))


def _results() -> dict[str, Any]:
    """Run every D63-fixed function on its fixed synthetic input."""
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
        "sd_shrinkage_v1": _sd_v1_result(),
        "sd_shrinkage_v2": _sd_v2_result(),
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
    "sd_shrinkage_v1",
    "sd_shrinkage_v2",
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
    # The v2 stub must leave room for a random draw: some K' not exhaustive.
    assert any(not row["exhaustive"] for row in res["sd_shrinkage_v2"][1]["per_k"])
    f1 = res["bootstrap_effect_size_ci"]["f1_difference"]
    mcc = res["bootstrap_tile_effect_size_ci"]["mcc_difference"]
    dod = res["bootstrap_interaction_ci"]["interaction_contrasts"][0][
        "difference_of_differences"]
    for name, ci in (("f1", f1), ("mcc", mcc), ("interaction", dod)):
        assert ci["ci_upper"] - ci["ci_lower"] > 0.01, (name, ci)
