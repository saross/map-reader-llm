#!/usr/bin/env python3
"""
Tier-1 tests for ``scripts/audit_null_exemplar_overlap.py`` (E86 remediation 3).

The geometry is small, exact integer arithmetic, so it is tested directly:
stride-448 neighbours overlap and the next ring out does not; the 336 px step
of the 384 px frames gives up to a 3 x 3 neighbourhood; abutting windows do not
count as overlapping.

The committed sidecar is then checked against a fresh computation and against
the counts the erratum publishes. Those counts are quoted in E86, in
``docs/paper/methods-draft.md`` and in
``reports/null-exemplar-errata-2026-09-13.md``, so pinning them here means a
silent change to a manifest cannot quietly falsify published prose.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import audit_null_exemplar_overlap as overlap_mod  # noqa: E402

pytestmark = pytest.mark.tier1

REPO_ROOT = Path(__file__).resolve().parent.parent
SIDECAR = REPO_ROOT / overlap_mod.DEFAULT_SIDECAR

#: The exposure E86 publishes: frame label -> (overlapping, total).
PUBLISHED_EXPOSURE = {
    "era1-512-full-evaluation": (25, 340),
    "era1-512-validation": (3, 60),
    "era1-512-verification": (0, 5),
    "era1-512-calibration": (2, 20),
    "era2-384-full-evaluation": (20, 487),
    "era2-384-validation": (6, 240),
    "h10-384-test": (13, 327),
}

#: The three null exemplars, as E86 names them.
NULL_TILES = {
    "K-35-078-1_Lesovo": (2240, 2688),
    "K-35-053-3_Elenovo": (3584, 1344),
    "K-35-052-4_32635": (896, 1792),
}


# ---------------------------------------------------------------------------
# Filename parsing
# ---------------------------------------------------------------------------


def test_parse_tile_reads_sheet_and_offset() -> None:
    """A tile filename yields its sheet name and integer pixel offset."""
    assert overlap_mod.parse_tile("K-35-078-1_Lesovo_x2240_y2688.png") == (
        "K-35-078-1_Lesovo", 2240, 2688,
    )


def test_parse_tile_rejects_a_name_without_an_offset() -> None:
    """A filename carrying no offset raises rather than defaulting to (0, 0)."""
    with pytest.raises(ValueError, match="pixel offset"):
        overlap_mod.parse_tile("legend.png")


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------


def test_a_null_tile_overlaps_itself() -> None:
    """The exemplar is itself a member of the Era-1 512 px frames."""
    assert overlap_mod.windows_overlap(2240, 2688, 512, 2240, 2688)


@pytest.mark.parametrize("dx", [-448, 0, 448])
@pytest.mark.parametrize("dy", [-448, 0, 448])
def test_stride_448_neighbours_overlap(dx: int, dy: int) -> None:
    """At 512 px on a 448 px stride, all eight neighbours share pixels."""
    assert overlap_mod.windows_overlap(2240 + dx, 2688 + dy, 512, 2240, 2688)


@pytest.mark.parametrize("offset", [-896, 896])
def test_the_next_ring_out_does_not_overlap(offset: int) -> None:
    """Two strides away the windows are disjoint (896 >= 512)."""
    assert not overlap_mod.windows_overlap(2240 + offset, 2688, 512, 2240, 2688)
    assert not overlap_mod.windows_overlap(2240, 2688 + offset, 512, 2240, 2688)


def test_abutting_windows_do_not_overlap() -> None:
    """Half-open windows that merely touch share no pixel."""
    assert not overlap_mod.windows_overlap(2752, 2688, 384, 2240, 2688)


def test_384px_window_overlapping_a_512px_null() -> None:
    """A 384 px tile whose right edge reaches into the null window counts."""
    # A 384 px tile at x=1904 ends at 2288, three pixels past the null's left
    # edge at 2240.
    assert overlap_mod.windows_overlap(1904, 2688, 384, 2240, 2688)
    assert not overlap_mod.windows_overlap(1856, 2688, 384, 2240, 2688)


def test_other_sheets_are_never_counted() -> None:
    """Overlap is computed per sheet; a coincident offset elsewhere is not a hit."""
    windows = overlap_mod.load_null_windows(REPO_ROOT)
    assert "K-35-062-2_Rakovski" not in windows


# ---------------------------------------------------------------------------
# The null manifest and the committed sidecar
# ---------------------------------------------------------------------------


def test_null_windows_match_the_erratum() -> None:
    """The three exemplars are the tiles E86 names, at the offsets it gives."""
    assert overlap_mod.load_null_windows(REPO_ROOT) == NULL_TILES


def test_sidecar_exists_and_declares_its_schema() -> None:
    """The committed sidecar is present and self-describing."""
    payload = json.loads(SIDECAR.read_text(encoding="utf-8"))
    assert payload["schema"] == "null-exemplar-overlap-by-frame/1"
    assert payload["erratum"] == "E86"


def test_sidecar_matches_a_fresh_computation() -> None:
    """``--check`` semantics: the committed sidecar has not drifted."""
    fresh = overlap_mod.build_sidecar(REPO_ROOT)
    committed = json.loads(SIDECAR.read_text(encoding="utf-8"))
    assert committed == fresh


@pytest.mark.parametrize(
    ("label", "expected"), sorted(PUBLISHED_EXPOSURE.items()),
)
def test_published_exposure_per_frame(label: str, expected: tuple[int, int]) -> None:
    """Each frame's overlap count and total are the figures E86 publishes."""
    frame = overlap_mod.build_sidecar(REPO_ROOT)["frames"][label]
    assert (frame["n_overlapping"], frame["n_tiles"]) == expected


def test_every_null_tile_is_itself_an_era1_evaluation_tile() -> None:
    """The sharpest form of the E86 exposure: the exemplars are scored tiles."""
    frame = overlap_mod.build_sidecar(REPO_ROOT)[
        "frames"]["era1-512-full-evaluation"]
    for sheet, (x, y) in NULL_TILES.items():
        assert f"{sheet}_x{x}_y{y}.png" in frame["overlapping_tiles"]


def test_overlapping_ids_are_a_subset_of_their_frame() -> None:
    """Every reported id is really a member of the manifest it is reported for."""
    payload = overlap_mod.build_sidecar(REPO_ROOT)
    for frame in payload["frames"].values():
        tiles = set(json.loads(
            (REPO_ROOT / frame["manifest"]).read_text(encoding="utf-8")))
        assert set(frame["overlapping_tiles"]) <= tiles
        assert len(frame["overlapping_tiles"]) == frame["n_overlapping"]


def test_check_mode_passes_against_the_committed_sidecar() -> None:
    """The documented drift guard is green on the committed tree."""
    assert overlap_mod.main(["--check", "--root", str(REPO_ROOT)]) == 0
