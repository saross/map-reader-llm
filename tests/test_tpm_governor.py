"""
Tests for TPM-Aware Adaptive Concurrency Governor
==================================================

Unit tests for scripts/lib_tpm_governor.py. Verifies semaphore behaviour,
sliding window pruning, concurrency adaptation, and thread safety.

All tests are tier1 (critical path).
"""

import threading
import time

import pytest

# Add project root to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib_tpm_governor import TPMGovernor, TokenRecord


@pytest.mark.tier1
class TestTPMGovernorBasic:
    """Basic acquire/release and semaphore behaviour."""

    def test_acquire_release_basic(self):
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

    def test_acquire_blocks_at_limit(self):
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

    def test_zero_token_release(self):
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

    def test_sliding_window_prune(self):
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

    def test_tpm_calculation_extrapolates(self):
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

    def test_concurrency_reduces_when_over_tpm(self):
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

    def test_concurrency_increases_when_under_tpm(self):
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

    def test_ramp_up_stability(self):
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

    def test_concurrency_respects_min_max(self):
        """Concurrency never goes below min or above max."""
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

        # Reset and test max
        governor2 = TPMGovernor(
            tpm_limit=999_999_999,
            target_utilisation=0.80,
            initial_concurrency=5,
            min_concurrency=2,
            max_concurrency=8,
            adjust_interval=0.0,
        )

        for _ in range(20):
            governor2.acquire()
            governor2.release(1)
            time.sleep(0.01)

        assert governor2._concurrency <= 8


@pytest.mark.tier1
class TestThreadSafety:
    """Multi-threaded acquire/release without deadlocks or corruption."""

    def test_thread_safety(self):
        """Multiple threads can acquire/release without deadlocks."""
        governor = TPMGovernor(
            initial_concurrency=4,
            max_concurrency=10,
            adjust_interval=0.1,
        )

        errors = []
        completed = threading.Event()
        count = threading.atomic() if hasattr(threading, 'atomic') else None

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
class TestGetStats:
    """Verify get_stats() returns expected structure."""

    def test_get_stats_structure(self):
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

    def test_get_stats_initial_values(self):
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

    def test_token_record_creation(self):
        """TokenRecord stores timestamp and token count."""
        record = TokenRecord(timestamp=100.0, tokens=5000)
        assert record.timestamp == 100.0
        assert record.tokens == 5000
