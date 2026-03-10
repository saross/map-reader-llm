#!/usr/bin/env python3
"""
Cross-Modal Union Proposer + Adversarial Verifier Experiment
=============================================================

Chains four stages using existing infrastructure to test whether the
union of image and text-only proposer tracks, followed by adversarial
verification, achieves higher F1 than either single-track pipeline.

Stages:
    1. Build union candidates — spatially deduplicate image + text detections
    2. Extract crops — crop tiles around union candidate centroids
    3. Run adversarial verifier — API calls to classify each candidate
    4. Evaluate and report — threshold sweep, provenance breakdown

Motivation:
    Phase 3d pilot extended analyses (Session 44) showed cross-modal
    complementarity: union recall = 0.866 (84/97 mounds) vs 0.804 text
    or 0.732 image alone. False positives are largely independent (only
    20/62 co-occur). This experiment tests whether union + adversarial
    verification achieves higher F1 than single-track pipelines.

Usage:
    uv run python scripts/run_union_experiment.py
    uv run python scripts/run_union_experiment.py --dry-run
    uv run python scripts/run_union_experiment.py --skip-verify
    uv run python scripts/run_union_experiment.py --include-examples

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

# Proposer data — reuse Phase 2d optimal config, run 1 (same as pilot)
PROPOSER_PATHS = {
    "track1-image": (
        REPO_ROOT / "outputs" / "phase2d" / "track1-image" / "minimal"
        / "run_1" / "detections_plus-hp_run01"
    ),
    "track2-text": (
        REPO_ROOT / "outputs" / "phase2d" / "track2-text" / "minimal"
        / "run_1" / "detections_T0.0_run01"
    ),
}

# Ground truth
REFERENCES_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "references"
    / "mounds-reference.geojson"
)
BOUNDS_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "bounds"
    / "validation_bounds.geojson"
)

# Tiles for crop extraction
TILES_DIR = REPO_ROOT / "inputs" / "tiles"

# Output paths
OUTPUT_DIR = REPO_ROOT / "outputs" / "phase3d-union"
RESULTS_DIR = REPO_ROOT / "results"

# Verifier configuration — matches pilot settings
VERIFIER_INSTRUCTION = "verify_adversarial.md"
INSTRUCTIONS_DIR = REPO_ROOT / "prompts" / "system-instructions"

# Evaluation
MATCH_BUFFER_M = 20.0
THRESHOLD_STEPS = 101  # 0.00 to 1.00 in 0.01 increments

# Single-track baselines (from Phase 3d pilot, adversarial verifier)
SINGLE_TRACK_BASELINES = {
    "track1-image": {
        "unfiltered": {"f1": 0.620, "precision": 0.538, "recall": 0.732,
                       "n": 132},
        "adversarial": {"f1": 0.711, "precision": 0.711, "recall": 0.711,
                        "n": 97, "threshold": 0.21},
    },
    "track2-text": {
        "unfiltered": {"f1": 0.658, "precision": 0.557, "recall": 0.804,
                       "n": 140},
        "adversarial": {"f1": 0.796, "precision": 0.809, "recall": 0.784,
                        "n": 94, "threshold": 0.16},
    },
}


# ---------------------------------------------------------------------------
# Stage 1: Build union candidates
# ---------------------------------------------------------------------------

def build_union_features(
    clusters: list[list[dict]],
) -> list[dict]:
    """
    Convert cluster list to GeoJSON features with provenance tracking.

    Each feature records which tracks contributed to the cluster, enabling
    per-provenance evaluation in Stage 4.

    Args:
        clusters: Output from cluster_detections() — list of clusters,
            each cluster a list of detection dicts with 'run_id',
            'geom_bounds', 'source_tile', and 'original' keys.

    Returns:
        List of GeoJSON Feature dicts with source_tracks, proposer_votes,
        cluster_size, and averaged geometry.
    """
    features = []
    for cluster in clusters:
        # Track provenance
        source_tracks = sorted(set(c["run_id"] for c in cluster))
        proposer_votes = len(source_tracks)

        # Average geometry across cluster members (for crop extraction)
        boxes = np.array([c["box"] for c in cluster])
        avg_box = np.mean(boxes, axis=0).tolist()  # ymin, xmin, ymax, xmax

        # Convert from legacy (ymin, xmin, ymax, xmax) to geom order
        minx = avg_box[1]
        miny = avg_box[0]
        maxx = avg_box[3]
        maxy = avg_box[2]

        # Store original member centroids for evaluation (avoids
        # recall loss from centroid averaging — see design note below)
        member_centroids = []
        for det in cluster:
            gb = det["geom_bounds"]  # (minx, miny, maxx, maxy)
            cx = (gb[0] + gb[2]) / 2
            cy = (gb[1] + gb[3]) / 2
            member_centroids.append([cx, cy])

        feat = {
            "type": "Feature",
            "properties": {
                "source_tile": cluster[0]["source_tile"],
                "source_tracks": source_tracks,
                "proposer_votes": proposer_votes,
                "cluster_size": len(cluster),
                "member_centroids": member_centroids,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [minx, miny],
                    [maxx, miny],
                    [maxx, maxy],
                    [minx, maxy],
                    [minx, miny],
                ]],
            },
        }
        features.append(feat)

    return features


def stage_build_union() -> Path:
    """
    Stage 1: Load both proposer GeoJSONs, cluster, and write union.

    Always writes the union GeoJSON — this is local I/O only, no API
    calls. The --dry-run flag only skips Stage 3 (verifier API calls).

    Returns:
        Path to the union GeoJSON file.
    """
    # Import clustering function from existing script
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from generate_union_candidates import cluster_detections
    from run_h2_pilot import load_geojson

    print("\n" + "=" * 70)
    print("STAGE 1: Build union candidates")
    print("=" * 70)

    # Load both proposer outputs
    all_detections: dict[str, list[dict]] = {}
    total_features = 0
    for track_id, path in PROPOSER_PATHS.items():
        if not path.exists():
            print(f"  ERROR: Missing proposer file: {path}")
            sys.exit(1)
        data = load_geojson(path)
        feats = data.get("features", [])
        all_detections[track_id] = feats
        total_features += len(feats)
        print(f"  Loaded {len(feats)} features from {track_id}")

    # Cluster across tracks (20 m, same-tile constraint)
    clusters = cluster_detections(all_detections)
    print(
        f"  Clustered {total_features} detections → "
        f"{len(clusters)} unique candidates"
    )

    # Build union features with provenance
    union_features = build_union_features(clusters)

    # Count provenance categories
    image_only = sum(
        1 for f in union_features
        if f["properties"]["source_tracks"] == ["track1-image"]
    )
    text_only = sum(
        1 for f in union_features
        if f["properties"]["source_tracks"] == ["track2-text"]
    )
    both = sum(
        1 for f in union_features
        if len(f["properties"]["source_tracks"]) == 2
    )
    print(f"  Provenance: {image_only} image-only, {text_only} text-only, "
          f"{both} both tracks")

    # Write union GeoJSON (always — local I/O only)
    output_path = OUTPUT_DIR / "union_detections.geojson"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fc = {"type": "FeatureCollection", "features": union_features}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fc, f, indent=2)
    print(f"  Saved to {output_path}")

    return output_path


# ---------------------------------------------------------------------------
# Stage 2: Extract crops
# ---------------------------------------------------------------------------

def stage_extract_crops(union_geojson: Path) -> Path | None:
    """
    Stage 2: Extract candidate crops from union GeoJSON.

    Always runs — this is local I/O only (reads tiles, writes crops).
    The --dry-run flag only skips Stage 3 (verifier API calls).

    Returns:
        Path to candidate_manifest.json, or None on failure.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from extract_candidates import extract_candidates

    print("\n" + "=" * 70)
    print("STAGE 2: Extract candidate crops")
    print("=" * 70)

    candidates_dir = OUTPUT_DIR / "candidates"
    manifest_path = extract_candidates(
        proposer_geojson=union_geojson,
        tiles_dir=TILES_DIR,
        output_dir=candidates_dir,
    )

    if manifest_path:
        print(f"  Manifest: {manifest_path}")
    else:
        print("  ERROR: Crop extraction failed")

    return manifest_path


# ---------------------------------------------------------------------------
# Stage 3: Run adversarial verifier
# ---------------------------------------------------------------------------

def stage_run_verifier(
    manifest_path: Path,
    include_examples: bool = False,
    dry_run: bool = False,
) -> Path:
    """
    Stage 3: Run adversarial verifier on all union candidates.

    Args:
        manifest_path: Path to candidate_manifest.json from Stage 2.
        include_examples: Whether to include visual reference examples.
            Default False (text-only mode, which outperformed in pilot).
        dry_run: If True, skip API calls.

    Returns:
        Path to the probability output JSON file.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from run_h2_pilot import call_verifier, resolve_model_name

    print("\n" + "=" * 70)
    print("STAGE 3: Run adversarial verifier")
    print("=" * 70)

    # Load manifest
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    candidates = manifest["candidates"]
    n_candidates = len(candidates)
    crops_dir = manifest_path.parent / "crops"
    print(f"  Candidates: {n_candidates}")
    print(f"  Mode: {'image+text' if include_examples else 'text-only'}")

    # Load verifier instruction
    instruction_path = INSTRUCTIONS_DIR / VERIFIER_INSTRUCTION
    instruction_text = instruction_path.read_text(encoding="utf-8")
    print(f"  Instruction: {VERIFIER_INSTRUCTION}")

    output_path = (
        OUTPUT_DIR / "verifier_adversarial_probabilities.json"
    )

    if dry_run:
        print(f"  [DRY RUN] Would call verifier on {n_candidates} "
              f"candidates")
        print(f"  [DRY RUN] Would save to {output_path}")
        return output_path

    # Load .env if available (matches pilot pattern)
    import os
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            pass

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("  ERROR: GOOGLE_API_KEY not set (check .env or environment)")
        sys.exit(1)

    from google import genai
    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": "v1alpha"},
    )
    model_name = resolve_model_name(client, "gemini-3-flash")
    print(f"  Model: {model_name}")

    # Call verifier on each candidate (keys are string candidate IDs)
    probabilities: dict[str, float | None] = {}
    start_time = time.time()

    for i, candidate in enumerate(candidates):
        cid = str(candidate["candidate_id"])
        crop_file = candidate["crop_file"]
        crop_path = crops_dir.parent / crop_file

        if not crop_path.exists():
            print(f"  [{i + 1}/{n_candidates}] MISSING: {crop_file}")
            probabilities[cid] = None
            continue

        result = call_verifier(
            client=client,
            model_name=model_name,
            instruction_text=instruction_text,
            crop_path=crop_path,
            include_examples=include_examples,
        )

        if result and "mound_probability" in result:
            prob = float(result["mound_probability"])
            probabilities[cid] = prob
            status = f"p={prob:.2f}"
        else:
            probabilities[cid] = None
            status = "FAILED"

        # Progress update every 20 candidates
        if (i + 1) % 20 == 0 or (i + 1) == n_candidates:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(
                f"  [{i + 1}/{n_candidates}] {status} "
                f"({rate:.1f} candidates/s)"
            )

    # Save probabilities
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(probabilities, f, indent=2)

    n_success = sum(1 for v in probabilities.values() if v is not None)
    n_failed = n_candidates - n_success
    elapsed = time.time() - start_time
    print(f"  Completed: {n_success} success, {n_failed} failed "
          f"({elapsed:.1f}s)")
    print(f"  Saved to {output_path}")

    return output_path


# ---------------------------------------------------------------------------
# Stage 4: Evaluate and report
# ---------------------------------------------------------------------------

def get_provenance_category(
    source_tracks: list[str],
) -> str:
    """Classify a candidate's provenance from its source_tracks list."""
    has_image = "track1-image" in source_tracks
    has_text = "track2-text" in source_tracks
    if has_image and has_text:
        return "both"
    elif has_image:
        return "image-only"
    elif has_text:
        return "text-only"
    return "unknown"


def evaluate_cluster_level(
    member_coords: list[tuple[float, float]],
    member_to_cluster: list[int],
    ref_coords: list[tuple[float, float]],
    buffer_m: float,
) -> dict:
    """
    Cluster-level evaluation with member-level matching.

    Uses all original member coordinates for greedy spatial matching
    (preserving recall), then maps matched detections back to their
    parent clusters for precision counting (avoiding duplicate
    penalisation from multi-member clusters).

    Args:
        member_coords: All member coordinates across passing clusters.
        member_to_cluster: Maps each member index to its cluster index.
        ref_coords: Ground-truth reference coordinates.
        buffer_m: Maximum matching distance in metres.

    Returns:
        Dict with tp, fp, fn, precision, recall, f1, n_clusters.
    """
    import math as _math

    if not member_coords and not ref_coords:
        return {"tp": 0, "fp": 0, "fn": 0,
                "precision": 0.0, "recall": 0.0, "f1": 0.0,
                "n_clusters": 0}
    if not member_coords:
        return {"tp": 0, "fp": 0, "fn": len(ref_coords),
                "precision": 0.0, "recall": 0.0, "f1": 0.0,
                "n_clusters": 0}

    # All pairwise distances (member-level)
    pairs = []
    for d_idx, det in enumerate(member_coords):
        for r_idx, ref in enumerate(ref_coords):
            dist = _math.sqrt(
                (det[0] - ref[0]) ** 2 + (det[1] - ref[1]) ** 2
            )
            pairs.append((dist, d_idx, r_idx))
    pairs.sort()

    # Greedy assignment at member level
    matched_d: set[int] = set()
    matched_r: set[int] = set()
    for dist, d_idx, r_idx in pairs:
        if dist > buffer_m:
            break
        if d_idx in matched_d or r_idx in matched_r:
            continue
        matched_d.add(d_idx)
        matched_r.add(r_idx)

    # Map matched members to clusters
    matched_clusters = set(
        member_to_cluster[di] for di in matched_d
    )
    all_clusters = set(member_to_cluster)

    tp = len(matched_clusters)
    fp = len(all_clusters) - tp
    fn = len(ref_coords) - len(matched_r)
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": p, "recall": r, "f1": f1,
        "n_clusters": len(all_clusters),
    }


def evaluate_union(
    manifest: dict,
    probabilities: dict[str, float | None],
    union_geojson: dict,
    ref_coords: list[tuple[float, float]],
    thresholds: list[float],
) -> dict:
    """
    Threshold sweep with cluster-level evaluation and provenance
    breakdown.

    Uses member-level coordinates for spatial matching (preserving
    recall that would be lost to centroid averaging) and cluster-level
    counting for precision (avoiding duplicate penalisation from
    multi-member clusters).

    Args:
        manifest: Candidate manifest (from extract_candidates).
        probabilities: Map of candidate_id → mound_probability.
        union_geojson: Union GeoJSON FeatureCollection with provenance.
        ref_coords: Ground-truth reference coordinates.
        thresholds: List of probability thresholds to sweep.

    Returns:
        Dict with threshold_results, optimal_threshold, provenance
        breakdown, and unfiltered baseline.
    """
    candidates = manifest["candidates"]
    union_features = union_geojson.get("features", [])

    # Build member coordinate list with cluster mapping and provenance
    all_member_coords: list[tuple[float, float]] = []
    all_member_to_cluster: list[int] = []
    candidate_provenance: list[str] = []

    for ci, candidate in enumerate(candidates):
        idx = candidate["candidate_id"]
        if isinstance(idx, str):
            idx = int(idx.replace("candidate_", "")) - 1

        # Get provenance and member centroids
        if idx < len(union_features):
            props = union_features[idx]["properties"]
            tracks = props.get("source_tracks", [])
            prov = get_provenance_category(tracks)
            member_centroids = props.get("member_centroids", [])
        else:
            prov = "unknown"
            member_centroids = []

        candidate_provenance.append(prov)

        if member_centroids:
            for mc in member_centroids:
                all_member_coords.append((mc[0], mc[1]))
                all_member_to_cluster.append(ci)
        else:
            x = candidate["centroid_x"]
            y = candidate["centroid_y"]
            all_member_coords.append((x, y))
            all_member_to_cluster.append(ci)

    # Unfiltered baseline (all clusters)
    unfiltered = evaluate_cluster_level(
        all_member_coords, all_member_to_cluster,
        ref_coords, MATCH_BUFFER_M,
    )
    unfiltered["n"] = len(candidates)

    # Threshold sweep
    threshold_results = []
    best_f1 = 0.0
    best_threshold = 0.0
    best_result = None

    for threshold in thresholds:
        # Build member pool for passing clusters
        kept_members: list[tuple[float, float]] = []
        kept_member_to_cluster: list[int] = []
        passing_clusters: set[int] = set()

        for mi, coord in enumerate(all_member_coords):
            ci = all_member_to_cluster[mi]
            cid = str(candidates[ci]["candidate_id"])
            prob = probabilities.get(cid)
            if prob is not None and prob >= threshold:
                kept_members.append(coord)
                kept_member_to_cluster.append(ci)
                passing_clusters.add(ci)

        metrics = evaluate_cluster_level(
            kept_members, kept_member_to_cluster,
            ref_coords, MATCH_BUFFER_M,
        )
        metrics["threshold"] = threshold
        metrics["n_kept"] = len(passing_clusters)
        threshold_results.append(metrics)

        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            best_threshold = threshold
            best_result = metrics.copy()

    # Provenance breakdown at optimal threshold
    provenance_breakdown = {}
    if best_result:
        for category in ["image-only", "text-only", "both"]:
            cat_members: list[tuple[float, float]] = []
            cat_member_to_cluster: list[int] = []

            for mi, coord in enumerate(all_member_coords):
                ci = all_member_to_cluster[mi]
                cid = str(candidates[ci]["candidate_id"])
                prob = probabilities.get(cid)
                if (prob is not None
                        and prob >= best_threshold
                        and candidate_provenance[ci] == category):
                    cat_members.append(coord)
                    cat_member_to_cluster.append(ci)

            cat_metrics = evaluate_cluster_level(
                cat_members, cat_member_to_cluster,
                ref_coords, MATCH_BUFFER_M,
            )
            cat_metrics["n"] = len(set(cat_member_to_cluster))
            provenance_breakdown[category] = cat_metrics

    return {
        "unfiltered": unfiltered,
        "threshold_results": threshold_results,
        "optimal_threshold": best_threshold,
        "optimal_result": best_result,
        "provenance_breakdown": provenance_breakdown,
        "n_candidates": len(candidates),
        "n_references": len(ref_coords),
    }


def generate_report(results: dict) -> str:
    """
    Generate a Markdown report from evaluation results.

    Args:
        results: Output from evaluate_union().

    Returns:
        Markdown report string.
    """
    opt = results.get("optimal_result") or {}
    unf = results.get("unfiltered") or {}
    prov = results.get("provenance_breakdown") or {}

    lines = [
        "# Phase 3d — Cross-Modal Union Experiment Results",
        "",
        "## Metadata",
        "",
        f"- **Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "- **Script**: `scripts/run_union_experiment.py`",
        "- **Matching method**: Greedy nearest-neighbour, "
        f"{MATCH_BUFFER_M} m buffer",
        "- **Verifier**: Adversarial (text-only mode)",
        f"- **Candidates**: {results.get('n_candidates', '?')} "
        f"(from union of image + text proposers)",
        f"- **Ground truth**: {results.get('n_references', '?')} mounds",
        "",
        "## Comparison Table",
        "",
        "| Pipeline | F1 | Precision | Recall | N | Threshold |",
        "|----------|---:|----------:|-------:|--:|----------:|",
    ]

    # Single-track baselines
    for track_id, label in [
        ("track1-image", "Image single-track (adversarial)"),
        ("track2-text", "Text single-track (adversarial)"),
    ]:
        b = SINGLE_TRACK_BASELINES[track_id]["adversarial"]
        lines.append(
            f"| {label} | {b['f1']:.3f} | {b['precision']:.3f} "
            f"| {b['recall']:.3f} | {b['n']} | {b['threshold']} |"
        )

    # Union unfiltered
    lines.append(
        f"| Union unfiltered | {unf.get('f1', 0):.3f} "
        f"| {unf.get('precision', 0):.3f} | {unf.get('recall', 0):.3f} "
        f"| {unf.get('n', '?')} | — |"
    )

    # Union + adversarial
    lines.append(
        f"| **Union + adversarial** | **{opt.get('f1', 0):.3f}** "
        f"| {opt.get('precision', 0):.3f} | {opt.get('recall', 0):.3f} "
        f"| {opt.get('n_kept', '?')} "
        f"| {results.get('optimal_threshold', '?')} |"
    )

    # Provenance breakdown
    lines.extend([
        "",
        "## Provenance Breakdown (at Optimal Threshold)",
        "",
        "| Source | N | TP | FP | Precision | Recall |",
        "|--------|--:|---:|---:|----------:|-------:|",
    ])
    for category in ["image-only", "text-only", "both"]:
        m = prov.get(category, {})
        lines.append(
            f"| {category} | {m.get('n', 0)} | {m.get('tp', 0)} "
            f"| {m.get('fp', 0)} | {m.get('precision', 0):.3f} "
            f"| {m.get('recall', 0):.3f} |"
        )

    # Threshold sweep summary
    lines.extend([
        "",
        "## Threshold Sweep",
        "",
        "| Threshold | F1 | Precision | Recall | N kept |",
        "|----------:|---:|----------:|-------:|-------:|",
    ])
    for tr in results.get("threshold_results", []):
        # Show every 0.05 step plus the optimal
        t = tr["threshold"]
        is_round = abs(t * 20 - round(t * 20)) < 0.001
        is_optimal = abs(t - results.get("optimal_threshold", -1)) < 0.001
        if is_round or is_optimal:
            marker = " *" if is_optimal else ""
            lines.append(
                f"| {t:.2f}{marker} | {tr['f1']:.3f} "
                f"| {tr['precision']:.3f} | {tr['recall']:.3f} "
                f"| {tr['n_kept']} |"
            )

    lines.append("")
    return "\n".join(lines)


def stage_evaluate(
    manifest_path: Path,
    probs_path: Path,
    union_geojson_path: Path,
) -> dict:
    """
    Stage 4: Evaluate union + verifier against ground truth.

    Returns:
        Evaluation results dict.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from run_h2_pilot import (
        get_references_in_bounds,
        load_geojson,
    )

    print("\n" + "=" * 70)
    print("STAGE 4: Evaluate and report")
    print("=" * 70)

    # Load inputs
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    probabilities: dict[str, float | None] = {}
    if probs_path.exists():
        with open(probs_path, encoding="utf-8") as f:
            probabilities = json.load(f)
    else:
        print("  No probability file — evaluating unfiltered only")

    union_geojson = load_geojson(union_geojson_path)

    # Load ground truth
    refs_data = load_geojson(REFERENCES_PATH)
    bounds_data = load_geojson(BOUNDS_PATH)

    # Get tile names from union candidates
    source_tiles = set()
    for feat in union_geojson.get("features", []):
        tile = feat.get("properties", {}).get("source_tile", "")
        if tile:
            source_tiles.add(tile)

    ref_coords = get_references_in_bounds(
        refs_data["features"], bounds_data["features"], source_tiles
    )
    print(f"  Reference mounds: {ref_coords.__len__()}")
    print(f"  Candidates: {len(manifest['candidates'])}")

    # Generate thresholds (0.00 to 1.00 in 0.01 steps)
    thresholds = [i / 100 for i in range(THRESHOLD_STEPS)]

    # Evaluate
    results = evaluate_union(
        manifest=manifest,
        probabilities=probabilities,
        union_geojson=union_geojson,
        ref_coords=ref_coords,
        thresholds=thresholds,
    )

    # Print summary
    opt = results.get("optimal_result", {})
    unf = results.get("unfiltered", {})
    print(f"\n  Unfiltered: F1={unf.get('f1', 0):.3f} "
          f"(P={unf.get('precision', 0):.3f}, "
          f"R={unf.get('recall', 0):.3f}, N={unf.get('n', '?')})")
    if opt:
        print(f"  Optimal:   F1={opt.get('f1', 0):.3f} "
              f"(P={opt.get('precision', 0):.3f}, "
              f"R={opt.get('recall', 0):.3f}, "
              f"N={opt.get('n_kept', '?')}, "
              f"t={results.get('optimal_threshold', '?')})")

    # Compare to baselines
    best_single = SINGLE_TRACK_BASELINES["track2-text"]["adversarial"]
    if opt:
        delta = opt.get("f1", 0) - best_single["f1"]
        print(f"  vs best single-track: "
              f"ΔF1 = {delta:+.3f}")

    # Save results (always — local I/O only)
    results_path = OUTPUT_DIR / "union_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved results to {results_path}")

    # Generate and save report
    report = generate_report(results)
    report_path = RESULTS_DIR / "phase3d-union-results.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Saved report to {report_path}")

    return results


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the cross-modal union experiment."""
    parser = argparse.ArgumentParser(
        description=(
            "Cross-modal union proposer + adversarial verifier experiment"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full run (builds union, extracts crops, runs verifier, evaluates)
    uv run python scripts/run_union_experiment.py

    # Dry run (validates paths, builds union, skips API calls)
    uv run python scripts/run_union_experiment.py --dry-run

    # Skip verification (stages 1-2 + evaluate unfiltered only)
    uv run python scripts/run_union_experiment.py --skip-verify

    # Use image+text verifier mode (default is text-only)
    uv run python scripts/run_union_experiment.py --include-examples
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and build union without API calls",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip verifier stage; evaluate unfiltered union only",
    )
    parser.add_argument(
        "--include-examples",
        action="store_true",
        help=(
            "Include visual reference examples in verifier calls "
            "(default: text-only mode)"
        ),
    )
    args = parser.parse_args()

    print("Cross-Modal Union Proposer + Adversarial Verifier Experiment")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")

    # Stage 1: Build union candidates (always runs — local I/O only)
    union_geojson_path = stage_build_union()

    # Stage 2: Extract crops (always runs — local I/O only)
    manifest_path = stage_extract_crops(union_geojson_path)
    if manifest_path is None:
        print("\nERROR: Crop extraction failed. Aborting.")
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Stages 1-2 complete. Skipping stages 3-4.")
        return

    # Stage 3: Run adversarial verifier (unless --skip-verify)
    probs_path = OUTPUT_DIR / "verifier_adversarial_probabilities.json"
    if not args.skip_verify:
        probs_path = stage_run_verifier(
            manifest_path=manifest_path,
            include_examples=args.include_examples,
        )
    else:
        print("\n[SKIP] Stage 3 skipped (--skip-verify)")

    # Stage 4: Evaluate and report
    stage_evaluate(
        manifest_path=manifest_path,
        probs_path=probs_path,
        union_geojson_path=union_geojson_path,
    )

    print(f"\nCompleted: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
