#!/usr/bin/env python3
"""
Final 55-map board addendum: the post-hoc 3.7-family cells.

Materialises cells that the stage-1 sweep swept but never built, at
points the board itself already holds a sweep row for. Two sets, chosen
with ``--set``:

``carried-analogue`` (PI ruling 2026-09-20, item 1)
    The seven missing **carried-analogue** rungs of the 3.7 families.
    Each family's top rung carries a GS-selected operating point
    (ARM1 (0.10, k5); ARM2 (0.80, k5); FOURTH (0.98, k10) — read from
    ``final_board_sweeps.G37_IDENTITY``, so the threshold cannot drift
    from the one the identity gate enforces). A *carried analogue* is
    that same probability threshold applied DOWNWARD to a lower rung,
    with ``k`` set to the rung's own N. The canonical grid board already
    publishes exactly this construction for the two arms
    (``results/gemini37-55map-2026-08-31/grid-board/grid_board.json``,
    ``basis: "carried-analogue"``); it was never carried onto the r2
    board, which is why image-vs-text at K/N = 1 and 3 could only be
    read carried-against-oracle
    (``reports/comparability-inventory-37-runs-2026-09-20.md`` § 3.2).

``mcc-oracle`` (PI ruling 2026-09-20, item 2)
    The ten **tile-MCC argmax** cells of the same ten families, read
    from ``sweeps.json``'s ``mcc_argmax`` (written by
    ``final_board_sweeps.py`` once its sweep record carries the tile
    confusion). The image campaigns publish an ``mcc_oracle`` per rung;
    the text track and the fourth cell had none, so any MCC comparison
    across the two tracks was one-sided.

Both sets are **post-hoc**: they are not registered claims, and they
are labelled ``basis: "... (post-hoc)"`` wherever they appear — the same
discipline as ``final_board_n3_carried.py``'s emergent N = 3 cells, and
the same label prefix that makes ``final_board_sweeps.py`` carry them
forward across a regeneration.

GATE: each materialised cell's detection count must equal the committed
sweep CSV row for its point EXACTLY, proving the same derivation chain
produced it. The ``carried-analogue`` set additionally cross-checks that
row's micro-F1 against the inventory's published figure, so a silent
change of either the CSV or the family build is caught twice.

This script does NOT re-tier the board: ``final_board_50m.json``, its
tiers and its BH family are not touched, and ``final_board_build.py`` is
not run (PI ruling 2026-09-13, carried forward 2026-09-20). Scoring is
``r2_score_cells.py --stage board``, which picks the new cells up from
the manifest.

Usage::

    python scripts/final_board_posthoc_cells.py --set carried-analogue
    python scripts/final_board_posthoc_cells.py --set mcc-oracle
    python scripts/r2_score_cells.py --stage board --jobs 4 --workers 2

Zero API. Run on sapphire.

Created: 2026-09-20 (Session 157)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.build_55map_leaderboard import BOUNDS, board_home  # noqa: E402
from scripts.final_board_sweeps import (  # noqa: E402
    G37_IDENTITY,
    build_g37_families,
)
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402
from scripts.stride55_score import build_map_constrained_index  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: Cross-check for the ``carried-analogue`` set: the micro-F1 @ 50 m the
#: inventory published for each point (§ 3.2, read from the committed sweep
#: CSVs on 2026-09-20). The gate compares the CSV row this run reads against
#: this table to 4 d.p., so a regenerated CSV that moved cannot pass silently.
CARRIED_ANALOGUE_F1 = {
    "ARM2-N1-carried": 0.8459,
    "ARM2-N3-carried": 0.8802,
    "ARM1-N1-carried": 0.7859,
    "ARM1-N3-carried": 0.8469,
    "FOURTH-N1-carried": 0.8348,
    "FOURTH-N3-carried": 0.8744,
    "FOURTH-N5-carried": 0.8754,
}

#: Basis labels. Both contain "post-hoc", which is what
#: ``final_board_sweeps.py``'s carry-forward matches on.
BASIS = {
    "carried-analogue": "carried-analogue (post-hoc)",
    "mcc-oracle": "mcc-oracle (post-hoc)",
}

F1_TOLERANCE = 5e-5  # half a 4-d.p. ulp: identity at published precision


def carried_analogue_points() -> list[tuple[str, str, float, int, str]]:
    """The seven carried-analogue cells: family, label, threshold, k, note.

    Derived rather than listed: each 3.7 family's top rung carries a
    GS-selected ``(prob_t, k_max)`` in
    ``final_board_sweeps.G37_IDENTITY`` — the same table the stage-1
    identity gate enforces — and the analogue applies that ``prob_t``
    downward at every rung ``n < k_max`` with ``k = n``. The rung set
    therefore follows ``k_max`` (5 for the arms, 10 for the fourth cell)
    and cannot drift away from the families the sweep actually builds.

    Returns:
        One tuple per cell: ``(family, label, prob_t, min_votes, note)``,
        in the inventory's order.
    """
    out: list[tuple[str, str, float, int, str]] = []
    for top_family, ((prob_t, k_max), _n) in G37_IDENTITY.items():
        stem = top_family.rsplit("-N", 1)[0]
        for n in (n for n in (1, 3, 5) if n < k_max):
            note = (
                f"carried analogue: ({prob_t:.2f}, k{k_max}) is {stem}'s "
                f"GS-carried operating point at its top rung; the same "
                f"probability threshold is applied downward here with k set "
                f"to this rung's own N. Added 2026-09-20 per "
                f"reports/comparability-inventory-37-runs-2026-09-20.md "
                f"§ 3.2. Post-hoc, not a registered claim."
            )
            out.append((f"{stem}-N{n}", f"{stem}-N{n}-carried", prob_t, n,
                        note))
    return out


def mcc_oracle_points(out_dir: Path) -> list[tuple[str, str, float, int, str]]:
    """The ten tile-MCC argmax cells, read from the board's ``sweeps.json``.

    Args:
        out_dir: The board home holding ``sweeps.json``.

    Returns:
        One tuple per cell: ``(family, label, prob_t, min_votes, note)``.

    Raises:
        SystemExit: If a family's sweep record carries no ``mcc_argmax``
            (i.e. ``final_board_sweeps.py`` has not been re-run with the
            extended sweep record for that family).
    """
    sweeps = json.loads((out_dir / "sweeps.json").read_text())
    families = sweeps.get("families", {})
    stems = [f.rsplit("-N", 1)[0] for f in G37_IDENTITY]
    wanted = [name for name in families
              if name.rsplit("-N", 1)[0] in stems]
    missing = [name for name in wanted if "mcc_argmax" not in families[name]]
    if missing:
        raise SystemExit(
            "sweeps.json carries no mcc_argmax for "
            f"{', '.join(sorted(missing))} — re-run "
            "scripts/final_board_sweeps.py --reference r2 --families "
            "<families> first (PI ruling 2026-09-20, item 2).")
    out: list[tuple[str, str, float, int, str]] = []
    for name in sorted(wanted):
        best = families[name]["mcc_argmax"]
        note = (
            f"tile-MCC argmax of this family's committed sweep space "
            f"(tile-MCC {best['tile_mcc']:.4f} against the F1 argmax's "
            f"{families[name]['argmax']['micro_f1_50']:.4f} micro-F1@50). "
            f"Added 2026-09-20 per "
            f"reports/comparability-inventory-37-runs-2026-09-20.md § 3.7, "
            f"so the text track and the fourth cell carry the MCC oracle "
            f"the image rows already publish. Post-hoc, not a registered "
            f"claim."
        )
        out.append((name, f"{name}-mcc-oracle", float(best["prob_t"]),
                    int(best["min_votes"]), note))
    return out


def sweep_row(out_dir: Path, family: str, prob_t: float,
              min_votes: int) -> dict:
    """The committed sweep CSV row for one point.

    Args:
        out_dir: The board home holding ``sweep_<family>.csv``.
        family: Family name (CSV stem).
        prob_t: Probability threshold.
        min_votes: Minimum vote count.

    Returns:
        The matching row as a dict of strings.

    Raises:
        SystemExit: If the CSV has no row at that point.
    """
    path = out_dir / f"sweep_{family}.csv"
    with path.open(newline="") as fh:
        for row in csvmod.DictReader(fh):
            if (abs(float(row["prob_t"]) - prob_t) < 1e-9
                    and int(row["min_votes"]) == min_votes):
                return row
    raise SystemExit(f"{path.name}: no sweep row at ({prob_t}, k{min_votes})")


def main(which: str, reference: str = "r2", force_r1: bool = False) -> int:
    """Materialise one post-hoc set and append it to the board's manifest.

    Args:
        which: ``carried-analogue`` or ``mcc-oracle``.
        reference: Board vintage — only ``r2`` carries the 3.7 families.
        force_r1: Permit writing into the committed r1 board home
            (read-only by policy, H2/H15).

    Returns:
        Process exit code.

    Raises:
        RuntimeError: If a cell's count does not reproduce its committed
            sweep row exactly, or (carried-analogue) if that row's
            micro-F1 has moved off the inventory's published figure.
    """
    out = board_home(reference)
    if reference == "standardised" and not force_r1:
        raise SystemExit(
            f"{out.relative_to(PROJECT_ROOT)} is the committed r1 board home "
            "and is read-only (H2/H15); the 3.7 families are an r2-only "
            "membership in any case. Use --reference r2.")

    points = (carried_analogue_points() if which == "carried-analogue"
              else mcc_oracle_points(out))
    logger.info("%s: %d cells to materialise", which, len(points))

    bounds = gpd.read_file(BOUNDS)
    if bounds.crs is None:
        bounds = bounds.set_crs("EPSG:4326")
    bounds = bounds.to_crs("EPSG:32635")
    index = build_map_constrained_index()
    families = build_g37_families(index)
    for spec in families.values():
        spec["gdf"] = assign_source_tiles(spec["gdf"], bounds)

    manifest_path = out / "cells_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    have = {c["label"] for c in manifest["cells"]}

    for family, label, prob_t, min_votes, note in points:
        row = sweep_row(out, family, prob_t, min_votes)
        expected = int(row["n_detections"])
        if which == "carried-analogue":
            published = CARRIED_ANALOGUE_F1[label]
            got = float(row["micro_f1_50"])
            if abs(got - published) > F1_TOLERANCE:
                raise RuntimeError(
                    f"{label}: sweep row micro-F1 {got:.6f} has moved off "
                    f"the inventory's published {published:.4f}")
        g = families[family]["gdf"]
        sub = g[(g["mound_probability"] >= prob_t)
                & (g["vote_count"] >= min_votes)]
        if len(sub) != expected:
            raise RuntimeError(
                f"{label}: gate FAILED — {len(sub)} at ({prob_t}, "
                f"k{min_votes}) vs committed sweep {expected}")
        logger.info("%-22s gate OK (%d at (%.2f, k%d), sweep micro-F1 %.4f)",
                    label, len(sub), prob_t, min_votes,
                    float(row["micro_f1_50"]))
        dest = out / "cells" / label / "detections.geojson"
        dest.parent.mkdir(parents=True, exist_ok=True)
        sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
        if label not in have:
            manifest["cells"].append({
                "label": label,
                "det": str(dest.relative_to(PROJECT_ROOT)),
                "basis": BASIS[which],
                "point": f"({prob_t:.2f}, k{min_votes})",
                "committed_eval": False,
                "note": note})
            logger.info("%s: appended to cells_manifest", label)

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    logger.info("%s ADDENDUM COMPLETE (%d cells in manifest)", which.upper(),
                len(manifest["cells"]))
    return 0


if __name__ == "__main__":
    _ap = argparse.ArgumentParser(description=__doc__)
    _ap.add_argument("--set", dest="which", required=True,
                     choices=sorted(BASIS),
                     help="Which post-hoc set to materialise.")
    _ap.add_argument(
        "--reference", choices=["standardised", "r2"], default="r2",
        help="Board vintage to append to (default: r2, the only vintage "
             "whose membership includes the 3.7 families).")
    _ap.add_argument("--force-r1", action="store_true",
                     help="Permit writing into the committed r1 board home.")
    _a = _ap.parse_args()
    sys.exit(main(_a.which, _a.reference, force_r1=_a.force_r1))
