"""
Tests for ``merge_passes.resolve_pass_files`` and recovery fragments.

A storm-interrupted proposer pass is completed by re-running its residual
tiles into a sibling ``run_<N>_recovery`` (or ``run_<N>_recovery2``)
directory. The fragment's tiles are disjoint from the main file's: the two
together are ONE pass.

``resolve_pass_files`` parses a pass directory's number with
``int(pass_name.replace("run_", ""))`` (``scripts/merge_passes.py``, the
``try`` block whose ``except ValueError: continue`` sits at line 459), so
``int("2_recovery")`` raises and the fragment is skipped — silently, with no
warning. Two consequences, both tested here:

1. the fragment's detections never reach the union; and
2. a pass whose main directory holds no features at all drops out of
   ``load_pass_detections`` entirely, so ``total_passes`` — and with it every
   ``confidence`` and every vote threshold — is computed over the wrong
   denominator.

The proposed repair is ``reports/recovery-fragment-drop/merge_passes.patch``,
which folds ``run_<N><suffix>`` into pass N. It is **not applied on this
branch**: the fix changes what any rebuilt union contains, which is the
Principal Investigator's call, not an audit fix.

This module is therefore written to be green in BOTH states:

* the characterisation tests assert today's behaviour and are expected to
  FAIL the moment the patch lands — that failure is the signal to invert them
  (each says so in its docstring); and
* the acceptance tests assert the repaired behaviour and skip while the patch
  is absent, detected by the ``_PASS_DIR_RE`` constant the patch introduces.

Evidence for the measured reach of the defect:
``reports/recovery-fragment-drop-2026-09-13.md``.
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import merge_passes
from scripts.merge_passes import load_pass_detections, resolve_pass_files

pytestmark = pytest.mark.tier1

#: True once ``reports/recovery-fragment-drop/merge_passes.patch`` is applied.
#: The patch introduces this module constant as the directory-name matcher, so
#: its presence is a reliable, import-time signal of which behaviour is live.
PATCH_APPLIED = hasattr(merge_passes, "_PASS_DIR_RE")

_PATCH_REASON = (
    "reports/recovery-fragment-drop/merge_passes.patch is not applied on this "
    "branch (the repair is the PI's ruling to make)"
)


def _write_pass(directory: Path, tiles: list[str]) -> Path:
    """Write one pass-shaped detection GeoJSON, one point feature per tile.

    Coordinates are EPSG:32635-shaped metres 1,000 m apart, so every feature
    is its own cluster under the 20 m voting tolerance and the arithmetic of
    the assertions stays obvious.

    Args:
        directory: Pass or recovery directory to create and write into.
        tiles: Source tile names; one feature is written per name. An empty
            list writes a valid but empty FeatureCollection, which is what a
            fully storm-hit pass leaves behind.

    Returns:
        The path of the written GeoJSON.
    """
    directory.mkdir(parents=True, exist_ok=True)
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [400_000.0 + 1_000.0 * i, 4_700_000.0],
            },
            "properties": {"subtype": "mound", "source_tile": tile},
        }
        # The index is taken from the tile name so the same tile lands at the
        # same coordinate in every fragment that reports it.
        for tile, i in ((t, int(t.split("_")[-1])) for t in tiles)
    ]
    path = directory / "detections-brief-text-flash-2026-01-01.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    # A sidecar the resolver must keep ignoring.
    (directory / "detections-brief-text-flash-2026-01-01.meta.json").write_text("{}")
    return path


@pytest.fixture
def storm_pool(tmp_path: Path) -> Path:
    """A three-pass pool shaped like the committed storm-hit campaigns.

    ``run_2`` is partly recovered (one tile in the main file, two in the
    fragment) and ``run_3`` is almost entirely recovered — its main file holds
    a valid but EMPTY FeatureCollection, which is the shape
    ``outputs/gemini37-image-gs-2026-09-01/g384_ov192_g37img/run_3`` has (0
    features against 1,663 in ``run_3_recovery``).

    Returns:
        The pool directory.
    """
    pool = tmp_path / "pool"
    _write_pass(pool / "run_1", ["tile_1", "tile_2"])
    _write_pass(pool / "run_2", ["tile_1"])
    _write_pass(pool / "run_2_recovery", ["tile_2", "tile_3"])
    _write_pass(pool / "run_3", [])
    _write_pass(pool / "run_3_recovery", ["tile_1", "tile_2"])
    _write_pass(pool / "run_3_recovery2", ["tile_3"])
    return pool


class TestDefectCharacterisation:
    """Today's behaviour. These tests FAIL once the patch lands — invert them."""

    def test_recovery_directories_are_not_resolved(self, storm_pool: Path) -> None:
        """No ``run_<N>_recovery`` directory appears in the resolved mapping.

        Invert when the patch lands: the fragments' files should then appear
        under their parent pass id, not as keys of their own.
        """
        resolved = resolve_pass_files(storm_pool)
        assert set(resolved) == {"run_1", "run_2", "run_3"}
        assert not any("recovery" in name for name in resolved)
        # Every pass resolves exactly its own single main file.
        assert [len(files) for _, files in sorted(resolved.items())] == [1, 1, 1]

    def test_recovery_detections_never_reach_the_loader(
        self, storm_pool: Path
    ) -> None:
        """The fragments' features are absent, so pass 2 reports only one.

        Invert when the patch lands: pass 2 should then carry three features
        and pass 3 three.
        """
        loaded = load_pass_detections(storm_pool)
        assert len(loaded["run_2"]) == 1
        tiles = {f["properties"]["source_tile"] for f in loaded["run_2"]}
        assert tiles == {"tile_1"}

    def test_storm_hit_pass_disappears_corrupting_the_denominator(
        self, storm_pool: Path
    ) -> None:
        """``run_3`` vanishes from the loader, so ``total_passes`` reads 2, not 3.

        This is the consequential half of the defect: ``merge_passes`` sets
        ``total_passes = len(raw_passes)``, and ``apply_threshold`` divides
        ``vote_count`` by it to write ``confidence``. A pass that contributed
        1,663 detections through its fragment is counted as no pass at all.

        Invert when the patch lands: ``run_3`` should be present and the
        denominator 3.
        """
        resolved = resolve_pass_files(storm_pool)
        loaded = load_pass_detections(storm_pool)
        assert "run_3" in resolved, "the empty main file is still resolved"
        assert "run_3" not in loaded, "but contributes nothing, so it is dropped"
        assert len(loaded) == 2
        assert len(loaded) != len(resolved)


@pytest.mark.skipif(not PATCH_APPLIED, reason=_PATCH_REASON)
class TestRepairedBehaviour:
    """The acceptance criteria for the proposed patch."""

    def test_fragments_fold_into_their_parent_pass(self, storm_pool: Path) -> None:
        """Each fragment's files join its parent pass, creating no new pass."""
        resolved = resolve_pass_files(storm_pool)
        assert set(resolved) == {"run_1", "run_2", "run_3"}
        assert len(resolved["run_1"]) == 1
        assert len(resolved["run_2"]) == 2
        # run_3 takes its main file plus both _recovery and _recovery2.
        assert len(resolved["run_3"]) == 3

    def test_main_file_precedes_its_fragments(self, storm_pool: Path) -> None:
        """Ordering is main-first, so within-pass dedup keeps the main feature.

        ``deduplicate_within_pass`` keeps the FIRST of a near-duplicate pair,
        so a fragment must never be read ahead of the main file it supplements.
        """
        resolved = resolve_pass_files(storm_pool)
        assert resolved["run_2"][0].parent.name == "run_2"
        assert resolved["run_2"][1].parent.name == "run_2_recovery"
        assert [p.parent.name for p in resolved["run_3"]] == [
            "run_3",
            "run_3_recovery",
            "run_3_recovery2",
        ]

    def test_every_pass_reaches_the_loader(self, storm_pool: Path) -> None:
        """The storm-hit pass now contributes, so the denominator is right."""
        loaded = load_pass_detections(storm_pool)
        assert set(loaded) == {"run_1", "run_2", "run_3"}
        assert len(loaded) == 3
        assert len(loaded["run_2"]) == 3
        assert len(loaded["run_3"]) == 3

    def test_pass_filter_still_selects_by_pass_number(self, storm_pool: Path) -> None:
        """A fragment is filtered with its parent, never independently."""
        resolved = resolve_pass_files(storm_pool, pass_filter=[1, 2])
        assert set(resolved) == {"run_1", "run_2"}
        assert len(resolved["run_2"]) == 2

    def test_sidecars_are_still_excluded(self, storm_pool: Path) -> None:
        """``*.meta.json`` sidecars must not be mistaken for pass files."""
        resolved = resolve_pass_files(storm_pool)
        for files in resolved.values():
            assert all(f.suffix == ".geojson" for f in files)
            assert all(".meta" not in f.name for f in files)


class TestStateIndependentInvariants:
    """Properties that must hold whether or not the patch is applied."""

    def test_a_pool_with_no_fragments_is_unchanged(self, tmp_path: Path) -> None:
        """The patch must be a no-op on pools that never stormed."""
        pool = tmp_path / "clean"
        for n in (1, 2, 3):
            _write_pass(pool / f"run_{n}", ["tile_1", "tile_2"])
        resolved = resolve_pass_files(pool)
        assert set(resolved) == {"run_1", "run_2", "run_3"}
        assert all(len(files) == 1 for files in resolved.values())
        assert len(load_pass_detections(pool)) == 3

    def test_pass_naming_is_supported_alongside_run_naming(
        self, tmp_path: Path
    ) -> None:
        """``pass_NN`` pools keep their own pass ids."""
        pool = tmp_path / "passnamed"
        _write_pass(pool / "pass_01", ["tile_1"])
        _write_pass(pool / "pass_02", ["tile_2"])
        resolved = resolve_pass_files(pool)
        assert set(resolved) == {"pass_01", "pass_02"}

    def test_empty_pool_returns_empty(self, tmp_path: Path) -> None:
        """A directory with no pass subdirectories resolves to nothing."""
        empty = tmp_path / "empty"
        empty.mkdir()
        assert resolve_pass_files(empty) == {}

    def test_pass_with_no_geojson_is_omitted(self, tmp_path: Path) -> None:
        """A pass directory holding only sidecars contributes no files."""
        pool = tmp_path / "sidecars-only"
        _write_pass(pool / "run_1", ["tile_1"])
        (pool / "run_2").mkdir(parents=True)
        (pool / "run_2" / "detections-x-2026-01-01.meta.json").write_text("{}")
        assert set(resolve_pass_files(pool)) == {"run_1"}
