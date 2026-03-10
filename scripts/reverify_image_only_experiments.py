#!/usr/bin/env python3
"""
Unified Image-Only Re-Verification Experiments (A–D).

Re-verifies the 44 image-only candidates from the cross-modal union
experiment under different verifier modifications, each changing exactly
one parameter from the baseline (adversarial verifier, T=0.0,
thinking=minimal, include_examples=False):

    A: provenance  — prepend a provenance preamble informing the verifier
       that this candidate was found ONLY by the image analyser
    B: examples    — include visual reference example images
    C: temperature — T=0.5, multiple passes (default 3), report means
    D: cascaded    — two-stage: first-stage adversarial filter, then
       comparative second-stage verifier on passing candidates only

The --evaluate mode merges experiment probabilities into the full
184-candidate baseline, runs a threshold sweep, and prints a comparison
table (baseline vs experiment).

Outputs (all in outputs/phase3d-union/):
    A: verifier_adversarial_provenance_probabilities.json
    B: verifier_adversarial_examples_probabilities.json
    C: verifier_adversarial_temperature_probabilities.json   (means)
       verifier_adversarial_temperature_all_passes.json      (per-pass)
    D: verifier_comparative_cascaded_probabilities.json

Usage:
    python scripts/reverify_image_only_experiments.py --experiment provenance
    python scripts/reverify_image_only_experiments.py --experiment examples
    python scripts/reverify_image_only_experiments.py --experiment temperature --passes 3
    python scripts/reverify_image_only_experiments.py --experiment cascaded
    python scripts/reverify_image_only_experiments.py --evaluate \\
        outputs/phase3d-union/verifier_adversarial_provenance_probabilities.json
    python scripts/reverify_image_only_experiments.py --experiment provenance --dry-run

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME = "gemini-3-flash"
API_VERSION = "v1alpha"
MAX_OUTPUT_TOKENS = 8192
MAX_RETRIES = 3
RETRY_BASE_DELAY_S = 5.0

# Baseline verifier parameters (cross-modal union experiment)
BASELINE_TEMPERATURE = 0.0
BASELINE_THINKING_LEVEL = "minimal"

UNION_DIR = REPO_ROOT / "outputs" / "phase3d-union"
MANIFEST_PATH = UNION_DIR / "candidates" / "candidate_manifest.json"
UNION_GEOJSON_PATH = UNION_DIR / "union_detections.geojson"
BASELINE_PROBS_PATH = UNION_DIR / "verifier_adversarial_probabilities.json"
CROPS_DIR = UNION_DIR / "candidates"

INSTRUCTION_PATH = (
    REPO_ROOT / "prompts" / "system-instructions" / "verify_adversarial.md"
)
COMPARATIVE_INSTRUCTION_PATH = (
    REPO_ROOT / "prompts" / "system-instructions" / "verify_comparative.md"
)

# Reference example images for the verifier
EXAMPLES_DIR = REPO_ROOT / "inputs" / "examples"
VERIFIER_EXAMPLES = [
    {"path": "neutral-naming/example_01.png",
     "label": "Positive: Burial Mound (Kurgan)"},
    {"path": "neutral-naming/example_02.png",
     "label": "Positive: Settlement Mound"},
    {"path": "neutral-naming/example_03.png",
     "label": "Positive: Triangulation Point ON Mound"},
    {"path": "neutral-naming/example_04.png",
     "label": "Positive: Benchmark ON Mound"},
    {"path": "neutral-naming/example_09.png",
     "label": "Negative: Triangulation Point ALONE"},
    {"path": "neutral-naming/example_10.png",
     "label": "Negative: Benchmark ALONE"},
]

# Positive-only reference examples for the comparative verifier (Experiment D)
COMPARATIVE_EXAMPLES = [
    {"path": "neutral-naming/example_01.png",
     "label": ("Confirmed mound: Burial Mound (Kurgan) "
               "— note outward rays")},
    {"path": "neutral-naming/example_02.png",
     "label": ("Confirmed mound: Settlement Mound "
               "— note outward rays")},
    {"path": "neutral-naming/example_03.png",
     "label": ("Confirmed mound: Trig Point ON Mound "
               "— note rays from triangle")},
    {"path": "neutral-naming/example_04.png",
     "label": ("Confirmed mound: Benchmark ON Mound "
               "— note rays from square")},
]

# Ground truth paths (for --evaluate mode)
REFERENCES_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "references"
    / "mounds-reference.geojson"
)
BOUNDS_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "bounds"
    / "validation_bounds.geojson"
)

# Provenance preamble (Experiment A)
PROVENANCE_PREAMBLE = (
    "Note: This candidate was detected by the image-based analyser ONLY. "
    "A separate text-based analysis of the same map area did NOT flag this "
    "location. Consider whether this absence is informative."
)

# Output file names per experiment
OUTPUT_FILES = {
    "provenance": "verifier_adversarial_provenance_probabilities.json",
    "examples": "verifier_adversarial_examples_probabilities.json",
    "temperature": "verifier_adversarial_temperature_probabilities.json",
    "cascaded": "verifier_comparative_cascaded_probabilities.json",
}
TEMPERATURE_ALL_PASSES_FILE = (
    "verifier_adversarial_temperature_all_passes.json"
)

# Experiment-specific parameter overrides
EXPERIMENT_PARAMS = {
    "provenance": {
        "temperature": BASELINE_TEMPERATURE,
        "thinking_level": BASELINE_THINKING_LEVEL,
        "include_examples": False,
        "provenance_preamble": True,
    },
    "examples": {
        "temperature": BASELINE_TEMPERATURE,
        "thinking_level": BASELINE_THINKING_LEVEL,
        "include_examples": True,
        "provenance_preamble": False,
    },
    "temperature": {
        "temperature": 0.5,
        "thinking_level": BASELINE_THINKING_LEVEL,
        "include_examples": False,
        "provenance_preamble": False,
    },
    "cascaded": {
        "temperature": BASELINE_TEMPERATURE,
        "thinking_level": BASELINE_THINKING_LEVEL,
        # Cascaded uses its own build_comparative_content_parts()
        # and verify_comparative.md instruction, not the flags below
        "include_examples": False,
        "provenance_preamble": False,
    },
}


# ---------------------------------------------------------------------------
# Content building
# ---------------------------------------------------------------------------

def build_content_parts(
    crop_path: Path,
    *,
    include_examples: bool = False,
    provenance_preamble: bool = False,
) -> list:
    """
    Build content parts for a verifier Application Programming Interface
    (API) call.

    Part ordering:
        1. Provenance preamble (if set) — Experiment A
        2. Reference examples (images or text-only) — Experiment B toggles
           between image+text and text-only mode
        3. Classification prompt + candidate crop image

    Args:
        crop_path: Path to the candidate crop image.
        include_examples: Whether to include visual reference example
            images (True) or text-only descriptions (False).
        provenance_preamble: Whether to prepend the provenance context
            preamble informing the verifier of image-only provenance.

    Returns:
        List of Part objects for the API call.
    """
    from google.genai import types

    parts = []

    # (1) Provenance preamble (Experiment A)
    if provenance_preamble:
        parts.append(types.Part.from_text(text=PROVENANCE_PREAMBLE))

    # (2) Reference examples
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

    # (3) Candidate crop
    parts.append(types.Part.from_text(
        text="Now classify the candidate symbol at the centre of this crop:"
    ))
    with open(crop_path, "rb") as f:
        parts.append(types.Part.from_bytes(
            data=f.read(), mime_type="image/png"
        ))

    return parts


# ---------------------------------------------------------------------------
# Comparative content building (Experiment D)
# ---------------------------------------------------------------------------

def build_comparative_content_parts(crop_path: Path) -> list:
    """
    Build content parts for the comparative (second-stage) verifier.

    Shows 4 confirmed positive reference images with diagnostic labels,
    followed by a comparison prompt and the candidate crop. This is
    separate from build_content_parts() because the framing, examples
    (positive-only, 4 not 6), and prompt text are fundamentally different.

    Part ordering:
        1. Reference header text
        2–9. 4× (label text + reference image bytes)
        10. Comparison prompt / separator text
        11. Candidate crop image bytes
    Total: 11 parts.

    Args:
        crop_path: Path to the candidate crop image.

    Returns:
        List of Part objects for the API call.
    """
    from google.genai import types

    parts = []

    # (1) Reference header
    parts.append(types.Part.from_text(
        text="Confirmed burial mound reference examples for comparison:"
    ))

    # (2–9) 4× label + image pairs
    for ex in COMPARATIVE_EXAMPLES:
        img_path = EXAMPLES_DIR / ex["path"]
        parts.append(types.Part.from_text(text=ex["label"]))
        if img_path.exists():
            with open(img_path, "rb") as f:
                parts.append(types.Part.from_bytes(
                    data=f.read(), mime_type="image/png"
                ))

    # (10) Comparison prompt / separator
    parts.append(types.Part.from_text(
        text=(
            "Now compare the following candidate to the confirmed "
            "examples above. Assess each diagnostic feature "
            "(rays, shape, colour, gestalt):"
        )
    ))

    # (11) Candidate crop
    with open(crop_path, "rb") as f:
        parts.append(types.Part.from_bytes(
            data=f.read(), mime_type="image/png"
        ))

    return parts


# ---------------------------------------------------------------------------
# Candidate filtering (Experiment D)
# ---------------------------------------------------------------------------

def filter_passing_candidates(
    image_only_indices: list[int],
    candidates: list[dict],
    baseline_probs: dict[str, float | None],
    threshold: float,
) -> list[int]:
    """
    Return indices of image-only candidates that pass the first-stage
    verifier at a given probability threshold.

    A candidate passes if its baseline probability is not None and is
    greater than or equal to the threshold.

    Args:
        image_only_indices: Indices of image-only candidates in the
            full candidate list.
        candidates: Full candidate list from the manifest.
        baseline_probs: Baseline probability map (string keys).
        threshold: Minimum probability to pass the first stage.

    Returns:
        Subset of image_only_indices where baseline prob >= threshold.
    """
    passing = []
    for idx in image_only_indices:
        cid = str(candidates[idx]["candidate_id"])
        prob = baseline_probs.get(cid)
        if prob is not None and prob >= threshold:
            passing.append(idx)
    return passing


# ---------------------------------------------------------------------------
# Cascaded experiment runner (Experiment D)
# ---------------------------------------------------------------------------

def run_cascaded_experiment(
    client,
    model_name: str,
    candidates: list[dict],
    image_only_indices: list[int],
    baseline_probs: dict[str, float | None],
    first_stage_threshold: float,
) -> dict[str, float | None]:
    """
    Run the cascaded comparative verification experiment.

    Filters image-only candidates to those passing the first-stage
    adversarial verifier at the given threshold, then runs a second-
    stage comparative verifier on the passing subset. Non-passing
    candidates retain their baseline probabilities.

    Args:
        client: Google GenAI client instance.
        model_name: Resolved model identifier.
        candidates: Full candidate list from the manifest.
        image_only_indices: Indices of image-only candidates.
        baseline_probs: Baseline probability map (string keys).
        first_stage_threshold: Probability threshold for first-stage
            pass (default 0.11).

    Returns:
        Dict mapping candidate_id (str) → probability (float | None)
        for all 44 image-only candidates. Passing candidates get
        second-stage values; non-passing retain baseline values.
    """
    # Load comparative verifier instruction
    comparative_instruction = COMPARATIVE_INSTRUCTION_PATH.read_text(
        encoding="utf-8"
    )

    # Filter to passing candidates
    passing_indices = filter_passing_candidates(
        image_only_indices, candidates, baseline_probs,
        first_stage_threshold,
    )

    n_total = len(image_only_indices)
    n_passing = len(passing_indices)

    print("\nExperiment: cascaded (comparative second stage)")
    print(f"  Image-only candidates: {n_total}")
    print(f"  First-stage threshold: {first_stage_threshold}")
    print(f"  Passing first stage: {n_passing}")
    print(f"  Rejected by first stage: {n_total - n_passing}")
    print(f"  API calls (second stage only): {n_passing}")

    # Initialise output with baseline values for all 44
    probabilities: dict[str, float | None] = {}
    for idx in image_only_indices:
        cid = str(candidates[idx]["candidate_id"])
        probabilities[cid] = baseline_probs.get(cid)

    # Run second-stage comparative verifier on passing candidates
    n_success = 0
    n_fail = 0
    start_time = time.time()

    for seq, idx in enumerate(passing_indices, 1):
        c = candidates[idx]
        cid = str(c["candidate_id"])
        crop_path = CROPS_DIR / c["crop_file"]
        baseline_p = baseline_probs.get(cid)

        print(
            f"  [{seq}/{n_passing}] Candidate {cid} "
            f"(baseline p={baseline_p})...",
            end=" ",
        )

        if not crop_path.exists():
            print("SKIP (crop not found)")
            n_fail += 1
            continue

        # Build comparative content parts
        content_parts = build_comparative_content_parts(crop_path)

        result = call_verifier(
            client, model_name, comparative_instruction, crop_path,
            temperature=BASELINE_TEMPERATURE,
            thinking_level=BASELINE_THINKING_LEVEL,
            content_override=content_parts,
        )

        if result and "mound_probability" in result:
            prob = float(result["mound_probability"])
            probabilities[cid] = prob
            n_success += 1
            delta = prob - baseline_p if baseline_p is not None else 0
            print(f"p={prob:.2f} (Δ={delta:+.2f})")
        else:
            # Keep baseline value on failure
            n_fail += 1
            print("FAILED (keeping baseline)")

    elapsed = time.time() - start_time
    print(f"\n  Done in {elapsed:.0f}s — "
          f"{n_success} success, {n_fail} failed")

    return probabilities


# ---------------------------------------------------------------------------
# Verifier API call
# ---------------------------------------------------------------------------

def call_verifier(
    client,
    model_name: str,
    instruction_text: str,
    crop_path: Path,
    *,
    temperature: float = BASELINE_TEMPERATURE,
    thinking_level: str = BASELINE_THINKING_LEVEL,
    include_examples: bool = False,
    provenance_preamble: bool = False,
    content_override: list | None = None,
) -> dict | None:
    """
    Call the verifier on a single candidate crop image.

    Wraps content building, API call, JSON parsing, and retry logic
    into a single function parameterised by experiment-specific settings.

    Args:
        client: Google GenAI client instance.
        model_name: Resolved model identifier.
        instruction_text: Verifier system instruction text.
        crop_path: Path to the candidate crop image.
        temperature: Sampling temperature (0.0 = deterministic).
        thinking_level: Model thinking budget ("minimal" or "high").
        include_examples: Include visual reference example images.
        provenance_preamble: Prepend provenance context preamble.
        content_override: Pre-built content parts list. When provided,
            bypasses internal build_content_parts() call. Used by the
            cascaded experiment to pass comparative content.

    Returns:
        Parsed JSON response dict with mound_probability, or None
        on failure after exhausting retries.
    """
    from google.genai import types

    if content_override is not None:
        content_parts = content_override
    else:
        content_parts = build_content_parts(
            crop_path,
            include_examples=include_examples,
            provenance_preamble=provenance_preamble,
        )
    content = types.Content(parts=content_parts)

    gen_config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
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

    raw = ""
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
# Data loading helpers
# ---------------------------------------------------------------------------

def load_image_only_indices(union_geojson_path: Path) -> list[int]:
    """
    Load the union GeoJSON and return indices of image-only candidates.

    Args:
        union_geojson_path: Path to union_detections.geojson.

    Returns:
        List of integer indices into the feature array where
        source_tracks == ["track1-image"].
    """
    with open(union_geojson_path, encoding="utf-8") as f:
        union_geo = json.load(f)

    indices = []
    for i, feat in enumerate(union_geo["features"]):
        tracks = feat["properties"]["source_tracks"]
        if tracks == ["track1-image"]:
            indices.append(i)

    return indices


def load_candidates(manifest_path: Path) -> list[dict]:
    """
    Load the candidate manifest and return the candidates list.

    Args:
        manifest_path: Path to candidate_manifest.json.

    Returns:
        List of candidate dicts from the manifest.
    """
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest["candidates"]


# ---------------------------------------------------------------------------
# Temperature aggregation
# ---------------------------------------------------------------------------

def aggregate_temperature_passes(
    all_pass_probs: list[dict[str, float | None]],
) -> dict[str, float | None]:
    """
    Aggregate multiple temperature passes into mean probabilities.

    Filters out None values before computing the mean. If all passes
    returned None for a candidate, the mean is None.

    Args:
        all_pass_probs: List of per-pass probability dicts, each
            mapping candidate_id (str) → probability (float | None).

    Returns:
        Dict mapping candidate_id → mean probability (or None).
    """
    if not all_pass_probs:
        return {}

    # Collect all candidate IDs across passes
    all_ids = set()
    for pass_probs in all_pass_probs:
        all_ids.update(pass_probs.keys())

    means: dict[str, float | None] = {}
    for cid in sorted(all_ids):
        values = [
            pass_probs.get(cid)
            for pass_probs in all_pass_probs
        ]
        valid = [v for v in values if v is not None]
        if valid:
            means[cid] = statistics.mean(valid)
        else:
            means[cid] = None

    return means


# ---------------------------------------------------------------------------
# Experiment runner
# ---------------------------------------------------------------------------

def run_experiment(
    client,
    model_name: str,
    instruction_text: str,
    candidates: list[dict],
    image_only_indices: list[int],
    experiment: str,
    passes: int = 1,
) -> dict[str, float | None]:
    """
    Run a re-verification experiment on image-only candidates.

    Dispatches to call_verifier with experiment-specific kwargs. For the
    temperature experiment, iterates multiple passes per candidate and
    returns mean probabilities.

    Args:
        client: Google GenAI client instance.
        model_name: Resolved model identifier.
        instruction_text: Verifier system instruction text.
        candidates: Full candidate list from the manifest.
        image_only_indices: Indices of image-only candidates.
        experiment: Experiment name ("provenance", "examples", "temperature").
        passes: Number of passes per candidate (only >1 for temperature).

    Returns:
        Dict mapping candidate_id (str) → probability (float | None).
    """
    params = EXPERIMENT_PARAMS[experiment]
    n_total = len(image_only_indices)
    effective_passes = passes if experiment == "temperature" else 1

    print(f"\nExperiment: {experiment}")
    print(f"  Candidates: {n_total}")
    print(f"  Temperature: {params['temperature']}")
    print(f"  Include examples: {params['include_examples']}")
    print(f"  Provenance preamble: {params['provenance_preamble']}")
    print(f"  Passes: {effective_passes}")
    print(f"  Total API calls: {n_total * effective_passes}")

    if experiment == "temperature" and effective_passes > 1:
        return _run_temperature_experiment(
            client, model_name, instruction_text,
            candidates, image_only_indices, params, effective_passes,
        )

    # Single-pass experiments (A: provenance, B: examples)
    probabilities: dict[str, float | None] = {}
    n_success = 0
    n_fail = 0
    start_time = time.time()

    for seq, idx in enumerate(image_only_indices, 1):
        c = candidates[idx]
        cid = str(c["candidate_id"])
        crop_path = CROPS_DIR / c["crop_file"]

        print(
            f"  [{seq}/{n_total}] Candidate {cid} "
            f"({crop_path.name})...",
            end=" ",
        )

        if not crop_path.exists():
            print("SKIP (crop not found)")
            probabilities[cid] = None
            n_fail += 1
            continue

        result = call_verifier(
            client, model_name, instruction_text, crop_path,
            temperature=params["temperature"],
            thinking_level=params["thinking_level"],
            include_examples=params["include_examples"],
            provenance_preamble=params["provenance_preamble"],
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
    print(f"\n  Done in {elapsed:.0f}s — "
          f"{n_success} success, {n_fail} failed")

    return probabilities


def _run_temperature_experiment(
    client,
    model_name: str,
    instruction_text: str,
    candidates: list[dict],
    image_only_indices: list[int],
    params: dict,
    passes: int,
) -> dict[str, float | None]:
    """
    Run multi-pass temperature experiment and return mean probabilities.

    Also saves the per-pass raw data and prints per-candidate statistics
    (mean, median, min, max, std) to stdout.

    Args:
        client: Google GenAI client instance.
        model_name: Resolved model identifier.
        instruction_text: Verifier system instruction text.
        candidates: Full candidate list from the manifest.
        image_only_indices: Indices of image-only candidates.
        params: Experiment-specific parameter dict.
        passes: Number of passes per candidate.

    Returns:
        Dict mapping candidate_id (str) → mean probability (float | None).
    """
    n_total = len(image_only_indices)
    all_pass_probs: list[dict[str, float | None]] = []
    start_time = time.time()

    for pass_num in range(1, passes + 1):
        print(f"\n  --- Pass {pass_num}/{passes} ---")
        pass_probs: dict[str, float | None] = {}

        for seq, idx in enumerate(image_only_indices, 1):
            c = candidates[idx]
            cid = str(c["candidate_id"])
            crop_path = CROPS_DIR / c["crop_file"]

            if seq % 10 == 0 or seq == n_total:
                print(f"    [{seq}/{n_total}]", end=" ")

            if not crop_path.exists():
                pass_probs[cid] = None
                if seq % 10 == 0 or seq == n_total:
                    print("SKIP")
                continue

            result = call_verifier(
                client, model_name, instruction_text, crop_path,
                temperature=params["temperature"],
                thinking_level=params["thinking_level"],
                include_examples=params["include_examples"],
                provenance_preamble=params["provenance_preamble"],
            )

            if result and "mound_probability" in result:
                prob = float(result["mound_probability"])
                pass_probs[cid] = prob
                if seq % 10 == 0 or seq == n_total:
                    print(f"p={prob:.2f}")
            else:
                pass_probs[cid] = None
                if seq % 10 == 0 or seq == n_total:
                    print("FAILED")

        all_pass_probs.append(pass_probs)

    elapsed = time.time() - start_time

    # Save per-pass data
    all_passes_path = UNION_DIR / TEMPERATURE_ALL_PASSES_FILE
    with open(all_passes_path, "w", encoding="utf-8") as f:
        json.dump(
            {"passes": passes, "per_pass": all_pass_probs},
            f, indent=2,
        )
    print(f"\n  Per-pass data saved to: {all_passes_path}")

    # Aggregate to means
    means = aggregate_temperature_passes(all_pass_probs)

    # Print per-candidate statistics
    print(f"\n  Per-candidate statistics ({passes} passes):")
    print(f"  {'ID':<16} {'Mean':>6} {'Median':>6} "
          f"{'Min':>6} {'Max':>6} {'Std':>6}")
    print(f"  {'-'*16} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
    for cid in sorted(means.keys(), key=lambda x: int(x.split("_")[-1])
                       if "_" in x else int(x)):
        values = [
            pp.get(cid) for pp in all_pass_probs
            if pp.get(cid) is not None
        ]
        if values:
            mean_v = statistics.mean(values)
            median_v = statistics.median(values)
            min_v = min(values)
            max_v = max(values)
            std_v = statistics.stdev(values) if len(values) > 1 else 0.0
            print(f"  {cid:<16} {mean_v:>6.3f} {median_v:>6.3f} "
                  f"{min_v:>6.3f} {max_v:>6.3f} {std_v:>6.3f}")
        else:
            print(f"  {cid:<16}   —      —      —      —      —")

    print(f"\n  Done in {elapsed:.0f}s")

    return means


# ---------------------------------------------------------------------------
# Probability merging
# ---------------------------------------------------------------------------

def merge_probabilities(
    baseline_probs: dict[str, float | None],
    experiment_probs: dict[str, float | None],
) -> dict[str, float | None]:
    """
    Merge experiment probabilities into the baseline probability map.

    Copies all 184 baseline entries, then overwrites the 44 image-only
    candidate keys with values from the experiment. This produces a
    full probability map suitable for evaluate_union().

    Args:
        baseline_probs: Full probability map from the union experiment
            (184 entries, string keys).
        experiment_probs: Experiment probabilities for image-only
            candidates (44 entries, string keys).

    Returns:
        New dict with baseline values overwritten by experiment values
        where keys overlap.
    """
    merged = dict(baseline_probs)
    for cid, prob in experiment_probs.items():
        merged[cid] = prob
    return merged


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def run_evaluation(experiment_probs_path: Path) -> None:
    """
    Evaluate experiment probabilities against the baseline.

    Loads baseline and experiment probability files, merges them,
    runs a threshold sweep for both using evaluate_union(), and prints
    a comparison table showing F1, P, R, N, and threshold for baseline
    vs merged experiment results plus a delta row.

    Args:
        experiment_probs_path: Path to the experiment probability JSON
            file (44 entries for image-only candidates).
    """
    # Import evaluation functions from existing scripts
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from run_h2_pilot import (
        get_references_in_bounds,
        load_geojson,
    )
    from run_union_experiment import evaluate_union

    # Load inputs
    print("Loading data...")
    if not BASELINE_PROBS_PATH.exists():
        print(f"  ERROR: Baseline probabilities not found: "
              f"{BASELINE_PROBS_PATH}")
        sys.exit(1)

    with open(BASELINE_PROBS_PATH, encoding="utf-8") as f:
        baseline_probs = json.load(f)

    with open(experiment_probs_path, encoding="utf-8") as f:
        experiment_probs = json.load(f)

    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    union_geojson = load_geojson(UNION_GEOJSON_PATH)

    # Load ground truth
    refs_data = load_geojson(REFERENCES_PATH)
    bounds_data = load_geojson(BOUNDS_PATH)

    source_tiles = set()
    for feat in union_geojson.get("features", []):
        tile = feat.get("properties", {}).get("source_tile", "")
        if tile:
            source_tiles.add(tile)

    ref_coords = get_references_in_bounds(
        refs_data["features"], bounds_data["features"], source_tiles
    )
    print(f"  Reference mounds: {len(ref_coords)}")
    print(f"  Baseline entries: {len(baseline_probs)}")
    print(f"  Experiment entries: {len(experiment_probs)}")

    # Merge experiment into baseline
    merged_probs = merge_probabilities(baseline_probs, experiment_probs)
    n_changed = sum(
        1 for k in experiment_probs
        if baseline_probs.get(k) != experiment_probs[k]
    )
    print(f"  Changed entries: {n_changed}")

    # Generate thresholds (0.00 to 1.00 in 0.01 steps)
    thresholds = [i / 100 for i in range(101)]

    # Evaluate baseline
    print("\nRunning threshold sweep (baseline)...")
    baseline_results = evaluate_union(
        manifest=manifest,
        probabilities=baseline_probs,
        union_geojson=union_geojson,
        ref_coords=ref_coords,
        thresholds=thresholds,
    )

    # Evaluate merged
    print("Running threshold sweep (experiment)...")
    merged_results = evaluate_union(
        manifest=manifest,
        probabilities=merged_probs,
        union_geojson=union_geojson,
        ref_coords=ref_coords,
        thresholds=thresholds,
    )

    # Print comparison table
    bl_opt = baseline_results.get("optimal_result", {})
    ex_opt = merged_results.get("optimal_result", {})

    print(f"\n{'='*70}")
    print("EVALUATION COMPARISON")
    print(f"{'='*70}")
    print(f"\n  Experiment file: {experiment_probs_path.name}")
    print(f"  Reference mounds: {len(ref_coords)}")
    print()

    header = (f"  {'Configuration':<25} {'F1':>6} {'P':>6} "
              f"{'R':>6} {'N':>4} {'Threshold':>9}")
    print(header)
    print(f"  {'-'*25} {'-'*6} {'-'*6} {'-'*6} {'-'*4} {'-'*9}")

    # Baseline row
    bl_f1 = bl_opt.get("f1", 0)
    bl_p = bl_opt.get("precision", 0)
    bl_r = bl_opt.get("recall", 0)
    bl_n = bl_opt.get("n_kept", "?")
    bl_t = baseline_results.get("optimal_threshold", "?")
    print(f"  {'Baseline':<25} {bl_f1:>6.3f} {bl_p:>6.3f} "
          f"{bl_r:>6.3f} {bl_n:>4} {bl_t:>9}")

    # Experiment row
    ex_f1 = ex_opt.get("f1", 0)
    ex_p = ex_opt.get("precision", 0)
    ex_r = ex_opt.get("recall", 0)
    ex_n = ex_opt.get("n_kept", "?")
    ex_t = merged_results.get("optimal_threshold", "?")
    print(f"  {'Experiment':<25} {ex_f1:>6.3f} {ex_p:>6.3f} "
          f"{ex_r:>6.3f} {ex_n:>4} {ex_t:>9}")

    # Delta row
    d_f1 = ex_f1 - bl_f1
    d_p = ex_p - bl_p
    d_r = ex_r - bl_r
    print(f"  {'Delta':<25} {d_f1:>+6.3f} {d_p:>+6.3f} "
          f"{d_r:>+6.3f} {'':>4} {'':>9}")

    print()

    # Provenance breakdown at optimal thresholds
    bl_prov = baseline_results.get("provenance_breakdown", {})
    ex_prov = merged_results.get("provenance_breakdown", {})

    if bl_prov and ex_prov:
        print("  Provenance breakdown (image-only candidates):")
        bl_io = bl_prov.get("image-only", {})
        ex_io = ex_prov.get("image-only", {})
        print(f"    Baseline:   TP={bl_io.get('tp', '?')}, "
              f"FP={bl_io.get('fp', '?')}, "
              f"P={bl_io.get('precision', 0):.3f}")
        print(f"    Experiment: TP={ex_io.get('tp', '?')}, "
              f"FP={ex_io.get('fp', '?')}, "
              f"P={ex_io.get('precision', 0):.3f}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Unified image-only re-verification experiments (A–D)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Experiments:
    provenance  — prepend provenance preamble (image-only signal)
    examples    — include visual reference example images
    temperature — T=0.5 with multiple passes (default 3)
    cascaded    — two-stage: adversarial first stage, comparative second stage

Examples:
    python scripts/reverify_image_only_experiments.py --experiment provenance
    python scripts/reverify_image_only_experiments.py --experiment temperature --passes 5
    python scripts/reverify_image_only_experiments.py --experiment cascaded
    python scripts/reverify_image_only_experiments.py --experiment cascaded --first-stage-threshold 0.2
    python scripts/reverify_image_only_experiments.py --evaluate \\
        outputs/phase3d-union/verifier_adversarial_provenance_probabilities.json
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--experiment",
        choices=["provenance", "examples", "temperature", "cascaded"],
        help="Run a re-verification experiment on image-only candidates",
    )
    group.add_argument(
        "--evaluate",
        type=Path,
        metavar="PROBS_PATH",
        help=(
            "Evaluate experiment probabilities against the baseline "
            "(no API calls)"
        ),
    )

    parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help=(
            "Number of passes per candidate for the temperature "
            "experiment (default: 3)"
        ),
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        metavar="T",
        help=(
            "Override the default temperature for the experiment "
            "(e.g., --temperature 1.0)"
        ),
    )
    parser.add_argument(
        "--first-stage-threshold",
        type=float,
        default=0.11,
        metavar="T",
        help=(
            "Probability threshold for the first-stage adversarial "
            "verifier in the cascaded experiment (default: 0.11)"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview experiment setup without making API calls",
    )

    return parser


def main() -> None:
    """Entry point for the unified re-verification experiments."""
    parser = build_parser()
    args = parser.parse_args()

    # --- Evaluate mode (local only, no API calls) ---
    if args.evaluate:
        if not args.evaluate.exists():
            print(f"ERROR: File not found: {args.evaluate}")
            sys.exit(1)
        run_evaluation(args.evaluate)
        return

    # --- Experiment mode ---
    experiment = args.experiment

    # Apply temperature override if provided
    if args.temperature is not None:
        EXPERIMENT_PARAMS[experiment]["temperature"] = args.temperature

    # Load data
    image_only_indices = load_image_only_indices(UNION_GEOJSON_PATH)
    candidates = load_candidates(MANIFEST_PATH)

    # Cascaded experiment uses comparative instruction; others use
    # the adversarial instruction
    if experiment == "cascaded":
        instruction_text = COMPARATIVE_INSTRUCTION_PATH.read_text(
            encoding="utf-8"
        )
    else:
        instruction_text = INSTRUCTION_PATH.read_text(encoding="utf-8")

    print(f"Image-only candidates: {len(image_only_indices)}")
    print(f"Total candidates in manifest: {len(candidates)}")

    output_path = UNION_DIR / OUTPUT_FILES[experiment]

    if args.dry_run:
        if experiment == "cascaded":
            # Cascaded dry-run: show passing candidates and their
            # baseline probabilities
            with open(BASELINE_PROBS_PATH, encoding="utf-8") as f:
                baseline_probs = json.load(f)

            passing = filter_passing_candidates(
                image_only_indices, candidates, baseline_probs,
                args.first_stage_threshold,
            )

            print("\n[DRY RUN] Experiment: cascaded")
            print(f"  Verifier instruction: "
                  f"{COMPARATIVE_INSTRUCTION_PATH.name}")
            print(f"  First-stage threshold: "
                  f"{args.first_stage_threshold}")
            print(f"  Passing first stage: {len(passing)}")
            print(f"  Rejected by first stage: "
                  f"{len(image_only_indices) - len(passing)}")
            print(f"  API calls (second stage): {len(passing)}")
            print("\n  Would verify these candidates:")
            for idx in passing:
                c = candidates[idx]
                cid = str(c["candidate_id"])
                bp = baseline_probs.get(cid)
                print(f"    ID {cid}: baseline p={bp}")
            print(f"\n  Output: {output_path}")
        else:
            params = EXPERIMENT_PARAMS[experiment]
            effective_passes = (
                args.passes if experiment == "temperature" else 1
            )

            print(f"\n[DRY RUN] Experiment: {experiment}")
            print(f"  Verifier instruction: {INSTRUCTION_PATH.name}")
            print(f"  Temperature: {params['temperature']}")
            print(f"  Include examples: {params['include_examples']}")
            print(f"  Provenance preamble: "
                  f"{params['provenance_preamble']}")
            print(f"  Passes: {effective_passes}")
            print(f"  API calls: "
                  f"{len(image_only_indices) * effective_passes}")
            print("\n  Would verify these candidates:")
            for idx in image_only_indices[:5]:
                c = candidates[idx]
                crop_path = CROPS_DIR / c["crop_file"]
                print(f"    ID {c['candidate_id']}: {crop_path.name} "
                      f"(exists={crop_path.exists()})")
            if len(image_only_indices) > 5:
                print(
                    f"    ... and "
                    f"{len(image_only_indices) - 5} more"
                )
            print(f"\n  Output: {output_path}")
        return

    # Initialise Gemini API client
    import os
    from google import genai

    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set")
        sys.exit(1)

    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": API_VERSION},
    )

    # Resolve model name
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from run_h2_pilot import resolve_model_name
    model_name = resolve_model_name(client, MODEL_NAME)
    print(f"Model: {model_name}")

    # Run experiment — cascaded uses its own runner
    if experiment == "cascaded":
        with open(BASELINE_PROBS_PATH, encoding="utf-8") as f:
            baseline_probs = json.load(f)

        probabilities = run_cascaded_experiment(
            client=client,
            model_name=model_name,
            candidates=candidates,
            image_only_indices=image_only_indices,
            baseline_probs=baseline_probs,
            first_stage_threshold=args.first_stage_threshold,
        )
    else:
        probabilities = run_experiment(
            client=client,
            model_name=model_name,
            instruction_text=instruction_text,
            candidates=candidates,
            image_only_indices=image_only_indices,
            experiment=experiment,
            passes=args.passes,
        )

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(probabilities, f, indent=2)
    print(f"\nSaved to: {output_path}")

    # Quick distribution summary
    valid_probs = [v for v in probabilities.values() if v is not None]
    if valid_probs:
        high = sum(1 for p in valid_probs if p >= 0.5)
        low = sum(1 for p in valid_probs if p < 0.5)
        print(f"Distribution: {high} high (≥0.5), {low} low (<0.5)")


if __name__ == "__main__":
    main()
