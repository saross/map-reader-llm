"""Tier-1 tests for the canonical detection-path resolver.

Covers the behaviour that defect D6 turned on: that both filename conventions
are resolved, that a mixed pool yields their union rather than whichever
convention the glob happened to match, and — the substantive part — that a
pass-count mismatch raises rather than passing silently.

Directory structures are built with ``tmp_path`` rather than committed
fixtures, matching the house pattern for on-disk state; ``tests/fixtures/`` is
flat and holds data files only.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib_detection_paths import (  # noqa: E402
    PASS_GLOBS,
    AmbiguousPassError,
    PassCountMismatch,
    find_pass_geojsons,
    resolve_pool_passes,
    run_sort_key,
)

CONV_A = "detections_brief-text_run{n:02d}.geojson"
CONV_B = "detections-detect_brief-text-3-flash-2026-08-{n:02d}.geojson"


def _make_pool(root: Path, layout: dict[str, list[str]]) -> Path:
    """Build a pool directory from a {run_dir: [filenames]} description.

    Args:
        root: Parent directory (usually ``tmp_path``).
        layout: Mapping of run-directory name to the files it should contain.

    Returns:
        The created pool directory.
    """
    pool = root / "pool"
    for run_name, filenames in layout.items():
        run_dir = pool / run_name
        run_dir.mkdir(parents=True)
        for filename in filenames:
            (run_dir / filename).write_text('{"type": "FeatureCollection"}')
    return pool


@pytest.mark.tier1
def test_finds_convention_a(tmp_path):
    """A batch-written pass directory resolves."""
    pool = _make_pool(tmp_path, {"run_1": [CONV_A.format(n=1)]})
    assert [p.name for p in find_pass_geojsons(pool / "run_1")] == [CONV_A.format(n=1)]


@pytest.mark.tier1
def test_finds_convention_b(tmp_path):
    """A realtime-written pass directory resolves — the case an A-only glob missed."""
    pool = _make_pool(tmp_path, {"run_1": [CONV_B.format(n=17)]})
    assert [p.name for p in find_pass_geojsons(pool / "run_1")] == [CONV_B.format(n=17)]


@pytest.mark.tier1
def test_mixed_pool_resolves_to_the_union(tmp_path):
    """The defect case: a pool straddling the batch/realtime switch.

    An A-only glob returns 1 of 3 here; the resolver must return all three.
    """
    pool = _make_pool(tmp_path, {
        "run_1": [CONV_A.format(n=1)],
        "run_2": [CONV_B.format(n=17)],
        "run_3": [CONV_B.format(n=18)],
    })
    assert len(list(pool.glob("run_*/detections_*.geojson"))) == 1, "precondition"
    assert len(resolve_pool_passes(pool)) == 3


@pytest.mark.tier1
def test_pass_count_guard_raises_on_undercount(tmp_path):
    """The guard is the point: a wrong count must be loud, not silent."""
    pool = _make_pool(tmp_path, {"run_1": [CONV_A.format(n=1)]})
    with pytest.raises(PassCountMismatch) as excinfo:
        resolve_pool_passes(pool, expected_passes=3)
    message = str(excinfo.value)
    assert "expected 3" in message
    assert str(pool) in message, "message must name the directory"


@pytest.mark.tier1
def test_pass_count_guard_silent_when_satisfied(tmp_path):
    """A matching count returns normally."""
    pool = _make_pool(tmp_path, {
        "run_1": [CONV_A.format(n=1)], "run_2": [CONV_B.format(n=17)],
    })
    assert len(resolve_pool_passes(pool, expected_passes=2)) == 2


@pytest.mark.tier1
def test_non_numeric_run_directory_is_skipped(tmp_path):
    """``run_1_recovery`` supplements a pass; it is not itself a pass."""
    pool = _make_pool(tmp_path, {
        "run_1": [CONV_A.format(n=1)],
        "run_1_recovery": [CONV_B.format(n=18)],
    })
    resolved = resolve_pool_passes(pool)
    assert len(resolved) == 1
    assert resolved[0].parent.name == "run_1"


@pytest.mark.tier1
def test_aggregation_artefacts_and_sidecars_excluded(tmp_path):
    """Consensus/verified outputs and .meta/.tiles sidecars are not passes."""
    pool = _make_pool(tmp_path, {"run_1": [
        CONV_A.format(n=1),
        "consensus_t3.geojson",
        "verified_detections.geojson",
        "accepted_run1.geojson",
        "detections_brief-text_run01.meta.json",
        "detections_brief-text_run01.tiles.json",
    ]})
    assert [p.name for p in find_pass_geojsons(pool / "run_1")] == [CONV_A.format(n=1)]


@pytest.mark.tier1
def test_ambiguous_run_directory_refuses_to_guess(tmp_path):
    """Two candidate files in one run must raise, not be silently narrowed.

    Mirrors ``outputs/flash35-pv-2x2/proposer/run_3``, where a complete
    487-tile re-run supersedes an incomplete 486-tile attempt.
    """
    pool = _make_pool(tmp_path, {"run_1": [CONV_B.format(n=10), CONV_B.format(n=11)]})
    with pytest.raises(AmbiguousPassError):
        resolve_pool_passes(pool)
    assert len(resolve_pool_passes(pool, allow_multiple=True)) == 2


@pytest.mark.tier1
def test_missing_and_empty_directories_return_empty(tmp_path):
    """Probing an absent or empty pool is routine, not an error."""
    assert find_pass_geojsons(tmp_path / "does-not-exist") == []
    empty = _make_pool(tmp_path, {"run_1": []})
    assert resolve_pool_passes(empty) == []


@pytest.mark.tier1
def test_runs_are_ordered_numerically(tmp_path):
    """``run_2`` must precede ``run_10`` — lexical order would invert them."""
    pool = _make_pool(tmp_path, {
        f"run_{n}": [CONV_A.format(n=n)] for n in (1, 2, 10)
    })
    assert [p.parent.name for p in resolve_pool_passes(pool)] == ["run_1", "run_2", "run_10"]
    assert run_sort_key(Path("run_2")) < run_sort_key(Path("run_10"))


@pytest.mark.tier1
def test_no_bare_convention_a_glob_outside_this_module():
    """Repo guard — the fix must not erode.

    The codebase independently re-solved this resolution problem five times
    before it was centralised. A new script reaching for a bare
    ``detections_*`` glob reintroduces the defect, so the suite fails on it.
    """
    scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
    allowed = {"lib_detection_paths.py"}
    offenders = []
    for path in sorted(scripts_dir.glob("*.py")):
        if path.name in allowed:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            if "detections_*" in line and "lib_detection_paths" not in line:
                offenders.append(f"{path.name}:{lineno}")
    assert not offenders, (
        "bare convention-A glob outside the resolver (defect D6 vector); "
        "use scripts.lib_detection_paths instead:\n  " + "\n  ".join(offenders)
    )


@pytest.mark.tier1
def test_pass_globs_covers_both_conventions():
    """Both conventions must be present — the tuple is the contract."""
    assert len(PASS_GLOBS) == 2
    assert any("detections_" in g for g in PASS_GLOBS)
    assert any("detections-" in g for g in PASS_GLOBS)
