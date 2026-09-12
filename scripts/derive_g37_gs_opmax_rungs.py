#!/usr/bin/env python3
"""
Derive the sweep-optimal point for the committed 3.7 GS screen K=5/K=10 rungs
============================================================================

Description:
    Tier D of the K-ladder Phase 2 gap-fill buys the K = 1 and K = 3 rungs of
    the Gemini 3.7 proposer screened on the gold standard, so that a second
    model family carries a four-rung fixed-parameter ladder. Its committed
    K = 5 and K = 10 rungs, however, are registered at their **carried** point
    only — ``g37-text-k5-verified-carried-p0.10-k5`` and its K = 10 sibling —
    so the family's ``-opmax`` column would stop at K = 3 while the pv-diag-384
    families carry it at all four rungs.

    Those two stages' crops manifests, probabilities and unions are all
    committed, so the sweep-optimal point is reachable at **US$0**. This script
    sweeps each on both 487-tile gold-standard frames, takes the F1@20 argmax on
    the board frame (ruling R2), materialises it, and emits the board-frame
    evaluation job. No API call is made; no register row is written.

    Ruling R1 holds without a swap: both committed stages were verified by the
    carried Gemini 3 verifier, not by a 3.7 one (the ``verify_swap37`` and
    ``verify_swap38`` stages beside them are the swaps, and are excluded).

Usage::

    python scripts/derive_g37_gs_opmax_rungs.py prepare
    xargs -P 4 -I CMD bash -c CMD < \
        results/k-ladder-2026-09-12/phase2/g37-opmax-jobs.txt
    python scripts/derive_g37_gs_opmax_rungs.py collect

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.score_k_ladder_phase2_rungs import (  # noqa: E402
    BOARD_BOUNDS,
    BOOTSTRAP,
    BUFFERS,
    ERA2_BOUNDS,
    GROUND_TRUTH,
    HEADLINE_BUFFER,
    PHASE2_DIR,
    SEED,
    SWEEP_BUFFERS,
    argmax_at_headline,
    cell_dir_name,
    eval_command,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

RUN_ID = "gemini37-screen-2026-08-28"
VERIFIER_ROOT = (
    "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37"
)

#: This family's unions declare their CRS explicitly as CRS84 and carry
#: degrees, unlike the pv-diag-384 consensus files which declare nothing and
#: are read as WGS84 by default. ``materialise_pv_geojson.py`` refuses a
#: mismatch between a declared CRS and ``--crs``, so the declaration is passed
#: through verbatim — which also reproduces the CRS the family's committed
#: detections carry (``results/gemini37-screen-2026-08-28/
#: verified_best_20m.geojson``).
UNION_CRS = "urn:ogc:def:crs:OGC:1.3:CRS84"

#: Cross-check: the committed carried cell of the K = 5 stage holds this many
#: features at (vote_t 5, prob_t 0.10). Re-applying the same filter here must
#: reproduce it, or the join has moved and the derivation is not trustworthy.
CARRIED_CROSSCHECK = {
    5: {"vote_t": 5, "prob_t": 0.10, "n_detections": 443,
        "source": "results/gemini37-screen-2026-08-28/verified_best_20m.geojson"},
}

OUT_DIR = PHASE2_DIR / "g37-opmax"
JOBS_FILE = PHASE2_DIR / "g37-opmax-jobs.txt"
POINTS_JSON = OUT_DIR / "operating-points.json"
SCORES_JSON = OUT_DIR / "scores.json"

#: The two committed stages, each verified by the carried Gemini 3 verifier.
#: ``union`` is the file the stage's crops manifest names as its
#: ``source_geojson``; ``carried`` is the point the register already holds.
STAGES: list[dict[str, Any]] = [
    {
        "k": 5,
        "verify_dir": f"{VERIFIER_ROOT}/verify",
        "crops_dir": f"{VERIFIER_ROOT}/crops",
        "union": f"{VERIFIER_ROOT}/union_k5.geojson",
        "stage_id": "g384_ov192_g37-union-k5-verify",
        "carried_condition_id": (
            "gemini37-screen-2026-08-28::"
            "g37-text-k5-verified-carried-p0.10-k5-era2b"
        ),
    },
    {
        "k": 10,
        "verify_dir": f"{VERIFIER_ROOT}/verify_k10",
        "crops_dir": f"{VERIFIER_ROOT}/crops_k10",
        "union": f"{VERIFIER_ROOT}/union_k10.geojson",
        "stage_id": "g384_ov192_g37-union-k10-verify",
        "carried_condition_id": (
            "gemini37-screen-2026-08-28::"
            "g37-text-k10-verified-carried-p0.10-k10-era2b"
        ),
    },
]


def sweep(stage: dict[str, Any], *, bounds: str, out_name: str) -> Path:
    """Sweep one committed stage on one frame."""
    output = BASE_DIR / stage["verify_dir"] / out_name
    command = [
        sys.executable,
        "scripts/sweep_f1_greedy_pv.py",
        "--config",
        f"g37-text-k{stage['k']}",
        "--crops-dir",
        stage["crops_dir"],
        "--verified-dir",
        stage["verify_dir"],
        "--output",
        str(output.relative_to(BASE_DIR)),
        "--bounds",
        bounds,
        "--buffer-m",
        *[str(buffer) for buffer in SWEEP_BUFFERS],
    ]
    completed = subprocess.run(
        command, cwd=BASE_DIR, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        logger.error(
            "sweep failed for K=%d on %s:\n%s",
            stage["k"],
            bounds,
            completed.stderr[-2000:],
        )
        sys.exit(5)
    return output


def cmd_prepare(args: argparse.Namespace) -> None:
    """Sweep, pick the board-frame argmax, materialise, write the eval jobs."""
    entries: list[dict[str, Any]] = []
    jobs: list[str] = []

    for stage in STAGES:
        # Before trusting the join, reproduce a point whose feature count is
        # already committed (the feedback_feature_count_crosscheck rule).
        check = CARRIED_CROSSCHECK.get(stage["k"])
        if check:
            probe = OUT_DIR / "crosscheck" / f"k{stage['k']}-carried.geojson"
            got = materialise_named(
                stage["union"],
                f"{stage['verify_dir']}/probabilities.json",
                vote_t=check["vote_t"],
                prob_t=check["prob_t"],
                output=probe,
            )
            if got != check["n_detections"]:
                logger.error(
                    "K=%d cross-check FAILED: re-applying (%d, %.2f) to this "
                    "stage yields %d features, but %s holds %d. The index join "
                    "has moved; refusing to derive an operating point from it.",
                    stage["k"],
                    check["vote_t"],
                    check["prob_t"],
                    got,
                    check["source"],
                    check["n_detections"],
                )
                sys.exit(8)
            logger.info(
                "K=%d cross-check OK: (%d, %.2f) reproduces %d features",
                stage["k"],
                check["vote_t"],
                check["prob_t"],
                got,
            )

        board = argmax_at_headline(
            sweep(stage, bounds=BOARD_BOUNDS, out_name="sweep_2d_era2b.json")
        )
        era2 = argmax_at_headline(
            sweep(stage, bounds=ERA2_BOUNDS, out_name="sweep_2d.json")
        )
        agree = (board["vote_t"], board["prob_t"]) == (
            era2["vote_t"],
            era2["prob_t"],
        )
        label = f"g37-text-k{stage['k']}-verified-opmax"
        detections = OUT_DIR / "materialised" / f"{label}.geojson"
        count = materialise_named(
            stage["union"],
            f"{stage['verify_dir']}/probabilities.json",
            vote_t=board["vote_t"],
            prob_t=board["prob_t"],
            output=detections,
        )
        cell = cell_dir_name(RUN_ID, label)
        jobs.append(
            eval_command(detections, cell, label).replace(
                "results/k-ladder-2026-09-12/phase2/cells/",
                "results/k-ladder-2026-09-12/phase2/g37-opmax/cells/",
            )
        )
        entries.append(
            {
                "k": stage["k"],
                "label": label,
                "run_id": RUN_ID,
                "stage_id": stage["stage_id"],
                "union": stage["union"],
                "probabilities": f"{stage['verify_dir']}/probabilities.json",
                "opmax": {
                    "vote_t": board["vote_t"],
                    "prob_t": board["prob_t"],
                    "sweep_f1_20": board["f1"],
                    "sweep_n": board["n"],
                    "n_ties_at_argmax": board["n_ties"],
                },
                "opmax_on_era2_frame": {
                    "vote_t": era2["vote_t"],
                    "prob_t": era2["prob_t"],
                    "sweep_f1_20": era2["f1"],
                },
                "frames_agree_on_argmax": agree,
                "n_detections": count,
                "detections": str(detections.relative_to(BASE_DIR)),
                "cell": cell,
                "eval_path": (
                    "results/k-ladder-2026-09-12/phase2/g37-opmax/cells/"
                    f"{cell}/evaluation.json"
                ),
                "carried_condition_id": stage["carried_condition_id"],
            }
        )
        logger.info(
            "K=%2d  opmax (%d, %.2f) sweep F1 %.4f n=%d  frames agree: %s",
            stage["k"],
            board["vote_t"],
            board["prob_t"],
            board["f1"],
            count,
            agree,
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(POINTS_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "script": "scripts/derive_g37_gs_opmax_rungs.py",
                "script_version": __version__,
                "api_calls": 0,
                "registered": False,
                "stages": entries,
            },
            handle,
            indent=2,
        )
        handle.write("\n")
    with open(JOBS_FILE, "w") as handle:
        handle.write("\n".join(jobs) + "\n")
    logger.info("%d eval job(s) -> %s", len(jobs), JOBS_FILE.relative_to(BASE_DIR))


def materialise_named(
    union: str, probabilities: str, *, vote_t: int, prob_t: float, output: Path
) -> int:
    """Materialise one operating point from an explicitly named union.

    :func:`scripts.score_k_ladder_phase2_rungs.materialise` assumes the
    ``consensus-n<N>/consensus_t1.geojson`` layout; the 3.7 screen names its
    unions ``union_k5.geojson`` / ``union_k10.geojson``, so the paths are passed
    through directly here.

    Returns:
        The feature count of the written GeoJSON.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "scripts/materialise_pv_geojson.py",
        "--consensus",
        union,
        "--probabilities",
        probabilities,
        "--vote-t",
        str(vote_t),
        "--prob-t",
        str(prob_t),
        "--output",
        str(output.relative_to(BASE_DIR)),
        "--crs",
        UNION_CRS,
    ]
    completed = subprocess.run(
        command, cwd=BASE_DIR, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        logger.error("materialise failed:\n%s", completed.stderr[-2000:])
        sys.exit(6)
    with open(output) as handle:
        return len(json.load(handle).get("features", []))


def cmd_collect(args: argparse.Namespace) -> None:
    """Read the two derived opmax evaluations into a scores JSON."""
    with open(POINTS_JSON) as handle:
        points = json.load(handle)
    missing: list[str] = []
    for stage in points["stages"]:
        path = BASE_DIR / stage["eval_path"]
        if not path.exists():
            missing.append(stage["eval_path"])
            continue
        with open(path) as handle:
            evaluation = json.load(handle)
        summary = evaluation["summary"]
        headline = next(
            entry
            for entry in summary["buffers"]
            if int(entry["buffer_metres"]) == HEADLINE_BUFFER
        )
        mcc = (summary.get("tile_classification") or {}).get("mcc") or {}
        stage["f1_20"] = headline.get("f1")
        stage["tile_mcc"] = mcc.get("point")
        logger.info(
            "K=%2d  F1@20 %.4f  tile-MCC %.4f",
            stage["k"],
            stage["f1_20"],
            stage["tile_mcc"],
        )
    with open(SCORES_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "recipe": {
                    "bounds": BOARD_BOUNDS,
                    "ground_truth": GROUND_TRUTH,
                    "buffers": BUFFERS,
                    "bootstrap": BOOTSTRAP,
                    "seed": SEED,
                    "mcc": True,
                },
                "n_missing_evaluations": len(missing),
                "missing_evaluations": missing,
                "stages": points["stages"],
            },
            handle,
            indent=2,
        )
        handle.write("\n")
    logger.info("-> %s", SCORES_JSON.relative_to(BASE_DIR))


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Derive the sweep-optimal point for the committed 3.7 GS screen "
            "K = 5 / K = 10 rungs (US$0, no API calls, not registered)"
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.set_defaults(func=cmd_prepare)
    collect = subparsers.add_parser("collect")
    collect.set_defaults(func=cmd_collect)
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    args.func(args)


if __name__ == "__main__":
    main()
