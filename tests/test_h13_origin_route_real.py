"""The H13 tier-0 sweep, on the committed passes, scores clusters on their sheets.

PI ruling D62 (1), 2026-10-13. A real-data companion to
``tests/test_h13_origin_route.py``: the tier-0 aggregation sweep's arm A
cell at corroboration ``c >= 1`` and consensus ``k >= 3`` is rebuilt from
the committed prepared passes (``outputs/h13/scoring/common/armA/``), and

* the in-memory cell and the same cell read back from the file it writes
  score identically (the origin travels with the file);
* its F1 at 20 m is 0.642599 (570 detections), where the bare-centroid
  route gave 0.626354 (PR #35's regenerated ``tier0_sweep.json`` and the
  committed one before it): 9 clusters are booked to their own sheet
  instead of the neighbouring one (``reports/s163-agent-records/
  origin-gap-h13-copies.md`` § 2);
* the legacy route is still reachable by tiling without origins, and
  reproduces the pre-fix F1 exactly.

Tier 2: it reads the committed passes and clusters about 2,600 points in
pure Python (several seconds).

Usage:
    python -m pytest tests/test_h13_origin_route_real.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.h13_aggregation_sweep import (  # noqa: E402
    GROUND_TRUTH,
    aggregate,
    load_arm_passes,
    write_cell,
)
from scripts.lib_advanced_metrics import calculate_f1_internal  # noqa: E402
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402

pytestmark = pytest.mark.tier2

SCORING = PROJECT_ROOT / "outputs" / "h13" / "scoring"


def test_tier0_arm_a_cell_scored_on_origin_sheets(tmp_path):
    """Arm A, c >= 1, k >= 3: origin route 0.642599, legacy route 0.626354."""
    bounds = gpd.read_file(SCORING / "bounds" / "h13_common_bounds.geojson")
    ref = gpd.read_file(GROUND_TRUTH)
    clusters = aggregate(load_arm_passes(SCORING, "armA"), 1, 3)
    target = tmp_path / "armA_c1_k3.geojson"
    gdf = write_cell(clusters, bounds, target)
    assert len(gdf) == 570

    _, _, f1 = calculate_f1_internal(gdf, ref, bounds, buffer_metres=20)
    assert f1 == pytest.approx(0.6425992779783394, abs=1e-12)
    _, _, f1_file = calculate_f1_internal(
        gpd.read_file(target), ref, bounds, buffer_metres=20)
    assert f1_file == f1

    # The legacy route: the same centroids, tiled with no origin.
    legacy = gdf[["geometry"]].copy()
    legacy["source_tile"] = assign_primary_tiles(legacy, bounds)
    moved = int((legacy["source_tile"] != gdf["source_tile"]).sum())
    assert moved == 9
    _, _, f1_legacy = calculate_f1_internal(legacy, ref, bounds, buffer_metres=20)
    assert f1_legacy == pytest.approx(0.6263537906137184, abs=1e-12)
