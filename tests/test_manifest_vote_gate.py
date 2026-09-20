"""
Tier-1 tests for the crop-manifest / union vote gate.

``scripts/check_union_provenance.py --manifest`` compares a
``candidate_manifest.json`` against the union it declares in
``source_geojson``: the count of detections, and every candidate's
``vote_count``. ``scripts/run_pv.py verify`` runs that check before either
the batch or the real-time path and refuses to spend on a manifest that
disagrees unless ``--allow-stale-manifest`` is passed.

The guard exists because the drift was silent for four months:
``results/im-june-pool-grid-2026-09-20/findings.md`` § 7 found five manifests
from the April/May 2026 recovery campaign carrying a ``vote_count`` one low on
15 to 110 candidates each, and one manifest a whole candidate short of its
union, with no artefact anywhere flagging either.

The contract exercised here, on synthetic manifests and unions:

* a manifest that agrees with its union passes;
* one stale ``vote_count`` fails and names the candidate id;
* a manifest carrying a candidate the union does not have fails;
* a union carrying a detection the manifest lacks fails — unless the
  manifest's own ``failed_extractions`` books it;
* a single-pass proposer output, which has no votes on either side, is
  ``NOT-APPLICABLE`` rather than a failure, and so is a union that is not on
  this machine (``UNRESOLVED``);
* ``run_pv.py verify`` refuses a ``DISAGREES`` manifest and proceeds under
  ``--allow-stale-manifest``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.check_union_provenance import (  # noqa: E402
    check_manifest_votes,
    main as check_main,
    resolve_manifest_union,
)
from scripts.merge_passes import geojson_coords_to_utm  # noqa: E402

pytestmark = pytest.mark.tier1


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

#: WGS84 anchors inside the 55-map corpus, far enough apart (~1 km) that no
#: pairing radius could confuse them.
ANCHORS: list[tuple[float, float]] = [
    (25.30000, 42.80000),
    (25.31200, 42.80000),
    (25.32400, 42.80000),
    (25.33600, 42.80000),
]

TILE = "K-35-051-4_x1344_y3360.png"


def _union_feature(lon: float, lat: float, vote_count: int) -> dict[str, Any]:
    """One consensus union feature, as ``merge_passes`` writes them (WGS84)."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "subtype": "burial_mound",
            "vote_count": vote_count,
            "total_passes": 5,
            "cluster_size": vote_count,
            "source_tiles": [TILE],
        },
    }


def _candidate(
    candidate_id: int,
    lon: float,
    lat: float,
    vote_count: int | None,
) -> dict[str, Any]:
    """One crop-manifest entry, with the UTM centroid ``extract`` records."""
    x, y = geojson_coords_to_utm(lon, lat)
    properties: dict[str, Any] = {"subtype": "burial_mound", "source_tile": TILE}
    if vote_count is not None:
        properties |= {
            "vote_count": vote_count,
            "total_passes": 5,
            "cluster_size": vote_count,
        }
    return {
        "candidate_id": candidate_id,
        "crop_file": f"crops/candidate_{candidate_id:05d}.png",
        "source_tile": TILE,
        "centroid_x": x,
        "centroid_y": y,
        "cropped_from": "raster",
        "properties": properties,
    }


def _write_case(
    tmp_path: Path,
    union_votes: list[int | None],
    manifest_votes: list[int | None],
    manifest_ids: list[int] | None = None,
    manifest_anchors: list[int] | None = None,
    failed_extractions: int = 0,
    source_geojson: str | None = None,
) -> Path:
    """Write a union and a crop manifest that points at it.

    Args:
        tmp_path: Test directory.
        union_votes: One vote count per union feature, positionally against
            :data:`ANCHORS`. ``None`` writes a feature with no ``vote_count``.
        manifest_votes: One vote count per manifest candidate.
        manifest_ids: Candidate ids (default: ``0..n-1``).
        manifest_anchors: Which anchor each candidate sits on (default: its
            own position).
        failed_extractions: The count the manifest books for itself.
        source_geojson: Override the declared union path.

    Returns:
        The path of the written ``candidate_manifest.json``.
    """
    union_path = tmp_path / "consensus" / "consensus-3of5.geojson"
    union_path.parent.mkdir(parents=True, exist_ok=True)
    union_path.write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [
            _union_feature(*ANCHORS[i], votes) if votes is not None else {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(ANCHORS[i])},
                "properties": {"subtype": "burial_mound"},
            }
            for i, votes in enumerate(union_votes)
        ],
    }))

    ids = manifest_ids if manifest_ids is not None else list(range(len(manifest_votes)))
    anchors = (
        manifest_anchors if manifest_anchors is not None
        else list(range(len(manifest_votes)))
    )
    crops_dir = tmp_path / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = crops_dir / "candidate_manifest.json"
    manifest_path.write_text(json.dumps({
        "version": "2.0",
        "source_geojson": source_geojson or str(union_path),
        "padding": 75,
        "total_detections": len(union_votes),
        "successful_extractions": len(manifest_votes),
        "failed_extractions": failed_extractions,
        "candidates": [
            _candidate(cid, *ANCHORS[anchor], votes)
            for cid, anchor, votes in zip(ids, anchors, manifest_votes)
        ],
    }, indent=2))
    return manifest_path


# ---------------------------------------------------------------------------
# The check itself
# ---------------------------------------------------------------------------


def test_agreeing_manifest_passes(tmp_path: Path) -> None:
    """Same detections, same votes — nothing to report."""
    manifest = _write_case(tmp_path, [5, 4, 3], [5, 4, 3])

    result = check_manifest_votes(manifest)

    assert result.classification == "AGREES"
    assert result.ok is True
    assert result.pairing == "candidate-id-index"
    assert (result.manifest_candidates, result.union_features) == (3, 3)
    assert result.vote_mismatches == []
    assert "Every vote_count agrees" in result.detail


def test_one_stale_vote_fails_and_names_the_candidate(tmp_path: Path) -> None:
    """The 2026-05-03 defect in miniature: one candidate a vote low."""
    manifest = _write_case(tmp_path, [5, 5, 3], [5, 4, 3])

    result = check_manifest_votes(manifest)

    assert result.classification == "DISAGREES"
    assert result.ok is False
    assert [m["candidate_id"] for m in result.vote_mismatches] == [1]
    assert result.vote_mismatches[0]["manifest_vote_count"] == 4
    assert result.vote_mismatches[0]["union_vote_count"] == 5
    assert "1 candidate(s) disagree on vote_count: 1" in result.detail
    # The counts agree, so only the votes can have raised this.
    assert (result.manifest_candidates, result.union_features) == (3, 3)


def test_manifest_with_an_extra_candidate_fails(tmp_path: Path) -> None:
    """A candidate the union does not carry is a detection nobody voted for."""
    manifest = _write_case(tmp_path, [5, 4], [5, 4, 3])

    result = check_manifest_votes(manifest)

    assert result.classification == "DISAGREES"
    assert result.manifest_only == [2]
    assert "have no union counterpart: 2" in result.detail


def test_union_candidate_the_manifest_lacks_fails(tmp_path: Path) -> None:
    """A union detection with no crop was never shown to the verifier."""
    manifest = _write_case(tmp_path, [5, 4, 3], [5, 4])

    result = check_manifest_votes(manifest)

    assert result.classification == "DISAGREES"
    assert result.union_only == [2]
    assert result.reconciled_failed_extractions == 0
    assert "union feature(s) have no candidate: index 2" in result.detail


def test_booked_failed_extractions_reconcile_a_missing_candidate(
    tmp_path: Path,
) -> None:
    """A crop the extractor recorded as failed is not a silent loss."""
    manifest = _write_case(tmp_path, [5, 4, 3], [5, 4], failed_extractions=1)

    result = check_manifest_votes(manifest)

    assert result.classification == "AGREES"
    assert result.reconciled_failed_extractions == 1
    assert "failed_extractions" in result.detail


def test_non_index_candidate_ids_fall_back_to_spatial_pairing(
    tmp_path: Path,
) -> None:
    """A recovery-patched manifest whose ids continue past the union's length.

    Its ids are no longer union indices, so the check pairs by position on
    the ground instead — and still catches the stale vote.
    """
    manifest = _write_case(
        tmp_path, [5, 4], [4, 4], manifest_ids=[7877, 7878],
    )

    result = check_manifest_votes(manifest)

    assert result.pairing == "spatial-nearest"
    assert result.classification == "DISAGREES"
    assert [m["candidate_id"] for m in result.vote_mismatches] == [7877]


def test_single_pass_output_without_votes_is_not_applicable(
    tmp_path: Path,
) -> None:
    """A proposer geojson has no votes; the gate must not block on it."""
    manifest = _write_case(tmp_path, [None, None], [None, None])

    result = check_manifest_votes(manifest)

    assert result.classification == "NOT-APPLICABLE"
    assert result.ok is True


def test_union_absent_from_this_machine_is_unresolved_not_a_refusal(
    tmp_path: Path,
) -> None:
    """An archived union leaves the votes unchecked, but does not stop a run."""
    manifest = _write_case(
        tmp_path, [5, 4], [5, 4], source_geojson="outputs/archived/nowhere.geojson",
    )

    result = check_manifest_votes(manifest)

    assert result.classification == "UNRESOLVED"
    assert result.ok is True
    assert "UNCHECKED" in result.detail


def test_explicit_union_overrides_the_declaration(tmp_path: Path) -> None:
    """``--manifest-union`` compares against a union the manifest does not name."""
    manifest = _write_case(
        tmp_path, [5, 4], [5, 4], source_geojson="outputs/archived/nowhere.geojson",
    )
    union = tmp_path / "consensus" / "consensus-3of5.geojson"

    result = check_manifest_votes(manifest, union_path=union)

    assert result.classification == "AGREES"


def test_resolve_manifest_union_reads_the_declaration(tmp_path: Path) -> None:
    """The union is found from ``source_geojson`` without being passed in."""
    manifest_path = _write_case(tmp_path, [5], [5])
    manifest = json.loads(manifest_path.read_text())

    resolved = resolve_manifest_union(manifest, manifest_path)

    assert resolved is not None
    assert resolved.name == "consensus-3of5.geojson"


# ---------------------------------------------------------------------------
# The standalone command
# ---------------------------------------------------------------------------


def test_cli_exits_non_zero_and_prints_the_disagreeing_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """Standalone use: exit 1, and the id is on stdout for a human."""
    manifest = _write_case(tmp_path, [5, 5], [5, 4])

    code = check_main(["--manifest", str(manifest)])
    out = capsys.readouterr().out

    assert code == 1
    assert "DISAGREES" in out
    assert "candidate 1: manifest vote_count 4 against union 5" in out


def test_cli_exits_zero_on_an_agreeing_manifest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """The green path stays green, and writes its JSON when asked."""
    manifest = _write_case(tmp_path, [5, 4], [5, 4])
    json_out = tmp_path / "manifest-check.json"

    code = check_main(["--manifest", str(manifest), "--json-out", str(json_out)])

    assert code == 0
    assert "AGREES" in capsys.readouterr().out
    written = json.loads(json_out.read_text())
    assert written["manifest_results"][0]["classification"] == "AGREES"


# ---------------------------------------------------------------------------
# The wiring into run_pv.py verify
# ---------------------------------------------------------------------------


def _verify_args(manifest_path: Path, tmp_path: Path, **overrides: Any) -> Any:
    """A ``run_pv.py verify`` argument namespace pointing at a crops dir."""
    config_path = tmp_path / "verify_adversarial-text.json"
    config_path.write_text(json.dumps({"model": "gemini-3-flash", "prompt": "x"}))
    args = {
        "crops_dir": manifest_path.parent,
        "verifier_config": config_path,
        "output_dir": tmp_path / "verified",
        "mode": "batch",
        "iterations": 1,
        "temperature": None,
        "workers": 5,
        "model": None,
        "thinking_level": None,
        "dry_run": False,
        "strict": True,
        "service_tier": "flex",
        "allow_stale_manifest": False,
    }
    args.update(overrides)
    return SimpleNamespace(**args)


def test_verify_refuses_a_stale_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No batch job and no real-time call is made over a stale manifest."""
    from scripts import run_pv

    called: list[str] = []
    monkeypatch.setattr(
        run_pv, "_verify_batch", lambda **kw: called.append("batch") or 0,
    )
    monkeypatch.setattr(
        run_pv, "_verify_realtime", lambda **kw: called.append("realtime") or 0,
    )
    manifest = _write_case(tmp_path, [5, 5], [5, 4])

    assert run_pv.cmd_verify(_verify_args(manifest, tmp_path)) == 1
    assert called == [], "the verifier must not be reached"


def test_allow_stale_manifest_proceeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The opt-out is explicit, and then the run goes ahead."""
    from scripts import run_pv

    called: list[str] = []
    monkeypatch.setattr(
        run_pv, "_verify_batch", lambda **kw: called.append("batch") or 0,
    )
    manifest = _write_case(tmp_path, [5, 5], [5, 4])

    code = run_pv.cmd_verify(
        _verify_args(manifest, tmp_path, allow_stale_manifest=True),
    )

    assert code == 0
    assert called == ["batch"]


def test_verify_proceeds_over_an_agreeing_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The gate is not in the way of a sound run."""
    from scripts import run_pv

    called: list[str] = []
    monkeypatch.setattr(
        run_pv, "_verify_batch", lambda **kw: called.append("batch") or 0,
    )
    manifest = _write_case(tmp_path, [5, 4], [5, 4])

    assert run_pv.cmd_verify(_verify_args(manifest, tmp_path)) == 0
    assert called == ["batch"]


def test_gate_is_open_when_the_union_cannot_be_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An archived union must not block a run that is otherwise sound."""
    from scripts import run_pv

    manifest = _write_case(
        tmp_path, [5, 4], [5, 4], source_geojson="outputs/archived/nowhere.geojson",
    )

    assert run_pv._manifest_vote_gate(manifest) is True
