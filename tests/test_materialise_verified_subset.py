"""Tier-1 deterministic unit tests for ``scripts/materialise_verified_subset``.

Exercises the per-feature ``verified``-flag filter (Decision 1A): the
accepted subset must contain only genuine ``verified is True`` features,
carry an explicit EPSG:4326 ``crs`` member, tolerate an empty accepted
set, and refuse UTM-metre coordinates (the Session 94 CRS-misread guard).
Pure JSON I/O on synthetic fixtures — no geopandas, no API.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.materialise_verified_subset import (
    WGS84_URN,
    _first_coord,
    _looks_like_lonlat,
    filter_verified,
)


# =========================================================================
# Helpers
# =========================================================================


def _feature(lon: float, lat: float, **props: object) -> dict:
    """Build a minimal Point feature with the given properties."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": props,
    }


def _write_fc(path: Path, features: list[dict]) -> Path:
    """Write a crs-less FeatureCollection (the input shape) to ``path``."""
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )
    return path


def _polygon_feature(lon: float, lat: float, **props: object) -> dict:
    """Build a tiny square Polygon feature (nested coordinate arrays)."""
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [lon, lat], [lon + 0.001, lat],
                [lon + 0.001, lat + 0.001], [lon, lat],
            ]],
        },
        "properties": props,
    }


# =========================================================================
# filter_verified — the core transform
# =========================================================================


@pytest.mark.tier1
def test_keeps_only_verified_true(tmp_path: Path) -> None:
    """Only features with ``verified is True`` survive the filter."""
    src = _write_fc(tmp_path / "in.geojson", [
        _feature(25.7, 42.3, verified=True, id="a"),
        _feature(25.8, 42.4, verified=False, id="b"),
        _feature(25.9, 42.5, verified=True, id="c"),
    ])
    dst = tmp_path / "out.geojson"

    kept, total = filter_verified(src, dst)

    assert (kept, total) == (2, 3)
    out = json.loads(dst.read_text())
    ids = {f["properties"]["id"] for f in out["features"]}
    assert ids == {"a", "c"}


@pytest.mark.tier1
def test_output_stamps_explicit_wgs84_crs(tmp_path: Path) -> None:
    """The materialised subset declares EPSG:4326 explicitly."""
    src = _write_fc(tmp_path / "in.geojson", [
        _feature(25.7, 42.3, verified=True),
    ])
    dst = tmp_path / "out.geojson"

    filter_verified(src, dst)

    out = json.loads(dst.read_text())
    assert out["crs"]["properties"]["name"] == WGS84_URN


@pytest.mark.tier1
def test_truthy_non_boolean_not_kept(tmp_path: Path) -> None:
    """A truthy string/number must NOT be treated as accepted (``is True``)."""
    src = _write_fc(tmp_path / "in.geojson", [
        _feature(25.7, 42.3, verified="true", id="str"),
        _feature(25.8, 42.4, verified=1, id="one"),
        _feature(25.9, 42.5, verified=True, id="bool"),
    ])
    dst = tmp_path / "out.geojson"

    kept, total = filter_verified(src, dst)

    assert (kept, total) == (1, 3)
    out = json.loads(dst.read_text())
    assert [f["properties"]["id"] for f in out["features"]] == ["bool"]


@pytest.mark.tier1
def test_empty_accepted_subset_is_valid(tmp_path: Path) -> None:
    """All-rejected input yields a valid, empty FeatureCollection (F1=0 case)."""
    src = _write_fc(tmp_path / "in.geojson", [
        _feature(25.7, 42.3, verified=False),
        _feature(25.8, 42.4, verified=False),
    ])
    dst = tmp_path / "out.geojson"

    kept, total = filter_verified(src, dst)

    assert (kept, total) == (0, 2)
    out = json.loads(dst.read_text())
    assert out["features"] == []
    assert out["crs"]["properties"]["name"] == WGS84_URN


@pytest.mark.tier1
def test_keep_false_selects_rejected(tmp_path: Path) -> None:
    """``keep_value=False`` materialises the rejected subset instead."""
    src = _write_fc(tmp_path / "in.geojson", [
        _feature(25.7, 42.3, verified=True, id="a"),
        _feature(25.8, 42.4, verified=False, id="b"),
    ])
    dst = tmp_path / "out.geojson"

    kept, total = filter_verified(src, dst, keep_value=False)

    assert (kept, total) == (1, 2)
    out = json.loads(dst.read_text())
    assert out["features"][0]["properties"]["id"] == "b"


@pytest.mark.tier1
def test_polygon_geometry_supported(tmp_path: Path) -> None:
    """Nested (Polygon) coordinates pass the lon/lat guard and filter."""
    src = _write_fc(tmp_path / "in.geojson", [
        _polygon_feature(25.7, 42.3, verified=True, id="poly"),
    ])
    dst = tmp_path / "out.geojson"

    kept, total = filter_verified(src, dst)

    assert (kept, total) == (1, 1)


@pytest.mark.tier1
def test_rejects_utm_coordinates(tmp_path: Path) -> None:
    """UTM-metre coordinates must raise (the CRS-misread guard)."""
    src = _write_fc(tmp_path / "in.geojson", [
        _feature(369600.0, 4733600.0, verified=True),  # UTM 35N metres
    ])
    dst = tmp_path / "out.geojson"

    with pytest.raises(ValueError, match="UTM"):
        filter_verified(src, dst)
    assert not dst.exists()


@pytest.mark.tier1
def test_missing_flag_property_raises(tmp_path: Path) -> None:
    """Input with no ``verified`` property is the wrong shape and raises."""
    src = _write_fc(tmp_path / "in.geojson", [
        _feature(25.7, 42.3, id="no-flag"),
    ])
    dst = tmp_path / "out.geojson"

    with pytest.raises(ValueError, match="verified"):
        filter_verified(src, dst)


# =========================================================================
# Coordinate helpers
# =========================================================================


@pytest.mark.tier1
def test_first_coord_descends_nesting() -> None:
    """``_first_coord`` reaches the innermost vertex of a Polygon."""
    feats = [_polygon_feature(25.7, 42.3, verified=True)]
    assert _first_coord(feats) == (25.7, 42.3)


@pytest.mark.tier1
def test_first_coord_empty_collection() -> None:
    """An empty collection yields ``None`` (nothing to inspect)."""
    assert _first_coord([]) is None


@pytest.mark.tier1
@pytest.mark.parametrize(
    "xy,expected",
    [
        ((25.7, 42.3), True),       # Bulgarian lon/lat
        ((-179.9, -89.9), True),    # extreme but valid lon/lat
        ((369600.0, 4733600.0), False),  # UTM metres
        (None, True),               # empty → allowed
    ],
)
def test_looks_like_lonlat(xy: tuple[float, float] | None, expected: bool) -> None:
    """The lon/lat plausibility guard accepts degrees, rejects metres."""
    assert _looks_like_lonlat(xy) is expected
