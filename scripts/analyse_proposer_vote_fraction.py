#!/usr/bin/env python3
"""
Proposer Vote-Fraction Analysis (Item H-a)
==========================================

Behavioural-confidence proxy analysis for the Phase 3a proposer matrix.

The Phase 3a proposer (Gemini Flash 3) does not emit a numeric
``mound_probability`` — its required JSON schema is
``{box_2d, label, subtype}`` and the ``confidence: "high"`` string
seen in detection GeoJSONs is hard-coded by the detection pipeline
(``scripts/4_detect_mounds_batch.py`` ~line 627). There are no
logprobs captured. A literal "proposer confidence distribution" is
therefore vacuous on existing artefacts.

This script measures the strongest available **behavioural** proxy
for proposer confidence: the per-clustered-candidate **vote
fraction** (``vote_count / K``), where ``K`` is the number of
independent VLM passes and ``vote_count`` is the number of distinct
passes contributing to a 20 m spatial cluster. This is the
proposer's empirical agreement-rate distribution and is the closest
available analogue to a per-detection probability.

Key metrics per stratum (Era × {Image,Text} × Architecture × T ∈
{0.0, 0.3, 0.7, 1.0} × {MIN, HIGH}):

    a. Vote-fraction distribution per clustered candidate
    b. Per-tile detection-count distribution (skew, kurtosis, modes)
    c. Quantisation level + entropy + mass at extremes
    d. Subtype distribution as a secondary proxy
    e. Distribution-shape descriptors (Hartigan's dip; mean-shift modes)

A side-by-side comparison with verifier ``mound_probability``
calibration bin counts (Obs 269 / 277) tests whether the bimodality
observed in the verifier is also present in proposer behaviour
(system property) or only in the verifier (verifier-specific).

Usage::

    python scripts/analyse_proposer_vote_fraction.py \\
        --output-dir results/proposer-vote-fraction/

Inputs:
    - Per-run detection GeoJSONs in
      ``outputs/h11/pv-diag-384/<arch>/<modality>-t<T>/run_*/``
      and ``outputs/h11/n1-outstanding-384/image-t0/run_*/``.
    - Tile bounds: ``inputs/vectors/bounds/384/full_evaluation_bounds.geojson``.
    - Verifier calibration bins:
      ``results/verifier-calibration-matrix/<pool-variant>/calibration.json``.

Outputs (under ``--output-dir``):
    - ``vote_fraction.json`` — per-stratum descriptors + bin counts.
    - ``report.md`` — schema-absence caveat, descriptor table,
      figures, and discussion of the bimodality bottleneck question.
    - ``figures/vote_fraction_panels.png`` — 6-panel matrix-corners
      figure.
    - ``figures/proposer_vs_verifier_bimodality.png`` — side-by-side
      proposer vote-fraction vs verifier calibration-bin counts.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-27
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.signal import find_peaks

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

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

DEFAULT_BOUNDS = (
    PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "results/proposer-vote-fraction"

# 16-stratum Phase 3a registry: 2 modalities × 2 thinking × 4 temperatures.
# Image registry mirrors ``analyse_secondary_effects.CONDITION_REGISTRY``;
# text registry mirrors ``analyse_secondary_effects_text.CONDITION_REGISTRY``.
# Architecture is fixed (Gemini-3-Flash) and Era is "Phase 3a / 487 tiles".
CONDITION_REGISTRY: dict[str, dict] = {
    # ---- Image track ----
    "image-HIGH-T0.0": {
        "modality": "image", "thinking": "HIGH", "temperature": 0.0, "K": 3,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0",
    },
    "image-HIGH-T0.3": {
        "modality": "image", "thinking": "HIGH", "temperature": 0.3, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3",
    },
    "image-HIGH-T0.7": {
        "modality": "image", "thinking": "HIGH", "temperature": 0.7, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
    },
    "image-HIGH-T1.0": {
        "modality": "image", "thinking": "HIGH", "temperature": 1.0, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0",
    },
    "image-MIN-T0.0": {
        "modality": "image", "thinking": "MINIMAL", "temperature": 0.0, "K": 3,
        "run_dir": "outputs/h11/n1-outstanding-384/image-t0",
    },
    "image-MIN-T0.3": {
        "modality": "image", "thinking": "MINIMAL", "temperature": 0.3, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t0.3",
    },
    "image-MIN-T0.7": {
        "modality": "image", "thinking": "MINIMAL", "temperature": 0.7, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t0.7",
    },
    "image-MIN-T1.0": {
        "modality": "image", "thinking": "MINIMAL", "temperature": 1.0, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t1.0",
    },
    # ---- Text track ----
    "text-HIGH-T0.0": {
        "modality": "text", "thinking": "HIGH", "temperature": 0.0, "K": 3,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0",
    },
    "text-HIGH-T0.3": {
        "modality": "text", "thinking": "HIGH", "temperature": 0.3, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3",
    },
    "text-HIGH-T0.7": {
        "modality": "text", "thinking": "HIGH", "temperature": 0.7, "K": 30,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
    },
    "text-HIGH-T1.0": {
        "modality": "text", "thinking": "HIGH", "temperature": 1.0, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0",
    },
    "text-MIN-T0.0": {
        "modality": "text", "thinking": "MINIMAL", "temperature": 0.0, "K": 3,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.0",
    },
    "text-MIN-T0.3": {
        "modality": "text", "thinking": "MINIMAL", "temperature": 0.3, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3",
    },
    "text-MIN-T0.7": {
        "modality": "text", "thinking": "MINIMAL", "temperature": 0.7, "K": 30,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
    },
    "text-MIN-T1.0": {
        "modality": "text", "thinking": "MINIMAL", "temperature": 1.0, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0",
    },
}

# Verifier calibration matches the HIGH-T0.7 text proposer pool. Used for
# the side-by-side bimodality comparison (Obs 269 / 277).
VERIFIER_CALIBRATION_DEFAULT = (
    PROJECT_ROOT
    / "results/verifier-calibration-matrix/text-brief/calibration.json"
)
VERIFIER_PROPOSER_CONDITION = "text-HIGH-T0.7"

# Six-panel figure: matrix corners + image/text mid-T comparison.
SIX_PANEL_CONDITIONS: list[str] = [
    "image-MIN-T0.0",
    "image-HIGH-T0.0",
    "image-MIN-T1.0",
    "image-HIGH-T1.0",
    "image-HIGH-T0.7",
    "text-HIGH-T0.7",
]


# ---------------------------------------------------------------------------
# Per-condition extraction
# ---------------------------------------------------------------------------


def list_run_dirs(condition_dir: Path) -> list[Path]:
    """Return sorted ``run_*`` subdirectories under a condition directory.

    Args:
        condition_dir: Condition directory expected to contain ``run_1/``,
            ``run_2/``, ... subdirectories of per-pass detection GeoJSONs.

    Returns:
        Naturally-sorted list of ``run_*`` paths (run_1, run_2, ..., run_10).
    """
    runs = [p for p in condition_dir.glob("run_*") if p.is_dir()]
    # Natural sort: extract trailing integer from "run_<N>".
    runs.sort(key=lambda p: int(p.name.split("_")[-1]))
    return runs


def _load_run_features(run_dir: Path) -> list[dict]:
    """Load features from every per-pass detection GeoJSON in a run dir.

    The Phase 3a corpus uses two filename conventions interchangeably:
    ``detections_<condition>_run<NN>.geojson`` (image-n5, n1-outstanding)
    and ``detections-<library>-<arch>-<date>.geojson`` (flash-high-text-n5,
    flash-high-image-n5). Both are resolved by
    ``lib_detection_paths.find_pass_geojsons``, which also excludes the
    ``.meta.json`` / ``.tiles.json`` side-files; the local glob this
    function used to carry is therefore obsolete.

    Args:
        run_dir: Path to a per-pass run directory.

    Returns:
        Combined list of GeoJSON features from every detection file in
        the directory.
    """
    features: list[dict] = []
    for path in find_pass_geojsons(run_dir):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            logger.warning("Could not parse %s: %s", path, exc)
            continue
        features.extend(data.get("features", []))
    return features


def load_pass_detections(
    condition_dir: Path,
) -> tuple[dict[str, list[dict]], list[dict]]:
    """Load and deduplicate per-pass detections for a condition.

    Loads every per-pass detection GeoJSON (both naming conventions, via
    ``lib_detection_paths``) from each ``run_*/`` directory,
    deduplicates within-pass at 20 m, and returns:

    1. ``pass_detections``: mapping from run name to deduplicated
       detection dicts (input to ``cluster_across_passes``).
    2. ``raw_features``: the un-deduplicated raw feature list across all
       passes — used for subtype extraction and per-tile-per-pass counts.

    Args:
        condition_dir: Path to a Phase 3a condition directory containing
            ``run_*/`` subdirectories.

    Returns:
        Tuple of (pass_detections, raw_features).
    """
    pass_detections: dict[str, list[dict]] = {}
    raw_features: list[dict] = []
    for run_dir in list_run_dirs(condition_dir):
        features = _load_run_features(run_dir)
        if not features:
            logger.warning("No features in %s", run_dir)
            continue
        # Tag each raw feature with its run name so per-pass-per-tile
        # counts can be reconstructed downstream without re-globbing.
        for f in features:
            props = f.setdefault("properties", {})
            props["__run"] = run_dir.name
        raw_features.extend(features)
        pass_detections[run_dir.name] = deduplicate_within_pass(features)
    return pass_detections, raw_features


def per_tile_detection_counts(
    raw_features: list[dict],
    gdf_bounds: gpd.GeoDataFrame,
) -> np.ndarray:
    """Compute per-tile-per-pass detection counts.

    For every (run, tile) pair, count the number of raw detections whose
    ``source_tile`` property matches that tile. Tiles with no detections
    contribute zeros, ensuring the resulting distribution reflects the
    full evaluation scope rather than only "active" tiles.

    Args:
        raw_features: Raw GeoJSON features tagged with ``__run`` in
            ``properties`` (set by ``load_pass_detections``).
        gdf_bounds: Tile bounds GeoDataFrame; provides the canonical
            tile name list (e.g., 487 tiles for Phase 3a).

    Returns:
        Flat NumPy array of length ``n_passes × n_tiles`` containing
        per-pass-per-tile detection counts.
    """
    tile_names: list[str] = gdf_bounds["tile_name"].tolist()
    runs: list[str] = sorted(
        {f["properties"].get("__run", "unknown") for f in raw_features}
    )
    if not runs:
        return np.array([], dtype=int)

    # Group features by run, then tally per tile via Counter.
    counts_matrix = np.zeros((len(runs), len(tile_names)), dtype=int)
    tile_index = {name: i for i, name in enumerate(tile_names)}
    run_index = {name: i for i, name in enumerate(runs)}

    for f in raw_features:
        props = f.get("properties", {})
        tile = props.get("source_tile") or props.get("tile_id")
        run = props.get("__run", "unknown")
        if tile in tile_index and run in run_index:
            counts_matrix[run_index[run], tile_index[tile]] += 1

    return counts_matrix.flatten()


# ---------------------------------------------------------------------------
# Distribution descriptors
# ---------------------------------------------------------------------------


def shannon_entropy(values: np.ndarray) -> float:
    """Shannon entropy (in bits) of a discrete value array.

    Treats every distinct value as a category and computes
    ``-sum(p_i log2 p_i)``.

    Args:
        values: 1-D array of (potentially repeated) discrete values.

    Returns:
        Entropy in bits (0.0 for empty or constant arrays).
    """
    if values.size == 0:
        return 0.0
    counts = np.array(list(Counter(values).values()), dtype=float)
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log2(probs)))


def hartigan_dip(values: np.ndarray) -> tuple[float, float]:
    """Hartigan's dip statistic and p-value, with graceful fallback.

    The dip statistic measures departure from unimodality; small dip
    values mean unimodal, larger dips suggest multi-modality. The
    p-value is computed via the bootstrap procedure provided by the
    ``diptest`` package.

    Args:
        values: 1-D array of continuous (or fine-grained discrete)
            values. Must contain at least 4 elements for a meaningful
            test.

    Returns:
        Tuple of (dip_statistic, p_value). Returns (0.0, 1.0) if the
        ``diptest`` package is not installed or the input is too small.
    """
    if values.size < 4:
        return 0.0, 1.0
    try:
        import diptest  # type: ignore[import-untyped]

        dip, pval = diptest.diptest(values.astype(float))
        return float(dip), float(pval)
    except ImportError:
        logger.warning("diptest not installed; returning (0.0, 1.0)")
        return 0.0, 1.0


def mean_shift_modes(
    values: np.ndarray,
    quantile: float = 0.2,
) -> int:
    """Count distinct modes via mean-shift clustering with a Silverman bandwidth.

    Uses scikit-learn's ``MeanShift`` with bandwidth estimated via
    ``estimate_bandwidth`` at the supplied quantile. Falls back to a
    simple peak count on a histogram if scikit-learn is unavailable.

    Args:
        values: 1-D array of continuous values.
        quantile: Quantile used by ``estimate_bandwidth`` (default 0.2).

    Returns:
        Number of modes (cluster centres) found. Returns 1 for empty,
        constant, or trivially small inputs.
    """
    values = values.astype(float)
    if values.size < 8 or float(values.std()) == 0.0:
        return 1
    try:
        from sklearn.cluster import MeanShift, estimate_bandwidth

        bw = estimate_bandwidth(values.reshape(-1, 1), quantile=quantile)
        if bw is None or bw <= 0:
            return 1
        ms = MeanShift(bandwidth=bw, bin_seeding=True)
        ms.fit(values.reshape(-1, 1))
        return int(len(np.unique(ms.labels_)))
    except (ImportError, ValueError):
        # Fallback: count peaks on a 30-bin histogram.
        hist, _ = np.histogram(values, bins=30)
        peaks, _ = find_peaks(hist)
        return max(1, int(peaks.size))


def descriptor_summary(
    vote_fractions: np.ndarray,
    tile_dets: np.ndarray,
    K: int,
    n_distinct_quanta: int,
) -> dict:
    """Compile per-condition descriptor statistics.

    Args:
        vote_fractions: Array of vote-count / K values, one per
            clustered candidate.
        tile_dets: Flat array of per-tile-per-pass detection counts.
        K: Number of independent VLM passes for this condition.
        n_distinct_quanta: Distinct vote-count integer values observed
            (bounded above by ``K``).

    Returns:
        Dict of descriptor metrics suitable for JSON serialisation.
    """
    vf = vote_fractions
    n = int(vf.size)

    if n == 0:
        return {
            "n_candidates": 0,
            "n_distinct_vote_fractions": 0,
            "entropy_bits": 0.0,
            "mass_at_one_over_K": 0.0,
            "mass_at_K_over_K": 0.0,
            "vf_skew": 0.0,
            "vf_kurtosis": 0.0,
            "dip_statistic": 0.0,
            "dip_p_value": 1.0,
            "tile_dets_mean": 0.0,
            "tile_dets_sd": 0.0,
            "tile_dets_skew": 0.0,
            "tile_dets_kurtosis": 0.0,
            "tile_dets_modes": 0,
            "tile_dets_n": 0,
        }

    one_over_k = 1.0 / K
    mass_low = float(np.mean(np.isclose(vf, one_over_k)))
    mass_high = float(np.mean(np.isclose(vf, 1.0)))
    # Compute dip statistic + p-value once (the bootstrap p-value is the
    # expensive part of ``diptest.diptest``).
    dip_stat, dip_pval = hartigan_dip(vf)

    return {
        "n_candidates": n,
        "n_distinct_vote_fractions": n_distinct_quanta,
        "entropy_bits": shannon_entropy(vf),
        "mass_at_one_over_K": round(mass_low, 4),
        "mass_at_K_over_K": round(mass_high, 4),
        "vf_skew": (
            float(stats.skew(vf, bias=False)) if n >= 3 else 0.0
        ),
        "vf_kurtosis": (
            float(stats.kurtosis(vf, bias=False, fisher=True))
            if n >= 4 else 0.0
        ),
        "dip_statistic": dip_stat,
        "dip_p_value": dip_pval,
        "tile_dets_mean": (
            float(np.mean(tile_dets)) if tile_dets.size else 0.0
        ),
        "tile_dets_sd": (
            float(np.std(tile_dets, ddof=1))
            if tile_dets.size >= 2 else 0.0
        ),
        "tile_dets_skew": (
            float(stats.skew(tile_dets, bias=False))
            if tile_dets.size >= 3 else 0.0
        ),
        "tile_dets_kurtosis": (
            float(stats.kurtosis(tile_dets, bias=False, fisher=True))
            if tile_dets.size >= 4 else 0.0
        ),
        "tile_dets_modes": mean_shift_modes(tile_dets),
        "tile_dets_n": int(tile_dets.size),
    }


# ---------------------------------------------------------------------------
# Per-condition driver
# ---------------------------------------------------------------------------


def analyse_condition(
    condition_id: str,
    cfg: dict,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict:
    """Run vote-fraction and per-tile analysis for a single condition.

    Args:
        condition_id: Condition key (e.g., ``image-HIGH-T0.0``).
        cfg: Registry entry providing ``run_dir`` and ``K``.
        gdf_bounds: Tile bounds GeoDataFrame (487 tiles).

    Returns:
        Per-condition result dict (descriptors + raw arrays for
        downstream plotting).
    """
    run_dir = PROJECT_ROOT / cfg["run_dir"]
    K = cfg["K"]
    logger.info("=== %s (K=%d) ===", condition_id, K)
    logger.info("  run_dir: %s", run_dir)

    if not run_dir.exists():
        logger.error("Missing condition directory: %s", run_dir)
        return {
            "condition": condition_id,
            **cfg,
            "status": "missing",
            "descriptors": descriptor_summary(
                np.array([]), np.array([]), K, 0,
            ),
        }

    pass_detections, raw_features = load_pass_detections(run_dir)
    if not pass_detections:
        logger.error("No per-pass detections under %s", run_dir)
        return {
            "condition": condition_id,
            **cfg,
            "status": "no-data",
            "descriptors": descriptor_summary(
                np.array([]), np.array([]), K, 0,
            ),
        }

    # Cluster across passes at 20 m; vote_count counts distinct passes.
    clusters = cluster_across_passes(pass_detections)
    vote_counts = np.array(
        [c["vote_count"] for c in clusters], dtype=int,
    )
    vote_fractions = vote_counts.astype(float) / float(K)
    n_distinct_quanta = int(np.unique(vote_counts).size)

    tile_dets = per_tile_detection_counts(raw_features, gdf_bounds)
    # Some legacy detection features carry an explicit ``subtype: null``
    # rather than omitting the key, so a plain ``.get(..., "unknown")``
    # would still return ``None``. Coerce explicitly.
    subtypes = Counter(
        (f.get("properties", {}).get("subtype") or "unknown")
        for f in raw_features
    )

    # Histogram bins for vote-count integers (1..K) and per-tile dets.
    vote_count_hist = {
        str(int(k)): int(np.sum(vote_counts == int(k)))
        for k in range(1, K + 1)
    }
    tile_dets_hist_bins = list(range(0, int(tile_dets.max() or 0) + 2))
    tile_dets_hist = {
        str(int(b)): int(np.sum(tile_dets == int(b)))
        for b in tile_dets_hist_bins
    }

    descriptors = descriptor_summary(
        vote_fractions, tile_dets, K, n_distinct_quanta,
    )

    return {
        "condition": condition_id,
        "modality": cfg["modality"],
        "thinking": cfg["thinking"],
        "temperature": cfg["temperature"],
        "K": K,
        "run_dir": str(cfg["run_dir"]),
        "status": "ok",
        "descriptors": descriptors,
        "vote_count_histogram": vote_count_hist,
        "tile_dets_histogram": tile_dets_hist,
        "subtype_counts": dict(subtypes),
        "_arrays": {
            # Stashed for plotting; not serialised to JSON.
            "vote_fractions": vote_fractions,
            "tile_dets": tile_dets,
        },
    }


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------


def plot_six_panel(
    results: dict[str, dict],
    out_path: Path,
) -> None:
    """Produce the 6-panel matrix-corners figure.

    Top row: vote-fraction histograms (with KDE overlay); bottom row:
    per-tile detection-count KDEs. Columns correspond to
    ``SIX_PANEL_CONDITIONS``.

    Args:
        results: Per-condition results dict from ``analyse_condition``.
        out_path: Destination PNG path.
    """
    fig, axes = plt.subplots(
        2, len(SIX_PANEL_CONDITIONS),
        figsize=(3 * len(SIX_PANEL_CONDITIONS), 6),
        sharey="row",
    )

    for col, cid in enumerate(SIX_PANEL_CONDITIONS):
        res = results.get(cid)
        if res is None or res.get("status") != "ok":
            for row in (0, 1):
                axes[row, col].text(
                    0.5, 0.5, f"{cid}\n(no data)",
                    ha="center", va="center",
                    transform=axes[row, col].transAxes,
                )
                axes[row, col].set_xticks([])
                axes[row, col].set_yticks([])
            continue

        vf = res["_arrays"]["vote_fractions"]
        td = res["_arrays"]["tile_dets"]
        K = res["K"]

        # Top: vote-fraction histogram with KDE overlay (if non-degenerate).
        ax_top = axes[0, col]
        if vf.size:
            bins = np.linspace(0, 1, K + 2)
            ax_top.hist(
                vf, bins=bins, density=True,
                color="steelblue", edgecolor="white", alpha=0.85,
            )
            if vf.size >= 3 and float(vf.std()) > 0:
                try:
                    kde = stats.gaussian_kde(vf)
                    grid = np.linspace(0, 1, 200)
                    ax_top.plot(grid, kde(grid), color="black", lw=1.2)
                except np.linalg.LinAlgError:
                    pass
        ax_top.set_xlim(0, 1.05)
        ax_top.set_title(f"{cid}\nK={K}, n={vf.size}", fontsize=10)
        if col == 0:
            ax_top.set_ylabel("vote-fraction\ndensity")

        # Bottom: per-tile detection-count KDE.
        ax_bot = axes[1, col]
        if td.size and float(td.std()) > 0:
            try:
                kde = stats.gaussian_kde(td)
                grid = np.linspace(td.min(), td.max(), 200)
                ax_bot.plot(grid, kde(grid), color="firebrick", lw=1.4)
                ax_bot.fill_between(
                    grid, kde(grid), color="firebrick", alpha=0.3,
                )
            except np.linalg.LinAlgError:
                pass
        ax_bot.set_xlabel("dets / tile / pass")
        if col == 0:
            ax_bot.set_ylabel("density")

    fig.suptitle(
        "Proposer behavioural-confidence proxies — Phase 3a matrix corners",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info("Wrote %s", out_path)


def plot_proposer_vs_verifier(
    proposer_result: dict,
    verifier_calibration: dict,
    out_path: Path,
) -> None:
    """Produce the proposer-vs-verifier bimodality side-by-side figure.

    Left axis: proposer vote-fraction histogram for the matched
    HIGH-T0.7 text condition (or the user-supplied substrate).
    Right axis: verifier ``mound_probability`` calibration-bin counts
    drawn from ``calibration.json`` (Obs 269 / 277).

    Args:
        proposer_result: Per-condition result dict for the matched
            condition (must contain ``_arrays.vote_fractions``).
        verifier_calibration: Parsed ``calibration.json`` content.
        out_path: Destination PNG path.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # Proposer panel.
    ax_p = axes[0]
    vf = proposer_result["_arrays"]["vote_fractions"]
    K = proposer_result["K"]
    bins = np.linspace(0, 1, K + 2)
    ax_p.hist(
        vf, bins=bins, color="steelblue", edgecolor="white", alpha=0.85,
    )
    ax_p.set_xlim(0, 1.05)
    ax_p.set_xlabel("proposer vote fraction (vote_count / K)")
    ax_p.set_ylabel("clustered candidates")
    ax_p.set_title(
        f"Proposer — {proposer_result['condition']} (K={K})",
        fontsize=11,
    )

    # Verifier panel.
    ax_v = axes[1]
    bins_meta = verifier_calibration.get("calibration_bins", [])
    los = [b["lo"] for b in bins_meta]
    his = [b["hi"] for b in bins_meta]
    counts = [b["count"] for b in bins_meta]
    centres = [(lo + hi) / 2 for lo, hi in zip(los, his, strict=False)]
    widths = [hi - lo for lo, hi in zip(los, his, strict=False)]
    ax_v.bar(
        centres, counts, width=widths,
        align="center", color="firebrick", edgecolor="white", alpha=0.85,
    )
    ax_v.set_xlim(0, 1.05)
    ax_v.set_xlabel("verifier mound_probability")
    ax_v.set_ylabel("verifications")
    pool = verifier_calibration.get("pool", "?")
    variant = verifier_calibration.get("variant", "?")
    n_total = verifier_calibration.get("n_total", "?")
    ax_v.set_title(
        f"Verifier — {pool}-{variant} (n={n_total}, Obs 269/277)",
        fontsize=11,
    )

    fig.suptitle(
        "Proposer vote-fraction vs. verifier mound_probability "
        "(bimodality bottleneck check)",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info("Wrote %s", out_path)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def render_descriptor_table(results: dict[str, dict]) -> str:
    """Render a Markdown descriptor table (one row per condition).

    Args:
        results: Per-condition results dict.

    Returns:
        Multi-line Markdown table string.
    """
    header = (
        "| condition | K | n_cand | n_distinct | H(bits) | mass@1/K | "
        "mass@K/K | skew | kurt | dip | dip-p | "
        "dets/tile mean | dets/tile sd | dets/tile modes |"
    )
    sep = (
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
    )
    lines = [header, sep]
    for cid, res in results.items():
        d = res.get("descriptors", {})
        lines.append(
            "| {cid} | {K} | {n} | {nd} | {h:.2f} | {ml:.2f} | {mh:.2f} "
            "| {sk:.2f} | {kt:.2f} | {dp:.3f} | {pp:.3f} "
            "| {tm:.2f} | {ts:.2f} | {mo} |".format(
                cid=cid, K=res.get("K", 0),
                n=d.get("n_candidates", 0),
                nd=d.get("n_distinct_vote_fractions", 0),
                h=d.get("entropy_bits", 0.0),
                ml=d.get("mass_at_one_over_K", 0.0),
                mh=d.get("mass_at_K_over_K", 0.0),
                sk=d.get("vf_skew", 0.0),
                kt=d.get("vf_kurtosis", 0.0),
                dp=d.get("dip_statistic", 0.0),
                pp=d.get("dip_p_value", 1.0),
                tm=d.get("tile_dets_mean", 0.0),
                ts=d.get("tile_dets_sd", 0.0),
                mo=d.get("tile_dets_modes", 0),
            )
        )
    return "\n".join(lines)


def render_marginal_pivots(results: dict[str, dict]) -> str:
    """Stratified pivots: marginal effect of T (within thinking × modality).

    Returns a compact Markdown summary highlighting how mean entropy
    and mean mass-at-K/K change as T sweeps within each
    ``(modality, thinking)`` cell — i.e., does sampling diversity at
    higher T flatten the proposer's confidence proxy?

    Args:
        results: Per-condition results dict.

    Returns:
        Markdown text.
    """
    rows: list[str] = [
        "| modality | thinking | T | H(bits) | mass@K/K | "
        "mass@1/K | n_cand | dip-p |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cid, res in results.items():
        if res.get("status") != "ok":
            continue
        d = res["descriptors"]
        rows.append(
            f"| {res['modality']} | {res['thinking']} "
            f"| {res['temperature']:.1f} "
            f"| {d['entropy_bits']:.2f} "
            f"| {d['mass_at_K_over_K']:.2f} "
            f"| {d['mass_at_one_over_K']:.2f} "
            f"| {d['n_candidates']} "
            f"| {d['dip_p_value']:.3f} |"
        )
    return "\n".join(rows)


def render_bimodality_discussion(
    proposer_result: dict | None,
    verifier_calibration: dict | None,
) -> str:
    """Render the bimodality bottleneck discussion paragraph.

    Compares the matched proposer condition's vote-fraction distribution
    with the verifier ``mound_probability`` calibration counts and
    classifies the bimodality finding as system-wide or verifier-specific.

    Args:
        proposer_result: Per-condition result dict for the matched
            condition (or None if missing).
        verifier_calibration: Parsed ``calibration.json`` content
            (or None if missing).

    Returns:
        Markdown paragraph text.
    """
    if proposer_result is None or proposer_result.get("status") != "ok":
        return (
            "**Discussion (bimodality bottleneck)**: matched proposer "
            "condition data missing; cannot adjudicate."
        )
    if verifier_calibration is None:
        return (
            "**Discussion (bimodality bottleneck)**: verifier calibration "
            "data missing; cannot adjudicate."
        )

    d = proposer_result["descriptors"]
    n = d["n_candidates"]
    mh = d["mass_at_K_over_K"]
    ml = d["mass_at_one_over_K"]
    dip = d["dip_statistic"]
    dip_p = d["dip_p_value"]
    extreme_mass = mh + ml

    bins = verifier_calibration.get("calibration_bins", [])
    n_total = verifier_calibration.get("n_total", 0)
    if bins and n_total:
        low_count = sum(b["count"] for b in bins if b["hi"] <= 0.2)
        high_count = sum(b["count"] for b in bins if b["lo"] >= 0.8)
        v_low = low_count / n_total if n_total else 0.0
        v_high = high_count / n_total if n_total else 0.0
        v_extreme = v_low + v_high
    else:
        v_low = v_high = v_extreme = 0.0

    if extreme_mass >= 0.7 and dip_p < 0.10:
        verdict = (
            "U-shape with statistically detectable departure from "
            "unimodality. Bimodality appears to be a **system property**: "
            "the proposer commits to either singletons or near-unanimous "
            "clusters, mirroring the verifier's saturation at the tails."
        )
    elif extreme_mass >= 0.7:
        verdict = (
            "Heavy mass at vote=1 and vote=K but the dip test does not "
            "reject unimodality. Likely a **shared system tendency** "
            "rather than a verifier-only artefact, although the proxy "
            "is too coarsely quantised for a strong claim."
        )
    elif mh >= 0.5 and ml < 0.2:
        verdict = (
            "Right-skewed: proposer heavily favours high-consensus "
            "clusters with a thin singleton tail. The verifier's "
            "U-shape is not mirrored here; bimodality looks more "
            "**verifier-specific** (consistent with Obs 269/277 framing)."
        )
    else:
        verdict = (
            "Proposer vote-fraction is approximately unimodal/centred. "
            "Verifier bimodality is the **binding downstream constraint**; "
            "this supports treating Obs 269 as a verifier-specific "
            "phenomenon."
        )

    return (
        "**Discussion (bimodality bottleneck)**: For the matched "
        f"condition `{proposer_result['condition']}` (n={n} clustered "
        f"candidates, K={proposer_result['K']}), the proposer places "
        f"{mh:.2f} of mass at vote_count=K and {ml:.2f} at vote_count=1; "
        f"Hartigan's dip = {dip:.3f} (p = {dip_p:.3f}). For comparison, "
        f"the matched verifier substrate "
        f"({verifier_calibration.get('pool','?')}-"
        f"{verifier_calibration.get('variant','?')}, n="
        f"{n_total}) places {v_low:.2f} of probability mass below 0.2 "
        f"and {v_high:.2f} above 0.8 — total extreme mass "
        f"{v_extreme:.2f}. " + verdict
    )


def render_report(
    results: dict[str, dict],
    proposer_match: dict | None,
    verifier_calibration: dict | None,
    descriptor_table: str,
    pivots: str,
    six_panel_path: Path,
    side_by_side_path: Path,
) -> str:
    """Compile the final ``report.md`` content.

    Args:
        results: Per-condition results dict.
        proposer_match: Matched proposer condition for the side-by-side
            comparison (or None if missing).
        verifier_calibration: Parsed ``calibration.json`` (or None).
        descriptor_table: Pre-rendered descriptor table Markdown.
        pivots: Pre-rendered marginal-pivots table Markdown.
        six_panel_path: Path (relative to repo root) of the 6-panel
            figure.
        side_by_side_path: Path of the proposer-vs-verifier figure.

    Returns:
        Full Markdown document text.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    discussion = render_bimodality_discussion(
        proposer_match, verifier_calibration,
    )

    n_ok = sum(1 for r in results.values() if r.get("status") == "ok")
    n_total = len(results)

    # Subtype frequency-rank summary, condensed.
    subtype_lines: list[str] = []
    for cid, res in results.items():
        if res.get("status") != "ok":
            continue
        sub = res.get("subtype_counts", {})
        if not sub:
            continue
        ranked = sorted(sub.items(), key=lambda kv: -kv[1])[:3]
        rendered = ", ".join(f"{k}={v}" for k, v in ranked)
        subtype_lines.append(f"- `{cid}`: {rendered}")
    subtype_block = "\n".join(subtype_lines) if subtype_lines else "(none)"

    return (
        "# Proposer vote-fraction analysis (item H-a)\n\n"
        f"_Generated {timestamp} UTC. Conditions analysed: "
        f"{n_ok}/{n_total}._\n\n"
        "## Schema-absence caveat\n\n"
        "The Phase 3a proposer (Gemini-3-Flash) does **not** emit a "
        "numeric `mound_probability`. Its required JSON schema is "
        "`{box_2d, label, subtype}`; the `confidence: \"high\"` string "
        "in detection GeoJSONs is hard-coded by the detection pipeline "
        "(`scripts/4_detect_mounds_batch.py` ~line 627). No logprobs "
        "are captured. A literal \"proposer confidence distribution\" is "
        "therefore vacuous on existing artefacts.\n\n"
        "This report substitutes **behavioural-confidence proxies**, "
        "primarily the per-clustered-candidate **vote fraction** "
        "(vote_count / K) at 20 m, the per-tile-per-pass detection-count "
        "distribution, and the subtype distribution. Vote fraction is the "
        "proposer's empirical agreement-rate distribution and is the "
        "closest available analogue to a per-detection probability — but "
        "it is **not** a calibrated confidence score. Quantisation is "
        "bounded above by K+1 distinct values, so entropy and dip-test "
        "results should be read with K in mind.\n\n"
        "References for the verifier comparison: Obs 269 (verifier "
        "calibration is bimodal — saturated at 0–0.1 and 0.9–1.0) and "
        "Obs 277 (matrix-wide replication of the U-shape).\n\n"
        "## Descriptor table\n\n"
        f"{descriptor_table}\n\n"
        "## Marginal pivots (T within modality × thinking)\n\n"
        f"{pivots}\n\n"
        "## Subtype distribution (top-3 per condition)\n\n"
        f"{subtype_block}\n\n"
        "## Six-panel matrix-corners figure\n\n"
        f"![Vote-fraction & per-tile-dets panels](figures/{six_panel_path.name})\n\n"
        "Top row: vote-fraction histograms with KDE overlays. Bottom "
        "row: per-tile-per-pass detection-count KDEs. Columns: "
        + ", ".join(f"`{c}`" for c in SIX_PANEL_CONDITIONS)
        + ".\n\n"
        "## Proposer vs. verifier bimodality\n\n"
        f"![Proposer vs. verifier](figures/{side_by_side_path.name})\n\n"
        f"{discussion}\n\n"
        "## Caveats\n\n"
        "- **Schema absence.** As noted above; vote-fraction is a "
        "behavioural proxy, not a calibrated detector confidence.\n"
        "- **Quantisation.** Vote count is integer in [1, K]; entropy "
        "is bounded by log2(K). Comparisons across conditions with "
        "different K should normalise mentally.\n"
        "- **20 m clustering radius.** Imported unchanged from "
        "`lib_consensus.cluster_across_passes`; sensitivity to this "
        "radius is not explored here.\n"
        "- **Per-pass tagging.** The internal `__run` property added "
        "during loading is a transient analysis artefact and is not "
        "persisted to disk.\n"
        "- **Verifier substrate.** The side-by-side uses the "
        "`text-brief` verifier pool, which matches the HIGH-T0.7 text "
        "proposer pool (487 tiles). Other proposer conditions can be "
        "compared by re-running with `--proposer-condition <id>` and a "
        "matching `--verifier-calibration` path.\n"
    )


# ---------------------------------------------------------------------------
# CLI driver
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Optional command-line argument list (defaults to
            ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Proposer vote-fraction (behavioural confidence proxy) "
            "analysis for Phase 3a."
        ),
    )
    parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT,
        help="Output directory (default: %(default)s)",
    )
    parser.add_argument(
        "--bounds", type=Path, default=DEFAULT_BOUNDS,
        help="Tile bounds GeoJSON (default: %(default)s)",
    )
    parser.add_argument(
        "--verifier-calibration",
        type=Path,
        default=VERIFIER_CALIBRATION_DEFAULT,
        help=(
            "Path to a verifier calibration.json for the side-by-side "
            "comparison (default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--proposer-condition",
        default=VERIFIER_PROPOSER_CONDITION,
        help=(
            "Condition ID to use for the proposer-vs-verifier figure "
            "(default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--only", action="append", default=None,
        help="Run only the named condition(s); may be repeated.",
    )
    parser.add_argument(
        "--log-level", default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = args.output_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading bounds: %s", args.bounds)
    gdf_bounds = gpd.read_file(args.bounds)

    selected = (
        {k: v for k, v in CONDITION_REGISTRY.items() if k in args.only}
        if args.only else CONDITION_REGISTRY
    )

    results: dict[str, dict] = {}
    for cid, cfg in selected.items():
        results[cid] = analyse_condition(cid, cfg, gdf_bounds)

    # Verifier calibration (optional).
    verifier_calibration: dict | None = None
    if args.verifier_calibration and args.verifier_calibration.exists():
        with open(args.verifier_calibration, encoding="utf-8") as f:
            verifier_calibration = json.load(f)
        logger.info(
            "Loaded verifier calibration: %s", args.verifier_calibration,
        )
    else:
        logger.warning(
            "Verifier calibration not found: %s",
            args.verifier_calibration,
        )

    # ---- Figures ----
    six_panel_path = fig_dir / "vote_fraction_panels.png"
    plot_six_panel(results, six_panel_path)

    side_by_side_path = fig_dir / "proposer_vs_verifier_bimodality.png"
    proposer_match = results.get(args.proposer_condition)
    if (
        proposer_match is not None
        and proposer_match.get("status") == "ok"
        and verifier_calibration is not None
    ):
        plot_proposer_vs_verifier(
            proposer_match, verifier_calibration, side_by_side_path,
        )
    else:
        logger.warning(
            "Skipping side-by-side plot (proposer or verifier missing).",
        )

    # ---- Report ----
    descriptor_table = render_descriptor_table(results)
    pivots = render_marginal_pivots(results)
    report_md = render_report(
        results,
        proposer_match,
        verifier_calibration,
        descriptor_table,
        pivots,
        six_panel_path,
        side_by_side_path,
    )

    (args.output_dir / "report.md").write_text(report_md, encoding="utf-8")
    logger.info("Wrote %s/report.md", args.output_dir)

    # ---- JSON ----
    # Strip transient _arrays before serialisation.
    json_payload: dict[str, dict] = {
        "metadata": {
            "version": __version__,
            "generated_utc": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "bounds": str(args.bounds),
            "verifier_calibration": (
                str(args.verifier_calibration)
                if args.verifier_calibration else None
            ),
            "proposer_condition_for_side_by_side": args.proposer_condition,
            "n_conditions": len(results),
        },
        "conditions": {},
    }
    for cid, res in results.items():
        out = {k: v for k, v in res.items() if k != "_arrays"}
        json_payload["conditions"][cid] = out

    json_path = args.output_dir / "vote_fraction.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_payload, f, indent=2, sort_keys=True)
    logger.info("Wrote %s", json_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
