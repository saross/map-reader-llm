#!/usr/bin/env python3
"""Filter a consensus / WBF candidate GeoJSON to a minimum vote count.

Multi-pass aggregation (greedy spatial clustering or Weighted Boxes Fusion)
emits one candidate per fused cluster, each carrying a ``vote_count`` property
(how many of the ``total_passes`` proposer passes contributed to that cluster).
The *raw* candidate file therefore contains every cluster down to ``vote_count``
of 1 (a single-pass detection). To compare two aggregation algorithms at a
matched operating point — or to materialise the headline condition at a chosen
vote threshold — the candidates must be filtered to ``vote_count >= N``.

This is exactly how the greedy primary is materialised: ``consensus_t4.geojson``
is the greedy candidate set restricted to ``vote_count`` in {4, 5} (i.e. >= 4 of
5 passes). This script applies the same restriction to any candidate GeoJSON so
that, for example, a WBF candidate set can be scored at the same vote threshold
as its greedy counterpart (the apples-to-apples comparator used by the
post-hoc greedy-vs-WBF equivalence check established in Decision 26,
``vote_t = 4`` at K = 5; neither WBF nor the t=4 operating point is
preregistered — the registration specifies greedy clustering, §8.5, with a
full threshold grid search and no a priori threshold selection).

The filter is purely structural: every feature property is preserved untouched;
only features failing the ``vote_count`` threshold are dropped. The CRS block and
any top-level GeoJSON keys are carried through verbatim.

Usage:
    python scripts/filter_detections_by_vote.py \
        --input outputs/h8-v2/wbf/canonical/wbf_candidates.geojson \
        --output outputs/h8-v2/wbf/canonical/wbf_vote4.geojson \
        --min-votes 4

Exit codes:
    0  success
    1  input missing, malformed, or a feature lacks a ``vote_count`` property
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def filter_features_by_vote(geojson: dict, min_votes: int) -> tuple[dict, Counter]:
    """Return a copy of ``geojson`` keeping only features with vote_count >= min_votes.

    Args:
        geojson: a parsed GeoJSON ``FeatureCollection`` whose features each carry
            an integer ``vote_count`` property.
        min_votes: the inclusive minimum vote count to retain.

    Returns:
        A 2-tuple of (filtered FeatureCollection, vote_count distribution of the
        *input* as a Counter), so the caller can report what was dropped.

    Raises:
        KeyError: if any feature lacks a ``vote_count`` property — the filter must
            never silently treat a missing vote as zero (that would drop valid
            candidates or, worse, keep them under a default).
    """
    features = geojson.get("features", [])
    dist: Counter = Counter()
    kept: list[dict] = []
    for feat in features:
        props = feat.get("properties") or {}
        if "vote_count" not in props:
            raise KeyError(
                f"feature {props.get('candidate_id', '?')} has no 'vote_count' "
                "property; refusing to filter (cannot assume a default vote)"
            )
        vc = props["vote_count"]
        dist[vc] += 1
        if vc >= min_votes:
            kept.append(feat)

    # Shallow-copy the collection, swap in the filtered feature list; preserve
    # CRS and every other top-level key (type, name, crs, …) verbatim.
    out = dict(geojson)
    out["features"] = kept
    return out, dist


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(
        description="Filter a candidate GeoJSON to vote_count >= N (preserves all properties)."
    )
    parser.add_argument("--input", type=Path, required=True,
                        help="Input candidate GeoJSON (must carry per-feature vote_count).")
    parser.add_argument("--output", type=Path, required=True,
                        help="Output path for the filtered GeoJSON.")
    parser.add_argument("--min-votes", type=int, required=True,
                        help="Inclusive minimum vote_count to retain (e.g. 4 for >= 4 of 5).")
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input does not exist: {args.input}", file=sys.stderr)
        return 1
    try:
        geojson = json.loads(args.input.read_text())
    except json.JSONDecodeError as exc:
        print(f"ERROR: input is not valid JSON: {exc}", file=sys.stderr)
        return 1

    try:
        filtered, dist = filter_features_by_vote(geojson, args.min_votes)
    except KeyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(filtered, indent=2))

    n_in = sum(dist.values())
    n_out = len(filtered["features"])
    dist_str = ", ".join(f"{k}:{dist[k]}" for k in sorted(dist))
    print(f"vote_count distribution (input): {{{dist_str}}}")
    print(f"kept {n_out}/{n_in} features (vote_count >= {args.min_votes}) -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
