#!/usr/bin/env python3
"""
Score the 2026-09-20 batch replicate of the 3.7 image arm 2 K = 5 verifier leg.

Purpose
-------
The 3.7 image campaign's pure stack (arm 2 = 3.7 proposer + 3.7 verifier) gains
+0.0071 micro-F1 @ 50 m from K = 3 to K = 5 at the carried operating points.
That gain sits inside the E89 re-invocation drift band (3.5-5.3 % decision flips
between independent invocations of the same verifier,
``reports/image-2x2-tests-declaration-2026-09-19.md`` section 5 caveat 1), so the
image-2x2 declaration's rule refuses it without a replicate arm. This script
scores that replicate.

Everything here is *imported* from ``scripts/gemini37_image_55map_r2.py`` — the
frames, the materialiser, the per-tile machinery, the permutation tests, the
engine recipe — so the replicate lands on the same instrument as the cells it is
compared against. Nothing in ``scripts/`` is modified (another agent owns that
file).

Stages
------
``agree``        Probability-level agreement between the two invocations.
``materialise``  The replicate's carried cell and its own F1 oracle, plus the
                 full achievable-point sweep CSV.
``tests``        The four paired tile-swap permutation tests (a)-(d).

Usage::

    cd ~/Code/map-reader-llm
    .venv/bin/python ~/scratch-replicate/replicate_k5_arm2.py --stage agree
    .venv/bin/python ~/scratch-replicate/replicate_k5_arm2.py --stage materialise --workers 12
    # commit the detections, then:
    .venv/bin/python ~/scratch-replicate/replicate_k5_arm2.py --stage tests

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

#: The 3.7 image campaign's verifier root, the K = 5 crop manifest, and the two
#: invocations of the arm 2 verifier over it.
VROOT = (PROJECT_ROOT / "outputs/gemini37-image-55map-2026-09-13"
         / "verifier/g384_ov192_55map_g37img")
CROPS_K5 = VROOT / "crops_k5"
VERIFY_ORIGINAL = VROOT / "verify_k5_arm2"
VERIFY_REPLICATE = VROOT / "verify_k5_arm2_replicate-batch-2026-09-20"

#: Where the replicate's derived artefacts land. Its own home, so nothing in the
#: campaign's committed cells or manifests is touched.
REP_HOME = (PROJECT_ROOT / "results/gemini37-image-55map-2026-09-13"
            / "replicate-k5-arm2-batch-2026-09-20")
CAMPAIGN_HOME = PROJECT_ROOT / "results/gemini37-image-55map-2026-09-13"

#: The rung the replicate re-verifies, and its label in the sweep CSV.
ARM = "arm2"
K = 5
REP_RUNG = "IMG-ARM2-K5-replicate"

#: The decision threshold at which a flip is counted, i.e. the carried point's
#: probability threshold.
DECISION_T = 0.90


# ---------------------------------------------------------------------------
# Stage: probability-level agreement between the two invocations.
# ---------------------------------------------------------------------------


def _probs(vdir: Path) -> dict[str, float]:
    """``candidate_id -> mound_probability`` for one verifier invocation."""
    results = json.loads((vdir / "probabilities.json").read_text())["results"]
    return {k: float(v["mound_probability"]) for k, v in results.items()}


def stage_agree() -> int:
    """Identical-probability share, decision flips at 0.90, and |dp| > 0.5."""
    orig, rep = _probs(VERIFY_ORIGINAL), _probs(VERIFY_REPLICATE)
    keys = sorted(set(orig) & set(rep))
    if len(keys) != len(orig) or len(keys) != len(rep):
        logger.warning("key sets differ: original %d, replicate %d, shared %d",
                       len(orig), len(rep), len(keys))
    a = np.array([orig[k] for k in keys])
    b = np.array([rep[k] for k in keys])
    identical = int((a == b).sum())
    flips = int(((a >= DECISION_T) != (b >= DECISION_T)).sum())
    big = int((np.abs(a - b) > 0.5).sum())
    # Which way the flips go: a candidate the replicate keeps but the original
    # dropped is a gain, the reverse a loss.
    gained = int(((b >= DECISION_T) & (a < DECISION_T)).sum())
    lost = int(((a >= DECISION_T) & (b < DECISION_T)).sum())
    out = {
        "original": str(VERIFY_ORIGINAL.relative_to(PROJECT_ROOT)),
        "replicate": str(VERIFY_REPLICATE.relative_to(PROJECT_ROOT)),
        "n_candidates_original": len(orig),
        "n_candidates_replicate": len(rep),
        "n_compared": len(keys),
        "n_identical": identical,
        "identical_share": round(identical / len(keys), 6),
        "decision_threshold": DECISION_T,
        "n_flips": flips,
        "flip_share": round(flips / len(keys), 6),
        "n_flips_replicate_keeps_original_drops": gained,
        "n_flips_original_keeps_replicate_drops": lost,
        "n_abs_delta_gt_0.5": big,
        "n_kept_original": int((a >= DECISION_T).sum()),
        "n_kept_replicate": int((b >= DECISION_T).sum()),
        "mean_abs_delta": round(float(np.abs(a - b).mean()), 6),
        "median_abs_delta": round(float(np.median(np.abs(a - b))), 6),
    }
    REP_HOME.mkdir(parents=True, exist_ok=True)
    dest = REP_HOME / "agreement.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    logger.info("agreement: %d/%d identical (%.1f %%), %d flips at %.2f "
                "(%.2f %%), %d |dp| > 0.5",
                identical, len(keys), 100 * identical / len(keys),
                flips, DECISION_T, 100 * flips / len(keys), big)
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
    raw = load_manifest_probs(CROPS_K5, VERIFY_REPLICATE)
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

    points = with_carried(achievable_points(frame, K), ARM, K)
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
    carried_prob, carried_votes = carried_point(ARM, K)
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
        cell_label = f"IMG-ARM2-K5-{basis}-replicate"
        cdest = REP_HOME / "cells" / cell_label / "detections.geojson"
        cdest.parent.mkdir(parents=True, exist_ok=True)
        sub.to_crs("EPSG:4326").to_file(cdest, driver="GeoJSON")
        cells.append({
            "label": cell_label,
            "rung": REP_RUNG,
            "arm": ARM,
            "verifier_model": ARM_MODEL[ARM][0],
            "verifier_thinking": ARM_MODEL[ARM][1],
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
        "source_probabilities": str(VERIFY_REPLICATE.relative_to(PROJECT_ROOT)),
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

#: The tests the replicate arm exists to run. ``(name, a_label, b_label, why)``.
TESTS = (
    ("a", "IMG-ARM2-K5-carried-replicate", "IMG-ARM2-K5-carried",
     "drift-only: same union, same point, different invocation"),
    ("b", "IMG-ARM2-K5-carried-replicate", "IMG-ARM2-K3-carried",
     "does the K3 -> K5 gain survive a fresh invocation?"),
    ("c", "IMG-ARM2-K5-carried", "IMG-ARM2-K3-carried",
     "the original K3 -> K5 contrast, reproduced for the record"),
    ("d", "IMG-ARM2-K5-f1-oracle-replicate", "IMG-ARM2-K5-f1-oracle",
     "drift-only at each leg's own F1 oracle"),
)

#: Detections for every cell the four tests touch.
CELL_DET = {
    "IMG-ARM2-K5-carried-replicate":
        REP_HOME / "cells/IMG-ARM2-K5-carried-replicate/detections.geojson",
    "IMG-ARM2-K5-f1-oracle-replicate":
        REP_HOME / "cells/IMG-ARM2-K5-f1-oracle-replicate/detections.geojson",
    "IMG-ARM2-K5-carried":
        CAMPAIGN_HOME / "cells/IMG-ARM2-K5-carried/detections.geojson",
    "IMG-ARM2-K3-carried":
        CAMPAIGN_HOME / "cells/IMG-ARM2-K3-carried/detections.geojson",
    "IMG-ARM2-K5-f1-oracle":
        CAMPAIGN_HOME / "cells/IMG-ARM2-K5-f1-oracle/detections.geojson",
}


def stage_tests() -> int:
    """Run tests (a)-(d) on both metrics and write ``tests.json``."""
    ref, bounds, tile_index = load_frames()

    def vectors(label: str) -> dict[str, Any]:
        det = read_detections(CELL_DET[label])
        tp, fp, fn = per_tile_arrays(det, ref, bounds, tile_index)
        truth, pred, conf = tile_vectors(det, ref, bounds)
        return {"tp": tp, "fp": fp, "fn": fn, "truth": truth, "pred": pred,
                "confusion": conf, "n": int(len(det))}

    cache: dict[str, dict[str, Any]] = {}
    for label in {lbl for _, a, b, _ in TESTS for lbl in (a, b)}:
        cache[label] = vectors(label)
        logger.info("loaded %-34s n=%5d", label, cache[label]["n"])

    mcc_rows, f1_rows = [], []
    for name, a_label, b_label, why in TESTS:
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

    out = {
        "purpose": (
            "Does the arm 2 K = 3 -> K = 5 micro-F1 gain survive an "
            "independent re-invocation of the same verifier? Declaration "
            "rule: reports/image-2x2-tests-declaration-2026-09-19.md "
            "section 5 caveat 1."),
        "buffer_m": BUFFER_M,
        "reference": REFERENCE,
        "n_permutations": N_PERMS,
        "seed": SEED,
        "cells": {k: str(v.relative_to(PROJECT_ROOT)) for k, v in CELL_DET.items()},
        "n_detections": {k: v["n"] for k, v in cache.items()},
        "tile_confusion": {k: v["confusion"] for k, v in cache.items()},
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
    logger.info("wrote %s", dest.relative_to(PROJECT_ROOT))
    return 0


def main() -> int:
    """Parse arguments and dispatch to a stage."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True,
                    choices=("agree", "materialise", "score", "tests"))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--jobs", type=int, default=2)
    args = ap.parse_args()
    if args.stage == "agree":
        return stage_agree()
    if args.stage == "materialise":
        return stage_materialise(args.workers)
    if args.stage == "score":
        return stage_score(args.workers, args.jobs)
    return stage_tests()


if __name__ == "__main__":
    raise SystemExit(main())
