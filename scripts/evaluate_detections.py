#!/usr/bin/env python3
"""Evaluate detection GeoJSON files against ground truth.

General-purpose evaluation script for single-pass or arbitrary detection
outputs. Computes F1, Precision, Recall with 95% bootstrap confidence
intervals at one or more spatial buffer distances. Supports evaluating
individual runs or averaging across multiple runs of the same condition.

This is the fundamental evaluation building block — other scripts
(consensus sweeps, PV threshold sweeps) build on the same library
functions but add condition-specific logic. Use this script when you
have plain detection GeoJSON files and want metrics.

Usage:
    # Single file at default 20m buffer
    python scripts/evaluate_detections.py \\
        --detections path/to/detections.geojson

    # Multiple files (averaged as independent runs of the same condition)
    python scripts/evaluate_detections.py \\
        --detections run_1/detections.geojson run_2/detections.geojson

    # All passes in a directory (both naming conventions resolved automatically)
    python scripts/evaluate_detections.py \\
        --detections-dir outputs/retest/h11-single-pass-384-t0/brief-text-t0

    # Multiple buffer distances with custom output
    python scripts/evaluate_detections.py \\
        --detections path/to/detections.geojson \\
        --buffers 20 30 40 50 \\
        --output-dir results/my-evaluation

Created: 2026-03-27
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import multiprocessing
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib_detection_paths import resolve_pool_passes  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    CI_FLAG_BASIS_FULL,
    COVERAGE_STATUS_NORMAL,
    COVERAGE_STATUS_PARTIAL,
    COVERAGE_STATUS_SPARSE,
    DEFAULT_CRS,
    bootstrap_ci,
    bootstrap_tile_classification_ci,
    calculate_f1_internal,
    calculate_tile_classification,
    measured_exclusion,
    read_processed_tiles,
)

#: Coverage statuses ordered worst-last, for the "worst case wins" rollups
#: across buffers and across runs. ``partial_coverage`` (E72 — the detection
#: set does not cover the bounds it is scored against) outranks
#: ``sparse_cross_grid`` (the CIs are shaky) because it invalidates the
#: point estimate itself, not just its interval.
_COVERAGE_SEVERITY: dict[str, int] = {
    COVERAGE_STATUS_NORMAL: 0,
    COVERAGE_STATUS_SPARSE: 1,
    COVERAGE_STATUS_PARTIAL: 2,
}


def _worst_coverage_status(statuses: list[str]) -> str:
    """Return the most severe coverage status in ``statuses``.

    Args:
        statuses: Coverage-status strings. Unrecognised values are treated
            as ``"normal"`` so an unexpected label can never mask a real
            flag by sorting above it.

    Returns:
        The most severe status present, or ``"normal"`` for an empty list.
    """
    if not statuses:
        return COVERAGE_STATUS_NORMAL
    return max(statuses, key=lambda s: _COVERAGE_SEVERITY.get(s, 0))


# ── Undefined-metric rendering (errata E81) ───────────────────────────

# Rendered in human-readable output wherever a tile-level metric is not
# computable. Deliberately a word rather than a number: the whole point of
# E81 is that no numeral on the MCC scale can stand in for "undefined"
# without asserting something the data do not support.
UNDEFINED_DISPLAY = "undefined"


def _observed_metric(block: Any) -> float | None:
    """Return the OBSERVED tile statistic from a ``tile_classification`` block.

    Defect D30 (Session 137 audit, finding F6): the CSV and Markdown
    writers used to publish ``block["mean"]`` — the mean of the bootstrap
    resample distribution — under the bare names ``mcc`` /
    ``sensitivity`` / ``specificity``. Those names denote the statistic
    computed on the observed tile confusion matrix, which the block keeps
    separately as ``point``. The two differ in the third or fourth
    decimal place (the corpus maximum measured on 2026-08-20 was 0.0151),
    so the published column was a different quantity from the one its
    header named.

    Args:
        block: One metric block of a ``tile_classification`` dict, i.e.
            ``{"point": …, "mean": …, "ci_lower": …, …}``. A bare float
            (a legacy adapter shape) and ``None`` are tolerated.

    Returns:
        The observed statistic, or ``None`` when it is undefined
        (degenerate tile confusion matrix — errata E81). ``mean`` is used
        ONLY when the block carries no ``point`` key at all, which marks a
        pre-``point`` in-memory shape; a ``point`` that is present and
        ``None`` is an undefined measurement and is returned as ``None``,
        never silently replaced by the resample mean.

    Examples:
        >>> _observed_metric({"point": 0.6924, "mean": 0.6925})
        0.6924
        >>> _observed_metric({"point": None, "mean": 0.31}) is None
        True
        >>> _observed_metric({"mean": 0.6925})
        0.6925
    """
    if block is None:
        return None
    if isinstance(block, (int, float)):
        return float(block)
    if not isinstance(block, dict):
        return None
    if "point" in block:
        return block["point"]
    return block.get("mean")


def _csv_metric(val: float | None) -> float | str:
    """Render a possibly-undefined metric for a CSV cell.

    Args:
        val: The metric value, or ``None`` when it is undefined.

    Returns:
        ``val`` unchanged when it is a number, or ``""`` (an empty cell)
        when it is ``None``. Errata E81: an empty cell is the only
        honest CSV rendering of an undefined metric — ``0`` would be
        read as a measurement.

    Examples:
        >>> _csv_metric(0.0)
        0.0
        >>> _csv_metric(None)
        ''
    """
    return "" if val is None else val


def _safe_round(val: float | None, digits: int = 4) -> float | None:
    """Round a metric value, preserving ``None`` for an undefined metric.

    Errata E81 (2026-08-18): this helper used to return ``0.0`` for
    ``None``. The tile-level Matthews Correlation Coefficient (MCC) is
    *undefined* when the 2 x 2 tile confusion matrix is degenerate, and
    ``0.0`` is not a neutral placeholder for it — § 4.2 of the
    preregistration labels ``0`` on this scale "random", so the
    substitution published nine conditions as performing at chance where
    the metric was simply not computable. ``None`` serialises to JSON
    ``null``, which readers and downstream consumers can tell apart from
    a measured zero. A genuine zero — for example the specificity of a
    condition that false-positives on every reference-empty tile — still
    comes through as ``0.0``. Distinguishing those two cases is the
    entire point of the change.

    Args:
        val: The value to round, or ``None`` when the underlying metric
            is undefined.
        digits: Decimal places (default 4, the published precision of
            the ``tile_classification`` block).

    Returns:
        The rounded ``float``, or ``None`` when ``val`` is ``None``.

    Examples:
        >>> _safe_round(0.06651234)
        0.0665
        >>> _safe_round(0.0)
        0.0
        >>> _safe_round(None) is None
        True
    """
    return round(val, digits) if val is not None else None


def build_tile_classification_block(
    tile_class: dict[str, Any],
    tile_ci: dict[str, Any],
) -> dict[str, Any]:
    """Assemble the published ``tile_classification`` block for one pass.

    Pairs the deterministic point estimates from
    :func:`lib_advanced_metrics.calculate_tile_classification` with the
    bootstrap distribution summary from
    :func:`lib_advanced_metrics.bootstrap_tile_classification_ci`.

    ``point`` fields carry the deterministic estimate computed across all
    tiles (no bootstrap). The § 7.5 verifier fix needs a named field that
    is invariant to bootstrap iteration count; ``mean`` is the bootstrap
    distribution mean and is not deterministic across seed changes.

    Every numeric field passes through :func:`_safe_round`, so an
    undefined metric arrives at the JSON as ``null`` rather than ``0.0``
    (errata E81).

    Args:
        tile_class: Result of ``calculate_tile_classification`` — the
            confusion counts plus deterministic MCC / sensitivity /
            specificity (any of which may be ``None``).
        tile_ci: Result of ``bootstrap_tile_classification_ci`` — per
            metric ``mean`` / ``ci_lower`` / ``ci_upper`` / ``method``.

    Returns:
        The ``tile_classification`` dict as published in
        ``evaluation.json``.
    """
    block: dict[str, Any] = {
        "confusion": {
            "tp": tile_class["tp"],
            "tn": tile_class["tn"],
            "fp": tile_class["fp"],
            "fn": tile_class["fn"],
        },
    }
    for metric in ("mcc", "sensitivity", "specificity"):
        ci = tile_ci[metric]
        block[metric] = {
            "point": _safe_round(tile_class.get(metric)),
            "mean": _safe_round(ci["mean"]),
            "ci_lower": _safe_round(ci["ci_lower"]),
            "ci_upper": _safe_round(ci["ci_upper"]),
            # D36: measured, never defaulted — see the buffer-row comment
            # in :func:`evaluate_single_run`.
            "method": ci.get("method"),
        }
    return block


def aggregate_tile_classification(
    mcc_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Average per-pass ``tile_classification`` blocks over DEFINED passes.

    Errata E81 (2026-08-18): an undefined tile metric used to reach this
    function as a coerced ``0.0``, indistinguishable from a measurement,
    so a cell with two computable passes and one degenerate pass
    published a mean pulled toward the value the § 4.2 scale legend calls
    "random" — ``0.0443 = mean(0.0665, 0, 0.0665)`` where the honest
    answer over the defined passes is ``0.0665``. Undefined passes now
    arrive as ``None`` and are excluded from the mean, and the block
    records how many passes actually contributed.

    Args:
        mcc_results: Per-pass ``tile_classification`` blocks, in run
            order, as produced by :func:`build_tile_classification_block`.

    Returns:
        An aggregated ``tile_classification`` block. Each metric carries
        ``mean`` / ``ci_lower`` / ``ci_upper`` (and ``point`` when the
        per-pass blocks supply it), each of which is ``None`` when no
        pass was defined; plus ``n_runs`` (passes carrying the metric)
        and ``n_runs_defined`` (passes that contributed a value). The
        block also carries ``confusion`` — **run 1's matrix, not a sum
        or a mean** — and ``confusion_source`` recording that fact.

    Examples:
        >>> blocks = [
        ...     {"mcc": {"point": 0.0665, "mean": 0.05, "ci_lower": 0.0,
        ...              "ci_upper": 0.12}},
        ...     {"mcc": {"point": None, "mean": None, "ci_lower": None,
        ...              "ci_upper": None}},
        ... ]
        >>> agg = aggregate_tile_classification(blocks)
        >>> agg["mcc"]["point"], agg["mcc"]["n_runs_defined"]
        (0.0665, 1)
    """
    avg: dict[str, Any] = {}
    for metric in ("mcc", "sensitivity", "specificity"):
        values = [m[metric] for m in mcc_results if metric in m]
        if not values:
            continue
        metric_block: dict[str, Any] = {}
        for key in ("mean", "ci_lower", "ci_upper"):
            defined = [
                v[key] for v in values if key in v and v[key] is not None
            ]
            metric_block[key] = (
                round(float(np.mean(defined)), 4) if defined else None
            )
        point_present = [v for v in values if "point" in v]
        point_defined = [
            v["point"] for v in point_present if v["point"] is not None
        ]
        if point_present:
            metric_block["point"] = (
                round(float(np.mean(point_defined)), 4)
                if point_defined else None
            )
        # Definedness bookkeeping: a reader must be able to see that a
        # "mean across 3 runs" was in fact a mean across 2. Counted on
        # the deterministic ``point`` where present, falling back to the
        # bootstrap ``mean`` for legacy per-pass blocks that predate the
        # ``point`` field.
        if point_present:
            n_defined = len(point_defined)
        else:
            n_defined = len([
                v for v in values if v.get("mean") is not None
            ])
        metric_block["n_runs"] = len(values)
        metric_block["n_runs_defined"] = n_defined
        avg[metric] = metric_block

    # Use the first run's confusion matrix as representative. E81 flagged
    # that this is easy to misread as a pooled matrix — a run-1 matrix
    # with TN = 1 sitting beside a mean contaminated by a *different*
    # run's degenerate matrix is what made the defect invisible on the
    # face of the record — so the provenance is now stated in the block.
    avg["confusion"] = mcc_results[0].get("confusion", {}) if mcc_results else {}
    avg["confusion_source"] = "run_1"
    return avg


def _fmt_metric(val: float | None, digits: int = 3) -> str:
    """Format a possibly-undefined metric for human-readable output.

    Args:
        val: The metric value, or ``None`` when it is undefined
            (degenerate tile confusion matrix — see errata E81).
        digits: Decimal places for the numeric case (default 3, matching
            the precision used in the evaluation Markdown tables).

    Returns:
        The formatted number, or :data:`UNDEFINED_DISPLAY` for ``None``.

    Examples:
        >>> _fmt_metric(0.2132)
        '0.213'
        >>> _fmt_metric(0.0)
        '0.000'
        >>> _fmt_metric(None)
        'undefined'
    """
    if val is None:
        return UNDEFINED_DISPLAY
    return f"{val:.{digits}f}"


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

__version__ = "1.0.0"

# ── Defaults ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_GROUND_TRUTH = (
    PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
)
DEFAULT_BOUNDS = (
    PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
)
DEFAULT_BUFFERS = [20]
DEFAULT_BOOTSTRAP = 1000
DEFAULT_SEED = 42


# ── Metadata helpers ──────────────────────────────────────────────────

# Relative script path used for provenance in the _metadata block. Fixed
# so that the recorded path is stable across invocations, regardless of
# the caller's current working directory.
_SCRIPT_RELATIVE_PATH = "scripts/evaluate_detections.py"


def _git_short_hash(repo_root: Path) -> str:
    """Return the short Git hash of HEAD, or 'unknown' on failure.

    Runs `git rev-parse --short HEAD` in the given repository root. Any
    failure mode (git not installed, not a repository, non-zero exit
    code) is mapped to the string ``"unknown"`` so that callers never
    have to handle exceptions.

    Args:
        repo_root: Path to the Git repository (typically the project
            root). The command is executed with this as its working
            directory.

    Returns:
        The short commit hash, or ``"unknown"`` if it cannot be
        determined.
    """
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, OSError):
        return "unknown"
    if proc.returncode != 0:
        return "unknown"
    value = proc.stdout.strip()
    return value or "unknown"


def _git_status(repo_root: Path) -> str:
    """Return 'clean' if the working tree is clean, else 'dirty'.

    Uses ``git status --porcelain``: an empty output indicates a clean
    tree, any non-empty output indicates uncommitted changes. If git is
    unavailable or the call fails, returns ``"unknown"`` so reviewers
    can still interpret the field.

    Args:
        repo_root: Path to the Git repository to inspect.

    Returns:
        One of ``"clean"``, ``"dirty"``, or ``"unknown"``.
    """
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, OSError):
        return "unknown"
    if proc.returncode != 0:
        return "unknown"
    return "clean" if proc.stdout.strip() == "" else "dirty"


def _input_git_states(paths: list[Any]) -> dict[str, str]:
    """Classify each recipe input's git state at scoring time (defect D40).

    The E82 pre-launch audit found ~324 committed evaluations that were
    scored against inputs later changed in git — sometimes a working tree
    committed minutes after scoring — leaving artefacts that do not
    reproduce from current inputs. This classifier makes that state
    visible IN the artefact at scoring time, so input-vintage drift is
    disclosed rather than discovered by a later replay campaign.

    Classes: ``clean`` (tracked, no uncommitted changes), ``modified``
    (tracked, uncommitted changes present), ``untracked`` (exists,
    neither tracked nor ignored), ``ignored`` (gitignored by design —
    e.g. the regenerable tile trees), ``outside-repo`` (not under the
    repository root — e.g. a replay's temp materialisation), and
    ``missing``. Any git failure yields ``unknown`` rather than blocking
    scoring.

    Args:
        paths: Candidate input paths (str/Path/None; Nones are skipped).

    Returns:
        Mapping of repo-relative (or original, when outside the repo)
        path → state.
    """
    states: dict[str, str] = {}
    root = PROJECT_ROOT.resolve()
    for p in paths:
        if not p:
            continue
        path = Path(p)
        try:
            rel = str(path.resolve().relative_to(root))
        except ValueError:
            states[str(p)] = "outside-repo"
            continue
        if not (root / rel).exists():
            states[rel] = "missing"
            continue
        try:
            porcelain = subprocess.run(
                ["git", "status", "--porcelain", "--ignored=no", "--", rel],
                cwd=str(root), capture_output=True, text=True, check=False,
            )
            if porcelain.returncode != 0:
                states[rel] = "unknown"
                continue
            lines = porcelain.stdout.strip().splitlines()
            if lines:
                states[rel] = ("untracked"
                               if all(ln.startswith("??") for ln in lines)
                               else "modified")
                continue
            tracked = subprocess.run(
                ["git", "ls-files", "--", rel],
                cwd=str(root), capture_output=True, text=True, check=False,
            ).stdout.strip()
            if tracked:
                states[rel] = "clean"
            else:
                ignored = subprocess.run(
                    ["git", "check-ignore", "-q", rel],
                    cwd=str(root), capture_output=True, check=False,
                ).returncode == 0
                states[rel] = "ignored" if ignored else "untracked"
        except (FileNotFoundError, OSError):
            states[rel] = "unknown"
    return states


#: Input states that mean "this artefact will not reproduce once the
#: pending change is committed" — the D40 drift signature.
_DIRTY_INPUT_STATES: frozenset[str] = frozenset({"modified", "untracked"})


def enforce_input_hygiene(metadata: dict, require_clean: bool) -> None:
    """Warn on, or refuse, dirty recipe inputs (defect D40 forward fix).

    Always warns when any input is ``modified`` or ``untracked`` (the
    normal pipeline legitimately scores freshly generated, not-yet-
    committed outputs — a warning plus the metadata stamp keeps that
    workflow intact while making the drift disclosed). With
    ``require_clean`` — the ``--require-clean-inputs`` flag, intended for
    replay and campaign contexts — a dirty input aborts scoring instead.

    Args:
        metadata: The ``_build_metadata`` result (reads
            ``input_git_state``).
        require_clean: Refuse instead of warning.

    Raises:
        SystemExit: exit code 4 when ``require_clean`` and any input is
            dirty.
    """
    states = (metadata.get("input_git_state") or {}).get("inputs") or {}
    dirty = {p: s for p, s in states.items() if s in _DIRTY_INPUT_STATES}
    if not dirty:
        return
    detail = ", ".join(f"{p} ({s})" for p, s in sorted(dirty.items()))
    if require_clean:
        logger.error(
            "REFUSING to score against dirty inputs (--require-clean-inputs; "
            "defect D40): %s — commit them first or drop the flag.", detail)
        raise SystemExit(4)
    logger.warning(
        "Scoring against uncommitted inputs (defect D40 drift hazard): %s — "
        "the evaluation will not reproduce once these change; their git "
        "states are recorded in _metadata.input_git_state.", detail)


#: CLI argument keys that hold filesystem paths, normalised to repo-relative in the
#: serialised ``cli_args`` block (the other keys — bootstrap, seed, label, mcc — are
#: passed through verbatim).
_PATH_ARG_KEYS: frozenset[str] = frozenset(
    {"detections", "detections_dir", "batch", "bounds", "ground_truth", "output_dir"}
)


def _repo_relative(value: Any) -> Any:
    """Normalise a path (str/Path), list of paths, or ``None`` to repo-relative POSIX.

    Provenance paths recorded in ``_metadata`` must be portable across machines: an
    absolute ``/home/<user>/...`` path embedded in an eval breaks on every other clone
    (and trips the run-conditions audit verifier's scope/eval-detections checks, which
    compare against repo-relative inputs). Any path resolving under ``PROJECT_ROOT`` is
    rewritten relative to it; already-relative paths are preserved; paths outside the
    repo (e.g. ``/tmp``) and ``None`` are returned unchanged. The check is independent
    of the current working directory for absolute inputs.
    """
    if value is None:
        return None
    if isinstance(value, list):
        return [_repo_relative(v) for v in value]
    try:
        return Path(str(value)).resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except (ValueError, OSError):
        return str(value)


def _serialise_cli_args(args: argparse.Namespace) -> dict[str, Any]:
    """Convert a parsed argparse Namespace into a JSON-safe dict.

    ``argparse`` may store values such as :class:`pathlib.Path` instances
    that the :mod:`json` encoder cannot handle natively. This helper
    walks the namespace once and replaces those values with plain
    strings (or lists of strings), preserving all keys exactly as the
    CLI defined them.

    Args:
        args: The parsed argparse namespace.

    Returns:
        A dict mapping option names to JSON-serialisable values.
    """
    serialised: dict[str, Any] = {}
    for key, value in vars(args).items():
        if key in _PATH_ARG_KEYS:
            # Path-valued args are recorded repo-relative for portability.
            serialised[key] = _repo_relative(
                [str(item) for item in value] if isinstance(value, list) else value
            )
        elif isinstance(value, Path):
            serialised[key] = str(value)
        elif isinstance(value, list):
            serialised[key] = [
                str(item) if isinstance(item, Path) else item
                for item in value
            ]
        else:
            serialised[key] = value
    return serialised


def _build_metadata(args: argparse.Namespace) -> dict[str, Any]:
    """Build the ``_metadata`` block embedded in evaluation outputs.

    The block captures bootstrap parameters (iterations, seed, resampling
    unit), Git provenance (short HEAD hash, clean/dirty status), the
    parsed CLI arguments, and the resolved input file paths. Writing
    this alongside the metrics makes each ``evaluation.json`` file
    self-documenting — reviewers can reproduce confidence intervals
    without reading the script source.

    The schema is versioned via ``metadata_version`` so downstream
    consumers can evolve alongside future changes.

    Args:
        args: The parsed argparse namespace for this run. Expected
            attributes include ``bootstrap``, ``seed``, ``ground_truth``,
            ``bounds``, and at least one of ``detections``,
            ``detections_dir``, or ``batch``.

    Returns:
        A dict with the schema described in the module-level task
        specification. All values are JSON-serialisable.
    """
    # Resolve the input-files block from whichever input mode was used.
    # In batch mode the per-condition detection paths live inside the
    # YAML file, so we record the YAML path itself here.
    if getattr(args, "detections", None):
        detections_value: Any = [str(p) for p in args.detections]
    elif getattr(args, "detections_dir", None):
        detections_value = str(args.detections_dir)
    elif getattr(args, "batch", None):
        detections_value = str(args.batch)
    else:
        detections_value = None

    ground_truth = getattr(args, "ground_truth", None)
    bounds = getattr(args, "bounds", None)

    metadata: dict[str, Any] = {
        # ``metadata_version``: 1.1 (2026-04-29) added BCa + the Mitigation 3
        # sparse-coverage flag; 1.2 (2026-05-31) added the ``spatial`` block recording
        # the evaluation CRS explicitly (after the missing-crs F1=0 bug). Downstream
        # consumers should treat 1.0 outputs as percentile-method and 1.1+ as
        # BCa-requested. 1.3 (2026-08-20, defect D36) split the single
        # ``bootstrap.method`` literal into ``method_requested`` (what the code
        # asked for) and a ``method`` derived from what the run actually
        # measured — the literal was contradicted by 162 per-metric ``method``
        # values inside 58 committed files.
        "metadata_version": "1.3",
        "script_path": _SCRIPT_RELATIVE_PATH,
        "script_git_commit": _git_short_hash(PROJECT_ROOT),
        "script_git_status": _git_status(PROJECT_ROOT),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cli_args": _serialise_cli_args(args),
        "bootstrap": {
            "n_iterations": int(getattr(args, "bootstrap", DEFAULT_BOOTSTRAP)),
            "seed": int(getattr(args, "seed", DEFAULT_SEED)),
            "resampling_unit": "tile_level",
            # D36: what the code ASKS the CI helper for. The helper falls
            # back to the percentile method per metric whenever the BCa
            # acceleration is undefined, so this is an intent, not an
            # observation — the observed ``method`` key is added by
            # :func:`write_outputs`, which can see what was measured.
            # Downstream consumers that need the method of a specific
            # interval should read the per-metric ``*_ci_method`` fields.
            "method_requested": "BCa",
            "library": "scipy.stats.bootstrap",
        },
        "input_files": {
            # Recorded repo-relative for portability (see _repo_relative): an absolute
            # path here is non-portable and trips the run-conditions audit verifier.
            "detections": _repo_relative(detections_value),
            "ground_truth": _repo_relative(str(ground_truth)) if ground_truth else None,
            "bounds": _repo_relative(str(bounds)) if bounds else None,
        },
        # Per-input git state at scoring time (defect D40): discloses in the
        # artefact whether any recipe input was uncommitted when scored, so
        # input-vintage drift is visible without a replay campaign.
        "input_git_state": {
            "head": _git_short_hash(PROJECT_ROOT),
            "inputs": _input_git_states(
                (detections_value if isinstance(detections_value, list)
                 else [detections_value])
                + [ground_truth, bounds]),
        },
        "spatial": {
            # All geometries are reprojected to this CRS for matching/scoring; recorded
            # explicitly so the spatial provenance lives in the eval, not just the code.
            # See docs/methodology/spatial-reference.md.
            "evaluation_crs": DEFAULT_CRS,
            "evaluation_crs_name": "UTM Zone 35N (Bulgaria)",
            "geojson_storage_crs": "EPSG:4326",
            "geojson_storage_note": (
                "GeoJSON is WGS84 (RFC 7946) unless a file declares its own crs member; "
                "the scorer reprojects to evaluation_crs before matching."
            ),
        },
    }
    return metadata


# ── Data loading ──────────────────────────────────────────────────────

def load_geojson(path: Path, target_crs: str = DEFAULT_CRS) -> gpd.GeoDataFrame:
    """Load a GeoJSON file and ensure it is in the target CRS.

    Args:
        path: Path to GeoJSON file.
        target_crs: Target Coordinate Reference System (default EPSG:32635).

    Returns:
        GeoDataFrame in the target CRS.
    """
    gdf = gpd.read_file(path)
    if gdf.empty:
        logger.warning("Empty GeoJSON: %s", path)
        return gdf
    if gdf.crs is None:
        gdf.set_crs(target_crs, inplace=True)
    elif str(gdf.crs) != target_crs:
        gdf = gdf.to_crs(target_crs)
    return gdf


def find_detection_files(
    detections_dir: Path,
    glob_pattern: str | None = None,
) -> list[Path]:
    """Find detection GeoJSON files in a directory.

    With no explicit pattern, resolution is delegated to
    :func:`scripts.lib_detection_paths.resolve_pool_passes`, which expands BOTH
    per-pass filename conventions. The previous default,
    a batch-only pattern, matched just the ``..._run<NN>.geojson`` shape and so
    silently under-read any pool whose passes straddled the project's switch
    from the Batch API to real-time flex (defect D6).

    An explicit ``glob_pattern`` still takes precedence, because a few callers
    legitimately target non-pass artefacts — ``accepted_run*.geojson`` under
    ``results/era1-pv-stage-d/``, for instance.

    Args:
        detections_dir: Base directory to search.
        glob_pattern: Optional glob relative to ``detections_dir``. ``None``
            (the default) uses the canonical resolver.

    Returns:
        Matching file paths, in run order (run_2 before run_10).
    """
    if glob_pattern is None:
        # allow_multiple stays False: a run directory holding two candidate
        # files means a superseded artefact is present, and averaging both
        # into a 'pass' count is the silent-wrongness this resolver exists
        # to prevent. Let it raise and make the operator disambiguate.
        matches = resolve_pool_passes(detections_dir)
    else:
        matches = sorted(detections_dir.glob(glob_pattern))
    if not matches:
        logger.warning(
            "No pass files found in %s (pattern: %s)",
            detections_dir, glob_pattern or "canonical resolver",
        )
    return matches


# ── Evaluation ────────────────────────────────────────────────────────

def assess_ci_reliability(
    ci: dict, f1: float, precision: float, recall: float, coverage_status: str,
) -> tuple[bool, bool]:
    """Decide whether a buffer's confidence intervals are untrustworthy.

    Two independent grounds, both measured rather than inferred:

    * **The interval excludes its own point estimate.** This is the pathology
      "Mitigation 3" was introduced for in 2026999ad, when the percentile method
      could produce a 2.5-97.5 range that did not contain the all-data estimate.
      It is now tested for directly instead of being predicted from a
      zero-count-tile heuristic.
    * **Partial coverage (E72).** A detection set that does not cover its
      evaluation bounds manufactures false negatives on every unprocessed
      mound-bearing tile, so the point estimate is wrong too, not just the
      interval.

    ``sparse_cross_grid`` deliberately does NOT set the flag. It did until
    2026-08-19, when a re-check across all 1,041 flagged buffer-rows in the
    committed manifest found 1,041 containing their point estimate and none
    excluding it: the BCa migration in the same commit that added the heuristic
    had already fixed what the heuristic was watching for, and it had reached 91
    of 337 conditions at the 20 m headline. Sparseness is still reported, as
    ``sparse_coverage`` and ``coverage.zero_fraction``, because a mostly-empty
    scope genuinely carries less information than its tile count suggests — but
    that is a fact for the reader, not a reliability verdict.

    Args:
        ci: The per-metric CI block, keyed ``f1`` / ``precision`` / ``recall``.
        f1: All-data F1 point estimate.
        precision: All-data precision point estimate.
        recall: All-data recall point estimate.
        coverage_status: This buffer's coverage status.

    Returns:
        ``(ci_unreliable, ci_excludes_point)``.
    """
    excludes = any(
        (block := ci.get(metric, {})).get("ci_lower") is not None
        and block.get("ci_upper") is not None
        and not (block["ci_lower"] <= point <= block["ci_upper"])
        for metric, point in (
            ("f1", f1), ("precision", precision), ("recall", recall),
        )
    )
    return (coverage_status == COVERAGE_STATUS_PARTIAL or excludes), excludes


def evaluate_single_run(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
    n_bootstrap: int = DEFAULT_BOOTSTRAP,
    seed: int = DEFAULT_SEED,
    label: str = "",
    compute_mcc: bool = False,
    processed_tiles: set[str] | None = None,
) -> dict:
    """Evaluate a single detection run at multiple buffer distances.

    Args:
        gdf_det: Detection GeoDataFrame.
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Evaluation tile boundaries GeoDataFrame.
        buffers: Buffer distances in metres.
        n_bootstrap: Bootstrap iterations for CIs.
        seed: Random seed for reproducibility.
        label: Human-readable label for this run.
        compute_mcc: If True, also compute tile-level MCC, sensitivity,
            and specificity with bootstrap CIs.
        processed_tiles: Optional set of tile filenames the detection set
            actually processed (E72). When supplied, unprocessed tiles are
            counted directly against the evaluation bounds and a shortfall
            flags ``coverage_status = "partial_coverage"``. ``None``
            preserves the pre-E72 zero-fraction-only behaviour.

    Returns:
        Dict with metadata and per-buffer results including F1, P, R
        with bootstrap CIs. When compute_mcc is True, also includes
        a tile_classification key.
    """
    n_det = len(gdf_det)
    buffer_results = []

    for buffer_m in buffers:
        if n_det == 0:
            buffer_results.append({
                "buffer_metres": buffer_m,
                "f1": 0.0, "precision": 0.0, "recall": 0.0,
                "ci": {},
            })
            continue

        # Point estimate
        precision, recall, f1 = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_m,
        )

        # Bootstrap CIs
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=n_bootstrap,
            random_seed=seed,
            buffer_metres=buffer_m,
            processed_tiles=processed_tiles,
        )

        # Mitigation 3 (sparse-coverage transparency): surface the coverage
        # block on each buffer entry so MD/CSV writers can suppress
        # numerically-misleading CIs while keeping the JSON copy intact for
        # downstream tooling. ``coverage_status`` is the canonical
        # human-readable flag; ``ci`` retains all numeric bounds.
        #
        # E72: ``partial_coverage`` also sets ``ci_unreliable``. A detection
        # set that does not cover its evaluation bounds produces artificial
        # false negatives on every unprocessed mound-bearing tile, so both
        # the interval AND the point estimate are untrustworthy — flagging
        # is strictly more conservative than the pre-E72 behaviour, which
        # could not detect this case at all.
        coverage = ci.get("coverage", {})
        coverage_status = coverage.get(
            "coverage_status", COVERAGE_STATUS_NORMAL,
        )
        # ``ci_unreliable`` is MEASURED, not inferred from sparseness alone
        # (revised 2026-08-19).
        #
        # Until this revision the flag fired on ``sparse_cross_grid`` as well,
        # a >50 % zero-count-tile heuristic introduced in 2026999ad to catch a
        # percentile-method pathology: bootstrap distributions whose 2.5-97.5
        # range EXCLUDED the all-data point estimate. The same commit replaced
        # the percentile method with BCa, which fixed that pathology, and the
        # heuristic was never re-evaluated against the corrected intervals.
        # Re-checked across all 1,041 flagged buffer-rows in the committed
        # manifest: 1,041 contain their point estimate and 0 exclude it. The
        # heuristic reached 91 of 337 conditions at the 20 m headline buffer,
        # including the paper's gold-standard cell, so it was warning about a
        # defect that no longer occurs.
        #
        # The pathology is now tested for directly, and E72's partial coverage
        # still flags unconditionally: an uncovered evaluation bound produces
        # artificial false negatives on every unprocessed mound-bearing tile,
        # so there BOTH the interval and the point estimate are untrustworthy.
        # Sparseness remains real and is reported descriptively rather than as
        # a reliability verdict — see docs/methodology/inference-instrument-policy.md.
        ci_unreliable, ci_excludes_point = assess_ci_reliability(
            ci, f1, precision, recall, coverage_status,
        )
        buffer_results.append({
            "buffer_metres": buffer_m,
            "f1": round(f1, 4),
            "f1_point": round(f1, 4),  # Same as ``f1`` — alias for clarity
            "f1_ci_lower": round(ci["f1"]["ci_lower"], 4),
            "f1_ci_upper": round(ci["f1"]["ci_upper"], 4),
            # D36: the measured method, or ``None`` when the CI helper did
            # not report one. A ``"BCa"`` default here would assert a
            # method nothing measured (the D17 principle: an absent
            # parameter is not evidence of the standard one).
            "f1_ci_method": ci["f1"].get("method"),
            "precision": round(precision, 4),
            "p_point": round(precision, 4),
            "p_ci_lower": round(ci["precision"]["ci_lower"], 4),
            "p_ci_upper": round(ci["precision"]["ci_upper"], 4),
            "p_ci_method": ci["precision"].get("method"),
            "recall": round(recall, 4),
            "r_point": round(recall, 4),
            "r_ci_lower": round(ci["recall"]["ci_lower"], 4),
            "r_ci_upper": round(ci["recall"]["ci_upper"], 4),
            "r_ci_method": ci["recall"].get("method"),
            "coverage": coverage,
            "coverage_status": coverage_status,
            "ci_unreliable": ci_unreliable,
            "ci_excludes_point": ci_excludes_point,
            "sparse_coverage": coverage_status == COVERAGE_STATUS_SPARSE,
            # Which rule produced ci_unreliable, so an artefact is readable
            # without knowing its vintage. Evaluations written before
            # 2026-08-19 lack this key and used the superseded rule, where
            # sparse coverage alone set the flag.
            "ci_flag_basis": "measured-exclusion-or-partial-coverage",
        })

        logger.info(
            "  %dm: F1=%.3f [%.3f, %.3f], P=%.3f [%.3f, %.3f], "
            "R=%.3f [%.3f, %.3f]%s",
            buffer_m, f1, ci["f1"]["ci_lower"], ci["f1"]["ci_upper"],
            precision, ci["precision"]["ci_lower"],
            ci["precision"]["ci_upper"],
            recall, ci["recall"]["ci_lower"], ci["recall"]["ci_upper"],
            (
                f" [{coverage.get('coverage_detail')}]"
                if coverage.get("coverage_detail")
                else (
                    f" [sparse coverage: "
                    f"{coverage.get('zero_fraction', 0):.1%} zero-tiles]"
                    if coverage_status == COVERAGE_STATUS_SPARSE else ""
                )
            ),
        )

    # Cell-level rollup (Mitigation 3, per-cell flag): if ANY buffer's
    # bootstrap distribution flagged sparse coverage, flag the whole cell.
    # This gives consumers a one-shot boolean per cell without scanning
    # individual buffer entries; useful for paper tables and analysis
    # notebooks. The 20 m and 30 m buffers can in principle differ; the
    # any-buffer rule treats the worst case as the cell's status.
    cell_ci_unreliable = any(
        buf.get("ci_unreliable", False) for buf in buffer_results
    )
    cell_coverage_status = _worst_coverage_status([
        buf.get("coverage_status", COVERAGE_STATUS_NORMAL)
        for buf in buffer_results
    ])

    result = {
        "label": label,
        "n_detections": n_det,
        "buffers": buffer_results,
        "ci_unreliable_any_buffer": cell_ci_unreliable,
        "coverage_status": cell_coverage_status,
    }

    # Tile-level MCC (optional)
    if compute_mcc and n_det > 0:
        tile_class = calculate_tile_classification(
            gdf_det, gdf_ref, gdf_bounds,
        )
        tile_ci = bootstrap_tile_classification_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=n_bootstrap, random_seed=seed,
        )
        result["tile_classification"] = build_tile_classification_block(
            tile_class, tile_ci,
        )
        # E81: every field here can legitimately be ``None`` when the
        # tile confusion matrix is degenerate, so the log line is built
        # from the None-safe formatter rather than ``%.3f``.
        logger.info(
            "  MCC=%s [%s, %s], Sens=%s, Spec=%s",
            _fmt_metric(tile_class["mcc"]),
            _fmt_metric(tile_ci["mcc"]["ci_lower"]),
            _fmt_metric(tile_ci["mcc"]["ci_upper"]),
            _fmt_metric(tile_class["sensitivity"]),
            _fmt_metric(tile_class["specificity"]),
        )

    return result


def evaluate_multi_run_mean(
    run_results: list[dict],
    label: str = "",
) -> dict:
    """Compute mean metrics across multiple independent runs.

    For each buffer distance, averages the point estimates and CIs
    across runs. This gives the expected single-run performance.

    Schema 1.1 parity (added 2026-04-29, Obs 311 follow-up): the
    summary's per-buffer dicts now also carry the deterministic
    ``*_point`` aliases, ``coverage_status``, ``ci_unreliable``,
    ``ci_zero_fraction``, and ``ci_n_tiles`` fields that
    non-aggregated (single-pass) cells already expose. These are
    additive — existing callers that read ``f1`` / ``f1_ci_lower`` /
    etc. continue to work unchanged. The new fields use a
    conservative "worst-case across runs" rollup so that downstream
    consumers can apply a single per-cell or per-buffer flag-check
    without scanning ``per_run[*]``.

    Rollup rules:

    - ``f1_point`` / ``p_point`` / ``r_point``: arithmetic mean of
      per-run ``*_point`` values (equals ``f1`` / ``precision`` /
      ``recall`` since those are themselves averaged from per-run
      points; the alias exists for schema parity).
    - ``coverage_status``: the worst status across per-run entries
      (``partial_coverage`` > ``sparse_cross_grid`` > ``normal``).
    - ``ci_unreliable`` / ``ci_excludes_point`` / ``sparse_coverage`` /
      ``ci_flag_basis``: the MEASURED reliability block, evaluated on the
      aggregated row itself (partial coverage or a CI excluding its own
      averaged point) — the 2026-08-19 measured-flag rule, which the
      2026-08-20 corpus migration applied to every committed aggregate
      (defect D42). Superseded the earlier any-run-flagged rollup on
      2026-08-23; the two never disagreed on the migrated corpus.
    - ``ci_zero_fraction``: maximum across per-run entries
      (worst-case zero-tile fraction).
    - ``ci_n_tiles``: minimum across per-run entries (worst-case
      effective sample size).

    The cell-level summary additionally carries
    ``ci_unreliable_any_buffer`` and ``coverage_status`` (any-buffer
    rollup) for one-shot per-cell flag checks. For tile-level MCC,
    the existing ``tile_classification`` block now also includes
    ``point`` keys for ``mcc`` / ``sensitivity`` / ``specificity``,
    averaged across per-run point estimates.

    Undefined-metric rollup (errata E81, 2026-08-18): a tile-level
    metric is *undefined* on a pass whose 2 x 2 tile confusion matrix is
    degenerate, and such a pass now arrives here as ``None`` rather than
    as a coerced ``0.0``. The mean is therefore taken over the
    **defined** passes only; each metric block additionally carries
    ``n_runs`` (passes with a ``tile_classification`` block) and
    ``n_runs_defined`` (passes that contributed a computable value), so
    a mean of two defined passes can never be read as a mean of three.
    When *no* pass is defined the averaged fields are ``None``. The
    block also records ``confusion_source`` — the confusion matrix
    reported for an aggregated cell is run 1's, not a sum or a mean.

    Args:
        run_results: List of per-run result dicts from evaluate_single_run().
        label: Human-readable label for the averaged condition.

    Returns:
        Dict with averaged metrics per buffer distance plus the
        schema-parity flag fields described above.
    """
    n_runs = len(run_results)
    if n_runs == 0:
        return {"label": label, "n_runs": 0, "buffers": []}

    # Group by buffer distance
    from collections import defaultdict
    by_buffer: dict[int, list[dict]] = defaultdict(list)
    for result in run_results:
        for buf_entry in result["buffers"]:
            by_buffer[buf_entry["buffer_metres"]].append(buf_entry)

    avg_buffers = []
    # Numeric metric keys averaged across runs. ``*_point`` aliases
    # are appended here so the summary's per-buffer dict mirrors the
    # non-aggregated schema introduced for the BCa migration. The
    # mean of per-run point estimates equals the canonical ``f1`` /
    # ``precision`` / ``recall`` values (which are themselves means of
    # per-run F1/P/R), but exposing the named alias avoids forcing
    # downstream code to special-case aggregated vs single-run cells.
    metric_keys = [
        "f1", "f1_point", "f1_ci_lower", "f1_ci_upper",
        "precision", "p_point", "p_ci_lower", "p_ci_upper",
        "recall", "r_point", "r_ci_lower", "r_ci_upper",
    ]

    for buffer_m in sorted(by_buffer.keys()):
        entries = by_buffer[buffer_m]
        avg: dict[str, Any] = {"buffer_metres": buffer_m}
        for key in metric_keys:
            values = [e[key] for e in entries if key in e]
            avg[key] = round(float(np.mean(values)), 4) if values else 0.0

        coverage_statuses = [
            e.get("coverage_status", COVERAGE_STATUS_NORMAL)
            for e in entries
        ]
        # Worst case wins (E72 added a third, more severe status —
        # ``partial_coverage`` — so the rollup ranks rather than tests a
        # single literal).
        avg["coverage_status"] = _worst_coverage_status(coverage_statuses)
        # Reliability block, MEASURED on the aggregated row itself (defect
        # D42): the 2026-08-19 measured-flag policy defines
        # ``ci_unreliable`` as partial-coverage-or-exclusion evaluated on
        # the row as stored, and the 2026-08-20 corpus migration applied
        # exactly that rule to every committed aggregate. The earlier
        # any-run-flagged rollup is superseded — in the whole migrated
        # corpus the two rules never disagreed (zero flag flips across
        # 1,424 re-derived rows), but only this formulation keeps
        # ``migrate_ci_flag_basis --dry-run`` a true zero-invariant over
        # fresh multi-run output.
        excludes = measured_exclusion(avg)
        avg["ci_unreliable"] = (
            avg["coverage_status"] == COVERAGE_STATUS_PARTIAL or excludes
        )
        avg["ci_excludes_point"] = excludes
        avg["sparse_coverage"] = (
            avg["coverage_status"] == COVERAGE_STATUS_SPARSE
        )
        avg["ci_flag_basis"] = CI_FLAG_BASIS_FULL

        # Worst-case coverage diagnostics across runs: max
        # zero-fraction (highest sparsity), min n_tiles (smallest
        # effective sample). Both are read from the per-run
        # ``coverage`` sub-dict produced by ``bootstrap_ci`` — we
        # default to the buffer-level ``ci_zero_fraction`` /
        # ``ci_n_tiles`` keys that ``write_outputs`` already
        # populates for non-aggregated cells if ``coverage`` is
        # absent.
        zero_fractions: list[float] = []
        n_tiles_values: list[int] = []
        for e in entries:
            cov = e.get("coverage", {}) or {}
            zf = cov.get(
                "zero_fraction",
                e.get("ci_zero_fraction", 0.0),
            )
            nt = cov.get("n_tiles", e.get("ci_n_tiles", 0))
            if zf is not None:
                zero_fractions.append(float(zf))
            if nt is not None:
                n_tiles_values.append(int(nt))
        avg["ci_zero_fraction"] = (
            round(max(zero_fractions), 6) if zero_fractions else 0.0
        )
        avg["ci_n_tiles"] = (
            min(n_tiles_values) if n_tiles_values else 0
        )

        avg_buffers.append(avg)

        logger.info(
            "  Mean across %d runs @ %dm: F1=%.3f [%.3f, %.3f], "
            "P=%.3f, R=%.3f%s",
            n_runs, buffer_m,
            avg["f1"], avg["f1_ci_lower"], avg["f1_ci_upper"],
            avg["precision"], avg["recall"],
            (
                f" [sparse coverage: max zero-fraction "
                f"{avg['ci_zero_fraction']:.1%}]"
                if avg["ci_unreliable"] else ""
            ),
        )

    # Cell-level rollup: a single boolean answers "does this cell
    # carry any unreliable buffer?" — same any-buffer rule used for
    # non-aggregated cells in ``evaluate_single_run``.
    cell_ci_unreliable = any(
        bool(buf.get("ci_unreliable", False)) for buf in avg_buffers
    )
    cell_coverage_status = _worst_coverage_status([
        buf.get("coverage_status", COVERAGE_STATUS_NORMAL)
        for buf in avg_buffers
    ])

    result: dict[str, Any] = {
        "label": label,
        "n_runs": n_runs,
        "buffers": avg_buffers,
        "ci_unreliable_any_buffer": cell_ci_unreliable,
        "coverage_status": cell_coverage_status,
    }

    # Average tile-level MCC across runs (if computed)
    mcc_results = [
        r["tile_classification"] for r in run_results
        if "tile_classification" in r
    ]
    if mcc_results:
        avg_mcc = aggregate_tile_classification(mcc_results)
        result["tile_classification"] = avg_mcc

        mcc_block = avg_mcc.get("mcc", {})
        logger.info(
            # D30: the observed statistic, averaged over the defined
            # passes — not the mean of the bootstrap distributions.
            "  Mean MCC across %d/%d defined runs: %s [%s, %s]",
            mcc_block.get("n_runs_defined", len(mcc_results)),
            len(mcc_results),
            _fmt_metric(_observed_metric(mcc_block)),
            _fmt_metric(mcc_block.get("ci_lower")),
            _fmt_metric(mcc_block.get("ci_upper")),
        )

    return result


# ── Output ────────────────────────────────────────────────────────────

def collect_ci_methods(
    results: dict,
    run_results: list[dict] | None = None,
) -> set[str]:
    """Census the CI methods a run actually measured.

    Reads the per-metric ``method`` strings the CI helpers recorded:
    ``f1_ci_method`` / ``p_ci_method`` / ``r_ci_method`` on every buffer
    row, and ``method`` on every ``tile_classification`` metric block.
    Values are whatever :func:`lib_advanced_metrics._bca_ci_from_indices`
    reported — ``"BCa"``, ``"percentile_fallback"``, or ``"undefined"``.

    Args:
        results: The summary results dict.
        run_results: Optional per-run results dicts (multi-run mode).

    Returns:
        The set of distinct measured method strings (empty when the run
        recorded none).
    """
    methods: set[str] = set()
    for block in [results, *(run_results or [])]:
        if not isinstance(block, dict):
            continue
        for buf in block.get("buffers") or []:
            if not isinstance(buf, dict):
                continue
            for key in ("f1_ci_method", "p_ci_method", "r_ci_method"):
                value = buf.get(key)
                if value is not None:
                    methods.add(str(value))
        tile = block.get("tile_classification") or {}
        if isinstance(tile, dict):
            for metric in ("mcc", "sensitivity", "specificity"):
                metric_block = tile.get(metric)
                if isinstance(metric_block, dict):
                    value = metric_block.get("method")
                    if value is not None:
                        methods.add(str(value))
    return methods


def with_measured_bootstrap_method(
    metadata: dict[str, Any],
    results: dict,
    run_results: list[dict] | None = None,
) -> dict[str, Any]:
    """Return a copy of ``metadata`` whose bootstrap method is measured.

    Defect D36 (Session 137 audit, finding F12): ``_metadata.bootstrap``
    carried the literal ``"method": "BCa"``, written before any interval
    was computed. Across 58 committed files that literal is contradicted
    by 162 per-metric ``method`` values (``percentile_fallback`` ×127,
    ``undefined`` ×35) sitting in the same document. The intent now lives
    in ``method_requested`` (written by :func:`_build_metadata`) and this
    function adds the observation.

    ``method`` becomes the single measured method when the run used only
    one, ``"mixed"`` when several were used, and is omitted entirely when
    the run measured none — an absent key is the honest record of "not
    observed", which is what D17 taught. ``methods_measured`` lists the
    census so a reader never has to trust the summary word.

    The input dict is never mutated: in batch mode one metadata block is
    shared by every condition, and each condition measures its own
    methods.

    Args:
        metadata: The provenance block from :func:`_build_metadata`.
        results: The summary results dict for THIS condition.
        run_results: Optional per-run results dicts.

    Returns:
        A copy of ``metadata`` with its ``bootstrap`` sub-dict replaced.
    """
    methods = collect_ci_methods(results, run_results)
    bootstrap = dict(metadata.get("bootstrap") or {})
    bootstrap.pop("method", None)
    if methods:
        bootstrap["method"] = (
            next(iter(methods)) if len(methods) == 1 else "mixed"
        )
        bootstrap["methods_measured"] = sorted(methods)
    return {**metadata, "bootstrap": bootstrap}


def write_outputs(
    results: dict,
    run_results: list[dict] | None,
    output_dir: Path,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Write evaluation results as JSON, CSV, and Markdown.

    Args:
        results: Averaged or single-run results dict.
        run_results: Optional list of per-run results (for multi-run).
        output_dir: Output directory.
        metadata: Optional ``_metadata`` block describing how the
            evaluation was generated (bootstrap config, git provenance,
            CLI args, input files). When provided, it is written as a
            top-level ``_metadata`` key in ``evaluation.json`` so the
            JSON output is self-documenting. Its ``bootstrap.method`` is
            replaced by what this condition actually measured (D36); the
            caller's dict is left untouched.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # D36: reconcile the requested bootstrap method with the measured one
    # before the block is published. Done here rather than in
    # ``_build_metadata`` because the methods are only known once the
    # intervals have been computed.
    if metadata is not None:
        metadata = with_measured_bootstrap_method(
            metadata, results, run_results,
        )

    # JSON — key order preserves backward compatibility: existing
    # consumers that look up ``version`` / ``summary`` continue to work,
    # and the new ``_metadata`` block is additive.
    output: dict[str, Any] = {
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": results,
    }
    if metadata is not None:
        output["_metadata"] = metadata
    if run_results:
        output["per_run"] = run_results

    json_path = output_dir / "evaluation.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logger.info("JSON written: %s", json_path)

    # CSV
    # MCC is buffer-invariant (computed at the tile level), so when the
    # ``tile_classification`` block is present we repeat the same MCC,
    # sensitivity, and specificity values across every buffer row for
    # tabular convenience. ``has_mcc`` gates both the wider CSV columns
    # and the wider Markdown header below so legacy outputs without MCC
    # remain byte-identical.
    tc = results.get("tile_classification") or {}
    has_mcc = bool(tc)

    # Mitigation 3 (sparse coverage): emit machine-readable diagnostics
    # columns alongside the numeric CI bounds. Downstream consumers that
    # only read the numeric columns continue to work; consumers that
    # respect the flag can hide unreliable bounds at render time. The
    # boolean is the contract: "do you trust these CIs?".
    has_coverage = any(
        "coverage_status" in buf for buf in results["buffers"]
    )

    csv_path = output_dir / "evaluation.csv"
    fieldnames = [
        "label", "buffer_metres",
        "f1", "f1_ci_lower", "f1_ci_upper",
        "precision", "p_ci_lower", "p_ci_upper",
        "recall", "r_ci_lower", "r_ci_upper",
    ]
    if has_mcc:
        fieldnames.extend([
            "mcc", "mcc_ci_lower", "mcc_ci_upper",
            "sensitivity", "specificity",
            # D30: the resample means, published under their own names so
            # the bootstrap-distribution centre stays available to any
            # consumer that wants it. Appended after the historical five
            # so existing column positions do not move.
            "mcc_boot_mean", "sensitivity_boot_mean",
            "specificity_boot_mean",
        ])
    if has_coverage:
        fieldnames.extend([
            "coverage_status", "ci_unreliable",
            "ci_zero_fraction", "ci_n_tiles",
            # E72: how the status was decided, and the direct count that
            # decided it. A consumer reading only ``ci_zero_fraction``
            # cannot distinguish "well covered" from "never checked".
            "coverage_source", "n_unprocessed_tiles",
        ])
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for buf in results["buffers"]:
            row = {"label": results["label"], **buf}
            if has_mcc:
                mcc = tc.get("mcc", {})
                sens = tc.get("sensitivity", {})
                spec = tc.get("specificity", {})
                # MCC is buffer-invariant; repeated per row for tabular
                # convenience. E81: an undefined value is written as an
                # empty cell, never as ``0``. ``csv`` renders ``None`` as
                # the empty string, but the intent is made explicit here
                # rather than left to that default — a ``0`` in this
                # column is a claim about the model, and only a measured
                # zero may make it.
                # D30: the bare names carry the OBSERVED statistic
                # (``point``); the resample means ride alongside in the
                # ``*_boot_mean`` columns.
                row.update({
                    "mcc": _csv_metric(_observed_metric(mcc)),
                    "mcc_ci_lower": _csv_metric(mcc.get("ci_lower")),
                    "mcc_ci_upper": _csv_metric(mcc.get("ci_upper")),
                    "sensitivity": _csv_metric(_observed_metric(sens)),
                    "specificity": _csv_metric(_observed_metric(spec)),
                    "mcc_boot_mean": _csv_metric(mcc.get("mean")),
                    "sensitivity_boot_mean": _csv_metric(sens.get("mean")),
                    "specificity_boot_mean": _csv_metric(spec.get("mean")),
                })
            if has_coverage:
                cov = buf.get("coverage", {}) or {}
                row.update({
                    "coverage_status": buf.get(
                        "coverage_status", COVERAGE_STATUS_NORMAL,
                    ),
                    "ci_unreliable": bool(buf.get("ci_unreliable", False)),
                    "ci_zero_fraction": cov.get("zero_fraction", 0.0),
                    "ci_n_tiles": cov.get("n_tiles", 0),
                    "coverage_source": cov.get("coverage_source", ""),
                    "n_unprocessed_tiles": (
                        "" if cov.get("n_unprocessed_tiles") is None
                        else cov["n_unprocessed_tiles"]
                    ),
                })
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    logger.info("CSV written: %s", csv_path)

    # Markdown
    md_path = output_dir / "evaluation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Evaluation: {results['label']}\n\n")
        f.write(f"**Generated**: {datetime.now(timezone.utc).isoformat()}  \n")
        if "n_runs" in results:
            f.write(f"**Runs**: {results['n_runs']}  \n")
        f.write(
            f"**Detections**: {results.get('n_detections', '—')}  \n\n",
        )

        # When MCC is present we emit four additional columns per row.
        # The MCC mean and CI come from the buffer-invariant
        # ``tile_classification`` block; sensitivity and specificity are
        # likewise repeated across rows.
        if has_mcc:
            mcc = tc.get("mcc", {})
            sens = tc.get("sensitivity", {})
            spec = tc.get("specificity", {})
            f.write(
                "| Buffer | F1 | F1 CI | P | P CI | R | R CI "
                "| MCC | MCC CI | Sens | Spec |\n",
            )
            f.write("|" + "---|" * 11 + "\n")
        else:
            f.write("| Buffer | F1 | F1 CI | P | P CI | R | R CI |\n")
            f.write("|---|---|---|---|---|---|---|\n")
        # Mitigation 3 (sparse coverage): when a buffer's
        # ``ci_unreliable`` flag is set, replace the numeric CI cells with
        # ``N/A *`` and emit a footnote at the bottom of the table. The
        # point estimate is preserved in the F1/P/R columns; the
        # numerically-misleading bounds are hidden from human-readable
        # output. The JSON copy retains the bounds for downstream tooling.
        any_sparse = False
        for buf in results["buffers"]:
            ci_unreliable = bool(buf.get("ci_unreliable", False))
            if ci_unreliable:
                any_sparse = True

            def _ci(lo: float, hi: float, suppress: bool) -> str:
                """Format a CI cell as ``[lo, hi]`` or ``N/A *`` when sparse."""
                if suppress:
                    return "N/A *"
                return f"[{lo:.3f}, {hi:.3f}]"

            row_body = (
                f"| {buf['buffer_metres']}m "
                f"| {buf['f1']:.3f} "
                f"| {_ci(buf.get('f1_ci_lower', 0), buf.get('f1_ci_upper', 0), ci_unreliable)} "
                f"| {buf['precision']:.3f} "
                f"| {_ci(buf.get('p_ci_lower', 0), buf.get('p_ci_upper', 0), ci_unreliable)} "
                f"| {buf['recall']:.3f} "
                f"| {_ci(buf.get('r_ci_lower', 0), buf.get('r_ci_upper', 0), ci_unreliable)} "
            )
            if has_mcc:
                # MCC CI is buffer-invariant; suppression for tabular
                # MCC follows the same rule because the same tile pool
                # underlies all CIs. E81: an undefined MCC renders as
                # the word "undefined", never as 0.000 — see the
                # footnote emitted below the table.
                mcc_lo = mcc.get("ci_lower")
                mcc_hi = mcc.get("ci_upper")
                if mcc_lo is None or mcc_hi is None:
                    mcc_ci_cell = UNDEFINED_DISPLAY
                else:
                    mcc_ci_cell = _ci(mcc_lo, mcc_hi, ci_unreliable)
                # D30: the MCC / Sens / Spec columns carry the OBSERVED
                # statistic. The resample mean is a bootstrap diagnostic
                # and belongs in the CSV's ``*_boot_mean`` columns and
                # the JSON, not under a column header that names the
                # statistic itself.
                mcc_cells = (
                    f"| {_fmt_metric(_observed_metric(mcc))} "
                    f"| {mcc_ci_cell} "
                    f"| {_fmt_metric(_observed_metric(sens))} "
                    f"| {_fmt_metric(_observed_metric(spec))} "
                )
                f.write(row_body + mcc_cells + "|\n")
            else:
                f.write(row_body + "|\n")

        # Footnote: only emit when at least one row is suppressed. Partial
        # coverage (E72) and sparse coverage are different diagnoses and get
        # different footnotes — writing the sparse text over a partial cell
        # would misdescribe the defect (and, worse, imply the point estimate
        # is sound when it is not).
        partial_buffers = [
            buf for buf in results["buffers"]
            if buf.get("coverage_status") == COVERAGE_STATUS_PARTIAL
        ]
        # ``coverage_detail`` is present on single-run buffer entries but
        # not on the averaged entries produced by
        # ``evaluate_multi_run_mean``, which roll up the status only — so
        # the status is the trigger and the detail is best-effort.
        partial_details = sorted({
            detail for buf in partial_buffers
            if (detail := (buf.get("coverage") or {}).get("coverage_detail"))
        }) or ["tile-level detail not retained in this aggregation"]
        if partial_buffers:
            f.write(
                "\n\\* **Partial coverage** — the detection set does not "
                "cover the evaluation bounds it is scored against "
                f"({'; '.join(partial_details)}). Ground-truth "
                "mounds on unprocessed tiles are counted as artificial "
                "false negatives, so the POINT ESTIMATE is deflated as well "
                "as the interval; neither is comparable with a full-coverage "
                "cell. Re-score both arms against bounds the data actually "
                "covers. See erratum E72 in "
                "`docs/methodology/preregistration/protocol-errata.md` and "
                "`results/evaluation-scopes.md` § 12.\n",
            )
        elif any_sparse:
            zero_pcts = [
                f"{buf.get('coverage', {}).get('zero_fraction', 0):.1%}"
                for buf in results["buffers"]
                if buf.get("ci_unreliable", False)
            ]
            f.write(
                "\n\\* Bootstrap CI suppressed for sparse-coverage buffers "
                f"({', '.join(zero_pcts)} of evaluation tiles have zero "
                "TP/FP/FN counts; threshold > 50 %). "
                "Numeric bounds remain in `evaluation.json` and "
                "`evaluation.csv` for downstream tooling. The point "
                "estimate (F1, P, R, MCC) is unaffected. See "
                "`archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` "
                "for the underlying methodology decision.\n",
            )

        # Undefined-metric footnote (errata E81). Emitted independently of
        # the coverage footnotes above: an undefined MCC is a different
        # diagnosis from a sparse or partial CI, and a reader who sees the
        # word "undefined" in a metric column is owed the reason.
        if has_mcc:
            mcc_block = tc.get("mcc", {})
            undefined_fields = [
                name for name in ("point", "mean", "ci_lower", "ci_upper")
                if name in mcc_block and mcc_block[name] is None
            ]
            if undefined_fields:
                n_defined = mcc_block.get("n_runs_defined")
                n_runs_total = mcc_block.get("n_runs")
                runs_clause = (
                    f" (defined on {n_defined} of {n_runs_total} passes)"
                    if n_defined is not None and n_runs_total is not None
                    else ""
                )
                conf = tc.get("confusion", {})
                f.write(
                    "\n**Undefined MCC** — the tile-level Matthews "
                    "Correlation Coefficient is not computable here"
                    f"{runs_clause}: the 2 x 2 tile confusion matrix is "
                    "degenerate, so the denominator "
                    "sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes "
                    f"(TP={conf.get('tp', '?')}, TN={conf.get('tn', '?')}, "
                    f"FP={conf.get('fp', '?')}, FN={conf.get('fn', '?')}). "
                    "It is reported as `undefined` rather than 0.000, "
                    "because 0 on this scale means \"random\" (§ 4.2 of "
                    "the preregistration) and would assert a measurement "
                    "that was not made. See erratum E81 in "
                    "`docs/methodology/preregistration/protocol-errata.md`.\n",
                )
        f.write("\n")
    logger.info("Markdown written: %s", md_path)


# ── Batch mode ────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert a label to a filesystem-safe directory name.

    Args:
        text: Human-readable label.

    Returns:
        Lowercase string with spaces/special chars replaced by hyphens.
    """
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def load_batch_yaml(
    path: Path,
) -> tuple[dict, list[dict]]:
    """Load a batch evaluation YAML spec.

    Reads the YAML file, extracts defaults and per-condition specs,
    and merges overrides. Each condition inherits from defaults unless
    it provides its own value.

    Args:
        path: Path to the batch YAML file.

    Returns:
        Tuple of (defaults_dict, conditions_list) where each condition
        dict has all parameters resolved.
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    defaults = data.get("defaults", {})
    metadata = data.get("metadata", {})
    conditions = data.get("conditions", [])

    if not conditions:
        raise ValueError(f"No conditions found in {path}")

    # Resolve paths relative to PROJECT_ROOT
    for key in ["bounds", "ground_truth"]:
        if key in defaults and not Path(defaults[key]).is_absolute():
            defaults[key] = str(PROJECT_ROOT / defaults[key])

    # Merge defaults into each condition
    resolved = []
    for cond in conditions:
        merged = {**defaults, **cond}
        # Resolve condition-specific paths
        for key in ["bounds", "ground_truth"]:
            if key in merged and not Path(merged[key]).is_absolute():
                merged[key] = str(PROJECT_ROOT / merged[key])
        if "detections_dir" in merged:
            det_dir = merged["detections_dir"]
            if not Path(det_dir).is_absolute():
                merged["detections_dir"] = str(PROJECT_ROOT / det_dir)
        resolved.append(merged)

    logger.info(
        "Loaded %d conditions from %s", len(resolved), path,
    )
    if metadata:
        defaults["_metadata"] = metadata

    return defaults, resolved


def write_batch_summary(
    all_summaries: list[dict],
    output_dir: Path,
    metadata: dict | None = None,
) -> None:
    """Write consolidated batch summary files.

    Produces CSV, Markdown, and JSON summaries across all conditions.

    Args:
        all_summaries: List of per-condition summary dicts (from
            evaluate_single_run or evaluate_multi_run_mean).
        output_dir: Output directory.
        metadata: Optional metadata dict from the batch YAML.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Flatten to rows: one per condition × buffer
    flat_rows = []
    has_mcc = any("tile_classification" in s for s in all_summaries)

    for summary in all_summaries:
        label = summary.get("label", "unknown")
        n_runs = summary.get("n_runs", 1)
        tc = summary.get("tile_classification", {})
        for buf in summary.get("buffers", []):
            row = {
                "label": label,
                "n_runs": n_runs,
                "buffer_metres": buf.get("buffer_metres"),
                "f1": buf.get("f1", 0),
                "f1_ci_lower": buf.get("f1_ci_lower", 0),
                "f1_ci_upper": buf.get("f1_ci_upper", 0),
                "precision": buf.get("precision", 0),
                "p_ci_lower": buf.get("p_ci_lower", 0),
                "p_ci_upper": buf.get("p_ci_upper", 0),
                "recall": buf.get("recall", 0),
                "r_ci_lower": buf.get("r_ci_lower", 0),
                "r_ci_upper": buf.get("r_ci_upper", 0),
            }
            if has_mcc and tc:
                mcc = tc.get("mcc", {})
                sens = tc.get("sensitivity", {})
                spec = tc.get("specificity", {})
                # E81: preserve ``None`` (undefined) all the way to the
                # renderers — the batch summary must not be the place
                # where an undefined MCC quietly becomes a zero.
                # D30: the bare names carry the OBSERVED statistic; the
                # resample means ride alongside under their own names.
                row.update({
                    "mcc": _observed_metric(mcc),
                    "mcc_ci_lower": mcc.get("ci_lower"),
                    "mcc_ci_upper": mcc.get("ci_upper"),
                    "sensitivity": _observed_metric(sens),
                    "specificity": _observed_metric(spec),
                    "mcc_boot_mean": mcc.get("mean"),
                    "sensitivity_boot_mean": sens.get("mean"),
                    "specificity_boot_mean": spec.get("mean"),
                })
            flat_rows.append(row)

    # Sort by F1 descending
    flat_rows.sort(key=lambda r: r["f1"], reverse=True)

    # CSV
    csv_path = output_dir / "batch_summary.csv"
    fieldnames = [
        "label", "n_runs", "buffer_metres",
        "f1", "f1_ci_lower", "f1_ci_upper",
        "precision", "p_ci_lower", "p_ci_upper",
        "recall", "r_ci_lower", "r_ci_upper",
    ]
    if has_mcc:
        fieldnames.extend([
            "mcc", "mcc_ci_lower", "mcc_ci_upper",
            "sensitivity", "specificity",
            # D30, as in the per-condition CSV: the resample means keep
            # their own columns, appended so existing positions hold.
            "mcc_boot_mean", "sensitivity_boot_mean",
            "specificity_boot_mean",
        ])
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in flat_rows:
            writer.writerow(row)
    logger.info("Batch CSV written: %s (%d rows)", csv_path, len(flat_rows))

    # JSON
    json_path = output_dir / "batch_summary.json"
    json_output = {
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_conditions": len(all_summaries),
        "n_rows": len(flat_rows),
    }
    if metadata:
        json_output["metadata"] = metadata
    json_output["rows"] = flat_rows
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2)
    logger.info("Batch JSON written: %s", json_path)

    # Markdown
    md_path = output_dir / "batch_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# N=1 Single-Pass Evaluation Summary\n\n")
        f.write(
            f"**Generated**: "
            f"{datetime.now(timezone.utc).isoformat()}  \n",
        )
        f.write(f"**Conditions**: {len(all_summaries)}  \n")
        if metadata:
            desc = metadata.get("description", "")
            if desc:
                f.write(f"**Description**: {desc}  \n")
        f.write("\n")

        # ``has_mcc`` mirrors the gating used for the CSV above: when any
        # condition supplied a ``tile_classification`` block, every row
        # already carries MCC / sensitivity / specificity values (the
        # row-builder above falls back to defaults for conditions that
        # did not), so the wider header is safe to emit.
        if has_mcc:
            f.write(
                "| Rank | Condition | Runs | Buffer "
                "| F1 | F1 CI | P | P CI | R | R CI "
                "| MCC | MCC CI | Sens | Spec |\n",
            )
            f.write("|" + "---|" * 14 + "\n")
        else:
            f.write(
                "| Rank | Condition | Runs | Buffer "
                "| F1 | F1 CI | P | P CI | R | R CI |\n",
            )
            f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        for i, row in enumerate(flat_rows, 1):
            row_body = (
                f"| {i} "
                f"| {row['label']} "
                f"| {row['n_runs']} "
                f"| {row['buffer_metres']}m "
                f"| {row['f1']:.3f} "
                f"| [{row['f1_ci_lower']:.3f}, {row['f1_ci_upper']:.3f}] "
                f"| {row['precision']:.3f} "
                f"| [{row['p_ci_lower']:.3f}, {row['p_ci_upper']:.3f}] "
                f"| {row['recall']:.3f} "
                f"| [{row['r_ci_lower']:.3f}, "
                f"{row['r_ci_upper']:.3f}] "
            )
            if has_mcc:
                # E81: ``undefined`` covers both "this condition carries
                # no tile_classification block" and "the metric is not
                # computable on this condition". Neither may render as
                # 0.000, which reads as a measured chance-level result.
                mcc_lo = row.get("mcc_ci_lower")
                mcc_hi = row.get("mcc_ci_upper")
                mcc_ci_cell = (
                    UNDEFINED_DISPLAY
                    if mcc_lo is None or mcc_hi is None
                    else f"[{mcc_lo:.3f}, {mcc_hi:.3f}]"
                )
                mcc_cells = (
                    f"| {_fmt_metric(row.get('mcc'))} "
                    f"| {mcc_ci_cell} "
                    f"| {_fmt_metric(row.get('sensitivity'))} "
                    f"| {_fmt_metric(row.get('specificity'))} "
                )
                f.write(row_body + mcc_cells + "|\n")
            else:
                f.write(row_body + "|\n")
        f.write("\n")
    logger.info("Batch Markdown written: %s", md_path)


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> int:
    """Run the detection evaluation."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate detection GeoJSON files against ground truth. "
            "Computes F1, Precision, Recall with 95% bootstrap CIs "
            "at configurable spatial buffer distances."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )

    # Input modes
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--detections", type=Path, nargs="+",
        help=(
            "One or more detection GeoJSON files. Multiple files are "
            "treated as independent runs of the same condition."
        ),
    )
    input_group.add_argument(
        "--detections-dir", type=Path,
        help="Directory containing detection runs (use with --glob).",
    )
    input_group.add_argument(
        "--batch", type=Path,
        help=(
            "YAML batch spec file listing multiple conditions to "
            "evaluate. Produces per-condition outputs plus a "
            "consolidated summary. See docstring for YAML format."
        ),
    )

    parser.add_argument(
        "--glob", type=str, default=None,
        help=(
            "Glob pattern for finding GeoJSON files within --detections-dir. "
            "Default: resolve both per-pass naming conventions via "
            "scripts.lib_detection_paths. Pass an explicit pattern only to "
            "target non-pass artefacts (e.g. 'accepted_run*.geojson')."
        ),
    )

    # Evaluation parameters
    parser.add_argument(
        "--buffers", type=int, nargs="+", default=DEFAULT_BUFFERS,
        help=(
            "Buffer distances in metres "
            f"(default: {' '.join(map(str, DEFAULT_BUFFERS))})"
        ),
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=DEFAULT_GROUND_TRUTH,
        help=f"Ground truth GeoJSON (default: {DEFAULT_GROUND_TRUTH.name})",
    )
    parser.add_argument(
        "--bounds", type=Path, default=DEFAULT_BOUNDS,
        help=f"Tile boundaries GeoJSON (default: {DEFAULT_BOUNDS.name})",
    )
    parser.add_argument(
        "--bootstrap", type=int, default=DEFAULT_BOOTSTRAP,
        help=f"Bootstrap iterations (default: {DEFAULT_BOOTSTRAP})",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
        help=f"Random seed (default: {DEFAULT_SEED})",
    )

    # Output
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Output directory (default: prints to console only)",
    )
    parser.add_argument(
        "--label", type=str, default=None,
        help="Human-readable condition label (default: derived from path)",
    )
    parser.add_argument(
        "--mcc", action="store_true",
        help=(
            "Compute tile-level MCC (Matthews Correlation Coefficient) "
            "with bootstrap CIs. Classifies each tile as populated or "
            "empty and reports MCC, sensitivity, and specificity."
        ),
    )
    parser.add_argument(
        "--require-clean-inputs", action="store_true",
        help=(
            "Refuse to score when any recipe input carries uncommitted "
            "changes or is untracked (defect D40 input-vintage drift). "
            "Without the flag a dirty input warns and is recorded in "
            "_metadata.input_git_state. Intended for replay and campaign "
            "contexts; gitignored and outside-repo inputs never trip it."
        ),
    )
    parser.add_argument(
        "--workers", type=int, default=1,
        help=(
            "Number of parallel worker processes for batch mode "
            "(default: 1). With the default of 1, conditions run "
            "strictly sequentially in the parent process — the exact "
            "legacy code path, preserved for reproducibility. Values "
            "greater than 1 evaluate independent conditions concurrently "
            "in a process pool (the bootstrap is CPU-bound, so processes "
            "side-step the GIL). A value of 0 means 'auto', resolving to "
            "os.cpu_count(). The pool is always capped at the number of "
            "conditions. Results are reordered back to YAML condition "
            "order before the batch summary is written, so the summary "
            "is byte-for-identical regardless of worker count. Ignored "
            "outside batch mode."
        ),
    )

    args = parser.parse_args()

    # ── Batch mode ────────────────────────────────────────────
    if args.batch:
        return _run_batch_mode(args)

    # ── Single-condition mode ─────────────────────────────────
    return _run_single_mode(args)


def _evaluate_condition(
    det_files: list[Path],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
    n_bootstrap: int,
    seed: int,
    label: str,
    output_dir: Path | None = None,
    compute_mcc: bool = False,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Evaluate a single condition (one or more detection files).

    Shared logic for both single and batch modes.

    Args:
        det_files: Detection GeoJSON file paths.
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Evaluation tile boundaries GeoDataFrame.
        buffers: Buffer distances in metres.
        n_bootstrap: Bootstrap iterations.
        seed: Random seed.
        label: Human-readable condition label.
        output_dir: Optional output directory for per-condition files.
        compute_mcc: If True, compute tile-level MCC with bootstrap CIs.
        metadata: Optional provenance metadata (see ``_build_metadata``)
            written into the resulting ``evaluation.json`` so the output
            is self-documenting.

    Returns:
        Summary dict with metrics.
    """
    run_results = []
    for det_path in det_files:
        run_label = det_path.stem
        logger.info("Evaluating: %s", det_path.name)
        gdf_det = load_geojson(det_path)

        # E72 coverage guard: per-pass detection GeoJSONs carry a
        # top-level ``processed_tiles`` array recording exactly which
        # tiles the pass completed. Reading it here lets the coverage
        # check COUNT unprocessed tiles against the evaluation bounds
        # instead of inferring coverage from detection density — the
        # inference that E43/E72 slipped under (240/487 tiles covered,
        # zero_fraction 0.4641 against a 0.5 threshold). Aggregation
        # artefacts (consensus/WBF/verified) do not preserve the array,
        # so they get ``None`` and fall back to the heuristic.
        processed_tiles = read_processed_tiles(det_path)
        if processed_tiles is None:
            logger.debug(
                "No processed_tiles record in %s — coverage falls back to "
                "the zero-fraction heuristic", det_path.name,
            )

        # Add source_tile column if missing (required by bootstrap)
        if "source_tile" not in gdf_det.columns and not gdf_det.empty:
            joined = gpd.sjoin(
                gdf_det, gdf_bounds[["tile_name", "geometry"]],
                how="left", predicate="intersects",
            )
            # Deduplicate: a single detection may intersect multiple
            # bounds tiles when tiles overlap (e.g. tile_size=384 with
            # stride=336 overlaps neighbours by 48 px). Keep the first
            # matching tile per detection so the index aligns with
            # gdf_det for assignment.
            joined = joined[~joined.index.duplicated(keep="first")]
            gdf_det["source_tile"] = joined["tile_name"]

        result = evaluate_single_run(
            gdf_det, gdf_ref, gdf_bounds,
            buffers=buffers,
            n_bootstrap=n_bootstrap,
            seed=seed,
            label=run_label,
            compute_mcc=compute_mcc,
            processed_tiles=processed_tiles,
        )
        run_results.append(result)

    # Compute summary
    if len(run_results) == 1:
        summary = run_results[0]
        summary["label"] = label
        per_run = None
    else:
        summary = evaluate_multi_run_mean(run_results, label=label)
        per_run = run_results

    if output_dir:
        write_outputs(summary, per_run, output_dir, metadata=metadata)

    return summary


def _run_single_mode(args: argparse.Namespace) -> int:
    """Run single-condition evaluation mode.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Resolve detection files
    if args.detections_dir:
        det_files = find_detection_files(args.detections_dir, args.glob)
    else:
        det_files = args.detections

    if not det_files:
        logger.error("No detection files found.")
        return 1

    logger.info("Detection files: %d", len(det_files))

    # Load reference data
    logger.info("Loading ground truth: %s", args.ground_truth)
    gdf_ref = load_geojson(args.ground_truth)
    logger.info("Loading bounds: %s", args.bounds)
    gdf_bounds = load_geojson(args.bounds)
    logger.info(
        "Reference: %d mounds, %d evaluation tiles",
        len(gdf_ref), len(gdf_bounds),
    )

    label = args.label or (
        det_files[0].parent.parent.name
        if len(det_files) > 1
        else det_files[0].stem
    )

    # Capture run provenance once, so the same metadata block is
    # attached to every output file produced by this invocation.
    run_metadata = _build_metadata(args)
    enforce_input_hygiene(
        run_metadata, getattr(args, "require_clean_inputs", False))

    summary = _evaluate_condition(
        det_files, gdf_ref, gdf_bounds,
        buffers=args.buffers,
        n_bootstrap=args.bootstrap,
        seed=args.seed,
        label=label,
        output_dir=args.output_dir,
        compute_mcc=args.mcc,
        metadata=run_metadata,
    )

    if not args.output_dir:
        print(json.dumps(summary, indent=2))

    return 0


def _evaluate_condition_worker(task: dict[str, Any]) -> tuple[int, dict]:
    """Evaluate one batch condition in a worker process.

    This is the picklable unit of parallel work. It receives only file
    paths and scalar parameters (never a GeoDataFrame), so nothing large
    or unpicklable crosses the process boundary. Each invocation loads
    its own ground-truth and bounds GeoDataFrames via
    :func:`load_geojson`, then delegates to :func:`_evaluate_condition`,
    which performs the identical metric and bootstrap logic used by the
    serial path. Because every condition carries a fixed per-condition
    ``seed``, results are deterministic and independent of which worker
    runs them or in what order they complete.

    The ``index`` is echoed back unchanged so the caller can reorder
    out-of-order futures into the original YAML condition order before
    writing the batch summary.

    Args:
        task: A task specification produced by
            :func:`_build_condition_tasks`. Required keys:

            - ``index`` (int): zero-based position in the YAML condition
              list, used to restore deterministic ordering.
            - ``det_files`` (list[Path]): detection GeoJSON paths.
            - ``ground_truth`` (Path): ground-truth reference GeoJSON.
            - ``bounds`` (Path): tile-boundaries GeoJSON.
            - ``buffers`` (list[int]): buffer distances in metres.
            - ``n_bootstrap`` (int): bootstrap iterations.
            - ``seed`` (int): per-condition random seed.
            - ``label`` (str): human-readable condition label.
            - ``output_dir`` (Path): per-condition output directory.
            - ``compute_mcc`` (bool): whether to compute tile-level MCC.
            - ``metadata`` (dict): provenance metadata block.

    Returns:
        A ``(index, summary)`` tuple, where ``summary`` is the per-condition
        metrics dict returned by :func:`_evaluate_condition`.
    """
    gdf_ref = load_geojson(task["ground_truth"])
    gdf_bounds = load_geojson(task["bounds"])
    summary = _evaluate_condition(
        task["det_files"],
        gdf_ref,
        gdf_bounds,
        buffers=task["buffers"],
        n_bootstrap=task["n_bootstrap"],
        seed=task["seed"],
        label=task["label"],
        output_dir=task["output_dir"],
        compute_mcc=task["compute_mcc"],
        metadata=task["metadata"],
    )
    return task["index"], summary


def _build_condition_tasks(
    conditions: list[dict],
    args: argparse.Namespace,
    run_metadata: dict[str, Any],
    gt_path: Path,
) -> list[dict[str, Any]]:
    """Resolve each YAML condition into a self-contained task specification.

    Walks the conditions in YAML order and, for each, resolves every
    parameter the evaluator needs (label, detection files, buffers,
    bootstrap iterations, seed, bounds path, per-condition metadata, and
    output directory) into a single picklable dict. Detection-file
    discovery (:func:`find_detection_files`) happens here, in the parent
    process, so empty conditions are skipped exactly as the serial loop
    skips them and the warning ordering is preserved.

    Crucially, only file paths and scalars are stored — no GeoDataFrames —
    so each task can be dispatched to a worker process without pickling
    large geometry objects. The serial and parallel code paths both consume
    these task specs, guaranteeing identical inputs to
    :func:`_evaluate_condition` regardless of worker count.

    Args:
        conditions: Resolved condition dicts from :func:`load_batch_yaml`.
        args: Parsed CLI arguments (supplies ``output_dir`` and ``mcc``).
        run_metadata: Shared run-provenance block from
            :func:`_build_metadata`.
        gt_path: Ground-truth GeoJSON path shared across all conditions.

    Returns:
        A list of task-specification dicts in YAML condition order, one
        per condition that has at least one detection file. Each dict's
        ``index`` field records its position in this returned list, used
        to reorder out-of-order parallel results.
    """
    tasks: list[dict[str, Any]] = []
    total = len(conditions)

    for i, cond in enumerate(conditions, 1):
        label = cond.get("label", f"condition_{i}")
        det_dir = Path(cond["detections_dir"])
        # None means "use the canonical resolver" (see find_detection_files).
        glob_pat = cond.get("glob")
        buffers = cond.get("buffers", DEFAULT_BUFFERS)
        n_bootstrap = cond.get("bootstrap", DEFAULT_BOOTSTRAP)
        seed = cond.get("seed", DEFAULT_SEED)
        bounds_path = cond.get("bounds", str(DEFAULT_BOUNDS))

        logger.info(
            "[%d/%d] %s (dir=%s)", i, total, label, det_dir,
        )

        # Find detection files (parent process, preserving skip/warn order).
        det_files = find_detection_files(det_dir, glob_pat)
        if not det_files:
            logger.warning("No files found for %s — skipping", label)
            continue

        logger.info("  %d detection files", len(det_files))

        # Each condition records the shared run provenance plus its own
        # bootstrap/seed values from the YAML — these may differ from
        # the CLI defaults captured in ``run_metadata``.
        cond_metadata: dict[str, Any] = {
            **run_metadata,
            "bootstrap": {
                "n_iterations": int(n_bootstrap),
                "seed": int(seed),
                "resampling_unit": "tile_level",
            },
            "input_files": {
                **run_metadata["input_files"],
                # Repo-relative for portability (det_dir/bounds_path are resolved to
                # absolute by load_batch_yaml for loading; see _repo_relative).
                "detections": _repo_relative(str(det_dir)),
                "bounds": _repo_relative(str(bounds_path)),
            },
        }

        tasks.append({
            # ``index`` is the position within ``tasks`` (skipped conditions
            # excluded), used to restore deterministic order after parallel
            # completion.
            "index": len(tasks),
            "det_files": det_files,
            "ground_truth": gt_path,
            "bounds": Path(bounds_path),
            "buffers": buffers,
            "n_bootstrap": n_bootstrap,
            "seed": seed,
            "label": label,
            "output_dir": args.output_dir / slugify(label),
            "compute_mcc": args.mcc,
            "metadata": cond_metadata,
        })

    return tasks


def _run_batch_mode(args: argparse.Namespace) -> int:
    """Run batch evaluation mode from a YAML spec.

    Evaluates multiple conditions, writes per-condition outputs, and
    produces a consolidated batch summary.

    Conditions are independent and deterministic (each uses a fixed
    per-condition seed), so they parallelise cleanly. With ``--workers 1``
    (the default) the conditions run strictly sequentially in the parent
    process — the exact legacy code path, preserved for reproducibility.
    With ``--workers`` greater than 1 (or 0 for ``os.cpu_count()``) the
    independent conditions are evaluated concurrently in a
    :class:`~concurrent.futures.ProcessPoolExecutor`. The CPU-bound
    bootstrap dominates wall-clock time, so processes (not threads)
    are used to side-step the Global Interpreter Lock (GIL). Whatever the
    worker count, results are reordered back to YAML condition order
    before the summary is written, so ``batch_summary.{json,csv,md}`` is
    byte-for-identical across worker counts.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    if not args.output_dir:
        logger.error("--output-dir is required in batch mode.")
        return 1

    defaults, conditions = load_batch_yaml(args.batch)
    metadata = defaults.get("_metadata")

    # Capture run provenance once for the entire batch. Each condition
    # inherits the same block, then overlays its own bootstrap/seed
    # values from the YAML below.
    run_metadata = _build_metadata(args)
    enforce_input_hygiene(
        run_metadata, getattr(args, "require_clean_inputs", False))

    # Ground-truth path shared across conditions (each worker loads its
    # own copy in parallel mode; the serial path loads it once below).
    gt_path = Path(defaults.get(
        "ground_truth",
        str(DEFAULT_GROUND_TRUTH),
    ))

    # Resolve every condition into a self-contained, picklable task spec.
    # Detection-file discovery and per-condition skip/warn ordering happen
    # here so the serial and parallel paths share identical inputs.
    tasks = _build_condition_tasks(conditions, args, run_metadata, gt_path)

    if not tasks:
        logger.error("No conditions produced results.")
        return 1

    # Resolve worker count: 0 means auto (os.cpu_count()), and the pool is
    # always capped at the number of conditions — no point spawning idle
    # workers, and a cap of 1 collapses to the serial path.
    if args.workers == 0:
        requested_workers = os.cpu_count() or 1
    else:
        requested_workers = max(1, args.workers)
    n_workers = min(requested_workers, len(tasks))

    # ``results`` is index-aligned to ``tasks`` (YAML condition order) so
    # the batch summary is deterministic regardless of completion order.
    results: list[dict | None] = [None] * len(tasks)

    if n_workers == 1:
        # ── Serial path (exact legacy behaviour) ──────────────────
        # Load ground truth once (shared across conditions) and reload
        # bounds only when the path changes, mirroring the original loop.
        logger.info("Loading ground truth: %s", gt_path)
        gdf_ref = load_geojson(gt_path)

        current_bounds_path: str | None = None
        gdf_bounds: gpd.GeoDataFrame | None = None

        for task in tasks:
            bounds_path = str(task["bounds"])
            if bounds_path != current_bounds_path:
                logger.info("Loading bounds: %s", bounds_path)
                gdf_bounds = load_geojson(task["bounds"])
                current_bounds_path = bounds_path
                logger.info("Bounds: %d tiles", len(gdf_bounds))

            summary = _evaluate_condition(
                task["det_files"], gdf_ref, gdf_bounds,
                buffers=task["buffers"],
                n_bootstrap=task["n_bootstrap"],
                seed=task["seed"],
                label=task["label"],
                output_dir=task["output_dir"],
                compute_mcc=task["compute_mcc"],
                metadata=task["metadata"],
            )
            results[task["index"]] = summary
    else:
        # ── Parallel path (process pool) ──────────────────────────
        # Each worker loads its own ground-truth and bounds; only paths and
        # scalars cross the process boundary. Futures complete out of order,
        # so each result is slotted back into its YAML position via ``index``.
        logger.info(
            "Evaluating %d conditions across %d worker processes",
            len(tasks), n_workers,
        )
        # Use the 'spawn' start method rather than the Linux default 'fork':
        # the parent may already be multi-threaded (geopandas/pyogrio,
        # NumPy/BLAS pools), and forking a multi-threaded process risks
        # deadlocks. 'spawn' starts each worker from a clean interpreter,
        # which also makes behaviour consistent across platforms. The slightly
        # higher per-worker start-up cost is negligible against the
        # bootstrap-dominated, minutes-long workload.
        mp_context = multiprocessing.get_context("spawn")
        with ProcessPoolExecutor(
            max_workers=n_workers, mp_context=mp_context,
        ) as executor:
            futures = {
                executor.submit(_evaluate_condition_worker, task): task["index"]
                for task in tasks
            }
            for future in as_completed(futures):
                index, summary = future.result()
                results[index] = summary

    # By construction every task produced a summary, so ``results`` has no
    # gaps; the cast to a plain list documents that intent for type checkers.
    all_summaries: list[dict] = [s for s in results if s is not None]

    # Write batch summary (deterministic order: YAML condition order).
    write_batch_summary(all_summaries, args.output_dir, metadata=metadata)

    logger.info(
        "Batch complete: %d conditions evaluated", len(all_summaries),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
