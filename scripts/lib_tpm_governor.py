"""
TPM-Aware Adaptive Concurrency Governor
========================================

Description:
    Controls the effective concurrency of API requests to stay within
    Tokens Per Minute (TPM) limits. Uses a semaphore + sliding-window
    token ledger to dynamically adjust how many workers can make API
    calls simultaneously.

    Workers call acquire() before each API request and release() after.
    The governor adjusts concurrency every `adjust_interval` seconds
    based on observed TPM usage vs the configured target.

    Key insight: when the API is fast (~6s/tile), fewer workers are
    needed to hit the TPM ceiling. When the API is slow (~20min/tile),
    many workers can safely run in parallel. The governor adapts
    automatically to current API conditions.

Rate-limit awareness:
    The governor distinguishes between two failure modes that produce
    identical TPM readings (low throughput):

    1. Slow API (high latency, no 429s): ramp up aggressively using
       latency-informed gap-proportional scaling.
    2. Rate limited (429 errors): halve immediately, enter cooldown
       to prevent re-escalation.

    Workers pass `was_rate_limited` and `latency_seconds` to release()
    so the governor can distinguish these cases and respond correctly.

Architecture:
    The governor wraps API calls inside process_single_tile(), not at
    executor submission. The ThreadPoolExecutor's max_workers stays high
    (the pool ceiling), while the governor's semaphore is the actual
    throttle. Retries also go through the governor.

Usage:
    from scripts.lib_tpm_governor import TPMGovernor

    governor = TPMGovernor(
        tpm_limit=1_000_000,
        tokens_per_request=20_000,
        max_concurrency=60,
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

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenRecord:
    """A single record of tokens consumed at a point in time."""

    timestamp: float  # time.monotonic() value
    tokens: int


@dataclass
class LatencyRecord:
    """A single record of successful request latency."""

    timestamp: float  # time.monotonic() value
    latency: float    # seconds
    tokens: int       # tokens consumed


class TPMGovernor:
    """
    Adaptive concurrency governor that keeps API usage within TPM limits.

    Uses a sliding-window token ledger to track recent consumption, and
    a semaphore to control how many workers can make API calls at once.
    Concurrency is adjusted periodically based on observed TPM vs target,
    with priority given to rate-limit signals over throughput signals.

    Priority-based adjustment rules:
        1. Rate limited (429s in window) -> halve, enter cooldown
        2. Over target (TPM > target) -> proportional reduction
        3. Under 60% of target -> latency-informed ramp-up (or +1
           during cooldown / cold start)
        4. Within range -> hold steady

    Args:
        tpm_limit: Maximum tokens per minute allowed by the API.
        tokens_per_request: Estimated tokens per request (used for
            theoretical max calculation). ~20K for image, ~1.5K for text.
        target_utilisation: Fraction of tpm_limit to target (0.0-1.0).
            Lower values leave more headroom for bursts.
        initial_concurrency: Starting number of concurrent API slots.
            Conservative start prevents initial burst of 429s.
        min_concurrency: Floor for concurrency (never go below this).
        max_concurrency: Ceiling for concurrency (never go above this).
        window_seconds: Sliding window duration for TPM calculation.
        adjust_interval: Seconds between concurrency adjustments.
        cooldown_seconds: Duration after a 429 during which only +1
            scale-up is permitted. Must be greater than window_seconds
            to have effect — while 429 events remain in the sliding
            window, the rate_limited priority (halving) takes
            precedence; the cooldown provides cautious +1 recovery
            in the gap between the window expiry and the cooldown
            expiry. Default 90s gives a 30s cautious recovery window
            after the 60s default sliding window.
    """

    def __init__(
        self,
        tpm_limit: int = 1_000_000,
        tokens_per_request: int = 20_000,
        target_utilisation: float = 0.80,
        initial_concurrency: int = 4,
        min_concurrency: int = 1,
        max_concurrency: int = 60,
        window_seconds: float = 60.0,
        adjust_interval: float = 10.0,
        cooldown_seconds: float = 90.0,
    ):
        # Validate concurrency bounds early to surface configuration
        # errors before any threads are spawned
        if min_concurrency < 1:
            raise ValueError("min_concurrency must be >= 1")
        if max_concurrency < min_concurrency:
            raise ValueError(
                "max_concurrency must be >= min_concurrency"
            )

        self._tpm_limit = tpm_limit
        self._tokens_per_request = tokens_per_request
        self._target_tpm = int(tpm_limit * target_utilisation)
        self._min_concurrency = min_concurrency
        self._max_concurrency = max_concurrency
        self._window_seconds = window_seconds
        self._adjust_interval = adjust_interval
        self._cooldown_seconds = cooldown_seconds

        # Concurrency control — semaphore is the actual throttle.
        # initial_concurrency is clamped to max_concurrency but not
        # to min_concurrency, allowing a conservative cold start.
        self._concurrency = min(initial_concurrency, max_concurrency)
        self._semaphore = threading.Semaphore(self._concurrency)

        # Number of workers currently holding a semaphore slot.
        # Used by the drain logic in release() to decide whether
        # to absorb a returned slot when concurrency is reduced.
        self._active_count = 0

        # Sliding window token ledger (thread-safe via _lock)
        self._lock = threading.Lock()
        self._ledger: deque[TokenRecord] = deque()

        # Rate-limit tracking — timestamps of 429 events within
        # the sliding window, plus the most recent for cooldown
        self._rate_limit_events: deque[float] = deque()
        self._last_rate_limit_time: float = 0.0

        # Latency tracking — successful request latencies within
        # the sliding window, used to calculate sustainable concurrency
        self._latency_records: deque[LatencyRecord] = deque()

        # Adjustment state
        self._last_adjust_time = time.monotonic()
        self._completed_since_adjust = 0

        # Lifetime statistics
        self._total_tokens = 0
        self._total_requests = 0
        self._total_rate_limits = 0
        self._adjustments: list[dict] = []
        self._peak_concurrency = self._concurrency
        self._min_observed_concurrency = self._concurrency
        self._start_time = time.monotonic()

    def acquire(self) -> None:
        """
        Block until a concurrency slot is available.

        Workers call this before each API request. The semaphore
        controls how many API calls can be in-flight simultaneously.
        """
        self._semaphore.acquire()
        with self._lock:
            self._active_count += 1

    def release(
        self,
        actual_tokens: int,
        *,
        was_rate_limited: bool = False,
        latency_seconds: float | None = None,
    ) -> None:
        """
        Record token consumption, release the slot, and maybe adjust.

        Workers call this after each API request completes (in a
        finally block to ensure the slot is always released).

        Args:
            actual_tokens: Actual token count from the API response.
                Pass 0 if the request failed and no tokens were
                consumed.
            was_rate_limited: True if the API returned a 429 error
                for this request. Triggers immediate aggressive
                downscaling on the next adjustment.
            latency_seconds: Wall-clock duration of the API call in
                seconds. Only pass for successful requests (non-429,
                non-zero tokens) — error latencies would pollute the
                average used for sustainable concurrency calculation.
        """
        now = time.monotonic()

        with self._lock:
            self._active_count -= 1

            # Record this request in the sliding window
            self._ledger.append(
                TokenRecord(timestamp=now, tokens=actual_tokens)
            )
            self._total_tokens += actual_tokens
            self._total_requests += 1
            self._completed_since_adjust += 1

            # Record rate-limit event if flagged
            if was_rate_limited:
                self._rate_limit_events.append(now)
                self._last_rate_limit_time = now
                self._total_rate_limits += 1

            # Record latency for successful requests only — errors
            # and 429s have uninformative latency (instant rejection
            # or timeout) that would pollute the average
            if latency_seconds is not None and actual_tokens > 0:
                self._latency_records.append(
                    LatencyRecord(
                        timestamp=now,
                        latency=latency_seconds,
                        tokens=actual_tokens,
                    )
                )

            # Prune stale entries outside the window
            self._prune_ledger(now)

            # Check if it is time to adjust concurrency.
            # Require at least 3 completed requests since the last
            # adjustment to avoid reacting to noise during ramp-up.
            should_adjust = (
                now - self._last_adjust_time >= self._adjust_interval
                and self._completed_since_adjust >= 3
            )

            # Drain logic: when _adjust_concurrency() lowers the
            # target, it does not manipulate the semaphore directly.
            # Instead, workers returning slots check whether there
            # are still more active workers than the new target. If
            # so, the slot is absorbed (not released back to the
            # semaphore), naturally reducing effective concurrency
            # as workers finish their in-flight requests.
            absorb_slot = self._active_count >= self._concurrency

        # Release the semaphore slot only if not absorbing.
        # Performed outside the lock to avoid holding both the lock
        # and the semaphore simultaneously.
        if not absorb_slot:
            self._semaphore.release()

        # Adjust concurrency if needed (acquires lock internally)
        if should_adjust:
            self._adjust_concurrency(now)

    def get_stats(self) -> dict:
        """
        Return governor statistics for metadata/logging.

        All field reads are performed inside the lock to ensure a
        consistent snapshot -- without this, concurrent adjustments
        could produce internally contradictory stats (e.g.,
        total_requests from before an adjustment paired with
        current_tpm from after).

        Returns:
            Dictionary with current state and lifetime statistics.
        """
        with self._lock:
            now = time.monotonic()
            current_tpm = self._calculate_tpm(now)
            elapsed = now - self._start_time
            avg_latency, _avg_tokens = self._calculate_avg_latency()
            return {
                "tpm_limit": self._tpm_limit,
                "target_tpm": self._target_tpm,
                "current_tpm": current_tpm,
                "current_concurrency": self._concurrency,
                "peak_concurrency": self._peak_concurrency,
                "min_observed_concurrency": (
                    self._min_observed_concurrency
                ),
                "total_tokens": self._total_tokens,
                "total_requests": self._total_requests,
                "total_rate_limits": self._total_rate_limits,
                "rate_limits_in_window": len(
                    self._rate_limit_events
                ),
                "avg_latency_seconds": (
                    round(avg_latency, 2)
                    if avg_latency is not None
                    else None
                ),
                "adjustments": len(self._adjustments),
                "adjustment_history": self._adjustments[-20:],
                "elapsed_seconds": round(elapsed, 1),
            }

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _prune_ledger(self, now: float) -> None:
        """
        Remove entries older than the sliding window.

        Prunes the token ledger, rate-limit event deque, and latency
        record deque. Must be called with self._lock held.
        """
        cutoff = now - self._window_seconds
        while self._ledger and self._ledger[0].timestamp < cutoff:
            self._ledger.popleft()
        while (
            self._rate_limit_events
            and self._rate_limit_events[0] < cutoff
        ):
            self._rate_limit_events.popleft()
        while (
            self._latency_records
            and self._latency_records[0].timestamp < cutoff
        ):
            self._latency_records.popleft()

    def _calculate_tpm(self, now: float) -> int:
        """
        Calculate current tokens-per-minute from the sliding window.

        Extrapolates to a full minute if the window is shorter than
        60 seconds (e.g., early in the run).

        Must be called with self._lock held.

        Args:
            now: Current monotonic time.

        Returns:
            Estimated tokens per minute.
        """
        self._prune_ledger(now)

        if not self._ledger:
            return 0

        window_tokens = sum(r.tokens for r in self._ledger)

        # Calculate effective window span
        oldest = self._ledger[0].timestamp
        window_span = now - oldest

        if window_span < 1.0:
            # Too little data to extrapolate meaningfully
            return 0

        # Extrapolate to a full minute
        return int(window_tokens * (60.0 / window_span))

    def _calculate_avg_latency(
        self,
    ) -> tuple[float | None, float | None]:
        """
        Calculate average latency and tokens from recent records.

        Must be called with self._lock held.

        Returns:
            (avg_latency, avg_tokens) tuple. Returns (None, None) if
            fewer than 5 latency records are in the sliding window —
            too few samples for a reliable estimate.
        """
        if len(self._latency_records) < 5:
            return (None, None)
        total_latency = sum(
            r.latency for r in self._latency_records
        )
        total_tokens = sum(
            r.tokens for r in self._latency_records
        )
        count = len(self._latency_records)
        return (total_latency / count, total_tokens / count)

    def _adjust_concurrency(self, now: float) -> None:
        """
        Adjust concurrency using a priority-based state machine.

        Priority order:
            1. Rate limited (429s in window) -> halve immediately
            2. Over target (TPM > target) -> proportional reduction
            3. Under 60% of target -> latency-informed ramp-up
               (or +1 during cooldown / cold start)
            4. Within range -> hold steady

        The sustainable concurrency formula answers: "how many
        concurrent workers would produce target TPM at the currently
        observed API speed?"

            sustainable = target_tpm * avg_latency / (avg_tokens * 60)
        """
        with self._lock:
            current_tpm = self._calculate_tpm(now)
            old_concurrency = self._concurrency
            self._last_adjust_time = now
            self._completed_since_adjust = 0

            target = self._target_tpm
            low_threshold = int(target * 0.60)

            # Determine whether we're in post-429 cooldown
            in_cooldown = (
                self._last_rate_limit_time > 0
                and (now - self._last_rate_limit_time)
                < self._cooldown_seconds
            )

            # --- Priority 1: Rate limited ---
            if len(self._rate_limit_events) > 0:
                new_concurrency = max(
                    old_concurrency // 2,
                    self._min_concurrency,
                )
                reason = "rate_limited"

            # --- Priority 2: Over target ---
            elif current_tpm > target:
                ratio = target / max(current_tpm, 1)
                new_concurrency = max(
                    int(old_concurrency * max(ratio, 0.5)),
                    self._min_concurrency,
                )
                reason = "over_target"

            # --- Priority 3: Under threshold ---
            elif current_tpm < low_threshold:
                avg_latency, avg_tokens = (
                    self._calculate_avg_latency()
                )

                # 3a: In cooldown — cautious +1 only
                if in_cooldown:
                    new_concurrency = min(
                        old_concurrency + 1,
                        self._max_concurrency,
                    )
                    reason = "under_threshold_cooldown"

                # 3b: Latency data available — gap-proportional ramp
                elif avg_latency is not None:
                    sustainable = (
                        target * avg_latency
                        / (avg_tokens * 60)
                    )
                    sustainable = min(
                        sustainable, self._max_concurrency
                    )

                    if old_concurrency < sustainable:
                        gap = sustainable - old_concurrency
                        step = max(1, int(gap) // 3)
                        # Safety cap: no single jump > 25% of max
                        step = min(
                            step,
                            max(1, self._max_concurrency // 4),
                        )
                        new_concurrency = min(
                            old_concurrency + step,
                            self._max_concurrency,
                        )
                        reason = "under_threshold_ramp"
                    else:
                        # At or above sustainable — hold
                        new_concurrency = old_concurrency
                        reason = "at_sustainable"

                # 3c: Cold start — conservative +1
                else:
                    new_concurrency = min(
                        old_concurrency + 1,
                        self._max_concurrency,
                    )
                    reason = "under_threshold_cold"

            # --- Priority 4: Within range ---
            else:
                new_concurrency = old_concurrency
                reason = "within_range"

            if new_concurrency != old_concurrency:
                self._apply_concurrency_change(
                    old_concurrency, new_concurrency
                )
                self._adjustments.append({
                    "time_offset": round(
                        now - self._start_time, 1
                    ),
                    "old": old_concurrency,
                    "new": new_concurrency,
                    "current_tpm": current_tpm,
                    "target_tpm": target,
                    "reason": reason,
                })
                self._peak_concurrency = max(
                    self._peak_concurrency, new_concurrency
                )
                self._min_observed_concurrency = min(
                    self._min_observed_concurrency, new_concurrency
                )

                logger.info(
                    "TPM Governor: concurrency %d -> %d "
                    "(TPM: %d / target: %d, reason: %s)",
                    old_concurrency,
                    new_concurrency,
                    current_tpm,
                    target,
                    reason,
                )

    def _apply_concurrency_change(
        self, old_concurrency: int, new_concurrency: int
    ) -> None:
        """
        Adjust the semaphore to match new concurrency level.

        Must be called with self._lock held.

        To increase: release extra slots into the semaphore so
        blocked workers can proceed immediately.

        To decrease: only update self._concurrency (the target).
        The drain logic in release() compares _active_count against
        _concurrency and absorbs returned slots when workers still
        exceed the new target, naturally reducing capacity without
        needing to acquire semaphore slots here.

        Args:
            old_concurrency: Previous concurrency level.
            new_concurrency: Desired concurrency level.
        """
        if new_concurrency > old_concurrency:
            # Increase: release additional slots into the semaphore
            for _ in range(new_concurrency - old_concurrency):
                self._semaphore.release()
        # Decrease: no semaphore manipulation needed. The drain
        # logic in release() handles it once self._concurrency is
        # updated below.

        self._concurrency = new_concurrency
