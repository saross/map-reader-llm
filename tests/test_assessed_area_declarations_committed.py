"""
Tier-2 checks of the committed assessed-area declarations (PI ruling D57 (3)).

``inputs/provenance/assessed-area-declarations.json`` declares, for legacy
artefacts that recorded too little, the tiling of the four T 0.7 pv-diag-384
ladders' March 2026 passes (``pass_tilings``) and the pass lists of the
thirteen pv-diag-384 ladders' K = 5 and K = 10 consensus pools
(``declarations[].pass_provenance``). The evidence for each was assembled
by ``reports/d51-ladder-provenance-2026-10-08-scripts/`` (``t07_tilings.py``,
``rebuild_pools.py``). These tests re-check, against the committed data:

* every declared pass file still has its declared git blob hash, its
  ``processed_tiles`` lie inside the declared manifest, and its
  ``.tiles.json`` attempted (completed ∪ failed) exactly that manifest;
* every declared pool resolves through the library as ``declared``, with
  every candidate inside its area;
* every declaration is pinned (Astra's review of 2026-10-09, P2): a pool's
  ``pool_git_blob_hash`` is the blob committed at ``HEAD``, and each entry
  pins every file its area is read from, at the hash committed at ``HEAD``;
* the four T 0.7 ladders' gate verdicts: MINIMAL image T 0.7 is refused
  (its K = 1 pass skipped ``K-35-053-3_Elenovo_x1344_y672.png``, as its
  T 1.0 sibling's did), and the other three assessed the same area.

Tier 2: reads about 120 committed pass GeoJSONs (tens of MB) and runs the
D51 gate on real tilings.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import lib_assessed_area as laa  # noqa: E402
from scripts.lib_content_anchor import git_blob_hash  # noqa: E402

pytestmark = pytest.mark.tier2

DECLARATIONS = json.loads(laa.DECLARATIONS_PATH.read_text(encoding="utf-8"))
BOARD = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
PV = "outputs/h11/pv-diag-384"
T07_CELLS = {
    "flash-minimal-text-n30-t07/text-t0.7": ("consensus-n10", True),
    "flash-high-text-n5/text-t0.7": ("consensus-n10", True),
    "image-n5/image-t0.7": ("consensus", False),
    "flash-high-image-n5/image-t0.7": ("consensus", True),
}


@pytest.fixture(autouse=True)
def _fresh_caches():
    """Read the committed declarations, not a test's temporary file."""
    laa.clear_declaration_caches()
    yield
    laa.clear_declaration_caches()


@pytest.mark.parametrize(
    "entry", DECLARATIONS.get("pass_tilings", []), ids=lambda e: e.get("label", "?"))
def test_declared_tilings_still_hold(entry):
    """Blob, processed tiles and attempted tiles agree with the declared manifest."""
    assert entry["schema"] == laa.PASS_TILING_SCHEMA
    assert entry["manifest"] in laa.KNOWN_TILINGS
    manifest = set(json.loads((PROJECT_ROOT / entry["manifest"]).read_text()))
    for item in entry["passes"]:
        path = PROJECT_ROOT / item["path"]
        assert git_blob_hash(path) == item["git_blob_hash"], item["path"]
        processed = set(json.loads(path.read_text())["processed_tiles"])
        assert processed <= manifest, item["path"]
        tiles = json.loads(path.with_name(path.name.replace(".geojson", ".tiles.json"))
                           .read_text())
        assert set(tiles["completed"]) | set(tiles["failed"]) == manifest, item["path"]


POOLS = [d for d in DECLARATIONS["declarations"] if d.get("pass_provenance")]


@pytest.mark.parametrize("entry", POOLS, ids=lambda e: e["pool"].split("pv-diag-384/")[-1])
def test_declared_pools_resolve(entry):
    """Each declared pool is determinable, declared, and holds its candidates."""
    area = laa.determine_assessed_area(entry["pool"], label=entry["pool"])
    assert area.method == laa.METHOD_DECLARED, area.reason
    assert not area.warnings


def _head_blob(path: str) -> str:
    """The blob committed at HEAD for a repository path (``git rev-parse``)."""
    return subprocess.run(["git", "-C", str(PROJECT_ROOT), "rev-parse", f"HEAD:{path}"],
                          capture_output=True, text=True, check=True).stdout.strip()


@pytest.mark.parametrize("entry", DECLARATIONS["declarations"] + DECLARATIONS["pass_tilings"],
                         ids=lambda e: (e.get("pool") or e.get("label", "?"))
                         .split("pv-diag-384/")[-1])
def test_every_declaration_is_pinned_to_committed_bytes(entry):
    """The consensus and every input are pinned, and pinned to what HEAD holds."""
    if entry.get("schema") != laa.PASS_TILING_SCHEMA:
        assert entry[laa.POOL_HASH_KEY] == _head_blob(entry["pool"]) \
            == git_blob_hash(PROJECT_ROOT / entry["pool"])
    pinned = {item["path"]: item["git_blob_hash"] for item in entry[laa.INPUTS_KEY]}
    assert set(laa.declaration_inputs(entry)) <= set(pinned)
    for path, digest in pinned.items():
        assert digest == _head_blob(path) == git_blob_hash(PROJECT_ROOT / path), path
    assert laa.check_declaration_pins(entry, "test") == len(pinned)


def test_there_are_twenty_six_declared_pools_and_four_tilings():
    """Thirteen ladders x (K = 5, K = 10); four T 0.7 cells x runs 1-10."""
    assert len(POOLS) == 26
    assert len(DECLARATIONS["pass_tilings"]) == 4
    assert sum(len(t["passes"]) for t in DECLARATIONS["pass_tilings"]) == 40


@pytest.mark.parametrize("cell", sorted(T07_CELLS))
def test_t07_ladder_gate_verdicts(cell):
    """MINIMAL image T 0.7 is refused like its T 1.0 sibling; the rest agree."""
    k10_dir, same = T07_CELLS[cell]
    pools = {1: "consensus-n1", 3: "consensus-n3", 5: "consensus-n5", 10: k10_dir}
    areas = [laa.determine_assessed_area(f"{PV}/{cell}/{d}/consensus_t1.geojson",
                                         label=f"K = {k}") for k, d in pools.items()]
    assert all(a.determined for a in areas), [a.reason for a in areas]
    if same:
        assert laa.compare_assessed_areas(areas, frame=BOARD).status == laa.STATUS_SAME
    else:
        with pytest.raises(laa.AssessedAreaMismatchError) as caught:
            laa.compare_assessed_areas(areas, frame=BOARD)
        pools_rec = {p["label"]: p for p in caught.value.comparison["pools"]}
        assert pools_rec["K = 1"]["excess_over_common_km2"] == 0.0
        assert all(pools_rec[f"K = {k}"]["excess_over_common_km2"] > 1.0
                   for k in (3, 5, 10))
