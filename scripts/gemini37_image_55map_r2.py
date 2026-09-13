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

CAMPAIGN_ROOT = PROJECT_ROOT / "outputs/gemini37-image-55map-2026-09-13"
CAMPAIGN_CELL = "g384_ov192_55map_g37img"
RESULTS_HOME = PROJECT_ROOT / "results/gemini37-image-55map-2026-09-13"

#: The carried operating points, FIXED by the Gold Standard calibration leg
#: before any 55-map scoring (card section 2). Both arms select unanimity, so
#: a K = 1 rung carries ``prob_t`` only and ``k`` collapses to 1 — stated here
#: rather than inferred later, because it means the K contrast varies the vote
#: threshold as well as the pass count (deltas section 5).
CARRIED: dict[str, float] = {"arm1": 0.10, "arm2": 0.88}

#: Verifier arms. ``model`` and ``thinking`` are recorded for the report; the
#: verifier runs themselves are launched outside this script.
ARM_MODEL = {
    "arm1": ("gemini-3-flash-preview", "minimal"),
    "arm2": ("gemini-3.7-flash", "low"),
}

RUNGS = (1, 3)

#: The Gold Standard calibration leg, used by the materialiser identity gate.
#: Feature counts are the committed ones read from the leg's analysis.json.
GS_VERIFIER = (
    PROJECT_ROOT / "outputs/gemini37-image-gs-2026-09-01/verifier/g384_ov192_g37img"
)
GS_CALIBRATION = {
    "arm1": {"verify": "verify_k3_arm1", "point": (0.10, 3), "n": 444},
    "arm2": {"verify": "verify_k3_arm2", "point": (0.88, 3), "n": 433},
}


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


def rung_frame(arm: str, k: int) -> gpd.GeoDataFrame:
    """The candidate frame for one rung: union geometry plus arm probabilities.

    Args:
        arm: ``arm1`` or ``arm2``.
        k: The rung's first-N pass count.

    Returns:
        A GeoDataFrame in EPSG:32635 with ``vote_count``,
        ``mound_probability`` and ``source_tile``, one row per candidate.
    """
    vroot = CAMPAIGN_ROOT / "verifier" / CAMPAIGN_CELL
    return load_manifest_probs(vroot / f"crops_k{k}", vroot / f"verify_k{k}_{arm}")


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
    carried = (CARRIED[arm], min(3, k))
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


def rung_label(arm: str, k: int) -> str:
    """The campaign's label for one rung, e.g. ``IMG-ARM2-K3``."""
    return f"IMG-{arm.upper()}-K{k}"


def stage_sweep(workers: int) -> int:
    """Sweep every achievable point of every rung; write CSVs and the oracles."""
    ref, bounds, tile_index = load_frames()
    frames = {}
    for arm in ARM_MODEL:
        for k in RUNGS:
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
    sweeps: dict[str, Any] = {
        "buffer_m": BUFFER_M,
        "reference": REFERENCE,
        "declared_family": "four external comparators + the K=1 vs K=3 contrast",
        "rungs": {},
    }
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
        carried_votes = min(3, k)
        carried = next(
            (r for r in frows
             if abs(r["prob_t"] - CARRIED[arm]) < 1e-9
             and r["min_votes"] == carried_votes),
            None,
        )
        sweeps["rungs"][label] = {
            "n_sweep_points": len(frows),
            "carried_point": [CARRIED[arm], carried_votes],
            "carried": carried,
            "f1_oracle": f1_best,
            "mcc_oracle": mcc_best,
        }
        logger.info(
            "%-14s F1 oracle %.4f at (%.2f, k%d) | MCC oracle %.4f at (%.2f, k%d)",
            label, f1_best["micro_f1_50"], f1_best["prob_t"], f1_best["min_votes"],
            mcc_best["tile_mcc"], mcc_best["prob_t"], mcc_best["min_votes"],
        )
    (RESULTS_HOME / "sweeps.json").write_text(json.dumps(sweeps, indent=2) + "\n")
    logger.info("wrote %s", (RESULTS_HOME / "sweeps.json").relative_to(PROJECT_ROOT))
    return 0


# ---------------------------------------------------------------------------
# Materialisation.
# ---------------------------------------------------------------------------


def stage_materialise() -> int:
    """Write one detections file per cell: carried, F1 oracle, MCC oracle."""
    sweeps = json.loads((RESULTS_HOME / "sweeps.json").read_text())
    cells: list[dict[str, Any]] = []
    for label, info in sweeps["rungs"].items():
        arm = "arm1" if "ARM1" in label else "arm2"
        k = int(label.rsplit("K", 1)[1])
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
    dest = RESULTS_HOME / "cells_manifest.json"
    dest.write_text(json.dumps({"buffer_m": BUFFER_M, "reference": REFERENCE,
                                "cells": cells}, indent=2) + "\n")
    logger.info("wrote %s", dest.relative_to(PROJECT_ROOT))
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


def stage_score(workers: int, jobs: int) -> int:
    """Score every materialised cell with the engine, on the board's recipe.

    ``--require-clean-inputs`` makes the engine refuse a detections file that
    is untracked or modified, so this stage checks git state first and says
    plainly what to commit rather than letting the engine exit 4 per cell.

    Args:
        workers: Engine parallelism per cell.
        jobs: Cells scored concurrently.

    Returns:
        A process exit status.
    """
    import subprocess
    from concurrent.futures import ThreadPoolExecutor

    manifest = json.loads((RESULTS_HOME / "cells_manifest.json").read_text())
    cells = manifest["cells"]
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
    for arm, spec in GS_CALIBRATION.items():
        try:
            frame = load_manifest_probs(GS_VERIFIER / "crops_k3",
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
    primary = primary or "IMG-ARM2-K3-carried"
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
    args = ap.parse_args()

    if args.stage == "selftest":
        return stage_selftest()
    if args.stage == "sweep":
        return stage_sweep(args.workers)
    if args.stage == "materialise":
        return stage_materialise()
    if args.stage == "score":
        return stage_score(args.workers, args.jobs)
    return stage_tests(args.primary)


if __name__ == "__main__":
    sys.exit(main())
