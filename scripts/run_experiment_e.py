#!/usr/bin/env python3
"""
Experiment E — High-Recall Text Proposer Evaluation
=====================================================

Three-stage single-track pipeline for evaluating a recall-biased text
proposer against the adversarial verifier:

    1. Extract — crop candidate images from proposer detections
    2. Verify — run adversarial verifier on each candidate
    3. Evaluate — threshold sweep, find optimal F1, compare to baselines

Reuses existing infrastructure:
    - extract_candidates() from extract_candidates.py
    - call_verifier(), evaluate_detections(), etc. from run_h2_pilot.py

Usage:
    # Full pipeline (extract + verify + evaluate)
    python scripts/run_experiment_e.py \\
        --proposer-output outputs/results/detect_brief-text_high-recall/detections.geojson

    # Skip extraction (reuse existing candidates)
    python scripts/run_experiment_e.py \\
        --proposer-output outputs/results/detect_brief-text_high-recall/detections.geojson \\
        --skip-extract

    # Evaluate only (reuse existing probabilities)
    python scripts/run_experiment_e.py \\
        --proposer-output outputs/results/detect_brief-text_high-recall/detections.geojson \\
        --skip-verify

    # Dry run (validate paths, count candidates, no API calls)
    python scripts/run_experiment_e.py \\
        --proposer-output outputs/results/detect_brief-text_high-recall/detections.geojson \\
        --dry-run

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — scripts/ is not a package, so we add it to sys.path
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from extract_candidates import extract_candidates  # noqa: E402
from run_h2_pilot import (  # noqa: E402
    MATCH_BUFFER_M,
    call_verifier,
    evaluate_detections,
    get_references_in_bounds,
    load_geojson,
    resolve_model_name,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = REPO_ROOT / "outputs" / "phase3d-experiment-e"
VERIFIER_INSTRUCTION_PATH = (
    REPO_ROOT / "prompts" / "system-instructions" / "verify_adversarial.md"
)
TILES_DIR = REPO_ROOT / "inputs" / "tiles"

# Ground truth
REFERENCES_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "references"
    / "mounds-reference.geojson"
)
BOUNDS_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "bounds"
    / "validation_bounds.geojson"
)

# Application Programming Interface (API) configuration
MODEL_NAME = "gemini-3-flash"
API_VERSION = "v1alpha"

# Baseline comparisons (from Phase 3d pilot and union experiments)
BASELINE_TEXT_ONLY = {
    "f1": 0.796, "precision": 0.809, "recall": 0.784,
    "n": 94, "threshold": 0.16,
}
BASELINE_UNION = {
    "f1": 0.768, "precision": 0.711, "recall": 0.835,
    "n": 114, "threshold": 0.11,
}
BASELINE_PROPOSER_RAW = {
    "n_detections": 140, "precision": 0.557, "recall": 0.804,
}

# Threshold sweep range: 0.00, 0.01, 0.02, ..., 1.00
N_THRESHOLDS = 101


# ---------------------------------------------------------------------------
# Pure-logic functions (testable without API or filesystem)
# ---------------------------------------------------------------------------

def threshold_sweep(
    candidates: list[dict],
    probabilities: dict[int, float],
    ref_coords: list[tuple[float, float]],
    buffer_m: float,
    thresholds: list[float],
) -> list[dict]:
    """
    Evaluate detection performance at each probability threshold.

    For each threshold, filters candidates by probability >= threshold,
    extracts geographic coordinates, and runs greedy nearest-neighbour
    matching against ground truth.

    Args:
        candidates: List of candidate dicts with 'candidate_id',
            'centroid_x', 'centroid_y'.
        probabilities: Mapping of candidate_id → mound_probability.
            Candidates with missing or None probabilities are excluded.
        ref_coords: Ground truth coordinates [(easting, northing), ...].
        buffer_m: Match radius in metres.
        thresholds: List of threshold values to evaluate.

    Returns:
        List of result dicts, one per threshold:
            {threshold, tp, fp, fn, precision, recall, f1, n_kept}
    """
    results = []

    for thresh in thresholds:
        # Filter candidates by probability threshold
        kept_coords = []
        for candidate in candidates:
            cid = candidate["candidate_id"]
            prob = probabilities.get(cid)
            if prob is not None and prob >= thresh:
                kept_coords.append(
                    (candidate["centroid_x"], candidate["centroid_y"])
                )

        # Evaluate against ground truth
        eval_result = evaluate_detections(
            kept_coords, ref_coords, buffer_m
        )
        eval_result["threshold"] = thresh
        eval_result["n_kept"] = len(kept_coords)
        results.append(eval_result)

    return results


def find_optimal_threshold(threshold_results: list[dict]) -> dict | None:
    """
    Find the threshold that maximises F1 score.

    Ties are broken by selecting the lower threshold (more permissive),
    which favours recall when F1 is equal.

    Args:
        threshold_results: Output from threshold_sweep().

    Returns:
        Dict with the best threshold's metrics, or None if empty input.
    """
    if not threshold_results:
        return None

    # Sort by F1 descending, then threshold ascending (for tie-breaking)
    best = max(
        threshold_results,
        key=lambda r: (r["f1"], -r["threshold"]),
    )
    return best


def format_comparison_table(
    experiment_optimal: dict,
    baselines: dict[str, dict],
) -> str:
    """
    Format a Markdown comparison table of experiment vs baselines.

    Args:
        experiment_optimal: Best threshold result from find_optimal_threshold().
        baselines: Dict mapping baseline name → metrics dict with
            f1, precision, recall, n, threshold.

    Returns:
        Markdown table string with header, baseline rows, experiment row,
        and delta row (vs text-only baseline).
    """
    lines = []
    lines.append(
        "| Configuration | Threshold | N | Precision | Recall | F1 |"
    )
    lines.append(
        "|---|---|---|---|---|---|"
    )

    # Baseline rows
    for name, bl in baselines.items():
        lines.append(
            f"| {name} | {bl['threshold']:.2f} | {bl['n']} | "
            f"{bl['precision']:.3f} | {bl['recall']:.3f} | "
            f"{bl['f1']:.3f} |"
        )

    # Experiment row
    exp = experiment_optimal
    lines.append(
        f"| **Experiment E** | {exp['threshold']:.2f} | "
        f"{exp['n_kept']} | {exp['precision']:.3f} | "
        f"{exp['recall']:.3f} | {exp['f1']:.3f} |"
    )

    # Delta row vs text-only baseline
    if "Text-only baseline" in baselines:
        bl = baselines["Text-only baseline"]
        delta_f1 = exp["f1"] - bl["f1"]
        delta_p = exp["precision"] - bl["precision"]
        delta_r = exp["recall"] - bl["recall"]
        sign = "+" if delta_f1 >= 0 else ""
        lines.append(
            f"| *Delta vs text-only* | — | — | "
            f"{delta_p:+.3f} | {delta_r:+.3f} | "
            f"{sign}{delta_f1:.3f} |"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestration functions
# ---------------------------------------------------------------------------

def stage_extract(
    proposer_geojson_path: Path,
    dry_run: bool = False,
) -> Path | None:
    """
    Stage 1: Extract candidate crops from proposer detections.

    Delegates to extract_candidates() from extract_candidates.py.

    Args:
        proposer_geojson_path: Path to proposer output GeoJSON.
        dry_run: If True, validate without extracting.

    Returns:
        Path to candidate_manifest.json, or None on failure/dry-run.
    """
    candidates_dir = OUTPUT_DIR / "candidates"
    print(f"\n{'='*70}")
    print("STAGE 1: EXTRACT CANDIDATES")
    print(f"{'='*70}")
    print(f"  Proposer GeoJSON: {proposer_geojson_path}")
    print(f"  Output dir: {candidates_dir}")

    manifest_path = extract_candidates(
        proposer_geojson=proposer_geojson_path,
        tiles_dir=TILES_DIR,
        output_dir=candidates_dir,
        dry_run=dry_run,
    )
    return manifest_path


def stage_verify(
    manifest_path: Path,
    dry_run: bool = False,
) -> Path | None:
    """
    Stage 2: Run adversarial verifier on each candidate.

    Uses call_verifier() from run_h2_pilot.py with baseline verifier
    settings (T=0.0, minimal thinking, text-only mode).

    Args:
        manifest_path: Path to candidate_manifest.json.
        dry_run: If True, count candidates without calling the API.

    Returns:
        Path to saved probabilities JSON, or None on dry-run.
    """
    print(f"\n{'='*70}")
    print("STAGE 2: ADVERSARIAL VERIFICATION")
    print(f"{'='*70}")

    # Load manifest
    with open(manifest_path) as f:
        manifest = json.load(f)
    candidates = manifest["candidates"]
    n_candidates = len(candidates)
    print(f"  Candidates to verify: {n_candidates}")

    if dry_run:
        print(f"\n[DRY RUN] Would make {n_candidates} API calls")
        print(f"  Estimated cost: ~${n_candidates * 0.007:.2f}")
        return None

    # Load verifier instruction
    instruction_text = VERIFIER_INSTRUCTION_PATH.read_text(encoding="utf-8")
    print(f"  Verifier: {VERIFIER_INSTRUCTION_PATH.name}")

    # Initialise API client
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # Try loading from .env
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                api_key = os.environ.get("GOOGLE_API_KEY")
            except ImportError:
                pass
    if not api_key:
        print("Error: GOOGLE_API_KEY not set")
        sys.exit(1)

    from google import genai
    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": API_VERSION},
    )
    model_name = resolve_model_name(client, MODEL_NAME)
    print(f"  Model: {model_name}")

    # Verify each candidate (text-only mode: include_examples=False)
    crops_dir = manifest_path.parent
    probabilities = {}
    failures = 0

    for i, candidate in enumerate(candidates):
        cid = candidate["candidate_id"]
        crop_file = candidate["crop_file"]
        crop_path = crops_dir / crop_file

        if not crop_path.exists():
            print(f"    Warning: crop not found: {crop_path}")
            probabilities[cid] = None
            failures += 1
            continue

        result = call_verifier(
            client, model_name, instruction_text,
            crop_path, include_examples=False,
        )

        prob = None
        if result and "mound_probability" in result:
            prob = float(result["mound_probability"])
        elif result:
            # Fallback: try alternative probability keys
            for key in ["probability", "score", "confidence"]:
                if key in result:
                    prob = float(result[key])
                    break

        if prob is None:
            failures += 1

        probabilities[cid] = prob

        # Progress reporting
        if (i + 1) % 20 == 0 or (i + 1) == n_candidates:
            p_str = f"p={prob:.2f}" if prob is not None else "FAIL"
            print(f"    [{i+1}/{n_candidates}] {p_str}")

    # Save probabilities
    probs_path = OUTPUT_DIR / "verifier_adversarial_probabilities.json"
    probs_path.parent.mkdir(parents=True, exist_ok=True)
    with open(probs_path, "w") as f:
        json.dump({
            "experiment": "E",
            "verifier": "adversarial",
            "model": model_name,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "n_candidates": n_candidates,
            "n_failures": failures,
            "probabilities": {str(k): v for k, v in probabilities.items()},
        }, f, indent=2)

    print(f"\n  Probabilities saved to: {probs_path}")
    print(f"  Failures: {failures}/{n_candidates}")
    return probs_path


def stage_evaluate(
    manifest_path: Path,
    probs_path: Path,
    proposer_geojson_path: Path,
) -> dict:
    """
    Stage 3: Evaluate results with threshold sweep and comparison.

    Computes raw proposer metrics, runs threshold sweep across 101
    thresholds, finds optimal F1, and prints comparison table.

    Args:
        manifest_path: Path to candidate_manifest.json.
        probs_path: Path to verifier probabilities JSON.
        proposer_geojson_path: Path to proposer output GeoJSON.

    Returns:
        Dict with full results (sweep, optimal, comparisons).
    """
    print(f"\n{'='*70}")
    print("STAGE 3: EVALUATE")
    print(f"{'='*70}")

    # Load manifest and probabilities
    with open(manifest_path) as f:
        manifest = json.load(f)
    candidates = manifest["candidates"]

    with open(probs_path) as f:
        probs_data = json.load(f)
    # Parse probabilities — keys are string candidate_ids
    raw_probs = probs_data["probabilities"]
    probabilities = {}
    for k, v in raw_probs.items():
        probabilities[int(k)] = v

    # Load ground truth
    proposer_data = load_geojson(proposer_geojson_path)
    proposer_features = proposer_data.get("features", [])

    # Get tile names from proposer for bounding
    source_tiles = set()
    for feat in proposer_features:
        tile = feat.get("properties", {}).get("source_tile", "")
        if tile:
            source_tiles.add(tile)

    refs_data = load_geojson(REFERENCES_PATH)
    bounds_data = load_geojson(BOUNDS_PATH)
    ref_coords = get_references_in_bounds(
        refs_data["features"], bounds_data["features"], source_tiles
    )
    print(f"  Reference mounds in scope: {len(ref_coords)}")

    # --- Raw proposer metrics (before verifier) ---
    from run_h2_pilot import get_feature_centroid  # noqa: E402
    proposer_coords = []
    for feat in proposer_features:
        centroid = get_feature_centroid(feat)
        if centroid:
            proposer_coords.append(centroid)

    raw_eval = evaluate_detections(proposer_coords, ref_coords, MATCH_BUFFER_M)
    print("\n  Raw proposer (no verifier):")
    print(f"    Detections: {len(proposer_coords)}")
    print(f"    TP={raw_eval['tp']} FP={raw_eval['fp']} "
          f"FN={raw_eval['fn']}")
    print(f"    P={raw_eval['precision']:.3f} "
          f"R={raw_eval['recall']:.3f} "
          f"F1={raw_eval['f1']:.3f}")

    # --- Threshold sweep ---
    thresholds = [i / (N_THRESHOLDS - 1) for i in range(N_THRESHOLDS)]
    sweep_results = threshold_sweep(
        candidates, probabilities, ref_coords, MATCH_BUFFER_M, thresholds
    )

    # Find optimal threshold
    optimal = find_optimal_threshold(sweep_results)
    print(f"\n  Optimal threshold: {optimal['threshold']:.2f}")
    print(f"    N={optimal['n_kept']} TP={optimal['tp']} "
          f"FP={optimal['fp']} FN={optimal['fn']}")
    print(f"    P={optimal['precision']:.3f} "
          f"R={optimal['recall']:.3f} "
          f"F1={optimal['f1']:.3f}")

    # --- Comparison table ---
    baselines = {
        "Text-only baseline": BASELINE_TEXT_ONLY,
        "Cross-modal union": BASELINE_UNION,
    }
    table = format_comparison_table(optimal, baselines)
    print(f"\n{table}")

    # --- Success criteria check ---
    print("\n  Success criteria:")
    recall_ok = optimal["recall"] > 0.835
    precision_ok = optimal["precision"] > 0.78
    f1_ok = optimal["f1"] > 0.796
    f1_stretch = optimal["f1"] > 0.80
    print(f"    Recall > 0.835 (union):    "
          f"{'PASS' if recall_ok else 'FAIL'} ({optimal['recall']:.3f})")
    print(f"    Precision > 0.78:          "
          f"{'PASS' if precision_ok else 'FAIL'} ({optimal['precision']:.3f})")
    print(f"    F1 > 0.796 (text-only):    "
          f"{'PASS' if f1_ok else 'FAIL'} ({optimal['f1']:.3f})")
    print(f"    F1 > 0.80 (stretch):       "
          f"{'PASS' if f1_stretch else 'FAIL'} ({optimal['f1']:.3f})")

    # --- Save results ---
    results = {
        "metadata": {
            "script": "run_experiment_e.py",
            "experiment": "E",
            "description": "High-recall text proposer + adversarial verifier",
            "proposer_geojson": str(proposer_geojson_path),
            "manifest": str(manifest_path),
            "probabilities": str(probs_path),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "n_references": len(ref_coords),
            "match_buffer_m": MATCH_BUFFER_M,
        },
        "raw_proposer": {
            "n_detections": len(proposer_coords),
            **raw_eval,
        },
        "optimal_threshold": optimal,
        "threshold_sweep": sweep_results,
        "baselines": baselines,
        "success_criteria": {
            "recall_gt_0.835": recall_ok,
            "precision_gt_0.78": precision_ok,
            "f1_gt_0.796": f1_ok,
            "f1_gt_0.80": f1_stretch,
        },
    }

    # Save JSON results
    results_json_path = OUTPUT_DIR / "experiment_e_results.json"
    results_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results JSON: {results_json_path}")

    # Save Markdown report
    md_path = REPO_ROOT / "results" / "phase3d-experiment-e-results.md"
    _write_markdown_report(results, md_path, table)
    print(f"  Markdown report: {md_path}")

    return results


def _write_markdown_report(
    results: dict,
    md_path: Path,
    comparison_table: str,
) -> None:
    """Write a Markdown results report for Experiment E."""
    meta = results["metadata"]
    raw = results["raw_proposer"]
    criteria = results["success_criteria"]

    md_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Experiment E — High-Recall Text Proposer Results",
        "",
        "## Metadata",
        "",
        f"- **Script**: `{meta['script']}`",
        f"- **Timestamp**: {meta['timestamp']}",
        f"- **References in scope**: {meta['n_references']}",
        f"- **Match buffer**: {meta['match_buffer_m']} m",
        f"- **Proposer**: `{Path(meta['proposer_geojson']).name}`",
        "",
        "## Raw Proposer (Before Verifier)",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Detections | {raw['n_detections']} |",
        f"| TP | {raw['tp']} |",
        f"| FP | {raw['fp']} |",
        f"| FN | {raw['fn']} |",
        f"| Precision | {raw['precision']:.3f} |",
        f"| Recall | {raw['recall']:.3f} |",
        f"| F1 | {raw['f1']:.3f} |",
        "",
        "## Verified Results (Optimal Threshold)",
        "",
        comparison_table,
        "",
        "## Success Criteria",
        "",
    ]

    for criterion, passed in criteria.items():
        status = "PASS" if passed else "FAIL"
        lines.append(f"- **{criterion}**: {status}")

    lines.extend([
        "",
        "## Data Artefacts",
        "",
        "| File | Description |",
        "|---|---|",
        f"| `{meta['proposer_geojson']}` | Proposer output GeoJSON |",
        f"| `{meta['manifest']}` | Candidate manifest |",
        f"| `{meta['probabilities']}` | Verifier probabilities |",
        "| `outputs/phase3d-experiment-e/experiment_e_results.json`"
        " | Full results JSON |",
        "",
    ])

    with open(md_path, "w") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------------------
# Command-Line Interface (CLI)
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse command-line arguments and run Experiment E pipeline."""
    parser = argparse.ArgumentParser(
        description="Experiment E: High-recall text proposer evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline
  python scripts/run_experiment_e.py \\
      --proposer-output outputs/results/.../detections.geojson

  # Skip extraction (reuse existing candidates)
  python scripts/run_experiment_e.py \\
      --proposer-output outputs/results/.../detections.geojson \\
      --skip-extract

  # Evaluate only (reuse existing verifier probabilities)
  python scripts/run_experiment_e.py \\
      --proposer-output outputs/results/.../detections.geojson \\
      --skip-verify

  # Dry run (validate paths, no API calls)
  python scripts/run_experiment_e.py \\
      --proposer-output outputs/results/.../detections.geojson \\
      --dry-run
        """,
    )
    parser.add_argument(
        "--proposer-output",
        type=Path,
        required=True,
        help="Path to proposer output GeoJSON",
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Skip extraction, reuse existing candidates",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip verification, reuse existing probabilities",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate paths and count candidates without API calls",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("EXPERIMENT E — HIGH-RECALL TEXT PROPOSER")
    print("=" * 70)
    print(f"  Proposer output: {args.proposer_output}")

    # Validate proposer GeoJSON exists
    if not args.proposer_output.exists():
        print(f"Error: Proposer output not found: {args.proposer_output}")
        sys.exit(1)

    # Determine file paths
    manifest_path = OUTPUT_DIR / "candidates" / "candidate_manifest.json"
    probs_path = OUTPUT_DIR / "verifier_adversarial_probabilities.json"

    # --- Stage 1: Extract ---
    if args.skip_extract or args.skip_verify:
        print(f"\n  [Skipping extraction — using: {manifest_path}]")
        if not manifest_path.exists():
            print(f"Error: Manifest not found: {manifest_path}")
            sys.exit(1)
    else:
        result = stage_extract(
            args.proposer_output, dry_run=args.dry_run
        )
        if args.dry_run:
            # Load proposer GeoJSON to count features for dry-run summary
            data = load_geojson(args.proposer_output)
            n_feat = len(data.get("features", []))
            print("\n[DRY RUN] Summary:")
            print(f"  Proposer detections: {n_feat}")
            print(f"  Estimated verifier cost: ~${n_feat * 0.007:.2f}")
            print(f"  Estimated verifier time: ~{n_feat / 2 / 60:.0f} min")
            return
        if result is None:
            print("Error: Extraction failed")
            sys.exit(1)
        manifest_path = result

    # --- Stage 2: Verify ---
    if args.skip_verify:
        print(f"\n  [Skipping verification — using: {probs_path}]")
        if not probs_path.exists():
            print(f"Error: Probabilities not found: {probs_path}")
            sys.exit(1)
    else:
        result = stage_verify(manifest_path, dry_run=args.dry_run)
        if args.dry_run:
            return
        if result is None:
            print("Error: Verification failed")
            sys.exit(1)
        probs_path = result

    # --- Stage 3: Evaluate ---
    stage_evaluate(manifest_path, probs_path, args.proposer_output)


if __name__ == "__main__":
    main()
