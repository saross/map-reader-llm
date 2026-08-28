#!/usr/bin/env python3
"""
The MINIMAL-vs-HIGH image pair: HP1–HP5 verdicts.

Card § 5a (`planning/image-b-gs-2026-08-28.md`, approved 2026-08-28):
the first matched thinking-level pair on the image track. Runs AFTER
`image_b_analysis.py` has produced both cells' analyses; consumes their
committed outputs plus the two unions, and answers the registered bets:

- HP1: verified best @20 m — HIGH ≈ MINIMAL within GS resolution?
  (paired tile-swap permutation, 10,000 / seed 42, the board chain)
- HP2: union growth ≥ 20 %?
- HP3: MCC within ±0.02?
- HP4: operating point on the lattice (prob ∈ {0.15, 0.20}, k ≥ 8)?
- HP5: proposer cost 3.0–3.5× MINIMAL's audited $20.3?
  (audited-rate reconciliation from the metas' token counts)

Usage::

    python scripts/image_b_pair.py

Zero API. Run on sapphire.

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import glob
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.grid_analysis import CRS  # noqa: E402
from scripts.grid_verifier_analysis import (  # noqa: E402
    per_tile_counts,
    verified_subset,
)
from scripts.image_b_analysis import load_image_union  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    permutation_test_float,
)
from scripts.stride_verifier_analysis import (  # noqa: E402
    COMMON_BOUNDS,
    GROUND_TRUTH,
    reassign_gate,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

VBASE = PROJECT_ROOT / "outputs/image-b-gs-2026-08-28/verifier"
RES = PROJECT_ROOT / "results/image-b-gs-2026-08-28"
# Audited flex rates (token-load audit § 3.4): non-cached input $0.25/M,
# cached $0.05/M, output + thinking $1.50/M.
RATES = {"fresh": 0.25e-6, "cached": 0.05e-6, "out": 1.50e-6}
MIN_PROPOSER_AUDITED = 20.3  # the MINIMAL run's audited proposer spend


def audited_proposer(outroot: Path) -> float:
    """Audited-rate proposer spend from the metas' token counts."""
    total = 0.0
    for f in glob.glob(str(outroot / "run_*" / "*.meta.json")) + glob.glob(
            str(outroot / "run_*_recovery" / "*.meta.json")):
        u = json.loads(open(f).read())["usage_stats"]
        cached = u.get("total_cached_tokens", 0)
        fresh = u.get("total_input_tokens", 0) - cached
        out = (u.get("total_output_tokens", 0)
               + u.get("total_thoughts_tokens", 0)
               + u.get("total_reasoning_tokens", 0))
        total += (fresh * RATES["fresh"] + cached * RATES["cached"]
                  + out * RATES["out"])
    return total


def main() -> int:
    bounds = gpd.read_file(COMMON_BOUNDS)
    ref = gpd.read_file(GROUND_TRUTH).to_crs(CRS)

    a_min = json.loads((RES / "analysis.json").read_text())
    a_high = json.loads((RES / "high/analysis.json").read_text())
    bmin, bhigh = a_min["image_best"], a_high["image_best"]

    sets = {}
    for tag, cell, best in (("min", "g384_ov192_image", bmin),
                            ("high", "g384_ov192_image_high", bhigh)):
        u = reassign_gate(load_image_union(VBASE / cell), bounds, cell)
        sets[tag] = {"union": u,
                     "best": verified_subset(u, best["prob_t"],
                                             best["min_votes"])}

    tm = per_tile_counts(sets["min"]["best"], bounds, ref)
    th = per_tile_counts(sets["high"]["best"], bounds, ref)
    hp1 = permutation_test_float(th["tp"], th["fp"], th["fn"],
                                 tm["tp"], tm["fp"], tm["fn"],
                                 n_permutations=10_000, seed=42)
    logger.info("HP1 HIGH - MIN @20m verified best: dF1=%+.4f p=%.4f "
                "(HIGH %.4f vs MIN %.4f)", hp1["observed_diff"],
                hp1["p_value"], bhigh["f1"], bmin["f1"])

    n_min, n_high = len(sets["min"]["union"]), len(sets["high"]["union"])
    hp2 = {"union_min": n_min, "union_high": n_high,
           "growth": n_high / n_min - 1.0}
    logger.info("HP2 union growth: %d -> %d (%+.1f%%)", n_min, n_high,
                100 * hp2["growth"])

    mcc_min = a_min["buffer_curves"]["image"]["20"]["mcc"]
    mcc_high = a_high["buffer_curves"]["image"]["20"]["mcc"]
    logger.info("HP3 MCC: MIN %.4f vs HIGH %.4f (d %+.4f)",
                mcc_min, mcc_high, mcc_high - mcc_min)

    logger.info("HP4 operating points: MIN (%.2f, k%d) | HIGH (%.2f, k%d)",
                bmin["prob_t"], bmin["min_votes"], bhigh["prob_t"],
                bhigh["min_votes"])

    cost_high = audited_proposer(
        PROJECT_ROOT / "outputs/image-b-gs-2026-08-28/g384_ov192_image_high")
    ratio = cost_high / MIN_PROPOSER_AUDITED
    logger.info("HP5 proposer cost: HIGH audited $%.2f = %.2fx MINIMAL "
                "($%.1f)", cost_high, ratio, MIN_PROPOSER_AUDITED)

    payload = {
        "hp1_high_vs_min_20m": hp1,
        "hp1_bests": {"min": bmin, "high": bhigh},
        "hp2_union": hp2,
        "hp3_mcc": {"min": mcc_min, "high": mcc_high,
                    "delta": mcc_high - mcc_min},
        "hp4_points": {"min": [bmin["prob_t"], bmin["min_votes"]],
                       "high": [bhigh["prob_t"], bhigh["min_votes"]]},
        "hp5_cost": {"high_proposer_audited_usd": cost_high,
                     "min_proposer_audited_usd": MIN_PROPOSER_AUDITED,
                     "ratio": ratio},
    }
    (RES / "high/pair_verdicts.json").write_text(
        json.dumps(payload, indent=2, default=float) + "\n")
    logger.info("PAIR VERDICTS -> %s",
                (RES / "high/pair_verdicts.json").relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
