#!/usr/bin/env python3
"""
Tier the tier E ladder with the board instrument (US$0, sapphire)
================================================================

Description:
    The last step of tier E: run the board's own round-robin tile-swap
    permutation over the four rungs of the verified grid 384 px / 50 % MINIMAL
    text ladder — K = 1, 3, 5 from tier E and K = 10 from the committed
    ``grid-postverifier-2026-08-18`` cell — with ``--permute-mcc``, so the F1 and
    tile-MCC arms see byte-identical swap masks and a ΔF1 and a ΔMCC are two
    statistics of one permutation.

    **Why a scratch conditions sidecar, not the register.** The K = 10 rung's
    registered condition (``grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10``)
    carries its committed evaluation on ``grid_common_bounds.geojson``, and the
    other three are on the board frame. The tiering harness requires one frame
    across the cells it tiers, and it is correct to: a ladder scored on two
    polygon sets is not a ladder. The register is therefore left alone and a
    scratch sidecar points the K = 10 rung at its board-frame re-score — the
    same pattern ``scripts/k_ladder_mcc_test.py`` established for the analyses
    file, for the same reason (breaking a circularity without writing to a
    register).

    The board-frame re-score is a derived comparison, not a new cell, exactly as
    ``findings.md`` § 2's board-frame columns are for the gold-standard stride
    ladder. It is not registered as a condition.

Usage::

    python scripts/tier_e_ladder_tiering.py

Outputs:
    results/k-ladder-2026-09-12/tier-e/tiering-input/{run-analyses,run-conditions}.json
    results/k-ladder-2026-09-12/tier-e/tiering/tiering_20m.{json,md}
    results/k-ladder-2026-09-12/tier-e/ladder.json

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

from scripts.run_k_ladder_tier_e import (  # noqa: E402
    BOARD_BOUNDS,
    CARRIED_PROB,
    HEADLINE_BUFFER,
    RUN_ID,
    SCORES_JSON,
    TIER_E_DIR,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

ANALYSIS_ID = "k-ladder-tier-e-2026-09-12"
INPUT_DIR = TIER_E_DIR / "tiering-input"
TIERING_DIR = TIER_E_DIR / "tiering"
LADDER_JSON = TIER_E_DIR / "ladder.json"

N_PERMUTATIONS = 10_000
SEED = 42

#: The K = 10 rung: the committed grid cell's detections, re-scored on the board
#: frame by this job so the ladder sits on one frame.
K10 = {
    "label": "g384-ov192-k10-verified-p0.15-k10-boardframe",
    "vote_threshold": 10,
    "prob_threshold": CARRIED_PROB,
    "n_passes": 10,
    "detections": (
        "results/grid-2026-08-18/conditions-verified/g384_ov192/"
        "detections.geojson"
    ),
    "eval_path": (
        "results/k-ladder-2026-09-12/tier-e/cells/"
        "grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10-boardframe/"
        "evaluation.json"
    ),
}


def tier_e_rungs() -> list[dict[str, Any]]:
    """Read tier E's three sweep-optimal rungs from its scores file."""
    scores = json.loads(SCORES_JSON.read_text())
    out: list[dict[str, Any]] = []
    for row in scores["rungs"]:
        opmax = row.get("opmax") or {}
        if not opmax.get("eval_path"):
            logger.error("K=%s has no scored opmax cell", row["K"])
            sys.exit(2)
        out.append(
            {
                "label": opmax["label"],
                "vote_threshold": opmax["vote_t"],
                "prob_threshold": opmax["prob_t"],
                "n_passes": row["K"],
                "detections": None,
                "eval_path": opmax["eval_path"],
                "f1_20": opmax.get("f1_20"),
                "tile_mcc": opmax.get("tile_mcc"),
            }
        )
    return out


def read_cell_figures(eval_path: str) -> dict[str, Any]:
    """Read a cell's headline F1 and tile-MCC back from its own evaluation.

    Args:
        eval_path: Repository-relative path to an ``evaluation.json``.

    Returns:
        ``{"f1_20", "tile_mcc", "n_detections"}``, with ``tile_mcc`` ``None``
        when the scorer withheld it.
    """
    doc = json.loads((BASE_DIR / eval_path).read_text())
    summary = doc.get("summary", {})
    buffers = {
        int(entry["buffer_metres"]): entry
        for entry in summary.get("buffers", [])
    }
    headline = buffers.get(HEADLINE_BUFFER, {})
    tile = summary.get("tile_classification") or {}
    mcc = tile.get("mcc")
    return {
        "f1_20": headline.get("f1"),
        "tile_mcc": mcc.get("point") if isinstance(mcc, dict) else mcc,
        "tile_mcc_withheld": bool(tile.get("withheld")),
        "n_detections": summary.get("n_detections"),
    }


def write_inputs(rungs: list[dict[str, Any]]) -> tuple[Path, Path]:
    """Write the scratch analyses and conditions sidecars.

    Args:
        rungs: The four rungs in ascending K order.

    Returns:
        ``(analyses_path, conditions_path)``.
    """
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    readme = (
        "TIERING INPUT — NOT REGISTERED. Written by "
        "scripts/tier_e_ladder_tiering.py so "
        "scripts/era1_leaderboard_tiering.py can tier the tier E ladder's four "
        "rungs on ONE frame. The K = 10 rung's eval_path here is its BOARD-FRAME "
        "re-score, not the committed grid-common evaluation its registered row "
        "carries; that re-score is a derived comparison, not a new cell. "
        "results/run-conditions.json and results/run-analyses.json are not "
        "modified and this file must never be written back over either."
    )

    register = json.loads(
        (BASE_DIR / "results" / "run-conditions.json").read_text()
    )
    source = register["decomposition"][RUN_ID]
    by_label = {c["label"]: c for c in source["conditions"]}

    conditions: list[dict[str, Any]] = []
    for rung in rungs:
        existing = by_label.get(rung["label"])
        if existing is not None:
            row = dict(existing)
        else:
            # The K = 10 board-frame rung: clone the committed row's identity
            # and point it at the board-frame evaluation.
            committed = by_label["g384-ov192-k10-verified-p0.15-k10"]
            row = dict(committed)
            row["label"] = rung["label"]
            row["detections"] = rung["detections"]
        row["eval_path"] = rung["eval_path"]
        row["_note"] = (
            "TIERING INPUT ONLY — see this file's _README. "
            + (row.get("_note") or "")
        )
        conditions.append(row)

    conditions_path = INPUT_DIR / "run-conditions.json"
    conditions_path.write_text(
        json.dumps(
            {
                "_README": readme,
                "schema_version": "1.0",
                "decomposition": {
                    RUN_ID: {
                        "proposer_pools": source.get("proposer_pools", {}),
                        "verifier_passes": source.get("verifier_passes", {}),
                        "conditions": conditions,
                        "_ignored_evals": [],
                    }
                },
            },
            indent=2,
        )
        + "\n"
    )

    analyses_path = INPUT_DIR / "run-analyses.json"
    analyses_path.write_text(
        json.dumps(
            {
                "_README": readme,
                "schema_version": "1.0",
                "analyses": [
                    {
                        "analysis_id": ANALYSIS_ID,
                        "type": "comparison",
                        "_note": (
                            "Tier E: the verified grid 384 px / 50 % MINIMAL "
                            "text K ladder, sweep-optimal basis, board frame "
                            f"era2-b-487, headline buffer {HEADLINE_BUFFER} m."
                        ),
                        "conditions_compared": [
                            f"{RUN_ID}::{rung['label']}" for rung in rungs
                        ],
                        "hypothesis_refs": ["H3", "H13"],
                        "outcome": (
                            "PENDING: this is a tiering input, not a registered "
                            "result"
                        ),
                        "paper_section": "Results",
                        "output_path": None,
                        "working_notes_obs": [],
                        "preregistered": "post-hoc",
                        "deviations": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n"
    )
    return analyses_path, conditions_path


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Tier the tier E ladder with the board instrument"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--n-permutations", type=int, default=N_PERMUTATIONS,
        help=f"Permutation count (default: {N_PERMUTATIONS})",
    )
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    rungs = tier_e_rungs()
    k10 = dict(K10)
    k10.update(read_cell_figures(k10["eval_path"]))
    rungs.append(k10)
    rungs.sort(key=lambda rung: rung["n_passes"])
    logger.info(
        "ladder: K = %s", ", ".join(str(r["n_passes"]) for r in rungs)
    )

    analyses, conditions = write_inputs(rungs)
    TIERING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "scripts/era1_leaderboard_tiering.py",
        "--analysis-id", ANALYSIS_ID,
        "--conditions", str(conditions.relative_to(BASE_DIR)),
        "--analyses", str(analyses.relative_to(BASE_DIR)),
        "--bounds", BOARD_BOUNDS,
        "--output-dir", str(TIERING_DIR.relative_to(BASE_DIR)),
        "--buffer", str(HEADLINE_BUFFER),
        "--n-permutations", str(args.n_permutations),
        "--seed", str(args.seed),
        "--permute-mcc",
    ]
    logger.info("$ %s", " ".join(command))
    subprocess.run(command, check=True, cwd=BASE_DIR)

    tiering = json.loads(
        (TIERING_DIR / f"tiering_{HEADLINE_BUFFER}m.json").read_text()
    )
    pairwise = tiering.get("pairwise") or []
    mcc = (tiering.get("mcc_permutation") or {}).get("pairwise") or []
    ladder = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "family": (
            "Gemini 3 MINIMAL text 384 px / 50 % (B geometry), grid pool, "
            "VERIFIED"
        ),
        "corpus": "4-map gold standard",
        "frame": "era2-b-487",
        "reference": "inputs/vectors/references/mounds-reference.geojson",
        "headline_buffer_m": HEADLINE_BUFFER,
        "instrument": (
            "round-robin tile-swap micro-F1 permutation with --permute-mcc, "
            f"{args.n_permutations} permutations, seed {args.seed}, BH q = 0.05, "
            "greedy-clique tiers"
        ),
        "rungs": rungs,
        "n_tiles": tiering.get("n_tiles"),
        "n_permutations": tiering.get("n_permutations"),
        "seed": tiering.get("seed"),
        "fdr_q": tiering.get("fdr_q"),
        "tiers": tiering.get("tiers"),
        "n_tiers": len(tiering.get("tiers") or []) or None,
        "tie_set": tiering.get("tie_set"),
        "n_pairs_f1": len(pairwise),
        "n_significant_f1": sum(
            1 for row in pairwise if row.get("significant")
        ),
        "n_pairs_mcc": len(mcc),
        "n_significant_mcc": sum(1 for row in mcc if row.get("significant")),
        "pairwise_f1": pairwise,
        "pairwise_mcc": mcc,
        "ranking": tiering.get("ranking"),
    }
    LADDER_JSON.write_text(json.dumps(ladder, indent=2) + "\n")
    logger.info(
        "tiers %s, tie set %s, F1 %d/%d significant, MCC %d/%d -> %s",
        ladder["n_tiers"],
        len(tiering.get("tie_set") or []),
        ladder["n_significant_f1"],
        ladder["n_pairs_f1"],
        ladder["n_significant_mcc"],
        ladder["n_pairs_mcc"],
        LADDER_JSON.relative_to(BASE_DIR),
    )


if __name__ == "__main__":
    main()
