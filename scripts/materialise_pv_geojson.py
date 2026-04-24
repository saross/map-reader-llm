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

Input expectations:

* The consensus GeoJSON features must be in the same canonical order
  that the verifier manifest used, so that enumerate-index equals
  ``candidate_id``. Both the preregistered threshold-1 consensus and
  post-consensus subsets (e.g. consensus-4of5) satisfy this when they
  were produced by the project's aggregation pipeline, because feature
  order is preserved. A ``--strict-indexing`` check (default on) fails
  loudly if probabilities.json refers to any index beyond the consensus
  feature count.

* Consensus coordinates are assumed to be in UTM 35N (EPSG:32635) by
  default because the project's burial-mound corpus sits in that zone
  and the consensus writer does not declare a CRS. Override with
  ``--crs`` if a future corpus uses a different projection.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:  # pyproj is optional at import time so the strict-indexing CLI path
    # remains usable without it; we only require the package when the
    # lat/lon auto-detect heuristic actually fires (see ``materialise``).
    from pyproj import Transformer
except ImportError:  # pragma: no cover - exercised only when pyproj absent
    Transformer = None  # type: ignore[assignment]

DEFAULT_CRS = "EPSG:32635"
CANDIDATE_KEY_RE = re.compile(r"^candidate_(\d+)$")


def _crs_to_urn(crs: str) -> str:
    """Convert an ``EPSG:NNNNN`` string into the GeoJSON URN form."""
    if crs.upper().startswith("EPSG:"):
        return f"urn:ogc:def:crs:EPSG::{crs.split(':', 1)[1]}"
    return crs


def _max_probabilities_index(results: dict) -> int:
    """Return the largest ``candidate_NNNNN`` index in ``results``.

    Returns ``-1`` if ``results`` is empty or contains no candidate keys.
    """
    max_idx = -1
    for key in results:
        match = CANDIDATE_KEY_RE.match(key)
        if match:
            idx = int(match.group(1))
            if idx > max_idx:
                max_idx = idx
    return max_idx


def materialise(
    consensus_geojson: Path,
    probabilities_json: Path,
    vote_t: int,
    prob_t: float,
    output: Path,
    crs: str = DEFAULT_CRS,
    strict_indexing: bool = True,
) -> int:
    """Write a filtered GeoJSON applying vote_t and prob_t thresholds.

    Args:
        consensus_geojson: Proposer consensus GeoJSON whose features are
            in the same canonical order as the verifier's manifest, so
            that ``enumerate`` index equals ``candidate_id``.
        probabilities_json: Verifier ``probabilities.json`` dict with a
            ``results`` mapping keyed by ``candidate_NNNNN``.
        vote_t: Minimum vote count (proposer consensus).
        prob_t: Minimum verifier ``mound_probability``.
        output: Output GeoJSON path.
        crs: CRS string (e.g. ``"EPSG:32635"``) to stamp on the output
            and, if the consensus file lacks a ``crs`` member, to use
            for the input interpretation.
        strict_indexing: If True (default), raise when any candidate key
            in ``results`` refers to an index beyond the consensus
            feature count. Disables only for legacy inputs.

    Returns:
        Number of kept features.

    Raises:
        ValueError: On CRS mismatch (if ``strict_indexing=True``) or
            index-out-of-range between consensus and probabilities.
    """
    with open(consensus_geojson, encoding="utf-8") as f:
        gj = json.load(f)
    features = gj.get("features", [])

    # CRS consistency check: if the consensus file declares a crs member
    # and it disagrees with the caller's expectation, fail loudly rather
    # than silently stamp the wrong projection onto the output.
    declared_crs = (
        gj.get("crs", {}).get("properties", {}).get("name")
        if isinstance(gj.get("crs"), dict)
        else None
    )
    target_urn = _crs_to_urn(crs)
    if declared_crs and declared_crs != target_urn:
        raise ValueError(
            f"Consensus CRS mismatch: file declares {declared_crs!r} "
            f"but --crs requested {target_urn!r}. Pass --crs to match "
            f"the file's declaration or omit it to accept the default."
        )

    # Lat/lon auto-detect + reproject heuristic (Session 78 discovery).
    #
    # The proposer consensus pipeline emits GeoJSONs without a CRS member
    # but coordinates are written as raw lat/lon (e.g. [25.76, 42.48] for
    # the Bulgarian corpus). Earlier versions of this script silently
    # stamped the target CRS (UTM 35N) onto those lat/lon coordinates,
    # producing files that downstream evaluation interpreted as UTM —
    # leading to F1=0 across every buffer. Detect this case and reproject
    # the geometries from EPSG:4326 to the target CRS before writing.
    needs_reproject = False
    if declared_crs is None and features:
        x0, y0 = features[0]["geometry"]["coordinates"][:2]
        if abs(x0) <= 180 and abs(y0) <= 90:
            needs_reproject = True
            print(
                f"Warning: undeclared CRS + coords look like lat/lon; "
                f"reprojecting from EPSG:4326 to {crs}",
                file=sys.stderr,
            )
    transformer = None
    if needs_reproject:
        if Transformer is None:
            raise RuntimeError(
                "pyproj is required to reproject lat/lon consensus "
                "coordinates to the target CRS but is not installed."
            )
        transformer = Transformer.from_crs(
            "EPSG:4326", crs, always_xy=True,
        )

    with open(probabilities_json, encoding="utf-8") as f:
        probs = json.load(f)
    results = probs.get("results", {})

    # Indexing-consistency check: probabilities.json cannot reference a
    # candidate index beyond what the consensus file contains, because
    # the script uses enumerate(features) as the lookup key.
    max_prob_idx = _max_probabilities_index(results)
    if strict_indexing and max_prob_idx >= len(features):
        raise ValueError(
            f"Indexing mismatch: probabilities.json references "
            f"candidate_{max_prob_idx:05d} but consensus has only "
            f"{len(features)} features. Check that the consensus file "
            f"preserves canonical feature order; a pre-filtered "
            f"consensus will silently misassign verifier probabilities "
            f"to wrong geometries."
        )

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
        # Fail-closed default: a feature with no vote_count is treated
        # as zero votes and will be filtered unless vote_t <= 0. Every
        # pipeline-produced consensus GeoJSON carries vote_count, so
        # this default only activates for malformed/partial inputs.
        vote_count = props.get("vote_count", 0)
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
        # Reproject geometry if the lat/lon auto-detect heuristic fired.
        # Only Point geometries are supported here because the consensus
        # pipeline only emits points; extend if richer geometries appear.
        geom = feat["geometry"]
        if transformer is not None:
            if geom.get("type") != "Point":
                raise ValueError(
                    f"Auto-reproject only supports Point geometries; "
                    f"got {geom.get('type')!r} at index {idx}."
                )
            x_in, y_in = geom["coordinates"][:2]
            x_out, y_out = transformer.transform(x_in, y_in)
            geom = {"type": "Point", "coordinates": [x_out, y_out]}
        kept.append({
            "type": "Feature",
            "geometry": geom,
            "properties": new_props,
        })

    # Explicit CRS header: the proposer consensus GeoJSONs contain UTM
    # coordinates but do not declare a CRS in the file header. Per RFC
    # 7946 (2016) the default CRS is WGS84 (EPSG:4326), so geopandas
    # assigns 4326 on load and downstream reprojection silently
    # produces garbage geometries. RFC 7946 deprecates the ``crs``
    # member but geopandas still honours it for backwards compatibility;
    # declaring it here propagates the correct projection into every
    # downstream loader.
    out_fc = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": target_urn},
        },
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
                   help="Proposer consensus GeoJSON (canonical feature "
                        "order required).")
    p.add_argument("--probabilities", type=Path, required=True,
                   help="Verifier probabilities.json")
    p.add_argument("--vote-t", type=int, required=True,
                   help="Minimum vote count.")
    p.add_argument("--prob-t", type=float, required=True,
                   help="Minimum mound_probability.")
    p.add_argument("--output", type=Path, required=True,
                   help="Output GeoJSON path.")
    p.add_argument("--crs", default=DEFAULT_CRS,
                   help=f"CRS for the output (default {DEFAULT_CRS}). "
                        f"Must match the consensus file's declared CRS "
                        f"if present; otherwise stamped onto the output.")
    p.add_argument("--no-strict-indexing", dest="strict_indexing",
                   action="store_false",
                   help="Disable the consensus-vs-probabilities index "
                        "range check. Only for legacy inputs.")
    args = p.parse_args()

    if not args.consensus.is_file():
        print(f"Consensus not found: {args.consensus}", file=sys.stderr)
        return 2
    if not args.probabilities.is_file():
        print(f"Probabilities not found: {args.probabilities}", file=sys.stderr)
        return 2

    try:
        n = materialise(
            args.consensus, args.probabilities,
            args.vote_t, args.prob_t, args.output,
            crs=args.crs,
            strict_indexing=args.strict_indexing,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {n} features to {args.output} "
          f"(vote_t={args.vote_t}, prob_t={args.prob_t}, "
          f"crs={args.crs})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
