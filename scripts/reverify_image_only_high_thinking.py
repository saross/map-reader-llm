#!/usr/bin/env python3
"""
Re-verify image-only union candidates with HIGH thinking budget.

This script re-verifies the 44 image-only candidates from the cross-modal
union experiment using the adversarial verifier with thinking_level="high"
(instead of "minimal"). The hypothesis is that extended reasoning may help
the verifier correctly reject high-confidence false positives that the
minimal-thinking verifier misclassifies.

Outputs:
    outputs/phase3d-union/verifier_adversarial_high_thinking_probabilities.json
        — probability map for the 44 image-only candidates

Usage:
    python scripts/reverify_image_only_high_thinking.py [--dry-run]
"""

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME = "gemini-3-flash"
API_VERSION = "v1alpha"
TEMPERATURE = 0.0
THINKING_LEVEL = "high"  # The key change from the original experiment
MAX_OUTPUT_TOKENS = 8192
MAX_RETRIES = 3
RETRY_BASE_DELAY_S = 5.0

UNION_DIR = REPO_ROOT / "outputs" / "phase3d-union"
MANIFEST_PATH = UNION_DIR / "candidates" / "candidate_manifest.json"
UNION_GEOJSON_PATH = UNION_DIR / "union_detections.geojson"
CROPS_DIR = UNION_DIR / "candidates"

INSTRUCTION_PATH = (
    REPO_ROOT / "prompts" / "system-instructions" / "verify_adversarial.md"
)

# Example images for verifier (text-only mode — no images included)
EXAMPLES_DIR = REPO_ROOT / "inputs" / "examples"
VERIFIER_EXAMPLES = [
    {"path": "neutral-naming/example_01.png", "label": "Positive: Burial Mound (Kurgan)"},
    {"path": "neutral-naming/example_02.png", "label": "Positive: Settlement Mound"},
    {"path": "neutral-naming/example_03.png", "label": "Positive: Triangulation Point ON Mound"},
    {"path": "neutral-naming/example_04.png", "label": "Positive: Benchmark ON Mound"},
    {"path": "neutral-naming/example_09.png", "label": "Negative: Triangulation Point ALONE"},
    {"path": "neutral-naming/example_10.png", "label": "Negative: Benchmark ALONE"},
]

OUTPUT_PATH = UNION_DIR / "verifier_adversarial_high_thinking_probabilities.json"

# Match the union experiment: include_examples=False (text-only mode)
INCLUDE_EXAMPLES = False


# ---------------------------------------------------------------------------
# Verifier API call (adapted from run_h2_pilot.py with thinking_level param)
# ---------------------------------------------------------------------------

def build_verifier_request(
    instruction_text: str,
    crop_path: Path,
    include_examples: bool = False,
) -> list:
    """Build content parts for a verifier API call."""
    from google.genai import types

    parts = []

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


def call_verifier_high_thinking(
    client,
    model_name: str,
    instruction_text: str,
    crop_path: Path,
    include_examples: bool,
) -> dict | None:
    """
    Call verifier on a single candidate crop with HIGH thinking.

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
            print(f"    JSON parse error: {raw[:80] if raw else 'empty'}")
            return None
        except Exception as e:
            err = str(e)
            if "429" in err or "500" in err or "503" in err:
                delay = RETRY_BASE_DELAY_S * (2 ** (attempt - 1))
                print(
                    f"    Retry {attempt}/{MAX_RETRIES} after {delay:.0f}s"
                    f" ({err[:60]})"
                )
                time.sleep(delay)
            else:
                print(f"    API error: {err[:100]}")
                return None

    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Re-verify image-only candidates with HIGH thinking."""
    dry_run = "--dry-run" in sys.argv

    # Load union GeoJSON to identify image-only candidates
    with open(UNION_GEOJSON_PATH) as f:
        union_geo = json.load(f)

    image_only_indices = []
    for i, feat in enumerate(union_geo["features"]):
        tracks = feat["properties"]["source_tracks"]
        if tracks == ["track1-image"]:
            image_only_indices.append(i)

    print(f"Image-only candidates: {len(image_only_indices)}")

    # Load candidate manifest
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    candidates = manifest["candidates"]
    print(f"Total candidates in manifest: {len(candidates)}")

    # Load verifier instruction
    instruction_text = INSTRUCTION_PATH.read_text()
    print(f"Verifier instruction: {INSTRUCTION_PATH.name}")
    print(f"Thinking level: {THINKING_LEVEL}")
    print(f"Include examples: {INCLUDE_EXAMPLES}")

    if dry_run:
        print("\n[DRY RUN] Would verify these candidates:")
        for idx in image_only_indices:
            c = candidates[idx]
            crop_path = CROPS_DIR / c["crop_file"]
            print(f"  ID {c['candidate_id']}: {crop_path.name}"
                  f" (exists={crop_path.exists()})")
        print(f"\nEstimated API calls: {len(image_only_indices)}")
        print(f"Output would be saved to: {OUTPUT_PATH}")
        return

    # Initialise Gemini client
    import os
    from google import genai

    # Load .env if present (matches run_h2_pilot.py pattern)
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not set")
        sys.exit(1)

    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": API_VERSION},
    )

    # Resolve model name (use same pattern as run_h2_pilot)
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from run_h2_pilot import resolve_model_name
    model_name = resolve_model_name(client, MODEL_NAME)
    print(f"Model: {model_name}")

    # Verify each image-only candidate
    probabilities: dict[str, float | None] = {}
    n_success = 0
    n_fail = 0
    start_time = time.time()

    for seq, idx in enumerate(image_only_indices, 1):
        c = candidates[idx]
        cid = str(c["candidate_id"])
        crop_path = CROPS_DIR / c["crop_file"]

        print(f"  [{seq}/{len(image_only_indices)}] "
              f"Candidate {cid} ({crop_path.name})...", end=" ")

        if not crop_path.exists():
            print("SKIP (crop not found)")
            probabilities[cid] = None
            n_fail += 1
            continue

        result = call_verifier_high_thinking(
            client, model_name, instruction_text,
            crop_path, INCLUDE_EXAMPLES,
        )

        if result and "mound_probability" in result:
            prob = float(result["mound_probability"])
            probabilities[cid] = prob
            n_success += 1
            print(f"p={prob:.2f}")
        else:
            probabilities[cid] = None
            n_fail += 1
            print("FAILED")

    elapsed = time.time() - start_time

    # Save results
    with open(OUTPUT_PATH, "w") as f:
        json.dump(probabilities, f, indent=2)

    print(f"\nDone in {elapsed:.0f}s")
    print(f"  Success: {n_success}, Failed: {n_fail}")
    print(f"  Saved to: {OUTPUT_PATH}")

    # Quick summary of probability distribution
    valid_probs = [v for v in probabilities.values() if v is not None]
    if valid_probs:
        high = sum(1 for p in valid_probs if p >= 0.5)
        low = sum(1 for p in valid_probs if p < 0.5)
        print(f"  Distribution: {high} high (≥0.5), {low} low (<0.5)")


if __name__ == "__main__":
    main()
