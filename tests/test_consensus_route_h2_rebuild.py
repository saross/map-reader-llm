"""H2's 26-of-30 arm rebuilt from its 30 passes scores as its committed cell.

Tier-2 companion to ``tests/test_consensus_route_origins.py`` (PI ruling
D60 (3), 2026-10-12). It runs the whole in-memory route
``run_pairwise_tests.py`` uses for a consensus arm: the 30 pass files of
``outputs/h11/pv-diag-384/flash-high-text-n5`` are loaded, deduplicated,
clustered and thresholded at 26 votes
(``pairwise_permutation_test.load_consensus_detections``), and the arm is
scored by the shared scorer. Before the fix the route dropped each
cluster's contributing tiles and read F1 0.814118 at 20 m; the re-scored
committed cell (``results/rescore-2026-06-05/pv-diag-384/consensus-sweep/
flash-high-text-n5__text-t0.7__consensus__t26/evaluation.json``) and H3
read 0.816471. Tier 2 because it reads about 45,000 committed pass
features.

Usage:
    python -m pytest -m tier2 tests/test_consensus_route_h2_rebuild.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import lib_advanced_metrics as lam  # noqa: E402
import pairwise_permutation_test as ppt  # noqa: E402

pytestmark = pytest.mark.tier2

_STUDY = PROJECT_ROOT / "outputs" / "h11" / "pv-diag-384" / "flash-high-text-n5"
_BOUNDS = (
    PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "384"
    / "full_evaluation_bounds.geojson"
)
_REFERENCE = PROJECT_ROOT / "inputs" / "vectors" / "references" / "mounds-reference.geojson"


@pytest.mark.skipif(
    not (_STUDY.is_dir() and _BOUNDS.exists() and _REFERENCE.exists()),
    reason="H2's 26-of-30 pool or the 384 px frame not present",
)
def test_h2_26_of_30_arm_matches_the_rescored_cell() -> None:
    """415 detections, F1 0.816471 at 20 m, one origin restored."""
    bounds = gpd.read_file(_BOUNDS).to_crs("EPSG:32635")
    refs = gpd.read_file(_REFERENCE).to_crs("EPSG:32635")
    gdf = ppt.load_consensus_detections(_STUDY, "text-t0.7,30,26", bounds)
    assert len(gdf) == 415
    scope = lam.scope_detections_to_frame(gdf, bounds)
    assert scope.diagnostics["n_origin_restored"] == 1
    _p, _r, f1 = lam.calculate_f1_internal(gdf, refs, bounds, buffer_metres=20)
    assert round(f1, 6) == 0.816471
