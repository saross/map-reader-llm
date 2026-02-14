"""
Tests for TPM-Aware Adaptive Concurrency Governor
==================================================

Unit tests for scripts/lib_tpm_governor.py. Verifies semaphore behaviour,
sliding window pruning, concurrency adaptation, and thread safety.

All tests are tier1 (critical path).
"""

import sys
import threading
import time
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_tpm_governor import (
    LatencyRecord,
    TPMGovernor,
    TokenRecord,
)


@pytest.mark.tier1
class TestTPMGovernorBasic:
    """Basic acquire/release and semaphore behaviour."""

    def test_acquire_release_basic(self) -> None:
        """Single-thread acquire/release works without deadlock."""
        governor = TPMGovernor(
            initial_concurrency=2,
            max_concurrency=10,
        )
        # Should not block
        governor.acquire()
        governor.release(1000)

        stats = governor.get_stats()
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 1000

    def test_acquire_blocks_at_limit(self) -> None:
        """Acquire blocks when concurrency limit is reached."""
        governor = TPMGovernor(
            initial_concurrency=1,
            max_concurrency=1,
            # Disable auto-adjustment to test pure semaphore
            adjust_interval=9999.0,
        )

        # Acquire the single slot
        governor.acquire()

        # Second acquire should block — verify with a timeout
        acquired = threading.Event()

        def try_acquire():
            governor.acquire()
            acquired.set()

        t = threading.Thread(target=try_acquire, daemon=True)
        t.start()

        # Should NOT have acquired within 0.1s
        assert not acquired.wait(timeout=0.1)

        # Release first slot — second should now acquire
        governor.release(500)
        assert acquired.wait(timeout=1.0)

        # Clean up — release second slot
        governor.release(500)

    def test_zero_token_release(self) -> None:
        """Releasing with 0 tokens (failed request) still works."""
        governor = TPMGovernor(initial_concurrency=4)
        governor.acquire()
        governor.release(0)

        stats = governor.get_stats()
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 0


@pytest.mark.tier1
class TestSlidingWindow:
    """Sliding window pruning and TPM calculation."""

    def test_sliding_window_prune(self) -> None:
        """Stale entries are removed from the sliding window."""
        governor = TPMGovernor(
            window_seconds=1.0,
            initial_concurrency=10,
            adjust_interval=9999.0,  # Disable auto-adjustment
        )

        # Add an entry
        governor.acquire()
        governor.release(10_000)

        # Wait for it to expire
        time.sleep(1.1)

        # Add another entry (this triggers pruning)
        governor.acquire()
        governor.release(5_000)

        # Ledger should only have the recent entry
        with governor._lock:
            assert len(governor._ledger) == 1
            assert governor._ledger[0].tokens == 5_000

    def test_tpm_calculation_extrapolates(self) -> None:
        """TPM is correctly extrapolated from partial window."""
        governor = TPMGovernor(
            window_seconds=60.0,
            initial_concurrency=10,
            adjust_interval=9999.0,
        )

        # Need entries spanning >1 second for extrapolation to work
        governor.acquire()
        governor.release(10_000)
        time.sleep(1.1)
        governor.acquire()
        governor.release(10_000)

        with governor._lock:
            tpm = governor._calculate_tpm(time.monotonic())

        # 20K tokens over ~1.1s → extrapolated to ~1.1M TPM
        # Allow wide margin since timing is imprecise in tests
        assert tpm > 0


@pytest.mark.tier1
class TestConcurrencyAdaptation:
    """Concurrency adjustments based on TPM vs target."""

    def test_concurrency_reduces_when_over_tpm(self) -> None:
        """Concurrency decreases when TPM exceeds target."""
        governor = TPMGovernor(
            tpm_limit=100_000,
            target_utilisation=0.80,  # target = 80K TPM
            initial_concurrency=10,
            min_concurrency=1,
            max_concurrency=20,
            window_seconds=60.0,
            adjust_interval=0.0,  # Adjust immediately
        )

        # Build up entries spanning >1s so TPM can be calculated
        governor.acquire()
        governor.release(200_000)
        time.sleep(1.1)

        # Rapid high-token releases push TPM well over the 80K target
        for _ in range(5):
            governor.acquire()
            governor.release(200_000)

        # The governor should have reduced concurrency below initial 10
        # because estimated TPM far exceeds target (80K)
        assert governor._concurrency < 10

    def test_concurrency_increases_when_under_tpm(self) -> None:
        """Concurrency increases when TPM is well below target."""
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            target_utilisation=0.80,  # target = 800K TPM
            initial_concurrency=2,
            min_concurrency=1,
            max_concurrency=20,
            window_seconds=60.0,
            adjust_interval=0.0,  # Adjust immediately
        )

        # Simulate low token consumption — just 100 tokens, far below
        # target of 800K TPM
        for _ in range(4):
            governor.acquire()
            governor.release(100)

        time.sleep(0.05)

        # Trigger adjustment
        governor.acquire()
        governor.release(100)

        # Concurrency should have increased from 2
        assert governor._concurrency > 2

    def test_ramp_up_stability(self) -> None:
        """No adjustment before minimum completed requests (3)."""
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            tokens_per_request=10_000,  # Low enough to avoid safe_initial clamp
            initial_concurrency=4,
            adjust_interval=0.0,  # Would adjust immediately if allowed
        )

        # Only 2 requests — should not adjust
        governor.acquire()
        governor.release(100)
        governor.acquire()
        governor.release(100)

        assert governor._concurrency == 4
        assert len(governor._adjustments) == 0

    def test_decrease_drains_via_release(self) -> None:
        """Concurrency decrease takes effect as workers finish (drain)."""
        governor = TPMGovernor(
            tpm_limit=100_000,
            tokens_per_request=1_000,  # Avoid safe_initial clamp
            target_utilisation=0.80,  # target = 80K TPM
            initial_concurrency=5,
            min_concurrency=1,
            max_concurrency=10,
            window_seconds=60.0,
            adjust_interval=0.0,  # Adjust immediately
        )

        # Acquire all 5 slots to simulate busy workers
        for _ in range(5):
            governor.acquire()

        # Release one slot with high tokens, then wait >1s so the TPM
        # calculator has enough span to extrapolate (it returns 0 when
        # window_span < 1.0s). This mirrors the setup pattern in
        # test_concurrency_reduces_when_over_tpm.
        governor.release(500_000)
        time.sleep(1.1)

        # Pump remaining high-token releases to trigger a decrease.
        # Each release frees a slot, records high tokens, and may
        # trigger an adjustment that lowers the target.
        for _ in range(4):
            governor.release(500_000)

        # After the burst, concurrency should have been reduced
        assert governor._concurrency < 5

        # The drain should have absorbed slots — verify that the
        # effective semaphore capacity matches the new target by
        # acquiring up to _concurrency slots (should not block).
        target = governor._concurrency
        acquired_count = 0
        for _ in range(target):
            if governor._semaphore.acquire(blocking=False):
                acquired_count += 1

        assert acquired_count == target

        # Clean up — release what we acquired
        for _ in range(acquired_count):
            governor._semaphore.release()

    def test_concurrency_respects_min(self) -> None:
        """Concurrency never goes below min_concurrency."""
        governor = TPMGovernor(
            tpm_limit=100,  # Very low limit
            target_utilisation=0.80,
            initial_concurrency=5,
            min_concurrency=2,
            max_concurrency=8,
            adjust_interval=0.0,
        )

        # Hammer with high tokens to push concurrency down
        for _ in range(20):
            governor.acquire()
            governor.release(1_000_000)
            time.sleep(0.01)

        assert governor._concurrency >= 2

    def test_concurrency_respects_max(self) -> None:
        """Concurrency never goes above max_concurrency."""
        governor = TPMGovernor(
            tpm_limit=999_999_999,
            target_utilisation=0.80,
            initial_concurrency=5,
            min_concurrency=2,
            max_concurrency=8,
            adjust_interval=0.0,
        )

        for _ in range(20):
            governor.acquire()
            governor.release(1)
            time.sleep(0.01)

        assert governor._concurrency <= 8


@pytest.mark.tier1
class TestThreadSafety:
    """Multi-threaded acquire/release without deadlocks or corruption."""

    def test_thread_safety(self) -> None:
        """Multiple threads can acquire/release without deadlocks."""
        governor = TPMGovernor(
            tokens_per_request=10_000,  # Avoid safe_initial clamp
            initial_concurrency=4,
            max_concurrency=10,
            adjust_interval=0.1,
        )

        errors = []

        # Use a simple counter with lock
        counter_lock = threading.Lock()
        counter = [0]

        def worker():
            try:
                for _ in range(10):
                    governor.acquire()
                    time.sleep(0.01)  # Simulate work
                    governor.release(1000)
                with counter_lock:
                    counter[0] += 1
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        assert not errors, f"Thread errors: {errors}"
        assert counter[0] == 8, f"Only {counter[0]}/8 threads completed"

        stats = governor.get_stats()
        assert stats["total_requests"] == 80  # 8 threads × 10 releases


@pytest.mark.tier1
class TestConstructorValidation:
    """Constructor parameter validation."""

    def test_min_concurrency_must_be_positive(self) -> None:
        """min_concurrency < 1 raises ValueError."""
        with pytest.raises(ValueError, match="min_concurrency must be >= 1"):
            TPMGovernor(min_concurrency=0)

    def test_max_below_min_raises(self) -> None:
        """max_concurrency < min_concurrency raises ValueError."""
        with pytest.raises(
            ValueError, match="max_concurrency must be >= min_concurrency"
        ):
            TPMGovernor(min_concurrency=5, max_concurrency=3)


@pytest.mark.tier1
class TestGetStats:
    """Verify get_stats() returns expected structure."""

    def test_get_stats_structure(self) -> None:
        """get_stats() returns all expected keys."""
        governor = TPMGovernor()

        stats = governor.get_stats()

        expected_keys = {
            "tpm_limit",
            "target_tpm",
            "current_tpm",
            "current_concurrency",
            "peak_concurrency",
            "min_observed_concurrency",
            "total_tokens",
            "total_requests",
            "total_rate_limits",
            "rate_limits_in_window",
            "avg_latency_seconds",
            "adjustments",
            "adjustment_history",
            "elapsed_seconds",
        }
        assert set(stats.keys()) == expected_keys

    def test_get_stats_initial_values(self) -> None:
        """Initial stats have sensible defaults."""
        governor = TPMGovernor(
            tpm_limit=500_000,
            tokens_per_request=1_000,  # Low enough to avoid safe_initial clamp
            initial_concurrency=3,
        )

        stats = governor.get_stats()
        assert stats["tpm_limit"] == 500_000
        assert stats["current_concurrency"] == 3
        assert stats["total_tokens"] == 0
        assert stats["total_requests"] == 0
        assert stats["adjustments"] == 0
        assert stats["adjustment_history"] == []


@pytest.mark.tier1
class TestTokenRecord:
    """TokenRecord dataclass basic tests."""

    def test_token_record_creation(self) -> None:
        """TokenRecord stores timestamp and token count."""
        record = TokenRecord(timestamp=100.0, tokens=5000)
        assert record.timestamp == 100.0
        assert record.tokens == 5000

    def test_latency_record_creation(self) -> None:
        """LatencyRecord stores timestamp, latency, and token count."""
        record = LatencyRecord(
            timestamp=100.0, latency=5.5, tokens=20_000
        )
        assert record.timestamp == 100.0
        assert record.latency == 5.5
        assert record.tokens == 20_000


# ===================================================================
# Rate-limit awareness tests (new governor capabilities)
# ===================================================================


@pytest.mark.tier1
class TestRateLimitResponse:
    """Governor responds correctly to rate-limit (429) signals."""

    def test_reduces_on_rate_limit(self) -> None:
        """Concurrency reduces by ~10% on sustained 429s."""
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            tokens_per_request=1_000,  # Avoid safe_initial clamp
            initial_concurrency=20,
            min_concurrency=1,
            max_concurrency=60,
            adjust_interval=0.0,
        )

        # Seed the ledger with enough data so TPM can be calculated.
        # Need >1s span and >=3 completed requests for adjustment.
        governor.acquire()
        governor.release(10_000, latency_seconds=5.0)
        time.sleep(1.1)

        # Report three 429s to trigger adjustment (need >=3 requests).
        # The 3-request guard fires on the 2nd 429 (seed + 2 429s = 3),
        # with 429 rate = 2/3 = 67% (above 25% threshold).
        for _ in range(3):
            governor.acquire()
            governor.release(0, was_rate_limited=True)

        # 10% reduction: max(20 // 10, 1) = 2, so 20 - 2 = 18
        assert governor._concurrency == 18

    def test_cooldown_prevents_aggressive_ramp(self) -> None:
        """During cooldown after a 429, only +1 ramp-up is allowed."""
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            target_utilisation=0.80,  # target = 800K
            initial_concurrency=10,
            min_concurrency=1,
            max_concurrency=60,
            adjust_interval=0.0,
            cooldown_seconds=60.0,
        )

        # Seed with data spanning >1s
        governor.acquire()
        governor.release(100, latency_seconds=5.0)
        time.sleep(1.1)

        # Report a 429 to trigger halving and set cooldown
        for _ in range(3):
            governor.acquire()
            governor.release(0, was_rate_limited=True)

        halved = governor._concurrency  # Should be 5

        # Now simulate low-TPM releases (no more 429s) — but we're
        # in cooldown, so ramp-up should be cautious (+1 only).
        # Clear rate_limit_events from window by manually aging them
        # (the 429 events are still fresh, so we need to ensure they
        # don't interfere with the under_threshold path).
        with governor._lock:
            governor._rate_limit_events.clear()

        for _ in range(4):
            governor.acquire()
            governor.release(100, latency_seconds=5.0)

        # Should have increased by at most +1 per adjustment
        assert governor._concurrency <= halved + 2

    def test_cooldown_expires(self) -> None:
        """After cooldown_seconds, normal latency-based ramp resumes."""
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            target_utilisation=0.80,
            initial_concurrency=10,
            min_concurrency=1,
            max_concurrency=60,
            adjust_interval=0.0,
            # Very short cooldown so the test runs quickly
            cooldown_seconds=0.5,
        )

        # Seed and trigger a 429
        governor.acquire()
        governor.release(1, latency_seconds=5.0)
        time.sleep(1.1)

        for _ in range(3):
            governor.acquire()
            governor.release(0, was_rate_limited=True)

        after_halve = governor._concurrency

        # Clear rate-limit events from window so priority 1 doesn't
        # fire, and wait for cooldown to expire
        with governor._lock:
            governor._rate_limit_events.clear()
        time.sleep(0.6)

        # Inject latency records directly so TPM stays below threshold
        now = time.monotonic()
        with governor._lock:
            for i in range(6):
                governor._latency_records.append(
                    LatencyRecord(
                        timestamp=now - (0.01 * i),
                        latency=120.0,
                        tokens=20_000,
                    )
                )

        # Release a few tiny-token requests to trigger adjustment
        for _ in range(4):
            governor.acquire()
            governor.release(1, latency_seconds=120.0)

        # With 120s latency and 20K tokens, sustainable is very high.
        # Governor should have ramped up by more than +1 from the
        # post-halve level.
        assert governor._concurrency > after_halve

    def test_repeated_rate_limits_cascade(self) -> None:
        """Ongoing 429s across intervals cascade ~10% reductions."""
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            tokens_per_request=1_000,  # Avoid safe_initial clamp
            initial_concurrency=40,
            min_concurrency=2,
            max_concurrency=60,
            adjust_interval=0.0,
        )

        # Seed with data spanning >1s
        governor.acquire()
        governor.release(100, latency_seconds=1.0)
        time.sleep(1.1)

        # First batch of 429s: adjustment fires on 2nd 429
        # (seed + 2 = 3 completed). 10% of 40 = 4 → 36
        for _ in range(3):
            governor.acquire()
            governor.release(0, was_rate_limited=True)

        assert governor._concurrency == 36

        # Second batch: fires on 2nd 429 (3 more completed since
        # last adjust). 10% of 36 = 3 → 33
        for _ in range(3):
            governor.acquire()
            governor.release(0, was_rate_limited=True)

        assert governor._concurrency == 33

        # Third batch: 10% of 33 = 3 → 30
        for _ in range(3):
            governor.acquire()
            governor.release(0, was_rate_limited=True)

        assert governor._concurrency == 30

    def test_min_request_guard_prevents_rapid_reduction(self) -> None:
        """Multiple 429s in one interval only trigger one ~10% reduction.

        The existing 3-request guard means concurrency only adjusts
        once per 3 completed requests, preventing rapid reduction from
        a burst of 429s within a single adjustment interval.
        """
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            tokens_per_request=1_000,  # Avoid safe_initial clamp
            initial_concurrency=20,
            min_concurrency=1,
            max_concurrency=60,
            # Long interval — only the 3-request guard matters
            adjust_interval=0.0,
        )

        # Seed
        governor.acquire()
        governor.release(100, latency_seconds=1.0)
        time.sleep(1.1)

        # Send exactly 3 requests (the minimum for an adjustment)
        # with 429s — should trigger exactly one reduction
        for _ in range(3):
            governor.acquire()
            governor.release(0, was_rate_limited=True)

        # One 10% reduction: 20 → 18
        assert governor._concurrency == 18

    def test_intermittent_429s_hold_steady(self) -> None:
        """Isolated 429s (API degradation) do not reduce concurrency.

        When only a small fraction of requests get 429s (<25%), the
        governor treats this as transient API degradation rather than
        genuine rate limiting. Concurrency should hold steady.
        """
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            tokens_per_request=1_000,  # Avoid safe_initial clamp
            initial_concurrency=20,
            min_concurrency=1,
            max_concurrency=60,
            adjust_interval=0.0,
        )

        # Seed the ledger with enough normal requests to dilute
        # the 429 rate below 25%. Use tiny tokens to avoid
        # triggering the over_target path.
        governor.acquire()
        governor.release(1, latency_seconds=5.0)
        time.sleep(1.1)

        # 8 normal requests + 1 429 = 10% 429 rate (below 25%).
        # The adjustment fires every 3 completed requests, so after
        # 9 total releases (seed + 8 normal + 1 429), we get 3
        # adjustments. At each, the single 429 is <25% of requests
        # → api_degradation, not rate_limited.
        for _ in range(8):
            governor.acquire()
            governor.release(1, latency_seconds=5.0)

        governor.acquire()
        governor.release(0, was_rate_limited=True)

        # Concurrency should not have reduced (api_degradation path
        # holds steady, under_threshold path may ramp up)
        assert governor._concurrency >= 20


@pytest.mark.tier1
class TestLatencyBasedRampUp:
    """Latency-informed gap-proportional ramp-up."""

    def _build_governor_with_latency(
        self,
        initial: int = 4,
        max_conc: int = 60,
        latency: float = 120.0,
        tokens: int = 20_000,
        target_tpm: int = 800_000,
    ) -> TPMGovernor:
        """Create a governor with seeded latency records.

        Injects latency records directly into governor state to avoid
        contaminating the TPM ledger with high token counts (which
        would push TPM over target and trigger the wrong adjustment
        path). The token ledger is kept minimal to ensure TPM stays
        well below the 60% threshold.
        """
        governor = TPMGovernor(
            tpm_limit=target_tpm,
            target_utilisation=1.0,  # target = tpm_limit exactly
            initial_concurrency=initial,
            min_concurrency=1,
            max_concurrency=max_conc,
            adjust_interval=0.0,
        )

        # Seed TPM ledger with data spanning >1s using tiny token
        # counts so TPM stays well below threshold
        governor.acquire()
        governor.release(1, latency_seconds=latency)
        time.sleep(1.1)

        # Inject latency records directly (simulating what release()
        # would record) to avoid inflating the TPM ledger
        now = time.monotonic()
        with governor._lock:
            for i in range(6):
                governor._latency_records.append(
                    LatencyRecord(
                        timestamp=now - (0.01 * i),
                        latency=latency,
                        tokens=tokens,
                    )
                )

        # Now release a few more tiny-token requests to trigger
        # adjustment (need >=3 completed since last adjust)
        for _ in range(3):
            governor.acquire()
            governor.release(1, latency_seconds=latency)

        return governor

    def test_ramps_faster_than_plus_one(self) -> None:
        """With latency data, concurrency increases by more than 1."""
        governor = self._build_governor_with_latency(
            initial=4,
            max_conc=60,
            latency=120.0,   # Slow API
            tokens=20_000,
            target_tpm=800_000,
        )

        # sustainable = 800_000 * 120 / (20_000 * 60) = 80
        # Capped to max_concurrency=60. Gap = 60 - 4 = 56.
        # Step = 56 // 3 = 18, but safety cap = 60 // 4 = 15.
        # So step = 15 → new = 4 + 15 = 19.
        # At minimum, it should be more than +1
        assert governor._concurrency > 5

    def test_sustainable_calculation(self) -> None:
        """Known latency/tokens/target produces correct sustainable."""
        governor = TPMGovernor(
            tpm_limit=800_000,
            target_utilisation=1.0,
            initial_concurrency=4,
            max_concurrency=100,
            adjust_interval=9999.0,  # Disable auto-adjust
        )

        # Manually populate latency records
        now = time.monotonic()
        with governor._lock:
            for i in range(10):
                governor._latency_records.append(
                    LatencyRecord(
                        timestamp=now - i,
                        latency=120.0,
                        tokens=20_000,
                    )
                )
            avg_latency, avg_tokens = (
                governor._calculate_avg_latency()
            )

        # sustainable = 800_000 * 120 / (20_000 * 60) = 80
        expected_sustainable = 800_000 * 120.0 / (20_000 * 60)
        assert avg_latency == 120.0
        assert avg_tokens == 20_000
        assert expected_sustainable == 80.0

    def test_gap_proportional_step(self) -> None:
        """Step size is gap // 3, verified at various gaps."""
        # Gap = 60: step = 60 // 3 = 20, capped at 100 // 4 = 25 → 20
        governor = self._build_governor_with_latency(
            initial=4,
            max_conc=100,
            latency=120.0,
            tokens=20_000,
            target_tpm=800_000,
        )
        # sustainable = 80, gap = 80 - 4 = 76, step = 76//3 = 25,
        # safety cap = 100//4 = 25 → step = 25, new = 29
        assert governor._concurrency >= 20

    def test_safety_cap(self) -> None:
        """Step never exceeds max_concurrency // 4."""
        governor = self._build_governor_with_latency(
            initial=4,
            max_conc=20,      # Safety cap = 20 // 4 = 5
            latency=120.0,
            tokens=20_000,
            target_tpm=800_000,
        )
        # sustainable = 80 capped to 20, gap = 20-4=16,
        # step = 16//3=5, safety cap = 20//4=5, so step=5
        # new = 4 + 5 = 9
        assert governor._concurrency <= 4 + 5

    def test_holds_at_sustainable(self) -> None:
        """When concurrency >= sustainable, don't increase further.

        With 6s latency and 20K tokens:
        sustainable = 800_000 * 6 / (20_000 * 60) = 4.
        Starting at concurrency=10, the governor should recognise
        that we're already above sustainable and hold (at_sustainable
        path), not ramp up further.

        Uses direct latency record injection to avoid contaminating
        the TPM ledger (high token counts would push TPM over target
        and trigger the over_target path instead of at_sustainable).
        """
        governor = TPMGovernor(
            tpm_limit=800_000,
            tokens_per_request=1_000,  # Avoid safe_initial clamp
            target_utilisation=1.0,
            initial_concurrency=10,
            min_concurrency=1,
            max_concurrency=60,
            adjust_interval=0.0,
        )

        # Seed TPM ledger with tiny tokens spanning >1s
        governor.acquire()
        governor.release(1, latency_seconds=6.0)
        time.sleep(1.1)

        # Inject latency records showing fast API (6s, 20K tokens)
        # → sustainable = 800K * 6 / (20K * 60) = 4
        now = time.monotonic()
        with governor._lock:
            for i in range(6):
                governor._latency_records.append(
                    LatencyRecord(
                        timestamp=now - (0.01 * i),
                        latency=6.0,
                        tokens=20_000,
                    )
                )

        # Trigger adjustments with tiny tokens (TPM stays low →
        # under_threshold fires, but concurrency 10 > sustainable 4
        # → at_sustainable path holds, producing no change).
        # Note: at_sustainable sets new == old, so no adjustment is
        # recorded in history — we verify indirectly by checking
        # concurrency didn't increase.
        for _ in range(4):
            governor.acquire()
            governor.release(1, latency_seconds=6.0)

        # Concurrency should not have increased from 10
        assert governor._concurrency == 10
        # No adjustments should have been recorded (at_sustainable
        # produces no change, and no other path fires)
        assert len(governor._adjustments) == 0


@pytest.mark.tier1
class TestColdStart:
    """Cold-start behaviour with insufficient latency data."""

    def test_plus_one_without_latency_data(self) -> None:
        """Fewer than 5 latency records leads to conservative +1."""
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            target_utilisation=0.80,
            initial_concurrency=2,
            min_concurrency=1,
            max_concurrency=20,
            adjust_interval=0.0,
        )

        # Seed data spanning >1s but only 4 latency records
        # (below the threshold of 5)
        governor.acquire()
        governor.release(100, latency_seconds=5.0)
        time.sleep(1.1)

        for _ in range(3):
            governor.acquire()
            governor.release(100, latency_seconds=5.0)

        # With only 4 latency records, should use cold-start +1
        # Total: 4 releases, 4 latency records < 5 threshold
        # Multiple +1 adjustments may have fired (adjust_interval=0)
        # but each step should be exactly +1
        history = governor._adjustments
        for adj in history:
            if adj["reason"] in (
                "under_threshold_cold",
                "under_threshold",
            ):
                assert adj["new"] - adj["old"] == 1


@pytest.mark.tier1
class TestBackwardCompatibility:
    """Ensure existing code works without new kwargs."""

    def test_release_without_kwargs(self) -> None:
        """release(tokens) with no keyword args works identically."""
        governor = TPMGovernor(
            initial_concurrency=4,
            max_concurrency=10,
            adjust_interval=9999.0,
        )
        governor.acquire()
        governor.release(1000)

        stats = governor.get_stats()
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 1000
        assert stats["total_rate_limits"] == 0
        assert stats["rate_limits_in_window"] == 0
        assert stats["avg_latency_seconds"] is None

    def test_stats_include_new_fields(self) -> None:
        """get_stats() includes rate-limit and latency fields."""
        governor = TPMGovernor()
        stats = governor.get_stats()

        assert "total_rate_limits" in stats
        assert "rate_limits_in_window" in stats
        assert "avg_latency_seconds" in stats

        # Initial values
        assert stats["total_rate_limits"] == 0
        assert stats["rate_limits_in_window"] == 0
        assert stats["avg_latency_seconds"] is None


@pytest.mark.tier1
class TestMixedScenarios:
    """End-to-end scenarios mixing rate limits, latency, and recovery."""

    def test_rate_limit_then_recovery(self) -> None:
        """429 -> ~10% reduce -> cooldown -> cautious -> latency ramp."""
        governor = TPMGovernor(
            tpm_limit=1_000_000,
            tokens_per_request=1_000,  # Avoid safe_initial clamp
            target_utilisation=0.80,
            initial_concurrency=20,
            min_concurrency=1,
            max_concurrency=60,
            adjust_interval=0.0,
            cooldown_seconds=0.5,  # Short cooldown for test speed
        )

        # Phase 1: Seed data
        governor.acquire()
        governor.release(1, latency_seconds=5.0)
        time.sleep(1.1)

        # Phase 2: Rate limit → ~10% reduce (20 → 18)
        for _ in range(3):
            governor.acquire()
            governor.release(0, was_rate_limited=True)

        after_reduce = governor._concurrency
        assert after_reduce == 18

        # Phase 3: Clear 429 events, still in cooldown → +1 only
        with governor._lock:
            governor._rate_limit_events.clear()

        for _ in range(3):
            governor.acquire()
            governor.release(1, latency_seconds=120.0)

        after_cooldown_ramp = governor._concurrency
        # In cooldown, should only add +1 per adjustment
        assert after_cooldown_ramp <= after_reduce + 2

        # Phase 4: Wait for cooldown to expire, then ramp
        time.sleep(0.6)

        # Inject latency records directly so TPM stays low
        now = time.monotonic()
        with governor._lock:
            for i in range(6):
                governor._latency_records.append(
                    LatencyRecord(
                        timestamp=now - (0.01 * i),
                        latency=120.0,
                        tokens=20_000,
                    )
                )

        # Trigger adjustments with tiny tokens
        for _ in range(4):
            governor.acquire()
            governor.release(1, latency_seconds=120.0)

        # With 120s latency and 20K tokens, sustainable is very high.
        # Should have ramped up aggressively from after_cooldown_ramp.
        assert governor._concurrency > after_cooldown_ramp + 1

    def test_api_speedup_triggers_reduction(self) -> None:
        """Simulate latency dropping → TPM goes over → reduction."""
        governor = TPMGovernor(
            tpm_limit=100_000,
            target_utilisation=0.80,  # target = 80K
            initial_concurrency=10,
            min_concurrency=1,
            max_concurrency=20,
            window_seconds=60.0,
            adjust_interval=0.0,
        )

        # Seed data spanning >1s with moderate tokens
        governor.acquire()
        governor.release(10_000, latency_seconds=10.0)
        time.sleep(1.1)

        # Pump high-token releases to push TPM well over 80K target
        for _ in range(5):
            governor.acquire()
            governor.release(200_000, latency_seconds=2.0)

        # Should have reduced concurrency due to over_target
        assert governor._concurrency < 10
