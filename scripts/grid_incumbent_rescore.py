#!/usr/bin/env python3
"""
Stride-programme Phase A: incumbents re-scored on the grid's common footprint.

The grid post-verifier board (`results/grid-2026-08-18/findings.md` § "The
verifier stage, run") and the study's incumbent leaders sit on different
footprints: the grid on the four-way tile-union intersection (487 clipped
carrier tiles, 428 references) and the incumbents on the full era-2-487
scope (435 references). The stride programme
(`planning/stride-programme-2026-08-24.md` § Phase A) removes that caveat
for $0 by clipping each incumbent's committed verified detection set to the
common footprint and scoring it with the grid's own machinery, so the
"does the new geometry dethrone the incumbents?" comparison is on ONE
evaluation.

Per incumbent set, two stages with a hard gate between them:

1. **Own-scope reproduction gate.** The committed detections are scored on
   their own registered bounds (era-2-487) at 20 m and must reproduce the
   registered F1@20 m within 5e-4, or the script refuses to publish.
2. **Common-footprint scoring.** Centroids are reassigned to the grid's
   clipped carrier via `grid_analysis.as_gdf` (off-carrier detections drop,
   exactly as every grid cell's detections were clipped) and scored at 20 m
   and 30 m with tile Matthews Correlation Coefficient (MCC; undefined
   stays ``null``, erratum E81).

Usage::

    python scripts/grid_incumbent_rescore.py

Inputs: the four incumbents' committed detection sets (paths and registered
anchors below), the grid common bounds, the era-2-487 bounds, and the
curator ground truth. Output:
``results/grid-2026-08-18/incumbents_common_footprint.json``.

Zero API. Light compute (a dozen Hungarian matchings); run beside the
scoring artefacts on sapphire.

Created: 2026-08-24 (Session 142)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_analysis import CRS, as_gdf, score  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

COMMON_BOUNDS = (
    PROJECT_ROOT / "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson")
OWN_BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
OUT_PATH = (
    PROJECT_ROOT / "results/grid-2026-08-18/incumbents_common_footprint.json")

#: The incumbent sets: condition id -> (detections path, registered F1@20 m).
#: Anchors re-read from each condition's registered evaluation.json (S142);
#: the reproduction gate asserts them against a fresh own-scope score.
INCUMBENTS: dict[str, tuple[str, float]] = {
    "verifier-robustness::verified-384-16of30-t0-3-n5-opmax": (
        "results/verifier-robustness/opmax-sets/"
        "opmax-16of30-N5minT0.3-vt3-pt0.15.geojson", 0.8951),
    "pv-diag-384::verified-adv-text-consensus-16of30": (
        "outputs/era1-pv-stage-d/384-consensus-text-high/pass_1/"
        "accepted_t0.2.geojson", 0.8902),
    "pv-diag-384::verified-adv-text-min-6of10": (
        "results/verifier-robustness/min-thinking-sets/"
        "text-min-t07-10pass-6of10-n1-pt0.2.geojson", 0.8835),
    "pv-diag-384::verified-adv-text-min-true-3of5": (
        "results/verifier-robustness/min-thinking-sets/"
        "text-min-t07-TRUE-5pass-3of5-n1-pt0.15.geojson", 0.8784),
}

GATE_TOL = 5e-4


class ReproductionError(RuntimeError):
    """An incumbent failed its own-scope reproduction gate."""


def rescore_incumbent(
    condition_id: str, det_path: Path, registered_f1: float,
    own_bounds: gpd.GeoDataFrame, common_bounds: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
) -> dict[str, Any]:
    """Gate one incumbent on its own scope, then score it on the common one.

    Args:
        condition_id: The registered condition id, for the report.
        det_path: Committed verified detection set.
        registered_f1: The registered F1@20 m anchor.
        own_bounds: The era-2-487 bounds the registered evaluation used.
        common_bounds: The grid's clipped common carrier bounds.
        gdf_ref: Curator ground truth.

    Returns:
        Row with the own-scope reproduction and the common-footprint scores.

    Raises:
        ReproductionError: If the own-scope score misses the anchor.
    """
    gdf = gpd.read_file(det_path).to_crs(CRS)
    own = score(gdf, gdf_ref, own_bounds)
    delta = abs(own["f1"] - registered_f1)
    if delta > GATE_TOL:
        raise ReproductionError(
            f"{condition_id}: own-scope F1@20m {own['f1']:.4f} misses the "
            f"registered {registered_f1:.4f} by {delta:.5f}")

    centroids = np.asarray([[g.x, g.y] for g in gdf.geometry], dtype=float)
    clipped = as_gdf(centroids, common_bounds)
    row: dict[str, Any] = {
        "condition_id": condition_id,
        "detections": str(det_path.relative_to(PROJECT_ROOT)),
        "registered_f1_at_20m": registered_f1,
        "own_scope_reproduced_f1_at_20m": own["f1"],
        "n_detections_own_scope": own["n_detections"],
        "n_detections_common": int(len(clipped)),
        "n_dropped_by_clip": int(own["n_detections"] - len(clipped)),
    }
    for buf in (20, 30):
        result = score(clipped, gdf_ref, common_bounds) if buf == 20 else None
        if result is None:
            from scripts.lib_advanced_metrics import score_detection_set
            raw = score_detection_set(
                clipped, gdf_ref, common_bounds, buffer_metres=buf)
            result = {
                "precision": raw["precision"], "recall": raw["recall"],
                "f1": raw["f1"], "n_detections": raw["n_detections"],
                "mcc": None if raw["mcc"] is None else float(raw["mcc"]),
            }
        row[f"common_footprint_{buf}m"] = result
        logger.info(
            "%-55s common @%dm: P=%.4f R=%.4f F1=%.4f MCC=%s",
            condition_id.split("::")[1], buf, result["precision"],
            result["recall"], result["f1"],
            "undefined" if result["mcc"] is None else f"{result['mcc']:.4f}")
    return row


def main() -> int:
    """Gate and re-score all four incumbents; write the Phase A artefact.

    Returns:
        Process exit status (0 on success).
    """
    own_bounds = gpd.read_file(OWN_BOUNDS)
    common_bounds = gpd.read_file(COMMON_BOUNDS)
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    logger.info("own scope: %d tiles | common carrier: %d tiles",
                len(own_bounds), len(common_bounds))

    rows = []
    for condition_id, (rel_path, anchor) in INCUMBENTS.items():
        row = rescore_incumbent(
            condition_id, PROJECT_ROOT / rel_path, anchor,
            own_bounds, common_bounds, gdf_ref)
        logger.info(
            "%-55s own-scope gate OK (%.4f, clip dropped %d of %d)",
            condition_id.split("::")[1], row["own_scope_reproduced_f1_at_20m"],
            row["n_dropped_by_clip"], row["n_detections_own_scope"])
        rows.append(row)

    OUT_PATH.write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": (
            "Stride-programme Phase A ($0): incumbent verified sets clipped "
            "to the grid common footprint and re-scored at 20/30 m, each "
            "under an own-scope reproduction gate at 5e-4. POST-HOC "
            "(E41-class) comparison material for "
            "planning/stride-programme-2026-08-24.md."),
        "scope": {
            "own": "era-2-487 (full_evaluation_bounds, 384px grid)",
            "common": "grid four-way intersection on the clipped 487-tile "
                      "carrier (428 references)",
        },
        "incumbents": rows,
    }, indent=2) + "\n")
    logger.info("wrote %s", OUT_PATH.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
