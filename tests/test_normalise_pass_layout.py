"""Tests for the cross-mode pass-layout normaliser."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.normalise_pass_layout import (  # noqa: E402
    canonical_stem,
    find_pass_files,
    normalise,
    select_pass_file,
)


def _batch_layout(root: Path) -> Path:
    """Build the directory shape the BATCH path produces."""
    d = root / "detect_brief-text-image" / "run_1"
    d.mkdir(parents=True)
    (d / "detections_detect_brief-text-image_run01.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": []}))
    (d / "detections_detect_brief-text-image_run01.meta.json").write_text("{}")
    (d / "detections_detect_brief-text-image_run01.tiles.json").write_text(
        json.dumps({"total_tiles": 3, "completed": ["a.png"]}))
    # Working files must not be mistaken for outputs.
    w = d / "batch_working"
    w.mkdir()
    (w / "chunk0.jsonl").write_text("{}\n")
    return root


@pytest.mark.tier1
def test_canonical_stem_matches_the_realtime_convention():
    assert canonical_stem("detect_brief-text-image", "gemini-3.7-flash",
                          "2026-09-17") == \
        "detections-detect_brief-text-image-3.7-flash-2026-09-17"


@pytest.mark.tier1
def test_batch_outputs_are_found_by_suffix_not_name(tmp_path):
    """Naming is exactly what differs between modes, so match on suffix."""
    src = _batch_layout(tmp_path)
    found = find_pass_files(src)
    assert set(found) == {".geojson", ".meta.json", ".tiles.json"}
    # The JSONL request files are inputs, not outputs.
    assert all("batch_working" not in p.parts for p in found.values())


@pytest.mark.tier1
def test_normalise_writes_the_realtime_layout(tmp_path):
    src = _batch_layout(tmp_path / "batchout")
    pool = tmp_path / "pool"
    dest = normalise(src, pool, run=4, version="detect_brief-text-image",
                     model="gemini-3.7-flash", date="2026-09-17")
    assert dest == pool / "run_4"
    names = sorted(p.name for p in dest.iterdir())
    assert names == [
        "detections-detect_brief-text-image-3.7-flash-2026-09-17.geojson",
        "detections-detect_brief-text-image-3.7-flash-2026-09-17.meta.json",
        "detections-detect_brief-text-image-3.7-flash-2026-09-17.tiles.json",
    ]
    # Copy by default: the source stays as the producing mode's own record.
    assert (src / "detect_brief-text-image" / "run_1" /
            "detections_detect_brief-text-image_run01.geojson").exists()


@pytest.mark.tier1
def test_normalise_refuses_to_overwrite_an_existing_pass(tmp_path):
    """A committed pass is evidence; clobbering it must be impossible."""
    src = _batch_layout(tmp_path / "batchout")
    pool = tmp_path / "pool"
    normalise(src, pool, 4, "detect_brief-text-image", "gemini-3.7-flash",
              "2026-09-17")
    with pytest.raises(FileExistsError):
        normalise(src, pool, 4, "detect_brief-text-image", "gemini-3.7-flash",
                  "2026-09-17")


@pytest.mark.tier1
def test_dry_run_writes_nothing(tmp_path):
    src = _batch_layout(tmp_path / "batchout")
    pool = tmp_path / "pool"
    normalise(src, pool, 4, "detect_brief-text-image", "gemini-3.7-flash",
              "2026-09-17", dry_run=True)
    assert not pool.exists()


def _chunked_batch_layout(root: Path, n_chunks: int = 7,
                          merged: bool = True) -> Path:
    """The shape a CHUNKED batch run leaves: per-chunk files, plus (usually)
    the merged pass files beside them."""
    d = root / "detect_brief-text-image" / "run_1"
    d.mkdir(parents=True)
    stem = "detections_detect_brief-text-image_run01"
    for i in range(n_chunks):
        (d / f"{stem}_chunk{i}.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": []}))
        (d / f"{stem}_chunk{i}.meta.json").write_text("{}")
        (d / f"{stem}_chunk{i}.tiles.json").write_text(
            json.dumps({"total_tiles": 10, "completed": [f"c{i}.png"]}))
    if merged:
        (d / f"{stem}.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": []}))
        (d / f"{stem}.meta.json").write_text("{}")
        (d / f"{stem}.tiles.json").write_text(json.dumps(
            {"total_tiles": 10 * n_chunks,
             "completed": [f"c{i}.png" for i in range(n_chunks)]}))
    return root


@pytest.mark.tier1
def test_chunked_run_takes_the_merged_file_not_a_chunk(tmp_path):
    """The merged file is the pass; a chunk is one seventh of it.

    Before 2026-09-18 the choice was by sort order and happened to land on
    the merged file only because ``run01.tiles.json`` sorts before
    ``run01_chunk0.tiles.json``. The rule must be explicit.
    """
    src = _chunked_batch_layout(tmp_path)
    found = find_pass_files(src)
    for suffix, path in found.items():
        assert "_chunk" not in path.name, (suffix, path.name)
    tiles = json.loads(found[".tiles.json"].read_text())
    assert len(tiles["completed"]) == 7


@pytest.mark.tier1
def test_chunk_only_layout_is_refused_not_normalised(tmp_path):
    """An unmerged chunked pass must be refused: normalising one chunk
    would put a well-formed file covering a fraction of the corpus into the
    pool, and nothing downstream would notice."""
    src = _chunked_batch_layout(tmp_path, merged=False)
    with pytest.raises(FileNotFoundError, match="not been merged"):
        find_pass_files(src)
    with pytest.raises(FileNotFoundError):
        normalise(src, tmp_path / "pool", 4, "detect_brief-text-image",
                  "gemini-3.7-flash", "2026-09-17")
    assert not (tmp_path / "pool").exists()


@pytest.mark.tier1
def test_ambiguous_layout_is_refused_not_sorted():
    """Two non-chunk candidates: refuse, never resolve by sort order."""
    hits = [Path("a/detections_x_run01.tiles.json"),
            Path("a/detections_x_run02.tiles.json")]
    with pytest.raises(ValueError, match="sort order"):
        select_pass_file(hits, ".tiles.json", Path("a"))


@pytest.mark.tier1
def test_select_pass_file_ignores_chunks_whatever_their_sort_position():
    """Chunk names that would SORT FIRST must still lose to the merged file."""
    hits = sorted([Path("a/_chunk0.tiles.json"),   # sorts before everything
                   Path("a/detections_x_run01_chunk1.tiles.json"),
                   Path("a/detections_x_run01.tiles.json")])
    assert hits[0].name == "_chunk0.tiles.json"
    chosen = select_pass_file(hits, ".tiles.json", Path("a"))
    assert chosen.name == "detections_x_run01.tiles.json"
