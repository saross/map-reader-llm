#!/usr/bin/env python3
# ============================================================================
# mcc_tiering_55map.py
# ----------------------------------------------------------------------------
# Session 114: alternate-metric (tile-MCC) permutation tiering for the
# 55-map canonical board (Shawn-requested 2026-06-13: "run the alternate
# metric permutation, I would like CIs").
#
# The metric-led boards (results/metric-leaderboards/55map-canonical-50m.md)
# rank the eight canonical-GT cells by tile-MCC but carry no statistics —
# the board header notes "alternate-metric permutation tiering is available
# on demand (same tile-swap machinery)". This script supplies it:
#
#   1. Rebuild each cell's PER-TILE binary classification (has_detections
#      vs has_mounds) exactly as the Track-2 engine computed it: the
#      detections' own `source_tile` property, reference = canonical
#      extended GT at R = 50 m (reviewed students + phantoms gated <= 50 m
#      via the engine's build_phantom_gdf / build_extended_gt), tile truth
#      by geometric intersection, all in EPSG:32635.
#   2. GATE (exact): each cell's rebuilt confusion matrix (tp/tn/fp/fn)
#      must EQUAL the committed Track-2 summary.json tile_classification
#      at 50 m. Any mismatch aborts.
#   3. Round-robin pairwise tile-swap permutation on the MCC statistic
#      (10k perms, seed 42, two-sided — mirrors the F1 board's
#      permutation_test_float conventions: probability-0.5 per-tile swap,
#      numpy default_rng stream, p = mean(|null| >= |observed|)),
#      then BH-FDR q = 0.05 and greedy-clique tiers (machinery imported
#      VERBATIM from the F1 boards).
#   4. Bootstrap CIs are NOT recomputed: the Track-2 engine already wrote
#      BCa MCC CIs (summary.json tile_classification.mcc_CI); they are
#      carried through to the outputs.
#
# TILE JOINS (Wave 1, PI rulings D72 and D73; 2026-11-18):
#   --tile-join  the CLASSIFICATION join of every cell's truth and prediction
#                vectors (default ``sheet-contains``). Two computations, in
#                order: each cell's committed confusion is first rebuilt
#                under the join its record names (Track-2 ``summary.json``
#                records none: the legacy ``id``; an r2 ``evaluation.json``
#                is read by ``lib_advanced_metrics.recorded_tile_joins``) and
#                gated exactly as before; then the vectors, MCC,
#                sensitivity, specificity and ranks are computed under the
#                requested join. Where the two differ the committed BCa
#                interval belongs to the recorded join and is NOT carried
#                (``mcc_ci`` null, ``mcc_ci_status`` says why), and the
#                output name gains ``-<join>`` unless the join is the default.
#   No count-table option: this board reads no per-tile count table (MCC
#   only; F1 intervals are not recomputed here), and an option that did
#   nothing would misdescribe the output. ``tile_joins.count_table`` is null.
#
# OUTPUTS: results/metric-leaderboards/55map-mcc-tiering.{json,md}
# COST: $0 (on-disk re-analysis). Run on zbook (sapphire in use, S114).
#
# Usage:
#   .venv/bin/python scripts/mcc_tiering_55map.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-13 | Apache 2.0
# ============================================================================
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.build_55map_leaderboard import r2_gt  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    TILE_JOIN_CLASSIFICATION_DEFAULT,
    TILE_JOIN_LEGACY_CLASSIFICATION,
    TILE_JOIN_RULINGS,
    TILE_JOINS_CLASSIFICATION,
    calculate_tile_classification,
    recorded_tile_joins,
)
from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    ATTRIBUTION_RESOLUTION_NOTE,
    DEFAULT_CRS,
    PAIRED_CI_NOTE,
    R2_ATTRIBUTION_NOTE,
    STANDARDISED_ATTRIBUTION_NOTE,
    build_extended_gt,
    build_phantom_gdf,
    load_standardised_extension,
)
from scripts.n1_baseline_leaderboard_tiering import greedy_clique_tiers  # noqa: E402

BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
STUDENT_GT = BASE_DIR / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
TRACK2 = BASE_DIR / "results/55maps-extended-gt-2026-06-07"
TRACK2_STD = BASE_DIR / "results/55maps-standardised-ref-2026-08-14"
#: Reference revision r2 scoring home (card planning/reference-revision-
#: 2026-09-06.md). Its cells are scored by evaluate_detections.py (the IM-k4
#: template, one engine for the whole r2 chain), so they carry an
#: evaluation.json rather than a Track-2 summary.json; _load_cell_inputs
#: reads either.
TRACK2_R2 = BASE_DIR / "results/55maps-r2-ref-2026-09-06"
REVIEW_YESTERDAY = TRACK2 / "empty-yesterday-review.csv"
CANONICAL_REVIEW = (
    BASE_DIR / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv"
)
STD_DIR = BASE_DIR / "results/deployment-oracle-2026-06-06/canonical-gt/standardised"
STUDENT_STD = STD_DIR / "student-mounds-55maps-standardised.geojson"
EXTENSION_STD = STD_DIR / "extension-mounds-standardised.csv"
OUT_DIR = BASE_DIR / "results/metric-leaderboards"
BUFFER_M = 50
N_PERMUTATIONS = 10_000
SEED = 42

# Display name -> Track-2 evaluation directory (the eight canonical cells,
# matching results/metric-leaderboards/55map-canonical-50m.md). Detections
# paths are taken from each cell's OWN summary.json provenance block, so the
# permutation consumes exactly the files the committed evaluations scored.
CELLS = {
    "IM-k3": "IM-k3",
    "T03-k3 (oracle)": "T03-k3",
    "T03-k4": "T03-k4",
    "TH7-k3": "TH7-k3",
    "TH7-k4 (carry-forward)": "TH7-k4",
    "TM-k3": "TM-k3",
    "TM-k4": "TM-k4",
    "TM-n10-k5 (uplift)": "TM-n10-k5",
}


def mcc_from_confusion(
    tp: np.ndarray | float,
    tn: np.ndarray | float,
    fp: np.ndarray | float,
    fn: np.ndarray | float,
) -> np.ndarray | float:
    """Matthews correlation coefficient from confusion counts.

    Mirrors ``lib_advanced_metrics.calculate_tile_classification``:
    MCC = (TP*TN - FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)), with 0.0
    where the denominator is zero (the vectorised analogue of its
    ``None`` edge case — a zero row/column sum cannot occur on this
    board, so the substitution is inert here).

    Args:
        tp, tn, fp, fn: Confusion counts (scalars or aligned arrays).

    Returns:
        MCC value(s), same shape as the inputs.
    """
    tp = np.asarray(tp, dtype=float)
    tn = np.asarray(tn, dtype=float)
    fp = np.asarray(fp, dtype=float)
    fn = np.asarray(fn, dtype=float)
    numerator = tp * tn - fp * fn
    denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    out = np.divide(
        numerator, np.sqrt(denom), out=np.zeros_like(numerator), where=denom > 0
    )
    return float(out) if out.ndim == 0 else out


def tile_vectors(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_join: str = TILE_JOIN_CLASSIFICATION_DEFAULT,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Per-tile truth and prediction vectors for tile classification.

    Vectorised equivalent of the per-tile loop in
    ``lib_advanced_metrics.calculate_tile_classification``: a tile is
    TRUE if any reference point belongs to it and PREDICTED if any
    detection does. Both sides now go through
    ``lib_advanced_metrics.assign_points_to_tiles`` so this function
    cannot drift from the scorer's rule — it used to carry its own copy of
    the string join (``pred`` from ``source_tile`` names, ``truth`` from
    geometry), which is the 2026-09-12 name-versus-geometry defect.
    Equivalence with the scorer is pinned by a tier-1 test and by the
    exact confusion-matrix gate in ``main``.

    Args:
        gdf_det: Detections with a ``source_tile`` column (required by the
            ``id`` join only).
        gdf_ref: Reference (ground-truth) points, same CRS as bounds.
        gdf_bounds: Tile boundary polygons with ``tile_name``.
        tile_join: One of ``lib_advanced_metrics.TILE_JOINS_CLASSIFICATION``.

    Returns:
        (tile_names, truth, pred) — names in bounds order, two aligned
        boolean arrays.

    Raises:
        ValueError: on duplicate tile names, or when the tile join is
            refused for this frame (a point inside the frame booked to no
            tile), so a mislabelled prediction vector cannot be tiered.
    """
    tiles = list(gdf_bounds["tile_name"].unique())
    if len(tiles) != len(gdf_bounds):
        raise ValueError("duplicate tile_name rows in bounds — loop/sjoin semantics differ")
    index = {t: i for i, t in enumerate(tiles)}

    classification = calculate_tile_classification(
        gdf_det, gdf_ref, gdf_bounds, tile_join=tile_join,
    )
    if "error" in classification:
        raise ValueError(
            f"tile vectors refused ({classification.get('reason')}): "
            f"{classification['error']}"
        )

    truth = np.zeros(len(tiles), dtype=bool)
    pred = np.zeros(len(tiles), dtype=bool)
    for detail in classification["tile_details"]:
        i = index.get(detail["tile_name"])
        if i is None:
            continue
        truth[i] = bool(detail["has_mounds"])
        pred[i] = bool(detail["has_detections"])
    return tiles, truth, pred


def permutation_test_mcc(
    pred_a: np.ndarray,
    pred_b: np.ndarray,
    truth: np.ndarray,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict:
    """Paired tile-swap permutation test on the tile-MCC statistic.

    Mirrors ``n1_baseline_leaderboard_tiering.permutation_test_float``
    exactly — the probability-0.5 per-tile label swap, the
    ``numpy.random.default_rng(seed)`` stream, and the two-sided
    p = mean(|null| >= |observed|) — but the statistic is tile-level MCC
    rather than micro-F1. Truth labels are fixed per tile; the swap
    exchanges the two cells' predictions tile-by-tile.

    Args:
        pred_a: Cell A per-tile boolean predictions.
        pred_b: Cell B per-tile boolean predictions.
        truth: Per-tile boolean ground-truth labels (shared).
        n_permutations: Number of permutation iterations.
        seed: Random seed for reproducibility.

    Returns:
        Dict with ``mcc_a``, ``mcc_b``, ``observed_diff``, ``p_value``,
        ``n_permutations``, ``n_tiles``, and null-distribution stats.
    """
    def _mcc(pred: np.ndarray) -> float | np.ndarray:
        """MCC of prediction vector(s) against the shared truth."""
        tp = (pred & truth).sum(axis=-1)
        fp = (pred & ~truth).sum(axis=-1)
        fn = (~pred & truth).sum(axis=-1)
        tn = (~pred & ~truth).sum(axis=-1)
        return mcc_from_confusion(tp, tn, fp, fn)

    mcc_a = float(_mcc(pred_a))
    mcc_b = float(_mcc(pred_b))
    observed_diff = mcc_a - mcc_b

    rng = np.random.default_rng(seed)
    swap = rng.random((n_permutations, len(truth))) < 0.5
    perm_a = np.where(swap, pred_b[None, :], pred_a[None, :])
    perm_b = np.where(swap, pred_a[None, :], pred_b[None, :])
    null_diffs = _mcc(perm_a) - _mcc(perm_b)
    p_value = float(np.mean(np.abs(null_diffs) >= abs(observed_diff)))

    return {
        "mcc_a": round(mcc_a, 6),
        "mcc_b": round(mcc_b, 6),
        "observed_diff": round(observed_diff, 6),
        "p_value": round(p_value, 4),
        "n_permutations": n_permutations,
        "n_tiles": int(len(truth)),
        "null_mean": round(float(np.mean(null_diffs)), 6),
        "null_std": round(float(np.std(null_diffs)), 6),
    }


def rank_by_mcc(cells: list[dict]) -> list[dict]:
    """Cells in descending MCC, an undefined MCC (E81) after every defined one.

    Args:
        cells: Dicts with an ``mcc`` value (float or ``None``).

    Returns:
        A new list, best first.

    Example:
        >>> [c["mcc"] for c in rank_by_mcc([{"mcc": None}, {"mcc": 0.2}, {"mcc": 0.5}])]
        [0.5, 0.2, None]
    """
    return sorted(cells, key=lambda c: (c["mcc"] is None, -(c["mcc"] or 0.0)))


#: The first ``compute_corrected_f1_multi_buffer.py`` output version that
#: records its tile joins (Wave 1); a file at or above it that records none
#: is refused, never read as the legacy ``id`` (re-audit Low).
TRACK2_JOINS_VERSION = (1, 1, 0)


def _track2_recorded_join(summary: dict, row: dict) -> str:
    """The classification join a Track-2 ``summary.json`` row was built under.

    Wave 1 made ``compute_corrected_f1_multi_buffer.py`` record it twice: in
    each row's ``tile_classification.tile_join`` and in
    ``metadata.tile_joins.classification``. A file that records neither is
    historical and was built under the legacy ``id``; two records that
    disagree are refused (audit A-M2).

    Args:
        summary: The parsed ``summary.json``.
        row: The row the board reads (``R_m == BUFFER_M``).

    Returns:
        The recorded classification join.

    Raises:
        ValueError: On contradictory records, or a name that is not a
            classification join.
    """
    records = {
        (row.get("tile_classification") or {}).get("tile_join"),
        ((summary.get("metadata") or {}).get("tile_joins") or {}).get("classification"),
    } - {None}
    if len(records) > 1:
        raise ValueError(f"summary.json records contradictory classification joins "
                         f"{sorted(records)}")
    if not records:
        try:
            version = tuple(int(x) for x in str(summary.get("version") or "0").split("."))
        except ValueError:
            version = (0,)
        if version >= TRACK2_JOINS_VERSION:
            raise ValueError(f"summary.json version {summary.get('version')} must "
                             f"record its classification join, and records none")
    join = records.pop() if records else TILE_JOIN_LEGACY_CLASSIFICATION
    if join not in TILE_JOINS_CLASSIFICATION:
        raise ValueError(f"summary.json records {join!r}, not a classification join")
    return join


def _load_cell_inputs(track2_dir: Path) -> tuple[gpd.GeoDataFrame, dict]:
    """Load one cell's detections (engine CRS handling) and its committed
    50 m tile_classification block (the gate target + the BCa CI source).

    Args:
        track2_dir: The cell's Track-2 evaluation directory.

    Returns:
        (gdf_det reprojected to the engine CRS, tile_classification dict).
        The dict carries ``recorded_tile_join``: the classification join the
        committed block was built under (a Track-2 ``summary.json`` records
        none, so the legacy ``id``).
    """
    if (track2_dir / "summary.json").exists():
        summary = json.loads((track2_dir / "summary.json").read_text())
        det_path = summary["metadata"]["input_paths"]["detections"]
        # Provenance paths were recorded absolute on the scoring host;
        # relativise against this repo checkout.
        rel = det_path.split("map-reader-llm/", 1)[1]
        row50 = next(r for r in summary["results"] if r["R_m"] == BUFFER_M)
        tile = {**row50["tile_classification"],
                "recorded_tile_join": _track2_recorded_join(summary, row50)}
    else:
        # evaluate_detections.py shape (the r2 chain's single engine): the
        # tile block nests point + BCa interval per metric; flatten it to
        # the Track-2 keys the gate and the board read.
        ev = json.loads((track2_dir / "evaluation.json").read_text())
        rel = ev["_metadata"]["input_files"]["detections"][0]
        tc = ev["summary"]["tile_classification"]
        tile = {**tc["confusion"],
                "mcc": tc["mcc"]["point"],
                "mcc_CI": [tc["mcc"]["ci_lower"], tc["mcc"]["ci_upper"]],
                "sensitivity": tc["sensitivity"]["point"],
                "specificity": tc["specificity"]["point"],
                "recorded_tile_join": recorded_tile_joins(ev)["classification"]}
    gdf_det = gpd.read_file(BASE_DIR / rel)
    if gdf_det.crs is None:
        gdf_det = gdf_det.set_crs("EPSG:4326")
    gdf_det = gdf_det.to_crs(DEFAULT_CRS)
    return gdf_det, tile


#: Cardinal numbers spelled out for the board's prose. Anything larger
#: falls back to digits — a board of thirteen cells should read "13",
#: not silently keep saying "eight".
_NUMBER_WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
    12: "twelve",
}


def count_word(n: int) -> str:
    """Spell a small cardinal for prose; fall back to digits.

    Args:
        n: The count to render.

    Returns:
        ``"eight"`` for 8, ``"13"`` for 13.
    """
    return _NUMBER_WORDS.get(n, str(n))


def _fmt3(value: float | None) -> str:
    """Three decimals, or ``undefined`` for a null rate (erratum E81)."""
    return "undefined" if value is None else f"{value:.3f}"


def render_md(out: dict) -> str:
    """Render the board markdown from the results dict (== the committed JSON).

    Kept separate from the compute path so the citable document can be
    regenerated verbatim — e.g. after a methodological note is revised — without
    re-running the permutation tests. ``main(rebuild_md_only=True)`` uses this
    against the committed ``55map-mcc-tiering.json``.

    Args:
        out: The results mapping written to ``55map-mcc-tiering.json``. Must
            carry ``cells`` (tier-annotated, MCC-descending), ``pairwise``,
            ``tiers``, ``n_significant``, ``n_pairs``, ``n_permutations`` and
            ``seed``.

    Returns:
        The full markdown document as a single string (no trailing newline).

    Example:
        >>> doc = render_md(json.loads(Path("55map-mcc-tiering.json").read_text()))
        >>> doc.splitlines()[0]
        '# 55-map canonical board — tile-MCC permutation tiering @ 50 m'
    """
    n_sig, n_pairs = out["n_significant"], out["n_pairs"]
    reference = out.get("reference", "canonical")
    standardised = reference == "standardised"
    is_r2 = reference == "r2"
    # Board size and gate tally are DERIVED, never asserted. Both used to
    # be the fixed strings "the eight" and "(8/8)", so adding or removing
    # a cell in CELLS would have left the committed board claiming a
    # verification it never performed (defect D37, audit finding F17d).
    # ``gate_cells_*`` are written by the compute path; a JSON from an
    # older vintage (``--rebuild-md``) falls back to the cell list, every
    # member of which passed the gate — the compute path exits on the
    # first failure, so a cell in ``cells`` is a cell that reproduced.
    n_cells = len(out["cells"])
    gate_verified = out.get("gate_cells_verified", n_cells)
    gate_total = out.get("gate_cells_total", n_cells)
    title = {
        "r2": "# 55-map board, reference r2 — tile-MCC permutation tiering",
        "standardised": "# 55-map standardised board — tile-MCC permutation tiering",
    }.get(reference, "# 55-map canonical board — tile-MCC permutation tiering @ 50 m")
    cells_desc = {
        "r2": ("reference-r2 cells (MCC is buffer-invariant on this "
               "reference)"),
        "standardised": ("standardised-reference cells (MCC is buffer-invariant "
                         "on this reference)"),
    }.get(reference, "canonical-GT cells")
    ci_engine = "scoring" if (standardised or is_r2) else "Track-2"
    ci_file = "`evaluation.json`" if is_r2 else "`summary.json`"
    md = [
        title,
        "",
        f"> Alternate-metric (tile-MCC) statistical tiering for the"
        f" {count_word(n_cells)}"
        f" {cells_desc}: round-robin tile-swap permutation on the MCC"
        f" statistic ({out['n_permutations'] // 1000}k, seed {out['seed']},"
        " two-sided) + BH-FDR q=0.05 + greedy-clique tiers — the same machinery"
        f" as the F1-led board. {n_sig}/{n_pairs} pairs significant ->"
        f" {len(out['tiers'])} tier(s). 95% CIs are the "
        f"{ci_engine} engine's BCa"
        f" bootstrap CIs, carried from {ci_file}. Gate: rebuilt"
        " per-tile confusion matrices reproduce the committed evaluations"
        f" exactly ({gate_verified}/{gate_total}).",
        "",
        "| rank | cell | tier | MCC | 95% CI | sens | spec | tp/fp/fn/tn |",
        "|---:|---|---:|---:|---|---:|---:|---|",
    ]
    for i, c in enumerate(out["cells"], 1):
        lo, hi = c["mcc_ci"] if c["mcc_ci"] else (None, None)
        ci = f"[{lo:.3f}, {hi:.3f}]" if lo is not None else "—"
        cf = c["confusion"]
        md.append(
            f"| {i} | {c['name']} | {c['tier']} | "
            f"{'undefined' if c['mcc'] is None else format(c['mcc'], '.4f')} | {ci} "
            f"| {_fmt3(c['sensitivity'])} | {_fmt3(c['specificity'])} "
            f"| {cf['tp']}/{cf['fp']}/{cf['fn']}/{cf['tn']} |")
    md += ["", "## Reading this board", "", PAIRED_CI_NOTE, "",
           (R2_ATTRIBUTION_NOTE if is_r2
            else STANDARDISED_ATTRIBUTION_NOTE if standardised
            else ATTRIBUTION_RESOLUTION_NOTE), "",
           "## Pairwise (BH-adjusted)", "",
           "| pair | ΔMCC | p | BH p | sig |", "|---|---:|---:|---:|---|"]
    for p in sorted(out["pairwise"], key=lambda x: x["bh_adjusted_p"]):
        md.append(f"| {p['a']} vs {p['b']} | {p['observed_diff']:+.4f} "
                  f"| {p['p_value']:.4f} | {p['bh_adjusted_p']:.4f} "
                  f"| {'yes' if p['significant'] else 'ns'} |")
    return "\n".join(md)


def main(rebuild_md_only: bool = False, reference: str = "canonical",
         force_r1: bool = False,
         tile_join: str = TILE_JOIN_CLASSIFICATION_DEFAULT,
         overwrite_other_joins: bool = False) -> int:
    """Build the 55-map tile-MCC permutation tiering.

    Args:
        rebuild_md_only: When True, skip all computation and re-render the
            markdown from the committed JSON. Used to refresh prose in the
            citable document without disturbing any number.
        reference: ``canonical`` (legacy ring-gated pairing, default —
            unchanged behaviour) or ``standardised`` (ruling-21 layers,
            queue item 5; separate ``-standardised`` output files, cells
            read from ``results/55maps-standardised-ref-2026-08-14/``), or
            ``r2`` (reference revision r2; ``-r2`` outputs, cells read from
            ``results/55maps-r2-ref-2026-09-06/``).
        tile_join: The classification join every analysed value is
            computed under (see the header's TILE JOINS).
        overwrite_other_joins: Allow replacing an existing board that
            records another classification join (audit A-L5).
    """
    if tile_join not in TILE_JOINS_CLASSIFICATION:
        raise ValueError(f"tile_join must be one of {TILE_JOINS_CLASSIFICATION!r}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    standardised = reference == "standardised"
    is_r2 = reference == "r2"
    stem = {"standardised": "55map-mcc-tiering-standardised",
            "r2": "55map-mcc-tiering-r2"}.get(reference, "55map-mcc-tiering")
    if tile_join != TILE_JOIN_CLASSIFICATION_DEFAULT:
        stem += f"-{tile_join}"
    if reference != "r2" and not rebuild_md_only and not force_r1 \
            and (OUT_DIR / f"{stem}.json").exists():
        sys.exit(f"{OUT_DIR.relative_to(BASE_DIR)}/{stem}.json is a committed r1 "
                 f"board; refusing to rewrite it (H15). Use --reference r2, "
                 f"--rebuild-md, or --force-r1.")

    out_json = OUT_DIR / f"{stem}.json"
    if not rebuild_md_only and not overwrite_other_joins and out_json.exists():
        # Audit A-L5: never replace a committed board built under another
        # classification join as a side effect of a default run.
        recorded = (json.loads(out_json.read_text()).get("tile_joins") or {}).get(
            "classification") or TILE_JOIN_LEGACY_CLASSIFICATION
        if recorded != tile_join:
            sys.exit(f"{out_json.relative_to(BASE_DIR)} records classification join "
                     f"{recorded!r}, not {tile_join!r}; refusing to overwrite it. "
                     f"Pass --overwrite-other-joins to replace it deliberately.")

    if rebuild_md_only:
        src = OUT_DIR / f"{stem}.json"
        out = json.loads(src.read_text())
        (OUT_DIR / f"{stem}.md").write_text(render_md(out) + "\n")
        print(f"rebuilt {OUT_DIR.relative_to(BASE_DIR)}/{stem}.md "
              f"from {src.name} (no recomputation)", flush=True)
        return 0

    gdf_bounds = gpd.read_file(BOUNDS)
    if gdf_bounds.crs is None:
        gdf_bounds = gdf_bounds.set_crs("EPSG:4326")
    gdf_bounds = gdf_bounds.to_crs(DEFAULT_CRS)

    if is_r2:
        gdf_ref = r2_gt()
        print(f"r2 reference (buffer-invariant): {len(gdf_ref)} points; "
              f"{len(gdf_bounds)} tiles", flush=True)
    elif standardised:
        gdf_student = gpd.read_file(STUDENT_STD).to_crs(DEFAULT_CRS)
        gdf_phantoms = load_standardised_extension(
            EXTENSION_STD, crs=DEFAULT_CRS,
        )
        gdf_ref = build_extended_gt(gdf_student, gdf_phantoms)
        if gdf_ref.attrs.get("n_phantom_duplicates_dropped", 0) != 0:
            sys.exit("GATE FAIL: standardised reference dropped extension "
                     "records in de-duplication — layer drift")
        print(f"standardised reference (buffer-invariant): {len(gdf_ref)} "
              f"points ({len(gdf_student)} students + "
              f"{len(gdf_phantoms)} extension); "
              f"{len(gdf_bounds)} tiles", flush=True)
    else:
        gdf_student = gpd.read_file(STUDENT_GT).to_crs(DEFAULT_CRS)
        review_y = pd.read_csv(REVIEW_YESTERDAY)
        review_t = pd.read_csv(CANONICAL_REVIEW)
        gdf_phantoms = build_phantom_gdf(
            review_y, review_t, BUFFER_M, crs=DEFAULT_CRS,
        )
        gdf_ref = build_extended_gt(gdf_student, gdf_phantoms)
        print(f"extended GT at {BUFFER_M} m: {len(gdf_ref)} points "
              f"({len(gdf_student)} students + {len(gdf_phantoms)} phantoms); "
              f"{len(gdf_bounds)} tiles", flush=True)

    cell_base = {"standardised": TRACK2_STD, "r2": TRACK2_R2}.get(reference, TRACK2)
    cells: list[dict] = []
    # Names whose rebuilt confusion matrix matched the committed one.
    # Counted rather than assumed: the gate verdict published in the JSON
    # and the markdown is derived from this list and from ``CELLS``, so
    # the claim cannot decouple from the cell set (D37 / F17d).
    gate_verified: list[str] = []
    truth: np.ndarray | None = None
    for name, dirname in CELLS.items():
        gdf_det, committed = _load_cell_inputs(cell_base / dirname)
        recorded_join = committed["recorded_tile_join"]
        # Step 1: rebuild the committed confusion under ITS join and gate it.
        tiles, rec_truth, rec_pred = tile_vectors(
            gdf_det, gdf_ref, gdf_bounds, tile_join=recorded_join)
        rec_confusion = {
            "tp": int((rec_pred & rec_truth).sum()),
            "tn": int((~rec_pred & ~rec_truth).sum()),
            "fp": int((rec_pred & ~rec_truth).sum()),
            "fn": int((~rec_pred & rec_truth).sum()),
        }
        committed_counts = {k: committed[k] for k in ("tp", "tn", "fp", "fn")}
        if rec_confusion != committed_counts:
            sys.exit(f"GATE FAIL: {name} rebuilt confusion under the recorded "
                     f"join '{recorded_join}' {rec_confusion} != committed "
                     f"{committed_counts}")
        # Step 2: every analysed value under the requested join.
        same_join = recorded_join == tile_join
        if same_join:
            cell_truth, pred = rec_truth, rec_pred
        else:
            tiles, cell_truth, pred = tile_vectors(
                gdf_det, gdf_ref, gdf_bounds, tile_join=tile_join)
        if truth is None:
            truth = cell_truth
        elif not np.array_equal(truth, cell_truth):
            sys.exit("GATE FAIL: truth vector differs between cells")
        confusion = {
            "tp": int((pred & truth).sum()), "tn": int((~pred & ~truth).sum()),
            "fp": int((pred & ~truth).sum()), "fn": int((~pred & truth).sum()),
        }
        print(f"  {name:<24} rebuilt under '{recorded_join}' == committed ok; "
              f"under '{tile_join}' {confusion}", flush=True)
        gate_verified.append(name)
        if same_join:
            mcc, sens, spec = (committed["mcc"], committed["sensitivity"],
                               committed["specificity"])
        else:
            tp_, tn_, fp_, fn_ = (confusion[k] for k in ("tp", "tn", "fp", "fn"))
            # Erratum E81 (audit A-L2): a degenerate confusion has no MCC; it
            # is null, never the 0.0 ``mcc_from_confusion`` substitutes.
            degenerate = (tp_ + fp_) * (tp_ + fn_) * (tn_ + fp_) * (tn_ + fn_) == 0
            mcc = (None if degenerate
                   else round(float(mcc_from_confusion(tp_, tn_, fp_, fn_)), 4))
            sens = round(tp_ / (tp_ + fn_), 4) if tp_ + fn_ else None
            spec = round(tn_ / (tn_ + fp_), 4) if tn_ + fp_ else None
        cell = {
            "name": name,
            "condition_dir": str((cell_base / dirname).relative_to(BASE_DIR)),
            "mcc": mcc,
            # The committed interval is the recorded join's; it is never
            # carried beside values computed under another join.
            "mcc_ci": committed.get("mcc_CI") if same_join else None,
            "sensitivity": sens,
            "specificity": spec,
            "confusion": confusion,
            "recorded_tile_join": recorded_join,
            "pred": pred,
        }
        if not same_join:
            cell["mcc_ci_status"] = (
                f"not carried: the committed interval is under '{recorded_join}', "
                f"the values here under '{tile_join}'; not recomputed by this board")
        cells.append(cell)

    assert truth is not None
    print(f"\n=== round-robin ({len(cells)} cells, {N_PERMUTATIONS // 1000}k "
          f"tile-swap on MCC, seed {SEED}) ===", flush=True)
    pairs, significant = [], {}
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            a, b = cells[i], cells[j]
            r = permutation_test_mcc(a["pred"], b["pred"], truth)
            pairs.append({"a": a["name"], "b": b["name"], **r})
    adjusted = apply_bh_correction([p["p_value"] for p in pairs], q=0.05)
    for p, adj in zip(pairs, adjusted):
        p["bh_adjusted_p"] = round(adj, 6)
        p["significant"] = bool(adj < 0.05)
        significant[frozenset({p["a"], p["b"]})] = p["significant"]

    ordered = rank_by_mcc(cells)
    tiers = greedy_clique_tiers([c["name"] for c in ordered], significant)
    tier_of = {n: t for t, members in enumerate(tiers, 1) for n in members}
    n_sig = sum(1 for p in pairs if p["significant"])
    print(f"{n_sig}/{len(pairs)} pairs significant -> {len(tiers)} tier(s)", flush=True)

    out = {
        "track": {"standardised": "55map-standardised",
                  "r2": "55map-r2"}.get(reference, "55map-canonical"),
        "reference": reference,
        "metric": "tile_mcc", "buffer_m": BUFFER_M,
        "tile_joins": {"classification": tile_join, "count_table": None,
                       "count_table_note": "this board reads no count table",
                       "rulings": TILE_JOIN_RULINGS},
        "n_tiles": int(len(truth)), "n_populated_tiles": int(truth.sum()),
        "n_permutations": N_PERMUTATIONS, "seed": SEED,
        "bh_q": 0.05, "n_significant": n_sig, "n_pairs": len(pairs),
        "ci_source": (
            ("r2-scoring evaluation.json tile_classification.mcc ci_lower/"
             "ci_upper (BCa, 10k bootstrap, seed 42 — evaluate_detections.py "
             "at scoring time)")
            if is_r2 else
            ("standardised-scoring summary.json tile_classification.mcc_CI "
             "(BCa, 10k bootstrap, seed 42 — computed by the engine at "
             "scoring time)")
            if standardised else
            ("Track-2 summary.json tile_classification.mcc_CI "
             "(BCa, 10k bootstrap, seed 42 — computed by the engine at scoring time)")
        ),
        "gate": (
            "rebuilt per-tile confusion, under each cell's recorded join, == "
            f"committed summary.json (exact), {len(gate_verified)}/{len(CELLS)}"
        ),
        "gate_cells_verified": len(gate_verified),
        "gate_cells_total": len(CELLS),
        "cells": [{k: v for k, v in c.items() if k != "pred"}
                  | {"tier": tier_of[c["name"]]} for c in ordered],
        "pairwise": pairs,
        "tiers": tiers,
    }
    (OUT_DIR / f"{stem}.json").write_text(json.dumps(out, indent=2) + "\n")

    (OUT_DIR / f"{stem}.md").write_text(render_md(out) + "\n")
    print(f"wrote {OUT_DIR.relative_to(BASE_DIR)}/{stem}.{{json,md}}",
          flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rebuild-md",
        action="store_true",
        help="Re-render the board markdown from the committed JSON without "
             "re-running the permutation tests (prose-only refresh).",
    )
    parser.add_argument(
        "--reference",
        choices=["canonical", "standardised", "r2"],
        default="canonical",
        help="Reference to tier against: canonical (legacy, default), "
             "standardised (ruling 21; writes -standardised outputs), or r2 "
             "(the 2026-09 audit revision; writes -r2 outputs, reads the r2 "
             "scoring home).",
    )
    parser.add_argument(
        "--force-r1", action="store_true",
        help="Permit rewriting a committed r1 board.",
    )
    parser.add_argument(
        "--tile-join", choices=TILE_JOINS_CLASSIFICATION,
        default=TILE_JOIN_CLASSIFICATION_DEFAULT,
        help="Classification join every analysed value is computed under "
             f"(default {TILE_JOIN_CLASSIFICATION_DEFAULT!r}); each committed "
             "confusion is first gated under its own recorded join. 'id' "
             "replays the committed boards (output name gains -id).",
    )
    parser.add_argument(
        "--overwrite-other-joins", action="store_true",
        help="Allow replacing an existing board that records another "
             "classification join (refused otherwise).",
    )
    _args = parser.parse_args()
    raise SystemExit(main(
        rebuild_md_only=_args.rebuild_md, reference=_args.reference,
        force_r1=_args.force_r1, tile_join=_args.tile_join,
        overwrite_other_joins=_args.overwrite_other_joins,
    ))
