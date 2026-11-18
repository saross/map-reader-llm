#!/usr/bin/env python3
"""
Detection-input facts for the tile-join Wave 1 census (W1.0, step 4).

For every evaluation in the census extraction (``census_extract.py``), open
its recorded detection input(s), read-only, and record what the file says
about how it was built: the property keys its features carry, the feature
count, and whether any feature carries a merge marker (a vote count or a
member list written by the consensus and union builders). The construction
route is then decided from these facts in the worklist builder.

Detection inputs are often gitignored, so they are read from a data root
(zbook's main checkout) given on the command line; nothing is written there.

Usage (zbook)::

    python3 reports/tile-join-wave-1/scripts/census_detections.py \\
        --census ~/scratch/wave1/w10/census/census.jsonl \\
        --data-root ~/Code/map-reader-llm --workers 14 \\
        > ~/scratch/wave1/w10/census/detections.jsonl

Created: 2026-11-18 (tile-join Wave 1, W1.0)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

#: Property names that only a merging step writes (consensus clustering,
#: union building, or the verifier's materialisation of a union).
MERGE_MARKERS = ("vote_count", "votes", "n_votes", "cluster_size", "source_tiles",
                 "n_members", "member_count", "origin_tiles", "n_passes",
                 "pass_count", "support")
MAX_FILES = 40


def detection_files(rec: dict[str, Any], root: Path) -> list[Path]:
    """Resolve an evaluation's recorded detection inputs to files.

    Args:
        rec: One census record.
        root: Data root that holds the (possibly gitignored) inputs.

    Returns:
        Existing GeoJSON files (a directory input expands to its GeoJSONs).
    """
    det = rec.get("detections")
    paths: list[str] = ([det] if isinstance(det, str) else
                        list(det) if isinstance(det, list) else [])
    if rec.get("detections_dir"):
        paths.append(rec["detections_dir"])
    files: list[Path] = []
    declared_dir = bool(rec.get("detections_dir"))
    for p in paths:
        path = Path(p) if Path(p).is_absolute() else root / p
        if path.is_dir():
            files.extend(resolve_dir(path, rec.get("glob") if declared_dir else None))
        elif path.exists():
            files.append(path)
    return files


def resolve_dir(path: Path, glob_pattern: str | None) -> list[Path]:
    """Resolve a detection directory as the scorer does.

    A recorded ``--glob`` wins; otherwise the canonical pass resolver
    (``scripts.lib_detection_paths.resolve_pool_passes``, the scorer's own,
    imported read-only) is used, falling back to every GeoJSON if it
    refuses. This mirrors ``evaluate_detections.find_detection_files`` and
    the D22 rule that a glob recorded for a recovered source is ignored.

    Args:
        path: Detection directory.
        glob_pattern: Recorded glob, or None.

    Returns:
        Up to :data:`MAX_FILES` files.
    """
    if glob_pattern:
        return sorted(path.glob(glob_pattern))[:MAX_FILES]
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
        from scripts.lib_detection_paths import resolve_pool_passes  # noqa: PLC0415
        found = resolve_pool_passes(path, allow_multiple=True)
    except Exception:  # noqa: BLE001 (any refusal falls back to the listing)
        found = []
    return (found or sorted(path.rglob("*.geojson")))[:MAX_FILES]


def file_facts(path: Path) -> dict[str, Any]:
    """Read one detection file's keys and merge markers.

    Args:
        path: GeoJSON file.

    Returns:
        Key union, feature count, merge markers present, and any
        top-level provenance keys.
    """
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return {"file": str(path), "error": repr(exc)}
    feats = data.get("features") or []
    keys: set[str] = set()
    for f in feats:
        keys.update((f.get("properties") or {}).keys())
    return {
        "file": str(path), "n_features": len(feats), "keys": sorted(keys),
        "merge_markers": [k for k in MERGE_MARKERS if k in keys],
        "top_keys": sorted(k for k in data.keys() if k not in ("features", "type")),
    }


def one(args: tuple[dict[str, Any], str]) -> dict[str, Any]:
    """Facts for one evaluation (worker entry point)."""
    rec, root = args
    files = detection_files(rec, Path(root))
    return {"path": rec["path"], "n_files": len(files),
            "files": [file_facts(f) for f in files]}


def main() -> None:
    """Emit one JSON line per evaluation."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    recs = [json.loads(line) for line in args.census.read_text().splitlines()]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for out in pool.map(one, [(r, str(args.data_root)) for r in recs], chunksize=8):
            sys.stdout.write(json.dumps(out) + "\n")


if __name__ == "__main__":
    main()
