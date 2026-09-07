#!/usr/bin/env python3
"""
Sensitivity of the study's instruments: MDE table + equivalence margins.

PI-commissioned (2026-08-28): the paper makes negative claims ("varying
the image library has no statistically significant effect") whose
evidential weight depends on the instruments' statistical power. This
script harvests the COMMITTED permutation-null records across corpora
and instruments and reports, per instrument:

- the permutation null SD (the instrument's noise floor),
- the Minimum Detectable Effect at 50 % and 80 % power for a two-sided
  α = 0.05 paired test (1.96 σ and 2.80 σ),
- and, for the seven H8 library contrasts, a TOST-style equivalence
  test (normal approximation on the permutation null, flagged as such)
  across a grid of candidate margins Δ — reporting the smallest margin
  at which ALL seven contrasts pass at α = 0.05.

No re-computation of permutations: every σ comes from a committed
record, so the table is an audit of instruments as actually run.

Usage::

    python scripts/sensitivity_mde.py

Zero API, seconds of CPU (pure JSON harvesting + arithmetic).

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import glob
import json
import logging
import sys
from math import erf, sqrt
from pathlib import Path
from statistics import median

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "results/sensitivity-mde-2026-08-28"
#: Reference revision r2 (planning/reference-revision-2026-09-06.md, step 5):
#: the 55-map deployment instrument re-measured on the r2 final board. Its
#: permutation nulls are harvested beside the r1 rows into sensitivity-r2.json;
#: the committed r1 artefact is never rewritten by the r2 mode.
R2_BOARD = PROJECT_ROOT / "results/55map-final-board-r2-2026-09-06/final_board_50m.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

Z50 = 1.959964  # two-sided alpha=.05 critical value (50% power MDE)
Z80 = Z50 + 0.841621  # + z_{0.80} (80% power MDE)
MARGIN_GRID = (0.03, 0.04, 0.05, 0.06, 0.07, 0.075, 0.08, 0.09, 0.10)


def phi(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def harvest(reference: str = "standardised") -> dict[str, dict]:
    """Committed null SDs, grouped by (corpus, instrument).

    Args:
        reference: ``standardised`` (the committed r1 rows, default) or
            ``r2`` -- adds the r2 final board's 55-map instrument as a
            further group; the r1 groups stay, so the two can be compared.
    """
    groups: dict[str, dict] = {}

    def add(group: str, n_tiles, sd: float, meta: str) -> None:
        g = groups.setdefault(group, {"n_tiles": n_tiles, "sds": [],
                                      "source": meta})
        g["sds"].append(float(sd))

    # GS 327-tile consensus instrument (H8 v2 family).
    for f in glob.glob(str(PROJECT_ROOT
                           / "results/h8-v2/permutation-t4/*/"
                           "pairwise_permutation_result.json")):
        d = json.loads(open(f).read())
        pt = d["permutation_test"]
        add("GS 327-tile tile-swap (H8 v2, 20 m)", pt["n_tiles"],
            pt["null_distribution"]["std"],
            "results/h8-v2/permutation-t4/")
    # GS 340-tile single/consensus board (Era-1).
    e1 = json.loads((PROJECT_ROOT
                     / "results/era1-leaderboard/tiering_20m.json"
                     ).read_text())
    for p in e1.get("pairwise", []):
        if "null_std" in p:
            add("GS 340-tile tile-swap (Era-1 board, 20 m)",
                p.get("n_tiles"), p["null_std"],
                "results/era1-leaderboard/tiering_20m.json")
    # GS common-footprint verified sets (image-B head-to-head).
    ib = json.loads((PROJECT_ROOT
                     / "results/image-b-gs-2026-08-28/analysis.json"
                     ).read_text())
    for key in ("head_to_head_20m", "saturation_N5_vs_N10",
                "saturation_N3_vs_N10"):
        r = ib.get(key)
        if r and "null_std" in r:
            add("GS common-footprint tile-swap (verified sets, 20 m)",
                r.get("n_tiles"), r["null_std"],
                "results/image-b-gs-2026-08-28/analysis.json")
    # 55-map 8,541-tile deployment board.
    fb = json.loads((PROJECT_ROOT
                     / "results/55map-final-board-2026-08-27/"
                     "final_board_50m.json").read_text())
    for p in fb["pairwise"]:
        if "null_std" in p:
            add("55-map 8,541-tile tile-swap (final board, 50 m)",
                p.get("n_tiles"), p["null_std"],
                "results/55map-final-board-2026-08-27/final_board_50m.json")
    if reference == "r2":
        if not R2_BOARD.exists():
            raise SystemExit(f"{R2_BOARD} does not exist: "
                             "build the r2 final board (step 4e) first")
        fb2 = json.loads(R2_BOARD.read_text())
        for p in fb2["pairwise"]:
            if "null_std" in p:
                add("55-map 8,541-tile tile-swap (final board r2, 50 m)",
                    p.get("n_tiles"), p["null_std"],
                    str(R2_BOARD.relative_to(PROJECT_ROOT)))
    return groups


def h8_tost() -> tuple[list[dict], float | None]:
    """Normal-approximation TOST for the seven H8 contrasts."""
    rows = []
    for f in sorted(glob.glob(str(
            PROJECT_ROOT / "results/h8-v2/permutation-t4/*/"
            "pairwise_permutation_result.json"))):
        d = json.loads(open(f).read())
        pt = d["permutation_test"]
        obs = pt["observed_f1_diff"]
        sd = pt["null_distribution"]["std"]
        row = {"contrast": Path(f).parent.name, "observed": obs,
               "null_sd": sd, "tost_p": {}}
        for m in MARGIN_GRID:
            p1 = 1.0 - phi((obs + m) / sd)  # H0: diff <= -m
            p2 = phi((obs - m) / sd)        # H0: diff >= +m
            row["tost_p"][m] = max(p1, p2)
        rows.append(row)
    passing = None
    for m in MARGIN_GRID:
        if all(r["tost_p"][m] < 0.05 for r in rows):
            passing = m
            break
    return rows, passing


def main(reference: str = "standardised") -> int:
    out_name = "sensitivity.json" if reference == "standardised" else "sensitivity-r2.json"
    groups = harvest(reference)
    tost_rows, tost_margin = h8_tost()
    OUT.mkdir(parents=True, exist_ok=True)

    table = []
    for name, g in groups.items():
        sd_med = median(g["sds"])
        table.append({
            "instrument": name, "n_tiles": g["n_tiles"],
            "n_comparisons": len(g["sds"]),
            "null_sd_median": sd_med,
            "null_sd_range": [min(g["sds"]), max(g["sds"])],
            "mde_50pc_power": Z50 * sd_med,
            "mde_80pc_power": Z80 * sd_med,
            "source": g["source"]})
        logger.info("%-52s n=%3d sd=%.4f  MDE50=%.3f  MDE80=%.3f",
                    name, len(g["sds"]), sd_med, Z50 * sd_med,
                    Z80 * sd_med)
    logger.info("H8 TOST: smallest margin passing all 7 = %s", tost_margin)
    for r in tost_rows:
        logger.info("  %-38s obs %+0.4f sd %.4f  p(Δ=%.3f)=%.4f",
                    r["contrast"], r["observed"], r["null_sd"],
                    tost_margin or 0.075,
                    r["tost_p"].get(tost_margin or 0.075))

    payload = {"mde_table": table,
               "h8_tost": {"rows": tost_rows,
                           "smallest_passing_margin": tost_margin,
                           "method": ("two one-sided tests, normal "
                                      "approximation on the committed "
                                      "permutation null SD — an "
                                      "approximation, flagged as such")},
               "notes": [
                   "MDE = z * null SD for the paired tile-swap "
                   "instrument as actually run (alpha=.05 two-sided; "
                   "z=1.96 for 50% power, 2.80 for 80%).",
                   "Per-sheet sign-swap records (55-map A-vs-B) do not "
                   "store null SDs; their resolution is evidenced "
                   "directly by detected effects down to ~0.010 "
                   "(p=0.0042-0.0147).",
                   "The cross-scale calibration (Obs 362; P6) is the "
                   "empirical anchor: a real ~0.010 effect invisible "
                   "at GS scale was resolved at 55-map scale."]}
    payload["reference"] = reference
    (OUT / out_name).write_text(
        json.dumps(payload, indent=2) + "\n")
    logger.info("SENSITIVITY TABLE -> %s",
                (OUT / out_name).relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    import argparse

    _ap = argparse.ArgumentParser(description=__doc__)
    _ap.add_argument("--reference", choices=("standardised", "r2"), default="standardised",
                     help="standardised = the committed rows (default); r2 = add the r2 "
                          "final board's instrument, written to sensitivity-r2.json.")
    sys.exit(main(_ap.parse_args().reference))
