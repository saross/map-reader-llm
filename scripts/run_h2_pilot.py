#!/usr/bin/env python3
"""
H2 Two-Stage Pipeline Pilot
============================

Runs a K=1, T=0.0 pilot of the two-stage proposer→verifier architecture
against the single-stage baseline. Tests three verifier strategies:
  B: Standard verification (verify_brief.md)
  C: Adversarial verification (verify_adversarial.md)
  D: Feature checklist verification (verify_checklist.md)

Reuses existing Phase 2d detection outputs as proposer data and crops
extracted by extract_candidates.py.

Usage:
    uv run python scripts/run_h2_pilot.py
    uv run python scripts/run_h2_pilot.py --dry-run
    uv run python scripts/run_h2_pilot.py --track track1-image

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
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

# Proposer data — reuse Phase 2d optimal config, run 1
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

# Candidate manifests (from extract_candidates.py)
CANDIDATE_PATHS = {
    "track1-image": (
        REPO_ROOT / "outputs" / "phase3d-pilot" / "track1-image"
        / "candidates" / "candidate_manifest.json"
    ),
    "track2-text": (
        REPO_ROOT / "outputs" / "phase3d-pilot" / "track2-text"
        / "candidates" / "candidate_manifest.json"
    ),
}

# Crop directories
CROP_DIRS = {
    "track1-image": (
        REPO_ROOT / "outputs" / "phase3d-pilot" / "track1-image"
        / "candidates" / "crops"
    ),
    "track2-text": (
        REPO_ROOT / "outputs" / "phase3d-pilot" / "track2-text"
        / "candidates" / "crops"
    ),
}

# Ground truth
REFERENCES_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
)
BOUNDS_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "bounds" / "validation_bounds.geojson"
)

# Verifier configurations
VERIFIER_VARIANTS = {
    "standard": {
        "instruction": "verify_brief.md",
        "description": "Standard verifier",
    },
    "adversarial": {
        "instruction": "verify_adversarial.md",
        "description": "Adversarial verifier",
    },
    "checklist": {
        "instruction": "verify_checklist.md",
        "description": "Feature checklist verifier",
    },
}

# Example images for verifier (from existing verify_brief.json)
EXAMPLES_DIR = REPO_ROOT / "inputs" / "examples"
VERIFIER_EXAMPLES = [
    {"path": "neutral-naming/example_01.png", "label": "Positive: Burial Mound (Kurgan)"},
    {"path": "neutral-naming/example_02.png", "label": "Positive: Settlement Mound"},
    {"path": "neutral-naming/example_03.png", "label": "Positive: Triangulation Point ON Mound"},
    {"path": "neutral-naming/example_04.png", "label": "Positive: Benchmark ON Mound"},
    {"path": "neutral-naming/example_09.png", "label": "Negative: Triangulation Point ALONE"},
    {"path": "neutral-naming/example_10.png", "label": "Negative: Benchmark ALONE"},
]

# API configuration
MODEL_NAME = "gemini-3-flash"
API_VERSION = "v1alpha"
TEMPERATURE = 0.0
THINKING_LEVEL = "minimal"
MAX_OUTPUT_TOKENS = 8192
MAX_RETRIES = 3
RETRY_BASE_DELAY_S = 5.0

# Evaluation
MATCH_BUFFER_M = 20.0
PROBABILITY_THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

OUTPUT_DIR = REPO_ROOT / "outputs" / "phase3d-pilot"


# ---------------------------------------------------------------------------
# Ground truth loading and evaluation
# ---------------------------------------------------------------------------

def load_geojson(path: Path) -> dict:
    """Load a GeoJSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_feature_centroid(feature: dict) -> tuple[float, float] | None:
    """Extract centroid from a GeoJSON feature geometry."""
    from shapely.geometry import shape
    try:
        geom = shape(feature["geometry"])
        return (geom.centroid.x, geom.centroid.y)
    except Exception:
        return None


def get_references_in_bounds(
    references: list[dict],
    bounds_features: list[dict],
    tile_names: set[str],
) -> list[tuple[float, float]]:
    """
    Get all reference mound coordinates within the given tile bounds.

    Args:
        references: Reference mound GeoJSON features.
        bounds_features: Tile bounds GeoJSON features.
        tile_names: Set of tile filenames to include.

    Returns:
        List of (easting, northing) reference coordinates.
    """
    from shapely.geometry import Point, shape

    # Build union of tile bounds
    tile_polys = []
    for feat in bounds_features:
        name = feat.get("properties", {}).get("tile_name", "")
        if name in tile_names:
            tile_polys.append(shape(feat["geometry"]))

    if not tile_polys:
        return []

    from shapely.ops import unary_union
    bounds_union = unary_union(tile_polys)

    ref_coords = []
    for feat in references:
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [])
        geom_type = geom.get("type", "")

        points = []
        if geom_type == "MultiPoint":
            points = [(c[0], c[1]) for c in coords if len(c) >= 2]
        elif geom_type == "Point" and len(coords) >= 2:
            points = [(coords[0], coords[1])]

        for x, y in points:
            if bounds_union.contains(Point(x, y)):
                ref_coords.append((x, y))

    return ref_coords


def evaluate_detections(
    det_coords: list[tuple[float, float]],
    ref_coords: list[tuple[float, float]],
    buffer_m: float,
) -> dict:
    """
    Evaluate detections against references using greedy nearest-neighbour.

    Returns:
        Dict with tp, fp, fn, precision, recall, f1.
    """
    import math

    if not det_coords and not ref_coords:
        return {"tp": 0, "fp": 0, "fn": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0}
    if not det_coords:
        return {"tp": 0, "fp": 0, "fn": len(ref_coords),
                "precision": 0.0, "recall": 0.0, "f1": 0.0}
    if not ref_coords:
        return {"tp": 0, "fp": len(det_coords), "fn": 0,
                "precision": 0.0, "recall": 0.0, "f1": 0.0}

    # All pairwise distances
    pairs = []
    for d_idx, det in enumerate(det_coords):
        for r_idx, ref in enumerate(ref_coords):
            dist = math.sqrt((det[0] - ref[0]) ** 2 + (det[1] - ref[1]) ** 2)
            pairs.append((dist, d_idx, r_idx))
    pairs.sort()

    # Greedy assignment
    matched_d, matched_r = set(), set()
    for dist, d_idx, r_idx in pairs:
        if dist > buffer_m:
            break
        if d_idx in matched_d or r_idx in matched_r:
            continue
        matched_d.add(d_idx)
        matched_r.add(r_idx)

    tp = len(matched_d)
    fp = len(det_coords) - tp
    fn = len(ref_coords) - len(matched_r)
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    return {"tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": r, "f1": f1}


# ---------------------------------------------------------------------------
# API calling
# ---------------------------------------------------------------------------

def resolve_model_name(client, model_name: str) -> str:
    """Resolve model name, trying -preview suffix if needed."""
    try:
        available = {
            m.name.removeprefix("models/") for m in client.models.list()
        }
    except Exception:
        return model_name

    if model_name in available:
        return model_name
    preview = f"{model_name}-preview"
    if preview in available:
        print(f"  Resolved '{model_name}' → '{preview}'")
        return preview
    return model_name


def build_verifier_request(
    instruction_text: str,
    crop_path: Path,
    include_examples: bool = True,
) -> list:
    """
    Build content parts for a verifier API call.

    Args:
        instruction_text: Verifier system instruction text.
        crop_path: Path to the candidate crop image.
        include_examples: Whether to include visual reference examples.

    Returns:
        List of Part objects.
    """
    from google.genai import types

    parts = []

    # Example images (if image track)
    if include_examples:
        parts.append(types.Part.from_text(
            text="Reference examples for comparison:"
        ))
        for ex in VERIFIER_EXAMPLES:
            img_path = EXAMPLES_DIR / ex["path"]
            if img_path.exists():
                parts.append(types.Part.from_text(text=ex["label"]))
                with open(img_path, "rb") as f:
                    parts.append(types.Part.from_bytes(
                        data=f.read(), mime_type="image/png"
                    ))
    else:
        # Text-only: provide labels without images
        parts.append(types.Part.from_text(
            text="Reference examples (text descriptions only):\n"
            + "\n".join(f"- {ex['label']}" for ex in VERIFIER_EXAMPLES)
        ))

    # Candidate crop
    parts.append(types.Part.from_text(
        text="Now classify the candidate symbol at the centre of this crop:"
    ))
    with open(crop_path, "rb") as f:
        parts.append(types.Part.from_bytes(
            data=f.read(), mime_type="image/png"
        ))

    return parts


def call_verifier(
    client,
    model_name: str,
    instruction_text: str,
    crop_path: Path,
    include_examples: bool,
) -> dict | None:
    """
    Call verifier on a single candidate crop.

    Returns:
        Parsed JSON response dict with mound_probability, or None on failure.
    """
    from google.genai import types

    content_parts = build_verifier_request(
        instruction_text, crop_path, include_examples
    )
    content = types.Content(parts=content_parts)

    gen_config = types.GenerateContentConfig(
        temperature=TEMPERATURE,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL),
        system_instruction=instruction_text,
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
            ),
        ],
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=content,
                config=gen_config,
            )
            if response.candidates and response.candidates[0].content:
                text_parts = [
                    p.text
                    for p in response.candidates[0].content.parts
                    if hasattr(p, "text") and p.text
                ]
                raw = "".join(text_parts)
                if raw:
                    return json.loads(raw)
            return None

        except json.JSONDecodeError:
            # Got a response but couldn't parse JSON
            print(f"    JSON parse error: {raw[:80] if raw else 'empty'}")
            return None
        except Exception as e:
            err = str(e)
            if "429" in err or "500" in err or "503" in err:
                delay = RETRY_BASE_DELAY_S * (2 ** (attempt - 1))
                print(f"    Retry {attempt}/{MAX_RETRIES} after {delay:.0f}s")
                time.sleep(delay)
            else:
                print(f"    API error: {err[:100]}")
                return None

    return None


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run_track(
    track: str,
    client,
    model_name: str,
    dry_run: bool = False,
) -> dict:
    """
    Run the full pilot for one track.

    Returns:
        Dict mapping condition name → evaluation results at each threshold.
    """
    print(f"\n{'='*70}")
    print(f"TRACK: {track}")
    print(f"{'='*70}")

    # Load proposer detections
    proposer_path = PROPOSER_PATHS[track]
    proposer_data = load_geojson(proposer_path)
    proposer_features = proposer_data["features"]
    n_det = len(proposer_features)
    print(f"Proposer detections: {n_det}")

    # Extract detection coordinates
    det_coords_all = []
    source_tiles = set()
    for feat in proposer_features:
        centroid = get_feature_centroid(feat)
        tile = feat.get("properties", {}).get("source_tile", "")
        if centroid:
            det_coords_all.append(centroid)
            source_tiles.add(tile)
        else:
            det_coords_all.append(None)

    # Load ground truth
    refs_data = load_geojson(REFERENCES_PATH)
    bounds_data = load_geojson(BOUNDS_PATH)
    ref_coords = get_references_in_bounds(
        refs_data["features"], bounds_data["features"], source_tiles
    )
    print(f"Reference mounds in scope: {len(ref_coords)}")

    # --- Condition A: Single-stage baseline (unfiltered proposer) ---
    valid_coords = [c for c in det_coords_all if c is not None]
    baseline_eval = evaluate_detections(valid_coords, ref_coords, MATCH_BUFFER_M)
    print("\nCondition A (single-stage baseline):")
    print(f"  Detections: {len(valid_coords)}")
    print(f"  TP={baseline_eval['tp']} FP={baseline_eval['fp']} "
          f"FN={baseline_eval['fn']}")
    print(f"  P={baseline_eval['precision']:.3f} "
          f"R={baseline_eval['recall']:.3f} "
          f"F1={baseline_eval['f1']:.3f}")

    results = {"baseline": {"all_thresholds": {}, "raw_eval": baseline_eval}}

    if dry_run:
        print("\n[DRY RUN] Would run verifier on "
              f"{n_det} candidates × 3 variants = {n_det * 3} API calls")
        return results

    # Load candidate manifest
    manifest_path = CANDIDATE_PATHS[track]
    with open(manifest_path) as f:
        manifest = json.load(f)
    candidates = manifest["candidates"]

    include_examples = (track == "track1-image")

    # --- Run verifier variants ---
    for variant_name, variant_info in VERIFIER_VARIANTS.items():
        instruction_path = (
            REPO_ROOT / "prompts" / "system-instructions"
            / variant_info["instruction"]
        )
        instruction_text = instruction_path.read_text(encoding="utf-8")

        print(f"\nCondition {variant_name} ({variant_info['description']}):")
        print(f"  Instruction: {variant_info['instruction']}")
        print(f"  Examples: {'image+text' if include_examples else 'text-only'}")

        # Verify each candidate
        probabilities = {}
        for i, candidate in enumerate(candidates):
            cid = candidate["candidate_id"]
            crop_file = candidate["crop_file"]
            crop_path = CROP_DIRS[track].parent / crop_file

            if not crop_path.exists():
                print(f"    Warning: crop not found: {crop_path}")
                probabilities[cid] = 0.0
                continue

            result = call_verifier(
                client, model_name, instruction_text,
                crop_path, include_examples,
            )

            prob = 0.0
            if result and "mound_probability" in result:
                prob = float(result["mound_probability"])
            elif result:
                # Try to extract probability from nested structure
                for key in ["probability", "score", "confidence"]:
                    if key in result:
                        prob = float(result[key])
                        break

            probabilities[cid] = prob

            status = f"p={prob:.2f}"
            if (i + 1) % 20 == 0 or (i + 1) == len(candidates):
                print(f"    [{i+1}/{len(candidates)}] {status}")

        # Save raw probabilities
        prob_path = (
            OUTPUT_DIR / track / f"verifier_{variant_name}_probabilities.json"
        )
        prob_path.parent.mkdir(parents=True, exist_ok=True)
        with open(prob_path, "w") as f:
            json.dump({
                "variant": variant_name,
                "track": track,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "n_candidates": len(candidates),
                "probabilities": {str(k): v for k, v in probabilities.items()},
            }, f, indent=2)

        # Evaluate at multiple thresholds
        threshold_results = {}
        for thresh in PROBABILITY_THRESHOLDS:
            # Filter detections by probability threshold
            kept_coords = []
            for candidate in candidates:
                cid = candidate["candidate_id"]
                if probabilities.get(cid, 0.0) >= thresh:
                    # Use original geographic coordinates
                    cx = candidate["centroid_x"]
                    cy = candidate["centroid_y"]
                    kept_coords.append((cx, cy))

            eval_result = evaluate_detections(
                kept_coords, ref_coords, MATCH_BUFFER_M
            )
            eval_result["n_kept"] = len(kept_coords)
            threshold_results[str(thresh)] = eval_result

        results[variant_name] = {
            "all_thresholds": threshold_results,
            "probabilities": probabilities,
        }

        # Print best threshold result
        best_thresh = max(
            threshold_results.items(),
            key=lambda x: x[1]["f1"],
        )
        bt, br = best_thresh
        print(f"  Best threshold: {bt} → "
              f"F1={br['f1']:.3f} (P={br['precision']:.3f} "
              f"R={br['recall']:.3f}, kept={br['n_kept']})")

    return results


def print_summary(all_results: dict) -> None:
    """Print a comparison summary table across all tracks and conditions."""
    print(f"\n{'='*70}")
    print("PILOT SUMMARY")
    print(f"{'='*70}\n")

    for track, track_results in all_results.items():
        print(f"--- {track} ---\n")

        # Header
        print(f"{'Condition':<16} | {'Threshold':>9} | {'Kept':>4} | "
              f"{'TP':>3} {'FP':>3} {'FN':>3} | "
              f"{'Precision':>9} {'Recall':>7} {'F1':>6}")
        print("-" * 75)

        # Baseline
        bl = track_results["baseline"]["raw_eval"]
        n_det = bl["tp"] + bl["fp"]
        print(f"{'A (baseline)':<16} | {'  —':>9} | {n_det:>4} | "
              f"{bl['tp']:>3} {bl['fp']:>3} {bl['fn']:>3} | "
              f"{bl['precision']:>9.3f} {bl['recall']:>7.3f} "
              f"{bl['f1']:>6.3f}")

        # Verifier conditions
        labels = {"standard": "B (standard)", "adversarial": "C (adversarial)",
                  "checklist": "D (checklist)"}
        for variant in ["standard", "adversarial", "checklist"]:
            if variant not in track_results:
                continue
            thresholds = track_results[variant]["all_thresholds"]
            if not thresholds:
                continue
            # Find best F1
            best_t, best_r = max(
                thresholds.items(), key=lambda x: x[1]["f1"]
            )
            label = labels[variant]
            print(f"{label:<16} | {best_t:>9} | {best_r['n_kept']:>4} | "
                  f"{best_r['tp']:>3} {best_r['fp']:>3} {best_r['fn']:>3} | "
                  f"{best_r['precision']:>9.3f} {best_r['recall']:>7.3f} "
                  f"{best_r['f1']:>6.3f}")

        print()


def main() -> None:
    """Run the H2 two-stage pilot."""
    parser = argparse.ArgumentParser(
        description="H2 Two-Stage Pipeline Pilot",
    )
    parser.add_argument(
        "--track", choices=["track1-image", "track2-text"],
        default=None,
        help="Run single track only (default: both)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate setup without making API calls",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("H2 TWO-STAGE PIPELINE PILOT")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Thinking: {THINKING_LEVEL}")
    print(f"Verifier variants: {', '.join(VERIFIER_VARIANTS.keys())}")
    print(f"Probability thresholds: {PROBABILITY_THRESHOLDS}")
    print("=" * 70)

    # Check API key
    # Load .env if available
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            pass

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: GOOGLE_API_KEY not set")
        sys.exit(1)

    client = None
    model_name = MODEL_NAME
    if not args.dry_run:
        from google import genai
        client = genai.Client(
            api_key=api_key,
            http_options={"api_version": API_VERSION},
        )
        model_name = resolve_model_name(client, MODEL_NAME)
        print(f"Model: {model_name}")

    # Determine tracks to run
    tracks = [args.track] if args.track else ["track1-image", "track2-text"]

    # Validate paths
    for track in tracks:
        for label, path in [
            ("Proposer", PROPOSER_PATHS[track]),
            ("Manifest", CANDIDATE_PATHS[track]),
        ]:
            if not path.exists():
                print(f"Error: {label} not found for {track}: {path}")
                sys.exit(1)

    # Run
    all_results = {}
    for track in tracks:
        track_results = run_track(
            track, client, model_name, dry_run=args.dry_run
        )
        all_results[track] = track_results

    # Save full results
    results_path = OUTPUT_DIR / "pilot_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    # Serialise (strip non-serialisable probability dicts)
    serialisable = {}
    for track, tr in all_results.items():
        serialisable[track] = {}
        for cond, cr in tr.items():
            serialisable[track][cond] = {
                "all_thresholds": cr.get("all_thresholds", {}),
                "raw_eval": cr.get("raw_eval"),
            }

    with open(results_path, "w") as f:
        json.dump({
            "metadata": {
                "script": "run_h2_pilot.py",
                "model": model_name,
                "temperature": TEMPERATURE,
                "thinking_level": THINKING_LEVEL,
                "match_buffer_m": MATCH_BUFFER_M,
                "tracks": tracks,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            },
            "results": serialisable,
        }, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    # Print summary
    if not args.dry_run:
        print_summary(all_results)
    else:
        total_calls = sum(
            len(load_geojson(PROPOSER_PATHS[t])["features"])
            for t in tracks
        ) * len(VERIFIER_VARIANTS)
        print(f"\n[DRY RUN] Total API calls needed: {total_calls}")
        print(f"Estimated cost (real-time): ${total_calls * 0.003:.2f}")
        print(f"Estimated time: ~{total_calls / 2 / 60:.0f} minutes")


if __name__ == "__main__":
    main()
