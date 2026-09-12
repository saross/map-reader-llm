"""Tier-1 tests for the bootstrap CI path repair and re-run.

``scripts/repair_bootstrap_cis.py`` rewrote 472 ``source_file`` values and
replaced the values of 85 entries in a paper-citable store, so the properties
worth pinning are the ones that make that safe to have done:

* the repair is **byte-idempotent** — running it twice leaves the file alone,
  including its provenance note, which an early version clobbered with zeros;
* it **preserves** the original string rather than discarding it, and marks what
  it could not resolve instead of guessing;
* it preserves the committed **formatting** (``indent=2``, no trailing newline),
  so the diff is confined to the fields that changed;
* the estimator is the **percentile** method, not today's BCa — the 411
  untouched entries were computed with the former, and mixing the two inside one
  store would have been a methodological error invisible to every existing gate.

The bootstrap itself is exercised on a two-tile synthetic frame, which is enough
to pin the estimator's shape and determinism without the ~8 s a real pass costs.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

import scripts.repair_bootstrap_cis as rbc

pytestmark = pytest.mark.tier1

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def write_geojson(path: Path, points: list[tuple[float, float]]) -> None:
    """Write a point FeatureCollection at ``path``.

    Args:
        path: Destination file (parent directories are created).
        points: ``(x, y)`` coordinates, one feature each.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {"type": "Point", "coordinates": [x, y]},
                }
                for x, y in points
            ],
        }),
        encoding="utf-8",
    )


def make_store(entries: dict[str, dict]) -> dict:
    """Wrap entries in the store's two-key top-level shape."""
    return {"_metadata": {"total_tasks": len(entries)}, "results": entries}


def entry(n_detections: int, source_file: str) -> dict:
    """Build a store entry with the real field order."""
    block = {"mean": 0.5, "ci_lower": 0.4, "ci_upper": 0.6}
    return {
        "f1": dict(block),
        "precision": dict(block),
        "recall": dict(block),
        "n_iterations": 1000,
        "n_detections": n_detections,
        "source_file": source_file,
        "elapsed_seconds": 7.0,
    }


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A synthetic repository root the repair resolves paths against.

    ``repair_paths`` resolves against the module-level ``PROJECT_ROOT``, so the
    fixture repoints it at ``tmp_path`` for the duration of the test.
    """
    monkeypatch.setattr(rbc, "PROJECT_ROOT", tmp_path)
    return tmp_path


class TestRemapSource:
    """The prefix remap table, entry by entry."""

    def test_retest_prefix(self, repo: Path) -> None:
        """A ``data/retest/`` path resolves under ``outputs/retest/``."""
        write_geojson(repo / "outputs/retest/a/d.geojson", [(0.0, 0.0)])
        assert rbc.remap_source("data/retest/a/d.geojson") == "outputs/retest/a/d.geojson"

    def test_consensus_proposer_prefix(self, repo: Path) -> None:
        """A ``data/consensus-proposers/`` path resolves into the archive tree."""
        target = "archive/outputs-experimental-pilot/pv/consensus-proposers/c.geojson"
        write_geojson(repo / target, [(0.0, 0.0)])
        assert rbc.remap_source("data/consensus-proposers/c.geojson") == target

    def test_pseudo_path_never_resolves(self, repo: Path) -> None:
        """A ``consensus:`` label is not a path and must not be guessed at."""
        assert rbc.remap_source("consensus:consensus-n30:high/25of30") is None

    def test_absent_file_does_not_resolve(self, repo: Path) -> None:
        """A remapped path that does not exist is reported as unresolved."""
        assert rbc.remap_source("data/retest/missing/d.geojson") is None


class TestRepairPaths:
    """What the ``repair-paths`` subcommand writes, and what it leaves alone."""

    @pytest.fixture()
    def store_path(self, repo: Path) -> Path:
        """A three-entry store: one remappable, one dead, one pseudo-path."""
        write_geojson(repo / "outputs/retest/a/d.geojson", [(0.0, 0.0)])
        store = make_store({
            "single:a": entry(1, "data/retest/a/d.geojson"),
            "single:gone": entry(5, "data/retest/gone/d.geojson"),
            "consensus-n30:label": entry(9, "consensus:consensus-n30:text/5of30"),
        })
        path = repo / "store.json"
        path.write_text(json.dumps(store, indent=2), encoding="utf-8")
        return path

    def test_rewrites_and_preserves_the_original(self, store_path: Path) -> None:
        """The resolvable entry is rewritten with its original string kept."""
        rbc.repair_paths([store_path])
        payload = json.loads(store_path.read_text(encoding="utf-8"))
        got = payload["results"]["single:a"]
        assert got["source_file"] == "outputs/retest/a/d.geojson"
        assert got["source_file_original"] == "data/retest/a/d.geojson"

    def test_source_file_original_sits_beside_source_file(
        self, store_path: Path
    ) -> None:
        """Key order is preserved, with the original inserted adjacently.

        The store is read by humans reviewing a diff; a reordered entry would
        make the repair's diff unreadable and hide what actually changed.
        """
        rbc.repair_paths([store_path])
        payload = json.loads(store_path.read_text(encoding="utf-8"))
        keys = list(payload["results"]["single:a"])
        assert keys == [
            "f1", "precision", "recall", "n_iterations", "n_detections",
            "source_file", "source_file_original", "elapsed_seconds",
        ]

    def test_marks_what_it_cannot_resolve(self, store_path: Path) -> None:
        """Unresolvable entries are flagged, not silently rewritten."""
        rbc.repair_paths([store_path])
        results = json.loads(store_path.read_text(encoding="utf-8"))["results"]
        for key in ("single:gone", "consensus-n30:label"):
            assert results[key]["source_status"] == "unresolved"
            assert "source_file_original" not in results[key]
        assert results["single:gone"]["source_file"] == "data/retest/gone/d.geojson"

    def test_records_a_provenance_note_at_the_head(self, store_path: Path) -> None:
        """``_path_repair`` carries the counts and sits beside ``_metadata``."""
        rbc.repair_paths([store_path])
        payload = json.loads(store_path.read_text(encoding="utf-8"))
        assert list(payload) == ["_metadata", "_path_repair", "results"]
        note = payload["_path_repair"]
        assert (note["repaired_entries"], note["unresolved_entries"]) == (1, 2)
        assert note["audit_report"].startswith("reports/name-keyed-cache-audit")
        assert [r["from"] for r in note["remaps"]] == [a for a, _ in rbc.REMAPS]

    def test_is_byte_idempotent(self, store_path: Path) -> None:
        """A second run changes nothing — not even the note's own counters.

        An earlier version rewrote ``repaired_entries`` to 0 and
        ``already_current`` to 472 on the second run, destroying the record of
        what the repair had done.
        """
        rbc.repair_paths([store_path])
        first = store_path.read_bytes()
        rbc.repair_paths([store_path])
        assert store_path.read_bytes() == first

    def test_dry_run_writes_nothing(self, store_path: Path) -> None:
        """``--dry-run`` reports without touching the file."""
        before = store_path.read_bytes()
        rbc.repair_paths([store_path], dry_run=True)
        assert store_path.read_bytes() == before


class TestStoreFormatting:
    """The committed files' formatting, which the repair had to preserve."""

    def test_round_trip_is_byte_identical(self, tmp_path: Path) -> None:
        """``write_store`` reproduces ``indent=2`` with no trailing newline."""
        payload = {"_metadata": {"a": 1}, "results": {"k": {"n_detections": 2}}}
        path = tmp_path / "s.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        original = path.read_bytes()
        rbc.write_store(path, json.loads(path.read_text(encoding="utf-8")))
        assert path.read_bytes() == original

    def test_committed_store_matches_that_formatting(self) -> None:
        """The real store still round-trips byte-identically after the repair."""
        path = PROJECT_ROOT / "results" / "all-bootstrap-cis.json"
        raw = path.read_bytes()
        assert json.dumps(json.loads(raw), indent=2).encode("utf-8") == raw


class TestPinnedEstimator:
    """The percentile bootstrap, pinned to the March 2026 implementation."""

    @pytest.fixture()
    def frame(self) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """A two-tile frame with one hit and one miss per tile.

        Tiles are 1 km squares side by side. Each holds one reference point; the
        detections hit the first tile's point (5 m away, inside the 20 m buffer)
        and miss the second's (500 m away), so the resample distribution is
        non-degenerate and the percentile bounds are meaningful.
        """
        crs = rbc.TARGET_CRS
        # ``tile_name`` carries the ``.png`` suffix, and a detection's
        # ``source_tile`` must equal it exactly — the per-tile builder drops
        # counts for any tile name it cannot find, so a fixture that got this
        # wrong would silently score 0.0 rather than fail.
        bounds = gpd.GeoDataFrame(
            {"tile_name": ["MAPA_x0_y0.png", "MAPA_x1000_y0.png"]},
            geometry=[box(0, 0, 1000, 1000), box(1000, 0, 2000, 1000)],
            crs=crs,
        )
        reference = gpd.GeoDataFrame(
            {"Map": ["MAPA", "MAPA"]},
            geometry=[Point(500, 500), Point(1500, 500)],
            crs=crs,
        )
        # ``source_tile`` is required: the per-tile metric builder scopes
        # detections to a map by that column, as the pipeline's own GeoJSONs do.
        detections = gpd.GeoDataFrame(
            {
                "label": ["burial mound", "burial mound"],
                "source_tile": ["MAPA_x0_y0.png", "MAPA_x1000_y0.png"],
            },
            geometry=[Point(505, 500), Point(1900, 900)],
            crs=crs,
        )
        return detections, reference, bounds

    def test_returns_the_stored_block_shape(self, frame) -> None:
        """Each metric carries exactly ``mean`` / ``ci_lower`` / ``ci_upper``."""
        detections, reference, bounds = frame
        got = rbc.bootstrap_ci_percentile(
            detections, reference, bounds, n_iterations=50, random_seed=42
        )
        assert set(got) == {"f1", "precision", "recall", "n_iterations"}
        for metric in ("f1", "precision", "recall"):
            assert set(got[metric]) == {"mean", "ci_lower", "ci_upper"}
            assert got[metric]["ci_lower"] <= got[metric]["mean"] <= got[metric]["ci_upper"]
        assert got["n_iterations"] == 50

    def test_is_deterministic_under_the_seed(self, frame) -> None:
        """The same seed gives the same numbers; a different seed does not."""
        detections, reference, bounds = frame
        kwargs = {"n_iterations": 50}
        first = rbc.bootstrap_ci_percentile(
            detections, reference, bounds, random_seed=42, **kwargs
        )
        again = rbc.bootstrap_ci_percentile(
            detections, reference, bounds, random_seed=42, **kwargs
        )
        other = rbc.bootstrap_ci_percentile(
            detections, reference, bounds, random_seed=7, **kwargs
        )
        assert first == again
        assert first["f1"]["mean"] != other["f1"]["mean"]

    def test_bounds_are_percentiles_not_bca(self, frame) -> None:
        """The bounds are the 2.5th / 97.5th percentiles of the resamples.

        Recomputed here from the same resampling loop, which is what makes this
        a test of the *method* rather than of the numbers. Today's
        ``lib_advanced_metrics.bootstrap_ci`` returns BCa intervals and would
        fail this.
        """
        detections, reference, bounds = frame
        got = rbc.bootstrap_ci_percentile(
            detections, reference, bounds, n_iterations=200, random_seed=42
        )
        tiles = bounds["tile_name"].unique()
        tile_metrics = rbc.compute_per_tile_tp_fp_fn(
            detections, reference, bounds, buffer_metres=rbc.DEFAULT_BUFFER_METRES
        )
        rng = np.random.default_rng(42)
        f1_scores = []
        for _ in range(200):
            sample = rng.choice(tiles, len(tiles), replace=True)
            f1_scores.append(rbc.aggregate_tile_metrics(tile_metrics, sample)[2])
        assert got["f1"]["mean"] == pytest.approx(float(np.mean(f1_scores)))
        assert got["f1"]["ci_lower"] == pytest.approx(
            float(np.percentile(f1_scores, 2.5))
        )
        assert got["f1"]["ci_upper"] == pytest.approx(
            float(np.percentile(f1_scores, 97.5))
        )

    def test_empty_bounds_return_empty(self, frame) -> None:
        """No tiles means no resampling unit, so no interval is invented."""
        detections, reference, bounds = frame
        assert rbc.bootstrap_ci_percentile(detections, reference, bounds.iloc[0:0]) == {}


class TestEvaluationFrame:
    """The frame the re-run used, which the reproduction gate identified."""

    def test_frame_files_exist_and_have_the_expected_extent(self) -> None:
        """340 tiles and the gold-standard reference, per the passing gate.

        The 487-tile 384 px frame would have been the wrong choice and would
        have failed the gate; pinning the counts stops a later default change
        from silently redefining what a re-run means.
        """
        reference, bounds = rbc.load_frame()
        assert len(bounds) == 340
        assert bounds["tile_name"].nunique() == 340
        assert len(reference) == 569
        assert "Map" in reference.columns
        assert bounds.crs.to_string() == rbc.TARGET_CRS
        assert reference.crs.to_string() == rbc.TARGET_CRS

    def test_rerun_note_records_that_frame(self) -> None:
        """The committed store says which frame and estimator produced the 85."""
        path = PROJECT_ROOT / "results" / "all-bootstrap-cis.json"
        note = json.loads(path.read_text(encoding="utf-8"))["_rerun"]
        assert note["n_iterations"] == rbc.DEFAULT_ITERATIONS
        assert note["random_seed"] == rbc.DEFAULT_SEED
        assert note["buffer_metres"] == rbc.DEFAULT_BUFFER_METRES
        assert note["method"].startswith("percentile")
        assert note["bounds"].endswith("full_evaluation_bounds.geojson")
        assert note["reference"].endswith("mounds-reference.geojson")
