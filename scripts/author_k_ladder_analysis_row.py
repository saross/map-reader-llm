#!/usr/bin/env python3
"""
Author the UNSIGNED `k-ladder-2026-09-12` analysis row
=====================================================

Description:
    The K-ladder review's registered outcome. ``findings.md`` § 6.2 recorded
    why the row was not authored earlier: an analysis row states an outcome,
    and the document's headline outcome — which rungs are statistically
    separable — was exactly what had not been measured. It has been measured
    since (§§ 4.1, 4.2, 7.1 and the closeout's tension analyses), so the row
    can be authored.

    The row is authored **UNSIGNED** (``manually_verified_at: null``). Only the
    Principal Investigator signs, and this row's outcome is the review's
    headline claim.

    ``conditions_compared`` is **derived, not transcribed**: every rung cell of
    every ladder is read out of the three committed ladder inventories, so the
    list cannot drift from the artefacts it describes.

    * ``results/k-ladder-2026-09-12/ladders.json`` — the eight Phase 1 ladders
      (the gold-standard stride A ladder and the seven 55-map ladders), whose
      rungs carry a ``condition_id`` each;
    * ``results/k-ladder-2026-09-12/phase2/ladders.json`` — the fourteen Phase 2
      ladders, whose rungs carry ``labels.opmax`` and ``labels.carried``;
    * ``results/k-ladder-2026-09-12/tier-e/operating-points.json`` — tier E's
      three rungs, if it has been scored.

    The PI's instrument ruling is stated in the outcome text as the ruling it
    is: **the board tile-swap is the instrument, the per-map sign-swap the
    cross-check.**

Usage::

    python scripts/author_k_ladder_analysis_row.py --dry-run
    python scripts/author_k_ladder_analysis_row.py --write
    python scripts/generate_post_run_report.py --all --write
    python scripts/generate_hypothesis_outcome_table.py
    python scripts/generate_hypothesis_outcome_table.py --check

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

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

RUN_ANALYSES = BASE_DIR / "results" / "run-analyses.json"
K_LADDER = BASE_DIR / "results" / "k-ladder-2026-09-12"
ANALYSIS_ID = "k-ladder-2026-09-12"


def phase1_condition_ids() -> list[str]:
    """Every rung condition id of the eight Phase 1 ladders."""
    doc = json.loads((K_LADDER / "ladders.json").read_text())
    out: list[str] = []
    for ladder in doc.get("ladders", []):
        for rung in ladder.get("rungs", []):
            cid = rung.get("condition_id")
            if cid:
                out.append(cid)
    return out


def phase2_condition_ids() -> list[str]:
    """Every rung condition id of the fourteen Phase 2 ladders."""
    doc = json.loads((K_LADDER / "phase2" / "ladders.json").read_text())
    out: list[str] = []
    for ladder in doc.get("ladders", []):
        run_id = ladder.get("run_id")
        for rung in ladder.get("rungs", []):
            labels = rung.get("labels") or {}
            identical = bool(rung.get("carried_identical_to_opmax"))
            for key in ("opmax", "carried"):
                if key == "carried" and identical:
                    continue
                label = labels.get(key)
                if label and run_id:
                    out.append(f"{run_id}::{label}")
    return out


def tier_e_condition_ids() -> list[str]:
    """Every rung condition id of tier E, or an empty list if unscored."""
    path = K_LADDER / "tier-e" / "operating-points.json"
    if not path.exists():
        logger.warning("tier E not scored yet: %s", path)
        return []
    doc = json.loads(path.read_text())
    out: list[str] = []
    for rung in doc.get("rungs", []):
        run_id = rung.get("run_id")
        identical = bool(rung.get("carried_is_opmax"))
        for key in ("opmax", "carried"):
            if key == "carried" and identical:
                continue
            label = (rung.get(key) or {}).get("label")
            if label and run_id:
                out.append(f"{run_id}::{label}")
    return out


def registered_ids() -> set[str]:
    """Every condition id the register resolves, for the foreign-key check."""
    doc = json.loads(
        (BASE_DIR / "results" / "run-conditions.json").read_text()
    )
    out: set[str] = set()
    for run_id, entry in doc["decomposition"].items():
        for cond in entry.get("conditions", []):
            out.add(f"{run_id}::{cond['label']}")
    return out


OUTCOME = (
    "The pass-count ladder K at otherwise fixed parameters, on 23 ladders: the "
    "gold-standard stride A ladder (the only one whose every rung is an exact "
    "re-verification of its own first-N union), the thirteen Gemini 3 "
    "pv-diag-384 families and the 3.7 gold-standard text screen that Phase 2 "
    "completed to four rungs for US$24.8065, the grid 384 px / 50 % MINIMAL "
    "text ladder tier E completed for US$4.9595, and the seven 55-map "
    "deployment ladders. "
    "SHAPE: the return is FRONT-LOADED and K = 3 is on the efficient set of "
    "every ladder in the corpus — 37 % to 93 % of a ladder's total F1 gain for "
    "31 % to 64 % of its top rung's cost — while the last step is the worst buy "
    "on every ladder, at US$1,100 to US$43,000 per 0.001 F1 (the 3.7 family's "
    "K = 5 -> K = 10 step buys +0.0002 F1@20 for US$8.65). "
    "WHAT GOVERNS THE RETURN: the proposer's thinking level, and within a level "
    "its temperature. The K = 1 -> best-rung F1 gain is significant on 7 of 7 "
    "HIGH-thinking ladders and 2 of 6 MINIMAL ones; four ladders, every one of "
    "them MINIMAL, greedy-clique into a SINGLE tier in which K buys nothing "
    "detectable; and on both HIGH tracks the gain rises monotonically with "
    "temperature (text +0.0559 -> +0.0735 -> +0.0994, image +0.0780 -> +0.0959 "
    "-> +0.1514 across T 0.3 -> 0.7 -> 1.0). Read as the diversity dividend "
    "(Obs 141) measured on a K ladder: K buys sampling diversity, and pays in "
    "proportion to how much the configuration already generates. "
    "TILE-MCC DOES NOT FOLLOW F1. Across the 21 verified ladders with an "
    "interpretable tile-MCC, F1 rises on all 21 and tile-MCC falls on 16, and "
    "NO ladder shows a significant tile-MCC RISE; the gold-standard ladder's "
    "+0.0135, § 4 of the findings' one apparent counter-example, tests at BH "
    "p = 0.7678. Significant FALLS are found on four ladders — the 3.7-verifier "
    "stride B (-0.0112), 3.7 arm 1 (-0.0099), 3.7 arm 2 (-0.0275) and HIGH "
    "image T 1.0 (-0.0637, BH p = 0.0420, the family with the largest F1 gain). "
    "More passes buy localisation inside already-positive tiles, not tile-level "
    "discrimination, which matters for any application whose unit is the tile "
    "rather than the mound. CAVEAT on the MCC column: tile-MCC is computed by a "
    "string join on source_tile, and three cells of the 3.7 gold-standard text "
    "family are scored on a frame whose tile vocabulary is not their proposer's, "
    "so their tile-MCC is WITHHELD with a named reason rather than reported "
    "(g37-text-k1-verified-opmax, g37-text-k1-verified-carried-p0.10-k1, "
    "g37-text-k3-verified-opmax; raw 0.1337 / 0.1422 / 0.1337). The corpus-wide "
    "exposure is measured at 3 of 149 committed cells the Era-2 board reads, no "
    "published board MCC is affected, and the repair is a corpus-wide decision "
    "with the PI because the 384 px frames overlap "
    "(reports/tile-mcc-geometric-join-2026-09-12.md). Their F1 is sound and is "
    "reported in full. "
    "INSTRUMENT (PI ruling): the board's round-robin tile-swap micro-F1 "
    "permutation is THE instrument — 10,000 permutations, seed 42, BH q = 0.05 "
    "within each ladder's own round-robin, tile-MCC swapped on byte-identical "
    "masks so a ΔF1 and a ΔMCC are two statistics of one permutation — and the "
    "registered per-map paired sign-swap is the CROSS-CHECK. Where both cover a "
    "pair (8 pairs, 2 ladders) all eight tile-MCC significance calls AGREE, with "
    "ΔMCC estimates within 0.0006; one marginal F1 call differs (stride A's "
    "K = 3 -> 5, BH p 0.0079 against 0.0655), so the instrument choice is live "
    "for marginal F1 claims and immaterial to the MCC conclusion. "
    "THE TWO CORPORA AGREE once resolution is accounted for. The deployment "
    "MINIMAL ladders' own cells, scored on random 487-tile subsets of their own "
    "8,541 tiles (200 draws, seed 42, same instrument), keep BH significance in "
    "197 of 200 draws at ΔF1 +0.0547 and in only 39 of 200 at +0.0192 — a "
    "subsampling standard deviation of ~0.0114 either way — so 487 tiles "
    "resolve a ΔF1 of about 0.03 and above and not below. The nine MINIMAL "
    "ladders sort by effect size rather than by corpus (every one at or above "
    "+0.0546 separates, every one at or below +0.0223 does not), and the "
    "deployment range +0.0192..+0.0547 sits INSIDE the gold-standard range "
    "+0.0139..+0.0629. So 'K buys nothing detectable' on four MINIMAL "
    "configurations is a statement about 487 tiles, not about K. "
    "PARETO MCC SET: on tile-MCC no rung above K = 1 is ever the admissible "
    "choice — K = 1 holds the highest tile-MCC on 13 of the 21 interpretable "
    "ladders and is never significantly beaten on it — so the MCC-efficient "
    "rung is K = 1 wherever tile-level discrimination is the objective, while "
    "the F1-efficient rung is K = 3. The two objectives select different rungs, "
    "and that is the review's practical finding. "
    "A GEOMETRY EFFECT, consensus-only: at fixed MINIMAL text T 0.7 the grid "
    "study's K = 1 -> 10 gain is about 2.4x larger at 12.5 % overlap than at "
    "50 % (+0.1454 against +0.0572 at 384 px; +0.0914 against +0.0396 at "
    "512 px), and tile-MCC RISES with K on all four consensus-only cells "
    "(+0.038..+0.154) — the opposite of the verified ladders, consistent with "
    "the same mechanism. Overlap and pass count buy the same redundancy. The "
    "pattern does not survive to the verified deployment ladders, which order "
    "the other way. "
    "NOT CLAIMED: no Hsu MCB admissible set per family (a different instrument, "
    "scripts/selection_aware_intervals.py, still outstanding); no MCC RANKING "
    "of rungs, tiering stays on the preregistered F1; and the five "
    "non-separating ladders' MCC moves are not shown to be zero. "
    "Findings: results/k-ladder-2026-09-12/findings.md (all sections); tension "
    "analyses results/k-ladder-2026-09-12/tension/; spend "
    "reports/k-ladder-phase2-deltas-2026-09-12.md and "
    "results/k-ladder-2026-09-12/tier-e/."
)

ROW: dict[str, Any] = {
    "analysis_id": ANALYSIS_ID,
    "type": "comparison",
    "_note": (
        "The K-ladder review's registered outcome (controlling card "
        "planning/k-ladder-review-2026-09-11.md, rulings R1-R5). 23 ladders at "
        "otherwise fixed parameters across two corpora, two model families, two "
        "thinking levels, two modalities, three temperatures and four tile "
        "geometries. conditions_compared is DERIVED from the three committed "
        "ladder inventories by scripts/author_k_ladder_analysis_row.py, not "
        "transcribed. Phase 1 landed at US$0, Phase 2 at US$24.8065 and tier E "
        "at US$4.9595."
    ),
    "_prereg_rationale": (
        "post-hoc: the preregistration's H3 registers consensus voting over K "
        "proposer passes as a factor and its vote-threshold x N characterisation "
        "as the method (osf:497, 519-521), and H13 registers the tile geometry; "
        "this review executes that factor-at-a-time intent over production "
        "carry-forward pools the registration does not name, under the PI's "
        "'ladder, then board' principle. The operating points of the -opmax "
        "cells are selected on the set they are scored on (E56 class), which the "
        "outcome states."
    ),
    "conditions_compared": [],
    "hypothesis_refs": ["H3", "H13"],
    "preregistered": "post-hoc",
    "deviations": ["E56", "E85"],
    "predicted_outcome": (
        "K's F1 return saturates early (the registered pass-budget Pareto's "
        "reading), and K = 3 is on the efficient set."
    ),
    "tie_set": [],
    "outcome": OUTCOME,
    "paper_section": "Results",
    "output_path": "results/k-ladder-2026-09-12/findings.md",
    "working_notes_obs": [],
    "manually_verified_at": None,
    "_signature_note": (
        "UNSIGNED — authored 2026-09-12 by the closeout job and awaiting the "
        "PI's signature. The outcome is the review's headline claim, so only the "
        "PI signs it. Two things the PI should know before signing: the Hsu MCB "
        "admissible sets are still not supplied, and three cells' tile-MCC is "
        "withheld under the open tile-join decision."
    ),
}


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Author the UNSIGNED k-ladder-2026-09-12 analysis row"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--write", action="store_true",
        help="Write results/run-analyses.json (default: dry run)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Default; no-op")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    p1 = phase1_condition_ids()
    p2 = phase2_condition_ids()
    te = tier_e_condition_ids()
    # Order is deterministic and de-duplicated, so a re-run produces an
    # identical list rather than a reshuffled one.
    ids = sorted(set(p1 + p2 + te))
    logger.info(
        "conditions_compared: %d unique (%d Phase 1, %d Phase 2, %d tier E)",
        len(ids), len(p1), len(p2), len(te),
    )

    known = registered_ids()
    missing = [cid for cid in ids if cid not in known]
    if missing:
        logger.error(
            "%d id(s) do not resolve in results/run-conditions.json — the "
            "generator's foreign-key guard would warn and a tier-1 test would "
            "fail. Not writing.",
            len(missing),
        )
        for cid in missing[:10]:
            logger.error("  unresolved: %s", cid)
        sys.exit(2)
    logger.info("all %d id(s) resolve in the register", len(ids))

    row = dict(ROW)
    row["conditions_compared"] = ids

    doc = json.loads(RUN_ANALYSES.read_text())
    existing = next(
        (
            index
            for index, candidate in enumerate(doc["analyses"])
            if candidate.get("analysis_id") == ANALYSIS_ID
        ),
        None,
    )
    if existing is None:
        doc["analyses"].append(row)
        logger.info("+ %s (appended, %d rows total)", ANALYSIS_ID,
                    len(doc["analyses"]))
    else:
        previous = doc["analyses"][existing]
        if previous.get("manually_verified_at"):
            logger.error(
                "%s is SIGNED (%s) — refusing to overwrite a signed row",
                ANALYSIS_ID, previous["manually_verified_at"],
            )
            sys.exit(3)
        doc["analyses"][existing] = row
        logger.info("~ %s (refreshed in place, still unsigned)", ANALYSIS_ID)

    if not args.write:
        logger.info("dry run — nothing written. Pass --write to commit.")
        return

    with open(RUN_ANALYSES, "w") as handle:
        json.dump(doc, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    logger.info("wrote %s", RUN_ANALYSES.relative_to(BASE_DIR))
    logger.info(
        "next: python scripts/generate_post_run_report.py --all --write, then "
        "python scripts/generate_hypothesis_outcome_table.py [--check]"
    )


if __name__ == "__main__":
    main()
