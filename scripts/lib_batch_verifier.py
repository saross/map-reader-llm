"""
Batch API Verifier Module
=========================

Description:
    Builds JSONL request files for the verifier stage of the Proposer-Verifier
    (PV) pipeline using the Gemini Batch API. Each JSONL line contains one
    candidate crop image with reference examples and the verifier system
    instruction.

    Reuses ``lib_batch_api.py`` for batch lifecycle (upload, submit, poll,
    retrieve). This module handles only JSONL construction and response
    parsing, which have different schemas from the proposer stage.

Verifier Response Schema:
    The verifier returns JSON with the following fields::

        {
            "best_alternative": "Strongest non-mound interpretation",
            "alternative_evidence": "Visual features supporting it",
            "reasoning": "Why accepted/rejected",
            "mound_probability": 0.85
        }

Usage::

    from scripts.lib_batch_verifier import (
        build_verifier_jsonl,
        parse_verifier_results,
        aggregate_consensus_votes,
    )

Created: 2026-03-19
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
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


def _load_system_instruction(config: dict) -> str:
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


def _build_verifier_reference_parts(config: dict) -> list[dict]:
    """Build reference example parts for a verifier JSONL line.

    Handles both image-using examples (``config["examples"]``) and
    text-only labels (``config["text_only_labels"]``), mirroring the
    logic in ``5_verify_crops.py:construct_verifier_prompt()``.

    Args:
        config: Verifier config dict.

    Returns:
        List of JSONL-compatible content part dicts.
    """
    parts: list[dict] = []

    # Text-only labels (mutually exclusive with image examples)
    text_labels = config.get("text_only_labels", [])
    if text_labels:
        label_lines = "\n".join(f"- {lbl}" for lbl in text_labels)
        parts.append({
            "text": f"Reference examples (text descriptions only):\n"
                    f"{label_lines}",
        })
        return parts

    # Image examples
    examples = config.get("examples", [])
    if examples:
        parts.append({"text": "Reference examples for comparison:"})

    for ex in examples:
        img_path = _EXAMPLES_DIR / ex["path"]
        if not img_path.exists():
            logger.warning("Missing reference image: %s", img_path)
            continue
        parts.append({"text": f"Example: {ex['label']}"})
        parts.append({
            "inline_data": {
                "mime_type": _mime_type_for(img_path),
                "data": _encode_image_base64(img_path),
            },
        })

    return parts


def build_verifier_jsonl(
    manifest: dict,
    config: dict,
    output_path: Path,
    temperature_override: float | None = None,
    iteration_suffix: str = "",
) -> int:
    """Build a JSONL file for batch verifier submission.

    Each line contains one candidate with reference examples, crop image,
    system instruction, and generation config.

    Args:
        manifest: Candidate manifest dict (from ``extract_candidates.py``)
            with ``candidates`` list.
        config: Verifier config dict (e.g., ``verify_adversarial.json``).
        output_path: Path to write the JSONL file.
        temperature_override: Override temperature from config. Used for
            consensus voting where T > 0 is needed.
        iteration_suffix: Suffix appended to candidate keys for consensus
            (e.g., ``"_iter3"``). Empty for single-pass.

    Returns:
        Number of lines written.
    """
    system_instruction = _load_system_instruction(config)
    reference_parts = _build_verifier_reference_parts(config)
    crop_label = config.get(
        "crop_label",
        "Now classify the candidate symbol at the centre of this crop:",
    )

    temperature = temperature_override if temperature_override is not None else (
        config.get("temperature", 0.0)
    )

    # Generation config
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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0

    with open(output_path, "w") as f:
        for candidate in manifest.get("candidates", []):
            candidate_id = candidate["candidate_id"]
            crop_file = candidate["crop_file"]
            crop_path = output_path.parent.parent / crop_file

            # Resolve crop path relative to manifest location
            if not crop_path.exists():
                # Try relative to manifest's directory
                manifest_dir = output_path.parent.parent
                crop_path = manifest_dir / crop_file
            if not crop_path.exists():
                logger.warning(
                    "Crop file not found: %s (candidate %d)",
                    crop_file, candidate_id,
                )
                continue

            # Build content parts: references + crop label + crop image
            parts = list(reference_parts)  # Copy shared reference parts
            parts.append({"text": crop_label})
            parts.append({
                "inline_data": {
                    "mime_type": _mime_type_for(crop_path),
                    "data": _encode_image_base64(crop_path),
                },
            })

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

    system_instruction = _load_system_instruction(config)
    reference_parts = _build_verifier_reference_parts(config)
    crop_label = config.get(
        "crop_label",
        "Now classify the candidate symbol at the centre of this crop:",
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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0

    with open(output_path, "w") as f:
        for candidate in manifest.get("candidates", []):
            candidate_id = candidate["candidate_id"]
            crop_file = candidate["crop_file"]
            crop_path = output_path.parent.parent / crop_file

            if not crop_path.exists():
                manifest_dir = output_path.parent.parent
                crop_path = manifest_dir / crop_file
            if not crop_path.exists():
                logger.warning(
                    "Crop file not found: %s (candidate %d)",
                    crop_file, candidate_id,
                )
                continue

            # Build content parts once per candidate
            parts = list(reference_parts)
            parts.append({"text": crop_label})
            parts.append({
                "inline_data": {
                    "mime_type": _mime_type_for(crop_path),
                    "data": _encode_image_base64(crop_path),
                },
            })

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
) -> int:
    """Build JSONL with two crop scales per candidate in one request.

    Each JSONL line contains both a small-scale (e.g., 75×75) and
    large-scale (e.g., 150×150) crop of the same candidate, enabling
    the model to assess at both detail and context levels.

    Args:
        manifest_small: Candidate manifest for smaller crops (e.g., 75px).
        manifest_large: Candidate manifest for larger crops (e.g., 150px).
        config: Verifier config dict.
        output_path: Path to write the JSONL file.

    Returns:
        Number of lines written.
    """
    system_instruction = _load_system_instruction(config)
    reference_parts = _build_verifier_reference_parts(config)

    gen_config: dict[str, Any] = {
        "temperature": config.get("temperature", 0.0),
        "max_output_tokens": config.get("max_output_tokens", 8192),
        "response_mime_type": "application/json",
    }
    thinking_level = config.get("thinking_level")
    if thinking_level:
        gen_config["thinking_config"] = {
            "thinking_level": thinking_level.upper(),
        }

    # Build lookup for large crops by candidate_id
    large_by_id = {
        c["candidate_id"]: c for c in manifest_large.get("candidates", [])
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0
    base_dir_small = output_path.parent.parent
    base_dir_large = output_path.parent.parent

    with open(output_path, "w") as f:
        for candidate in manifest_small.get("candidates", []):
            cid = candidate["candidate_id"]
            large_candidate = large_by_id.get(cid)
            if large_candidate is None:
                logger.warning(
                    "No matching large crop for candidate %d", cid,
                )
                continue

            small_path = base_dir_small / candidate["crop_file"]
            large_path = base_dir_large / large_candidate["crop_file"]

            if not small_path.exists() or not large_path.exists():
                logger.warning(
                    "Missing crop(s) for candidate %d", cid,
                )
                continue

            # Build parts: references + small crop + large crop + label
            parts = list(reference_parts)
            parts.append({
                "text": "Detail view (close-up of candidate symbol):",
            })
            parts.append({
                "inline_data": {
                    "mime_type": _mime_type_for(small_path),
                    "data": _encode_image_base64(small_path),
                },
            })
            parts.append({
                "text": "Context view (surrounding map features):",
            })
            parts.append({
                "inline_data": {
                    "mime_type": _mime_type_for(large_path),
                    "data": _encode_image_base64(large_path),
                },
            })
            parts.append({
                "text": "Now classify the candidate symbol shown "
                        "at the centre of both views:",
            })

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
            logger.warning("Failed to parse verifier result for %s: %s", key, e)
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
            result dicts (from ``parse_verifier_results``).
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
        # Parse candidate ID from key: "candidate_00042_iter3" or "candidate_00042"
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
            "mean_probability": sum(probs) / len(probs) if probs else 0.0,
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
