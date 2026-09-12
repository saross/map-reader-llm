#!/usr/bin/env python3
"""
Derive the carried operating point for the committed K = 5 / K = 10 rungs
========================================================================

Description:
    Ruling R2 asks every ladder rung to be reported at two operating points:
    the sweep-optimal (``-opmax``) and the **carried** point, the latter as the
    transfer-tax column. Phase 2's 28 new rungs get both. The committed
    K = 5 and K = 10 rungs of the same 13 ``pv-diag-384`` pools, however, are
    registered at their ``-opmax`` point ONLY — no carried cell exists for
    them — so without this step R2's carried column would be a two-rung stub
    rather than a ladder.

    Their unions and ``probabilities.json`` are committed, so the carried point
    is reachable at **US$0**: re-materialise at (prob_t, vote_t) and re-score.
    No API call is made and no register row is written — these are reported
    cells, not registered ones, and the deltas report says so.

    **The carried convention, and its ambiguity, stated rather than buried.**
    The corpus holds two readings of "the carried point":

    * ``k = K`` (unanimity) — the 3.7 GS screen's committed rungs
      (``g37-text-k5-verified-carried-p0.10-k5``, ``…-k10-…-k10``) and the
      55-map carried rows.
    * ``k = 1 / 3 / 4 / 8`` at K = 1 / 3 / 5 / 10 — the gold-standard stride
      ladder (`results/k-ladder-2026-09-12/inventory.md` § 2).

    Ruling R2's text says "prob 0.15, k = K", so this script uses ``k = K``.
    The two readings coincide at K = 1 and K = 3 — every new Phase 2 rung — and
    diverge only at K = 5 and K = 10, which is exactly the range this script
    covers. At K = 10 ``k = K`` is unanimity across ten passes, a severe
    threshold, so a large transfer tax there is a property of the convention
    and not of the pipeline. The deltas report repeats that caveat beside the
    numbers.

Usage::

    python scripts/derive_k_ladder_committed_carried.py prepare
    xargs -P 8 -I CMD bash -c CMD < \
        results/k-ladder-2026-09-12/phase2/committed-carried-jobs.txt
    python scripts/derive_k_ladder_committed_carried.py collect

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

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.score_k_ladder_phase2_rungs import (  # noqa: E402
    BOARD_BOUNDS,
    BUFFERS,
    BOOTSTRAP,
    GROUND_TRUTH,
    HEADLINE_BUFFER,
    PHASE2_DIR,
    SEED,
    cell_dir_name,
    eval_command,
    materialise,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

MEMBERSHIP = (
    BASE_DIR
    / "results"
    / "leaderboard"
    / "era2"
    / "gs-era2-verified-board-2026-09-10"
    / "opmax"
    / "membership.json"
)

OUT_DIR = PHASE2_DIR / "committed-carried"
JOBS_FILE = PHASE2_DIR / "committed-carried-jobs.txt"
POINTS_JSON = OUT_DIR / "operating-points.json"
SCORES_JSON = OUT_DIR / "scores.json"

#: The 13 pv-diag-384 pools whose K = 1 and K = 3 rungs Phase 2 added.
TARGET_POOLS = {
    "flash-minimal-text-n30-t07-text-t0.3",
    "flash-minimal-text-n30-t07-text-t0.7",
    "flash-minimal-text-n30-t07-text-t1.0",
    "flash-high-text-n5-text-t0.3",
    "flash-high-text-n5-text-t0.7",
    "flash-high-text-n5-text-t1.0",
    "image-n5-image-t0.3",
    "image-n5-image-t0.7",
    "image-n5-image-t1.0",
    "flash-high-image-n5-image-t0.3",
    "flash-high-image-n5-image-t0.7",
    "flash-high-image-n5-image-t1.0",
    "scale-4-optimal-487",
}

CARRIED_PROB = 0.15

#: The two readings of "the carried vote threshold", both computed so the PI
#: can rule on which the ladder should report. They coincide at K = 1 and
#: K = 3 — every new Phase 2 rung — and diverge at K = 5 and K = 10.
#:
#: ``k-equals-K``   R2's literal text ("prob 0.15, k = K"): unanimity.
#: ``stride-shell`` the gold-standard stride ladder's own values, 1 / 3 / 4 / 8
#:                  at K = 1 / 3 / 5 / 10 (`inventory.md` § 2, the four
#:                  `stride-phaseb-2026-08-25` rungs' `k` column).
CARRIED_VOTE_READINGS: dict[str, dict[int, int]] = {
    "k-equals-K": {1: 1, 3: 3, 5: 5, 10: 10},
    "stride-shell": {1: 1, 3: 3, 5: 4, 10: 8},
}


def members() -> list[dict[str, Any]]:
    """Return the committed K = 5 / K = 10 board members of the target pools."""
    with open(MEMBERSHIP) as handle:
        data = json.load(handle)
    # R1 fixes the verifier: only the carried Gemini 3 adversarial v1 verifier
    # counts as a rung of this ladder. Several Session-78 cells share these
    # pools at K = 5 but swap the verifier instruction (comparative, checklist,
    # brief), so they are excluded here explicitly rather than by accident.
    kept = [
        member
        for member in data["members"]
        if member.get("proposer_pool") in TARGET_POOLS
        and member.get("k") in (5, 10)
        and (member.get("verifier_config") or {}).get("variant") == "v1"
        and (member.get("verifier_config") or {}).get("instruction_file")
        == "verify_adversarial.md"
    ]
    kept.sort(key=lambda member: (member["proposer_pool"], member["k"]))
    return kept


def cmd_prepare(args: argparse.Namespace) -> None:
    """Materialise each committed rung's carried point and write eval jobs."""
    entries: list[dict[str, Any]] = []
    jobs: list[str] = []

    for member in members():
        vintage = member.get("vintage") or {}
        union = vintage.get("union")
        probabilities = vintage.get("probabilities") or member.get(
            "probabilities_path"
        )
        if not union or not probabilities:
            logger.error(
                "%s: no union/probabilities recorded in membership — skipping",
                member["label"],
            )
            continue
        if vintage.get("verdict") not in (None, "same-vintage"):
            logger.warning(
                "%s: vintage verdict is %r, not same-vintage — the carried "
                "point is still derived, and the verdict is recorded",
                member["label"],
                vintage.get("verdict"),
            )

        k = int(member["k"])
        # materialise() takes a rung-shaped dict; build the minimum it reads.
        shim = {
            "row": -1,
            "consensus_dir": str(Path(union).parent),
            "paths": {"verify_dir": str(Path(probabilities).parent)},
        }
        entry: dict[str, Any] = {
            "label": member["label"],
            "run_id": member["run_id"],
            "proposer_pool": member["proposer_pool"],
            "stage_id": member["stage_id"],
            "k": k,
            "carried_prob_t": CARRIED_PROB,
            "opmax_vote_t": member["vote_threshold"],
            "opmax_prob_t": member["prob_threshold"],
            "opmax_condition_id": member["condition_id"],
            "opmax_eval_path": (
                "results/leaderboard/era2/"
                "gs-era2-verified-board-2026-09-10/cells/"
                f"{cell_dir_name(member['run_id'], member['label'] + '-opmax')}"
                "/evaluation.json"
            ),
            "union": union,
            "probabilities": probabilities,
            "vintage_verdict": vintage.get("verdict"),
            "readings": {},
        }

        seen_vote: dict[int, str] = {}
        for reading, vote_by_k in CARRIED_VOTE_READINGS.items():
            vote_t = vote_by_k[k]
            if vote_t in seen_vote:
                entry["readings"][reading] = {
                    **entry["readings"][seen_vote[vote_t]],
                    "_note": (
                        f"identical to the {seen_vote[vote_t]} reading at "
                        f"K = {k} (both give vote_t {vote_t}); one cell"
                    ),
                }
                continue
            seen_vote[vote_t] = reading
            label = (
                f"{member['label']}-carried-p{CARRIED_PROB:.2f}-k{vote_t}"
            )
            detections = OUT_DIR / "materialised" / f"{label}.geojson"
            count = materialise(
                shim, vote_t=vote_t, prob_t=CARRIED_PROB, output=detections
            )
            cell = cell_dir_name(member["run_id"], label)
            jobs.append(
                eval_command(detections, cell, label).replace(
                    "results/k-ladder-2026-09-12/phase2/cells/",
                    "results/k-ladder-2026-09-12/phase2/committed-carried/"
                    "cells/",
                )
            )
            entry["readings"][reading] = {
                "carried_label": label,
                "vote_t": vote_t,
                "prob_t": CARRIED_PROB,
                "n_detections": count,
                "detections": str(detections.relative_to(BASE_DIR)),
                "cell": cell,
                "eval_path": (
                    "results/k-ladder-2026-09-12/phase2/committed-carried/"
                    f"cells/{cell}/evaluation.json"
                ),
            }

        entries.append(entry)
        logger.info(
            "%-28s K=%2d  k=K (%2d) n=%4d | stride-shell (%2d) n=%4d | "
            "opmax (%s, %s)",
            member["label"],
            k,
            entry["readings"]["k-equals-K"]["vote_t"],
            entry["readings"]["k-equals-K"]["n_detections"],
            entry["readings"]["stride-shell"]["vote_t"],
            entry["readings"]["stride-shell"]["n_detections"],
            member["vote_threshold"],
            member["prob_threshold"],
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(POINTS_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "script": "scripts/derive_k_ladder_committed_carried.py",
                "script_version": __version__,
                "carried_convention": (
                    "prob_t 0.15, vote_t = K (R2's literal reading; the GS "
                    "stride ladder's alternative reading is k = 1/3/4/8 at "
                    "K = 1/3/5/10, which coincides at K = 1 and K = 3)"
                ),
                "api_calls": 0,
                "registered": False,
                "n_cells": len(entries),
                "cells": entries,
            },
            handle,
            indent=2,
        )
        handle.write("\n")
    with open(JOBS_FILE, "w") as handle:
        handle.write("\n".join(jobs) + "\n")
    logger.info(
        "%d carried cell(s) materialised; %d eval job(s) -> %s",
        len(entries),
        len(jobs),
        JOBS_FILE.relative_to(BASE_DIR),
    )


def cmd_collect(args: argparse.Namespace) -> None:
    """Read the derived carried cells' evaluations into one scores JSON."""
    with open(POINTS_JSON) as handle:
        points = json.load(handle)

    def read_metrics(path: str) -> dict[str, Any] | None:
        """Read F1@20 and tile-MCC from one evaluation, or ``None``."""
        full = BASE_DIR / path
        if not full.exists():
            missing.append(path)
            return None
        with open(full) as handle:
            evaluation = json.load(handle)
        summary = evaluation["summary"]
        headline = next(
            entry
            for entry in summary["buffers"]
            if int(entry["buffer_metres"]) == HEADLINE_BUFFER
        )
        mcc = (summary.get("tile_classification") or {}).get("mcc") or {}
        return {"f1_20": headline.get("f1"), "tile_mcc": mcc.get("point")}

    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for cell in points["cells"]:
        record = dict(cell)
        opmax = read_metrics(cell["opmax_eval_path"])
        if opmax:
            record["opmax_f1_20"] = opmax["f1_20"]
            record["opmax_tile_mcc"] = opmax["tile_mcc"]
        record["readings"] = {
            reading: dict(values) for reading, values in cell["readings"].items()
        }
        for reading, values in record["readings"].items():
            metrics = read_metrics(values["eval_path"])
            if not metrics:
                continue
            values["f1_20"] = metrics["f1_20"]
            values["tile_mcc"] = metrics["tile_mcc"]
            if opmax:
                values["transfer_tax_f1_20"] = round(
                    metrics["f1_20"] - opmax["f1_20"], 4
                )
                values["transfer_tax_tile_mcc"] = round(
                    metrics["tile_mcc"] - opmax["tile_mcc"], 4
                )
        rows.append(record)

    with open(SCORES_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "script": "scripts/derive_k_ladder_committed_carried.py",
                "script_version": __version__,
                "recipe": {
                    "bounds": BOARD_BOUNDS,
                    "ground_truth": GROUND_TRUTH,
                    "buffers": BUFFERS,
                    "bootstrap": BOOTSTRAP,
                    "seed": SEED,
                    "mcc": True,
                },
                "n_cells": len(rows),
                "n_missing_evaluations": len(missing),
                "missing_evaluations": missing,
                "cells": rows,
            },
            handle,
            indent=2,
        )
        handle.write("\n")
    logger.info(
        "collected %d cell(s), %d evaluation(s) missing -> %s",
        len(rows),
        len(missing),
        SCORES_JSON.relative_to(BASE_DIR),
    )


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Derive the carried operating point for the committed K = 5 / "
            "K = 10 pv-diag-384 rungs (US$0, no API calls, not registered)"
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
