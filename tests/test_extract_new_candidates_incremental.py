"""
Tier-1 tests for ``scripts/55maps-t0.3-extract-new-candidates.py``.

The script appends post-recovery consensus features to an existing crop
manifest without disturbing the candidate ids the verifier's
``probabilities.json`` is keyed to. Two defects in the version that ran the
2026-05-03 recovery campaign are diagnosed in
``results/im-june-pool-grid-2026-09-20/findings.md`` § 7 and fixed here:

* a **matched** entry's ``properties`` were never refreshed, so five legacy
  manifests carry a ``vote_count`` one low on 15 to 110 candidates each;
* matching was **greedy first-match** at a radius equal to the 20 m clustering
  radius, so two distinct consensus clusters 17.29 m apart both matched one
  manifest entry (``55maps-text-high-generalisation`` candidate 505) and the
  second cluster was never extracted or verified.

The contract exercised here, on a synthetic manifest and consensus:

* a matched entry's stale ``vote_count`` is refreshed from the consensus
  feature that claimed it, and keys the consensus does not carry survive;
* two clusters 17 m apart beside one entry yield **one** match and **one**
  extraction, and the collision is recorded as ambiguous with its distances;
* the ``candidate_id`` of a matched entry never changes;
* a run that only refreshes (no new features) still writes the manifest.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

pytestmark = pytest.mark.tier1

# The script's filename is not a legal module name (leading digit, hyphens),
# so it is loaded by path — the same pattern as tests/test_threshold_sweep.py.
_SPEC = importlib.util.spec_from_file_location(
    "extract_new_candidates",
    PROJECT_ROOT / "scripts" / "55maps-t0.3-extract-new-candidates.py",
)
extractor = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(extractor)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

#: A UTM (EPSG:32635) anchor inside the 55-map corpus. Coordinates above the
#: lat/lon magnitude bounds keep the script on its "already UTM" branch, so
#: the fixtures need no pyproj round trip.
ANCHOR_X, ANCHOR_Y = 467946.0, 4739799.0

TILE = "K-35-051-4_x1344_y3360.png"


def _manifest_entry(
    candidate_id: int,
    x: float,
    y: float,
    vote_count: int,
    passes: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """One ``candidate_manifest.json`` entry in the pipeline's shape."""
    properties: dict[str, Any] = {
        "subtype": "burial_mound",
        "vote_count": vote_count,
        "total_passes": 5,
        "contributing_passes": passes,
        "cluster_size": vote_count,
        "source_tiles": [TILE],
        "source_tile": TILE,
    }
    properties.update(extra or {})
    return {
        "candidate_id": candidate_id,
        "crop_file": f"crops/candidate_{candidate_id:05d}.png",
        "source_tile": TILE,
        "centroid_x": x,
        "centroid_y": y,
        "cropped_from": "raster",
        "properties": properties,
    }


def _consensus_feature(
    x: float, y: float, vote_count: int, passes: list[str],
) -> dict[str, Any]:
    """One post-recovery consensus feature, in UTM as the fixtures use it."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [x, y]},
        "properties": {
            "subtype": "burial_mound",
            "confidence": 1.0,
            "vote_count": vote_count,
            "total_passes": 5,
            "contributing_passes": passes,
            "cluster_size": vote_count,
            "source_tiles": [TILE],
        },
    }


def _write_case(
    tmp_path: Path,
    entries: list[dict[str, Any]],
    features: list[dict[str, Any]],
) -> tuple[Path, Path]:
    """Write a crops dir with a manifest and a consensus GeoJSON beside it."""
    crops_dir = tmp_path / "crops"
    (crops_dir / "crops").mkdir(parents=True)
    manifest = {
        "version": "2.0",
        "source_geojson": "outputs/synthetic/consensus/consensus-3of5.geojson",
        "padding": 75,
        "total_detections": len(entries),
        "successful_extractions": len(entries),
        "failed_extractions": 0,
        "candidates": entries,
    }
    manifest_path = crops_dir / "candidate_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    consensus_path = tmp_path / "consensus-3of5.geojson"
    consensus_path.write_text(json.dumps(
        {"type": "FeatureCollection", "features": features},
    ))
    return crops_dir, consensus_path


def _run_main(
    monkeypatch: pytest.MonkeyPatch,
    crops_dir: Path,
    consensus_path: Path,
    extra_argv: list[str] | None = None,
) -> int:
    """Invoke the script's ``main()`` with crop extraction stubbed out.

    The crop writer is replaced so the test needs neither the source rasters
    nor the tile PNGs; everything else — matching, refreshing, manifest
    rewriting — runs for real.
    """
    from scripts import extract_candidates

    def _fake_crop_region(source: Any, centroid: Any, padding: int, out: Path) -> bool:
        Path(out).write_bytes(b"PNG")
        return True

    monkeypatch.setattr(extract_candidates, "crop_region", _fake_crop_region)
    monkeypatch.setattr(
        extract_candidates, "resolve_raster_path",
        lambda tile, rasters_dir: Path("/nonexistent/raster.tif"),
    )
    monkeypatch.setattr(
        extract_candidates, "tile_id_to_map_name", lambda tile: "K-35-051-4",
    )
    monkeypatch.setattr(
        extract_candidates, "get_tile_path", lambda tile, tiles_dir: None,
    )

    argv = [
        "55maps-t0.3-extract-new-candidates.py",
        "--consensus", str(consensus_path),
        "--crops-dir", str(crops_dir),
        "--rasters-dir", str(crops_dir / "rasters"),
        "--tiles-dir", str(crops_dir / "tiles"),
    ] + (extra_argv or [])
    monkeypatch.setattr(sys, "argv", argv)
    return extractor.main()


def _load_manifest(crops_dir: Path) -> dict[str, Any]:
    return json.loads((crops_dir / "candidate_manifest.json").read_text())


# ---------------------------------------------------------------------------
# Defect 1 — a matched entry's properties were never refreshed
# ---------------------------------------------------------------------------


def test_refresh_replaces_a_stale_vote_count() -> None:
    """A matched entry takes the consensus feature's post-recovery votes."""
    entry = _manifest_entry(7, ANCHOR_X, ANCHOR_Y, 4, ["run_1", "run_2", "run_4", "run_5"])
    changed, before, after = extractor.refresh_entry_properties(
        entry,
        _consensus_feature(
            ANCHOR_X, ANCHOR_Y, 5,
            ["run_1", "run_2", "run_3", "run_4", "run_5"],
        )["properties"],
    )

    assert changed is True
    assert (before, after) == (4, 5)
    assert entry["properties"]["vote_count"] == 5
    assert entry["properties"]["cluster_size"] == 5
    assert entry["properties"]["contributing_passes"] == [
        "run_1", "run_2", "run_3", "run_4", "run_5",
    ]


def test_refresh_keeps_keys_the_consensus_does_not_carry() -> None:
    """A refresh is a merge: verification-derived fields survive it."""
    entry = _manifest_entry(
        7, ANCHOR_X, ANCHOR_Y, 4, ["run_1"], extra={"verifier_probability": 0.87},
    )
    extractor.refresh_entry_properties(
        entry, {"vote_count": 5, "cluster_size": 5},
    )

    assert entry["properties"]["verifier_probability"] == 0.87
    assert entry["properties"]["vote_count"] == 5
    # The crop on disk was cut from this tile; a refresh must not re-point it.
    assert entry["properties"]["source_tile"] == TILE


def test_refresh_reports_no_change_when_votes_already_current() -> None:
    """An entry that already agrees with its cluster is left alone."""
    passes = ["run_1", "run_2", "run_3"]
    entry = _manifest_entry(7, ANCHOR_X, ANCHOR_Y, 3, passes)
    feature_props = _consensus_feature(ANCHOR_X, ANCHOR_Y, 3, passes)["properties"]
    # The consensus feature carries no ``source_tile``; the entry keeps its own.
    feature_props.pop("confidence")

    changed, before, after = extractor.refresh_entry_properties(entry, feature_props)

    assert changed is False
    assert (before, after) == (3, 3)


# ---------------------------------------------------------------------------
# Defect 2 — greedy first-match let one entry absorb two clusters
# ---------------------------------------------------------------------------


def test_two_clusters_17m_apart_yield_one_match_and_one_extraction() -> None:
    """The 55maps-text-high candidate 505 collision, in miniature.

    Both clusters sit inside the 20 m radius of one manifest entry. The
    nearest claims it; the other is left unassigned, which is what makes the
    caller extract and verify it instead of dropping it.
    """
    assignment, ambiguous = extractor.match_one_to_one(
        consensus_points=[(ANCHOR_X, ANCHOR_Y), (ANCHOR_X + 17.29, ANCHOR_Y)],
        existing_points=[(ANCHOR_X, ANCHOR_Y)],
        threshold=20.0,
        consensus_ids=[0, 1],
        existing_ids=[505],
    )

    assert assignment == {0: 0}, "exactly one consensus feature may claim the entry"
    assert 1 not in assignment, "the second cluster must fall through to extraction"

    assert len(ambiguous) == 1
    record = ambiguous[0]
    assert record["candidate_id"] == 505
    assert record["n_features_within_radius"] == 2
    assert [hit["feature_id"] for hit in record["features"]] == [0, 1]
    assert [hit["distance_m"] for hit in record["features"]] == [0.0, 17.29]
    assert [hit["assigned"] for hit in record["features"]] == [True, False]


def test_nearest_pair_wins_regardless_of_file_order() -> None:
    """Assignment is by distance, not by the order features happen to sit in."""
    assignment, _ = extractor.match_one_to_one(
        # The far cluster is first in file order; the near one must still win.
        consensus_points=[(ANCHOR_X + 17.29, ANCHOR_Y), (ANCHOR_X + 0.5, ANCHOR_Y)],
        existing_points=[(ANCHOR_X, ANCHOR_Y)],
        threshold=20.0,
    )

    assert assignment == {1: 0}


def test_each_manifest_entry_is_claimed_at_most_once() -> None:
    """Three clusters over two entries leave exactly one unassigned."""
    assignment, _ = extractor.match_one_to_one(
        consensus_points=[
            (ANCHOR_X, ANCHOR_Y),
            (ANCHOR_X + 5.0, ANCHOR_Y),
            (ANCHOR_X + 10.0, ANCHOR_Y),
        ],
        existing_points=[(ANCHOR_X, ANCHOR_Y), (ANCHOR_X + 10.0, ANCHOR_Y)],
        threshold=20.0,
    )

    assert len(assignment) == 2
    assert len(set(assignment.values())) == 2, "no entry may be claimed twice"


def test_features_beyond_the_radius_are_not_matched() -> None:
    """Nothing outside the tolerance is absorbed."""
    assignment, ambiguous = extractor.match_one_to_one(
        consensus_points=[(ANCHOR_X + 25.0, ANCHOR_Y)],
        existing_points=[(ANCHOR_X, ANCHOR_Y)],
        threshold=20.0,
    )

    assert assignment == {}
    assert ambiguous == []


# ---------------------------------------------------------------------------
# End to end through ``main()``
# ---------------------------------------------------------------------------


def test_end_to_end_refreshes_matches_and_extracts_the_collision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One run covering both defects, plus the id-stability guarantee."""
    entries = [
        _manifest_entry(0, ANCHOR_X, ANCHOR_Y, 4, ["run_1", "run_2", "run_4", "run_5"]),
        _manifest_entry(
            505, ANCHOR_X + 1000.0, ANCHOR_Y, 4, ["run_1", "run_2", "run_3", "run_4"],
        ),
    ]
    features = [
        # Refreshes candidate 0 from 4 votes to 5.
        _consensus_feature(
            ANCHOR_X, ANCHOR_Y, 5, ["run_1", "run_2", "run_3", "run_4", "run_5"],
        ),
        # Claims candidate 505 and refreshes it to 5 votes.
        _consensus_feature(
            ANCHOR_X + 1000.0, ANCHOR_Y, 5,
            ["run_1", "run_2", "run_3", "run_4", "run_5"],
        ),
        # 17.29 m from candidate 505 — inside the radius, a distinct cluster.
        _consensus_feature(
            ANCHOR_X + 1017.29, ANCHOR_Y, 4, ["run_1", "run_2", "run_3", "run_5"],
        ),
    ]
    crops_dir, consensus_path = _write_case(tmp_path, entries, features)

    assert _run_main(monkeypatch, crops_dir, consensus_path) == 0

    manifest = _load_manifest(crops_dir)
    by_id = {c["candidate_id"]: c for c in manifest["candidates"]}

    # Ids of matched entries never change — probabilities.json stays valid.
    assert 0 in by_id and 505 in by_id
    assert by_id[0]["crop_file"] == "crops/candidate_00000.png"
    assert by_id[505]["crop_file"] == "crops/candidate_00505.png"

    # Both matched entries carry post-recovery votes.
    assert by_id[0]["properties"]["vote_count"] == 5
    assert by_id[505]["properties"]["vote_count"] == 5
    assert by_id[505]["properties"]["contributing_passes"] == [
        "run_1", "run_2", "run_3", "run_4", "run_5",
    ]

    # The collision was extracted rather than absorbed, under a fresh id that
    # continues from the manifest's previous maximum (505 → 506).
    assert len(manifest["candidates"]) == 3
    assert set(by_id) == {0, 505, 506}
    assert by_id[506]["properties"]["vote_count"] == 4
    assert by_id[506]["crop_file"] == "crops/candidate_00506.png"

    # A manifest can never again book more matches than it has entries.
    history = manifest["recovery_history"][-1]
    assert history["matched_to_existing"] == 2
    assert history["matched_to_existing"] <= history["existing_candidates"]
    assert history["new_consensus_features"] == 3
    assert history["new_extracted"] == 1
    assert history["matching"] == "one-to-one-nearest"

    # The audit block books the refresh and the ambiguity.
    assert history["properties_refreshed"] == 2
    assert history["vote_count_changed"] == 2
    assert sorted(
        change["candidate_id"] for change in history["vote_count_changes"]
    ) == [0, 505]
    assert all(
        (change["vote_count_before"], change["vote_count_after"]) == (4, 5)
        for change in history["vote_count_changes"]
    )
    assert len(history["ambiguous_matches"]) == 1
    assert history["ambiguous_matches"][0]["candidate_id"] == 505
    assert [
        hit["distance_m"] for hit in history["ambiguous_matches"][0]["features"]
    ] == [0.0, 17.29]


def test_refresh_only_run_still_writes_the_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No new features is not the same as nothing to do.

    The pre-fix script returned early when every consensus feature matched,
    which is exactly the case the three text recovery runs hit — and why
    their stale vote counts were never repaired.
    """
    entries = [_manifest_entry(0, ANCHOR_X, ANCHOR_Y, 4, ["run_1", "run_2", "run_4", "run_5"])]
    features = [_consensus_feature(
        ANCHOR_X, ANCHOR_Y, 5, ["run_1", "run_2", "run_3", "run_4", "run_5"],
    )]
    crops_dir, consensus_path = _write_case(tmp_path, entries, features)

    assert _run_main(monkeypatch, crops_dir, consensus_path) == 0

    manifest = _load_manifest(crops_dir)
    assert len(manifest["candidates"]) == 1
    assert manifest["candidates"][0]["candidate_id"] == 0
    assert manifest["candidates"][0]["properties"]["vote_count"] == 5
    history = manifest["recovery_history"][-1]
    assert (history["properties_refreshed"], history["new_extracted"]) == (1, 0)
    assert list(crops_dir.glob("candidate_manifest.json.pre-recovery-*.backup"))


def test_dry_run_leaves_the_manifest_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``--dry-run`` reports the refresh without performing it."""
    entries = [_manifest_entry(0, ANCHOR_X, ANCHOR_Y, 4, ["run_1"])]
    features = [_consensus_feature(ANCHOR_X, ANCHOR_Y, 5, ["run_1", "run_2"])]
    crops_dir, consensus_path = _write_case(tmp_path, entries, features)
    before = (crops_dir / "candidate_manifest.json").read_text()

    assert _run_main(monkeypatch, crops_dir, consensus_path, ["--dry-run"]) == 0

    assert (crops_dir / "candidate_manifest.json").read_text() == before
    assert not list(crops_dir.glob("*.backup"))
