"""Tests for scripts/k_ladder_clipped_cells.py and the two options it relies on.

Added 2026-10-30 (Session 166) with the driver, which writes D51-clipped
per-tile evaluations for tier E and the six Gemini 3 Phase 2 ladders so that
``scripts/k_ladder_mcc_test.py`` and ``scripts/k_ladder_mcb.py`` can test
tile-MCC on PI ruling D51's clipped basis.

The driver reimplements neither the clip nor the scorer, so these tests target
what it does own:

* the verbatim writer — kept features are the source's own feature dicts, in
  order; a rung the clip leaves whole is a byte copy; a reading that does not
  line up with the raw file refuses;
* the recorded-recipe replay — every key replayed, only detections, output
  and label replaced, and an unknown or multi-set recipe refused;
* the gates — the expected seven clipped Phase 2 ladders, the committed area
  record, the 4 dp F1 rule, and the evaluation gate;
* the contracts with the two instruments — the analysis id the MCB registry
  names is the one ``k_ladder_mcc_test.write_analysis_row`` writes, the MCC
  test resolves its rungs through ``--conditions``, and the MCB driver's
  ``--registry`` replaces the committed registry.

A red sentinel was run on 2026-10-30 against a real-file copy (record:
``reports/s166-agent-records/clipped-tile-mcc.md`` § 2).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from shapely.geometry import box

import scripts.k_ladder_clipped_cells as kcc
import scripts.k_ladder_mcb as mcb
import scripts.k_ladder_mcc_test as kmt

pytestmark = pytest.mark.tier1

BASE = Path(__file__).resolve().parent.parent


# --- Fixtures -------------------------------------------------------------------


def _geojson(path: Path, points: list[tuple[float, float]]) -> Path:
    """Write a small UTM 35N point GeoJSON with per-feature properties.

    Args:
        path: Where to write it.
        points: ``(x, y)`` coordinates in EPSG:32635.

    Returns:
        ``path``.
    """
    features = [{"type": "Feature",
                 "properties": {"id": i, "source_tile": f"tile_{i}.png",
                                "source_tiles": f"tile_{i}.png", "prob": 0.5 + i / 100},
                 "geometry": {"type": "Point", "coordinates": [x, y]}}
                for i, (x, y) in enumerate(points)]
    payload = {"type": "FeatureCollection", "name": "fixture",
               "crs": {"type": "name",
                       "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}},
               "features": features}
    path.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    return path


POINTS = [(500_000.0, 4_700_000.0), (500_100.0, 4_700_000.0),
          (510_000.0, 4_700_000.0), (500_050.0, 4_700_050.0)]


# --- The verbatim writer --------------------------------------------------------


def test_clip_keeps_the_source_features_verbatim_and_in_order(tmp_path: Path) -> None:
    source = _geojson(tmp_path / "det.geojson", POINTS)
    area = box(499_000, 4_699_000, 501_000, 4_701_000)  # excludes the third point
    record = kcc.clip_geojson_verbatim(source, tmp_path / "out.geojson", area)
    written = json.loads((tmp_path / "out.geojson").read_text())
    original = json.loads(source.read_text())
    assert record["n_removed"] == 1 and record["n_kept"] == 3
    assert record["byte_copy"] is False
    assert written["features"] == [original["features"][i] for i in (0, 1, 3)]
    assert written["crs"] == original["crs"] and written["name"] == original["name"]


def test_a_rung_the_clip_leaves_whole_is_a_byte_copy(tmp_path: Path) -> None:
    source = _geojson(tmp_path / "det.geojson", POINTS)
    area = box(490_000, 4_690_000, 520_000, 4_710_000)
    record = kcc.clip_geojson_verbatim(source, tmp_path / "out.geojson", area)
    assert record["n_removed"] == 0 and record["byte_copy"] is True
    digest = hashlib.sha256((tmp_path / "out.geojson").read_bytes()).hexdigest()
    assert digest == record["source_sha256"] == record["target_sha256"]


def test_clip_refuses_a_reading_that_does_not_match_the_raw_file(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _geojson(tmp_path / "det.geojson", POINTS)
    real = kcc.gpd.read_file
    monkeypatch.setattr(kcc.gpd, "read_file", lambda p: real(p).iloc[:-1])
    with pytest.raises(kcc.GateError, match="geopandas read 3"):
        kcc.clip_geojson_verbatim(source, tmp_path / "out.geojson", box(0, 0, 1, 1))


def test_clip_refuses_a_feature_order_it_cannot_map(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _geojson(tmp_path / "det.geojson", POINTS)
    real = kcc.gpd.read_file
    monkeypatch.setattr(kcc.gpd, "read_file",
                        lambda p: real(p).iloc[::-1].reset_index(drop=True))
    with pytest.raises(kcc.GateError, match="cannot be applied verbatim"):
        kcc.clip_geojson_verbatim(source, tmp_path / "out.geojson", box(0, 0, 1, 1))


# --- The recorded recipe --------------------------------------------------------


RECIPE: dict[str, Any] = {
    "detections": ["results/x/materialised/a.geojson"], "detections_dir": None,
    "batch": None, "glob": None, "buffers": [5, 20, 50],
    "ground_truth": "inputs/vectors/references/mounds-reference.geojson",
    "bounds": kcc.BOARD_BOUNDS, "bootstrap": 10000, "seed": 42,
    "output_dir": "results/x/cells/a", "label": "a", "mcc": True,
    "tile_join": "id", "require_clean_inputs": False, "workers": 1,
}


def test_recipe_replays_every_key_and_replaces_only_three() -> None:
    argv = kcc.recipe_argv(RECIPE, detections="OUT/a-d51clip.geojson",
                           output_dir="OUT/cells/a-d51clip", label="a-d51clip")
    assert argv == ["--detections", "OUT/a-d51clip.geojson",
                    "--buffers", "5", "20", "50",
                    "--ground-truth", RECIPE["ground_truth"], "--bounds", kcc.BOARD_BOUNDS,
                    "--bootstrap", "10000", "--seed", "42",
                    "--output-dir", "OUT/cells/a-d51clip", "--label", "a-d51clip",
                    "--mcc", "--tile-join", "id", "--workers", "1"]


def test_recipe_omits_a_tile_join_the_cell_did_not_record() -> None:
    argv = kcc.recipe_argv({**RECIPE, "tile_join": None}, detections="d",
                           output_dir="o", label="l")
    assert "--tile-join" not in argv


@pytest.mark.parametrize("change, message", [
    ({"surprise": 1}, "unknown recipe keys"),
    ({"detections_dir": "outputs/x"}, "not a single set"),
    ({"detections": ["a.geojson", "b.geojson"]}, "names 2 detection files"),
    ({"bootstrap": None}, "records no 'bootstrap'"),
])
def test_recipe_refuses_what_it_cannot_replay(change: dict, message: str) -> None:
    with pytest.raises(kcc.GateError, match=message):
        kcc.recipe_argv({**RECIPE, **change}, detections="d", output_dir="o", label="l")


# --- The gates ------------------------------------------------------------------


def test_the_expected_seven_clip_and_nothing_else_does() -> None:
    statuses = {pool: kcc.STATUS_CLIPPED for pool in kcc.EXPECTED_CLIPPED_PHASE2}
    statuses["scale-4-optimal-487"] = kcc.STATUS_SAME
    assert kcc.check_clip_set(statuses) == []


def test_a_ladder_that_fails_to_clip_refuses() -> None:
    statuses = {pool: kcc.STATUS_CLIPPED for pool in kcc.EXPECTED_CLIPPED_PHASE2}
    statuses["image-n5-image-t0.7"] = kcc.STATUS_SAME
    assert any("n = 6" in p for p in kcc.check_clip_set(statuses))


def test_an_undetermined_ladder_refuses_even_when_the_clip_set_is_right() -> None:
    statuses = {pool: kcc.STATUS_CLIPPED for pool in kcc.EXPECTED_CLIPPED_PHASE2}
    statuses["scale-4-optimal-487"] = "undetermined"
    assert any("neither clipped nor" in p for p in kcc.check_clip_set(statuses))


def _record(common: float = 1400.3248, source: str = "pool/k1") -> dict[str, Any]:
    return {"common_area_km2": common, "max_excess_km2": 2.0819,
            "frame_area_km2": 1402.4067,
            "pools": [{"label": "K = 1", "source": source,
                       "effective_area_km2": 1400.3248, "excess_over_common_km2": 0.0}]}


def test_the_area_record_must_equal_the_committed_one() -> None:
    assert kcc.check_against_record("L", _record(), _record()) == []
    assert kcc.check_against_record("L", _record(common=1400.33), _record())
    assert kcc.check_against_record("L", _record(source="pool/other"), _record())


def test_f1_agrees_to_four_places_only_within_half_a_unit() -> None:
    assert kcc.same_4dp(0.86036, 0.8604)
    assert not kcc.same_4dp(0.86034, 0.8604)
    assert not kcc.same_4dp(None, 0.8604)


def _evaluation(path: Path, *, f1: float, n_det: int, detections: str,
                tile: bool = True) -> Path:
    summary: dict[str, Any] = {"n_detections": n_det,
                               "buffers": [{"buffer_metres": 20, "f1": f1}]}
    if tile:
        summary["tile_classification"] = {"confusion": {"tp": 1, "tn": 1, "fp": 0,
                                                        "fn": 0}, "mcc": {"point": 1.0}}
    path.mkdir(parents=True, exist_ok=True)
    (path / "evaluation.json").write_text(json.dumps({
        "summary": summary, "_metadata": {"cli_args": {"detections": [detections]}}}))
    return path / "evaluation.json"


def _gate_rung(tmp_path: Path, **kwargs: Any) -> dict[str, Any]:
    eval_path = _evaluation(tmp_path / "cell", **kwargs)
    return {"condition_id": "run::a-d51clip", "clipped_eval_path": str(eval_path),
            "committed_clipped_f1_20": 0.8604, "clip": {"n_kept": 453},
            "clipped_detections": "OUT/a-d51clip.geojson"}


def test_evaluation_gate_passes_a_faithful_cell(tmp_path: Path) -> None:
    rung = _gate_rung(tmp_path, f1=0.8604, n_det=453, detections="OUT/a-d51clip.geojson")
    assert kcc.evaluation_gate(rung)["passed"] is True


@pytest.mark.parametrize("kwargs, message", [
    ({"f1": 0.8605, "n_det": 453, "detections": "OUT/a-d51clip.geojson"}, "F1@20"),
    ({"f1": 0.8604, "n_det": 482, "detections": "OUT/a-d51clip.geojson"}, "n_detections"),
    ({"f1": 0.8604, "n_det": 453, "detections": "OUT/a.geojson"}, "evaluation scored"),
    ({"f1": 0.8604, "n_det": 453, "detections": "OUT/a-d51clip.geojson", "tile": False},
     "tile_classification"),
])
def test_evaluation_gate_refuses_a_drifted_cell(tmp_path: Path, kwargs: dict,
                                                message: str) -> None:
    gate = kcc.evaluation_gate(_gate_rung(tmp_path, **kwargs))
    assert gate["passed"] is False
    assert any(message in p for p in gate["problems"])


def test_phase2_rungs_refuse_a_point_not_on_the_clipped_basis() -> None:
    ladder = {"family": "F", "rungs": [{"K": 1, "labels": {"opmax": "a"},
                                        "opmax": {"score_basis": "as-evaluated"}}]}
    with pytest.raises(kcc.GateError, match="not on the clipped basis"):
        kcc.phase2_rungs(ladder)


def test_pairs_are_oriented_higher_k_minus_lower_k() -> None:
    tiering = {"pairwise": [{"ref_a": "r::k1", "ref_b": "r::k10", "observed_diff": -0.03,
                             "p_value": 0.01, "bh_adjusted_p": 0.02, "significant": True}],
               "mcc_permutation": {"pairwise": [
                   {"ref_a": "r::k10", "ref_b": "r::k1", "observed_mcc_diff": -0.02,
                    "p_value": 0.5, "bh_adjusted_p": 0.6, "significant": False}]}}
    k_of = {"r::k1": 1, "r::k10": 10}
    assert kcc._pair(tiering, "f1", k_of, 1, 10)["delta"] == pytest.approx(0.03)
    assert kcc._pair(tiering, "mcc", k_of, 1, 10)["delta"] == pytest.approx(-0.02)
    assert kcc.direction(-0.0238) == "down" and kcc.direction(0.003) == "flat"


# --- The committed inputs the driver gates against -------------------------------


def test_the_expected_clip_set_is_the_committed_one() -> None:
    ladders = kcc.load(kcc.PHASE2_LADDERS)["ladders"]
    clipped = {L["proposer_pool"] for L in ladders
               if L["assessed_area"]["status"] == kcc.STATUS_CLIPPED}
    assert clipped == kcc.EXPECTED_CLIPPED_PHASE2
    assert set(kcc.TARGET_PHASE2_POOLS) == clipped - {kcc.G37_POOL}


def test_tier_e_pools_are_the_committed_gates_pools() -> None:
    committed = kcc.load(kcc.TIER_E_CLIPPED)["tier_e"]["assessed_area"]["pools"]
    assert kcc.tier_e_pools() == {p["label"]: p["source"] for p in committed}


def test_tier_e_rungs_carry_the_committed_clipped_values() -> None:
    rungs = kcc.tier_e_rungs()
    assert [r["K"] for r in rungs] == [1, 3, 5, 10]
    assert [r["committed_clipped_f1_20"] for r in rungs] == [0.8604, 0.8902, 0.8968, 0.8942]
    assert [r["committed_n_removed"] for r in rungs] == [29, 29, 27, 0]
    assert round(rungs[0]["committed_full_precision_f1"], 6) == 0.86036


# --- The contracts with the two instruments ---------------------------------------


def test_registry_names_the_analysis_id_the_mcc_test_writes(tmp_path: Path) -> None:
    ladder = {"slug": "d51clip-x", "family": "X", "run_id": "run",
              "rungs": [{"K": 1, "clipped_label": "a-d51clip"}]}
    entry = kcc.mcb_registry([ladder], tmp_path)[0]
    inventory = {"family_base": "X", "reference_file": "r.geojson",
                 "headline_buffer_m": 20}
    _path, analysis_id = kmt.write_analysis_row(
        tmp_path, "d51clip-x", inventory, [{"condition_id": "run::a-d51clip"}])
    assert entry["analysis_id"] == analysis_id
    assert entry["k_by_label"] == {"a-d51clip": 1}


def _stop(*_args: Any, **_kwargs: Any) -> None:
    raise RuntimeError("stopped")


def test_mcc_test_resolves_rungs_through_the_named_conditions(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inventory = tmp_path / "ladders.json"
    inventory.write_text(json.dumps({"ladders": [{
        "slug": "d51clip-x", "family_base": "X", "reference_file": "r.geojson",
        "headline_buffer_m": 20, "corpus": "4-map-gs",
        "rungs": [{"K": 1, "condition_id": "run::a", "eval_path": "e", "f1_headline": 0.8},
                  {"K": 3, "condition_id": "run::b", "eval_path": "e", "f1_headline": 0.9}],
    }]}))
    seen: dict[str, Any] = {}

    def capture(analyses: Path, conditions: Path, *_args: Any) -> None:
        seen["conditions"] = conditions
        raise RuntimeError("stopped")

    monkeypatch.setattr(kmt, "run_tiering", capture)
    for extra, expected in (([], kmt.RUN_CONDITIONS),
                            (["--conditions", str(tmp_path / "side.json")],
                             tmp_path / "side.json")):
        monkeypatch.setattr("sys.argv", ["k_ladder_mcc_test.py", "--ladders", str(inventory),
                                         "--output-dir", str(tmp_path / "out"), *extra])
        with pytest.raises(RuntimeError, match="stopped"):
            kmt.main()
        assert seen["conditions"] == expected


def _registry_file(tmp_path: Path, **override: Any) -> Path:
    entry = {"slug": "d51clip-x", "analysis_id": "k-ladder-mcc-d51clip-x-2026-09-12",
             "analyses": "a.json", "conditions": "c.json", "bounds": kcc.BOARD_BOUNDS,
             "buffer_m": 20, "tiering": "t.json", "group": "D51 clipped",
             "family": "X (D51 clipped)", "k_by_label": {"a-d51clip": 1, "b-d51clip": 3}}
    entry.update(override)
    path = tmp_path / "registry.json"
    path.write_text(json.dumps([entry]))
    return path


def test_mcb_registry_file_is_read_whole(tmp_path: Path) -> None:
    entries, k_of, names = mcb.load_registry(_registry_file(tmp_path))
    assert [e["slug"] for e in entries] == ["d51clip-x"]
    assert entries[0]["conditions"] == Path("c.json") and entries[0]["buffer_m"] == 20
    assert k_of == {"a-d51clip": 1, "b-d51clip": 3}
    assert names == {"d51clip-x": "X (D51 clipped)"}


def test_mcb_registry_refuses_an_incomplete_entry(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps([{"slug": "x"}]))
    with pytest.raises(ValueError, match="lacks"):
        mcb.load_registry(path)


def test_mcb_main_runs_the_registry_it_is_given(tmp_path: Path,
                                                monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def capture(entry: dict[str, Any], *_args: Any) -> None:
        seen.append(entry["slug"])
        raise RuntimeError("stopped")

    monkeypatch.setattr(mcb, "committed_ranking", lambda _path: {})
    monkeypatch.setattr(mcb, "run_mcb", capture)
    monkeypatch.setattr("sys.argv", ["k_ladder_mcb.py", "--registry",
                                     str(_registry_file(tmp_path)),
                                     "--output-dir", str(tmp_path / "out")])
    with pytest.raises(RuntimeError, match="stopped"):
        mcb.main()
    assert seen == ["d51clip-x"]


def test_mcb_default_registry_is_unchanged() -> None:
    slugs = [entry["slug"] for entry in mcb.ladder_registry()]
    assert len(slugs) == 22 and slugs[:2] == ["gs-stride-a", "tier-e"]
