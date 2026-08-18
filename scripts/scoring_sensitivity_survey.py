#!/usr/bin/env python3
"""
Establish which committed conditions are exposed to each scoring-path sensitivity.

Session 136 surfaced two independent properties of
``scripts/evaluate_detections.py``. This script answers "how much of the
committed corpus does each one touch?" over every condition in
``results/conditions-manifest.json``, and writes a machine-readable
exposure register.

**Sensitivity 1 — missing within-pass deduplication.** The scorer has no
deduplication step, so any detection set that reaches it still carrying
the cross-tile duplicates produced by the study's 12.5 % tile overlap
scores those duplicates as false positives. The preregistered 20 m
within-pass deduplication (§ 8.5 Step 1) lives in
``scripts/merge_passes.py``.

Exposure here is deliberately established by MEASUREMENT, not by
architecture label. Reading the label would give the wrong answer: a
proposer-verifier cell whose proposer pool is a single raw pass never
passes through ``merge_passes`` at all, because
``scripts/extract_candidates.py`` crops one candidate per input feature
without clustering, so the duplicates survive verification and land in
the scored set. The test applied is therefore direct — count the
features lying within the 20 m deduplication radius of another feature
in the same artefact.

**Sensitivity 2 — order-dependent tile assignment.** When a detection
GeoJSON carries no ``source_tile`` property, the scorer derives one at
``scripts/evaluate_detections.py:1431-1444`` by taking the FIRST
intersecting bounds tile in GeoDataFrame row order. Exposure is
therefore exactly "the artefact lacks a ``source_tile`` property".

Usage::

    python scripts/scoring_sensitivity_survey.py \\
        --output results/scoring-sensitivity-2026-08-18/exposure-survey.json

Notes:
    - Zero API spend; reads committed artefacts only.
    - Reprojects every artefact through
      ``evaluate_detections.load_geojson`` before applying the metric
      20 m test, because committed detection files are stored in a
      mixture of UTM 35N and WGS84 degrees.
    - Run on sapphire: it opens several hundred GeoJSONs and builds a
      KD-tree for each.

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_detection_paths import resolve_pool_passes  # noqa: E402
from scripts.merge_passes import DISTANCE_THRESHOLD_METRES  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: Default conditions manifest.
DEFAULT_MANIFEST = PROJECT_ROOT / "results/conditions-manifest.json"

#: A condition counts as duplicate-exposed above this share of its
#: features lying within the deduplication radius of another feature.
#: Deduplicated artefacts sit at or near zero; raw per-pass artefacts sit
#: an order of magnitude above it. The threshold is not load-bearing —
#: the full per-condition fraction is written out.
EXPOSURE_THRESHOLD = 0.01


def resolve_detection_paths(cond: dict[str, Any]) -> list[str]:
    """Resolve a condition's scored detection files from its provenance.

    Walks ``provenance.source_files`` (evaluation.json paths) and reads
    the ``_metadata`` block each one carries, which records exactly what
    the scorer was pointed at. Three input modes need handling:

    - ``--detections``: an explicit list of files.
    - ``--detections-dir``: a directory. A recorded ``--glob`` that names
      a per-pass artefact is honoured by resolving the pool through
      ``lib_detection_paths.resolve_pool_passes``, which expands BOTH
      naming conventions — the recorded pattern is convention-A-only and
      replaying it verbatim silently drops any real-time pass (defect D6).
      A glob naming something else (``replication_*/consensus_t3.geojson``,
      ``accepted_run*.geojson``) is replayed verbatim, because it targets a
      non-pass artefact the resolver knows nothing about. A directory that
      neither route matches falls back to a wider pattern.
    - stale paths: a few artefacts were relocated after their evaluation
      ran; these are recovered by unique basename under ``outputs/``.

    Args:
        cond: One entry from the conditions manifest.

    Returns:
        Sorted list of repo-relative detection GeoJSON paths.
    """
    out: list[str] = []
    for src in (cond.get("provenance") or {}).get("source_files") or []:
        if not os.path.exists(src):
            continue
        try:
            ev = json.loads(Path(src).read_text())
        except (OSError, json.JSONDecodeError):
            logger.warning("Unreadable evaluation record: %s", src)
            continue
        meta = ev.get("_metadata") or {}
        cli = meta.get("cli_args") or {}
        pattern = cli.get("glob")
        value = (meta.get("input_files") or {}).get("detections")
        if value is None:
            value = cli.get("detections") or cli.get("detections_dir") or cli.get("batch")
        if isinstance(value, str):
            value = [value]
        for path in value or []:
            if os.path.isdir(path):
                if pattern and "detections" not in pattern:
                    # Non-pass artefact (consensus / accepted set) — replay
                    # the recorded pattern verbatim.
                    hits = sorted(glob.glob(os.path.join(path, pattern)))
                else:
                    hits = [str(f) for f in resolve_pool_passes(
                        Path(path), allow_multiple=True,
                    )]
                if not hits:
                    hits = sorted(glob.glob(os.path.join(path, "*/detections*.geojson")))
                out.extend(hits)
            elif os.path.isfile(path):
                out.append(path)
            else:
                alt = sorted(glob.glob(
                    os.path.join("outputs", "**", os.path.basename(path)),
                    recursive=True,
                ))
                out.extend(alt[:1] if len(alt) == 1 else [path])
    return sorted(set(out))


def artefact_stats(
    path: str,
    radius: float,
    cache: dict[str, Any],
) -> dict[str, Any] | None:
    """Measure one detection artefact's duplicate load and tile-key status.

    Args:
        path: Detection GeoJSON path.
        radius: Deduplication radius in metres.
        cache: Memoisation dict shared across conditions.

    Returns:
        Dict with ``n_features``, ``n_within_radius`` (features having at
        least one neighbour inside the radius), and ``has_source_tile``,
        or ``None`` if the file could not be read.
    """
    if path in cache:
        return cache[path]
    try:
        gdf = load_geojson(Path(path))
    except Exception:  # noqa: BLE001 — any read failure is reported, not raised
        logger.warning("Unreadable detection artefact: %s", path)
        cache[path] = None
        return None
    if gdf.empty:
        cache[path] = None
        return None

    centroids = gdf.geometry.centroid
    pts = np.column_stack([centroids.x.values, centroids.y.values])
    involved: set[int] = set()
    if len(pts) > 1:
        for a, b in cKDTree(pts).query_pairs(radius):
            involved.add(a)
            involved.add(b)

    cache[path] = {
        "n_features": int(len(gdf)),
        "n_within_radius": len(involved),
        "has_source_tile": "source_tile" in gdf.columns,
    }
    return cache[path]


def survey(manifest_path: Path, radius: float) -> dict[str, Any]:
    """Build the exposure register over every condition in the manifest.

    Args:
        manifest_path: Path to ``results/conditions-manifest.json``.
        radius: Deduplication radius in metres.

    Returns:
        Register dict ready to serialise.
    """
    manifest = json.loads(manifest_path.read_text())
    conditions = manifest["conditions"]
    cache: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []

    for cond in conditions:
        paths = resolve_detection_paths(cond)
        stats = [s for s in (artefact_stats(p, radius, cache) for p in paths)
                 if s is not None]
        n = sum(s["n_features"] for s in stats)
        dup = sum(s["n_within_radius"] for s in stats)
        buffers = cond["metrics"]["per_buffer"]
        rows.append({
            "condition_id": cond["condition_id"],
            "architecture": cond["architecture"],
            "aggregation": cond["aggregation"],
            "detection_paths": paths,
            "n_artefacts_read": len(stats),
            "n_features": n,
            "n_features_within_dedup_radius": dup,
            "duplicate_fraction": (dup / n) if n else None,
            "dedup_exposed": bool(n) and (dup / n) > EXPOSURE_THRESHOLD,
            "tiebreak_exposed": any(not s["has_source_tile"] for s in stats),
            "f1_20": buffers.get("20", {}).get("f1"),
            "f1_30": buffers.get("30", {}).get("f1"),
            "resolved": bool(stats),
        })

    dedup = [r for r in rows if r["dedup_exposed"]]
    tie = [r for r in rows if r["tiebreak_exposed"]]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest": str(manifest_path),
        "dedup_radius_metres": radius,
        "exposure_threshold": EXPOSURE_THRESHOLD,
        "summary": {
            "n_conditions": len(rows),
            "n_unresolved": sum(1 for r in rows if not r["resolved"]),
            "n_dedup_exposed": len(dedup),
            "n_tiebreak_exposed": len(tie),
            "n_exposed_to_both": len({r["condition_id"] for r in dedup}
                                     & {r["condition_id"] for r in tie}),
            "dedup_exposed_by_architecture": dict(
                collections.Counter(r["architecture"] for r in dedup)),
            "tiebreak_exposed_by_architecture": dict(
                collections.Counter(r["architecture"] for r in tie)),
            "dedup_exposed_by_run": dict(collections.Counter(
                r["condition_id"].split("::")[0] for r in dedup)),
        },
        "conditions": rows,
    }


def main() -> int:
    """Run the survey and write the exposure register.

    Returns:
        Process exit code (0 on success).
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST,
                    help="Conditions manifest to survey.")
    ap.add_argument("--output", type=Path, required=True,
                    help="Destination JSON for the exposure register.")
    ap.add_argument("--radius", type=float, default=DISTANCE_THRESHOLD_METRES,
                    help="Deduplication radius in metres (default 20).")
    args = ap.parse_args()

    register = survey(args.manifest, args.radius)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(register, indent=2))

    s = register["summary"]
    logger.info("conditions: %d (unresolved %d)", s["n_conditions"], s["n_unresolved"])
    logger.info("dedup-exposed: %d %s", s["n_dedup_exposed"],
                s["dedup_exposed_by_architecture"])
    logger.info("tie-break-exposed: %d %s", s["n_tiebreak_exposed"],
                s["tiebreak_exposed_by_architecture"])
    logger.info("exposed to both: %d", s["n_exposed_to_both"])
    logger.info("Wrote %s", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
