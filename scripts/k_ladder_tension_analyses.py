#!/usr/bin/env python3
"""
The MINIMAL-ladder tension: is the corpora's disagreement about K a scale effect?
================================================================================

Description:
    `results/k-ladder-2026-09-12/findings.md` records a tension it does not
    resolve. On the **deployment** corpus (55 maps, 8,541 tiles) the MINIMAL
    stride ladders gain a lot from K and gain it significantly — stride B
    +0.0547 F1@50 from K = 1 to K = 10, BH p < 0.0001. On the **gold standard**
    (4 maps, 487 tiles) the MINIMAL ladders gain +0.0139 to +0.0629 and four of
    six are a single statistical tier in which K buys nothing detectable. Two
    readings compete:

    - **the scale reading** — the effect is the same size on both corpora, and
      the gold standard simply has 17.5x fewer tiles, so the instrument cannot
      resolve it;
    - **the corpus reading** — the effect really is larger at deployment, where
      the proposer meets 55 unseen sheets rather than the 4 it was calibrated
      on, so extra passes have more to find.

    Three analyses, all US$0, all on sapphire:

    **(a) The subsample test, which is the one that separates the readings.**
    The deployment ladders are re-tested on random **487-tile** subsets of their
    own 8,541 tiles — 200 draws, seed 42 — with the ladder's own instrument
    (round-robin tile-swap permutation over the four rungs, 10,000 permutations,
    BH q = 0.05 within each draw's six pairs). If the gain stays significant in
    most draws, the corpora differ for a reason other than tile count and the
    corpus reading is supported. If significance collapses, the gold standard's
    null results are a power limitation and the scale reading is supported.
    This holds the corpus, the reference, the recipe and the cells fixed and
    varies only the number of tiles scored, which no comparison across the two
    corpora can do.

    **(b) The effect-size table.** Every MINIMAL ladder on both corpora, K = 1
    to its best rung, with the delta, its bootstrap interval and its BH p,
    read from the committed artefacts rather than recomputed — so the two
    corpora's effect sizes can be compared without reference to significance.

    **(c) The grid overlap comparison.** The grid study's consensus-only
    K = 1/3/5/10 ladders exist at four (tile size x overlap) geometries at
    fixed MINIMAL text T 0.7, which isolates whether K's return depends on the
    geometry rather than on the corpus. The verified B-geometry ladder tier E
    bought is set beside them.

Usage::

    # All three, on sapphire
    python scripts/k_ladder_tension_analyses.py --all

    # One at a time
    python scripts/k_ladder_tension_analyses.py --subsample --draws 200
    python scripts/k_ladder_tension_analyses.py --effect-sizes
    python scripts/k_ladder_tension_analyses.py --grid-overlap

Outputs:
    results/k-ladder-2026-09-12/tension/subsample.json
    results/k-ladder-2026-09-12/tension/effect-sizes.json
    results/k-ladder-2026-09-12/tension/grid-overlap.json
    results/k-ladder-2026-09-12/tension/tables.md

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

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
)
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    TARGET_CRS,
    micro_f1,
    permutation_test_float,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

OUT_DIR = BASE_DIR / "results" / "k-ladder-2026-09-12" / "tension"

#: The deployment board the stride ladders' rungs are cells of.
BOARD_55MAP = BASE_DIR / "results" / "55map-final-board-r2-2026-09-06"
GT_55MAP = (
    BASE_DIR / "inputs" / "vectors" / "references"
    / "best-available-gt-55maps-r2.geojson"
)
BOUNDS_55MAP = (
    BASE_DIR / "inputs" / "vectors" / "bounds" / "384"
    / "55maps_evaluation_bounds.geojson"
)

#: The 55-map ladders' headline buffer, and the gold standard's.
BUFFER_55MAP = 50
BUFFER_GS = 20

#: The gold standard's tile count — the subsample size, so the deployment
#: ladders are tested at exactly the gold standard's scale.
GS_N_TILES = 487

N_PERMUTATIONS = 10_000
SEED = 42
BH_Q = 0.05

#: The two deployment MINIMAL ladders, as board cell labels per rung.
DEPLOYMENT_LADDERS: dict[str, dict[str, Any]] = {
    "55map-stride-a-r2": {
        "family": "Stride A (g384 ov128), 55-map, r2",
        "cells": {1: "A-N1-oracle", 3: "A-N3-oracle", 5: "A-N5-oracle",
                  10: "A-N10-oracle"},
    },
    "55map-stride-b-r2": {
        "family": "Stride B (g384 ov192), 55-map, r2",
        "cells": {1: "B-N1-oracle", 3: "B-N3-oracle", 5: "B-N5-oracle",
                  10: "B-N10-oracle"},
    },
}


def bh_adjust(p_values: list[float]) -> list[float]:
    """Benjamini-Hochberg step-up adjustment, the project's convention.

    Args:
        p_values: Raw two-sided p-values.

    Returns:
        BH-adjusted p-values in the input order.
    """
    n = len(p_values)
    order = sorted(range(n), key=lambda i: p_values[i])
    adjusted = [0.0] * n
    running = 1.0
    for rank, idx in enumerate(reversed(order), start=1):
        position = n - rank + 1
        running = min(running, p_values[idx] * n / position)
        adjusted[idx] = running
    return adjusted


# --- (a) the subsample test -------------------------------------------------


def per_tile_table(
    detections: Path,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Build one cell's per-tile TP/FP/FN arrays on a fixed tile order.

    Args:
        detections: The cell's committed detections GeoJSON.
        gdf_ref: The reference.
        gdf_bounds: The frame, whose ``tile_name`` order fixes the array order.
        buffer_metres: Matching tolerance.

    Returns:
        ``(tp, fp, fn, tile_names)`` — three float arrays and the tile order.
    """
    gdf_det = gpd.read_file(detections)
    # Every input is projected to the metric CRS before matching, exactly as
    # ``era1_leaderboard_tiering.load_geojson`` (:232-235) and its
    # reference/bounds loader (:665-666) do. Without this the committed cells'
    # EPSG:4326 detections are matched against EPSG:32635 references at a 50 m
    # tolerance expressed in degrees, which books every reference as a false
    # negative and yields a micro-F1 of 0.0000 — the shape the rebuild gate
    # caught on the first run of this script.
    if gdf_det.crs is None:
        gdf_det = gdf_det.set_crs("EPSG:4326")
    gdf_det = gdf_det.to_crs(TARGET_CRS)
    table = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres
    )
    table = table.set_index("tile_name")
    order = list(gdf_bounds["tile_name"])
    table = table.reindex(order).fillna(0.0)
    return (
        table["tp"].to_numpy(dtype=float),
        table["fp"].to_numpy(dtype=float),
        table["fn"].to_numpy(dtype=float),
        order,
    )


def committed_f1(cell: str, buffer_metres: int) -> float:
    """Read a board cell's committed F1 at one buffer, for the gate."""
    path = BOARD_55MAP / "cells" / cell / "evaluation.json"
    doc = json.loads(path.read_text())
    for entry in doc["summary"]["buffers"]:
        if int(entry["buffer_metres"]) == buffer_metres:
            return float(entry["f1"])
    raise KeyError(f"{cell}: no buffer {buffer_metres} in {path}")


def subsample_ladder(
    slug: str,
    spec: dict[str, Any],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    *,
    draws: int,
) -> dict[str, Any]:
    """Re-test one deployment ladder on random gold-standard-sized subsets.

    Args:
        slug: The ladder's mcc-test slug.
        spec: Its entry of :data:`DEPLOYMENT_LADDERS`.
        gdf_ref: The r2 reference.
        gdf_bounds: The 8,541-tile deployment frame.
        draws: Number of random subsets.

    Returns:
        The ladder's result block.
    """
    ks = sorted(spec["cells"])
    tables: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    gate: list[dict[str, Any]] = []
    for k in ks:
        cell = spec["cells"][k]
        tp, fp, fn, order = per_tile_table(
            BOARD_55MAP / "cells" / cell / "detections.geojson",
            gdf_ref,
            gdf_bounds,
            BUFFER_55MAP,
        )
        tables[k] = (tp, fp, fn)
        rebuilt = micro_f1(tp.sum(), fp.sum(), fn.sum())
        recorded = committed_f1(cell, BUFFER_55MAP)
        gate.append(
            {
                "K": k,
                "cell": cell,
                "rebuilt_micro_f1": round(float(rebuilt), 6),
                "committed_f1": round(recorded, 6),
                "gap": round(float(rebuilt) - recorded, 6),
                "passed": abs(float(rebuilt) - recorded) < 5e-4,
            }
        )
        logger.info(
            "%s K=%d: rebuilt %.6f against committed %.6f (gap %+.6f)",
            slug, k, rebuilt, recorded, float(rebuilt) - recorded,
        )
    if not all(entry["passed"] for entry in gate):
        logger.error("%s: per-tile rebuild gate FAILED — not subsampling", slug)
        return {"ladder": slug, "family": spec["family"], "gate": gate,
                "gate_passed": False, "draws": []}

    n_tiles = len(tables[ks[0]][0])
    pairs = [(a, b) for i, a in enumerate(ks) for b in ks[i + 1:]]
    target = (ks[0], ks[-1])

    rng = np.random.default_rng(SEED)
    results: list[dict[str, Any]] = []
    for draw in range(draws):
        idx = rng.choice(n_tiles, size=GS_N_TILES, replace=False)
        raw: list[float] = []
        deltas: list[float] = []
        for low, high in pairs:
            tp_h, fp_h, fn_h = (arr[idx] for arr in tables[high])
            tp_l, fp_l, fn_l = (arr[idx] for arr in tables[low])
            # Oriented (higher K) - (lower K), as findings.md § 4.1 orients it.
            out = permutation_test_float(
                tp_h, fp_h, fn_h, tp_l, fp_l, fn_l,
                n_permutations=N_PERMUTATIONS,
                seed=SEED + draw,
            )
            raw.append(float(out["p_value"]))
            deltas.append(float(out["observed_diff"]))
        adjusted = bh_adjust(raw)
        position = pairs.index(target)
        results.append(
            {
                "draw": draw,
                "delta_f1": round(deltas[position], 6),
                "p_raw": round(raw[position], 6),
                "p_bh": round(adjusted[position], 6),
                "significant": adjusted[position] <= BH_Q,
                "n_pairs_significant": sum(p <= BH_Q for p in adjusted),
            }
        )
        if (draw + 1) % 25 == 0:
            done = sum(r["significant"] for r in results)
            logger.info(
                "%s: %d/%d draws, %d significant so far",
                slug, draw + 1, draws, done,
            )

    significant = [r for r in results if r["significant"]]
    values = np.array([r["delta_f1"] for r in results], dtype=float)
    full = permutation_test_float(
        *tables[ks[-1]], *tables[ks[0]],
        n_permutations=N_PERMUTATIONS, seed=SEED,
    )
    return {
        "ladder": slug,
        "family": spec["family"],
        "gate": gate,
        "gate_passed": True,
        "n_tiles_full": n_tiles,
        "n_tiles_subset": GS_N_TILES,
        "pair_tested": f"K={target[0]} -> K={target[1]}",
        "pairs_in_family": [f"K{a}->K{b}" for a, b in pairs],
        "full_corpus": {
            "delta_f1": round(float(full["observed_diff"]), 6),
            "p_raw": round(float(full["p_value"]), 6),
        },
        "n_draws": draws,
        "n_significant": len(significant),
        "fraction_significant": round(len(significant) / draws, 4),
        "delta_distribution": {
            "mean": round(float(values.mean()), 6),
            "sd": round(float(values.std(ddof=1)), 6),
            "min": round(float(values.min()), 6),
            "p05": round(float(np.percentile(values, 5)), 6),
            "median": round(float(np.median(values)), 6),
            "p95": round(float(np.percentile(values, 95)), 6),
            "max": round(float(values.max()), 6),
            "n_negative": int((values < 0).sum()),
        },
        "draws": results,
    }


def cmd_subsample(args: argparse.Namespace) -> dict[str, Any]:
    """Run analysis (a) for both deployment MINIMAL ladders."""
    gdf_ref = gpd.read_file(GT_55MAP).to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file(BOUNDS_55MAP).to_crs(TARGET_CRS)
    logger.info(
        "reference %d records; frame %d tiles", len(gdf_ref), len(gdf_bounds)
    )
    ladders = [
        subsample_ladder(slug, spec, gdf_ref, gdf_bounds, draws=args.draws)
        for slug, spec in DEPLOYMENT_LADDERS.items()
    ]
    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "question": (
            "Does the deployment MINIMAL ladders' K = 1 -> K = 10 F1 gain stay "
            "BH-significant when only 487 of the 8,541 tiles are scored — the "
            "gold standard's tile count?"
        ),
        "instrument": (
            "round-robin tile-swap permutation over the ladder's four rungs, "
            f"{N_PERMUTATIONS} permutations, BH q = {BH_Q} within each draw's "
            "six pairs — the instrument findings.md § 4.1 used, at a different "
            "tile count"
        ),
        "reference": str(GT_55MAP.relative_to(BASE_DIR)),
        "frame": str(BOUNDS_55MAP.relative_to(BASE_DIR)),
        "buffer_m": BUFFER_55MAP,
        "seed": SEED,
        "n_draws": args.draws,
        "subset_size": GS_N_TILES,
        "ladders": ladders,
    }
    path = OUT_DIR / "subsample.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n")
    logger.info("-> %s", path.relative_to(BASE_DIR))
    return out


# --- (b) the effect-size table ----------------------------------------------


def cmd_effect_sizes(args: argparse.Namespace) -> dict[str, Any]:
    """Assemble every MINIMAL ladder's K = 1 -> best-rung effect size.

    Reads the committed ladder inventories and permutation summaries rather
    than recomputing, so the table is a re-presentation of registered numbers.
    """
    rows: list[dict[str, Any]] = []

    # The gold-standard MINIMAL ladders: Phase 2's six (three text, three
    # image) plus the scale-4-optimal cell, from the Phase 2 ladder tables.
    phase2 = json.loads(
        (BASE_DIR / "results" / "k-ladder-2026-09-12" / "phase2"
         / "ladders.json").read_text()
    )
    p2_mcc = json.loads(
        (BASE_DIR / "results" / "k-ladder-2026-09-12" / "phase2" / "mcc-test"
         / "summary.json").read_text()
    )
    p2_by_family = {
        entry.get("family") or entry.get("ladder"): entry
        for entry in p2_mcc.get("ladders", [])
    }
    for ladder in phase2.get("ladders", []):
        family = ladder.get("family") or ""
        if "MINIMAL" not in family:
            continue
        rungs = {int(r["K"]): r for r in ladder["rungs"]}
        if 1 not in rungs:
            continue
        best_k = max(rungs, key=lambda k: rungs[k].get("f1_headline") or -1.0)
        stat = p2_by_family.get(family, {})
        rows.append(
            {
                "corpus": "gold standard (4 maps, 487 tiles)",
                "ladder": family,
                "buffer_m": ladder.get("headline_buffer_m"),
                "K_low": 1,
                "K_best": best_k,
                "f1_low": rungs[1].get("f1_headline"),
                "f1_best": rungs[best_k].get("f1_headline"),
                "delta_f1": (
                    round(rungs[best_k]["f1_headline"]
                          - rungs[1]["f1_headline"], 6)
                    if rungs[best_k].get("f1_headline") is not None
                    and rungs[1].get("f1_headline") is not None else None
                ),
                "ci_low": rungs[1].get("f1_ci_low"),
                "ci_high": rungs[1].get("f1_ci_high"),
                "p_bh": stat.get("f1_p_bh_k1_to_best"),
                "one_tier": stat.get("n_tiers") == 1,
                "source": "results/k-ladder-2026-09-12/phase2/ladders.json",
            }
        )

    # The deployment MINIMAL ladders, from the Phase 1 inventory and its
    # permutation summary.
    phase1 = json.loads(
        (BASE_DIR / "results" / "k-ladder-2026-09-12"
         / "ladders.json").read_text()
    )
    p1_mcc = json.loads(
        (BASE_DIR / "results" / "k-ladder-2026-09-12" / "mcc-test"
         / "summary.json").read_text()
    )
    p1_by_slug = {e["ladder"]: e for e in p1_mcc.get("ladders", [])}
    slug_of = {
        "Stride A (g384 ov128), 55-map": "55map-stride-a-r2",
        "Stride B (g384 ov192), 55-map": "55map-stride-b-r2",
        "Stride A (g384 ov128), GS, exact re-verification": "gs-stride-a",
    }
    for ladder in phase1.get("ladders", []):
        base = ladder.get("family_base") or ladder.get("family") or ""
        slug = slug_of.get(base)
        if slug is None:
            continue
        rungs = {int(r["K"]): r for r in ladder["rungs"]}
        if 1 not in rungs:
            continue
        best_k = max(rungs, key=lambda k: rungs[k].get("f1_headline") or -1.0)
        stat = p1_by_slug.get(slug, {})
        corpus = (
            "gold standard (4 maps, 487 tiles)"
            if "GS" in base else "deployment (55 maps, 8,541 tiles)"
        )
        rows.append(
            {
                "corpus": corpus,
                "ladder": ladder.get("family"),
                "buffer_m": ladder.get("headline_buffer_m"),
                "K_low": 1,
                "K_best": best_k,
                "f1_low": rungs[1].get("f1_headline"),
                "f1_best": rungs[best_k].get("f1_headline"),
                "delta_f1": (
                    round(rungs[best_k]["f1_headline"]
                          - rungs[1]["f1_headline"], 6)
                    if rungs[best_k].get("f1_headline") is not None
                    and rungs[1].get("f1_headline") is not None else None
                ),
                "p_bh": stat.get("f1_p_bh_k1_to_best"),
                "source": "results/k-ladder-2026-09-12/ladders.json",
            }
        )

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "scope": (
            "every MINIMAL-thinking K ladder in the corpus, K = 1 to its best "
            "rung, both corpora side by side. Figures are re-read from the "
            "committed ladder inventories and permutation summaries, not "
            "recomputed."
        ),
        "n_rows": len(rows),
        "rows": rows,
    }
    path = OUT_DIR / "effect-sizes.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n")
    logger.info("%d MINIMAL ladder(s) -> %s", len(rows),
                path.relative_to(BASE_DIR))
    return out


# --- (c) the grid overlap comparison ----------------------------------------


def cmd_grid_overlap(args: argparse.Namespace) -> dict[str, Any]:
    """Tabulate the grid study's K gain by overlap and tile size.

    The grid sweep is consensus-only (no verifier), at fixed MINIMAL text
    T 0.7, over four (tile size x overlap) cells at K = 1, 3, 5, 10. For each
    cell the best F1@20 over the (corroboration, vote) grid is taken at each K,
    which is how ``results/grid-2026-08-18/findings.md`` reads that sweep.
    """
    sweep = BASE_DIR / "results" / "grid-2026-08-18" / "sweep.csv"
    best: dict[tuple[str, int], dict[str, Any]] = {}
    meta: dict[str, dict[str, Any]] = {}
    with open(sweep, newline="") as handle:
        for row in csv.DictReader(handle):
            cell = row["cell"]
            k = int(row["K"])
            f1 = float(row["f1"])
            meta.setdefault(cell, {
                "label": row["label"],
                "tile_px": int(row["tile_px"]),
                "overlap_frac": float(row["overlap_frac"]),
            })
            key = (cell, k)
            if key not in best or f1 > best[key]["f1"]:
                best[key] = {
                    "f1": f1,
                    "mcc": float(row["mcc"]),
                    "min_corroboration": int(row["min_corroboration"]),
                    "min_votes": int(row["min_votes"]),
                    "n_detections": int(row["n_detections"]),
                }

    cells: list[dict[str, Any]] = []
    for cell, info in sorted(
        meta.items(), key=lambda kv: (-kv[1]["overlap_frac"], kv[1]["tile_px"])
    ):
        rungs = {k: best[(cell, k)] for k in (1, 3, 5, 10) if (cell, k) in best}
        if 1 not in rungs:
            continue
        best_k = max(rungs, key=lambda k: rungs[k]["f1"])
        cells.append(
            {
                "cell": cell,
                "label": info["label"],
                "tile_px": info["tile_px"],
                "overlap_frac": info["overlap_frac"],
                "rungs": {
                    str(k): {
                        "f1_20": round(v["f1"], 6),
                        "mcc": round(v["mcc"], 6),
                        "operating_point": (
                            f"c>={v['min_corroboration']}, "
                            f"k>={v['min_votes']}"
                        ),
                        "n_detections": v["n_detections"],
                    }
                    for k, v in sorted(rungs.items())
                },
                "K_best": best_k,
                "delta_f1_k1_to_best": round(
                    rungs[best_k]["f1"] - rungs[1]["f1"], 6
                ),
                "delta_f1_k1_to_k10": (
                    round(rungs[10]["f1"] - rungs[1]["f1"], 6)
                    if 10 in rungs else None
                ),
                "delta_mcc_k1_to_best": round(
                    rungs[best_k]["mcc"] - rungs[1]["mcc"], 6
                ),
            }
        )

    tier_e: dict[str, Any] | None = None
    tier_e_path = (
        BASE_DIR / "results" / "k-ladder-2026-09-12" / "tier-e" / "scores.json"
    )
    if tier_e_path.exists():
        scores = json.loads(tier_e_path.read_text())
        tier_e = {
            "source": str(tier_e_path.relative_to(BASE_DIR)),
            "note": (
                "the same B geometry (384 px / 50 %) and the same MINIMAL text "
                "pool as grid cell g384_ov192, but VERIFIED and scored on the "
                "board frame at 20 m, so its F1 is not comparable with the "
                "consensus-only column above — only its SHAPE across K is"
            ),
            "rungs": {
                str(row["K"]): {
                    "f1_20": (row.get("opmax") or {}).get("f1_20"),
                    "tile_mcc": (row.get("opmax") or {}).get("tile_mcc"),
                }
                for row in scores.get("rungs", [])
            },
        }
    else:
        logger.warning("tier E scores not present yet: %s", tier_e_path)

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "source": "results/grid-2026-08-18/sweep.csv",
        "scope": (
            "consensus-only K ladders at four (tile size x overlap) geometries, "
            "fixed MINIMAL text T 0.7, best F1@20 over the (corroboration, "
            "vote) grid per K, on the grid-common 487-tile footprint"
        ),
        "n_cells": len(cells),
        "cells": cells,
        "tier_e_verified_b_geometry": tier_e,
    }
    path = OUT_DIR / "grid-overlap.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n")
    logger.info("%d grid cell(s) -> %s", len(cells), path.relative_to(BASE_DIR))
    return out


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--all", action="store_true", help="Run all three")
    parser.add_argument("--subsample", action="store_true", help="Analysis (a)")
    parser.add_argument(
        "--effect-sizes", action="store_true", help="Analysis (b)"
    )
    parser.add_argument(
        "--grid-overlap", action="store_true", help="Analysis (c)"
    )
    parser.add_argument(
        "--draws", type=int, default=200,
        help="Subsample draws for analysis (a) (default: 200)",
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    if not (args.all or args.subsample or args.effect_sizes
            or args.grid_overlap):
        parser.error("choose --all or one of the three analyses")

    if args.all or args.effect_sizes:
        cmd_effect_sizes(args)
    if args.all or args.grid_overlap:
        cmd_grid_overlap(args)
    if args.all or args.subsample:
        cmd_subsample(args)


if __name__ == "__main__":
    main()
