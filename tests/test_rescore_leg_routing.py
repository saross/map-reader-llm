"""
Tier-1 tests: the gold-standard (GS) and bridge readers route their legs through the leg rule.

Why this exists
---------------
PI decision D62 (1) step 2 (2026-10-13) re-verified 1,029 verifier rows whose
crops had been cut from the neighbouring sheet's raster, and booked the
answers in ``<leg>_repaired/`` copies beside 95 committed legs
(``reports/s163-agent-records/wrong-sheet-crops-sweep-2026-10-13.md``). The
GS readers read their legs by fixed name, so none of those rows reached a
board. The S164 re-score (``reports/s164-agent-records/rescore-repaired-gs.md``)
routes every reader through the one rule in ``scripts/lib_verify_dirs.py``:
a leg is read from ``<leg>_repaired/`` when that copy holds
``probabilities.json``, from ``<leg>/`` otherwise, and always from ``<leg>/``
under ``MAP_READER_VERIFY_DIRS=fixed``; each reader records the directory it
read as ``verifier_probabilities``.

What is pinned
--------------
* the three union loaders (``grid_verifier_analysis.load_verified_union``,
  ``stride_verifier_analysis.load_stride_union``,
  ``image_b_analysis.load_image_union``) read the repaired copy by default,
  the leg under the fixed policy, and record which;
* ``load_stride_union_on_origin`` keeps that record through the origin step;
* the six-cell anchor gate reads its originals FIXED (it checks the
  instrument against the values registered on the legs as run);
* the bridge's replicate-1 readers resolve ``verify_g3`` to
  ``verify_g3_repaired`` and record the directory actually read;
* the temperature probe reads each leg under the rule.

The loader tests are the red sentinel of the S164 routing PR: on the code
before it, each loader read ``verify/`` by name and set no record, so they fail.
All synthetic; nothing is read from the repository's data.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point

from scripts.lib_verify_dirs import POLICY_ENV, read_leg_results

pytestmark = pytest.mark.tier1

#: Two candidates; the base leg and the repaired copy disagree on the second.
BASE = {"candidate_00000": 0.9, "candidate_00001": 0.05}
REPAIRED = {"candidate_00000": 0.9, "candidate_00001": 0.95}


@pytest.fixture(autouse=True)
def _default_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test starts from the default policy, whatever the shell exports."""
    monkeypatch.delenv(POLICY_ENV, raising=False)


def _write_probs(vdir: Path, probs: dict[str, float]) -> None:
    """A minimal ``probabilities.json`` in ``vdir``."""
    vdir.mkdir(parents=True, exist_ok=True)
    (vdir / "probabilities.json").write_text(json.dumps(
        {"results": {k: {"mound_probability": v} for k, v in probs.items()}}))


def _write_union(path: Path) -> None:
    """A two-row union in EPSG:4326 with the columns the loaders read."""
    path.parent.mkdir(parents=True, exist_ok=True)
    gpd.GeoDataFrame(
        {"vote_count": [3, 1], "source_tile": ["K-35-053-3_Elenovo_x0_y0"] * 2},
        geometry=[Point(25.0, 42.0), Point(25.001, 42.001)], crs="EPSG:4326",
    ).to_file(path, driver="GeoJSON")


def _cell(vroot: Path, leg: str, union_name: str) -> Path:
    """A verifier cell holding one union, its leg, and the leg's repaired copy."""
    _write_union(vroot / union_name)
    _write_probs(vroot / leg, BASE)
    _write_probs(vroot / f"{leg}_repaired", REPAIRED)
    return vroot


# --------------------------------------------------------------------------- #
# The library helper.
# --------------------------------------------------------------------------- #


def test_read_leg_results_returns_the_rows_and_the_record(tmp_path: Path) -> None:
    _write_probs(tmp_path / "verify", BASE)
    _write_probs(tmp_path / "verify_repaired", REPAIRED)
    results, prov = read_leg_results(tmp_path, "verify", tmp_path)
    assert results["candidate_00001"]["mound_probability"] == 0.95
    assert prov["dir"] == "verify_repaired"
    assert prov["policy"] == "repaired"
    results, prov = read_leg_results(tmp_path, "verify", tmp_path, "fixed")
    assert results["candidate_00001"]["mound_probability"] == 0.05
    assert prov["dir"] == "verify"
    assert prov["policy"] == "fixed"


# --------------------------------------------------------------------------- #
# The three union loaders (the red sentinel).
# --------------------------------------------------------------------------- #


def test_grid_loader_reads_the_repaired_copy_and_records_it(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import grid_verifier_analysis as gva

    _cell(tmp_path / "g384_ov192", "verify", "union_k10.geojson")
    monkeypatch.setattr(gva, "VERIFIER_DIR", tmp_path)
    monkeypatch.setattr(gva, "PROJECT_ROOT", tmp_path)
    monkeypatch.setitem(gva.EXPECTED, "g384_ov192", 2)

    gdf = gva.load_verified_union("g384_ov192")
    assert list(gdf["mound_probability"]) == [0.9, 0.95]
    assert gdf.attrs["verifier_probabilities"]["dir"] == "g384_ov192/verify_repaired"

    monkeypatch.setenv(POLICY_ENV, "fixed")
    gdf = gva.load_verified_union("g384_ov192")
    assert list(gdf["mound_probability"]) == [0.9, 0.05]
    assert gdf.attrs["verifier_probabilities"]["dir"] == "g384_ov192/verify"
    assert gdf.attrs["verifier_probabilities"]["policy"] == "fixed"


def test_stride_loader_reads_the_repaired_copy_and_records_it(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import stride_verifier_analysis as sva

    _cell(tmp_path / "out" / "verifier" / "g9_test", "verify_k3", "union_k3.geojson")
    monkeypatch.setattr(sva, "PROJECT_ROOT", tmp_path)
    monkeypatch.setitem(sva.STRIDE_CELLS, "g9_test", ("out", 0, 0, 0.0))

    gdf = sva.load_stride_union("g9_test", union_name="union_k3.geojson",
                                verify_dir="verify_k3")
    assert list(gdf["mound_probability"]) == [0.9, 0.95]
    prov = gdf.attrs["verifier_probabilities"]
    assert prov["dir"] == "out/verifier/g9_test/verify_k3_repaired"

    monkeypatch.setenv(POLICY_ENV, "fixed")
    gdf = sva.load_stride_union("g9_test", union_name="union_k3.geojson",
                                verify_dir="verify_k3")
    assert list(gdf["mound_probability"]) == [0.9, 0.05]
    assert gdf.attrs["verifier_probabilities"]["dir"] == "out/verifier/g9_test/verify_k3"


def test_stride_origin_loader_keeps_the_record(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import stride_verifier_analysis as sva

    _cell(tmp_path / "out" / "verifier" / "g9_test", "verify", "union_k10.geojson")
    monkeypatch.setattr(sva, "PROJECT_ROOT", tmp_path)
    monkeypatch.setitem(sva.STRIDE_CELLS, "g9_test", ("out", 0, 0, 0.0))
    # The gates and the origin step are tested elsewhere; here they are
    # identities that DROP attrs, as a pandas merge may.
    monkeypatch.setattr(sva, "reassign_gate", lambda gdf, _b, _l: gdf)
    monkeypatch.setattr(sva, "load_cell_passes", lambda *_a, **_k: [])

    def _origin(gdf, *_a, **_k):
        out = gdf.copy()
        out.attrs = {}
        return out

    monkeypatch.setattr(sva, "union_on_origin", _origin)
    gdf = sva.load_stride_union_on_origin("g9_test", None)
    assert gdf.attrs["verifier_probabilities"]["dir"] == "out/verifier/g9_test/verify_repaired"


def test_image_loader_reads_the_repaired_copy_and_records_it(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import image_b_analysis as iba

    vroot = _cell(tmp_path / "cell", "verify_swap37", "union_k5.geojson")
    monkeypatch.setattr(iba, "PROJECT_ROOT", tmp_path)

    gdf = iba.load_image_union(vroot, "union_k5.geojson", "verify_swap37")
    assert list(gdf["mound_probability"]) == [0.9, 0.95]
    assert gdf.attrs["verifier_probabilities"]["dir"] == "cell/verify_swap37_repaired"

    # A per-call policy wins over the environment (the anchor gate's form).
    gdf = iba.load_image_union(vroot, "union_k5.geojson", "verify_swap37", policy="fixed")
    assert list(gdf["mound_probability"]) == [0.9, 0.05]
    assert gdf.attrs["verifier_probabilities"]["dir"] == "cell/verify_swap37"

    # A name already ending in ``_repaired`` is read as named, under both.
    monkeypatch.setenv(POLICY_ENV, "fixed")
    gdf = iba.load_image_union(vroot, "union_k5.geojson", "verify_swap37_repaired")
    assert list(gdf["mound_probability"]) == [0.9, 0.95]


# --------------------------------------------------------------------------- #
# The anchor gate reads fixed; the bridge's replicate-1 legs resolve.
# --------------------------------------------------------------------------- #


def test_six_cell_gate_reads_its_originals_fixed(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import image_b_analysis as iba
    from scripts import modality_bridge_anchors as mba

    assert mba.GATE_POLICY == "fixed"
    seen: list[str | None] = []

    class _Stop(Exception):
        pass

    def _spy(_vroot, _union, _vdir, policy=None):
        seen.append(policy)
        raise _Stop

    monkeypatch.setattr(iba, "load_image_union", _spy)
    with pytest.raises(_Stop):
        mba.score_cell(Path("x"), "union_k10.geojson", "verify", 10, "g3-text")
    assert seen == ["fixed"]


def test_bridge_replicate_one_resolves_to_the_repaired_copy(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import image_b_analysis as iba
    from scripts import lib_cluster_origins as lco
    from scripts import modality_bridge_floors as fl
    from scripts import modality_bridge_verifier_sd as vsd
    from scripts import stride_verifier_analysis as sva

    # The three Run B legs name replicate 1 by its fixed name.
    for name in ("g3-text", "g3-image", "g3-text-temp1"):
        assert fl.ARMS[name].legs == (("g3v", "verify_g3"),)

    arm = fl.Arm("g3-text", "detect_brief-text", 10, (("g3v", "verify_g3"),))
    _cell(tmp_path / "g3-text" / "verifier" / arm.cell, "verify_g3", arm.union_name)
    monkeypatch.setattr(fl, "ARMS", {"g3-text": arm})
    monkeypatch.setattr(fl, "OUTPUTS", tmp_path)
    monkeypatch.setitem(fl._G, "bounds", None)
    monkeypatch.setattr(iba, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(sva, "reassign_gate", lambda gdf, _b, _l: gdf.copy())
    # The origin step (D65 (6) restatement) needs the arm's passes and a
    # frame; this test pins only which directory is read, so it is a pass-
    # through here (tests/test_modality_bridge_origin.py pins the step).
    monkeypatch.setattr(fl, "load_passes", lambda *_a: [])
    monkeypatch.setattr(lco, "union_on_origin", lambda gdf, *_a, **_k: gdf)

    unions, prov, failures = vsd.load_replicates((1,))
    assert failures == []
    assert list(unions[("g3-text", "g3v", 1)]["mound_probability"]) == [0.9, 0.95]
    rec = prov["g3-text/g3v/rep1"]
    assert rec["dir"] == "g3-text/verifier/detect_brief-text/verify_g3_repaired"
    assert rec["n"] == 2

    monkeypatch.setenv(POLICY_ENV, "fixed")
    _unions, prov, _failures = vsd.load_replicates((1,))
    assert prov["g3-text/g3v/rep1"]["dir"] == "g3-text/verifier/detect_brief-text/verify_g3"


def test_temperature_probe_reads_each_leg_under_the_rule(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import temperature_probe_2026_10_07 as tp

    _write_probs(tmp_path / "g37-t0a", BASE)
    _write_probs(tmp_path / "g37-t0a_repaired", REPAIRED)
    prov: dict = {}
    assert tp._leg_probs(tmp_path, "g37-t0a", prov)["candidate_00001"] == 0.95
    assert prov["g37-t0a"]["dir"].endswith("g37-t0a_repaired")
    monkeypatch.setenv(POLICY_ENV, "fixed")
    assert tp._leg_probs(tmp_path, "g37-t0a", prov)["candidate_00001"] == 0.05
