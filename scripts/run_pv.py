#!/usr/bin/env python3
"""
Proposer-Verifier Pipeline Orchestrator (Dual-Mode)
====================================================

Description:
    Orchestrates the verifier stage of the Proposer-Verifier (PV) pipeline.
    Supports both Gemini Batch API and real-time API execution through a
    shared prompt construction layer in ``lib_verifier.py``.

    Two subcommands:

    - **extract** — Crop candidate images from proposer detections
    - **verify** — Run verifier on cropped candidates (batch or real-time)

Usage::

    # Extract candidates from proposer detections
    python scripts/run_pv.py extract \\
        --proposer outputs/retest/.../detections.geojson \\
        --output-dir outputs/pv/crops-150/config-name \\
        --padding 75

    # Verify via real-time API (Application Programming Interface)
    python scripts/run_pv.py verify \\
        --crops-dir outputs/pv/crops-150/config-name \\
        --verifier-config prompts/configs/verify_adversarial-text.json \\
        --output-dir outputs/pv/results/adversarial-text/config-name \\
        --mode realtime --workers 10

    # Verify via Batch API
    python scripts/run_pv.py verify \\
        --crops-dir outputs/pv/crops-150/config-name \\
        --verifier-config prompts/configs/verify_adversarial-text.json \\
        --output-dir outputs/pv/results/adversarial-text/config-name \\
        --mode batch

    # Consensus voting (both modes)
    python scripts/run_pv.py verify \\
        --crops-dir outputs/pv/crops-150/config-name \\
        --verifier-config prompts/configs/verify_adversarial-text.json \\
        --output-dir outputs/pv/results/adversarial-text-n5/config-name \\
        --mode realtime --iterations 5 --temperature 0.7

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_verifier import (
    aggregate_consensus_votes,
    build_generation_config,
    build_reference_items,
    build_verifier_jsonl,
    build_verifier_jsonl_consensus,
    gen_config_to_sdk,
    load_system_instruction,
    parse_verifier_results,
    verify_candidate_realtime,
)

# Script version
__version__ = "1.0.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =========================================================================
# Extract Subcommand
# =========================================================================


def cmd_extract(args: argparse.Namespace) -> int:
    """Execute the extract subcommand.

    Calls ``extract_candidates.extract_candidates()`` directly to crop
    image regions around proposer detections.

    Args:
        args: Parsed Command-Line Interface (CLI) arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    from scripts.extract_candidates import extract_candidates

    logger.info("Extracting candidates from: %s", args.proposer)
    logger.info("Output directory: %s", args.output_dir)
    logger.info("Padding: %d px (crop size: %d×%d)", args.padding,
                args.padding * 2, args.padding * 2)

    result = extract_candidates(
        proposer_geojson=args.proposer,
        tiles_dir=args.tiles_dir,
        output_dir=args.output_dir,
        rasters_dir=args.rasters_dir,
        padding=args.padding,
        dry_run=args.dry_run,
    )

    if result is None and not args.dry_run:
        logger.error("Extraction failed")
        return 1

    return 0


# =========================================================================
# Verify Subcommand
# =========================================================================


def cmd_verify(args: argparse.Namespace) -> int:
    """Execute the verify subcommand.

    Dispatches to batch or real-time path based on ``--mode``.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    # Load manifest
    manifest_path = args.crops_dir / "candidate_manifest.json"
    if not manifest_path.exists():
        logger.error("Manifest not found: %s", manifest_path)
        return 1

    with open(manifest_path) as f:
        manifest = json.load(f)

    n_candidates = len(manifest.get("candidates", []))
    if n_candidates == 0:
        logger.warning("No candidates in manifest — nothing to verify")
        return 0

    # Load verifier config
    with open(args.verifier_config) as f:
        config = json.load(f)

    # Apply thinking level override before any JSONL construction
    thinking_override = getattr(args, "thinking_level", None)
    if thinking_override is not None:
        config["thinking_level"] = thinking_override
        logger.info("Thinking level override: %s", thinking_override)

    logger.info("Verifier config: %s", args.verifier_config.name)
    logger.info("Candidates: %d", n_candidates)
    logger.info("Mode: %s", args.mode)
    logger.info("Iterations: %d", args.iterations)
    if args.temperature is not None:
        logger.info("Temperature override: %.2f", args.temperature)

    # Defensive model check: verify model is consistent with output dir
    effective_model = args.model or config.get("model", "gemini-3-flash")
    out_lower = str(args.output_dir).lower()
    if "pro" in out_lower and "flash" in effective_model.lower():
        logger.warning(
            "Output directory contains 'pro' but model is '%s'. "
            "Check for model/directory mismatch.",
            effective_model,
        )
    if "flash" in out_lower and "pro" in effective_model.lower():
        logger.warning(
            "Output directory contains 'flash' but model is '%s'. "
            "Check for model/directory mismatch.",
            effective_model,
        )

    # Warn if --dry-run used with real-time mode (not supported)
    if args.dry_run and args.mode == "realtime":
        logger.warning(
            "--dry-run is only supported in batch mode. "
            "No API calls will be made — exiting.",
        )
        return 0

    # Dispatch to mode-specific path
    if args.mode == "batch":
        return _verify_batch(
            manifest=manifest,
            config=config,
            crops_base_dir=args.crops_dir,
            output_dir=args.output_dir,
            iterations=args.iterations,
            temperature=args.temperature,
            dry_run=args.dry_run,
            model_override=args.model,
        )
    else:
        return _verify_realtime(
            manifest=manifest,
            config=config,
            crops_base_dir=args.crops_dir,
            output_dir=args.output_dir,
            workers=args.workers,
            iterations=args.iterations,
            temperature=args.temperature,
            model_override=args.model,
            service_tier=getattr(args, "service_tier", None),
        )


# =========================================================================
# Batch Verification Path
# =========================================================================


def _verify_batch(
    manifest: dict,
    config: dict,
    crops_base_dir: Path,
    output_dir: Path,
    iterations: int,
    temperature: float | None,
    dry_run: bool,
    model_override: str | None = None,
) -> int:
    """Batch API verification path.

    Builds JSONL, uploads, submits, polls, retrieves, and parses
    results using ``lib_batch_api`` lifecycle functions and
    ``lib_verifier`` JSONL builders.

    Args:
        manifest: Candidate manifest dict.
        config: Verifier config dict.
        crops_base_dir: Base directory for crop files.
        output_dir: Output directory for results.
        iterations: Number of verifier passes (1=single, >1=consensus).
        temperature: Temperature override for consensus.
        dry_run: If True, build JSONL without submitting.
        model_override: Optional model name override from CLI.

    Returns:
        Exit code (0=success, 1=error).
    """
    from scripts.lib_batch_api import (
        poll_batch_job,
        retrieve_batch_results,
        submit_batch_job,
        upload_jsonl,
        validate_batch_results,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "verifier_requests.jsonl"

    # Build JSONL
    if iterations > 1:
        temp = temperature if temperature is not None else 0.7
        n_lines = build_verifier_jsonl_consensus(
            manifest=manifest,
            config=config,
            output_path=jsonl_path,
            crops_base_dir=crops_base_dir,
            iterations=iterations,
            temperature=temp,
        )
    else:
        n_lines = build_verifier_jsonl(
            manifest=manifest,
            config=config,
            output_path=jsonl_path,
            crops_base_dir=crops_base_dir,
            temperature_override=temperature,
        )

    logger.info("Built JSONL: %d lines → %s", n_lines, jsonl_path)

    if dry_run:
        logger.info("[DRY RUN] JSONL written but not submitted")
        return 0

    if n_lines == 0:
        logger.warning("No valid candidates — nothing to submit")
        return 0

    # Batch lifecycle
    try:
        from google import genai

        client = genai.Client(
            api_key=_get_api_key(),
            http_options={"api_version": "v1alpha"},
        )

        # Upload
        display_name = f"pv-verifier-{datetime.now(timezone.utc):%Y%m%d-%H%M}"
        uploaded_file = upload_jsonl(client, jsonl_path, display_name)
        logger.info("Uploaded: %s", uploaded_file)

        # Resolve model name (handles -preview suffix fallback)
        model_name = model_override or config.get("model", "gemini-3-flash")
        model_name = _resolve_model_name(client, model_name)
        if model_name is None:
            return 1

        batch_job = submit_batch_job(
            client, model_name, uploaded_file, display_name,
        )
        logger.info("Submitted batch job: %s", batch_job.name)

        # Poll
        completed_job = poll_batch_job(client, batch_job.name)
        # Use getattr for safe access — state may be enum or string
        state_str = getattr(
            completed_job.state, "name", str(completed_job.state),
        )
        logger.info("Batch job complete: %s", state_str)

        # Retrieve and parse
        raw_results = retrieve_batch_results(client, completed_job)

        # Build expected keys for validation (sorted list to match
        # validate_batch_results' list[str] type contract)
        expected_keys: list[str] = []
        for candidate in manifest.get("candidates", []):
            cid = candidate["candidate_id"]
            if iterations > 1:
                for i in range(1, iterations + 1):
                    expected_keys.append(f"candidate_{cid:05d}_iter{i}")
            else:
                expected_keys.append(f"candidate_{cid:05d}")

        matched, missing, errored = validate_batch_results(
            expected_keys, raw_results,
        )
        if missing:
            logger.warning(
                "%d missing results (of %d expected)",
                len(missing), len(expected_keys),
            )

        parsed = parse_verifier_results(matched)

    except Exception as e:
        logger.error("Batch verification failed: %s", e)
        return 1

    # Create a minimal metadata tracker for batch runs — no per-response
    # data (the Batch API doesn't return it), but captures run config.
    from scripts.lib_llm_metadata import LLMMetadataTracker
    batch_metadata = LLMMetadataTracker(
        config=config,
        system_instruction=load_system_instruction(config),
        script_name="run_pv.py",
        script_version=__version__,
        model_override=model_name,
    )

    # Write outputs
    _write_verification_outputs(
        parsed_results=parsed,
        manifest=manifest,
        config=config,
        output_dir=output_dir,
        iterations=iterations,
        mode="batch",
        metadata_tracker=batch_metadata,
        model_name=model_name,
    )

    return 0


# =========================================================================
# Real-Time Verification Path
# =========================================================================


def _verify_realtime(
    manifest: dict,
    config: dict,
    crops_base_dir: Path,
    output_dir: Path,
    workers: int,
    iterations: int,
    temperature: float | None,
    model_override: str | None,
    service_tier: str | None = None,
) -> int:
    """Real-time API verification path.

    Uses ``ThreadPoolExecutor`` with configurable workers. Each worker
    calls ``verify_candidate_realtime()`` from ``lib_verifier.py``.

    Args:
        manifest: Candidate manifest dict.
        config: Verifier config dict.
        crops_base_dir: Base directory for crop files.
        output_dir: Output directory for results.
        workers: Number of parallel workers.
        iterations: Number of verifier passes per candidate.
        temperature: Temperature override for consensus.
        model_override: Optional model name override.

    Returns:
        Exit code (0=success, 1=error).
    """
    from google import genai

    from scripts.lib_llm_metadata import LLMMetadataTracker

    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialise API client
    client = genai.Client(
        api_key=_get_api_key(),
        http_options={"api_version": "v1alpha"},
    )

    # Resolve model name
    model_name = model_override or config.get("model", "gemini-3-flash")
    model_name = _resolve_model_name(client, model_name)
    if model_name is None:
        return 1

    # Build shared prompt components once
    system_instruction = load_system_instruction(config)
    reference_items = build_reference_items(config)
    gen_config_dict = build_generation_config(config, temperature)
    sdk_gen_config = gen_config_to_sdk(
        gen_config_dict, system_instruction, service_tier=service_tier,
    )

    # Metadata tracker
    metadata_tracker = LLMMetadataTracker(
        config=config,
        system_instruction=system_instruction,
        script_name="run_pv.py",
        script_version=__version__,
        model_override=model_name,
    )

    candidates = manifest.get("candidates", [])
    total = len(candidates)
    logger.info(
        "Starting real-time verification: %d candidates × %d iterations, "
        "%d workers",
        total, iterations, workers,
    )

    # Submit to thread pool
    all_results: dict[str, dict] = {}
    completed = 0
    verified_count = 0
    failed_count = 0

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers,
    ) as executor:
        future_to_cand = {
            executor.submit(
                verify_candidate_realtime,
                candidate=cand,
                reference_items=reference_items,
                client=client,
                model_name=model_name,
                gen_config=sdk_gen_config,
                config=config,
                crops_base_dir=crops_base_dir,
                iterations=iterations,
                candidate_id_str=f"cand_{cand['candidate_id']:04d}",
            ): cand
            for cand in candidates
        }

        for future in concurrent.futures.as_completed(future_to_cand):
            completed += 1

            try:
                cand_results, metadata_list = future.result()

                # Log metadata
                for meta in metadata_list:
                    item_id = getattr(meta, "item_id", None) or "unknown"
                    metadata_tracker.log_response(item_id, meta)

                if cand_results:
                    all_results.update(cand_results)
                    verified_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                failed_count += 1
                cand = future_to_cand[future]
                logger.error(
                    "Candidate %s failed: %s",
                    cand["candidate_id"], e,
                )

            # Log progress after counters are updated
            if completed % 10 == 0 or completed == total:
                logger.info(
                    "Progress: %d/%d (verified: %d, failed: %d)",
                    completed, total, verified_count, failed_count,
                )

    logger.info(
        "Verification complete: %d/%d candidates succeeded",
        verified_count, total,
    )

    # Write outputs
    _write_verification_outputs(
        parsed_results=all_results,
        manifest=manifest,
        config=config,
        output_dir=output_dir,
        iterations=iterations,
        mode="realtime",
        metadata_tracker=metadata_tracker,
        model_name=model_name,
    )

    return 0


# =========================================================================
# Shared Output Writer
# =========================================================================


def _write_verification_outputs(
    parsed_results: dict[str, dict],
    manifest: dict,
    config: dict,
    output_dir: Path,
    iterations: int,
    mode: str,
    metadata_tracker: Any = None,
    threshold: float = 0.5,
    model_name: str | None = None,
) -> None:
    """Write verification outputs shared by both modes.

    Produces:
    - ``probabilities.json`` — per-candidate parsed results
    - ``consensus.json`` — aggregated votes (if iterations > 1)
    - ``run.meta.json`` — LLM metadata (if tracker provided)

    Args:
        parsed_results: Dict mapping candidate key to parsed result.
        manifest: Candidate manifest dict.
        config: Verifier config dict.
        output_dir: Output directory.
        iterations: Number of iterations used.
        mode: Execution mode ("batch" or "realtime").
        metadata_tracker: LLM metadata tracker (optional).
        threshold: Probability threshold for consensus voting.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Probabilities
    prob_path = output_dir / "probabilities.json"
    with open(prob_path, "w") as f:
        json.dump({
            "version": "1.0",
            "mode": mode,
            "verifier_config": config.get("version", "unknown"),
            "iterations": iterations,
            "total_results": len(parsed_results),
            "results": parsed_results,
        }, f, indent=2)
    logger.info("Probabilities written: %s", prob_path)

    # Consensus aggregation (if multiple iterations)
    if iterations > 1:
        consensus = aggregate_consensus_votes(parsed_results, threshold)
        consensus_path = output_dir / "consensus.json"
        # Convert int keys to strings for JSON serialisation
        serialisable = {str(k): v for k, v in consensus.items()}
        with open(consensus_path, "w") as f:
            json.dump({
                "version": "1.0",
                "mode": mode,
                "verifier_config": config.get("version", "unknown"),
                "iterations": iterations,
                "threshold": threshold,
                "total_candidates": len(consensus),
                "consensus": serialisable,
            }, f, indent=2)
        logger.info("Consensus written: %s", consensus_path)

        # Summary stats — minimum votes to accept is majority
        import math
        min_votes = math.ceil(iterations / 2)
        n_accepted = sum(
            1 for v in consensus.values()
            if v["vote_count"] >= min_votes
        )
        logger.info(
            "Consensus summary: %d/%d candidates accepted "
            "(≥%d/%d votes)",
            n_accepted, len(consensus),
            min_votes, iterations,
        )

    # Metadata
    if metadata_tracker is not None:
        from scripts.lib_llm_metadata import estimate_cost, LLMProvider

        meta = metadata_tracker.finalise(include_per_item=False)
        meta["cost_estimate"] = estimate_cost(
            usage=metadata_tracker.usage,
            provider=LLMProvider.GEMINI.value,
            model=model_name or config.get("model", "gemini-3-flash"),
        )
        meta_path = output_dir / "run.meta.json"
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        logger.info("Metadata written: %s", meta_path)

    # Print summary
    if parsed_results:
        probs = [
            r["mound_probability"]
            for r in parsed_results.values()
            if isinstance(r.get("mound_probability"), (int, float))
        ]
        if probs:
            above = sum(1 for p in probs if p >= threshold)
            logger.info(
                "Score summary: mean=%.3f, "
                "above threshold (%.1f): %d/%d (%.1f%%)",
                sum(probs) / len(probs), threshold,
                above, len(probs), 100 * above / len(probs),
            )


# =========================================================================
# Helpers
# =========================================================================


def _get_api_key() -> str:
    """Load Google API key from config module.

    Returns:
        API key string.

    Raises:
        RuntimeError: If config module or API key not found.
    """
    try:
        from config import GOOGLE_API_KEY
        return GOOGLE_API_KEY
    except ImportError:
        raise RuntimeError(
            "config.py not found — cannot load API key"
        )


def _resolve_model_name(client: Any, model_name: str) -> str | None:
    """Resolve a model name to its API-available form.

    Checks for exact match, then tries ``-preview`` suffix. Matches
    the pattern in ``5_verify_crops.py``.

    Args:
        client: Initialised google-genai Client.
        model_name: Model name from config (e.g., ``"gemini-3-flash"``).

    Returns:
        Resolved model name, or None if not found.
    """
    try:
        available = {
            m.name.removeprefix("models/") for m in client.models.list()
        }
    except Exception as e:
        logger.warning(
            "Could not list models: %s — proceeding with '%s' as-is.",
            e, model_name,
        )
        return model_name

    if model_name in available:
        return model_name

    preview_name = f"{model_name}-preview"
    if preview_name in available:
        logger.info(
            "Model '%s' not found; resolved to '%s'",
            model_name, preview_name,
        )
        return preview_name

    logger.error(
        "Model '%s' not found in API (also tried '%s')",
        model_name, preview_name,
    )
    return None


# =========================================================================
# CLI
# =========================================================================


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with extract and verify subcommands."""
    parser = argparse.ArgumentParser(
        description=(
            "Proposer-Verifier pipeline orchestrator — extract candidate "
            "crops and verify them via Batch or real-time API"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Extract subcommand ---
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract candidate crops from proposer detections",
    )
    extract_parser.add_argument(
        "--proposer", type=Path, required=True,
        help="Path to proposer output GeoJSON",
    )
    extract_parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Directory for cropped candidate images and manifest",
    )
    extract_parser.add_argument(
        "--rasters-dir", type=Path,
        default=BASE_DIR / "inputs" / "rasters",
        help="Directory containing source GeoTIFF rasters",
    )
    extract_parser.add_argument(
        "--tiles-dir", type=Path,
        default=BASE_DIR / "inputs" / "tiles",
        help="Directory containing source tiles (fallback)",
    )
    extract_parser.add_argument(
        "--padding", type=int, default=75,
        help="Pixels of context around centroid (default: 75)",
    )
    extract_parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate inputs without extracting crops",
    )
    extract_parser.set_defaults(func=cmd_extract)

    # --- Verify subcommand ---
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify candidates via Batch or real-time API",
    )
    verify_parser.add_argument(
        "--crops-dir", type=Path, required=True,
        help="Directory with candidate crops and manifest",
    )
    verify_parser.add_argument(
        "--verifier-config", type=Path, required=True,
        help="Path to verifier config JSON",
    )
    verify_parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Directory for verification results",
    )
    verify_parser.add_argument(
        "--mode", choices=["batch", "realtime"], default="realtime",
        help="Execution mode (default: realtime)",
    )
    verify_parser.add_argument(
        "--iterations", type=int, default=1,
        help="Number of verifier passes per candidate (default: 1)",
    )
    verify_parser.add_argument(
        "--temperature", type=float, default=None,
        help="Temperature override (for consensus, use T > 0)",
    )
    verify_parser.add_argument(
        "--workers", type=int, default=5,
        help="Parallel workers for real-time mode (default: 5)",
    )
    verify_parser.add_argument(
        "--model", type=str, default=None,
        help="Override model name from config",
    )
    verify_parser.add_argument(
        "--thinking-level", type=str, default=None,
        help=(
            "Override thinking level from config "
            "(e.g., 'medium'). Required when --model targets a "
            "model that does not support the config's default "
            "thinking level (e.g., Gemini 3.1 Pro requires "
            "MEDIUM, not MINIMAL)."
        ),
    )
    verify_parser.add_argument(
        "--dry-run", action="store_true",
        help="Build JSONL without submitting (batch mode only)",
    )
    verify_parser.add_argument(
        "--service-tier",
        choices=["standard", "flex"],
        default=None,
        dest="service_tier",
        help="Service tier for real-time API calls. 'flex' gives 50%% "
        "discount with 1-15 min latency. Ignored in batch mode.",
    )
    verify_parser.set_defaults(func=cmd_verify)

    return parser


def main() -> None:
    """Parse arguments and dispatch to subcommand handler."""
    parser = _build_parser()
    args = parser.parse_args()
    exit_code = args.func(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
