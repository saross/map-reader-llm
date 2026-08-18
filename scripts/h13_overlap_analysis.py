#!/usr/bin/env python3
"""
H13 overlap-arm analyses: F1-vs-overlap, cost-efficiency, and edge detection.

Runs the three analyses the preregistration attaches to H13
(§§ 1014-1048) over the deduplicated, common-scope detection sets built
by ``scripts/prepare_h13_scoring.py``:

1. **F1 as a function of overlap** — per-arm micro-F1 on the common
   340-tile carrier grid, plus *paired* tile bootstrap deltas for the
   three pairwise contrasts. Pairing matters: the arms are scored over
   the same ground, so resampling the same tile draw for both arms of a
   contrast removes between-tile variance (the dominant variance
   component) from the delta.

2. **Cost-efficiency per additional API dollar** — F1 per dollar and the
   marginal F1 bought by each step up in overlap, on audited spend.
   Arm A ran free-tier in March so its dollar cost is *imputed* at the
   measured arm-B/arm-C per-tile rate; this is stated wherever the
   number is reported.

3. **Edge-detection analysis** — the registered mechanism question.
   For each ground-truth mound, ``best_margin`` is the largest distance
   to a tile edge the mound ever enjoyed across the tiles that contain
   it: a mound stuck in a tile corner under a sparse tiling has a small
   best margin, while a denser tiling is likely to place it near some
   tile's centre. Recall is then reported against that margin, which is
   what separates "overlap helps because edge mounds get a better look"
   from "overlap helps because more looks means more guesses".

Bootstrap conventions follow the project's registered instrument
(Decision 10, ``decisions-log.md:337``; E54 for the narrow-effect
sensitivity): tile-level resampling with replacement, seed 42,
percentile CI95, B = 1,000 primary and B = 10,000 sensitivity,
two-sided p = max(2 * min tail, 1/B).

Usage::

    python scripts/h13_overlap_analysis.py \\
        --scoring-dir outputs/h13/scoring \\
        --output-dir results/h13-overlap-2026-08-18

Inputs:
    - outputs/h13/scoring/common/arm{A,B,C}/run_N/detections_dedup.geojson
    - outputs/h13/scoring/bounds/h13_common_bounds.geojson (carrier grid)
    - outputs/h13/scoring/bounds/h13_arm{A,B,C}_bounds.geojson (native tilings)
    - inputs/vectors/references/mounds-reference.geojson
    - outputs/h13/arm{B,C}/**/*.meta.json (audited cost)

Outputs:
    - h13_overlap_analysis.json - all three analyses, machine-readable
    - per_tile_counts.json      - per-arm per-tile TP/FP/FN (bootstrap input)

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
    get_map_name,
    match_detections_to_references,
    scope_references_to_tiles,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SEED = 42
B_PRIMARY = 1_000
B_SENSITIVITY = 10_000
BUFFER_M = 20
RUNS = ("run_1", "run_2", "run_3")
ARM_OVERLAP = {"armA": 0.125, "armB": 0.25, "armC": 0.50}
ARM_TILES = {"armA": 340, "armB": 430, "armC": 999}
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"

#: Audited spend, summed from the per-pass ``cost_estimate`` blocks of the
#: committed run metadata (arm B includes its single-tile recovery pass).
#: Arm A predates the paid runs (free-tier March passes, $0 recorded), so
#: its cost is imputed downstream at the measured B/C per-tile rate.
COST_META = {
    "armB": [
        "outputs/h13/armB/run_1/detections-detect_brief-text-3-flash-2026-08-17.meta.json",
        "outputs/h13/armB/run_1_recovery/detections-detect_brief-text-3-flash-2026-08-17.meta.json",
        "outputs/h13/armB/run_2/detections-detect_brief-text-3-flash-2026-08-17.meta.json",
        "outputs/h13/armB/run_3/detections-detect_brief-text-3-flash-2026-08-17.meta.json",
    ],
    "armC": [
        "outputs/h13/armC/run_1/detections-detect_brief-text-3-flash-2026-08-17.meta.json",
        "outputs/h13/armC/run_2/detections-detect_brief-text-3-flash-2026-08-17.meta.json",
        "outputs/h13/armC/run_3/detections-detect_brief-text-3-flash-2026-08-17.meta.json",
    ],
}


def micro_f1(tp: float, fp: float, fn: float) -> tuple[float, float, float]:
    """Return (precision, recall, F1) from pooled counts.

    Args:
        tp: True positives. fp: False positives. fn: False negatives.

    Returns:
        Tuple of precision, recall and F1; each 0.0 where undefined.
    """
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return p, r, f


def build_per_tile(
    scoring_dir: Path, bounds: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
) -> dict[str, dict[str, np.ndarray]]:
    """Build per-arm, run-averaged per-tile TP/FP/FN arrays on the carrier grid.

    Counts are averaged across the arm's three passes before resampling,
    the same pass-averaged float convention the H3 bootstrap leg used for
    single-pass cells (``scripts/e45_bootstrap_pairings.py``). Averaging
    first keeps the resampling unit the tile rather than the pass, which
    is what Decision 10 registers.

    Args:
        scoring_dir: Root of the prepared scoring artefacts.
        bounds: Common-scope carrier bounds (defines tile order).
        gdf_ref: Ground-truth references.

    Returns:
        Mapping arm -> {"tp", "fp", "fn"} float arrays aligned with
        ``bounds['tile_name']`` order.
    """
    tile_order = list(bounds["tile_name"])
    out: dict[str, dict[str, np.ndarray]] = {}

    for arm in ARM_OVERLAP:
        acc = {k: np.zeros(len(tile_order)) for k in ("tp", "fp", "fn")}
        for run in RUNS:
            det_path = scoring_dir / "common" / arm / run / "detections_dedup.geojson"
            gdf_det = gpd.read_file(det_path)
            tm = compute_per_tile_tp_fp_fn(
                gdf_det, gdf_ref, bounds, buffer_metres=BUFFER_M,
            )
            tm = tm.set_index("tile_name").reindex(tile_order).fillna(0)
            for k in ("tp", "fp", "fn"):
                acc[k] += tm[k].to_numpy(dtype=float)
        out[arm] = {k: v / len(RUNS) for k, v in acc.items()}
        p, r, f = micro_f1(*(out[arm][k].sum() for k in ("tp", "fp", "fn")))
        logger.info(
            "%s pooled per-tile: TP=%.1f FP=%.1f FN=%.1f -> micro-F1=%.4f "
            "(P=%.4f R=%.4f)",
            arm, out[arm]["tp"].sum(), out[arm]["fp"].sum(),
            out[arm]["fn"].sum(), f, p, r,
        )
    return out


def paired_bootstrap(
    a: dict[str, np.ndarray], b: dict[str, np.ndarray],
    n_iter: int, seed: int = SEED,
) -> dict[str, Any]:
    """Paired tile bootstrap of the micro-F1 difference between two arms.

    Each iteration draws one tile index sample with replacement and applies
    it to *both* arms, so the resampled difference isolates the arm effect
    from between-tile heterogeneity.

    Args:
        a: Per-tile count arrays for the first arm.
        b: Per-tile count arrays for the second arm.
        n_iter: Bootstrap iterations.
        seed: Random seed.

    Returns:
        Dict with the observed delta, percentile CI95, bootstrap mean, and
        the two-sided p-value ``max(2 * min tail, 1/B)``.
    """
    n = len(a["tp"])
    rng = np.random.default_rng(seed)
    obs = (micro_f1(*(a[k].sum() for k in ("tp", "fp", "fn")))[2]
           - micro_f1(*(b[k].sum() for k in ("tp", "fp", "fn")))[2])

    deltas = np.empty(n_iter)
    for i in range(n_iter):
        idx = rng.integers(0, n, n)
        fa = micro_f1(*(a[k][idx].sum() for k in ("tp", "fp", "fn")))[2]
        fb = micro_f1(*(b[k][idx].sum() for k in ("tp", "fp", "fn")))[2]
        deltas[i] = fa - fb

    below = float((deltas <= 0).sum()) / n_iter
    above = float((deltas >= 0).sum()) / n_iter
    p = max(2 * min(below, above), 1.0 / n_iter)

    return {
        "delta": float(obs),
        "ci_lower": float(np.percentile(deltas, 2.5)),
        "ci_upper": float(np.percentile(deltas, 97.5)),
        "bootstrap_mean": float(deltas.mean()),
        "p_two_sided": float(p),
        "n_iterations": n_iter,
        "seed": seed,
        "excludes_zero": bool(
            np.percentile(deltas, 2.5) > 0 or np.percentile(deltas, 97.5) < 0
        ),
    }


def audited_costs(per_tile_rate_source: tuple[str, ...] = ("armB", "armC")) -> dict[str, Any]:
    """Sum audited API spend per arm and impute arm A's free-tier cost.

    Args:
        per_tile_rate_source: Arms whose measured spend sets the imputation
            rate for arm A.

    Returns:
        Dict of per-arm cost blocks plus the imputation rate and basis.
    """
    costs: dict[str, Any] = {}
    for arm, paths in COST_META.items():
        total = 0.0
        for rel in paths:
            meta = json.loads((PROJECT_ROOT / rel).read_text())
            total += float(meta["cost_estimate"]["total_cost_usd"])
        calls = ARM_TILES[arm] * len(RUNS)
        costs[arm] = {
            "total_usd": round(total, 6),
            "calls": calls,
            "usd_per_call": round(total / calls, 8),
            "basis": "audited (summed per-pass cost_estimate)",
        }

    rate = float(np.mean([costs[a]["usd_per_call"] for a in per_tile_rate_source]))
    calls_a = ARM_TILES["armA"] * len(RUNS)
    costs["armA"] = {
        "total_usd": round(rate * calls_a, 6),
        "calls": calls_a,
        "usd_per_call": round(rate, 8),
        "basis": (
            "IMPUTED — arm A ran free-tier in March 2026 ($0 recorded); "
            f"priced at the mean measured arm-B/arm-C rate ${rate:.6f}/call"
        ),
    }
    return costs


def edge_analysis(
    scoring_dir: Path, common_bounds: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame, common_geom: Any,
) -> dict[str, Any]:
    """Recall as a function of each mound's best distance-to-tile-edge.

    ``best_margin`` for a mound under an arm is the maximum, over that
    arm's *native* tiles containing the mound, of the distance from the
    mound to the tile's edge. It answers "how central a look did this arm
    ever give this mound?" — the quantity a denser tiling is supposed to
    improve. Recall is the fraction of the arm's three passes in which the
    mound was matched (20 m, Hungarian, per map).

    Args:
        scoring_dir: Root of the prepared scoring artefacts.
        common_bounds: Common-scope carrier bounds (for reference scoping).
        gdf_ref: Ground-truth references.
        common_geom: Common footprint geometry.

    Returns:
        Dict with per-arm margin distributions, binned recall, and the
        low-margin subgroup comparison.
    """
    # Ground truth in the common scope, per map.
    in_scope_idx: list[Any] = []
    for map_name in sorted({get_map_name(n) for n in common_bounds["tile_name"]}):
        mb = common_bounds[common_bounds["tile_name"].str.startswith(map_name)]
        rs = gdf_ref[gdf_ref["Map"] == map_name]
        if not rs.empty:
            in_scope_idx.extend(list(scope_references_to_tiles(rs, mb).index))
    refs = gdf_ref.loc[sorted(set(in_scope_idx))].copy()
    logger.info("edge analysis: %d ground-truth mounds in common scope", len(refs))

    # Per-arm best margin from the arm's own (native) tiling.
    margins: dict[str, np.ndarray] = {}
    for arm in ARM_OVERLAP:
        nb = gpd.read_file(scoring_dir / "bounds" / f"h13_{arm}_bounds.geojson")
        joined = gpd.sjoin(refs, nb[["tile_name", "geometry"]],
                           how="left", predicate="intersects")
        tile_geom = {r["tile_name"]: r.geometry for _, r in nb.iterrows()}
        best = []
        for idx, point in zip(refs.index, refs.geometry):
            names = joined.loc[[idx], "tile_name"].dropna().tolist() \
                if idx in joined.index else []
            if not names:
                best.append(0.0)
            else:
                best.append(max(
                    point.distance(tile_geom[t].exterior) for t in names
                ))
        margins[arm] = np.asarray(best)
        logger.info(
            "%s best-margin (m): min=%.1f p10=%.1f median=%.1f max=%.1f",
            arm, margins[arm].min(), np.percentile(margins[arm], 10),
            np.median(margins[arm]), margins[arm].max(),
        )

    # Per-arm per-mound recall across the three passes.
    recall: dict[str, np.ndarray] = {}
    for arm in ARM_OVERLAP:
        hits = np.zeros(len(refs))
        for run in RUNS:
            gdf_det = gpd.read_file(
                scoring_dir / "common" / arm / run / "detections_dedup.geojson")
            matched_global: set[Any] = set()
            for map_name in sorted({get_map_name(n) for n in common_bounds["tile_name"]}):
                r_scope = refs[refs["Map"] == map_name]
                d_scope = gdf_det[gdf_det["source_tile"].str.startswith(map_name)]
                if r_scope.empty or d_scope.empty:
                    continue
                _, m_ref, _, _ = match_detections_to_references(
                    list(d_scope.geometry), list(r_scope.geometry), BUFFER_M,
                )
                matched_global.update(r_scope.index[i] for i in m_ref)
            hits += np.asarray([1.0 if i in matched_global else 0.0
                                for i in refs.index])
        recall[arm] = hits / len(RUNS)
        logger.info("%s per-mound recall: mean=%.4f", arm, recall[arm].mean())

    # Binned recall against arm A's margin — the fixed x-axis makes the
    # arms comparable mound-for-mound (each mound sits in the same bin for
    # every arm, so bin-wise differences are arm effects, not re-binning).
    edges = [0, 50, 100, 200, 400, 800, 1300]
    binned: list[dict[str, Any]] = []
    a_margin = margins["armA"]
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (a_margin >= lo) & (a_margin < hi)
        if not sel.any():
            continue
        binned.append({
            "armA_margin_lo_m": lo, "armA_margin_hi_m": hi,
            "n_mounds": int(sel.sum()),
            **{f"recall_{arm}": float(recall[arm][sel].mean()) for arm in ARM_OVERLAP},
            **{f"median_margin_{arm}_m": float(np.median(margins[arm][sel]))
               for arm in ARM_OVERLAP},
        })

    # Low-margin subgroup: mounds arm A could only ever see near a tile edge.
    low = a_margin < 100
    return {
        "n_mounds": int(len(refs)),
        "margin_summary_m": {
            arm: {
                "min": float(margins[arm].min()),
                "p10": float(np.percentile(margins[arm], 10)),
                "median": float(np.median(margins[arm])),
                "max": float(margins[arm].max()),
                "frac_under_100m": float((margins[arm] < 100).mean()),
            } for arm in ARM_OVERLAP
        },
        "binned_by_armA_margin": binned,
        "low_margin_subgroup": {
            "definition": "arm-A best margin < 100 m",
            "n_mounds": int(low.sum()),
            **{f"recall_{arm}": float(recall[arm][low].mean()) for arm in ARM_OVERLAP},
            **{f"recall_{arm}_high_margin": float(recall[arm][~low].mean())
               for arm in ARM_OVERLAP},
        },
        "overall_recall": {arm: float(recall[arm].mean()) for arm in ARM_OVERLAP},
    }


def main() -> int:
    """Run all three H13 analyses and write the combined JSON.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="H13 overlap analyses: F1-vs-overlap, cost-efficiency, edges.")
    parser.add_argument(
        "--scoring-dir", type=Path,
        default=PROJECT_ROOT / "outputs/h13/scoring",
        help="Prepared scoring artefacts (default: outputs/h13/scoring)")
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results/h13-overlap-2026-08-18",
        help="Output directory")
    parser.add_argument(
        "--bootstrap", type=int, default=B_PRIMARY,
        help=f"Primary bootstrap iterations (default: {B_PRIMARY})")
    parser.add_argument(
        "--sensitivity", type=int, default=B_SENSITIVITY,
        help=f"Sensitivity bootstrap iterations (default: {B_SENSITIVITY})")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    common_bounds = gpd.read_file(
        args.scoring_dir / "bounds" / "h13_common_bounds.geojson")
    common_geom = common_bounds.geometry.union_all()
    gdf_ref = gpd.read_file(GROUND_TRUTH)

    logger.info("--- Analysis 1: F1 as a function of overlap ---")
    per_tile = build_per_tile(args.scoring_dir, common_bounds, gdf_ref)

    arms_block = {}
    for arm, counts in per_tile.items():
        tp, fp, fn = (counts[k].sum() for k in ("tp", "fp", "fn"))
        p, r, f = micro_f1(tp, fp, fn)
        arms_block[arm] = {
            "overlap_fraction": ARM_OVERLAP[arm],
            "tiles_per_pass": ARM_TILES[arm],
            "tp": float(tp), "fp": float(fp), "fn": float(fn),
            "precision": p, "recall": r, "micro_f1": f,
        }

    contrasts = {}
    for hi, lo in (("armA", "armB"), ("armA", "armC"), ("armB", "armC")):
        key = f"{hi}_vs_{lo}"
        contrasts[key] = {
            "primary": paired_bootstrap(per_tile[hi], per_tile[lo], args.bootstrap),
            "sensitivity": paired_bootstrap(
                per_tile[hi], per_tile[lo], args.sensitivity),
        }
        pr = contrasts[key]["primary"]
        logger.info(
            "%s: delta F1 = %+.4f, CI95 [%+.4f, %+.4f], p = %.4f%s",
            key, pr["delta"], pr["ci_lower"], pr["ci_upper"], pr["p_two_sided"],
            "  (excludes 0)" if pr["excludes_zero"] else "",
        )

    logger.info("--- Analysis 2: cost-efficiency ---")
    costs = audited_costs()
    for arm in ("armA", "armB", "armC"):
        costs[arm]["micro_f1"] = arms_block[arm]["micro_f1"]
        costs[arm]["f1_per_usd"] = (
            arms_block[arm]["micro_f1"] / costs[arm]["total_usd"]
            if costs[arm]["total_usd"] else None
        )
    marginal = []
    for base, step in (("armA", "armB"), ("armB", "armC"), ("armA", "armC")):
        d_f1 = arms_block[step]["micro_f1"] - arms_block[base]["micro_f1"]
        d_usd = costs[step]["total_usd"] - costs[base]["total_usd"]
        marginal.append({
            "from": base, "to": step,
            "delta_f1": d_f1, "delta_usd": round(d_usd, 6),
            "f1_per_additional_usd": d_f1 / d_usd if d_usd else None,
        })
        logger.info(
            "%s -> %s: dF1 = %+.4f for +$%.2f (%.4f F1 per additional $)",
            base, step, d_f1, d_usd, d_f1 / d_usd if d_usd else float("nan"),
        )

    logger.info("--- Analysis 3: edge detection ---")
    edges = edge_analysis(args.scoring_dir, common_bounds, gdf_ref, common_geom)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "name": "common (arm A n arm B n arm C)",
            "carrier_tiles": len(common_bounds),
            "area_km2": common_geom.area / 1e6,
            "buffer_metres": BUFFER_M,
            "dedup_metres": 20.0,
            "runs_per_arm": len(RUNS),
        },
        "f1_vs_overlap": {"arms": arms_block, "paired_contrasts": contrasts},
        "cost_efficiency": {"per_arm": costs, "marginal": marginal},
        "edge_detection": edges,
    }
    target = args.output_dir / "h13_overlap_analysis.json"
    target.write_text(json.dumps(payload, indent=2))
    logger.info("Wrote %s", target)

    (args.output_dir / "per_tile_counts.json").write_text(json.dumps(
        {arm: {k: v.tolist() for k, v in c.items()} for arm, c in per_tile.items()},
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
