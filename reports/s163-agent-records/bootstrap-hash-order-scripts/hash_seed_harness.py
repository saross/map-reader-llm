#!/usr/bin/env python3
"""
Hash-seed harness for the resampling and permutation functions (ruling D63).

CPython randomises ``str`` hashes per process unless ``PYTHONHASHSEED`` is
set, so the iteration order of a set of tile names changes from process to
process. Where that order decides which tiles a seeded resampler draws, the
"seeded" result is not reproducible. This harness runs each candidate
function on FIXED synthetic inputs in fresh subprocesses under several
``PYTHONHASHSEED`` values and reports any case whose output is not byte
identical across them.

Usage (repository root on ``PYTHONPATH`` or as the working directory)::

    python reports/s163-agent-records/bootstrap-hash-order-scripts/hash_seed_harness.py
    python .../hash_seed_harness.py --seeds 0 1 2 3 --out record.json
    python .../hash_seed_harness.py --worker bootstrap_effect_size_ci

The driver mode prints one line per case (``VARIES`` or ``stable``) and,
with ``--out``, writes a JSON record of every case's per-seed SHA-256
digest. Worker mode prints the case's canonical JSON output on stdout.

The synthetic inputs are generated from a fixed ``numpy`` seed and built in
list order only, so they are identical under every hash seed; any variation
therefore comes from the function under test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Number of bootstrap iterations and permutations used by every case. Small
# enough to keep each worker under a few seconds, large enough that a
# different tile order changes the interval.
N_ITER = 300
N_PERM = 2000


# ---------------------------------------------------------------------------
# Fixed synthetic inputs
# ---------------------------------------------------------------------------

def _synthetic(seed: int = 7, n_maps: int = 2, tiles_per_map: int = 40) -> dict[str, Any]:
    """Build a fixed two-condition scoring problem.

    Every structure is built by iterating lists, never sets, so the inputs do
    not depend on the hash seed.

    Args:
        seed: ``numpy`` seed for the generator.
        n_maps: Number of map sheets.
        tiles_per_map: Tiles per sheet (100 m squares in one row).

    Returns:
        Dict with ``bounds`` (all tiles), ``bounds_b`` (a subset in reversed
        order, so the two conditions' tile sets differ), ``ref``, ``det_a``,
        ``det_b``, ``runs_a`` and ``runs_b`` (three passes each), and
        ``tiles`` (the bounds order).
    """
    import geopandas as gpd
    import numpy as np
    from shapely.geometry import Point, box

    rs = np.random.RandomState(seed)
    crs = "EPSG:32635"
    tile_rows: list[dict[str, Any]] = []
    ref_rows: list[dict[str, Any]] = []
    refs_by_tile: list[tuple[str, list[tuple[float, float]]]] = []
    for m in range(n_maps):
        sheet = f"K-35-{52 + m:03d}-4_32635"
        y0 = 4_700_000 + m * 10_000
        for i in range(tiles_per_map):
            # The tiling pipeline's name form, which ``get_map_name`` parses.
            name = f"{sheet}_x{i * 100}_y0.png"
            x0 = 500_000 + i * 100
            tile_rows.append({"tile_name": name, "geometry": box(x0, y0, x0 + 100, y0 + 100)})
            pts = []
            for _ in range(rs.poisson(1.2)):
                x = x0 + 25 + rs.uniform(0, 50)
                y = y0 + 25 + rs.uniform(0, 50)
                pts.append((x, y))
                ref_rows.append({"geometry": Point(x, y), "Map": sheet,
                                 "Symbol": "Burial Mound"})
            refs_by_tile.append((name, pts))
    bounds = gpd.GeoDataFrame(tile_rows, crs=crs)
    ref = gpd.GeoDataFrame(ref_rows, crs=crs)

    def detections(p_hit: float, fp_rate: float) -> gpd.GeoDataFrame:
        """One pass: each reference found with ``p_hit``; Poisson false alarms."""
        rows = []
        for (name, pts), tile in zip(refs_by_tile, tile_rows):
            for (x, y) in pts:
                if rs.uniform() < p_hit:
                    dx, dy = rs.normal(0, 4, size=2)
                    rows.append({"source_tile": name,
                                 "geometry": box(x + dx - 5, y + dy - 5, x + dx + 5, y + dy + 5)})
            minx, miny, _, _ = tile["geometry"].bounds
            for _ in range(rs.poisson(fp_rate)):
                x = minx + 10 + rs.uniform(0, 80)
                y = miny + 10 + rs.uniform(0, 80)
                rows.append({"source_tile": name,
                             "geometry": box(x - 5, y - 5, x + 5, y + 5)})
        gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs=crs)
        gdf["label"] = "mound"
        return gdf

    det_a = detections(0.85, 0.35)
    det_b = detections(0.70, 0.20)
    runs_a = [(r, detections(0.85, 0.35)) for r in (1, 2, 3)]
    runs_b = [(r, detections(0.70, 0.20)) for r in (1, 2, 3)]
    # Condition B covers every tile but the last five, in reversed order.
    bounds_b = bounds.iloc[: len(bounds) - 5].iloc[::-1].reset_index(drop=True)
    return {"bounds": bounds, "bounds_b": bounds_b, "ref": ref,
            "det_a": det_a, "det_b": det_b, "runs_a": runs_a, "runs_b": runs_b,
            "tiles": list(bounds["tile_name"])}


def _arrays(seed: int = 11, n: int = 80) -> dict[str, Any]:
    """Fixed per-tile count arrays for the array-level helpers."""
    import numpy as np

    rs = np.random.RandomState(seed)
    out = {}
    for arm in ("a", "b"):
        out[f"tp_{arm}"] = rs.poisson(1.0, n).astype(float)
        out[f"fp_{arm}"] = rs.poisson(0.6 if arm == "a" else 0.3, n).astype(float)
        out[f"fn_{arm}"] = rs.poisson(0.3 if arm == "a" else 0.6, n).astype(float)
    return out


# ---------------------------------------------------------------------------
# Cases: each returns a JSON-serialisable result
# ---------------------------------------------------------------------------

def case_bootstrap_ci() -> Any:
    """``lib_advanced_metrics.bootstrap_ci`` on condition A."""
    from scripts.lib_advanced_metrics import bootstrap_ci
    s = _synthetic()
    return bootstrap_ci(s["det_a"], s["ref"], s["bounds"], n_iterations=N_ITER, random_seed=42)


def case_bootstrap_effect_size_ci() -> Any:
    """``bootstrap_effect_size_ci`` (A on all tiles, B on a reversed subset)."""
    from scripts.lib_advanced_metrics import bootstrap_effect_size_ci
    s = _synthetic()
    return bootstrap_effect_size_ci(
        s["det_a"], s["bounds"], s["det_b"], s["bounds_b"], s["ref"],
        n_iterations=N_ITER, random_seed=42, return_p_values=True)


def case_bootstrap_multi_run_ci() -> Any:
    """``bootstrap_multi_run_ci`` on condition A's three passes."""
    from scripts.lib_advanced_metrics import bootstrap_multi_run_ci
    s = _synthetic()
    return bootstrap_multi_run_ci(s["runs_a"], s["ref"], s["bounds"],
                                  n_iterations=N_ITER, random_seed=42)


def case_bootstrap_multi_run_effect_size_ci() -> Any:
    """``bootstrap_multi_run_effect_size_ci`` with permutation p values."""
    from scripts.lib_advanced_metrics import bootstrap_multi_run_effect_size_ci
    s = _synthetic()
    return bootstrap_multi_run_effect_size_ci(
        s["runs_a"], s["runs_b"], s["ref"], s["bounds"],
        n_iterations=N_ITER, random_seed=42, return_p_values=True)


def case_bootstrap_interaction_ci() -> Any:
    """``bootstrap_interaction_ci`` over a 2 x 2 design with unequal tile sets."""
    from scripts.lib_advanced_metrics import bootstrap_interaction_ci
    s = _synthetic()
    conditions = {
        ("lo", "x"): (s["runs_a"][0][1], s["bounds"]),
        ("lo", "y"): (s["runs_b"][0][1], s["bounds_b"]),
        ("hi", "x"): (s["runs_a"][1][1], s["bounds"]),
        ("hi", "y"): (s["runs_b"][1][1], s["bounds_b"]),
    }
    return bootstrap_interaction_ci(conditions, s["ref"], n_iterations=N_ITER,
                                    random_seed=42)


def case_bootstrap_tile_classification_ci() -> Any:
    """``bootstrap_tile_classification_ci`` on condition A."""
    from scripts.lib_advanced_metrics import bootstrap_tile_classification_ci
    s = _synthetic()
    out = bootstrap_tile_classification_ci(s["det_a"], s["ref"], s["bounds"],
                                           n_iterations=N_ITER, random_seed=42)
    return out


def case_bootstrap_tile_effect_size_ci() -> Any:
    """``bootstrap_tile_effect_size_ci`` (A on all tiles, B on a reversed subset)."""
    from scripts.lib_advanced_metrics import bootstrap_tile_effect_size_ci
    s = _synthetic()
    return bootstrap_tile_effect_size_ci(
        s["det_a"], s["bounds"], s["det_b"], s["bounds_b"], s["ref"],
        n_iterations=N_ITER, random_seed=42)


def case_paired_permutation_test() -> Any:
    """``lib_permutation.paired_permutation_test`` on fixed arrays."""
    from scripts.lib_permutation import paired_permutation_test
    a = _arrays()
    return paired_permutation_test(
        {"tp": a["tp_a"], "fp": a["fp_a"], "fn": a["fn_a"]},
        {"tp": a["tp_b"], "fp": a["fp_b"], "fn": a["fn_b"]},
        n_permutations=N_PERM)


def case_e45_paired_bootstrap() -> Any:
    """``e45_bootstrap_pairings.paired_bootstrap`` on fixed arrays."""
    from scripts.e45_bootstrap_pairings import paired_bootstrap
    a = _arrays()
    return paired_bootstrap(a["tp_a"], a["fp_a"], a["fn_a"], a["tp_b"], a["fp_b"],
                            a["fn_b"], n_iterations=N_ITER, seed=42)


def case_n1_permutation_test_float() -> Any:
    """``n1_baseline_leaderboard_tiering.permutation_test_float`` on fixed arrays."""
    from scripts.n1_baseline_leaderboard_tiering import permutation_test_float
    a = _arrays()
    return permutation_test_float(a["tp_a"], a["fp_a"], a["fn_a"], a["tp_b"], a["fp_b"],
                                  a["fn_b"], n_permutations=N_PERM, seed=42)


def case_pairwise_run_permutation_test() -> Any:
    """``pairwise_permutation_test.run_permutation_test`` on the synthetic frames."""
    from scripts.pairwise_permutation_test import run_permutation_test
    s = _synthetic()
    return run_permutation_test(s["det_a"], s["det_b"], s["ref"], s["bounds"],
                                n_permutations=N_PERM, seed=42)


def case_selection_aware_run() -> Any:
    """``selection_aware_intervals.run`` on a fixed candidate-count cube."""
    import numpy as np

    from scripts.selection_aware_intervals import run
    a = _arrays()
    rs = np.random.RandomState(3)
    cands = []
    for _ in range(4):
        base = np.stack([a["tp_a"], a["fp_a"], a["fn_a"]], axis=1)
        cands.append(base + rs.poisson(0.3, base.shape))
    return run(np.stack(cands), b=N_ITER, m_frac=1.0, seed=42)


CASES: dict[str, Callable[[], Any]] = {
    name[len("case_"):]: fn for name, fn in sorted(globals().items())
    if name.startswith("case_") and callable(fn)
}


# ---------------------------------------------------------------------------
# Canonical output and the driver
# ---------------------------------------------------------------------------

def _canonical(obj: Any) -> Any:
    """Convert numpy scalars/arrays and sets to plain JSON types, exactly."""
    import numpy as np

    if isinstance(obj, dict):
        return {str(k): _canonical(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_canonical(v) for v in obj]
    if isinstance(obj, (set, frozenset)):
        return sorted(_canonical(v) for v in obj)
    if isinstance(obj, np.ndarray):
        return [_canonical(v) for v in obj.tolist()]
    if isinstance(obj, np.generic):
        return obj.item()
    if hasattr(obj, "to_dict"):
        return _canonical(obj.to_dict())
    return obj


def run_worker(case: str) -> None:
    """Run one case and print its canonical JSON (``repr`` floats: exact)."""
    import warnings
    warnings.filterwarnings("ignore")
    result = _canonical(CASES[case]())
    sys.stdout.write(json.dumps(result, sort_keys=True, default=str))


def run_driver(cases: list[str], seeds: list[int], out: Path | None) -> int:
    """Run every case under every hash seed; report cases that vary.

    Returns:
        Number of cases whose output varies across hash seeds.
    """
    record: dict[str, Any] = {"seeds": seeds, "cases": {}}
    n_varies = 0
    for case in cases:
        digests: dict[str, str] = {}
        samples: dict[str, str] = {}
        for seed in seeds:
            env = dict(os.environ, PYTHONHASHSEED=str(seed))
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--worker", case],
                env=env, capture_output=True, text=True, cwd=str(REPO_ROOT), check=False)
            if proc.returncode != 0:
                digests[str(seed)] = "ERROR"
                samples[str(seed)] = proc.stderr[-2000:]
                continue
            digests[str(seed)] = hashlib.sha256(proc.stdout.encode()).hexdigest()
            samples[str(seed)] = proc.stdout
        distinct = sorted(set(digests.values()))
        varies = len(distinct) > 1 or "ERROR" in distinct
        n_varies += int(varies)
        status = "ERROR" if "ERROR" in distinct else ("VARIES" if varies else "stable")
        print(f"{status:7s} {case:45s} distinct outputs: {len(distinct)}", flush=True)
        entry: dict[str, Any] = {"status": status, "digests": digests}
        if varies:
            entry["outputs"] = {s: (json.loads(v) if v and v[0] in "{[" else v)
                                for s, v in samples.items()}
        record["cases"][case] = entry
    if out is not None:
        out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    return n_varies


def main() -> int:
    """Parse arguments and run the worker or the driver."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--worker", help="run one case and print its JSON")
    parser.add_argument("--cases", nargs="*", help="cases to run (default: all)")
    parser.add_argument("--seeds", nargs="*", type=int, default=[0, 1, 2, 3])
    parser.add_argument("--out", type=Path, help="write the JSON record here")
    parser.add_argument("--list", action="store_true", help="list the cases")
    args = parser.parse_args()
    if args.list:
        print("\n".join(CASES))
        return 0
    if args.worker:
        run_worker(args.worker)
        return 0
    cases = args.cases or list(CASES)
    n = run_driver(cases, args.seeds, args.out)
    print(f"{n} of {len(cases)} cases vary across PYTHONHASHSEED {args.seeds}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
