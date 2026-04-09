"""
Verifier Library (Dual-Mode)
============================

Description:
    Shared library for the verifier stage of the Proposer-Verifier (PV)
    pipeline. Supports both Gemini Batch API and real-time API execution
    through an intermediate representation (IR) for prompt construction.

    Content is built as mode-agnostic ``TextItem`` / ``ImageItem`` objects,
    then serialised to either:

    - JSONL-compatible dicts (batch path) via ``content_items_to_batch_parts``
    - google-genai SDK ``types.Part`` objects (real-time) via
      ``content_items_to_sdk_parts``

    Reuses ``lib_batch_api.py`` for batch lifecycle and image encoding.

Verifier Response Schema:
    The verifier returns JSON (JavaScript Object Notation) with::

        {
            "best_alternative": "Strongest non-mound interpretation",
            "alternative_evidence": "Visual features supporting it",
            "reasoning": "Why accepted/rejected",
            "mound_probability": 0.85
        }

Usage::

    from scripts.lib_verifier import (
        TextItem, ImageItem,
        build_reference_items,
        build_candidate_content,
        content_items_to_batch_parts,
        content_items_to_sdk_parts,
        build_verifier_jsonl,
        parse_verifier_results,
        aggregate_consensus_votes,
        verify_candidate_realtime,
    )

Created: 2026-03-19
Updated: 2026-03-20 — Dual-mode refactor with shared IR layer
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import dataclasses
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Re-use encoding utilities from the proposer batch module
from scripts.lib_batch_api import (
    _encode_image_base64,
    _mime_type_for,
)

# Project paths
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_EXAMPLES_DIR = _PROJECT_ROOT / "inputs" / "examples"
_INSTRUCTIONS_DIR = _PROJECT_ROOT / "prompts" / "system-instructions"

# Retry configuration for real-time API calls
_MAX_RETRIES = 3
_RETRY_BACKOFF_SECONDS = [2, 4, 8]


# =========================================================================
# Intermediate Representation (IR) Types
# =========================================================================


@dataclasses.dataclass(frozen=True, slots=True)
class TextItem:
    """A text content part in the intermediate representation.

    Frozen and slotted for immutability and thread safety.
    """

    text: str


@dataclasses.dataclass(frozen=True, slots=True)
class ImageItem:
    """An image file reference in the intermediate representation.

    The image is loaded lazily — only when serialised for a specific
    mode (base64 for batch, binary bytes for real-time).

    Frozen and slotted for immutability and thread safety.
    """

    path: Path


# Type alias for content item lists
ContentItems = list[TextItem | ImageItem]


# =========================================================================
# Serialisers
# =========================================================================


def content_items_to_batch_parts(items: ContentItems) -> list[dict]:
    """Convert IR content items to JSONL-compatible dicts.

    ``TextItem`` → ``{"text": "..."}``
    ``ImageItem`` → ``{"inline_data": {"mime_type": "...", "data": "base64..."}}``

    Args:
        items: List of IR content items.

    Returns:
        List of dicts suitable for Gemini Batch API JSONL serialisation.
    """
    parts: list[dict] = []
    for item in items:
        if isinstance(item, TextItem):
            parts.append({"text": item.text})
        elif isinstance(item, ImageItem):
            parts.append({
                "inline_data": {
                    "mime_type": _mime_type_for(item.path),
                    "data": _encode_image_base64(item.path),
                },
            })
        else:
            raise TypeError(f"Unknown content item type: {type(item)}")
    return parts


def content_items_to_sdk_parts(items: ContentItems) -> list:
    """Convert IR content items to google-genai SDK Part objects.

    ``TextItem`` → ``types.Part.from_text(text="...")``
    ``ImageItem`` → ``types.Part.from_bytes(data=bytes, mime_type="...")``

    The google-genai SDK import is deferred so batch-only usage does not
    require the SDK to be installed.

    Args:
        items: List of IR content items.

    Returns:
        List of ``google.genai.types.Part`` objects for real-time API calls.
    """
    from google.genai import types

    parts: list[types.Part] = []
    for item in items:
        if isinstance(item, TextItem):
            parts.append(types.Part.from_text(text=item.text))
        elif isinstance(item, ImageItem):
            with open(item.path, "rb") as f:
                image_bytes = f.read()
            parts.append(types.Part.from_bytes(
                data=image_bytes,
                mime_type=_mime_type_for(item.path),
            ))
        else:
            raise TypeError(f"Unknown content item type: {type(item)}")
    return parts


# =========================================================================
# Generation Config Helpers
# =========================================================================


def build_generation_config(
    config: dict,
    temperature_override: float | None = None,
) -> dict[str, Any]:
    """Build generation config as a plain dict (for batch JSONL).

    Includes temperature, max_output_tokens, response_mime_type, and
    thinking_config. Does NOT include safety_settings (Batch API
    rejects them).

    Args:
        config: Verifier config dict.
        temperature_override: Override temperature from config.

    Returns:
        Generation config dict suitable for batch JSONL or conversion
        to SDK ``GenerateContentConfig``.
    """
    temperature = (
        temperature_override
        if temperature_override is not None
        else config.get("temperature", 0.0)
    )

    gen_config: dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": config.get("max_output_tokens", 8192),
        "response_mime_type": "application/json",
    }

    thinking_level = config.get("thinking_level")
    if thinking_level:
        gen_config["thinking_config"] = {
            "thinking_level": thinking_level.upper(),
        }

    return gen_config


def gen_config_to_sdk(
    config_dict: dict[str, Any],
    system_instruction: str,
    service_tier: str | None = None,
) -> Any:
    """Convert a plain-dict generation config to SDK GenerateContentConfig.

    Adds ``system_instruction`` and ``safety_settings`` (which the batch
    path cannot include). Converts ``thinking_config`` dict to a
    ``ThinkingConfig`` object.

    The google-genai SDK import is deferred so batch-only usage does not
    require the SDK to be installed.

    Args:
        config_dict: Generation config dict from ``build_generation_config()``.
        system_instruction: System instruction text.

    Returns:
        ``google.genai.types.GenerateContentConfig`` for real-time API calls.
    """
    from google.genai import types

    # Convert thinking config dict to SDK object
    thinking_config = None
    if "thinking_config" in config_dict:
        thinking_config = types.ThinkingConfig(
            thinking_level=config_dict["thinking_config"]["thinking_level"],
        )

    # Safety settings — disabled for archaeological/neutral content.
    # Batch API rejects these, so they are real-time only.
    safety_settings = [
        types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF",
        ),
    ]

    return types.GenerateContentConfig(
        temperature=config_dict["temperature"],
        max_output_tokens=config_dict["max_output_tokens"],
        response_mime_type=config_dict["response_mime_type"],
        thinking_config=thinking_config,
        system_instruction=system_instruction,
        safety_settings=safety_settings,
        service_tier=service_tier,
    )


# =========================================================================
# Shared Prompt Construction
# =========================================================================


def load_system_instruction(config: dict) -> str:
    """Load verifier system instruction text from file.

    Args:
        config: Verifier config dict with ``instruction_file`` key.

    Returns:
        System instruction text, or empty string if not found.
    """
    instruction_file = config.get("instruction_file", "")
    if not instruction_file:
        return ""
    path = _INSTRUCTIONS_DIR / instruction_file
    if not path.exists():
        logger.warning("Instruction file not found: %s", path)
        return ""
    return path.read_text()


def build_reference_items(config: dict) -> ContentItems:
    """Build reference example items as IR for a verifier prompt.

    Handles both image-using examples (``config["examples"]``) and
    text-only labels (``config["text_only_labels"]``), which are
    mutually exclusive. Mirrors the logic previously duplicated in
    ``5_verify_crops.py:construct_verifier_prompt()`` and the old
    ``_build_verifier_reference_parts()``.

    Args:
        config: Verifier config dict.

    Returns:
        List of IR content items for reference examples.
    """
    items: ContentItems = []

    # Text-only labels (mutually exclusive with image examples)
    text_labels = config.get("text_only_labels", [])
    if text_labels:
        label_lines = "\n".join(f"- {lbl}" for lbl in text_labels)
        items.append(TextItem(
            text=f"Reference examples (text descriptions only):\n"
                 f"{label_lines}",
        ))
        return items

    # Image examples
    examples = config.get("examples", [])
    if examples:
        items.append(TextItem(text="Reference examples for comparison:"))

    for ex in examples:
        img_path = _EXAMPLES_DIR / ex["path"]
        if not img_path.exists():
            logger.warning("Missing reference image: %s", img_path)
            continue
        items.append(TextItem(text=f"Example: {ex['label']}"))
        items.append(ImageItem(path=img_path))

    return items


def build_candidate_content(
    candidate: dict,
    config: dict,
    crops_base_dir: Path,
    reference_items: ContentItems | None = None,
) -> ContentItems:
    """Build complete prompt IR for one candidate.

    Combines reference examples + crop label + crop image into a
    single content item list. The ``reference_items`` can be pre-built
    (via ``build_reference_items``) and shared across candidates.

    Args:
        candidate: Candidate dict from manifest with ``crop_file``
            and ``candidate_id``.
        config: Verifier config dict.
        crops_base_dir: Base directory for resolving ``crop_file`` paths.
        reference_items: Pre-built reference items (optional; built
            from config if not provided).

    Returns:
        List of IR content items for the complete prompt.

    Raises:
        FileNotFoundError: If the crop file does not exist.
    """
    if reference_items is None:
        reference_items = build_reference_items(config)

    crop_label = config.get(
        "crop_label",
        "Now classify the candidate symbol at the centre of this crop:",
    )

    crop_path = crops_base_dir / candidate["crop_file"]
    if not crop_path.exists():
        raise FileNotFoundError(
            f"Crop file not found: {crop_path} "
            f"(candidate {candidate['candidate_id']})"
        )

    # Assemble: references + crop label + crop image
    items: ContentItems = list(reference_items)
    items.append(TextItem(text=crop_label))
    items.append(ImageItem(path=crop_path))

    return items


def _resolve_crop_path(
    candidate: dict,
    crops_base_dir: Path,
) -> Path | None:
    """Resolve crop file path for a candidate, with fallback.

    Args:
        candidate: Candidate dict from manifest.
        crops_base_dir: Base directory for crop files.

    Returns:
        Resolved crop path, or None if not found.
    """
    crop_path = crops_base_dir / candidate["crop_file"]
    if crop_path.exists():
        return crop_path

    logger.warning(
        "Crop file not found: %s (candidate %s)",
        candidate["crop_file"],
        candidate["candidate_id"],
    )
    return None


# =========================================================================
# Batch JSONL Construction (uses IR internally)
# =========================================================================


def build_verifier_jsonl(
    manifest: dict,
    config: dict,
    output_path: Path,
    crops_base_dir: Path,
    temperature_override: float | None = None,
    iteration_suffix: str = "",
) -> int:
    """Build a JSONL file for batch verifier submission.

    Each line contains one candidate with reference examples, crop image,
    system instruction, and generation config. Prompt content is built
    via the shared IR layer.

    Args:
        manifest: Candidate manifest dict (from ``extract_candidates.py``)
            with ``candidates`` list.
        config: Verifier config dict (e.g., ``verify_adversarial.json``).
        output_path: Path to write the JSONL file.
        crops_base_dir: Base directory for resolving crop file paths.
        temperature_override: Override temperature from config. Used for
            consensus voting where T > 0 is needed.
        iteration_suffix: Suffix appended to candidate keys for consensus
            (e.g., ``"_iter3"``). Empty for single-pass.

    Returns:
        Number of lines written.
    """
    system_instruction = load_system_instruction(config)
    reference_items = build_reference_items(config)
    gen_config = build_generation_config(config, temperature_override)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0

    with open(output_path, "w") as f:
        for candidate in manifest.get("candidates", []):
            # Build IR and serialise to batch parts — skip candidates
            # with missing crop files rather than crashing mid-write
            try:
                items = build_candidate_content(
                    candidate, config, crops_base_dir, reference_items,
                )
            except FileNotFoundError as e:
                logger.warning("%s", e)
                continue
            parts = content_items_to_batch_parts(items)

            candidate_id = candidate["candidate_id"]
            key = f"candidate_{candidate_id:05d}{iteration_suffix}"

            line = {
                "key": key,
                "request": {
                    "contents": [{
                        "parts": parts,
                        "role": "user",
                    }],
                    "system_instruction": {
                        "parts": [{"text": system_instruction}],
                    },
                    "generation_config": gen_config,
                },
            }

            f.write(json.dumps(line) + "\n")
            n_written += 1

    logger.info(
        "Built verifier JSONL: %d lines (%s)", n_written, output_path,
    )
    return n_written


def build_verifier_jsonl_consensus(
    manifest: dict,
    config: dict,
    output_path: Path,
    crops_base_dir: Path,
    iterations: int = 5,
    temperature: float = 0.7,
) -> int:
    """Build JSONL with N copies per candidate for consensus voting.

    Each candidate is emitted ``iterations`` times with unique keys
    (``candidate_00042_iter1`` through ``candidate_00042_iter5``).
    Temperature must be > 0 for consensus to produce variation.

    Args:
        manifest: Candidate manifest dict.
        config: Verifier config dict.
        output_path: Path to write the JSONL file.
        crops_base_dir: Base directory for resolving crop file paths.
        iterations: Number of verifier passes per candidate.
        temperature: Temperature for consensus (must be > 0).

    Returns:
        Total number of lines written (candidates × iterations).
    """
    if temperature == 0.0:
        logger.warning(
            "Consensus with T=0.0 will produce identical passes — "
            "consider T > 0 for meaningful consensus voting.",
        )

    system_instruction = load_system_instruction(config)
    reference_items = build_reference_items(config)
    gen_config = build_generation_config(config, temperature)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0

    with open(output_path, "w") as f:
        for candidate in manifest.get("candidates", []):
            # Build IR and serialise once per candidate — skip
            # candidates with missing crop files
            try:
                items = build_candidate_content(
                    candidate, config, crops_base_dir, reference_items,
                )
            except FileNotFoundError as e:
                logger.warning("%s", e)
                continue
            parts = content_items_to_batch_parts(items)
            candidate_id = candidate["candidate_id"]

            # Emit N copies with unique keys
            for iter_n in range(1, iterations + 1):
                key = f"candidate_{candidate_id:05d}_iter{iter_n}"
                line = {
                    "key": key,
                    "request": {
                        "contents": [{
                            "parts": parts,
                            "role": "user",
                        }],
                        "system_instruction": {
                            "parts": [{"text": system_instruction}],
                        },
                        "generation_config": gen_config,
                    },
                }
                f.write(json.dumps(line) + "\n")
                n_written += 1

    logger.info(
        "Built consensus verifier JSONL: %d lines "
        "(%d candidates × %d iterations, T=%.1f, %s)",
        n_written, len(manifest.get("candidates", [])),
        iterations, temperature, output_path,
    )
    return n_written


def build_verifier_jsonl_multiscale(
    manifest_small: dict,
    manifest_large: dict,
    config: dict,
    output_path: Path,
    crops_base_dir_small: Path,
    crops_base_dir_large: Path,
) -> int:
    """Build JSONL with two crop scales per candidate in one request.

    Each JSONL line contains both a small-scale (e.g., 75×75) and
    large-scale (e.g., 150×150) crop of the same candidate, enabling
    the model to assess at both detail and context levels.

    This function builds a custom IR per candidate rather than using
    ``build_candidate_content()``, because the multi-scale prompt has
    a different structure (two images with distinct labels).

    Args:
        manifest_small: Candidate manifest for smaller crops (e.g., 75px).
        manifest_large: Candidate manifest for larger crops (e.g., 150px).
        config: Verifier config dict.
        output_path: Path to write the JSONL file.
        crops_base_dir_small: Base directory for small crop files.
        crops_base_dir_large: Base directory for large crop files.

    Returns:
        Number of lines written.
    """
    system_instruction = load_system_instruction(config)
    reference_items = build_reference_items(config)
    gen_config = build_generation_config(config)

    # Build lookup for large crops by candidate_id
    large_by_id = {
        c["candidate_id"]: c for c in manifest_large.get("candidates", [])
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0

    with open(output_path, "w") as f:
        for candidate in manifest_small.get("candidates", []):
            cid = candidate["candidate_id"]
            large_candidate = large_by_id.get(cid)
            if large_candidate is None:
                logger.warning(
                    "No matching large crop for candidate %s", cid,
                )
                continue

            small_path = _resolve_crop_path(candidate, crops_base_dir_small)
            large_path = _resolve_crop_path(
                large_candidate, crops_base_dir_large,
            )
            if small_path is None or large_path is None:
                continue

            # Build custom multi-scale IR
            items: ContentItems = list(reference_items)
            items.append(TextItem(
                text="Detail view (close-up of candidate symbol):",
            ))
            items.append(ImageItem(path=small_path))
            items.append(TextItem(
                text="Context view (surrounding map features):",
            ))
            items.append(ImageItem(path=large_path))
            items.append(TextItem(
                text="Now classify the candidate symbol shown "
                     "at the centre of both views:",
            ))

            parts = content_items_to_batch_parts(items)

            key = f"candidate_{cid:05d}"
            line = {
                "key": key,
                "request": {
                    "contents": [{
                        "parts": parts,
                        "role": "user",
                    }],
                    "system_instruction": {
                        "parts": [{"text": system_instruction}],
                    },
                    "generation_config": gen_config,
                },
            }
            f.write(json.dumps(line) + "\n")
            n_written += 1

    logger.info(
        "Built multi-scale verifier JSONL: %d lines (%s)",
        n_written, output_path,
    )
    return n_written


# =========================================================================
# Real-Time Verification
# =========================================================================


def verify_candidate_realtime(
    candidate: dict,
    reference_items: ContentItems,
    client: Any,
    model_name: str,
    gen_config: Any,
    config: dict,
    crops_base_dir: Path,
    iterations: int = 1,
    candidate_id_str: str = "",
) -> tuple[dict[str, dict], list]:
    """Verify a single candidate via the real-time API.

    Builds the prompt IR, serialises to SDK parts, calls
    ``generate_content()``, and parses the JSON response. Supports
    multiple iterations for consensus voting.

    Designed to be called from within a ``ThreadPoolExecutor`` worker.
    The ``client`` object is thread-safe (as demonstrated by
    ``5_verify_crops.py``).

    Args:
        candidate: Candidate dict from manifest.
        reference_items: Pre-built reference IR items (shared across
            candidates for efficiency).
        client: Initialised ``google.genai.Client``.
        model_name: Resolved model name (e.g., ``"gemini-3-flash"``).
        gen_config: SDK ``GenerateContentConfig``.
        config: Verifier config dict.
        crops_base_dir: Base directory for crop files.
        iterations: Number of verification passes (1 = single, >1 = consensus).
        candidate_id_str: Human-readable ID for logging (e.g., ``"cand_0042"``).

    Returns:
        Tuple of:
        - Dict mapping iteration keys (e.g., ``"candidate_00042_iter1"``)
          to parsed result dicts with ``mound_probability``, ``reasoning``,
          etc. Empty dict if all iterations failed.
        - List of ``LLMResponseMetadata`` objects (one per API call).
    """
    from google.genai import types  # noqa: F811 — deferred import

    cid = candidate["candidate_id"]
    if not candidate_id_str:
        candidate_id_str = f"cand_{cid:04d}"

    # Build prompt content via shared IR
    try:
        items = build_candidate_content(
            candidate, config, crops_base_dir, reference_items,
        )
    except FileNotFoundError as e:
        logger.warning("Skipping candidate %s: %s", cid, e)
        return {}, []

    sdk_parts = content_items_to_sdk_parts(items)
    content = types.Content(parts=sdk_parts)

    results: dict[str, dict] = {}
    metadata_list: list = []

    for iter_num in range(1, iterations + 1):
        if iterations > 1:
            iter_key = f"candidate_{cid:05d}_iter{iter_num}"
        else:
            iter_key = f"candidate_{cid:05d}"

        iteration_id = f"{candidate_id_str}_iter{iter_num}"
        parsed = _call_verifier_api(
            client=client,
            model_name=model_name,
            content=content,
            gen_config=gen_config,
            iteration_id=iteration_id,
            metadata_list=metadata_list,
        )

        if parsed is not None:
            results[iter_key] = parsed

    return results, metadata_list


def _call_verifier_api(
    client: Any,
    model_name: str,
    content: Any,
    gen_config: Any,
    iteration_id: str,
    metadata_list: list,
) -> dict | None:
    """Make a single verifier API call with retry logic.

    Retries up to ``_MAX_RETRIES`` times with exponential backoff on
    transient API errors and JSON parse failures.

    Args:
        client: Initialised ``google.genai.Client``.
        model_name: Resolved model name.
        content: SDK ``Content`` object with prompt parts.
        gen_config: SDK ``GenerateContentConfig``.
        iteration_id: ID for metadata tracking.
        metadata_list: Mutable list to append metadata to.

    Returns:
        Parsed result dict, or None if all retries failed.
    """
    from scripts.lib_llm_metadata import (
        extract_gemini_metadata,
        create_error_metadata,
        LLMProvider,
    )

    for attempt in range(1, _MAX_RETRIES + 1):
        request_start = datetime.now(timezone.utc)
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=content,
                config=gen_config,
            )

            # Track metadata before attempting to parse text —
            # response.text can raise ValueError on safety-blocked or
            # empty responses, so we capture metadata first.
            response_metadata = extract_gemini_metadata(
                response=response,
                request_start=request_start,
                model_requested=model_name,
                item_id=iteration_id,
                attempt=attempt,
            )
            metadata_list.append(response_metadata)

            # Access response text — raises ValueError if safety-blocked
            # or no candidates returned. Handle this distinctly from
            # transient API errors: safety blocks are deterministic and
            # should not be retried.
            try:
                txt = response.text
            except ValueError as e:
                response_metadata.parse_success = False
                response_metadata.parse_error = f"BLOCKED: {e}"
                logger.warning(
                    "%s attempt %d: response blocked or empty (%s) — "
                    "not retrying (deterministic)",
                    iteration_id, attempt, e,
                )
                return None

            if txt is None:
                response_metadata.parse_success = False
                response_metadata.parse_error = "EMPTY_RESPONSE"
                logger.warning(
                    "%s attempt %d: response.text is None — "
                    "not retrying",
                    iteration_id, attempt,
                )
                return None

            # Parse JSON response
            txt = txt.replace("```json", "").replace("```", "").strip()
            data = json.loads(txt)

            return {
                "mound_probability": float(
                    data.get("mound_probability", 0.0),
                ),
                "reasoning": data.get("reasoning", ""),
                "best_alternative": data.get("best_alternative", ""),
                "alternative_evidence": data.get(
                    "alternative_evidence", "",
                ),
            }

        except json.JSONDecodeError as e:
            # Metadata already tracked above; mark parse failure
            response_metadata.parse_success = False
            response_metadata.parse_error = str(e)

            if attempt < _MAX_RETRIES:
                backoff = _RETRY_BACKOFF_SECONDS[attempt - 1]
                logger.warning(
                    "%s attempt %d: JSON parse error (%s), "
                    "retrying in %ds",
                    iteration_id, attempt, e, backoff,
                )
                time.sleep(backoff)
            else:
                logger.warning(
                    "%s: JSON parse failed after %d attempts: %s",
                    iteration_id, _MAX_RETRIES, e,
                )
                return None

        except Exception as e:
            # Track error metadata
            error_metadata = create_error_metadata(
                error=e,
                request_start=request_start,
                provider=LLMProvider.GEMINI.value,
                model_requested=model_name,
                item_id=iteration_id,
                attempt=attempt,
            )
            metadata_list.append(error_metadata)

            if attempt < _MAX_RETRIES:
                backoff = _RETRY_BACKOFF_SECONDS[attempt - 1]
                logger.warning(
                    "%s attempt %d: API error (%s), retrying in %ds",
                    iteration_id, attempt, e, backoff,
                )
                time.sleep(backoff)
            else:
                logger.warning(
                    "%s: API call failed after %d attempts: %s",
                    iteration_id, _MAX_RETRIES, e,
                )
                return None

    return None  # Should not reach here, but satisfies type checker


# =========================================================================
# Response Parsing (unchanged from original)
# =========================================================================


def parse_verifier_results(
    matched_results: dict[str, dict],
) -> dict[str, dict]:
    """Parse verifier batch results into probability scores.

    Extracts ``mound_probability`` and ``reasoning`` from each batch
    response line. The batch response wraps the model's JSON output in
    a ``response.candidates[0].content.parts[0].text`` structure.

    Args:
        matched_results: Dictionary mapping candidate key to batch
            response dict (from ``lib_batch_api.retrieve_batch_results``
            + ``validate_batch_results``).

    Returns:
        Dictionary mapping candidate key to parsed result dict with
        ``mound_probability``, ``reasoning``, ``best_alternative``,
        and ``alternative_evidence`` fields.
    """
    parsed: dict[str, dict] = {}

    for key, result in matched_results.items():
        try:
            # Navigate batch response structure
            candidates = result.get("response", {}).get("candidates", [])
            if not candidates:
                logger.warning("No candidates in response for %s", key)
                continue

            text = candidates[0].get("content", {}).get(
                "parts", [{}],
            )[0].get("text", "")

            # Clean up markdown code fences if present
            text = text.replace("```json", "").replace("```", "").strip()

            data = json.loads(text)
            parsed[key] = {
                "mound_probability": float(
                    data.get("mound_probability", 0.0),
                ),
                "reasoning": data.get("reasoning", ""),
                "best_alternative": data.get("best_alternative", ""),
                "alternative_evidence": data.get(
                    "alternative_evidence", "",
                ),
            }
        except (json.JSONDecodeError, ValueError, KeyError, IndexError) as e:
            logger.warning(
                "Failed to parse verifier result for %s: %s", key, e,
            )
            parsed[key] = {
                "mound_probability": 0.0,
                "reasoning": f"PARSE_ERROR: {e}",
                "best_alternative": "",
                "alternative_evidence": "",
            }

    return parsed


def aggregate_consensus_votes(
    parsed_results: dict[str, dict],
    threshold: float = 0.5,
) -> dict[int, dict]:
    """Aggregate consensus voting results across iterations.

    Groups parsed results by candidate ID (extracted from keys like
    ``candidate_00042_iter3``), computes vote count and mean probability.

    Args:
        parsed_results: Dictionary mapping iteration keys to parsed
            result dicts (from ``parse_verifier_results`` or
            ``verify_candidate_realtime``).
        threshold: Probability threshold for counting a vote as
            positive (default 0.5).

    Returns:
        Dictionary mapping candidate ID (int) to aggregated result dict
        with ``vote_count``, ``total_iterations``, ``mean_probability``,
        ``min_probability``, ``max_probability``, and per-iteration
        ``iterations`` list.
    """
    # Group by candidate ID
    candidates: dict[int, list[tuple[str, dict]]] = {}
    for key, result in parsed_results.items():
        # Parse candidate ID from key:
        # "candidate_00042_iter3" or "candidate_00042"
        parts = key.split("_")
        try:
            cid = int(parts[1])
        except (IndexError, ValueError):
            logger.warning("Cannot parse candidate ID from key: %s", key)
            continue
        candidates.setdefault(cid, []).append((key, result))

    # Aggregate
    aggregated: dict[int, dict] = {}
    for cid, iteration_results in sorted(candidates.items()):
        probs = [r["mound_probability"] for _, r in iteration_results]
        votes = sum(1 for p in probs if p >= threshold)

        aggregated[cid] = {
            "candidate_id": cid,
            "vote_count": votes,
            "total_iterations": len(iteration_results),
            "mean_probability": (
                sum(probs) / len(probs) if probs else 0.0
            ),
            "min_probability": min(probs) if probs else 0.0,
            "max_probability": max(probs) if probs else 0.0,
            "iterations": [
                {
                    "key": key,
                    "mound_probability": r["mound_probability"],
                    "reasoning": r.get("reasoning", ""),
                }
                for key, r in iteration_results
            ],
        }

    return aggregated
