#!/usr/bin/env python3
# ============================================================================
# paired_mcc_permutation.py
# ----------------------------------------------------------------------------
# Paired tile-level permutation test for the difference in Matthews Correlation
# Coefficient (MCC) between two detection conditions.
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# ``results/e43-matched-temperature/findings.md`` § 11.2 reported that
# tile-level MCC separates the matched T=0.7 and T=1.0 arms in T=1.0's favour
# with non-overlapping bias-corrected and accelerated (BCa) 95 % bootstrap
# intervals, and flagged the comparison as UNPAIRED: two per-condition
# bootstraps are suggestive, but they are not a p-value. This script supplies
# the paired test, so a ΔMCC claim can be made rather than merely noted.
#
# WHAT IT DOES *NOT* REIMPLEMENT, AND WHY
# ---------------------------------------
# The permutation kernel already exists and is in production use:
# ``pairwise_permutation_test.run_permutation_test_mcc`` (added 2026-04-25,
# commit ``62d1173af``; called by ``build_tiered_leaderboard.py`` and
# ``build_cross_architecture_tables.py``). It performs exactly the required
# test — for each tile the full (TP, TN, FP, FN) one-hot 4-tuple is swapped
# between the two arms with probability 0.5, the aggregate MCC is recomputed,
# and the two-sided p-value is the fraction of permutations whose |ΔMCC|
# equals or exceeds the observed |ΔMCC|. It is NOT exposed on that script's
# command line (the CLI runs the F1 sibling only), which is why the § 11.2
# caveat read "no paired MCC permutation test was run".
#
# Duplicating a tested statistical kernel would invite drift between two
# implementations of the same house metric. This script therefore supplies the
# missing pieces around it: a command-line front end, a hard per-arm validation
# gate, batch execution over a job file, and a ladder-shaped summary.
#
# THE VALIDATION GATE (hard — the script refuses to test an arm that fails)
# ------------------------------------------------------------------------
# Per-tile labels are produced by ``lib_advanced_metrics``'s own
# ``compute_per_tile_classification`` (a thin per-tile view over
# ``calculate_tile_classification``), so they cannot drift from the house
# definition. The gate then proves it end to end: the per-tile labels are
# aggregated and compared against the TP/TN/FP/FN and MCC point estimate
# RECORDED in one or more on-disk ``evaluation.json`` files for that same cell.
# Any disagreement raises ``ConfusionGateError`` and the pair is not tested.
#
# BUFFER INDEPENDENCE — IMPORTANT
# -------------------------------
# House tile classification asks two buffer-free questions per tile: does the
# tile intersect any ground-truth mound, and did the arm emit any detection
# assigned to that tile? No spatial matching tolerance enters. Tile-level MCC
# is therefore INVARIANT to the F1 buffer, and a "20 m ΔMCC" and a "30 m ΔMCC"
# are the same number by construction. The script takes no buffer argument;
# it reports the invariance explicitly so callers do not mistake one test for
# two.
#
# DRY-RUN BY DEFAULT — the gates and the observed ΔMCC (both deterministic)
# run, the 10,000 permutations and all writes do not. Pass --execute for the
# full test.
#
# Usage — job file (the ladder):
#   .venv/bin/python scripts/paired_mcc_permutation.py \
#       --jobs planning/paired-mcc-jobs/e72-temperature-ladder-2026-08-03.json \
#       --output-dir results/e43-matched-temperature/paired-mcc --execute
#
# Usage — a single ad-hoc pair:
#   .venv/bin/python scripts/paired_mcc_permutation.py \
#       --pair-id t07-vs-t10-n10 \
#       --label-a "T=0.7 10-of-10" --geojson-a outputs/.../consensus_t10.geojson \
#       --expect-a results/.../t07-n10-10of10/evaluation.json \
#       --label-b "T=1.0 9-of-10"  --geojson-b outputs/.../consensus_t9.geojson \
#       --expect-b results/.../t10-n10-9of10/evaluation.json \
#       --output-dir results/e43-matched-temperature/paired-mcc --execute
#
# Zero application programming interface (API) calls. All computation is local.
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-08-03 | Apache 2.0
# ============================================================================
"""Paired tile-level permutation test for ΔMCC between two detection arms.

Public entry points:
    - :func:`load_detections` — load a detection GeoJSON and give every
      feature a ``source_tile``, mirroring ``evaluate_detections.py``.
    - :func:`aggregate_confusion` — per-tile labels aggregated to a
      TP/TN/FP/FN table plus the MCC point estimate.
    - :func:`expected_from_evaluation` — read the recorded confusion cells
      out of an ``evaluation.json``.
    - :func:`check_confusion_gate` — hard gate; raises
      :class:`ConfusionGateError` on any disagreement.
    - :func:`run_pair` — gate both arms, then run the paired ΔMCC
      permutation test.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd

# Ensure scripts/ is importable for sibling modules.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_classification,
)
from pairwise_permutation_test import (  # noqa: E402
    compute_mcc_or_none,
    run_permutation_test_mcc,
)

__version__ = "1.0.0"

logger = logging.getLogger(__name__)

REPO = _SCRIPT_DIR.parent
_VECTORS_DIR = REPO / "inputs" / "vectors"
DEFAULT_BOUNDS = _VECTORS_DIR / "bounds" / "384" / "full_evaluation_bounds.geojson"
DEFAULT_GROUND_TRUTH = _VECTORS_DIR / "references" / "mounds-reference.geojson"
TARGET_CRS = "EPSG:32635"

DEFAULT_N_PERMUTATIONS = 10_000
DEFAULT_SEED = 42

#: Tolerance for comparing a recomputed MCC against a recorded one. The
#: recorded value is rounded to 4 decimal places by ``evaluate_detections.py``,
#: so anything tighter than half a unit in the last place would fail on
#: rounding alone.
MCC_TOLERANCE = 5e-5

#: Rendered wherever the tile-level MCC is not computable (erratum E81).
#: Matches ``evaluate_detections.UNDEFINED_DISPLAY``.
UNDEFINED_DISPLAY = "undefined"


def _safe_round(val: float | None, digits: int = 6) -> float | None:
    """Round a possibly-undefined MCC, preserving ``None``.

    Args:
        val: The value, or ``None`` when the coefficient is undefined.
        digits: Decimal places.

    Returns:
        The rounded float, or ``None``. Erratum E81: ``None`` must
        reach the JSON as ``null``, never as 0.0.
    """
    return None if val is None else round(val, digits)


def _delta(a: float | None, b: float | None) -> float | None:
    """Difference ``a - b``, propagating undefinedness.

    Args:
        a: Arm A's MCC, or ``None`` when undefined.
        b: Arm B's MCC, or ``None`` when undefined.

    Returns:
        ``a - b``, or ``None`` when either arm's coefficient is
        undefined — a ΔMCC measured against a non-measurement is not
        itself a measurement (erratum E81).
    """
    if a is None or b is None:
        return None
    return a - b


def _fmt_mcc(val: float | None, width: int = 8, digits: int = 4) -> str:
    """Right-align a possibly-undefined MCC for a console column.

    Args:
        val: The coefficient, or ``None`` when undefined.
        width: Column width.
        digits: Decimal places for the numeric case.

    Returns:
        The formatted number, or :data:`UNDEFINED_DISPLAY`, padded to
        ``width``. A genuine zero still renders as ``'0.0000'``.
    """
    if val is None:
        return f"{UNDEFINED_DISPLAY:>{width}s}"
    return f"{val:{width}.{digits}f}"


class ConfusionGateError(RuntimeError):
    """Raised when recomputed per-tile confusion cells do not reproduce.

    The gate exists so that a ΔMCC p-value can never be reported against
    per-tile labels that disagree with the cell's filed evaluation. It is a
    hard failure by design: a silent disagreement would mean the test and the
    published MCC table describe different data.
    """


# -----------------------------------------------
# Loading
# -----------------------------------------------

def load_geojson(path: Path, target_crs: str = TARGET_CRS) -> gpd.GeoDataFrame:
    """Load a GeoJSON and reproject it to the evaluation CRS.

    Mirrors ``evaluate_detections.load_geojson`` so that geometry handling
    is identical to the harness that produced the recorded evaluations.

    Args:
        path: Path to the GeoJSON file.
        target_crs: Coordinate Reference System (CRS) to work in
            (default ``EPSG:32635``, Universal Transverse Mercator zone 35N).

    Returns:
        GeoDataFrame in ``target_crs``.
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


def load_detections(
    path: Path,
    gdf_bounds: gpd.GeoDataFrame,
    target_crs: str = TARGET_CRS,
) -> gpd.GeoDataFrame:
    """Load a detection GeoJSON and ensure every feature has a ``source_tile``.

    Consensus artefacts carry a plural ``source_tiles`` list (one entry per
    contributing pass) but no singular ``source_tile``, so tile assignment
    falls to a spatial join. The join replicates
    ``evaluate_detections.py`` exactly — ``how="left"``,
    ``predicate="intersects"``, first match kept per detection — because 384 px
    tiles overlap their neighbours by 48 px and a detection in the overlap
    intersects two tiles. Keeping the first match is what the published
    evaluations did; any other rule would move the confusion cells.

    Args:
        path: Detection GeoJSON path.
        gdf_bounds: Evaluation bounds with a ``tile_name`` column.
        target_crs: CRS to work in.

    Returns:
        GeoDataFrame with ``source_tile`` and ``geometry`` columns.
    """
    gdf_det = load_geojson(path, target_crs=target_crs)
    if "source_tile" not in gdf_det.columns and not gdf_det.empty:
        joined = gpd.sjoin(
            gdf_det, gdf_bounds[["tile_name", "geometry"]],
            how="left", predicate="intersects",
        )
        joined = joined[~joined.index.duplicated(keep="first")]
        gdf_det["source_tile"] = joined["tile_name"]
    return gdf_det


# -----------------------------------------------
# Confusion reproduction gate
# -----------------------------------------------

def aggregate_confusion(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict:
    """Aggregate per-tile classifications into a confusion table plus MCC.

    Uses ``lib_advanced_metrics.compute_per_tile_classification``, the same
    per-tile view the permutation kernel consumes, so a passing gate certifies
    the *test's own* labels rather than a parallel recomputation.

    Args:
        gdf_det: Detections with a ``source_tile`` column.
        gdf_ref: Ground-truth references.
        gdf_bounds: Evaluation bounds with a ``tile_name`` column.

    Returns:
        Dict with ``tp``, ``tn``, ``fp``, ``fn``, ``n_tiles`` and
        ``mcc``, where ``mcc`` is ``None`` when the 2 x 2 table is
        degenerate (erratum E81, 2026-08-18). It used to be 0.0 in two
        places — an empty per-tile frame, and any zero-denominator
        table via ``_compute_mcc`` — which published a coefficient
        that was never computable at the value § 4.2 of the
        preregistration reads as chance.

    Example:
        >>> cells = aggregate_confusion(det, ref, bounds)  # doctest: +SKIP
        >>> cells["tp"] + cells["tn"] + cells["fp"] + cells["fn"]  # doctest: +SKIP
        487
    """
    per_tile = compute_per_tile_classification(gdf_det, gdf_ref, gdf_bounds)
    if per_tile.empty:
        # No tiles at all: the confusion table does not exist, so the
        # coefficient is undefined rather than zero.
        return {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "n_tiles": 0,
                "mcc": None}
    tp = int(per_tile["tp"].sum())
    tn = int(per_tile["tn"].sum())
    fp = int(per_tile["fp"].sum())
    fn = int(per_tile["fn"].sum())
    return {
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "n_tiles": int(len(per_tile)),
        "mcc": compute_mcc_or_none(tp, tn, fp, fn),
    }


def expected_from_evaluation(eval_path: Path) -> dict:
    """Read the recorded tile-classification cells out of an evaluation.json.

    Args:
        eval_path: Path to an ``evaluation.json`` written by
            ``evaluate_detections.py`` with ``--mcc``.

    Returns:
        Dict with ``tp``, ``tn``, ``fp``, ``fn``, ``mcc``,
        ``mcc_recorded`` and ``n_detections``.

        ``mcc`` may be ``None`` for two quite different reasons, which
        erratum E81 makes it essential to separate: the evaluation may
        predate the ``point`` field (nothing recorded — nothing to
        gate against), or it may record the coefficient as JSON
        ``null`` (recorded, and recorded as *undefined* — which the
        gate must enforce). ``mcc_recorded`` is ``True`` only in the
        second case, i.e. when the ``point`` key is present.

    Raises:
        ConfusionGateError: if the file carries no tile-classification block,
            which means it was scored without ``--mcc`` and cannot gate.
    """
    with open(eval_path, encoding="utf-8") as handle:
        payload = json.load(handle)
    summary = payload.get("summary", {})
    tile_class = summary.get("tile_classification")
    if not tile_class or "confusion" not in tile_class:
        raise ConfusionGateError(
            f"{eval_path} carries no tile_classification block — it was "
            "scored without --mcc and cannot serve as a gate reference.",
        )
    confusion = tile_class["confusion"]
    mcc_block = tile_class.get("mcc") or {}
    return {
        "tp": int(confusion["tp"]),
        "tn": int(confusion["tn"]),
        "fp": int(confusion["fp"]),
        "fn": int(confusion["fn"]),
        "mcc": mcc_block.get("point"),
        # Key presence, not truthiness: a recorded ``null`` is an
        # assertion that the coefficient is undefined and must be
        # gated on; an absent key is simply nothing to gate against.
        "mcc_recorded": "point" in mcc_block,
        "n_detections": summary.get("n_detections"),
        "source": str(eval_path),
    }


def check_confusion_gate(
    observed: dict,
    expected: dict,
    label: str,
    n_detections: int | None = None,
    mcc_tolerance: float = MCC_TOLERANCE,
) -> dict:
    """Assert that recomputed confusion cells reproduce a recorded evaluation.

    Three checks, all hard:

    1. the four confusion cells match exactly;
    2. the recomputed MCC agrees with the recorded point estimate — first
       on **definedness** (both defined, or both undefined; a mismatch is
       a failure), then, when both are defined, on value within
       ``mcc_tolerance`` (the recorded value is stored rounded to 4 dp).
       Erratum E81: an evaluation that records the coefficient as
       ``null`` still gates, rather than skipping the check;
    3. where both are available, the detection GeoJSON's feature count matches
       the evaluation's ``n_detections`` — the cross-check that caught three
       wrong-source errors retrospectively in an earlier session, and the
       cheapest guard against gating an arm on another cell's numbers.

    Args:
        observed: Output of :func:`aggregate_confusion`.
        expected: Output of :func:`expected_from_evaluation`.
        label: Human-readable arm label, used in the error message.
        n_detections: Feature count of the arm's detection GeoJSON, or
            ``None`` to skip check 3.
        mcc_tolerance: Absolute tolerance for the MCC comparison.

    Returns:
        A dict recording what was checked, for the output provenance block.

    Raises:
        ConfusionGateError: on any disagreement.
    """
    failures: list[str] = []
    for cell in ("tp", "tn", "fp", "fn"):
        if observed[cell] != expected[cell]:
            failures.append(
                f"{cell.upper()}: recomputed {observed[cell]} != "
                f"recorded {expected[cell]}",
            )

    # Erratum E81: this used to be ``if recorded_mcc is not None:``,
    # which meant a cell recording an *undefined* MCC (JSON ``null``)
    # skipped the MCC check entirely — the gate weakened silently
    # exactly where the record was most fragile. The check is now on
    # DEFINEDNESS first: whenever the evaluation recorded a value at
    # all, the recomputation must agree about whether the coefficient
    # exists, and only then about what it is.
    recorded_mcc = expected.get("mcc")
    observed_mcc = observed["mcc"]
    mcc_recorded = expected.get("mcc_recorded", recorded_mcc is not None)
    if mcc_recorded:
        if recorded_mcc is None and observed_mcc is not None:
            failures.append(
                f"MCC: the evaluation records the coefficient as "
                f"{UNDEFINED_DISPLAY} (degenerate tile confusion matrix) "
                f"but the recomputation gives {observed_mcc:.6f}",
            )
        elif recorded_mcc is not None and observed_mcc is None:
            failures.append(
                f"MCC: the recomputation gives {UNDEFINED_DISPLAY} "
                "(degenerate tile confusion matrix) but the evaluation "
                f"records {float(recorded_mcc):.6f}",
            )
        elif recorded_mcc is not None and observed_mcc is not None:
            delta = abs(observed_mcc - float(recorded_mcc))
            if delta > mcc_tolerance:
                failures.append(
                    f"MCC: recomputed {observed_mcc:.6f} != recorded "
                    f"{float(recorded_mcc):.6f} (|Δ| = {delta:.2e} > "
                    f"{mcc_tolerance:.0e})",
                )
        # Both ``None`` — recomputation and record agree that the
        # coefficient is undefined. That is a PASS, and reaching it
        # required the check above rather than a skip.

    recorded_n = expected.get("n_detections")
    if n_detections is not None and recorded_n is not None:
        if int(n_detections) != int(recorded_n):
            failures.append(
                f"n_detections: GeoJSON has {n_detections} features but "
                f"the evaluation records {recorded_n} — wrong source file?",
            )

    if failures:
        raise ConfusionGateError(
            f"Confusion-cell gate FAILED for '{label}' against "
            f"{expected.get('source', '<unknown>')}:\n  - "
            + "\n  - ".join(failures),
        )

    return {
        "reference": expected.get("source"),
        "confusion_matched": True,
        # ``mcc_matched`` now means "the MCC check ran and passed",
        # which includes the both-undefined case. ``mcc_defined``
        # records which of the two agreements it was, so a provenance
        # reader can tell a matched number from a matched
        # non-measurement (erratum E81).
        "mcc_matched": bool(mcc_recorded),
        "mcc_defined": (
            None if not mcc_recorded else observed_mcc is not None
        ),
        "n_detections_matched": (
            n_detections is not None and recorded_n is not None
        ),
    }


# -----------------------------------------------
# The paired test
# -----------------------------------------------

def _gate_arm(
    geojson_path: Path,
    expect_paths: list[Path],
    label: str,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, dict, list[dict]]:
    """Load one arm and run the confusion gate against every reference given.

    Args:
        geojson_path: The arm's detection GeoJSON.
        expect_paths: One or more ``evaluation.json`` files for the same
            cell. Every one is checked; more references means a stronger gate.
        label: Human-readable arm label.
        gdf_ref: Ground-truth references.
        gdf_bounds: Evaluation bounds.

    Returns:
        Tuple of (detections GeoDataFrame, observed confusion dict, list of
        per-reference gate records).

    Raises:
        ConfusionGateError: if no reference was supplied, or any check fails.
    """
    if not expect_paths:
        raise ConfusionGateError(
            f"No gate reference supplied for '{label}'. The gate is "
            "mandatory: pass at least one evaluation.json.",
        )
    gdf_det = load_detections(geojson_path, gdf_bounds)
    observed = aggregate_confusion(gdf_det, gdf_ref, gdf_bounds)
    records = []
    for expect_path in expect_paths:
        expected = expected_from_evaluation(Path(expect_path))
        records.append(
            check_confusion_gate(
                observed, expected, label, n_detections=len(gdf_det),
            ),
        )
    logger.info(
        "  GATE PASSED %-42s TP/TN/FP/FN %d/%d/%d/%d  MCC %s  "
        "(%d reference%s)",
        label, observed["tp"], observed["tn"], observed["fp"],
        observed["fn"], _fmt_mcc(observed["mcc"], width=0), len(records),
        "" if len(records) == 1 else "s",
    )
    return gdf_det, observed, records


def run_pair(
    job: dict,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_permutations: int = DEFAULT_N_PERMUTATIONS,
    seed: int = DEFAULT_SEED,
    permute: bool = True,
) -> dict:
    """Gate both arms of a pair, then run the paired ΔMCC permutation test.

    Δ is reported as ``MCC(A) − MCC(B)``, so the sign convention is the
    caller's to choose through the ordering of the job's arms.

    Args:
        job: Job dict with keys ``pair_id``, ``label_a``, ``geojson_a``,
            ``expect_a`` (str or list), ``label_b``, ``geojson_b``,
            ``expect_b``, and optionally ``note``.
        gdf_ref: Ground-truth references.
        gdf_bounds: Evaluation bounds.
        n_permutations: Permutation iterations.
        seed: Random seed.
        permute: If False, gate and report the observed ΔMCC only (dry-run).

    Returns:
        Result dict with the gate records, the observed MCCs and ΔMCC, and —
        when ``permute`` is True — the permutation test block.
    """
    def _as_paths(value) -> list[Path]:
        if value is None:
            return []
        if isinstance(value, (str, Path)):
            return [Path(value)]
        return [Path(v) for v in value]

    logger.info("Pair %s: %s  vs  %s",
                job["pair_id"], job["label_a"], job["label_b"])

    gdf_a, conf_a, gate_a = _gate_arm(
        Path(job["geojson_a"]), _as_paths(job.get("expect_a")),
        job["label_a"], gdf_ref, gdf_bounds,
    )
    gdf_b, conf_b, gate_b = _gate_arm(
        Path(job["geojson_b"]), _as_paths(job.get("expect_b")),
        job["label_b"], gdf_ref, gdf_bounds,
    )

    result = {
        "pair_id": job["pair_id"],
        "note": job.get("note"),
        "metric": "tile_level_mcc",
        "buffer_invariance": (
            "Tile-level MCC is computed from buffer-free tile labels "
            "(tile intersects ground truth? arm emitted a detection in "
            "tile?), so this ΔMCC is identical at every F1 buffer, "
            "including 20 m and 30 m."
        ),
        "arm_a": {
            "label": job["label_a"],
            "geojson": str(job["geojson_a"]),
            "n_detections": int(len(gdf_a)),
            "confusion": {k: conf_a[k] for k in ("tp", "tn", "fp", "fn")},
            "mcc": _safe_round(conf_a["mcc"]),
            "gate": gate_a,
        },
        "arm_b": {
            "label": job["label_b"],
            "geojson": str(job["geojson_b"]),
            "n_detections": int(len(gdf_b)),
            "confusion": {k: conf_b[k] for k in ("tp", "tn", "fp", "fn")},
            "mcc": _safe_round(conf_b["mcc"]),
            "gate": gate_b,
        },
        "observed_mcc_diff": _safe_round(
            _delta(conf_a["mcc"], conf_b["mcc"]),
        ),
    }

    if not permute:
        result["permutation_test"] = None
        return result

    # Erratum E81: with either arm's coefficient undefined there is no
    # observed ΔMCC, so there is no statistic for the null to be a null
    # OF. Running the kernel anyway would silently substitute its
    # internal 0.0 convention for the missing arm and return a p-value
    # for a comparison that was never made — the exact defect E81
    # exists to stop. The pair is reported as undefined instead.
    if result["observed_mcc_diff"] is None:
        logger.warning(
            "  Pair %s: tile MCC is %s for at least one arm (A=%s, B=%s) "
            "— the 2 x 2 tile confusion matrix is degenerate. No ΔMCC "
            "and no permutation test; the pair is reported as %s rather "
            "than tested against a substituted zero (erratum E81).",
            job["pair_id"], UNDEFINED_DISPLAY,
            _fmt_mcc(conf_a["mcc"], width=0),
            _fmt_mcc(conf_b["mcc"], width=0), UNDEFINED_DISPLAY,
        )
        result["permutation_test"] = None
        result["mcc_undefined"] = True
        result["mcc_undefined_note"] = (
            "Tile-level MCC is undefined for at least one arm "
            "(degenerate 2 x 2 tile confusion matrix), so ΔMCC and its "
            "permutation p-value do not exist for this pair. Erratum "
            "E81: not reported as 0."
        )
        return result

    perm = run_permutation_test_mcc(
        gdf_a, gdf_b, gdf_ref, gdf_bounds,
        n_permutations=n_permutations, seed=seed,
    )
    # Cross-check: the kernel's own observed ΔMCC must equal the gated one.
    kernel_diff = perm["permutation_test"]["observed_mcc_diff"]
    if abs(kernel_diff - result["observed_mcc_diff"]) > 1e-9:
        raise ConfusionGateError(
            f"Pair {job['pair_id']}: permutation kernel reports ΔMCC "
            f"{kernel_diff} but the gated arms give "
            f"{result['observed_mcc_diff']}.",
        )
    result["permutation_test"] = perm["permutation_test"]
    # Keep the per-tile classification pair on the per-pair artefact so a
    # reader can re-derive the test without re-running the spatial joins.
    # The batch summary strips it (see ``main``) to stay readable.
    result["per_tile"] = perm["per_tile"]
    logger.info(
        "  ΔMCC = %+.4f   p = %.4f   (%d permutations, seed %d)",
        kernel_diff, perm["permutation_test"]["p_value"],
        n_permutations, seed,
    )
    return result


# -----------------------------------------------
# Command line
# -----------------------------------------------

def _jobs_from_args(args: argparse.Namespace) -> list[dict]:
    """Assemble the job list from either --jobs or the single-pair flags.

    Args:
        args: Parsed command-line arguments.

    Returns:
        List of job dicts.

    Raises:
        SystemExit: if neither input form is complete.
    """
    if args.jobs:
        with open(args.jobs, encoding="utf-8") as handle:
            payload = json.load(handle)
        jobs = payload["jobs"] if isinstance(payload, dict) else payload
        return list(jobs)

    required = (args.geojson_a, args.geojson_b, args.expect_a, args.expect_b)
    if not all(required):
        raise SystemExit(
            "Supply either --jobs, or all of --geojson-a/--geojson-b/"
            "--expect-a/--expect-b (the gate references are mandatory).",
        )
    return [{
        "pair_id": args.pair_id,
        "label_a": args.label_a,
        "geojson_a": str(args.geojson_a),
        "expect_a": [str(p) for p in args.expect_a],
        "label_b": args.label_b,
        "geojson_b": str(args.geojson_b),
        "expect_b": [str(p) for p in args.expect_b],
    }]


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    Returns:
        Configured :class:`argparse.ArgumentParser`.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Paired tile-level permutation test for ΔMCC between two "
            "detection conditions. Dry-run by default."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--jobs", type=Path,
        help="JSON job file: a list of pairs, or {'jobs': [...]}.",
    )
    parser.add_argument("--pair-id", type=str, default="pair")
    parser.add_argument("--label-a", type=str, default="Condition A")
    parser.add_argument("--label-b", type=str, default="Condition B")
    parser.add_argument("--geojson-a", type=Path)
    parser.add_argument("--geojson-b", type=Path)
    parser.add_argument(
        "--expect-a", type=Path, nargs="+",
        help="One or more evaluation.json gate references for arm A.",
    )
    parser.add_argument(
        "--expect-b", type=Path, nargs="+",
        help="One or more evaluation.json gate references for arm B.",
    )
    parser.add_argument(
        "--bounds", type=Path, default=DEFAULT_BOUNDS,
        help=f"Evaluation bounds GeoJSON (default: {DEFAULT_BOUNDS.name}).",
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=DEFAULT_GROUND_TRUTH,
        help=f"Ground-truth GeoJSON (default: {DEFAULT_GROUND_TRUTH.name}).",
    )
    parser.add_argument(
        "--n-permutations", type=int, default=DEFAULT_N_PERMUTATIONS,
        help=f"Permutation iterations (default: {DEFAULT_N_PERMUTATIONS:,}).",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
        help=f"Random seed (default: {DEFAULT_SEED}).",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        help="Directory for per-pair JSON results and the summary.",
    )
    parser.add_argument(
        "--execute", action="store_true",
        help=(
            "Run the permutations and write results. Without it the script "
            "gates the arms, prints the observed ΔMCC, and writes nothing."
        ),
    )
    parser.add_argument("--quiet", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Dry-run by default; ``--execute`` permutes and writes.

    Args:
        argv: Optional argument vector (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code: 0 on success, 1 if any gate failed.
    """
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(message)s",
    )

    jobs = _jobs_from_args(args)
    logger.info(
        "Loading bounds  %s\nLoading ground truth %s",
        args.bounds, args.ground_truth,
    )
    gdf_bounds = load_geojson(args.bounds)
    gdf_ref = load_geojson(args.ground_truth)
    logger.info(
        "%d tiles, %d reference mounds, %d pair(s), %s\n",
        len(gdf_bounds), len(gdf_ref), len(jobs),
        "EXECUTE" if args.execute else "DRY-RUN",
    )

    results = []
    for job in jobs:
        try:
            results.append(run_pair(
                job, gdf_ref, gdf_bounds,
                n_permutations=args.n_permutations,
                seed=args.seed,
                permute=args.execute,
            ))
        except ConfusionGateError as exc:
            logger.error("GATE FAILURE\n%s", exc)
            return 1

    payload = {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "metric": "tile_level_mcc",
        "test": (
            "paired tile-swap permutation test; each tile's (TP, TN, FP, FN) "
            "one-hot 4-tuple is swapped between arms with probability 0.5 and "
            "the aggregate MCC recomputed; two-sided p = fraction of "
            "permutations with |ΔMCC| >= |observed ΔMCC|"
        ),
        "kernel": "pairwise_permutation_test.run_permutation_test_mcc",
        "n_permutations": args.n_permutations,
        "seed": args.seed,
        "bounds": str(args.bounds),
        "ground_truth": str(args.ground_truth),
        "n_tiles": int(len(gdf_bounds)),
        "executed": bool(args.execute),
        "pairs": results,
    }

    if args.execute and args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for result in results:
            out = args.output_dir / f"{result['pair_id']}.json"
            with open(out, "w", encoding="utf-8") as handle:
                json.dump(result, handle, indent=2)
            logger.info("Wrote %s", out)
        summary_path = args.output_dir / "paired_mcc_summary.json"
        slim = dict(payload)
        slim["pairs"] = [
            {k: v for k, v in r.items() if k != "per_tile"} for r in results
        ]
        with open(summary_path, "w", encoding="utf-8") as handle:
            json.dump(slim, handle, indent=2)
        logger.info("Wrote %s", summary_path)
    elif not args.execute:
        logger.info(
            "\nDRY-RUN: gates passed, no permutations run, nothing written. "
            "Re-run with --execute.",
        )

    if not args.quiet:
        print("\n" + "=" * 78)
        print(f"{'pair':28s} {'MCC A':>8s} {'MCC B':>8s} {'ΔMCC':>9s} {'p':>8s}")
        print("=" * 78)
        for result in results:
            perm = result.get("permutation_test") or {}
            p_str = (
                f"{perm['p_value']:.4f}" if "p_value" in perm else "  (dry)"
            )
            # Erratum E81: an undefined arm MCC (or the ΔMCC that
            # cannot be formed from one) prints the word, not a number.
            diff = result["observed_mcc_diff"]
            diff_str = (
                f"{UNDEFINED_DISPLAY:>9s}" if diff is None
                else f"{diff:+9.4f}"
            )
            print(
                f"{result['pair_id']:28s} "
                f"{_fmt_mcc(result['arm_a']['mcc'])} "
                f"{_fmt_mcc(result['arm_b']['mcc'])} "
                f"{diff_str} {p_str:>8s}",
            )
        print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
