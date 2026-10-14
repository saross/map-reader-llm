#!/usr/bin/env python3
"""
Stride-programme post-verifier scoring: the nine-cell board and contrasts.

Scores the five overnight stride cells (Phase B: g512_ov176, g384_ov128,
g256_ov064, g512_ov320; Phase C: g384_ov240) with the grid's machinery on the
common footprint, joins them to the four grid cells' registered verified
best points, and computes the paired contrasts the programme was run to
settle: the iso-stride decompositions (three tile sizes at stride 192; pairs
at 256 and 336), the stride-144 ladder rung, and every new cell against the
incumbent bar (g384_ov192 verified, F1 0.8961).

Join gates per stride cell (the S142 audit standard): probability count
equals the union file's feature count; keys are exactly the contiguous
``candidate_NNNNN`` range; carrier-tile reassignment reproduces the stored
``source_tile`` after the CRS round-trip. There is no committed-sweep anchor
for the new cells (they are new); the union score is recorded, not gated.
Then (PI ruling D62 (1), 2026-10-13) each union is rebuilt from its cell's
ten prepared passes under a row-for-row gate, every row carries the tiles
its members were seen on, and it is booked to a carrier tile on its OWN
sheet; the stored ``source_tile`` was the nearest among all carrier tiles,
which near a sheet edge can be the neighbouring sheet's.

Each leg is read under the shared leg rule (``scripts/lib_verify_dirs.py``:
``verify_repaired/`` when it holds ``probabilities.json``, else ``verify/``;
``MAP_READER_VERIFY_DIRS=fixed`` reads ``verify/``), and the directory read is
recorded as ``verifier_probabilities``.

Outputs (under ``results/stride-2026-08-25/``):
    - stride_verifier_analysis.json — boards (20 m and 30 m), contrasts,
      billing reconciliation, ``verifier_probabilities``
    - stride_verifier_sweep.csv — the full prob_t × k sweep, five cells

Zero API. Run on sapphire: ~800 scorings plus B = 10,000 paired bootstraps.

Created: 2026-08-25 (Session 142 overnight)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
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

from scripts.grid_analysis import (  # noqa: E402
    CRS,
    SEED,
    load_cell_passes,
    paired_bootstrap,
    score,
)
from scripts.grid_verifier_analysis import (  # noqa: E402
    JoinGateError,
    per_tile_counts,
    verified_subset,
)
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402
from scripts.lib_cluster_origins import union_on_origin  # noqa: E402
from scripts.lib_verify_dirs import read_leg_results  # noqa: E402
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

COMMON_BOUNDS = (
    PROJECT_ROOT / "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson")
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
OUT_DIR = PROJECT_ROOT / "results/stride-2026-08-25"

BOOTSTRAP = 10_000
K_TOTAL = 10
FLEX_DIVISOR = 2.0

#: Stride cells: label -> (output root, stride m-equivalent px, tile px, overlap frac).
STRIDE_CELLS: dict[str, tuple[str, int, int, float]] = {
    "g512_ov176": ("outputs/stride-phaseb-2026-08-25", 336, 512, 0.34375),
    "g384_ov128": ("outputs/stride-phaseb-2026-08-25", 256, 384, 1 / 3),
    "g256_ov064": ("outputs/stride-phaseb-2026-08-25", 192, 256, 0.25),
    "g512_ov320": ("outputs/stride-phaseb-2026-08-25", 192, 512, 0.625),
    "g384_ov240": ("outputs/stride-phasec-2026-08-25", 144, 384, 0.625),
}

#: The four grid cells' registered verified best points (D16-pattern files).
GRID_CELLS: dict[str, tuple[str, int, int, float]] = {
    "g512_ov064": ("results/grid-2026-08-18/conditions-verified/g512_ov064", 448, 512, 0.125),
    "g512_ov256": ("results/grid-2026-08-18/conditions-verified/g512_ov256", 256, 512, 0.50),
    "g384_ov048": ("results/grid-2026-08-18/conditions-verified/g384_ov048", 336, 384, 0.125),
    "g384_ov192": ("results/grid-2026-08-18/conditions-verified/g384_ov192", 192, 384, 0.50),
}

#: The contrasts the programme was run to settle: name -> (a, b) as ΔF1 = a − b.
CONTRASTS: dict[str, tuple[str, str]] = {
    "iso192: 512/62.5 - 384/50": ("g512_ov320", "g384_ov192"),
    "iso192: 256/25 - 384/50": ("g256_ov064", "g384_ov192"),
    "iso192: 256/25 - 512/62.5": ("g256_ov064", "g512_ov320"),
    "iso256: 384/33.3 - 512/50": ("g384_ov128", "g512_ov256"),
    "iso336: 512/34.4 - 384/12.5": ("g512_ov176", "g384_ov048"),
    "rung144: 384/62.5 - 384/50": ("g384_ov240", "g384_ov192"),
    "bar: 384/62.5 - grid winner": ("g384_ov240", "g384_ov192"),
    "bar: 384/33.3 - grid winner": ("g384_ov128", "g384_ov192"),
    "bar: 512/34.4 - grid winner": ("g512_ov176", "g384_ov192"),
    # The 384 px stride ladder. These two rows are in the committed
    # stride_verifier_analysis.json (2026-08-25) but were missing from this
    # list, so the script could not reproduce its own artefact. Restored
    # 2026-10-05 (D42 regeneration) with the cells their names imply; W2's
    # re-test reproduced the committed values exactly with this mapping
    # (reports/retest-bootstrap-check-2026-10-05.md, class C2).
    "ladder384: 256-stride - 336-stride": ("g384_ov128", "g384_ov048"),
    "ladder384: 144-stride - 256-stride": ("g384_ov240", "g384_ov128"),
}


def load_stride_union(label: str, *, union_name: str = "union_k10.geojson",
                      verify_dir: str = "verify") -> gpd.GeoDataFrame:
    """Load one stride cell's union joined to its verifier probabilities.

    The probabilities are read under the shared leg rule
    (``scripts/lib_verify_dirs.py``): from ``<verify_dir>_repaired/`` when
    that copy holds ``probabilities.json`` (D62 (1) step 2's re-verified
    wrong-sheet rows), from ``<verify_dir>/`` otherwise, or always from
    ``<verify_dir>/`` under ``MAP_READER_VERIFY_DIRS=fixed``. The directory
    read is recorded in ``gdf.attrs["verifier_probabilities"]``.

    Args:
        label: Cell label.
        union_name: The union file under ``verifier/<label>/``.
        verify_dir: The verify-stage directory's fixed name (the leg).

    Returns:
        GeoDataFrame in the project CRS with ``vote_count``,
        ``mound_probability`` and reassignment-verified ``source_tile``.

    Raises:
        JoinGateError: On any join-gate failure.
    """
    root = PROJECT_ROOT / STRIDE_CELLS[label][0] / "verifier" / label
    gdf = gpd.read_file(root / union_name).to_crs(CRS)
    results, provenance = read_leg_results(root, verify_dir, PROJECT_ROOT)
    if len(results) != len(gdf):
        raise JoinGateError(
            f"{label}: {len(results)} probabilities vs {len(gdf)} union features")
    expected = {f"candidate_{i:05d}" for i in range(len(gdf))}
    if set(results) != expected:
        raise JoinGateError(f"{label}: probability keys not the contiguous range")
    gdf["mound_probability"] = [
        float(results[f"candidate_{i:05d}"]["mound_probability"])
        for i in range(len(gdf))
    ]
    gdf.attrs["verifier_probabilities"] = provenance
    return gdf


def reassign_gate(gdf: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
                  label: str) -> gpd.GeoDataFrame:
    """Assert carrier reassignment reproduces the stored source_tile."""
    fresh = assign_primary_tiles(gdf, bounds)
    if int((np.asarray(fresh) != gdf["source_tile"].to_numpy()).sum()):
        raise JoinGateError(f"{label}: carrier reassignment mismatch")
    out = gdf.copy()
    out["source_tile"] = fresh
    return out


def load_stride_union_on_origin(
    label: str, bounds: gpd.GeoDataFrame, *, union_name: str = "union_k10.geojson",
    verify_dir: str = "verify", n_passes: int = K_TOTAL,
) -> gpd.GeoDataFrame:
    """A stride cell's verified union, gated, with each row on its own sheet.

    :func:`load_stride_union` and :func:`reassign_gate`, then (D62 (1)) the
    union's clusters rebuilt from the cell's first ``n_passes`` prepared
    passes, their member tiles attached, and each row booked to a carrier
    tile on its own sheet (``lib_cluster_origins.union_on_origin``).

    Args:
        label: Cell label.
        bounds: Common carrier bounds.
        union_name: The union file under ``verifier/<label>/`` (the winner
            ladder's first-N unions are ``union_k<N>.geojson``).
        verify_dir: Its verify-stage directory.
        n_passes: How many passes the union was built from.

    Returns:
        The joined union with ``origin_tiles`` and an origin-sheet
        ``source_tile``; index = the verifier's candidate number;
        ``attrs["verifier_probabilities"]`` the leg directory read
        (:func:`load_stride_union`).
    """
    root = PROJECT_ROOT / STRIDE_CELLS[label][0]
    joined = load_stride_union(label, union_name=union_name, verify_dir=verify_dir)
    provenance = joined.attrs["verifier_probabilities"]
    gdf = reassign_gate(joined, bounds, label)
    out = union_on_origin(gdf, load_cell_passes(root / "scoring", label), bounds,
                          label=f"{label}/{union_name}", n_passes=n_passes)
    # Carried explicitly: pandas does not promise to keep attrs through
    # union_on_origin's merges.
    out.attrs["verifier_probabilities"] = provenance
    return out


def score_at(gdf: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
             bounds: gpd.GeoDataFrame, buffer_m: int) -> dict[str, Any]:
    """Score one set at an arbitrary buffer, preserving the E81 MCC contract."""
    raw = score_detection_set(gdf, gdf_ref, bounds, buffer_metres=buffer_m)
    return {
        "precision": raw["precision"], "recall": raw["recall"], "f1": raw["f1"],
        "n_detections": raw["n_detections"],
        "mcc": None if raw["mcc"] is None else float(raw["mcc"]),
    }


def main() -> int:
    """Score the five stride cells, build the boards, run the contrasts."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bootstrap", type=int, default=BOOTSTRAP)
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    bounds = gpd.read_file(COMMON_BOUNDS)
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    logger.info("common carrier: %d tiles", len(bounds))

    sweep_rows: list[dict[str, Any]] = []
    best: dict[str, dict[str, Any]] = {}
    best_sets: dict[str, gpd.GeoDataFrame] = {}
    union_scores: dict[str, dict[str, Any]] = {}
    #: Which directory each cell's probabilities were read from (lib_verify_dirs).
    verifier_probabilities: dict[str, dict[str, Any]] = {}

    for label, (_, stride, px, ov) in STRIDE_CELLS.items():
        gdf = load_stride_union_on_origin(label, bounds)
        verifier_probabilities[label] = gdf.attrs["verifier_probabilities"]
        union_scores[label] = score(gdf, gdf_ref, bounds)
        thresholds = sorted({0.0} | {float(v) for v in gdf["mound_probability"]})
        rows = []
        for prob_t in thresholds:
            for k in range(1, K_TOTAL + 1):
                subset = verified_subset(gdf, prob_t, k)
                row = score(subset, gdf_ref, bounds)
                row.update({"cell": label, "stride": stride, "tile_px": px,
                            "overlap_frac": round(ov, 4), "K": K_TOTAL,
                            "prob_t": prob_t, "min_votes": k})
                rows.append(row)
        sweep_rows.extend(rows)
        b = max(rows, key=lambda r: r["f1"])
        subset = verified_subset(gdf, b["prob_t"], b["min_votes"])
        b["f1_30m"] = score_at(subset, gdf_ref, bounds, 30)["f1"]
        best[label] = b
        best_sets[label] = subset
        logger.info(
            "%-11s stride %3d: union %5d (F1 %.4f) | best F1@20=%.4f @30=%.4f "
            "at p>=%.2f k>=%d (n=%d, P=%.4f R=%.4f MCC=%s)",
            label, stride, len(gdf), union_scores[label]["f1"], b["f1"],
            b["f1_30m"], b["prob_t"], b["min_votes"], b["n_detections"],
            b["precision"], b["recall"],
            "undef" if b["mcc"] is None else f"{b['mcc']:.4f}")

    # Grid cells: registered verified best points, re-scored here for a
    # uniform board (20 m values must reproduce the register exactly).
    for label, (rel, stride, px, ov) in GRID_CELLS.items():
        gdf = gpd.read_file(PROJECT_ROOT / rel / "detections.geojson")
        row = score(gdf, gdf_ref, bounds)
        row.update({"cell": label, "stride": stride, "tile_px": px,
                    "overlap_frac": ov,
                    "f1_30m": score_at(gdf, gdf_ref, bounds, 30)["f1"]})
        best[label] = row
        best_sets[label] = gdf
        logger.info("%-11s stride %3d (grid): F1@20=%.4f @30=%.4f",
                    label, stride, row["f1"], row["f1_30m"])

    per_tile = {label: per_tile_counts(best_sets[label], bounds, gdf_ref)
                for label in best_sets}
    contrasts = {}
    for name, (a, b) in CONTRASTS.items():
        res = paired_bootstrap(per_tile[a], per_tile[b], args.bootstrap, seed=SEED)
        contrasts[name] = res
        logger.info("%-32s dF1=%+.4f CI95 [%+.4f, %+.4f] p=%.4f %s",
                    name, res["delta"], res["ci_lower"], res["ci_upper"],
                    res["p_two_sided"],
                    "EXCLUDES 0" if res["excludes_zero"] else "includes 0")

    billing = {"cells": {}, "total_list_usd": 0.0}
    for label, (root, *_rest) in STRIDE_CELLS.items():
        meta = json.loads((PROJECT_ROOT / root / "verifier" / label /
                           "verify" / "run.meta.json").read_text())
        li = meta["cost_estimate"]["list_total_cost_usd"]
        billing["cells"][label] = {
            "verifier_calls": meta["execution_stats"]["items_processed"],
            "verifier_failed": meta["execution_stats"]["items_failed"],
            "list_usd": li, "flex_usd": li / FLEX_DIVISOR,
        }
        billing["total_list_usd"] += li
    billing["total_flex_usd"] = round(billing["total_list_usd"] / FLEX_DIVISOR, 4)
    billing["total_list_usd"] = round(billing["total_list_usd"], 4)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": (
            "POST-HOC (E41-class) stride-programme Phase B + C(part) board: "
            "five new geometry cells, K = 10 union + adversarial text "
            "verifier, scored on the grid common footprint. $0 scoring over "
            "committed data."),
        "boards": {label: {k: best[label].get(k) for k in
                           ("stride", "tile_px", "overlap_frac", "precision",
                            "recall", "f1", "f1_30m", "mcc", "n_detections",
                            "prob_t", "min_votes")}
                   for label in best},
        "union_scores": union_scores,
        "verifier_probabilities": verifier_probabilities,
        "contrasts": contrasts,
        "bootstrap_config": {"n_iterations": args.bootstrap, "seed": SEED},
        "billing_verifier": billing,
    }
    (OUT_DIR / "stride_verifier_analysis.json").write_text(
        json.dumps(payload, indent=2) + "\n")

    cols = ["cell", "stride", "tile_px", "overlap_frac", "K", "prob_t",
            "min_votes", "n_detections", "precision", "recall", "f1", "mcc"]
    with (OUT_DIR / "stride_verifier_sweep.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(sweep_rows)
    logger.info("wrote %s (%d sweep rows)", OUT_DIR.name, len(sweep_rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
