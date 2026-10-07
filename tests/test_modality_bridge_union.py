"""
Tests for ``scripts/modality_bridge_union.py`` — Run B Stage 2's union chain.

The module's job is narrow: resolve a batch-layout pass (the merged main file,
never the chunk files, then every recovery round's fragment in numeric round
order) and hand it to the originals' union chain unchanged. The tests pin
the resolver's contract on synthetic layouts, the coverage and overlap gates,
and — end to end — that the same pass files laid out the legacy way and the
batch way build byte-identical unions, so the adapter cannot change a union.

All synthetic; the only committed file read is the small common-footprint
bounds GeoJSON (487 tiles) the chain clips to.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_prepare_scoring import CoverageError  # noqa: E402
from scripts.modality_bridge_union import (  # noqa: E402
    LayoutError,
    OverlapError,
    build_union,
    check_batch_run_dirs,
    compare_union_files,
    gate_passes,
    main,
    overlapping_tiles,
    resolve_batch_pass_paths,
)

pytestmark = pytest.mark.tier1

VERSION = "detect_brief-text"


def _fc(features: list[dict], processed: list[str]) -> dict:
    """A detector-shaped FeatureCollection (UTM 35N, processed_tiles record)."""
    return {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}},
        "processed_tiles": sorted(processed),
        "features": features,
    }


def _point(x: float, y: float, tile: str) -> dict:
    """One detection as a small square polygon around (x, y)."""
    d = 2.0
    ring = [[x - d, y - d], [x + d, y - d], [x + d, y + d], [x - d, y + d], [x - d, y - d]]
    return {"type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {"source_tile": tile, "label": "mound",
                           "subtype": "burial_mound"}}


def _write(path: Path, data: dict | None = None) -> Path:
    """Write a FeatureCollection (empty by default) and return the path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data or _fc([], [])))
    return path


def _main_name(n: int) -> str:
    return f"detections_{VERSION}_run{n:02d}.geojson"


# ---------------------------------------------------------------------------
# The resolver
# ---------------------------------------------------------------------------


def test_main_only(tmp_path: Path) -> None:
    cell = tmp_path / "arm" / VERSION
    main_file = _write(cell / "run_1" / _main_name(1))
    assert resolve_batch_pass_paths(cell, "run_1") == [main_file]


def test_chunk_files_are_excluded(tmp_path: Path) -> None:
    """A chunked pass is read through its merged file only (chunks would double it)."""
    cell = tmp_path / "arm" / VERSION
    main_file = _write(cell / "run_2" / _main_name(2))
    for c in range(3):
        _write(cell / "run_2" / f"detections_{VERSION}_run02_chunk{c}.geojson")
    assert resolve_batch_pass_paths(cell, "run_2") == [main_file]


def test_unmerged_chunked_pass_is_refused(tmp_path: Path) -> None:
    cell = tmp_path / "arm" / VERSION
    for c in range(2):
        _write(cell / "run_3" / f"detections_{VERSION}_run03_chunk{c}.geojson")
    with pytest.raises(LayoutError, match="withheld the merge"):
        resolve_batch_pass_paths(cell, "run_3")


def test_missing_pass_is_refused(tmp_path: Path) -> None:
    cell = tmp_path / "arm" / VERSION
    (cell / "run_1").mkdir(parents=True)
    with pytest.raises(LayoutError, match="has not landed"):
        resolve_batch_pass_paths(cell, "run_1")


def test_wrongly_named_merged_file_is_refused(tmp_path: Path) -> None:
    cell = tmp_path / "arm" / VERSION
    _write(cell / "run_1" / "detections_other-version_run01.geojson")
    with pytest.raises(LayoutError, match="expected exactly one merged file"):
        resolve_batch_pass_paths(cell, "run_1")


def test_every_fragment_folded_in_numeric_round_order(tmp_path: Path) -> None:
    """rd10 comes after rd2 (numeric, not lexicographic, order)."""
    arm = tmp_path / "arm"
    cell = arm / VERSION
    main_file = _write(cell / "run_4" / _main_name(4))
    frags = {r: _write(arm / f"recovery_rd{r}" / VERSION / "run_4" / _main_name(4))
             for r in (10, 1, 2)}
    assert resolve_batch_pass_paths(cell, "run_4") == [
        main_file, frags[1], frags[2], frags[10]]


def test_fragment_chunks_excluded_and_other_runs_ignored(tmp_path: Path) -> None:
    arm = tmp_path / "arm"
    cell = arm / VERSION
    main_file = _write(cell / "run_1" / _main_name(1))
    frag = _write(arm / "recovery_rd1" / VERSION / "run_1" / _main_name(1))
    _write(arm / "recovery_rd1" / VERSION / "run_1"
           / f"detections_{VERSION}_run01_chunk0.geojson")
    # A fragment for another pass must not be folded into this one.
    _write(arm / "recovery_rd1" / VERSION / "run_2" / _main_name(2))
    assert resolve_batch_pass_paths(cell, "run_1") == [main_file, frag]


def test_round_without_this_pass_is_skipped(tmp_path: Path) -> None:
    arm = tmp_path / "arm"
    cell = arm / VERSION
    main_file = _write(cell / "run_1" / _main_name(1))
    (arm / "recovery_rd1" / VERSION / "run_3").mkdir(parents=True)
    # A round directory for this pass that holds no output at all (a lodge
    # that wrote nothing) is skipped; the coverage gate decides.
    (arm / "recovery_rd2" / VERSION / "run_1" / "batch_working").mkdir(parents=True)
    assert resolve_batch_pass_paths(cell, "run_1") == [main_file]


def test_unmerged_chunked_fragment_is_refused(tmp_path: Path) -> None:
    arm = tmp_path / "arm"
    cell = arm / VERSION
    _write(cell / "run_1" / _main_name(1))
    _write(arm / "recovery_rd1" / VERSION / "run_1"
           / f"detections_{VERSION}_run01_chunk0.geojson")
    with pytest.raises(LayoutError, match="withheld the merge"):
        resolve_batch_pass_paths(cell, "run_1")


def test_unrecognised_recovery_directory_is_refused(tmp_path: Path) -> None:
    arm = tmp_path / "arm"
    cell = arm / VERSION
    _write(cell / "run_1" / _main_name(1))
    (arm / "recovery_rd1-old").mkdir(parents=True)
    with pytest.raises(LayoutError, match="unrecognised recovery directory"):
        resolve_batch_pass_paths(cell, "run_1")


def test_bad_run_name_is_refused(tmp_path: Path) -> None:
    with pytest.raises(LayoutError, match="not a pass directory"):
        resolve_batch_pass_paths(tmp_path / "arm" / VERSION, "run_1_recovery")


def test_stage2_siblings_do_not_disturb_the_resolver(tmp_path: Path) -> None:
    """scoring/, verifier/ and residual files beside the arm's passes are ignored."""
    arm = tmp_path / "arm"
    cell = arm / VERSION
    main_file = _write(cell / "run_1" / _main_name(1))
    (arm / "scoring" / "common").mkdir(parents=True)
    (arm / "verifier" / VERSION).mkdir(parents=True)
    (arm / "residual_run_1.json").write_text("[]")
    assert resolve_batch_pass_paths(cell, "run_1") == [main_file]


# ---------------------------------------------------------------------------
# Run-directory and coverage gates
# ---------------------------------------------------------------------------


def test_run_dirs_must_be_exactly_one_to_k(tmp_path: Path) -> None:
    cell = tmp_path / "arm" / VERSION
    for n in (1, 2, 3):
        (cell / f"run_{n}").mkdir(parents=True)
    check_batch_run_dirs(cell, 3)
    with pytest.raises(LayoutError):
        check_batch_run_dirs(cell, 5)  # passes 4 and 5 never lodged
    (cell / "run_4").mkdir()
    with pytest.raises(LayoutError):
        check_batch_run_dirs(cell, 3)  # an unplanned run_4


def test_overlapping_tiles() -> None:
    assert overlapping_tiles([{"a", "b"}, {"c"}]) == set()
    assert overlapping_tiles([{"a", "b"}, {"b"}, {"b", "c"}]) == {"b"}


def _batch_arm(root: Path, coverage: dict[int, list[list[str]]]) -> Path:
    """Lay out a batch arm: coverage[run] = [main tiles, rd1 tiles, ...]."""
    arm = root / "arm"
    cell = arm / VERSION
    for run, parts in coverage.items():
        for r, tiles in enumerate(parts):
            base = cell if r == 0 else arm / f"recovery_rd{r}" / VERSION
            _write(base / f"run_{run}" / _main_name(run), _fc([], tiles))
    return cell


def test_gate_folds_fragments_to_exact_coverage(tmp_path: Path) -> None:
    manifest = {"t1", "t2", "t3"}
    cell = _batch_arm(tmp_path, {1: [["t1", "t2", "t3"]], 2: [["t1"], ["t2"], ["t3"]]})
    recs = gate_passes(cell, 2, "batch", manifest)
    assert [r["tiles_per_file"] for r in recs] == [[3], [1, 1, 1]]
    assert all(r["processed_tiles"] == 3 for r in recs)


def test_gate_refuses_a_short_pass(tmp_path: Path) -> None:
    cell = _batch_arm(tmp_path, {1: [["t1", "t2"]]})
    with pytest.raises(CoverageError, match="1 missing"):
        gate_passes(cell, 1, "batch", {"t1", "t2", "t3"})


def test_gate_refuses_an_extra_tile(tmp_path: Path) -> None:
    cell = _batch_arm(tmp_path, {1: [["t1", "t2", "t9"]]})
    with pytest.raises(CoverageError, match="1 extra"):
        gate_passes(cell, 1, "batch", {"t1", "t2"})


def test_gate_refuses_overlap(tmp_path: Path) -> None:
    cell = _batch_arm(tmp_path, {1: [["t1", "t2"], ["t2"]]})
    with pytest.raises(OverlapError):
        gate_passes(cell, 1, "batch", {"t1", "t2"})


def test_gate_refuses_a_missing_pass(tmp_path: Path) -> None:
    cell = _batch_arm(tmp_path, {1: [["t1"]], 2: [["t1"]]})
    with pytest.raises(LayoutError):
        gate_passes(cell, 3, "batch", {"t1"})


# ---------------------------------------------------------------------------
# End to end: the adapter cannot change a union
# ---------------------------------------------------------------------------


def _carrier_points(n: int) -> list[tuple[float, float, str]]:
    """Interior points of n carrier tiles of the committed common footprint."""
    from scripts.stride_prepare_and_union import COMMON_BOUNDS

    bounds = gpd.read_file(COMMON_BOUNDS).to_crs("EPSG:32635")
    pts = bounds.geometry.representative_point()
    return [(float(p.x), float(p.y), str(t))
            for p, t in zip(pts[:n], bounds["tile_name"][:n])]


def _passes(k: int) -> list[list[tuple[list[dict], list[str]]]]:
    """K passes over a 4-tile manifest; passes 2 and 3 split across fragments.

    Each pass is a list of (features, processed tiles) parts, main first.
    """
    pts = _carrier_points(4)
    tiles = [p[2] for p in pts]
    passes = []
    for run in range(1, k + 1):
        feats = []
        for j, (x, y, tile) in enumerate(pts):
            if (run + j) % 3 == 0:
                continue  # this pass misses this mound
            feats.append(_point(x + run, y - run, tile))
            if j == 1:
                feats.append(_point(x + run + 5, y - run, tile))  # within-pass dup
        if run in (2, 3):
            # Main misses the last tile; a fragment (two rounds for pass 3)
            # completes it.
            last = tiles[-1]
            main = ([f for f in feats if f["properties"]["source_tile"] != last],
                    tiles[:-1])
            frag = ([f for f in feats if f["properties"]["source_tile"] == last],
                    [last])
            passes.append([main, ([], []), frag] if run == 3 else [main, frag])
        else:
            passes.append([(feats, tiles)])
    return passes


def test_legacy_and_batch_layouts_build_identical_unions(tmp_path: Path) -> None:
    k = 3
    passes = _passes(k)
    tiles = sorted({t for p in passes for _, ts in p for t in ts})
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(tiles))

    legacy = tmp_path / "legacy" / "cell_x"
    arm = tmp_path / "batch" / "arm"
    batch = arm / VERSION
    for run, parts in enumerate(passes, start=1):
        real = [p for p in parts if p[1]]  # legacy has no empty middle round
        _write(legacy / f"run_{run}" / "detections-x.geojson", _fc(*real[0]))
        if len(real) > 1:
            _write(legacy / f"run_{run}_recovery" / "detections-x.geojson",
                   _fc(*real[1]))
        for r, (feats, ts) in enumerate(parts):
            if r == 0:
                _write(batch / f"run_{run}" / _main_name(run), _fc(feats, ts))
            elif ts:
                _write(arm / f"recovery_rd{r}" / VERSION / f"run_{run}" / _main_name(run),
                       _fc(feats, ts))
            else:
                (arm / f"recovery_rd{r}" / VERSION / f"run_{run}").mkdir(parents=True)

    out_l, out_b = tmp_path / "out_l", tmp_path / "out_b"
    rec_l = build_union(legacy, k, "legacy", out_l, manifest, write=True)
    rec_b = build_union(batch, k, "batch", out_b, manifest, write=True)
    assert rec_l["union_features"] == rec_b["union_features"] > 0
    assert rec_b["passes"][2]["tiles_per_file"] == [3, 1]
    u_l = out_l / "verifier" / "cell_x" / f"union_k{k}.geojson"
    u_b = out_b / "verifier" / VERSION / f"union_k{k}.geojson"
    cmp = compare_union_files(u_b, u_l)
    assert cmp["equal"] and cmp["bytes_identical"]
    # The build record lands beside the union, with the pass files' digests.
    rec = json.loads(u_b.with_name(f"union_k{k}.build.json").read_text())
    assert rec["layout"] == "batch" and len(rec["passes"]) == k
    assert all(len(p["file_sha256"]) == len(p["files"]) for p in rec["passes"])


def test_existing_union_is_not_overwritten(tmp_path: Path) -> None:
    passes = _passes(1)
    tiles = sorted({t for p in passes for _, ts in p for t in ts})
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(tiles))
    cell = tmp_path / "arm" / VERSION
    _write(cell / "run_1" / _main_name(1), _fc(*passes[0][0]))
    build_union(cell, 1, "batch", tmp_path / "out", manifest, write=True)
    with pytest.raises(FileExistsError):
        build_union(cell, 1, "batch", tmp_path / "out", manifest, write=True)
    assert main(["--layout", "batch", "--cell-dir", str(cell), "--k", "1",
                 "--out-root", str(tmp_path / "out"), "--manifest", str(manifest),
                 "--write"]) == 1


def test_compare_detects_a_vote_difference(tmp_path: Path) -> None:
    def fc(votes: list[int]) -> dict:
        return {"type": "FeatureCollection", "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [25.0, 42.0]},
             "properties": {"vote_count": v, "source_tile": "t"}} for v in votes]}
    a, b = tmp_path / "a.geojson", tmp_path / "b.geojson"
    a.write_text(json.dumps(fc([1, 2])))
    b.write_text(json.dumps(fc([1, 3])))
    cmp = compare_union_files(a, b)
    assert not cmp["equal"] and cmp["vote_mismatches"] == 1
    b.write_text(json.dumps(fc([1])))
    assert not compare_union_files(a, b)["equal"]


def test_cli_gates_only_writes_nothing(tmp_path: Path) -> None:
    cell = _batch_arm(tmp_path, {1: [["t1", "t2"]]})
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps(["t1", "t2"]))
    out = tmp_path / "out"
    assert main(["--layout", "batch", "--cell-dir", str(cell), "--k", "1",
                 "--out-root", str(out), "--manifest", str(manifest)]) == 0
    assert not out.exists()
    manifest.write_text(json.dumps(["t1", "t2", "t3"]))
    assert main(["--layout", "batch", "--cell-dir", str(cell), "--k", "1",
                 "--out-root", str(out), "--manifest", str(manifest)]) == 1
