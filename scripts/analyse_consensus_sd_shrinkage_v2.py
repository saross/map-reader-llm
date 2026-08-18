#!/usr/bin/env python3
"""
Consensus SD Shrinkage Analysis -- v2 genuine shared-mode test
================================================================

This is the v2 sibling of ``analyse_consensus_sd_shrinkage.py`` (v1).
It replaces the structurally-tautological ``mean of K i.i.d. F1s`` proxy
with a **genuine** test that rebuilds greedy-vote consensus on
K-subsamples drawn from per-pass detection geometries and re-evaluates
F1 against the canonical reference layer at 20 m.

Why v2 is needed
----------------

The v1 analysis estimated the SD of the K-consensus F1 by taking the
empirical SD of the mean of K i.i.d. samples drawn (with replacement)
from the K_max single-pass F1 list. Under the i.i.d. null,
``SD(mean of K samples) = sigma / sqrt(K)`` **by construction**, so the
log-log slope is forced toward -0.5 regardless of any shared-mode
signal in the underlying detection geometries. v1 thus served as a
sanity check on the i.i.d. expectation but could not test for
departures from i.i.d.

v2 tests for shared-mode signal **structurally**: it rebuilds the
actual greedy-vote consensus from per-pass detection GeoJSONs on
random K-subsamples, materialises the resulting candidate set at a
canonical vote threshold, and recomputes the point F1 against the
reference. The SD across subsamples then reflects the true variability
of the K-consensus estimator, including any correlated per-pass error
modes (shared "hard" map sheets, shared confusable features, etc.).

Methodology
-----------

For each (track, thinking, T) stratum with K_max >= 4:

1. Discover ``run_*`` directories under the canonical stratum root and
   load each run's detection features (deduplicated within-pass at
   20 m via ``deduplicate_within_pass``).
2. For each K' in ``{1, 2, ..., K_max}``:
   a. Generate R subsamples of K' passes from the K_max pool. If
      ``C(K_max, K') <= 200`` use exhaustive enumeration; otherwise
      randomly sample 200 distinct subsets (seed = 42 + stratum hash).
   b. For each subsample:
      - Build greedy-vote consensus via
        ``cluster_across_passes`` at 20 m (UTM-32635).
      - Apply ``vote_t = max(1, round(K' * 0.5))`` -- uniform majority
        rule across all K' for cross-K comparability.
      - Materialise consensus survivors as a GeoDataFrame and evaluate
        F1 at 20 m vs the canonical reference layer using
        ``calculate_f1_internal``.
   c. Record per-subsample point F1; compute the SD and mean across
      subsamples at this K'.
3. Fit ``log(SD_F1) ~ beta_0 + beta_1 * log(K')`` per stratum.
4. Bootstrap CI on ``beta_1`` (1000 iterations): for each iteration,
   resample subsamples within each K' with replacement, recompute SD
   per K', and refit the slope.
5. Flag a stratum as exhibiting shared-mode signal if its 95% CI on
   ``beta_1`` excludes -0.5 in either direction (i.e., genuinely
   slower-than-i.i.d. would be ``beta_1 > -0.3`` and is the headline
   test; faster-than-i.i.d. ``beta_1 < -0.7`` would be surprising and
   is also flagged).

Voting rule rationale
~~~~~~~~~~~~~~~~~~~~~

A uniform majority rule (``round(K * 0.5)``) is used across all K'
for cross-K comparability. The per-condition F1-optimal thresholds
in the published Phase 3a tables (e.g. 26-of-30 for HIGH-T0.7 text)
are valid only at the full K_max -- applying them naively at smaller
K' would conflate threshold mis-calibration with consensus shrinkage.
The majority rule is invariant under K' rescaling and gives a clean
SD-shrinkage curve.

Outputs
-------

- ``results/secondary-effects-consensus-sd/sd_shrinkage_v2.json``
- ``results/secondary-effects-consensus-sd/sd_shrinkage_v2.png``
- ``results/secondary-effects-consensus-sd/report.md`` (updated in
  place to add a new Section 3 "Genuine shared-mode test (v2)"; v1
  Sections 1-2 are preserved with a methodology note).

Usage
-----

    python scripts/analyse_consensus_sd_shrinkage_v2.py \\
        --output-dir results/secondary-effects-consensus-sd/ \\
        --max-workers 4

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-27
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # headless backend for sapphire / CI
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# These imports are colocated below the sys.path mutation so the
# script-local lib_consensus / evaluate_detections modules resolve
# correctly when running as a top-level script. The noqa comments
# silence ruff's E402 (module-level import not at top of file).
from lib_consensus import (  # noqa: E402
    cluster_across_passes,
    deduplicate_within_pass,
)
from lib_detection_paths import find_pass_geojsons  # noqa: E402

__version__ = "1.0.0"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_GT = (
    PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
)
BOUNDS_487 = PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

DEFAULT_RADIUS_M = 20.0
DEFAULT_BUFFER_M = 20  # F1 evaluation buffer
MAX_SUBSAMPLES_PER_K = 200
RANDOM_SEED = 42

# Theoretical i.i.d. log-log slope reference
IID_SLOPE = -0.5
# Shared-mode flag: slopes shallower than this are flagged
SHARED_MODE_FLAG = -0.3


# ---------------------------------------------------------------------------
# Stratum / condition registry
#
# Limited to the 13 v1-fitted strata (K_max >= 4 so that the slope can
# be estimated across multiple K'). T=0.0 cells (K_max = 3) are
# excluded -- they support only K' in {1, 2, 3} which is too few for a
# robust slope fit and was the same exclusion used by v1.
# ---------------------------------------------------------------------------

STRATA: list[dict[str, Any]] = [
    # ----- text-track Phase 3a matrix -----
    {
        "label": "text_HIGH_T0.3",
        "track": "text", "thinking": "HIGH", "T": 0.3,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    {
        "label": "text_HIGH_T0.7",
        "track": "text", "thinking": "HIGH", "T": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
        "K_max": 30, "bounds": BOUNDS_487,
    },
    {
        "label": "text_HIGH_T1.0",
        "track": "text", "thinking": "HIGH", "T": 1.0,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    {
        "label": "text_MINIMAL_T0.3",
        "track": "text", "thinking": "MINIMAL", "T": 0.3,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    {
        "label": "text_MINIMAL_T0.7",
        "track": "text", "thinking": "MINIMAL", "T": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
        "K_max": 30, "bounds": BOUNDS_487,
    },
    {
        "label": "text_MINIMAL_T1.0",
        "track": "text", "thinking": "MINIMAL", "T": 1.0,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    # ----- image-track Phase 3a matrix -----
    {
        "label": "image_HIGH_T0.3",
        "track": "image", "thinking": "HIGH", "T": 0.3,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    {
        "label": "image_HIGH_T0.7",
        "track": "image", "thinking": "HIGH", "T": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    {
        "label": "image_HIGH_T1.0",
        "track": "image", "thinking": "HIGH", "T": 1.0,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    {
        "label": "image_MINIMAL_T0.3",
        "track": "image", "thinking": "MINIMAL", "T": 0.3,
        "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t0.3",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    {
        "label": "image_MINIMAL_T0.7",
        "track": "image", "thinking": "MINIMAL", "T": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t0.7",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    {
        "label": "image_MINIMAL_T1.0",
        "track": "image", "thinking": "MINIMAL", "T": 1.0,
        "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t1.0",
        "K_max": 10, "bounds": BOUNDS_487,
    },
    # ----- SCALE4-T0.7 (image, K_max = 10) -----
    {
        "label": "image_SCALE4_T0.7",
        "track": "image", "thinking": "SCALE4", "T": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/scale-4-optimal-487",
        "K_max": 10, "bounds": BOUNDS_487,
    },
]


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------


def load_run_features(run_dir: Path) -> list[dict]:
    """Load all detection GeoJSON features from a run directory.

    Mirrors :mod:`analyse_inter_pass_agreement`: resolution is delegated to
    ``lib_detection_paths.find_pass_geojsons``, which covers the h11
    ``detections-<config>-...geojson`` and retest
    ``detections_T<x>_run<NN>.geojson`` layouts alike and skips ``.meta`` /
    ``.tiles`` side-files. The tolerant local glob this function carried was
    a workaround for the convention-A-only loader in ``lib_consensus``, which
    now uses the same resolver; the workaround is obsolete.

    Args:
        run_dir: Path to a run directory.

    Returns:
        List of GeoJSON feature dicts (possibly empty).
    """
    features: list[dict] = []
    for gj in find_pass_geojsons(run_dir):
        try:
            with open(gj, encoding="utf-8") as fh:
                data = json.load(fh)
            features.extend(data.get("features", []))
        except json.JSONDecodeError as exc:
            logger.warning("Could not parse %s: %s", gj, exc)
    return features


def discover_run_dirs(run_root: Path) -> list[Path]:
    """List ``run_*`` subdirectories sorted by numeric run id.

    Args:
        run_root: Directory containing ``run_<N>`` subdirectories.

    Returns:
        Sorted list of run directory paths (run_2 before run_10).
    """
    if not run_root.exists():
        return []
    runs: list[tuple[int, Path]] = []
    for p in run_root.glob("run_*"):
        if not p.is_dir():
            continue
        m = re.match(r"run_(\d+)$", p.name)
        if m:
            runs.append((int(m.group(1)), p))
    runs.sort(key=lambda pair: pair[0])
    return [p for _, p in runs]


# ---------------------------------------------------------------------------
# Subsample generation
# ---------------------------------------------------------------------------


def generate_subsamples(
    pass_ids: list[str],
    k_used: int,
    max_subsamples: int = MAX_SUBSAMPLES_PER_K,
    seed: int = RANDOM_SEED,
) -> list[tuple[str, ...]]:
    """Produce up to ``max_subsamples`` distinct K'-subsets of pass_ids.

    If ``C(K_max, K') <= max_subsamples`` returns the exhaustive
    enumeration (sorted); otherwise returns a deterministically random
    sample without replacement.

    Args:
        pass_ids: ordered list of K_max pass identifiers.
        k_used: subset size K' (1 <= K' <= K_max).
        max_subsamples: cap on the number of subsamples returned.
        seed: random seed for the non-exhaustive branch.

    Returns:
        List of tuples; each tuple is a K'-subset of pass_ids.
    """
    k_max = len(pass_ids)
    if k_used < 1 or k_used > k_max:
        raise ValueError(f"k_used={k_used} out of range for K_max={k_max}")

    n_combos = comb(k_max, k_used)
    if n_combos <= max_subsamples:
        return list(combinations(pass_ids, k_used))

    # Random sample without replacement. Use a Python-level deterministic
    # RNG so the same (k_max, k_used, seed) produces the same draw
    # regardless of platform numpy version.
    rng = random.Random(seed)
    picked: set[tuple[str, ...]] = set()
    # Iterate until we have max_subsamples distinct subsets
    while len(picked) < max_subsamples:
        sample = tuple(sorted(rng.sample(pass_ids, k_used)))
        picked.add(sample)
    return sorted(picked)


# ---------------------------------------------------------------------------
# Per-subsample consensus + evaluation
# ---------------------------------------------------------------------------


def consensus_f1_for_subsample(
    pass_dedup: dict[str, list[dict]],
    subsample: tuple[str, ...],
    k_used: int,
    gdf_ref,  # geopandas.GeoDataFrame
    gdf_bounds,  # geopandas.GeoDataFrame
    radius_m: float = DEFAULT_RADIUS_M,
    buffer_m: int = DEFAULT_BUFFER_M,
) -> float:
    """Build greedy-vote consensus on a K' subsample and return point F1.

    Args:
        pass_dedup: mapping ``pass_id -> deduplicated detection list``
            (per-pass dedup at ``radius_m`` already applied).
        subsample: tuple of K' pass_ids drawn from pass_dedup.
        k_used: subsample size K'.
        gdf_ref: GeoDataFrame of reference mounds (in canonical UTM CRS).
        gdf_bounds: GeoDataFrame of evaluation bounds (UTM CRS).
        radius_m: clustering radius in metres (canonical 20).
        buffer_m: F1 matching buffer in metres (canonical 20).

    Returns:
        Point F1 of the K'-pass greedy-vote consensus at vote_t =
        ``max(1, round(K' * 0.5))``.
    """
    # Local imports inside the worker -- geopandas/shapely don't
    # serialise cleanly across ProcessPoolExecutor boundaries.
    import geopandas as gpd
    from shapely.geometry import Point as ShapelyPoint

    from lib_advanced_metrics import calculate_f1_internal

    # Build the K' subset of pass_detections
    pass_subset = {pid: pass_dedup[pid] for pid in subsample}
    clusters = cluster_across_passes(pass_subset, distance_thresh=radius_m)
    if not clusters:
        return 0.0

    # Uniform majority rule: vote_t = max(1, round(K' / 2))
    vote_t = max(1, int(round(k_used * 0.5)))
    survivors = [c for c in clusters if c["vote_count"] >= vote_t]
    if not survivors:
        return 0.0

    # Materialise as GeoDataFrame in canonical UTM CRS
    rows = []
    for c in survivors:
        source_tile = (
            c["source_tiles"][0] if c["source_tiles"] else "unknown"
        )
        rows.append({
            "geometry": ShapelyPoint(c["centroid"]),
            "source_tile": source_tile,
            "subtype": c["label"],
        })
    gdf_det = gpd.GeoDataFrame(rows, crs="EPSG:32635")

    _, _, f1 = calculate_f1_internal(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_m,
    )
    return float(f1)


# ---------------------------------------------------------------------------
# Per-stratum worker
# ---------------------------------------------------------------------------


def _process_stratum(
    args: tuple,
) -> tuple[str, dict[str, Any]]:
    """Worker entrypoint for ProcessPoolExecutor.

    Loads everything fresh (geopandas + shapely + sklearn import poorly
    across worker boundaries).

    Args:
        args: 5-tuple ``(stratum, gt_path, max_subsamples, radius_m,
            buffer_m)``.

    Returns:
        Tuple of (stratum_label, payload_dict).
    """
    stratum, gt_path, max_subsamples, radius_m, buffer_m = args

    # Fresh imports inside the worker
    import sys as _sys
    _sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from evaluate_detections import load_geojson as _lg

    gt_gdf = _lg(gt_path)
    bounds_gdf = _lg(stratum["bounds"])
    run_root = PROJECT_ROOT / stratum["run_dir"]
    run_dirs = discover_run_dirs(run_root)
    if not run_dirs:
        return stratum["label"], {
            "error": f"No run_* dirs under {run_root}",
            "K_declared": stratum["K_max"], "K_found": 0,
        }

    # Build per-pass dedup once -- this is the slow part
    pass_dedup: dict[str, list[dict]] = {}
    for run_dir in run_dirs:
        feats = load_run_features(run_dir)
        if feats:
            pass_dedup[run_dir.name] = deduplicate_within_pass(
                feats, distance_thresh=radius_m,
            )
        else:
            pass_dedup[run_dir.name] = []
    pass_ids = list(pass_dedup.keys())
    k_max = len(pass_ids)

    # Stratum hash for deterministic-but-distinct random seeds
    stratum_seed = (RANDOM_SEED + abs(hash(stratum["label"]))) % (2**31)

    per_k: list[dict[str, Any]] = []
    per_subsample_f1s: dict[int, list[float]] = {}

    # Iterate K' from 1..K_max
    for k_used in range(1, k_max + 1):
        subsamples = generate_subsamples(
            pass_ids, k_used,
            max_subsamples=max_subsamples,
            seed=stratum_seed + k_used,  # distinct draw per K'
        )
        f1s: list[float] = []
        vote_t = max(1, int(round(k_used * 0.5)))
        for ss in subsamples:
            f1 = consensus_f1_for_subsample(
                pass_dedup, ss, k_used,
                gt_gdf, bounds_gdf,
                radius_m=radius_m, buffer_m=buffer_m,
            )
            f1s.append(f1)

        f1_arr = np.array(f1s, dtype=float)
        # Guard SD against degenerate cases (all subsamples identical)
        if len(f1_arr) >= 2:
            sd = float(np.std(f1_arr, ddof=1))
        else:
            sd = 0.0
        per_k.append({
            "K_used": k_used,
            "vote_t": vote_t,
            "n_subsamples": len(f1_arr),
            "exhaustive": comb(k_max, k_used) <= max_subsamples,
            "mean_f1": float(np.mean(f1_arr)) if len(f1_arr) > 0 else 0.0,
            "sd_f1": sd,
            "min_f1": float(np.min(f1_arr)) if len(f1_arr) > 0 else 0.0,
            "max_f1": float(np.max(f1_arr)) if len(f1_arr) > 0 else 0.0,
        })
        per_subsample_f1s[k_used] = f1s

    return stratum["label"], {
        "K_declared": stratum["K_max"],
        "K_found": k_max,
        "track": stratum["track"],
        "thinking": stratum["thinking"],
        "T": stratum["T"],
        "run_dir": str(stratum["run_dir"]),
        "per_k": per_k,
        "per_subsample_f1s": per_subsample_f1s,
    }


# ---------------------------------------------------------------------------
# Slope fit + bootstrap CI
# ---------------------------------------------------------------------------


def _fit_loglog_slope(
    k_values: np.ndarray, sd_values: np.ndarray,
) -> tuple[float, float]:
    """Fit ``log(SD) ~ beta_0 + beta_1 * log(K)``. Returns (intercept, slope)."""
    log_k = np.log(k_values)
    log_sd = np.log(sd_values)
    slope, intercept = np.polyfit(log_k, log_sd, deg=1)
    return float(intercept), float(slope)


def fit_slope_with_ci(
    per_k: list[dict[str, Any]],
    per_subsample_f1s: dict[int, list[float]],
    n_bootstrap: int = 1000,
    seed: int = RANDOM_SEED,
) -> dict[str, Any]:
    """Fit per-stratum log-log slope and bootstrap CI.

    Bootstrap procedure: for each iteration, **resample within each K'
    bin with replacement** (preserves the empirical per-K SD
    distribution), recompute SD per K', and refit the slope. This
    differs from v1's approach (which resampled the underlying per-pass
    F1 pool) because v2's per-subsample F1s are not exchangeable across
    K' (they reflect different subsets of the same pool).

    Args:
        per_k: list of per-K' summary dicts (from ``_process_stratum``).
        per_subsample_f1s: mapping K' -> list of per-subsample F1s.
        n_bootstrap: number of bootstrap iterations.
        seed: random seed.

    Returns:
        Dict with ``beta_1``, ``beta_1_ci_lower``, ``beta_1_ci_upper``,
        ``n_k_levels``, plus convenience flags.
    """
    # Filter degenerate SDs (zero SD breaks log)
    rows = [r for r in per_k if r["sd_f1"] > 0]
    if len(rows) < 3:
        return {
            "beta_1": float("nan"),
            "beta_1_ci_lower": float("nan"),
            "beta_1_ci_upper": float("nan"),
            "n_k_levels": len(rows),
            "ci_excludes_iid": False,
            "shared_mode_flagged": False,
            "anti_shared_mode_flagged": False,
            "skip_reason": (
                f"Only {len(rows)} K-levels with SD > 0; need >= 3"
            ),
        }

    k_arr = np.array([r["K_used"] for r in rows], dtype=float)
    sd_arr = np.array([r["sd_f1"] for r in rows], dtype=float)
    _, beta_1 = _fit_loglog_slope(k_arr, sd_arr)

    # Bootstrap CI: resample within each K' bin
    rng = np.random.default_rng(seed)
    slopes: list[float] = []
    for _ in range(n_bootstrap):
        sds: list[float] = []
        for r in rows:
            k = r["K_used"]
            f1s = per_subsample_f1s.get(k, [])
            if len(f1s) < 2:
                sds.append(r["sd_f1"])
                continue
            arr = np.array(f1s, dtype=float)
            resample = rng.choice(arr, size=len(arr), replace=True)
            sd_b = float(np.std(resample, ddof=1))
            sds.append(sd_b if sd_b > 0 else r["sd_f1"])
        sds_arr = np.array(sds, dtype=float)
        if np.any(sds_arr <= 0):
            continue
        try:
            _, slope = _fit_loglog_slope(k_arr, sds_arr)
            slopes.append(slope)
        except (ValueError, RuntimeWarning):
            continue

    if slopes:
        ci_lo = float(np.percentile(slopes, 2.5))
        ci_hi = float(np.percentile(slopes, 97.5))
    else:
        ci_lo = ci_hi = float("nan")

    # Decision flags
    ci_excludes_iid = (
        not np.isnan(ci_lo) and not np.isnan(ci_hi)
        and (ci_hi < IID_SLOPE or ci_lo > IID_SLOPE)
    )
    shared_mode_flagged = bool(beta_1 > SHARED_MODE_FLAG)
    anti_shared_mode_flagged = bool(beta_1 < -0.7)

    return {
        "beta_1": beta_1,
        "beta_1_ci_lower": ci_lo,
        "beta_1_ci_upper": ci_hi,
        "n_k_levels": len(rows),
        "n_bootstrap": n_bootstrap,
        "ci_excludes_iid": bool(ci_excludes_iid),
        "shared_mode_flagged": shared_mode_flagged,
        "anti_shared_mode_flagged": anti_shared_mode_flagged,
    }


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def write_json(
    payloads: dict[str, dict[str, Any]],
    output_path: Path,
) -> None:
    """Write the full v2 numeric output to JSON.

    Strips the per-subsample F1 lists (large) into a separate compressed
    section keyed by stratum -- they are useful for re-analysis but
    bloat the headline file.
    """
    payload = {
        "metadata": {
            "version": __version__,
            "generated": datetime.now(tz=timezone.utc).isoformat(),
            "max_subsamples_per_k": MAX_SUBSAMPLES_PER_K,
            "random_seed": RANDOM_SEED,
            "iid_theoretical_slope": IID_SLOPE,
            "shared_mode_flag_threshold": SHARED_MODE_FLAG,
            "default_radius_m": DEFAULT_RADIUS_M,
            "default_buffer_m": DEFAULT_BUFFER_M,
            "voting_rule": "vote_t = max(1, round(K * 0.5))",
            "method_note": (
                "Genuine shared-mode test: greedy-vote consensus rebuilt "
                "on K-subsamples of per-pass detection geometries; F1 "
                "evaluated against canonical reference at 20 m."
            ),
        },
        "strata": payloads,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=_json_default)
    logger.info("JSON written: %s", output_path)


def _json_default(obj: Any) -> Any:
    """JSON encoder for numpy / Path objects."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        if np.isnan(obj):
            return None
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Not serialisable: {type(obj)}")


def write_plot(
    payloads: dict[str, dict[str, Any]],
    output_path: Path,
) -> None:
    """Write the v2 log-log SD vs K plot, faceted by track.

    Mirrors v1's layout but adds a clear "v2 GENUINE" subtitle and a
    secondary -0.5 reference annotated as "i.i.d. null".
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True)
    cmap = plt.get_cmap("viridis")
    # Build colour map from the union of T values
    temps = sorted({p["T"] for p in payloads.values() if "T" in p})
    color_map = {
        t: cmap(i / max(1, len(temps) - 1)) for i, t in enumerate(temps)
    }
    line_styles = {"HIGH": "-", "MINIMAL": "--", "SCALE4": ":"}

    for ax, track in zip(axes, ["text", "image"]):
        # Anchor for the i.i.d. reference line: max K=1 SD across this track
        anchor_sd = 0.0
        any_data = False
        for label, p in payloads.items():
            if p.get("track") != track or "per_k" not in p:
                continue
            any_data = True
            per_k = p["per_k"]
            ks = np.array([r["K_used"] for r in per_k])
            sds = np.array([r["sd_f1"] for r in per_k])
            # Skip zero SDs in the plot (log scale) but keep marker
            mask = sds > 0
            if not mask.any():
                continue
            anchor_sd = max(anchor_sd, sds[mask][0] if mask[0] else 0.0)
            ax.plot(
                ks[mask], sds[mask],
                marker="o",
                linestyle=line_styles.get(p["thinking"], "-"),
                color=color_map.get(p["T"], "k"),
                label=f"{p['thinking']} T{p['T']:.1f}",
                alpha=0.85,
            )
        if any_data and anchor_sd > 0:
            ks_ref = np.array(
                sorted({r["K_used"]
                        for p in payloads.values()
                        if p.get("track") == track and "per_k" in p
                        for r in p["per_k"]})
            )
            ref = anchor_sd * (ks_ref / 1.0) ** -0.5
            ax.plot(
                ks_ref, ref, "k--", alpha=0.5,
                label="i.i.d. null (-0.5)",
            )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("K' (subsample size)")
        ax.set_ylabel("SD of K'-consensus F1 (across subsamples)")
        ax.set_title(f"{track.capitalize()} track")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=7, loc="best", ncol=2)

    fig.suptitle(
        "v2 GENUINE: K-consensus F1 SD shrinkage on rebuilt subsamples "
        "(log-log)",
        fontsize=12,
    )
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Plot written: %s", output_path)


def update_report(
    payloads: dict[str, dict[str, Any]],
    slopes: dict[str, dict[str, Any]],
    report_path: Path,
) -> None:
    """Update report.md in place with a new Section 3 for v2 results.

    Strategy:
        - Read existing v1 content.
        - Insert a methodology note at the top of Section 2 (the v1
          per-stratum table) flagging the proxy limitation.
        - Append a new Section 3 "Genuine shared-mode test (v2)"
          containing the v2 prose, table, and plot reference.
        - Preserve v1 Sections 1 and 2 verbatim except for the
          methodology-note insertion.

    Args:
        payloads: per-stratum v2 payloads (per_k, etc.).
        slopes: per-stratum v2 slope-fit dicts.
        report_path: target ``report.md`` path.
    """
    # Load v1 content (or write a stub if absent)
    if report_path.exists():
        old = report_path.read_text(encoding="utf-8")
    else:
        old = "# Consensus SD Shrinkage Analysis (Phase 3a Text + Image)\n\n"

    # Inject v1 methodology note. Conservative anchor: prepend a note
    # paragraph just below the level-2 heading "Per-stratum log-log
    # slope and SD shrinkage" if present.
    v1_note = (
        "\n> **v1 methodology note** (added 2026-04-27 alongside v2): "
        "the per-K SD values in this section are computed under the "
        "**mean-of-K-i.i.d.-passes proxy**, which by construction "
        "yields ``SD = sigma / sqrt(K)`` and a log-log slope of -0.5 "
        "regardless of any shared-mode signal in the underlying "
        "detection geometries. The slopes reported below are therefore "
        "best read as a **sanity check on the i.i.d. expectation**, "
        "not as an independent test of departure from i.i.d. See "
        "Section 3 for the v2 genuine test based on rebuilt greedy-"
        "vote consensus.\n"
    )
    anchor = "## Per-stratum log-log slope and SD shrinkage"
    if anchor in old and v1_note.strip() not in old:
        idx = old.index(anchor)
        # Place note just after the heading line + its trailing newline
        end_of_line = old.index("\n", idx) + 1
        old = old[:end_of_line] + v1_note + old[end_of_line:]

    # Build Section 3
    lines: list[str] = []
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Genuine shared-mode test (v2)")
    lines.append("")
    lines.append(
        f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}"
    )
    lines.append("**Script**: ``scripts/analyse_consensus_sd_shrinkage_v2.py``")
    lines.append(
        f"**Method**: greedy-vote consensus rebuilt on K-subsamples of "
        f"per-pass detection GeoJSONs; F1 re-evaluated at 20 m vs "
        f"``{DEFAULT_GT.relative_to(PROJECT_ROOT)}``. Voting rule = "
        f"``vote_t = max(1, round(K' * 0.5))``."
    )
    lines.append(
        f"**Subsample budget**: exhaustive ``C(K_max, K')`` if "
        f"≤{MAX_SUBSAMPLES_PER_K}, otherwise random {MAX_SUBSAMPLES_PER_K} "
        f"distinct subsets (seed = {RANDOM_SEED} + per-stratum offset)."
    )
    lines.append(
        "**Bootstrap CI on beta_1**: 1000 iterations resampling "
        "within-K' subsample F1 lists with replacement."
    )
    lines.append("")

    # Methodology rationale
    lines.append("### Why v2 is needed")
    lines.append("")
    lines.append(
        "Section 2 above used a **mean-of-K-i.i.d.-F1s proxy** for the "
        "K-consensus F1 estimator. Under any i.i.d. null this proxy "
        "yields ``SD = sigma / sqrt(K)`` and a log-log slope of -0.5 "
        "**by construction** -- the proxy is therefore mathematically "
        "incapable of detecting shared-mode departures from i.i.d. "
        "v2 fixes this by rebuilding the actual greedy-vote consensus "
        "on K-subsamples drawn from per-pass detection geometries and "
        "re-evaluating F1 against the canonical reference. Departures "
        "from -0.5 in v2 reflect genuine correlated per-pass error "
        "modes (shared 'hard' map sheets, shared confusable features, "
        "etc.)."
    )
    lines.append("")

    # Headline table
    lines.append("### Per-stratum slopes (v2)")
    lines.append("")
    lines.append(
        "| Stratum | K_max | n@K=1 | n@K=K_max | "
        "SD@K=1 | SD@K=K_max | beta_1 [95% CI] | "
        "Decision |"
    )
    lines.append(
        "|---------|------:|------:|---------:|"
        "------:|-----------:|:----------------:|:---------|"
    )
    for label in sorted(payloads.keys()):
        p = payloads[label]
        s = slopes.get(label, {})
        if "error" in p:
            lines.append(
                f"| {label} | — | — | — | — | — | "
                f"_error: {p['error']}_ | — |"
            )
            continue
        per_k = p["per_k"]
        k_max = p["K_found"]
        sd_k1 = next(
            (r["sd_f1"] for r in per_k if r["K_used"] == 1), None,
        )
        sd_kmax = next(
            (r["sd_f1"] for r in per_k if r["K_used"] == k_max), None,
        )
        n_k1 = next(
            (r["n_subsamples"] for r in per_k if r["K_used"] == 1), 0,
        )
        n_kmax = next(
            (r["n_subsamples"] for r in per_k if r["K_used"] == k_max), 0,
        )
        if "skip_reason" in s:
            beta_str = f"_{s['skip_reason']}_"
            decision = "—"
        else:
            beta_str = (
                f"{s.get('beta_1', float('nan')):+.2f} "
                f"[{s.get('beta_1_ci_lower', float('nan')):+.2f}, "
                f"{s.get('beta_1_ci_upper', float('nan')):+.2f}]"
            )
            if s.get("shared_mode_flagged"):
                decision = "**shared-mode**"
            elif s.get("anti_shared_mode_flagged"):
                decision = "**anti-i.i.d.**"
            elif s.get("ci_excludes_iid"):
                decision = "CI excludes -0.5"
            else:
                decision = "i.i.d. consistent"
        sd_k1_str = f"{sd_k1:.4f}" if sd_k1 is not None else "—"
        sd_km_str = f"{sd_kmax:.4f}" if sd_kmax is not None else "—"
        lines.append(
            f"| {label} | {k_max} | {n_k1} | {n_kmax} | "
            f"{sd_k1_str} | {sd_km_str} | {beta_str} | {decision} |"
        )
    lines.append("")

    # Plot reference
    lines.append("### Plot")
    lines.append("")
    lines.append(
        "![v2 SD shrinkage](sd_shrinkage_v2.png)"
    )
    lines.append("")
    lines.append(
        "*Solid = HIGH thinking, dashed = MINIMAL thinking, dotted = "
        "SCALE4. Black dashed = i.i.d. reference (-0.5).*"
    )
    lines.append("")

    # Headline prose
    lines.append("### Summary")
    lines.append("")
    lines.append(_compose_v2_prose(payloads, slopes))
    lines.append("")

    # File manifest
    lines.append("### v2 output files")
    lines.append("")
    lines.append(
        "- ``sd_shrinkage_v2.json`` -- full numeric results including "
        "per-subsample F1 lists."
    )
    lines.append("- ``sd_shrinkage_v2.png`` -- log-log plot.")
    lines.append("- ``report.md`` -- this file (Section 3 added).")
    lines.append("")
    lines.append(f"*Section 3 added: {datetime.now(tz=timezone.utc).isoformat()}*")
    lines.append("")

    new_content = old.rstrip() + "\n\n" + "\n".join(lines) + "\n"
    report_path.write_text(new_content, encoding="utf-8")
    logger.info("Report updated: %s", report_path)


def _compose_v2_prose(
    payloads: dict[str, dict[str, Any]],
    slopes: dict[str, dict[str, Any]],
) -> str:
    """Compose the paper-ready paragraph summarising the v2 result."""
    fitted = [
        (label, slopes[label])
        for label in slopes
        if "skip_reason" not in slopes[label]
        and not np.isnan(slopes[label].get("beta_1", float("nan")))
    ]
    if not fitted:
        return (
            "No v2 strata produced a fittable log-log slope (likely "
            "because per-K subsamples produced degenerate zero SDs)."
        )

    text_betas = [s["beta_1"] for label, s in fitted if "text" in label]
    image_betas = [s["beta_1"] for label, s in fitted if "image" in label]
    text_mean = (
        float(np.mean(text_betas)) if text_betas else float("nan")
    )
    image_mean = (
        float(np.mean(image_betas)) if image_betas else float("nan")
    )

    flagged_shared = [
        label for label, s in fitted if s.get("shared_mode_flagged")
    ]
    flagged_anti = [
        label for label, s in fitted if s.get("anti_shared_mode_flagged")
    ]
    flagged_excl = [
        label for label, s in fitted
        if s.get("ci_excludes_iid")
        and not s.get("shared_mode_flagged")
        and not s.get("anti_shared_mode_flagged")
    ]

    parts: list[str] = []
    parts.append(
        f"Across {len(fitted)} strata, the v2 K-consensus F1 SD "
        f"shrinks with K' at a mean log-log slope of "
        f"{text_mean:+.2f} for the text track and "
        f"{image_mean:+.2f} for the image track, against the i.i.d. "
        f"theoretical reference of -0.5."
    )
    if not flagged_shared and not flagged_anti and not flagged_excl:
        parts.append(
            "All strata's 95% bootstrap CIs on beta_1 contain -0.5, "
            "providing **no evidence** for shared-mode signal in the "
            "consensus-vote estimator: K-pass consensus shrinks "
            "uncertainty at the i.i.d. ``sqrt(K)`` rate even when the "
            "consensus is rebuilt structurally on detection geometries. "
            "This is a **publishable null result** -- it rules out the "
            "concern that correlated per-pass error modes might be "
            "limiting consensus headroom in this study, and validates "
            "the use of effective sample size N/K' for power "
            "calculations on consensus-derived metrics."
        )
    else:
        if flagged_shared:
            parts.append(
                f"Strata with **shared-mode signal** "
                f"(beta_1 > {SHARED_MODE_FLAG}): "
                f"{', '.join(flagged_shared)}. These reflect correlated "
                f"per-pass error modes that limit the consensus shrinkage."
            )
        if flagged_anti:
            parts.append(
                f"Strata with **faster-than-i.i.d. shrinkage** "
                f"(beta_1 < -0.7): {', '.join(flagged_anti)}. "
                f"This is unexpected and worth investigating -- a "
                f"plausible cause is sub-K_max pool stratification "
                f"(e.g. specific runs being systematically more "
                f"diverse)."
            )
        if flagged_excl:
            parts.append(
                f"Strata with CIs that exclude -0.5 but stay within "
                f"the (-0.7, -0.3) band: {', '.join(flagged_excl)}. "
                f"These are weak departures and worth flagging but do "
                f"not warrant the full shared-mode interpretation."
            )
        parts.append(
            "Strata not listed above have CIs containing -0.5 and are "
            "consistent with the i.i.d. null."
        )

    return " ".join(parts)


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------


def main() -> int:
    """Run the v2 genuine shared-mode SD-shrinkage analysis."""
    parser = argparse.ArgumentParser(
        description=(
            "v2 genuine shared-mode test for consensus F1 SD shrinkage. "
            "Replaces v1's mean-of-K-passes proxy with rebuilt greedy-"
            "vote consensus on K-subsamples."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results" / "secondary-effects-consensus-sd",
        help="Directory for sd_shrinkage_v2.json/png and updated report.md.",
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=DEFAULT_GT,
        help="GeoJSON of GT mounds (default: mounds-reference.geojson).",
    )
    parser.add_argument(
        "--max-workers", type=int, default=4,
        help="ProcessPoolExecutor worker count (default 4).",
    )
    parser.add_argument(
        "--max-subsamples", type=int, default=MAX_SUBSAMPLES_PER_K,
        help=(
            f"Cap on subsamples per K' (default {MAX_SUBSAMPLES_PER_K}); "
            "below this cap exhaustive enumeration is used."
        ),
    )
    parser.add_argument(
        "--radius", type=float, default=DEFAULT_RADIUS_M,
        help="Cluster radius (m) -- canonical 20.",
    )
    parser.add_argument(
        "--buffer", type=int, default=DEFAULT_BUFFER_M,
        help="F1 matching buffer (m) -- canonical 20.",
    )
    parser.add_argument(
        "--strata", nargs="*", default=None,
        help="Optional subset of stratum labels to process.",
    )
    parser.add_argument(
        "--n-bootstrap", type=int, default=1000,
        help="Bootstrap iterations for slope CI (default 1000).",
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
    logger.info(
        "analyse_consensus_sd_shrinkage_v2.py v%s -- %d workers, "
        "max_subsamples=%d",
        __version__, args.max_workers, args.max_subsamples,
    )
    start = time.monotonic()

    # Filter strata
    strata = (
        [s for s in STRATA if s["label"] in args.strata]
        if args.strata else STRATA
    )
    logger.info("Submitting %d stratum tasks", len(strata))

    # Build task list
    tasks = [
        (
            s, args.ground_truth, args.max_subsamples,
            args.radius, args.buffer,
        )
        for s in strata
    ]

    payloads: dict[str, dict[str, Any]] = {}
    with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(_process_stratum, t): t[0]["label"]
            for t in tasks
        }
        for fut in as_completed(futures):
            label = futures[fut]
            try:
                _, payload = fut.result()
                payloads[label] = payload
                if "error" in payload:
                    logger.error(
                        "  %s -- error: %s", label, payload["error"],
                    )
                else:
                    per_k = payload["per_k"]
                    sd_k1 = next(
                        (r["sd_f1"] for r in per_k if r["K_used"] == 1),
                        None,
                    )
                    sd_kmax = next(
                        (r["sd_f1"] for r in per_k
                         if r["K_used"] == payload["K_found"]),
                        None,
                    )
                    logger.info(
                        "  %s -- K=%d, SD@K=1=%.4f SD@K=K_max=%.4f",
                        label, payload["K_found"],
                        sd_k1 or 0.0, sd_kmax or 0.0,
                    )
            except Exception as exc:
                logger.exception(
                    "  %s -- unhandled exception: %s", label, exc,
                )
                payloads[label] = {"error": str(exc)}

    # Fit slopes per stratum (sequential, fast -- numpy polyfit)
    slopes: dict[str, dict[str, Any]] = {}
    for label, payload in payloads.items():
        if "error" in payload:
            slopes[label] = {"skip_reason": "error during stratum"}
            continue
        slopes[label] = fit_slope_with_ci(
            payload["per_k"],
            payload["per_subsample_f1s"],
            n_bootstrap=args.n_bootstrap,
        )

    # Stamp slope-fits into payloads for the JSON output
    for label, fit in slopes.items():
        if label in payloads and "error" not in payloads[label]:
            payloads[label]["slope_fit"] = fit

    # Write outputs
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(payloads, out_dir / "sd_shrinkage_v2.json")
    write_plot(payloads, out_dir / "sd_shrinkage_v2.png")
    update_report(payloads, slopes, out_dir / "report.md")

    # Console summary
    logger.info("Per-stratum v2 slopes:")
    for label in sorted(slopes.keys()):
        s = slopes[label]
        if "skip_reason" in s:
            logger.info("  %s -- skip: %s", label, s["skip_reason"])
            continue
        flag = ""
        if s.get("shared_mode_flagged"):
            flag = " *SHARED-MODE"
        elif s.get("anti_shared_mode_flagged"):
            flag = " *ANTI-IID"
        elif s.get("ci_excludes_iid"):
            flag = " *CI-excl-iid"
        logger.info(
            "  %s: beta_1 = %+.3f [%+.3f, %+.3f]%s",
            label,
            s.get("beta_1", float("nan")),
            s.get("beta_1_ci_lower", float("nan")),
            s.get("beta_1_ci_upper", float("nan")),
            flag,
        )

    elapsed = time.monotonic() - start
    logger.info("Complete in %.1f s (%.1f min)", elapsed, elapsed / 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
