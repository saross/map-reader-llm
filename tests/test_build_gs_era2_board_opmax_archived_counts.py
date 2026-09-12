"""Tier-1 tests for ``archived_cells()`` in ``scripts/build_gs_era2_board_opmax.py``.

Why these exist
---------------
``archived_n`` decides ``registry_vs_archived``, and that verdict decides whether
an ``-opmax`` row is re-pointed from the 2026-04-19 materialisation at a
re-materialised file. Until 2026-09-12 the count came from the archived
label-keyed evaluation cache whenever the archived board JSON omitted it — which
it does for all 44 cells. That cache has no content key, so a file
re-materialised under the same name leaves a stale count behind:
``reports/name-keyed-cache-audit-2026-09-12.md`` Finding 2 demonstrated it on
``pv-high-image-t0.3-n5``, where the cache's 372 agreed with the registry's 372
and so SUPPRESSED the ``differs`` verdict the file's real 373 features would have
raised.

The fix counts the features of the file the row names. These tests pin that
behaviour on a synthetic archive, so they exercise exactly the failure the audit
found without reading the 44 committed cells:

* the count comes from the file, not from the cache, even when the two disagree;
* the cache's value is still recorded, with an explicit agreement flag, so the
  discrepancy is visible rather than erased;
* a missing detection file raises rather than falling back to an inferred count.
"""

from __future__ import annotations

import json

import pytest

from scripts import build_gs_era2_board_opmax as opmax

pytestmark = pytest.mark.tier1


def _point_collection(n: int) -> dict:
    """A FeatureCollection of ``n`` Point features, the shape the counter reads."""
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature",
             "geometry": {"type": "Point", "coordinates": [300000.0 + i, 4700000.0]},
             "properties": {"label": "mound"}}
            for i in range(n)
        ],
    }


@pytest.fixture()
def fake_archive(tmp_path, monkeypatch):
    """A minimal archived board plus materialised files and one stale cache entry.

    Returns:
        The temporary repository root, with ``opmax.REPO_ROOT`` pointed at it.
    """
    archive = tmp_path / opmax.ARCHIVE
    materialised = tmp_path / opmax.MATERIALISED
    materialised.mkdir(parents=True)
    board = tmp_path / opmax.ARCHIVED_BOARD
    board.parent.mkdir(parents=True, exist_ok=True)
    board.write_text(json.dumps({
        "tiers": [
            {"tier": 1, "conditions": [
                # The audit's cell: the file holds 373, the cache says 372.
                {"label": "pv-high-image-t0.3-n5", "track": "image", "k": 5,
                 "evaluations": {"20": {"f1": 0.746}}},
                # A cell whose cache agrees with its file.
                {"label": "pv-min-text-t0.3-n5", "track": "text", "k": 5,
                 "evaluations": {"20": {"f1": 0.8778}}},
            ]},
        ],
    }), encoding="utf-8")
    (materialised / "pv-high-image-t0.3-n5.geojson").write_text(
        json.dumps(_point_collection(373)), encoding="utf-8")
    (materialised / "pv-min-text-t0.3-n5.geojson").write_text(
        json.dumps(_point_collection(408)), encoding="utf-8")
    cache_root = archive / "per-architecture/era2/pv/.cache/evaluations"
    for label, cached in (("pv-high-image-t0-3-n5", 372), ("pv-min-text-t0-3-n5", 408)):
        (cache_root / label).mkdir(parents=True)
        (cache_root / label / "t1_20m.json").write_text(
            json.dumps({"n_detections": cached}), encoding="utf-8")
    monkeypatch.setattr(opmax, "REPO_ROOT", tmp_path)
    return tmp_path


def test_archived_n_is_counted_from_the_file_not_the_cache(fake_archive):
    """The stale cache must not decide the count (audit Finding 2)."""
    cells = opmax.archived_cells()
    assert cells["pv-high-image-t0.3-n5"]["archived_n"] == 373
    assert cells["pv-high-image-t0.3-n5"]["archived_cache_n"] == 372
    assert cells["pv-high-image-t0.3-n5"]["archived_cache_agrees"] is False
    assert "counted from" in cells["pv-high-image-t0.3-n5"]["archived_n_basis"]


def test_a_cache_that_agrees_is_recorded_as_agreeing(fake_archive):
    cells = opmax.archived_cells()
    assert cells["pv-min-text-t0.3-n5"]["archived_n"] == 408
    assert cells["pv-min-text-t0.3-n5"]["archived_cache_n"] == 408
    assert cells["pv-min-text-t0.3-n5"]["archived_cache_agrees"] is True


def test_the_archived_f1_still_comes_from_the_board(fake_archive):
    """Only the COUNT moved to the file; F1 and tier are the board's as before."""
    cells = opmax.archived_cells()
    assert cells["pv-high-image-t0.3-n5"]["archived_f1_20"] == pytest.approx(0.746)
    assert cells["pv-high-image-t0.3-n5"]["archived_tier"] == 1
    assert cells["pv-high-image-t0.3-n5"]["track"] == "image"
    assert cells["pv-high-image-t0.3-n5"]["k_yaml"] == 5


def test_a_missing_detection_file_raises_rather_than_inferring_a_count(fake_archive):
    (fake_archive / opmax.MATERIALISED / "pv-high-image-t0.3-n5.geojson").unlink()
    with pytest.raises(FileNotFoundError, match="never inferred"):
        opmax.archived_cells()
