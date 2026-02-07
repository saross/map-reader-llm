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
        governor.release(actual_tokens)

    # At end of run:
    stats = governor.get_stats()

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

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


class TPMGovernor:
    """
    Adaptive concurrency governor that keeps API usage within TPM limits.

    Uses a sliding-window token ledger to track recent consumption, and
    a semaphore to control how many workers can make API calls at once.
    Concurrency is adjusted periodically based on observed TPM vs target.

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

        # Adjustment state
        self._last_adjust_time = time.monotonic()
        self._completed_since_adjust = 0

        # Lifetime statistics
        self._total_tokens = 0
        self._total_requests = 0
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

    def release(self, actual_tokens: int) -> None:
        """
        Record token consumption, release the slot, and maybe adjust.

        Workers call this after each API request completes (in a
        finally block to ensure the slot is always released).

        Args:
            actual_tokens: Actual token count from the API response.
                Pass 0 if the request failed and no tokens were
                consumed.
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

        Must be called with self._lock held.
        """
        cutoff = now - self._window_seconds
        while self._ledger and self._ledger[0].timestamp < cutoff:
            self._ledger.popleft()

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

    def _adjust_concurrency(self, now: float) -> None:
        """
        Adjust the semaphore count based on observed TPM vs target.

        Rules:
        - Over target: reduce concurrency (proportionally, max halve)
        - Under 60% of target: increase concurrency (+1, capped by
          theoretical max from observed latency)
        - Otherwise: hold steady
        """
        with self._lock:
            current_tpm = self._calculate_tpm(now)
            old_concurrency = self._concurrency
            self._last_adjust_time = now
            self._completed_since_adjust = 0

            target = self._target_tpm
            low_threshold = int(target * 0.60)

            if current_tpm > target:
                # Over target — reduce proportionally, but max halve
                ratio = target / max(current_tpm, 1)
                new_concurrency = max(
                    int(old_concurrency * max(ratio, 0.5)),
                    self._min_concurrency,
                )
            elif current_tpm < low_threshold:
                # Under 60% of target — increase by 1
                # Cap by theoretical max: how many requests could fit
                # in 1 minute at current average latency?
                new_concurrency = min(
                    old_concurrency + 1,
                    self._max_concurrency,
                )
            else:
                # Within acceptable range — hold steady
                new_concurrency = old_concurrency

            if new_concurrency != old_concurrency:
                self._apply_concurrency_change(old_concurrency, new_concurrency)
                self._adjustments.append({
                    "time_offset": round(now - self._start_time, 1),
                    "old": old_concurrency,
                    "new": new_concurrency,
                    "current_tpm": current_tpm,
                    "target_tpm": target,
                    "reason": (
                        "over_target" if current_tpm > target
                        else "under_threshold"
                    ),
                })
                self._peak_concurrency = max(
                    self._peak_concurrency, new_concurrency
                )
                self._min_observed_concurrency = min(
                    self._min_observed_concurrency, new_concurrency
                )

                logger.info(
                    "TPM Governor: concurrency %d → %d "
                    "(TPM: %d / target: %d)",
                    old_concurrency,
                    new_concurrency,
                    current_tpm,
                    target,
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
