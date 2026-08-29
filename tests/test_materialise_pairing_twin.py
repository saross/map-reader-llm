"""Tier-1 tests for the pre-verifier twin materialiser.

The corrected-F1 engine scopes detections per map sheet with
``gdf_det["source_tile"].str.startswith(...)``, so a twin without that column
crashes at the first buffer — which is what the two 55-map twin jobs did on
2026-08-29. The twin is therefore built from the verifier stage's own crop
manifest, where the value the VERIFIED side used is recorded, rather than
inferred from the bounds file.

These tests pin the gates that make that substitution safe: the shell filter,
the recorded-tile copy, and the refusals that stop a silently-different twin
from being written.

Created: 2026-08-29 (uplift-supplement card, pairing-scoring repair)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.materialise_pairing_twin import (
    TwinMaterialisationError,
    build_twin,
    main,
)

pytestmark = pytest.mark.tier1


def _manifest(votes_and_tiles: list[tuple[int, str | None]]) -> dict:
    """Build a crop manifest from (vote_count, source_tile) pairs."""
    return {
        "source_geojson": "outputs/run/consensus/consensus-3of5.geojson",
        "total_detections": len(votes_and_tiles),
        "candidates": [
            {
                "candidate_id": i,
                "centroid_x": 400000.0 + i,
                "centroid_y": 4700000.0 + i,
                "source_tile": tile,
                "properties": {"vote_count": votes, "source_tiles": ["a", "b"]},
            }
            for i, (votes, tile) in enumerate(votes_and_tiles)
        ],
    }


class TestBuildTwin:
    """Selecting the vote shell and carrying the recorded tile."""

    def test_keeps_only_the_vote_shell(self) -> None:
        """k is the verified cell's own threshold; below it is not the twin."""
        manifest = _manifest([(1, "t1"), (3, "t2"), (4, "t3"), (5, "t4")])
        features, stats = build_twin(manifest, min_votes=3)
        assert stats["n_kept"] == 3
        assert [f["properties"]["vote_count"] for f in features] == [3, 4, 5]

    def test_copies_the_recorded_source_tile(self) -> None:
        """Copied verbatim — the verified side used exactly these values.

        Deriving the tile from the bounds file instead would be the
        unconstrained nearest-centroid assignment that `stride55_score.py`
        records as flipping 10.1 % of candidates to the adjacent sheet and
        moving corrected-F1 by about 0.04.
        """
        manifest = _manifest([(3, "K-35-052-4_x0_y0"), (5, "K-35-052-4_x1_y1")])
        features, _stats = build_twin(manifest, min_votes=3)
        assert [f["properties"]["source_tile"] for f in features] == [
            "K-35-052-4_x0_y0", "K-35-052-4_x1_y1",
        ]

    def test_geometry_is_the_recorded_centroid(self) -> None:
        """Same centroids as the verified side, so only the filter differs."""
        manifest = _manifest([(3, "t1")])
        features, _stats = build_twin(manifest, min_votes=3)
        assert features[0]["geometry"]["coordinates"] == [400000.0, 4700000.0]

    def test_missing_source_tile_refuses(self) -> None:
        """A kept candidate with no tile would leave its map's scope silently."""
        manifest = _manifest([(3, "t1"), (4, None)])
        with pytest.raises(TwinMaterialisationError, match="no source_tile"):
            build_twin(manifest, min_votes=3)

    def test_a_missing_tile_below_the_shell_is_irrelevant(self) -> None:
        """Only KEPT candidates matter; the rest are not in the twin."""
        manifest = _manifest([(1, None), (4, "t2")])
        features, _stats = build_twin(manifest, min_votes=3)
        assert len(features) == 1

    def test_non_contiguous_ids_refuse(self) -> None:
        """The manifest is joined positionally elsewhere in the chain."""
        manifest = _manifest([(3, "t1"), (4, "t2")])
        manifest["candidates"][1]["candidate_id"] = 7
        with pytest.raises(TwinMaterialisationError, match="contiguous range"):
            build_twin(manifest, min_votes=3)

    def test_empty_manifest_refuses(self) -> None:
        """Nothing to build a twin from is a stop, not an empty twin."""
        with pytest.raises(TwinMaterialisationError, match="no candidates"):
            build_twin({"candidates": []}, min_votes=3)

    def test_non_integer_votes_are_not_kept(self) -> None:
        """A missing or malformed vote count cannot satisfy a threshold."""
        manifest = _manifest([(3, "t1")])
        manifest["candidates"][0]["properties"]["vote_count"] = None
        features, _stats = build_twin(manifest, min_votes=3)
        assert features == []


class TestMain:
    """The CLI, including the candidate-universe report."""

    def test_writes_a_geojson_with_the_evaluation_crs(self, tmp_path: Path) -> None:
        """The 55-map corrected-F1 chain works in UTM 35N."""
        manifest_path = tmp_path / "candidate_manifest.json"
        manifest_path.write_text(json.dumps(_manifest([(3, "t1"), (5, "t2")])),
                                 encoding="utf-8")
        out = tmp_path / "twin.geojson"
        assert main(["--crop-manifest", str(manifest_path), "--min-votes", "3",
                     "--output", str(out)]) == 0
        document = json.loads(out.read_text(encoding="utf-8"))
        assert document["crs"]["properties"]["name"] == "EPSG:32635"
        assert len(document["features"]) == 2

    def test_reports_a_candidate_universe_difference(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """text-high's manifest holds 9,205 of the committed set's 9,206.

        The twin follows the MANIFEST — that is the universe the verified side
        was drawn from — but the difference is reported rather than absorbed.
        """
        manifest_path = tmp_path / "candidate_manifest.json"
        manifest_path.write_text(json.dumps(_manifest([(3, "t1"), (5, "t2")])),
                                 encoding="utf-8")
        consensus = tmp_path / "consensus.geojson"
        consensus.write_text(json.dumps({
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {}} for _ in range(3)],
        }), encoding="utf-8")
        main(["--crop-manifest", str(manifest_path), "--min-votes", "3",
              "--expect-consensus", str(consensus),
              "--output", str(tmp_path / "twin.geojson")])
        assert "delta +1" in capsys.readouterr().err

    def test_a_failed_gate_writes_nothing(self, tmp_path: Path) -> None:
        """A refused twin must not leave a half-right file behind."""
        manifest_path = tmp_path / "candidate_manifest.json"
        manifest_path.write_text(json.dumps(_manifest([(3, None)])),
                                 encoding="utf-8")
        out = tmp_path / "twin.geojson"
        assert main(["--crop-manifest", str(manifest_path), "--min-votes", "3",
                     "--output", str(out)]) == 2
        assert not out.exists()
