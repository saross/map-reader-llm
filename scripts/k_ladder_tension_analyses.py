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

    **(b) under a D51 clip (v1.1.0).** When the Phase 2 builder
    (``scripts/build_k_ladder_phase2_tables.py`` v1.4.0) was run with
    ``--clip-to-common-area``, a clipped ladder's ``phase2/ladders.json``
    reports clipped F1@20 values, while ``phase2/mcc-test/summary.json`` can
    only hold inference on the as-evaluated (unclipped) cells: the
    compatibility export the permutation instrument reads withholds every
    clipped ladder. A row for a clipped ladder therefore keeps its clipped F1
    values, names its ``score_basis``, and sets every field computed on the
    other basis — the permutation p-value and tier count joined from the
    summary, and the bootstrap intervals and tile-MCC of the unclipped cells —
    to ``null``, listing each under ``withheld`` with its reason (Astra's
    re-review of 2026-10-10). Without a clip, the builder names no basis and
    neither does this table, so its output is unchanged.

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
from scripts.lib_assessed_area import COMMON_AREA_CLIP_NAME  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    TARGET_CRS,
    micro_f1,
    permutation_test_float,
)

logger = logging.getLogger(__name__)

#: 1.1.0 (2026-10-10): the effect-size table withholds the inference of a
#: ladder the D51 gate clipped and names its score basis (Astra's re-review of
#: PR #30, 2026-10-10); 1.0.0: the three analyses.
__version__ = "1.1.0"

#: The score-basis markers the Phase 2 builder
#: (``scripts/build_k_ladder_phase2_tables.py`` v1.4.0) writes into
#: ``phase2/ladders.json`` when a clip is requested: ``score_basis`` on the
#: payload (a record), on each ladder (``{"reported": ...}``) and on each
#: clipped point (a string). They are mirrored here rather than imported from
#: the builder, which prices its families at import time;
#: ``tests/test_k_ladder_tension_basis.py`` pins them to the builder's.
BASIS_CLIPPED = COMMON_AREA_CLIP_NAME
BASIS_AS_EVALUATED = "as-evaluated"

#: The fields of a gold-standard effect-size row that are not on the clipped
#: basis when its ladder is reported clipped, each with the reason it is
#: withheld. ``phase2/mcc-test/summary.json`` is written by
#: ``scripts/k_ladder_mcc_test.py`` from ``phase2/ladders-compat.json``, which
#: withholds every clipped ladder, so whatever it holds for the family was
#: computed on the as-evaluated (unclipped) cells.
NOT_ON_CLIPPED_BASIS: dict[str, str] = {
    "f1_low_ci": "the bootstrap interval of the unclipped K = 1 cell; not "
                 "regenerated on the clipped detections",
    "f1_best_ci": "the bootstrap interval of the unclipped best-rung cell; not "
                  "regenerated on the clipped detections",
    "tile_mcc_low": "tile-MCC of the unclipped K = 1 cell's tile table; not "
                    "regenerated on the clipped detections",
    "tile_mcc_best": "tile-MCC of the unclipped best-rung cell's tile table; not "
                     "regenerated on the clipped detections",
    "p_bh": "the BH-adjusted K = 1 -> best-rung permutation p-value of "
            "phase2/mcc-test/summary.json, computed on the as-evaluated "
            "(unclipped) cells; no permutation test exists on the clipped basis",
    "n_tiers": "the statistical tier count of phase2/mcc-test/summary.json, "
               "computed on the as-evaluated (unclipped) cells",
    "one_tier": "the tier classification derived from n_tiers, which is withheld",
}

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


def phase2_row_basis(
    ladder: dict[str, Any], *points: dict[str, Any]
) -> str | None:
    """The score basis a Phase 2 ladder's effect-size row is reported on.

    Reads the markers the Phase 2 builder writes (:data:`BASIS_CLIPPED`).
    The row is clipped when the ladder's ``score_basis`` reports the clip,
    or when any point the row reads carries the clipped ``score_basis``: the
    builder clips every point of a clipped ladder or refuses the ladder, so
    the second test only matters to a payload trimmed after the build.

    Args:
        ladder: One ladder of ``phase2/ladders.json``.
        *points: The operating points the row reads (K = 1 and the best rung).

    Returns:
        :data:`BASIS_CLIPPED`, the ladder's named basis otherwise, or ``None``
        when nothing names a basis — an unclipped build, whose rows gain no
        field.
    """
    reported = (ladder.get("score_basis") or {}).get("reported")
    if reported == BASIS_CLIPPED or any(
        point.get("score_basis") == BASIS_CLIPPED for point in points
    ):
        return BASIS_CLIPPED
    return reported


def withhold_off_basis_fields(row: dict[str, Any]) -> None:
    """Null a clipped row's fields that are not on its basis, and say why.

    Every field of :data:`NOT_ON_CLIPPED_BASIS` is set to ``None`` and listed
    with its reason under ``withheld`` — the shape the Phase 2 builder gives a
    clipped point — so the clipped F1 is never paired with inference computed
    on the unclipped cells.

    Args:
        row: A gold-standard effect-size row (mutated).
    """
    for key in NOT_ON_CLIPPED_BASIS:
        row[key] = None
    row["withheld"] = dict(NOT_ON_CLIPPED_BASIS)


def cmd_effect_sizes(args: argparse.Namespace) -> dict[str, Any]:
    """Assemble every MINIMAL ladder's K = 1 -> best-rung effect size.

    Reads the committed ladder inventories and permutation summaries rather
    than recomputing, so the table is a re-presentation of registered numbers.

    A Phase 2 ladder the D51 gate clipped keeps its clipped F1 values, names
    its ``score_basis`` and has the fields computed on its unclipped cells
    withheld (:func:`withhold_off_basis_fields`); no permutation or bootstrap
    is run here to replace them. Without a clip nothing names a basis and the
    output is unchanged.
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
    # The builder records a payload-level score basis only when a clip was
    # requested (D51); an unclipped build names no basis anywhere, and then
    # neither does any row here, so the table keeps its bytes.
    clip_requested = bool(phase2.get("score_basis"))
    withheld_families: list[str] = []
    for ladder in phase2.get("ladders", []):
        family = ladder.get("family") or ""
        if "MINIMAL" not in family:
            continue
        # A Phase 2 rung carries its figures under the operating-point key,
        # not at the rung's top level: ``rung["opmax"]["f1_20"]``.
        rungs = {int(r["K"]): (r.get("opmax") or {}) for r in ladder["rungs"]}
        if 1 not in rungs or rungs[1].get("f1_20") is None:
            continue
        best_k = max(rungs, key=lambda k: rungs[k].get("f1_20") or -1.0)
        stat = p2_by_family.get(family, {})
        row = {
            "corpus": "gold standard (4 maps, 487 tiles)",
            "ladder": family,
            "buffer_m": ladder.get("headline_buffer_m"),
            "thinking": ladder.get("thinking_level"),
            "modality": ladder.get("modality"),
            "temperature": ladder.get("temperature"),
            "K_low": 1,
            "K_best": best_k,
            "f1_low": rungs[1].get("f1_20"),
            "f1_best": rungs[best_k].get("f1_20"),
            "delta_f1": round(
                rungs[best_k]["f1_20"] - rungs[1]["f1_20"], 6
            ),
            "f1_low_ci": rungs[1].get("f1_20_ci"),
            "f1_best_ci": rungs[best_k].get("f1_20_ci"),
            "tile_mcc_low": rungs[1].get("tile_mcc"),
            "tile_mcc_best": rungs[best_k].get("tile_mcc"),
            "p_bh": stat.get("f1_p_bh_k1_to_best"),
            "n_tiers": stat.get("n_tiers"),
            "one_tier": stat.get("n_tiers") == 1,
            "source": "results/k-ladder-2026-09-12/phase2/ladders.json",
        }
        # D51 (Astra's re-review of PR #30, 2026-10-10): a clipped ladder's F1
        # values are the clipped re-scores, but the summary joined above was
        # computed on its unclipped cells, and so were the point's interval
        # and tile-MCC. Keep the clipped F1, withhold the rest, name the basis.
        basis = phase2_row_basis(ladder, rungs[1], rungs[best_k])
        if basis == BASIS_CLIPPED:
            withhold_off_basis_fields(row)
            withheld_families.append(family)
        if basis is not None or clip_requested:
            row["score_basis"] = basis or BASIS_AS_EVALUATED
        rows.append(row)
    if withheld_families:
        logger.warning(
            "%d gold-standard ladder(s) reported on the clipped basis (%s): "
            "their clipped F1 is kept and the inference computed on the "
            "unclipped cells is withheld (%s)",
            len(withheld_families), BASIS_CLIPPED, "; ".join(withheld_families),
        )

    # The deployment MINIMAL ladders, from the Phase 1 inventory and its
    # permutation summary. That inventory is written by
    # scripts/build_k_ladder_tables.py, which has no clip, so these rows are
    # always as evaluated; they name that basis only beside a clipped table.
    phase1 = json.loads(
        (BASE_DIR / "results" / "k-ladder-2026-09-12"
         / "ladders.json").read_text()
    )
    p1_mcc = json.loads(
        (BASE_DIR / "results" / "k-ladder-2026-09-12" / "mcc-test"
         / "summary.json").read_text()
    )
    p1_by_slug = {e["ladder"]: e for e in p1_mcc.get("ladders", [])}
    # ``family_base`` is NOT unique: stride A and stride B each appear three
    # times (the r2 and standardised references, and for B a 3.7-verifier arm),
    # so the key must also carry the reference and the R1 verdict. Only the
    # R1-compliant r2 ladders belong in this comparison; the 3.7-verifier arm
    # varies the verifier as well as K, which is why findings.md § 3.3 reports
    # it separately.
    slug_of = {
        ("Stride A (g384 ov128), 55-map",
         "best-available-gt-55maps-r2.geojson", True): "55map-stride-a-r2",
        ("Stride B (g384 ov192), 55-map",
         "best-available-gt-55maps-r2.geojson", True): "55map-stride-b-r2",
        ("Stride A (g384 ov128), GS, exact re-verification",
         "mounds-reference.geojson", True): "gs-stride-a",
    }
    for ladder in phase1.get("ladders", []):
        base = ladder.get("family_base") or ladder.get("family") or ""
        key = (
            base,
            Path(ladder.get("reference_file") or "").name,
            bool(ladder.get("r1_verifier")),
        )
        slug = slug_of.get(key)
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
                "thinking": "minimal",
                "modality": "text",
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
                "tile_mcc_low": rungs[1].get("tile_mcc"),
                "tile_mcc_best": rungs[best_k].get("tile_mcc"),
                "p_bh": stat.get("f1_p_bh_k1_to_best"),
                "source": "results/k-ladder-2026-09-12/ladders.json",
            }
        )
        if clip_requested:
            rows[-1]["score_basis"] = BASIS_AS_EVALUATED

    out: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "scope": (
            "every MINIMAL-thinking K ladder in the corpus, K = 1 to its best "
            "rung, both corpora side by side. Figures are re-read from the "
            "committed ladder inventories and permutation summaries, not "
            "recomputed."
        ),
    }
    if clip_requested:
        # Named only under a clip request, so an unclipped table keeps its
        # bytes (the builder's convention, "an unclipped build names no basis").
        out["score_basis"] = {
            "clip_requested": True,
            "clip": BASIS_CLIPPED,
            "per_row": (
                "each row names its score basis. A gold-standard row reported "
                f"{BASIS_CLIPPED!r} carries its ladder's clipped F1@20 values; "
                "every field computed on the unclipped cells (the bootstrap "
                "intervals, tile-MCC, and the permutation p-value and tier "
                "count joined from phase2/mcc-test/summary.json) is null and "
                "listed under 'withheld'. The as-evaluated values remain in "
                "phase2/ladders.json under 'historical_as_evaluated'. Every "
                f"other row is {BASIS_AS_EVALUATED!r}"
            ),
            "n_withheld": len(withheld_families),
        }
    out["n_rows"] = len(rows)
    out["rows"] = rows
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
