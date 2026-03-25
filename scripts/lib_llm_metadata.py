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
import subprocess
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


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

    def log_failure(self, item_id: str, reason: str) -> None:
        """Log a failed item."""
        with self._lock:
            self.stats.items_failed += 1
            self.stats.failed_items.append({
                "item_id": item_id,
                "reason": reason,
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
    "google_gemini": {
        "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
        "gemini-3-flash": {"input": 0.10, "output": 0.40},
        "gemini-3-pro": {"input": 2.50, "output": 10.00},
        "gemini-3.1-pro": {"input": 2.00, "output": 12.00},
        "default": {"input": 0.10, "output": 0.40},
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


def estimate_cost(
    usage: AggregatedUsage,
    provider: str,
    model: str,
) -> dict[str, float]:
    """
    Estimate cost from aggregated token usage.

    Args:
        usage: Aggregated token usage stats.
        provider: The LLM provider.
        model: The model name.

    Returns:
        Dict with input_cost, output_cost, total_cost (in USD).
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

    input_cost = (usage.total_input_tokens / 1_000_000) * rates["input"]
    output_cost = (usage.total_output_tokens / 1_000_000) * rates["output"]

    return {
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(input_cost + output_cost, 6),
        "pricing_used": {
            "model": model,
            "input_per_1m": rates["input"],
            "output_per_1m": rates["output"],
        },
    }
