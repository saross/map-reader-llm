"""
Tier-1 tests for ``scripts/check_union_provenance.py``.

The script settles Finding 4 of ``reports/name-keyed-cache-audit-2026-09-12.md``
retrospectively: for a union committed before the pass-provenance fix, it
re-derives the union from its pool and decides whether the union still matches.

The contract exercised here, on a synthetic pool rather than any committed
artefact:

* a union rebuilt from the whole pool classifies **REPRODUCES**;
* a first-N sub-pool union under a larger pool classifies
  **SUBPOOL-CONSISTENT**, naming the passes it does not reflect;
* a union built before the pool grew classifies **STALE** — as does one built
  before a pass was rewritten in place under the same name (the E57 / E70
  failure mode), where the pass count alone shows nothing;
* a pool whose passes were never materialised classifies **UNRESOLVED**;
* the coordinate comparison is bidirectional, so a union that is a strict
  subset of the re-derivation is not called identical.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.check_union_provenance import (  # noqa: E402
    UNRESOLVABLE,
    check_union,
    compare_feature_sets,
    enumerate_registered_unions,
    resolve_union_spec,
)
from scripts.merge_passes import threshold_sweep  # noqa: E402

pytestmark = pytest.mark.tier1


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _feature(easting: float, northing: float) -> dict:
    """A minimal detection feature in the pass files' own CRS.

    Pass detections are written in EPSG:32635 (Universal Transverse Mercator,
    zone 35N) metres — see any ``outputs/**/run_*/detections*.geojson`` — and
    ``merge_passes`` clusters them in that CRS before reprojecting the union's
    centroids to WGS84. The fixture therefore uses metres, not degrees.
    """
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [easting, northing]},
        "properties": {"subtype": "mound", "source_tile": "tile_001"},
    }


def _wgs84_feature(lon: float, lat: float) -> dict:
    """A union-style point feature in EPSG:4326, as the merger writes them."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {"subtype": "mound"},
    }


def _write_pass(pool: Path, run: int, features: list[dict]) -> Path:
    """Write (or rewrite) one pass directory's detections GeoJSON."""
    run_dir = pool / f"run_{run}"
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / f"detections_test_run{run:02d}.geojson"
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )
    return path


#: Four points 500 m apart in EPSG:32635 — well beyond the 20 m clustering
#: tolerance — so each cluster's vote count is exactly the number of passes
#: that reported that point.
_P = [
    (404300.0, 4702900.0),
    (404800.0, 4702900.0),
    (405300.0, 4702900.0),
    (405800.0, 4702900.0),
]


def _pool_of(pool: Path, per_run: dict[int, list[int]]) -> None:
    """Build a pool where ``per_run[run]`` lists the point indices it saw."""
    for run, idxs in per_run.items():
        _write_pass(pool, run, [_feature(*_P[i]) for i in idxs])


# ---------------------------------------------------------------------------
# REPRODUCES
# ---------------------------------------------------------------------------


def test_whole_pool_union_reproduces(tmp_path: Path) -> None:
    """A union rebuilt from the pool it names reproduces exactly."""
    pool = tmp_path / "cell"
    _pool_of(pool, {1: [0, 1], 2: [0, 1], 3: [0, 2]})
    threshold_sweep(pool, pool / "consensus")

    result = check_union(
        pool / "consensus" / "consensus_t2.geojson",
        tmp_path / "scratch",
        repo_root=tmp_path,
    )
    assert result.classification == "REPRODUCES"
    assert result.committed_features == result.rederived_features == 2
    assert result.unmatched_committed == 0
    assert result.unmatched_rederived == 0
    assert result.passes_not_reflected == []


# ---------------------------------------------------------------------------
# SUBPOOL-CONSISTENT
# ---------------------------------------------------------------------------


def test_declared_first_n_subpool_is_consistent_not_stale(tmp_path: Path) -> None:
    """A ``consensus-n2`` union under a four-pass pool is a declared sub-pool.

    Its pass count disagrees with the pool's — the ambiguity the audit could
    not resolve — but it reproduces from passes 1-2, so it is sound.
    """
    pool = tmp_path / "cell"
    _pool_of(pool, {1: [0, 1], 2: [0, 1], 3: [2, 3], 4: [2, 3]})
    threshold_sweep(pool, pool / "consensus-n2", pass_filter=[1, 2])

    result = check_union(
        pool / "consensus-n2" / "consensus_t2.geojson",
        tmp_path / "scratch",
        repo_root=tmp_path,
    )
    assert result.classification == "SUBPOOL-CONSISTENT"
    assert result.declared_subpool_n == 2
    assert result.union_passes_used == ["run_1", "run_2"]
    assert result.passes_not_reflected == ["run_3", "run_4"]


def test_subpool_spec_expands_the_first_n_rule(tmp_path: Path) -> None:
    """``consensus-n10`` means ``--passes 1..10``, not "any ten passes"."""
    spec = resolve_union_spec(
        Path("outputs/x/cell/consensus-n10/consensus_t7.geojson"),
        repo_root=tmp_path,
    )
    assert spec.declared_subpool_n == 10
    assert spec.pass_filter == list(range(1, 11))
    assert spec.threshold == 7


# ---------------------------------------------------------------------------
# STALE
# ---------------------------------------------------------------------------


def test_union_built_before_the_pool_grew_is_stale(tmp_path: Path) -> None:
    """Passes added after the union was written make it stale.

    The union directory is the undeclared ``consensus/``, so nothing on disk
    says "first two passes only" — exactly the E57 top-up scenario.
    """
    pool = tmp_path / "cell"
    _pool_of(pool, {1: [0, 1], 2: [0, 1]})
    threshold_sweep(pool, pool / "consensus")
    # The pool grows under the union's feet.
    _pool_of(pool, {3: [0, 2], 4: [0, 2]})

    result = check_union(
        pool / "consensus" / "consensus_t2.geojson",
        tmp_path / "scratch",
        repo_root=tmp_path,
    )
    assert result.classification == "STALE"
    assert result.pool_passes == ["run_1", "run_2", "run_3", "run_4"]
    assert result.union_passes_used == ["run_1", "run_2", "run_3", "run_4"]
    assert result.rederived_features != result.committed_features
    # The verdict names what the union does reflect, not merely that it is wrong.
    assert result.reflects_subset == ["run_1", "run_2"]
    assert result.passes_not_reflected == ["run_3", "run_4"]
    assert "FIRST 2 of 4" in result.detail


def test_union_built_before_a_pass_was_rewritten_is_stale(tmp_path: Path) -> None:
    """A pass rewritten in place makes the union stale at an unchanged count.

    This is the E70 patch campaign: the pass file keeps its name and the pool
    keeps its size, so ``total_passes`` is no help at all — only the content
    comparison detects it.
    """
    pool = tmp_path / "cell"
    _pool_of(pool, {1: [0, 1], 2: [0, 1], 3: [0, 1]})
    threshold_sweep(pool, pool / "consensus")
    committed = json.loads(
        (pool / "consensus" / "consensus_t3.geojson").read_text(encoding="utf-8"),
    )
    assert len(committed["features"]) == 2

    # A recovery adds a tile's detections to run_3 under the same filename.
    _write_pass(pool, 3, [_feature(*_P[0]), _feature(*_P[1]), _feature(*_P[2])])
    _write_pass(pool, 1, [_feature(*_P[0]), _feature(*_P[1]), _feature(*_P[2])])
    _write_pass(pool, 2, [_feature(*_P[0]), _feature(*_P[1]), _feature(*_P[2])])

    result = check_union(
        pool / "consensus" / "consensus_t3.geojson",
        tmp_path / "scratch",
        repo_root=tmp_path,
    )
    assert result.classification == "STALE"
    assert result.vs_total_passes == 3
    assert len(result.pool_passes) == 3  # the count is unchanged — content is not
    assert result.rederived_features == 3
    assert result.committed_features == 2


# ---------------------------------------------------------------------------
# UNRESOLVED
# ---------------------------------------------------------------------------


def test_pool_without_pass_directories_is_unresolved(tmp_path: Path) -> None:
    """A union whose pool was never materialised cannot be re-derived."""
    union_dir = tmp_path / "outputs" / "run" / "consensus"
    union_dir.mkdir(parents=True)
    (union_dir / "consensus_t3.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": []}), encoding="utf-8",
    )

    result = check_union(
        union_dir / "consensus_t3.geojson", tmp_path / "scratch", repo_root=tmp_path,
    )
    assert result.classification == "UNRESOLVED"
    assert "run_*/pass_*" in result.detail


def test_documented_unresolvable_dirs_are_declared_not_guessed() -> None:
    """The unresolvable table carries a re-verifiable anchor for each entry."""
    assert UNRESOLVABLE, "the table should not be silently emptied"
    for union_dir, reason in UNRESOLVABLE.items():
        assert union_dir.startswith("outputs/")
        assert "run-conditions.json" in reason or "." in reason


# ---------------------------------------------------------------------------
# The comparison itself
# ---------------------------------------------------------------------------


def test_comparison_is_bidirectional(tmp_path: Path) -> None:
    """A strict subset is not identical, in either direction."""
    a = [_wgs84_feature(25.00, 42.0), _wgs84_feature(25.01, 42.0)]
    b = a + [_wgs84_feature(25.02, 42.0)]

    subset = compare_feature_sets(a, b)
    assert subset["identical"] is False
    assert subset["unmatched_committed"] == 0
    assert subset["unmatched_rederived"] == 1

    superset = compare_feature_sets(b, a)
    assert superset["identical"] is False
    assert superset["unmatched_committed"] == 1
    assert superset["unmatched_rederived"] == 0

    assert compare_feature_sets(a, list(a))["identical"] is True


def test_comparison_tolerance_is_metres_not_degrees() -> None:
    """A shift of ~8 m fails at the 1 m default and passes at 20 m.

    ``compare_feature_sets`` reads *union* features, which are WGS84 points,
    and projects them to metres before measuring — so its inputs are degrees,
    unlike the pass-file fixtures above.
    """
    a = [_wgs84_feature(25.0, 42.0)]
    b = [_wgs84_feature(25.0001, 42.0)]  # ~8.3 m east at this latitude
    assert compare_feature_sets(a, b, tolerance_m=1.0)["identical"] is False
    loose = compare_feature_sets(a, b, tolerance_m=20.0)
    assert loose["identical"] is True
    assert 1.0 < (loose["max_match_distance_m"] or 0) < 20.0


# ---------------------------------------------------------------------------
# Enumeration
# ---------------------------------------------------------------------------


def test_enumeration_excludes_non_union_detections(tmp_path: Path) -> None:
    """Single-pass, verifier-accepted, and WBF outputs are not unions."""
    union_dir = tmp_path / "outputs" / "cell" / "consensus"
    union_dir.mkdir(parents=True)
    for name in (
        "consensus_t4.geojson", "detections_384_run01.geojson",
        "accepted_t0.2.geojson", "wbf_vote4.geojson",
    ):
        (union_dir / name).write_text("{}", encoding="utf-8")

    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"conditions": [{
        "condition_id": "r::c",
        "provenance": {"source_files": [
            f"outputs/cell/consensus/{name}" for name in (
                "consensus_t4.geojson", "detections_384_run01.geojson",
                "accepted_t0.2.geojson", "wbf_vote4.geojson",
            )
        ]},
    }]}), encoding="utf-8")

    found = enumerate_registered_unions(tmp_path, manifest)
    assert list(found) == ["outputs/cell/consensus/consensus_t4.geojson"]
    assert found["outputs/cell/consensus/consensus_t4.geojson"] == ["r::c"]


def test_enumeration_follows_the_evaluation_hop(tmp_path: Path) -> None:
    """A condition that names only its evaluation still resolves to its union."""
    union_dir = tmp_path / "outputs" / "cell" / "consensus"
    union_dir.mkdir(parents=True)
    (union_dir / "consensus_t4.geojson").write_text("{}", encoding="utf-8")
    eval_path = tmp_path / "results" / "x" / "evaluation.json"
    eval_path.parent.mkdir(parents=True)
    eval_path.write_text(json.dumps({"_metadata": {"input_files": {
        "detections": ["outputs/cell/consensus/consensus_t4.geojson"],
    }}}), encoding="utf-8")

    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"conditions": [{
        "condition_id": "r::c",
        "provenance": {"source_files": ["results/x/evaluation.json"]},
    }]}), encoding="utf-8")

    found = enumerate_registered_unions(tmp_path, manifest)
    assert list(found) == ["outputs/cell/consensus/consensus_t4.geojson"]
