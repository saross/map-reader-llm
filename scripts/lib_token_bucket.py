"""
Token-Bucket Rate Limiter for Google Gemini API
================================================

Description:
    Proactive rate limiter with dual RPM + TPM constraints and continuous
    capacity replenishment. Based on the proven pattern from OpenAI's
    api_request_parallel_processor.py, adapted for the Google Gemini API
    and synchronous ThreadPoolExecutor pipelines.

Key design principles:
    1. Token-aware: pre-deducts estimated tokens on acquire(), adjusts
       for actual usage on release(). No over- or under-counting.
    2. Dual constraints: tracks both Requests Per Minute (RPM) and
       Tokens Per Minute (TPM). Only dispatches when BOTH budgets allow.
    3. Continuous replenishment: capacity regenerates fractionally per
       elapsed second, matching how APIs actually enforce rolling limits
       (not fixed windows).
    4. Proactive gating: workers block in acquire() until capacity is
       available. No adaptive concurrency — the capacity itself IS the
       concurrency control.
    5. Cooldown on 429: configurable freeze on new dispatches after any
       rate-limit signal, with capacity continuing to replenish.

Architecture:
    Drop-in replacement for TPMGovernor. Workers call acquire() before
    each API request and release() after. The ThreadPoolExecutor pool
    size stays high (ceiling); the token bucket is the actual throttle.

    acquire() blocks until:
        - Not in cooldown, AND
        - available_request_capacity >= 1.0, AND
        - available_token_capacity >= tokens_per_request

    release() records:
        - Actual token usage (adjusts pre-deducted estimate)
        - Rate-limit signal (triggers cooldown)
        - Latency (for stats only — no adaptive concurrency)

Usage:
    from scripts.lib_token_bucket import TokenBucketGovernor

    governor = TokenBucketGovernor(
        tokens_per_request=20_000,
        tpm_limit=1_000_000,
        rpm_limit=2_000,
    )

    # In each worker thread:
    governor.acquire()
    try:
        response = client.models.generate_content(...)
        actual_tokens = response.usage_metadata.total_token_count
    finally:
        governor.release(
            actual_tokens,
            was_rate_limited=False,
            latency_seconds=elapsed,
        )

    # At end of run:
    stats = governor.get_stats()

Reference:
    OpenAI api_request_parallel_processor.py — the ground-truth for
    token-bucket structure, capacity replenishment, and dispatch gating.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger(__name__)


class TokenBucketGovernor:
    """
    Proactive token-bucket rate limiter with dual RPM + TPM constraints.

    Capacity replenishes continuously based on elapsed time, matching
    how APIs enforce rolling rate limits. Workers block in acquire()
    until both RPM and TPM budgets allow dispatch.

    Args:
        rpm_limit: Maximum requests per minute allowed by the API.
        tpm_limit: Maximum tokens per minute allowed by the API.
        target_utilisation: Fraction of limits to target (0.0–1.0).
            Lower values leave headroom for bursts. 0.72 is tuned
            from production experience (0.80 caused TPM overshoot).
        cooldown_seconds: Duration to freeze new dispatches after a
            429 response. Capacity continues to replenish during
            cooldown, enabling a controlled burst on resumption.
        tokens_per_request: Estimated tokens per request. Used for
            pre-deduction in acquire() and adjusted to actuals in
            release(). ~20,000 for image-track, ~1,500 for text-only.
        status_interval: Seconds between periodic status prints.
            Set to 0 to disable status output.
        initial_concurrency: Legacy arg (accepted, ignored). Logged
            for diagnostics.
        min_concurrency: Legacy arg (accepted, ignored).
        max_concurrency: Legacy arg (accepted, ignored).
    """

    def __init__(
        self,
        rpm_limit: int = 2_000,
        tpm_limit: int = 1_000_000,
        target_utilisation: float = 0.72,
        cooldown_seconds: float = 15.0,
        tokens_per_request: int = 20_000,
        status_interval: float = 10.0,
        # Legacy args accepted for drop-in compatibility with
        # TPMGovernor constructor calls in 4_detect_mounds_batch.py.
        # Capacity gating replaces explicit concurrency control.
        initial_concurrency: int | None = None,
        min_concurrency: int | None = None,
        max_concurrency: int | None = None,
    ):
        # Validate inputs — rpm_limit and tpm_limit must be positive
        # to prevent infinite loops in acquire() (capacity would never
        # replenish if either is zero).
        if rpm_limit <= 0:
            raise ValueError(
                f"rpm_limit must be > 0, got {rpm_limit}"
            )
        if tpm_limit <= 0:
            raise ValueError(
                f"tpm_limit must be > 0, got {tpm_limit}"
            )
        if target_utilisation <= 0 or target_utilisation > 1.0:
            raise ValueError(
                f"target_utilisation must be in (0.0, 1.0], "
                f"got {target_utilisation}"
            )
        if tokens_per_request <= 0:
            raise ValueError(
                f"tokens_per_request must be > 0, "
                f"got {tokens_per_request}"
            )

        self._rpm_limit = rpm_limit
        self._tpm_limit = tpm_limit
        self._target_utilisation = target_utilisation
        self._target_rpm = int(rpm_limit * target_utilisation)
        self._target_tpm = int(tpm_limit * target_utilisation)
        self._cooldown_seconds = cooldown_seconds
        self._tokens_per_request = tokens_per_request
        self._status_interval = status_interval

        # Available capacity — starts at target (not limit) to avoid
        # an initial burst above the target utilisation ceiling.
        self._available_request_capacity: float = float(self._target_rpm)
        self._available_token_capacity: float = float(self._target_tpm)

        # Timestamp of last capacity replenishment
        self._last_update_time: float = time.monotonic()

        # Cooldown state: no new dispatches until this monotonic time
        self._cooldown_until: float = 0.0

        # Thread synchronisation — single lock guards all mutable state
        self._lock = threading.Lock()

        # Periodic status printing
        self._last_status_time: float = time.monotonic()

        # Lifetime statistics
        self._total_tokens: int = 0
        self._total_requests: int = 0
        self._total_rate_limits: int = 0
        self._total_cooldown_seconds: float = 0.0
        self._start_time: float = time.monotonic()
        self._latency_sum: float = 0.0
        self._latency_count: int = 0
        self._peak_wait_seconds: float = 0.0

        # Log legacy arg usage for diagnostics
        if initial_concurrency is not None:
            logger.debug(
                "TokenBucketGovernor: initial_concurrency=%d ignored "
                "(capacity gating replaces concurrency control)",
                initial_concurrency,
            )

    def acquire(self) -> None:
        """
        Block until both RPM and TPM budgets allow a new request.

        Pre-deducts estimated tokens (tokens_per_request) and one
        request from available capacity. If insufficient capacity,
        sleeps until replenishment makes it available. If in cooldown
        after a 429, waits for cooldown to expire first.

        Thread-safe: multiple workers can call acquire() concurrently.
        The lock ensures atomic check-and-deduct; sleeping happens
        outside the lock so other threads can release() and replenish.
        """
        acquire_start = time.monotonic()

        while True:
            with self._lock:
                self._replenish()
                now = time.monotonic()

                # Periodic status output for monitoring
                self._maybe_print_status(now)

                # Priority 1: Check cooldown
                if now < self._cooldown_until:
                    wait_time = self._cooldown_until - now
                else:
                    # Priority 2: Check both capacity constraints
                    has_rpm = self._available_request_capacity >= 1.0
                    has_tpm = (
                        self._available_token_capacity
                        >= self._tokens_per_request
                    )

                    if has_rpm and has_tpm:
                        # Deduct capacity and dispatch immediately
                        self._available_request_capacity -= 1.0
                        self._available_token_capacity -= (
                            self._tokens_per_request
                        )
                        # Track peak wait time for stats
                        wait_duration = now - acquire_start
                        self._peak_wait_seconds = max(
                            self._peak_wait_seconds, wait_duration
                        )
                        return

                    # Calculate minimum wait until capacity is sufficient.
                    # The binding constraint (RPM or TPM) determines how
                    # long we need to wait for replenishment.
                    rpm_wait = 0.0
                    tpm_wait = 0.0
                    if not has_rpm:
                        rpm_deficit = (
                            1.0 - self._available_request_capacity
                        )
                        rpm_rate = self._target_rpm / 60.0
                        rpm_wait = (
                            rpm_deficit / rpm_rate
                            if rpm_rate > 0
                            else 60.0
                        )
                    if not has_tpm:
                        tpm_deficit = (
                            self._tokens_per_request
                            - self._available_token_capacity
                        )
                        tpm_rate = self._target_tpm / 60.0
                        tpm_wait = (
                            tpm_deficit / tpm_rate
                            if tpm_rate > 0
                            else 60.0
                        )

                    # Sleep for whichever constraint takes longer to fill,
                    # with a minimum of 10ms to avoid busy-spinning
                    wait_time = max(rpm_wait, tpm_wait, 0.01)

            # Sleep OUTSIDE the lock so other threads can release()
            # and replenish capacity while we wait
            time.sleep(wait_time)

    def release(
        self,
        actual_tokens: int,
        *,
        was_rate_limited: bool = False,
        latency_seconds: float | None = None,
    ) -> None:
        """
        Record actual token usage and handle rate-limit signals.

        Adjusts the pre-deducted token estimate to match actual usage.
        If the request consumed fewer tokens than estimated, the surplus
        is returned to the capacity pool. If more, the deficit is
        deducted further.

        Args:
            actual_tokens: Actual token count from the API response.
                Pass 0 if the request failed (full estimate returned
                to pool — no tokens were consumed).
            was_rate_limited: True if the API returned a 429 error.
                Triggers a cooldown period freezing new dispatches.
            latency_seconds: Wall-clock duration of the API call.
                Only pass for successful (non-429) requests. Used for
                statistics only — no adaptive concurrency.
        """
        with self._lock:
            # Adjust token capacity for actual vs estimated usage.
            # Positive delta = request used fewer tokens than estimated,
            # so return the surplus. Negative = used more, deduct extra.
            token_delta = self._tokens_per_request - actual_tokens
            self._available_token_capacity += token_delta

            # Record statistics
            self._total_tokens += actual_tokens
            self._total_requests += 1

            # Handle 429: freeze new dispatches for cooldown_seconds.
            # Multiple concurrent 429s extend cooldown (each resets
            # the timer), which is conservative and correct — if the
            # API is still returning 429s, we should still be waiting.
            if was_rate_limited:
                now = time.monotonic()
                self._cooldown_until = now + self._cooldown_seconds
                self._total_rate_limits += 1
                self._total_cooldown_seconds += self._cooldown_seconds
                print(
                    f"  [TokenBucket] 429 received — "
                    f"cooldown {self._cooldown_seconds}s "
                    f"(total 429s: {self._total_rate_limits})",
                    flush=True,
                )

            # Record latency for successful requests only — errors
            # and 429s have uninformative latency
            if latency_seconds is not None and actual_tokens > 0:
                self._latency_sum += latency_seconds
                self._latency_count += 1

    def get_stats(self) -> dict:
        """
        Return governor statistics for metadata/logging.

        Compatible with the metadata structure expected by
        4_detect_mounds_batch.py (writes to .meta.json files).

        Returns:
            Dictionary with current state and lifetime statistics.
        """
        with self._lock:
            self._replenish()
            now = time.monotonic()
            elapsed = now - self._start_time

            # Estimate current TPM from lifetime consumption.
            # Only meaningful after the first 30 seconds of running;
            # before that, report 0 to avoid noisy extrapolation.
            elapsed_minutes = elapsed / 60.0
            current_tpm = (
                int(self._total_tokens / elapsed_minutes)
                if elapsed_minutes > 0.5
                else 0
            )

            avg_latency = (
                round(self._latency_sum / self._latency_count, 2)
                if self._latency_count > 0
                else None
            )

            return {
                "governor_type": "token_bucket",
                "rpm_limit": self._rpm_limit,
                "tpm_limit": self._tpm_limit,
                "target_rpm": self._target_rpm,
                "target_tpm": self._target_tpm,
                "target_utilisation": self._target_utilisation,
                "current_tpm": current_tpm,
                "available_request_capacity": round(
                    self._available_request_capacity, 1
                ),
                "available_token_capacity": round(
                    self._available_token_capacity, 0
                ),
                "cooldown_seconds": self._cooldown_seconds,
                "tokens_per_request": self._tokens_per_request,
                "total_tokens": self._total_tokens,
                "total_requests": self._total_requests,
                "total_rate_limits": self._total_rate_limits,
                "total_cooldown_seconds": round(
                    self._total_cooldown_seconds, 1
                ),
                "avg_latency_seconds": avg_latency,
                "peak_wait_seconds": round(
                    self._peak_wait_seconds, 2
                ),
                "elapsed_seconds": round(elapsed, 1),
            }

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _replenish(self) -> None:
        """
        Replenish capacity based on elapsed time since last update.

        Adds fractional capacity continuously — e.g., if 0.5 seconds
        have elapsed and the target TPM is 720,000, adds 6,000 tokens
        (720,000 / 60 × 0.5). Capacity is capped at the target to
        prevent unbounded accumulation during idle periods.

        Must be called with self._lock held.
        """
        now = time.monotonic()
        elapsed = now - self._last_update_time
        self._last_update_time = now

        if elapsed <= 0:
            return

        # RPM replenishment: target_rpm requests per 60 seconds
        rpm_increment = elapsed * (self._target_rpm / 60.0)
        self._available_request_capacity = min(
            self._available_request_capacity + rpm_increment,
            float(self._target_rpm),
        )

        # TPM replenishment: target_tpm tokens per 60 seconds
        tpm_increment = elapsed * (self._target_tpm / 60.0)
        self._available_token_capacity = min(
            self._available_token_capacity + tpm_increment,
            float(self._target_tpm),
        )

    def _maybe_print_status(self, now: float) -> None:
        """
        Print periodic status for monitoring during long runs.

        Throttled to self._status_interval to avoid flooding output.
        Only prints when status_interval > 0.

        Must be called with self._lock held.

        Args:
            now: Current monotonic time.
        """
        if self._status_interval <= 0:
            return
        if now - self._last_status_time < self._status_interval:
            return

        self._last_status_time = now
        in_cooldown = now < self._cooldown_until
        cooldown_str = " COOLDOWN" if in_cooldown else ""

        avg_lat = (
            f"{self._latency_sum / self._latency_count:.1f}s"
            if self._latency_count > 0
            else "N/A"
        )

        print(
            f"  [TokenBucket] RPM={self._available_request_capacity:.0f}"
            f"/{self._target_rpm} "
            f"TPM={self._available_token_capacity:,.0f}"
            f"/{self._target_tpm:,} "
            f"requests={self._total_requests} "
            f"429s={self._total_rate_limits} "
            f"avg_lat={avg_lat}"
            f"{cooldown_str}",
            flush=True,
        )
