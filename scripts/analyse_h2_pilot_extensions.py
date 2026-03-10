#!/usr/bin/env python3
"""
Phase 3d Pilot — Extended Analyses
====================================

Three "free" analyses (zero API calls) on existing Phase 3d pilot data:

1. **Precision-Recall curves**: Fine-grained threshold sweep (0.01 steps)
   for each verifier strategy × track combination.
2. **Cross-modal overlap**: Which ground-truth mounds does each track
   (image vs text-only) discover? Produces the Venn diagram that decides
   whether cross-modal union proposer is viable.
3. **Multi-verifier ensemble**: Combines the three verifier strategies
   (standard, adversarial, checklist) via averaging, majority vote,
   and union vote to test whether ensembling improves on the best
   single verifier.

Usage:
    uv run python scripts/analyse_h2_pilot_extensions.py --analysis all
    uv run python scripts/analyse_h2_pilot_extensions.py --analysis pr-curves
    uv run python scripts/analyse_h2_pilot_extensions.py --analysis cross-modal
    uv run python scripts/analyse_h2_pilot_extensions.py --analysis ensemble

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Import evaluation functions from the pilot script to ensure
# consistency with the original pilot analysis methodology.
from run_h2_pilot import (  # noqa: E402
    BOUNDS_PATH,
    MATCH_BUFFER_M,
    REFERENCES_PATH,
    evaluate_detections,
    get_references_in_bounds,
    load_geojson,
)

# Pilot output paths
PILOT_DIR = REPO_ROOT / "outputs" / "phase3d-pilot"
RESULTS_DIR = REPO_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

TRACKS = ["track1-image", "track2-text"]
TRACK_LABELS = {"track1-image": "Image", "track2-text": "Text-only"}
VERIFIER_VARIANTS = ["standard", "adversarial", "checklist"]

# Threshold sweep: 0.00 to 1.00 in 0.01 steps (101 points)
THRESHOLDS = [round(t / 100, 2) for t in range(101)]


# ---------------------------------------------------------------------------
# Shared data loading
# ---------------------------------------------------------------------------

def load_candidate_manifest(track: str) -> list[dict]:
    """
    Load candidate manifest for a given track.

    Returns:
        List of candidate dicts, each with keys: candidate_id,
        centroid_x, centroid_y, source_tile, crop_file, properties.
    """
    manifest_path = (
        PILOT_DIR / track / "candidates" / "candidate_manifest.json"
    )
    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)
    return data["candidates"]


def load_probabilities(track: str, variant: str) -> dict[str, float]:
    """
    Load verifier probability file for a given track and variant.

    Returns:
        Dict mapping string candidate_id to mound_probability float.
    """
    prob_path = (
        PILOT_DIR / track / f"verifier_{variant}_probabilities.json"
    )
    with open(prob_path, encoding="utf-8") as f:
        data = json.load(f)
    return data["probabilities"]


def get_candidate_coords(
    candidates: list[dict],
) -> list[tuple[float, float]]:
    """Extract centroid coordinates from candidate list."""
    return [
        (c["centroid_x"], c["centroid_y"]) for c in candidates
    ]


def load_reference_coords(tile_names: set[str]) -> list[tuple[float, float]]:
    """
    Load ground-truth reference mound coordinates, scoped to the
    tiles covered by the proposer's detections.

    Args:
        tile_names: Set of tile filenames from the candidate manifest.

    Returns:
        List of (easting, northing) reference coordinates within
        the specified tile bounds.
    """
    refs_data = load_geojson(REFERENCES_PATH)
    bounds_data = load_geojson(BOUNDS_PATH)
    return get_references_in_bounds(
        refs_data["features"], bounds_data["features"], tile_names
    )


def load_pilot_data() -> dict:
    """
    Load all pilot data: candidate manifests, probabilities, and
    ground truth for both tracks.

    Returns:
        Dict with structure:
        {
            "tracks": {
                "track1-image": {
                    "candidates": [...],
                    "coords": [(x, y), ...],
                    "tile_names": {"tile1.png", ...},
                    "ref_coords": [(x, y), ...],
                    "probabilities": {
                        "standard": {"0": 0.95, ...},
                        "adversarial": {...},
                        "checklist": {...},
                    },
                },
                "track2-text": { ... },
            }
        }
    """
    pilot_data: dict = {"tracks": {}}

    for track in TRACKS:
        candidates = load_candidate_manifest(track)
        coords = get_candidate_coords(candidates)
        tile_names = {c["source_tile"] for c in candidates}
        ref_coords = load_reference_coords(tile_names)

        probs = {}
        for variant in VERIFIER_VARIANTS:
            probs[variant] = load_probabilities(track, variant)

        pilot_data["tracks"][track] = {
            "candidates": candidates,
            "coords": coords,
            "tile_names": tile_names,
            "ref_coords": ref_coords,
            "probabilities": probs,
        }

    return pilot_data


# ---------------------------------------------------------------------------
# Detailed evaluation (extends greedy matcher with pair tracking)
# ---------------------------------------------------------------------------

def evaluate_detections_detailed(
    det_coords: list[tuple[float, float]],
    ref_coords: list[tuple[float, float]],
    buffer_m: float,
) -> dict:
    """
    Evaluate detections against references using greedy nearest-neighbour.

    Same algorithm as evaluate_detections() in run_h2_pilot.py, but also
    returns the matched pairs for per-mound analysis.

    Args:
        det_coords: List of detection (easting, northing) tuples.
        ref_coords: List of reference (easting, northing) tuples.
        buffer_m: Maximum matching distance in metres.

    Returns:
        Dict with:
            tp, fp, fn: int counts
            precision, recall, f1: float metrics
            matched_pairs: list of (det_idx, ref_idx) tuples
            matched_det_indices: set of matched detection indices
            matched_ref_indices: set of matched reference indices
    """
    if not det_coords and not ref_coords:
        return {
            "tp": 0, "fp": 0, "fn": 0,
            "precision": 0.0, "recall": 0.0, "f1": 0.0,
            "matched_pairs": [],
            "matched_det_indices": set(),
            "matched_ref_indices": set(),
        }
    if not det_coords:
        return {
            "tp": 0, "fp": 0, "fn": len(ref_coords),
            "precision": 0.0, "recall": 0.0, "f1": 0.0,
            "matched_pairs": [],
            "matched_det_indices": set(),
            "matched_ref_indices": set(),
        }
    if not ref_coords:
        return {
            "tp": 0, "fp": len(det_coords), "fn": 0,
            "precision": 0.0, "recall": 0.0, "f1": 0.0,
            "matched_pairs": [],
            "matched_det_indices": set(),
            "matched_ref_indices": set(),
        }

    # Compute all pairwise distances, identical to run_h2_pilot.py
    pairs = []
    for d_idx, det in enumerate(det_coords):
        for r_idx, ref in enumerate(ref_coords):
            dist = math.sqrt(
                (det[0] - ref[0]) ** 2 + (det[1] - ref[1]) ** 2
            )
            pairs.append((dist, d_idx, r_idx))
    pairs.sort()

    # Greedy assignment — closest pairs matched first
    matched_d: set[int] = set()
    matched_r: set[int] = set()
    matched_pairs: list[tuple[int, int]] = []
    for dist, d_idx, r_idx in pairs:
        if dist > buffer_m:
            break
        if d_idx in matched_d or r_idx in matched_r:
            continue
        matched_d.add(d_idx)
        matched_r.add(r_idx)
        matched_pairs.append((d_idx, r_idx))

    tp = len(matched_d)
    fp = len(det_coords) - tp
    fn = len(ref_coords) - len(matched_r)
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": p, "recall": r, "f1": f1,
        "matched_pairs": matched_pairs,
        "matched_det_indices": matched_d,
        "matched_ref_indices": matched_r,
    }


# ---------------------------------------------------------------------------
# Analysis 1: Precision-Recall Curves
# ---------------------------------------------------------------------------

def filter_candidates_by_threshold(
    coords: list[tuple[float, float]],
    probabilities: dict[str, float],
    threshold: float,
) -> list[tuple[float, float]]:
    """
    Return coordinates of candidates with probability >= threshold.

    Args:
        coords: Full list of candidate coordinates (indexed by position).
        probabilities: Dict mapping string candidate_id to probability.
        threshold: Minimum probability to retain.

    Returns:
        List of (easting, northing) tuples for surviving candidates.
    """
    filtered = []
    for idx, coord in enumerate(coords):
        prob = probabilities.get(str(idx), 0.0)
        if prob >= threshold:
            filtered.append(coord)
    return filtered


def compute_pr_sweep(
    coords: list[tuple[float, float]],
    ref_coords: list[tuple[float, float]],
    probabilities: dict[str, float],
    thresholds: list[float],
) -> list[dict]:
    """
    Sweep probability thresholds and compute P/R/F1 at each point.

    Returns:
        List of dicts with: threshold, n_kept, tp, fp, fn,
        precision, recall, f1.
    """
    results = []
    for threshold in thresholds:
        filtered = filter_candidates_by_threshold(
            coords, probabilities, threshold
        )
        metrics = evaluate_detections(filtered, ref_coords, MATCH_BUFFER_M)
        results.append({
            "threshold": threshold,
            "n_kept": len(filtered),
            **metrics,
        })
    return results


def compute_auc_pr(sweep_data: list[dict]) -> float:
    """
    Compute Area Under Precision-Recall curve using the trapezoidal
    rule, with points sorted by recall ascending.

    Args:
        sweep_data: List of dicts from compute_pr_sweep().

    Returns:
        AUC-PR value (float between 0 and 1).
    """
    # Extract (recall, precision) pairs, sort by recall ascending
    points = [
        (row["recall"], row["precision"])
        for row in sweep_data
        if row["n_kept"] > 0  # Skip threshold=1.0 if no candidates kept
    ]
    if not points:
        return 0.0

    # Sort by recall ascending; break ties by precision descending
    # to get the upper envelope (interpolated precision)
    points.sort(key=lambda p: (p[0], -p[1]))

    # Remove duplicate recall values, keeping highest precision
    deduped = []
    for recall, precision in points:
        if deduped and deduped[-1][0] == recall:
            deduped[-1] = (recall, max(deduped[-1][1], precision))
        else:
            deduped.append((recall, precision))

    if len(deduped) < 2:
        return 0.0

    # Trapezoidal integration
    auc = 0.0
    for i in range(1, len(deduped)):
        dr = deduped[i][0] - deduped[i - 1][0]
        avg_p = (deduped[i][1] + deduped[i - 1][1]) / 2
        auc += dr * avg_p

    return auc


def find_optimal_f1(sweep_data: list[dict]) -> dict:
    """Find the threshold that maximises F1."""
    best = max(sweep_data, key=lambda row: row["f1"])
    return best


def analyse_pr_curves(pilot_data: dict) -> dict:
    """
    Run Analysis 1: Precision-Recall curves for all track × verifier
    combinations.

    Returns:
        Dict with per-(track, variant) sweep data, AUC-PR, and
        optimal operating points.
    """
    print("\n=== Analysis 1: Precision-Recall Curves ===")
    results: dict = {}

    for track in TRACKS:
        td = pilot_data["tracks"][track]
        results[track] = {}

        # Baseline (unfiltered proposer)
        baseline = evaluate_detections(
            td["coords"], td["ref_coords"], MATCH_BUFFER_M
        )
        results[track]["baseline"] = baseline
        print(
            f"\n  {TRACK_LABELS[track]} baseline: "
            f"P={baseline['precision']:.3f}  "
            f"R={baseline['recall']:.3f}  "
            f"F1={baseline['f1']:.3f}  "
            f"(n={len(td['coords'])})"
        )

        for variant in VERIFIER_VARIANTS:
            sweep = compute_pr_sweep(
                td["coords"], td["ref_coords"],
                td["probabilities"][variant], THRESHOLDS,
            )
            auc = compute_auc_pr(sweep)
            optimal = find_optimal_f1(sweep)

            results[track][variant] = {
                "sweep": sweep,
                "auc_pr": auc,
                "optimal": optimal,
            }
            print(
                f"  {variant:12s}: AUC-PR={auc:.3f}  "
                f"optimal F1={optimal['f1']:.3f} "
                f"@ t={optimal['threshold']:.2f}  "
                f"P={optimal['precision']:.3f}  "
                f"R={optimal['recall']:.3f}  "
                f"(n={optimal['n_kept']})"
            )

    return results


def plot_pr_curves(pr_results: dict, output_path: Path) -> None:
    """
    Plot precision-recall curves: 2×1 subplots (image, text),
    3 curves per subplot (one per verifier variant), with baseline
    proposer marked and optimal F1 starred.
    """
    # Colour and style for each verifier variant
    variant_styles = {
        "standard": {"colour": "#2196F3", "label": "Standard"},
        "adversarial": {"colour": "#F44336", "label": "Adversarial"},
        "checklist": {"colour": "#4CAF50", "label": "Checklist"},
    }

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    for ax_idx, track in enumerate(TRACKS):
        ax = axes[ax_idx]
        td = pr_results[track]

        # Plot baseline proposer as a single point
        bl = td["baseline"]
        ax.plot(
            bl["recall"], bl["precision"],
            marker="D", markersize=10, color="#888888",
            label=f"Baseline (F1={bl['f1']:.3f})",
            zorder=5, linestyle="none",
        )

        for variant in VERIFIER_VARIANTS:
            style = variant_styles[variant]
            sweep = td[variant]["sweep"]
            optimal = td[variant]["optimal"]
            auc = td[variant]["auc_pr"]

            # Extract recall and precision arrays
            recalls = [row["recall"] for row in sweep if row["n_kept"] > 0]
            precisions = [
                row["precision"] for row in sweep if row["n_kept"] > 0
            ]

            ax.plot(
                recalls, precisions,
                color=style["colour"], linewidth=2,
                label=(
                    f"{style['label']} "
                    f"(AUC={auc:.3f}, F1*={optimal['f1']:.3f})"
                ),
            )

            # Star at optimal F1 point
            ax.plot(
                optimal["recall"], optimal["precision"],
                marker="*", markersize=14,
                color=style["colour"], zorder=6,
            )

        ax.set_xlabel("Recall", fontsize=12)
        if ax_idx == 0:
            ax.set_ylabel("Precision", fontsize=12)
        ax.set_title(
            f"{TRACK_LABELS[track]} Track", fontsize=14, fontweight="bold"
        )
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)
        ax.legend(fontsize=9, loc="lower left")
        ax.grid(True, alpha=0.3)
        # Diagonal reference line (P = R, i.e. F1 isocline)
        ax.plot([0, 1], [0, 1], "k--", alpha=0.15, linewidth=0.8)

    fig.suptitle(
        "Precision-Recall Curves: Verifier Probability Threshold Sweep",
        fontsize=14, fontweight="bold", y=1.01,
    )
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  P-R curves saved to: {output_path}")


def save_pr_csv(pr_results: dict, output_path: Path) -> None:
    """Save threshold sweep data as CSV for reproducibility."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(
            "track,variant,threshold,n_kept,tp,fp,fn,"
            "precision,recall,f1\n"
        )
        for track in TRACKS:
            for variant in VERIFIER_VARIANTS:
                for row in pr_results[track][variant]["sweep"]:
                    f.write(
                        f"{track},{variant},{row['threshold']:.2f},"
                        f"{row['n_kept']},{row['tp']},{row['fp']},"
                        f"{row['fn']},{row['precision']:.6f},"
                        f"{row['recall']:.6f},{row['f1']:.6f}\n"
                    )
    print(f"  Sweep CSV saved to: {output_path}")


# ---------------------------------------------------------------------------
# Analysis 2: Cross-Modal Overlap
# ---------------------------------------------------------------------------

def analyse_cross_modal_overlap(pilot_data: dict) -> dict:
    """
    Run Analysis 2: Determine which ground-truth mounds each track
    discovers and quantify overlap.

    Returns:
        Dict with overlap statistics, Venn diagram counts, FP overlap,
        and post-verification overlap.
    """
    print("\n=== Analysis 2: Cross-Modal Overlap ===")

    # Both tracks must share the same reference set for comparison.
    # Build a unified reference set from the union of both tracks'
    # tile coverage.
    t1 = pilot_data["tracks"]["track1-image"]
    t2 = pilot_data["tracks"]["track2-text"]
    all_tiles = t1["tile_names"] | t2["tile_names"]
    unified_refs = load_reference_coords(all_tiles)

    print(f"  Unified reference set: {len(unified_refs)} mounds "
          f"across {len(all_tiles)} tiles")

    # --- Pre-verification overlap (proposer candidates) ---

    eval_t1 = evaluate_detections_detailed(
        t1["coords"], unified_refs, MATCH_BUFFER_M
    )
    eval_t2 = evaluate_detections_detailed(
        t2["coords"], unified_refs, MATCH_BUFFER_M
    )

    # Sets of matched reference indices (which ground-truth mounds found)
    refs_by_image = eval_t1["matched_ref_indices"]
    refs_by_text = eval_t2["matched_ref_indices"]
    all_ref_indices = set(range(len(unified_refs)))

    found_by_both = refs_by_image & refs_by_text
    image_only = refs_by_image - refs_by_text
    text_only = refs_by_text - refs_by_image
    found_by_neither = all_ref_indices - (refs_by_image | refs_by_text)
    union_refs = refs_by_image | refs_by_text

    union_recall = len(union_refs) / len(unified_refs) if unified_refs else 0
    jaccard = (
        len(found_by_both) / len(union_refs) if union_refs else 0
    )

    pre_verif = {
        "total_refs": len(unified_refs),
        "image_tp": len(refs_by_image),
        "text_tp": len(refs_by_text),
        "found_by_both": len(found_by_both),
        "image_only": len(image_only),
        "text_only": len(text_only),
        "found_by_neither": len(found_by_neither),
        "union_count": len(union_refs),
        "union_recall": union_recall,
        "jaccard": jaccard,
        # Raw indices for downstream use
        "_image_ref_indices": sorted(refs_by_image),
        "_text_ref_indices": sorted(refs_by_text),
    }

    print("\n  Pre-verification overlap:")
    print(f"    Image TPs: {pre_verif['image_tp']}  "
          f"Text TPs: {pre_verif['text_tp']}")
    print(f"    Both: {pre_verif['found_by_both']}  "
          f"Image-only: {pre_verif['image_only']}  "
          f"Text-only: {pre_verif['text_only']}  "
          f"Neither: {pre_verif['found_by_neither']}")
    print(f"    Union recall: {union_recall:.3f}  "
          f"({pre_verif['union_count']}/{pre_verif['total_refs']})")
    print(f"    Jaccard index: {jaccard:.3f}")

    # --- FP overlap ---
    # Identify FP coordinates from each track and check spatial proximity
    fp_image_indices = (
        set(range(len(t1["coords"]))) - eval_t1["matched_det_indices"]
    )
    fp_text_indices = (
        set(range(len(t2["coords"]))) - eval_t2["matched_det_indices"]
    )
    fp_image_coords = [t1["coords"][i] for i in sorted(fp_image_indices)]
    fp_text_coords = [t2["coords"][i] for i in sorted(fp_text_indices)]

    # Count co-occurring FPs (any FP in track A within 20m of any
    # FP in track B)
    co_occurring_fp = 0
    image_fp_matched = set()
    text_fp_matched = set()
    for i, fp_i in enumerate(fp_image_coords):
        for j, fp_t in enumerate(fp_text_coords):
            dist = math.sqrt(
                (fp_i[0] - fp_t[0]) ** 2 + (fp_i[1] - fp_t[1]) ** 2
            )
            if dist <= MATCH_BUFFER_M:
                if i not in image_fp_matched and j not in text_fp_matched:
                    co_occurring_fp += 1
                    image_fp_matched.add(i)
                    text_fp_matched.add(j)

    fp_overlap = {
        "image_fps": len(fp_image_coords),
        "text_fps": len(fp_text_coords),
        "co_occurring": co_occurring_fp,
        "image_unique_fps": len(fp_image_coords) - co_occurring_fp,
        "text_unique_fps": len(fp_text_coords) - co_occurring_fp,
    }

    print("\n  False positive overlap:")
    print(f"    Image FPs: {fp_overlap['image_fps']}  "
          f"Text FPs: {fp_overlap['text_fps']}")
    print(f"    Co-occurring: {fp_overlap['co_occurring']}  "
          f"Image-unique: {fp_overlap['image_unique_fps']}  "
          f"Text-unique: {fp_overlap['text_unique_fps']}")

    # --- Post-verification overlap (adversarial filtered) ---
    # Use the adversarial verifier at its optimal threshold for
    # each track. For simplicity, use threshold=0.5 (splits the
    # bimodal distribution cleanly).
    post_verif_threshold = 0.5
    filtered_t1 = [
        t1["coords"][i]
        for i in range(len(t1["coords"]))
        if float(
            t1["probabilities"]["adversarial"].get(str(i), 0.0)
        ) >= post_verif_threshold
    ]
    filtered_t2 = [
        t2["coords"][i]
        for i in range(len(t2["coords"]))
        if float(
            t2["probabilities"]["adversarial"].get(str(i), 0.0)
        ) >= post_verif_threshold
    ]

    eval_t1_post = evaluate_detections_detailed(
        filtered_t1, unified_refs, MATCH_BUFFER_M
    )
    eval_t2_post = evaluate_detections_detailed(
        filtered_t2, unified_refs, MATCH_BUFFER_M
    )

    refs_post_image = eval_t1_post["matched_ref_indices"]
    refs_post_text = eval_t2_post["matched_ref_indices"]
    post_union = refs_post_image | refs_post_text
    post_both = refs_post_image & refs_post_text

    post_verif = {
        "threshold": post_verif_threshold,
        "image_kept": len(filtered_t1),
        "text_kept": len(filtered_t2),
        "image_tp": len(refs_post_image),
        "text_tp": len(refs_post_text),
        "found_by_both": len(post_both),
        "image_only": len(refs_post_image - refs_post_text),
        "text_only": len(refs_post_text - refs_post_image),
        "found_by_neither": len(
            all_ref_indices - post_union
        ),
        "union_count": len(post_union),
        "union_recall": (
            len(post_union) / len(unified_refs) if unified_refs else 0
        ),
        "jaccard": (
            len(post_both) / len(post_union) if post_union else 0
        ),
    }

    print(f"\n  Post-verification overlap (adversarial, t≥{post_verif_threshold}):")
    print(f"    Image: {post_verif['image_kept']} kept → "
          f"{post_verif['image_tp']} TPs  "
          f"Text: {post_verif['text_kept']} kept → "
          f"{post_verif['text_tp']} TPs")
    print(f"    Both: {post_verif['found_by_both']}  "
          f"Image-only: {post_verif['image_only']}  "
          f"Text-only: {post_verif['text_only']}  "
          f"Neither: {post_verif['found_by_neither']}")
    print(f"    Union recall: {post_verif['union_recall']:.3f}  "
          f"({post_verif['union_count']}/{pre_verif['total_refs']})")

    return {
        "pre_verification": pre_verif,
        "fp_overlap": fp_overlap,
        "post_verification": post_verif,
    }


def plot_cross_modal_venn(
    overlap_results: dict, output_path: Path,
) -> None:
    """
    Draw a simple Venn diagram showing cross-modal overlap using
    matplotlib primitives (matplotlib_venn not available).
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax_idx, (label, data) in enumerate([
        ("Pre-verification (Proposer)", overlap_results["pre_verification"]),
        ("Post-verification (Adversarial)", overlap_results["post_verification"]),
    ]):
        ax = axes[ax_idx]

        # Draw two overlapping circles
        circle_image = plt.Circle(
            (-0.2, 0), 0.55, fill=True, alpha=0.25,
            facecolor="#2196F3", edgecolor="#1565C0", linewidth=2,
        )
        circle_text = plt.Circle(
            (0.2, 0), 0.55, fill=True, alpha=0.25,
            facecolor="#F44336", edgecolor="#C62828", linewidth=2,
        )
        ax.add_patch(circle_image)
        ax.add_patch(circle_text)

        # Annotate regions
        # Image-only (left)
        ax.text(
            -0.45, 0, str(data["image_only"]),
            ha="center", va="center", fontsize=18, fontweight="bold",
        )
        # Both (centre)
        ax.text(
            0, 0, str(data["found_by_both"]),
            ha="center", va="center", fontsize=18, fontweight="bold",
        )
        # Text-only (right)
        ax.text(
            0.45, 0, str(data["text_only"]),
            ha="center", va="center", fontsize=18, fontweight="bold",
        )
        # Neither (bottom)
        ax.text(
            0, -0.75, f"Neither: {data['found_by_neither']}",
            ha="center", va="center", fontsize=11, style="italic",
        )

        # Labels
        ax.text(-0.55, 0.65, "Image", ha="center", fontsize=12,
                color="#1565C0", fontweight="bold")
        ax.text(0.55, 0.65, "Text", ha="center", fontsize=12,
                color="#C62828", fontweight="bold")

        # Union recall annotation
        union_recall = data.get("union_recall", 0)
        ax.text(
            0, -0.95, f"Union recall: {union_recall:.3f}",
            ha="center", va="center", fontsize=11,
        )

        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 0.9)
        ax.set_aspect("equal")
        ax.set_title(label, fontsize=13, fontweight="bold")
        ax.axis("off")

    fig.suptitle(
        "Cross-Modal Overlap: Which Mounds Does Each Track Find?",
        fontsize=14, fontweight="bold", y=1.01,
    )
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Venn diagram saved to: {output_path}")


# ---------------------------------------------------------------------------
# Analysis 3: Multi-Verifier Ensemble
# ---------------------------------------------------------------------------

def compute_ensemble_scores(
    probabilities: dict[str, dict[str, float]],
    n_candidates: int,
) -> dict[str, dict[str, float]]:
    """
    Compute ensemble composite scores from 3 verifier probabilities.

    Args:
        probabilities: Dict mapping variant name to {candidate_id: prob}.
        n_candidates: Total number of candidates.

    Returns:
        Dict mapping ensemble strategy name to {candidate_id: score}.
        Strategies: "average", plus raw probabilities for voting-based
        methods (handled at threshold sweep time).
    """
    average_scores: dict[str, float] = {}
    for i in range(n_candidates):
        cid = str(i)
        probs = [
            probabilities[v].get(cid, 0.0) for v in VERIFIER_VARIANTS
        ]
        average_scores[cid] = sum(probs) / len(probs)

    return {"average": average_scores}


def compute_agreement_statistics(
    probabilities: dict[str, dict[str, float]],
    n_candidates: int,
    decision_threshold: float = 0.5,
) -> dict:
    """
    Compute agreement statistics across verifier strategies.

    Args:
        probabilities: Dict mapping variant → {candidate_id: prob}.
        n_candidates: Total number of candidates.
        decision_threshold: Threshold for binary accept/reject.

    Returns:
        Dict with pairwise and 3-way agreement rates.
    """
    # Convert probabilities to binary decisions
    decisions: dict[str, list[bool]] = {}
    for variant in VERIFIER_VARIANTS:
        decisions[variant] = [
            probabilities[variant].get(str(i), 0.0) >= decision_threshold
            for i in range(n_candidates)
        ]

    # Pairwise agreement
    pairwise: dict[str, float] = {}
    variants_list = list(VERIFIER_VARIANTS)
    for i in range(len(variants_list)):
        for j in range(i + 1, len(variants_list)):
            v1, v2 = variants_list[i], variants_list[j]
            agree = sum(
                1 for k in range(n_candidates)
                if decisions[v1][k] == decisions[v2][k]
            )
            pairwise[f"{v1}_vs_{v2}"] = agree / n_candidates

    # 3-way agreement (all three agree)
    three_way = sum(
        1 for k in range(n_candidates)
        if decisions["standard"][k] == decisions["adversarial"][k]
        == decisions["checklist"][k]
    )

    # Count where ensemble would differ from adversarial alone
    ensemble_differs = 0
    for k in range(n_candidates):
        votes = sum(
            1 for v in VERIFIER_VARIANTS if decisions[v][k]
        )
        majority = votes >= 2
        if majority != decisions["adversarial"][k]:
            ensemble_differs += 1

    return {
        "pairwise_agreement": pairwise,
        "three_way_agreement": three_way / n_candidates,
        "three_way_count": three_way,
        "ensemble_differs_from_adversarial": ensemble_differs,
        "n_candidates": n_candidates,
    }


def sweep_ensemble_thresholds(
    coords: list[tuple[float, float]],
    ref_coords: list[tuple[float, float]],
    probabilities: dict[str, dict[str, float]],
    ensemble_scores: dict[str, dict[str, float]],
    n_candidates: int,
    thresholds: list[float],
) -> dict[str, list[dict]]:
    """
    Sweep thresholds for ensemble strategies: average, majority, union.

    Returns:
        Dict mapping strategy name to list of threshold sweep results.
    """
    results: dict[str, list[dict]] = {
        "average": [],
        "majority": [],
        "union": [],
    }

    for threshold in thresholds:
        # Average: filter by averaged score >= threshold
        avg_filtered = [
            coords[i]
            for i in range(n_candidates)
            if ensemble_scores["average"].get(str(i), 0.0) >= threshold
        ]
        avg_metrics = evaluate_detections(
            avg_filtered, ref_coords, MATCH_BUFFER_M
        )
        results["average"].append({
            "threshold": threshold,
            "n_kept": len(avg_filtered),
            **avg_metrics,
        })

        # Majority (2-of-3): accept if ≥2 verifiers have prob ≥ threshold
        maj_filtered = []
        for i in range(n_candidates):
            cid = str(i)
            votes = sum(
                1 for v in VERIFIER_VARIANTS
                if probabilities[v].get(cid, 0.0) >= threshold
            )
            if votes >= 2:
                maj_filtered.append(coords[i])
        maj_metrics = evaluate_detections(
            maj_filtered, ref_coords, MATCH_BUFFER_M
        )
        results["majority"].append({
            "threshold": threshold,
            "n_kept": len(maj_filtered),
            **maj_metrics,
        })

        # Union (1-of-3): accept if ≥1 verifier has prob ≥ threshold
        union_filtered = []
        for i in range(n_candidates):
            cid = str(i)
            any_above = any(
                probabilities[v].get(cid, 0.0) >= threshold
                for v in VERIFIER_VARIANTS
            )
            if any_above:
                union_filtered.append(coords[i])
        union_metrics = evaluate_detections(
            union_filtered, ref_coords, MATCH_BUFFER_M
        )
        results["union"].append({
            "threshold": threshold,
            "n_kept": len(union_filtered),
            **union_metrics,
        })

    return results


def analyse_verifier_ensemble(pilot_data: dict) -> dict:
    """
    Run Analysis 3: Multi-verifier ensemble combining standard,
    adversarial, and checklist verifier strategies.

    Returns:
        Dict with agreement statistics and ensemble sweep results.
    """
    print("\n=== Analysis 3: Multi-Verifier Ensemble ===")
    results: dict = {}

    for track in TRACKS:
        td = pilot_data["tracks"][track]
        n = len(td["candidates"])
        probs = td["probabilities"]

        # Agreement statistics
        agreement = compute_agreement_statistics(probs, n)
        print(f"\n  {TRACK_LABELS[track]} agreement (threshold=0.5):")
        for pair, rate in agreement["pairwise_agreement"].items():
            print(f"    {pair}: {rate:.3f} ({int(rate * n)}/{n})")
        print(
            f"    3-way: {agreement['three_way_agreement']:.3f} "
            f"({agreement['three_way_count']}/{n})"
        )
        print(
            f"    Ensemble differs from adversarial: "
            f"{agreement['ensemble_differs_from_adversarial']}/{n}"
        )

        # Ensemble scores
        ensemble_scores = compute_ensemble_scores(probs, n)

        # Threshold sweep
        sweep = sweep_ensemble_thresholds(
            td["coords"], td["ref_coords"],
            probs, ensemble_scores, n, THRESHOLDS,
        )

        # Find optimal F1 for each strategy
        optimals = {}
        for strategy, sweep_data in sweep.items():
            opt = find_optimal_f1(sweep_data)
            optimals[strategy] = opt
            print(
                f"  {strategy:10s}: optimal F1={opt['f1']:.3f} "
                f"@ t={opt['threshold']:.2f}  "
                f"P={opt['precision']:.3f}  "
                f"R={opt['recall']:.3f}  "
                f"(n={opt['n_kept']})"
            )

        # Also report best single verifier for comparison
        best_single = {"variant": "", "f1": 0.0}
        for variant in VERIFIER_VARIANTS:
            prob = probs[variant]
            for t in THRESHOLDS:
                filtered = filter_candidates_by_threshold(
                    td["coords"], prob, t
                )
                m = evaluate_detections(
                    filtered, td["ref_coords"], MATCH_BUFFER_M
                )
                if m["f1"] > best_single["f1"]:
                    best_single = {
                        "variant": variant,
                        "threshold": t,
                        "f1": m["f1"],
                        "precision": m["precision"],
                        "recall": m["recall"],
                        "n_kept": len(filtered),
                    }

        print(
            f"  Best single: {best_single['variant']} "
            f"F1={best_single['f1']:.3f} "
            f"@ t={best_single.get('threshold', '?')}"
        )

        results[track] = {
            "agreement": agreement,
            "ensemble_sweep": {
                k: v for k, v in sweep.items()
            },
            "ensemble_optimals": {
                k: v for k, v in optimals.items()
            },
            "best_single_verifier": best_single,
        }

    return results


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    pr_results: dict | None,
    overlap_results: dict | None,
    ensemble_results: dict | None,
    output_path: Path,
) -> None:
    """Generate Markdown report combining all analyses."""
    lines = [
        "# Phase 3d Pilot — Extended Analyses",
        "",
        "## Metadata",
        "",
        f"- **Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "- **Script**: `scripts/analyse_h2_pilot_extensions.py`",
        f"- **Matching method**: Greedy nearest-neighbour, {MATCH_BUFFER_M} m buffer",
        "- **Data source**: Phase 3d pilot (K=1, T=0.0, 3 verifier strategies)",
        "",
    ]

    # --- Analysis 1: P-R curves ---
    if pr_results:
        lines.extend([
            "## Analysis 1: Precision-Recall Curves",
            "",
            "Fine-grained threshold sweep (0.01 steps) across all verifier",
            "strategy × track combinations.",
            "",
            "### AUC-PR and Optimal Operating Points",
            "",
            "| Track | Verifier | AUC-PR | Optimal F1 | Threshold "
            "| Precision | Recall | N kept |",
            "|-------|----------|--------|------------|----------"
            "|-----------|--------|--------|",
        ])
        for track in TRACKS:
            for variant in VERIFIER_VARIANTS:
                d = pr_results[track][variant]
                opt = d["optimal"]
                lines.append(
                    f"| {TRACK_LABELS[track]} | {variant.capitalize()} "
                    f"| {d['auc_pr']:.3f} | {opt['f1']:.3f} "
                    f"| {opt['threshold']:.2f} | {opt['precision']:.3f} "
                    f"| {opt['recall']:.3f} | {opt['n_kept']} |"
                )
        lines.extend([
            "",
            "### Baselines (unfiltered proposer)",
            "",
            "| Track | Precision | Recall | F1 | N candidates |",
            "|-------|-----------|--------|----|-------------|",
        ])
        for track in TRACKS:
            bl = pr_results[track]["baseline"]
            lines.append(
                f"| {TRACK_LABELS[track]} | {bl['precision']:.3f} "
                f"| {bl['recall']:.3f} | {bl['f1']:.3f} "
                f"| {bl['tp'] + bl['fp']} |"
            )
        lines.extend([
            "",
            "**Figure**: See `results/figures/phase3d-pr-curves.png`",
            "",
            "**Note**: Standard and checklist verifiers produce extremely",
            "bimodal probability distributions (nearly all values at 0.0–0.1",
            "or 0.9–1.0), so their P-R curves are effectively step functions.",
            "The adversarial verifier has more intermediate probabilities and",
            "produces the most informative curve.",
            "",
        ])

    # --- Analysis 2: Cross-modal overlap ---
    if overlap_results:
        pre = overlap_results["pre_verification"]
        fp = overlap_results["fp_overlap"]
        post = overlap_results["post_verification"]

        lines.extend([
            "## Analysis 2: Cross-Modal Overlap",
            "",
            "Which specific ground-truth mounds does each track's proposer",
            "find? This determines whether cross-modal union is viable.",
            "",
            "### Pre-verification (proposer candidates only)",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total ground-truth mounds | {pre['total_refs']} |",
            f"| Image track TPs | {pre['image_tp']} |",
            f"| Text track TPs | {pre['text_tp']} |",
            f"| Found by both tracks | {pre['found_by_both']} |",
            f"| Image-only discoveries | {pre['image_only']} |",
            f"| Text-only discoveries | {pre['text_only']} |",
            f"| Found by neither | {pre['found_by_neither']} |",
            f"| **Union recall** | **{pre['union_recall']:.3f}** "
            f"({pre['union_count']}/{pre['total_refs']}) |",
            f"| Jaccard index | {pre['jaccard']:.3f} |",
            "",
            "### False positive overlap",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Image FPs | {fp['image_fps']} |",
            f"| Text FPs | {fp['text_fps']} |",
            f"| Co-occurring FPs (within 20 m) | {fp['co_occurring']} |",
            f"| Image-unique FPs | {fp['image_unique_fps']} |",
            f"| Text-unique FPs | {fp['text_unique_fps']} |",
            "",
            "### Post-verification (adversarial, "
            f"threshold ≥ {post['threshold']})",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Image kept → TPs | {post['image_kept']} → {post['image_tp']} |",
            f"| Text kept → TPs | {post['text_kept']} → {post['text_tp']} |",
            f"| Found by both tracks | {post['found_by_both']} |",
            f"| Image-only discoveries | {post['image_only']} |",
            f"| Text-only discoveries | {post['text_only']} |",
            f"| Found by neither | {post['found_by_neither']} |",
            f"| **Union recall** | **{post['union_recall']:.3f}** "
            f"({post['union_count']}/{pre['total_refs']}) |",
            f"| Jaccard index | {post['jaccard']:.3f} |",
            "",
            "**Figure**: See `results/figures/phase3d-cross-modal-venn.png`",
            "",
        ])

    # --- Analysis 3: Ensemble ---
    if ensemble_results:
        lines.extend([
            "## Analysis 3: Multi-Verifier Ensemble",
            "",
            "Combines the three verifier strategies as an ensemble to test",
            "whether diversity across cognitive tasks improves on the best",
            "single verifier.",
            "",
            "### Agreement Statistics (decision threshold = 0.5)",
            "",
            "| Track | Pair | Agreement |",
            "|-------|------|-----------|",
        ])
        for track in TRACKS:
            ag = ensemble_results[track]["agreement"]
            for pair, rate in ag["pairwise_agreement"].items():
                lines.append(
                    f"| {TRACK_LABELS[track]} | {pair} | "
                    f"{rate:.3f} ({int(rate * ag['n_candidates'])}/"
                    f"{ag['n_candidates']}) |"
                )
            lines.append(
                f"| {TRACK_LABELS[track]} | 3-way | "
                f"{ag['three_way_agreement']:.3f} "
                f"({ag['three_way_count']}/{ag['n_candidates']}) |"
            )

        lines.extend([
            "",
            "### Ensemble vs Best Single Verifier",
            "",
            "| Track | Strategy | F1 | Threshold "
            "| Precision | Recall | N kept |",
            "|-------|----------|-----|----------"
            "|-----------|--------|--------|",
        ])
        for track in TRACKS:
            bs = ensemble_results[track]["best_single_verifier"]
            lines.append(
                f"| {TRACK_LABELS[track]} | "
                f"Best single ({bs['variant']}) "
                f"| {bs['f1']:.3f} | {bs.get('threshold', '?')} "
                f"| {bs['precision']:.3f} | {bs['recall']:.3f} "
                f"| {bs.get('n_kept', '?')} |"
            )
            for strategy in ["average", "majority", "union"]:
                opt = ensemble_results[track]["ensemble_optimals"][strategy]
                lines.append(
                    f"| {TRACK_LABELS[track]} | "
                    f"Ensemble ({strategy}) "
                    f"| {opt['f1']:.3f} | {opt['threshold']:.2f} "
                    f"| {opt['precision']:.3f} | {opt['recall']:.3f} "
                    f"| {opt['n_kept']} |"
                )
        lines.append("")

    lines.extend([
        "## Implications for Next Experiments",
        "",
        "*(To be completed after reviewing results.)*",
        "",
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n  Report saved to: {output_path}")


def save_json_results(
    pr_results: dict | None,
    overlap_results: dict | None,
    ensemble_results: dict | None,
    output_path: Path,
) -> None:
    """Save machine-readable JSON results."""

    def make_serialisable(obj):
        """Convert sets and other non-serialisable types."""
        if isinstance(obj, set):
            return sorted(obj)
        if isinstance(obj, dict):
            return {k: make_serialisable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [make_serialisable(v) for v in obj]
        return obj

    combined = {
        "metadata": {
            "script": "scripts/analyse_h2_pilot_extensions.py",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "match_buffer_m": MATCH_BUFFER_M,
            "matching_method": "greedy_nearest_neighbour",
        },
    }
    if pr_results is not None:
        combined["pr_curves"] = make_serialisable(pr_results)
    if overlap_results is not None:
        combined["cross_modal_overlap"] = make_serialisable(overlap_results)
    if ensemble_results is not None:
        combined["verifier_ensemble"] = make_serialisable(ensemble_results)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, default=str)
    print(f"  JSON results saved to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Phase 3d pilot extended analyses (zero API calls).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--analysis",
        choices=["pr-curves", "cross-modal", "ensemble", "all"],
        default="all",
        help="Which analysis to run (default: all).",
    )
    args = parser.parse_args()

    run_pr = args.analysis in ("pr-curves", "all")
    run_overlap = args.analysis in ("cross-modal", "all")
    run_ensemble = args.analysis in ("ensemble", "all")

    print("Loading pilot data...")
    pilot_data = load_pilot_data()
    for track in TRACKS:
        td = pilot_data["tracks"][track]
        print(
            f"  {TRACK_LABELS[track]}: {len(td['candidates'])} candidates, "
            f"{len(td['ref_coords'])} reference mounds"
        )

    pr_results = None
    overlap_results = None
    ensemble_results = None

    if run_pr:
        pr_results = analyse_pr_curves(pilot_data)
        plot_pr_curves(pr_results, FIGURES_DIR / "phase3d-pr-curves.png")
        save_pr_csv(pr_results, RESULTS_DIR / "phase3d-pr-curves.csv")

    if run_overlap:
        overlap_results = analyse_cross_modal_overlap(pilot_data)
        plot_cross_modal_venn(
            overlap_results,
            FIGURES_DIR / "phase3d-cross-modal-venn.png",
        )

    if run_ensemble:
        ensemble_results = analyse_verifier_ensemble(pilot_data)

    # Save combined outputs
    generate_report(
        pr_results, overlap_results, ensemble_results,
        RESULTS_DIR / "phase3d-pilot-extensions.md",
    )
    save_json_results(
        pr_results, overlap_results, ensemble_results,
        RESULTS_DIR / "phase3d-pilot-extensions.json",
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
