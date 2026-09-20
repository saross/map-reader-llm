#!/usr/bin/env python3
"""
Final 55-map board, stage 1: gates, oracle re-sweeps, cell materialisation.

Executes §§ 3–5 of `planning/55map-final-board-2026-08-27.md` (PI
sign-off 2026-08-27). Every oracle cell on the final board is the
STANDARDISED-REFERENCE argmax within its run's verified sweep space
(PI ruling: the oracle column claims the theoretical maximum, so the
argmax is computed on the board's own reference, uniformly):

- Runs A/B and their N ∈ {1, 3, 5} rungs: the full vote ≥ 1 unions
  (rungs rebuilt by the gated first-N derivation with inherited
  K = 10 verification).
- Text incumbents (TH7 / T03 / TM): the original vote ≥ 4
  verification merged with the S104 vote-3 increment — the same
  two-pass union their committed k3 cells were built from;
  k ∈ {3, 4, 5}.
- Image: its own vote ≥ 3 verified union; k ∈ {3, 4, 5}.
- Uplift: the ≥ 3-of-10 verified band; k ∈ {3..10}.

Scorer: per-map Hungarian → per-tile counts → micro-F1 @ 50 m
(`lib_advanced_metrics.compute_per_tile_tp_fp_fn` + `micro_f1` — the
board instrument's own counting path, with uniform spatial tile
assignment via `assign_source_tiles`, so sweep argmaxes and board
tiers share one mechanism).

GATES (card § 5; nothing is written unless all pass):

- G4 sweep-scorer gate: the light scorer reproduces the committed
  standardised-board F1@50 for all 8 board cells + IM-k4 within the
  documented mechanism bound (0.003).
- Family identity gates: thresholding each family at its committed
  operating point reproduces the committed cell's detection count
  EXACTLY (TH7-k3 4,786; T03-k3 4,905; TM-k3 4,279; IM-k3 4,680;
  uplift 4,361; A-N10 4,475; B-N10 4,505; A-N5 4,597; B-N5 4,736).

Reference r2 (``--reference r2``; Session 149): the sweep runs on r2
(``reference_gt``) while EVERY gate above stays pinned to r1
(``standardised_gt``), and the 3.7 campaign families join under the
membership ruling — ARM1-N5 / ARM2-N5 / FOURTH-N10 with their N = 1 /
N = 3 rungs (``build_g37_families``), gated exactly as A/B: identity
counts (5,229 / 5,003 / 4,246), committed F1@50 within 0.003, exact
(TP, FP, FN) reconstruction, geometry vs the committed primaries. The
committed r1 home is read-only (``--force-r1`` to override, deliberately).

Sweep record (PI ruling 2026-09-20, item 2): every point also carries
the tile confusion and tile-MCC (``tile_mcc``, ``tile_tp``, ``tile_tn``,
``tile_fp``, ``tile_fn``) computed exactly as the image campaigns'
scorer computes them — through ``mcc_tiering_55map.tile_vectors``, the
shared wrapper over the engine's own tile-classification rule — and each
family's record gains an ``mcc_argmax`` beside its F1 ``argmax``. Before
this, the board could publish no MCC oracle while the image rows
published one per rung, so no text-vs-image MCC comparison was possible
(`reports/comparability-inventory-37-runs-2026-09-20.md` § 1.2, § 3.7).
``sweeps.json`` records which families carry it in ``mcc_families``.

Carried-k MCC oracle (PI ruling 2026-09-20, the redefinition): the
``mcc_argmax`` above is the **unconstrained** tile-MCC optimum — free to
pick any vote count the family's sweep offers — and every one of the 23
families put it at the LOWEST vote count available, paying 0.06–0.18 of
micro-F1 for a fraction of a point of tile-MCC. That makes it a poor
companion to the F1 oracle, which is read at the family's own vote
structure. So each family's record also gains
``mcc_argmax_at_carried_k``: the tile-MCC optimum over ``prob_t`` with
``min_votes`` PINNED to the family's CARRIED vote count (the ``k`` of its
carried cell in ``cells_manifest.json``, named in ``carried_k_source``).
That is the board's tile-MCC oracle from 2026-09-20. ``mcc_argmax`` is
NOT deleted: the collapse is a recorded property of the metric on this
corpus and the record keeps the evidence for it. Where a family's
carried k is the only rung its sweep offers (the N = 1 families) the two
coincide, flagged by ``mcc_argmax_at_carried_k_is_unconstrained``. A
family with no carried cell on the board has no carried k: its
``mcc_argmax_at_carried_k`` is ``null`` and
``mcc_argmax_at_carried_k_note`` says so. ``--record-carried-k``
recomputes the field for every family from the COMMITTED sweep CSVs
without re-sweeping anything.

Outputs (<board home>/): sweeps.json,
per-family sweep CSVs, cells/<label>/detections.geojson for every
non-committed cell, and cells_manifest.json for stages 2 (full
evaluations) and 3 (board build).

Usage::

    python scripts/final_board_sweeps.py [--workers N] [--reference {standardised,r2}]
    # sweep-record-only refresh of named families (no cells, no manifest):
    python scripts/final_board_sweeps.py --reference r2 --families ARM1-N1 ARM1-N3
    # carried-k MCC oracle from the committed CSVs (no sweep, no cells):
    python scripts/final_board_sweeps.py --reference r2 --record-carried-k

Zero API. Run on sapphire.

Created: 2026-08-27 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import sys
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.build_55map_leaderboard import (  # noqa: E402
    BOUNDS,
    board_home,
    reference_gt,
    standardised_gt,
)
from scripts.score_55maps_standardised_reference import (  # noqa: E402
    CELLS as BOARD_CELLS,
)
from scripts.lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
)
from scripts.mcc_tiering_55map import (  # noqa: E402
    mcc_from_confusion,
    tile_vectors,
)
from scripts.n1_baseline_leaderboard_tiering import micro_f1  # noqa: E402
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402
from scripts.gemini37_arm_ladder import (  # noqa: E402
    load_deduped_passes as load_g37_passes,
)
from scripts.gemini37_sweep_oracle import (  # noqa: E402
    CELLS as G37_CELLS,
    load_candidates as load_g37_candidates,
)
from scripts.stride55_ladder import (  # noqa: E402
    INHERIT_TOL_M,
    cluster_first_n,
    load_deduped_passes,
)
from scripts.stride55_score import build_map_constrained_index  # noqa: E402
from scripts.stride55_sweep_oracle import (  # noqa: E402
    RUNS as STRIDE_RUNS,
    load_candidates,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The r1 board home. Retained as documentation of where this script's outputs
#: historically landed; the output directory is now resolved per run through
#: ``board_home(--reference)`` so an r2 sweep cannot write into the r1 tree.
OUT = PROJECT_ROOT / "results/55map-final-board-2026-08-27"
BUFFER_M = 50

#: What a family with no carried cell on the board records instead of a
#: carried-k MCC oracle. Three families are in this position (``UPL``,
#: ``A-N1``, ``B-N1``): the board publishes an oracle cell for each but no
#: carried counterpart, so there is no vote count to pin the optimum to.
NO_CARRIED_K = "no carried k"

#: The record's own explanation of its two MCC argmaxes, written into
#: ``sweeps.json`` so a consumer reading the file alone cannot mistake the
#: retained unconstrained optimum for the board's published oracle.
SWEEPS_README = (
    "Per-family sweep record for the r2 board. 'argmax' is the micro-F1 @ 50 m "
    "optimum over the family's whole achievable grid (prob_t x min_votes) and "
    "is the basis of the '<family>-oracle' cells. "
    "'mcc_argmax_at_carried_k' is the board's TILE-MCC ORACLE from the PI "
    "ruling of 2026-09-20: the tile-MCC optimum over prob_t with min_votes "
    "PINNED to 'carried_k', the vote count of the family's carried cell "
    "('carried_k_source' in cells_manifest.json), so that it is a "
    "like-for-like companion of the F1 oracle. "
    "'mcc_argmax' is the UNCONSTRAINED tile-MCC optimum, free to choose any "
    "vote count. It is SUPERSEDED as the published oracle and RETAINED as a "
    "recorded finding: all 23 families put it at the lowest vote count their "
    "sweep offers, abandoning unanimity for a fraction of a point of tile-MCC "
    "at a cost of 0.06-0.18 micro-F1 (PI decision log D6a, 2026-09-20). "
    "'mcc_families' names the families whose rows carry a tile-MCC at all; "
    "'mcc_carried_k_families' names those with a carried-k oracle. A family "
    f"with no carried cell records '{NO_CARRIED_K}'."
)
MECHANISM_BOUND = 0.003  # the board's documented micro-vs-eval bound
DEPLOY = PROJECT_ROOT / "results/deployment-oracle-2026-06-06/vote3-verify"
IMK4_DET = (PROJECT_ROOT / "results/55maps-standardised-ref-2026-08-14"
            / "IM-k4/k4_verified_detections.geojson")
IMK4_F1_50 = 0.74  # committed evaluation.json @50 (2026-08-23)

# Family identity gates: committed operating point -> exact count.
IDENTITY = {
    "TH7": ((0.15, 3), 4786), "T03": ((0.15, 3), 4905),
    "TM": ((0.15, 3), 4279), "IM": ((0.15, 3), 4680),
    "UPL": ((0.15, 5), 4361),
    "A-N10": ((0.15, 8), 4475), "B-N10": ((0.15, 10), 4505),
    "A-N5": ((0.15, 4), 4597), "B-N5": ((0.15, 5), 4736),
}
#: The 3.7 campaign cells (membership ruling, PI 2026-09-06; on the board
#: from reference r2). Identity counts are the committed primaries' own
#: feature counts; committed F1@50 values are their standardised-ref
#: evaluations (results/gemini37-55map-2026-08-31/<arm>/.../standardised-ref
#: and results/gemini37-fourth-cell/55map/.../standardised-ref, read
#: 2026-09-07). Family names follow the campaign's own tags
#: (gemini37_sweep_oracle.CELLS) so every cell traces to its loader.
G37_IDENTITY = {
    "ARM1-N5": ((0.10, 5), 5229),
    "ARM2-N5": ((0.80, 5), 5003),
    "FOURTH-N10": ((0.98, 10), 4246),
}
G37_COMMITTED = [
    ("ARM1-N5-carried", "results/gemini37-55map-2026-08-31/arm1/"
                        "g384_ov192_55map_g37/primary/verified_detections.geojson",
     0.8550),
    ("ARM2-N5-carried", "results/gemini37-55map-2026-08-31/arm2/"
                        "g384_ov192_55map_g37/primary/verified_detections.geojson",
     0.8825),
    ("FOURTH-N10-carried", "results/gemini37-fourth-cell/55map/"
                           "g384_ov192_55map/primary/verified_detections.geojson",
     0.8732),
]
G37_FAMILY_OF_CELL = {"ARM1-N5": "arm1", "ARM2-N5": "arm2", "FOURTH-N10": "fourth"}

# Carried cells whose full evaluations are already committed.
COMMITTED_CARRIED = [
    ("TH7-k4", "outputs/55maps-text-high-generalisation/verified/"
               "verified_detections.geojson"),
    ("T03-k4", "outputs/55maps-text-high-t0.3-generalisation/verified/"
               "verified_detections.geojson"),
    ("TM-k4", "outputs/55maps-text-min-generalisation/verified/"
              "verified_detections.geojson"),
    ("IM-k4", "results/55maps-standardised-ref-2026-08-14/IM-k4/"
              "k4_verified_detections.geojson"),
]

_G: dict = {}  # worker globals


def prob_key(candidate_id) -> str:
    """probabilities.json key for a manifest candidate_id."""
    return (f"candidate_{candidate_id:05d}" if isinstance(candidate_id, int)
            else str(candidate_id))


def load_manifest_probs(cdir: Path, vdir: Path) -> gpd.GeoDataFrame:
    """Candidates + probabilities from an extract/verify pair (EPSG:32635)."""
    cands = json.loads(
        (cdir / "candidate_manifest.json").read_text())["candidates"]
    probs = json.loads((vdir / "probabilities.json").read_text())["results"]
    if len(cands) != len(probs):
        raise RuntimeError(
            f"{cdir}: {len(cands)} candidates vs {len(probs)} probabilities")
    return gpd.GeoDataFrame(
        {
            "vote_count": [c["properties"]["vote_count"] for c in cands],
            "mound_probability": [
                float(probs[prob_key(c["candidate_id"])]["mound_probability"])
                for c in cands],
            # The ORIGIN tile, not a spatial re-join: per-map matching in
            # the committed chain uses origin attribution, and ~6 % of
            # border detections land spatially inside the neighbouring
            # map's bounds (S143 diagnosis — a spatial re-join cost
            # −0.05 F1 by breaking those pairs into FP+FN).
            "source_tile": [c["source_tile"] for c in cands],
        },
        geometry=gpd.points_from_xy([c["centroid_x"] for c in cands],
                                    [c["centroid_y"] for c in cands]),
        crs="EPSG:32635")


def build_families(bounds: gpd.GeoDataFrame,
                   include_g37: bool = False) -> dict[str, dict]:
    """Every run's verified sweep space, per the card § 2.

    Args:
        bounds: The 55-map evaluation bounds (EPSG:32635).
        include_g37: Add the 3.7 campaign families (arm 1, arm 2, the
            fourth cell, each with its N = 1 / N = 3 first-N rungs) per the
            membership ruling. Off for the committed r1 board, whose
            membership is closed; on for reference r2 and later.
    """
    fam: dict[str, dict] = {}
    for label, run in (("TH7", "55maps-text-high-generalisation"),
                       ("T03", "55maps-text-high-t0.3-generalisation"),
                       ("TM", "55maps-text-min-generalisation")):
        orig = load_manifest_probs(PROJECT_ROOT / "outputs" / run / "crops",
                                   PROJECT_ROOT / "outputs" / run / "verified")
        inc = load_manifest_probs(DEPLOY / run / "crops",
                                  DEPLOY / run / "verified")
        if not (orig["vote_count"] >= 4).all() or not (
                inc["vote_count"] == 3).all():
            raise RuntimeError(
                f"{label}: unexpected vote structure in the two-pass union")
        fam[label] = {"gdf": pd.concat([orig, inc], ignore_index=True),
                      "ks": (3, 4, 5)}
    im = PROJECT_ROOT / "outputs/55maps-image-generalisation"
    fam["IM"] = {"gdf": load_manifest_probs(im / "crops", im / "verified"),
                 "ks": (3, 4, 5)}
    upl = PROJECT_ROOT / "outputs/55maps-text-min-n10-uplift"
    fam["UPL"] = {"gdf": load_manifest_probs(upl / "crops-3of10",
                                             upl / "verified-3of10"),
                  "ks": tuple(range(3, 11))}

    from scipy.spatial import cKDTree
    index = build_map_constrained_index()
    for cell, key in (("g384_ov128_55map", "A"), ("g384_ov192_55map", "B")):
        spec = STRIDE_RUNS[cell]
        k10 = load_candidates(cell, spec, bounds)
        fam[f"{key}-N10"] = {"gdf": k10, "ks": tuple(range(1, 11))}
        passes = load_deduped_passes(cell)
        tree = cKDTree(np.c_[k10.geometry.x, k10.geometry.y])
        probs10 = k10["mound_probability"].to_numpy()
        for n in (1, 3, 5):
            gdf = cluster_first_n(passes, n, index)
            d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
            gdf["mound_probability"] = probs10[idx]
            gdf = gdf[d <= INHERIT_TOL_M].copy()
            fam[f"{key}-N{n}"] = {"gdf": gdf, "ks": tuple(range(1, n + 1))}
    if include_g37:
        fam.update(build_g37_families(index))
    return fam


def build_g37_families(index: dict) -> dict[str, dict]:
    """The 3.7 campaign's sweep spaces: three N = K unions + six rungs.

    Mirrors the A/B branch of :func:`build_families` exactly — the rungs
    are the committed first-N derivation (``cluster_first_n`` over the
    pass-pinned passes) with probabilities inherited from the cell's own
    K-union verification within ``INHERIT_TOL_M`` — using the campaign's
    loaders (``gemini37_sweep_oracle.load_candidates`` for the unions,
    ``gemini37_arm_ladder.load_deduped_passes`` for the arms' five passes;
    the fourth cell re-verified stride B's ten passes, so it shares B's
    loader and pin).

    Args:
        index: The map-constrained tile index (``build_map_constrained_index``).

    Returns:
        Family name -> {"gdf", "ks"}: ``ARM1-N5``/``ARM2-N5`` (ks 1..5),
        ``FOURTH-N10`` (ks 1..10), and ``<family>-N1`` / ``-N3`` rungs.
    """
    from scipy.spatial import cKDTree

    fam: dict[str, dict] = {}
    arm_passes = load_g37_passes()  # pin-gated, five passes
    b_passes = load_deduped_passes("g384_ov192_55map")  # pin-gated, ten passes
    for family, tag in G37_FAMILY_OF_CELL.items():
        spec = G37_CELLS[tag]
        union = load_g37_candidates(tag, spec)
        k_max = spec["k_max"]
        fam[family] = {"gdf": union, "ks": tuple(range(1, k_max + 1))}
        passes = arm_passes if tag != "fourth" else b_passes
        tree = cKDTree(np.c_[union.geometry.x, union.geometry.y])
        probs = union["mound_probability"].to_numpy()
        stem = family.rsplit("-N", 1)[0]
        # Rungs are every first-N below the family's own K, so a family is
        # never given a rung that IS its full union. The two arms hold five
        # passes (k_max 5), so they keep exactly the (1, 3) they always had;
        # the fourth cell re-verified stride B's TEN passes (k_max 10), so it
        # gains the N = 5 rung findings.md § 3.3 records as
        # "zero-usd-inherited, never built". Derived from k_max rather than
        # listed, so the asymmetry cannot drift back in.
        for n in (n for n in (1, 3, 5) if n < k_max):
            gdf = cluster_first_n(passes, n, index)
            d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
            gdf["mound_probability"] = probs[idx]
            gdf = gdf[d <= INHERIT_TOL_M].copy()
            fam[f"{stem}-N{n}"] = {"gdf": gdf, "ks": tuple(range(1, n + 1))}
    return fam


def _init(ref, bounds, family_gdfs):
    _G["ref"], _G["bounds"], _G["fams"] = ref, bounds, family_gdfs


def tile_confusion(det: gpd.GeoDataFrame, ref: gpd.GeoDataFrame,
                   bounds: gpd.GeoDataFrame) -> dict:
    """The tile-level confusion and tile-MCC for one sweep point.

    The board's sweep record carried micro-F1 only, so the text track and
    the fourth cell could publish no MCC oracle while the image campaigns
    published one per rung (inventory § 1.2, § 3.7). This reproduces the
    image script's per-point computation exactly, through the shared
    library rather than a second copy of it:
    ``mcc_tiering_55map.tile_vectors`` (itself a thin wrapper over
    ``lib_advanced_metrics.calculate_tile_classification``, the scorer's
    own rule) for the boolean truth/prediction vectors, then
    ``mcc_from_confusion`` over the four counts.

    Args:
        det: Detections for this point, EPSG:32635, with ``source_tile``.
        ref: Reference points, same CRS.
        bounds: Tile polygons with ``tile_name``, same CRS.

    Returns:
        ``{"tile_mcc", "tile_tp", "tile_tn", "tile_fp", "tile_fn"}``. A
        point that retains no detection is reported with null values
        rather than crashing the sweep (the image script's convention);
        no committed board family has such a point.
    """
    if det.empty:
        return {"tile_mcc": None, "tile_tp": None, "tile_tn": None,
                "tile_fp": None, "tile_fn": None}
    _tiles, truth, pred = tile_vectors(det, ref, bounds)
    tp_t = int((pred & truth).sum())
    fp_t = int((pred & ~truth).sum())
    fn_t = int((~pred & truth).sum())
    tn_t = int((~pred & ~truth).sum())
    return {"tile_mcc": float(mcc_from_confusion(tp_t, tn_t, fp_t, fn_t)),
            "tile_tp": tp_t, "tile_tn": tn_t, "tile_fp": fp_t,
            "tile_fn": fn_t}


def _score(task):
    fam_name, prob_t, k = task
    g = _G["fams"][fam_name]
    sub = g[(g["mound_probability"] >= prob_t) & (g["vote_count"] >= k)]
    tm = compute_per_tile_tp_fp_fn(sub, _G["ref"], _G["bounds"],
                                   buffer_metres=BUFFER_M)
    tp, fp, fn = (int(tm["tp"].sum()), int(tm["fp"].sum()),
                  int(tm["fn"].sum()))
    return {"family": fam_name, "prob_t": prob_t, "min_votes": k,
            "n_detections": int(len(sub)), "tp": tp, "fp": fp, "fn": fn,
            "micro_f1_50": micro_f1(tp, fp, fn),
            **tile_confusion(sub, _G["ref"], _G["bounds"])}


def load_sweeps(path: Path, reference: str) -> dict:
    """The committed ``sweeps.json``, or a fresh record.

    A filtered re-sweep (``--families``) must keep the families it did not
    sweep, which is what this reads back. Extracted so the merge is
    testable without building a family frame.

    Args:
        path: The board home's ``sweeps.json``.
        reference: The reference vintage this run belongs to.

    Returns:
        The record to write into, with a ``families`` dict guaranteed.
    """
    if path.is_file():
        sweeps = json.loads(path.read_text())
        if not isinstance(sweeps.get("families"), dict):
            sweeps["families"] = {}
        sweeps["buffer_m"] = BUFFER_M
        sweeps["reference"] = reference
        return sweeps
    return {"buffer_m": BUFFER_M, "reference": reference, "families": {}}


def mcc_argmax(frows: list[dict]) -> dict | None:
    """The UNCONSTRAINED tile-MCC argmax of one family's sweep rows.

    Free to pick any ``min_votes`` the family's sweep offers. Every one of
    the board's 23 families puts this at the lowest vote count available
    (PI decision log D6a, 2026-09-20), which is why it is no longer the
    board's published MCC oracle — see :func:`mcc_argmax_at_carried_k`.
    It is kept in the record because that collapse is a finding about the
    metric on this corpus, not a defect to be edited out.

    Tie-break follows the image script: ``max`` over the rows in
    ``(prob_t, min_votes)`` order, so the lowest operating point wins a
    tie rather than whichever row the F1 sort happened to put first.

    Args:
        frows: One family's sweep rows.

    Returns:
        The winning row, or ``None`` when no row carries a tile-MCC
        (a sweep record written before this column existed).
    """
    scored = [r for r in frows if r.get("tile_mcc") is not None]
    if not scored:
        return None
    return max(sorted(scored, key=lambda r: (r["prob_t"], r["min_votes"])),
               key=lambda r: r["tile_mcc"])


def mcc_argmax_at_carried_k(frows: list[dict], carried_k: int | None) -> dict | None:
    """The tile-MCC argmax over ``prob_t`` at a FIXED vote count.

    The board's tile-MCC oracle from the PI ruling of 2026-09-20: the
    optimum is taken over the probability threshold only, with the vote
    count pinned to the family's carried ``k``, so that it is a
    like-for-like companion of the F1 oracle rather than a licence to
    abandon unanimity (which is what the unconstrained optimum does on
    every family of this board).

    Args:
        frows: One family's sweep rows.
        carried_k: The family's carried vote count, or ``None`` when the
            family has no carried cell on the board.

    Returns:
        The winning row, or ``None`` when there is no carried k, no row
        at that vote count, or no row carrying a tile-MCC.
    """
    if carried_k is None:
        return None
    scored = [r for r in frows
              if r.get("tile_mcc") is not None
              and int(r["min_votes"]) == int(carried_k)]
    if not scored:
        return None
    return max(sorted(scored, key=lambda r: (r["prob_t"], r["min_votes"])),
               key=lambda r: r["tile_mcc"])


def family_of_carried_label(label: str) -> str | None:
    """The family a carried cell's label belongs to, or ``None``.

    Two spellings are in use on this board and both are read here rather
    than listed, so a new carried cell is picked up without a table edit:

    * ``<family>-carried`` — every materialised carried cell, including
      the emergent N = 3 cells and the 3.7 carried analogues;
    * ``<family>-k<N>`` — the four committed text/image incumbents
      (``TH7-k4``, ``T03-k4``, ``TM-k4``, ``IM-k4``).

    Args:
        label: A cell label from ``cells_manifest.json``.

    Returns:
        The family name, or ``None`` if the label is neither spelling.
    """
    if label.endswith("-carried"):
        return label[: -len("-carried")]
    stem, sep, tail = label.rpartition("-k")
    if sep and stem and tail.isdigit():
        return stem
    return None


def carried_k_by_family(manifest_path: Path) -> dict[str, dict]:
    """Each family's CARRIED vote count, read from the board's cell manifest.

    "Carried" is whatever the manifest calls carried — basis ``carried``,
    ``carried (post-hoc)`` or ``carried-analogue (post-hoc)`` — so the
    carried analogues the 2026-09-20 addendum added give the 3.7 rungs a
    carried k, exactly as the ruling directs. Families with no carried
    cell (on this board: ``UPL``, ``A-N1``, ``B-N1``) are simply absent
    from the result, and their carried-k oracle is recorded as null.

    Args:
        manifest_path: The board home's ``cells_manifest.json``.

    Returns:
        ``family -> {"k": int, "prob_t": float, "label": str,
        "basis": str}``. Empty when the manifest does not exist yet.
    """
    if not manifest_path.is_file():
        return {}
    out: dict[str, dict] = {}
    for cell in json.loads(manifest_path.read_text()).get("cells", []):
        if "carried" not in str(cell.get("basis", "")):
            continue
        family = family_of_carried_label(str(cell.get("label", "")))
        if family is None:
            continue
        point = str(cell.get("point", ""))
        try:
            prob_s, k_s = point.strip("()").split(",")
            k = int(k_s.strip().lstrip("k"))
            prob_t = float(prob_s)
        except (ValueError, AttributeError):
            logger.warning("carried cell %s has an unreadable point %r — "
                           "skipped", cell.get("label"), point)
            continue
        if family in out and out[family]["k"] != k:
            raise RuntimeError(
                f"{family}: two carried cells disagree on k — "
                f"{out[family]['label']} k{out[family]['k']} vs "
                f"{cell['label']} k{k}")
        out[family] = {"k": k, "prob_t": prob_t, "label": cell["label"],
                       "basis": cell["basis"]}
    return out


def read_sweep_csv(path: Path) -> list[dict]:
    """One family's committed sweep CSV, typed as the sweep wrote it.

    ``--record-carried-k`` recomputes an argmax from the committed CSVs
    rather than re-sweeping, so the CSV's strings have to come back as the
    numbers the in-memory rows carried. Empty cells (a point that retained
    no detection) come back as ``None``.

    The counting columns are integers in this board's CSVs but floats in the
    image campaigns' (``gemini37_image_55map_r2._score_point`` sums numpy
    arrays into ``tp``/``fp``/``fn``), and the tile-presence builder reads
    both. So a counting column comes back as an ``int`` when its literal is
    one and a ``float`` otherwise, rather than being forced either way: a
    blanket ``float`` would make the board's exact counts approximate, and a
    blanket ``int`` crashes on ``4870.0``.

    Args:
        path: ``sweep_<family>.csv`` in a board or campaign home.

    Returns:
        The rows, in file order.
    """
    counts = {"min_votes", "n_detections", "tp", "fp", "fn",
              "tile_tp", "tile_tn", "tile_fp", "tile_fn"}
    floats = {"prob_t", "micro_f1_50", "tile_mcc"}
    rows: list[dict] = []
    with path.open(newline="") as fh:
        for raw in csvmod.DictReader(fh):
            row: dict = {}
            for key, value in raw.items():
                if value is None or value == "":
                    row[key] = None
                elif key in counts:
                    row[key] = (int(value) if _is_int_literal(value)
                                else float(value))
                elif key in floats:
                    row[key] = float(value)
                else:
                    row[key] = value
            rows.append(row)
    return rows


def _is_int_literal(value: str) -> bool:
    """Whether a CSV cell spells a whole number without a decimal point."""
    try:
        int(value)
    except ValueError:
        return False
    return True


def carried_k_record(frows: list[dict], carried: dict | None) -> dict:
    """The carried-k block of one family's ``sweeps.json`` entry.

    Args:
        frows: The family's sweep rows.
        carried: Its entry from :func:`carried_k_by_family`, or ``None``.

    Returns:
        The four keys the record gains, ready to merge into the family's
        entry.
    """
    if carried is None:
        return {"carried_k": None, "carried_k_source": None,
                "mcc_argmax_at_carried_k": None,
                "mcc_argmax_at_carried_k_note": NO_CARRIED_K,
                "mcc_argmax_at_carried_k_is_unconstrained": None}
    best = mcc_argmax_at_carried_k(frows, carried["k"])
    unconstrained = mcc_argmax(frows)
    coincide = (best is not None and unconstrained is not None
                and (best["prob_t"], best["min_votes"])
                == (unconstrained["prob_t"], unconstrained["min_votes"]))
    return {"carried_k": carried["k"],
            "carried_k_source": carried["label"],
            "mcc_argmax_at_carried_k": best,
            "mcc_argmax_at_carried_k_note": None,
            "mcc_argmax_at_carried_k_is_unconstrained": coincide}


def record_carried_k(out: Path, reference: str) -> int:
    """Merge ``mcc_argmax_at_carried_k`` into the committed sweep record.

    Reads the committed per-family CSVs — no family frame is built, no
    point is re-scored, and no cell or manifest is written. This is the
    path the 2026-09-20 redefinition took: the sweep rows already carry
    ``tile_mcc`` per point, so the new oracle is a different argmax over
    the same, unchanged evidence.

    Args:
        out: The board home.
        reference: The reference vintage, stamped into the record.

    Returns:
        Process exit code.
    """
    path = out / "sweeps.json"
    sweeps = load_sweeps(path, reference)
    carried = carried_k_by_family(out / "cells_manifest.json")
    logger.info("carried k read for %d famil%s from cells_manifest.json",
                len(carried), "y" if len(carried) == 1 else "ies")
    for name, record in sweeps["families"].items():
        csv_path = out / f"sweep_{name}.csv"
        if not csv_path.is_file():
            raise SystemExit(f"{csv_path.name}: missing — cannot recompute "
                             f"{name}'s carried-k MCC oracle from the "
                             "committed CSVs")
        frows = read_sweep_csv(csv_path)
        block = carried_k_record(frows, carried.get(name))
        record.update(block)
        best = block["mcc_argmax_at_carried_k"]
        if best is None:
            logger.info("%-10s %s", name, NO_CARRIED_K)
            continue
        logger.info("%-10s carried k%-2d (%s): MCC %.4f at (%.2f, k%d), "
                    "micro %.4f%s", name, block["carried_k"],
                    block["carried_k_source"], best["tile_mcc"],
                    best["prob_t"], best["min_votes"], best["micro_f1_50"],
                    "  [= unconstrained]"
                    if block["mcc_argmax_at_carried_k_is_unconstrained"]
                    else "")
    stamp_record(sweeps)
    path.write_text(json.dumps(sweeps, indent=2) + "\n")
    logger.info("CARRIED-K RECORD COMPLETE: %d families in %s",
                len(sweeps["families"]), path.relative_to(PROJECT_ROOT))
    return 0


def stamp_record(sweeps: dict) -> None:
    """Refresh the record's derived index keys and its ``_README``.

    Args:
        sweeps: The record about to be written.
    """
    sweeps["_README"] = SWEEPS_README
    sweeps["mcc_families"] = sorted(
        n for n, rec in sweeps["families"].items()
        if rec.get("mcc_argmax") is not None)
    sweeps["mcc_carried_k_families"] = sorted(
        n for n, rec in sweeps["families"].items()
        if rec.get("mcc_argmax_at_carried_k") is not None)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument(
        "--reference", choices=["standardised", "r2"], default="standardised",
        help="Reference vintage this sweep belongs to. Selects the OUTPUT "
             "home only: the G4 gate below always reproduces the committed r1 "
             "board, because 'the light scorer still agrees with the engine' "
             "is a claim about the mechanism, not about the reference under "
             "test (PI ruling, Session 149). Passing r2 writes to "
             "55map-final-board-r2-2026-09-06/ and leaves the r1 home "
             "untouched.",
    )
    ap.add_argument(
        "--force-r1", action="store_true",
        help="Permit writing into the COMMITTED r1 board home. The r1 home "
             "is read-only by policy (H2): G3/G4 reproduce it, so rewriting "
             "it destroys the regression evidence. Only for a deliberate, "
             "recorded regeneration.",
    )
    ap.add_argument(
        "--families", nargs="+", metavar="FAMILY",
        help="Sweep only these families and write only their CSVs, merging "
             "their entries into the existing sweeps.json and leaving every "
             "other family's committed record untouched. EVERY gate still "
             "runs over EVERY family — the filter narrows what is written, "
             "never what is checked. A filtered run also writes no cell and "
             "does not rewrite cells_manifest.json, because the materialised "
             "cells of the families it did not sweep would be dropped; use "
             "scripts/final_board_posthoc_cells.py for cells a filtered "
             "re-sweep implies.",
    )
    ap.add_argument(
        "--record-carried-k", action="store_true",
        help="Recompute every family's mcc_argmax_at_carried_k from the "
             "COMMITTED sweep CSVs and merge it into sweeps.json, then stop. "
             "No family frame is built, no point is re-scored, no gate over "
             "the frames runs and no cell or manifest is written: the rows "
             "already carry tile_mcc per point, so the 2026-09-20 "
             "redefinition is a different argmax over unchanged evidence.",
    )
    args = ap.parse_args()
    out = board_home(args.reference)
    include_g37 = args.reference == "r2"
    if args.record_carried_k:
        if args.families:
            ap.error("--record-carried-k rewrites the whole record from the "
                     "committed CSVs; --families would narrow nothing and "
                     "risks implying it did")
        if args.reference == "standardised" and not args.force_r1:
            ap.error(f"{out.relative_to(PROJECT_ROOT)} is the committed r1 "
                     "board home and is read-only (H2). Pass --reference r2.")
        return record_carried_k(out, args.reference)
    if args.reference == "standardised" and out.exists() and not args.force_r1:
        ap.error(f"{out.relative_to(PROJECT_ROOT)} is the committed r1 board "
                 "home and is read-only (H2). Pass --reference r2 for the "
                 "r2 board, or --force-r1 to regenerate r1 deliberately.")

    # PINNED TO r1, deliberately, whatever --reference says: G4 asks whether
    # the light scorer still reproduces the COMMITTED r1 board, which is a
    # regression test on the code. Pointing it at r2 would compare the r2
    # numbers to the r1 board and fail by construction, disabling the gate
    # exactly when a new reference makes it most worth having (BLOCKER 4).
    # ``ref`` is the vintage the SWEEP runs on — the oracle column claims
    # the argmax on the board's own reference, uniformly (card § 1).
    gate_ref = standardised_gt()
    ref = reference_gt(args.reference) if args.reference != "standardised" else gate_ref
    bounds = gpd.read_file(BOUNDS)
    if bounds.crs is None:
        bounds = bounds.set_crs("EPSG:4326")
    bounds = bounds.to_crs("EPSG:32635")

    # G4: the light scorer reproduces the committed standardised board.
    board = json.loads(
        (PROJECT_ROOT / "results/55map-leaderboard"
         / "55map_leaderboard_50m_standardised.json").read_text())
    committed = {c["name"].split(" ")[0]: c["f1_50"] for c in board["cells"]}
    checks = [(c["label"], PROJECT_ROOT / c["det"], committed[c["label"]])
              for c in BOARD_CELLS if c["label"] in committed]
    checks.append(("IM-k4", IMK4_DET, IMK4_F1_50))
    if include_g37:
        checks += [(label, PROJECT_ROOT / det, f1) for label, det, f1 in G37_COMMITTED]
    committed_counts: dict[str, tuple[int, int, int]] = {}
    for label, det_path, f1_committed in checks:
        det = gpd.read_file(det_path).to_crs("EPSG:32635")
        det = assign_source_tiles(det, bounds)
        tm = compute_per_tile_tp_fp_fn(det, gate_ref, bounds,
                                       buffer_metres=BUFFER_M)
        tp, fp, fn = (int(tm["tp"].sum()), int(tm["fp"].sum()),
                      int(tm["fn"].sum()))
        committed_counts[label] = (tp, fp, fn)
        f1 = micro_f1(tp, fp, fn)
        if abs(f1 - f1_committed) > MECHANISM_BOUND:
            raise RuntimeError(
                f"G4 FAILED {label}: micro {f1:.6f} vs committed "
                f"{f1_committed:.6f}")
        logger.info("G4 OK %-8s micro %.4f vs committed %.4f (d %+.4f)",
                    label, f1, f1_committed, f1 - f1_committed)

    families = build_families(bounds, include_g37=include_g37)
    for name, spec in families.items():
        spec["gdf"] = assign_source_tiles(spec["gdf"], bounds)

    identity = {**IDENTITY, **(G37_IDENTITY if include_g37 else {})}
    # Family identity gates.
    for name, ((pt, pk), expected) in identity.items():
        g = families[name]["gdf"]
        n = int(((g["mound_probability"] >= pt)
                 & (g["vote_count"] >= pk)).sum())
        if n != expected:
            raise RuntimeError(
                f"identity gate FAILED {name}: {n} at ({pt}, k{pk}) vs "
                f"committed {expected}")
        logger.info("identity OK %-6s (%.2f, k%d) -> %d", name, pt, pk, n)

    # Mechanism-equality gates (S143 lesson — counts alone missed a
    # −0.05 map-attribution defect): each incumbent family's
    # reconstruction at its committed point must reproduce the committed
    # file's EXACT integer (TP, FP, FN) triple.
    mechanism_pairs = [("TH7", "TH7-k3"), ("T03", "T03-k3"),
                       ("TM", "TM-k3"), ("IM", "IM-k3"),
                       ("UPL", "TM-n10-k5")]
    if include_g37:
        mechanism_pairs += [(f, f"{f}-carried") for f in G37_IDENTITY]
    for name, committed_label in mechanism_pairs:
        (pt, pk), _ = identity[name]
        g = families[name]["gdf"]
        sub = g[(g["mound_probability"] >= pt) & (g["vote_count"] >= pk)]
        tm = compute_per_tile_tp_fp_fn(sub, gate_ref, bounds,
                                       buffer_metres=BUFFER_M)
        triple = (int(tm["tp"].sum()), int(tm["fp"].sum()),
                  int(tm["fn"].sum()))
        if triple != committed_counts[committed_label]:
            raise RuntimeError(
                f"mechanism gate FAILED {name}: {triple} vs committed "
                f"{committed_label} {committed_counts[committed_label]}")
        logger.info("mechanism OK %-6s == %s %s", name, committed_label,
                    triple)

    # Geometry-identity gates for the A/B carried cells vs the committed
    # S142 primary detection sets (0.01 m = 4326 round-trip tolerance).
    from scipy.spatial import cKDTree
    geometry_checks = [
        ("A-N10", "results/stride55-2026-08-27/g384_ov128_55map/"
                  "primary/verified_detections.geojson"),
        ("B-N10", "results/stride55-2026-08-27/g384_ov192_55map/"
                  "primary/verified_detections.geojson")]
    if include_g37:
        geometry_checks += [(label.removesuffix("-carried"), det)
                            for label, det, _f1 in G37_COMMITTED]
    for name, committed_det in geometry_checks:
        (pt, pk), _ = identity[name]
        g = families[name]["gdf"]
        sub = g[(g["mound_probability"] >= pt) & (g["vote_count"] >= pk)]
        com = gpd.read_file(PROJECT_ROOT / committed_det).to_crs("EPSG:32635")
        if len(sub) != len(com):
            raise RuntimeError(
                f"geometry gate FAILED {name}: {len(sub)} vs {len(com)}")
        d, _i = cKDTree(np.c_[sub.geometry.x, sub.geometry.y]).query(
            np.c_[com.geometry.x, com.geometry.y], k=1)
        if d.max() > 0.01:
            raise RuntimeError(
                f"geometry gate FAILED {name}: max NN {d.max():.4f} m")
        logger.info("geometry OK %-6s n=%d max NN %.4f m", name, len(sub),
                    d.max())

    # Sweeps (parallel over points; family frames shared via initargs).
    # --families narrows what is SWEPT and WRITTEN. Every gate above has
    # already run over every family, so the filter cannot weaken a check.
    swept = list(families)
    if args.families:
        unknown = sorted(set(args.families) - set(families))
        if unknown:
            ap.error(f"unknown famil{'y' if len(unknown) == 1 else 'ies'}: "
                     f"{', '.join(unknown)}")
        swept = [name for name in families if name in set(args.families)]
        logger.info("FILTERED sweep: %d of %d families (%s)", len(swept),
                    len(families), ", ".join(swept))
    tasks = []
    for name in swept:
        spec = families[name]
        thresholds = sorted({0.0} | {round(float(v), 4)
                                     for v in spec["gdf"]["mound_probability"]})
        tasks.extend((name, prob_t, k)
                     for prob_t in thresholds for k in spec["ks"])
    logger.info("sweeping %d points across %d families (%d workers)",
                len(tasks), len(swept), args.workers)
    family_gdfs = {n: families[n]["gdf"] for n in swept}
    with Pool(args.workers, initializer=_init,
              initargs=(ref, bounds, family_gdfs)) as pool:
        rows = pool.map(_score, tasks, chunksize=4)

    out.mkdir(parents=True, exist_ok=True)
    # A FULL run rebuilds the record from scratch, as it always has, so a
    # family dropped from the build cannot linger. A FILTERED run merges
    # into the committed record instead — otherwise the families it did
    # not sweep would vanish from sweeps.json.
    sweeps = (load_sweeps(out / "sweeps.json", args.reference)
              if args.families
              else {"buffer_m": BUFFER_M, "reference": args.reference,
                    "families": {}})
    # Carried k is read from the manifest ON DISK, i.e. the one the PREVIOUS
    # run wrote: a full run rebuilds the manifest below, and the carried cells
    # it will write are the same points it reads here (the identity table and
    # the post-hoc carry-forward), so the record cannot depend on its own
    # output. A board with no manifest yet simply records "no carried k".
    carried_k = carried_k_by_family(out / "cells_manifest.json")
    for name in swept:
        frows = sorted((r for r in rows if r["family"] == name),
                       key=lambda r: -r["micro_f1_50"])
        with (out / f"sweep_{name}.csv").open("w", newline="") as fh:
            w = csvmod.DictWriter(fh, fieldnames=list(frows[0].keys()))
            w.writeheader()
            w.writerows(sorted(frows, key=lambda r: (r["prob_t"],
                                                     r["min_votes"])))
        best = frows[0]
        mcc_best = mcc_argmax(frows)
        sweeps["families"][name] = {
            "n_sweep_points": len(frows), "argmax": best, "top3": frows[:3],
            "mcc_argmax": mcc_best,
            **carried_k_record(frows, carried_k.get(name))}
        logger.info("%-6s oracle: micro %.4f at (%.2f, k%d) | runners: %s",
                    name, best["micro_f1_50"], best["prob_t"],
                    best["min_votes"],
                    ", ".join(f"{r['micro_f1_50']:.4f}@({r['prob_t']:.2f},"
                              f"k{r['min_votes']})" for r in frows[1:3]))
        if mcc_best is not None:
            logger.info("%-6s MCC optimum (unconstrained, superseded): %.4f "
                        "at (%.2f, k%d), micro %.4f", name,
                        mcc_best["tile_mcc"], mcc_best["prob_t"],
                        mcc_best["min_votes"], mcc_best["micro_f1_50"])
        at_k = sweeps["families"][name]["mcc_argmax_at_carried_k"]
        if at_k is not None:
            logger.info("%-6s MCC oracle (carried k%d): %.4f at (%.2f, k%d), "
                        "micro %.4f", name,
                        sweeps["families"][name]["carried_k"],
                        at_k["tile_mcc"], at_k["prob_t"], at_k["min_votes"],
                        at_k["micro_f1_50"])
        else:
            logger.info("%-6s MCC oracle: %s", name, NO_CARRIED_K)
    stamp_record(sweeps)

    if args.families:
        # A filtered run writes the sweep RECORD only. Materialising here
        # would rebuild cells_manifest.json from the swept families alone
        # and silently drop every cell of the families it skipped — the
        # 2026-09-13 manifest defect, in a new guise.
        (out / "sweeps.json").write_text(json.dumps(sweeps, indent=2) + "\n")
        logger.info("FILTERED STAGE 1 COMPLETE: %d famil%s re-swept; "
                    "sweeps.json merged, no cell written and "
                    "cells_manifest.json untouched", len(swept),
                    "y" if len(swept) == 1 else "ies")
        return 0

    # Cells manifest: committed carried incumbents + materialised new cells.
    manifest_cells: list[dict] = [
        {"label": label, "det": det, "basis": "carried",
         "point": "(0.15, k4)", "committed_eval": True}
        for label, det in COMMITTED_CARRIED]

    def materialise(name: str, label: str, basis: str,
                    pt: float, pk: int) -> None:
        g = families[name]["gdf"]
        sub = g[(g["mound_probability"] >= pt) & (g["vote_count"] >= pk)]
        dest = out / "cells" / label / "detections.geojson"
        dest.parent.mkdir(parents=True, exist_ok=True)
        sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
        manifest_cells.append({
            "label": label, "det": str(dest.relative_to(PROJECT_ROOT)),
            "basis": basis, "point": f"({pt:.2f}, k{pk})",
            "committed_eval": False})

    for name in families:
        best = sweeps["families"][name]["argmax"]
        materialise(name, f"{name}-oracle",
                    f"oracle ({args.reference}-reference argmax)",
                    best["prob_t"], best["min_votes"])
        if name in ("A-N10", "B-N10", "A-N5", "B-N5") or name in G37_IDENTITY:
            (pt, pk), _ = identity[name]
            materialise(name, f"{name}-carried", "carried", pt, pk)

    (out / "sweeps.json").write_text(json.dumps(sweeps, indent=2) + "\n")
    # Carry forward EVERY committed cell this stage does not produce. Stage 1
    # builds the oracle and carried cells only; other steps append their own —
    # the emergent GS-carried N = 3 cells from scripts/final_board_n3_carried.py
    # (step 4c, PI direction 2026-08-28), the carried analogues and the tile-MCC
    # cells from scripts/final_board_posthoc_cells.py — and rebuilding the
    # manifest from this run alone silently DROPPED them, which would have
    # shrunk the board on any regeneration. Found 2026-09-13 while adding the
    # fourth cell's N = 5 rung.
    #
    # The match used to be the substring "post-hoc", which every basis then in
    # use happened to contain. That made the guard depend on a WORD rather than
    # on the fact that matters, and the PI ruling of 2026-09-21 broke it: it
    # re-labelled twenty cells to bases naming the tile-presence presentation,
    # none of which says "post-hoc". Carrying forward anything unproduced is
    # the invariant that was always meant; matched on label, so a cell this run
    # does produce is not duplicated.
    manifest_path = out / "cells_manifest.json"
    carried_over: list[str] = []
    if manifest_path.is_file():
        produced = {c["label"] for c in manifest_cells}
        prior = json.loads(manifest_path.read_text()).get("cells", [])
        for cell in prior:
            if cell["label"] not in produced:
                manifest_cells.append(cell)
                carried_over.append(cell["label"])
    if carried_over:
        logger.info("carried forward %d committed cell(s) this stage does not "
                    "produce: %s", len(carried_over), ", ".join(carried_over))
    manifest_path.write_text(
        json.dumps({"cells": manifest_cells}, indent=2) + "\n")
    logger.info("STAGE 1 COMPLETE: %d cells in the manifest",
                len(manifest_cells))
    return 0


if __name__ == "__main__":
    sys.exit(main())
