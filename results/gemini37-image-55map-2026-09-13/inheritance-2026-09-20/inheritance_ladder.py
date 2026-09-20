#!/usr/bin/env python3
"""
Derive the 3.7 image row's K = 1 and K = 3 rungs by INHERITANCE from its K = 5 legs.

Why this exists
---------------
The project's verifier-ladder method is *inheritance*: one verifier leg is run
over the top-rung union, and every lower-rung candidate takes the probability of
its nearest top-rung candidate within 10 m; a lower-rung candidate with no
top-rung neighbour inside that radius is counted and excluded from scoring. That
is what ``scripts/stride55_ladder.py`` does for the Gemini 3 text row (its
docstring, "probability inheritance by nearest K = 10 candidate within 10 m
(unmatched clusters counted, excluded from scoring, included in cost)") and what
``scripts/gemini37_arm_ladder.py`` does for the 3.7 text row, whose result is
``results/gemini37-55map-2026-08-31/ladder/ladder.json``.

The 3.7 **image** campaign (``gemini37-image-55map-2026-09-13``) did not do that.
It ran a *separate verifier leg per rung* — ``verify_k1_arm{1,2}``,
``verify_k3_arm{1,2}``, ``verify_k5_arm{1,2}`` — six legs over three unions. So
the image row's K = 1 and K = 3 cells are own-leg cells, not inherited ones, and
nobody has measured what the two methods do to the same candidates.

This script measures it. For each arm it gives every K = 1 and K = 3 union
candidate the K = 5 leg's probability of its nearest K = 5 candidate within 10 m,
materialises the resulting cells at the SAME carried operating points as the
own-leg cells, scores them on the r2 board's instrument, and runs the head-to-head
paired tile-swap tests.

The matching rule
-----------------
``stride55_ladder.py`` does not expose its matching as a function — the rule is
inline (``cKDTree(...).query(..., k=1)`` then ``d <= INHERIT_TOL_M``,
lines 435-440 of that file, repeated at lines 201-207 of
``scripts/gemini37_arm_ladder.py``). So the rule is **reproduced** here rather
than imported, with one exception: ``INHERIT_TOL_M`` itself is imported from
``stride55_ladder``, so the 10 m radius is provably the same constant and not a
retyped one.

One difference from the text track is structural and unavoidable: there the
lower-rung unions are *rebuilt* from the first-N passes, because no lower-rung
union was ever built. Here the campaign's lower-rung unions already exist and are
committed (``union_k1.geojson`` 6,985, ``union_k3.geojson`` 8,337,
``union_k5.geojson`` 9,173), and the own-leg cells this comparison is against were
built from exactly those crop manifests. Rebuilding them would change the
comparison from "two verification methods over one candidate set" to "two
verification methods over two candidate sets". So the unions are taken as given
and only the probabilities differ — which is the contrast the PI asked for.

Everything else is *imported* from ``scripts/gemini37_image_55map_r2.py`` — the
frames, the tile re-stamp, the materialiser, the achievable grid, the per-tile
machinery, the permutation tests, the engine recipe — so these cells land on the
same instrument as the cells they are compared against. Nothing in ``scripts/``
is modified.

Stages
------
``ladder``       Inherit, record match and agreement statistics, sweep each
                 inherited rung's achievable grid, write ``ladder.json``, the
                 sweep CSVs, the four carried cells and ``cells_manifest.json``.
``score``        Run ``evaluate_detections.py`` over the four cells on the r2
                 recipe (needs the detections committed first).
``tests``        The four head-to-head paired tile-swap tests plus the arm 2
                 ladder contrasts under each method; writes ``tests.json``.

Usage::

    cd ~/Code/map-reader-llm
    .venv/bin/python results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/\
inheritance_ladder.py --stage ladder --workers 12
    # commit the detections, then:
    .venv/bin/python .../inheritance_ladder.py --stage score --workers 6 --jobs 4
    .venv/bin/python .../inheritance_ladder.py --stage tests

Zero API. Run on sapphire.

Created: 2026-09-20
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import sys
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

PROJECT_ROOT = Path("/home/shawn/Code/map-reader-llm")
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.gemini37_image_55map_r2 import (  # noqa: E402
    ARM_MODEL,
    BUFFER_M,
    N_PERMS,
    REFERENCE,
    SEED,
    _init,
    _score_point,
    achievable_points,
    carried_point,
    engine_command,
    load_frames,
    materialise,
    per_tile_arrays,
    permutation_test_float,
    permutation_test_mcc,
    read_detections,
    rung_frame,
    select_campaign,
    tile_vectors,
    with_carried,
)
from scripts.stride55_ladder import INHERIT_TOL_M  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# The r2 script serves both pools of the image 2x2; bind it to the 3.7 pool so
# rung_frame/carried_point read the same tables the own-leg cells were built from.
CAMPAIGN = select_campaign("g37")

#: The campaign's results home, and this study's own home beneath it. Nothing
#: committed by the campaign is touched.
CAMPAIGN_HOME = PROJECT_ROOT / "results/gemini37-image-55map-2026-09-13"
HOME = CAMPAIGN_HOME / "inheritance-2026-09-20"

#: The rung the probabilities are inherited FROM, and the rungs they are
#: inherited TO.
SOURCE_K = 5
RUNGS = (1, 3)
ARMS = ("arm1", "arm2")


def rung_label(arm: str, k: int) -> str:
    """Sweep label for one inherited rung, e.g. ``IMG-ARM2-K3-inherited``."""
    return f"{CAMPAIGN.prefix}-{arm.upper()}-K{k}-inherited"


def cell_label(arm: str, k: int) -> str:
    """Cell label for one inherited carried cell."""
    return f"{CAMPAIGN.prefix}-{arm.upper()}-K{k}-carried-inherited"


def own_cell_label(arm: str, k: int) -> str:
    """The campaign's own-leg carried cell this rung is compared against."""
    return f"{CAMPAIGN.prefix}-{arm.upper()}-K{k}-carried"


# ---------------------------------------------------------------------------
# Inheritance.
# ---------------------------------------------------------------------------


def inherit(arm: str, k: int) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, dict[str, Any]]:
    """One rung's inherited frame, its own-leg frame, and the match record.

    The rule is ``stride55_ladder.py``' (lines 435-440), reproduced: nearest
    K = 5 candidate by Euclidean distance in EPSG:32635, matched when that
    distance is at most ``INHERIT_TOL_M``; unmatched candidates are counted and
    dropped from the scored set.

    Geometry is shared by the two arms — the unions are the same candidates —
    so the match statistics are arm-invariant by construction and are recorded
    per arm anyway, as the ruling asks.

    Args:
        arm: ``arm1`` or ``arm2``.
        k: The rung, 1 or 3.

    Returns:
        ``(inherited, own, record)``. ``inherited`` is the matched subset with
        ``mound_probability`` replaced by the K = 5 leg's and the own-leg value
        preserved as ``own_leg_probability``; ``own`` is the campaign's own-leg
        frame for the rung, untouched; ``record`` holds the match counts and
        distance quantiles.
    """
    own = rung_frame(arm, k)
    src = rung_frame(arm, SOURCE_K)
    tree = cKDTree(np.c_[src.geometry.x, src.geometry.y])
    dist, idx = tree.query(np.c_[own.geometry.x, own.geometry.y], k=1)
    matched = dist <= INHERIT_TOL_M

    inherited = own[matched].copy()
    inherited["own_leg_probability"] = own.loc[matched, "mound_probability"].to_numpy()
    inherited["mound_probability"] = src["mound_probability"].to_numpy()[idx[matched]]
    inherited["inherit_distance_m"] = dist[matched]

    record = {
        "union_n": int(len(own)),
        "matched": int(matched.sum()),
        "unmatched": int((~matched).sum()),
        "match_dist_p50_m": round(float(np.percentile(dist, 50)), 6),
        "match_dist_p95_m": round(float(np.percentile(dist, 95)), 6),
        "match_dist_max_m": round(float(dist.max()), 6),
        "n_exact_coincident": int((dist == 0.0).sum()),
    }
    return inherited, own, record


def agreement(inherited: gpd.GeoDataFrame, own: gpd.GeoDataFrame,
              arm: str, k: int) -> dict[str, Any]:
    """Candidate-level agreement between the own-leg and inherited probabilities.

    Computed on the MATCHED candidates only — an unmatched candidate has no
    inherited probability to disagree with. The decision threshold is the rung's
    carried ``prob_t``; the vote threshold is common to both methods (the two
    frames are the same candidates with the same votes), so a flip is a
    probability-threshold flip.

    ``mean_signed_delta`` follows the ruling's convention, own-leg minus
    inherited.

    Args:
        inherited: The matched subset carrying both probabilities.
        own: The rung's own-leg frame (all candidates), for the count of
            unmatched candidates the own-leg cell keeps.
        arm: ``arm1`` or ``arm2``.
        k: The rung.

    Returns:
        The agreement record.
    """
    prob_t, min_votes = carried_point(arm, k)
    a = inherited["own_leg_probability"].to_numpy(dtype=float)
    b = inherited["mound_probability"].to_numpy(dtype=float)
    votes = inherited["vote_count"].to_numpy()
    keep_a, keep_b = a >= prob_t, b >= prob_t
    gate = votes >= min_votes
    n_own_full = int(len(materialise(own, prob_t, min_votes)))
    n_own_matched = int((gate & keep_a).sum())
    # The ``*_vote_gated`` counts are the flips that actually reach the cells,
    # and they close the identity
    #     n_kept_inherited_cell = n_kept_own_leg_matched_only
    #                             - n_own_keeps_inherited_drops_vote_gated
    #                             + n_inherited_keeps_own_drops_vote_gated
    # exactly. The ungated counts above are the probability-threshold flip rate
    # the ruling asks for, over every matched candidate; at K = 3 the carried
    # point also demands three votes, so only a subset of those flips changes
    # the cell and the ungated numbers do not reconcile with it on their own.
    return {
        "n_matched": int(len(inherited)),
        "n_identical": int((a == b).sum()),
        "identical_share": round(float((a == b).mean()), 6),
        "decision_threshold": prob_t,
        "min_votes": min_votes,
        "n_flips": int((keep_a != keep_b).sum()),
        "flip_share": round(float((keep_a != keep_b).mean()), 6),
        "n_own_keeps_inherited_drops": int((keep_a & ~keep_b).sum()),
        "n_inherited_keeps_own_drops": int((keep_b & ~keep_a).sum()),
        "n_abs_delta_gt_0.5": int((np.abs(a - b) > 0.5).sum()),
        "mean_abs_delta": round(float(np.abs(a - b).mean()), 6),
        "median_abs_delta": round(float(np.median(np.abs(a - b))), 6),
        "mean_signed_delta_own_minus_inherited": round(float((a - b).mean()), 6),
        "n_flips_vote_gated": int(((keep_a != keep_b) & gate).sum()),
        "n_own_keeps_inherited_drops_vote_gated": int((keep_a & ~keep_b & gate).sum()),
        "n_inherited_keeps_own_drops_vote_gated": int((keep_b & ~keep_a & gate).sum()),
        "n_kept_own_leg_matched_only": n_own_matched,
        "n_kept_own_leg_full_cell": n_own_full,
        "n_dropped_by_inheritance": n_own_full - n_own_matched,
        "n_kept_inherited_cell": int((keep_b & gate).sum()),
    }


# ---------------------------------------------------------------------------
# Stage: ladder — inherit, sweep, materialise.
# ---------------------------------------------------------------------------


def stage_ladder(workers: int) -> int:
    """Inherit every rung, sweep it, write ``ladder.json``, the CSVs and the cells.

    Args:
        workers: Sweep parallelism.

    Returns:
        A process exit status.
    """
    ref, bounds, tile_index = load_frames()
    own_sweeps = json.loads((CAMPAIGN_HOME / "sweeps.json").read_text())["rungs"]

    frames: dict[str, gpd.GeoDataFrame] = {}
    records: dict[str, dict[int, dict[str, Any]]] = {a: {} for a in ARMS}
    for arm in ARMS:
        for k in RUNGS:
            inherited, own, record = inherit(arm, k)
            label = rung_label(arm, k)
            frames[label] = inherited
            record["agreement"] = agreement(inherited, own, arm, k)
            records[arm][k] = record
            logger.info(
                "%-24s union %5d, matched %5d, unmatched %3d (p50 %.2f m, "
                "p95 %.2f m, max %.2f m) | identical %.1f %%, flips %.2f %%",
                label, record["union_n"], record["matched"], record["unmatched"],
                record["match_dist_p50_m"], record["match_dist_p95_m"],
                record["match_dist_max_m"],
                100 * record["agreement"]["identical_share"],
                100 * record["agreement"]["flip_share"])

    tasks = []
    for arm in ARMS:
        for k in RUNGS:
            label = rung_label(arm, k)
            for prob_t, votes in with_carried(achievable_points(frames[label], k), arm, k):
                tasks.append((label, prob_t, votes))
    logger.info("sweeping %d points across %d inherited rungs (%d workers)",
                len(tasks), len(frames), workers)
    with Pool(workers, initializer=_init,
              initargs=(ref, bounds, tile_index, frames)) as pool:
        rows = pool.map(_score_point, tasks, chunksize=2)

    HOME.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "buffer_m": BUFFER_M,
        "reference": REFERENCE,
        "inherit_tol_m": INHERIT_TOL_M,
        "cell": CAMPAIGN.cell,
        "method": (
            "verifier-ladder inheritance, the text track's rule "
            "(scripts/stride55_ladder.py): every K = 1 / K = 3 union candidate "
            "takes the probability of its nearest K = 5 candidate within "
            f"{INHERIT_TOL_M:.0f} m; unmatched candidates are counted and excluded "
            "from scoring."),
        "source_leg": {
            arm: str((CAMPAIGN.root / "verifier" / CAMPAIGN.cell
                      / f"verify_k{SOURCE_K}_{arm}").relative_to(PROJECT_ROOT))
            for arm in ARMS},
        "unions": {
            f"k{k}": str((CAMPAIGN.root / "verifier" / CAMPAIGN.cell
                          / f"union_k{k}.geojson").relative_to(PROJECT_ROOT))
            for k in (1, 3, 5)},
        "arms": {},
    }
    cells: list[dict[str, Any]] = []
    for arm in ARMS:
        for k in RUNGS:
            label = rung_label(arm, k)
            frows = [r for r in rows
                     if r["rung"] == label and r["micro_f1_50"] is not None]
            frows.sort(key=lambda r: (r["prob_t"], r["min_votes"]))
            dest = HOME / f"sweep_{label}.csv"
            with dest.open("w", newline="") as fh:
                w = csvmod.DictWriter(fh, fieldnames=list(frows[0].keys()))
                w.writeheader()
                w.writerows(frows)
            logger.info("wrote %s (%d points)", dest.relative_to(PROJECT_ROOT), len(frows))

            prob_t, votes = carried_point(arm, k)
            carried = next(r for r in frows
                           if abs(r["prob_t"] - prob_t) < 1e-9 and r["min_votes"] == votes)
            f1_best = max(frows, key=lambda r: r["micro_f1_50"])
            mcc_best = max(frows, key=lambda r: r["tile_mcc"])
            own = own_sweeps[f"{CAMPAIGN.prefix}-{arm.upper()}-K{k}"]

            record = records[arm][k]
            record.update({
                "n_sweep_points": len(frows),
                "carried_point": [prob_t, votes],
                "carried": carried,
                "oracle": f1_best,
                "mcc_oracle": mcc_best,
                "own_leg": {"carried": own["carried"],
                            "f1_oracle": own["f1_oracle"],
                            "mcc_oracle": own["mcc_oracle"]},
            })
            payload["arms"].setdefault(arm, {})[str(k)] = record

            sub = materialise(frames[label], float(prob_t), int(votes))
            cdest = HOME / "cells" / cell_label(arm, k) / "detections.geojson"
            cdest.parent.mkdir(parents=True, exist_ok=True)
            sub.to_crs("EPSG:4326").to_file(cdest, driver="GeoJSON")
            cells.append({
                "label": cell_label(arm, k),
                "rung": label,
                "arm": arm,
                "verifier_model": ARM_MODEL[arm][0],
                "verifier_thinking": ARM_MODEL[arm][1],
                "k": k,
                "basis": "carried-inherited",
                "point": f"({float(prob_t):.2f}, k{int(votes)})",
                "n_detections": int(len(sub)),
                "det": str(cdest.relative_to(PROJECT_ROOT)),
            })
            logger.info(
                "%-32s n=%5d (own-leg %5d) | inherited carried F1 %.4f MCC %.4f "
                "vs own-leg F1 %.4f MCC %.4f | inherited F1 oracle %.4f at "
                "(%.2f, k%d) vs own-leg %.4f",
                cell_label(arm, k), len(sub), own["carried"]["n_detections"],
                carried["micro_f1_50"], carried["tile_mcc"],
                own["carried"]["micro_f1_50"], own["carried"]["tile_mcc"],
                f1_best["micro_f1_50"], f1_best["prob_t"], f1_best["min_votes"],
                own["f1_oracle"]["micro_f1_50"])

    (HOME / "ladder.json").write_text(json.dumps(payload, indent=2) + "\n")
    (HOME / "cells_manifest.json").write_text(
        json.dumps({"buffer_m": BUFFER_M, "reference": REFERENCE,
                    "cells": cells}, indent=2) + "\n")
    logger.info("wrote %s and %s", (HOME / "ladder.json").relative_to(PROJECT_ROOT),
                (HOME / "cells_manifest.json").relative_to(PROJECT_ROOT))
    return 0


# ---------------------------------------------------------------------------
# Stage: score on the r2 recipe.
# ---------------------------------------------------------------------------


def stage_score(workers: int, jobs: int) -> int:
    """Score the four inherited cells with the engine, on the board's recipe.

    Mirrors ``gemini37_image_55map_r2.stage_score``: the same engine command via
    ``engine_command``, the same git-cleanliness precheck that
    ``--require-clean-inputs`` demands, one ``score.log`` per cell.

    Args:
        workers: Engine parallelism per cell.
        jobs: Cells scored concurrently.

    Returns:
        A process exit status.
    """
    import subprocess
    from concurrent.futures import ThreadPoolExecutor

    cells = json.loads((HOME / "cells_manifest.json").read_text())["cells"]
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", *[c["det"] for c in cells]],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip()
    if dirty:
        logger.error("detections not committed — --require-clean-inputs would "
                     "refuse them. Commit these first:\n%s", dirty)
        return 4

    def run_one(cell: dict[str, Any]) -> tuple[str, int]:
        out_dir = str((HOME / "cells" / cell["label"]).relative_to(PROJECT_ROOT))
        cmd = engine_command(cell["det"], out_dir, cell["label"], workers)
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                              text=True, check=False)
        (HOME / "cells" / cell["label"] / "score.log").write_text(
            proc.stdout + proc.stderr)
        return cell["label"], proc.returncode

    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for label, rc in pool.map(run_one, cells):
            logger.info("scored %-34s rc=%d", label, rc)
            if rc != 0:
                failed.append(label)
    if failed:
        logger.error("scoring FAILED for %s — see each cell's score.log", failed)
        return 1
    logger.info("scored %d cells", len(cells))
    return 0


# ---------------------------------------------------------------------------
# Stage: the head-to-head tests.
# ---------------------------------------------------------------------------


def build_tests() -> list[tuple[str, str, str, str]]:
    """The declared contrast list, as ``(id, a_label, b_label, why)``.

    H1-H4 are the head-to-head: the same rung, the same candidates, the same
    carried point, verified two ways. The sign convention is own-leg minus
    inherited throughout, so a positive difference favours the own-leg method.

    L1-L4 are the arm 2 ladder contrasts under each method. L3 is the contrast
    the campaign's current documents report; L4 is its inheritance counterpart,
    and is *pure* because the K = 5 cell is the inheritance source leg itself —
    under inheritance there is nothing to derive at the top rung.
    """
    tests: list[tuple[str, str, str, str]] = []
    for i, (arm, k) in enumerate([(a, kk) for a in ARMS for kk in RUNGS], start=1):
        tests.append((
            f"H{i}", own_cell_label(arm, k), cell_label(arm, k),
            f"head-to-head {arm} K = {k}: own verifier leg vs inheritance from "
            f"the K = {SOURCE_K} leg, same union, same carried point"))
    tests += [
        ("L1", "IMG-ARM2-K3-carried", "IMG-ARM2-K1-carried",
         "arm 2 ladder K1 -> K3, own-leg method (both rungs own-leg)"),
        ("L2", "IMG-ARM2-K3-carried-inherited", "IMG-ARM2-K1-carried-inherited",
         "arm 2 ladder K1 -> K3, inheritance method (both rungs inherited)"),
        ("L3", "IMG-ARM2-K5-carried", "IMG-ARM2-K3-carried",
         "arm 2 ladder K3 -> K5 as the campaign's current documents report it "
         "(both rungs own-leg)"),
        ("L4", "IMG-ARM2-K5-carried", "IMG-ARM2-K3-carried-inherited",
         "arm 2 ladder K3 -> K5 under inheritance: the K = 5 cell IS the "
         "inheritance source leg, so this is the pure inheritance ladder contrast"),
    ]
    return tests


def cell_path(label: str) -> Path:
    """Detections path for a cell label, in whichever home holds it."""
    home = HOME if label.endswith("-inherited") else CAMPAIGN_HOME
    return home / "cells" / label / "detections.geojson"


def stage_tests() -> int:
    """Run every declared contrast on both metrics and write ``tests.json``."""
    ref, bounds, tile_index = load_frames()
    tests = build_tests()

    def vectors(label: str) -> dict[str, Any]:
        det = read_detections(cell_path(label))
        tp, fp, fn = per_tile_arrays(det, ref, bounds, tile_index)
        truth, pred, conf = tile_vectors(det, ref, bounds)
        return {"tp": tp, "fp": fp, "fn": fn, "truth": truth, "pred": pred,
                "confusion": conf, "n": int(len(det))}

    cache: dict[str, dict[str, Any]] = {}
    for label in sorted({lbl for _, a, b, _ in tests for lbl in (a, b)}):
        cache[label] = vectors(label)
        logger.info("loaded %-34s n=%5d", label, cache[label]["n"])

    f1_rows, mcc_rows = [], []
    for tid, a_label, b_label, why in tests:
        a, b = cache[a_label], cache[b_label]
        if not np.array_equal(a["truth"], b["truth"]):
            logger.error("truth vectors differ for %s vs %s — different frames",
                         a_label, b_label)
            return 3
        f1_rows.append({
            "test": tid, "a": a_label, "b": b_label, "contrast": why,
            **permutation_test_float(a["tp"], a["fp"], a["fn"],
                                     b["tp"], b["fp"], b["fn"],
                                     n_permutations=N_PERMS, seed=SEED)})
        mcc_rows.append({
            "test": tid, "a": a_label, "b": b_label, "contrast": why,
            **permutation_test_mcc(a["pred"], b["pred"], a["truth"],
                                   n_permutations=N_PERMS, seed=SEED)})

    out = {
        "purpose": (
            "Does deriving the image row's lower rungs by inheritance from its "
            "K = 5 legs — the project's own verifier-ladder method — differ from "
            "the per-rung verifier legs the campaign actually ran? Head-to-head "
            "on the same candidates at the same carried points, plus the arm 2 "
            "ladder contrasts under each method."),
        "buffer_m": BUFFER_M,
        "reference": REFERENCE,
        "inherit_tol_m": INHERIT_TOL_M,
        "n_permutations": N_PERMS,
        "seed": SEED,
        "delta_convention": "observed_diff = a - b, i.e. own-leg minus inherited on H1-H4",
        "cells": {k: str(cell_path(k).relative_to(PROJECT_ROOT)) for k in cache},
        "n_detections": {k: v["n"] for k, v in cache.items()},
        "tile_confusion": {k: v["confusion"] for k, v in cache.items()},
        "multiplicity": (
            "No Benjamini-Hochberg adjustment: this is a method-comparison probe "
            "of contrasts that already exist on the board, not a new declared "
            "family. Raw p-values are reported, and the verdict is read against "
            "the E89 drift floor (reports/image-2x2-tests-declaration-2026-09-19.md "
            "section 5 caveat 1), not against a significance threshold."),
        "f1_tests": f1_rows,
        "mcc_tests": mcc_rows,
    }
    HOME.mkdir(parents=True, exist_ok=True)
    dest = HOME / "tests.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    for r in f1_rows:
        logger.info("F1  (%s) %-34s vs %-34s %.4f vs %.4f d=%+.4f p=%.4f",
                    r["test"], r["a"], r["b"], r["f1_a"], r["f1_b"],
                    r["observed_diff"], r["p_value"])
    for r in mcc_rows:
        logger.info("MCC (%s) %-34s vs %-34s %.4f vs %.4f d=%+.4f p=%.4f",
                    r["test"], r["a"], r["b"], r["mcc_a"], r["mcc_b"],
                    r["observed_diff"], r["p_value"])
    logger.info("wrote %s", dest.relative_to(PROJECT_ROOT))
    return 0


def main() -> int:
    """Parse arguments and dispatch to a stage."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True, choices=("ladder", "score", "tests"))
    ap.add_argument("--workers", type=int, default=12,
                    help="Sweep parallelism, or engine workers per cell")
    ap.add_argument("--jobs", type=int, default=4,
                    help="Cells scored concurrently in --stage score")
    args = ap.parse_args()
    if args.stage == "ladder":
        return stage_ladder(args.workers)
    if args.stage == "score":
        return stage_score(args.workers, args.jobs)
    return stage_tests()


if __name__ == "__main__":
    raise SystemExit(main())
