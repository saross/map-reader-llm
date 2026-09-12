"""
Pass-provenance tests for the consensus union builders.

Guards the Finding 4 fix of ``reports/name-keyed-cache-audit-2026-09-12.md``:
a consensus union recorded only ``total_passes``, and ``build_all_consensus.py``
skipped a condition on PRESENCE alone. A pool whose passes had been rewritten in
place (E57 and E70 both did that) was therefore reported "skipped — existing
consensus: complete", and the stale union went on serving as the candidate
universe for extraction, verification, and every sweep downstream. The audit's
own attempted demonstration was inconclusive precisely because ``total_passes``
cannot distinguish a declared sub-pool from a stale union.

``merge_passes.threshold_sweep`` now records each contributing pass file's
repository-relative path and content hash, and
``build_all_consensus.check_existing_consensus`` compares that record against
the pool. The three cases below are the contract:

* **match** — provenance verified, the condition still skips;
* **mismatch** — the union is reported stale and refused, naming the change;
* **legacy** — a summary with no pass list is "unknown provenance" with a
  warning, never a match.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_all_consensus import (  # noqa: E402
    PROVENANCE_STALE,
    PROVENANCE_UNKNOWN,
    PROVENANCE_VERIFIED,
    check_existing_consensus,
    compare_pass_provenance,
    process_single_condition,
)
from scripts.lib_content_anchor import git_blob_hash  # noqa: E402
from scripts.merge_passes import (  # noqa: E402
    PASS_PROVENANCE_SCHEMA,
    build_pass_provenance,
    resolve_pass_files,
    threshold_sweep,
)

pytestmark = pytest.mark.tier1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _feature(lon: float, lat: float) -> dict:
    """A minimal GeoJSON point feature in EPSG:4326."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {"subtype": "mound", "source_tile": "tile_001"},
    }


def _write_pass(pool: Path, run: int, features: list[dict]) -> Path:
    """Write one pass directory with a single detections GeoJSON."""
    run_dir = pool / f"run_{run}"
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / f"detections_test_run{run:02d}.geojson"
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def built_pool(tmp_path: Path) -> tuple[Path, Path]:
    """A three-pass pool with a swept consensus union built from it.

    Returns ``(pool_dir, consensus_dir)``.
    """
    pool = tmp_path / "condition"
    for run in (1, 2, 3):
        _write_pass(pool, run, [_feature(25.0, 42.0), _feature(25.001, 42.001)])
    consensus = pool / "consensus"
    threshold_sweep(pool, consensus)
    return pool, consensus


# ---------------------------------------------------------------------------
# merge_passes writes the pass list
# ---------------------------------------------------------------------------


def test_voting_summary_records_every_pass_file(built_pool) -> None:
    """The union's summary names each pass file and anchors it to its bytes."""
    pool, consensus = built_pool
    summary = json.loads(
        (consensus / "voting_summary.json").read_text(encoding="utf-8"),
    )

    assert summary["pass_provenance_schema"] == PASS_PROVENANCE_SCHEMA
    assert summary["total_passes"] == 3
    assert summary["pass_ids"] == ["run_1", "run_2", "run_3"]

    provenance = summary["pass_provenance"]
    assert len(provenance) == 3
    for entry in provenance:
        assert entry["pass_id"].startswith("run_")
        recorded_path = Path(entry["path"])
        on_disk = (
            recorded_path if recorded_path.is_absolute()
            else PROJECT_ROOT / recorded_path
        )
        assert entry["git_blob_hash"] == git_blob_hash(on_disk)
    # Legacy fields survive untouched.
    assert set(summary["thresholds"]) == {"1", "2", "3"}


def test_pass_filter_records_only_the_subpool(tmp_path: Path) -> None:
    """A declared sub-pool records exactly its own passes — the audit's
    negative demonstration becomes decisive with a pass list."""
    pool = tmp_path / "condition"
    for run in (1, 2, 3, 4, 5):
        _write_pass(pool, run, [_feature(25.0, 42.0)])
    consensus = pool / "consensus-n3"
    threshold_sweep(pool, consensus, pass_filter=[1, 2, 3])

    summary = json.loads(
        (consensus / "voting_summary.json").read_text(encoding="utf-8"),
    )
    assert summary["total_passes"] == 3
    assert {e["pass_id"] for e in summary["pass_provenance"]} == {
        "run_1", "run_2", "run_3",
    }


def test_build_pass_provenance_is_sorted_and_content_keyed(tmp_path: Path) -> None:
    """Provenance is stable in order and changes when a pass's bytes change."""
    pool = tmp_path / "condition"
    _write_pass(pool, 2, [_feature(25.0, 42.0)])
    _write_pass(pool, 1, [_feature(25.0, 42.0)])

    first = build_pass_provenance(resolve_pass_files(pool))
    assert [e["pass_id"] for e in first] == ["run_1", "run_2"]

    _write_pass(pool, 1, [_feature(25.0, 42.0), _feature(26.0, 43.0)])
    second = build_pass_provenance(resolve_pass_files(pool))
    assert second[0]["git_blob_hash"] != first[0]["git_blob_hash"]
    assert second[1]["git_blob_hash"] == first[1]["git_blob_hash"]


# ---------------------------------------------------------------------------
# check_existing_consensus compares it
# ---------------------------------------------------------------------------


def test_match_reports_verified_and_still_exists(built_pool) -> None:
    """An unchanged pool verifies, and the condition still reports as existing."""
    pool, consensus = built_pool
    verdict, detail = compare_pass_provenance(consensus, pool)
    assert verdict == PROVENANCE_VERIFIED
    assert "3 pass file(s) unchanged" in detail

    exists, description = check_existing_consensus(consensus, pool)
    assert exists is True
    assert description.startswith("complete:")
    assert "verified" in description


def test_rewritten_pass_is_stale_and_named(built_pool) -> None:
    """A pass rewritten in place — the E57 / E70 signature — reports stale."""
    pool, consensus = built_pool
    _write_pass(pool, 2, [_feature(25.0, 42.0), _feature(27.0, 43.0)])

    verdict, detail = compare_pass_provenance(consensus, pool)
    assert verdict == PROVENANCE_STALE
    assert "rewritten" in detail
    assert "run_2" in detail

    exists, description = check_existing_consensus(consensus, pool)
    assert exists is True
    assert description.startswith("stale: ")


def test_added_pass_is_stale_and_named(built_pool) -> None:
    """A top-up pass the union does not record reports stale."""
    pool, consensus = built_pool
    _write_pass(pool, 4, [_feature(25.0, 42.0)])

    verdict, detail = compare_pass_provenance(consensus, pool)
    assert verdict == PROVENANCE_STALE
    assert "does not record" in detail
    assert "run_4" in detail


def test_removed_pass_is_stale_and_named(built_pool) -> None:
    """A recorded pass file that has vanished reports stale."""
    pool, consensus = built_pool
    target = next((pool / "run_3").glob("*.geojson"))
    target.unlink()

    verdict, detail = compare_pass_provenance(consensus, pool)
    assert verdict == PROVENANCE_STALE
    assert "no longer present" in detail


def test_legacy_summary_is_unknown_provenance_never_a_match(
    built_pool, caplog,
) -> None:
    """A pre-fix summary (``total_passes`` + ``thresholds`` only) is UNKNOWN."""
    pool, consensus = built_pool
    (consensus / "voting_summary.json").write_text(
        json.dumps({"total_passes": 3, "thresholds": {"1": 2, "2": 2, "3": 2}}),
        encoding="utf-8",
    )

    verdict, detail = compare_pass_provenance(consensus, pool)
    assert verdict == PROVENANCE_UNKNOWN
    assert "no pass_provenance" in detail

    with caplog.at_level("WARNING"):
        exists, description = check_existing_consensus(consensus, pool)
    assert exists is True
    assert "provenance UNKNOWN" in description
    assert "UNKNOWN" in caplog.text


def test_unreadable_summary_is_unknown_provenance(built_pool) -> None:
    """A corrupt summary is unknown provenance, not a crash."""
    pool, consensus = built_pool
    (consensus / "voting_summary.json").write_text("{not json", encoding="utf-8")
    verdict, _detail = compare_pass_provenance(consensus, pool)
    assert verdict == PROVENANCE_UNKNOWN


def test_legacy_call_without_pool_dir_is_unchanged(built_pool) -> None:
    """Omitting *pool_dir* preserves the pre-fix presence-only behaviour."""
    _pool, consensus = built_pool
    exists, description = check_existing_consensus(consensus)
    assert exists is True
    assert description == "complete: 3 threshold files + voting_summary.json"


def test_partial_build_still_reported_as_partial(built_pool) -> None:
    """A missing summary is still "partial" — behaviour preserved."""
    pool, consensus = built_pool
    (consensus / "voting_summary.json").unlink()
    exists, description = check_existing_consensus(consensus, pool)
    assert exists is True
    assert description.startswith("partial:")


# ---------------------------------------------------------------------------
# The driver refuses rather than silently skipping
# ---------------------------------------------------------------------------


def _condition(pool: Path) -> dict:
    """A condition dict whose path is *pool*, relative to the repo root."""
    return {"id": "test-condition", "path": str(pool), "K": 3}


def test_process_single_condition_skips_a_verified_union(
    built_pool, monkeypatch,
) -> None:
    """An unchanged pool still skips — no behaviour change for unchanged inputs."""
    pool, _consensus = built_pool
    monkeypatch.setattr("scripts.build_all_consensus.PROJECT_ROOT", Path("/"))
    result = process_single_condition(_condition(pool), output_subdir="consensus")
    assert result["status"] == "skipped"
    assert "verified" in result["message"]


def test_process_single_condition_refuses_a_stale_union(
    built_pool, monkeypatch,
) -> None:
    """A rewritten pool is refused with an actionable message, not skipped."""
    pool, _consensus = built_pool
    _write_pass(pool, 2, [_feature(25.0, 42.0), _feature(27.0, 43.0)])
    monkeypatch.setattr("scripts.build_all_consensus.PROJECT_ROOT", Path("/"))

    result = process_single_condition(_condition(pool), output_subdir="consensus")
    assert result["status"] == "stale"
    assert "rewritten" in result["message"]
    assert "--force" in result["message"]
