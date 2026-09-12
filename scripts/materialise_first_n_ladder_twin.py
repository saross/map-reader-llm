#!/usr/bin/env python3
"""
Materialise the PRE-VERIFIER set of a first-N ladder rung, as a pairing twin.

The gap this closes
-------------------
Twenty-seven rows of ``results/uplift-supplement/verifier-pairing-worklist.csv``
are ``blocked`` because their verified cell is a **first-N rung** whose candidate
universe was never committed to disk. The rung is re-clustered at analysis time
from the first N of the campaign's committed passes
(``scripts/stride55_ladder.py`` and ``scripts/gemini37_arm_ladder.py``,
``cluster_first_n``), so filtering the committed K-pass union at the rung's vote
threshold would pair the cell with a universe of a different vote basis — the
"different rung of the ladder" refusal
``scripts/build_verifier_pairing_worklist.py`` makes by design
(``planning/uplift-supplement-2026-08-28.md``, "The 27 that stay blocked").

The PI ruled on 2026-09-12 (B3, ``planning/k-ladder-review-2026-09-11.md`` § 5)
that those universes are derived inside the K-ladder job, under its gates. This
script is that derivation. It reproduces the rung EXACTLY as the ladder scripts
build it — same pinned passes, same dedup, same ``cluster_votes`` at
corroboration 1, same standard-grid tile assignment, same nearest-K-candidate
inheritance filter at 10 m — and then takes the rung's PRE-VERIFIER set: the
vote shell ``vote_count >= k`` at ``prob_t = 0.0``.

Why the inheritance filter is applied to a pre-verifier set
-----------------------------------------------------------
It looks like a verifier step and is not. ``cluster_first_n`` yields clusters,
some of which have no committed K-pass candidate within 10 m; the ladder scripts
DROP those before sweeping, so every number the ladder published — including the
``prob_t = 0.0`` row this script gates against — describes the matched subset.
The twin must be that same subset, or it would differ from its verified pair in
membership as well as in the verifier, which is precisely what a pairing twin
exists to avoid.

Gates, all fatal
----------------
1. **Union gate.** The full-K rebuild reproduces the committed union: exact
   candidate count, identical votes, every centroid within
   ``stride55_ladder.UNION_GATE_M`` of the verifier manifest's. This is the
   ladder scripts' own gate 1, re-run, so a re-run pass or a rename cannot move
   a rung silently.
2. **Count gate.** The materialised shell's feature count equals the rung's
   recorded pre-verifier count — the ``prob_t = 0.0`` row at this ``min_votes``
   in the final board's sweep CSV
   (``results/55map-final-board-2026-08-27/sweep_<family>.csv``). A mismatch
   writes nothing and exits non-zero: it is a STOP state for that rung
   (``planning/k-ladder-phase1-run-2026-09-12.md`` § 3.2).
3. **Tile gate.** Every kept feature carries a non-empty ``source_tile``,
   because the corrected-F1 engine scopes detections per map sheet by it
   (``scripts/materialise_pairing_twin.py`` header).

Usage::

    python scripts/materialise_first_n_ladder_twin.py \\
        --cell g384_ov128_55map --n 3 --min-votes 2 \\
        --sweep-family A-N3 \\
        --output results/uplift-supplement/verifier-pairing/first-n/\\
g384_ov128_55map-n3-k2/twin.geojson

Zero API. Heavy (pass dedup plus clustering over up to ten 55-map passes), so
run it on sapphire.

Created: 2026-09-12 (Session 154, K-ladder Phase 1 step 2; PI ruling B3)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.stride55_ladder import (  # noqa: E402
    INHERIT_TOL_M,
    UNION_GATE_M,
    cluster_first_n,
    load_deduped_passes,
)
from scripts.stride55_score import build_map_constrained_index  # noqa: E402
from scripts.stride55_sweep_oracle import (  # noqa: E402
    BOUNDS,
    RUNS as STRIDE_RUNS,
    load_candidates as stride_load_candidates,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The evaluation CRS of the 55-map corrected-F1 chain (UTM 35N, Bulgaria).
EVALUATION_CRS = "EPSG:32635"

#: The final boards' sweep CSVs hold each rung's pre-verifier count at
#: ``prob_t = 0.0``. Column order: family, prob_t, min_votes, n_detections, …
#: The 2026-08-27 board covers cells A and B; the r2 re-reference board of
#: 2026-09-06 covers those plus the 3.7 arms and the fourth cell. Where both
#: hold a family they must agree on ``n_detections`` — they re-scored the same
#: candidate sets against different references, so only TP/FP/FN may differ.
SWEEP_DIRS = (
    PROJECT_ROOT / "results/55map-final-board-2026-08-27",
    PROJECT_ROOT / "results/55map-final-board-r2-2026-09-06",
)

#: Second witness for the count gate: the ladder runs' own sweep CSVs. The two
#: agree on ``n_detections`` and differ only in TP/FP/FN, because the final
#: board re-scored against a later extended GT.
LADDER_SWEEPS = {
    "g384_ov128_55map": PROJECT_ROOT / "results/stride55-2026-08-27/g384_ov128_55map/ladder_sweep_50m.csv",
    "g384_ov192_55map": PROJECT_ROOT / "results/stride55-2026-08-27/g384_ov192_55map/ladder_sweep_50m.csv",
    "g384_ov192_55map_g37": PROJECT_ROOT / "results/gemini37-55map-2026-08-31/ladder/ladder_sweep_50m.csv",
}

#: Total committed passes per cell, and the sweep-CSV family prefix.
CELLS: dict[str, dict[str, Any]] = {
    "g384_ov128_55map": {"k_total": 10, "sweep_prefix": "A"},
    "g384_ov192_55map": {"k_total": 10, "sweep_prefix": "B"},
    "g384_ov192_55map_g37": {"k_total": 5, "sweep_prefix": None},
}


class TwinGateError(RuntimeError):
    """A gate failed, so no twin was written."""


def expected_count_from_final_board(family: str, min_votes: int) -> tuple[int, list[str]]:
    """The rung's recorded pre-verifier count, from the final boards' sweep CSVs.

    Args:
        family: The sweep family, e.g. ``A-N3`` (cell A, rung N = 3) or
            ``ARM1-N3``.
        min_votes: The rung's vote threshold k.

    Returns:
        ``(n_detections, sources)`` — the count on the ``prob_t = 0.0`` row at
        this ``min_votes``, and the paths it was read from.

    Raises:
        TwinGateError: If no board holds the row, or two boards disagree on it.
    """
    found: dict[str, int] = {}
    for base in SWEEP_DIRS:
        path = base / f"sweep_{family}.csv"
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if (float(row["prob_t"]) == 0.0
                        and int(row["min_votes"]) == min_votes):
                    found[str(path.relative_to(PROJECT_ROOT))] = int(
                        row["n_detections"])
                    break
    if not found:
        raise TwinGateError(
            f"no final-board sweep CSV holds family {family} with a "
            f"prob_t = 0.0 row at min_votes = {min_votes}")
    values = set(found.values())
    if len(values) > 1:
        raise TwinGateError(
            f"the final boards disagree on the pre-verifier count for "
            f"{family} at k = {min_votes}: {found}")
    return values.pop(), sorted(found)


def expected_count_from_ladder(cell: str, n: int, min_votes: int) -> int | None:
    """The same count from the ladder run's own sweep CSV, as a second witness.

    Args:
        cell: The campaign cell.
        n: The rung's pass count N.
        min_votes: The rung's vote threshold k.

    Returns:
        ``n_detections`` at ``prob_t = 0.0``, or ``None`` if not recorded.
    """
    path = LADDER_SWEEPS.get(cell)
    if not path or not path.exists():
        return None
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            # The stride ladder CSVs key on "cell"; the 3.7 one on "arm".
            if row.get("cell") not in (None, cell) and "arm" not in row:
                continue
            if int(row["N"]) != n or int(row["min_votes"]) != min_votes:
                continue
            if float(row["prob_t"]) != 0.0:
                continue
            return int(row["n_detections"])
    return None


def rebuild_rung(cell: str, n: int) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    """Rebuild one first-N rung's matched cluster set, with the union gate run.

    Args:
        cell: The campaign cell (``g384_ov128_55map``, ``g384_ov192_55map`` or
            ``g384_ov192_55map_g37``).
        n: The rung's pass count N.

    Returns:
        ``(gdf, gate)`` — the matched clusters with ``vote_count`` and
        ``source_tile``, and a record of the union gate's measurements.

    Raises:
        TwinGateError: If the full-K rebuild does not reproduce the committed
            union.
    """
    spec = CELLS[cell]
    index = build_map_constrained_index()
    if cell == "g384_ov192_55map_g37":
        from scripts.gemini37_arm_ladder import load_deduped_passes as load_g37
        from scripts.gemini37_sweep_oracle import (
            CELLS as G37_CELLS,
            load_candidates as g37_load_candidates,
        )
        passes = load_g37()
        full = g37_load_candidates("arm1", G37_CELLS["arm1"])
        union_n = G37_CELLS["arm1"]["union_n"]
    else:
        bounds = gpd.read_file(BOUNDS)
        passes = load_deduped_passes(cell)
        full = stride_load_candidates(cell, STRIDE_RUNS[cell], bounds)
        union_n = STRIDE_RUNS[cell]["union_n"]

    tree = cKDTree(np.c_[full.geometry.x, full.geometry.y])

    # Gate 1 — the ladder scripts' own union gate, re-run here.
    rebuilt = cluster_first_n(passes, spec["k_total"], index)
    if len(rebuilt) != union_n:
        raise TwinGateError(
            f"{cell}: union gate FAILED — rebuilt {len(rebuilt)} vs committed "
            f"{union_n}")
    dist_full, idx_full = tree.query(
        np.c_[rebuilt.geometry.x, rebuilt.geometry.y], k=1)
    votes_match = (rebuilt["vote_count"].to_numpy()
                   == full["vote_count"].to_numpy()[idx_full])
    if dist_full.max() > UNION_GATE_M or not votes_match.all():
        raise TwinGateError(
            f"{cell}: union gate FAILED — max centroid distance "
            f"{dist_full.max():.6f} m, vote mismatches "
            f"{int((~votes_match).sum())}")
    logger.info("%s: union gate OK (n=%d, max dist %.6f m)",
                cell, len(rebuilt), dist_full.max())

    gdf = cluster_first_n(passes, n, index)
    dist, _ = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
    matched = dist <= INHERIT_TOL_M
    n_total = int(len(gdf))
    gdf = gdf[matched].copy()
    gate = {
        "cell": cell,
        "n_passes": n,
        "k_total": spec["k_total"],
        "committed_union_n": union_n,
        "full_k_rebuild_n": int(len(rebuilt)),
        "full_k_max_centroid_distance_m": float(dist_full.max()),
        "union_gate_tolerance_m": UNION_GATE_M,
        "rung_clusters_before_inheritance_filter": n_total,
        "rung_clusters_unmatched_beyond_tolerance": n_total - int(len(gdf)),
        "inheritance_tolerance_m": INHERIT_TOL_M,
    }
    return gdf, gate


def main(argv: list[str] | None = None) -> int:
    """Materialise one rung's pre-verifier twin, or refuse at a failed gate."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--cell", required=True, choices=sorted(CELLS),
                        help="The campaign cell whose ladder the rung belongs to.")
    parser.add_argument("--n", type=int, required=True,
                        help="The rung's pass count N.")
    parser.add_argument("--min-votes", type=int, required=True,
                        help="The verified cell's vote threshold k; the shell "
                             "vote_count >= k is the twin.")
    parser.add_argument("--sweep-family", default=None,
                        help="Final-board sweep family for the count gate "
                             "(e.g. A-N3, ARM1-N3). Omitted, the ladder run's "
                             "own sweep CSV is used instead.")
    parser.add_argument("--expect-count", type=int, default=None,
                        help="Override the count gate's expected value. Use "
                             "only with a recorded anchor for the number.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Destination GeoJSON.")
    args = parser.parse_args(argv)

    if args.min_votes < 1 or args.min_votes > args.n:
        print(f"REFUSED: k = {args.min_votes} is outside 1..N = {args.n}; a "
              "vote shell is defined relative to its own rung", file=sys.stderr)
        return 2

    ladder_count = expected_count_from_ladder(args.cell, args.n, args.min_votes)
    if args.expect_count is not None:
        expected, source = args.expect_count, "--expect-count"
    elif args.sweep_family:
        try:
            expected, sources = expected_count_from_final_board(
                args.sweep_family, args.min_votes)
        except TwinGateError as error:
            print(f"REFUSED: {error}", file=sys.stderr)
            return 2
        source = " + ".join(sources)
    elif ladder_count is not None:
        expected, source = ladder_count, str(LADDER_SWEEPS[args.cell])
    else:
        print("REFUSED: no recorded pre-verifier count to gate against; pass "
              "--sweep-family or --expect-count", file=sys.stderr)
        return 2

    if ladder_count is not None and ladder_count != expected:
        print(f"REFUSED: the two recorded counts disagree — gate source "
              f"{expected}, ladder CSV {ladder_count}. One of them does not "
              "describe this rung, and guessing which would be worse than "
              "stopping", file=sys.stderr)
        return 2

    try:
        gdf, gate = rebuild_rung(args.cell, args.n)
    except TwinGateError as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2

    shell = gdf[gdf["vote_count"] >= args.min_votes]
    got = int(len(shell))
    if got != expected:
        print(f"REFUSED: count gate FAILED for {args.cell} N={args.n} "
              f"k={args.min_votes} — materialised {got}, recorded {expected} "
              f"({source}). STOP state for this rung; nothing written",
              file=sys.stderr)
        return 2
    logger.info("%s N=%d k=%d: count gate OK (%d)",
                args.cell, args.n, args.min_votes, got)

    missing_tile = [i for i, tile in enumerate(shell["source_tile"]) if not tile]
    if missing_tile:
        print(f"REFUSED: {len(missing_tile)} kept cluster(s) carry no "
              f"source_tile (first {missing_tile[0]}); the corrected-F1 engine "
              "scopes detections per map sheet by it", file=sys.stderr)
        return 2

    features = []
    for order, (_, row) in enumerate(shell.iterrows()):
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point",
                         "coordinates": [float(row.geometry.x),
                                         float(row.geometry.y)]},
            "properties": {
                "candidate_id": order,
                "vote_count": int(row["vote_count"]),
                "source_tile": row["source_tile"],
                "label": "mound",
            },
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "type": "FeatureCollection",
        "name": f"first-n-twin-{args.cell}-n{args.n}-k{args.min_votes}",
        "crs": {"type": "name", "properties": {"name": EVALUATION_CRS}},
        "_materialised": {
            "mode": "first-n-recluster",
            "materialised_at_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds"),
            "script": "scripts/materialise_first_n_ladder_twin.py",
            "derivation": (
                "cluster_first_n(passes[:N]) as scripts/stride55_ladder.py "
                "builds it — pinned deduped passes, cluster_votes at "
                "corroboration 1, standard-grid tile assignment, clusters "
                "without a committed K-pass candidate within "
                f"{INHERIT_TOL_M} m dropped — then the shell "
                f"vote_count >= {args.min_votes} at prob_t = 0.0"),
            "filter": f"vote_count >= {args.min_votes}, prob_t = 0.0",
            "n_kept": got,
            "recorded_count": expected,
            "recorded_count_source": source,
            "ladder_csv_count": ladder_count,
            "gates": gate,
        },
        "features": features,
    }, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {got} features (recorded {expected}) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
