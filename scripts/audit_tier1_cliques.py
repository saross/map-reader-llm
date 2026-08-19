#!/usr/bin/env python3
"""
Audit every tiering artefact's Tier 1 against the leader's true clique.

``greedy_clique_tiers`` walks conditions in F1-descending order and closes the
current tier at the FIRST condition that is BH-significant against any current
member. Its docstring promises that ``tiers[0]`` is "the leader's clique (the
tie_set)". That promise fails whenever a marginally significant condition sits
immediately below the leader: the tier closes at that condition, and every
lower-ranked condition the test CANNOT separate from the leader is pushed into
tier 2 without ever being considered for tier 1.

The result is order-dependent and can understate the tie set, which matters
because ``tie_set`` is what the register publishes as "statistically
indistinguishable from the best".

This audit recomputes, for each artefact, the maximal set containing the leader
in which EVERY pair is non-significant, and reports where it exceeds Tier 1. It
verifies the recomputed set really is a clique rather than trusting the search.

Usage::

    python scripts/audit_tier1_cliques.py --out results/selection-aware/tier1-clique-audit.json

Notes:
    - Zero API spend; reads committed tiering artefacts only.
    - Cheap; runs anywhere.

Created: 2026-08-19 (Session 137)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import glob
import json
import logging
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def leader_clique(pairwise: list[dict]) -> tuple[list[str], dict[str, float], int]:
    """Return the leader's maximal non-significant clique, F1 map, and violations.

    Candidates are considered in F1-descending order and admitted only if
    non-significant against every member already admitted, so the result is a
    genuine clique by construction; the violation count re-checks that.
    """
    sig: dict[frozenset, bool] = {}
    f1: dict[str, float] = {}
    for p in pairwise:
        sig[frozenset((p["ref_a"], p["ref_b"]))] = bool(p["significant"])
        for side in ("a", "b"):
            if p.get(f"f1_{side}") is not None:
                f1[p[f"ref_{side}"]] = float(p[f"f1_{side}"])
    if not f1:
        return [], {}, 0
    nodes = sorted(f1, key=lambda x: -f1[x])
    clique = [nodes[0]]
    for r in nodes[1:]:
        if all(not sig.get(frozenset((r, m)), False) for m in clique):
            clique.append(r)
    violations = sum(1 for a, b in combinations(clique, 2)
                     if sig.get(frozenset((a, b)), False))
    return clique, f1, violations


def main() -> int:
    """Audit every committed tiering artefact and report understated tiers."""
    ap = argparse.ArgumentParser(description="Audit Tier 1 against the leader's clique.")
    ap.add_argument("--out", type=Path,
                    default=PROJECT_ROOT / "results/selection-aware/tier1-clique-audit.json")
    args = ap.parse_args()

    rows: list[dict[str, Any]] = []
    for f in sorted(glob.glob(str(PROJECT_ROOT / "results/**/tiering*.json"),
                              recursive=True)):
        try:
            doc = json.loads(Path(f).read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if "pairwise" not in doc or "tiers" not in doc:
            continue
        clique, f1, violations = leader_clique(doc["pairwise"])
        if not clique:
            continue
        t1 = doc["tiers"][0]
        members = t1["members"] if isinstance(t1, dict) else t1
        rel = str(Path(f).relative_to(PROJECT_ROOT))
        rows.append({
            "artefact": rel,
            "analysis_id": doc.get("analysis_id") or doc.get("analysis"),
            "n_cells": len(f1),
            "tier1_size": len(members),
            "leader_clique_size": len(clique),
            "clique_violations": violations,
            "understated": len(clique) > len(members),
            "leader": clique[0],
            "clique": [{"ref": r, "f1": f1[r]} for r in clique],
            "missing_from_tier1": [r for r in clique if r not in members],
        })
        flag = "  <-- UNDERSTATED" if len(clique) > len(members) else ""
        logger.info("%-58s cells=%3d tier1=%2d clique=%2d viol=%d%s",
                    rel[-58:], len(f1), len(members), len(clique), violations, flag)

    bad = [r for r in rows if r["understated"]]
    payload = {
        "n_artefacts": len(rows),
        "n_understated": len(bad),
        "note": "Tier 1 understates the leader's clique when a marginally "
                "significant condition sits immediately below the leader and "
                "closes the tier before lower-ranked, non-separable conditions "
                "are considered.",
        "artefacts": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2))
    logger.info("wrote %s", args.out)
    logger.info("understated: %d of %d artefacts", len(bad), len(rows))
    for r in bad:
        logger.info("  %s: tier1=%d, clique=%d, missing %d",
                    r["artefact"], r["tier1_size"], r["leader_clique_size"],
                    len(r["missing_from_tier1"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
