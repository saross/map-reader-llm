#!/usr/bin/env python3
"""
Gemini 3.7 image at 55-map scale: r2 sweeps, materialisation, and the tests.

Card: ``planning/gemini37-image-55map-2026-09-13.md`` (section 2 the cells,
section 4 predictions P1-P5, section 5 run order). Deltas and the rulings this
script implements: ``reports/gemini37-image-55map-deltas-2026-09-13.md``
section 10.

What this script is for
-----------------------
The campaign's four rungs (two verifier arms x K = 1 and K = 3) have to be
scored **on the r2 board's own instrument**, because every prediction P1-P5 is
a difference against a cell on that board. The instrument is
``evaluate_detections.py`` against
``inputs/vectors/references/best-available-gt-55maps-r2.geojson`` over the
8,541-tile evaluation frame, NOT the canonical Track-2 corrected-F1 engine,
which belongs to a different reference and matching chain (deltas section
10.3). This script does everything around that engine: the achievable-point
sweeps, the materialisation of each cell at its operating point, and the
paired tile-swap family. The engine itself is then invoked per cell, unchanged
and directly, on the recipe quoted in the deltas report section 10.3.

Why it is a new script rather than a new family in ``final_board_sweeps.py``
---------------------------------------------------------------------------
The campaign is forbidden to re-tier the 55-map board or the tile-MCC tiering
and forbidden to touch a signed row. Adding families to the board's own
sweeper and builder would edit the membership structures those boards are
built from. So the primitives are **imported** from the board's modules —
never reimplemented — and the derived artefacts land in this campaign's own
results home.

Gates (nothing downstream is trusted until these pass; ``--stage selftest``)
---------------------------------------------------------------------------
1. **Materialiser identity.** Re-deriving the Gold Standard calibration leg's
   verified sets from the committed crop manifest and probabilities at the
   carried points reproduces their committed feature counts exactly.
2. **F1 mechanism.** Per-tile TP/FP/FN arrays recomputed for each comparator
   reproduce its committed ``evaluation.json`` F1 @ 50 m to 1e-4 — the same
   gate ``final_board_build.py`` applies to the legacy cells.
3. **MCC mechanism.** Per-tile truth/prediction vectors recomputed for each
   comparator reproduce its committed tile confusion matrix **exactly**, the
   gate ``mcc_tiering_55map.py`` applies.

The five-test family (declared 2026-09-13, before any 55-map score existed)
--------------------------------------------------------------------------
Four external comparators — ``FOURTH-N1-oracle``, ``ARM2-N3-oracle``,
``ARM2-N5-oracle``, ``IM-k3`` — plus the within-campaign K = 1 versus K = 3
contrast that P2 requires. Benjamini-Hochberg at q = 0.05 across those five,
separately on tile-MCC and on corrected micro-F1 @ 50 m.

Usage::

    python scripts/gemini37_image_55map_r2.py --stage selftest
    python scripts/gemini37_image_55map_r2.py --stage sweep --workers 12
    python scripts/gemini37_image_55map_r2.py --stage materialise
    # commit the materialised detections, then:
    python scripts/gemini37_image_55map_r2.py --stage score --workers 5 --jobs 4
    python scripts/gemini37_image_55map_r2.py --stage tests

Zero API. Run on sapphire (Hungarian matching over 8,541 tiles per sweep
point, and 10,000-draw permutations).

Created: 2026-09-13
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import sys
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.build_55map_leaderboard import BOUNDS, reference_gt  # noqa: E402
from scripts.final_board_sweeps import load_manifest_probs  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    calculate_tile_classification,
    compute_per_tile_tp_fp_fn,
)
from scripts.mcc_tiering_55map import (  # noqa: E402
    mcc_from_confusion,
    permutation_test_mcc,
)
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    micro_f1,
    permutation_test_float,
)
from scripts.stride55_score import (  # noqa: E402
    assign_standard_tile,
    build_map_constrained_index,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The r2 board's instrument, fixed. Changing any of these makes the campaign's
#: numbers incomparable with the cells P1-P5 are stated against.
BUFFER_M = 50
N_PERMS = 10_000
SEED = 42
REFERENCE = "r2"

#: Mechanism-gate tolerances. F1 is recomputed through a different code path
#: from the engine's, so it is compared to 1e-4; the tile confusion matrix is
#: integer-exact and compared exactly.
F1_GATE_TOL = 1e-4

#: Verifier arms. ``model`` and ``thinking`` are recorded for the report; the
#: verifier runs themselves are launched outside this script. The arms are
#: shared by every campaign of the image 2x2: arm 1 and arm 2 verify the SAME
#: candidates, so two pools x two arms are the four cells.
ARM_MODEL = {
    "arm1": ("gemini-3-flash-preview", "minimal"),
    "arm2": ("gemini-3.7-flash", "low"),
}


@dataclass(frozen=True)
class Campaign:
    """One proposer pool of the image 2x2 at deployment scale.

    The stages below are the same for every pool; only where the pool lives,
    which rungs it carries and which operating points its GS calibration leg
    fixed differ. Those are data, so they are a record rather than a second
    copy of the script (S155, 2026-09-18).

    Attributes:
        key: The ``--campaign`` name.
        prefix: Rung-label prefix, e.g. ``IMG`` gives ``IMG-ARM2-K3``.
        root: Campaign outputs root holding ``verifier/<cell>/``.
        cell: The pass-pool directory name.
        results_home: Where sweeps, cells and tests land.
        rungs: The first-N pass counts the pool carries.
        carried: ``(arm, k) -> (prob_t, min_votes)``, FIXED by the pool's Gold
            Standard calibration leg before any 55-map scoring. ``None`` until
            that leg has run — the sweep refuses to start without it.
        gs_verifier: The calibration leg's verifier root.
        gs_calibration: ``arm -> {crops, verify, point, n}`` for the
            materialiser identity gate: re-deriving the leg's verified set at
            the carried point must reproduce its committed feature count.
        calibration_files: ``arm -> analysis.json`` of the calibration leg's
            sweep, whose ``image_best`` must equal the carried point above —
            so a constant retyped wrongly fails the selftest rather than
            silently sweeping the wrong point.
    """

    key: str
    prefix: str
    root: Path
    cell: str
    results_home: Path
    rungs: tuple[int, ...]
    carried: dict[tuple[str, int], tuple[float, int]] | None
    gs_verifier: Path
    gs_calibration: dict[str, dict[str, Any]] | None
    calibration_files: dict[str, Path] | None = None


#: The 3.7 image pool. Carried points from card section 2 (K = 1 and K = 3,
#: the GS K = 3 leg of 30e36bcd1) and from the registered GS K = 5 cells
#: ``g37-image-k5-verified-carried-p0.10-k5`` / ``-swap37-p0.90-k5``
#: (``results/run-conditions.json``). Both arms select unanimity at every
#: rung, so a K = 1 rung carries ``prob_t`` only and ``k`` collapses to 1 —
#: stated here rather than inferred later, because it means the K contrast
#: varies the vote threshold as well as the pass count (deltas section 5).
G37 = Campaign(
    key="g37",
    prefix="IMG",
    root=PROJECT_ROOT / "outputs/gemini37-image-55map-2026-09-13",
    cell="g384_ov192_55map_g37img",
    results_home=PROJECT_ROOT / "results/gemini37-image-55map-2026-09-13",
    rungs=(1, 3, 5),
    carried={
        ("arm1", 1): (0.10, 1), ("arm1", 3): (0.10, 3), ("arm1", 5): (0.10, 5),
        ("arm2", 1): (0.88, 1), ("arm2", 3): (0.88, 3), ("arm2", 5): (0.90, 5),
    },
    gs_verifier=PROJECT_ROOT
    / "outputs/gemini37-image-gs-2026-09-01/verifier/g384_ov192_g37img",
    gs_calibration={
        "arm1": {"crops": "crops_k3", "verify": "verify_k3_arm1",
                 "point": (0.10, 3), "n": 444},
        "arm2": {"crops": "crops_k3", "verify": "verify_k3_arm2",
                 "point": (0.88, 3), "n": 433},
    },
    calibration_files={
        "arm1": PROJECT_ROOT / "results/gemini37-image-55map-2026-09-13/gs-calibration/arm1/analysis.json",
        "arm2": PROJECT_ROOT / "results/gemini37-image-55map-2026-09-13/gs-calibration/arm2/analysis.json",
    },
)

#: The Gemini 3 image pool. Its calibration leg ran on
#: ``image-b-gs-2026-08-28`` on 2026-09-18
#: (scripts/gemini3-image-55map-gs-calibration.sh; commits 276e25dcb and
#: 99afa6a4d): image_b_prepare_and_union.py first-N unions at K = 3 (2,227)
#: and K = 5 (2,788), both arms, swept at 20 m. The K = 1 rung carries the
#: K = 3 probability with votes collapsed to 1, as on the 3.7 pool.
G3_CALIBRATION_HOME = PROJECT_ROOT / "results/gemini3-image-55map-2026-09-16/gs-calibration"
G3 = Campaign(
    key="g3",
    prefix="G3IMG",
    root=PROJECT_ROOT / "outputs/gemini3-image-55map-2026-09-16",
    cell="g384_ov192_55map_g3img",
    results_home=PROJECT_ROOT / "results/gemini3-image-55map-2026-09-16",
    rungs=(1, 3, 5),
    carried={
        ("arm1", 1): (0.15, 1), ("arm1", 3): (0.15, 3), ("arm1", 5): (0.15, 5),
        ("arm2", 1): (0.88, 1), ("arm2", 3): (0.88, 3), ("arm2", 5): (0.95, 5),
    },
    gs_verifier=PROJECT_ROOT / "outputs/image-b-gs-2026-08-28/verifier/g384_ov192_image",
    gs_calibration={
        "arm1": {"crops": "crops_k3", "verify": "verify_k3_arm1",
                 "point": (0.15, 3), "n": 433},
        "arm2": {"crops": "crops_k3", "verify": "verify_k3_arm2",
                 "point": (0.88, 3), "n": 445},
    },
    calibration_files={
        "arm1": G3_CALIBRATION_HOME / "k3/arm1/analysis.json",
        "arm2": G3_CALIBRATION_HOME / "k3/arm2/analysis.json",
    },
)

CAMPAIGNS = {c.key: c for c in (G37, G3)}

#: The selected campaign and its aliases. The aliases exist so the stages read
#: as they did when the script served one pool; ``select_campaign`` rebinds
#: them all at once. The default is the 3.7 pool the script was written for.
CAMPAIGN: Campaign = G37
CAMPAIGN_ROOT = G37.root
CAMPAIGN_CELL = G37.cell
RESULTS_HOME = G37.results_home
RUNGS = G37.rungs
GS_VERIFIER = G37.gs_verifier

#: Backward-compatible view of the carried PROBABILITY per arm at the rungs
#: the script originally served (K = 1 and K = 3 share one probability per
#: arm); :func:`carried_point` is the general form.
CARRIED: dict[str, float] = {"arm1": 0.10, "arm2": 0.88}


def select_campaign(key: str) -> Campaign:
    """Bind the module to one campaign of the 2x2.

    Args:
        key: A key of :data:`CAMPAIGNS`.

    Returns:
        The selected campaign.
    """
    global CAMPAIGN, CAMPAIGN_ROOT, CAMPAIGN_CELL, RESULTS_HOME, RUNGS
    global GS_VERIFIER, GS_CALIBRATION, CARRIED
    camp = CAMPAIGNS[key]
    CAMPAIGN = camp
    CAMPAIGN_ROOT, CAMPAIGN_CELL = camp.root, camp.cell
    RESULTS_HOME, RUNGS, GS_VERIFIER = camp.results_home, camp.rungs, camp.gs_verifier
    GS_CALIBRATION = camp.gs_calibration or {}
    if camp.carried:
        CARRIED = {arm: camp.carried[(arm, min(camp.rungs))][0]
                   for arm in ARM_MODEL if (arm, min(camp.rungs)) in camp.carried}
    else:
        CARRIED = {}
    return camp


def carried_point(arm: str, k: int) -> tuple[float, int]:
    """The campaign's carried operating point for one rung.

    Args:
        arm: ``arm1`` or ``arm2``.
        k: The rung's pass count.

    Returns:
        ``(prob_t, min_votes)``.

    Raises:
        RuntimeError: The campaign's calibration leg has not fixed its points.
        KeyError: The rung has no carried point.
    """
    if not CAMPAIGN.carried:
        raise RuntimeError(
            f"campaign {CAMPAIGN.key}: carried points not fixed — run its GS "
            "calibration leg and record image_best here before sweeping")
    return CAMPAIGN.carried[(arm, k)]


def parse_rungs(spec: str | None) -> tuple[int, ...]:
    """``--rungs 5`` or ``--rungs 1,3`` to a tuple; ``None`` means all."""
    if not spec:
        return RUNGS
    rungs = tuple(int(x) for x in spec.split(","))
    bad = [k for k in rungs if k not in RUNGS]
    if bad:
        raise SystemExit(f"rungs {bad} are not in campaign {CAMPAIGN.key}'s {RUNGS}")
    return rungs
#: The committed r2 board, and the pair whose permutation result gate 4
#: reproduces. This pair is chosen because its committed p-value is 0.1208
#: rather than 0.0: a saturated verdict would pass even with a broken null.
COMMITTED_BOARD = Path(
    "results/55map-final-board-r2-2026-09-06/final_board_50m.json"
)
PAIRWISE_GATE_PAIR = ("ARM2-N5-oracle", "ARM2-N3-oracle")

GS_CALIBRATION: dict[str, dict[str, Any]] = G37.gs_calibration or {}


@dataclass(frozen=True)
class Comparator:
    """One external cell the campaign is tested against.

    Attributes:
        label: The cell's board label.
        detections: Repository-relative path to its detection set.
        evaluation: Repository-relative path to its committed evaluation.
        prob_field: The property holding the verifier probability, which
            differs between writers (``mound_probability`` on board-
            materialised cells, ``probability`` on the original verified file).
    """

    label: str
    detections: str
    evaluation: str
    prob_field: str


#: The four external comparators of the declared five-test family. IM-k3's
#: detection set is NOT under its evaluation directory: the MCC tiering scored
#: the original verified file in place, and that file — not the board's
#: re-serialised IM-oracle copy — is the one its committed confusion matrix
#: belongs to.
COMPARATORS: tuple[Comparator, ...] = (
    Comparator(
        "FOURTH-N1-oracle",
        "results/55map-final-board-r2-2026-09-06/cells/FOURTH-N1-oracle/detections.geojson",
        "results/55map-final-board-r2-2026-09-06/cells/FOURTH-N1-oracle/evaluation.json",
        "mound_probability",
    ),
    Comparator(
        "ARM2-N3-oracle",
        "results/55map-final-board-r2-2026-09-06/cells/ARM2-N3-oracle/detections.geojson",
        "results/55map-final-board-r2-2026-09-06/cells/ARM2-N3-oracle/evaluation.json",
        "mound_probability",
    ),
    Comparator(
        "ARM2-N5-oracle",
        "results/55map-final-board-r2-2026-09-06/cells/ARM2-N5-oracle/detections.geojson",
        "results/55map-final-board-r2-2026-09-06/cells/ARM2-N5-oracle/evaluation.json",
        "mound_probability",
    ),
    Comparator(
        "IM-k3",
        "outputs/55maps-image-generalisation/verified/verified_detections.geojson",
        "results/55maps-r2-ref-2026-09-06/IM-k3/evaluation.json",
        "probability",
    ),
)


# ---------------------------------------------------------------------------
# Frames, loaded once.
# ---------------------------------------------------------------------------


def load_frames() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, dict[str, int]]:
    """The r2 reference, the evaluation bounds, and the tile index.

    Returns:
        ``(ref, bounds, tile_index)`` — the reference in EPSG:32635 with its
        census gates applied by ``reference_gt``, the bounds in EPSG:32635,
        and a ``tile_name -> row`` index in the bounds' own sorted order (the
        order ``final_board_build.py`` uses, so per-tile arrays align).
    """
    ref = reference_gt(REFERENCE)
    bounds = gpd.read_file(BOUNDS)
    if bounds.crs is None:
        bounds = bounds.set_crs("EPSG:4326")
    bounds = bounds.to_crs("EPSG:32635")
    tile_order = sorted(bounds["tile_name"].tolist())
    return ref, bounds, {t: i for i, t in enumerate(tile_order)}


def read_detections(path: Path) -> gpd.GeoDataFrame:
    """Load a detection set into EPSG:32635, inferring its stored CRS.

    The heuristic is ``final_board_build.per_tile_arrays``': a first-point
    easting above 180 cannot be a longitude, so the file is already projected.

    Args:
        path: The detections GeoJSON.

    Returns:
        The detections in EPSG:32635.

    Raises:
        RuntimeError: If the file carries no ``source_tile`` column, without
            which per-tile attribution is not origin-tile attribution.
    """
    det = gpd.read_file(path)
    crs = "EPSG:32635" if abs(det.geometry.x.iloc[0]) > 180 else "EPSG:4326"
    det = det.set_crs(crs, allow_override=True).to_crs("EPSG:32635")
    if "source_tile" not in det.columns:
        raise RuntimeError(f"{path}: no source_tile — attribution must be origin-tile")
    return det


def per_tile_arrays(
    det: gpd.GeoDataFrame,
    ref: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
    tile_index: dict[str, int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-tile TP/FP/FN at 50 m, in the bounds' tile order.

    Args:
        det: Detections in EPSG:32635 with ``source_tile``.
        ref: Reference points in EPSG:32635.
        bounds: Tile polygons in EPSG:32635 with ``tile_name``.
        tile_index: ``tile_name -> row`` index.

    Returns:
        Three float arrays of length ``len(tile_index)``.
    """
    tm = compute_per_tile_tp_fp_fn(det, ref, bounds, buffer_metres=BUFFER_M)
    n = len(tile_index)
    tp, fp, fn = np.zeros(n), np.zeros(n), np.zeros(n)
    for _, row in tm.iterrows():
        i = tile_index.get(row["tile_name"])
        if i is not None:
            tp[i], fp[i], fn[i] = float(row["tp"]), float(row["fp"]), float(row["fn"])
    return tp, fp, fn


def tile_vectors(
    det: gpd.GeoDataFrame,
    ref: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    """Boolean per-tile truth and prediction vectors, plus the confusion.

    Delegates to ``lib_advanced_metrics.calculate_tile_classification`` — the
    scorer's own rule — so the vectors cannot drift from the engine's MCC.

    Args:
        det: Detections in EPSG:32635 with ``source_tile``.
        ref: Reference points in EPSG:32635.
        bounds: Tile polygons in EPSG:32635 with ``tile_name``.

    Returns:
        ``(truth, pred, confusion)`` with the vectors in bounds order and the
        confusion dict the scorer reports.

    Raises:
        ValueError: If the tile join is refused for this frame.
    """
    tiles = list(bounds["tile_name"].unique())
    index = {t: i for i, t in enumerate(tiles)}
    cls = calculate_tile_classification(det, ref, bounds)
    if "error" in cls:
        raise ValueError(f"tile vectors refused: {cls['error']}")
    truth = np.zeros(len(tiles), dtype=bool)
    pred = np.zeros(len(tiles), dtype=bool)
    for detail in cls["tile_details"]:
        i = index.get(detail["tile_name"])
        if i is None:
            continue
        truth[i] = bool(detail["has_mounds"])
        pred[i] = bool(detail["has_detections"])
    confusion = {k: int(cls[k]) for k in ("tp", "tn", "fp", "fn") if k in cls}
    return truth, pred, confusion


# ---------------------------------------------------------------------------
# The campaign's own frames: union + probabilities per rung.
# ---------------------------------------------------------------------------


def assign_eval_frame_tiles(frame: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Re-stamp ``source_tile`` from the proposer's tiling onto the scoring frame.

    **Why this exists.** The proposer runs on ``g384_ov192_55map`` — 384 px
    tiles on a 192 px stride, 24,561 of them — while the scoring frame
    ``55maps_evaluation_bounds.geojson`` is 384 px tiles on a **336 px**
    stride, 8,541 of them. Only 660 tile names are common to the two. The
    published tile-MCC convention is the name-based ``id`` join (PI ruling,
    ``reports/tile-mcc-geometric-join-2026-09-12.md``), which is well defined
    only when a cell's ``source_tile`` names tiles **of the scoring frame**. A
    union frame carrying the proposer's origin tiles therefore books almost
    nothing: measured here, 192 of 6,250 detections, and the invariant in
    ``lib_advanced_metrics`` rightly refuses the resulting table.

    Every other 55-map cell went through this step. The rule is
    ``stride55_score.assign_standard_tile`` over
    ``stride55_score.build_map_constrained_index``: the nearest standard-grid
    tile centroid **within the origin raster's own map**. The map constraint is
    not cosmetic — the sheet rasters overlap, and an unconstrained
    nearest-centroid assignment flips about 10 % of candidates to the adjacent
    sheet and moves corrected F1 by ~0.04 (``stride55_score.py`` lines 119-127).

    The rule is confirmed, not assumed: re-applying it to the committed
    ``FOURTH-N1-oracle``, ``ARM2-N3-oracle`` and ``ARM2-N5-oracle`` detection
    sets reproduces their stored ``source_tile`` for **100 %** of features, so
    it is provably the writer that produced the cells P1-P5 are stated against.
    ``stage_selftest`` gates that idempotency on every run.

    The proposer's origin tile is preserved as ``origin_source_tile`` so a
    detection can still be traced to the tile the model actually saw.

    Args:
        frame: A rung frame whose ``source_tile`` holds proposer origin tiles.

    Returns:
        The frame with ``source_tile`` on the scoring frame's vocabulary and
        ``origin_source_tile`` carrying what it replaced.
    """
    index = build_map_constrained_index()
    out = frame.copy()
    origin = out["source_tile"].astype(str).to_numpy()
    xs = out.geometry.x.to_numpy()
    ys = out.geometry.y.to_numpy()
    out["origin_source_tile"] = origin
    out["source_tile"] = [
        assign_standard_tile(index, origin[i], float(xs[i]), float(ys[i]))
        for i in range(len(out))
    ]
    return out


def rung_frame(arm: str, k: int) -> gpd.GeoDataFrame:
    """The candidate frame for one rung: union geometry plus arm probabilities.

    ``source_tile`` is re-stamped onto the scoring frame's vocabulary by
    :func:`assign_eval_frame_tiles`; without that the per-tile machinery cannot
    book the campaign's detections at all.

    Args:
        arm: ``arm1`` or ``arm2``.
        k: The rung's first-N pass count.

    Returns:
        A GeoDataFrame in EPSG:32635 with ``vote_count``,
        ``mound_probability``, ``source_tile`` (scoring frame) and
        ``origin_source_tile`` (proposer tiling), one row per candidate.
    """
    vroot = CAMPAIGN_ROOT / "verifier" / CAMPAIGN_CELL
    raw = load_manifest_probs(vroot / f"crops_k{k}", vroot / f"verify_k{k}_{arm}")
    return assign_eval_frame_tiles(raw)


def materialise(frame: gpd.GeoDataFrame, prob_t: float, min_votes: int) -> gpd.GeoDataFrame:
    """Apply an operating point to a candidate frame.

    The predicate is the board's, verbatim: keep a candidate when its verifier
    probability is at least ``prob_t`` AND its vote count is at least
    ``min_votes``.

    Args:
        frame: The rung's candidate frame.
        prob_t: Probability threshold.
        min_votes: Vote threshold.

    Returns:
        The retained subset.
    """
    return frame[
        (frame["mound_probability"] >= prob_t) & (frame["vote_count"] >= min_votes)
    ]


def achievable_points(frame: gpd.GeoDataFrame, k: int) -> list[tuple[float, int]]:
    """Every operating point the rung can actually reach.

    The grid is ``final_board_sweeps.py``': zero plus each distinct observed
    probability, rounded to four places, crossed with every vote threshold up
    to the rung's pass count. An oracle over this set is an oracle over the
    rung's whole achievable space, not over an arbitrary lattice.

    Args:
        frame: The rung's candidate frame.
        k: The rung's pass count.

    Returns:
        ``(prob_t, min_votes)`` pairs, sorted.
    """
    thresholds = sorted({0.0} | {round(float(v), 4) for v in frame["mound_probability"]})
    points = [(p, votes) for p in thresholds for votes in range(1, k + 1)]
    return points


def with_carried(
    points: list[tuple[float, int]], arm: str, k: int
) -> list[tuple[float, int]]:
    """Add the rung's carried point if the achievable grid does not contain it.

    The achievable grid is built from *observed* probabilities, so a carried
    threshold that no candidate happens to sit on exactly would otherwise be
    missing from the sweep — and the carried point is the campaign's headline
    cell, not an optional extra.

    Args:
        points: The achievable grid.
        arm: ``arm1`` or ``arm2``.
        k: The rung's pass count.

    Returns:
        The grid, with the carried point appended when it was absent.
    """
    carried = carried_point(arm, k)
    if carried in points:
        return points
    return sorted([*points, carried])


# ---------------------------------------------------------------------------
# Sweep, parallel over points.
# ---------------------------------------------------------------------------

_SHARED: dict[str, Any] = {}


def _init(ref, bounds, tile_index, frames) -> None:
    """Pool initialiser: share the heavy frames rather than pickling per task."""
    _SHARED.update(ref=ref, bounds=bounds, tile_index=tile_index, frames=frames)


def _score_point(task: tuple[str, float, int]) -> dict[str, Any]:
    """Score one sweep point on both metrics.

    Args:
        task: ``(rung_label, prob_t, min_votes)``.

    Returns:
        A row with detection count, the tile confusion, micro-F1 @ 50 m and
        tile-MCC. A point that retains nothing is reported with null metrics
        rather than crashing the sweep.
    """
    label, prob_t, min_votes = task
    frame = _SHARED["frames"][label]
    sub = materialise(frame, prob_t, min_votes)
    row: dict[str, Any] = {
        "rung": label,
        "prob_t": prob_t,
        "min_votes": min_votes,
        "n_detections": int(len(sub)),
    }
    if sub.empty:
        row.update(tp=0.0, fp=0.0, fn=None, micro_f1_50=None, tile_mcc=None)
        return row
    tp, fp, fn = per_tile_arrays(
        sub, _SHARED["ref"], _SHARED["bounds"], _SHARED["tile_index"]
    )
    truth, pred, _ = tile_vectors(sub, _SHARED["ref"], _SHARED["bounds"])
    tp_t = int((pred & truth).sum())
    fp_t = int((pred & ~truth).sum())
    fn_t = int((~pred & truth).sum())
    tn_t = int((~pred & ~truth).sum())
    row.update(
        tp=float(tp.sum()),
        fp=float(fp.sum()),
        fn=float(fn.sum()),
        micro_f1_50=micro_f1(tp.sum(), fp.sum(), fn.sum()),
        tile_mcc=float(mcc_from_confusion(tp_t, tn_t, fp_t, fn_t)),
        tile_tp=tp_t,
        tile_tn=tn_t,
        tile_fp=fp_t,
        tile_fn=fn_t,
    )
    return row


def load_sweeps(path: Path) -> dict[str, Any]:
    """The existing ``sweeps.json`` with its rungs, or a fresh record.

    A filtered sweep (``--rungs 5``) must keep the other rungs' entries;
    this is where they are read back. Extracted so the merge is testable
    without a frame (audit lens B, 2026-09-19).
    """
    if path.exists():
        sweeps = json.loads(path.read_text())
        sweeps.setdefault("rungs", {})
        return sweeps
    return {
        "buffer_m": BUFFER_M,
        "reference": REFERENCE,
        "declared_family": "four external comparators + the K=1 vs K=3 contrast",
        "rungs": {},
    }


def merge_cells(existing: list[dict[str, Any]],
                cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Replace same-label cells, keep the rest, append the new ones.

    ``--rungs 5`` materialises six cells; the K = 1 and K = 3 cells in the
    manifest must survive it. Order: surviving existing cells first, then
    the new ones.
    """
    new_labels = {c["label"] for c in cells}
    return [c for c in existing if c["label"] not in new_labels] + cells


def rung_label(arm: str, k: int) -> str:
    """The campaign's label for one rung, e.g. ``IMG-ARM2-K3``."""
    return f"{CAMPAIGN.prefix}-{arm.upper()}-K{k}"


def stage_sweep(workers: int, rungs: tuple[int, ...] | None = None) -> int:
    """Sweep every achievable point of every rung; write CSVs and the oracles.

    Args:
        workers: Sweep parallelism.
        rungs: Restrict to these rungs (e.g. a rung added after the others
            were swept); their entries replace the same rungs' entries in an
            existing ``sweeps.json`` and the other rungs' entries are kept.
    """
    rungs = rungs or RUNGS
    ref, bounds, tile_index = load_frames()
    frames = {}
    for arm in ARM_MODEL:
        for k in rungs:
            label = rung_label(arm, k)
            frames[label] = rung_frame(arm, k)
            logger.info("%s: %d candidates", label, len(frames[label]))

    tasks = []
    for label, frame in frames.items():
        k = int(label.rsplit("K", 1)[1])
        arm = "arm1" if "ARM1" in label else "arm2"
        for prob_t, votes in with_carried(achievable_points(frame, k), arm, k):
            tasks.append((label, prob_t, votes))
    logger.info("sweeping %d points across %d rungs (%d workers)",
                len(tasks), len(frames), workers)
    with Pool(workers, initializer=_init,
              initargs=(ref, bounds, tile_index, frames)) as pool:
        rows = pool.map(_score_point, tasks, chunksize=2)

    RESULTS_HOME.mkdir(parents=True, exist_ok=True)
    sweeps_path = RESULTS_HOME / "sweeps.json"
    sweeps = load_sweeps(sweeps_path)
    for label in frames:
        frows = [r for r in rows if r["rung"] == label and r["micro_f1_50"] is not None]
        frows.sort(key=lambda r: (r["prob_t"], r["min_votes"]))
        dest = RESULTS_HOME / f"sweep_{label}.csv"
        with dest.open("w", newline="") as fh:
            w = csvmod.DictWriter(fh, fieldnames=list(frows[0].keys()))
            w.writeheader()
            w.writerows(frows)
        f1_best = max(frows, key=lambda r: r["micro_f1_50"])
        mcc_best = max(frows, key=lambda r: r["tile_mcc"])
        k = int(label.rsplit("K", 1)[1])
        arm = "arm1" if "ARM1" in label else "arm2"
        carried_prob, carried_votes = carried_point(arm, k)
        carried = next(
            (r for r in frows
             if abs(r["prob_t"] - carried_prob) < 1e-9
             and r["min_votes"] == carried_votes),
            None,
        )
        sweeps["rungs"][label] = {
            "n_sweep_points": len(frows),
            "carried_point": [carried_prob, carried_votes],
            "carried": carried,
            "f1_oracle": f1_best,
            "mcc_oracle": mcc_best,
        }
        logger.info(
            "%-14s F1 oracle %.4f at (%.2f, k%d) | MCC oracle %.4f at (%.2f, k%d)",
            label, f1_best["micro_f1_50"], f1_best["prob_t"], f1_best["min_votes"],
            mcc_best["tile_mcc"], mcc_best["prob_t"], mcc_best["min_votes"],
        )
    sweeps_path.write_text(json.dumps(sweeps, indent=2) + "\n")
    logger.info("wrote %s", sweeps_path.relative_to(PROJECT_ROOT))
    return 0


# ---------------------------------------------------------------------------
# Materialisation.
# ---------------------------------------------------------------------------


def stage_materialise(rungs: tuple[int, ...] | None = None) -> int:
    """Write one detections file per cell: carried, F1 oracle, MCC oracle.

    Args:
        rungs: Restrict to these rungs; their cells replace the same labels
            in an existing ``cells_manifest.json`` and other cells are kept.
    """
    rungs = rungs or RUNGS
    sweeps = json.loads((RESULTS_HOME / "sweeps.json").read_text())
    manifest_path = RESULTS_HOME / "cells_manifest.json"
    existing: list[dict[str, Any]] = []
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text())["cells"]
    cells: list[dict[str, Any]] = []
    for label, info in sweeps["rungs"].items():
        arm = "arm1" if "ARM1" in label else "arm2"
        k = int(label.rsplit("K", 1)[1])
        if k not in rungs:
            continue
        frame = rung_frame(arm, k)
        wanted = {
            "carried": tuple(info["carried_point"]),
            "f1-oracle": (info["f1_oracle"]["prob_t"], info["f1_oracle"]["min_votes"]),
            "mcc-oracle": (info["mcc_oracle"]["prob_t"], info["mcc_oracle"]["min_votes"]),
        }
        for basis, (prob_t, votes) in wanted.items():
            sub = materialise(frame, float(prob_t), int(votes))
            cell_label = f"{label}-{basis}"
            dest = RESULTS_HOME / "cells" / cell_label / "detections.geojson"
            dest.parent.mkdir(parents=True, exist_ok=True)
            sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
            cells.append({
                "label": cell_label,
                "rung": label,
                "arm": arm,
                "verifier_model": ARM_MODEL[arm][0],
                "verifier_thinking": ARM_MODEL[arm][1],
                "k": k,
                "basis": basis,
                "point": f"({float(prob_t):.2f}, k{int(votes)})",
                "n_detections": int(len(sub)),
                "det": str(dest.relative_to(PROJECT_ROOT)),
            })
            logger.info("%-28s n=%5d -> %s", cell_label, len(sub),
                        dest.relative_to(PROJECT_ROOT))
    merged = merge_cells(existing, cells)
    manifest_path.write_text(json.dumps({"buffer_m": BUFFER_M, "reference": REFERENCE,
                                         "cells": merged}, indent=2) + "\n")
    logger.info("wrote %s (%d cells, %d new or replaced)",
                manifest_path.relative_to(PROJECT_ROOT), len(merged), len(cells))
    return 0


# ---------------------------------------------------------------------------
# Scoring: the engine, on the board's recipe, unchanged.
# ---------------------------------------------------------------------------

#: The r2 board's stage-2 recipe, read from a committed cell's own
#: ``evaluation.json`` ``cli_args`` block rather than retyped from prose
#: (``results/55map-final-board-r2-2026-09-06/cells/FOURTH-N1-oracle``).
ENGINE_BUFFERS = (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150)
ENGINE_BOOTSTRAP = 10_000
GROUND_TRUTH = "inputs/vectors/references/best-available-gt-55maps-r2.geojson"


def engine_command(det: str, out_dir: str, label: str, workers: int) -> list[str]:
    """The scoring command for one cell.

    Args:
        det: Repository-relative detections path.
        out_dir: Repository-relative output directory.
        label: The evaluation label to stamp.
        workers: Engine parallelism.

    Returns:
        The argument vector, for ``subprocess.run``.
    """
    return [
        ".venv/bin/python", "scripts/evaluate_detections.py",
        "--detections", det,
        "--buffers", *[str(b) for b in ENGINE_BUFFERS],
        "--ground-truth", GROUND_TRUTH,
        "--bounds", str(Path(BOUNDS).relative_to(PROJECT_ROOT)),
        "--bootstrap", str(ENGINE_BOOTSTRAP),
        "--seed", str(SEED),
        "--output-dir", out_dir,
        "--label", f"{label}-image-55map-r2",
        "--mcc", "--workers", str(workers),
        "--require-clean-inputs",
    ]


def stage_score(workers: int, jobs: int, rungs: tuple[int, ...] | None = None) -> int:
    """Score every materialised cell with the engine, on the board's recipe.

    ``--require-clean-inputs`` makes the engine refuse a detections file that
    is untracked or modified, so this stage checks git state first and says
    plainly what to commit rather than letting the engine exit 4 per cell.

    Args:
        workers: Engine parallelism per cell.
        jobs: Cells scored concurrently.
        rungs: Restrict to these rungs' cells (already-scored rungs are not
            re-scored; a re-score would only reproduce them).

    Returns:
        A process exit status.
    """
    import subprocess
    from concurrent.futures import ThreadPoolExecutor

    rungs = rungs or RUNGS
    manifest = json.loads((RESULTS_HOME / "cells_manifest.json").read_text())
    cells = [c for c in manifest["cells"] if c["k"] in rungs]
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", *[c["det"] for c in cells]],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip()
    if dirty:
        logger.error(
            "detections not committed — the engine's --require-clean-inputs "
            "would refuse them. Commit these first:\n%s", dirty)
        return 4

    def run_one(cell: dict[str, Any]) -> tuple[str, int]:
        out_dir = str((RESULTS_HOME / "cells" / cell["label"]).relative_to(PROJECT_ROOT))
        cmd = engine_command(cell["det"], out_dir, cell["label"], workers)
        log = RESULTS_HOME / "cells" / cell["label"] / "score.log"
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                              text=True, check=False)
        log.write_text(proc.stdout + proc.stderr)
        return cell["label"], proc.returncode

    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for label, rc in pool.map(run_one, cells):
            logger.info("scored %-28s rc=%d", label, rc)
            if rc != 0:
                failed.append(label)
    if failed:
        logger.error("scoring FAILED for %s — see each cell's score.log", failed)
        return 1
    logger.info("scored %d cells", len(cells))
    return 0


# ---------------------------------------------------------------------------
# Gates.
# ---------------------------------------------------------------------------


def stage_selftest() -> int:
    """Run the three mechanism gates. Returns non-zero on any failure."""
    failures: list[str] = []

    # Gate 1 — the materialiser reproduces the committed calibration counts.
    if not GS_CALIBRATION:
        failures.append(f"campaign {CAMPAIGN.key}: no GS calibration recorded")
    for arm, spec in GS_CALIBRATION.items():
        try:
            frame = load_manifest_probs(GS_VERIFIER / spec.get("crops", "crops_k3"),
                                        GS_VERIFIER / spec["verify"])
            got = len(materialise(frame, *spec["point"]))
        except Exception as exc:  # noqa: BLE001 - a gate reports, never raises
            failures.append(f"materialiser {arm}: {exc}")
            continue
        ok = got == spec["n"]
        logger.info("gate 1 materialiser %-5s at %s: %d vs committed %d — %s",
                    arm, spec["point"], got, spec["n"], "OK" if ok else "FAIL")
        if not ok:
            failures.append(f"materialiser {arm}: {got} != {spec['n']}")

    # Gate 1b — the carried constants are the calibration files' image_best.
    for arm, path in (CAMPAIGN.calibration_files or {}).items():
        try:
            best = json.loads(Path(path).read_text())["image_best"]
        except Exception as exc:  # noqa: BLE001 - a gate reports, never raises
            failures.append(f"calibration file {arm}: {exc}")
            continue
        want = carried_point(arm, int(best["min_votes"]))
        got = (round(float(best["prob_t"]), 4), int(best["min_votes"]))
        ok = got == want and best.get("n_detections") == GS_CALIBRATION[arm]["n"]
        logger.info("gate 1b calibration %-5s file says %s n=%s vs table %s n=%s — %s",
                    arm, got, best.get("n_detections"), want,
                    GS_CALIBRATION[arm]["n"], "OK" if ok else "FAIL")
        if not ok:
            failures.append(f"calibration {arm}: file {got} != table {want}")

    # Gates 2 and 3 — the two statistics reproduce each comparator's committed
    # evaluation through this script's own code path.
    ref, bounds, tile_index = load_frames()
    logger.info("reference %d points, bounds %d tiles", len(ref), len(bounds))
    for comp in COMPARATORS:
        ev = json.loads((PROJECT_ROOT / comp.evaluation).read_text())["summary"]
        want_f1 = next(b for b in ev["buffers"]
                       if b["buffer_metres"] == BUFFER_M)["f1"]
        want_conf = ev["tile_classification"]["confusion"]
        det = read_detections(PROJECT_ROOT / comp.detections)
        tp, fp, fn = per_tile_arrays(det, ref, bounds, tile_index)
        got_f1 = micro_f1(tp.sum(), fp.sum(), fn.sum())
        f1_ok = abs(got_f1 - want_f1) <= F1_GATE_TOL
        logger.info("gate 2 F1   %-18s %.6f vs committed %.4f — %s",
                    comp.label, got_f1, want_f1, "OK" if f1_ok else "FAIL")
        if not f1_ok:
            failures.append(f"F1 {comp.label}: {got_f1:.6f} != {want_f1}")
        _truth, _pred, got_conf = tile_vectors(det, ref, bounds)
        conf_ok = all(got_conf.get(k) == want_conf.get(k)
                      for k in ("tp", "tn", "fp", "fn"))
        logger.info("gate 3 MCC  %-18s %s vs committed %s — %s",
                    comp.label, got_conf, want_conf, "OK" if conf_ok else "FAIL")
        if not conf_ok:
            failures.append(f"confusion {comp.label}: {got_conf} != {want_conf}")

    # Gate 4 — the paired F1 test itself reproduces a committed pairwise result.
    # The pair chosen is the board's only non-degenerate one among the
    # comparators (p = 0.1208, not 0.0), so the null distribution is actually
    # being compared, not just a saturated verdict.
    board = json.loads((PROJECT_ROOT / COMMITTED_BOARD).read_text())
    want = next(
        (p for p in board["pairwise"]
         if {p["a"], p["b"]} == set(PAIRWISE_GATE_PAIR)), None)
    if want is None:
        failures.append(f"no committed pairwise record for {PAIRWISE_GATE_PAIR}")
    else:
        cells = {c.label: c for c in COMPARATORS}
        arrays = {}
        for label in (want["a"], want["b"]):
            det = read_detections(PROJECT_ROOT / cells[label].detections)
            arrays[label] = per_tile_arrays(det, ref, bounds, tile_index)
        a_tp, a_fp, a_fn = arrays[want["a"]]
        b_tp, b_fp, b_fn = arrays[want["b"]]
        got = permutation_test_float(a_tp, a_fp, a_fn, b_tp, b_fp, b_fn,
                                     n_permutations=N_PERMS, seed=SEED)
        for key, tol in (("observed_diff", 1e-4), ("p_value", 1e-9),
                         ("null_mean", 1e-4), ("null_std", 1e-4)):
            ok = abs(got[key] - want[key]) <= tol
            logger.info("gate 4 perm  %-18s %s: %s vs committed %s — %s",
                        f"{want['a']}|{want['b']}", key, got[key], want[key],
                        "OK" if ok else "FAIL")
            if not ok:
                failures.append(
                    f"permutation {key}: {got[key]} != {want[key]}")

    # Gate 5 — the tile-assignment rule is the one that wrote the comparators.
    # Gates 2-4 above all consume comparator detection sets, which already carry
    # scoring-frame source_tile names, so NONE of them can detect a campaign
    # rung whose source_tile is on the proposer's tiling instead. That is
    # exactly the defect this gate exists to catch: re-applying
    # assign_eval_frame_tiles' rule to a committed comparator must be a fixed
    # point, or the rule is not the writer's and the campaign's cells are not
    # comparable with the cells P1-P5 are stated against.
    #
    # IM-k3 is deliberately excluded and checked separately: the MCC tiering
    # scored the original verified file in place, so it never went through this
    # writer and reproduces at ~84 %. That is a property of the committed
    # comparator, not of this rule.
    index = build_map_constrained_index()
    for comp in COMPARATORS:
        det = read_detections(PROJECT_ROOT / comp.detections)
        origin = det["source_tile"].astype(str).to_numpy()
        xs, ys = det.geometry.x.to_numpy(), det.geometry.y.to_numpy()
        fresh = [assign_standard_tile(index, origin[i], float(xs[i]), float(ys[i]))
                 for i in range(len(det))]
        same = sum(1 for a, b in zip(fresh, origin, strict=True) if a == b)
        share = same / max(len(det), 1)
        if comp.label == "IM-k3":
            logger.info("gate 5 tile-join %-18s idempotent %d/%d (%.2f%%) — "
                        "EXPECTED partial, scored in place by the MCC tiering",
                        comp.label, same, len(det), 100 * share)
            continue
        ok = same == len(det)
        logger.info("gate 5 tile-join %-18s idempotent %d/%d (%.2f%%) — %s",
                    comp.label, same, len(det), 100 * share,
                    "OK" if ok else "FAIL")
        if not ok:
            failures.append(
                f"tile-join rule not idempotent on {comp.label}: "
                f"{same}/{len(det)}"
            )

    # Gate 6 — every campaign rung books its detections on the scoring frame.
    # Runs only once the arms exist, so the gate is informative before the data
    # and binding after it.
    for arm in ARM_MODEL:
        for k in RUNGS:
            label = rung_label(arm, k)
            try:
                frame = rung_frame(arm, k)
            except Exception as exc:  # noqa: BLE001 - pre-data run, report only
                logger.info("gate 6 booking  %-14s not yet built (%s)",
                            label, type(exc).__name__)
                continue
            in_frame = int(frame["source_tile"].isin(set(bounds["tile_name"])).sum())
            ok = in_frame == len(frame)
            logger.info("gate 6 booking  %-14s %d/%d candidates on the scoring "
                        "frame — %s", label, in_frame, len(frame),
                        "OK" if ok else "FAIL")
            if not ok:
                failures.append(
                    f"booking {label}: {in_frame}/{len(frame)} on the frame")

    if failures:
        for f in failures:
            logger.error("GATE FAIL %s", f)
        return 1
    logger.info("all gates PASS")
    return 0


# ---------------------------------------------------------------------------
# The paired tests.
# ---------------------------------------------------------------------------


def stage_tests(primary: str | None) -> int:
    """Run the declared five-test family on MCC and F1, with BH at q = 0.05.

    Args:
        primary: The campaign cell under test. Defaults to the primary cell of
            card section 4 — the all-3.7 K = 3 rung at its carried point.

    Returns:
        A process exit status.
    """
    manifest = json.loads((RESULTS_HOME / "cells_manifest.json").read_text())
    by_label = {c["label"]: c for c in manifest["cells"]}
    primary = primary or f"{CAMPAIGN.prefix}-ARM2-K3-carried"
    if primary not in by_label:
        logger.error("no such cell %s; have %s", primary, sorted(by_label))
        return 2
    if "-K3-" not in primary:
        logger.error(
            "the primary cell must be a K = 3 rung (%s is not): the family's "
            "fifth test is the K = 1 versus K = 3 contrast, which a K = 1 "
            "primary would run against itself", primary)
        return 2
    internal = primary.replace("-K3-", "-K1-")
    if internal not in by_label:
        logger.error("no K=1 counterpart %s for the internal contrast", internal)
        return 2

    ref, bounds, tile_index = load_frames()

    def vectors(det_path: Path) -> dict[str, Any]:
        det = read_detections(det_path)
        tp, fp, fn = per_tile_arrays(det, ref, bounds, tile_index)
        truth, pred, conf = tile_vectors(det, ref, bounds)
        return {"tp": tp, "fp": fp, "fn": fn, "truth": truth, "pred": pred,
                "confusion": conf, "n": int(len(det))}

    a = vectors(PROJECT_ROOT / by_label[primary]["det"])
    family: list[tuple[str, dict[str, Any]]] = []
    for comp in COMPARATORS:
        family.append((comp.label, vectors(PROJECT_ROOT / comp.detections)))
    family.append((internal, vectors(PROJECT_ROOT / by_label[internal]["det"])))

    mcc_rows, f1_rows = [], []
    for label, b in family:
        if not np.array_equal(a["truth"], b["truth"]):
            logger.error("truth vectors differ for %s — different frames", label)
            return 3
        mcc_rows.append({"a": primary, "b": label,
                         **permutation_test_mcc(a["pred"], b["pred"], a["truth"],
                                                n_permutations=N_PERMS, seed=SEED)})
        f1_rows.append({"a": primary, "b": label,
                        **permutation_test_float(a["tp"], a["fp"], a["fn"],
                                                 b["tp"], b["fp"], b["fn"],
                                                 n_permutations=N_PERMS, seed=SEED)})

    for rows in (mcc_rows, f1_rows):
        adjusted = apply_bh_correction([r["p_value"] for r in rows], q=0.05)
        for r, adj in zip(rows, adjusted, strict=True):
            r["bh_adjusted_p"] = round(float(adj), 6)
            r["significant"] = bool(adj < 0.05)

    out = {
        "primary_cell": primary,
        "buffer_m": BUFFER_M,
        "reference": REFERENCE,
        "n_permutations": N_PERMS,
        "seed": SEED,
        "family": [label for label, _ in family],
        "family_declared": (
            "four external comparators (card section 5 step 4) plus the "
            "within-campaign K = 1 vs K = 3 contrast that P2 requires"
        ),
        "mcc_tests": mcc_rows,
        "f1_tests": f1_rows,
    }
    dest = RESULTS_HOME / f"tests_{primary}.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    for r in mcc_rows:
        logger.info("MCC %-18s %.4f vs %.4f  d=%+.4f p=%.4f BH=%.4f %s",
                    r["b"], r["mcc_a"], r["mcc_b"], r["observed_diff"],
                    r["p_value"], r["bh_adjusted_p"],
                    "SIG" if r["significant"] else "ns")
    for r in f1_rows:
        logger.info("F1  %-18s %.4f vs %.4f  d=%+.4f p=%.4f BH=%.4f %s",
                    r["b"], r["f1_a"], r["f1_b"], r["observed_diff"],
                    r["p_value"], r["bh_adjusted_p"],
                    "SIG" if r["significant"] else "ns")
    logger.info("wrote %s", dest.relative_to(PROJECT_ROOT))
    return 0


def main() -> int:
    """Entry point. Returns a process exit status."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True,
                    choices=["selftest", "sweep", "materialise", "score", "tests"])
    ap.add_argument("--workers", type=int, default=8,
                    help="Sweep parallelism, or engine workers per cell (default 8)")
    ap.add_argument("--jobs", type=int, default=3,
                    help="Cells scored concurrently in --stage score (default 3)")
    ap.add_argument("--primary", default=None,
                    help="Cell under test for --stage tests")
    ap.add_argument("--campaign", default="g37", choices=sorted(CAMPAIGNS),
                    help="Which pool of the image 2x2 (default g37)")
    ap.add_argument("--rungs", default=None,
                    help="Restrict sweep/materialise/score to these rungs, "
                         "e.g. '5' (default: the campaign's rungs)")
    args = ap.parse_args()
    select_campaign(args.campaign)
    rungs = parse_rungs(args.rungs)

    if args.stage == "selftest":
        return stage_selftest()
    if args.stage == "sweep":
        return stage_sweep(args.workers, rungs)
    if args.stage == "materialise":
        return stage_materialise(rungs)
    if args.stage == "score":
        return stage_score(args.workers, args.jobs, rungs)
    return stage_tests(args.primary)


if __name__ == "__main__":
    sys.exit(main())
