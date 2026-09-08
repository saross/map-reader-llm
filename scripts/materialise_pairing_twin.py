#!/usr/bin/env python3
"""Materialise a pre-verifier twin carrying the ``source_tile`` its pair needs.

The corrected-F1 engine scopes detections per map sheet with
``gdf_det["source_tile"].str.startswith(map_name)``
(``compute_corrected_f1_multi_buffer.compute_counts_at_r``), so every detection
it scores must carry a singular ``source_tile``. The committed consensus
GeoJSONs do not: a consensus candidate is a CLUSTER drawn from several passes
and possibly several tiles, so they carry ``source_tiles`` (plural, a list) and
no singular column. Passing one straight to the engine raises
``KeyError: 'source_tile'`` at the first buffer — which is exactly what the two
55-map twin jobs did.

Where the verified side gets its ``source_tile``
-----------------------------------------------
From the verifier's own ``candidate_manifest.json``: each candidate carries a
singular ``source_tile`` alongside its centroid, and the verified set is
materialised straight from it (``scripts/55maps-t0.3-rebuild-verified-geojson.py``,
``scripts/build_post_verifier_geojson.py``, ``scripts/stride55_score.py``).

This script builds the twin from THAT SAME MANIFEST, keeping every candidate at
``vote_count >= k`` and copying its recorded ``source_tile`` verbatim. The twin
therefore shares the verified cell's candidate universe, centroids, and tile
attribution exactly, and differs from it in one thing only — no probability
filter. That is the parameter control an uplift number needs.

Why not derive ``source_tile`` from the bounds file
---------------------------------------------------
Because that is a spatial inference the corpus has already measured and
rejected. ``scripts/stride55_score.py`` records that an unconstrained
nearest-centroid assignment flips 10.1 % of candidates to the adjacent sheet
(the 55-map rasters overlap) and moves corrected-F1 by about 0.04. An
engine-side "assign from bounds when the column is missing" fallback would BE
that inference, applied silently, to one side of a paired comparison. Copying a
recorded value is not an inference at all: verified against
``inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`` on 2026-08-29,
every ``source_tile`` in all five 55-map generalisation manifests is already a
standard-grid tile name (0 unknown of 5,151 / 4,583 / 5,185 / 5,453 / 6,494
distinct).

Gates, all fatal
----------------
* every kept candidate carries a non-empty ``source_tile``;
* candidate ids are the contiguous range the manifest declares;
* the manifest's candidate count is compared with the committed consensus
  GeoJSON's feature count, and any difference is reported (it is a real
  difference in candidate universe, not something to paper over).

The union mode (S151, 2026-09-08)
---------------------------------
Twenty-one pairing rows resolve their twin by the ``union`` rule: the committed
vote >= 1 union over the N passes (``union_k<N>.geojson`` under the run's
verifier tree), from which the paired vote shell must be filtered before
scoring. Those unions already carry a singular ``source_tile`` and a
``vote_count`` per Point feature (they are the file the verifier's crop
manifest was extracted from), so the twin is the shell ``vote_count >= k`` of
the union, geometry and CRS copied verbatim. The gate is the candidate
universe: ``--expect-manifest`` compares the union's feature count with the
verifier stage's crop-manifest candidate count and refuses on any difference,
so a union that is not the set the verifier consumed cannot be paired.

Usage::

    python scripts/materialise_pairing_twin.py \\
        --crop-manifest outputs/55maps-image-generalisation/crops/candidate_manifest.json \\
        --min-votes 3 \\
        --output results/uplift-supplement/verifier-pairing/<cell>/twin.geojson

    python scripts/materialise_pairing_twin.py \\
        --union outputs/grid-2026-08-18/verifier/g512_ov064/union_k10.geojson \\
        --min-votes 5 \\
        --expect-manifest outputs/grid-2026-08-18/verifier/g512_ov064/crops/candidate_manifest.json \\
        --output results/uplift-supplement/verifier-pairing/<cell>/twin-5of10.geojson

Zero API. Pure local transform.

Created: 2026-08-29 (uplift-supplement card, pairing-scoring repair)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#: The CRS the 55-map corrected-F1 chain works in (UTM 35N, Bulgaria).
EVALUATION_CRS = "EPSG:32635"


class TwinMaterialisationError(RuntimeError):
    """A gate failed, so no twin was written.

    Every gate here guards a silent-wrongness mode: a missing ``source_tile``
    would drop a detection from its map's scope, and a candidate-set mismatch
    would compare two different universes while calling the difference verifier
    uplift.
    """


def build_twin(
    manifest: dict[str, Any], min_votes: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Select the vote shell from a crop manifest and shape it as GeoJSON features.

    Args:
        manifest: A parsed ``candidate_manifest.json``.
        min_votes: The vote threshold k; candidates with ``vote_count >= k``
            are kept, matching the verified cell's own shell.

    Returns:
        ``(features, stats)`` — the twin's features and a summary of what was
        selected, for the caller to report.

    Raises:
        TwinMaterialisationError: If a kept candidate has no ``source_tile``, or
            the candidate ids are not the contiguous range.
    """
    candidates = manifest.get("candidates") or []
    if not candidates:
        raise TwinMaterialisationError("the crop manifest lists no candidates")

    ids = [c.get("candidate_id") for c in candidates]
    if sorted(ids) != list(range(len(candidates))):
        raise TwinMaterialisationError(
            f"candidate ids are not the contiguous range 0..{len(candidates) - 1}; "
            "the manifest cannot be joined positionally"
        )

    features: list[dict[str, Any]] = []
    missing_tile: list[int] = []
    for candidate in candidates:
        properties = candidate.get("properties") or {}
        votes = properties.get("vote_count")
        if not isinstance(votes, int) or votes < min_votes:
            continue
        # The candidate's own recorded tile. Copied, never inferred: the
        # verified side of this pair carries exactly this value.
        tile = candidate.get("source_tile") or properties.get("source_tile")
        if not tile:
            missing_tile.append(candidate.get("candidate_id"))
            continue
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [candidate["centroid_x"], candidate["centroid_y"]],
            },
            "properties": {
                "candidate_id": candidate["candidate_id"],
                "vote_count": votes,
                "source_tile": tile,
                "label": "mound",
            },
        })

    if missing_tile:
        raise TwinMaterialisationError(
            f"{len(missing_tile)} kept candidate(s) carry no source_tile "
            f"(first: {missing_tile[0]}). The corrected-F1 engine scopes by "
            "source_tile, so these detections would silently leave their map's "
            "scope. Refusing to write a twin that would score differently from "
            "its verified pair for a reason unrelated to the verifier"
        )

    return features, {
        "n_candidates": len(candidates),
        "n_kept": len(features),
        "min_votes": min_votes,
        "source_geojson": manifest.get("source_geojson"),
    }


def build_twin_from_union(
    union: dict[str, Any], min_votes: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Select the vote shell ``vote_count >= k`` from a committed union GeoJSON.

    Args:
        union: A parsed ``union_k<N>.geojson`` (Point features carrying
            ``vote_count`` and a singular ``source_tile``).
        min_votes: The vote threshold k of the verified cell.

    Returns:
        ``(features, stats)`` — copies of the kept features (geometry and
        properties verbatim) and a selection summary.

    Raises:
        TwinMaterialisationError: If the union has no features, a feature lacks
            an integer ``vote_count`` or a non-empty ``source_tile``, or the
            shell is empty.
    """
    all_features = union.get("features") or []
    if not all_features:
        raise TwinMaterialisationError("the union GeoJSON holds no features")
    kept: list[dict[str, Any]] = []
    bad_votes: list[int] = []
    missing_tile: list[int] = []
    for index, feature in enumerate(all_features):
        properties = feature.get("properties") or {}
        votes = properties.get("vote_count")
        if not isinstance(votes, int):
            bad_votes.append(index)
            continue
        if votes < min_votes:
            continue
        if not properties.get("source_tile"):
            missing_tile.append(index)
            continue
        kept.append({
            "type": "Feature",
            "geometry": feature.get("geometry"),
            "properties": dict(properties),
        })
    if bad_votes:
        raise TwinMaterialisationError(
            f"{len(bad_votes)} union feature(s) carry no integer vote_count "
            f"(first index {bad_votes[0]}); the shell cannot be selected"
        )
    if missing_tile:
        raise TwinMaterialisationError(
            f"{len(missing_tile)} kept feature(s) carry no source_tile (first "
            f"index {missing_tile[0]}); the corrected-F1 engine scopes by it"
        )
    if not kept:
        raise TwinMaterialisationError(
            f"no union feature reaches vote_count >= {min_votes}; the shell is empty"
        )
    return kept, {
        "n_candidates": len(all_features),
        "n_kept": len(kept),
        "min_votes": min_votes,
        "source_geojson": union.get("name"),
    }


def main(argv: list[str] | None = None) -> int:
    """Materialise one pre-verifier twin (crop-manifest mode or union mode).

    Args:
        argv: Command-line arguments.

    Returns:
        Process exit code: 0 on success, 2 on a failed gate.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--crop-manifest", type=Path,
                        help="The verifier stage's candidate_manifest.json (manifest mode).")
    source.add_argument("--union", type=Path,
                        help="The committed vote >= 1 union GeoJSON (union mode).")
    parser.add_argument(
        "--expect-manifest", type=Path, default=None,
        help=(
            "Union mode gate: the verifier stage's candidate_manifest.json; the "
            "union's feature count must equal its candidate count, else refused."
        ),
    )
    parser.add_argument("--min-votes", type=int, required=True,
                        help="Vote threshold k, matching the verified cell.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Destination GeoJSON.")
    parser.add_argument(
        "--expect-consensus", type=Path, default=None,
        help=(
            "Committed consensus GeoJSON to compare candidate counts against. "
            "A difference is reported, not silently accepted."
        ),
    )
    args = parser.parse_args(argv)

    if args.union is not None:
        union = json.loads(args.union.read_text(encoding="utf-8"))
        try:
            features, stats = build_twin_from_union(union, args.min_votes)
        except TwinMaterialisationError as error:
            print(f"REFUSED: {error}", file=sys.stderr)
            return 2
        if args.expect_manifest is not None:
            manifest = json.loads(args.expect_manifest.read_text(encoding="utf-8"))
            n_manifest = len(manifest.get("candidates") or [])
            if n_manifest != stats["n_candidates"]:
                print(
                    f"REFUSED: the union holds {stats['n_candidates']} features but "
                    f"the verifier stage's crop manifest lists {n_manifest} "
                    "candidates; they are not the same candidate universe, so the "
                    "pair would differ in membership as well as in the verifier",
                    file=sys.stderr,
                )
                return 2
            stats["n_manifest_candidates"] = n_manifest
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({
            "type": "FeatureCollection",
            "name": f"twin-{args.min_votes}of-union",
            "crs": union.get("crs"),
            "_materialised": {
                "mode": "union",
                "source_union": str(args.union),
                "filter": f"vote_count >= {args.min_votes}",
                "n_union": stats["n_candidates"],
                "n_kept": stats["n_kept"],
                "expect_manifest": str(args.expect_manifest) if args.expect_manifest else None,
            },
            "features": features,
        }, indent=1), encoding="utf-8")
        print(
            f"wrote {stats['n_kept']} of {stats['n_candidates']} union features "
            f"at vote_count >= {args.min_votes} to {args.output}"
        )
        return 0

    manifest = json.loads(args.crop_manifest.read_text(encoding="utf-8"))
    try:
        features, stats = build_twin(manifest, args.min_votes)
    except TwinMaterialisationError as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2

    if args.expect_consensus is not None and args.expect_consensus.exists():
        committed = json.loads(args.expect_consensus.read_text(encoding="utf-8"))
        n_committed = len(committed.get("features") or [])
        delta = n_committed - stats["n_candidates"]
        stats["n_committed_consensus"] = n_committed
        stats["candidate_universe_delta"] = delta
        if delta:
            print(
                f"NOTE: the committed consensus set holds {n_committed} features "
                f"and the crop manifest {stats['n_candidates']} (delta {delta:+d}). "
                "The twin follows the MANIFEST, because that is the candidate "
                "universe the verified side was drawn from; a twin built from "
                "the committed set would differ from its pair in candidate "
                "membership as well as in the verifier.",
                file=sys.stderr,
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": EVALUATION_CRS}},
        "features": features,
    }, indent=1), encoding="utf-8")

    print(
        f"wrote {stats['n_kept']} of {stats['n_candidates']} candidates "
        f"at vote_count >= {args.min_votes} to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
