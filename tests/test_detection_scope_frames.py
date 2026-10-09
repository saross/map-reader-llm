"""
Tier-2 tests: the D50 scorer's tile-to-sheet rule on the committed frames.

The D50 review (Astra, 2026-10-09, finding 3) replaced the per-sheet loop's
bare ``str.startswith(sheet)`` tile selection with the longest-prefix
assignment the detection scope already used
(``lib_advanced_metrics.frame_tile_sheets``). The two rules differ only
where one sheet name is a prefix of another. These tests read the committed
tile-bounds files and hold that:

1. the parent sheet catalogue ``STUDY_SHEETS`` is exactly the sheets of the
   gold-standard and 55-map evaluation frames; and
2. on every committed frame, each sheet's tiles under the new rule are the
   tiles the old rule selected, in the same order — so no committed score
   can move through this change.

They read about 11 MB of committed GeoJSON, hence tier 2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import lib_advanced_metrics as lam  # noqa: E402

pytestmark = pytest.mark.tier2

#: The two frames the catalogue is drawn from.
CATALOGUE_FRAMES = (
    "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
    "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson",
)

#: Where the committed tile-bounds files live (archive excluded).
BOUNDS_GLOBS = (
    "inputs/**/*bounds*.geojson",
    "outputs/**/bounds/*.geojson",
    "results/**/bounds/*.geojson",
)


def _tile_names(path: Path) -> pd.DataFrame:
    """A frame's tile names, read without geometry (only names matter here)."""
    features = json.loads(path.read_text())["features"]
    return pd.DataFrame(
        {"tile_name": [f["properties"].get("tile_name") for f in features]}
    ).dropna()


def _committed_frames() -> list[Path]:
    """Every committed tile-bounds file that names its tiles."""
    paths = sorted({p for g in BOUNDS_GLOBS for p in PROJECT_ROOT.glob(g)})
    return [p for p in paths if "archive" not in p.parts]


def test_study_sheets_are_the_evaluation_frames_sheets():
    """STUDY_SHEETS is the union of the gold-standard and 55-map frames' sheets."""
    paths = [PROJECT_ROOT / rel for rel in CATALOGUE_FRAMES]
    if not all(p.exists() for p in paths):
        pytest.skip("evaluation bounds absent")
    sheets: set[str] = set()
    for path in paths:
        sheets |= set(lam.frame_sheets(_tile_names(path)))
    assert sheets == set(lam.STUDY_SHEETS)


def test_every_committed_frame_selects_each_sheets_tiles_as_before():
    """The longest-prefix rule equals ``str.startswith`` on every committed frame."""
    frames = [p for p in _committed_frames() if not _tile_names(p).empty]
    if not frames:
        pytest.skip("no committed tile-bounds files present")
    differing = []
    for path in frames:
        tiles = _tile_names(path)
        assigned = lam.frame_tile_sheets(tiles)
        for sheet in lam.frame_sheets(tiles):
            old = tiles.index[tiles["tile_name"].str.startswith(sheet)].tolist()
            new = tiles.index[assigned == sheet].tolist()
            if old != new:
                differing.append((str(path.relative_to(PROJECT_ROOT)), sheet))
    assert differing == []
