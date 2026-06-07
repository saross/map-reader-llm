#!/usr/bin/env python3
"""
Materialise phase3c (H9 diversity) cross-variant consensus GeoJSONs.
===================================================================

The Phase 3c diversity study (``retest-phase3c``, H9) never wrote its
diversity-pool consensus detections to disk: ``analyse_diversity.py`` builds
each pool in memory, evaluates F1 internally, and persists only the aggregate
sweep CSV / report. To decompose the run into the manifest with re-scorable
conditions (14-buffer + MCC, matching the pv-diag-384 precedent) we need the
diversity-pool consensus GeoJSONs on disk.

What a "diversity pool" is
--------------------------
Per the preregistered grouping rule (studies/phase3c-h9-diversity-track*.yaml,
``consensus_design.grouping_rule``):

    Replication k = {run_k from sub-condition p1, ..., run_k from p5}

So each H9 condition (A=baseline/identical, B=instruction-variant, C=image/
hard-negative [track 1 only], D=temperature, E=combined) has 5 replications,
each a 5-pass *cross-variant* pool. We reproduce exactly the
``analyse_diversity`` pipeline — ``load_replication_passes`` (per-pass dedup,
reprojected to EPSG:32635) → ``cluster_across_passes`` → ``apply_threshold`` —
so the materialised GeoJSONs are the *same* pools the published diversity F1
numbers were computed from.

CRS
---
``apply_threshold`` emits centroids in the clustering CRS (EPSG:32635, metres).
The 14-buffer scorer (``evaluate_detections.py``) treats a crs-less GeoJSON as
WGS84 (RFC 7946) and reprojects to EPSG:32635 — so a crs-less file holding UTM
metres would be silently misread (the historical F1=0 / NaN bug). We therefore
reproject every materialised consensus back to **EPSG:4326** before writing,
matching the on-disk format of the phase3a consensus GeoJSONs (which the scorer
already handles correctly).

Output layout (consumed by the dir-mode replicate-mean re-score)::

    <out>/<track>/<condition>/replication_<k>/consensus_t<t>.geojson

so a given (condition, threshold) replicate-mean globs
``<out>/<track>/<condition>/replication_*/consensus_t<t>.geojson`` (5 files).

Usage
-----
    # Dry run — list what would be built
    python scripts/materialise_phase3c_consensus.py

    # Build (run on zbook / sapphire, not amd-tower)
    python scripts/materialise_phase3c_consensus.py --execute

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-06-07
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import mapping, shape

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from analyse_diversity import (  # noqa: E402
    extract_consensus_design,
    load_replication_passes,
    load_study_yaml,
)
from merge_passes import apply_threshold, cluster_across_passes  # noqa: E402

CLUSTER_CRS = "EPSG:32635"
STORAGE_CRS = "EPSG:4326"

# Track -> (study YAML, detections study_dir).
TRACKS = {
    "track1-image": (
        "studies/phase3c-h9-diversity-track1.yaml",
        "outputs/retest/phase3c/track1-image",
    ),
    "track2-text": (
        "studies/phase3c-h9-diversity-track2.yaml",
        "outputs/retest/phase3c/track2-text",
    ),
}

DEFAULT_OUT = "outputs/retest/phase3c/diversity-consensus"


def reproject_fc_to_storage(consensus_fc: dict) -> dict:
    """Reproject a consensus FeatureCollection from CLUSTER_CRS to STORAGE_CRS.

    ``apply_threshold`` returns Point features in the clustering CRS (UTM
    metres). This reprojects geometries back to WGS84 in place so the scorer
    reads them correctly, preserving all feature properties.

    Args:
        consensus_fc: GeoJSON FeatureCollection dict from apply_threshold().

    Returns:
        The same dict, geometries reprojected to STORAGE_CRS.
    """
    feats = consensus_fc.get("features", [])
    if not feats:
        return consensus_fc
    geoms = [shape(f["geometry"]) for f in feats]
    reproj = gpd.GeoSeries(geoms, crs=CLUSTER_CRS).to_crs(STORAGE_CRS)
    for feat, geom in zip(feats, reproj):
        feat["geometry"] = mapping(geom)
    return consensus_fc


def materialise_condition(
    study_dir: Path,
    condition: str,
    sub_conditions: list[str],
    n_replications: int,
    out_dir: Path,
    execute: bool,
) -> list[str]:
    """Build per-replication, per-threshold consensus GeoJSONs for one condition.

    Args:
        study_dir: Detections root (e.g. outputs/retest/phase3c/track2-text).
        condition: H9 condition label (A, B, C, D, E).
        sub_conditions: The 5 sub-condition (pass-variant) directory names.
        n_replications: Number of replications (run_k pools); 5 for phase3c.
        out_dir: Track output root (<out>/<track>).
        execute: When False, only report; build nothing.

    Returns:
        List of human-readable status lines.
    """
    msgs: list[str] = []
    total_passes = len(sub_conditions)
    for k in range(1, n_replications + 1):
        rep_dir = out_dir / condition / f"replication_{k}"
        if not execute:
            msgs.append(
                f"DRY-RUN  {rep_dir}/consensus_t1..t{total_passes}.geojson "
                f"(pool run_{k} of {sub_conditions})"
            )
            continue

        pass_detections = load_replication_passes(
            study_dir, sub_conditions, k
        )
        if not pass_detections:
            msgs.append(f"SKIP     {rep_dir} — no passes loaded")
            continue

        clusters = cluster_across_passes(pass_detections)
        rep_dir.mkdir(parents=True, exist_ok=True)
        for t in range(1, total_passes + 1):
            consensus_fc = apply_threshold(clusters, t, total_passes)
            consensus_fc = reproject_fc_to_storage(consensus_fc)
            out_path = rep_dir / f"consensus_t{t}.geojson"
            with open(out_path, "w") as fh:
                json.dump(consensus_fc, fh, indent=2)
        n_feat_t1 = len(
            apply_threshold(
                clusters, 1, total_passes
            ).get("features", [])
        )
        msgs.append(
            f"OK       {rep_dir}  "
            f"(t1..t{total_passes}; {n_feat_t1} detections at t1, "
            f"{len(pass_detections)} passes)"
        )
    return msgs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Materialise phase3c H9 diversity-pool consensus "
        "GeoJSONs (dry-run by default)."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually build (default dry-run). Run on zbook/sapphire.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / DEFAULT_OUT,
        help=f"Output root (default: {DEFAULT_OUT}).",
    )
    parser.add_argument(
        "--track",
        choices=sorted(TRACKS),
        help="Restrict to one track (default: both).",
    )
    args = parser.parse_args(argv)

    tracks = [args.track] if args.track else sorted(TRACKS)
    n_fail = 0
    for track in tracks:
        yaml_rel, study_rel = TRACKS[track]
        study = load_study_yaml(REPO_ROOT / yaml_rel)
        design = extract_consensus_design(study)
        n_reps = study.get("consensus_design", {}).get("replications", 5)
        study_dir = REPO_ROOT / study_rel
        out_dir = args.out / track
        print(f"\n=== {track}  (conditions: {sorted(design)}, "
              f"{n_reps} replications) ===")
        for condition in sorted(design):
            sub_conditions = design[condition]
            for msg in materialise_condition(
                study_dir, condition, sub_conditions,
                n_reps, out_dir, args.execute,
            ):
                print(f"  {msg}")
                n_fail += int(msg.startswith("SKIP"))

    if not args.execute:
        print("\nDRY-RUN — nothing built. Re-run with --execute (on zbook).")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
