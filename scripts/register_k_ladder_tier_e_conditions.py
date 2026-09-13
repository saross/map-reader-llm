#!/usr/bin/env python3
"""
Register the K-ladder tier E rungs as conditions
================================================

Description:
    The scoring step of tier E: turn each new rung's scored cell into a row of
    ``results/run-conditions.json``, so the generated manifests pick it up and
    the ladder's rungs are register-resolvable like every other cell. Modelled
    on ``scripts/register_k_ladder_phase2_conditions.py``, which registered the
    28 Phase 2 rungs; the differences are tier E's run
    (``grid-2026-08-18``), its pool slug (``brief-text``), and the union
    construction note warning 1 of the pre-launch audit records.

    One row per DISTINCT operating point per rung:

    * the sweep-optimal cell (``-opmax``), which ruling R2 tiers on;
    * the carried cell (prob_t 0.15, vote_t = K), where it is a different
      point. Where the sweep argmax lands on the carried point one row is
      registered and its ``_note`` says the transfer tax is zero by
      construction rather than by measurement.

    **What this script does NOT do**, deliberately:

    * it does not author or amend any analysis row, and touches no signature
      field (``manually_verified_at``, ``_signature_note``,
      ``gates.G1.pi_ruling``);
    * it does not add these cells to the Era-2 board. Admitting them is a
      re-tier and a re-signature, which is the PI's under "ladder, then board".

Usage::

    python scripts/register_k_ladder_tier_e_conditions.py --dry-run
    python scripts/register_k_ladder_tier_e_conditions.py --write
    python scripts/generate_post_run_report.py --all --write
    python scripts/verify_run_conditions.py --run grid-2026-08-18

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.register_k_ladder_phase2_conditions import (  # noqa: E402
    BOARD_SCOPE,
    RUN_CONDITIONS,
    VERIFIER_CONFIG,
)
from scripts.run_k_ladder_tier_e import (  # noqa: E402
    COMMITTED_K10,
    LEDGER_JSON,
    POINTS_JSON,
    RUN_ID,
    UNIONS_JSON,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

#: The run's output root, which register stage paths are relative to.
RUN_ROOT = "outputs/grid-2026-08-18"


def note_for(
    point: str,
    rung: dict[str, Any],
    union_row: dict[str, Any],
    spend: dict[str, Any],
) -> str:
    """Compose the row's provenance note.

    Args:
        point: ``"opmax"`` or ``"carried"``.
        rung: The rung's entry of ``tier-e/operating-points.json``.
        union_row: Its entry of ``tier-e/unions.json``.
        spend: Its entry of ``tier-e/spend-ledger.json``.

    Returns:
        The ``_note`` text.
    """
    flex = spend.get("flex_usd")
    flex_text = f"US${flex:.4f}" if flex is not None else "not recorded"
    shared = (
        f"K-LADDER TIER E (approved by the PI on the evening of 2026-09-12 at "
        f"US$5.02 for three rungs, hard stop US$7.00; controlling card "
        f"planning/k-ladder-review-2026-09-11.md, gate "
        f"results/k-ladder-2026-09-12/tier-e/pre_launch_audit.md). "
        f"First-N rung: the union is passes {union_row['pass_list']} of pool "
        f"{union_row['pool_dir']}, built at US$0 by "
        f"scripts/merge_passes.py --passes {union_row['pass_list']} --sweep "
        f"(union {union_row['measured_candidates']} candidates at vote >= 1, "
        f"reproducing the PI's approved figure of "
        f"{union_row['expected_candidates']} EXACTLY, delta "
        f"{union_row['delta']:+d}). "
        f"Verified by one pass of the carried Gemini 3 verifier (ruling R1: no "
        f"verifier swaps) at real-time flex tier, {flex_text} on the audited "
        f"flex basis (input x 0.25 + (output + thinking) x 1.50 per million). "
        f"NOTE the verify path stamps cost_basis 'list' with discount 1.0 even "
        f"under flex and records the tier nowhere, so the stage meta's "
        f"total_cost_usd is about twice the invoice "
        f"(reports/r7-gaps-deltas-2026-09-11.md § 2.3). "
        f"Scored on the board frame era2-b-487: curator reference, 14 buffers, "
        f"10,000 BCa draws, seed 42, MCC. "
        f"CONSTRUCTION CAVEAT, recorded because it makes this rung's candidate "
        f"universe wider than its K = 10 sibling's: the committed K = 10 rung "
        f"of this family ({COMMITTED_K10['union']}, "
        f"{COMMITTED_K10['candidates']} candidates) was built by "
        f"{COMMITTED_K10['builder']}, which filters the union to the grid "
        f"study's common 487-tile carrier footprint, while this rung is a "
        f"merge_passes union on the pool's native footprint (a merge_passes "
        f"K = 10 union holds {COMMITTED_K10['merge_passes_equivalent']}, of "
        f"which {COMMITTED_K10['merge_passes_on_carrier']} survive that "
        f"filter). Scoring on the board frame excludes the out-of-frame "
        f"candidates, so the F1 comparison across the ladder is like for like, "
        f"but the universe the verifier priced is not. Put to the PI in "
        f"reports/k-ladder-closeout-deltas-2026-09-12.md."
    )
    if point == "opmax":
        return (
            "IN-SAMPLE OPTIMUM (E56 class): the F1@20 argmax of this rung's "
            "own sweep, taken on the BOARD frame per ruling R2. The sweep was "
            "also run on the Era-2 frame full_evaluation_bounds.geojson and "
            "the two frames "
            f"{'agree' if rung.get('frames_agree') else 'DISAGREE'} on the "
            "argmax for this rung. Tie-break where needed: highest F1@20, then "
            "lowest vote_t, then lowest prob_t "
            f"({rung['opmax'].get('n_ties', 0)} point(s) tied here). " + shared
        )
    return (
        "CARRIED POINT (the transfer-tax column of ruling R2): prob_t "
        f"{rung['carried']['prob_t']}, k = K = {union_row['n_passes']}, fixed "
        "before this evaluation rather than selected on it. The probability is "
        "0.15 because that is the committed grid cells' threshold "
        "(g384-ov192-k10-verified-p0.15-k10), so the ladder stays a ladder. "
        + shared
    )


def rows_for_rung(
    rung: dict[str, Any],
    union_row: dict[str, Any],
    spend: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build the condition rows for one rung (one or two, never more)."""
    rows: list[dict[str, Any]] = []
    identical = bool(rung.get("carried_is_opmax"))

    for point in ("opmax", "carried"):
        if point == "carried" and identical:
            continue
        values = rung[point]
        note = note_for(point, rung, union_row, spend)
        if point == "opmax" and identical:
            note += (
                " THIS ROW IS ALSO THE CARRIED CELL: the sweep argmax lands "
                "exactly on the carried point (prob_t "
                f"{rung['carried']['prob_t']}, k = {rung['carried']['vote_t']}"
                "), so one cell serves both operating points and the transfer "
                "tax is 0.0000 by construction, not by measurement. No "
                "separate carried row is registered, because it would be the "
                "same detections file and the same evaluation."
            )
        rows.append(
            {
                "label": values["label"],
                "architecture": "proposer-verifier",
                "aggregation": "verified",
                "proposer_pool": union_row["pool_slug"],
                "n_passes": union_row["n_passes"],
                "vote_threshold": values["vote_t"],
                "prob_threshold": values["prob_t"],
                "verifier_config": dict(VERIFIER_CONFIG),
                "eval_path": (
                    f"results/k-ladder-2026-09-12/tier-e/cells/"
                    f"{values['cell']}/evaluation.json"
                ),
                "detections": values["detections"],
                "_note": note,
                "n_candidates": union_row["measured_candidates"],
                "scope_override": dict(BOARD_SCOPE),
            }
        )
    return rows


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Register the K-ladder tier E rungs as conditions"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--write", action="store_true",
        help="Write results/run-conditions.json (default: dry run)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Default; no-op")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    with open(POINTS_JSON) as handle:
        points = json.load(handle)["rungs"]
    with open(UNIONS_JSON) as handle:
        union_rows = {row["row"]: row for row in json.load(handle)["rungs"]}
    spend_by_row: dict[int, dict[str, Any]] = {}
    if LEDGER_JSON.exists():
        with open(LEDGER_JSON) as handle:
            spend_by_row = {
                entry["row"]: entry
                for entry in json.load(handle).get("rungs", {}).values()
            }

    with open(RUN_CONDITIONS) as handle:
        register = json.load(handle)
    run = register["decomposition"][RUN_ID]

    added = replaced = stages_added = 0
    for rung in points:
        union_row = union_rows[rung["row"]]
        spend = spend_by_row.get(rung["row"], {})

        stage_id = union_row["verifier_stage"]
        if stage_id not in run["verifier_passes"]:
            run["verifier_passes"][stage_id] = {
                "modality": "text",
                "path": str(
                    Path(union_row["verify_dir"]).relative_to(RUN_ROOT)
                ),
            }
            stages_added += 1

        for row in rows_for_rung(rung, union_row, spend):
            existing = next(
                (
                    index
                    for index, candidate in enumerate(run["conditions"])
                    if candidate.get("label") == row["label"]
                ),
                None,
            )
            if existing is None:
                run["conditions"].append(row)
                added += 1
                logger.info(
                    "+ %s::%s  (k>=%s, p>=%s) n_cand=%s",
                    RUN_ID, row["label"], row["vote_threshold"],
                    row["prob_threshold"], row["n_candidates"],
                )
            else:
                run["conditions"][existing] = row
                replaced += 1
                logger.info("~ %s::%s  (refreshed)", RUN_ID, row["label"])

    logger.info(
        "%d row(s) to add, %d to refresh, %d verifier stage(s) to add",
        added, replaced, stages_added,
    )
    if not args.write:
        logger.info("dry run — nothing written. Pass --write to commit.")
        return

    with open(RUN_CONDITIONS, "w") as handle:
        json.dump(register, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    logger.info("wrote %s", RUN_CONDITIONS.relative_to(BASE_DIR))
    logger.info(
        "next: python scripts/generate_post_run_report.py --all --write, then "
        "python scripts/verify_run_conditions.py --run %s", RUN_ID,
    )


if __name__ == "__main__":
    main()
