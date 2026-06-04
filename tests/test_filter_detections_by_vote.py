"""Tier-1 tests for ``scripts/filter_detections_by_vote.py``.

The filter materialises a vote-thresholded candidate set from a raw consensus /
WBF candidate GeoJSON — e.g. the ``vote_count >= 4`` WBF condition that mirrors
the greedy ``consensus_t4`` operating point for the H8/H12 library studies. These
tests assert the filter is purely structural: it keeps exactly the features at or
above the threshold, preserves every feature property and every top-level GeoJSON
key untouched, reports the input vote distribution accurately, and refuses to
guess a default when a feature lacks a ``vote_count`` (which would silently drop
or keep candidates under a fabricated vote).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.filter_detections_by_vote import (  # noqa: E402
    filter_features_by_vote,
    main,
)


def _feature(candidate_id: int, vote_count: int, **extra: object) -> dict:
    """Build a minimal GeoJSON point feature carrying a vote_count property."""
    props = {"candidate_id": candidate_id, "vote_count": vote_count, **extra}
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
    }


def _collection(features: list[dict], **top: object) -> dict:
    """Wrap features in a FeatureCollection with optional extra top-level keys."""
    return {"type": "FeatureCollection", "features": features, **top}


@pytest.mark.tier1
def test_keeps_only_at_or_above_threshold() -> None:
    """Features with vote_count >= min_votes are kept; lower ones dropped."""
    coll = _collection([_feature(i, vc) for i, vc in enumerate([1, 2, 3, 4, 5])])
    out, dist = filter_features_by_vote(coll, min_votes=4)
    kept_votes = sorted(f["properties"]["vote_count"] for f in out["features"])
    assert kept_votes == [4, 5]
    assert dist == {1: 1, 2: 1, 3: 1, 4: 1, 5: 1}


@pytest.mark.tier1
def test_preserves_all_feature_properties() -> None:
    """Every property on a surviving feature is carried through verbatim."""
    coll = _collection(
        [_feature(0, 5, subtype="benchmark_mound", confidence=1.0, cluster_size=22)]
    )
    out, _ = filter_features_by_vote(coll, min_votes=4)
    props = out["features"][0]["properties"]
    assert props == {
        "candidate_id": 0,
        "vote_count": 5,
        "subtype": "benchmark_mound",
        "confidence": 1.0,
        "cluster_size": 22,
    }


@pytest.mark.tier1
def test_preserves_top_level_keys() -> None:
    """CRS and any other top-level GeoJSON keys are preserved unchanged."""
    crs = {"type": "name", "properties": {"name": "EPSG:32635"}}
    coll = _collection([_feature(0, 5)], name="wbf_candidates", crs=crs)
    out, _ = filter_features_by_vote(coll, min_votes=4)
    assert out["type"] == "FeatureCollection"
    assert out["name"] == "wbf_candidates"
    assert out["crs"] == crs


@pytest.mark.tier1
def test_threshold_above_max_yields_empty() -> None:
    """A threshold above every vote count drops all features (no crash)."""
    coll = _collection([_feature(i, vc) for i, vc in enumerate([1, 2, 3])])
    out, dist = filter_features_by_vote(coll, min_votes=4)
    assert out["features"] == []
    assert sum(dist.values()) == 3


@pytest.mark.tier1
def test_missing_vote_count_raises() -> None:
    """A feature with no vote_count must raise, never assume a default."""
    bad = {"type": "Feature", "properties": {"candidate_id": 7}, "geometry": None}
    coll = _collection([bad])
    with pytest.raises(KeyError):
        filter_features_by_vote(coll, min_votes=4)


@pytest.mark.tier1
def test_does_not_mutate_input() -> None:
    """Filtering returns a new collection; the input feature list is untouched."""
    feats = [_feature(i, vc) for i, vc in enumerate([1, 5])]
    coll = _collection(feats)
    filter_features_by_vote(coll, min_votes=4)
    assert len(coll["features"]) == 2  # original list unchanged


@pytest.mark.tier1
def test_cli_round_trip(tmp_path: Path) -> None:
    """The CLI reads, filters, and writes a valid filtered GeoJSON to disk."""
    src = tmp_path / "in.geojson"
    dst = tmp_path / "out.geojson"
    src.write_text(json.dumps(_collection(
        [_feature(i, vc) for i, vc in enumerate([1, 1, 4, 5, 5])])))
    rc = main(["--input", str(src), "--output", str(dst), "--min-votes", "4"])
    assert rc == 0
    written = json.loads(dst.read_text())
    assert len(written["features"]) == 3  # the 4, 5, 5
    assert all(f["properties"]["vote_count"] >= 4 for f in written["features"])


@pytest.mark.tier1
def test_cli_missing_input_returns_error(tmp_path: Path) -> None:
    """A non-existent input path exits non-zero rather than throwing."""
    rc = main([
        "--input", str(tmp_path / "nope.geojson"),
        "--output", str(tmp_path / "out.geojson"),
        "--min-votes", "4",
    ])
    assert rc == 1
