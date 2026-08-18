#!/usr/bin/env python3
"""
Build Tiered Leaderboard from Detection Conditions
====================================================

General-purpose orchestrator for building statistically tiered leaderboards.
Evaluates detection conditions at multiple spatial buffers, finds optimal
consensus thresholds, runs round-robin pairwise permutation tests, applies
Benjamini-Hochberg False Discovery Rate (FDR) correction, and groups
conditions into statistically distinguishable tiers.

Six pipeline stages, each independently cacheable:

1. **Resolve conditions** — from YAML spec or condition inventory
2. **Evaluate** — threshold sweep at all buffers (parallelised)
3. **Select thresholds** — pick optimal consensus threshold per condition
4. **Pairwise tests** — C(N,2) tile-level paired permutation tests
5. **FDR + tier** — BH-FDR correction → greedy clique-based tiering
6. **Output** — Markdown + JSON (JavaScript Object Notation) leaderboard tables

Usage::

    # From YAML spec
    python scripts/build_tiered_leaderboard.py \\
        --spec leaderboard-era1.yaml \\
        --output-dir results/leaderboard/era1/

    # From condition inventory with era filter
    python scripts/build_tiered_leaderboard.py \\
        --inventory planning/condition-inventory.json \\
        --era 3 \\
        --bounds inputs/vectors/bounds/384/h10_test_bounds.geojson \\
        --output-dir results/leaderboard/era3/

    # Dry run — list conditions without executing
    python scripts/build_tiered_leaderboard.py \\
        --inventory planning/condition-inventory.json --era 1 --dry-run

    # Re-run tiering only (cached evaluations + pairwise)
    python scripts/build_tiered_leaderboard.py \\
        --spec leaderboard-era1.yaml \\
        --skip-evaluation --skip-pairwise \\
        --output-dir results/leaderboard/era1/

Inputs:
    - Condition inventory (``planning/condition-inventory.json``) or YAML spec
    - Consensus GeoJSON detection files (``outputs/**/consensus_t*.geojson``)
    - Ground truth reference (``inputs/vectors/references/mounds-reference.geojson``)
    - Evaluation bounds (``inputs/vectors/bounds/*.geojson``)

Outputs:
    - ``leaderboard_tiers_{primary_buffer}m.md`` — Markdown table grouped by tier
      (one MD per invocation, named for ``--primary-buffer``)
    - ``leaderboard_tiers_{primary_buffer}m.json`` — Machine-readable with provenance
    - ``leaderboard_all_evaluations.json`` — Full threshold × buffer sweep
    - ``leaderboard_tiers_{primary_buffer}m.json`` includes BH-FDR correction details

Note: prior to commit fixing Task #13, this script wrote one MD per
buffer in ``--buffers`` per invocation (all rendered from the
primary-buffer ``tiers``). That caused per-buffer F1 re-tiering
drivers — which loop over primary buffers but pass the full
``--buffers`` list each time — to overwrite each other's MD outputs.
The MD writer now emits one MD per invocation, named for
``--primary-buffer``. To produce MD at additional buffers, either
re-render from the per-buffer JSONs (see
``scripts/regenerate_per_arch_md_from_json.py``) or invoke this
script again with a different ``--primary-buffer``.

Exit Codes:
    0 - Success
    1 - Some conditions failed evaluation (partial)
    2 - Fatal error (bad configuration, missing files)

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-16
"""

from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
import logging
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GROUND_TRUTH = (
    PROJECT_ROOT / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
)
DEFAULT_BOUNDS = (
    PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "full_evaluation_bounds.geojson"
)
DEFAULT_BUFFERS = [20, 30, 40, 50]
DEFAULT_BOOTSTRAP = 1000
DEFAULT_SEED = 42
DEFAULT_FDR_Q = 0.05
DEFAULT_N_PERMUTATIONS = 10_000
DEFAULT_TOP_N = 20

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Imports from existing scripts (library-style reuse)
# ---------------------------------------------------------------------------

# Add scripts/ to path for imports
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from evaluate_detections import (  # noqa: E402
    UNDEFINED_DISPLAY,
    evaluate_single_run,
    load_geojson,
    slugify,
)
from lib_detection_paths import resolve_pool_passes  # noqa: E402
from pairwise_permutation_test import (  # noqa: E402
    load_geojson_detections,
    run_permutation_test,
    run_permutation_test_mcc,
)
from apply_fdr_correction import apply_bh_correction  # noqa: E402

# Metric labels — single source of truth used for cache paths,
# command-line flags, and human-readable output.
METRIC_F1 = "f1"
METRIC_MCC = "mcc"
SUPPORTED_METRICS = (METRIC_F1, METRIC_MCC)


def _fmt_metric(val: float | None, digits: int = 3) -> str:
    """Format a possibly-undefined metric for a Markdown/console cell.

    Mirrors ``evaluate_detections._fmt_metric`` so leaderboard tables
    and evaluation tables render an undefined tile-level Matthews
    Correlation Coefficient (MCC) identically. The display string
    itself is imported from ``evaluate_detections`` so there is one
    source of truth for it.

    Args:
        val: The metric value, or ``None`` when it is undefined
            (degenerate 2 x 2 tile confusion matrix — erratum E81).
        digits: Decimal places for the numeric case (default 3, the
            precision of the leaderboard tables).

    Returns:
        The formatted number, or :data:`UNDEFINED_DISPLAY` for
        ``None``. A genuine zero still renders as ``'0.000'``.

    Examples:
        >>> _fmt_metric(0.0665)
        '0.066'
        >>> _fmt_metric(0.0)
        '0.000'
        >>> _fmt_metric(None)
        'undefined'
    """
    if val is None:
        return UNDEFINED_DISPLAY
    return f"{val:.{digits}f}"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class ConditionSpec:
    """A condition to evaluate on the leaderboard."""

    label: str
    geojson_paths: list[Path]  # One per threshold (t=1..K), sorted
    thresholds: list[int]      # Corresponding threshold values
    era: int
    track: str
    category: str              # "consensus" | "single-pass"
    k: int
    condition_id: str = ""
    metadata: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class SelectedCondition:
    """A condition after threshold selection — ready for pairwise tests."""

    label: str
    geojson_path: Path
    best_threshold: int
    era: int
    track: str
    category: str
    k: int
    evaluations: dict  # buffer_metres -> evaluation result dict
    condition_id: str = ""
    # Tile-level MCC (buffer-invariant in this codebase). Populated
    # from the evaluation result's ``tile_classification.mcc.mean``
    # field by ``select_best_thresholds()`` when MCC was computed.
    # ``None`` means *undefined*: either MCC was not computed for this
    # condition, or the 2 x 2 tile confusion matrix is degenerate so
    # the coefficient has no value (erratum E81). The default is
    # deliberately ``None`` and not ``0.0`` — 0 on the MCC scale means
    # "random" (§ 4.2 of the preregistration), so defaulting to it
    # would publish a chance-level measurement that was never made.
    tile_mcc: float | None = None


def get_condition_score(
    cond: "SelectedCondition",
    buffer_metres: int,
    metric: str = METRIC_F1,
) -> float:
    """Return the per-condition score under the requested metric.

    Used everywhere ranking, sorting, or tier construction needs a
    single numeric score per condition. F1 is buffer-specific; MCC is
    buffer-invariant in this codebase (tile classification depends on
    presence-of-detection per tile, not buffer-distance matching) but
    is still keyed by buffer for symmetry with F1 ordering.

    Args:
        cond: Selected condition (post-threshold-selection).
        buffer_metres: Buffer at which to look up F1. Ignored for MCC
            (which is buffer-invariant) but accepted for API symmetry.
        metric: ``"f1"`` (default) or ``"mcc"``.

    Returns:
        The score (F1 in [0, 1] or MCC in [-1, 1]). F1 falls back to
        0.0 when the requested buffer was not evaluated — a missing
        F1 genuinely is "no detections matched", so 0.0 is a
        measurement there rather than a placeholder.

    Raises:
        ValueError: when ``metric`` is unsupported, or when
            ``metric="mcc"`` and ``cond.tile_mcc`` is ``None``.

            Erratum E81 (2026-08-18): this function used to return
            ``float(cond.tile_mcc or 0.0)``, which scored an
            *undefined* MCC as 0.0 and therefore ranked a condition
            whose coefficient was never computable alongside
            conditions measured at chance level (§ 4.2 of the
            preregistration labels 0 on this scale "random"). The
            ``or`` also swallowed a legitimate MCC of exactly 0.0.
            Conditions with an undefined MCC are now dropped from the
            MCC board by :func:`select_best_thresholds`, so reaching
            this branch means an unscoreable condition leaked into a
            ranking — failing loudly is the correct outcome, because
            the alternative is a silent chance-level score.
    """
    if metric == METRIC_F1:
        return cond.evaluations.get(buffer_metres, {}).get("f1", 0.0)
    if metric == METRIC_MCC:
        # MCC is stored at the condition level, not per-buffer.
        if cond.tile_mcc is None:
            raise ValueError(
                f"Tile-level MCC is undefined for {cond.label!r}, so it "
                "cannot be scored or ranked on MCC (erratum E81). "
                "Conditions with an undefined MCC are excluded from the "
                "MCC leaderboard by select_best_thresholds(); this "
                "condition reached a ranking path it should not have."
            )
        return float(cond.tile_mcc)
    raise ValueError(f"Unsupported metric: {metric!r}")


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def setup_logging(log_file: Path | None = None) -> None:
    """Configure dual-output logging (console INFO, file DEBUG)."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on repeated calls (e.g., in tests)
    root.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    root.addHandler(console)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        root.addHandler(fh)


def get_git_commit() -> str:
    """Return short git commit hash, or ``'(unknown)'`` on failure."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=2,
            cwd=str(PROJECT_ROOT),
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "(unknown)"


# ---------------------------------------------------------------------------
# Stage 1: Condition resolution
# ---------------------------------------------------------------------------


def discover_consensus_geojsons(
    base_path: Path,
) -> list[tuple[int, Path]]:
    """Find all consensus threshold GeoJSONs for a condition.

    Searches for ``consensus_t{N}.geojson`` in the condition directory
    and its ``consensus/``, ``greedy/``, and sibling ``greedy/{name}/``
    subdirectories. Also handles the H11-era ``{prefix}-{N}of{M}.geojson``
    naming convention.

    Args:
        base_path: Path to the condition output directory.

    Returns:
        List of ``(threshold, path)`` tuples sorted by threshold.
    """
    candidates: list[tuple[int, Path]] = []
    search_dirs = [base_path]

    for subdir in ["consensus", "greedy", "voting"]:
        d = base_path / subdir
        if d.is_dir():
            search_dirs.append(d)

    # Era 3 pattern: greedy tree lives at parent/greedy/{condition_name}/
    greedy_sibling = base_path.parent / "greedy" / base_path.name
    if greedy_sibling.is_dir():
        search_dirs.append(greedy_sibling)

    for d in search_dirs:
        # Pattern: consensus_t{N}.geojson
        for f in d.glob("consensus_t*.geojson"):
            match = re.search(r"consensus_t(\d+)", f.stem)
            if match:
                candidates.append((int(match.group(1)), f))

        # Pattern: {prefix}-{N}of{M}.geojson (H11-era)
        for f in d.glob("*-*of*.geojson"):
            match = re.search(r"-(\d+)of(\d+)", f.stem)
            if match:
                candidates.append((int(match.group(1)), f))

    # Deduplicate (same threshold from different search paths)
    seen: dict[int, Path] = {}
    for t, p in candidates:
        if t not in seen:
            seen[t] = p
    return sorted(seen.items(), key=lambda x: x[0])


def resolve_conditions_from_inventory(
    inventory_path: Path,
    *,
    era: int | None = None,
    track: str | None = None,
    hypothesis: str | None = None,
    architecture: str | None = None,
    status_filter: str | list[str] = "READY",
) -> list[ConditionSpec]:
    """Build condition list from condition-inventory.json with filters.

    Args:
        inventory_path: Path to condition-inventory.json.
        era: Filter to this era. ``None`` = all.
        track: Filter to track. ``None`` = all.
        hypothesis: Filter to hypothesis prefix. ``None`` = all.
        architecture: Filter to architecture label ({"single-pass",
            "consensus", "single-pass+PV", "pv"}). ``None`` = all.
        status_filter: Only include conditions with this status. Accepts
            a single string or a list of strings (OR-joined).

    Returns:
        List of ConditionSpec instances, sorted by label.
    """
    with open(inventory_path, encoding="utf-8") as f:
        inventory = json.load(f)

    # Normalise status_filter to a set for fast lookups
    if isinstance(status_filter, str):
        status_set = {status_filter} if status_filter else set()
    else:
        status_set = set(status_filter) if status_filter else set()

    specs: list[ConditionSpec] = []
    for cond in inventory:
        if status_set and cond.get("status") not in status_set:
            continue
        if era is not None and cond.get("era") != era:
            continue
        if track is not None and cond.get("track") != track:
            continue
        if architecture is not None and cond.get("architecture") != architecture:
            continue
        if hypothesis and not cond.get("hypothesis", "").startswith(hypothesis):
            continue

        cond_path = PROJECT_ROOT / cond["path"]
        k = cond.get("K", 1)
        cond_architecture = cond.get("architecture", "")

        # Build a shared metadata block so downstream writers have full
        # provenance to display in tier tables (proposer config, verifier
        # prompt, thresholds, etc.).
        shared_metadata = {
            "hypothesis": cond.get("hypothesis", ""),
            "architecture_label": cond_architecture,
            "model": cond.get("model"),
            "config_version": cond.get("config_version"),
            "thinking": cond.get("thinking"),
            "temperature": cond.get("T"),
            "N": cond.get("N"),
            "vote_t": cond.get("vote_t"),
            "prob_t": cond.get("prob_t"),
            "instruction_file": cond.get("instruction_file"),
            "verifier_prompt": cond.get("verifier_prompt"),
            "source_path": cond.get("path"),
            "status": cond.get("status"),
            "notes": cond.get("notes"),
        }

        if cond_architecture == "pv":
            # Proposer-verifier: a pre-materialised single-threshold GeoJSON
            # exists at the path. K/N are carried as metadata but the
            # pipeline treats this condition as a single fixed threshold.
            gj = cond_path if cond_path.suffix == ".geojson" else cond_path / "detections.geojson"
            if gj.is_file():
                specs.append(ConditionSpec(
                    label=cond["id"],
                    geojson_paths=[gj],
                    thresholds=[1],
                    era=cond.get("era", 0),
                    track=cond.get("track", "unknown"),
                    category="pv",
                    k=k,
                    condition_id=cond["id"],
                    metadata=shared_metadata,
                ))
            else:
                logger.warning(
                    "PV condition %s: materialised geojson not found at %s",
                    cond["id"], gj,
                )
        elif cond_architecture == "single-pass+PV":
            # Single-pass + verifier: the `path` points directly at a
            # materialised verified GeoJSON (one pre-thresholded file per
            # condition). K=1 (no proposer replication) but the verifier
            # has already filtered the output.
            gj = cond_path if cond_path.suffix == ".geojson" else cond_path / "detections.geojson"
            if gj.is_file():
                specs.append(ConditionSpec(
                    label=cond["id"],
                    geojson_paths=[gj],
                    thresholds=[1],
                    era=cond.get("era", 0),
                    track=cond.get("track", "unknown"),
                    category="single-pass+PV",
                    k=k,
                    condition_id=cond["id"],
                    metadata=shared_metadata,
                ))
            else:
                logger.warning(
                    "single-pass+PV condition %s: geojson not found at %s",
                    cond["id"], gj,
                )
        elif k <= 1:
            # Single-pass: the first per-pass GeoJSON in run order. Resolved
            # via lib_detection_paths so BOTH naming conventions are expanded;
            # the previous batch-only glob missed real-time passes (defect D6).
            det_files = resolve_pool_passes(cond_path, allow_multiple=True)
            if det_files:
                specs.append(ConditionSpec(
                    label=cond["id"],
                    geojson_paths=[det_files[0]],
                    thresholds=[1],
                    era=cond.get("era", 0),
                    track=cond.get("track", "unknown"),
                    category="single-pass",
                    k=k,
                    condition_id=cond["id"],
                    metadata=shared_metadata,
                ))
            else:
                logger.warning(
                    "Single-pass %s: detection geojson not found at %s",
                    cond["id"], cond_path,
                )
        else:
            # Consensus: discover threshold GeoJSONs
            threshold_files = discover_consensus_geojsons(cond_path)
            if threshold_files:
                thresholds, paths = zip(*threshold_files)
                specs.append(ConditionSpec(
                    label=cond["id"],
                    geojson_paths=list(paths),
                    thresholds=list(thresholds),
                    era=cond.get("era", 0),
                    track=cond.get("track", "unknown"),
                    category="consensus",
                    k=k,
                    condition_id=cond["id"],
                    metadata=shared_metadata,
                ))
            else:
                logger.warning(
                    "No consensus GeoJSONs found for %s at %s",
                    cond["id"], cond_path,
                )

    specs.sort(key=lambda s: s.label)
    logger.info(
        "Resolved %d conditions from inventory (era=%s, track=%s)",
        len(specs), era, track,
    )
    return specs


def resolve_conditions_from_yaml(spec_path: Path) -> tuple[dict, list[ConditionSpec]]:
    """Load conditions from a YAML leaderboard spec file.

    Args:
        spec_path: Path to the YAML spec file.

    Returns:
        Tuple of ``(config_dict, conditions_list)``.
    """
    import yaml

    with open(spec_path, encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    config = {
        "metadata": spec.get("metadata", {}),
        "evaluation": spec.get("evaluation", {}),
        "tiering": spec.get("tiering", {}),
    }

    specs: list[ConditionSpec] = []
    for entry in spec.get("conditions", []):
        geojson_path = PROJECT_ROOT / entry["geojson"]
        specs.append(ConditionSpec(
            label=entry["label"],
            geojson_paths=[geojson_path],
            thresholds=[entry.get("threshold", 1)],
            era=entry.get("era", 0),
            track=entry.get("track", "unknown"),
            category=entry.get("category", "consensus"),
            k=entry.get("k", 1),
            condition_id=entry.get("id", entry["label"]),
            metadata=entry.get("metadata", {}),
        ))

    specs.sort(key=lambda s: s.label)
    return config, specs


# ---------------------------------------------------------------------------
# Stage 2: Evaluation (threshold sweep)
# ---------------------------------------------------------------------------


def _cache_path_eval(cache_dir: Path, label: str, threshold: int, buffer_m: int) -> Path:
    """Build the cache file path for an evaluation result."""
    return cache_dir / "evaluations" / slugify(label) / f"t{threshold}_{buffer_m}m.json"


def _evaluate_single_threshold(
    geojson_path: Path,
    ref_path: Path,
    bounds_path: Path,
    buffers: list[int],
    n_bootstrap: int,
    seed: int,
    label: str,
) -> dict:
    """Worker function: evaluate one GeoJSON at all buffers.

    Loads reference data from disk (each worker is independent).
    Designed to be called from ProcessPoolExecutor.

    Args:
        geojson_path: Detection GeoJSON to evaluate.
        ref_path: Ground truth reference path.
        bounds_path: Evaluation bounds path.
        buffers: Buffer distances.
        n_bootstrap: Bootstrap iterations.
        seed: Random seed.
        label: Human-readable label.

    Returns:
        Evaluation result dict from ``evaluate_single_run()``.
    """
    import geopandas as gpd

    gdf_det = load_geojson(geojson_path)
    gdf_ref = load_geojson(ref_path)
    gdf_bounds = load_geojson(bounds_path)

    # ---------------------------------------------------------------
    # Single-pass+PV repair (Stage 0 fix, 2026-04-25)
    # ---------------------------------------------------------------
    # The ``outputs/h11/proposer-verifier-384/verified-*.geojson``
    # files have three pathologies that the generic loader does not
    # handle:
    #   1. They contain BOTH ``verified=True`` and ``verified=False``
    #      candidate features. Only verified=True features are kept
    #      detections; verified=False entries must be filtered out.
    #   2. Their geometries are tile-bounding **polygons** rather than
    #      point centroids; matchers cast to centroid implicitly, but
    #      explicitly converting here avoids per-buffer warnings.
    #   3. They lack a CRS declaration in the GeoJSON header but the
    #      coordinates are already projected (EPSG:32635, values like
    #      ``417490, 4702431``). geopandas defaults the CRS to
    #      EPSG:4326 on read; ``load_geojson()``'s subsequent
    #      ``.to_crs(EPSG:32635)`` then projects "lon=417490,
    #      lat=4702431" to infinity → silent F1=0.
    #
    # Detection: if the GeoDataFrame carries a ``verified`` column and
    # ``load_geojson()`` has produced any invalid geometries (the
    # signature of the infinity coordinate transformation), we repair
    # by re-reading the raw file, overriding the CRS to EPSG:32635,
    # filtering ``verified=True``, and converting polygon footprints
    # to centroids.
    # ---------------------------------------------------------------
    if (
        not gdf_det.empty
        and "verified" in gdf_det.columns
        and not gdf_det.geometry.is_valid.all()
    ):
        gdf_raw = gpd.read_file(geojson_path)
        gdf_raw = gdf_raw.set_crs("EPSG:32635", allow_override=True)
        gdf_det = gdf_raw[gdf_raw["verified"] == True].copy()  # noqa: E712
        gdf_det["geometry"] = gdf_det.geometry.centroid

    # Assign source_tile if missing (consensus GeoJSONs have source_tiles
    # but not source_tile). Matches evaluate_detections.py lines 770-782.
    if "source_tile" not in gdf_det.columns and not gdf_det.empty:
        joined = gpd.sjoin(
            gdf_det, gdf_bounds[["tile_name", "geometry"]],
            how="left", predicate="intersects",
        )
        joined = joined[~joined.index.duplicated(keep="first")]
        gdf_det["source_tile"] = joined["tile_name"]

    return evaluate_single_run(
        gdf_det, gdf_ref, gdf_bounds,
        buffers=buffers,
        n_bootstrap=n_bootstrap,
        seed=seed,
        label=label,
        compute_mcc=True,  # Tile-level MCC at the matching buffer (default 20m)
    )


def evaluate_all_conditions(
    conditions: list[ConditionSpec],
    ref_path: Path,
    bounds_path: Path,
    buffers: list[int],
    n_bootstrap: int,
    seed: int,
    cache_dir: Path,
    workers: int = 4,
    force: bool = False,
) -> dict[str, dict[int, dict]]:
    """Evaluate all conditions at all thresholds and buffers.

    Results are cached per (condition, threshold, buffer) triple.
    Returns a nested dict: ``{label: {threshold: eval_result_dict}}``.

    Args:
        conditions: Conditions to evaluate.
        ref_path: Ground truth path.
        bounds_path: Bounds path.
        buffers: Buffer distances.
        n_bootstrap: Bootstrap iterations.
        seed: Random seed.
        cache_dir: Cache directory.
        workers: Number of parallel workers.
        force: Recompute ignoring cache.

    Returns:
        Nested dict mapping label → threshold → evaluation result.
    """
    all_results: dict[str, dict[int, dict]] = {}

    # Build task list: (condition, threshold_idx)
    tasks: list[tuple[ConditionSpec, int, int, Path]] = []
    cached_count = 0

    for cond in conditions:
        all_results[cond.label] = {}
        for i, (threshold, gj_path) in enumerate(
            zip(cond.thresholds, cond.geojson_paths)
        ):
            # Check cache for ALL buffers at this threshold
            all_cached = not force and all(
                _cache_path_eval(cache_dir, cond.label, threshold, b).is_file()
                for b in buffers
            )
            if all_cached:
                # Load from cache
                merged = {"label": cond.label, "n_detections": 0, "buffers": []}
                tile_classification: dict | None = None
                for b in buffers:
                    cp = _cache_path_eval(cache_dir, cond.label, threshold, b)
                    with open(cp, encoding="utf-8") as f:
                        buf_data = json.load(f)
                    # Recover n_detections from cache (stored per-buffer)
                    if "n_detections" in buf_data:
                        merged["n_detections"] = buf_data.pop("n_detections")
                    # Lift tile_classification (MCC, sensitivity,
                    # specificity) — all per-buffer files carry the
                    # same copy; first one wins.
                    if (
                        tile_classification is None
                        and "__tile_classification__" in buf_data
                    ):
                        tile_classification = buf_data.pop(
                            "__tile_classification__",
                        )
                    else:
                        buf_data.pop("__tile_classification__", None)
                    merged["buffers"].append(buf_data)
                if tile_classification is not None:
                    merged["tile_classification"] = tile_classification
                all_results[cond.label][threshold] = merged
                cached_count += 1
            else:
                tasks.append((cond, i, threshold, gj_path))

    logger.info(
        "Evaluation: %d cached, %d to compute (%d workers)",
        cached_count, len(tasks), workers,
    )

    if not tasks:
        return all_results

    # Execute evaluations
    if workers <= 1:
        for cond, _idx, threshold, gj_path in tasks:
            logger.info("Evaluating %s t=%d...", cond.label, threshold)
            result = _evaluate_single_threshold(
                gj_path, ref_path, bounds_path,
                buffers, n_bootstrap, seed, cond.label,
            )
            all_results[cond.label][threshold] = result
            _write_eval_cache(cache_dir, cond.label, threshold, result)
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_map = {}
            for cond, _idx, threshold, gj_path in tasks:
                fut = executor.submit(
                    _evaluate_single_threshold,
                    gj_path, ref_path, bounds_path,
                    buffers, n_bootstrap, seed, cond.label,
                )
                future_map[fut] = (cond, threshold)

            completed = 0
            for fut in as_completed(future_map):
                cond, threshold = future_map[fut]
                completed += 1
                try:
                    result = fut.result()
                    all_results[cond.label][threshold] = result
                    _write_eval_cache(cache_dir, cond.label, threshold, result)
                    logger.info(
                        "[%d/%d] %s t=%d done",
                        completed, len(tasks), cond.label, threshold,
                    )
                except Exception as exc:
                    logger.error(
                        "[%d/%d] %s t=%d FAILED: %s",
                        completed, len(tasks), cond.label, threshold, exc,
                    )

    return all_results


def _write_eval_cache(
    cache_dir: Path, label: str, threshold: int, result: dict,
) -> None:
    """Write per-buffer cache files for an evaluation result.

    Tile-level MCC (in ``result["tile_classification"]``) is replicated
    into each per-buffer cache file under ``__tile_classification__``
    so it survives the cache round-trip. The aggregator
    (``evaluate_all_conditions``) lifts it back into the merged
    threshold-level dict on cache load.
    """
    n_det = result.get("n_detections", 0)
    tile_class = result.get("tile_classification")
    for buf_result in result.get("buffers", []):
        buf_m = buf_result["buffer_metres"]
        cp = _cache_path_eval(cache_dir, label, threshold, buf_m)
        cp.parent.mkdir(parents=True, exist_ok=True)
        # Include n_detections in each cache file for reconstruction
        cached = {**buf_result, "n_detections": n_det}
        # Replicate tile_classification (MCC, sensitivity, specificity)
        # at every buffer file. The aggregator only needs to read one
        # buffer's copy on load.
        if tile_class is not None:
            cached["__tile_classification__"] = tile_class
        with open(cp, "w", encoding="utf-8") as f:
            json.dump(cached, f, indent=2)


# ---------------------------------------------------------------------------
# Stage 3: Threshold selection
# ---------------------------------------------------------------------------


def select_best_thresholds(
    conditions: list[ConditionSpec],
    all_evaluations: dict[str, dict[int, dict]],
    primary_buffer: int,
    top_n: int | None = None,
    metric: str = METRIC_F1,
    undefined_metric_out: list[str] | None = None,
) -> list[SelectedCondition]:
    """Select the best consensus threshold per condition.

    For each condition, finds the threshold that maximises **F1 at
    the primary buffer**. The metric parameter does not change
    threshold selection — even MCC tier tables choose thresholds by
    F1 at the primary buffer, so the same condition row appears in
    F1 and MCC tables with the same vote_t. This keeps cross-metric
    comparisons aligned at the same operational point. The metric
    only changes the score used for the **final tier ordering**.

    Args:
        conditions: Original condition specs.
        all_evaluations: Nested dict from ``evaluate_all_conditions()``.
        primary_buffer: Buffer for threshold selection (always F1).
        top_n: If set, include only conditions in the top-N at any
            buffer (by F1, regardless of metric).
        metric: ``"f1"`` (default) or ``"mcc"``. When ``"mcc"`` the
            sort order at the end uses MCC; threshold selection still
            uses F1.
        undefined_metric_out: Optional list the caller supplies to
            receive the labels of conditions dropped because the
            scoring metric is undefined for them (``metric="mcc"``
            only — see Returns). Supplied as an out-parameter so the
            existing single-list return type, and every caller of it,
            stay unchanged.

    Returns:
        List of SelectedCondition, sorted by chosen metric descending
        at primary buffer.

        Erratum E81 (2026-08-18): when ``metric="mcc"``, conditions
        whose tile-level MCC is **undefined** (degenerate 2 x 2 tile
        confusion matrix, or MCC never computed) are excluded from
        this list rather than scored as 0.0. An undefined coefficient
        is not a chance-level result, and ranking it as one placed
        conditions on the board at a performance level that was never
        measured. Their labels are reported through
        ``undefined_metric_out`` so the caller can render them in an
        explicitly-labelled "MCC undefined" section instead of
        dropping them silently.
    """
    selected: list[SelectedCondition] = []

    for cond in conditions:
        evals = all_evaluations.get(cond.label, {})
        if not evals:
            logger.warning("No evaluations for %s — skipping", cond.label)
            continue

        # Find threshold with best F1 at primary buffer (metric-
        # independent — see docstring for rationale).
        best_t = None
        best_f1 = -1.0
        for threshold, result in evals.items():
            for buf in result.get("buffers", []):
                if buf["buffer_metres"] == primary_buffer:
                    if buf["f1"] > best_f1:
                        best_f1 = buf["f1"]
                        best_t = threshold
                    break

        if best_t is None:
            logger.warning(
                "No evaluation at %dm for %s — skipping",
                primary_buffer, cond.label,
            )
            continue

        # Build per-buffer evaluation dict at the best threshold
        best_eval = evals[best_t]
        buf_dict = {
            b["buffer_metres"]: b for b in best_eval.get("buffers", [])
        }

        # Extract tile-level MCC if available (populated when
        # _evaluate_single_threshold ran with compute_mcc=True).
        # Erratum E81: ``mean`` may be present and ``None`` (undefined
        # MCC — degenerate tile confusion matrix), and it may be
        # absent (MCC not computed). Both map to ``None``; neither
        # maps to 0.0.
        mcc_mean = (
            best_eval.get("tile_classification", {})
            .get("mcc", {})
            .get("mean")
        )
        tile_mcc = None if mcc_mean is None else float(mcc_mean)

        # Find the GeoJSON path for the best threshold
        try:
            t_idx = cond.thresholds.index(best_t)
            gj_path = cond.geojson_paths[t_idx]
        except ValueError:
            logger.warning(
                "Threshold %d not in paths for %s — skipping",
                best_t, cond.label,
            )
            continue

        selected.append(SelectedCondition(
            label=cond.label,
            geojson_path=gj_path,
            best_threshold=best_t,
            era=cond.era,
            track=cond.track,
            category=cond.category,
            k=cond.k,
            evaluations=buf_dict,
            condition_id=cond.condition_id,
            tile_mcc=tile_mcc,
        ))

    # Erratum E81: drop conditions the scoring metric cannot score
    # BEFORE sorting, so no unscoreable condition ever reaches a rank.
    # Only MCC can be undefined here; F1 is always computable (0.0 for
    # "nothing matched" is a measurement, not a placeholder).
    if metric == METRIC_MCC:
        undefined = [c.label for c in selected if c.tile_mcc is None]
        if undefined:
            logger.warning(
                "Excluding %d condition(s) from the MCC leaderboard — "
                "tile-level MCC is undefined for them (degenerate tile "
                "confusion matrix, or MCC not computed); erratum E81 "
                "forbids ranking an undefined coefficient as 0.0, which "
                "the MCC scale reads as chance: %s",
                len(undefined), ", ".join(undefined),
            )
            selected = [c for c in selected if c.tile_mcc is not None]
        if undefined_metric_out is not None:
            undefined_metric_out.extend(undefined)

    # Sort by chosen metric descending at primary buffer
    selected.sort(
        key=lambda c: get_condition_score(c, primary_buffer, metric),
        reverse=True,
    )

    # Top-N filtering (union across all buffers).
    # ``top_n=0`` (or ``None``) disables the filter — include every
    # condition. The 12-stratum redesign (Stage 2, 2026-04-25) sets
    # ``--top-n 0`` for comprehensive paper-table coverage; the
    # default of 20 was kept for backward compatibility.
    if top_n is not None and top_n > 0 and len(selected) > top_n:
        # Collect sets of top-N labels at each buffer
        all_buffers = set()
        for c in selected:
            all_buffers.update(c.evaluations.keys())

        included_labels: set[str] = set()
        for buf_m in sorted(all_buffers):
            ranked = sorted(
                selected,
                key=lambda c: c.evaluations.get(buf_m, {}).get("f1", 0),
                reverse=True,
            )
            for c in ranked[:top_n]:
                included_labels.add(c.label)

        before = len(selected)
        selected = [c for c in selected if c.label in included_labels]
        logger.info(
            "Top-%d filter: %d → %d conditions (union across %d buffers)",
            top_n, before, len(selected), len(all_buffers),
        )
    elif top_n is None or top_n == 0:
        logger.info(
            "Top-N filter disabled (top_n=%s); including all %d conditions",
            top_n, len(selected),
        )

    logger.info(
        "Selected %d conditions (best F1=%.3f at %dm)",
        len(selected),
        selected[0].evaluations.get(primary_buffer, {}).get("f1", 0)
        if selected else 0,
        primary_buffer,
    )
    return selected


# ---------------------------------------------------------------------------
# Stage 4: Pairwise permutation tests
# ---------------------------------------------------------------------------


def _cache_path_pairwise(
    cache_dir: Path,
    label_a: str,
    label_b: str,
    metric: str = METRIC_F1,
    buffer_metres: int | None = None,
) -> Path:
    """Build canonical write path for a pairwise test (alphabetical order).

    The metric is folded into the directory name so F1 and MCC caches
    do not collide. F1 caches additionally namespace by buffer
    (``pairwise_f1_<buffer>m/<a>_vs_<b>.json``) because the F1
    permutation test is buffer-dependent — re-running at 30 / 40 / 50 /
    100 m must not silently reuse 20 m results. MCC caches keep the
    historical metric-only layout (``pairwise_mcc/...``) because the
    tile-level MCC permutation test is buffer-independent.

    ``buffer_metres`` is required for ``metric=f1``; it is ignored for
    other metrics.

    See :func:`_cache_path_pairwise_read` for the read-side fallback to
    the legacy ``pairwise/<a>_vs_<b>.json`` layout used by the original
    per-architecture tier tables.
    """
    a, b = sorted([slugify(label_a), slugify(label_b)])
    if metric == METRIC_F1:
        if buffer_metres is None:
            raise ValueError(
                "buffer_metres is required for F1 pairwise cache paths "
                "(F1 permutation tests are buffer-dependent)",
            )
        return (
            cache_dir
            / f"pairwise_f1_{buffer_metres}m"
            / f"{a}_vs_{b}.json"
        )
    return cache_dir / f"pairwise_{metric}" / f"{a}_vs_{b}.json"


def _cache_path_pairwise_read(
    cache_dir: Path,
    label_a: str,
    label_b: str,
    metric: str = METRIC_F1,
    buffer_metres: int | None = None,
) -> Path:
    """Resolve the cache file to read for a pairwise test.

    Returns the canonical write path (see
    :func:`_cache_path_pairwise`) if it exists. For ``metric=f1`` at
    ``buffer_metres=20`` only, falls back to the legacy
    ``pairwise/<a>_vs_<b>.json`` path so the existing 20 m cache from
    the original 12-stratum build is honoured without recomputation.
    For all other (metric, buffer) combinations, returns the canonical
    path even if it does not yet exist (caller checks ``is_file()``).
    """
    canonical = _cache_path_pairwise(
        cache_dir, label_a, label_b,
        metric=metric, buffer_metres=buffer_metres,
    )
    if canonical.is_file():
        return canonical
    if metric == METRIC_F1 and buffer_metres == 20:
        a, b = sorted([slugify(label_a), slugify(label_b)])
        legacy = cache_dir / "pairwise" / f"{a}_vs_{b}.json"
        if legacy.is_file():
            return legacy
    return canonical


def _pairwise_worker(
    label_a: str,
    label_b: str,
    geojson_a: str,
    geojson_b: str,
    ref_path: str,
    bounds_path: str,
    buffer_metres: int,
    n_permutations: int,
    seed: int,
    metric: str,
    cache_dir: str,
) -> dict:
    """Top-level worker for ProcessPoolExecutor-parallel pairwise tests.

    Defined at module scope so it pickles cleanly. Loads its own
    geojsons (no in-memory sharing between processes); the disk cache
    handles cross-pair geometric overlap. For each pair, computes the
    permutation test (F1 or MCC), writes the cache file, and returns
    the result dict. Idempotent — if the cache file already exists
    and is non-empty, the cached result is returned without
    recomputation.
    """
    import geopandas as _gpd

    cache_root = Path(cache_dir)
    # Canonical write path (buffer-aware for F1; metric-only for MCC).
    write_path = _cache_path_pairwise(
        cache_root, label_a, label_b,
        metric=metric, buffer_metres=buffer_metres,
    )
    # Read path may fall back to the legacy 20 m F1 layout.
    read_path = _cache_path_pairwise_read(
        cache_root, label_a, label_b,
        metric=metric, buffer_metres=buffer_metres,
    )
    if read_path.is_file():
        with open(read_path, encoding="utf-8") as f:
            return json.load(f)
    cache_file = write_path

    gdf_ref = load_geojson(Path(ref_path))
    gdf_bounds = load_geojson(Path(bounds_path))

    def _load(label: str, gj: str) -> "_gpd.GeoDataFrame":
        gdf = load_geojson_detections(Path(gj))
        if "source_tile" not in gdf.columns and not gdf.empty:
            joined = _gpd.sjoin(
                gdf, gdf_bounds[["tile_name", "geometry"]],
                how="left", predicate="intersects",
            )
            joined = joined[~joined.index.duplicated(keep="first")]
            gdf["source_tile"] = joined["tile_name"]
        return gdf

    gdf_a = _load(label_a, geojson_a)
    gdf_b = _load(label_b, geojson_b)

    if metric == METRIC_MCC:
        perm_result = run_permutation_test_mcc(
            gdf_a, gdf_b, gdf_ref, gdf_bounds,
            n_permutations=n_permutations, seed=seed,
        )
        result = {
            "label_a": label_a,
            "label_b": label_b,
            "metric": metric,
            "mcc_a": perm_result["global_a"]["mcc"],
            "mcc_b": perm_result["global_b"]["mcc"],
            "delta_mcc": perm_result["permutation_test"][
                "observed_mcc_diff"
            ],
            "p_value": perm_result["permutation_test"]["p_value"],
            "n_permutations": perm_result["permutation_test"][
                "n_permutations"
            ],
            "n_tiles": perm_result["permutation_test"]["n_tiles"],
        }
    else:
        perm_result = run_permutation_test(
            gdf_a, gdf_b, gdf_ref, gdf_bounds,
            buffer_metres=buffer_metres,
            n_permutations=n_permutations, seed=seed,
        )
        result = {
            "label_a": label_a,
            "label_b": label_b,
            "metric": METRIC_F1,
            "f1_a": perm_result["global_a"]["f1"],
            "f1_b": perm_result["global_b"]["f1"],
            "delta_f1": perm_result["permutation_test"][
                "observed_f1_diff"
            ],
            "p_value": perm_result["permutation_test"]["p_value"],
            "n_permutations": perm_result["permutation_test"][
                "n_permutations"
            ],
            "n_tiles": perm_result["permutation_test"]["n_tiles"],
        }

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result


def run_all_pairwise_tests(
    conditions: list[SelectedCondition],
    ref_path: Path,
    bounds_path: Path,
    buffer_metres: int,
    n_permutations: int,
    seed: int,
    cache_dir: Path,
    force: bool = False,
    metric: str = METRIC_F1,
    workers: int = 1,
) -> list[dict]:
    """Run C(N,2) pairwise permutation tests between all conditions.

    Each pairwise result is cached to disk under a metric-specific
    subdirectory so F1 and MCC caches do not collide. When
    ``workers > 1`` the pairs run in parallel via
    ``ProcessPoolExecutor``; each worker loads its own geojsons
    (cross-process geojson sharing is not implemented — disk cache
    elimnates the redundant work for already-tested pairs).

    Args:
        conditions: Selected conditions for the leaderboard.
        ref_path: Ground truth path.
        bounds_path: Bounds path.
        buffer_metres: Buffer for F1 computation. Ignored for MCC
            (buffer-invariant) but kept for API symmetry.
        n_permutations: Number of permutations.
        seed: Random seed.
        cache_dir: Cache directory.
        force: Force recomputation. (When True, removes cached pair
            files before dispatch; the workers always check cache
            first as an idempotency safeguard.)
        metric: ``"f1"`` (default) or ``"mcc"``.
        workers: Number of parallel worker processes (default 1 =
            sequential). Recommended: ``min(8, os.cpu_count())`` for
            I/O-bound permutation work.

    Returns:
        List of pairwise result dicts.
    """
    gdf_ref = load_geojson(ref_path)
    gdf_bounds = load_geojson(bounds_path)

    # GeoDataFrame cache (in-memory). Used only in the sequential
    # path; the parallel path loads independently per worker.
    gdf_cache: dict = {}

    def _load_gdf(cond: SelectedCondition):
        if cond.label not in gdf_cache:
            import geopandas as _gpd

            gdf = load_geojson_detections(cond.geojson_path)
            # Assign source_tile if missing (consensus GeoJSONs)
            if "source_tile" not in gdf.columns and not gdf.empty:
                joined = _gpd.sjoin(
                    gdf, gdf_bounds[["tile_name", "geometry"]],
                    how="left", predicate="intersects",
                )
                joined = joined[~joined.index.duplicated(keep="first")]
                gdf["source_tile"] = joined["tile_name"]
            gdf_cache[cond.label] = gdf
        return gdf_cache[cond.label]

    pairs = list(itertools.combinations(conditions, 2))
    n_pairs = len(pairs)
    results: list[dict] = []
    cached = 0

    logger.info(
        "Pairwise tests (%s): %d pairs at %dm (%d permutations, "
        "%d workers)",
        metric, n_pairs, buffer_metres, n_permutations, workers,
    )

    if workers > 1:
        # Parallel dispatch via ProcessPoolExecutor. Each worker
        # loads its geojsons independently; the disk pairwise cache
        # provides cross-pair idempotency.
        # First, drop missing pairs into a worker queue. Cached
        # pairs are read directly from disk and added to results.
        to_compute: list[tuple[SelectedCondition, SelectedCondition]] = []
        for (cond_a, cond_b) in pairs:
            cp = _cache_path_pairwise_read(
                cache_dir, cond_a.label, cond_b.label,
                metric=metric, buffer_metres=buffer_metres,
            )
            if not force and cp.is_file():
                with open(cp, encoding="utf-8") as f:
                    results.append(json.load(f))
                cached += 1
            else:
                to_compute.append((cond_a, cond_b))

        if to_compute:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                fut_map = {}
                for cond_a, cond_b in to_compute:
                    fut = executor.submit(
                        _pairwise_worker,
                        cond_a.label, cond_b.label,
                        str(cond_a.geojson_path),
                        str(cond_b.geojson_path),
                        str(ref_path), str(bounds_path),
                        buffer_metres, n_permutations, seed, metric,
                        str(cache_dir),
                    )
                    fut_map[fut] = (cond_a.label, cond_b.label)
                done = 0
                for fut in as_completed(fut_map):
                    a, b = fut_map[fut]
                    done += 1
                    try:
                        results.append(fut.result())
                        if done % 50 == 0 or done == len(to_compute):
                            logger.info(
                                "[%d/%d] pairwise done", done, len(to_compute),
                            )
                    except Exception as exc:
                        logger.error(
                            "[%d/%d] pairwise %s vs %s FAILED: %s",
                            done, len(to_compute), a, b, exc,
                        )
        logger.info(
            "Pairwise: %d cached, %d computed",
            cached, len(results) - cached,
        )
        return results

    # Sequential path (workers <= 1)
    for i, (cond_a, cond_b) in enumerate(pairs, 1):
        # Resolve read path (may fall back to legacy 20 m F1 layout) and
        # canonical write path separately so newly computed results land
        # in the buffer-aware location.
        read_cp = _cache_path_pairwise_read(
            cache_dir, cond_a.label, cond_b.label,
            metric=metric, buffer_metres=buffer_metres,
        )
        cp = _cache_path_pairwise(
            cache_dir, cond_a.label, cond_b.label,
            metric=metric, buffer_metres=buffer_metres,
        )

        if not force and read_cp.is_file():
            with open(read_cp, encoding="utf-8") as f:
                result = json.load(f)
            results.append(result)
            cached += 1
            continue

        logger.info(
            "[%d/%d] %s vs %s...", i, n_pairs, cond_a.label, cond_b.label,
        )
        gdf_a = _load_gdf(cond_a)
        gdf_b = _load_gdf(cond_b)

        if metric == METRIC_MCC:
            perm_result = run_permutation_test_mcc(
                gdf_a, gdf_b, gdf_ref, gdf_bounds,
                n_permutations=n_permutations,
                seed=seed,
            )
            result = {
                "label_a": cond_a.label,
                "label_b": cond_b.label,
                "metric": metric,
                "mcc_a": perm_result["global_a"]["mcc"],
                "mcc_b": perm_result["global_b"]["mcc"],
                "delta_mcc": perm_result["permutation_test"][
                    "observed_mcc_diff"
                ],
                "p_value": perm_result["permutation_test"]["p_value"],
                "n_permutations": perm_result["permutation_test"][
                    "n_permutations"
                ],
                "n_tiles": perm_result["permutation_test"]["n_tiles"],
            }
            cp.parent.mkdir(parents=True, exist_ok=True)
            with open(cp, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            results.append(result)
            continue

        # Default path: F1 micro-average permutation test.
        perm_result = run_permutation_test(
            gdf_a, gdf_b, gdf_ref, gdf_bounds,
            buffer_metres=buffer_metres,
            n_permutations=n_permutations,
            seed=seed,
        )

        # Build compact result (drop per-tile details for cache)
        result = {
            "label_a": cond_a.label,
            "label_b": cond_b.label,
            "metric": METRIC_F1,
            "f1_a": perm_result["global_a"]["f1"],
            "f1_b": perm_result["global_b"]["f1"],
            "delta_f1": perm_result["permutation_test"]["observed_f1_diff"],
            "p_value": perm_result["permutation_test"]["p_value"],
            "n_permutations": perm_result["permutation_test"]["n_permutations"],
            "n_tiles": perm_result["permutation_test"]["n_tiles"],
        }

        # Cache
        cp.parent.mkdir(parents=True, exist_ok=True)
        with open(cp, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        results.append(result)

    logger.info("Pairwise: %d cached, %d computed", cached, n_pairs - cached)
    return results


# ---------------------------------------------------------------------------
# Stage 5: BH-FDR correction and tiering
# ---------------------------------------------------------------------------


def apply_fdr_and_tier(
    pairwise_results: list[dict],
    conditions: list[SelectedCondition],
    fdr_q: float = DEFAULT_FDR_Q,
    metric: str = METRIC_F1,
) -> tuple[list[dict], list[list[SelectedCondition]]]:
    """Apply BH-FDR correction and group conditions into tiers.

    Uses a greedy clique-based algorithm: conditions are processed in
    the order received (already sorted by chosen metric descending).
    Each condition is added to the current tier if it is statistically
    indistinguishable from ALL existing members; otherwise a new tier
    starts.

    Args:
        pairwise_results: All C(N,2) pairwise test results.
        conditions: Selected conditions sorted by chosen metric
            descending.
        fdr_q: FDR threshold for significance.
        metric: ``"f1"`` (default) or ``"mcc"`` — used for logging
            only; the actual algorithm is metric-agnostic since the
            sort order and significance flags are pre-computed
            upstream.

    Returns:
        Tuple of ``(annotated_results, tiers)`` where tiers is a list
        of lists, each inner list being conditions in that tier.
    """
    if not pairwise_results:
        return [], [conditions] if conditions else []

    # Apply BH-FDR
    raw_pvalues = [r["p_value"] for r in pairwise_results]
    adjusted = apply_bh_correction(raw_pvalues, q=fdr_q)

    # Annotate results
    annotated: list[dict] = []
    for r, adj_p in zip(pairwise_results, adjusted):
        annotated.append({
            **r,
            "bh_adjusted_p": round(adj_p, 6),
            "significant": adj_p < fdr_q,
        })

    # Build lookup: (label_a, label_b) -> significant?
    sig_lookup: dict[tuple[str, str], bool] = {}
    for r in annotated:
        key = tuple(sorted([r["label_a"], r["label_b"]]))
        sig_lookup[key] = r["significant"]

    # Greedy clique-based tiering
    tiers: list[list[SelectedCondition]] = []
    current_tier: list[SelectedCondition] = []

    for cond in conditions:
        if not current_tier:
            current_tier.append(cond)
            continue

        # Check if this condition is indistinguishable from ALL in current tier
        all_indistinguishable = True
        for member in current_tier:
            key = tuple(sorted([cond.label, member.label]))
            if sig_lookup.get(key, False):
                all_indistinguishable = False
                break

        if all_indistinguishable:
            current_tier.append(cond)
        else:
            tiers.append(current_tier)
            current_tier = [cond]

    if current_tier:
        tiers.append(current_tier)

    n_sig = sum(1 for r in annotated if r["significant"])
    logger.info(
        "FDR: %d/%d pairs significant at q=%.2f → %d tiers",
        n_sig, len(annotated), fdr_q, len(tiers),
    )
    return annotated, tiers


# ---------------------------------------------------------------------------
# Stage 6: Output
# ---------------------------------------------------------------------------


def write_leaderboard_markdown(
    tiers: list[list[SelectedCondition]],
    buffer_metres: int,
    output_path: Path,
    metadata: dict,
) -> None:
    """Write Markdown leaderboard table grouped by tier.

    The header label and the score column adapt to the metric in
    ``metadata["metric"]`` (``"f1"`` or ``"mcc"``); F1 and CI columns
    are always shown for context.

    Args:
        tiers: List of tiers (each a list of SelectedConditions).
        buffer_metres: Buffer distance for displayed metrics.
        output_path: Output .md file path.
        metadata: Leaderboard metadata. Must include ``metric``.
    """
    metric = metadata.get("metric", METRIC_F1)
    fdr_q = metadata.get("fdr_q", DEFAULT_FDR_Q)
    metric_label = metric.upper()

    lines: list[str] = []
    lines.append(
        f"# Leaderboard ({metric_label} tiers) — {buffer_metres}m buffer"
    )
    lines.append("")
    lines.append(
        f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}"
    )
    lines.append(f"**Tiering metric**: {metric_label}")
    lines.append(f"**FDR q**: {fdr_q:g}")
    if metric == METRIC_MCC:
        lines.append(
            "**Note**: MCC is buffer-invariant in this codebase "
            "(tile-level binary classification). Threshold selection "
            "still maximises F1 at the primary buffer for cross-metric "
            "alignment; the per-buffer F1 column reflects that."
        )
    if metadata.get("name"):
        lines.append(f"**Scope**: {metadata['name']}")
    lines.append(
        f"**Conditions**: {sum(len(t) for t in tiers)} "
        f"in {len(tiers)} tier(s)"
    )
    lines.append("")

    rank = 0
    for tier_idx, tier in enumerate(tiers, 1):
        score_vals = [
            get_condition_score(c, buffer_metres, metric) for c in tier
        ]
        s_min = min(score_vals) if score_vals else 0
        s_max = max(score_vals) if score_vals else 0

        lines.append(
            f"## Tier {tier_idx} ({metric_label}: {s_min:.3f}–{s_max:.3f})"
        )
        lines.append("")
        if metric == METRIC_MCC:
            lines.append(
                "| # | Condition | Arch | Era | Track | K | t | "
                "MCC | F1@buf | F1 95% CI | P | R |"
            )
            lines.append(
                "|--:|-----------|:----:|:---:|:-----:|--:|--:|"
                "---:|---:|:------:|---:|---:|"
            )
        else:
            lines.append(
                "| # | Condition | Arch | Era | Track | K | t | "
                "F1 | 95% CI | P | R | MCC |"
            )
            lines.append(
                "|--:|-----------|:----:|:---:|:-----:|--:|--:|"
                "---:|:------:|---:|---:|---:|"
            )

        for cond in tier:
            rank += 1
            e = cond.evaluations.get(buffer_metres, {})
            f1 = e.get("f1", 0)
            ci_lo = e.get("f1_ci_lower", 0)
            ci_hi = e.get("f1_ci_upper", 0)
            p = e.get("precision", 0)
            r = e.get("recall", 0)

            # Architecture: PV (proposer-verifier) vs greedy (consensus) vs
            # single-pass+PV vs single-pass.
            if cond.category == "pv":
                arch = "PV"
            elif cond.category == "single-pass+PV":
                arch = "1-pass+PV"
            elif cond.category == "consensus":
                arch = "greedy"
            else:
                arch = "1-pass"

            if metric == METRIC_MCC:
                lines.append(
                    f"| {rank} | {cond.label} | {arch} | {cond.era} | "
                    f"{cond.track} | {cond.k} | {cond.best_threshold} | "
                    f"{_fmt_metric(cond.tile_mcc)} | "
                    f"{f1:.3f} | [{ci_lo:.3f}, {ci_hi:.3f}] | "
                    f"{p:.3f} | {r:.3f} |"
                )
            else:
                lines.append(
                    f"| {rank} | {cond.label} | {arch} | {cond.era} | "
                    f"{cond.track} | {cond.k} | {cond.best_threshold} | "
                    f"{f1:.3f} | [{ci_lo:.3f}, {ci_hi:.3f}] | "
                    f"{p:.3f} | {r:.3f} | {_fmt_metric(cond.tile_mcc)} |"
                )

        lines.append("")

    # Erratum E81: conditions whose tile-level MCC is undefined are
    # excluded from the MCC tiers by ``select_best_thresholds`` rather
    # than ranked at 0.0. They are named here so the exclusion is on
    # the face of the record instead of being a silent omission.
    undefined_labels = metadata.get("mcc_undefined_conditions") or []
    if metric == METRIC_MCC and undefined_labels:
        lines.append(f"## MCC {UNDEFINED_DISPLAY} (not ranked)")
        lines.append("")
        lines.append(
            f"{len(undefined_labels)} condition(s) are absent from the "
            "tiers above because their tile-level MCC is not computable: "
            "the 2 x 2 tile confusion matrix is degenerate, so the "
            "denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes. "
            "They are **not** ranked at 0.000, because 0 on this scale "
            "means \"random\" (§ 4.2 of the preregistration) and would "
            "assert a measurement that was not made. See erratum E81 in "
            "`docs/methodology/preregistration/protocol-errata.md`."
        )
        lines.append("")
        for label in undefined_labels:
            lines.append(f"- {label}")
        lines.append("")
    elif metric == METRIC_F1 and any(
        c.tile_mcc is None for tier in tiers for c in tier
    ):
        lines.append(
            f"**MCC `{UNDEFINED_DISPLAY}`** — the tile-level Matthews "
            "Correlation Coefficient is not computable for the rows so "
            "marked (degenerate 2 x 2 tile confusion matrix, or MCC not "
            "computed for that condition). It is reported as "
            f"`{UNDEFINED_DISPLAY}` rather than 0.000 because 0 on this "
            "scale means \"random\" (§ 4.2 of the preregistration). "
            "Tiering here is on F1 and is unaffected. See erratum E81 in "
            "`docs/methodology/preregistration/protocol-errata.md`."
        )
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Markdown leaderboard written to %s", output_path)


def write_leaderboard_json(
    tiers: list[list[SelectedCondition]],
    all_evaluations: dict[str, dict[int, dict]],
    pairwise_annotated: list[dict],
    metadata: dict,
    output_path: Path,
) -> None:
    """Write machine-readable leaderboard with full provenance.

    Args:
        tiers: Tier assignments.
        all_evaluations: Complete evaluation data.
        pairwise_annotated: Annotated pairwise results with FDR.
        metadata: Leaderboard metadata.
        output_path: Output .json file path.
    """
    tier_data = []
    for tier_idx, tier in enumerate(tiers, 1):
        tier_data.append({
            "tier": tier_idx,
            "conditions": [
                {
                    "label": c.label,
                    "era": c.era,
                    "track": c.track,
                    "category": c.category,
                    "k": c.k,
                    "best_threshold": c.best_threshold,
                    "geojson": str(c.geojson_path),
                    "evaluations": c.evaluations,
                    # Tile-level MCC (buffer-invariant); JSON ``null``
                    # when it is undefined — the tile confusion matrix
                    # is degenerate, or MCC was not computed for this
                    # evaluation pass. Erratum E81: this used to be
                    # coerced to 0.0, which consumers could not tell
                    # apart from a measured chance-level coefficient.
                    "tile_mcc": c.tile_mcc,
                }
                for c in tier
            ],
        })

    output = {
        "script": "build_tiered_leaderboard.py",
        "version": __version__,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "metadata": metadata,
        "n_conditions": sum(len(t) for t in tiers),
        "n_tiers": len(tiers),
        "tiers": tier_data,
        "pairwise_tests": pairwise_annotated,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logger.info("JSON leaderboard written to %s", output_path)


def write_all_evaluations_json(
    all_evaluations: dict[str, dict[int, dict]],
    output_path: Path,
) -> None:
    """Write complete threshold × buffer sweep for all conditions.

    Args:
        all_evaluations: Nested dict from ``evaluate_all_conditions()``.
        output_path: Output .json file path.
    """
    # Convert int keys to strings for JSON
    serialisable = {}
    for label, thresholds in all_evaluations.items():
        serialisable[label] = {
            str(t): result for t, result in thresholds.items()
        }

    output = {
        "script": "build_tiered_leaderboard.py",
        "version": __version__,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "n_conditions": len(serialisable),
        "evaluations": serialisable,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logger.info("All evaluations written to %s", output_path)


def print_tier_summary(
    tiers: list[list[SelectedCondition]],
    primary_buffer: int,
    metric: str = METRIC_F1,
) -> None:
    """Print a human-readable tier summary to the console.

    Args:
        tiers: Tier assignments.
        primary_buffer: Buffer for displayed score.
        metric: ``"f1"`` or ``"mcc"``.
    """
    label = metric.upper()
    print(f"\n{'=' * 72}")
    print(f"LEADERBOARD TIERS ({label}, {primary_buffer}m buffer)")
    print(f"{'=' * 72}")

    rank = 0
    for tier_idx, tier in enumerate(tiers, 1):
        score_vals = [
            get_condition_score(c, primary_buffer, metric) for c in tier
        ]
        print(
            f"\nTier {tier_idx} "
            f"({label}: {min(score_vals):.3f}–{max(score_vals):.3f}, "
            f"{len(tier)} conditions)"
        )
        for cond in tier:
            rank += 1
            score = get_condition_score(cond, primary_buffer, metric)
            print(
                f"  {rank:>3}. {cond.label:<40} {label}={score:.3f}  "
                f"t={cond.best_threshold}"
            )

    print(f"\n{'=' * 72}")
    print(
        f"Total: {sum(len(t) for t in tiers)} conditions "
        f"in {len(tiers)} tiers"
    )
    print(f"{'=' * 72}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_cli() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Build tiered leaderboard from detection conditions. "
            "Evaluates conditions, runs round-robin pairwise permutation "
            "tests, applies BH-FDR correction, and groups into tiers."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Input mode
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--spec", type=Path,
        help="YAML leaderboard spec file",
    )
    input_group.add_argument(
        "--inventory", type=Path,
        help="Condition inventory JSON (with --era, --track filters)",
    )

    # Inventory filters
    parser.add_argument("--era", type=int, choices=[1, 2, 3])
    parser.add_argument("--track", choices=["text", "image"])
    parser.add_argument(
        "--architecture",
        choices=["single-pass", "consensus", "single-pass+PV", "pv"],
        help="Filter inventory to one architecture",
    )
    parser.add_argument("--hypothesis", type=str)
    parser.add_argument(
        "--status", nargs="+", default=["READY"],
        help=(
            "Inventory status values to include "
            "(default: READY). Common additions: PV_READY, "
            "SINGLE_PASS_ONLY."
        ),
    )

    # Evaluation
    parser.add_argument(
        "--bounds", type=Path, default=DEFAULT_BOUNDS,
        help=f"Evaluation bounds GeoJSON (default: {DEFAULT_BOUNDS.name})",
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=DEFAULT_GROUND_TRUTH,
        help="Ground truth reference GeoJSON",
    )
    parser.add_argument(
        "--buffers", type=int, nargs="+", default=DEFAULT_BUFFERS,
        help=f"Buffer distances in metres (default: {DEFAULT_BUFFERS})",
    )
    parser.add_argument(
        "--primary-buffer", type=int, default=20,
        help=(
            "Buffer used for pairwise permutation tests, tier "
            "construction, and tier-table outputs (default: 20). Per-cell "
            "thresholds are by default selected at the same buffer; pass "
            "--threshold-buffer to decouple them (Option A: fix "
            "thresholds at one buffer, re-tier at another)."
        ),
    )
    parser.add_argument(
        "--threshold-buffer", type=int, default=None,
        help=(
            "Buffer used for per-cell threshold selection. Defaults to "
            "--primary-buffer (the historical behaviour where threshold "
            "selection and tier construction share a buffer). When set "
            "explicitly (typically to 20 for the per-architecture "
            "re-tiering work), thresholds are fixed at this buffer while "
            "pairwise tests + tiering proceed at --primary-buffer."
        ),
    )
    parser.add_argument(
        "--bootstrap", type=int, default=DEFAULT_BOOTSTRAP,
        help=f"Bootstrap iterations for CIs (default: {DEFAULT_BOOTSTRAP})",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
        help=f"Random seed (default: {DEFAULT_SEED})",
    )

    # Tiering
    parser.add_argument(
        "--fdr-q", type=float, default=DEFAULT_FDR_Q,
        help=f"BH-FDR threshold (default: {DEFAULT_FDR_Q})",
    )
    parser.add_argument(
        "--n-permutations", type=int, default=DEFAULT_N_PERMUTATIONS,
        help=f"Permutation test iterations (default: {DEFAULT_N_PERMUTATIONS:,})",
    )
    parser.add_argument(
        "--top-n", type=int, default=DEFAULT_TOP_N,
        help=(
            f"Inclusion: top-N at any buffer (default: {DEFAULT_TOP_N}). "
            "Pass 0 (or any non-positive value) to disable filtering and "
            "include all conditions in the tier table."
        ),
    )
    parser.add_argument(
        "--metric", choices=list(SUPPORTED_METRICS), default=METRIC_F1,
        help=(
            f"Test statistic for tiering (default: {METRIC_F1!r}). "
            f"{METRIC_F1!r} uses micro-average F1 with the buffer-aware "
            f"tile-swap permutation test. {METRIC_MCC!r} uses tile-level "
            "Matthews Correlation Coefficient with a per-tile (TP, TN, "
            "FP, FN) classification swap. Threshold selection always "
            "uses F1 at the primary buffer for cross-metric alignment."
        ),
    )

    # Execution
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--workers", type=int, default=4,
        help="Parallel evaluation workers (default: 4)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--skip-evaluation", action="store_true",
        help="Use cached evaluations only",
    )
    parser.add_argument(
        "--skip-pairwise", action="store_true",
        help="Use cached pairwise results only",
    )
    parser.add_argument("--force", action="store_true")

    # Meta
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """Build tiered leaderboard: evaluate, test, tier, output.

    Returns:
        Exit code: 0 = success, 1 = partial failure, 2 = fatal.
    """
    args = build_cli().parse_args()
    # Default --threshold-buffer to --primary-buffer (preserves the
    # historical behaviour where threshold selection and tier
    # construction share a buffer). When explicitly supplied, the two
    # decouple — see Patch B in the per-architecture re-tiering plan.
    if args.threshold_buffer is None:
        args.threshold_buffer = args.primary_buffer
    setup_logging()

    logger.info(
        "build_tiered_leaderboard.py v%s — git %s",
        __version__, get_git_commit(),
    )

    # Stage 1: Resolve conditions
    if args.spec:
        config, conditions = resolve_conditions_from_yaml(args.spec)
        # Override defaults from YAML config
        eval_cfg = config.get("evaluation", {})
        if "bounds" in eval_cfg:
            args.bounds = PROJECT_ROOT / eval_cfg["bounds"]
        if "ground_truth" in eval_cfg:
            args.ground_truth = PROJECT_ROOT / eval_cfg["ground_truth"]
        if "buffers" in eval_cfg:
            args.buffers = eval_cfg["buffers"]
    else:
        conditions = resolve_conditions_from_inventory(
            args.inventory,
            era=args.era,
            track=args.track,
            hypothesis=args.hypothesis,
            architecture=args.architecture,
            status_filter=args.status,
        )
        config = {}

    if not conditions:
        logger.error("No conditions resolved — nothing to do")
        return 2

    logger.info("Resolved %d conditions", len(conditions))

    if args.dry_run:
        print(f"\nDry run: {len(conditions)} conditions")
        print(f"{'Label':<45} {'Era':>3} {'Track':<6} {'K':>3} {'Thresholds'}")
        print("-" * 80)
        for c in conditions:
            t_range = (
                f"t={c.thresholds[0]}..{c.thresholds[-1]}"
                if len(c.thresholds) > 1
                else f"t={c.thresholds[0]}"
            )
            print(f"{c.label:<45} {c.era:>3} {c.track:<6} {c.k:>3} {t_range}")
        return 0

    # Validate paths
    if not args.bounds.is_file():
        logger.error("Bounds file not found: %s", args.bounds)
        return 2
    if not args.ground_truth.is_file():
        logger.error("Ground truth not found: %s", args.ground_truth)
        return 2

    cache_dir = args.output_dir / ".cache"
    metadata = {
        "name": config.get("metadata", {}).get("name", ""),
        "primary_buffer": args.primary_buffer,
        "threshold_buffer": args.threshold_buffer,
        "buffers": args.buffers,
        "fdr_q": args.fdr_q,
        "n_permutations": args.n_permutations,
        "top_n": args.top_n,
        "metric": args.metric,
        "bootstrap": args.bootstrap,
        "seed": args.seed,
        "bounds": str(args.bounds),
        "n_conditions_input": len(conditions),
    }

    # Stage 2: Evaluate
    if not args.skip_evaluation:
        start = time.monotonic()
        all_evaluations = evaluate_all_conditions(
            conditions,
            ref_path=args.ground_truth,
            bounds_path=args.bounds,
            buffers=args.buffers,
            n_bootstrap=args.bootstrap,
            seed=args.seed,
            cache_dir=cache_dir,
            workers=args.workers,
            force=args.force,
        )
        logger.info("Stage 2 complete in %.1fs", time.monotonic() - start)
    else:
        logger.info("Skipping evaluation (--skip-evaluation)")
        # Load from cache
        all_evaluations = {}
        for cond in conditions:
            all_evaluations[cond.label] = {}
            for t in cond.thresholds:
                merged = {"label": cond.label, "n_detections": 0, "buffers": []}
                all_cached = True
                tile_classification: dict | None = None
                for b in args.buffers:
                    cp = _cache_path_eval(cache_dir, cond.label, t, b)
                    if cp.is_file():
                        with open(cp, encoding="utf-8") as f:
                            buf_data = json.load(f)
                        if "n_detections" in buf_data:
                            merged["n_detections"] = buf_data.pop("n_detections")
                        if (
                            tile_classification is None
                            and "__tile_classification__" in buf_data
                        ):
                            tile_classification = buf_data.pop(
                                "__tile_classification__",
                            )
                        else:
                            buf_data.pop("__tile_classification__", None)
                        merged["buffers"].append(buf_data)
                    else:
                        all_cached = False
                        break
                if tile_classification is not None:
                    merged["tile_classification"] = tile_classification
                if all_cached and merged["buffers"]:
                    all_evaluations[cond.label][t] = merged

    # Stage 3: Select thresholds at --threshold-buffer (defaults to
    # --primary-buffer). Decoupling the two enables Option A re-tiering:
    # fix per-cell thresholds at one buffer (e.g. 20 m) and re-run
    # pairwise + tiering at another (e.g. 30 / 40 / 50 / 100 m).
    if args.threshold_buffer != args.primary_buffer:
        logger.info(
            "Threshold selection at %dm; pairwise + tiering at %dm "
            "(Option A semantics)",
            args.threshold_buffer, args.primary_buffer,
        )
    # Erratum E81: conditions the scoring metric cannot score are
    # dropped inside select_best_thresholds; collect their labels so
    # the Markdown can name them rather than silently omitting them.
    mcc_undefined: list[str] = []
    selected = select_best_thresholds(
        conditions, all_evaluations,
        primary_buffer=args.threshold_buffer,
        top_n=args.top_n,
        metric=args.metric,
        undefined_metric_out=mcc_undefined,
    )
    metadata["mcc_undefined_conditions"] = mcc_undefined

    if not selected:
        logger.error("No conditions survived threshold selection")
        return 2

    # Stage 4: Pairwise tests
    if not args.skip_pairwise and len(selected) > 1:
        start = time.monotonic()
        pairwise_results = run_all_pairwise_tests(
            selected,
            ref_path=args.ground_truth,
            bounds_path=args.bounds,
            buffer_metres=args.primary_buffer,
            n_permutations=args.n_permutations,
            seed=args.seed,
            cache_dir=cache_dir,
            force=args.force,
            metric=args.metric,
            workers=args.workers,
        )
        logger.info("Stage 4 complete in %.1fs", time.monotonic() - start)
    elif args.skip_pairwise and len(selected) > 1:
        logger.info("Skipping pairwise (--skip-pairwise)")
        # Load from cache
        pairwise_results = []
        expected_pairs = len(selected) * (len(selected) - 1) // 2
        missing_pairs = 0
        for a, b in itertools.combinations(selected, 2):
            cp = _cache_path_pairwise_read(
                cache_dir, a.label, b.label,
                metric=args.metric,
                buffer_metres=args.primary_buffer,
            )
            if cp.is_file():
                with open(cp, encoding="utf-8") as f:
                    pairwise_results.append(json.load(f))
            else:
                missing_pairs += 1
                logger.warning(
                    "Missing cached pairwise: %s vs %s", a.label, b.label,
                )
        if missing_pairs > 0:
            logger.error(
                "%d/%d pairwise results missing from cache. "
                "Run without --skip-pairwise to compute them.",
                missing_pairs, expected_pairs,
            )
            return 2
    else:
        pairwise_results = []

    # Stage 5: FDR + tiering
    pairwise_annotated, tiers = apply_fdr_and_tier(
        pairwise_results, selected, fdr_q=args.fdr_q,
        metric=args.metric,
    )

    # Stage 6: Output. The metric goes into the filename so F1 and MCC
    # tier tables co-exist in the same output directory without
    # collision. The historical layout (no metric infix) is preserved
    # for ``metric=f1`` to keep prior consumers working.
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metric_infix = "" if args.metric == METRIC_F1 else f"_{args.metric}"
    fdr_infix = "" if args.fdr_q == DEFAULT_FDR_Q else (
        f"_q{int(round(args.fdr_q * 100)):02d}"
    )

    # Render Markdown only at the primary buffer. Earlier versions
    # rendered MD at every buffer in ``args.buffers`` using the same
    # primary-buffer-specific ``tiers`` data, which caused per-buffer
    # F1 re-tiering drivers (running once per primary buffer with the
    # full ``--buffers`` list) to overwrite each other's MD outputs.
    # The JSON below is also primary-buffer-only by the same logic.
    out_md = (
        args.output_dir
        / f"leaderboard_tiers{metric_infix}{fdr_infix}_"
        f"{args.primary_buffer}m.md"
    )
    write_leaderboard_markdown(
        tiers, args.primary_buffer, out_md, metadata,
    )

    out_json = (
        args.output_dir
        / f"leaderboard_tiers{metric_infix}{fdr_infix}_"
        f"{args.primary_buffer}m.json"
    )
    write_leaderboard_json(
        tiers, all_evaluations, pairwise_annotated, metadata, out_json,
    )
    # The full evaluation sweep is metric-independent — keep one file.
    write_all_evaluations_json(
        all_evaluations,
        args.output_dir / "leaderboard_all_evaluations.json",
    )

    print_tier_summary(tiers, args.primary_buffer, metric=args.metric)

    return 0


if __name__ == "__main__":
    sys.exit(main())
