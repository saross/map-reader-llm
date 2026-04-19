#!/usr/bin/env python3
"""
Materialise Post-Verifier GeoJSON from Consensus + Probabilities
=================================================================

For a given proposer-verifier (PV) pipeline stage, emit a filtered
detection GeoJSON by applying two thresholds:

1. ``vote_t`` — minimum proposer consensus vote count.
2. ``prob_t`` — minimum verifier ``mound_probability``.

The source consensus GeoJSON (at threshold 1, i.e. all candidates) is
aligned index-for-index to the verifier's ``probabilities.json`` result
keys (``candidate_00000`` ... ``candidate_NNNNN``). Candidates that
satisfy both thresholds are written to the output GeoJSON, preserving
``source_tiles``/``source_tile`` metadata so that the result is
compatible with the tile-level evaluation pipeline.

This replaces the pipeline ``extract_candidates → run_pv verify``
round-trip for downstream *evaluation* purposes: no API calls or image
crops are required because the verifier has already run and results
are cached in ``probabilities.json``.

Usage::

    python scripts/materialise_pv_geojson.py \\
        --consensus outputs/.../consensus-n5/consensus_t1.geojson \\
        --probabilities outputs/.../verified-v1-n5/probabilities.json \\
        --vote-t 4 --prob-t 0.20 \\
        --output results/leaderboard/era2/pv-materialised/high-text-t03-n5.geojson

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def materialise(
    consensus_geojson: Path,
    probabilities_json: Path,
    vote_t: int,
    prob_t: float,
    output: Path,
) -> int:
    """Write a filtered GeoJSON applying vote_t and prob_t thresholds.

    Args:
        consensus_geojson: Proposer consensus GeoJSON (threshold-1, all
            candidates) whose features align index-for-index with the
            verifier's ``probabilities.json`` result keys.
        probabilities_json: Verifier ``probabilities.json`` dict with a
            ``results`` mapping keyed by ``candidate_NNNNN``.
        vote_t: Minimum vote count (proposer consensus).
        prob_t: Minimum verifier ``mound_probability``.
        output: Output GeoJSON path.

    Returns:
        Number of kept features.
    """
    with open(consensus_geojson, encoding="utf-8") as f:
        gj = json.load(f)
    features = gj.get("features", [])

    with open(probabilities_json, encoding="utf-8") as f:
        probs = json.load(f)
    results = probs.get("results", {})

    kept = []
    for idx, feat in enumerate(features):
        key = f"candidate_{idx:05d}"
        entry = results.get(key)
        if entry is None:
            continue
        prob = entry.get("mound_probability")
        if prob is None or prob < prob_t:
            continue
        props = feat.get("properties", {}) or {}
        vote_count = props.get("vote_count", 1)
        if vote_count < vote_t:
            continue
        # Attach verifier probability + keep provenance
        new_props = dict(props)
        new_props["mound_probability"] = float(prob)
        new_props["candidate_id"] = idx
        # evaluate_detections.py expects source_tile (singular); consensus
        # GeoJSONs carry source_tiles (plural). Promote the first.
        if "source_tile" not in new_props:
            tiles = new_props.get("source_tiles") or []
            if tiles:
                new_props["source_tile"] = tiles[0]
        kept.append({
            "type": "Feature",
            "geometry": feat["geometry"],
            "properties": new_props,
        })

    out_fc = {
        "type": "FeatureCollection",
        "features": kept,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(out_fc, f)
    return len(kept)


def main() -> int:
    """CLI entry point."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--consensus", type=Path, required=True,
                   help="Proposer consensus_t1 GeoJSON (all candidates).")
    p.add_argument("--probabilities", type=Path, required=True,
                   help="Verifier probabilities.json")
    p.add_argument("--vote-t", type=int, required=True,
                   help="Minimum vote count.")
    p.add_argument("--prob-t", type=float, required=True,
                   help="Minimum mound_probability.")
    p.add_argument("--output", type=Path, required=True,
                   help="Output GeoJSON path.")
    args = p.parse_args()

    if not args.consensus.is_file():
        print(f"Consensus not found: {args.consensus}", file=sys.stderr)
        return 2
    if not args.probabilities.is_file():
        print(f"Probabilities not found: {args.probabilities}", file=sys.stderr)
        return 2

    n = materialise(
        args.consensus, args.probabilities,
        args.vote_t, args.prob_t, args.output,
    )
    print(f"Wrote {n} features to {args.output} "
          f"(vote_t={args.vote_t}, prob_t={args.prob_t})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
