"""
Tests for TokenBucketGovernor
=============================

Comprehensive test suite for the proactive token-bucket rate limiter.
Tests cover:
    - Basic acquire/release flow
    - Capacity deduction and replenishment
    - Dual RPM + TPM constraint checking
    - Cooldown behaviour on 429s
    - Token adjustment (actual vs estimated)
    - Thread safety under concurrent access
    - Constructor validation
    - Stats structure and values
    - Legacy constructor arg compatibility

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import threading
import time

import pytest

from scripts.lib_token_bucket import TokenBucketGovernor


# ── Helpers ──────────────────────────────────────────────────────────

def _quick_governor(**kwargs) -> TokenBucketGovernor:
    """
    Create a governor with fast-cycling defaults for testing.

    Reduces status_interval to 0 (no prints) and sets small limits
    to make capacity exhaustion testable without long waits.
    """
    defaults = {
        "rpm_limit": 60,           # 1 request/second
        "tpm_limit": 60_000,       # 1,000 tokens/second
        "target_utilisation": 1.0, # No headroom (simpler maths)
        "cooldown_seconds": 0.5,
        "tokens_per_request": 1_000,
        "status_interval": 0,      # Suppress prints in tests
    }
    defaults.update(kwargs)
    return TokenBucketGovernor(**defaults)


# ── Basic Flow ───────────────────────────────────────────────────────

class TestBasicFlow:
    """Test acquire/release without blocking."""

    @pytest.mark.tier1
    def test_acquire_release_no_deadlock(self):
        """Basic acquire + release completes without hanging."""
        gov = _quick_governor()
        gov.acquire()
        gov.release(800)
        # If we get here, no deadlock

    @pytest.mark.tier1
    def test_multiple_acquires_within_capacity(self):
        """Multiple acquires succeed when capacity is available."""
        gov = _quick_governor(
            rpm_limit=100,
            tpm_limit=100_000,
            tokens_per_request=1_000,
        )
        # Should be able to acquire many times with full capacity
        for _ in range(10):
            gov.acquire()
            gov.release(1_000)

    @pytest.mark.tier1
    def test_zero_token_release(self):
        """Release with 0 tokens (failed request) returns estimate."""
        gov = _quick_governor(tokens_per_request=5_000)
        initial_stats = gov.get_stats()
        initial_tpm_cap = initial_stats["available_token_capacity"]

        gov.acquire()
        # Acquire deducted 5,000 tokens
        gov.release(0)
        # Release should return all 5,000 (delta = 5000 - 0 = 5000)

        stats = gov.get_stats()
        # Capacity should be back near initial (minus tiny replenishment
        # timing differences)
        assert stats["available_token_capacity"] >= initial_tpm_cap - 100


# ── Capacity Gating ──────────────────────────────────────────────────

class TestCapacityGating:
    """Test that acquire blocks when capacity is exhausted."""

    @pytest.mark.tier1
    def test_blocks_when_rpm_exhausted(self):
        """Acquire blocks when RPM capacity is zero."""
        # 1 RPM at 100% utilisation = 1 request per minute
        gov = _quick_governor(
            rpm_limit=1,
            tpm_limit=1_000_000,
            tokens_per_request=100,
        )
        # First acquire should succeed (capacity = 1.0)
        gov.acquire()
        gov.release(100)

        # Deplete RPM capacity by acquiring again immediately
        # (replenishment is ~0.017/second, so after ~0ms only ~0.0)
        gov.acquire()

        # Now RPM capacity should be ~0. Next acquire must block.
        acquired = threading.Event()

        def _try_acquire():
            gov.acquire()
            acquired.set()
            gov.release(100)

        t = threading.Thread(target=_try_acquire, daemon=True)
        t.start()
        # Should NOT acquire within 100ms (needs ~60s to replenish)
        assert not acquired.wait(timeout=0.1)

        # Release first acquire to allow replenishment path
        gov.release(100)

    @pytest.mark.tier1
    def test_blocks_when_tpm_exhausted(self):
        """Acquire blocks when TPM capacity is zero."""
        # Very small TPM so we exhaust it quickly
        gov = _quick_governor(
            rpm_limit=1000,
            tpm_limit=2_000,   # Only 2K tokens/minute
            tokens_per_request=1_000,
        )
        # First acquire succeeds (capacity = 2,000)
        gov.acquire()
        gov.release(1_000)

        # Second acquire succeeds (capacity ~1,000 + replenishment)
        gov.acquire()
        gov.release(1_000)

        # Third acquire should block (capacity ~0 + tiny replenishment)
        acquired = threading.Event()

        def _try_acquire():
            gov.acquire()
            acquired.set()
            gov.release(1_000)

        t = threading.Thread(target=_try_acquire, daemon=True)
        t.start()
        # Should NOT acquire within 100ms
        assert not acquired.wait(timeout=0.1)

    @pytest.mark.tier1
    def test_capacity_replenishes_over_time(self):
        """Capacity replenishes and unblocks waiting workers."""
        # 60 RPM = 1/second, so after 1s we get 1 request back
        gov = _quick_governor(
            rpm_limit=60,
            tpm_limit=1_000_000,
            tokens_per_request=100,
        )

        # Exhaust capacity
        for _ in range(60):
            gov.acquire()
            gov.release(100)

        # Now capacity should be near zero. Wait 0.5s for partial
        # replenishment, then try to acquire
        time.sleep(0.5)

        acquired = threading.Event()

        def _try_acquire():
            gov.acquire()
            acquired.set()
            gov.release(100)

        t = threading.Thread(target=_try_acquire, daemon=True)
        t.start()
        # Should acquire within 2s (replenishment gives ~30 RPM capacity
        # in 0.5s wait + up to 2s more)
        assert acquired.wait(timeout=2.0)


# ── Token Adjustment ─────────────────────────────────────────────────

class TestTokenAdjustment:
    """Test that release adjusts for actual vs estimated tokens."""

    @pytest.mark.tier1
    def test_surplus_returned_when_actual_less_than_estimated(self):
        """When actual < estimated, surplus tokens return to pool."""
        gov = _quick_governor(
            tpm_limit=100_000,
            tokens_per_request=10_000,
        )
        stats_before = gov.get_stats()
        cap_before = stats_before["available_token_capacity"]

        gov.acquire()
        # Acquire deducted 10,000. Release with only 5,000 actual.
        gov.release(5_000)

        stats_after = gov.get_stats()
        cap_after = stats_after["available_token_capacity"]

        # Should have returned 5,000 surplus (plus some replenishment)
        # Net deduction should be only ~5,000
        net_deduction = cap_before - cap_after
        assert net_deduction < 6_000  # Allow some timing tolerance

    @pytest.mark.tier1
    def test_deficit_deducted_when_actual_more_than_estimated(self):
        """When actual > estimated, extra tokens are deducted."""
        gov = _quick_governor(
            tpm_limit=100_000,
            tokens_per_request=10_000,
        )
        stats_before = gov.get_stats()
        cap_before = stats_before["available_token_capacity"]

        gov.acquire()
        # Acquire deducted 10,000. Release with 15,000 actual.
        gov.release(15_000)

        stats_after = gov.get_stats()
        cap_after = stats_after["available_token_capacity"]

        # Net deduction should be ~15,000 (10K pre-deduct + 5K extra)
        net_deduction = cap_before - cap_after
        assert net_deduction > 14_000  # Allow some timing tolerance


# ── Cooldown Behaviour ───────────────────────────────────────────────

class TestCooldown:
    """Test 429 cooldown behaviour."""

    @pytest.mark.tier1
    def test_cooldown_blocks_acquire(self):
        """After a 429, acquire blocks for cooldown_seconds."""
        gov = _quick_governor(
            cooldown_seconds=0.5,
            rpm_limit=1000,
            tpm_limit=1_000_000,
        )

        # Trigger cooldown
        gov.acquire()
        gov.release(0, was_rate_limited=True)

        # Next acquire should block during cooldown
        start = time.monotonic()
        gov.acquire()
        elapsed = time.monotonic() - start
        gov.release(100)

        # Should have waited approximately cooldown_seconds
        assert elapsed >= 0.4  # Allow 100ms tolerance
        assert elapsed < 1.5   # But not excessively

    @pytest.mark.tier1
    def test_cooldown_extends_on_repeated_429(self):
        """Multiple 429s extend the cooldown timer."""
        gov = _quick_governor(
            cooldown_seconds=0.5,
            rpm_limit=1000,
            tpm_limit=1_000_000,
        )

        # First 429
        gov.acquire()
        gov.release(0, was_rate_limited=True)
        time.sleep(0.3)  # Partial cooldown

        # Second 429 resets timer
        gov.acquire()  # Might block briefly
        gov.release(0, was_rate_limited=True)

        # Should need to wait another full cooldown from now
        start = time.monotonic()
        gov.acquire()
        elapsed = time.monotonic() - start
        gov.release(100)

        assert elapsed >= 0.4

    @pytest.mark.tier1
    def test_capacity_replenishes_during_cooldown(self):
        """Capacity continues to fill while in cooldown."""
        gov = _quick_governor(
            cooldown_seconds=1.0,
            rpm_limit=60,        # 1/second
            tpm_limit=60_000,    # 1000/second
            tokens_per_request=1_000,
        )

        # Exhaust some capacity
        for _ in range(30):
            gov.acquire()
            gov.release(1_000)

        stats_before = gov.get_stats()
        cap_before = stats_before["available_token_capacity"]

        # Trigger cooldown
        gov.acquire()
        gov.release(0, was_rate_limited=True)

        # Wait through cooldown — capacity should replenish
        time.sleep(1.1)

        stats_after = gov.get_stats()
        cap_after = stats_after["available_token_capacity"]

        # Capacity should have increased during cooldown
        assert cap_after > cap_before

    @pytest.mark.tier1
    def test_stats_track_cooldown(self):
        """Stats correctly count rate limits and cooldown time."""
        gov = _quick_governor(cooldown_seconds=0.3)

        gov.acquire()
        gov.release(0, was_rate_limited=True)
        gov.acquire()
        gov.release(0, was_rate_limited=True)

        stats = gov.get_stats()
        assert stats["total_rate_limits"] == 2
        assert stats["total_cooldown_seconds"] == pytest.approx(0.6, abs=0.01)


# ── Dual Constraint ──────────────────────────────────────────────────

class TestDualConstraint:
    """Test that both RPM and TPM must be satisfied."""

    @pytest.mark.tier1
    def test_rpm_is_binding_constraint(self):
        """When RPM is low and TPM is high, RPM is the bottleneck."""
        gov = _quick_governor(
            rpm_limit=1,            # Very restrictive
            tpm_limit=10_000_000,   # Very generous
            tokens_per_request=100,
        )

        # First acquire succeeds
        gov.acquire()
        gov.release(100)

        # Second should block on RPM (not TPM)
        gov.acquire()
        # After depleting RPM, the binding constraint is RPM
        gov.release(100)

        stats = gov.get_stats()
        # TPM should still have lots of capacity
        assert stats["available_token_capacity"] > 1_000_000

    @pytest.mark.tier1
    def test_tpm_is_binding_constraint(self):
        """When TPM is low and RPM is high, TPM is the bottleneck."""
        gov = _quick_governor(
            rpm_limit=10_000,        # Very generous
            tpm_limit=3_000,         # Very restrictive
            tokens_per_request=1_000,
        )

        # First three acquires succeed (3,000 token capacity)
        for _ in range(3):
            gov.acquire()
            gov.release(1_000)

        # Fourth should block on TPM
        acquired = threading.Event()

        def _try():
            gov.acquire()
            acquired.set()
            gov.release(1_000)

        t = threading.Thread(target=_try, daemon=True)
        t.start()
        assert not acquired.wait(timeout=0.1)

        # RPM should still have plenty
        stats = gov.get_stats()
        assert stats["available_request_capacity"] > 100


# ── Thread Safety ────────────────────────────────────────────────────

class TestThreadSafety:
    """Test concurrent access from multiple threads."""

    @pytest.mark.tier1
    def test_concurrent_acquire_release(self):
        """Many threads doing acquire/release without deadlock."""
        gov = _quick_governor(
            rpm_limit=600,       # 10/second
            tpm_limit=600_000,   # 10,000/second
            tokens_per_request=500,
        )

        errors = []
        completed = threading.Event()
        count = 0
        count_lock = threading.Lock()
        target = 20

        def _worker():
            nonlocal count
            try:
                gov.acquire()
                time.sleep(0.01)  # Simulate API call
                gov.release(500)
                with count_lock:
                    count += 1
                    if count >= target:
                        completed.set()
            except Exception as e:
                errors.append(str(e))

        threads = [
            threading.Thread(target=_worker, daemon=True)
            for _ in range(target)
        ]
        for t in threads:
            t.start()

        # All should complete within 10s (generous timeout)
        assert completed.wait(timeout=10.0), (
            f"Only {count}/{target} completed"
        )
        assert len(errors) == 0, f"Thread errors: {errors}"

    @pytest.mark.tier1
    def test_stats_consistent_under_load(self):
        """Stats remain internally consistent during concurrent use."""
        gov = _quick_governor(
            rpm_limit=600,
            tpm_limit=600_000,
            tokens_per_request=1_000,
        )

        barrier = threading.Barrier(5)

        def _worker():
            barrier.wait()
            for _ in range(4):
                gov.acquire()
                time.sleep(0.01)
                gov.release(1_000)

        threads = [
            threading.Thread(target=_worker, daemon=True)
            for _ in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        stats = gov.get_stats()
        assert stats["total_requests"] == 20
        assert stats["total_tokens"] == 20_000


# ── Constructor Validation ───────────────────────────────────────────

class TestConstructorValidation:
    """Test input validation in constructor."""

    @pytest.mark.tier1
    def test_invalid_rpm_limit_zero(self):
        """rpm_limit=0 raises ValueError (would deadlock acquire)."""
        with pytest.raises(ValueError, match="rpm_limit"):
            TokenBucketGovernor(rpm_limit=0, status_interval=0)

    @pytest.mark.tier1
    def test_invalid_rpm_limit_negative(self):
        """Negative rpm_limit raises ValueError."""
        with pytest.raises(ValueError, match="rpm_limit"):
            TokenBucketGovernor(rpm_limit=-100, status_interval=0)

    @pytest.mark.tier1
    def test_invalid_tpm_limit_zero(self):
        """tpm_limit=0 raises ValueError (would deadlock acquire)."""
        with pytest.raises(ValueError, match="tpm_limit"):
            TokenBucketGovernor(tpm_limit=0, status_interval=0)

    @pytest.mark.tier1
    def test_invalid_tpm_limit_negative(self):
        """Negative tpm_limit raises ValueError."""
        with pytest.raises(ValueError, match="tpm_limit"):
            TokenBucketGovernor(tpm_limit=-1000, status_interval=0)

    @pytest.mark.tier1
    def test_invalid_target_utilisation_zero(self):
        """target_utilisation=0 raises ValueError."""
        with pytest.raises(ValueError, match="target_utilisation"):
            TokenBucketGovernor(target_utilisation=0.0)

    @pytest.mark.tier1
    def test_invalid_target_utilisation_negative(self):
        """Negative target_utilisation raises ValueError."""
        with pytest.raises(ValueError, match="target_utilisation"):
            TokenBucketGovernor(target_utilisation=-0.5)

    @pytest.mark.tier1
    def test_invalid_target_utilisation_over_one(self):
        """target_utilisation > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="target_utilisation"):
            TokenBucketGovernor(target_utilisation=1.5)

    @pytest.mark.tier1
    def test_invalid_tokens_per_request(self):
        """tokens_per_request <= 0 raises ValueError."""
        with pytest.raises(ValueError, match="tokens_per_request"):
            TokenBucketGovernor(tokens_per_request=0)

    @pytest.mark.tier1
    def test_target_utilisation_one_is_valid(self):
        """target_utilisation=1.0 is the upper bound and valid."""
        gov = TokenBucketGovernor(
            target_utilisation=1.0,
            status_interval=0,
        )
        stats = gov.get_stats()
        assert stats["target_tpm"] == stats["tpm_limit"]

    @pytest.mark.tier1
    def test_legacy_args_accepted(self):
        """Legacy TPMGovernor args are accepted without error."""
        gov = TokenBucketGovernor(
            tokens_per_request=20_000,
            initial_concurrency=12,
            max_concurrency=60,
            status_interval=0,
        )
        # Should work fine
        gov.acquire()
        gov.release(20_000)


# ── Stats Structure ──────────────────────────────────────────────────

class TestStats:
    """Test get_stats() output structure and values."""

    @pytest.mark.tier1
    def test_stats_has_required_keys(self):
        """Stats dict contains all expected keys."""
        gov = _quick_governor()
        stats = gov.get_stats()

        required_keys = {
            "governor_type",
            "rpm_limit",
            "tpm_limit",
            "target_rpm",
            "target_tpm",
            "target_utilisation",
            "current_tpm",
            "available_request_capacity",
            "available_token_capacity",
            "cooldown_seconds",
            "tokens_per_request",
            "total_tokens",
            "total_requests",
            "total_rate_limits",
            "total_cooldown_seconds",
            "avg_latency_seconds",
            "peak_wait_seconds",
            "elapsed_seconds",
        }
        assert required_keys.issubset(stats.keys())

    @pytest.mark.tier1
    def test_stats_initial_values(self):
        """Fresh governor has sensible initial stats."""
        gov = _quick_governor(
            rpm_limit=100,
            tpm_limit=50_000,
            tokens_per_request=2_000,
        )
        stats = gov.get_stats()

        assert stats["governor_type"] == "token_bucket"
        assert stats["rpm_limit"] == 100
        assert stats["tpm_limit"] == 50_000
        assert stats["total_tokens"] == 0
        assert stats["total_requests"] == 0
        assert stats["total_rate_limits"] == 0
        assert stats["avg_latency_seconds"] is None
        assert stats["peak_wait_seconds"] == 0.0

    @pytest.mark.tier1
    def test_stats_after_requests(self):
        """Stats reflect completed requests accurately."""
        gov = _quick_governor()

        gov.acquire()
        gov.release(800, latency_seconds=1.5)
        gov.acquire()
        gov.release(1_200, latency_seconds=2.5)

        stats = gov.get_stats()
        assert stats["total_requests"] == 2
        assert stats["total_tokens"] == 2_000
        assert stats["avg_latency_seconds"] == pytest.approx(2.0, abs=0.01)

    @pytest.mark.tier1
    def test_stats_after_rate_limit(self):
        """Stats reflect 429 events."""
        gov = _quick_governor(cooldown_seconds=0.1)

        gov.acquire()
        gov.release(0, was_rate_limited=True)
        time.sleep(0.15)  # Wait out cooldown

        stats = gov.get_stats()
        assert stats["total_rate_limits"] == 1
        assert stats["total_cooldown_seconds"] == pytest.approx(
            0.1, abs=0.01
        )


# ── Replenishment Logic ─────────────────────────────────────────────

class TestReplenishment:
    """Test continuous capacity replenishment."""

    @pytest.mark.tier1
    def test_capacity_increases_over_time(self):
        """After depletion, capacity regenerates with time."""
        gov = _quick_governor(
            rpm_limit=60,        # 1/second
            tpm_limit=60_000,    # 1,000/second
            tokens_per_request=1_000,
        )

        # Deplete some capacity
        for _ in range(10):
            gov.acquire()
            gov.release(1_000)

        stats_t0 = gov.get_stats()

        # Wait 1 second for replenishment
        time.sleep(1.0)

        stats_t1 = gov.get_stats()

        # Both capacities should have increased
        assert (
            stats_t1["available_request_capacity"]
            > stats_t0["available_request_capacity"]
        )
        assert (
            stats_t1["available_token_capacity"]
            > stats_t0["available_token_capacity"]
        )

    @pytest.mark.tier1
    def test_capacity_caps_at_target(self):
        """Capacity does not exceed the target limit."""
        gov = _quick_governor(
            rpm_limit=60,
            tpm_limit=60_000,
        )

        # Wait a long time — capacity should not exceed target
        time.sleep(0.5)

        stats = gov.get_stats()
        assert stats["available_request_capacity"] <= 60
        assert stats["available_token_capacity"] <= 60_000


# ── Integration-Compatible Scenarios ─────────────────────────────────

class TestIntegrationScenarios:
    """
    Test scenarios that mirror real usage in 4_detect_mounds_batch.py.
    """

    @pytest.mark.tier1
    def test_image_track_pattern(self):
        """Simulate image-track usage: 20K tokens, 60 tiles."""
        gov = TokenBucketGovernor(
            rpm_limit=2_000,
            tpm_limit=1_000_000,
            target_utilisation=0.72,
            tokens_per_request=20_000,
            cooldown_seconds=15.0,
            status_interval=0,
        )

        # Process 5 tiles sequentially (sanity check)
        for i in range(5):
            gov.acquire()
            time.sleep(0.01)  # Simulate API latency
            gov.release(
                18_000 + i * 500,  # Varying actual tokens
                latency_seconds=0.01,
            )

        stats = gov.get_stats()
        assert stats["total_requests"] == 5
        assert stats["total_tokens"] > 0
        assert stats["avg_latency_seconds"] is not None
        assert stats["total_rate_limits"] == 0

    @pytest.mark.tier1
    def test_text_track_pattern(self):
        """Simulate text-only track: 1.5K tokens, 60 tiles."""
        gov = TokenBucketGovernor(
            rpm_limit=2_000,
            tpm_limit=1_000_000,
            target_utilisation=0.72,
            tokens_per_request=1_500,
            cooldown_seconds=15.0,
            status_interval=0,
        )

        # Process 10 tiles quickly
        for _ in range(10):
            gov.acquire()
            gov.release(1_200, latency_seconds=0.005)

        stats = gov.get_stats()
        assert stats["total_requests"] == 10
        assert stats["total_tokens"] == 12_000

    @pytest.mark.tier1
    def test_mixed_success_and_429_pattern(self):
        """Simulate realistic pattern: successes then a 429 burst."""
        gov = _quick_governor(
            rpm_limit=600,
            tpm_limit=600_000,
            tokens_per_request=1_000,
            cooldown_seconds=0.3,
        )

        # 5 successful requests
        for _ in range(5):
            gov.acquire()
            gov.release(1_000, latency_seconds=0.01)

        # 1 rate-limited request
        gov.acquire()
        gov.release(0, was_rate_limited=True)

        # Wait out cooldown
        time.sleep(0.35)

        # Resume with successful requests
        for _ in range(3):
            gov.acquire()
            gov.release(1_000, latency_seconds=0.01)

        stats = gov.get_stats()
        assert stats["total_requests"] == 9
        assert stats["total_rate_limits"] == 1
        assert stats["total_tokens"] == 8_000  # 8 × 1000

    @pytest.mark.tier1
    def test_governor_release_before_backoff_pattern(self):
        """
        Verify the release-before-backoff pattern works.

        In 4_detect_mounds_batch.py, release() is called in the
        finally block BEFORE the backoff sleep. This means the
        governor sees the 429 signal immediately, not after a
        30–300s delay. Test that this pattern works correctly.
        """
        gov = _quick_governor(
            cooldown_seconds=0.2,
            rpm_limit=600,
            tpm_limit=600_000,
        )

        # Simulate: acquire, API returns 429, release immediately,
        # then backoff sleep (simulated by sleep below)
        gov.acquire()
        gov.release(0, was_rate_limited=True)
        # In real code: time.sleep(backoff) happens here

        # Governor should now be in cooldown
        stats = gov.get_stats()
        assert stats["total_rate_limits"] == 1

        # Wait out cooldown + tiny margin
        time.sleep(0.25)

        # Should be able to acquire again
        gov.acquire()
        gov.release(1_000)
