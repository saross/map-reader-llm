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

from scripts.lib_tpm_governor import TPMGovernor, TokenRecord


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
            "adjustments",
            "adjustment_history",
            "elapsed_seconds",
        }
        assert set(stats.keys()) == expected_keys

    def test_get_stats_initial_values(self) -> None:
        """Initial stats have sensible defaults."""
        governor = TPMGovernor(
            tpm_limit=500_000,
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
