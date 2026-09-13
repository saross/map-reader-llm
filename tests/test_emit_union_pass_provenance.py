"""
Contract tests for ``scripts/emit_union_pass_provenance.py``.

The sidecar exists because no single 55-map union builder satisfies both
text-arm comparability and the campaign card's ``pass_provenance``
requirement (`reports/gemini37-image-55map-deltas-2026-09-13.md` section 7,
blocker B2). These tests pin the two properties that make the sidecar
trustworthy: it describes **every** file the union builder resolved —
recovery fragments included, which is exactly what the ``merge_passes``
defect fixed in ``75d7c8d4c`` used to drop — and it anchors each one by
content hash, not by path alone.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.emit_union_pass_provenance import (
    PASS_PROVENANCE_SCHEMA,
    ProvenanceError,
    build_sidecar,
    sidecar_path,
)
from scripts.lib_content_anchor import git_blob_hash

pytestmark = pytest.mark.tier1


def _write_pass(cell_dir: Path, run: str, payload: str) -> Path:
    """Materialise one pass fragment with a single detections file."""
    d = cell_dir / run
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"detections-{run}.geojson"
    p.write_text(payload)
    return p


def _fixture(tmp_path: Path, k: int, *, with_fragment: bool = True) -> Path:
    """A campaign root with ``k`` passes, a recovery fragment, and a union."""
    root = tmp_path / "outputs" / "campaign"
    cell = "g384_ov192_55map_g37img"
    cell_dir = root / cell
    for i in range(1, k + 1):
        _write_pass(cell_dir, f"run_{i}", f'{{"pass": {i}}}')
    if with_fragment:
        _write_pass(cell_dir, "run_1_recovery_rd1", '{"pass": 1, "frag": 1}')
    union = root / "verifier" / cell / f"union_k{k}.geojson"
    union.parent.mkdir(parents=True, exist_ok=True)
    union.write_text(json.dumps({"type": "FeatureCollection", "features": [1, 2]}))
    return root


def test_sidecar_path_sits_beside_the_union() -> None:
    """The sidecar takes the union's stem so the pair sorts together."""
    assert (
        sidecar_path(Path("/x/verifier/cell/union_k3.geojson")).name
        == "union_k3_pass_provenance.json"
    )


def test_every_resolved_file_is_recorded_and_content_anchored(
    tmp_path: Path,
) -> None:
    """K = 2 with one recovery fragment yields three content-keyed entries."""
    root = _fixture(tmp_path, k=2)
    record, dest = build_sidecar(root, "g384_ov192_55map_g37img", 2)

    assert record["pass_provenance_schema"] == PASS_PROVENANCE_SCHEMA
    assert record["total_passes"] == 2
    assert record["pass_ids"] == ["run_1", "run_2"]
    assert record["union_feature_count"] == 2
    assert dest.name == "union_k2_pass_provenance.json"

    entries = record["pass_provenance"]
    assert len(entries) == 3, "run_1 main + run_1 fragment + run_2 main"
    assert [e["pass_id"] for e in entries] == ["run_1", "run_1", "run_2"]
    for entry in entries:
        on_disk = Path(entry["path"])
        assert on_disk.is_file()
        assert entry["git_blob_hash"] == git_blob_hash(on_disk)


def test_the_hash_moves_when_the_bytes_move(tmp_path: Path) -> None:
    """A rewritten pass file changes its anchor — the point of hashing."""
    root = _fixture(tmp_path, k=1)
    before, _ = build_sidecar(root, "g384_ov192_55map_g37img", 1)
    frag = root / "g384_ov192_55map_g37img" / "run_1_recovery_rd1"
    next(frag.glob("detections-*.geojson")).write_text('{"pass": 1, "frag": 2}')
    after, _ = build_sidecar(root, "g384_ov192_55map_g37img", 1)
    assert [e["git_blob_hash"] for e in before["pass_provenance"]] != [
        e["git_blob_hash"] for e in after["pass_provenance"]
    ]


def test_first_n_rule_ignores_passes_above_k(tmp_path: Path) -> None:
    """A K = 1 sidecar records run_1 only, though run_2 and run_3 exist."""
    root = _fixture(tmp_path, k=3)
    union = root / "verifier" / "g384_ov192_55map_g37img" / "union_k1.geojson"
    union.write_text(json.dumps({"type": "FeatureCollection", "features": [1]}))
    record, _ = build_sidecar(root, "g384_ov192_55map_g37img", 1)
    assert record["pass_ids"] == ["run_1"]
    assert {e["pass_id"] for e in record["pass_provenance"]} == {"run_1"}


def test_a_missing_union_is_a_gate_not_a_sidecar(tmp_path: Path) -> None:
    """The sidecar must describe an artefact that exists."""
    root = _fixture(tmp_path, k=1)
    (root / "verifier" / "g384_ov192_55map_g37img" / "union_k1.geojson").unlink()
    with pytest.raises(ProvenanceError, match="no union at"):
        build_sidecar(root, "g384_ov192_55map_g37img", 1)


def test_a_missing_pass_is_a_gate(tmp_path: Path) -> None:
    """K = 3 against a two-pass pool must fail, not silently record two."""
    root = _fixture(tmp_path, k=2)
    union = root / "verifier" / "g384_ov192_55map_g37img" / "union_k3.geojson"
    union.write_text(json.dumps({"type": "FeatureCollection", "features": []}))
    with pytest.raises((ProvenanceError, FileNotFoundError)):
        build_sidecar(root, "g384_ov192_55map_g37img", 3)


def test_k_below_one_is_rejected(tmp_path: Path) -> None:
    """A first-N union needs at least one pass."""
    root = _fixture(tmp_path, k=1)
    with pytest.raises(ProvenanceError, match="at least 1"):
        build_sidecar(root, "g384_ov192_55map_g37img", 0)
