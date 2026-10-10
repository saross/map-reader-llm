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

Detection scope (PI ruling D50, 2026-10-07):
- scope_detections_to_frame(): detections scoped per map sheet by tile
  geometry, exactly as references are, each attributed to the sheet it
  was SEEN on (its origin sheet); every scorer above routes through it
- iter_sheet_scopes(): the per-sheet (detections, references) pairs every
  per-sheet matcher iterates, so no script keeps its own copy of the rule
- ReducedFrameRefusalError: a frame narrower than its detection set refuses
  a detection seen across its edge unless ``parent_bounds`` names the full
  frame (the D50 review, finding 2; PI decision, 2026-10-10)
"""

import functools
import json
import logging
import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

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

# Tile-join constants (E-series: the name-versus-geometry defect) ----------
#
# The tile confusion matrix behind tile-level Matthews Correlation
# Coefficient (MCC) needs, for each evaluation-frame tile, two booleans:
# does the tile hold a reference mound, and does it hold a detection. The
# reference side has always been geometric. The detection side, until
# 2026-09-12, was a **string** comparison of the detection's
# ``source_tile`` property against the frame's ``tile_name``:
#
#     dets_in_tile = gdf_det[gdf_det['source_tile'] == tile_name]
#
# That silently produces a meaningless confusion — and therefore a
# meaningless MCC — whenever a cell is scored on a frame whose tile
# vocabulary differs from the tiling its proposer ran on, because no
# detection's name is ever equal to any frame tile's name. F1 is
# geometric (buffer matching) and stays correct, so the failure looks
# like a plausible number rather than an error. Measured on the K-ladder
# Phase 2 corpus: 44 of 47 cells matched, 3 did not, and the three
# reported MCC 0.1337 beside F1 0.8495
# (``results/k-ladder-2026-09-12/phase2/tile-vocabulary-match.json``).
#
# The three supported joins are below. They are NOT interchangeable, and
# the reason is that the project's main evaluation frames **overlap**:
# ``inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`` holds
# 384 px tiles on a 336 px stride, so the sum of its tile areas is
# 1.2783x its union area and about 35 % of detections lie inside more
# than one frame tile. "The tile containing this point" is therefore not
# unique, and the three joins disagree by up to ~0.05 MCC on cells whose
# vocabulary matches (see ``reports/tile-mcc-geometric-join-2026-09-12.md``).
#
#: Legacy join. A tile holds a detection iff some detection's
#: ``source_tile`` string equals the tile's ``tile_name``. Encodes *which
#: tile the model was shown*, not *where the point is*. Correct only when
#: the cell's proposer tiling is the scoring frame; guarded by the
#: shortfall invariant below so it can no longer fail silently.
TILE_JOIN_ID: str = "id"
#: Geometric, one tile per point. Among the frame tiles the point
#: intersects (``intersects``, so a point exactly on a shared edge is a
#: candidate for both neighbours), take the tile whose centroid is
#: nearest; ties are broken by the lexicographically smallest
#: ``tile_name`` so the result is deterministic. Mirrors
#: ``scripts/prepare_h13_scoring.assign_primary_tiles``, the rule the
#: materialisation scripts use when they *write* ``source_tile``.
TILE_JOIN_GEOMETRIC_PRIMARY: str = "geometric-primary"
#: Geometric, every containing tile. A tile holds a detection iff some
#: detection intersects it. Symmetric with the reference side's
#: long-standing rule, so the confusion matrix is built one way on both
#: axes; on an overlapping frame a point is booked to every tile that
#: contains it.
TILE_JOIN_GEOMETRIC_CONTAINS: str = "geometric-contains"

TILE_JOINS: tuple[str, ...] = (
    TILE_JOIN_ID,
    TILE_JOIN_GEOMETRIC_PRIMARY,
    TILE_JOIN_GEOMETRIC_CONTAINS,
)

#: The default join for every scorer in the repository.
#:
#: **It is deliberately still the legacy string join, and flipping it is a
#: one-line change that must not be made without the PI's ruling on which
#: geometric variant to adopt.** The 2026-09-12 ruling ("make the tile
#: assignment geometric") was made on the understanding that a geometric
#: join reproduces the string join wherever the vocabulary matches. It
#: does not: the frames overlap, so on a matched cell the string join,
#: ``geometric-primary`` and ``geometric-contains`` give three different
#: confusions (measured 0.8270 / 0.8162 / 0.8667 MCC on
#: ``pv-high-image-t0.3-n1-opmax``). Defaulting to a geometric join would
#: therefore move every MCC in the committed corpus — 103 signed Era-2
#: board cells among them — and make the board's own confusion gate fail
#: on all of them. Until the variant is chosen, the default reproduces
#: published numbers and the shortfall invariant below refuses to emit an
#: MCC where the string join is not interpretable.
TILE_JOIN_DEFAULT: str = TILE_JOIN_ID

#: Named reasons the tile confusion can be refused rather than reported.
#: A refusal returns ``{"error": ..., "reason": ...}`` with the
#: diagnostics attached, so a caller never receives a number it should
#: not have.
TILE_JOIN_REASON_DETECTION_SHORTFALL: str = "tile_join_detection_shortfall"
TILE_JOIN_REASON_REFERENCE_SHORTFALL: str = "tile_join_reference_shortfall"
TILE_JOIN_REASON_NO_TILES: str = "no_tiles_in_bounds"
TILE_JOIN_REASON_NO_SOURCE_TILE: str = "detections_have_no_source_tile"

#: Every quantity a tile-join refusal withholds, and why. The PI's ruling
#: of 2026-09-13 (S153 ruling 6, recorded in the banner of
#: ``reports/tile-mcc-geometric-join-2026-09-12.md``) is that the
#: name-based ``id`` join is the published tile-MCC convention and that a
#: cell the invariant refuses has its **whole-frame F1 reported in full**
#: and its **per-tile statistics withheld**. This tuple is the machine
#: readable boundary between those two sets, and it is what the scorer
#: writes into the artefact so a reader never has to infer which numbers
#: were suppressed.
#:
#: The bootstrap confidence intervals are on the withheld side, which is
#: the one judgement in this list that is not obvious. They are intervals
#: on F1, precision and recall — quantities whose POINT estimates survive
#: a refusal — but :func:`bootstrap_ci` resamples **tiles** (the unit
#: fixed pre-lodgement in Decision 10, ``decisions-log.md:337``, and
#: echoed in every artefact's ``_metadata.bootstrap.resampling_unit``),
#: and the per-tile table it resamples is exactly what the invariant
#: refuses. A refused cell therefore has no interval, only a point.
TILE_JOIN_WITHHELD_QUANTITIES: tuple[str, ...] = (
    "tile_classification",
    "tile_mcc",
    "tile_sensitivity",
    "tile_specificity",
    "per_tile_table",
    "bootstrap_ci_f1",
    "bootstrap_ci_precision",
    "bootstrap_ci_recall",
    "per_tile_permutation_tests",
    "coverage_diagnostics",
)

#: What a refusal leaves standing: the buffer-matched point estimates.
#: :func:`calculate_f1_internal` matches detections to references
#: geometrically (Hungarian, per map sheet) and consults no tile, so a
#: mismatched tile vocabulary does not touch it. The one caveat is the
#: per-map-sheet SCOPING inside that function, which is a ``source_tile``
#: string prefix — see ``reports/tile-mcc-geometric-join-2026-09-12.md``
#: § 5.1(a); the refused Gemini 3.7 cells share the frame's map prefixes,
#: so their F1 is sound, but a cell from a differently-named sheet set
#: would lose detections from F1 as quietly as from the tile table. The
#: refusal record therefore reports both map-prefix vocabularies.
TILE_JOIN_REPORTED_QUANTITIES: tuple[str, ...] = (
    "f1_point",
    "precision_point",
    "recall_point",
    "n_detections",
)


class TileJoinRefusalError(ValueError):
    """The tile-join invariant refused a per-tile table.

    Subclasses :class:`ValueError` so that callers written against the
    original bare ``raise ValueError(...)`` — and the tier-1 tests that
    assert it — keep working unchanged. What the subclass adds is the
    refusal as *data*: a caller that wants to carry on and publish the
    quantities a refusal leaves standing (the buffer-matched F1,
    precision and recall point estimates) can read the reason and the
    shortfall counts off the exception instead of parsing its message.

    Attributes:
        reason: One of the ``TILE_JOIN_REASON_*`` constants.
        tile_join: The rule in force when the refusal fired.
        n_booked: In-frame points that reached a tile.
        n_considered: In-frame points that should have reached one.
        diagnostics: The ``tile_join_diagnostics`` block, or ``None``.
    """

    def __init__(
        self,
        message: str,
        *,
        reason: str,
        tile_join: str,
        n_booked: int,
        n_considered: int,
        diagnostics: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.tile_join = tile_join
        self.n_booked = n_booked
        self.n_considered = n_considered
        self.diagnostics = diagnostics

    @property
    def shortfall(self) -> int:
        """How many in-frame points were never credited to a tile."""
        return self.n_considered - self.n_booked


# Mitigation 3 (sparse-coverage transparency) constants --------------------
#
# When ``zero_fraction`` (proportion of tiles with TP+FP+FN == 0) exceeds
# this threshold, the bootstrap CI is flagged as ``sparse_cross_grid``.
# The 0.50 threshold sits ~40 percentage points above the worst observed
# matched-grid case (~11 %) and ~25 points below the least-sparse cross-grid
# case (~75 %), giving a clean separation in both directions. A strict ``>``
# boundary (not ``>=``) is used so that the threshold is the maximum
# acceptable coverage gap, not the minimum trigger.
#
# E72 hardening (2026-08-02) --------------------------------------------
#
# The zero-fraction heuristic above is an INFERENCE about coverage, and it
# has a blind spot that cost the project a false finding. A tile that was
# never processed but *does* contain ground-truth mounds contributes false
# negatives, not zeros — so it raises the FN count instead of the zero
# count, and the heuristic cannot see it. The E43/E72 case scored a
# 240-tile detection set against 487-tile bounds: 247 unprocessed tiles,
# 193 ground-truth mounds turned into artificial false negatives, and a
# ``zero_fraction`` of 0.4641 that slipped under the 0.5 threshold. The
# resulting +0.17 "temperature effect" was a coverage artefact
# (``docs/methodology/preregistration/protocol-errata.md`` § E72).
#
# The fix is to stop inferring. When the caller can supply the detection
# set's own record of which tiles it processed (the ``processed_tiles``
# array that ``scripts/4_detect_mounds_batch.py`` writes into every
# per-pass detection GeoJSON), coverage is COUNTED against the evaluation
# bounds rather than guessed from detection density, and any shortfall is
# flagged as ``partial_coverage`` regardless of what the zero-fraction
# says. The heuristic remains the fallback for detection sets that carry
# no ``processed_tiles`` record — notably consensus/voting artefacts,
# which are written by the aggregation step and do not preserve it.
DEFAULT_COVERAGE_THRESHOLD: float = 0.5
COVERAGE_STATUS_NORMAL: str = "normal"
COVERAGE_STATUS_SPARSE: str = "sparse_cross_grid"
COVERAGE_STATUS_PARTIAL: str = "partial_coverage"

#: Coverage was not assessed, because assessing it needs the per-tile
#: table the tile-join invariant refused. This is distinct from
#: :data:`COVERAGE_STATUS_NORMAL`, which is a positive finding: a refused
#: cell's coverage is UNKNOWN, and recording it as "normal" would assert
#: a check that never ran (the D17 principle — an absent parameter is not
#: evidence of the standard one).
COVERAGE_STATUS_WITHHELD: str = "withheld"

#: How ``coverage_status`` was decided — direct evidence or inference.
COVERAGE_SOURCE_PROCESSED_TILES: str = "processed_tiles"
COVERAGE_SOURCE_HEURISTIC: str = "zero_fraction_heuristic"

#: Which rule produced a buffer row's ``ci_unreliable`` flag (defect D42:
#: one shared definition for the writer and the migration, so the two can
#: never diverge again). ``BASIS_FULL`` means both measured grounds could
#: be evaluated; ``BASIS_EXCLUSION_ONLY`` marks legacy rows whose
#: committed artefact carries no ``coverage_status``, so only the
#: exclusion ground could be tested.
CI_FLAG_BASIS_FULL: str = "measured-exclusion-or-partial-coverage"
CI_FLAG_BASIS_EXCLUSION_ONLY: str = "measured-exclusion-only"

#: A third basis, for a buffer row that has no interval at all because
#: the tile-join invariant refused the per-tile table the bootstrap
#: resamples. Neither measured ground is evaluable on such a row, and
#: ``ci_unreliable`` there does not mean "the interval is untrustworthy"
#: but "there is no interval" — which a reader must be able to tell apart
#: from a measured exclusion.
CI_FLAG_BASIS_WITHHELD: str = "ci-withheld-tile-join-refusal"

#: (point key, lower-bound key, upper-bound key) triples as committed in
#: evaluation buffer rows.
CI_METRIC_BOUNDS: tuple[tuple[str, str, str], ...] = (
    ("f1", "f1_ci_lower", "f1_ci_upper"),
    ("precision", "p_ci_lower", "p_ci_upper"),
    ("recall", "r_ci_lower", "r_ci_upper"),
)


def measured_exclusion(row: dict) -> bool:
    """True when any committed CI in a buffer row excludes its own point.

    Operates on the ROW AS STORED (4 dp rounded values), which is the
    convention the 2026-08-20 measured-flag migration established for
    committed artefacts; metrics with any missing bound are skipped.

    Args:
        row: An evaluation buffer row carrying point estimates and CI
            bounds under the ``CI_METRIC_BOUNDS`` key triples.

    Returns:
        Whether any metric's stored point lies outside its stored CI.
    """
    for point_key, lo_key, hi_key in CI_METRIC_BOUNDS:
        point, lo, hi = row.get(point_key), row.get(lo_key), row.get(hi_key)
        if point is None or lo is None or hi is None:
            continue
        if not (lo <= point <= hi):
            return True
    return False


def read_processed_tiles(source: Path | str | dict) -> set[str] | None:
    """Read a detection set's ``processed_tiles`` record, if it has one.

    Every per-pass detection GeoJSON written by
    ``scripts/4_detect_mounds_batch.py`` (and its Batch-API sibling in
    ``scripts/lib_batch_api.py``) carries a top-level ``processed_tiles``
    array listing the tile filenames the pass actually completed. That
    array is the authoritative coverage record for the pass — the audit
    charter's authority #1 for tile coverage — and is what
    :func:`_compute_coverage` needs in order to count unprocessed tiles
    instead of inferring them (E72).

    Aggregation artefacts (``consensus_tN.geojson``, WBF/greedy fusions,
    verified outputs) are written by a different code path and do **not**
    preserve the array; this function returns ``None`` for them, which is
    the signal to fall back to the zero-fraction heuristic.

    Args:
        source: Path to a detection GeoJSON, or an already-parsed GeoJSON
            ``dict``. Passing the parsed dict avoids a second read when
            the caller has already loaded the file.

    Returns:
        A set of processed tile filenames, or ``None`` when the source
        carries no ``processed_tiles`` record (absent key, unreadable
        file, or malformed JSON). ``None`` means "no coverage evidence",
        which is deliberately distinct from an empty set (which would
        mean "evidence that nothing was processed").

    Example:
        >>> tiles = read_processed_tiles(  # doctest: +SKIP
        ...     Path("outputs/h11/consensus-384-UNINTENDED-T1.0/384/"
        ...          "run_1/detections_384_run01.geojson")
        ... )
        >>> len(tiles)  # doctest: +SKIP
        240
    """
    if isinstance(source, dict):
        payload: Any = source
    else:
        path = Path(source)
        try:
            with path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            # A missing or malformed file is "no evidence", not an error:
            # the caller's fallback (the heuristic) is still correct, and
            # raising here would break evaluation of legitimately older
            # artefacts. Log so the silence is visible.
            logger.warning(
                "Could not read processed_tiles from %s: %s", source, exc,
            )
            return None

    if not isinstance(payload, dict):
        return None
    processed = payload.get("processed_tiles")
    if processed is None or not isinstance(processed, (list, tuple, set)):
        return None
    return {str(tile) for tile in processed}


def _compute_coverage(
    tile_metrics: pd.DataFrame,
    threshold: float = DEFAULT_COVERAGE_THRESHOLD,
    processed_tiles: set[str] | None = None,
) -> dict[str, Any]:
    """Compute sparse- and partial-coverage diagnostics for a tile-metrics frame.

    Two independent checks, in priority order:

    1. **Partial coverage (E72, direct evidence)** — when ``processed_tiles``
       is supplied, the evaluation-bounds tiles absent from it are counted
       directly. Any shortfall sets ``coverage_status`` to
       ``"partial_coverage"``: the detection set does not cover the bounds
       it is being scored against, so every ground-truth mound on an
       unprocessed tile is an artificial false negative. This check does
       not consult the zero-fraction at all.
    2. **Sparse coverage (Mitigation 3, inference)** — the fraction of
       tiles with zero TP, FP, and FN counts. When it strictly exceeds
       ``threshold`` the coverage is flagged ``sparse_cross_grid``:
       bootstrap CIs over such distributions are unreliable and should be
       suppressed in human-readable outputs. The numeric CI bounds are
       still computed and returned in the JSON output for downstream
       consumers that opt to read them.

    Check 1 is authoritative where it applies because it counts rather
    than infers; check 2 is the fallback for detection sets with no
    ``processed_tiles`` record. Behaviour is unchanged from the pre-E72
    implementation whenever ``processed_tiles`` is ``None`` (no evidence)
    or complete (full coverage) — the hardening is purely additive.

    Args:
        tile_metrics: DataFrame with columns ``[tile_name, tp, fp, fn]``,
            as returned by :func:`compute_per_tile_tp_fp_fn`. Its
            ``tile_name`` column is one row per evaluation-bounds tile,
            which is what the partial-coverage check counts against.
        threshold: Zero-fraction threshold above which coverage is sparse.
            Defaults to :data:`DEFAULT_COVERAGE_THRESHOLD` (0.5). Strict
            ``>`` boundary semantics.
        processed_tiles: Optional set of tile filenames the detection set
            actually processed, from :func:`read_processed_tiles`. ``None``
            (the default) means no coverage evidence is available and only
            the zero-fraction heuristic runs.

    Returns:
        Dict with keys ``n_tiles``, ``n_zero_count_tiles``,
        ``zero_fraction``, ``threshold``, ``coverage_status``
        (``"normal"``, ``"sparse_cross_grid"``, or ``"partial_coverage"``),
        ``coverage_source`` (``"processed_tiles"`` or
        ``"zero_fraction_heuristic"``), ``n_processed_tiles`` and
        ``n_unprocessed_tiles`` (``None`` under the heuristic), and
        ``coverage_detail`` — a human-readable string such as
        ``"partial: 247/487 tiles unprocessed"``, or ``None`` when
        coverage is not partial.

    Example:
        >>> import pandas as pd
        >>> frame = pd.DataFrame(
        ...     [{"tile_name": f"t{i}", "tp": 1, "fp": 0, "fn": 0}
        ...      for i in range(4)]
        ... )
        >>> cov = _compute_coverage(frame, processed_tiles={"t0", "t1"})
        >>> cov["coverage_status"], cov["coverage_detail"]
        ('partial_coverage', 'partial: 2/4 tiles unprocessed')
    """
    n_tiles = len(tile_metrics)
    if n_tiles == 0:
        return {
            "n_tiles": 0,
            "n_zero_count_tiles": 0,
            "zero_fraction": 0.0,
            "threshold": float(threshold),
            "coverage_status": COVERAGE_STATUS_NORMAL,
            "coverage_source": (
                COVERAGE_SOURCE_PROCESSED_TILES
                if processed_tiles is not None
                else COVERAGE_SOURCE_HEURISTIC
            ),
            "n_processed_tiles": None,
            "n_unprocessed_tiles": None,
            "coverage_detail": None,
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

    # Direct coverage count (E72). ``tile_metrics`` carries one row per
    # evaluation-bounds tile (``compute_per_tile_tp_fp_fn`` seeds its
    # counter from every bounds row), so the bounds tile set is exactly
    # this column and the set difference is the unprocessed tile count.
    n_processed: int | None = None
    n_unprocessed: int | None = None
    detail: str | None = None
    if processed_tiles is not None:
        bounds_tiles = set(tile_metrics["tile_name"].astype(str))
        unprocessed = bounds_tiles - processed_tiles
        n_unprocessed = len(unprocessed)
        n_processed = len(bounds_tiles) - n_unprocessed
        if n_unprocessed:
            detail = f"partial: {n_unprocessed}/{n_tiles} tiles unprocessed"

    if n_unprocessed:
        # Direct evidence of a coverage gap outranks the heuristic: the
        # E72 set would read "normal" on zero-fraction alone (0.4641).
        status = COVERAGE_STATUS_PARTIAL
    elif is_sparse:
        status = COVERAGE_STATUS_SPARSE
    else:
        status = COVERAGE_STATUS_NORMAL

    return {
        "n_tiles": int(n_tiles),
        "n_zero_count_tiles": n_zero,
        "zero_fraction": float(zero_fraction),
        "threshold": float(threshold),
        "coverage_status": status,
        "coverage_source": (
            COVERAGE_SOURCE_PROCESSED_TILES
            if processed_tiles is not None
            else COVERAGE_SOURCE_HEURISTIC
        ),
        "n_processed_tiles": n_processed,
        "n_unprocessed_tiles": n_unprocessed,
        "coverage_detail": detail,
    }


def _bca_ci_from_indices(
    indices: np.ndarray,
    statistic: Callable[[np.ndarray], float],
    n_iterations: int = 1000,
    random_seed: int | None = None,
    confidence_level: float = 0.95,
    skip_undefined: bool = False,
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
        skip_undefined: When ``True``, resamples on which ``statistic``
            returns a non-finite value (``NaN``) are treated as
            *undefined* and **dropped** before the bounds and the mean
            are computed, rather than being folded in as numbers.
            Errata E81: substituting ``0.0`` for an undefined Matthews
            Correlation Coefficient (MCC) makes every bound a mixture of
            measurements and placeholders. When every resample is
            undefined the returned ``mean`` / ``ci_lower`` / ``ci_upper``
            are ``None`` and ``method`` is ``"undefined"``. Leave
            ``False`` (the default) for statistics that are always
            defined — the numeric path is then bit-identical to the
            pre-E81 behaviour.

    Returns:
        Dict with keys ``mean``, ``ci_lower``, ``ci_upper`` (each
        ``float``, or ``None`` when ``skip_undefined`` is set and every
        resample was undefined), ``method`` (``"BCa"``,
        ``"percentile_fallback"``, or ``"undefined"``), ``n_valid`` (the
        number of resamples that produced a finite statistic), and
        ``bootstrap_distribution`` (numpy array — useful for diagnostics
        and back-compat callers that compute their own percentiles).
    """
    indices = np.asarray(indices)

    def _vectorised(idx_array: np.ndarray, axis: int = -1) -> np.ndarray:
        """Apply ``statistic`` along ``axis`` for scipy's vectorised loop.

        scipy's ``vectorized=True`` contract is *"the statistic is
        computed along ``axis`` and that axis is consumed"*: the call
        receives an array whose ``axis`` holds the resampled
        observations, and every remaining axis enumerates independent
        resamples. Concretely ``scipy.stats.bootstrap`` makes three
        kinds of call for a one-sample statistic on ``n`` observations
        with ``B`` resamples, all with ``axis=-1``:

        * ``(n,)`` — the point estimate, one scalar out;
        * ``(B, n)`` — the resample batch, ``B`` scalars out;
        * ``(n, n - 1)`` — the BCa jackknife batch (``n`` leave-one-out
          rows of ``n - 1`` observations), ``n`` scalars out.

        The correct adaptation therefore iterates the *leading* axes and
        hands ``statistic`` one slice **along** ``axis`` per call.

        **Defect history (D15, fixed 2026-08-19).** This wrapper
        previously did ``np.moveaxis(idx_array, axis, 0)`` and iterated
        the result, which transposes the batch: on a ``(B, n)`` input it
        returned ``n`` statistics of ``B`` draws each instead of ``B``
        statistics of ``n`` draws each, and on the jackknife batch it
        returned ``n - 1`` meaningless pseudo-values. scipy performs no
        length check on a vectorised statistic's return value, so this
        failed silently: the resulting interval scaled as
        ``sqrt(n / B)`` of the correct width — too narrow whenever
        ``B > n`` and too wide whenever ``B < n``. See
        ``reports/bca-axis-defect-2026-08-18.md``.

        Args:
            idx_array: Index array supplied by scipy — 1-D for the point
                estimate, otherwise a resample or jackknife batch.
            axis: Axis holding the resampled observations. scipy passes
                ``-1`` for every batched call.

        Returns:
            A float for the 1-D case, otherwise an array whose shape is
            ``idx_array``'s shape with ``axis`` removed.
        """
        idx_array = np.asarray(idx_array, dtype=int)
        if idx_array.ndim == 1:
            return float(statistic(idx_array))
        # Put the observation axis last, then flatten every remaining
        # (resample-enumerating) axis so each row is one resample of
        # ``n`` observations. Reshaping back drops ``axis``, which is
        # exactly what scipy's contract requires.
        moved = np.moveaxis(idx_array, axis, -1)
        flat = moved.reshape(-1, moved.shape[-1])
        return np.array(
            [statistic(row) for row in flat],
            dtype=float,
        ).reshape(moved.shape[:-1])

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
            if skip_undefined:
                # E81: drop undefined resamples instead of counting them
                # as zeros. ``nanpercentile`` over the same resample
                # sequence — the draws are unchanged, only the handling
                # of the undefined ones is.
                finite = distribution[np.isfinite(distribution)]
                if finite.size:
                    ci_lower = float(np.nanpercentile(distribution, 2.5))
                    ci_upper = float(np.nanpercentile(distribution, 97.5))
                else:
                    ci_lower = float("nan")
                    ci_upper = float("nan")
            else:
                ci_lower = float(np.percentile(distribution, 2.5))
                ci_upper = float(np.percentile(distribution, 97.5))
            method_used = "percentile_fallback"

    n_valid = int(np.count_nonzero(np.isfinite(distribution)))

    if skip_undefined and n_valid == 0:
        # Every resample was degenerate: the metric has no bootstrap
        # distribution at all. Report that honestly rather than
        # manufacturing a point at zero.
        return {
            "mean": None,
            "ci_lower": None,
            "ci_upper": None,
            "method": "undefined",
            "n_valid": 0,
            "bootstrap_distribution": distribution,
        }

    if skip_undefined:
        mean_value = float(np.nanmean(distribution))
    else:
        mean_value = (
            float(np.mean(distribution)) if distribution.size else 0.0
        )

    return {
        "mean": mean_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "method": method_used,
        "n_valid": n_valid,
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


# ── Detection scope: origin sheet, tile geometry (PI ruling D50) ─────────
#
# Until 2026-10-07 every per-sheet scorer scoped the two sides of the match
# by different rules. References were scoped GEOMETRICALLY: a reference on
# sheet M counted only if it intersected one of M's frame tiles
# (:func:`scope_references_to_tiles`). Detections were scoped by NAME: every
# detection whose ``source_tile`` began with M was kept, wherever it lay. A
# detection outside the frame was therefore booked as a false positive
# whenever its proposer tile carried a frame sheet's name, and silently
# dropped whenever a re-keying step had nulled its ``source_tile`` — the same
# detection, two different fates, decided by how the cell was built rather
# than by where the point is (``reports/frames-blast-radius-2026-10-07.md``,
# 70 committed cells affected, three of them registered conditions).
#
# The PI's ruling D50 (``planning/pi-decisions-2026-09-20.md``) adopts the
# report's option (A):
#
# 1. **Detections are scoped exactly as references are**: per sheet, kept
#    only if they intersect one of that sheet's frame tiles (``intersects``,
#    the predicate :func:`scope_references_to_tiles` uses).
# 2. **Each detection is attributed to its ORIGIN sheet** — the sheet whose
#    tile the proposer was shown. A detection is never re-keyed to another
#    sheet: where a file records the proposer's own tile(s) in one of
#    :data:`ORIGIN_TILE_COLUMNS` and a later step re-wrote ``source_tile`` to
#    a neighbouring sheet's tile (tier E's and h13's materialisers did,
#    through the overlap of padded tiles at sheet edges), the recorded
#    origin wins. Such a detection would otherwise be matched against the
#    wrong sheet's references and turn one true positive into a false
#    positive plus a false negative (report § 5.4).
# 3. **The rule is visible**: :class:`DetectionScope` carries the counts, and
#    ``evaluate_detections.py`` writes them into every ``evaluation.json`` as
#    ``detection_scope``, beside the tile-join diagnostics.
#
# A cell whose detections all lie inside their own sheet's tiles and carry
# no contradicting origin receives exactly the rows it received before, in
# the same order, so its numbers are unchanged bit for bit.

#: The detection-scope rule in force, written into every evaluation.
DETECTION_SCOPE_RULE: str = "origin-sheet-geometric"

#: Where the rule comes from, quoted into the diagnostics block.
DETECTION_SCOPE_RULING: str = (
    "PI ruling D50, 2026-10-07 (planning/pi-decisions-2026-09-20.md): "
    "detections are scoped per sheet by tile geometry, as references are, "
    "each attributed to its origin sheet and never re-keyed to another "
    "sheet. Option (A) of reports/frames-blast-radius-2026-10-07.md § 6."
)

#: Columns recording the proposer tile(s) a detection was SEEN on, in the
#: order they are consulted. ``origin_source_tile`` is a single name (written
#: by the D50 re-keying fix); ``origin_tiles`` is the h13 materialisers'
#: ``;``-joined list; ``source_tiles`` is the consensus step's cluster-member
#: list, which may arrive as a list, a JSON string, or — after a geopandas
#: round trip — the ``repr`` of a NumPy array (tier E's materialised cells).
ORIGIN_TILE_COLUMNS: tuple[str, ...] = (
    "origin_source_tile",
    "origin_tiles",
    "source_tiles",
)

#: The study's map sheets: the stable parent catalogue a recorded origin is
#: identified against when it names no sheet of the frame being scored (the
#: D50 review, finding 2: Astra, 2026-10-09). It lets the scope tell an
#: origin on a REAL sheet the frame leaves out — a frame reduced to some of
#: the sheets a detection set was proposed on — from a tile vocabulary the
#: study never used. The four gold-standard sheets and the 55-map
#: generalisation set, exactly the sheets of
#: ``inputs/vectors/bounds/384/full_evaluation_bounds.geojson`` and
#: ``inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`` (a tier-1
#: test holds the two equal). No name is a prefix of another, so the
#: longest-prefix rule reads each tile name one way.
STUDY_SHEETS: frozenset[str] = frozenset({
    # Gold standard (four sheets).
    "K-35-052-4_32635", "K-35-053-3_Elenovo", "K-35-062-2_Rakovski",
    "K-35-078-1_Lesovo",
    # 55-map generalisation set.
    "K-35-042-3", "K-35-050-4", "K-35-051-3", "K-35-051-4", "K-35-052-2",
    "K-35-052-3", "K-35-053-1", "K-35-053-2", "K-35-053-4_Boyadzhik",
    "K-35-054-1_Straldzha_4326", "K-35-054-2_Atolov_4326", "K-35-054-3_Yambol",
    "K-35-054-4_Voynika", "K-35-055-1", "K-35-055-2", "K-35-055-3",
    "K-35-055-4", "K-35-056-3", "K-35-062-4_Asenovgrad_4326",
    "K-35-063-1_Granit_4326", "K-35-063-2_Chirpan_4326",
    "K-35-063-3_Tatarevo_4326", "K-35-063-4_Skobelevo_4326",
    "K-35-064-1_Sredets_4326", "K-35-064-2_Radnevo_4326",
    "K-35-064-3_Dimitrovgrad_4326", "K-35-064-4_Galabovo_4326",
    "K-35-065-1_Radetski_4326", "K-35-065-2_GManastir_4326",
    "K-35-065-3_Glavan_4326", "K-35-065-4", "K-35-066-1", "K-35-066-2",
    "K-35-066-3", "K-35-066-4", "K-35-067-1", "K-35-067-2", "K-35-067-3",
    "K-35-067-4", "K-35-074-1", "K-35-074-2", "K-35-074-3", "K-35-074-4",
    "K-35-075-1", "K-35-075-2", "K-35-075-3", "K-35-075-4", "K-35-076-1",
    "K-35-076-2", "K-35-076-3", "K-35-076-4", "K-35-077-1", "K-35-077-2",
    "K-35-077-3", "K-35-077-4",
})

#: Quoted tokens inside a list-like string: ``'a'`` or ``"a"``.
_QUOTED_TOKEN_RE = re.compile(r"'([^']*)'|\"([^\"]*)\"")

#: What a list-like string holding no name may consist of (``"['']"``,
#: ``"[ ]"``): brackets, quotes, commas and white space.
_EMPTY_LIST_TEXT_RE = re.compile(r"[\[\]'\",\s]*")

#: The forms :func:`parse_tile_list` accepts, quoted in its errors.
_TILE_LIST_FORMS = (
    "a str (bare name, ';'-joined list, JSON list, or NumPy-array repr), "
    "a list, tuple or NumPy array of such strings, or a missing value "
    "(None, NaN, pd.NA)"
)


def _is_missing(value: Any) -> bool:
    """Whether a cell or list element records nothing (None, NaN, pd.NA, NaT).

    Args:
        value: A scalar from a GeoDataFrame cell or a list element.

    Returns:
        ``True`` for ``None``, a float or NumPy NaN, ``pd.NA`` and ``pd.NaT``.
    """
    if value is None or value is pd.NA or value is pd.NaT:
        return True
    return isinstance(value, (float, np.floating)) and bool(np.isnan(value))


@functools.lru_cache(maxsize=65536)
def _parse_tile_list_text(text: str) -> tuple[str, ...]:
    """Parse one string-encoded tile list (cached: sweeps re-read one universe).

    Args:
        text: A JSON list, a NumPy-array ``repr``, a ``;``-joined list or a
            bare tile name.

    Returns:
        The non-empty tile names, in their recorded order.

    Raises:
        ValueError: If a ``[``-string is neither JSON nor holds a quoted
            name (``"[A.png, B.png]"``), or a JSON list holds anything but
            names and nulls. Before 2026-10-08 the first gave an empty list
            and the second a bogus name, silently (PR #26 review, finding 2).
    """
    text = text.strip()
    if not text:
        return ()
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # The repr of a NumPy array of strings: space-separated quoted
            # tokens, possibly wrapped over several lines. Not JSON.
            names = tuple(
                a or b for a, b in _QUOTED_TOKEN_RE.findall(text) if (a or b)
            )
            if not names and not _EMPTY_LIST_TEXT_RE.fullmatch(text):
                raise ValueError(
                    f"unparseable tile list {text[:120]!r}: it starts with '[' but "
                    f"is not JSON and holds no quoted tile name"
                ) from None
            return names
        names_json: list[str] = []
        for v in parsed:  # a JSON text starting with '[' is always a list
            if _is_missing(v) or v == "":
                continue
            if not isinstance(v, str):
                raise ValueError(
                    f"unparseable tile list {text[:120]!r}: element {v!r} is a "
                    f"{type(v).__name__}, not a tile name"
                )
            names_json.append(v)
        return tuple(names_json)
    return tuple(part.strip() for part in text.split(";") if part.strip())


def parse_tile_list(value: Any) -> list[str]:
    """Normalise a recorded tile-list property to a list of tile names.

    Every serialisation the corpus holds is accepted: a Python list or
    tuple, a NumPy array, a JSON list string, the ``repr`` of a NumPy array
    (``"['a.png' 'b.png'\\n 'c.png']"``), a ``;``-joined string (h13's
    ``origin_tiles``) and a bare name. Missing values (``None``, NaN,
    ``pd.NA``) give an empty list, so a caller searching several columns
    moves on to the next; missing elements inside a list are dropped.

    Anything else raises rather than becoming a name or an empty list
    (PR #26 review, finding 2): before 2026-10-08 a set, dict or number
    became one bogus name, ``pd.NA`` became ``'<NA>'`` (which stopped the
    search at that column), a NaN element became ``'nan'``, and an unquoted
    ``[``-string became ``[]`` without trace.

    Args:
        value: The property value as read from a GeoDataFrame cell.

    Returns:
        Tile names, in their recorded order, empties dropped.

    Raises:
        TypeError: If the value, or an element of a list, is of a type no
            serialisation produces (a set, dict, number, bytes, ...).
        ValueError: If a string is list-like but unparseable
            (see :func:`_parse_tile_list_text`).

    Example:
        >>> parse_tile_list("['K-1_x0_y0.png' 'K-1_x0_y192.png']")
        ['K-1_x0_y0.png', 'K-1_x0_y192.png']
        >>> parse_tile_list("K-1_x0_y0.png;K-2_x0_y0.png")
        ['K-1_x0_y0.png', 'K-2_x0_y0.png']
    """
    if isinstance(value, str):  # np.str_ included
        return list(_parse_tile_list_text(str(value)))
    if isinstance(value, (list, tuple, np.ndarray)):
        # Each element is parsed as text too: reading a GeoJSON whose
        # property is the STRING repr of a NumPy array (tier E's materialised
        # cells) returns a one-element array holding that whole repr, which
        # must expand to its names. A plain tile name parses to itself.
        names: list[str] = []
        for v in value:
            if _is_missing(v):
                continue
            if not isinstance(v, str):
                raise TypeError(
                    f"unsupported tile-list element {v!r} "
                    f"({type(v).__name__}) in {value!r:.120}; expected {_TILE_LIST_FORMS}"
                )
            names.extend(_parse_tile_list_text(str(v)))
        return names
    if _is_missing(value):
        return []
    raise TypeError(
        f"unsupported tile-list value {value!r:.120} ({type(value).__name__}); "
        f"expected {_TILE_LIST_FORMS}"
    )


def _parse_origin_cell(value: Any, column: str, pos: int) -> list[str]:
    """:func:`parse_tile_list` on one cell, naming the column and row on failure.

    Args:
        value: The cell's value.
        column: Its column (an origin column or ``source_tile``).
        pos: Its row position.

    Returns:
        The tile names.

    Raises:
        TypeError, ValueError: As :func:`parse_tile_list`, prefixed with the
            column and row, so a refused file says where to look.
    """
    try:
        return parse_tile_list(value)
    except (TypeError, ValueError) as exc:
        raise type(exc)(f"column {column!r}, row {pos}: {exc}") from exc


def frame_sheets(gdf_bounds: gpd.GeoDataFrame) -> list[str]:
    """Return the map sheets a frame covers, as every per-sheet scorer derives them.

    Args:
        gdf_bounds: Frame tile polygons with a ``tile_name`` column.

    Returns:
        Sorted sheet names (``get_map_name`` of each tile), ``"Unknown"``
        excluded, as :func:`calculate_f1_internal` has always skipped it.
    """
    names = {get_map_name(str(n)) for n in gdf_bounds["tile_name"].unique()}
    names.discard("Unknown")
    return sorted(names)


def _sheet_of_tile_name(name: Any, sheets_longest_first: list[str]) -> str | None:
    """The frame sheet a tile name belongs to, by the scorers' prefix rule.

    The per-sheet scorers have always put a detection on sheet M when its
    ``source_tile`` *starts with* M (not when ``get_map_name`` equals M), so a
    name in a different tile vocabulary of the same sheet — a 192 px stride
    against a 336 px frame, or a 55-map tile carrying a place-name suffix —
    still lands on its sheet. The longest matching prefix wins, so the rule
    is unambiguous even if one sheet name were a prefix of another.

    Args:
        name: A tile name (or a missing value).
        sheets_longest_first: Frame sheet names, longest first.

    Returns:
        The frame sheet, or ``None`` for a missing, empty or foreign name.
    """
    if not isinstance(name, str) or not name:
        return None
    for sheet in sheets_longest_first:
        if name.startswith(sheet):
            return sheet
    return None


def frame_tile_sheets(gdf_bounds: gpd.GeoDataFrame) -> np.ndarray:
    """Each frame tile's sheet, by the one rule both sides of the scorer use.

    The detection scope puts a frame tile on the LONGEST frame sheet its
    name starts with (:func:`_sheet_of_tile_name`); the per-sheet loop used
    to select a sheet's tiles with a bare ``str.startswith(sheet)``, which
    also hands sheet ``A`` every tile of a sheet ``AB``. Where one sheet
    name is a prefix of another, references were then scoped to tiles the
    detection side gave to the other sheet (the D50 review, finding 3).
    Every per-sheet selection now reads this one assignment. Among the
    study's sheets (:data:`STUDY_SHEETS`) no name is a prefix of another,
    so on every committed frame it selects exactly the tiles
    ``str.startswith`` selected, in the same order.

    Args:
        gdf_bounds: Frame tile polygons with a ``tile_name`` column.

    Returns:
        An object array aligned row for row with ``gdf_bounds``: each
        tile's frame sheet, or ``None`` for a tile on no frame sheet.

    Example:
        >>> sheets = frame_tile_sheets(bounds)  # doctest: +SKIP
        >>> bounds[sheets == "K-35-052-4_32635"]  # doctest: +SKIP
    """
    longest_first = sorted(frame_sheets(gdf_bounds), key=len, reverse=True)
    return np.array(
        [_sheet_of_tile_name(str(t), longest_first) for t in gdf_bounds["tile_name"]],
        dtype=object,
    )


def _origin_sheets(
    names: list[str],
    frame_longest_first: list[str],
    excluded_longest_first: list[str],
) -> tuple[set[str], set[str], bool]:
    """The frame sheets, and the excluded catalogue sheets, a row's origins name.

    Each name is read once: a name on a frame sheet is that sheet's (the
    attribution rule, unchanged), and only a name on NO frame sheet is looked
    up among the catalogue sheets the frame leaves out, so a name can never
    count as both inside and outside the frame. A name on neither is in a
    tile vocabulary the catalogue does not know.

    Args:
        names: The row's recorded origin tile names.
        frame_longest_first: The frame's sheets, longest first.
        excluded_longest_first: The catalogue sheets the frame leaves out,
            longest first (:func:`_excluded_catalogue_longest_first`).

    Returns:
        ``(in_frame, excluded, unknown)``: the frame sheets named, the
        excluded catalogue sheets named (either may be empty), and whether
        any name lies on neither.
    """
    in_frame: set[str] = set()
    excluded: set[str] = set()
    unknown = False
    for name in names:
        sheet = _sheet_of_tile_name(name, frame_longest_first)
        if sheet is not None:
            in_frame.add(sheet)
            continue
        other = _sheet_of_tile_name(name, excluded_longest_first)
        if other is not None:
            excluded.add(other)
        else:
            unknown = True
    return in_frame, excluded, unknown


def _excluded_catalogue_longest_first(
    sheet_catalogue: Iterable[str] | None,
    frame_set: set[str],
) -> list[str]:
    """The catalogue sheets a frame leaves out, longest first.

    Args:
        sheet_catalogue: The parent catalogue; :data:`STUDY_SHEETS` when
            ``None``.
        frame_set: The frame's sheets.

    Returns:
        Catalogue sheets not in the frame, longest first (ties by name, so
        the order is deterministic).
    """
    catalogue = STUDY_SHEETS if sheet_catalogue is None else frozenset(sheet_catalogue)
    return sorted(catalogue - frame_set, key=lambda s: (-len(s), s))


# ── Reduced frames: the parent frame governs (the D50 review, finding 2) ──
#
# A REDUCED frame is part of a larger, parent, frame: one sheet of a
# multi-sheet evaluation, or any subset of its sheets. Attribution reads
# the frame's own sheets, so before 2026-10-10 a reduced frame could score
# a detection that the parent scores on another sheet, and per-sheet
# results stopped summing to the parent's (Astra's review, 2026-10-09).
# The contract since then (PI decision, 2026-10-10): **a detection counts in
# a reduced frame if and only if the parent frame attributes it to a sheet
# inside the reduced frame.** Three rules carry it out, in the detection
# scope and the primary-tile materialiser alike:
#
# 1. **Out-of-frame origin** (PI decision, 2026-10-10). A row whose
#    recorded origins name no sheet of the frame but at least one study
#    sheet the frame leaves out (``n_origin_excluded``) was seen only on
#    sheets outside the frame. It is excluded and counted; it no longer
#    falls back to ``source_tile``. Any parent frame either attributes it to
#    one of those sheets, outside this frame, or excludes it by this same
#    rule, so the exclusion is the parent's verdict. An origin in a tile
#    vocabulary the catalogue does not know keeps the ``source_tile``
#    fallback, but the scorer now warns about it (rule 3).
# 2. **Origins on both sides of the frame's edge.** A row seen on a frame
#    sheet AND on a study sheet the frame leaves out is attributed in the
#    parent by geometry: whichever origin sheet's tiles hold the point. The
#    reduced frame does not hold the left-out sheet's tiles, so it cannot
#    reproduce that choice, and it refuses (:class:`ReducedFrameRefusalError`)
#    rather than guess. Pass ``parent_bounds``, the full evaluation frame:
#    attribution is then computed on the parent and restricted to this
#    frame's sheets, which reproduces the parent's choice exactly.
# 3. **Warn where the catalogue cannot see.** An origin name on no sheet of
#    the frame and no catalogue sheet might still name a sheet of some
#    larger frame the catalogue does not list. That path cannot be ruled
#    out, so the scope and the materialiser log a WARNING when it occurs.
#
# On a full frame the three rules move nothing that has been measured: the
# read-only measurement of 2026-10-09 over all 2,751 committed full-frame
# cells (PR #33) found ``n_origin_unrecognised``, ``n_origin_excluded`` and
# ``n_origin_partly_excluded`` 0 in every cell.


class ReducedFrameRefusalError(ValueError):
    """A frame narrower than its detection set cannot attribute some detections.

    A detection seen on a sheet of the frame AND on a study sheet the frame
    leaves out (a cluster across the frame's edge) is scored, in the full
    frame, on whichever of its origin sheets holds it. Which one depends on
    the left-out sheet's tile geometry, which the reduced frame does not
    hold, so the scope and the materialiser refuse rather than guess, and
    name the argument that resolves it: ``parent_bounds``. A
    :class:`ValueError` subclass, like :class:`TileJoinRefusalError`.

    Attributes:
        n_rows: Rows refused.
        positions: Up to ten of their row positions.
        sheets_left_out: The left-out study sheets they were seen on.
        within_parent: ``True`` when a parent frame was given: the parent
            itself then leaves those sheets out.
    """

    def __init__(
        self,
        message: str,
        *,
        n_rows: int,
        positions: list[int],
        sheets_left_out: list[str],
        within_parent: bool,
    ) -> None:
        super().__init__(message)
        self.n_rows = n_rows
        self.positions = positions
        self.sheets_left_out = sheets_left_out
        self.within_parent = within_parent


def _refuse_partly_excluded(
    partly: np.ndarray,
    sheets_left_out: set[str],
    *,
    what: str,
    within_parent: bool,
) -> None:
    """Raise :class:`ReducedFrameRefusalError` if any row crosses the frame's edge.

    Args:
        partly: Per row, whether its origins name a frame sheet AND a study
            sheet the frame leaves out.
        sheets_left_out: The left-out sheets those rows name.
        what: The caller, for the message (``"detection scope"`` or
            ``"primary-tile assignment"``).
        within_parent: Whether the frame checked is a given parent frame.

    Raises:
        ReducedFrameRefusalError: If ``partly`` has any true entry.
    """
    if not partly.any():
        return
    positions = [int(p) for p in np.flatnonzero(partly)]
    left_out = sorted(sheets_left_out)
    if within_parent:
        remedy = (
            "The parent frame itself leaves out a study sheet these "
            "detections were seen on: pass the FULL evaluation frame as "
            "parent_bounds="
        )
    else:
        remedy = (
            "This frame is narrower than the detection set. Pass the full "
            "evaluation frame as parent_bounds= (attribution is then "
            "computed on it and restricted to this frame's sheets), or "
            "score the full frame once and read its partitions "
            "(DetectionScope.on_sheet, per_sheet_confusion)"
        )
    raise ReducedFrameRefusalError(
        f"{what}: {len(positions)} detection(s) (row positions "
        f"{positions[:10]}) were seen both on a sheet of this frame and on "
        f"study sheet(s) {left_out[:10]} that it leaves out. Which sheet "
        f"scores them depends on tile geometry this frame does not hold, "
        f"so they are refused rather than guessed. {remedy}.",
        n_rows=len(positions),
        positions=positions[:10],
        sheets_left_out=left_out,
        within_parent=within_parent,
    )


def _warn_unknown_origins(n_unknown: int, n_rows: int, what: str) -> None:
    """Warn that some origins name no frame sheet and no catalogue sheet (rule 3).

    Args:
        n_unknown: Rows with at least one such origin name.
        n_rows: Rows in the input.
        what: The caller, for the message.
    """
    if not n_unknown:
        return
    logger.warning(
        "%s: %d of %d detections record an origin tile on neither a sheet "
        "of this frame nor a sheet of the catalogue. If this frame is part "
        "of a larger frame that holds such a sheet, a detection may count "
        "here although that frame attributes it elsewhere; pass "
        "parent_bounds= (the full frame) or a sheet_catalogue= that names "
        "the sheet.",
        what, n_unknown, n_rows,
    )


def _check_within_parent(
    gdf_bounds: gpd.GeoDataFrame,
    parent_bounds: gpd.GeoDataFrame,
) -> None:
    """Refuse a parent frame that the frame is not a part of.

    The frame's tiles must be tiles of the parent: the same names, the
    same polygons and the same sheets. Only then is the parent's
    attribution, restricted to the frame, the parent's verdict.

    Args:
        gdf_bounds: The reduced frame's tile polygons.
        parent_bounds: The parent frame's tile polygons.

    Raises:
        ValueError: If the coordinate reference systems differ, a parent
            tile name repeats, a frame tile is not a parent tile, a
            same-named tile has another polygon, or the two frames put a
            tile on different sheets.
    """
    if gdf_bounds.crs != parent_bounds.crs:
        raise ValueError(
            f"parent_bounds: coordinate reference system {parent_bounds.crs} "
            f"differs from the frame's {gdf_bounds.crs}"
        )
    parent_names = parent_bounds["tile_name"].astype(str)
    if parent_names.duplicated().any():
        repeated = sorted(set(parent_names[parent_names.duplicated()]))
        raise ValueError(
            f"parent_bounds: tile names repeat ({repeated[:5]}), so the "
            f"frame's tiles cannot be identified in it"
        )
    position = pd.Series(np.arange(len(parent_bounds)), index=parent_names.to_numpy())
    names = gdf_bounds["tile_name"].astype(str)
    missing = sorted(set(names) - set(position.index))
    if missing:
        raise ValueError(
            f"parent_bounds: {len(missing)} of the frame's tiles are not "
            f"tiles of the parent frame (e.g. {missing[:5]}); a reduced "
            f"frame must be a subset of its parent's tiles"
        )
    pos = position.loc[names.to_numpy()].to_numpy()
    parent_geoms = gpd.GeoSeries(
        parent_bounds.geometry.iloc[pos].to_numpy(), crs=parent_bounds.crs,
    )
    same = gpd.GeoSeries(
        gdf_bounds.geometry.to_numpy(), crs=gdf_bounds.crs,
    ).geom_equals(parent_geoms)
    if not bool(same.all()):
        differ = sorted(set(names[~same.to_numpy()]))
        raise ValueError(
            f"parent_bounds: {len(differ)} same-named tiles have different "
            f"polygons in the parent frame (e.g. {differ[:5]})"
        )
    own = list(frame_tile_sheets(gdf_bounds))
    parents = list(frame_tile_sheets(parent_bounds)[pos])
    if own != parents:
        differ = sorted({n for n, a, b in zip(names, own, parents) if a != b})
        raise ValueError(
            f"parent_bounds: the parent frame puts {len(differ)} of the "
            f"frame's tiles on another sheet (e.g. {differ[:5]})"
        )


def _frame_hits(
    gdf_det: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> tuple[list[set[str]], np.ndarray]:
    """Which frame sheets' tiles each detection intersects, by one spatial join.

    The join is keyed by POSITION, so a non-unique input index cannot
    conflate rows. A tile belongs to the sheet :func:`frame_tile_sheets`
    gives it — the assignment the per-sheet loop
    (:func:`iter_sheet_scopes`) selects each sheet's tiles by, so both
    sides share one geometric support.

    Args:
        gdf_det: Detections in the frame's coordinate reference system.
        gdf_bounds: Frame tile polygons with a ``tile_name`` column.

    Returns:
        ``(hits, in_union)``: per row, the set of frame sheets whose tiles
        it intersects, and whether it intersects any frame tile at all.
    """
    n = len(gdf_det)
    tile_sheet = dict(zip(
        (str(t) for t in gdf_bounds["tile_name"]), frame_tile_sheets(gdf_bounds),
    ))
    points = gpd.GeoDataFrame(
        geometry=gdf_det.geometry.to_numpy(), crs=gdf_det.crs,
    )
    joined = gpd.sjoin(
        points, gdf_bounds[["tile_name", "geometry"]],
        how="inner", predicate="intersects",
    )
    hits: list[set[str]] = [set() for _ in range(n)]
    in_union = np.zeros(n, dtype=bool)
    for pos, tile_name in zip(joined.index.to_numpy(), joined["tile_name"]):
        in_union[pos] = True
        sheet = tile_sheet.get(str(tile_name))
        if sheet is not None:
            hits[pos].add(sheet)
    return hits, in_union


#: Per-row attribution flags that :func:`scope_detections_to_frame` sums.
_ROW_FLAGS: tuple[str, ...] = (
    "n_origin_restored", "n_origin_switched", "n_origin_only",
    "n_origin_unrecognised",
)


@dataclass(frozen=True)
class _RowAttribution:
    """Each detection's attribution on one frame, before any restriction.

    Attributes:
        sheet: The frame sheet each row is scored on, or ``None`` (no frame
            sheet, or excluded by the out-of-frame-origin rule).
        origin_frame: The frame sheets each row's origins name.
        hits: The frame sheets whose tiles each row intersects.
        in_union: Whether each row intersects any frame tile.
        excluded: Rows excluded by the out-of-frame-origin rule.
        partly: Rows seen on a frame sheet and on a left-out study sheet.
        unknown: Rows with an origin name on no frame or catalogue sheet.
        flags: The :data:`_ROW_FLAGS`, per row.
        sheets_left_out: The left-out study sheets the ``excluded`` and
            ``partly`` rows name.
    """

    sheet: list[str | None]
    origin_frame: list[set[str]]
    hits: list[set[str]]
    in_union: np.ndarray
    excluded: np.ndarray
    partly: np.ndarray
    unknown: np.ndarray
    flags: dict[str, np.ndarray]
    sheets_left_out: set[str]


def _attribute_rows(
    gdf_det: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    origin_columns: list[str],
    has_source_tile: bool,
    sheet_catalogue: Iterable[str] | None,
) -> _RowAttribution:
    """Attribute every detection to one sheet of a frame (ruling D50).

    The rule is documented in :func:`scope_detections_to_frame`; this is its
    per-row core, separated so a reduced frame can read its PARENT frame's
    attribution (``parent_bounds``).

    Args:
        gdf_det: Detections (non-empty).
        gdf_bounds: The frame attribution is computed on.
        origin_columns: The :data:`ORIGIN_TILE_COLUMNS` present.
        has_source_tile: Whether ``source_tile`` is present.
        sheet_catalogue: The parent catalogue; :data:`STUDY_SHEETS` when
            ``None``.

    Returns:
        A :class:`_RowAttribution`.
    """
    n = len(gdf_det)
    sheets = frame_sheets(gdf_bounds)
    frame_set = set(sheets)
    longest_first = sorted(sheets, key=len, reverse=True)
    excluded_longest_first = _excluded_catalogue_longest_first(
        sheet_catalogue, frame_set,
    )
    hits, in_union = _frame_hits(gdf_det, gdf_bounds)
    named = (
        [_sheet_of_tile_name(v, longest_first) for v in gdf_det["source_tile"]]
        if has_source_tile else [None] * n
    )
    origin_values = [(c, gdf_det[c].tolist()) for c in origin_columns]

    attributed: list[str | None] = [None] * n
    origin_frames: list[set[str]] = []
    excluded = np.zeros(n, dtype=bool)
    partly = np.zeros(n, dtype=bool)
    unknown = np.zeros(n, dtype=bool)
    flags = {key: np.zeros(n, dtype=bool) for key in _ROW_FLAGS}
    sheets_left_out: set[str] = set()
    for pos in range(n):
        source_sheet = named[pos]
        origin_names: list[str] = []
        for column, values in origin_values:
            origin_names = _parse_origin_cell(values[pos], column, pos)
            if origin_names:
                break
        # The sheets the detection was SEEN on. A consensus cluster lists
        # every member's tile, and near a sheet edge, where padded tiles
        # overlap, they can lie on two sheets; the detection was then seen on
        # both, and an attribution to either is not a re-key. Only an
        # attribution to a sheet it was never seen on is (h13's and tier E's
        # re-keyed rows were all seen on one sheet and keyed to the other).
        # No member is privileged: ``merge_passes.py`` sorts ``source_tiles``,
        # so its first entry is alphabetical, not first-seen. (Measured, the
        # two rules differ on few cells; the choice rests on that principle —
        # reports/scorer-frames-d50-d51-2026-10-08.md § 7.)
        # ``origin_excluded``: catalogue sheets it was seen on that this
        # frame leaves out (rules 1 and 2 above).
        origin_frame, origin_excluded, has_unknown = _origin_sheets(
            origin_names, longest_first, excluded_longest_first,
        )
        origin_frames.append(origin_frame)
        unknown[pos] = has_unknown
        sheet: str | None
        if origin_frame:
            if origin_excluded:
                # Rule 2: seen across the frame's edge. The caller refuses.
                partly[pos] = True
                sheets_left_out |= origin_excluded
            holding = sorted(origin_frame & hits[pos])
            if source_sheet is not None and source_sheet in origin_frame:
                if source_sheet in hits[pos] or not holding:
                    sheet = source_sheet
                else:
                    # Seen on two sheets, named on the one whose frame tiles
                    # do not hold it: the materialisers write the first,
                    # alphabetical, member into ``source_tile``. Scored on
                    # the origin sheet whose tiles do hold it (sorted first
                    # on a tie), as a re-keyed row is.
                    sheet = holding[0]
                    flags["n_origin_switched"][pos] = True
            else:
                sheet = holding[0] if holding else sorted(origin_frame)[0]
                if source_sheet is not None:
                    flags["n_origin_restored"][pos] = True
                else:
                    flags["n_origin_only"][pos] = True
        else:
            # No recorded origin, or one naming no frame sheet.
            sheet = source_sheet
            if origin_names:
                flags["n_origin_unrecognised"][pos] = True
                if origin_excluded:
                    # Rule 1: seen only off this frame, on a study sheet it
                    # leaves out. Excluded, never re-keyed by source_tile.
                    excluded[pos] = True
                    sheets_left_out |= origin_excluded
                    sheet = None
            # Otherwise ``source_tile`` decides as it always has: no origin
            # at all, or one in a tile vocabulary the study never used.
        attributed[pos] = sheet if sheet in frame_set else None
    return _RowAttribution(
        sheet=attributed, origin_frame=origin_frames, hits=hits,
        in_union=in_union, excluded=excluded, partly=partly, unknown=unknown,
        flags=flags, sheets_left_out=sheets_left_out,
    )


@dataclass(frozen=True)
class DetectionScope:
    """Detections scoped to a frame under ruling D50, with the counts that show it.

    Attributes:
        detections: The in-scope detections the per-sheet matchers score —
            the input's own rows, original index and original order, each
            attributed to a frame sheet and inside one of its tiles.
        sheets: The sheet each in-scope detection is scored on (its origin
            sheet), aligned row for row with ``detections``.
        diagnostics: The counts written into ``evaluation.json`` as
            ``detection_scope`` (see :func:`scope_detections_to_frame`).
        retained: The input minus EXACTLY the rows the rule removes (those
            attributed to a frame sheet but outside its tiles); rows on no
            frame sheet are kept, including those excluded by the
            out-of-frame-origin rule. Given a parent frame, the rows the
            parent removes as out of its frame are removed as well. This is
            what the tile confusion books: it never needed a sheet, and the
            ruling changes it only by the out-of-frame rows.
    """

    detections: gpd.GeoDataFrame
    sheets: np.ndarray
    diagnostics: dict[str, Any] = field(default_factory=dict)
    retained: gpd.GeoDataFrame | None = None

    def on_sheet(self, sheet: str) -> gpd.GeoDataFrame:
        """Return the in-scope detections attributed to one sheet.

        Args:
            sheet: A frame sheet name.

        Returns:
            Those rows of :attr:`detections`, in their original order.
        """
        if len(self.detections) == 0:
            return self.detections
        return self.detections[self.sheets == sheet]


def _empty_scope_diagnostics(n_detections: int) -> dict[str, Any]:
    """The diagnostics block with every count at zero."""
    return {
        "rule": DETECTION_SCOPE_RULE,
        "applied": True,
        "n_detections": n_detections,
        "n_in_scope": 0,
        "n_out_of_frame": 0,
        "n_out_of_frame_cross_sheet": 0,
        "n_origin_restored": 0,
        "n_origin_switched": 0,
        "n_origin_only": 0,
        "n_origin_unrecognised": 0,
        "n_origin_excluded": 0,
        "n_origin_partly_excluded": 0,
        "n_unattributed": 0,
        "n_unattributed_in_frame": 0,
        "origin_columns": [],
        "ruling": DETECTION_SCOPE_RULING,
    }


def scope_detections_to_frame(
    gdf_det: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    *,
    require_attribution: bool = True,
    sheet_catalogue: Iterable[str] | None = None,
    parent_bounds: gpd.GeoDataFrame | None = None,
) -> DetectionScope:
    """Scope detections to a frame per sheet by tile geometry (ruling D50).

    **Attribution.** Each detection is put on ONE sheet, its origin sheet:

    * when the row records the proposer's own tile(s) in one of
      :data:`ORIGIN_TILE_COLUMNS` (the first column with a parseable value
      wins), its origin sheets are the frame sheets those tiles lie on — the
      sheets it was SEEN on. If ``source_tile``'s sheet is one of them,
      ``source_tile`` stands: nothing was re-keyed — unless the point lies
      outside that sheet's frame tiles and inside another origin sheet's,
      when it is scored on that sheet (sorted first on a tie) and counted
      in ``n_origin_switched``. The materialisers write the first,
      alphabetical, member into ``source_tile``, so for a cluster seen on
      two sheets that sheet is an accident of naming. A row whose
      ``source_tile`` names a sheet it was never seen on was re-keyed across
      a sheet edge; it is scored on an origin sheet instead (the one whose
      tiles hold the point, sorted first on a tie) and counted in
      ``n_origin_restored``. No single member tile is privileged:
      ``merge_passes.py`` stores ``source_tiles`` SORTED, so its first entry
      is the alphabetically first member, not the first seen, and choosing
      it would re-attribute a cluster seen on two sheets arbitrarily;
    * when the recorded origins name no frame sheet but at least one sheet
      of ``sheet_catalogue`` that the frame leaves out, the detection was
      seen only off this frame: it is excluded, not scored, and counted in
      ``n_origin_excluded`` (the out-of-frame-origin rule, PI decision
      2026-10-10). It never falls back to ``source_tile``;
    * otherwise the sheet ``source_tile`` names by the scorers' prefix rule
      (:func:`_sheet_of_tile_name`) — no recorded origin, or one in a tile
      vocabulary the catalogue does not know.

    A row on no frame sheet (null or empty ``source_tile`` and no origin
    naming a frame sheet, or a foreign sheet's name) is *unattributed*: it
    is not scored, exactly as before the ruling, and counted.

    **Reduced frames.** A frame that is part of a larger, parent, frame
    (one sheet of a multi-sheet evaluation) must count a detection if and
    only if the parent attributes it to one of this frame's sheets, so that
    per-sheet results sum to the parent's (the D50 review, finding 2;
    PI decision 2026-10-10). A detection seen only on sheets the frame
    leaves out is excluded (above). A detection seen on a sheet of the
    frame AND on a catalogue sheet the frame leaves out is attributed in the
    parent by tile geometry the reduced frame does not hold, so without
    ``parent_bounds`` this raises :class:`ReducedFrameRefusalError` rather
    than guess. With ``parent_bounds`` the attribution is computed on the
    parent frame and restricted to this frame: a row the parent scores on
    another sheet is excluded here (``n_parent_elsewhere``), and a row it
    scores on one of this frame's sheets is kept when it intersects that
    sheet's tiles here. An origin naming neither a frame sheet nor a
    catalogue sheet is logged as a WARNING: the catalogue cannot tell
    whether it names a sheet of some larger frame. The simplest per-sheet
    report needs none of this: scope the FULL frame once and read its
    partitions (:meth:`DetectionScope.on_sheet`, :func:`per_sheet_confusion`).

    **Scope.** An attributed detection is kept only if it intersects one of
    its own sheet's frame tiles — the reference side's rule
    (:func:`scope_references_to_tiles`: per-tile spatial join,
    ``intersects``). One spatial join against every frame tile decides
    membership for all sheets at once; it is the same predicate on the same
    polygons, so the result is the per-sheet rule's.

    Args:
        gdf_det: Detections in the frame's coordinate reference system,
            carrying ``source_tile`` and/or an origin column.
        gdf_bounds: Frame tile polygons with a ``tile_name`` column.
        require_attribution: When ``True`` (the F1 and per-tile scorers), a
            non-empty detection set with neither ``source_tile`` nor any
            origin column raises, as the scorers always have. When ``False``
            (the tile confusion, which can book detections by geometry
            alone), such a set is returned unscoped with ``applied`` false.
        sheet_catalogue: The parent sheet catalogue an origin naming no
            frame sheet is identified against; :data:`STUDY_SHEETS` when
            ``None``. It separates an origin on a real sheet the frame
            leaves out (excluded, or refused when the row was also seen on
            a frame sheet) from a tile vocabulary the study never used
            (``source_tile`` fallback, with a warning).
        parent_bounds: The full frame this frame is part of, or ``None``.
            Its tiles must include every tile of ``gdf_bounds``, with the
            same polygons and sheets (checked). Attribution is then the
            parent's, restricted to this frame. A full frame needs none.

    Returns:
        A :class:`DetectionScope`. Its ``diagnostics`` hold:

        ``rule`` / ``ruling`` / ``applied``
            The rule, its source, and whether it could be applied.
        ``n_detections``
            Rows in the input. They split into ``n_in_scope``,
            ``n_out_of_frame``, ``n_unattributed``, ``n_origin_excluded``
            and, with a parent frame, ``n_parent_elsewhere``.
        ``n_in_scope``
            Rows kept: attributed and inside their own sheet's tiles.
        ``n_out_of_frame``
            Attributed rows outside every tile of their own sheet — removed.
            Before D50 these were false positives (or, if re-keyed to null,
            silently dropped).
        ``n_out_of_frame_cross_sheet``
            Of those, rows lying inside ANOTHER frame sheet's tiles: the
            per-sheet rule removes them where a union-geometry clip would
            not.
        ``n_origin_restored``
            Rows whose ``source_tile`` named a different frame sheet from
            their recorded origin, scored on the origin instead.
        ``n_origin_switched``
            Rows whose ``source_tile`` named an origin sheet whose frame
            tiles do not hold them, scored on another origin sheet whose
            tiles do. Before the switch these were out of frame.
        ``n_origin_only``
            Rows with a null ``source_tile`` attributed from their origin.
        ``n_origin_unrecognised``
            Rows whose recorded origin names no frame sheet. Those in
            ``n_origin_excluded`` are excluded; the remaining
            ``n_origin_unrecognised - n_origin_excluded`` rows name a tile
            vocabulary the catalogue does not know and are attributed by
            ``source_tile`` as before the ruling (a naming-convention
            difference is likelier than a detection from another sheet set).
        ``n_origin_excluded``
            Of those, rows whose origin names a catalogue sheet the frame
            leaves out: seen only off this frame, so excluded and not
            scored (before 2026-10-10 they fell back to ``source_tile`` and
            could be scored on a sheet they were never seen on). Nonzero
            means the frame is narrower than the detection set.
        ``n_origin_partly_excluded``
            Without a parent frame, always 0: such a row is refused. With
            one, rows scored on this frame's sheets (the parent decided)
            that were also seen on a sheet this frame leaves out.
        ``n_unattributed``
            Rows on no frame sheet, not scored.
        ``n_unattributed_in_frame``
            Of those, rows geometrically inside the frame's tile union —
            nonzero means detections inside the frame are not being scored,
            which a reader should see.
        ``origin_columns``
            The origin columns present in the input.
        ``n_parent_sheets``, ``n_parent_elsewhere``
            Only with ``parent_bounds``: the parent frame's sheet count,
            and the rows it attributes to one of its sheets outside this
            frame (excluded here).

    Raises:
        KeyError: If ``require_attribution`` and the set carries neither
            ``source_tile`` nor any origin column.
        ReducedFrameRefusalError: If a row was seen on a frame sheet and on
            a catalogue sheet the frame (or, with ``parent_bounds``, the
            parent frame) leaves out.
        ValueError: If ``parent_bounds`` is given but the frame is not part
            of it (see :func:`_check_within_parent`).

    Example:
        >>> scope = scope_detections_to_frame(dets, bounds)  # doctest: +SKIP
        >>> scope.diagnostics["n_out_of_frame"]  # doctest: +SKIP
        27
        >>> one = bounds[frame_tile_sheets(bounds) == "A"]  # doctest: +SKIP
        >>> scope_detections_to_frame(  # doctest: +SKIP
        ...     dets, one, parent_bounds=bounds).diagnostics["n_parent_elsewhere"]
        3
    """
    if parent_bounds is not None:
        # Checked first, so a misused parent fails even on an empty set.
        _check_within_parent(gdf_bounds, parent_bounds)
    n = len(gdf_det)
    diag = _empty_scope_diagnostics(n)
    if parent_bounds is not None:
        diag["n_parent_sheets"] = len(frame_sheets(parent_bounds))
        diag["n_parent_elsewhere"] = 0
    if n == 0:
        return DetectionScope(gdf_det, np.array([], dtype=object), diag, gdf_det)

    origin_columns = [c for c in ORIGIN_TILE_COLUMNS if c in gdf_det.columns]
    diag["origin_columns"] = origin_columns
    has_source_tile = "source_tile" in gdf_det.columns
    if not has_source_tile and not origin_columns:
        if require_attribution:
            raise KeyError(
                "source_tile: detections carry neither a 'source_tile' "
                f"column nor any origin column {ORIGIN_TILE_COLUMNS}, so no "
                "detection can be attributed to a map sheet. Assign "
                "source_tile first (evaluate_detections.py does so by a "
                "spatial join)."
            )
        diag["applied"] = False
        diag["n_in_scope"] = n
        diag["not_applied_reason"] = (
            "detections carry no source_tile or origin column"
        )
        return DetectionScope(
            gdf_det, np.full(n, None, dtype=object), diag, gdf_det,
        )

    # Attribution: on this frame, or — for a reduced frame given its
    # parent — on the parent, whose verdict this frame then restricts.
    within_parent = parent_bounds is not None
    att = _attribute_rows(
        gdf_det, parent_bounds if within_parent else gdf_bounds,
        origin_columns, has_source_tile, sheet_catalogue,
    )
    _refuse_partly_excluded(
        att.partly, att.sheets_left_out,
        what="detection scope", within_parent=within_parent,
    )
    # Membership is always decided on THIS frame's tiles.
    if within_parent:
        hits, in_union = _frame_hits(gdf_det, gdf_bounds)
    else:
        hits, in_union = att.hits, att.in_union
    frame_set = set(frame_sheets(gdf_bounds))

    attributed: list[str | None] = [None] * n
    keep = np.zeros(n, dtype=bool)
    out_of_frame = np.zeros(n, dtype=bool)
    # Rows the parent attributes elsewhere AND removes as out of its frame:
    # the parent's tile confusion never books them, so neither does this one.
    removed_by_parent = np.zeros(n, dtype=bool)
    counts = {
        "n_out_of_frame": 0, "n_out_of_frame_cross_sheet": 0,
        "n_origin_restored": 0, "n_origin_switched": 0, "n_origin_only": 0,
        "n_origin_unrecognised": 0, "n_origin_excluded": 0,
        "n_origin_partly_excluded": 0,
        "n_unattributed": 0, "n_unattributed_in_frame": 0,
    }
    n_elsewhere = 0
    n_unknown = 0
    for pos in range(n):
        sheet = att.sheet[pos]
        if sheet is not None and sheet not in frame_set:
            # Only with a parent: it scores this row on another sheet.
            n_elsewhere += 1
            removed_by_parent[pos] = sheet not in att.hits[pos]
            continue
        for key in _ROW_FLAGS:
            if att.flags[key][pos]:
                counts[key] += 1
        n_unknown += bool(att.unknown[pos])
        if att.excluded[pos]:
            # The out-of-frame-origin rule: seen only on sheets this frame
            # (or its parent) leaves out. Not scored, and never re-keyed.
            counts["n_origin_excluded"] += 1
            continue
        if within_parent and sheet is not None and att.origin_frame[pos] - frame_set:
            counts["n_origin_partly_excluded"] += 1
        if sheet is None:
            counts["n_unattributed"] += 1
            if in_union[pos]:
                counts["n_unattributed_in_frame"] += 1
            continue
        attributed[pos] = sheet
        if sheet in hits[pos]:
            keep[pos] = True
        else:
            out_of_frame[pos] = True
            counts["n_out_of_frame"] += 1
            if hits[pos]:
                counts["n_out_of_frame_cross_sheet"] += 1

    _warn_unknown_origins(n_unknown, n, "detection scope")
    diag.update(counts)
    if within_parent:
        diag["n_parent_elsewhere"] = n_elsewhere
    diag["n_in_scope"] = int(keep.sum())
    kept_sheets = np.array(
        [attributed[pos] for pos in range(n) if keep[pos]], dtype=object,
    )
    return DetectionScope(
        gdf_det.iloc[np.flatnonzero(keep)], kept_sheets, diag,
        gdf_det.iloc[np.flatnonzero(~(out_of_frame | removed_by_parent))],
    )


def reference_map_column(gdf_ref: gpd.GeoDataFrame) -> str:
    """Name the column that records each reference's map sheet.

    The gold standard (``mounds-reference.geojson``) uses ``Map``; the
    55-map student ground truth uses ``source_map``. Supporting both keeps
    the scorers generic across datasets.

    Args:
        gdf_ref: Reference GeoDataFrame.

    Returns:
        ``"Map"`` or ``"source_map"``.

    Raises:
        ValueError: If neither column is present.
    """
    if "Map" in gdf_ref.columns:
        return "Map"
    if "source_map" in gdf_ref.columns:
        return "source_map"
    raise ValueError(
        "Reference GeoDataFrame has no 'Map' or 'source_map' column. "
        f"Available columns: {list(gdf_ref.columns)}"
    )


def iter_sheet_scopes(
    gdf_det: gpd.GeoDataFrame | DetectionScope,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    *,
    ref_map_col: str | None = None,
    sheet_catalogue: Iterable[str] | None = None,
    parent_bounds: gpd.GeoDataFrame | None = None,
) -> Iterator[tuple[str, gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]]:
    """Yield each frame sheet's detections and references, scoped by one rule.

    This is the per-sheet loop every matcher in the repository runs —
    :func:`calculate_f1_internal`, :func:`compute_per_tile_tp_fp_fn`, the
    corrected-F1 engine and the analysis scripts that copied it — written
    once, so the detection side and the reference side are scoped the same
    way at every call site (ruling D50). References: the sheet's rows by
    their map column, then :func:`scope_references_to_tiles` on the sheet's
    tiles. Detections: :func:`scope_detections_to_frame`. A sheet's tiles
    are the ones :func:`frame_tile_sheets` assigns to it — the assignment
    the detection scope's spatial join reads — so a reference and a
    detection at the same point are judged against the same polygons even
    where one sheet name is a prefix of another (the D50 review,
    finding 3).

    Args:
        gdf_det: Detections, or a :class:`DetectionScope` already computed
            for this frame (saves the spatial join when the caller needs the
            scoped set as well). A scope computed for a DIFFERENT frame is
            not checked for; pass the scope of this ``gdf_bounds``.
        gdf_ref: References.
        gdf_bounds: Frame tile polygons with a ``tile_name`` column.
        ref_map_col: The references' sheet column; detected by
            :func:`reference_map_column` when ``None``.
        sheet_catalogue: Passed to :func:`scope_detections_to_frame`.
        parent_bounds: Passed to :func:`scope_detections_to_frame`: the
            full frame a reduced ``gdf_bounds`` is part of. The references
            need nothing more: the parent check guarantees each sheet's
            tiles here are the parent's tiles for that sheet, so a frame of
            whole sheets scopes each sheet's references as the parent does.

    Yields:
        ``(sheet, det_scope, ref_scope, sheet_bounds)`` for every frame
        sheet in sorted order, including sheets with nothing on either side
        (callers skip those as they always have).

    Raises:
        ValueError: If ``sheet_catalogue`` or ``parent_bounds`` is passed
            with a precomputed :class:`DetectionScope`, which is already
            attributed (pass them when computing it instead).
        ReducedFrameRefusalError: As :func:`scope_detections_to_frame`.
    """
    if ref_map_col is None:
        ref_map_col = reference_map_column(gdf_ref)
    if isinstance(gdf_det, DetectionScope):
        if sheet_catalogue is not None or parent_bounds is not None:
            raise ValueError(
                "sheet_catalogue and parent_bounds apply when a detection "
                "scope is computed, and this DetectionScope is already "
                "attributed: pass them to scope_detections_to_frame instead"
            )
        scope = gdf_det
    else:
        scope = scope_detections_to_frame(
            gdf_det, gdf_bounds,
            sheet_catalogue=sheet_catalogue, parent_bounds=parent_bounds,
        )
    tile_sheets = frame_tile_sheets(gdf_bounds)
    for sheet in frame_sheets(gdf_bounds):
        sheet_bounds = gdf_bounds[tile_sheets == sheet]
        ref_scope = gdf_ref[gdf_ref[ref_map_col] == sheet]
        if not ref_scope.empty:
            ref_scope = scope_references_to_tiles(ref_scope, sheet_bounds)
        yield sheet, scope.on_sheet(sheet), ref_scope, sheet_bounds


def origin_tiles_of(gdf_points: gpd.GeoDataFrame) -> list[list[str]]:
    """Each row's recorded proposer tile(s), from the columns that record them.

    The first of :data:`ORIGIN_TILE_COLUMNS` with a parseable value wins, row
    by row; ``source_tile`` is the fallback (before any re-keying it IS the
    proposer's tile).

    Args:
        gdf_points: Detections or candidates.

    Returns:
        One list of tile names per row (empty where nothing is recorded).
    """
    columns = [c for c in ORIGIN_TILE_COLUMNS if c in gdf_points.columns]
    if "source_tile" in gdf_points.columns:
        columns.append("source_tile")
    values = [(c, gdf_points[c].tolist()) for c in columns]
    out: list[list[str]] = []
    for pos in range(len(gdf_points)):
        names: list[str] = []
        for column, column_values in values:
            names = _parse_origin_cell(column_values[pos], column, pos)
            if names:
                break
        out.append(names)
    return out


#: The materialiser's per-point counts, in the order its diagnostics list them.
_PRIMARY_TILE_COUNTS: tuple[str, ...] = (
    "n_assigned", "n_outside_frame", "n_outside_origin_sheet",
    "n_cross_sheet_avoided", "n_no_origin", "n_origin_unrecognised",
    "n_origin_excluded", "n_origin_partly_excluded",
)


def _primary_tile_rows(
    gdf_points: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    origin: list[list[str]],
    sheet_catalogue: Iterable[str] | None,
) -> tuple[list[str | None], list[tuple[str, ...]], list[set[str]],
           np.ndarray, np.ndarray, set[str]]:
    """The per-point core of :func:`assign_primary_tiles_on_origin_sheet`.

    Separated so a reduced frame can follow its PARENT frame's assignment.

    Args:
        gdf_points: Points (non-empty) in the frame's coordinate reference
            system.
        gdf_bounds: The frame the assignment is computed on.
        origin: Per-row origin tile names.
        sheet_catalogue: The parent catalogue; :data:`STUDY_SHEETS` when
            ``None``.

    Returns:
        ``(assigned, counted, origin_sheets, partly, unknown,
        sheets_left_out)``: per point, its tile (or ``None``), the
        :data:`_PRIMARY_TILE_COUNTS` keys it adds one to, and the frame
        sheets its origins name; per point, whether it was seen on a frame
        sheet and on a left-out study sheet, and whether an origin name lies
        on no frame or catalogue sheet; and the left-out sheets named.
    """
    n = len(gdf_points)
    sheets = frame_sheets(gdf_bounds)
    longest_first = sorted(sheets, key=len, reverse=True)
    excluded_longest_first = _excluded_catalogue_longest_first(
        sheet_catalogue, set(sheets),
    )
    # The canonical tile-to-sheet assignment (frame_tile_sheets), the one
    # the scorer's detection scope and per-sheet loop read.
    tile_sheet = dict(zip(
        (str(t) for t in gdf_bounds["tile_name"]), frame_tile_sheets(gdf_bounds),
    ))

    points = gpd.GeoDataFrame(
        geometry=gdf_points.geometry.to_numpy(), crs=gdf_points.crs,
    )
    joined = gpd.sjoin(
        points, gdf_bounds[["tile_name", "geometry"]],
        how="inner", predicate="intersects",
    )
    centroids = {
        row["tile_name"]: row.geometry.centroid
        for _, row in gdf_bounds.iterrows()
    }
    candidates: list[list[str]] = [[] for _ in range(n)]
    for pos, tile_name in zip(joined.index.to_numpy(), joined["tile_name"]):
        candidates[pos].append(tile_name)

    geometries = list(points.geometry)
    assigned: list[str | None] = []
    counted: list[tuple[str, ...]] = []
    origin_sheet_sets: list[set[str]] = []
    partly = np.zeros(n, dtype=bool)
    unknown = np.zeros(n, dtype=bool)
    sheets_left_out: set[str] = set()
    for pos in range(n):
        # The sheets the point was seen on, the same set
        # scope_detections_to_frame attributes by, so a freshly written
        # source_tile is never re-attributed at scoring time; and the
        # catalogue sheets it was seen on that the frame leaves out.
        origin_sheets, origin_excluded, has_unknown = _origin_sheets(
            origin[pos], longest_first, excluded_longest_first,
        )
        origin_sheet_sets.append(origin_sheets)
        unknown[pos] = has_unknown
        if origin_sheets and origin_excluded:
            # Rule 2: seen across the frame's edge. The caller refuses.
            partly[pos] = True
            sheets_left_out |= origin_excluded
        names = candidates[pos]
        if not names:
            counted.append(("n_outside_frame",))
            assigned.append(None)
            continue
        geom = geometries[pos]

        def nearest(pool: list[str], point: Any = geom) -> str:
            """Nearest tile centroid; first in join order on a tie."""
            return pool[0] if len(pool) == 1 else min(
                pool, key=lambda t: point.distance(centroids[t]),
            )

        legacy = nearest(names)
        if not origin_sheets:
            if origin[pos] and origin_excluded:
                # Rule 1: seen only on study sheets the frame leaves out.
                # No tile here: never re-keyed onto a sheet it was not
                # seen on.
                sheets_left_out |= origin_excluded
                counted.append(("n_no_origin", "n_origin_unrecognised",
                                "n_origin_excluded"))
                assigned.append(None)
                continue
            keys: tuple[str, ...] = ("n_no_origin", "n_assigned")
            if origin[pos]:
                keys += ("n_origin_unrecognised",)
            counted.append(keys)
            assigned.append(legacy)
            continue
        own = [t for t in names if tile_sheet.get(str(t)) in origin_sheets]
        if not own:
            counted.append(("n_outside_origin_sheet",))
            assigned.append(None)
            continue
        choice = nearest(own)
        keys = ("n_assigned",)
        if tile_sheet.get(str(legacy)) not in origin_sheets:
            keys += ("n_cross_sheet_avoided",)
        counted.append(keys)
        assigned.append(choice)
    return assigned, counted, origin_sheet_sets, partly, unknown, sheets_left_out


def assign_primary_tiles_on_origin_sheet(
    gdf_points: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    origin: list[list[str]] | None = None,
    *,
    sheet_catalogue: Iterable[str] | None = None,
    parent_bounds: gpd.GeoDataFrame | None = None,
) -> tuple[list[str | None], dict[str, int]]:
    """Give each point one frame tile — never one on another sheet (ruling D50).

    The materialisers that write ``source_tile`` for a frame (h13's
    ``prepare_h13_scoring.assign_primary_tiles``, tier E's
    ``reassign_carrier_tiles``, the grid and image-B unions) take, among the
    frame tiles a point intersects, the one whose centroid is nearest. Where
    two sheets' padded tiles overlap, that tile can belong to the
    NEIGHBOURING sheet, and the per-sheet matcher then scores the detection
    against the wrong sheet's references (``reports/frames-blast-radius-
    2026-10-07.md`` § 5.4: 6 or 7 detections per tier E cell, 16 to 64 per
    h13 three-pass cell).

    This keeps the nearest-centroid rule but restricts the candidates to the
    point's ORIGIN sheets — the frame sheets its recorded tiles lie on, the
    sets :func:`scope_detections_to_frame` attributes by — so a point whose
    origin sheets' tiles it does not
    intersect gets ``None`` (it is outside the frame for its own sheet)
    rather than a neighbour's tile. A point with no recorded origin keeps
    the unrestricted legacy rule — there is nothing to re-key from — and is
    counted, so a caller can see how many attributions were geometric only.

    Ties are broken exactly as the legacy rule broke them (the first tile
    in spatial-join order at the minimum distance), so a point whose
    candidates all lie on one sheet receives the tile it always received.

    **Reduced frames** follow the detection scope's contract (see the
    comment above :class:`ReducedFrameRefusalError`). A point whose origins
    name no frame sheet but a catalogue sheet the frame leaves out gets
    ``None``, never the legacy rule's tile on a sheet it was not seen on
    (``n_origin_excluded``). A point seen on a frame sheet AND on a
    catalogue sheet the frame leaves out raises
    :class:`ReducedFrameRefusalError` unless ``parent_bounds`` is given: the
    parent frame might give it the left-out sheet's tile. With
    ``parent_bounds`` the assignment is the parent's, restricted to this
    frame: a point the parent assigns to a tile outside it gets ``None``
    (``n_parent_elsewhere``). An origin in a tile vocabulary the catalogue
    does not know keeps the legacy rule and is logged as a WARNING.

    Args:
        gdf_points: Points in the frame's coordinate reference system.
        gdf_bounds: Frame tile polygons with a ``tile_name`` column.
        origin: Per-row origin tile names; inferred by
            :func:`origin_tiles_of` when ``None``.
        sheet_catalogue: The parent sheet catalogue an origin naming no
            frame sheet is identified against; :data:`STUDY_SHEETS` when
            ``None``.
        parent_bounds: The full frame this frame is part of, or ``None``
            (checked as :func:`scope_detections_to_frame` checks it).

    Returns:
        ``(tile_names, diagnostics)``: one name (or ``None``) per row in
        ``gdf_points``' order, and the counts ``n_points``, ``n_assigned``,
        ``n_outside_frame`` (no frame tile at all), ``n_outside_origin_sheet``
        (frame tiles, but none on the origin sheet — formerly re-keyed to a
        neighbour), ``n_cross_sheet_avoided`` (the legacy rule would have
        picked another sheet's tile), ``n_no_origin`` (no origin names a
        frame sheet: the legacy rule is used) and, of those,
        ``n_origin_unrecognised`` (an origin is recorded but names no frame
        sheet) and, of those, ``n_origin_excluded`` (it names a catalogue
        sheet the frame leaves out: ``None``, not the legacy rule); and
        ``n_origin_partly_excluded`` (0 without a parent frame, which
        refuses such points; with one, points assigned here that were also
        seen on a sheet this frame leaves out). With ``parent_bounds``,
        also ``n_parent_elsewhere``.

    Raises:
        ReducedFrameRefusalError: As described under "Reduced frames".
        ValueError: If ``parent_bounds`` is given but the frame is not part
            of it.
    """
    if parent_bounds is not None:
        _check_within_parent(gdf_bounds, parent_bounds)
    n = len(gdf_points)
    diag = {"n_points": n, **dict.fromkeys(_PRIMARY_TILE_COUNTS, 0)}
    if parent_bounds is not None:
        diag["n_parent_elsewhere"] = 0
    if n == 0:
        return [], diag
    if origin is None:
        origin = origin_tiles_of(gdf_points)
    within_parent = parent_bounds is not None
    assigned, counted, origin_sheet_sets, partly, unknown, left_out = (
        _primary_tile_rows(
            gdf_points, parent_bounds if within_parent else gdf_bounds,
            origin, sheet_catalogue,
        )
    )
    _refuse_partly_excluded(
        partly, left_out, what="primary-tile assignment",
        within_parent=within_parent,
    )
    _warn_unknown_origins(int(unknown.sum()), n, "primary-tile assignment")
    if not within_parent:
        for keys in counted:
            for key in keys:
                diag[key] += 1
        return assigned, diag

    # Follow the parent: keep its tile where it is one of this frame's.
    frame_tiles = {str(t) for t in gdf_bounds["tile_name"]}
    frame_set = set(frame_sheets(gdf_bounds))
    out: list[str | None] = []
    for tile, keys, seen_on in zip(assigned, counted, origin_sheet_sets):
        if tile is not None and str(tile) not in frame_tiles:
            diag["n_parent_elsewhere"] += 1
            out.append(None)
            continue
        for key in keys:
            diag[key] += 1
        if tile is not None and seen_on - frame_set:
            diag["n_origin_partly_excluded"] += 1
        out.append(tile)
    return out, diag


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
    tile_join: str = TILE_JOIN_DEFAULT,
    *,
    parent_bounds: gpd.GeoDataFrame | None = None,
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

    **This function carries the same name-versus-geometry defect as the
    tile confusion, in the TP and FP arms.** TPs and FPs are booked to
    ``det_row["source_tile"]`` — a string — while FNs are booked to the
    reference's primary tile, computed geometrically. A cell scored on a
    frame whose tile vocabulary is not its proposer's therefore loses
    **every** TP and FP (no name matches a frame tile), leaving a table of
    pure false negatives; the global F1 in the same evaluation is
    unaffected, because it is matched geometrically before any tile is
    consulted. The consumers of this table are the per-tile bootstrap
    confidence intervals and the pairwise permutation tests, so the
    exposure is wider than tile-level Matthews Correlation Coefficient
    (MCC) alone.

    ``tile_join`` names the rule, exactly as in
    :func:`calculate_tile_classification`. Under the geometric rules the
    detection's booked tile is derived from its geometry against *this*
    bounds file, so a vocabulary difference cannot arise; under
    ``geometric-contains`` a detection in an overlap zone is booked to
    every tile containing it, which double-counts TPs and FPs across
    overlapping tiles exactly as the reference-side rule has always
    double-counted references. A shortfall between booked and in-union
    detections raises rather than passing a silently truncated table on.

    Args:
        gdf_det: GeoDataFrame of detections (must have 'source_tile' or an
            origin column; scoped by :func:`scope_detections_to_frame`).
        gdf_ref: GeoDataFrame of ground truth references (must have 'Map').
        gdf_bounds: GeoDataFrame of tile boundaries (must have 'tile_name').
        buffer_metres: Maximum distance for a valid match (default 20 m).
        tile_join: One of :data:`TILE_JOINS`; defaults to
            :data:`TILE_JOIN_DEFAULT`.
        parent_bounds: The frame ``gdf_bounds`` was cut from, or ``None``
            (:func:`scope_detections_to_frame`). The common-footprint
            bootstraps pass a condition's own frame here when the common
            footprint is smaller than it (:func:`_parent_of_cut`).

    Returns:
        DataFrame with columns [tile_name, tp, fp, fn], one row per tile.

    Raises:
        TileJoinRefusalError: If the booked TP + FP count falls short of
            the detections geometrically inside the frame, which means the
            join is not describing this frame. A :class:`ValueError`
            subclass, so pre-existing ``except ValueError`` handling still
            catches it; the subclass carries the reason and the shortfall
            counts as attributes so a caller can publish the quantities a
            refusal leaves standing instead of aborting outright (see
            :func:`describe_tile_join_refusal`).
    """
    tile_counts: dict[str, dict[str, int]] = {
        row["tile_name"]: {"tp": 0, "fp": 0, "fn": 0}
        for _, row in gdf_bounds.iterrows()
    }
    # Ruling D50: scope detections exactly as ``calculate_f1_internal`` does,
    # BEFORE anything is booked, so the per-tile table and the point
    # estimate describe the same detections. Before the ruling an
    # out-of-frame detection still took part in the per-sheet matching here
    # but was booked to no tile (``reports/frames-blast-radius-2026-10-07.md``
    # § 2.1). The matching below reads the attributed in-scope rows
    # (``scope``); the booking diagnostics read every row but the removed
    # out-of-frame ones (``scope.retained``), as they always read every row.
    scope = scope_detections_to_frame(gdf_det, gdf_bounds, parent_bounds=parent_bounds)
    gdf_det = scope.retained
    # Pre-book detections geometrically when asked to. ``booked_tiles``
    # maps a detection's GeoDataFrame index to the tile name(s) its
    # outcome should be credited to; the ``id`` rule keeps the legacy
    # single string.
    det_booking = assign_points_to_tiles(gdf_det, gdf_bounds, tile_join)
    geometric_booking: dict[Any, list[str]] | None = None
    if tile_join != TILE_JOIN_ID:
        geometric_booking = _tiles_intersecting(gdf_det, gdf_bounds)
        if tile_join == TILE_JOIN_GEOMETRIC_PRIMARY:
            centroids = {
                str(row["tile_name"]): row.geometry.centroid
                for _, row in gdf_bounds.iterrows()
            }
            geoms = dict(zip(gdf_det.index, gdf_det.geometry))
            geometric_booking = {
                idx: [
                    min(names, key=lambda t: geoms[idx].distance(centroids[t]))
                    if len(names) > 1 else names[0]
                ]
                for idx, names in geometric_booking.items()
            }

    # Detection indices lying geometrically inside the frame's tile union.
    # Only these are subject to the booking invariant: a detection outside
    # the frame is correctly booked nowhere, and one dropped earlier by the
    # per-map scoping is a different failure (see ``n_out_of_scope``).
    in_union = set(_tiles_intersecting(gdf_det, gdf_bounds))

    def _book(det_index: Any, recorded_tile: Any, outcome: str) -> tuple[int, int]:
        """Credit one matched/unmatched detection to its tile(s).

        Returns ``(considered, booked)``, each 0 or 1: ``considered`` counts
        the detection towards the invariant's denominator only when it is
        inside the frame's tile union, and ``booked`` records whether it
        reached any tile.
        """
        if geometric_booking is None:
            names = [recorded_tile] if recorded_tile in tile_counts else []
        else:
            names = geometric_booking.get(det_index, [])
        for name in names:
            if name in tile_counts:
                tile_counts[name][outcome] += 1
        considered = 1 if det_index in in_union else 0
        return considered, (1 if names else 0)

    n_considered = 0
    n_booked = 0

    # Pre-compute primary tile for each reference (for FN assignment)
    ref_primary = _assign_refs_to_primary_tiles(gdf_ref, gdf_bounds)
    # Invert: ref_index → tile_name
    ref_to_tile: dict[int, str] = {}
    for tile_name, ref_indices in ref_primary.items():
        for ref_idx in ref_indices:
            ref_to_tile[ref_idx] = tile_name

    # The per-sheet loop shared with calculate_f1_internal (same scoping of
    # both sides, same references, same matching).
    for _sheet, det_scope, ref_scope, _bounds in iter_sheet_scopes(
        scope, gdf_ref, gdf_bounds,
    ):
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
            for det_idx, det_row in det_scope.iterrows():
                considered, booked = _book(
                    det_idx, det_row["source_tile"], "fp",
                )
                n_considered += considered
                n_booked += booked
            continue

        # Per-map Hungarian matching (same as calculate_f1_internal)
        det_geoms = list(det_scope.geometry)
        ref_geoms = list(ref_scope.geometry)
        matched_det, matched_ref, unmatched_det, unmatched_ref = \
            match_detections_to_references(
                det_geoms, ref_geoms, buffer_metres,
            )

        # Assign TPs to the detection's tile
        det_scope_index = list(det_scope.index)
        for d_idx in matched_det:
            det_row = det_scope.iloc[d_idx]
            considered, booked = _book(
                det_scope_index[d_idx], det_row["source_tile"], "tp",
            )
            n_considered += considered
            n_booked += booked

        # Assign FPs to the detection's tile
        for d_idx in unmatched_det:
            det_row = det_scope.iloc[d_idx]
            considered, booked = _book(
                det_scope_index[d_idx], det_row["source_tile"], "fp",
            )
            n_considered += considered
            n_booked += booked

        # Assign FNs to the reference's primary tile
        ref_index_list = list(ref_scope.index)
        for r_idx in unmatched_ref:
            ref_original_idx = ref_index_list[r_idx]
            tile = ref_to_tile.get(ref_original_idx)
            if tile and tile in tile_counts:
                tile_counts[tile]["fn"] += 1

    # The same invariant the tile confusion enforces, in the TP/FP arm:
    # every in-frame detection that reached the booking step must have been
    # credited to some tile. A shortfall means the booking rule is not
    # describing this frame, and a table of pure false negatives must not
    # be handed to a bootstrap or a permutation test.
    if n_booked < n_considered:
        raise TileJoinRefusalError(
            f"per-tile TP/FP/FN table refused: {n_booked} of "
            f"{n_considered} in-frame detections were credited to a "
            f"tile under the '{tile_join}' tile join, a shortfall of "
            f"{n_considered - n_booked}. "
            f"({TILE_JOIN_REASON_DETECTION_SHORTFALL}) Most often the "
            f"cell's source_tile vocabulary is not this frame's; re-run "
            f"with a geometric tile_join.",
            reason=TILE_JOIN_REASON_DETECTION_SHORTFALL,
            tile_join=tile_join,
            n_booked=n_booked,
            n_considered=n_considered,
            diagnostics={"detections": _diagnostics(det_booking)},
        )

    # A *separate* failure, warned rather than raised because it is wider
    # than the tile join and predates it: a detection inside the frame that
    # the scope could attribute to no frame sheet (a null or foreign
    # ``source_tile`` and no recorded origin) never reaches the matching —
    # and is missing from ``calculate_f1_internal`` in exactly the same way,
    # which is why this cannot be fixed here without changing F1 as well.
    # Since ruling D50 every attributed detection that survives the scope is
    # inside its own sheet's tiles, so this is the only way an in-frame
    # detection can go unbooked.
    n_unattributed_in_frame = scope.diagnostics["n_unattributed_in_frame"]
    if n_unattributed_in_frame:
        logger.warning(
            "per-tile table: %d in-frame detection(s) carry no frame-sheet "
            "attribution (null or foreign source_tile, no recorded origin) "
            "and never reached the tile booking step. F1 is scoped the same "
            "way, so this is a wider issue than the tile join; see "
            "reports/tile-mcc-geometric-join-2026-09-12.md § 5.1(a).",
            n_unattributed_in_frame,
        )

    rows = [
        {"tile_name": tile, **counts}
        for tile, counts in tile_counts.items()
    ]
    return pd.DataFrame(rows)


def compute_per_tile_classification(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_join: str = TILE_JOIN_DEFAULT,
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
        tile_join: One of :data:`TILE_JOINS`; passed to
            :func:`calculate_tile_classification`, so the permutation
            tests that consume this table swap the same labels the
            reported confusion was built from.

    Returns:
        DataFrame with columns [tile_name, tp, tn, fp, fn]. Exactly one
        of {tp, tn, fp, fn} is 1 per row; the other three are 0.

    Raises:
        ValueError: If the tile join is refused for this frame (a
            shortfall of booked points against the frame's geometry) —
            the permutation test must not receive a mislabelled table.

    Notes:
        Sums over all rows reproduce the aggregate (TP, TN, FP, FN)
        returned by ``calculate_tile_classification()``. The per-tile
        representation is required for tile-swap permutation tests of
        MCC, where each tile's classification (one of the 4 cells) is
        independently swapped between two conditions.
    """
    classification_result = calculate_tile_classification(
        gdf_det, gdf_ref, gdf_bounds, tile_join=tile_join,
    )
    if "error" in classification_result:
        raise ValueError(
            f"per-tile classification refused "
            f"({classification_result.get('reason')}): "
            f"{classification_result['error']}"
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
    tile_join: str = TILE_JOIN_DEFAULT,
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
    redundant bootstrap + subprocess + I/O overhead is removed. The F1 /
    precision / recall point values match the CLI exactly; the one deliberate
    difference is that an *undefined* MCC (degenerate tile confusion matrix) is
    returned here as ``None`` rather than coerced to ``0.0`` as the CLI's
    ``_safe_round`` does — ``None`` is the more honest "undefined", and callers
    should rank/aggregate on F1 (or guard ``None``) rather than treat a missing
    MCC as zero discrimination.

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
        tile_join: One of :data:`TILE_JOINS`; defaults to
            :data:`TILE_JOIN_DEFAULT`.

    Returns:
        ``{"f1", "precision", "recall", "n_detections", "mcc",
        "mcc_refused_reason"}``. ``mcc`` is ``None`` when ``compute_mcc``
        is False, when there are no detections, when the confusion matrix
        is degenerate, or when the tile join was refused for this frame —
        ``mcc_refused_reason`` distinguishes the last case from the
        others and is ``None`` otherwise. A sweep must not rank on a
        refused MCC, so it is never silently returned as a number.
    """
    n_det = len(gdf_det)
    if n_det == 0:
        return {"f1": 0.0, "precision": 0.0, "recall": 0.0,
                "n_detections": 0, "mcc": None, "mcc_refused_reason": None}
    precision, recall, f1 = calculate_f1_internal(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )
    mcc = None
    mcc_refused_reason = None
    if compute_mcc:
        tile_class = calculate_tile_classification(
            gdf_det, gdf_ref, gdf_bounds, tile_join=tile_join,
        )
        if "error" in tile_class:
            mcc_refused_reason = tile_class.get("reason")
            logger.warning(
                "MCC withheld (%s): %s",
                mcc_refused_reason, tile_class["error"],
            )
        else:
            mcc = tile_class.get("mcc")
    return {"f1": float(f1), "precision": float(precision),
            "recall": float(recall), "n_detections": n_det, "mcc": mcc,
            "mcc_refused_reason": mcc_refused_reason}


def calculate_f1_internal(
    gdf_det: gpd.GeoDataFrame | DetectionScope,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int = 20,
    *,
    sheet_catalogue: Iterable[str] | None = None,
    parent_bounds: gpd.GeoDataFrame | None = None,
) -> tuple[float, float, float]:
    """
    Calculate global F1 using one-to-one matching via Hungarian algorithm.

    Each detection can match at most one reference, and vice versa.
    This ensures accurate mound counts: if one detection covers two mounds,
    it counts as 1 TP + 1 FN.

    Matching is per map sheet. Both sides are scoped to the frame the same
    way (PI ruling D50, :func:`iter_sheet_scopes`): a reference on sheet M
    counts only if it intersects one of M's tiles, and so does a detection
    attributed to M — its origin sheet (:func:`scope_detections_to_frame`).
    Before the ruling a detection was kept whenever its ``source_tile``
    began with M, wherever it lay.

    Pass the FULL frame. Scoring one sheet by passing only its tiles is a
    reduced frame: it excludes a detection seen only on sheets it leaves
    out, refuses one also seen on such a sheet unless ``parent_bounds``
    names the full frame, and with ``parent_bounds`` counts exactly the
    detections the full frame attributes to its sheets
    (:func:`scope_detections_to_frame`, "Reduced frames"). Per-sheet
    figures are simplest from :func:`per_sheet_confusion` on the full frame.

    Args:
        gdf_det: GeoDataFrame of detections, carrying ``source_tile`` and/or
            an origin column (:data:`ORIGIN_TILE_COLUMNS`), or the
            :class:`DetectionScope` already computed for this frame.
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries (defines evaluation scope).
        buffer_metres: Maximum distance for a valid match (default 20 m).
        sheet_catalogue: Passed to :func:`scope_detections_to_frame`.
        parent_bounds: The full frame a reduced ``gdf_bounds`` is part of
            (:func:`scope_detections_to_frame`).

    Returns:
        Tuple of (precision, recall, f1).

    Raises:
        ReducedFrameRefusalError: As :func:`scope_detections_to_frame`.
    """
    # The per-sheet counts of ONE full-frame scoring, summed: a per-sheet
    # report built from :func:`per_sheet_confusion` decomposes this exactly.
    tp = 0
    fp = 0
    fn = 0
    for s_tp, s_fp, s_fn in per_sheet_confusion(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres,
        sheet_catalogue=sheet_catalogue, parent_bounds=parent_bounds,
    ).values():
        tp += s_tp
        fp += s_fp
        fn += s_fn
    return precision_recall_f1(tp, fp, fn)


def precision_recall_f1(
    tp: int, fp: int, fn: int,
) -> tuple[float, float, float]:
    """Precision, recall and F1 from counts, exactly as the F1 scorer computes them.

    A zero denominator gives the integer ``0`` (not ``0.0``), as
    :func:`calculate_f1_internal` always has, so values written through it
    serialise unchanged.

    Args:
        tp: True positives.
        fp: False positives.
        fn: False negatives.

    Returns:
        ``(precision, recall, f1)``.

    Example:
        >>> precision_recall_f1(3, 1, 1)
        (0.75, 0.75, 0.75)
    """
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1


def per_sheet_confusion(
    gdf_det: gpd.GeoDataFrame | DetectionScope,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: float = 20,
    *,
    sheet_catalogue: Iterable[str] | None = None,
    parent_bounds: gpd.GeoDataFrame | None = None,
) -> dict[str, tuple[int, int, int]]:
    """Each frame sheet's TP, FP and FN, as partitions of ONE full-frame scoring.

    This is the matching :func:`calculate_f1_internal` sums, kept per
    sheet. A per-map report should read these partitions of the full frame
    rather than re-score each sheet on its own tiles: they sum to the full
    frame's counts by construction. A reduced frame (some of the full
    frame's sheets) sums to them too, but only because it excludes
    detections seen only off its sheets and refuses those seen across its
    edge unless ``parent_bounds`` is given (the D50 review, finding 2;
    :func:`scope_detections_to_frame`, "Reduced frames").

    Args:
        gdf_det: Detections, or the :class:`DetectionScope` of this same
            frame (computed once, it saves the spatial join when a caller
            scores several buffers).
        gdf_ref: References (``Map`` or ``source_map`` sheet column).
        gdf_bounds: The frame's tile polygons: the FULL frame, or a frame of
            whole sheets of it given ``parent_bounds``.
        buffer_metres: Maximum distance for a valid match.
        sheet_catalogue: Passed to :func:`scope_detections_to_frame`.
        parent_bounds: The full frame a reduced ``gdf_bounds`` is part of.

    Returns:
        ``sheet -> (tp, fp, fn)`` for every frame sheet, in sorted order,
        sheets with nothing on either side included as ``(0, 0, 0)``.

    Raises:
        ReducedFrameRefusalError: As :func:`scope_detections_to_frame`.

    Example:
        >>> scope = scope_detections_to_frame(dets, bounds)  # doctest: +SKIP
        >>> per_sheet_confusion(scope, refs, bounds, 20)["A"]  # doctest: +SKIP
        (41, 7, 5)
    """
    counts: dict[str, tuple[int, int, int]] = {}
    # The reference sheet column ('Map' for the gold standard, 'source_map'
    # for the 55-map student ground truth) is detected inside the shared
    # per-sheet loop, which raises if neither is present.
    for sheet, det_scope, ref_scope, _bounds in iter_sheet_scopes(
        gdf_det, gdf_ref, gdf_bounds,
        sheet_catalogue=sheet_catalogue, parent_bounds=parent_bounds,
    ):
        if det_scope.empty and ref_scope.empty:
            counts[sheet] = (0, 0, 0)
        elif det_scope.empty:
            counts[sheet] = (0, 0, len(ref_scope))
        elif ref_scope.empty:
            counts[sheet] = (0, len(det_scope), 0)
        else:
            # One-to-one matching using Hungarian algorithm
            det_geoms = list(det_scope.geometry)
            ref_geoms = list(ref_scope.geometry)

            matched_det, _matched_ref, unmatched_det, unmatched_ref = \
                match_detections_to_references(det_geoms, ref_geoms, buffer_metres)

            counts[sheet] = (len(matched_det), len(unmatched_det), len(unmatched_ref))
    return counts


def bootstrap_ci(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_iterations: int = 1000,
    random_seed: int | None = None,
    buffer_metres: int = 20,
    coverage_threshold: float = DEFAULT_COVERAGE_THRESHOLD,
    processed_tiles: set[str] | None = None,
) -> dict:
    """
    BCa bootstrap 95 % confidence intervals for precision, recall, and F1.

    Methodology aligned with preregistration Section 3.5 with the
    methodological upgrade applied in commit ``feat(bootstrap): replace
    percentile method with BCa`` (2026-04-29):

    * **Resampling unit**: tiles (fixed pre-lodgement in Decision 10,
      ``decisions-log.md:337``; the registered text specifies only "95%
      bootstrapped CIs", §3.5 — D17 audit U1).
    * **Resampling method**: with replacement (standard bootstrap).
    * **CI method**: Bias-Corrected and Accelerated (BCa) via
      :func:`scipy.stats.bootstrap`. Adjusts for both bias and skew of
      the bootstrap distribution. Falls back to the percentile method
      when BCa is degenerate (e.g. constant statistic or undefined
      acceleration).
    * **Coverage check**: Mitigation 3 (sparse-coverage transparency).
      Counts tiles with TP+FP+FN == 0; flags ``coverage_status =
      "sparse_cross_grid"`` when the zero-fraction strictly exceeds
      ``coverage_threshold`` (default 0.5). When ``processed_tiles`` is
      supplied, a direct unprocessed-tile count takes priority and flags
      ``coverage_status = "partial_coverage"`` instead (E72).

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
        processed_tiles: Optional set of tile filenames the detection set
            actually processed, typically obtained from
            :func:`read_processed_tiles` on the detection GeoJSON. When
            supplied, unprocessed tiles are counted directly against the
            evaluation bounds rather than inferred from detection density
            (E72). ``None`` (the default) preserves the pre-E72 behaviour
            exactly.

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

    coverage = _compute_coverage(
        tile_metrics,
        threshold=coverage_threshold,
        processed_tiles=processed_tiles,
    )

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


def _parent_of_cut(
    gdf_bounds: gpd.GeoDataFrame,
    cut: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame | None:
    """The frame a common-footprint cut was taken from, when the cut is smaller.

    The paired bootstraps score every condition on the tiles all conditions
    share. Where that footprint is smaller than a condition's own frame it
    is a REDUCED frame of it, and ruling D59 counts a detection there only
    if the condition's frame attributes it to a sheet inside the footprint
    (the comment above :class:`ReducedFrameRefusalError`): the frame is
    passed as ``parent_bounds``. Without it, a detection seen across the
    footprint's edge would refuse, and one in an unknown tile vocabulary
    would fall back to ``source_tile``, which carries no such guarantee.
    Where the footprint is the whole frame nothing is passed, so a
    same-frame comparison is scored exactly as before. A footprint that
    cuts through a sheet is still not an additive share of the frame's
    points (whole-sheet partitions only).

    Args:
        gdf_bounds: A condition's own frame.
        cut: Its rows on the common footprint.

    Returns:
        ``gdf_bounds`` when ``cut`` holds fewer tiles, else ``None``.
    """
    return gdf_bounds if len(cut) < len(gdf_bounds) else None


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
        return_p_values: If True, include a two-sided p-value for each
            metric from the paired tile-swap PERMUTATION test
            (``lib_permutation.paired_permutation_test``, 10,000
            permutations, seed 42, tiles in sorted order), never from the
            bootstrap (PI ruling D42, 2026-10-05). The bootstrap p this
            function used to return (2 x the minority tail, floored at
            1/B) sat at its floor between identical arms
            (``reports/retest-bootstrap-check-2026-10-05.md``).

    Returns:
        Effect size estimates with 95% CIs for F1, precision, recall differences.
        When ``return_p_values=True``, each metric dict also includes
        ``p_value`` and ``p_method``, and the result gains ``permutation``
        (tiles, discordant tiles, permutations, seed).
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
    # A footprint smaller than a condition's frame is a reduced frame of it,
    # attributed as that frame attributes (ruling D59).
    tile_metrics_a = compute_per_tile_tp_fp_fn(
        gdf_det_a, gdf_ref, common_bounds_a, buffer_metres=buffer_metres,
        parent_bounds=_parent_of_cut(gdf_bounds_a, common_bounds_a),
    )
    tile_metrics_b = compute_per_tile_tp_fp_fn(
        gdf_det_b, gdf_ref, common_bounds_b, buffer_metres=buffer_metres,
        parent_bounds=_parent_of_cut(gdf_bounds_b, common_bounds_b),
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
        metric_key: str,
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
            # D42: the p-value comes from the paired tile-swap permutation
            # test on the same per-tile counts, never from these bootstrap
            # draws.
            perm_metric = permutation["metrics"][metric_key]
            result["p_value"] = perm_metric["p_value"]
            result["p_method"] = permutation["method"]
        return result

    permutation = None
    if return_p_values:
        permutation = _permutation_on_tile_metrics(
            tile_metrics_a, tile_metrics_b, common_tiles,
        )

    out = {
        "f1_difference": _build_metric_dict(
            f1_diffs, return_p_values, "f1",
        ),
        "precision_difference": _build_metric_dict(
            precision_diffs, return_p_values, "precision",
        ),
        "recall_difference": _build_metric_dict(
            recall_diffs, return_p_values, "recall",
        ),
        "n_tiles": n_tiles,
        "n_iterations": n_iterations,
        "bootstrap_method": BOOTSTRAP_METHOD,
        "bootstrap_lib": BOOTSTRAP_LIB,
    }
    if permutation is not None:
        out["permutation"] = {
            key: permutation[key]
            for key in ("method", "n_tiles", "n_discordant_tiles",
                        "n_permutations", "seed")
        }
    return out


def _tile_count_arrays(
    tile_metrics: pd.DataFrame,
    tiles: list[str],
) -> dict[str, np.ndarray]:
    """Per-tile TP/FP/FN arrays aligned to ``tiles`` (absent tile = zeros).

    Mirrors :func:`aggregate_tile_metrics`: a tile listed twice in
    ``tile_metrics`` contributes its first row.

    Args:
        tile_metrics: Frame with columns ``tile_name``, ``tp``, ``fp``, ``fn``.
        tiles: Tile names, in the order the arrays should follow.

    Returns:
        Dict of float arrays ``tp``, ``fp``, ``fn``, each ``len(tiles)``.
    """
    first = tile_metrics.groupby("tile_name", sort=False)[["tp", "fp", "fn"]].first()
    aligned = first.reindex(tiles).fillna(0.0)
    return {key: aligned[key].to_numpy(dtype=float) for key in ("tp", "fp", "fn")}


def _permutation_on_tile_metrics(
    tile_metrics_a: pd.DataFrame,
    tile_metrics_b: pd.DataFrame,
    common_tiles: list[str],
) -> dict:
    """Paired tile-swap permutation test of A - B on per-tile counts (D42).

    Tiles are put in SORTED order first: the swap a tile receives depends
    on its position, and ``common_tiles`` comes from a set intersection
    whose order varies with the interpreter's hash seed.

    Args:
        tile_metrics_a: Per-tile counts for condition A.
        tile_metrics_b: Per-tile counts for condition B.
        common_tiles: The tiles both conditions cover.

    Returns:
        The :func:`lib_permutation.paired_permutation_test` result.
    """
    # Imported here, and by either name, because this library is imported
    # both as ``lib_advanced_metrics`` and as ``scripts.lib_advanced_metrics``.
    try:
        from lib_permutation import paired_permutation_test
    except ImportError:
        from scripts.lib_permutation import paired_permutation_test

    tiles = sorted(common_tiles)
    return paired_permutation_test(
        _tile_count_arrays(tile_metrics_a, tiles),
        _tile_count_arrays(tile_metrics_b, tiles),
    )


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

    This preserves tiles as the resampling unit (fixed pre-lodgement in
    Decision 10; the registered §3.5 specifies only "95% bootstrapped
    CIs" — D17 audit U1) while correctly handling the K=10
    repeated-measures structure. Errata E22: replaces the prior approach of merging all
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
    return_p_values: bool = False,
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
        return_p_values: If True, add a two-sided p-value per metric from
            the paired tile-swap PERMUTATION test (PI ruling D42): each
            tile's whole run block swaps between the conditions, and the
            statistic is the same mean-over-runs metric this function
            bootstraps. If the run counts differ, blocks cannot swap, so the
            test runs on pass-averaged per-tile counts (micro metric of the
            averaged counts) and ``permutation.statistic`` says so.

    Returns:
        dict: Effect size CIs for F1, precision, recall differences; with
        ``return_p_values``, each metric also carries ``p_value`` and
        ``p_method``, and the result gains ``permutation``.
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
    out = {
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
    if return_p_values:
        perm, statistic = _multi_run_permutation(
            run_metrics_a, run_metrics_b, sorted(tiles),
        )
        for key, metric in (("f1_difference", "f1"),
                            ("precision_difference", "precision"),
                            ("recall_difference", "recall")):
            out[key]["p_value"] = perm["metrics"][metric]["p_value"]
            out[key]["p_method"] = perm["method"]
        out["permutation"] = {
            "statistic": statistic,
            **{k: perm[k] for k in ("method", "n_tiles", "n_runs",
                                    "n_discordant_tiles", "n_permutations", "seed")},
        }
    return out


def _multi_run_permutation(
    run_metrics_a: list[pd.DataFrame],
    run_metrics_b: list[pd.DataFrame],
    tiles: list[str],
) -> tuple[dict, str]:
    """Paired permutation test between two multi-run conditions (D42).

    Equal run counts: each tile's run block swaps, statistic = mean over
    runs of each run's micro metric (the bootstrap's estimand). Unequal run
    counts: pass-averaged per-tile counts, statistic = micro metric of the
    averaged counts.

    Args:
        run_metrics_a: Per-run per-tile count frames, condition A.
        run_metrics_b: Per-run per-tile count frames, condition B.
        tiles: Tiles in the (sorted) order the test uses.

    Returns:
        (the ``paired_permutation_test`` result, a statistic description).
    """
    try:
        from lib_permutation import paired_permutation_test
    except ImportError:
        from scripts.lib_permutation import paired_permutation_test

    def _stack(run_tms: list[pd.DataFrame]) -> dict[str, np.ndarray]:
        per_run = [_tile_count_arrays(tm, tiles) for tm in run_tms]
        return {k: np.stack([r[k] for r in per_run]) for k in ("tp", "fp", "fn")}

    a, b = _stack(run_metrics_a), _stack(run_metrics_b)
    if a["tp"].shape[0] == b["tp"].shape[0]:
        return (paired_permutation_test(a, b),
                "mean over runs of each run's micro metric; run blocks swap per tile")
    a_mean = {k: v.mean(axis=0) for k, v in a.items()}
    b_mean = {k: v.mean(axis=0) for k, v in b.items()}
    return (paired_permutation_test(a_mean, b_mean),
            "run counts differ: micro metric of pass-averaged per-tile counts")


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
            parent_bounds=_parent_of_cut(gdf_bounds, common_bounds),
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


def _tiles_intersecting(
    gdf_points: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict[Any, list[str]]:
    """
    Map each point's index to every frame tile it intersects.

    ``intersects`` rather than ``contains`` is deliberate: it covers the
    boundary, so a point lying exactly on the edge shared by two tiles is
    a candidate for both. Which of the two it is finally booked to is the
    caller's rule (see :data:`TILE_JOIN_GEOMETRIC_PRIMARY` and
    :data:`TILE_JOIN_GEOMETRIC_CONTAINS`).

    Args:
        gdf_points: Point geometries (detections or references) in the
            frame's coordinate reference system.
        gdf_bounds: Tile polygons with a ``tile_name`` column.

    Returns:
        ``{point index: [tile_name, ...]}``, omitting points that
        intersect no tile. Tile-name lists are sorted so downstream
        tie-breaking is deterministic regardless of spatial-index order.

    Example:
        >>> # Two 10-unit tiles overlapping by 2 units; a point at x=9
        >>> # lies inside both, so both are candidates.
        >>> len(_tiles_intersecting(points, bounds)[0])  # doctest: +SKIP
        2
    """
    if gdf_points.empty:
        return {}

    joined = gpd.sjoin(
        gdf_points,
        gdf_bounds[["tile_name", "geometry"]],
        how="inner",
        predicate="intersects",
    )
    candidates: dict[Any, list[str]] = {}
    for idx, tile_name in zip(joined.index, joined["tile_name"]):
        candidates.setdefault(idx, []).append(tile_name)
    for names in candidates.values():
        names.sort()
    return candidates


def assign_points_to_tiles(
    gdf_points: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_join: str,
    *,
    id_column: str = "source_tile",
) -> dict[str, Any]:
    """
    Book each point to the frame tile(s) it belongs to, under one named rule.

    This is the single place in the library where a point becomes a tile.
    It exists so that the tile confusion matrix is built the same way on
    both of its axes and at every call site, and so that the rule in force
    is a recorded parameter rather than an implementation accident.

    The three rules are documented on :data:`TILE_JOIN_ID`,
    :data:`TILE_JOIN_GEOMETRIC_PRIMARY` and
    :data:`TILE_JOIN_GEOMETRIC_CONTAINS`. In summary:

    ``id``
        String equality of ``id_column`` against ``tile_name``. Geometry
        is not consulted, so this rule cannot detect that a point lies in
        a tile whose name it does not carry.
    ``geometric-primary``
        Exactly one tile per point: among the tiles the point intersects,
        the one whose centroid is nearest, ties broken by the
        lexicographically smallest ``tile_name``.
    ``geometric-contains``
        Every tile the point intersects, which on an overlapping frame is
        more than one for a substantial share of points.

    **Points in no tile** are never booked anywhere. They are excluded
    from the confusion matrix and counted in ``n_outside_union`` so the
    exclusion is reported rather than invisible. A point on a shared edge
    is inside the union and is booked by the rule above.

    Args:
        gdf_points: Point geometries (detections or references), already
            in the frame's coordinate reference system.
        gdf_bounds: Tile polygons with a ``tile_name`` column.
        tile_join: One of :data:`TILE_JOINS`.
        id_column: Column holding the recorded tile name, consulted only
            by the ``id`` rule.

    Returns:
        Dict with:

        ``tiles_with_point``
            ``set[str]`` of tile names holding at least one point.
        ``counts``
            ``{tile_name: int}``, points booked to each tile. Under
            ``geometric-contains`` these sum to more than ``n_points``.
        ``n_points``
            Rows in ``gdf_points``.
        ``n_assigned``
            Points booked to at least one tile.
        ``n_inside_union``
            Points intersecting at least one frame tile — the geometric
            truth the shortfall invariant compares ``n_assigned`` against.
        ``n_outside_union``
            ``n_points - n_inside_union``; excluded by design.
        ``n_multi_tile``
            Points intersecting more than one frame tile (a property of
            the frame, reported under every rule).
        ``tile_join``
            The rule applied, echoed back for the record.

    Raises:
        ValueError: If ``tile_join`` is not a member of :data:`TILE_JOINS`.
    """
    if tile_join not in TILE_JOINS:
        raise ValueError(
            f"tile_join must be one of {TILE_JOINS!r}, got {tile_join!r}",
        )

    n_points = len(gdf_points)
    candidates = _tiles_intersecting(gdf_points, gdf_bounds)
    n_inside_union = len(candidates)
    n_multi_tile = sum(1 for names in candidates.values() if len(names) > 1)

    counts: dict[str, int] = {}

    if tile_join == TILE_JOIN_ID:
        # Geometry is not consulted. A point counts towards a tile only
        # when the string it carries is byte-equal to that tile's name.
        frame = set(gdf_bounds["tile_name"].astype(str))
        if n_points and id_column not in gdf_points.columns:
            return {
                "tiles_with_point": set(),
                "counts": {},
                "n_points": n_points,
                "n_assigned": 0,
                "n_inside_union": n_inside_union,
                "n_outside_union": n_points - n_inside_union,
                "n_multi_tile": n_multi_tile,
                "tile_join": tile_join,
                "missing_id_column": True,
            }
        values = (
            gdf_points[id_column].tolist() if n_points else []
        )
        for value in values:
            if value is not None and str(value) in frame:
                counts[str(value)] = counts.get(str(value), 0) + 1

    elif tile_join == TILE_JOIN_GEOMETRIC_PRIMARY:
        centroids = {
            str(row["tile_name"]): row.geometry.centroid
            for _, row in gdf_bounds.iterrows()
        }
        geometries = dict(zip(gdf_points.index, gdf_points.geometry))
        for idx, names in candidates.items():
            if len(names) == 1:
                winner = names[0]
            else:
                geom = geometries[idx]
                # Nearest tile centroid; ``names`` is already sorted, and
                # ``min`` keeps the first minimum, so an exact distance
                # tie resolves to the lexicographically smallest name.
                winner = min(
                    names, key=lambda t: geom.distance(centroids[t]),
                )
            counts[winner] = counts.get(winner, 0) + 1

    else:  # TILE_JOIN_GEOMETRIC_CONTAINS
        for names in candidates.values():
            for name in names:
                counts[name] = counts.get(name, 0) + 1

    if tile_join == TILE_JOIN_ID:
        n_assigned = sum(counts.values())
    else:
        # Under the geometric rules every point inside the union is
        # booked, so the number of distinct assigned points is exactly
        # the number inside the union minus none.
        n_assigned = sum(
            1 for names in candidates.values() if names
        )

    return {
        "tiles_with_point": set(counts),
        "counts": counts,
        "n_points": n_points,
        "n_assigned": n_assigned,
        "n_inside_union": n_inside_union,
        "n_outside_union": n_points - n_inside_union,
        "n_multi_tile": n_multi_tile,
        "tile_join": tile_join,
    }


def check_tile_join_invariant(
    detection_assignment: dict[str, Any],
    reference_assignment: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Refuse a tile confusion whose join lost points that are inside the frame.

    The invariant, in one sentence: *the number of points booked to some
    tile must equal the number of points geometrically inside the frame's
    tile union.* It holds by construction under both geometric rules, and
    it is exactly what the legacy ``id`` rule violates when a cell is
    scored on a frame whose tile vocabulary is not the one its proposer
    ran on — 21 of 475 in-union detections booked, in the measured case.

    This replaces the need for a separate pre-flight vocabulary check for
    *correctness* purposes: the scorer itself now aborts the MCC with a
    named reason rather than emitting a plausible-looking number.
    ``scripts/check_tile_vocabulary_match.py`` remains useful as a cheap
    survey instrument over a corpus that has already been scored.

    Args:
        detection_assignment: Output of :func:`assign_points_to_tiles`
            for the detections.
        reference_assignment: Output of :func:`assign_points_to_tiles`
            for the reference mounds.

    Returns:
        ``None`` when the invariant holds. Otherwise a dict with
        ``error``, ``reason`` (one of the ``TILE_JOIN_REASON_*``
        constants) and a ``tile_join_diagnostics`` block, suitable for
        returning directly from a scorer.
    """
    if detection_assignment.get("missing_id_column"):
        return {
            "error": (
                "tile confusion refused: detections carry no "
                "'source_tile' property, which the 'id' tile join "
                "requires — re-score with a geometric --tile-join, or "
                "assign source_tile first"
            ),
            "reason": TILE_JOIN_REASON_NO_SOURCE_TILE,
            "tile_join_diagnostics": {
                "detections": detection_assignment,
                "references": reference_assignment,
            },
        }

    checks = (
        (detection_assignment, "detection", TILE_JOIN_REASON_DETECTION_SHORTFALL),
        (reference_assignment, "reference", TILE_JOIN_REASON_REFERENCE_SHORTFALL),
    )
    for assignment, noun, reason in checks:
        assigned = assignment["n_assigned"]
        inside = assignment["n_inside_union"]
        if assigned < inside:
            return {
                "error": (
                    f"tile confusion refused: {assigned} of {inside} "
                    f"in-frame {noun}s were booked to a tile under the "
                    f"'{assignment['tile_join']}' tile join, a shortfall "
                    f"of {inside - assigned}. The join is not describing "
                    f"this frame — most often because the cell's "
                    f"source_tile vocabulary is not the frame's. MCC is "
                    f"withheld rather than reported."
                ),
                "reason": reason,
                "tile_join_diagnostics": {
                    "detections": _diagnostics(detection_assignment),
                    "references": _diagnostics(reference_assignment),
                },
            }
    return None


def _diagnostics(assignment: dict[str, Any]) -> dict[str, Any]:
    """Strip the bulky members from an assignment for reporting."""
    return {
        key: value
        for key, value in assignment.items()
        if key not in ("tiles_with_point", "counts")
    }


def _vocabulary_census(
    gdf_det: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    *,
    id_column: str = "source_tile",
    n_sample: int = 3,
) -> dict[str, Any]:
    """Describe the two tile vocabularies a refusal is a disagreement between.

    A tile-join refusal is not a numerical anomaly; it is the scorer
    reporting that the detection set was named on one tiling and is being
    scored against another. The only way a reader can act on that is to
    see both vocabularies, so the refusal record carries a census of each:
    how many distinct tile names, which map-sheet prefixes, and a few
    literal names to eyeball. The measured case reads
    ``K-35-052-4_32635_x0_y1152.png`` (a 192 px stride) against
    ``K-35-052-4_32635_x0_y1008.png`` (a 336 px stride) — same sheet, same
    naming scheme, different offsets, which is exactly why the mismatch
    was invisible for a year.

    Args:
        gdf_det: The detections, whose ``id_column`` holds the recorded
            tile name.
        gdf_bounds: The scoring frame, whose ``tile_name`` column is the
            vocabulary the detections are being joined against.
        id_column: Column holding the recorded tile name.
        n_sample: How many literal names to quote from each vocabulary.
            Sorted, so the sample is deterministic.

    Returns:
        ``{"frame": {...}, "detections": {...}}``. Both sub-dicts carry
        ``n_distinct_tile_names``, ``map_prefixes`` and
        ``sample_tile_names``; the detection side adds
        ``n_names_in_frame_vocabulary``, which is the count the shortfall
        is a consequence of.

    Example:
        >>> census = _vocabulary_census(dets, bounds)  # doctest: +SKIP
        >>> census["detections"]["n_names_in_frame_vocabulary"]  # doctest: +SKIP
        7
    """
    frame_names = sorted({str(name) for name in gdf_bounds["tile_name"]})
    if id_column in gdf_det.columns:
        det_names = sorted({
            str(name) for name in gdf_det[id_column].dropna()
        })
    else:
        det_names = []
    frame_set = set(frame_names)
    return {
        "frame": {
            "n_tiles": int(len(gdf_bounds)),
            "n_distinct_tile_names": len(frame_names),
            "map_prefixes": sorted({get_map_name(n) for n in frame_names}),
            "sample_tile_names": frame_names[:n_sample],
        },
        "detections": {
            "n_detections": int(len(gdf_det)),
            "id_column": id_column,
            "id_column_present": id_column in gdf_det.columns,
            "n_distinct_tile_names": len(det_names),
            "n_names_in_frame_vocabulary": sum(
                1 for n in det_names if n in frame_set
            ),
            "map_prefixes": sorted({get_map_name(n) for n in det_names}),
            "sample_tile_names": det_names[:n_sample],
        },
    }


def describe_tile_join_refusal(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_join: str = TILE_JOIN_DEFAULT,
) -> dict[str, Any] | None:
    """Ask, before scoring, whether this frame's tile join is interpretable.

    The invariant of § 3 of ``reports/tile-mcc-geometric-join-2026-09-12.md``
    used to be discoverable only by tripping over it: a refused cell raised
    inside :func:`bootstrap_ci` and took the entire evaluation with it, so
    the cell's F1 — a quantity the refusal does not touch — could not be
    written at all. The PI's ruling of 2026-09-13 is that such a cell
    publishes its whole-frame F1 in full and withholds its per-tile
    statistics. That requires asking the question *up front*, which is
    what this function is for.

    It performs exactly the assignment :func:`calculate_tile_classification`
    performs — the same rule on detections, the containment rule on
    references whenever the detection rule is ``id``, so the two axes of
    the confusion are built the same way — and runs
    :func:`check_tile_join_invariant` over the result. It computes no
    metric and spends no bootstrap draw.

    Args:
        gdf_det: GeoDataFrame of detections.
        gdf_ref: GeoDataFrame of reference mounds.
        gdf_bounds: GeoDataFrame of the scoring frame's tile polygons.
        tile_join: One of :data:`TILE_JOINS`; defaults to
            :data:`TILE_JOIN_DEFAULT`.

    Returns:
        ``None`` when the join is sound and every per-tile quantity may be
        computed. Otherwise a record of the refusal, ready to serialise
        into an artefact:

        ``withheld``
            Always ``True``, so a consumer can test one key.
        ``reason``
            One of the ``TILE_JOIN_REASON_*`` constants.
        ``detail``
            The scorer's own human-readable refusal message.
        ``tile_join`` / ``reference_join``
            The rules that were in force on each axis.
        ``shortfall``
            ``n_booked``, ``n_inside_union``, ``n_outside_union``,
            ``n_multi_tile`` and ``shortfall`` for whichever axis failed,
            plus ``axis`` naming it.
        ``vocabularies``
            The two tile vocabularies (:func:`_vocabulary_census`).
        ``withheld_quantities`` / ``reported_quantities``
            :data:`TILE_JOIN_WITHHELD_QUANTITIES` and
            :data:`TILE_JOIN_REPORTED_QUANTITIES`, so the artefact states
            the boundary rather than leaving a reader to infer it.
        ``tile_join_diagnostics``
            The full per-axis diagnostics block.

    Example:
        >>> describe_tile_join_refusal(dets, refs, bounds) is None  # doctest: +SKIP
        True
    """
    if len(gdf_bounds) == 0:
        return None
    # Ruling D50: ask the question of the detections the confusion will
    # actually book — every row but the out-of-frame ones the rule removes
    # (see calculate_tile_classification).
    gdf_det = scope_detections_to_frame(
        gdf_det, gdf_bounds, require_attribution=False,
    ).retained
    reference_join = (
        TILE_JOIN_GEOMETRIC_CONTAINS
        if tile_join == TILE_JOIN_ID
        else tile_join
    )
    det_assignment = assign_points_to_tiles(gdf_det, gdf_bounds, tile_join)
    ref_assignment = assign_points_to_tiles(
        gdf_ref, gdf_bounds, reference_join,
    )
    refusal = check_tile_join_invariant(det_assignment, ref_assignment)
    if refusal is None:
        return None

    # Which axis failed decides which counts describe the shortfall. The
    # reference axis can only fail under a rule that is not ``id``, but it
    # is reported the same way when it does.
    if refusal["reason"] == TILE_JOIN_REASON_REFERENCE_SHORTFALL:
        axis, assignment = "references", ref_assignment
    else:
        axis, assignment = "detections", det_assignment

    return {
        "withheld": True,
        "reason": refusal["reason"],
        "detail": refusal["error"],
        "tile_join": tile_join,
        "reference_join": reference_join,
        "shortfall": {
            "axis": axis,
            "n_booked": assignment.get("n_assigned", 0),
            "n_inside_union": assignment.get("n_inside_union", 0),
            "n_outside_union": assignment.get("n_outside_union", 0),
            "n_multi_tile": assignment.get("n_multi_tile", 0),
            "shortfall": (
                assignment.get("n_inside_union", 0)
                - assignment.get("n_assigned", 0)
            ),
        },
        "vocabularies": _vocabulary_census(gdf_det, gdf_bounds),
        "withheld_quantities": list(TILE_JOIN_WITHHELD_QUANTITIES),
        "reported_quantities": list(TILE_JOIN_REPORTED_QUANTITIES),
        "tile_join_diagnostics": refusal.get("tile_join_diagnostics"),
        "ruling": (
            "PI ruling 2026-09-13 (S153 ruling 6): the name-based 'id' "
            "tile join is the published tile-MCC convention; a cell the "
            "invariant refuses reports its whole-frame F1 in full and "
            "withholds its per-tile statistics. See "
            "reports/tile-mcc-geometric-join-2026-09-12.md."
        ),
    }


def calculate_tile_classification(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_join: str = TILE_JOIN_DEFAULT,
    *,
    parent_bounds: gpd.GeoDataFrame | None = None,
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

    **The tile join.** ``tile_join`` names how a point becomes a tile, and
    the three rules are not interchangeable on an overlapping frame — see
    :data:`TILE_JOIN_ID`, :data:`TILE_JOIN_GEOMETRIC_PRIMARY`,
    :data:`TILE_JOIN_GEOMETRIC_CONTAINS` and the note on
    :data:`TILE_JOIN_DEFAULT`. The geometric rules are applied
    **symmetrically**, to references as well as detections, so that both
    axes of the confusion matrix are built the same way. ``id`` keeps the
    legacy asymmetric pairing (detections by name, references by
    containment) purely so that published numbers reproduce.

    Whichever rule is in force, the assignment is checked against
    geometry by :func:`check_tile_join_invariant` before any count is
    reported: every point inside the frame's tile union must have been
    booked to some tile. A shortfall returns ``{"error": ...,
    "reason": ...}`` instead of an MCC.

    Args:
        gdf_det: GeoDataFrame of detections. A ``source_tile`` column is
            required by the ``id`` join only.
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries (must have 'tile_name' column).
        tile_join: One of :data:`TILE_JOINS`; defaults to
            :data:`TILE_JOIN_DEFAULT`.
        parent_bounds: The frame ``gdf_bounds`` was cut from, or ``None``
            (:func:`scope_detections_to_frame`). The common-footprint
            bootstrap passes a condition's own frame here when the common
            footprint is smaller than it (:func:`_parent_of_cut`).

    Returns:
        Classification results including tp, tn, fp, fn counts; mcc;
        sensitivity; specificity; tile counts; per-tile details; and a
        ``tile_join`` / ``tile_join_diagnostics`` record of how the
        assignment was made and how many points fell outside the frame.
        On a refused confusion, ``error`` and ``reason`` instead.

    Example:
        >>> result = calculate_tile_classification(
        ...     dets, refs, bounds, tile_join=TILE_JOIN_GEOMETRIC_CONTAINS,
        ... )  # doctest: +SKIP
        >>> result["tile_join"]  # doctest: +SKIP
        'geometric-contains'
    """
    tiles = gdf_bounds['tile_name'].unique()
    n_tiles = len(tiles)

    if n_tiles == 0:
        return {"error": "No tiles in bounds", "reason": TILE_JOIN_REASON_NO_TILES}

    # Ruling D50: the confusion drops exactly the detections the F1 point
    # estimate drops as out of frame — attributed to a frame sheet but
    # outside its tiles. Before the ruling such a detection whose name
    # collided with a frame tile was booked to it under the ``id`` join (and
    # padded the invariant's booked count). Rows on no frame sheet (a null
    # or foreign ``source_tile``, or a frame whose tile names carry no
    # parseable sheet) are kept as they always were: the confusion never
    # needed a sheet, the geometric joins book them by position, and the
    # ``id`` join treats them by name below.
    scope = scope_detections_to_frame(
        gdf_det, gdf_bounds, require_attribution=False, parent_bounds=parent_bounds,
    )
    gdf_det = scope.retained

    # Book detections and references to tiles once, up front, instead of
    # re-scanning both frames inside the per-tile loop. The reference rule
    # follows the detection rule whenever the detection rule is geometric,
    # so the confusion matrix is not built one way on one axis and another
    # way on the other — the defect this parameter exists to close.
    reference_join = (
        TILE_JOIN_GEOMETRIC_CONTAINS
        if tile_join == TILE_JOIN_ID
        else tile_join
    )
    det_assignment = assign_points_to_tiles(gdf_det, gdf_bounds, tile_join)
    ref_assignment = assign_points_to_tiles(
        gdf_ref, gdf_bounds, reference_join,
    )

    refusal = check_tile_join_invariant(det_assignment, ref_assignment)
    if refusal is not None:
        refusal["n_tiles"] = n_tiles
        refusal["tile_join"] = tile_join
        return refusal

    det_counts = det_assignment["counts"]
    ref_counts = ref_assignment["counts"]

    tile_details = []
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for tile_name in tiles:
        n_references = ref_counts.get(str(tile_name), 0)
        n_detections = det_counts.get(str(tile_name), 0)
        has_mounds = n_references > 0
        has_detections = n_detections > 0

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
            "n_references": n_references,
            "n_detections": n_detections,
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
        "tile_join": tile_join,
        "tile_join_diagnostics": {
            "detections": _diagnostics(det_assignment),
            "references": _diagnostics(ref_assignment),
            "reference_join": reference_join,
        },
        "detection_scope": scope.diagnostics,
    }


def bootstrap_tile_classification_ci(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_iterations: int = 1000,
    random_seed: int | None = None,
    tile_join: str = TILE_JOIN_DEFAULT,
) -> dict:
    """
    BCa bootstrap 95 % CIs for tile-level MCC, sensitivity, and specificity.

    Tile-level resampling with replacement (unit fixed pre-lodgement in
    Decision 10; the registered §3.5 specifies only "95% bootstrapped
    CIs" — D17 audit U1). Uses :func:`scipy.stats.bootstrap` with ``method='BCa'``
    via :func:`_bca_ci_from_indices`. Each per-tile classification label
    (TP / TN / FP / FN) is held in arrays indexed by tile, and the
    bootstrap statistic is computed per resample by counting labels in
    the sampled subset.

    On bootstrap iterations where any of the (tp+fp), (tp+fn), (tn+fp),
    or (tn+fn) row/column sums is zero, the metric is undefined; the
    score is treated as ``NaN`` and skipped when computing the CI bounds.

    Errata E81 (2026-08-18) made the code match that sentence. Until
    then ``_mcc_from_idx`` returned ``0.0`` for a degenerate resample,
    so every bootstrap mean and both CI bounds were a mixture of
    measurements and placeholders — visible in the committed corpus as
    tile-MCC CI lower bounds of exactly ``0.0000`` on cells whose point
    estimate is positive. Degenerate resamples are now dropped. When
    *every* resample is degenerate (the whole-corpus case is
    TN + FN = 0 — the model predicted every tile populated) the metric
    has no distribution at all, and ``mean`` / ``ci_lower`` /
    ``ci_upper`` are returned as ``None`` with ``method`` set to
    ``"undefined"``. ``n_valid_mcc`` / ``n_valid_sensitivity`` /
    ``n_valid_specificity`` report how many of the ``n_iterations``
    resamples were actually defined.

    Args:
        gdf_det: GeoDataFrame of detections.
        gdf_ref: GeoDataFrame of ground truth references.
        gdf_bounds: GeoDataFrame of tile boundaries.
        n_iterations: Number of bootstrap iterations (default 1000).
        random_seed: Optional seed for reproducibility.
        tile_join: How points are booked to tiles; passed straight through
            to :func:`calculate_tile_classification`, which is the single
            place the rule is applied. When that function refuses the
            confusion (a tile-join shortfall), this function propagates
            the refusal rather than bootstrapping a meaningless statistic.

    Returns:
        Bootstrap CIs for MCC, sensitivity, and specificity. Each metric
        dict includes ``point`` (deterministic estimate from
        :func:`calculate_tile_classification`), ``mean`` (bootstrap mean),
        ``ci_lower``, ``ci_upper``, and ``method``. On a refused
        confusion, the refusal dict from
        :func:`check_tile_join_invariant`.
    """
    tiles = gdf_bounds['tile_name'].unique()
    n_tiles = len(tiles)

    if n_tiles == 0:
        return {"error": "No tiles in bounds", "reason": TILE_JOIN_REASON_NO_TILES}

    # Pre-compute per-tile classification once (errata E26: fixes isin()
    # de-duplication that turned bootstrap into subsampling).
    point_result = calculate_tile_classification(
        gdf_det, gdf_ref, gdf_bounds, tile_join=tile_join,
    )
    if "error" in point_result:
        # The tile join did not describe this frame. Resampling tiles
        # whose labels are wrong would produce a confidence interval
        # around a number that must not be reported at all.
        return point_result
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
            # MCC undefined on this resample (E81). Return NaN so the
            # resample is *dropped* by ``skip_undefined=True`` — the
            # behaviour this function's docstring has always claimed.
            # Substituting 0.0 here silently pulled means and lower
            # bounds toward the value § 4.2 of the registration labels
            # "random".
            return float("nan")
        return numerator / np.sqrt(denom_parts)

    def _sensitivity_from_idx(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        tp = float(tp_arr[idx].sum())
        fn = float(fn_arr[idx].sum())
        # Undefined when the resample contains no reference-populated
        # tile; NaN so the resample is dropped, not scored as zero.
        return tp / (tp + fn) if (tp + fn) > 0 else float("nan")

    def _specificity_from_idx(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        tn = float(tn_arr[idx].sum())
        fp = float(fp_arr[idx].sum())
        # Undefined when the resample contains no reference-empty tile.
        # NOTE: a specificity of 0.0 with (tn + fp) > 0 is a *measured*
        # zero (every empty tile drew a false positive) and is preserved
        # as 0.0 — only the empty-denominator case is undefined.
        return tn / (tn + fp) if (tn + fp) > 0 else float("nan")

    indices = np.arange(n_tiles)
    mcc_ci = _bca_ci_from_indices(
        indices, _mcc_from_idx, n_iterations, random_seed,
        skip_undefined=True,
    )
    sens_ci = _bca_ci_from_indices(
        indices, _sensitivity_from_idx, n_iterations, random_seed,
        skip_undefined=True,
    )
    spec_ci = _bca_ci_from_indices(
        indices, _specificity_from_idx, n_iterations, random_seed,
        skip_undefined=True,
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
        # E81: these were hard-coded to ``n_iterations`` while degenerate
        # resamples were being scored as 0.0, so they asserted a validity
        # the numbers did not have. They now report the true count of
        # resamples on which each metric was defined.
        "n_valid_mcc": int(mcc_ci.get("n_valid", n_iterations)),
        "n_valid_sensitivity": int(sens_ci.get("n_valid", n_iterations)),
        "n_valid_specificity": int(spec_ci.get("n_valid", n_iterations)),
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
    tile_join: str = TILE_JOIN_DEFAULT,
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
        tile_join: One of :data:`TILE_JOINS`; applied to both conditions
            so a paired comparison never pairs a name-joined confusion
            against a geometry-joined one.

    Returns:
        Effect size CIs for MCC, sensitivity, and specificity differences.
        If either condition's tile join is refused, the refusal dict is
        returned instead, with ``condition`` naming which side failed.
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

    # A footprint smaller than a condition's frame is a reduced frame of it,
    # attributed as that frame attributes (ruling D59).
    result_a_full = calculate_tile_classification(
        gdf_det_a, gdf_ref, common_bounds_a, tile_join=tile_join,
        parent_bounds=_parent_of_cut(gdf_bounds_a, common_bounds_a),
    )
    result_b_full = calculate_tile_classification(
        gdf_det_b, gdf_ref, common_bounds_b, tile_join=tile_join,
        parent_bounds=_parent_of_cut(gdf_bounds_b, common_bounds_b),
    )
    for label, result in (("A", result_a_full), ("B", result_b_full)):
        if "error" in result:
            refused = dict(result)
            refused["condition"] = label
            return refused

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
