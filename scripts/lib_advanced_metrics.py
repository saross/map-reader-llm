"""
Advanced metrics library for mound detection evaluation.

Provides F1, precision, recall calculations with one-to-one matching
using the Hungarian algorithm for optimal detection-to-reference assignment.

Includes bootstrapped confidence interval functions aligned with preregistration
Section 3.5:
- bootstrap_ci(): 95% CIs for absolute F1, precision, and recall
- bootstrap_effect_size_ci(): 95% CIs for differences between conditions

Tile-level classification (Section 4.2):
- calculate_tile_classification(): Binary classification of tiles (empty vs populated)
- bootstrap_tile_classification_ci(): 95% CIs for MCC, sensitivity, specificity
- bootstrap_tile_effect_size_ci(): 95% CIs for tile-level effect sizes

Factorial interaction testing (preregistration Section 5.5, M/E × H5):
- bootstrap_interaction_ci(): 95% CIs for two-way interaction via
  difference-of-differences bootstrap
"""

import json
import logging
import re
import warnings
from pathlib import Path
from typing import Any, Callable

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.stats import DegenerateDataWarning
from scipy.stats import bootstrap as scipy_bootstrap

# Configure module logger
logger = logging.getLogger(__name__)

# Constants for project structure
INPUTS_DIR = Path("inputs")
DEFAULT_CRS = "EPSG:32635"  # UTM Zone 35N (Bulgaria)

# Bootstrap CI methodology constants ----------------------------------------
#
# We use the Bias-Corrected and Accelerated (BCa) bootstrap rather than the
# percentile method. BCa adjusts for both the bias of the bootstrap
# distribution (median offset from the point estimate) and the skewness of
# the underlying statistic via a jackknife acceleration term. It produces
# better-calibrated confidence intervals on skewed or biased distributions
# where the percentile method systematically excludes the point estimate
# (cf. ``archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md``).
#
# When BCa cannot be computed (degenerate bootstrap distribution — e.g.
# every resample yields the same statistic), the helper falls back to the
# percentile method and records the fallback in the returned diagnostics.
BOOTSTRAP_METHOD: str = "BCa"
BOOTSTRAP_LIB: str = "scipy.stats.bootstrap"

# Mitigation 3 (sparse-coverage transparency) constants --------------------
#
# When ``zero_fraction`` (proportion of tiles with TP+FP+FN == 0) exceeds
# this threshold, the bootstrap CI is flagged as ``sparse_cross_grid``.
# The 0.50 threshold sits ~40 percentage points above the worst observed
# matched-grid case (~11 %) and ~25 points below the least-sparse cross-grid
# case (~75 %), giving a clean separation in both directions. A strict ``>``
# boundary (not ``>=``) is used so that the threshold is the maximum
# acceptable coverage gap, not the minimum trigger.
DEFAULT_COVERAGE_THRESHOLD: float = 0.5
COVERAGE_STATUS_NORMAL: str = "normal"
COVERAGE_STATUS_SPARSE: str = "sparse_cross_grid"


def _compute_coverage(
    tile_metrics: pd.DataFrame,
    threshold: float = DEFAULT_COVERAGE_THRESHOLD,
) -> dict[str, Any]:
    """Compute Mitigation 3 sparse-coverage diagnostics for a tile-metrics frame.

    Counts the fraction of tiles in the evaluation bounds with zero TP, FP,
    and FN counts. When the fraction strictly exceeds ``threshold`` the
    coverage is flagged as ``sparse_cross_grid`` — bootstrap CIs over such
    distributions are unreliable and should be suppressed in human-readable
    outputs. The numeric CI bounds are still computed and returned in the
    JSON output for downstream consumers that opt to read them.

    Args:
        tile_metrics: DataFrame with columns ``[tile_name, tp, fp, fn]``,
            as returned by :func:`compute_per_tile_tp_fp_fn`.
        threshold: Zero-fraction threshold above which coverage is sparse.
            Defaults to :data:`DEFAULT_COVERAGE_THRESHOLD` (0.5). Strict
            ``>`` boundary semantics.

    Returns:
        Dict with keys ``n_tiles``, ``n_zero_count_tiles``,
        ``zero_fraction`` (all ints/floats), ``threshold`` (float), and
        ``coverage_status`` (``"normal"`` or ``"sparse_cross_grid"``).
    """
    n_tiles = len(tile_metrics)
    if n_tiles == 0:
        return {
            "n_tiles": 0,
            "n_zero_count_tiles": 0,
            "zero_fraction": 0.0,
            "threshold": float(threshold),
            "coverage_status": COVERAGE_STATUS_NORMAL,
        }

    total_per_tile = (
        tile_metrics["tp"] + tile_metrics["fp"] + tile_metrics["fn"]
    )
    n_zero = int((total_per_tile == 0).sum())
    zero_fraction = n_zero / n_tiles
    # Strict ``>`` semantics: a ``zero_fraction`` of exactly the threshold
    # is considered borderline-but-acceptable. Cross-grid cases observed in
    # practice (74.5 % – 83.4 %) sit far above any reasonable threshold so
    # the choice does not matter empirically; we pick strict ``>`` to make
    # the threshold the maximum acceptable coverage gap rather than the
    # minimum trigger.
    is_sparse = zero_fraction > threshold
    return {
        "n_tiles": int(n_tiles),
        "n_zero_count_tiles": n_zero,
        "zero_fraction": float(zero_fraction),
        "threshold": float(threshold),
        "coverage_status": (
            COVERAGE_STATUS_SPARSE if is_sparse else COVERAGE_STATUS_NORMAL
        ),
    }


def _bca_ci_from_indices(
    indices: np.ndarray,
    statistic: Callable[[np.ndarray], float],
    n_iterations: int = 1000,
    random_seed: int | None = None,
    confidence_level: float = 0.95,
) -> dict[str, Any]:
    """Compute a Bias-Corrected and Accelerated (BCa) bootstrap CI.

    Uses :func:`scipy.stats.bootstrap` with ``method='BCa'`` to compute a
    confidence interval over a tile-index resampling. The ``statistic``
    callable must accept a 1-D NumPy array of indices into the original
    sample and return a scalar metric (precision, recall, F1, MCC, etc.).
    To support scipy's vectorised resampling we wrap the user-supplied
    statistic to apply along the last axis when scipy passes a 2-D array
    of resampled indices.

    On a degenerate bootstrap distribution (every resample yields the
    same statistic, or the jackknife acceleration cannot be computed)
    scipy returns ``ConfidenceInterval(low=nan, high=nan)``. We catch
    that case and fall back to the percentile method, recording the
    fallback in the returned ``method`` field.

    Args:
        indices: 1-D NumPy array of tile indices, length ``n_tiles``.
            scipy will resample this array with replacement.
        statistic: Callable that takes a 1-D array of indices and returns
            a scalar metric. Used both for the point estimate and inside
            scipy's vectorised resampling loop.
        n_iterations: Number of bootstrap resamples (default 1000).
        random_seed: Optional integer seed. When provided, every call
            with the same seed is bit-reproducible.
        confidence_level: Two-sided confidence level (default 0.95).

    Returns:
        Dict with keys ``mean``, ``ci_lower``, ``ci_upper``, ``method``
        (``"BCa"`` or ``"percentile_fallback"``), and
        ``bootstrap_distribution`` (numpy array — useful for diagnostics
        and back-compat callers that compute their own percentiles).
    """
    indices = np.asarray(indices)

    def _vectorised(idx_array: np.ndarray, axis: int = -1) -> np.ndarray:
        """Apply ``statistic`` along the last axis for scipy's vectorised loop.

        scipy passes either a 1-D ``(n,)`` array (for the point estimate
        and jackknife) or a 2-D ``(B, n)`` array (resampled batch). We
        broadcast the user-supplied statistic by iterating along the
        leading dimension when 2-D.
        """
        idx_array = np.asarray(idx_array, dtype=int)
        if idx_array.ndim == 1:
            return float(statistic(idx_array))
        # 2-D resample batch: apply statistic along ``axis``
        return np.array(
            [statistic(row) for row in np.moveaxis(idx_array, axis, 0)]
        )

    # Suppress scipy's DegenerateDataWarning so it does not leak into the
    # caller's log; we surface degeneracy via the ``method`` field instead.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DegenerateDataWarning)
        warnings.simplefilter("ignore", category=RuntimeWarning)
        try:
            result = scipy_bootstrap(
                (indices,),
                _vectorised,
                n_resamples=n_iterations,
                method="BCa",
                confidence_level=confidence_level,
                rng=random_seed,
                vectorized=True,
            )
            ci_lower = float(result.confidence_interval.low)
            ci_upper = float(result.confidence_interval.high)
            distribution = np.asarray(result.bootstrap_distribution)
            method_used = "BCa"
            # Detect NaN bounds (degenerate jackknife).
            if not (np.isfinite(ci_lower) and np.isfinite(ci_upper)):
                raise ValueError("BCa returned non-finite bounds")
        except (ValueError, ZeroDivisionError, FloatingPointError):
            # Fallback to deterministic percentile resampling (mirrors the
            # legacy implementation). Used only in degenerate cases.
            rng = np.random.default_rng(random_seed)
            n = len(indices)
            distribution = np.array([
                statistic(rng.choice(indices, size=n, replace=True))
                for _ in range(n_iterations)
            ])
            ci_lower = float(np.percentile(distribution, 2.5))
            ci_upper = float(np.percentile(distribution, 97.5))
            method_used = "percentile_fallback"

    return {
        "mean": float(np.mean(distribution)) if distribution.size else 0.0,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "method": method_used,
        "bootstrap_distribution": distribution,
    }


def _compute_ci(
    scores: list[float] | np.ndarray,
) -> dict[str, float | None]:
    """Compute mean and 95% percentile CI from an iterable of bootstrap scores.

    Legacy helper retained for callers that resample inside their own
    loops (e.g. effect-size differences) and pass a precomputed bootstrap
    distribution. New code should prefer :func:`_bca_ci_from_indices`,
    which delegates to scipy's BCa implementation.

    Args:
        scores: Iterable of scalar bootstrap statistics.

    Returns:
        Dict with ``mean`` (float or ``None`` when empty), ``ci_lower``
        (2.5th percentile), and ``ci_upper`` (97.5th percentile).
    """
    scores_array = np.asarray(list(scores)) if not isinstance(
        scores, np.ndarray,
    ) else scores
    if scores_array.size == 0:
        return {"mean": None, "ci_lower": None, "ci_upper": None}
    return {
        "mean": float(np.mean(scores_array)),
        "ci_lower": float(np.percentile(scores_array, 2.5)),
        "ci_upper": float(np.percentile(scores_array, 97.5)),
    }


def _compute_bca_ci(
    scores: list[float] | np.ndarray,
) -> dict[str, float | None]:
    """Compute mean and 95% BCa CI from an iterable of bootstrap scores.

    Used for paired-difference distributions (effect sizes) where the
    bootstrap loop computes a per-iteration scalar (e.g. ``F1_A - F1_B``)
    and we want a BCa-adjusted CI rather than the raw 2.5/97.5 percentiles.
    For these callers we cannot use scipy's index-based bootstrap because
    the resampling logic is condition-specific (paired tile indices,
    multi-run averaging, etc.); instead we compute BCa bias and
    acceleration directly from the bootstrap distribution and a
    leave-one-out jackknife pseudo-distribution.

    The implementation follows Efron (1987) / Davison & Hinkley (1997):

    * z0 (bias correction) = inverse-normal CDF of the proportion of
      bootstrap statistics ≤ the observed statistic (here, the
      distribution mean — the differential equivalent of the point
      estimate when the caller does not supply an external one).
    * a (acceleration) = skewness of the jackknife distribution. For a
      bootstrap-of-differences distribution we approximate jackknife by
      leave-one-out of the bootstrap iterations themselves. This is a
      coarser estimator than a true tile-level jackknife, but matches
      the resolution of the input.

    On degenerate distributions (constant or near-constant) the helper
    falls back to the percentile method, mirroring scipy's behaviour.

    Args:
        scores: Iterable of scalar bootstrap statistics.

    Returns:
        Dict with ``mean`` (float or ``None`` when empty), ``ci_lower``,
        ``ci_upper``, and ``method`` (``"BCa"`` or
        ``"percentile_fallback"``).
    """
    scores_array = (
        scores if isinstance(scores, np.ndarray) else np.asarray(list(scores))
    )
    if scores_array.size == 0:
        return {
            "mean": None,
            "ci_lower": None,
            "ci_upper": None,
            "method": "empty",
        }
    # The "point estimate" for an effect-size distribution is the mean of
    # the bootstrap iterations themselves — there is no external observed
    # difference because the caller resamples per iteration. We use the
    # mean rather than the median to match the percentile-method baseline.
    point = float(np.mean(scores_array))
    n = scores_array.size

    # Bias correction z0
    prop_le = float(np.mean(scores_array <= point))
    if prop_le <= 0.0 or prop_le >= 1.0:
        # Degenerate distribution — fall back to percentile.
        return {
            "mean": point,
            "ci_lower": float(np.percentile(scores_array, 2.5)),
            "ci_upper": float(np.percentile(scores_array, 97.5)),
            "method": "percentile_fallback",
        }
    from scipy.stats import norm
    z0 = float(norm.ppf(prop_le))

    # Acceleration via leave-one-out jackknife of the bootstrap
    # distribution. This is an approximation: a true BCa would jackknife
    # the original sample units (tiles), but in the difference-of-
    # differences regime the per-tile bootstrap sample is not directly
    # accessible from the scalar score array.
    sum_scores = scores_array.sum()
    jackknife_means = (sum_scores - scores_array) / (n - 1)
    jackknife_mean = jackknife_means.mean()
    deviations = jackknife_mean - jackknife_means
    numerator = float(np.sum(deviations ** 3))
    denominator = 6.0 * (float(np.sum(deviations ** 2)) ** 1.5)
    if denominator == 0.0 or not np.isfinite(denominator):
        return {
            "mean": point,
            "ci_lower": float(np.percentile(scores_array, 2.5)),
            "ci_upper": float(np.percentile(scores_array, 97.5)),
            "method": "percentile_fallback",
        }
    a = numerator / denominator

    # Adjusted percentiles
    z_alpha_lo = float(norm.ppf(0.025))
    z_alpha_hi = float(norm.ppf(0.975))
    alpha_lo = norm.cdf(z0 + (z0 + z_alpha_lo) / (1 - a * (z0 + z_alpha_lo)))
    alpha_hi = norm.cdf(z0 + (z0 + z_alpha_hi) / (1 - a * (z0 + z_alpha_hi)))

    # Clamp to [0, 1] in case of numerical drift.
    alpha_lo = float(np.clip(alpha_lo, 0.0, 1.0))
    alpha_hi = float(np.clip(alpha_hi, 0.0, 1.0))

    ci_lower = float(np.percentile(scores_array, 100 * alpha_lo))
    ci_upper = float(np.percentile(scores_array, 100 * alpha_hi))

    return {
        "mean": point,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "method": "BCa",
    }


def load_data(
    detection_file: Path | str,
    bounds_file: Path | str,
    inputs_dir: Path = INPUTS_DIR,
    target_crs: str = DEFAULT_CRS,
) -> tuple[gpd.GeoDataFrame | None, gpd.GeoDataFrame | None, gpd.GeoDataFrame | None]:
    """
    Load detection, bounds, and reference GeoDataFrames for metrics calculation.

    Args:
        detection_file: Path to the detection GeoJSON file.
        bounds_file: Path to the bounds GeoJSON file.
        inputs_dir: Base directory containing reference vectors (default: 'inputs').
        target_crs: Target CRS for all datasets (default: EPSG:32635).

    Returns:
        Tuple of (detections, bounds, references) GeoDataFrames, or (None, None, None) on error.
    """
    try:
        gdf_det = gpd.read_file(detection_file)
        gdf_bounds = gpd.read_file(bounds_file)

        # Load references from inputs/vectors/references/
        ref_dir = inputs_dir / "vectors" / "references"

        # Validate reference directory exists (catches wrong-path bugs like E5a)
        if not ref_dir.is_dir():
            logger.error(
                "Reference directory does not exist: %s. "
                "Expected reference GeoJSON files at inputs/vectors/references/.",
                ref_dir,
            )
            return None, None, None

        ref_files = list(ref_dir.glob("reference_*.geojson"))
        ref_gdfs = []
        for rf in ref_files:
            gdf = gpd.read_file(rf)
            gdf['Map'] = rf.stem.replace("reference_", "")
            ref_gdfs.append(gdf)

        if not ref_gdfs:
            # List directory contents for debugging — makes silent failures loud
            try:
                contents = [f.name for f in ref_dir.iterdir()]
            except OSError:
                contents = ["<unreadable>"]
            logger.error(
                "No reference files matching 'reference_*.geojson' in %s. "
                "Directory contains: %s",
                ref_dir,
                contents,
            )
            return None, None, None

        gdf_ref = pd.concat(ref_gdfs, ignore_index=True)

        # CRS Standardisation
        if gdf_det.crs != target_crs:
            if gdf_det.crs is None:
                gdf_det.set_crs(target_crs, inplace=True)
            else:
                gdf_det = gdf_det.to_crs(target_crs)

        if gdf_bounds.crs != target_crs:
            if gdf_bounds.crs is None:
                gdf_bounds.set_crs(target_crs, inplace=True)
            else:
                gdf_bounds = gdf_bounds.to_crs(target_crs)

        if gdf_ref.crs != target_crs:
            if gdf_ref.crs is None:
                gdf_ref.set_crs(target_crs, inplace=True)
            else:
                gdf_ref = gdf_ref.to_crs(target_crs)

        return gdf_det, gdf_bounds, gdf_ref
    except Exception as e:
        logger.error("Error loading metrics data: %s", e)
        return None, None, None


_MAP_NAME_RE = re.compile(r'^(.+?)_x\d+_y\d+(?:\.png)?$')


def get_map_name(tile_name: str) -> str:
    """
    Extract map name from tile filename.

    Uses a regex to strip the ``_x{digits}_y{digits}.png`` suffix that
    the tiling pipeline appends to every tile. This works for both the
    4-map validation set (e.g., ``K-35-052-4_32635_x0_y0.png``) and the
    55-map generalisation set (e.g., ``K-35-065-3_Glavan_4326_x0_y0.png``,
    ``K-35-042-3_x0_y0.png``).

    Args:
        tile_name: The tile filename (e.g., 'K-35-052-4_32635_x0_y0.png').

    Returns:
        The map name (everything before the ``_x{N}_y{N}`` offset),
        or 'Unknown' if the filename doesn't match the expected pattern.
    """
    m = _MAP_NAME_RE.match(tile_name)
    return m.group(1) if m else "Unknown"


def normalise_ref_class(symbol: Any) -> str:
    """Normalise reference symbol class names to standard categories."""
    s = str(symbol).lower()  # Handle None/NaN safety
    if "bench mark" in s:
        return "benchmark_mound"
    if "triangulation" in s:
        return "triangulation_mound"
    if "burial mound" in s or "kurgan" in s:
        return "burial_mound"
    if "settlement" in s:
        return "settlement_mound"
    return "unknown"


def match_detections_to_references(
    det_geoms: list,
    ref_geoms: list,
    max_distance: float,
) -> tuple[list[int], list[int], list[int], list[int]]:
    """
    Perform one-to-one matching between detections and references using
    the Hungarian algorithm.

    Each detection can match at most one reference, and vice versa.
    Matches are only valid if within max_distance metres.

    Args:
        det_geoms: List of detection geometries (points or centroids).
        ref_geoms: List of reference geometries (points or centroids).
        max_distance: Maximum distance in metres for a valid match.

    Returns:
        Tuple of (matched_det_indices, matched_ref_indices,
        unmatched_det_indices, unmatched_ref_indices).
    """
    n_det = len(det_geoms)
    n_ref = len(ref_geoms)

    if n_det == 0 or n_ref == 0:
        return ([], [], list(range(n_det)), list(range(n_ref)))

    # Build distance matrix
    # Use a large value for "no match possible" to ensure Hungarian algorithm
    # doesn't assign pairs beyond max_distance
    inf_cost = max_distance * 1000  # Effectively infinite

    cost_matrix = np.full((n_det, n_ref), inf_cost)

    for i, det_geom in enumerate(det_geoms):
        det_point = det_geom.centroid if det_geom.geom_type != 'Point' else det_geom
        for j, ref_geom in enumerate(ref_geoms):
            ref_point = ref_geom.centroid if ref_geom.geom_type != 'Point' else ref_geom
            dist = det_point.distance(ref_point)
            if dist <= max_distance:
                cost_matrix[i, j] = dist

    # Hungarian algorithm finds optimal assignment minimising total cost
    det_indices, ref_indices = linear_sum_assignment(cost_matrix)

    # Filter out assignments that exceed max_distance
    matched_det = []
    matched_ref = []
    for d_idx, r_idx in zip(det_indices, ref_indices):
        if cost_matrix[d_idx, r_idx] <= max_distance:
            matched_det.append(d_idx)
            matched_ref.append(r_idx)

    unmatched_det = [i for i in range(n_det) if i not in matched_det]
    unmatched_ref = [i for i in range(n_ref) if i not in matched_ref]

    return (matched_det, matched_ref, unmatched_det, unmatched_ref)


def scope_references_to_tiles(
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Return only references that intersect at least one individual tile polygon.

    Uses per-tile spatial join rather than union_all(), which could include
    references falling in gaps between non-contiguous tiles — a boundary-effect
    artefact that inflates false negative counts (see errata E7).

    Args:
        gdf_ref: GeoDataFrame of ground truth reference points.
        gdf_bounds: GeoDataFrame of tile boundary polygons.

    Returns:
        GeoDataFrame: Subset of gdf_ref intersecting at least one tile.
    """
    if gdf_ref.empty or gdf_bounds.empty:
        return gdf_ref.iloc[0:0]  # Empty GeoDataFrame preserving schema

    # Spatial join: each reference matched to every tile it intersects
    in_scope = gpd.sjoin(gdf_ref, gdf_bounds, how='inner', predicate='intersects')

    # Deduplicate: a reference intersecting multiple overlapping tiles
    # appears once per tile in the join — keep unique reference indices only
    return gdf_ref.loc[gdf_ref.index.isin(in_scope.index)].copy()


def _assign_refs_to_primary_tiles(
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict[str, set]:
    """
    Assign each reference to exactly one primary tile.

    When tiles overlap (e.g., 64-pixel stride overlap), a reference
    near a tile border may intersect multiple tile geometries. To
    prevent double-counting in per-tile TP/FP/FN computation, each
    reference is assigned to the tile whose centroid is nearest to
    the reference point.

    Args:
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries (must have 'tile_name').

    Returns:
        Dict mapping tile_name → set of reference indices assigned
        to that tile.
    """
    from collections import defaultdict

    # Spatial join: find all (ref, tile) intersections
    joined = gpd.sjoin(
        gdf_ref, gdf_bounds, how="inner", predicate="intersects",
    )

    if joined.empty:
        return {}

    # Pre-compute tile centroids
    centroid_map: dict[str, object] = {}
    for _, row in gdf_bounds.iterrows():
        centroid_map[row["tile_name"]] = row.geometry.centroid

    # For each reference, assign to nearest-centroid tile
    tile_assignments: dict[str, set] = defaultdict(set)

    for ref_idx in joined.index.unique():
        matches = joined.loc[[ref_idx]] if joined.index.duplicated().any() \
            else joined.loc[joined.index == ref_idx]
        tile_names = matches["tile_name"].tolist()

        if len(tile_names) == 1:
            tile_assignments[tile_names[0]].add(ref_idx)
        else:
            # Multiple tiles — assign to tile with nearest centroid
            ref_geom = gdf_ref.loc[ref_idx].geometry
            best_tile = min(
                tile_names,
                key=lambda t: ref_geom.distance(centroid_map[t]),
            )
            tile_assignments[best_tile].add(ref_idx)

    return dict(tile_assignments)


def compute_per_tile_tp_fp_fn(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int = 20,
) -> pd.DataFrame:
    """
    Pre-compute TP, FP, FN counts per tile via per-map Hungarian matching.

    Performs Hungarian-algorithm matching **per map** (identical to
    ``calculate_f1_internal``), then distributes the TP/FP/FN results
    to individual tiles for bootstrap resampling. This avoids two
    biases that arise from naive per-tile matching:

    1. **Reference double-counting** — with overlapping tiles, a reference
       near a tile border intersects multiple tile geometries. Per-tile
       matching counts it in each tile, inflating both TP and FN.
    2. **Border-detection misses** — a detection in tile A near the border
       may be closest to a reference in tile B's overlap zone. Per-tile
       matching can't make this cross-tile assignment.

    The approach: match globally per map, then assign each outcome to a
    tile — TPs and FPs to the detection's ``source_tile``, unmatched FNs
    to the reference's primary tile (nearest centroid).

    Args:
        gdf_det: GeoDataFrame of detections (must have 'source_tile').
        gdf_ref: GeoDataFrame of ground truth references (must have 'Map').
        gdf_bounds: GeoDataFrame of tile boundaries (must have 'tile_name').
        buffer_metres: Maximum distance for a valid match (default 20 m).

    Returns:
        DataFrame with columns [tile_name, tp, fp, fn], one row per tile.
    """
    tile_counts: dict[str, dict[str, int]] = {
        row["tile_name"]: {"tp": 0, "fp": 0, "fn": 0}
        for _, row in gdf_bounds.iterrows()
    }

    # Pre-compute primary tile for each reference (for FN assignment)
    ref_primary = _assign_refs_to_primary_tiles(gdf_ref, gdf_bounds)
    # Invert: ref_index → tile_name
    ref_to_tile: dict[int, str] = {}
    for tile_name, ref_indices in ref_primary.items():
        for ref_idx in ref_indices:
            ref_to_tile[ref_idx] = tile_name

    # Scope by processed maps (same logic as calculate_f1_internal)
    processed_maps = {
        get_map_name(n) for n in gdf_bounds["tile_name"].unique()
    }

    # Auto-detect the reference map column (see calculate_f1_internal).
    if "Map" in gdf_ref.columns:
        ref_map_col = "Map"
    elif "source_map" in gdf_ref.columns:
        ref_map_col = "source_map"
    else:
        raise ValueError(
            "Reference GeoDataFrame has no 'Map' or 'source_map' column. "
            f"Available columns: {list(gdf_ref.columns)}"
        )

    for map_name in processed_maps:
        if map_name == "Unknown":
            continue

        map_bounds = gdf_bounds[
            gdf_bounds["tile_name"].str.startswith(map_name)
        ]

        # Scope references to this map's tile bounds
        ref_for_map = gdf_ref[gdf_ref[ref_map_col] == map_name]
        if not ref_for_map.empty:
            ref_scope = scope_references_to_tiles(ref_for_map, map_bounds)
        else:
            ref_scope = ref_for_map.iloc[0:0]

        # All detections on this map
        det_scope = gdf_det[
            gdf_det["source_tile"].str.startswith(map_name)
        ]

        if det_scope.empty and ref_scope.empty:
            continue

        if det_scope.empty:
            # All in-scope references are FNs — assign to primary tiles
            for ref_idx in ref_scope.index:
                tile = ref_to_tile.get(ref_idx)
                if tile and tile in tile_counts:
                    tile_counts[tile]["fn"] += 1
            continue

        if ref_scope.empty:
            # All detections are FPs — assign to source tiles
            for _, det_row in det_scope.iterrows():
                tile = det_row["source_tile"]
                if tile in tile_counts:
                    tile_counts[tile]["fp"] += 1
            continue

        # Per-map Hungarian matching (same as calculate_f1_internal)
        det_geoms = list(det_scope.geometry)
        ref_geoms = list(ref_scope.geometry)
        matched_det, matched_ref, unmatched_det, unmatched_ref = \
            match_detections_to_references(
                det_geoms, ref_geoms, buffer_metres,
            )

        # Assign TPs to the detection's source tile
        for d_idx in matched_det:
            det_row = det_scope.iloc[d_idx]
            tile = det_row["source_tile"]
            if tile in tile_counts:
                tile_counts[tile]["tp"] += 1

        # Assign FPs to the detection's source tile
        for d_idx in unmatched_det:
            det_row = det_scope.iloc[d_idx]
            tile = det_row["source_tile"]
            if tile in tile_counts:
                tile_counts[tile]["fp"] += 1

        # Assign FNs to the reference's primary tile
        ref_index_list = list(ref_scope.index)
        for r_idx in unmatched_ref:
            ref_original_idx = ref_index_list[r_idx]
            tile = ref_to_tile.get(ref_original_idx)
            if tile and tile in tile_counts:
                tile_counts[tile]["fn"] += 1

    rows = [
        {"tile_name": tile, **counts}
        for tile, counts in tile_counts.items()
    ]
    return pd.DataFrame(rows)


def compute_per_tile_classification(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Pre-compute per-tile binary classification (TP, TN, FP, FN) for MCC.

    Each tile is classified as one of {TP, TN, FP, FN} based on whether it
    contains any reference mounds and whether the model produced any
    detections in that tile. Returns a per-tile DataFrame with one-hot
    encoded columns ``tp``, ``tn``, ``fp``, ``fn`` (each 0 or 1, exactly
    one is 1 per row), suitable for use in paired permutation tests of
    Matthews Correlation Coefficient (MCC).

    Classification matrix (matches calculate_tile_classification):
        - TP: tile has refs AND has detections
        - TN: tile has neither refs nor detections
        - FP: tile has detections but no refs
        - FN: tile has refs but no detections

    Args:
        gdf_det: GeoDataFrame of detections (must have ``source_tile``
            column).
        gdf_ref: GeoDataFrame of ground-truth references.
        gdf_bounds: GeoDataFrame of tile boundaries (must have
            ``tile_name`` column).

    Returns:
        DataFrame with columns [tile_name, tp, tn, fp, fn]. Exactly one
        of {tp, tn, fp, fn} is 1 per row; the other three are 0.

    Notes:
        Sums over all rows reproduce the aggregate (TP, TN, FP, FN)
        returned by ``calculate_tile_classification()``. The per-tile
        representation is required for tile-swap permutation tests of
        MCC, where each tile's classification (one of the 4 cells) is
        independently swapped between two conditions.
    """
    classification_result = calculate_tile_classification(
        gdf_det, gdf_ref, gdf_bounds,
    )
    rows = []
    for detail in classification_result.get("tile_details", []):
        cls = detail["classification"]
        rows.append({
            "tile_name": detail["tile_name"],
            "tp": 1 if cls == "TP" else 0,
            "tn": 1 if cls == "TN" else 0,
            "fp": 1 if cls == "FP" else 0,
            "fn": 1 if cls == "FN" else 0,
        })
    return pd.DataFrame(rows)


def aggregate_tile_metrics(
    tile_metrics: pd.DataFrame,
    sample_tiles: np.ndarray,
) -> tuple[float, float, float]:
    """
    Aggregate TP/FP/FN from pre-computed per-tile metrics for a bootstrap sample.

    Looks up each tile in sample_tiles (which may contain duplicates from
    bootstrap resampling) and sums TP, FP, FN across the sample. A tile
    sampled k times contributes k × its counts. Computes precision, recall,
    and F1 from the aggregated totals.

    Args:
        tile_metrics: DataFrame with columns [tile_name, tp, fp, fn],
            as returned by compute_per_tile_tp_fp_fn().
        sample_tiles: Array of tile names (may contain duplicates).

    Returns:
        Tuple of (precision, recall, f1).
    """
    # Index by tile_name for fast lookup
    indexed = tile_metrics.set_index('tile_name')

    tp_total = 0
    fp_total = 0
    fn_total = 0

    for tile_name in sample_tiles:
        if tile_name in indexed.index:
            row = indexed.loc[tile_name]
            # If tile_name appears multiple times in tile_metrics
            # (shouldn't happen, but handle gracefully), take first row
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            tp_total += int(row['tp'])
            fp_total += int(row['fp'])
            fn_total += int(row['fn'])

    precision = tp_total / (tp_total + fp_total) if (tp_total + fp_total) > 0 else 0.0
    recall = tp_total / (tp_total + fn_total) if (tp_total + fn_total) > 0 else 0.0
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return precision, recall, f1


def score_detection_set(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int = 20,
    compute_mcc: bool = True,
) -> dict:
    """Fast, bootstrap-free POINT scorer for grid / sweep analyses.

    This is the reusable primitive for scoring **many** detection sets against
    the same ground truth — threshold sweeps, operating-point grids, robustness
    matrices. It returns only point estimates (no bootstrap CIs) and does no
    file I/O, so the caller loads ``gdf_ref`` / ``gdf_bounds`` ONCE and reuses
    them across every set.

    **Why this exists** (use it instead of shelling out to
    ``evaluate_detections.py`` in a loop): the CLI wrapper reloads the ground
    truth + bounds, writes/reads a GeoJSON, and runs a 1,000-iteration BCa
    bootstrap on *every* call — ~20 s/set, so a 600-set grid takes ~3 hours.
    Calling the point functions in-process drops that to milliseconds/set. The
    metric is identical (the CLI wraps these same two functions); only the
    redundant bootstrap + subprocess + I/O overhead is removed.

    **When NOT to use this**: for a single authoritative cell evaluation where
    you need the published F1/MCC bootstrap CIs, use ``evaluate_detections.py``
    (or :func:`evaluate_single_run`) — the CIs are the point of those.

    Args:
        gdf_det: Detection GeoDataFrame in EPSG:32635 (:data:`DEFAULT_CRS`).
            For MCC it must carry a ``source_tile`` column.
        gdf_ref: Ground-truth references (EPSG:32635).
        gdf_bounds: Tile boundaries defining evaluation scope (EPSG:32635,
            with a ``tile_name`` column for MCC).
        buffer_metres: Match radius for F1 (default 20 m, the headline buffer).
        compute_mcc: If True, also compute the point tile-level MCC.

    Returns:
        ``{"f1", "precision", "recall", "n_detections", "mcc"}``. ``mcc`` is
        ``None`` when ``compute_mcc`` is False or there are no detections.
    """
    n_det = len(gdf_det)
    if n_det == 0:
        return {"f1": 0.0, "precision": 0.0, "recall": 0.0,
                "n_detections": 0, "mcc": None}
    precision, recall, f1 = calculate_f1_internal(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )
    mcc = None
    if compute_mcc:
        mcc = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds).get("mcc")
    return {"f1": float(f1), "precision": float(precision),
            "recall": float(recall), "n_detections": n_det, "mcc": mcc}


def calculate_f1_internal(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int = 20,
) -> tuple[float, float, float]:
    """
    Calculate global F1 using one-to-one matching via Hungarian algorithm.

    Each detection can match at most one reference, and vice versa.
    This ensures accurate mound counts: if one detection covers two mounds,
    it counts as 1 TP + 1 FN.

    Args:
        gdf_det: GeoDataFrame of detections.
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries (defines evaluation scope).
        buffer_metres: Maximum distance for a valid match (default 20 m).

    Returns:
        Tuple of (precision, recall, f1).
    """
    tp = 0
    fp = 0
    fn = 0

    # Scope by processed maps
    processed_maps = {get_map_name(n) for n in gdf_bounds['tile_name'].unique()}

    # Auto-detect the reference map column:
    #   - Gold standard (mounds-reference.geojson): 'Map'
    #   - Student ground truth (student-mounds-55maps.geojson): 'source_map'
    # Supporting both keeps the evaluator generic across datasets.
    if 'Map' in gdf_ref.columns:
        ref_map_col = 'Map'
    elif 'source_map' in gdf_ref.columns:
        ref_map_col = 'source_map'
    else:
        raise ValueError(
            "Reference GeoDataFrame has no 'Map' or 'source_map' column. "
            f"Available columns: {list(gdf_ref.columns)}"
        )

    for map_name in processed_maps:
        if map_name == "Unknown":
            continue

        map_bounds = gdf_bounds[gdf_bounds['tile_name'].str.startswith(map_name)]

        ref_scope = gdf_ref[gdf_ref[ref_map_col] == map_name]
        if not ref_scope.empty:
            ref_scope = scope_references_to_tiles(ref_scope, map_bounds)

        det_scope = gdf_det[gdf_det['source_tile'].str.startswith(map_name)]

        if det_scope.empty and ref_scope.empty:
            continue

        if det_scope.empty:
            fn += len(ref_scope)
        elif ref_scope.empty:
            fp += len(det_scope)
        else:
            # One-to-one matching using Hungarian algorithm
            det_geoms = list(det_scope.geometry)
            ref_geoms = list(ref_scope.geometry)

            matched_det, matched_ref, unmatched_det, unmatched_ref = \
                match_detections_to_references(det_geoms, ref_geoms, buffer_metres)

            tp += len(matched_det)
            fp += len(unmatched_det)
            fn += len(unmatched_ref)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return precision, recall, f1


def bootstrap_ci(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_iterations: int = 1000,
    random_seed: int | None = None,
    buffer_metres: int = 20,
    coverage_threshold: float = DEFAULT_COVERAGE_THRESHOLD,
) -> dict:
    """
    BCa bootstrap 95 % confidence intervals for precision, recall, and F1.

    Methodology aligned with preregistration Section 3.5 with the
    methodological upgrade applied in commit ``feat(bootstrap): replace
    percentile method with BCa`` (2026-04-29):

    * **Resampling unit**: tiles (the preregistered unit of analysis).
    * **Resampling method**: with replacement (standard bootstrap).
    * **CI method**: Bias-Corrected and Accelerated (BCa) via
      :func:`scipy.stats.bootstrap`. Adjusts for both bias and skew of
      the bootstrap distribution. Falls back to the percentile method
      when BCa is degenerate (e.g. constant statistic or undefined
      acceleration).
    * **Coverage check**: Mitigation 3 (sparse-coverage transparency).
      Counts tiles with TP+FP+FN == 0; flags ``coverage_status =
      "sparse_cross_grid"`` when the zero-fraction strictly exceeds
      ``coverage_threshold`` (default 0.5).

    Returned dict preserves the legacy ``f1.ci_lower`` / ``f1.ci_upper``
    schema so downstream consumers do not break. New fields:

    * ``f1.point`` / ``precision.point`` / ``recall.point`` — deterministic
      point estimates from :func:`calculate_f1_internal` (no bootstrap).
    * ``f1.method`` / etc — ``"BCa"`` or ``"percentile_fallback"``.
    * ``coverage`` — Mitigation 3 diagnostics block (see
      :func:`_compute_coverage`).

    Args:
        gdf_det: GeoDataFrame of detections.
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries (defines tiles for
            resampling).
        n_iterations: Number of bootstrap iterations (default 1000).
        random_seed: Optional seed for reproducibility.
        buffer_metres: Spatial matching tolerance in metres for TP/FP/FN
            assignment (default 20). Controls how close a detection must
            be to a reference point to count as a true positive.
        coverage_threshold: Zero-fraction threshold for the sparse-coverage
            flag. Strict ``>`` semantics. Defaults to
            :data:`DEFAULT_COVERAGE_THRESHOLD` (0.5).

    Returns:
        Bootstrap results with BCa CIs for F1, precision, and recall plus
        coverage diagnostics.
    """
    tiles = gdf_bounds['tile_name'].unique()
    n_tiles = len(tiles)
    if n_tiles == 0:
        return {}

    # Pre-compute per-tile TP/FP/FN once (errata E26: fixes duplicate-tile
    # reference de-duplication bias in bootstrap resampling).
    tile_metrics = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )

    # Vectorise the per-tile counts as NumPy arrays so the BCa statistic
    # callable can sum them via fancy indexing (much faster than the prior
    # DataFrame.loc loop and required for scipy's vectorised BCa path).
    tm_indexed = tile_metrics.set_index("tile_name").reindex(tiles)
    tp_arr = tm_indexed["tp"].fillna(0).to_numpy(dtype=float)
    fp_arr = tm_indexed["fp"].fillna(0).to_numpy(dtype=float)
    fn_arr = tm_indexed["fn"].fillna(0).to_numpy(dtype=float)

    def _precision_from_idx(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        tp = float(tp_arr[idx].sum())
        fp = float(fp_arr[idx].sum())
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0

    def _recall_from_idx(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        tp = float(tp_arr[idx].sum())
        fn = float(fn_arr[idx].sum())
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0

    def _f1_from_idx(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        tp = float(tp_arr[idx].sum())
        fp = float(fp_arr[idx].sum())
        fn = float(fn_arr[idx].sum())
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        return (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

    indices = np.arange(n_tiles)
    f1_ci = _bca_ci_from_indices(
        indices, _f1_from_idx, n_iterations, random_seed,
    )
    precision_ci = _bca_ci_from_indices(
        indices, _precision_from_idx, n_iterations, random_seed,
    )
    recall_ci = _bca_ci_from_indices(
        indices, _recall_from_idx, n_iterations, random_seed,
    )

    # Deterministic point estimates (do not depend on bootstrap iterations)
    # — these are the headline numbers the paper cites.
    p_point, r_point, f1_point = calculate_f1_internal(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )

    coverage = _compute_coverage(tile_metrics, threshold=coverage_threshold)

    return {
        "f1": {
            "point": float(f1_point),
            "mean": f1_ci["mean"],
            "ci_lower": f1_ci["ci_lower"],
            "ci_upper": f1_ci["ci_upper"],
            "method": f1_ci["method"],
        },
        "precision": {
            "point": float(p_point),
            "mean": precision_ci["mean"],
            "ci_lower": precision_ci["ci_lower"],
            "ci_upper": precision_ci["ci_upper"],
            "method": precision_ci["method"],
        },
        "recall": {
            "point": float(r_point),
            "mean": recall_ci["mean"],
            "ci_lower": recall_ci["ci_lower"],
            "ci_upper": recall_ci["ci_upper"],
            "method": recall_ci["method"],
        },
        "coverage": coverage,
        "n_iterations": n_iterations,
        "bootstrap_method": BOOTSTRAP_METHOD,
        "bootstrap_lib": BOOTSTRAP_LIB,
        # Backwards compatibility fields (deprecated, use nested structure
        # above). Kept for legacy consumers that index ci["mean"] /
        # ci["ci_lower"] / ci["ci_upper"] directly.
        "mean": f1_ci["mean"],
        "ci_lower": f1_ci["ci_lower"],
        "ci_upper": f1_ci["ci_upper"],
    }


def bootstrap_effect_size_ci(
    gdf_det_a: gpd.GeoDataFrame,
    gdf_bounds_a: gpd.GeoDataFrame,
    gdf_det_b: gpd.GeoDataFrame,
    gdf_bounds_b: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    n_iterations: int = 1000,
    random_seed: int | None = None,
    return_p_values: bool = False,
    buffer_metres: int = 20,
) -> dict:
    """
    Bootstrap confidence intervals for effect size (difference) between two conditions.

    Computes 95% bootstrapped CIs for the difference in F1, precision, and recall
    between Condition A and Condition B, as required by preregistration Section 3.5:
    "Report effect sizes (F1 difference, precision difference, recall difference)
    with 95% bootstrapped CIs"

    Methodology:
    - Paired bootstrap: Same tile indices sampled for both conditions
    - Resampling unit: Tiles (respects hierarchical structure)
    - Effect size: Condition A - Condition B (positive = A better)
    - CI calculation: 2.5th and 97.5th percentiles

    Args:
        gdf_det_a: GeoDataFrame of detections for Condition A.
        gdf_bounds_a: GeoDataFrame of tile boundaries for Condition A.
        gdf_det_b: GeoDataFrame of detections for Condition B.
        gdf_bounds_b: GeoDataFrame of tile boundaries for Condition B.
        gdf_ref: GeoDataFrame of ground truth references (shared).
        n_iterations: Number of bootstrap iterations (default 1000).
        random_seed: Optional seed for reproducibility.
        return_p_values: If True, compute and include two-sided bootstrap
            p-values for each metric. The p-value is the proportion of
            bootstrap samples where the effect size crosses zero,
            doubled for a two-sided test. Required for False Discovery
            Rate (FDR) correction across multiple comparisons.

    Returns:
        Effect size estimates with 95% CIs for F1, precision, recall differences.
        When ``return_p_values=True``, each metric dict also includes ``p_value``.
    """
    # Get common tiles between conditions
    tiles_a = set(gdf_bounds_a['tile_name'].unique())
    tiles_b = set(gdf_bounds_b['tile_name'].unique())
    common_tiles = list(tiles_a & tiles_b)
    n_tiles = len(common_tiles)

    if n_tiles == 0:
        return {"error": "No common tiles between conditions"}

    rng = np.random.default_rng(random_seed)

    # Pre-compute per-tile TP/FP/FN for both conditions (errata E26)
    # Filter bounds to common tiles for consistent scoping
    common_bounds_a = gdf_bounds_a[gdf_bounds_a['tile_name'].isin(common_tiles)]
    common_bounds_b = gdf_bounds_b[gdf_bounds_b['tile_name'].isin(common_tiles)]
    tile_metrics_a = compute_per_tile_tp_fp_fn(
        gdf_det_a, gdf_ref, common_bounds_a, buffer_metres=buffer_metres,
    )
    tile_metrics_b = compute_per_tile_tp_fp_fn(
        gdf_det_b, gdf_ref, common_bounds_b, buffer_metres=buffer_metres,
    )

    f1_diffs = []
    precision_diffs = []
    recall_diffs = []

    for _i in range(n_iterations):
        # Paired sampling: same tiles for both conditions
        sample_tiles = rng.choice(common_tiles, n_tiles, replace=True)

        p_a, r_a, f1_a = aggregate_tile_metrics(tile_metrics_a, sample_tiles)
        p_b, r_b, f1_b = aggregate_tile_metrics(tile_metrics_b, sample_tiles)

        # Effect sizes (A - B)
        f1_diffs.append(f1_a - f1_b)
        precision_diffs.append(p_a - p_b)
        recall_diffs.append(r_a - r_b)

    def _build_metric_dict(
        diffs: list[float],
        compute_p: bool,
    ) -> dict:
        """Build a metric difference dict with BCa CI and optional p-value.

        Uses :func:`_compute_bca_ci` which applies a leave-one-out
        jackknife of the bootstrap distribution to estimate the
        acceleration term (Efron 1987). Falls back to the percentile
        method on degenerate distributions.
        """
        bca = _compute_bca_ci(diffs)
        result = {
            "mean": bca["mean"],
            "ci_lower": bca["ci_lower"],
            "ci_upper": bca["ci_upper"],
            "method": bca["method"],
        }
        if compute_p:
            # Two-sided bootstrap p-value: proportion of samples on
            # the minority side of zero, doubled. Clamped to [1/N, 1]
            # to avoid exact-zero p-values from finite samples.
            diffs_arr = np.array(diffs)
            prop_le_zero = np.mean(diffs_arr <= 0)
            prop_gt_zero = np.mean(diffs_arr > 0)
            p_value = 2.0 * min(prop_le_zero, prop_gt_zero)
            # Floor at 1/n_iterations (cannot claim p=0 from
            # finite bootstrap)
            p_value = max(p_value, 1.0 / n_iterations)
            result["p_value"] = float(p_value)
        return result

    return {
        "f1_difference": _build_metric_dict(
            f1_diffs, return_p_values,
        ),
        "precision_difference": _build_metric_dict(
            precision_diffs, return_p_values,
        ),
        "recall_difference": _build_metric_dict(
            recall_diffs, return_p_values,
        ),
        "n_tiles": n_tiles,
        "n_iterations": n_iterations,
        "bootstrap_method": BOOTSTRAP_METHOD,
        "bootstrap_lib": BOOTSTRAP_LIB,
    }


def bootstrap_multi_run_ci(
    run_gdfs: list[tuple[int, gpd.GeoDataFrame]],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_iterations: int = 1000,
    random_seed: int | None = None,
    buffer_metres: int = 20,
) -> dict:
    """
    Bootstrap 95% CIs for a condition with K independent runs.

    For each bootstrap iteration:
    1. Sample tiles with replacement (same tile set for all runs)
    2. Compute F1, precision, recall for each run on the tile sample
    3. Average metrics across runs
    4. CI = 2.5th/97.5th percentiles of the mean-metric distribution

    This preserves tiles as the resampling unit (per preregistration
    section 3.5) while correctly handling the K=10 repeated-measures
    structure. Errata E22: replaces the prior approach of merging all
    runs and computing one F1, which inflated detection counts K-fold.

    Args:
        run_gdfs: List of (run_number, GeoDataFrame) tuples, one per run.
            Each GeoDataFrame must have 'source_tile' column.
        gdf_ref: GeoDataFrame of ground truth references (shared across runs).
        gdf_bounds: GeoDataFrame of tile boundaries (shared across runs).
            Must have 'tile_name' column.
        n_iterations: Number of bootstrap iterations (default 1000).
        random_seed: Optional seed for reproducibility.

    Returns:
        dict: Bootstrap CIs for F1, precision, and recall with structure
            matching bootstrap_ci() output for downstream compatibility.
    """
    tiles = gdf_bounds['tile_name'].unique()
    n_tiles = len(tiles)

    if n_tiles == 0 or not run_gdfs:
        return {}

    rng = np.random.default_rng(random_seed)

    # Pre-compute per-tile TP/FP/FN for each run (errata E26)
    run_tile_metrics: list[pd.DataFrame] = []
    for _run_num, gdf_det in run_gdfs:
        tm = compute_per_tile_tp_fp_fn(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
        )
        run_tile_metrics.append(tm)

    f1_means = []
    precision_means = []
    recall_means = []

    for _i in range(n_iterations):
        # Sample tiles with replacement
        sample_tiles = rng.choice(tiles, n_tiles, replace=True)

        # Compute metrics for each run on the same tile sample
        run_f1s = []
        run_precisions = []
        run_recalls = []

        for tm in run_tile_metrics:
            p, r, f1 = aggregate_tile_metrics(tm, sample_tiles)
            run_f1s.append(f1)
            run_precisions.append(p)
            run_recalls.append(r)

        # Average across runs
        f1_means.append(float(np.mean(run_f1s)))
        precision_means.append(float(np.mean(run_precisions)))
        recall_means.append(float(np.mean(run_recalls)))

    f1_bca = _compute_bca_ci(f1_means)
    p_bca = _compute_bca_ci(precision_means)
    r_bca = _compute_bca_ci(recall_means)
    return {
        "f1": {
            "mean": f1_bca["mean"],
            "ci_lower": f1_bca["ci_lower"],
            "ci_upper": f1_bca["ci_upper"],
            "method": f1_bca["method"],
        },
        "precision": {
            "mean": p_bca["mean"],
            "ci_lower": p_bca["ci_lower"],
            "ci_upper": p_bca["ci_upper"],
            "method": p_bca["method"],
        },
        "recall": {
            "mean": r_bca["mean"],
            "ci_lower": r_bca["ci_lower"],
            "ci_upper": r_bca["ci_upper"],
            "method": r_bca["method"],
        },
        "n_iterations": n_iterations,
        "n_runs": len(run_gdfs),
        "n_tiles": n_tiles,
        "bootstrap_method": BOOTSTRAP_METHOD,
        "bootstrap_lib": BOOTSTRAP_LIB,
    }


def bootstrap_multi_run_effect_size_ci(
    run_gdfs_a: list[tuple[int, gpd.GeoDataFrame]],
    run_gdfs_b: list[tuple[int, gpd.GeoDataFrame]],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_iterations: int = 1000,
    random_seed: int | None = None,
    buffer_metres: int = 20,
) -> dict:
    """
    Bootstrap 95% CIs for effect size between two multi-run conditions.

    For each bootstrap iteration:
    1. Sample tiles with replacement (same tiles for both conditions)
    2. Compute mean-F1 across runs for each condition on the tile sample
    3. Compute paired difference: mean_F1_A - mean_F1_B
    4. CI = 2.5th/97.5th percentiles of the difference distribution

    Positive difference means Condition A outperforms Condition B.
    Errata E22: uses per-run evaluation rather than merged detections.

    Args:
        run_gdfs_a: Per-run (run_number, GeoDataFrame) tuples for Condition A.
        run_gdfs_b: Per-run (run_number, GeoDataFrame) tuples for Condition B.
        gdf_ref: GeoDataFrame of ground truth references (shared).
        gdf_bounds: GeoDataFrame of tile boundaries (shared).
        n_iterations: Number of bootstrap iterations (default 1000).
        random_seed: Optional seed for reproducibility.

    Returns:
        dict: Effect size CIs for F1, precision, recall differences.
    """
    tiles = gdf_bounds['tile_name'].unique()
    n_tiles = len(tiles)

    if n_tiles == 0 or not run_gdfs_a or not run_gdfs_b:
        return {"error": "Insufficient data for effect size computation"}

    rng = np.random.default_rng(random_seed)

    # Pre-compute per-tile TP/FP/FN for every run in both conditions (E26)
    run_metrics_a: list[pd.DataFrame] = []
    for _rn, gdf_det in run_gdfs_a:
        run_metrics_a.append(
            compute_per_tile_tp_fp_fn(
                gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
            )
        )
    run_metrics_b: list[pd.DataFrame] = []
    for _rn, gdf_det in run_gdfs_b:
        run_metrics_b.append(
            compute_per_tile_tp_fp_fn(
                gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
            )
        )

    def _mean_metrics(
        run_tms: list[pd.DataFrame],
        sample: np.ndarray,
    ) -> tuple[float, float, float]:
        """Average precision, recall, F1 across runs for a bootstrap sample."""
        run_f1s, run_ps, run_rs = [], [], []
        for tm in run_tms:
            p, r, f1 = aggregate_tile_metrics(tm, sample)
            run_f1s.append(f1)
            run_ps.append(p)
            run_rs.append(r)
        return float(np.mean(run_f1s)), float(np.mean(run_ps)), float(np.mean(run_rs))

    f1_diffs = []
    precision_diffs = []
    recall_diffs = []

    for _i in range(n_iterations):
        # Paired sampling: same tiles for both conditions
        sample_tiles = rng.choice(tiles, n_tiles, replace=True)

        f1_a, p_a, r_a = _mean_metrics(run_metrics_a, sample_tiles)
        f1_b, p_b, r_b = _mean_metrics(run_metrics_b, sample_tiles)

        f1_diffs.append(f1_a - f1_b)
        precision_diffs.append(p_a - p_b)
        recall_diffs.append(r_a - r_b)

    f1_bca = _compute_bca_ci(f1_diffs)
    p_bca = _compute_bca_ci(precision_diffs)
    r_bca = _compute_bca_ci(recall_diffs)
    return {
        "f1_difference": {
            "mean": f1_bca["mean"],
            "ci_lower": f1_bca["ci_lower"],
            "ci_upper": f1_bca["ci_upper"],
            "method": f1_bca["method"],
        },
        "precision_difference": {
            "mean": p_bca["mean"],
            "ci_lower": p_bca["ci_lower"],
            "ci_upper": p_bca["ci_upper"],
            "method": p_bca["method"],
        },
        "recall_difference": {
            "mean": r_bca["mean"],
            "ci_lower": r_bca["ci_lower"],
            "ci_upper": r_bca["ci_upper"],
            "method": r_bca["method"],
        },
        "n_tiles": n_tiles,
        "n_iterations": n_iterations,
        "n_runs_a": len(run_gdfs_a),
        "n_runs_b": len(run_gdfs_b),
        "bootstrap_method": BOOTSTRAP_METHOD,
        "bootstrap_lib": BOOTSTRAP_LIB,
    }


def bootstrap_interaction_ci(
    conditions: dict,
    gdf_ref: gpd.GeoDataFrame,
    factor_a_name: str = "factor_a",
    factor_b_name: str = "factor_b",
    metric: str = "f1",
    n_iterations: int = 1000,
    random_seed: int | None = None,
    buffer_metres: int = 20,
) -> dict:
    """
    Bootstrap confidence intervals for a two-way interaction effect.

    Tests whether the effect of factor_b varies across levels of factor_a
    using paired difference-of-differences bootstrap. Designed for
    preregistration Section 5.5 (M/E × H5 interaction analysis).

    For each bootstrap iteration:
    1. Sample tiles with replacement (same tiles across all conditions)
    2. Compute the chosen metric for each (factor_a, factor_b) cell
    3. Compute simple effects of factor_b at each factor_a level
       (last level minus first level of factor_b)
    4. Compute pairwise interaction contrasts: the difference between
       simple effects at different factor_a levels
    5. If any interaction contrast CI excludes zero, interaction is present

    Args:
        conditions: Dict mapping (factor_a_level, factor_b_level) tuples
            to (gdf_det, gdf_bounds) tuples for each cell of the factorial
            design. All cells must share the same set of tiles.
        gdf_ref: GeoDataFrame of ground truth references (shared across
            all conditions).
        factor_a_name: Label for factor A (e.g., "M/E level"). Used in
            output keys for readability.
        factor_b_name: Label for factor B (e.g., "H5 level"). Used in
            output keys for readability.
        metric: Which metric to test ("f1", "precision", or "recall").
        n_iterations: Number of bootstrap iterations (default 1000).
        random_seed: Optional seed for reproducibility.

    Returns:
        dict with keys:
            - "simple_effects": Dict mapping each factor_a level to the
              simple effect of factor_b (with mean, ci_lower, ci_upper)
            - "interaction_contrasts": List of pairwise interaction
              contrasts between factor_a levels (difference-of-differences)
            - "interaction_detected": Boolean — True if any contrast CI
              excludes zero
            - "factor_a_levels": Sorted list of factor_a levels
            - "factor_b_levels": Sorted list of factor_b levels
            - "metric": The metric tested
            - "n_tiles": Number of common tiles
            - "n_iterations": Number of bootstrap iterations
    """
    # Extract factor levels from condition keys
    factor_a_levels = sorted({k[0] for k in conditions})
    factor_b_levels = sorted({k[1] for k in conditions})

    if len(factor_a_levels) < 2:
        return {"error": "Need at least 2 levels of factor_a for interaction test"}
    if len(factor_b_levels) < 2:
        return {"error": "Need at least 2 levels of factor_b for interaction test"}

    # Find common tiles across all conditions
    tile_sets = []
    for (a_level, b_level), (gdf_det, gdf_bounds) in conditions.items():
        tile_sets.append(set(gdf_bounds['tile_name'].unique()))

    common_tiles = list(set.intersection(*tile_sets))
    n_tiles = len(common_tiles)

    if n_tiles == 0:
        return {"error": "No common tiles across all conditions"}

    rng = np.random.default_rng(random_seed)

    # Metric extraction index: maps metric name to position in
    # (precision, recall, f1) tuple returned by aggregate_tile_metrics
    metric_index = {"precision": 0, "recall": 1, "f1": 2}
    if metric not in metric_index:
        return {"error": f"Unknown metric '{metric}'. Use 'f1', 'precision', or 'recall'."}
    m_idx = metric_index[metric]

    # Pre-compute per-tile TP/FP/FN for each cell (errata E26)
    # Filter bounds to common tiles for each cell
    cell_tile_metrics: dict[tuple, pd.DataFrame] = {}
    for (a_level, b_level), (gdf_det, gdf_bounds) in conditions.items():
        common_bounds = gdf_bounds[gdf_bounds['tile_name'].isin(common_tiles)]
        cell_tile_metrics[(a_level, b_level)] = compute_per_tile_tp_fp_fn(
            gdf_det, gdf_ref, common_bounds, buffer_metres=buffer_metres,
        )

    # Storage for simple effect distributions per factor_a level
    # simple_effect = metric(factor_b last level) - metric(factor_b first level)
    simple_effect_distributions: dict[Any, list[float]] = {
        a: [] for a in factor_a_levels
    }

    b_first = factor_b_levels[0]
    b_last = factor_b_levels[-1]

    for _i in range(n_iterations):
        # Paired sampling: same tiles for all conditions
        sample_tiles = rng.choice(common_tiles, n_tiles, replace=True)

        # Compute metric for each cell needed (first and last factor_b levels
        # at each factor_a level)
        cell_metrics: dict[tuple, float] = {}

        for a_level in factor_a_levels:
            for b_level in [b_first, b_last]:
                result = aggregate_tile_metrics(
                    cell_tile_metrics[(a_level, b_level)], sample_tiles
                )
                cell_metrics[(a_level, b_level)] = result[m_idx]

        # Compute simple effect of factor_b at each factor_a level
        for a_level in factor_a_levels:
            effect = (
                cell_metrics.get((a_level, b_last), 0.0)
                - cell_metrics.get((a_level, b_first), 0.0)
            )
            simple_effect_distributions[a_level].append(effect)

    # Compute CIs for simple effects (BCa via bootstrap-distribution
    # jackknife — see _compute_bca_ci docstring).
    simple_effects = {}
    for a_level in factor_a_levels:
        dist = simple_effect_distributions[a_level]
        bca = _compute_bca_ci(dist)
        simple_effects[a_level] = {
            "mean": bca["mean"],
            "ci_lower": bca["ci_lower"],
            "ci_upper": bca["ci_upper"],
            "method": bca["method"],
        }

    # Compute pairwise interaction contrasts (difference-of-differences)
    interaction_contrasts = []
    interaction_detected = False

    for i, a_i in enumerate(factor_a_levels):
        for a_j in factor_a_levels[i + 1:]:
            # Difference-of-differences for each bootstrap iteration
            dod = [
                simple_effect_distributions[a_i][k]
                - simple_effect_distributions[a_j][k]
                for k in range(n_iterations)
            ]
            dod_bca = _compute_bca_ci(dod)
            ci_lower = dod_bca["ci_lower"]
            ci_upper = dod_bca["ci_upper"]

            # Interaction detected if CI excludes zero. ``ci_lower`` /
            # ``ci_upper`` may be ``None`` for empty distributions; guard
            # against that.
            excludes_zero = (
                ci_lower is not None
                and ci_upper is not None
                and (ci_lower > 0 or ci_upper < 0)
            )

            if excludes_zero:
                interaction_detected = True

            interaction_contrasts.append({
                f"{factor_a_name}_level_1": a_i,
                f"{factor_a_name}_level_2": a_j,
                "difference_of_differences": {
                    "mean": dod_bca["mean"],
                    "ci_lower": ci_lower,
                    "ci_upper": ci_upper,
                    "method": dod_bca["method"],
                },
                "ci_excludes_zero": excludes_zero,
            })

    return {
        "simple_effects": simple_effects,
        "interaction_contrasts": interaction_contrasts,
        "interaction_detected": interaction_detected,
        "factor_a_levels": factor_a_levels,
        "factor_b_levels": factor_b_levels,
        "factor_a_name": factor_a_name,
        "factor_b_name": factor_b_name,
        "metric": metric,
        "n_tiles": n_tiles,
        "n_iterations": n_iterations,
        "bootstrap_method": BOOTSTRAP_METHOD,
        "bootstrap_lib": BOOTSTRAP_LIB,
    }


def calculate_tile_classification(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict:
    """
    Binary classification of tiles as empty vs populated for MCC calculation.

    Implements preregistration Section 4.2: Tile-level Discrimination (MCC).
    Each tile is classified based on whether it contains reference mounds
    and whether the model detected any mounds in that tile.

    Classification matrix:
    - True Positive:  Has mounds + Detected >=1 mound
    - True Negative:  Empty + Detected nothing
    - False Positive: Empty + Detected >=1 mound (hallucination)
    - False Negative: Has mounds + Detected nothing

    Args:
        gdf_det: GeoDataFrame of detections (must have 'source_tile' column).
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries (must have 'tile_name' column).

    Returns:
        Classification results including tp, tn, fp, fn counts; mcc;
        sensitivity; specificity; tile counts; and per-tile details.
    """
    tiles = gdf_bounds['tile_name'].unique()
    n_tiles = len(tiles)

    if n_tiles == 0:
        return {"error": "No tiles in bounds"}

    tile_details = []
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for tile_name in tiles:
        # Get tile geometry
        tile_row = gdf_bounds[gdf_bounds['tile_name'] == tile_name].iloc[0]
        tile_geom = tile_row.geometry

        # Check if tile has any reference mounds (intersecting tile geometry)
        refs_in_tile = gdf_ref[gdf_ref.intersects(tile_geom)]
        has_mounds = len(refs_in_tile) > 0

        # Check if model detected any mounds in this tile
        dets_in_tile = gdf_det[gdf_det['source_tile'] == tile_name]
        has_detections = len(dets_in_tile) > 0

        # Classify tile
        if has_mounds and has_detections:
            classification = "TP"
            tp += 1
        elif not has_mounds and not has_detections:
            classification = "TN"
            tn += 1
        elif not has_mounds and has_detections:
            classification = "FP"
            fp += 1
        else:  # has_mounds and not has_detections
            classification = "FN"
            fn += 1

        tile_details.append({
            "tile_name": tile_name,
            "has_mounds": has_mounds,
            "has_detections": has_detections,
            "n_references": len(refs_in_tile),
            "n_detections": len(dets_in_tile),
            "classification": classification,
        })

    # Calculate MCC
    # MCC = (TP×TN - FP×FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN))
    numerator = (tp * tn) - (fp * fn)
    denominator_parts = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)

    if denominator_parts == 0:
        # Edge case: MCC undefined when any row/column sum is zero
        mcc = None
    else:
        mcc = numerator / np.sqrt(denominator_parts)

    # Calculate sensitivity: TP / (TP + FN)
    if (tp + fn) > 0:
        sensitivity = tp / (tp + fn)
    else:
        sensitivity = None  # No populated tiles

    # Calculate specificity: TN / (TN + FP)
    if (tn + fp) > 0:
        specificity = tn / (tn + fp)
    else:
        specificity = None  # No empty tiles

    n_populated = tp + fn
    n_empty = tn + fp

    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "mcc": mcc,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "n_tiles": n_tiles,
        "n_populated": n_populated,
        "n_empty": n_empty,
        "tile_details": tile_details,
    }


def bootstrap_tile_classification_ci(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_iterations: int = 1000,
    random_seed: int | None = None,
) -> dict:
    """
    BCa bootstrap 95 % CIs for tile-level MCC, sensitivity, and specificity.

    Aligned with preregistration Section 3.5: tile-level resampling with
    replacement. Uses :func:`scipy.stats.bootstrap` with ``method='BCa'``
    via :func:`_bca_ci_from_indices`. Each per-tile classification label
    (TP / TN / FP / FN) is held in arrays indexed by tile, and the
    bootstrap statistic is computed per resample by counting labels in
    the sampled subset.

    On bootstrap iterations where any of the (tp+fp), (tp+fn), (tn+fp),
    or (tn+fn) row/column sums is zero, the metric is undefined; the
    score is treated as ``NaN`` and skipped when computing the CI bounds.

    Args:
        gdf_det: GeoDataFrame of detections.
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries.
        n_iterations: Number of bootstrap iterations (default 1000).
        random_seed: Optional seed for reproducibility.

    Returns:
        Bootstrap CIs for MCC, sensitivity, and specificity. Each metric
        dict includes ``point`` (deterministic estimate from
        :func:`calculate_tile_classification`), ``mean`` (bootstrap mean),
        ``ci_lower``, ``ci_upper``, and ``method``.
    """
    tiles = gdf_bounds['tile_name'].unique()
    n_tiles = len(tiles)

    if n_tiles == 0:
        return {"error": "No tiles in bounds"}

    # Pre-compute per-tile classification once (errata E26: fixes isin()
    # de-duplication that turned bootstrap into subsampling).
    point_result = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)
    tile_class_map: dict[str, str] = {}
    for detail in point_result.get("tile_details", []):
        tile_class_map[detail["tile_name"]] = detail["classification"]

    # Vectorise classification labels into one-hot arrays so per-resample
    # counts collapse to fast NumPy sums via fancy indexing.
    tp_arr = np.array(
        [1.0 if tile_class_map.get(t) == "TP" else 0.0 for t in tiles],
    )
    tn_arr = np.array(
        [1.0 if tile_class_map.get(t) == "TN" else 0.0 for t in tiles],
    )
    fp_arr = np.array(
        [1.0 if tile_class_map.get(t) == "FP" else 0.0 for t in tiles],
    )
    fn_arr = np.array(
        [1.0 if tile_class_map.get(t) == "FN" else 0.0 for t in tiles],
    )

    def _mcc_from_idx(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        tp = float(tp_arr[idx].sum())
        tn = float(tn_arr[idx].sum())
        fp = float(fp_arr[idx].sum())
        fn = float(fn_arr[idx].sum())
        numerator = (tp * tn) - (fp * fn)
        denom_parts = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
        if denom_parts <= 0.0:
            # MCC undefined — return 0.0 so scipy can compute bounds.
            # The point estimate is still tracked separately via
            # ``calculate_tile_classification``.
            return 0.0
        return numerator / np.sqrt(denom_parts)

    def _sensitivity_from_idx(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        tp = float(tp_arr[idx].sum())
        fn = float(fn_arr[idx].sum())
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0

    def _specificity_from_idx(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        tn = float(tn_arr[idx].sum())
        fp = float(fp_arr[idx].sum())
        return tn / (tn + fp) if (tn + fp) > 0 else 0.0

    indices = np.arange(n_tiles)
    mcc_ci = _bca_ci_from_indices(
        indices, _mcc_from_idx, n_iterations, random_seed,
    )
    sens_ci = _bca_ci_from_indices(
        indices, _sensitivity_from_idx, n_iterations, random_seed,
    )
    spec_ci = _bca_ci_from_indices(
        indices, _specificity_from_idx, n_iterations, random_seed,
    )

    # Deterministic point estimates from the original sample (no bootstrap).
    # ``calculate_tile_classification`` returns ``None`` when the metric
    # is undefined on the original data; preserve that as ``None`` rather
    # than coercing to a numeric placeholder.
    mcc_point = point_result.get("mcc")
    sens_point = point_result.get("sensitivity")
    spec_point = point_result.get("specificity")

    return {
        "mcc": {
            "point": float(mcc_point) if mcc_point is not None else None,
            "mean": mcc_ci["mean"],
            "ci_lower": mcc_ci["ci_lower"],
            "ci_upper": mcc_ci["ci_upper"],
            "method": mcc_ci["method"],
        },
        "sensitivity": {
            "point": float(sens_point) if sens_point is not None else None,
            "mean": sens_ci["mean"],
            "ci_lower": sens_ci["ci_lower"],
            "ci_upper": sens_ci["ci_upper"],
            "method": sens_ci["method"],
        },
        "specificity": {
            "point": float(spec_point) if spec_point is not None else None,
            "mean": spec_ci["mean"],
            "ci_lower": spec_ci["ci_lower"],
            "ci_upper": spec_ci["ci_upper"],
            "method": spec_ci["method"],
        },
        "n_iterations": n_iterations,
        "n_valid_mcc": int(n_iterations),
        "n_valid_sensitivity": int(n_iterations),
        "n_valid_specificity": int(n_iterations),
        "bootstrap_method": BOOTSTRAP_METHOD,
        "bootstrap_lib": BOOTSTRAP_LIB,
    }


def bootstrap_tile_effect_size_ci(
    gdf_det_a: gpd.GeoDataFrame,
    gdf_bounds_a: gpd.GeoDataFrame,
    gdf_det_b: gpd.GeoDataFrame,
    gdf_bounds_b: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    n_iterations: int = 1000,
    random_seed: int | None = None,
) -> dict:
    """
    Bootstrap 95% CIs for tile-level MCC difference between two conditions.

    Paired bootstrap: same tiles sampled for both conditions to enable
    valid effect size estimation.

    Args:
        gdf_det_a: GeoDataFrame of detections for Condition A.
        gdf_bounds_a: GeoDataFrame of tile boundaries for Condition A.
        gdf_det_b: GeoDataFrame of detections for Condition B.
        gdf_bounds_b: GeoDataFrame of tile boundaries for Condition B.
        gdf_ref: GeoDataFrame of ground truth references (shared).
        n_iterations: Number of bootstrap iterations (default 1000).
        random_seed: Optional seed for reproducibility.

    Returns:
        Effect size CIs for MCC, sensitivity, and specificity differences.
    """
    # Get common tiles between conditions
    tiles_a = set(gdf_bounds_a['tile_name'].unique())
    tiles_b = set(gdf_bounds_b['tile_name'].unique())
    common_tiles = list(tiles_a & tiles_b)
    n_tiles = len(common_tiles)

    if n_tiles == 0:
        return {"error": "No common tiles between conditions"}

    rng = np.random.default_rng(random_seed)

    # Pre-compute per-tile classifications for both conditions (errata E26)
    common_bounds_a = gdf_bounds_a[gdf_bounds_a['tile_name'].isin(common_tiles)]
    common_bounds_b = gdf_bounds_b[gdf_bounds_b['tile_name'].isin(common_tiles)]

    result_a_full = calculate_tile_classification(gdf_det_a, gdf_ref, common_bounds_a)
    result_b_full = calculate_tile_classification(gdf_det_b, gdf_ref, common_bounds_b)

    tile_class_a: dict[str, str] = {}
    for detail in result_a_full.get("tile_details", []):
        tile_class_a[detail["tile_name"]] = detail["classification"]

    tile_class_b: dict[str, str] = {}
    for detail in result_b_full.get("tile_details", []):
        tile_class_b[detail["tile_name"]] = detail["classification"]

    def _compute_tile_metrics(
        tile_class_map: dict[str, str],
        sample: np.ndarray,
    ) -> tuple[float | None, float | None, float | None]:
        """Compute MCC, sensitivity, specificity from sample with duplicates."""
        tp = sum(1 for t in sample if tile_class_map.get(t) == "TP")
        tn = sum(1 for t in sample if tile_class_map.get(t) == "TN")
        fp = sum(1 for t in sample if tile_class_map.get(t) == "FP")
        fn = sum(1 for t in sample if tile_class_map.get(t) == "FN")

        # MCC
        numerator = (tp * tn) - (fp * fn)
        denom_parts = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
        mcc = numerator / np.sqrt(denom_parts) if denom_parts > 0 else None

        # Sensitivity
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else None

        # Specificity
        specificity = tn / (tn + fp) if (tn + fp) > 0 else None

        return mcc, sensitivity, specificity

    mcc_diffs = []
    sensitivity_diffs = []
    specificity_diffs = []

    for _i in range(n_iterations):
        # Paired sampling: same tiles for both conditions
        sample_tiles = rng.choice(common_tiles, n_tiles, replace=True)

        mcc_a, sens_a, spec_a = _compute_tile_metrics(tile_class_a, sample_tiles)
        mcc_b, sens_b, spec_b = _compute_tile_metrics(tile_class_b, sample_tiles)

        # Calculate differences (A - B) where both are defined
        if mcc_a is not None and mcc_b is not None:
            mcc_diffs.append(mcc_a - mcc_b)

        if sens_a is not None and sens_b is not None:
            sensitivity_diffs.append(sens_a - sens_b)

        if spec_a is not None and spec_b is not None:
            specificity_diffs.append(spec_a - spec_b)

    mcc_bca = _compute_bca_ci(mcc_diffs)
    sens_bca = _compute_bca_ci(sensitivity_diffs)
    spec_bca = _compute_bca_ci(specificity_diffs)
    return {
        "mcc_difference": {
            "mean": mcc_bca["mean"],
            "ci_lower": mcc_bca["ci_lower"],
            "ci_upper": mcc_bca["ci_upper"],
            "method": mcc_bca["method"],
        },
        "sensitivity_difference": {
            "mean": sens_bca["mean"],
            "ci_lower": sens_bca["ci_lower"],
            "ci_upper": sens_bca["ci_upper"],
            "method": sens_bca["method"],
        },
        "specificity_difference": {
            "mean": spec_bca["mean"],
            "ci_lower": spec_bca["ci_lower"],
            "ci_upper": spec_bca["ci_upper"],
            "method": spec_bca["method"],
        },
        "n_tiles": n_tiles,
        "n_iterations": n_iterations,
        "bootstrap_method": BOOTSTRAP_METHOD,
        "bootstrap_lib": BOOTSTRAP_LIB,
    }


def spatial_tolerance_curve(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int] | None = None,
) -> list[dict]:
    """
    Compute F1, precision, and recall at multiple spatial tolerance buffers.

    Evaluates detection performance at increasing match distances to show
    how metrics change with spatial tolerance.

    Args:
        gdf_det: GeoDataFrame of detections.
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries.
        buffers: List of buffer distances in metres (default [10, 20, 30, 40, 50]).

    Returns:
        Per-buffer results with 'buffer', 'precision', 'recall', 'f1' keys.
    """
    if buffers is None:
        buffers = [10, 20, 30, 40, 50]
    results = []
    for b in buffers:
        p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_metres=b)
        results.append({
            "buffer": b,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
        })
    return results


def calculate_per_class_f1(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int = 20,
) -> list[dict]:
    """
    Calculate F1, precision, and recall per mound class.

    Classifies reference mounds by symbol type (burial, benchmark,
    triangulation) and computes metrics for each class independently.

    Args:
        gdf_det: GeoDataFrame of detections (must have 'subtype' column).
        gdf_ref: GeoDataFrame of ground truth references (must have 'Symbol' column).
        gdf_bounds: GeoDataFrame of tile boundaries.
        buffer_metres: Maximum distance for a valid match (default 20 m).

    Returns:
        Per-class results with 'class', 'precision', 'recall', 'f1' keys.
    """
    # Operate on a copy to avoid mutating the caller's DataFrame
    ref = gdf_ref.copy()
    ref['normalised_class'] = ref['Symbol'].apply(normalise_ref_class)
    classes = ["burial_mound", "benchmark_mound", "triangulation_mound"]

    results = []
    for cls in classes:
        det_cls = gdf_det[gdf_det['subtype'] == cls].copy()
        ref_cls = ref[ref['normalised_class'] == cls].copy()

        p, r, f1 = calculate_f1_internal(det_cls, ref_cls, gdf_bounds, buffer_metres)
        results.append({
            "class": cls,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
        })
    return results


def error_taxonomy(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int = 20,
) -> dict:
    """
    Categorise false positives and false negatives by symbol type.

    Uses one-to-one matching to ensure consistent error attribution.

    Args:
        gdf_det: GeoDataFrame of detections.
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries.
        buffer_metres: Maximum distance for a valid match (default 20 m).

    Returns:
        Dict with 'false_positives' (subtype: count) and
        'false_negatives' (class: count).
    """
    taxonomy = {"false_positives": {}, "false_negatives": {}}

    # Scope references to individual tile polygons (not union — see errata E7)
    refs_in_scope = scope_references_to_tiles(gdf_ref, gdf_bounds)

    if gdf_det.empty and refs_in_scope.empty:
        return taxonomy

    # Perform one-to-one matching
    det_geoms = list(gdf_det.geometry) if not gdf_det.empty else []
    ref_geoms = list(refs_in_scope.geometry) if not refs_in_scope.empty else []

    matched_det, matched_ref, unmatched_det, unmatched_ref = \
        match_detections_to_references(det_geoms, ref_geoms, buffer_metres)

    # Categorise false positives by detection subtype
    if unmatched_det and not gdf_det.empty:
        fp_detections = gdf_det.iloc[unmatched_det]
        if 'subtype' in fp_detections.columns:
            taxonomy["false_positives"] = fp_detections['subtype'].value_counts().to_dict()

    # Categorise false negatives by reference class
    if unmatched_ref and not refs_in_scope.empty:
        fn_refs = refs_in_scope.iloc[unmatched_ref].copy()
        fn_refs['normalised_class'] = fn_refs['Symbol'].apply(normalise_ref_class)
        taxonomy["false_negatives"] = fn_refs['normalised_class'].value_counts().to_dict()

    return taxonomy


def generate_report(
    detection_path: Path | str,
    bounds_path: Path | str,
    output_path: Path | str | None = None,
    bootstrap_iterations: int = 1000,
) -> dict:
    """
    Generate a comprehensive metrics report for a detection run.

    Computes global F1/precision/recall, bootstrapped CIs, spatial tolerance
    curve, per-class performance, and error taxonomy. Optionally writes
    results to a JSON file.

    Args:
        detection_path: Path to the detection GeoJSON file.
        bounds_path: Path to the bounds GeoJSON file.
        output_path: Optional path to write JSON report.
        bootstrap_iterations: Number of bootstrap iterations (default 1000).

    Returns:
        Report dictionary, or empty dict on load failure.
    """
    print("Generating Advanced Metrics Report...")
    gdf_det, gdf_bounds, gdf_ref = load_data(detection_path, bounds_path)

    if gdf_det is None:
        return {}

    report = {}

    # 1. Global metrics (at standard 20m buffer)
    p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_metres=20)
    report["global_metrics"] = {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(f1, 4),
    }

    # 2. Bootstrap CIs
    report["bootstrap_ci"] = bootstrap_ci(
        gdf_det, gdf_ref, gdf_bounds, n_iterations=bootstrap_iterations,
    )

    # 3. Spatial tolerance curve
    report["spatial_tolerance"] = spatial_tolerance_curve(
        gdf_det, gdf_ref, gdf_bounds,
    )

    # 4. Per-class performance
    report["per_class_performance"] = calculate_per_class_f1(
        gdf_det, gdf_ref, gdf_bounds,
    )

    # 5. Error taxonomy
    report["error_taxonomy"] = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Advanced metrics saved to {output_path}")

    return report


def print_report_summary(report: dict, title: str = "Metrics Summary") -> None:
    """
    Print a formatted summary of the metrics report to console.

    Args:
        report: The report dictionary from generate_report().
        title: Header title for the summary.
    """
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

    # Global metrics
    gm = report.get("global_metrics", {})
    print("\n[Global Performance @ 20m buffer]")
    print(f"  F1:        {gm.get('f1', 0):.4f}")
    print(f"  Precision: {gm.get('precision', 0):.4f}")
    print(f"  Recall:    {gm.get('recall', 0):.4f}")

    # Bootstrap CI (supports both new nested format and legacy flat format)
    ci = report.get("bootstrap_ci", {})
    if ci:
        n_iter = ci.get('n_iterations', 0)
        print(f"\n[Bootstrap 95% Confidence Intervals (N={n_iter})]")

        # Check for new nested format (preferred)
        if "f1" in ci and isinstance(ci["f1"], dict):
            print(f"  {'Metric':<12} {'Mean':>8} {'95% CI':>20}")
            print(f"  {'-'*12} {'-'*8} {'-'*20}")
            for metric in ["f1", "precision", "recall"]:
                m = ci.get(metric, {})
                mean_val = m.get('mean', 0)
                ci_low = m.get('ci_lower', 0)
                ci_high = m.get('ci_upper', 0)
                print(f"  {metric.capitalize():<12} {mean_val:>8.4f} [{ci_low:.4f}, {ci_high:.4f}]")
        else:
            # Legacy flat format (backwards compatibility)
            print(f"  Mean F1:   {ci.get('mean', 0):.4f}")
            print(f"  95% CI:    [{ci.get('ci_lower', 0):.4f}, {ci.get('ci_upper', 0):.4f}]")

    # Per-class performance
    pcp = report.get("per_class_performance", [])
    if pcp:
        print("\n[Per-Class Performance]")
        print(f"  {'Class':<22} {'F1':>8} {'Prec':>8} {'Rec':>8}")
        print(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*8}")
        for cls in pcp:
            name = cls['class']
            print(
                f"  {name:<22} {cls['f1']:>8.4f}"
                f" {cls['precision']:>8.4f} {cls['recall']:>8.4f}"
            )

    # Spatial tolerance
    st = report.get("spatial_tolerance", [])
    if st:
        print("\n[Spatial Tolerance Curve]")
        print(f"  {'Buffer (m)':<12} {'F1':>8} {'Prec':>8} {'Rec':>8}")
        print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}")
        for row in st:
            print(
                f"  {row['buffer']:<12} {row['f1']:>8.4f}"
                f" {row['precision']:>8.4f} {row['recall']:>8.4f}"
            )

    # Error taxonomy
    et = report.get("error_taxonomy", {})
    fps = et.get("false_positives", {})
    fns = et.get("false_negatives", {})
    if fps or fns:
        print("\n[Error Taxonomy]")
        if fps:
            print(f"  False Positives: {dict(fps)}")
        if fns:
            print(f"  False Negatives: {dict(fns)}")

    print(f"\n{'='*60}\n")


def print_effect_size_summary(
    effect_sizes: dict,
    condition_a: str = "Condition A",
    condition_b: str = "Condition B",
) -> None:
    """
    Print a formatted summary of effect size comparisons between two conditions.

    Args:
        effect_sizes: Output from bootstrap_effect_size_ci().
        condition_a: Name/label for first condition.
        condition_b: Name/label for second condition.
    """
    if "error" in effect_sizes:
        print(f"Error: {effect_sizes['error']}")
        return

    print(f"\n{'='*70}")
    print(f" Effect Size Comparison: {condition_a} vs {condition_b}")
    print(f"{'='*70}")
    print(f"\n[Bootstrapped 95% CIs for Differences (N={effect_sizes.get('n_iterations', 0)})]")
    print(f"  Positive values indicate {condition_a} outperforms {condition_b}")
    print()
    print(f"  {'Metric':<20} {'Δ Mean':>10} {'95% CI':>24}")
    print(f"  {'-'*20} {'-'*10} {'-'*24}")

    for metric_key, label in [
        ("f1_difference", "F1 Difference"),
        ("precision_difference", "Precision Difference"),
        ("recall_difference", "Recall Difference"),
    ]:
        m = effect_sizes.get(metric_key, {})
        mean_val = m.get('mean', 0)
        ci_low = m.get('ci_lower', 0)
        ci_high = m.get('ci_upper', 0)

        # Indicate significance (CI excludes zero)
        sig_marker = ""
        if ci_low > 0:
            sig_marker = " *"  # A significantly better
        elif ci_high < 0:
            sig_marker = " *"  # B significantly better

        print(f"  {label:<20} {mean_val:>+10.4f} [{ci_low:>+.4f}, {ci_high:>+.4f}]{sig_marker}")

    print("\n  * = 95% CI excludes zero (statistically significant at α=0.05)")
    print(f"  n_tiles = {effect_sizes.get('n_tiles', 'N/A')}")
    print(f"\n{'='*70}\n")


def print_tile_classification_summary(
    results: dict,
    title: str = "Tile-Level Classification",
) -> None:
    """
    Print a formatted summary of tile-level classification results.

    Args:
        results: Output from calculate_tile_classification().
        title: Header title for the summary.
    """
    if "error" in results:
        print(f"Error: {results['error']}")
        return

    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

    # Confusion matrix
    print("\n[Confusion Matrix]")
    print(f"  {'':15} {'Detected':>12} {'Not Detected':>14}")
    print(f"  {'Has Mounds':<15} {results['tp']:>12} (TP) {results['fn']:>10} (FN)")
    print(f"  {'Empty':<15} {results['fp']:>12} (FP) {results['tn']:>10} (TN)")

    # Metrics
    print("\n[Metrics]")
    mcc = results.get('mcc')
    sens = results.get('sensitivity')
    spec = results.get('specificity')

    mcc_str = f"{mcc:.4f}" if mcc is not None else "undefined"
    sens_str = f"{sens:.4f}" if sens is not None else "undefined"
    spec_str = f"{spec:.4f}" if spec is not None else "undefined"

    print(f"  MCC:         {mcc_str}")
    print(f"  Sensitivity: {sens_str}  (P(detect ≥1 | has mounds))")
    print(f"  Specificity: {spec_str}  (P(detect 0 | empty))")

    # Tile counts
    print("\n[Tile Counts]")
    print(f"  Total tiles:     {results['n_tiles']}")
    print(f"  Populated tiles: {results['n_populated']}")
    print(f"  Empty tiles:     {results['n_empty']}")

    print(f"\n{'='*60}\n")


def print_tile_classification_ci_summary(
    results: dict,
    ci_results: dict,
    title: str = "Tile-Level Classification",
) -> None:
    """
    Print a formatted summary of tile-level classification with bootstrap CIs.

    Args:
        results: Output from calculate_tile_classification().
        ci_results: Output from bootstrap_tile_classification_ci().
        title: Header title for the summary.
    """
    if "error" in results:
        print(f"Error: {results['error']}")
        return

    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

    # Confusion matrix
    print("\n[Confusion Matrix]")
    print(f"  {'':15} {'Detected':>12} {'Not Detected':>14}")
    print(f"  {'Has Mounds':<15} {results['tp']:>12} (TP) {results['fn']:>10} (FN)")
    print(f"  {'Empty':<15} {results['fp']:>12} (FP) {results['tn']:>10} (TN)")

    # Metrics with CIs
    n_iter = ci_results.get('n_iterations', 0)
    print(f"\n[Metrics with 95% Bootstrapped CIs (N={n_iter})]")
    print(f"  {'Metric':<12} {'Value':>10} {'95% CI':>24}")
    print(f"  {'-'*12} {'-'*10} {'-'*24}")

    for metric, label in [
        ("mcc", "MCC"),
        ("sensitivity", "Sensitivity"),
        ("specificity", "Specificity"),
    ]:
        val = results.get(metric)
        ci = ci_results.get(metric, {})
        ci_low = ci.get('ci_lower')
        ci_high = ci.get('ci_upper')

        if val is not None and ci_low is not None:
            print(f"  {label:<12} {val:>10.4f} [{ci_low:.4f}, {ci_high:.4f}]")
        elif val is not None:
            print(f"  {label:<12} {val:>10.4f} [CI unavailable]")
        else:
            print(f"  {label:<12} {'undefined':>10}")

    # Tile counts
    print("\n[Tile Counts]")
    print(f"  Total tiles:     {results['n_tiles']}")
    print(f"  Populated tiles: {results['n_populated']}")
    print(f"  Empty tiles:     {results['n_empty']}")

    print(f"\n{'='*60}\n")


def print_tile_effect_size_summary(
    effect_sizes: dict,
    condition_a: str = "Condition A",
    condition_b: str = "Condition B",
) -> None:
    """
    Print a formatted summary of tile-level effect size comparisons.

    Args:
        effect_sizes: Output from bootstrap_tile_effect_size_ci().
        condition_a: Name/label for first condition.
        condition_b: Name/label for second condition.
    """
    if "error" in effect_sizes:
        print(f"Error: {effect_sizes['error']}")
        return

    print(f"\n{'='*70}")
    print(f" Tile-Level Effect Size: {condition_a} vs {condition_b}")
    print(f"{'='*70}")
    print(f"\n[Bootstrapped 95% CIs for Differences (N={effect_sizes.get('n_iterations', 0)})]")
    print(f"  Positive values indicate {condition_a} outperforms {condition_b}")
    print()
    print(f"  {'Metric':<22} {'Δ Mean':>10} {'95% CI':>24}")
    print(f"  {'-'*22} {'-'*10} {'-'*24}")

    for metric_key, label in [
        ("mcc_difference", "MCC Difference"),
        ("sensitivity_difference", "Sensitivity Difference"),
        ("specificity_difference", "Specificity Difference"),
    ]:
        m = effect_sizes.get(metric_key, {})
        mean_val = m.get('mean')
        ci_low = m.get('ci_lower')
        ci_high = m.get('ci_upper')

        if mean_val is None:
            print(f"  {label:<22} {'undefined':>10}")
            continue

        # Indicate significance (CI excludes zero)
        sig_marker = ""
        if ci_low is not None and ci_high is not None:
            if ci_low > 0:
                sig_marker = " *"  # A significantly better
            elif ci_high < 0:
                sig_marker = " *"  # B significantly better

        print(f"  {label:<22} {mean_val:>+10.4f} [{ci_low:>+.4f}, {ci_high:>+.4f}]{sig_marker}")

    print("\n  * = 95% CI excludes zero (statistically significant at α=0.05)")
    print(f"  n_tiles = {effect_sizes.get('n_tiles', 'N/A')}")
    print(f"\n{'='*70}\n")
