#!/usr/bin/env python3
"""
Subtype-classification accuracy analysis on the 4-map gold-standard subset.

Implements the analysis plan at
``planning/gold-standard-classification-accuracy-plan.md`` with the
decisions recorded in
``planning/gold-standard-classification-metrics-decisions.md``.

Primary question
----------------
Conditional on a correctly-detected mound, how often does the VLM
(Vision Language Model) assign the correct subtype? The analysis
operates on the 4-map gold-standard subset (569 expert-labelled GT
features) and the consensus-4of5 VLM output (607 features), with a
consensus-threshold sweep (3/5 / 4/5 / 5/5) for sensitivity.

Metric set
----------
- 4x4 matched-pairs confusion matrix (row- and column-normalised).
- 5x5 confusion matrix adding an ``unmatched`` (no_match) row / column.
- Per-class precision / recall / F1 with 10 000-iteration bootstrap
  95 per cent confidence intervals (CIs). Bootstrap resamples matched
  pairs stratified by map (per decision D6 / D7).
- Weighted-F1 (HEADLINE) and Macro-F1 (companion) per decision D9.
- Linearly-weighted Cohen's kappa using hierarchical weights (Level-1
  errors weight 1.0, Level-2 errors weight 0.5) plus unweighted kappa
  per D8.
- Multi-class Matthews Correlation Coefficient (MCC).
- Two-level hierarchical decomposition per D1 (Level-1: mound-family
  vs settlement; Level-2: plain burial / +benchmark / +trig within
  the mound-family).
- Per-class-pair confusion rates as counts.
- Consensus-threshold sweep (3/5, 4/5, 5/5) per D3.
- Buffer sensitivity at 20 m, 30 m, 50 m (50 m is the headline).
- Per-map diagnostic tables (raw cells, no CIs).

Sparse-class policy
-------------------
Settlement_mound has n=5 GT features on this subset. Per plan section
5, settlement F1 is NOT bootstrapped; raw numerator / denominator
fractions are reported instead. The 5 GT settlement rows are
qualitatively traced into the report.

Reproducibility
---------------
- Seed: 42 (bootstrap + any stochastic component).
- Git commit hash and input-file SHA256 logged to ``analysis.log``.
- Vocabulary mapping recorded at the top of the log.
- All bootstrap / heavy-compute must run on sapphire per CLAUDE.md.

Usage
-----
::

    python scripts/analyse_subtype_classification.py \\
        --gt-dir inputs/vectors/references/ \\
        --detections outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson \\
        --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \\
        --buffers 20 30 50 \\
        --output-dir results/gold-standard-subtype-classification/ \\
        --bootstrap-n 10000 \\
        --seed 42 \\
        --consensus-thresholds 3 4 5

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd

# Local imports — ensure scripts directory is on sys.path when invoked
# both as a script and as a module.
_SCRIPTS_DIR = Path(__file__).parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib_advanced_metrics import match_detections_to_references  # noqa: E402
from lib_consensus import ensure_utm_crs  # noqa: E402

try:
    from sklearn.metrics import cohen_kappa_score, matthews_corrcoef
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "sklearn is required for kappa / MCC metrics. Install scikit-learn.",
    ) from exc


# ── Module-level constants ────────────────────────────────────────────

__version__ = "1.0.0"

#: Target Coordinate Reference System — UTM Zone 35N covers Bulgaria.
TARGET_CRS = "EPSG:32635"

#: Canonical subtype order used for confusion-matrix rows / columns.
#: Ordered so that the hierarchical decomposition is natural:
#: the first three labels belong to the mound-family (Level-1 group 1),
#: the fourth label is settlement (Level-1 group 2).
CANONICAL_ORDER: list[str] = [
    "burial_mound",
    "benchmark_mound",
    "triangulation_mound",
    "settlement_mound",
]

#: Label used in the 5x5 confusion matrix to represent "no match
#: at the specified buffer tolerance". Placed last so the mound-family
#: block remains contiguous when the table is displayed.
NO_MATCH_LABEL = "no_match"

#: Vocabulary normalisation. Folds the case-variant ``Burial Mound``
#: to ``Burial mound`` and projects the four GT symbols onto the
#: VLM's snake_case subtype vocabulary.
GT_TO_VLM_VOCABULARY: dict[str, str] = {
    "Burial mound": "burial_mound",
    "Burial Mound": "burial_mound",  # case-variant — Rakovski (1 feature)
    "Bench mark on burial mound": "benchmark_mound",
    "Triangulation point on burial mound": "triangulation_mound",
    "Settlement mound": "settlement_mound",
}

#: Level-1 partition used for hierarchical decomposition (D1).
#: Level-1: mound-family (any burial-type compound) vs settlement.
#: The complement (settlement) is left implicit throughout.
LEVEL1_MOUND_FAMILY: set[str] = {
    "burial_mound", "benchmark_mound", "triangulation_mound",
}

#: Linearly-weighted kappa weight scheme (D8). Within the mound-family
#: (Level-2 errors) misclassifications get weight 0.5; across the
#: Level-1 boundary errors get weight 1.0.
LEVEL1_ERROR_WEIGHT: float = 1.0
LEVEL2_ERROR_WEIGHT: float = 0.5

#: Bootstrap confidence level.
CI_ALPHA: float = 0.05  # → 95 per cent CI

logger = logging.getLogger("analyse_subtype_classification")


# ── Helpers ───────────────────────────────────────────────────────────

def sha256_file(path: Path) -> str:
    """Return a hexadecimal SHA256 digest of a file's contents.

    Args:
        path: File whose bytes will be hashed.

    Returns:
        Lowercase 64-character hexadecimal digest.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit_hash(repo_root: Path) -> str:
    """Return the current HEAD commit hash (or "unknown" if unavailable).

    Args:
        repo_root: Path to the git working tree root.

    Returns:
        Short (7-char) git hash or ``"unknown"`` on failure.
    """
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def normalise_gt_symbol(symbol: str | None) -> str:
    """Map a GT ``Symbol`` string to the VLM snake_case vocabulary.

    Case-folds ``Burial Mound`` → ``Burial mound`` (Rakovski variant)
    and maps all four GT symbols to the snake_case subtype labels
    used on the VLM side. Unknown symbols raise ``KeyError`` — the
    analysis script should fail loudly if the GT vocabulary drifts.

    Args:
        symbol: The ``Symbol`` attribute of a GT feature.

    Returns:
        One of ``burial_mound`` / ``benchmark_mound`` /
        ``triangulation_mound`` / ``settlement_mound``.

    Raises:
        KeyError: If ``symbol`` is not in ``GT_TO_VLM_VOCABULARY``.
    """
    if symbol is None:
        raise KeyError("GT feature has no Symbol attribute")
    return GT_TO_VLM_VOCABULARY[symbol]


# ── Data loading ──────────────────────────────────────────────────────

def load_ground_truth(gt_dir: Path) -> gpd.GeoDataFrame:
    """Load the 4-map GT GeoJSONs and normalise the subtype column.

    Reads every ``reference_*.geojson`` file under ``gt_dir``, skipping
    the ``mounds-reference.geojson`` master file and any ``student-``
    prefixed file (both are out of scope per plan section 7.1).

    Args:
        gt_dir: Directory containing the four ``reference_*.geojson``
            files for the gold-standard maps.

    Returns:
        GeoDataFrame with columns ``[Map, Symbol, gt_subtype, geometry]``
        in ``TARGET_CRS``. Adds a derived ``gt_subtype`` column with the
        snake_case vocabulary.
    """
    paths = sorted(
        p for p in gt_dir.glob("reference_*.geojson")
        if "student" not in p.name and p.name != "mounds-reference.geojson"
    )
    if not paths:
        raise FileNotFoundError(
            f"No reference_*.geojson files under {gt_dir}",
        )

    frames: list[gpd.GeoDataFrame] = []
    for p in paths:
        gdf = gpd.read_file(p)
        gdf = ensure_utm_crs(gdf, source_label=p.name)
        # Confirm there's a Map column — all 4 GT files have one.
        if "Map" not in gdf.columns:
            raise KeyError(f"{p.name} is missing the 'Map' column")
        frames.append(gdf)

    combined = pd.concat(frames, ignore_index=True)
    # Normalise to snake_case subtype.
    combined["gt_subtype"] = combined["Symbol"].apply(normalise_gt_symbol)
    # Re-wrap into a GeoDataFrame to preserve geometry ops.
    combined = gpd.GeoDataFrame(combined, geometry="geometry", crs=TARGET_CRS)
    logger.info(
        "Loaded %d GT features across %d files; by subtype: %s",
        len(combined),
        len(paths),
        dict(Counter(combined["gt_subtype"])),
    )
    return combined


def load_detections(path: Path) -> gpd.GeoDataFrame:
    """Load a consensus detections GeoJSON with CRS correction.

    Args:
        path: Path to ``consensus-*of5.geojson``.

    Returns:
        GeoDataFrame with ``[subtype, geometry]`` (and other attribute
        columns from the file), forced to ``TARGET_CRS``.
    """
    gdf = gpd.read_file(path)
    gdf = ensure_utm_crs(gdf, source_label=path.name)
    if "subtype" not in gdf.columns:
        raise KeyError(
            f"{path.name} is missing the 'subtype' column; got "
            f"{list(gdf.columns)}",
        )
    logger.info(
        "Loaded %d detections from %s; by subtype: %s",
        len(gdf),
        path.name,
        dict(Counter(gdf["subtype"])),
    )
    return gdf


def load_bounds(path: Path) -> gpd.GeoDataFrame:
    """Load the tile-bounds GeoJSON.

    Args:
        path: Path to the full evaluation bounds GeoJSON.

    Returns:
        GeoDataFrame in ``TARGET_CRS``.
    """
    gdf = gpd.read_file(path)
    gdf = ensure_utm_crs(gdf, source_label=path.name)
    return gdf


# ── Pair-list construction ────────────────────────────────────────────

def build_pair_list(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    buffer_m: float,
) -> pd.DataFrame:
    """Build the matched + unmatched pair list for confusion-matrix analysis.

    Runs the Hungarian matcher **per map** (so detections only match GT
    from the same map) at the given buffer distance. Produces one row
    per matched pair, plus one row for each unmatched detection and
    each unmatched GT. The returned table feeds every downstream
    metric (confusion matrix, per-class F1, kappa, MCC).

    Args:
        gdf_det: Detections GeoDataFrame with at least ``subtype`` and
            a UTM ``geometry`` column.
        gdf_ref: Reference GeoDataFrame with ``gt_subtype``, ``Map``
            and UTM ``geometry``.
        buffer_m: Buffer distance in metres for Hungarian matching.

    Returns:
        DataFrame with columns
        ``[map, det_subtype, gt_subtype, distance_m, match_type,
        ref_global_idx, det_global_idx]``.
        ``match_type`` ∈ {``matched``, ``unmatched_det``,
        ``unmatched_ref``}. For unmatched detections the ``gt_subtype``
        is ``NO_MATCH_LABEL`` and ``ref_global_idx`` is -1; for
        unmatched GT the ``det_subtype`` is ``NO_MATCH_LABEL`` and
        ``det_global_idx`` is -1. The global indices are positional
        indices into the input GeoDataFrames (i.e. ``iloc``-style
        indices into ``gdf_det`` / ``gdf_ref``). Used by
        :func:`settlement_trace` to preserve GT ordering even though
        the Hungarian matcher returns pairs in detection-index order.
    """
    # Determine the map-name column on the detections side. The
    # consensus GeoJSON does not carry a Map column directly, but the
    # source tiles encode the map name. Fall back to parsing the first
    # source_tile entry per feature.
    det_maps = _infer_detection_maps(gdf_det)
    rows: list[dict[str, Any]] = []

    # Positional (iloc) indices for each feature — used to record
    # ref_global_idx / det_global_idx so downstream consumers can
    # recover the original GT / detection feature. Note these are
    # int positions, NOT pandas index labels — callers use them with
    # .iloc[].
    det_pos = np.arange(len(gdf_det))
    ref_pos = np.arange(len(gdf_ref))
    det_maps_arr = det_maps.to_numpy()
    ref_maps_arr = gdf_ref["Map"].to_numpy()

    maps = sorted(set(gdf_ref["Map"].unique()) | set(det_maps.unique()))
    for map_name in maps:
        det_mask = det_maps_arr == map_name
        ref_mask = ref_maps_arr == map_name
        det_sub = gdf_det.loc[det_mask].reset_index(drop=True)
        ref_sub = gdf_ref.loc[ref_mask].reset_index(drop=True)
        det_global_map = det_pos[det_mask]
        ref_global_map = ref_pos[ref_mask]

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(
                list(det_sub.geometry),
                list(ref_sub.geometry),
                max_distance=float(buffer_m),
            )
        )

        for d_idx, r_idx in zip(matched_det, matched_ref):
            d_geom = det_sub.geometry.iloc[d_idx]
            r_geom = ref_sub.geometry.iloc[r_idx]
            dp = d_geom.centroid if d_geom.geom_type != "Point" else d_geom
            rp = r_geom.centroid if r_geom.geom_type != "Point" else r_geom
            rows.append({
                "map": map_name,
                "det_subtype": det_sub["subtype"].iloc[d_idx],
                "gt_subtype": ref_sub["gt_subtype"].iloc[r_idx],
                "distance_m": dp.distance(rp),
                "match_type": "matched",
                "ref_global_idx": int(ref_global_map[r_idx]),
                "det_global_idx": int(det_global_map[d_idx]),
            })
        for d_idx in unmatched_det:
            rows.append({
                "map": map_name,
                "det_subtype": det_sub["subtype"].iloc[d_idx],
                "gt_subtype": NO_MATCH_LABEL,
                "distance_m": float("nan"),
                "match_type": "unmatched_det",
                "ref_global_idx": -1,
                "det_global_idx": int(det_global_map[d_idx]),
            })
        for r_idx in unmatched_ref:
            rows.append({
                "map": map_name,
                "det_subtype": NO_MATCH_LABEL,
                "gt_subtype": ref_sub["gt_subtype"].iloc[r_idx],
                "distance_m": float("nan"),
                "match_type": "unmatched_ref",
                "ref_global_idx": int(ref_global_map[r_idx]),
                "det_global_idx": -1,
            })

    return pd.DataFrame(rows)


def _infer_detection_maps(gdf_det: gpd.GeoDataFrame) -> pd.Series:
    """Derive a per-feature map name for the detections GeoDataFrame.

    The consensus GeoJSON does not carry a ``Map`` column directly.
    Each feature has a ``source_tiles`` list (tile filenames) from
    which we can infer the map name by stripping the ``_xN_yN.png``
    suffix from the first tile name.

    Args:
        gdf_det: Detections GeoDataFrame.

    Returns:
        Series indexed like ``gdf_det`` containing the inferred map
        name per feature.
    """
    def parse(tiles: Any) -> str:
        # ``tiles`` can be a list, a NumPy array, or a scalar depending
        # on whether geopandas / pyogrio deserialised it as an ndarray.
        # Avoid truthiness checks that fail on ndarrays.
        if tiles is None:
            return "unknown"
        try:
            length = len(tiles)
        except TypeError:
            length = 1
        if length == 0:
            return "unknown"
        if isinstance(tiles, (list, tuple, np.ndarray)):
            first = tiles[0]
        else:
            first = tiles
        # Expected tile-name format: "<MAP>_xNN_yNN.png". Strip the
        # trailing coordinate + extension pair.
        stem = Path(str(first)).stem  # drop ".png"
        parts = stem.split("_")
        # Drop trailing x? and y? tokens (could be 1 or 2 tokens each).
        while parts and parts[-1].startswith(("x", "y")):
            parts.pop()
        return "_".join(parts)

    if "source_tiles" in gdf_det.columns:
        return gdf_det["source_tiles"].apply(parse)
    # Fallback: all points land on one unknown map.
    return pd.Series(["unknown"] * len(gdf_det), index=gdf_det.index)


# ── Confusion matrix / metrics ────────────────────────────────────────

def build_confusion_matrix(
    pair_list: pd.DataFrame,
    mode: str = "4x4",
) -> pd.DataFrame:
    """Build a confusion matrix from the pair list.

    Args:
        pair_list: Output of :func:`build_pair_list`.
        mode: ``"4x4"`` for matched pairs only; ``"5x5"`` to add the
            ``no_match`` pseudo-class as a row (for GT with no matched
            detection) and a column (for detections with no matched GT).

    Returns:
        Pandas DataFrame with GT subtypes as the index, predicted
        subtypes as the columns, and counts in the cells. Indexed in
        ``CANONICAL_ORDER`` (with ``no_match`` last for ``5x5``).
    """
    if mode == "4x4":
        sub = pair_list[pair_list["match_type"] == "matched"]
        labels = CANONICAL_ORDER
    elif mode == "5x5":
        sub = pair_list
        labels = CANONICAL_ORDER + [NO_MATCH_LABEL]
    else:
        raise ValueError(f"Unknown mode: {mode}")

    counts = (
        sub.groupby(["gt_subtype", "det_subtype"]).size()
        .unstack(fill_value=0)
    )
    # Reindex for consistent ordering + ensure every label is present
    # even if the corresponding cells are zero.
    counts = counts.reindex(index=labels, columns=labels, fill_value=0)
    counts = counts.astype(int)
    counts.index.name = "gt_subtype"
    counts.columns.name = "det_subtype"
    return counts


def per_class_prf(
    pair_list: pd.DataFrame,
    labels: list[str] | None = None,
) -> dict[str, dict[str, float]]:
    """Compute per-class precision / recall / F1 on matched pairs.

    The "denominator" for recall is the number of matched pairs with
    GT == class (settlement has n=5 on the 4-map subset — beware).
    The denominator for precision is the number of matched pairs with
    det == class.

    Args:
        pair_list: Output of :func:`build_pair_list`.
        labels: List of class labels to include (default
            ``CANONICAL_ORDER``).

    Returns:
        Dict mapping class label → dict with keys
        ``{precision, recall, f1, tp, fp, fn, support}``.
        ``support`` is the matched-pair GT count (recall denominator).
    """
    if labels is None:
        labels = CANONICAL_ORDER
    matched = pair_list[pair_list["match_type"] == "matched"]
    out: dict[str, dict[str, float]] = {}
    for cls in labels:
        tp = int(((matched["gt_subtype"] == cls)
                  & (matched["det_subtype"] == cls)).sum())
        fp = int(((matched["gt_subtype"] != cls)
                  & (matched["det_subtype"] == cls)).sum())
        fn = int(((matched["gt_subtype"] == cls)
                  & (matched["det_subtype"] != cls)).sum())
        support = int((matched["gt_subtype"] == cls).sum())
        prec = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
        rec = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
        if tp + fp + fn == 0:
            f1 = float("nan")
        else:
            f1 = (
                2 * tp / (2 * tp + fp + fn)
                if (2 * tp + fp + fn) > 0 else float("nan")
            )
        out[cls] = {
            "precision": prec, "recall": rec, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn, "support": support,
        }
    return out


def summary_f1(
    pair_list: pd.DataFrame,
    labels: list[str] | None = None,
) -> dict[str, float]:
    """Compute macro-F1 and weighted-F1 across labels.

    Args:
        pair_list: Output of :func:`build_pair_list`.
        labels: Class labels to include.

    Returns:
        Dict with keys ``macro_f1``, ``weighted_f1``, ``accuracy``
        (all matched-pairs-only). ``accuracy`` = fraction of matched
        pairs where GT == detection subtype.
    """
    if labels is None:
        labels = CANONICAL_ORDER
    matched = pair_list[pair_list["match_type"] == "matched"]
    if matched.empty:
        return {
            "macro_f1": float("nan"),
            "weighted_f1": float("nan"),
            "accuracy": float("nan"),
        }
    prf = per_class_prf(pair_list, labels)
    f1s = np.array([prf[c]["f1"] for c in labels])
    supports = np.array([prf[c]["support"] for c in labels])
    # Macro-F1: unweighted mean of per-class F1 (NaN-safe).
    macro = float(np.nanmean(f1s))
    # Weighted-F1: support-weighted mean of per-class F1. NaN F1s are
    # treated as zero (common convention when a class has zero support).
    f1s_clean = np.where(np.isnan(f1s), 0.0, f1s)
    denom = supports.sum()
    weighted = float((f1s_clean * supports).sum() / denom) if denom else float("nan")
    acc = float((matched["gt_subtype"] == matched["det_subtype"]).mean())
    return {"macro_f1": macro, "weighted_f1": weighted, "accuracy": acc}


def hierarchical_decomposition(
    pair_list: pd.DataFrame,
) -> dict[str, Any]:
    """Compute the 2-level hierarchical decomposition of matched pairs.

    Level-1 partitions classes into mound-family vs settlement.
    Level-2 (conditional on matched-to-mound-family) partitions the
    mound-family into plain / +benchmark / +trig.

    Args:
        pair_list: Output of :func:`build_pair_list`.

    Returns:
        Dict with Level-1 and Level-2 breakdowns, including 2x2 and
        3x3 confusion cells, per-class precision / recall / F1, and
        an overall "flat 4-class" accuracy figure.
    """
    matched = pair_list[pair_list["match_type"] == "matched"].copy()

    def level1(label: str) -> str:
        return "mound_family" if label in LEVEL1_MOUND_FAMILY else "settlement"

    matched["gt_L1"] = matched["gt_subtype"].apply(level1)
    matched["det_L1"] = matched["det_subtype"].apply(level1)

    # Level-1 2x2 confusion
    l1_labels = ["mound_family", "settlement"]
    l1_conf = (
        matched.groupby(["gt_L1", "det_L1"]).size().unstack(fill_value=0)
        .reindex(index=l1_labels, columns=l1_labels, fill_value=0)
        .astype(int)
    )
    l1_acc = (
        float((matched["gt_L1"] == matched["det_L1"]).mean())
        if len(matched) > 0 else float("nan")
    )

    # Level-2: restricted to rows where GT is mound-family AND det is
    # mound-family (so we ask about within-family subtype accuracy
    # conditional on Level-1 being correct, i.e. "matched pairs where
    # the Level-1 partition did not itself err"). Labels are the three
    # mound-family subtypes.
    l2_labels = ["burial_mound", "benchmark_mound", "triangulation_mound"]
    l2_mask = (
        (matched["gt_L1"] == "mound_family")
        & (matched["det_L1"] == "mound_family")
    )
    matched_l2 = matched[l2_mask]
    l2_conf = (
        matched_l2.groupby(["gt_subtype", "det_subtype"]).size()
        .unstack(fill_value=0)
        .reindex(index=l2_labels, columns=l2_labels, fill_value=0)
        .astype(int)
    )
    l2_acc = (
        float((matched_l2["gt_subtype"] == matched_l2["det_subtype"]).mean())
        if len(matched_l2) > 0 else float("nan")
    )

    flat_acc = (
        float((matched["gt_subtype"] == matched["det_subtype"]).mean())
        if len(matched) > 0 else float("nan")
    )

    # Use orient="index" so outer keys are GT rows and inner keys are
    # predicted columns — the intuitive confusion-matrix orientation.
    return {
        "level1": {
            "labels": l1_labels,
            "confusion_orient": "rows=GT, columns=predicted",
            "confusion": l1_conf.to_dict(orient="index"),
            "accuracy": l1_acc,
            "n_pairs": int(len(matched)),
        },
        "level2": {
            "labels": l2_labels,
            "confusion_orient": "rows=GT, columns=predicted",
            "confusion": l2_conf.to_dict(orient="index"),
            "accuracy": l2_acc,
            "n_pairs": int(len(matched_l2)),
        },
        "flat": {
            "labels": CANONICAL_ORDER,
            "accuracy": flat_acc,
            "n_pairs": int(len(matched)),
        },
    }


def hierarchical_kappa_weights(
    labels: list[str] = CANONICAL_ORDER,
) -> np.ndarray:
    """Build a hierarchical linear-weight kappa weight matrix.

    Within-mound-family errors get weight ``LEVEL2_ERROR_WEIGHT``;
    across-Level-1 errors get weight ``LEVEL1_ERROR_WEIGHT``; diagonal
    cells get weight 0.0 (perfect-agreement).

    Args:
        labels: Class label order.

    Returns:
        Square NumPy array of shape ``(len(labels), len(labels))``
        with non-negative entries.
    """
    n = len(labels)
    w = np.zeros((n, n))
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            if i == j:
                continue
            a_family = a in LEVEL1_MOUND_FAMILY
            b_family = b in LEVEL1_MOUND_FAMILY
            if a_family == b_family:
                # Both in same family → Level-2 error
                w[i, j] = LEVEL2_ERROR_WEIGHT
            else:
                # Crosses Level-1 boundary
                w[i, j] = LEVEL1_ERROR_WEIGHT
    return w


def compute_kappa_and_mcc(
    pair_list: pd.DataFrame,
    labels: list[str] = CANONICAL_ORDER,
) -> dict[str, float]:
    """Compute unweighted + hierarchical-linearly-weighted kappa and MCC.

    Args:
        pair_list: Output of :func:`build_pair_list`.
        labels: Class label order.

    Returns:
        Dict with ``kappa_unweighted``, ``kappa_linear_hierarchical``,
        ``mcc_multi``, ``n_pairs`` (matched only).
    """
    matched = pair_list[pair_list["match_type"] == "matched"]
    if matched.empty:
        return {
            "kappa_unweighted": float("nan"),
            "kappa_linear_hierarchical": float("nan"),
            "mcc_multi": float("nan"),
            "n_pairs": 0,
        }
    y_true = matched["gt_subtype"].tolist()
    y_pred = matched["det_subtype"].tolist()
    kappa_u = float(cohen_kappa_score(y_true, y_pred, labels=labels))
    # sklearn's cohen_kappa_score supports a custom weight matrix via
    # ``weights`` argument only when set to "linear" / "quadratic".
    # For a fully custom weight matrix we compute kappa by hand.
    kappa_lin_h = _weighted_kappa(
        y_true, y_pred, labels, hierarchical_kappa_weights(labels),
    )
    mcc = float(matthews_corrcoef(y_true, y_pred))
    return {
        "kappa_unweighted": kappa_u,
        "kappa_linear_hierarchical": kappa_lin_h,
        "mcc_multi": mcc,
        "n_pairs": int(len(matched)),
    }


def _weighted_kappa(
    y_true: list[str],
    y_pred: list[str],
    labels: list[str],
    weights: np.ndarray,
) -> float:
    """Compute Cohen's kappa with an arbitrary non-negative weight matrix.

    Follows the standard generalisation: kappa = 1 - (Σ w_ij p_o_ij) /
    (Σ w_ij p_e_ij), where p_o is the observed joint distribution,
    p_e the expected distribution under independence of marginals,
    and w_ij is the weight for (true=i, pred=j).

    Args:
        y_true: True class labels.
        y_pred: Predicted class labels.
        labels: Class label order aligned to the weight matrix.
        weights: Non-negative weight matrix (``weights[i][j]`` is the
            cost of calling i as j; 0 on the diagonal).

    Returns:
        Weighted kappa (−1 … 1).
    """
    idx = {lab: i for i, lab in enumerate(labels)}
    n = len(labels)
    p_o = np.zeros((n, n))
    for t, p in zip(y_true, y_pred):
        p_o[idx[t], idx[p]] += 1
    if p_o.sum() == 0:
        return float("nan")
    p_o = p_o / p_o.sum()
    row_marg = p_o.sum(axis=1, keepdims=True)
    col_marg = p_o.sum(axis=0, keepdims=True)
    p_e = row_marg @ col_marg

    obs = (weights * p_o).sum()
    exp = (weights * p_e).sum()
    if exp == 0:
        return float("nan")
    return float(1.0 - obs / exp)


# ── Bootstrap confidence intervals ────────────────────────────────────

def bootstrap_metrics(
    pair_list: pd.DataFrame,
    n_iter: int,
    seed: int,
    labels: list[str] = CANONICAL_ORDER,
    sparse_classes: tuple[str, ...] = ("settlement_mound",),
) -> dict[str, Any]:
    """Matched-pair-level bootstrap stratified by map.

    Resamples matched pairs WITH REPLACEMENT within each map (stratified
    bootstrap). Computes per-class F1, weighted-F1, macro-F1, kappas
    and MCC on each resample. Returns percentile CIs at 95 per cent.

    Per plan section 5, ``sparse_classes`` are EXCLUDED from the
    per-class F1 bootstrap because the settlement support (n=5 on this
    subset) produces uninterpretably wide intervals. Raw numerator /
    denominator fractions are already reported by
    :func:`per_class_prf`.

    Args:
        pair_list: Output of :func:`build_pair_list`.
        n_iter: Number of bootstrap iterations (10 000 for the full run).
        seed: RNG seed for reproducibility.
        labels: Class label order.
        sparse_classes: Classes for which per-class F1 bootstrap CIs
            are suppressed.

    Returns:
        Dict of bootstrap outputs including per-class F1 CIs, summary
        F1 CIs, kappa CIs, MCC CIs, and a count of valid iterations.
    """
    matched = pair_list[pair_list["match_type"] == "matched"].copy()
    if matched.empty:
        return {"n_iter": 0, "valid_iter": 0}

    rng = np.random.default_rng(seed)
    maps = sorted(matched["map"].unique())
    per_map_idx: dict[str, np.ndarray] = {
        m: matched.index[matched["map"] == m].to_numpy() for m in maps
    }

    # Preallocate arrays — we compute kappa / MCC / weighted-F1 /
    # macro-F1 on every iteration, plus per-class F1 for the
    # non-sparse classes.
    per_class_f1: dict[str, list[float]] = {lab: [] for lab in labels}
    weighted_f1_iters: list[float] = []
    macro_f1_iters: list[float] = []
    kappa_u_iters: list[float] = []
    kappa_h_iters: list[float] = []
    mcc_iters: list[float] = []
    valid = 0

    # Weight matrix computed once.
    w_h = hierarchical_kappa_weights(labels)
    label_set = set(labels)

    for _ in range(n_iter):
        # Draw indices from each map with replacement, then concat.
        drawn: list[int] = []
        for m in maps:
            pool = per_map_idx[m]
            if len(pool) == 0:
                continue
            draws = rng.choice(pool, size=len(pool), replace=True)
            drawn.extend(draws.tolist())
        sample = matched.loc[drawn]

        # Recompute metrics on the resample.
        prf = per_class_prf(
            pair_list=pd.DataFrame({
                "match_type": "matched",
                "gt_subtype": sample["gt_subtype"].values,
                "det_subtype": sample["det_subtype"].values,
                "map": sample["map"].values,
                "distance_m": sample["distance_m"].values,
            }),
            labels=labels,
        )
        for lab in labels:
            if lab in sparse_classes:
                continue
            per_class_f1[lab].append(prf[lab]["f1"])
        f1s = np.array([prf[c]["f1"] for c in labels])
        supports = np.array([prf[c]["support"] for c in labels])
        f1s_clean = np.where(np.isnan(f1s), 0.0, f1s)
        denom = supports.sum()
        weighted_f1_iters.append(
            float((f1s_clean * supports).sum() / denom) if denom else float("nan"),
        )
        macro_f1_iters.append(float(np.nanmean(f1s)))

        # Kappa / MCC require ≥ 2 unique classes to be defined.
        y_t = sample["gt_subtype"].tolist()
        y_p = sample["det_subtype"].tolist()
        uniq = set(y_t) | set(y_p)
        if not uniq.issubset(label_set):
            # Should not happen, but be defensive.
            continue
        if len(set(y_t)) < 2:
            kappa_u_iters.append(float("nan"))
            kappa_h_iters.append(float("nan"))
            mcc_iters.append(float("nan"))
        else:
            try:
                kappa_u_iters.append(
                    float(cohen_kappa_score(y_t, y_p, labels=labels)),
                )
            except Exception:
                kappa_u_iters.append(float("nan"))
            kappa_h_iters.append(_weighted_kappa(y_t, y_p, labels, w_h))
            try:
                mcc_iters.append(float(matthews_corrcoef(y_t, y_p)))
            except Exception:
                mcc_iters.append(float("nan"))
        valid += 1

    def ci(vs: list[float]) -> tuple[float, float]:
        arr = np.array([v for v in vs if not np.isnan(v)])
        if arr.size == 0:
            return (float("nan"), float("nan"))
        lo = float(np.quantile(arr, CI_ALPHA / 2))
        hi = float(np.quantile(arr, 1.0 - CI_ALPHA / 2))
        return (lo, hi)

    out: dict[str, Any] = {
        "n_iter": int(n_iter),
        "valid_iter": int(valid),
        "per_class_f1_ci": {
            lab: (ci(per_class_f1[lab]) if lab not in sparse_classes
                  else (None, None))
            for lab in labels
        },
        "weighted_f1_ci": ci(weighted_f1_iters),
        "macro_f1_ci": ci(macro_f1_iters),
        "kappa_unweighted_ci": ci(kappa_u_iters),
        "kappa_linear_hierarchical_ci": ci(kappa_h_iters),
        "mcc_ci": ci(mcc_iters),
    }
    return out


# ── Per-map stratification ────────────────────────────────────────────

def per_map_confusion_table(pair_list: pd.DataFrame) -> pd.DataFrame:
    """Build a long-form per-map 4x4 confusion-cell table.

    Args:
        pair_list: Output of :func:`build_pair_list`.

    Returns:
        DataFrame with columns ``[map, gt_subtype, det_subtype, count]``.
        Only matched pairs are included; GT subtypes with no matches on
        a map still appear (via :func:`build_confusion_matrix` reindex).
    """
    out_frames: list[pd.DataFrame] = []
    maps = sorted(pair_list["map"].unique())
    for m in maps:
        sub = pair_list[pair_list["map"] == m]
        cm = build_confusion_matrix(sub, mode="4x4")
        cm_long = (
            cm.stack()
            .rename("count").reset_index()
        )
        cm_long["map"] = m
        out_frames.append(cm_long[["map", "gt_subtype", "det_subtype", "count"]])
    if out_frames:
        return pd.concat(out_frames, ignore_index=True)
    return pd.DataFrame(
        columns=["map", "gt_subtype", "det_subtype", "count"],
    )


def per_map_summary(pair_list: pd.DataFrame) -> pd.DataFrame:
    """Per-map weighted / macro-F1 and accuracy summary (no CIs).

    Args:
        pair_list: Output of :func:`build_pair_list`.

    Returns:
        DataFrame with columns ``[map, n_matched, accuracy, macro_f1,
        weighted_f1]``.
    """
    rows: list[dict[str, Any]] = []
    for m in sorted(pair_list["map"].unique()):
        sub = pair_list[pair_list["map"] == m]
        n_matched = int((sub["match_type"] == "matched").sum())
        summary = summary_f1(sub)
        rows.append({
            "map": m,
            "n_matched": n_matched,
            "accuracy": summary["accuracy"],
            "macro_f1": summary["macro_f1"],
            "weighted_f1": summary["weighted_f1"],
        })
    return pd.DataFrame(rows)


# ── Settlement-class qualitative trace ────────────────────────────────

def settlement_trace(
    pair_list: pd.DataFrame,
    gdf_ref: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Per-GT-feature fate trace for the sparse settlement class.

    For each GT feature of class ``settlement_mound``, record its fate
    (matched and what subtype the VLM assigned, or unmatched).

    Args:
        pair_list: Output of :func:`build_pair_list`.
        gdf_ref: GT GeoDataFrame used to report the per-feature
            ``fid`` / ``Map`` origin.

    Returns:
        DataFrame with one row per GT settlement feature, columns
        ``[map, fid, fate, predicted_subtype, distance_m]`` — ``fate``
        ∈ {``correct``, ``misclassified``, ``unmatched``}.
    """
    rows: list[dict[str, Any]] = []

    # Use ref_global_idx from the pair list to map each settlement
    # pair-list row back to the exact GT feature it came from. This
    # avoids the subtle ordering bug where the Hungarian matcher
    # returns matched pairs in detection-index order rather than
    # GT-index order — a positional zip by encounter order was
    # therefore unreliable.
    gdf_ref_reset = gdf_ref.reset_index(drop=True)
    settlement_mask = gdf_ref_reset["gt_subtype"] == "settlement_mound"
    settlement_positions = gdf_ref_reset.index[settlement_mask].tolist()

    pl_settlement = pair_list[
        (pair_list["gt_subtype"] == "settlement_mound")
        & (pair_list["ref_global_idx"] >= 0)
    ]
    # Index the settlement pair-list rows by ref_global_idx for O(1)
    # lookup (each GT feature can appear at most once, since the
    # matcher is one-to-one and unmatched_ref is exclusive with
    # matched).
    pl_by_ref_idx: dict[int, pd.Series] = {
        int(row["ref_global_idx"]): row for _, row in pl_settlement.iterrows()
    }

    for pos in settlement_positions:
        gt_row = gdf_ref_reset.iloc[pos]
        map_name = gt_row["Map"]
        fid_val = gt_row.get("fid", "N/A")
        if pos in pl_by_ref_idx:
            pr = pl_by_ref_idx[pos]
            pred = pr["det_subtype"]
            if pr["match_type"] == "unmatched_ref":
                fate = "unmatched"
                pred = NO_MATCH_LABEL
            elif pred == "settlement_mound":
                fate = "correct"
            else:
                fate = "misclassified"
            rows.append({
                "map": map_name,
                "fid": fid_val,
                "fate": fate,
                "predicted_subtype": pred,
                "distance_m": pr["distance_m"],
            })
        else:
            # GT feature not in the pair list at all — shouldn't happen
            # because build_pair_list emits a row for every ref, but be
            # defensive in case someone passes a subsetted pair list.
            rows.append({
                "map": map_name,
                "fid": fid_val,
                "fate": "missing_from_pair_list",
                "predicted_subtype": NO_MATCH_LABEL,
                "distance_m": float("nan"),
            })
    return pd.DataFrame(rows)


# ── Orchestration ─────────────────────────────────────────────────────

def run_one_threshold(
    gdf_ref: gpd.GeoDataFrame,
    gdf_det: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
    bootstrap_n: int,
    seed: int,
    headline_buffer: int = 50,
) -> dict[str, Any]:
    """Run the full classification analysis for one detections set.

    Args:
        gdf_ref: GT GeoDataFrame (already normalised).
        gdf_det: Detections GeoDataFrame (one consensus threshold).
        gdf_bounds: Tile bounds (unused here but kept for future tile-
            stratified analyses).
        buffers: Buffers to evaluate.
        bootstrap_n: Bootstrap iteration count.
        seed: RNG seed.
        headline_buffer: The buffer distance used for the headline
            metrics (confusion matrices, kappa / MCC, bootstrap).

    Returns:
        Dict with buffer-keyed results plus the pair list at the
        headline buffer (needed for the per-class F1 CSV).
    """
    del gdf_bounds  # currently unused — retained in signature for API stability
    by_buffer: dict[int, dict[str, Any]] = {}
    for buf in buffers:
        pair_list = build_pair_list(gdf_det, gdf_ref, buffer_m=float(buf))
        prf = per_class_prf(pair_list)
        summary = summary_f1(pair_list)
        hier = hierarchical_decomposition(pair_list)
        km = compute_kappa_and_mcc(pair_list)
        cm_4x4 = build_confusion_matrix(pair_list, mode="4x4")
        cm_5x5 = build_confusion_matrix(pair_list, mode="5x5")

        result: dict[str, Any] = {
            "pair_list": pair_list,
            "per_class_prf": prf,
            "summary_f1": summary,
            "hierarchical": hier,
            "kappa_mcc": km,
            "confusion_4x4": cm_4x4,
            "confusion_5x5": cm_5x5,
            "n_matched": int((pair_list["match_type"] == "matched").sum()),
            "n_unmatched_det": int((pair_list["match_type"] == "unmatched_det").sum()),
            "n_unmatched_ref": int((pair_list["match_type"] == "unmatched_ref").sum()),
        }

        if buf == headline_buffer:
            logger.info(
                "Running %d-iteration bootstrap at buffer=%d m ...",
                bootstrap_n, buf,
            )
            result["bootstrap"] = bootstrap_metrics(
                pair_list, n_iter=bootstrap_n, seed=seed,
            )
        by_buffer[buf] = result
    return by_buffer


def row_and_col_normalised(cm: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return row- and column-normalised versions of a confusion matrix.

    Zero-row or zero-column cells become NaN (honest under-defined
    normalisation). The caller may fill NaNs when writing to disk.

    Args:
        cm: Confusion matrix as counts.

    Returns:
        Tuple of (row_normalised, column_normalised) DataFrames.
    """
    row_sums = cm.sum(axis=1).replace(0, np.nan)
    col_sums = cm.sum(axis=0).replace(0, np.nan)
    row_norm = cm.div(row_sums, axis=0)
    col_norm = cm.div(col_sums, axis=1)
    return row_norm, col_norm


# ── Output writing ────────────────────────────────────────────────────

def write_confusion_matrix_csv(
    cm: pd.DataFrame,
    path: Path,
    mode_label: str,
) -> None:
    """Write a confusion matrix with raw, row- and column-normalised blocks.

    Args:
        cm: Counts matrix.
        path: Output CSV path.
        mode_label: Header-row tag (e.g. ``"raw-counts"``).
    """
    row_norm, col_norm = row_and_col_normalised(cm)
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# {mode_label}: raw counts\n")
        cm.to_csv(f)
        f.write("\n# row-normalised: P(predicted | GT) — recall view\n")
        row_norm.round(4).to_csv(f)
        f.write("\n# column-normalised: P(GT | predicted) — precision view\n")
        col_norm.round(4).to_csv(f)


def write_per_class_f1_csv(
    prf: dict[str, dict[str, float]],
    bootstrap: dict[str, Any] | None,
    path: Path,
    sparse_classes: tuple[str, ...] = ("settlement_mound",),
) -> None:
    """Write per-class precision / recall / F1 with bootstrap CIs.

    Args:
        prf: Output of :func:`per_class_prf`.
        bootstrap: Output of :func:`bootstrap_metrics` (or None).
        path: CSV output path.
        sparse_classes: Classes for which F1 CIs are suppressed.
    """
    rows: list[dict[str, Any]] = []
    for cls in CANONICAL_ORDER:
        entry = prf[cls]
        ci_lo: float | None
        ci_hi: float | None
        if bootstrap and cls not in sparse_classes:
            ci_lo, ci_hi = bootstrap["per_class_f1_ci"].get(cls, (None, None))
        else:
            ci_lo, ci_hi = None, None
        rows.append({
            "class": cls,
            "support": entry["support"],
            "precision": round(entry["precision"], 4) if not np.isnan(entry["precision"]) else "",
            "recall": round(entry["recall"], 4) if not np.isnan(entry["recall"]) else "",
            "f1": round(entry["f1"], 4) if not np.isnan(entry["f1"]) else "",
            "tp": entry["tp"],
            "fp": entry["fp"],
            "fn": entry["fn"],
            "f1_ci_low": round(ci_lo, 4) if (ci_lo is not None and not np.isnan(ci_lo)) else "",
            "f1_ci_high": round(ci_hi, 4) if (ci_hi is not None and not np.isnan(ci_hi)) else "",
            "sparse": cls in sparse_classes,
        })
    pd.DataFrame(rows).to_csv(path, index=False)


def write_summary_json(
    by_buffer: dict[int, dict[str, Any]],
    headline_buffer: int,
    path: Path,
) -> None:
    """Write macro-F1 / weighted-F1 (+ bootstrap CI) to a JSON summary.

    Args:
        by_buffer: Buffer-keyed analysis dict.
        headline_buffer: The buffer at which bootstrap CIs were
            computed.
        path: Output JSON path.
    """
    buf = by_buffer[headline_buffer]
    boot = buf.get("bootstrap", {})
    out = {
        "buffer_headline_m": headline_buffer,
        "n_matched_pairs": buf["n_matched"],
        "summary_f1": buf["summary_f1"],
        "summary_f1_ci": {
            "weighted_f1_95ci": list(boot.get("weighted_f1_ci", [float("nan"), float("nan")])),
            "macro_f1_95ci": list(boot.get("macro_f1_ci", [float("nan"), float("nan")])),
            "valid_bootstrap_iter": boot.get("valid_iter", 0),
            "total_bootstrap_iter": boot.get("n_iter", 0),
        },
    }
    path.write_text(json.dumps(out, indent=2))


def write_kappa_mcc_json(
    by_buffer: dict[int, dict[str, Any]],
    headline_buffer: int,
    path: Path,
) -> None:
    """Write the kappa / MCC block (+ bootstrap CIs) to JSON.

    Args:
        by_buffer: Buffer-keyed analysis dict.
        headline_buffer: Buffer at which bootstrap was run.
        path: Output JSON path.
    """
    buf = by_buffer[headline_buffer]
    km = buf["kappa_mcc"]
    boot = buf.get("bootstrap", {})
    out = {
        "buffer_m": headline_buffer,
        **km,
        "kappa_unweighted_95ci": list(boot.get("kappa_unweighted_ci", [float("nan"), float("nan")])),
        "kappa_linear_hierarchical_95ci": list(boot.get("kappa_linear_hierarchical_ci", [float("nan"), float("nan")])),
        "mcc_95ci": list(boot.get("mcc_ci", [float("nan"), float("nan")])),
        "note": (
            "kappa_linear_hierarchical uses weights: same-family err=0.5, "
            "across-Level-1 err=1.0, diagonal=0.0"
        ),
    }
    path.write_text(json.dumps(out, indent=2))


def write_hierarchical_json(
    by_buffer: dict[int, dict[str, Any]],
    headline_buffer: int,
    path: Path,
) -> None:
    """Write the hierarchical-decomposition dict to JSON.

    Args:
        by_buffer: Buffer-keyed analysis dict.
        headline_buffer: Buffer at which bootstrap was run.
        path: Output JSON path.
    """
    out = {
        "buffer_m": headline_buffer,
        **by_buffer[headline_buffer]["hierarchical"],
    }
    path.write_text(json.dumps(out, indent=2, default=_json_default))


def _json_default(obj: Any) -> Any:  # pragma: no cover — serialiser helper
    """JSON fallback encoder for pandas / numpy types.

    Args:
        obj: Object to encode.

    Returns:
        JSON-serialisable representation.
    """
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict()
    raise TypeError(f"Not JSON-serializable: {type(obj)}")


def write_buffer_sensitivity_csv(
    by_buffer: dict[int, dict[str, Any]],
    path: Path,
) -> None:
    """Write buffer-sensitivity comparison across 20 / 30 / 50 m.

    Args:
        by_buffer: Buffer-keyed analysis dict.
        path: Output CSV path.
    """
    rows: list[dict[str, Any]] = []
    for buf, data in sorted(by_buffer.items()):
        summary = data["summary_f1"]
        hier = data["hierarchical"]
        km = data["kappa_mcc"]
        rows.append({
            "buffer_m": buf,
            "n_matched": data["n_matched"],
            "accuracy": round(summary["accuracy"], 4),
            "macro_f1": round(summary["macro_f1"], 4),
            "weighted_f1": round(summary["weighted_f1"], 4),
            "level1_accuracy": round(hier["level1"]["accuracy"], 4),
            "level2_accuracy": round(hier["level2"]["accuracy"], 4),
            "kappa_unweighted": round(km["kappa_unweighted"], 4),
            "kappa_linear_hier": round(km["kappa_linear_hierarchical"], 4),
            "mcc_multi": round(km["mcc_multi"], 4),
        })
    pd.DataFrame(rows).to_csv(path, index=False)


def write_consensus_sweep_csv(
    sweep: dict[int, dict[str, Any]],
    path: Path,
    headline_buffer: int = 50,
) -> None:
    """Write the consensus-threshold sweep comparison table.

    Args:
        sweep: Threshold-keyed dict of buffer-keyed results.
        path: Output CSV path.
        headline_buffer: Buffer to use for the comparison.
    """
    rows: list[dict[str, Any]] = []
    for thr, by_buf in sorted(sweep.items()):
        data = by_buf[headline_buffer]
        summary = data["summary_f1"]
        hier = data["hierarchical"]
        km = data["kappa_mcc"]
        rows.append({
            "threshold": f"{thr}/5",
            "n_detections": data["n_detections"],
            "n_matched": data["n_matched"],
            "weighted_f1": round(summary["weighted_f1"], 4),
            "macro_f1": round(summary["macro_f1"], 4),
            "accuracy": round(summary["accuracy"], 4),
            "level1_accuracy": round(hier["level1"]["accuracy"], 4),
            "level2_accuracy": round(hier["level2"]["accuracy"], 4),
            "kappa_unweighted": round(km["kappa_unweighted"], 4),
            "kappa_linear_hier": round(km["kappa_linear_hierarchical"], 4),
            "mcc_multi": round(km["mcc_multi"], 4),
        })
    pd.DataFrame(rows).to_csv(path, index=False)


# ── Main entry point ──────────────────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (default: ``sys.argv[1:]``).

    Returns:
        Namespace with all configured CLI parameters.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Subtype-classification accuracy analysis on the 4-map "
            "gold-standard subset (see planning/gold-standard-"
            "classification-accuracy-plan.md)."
        ),
    )
    parser.add_argument(
        "--gt-dir",
        type=Path,
        default=Path("inputs/vectors/references/"),
        help="Directory containing reference_*.geojson files.",
    )
    parser.add_argument(
        "--detections",
        type=Path,
        default=Path(
            "outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson",
        ),
        help=(
            "Consensus detections GeoJSON (default 4/5). The "
            "consensus-threshold sweep will construct 3/5 and 5/5 "
            "paths from this by replacing the threshold token."
        ),
    )
    parser.add_argument(
        "--bounds",
        type=Path,
        default=Path("inputs/vectors/bounds/384/full_evaluation_bounds.geojson"),
        help="Tile bounds GeoJSON.",
    )
    parser.add_argument(
        "--buffers",
        type=int,
        nargs="+",
        default=[20, 30, 50],
        help="Buffer distances in metres.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/gold-standard-subtype-classification/"),
        help="Output directory.",
    )
    parser.add_argument(
        "--bootstrap-n",
        type=int,
        default=10_000,
        help="Number of bootstrap iterations.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="RNG seed for the bootstrap.",
    )
    parser.add_argument(
        "--consensus-thresholds",
        type=int,
        nargs="+",
        default=[3, 4, 5],
        help="Consensus thresholds (out of 5) to include in the sweep.",
    )
    parser.add_argument(
        "--headline-buffer",
        type=int,
        default=50,
        help="Buffer distance used for headline tables (default 50 m).",
    )
    return parser.parse_args(argv)


def setup_logging(output_dir: Path) -> logging.Logger:
    """Configure console + file logging to ``analysis.log``.

    Args:
        output_dir: Output directory (must already exist).

    Returns:
        Configured root logger for the analysis.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "analysis.log"
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.FileHandler(log_path, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
    return logging.getLogger("analyse_subtype_classification")


def detections_path_for_threshold(base: Path, thr: int) -> Path:
    """Swap the consensus threshold in a file name (e.g. 4 → 3 or 5).

    Args:
        base: Base detections path (e.g. ``consensus-4of5.geojson``).
        thr: Target threshold (3, 4, or 5).

    Returns:
        Path pointing to ``consensus-<thr>of5.geojson``.
    """
    # Replace the threshold token wherever it appears in the stem.
    stem = base.stem
    for k in (3, 4, 5):
        stem = stem.replace(f"{k}of5", "PLACEHOLDER") if f"{k}of5" in stem else stem
    stem = stem.replace("PLACEHOLDER", f"{thr}of5")
    return base.with_name(f"{stem}{base.suffix}")


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success, non-zero on failure.

    Args:
        argv: Optional argument list override.

    Returns:
        Process exit code.
    """
    args = parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    log = setup_logging(args.output_dir)

    repo_root = Path(__file__).parent.parent.resolve()
    git_hash = get_git_commit_hash(repo_root)
    log.info("git commit: %s", git_hash)
    log.info("vocabulary mapping: %s", GT_TO_VLM_VOCABULARY)

    # Log input file SHA256s for reproducibility.
    log.info("GT dir SHA256s:")
    for p in sorted(args.gt_dir.glob("reference_*.geojson")):
        if "student" in p.name or p.name == "mounds-reference.geojson":
            continue
        log.info("  %s  %s", sha256_file(p)[:16], p.name)
    log.info(
        "bounds SHA256: %s  %s",
        sha256_file(args.bounds)[:16], args.bounds.name,
    )
    # Detections SHA256 logged per threshold below.

    # ── Load shared data ──
    gdf_ref = load_ground_truth(args.gt_dir)
    gdf_bounds = load_bounds(args.bounds)

    # Sanity check: GT count should be 569 on the 4-map subset.
    log.info("GT total features loaded: %d (expected 569)", len(gdf_ref))

    # ── Consensus-threshold sweep ──
    sweep: dict[int, dict[str, Any]] = {}
    for thr in sorted(args.consensus_thresholds):
        det_path = detections_path_for_threshold(args.detections, thr)
        if not det_path.exists():
            log.warning("Skipping threshold %d/5: %s does not exist", thr, det_path)
            continue
        log.info(
            "=== Analysing consensus %d/5 → %s (SHA256=%s) ===",
            thr, det_path, sha256_file(det_path)[:16],
        )
        gdf_det = load_detections(det_path)
        by_buf = run_one_threshold(
            gdf_ref=gdf_ref,
            gdf_det=gdf_det,
            gdf_bounds=gdf_bounds,
            buffers=args.buffers,
            bootstrap_n=args.bootstrap_n,
            seed=args.seed,
            headline_buffer=args.headline_buffer,
        )
        # Annotate with n_detections so the sweep CSV can surface it.
        for buf, data in by_buf.items():
            data["n_detections"] = int(len(gdf_det))
        sweep[thr] = by_buf

    if not sweep:
        log.error("No consensus files could be loaded; aborting.")
        return 2

    # ── Write outputs for the default (headline) threshold ──
    headline_thr = 4 if 4 in sweep else sorted(sweep.keys())[len(sweep) // 2]
    log.info("Using consensus %d/5 as headline threshold.", headline_thr)
    head = sweep[headline_thr]

    cm_4x4 = head[args.headline_buffer]["confusion_4x4"]
    cm_5x5 = head[args.headline_buffer]["confusion_5x5"]
    write_confusion_matrix_csv(
        cm_4x4,
        args.output_dir / f"confusion_matrix_4x4_buf{args.headline_buffer}.csv",
        mode_label="4x4 matched-pairs confusion",
    )
    write_confusion_matrix_csv(
        cm_5x5,
        args.output_dir / f"confusion_matrix_5x5_buf{args.headline_buffer}.csv",
        mode_label="5x5 (incl. no_match) confusion",
    )
    write_per_class_f1_csv(
        prf=head[args.headline_buffer]["per_class_prf"],
        bootstrap=head[args.headline_buffer].get("bootstrap"),
        path=args.output_dir / f"per_class_f1_buf{args.headline_buffer}.csv",
    )
    write_summary_json(
        head, args.headline_buffer,
        args.output_dir / "macro_weighted_summary.json",
    )
    write_kappa_mcc_json(
        head, args.headline_buffer,
        args.output_dir / "kappa_mcc.json",
    )
    write_hierarchical_json(
        head, args.headline_buffer,
        args.output_dir / "hierarchical_decomposition.json",
    )
    write_buffer_sensitivity_csv(
        head, args.output_dir / "buffer_sensitivity.csv",
    )

    # Per-map confusion + summary.
    pl_head = head[args.headline_buffer]["pair_list"]
    per_map_confusion_table(pl_head).to_csv(
        args.output_dir / "per_map_confusion.csv", index=False,
    )
    per_map_summary(pl_head).to_csv(
        args.output_dir / "per_map_summary.csv", index=False,
    )

    # Settlement trace (sparse-class qualitative).
    settlement_trace(pl_head, gdf_ref).to_csv(
        args.output_dir / "settlement_trace.csv", index=False,
    )

    # Consensus-threshold sweep table (always written).
    write_consensus_sweep_csv(
        sweep,
        args.output_dir / "consensus_threshold_sweep.csv",
        headline_buffer=args.headline_buffer,
    )

    # Record the run manifest alongside the log.
    manifest = {
        "git_commit": git_hash,
        "version": __version__,
        "seed": args.seed,
        "bootstrap_n": args.bootstrap_n,
        "buffers": args.buffers,
        "headline_buffer_m": args.headline_buffer,
        "consensus_thresholds": sorted(sweep.keys()),
        "headline_threshold": headline_thr,
        "gt_dir": str(args.gt_dir),
        "bounds": str(args.bounds),
        "detections_headline": str(
            detections_path_for_threshold(args.detections, headline_thr),
        ),
        "n_ground_truth_features": int(len(gdf_ref)),
        "vocabulary_mapping": GT_TO_VLM_VOCABULARY,
    }
    (args.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2),
    )

    log.info("All outputs written to %s", args.output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
