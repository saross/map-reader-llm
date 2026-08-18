"""
LLM Response Metadata Tracking Module
=====================================

Description:
    Provides standardised metadata capture for LLM API responses across multiple
    providers (Google Gemini, Anthropic Claude, OpenAI). Designed for comprehensive
    tracking of tokens, costs, timing, errors, and response quality metrics.

    This module supports the experimental infrastructure by ensuring all API
    interactions are fully auditable for reproducibility and cost analysis.

Supported Providers:
    - Google Generative AI (Gemini 2.0/2.5/3.0)
    - Anthropic Claude (3.5/4.0/4.5)
    - OpenAI (GPT-4/5)

Usage:
    from lib_llm_metadata import LLMMetadataTracker, extract_gemini_metadata

    tracker = LLMMetadataTracker(
        config, system_instruction, model_override=resolved_model_name,
    )

    # After each API call:
    metadata = extract_gemini_metadata(response, request_start_time)
    tracker.log_response(tile_id, metadata)

    # At end of run:
    final_metadata = tracker.finalise()

Author: Shawn Ross
Licence: Apache 2.0
"""

import hashlib
import json
import logging
import subprocess
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported Large Language Model (LLM) providers."""

    GEMINI = "google_gemini"
    CLAUDE = "anthropic_claude"
    OPENAI = "openai"
    UNKNOWN = "unknown"


class FinishReason(Enum):
    """
    Normalised finish/stop reasons across providers.

    Maps provider-specific values to standardised categories:

    - Gemini: STOP=1, MAX_TOKENS=2, SAFETY=3, RECITATION=4, OTHER=5
    - Claude: end_turn, max_tokens, stop_sequence, tool_use
    - OpenAI: stop, length, content_filter, tool_calls
    """

    SUCCESS = "success"           # Natural completion (STOP, end_turn, stop)
    MAX_TOKENS = "max_tokens"     # Hit token limit
    SAFETY = "safety"             # Safety/content filter blocked
    TOOL_USE = "tool_use"         # Model called a tool
    RECITATION = "recitation"     # Gemini: blocked for citation reasons
    ERROR = "error"               # API or parsing error
    UNKNOWN = "unknown"           # Unrecognised reason


@dataclass
class TokenUsage:
    """
    Token usage breakdown for a single Application Programming Interface (API) response.

    Fields are provider-agnostic; providers that don't support
    certain fields will have them set to 0 or None.
    """

    # Core token counts (all providers)
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    # Caching (Gemini, Claude, OpenAI)
    cached_input_tokens: int = 0          # Tokens read from cache
    cache_creation_tokens: int = 0        # Claude: tokens used to create cache

    # Reasoning/thinking tokens
    reasoning_tokens: int = 0             # OpenAI GPT-5/o-series: hidden chain-of-thought
    thoughts_tokens: int = 0              # Gemini: thinking tokens (thinking_level param)

    # Tool/function calling tokens (Gemini)
    tool_use_tokens: int = 0              # Tokens for tool-related prompts

    # Audio tokens (OpenAI multimodal)
    audio_input_tokens: int = 0
    audio_output_tokens: int = 0

    # Prediction tokens (OpenAI)
    accepted_prediction_tokens: int = 0
    rejected_prediction_tokens: int = 0


@dataclass
class SafetyRating:
    """Safety rating for a single category (Gemini-specific)."""

    category: str
    probability: str  # NEGLIGIBLE, LOW, MEDIUM, HIGH
    blocked: bool = False


@dataclass
class LLMResponseMetadata:
    """
    Comprehensive metadata for a single LLM API response.

    This dataclass captures all available metadata from any supported
    provider. Fields not applicable to a provider are left as defaults.
    """

    # Identification
    request_id: str | None = None      # Provider-assigned ID (Claude, OpenAI)
    item_id: str | None = None         # Our identifier (tile_id, candidate_id)

    # Model information
    provider: str = "unknown"             # google_gemini, anthropic_claude, openai
    model_requested: str = ""             # Model we asked for
    model_used: str = ""                  # Model actually used (from response)
    model_version: str | None = None   # Gemini: modelVersion field
    system_fingerprint: str | None = None  # OpenAI: backend config fingerprint

    # Token usage
    tokens: TokenUsage = field(default_factory=TokenUsage)

    # Token modality breakdown (Gemini: TEXT, IMAGE, AUDIO, VIDEO, DOCUMENT)
    # Each key maps to a list of {"modality": str, "count": int} dicts
    modality_breakdown: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    # Traffic type (Gemini: ON_DEMAND vs PROVISIONED_THROUGHPUT)
    traffic_type: str | None = None

    # Completion status
    finish_reason: str = "unknown"        # Normalised: success, max_tokens, safety, etc.
    raw_finish_reason: str = ""           # Original value from API

    # Safety (Gemini)
    safety_blocked: bool = False
    safety_ratings: list[dict[str, Any]] = field(default_factory=list)

    # Prompt-level safety (Gemini) — errata E23
    prompt_safety_ratings: list[dict[str, Any]] = field(default_factory=list)
    prompt_block_reason: str | None = None

    # Citation metadata (Gemini) — errata E23
    citation_metadata: dict[str, Any] | None = None

    # Grounding (Gemini with Google Search)
    grounding_used: bool = False
    grounding_queries: list[str] = field(default_factory=list)
    grounding_sources: list[dict[str, str]] = field(default_factory=list)

    # Timing
    request_timestamp: str | None = None   # ISO format
    response_timestamp: str | None = None  # ISO format
    latency_ms: int = 0

    # Retry information
    attempt_number: int = 1
    retry_reason: str | None = None

    # Response quality
    response_empty: bool = False
    parse_success: bool = True
    parse_error: str | None = None

    # Raw response text (optional, for debugging)
    raw_response_length: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, handling nested dataclasses."""
        return asdict(self)


@dataclass
class AggregatedUsage:
    """Aggregated token usage across all responses in a run."""

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cached_tokens: int = 0
    total_reasoning_tokens: int = 0       # OpenAI reasoning
    total_thoughts_tokens: int = 0        # Gemini thinking
    total_tool_use_tokens: int = 0        # Tool/function calling
    total_tokens: int = 0

    # Per-provider breakdown (if mixed providers used)
    by_provider: dict[str, dict[str, int]] = field(default_factory=dict)


@dataclass
class ExecutionStats:
    """Execution statistics for a run."""

    items_processed: int = 0
    items_failed: int = 0
    items_skipped: int = 0

    # Retry tracking
    retries_total: int = 0
    retries_rate_limit: int = 0      # 429 errors
    retries_server_error: int = 0    # 5xx errors
    retries_timeout: int = 0         # Deadline exceeded
    retries_other: int = 0

    # Finish reason distribution
    finish_reason_counts: dict[str, int] = field(default_factory=dict)

    # Safety
    safety_blocks: int = 0

    # Parsing
    parse_failures: int = 0
    empty_responses: int = 0

    # Detailed logs
    completed_items: list[str] = field(default_factory=list)
    failed_items: list[dict[str, Any]] = field(default_factory=list)
    retry_details: list[dict[str, Any]] = field(default_factory=list)


class LLMMetadataTracker:
    """
    Thread-safe metadata tracker for LLM API runs.

    Aggregates per-response metadata into run-level statistics
    and provides comprehensive audit trails.

    Usage:
        tracker = LLMMetadataTracker(
            config, system_instruction, model_override=resolved_model,
        )

        # For each API call:
        metadata = extract_gemini_metadata(response, start_time)
        tracker.log_response("tile_001", metadata)

        # At end:
        final = tracker.finalise()
    """

    def __init__(
        self,
        config: dict[str, Any],
        system_instruction: str,
        script_name: str = "unknown",
        script_version: str = "unknown",
        model_override: str | None = None,
    ) -> None:
        """
        Initialise the metadata tracker.

        Args:
            config: The prompt/experiment configuration dict.
            system_instruction: The system instruction text (for hashing and
                persisting in output metadata).
            script_name: Name of the calling script.
            script_version: Version of the calling script.
            model_override: If the model was overridden via CLI (e.g.,
                ``--model gemini-3.1-pro``), pass the resolved model name
                here. This ensures ``configuration.model`` in the output
                metadata reflects the actual model used, not the static
                default in the config JSON. Fixes E42 metadata bug where
                ``config.get("model")`` returned the config default even
                when a CLI override was active.
        """
        self.run_id = str(uuid.uuid4())
        self.start_time = datetime.now(timezone.utc)
        self.config = config
        self.model_override = model_override
        self.system_instruction_text = system_instruction or ""
        self.system_instruction_hash = hashlib.sha256(
            (system_instruction or "").encode('utf-8')
        ).hexdigest()
        self.library_hash = self._compute_library_hash(config)
        self.script_name = script_name
        self.script_version = script_version

        self._lock = threading.Lock()

        # Aggregated statistics
        self.usage = AggregatedUsage()
        self.stats = ExecutionStats()

        # Per-item metadata (optional detailed logging)
        self.response_metadata: list[LLMResponseMetadata] = []
        self._store_per_item = True  # Can be disabled for memory efficiency

        # Results summary (task-specific)
        self.results_summary: dict[str, Any] = {}

    @staticmethod
    def _compute_library_hash(config: dict[str, Any]) -> str:
        """
        Compute a SHA-256 hash of the example library composition.

        Hashes the list of examples (path, label, category) from the config
        to produce a unique fingerprint for each library variant. This
        distinguishes conditions that share the same system instruction but
        use different example sets.

        Args:
            config: The prompt/experiment configuration dict, expected to
                contain an 'examples' key with a list of example dicts.

        Returns:
            Hex digest of the library hash, or "no_examples" if the config
            has no examples list.
        """
        import json

        examples = config.get("examples", [])
        if not examples:
            return "no_examples"

        # Normalise to a stable representation: sorted list of (path, label, category)
        # tuples serialised as JSON. Sorting ensures order-independence.
        normalised = sorted(
            (ex.get("path", ""), ex.get("label", ""), ex.get("category", ""))
            for ex in examples
        )
        canonical = json.dumps(normalised, sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def log_response(
        self,
        item_id: str,
        metadata: LLMResponseMetadata,
        store_detailed: bool = True,
    ) -> None:
        """
        Log metadata from a single API response.

        Args:
            item_id: Identifier for the item processed (e.g., tile_id).
            metadata: The extracted response metadata.
            store_detailed: Whether to store full per-item metadata.
        """
        with self._lock:
            # Update item ID if not set
            if not metadata.item_id:
                metadata.item_id = item_id

            # Aggregate token usage
            self.usage.total_input_tokens += metadata.tokens.input_tokens
            self.usage.total_output_tokens += metadata.tokens.output_tokens
            self.usage.total_cached_tokens += metadata.tokens.cached_input_tokens
            self.usage.total_reasoning_tokens += metadata.tokens.reasoning_tokens
            self.usage.total_thoughts_tokens += metadata.tokens.thoughts_tokens
            self.usage.total_tool_use_tokens += metadata.tokens.tool_use_tokens
            self.usage.total_tokens += metadata.tokens.total_tokens

            # Provider-specific tracking
            provider = metadata.provider
            if provider not in self.usage.by_provider:
                self.usage.by_provider[provider] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "request_count": 0,
                }
            self.usage.by_provider[provider]["input_tokens"] += metadata.tokens.input_tokens
            self.usage.by_provider[provider]["output_tokens"] += metadata.tokens.output_tokens
            self.usage.by_provider[provider]["total_tokens"] += metadata.tokens.total_tokens
            self.usage.by_provider[provider]["request_count"] += 1

            # Finish reason distribution
            reason = metadata.finish_reason
            self.stats.finish_reason_counts[reason] = (
                self.stats.finish_reason_counts.get(reason, 0) + 1
            )

            # Track issues
            if metadata.safety_blocked:
                self.stats.safety_blocks += 1
            if not metadata.parse_success:
                self.stats.parse_failures += 1
            if metadata.response_empty:
                self.stats.empty_responses += 1

            # Store detailed metadata if requested
            if store_detailed and self._store_per_item:
                self.response_metadata.append(metadata)

    def log_success(self, item_id: str) -> None:
        """Log a successful item processing."""
        with self._lock:
            self.stats.items_processed += 1
            self.stats.completed_items.append(item_id)

    #: Failure categories that are also parse failures. Kept as a set so the
    #: mapping from a caller's category string to the summary counter is
    #: explicit rather than inferred from the free-text reason.
    _PARSE_FAILURE_CATEGORIES = frozenset({"parse", "json_parse"})

    def log_failure(
        self, item_id: str, reason: str, category: str | None = None,
    ) -> None:
        """Log a failed item, and attribute it to a summary counter.

        ``parse_failures`` was previously incremented only inside
        :meth:`log_response`, from ``metadata.parse_success``. That flag
        describes whether the *API envelope* parsed — so a response that
        arrived cleanly and whose JSON body then failed to parse downstream
        was recorded as ``parse_failures: 0`` while the item was genuinely
        lost. Six passes of the 2026-08-18 grid run carried exactly that
        contradiction: one tile lost each, ``parse_failures: 0``, and
        ``finish_reason_counts`` reporting unbroken success.

        ``finish_reason_counts`` remains the API's own verdict and is
        deliberately not rewritten here — the call really did finish
        successfully. The categorised counter is what distinguishes "the model
        answered" from "we could use the answer".

        Args:
            item_id: Identifier of the failed item (usually a tile filename).
            reason: Free-text explanation, recorded verbatim.
            category: Machine-readable class, e.g. ``"parse"``, ``"api"``,
                ``"io"``. ``None`` records the failure without attributing it
                to a category counter.
        """
        with self._lock:
            self.stats.items_failed += 1
            if category in self._PARSE_FAILURE_CATEGORIES:
                self.stats.parse_failures += 1
            self.stats.failed_items.append({
                "item_id": item_id,
                "reason": reason,
                "category": category,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    def log_skip(self, item_id: str, reason: str = "already_processed") -> None:
        """Log a skipped item."""
        with self._lock:
            self.stats.items_skipped += 1

    def log_retry(
        self,
        item_id: str,
        attempt: int,
        reason: str,
        error_type: str = "other",
    ) -> None:
        """
        Log a retry attempt.

        Args:
            item_id: The item being retried.
            attempt: Attempt number (1-indexed).
            reason: Description of why retry was needed.
            error_type: Category: "rate_limit", "server_error", "timeout", "other".
        """
        with self._lock:
            self.stats.retries_total += 1

            if error_type == "rate_limit":
                self.stats.retries_rate_limit += 1
            elif error_type == "server_error":
                self.stats.retries_server_error += 1
            elif error_type == "timeout":
                self.stats.retries_timeout += 1
            else:
                self.stats.retries_other += 1

            self.stats.retry_details.append({
                "item_id": item_id,
                "attempt": attempt,
                "reason": reason,
                "error_type": error_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    def update_results_summary(self, summary: dict[str, Any]) -> None:
        """Update the task-specific results summary."""
        with self._lock:
            self.results_summary.update(summary)

    def set_per_item_storage(self, enabled: bool) -> None:
        """Enable or disable per-item metadata storage."""
        with self._lock:
            self._store_per_item = enabled

    @staticmethod
    def get_git_revision() -> str:
        """Get the current git commit hash."""
        try:
            return subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                stderr=subprocess.DEVNULL,
            ).decode('ascii').strip()
        except Exception:
            return "unknown"

    def finalise(self, include_per_item: bool = False) -> dict[str, Any]:
        """
        Finalise and return the complete metadata for the run.

        Acquires the internal lock to ensure a consistent snapshot of
        aggregated statistics, even if called before worker threads have
        fully drained (defensive; callers should join workers first).

        Args:
            include_per_item: Include detailed per-item metadata
                (can be large; default False).

        Returns:
            Complete metadata dictionary suitable for JSON serialisation.
        """
        end_time = datetime.now(timezone.utc)
        duration = (end_time - self.start_time).total_seconds()

        with self._lock:
            result = {
                "run_id": self.run_id,
                "timestamp": {
                    "start": self.start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration_seconds": duration,
                },
                "environment": {
                    "git_commit": self.get_git_revision(),
                    "script": self.script_name,
                    "script_version": self.script_version,
                },
                "configuration": {
                    "version": self.config.get("version"),
                    "model": (
                        self.model_override
                        if self.model_override is not None
                        else self.config.get("model")
                    ),
                    "instruction_file": self.config.get(
                        "instruction_file", "unknown"
                    ),
                    "system_instruction_hash": self.system_instruction_hash,
                    "system_instruction_text": self.system_instruction_text,
                    "library_hash": self.library_hash,
                    "temperature": self.config.get("temperature"),
                    "max_output_tokens": self.config.get(
                        "max_output_tokens"
                    ),
                    "thinking_level": self.config.get("thinking_level"),
                    "tile_size": self.config.get("tile_size"),
                    "include_example_images": self.config.get(
                        "include_example_images", True
                    ),
                    "example_count": len(
                        self.config.get("examples", [])
                    ),
                    "full_config_snapshot": self.config,
                },
                "execution_stats": asdict(self.stats),
                "usage_stats": asdict(self.usage),
                "results_summary": self.results_summary,
            }

            if include_per_item and self.response_metadata:
                result["per_item_metadata"] = [
                    m.to_dict() for m in self.response_metadata
                ]

        return result


# =============================================================================
# Provider-Specific Metadata Extraction Functions
# =============================================================================

def extract_gemini_metadata(
    response: Any,
    request_start: datetime,
    model_requested: str = "",
    item_id: str = "",
    attempt: int = 1,
) -> LLMResponseMetadata:
    """
    Extract metadata from a Google Gemini API response.

    Args:
        response: The GenerateContentResponse from google.generativeai.
        request_start: Timestamp when request was initiated.
        model_requested: The model name we requested.
        item_id: Identifier for the item being processed.
        attempt: Attempt number (for retries).

    Returns:
        LLMResponseMetadata with all available fields populated.
    """
    response_time = datetime.now(timezone.utc)
    latency_ms = int((response_time - request_start).total_seconds() * 1000)

    metadata = LLMResponseMetadata(
        item_id=item_id,
        provider=LLMProvider.GEMINI.value,
        model_requested=model_requested,
        request_timestamp=request_start.isoformat(),
        response_timestamp=response_time.isoformat(),
        latency_ms=latency_ms,
        attempt_number=attempt,
    )

    # Token usage
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        um = response.usage_metadata
        metadata.tokens = TokenUsage(
            input_tokens=getattr(um, 'prompt_token_count', 0) or 0,
            output_tokens=getattr(um, 'candidates_token_count', 0) or 0,
            total_tokens=getattr(um, 'total_token_count', 0) or 0,
            cached_input_tokens=getattr(um, 'cached_content_token_count', 0) or 0,
            thoughts_tokens=getattr(um, 'thoughts_token_count', 0) or 0,
            tool_use_tokens=getattr(um, 'tool_use_prompt_token_count', 0) or 0,
        )

        # Traffic type (ON_DEMAND vs PROVISIONED_THROUGHPUT)
        traffic_type = getattr(um, 'traffic_type', None)
        if traffic_type is not None:
            metadata.traffic_type = str(traffic_type)

        # Modality breakdown for research analysis
        # Shows token distribution across TEXT, IMAGE, AUDIO, VIDEO, DOCUMENT
        prompt_details = getattr(um, 'prompt_tokens_details', None)
        if prompt_details:
            metadata.modality_breakdown["prompt"] = [
                {"modality": str(m.modality), "count": m.token_count}
                for m in prompt_details
                if hasattr(m, "modality") and hasattr(m, "token_count")
            ]

        candidates_details = getattr(um, 'candidates_tokens_details', None)
        if candidates_details:
            metadata.modality_breakdown["candidates"] = [
                {"modality": str(m.modality), "count": m.token_count}
                for m in candidates_details
                if hasattr(m, "modality") and hasattr(m, "token_count")
            ]

        cache_details = getattr(um, 'cache_tokens_details', None)
        if cache_details:
            metadata.modality_breakdown["cache"] = [
                {"modality": str(m.modality), "count": m.token_count}
                for m in cache_details
                if hasattr(m, "modality") and hasattr(m, "token_count")
            ]

    # Model version (if available)
    if hasattr(response, 'model_version'):
        metadata.model_version = response.model_version
        metadata.model_used = response.model_version
    else:
        metadata.model_used = model_requested

    # Finish reason and candidates
    if hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]

        # Raw finish reason (Gemini uses integers)
        raw_reason = getattr(candidate, 'finish_reason', None)
        metadata.raw_finish_reason = str(raw_reason) if raw_reason else ""

        # Normalise finish reason
        # Gemini: 1=STOP, 2=MAX_TOKENS, 3=SAFETY, 4=RECITATION, 5=OTHER
        reason_map = {
            1: FinishReason.SUCCESS,
            2: FinishReason.MAX_TOKENS,
            3: FinishReason.SAFETY,
            4: FinishReason.RECITATION,
            5: FinishReason.UNKNOWN,
        }
        if isinstance(raw_reason, int):
            metadata.finish_reason = reason_map.get(
                raw_reason, FinishReason.UNKNOWN
            ).value
        elif raw_reason:
            # Handle string enum values
            reason_str = str(raw_reason).upper()
            if "STOP" in reason_str:
                metadata.finish_reason = FinishReason.SUCCESS.value
            elif "MAX" in reason_str or "TOKEN" in reason_str:
                metadata.finish_reason = FinishReason.MAX_TOKENS.value
            elif "SAFETY" in reason_str:
                metadata.finish_reason = FinishReason.SAFETY.value
            else:
                metadata.finish_reason = FinishReason.UNKNOWN.value

        # Safety ratings (candidate-level)
        if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
            for rating in candidate.safety_ratings:
                metadata.safety_ratings.append({
                    "category": str(getattr(rating, 'category', '')),
                    "probability": str(getattr(rating, 'probability', '')),
                    "blocked": getattr(rating, 'blocked', False),
                })
                if getattr(rating, 'blocked', False):
                    metadata.safety_blocked = True

        # Citation metadata — errata E23
        # Previously silently discarded; now captured for audit
        if hasattr(candidate, 'citation_metadata') and candidate.citation_metadata:
            try:
                cm = candidate.citation_metadata
                citations = []
                for src in getattr(cm, 'citation_sources', []) or []:
                    citations.append({
                        "start_index": getattr(src, 'start_index', None),
                        "end_index": getattr(src, 'end_index', None),
                        "uri": getattr(src, 'uri', None),
                        "licence": getattr(src, 'license', None),
                    })
                if citations:
                    metadata.citation_metadata = {"citations": citations}
            except Exception:
                pass  # Graceful default — citation_metadata stays None

        # Check for content
        if hasattr(candidate, 'content') and candidate.content:
            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                # Has content
                try:
                    text = response.text
                    metadata.raw_response_length = len(text) if text else 0
                    metadata.response_empty = metadata.raw_response_length == 0
                except Exception:
                    metadata.response_empty = True
            else:
                metadata.response_empty = True
        else:
            metadata.response_empty = True
    else:
        metadata.response_empty = True
        metadata.finish_reason = FinishReason.ERROR.value

    # Prompt feedback (blocking at prompt level)
    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
        pf = response.prompt_feedback

        # Capture prompt block reason value — errata E23
        # Previously only checked existence, discarded actual value
        if hasattr(pf, 'block_reason') and pf.block_reason:
            metadata.prompt_block_reason = str(pf.block_reason)
            metadata.safety_blocked = True
            metadata.finish_reason = FinishReason.SAFETY.value

        # Capture prompt-level safety ratings — errata E23
        # Previously only candidate-level ratings were captured
        if hasattr(pf, 'safety_ratings') and pf.safety_ratings:
            for rating in pf.safety_ratings:
                metadata.prompt_safety_ratings.append({
                    "category": str(getattr(rating, 'category', '')),
                    "probability": str(getattr(rating, 'probability', '')),
                    "blocked": getattr(rating, 'blocked', False),
                })

    # Grounding metadata (if Google Search grounding was used)
    if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
        gm = response.grounding_metadata
        metadata.grounding_used = True
        if hasattr(gm, 'web_search_queries'):
            metadata.grounding_queries = list(gm.web_search_queries or [])
        if hasattr(gm, 'grounding_chunks'):
            for chunk in (gm.grounding_chunks or []):
                if hasattr(chunk, 'web'):
                    metadata.grounding_sources.append({
                        "title": getattr(chunk.web, 'title', ''),
                        "uri": getattr(chunk.web, 'uri', ''),
                    })

    return metadata


def extract_claude_metadata(
    response: Any,
    request_start: datetime,
    model_requested: str = "",
    item_id: str = "",
    attempt: int = 1,
) -> LLMResponseMetadata:
    """
    Extract metadata from an Anthropic Claude API response.

    Args:
        response: The Message response from anthropic client.
        request_start: Timestamp when request was initiated.
        model_requested: The model name we requested.
        item_id: Identifier for the item being processed.
        attempt: Attempt number (for retries).

    Returns:
        LLMResponseMetadata with all available fields populated.
    """
    response_time = datetime.now(timezone.utc)
    latency_ms = int((response_time - request_start).total_seconds() * 1000)

    metadata = LLMResponseMetadata(
        item_id=item_id,
        provider=LLMProvider.CLAUDE.value,
        model_requested=model_requested,
        request_timestamp=request_start.isoformat(),
        response_timestamp=response_time.isoformat(),
        latency_ms=latency_ms,
        attempt_number=attempt,
    )

    # Request ID
    if hasattr(response, 'id'):
        metadata.request_id = response.id

    # Model used
    if hasattr(response, 'model'):
        metadata.model_used = response.model
    else:
        metadata.model_used = model_requested

    # Token usage
    if hasattr(response, 'usage') and response.usage:
        usage = response.usage
        metadata.tokens = TokenUsage(
            input_tokens=getattr(usage, 'input_tokens', 0) or 0,
            output_tokens=getattr(usage, 'output_tokens', 0) or 0,
            cached_input_tokens=getattr(usage, 'cache_read_input_tokens', 0) or 0,
            cache_creation_tokens=getattr(usage, 'cache_creation_input_tokens', 0) or 0,
        )
        # Calculate total
        metadata.tokens.total_tokens = (
            metadata.tokens.input_tokens +
            metadata.tokens.output_tokens +
            metadata.tokens.cache_creation_tokens
        )

    # Stop reason
    if hasattr(response, 'stop_reason'):
        raw_reason = response.stop_reason
        metadata.raw_finish_reason = str(raw_reason) if raw_reason else ""

        reason_map = {
            "end_turn": FinishReason.SUCCESS,
            "max_tokens": FinishReason.MAX_TOKENS,
            "stop_sequence": FinishReason.SUCCESS,
            "tool_use": FinishReason.TOOL_USE,
        }
        metadata.finish_reason = reason_map.get(
            raw_reason, FinishReason.UNKNOWN
        ).value

    # Check for content
    if hasattr(response, 'content') and response.content:
        total_length = 0
        for block in response.content:
            if hasattr(block, 'text'):
                total_length += len(block.text)
        metadata.raw_response_length = total_length
        metadata.response_empty = total_length == 0
    else:
        metadata.response_empty = True

    return metadata


def extract_openai_metadata(
    response: Any,
    request_start: datetime,
    model_requested: str = "",
    item_id: str = "",
    attempt: int = 1,
) -> LLMResponseMetadata:
    """
    Extract metadata from an OpenAI API response.

    Args:
        response: The ChatCompletion response from openai client.
        request_start: Timestamp when request was initiated.
        model_requested: The model name we requested.
        item_id: Identifier for the item being processed.
        attempt: Attempt number (for retries).

    Returns:
        LLMResponseMetadata with all available fields populated.
    """
    response_time = datetime.now(timezone.utc)
    latency_ms = int((response_time - request_start).total_seconds() * 1000)

    metadata = LLMResponseMetadata(
        item_id=item_id,
        provider=LLMProvider.OPENAI.value,
        model_requested=model_requested,
        request_timestamp=request_start.isoformat(),
        response_timestamp=response_time.isoformat(),
        latency_ms=latency_ms,
        attempt_number=attempt,
    )

    # Request ID
    if hasattr(response, 'id'):
        metadata.request_id = response.id

    # Model used and system fingerprint
    if hasattr(response, 'model'):
        metadata.model_used = response.model
    else:
        metadata.model_used = model_requested

    if hasattr(response, 'system_fingerprint'):
        metadata.system_fingerprint = response.system_fingerprint

    # Token usage (with detailed breakdown for GPT-5)
    if hasattr(response, 'usage') and response.usage:
        usage = response.usage
        tokens = TokenUsage(
            input_tokens=getattr(usage, 'prompt_tokens', 0) or 0,
            output_tokens=getattr(usage, 'completion_tokens', 0) or 0,
            total_tokens=getattr(usage, 'total_tokens', 0) or 0,
        )

        # Prompt token details
        if hasattr(usage, 'prompt_tokens_details') and usage.prompt_tokens_details:
            ptd = usage.prompt_tokens_details
            tokens.cached_input_tokens = getattr(ptd, 'cached_tokens', 0) or 0
            tokens.audio_input_tokens = getattr(ptd, 'audio_tokens', 0) or 0

        # Completion token details (GPT-5 reasoning tokens)
        if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details:
            ctd = usage.completion_tokens_details
            tokens.reasoning_tokens = getattr(ctd, 'reasoning_tokens', 0) or 0
            tokens.audio_output_tokens = getattr(ctd, 'audio_tokens', 0) or 0
            tokens.accepted_prediction_tokens = getattr(ctd, 'accepted_prediction_tokens', 0) or 0
            tokens.rejected_prediction_tokens = getattr(ctd, 'rejected_prediction_tokens', 0) or 0

        metadata.tokens = tokens

    # Finish reason from first choice
    if hasattr(response, 'choices') and response.choices:
        choice = response.choices[0]

        if hasattr(choice, 'finish_reason'):
            raw_reason = choice.finish_reason
            metadata.raw_finish_reason = str(raw_reason) if raw_reason else ""

            reason_map = {
                "stop": FinishReason.SUCCESS,
                "length": FinishReason.MAX_TOKENS,
                "content_filter": FinishReason.SAFETY,
                "tool_calls": FinishReason.TOOL_USE,
                "function_call": FinishReason.TOOL_USE,
            }
            metadata.finish_reason = reason_map.get(
                raw_reason, FinishReason.UNKNOWN
            ).value

            if raw_reason == "content_filter":
                metadata.safety_blocked = True

        # Check for content
        if hasattr(choice, 'message') and choice.message:
            msg = choice.message
            if hasattr(msg, 'content') and msg.content:
                metadata.raw_response_length = len(msg.content)
                metadata.response_empty = False
            else:
                metadata.response_empty = True
        else:
            metadata.response_empty = True
    else:
        metadata.response_empty = True

    return metadata


def create_error_metadata(
    error: Exception,
    request_start: datetime,
    provider: str,
    model_requested: str,
    item_id: str,
    attempt: int,
) -> LLMResponseMetadata:
    """
    Create metadata for a failed API request.

    Args:
        error: The exception that occurred.
        request_start: When the request started.
        provider: The LLM provider.
        model_requested: The model we tried to use.
        item_id: The item being processed.
        attempt: Attempt number.

    Returns:
        LLMResponseMetadata representing the error.
    """
    response_time = datetime.now(timezone.utc)
    latency_ms = int((response_time - request_start).total_seconds() * 1000)

    return LLMResponseMetadata(
        item_id=item_id,
        provider=provider,
        model_requested=model_requested,
        model_used="",
        request_timestamp=request_start.isoformat(),
        response_timestamp=response_time.isoformat(),
        latency_ms=latency_ms,
        attempt_number=attempt,
        finish_reason=FinishReason.ERROR.value,
        raw_finish_reason=type(error).__name__,
        parse_success=False,
        parse_error=str(error),
        response_empty=True,
    )


# =============================================================================
# Cost Estimation Utilities
# =============================================================================

# Pricing as of January 2026 (USD per 1M tokens)
# Update these as pricing changes
PRICING = {
    # Verified against cloud.google.com/vertex-ai/generative-ai/pricing
    # on 2026-03-27. Prices are per 1M tokens (standard tier, ≤200K
    # context). Batch API discounts are applied separately via the
    # batch_discount multiplier in cost_estimate output.
    "google_gemini": {
        "gemini-2.0-flash-lite": {"input": 0.075, "output": 0.30},
        "gemini-2.0-flash": {"input": 0.15, "output": 0.60},
        "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
        "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
        "gemini-3-flash-preview": {"input": 0.50, "output": 3.00},
        "gemini-3.1-flash-lite": {"input": 0.25, "output": 1.50},
        "gemini-3-pro": {"input": 2.50, "output": 10.00},
        "gemini-3.1-pro": {"input": 2.00, "output": 12.00},
        "gemini-3.1-pro-preview": {"input": 2.00, "output": 12.00},
        "default": {"input": 0.50, "output": 3.00},
    },
    "anthropic_claude": {
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "claude-opus-4-5": {"input": 15.00, "output": 75.00},
        "default": {"input": 3.00, "output": 15.00},
    },
    "openai": {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-5": {"input": 5.00, "output": 20.00},
        "gpt-5.2": {"input": 5.00, "output": 20.00},
        "default": {"input": 2.50, "output": 10.00},
    },
}


#: Discount applied to Gemini real-time **flex** traffic. Flex carries the
#: same 50 % reduction as the async Batch API — the project moved from batch
#: to flex for simplicity once that became true — so a run priced at list
#: rates overstates the actual bill by a factor of two.
#:
#: Recording the list price as though it were the bill is not a rounding
#: matter: it silently doubled every cost-efficiency figure derived from run
#: metadata, and left two internal sources (this metadata and the audited
#: ``pareto_v2.json`` model, which does apply the discount) disagreeing by
#: exactly 2x with nothing in either artefact to say which was right.
FLEX_DISCOUNT = 0.5

#: Discount for the Google async Batch API. Identical in size to the flex
#: discount; kept as a separate constant because they are separate commercial
#: terms and may diverge.
BATCH_API_DISCOUNT = 0.5


def estimate_cost(
    usage: AggregatedUsage,
    provider: str,
    model: str,
    discount: float = 1.0,
    discount_reason: str | None = None,
) -> dict[str, float]:
    """
    Estimate cost from aggregated token usage.

    Records BOTH the list price and the amount actually billed, so a reader
    can always tell which basis a figure is on. ``total_cost_usd`` is the
    **billed** amount — the number anyone comparing against an invoice or
    computing cost-efficiency wants — while ``list_total_cost_usd`` preserves
    the undiscounted figure.

    Historical metadata written before 2026-08-18 records list price in
    ``total_cost_usd`` for real-time runs (no discount was applied) and billed
    price for Batch API runs (a 0.5 multiplier was applied after the fact).
    The ``cost_basis`` field distinguishes them: its absence means the older,
    ambiguous convention.

    Args:
        usage: Aggregated token usage stats.
        provider: The LLM provider.
        model: The model name.
        discount: Multiplier applied to list price to get the billed amount.
            1.0 means list price is the bill. Use :data:`FLEX_DISCOUNT` for
            Gemini real-time flex and :data:`BATCH_API_DISCOUNT` for the async
            Batch API.
        discount_reason: Human-readable justification, recorded alongside the
            multiplier so the number can be audited without reading this code.

    Returns:
        Dict with billed input/output/total cost, the list-price equivalents,
        and a ``pricing_used`` block carrying the rates, the discount, and the
        basis.
    """
    pricing_table = PRICING.get(provider, PRICING.get("google_gemini"))

    # Find model pricing (fuzzy match on model name, longest match wins
    # to avoid e.g. "gpt-4o" matching before "gpt-4o-mini")
    model_lower = model.lower()
    rates = pricing_table.get("default")
    best_match_len = 0
    for model_key, model_rates in pricing_table.items():
        if model_key != "default" and model_key in model_lower:
            if len(model_key) > best_match_len:
                rates = model_rates
                best_match_len = len(model_key)

    list_input_cost = (usage.total_input_tokens / 1_000_000) * rates["input"]
    list_output_cost = (usage.total_output_tokens / 1_000_000) * rates["output"]
    input_cost = list_input_cost * discount
    output_cost = list_output_cost * discount

    return {
        # Billed amounts — what the invoice will show.
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(input_cost + output_cost, 6),
        # List-price equivalents, kept so the discount is auditable and so a
        # figure quoted on either basis can be reconciled with the other.
        "list_input_cost_usd": round(list_input_cost, 6),
        "list_output_cost_usd": round(list_output_cost, 6),
        "list_total_cost_usd": round(list_input_cost + list_output_cost, 6),
        "cost_basis": "billed" if discount != 1.0 else "list",
        "pricing_used": {
            "model": model,
            "input_per_1m": rates["input"],
            "output_per_1m": rates["output"],
            "discount": discount,
            "discount_reason": discount_reason or (
                "no discount applied" if discount == 1.0 else "unspecified"
            ),
        },
    }


# =========================================================================
# Resume-Mode Meta Merging
# =========================================================================
#
# Resume runs (e.g. proposer recovery against an existing GeoJSON) write
# a per-pass ``*.meta.json`` containing only the resume-batch statistics.
# Without merging, this overwrites the original (pre-resume) meta and
# breaks downstream cost aggregation. The helpers below are extracted
# verbatim from ``scripts/merge_recovery_meta.py`` so the merge can run
# inline at write time. The standalone CLI in ``merge_recovery_meta.py``
# remains for already-corrupted historical runs.


def _sum_dicts(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Element-wise sum two dicts of numeric values; missing keys treated as 0."""
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict):
            out[k] = _sum_dicts(out.get(k, {}), v)
        else:
            out[k] = (out.get(k, 0) or 0) + (v or 0)
    return out


def merge_meta(original: dict[str, Any], recovery: dict[str, Any]) -> dict[str, Any]:
    """Merge a recovery meta.json into an original meta.json.

    See ``scripts/merge_recovery_meta.py`` module docstring for
    field-by-field semantics.

    Args:
        original: The pre-recovery meta.json contents.
        recovery: The post-recovery meta.json contents (only the recovery run).

    Returns:
        Merged meta dict.
    """
    merged = dict(original)  # shallow copy at top level

    # ---- timestamp: start from original, end from recovery, durations sum ----
    o_ts = original.get("timestamp", {})
    r_ts = recovery.get("timestamp", {})
    merged["timestamp"] = {
        "start": o_ts.get("start"),
        "end": r_ts.get("end") or o_ts.get("end"),
        "duration_seconds": (
            (o_ts.get("duration_seconds") or 0.0)
            + (r_ts.get("duration_seconds") or 0.0)
        ),
    }

    # ---- execution_stats ----
    o_es = original.get("execution_stats", {})
    r_es = recovery.get("execution_stats", {})
    o_completed = list(o_es.get("completed_items", []))
    r_completed = list(r_es.get("completed_items", []))
    # Combine completed items, dedup by ID (recovery wins on duplicate)
    seen = set()
    combined_completed: list[str] = []
    for item in o_completed + r_completed:
        if item not in seen:
            combined_completed.append(item)
            seen.add(item)

    # The recovery-run's failed_items represents the residual still-failing
    # tiles. The original's failed_items is now obsolete (most/all recovered).
    r_failed_raw = list(r_es.get("failed_items", []))

    # Defensive cleanup: any failed_items entry whose item_id appears in the
    # combined completed_items list is stale (the item was actually processed
    # successfully in either the original or recovery pass). This protects
    # against historical drift where failed_items was not refreshed after a
    # successful retry — see docs/notes for the post-mortem.
    combined_completed_set = set(combined_completed)

    def _failed_item_id_local(entry: Any) -> str | None:
        if isinstance(entry, dict):
            return entry.get("item_id")
        if isinstance(entry, str):
            return entry
        return None

    r_failed: list[Any] = []
    defensively_recovered_ids: list[str] = []
    for entry in r_failed_raw:
        item_id = _failed_item_id_local(entry)
        if item_id is not None and item_id in combined_completed_set:
            defensively_recovered_ids.append(item_id)
        else:
            r_failed.append(entry)

    if defensively_recovered_ids:
        logger.warning(
            "merge_meta: dropped %d failed_items entry/entries whose ids "
            "appear in completed_items (historical drift). Examples: %s",
            len(defensively_recovered_ids),
            defensively_recovered_ids[:5],
        )

    merged["execution_stats"] = {
        "items_processed": (
            (o_es.get("items_processed") or 0)
            + (r_es.get("items_processed") or 0)
        ),
        "items_failed": len(r_failed),
        "items_skipped": (
            (o_es.get("items_skipped") or 0)
            + (r_es.get("items_skipped") or 0)
        ),
        "retries_total": (
            (o_es.get("retries_total") or 0)
            + (r_es.get("retries_total") or 0)
        ),
        "retries_rate_limit": (
            (o_es.get("retries_rate_limit") or 0)
            + (r_es.get("retries_rate_limit") or 0)
        ),
        "retries_server_error": (
            (o_es.get("retries_server_error") or 0)
            + (r_es.get("retries_server_error") or 0)
        ),
        "retries_timeout": (
            (o_es.get("retries_timeout") or 0)
            + (r_es.get("retries_timeout") or 0)
        ),
        "retries_other": (
            (o_es.get("retries_other") or 0)
            + (r_es.get("retries_other") or 0)
        ),
        "finish_reason_counts": _sum_dicts(
            o_es.get("finish_reason_counts", {}),
            r_es.get("finish_reason_counts", {}),
        ),
        "safety_blocks": (
            (o_es.get("safety_blocks") or 0)
            + (r_es.get("safety_blocks") or 0)
        ),
        "parse_failures": (
            (o_es.get("parse_failures") or 0)
            + (r_es.get("parse_failures") or 0)
        ),
        "empty_responses": (
            (o_es.get("empty_responses") or 0)
            + (r_es.get("empty_responses") or 0)
        ),
        "completed_items": combined_completed,
        "failed_items": r_failed,
        "retry_details": (
            list(o_es.get("retry_details", []))
            + list(r_es.get("retry_details", []))
        ),
    }

    # ---- usage_stats: sum tokens ----
    o_us = original.get("usage_stats", {})
    r_us = recovery.get("usage_stats", {})
    merged["usage_stats"] = _sum_dicts(o_us, r_us)
    # _sum_dicts may have inadvertently summed numeric fields inside
    # by_provider — that's correct behaviour for token counts and request counts.

    # ---- cost_estimate: sum numeric fields, keep pricing_used from original ----
    o_ce = original.get("cost_estimate", {}) or {}
    r_ce = recovery.get("cost_estimate", {}) or {}
    merged["cost_estimate"] = {
        "input_cost_usd": (
            (o_ce.get("input_cost_usd") or 0.0)
            + (r_ce.get("input_cost_usd") or 0.0)
        ),
        "output_cost_usd": (
            (o_ce.get("output_cost_usd") or 0.0)
            + (r_ce.get("output_cost_usd") or 0.0)
        ),
        "total_cost_usd": (
            (o_ce.get("total_cost_usd") or 0.0)
            + (r_ce.get("total_cost_usd") or 0.0)
        ),
        "pricing_used": o_ce.get("pricing_used") or r_ce.get("pricing_used"),
    }

    # ---- per_item_metadata: combine, recovery wins on duplicate item_id ----
    o_pim = original.get("per_item_metadata", []) or []
    r_pim = recovery.get("per_item_metadata", []) or []
    # Build dict by item_id; recovery overwrites original
    combined_pim: dict[str, dict[str, Any]] = {}
    for item in o_pim:
        iid = item.get("item_id")
        if iid:
            combined_pim[iid] = item
    for item in r_pim:
        iid = item.get("item_id")
        if iid:
            combined_pim[iid] = item
    # Preserve original ordering, append new items at the end
    merged_pim: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in o_pim:
        iid = item.get("item_id")
        if iid:
            merged_pim.append(combined_pim[iid])
            seen_ids.add(iid)
    for iid, item in combined_pim.items():
        if iid not in seen_ids:
            merged_pim.append(item)
    merged["per_item_metadata"] = merged_pim

    # ---- recovery_history: track the merge operation ----
    initial_failed_ids = sorted(
        fi["item_id"] if isinstance(fi, dict) else fi
        for fi in o_es.get("failed_items", [])
    )
    still_failing_ids = sorted(
        fi["item_id"] if isinstance(fi, dict) else fi
        for fi in r_failed
    )
    recovered_ids = sorted(set(initial_failed_ids) - set(still_failing_ids))

    history = list(merged.get("recovery_history", []))
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "initial_failed": len(initial_failed_ids),
        "recovered": len(recovered_ids),
        "still_failing": len(still_failing_ids),
        "still_failing_ids": still_failing_ids,
        "recovered_ids": recovered_ids,
        "recovery_cost_usd": r_ce.get("total_cost_usd"),
        "recovery_duration_seconds": r_ts.get("duration_seconds"),
        "recovery_run_id": recovery.get("run_id"),
    }
    if defensively_recovered_ids:
        entry["defensively_recovered_ids"] = sorted(set(defensively_recovered_ids))
        entry["defensively_recovered"] = len(set(defensively_recovered_ids))
        entry["defensive_cleanup_note"] = (
            "merge_meta filtered failed_items entries whose ids were also "
            "present in completed_items (historical drift). These are "
            "treated as recovered and tracked here for the audit trail."
        )
    history.append(entry)
    merged["recovery_history"] = history

    # tpm_governor: keep original (recovery's small run governor stats not
    # meaningful at scale). If recovery has one, append as a list.
    if "tpm_governor" in recovery:
        merged.setdefault("tpm_governor_recovery", []).append(
            recovery["tpm_governor"],
        )

    # results_summary: keep original (recovery may overwrite or be empty)
    if recovery.get("results_summary"):
        # Element-wise merge would be domain-specific; keep originals and
        # store the recovery summary alongside if non-empty.
        merged.setdefault("results_summary_recovery", []).append(
            recovery["results_summary"],
        )

    return merged


def merge_meta_into_existing(
    meta_path: Path,
    fresh: dict[str, Any],
) -> dict[str, Any]:
    """Return the merge of an on-disc meta with a fresh meta dict.

    If ``meta_path`` exists, read it and return ``merge_meta(existing,
    fresh)``. Otherwise return ``fresh`` unchanged. Logs a warning when
    ``execution_stats.completed_items`` overlaps between the two passes —
    a possible double-count signal.

    Args:
        meta_path: Path to a per-pass ``*.meta.json`` that may or may
            not already exist on disc.
        fresh: The freshly-finalised meta dict from the current resume
            pass.

    Returns:
        Either the merged meta dict (when ``meta_path`` existed) or the
        ``fresh`` dict as supplied.
    """
    if not meta_path.exists():
        return fresh

    with open(meta_path) as f:
        existing = json.load(f)

    # Defensive double-count guard: if any tile id appears in both
    # passes' ``completed_items`` lists, the resume manifest may not
    # have filtered correctly. Log but do not abort — ``merge_meta``
    # dedupes by id, so totals stay correct.
    existing_completed = set(
        existing.get("execution_stats", {}).get("completed_items", []),
    )
    fresh_completed = set(
        fresh.get("execution_stats", {}).get("completed_items", []),
    )
    overlap = existing_completed & fresh_completed
    if overlap:
        logger.warning(
            "Resume meta merge: %d items appear in both passes — "
            "possible double-count. Items: %s...",
            len(overlap), list(overlap)[:5],
        )

    return merge_meta(existing, fresh)
