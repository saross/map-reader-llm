#!/usr/bin/env python3
"""
Probe whether a shorter pass sub-pool's candidates are covered by a longer
pool's verifier output, by CANDIDATE-POSITION MATCHING.

Why this exists
---------------
A verifier's ``probabilities.json`` is keyed to the candidate universe the
verifier saw: key ``candidate_{i:05d}`` is feature *i* of that union, in that
union's order. So an existing verifier output can be reused for a shorter
first-N rung only if the rung's candidate set is a POSITION-MATCHED subset of
that union — same feature at the same index. Counts agreeing is not evidence,
and a nearest-neighbour match is a different thing (inheritance, an
approximation), not coverage.

The K-ladder review's step 1 has to classify each K gap as fillable at US$0 or
needing a verifier pass, and the classification turns entirely on this
question. This script answers it from committed artefacts, per pool:

* read the vote >= 1 union of the SHORTER pool (the sub-pool the rung would
  use) and of the LONGER pool (the union a verifier has already scored);
* compare feature *i* of one with feature *i* of the other, in order, at a
  tolerance the caller sets (default 0.01 m — storage precision, not a
  clustering difference);
* report the count of positions that hold the same point, the first index that
  does not, and whether the shorter union is a strict positional prefix.

It also reports the SET-level relation (how many of the shorter union's points
exist anywhere in the longer union within the tolerance), because that
distinguishes "different order, same points" from "genuinely different
clustering" — the two diagnoses the Era-2 board's 2026-09-11 vintage note had
to separate.

Usage::

    python scripts/probe_subpool_verifier_coverage.py \\
        --pair outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus-n5/consensus_t1.geojson \\
               outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus/consensus_t1.geojson \\
        --label "MINIMAL image T0.7: 5-pass sub-pool vs 10-pass union" \\
        --out results/k-ladder-2026-09-12/subpool-coverage-probe.json

Repeat ``--pair``/``--label`` for more comparisons; every probe lands in one
JSON. Zero API. Cheap, but it reads bulk committed data, so run it on sapphire
with the rest of the chain.

Created: 2026-09-12 (Session 154, K-ladder Phase 1 step 1)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Two coordinates closer than this are the same point. A GeoJSON round trip
#: costs about 1e-7 degrees, well under a centimetre in projected metres, so
#: anything above this is a real difference in the clustering.
DEFAULT_TOLERANCE_M = 0.01


def load_points(path: Path) -> list[tuple[float, float]]:
    """Every Point feature's coordinates, in file order.

    Args:
        path: A GeoJSON FeatureCollection of Point features.

    Returns:
        The coordinates as ``(x, y)`` pairs, in the order the file stores them
        — which is the order a ``candidate_{i:05d}`` probability key refers to.

    Raises:
        ValueError: If a feature is not a Point, since a non-Point cannot be
            position-matched against a candidate centroid.
    """
    doc = json.loads(path.read_text(encoding="utf-8"))
    points: list[tuple[float, float]] = []
    for index, feature in enumerate(doc.get("features") or []):
        geom = feature.get("geometry") or {}
        if geom.get("type") != "Point":
            raise ValueError(
                f"{path}: feature {index} is a {geom.get('type')!r}, not a Point; "
                "candidate-position matching is defined on centroids only")
        x, y = geom["coordinates"][:2]
        points.append((float(x), float(y)))
    return points


def positional_match(
    shorter: list[tuple[float, float]],
    longer: list[tuple[float, float]],
    tolerance: float,
) -> dict[str, Any]:
    """Compare the two unions index by index and as sets.

    Args:
        shorter: The sub-pool union's points, in file order.
        longer: The union a verifier has already scored, in file order.
        tolerance: Metres within which two coordinates are the same point.

    Returns:
        A verdict dict: the two sizes, how many leading indices agree, the
        first index that does not, how many of the shorter union's points
        appear anywhere in the longer union, and the covered verdict.
    """
    overlap = min(len(shorter), len(longer))
    agree = 0
    first_mismatch = None
    for i in range(overlap):
        ax, ay = shorter[i]
        bx, by = longer[i]
        if abs(ax - bx) <= tolerance and abs(ay - by) <= tolerance:
            agree += 1
        elif first_mismatch is None:
            first_mismatch = i
    # Set-level containment, on a rounded grid so the tolerance applies.
    scale = 1.0 / tolerance if tolerance else 1.0
    longer_set = {(round(x * scale), round(y * scale)) for x, y in longer}
    in_set = sum(
        1 for x, y in shorter
        if (round(x * scale), round(y * scale)) in longer_set)
    prefix = first_mismatch is None and len(shorter) <= len(longer)
    return {
        "n_shorter": len(shorter),
        "n_longer": len(longer),
        "n_positions_compared": overlap,
        "n_positions_agreeing": agree,
        "first_mismatching_index": first_mismatch,
        "n_shorter_points_present_anywhere_in_longer": in_set,
        "is_positional_prefix": prefix,
        "covered_by_position_match": prefix,
        "verdict": (
            "COVERED: the sub-pool union is a positional prefix of the longer "
            "union, so the longer union's probabilities can be reused by index"
            if prefix else
            "NOT COVERED: the sub-pool union is not a positional prefix, so an "
            "index join against the longer union's probabilities would pair "
            "probabilities with the wrong candidates"),
    }


def main(argv: list[str] | None = None) -> int:
    """Run every requested probe and write one JSON report."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--pair", nargs=2, action="append", metavar=("SHORTER", "LONGER"),
                        required=True,
                        help="Sub-pool union GeoJSON and the longer union a "
                             "verifier has scored. Repeatable.")
    parser.add_argument("--label", action="append", default=[],
                        help="Human label for the matching --pair. Repeatable.")
    parser.add_argument("--tolerance-m", type=float, default=DEFAULT_TOLERANCE_M,
                        help=f"Same-point tolerance in metres (default "
                             f"{DEFAULT_TOLERANCE_M}).")
    parser.add_argument("--out", type=Path, required=True,
                        help="Destination JSON.")
    args = parser.parse_args(argv)

    probes = []
    for index, (shorter_path, longer_path) in enumerate(args.pair):
        label = args.label[index] if index < len(args.label) else f"probe-{index}"
        shorter = load_points(Path(shorter_path))
        longer = load_points(Path(longer_path))
        result = positional_match(shorter, longer, args.tolerance_m)
        probes.append({"label": label, "shorter": shorter_path,
                       "longer": longer_path, **result})
        print(f"{label}\n  {shorter_path}\n  {longer_path}\n  "
              f"{result['n_shorter']} vs {result['n_longer']}; "
              f"{result['n_positions_agreeing']} of "
              f"{result['n_positions_compared']} positions agree; "
              f"set-present {result['n_shorter_points_present_anywhere_in_longer']}; "
              f"prefix={result['is_positional_prefix']}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tolerance_m": args.tolerance_m,
        "method": ("candidate-position matching: feature i of the sub-pool union "
                   "against feature i of the longer union; a verifier's "
                   "probabilities.json is keyed candidate_{i:05d} to the union "
                   "it saw, so only a positional prefix can be reused by index"),
        "n_probes": len(probes),
        "probes": probes,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
