#!/usr/bin/env python3
"""
Derive tile-level precision, recall, and F1 as a supplemental discrimination metric.

Purpose
-------
The project's registered tile-level discrimination metric is the Matthews
Correlation Coefficient (MCC) over a 2 x 2 tile confusion matrix (preregistration
Section 4.2). The only published Vision Language Model (VLM) archaeological
detection study — Landauer & Klassen (2025), DOI 10.3390/geomatics5040052 — scored
its models with per-tile binary classification and reported precision, recall, and
F1 rather than MCC. To compare on a like protocol, this script derives tile-level
P/R/F1 from **exactly the same committed tile confusion matrices** that back the
committed MCC values, and tabulates the Landauer & Klassen confusion cells beside
them.

Design constraints (from ``docs/methodology/tile-mcc-explained.md``)
-------------------------------------------------------------------
1. **Same matrix, same booking rules.** No re-scoring is performed. The confusion
   counts are read verbatim from the committed ``evaluation.json`` artefacts, so
   the two axes keep their documented booking rules (detections booked to one tile
   under the E79 nearest-centroid rule; references booked to every tile they
   intersect). Re-deriving reference occupancy from the detection-level
   false-negative column is the documented Trap 1 and is not done here.
2. **Undefined is not zero.** A vanishing marginal makes the corresponding
   statistic undefined. Undefined values are emitted as JSON ``null`` with a
   machine-readable reason string, never as ``0.0`` (Trap 2, erratum E81).
3. **Tiling scope is carried with the number.** Every cell records its carrier
   grid (tile size, stride, footprint, tile count), because tile-level statistics
   computed on different tilings are not comparable (Trap 3).

Validation gate
---------------
For every cell, MCC is recomputed from the confusion matrix and required to
reproduce the committed ``mcc.point`` value to at least four decimal places before
any P/R/F1 is emitted for that cell. A cell failing the gate is reported as
``gate_passed: false`` and its derived metrics are withheld.

Usage
-----
Dry run (default — prints the table, writes nothing)::

    python scripts/derive_tile_level_f1.py

Emit the JSON artefact::

    python scripts/derive_tile_level_f1.py --write

Cost: zero. All inputs are committed JSON artefacts on disk; no Application
Programming Interface (API) calls and no geometry work are performed.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "tile-level-f1"
#: Reference revision r2 (planning/reference-revision-2026-09-06.md, step 5):
#: the eight 55-map cells re-derived from their r2 evaluations
#: (results/55maps-r2-ref-2026-09-06/<cell>/evaluation.json, -r2-gt rows).
#: The GS cells are unchanged -- r2 does not touch the GS reference.
R2_SCORING_HOME = "results/55maps-r2-ref-2026-09-06"
R2_OUTPUT_DIR = PROJECT_ROOT / "results" / "tile-level-f1-r2"
R2_BOARD_ID = "55map-r2-leaderboard-50m"
OUTPUT_FILENAME = "tile_level_f1.json"

#: Tolerance for the MCC reproduction gate (four decimal places).
MCC_GATE_TOLERANCE = 1e-4

SCHEMA_VERSION = "1.0.0"
GENERATOR_VERSION = "0.1.0"


# =============================================================================
# Confusion-matrix arithmetic (undefined-aware)
# =============================================================================


@dataclass(frozen=True)
class Confusion:
    """A 2 x 2 tile confusion matrix.

    Attributes:
        tp: Tiles with at least one reference mound and at least one detection.
        fp: Tiles with no reference mound but at least one detection.
        fn: Tiles with at least one reference mound and no detection.
        tn: Tiles with no reference mound and no detection.
    """

    tp: int
    fp: int
    fn: int
    tn: int

    @property
    def n_tiles(self) -> int:
        """Total tiles on the carrier grid."""
        return self.tp + self.fp + self.fn + self.tn

    @property
    def predicted_positive(self) -> int:
        """Tiles the model flagged (TP + FP)."""
        return self.tp + self.fp

    @property
    def reference_positive(self) -> int:
        """Tiles the reference populates (TP + FN)."""
        return self.tp + self.fn

    @property
    def reference_negative(self) -> int:
        """Tiles the reference leaves empty (TN + FP)."""
        return self.tn + self.fp

    @property
    def predicted_negative(self) -> int:
        """Tiles the model left unflagged (TN + FN)."""
        return self.tn + self.fn


def marginal_report(cm: Confusion) -> dict[str, int]:
    """Return the four marginals of a confusion matrix, named.

    Args:
        cm: The confusion matrix.

    Returns:
        Mapping of marginal name to count.
    """
    return {
        "tp_plus_fp": cm.predicted_positive,
        "tp_plus_fn": cm.reference_positive,
        "tn_plus_fp": cm.reference_negative,
        "tn_plus_fn": cm.predicted_negative,
    }


def vanishing_marginals(cm: Confusion) -> list[str]:
    """Name every marginal of ``cm`` that is zero.

    Args:
        cm: The confusion matrix.

    Returns:
        Sorted list of the names of the vanishing marginals; empty when all four
        marginals are non-zero.
    """
    return [name for name, value in marginal_report(cm).items() if value == 0]


def tile_precision(cm: Confusion) -> float | None:
    """Tile-level precision, or ``None`` when the predicted-positive column is empty.

    Args:
        cm: The confusion matrix.

    Returns:
        ``TP / (TP + FP)``, or ``None`` if undefined. Never ``0.0`` as a filler.
    """
    if cm.predicted_positive == 0:
        return None
    return cm.tp / cm.predicted_positive


def tile_recall(cm: Confusion) -> float | None:
    """Tile-level recall, or ``None`` when the reference-positive row is empty.

    Args:
        cm: The confusion matrix.

    Returns:
        ``TP / (TP + FN)``, or ``None`` if undefined.
    """
    if cm.reference_positive == 0:
        return None
    return cm.tp / cm.reference_positive


def tile_f1(cm: Confusion) -> float | None:
    """Tile-level F1, or ``None`` when precision or recall is undefined.

    A genuine ``0.0`` is returned when both marginals are non-zero but ``TP`` is
    zero: that is a defined result (the model flagged tiles, none of them
    populated), not a missing one.

    Args:
        cm: The confusion matrix.

    Returns:
        ``2·TP / (2·TP + FP + FN)``, or ``None`` if undefined.
    """
    if cm.predicted_positive == 0 or cm.reference_positive == 0:
        return None
    return (2 * cm.tp) / ((2 * cm.tp) + cm.fp + cm.fn)


def tile_mcc(cm: Confusion) -> float | None:
    """Matthews Correlation Coefficient, or ``None`` when any marginal vanishes.

    Mirrors ``lib_advanced_metrics.calculate_tile_classification`` exactly: an
    undefined MCC is ``None``, never ``0.0`` (erratum E81).

    Args:
        cm: The confusion matrix.

    Returns:
        The MCC of ``cm``, or ``None`` if undefined.
    """
    denominator = (
        cm.predicted_positive * cm.reference_positive * cm.reference_negative
        * cm.predicted_negative
    )
    if denominator == 0:
        return None
    return ((cm.tp * cm.tn) - (cm.fp * cm.fn)) / math.sqrt(denominator)


def prevalence(cm: Confusion) -> float | None:
    """Reference-positive tile share, ``(TP + FN) / N``.

    Args:
        cm: The confusion matrix.

    Returns:
        The share of tiles the reference populates, or ``None`` for an empty grid.
    """
    if cm.n_tiles == 0:
        return None
    return cm.reference_positive / cm.n_tiles


# =============================================================================
# Cell registry — committed artefacts only
# =============================================================================


@dataclass(frozen=True)
class CellSpec:
    """A cell whose committed tile confusion matrix is to be re-expressed as F1.

    Attributes:
        key: Short stable identifier used as the JSON key.
        display_name: Board label as published.
        board: The board or headline this cell belongs to.
        condition_id: Condition identifier in ``results/conditions-manifest.json``.
        evaluation_path: Committed evaluation artefact, relative to the project root.
        carrier: Human-readable description of the tiling scope (Trap 3).
        object_f1: Committed object-level (buffer-matched) F1, for context only.
        object_f1_buffer_m: Buffer radius in metres at which ``object_f1`` was scored.
    """

    key: str
    display_name: str
    board: str
    condition_id: str
    evaluation_path: str
    carrier: str
    object_f1: float
    object_f1_buffer_m: int


GS_CARRIER = "Era-2 gold standard: 384 px tiles, 336 px stride, 4 map sheets, 487 tiles"
M55_CARRIER = "55-map generalisation: 384 px tiles, Era-2-style bounds, 55 map sheets, 8,541 tiles"

CELLS: tuple[CellSpec, ...] = (
    CellSpec(
        key="gs-verified-adv-text-consensus-16of30",
        display_name="verified-adv-text-consensus-16of30",
        board="gold-standard headline",
        condition_id="pv-diag-384::verified-adv-text-consensus-16of30",
        evaluation_path="results/era1-pv-stage-d/384-consensus-text-high/evaluation.json",
        carrier=GS_CARRIER,
        object_f1=0.8902,
        object_f1_buffer_m=20,
    ),
    CellSpec(
        key="gs-verified-adv-image-baseline-pro-vf",
        display_name="verified-adv-image-baseline-pro-vf",
        board="gold-standard MCC crown",
        condition_id="pv-diag-384::verified-adv-image-baseline-pro-vf",
        evaluation_path=(
            "results/verifier-robustness/evals/verified-adv-image-baseline-pro-vf/"
            "evaluation.json"
        ),
        carrier=GS_CARRIER,
        object_f1=0.7309,
        object_f1_buffer_m=20,
    ),
    CellSpec(
        key="55map-T03-k3",
        display_name="T03-k3 (oracle)",
        board="55map-canonical-leaderboard-50m",
        condition_id="55maps-text-high-t0-3-generalisation::verified-k3-canonical-gt",
        evaluation_path="results/55maps-extended-gt-2026-06-07/T03-k3/evaluation.json",
        carrier=M55_CARRIER,
        object_f1=0.8476,
        object_f1_buffer_m=50,
    ),
    CellSpec(
        key="55map-TH7-k3",
        display_name="TH7-k3",
        board="55map-canonical-leaderboard-50m",
        condition_id="55maps-text-high-generalisation::verified-k3-canonical-gt",
        evaluation_path="results/55maps-extended-gt-2026-06-07/TH7-k3/evaluation.json",
        carrier=M55_CARRIER,
        object_f1=0.8425,
        object_f1_buffer_m=50,
    ),
    CellSpec(
        key="55map-T03-k4",
        display_name="T03-k4",
        board="55map-canonical-leaderboard-50m",
        condition_id="55maps-text-high-t0-3-generalisation::verified-k4-canonical-gt",
        evaluation_path="results/55maps-extended-gt-2026-06-07/T03-k4/evaluation.json",
        carrier=M55_CARRIER,
        object_f1=0.8359,
        object_f1_buffer_m=50,
    ),
    CellSpec(
        key="55map-TM-n10-k5",
        display_name="TM-n10-k5 (uplift)",
        board="55map-canonical-leaderboard-50m",
        condition_id="55maps-text-min-n10-uplift::verified-5of10-canonical-gt",
        evaluation_path="results/55maps-extended-gt-2026-06-07/TM-n10-k5/evaluation.json",
        carrier=M55_CARRIER,
        object_f1=0.8290,
        object_f1_buffer_m=50,
    ),
    CellSpec(
        key="55map-TH7-k4",
        display_name="TH7-k4 (carry-forward)",
        board="55map-canonical-leaderboard-50m",
        condition_id="55maps-text-high-generalisation::verified-k4-canonical-gt",
        evaluation_path="results/55maps-extended-gt-2026-06-07/TH7-k4/evaluation.json",
        carrier=M55_CARRIER,
        object_f1=0.8152,
        object_f1_buffer_m=50,
    ),
    CellSpec(
        key="55map-TM-k3",
        display_name="TM-k3",
        board="55map-canonical-leaderboard-50m",
        condition_id="55maps-text-min-generalisation::verified-k3-canonical-gt",
        evaluation_path="results/55maps-extended-gt-2026-06-07/TM-k3/evaluation.json",
        carrier=M55_CARRIER,
        object_f1=0.8127,
        object_f1_buffer_m=50,
    ),
    CellSpec(
        key="55map-IM-k3",
        display_name="IM-k3",
        board="55map-canonical-leaderboard-50m",
        condition_id="55maps-image-generalisation::verified-k3-canonical-gt",
        evaluation_path="results/55maps-extended-gt-2026-06-07/IM-k3/evaluation.json",
        carrier=M55_CARRIER,
        object_f1=0.7987,
        object_f1_buffer_m=50,
    ),
    CellSpec(
        key="55map-TM-k4",
        display_name="TM-k4",
        board="55map-canonical-leaderboard-50m",
        condition_id="55maps-text-min-generalisation::verified-k4-canonical-gt",
        evaluation_path="results/55maps-extended-gt-2026-06-07/TM-k4/evaluation.json",
        carrier=M55_CARRIER,
        object_f1=0.7831,
        object_f1_buffer_m=50,
    ),
)


# =============================================================================
# Landauer & Klassen (2025) comparator registry
# =============================================================================


@dataclass(frozen=True)
class ComparatorSpec:
    """A published per-experiment confusion matrix used as a protocol comparator.

    Attributes:
        key: Short stable identifier used as the JSON key.
        experiment: Feature class and sensor of the published experiment.
        model: The model the published cell scored.
        confusion: The published confusion matrix.
        tile_footprint: Ground footprint of one classified tile, as published.
        reported_f1: F1 as reported by the authors (percentage points, /100).
    """

    key: str
    experiment: str
    model: str
    confusion: Confusion
    tile_footprint: str
    reported_f1: float


#: Confusion cells quoted in
#: ``docs/methodology/research/lit-scout-detection-baselines-2026-08-21.md``
#: (strand 3 table row for Landauer & Klassen 2025, DOI 10.3390/geomatics5040052).
COMPARATORS: tuple[ComparatorSpec, ...] = (
    ComparatorSpec(
        key="lk2025-castles-gpt41",
        experiment="Bavarian castles (Bing satellite imagery)",
        model="GPT-4.1",
        confusion=Confusion(tp=244, fp=101, fn=135, tn=899),
        tile_footprint="150 x 150 m",
        reported_f1=0.67,
    ),
    ComparatorSpec(
        key="lk2025-castles-gemini",
        experiment="Bavarian castles (Bing satellite imagery)",
        model="Gemini 2.0 Flash",
        confusion=Confusion(tp=144, fp=2, fn=235, tn=998),
        tile_footprint="150 x 150 m",
        reported_f1=0.55,
    ),
    ComparatorSpec(
        key="lk2025-temples-gpt41",
        experiment="Angkorian temples (satellite imagery)",
        model="GPT-4.1",
        confusion=Confusion(tp=57, fp=98, fn=43, tn=902),
        tile_footprint="140 x 140 m",
        reported_f1=0.45,
    ),
    ComparatorSpec(
        key="lk2025-temples-gemini",
        experiment="Angkorian temples (satellite imagery)",
        model="Gemini 2.0 Flash",
        confusion=Confusion(tp=32, fp=23, fn=68, tn=977),
        tile_footprint="140 x 140 m",
        reported_f1=0.41,
    ),
    ComparatorSpec(
        key="lk2025-hillforts-gpt41",
        experiment="English hillforts (LiDAR hillshade)",
        model="GPT-4.1",
        confusion=Confusion(tp=286, fp=813, fn=14, tn=187),
        tile_footprint="768 x 768 m",
        reported_f1=0.42,
    ),
    ComparatorSpec(
        key="lk2025-hillforts-gemini",
        experiment="English hillforts (LiDAR hillshade)",
        model="Gemini 2.0 Flash",
        confusion=Confusion(tp=149, fp=66, fn=151, tn=934),
        tile_footprint="768 x 768 m",
        reported_f1=0.58,
    ),
)


# =============================================================================
# Artefact loading and the MCC reproduction gate
# =============================================================================


def load_committed_block(path: Path) -> tuple[Confusion, float | None, str]:
    """Read the committed tile confusion matrix and MCC point estimate.

    Two committed serialisations exist. The gold-standard evaluations store MCC as
    a block with ``point``/``mean``/CI fields; the Track-2 55-map adapter stores a
    bare float, which *is* the all-data point estimate.

    Args:
        path: Absolute path to a committed ``evaluation.json``.

    Returns:
        Tuple of (confusion matrix, committed MCC point estimate or ``None``,
        description of which serialisation was found).

    Raises:
        KeyError: If the artefact exposes no ``summary.tile_classification`` block
            or no confusion counts within it.
    """
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    block = payload["summary"]["tile_classification"]
    counts = block["confusion"]
    cm = Confusion(tp=counts["tp"], fp=counts["fp"], fn=counts["fn"], tn=counts["tn"])

    raw_mcc = block.get("mcc")
    if isinstance(raw_mcc, dict):
        return cm, raw_mcc.get("point"), "summary.tile_classification.mcc.point"
    return cm, raw_mcc, "summary.tile_classification.mcc (bare float point estimate)"


def check_mcc_gate(recomputed: float | None, committed: float | None) -> dict[str, Any]:
    """Test whether a recomputed MCC reproduces its committed value to 4 decimals.

    Committed values are stored at differing precision (four decimal places for the
    gold-standard blocks, full float precision for the Track-2 blocks), so the gate
    compares both the absolute difference against a 1e-4 tolerance and the values
    rounded to four decimal places. Both must agree.

    Args:
        recomputed: MCC recomputed from the committed confusion matrix.
        committed: MCC as committed in the evaluation artefact.

    Returns:
        A gate record with ``passed``, the two values, the absolute delta, and a
        human-readable reason when the gate does not pass.
    """
    if committed is None or recomputed is None:
        return {
            "passed": False,
            "committed_mcc": committed,
            "recomputed_mcc": recomputed,
            "abs_delta": None,
            "tolerance": MCC_GATE_TOLERANCE,
            "reason": (
                "MCC undefined or absent on one side; cannot verify the matrix "
                "against its committed value"
            ),
        }

    delta = abs(recomputed - committed)
    rounded_match = round(recomputed, 4) == round(committed, 4)
    passed = bool(delta <= MCC_GATE_TOLERANCE and rounded_match)
    return {
        "passed": passed,
        "committed_mcc": committed,
        "recomputed_mcc": recomputed,
        "abs_delta": delta,
        "tolerance": MCC_GATE_TOLERANCE,
        "reason": None if passed else "recomputed MCC does not reproduce the committed value",
    }


def derive_cell(spec: CellSpec, project_root: Path) -> dict[str, Any]:
    """Derive the supplemental tile-level metrics for one registered cell.

    Args:
        spec: The cell to derive.
        project_root: Repository root, used to resolve ``spec.evaluation_path``.

    Returns:
        A per-cell record. When the artefact is missing, or exposes no confusion
        matrix, or fails the MCC gate, the derived metrics are withheld and the
        record explains why.
    """
    record: dict[str, Any] = {
        "key": spec.key,
        "display_name": spec.display_name,
        "board": spec.board,
        "condition_id": spec.condition_id,
        "evaluation_path": spec.evaluation_path,
        "carrier": spec.carrier,
        "object_level_f1": spec.object_f1,
        "object_level_f1_buffer_m": spec.object_f1_buffer_m,
    }

    path = project_root / spec.evaluation_path
    if not path.exists():
        record["status"] = "missing-artefact"
        record["note"] = f"committed artefact not found at {spec.evaluation_path}"
        return record

    try:
        cm, committed, source_field = load_committed_block(path)
    except KeyError as exc:
        record["status"] = "no-confusion-matrix"
        record["note"] = (
            f"artefact does not expose a tile confusion matrix (missing key {exc}); "
            "not reconstructed by re-scoring"
        )
        return record

    recomputed = tile_mcc(cm)
    gate = check_mcc_gate(recomputed, committed)

    record["committed_mcc_field"] = source_field
    record["confusion"] = {"tp": cm.tp, "fp": cm.fp, "fn": cm.fn, "tn": cm.tn}
    record["n_tiles"] = cm.n_tiles
    record["marginals"] = marginal_report(cm)
    record["vanishing_marginals"] = vanishing_marginals(cm)
    record["gate"] = gate

    if not gate["passed"]:
        record["status"] = "gate-failed"
        record["note"] = (
            "MCC reproduction gate failed; no tile-level F1 is published from this "
            "matrix"
        )
        return record

    record["status"] = "ok"
    record["prevalence_reference_positive_tile_share"] = prevalence(cm)
    record["tile_precision"] = tile_precision(cm)
    record["tile_recall"] = tile_recall(cm)
    record["tile_f1"] = tile_f1(cm)
    undefined = [
        name
        for name, value in (
            ("tile_precision", record["tile_precision"]),
            ("tile_recall", record["tile_recall"]),
            ("tile_f1", record["tile_f1"]),
        )
        if value is None
    ]
    record["undefined_metrics"] = undefined
    record["undefined_reason"] = (
        None
        if not undefined
        else "vanishing marginal(s): " + ", ".join(vanishing_marginals(cm))
    )
    return record


def derive_comparator(spec: ComparatorSpec) -> dict[str, Any]:
    """Recompute tile-level statistics from a published comparator confusion matrix.

    Args:
        spec: The published comparator cell.

    Returns:
        A per-comparator record with prevalence, P/R/F1, MCC, and the authors'
        own reported F1 for cross-checking.
    """
    cm = spec.confusion
    return {
        "key": spec.key,
        "study": "Landauer & Klassen 2025",
        "doi": "10.3390/geomatics5040052",
        "experiment": spec.experiment,
        "model": spec.model,
        "tile_footprint": spec.tile_footprint,
        "confusion": {"tp": cm.tp, "fp": cm.fp, "fn": cm.fn, "tn": cm.tn},
        "n_tiles": cm.n_tiles,
        "prevalence_reference_positive_tile_share": prevalence(cm),
        "prevalence_basis": "constructed (fixed positive:negative ratio by design)",
        "tile_precision": tile_precision(cm),
        "tile_recall": tile_recall(cm),
        "tile_f1": tile_f1(cm),
        "tile_mcc": tile_mcc(cm),
        "reported_f1_as_published": spec.reported_f1,
    }


# =============================================================================
# Report assembly and rendering
# =============================================================================


def cells_for(reference: str, project_root: Path) -> tuple[CellSpec, ...]:
    """The registered cells for a reference vintage.

    Args:
        reference: ``canonical`` (the committed r1 specs, default) or ``r2``
            -- every 55-map spec is re-pointed at its r2 evaluation
            (``-r2-gt`` condition, r2 scoring home, r2 leaderboard id) with
            ``object_f1`` read from that evaluation at 50 m rather than the
            hard-coded r1 value. GS specs pass through unchanged.
        project_root: Repository root, to read the r2 evaluations.

    Returns:
        The specs to derive.
    """
    if reference != "r2":
        return CELLS
    out = []
    for spec in CELLS:
        if spec.carrier != M55_CARRIER:
            out.append(spec)
            continue
        cell = spec.key.removeprefix("55map-")
        ev_path = f"{R2_SCORING_HOME}/{cell}/evaluation.json"
        with (project_root / ev_path).open(encoding="utf-8") as handle:
            summary = json.load(handle)["summary"]
        f1_50 = next(b for b in summary["buffers"] if b["buffer_metres"] == 50)["f1"]
        out.append(dataclasses.replace(
            spec,
            board=R2_BOARD_ID,
            condition_id=spec.condition_id.replace("-canonical-gt", "-r2-gt"),
            evaluation_path=ev_path,
            object_f1=f1_50,
        ))
    return tuple(out)


def build_report(project_root: Path, reference: str = "canonical") -> dict[str, Any]:
    """Assemble the full supplemental-metric report.

    Args:
        project_root: Repository root used to resolve committed artefact paths.
        reference: ``canonical`` (default) or ``r2`` -- see :func:`cells_for`.

    Returns:
        The serialisable report payload.
    """
    cells = [derive_cell(spec, project_root) for spec in cells_for(reference, project_root)]
    comparators = [derive_comparator(spec) for spec in COMPARATORS]
    return {
        "schema_version": SCHEMA_VERSION,
        "generator": "scripts/derive_tile_level_f1.py",
        "generator_version": GENERATOR_VERSION,
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "metric_definition": {
            "unit": "tile",
            "positive_class": "tile the reference populates with at least one mound",
            "prediction": "tile in which the model returned at least one detection",
            "tile_precision": "TP / (TP + FP)",
            "tile_recall": "TP / (TP + FN)",
            "tile_f1": "2*TP / (2*TP + FP + FN)",
            "undefined_discipline": (
                "a statistic whose denominator marginal vanishes is null, never 0.0 "
                "(docs/methodology/tile-mcc-explained.md, trap 2; erratum E81)"
            ),
            "booking_rules": (
                "unchanged from the committed evaluations: detections booked to one "
                "tile (E79 nearest-centroid rule), references booked to every tile "
                "they intersect (tile-mcc-explained.md, trap 1)"
            ),
            "comparability": (
                "tile-level statistics are carrier-specific and are not comparable "
                "across tilings or footprints (tile-mcc-explained.md, trap 3)"
            ),
        },
        "validation_gate": {
            "rule": (
                "MCC recomputed from each committed confusion matrix must reproduce "
                "the committed point estimate to at least four decimal places"
            ),
            "tolerance": MCC_GATE_TOLERANCE,
            "n_cells": len(cells),
            "n_passed": sum(1 for cell in cells if cell.get("gate", {}).get("passed")),
            "n_failed": sum(
                1 for cell in cells if cell.get("status") in {"gate-failed", "no-confusion-matrix",
                                                              "missing-artefact"}
            ),
        },
        "cells": cells,
        "comparators": comparators,
        "registration": (
            "Registered as first-class analysis 'tile-level-f1' in "
            "results/analyses-manifest.md (Principal Investigator ruling "
            "2026-08-22; spec in results/run-analyses.json). Type comparison, "
            "class post-hoc, destination Results."
        ),
    }


def _fmt(value: float | None, places: int = 4) -> str:
    """Format an optional float for the console table.

    Args:
        value: Value to render, possibly ``None``.
        places: Decimal places.

    Returns:
        The formatted value, or ``"undef"`` when ``value`` is ``None``.
    """
    return "undef" if value is None else f"{value:.{places}f}"


def render_table(report: dict[str, Any]) -> str:
    """Render the derived cells and comparators as a plain-text table.

    Args:
        report: The assembled report payload.

    Returns:
        A multi-line string suitable for stdout.
    """
    lines: list[str] = []
    header = (
        f"{'cell':38s} {'N':>6s} {'TP':>6s} {'FP':>5s} {'FN':>6s} {'TN':>6s} "
        f"{'prev':>7s} {'P':>7s} {'R':>7s} {'F1':>7s} {'MCC':>7s} {'gate':>6s}"
    )
    lines.append("Derived tile-level metrics (committed matrices only)")
    lines.append(header)
    lines.append("-" * len(header))
    for cell in report["cells"]:
        if cell["status"] != "ok":
            lines.append(f"{cell['display_name'][:38]:38s} {cell['status']:>60s}")
            continue
        cm = cell["confusion"]
        lines.append(
            f"{cell['display_name'][:38]:38s} {cell['n_tiles']:6d} {cm['tp']:6d} "
            f"{cm['fp']:5d} {cm['fn']:6d} {cm['tn']:6d} "
            f"{_fmt(cell['prevalence_reference_positive_tile_share'], 3):>7s} "
            f"{_fmt(cell['tile_precision']):>7s} {_fmt(cell['tile_recall']):>7s} "
            f"{_fmt(cell['tile_f1']):>7s} "
            f"{_fmt(cell['gate']['recomputed_mcc']):>7s} "
            f"{'PASS' if cell['gate']['passed'] else 'FAIL':>6s}"
        )

    lines.append("")
    lines.append("Landauer & Klassen 2025 comparators (constructed prevalence)")
    lines.append(header)
    lines.append("-" * len(header))
    for comp in report["comparators"]:
        cm = comp["confusion"]
        label = f"{comp['model']} — {comp['experiment'].split(' (')[0]}"
        lines.append(
            f"{label[:38]:38s} {comp['n_tiles']:6d} {cm['tp']:6d} {cm['fp']:5d} "
            f"{cm['fn']:6d} {cm['tn']:6d} "
            f"{_fmt(comp['prevalence_reference_positive_tile_share'], 3):>7s} "
            f"{_fmt(comp['tile_precision']):>7s} {_fmt(comp['tile_recall']):>7s} "
            f"{_fmt(comp['tile_f1']):>7s} {_fmt(comp['tile_mcc']):>7s} "
            f"{'n/a':>6s}"
        )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument vector, or ``None`` to read ``sys.argv``.

    Returns:
        The parsed namespace.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Derive supplemental tile-level precision/recall/F1 from the project's "
            "committed tile confusion matrices."
        )
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the JSON artefact (default: dry run, print only)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(f"output directory (default: {DEFAULT_OUTPUT_DIR}, or "
              f"{R2_OUTPUT_DIR} under --reference r2)"),
    )
    parser.add_argument(
        "--reference",
        choices=("canonical", "r2"),
        default="canonical",
        help=("canonical = the committed r1 cells (default); r2 = the 55-map cells "
              "re-derived from reference revision r2 (GS cells unchanged)."),
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="repository root used to resolve committed artefact paths",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Argument vector, or ``None`` to read ``sys.argv``.

    Returns:
        ``0`` when every registered cell passed the MCC gate, ``1`` otherwise.
    """
    args = parse_args(argv)
    if args.output_dir is None:
        args.output_dir = DEFAULT_OUTPUT_DIR if args.reference == "canonical" else R2_OUTPUT_DIR
    report = build_report(args.project_root, args.reference)
    report["reference"] = args.reference

    print(render_table(report))
    print()
    gate = report["validation_gate"]
    print(f"MCC reproduction gate: {gate['n_passed']}/{gate['n_cells']} cells passed.")

    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        destination = args.output_dir / OUTPUT_FILENAME
        with destination.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print(f"Wrote {destination}")
    else:
        print("Dry run — nothing written. Pass --write to emit the JSON artefact.")

    return 0 if gate["n_passed"] == gate["n_cells"] else 1


if __name__ == "__main__":
    sys.exit(main())
