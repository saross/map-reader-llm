#!/usr/bin/env python3
"""
Score the 2026-09-20 batch replicate of a 3.7 image K = 5 verifier leg.

Purpose
-------
This is ``replicate_k5_arm2.py`` **parametrised by arm**. The arm 2 note
(``results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20/findings.md``)
measured the E89 re-invocation drift floor for the arm 2 verifier
(``gemini-3.7-flash``, low thinking, T = 0) and, with it, made the arm 2
K = 3 -> K = 5 micro-F1 gain claimable under the image-2x2 declaration's
replicate rule (``reports/image-2x2-tests-declaration-2026-09-19.md`` § 5
caveat 1). That declaration's "Scope" paragraph records that the **arm 1**
verifier (``gemini-3-flash-preview``, ``minimal``, T = 0) has no measured
floor, so an arm-1 difference of order 0.001 is uncharacterised rather than
known to be drift. This script measures it, on the arm 1 batch replicate of
2026-09-20 (data commit ``5778b5569``).

Everything is *imported* from ``scripts/gemini37_image_55map_r2.py`` — the
frames, the materialiser, the per-tile machinery, the permutation tests, the
engine recipe — so the replicate lands on the same instrument as the cells it
is compared against. Nothing in ``scripts/`` is modified (another agent owns
that file).

What this adds over the arm 2 driver
------------------------------------
The ``agree`` stage reports three extra things the arm 2 note did not need:

* the flip rate at **0.50** and at **0.90** as well as at the arm's own
  carried threshold, so the two verifiers can be compared at a common
  threshold rather than each at its own;
* the **probability vocabulary** of every leg — how many distinct values it
  uses, and its commonest values — because a higher identical-probability
  share can be an artefact of a coarser vocabulary rather than evidence of a
  steadier verifier;
* a **Wilson 95 % interval** on every flip rate, the interval form the
  declaration uses for this proportion.

An ``arm2_reference`` block recomputes the other arm's flip rates at the same
three thresholds and its vocabulary, read-only, from that arm's committed
probabilities, so every cross-arm number in the arm 1 note has a source inside
the arm 1 directory. Nothing in the arm 2 home is written or re-run.

Stages
------
``agree``        Probability-level agreement between the two invocations.
``materialise``  The replicate's carried cell and its own F1 oracle, plus the
                 full achievable-point sweep CSV.
``score``        The r2 engine recipe over both replicate cells.
``tests``        The four paired tile-swap permutation tests (a)-(d).

Usage::

    cd ~/Code/map-reader-llm
    .venv/bin/python <this file> --arm arm1 --stage agree
    .venv/bin/python <this file> --arm arm1 --stage materialise --workers 12
    # commit the detections, then:
    .venv/bin/python <this file> --arm arm1 --stage score --workers 5 --jobs 2
    .venv/bin/python <this file> --arm arm1 --stage tests

Running it with ``--arm arm2`` reproduces the arm 2 note's artefacts into the
arm 2 home; it was not re-run there, so that home keeps the driver and the
artefacts it was published with.

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
import math
import sys
from collections import Counter
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path("/home/shawn/Code/map-reader-llm")
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.final_board_sweeps import load_manifest_probs  # noqa: E402
from scripts.gemini37_image_55map_r2 import (  # noqa: E402
    ARM_MODEL,
    BUFFER_M,
    N_PERMS,
    REFERENCE,
    SEED,
    _init,
    _score_point,
    achievable_points,
    assign_eval_frame_tiles,
    carried_point,
    engine_command,
    load_frames,
    materialise,
    per_tile_arrays,
    permutation_test_float,
    permutation_test_mcc,
    read_detections,
    tile_vectors,
    with_carried,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The 3.7 image campaign's verifier root, the K = 5 crop manifest, and the
#: campaign's own committed cells. Both arms verify the SAME candidates over
#: the SAME union, so only the verify directories differ between them.
VROOT = (PROJECT_ROOT / "outputs/gemini37-image-55map-2026-09-13"
         / "verifier/g384_ov192_55map_g37img")
CROPS_K5 = VROOT / "crops_k5"
CAMPAIGN_HOME = PROJECT_ROOT / "results/gemini37-image-55map-2026-09-13"

#: The rung this driver replicates. Fixed: the replicate legs exist at K = 5
#: only, and the K = 3 comparator is the campaign's committed cell.
K = 5

#: Thresholds at which a decision flip is counted on every arm, beside the
#: arm's own carried threshold. 0.50 is the neutral reading and 0.90 is arm
#: 2's carried point, which makes the two arms comparable at one threshold.
COMMON_THRESHOLDS = (0.50, 0.90)


@dataclass(frozen=True)
class Arm:
    """One verifier arm's pair of K = 5 invocations and where its work lands.

    Attributes:
        key: ``arm1`` or ``arm2``, the key of
            :data:`scripts.gemini37_image_55map_r2.ARM_MODEL`.
        original: The campaign's first invocation of this arm at K = 5.
        replicate: The 2026-09-20 batch re-invocation of it.
        home: Where this arm's replicate artefacts live.
        prefix: The cell-label stem, e.g. ``IMG-ARM1-K5``.
        data_commit: The commit that landed the replicate leg's raw data.
    """

    key: str
    original: Path
    replicate: Path
    home: Path
    prefix: str
    data_commit: str


ARMS = {
    "arm1": Arm(
        key="arm1",
        original=VROOT / "verify_k5_arm1",
        replicate=VROOT / "verify_k5_arm1_replicate-batch-2026-09-20",
        home=CAMPAIGN_HOME / "replicate-k5-arm1-batch-2026-09-20",
        prefix="IMG-ARM1-K5",
        data_commit="5778b5569",
    ),
    "arm2": Arm(
        key="arm2",
        original=VROOT / "verify_k5_arm2",
        replicate=VROOT / "verify_k5_arm2_replicate-batch-2026-09-20",
        home=CAMPAIGN_HOME / "replicate-k5-arm2-batch-2026-09-20",
        prefix="IMG-ARM2-K5",
        data_commit="3f8af3a65",
    ),
}

#: The arm this invocation is bound to; :func:`select_arm` rebinds it and the
#: labels derived from it. The default is arm 1, the arm this file was written
#: for.
ARM: Arm = ARMS["arm1"]
OTHER: Arm = ARMS["arm2"]
REP_HOME: Path = ARM.home
REP_RUNG: str = f"{ARM.prefix}-replicate"


def select_arm(key: str) -> Arm:
    """Bind the module to one verifier arm.

    Args:
        key: ``arm1`` or ``arm2``.

    Returns:
        The selected arm's record.
    """
    global ARM, OTHER, REP_HOME, REP_RUNG
    ARM = ARMS[key]
    OTHER = ARMS["arm2" if key == "arm1" else "arm1"]
    REP_HOME = ARM.home
    REP_RUNG = f"{ARM.prefix}-replicate"
    return ARM


def decision_threshold() -> float:
    """The arm's carried probability threshold at K = 5, from the r2 module.

    Derived rather than retyped: a constant copied into this file could drift
    from the campaign's own carried point without anything noticing.

    Returns:
        The probability threshold of the arm's carried operating point.
    """
    return float(carried_point(ARM.key, K)[0])


# ---------------------------------------------------------------------------
# Stage: probability-level agreement between the two invocations.
# ---------------------------------------------------------------------------


def _probs(vdir: Path) -> dict[str, float]:
    """``candidate_id -> mound_probability`` for one verifier invocation."""
    results = json.loads((vdir / "probabilities.json").read_text())["results"]
    return {k: float(v["mound_probability"]) for k, v in results.items()}


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """The Wilson score interval for a binomial proportion.

    The normal approximation is unreliable at the proportions measured here
    (a few per cent), which is why the declaration quotes Wilson; this is the
    same formula it states, ``(p + z^2/2n +/- z*sqrt(p(1-p)/n + z^2/4n^2)) /
    (1 + z^2/n)``.

    Args:
        successes: Count of the event.
        n: Number of trials.
        z: Normal quantile; 1.96 gives a 95 % interval.

    Returns:
        ``(low, high)`` as proportions.
    """
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1.0 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - half) / denom, (centre + half) / denom)


def flip_block(a: np.ndarray, b: np.ndarray, threshold: float) -> dict[str, Any]:
    """Decision flips between two probability vectors at one threshold.

    A flip is a candidate the two invocations place on opposite sides of the
    threshold. The direction is recorded because a balanced flip count leaves
    the retained set almost the same size while an unbalanced one does not.

    Args:
        a: The original invocation's probabilities.
        b: The replicate's, aligned to ``a``.
        threshold: The decision threshold.

    Returns:
        Counts, shares, the Wilson interval on the flip share, and the kept
        counts on each side.
    """
    keep_a, keep_b = a >= threshold, b >= threshold
    flips = int((keep_a != keep_b).sum())
    low, high = wilson_interval(flips, len(a))
    return {
        "threshold": threshold,
        "n_flips": flips,
        "flip_share": round(flips / len(a), 6),
        "flip_share_wilson95": [round(low, 6), round(high, 6)],
        "n_flips_replicate_keeps_original_drops": int((keep_b & ~keep_a).sum()),
        "n_flips_original_keeps_replicate_drops": int((keep_a & ~keep_b).sum()),
        "n_kept_original": int(keep_a.sum()),
        "n_kept_replicate": int(keep_b.sum()),
    }


def vocabulary(values: np.ndarray, top: int = 10) -> dict[str, Any]:
    """How coarse a leg's probability vocabulary is.

    A verifier that answers on a short list of round numbers will agree with
    itself on more candidates than one that answers on a fine grid, without
    being any steadier in its judgement. Counting the distinct values is what
    separates the two readings.

    Args:
        values: One leg's probabilities.
        top: How many of the commonest values to record.

    Returns:
        The distinct-value count, the share of mass on the commonest value,
        and the ``top`` commonest values with their counts and shares.
    """
    counts = Counter(float(v) for v in values)
    common = counts.most_common(top)
    n = len(values)
    return {
        "n_distinct": len(counts),
        "top_share": round(common[0][1] / n, 6),
        "top_values": [{"value": v, "n": c, "share": round(c / n, 6)}
                       for v, c in common],
    }


def chance_identical(a: np.ndarray, b: np.ndarray) -> float:
    """Identical-probability share expected from the vocabularies alone.

    The share of candidates on which two legs agree exactly is not a clean
    measure of steadiness: a verifier answering on a short list of round
    numbers will hit the same value twice by luck more often than one
    answering on a fine grid. This is the agreement the two legs would reach
    if each drew independently from its own observed marginal distribution of
    probabilities — ``sum_v P_original(v) * P_replicate(v)`` — which is the
    baseline the observed share has to be read against.

    Args:
        a: The original invocation's probabilities.
        b: The replicate's.

    Returns:
        The expected identical share under independence.
    """
    ca, cb = Counter(float(v) for v in a), Counter(float(v) for v in b)
    n = len(a)
    return sum(count * cb.get(value, 0) for value, count in ca.items()) / (n * n)


def agreement_block(orig: dict[str, float], rep: dict[str, float],
                    thresholds: tuple[float, ...]) -> dict[str, Any]:
    """Every agreement statistic for one pair of invocations.

    Args:
        orig: The original invocation's probabilities by candidate id.
        rep: The replicate's.
        thresholds: Decision thresholds at which to count flips.

    Returns:
        A record with the compared count, the identical share, one flip block
        per threshold, the large-jump count, the |dp| summary statistics and
        each leg's probability vocabulary.
    """
    keys = sorted(set(orig) & set(rep))
    if len(keys) != len(orig) or len(keys) != len(rep):
        logger.warning("key sets differ: original %d, replicate %d, shared %d",
                       len(orig), len(rep), len(keys))
    a = np.array([orig[k] for k in keys])
    b = np.array([rep[k] for k in keys])
    identical = int((a == b).sum())
    delta = np.abs(a - b)
    observed = identical / len(keys)
    expected = chance_identical(a, b)
    return {
        "n_candidates_original": len(orig),
        "n_candidates_replicate": len(rep),
        "n_compared": len(keys),
        "n_identical": identical,
        "identical_share": round(observed, 6),
        "chance_identical_share": round(expected, 6),
        "identical_kappa": round((observed - expected) / (1 - expected), 6),
        "flips": [flip_block(a, b, t) for t in thresholds],
        "n_abs_delta_gt_0.5": int((delta > 0.5).sum()),
        "share_abs_delta_gt_0.5": round(float((delta > 0.5).mean()), 6),
        "mean_abs_delta": round(float(delta.mean()), 6),
        "median_abs_delta": round(float(np.median(delta)), 6),
        "p90_abs_delta": round(float(np.quantile(delta, 0.90)), 6),
        "max_abs_delta": round(float(delta.max()), 6),
        "vocabulary_original": vocabulary(a),
        "vocabulary_replicate": vocabulary(b),
    }


def stage_agree() -> int:
    """Write ``agreement.json`` for this arm, with the other arm beside it."""
    carried_t = decision_threshold()
    thresholds = tuple(sorted({carried_t, *COMMON_THRESHOLDS}))
    block = agreement_block(_probs(ARM.original), _probs(ARM.replicate), thresholds)
    other = agreement_block(_probs(OTHER.original), _probs(OTHER.replicate), thresholds)

    out = {
        "arm": ARM.key,
        "verifier_model": ARM_MODEL[ARM.key][0],
        "verifier_thinking": ARM_MODEL[ARM.key][1],
        "k": K,
        "carried_threshold": carried_t,
        "original": str(ARM.original.relative_to(PROJECT_ROOT)),
        "replicate": str(ARM.replicate.relative_to(PROJECT_ROOT)),
        **block,
        "arm2_reference" if ARM.key == "arm1" else "arm1_reference": {
            "note": (
                "The other arm's two committed invocations, recomputed here "
                "read-only at the same thresholds so the cross-arm "
                "comparison in findings.md has a source in this directory. "
                "Nothing in that arm's home is written or re-run."),
            "arm": OTHER.key,
            "verifier_model": ARM_MODEL[OTHER.key][0],
            "verifier_thinking": ARM_MODEL[OTHER.key][1],
            "carried_threshold": float(carried_point(OTHER.key, K)[0]),
            "original": str(OTHER.original.relative_to(PROJECT_ROOT)),
            "replicate": str(OTHER.replicate.relative_to(PROJECT_ROOT)),
            **other,
        },
    }
    REP_HOME.mkdir(parents=True, exist_ok=True)
    dest = REP_HOME / "agreement.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")

    logger.info("%s: %d/%d identical (%.2f %%), %d |dp| > 0.5 (%.2f %%)",
                ARM.key, block["n_identical"], block["n_compared"],
                100 * block["identical_share"], block["n_abs_delta_gt_0.5"],
                100 * block["share_abs_delta_gt_0.5"])
    for f in block["flips"]:
        logger.info("  flips at %.2f: %4d (%.2f %%) Wilson95 [%.2f %%, %.2f %%]",
                    f["threshold"], f["n_flips"], 100 * f["flip_share"],
                    100 * f["flip_share_wilson95"][0],
                    100 * f["flip_share_wilson95"][1])
    logger.info("  vocabulary: original %d distinct, replicate %d distinct; "
                "chance identical %.2f %%, kappa %.4f",
                block["vocabulary_original"]["n_distinct"],
                block["vocabulary_replicate"]["n_distinct"],
                100 * block["chance_identical_share"], block["identical_kappa"])
    logger.info("%s (reference): %.2f %% identical (chance %.2f %%, kappa %.4f), "
                "vocabulary %d / %d distinct",
                OTHER.key, 100 * other["identical_share"],
                100 * other["chance_identical_share"], other["identical_kappa"],
                other["vocabulary_original"]["n_distinct"],
                other["vocabulary_replicate"]["n_distinct"])
    logger.info("wrote %s", dest.relative_to(PROJECT_ROOT))
    return 0


# ---------------------------------------------------------------------------
# Stage: materialise the replicate's carried cell and its own F1 oracle.
# ---------------------------------------------------------------------------


def replicate_frame():
    """The replicate's candidate frame: K = 5 union geometry, replicate probabilities.

    Mirrors ``gemini37_image_55map_r2.rung_frame`` exactly, with the replicate's
    verify directory in place of the original's.

    Returns:
        A GeoDataFrame in EPSG:32635 with ``vote_count``, ``mound_probability``,
        ``source_tile`` (scoring frame) and ``origin_source_tile``.
    """
    raw = load_manifest_probs(CROPS_K5, ARM.replicate)
    return assign_eval_frame_tiles(raw)


def stage_materialise(workers: int) -> int:
    """Sweep the replicate's achievable grid, then write its two cells.

    Args:
        workers: Sweep parallelism.

    Returns:
        A process exit status.
    """
    ref, bounds, tile_index = load_frames()
    frame = replicate_frame()
    logger.info("%s: %d candidates", REP_RUNG, len(frame))

    points = with_carried(achievable_points(frame, K), ARM.key, K)
    tasks = [(REP_RUNG, p, v) for p, v in points]
    logger.info("sweeping %d points (%d workers)", len(tasks), workers)
    with Pool(workers, initializer=_init,
              initargs=(ref, bounds, tile_index, {REP_RUNG: frame})) as pool:
        rows = pool.map(_score_point, tasks, chunksize=2)

    rows = [r for r in rows if r["micro_f1_50"] is not None]
    rows.sort(key=lambda r: (r["prob_t"], r["min_votes"]))
    REP_HOME.mkdir(parents=True, exist_ok=True)
    dest = REP_HOME / f"sweep_{REP_RUNG}.csv"
    with dest.open("w", newline="") as fh:
        w = csvmod.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    logger.info("wrote %s (%d points)", dest.relative_to(PROJECT_ROOT), len(rows))

    f1_best = max(rows, key=lambda r: r["micro_f1_50"])
    mcc_best = max(rows, key=lambda r: r["tile_mcc"])
    carried_prob, carried_votes = carried_point(ARM.key, K)
    carried = next(
        (r for r in rows
         if abs(r["prob_t"] - carried_prob) < 1e-9
         and r["min_votes"] == carried_votes),
        None,
    )

    cells: list[dict[str, Any]] = []
    wanted = {
        "carried": (carried_prob, carried_votes),
        "f1-oracle": (f1_best["prob_t"], f1_best["min_votes"]),
    }
    for basis, (prob_t, votes) in wanted.items():
        sub = materialise(frame, float(prob_t), int(votes))
        cell_label = f"{ARM.prefix}-{basis}-replicate"
        cdest = REP_HOME / "cells" / cell_label / "detections.geojson"
        cdest.parent.mkdir(parents=True, exist_ok=True)
        sub.to_crs("EPSG:4326").to_file(cdest, driver="GeoJSON")
        cells.append({
            "label": cell_label,
            "rung": REP_RUNG,
            "arm": ARM.key,
            "verifier_model": ARM_MODEL[ARM.key][0],
            "verifier_thinking": ARM_MODEL[ARM.key][1],
            "k": K,
            "basis": basis,
            "point": f"({float(prob_t):.2f}, k{int(votes)})",
            "n_detections": int(len(sub)),
            "det": str(cdest.relative_to(PROJECT_ROOT)),
        })
        logger.info("%-34s n=%5d -> %s", cell_label, len(sub),
                    cdest.relative_to(PROJECT_ROOT))

    sweeps = {
        "buffer_m": BUFFER_M,
        "reference": REFERENCE,
        "source_probabilities": str(ARM.replicate.relative_to(PROJECT_ROOT)),
        "rungs": {REP_RUNG: {
            "n_sweep_points": len(rows),
            "carried_point": [carried_prob, carried_votes],
            "carried": carried,
            "f1_oracle": f1_best,
            "mcc_oracle": mcc_best,
        }},
        "cells": cells,
    }
    (REP_HOME / "sweeps.json").write_text(json.dumps(sweeps, indent=2) + "\n")
    (REP_HOME / "cells_manifest.json").write_text(
        json.dumps({"buffer_m": BUFFER_M, "reference": REFERENCE,
                    "cells": cells}, indent=2) + "\n")
    logger.info("carried  F1 %.4f MCC %.4f at (%.2f, k%d), n=%d",
                carried["micro_f1_50"], carried["tile_mcc"],
                carried["prob_t"], carried["min_votes"], carried["n_detections"])
    logger.info("F1 oracle %.4f at (%.2f, k%d) | MCC oracle %.4f at (%.2f, k%d)",
                f1_best["micro_f1_50"], f1_best["prob_t"], f1_best["min_votes"],
                mcc_best["tile_mcc"], mcc_best["prob_t"], mcc_best["min_votes"])
    return 0


# ---------------------------------------------------------------------------
# Stage: score the replicate's cells on the r2 recipe.
# ---------------------------------------------------------------------------


def stage_score(workers: int, jobs: int) -> int:
    """Run ``evaluate_detections.py`` over the replicate's cells.

    Mirrors ``gemini37_image_55map_r2.stage_score``: the same engine command,
    the same git-cleanliness precheck, ``score.log`` per cell.

    Args:
        workers: Engine parallelism per cell.
        jobs: Cells scored concurrently.

    Returns:
        A process exit status.
    """
    import subprocess
    from concurrent.futures import ThreadPoolExecutor

    cells = json.loads((REP_HOME / "cells_manifest.json").read_text())["cells"]
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", *[c["det"] for c in cells]],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip()
    if dirty:
        logger.error("detections not committed — --require-clean-inputs would "
                     "refuse them. Commit these first:\n%s", dirty)
        return 4

    def run_one(cell: dict[str, Any]) -> tuple[str, int]:
        out_dir = str((REP_HOME / "cells" / cell["label"]).relative_to(PROJECT_ROOT))
        cmd = engine_command(cell["det"], out_dir, cell["label"], workers)
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                              text=True, check=False)
        (REP_HOME / "cells" / cell["label"] / "score.log").write_text(
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
# Stage: the four paired tile-swap permutation tests.
# ---------------------------------------------------------------------------


def tests_for_arm() -> tuple[tuple[str, str, str, str], ...]:
    """The four contrasts, labelled for this arm.

    Returns:
        ``(name, a_label, b_label, why)`` per test, in the arm 2 note's order.
    """
    p = ARM.prefix
    k3 = p.replace("-K5", "-K3")
    return (
        ("a", f"{p}-carried-replicate", f"{p}-carried",
         "drift-only: same union, same point, different invocation"),
        ("b", f"{p}-carried-replicate", f"{k3}-carried",
         "does the K3 -> K5 gain survive a fresh invocation?"),
        ("c", f"{p}-carried", f"{k3}-carried",
         "the original K3 -> K5 contrast, reproduced for the record"),
        ("d", f"{p}-f1-oracle-replicate", f"{p}-f1-oracle",
         "drift-only at each leg's own F1 oracle"),
    )


def cell_detections() -> dict[str, Path]:
    """Detections for every cell the four tests touch.

    The two ``-replicate`` cells are this driver's own; the three comparators
    are the campaign's committed cells.

    Returns:
        ``cell_label -> detections path``.
    """
    p = ARM.prefix
    k3 = p.replace("-K5", "-K3")
    return {
        f"{p}-carried-replicate":
            REP_HOME / f"cells/{p}-carried-replicate/detections.geojson",
        f"{p}-f1-oracle-replicate":
            REP_HOME / f"cells/{p}-f1-oracle-replicate/detections.geojson",
        f"{p}-carried": CAMPAIGN_HOME / f"cells/{p}-carried/detections.geojson",
        f"{k3}-carried": CAMPAIGN_HOME / f"cells/{k3}-carried/detections.geojson",
        f"{p}-f1-oracle": CAMPAIGN_HOME / f"cells/{p}-f1-oracle/detections.geojson",
    }


def stage_tests() -> int:
    """Run tests (a)-(d) on both metrics and write ``tests.json``."""
    ref, bounds, tile_index = load_frames()
    tests = tests_for_arm()
    cell_det = cell_detections()

    def vectors(label: str) -> dict[str, Any]:
        det = read_detections(cell_det[label])
        tp, fp, fn = per_tile_arrays(det, ref, bounds, tile_index)
        truth, pred, conf = tile_vectors(det, ref, bounds)
        return {"tp": tp, "fp": fp, "fn": fn, "truth": truth, "pred": pred,
                "confusion": conf, "n": int(len(det))}

    cache: dict[str, dict[str, Any]] = {}
    for label in {lbl for _, a, b, _ in tests for lbl in (a, b)}:
        cache[label] = vectors(label)
        logger.info("loaded %-34s n=%5d", label, cache[label]["n"])

    mcc_rows, f1_rows = [], []
    for name, a_label, b_label, why in tests:
        a, b = cache[a_label], cache[b_label]
        if not np.array_equal(a["truth"], b["truth"]):
            logger.error("truth vectors differ for %s vs %s — different frames",
                         a_label, b_label)
            return 3
        mcc_rows.append({
            "test": name, "a": a_label, "b": b_label, "contrast": why,
            **permutation_test_mcc(a["pred"], b["pred"], a["truth"],
                                   n_permutations=N_PERMS, seed=SEED)})
        f1_rows.append({
            "test": name, "a": a_label, "b": b_label, "contrast": why,
            **permutation_test_float(a["tp"], a["fp"], a["fn"],
                                     b["tp"], b["fp"], b["fn"],
                                     n_permutations=N_PERMS, seed=SEED)})

    # Where an arm's F1 oracle coincides with its carried point, the oracle
    # cell IS the carried cell, and test (d) becomes a second copy of test
    # (a). That is worth recording in the JSON rather than leaving a reader to
    # notice that two rows carry identical numbers, so duplicate CONTRASTS are
    # detected by comparing each test's two sides cell-for-cell against every
    # earlier test's.
    def same_cell(x: str, y: str) -> bool:
        """Do two labels materialise identical detections on the frame?"""
        return (cache[x]["n"] == cache[y]["n"]
                and np.array_equal(cache[x]["pred"], cache[y]["pred"])
                and np.array_equal(cache[x]["tp"], cache[y]["tp"])
                and np.array_equal(cache[x]["fp"], cache[y]["fp"])
                and np.array_equal(cache[x]["fn"], cache[y]["fn"]))

    degenerate = []
    for i, (name, a_label, b_label, _) in enumerate(tests):
        for prior, pa, pb, _ in tests[:i]:
            if same_cell(a_label, pa) and same_cell(b_label, pb):
                degenerate.append({
                    "test": name, "duplicates": prior,
                    "a": a_label, "b": b_label,
                    "note": (f"{a_label} and {pa} are the same cell, as are "
                             f"{b_label} and {pb}: this arm's F1 oracle "
                             "coincides with its carried point on both "
                             f"invocations, so test ({name}) is test "
                             f"({prior}) again and carries no extra "
                             "information."),
                })
                break

    out = {
        "purpose": (
            f"Does the {ARM.key} K = 3 -> K = 5 micro-F1 gain survive an "
            "independent re-invocation of the same verifier, and what is that "
            "verifier's drift-only contrast? Declaration rule: "
            "reports/image-2x2-tests-declaration-2026-09-19.md section 5 "
            "caveat 1."),
        "arm": ARM.key,
        "verifier_model": ARM_MODEL[ARM.key][0],
        "verifier_thinking": ARM_MODEL[ARM.key][1],
        "buffer_m": BUFFER_M,
        "reference": REFERENCE,
        "n_permutations": N_PERMS,
        "seed": SEED,
        "cells": {k: str(v.relative_to(PROJECT_ROOT)) for k, v in cell_det.items()},
        "n_detections": {k: v["n"] for k, v in cache.items()},
        "tile_confusion": {k: v["confusion"] for k, v in cache.items()},
        "degenerate_contrasts": degenerate,
        "multiplicity": (
            "No Benjamini-Hochberg adjustment: these four tests are a "
            "replication probe of one already-declared contrast, not a new "
            "declared family. Raw p-values are reported."),
        "f1_tests": f1_rows,
        "mcc_tests": mcc_rows,
    }
    REP_HOME.mkdir(parents=True, exist_ok=True)
    dest = REP_HOME / "tests.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    for r in f1_rows:
        logger.info("F1  (%s) %-34s vs %-34s %.4f vs %.4f d=%+.4f p=%.4f",
                    r["test"], r["a"], r["b"], r["f1_a"], r["f1_b"],
                    r["observed_diff"], r["p_value"])
    for r in mcc_rows:
        logger.info("MCC (%s) %-34s vs %-34s %.4f vs %.4f d=%+.4f p=%.4f",
                    r["test"], r["a"], r["b"], r["mcc_a"], r["mcc_b"],
                    r["observed_diff"], r["p_value"])
    for d in degenerate:
        logger.warning("test (%s) duplicates test (%s): same cells on both "
                       "sides, so its row carries no extra information",
                       d["test"], d["duplicates"])
    logger.info("wrote %s", dest.relative_to(PROJECT_ROOT))
    return 0


def main() -> int:
    """Parse arguments and dispatch to a stage."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arm", default="arm1", choices=tuple(ARMS),
                    help="which verifier arm's replicate to score")
    ap.add_argument("--stage", required=True,
                    choices=("agree", "materialise", "score", "tests"))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--jobs", type=int, default=2)
    args = ap.parse_args()
    select_arm(args.arm)
    logger.info("arm %s: %s / %s, carried (%.2f, k%d)", ARM.key,
                *ARM_MODEL[ARM.key], *carried_point(ARM.key, K))
    if args.stage == "agree":
        return stage_agree()
    if args.stage == "materialise":
        return stage_materialise(args.workers)
    if args.stage == "score":
        return stage_score(args.workers, args.jobs)
    return stage_tests()


if __name__ == "__main__":
    raise SystemExit(main())
