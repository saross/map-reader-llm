#!/usr/bin/env python3
"""
Register the K-ladder Phase 2 rungs as conditions
=================================================

Description:
    Step 4 of the K-ladder Phase 2 run: turn each new rung's scored cell into a
    row of ``results/run-conditions.json``, so the generated manifests pick it
    up and the ladder's rungs are register-resolvable like every other cell.

    One row per DISTINCT operating point per rung:

    * the sweep-optimal cell (``-opmax``), which ruling R2 tiers on;
    * the carried cell, where it is a different point. At K = 1 the vote axis
      is degenerate and the sweep argmax often lands on the carried
      probability, so the two points coincide; then one row is registered and
      its ``_note`` records that the transfer tax is zero by construction
      rather than by measurement.

    Each row carries ``scope_override`` for the board frame ``era2-b-487``,
    the verifier configuration R1 fixes, and a ``_note`` that names the E56
    class for the in-sample ``-opmax`` point, the union, the pass list, and the
    audited flex cost of the verifier pass that produced it.

    **What this script does NOT do**, deliberately:

    * it does not author or amend any analysis row, and touches no signature
      field (``manually_verified_at``, ``_signature_note``,
      ``gates.G1.pi_ruling``);
    * it does not add these cells to the Era-2 board — the board is
      ``re_sign_pending`` from Phase 1, and admitting 40-odd new cells to a
      board awaiting the PI's signature is a decision for the PI, not for this
      run;
    * it does not register the US$0 derived cells (the committed rungs' carried
      points, the 3.7 family's opmax points). Those are reported in the
      findings and the deltas report as derived comparisons, not registered as
      cells.

Usage::

    python scripts/register_k_ladder_phase2_conditions.py --dry-run
    python scripts/register_k_ladder_phase2_conditions.py --write
    python scripts/generate_post_run_report.py --all --write
    python scripts/verify_run_conditions.py --run pv-diag-384

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

from scripts.run_k_ladder_phase2_verifier import (  # noqa: E402
    LEDGER_JSON,
    resolve_paths,
)
from scripts.score_k_ladder_phase2_rungs import POINTS_JSON  # noqa: E402

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

RUN_CONDITIONS = BASE_DIR / "results" / "run-conditions.json"
UNIONS_JSON = (
    BASE_DIR / "results" / "k-ladder-2026-09-12" / "phase2" / "unions.json"
)

BOARD_SCOPE = {
    "test_set_id": "era2-b-487",
    "bounds_path": "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson",
    "n_test_tiles": 487,
    "calibration_set_id": None,
    "n_calibration_tiles": None,
}

VERIFIER_CONFIG = {
    "variant": "v1",
    "instruction_file": "verify_adversarial.md",
    "model": "gemini-3-flash-preview",
    "thinking_level": "minimal",
    "temperature": 0.0,
    "iterations": 1,
}

#: Each run's output root, which register stage paths are relative to.
RUN_ROOT = {
    "pv-diag-384": "outputs/h11/pv-diag-384",
    "gemini37-screen-2026-08-28": "outputs/gemini37-screen-2026-08-28",
}


def modality(pool_slug: str) -> str:
    """Infer the register's modality field from the pool slug."""
    return "image" if "image" in pool_slug else "text"


def note_for(
    point: str,
    rung: dict[str, Any],
    union_row: dict[str, Any],
    spend: dict[str, Any],
) -> str:
    """Compose the row's provenance note."""
    pass_ids = ", ".join(union_row["pass_ids"])
    flex = spend.get("flex_usd")
    flex_text = f"US${flex:.4f}" if flex is not None else "not recorded"
    shared = (
        f"K-LADDER PHASE 2 (approved by the PI 2026-09-12 at US$24.84 for 28 "
        f"rungs; controlling card planning/k-ladder-review-2026-09-11.md, "
        f"costing reports/k-ladder-phase2-costing-2026-09-12.md row "
        f"{union_row['row']}, tier {union_row['tier']}). "
        f"First-N rung: the union is passes {pass_ids} of pool "
        f"{union_row['pool_dir']}, built at US$0 by "
        f"scripts/merge_passes.py --passes {union_row['pass_list']} --sweep "
        f"(union {union_row['measured_candidates']} candidates at vote >= 1, "
        f"reproducing the costing table's figure of "
        f"{union_row['expected_candidates']} exactly). "
        f"Verified by one pass of the carried Gemini 3 verifier (ruling R1: no "
        f"verifier swaps) at real-time flex tier, {flex_text} on the audited "
        f"flex basis (input x 0.25 + (output + thinking) x 1.50 per million). "
        f"NOTE the verify path stamps cost_basis 'list' with discount 1.0 even "
        f"under flex and records the tier nowhere, so the stage meta's "
        f"total_cost_usd is about twice the invoice "
        f"(reports/r7-gaps-deltas-2026-09-11.md § 2.3). "
        f"Scored on the board frame era2-b-487 with the family's recipe: "
        f"curator reference, 14 buffers, 10,000 BCa draws, seed 42, MCC."
    )
    if point == "opmax":
        return (
            "IN-SAMPLE OPTIMUM (E56 class): the F1@20 argmax of this rung's "
            "own sweep, taken on the BOARD frame per ruling R2. The sweep was "
            "also run on the Era-2 frame full_evaluation_bounds.geojson (the "
            "frame the committed -opmax cells' optima were selected on) and "
            f"the two frames "
            f"{'agree' if rung.get('frames_agree_on_argmax') else 'DISAGREE'} "
            f"on the argmax for this rung. "
            f"Tie-break where needed: highest F1@20, then lowest vote_t, then "
            f"lowest prob_t "
            f"({rung['opmax'].get('n_ties_at_argmax', 0)} point(s) tied here). "
            + shared
        )
    return (
        "CARRIED POINT (the transfer-tax column of ruling R2): prob_t "
        f"{rung['carried']['prob_t']}, k = K = {union_row['n_passes']}, fixed "
        "before this evaluation rather than selected on it. At K = 1 and K = 3 "
        "the corpus's two readings of the carried vote threshold coincide "
        "(k = K, and the gold-standard stride ladder's 1/3/4/8 shell), so this "
        "point is unambiguous; they diverge only at K = 5 and K = 10. " + shared
    )


def rows_for_rung(
    rung: dict[str, Any],
    union_row: dict[str, Any],
    spend: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build the condition rows for one rung (one or two, never more)."""
    rows: list[dict[str, Any]] = []
    identical = bool(rung.get("carried_identical_to_opmax"))

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
                "label": rung["labels"][point],
                "architecture": "proposer-verifier",
                "aggregation": "verified",
                "proposer_pool": rung["pool_slug"],
                "n_passes": union_row["n_passes"],
                "vote_threshold": values["vote_t"],
                "prob_threshold": values["prob_t"],
                "verifier_config": dict(VERIFIER_CONFIG),
                "eval_path": values["eval_path"],
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
        description="Register the K-ladder Phase 2 rungs as conditions"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--write",
        action="store_true",
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

    added = 0
    replaced = 0
    stages_added = 0
    for rung in points:
        union_row = union_rows[rung["row"]]
        spend = spend_by_row.get(rung["row"], {})
        run = register["decomposition"][rung["run_id"]]

        # Ensure the verifier stage is registered before the rows that cite it.
        paths = resolve_paths(union_row)
        stage_id = paths["verifier_stage"]
        if stage_id not in run["verifier_passes"]:
            # The register records a stage path relative to the run's own
            # output root, e.g. "image-n5/image-t0.7/verified-v1-n3".
            run["verifier_passes"][stage_id] = {
                "modality": modality(rung["pool_slug"]),
                "path": str(
                    Path(paths["verify_dir"]).relative_to(RUN_ROOT[rung["run_id"]])
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
                    "+ %s::%s  (%s, %s) n=%s",
                    rung["run_id"],
                    row["label"],
                    row["vote_threshold"],
                    row["prob_threshold"],
                    row["n_candidates"],
                )
            else:
                run["conditions"][existing] = row
                replaced += 1
                logger.info(
                    "~ %s::%s  (refreshed in place)",
                    rung["run_id"],
                    row["label"],
                )

    logger.info(
        "%d row(s) to add, %d to refresh, %d verifier stage(s) to add",
        added,
        replaced,
        stages_added,
    )

    if not args.write:
        logger.info("dry run — nothing written. Pass --write to commit.")
        return

    # The register is serialised with indent=1 and ensure_ascii=False by
    # scripts/build_gs_era2_board_opmax.py; matching it keeps the diff to the
    # rows this script actually touches.
    with open(RUN_CONDITIONS, "w") as handle:
        json.dump(register, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    logger.info("wrote %s", RUN_CONDITIONS.relative_to(BASE_DIR))
    logger.info(
        "next: python scripts/generate_post_run_report.py --all --write, then "
        "python scripts/verify_run_conditions.py"
    )


if __name__ == "__main__":
    main()
