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
import shutil
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

    # Default strict=True for direct ``verify`` invocations so silent
    # drops fail loud. The ``--no-strict`` flag is the explicit opt-out.
    strict = getattr(args, "strict", True)

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
            strict=strict,
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
            strict=strict,
        )


# =========================================================================
# Cleanup Subcommand
# =========================================================================


def _compute_missing_candidates(
    manifest: dict,
    probs_path: Path,
    iterations: int = 1,
) -> tuple[set[str], dict]:
    """Identify candidates missing from probabilities.json.

    Args:
        manifest: Candidate manifest dict.
        probs_path: Path to existing probabilities.json.
        iterations: Verifier iterations (affects key format).

    Returns:
        Tuple of (missing_ids set, loaded probs dict).
    """
    # Expand to the full per-iteration key set so multi-iteration runs
    # surface iter2..iterN gaps to ``cmd_cleanup``. Using the single
    # iter1 proxy here masked tail-iteration failures, blocking cleanup
    # from re-attempting them.
    all_ids: set[str] = set()
    for c in manifest.get("candidates", []):
        all_ids.update(_candidate_iteration_keys(c, iterations))

    probs: dict = {}
    if probs_path.exists():
        with open(probs_path) as f:
            probs = json.load(f)

    verified_ids = set(probs.get("results", {}).keys())
    missing = all_ids - verified_ids
    return missing, probs


def cmd_cleanup(args: argparse.Namespace) -> int:
    """Execute the cleanup subcommand.

    Identifies candidates missing from an existing probabilities.json
    and re-verifies them with iterative retries. Uses the resume logic
    in ``_verify_realtime()`` to skip already-verified candidates.

    Optionally applies safe-mode (reduced ``max_output_tokens``) on
    the final attempt to recover candidates that fail due to thinking
    token budget exhaustion.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0=all recovered, 1=some remain missing).
    """
    # Load manifest
    manifest_path = args.crops_dir / "candidate_manifest.json"
    if not manifest_path.exists():
        logger.error("Manifest not found: %s", manifest_path)
        return 1

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Load existing probabilities and compute missing set
    probs_path = args.verified_dir / "probabilities.json"
    if not probs_path.exists():
        logger.error("probabilities.json not found in %s", args.verified_dir)
        return 1

    missing, _ = _compute_missing_candidates(
        manifest, probs_path, args.iterations,
    )
    initial_missing = len(missing)

    if initial_missing == 0:
        logger.info("Nothing to clean up — all candidates already verified")
        return 0

    logger.info("Cleanup: %d candidates missing from %s", initial_missing, probs_path)

    if args.dry_run:
        logger.info("Dry run — missing candidate IDs:")
        for mid in sorted(missing):
            logger.info("  %s", mid)
        return 0

    # Load verifier config
    with open(args.verifier_config) as f:
        config = json.load(f)

    # Apply thinking level override if specified
    thinking_override = getattr(args, "thinking_level", None)
    if thinking_override is not None:
        config["thinking_level"] = thinking_override

    # Backup before modifying
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup_path = probs_path.with_name(
        f"probabilities.json.pre-cleanup-{timestamp}.backup"
    )
    shutil.copy(probs_path, backup_path)
    logger.info("Backup: %s", backup_path.name)

    # The retry pass's tracker rewrites run.meta.json with the retries'
    # usage only, so the main run's usage stats survive here or nowhere.
    meta_path = args.verified_dir / "run.meta.json"
    if meta_path.exists():
        meta_backup = meta_path.with_name(
            f"run.meta.json.pre-cleanup-{timestamp}.backup"
        )
        shutil.copy(meta_path, meta_backup)
        logger.info("Backup: %s", meta_backup.name)

    # Iterative cleanup loop
    attempts_used = 0
    for attempt in range(1, args.max_attempts + 1):
        missing, _ = _compute_missing_candidates(
            manifest, probs_path, args.iterations,
        )
        if not missing:
            break

        attempts_used = attempt
        logger.info(
            "Attempt %d/%d: %d candidates remaining",
            attempt, args.max_attempts, len(missing),
        )

        # Safe-mode on final attempt: override max_output_tokens
        attempt_config = dict(config)
        if (
            args.safe_mode_tokens is not None
            and attempt == args.max_attempts
        ):
            attempt_config["max_output_tokens"] = args.safe_mode_tokens
            logger.info(
                "Safe-mode: max_output_tokens → %d",
                args.safe_mode_tokens,
            )

        # Call _verify_realtime() — resume logic skips verified candidates,
        # incremental write saves progress, so this is safe to interrupt.
        # Pass strict=False: cleanup owns its own audit trail via
        # cleanup_history (and _log_cleanup_failures_to_meta below), so
        # the inner completeness assertion must not short-circuit our
        # post-loop tally with a non-zero return.
        _verify_realtime(
            manifest=manifest,
            config=attempt_config,
            crops_base_dir=args.crops_dir,
            output_dir=args.verified_dir,
            workers=args.workers,
            iterations=args.iterations,
            temperature=args.temperature,
            model_override=args.model,
            service_tier=getattr(args, "service_tier", None),
            strict=False,
        )

    # Final tally
    final_missing, probs = _compute_missing_candidates(
        manifest, probs_path, args.iterations,
    )
    recovered = initial_missing - len(final_missing)

    # Add cleanup_history audit trail
    probs.setdefault("cleanup_history", []).append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "initial_missing": initial_missing,
        "recovered": recovered,
        "still_missing": len(final_missing),
        "still_missing_ids": sorted(final_missing),
        "attempts_used": attempts_used,
        "max_attempts": args.max_attempts,
        "safe_mode_used": args.safe_mode_tokens is not None,
    })
    probs["total_results"] = len(probs.get("results", {}))

    with open(probs_path, "w") as f:
        json.dump(probs, f, indent=2)

    # Mirror still-missing IDs into run.meta.json:execution_stats.failed_items[]
    # so downstream consumers (clean_meta_failed_items.py, run_generalisation.py
    # retry path, future audit sweeps) see the residual gap without parsing
    # cleanup_history. Idempotent — pre-existing entries are preserved.
    if final_missing:
        _log_cleanup_failures_to_meta(args.verified_dir, final_missing)

    # Report
    logger.info("=" * 50)
    logger.info("Cleanup Report")
    logger.info("=" * 50)
    logger.info("Initial missing: %d", initial_missing)
    logger.info("Recovered:       %d", recovered)
    logger.info("Still missing:   %d", len(final_missing))
    if final_missing:
        for mid in sorted(final_missing):
            logger.info("  %s", mid)
    logger.info("Attempts used:   %d", attempts_used)
    logger.info("Backup:          %s", backup_path.name)

    return 1 if final_missing else 0


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
    strict: bool = True,
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
        strict: If True, surface non-zero exit code on completeness
            gaps detected by the post-run assertion. Mirrors the
            ``--no-strict`` flag plumbed through ``_verify_realtime``.

    Returns:
        Exit code (0=success, 1=error or completeness gap in strict mode).
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

    # Hoist metadata tracker construction above the lifecycle so the
    # `missing` set computed from validate_batch_results() can be logged
    # into failed_items[] before _write_verification_outputs runs the
    # completeness assertion. The Batch API does not return per-response
    # metadata, so the tracker captures run config only — but the
    # failed_items[] audit trail is the load-bearing piece of the
    # silent-drop surfacing fix.
    from scripts.lib_llm_metadata import LLMMetadataTracker
    batch_metadata = LLMMetadataTracker(
        config=config,
        system_instruction=load_system_instruction(config),
        script_name="run_pv.py",
        script_version=__version__,
        model_override=model_override,
    )

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
        # Update tracker now that the model is resolved.
        batch_metadata.model_override = model_name

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
        # Surface every missing result as a failed_items[] entry so the
        # batch path matches realtime parity. _assert_completeness in
        # _write_verification_outputs is idempotent against these IDs.
        for mid in sorted(missing):
            batch_metadata.log_failure(
                mid, "absent from batch response",
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

    # Write outputs (also runs the completeness assertion).
    gap_count = _write_verification_outputs(
        parsed_results=parsed,
        manifest=manifest,
        config=config,
        output_dir=output_dir,
        iterations=iterations,
        mode="batch",
        metadata_tracker=batch_metadata,
        model_name=model_name,
        strict=strict,
    )

    return 1 if gap_count > 0 and strict else 0


# =========================================================================
# Resume and Incremental Save Helpers
# =========================================================================


def _candidate_iteration_keys(candidate: dict, iterations: int) -> list[str]:
    """Return every expected result key for ``candidate`` × ``iterations``.

    Single canonical key-expansion site: the resume filter, cleanup
    missing-set computation, driver per-attempt logging, and the
    completeness assertion all consume this list so they cannot drift
    out of sync. The Layer 1 surfacing fix originally relied on
    ``_candidate_result_key`` returning a single ``_iter1`` proxy across
    all three call sites — that under-counted multi-iteration runs by a
    factor of N, allowing iter2..iterN failures to slip past the resume
    filter, the cleanup sweep, and the metadata tracker. Centralising
    the expansion here prevents that regression from recurring.

    For single-iteration runs the list contains ``["candidate_NNNNN"]``.
    For multi-iteration consensus the list contains
    ``["candidate_NNNNN_iter1", ..., "candidate_NNNNN_iterN"]``.

    Args:
        candidate: Candidate dict with ``candidate_id``.
        iterations: Number of verifier iterations (1 for single-pass,
            N for consensus). Must be ``>= 1``.

    Returns:
        Ordered list of result keys — one per expected iteration.

    Raises:
        ValueError: If ``iterations < 1``. The CLI parser enforces a
            positive iteration count, so this branch should be
            unreachable in practice; the explicit raise prevents
            silent misuse if a future caller omits validation.
    """
    if iterations < 1:
        raise ValueError(
            f"iterations must be >= 1, got {iterations}",
        )
    cid = candidate["candidate_id"]
    if iterations > 1:
        return [
            f"candidate_{cid:05d}_iter{i}"
            for i in range(1, iterations + 1)
        ]
    return [f"candidate_{cid:05d}"]


def _candidate_result_key(candidate: dict, iterations: int) -> str:
    """Return the canonical *single* result-key proxy for a candidate.

    Retained for back-compat with callers/tests that need a single
    string identifier per candidate (rather than the full per-iteration
    set). For multi-iteration runs this returns the iter1 suffix as a
    proxy — DO NOT use it to determine "is this candidate fully
    covered" or "what failed for this candidate" — those questions
    require the full set from ``_candidate_iteration_keys``.

    Args:
        candidate: Candidate dict with ``candidate_id``.
        iterations: Number of verifier iterations.

    Returns:
        Result dict key string (always one entry; for consensus runs
        this is the iter1 proxy).
    """
    return _candidate_iteration_keys(candidate, iterations)[0]


def _iteration_id_to_result_key(
    iteration_id: str | None,
    iterations: int,
) -> str | None:
    """Map a worker ``iteration_id`` string to its ``probabilities.json`` key.

    The verifier worker tags each metadata entry with an
    ``iteration_id`` like ``cand_0042_iter1``; the corresponding
    persisted result-key is ``candidate_00042`` (single-pass) or
    ``candidate_00042_iter1`` (consensus). This helper performs that
    translation so the driver can match metadata to expected keys when
    deciding which per-iteration ``log_success`` / ``log_failure`` call
    to emit.

    Returns ``None`` when ``iteration_id`` cannot be parsed (malformed
    or missing) — the caller is responsible for falling back to a
    generic identifier.

    Args:
        iteration_id: Worker-side ID like ``"cand_0042_iter1"``.
        iterations: Number of verifier iterations (decides the key
            shape — bare ``candidate_NNNNN`` vs ``candidate_NNNNN_iterK``).

    Returns:
        Result-dict key string, or ``None`` on parse failure.
    """
    if not iteration_id:
        return None
    # Expected shape: cand_<id4>_iter<n>
    parts = iteration_id.split("_")
    if len(parts) < 3 or not parts[0] == "cand":
        return None
    try:
        cid = int(parts[1])
    except ValueError:
        return None
    iter_part = parts[2]
    if not iter_part.startswith("iter"):
        return None
    try:
        iter_num = int(iter_part.removeprefix("iter"))
    except ValueError:
        return None
    if iterations > 1:
        return f"candidate_{cid:05d}_iter{iter_num}"
    return f"candidate_{cid:05d}"


def _summarise_failure_reason(metadata_list: list) -> str:
    """Summarise the terminal failure reason from a metadata list.

    Walks the list back-to-front, returning the most recent
    ``parse_error`` annotation, or — when no ``parse_error`` is set — a
    ``finish_reason``-based label for entries that recorded a terminal
    error (e.g. ``error``, ``max_tokens``, ``safety``). Falls back to a
    generic string when the list is empty (the ``FileNotFoundError``
    early-return path before Layer 2 propagated a synthetic metadata
    entry).

    The ``finish_reason`` branch handles the case where
    ``_call_verifier_api`` synthesises an error-metadata entry on a
    terminal exception (``finish_reason=error``,
    ``raw_finish_reason=<ExceptionClassName>``) but does not populate
    ``parse_error`` — without this branch the helper would fall through
    to the generic fallback and lose the discriminating diagnostic.

    Args:
        metadata_list: Mutable metadata list populated by
            ``_call_verifier_api()`` with ``LLMResponseMetadata`` (and/or
            error-metadata) entries.

    Returns:
        Human-readable failure reason suitable for ``log_failure``'s
        ``reason`` field.
    """
    for meta in reversed(metadata_list):
        err = getattr(meta, "parse_error", None)
        if err:
            return str(err)
        # ``LLMResponseMetadata`` exposes ``finish_reason`` (normalised
        # enum value, e.g. ``"error"``, ``"max_tokens"``, ``"safety"``)
        # plus ``raw_finish_reason`` (the original API/exception type
        # name). Surface both when the entry signals a terminal failure.
        finish = getattr(meta, "finish_reason", None)
        if finish and finish not in ("success", "unknown"):
            raw = getattr(meta, "raw_finish_reason", "") or ""
            if raw:
                return f"{finish}: {raw}"
            return f"{finish}: retries exhausted"
    return "no result returned (retries exhausted)"


def _assert_completeness(
    parsed_results: dict[str, dict],
    manifest: dict,
    iterations: int,
    mode: str,
    metadata_tracker: Any,
    strict: bool,
) -> int:
    """Assert that ``parsed_results`` covers every candidate × iteration key.

    Computes the expected key set from the manifest (single-iteration:
    ``candidate_NNNNN``; consensus: ``candidate_NNNNN_iter1``…
    ``candidate_NNNNN_iterN``), takes the difference against
    ``parsed_results.keys()``, and — when a gap exists — backfills
    ``failed_items[]`` with one entry per missing key (idempotent against
    pre-existing entries) and stores a ``completeness_gap`` summary on the
    tracker's ``results_summary``.

    The helper is non-destructive: it never deletes results, never modifies
    crops, never rewrites prior ``run.meta.json`` content. It exists so
    every retry-exhausted candidate appears in the per-run audit trail —
    closing the silent-drop surfacing gap that allowed 30 cells to lose
    835 candidates between commit ``5d725930`` (March 2026) and 2026-05-03.

    Args:
        parsed_results: Mapping of candidate-result keys to parsed result
            dicts (the contents of ``probabilities.json:results``).
        manifest: Candidate manifest dict — read for the canonical input
            cardinality.
        iterations: Number of verifier passes per candidate (1 or N).
        mode: Execution mode (``"realtime"`` or ``"batch"``) — included in
            log output for forensic context only.
        metadata_tracker: ``LLMMetadataTracker`` instance whose
            ``stats.failed_items`` and ``results_summary`` are mutated.
            May be ``None`` (defensive — no-op for tracker side effects).
        strict: If True, log a guidance message pointing the operator at
            ``run_pv.py cleanup``; the caller is responsible for
            propagating a non-zero exit code based on the return value.

    Returns:
        Gap count — ``0`` when complete, otherwise the number of missing
        candidate keys.
    """
    # Defer key expansion to ``_candidate_iteration_keys`` so this assertion
    # cannot drift out of sync with the resume filter, cleanup missing-set
    # computation, and the per-iteration logging path. All four sites must
    # consume the same canonical key list — the helper is the single source
    # of truth for "what does completeness look like for candidate × N".
    expected: set[str] = set()
    for cand in manifest.get("candidates", []):
        expected.update(_candidate_iteration_keys(cand, iterations))

    actual = set(parsed_results.keys())
    gap = expected - actual

    if not gap:
        return 0

    logger.error(
        "Completeness gap: %d candidates missing from results "
        "(mode=%s, expected=%d, actual=%d)",
        len(gap), mode, len(expected), len(parsed_results),
    )
    sample = sorted(gap)[:10]
    logger.warning("First %d missing IDs: %s", len(sample), sample)

    if metadata_tracker is not None:
        existing_ids = {
            f["item_id"] for f in metadata_tracker.stats.failed_items
        }
        for mid in sorted(gap):
            if mid not in existing_ids:
                metadata_tracker.log_failure(
                    mid,
                    "absent from results — completeness assertion",
                )
        metadata_tracker.results_summary["completeness_gap"] = {
            "expected": len(expected),
            "actual": len(parsed_results),
            "missing_count": len(gap),
            "missing_ids_sample": sorted(gap)[:100],
        }

    if strict:
        logger.error(
            "Strict mode: returning non-zero exit code due to "
            "completeness gap. Run `run_pv.py cleanup` to retry "
            "missing candidates, or pass --no-strict to suppress.",
        )

    return len(gap)


def _log_cleanup_failures_to_meta(
    verified_dir: Path,
    missing: set[str],
) -> None:
    """Append residual cleanup-loop failures to ``run.meta.json``.

    Loads ``verified_dir/run.meta.json`` (if present), ensures every ID in
    ``missing`` appears in ``execution_stats.failed_items[]`` exactly once,
    and writes the file back. Idempotent: pre-existing entries are
    preserved verbatim and never duplicated.

    No-op if ``run.meta.json`` does not exist (older runs that pre-date
    the metadata-tracker integration; also covers the ``--dry-run`` path
    where the meta file is never written).

    Args:
        verified_dir: Directory containing ``run.meta.json`` (the same
            ``--verified-dir`` argument passed to ``cmd_cleanup``).
        missing: Set of candidate IDs that remain absent from
            ``probabilities.json`` after the cleanup loop's
            ``max_attempts`` exhausted.
    """
    meta_path = verified_dir / "run.meta.json"
    if not meta_path.exists():
        return

    try:
        with open(meta_path) as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning(
            "Could not read %s for cleanup-failure logging: %s",
            meta_path, exc,
        )
        return

    exec_stats = meta.setdefault("execution_stats", {})
    failed_items = exec_stats.setdefault("failed_items", [])
    existing_ids = {
        f.get("item_id") for f in failed_items if isinstance(f, dict)
    }

    timestamp = datetime.now(timezone.utc).isoformat()
    added = 0
    for mid in sorted(missing):
        if mid in existing_ids:
            continue
        failed_items.append({
            "item_id": mid,
            "reason": "absent after cleanup max_attempts",
            "timestamp": timestamp,
        })
        added += 1

    if added == 0:
        return

    # Atomic write — tmp + rename — to avoid corruption mid-write.
    tmp_path = meta_path.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(meta, f, indent=2)
    tmp_path.rename(meta_path)
    logger.info(
        "Logged %d residual cleanup failures to %s",
        added, meta_path.name,
    )


def _save_probabilities_incremental(
    results: dict[str, dict],
    output_dir: Path,
    config_version: str,
    mode: str,
    iterations: int,
) -> None:
    """Write probabilities.json incrementally for resume safety.

    Uses atomic write (tmp file + rename) to prevent corruption if
    killed mid-write. Called periodically from the ``as_completed()``
    loop so that partial results survive process termination.

    Args:
        results: Current results dict (candidate keys → result dicts).
        output_dir: Directory to write probabilities.json.
        config_version: Verifier config version string.
        mode: Execution mode (``"realtime"`` or ``"batch"``).
        iterations: Number of verifier iterations per candidate.
    """
    probs = {
        "version": "1.0",
        "mode": mode,
        "verifier_config": config_version,
        "iterations": iterations,
        "total_results": len(results),
        "results": results,
    }
    out_path = output_dir / "probabilities.json"
    tmp_path = out_path.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(probs, f)
    tmp_path.rename(out_path)


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
    strict: bool = True,
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
        service_tier: Optional service tier ("standard" or "flex").
        strict: If True, surface non-zero exit code when the post-run
            completeness assertion identifies a gap. Defaults to True
            so silent drops fail loud; ``cmd_cleanup`` overrides to
            False because it owns its own audit trail.

    Returns:
        Exit code (0=success, 1=completeness gap in strict mode).
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
    config_version = config.get("version", "unknown")

    # ── Resume: load existing results and skip verified candidates ──
    existing_results: dict[str, dict] = {}
    probs_path = output_dir / "probabilities.json"
    if probs_path.exists():
        try:
            with open(probs_path) as f:
                existing = json.load(f)
            existing_results = existing.get("results", {})
            logger.info(
                "Resuming: %d candidates already verified",
                len(existing_results),
            )
        except (json.JSONDecodeError, KeyError):
            logger.warning(
                "Could not parse existing probabilities.json, starting fresh"
            )

    # Filter out already-verified candidates. A candidate is "verified"
    # only when *every* expected iteration key is present — for multi-
    # iteration consensus runs (K=10, K=30) the iter1 proxy alone is
    # insufficient: iter2..iterN may be missing and require re-attempt.
    # The worker idempotently re-runs all iterations for any candidate
    # we re-submit; the cost of re-running iter1 for a partial-coverage
    # candidate is bounded and far cheaper than the silent-drop the
    # iter1-only filter previously caused.
    if existing_results:
        original_count = len(candidates)
        candidates = [
            c for c in candidates
            if not all(
                k in existing_results
                for k in _candidate_iteration_keys(c, iterations)
            )
        ]
        skipped = original_count - len(candidates)
        if skipped:
            logger.info(
                "Skipping %d already-verified candidates, %d remaining",
                skipped, len(candidates),
            )

    total = len(candidates)
    logger.info(
        "Starting real-time verification: %d candidates × %d iterations, "
        "%d workers",
        total, iterations, workers,
    )

    # Submit to thread pool — seed with existing results for merge
    all_results: dict[str, dict] = dict(existing_results)
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
                metadata_tracker=metadata_tracker,
            ): cand
            for cand in candidates
        }

        for future in concurrent.futures.as_completed(future_to_cand):
            completed += 1
            cand = future_to_cand[future]
            # Expand to the full per-iteration key set so multi-iteration
            # runs (K=10, K=30 consensus) record one log_success /
            # log_failure entry per actual API call rather than a single
            # iter1 proxy. The proxy under-counted items_processed by a
            # factor of N and routed iter2..iterN failures through the
            # generic completeness backfill rather than the rich
            # per-attempt failure-reason path.
            expected_keys = _candidate_iteration_keys(cand, iterations)

            try:
                cand_results, metadata_list = future.result()

                # Log metadata
                for meta in metadata_list:
                    item_id = getattr(meta, "item_id", None) or "unknown"
                    metadata_tracker.log_response(item_id, meta)

                # Build a parse_error map keyed by result-key so we can
                # attribute each missing iter to its own failure reason
                # rather than collapsing all iters under one label.
                iter_errors: dict[str, str] = {}
                for meta in metadata_list:
                    err = getattr(meta, "parse_error", None)
                    if not err:
                        continue
                    rk = _iteration_id_to_result_key(
                        getattr(meta, "item_id", None), iterations,
                    )
                    if rk:
                        iter_errors[rk] = str(err)

                # Per-iteration accounting — drives both the audit trail
                # and the live progress log.
                all_results.update(cand_results)
                fully_verified = True
                for key in expected_keys:
                    if key in cand_results:
                        metadata_tracker.log_success(key)
                    else:
                        fully_verified = False
                        reason = iter_errors.get(
                            key, _summarise_failure_reason(metadata_list),
                        )
                        metadata_tracker.log_failure(key, reason)

                if fully_verified:
                    verified_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                failed_count += 1
                logger.error(
                    "Candidate %s failed: %s",
                    cand["candidate_id"], e,
                )
                # Mark every expected iteration key as a driver-level
                # failure so the audit trail shows the full impact of
                # the unhandled exception.
                reason = f"unhandled in driver: {type(e).__name__}: {e}"
                for key in expected_keys:
                    metadata_tracker.log_failure(key, reason)

            # Log progress after counters are updated
            if completed % 10 == 0 or completed == total:
                logger.info(
                    "Progress: %d/%d (verified: %d, failed: %d)",
                    completed, total, verified_count, failed_count,
                )

            # Incremental save every 100 candidates for resume safety.
            # If killed mid-run, at most ~100 candidates of work is lost.
            if completed % 100 == 0:
                _save_probabilities_incremental(
                    all_results, output_dir, config_version,
                    "realtime", iterations,
                )

    logger.info(
        "Verification complete: %d/%d candidates succeeded",
        verified_count, total,
    )

    # Write outputs (also runs the completeness assertion).
    gap_count = _write_verification_outputs(
        parsed_results=all_results,
        manifest=manifest,
        config=config,
        output_dir=output_dir,
        iterations=iterations,
        mode="realtime",
        metadata_tracker=metadata_tracker,
        model_name=model_name,
        strict=strict,
    )

    return 1 if gap_count > 0 and strict else 0


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
    strict: bool = True,
) -> int:
    """Write verification outputs shared by both modes.

    Produces:
    - ``probabilities.json`` — per-candidate parsed results
    - ``consensus.json`` — aggregated votes (if iterations > 1)
    - ``run.meta.json`` — LLM metadata (if tracker provided)

    Before writing, runs ``_assert_completeness()`` over
    ``parsed_results`` against the manifest's candidate × iterations key
    set; any gap is backfilled to ``metadata_tracker.stats.failed_items``
    so the resulting ``run.meta.json`` carries a per-candidate audit
    trail rather than the silent-drop pattern the Layer 1 fix targets.

    Args:
        parsed_results: Dict mapping candidate key to parsed result.
        manifest: Candidate manifest dict.
        config: Verifier config dict.
        output_dir: Output directory.
        iterations: Number of iterations used.
        mode: Execution mode ("batch" or "realtime").
        metadata_tracker: LLM metadata tracker (optional).
        threshold: Probability threshold for consensus voting.
        model_name: Resolved model name (recorded in cost estimate).
        strict: If True, surface non-zero exit code on gap. Cleanup
            paths set this False — they own their own audit trail via
            ``cleanup_history`` and would otherwise short-circuit before
            writing it.

    Returns:
        Completeness gap count (0 when complete). The caller decides
        whether to propagate this as a non-zero process exit.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Completeness assertion — must run before file writes so that
    # backfilled failed_items[] entries land in run.meta.json.
    gap_count = _assert_completeness(
        parsed_results=parsed_results,
        manifest=manifest,
        iterations=iterations,
        mode=mode,
        metadata_tracker=metadata_tracker,
        strict=strict,
    )

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

    return gap_count


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
        default="flex",
        dest="service_tier",
        help="Service tier for real-time API calls. 'flex' gives 50%% "
        "discount with 1-15 min latency. Ignored in batch mode. "
        "Default: flex.",
    )
    verify_parser.add_argument(
        "--no-strict",
        dest="strict",
        action="store_false",
        default=True,
        help=(
            "Allow incomplete results without exit-1. Default behaviour "
            "fails loud on completeness gaps so silent drops surface; "
            "pass --no-strict for deliberate sub-corpus runs or recovery "
            "campaigns where partial completion is acceptable."
        ),
    )
    verify_parser.set_defaults(func=cmd_verify)

    # --- Cleanup subcommand ---
    cleanup_parser = subparsers.add_parser(
        "cleanup",
        help="Re-verify missing candidates with iterative retries",
    )
    cleanup_parser.add_argument(
        "--crops-dir", type=Path, required=True,
        help="Source crops directory with candidate_manifest.json",
    )
    cleanup_parser.add_argument(
        "--verified-dir", type=Path, required=True,
        help="Existing verifier output directory containing "
        "the (possibly incomplete) probabilities.json to patch",
    )
    cleanup_parser.add_argument(
        "--verifier-config", type=Path, required=True,
        help="Path to verifier config JSON",
    )
    cleanup_parser.add_argument(
        "--service-tier",
        choices=["standard", "flex"],
        default="flex",
        dest="service_tier",
        help="Service tier for real-time API calls. Default: flex.",
    )
    cleanup_parser.add_argument(
        "--workers", type=int, default=10,
        help="Parallel workers (default: 10)",
    )
    cleanup_parser.add_argument(
        "--iterations", type=int, default=1,
        help="Verifier passes per candidate (default: 1)",
    )
    cleanup_parser.add_argument(
        "--temperature", type=float, default=None,
        help="Temperature override",
    )
    cleanup_parser.add_argument(
        "--model", type=str, default=None,
        help="Override model name from config",
    )
    cleanup_parser.add_argument(
        "--thinking-level", type=str, default=None,
        help="Override thinking level from config",
    )
    cleanup_parser.add_argument(
        "--max-attempts", type=int, default=3,
        dest="max_attempts",
        help="Maximum cleanup rounds (default: 3). Each round "
        "re-attempts only the candidates still missing.",
    )
    cleanup_parser.add_argument(
        "--safe-mode-tokens", type=int, default=None,
        dest="safe_mode_tokens",
        help="Override max_output_tokens on the final attempt to "
        "prevent thinking token exhaustion (e.g., 2048).",
    )
    cleanup_parser.add_argument(
        "--dry-run", action="store_true",
        help="Identify missing candidates without making API calls",
    )
    cleanup_parser.set_defaults(func=cmd_cleanup)

    return parser


def main() -> None:
    """Parse arguments and dispatch to subcommand handler."""
    parser = _build_parser()
    args = parser.parse_args()
    exit_code = args.func(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
