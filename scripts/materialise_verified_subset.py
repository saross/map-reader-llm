#!/usr/bin/env python3
"""
Materialise the accepted (verified) subset of a per-feature-flagged
verifier GeoJSON
==================================================================

The proposer-verifier runs (``proposer-verifier-384`` / ``-512``) write
ONE GeoJSON per verifier configuration containing the **full candidate
set** — every detection the proposer single pass returned — with a
per-feature ``verified`` boolean (``True`` = the verifier accepted the
candidate, ``False`` = rejected) plus verification provenance
(``verification_threshold``, ``verifier_votes``, ``verifier_avg_score``).

Scoring that file as-is measures the *unfiltered proposer baseline*:
every configuration shares the same candidate union, so every one scores
the same F1. Per Decision 1A (Session 94), the scoreable **verifier
output** is the accepted subset (``verified == True``), materialised as
its own GeoJSON so it can be scored independently — only then does the
number measure the verifier rather than the proposer.

This is a pure deterministic transform: NO API calls, NO image crops.

CRS handling
------------
These verifier GeoJSONs store coordinates in WGS84 lon/lat (EPSG:4326)
with **no** ``crs`` member (RFC 7946 default), which the scorer
correctly reprojects to the evaluation CRS (EPSG:32635). A prior bug
(Session 94) arose when UTM-metre coordinates were written without a
``crs`` member and silently misread as lon/lat — producing F1=0 at every
buffer. The cure was to make CRS explicit. This script therefore:

* refuses to run if the input coordinates do **not** look like lon/lat,
  guarding against re-introducing the UTM-misread bug; and
* stamps an explicit ``crs`` member (EPSG:4326, URN form) on the output
  so downstream loaders never have to guess. Stamping 4326 is
  behaviour-identical to leaving the member absent (geopandas defaults a
  crs-less GeoJSON to 4326) but removes the ambiguity.

Usage
-----
    # single file
    python scripts/materialise_verified_subset.py \\
        --input  outputs/h11/proposer-verifier-384/verified-brief-text.geojson \\
        --output outputs/h11/proposer-verifier-384/verified-brief-text-accepted.geojson

    # batch: one accepted-subset per input, written into --output-dir
    python scripts/materialise_verified_subset.py \\
        --input outputs/h11/proposer-verifier-384/verified-*.geojson \\
        --output-dir outputs/h11/proposer-verifier-384 --suffix -accepted

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# WGS84 lon/lat URN — RFC 7946 default CRS, stamped explicitly on outputs
# so no downstream loader has to infer it.
WGS84_URN = "urn:ogc:def:crs:EPSG::4326"


def _first_coord(features: list) -> tuple[float, float] | None:
    """Return the first ``(x, y)`` vertex found in a feature collection.

    Descends nested coordinate arrays (Point, Polygon, MultiPolygon …)
    until it reaches the first numeric pair, so it works regardless of
    geometry type. Returns ``None`` for an empty or geometry-less
    collection.
    """
    for feat in features:
        geom = (feat or {}).get("geometry") or {}
        coords = geom.get("coordinates")
        # Peel off list-of-list nesting (rings, multi-parts) until the
        # innermost element is a scalar coordinate value.
        while isinstance(coords, list) and coords and isinstance(coords[0], list):
            coords = coords[0]
        if (
            isinstance(coords, list)
            and len(coords) >= 2
            and all(isinstance(v, (int, float)) for v in coords[:2])
        ):
            return float(coords[0]), float(coords[1])
    return None


def _looks_like_lonlat(xy: tuple[float, float] | None) -> bool:
    """True if ``xy`` plausibly lon/lat (``|x| <= 180`` and ``|y| <= 90``).

    An empty collection (``xy is None``) returns ``True``: there is no
    coordinate to misread, so materialising an empty accepted subset is
    allowed (a verifier that rejected every candidate).
    """
    if xy is None:
        return True
    x, y = xy
    return abs(x) <= 180.0 and abs(y) <= 90.0


def filter_verified(
    input_path: Path,
    output_path: Path,
    prop: str = "verified",
    keep_value: bool = True,
) -> tuple[int, int]:
    """Write ``output_path`` with only the features whose ``prop`` matches.

    Args:
        input_path: Source verifier GeoJSON carrying a per-feature ``prop``
            boolean over the full candidate set.
        output_path: Destination GeoJSON for the accepted subset.
        prop: Property name carrying the accept/reject flag (default
            ``"verified"``).
        keep_value: The boolean value that marks an accepted feature
            (default ``True``); compared with ``is`` so only a genuine
            boolean ``True``/``False`` is kept, never a truthy string or
            number.

    Returns:
        ``(kept, total)`` feature counts.

    Raises:
        ValueError: if no feature carries ``prop`` (wrong input shape), or
            if the coordinates do not look like lon/lat (guards against the
            Session 94 UTM-misread F1=0 bug).
    """
    gj = json.loads(input_path.read_text(encoding="utf-8"))
    features = gj.get("features", [])

    if features and not any(
        prop in (f.get("properties") or {}) for f in features
    ):
        raise ValueError(
            f"{input_path}: no feature carries a {prop!r} property; this "
            f"does not look like a per-feature-flagged verifier GeoJSON."
        )

    xy = _first_coord(features)
    if not _looks_like_lonlat(xy):
        raise ValueError(
            f"{input_path}: first coordinate {xy} does not look like "
            f"lon/lat (EPSG:4326). Refusing to stamp 4326 onto what may be "
            f"UTM metres — this is the Session 94 CRS-misread bug. Inspect "
            f"and reproject before materialising."
        )

    kept = [
        f
        for f in features
        if (f.get("properties") or {}).get(prop) is keep_value
    ]

    out_fc = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": WGS84_URN}},
        "features": kept,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out_fc), encoding="utf-8")
    return len(kept), len(features)


def main() -> int:
    """CLI entry point. Returns a process exit code."""
    p = argparse.ArgumentParser(
        description="Materialise the verified-subset of per-feature-flagged "
        "verifier GeoJSON(s) (Decision 1A).",
    )
    p.add_argument(
        "--input", type=Path, nargs="+", required=True,
        help="One or more source verifier GeoJSONs.",
    )
    p.add_argument(
        "--output", type=Path,
        help="Output path (single --input only).",
    )
    p.add_argument(
        "--output-dir", type=Path,
        help="Directory for batch mode; one output per input "
        "(named <stem><suffix>.geojson).",
    )
    p.add_argument(
        "--suffix", default="-accepted",
        help="Stem suffix for batch outputs (default '-accepted').",
    )
    p.add_argument(
        "--property", dest="prop", default="verified",
        help="Per-feature flag property to filter on (default 'verified').",
    )
    p.add_argument(
        "--keep-false", action="store_true",
        help="Keep the REJECTED subset (flag is False) instead of accepted.",
    )
    args = p.parse_args()

    keep_value = False if args.keep_false else True

    if args.output is not None:
        if len(args.input) != 1:
            print("--output requires exactly one --input", file=sys.stderr)
            return 2
        jobs = [(args.input[0], args.output)]
    elif args.output_dir is not None:
        jobs = [
            (src, args.output_dir / f"{src.stem}{args.suffix}.geojson")
            for src in args.input
        ]
    else:
        print(
            "Provide --output (single file) or --output-dir (batch).",
            file=sys.stderr,
        )
        return 2

    rc = 0
    for src, dst in jobs:
        if not src.is_file():
            print(f"Missing input: {src}", file=sys.stderr)
            rc = 2
            continue
        try:
            kept, total = filter_verified(
                src, dst, prop=args.prop, keep_value=keep_value,
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            rc = 1
            continue
        print(f"{src.name}: kept {kept}/{total} -> {dst}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
