#!/usr/bin/env python3
"""Compute buffer-stratified corrected F1 / P / R on the 55-map image set.

Methodology: **Approach B — extended-GT-at-R Hungarian matching.**

At each buffer R in {50, 75, 100, 125, 150} m this script:

1. Builds an "extended" ground truth set by adding reviewer-promoted phantom
   mounds (candidates the reviewers confirmed as real within R) to the
   student ground truth. Each phantom's geometry is the detection's
   (x, y) position — i.e., the detection *becomes* the GT point, which is
   what the reviewers confirmed as a real mound during review.
2. Runs per-map Hungarian matching at ``max_distance=R`` between the
   accepted detection pool and the extended GT (student GT scoped to
   tiles ∪ in-scope phantoms).
3. Aggregates true positive (TP), false positive (FP), and false negative
   (FN) counts across maps and derives precision, recall, and F1.
4. Computes 95 % confidence intervals (CIs) via tile-level bootstrap —
   the same resampling unit used by ``lib_advanced_metrics.bootstrap_ci``.

The 74 candidates labelled ``mound`` at today's ``>150 m`` shell (sentinel
``buffer_metres=200``) are visible mounds inside the 286 m corners-plus-5 px
circle but outside all review rings. They are EXCLUDED from every extended
GT build here; their detections therefore appear as FP at every R ≤ 150.

Context:
- Yesterday's single-buffer correction
  (``compute_corrected_f1_human_reviewed.py``) produced F1 = 0.830 at 50 m
  via an analytic adjustment to measured counts (not a Hungarian re-match).
  This script re-runs Hungarian over extended GT at each R, so the 50 m
  row should be close (±0.003) to 0.830 — the small residual reflects the
  2 today-corrections plus per-map scoping differences.
- Obs 272 in ``docs/notes/reflections/working-notes.md`` shows the
  attractor-pull effect is statistically significant only through 125 m;
  the 150 m row should therefore be reported as an upper bound, not as a
  practitioner-useful recall claim.

Usage:
    python scripts/compute_corrected_f1_multi_buffer.py \\
        --verified-detections outputs/.../verified_detections.geojson \\
        --student-gt inputs/.../student-mounds-55maps-reviewed.geojson \\
        --bounds inputs/.../55maps_evaluation_bounds.geojson \\
        --review-yesterday results/.../human-review.csv \\
        --review-today results/.../human-review-multi-buffer.csv \\
        --output-dir results/.../corrected-f1-multi-buffer \\
        [--buffers 50 75 100 125 150] \\
        [--n-bootstrap 10000] [--seed 42]

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

# Ensure we can import lib_advanced_metrics regardless of invocation CWD.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib_advanced_metrics import (  # noqa: E402  (import after sys.path tweak)
    bootstrap_tile_classification_ci,
    calculate_tile_classification,
    compute_per_tile_tp_fp_fn,
    get_map_name,
    match_detections_to_references,
    scope_references_to_tiles,
)

DEFAULT_CRS = "EPSG:32635"
DEFAULT_BUFFERS = (50, 75, 100, 125, 150)
SENTINEL_BUFFER_EXCLUDED = 200  # today's ">150 m" shell — EXCLUDE from all R
REF_MAP_COL = "source_map"  # student GT column (matches lib_advanced_metrics)

# --- Citable methodological notes emitted into generated 55-map board docs ---
# These live here, beside `build_phantom_gdf` (the function that implements the
# per-buffer gating they describe), so the prose and the behaviour cannot drift
# apart. Generated board markdowns import and emit them verbatim; do NOT
# hand-edit the rendered .md files, which are overwritten on regeneration.

ATTRIBUTION_RESOLUTION_NOTE = """\
**Attribution resolution (55-map deployment corpus).** Two distinct sources of
spatial imprecision affect this reference, and they behave differently:

1. *Student-digitised mounds* (n = 4,746) carry roughly 20–25 m of positional
   jitter — continuous error in where a recorded mound sits.
2. *Reviewer-confirmed phantoms* (n = 773 — model detections that human
   verification found to be real mounds the students had missed) carry their
   match distance only as a **25 m ring anchored at 50 m**: a mound within 50 m
   of the detection was recorded as "50 m", the next ring as "75 m", and so on.
   This error is interval-censored, not continuous.

Phantoms enter the extended ground truth only at R >= their recorded ring
(`build_phantom_gdf`): detections we cannot localise at the scoring radius are
not credited. Because the tightest available ring is 50 m, **below R = 50 m the
extended ground truth reduces to the reviewed student ground truth** — Track-2
results are distinct from Track-1 only at R >= 50 m, and sub-50 m Track-2
figures penalise correct detections of student-missed mounds. The 55-map
headline is therefore reported at 50 m, and the full 14-buffer sweep should be
read as descriptive rather than as evidence of sub-25 m precision differences.
This applies to the 55-map deployment corpus only; the gold-standard corpus
uses curator ground truth and is unaffected.

Review coverage was pooled across all four proposer configurations
(`build_canonical_gt.py` `CARRIED_RUNS`) and deduplicated by 20 m clustering,
each cluster taking the tightest ring any run achieved, so the reference is
config-agnostic. The additional k3-shell review pass covered the three text
configurations only, so any residual enrichment asymmetry favours the text
cells."""

PAIRED_CI_NOTE = """\
**Confidence intervals vs significance.** The 95% intervals in the board table
are *marginal* per-cell BCa bootstrap intervals; the significance tests are
*paired* tile-swap permutations over the same tiles. Overlapping intervals are
therefore consistent with a significant paired difference — the paired test
removes between-tile variance that the marginal intervals retain. Read the
BH-adjusted pairwise table below, not interval overlap, for significance."""


@dataclass(frozen=True)
class BufferResult:
    """Aggregated corrected-F1 statistics at a single buffer radius R."""

    buffer_metres: int
    tp: int
    fp: int
    fn: int
    n_ref_student_only: int
    n_reviewer_promoted: int
    n_ref_extended: int
    precision: float
    precision_ci: tuple[float, float]
    recall: float
    recall_ci: tuple[float, float]
    f1: float
    f1_ci: tuple[float, float]
    # --- Optional tile-level MCC block (populated only when --compute-mcc) ---
    # Tile-classification MCC against the SAME per-buffer-gated extended GT used
    # for the corrected F1 above. MCC is buffer-independent within the matching
    # step (tiles are classified by mound/detection presence), so it varies with
    # R only through the gated GT: below 50 m the extended GT == student GT, so
    # MCC equals the historical (Track-1) student-GT MCC; phantoms gate in at
    # R >= 50 m, flipping FP tiles to TP where the model found a student-missed
    # mound. All None when MCC was not requested.
    mcc: float | None = None
    mcc_ci: tuple[float, float] | None = None
    tile_tp: int | None = None
    tile_tn: int | None = None
    tile_fp: int | None = None
    tile_fn: int | None = None
    sensitivity: float | None = None
    specificity: float | None = None


def compute_point_estimate(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    """Return (precision, recall, F1) from integer counts. Safe for zero-division."""
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return p, r, f1


def build_phantom_gdf(
    review_yesterday: pd.DataFrame,
    review_today: pd.DataFrame,
    buffer_r: int,
    crs: str = DEFAULT_CRS,
) -> gpd.GeoDataFrame:
    """Build the phantom-GT GeoDataFrame at buffer R.

    Phantoms at R comprise:

    - **Yesterday's mound labels.** Every row in ``review_yesterday`` with
      ``human_label == 'mound'`` — all are at ``buffer_metres == 50``, so
      include for every R ≥ 50 m.
    - **Today's mound labels at the selected shell.** Rows in
      ``review_today`` with ``human_label == 'mound'`` AND
      ``buffer_metres <= R`` AND ``buffer_metres != 200`` (the latter
      excludes the 74 visible-but-out-of-range sentinels).

    Geometry: a point at (``x``, ``y``) in the input CRS (EPSG:32635).
    The ``source_map`` column is set from the CSV's ``map_name`` column so
    the resulting GDF plays nicely with ``lib_advanced_metrics`` helpers.

    Args:
        review_yesterday: Yesterday's 1 028-row review DataFrame.
        review_today: Today's 557-row multi-buffer review DataFrame.
        buffer_r: Buffer radius in metres.
        crs: Target CRS for the output geometries.

    Returns:
        GeoDataFrame with columns ``candidate_id``, ``source_map``,
        ``human_label``, ``buffer_metres``, ``geometry``.
    """
    # Yesterday's mounds: gate by buffer_metres <= R when the column is
    # present (multi-buffer reviews). Single-buffer reviews (all 50 m) and
    # empty reviews are unaffected at R >= 50, so the published corrected-F1
    # numbers (which used an empty or single-buffer-50 m "yesterday") are
    # unchanged. Without this gate, passing a *multi-buffer* review as
    # "yesterday" over-promotes wider-ring (>R) mounds at R = 50 — the latent
    # bug worked around in paired_permutation_corrected_55maps (which pre-gates
    # yesterday before calling this helper).
    y_all = review_yesterday[review_yesterday["human_label"] == "mound"]
    if "buffer_metres" in y_all.columns:
        y_mounds = y_all[
            (y_all["buffer_metres"] <= buffer_r)
            & (y_all["buffer_metres"] != SENTINEL_BUFFER_EXCLUDED)
        ].copy()
    else:
        y_mounds = y_all.copy()
    t_mounds = review_today[
        (review_today["human_label"] == "mound")
        & (review_today["buffer_metres"] <= buffer_r)
        & (review_today["buffer_metres"] != SENTINEL_BUFFER_EXCLUDED)
    ].copy()

    # Unify column schema
    phantoms = pd.concat([y_mounds, t_mounds], ignore_index=True)
    phantoms = phantoms.rename(columns={"map_name": REF_MAP_COL})
    geometry = [Point(row["x"], row["y"]) for _, row in phantoms.iterrows()]
    gdf = gpd.GeoDataFrame(
        phantoms[["candidate_id", REF_MAP_COL, "human_label", "buffer_metres"]],
        geometry=geometry,
        crs=crs,
    )
    return gdf


def build_extended_gt(
    gdf_student: gpd.GeoDataFrame,
    gdf_phantoms: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Concatenate student GT and phantom GT into a single extended-GT GDF.

    Only the subset of columns needed downstream (``source_map``, ``geometry``)
    is preserved, so the Hungarian helpers see a clean schema.

    Args:
        gdf_student: Student ground truth with ``source_map`` column.
        gdf_phantoms: Phantom GT built by :func:`build_phantom_gdf`.

    Returns:
        Combined GeoDataFrame with ``source_map`` and ``geometry`` columns.
    """
    s = gdf_student[[REF_MAP_COL, "geometry"]].copy()
    s["_is_phantom"] = False
    p = gdf_phantoms[[REF_MAP_COL, "geometry"]].copy()
    p["_is_phantom"] = True
    combined = pd.concat([s, p], ignore_index=True)
    return gpd.GeoDataFrame(combined, geometry="geometry", crs=gdf_student.crs)


def compute_counts_at_r(
    gdf_det: gpd.GeoDataFrame,
    gdf_ext_gt: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_r: int,
) -> tuple[int, int, int, int]:
    """Per-map Hungarian matching at max_distance=R; return aggregate counts.

    Mirrors the scoping + matching logic of
    ``lib_advanced_metrics.calculate_f1_internal`` but also returns the
    scoped-reference count so the recall denominator is explicit.

    Args:
        gdf_det: Accepted detections with ``source_tile``.
        gdf_ext_gt: Extended GT (student + phantoms), with ``source_map``.
        gdf_bounds: Tile boundary polygons with ``tile_name``.
        buffer_r: Maximum matching distance in metres.

    Returns:
        (TP, FP, FN, n_ref_scoped) totals over all processed maps.
    """
    tp = fp = fn = n_ref_scoped = 0

    processed_maps = {get_map_name(n) for n in gdf_bounds["tile_name"].unique()}
    processed_maps.discard("Unknown")

    for map_name in processed_maps:
        map_bounds = gdf_bounds[gdf_bounds["tile_name"].str.startswith(map_name)]

        ref_for_map = gdf_ext_gt[gdf_ext_gt[REF_MAP_COL] == map_name]
        if not ref_for_map.empty:
            ref_scope = scope_references_to_tiles(ref_for_map, map_bounds)
        else:
            ref_scope = ref_for_map.iloc[0:0]

        det_scope = gdf_det[gdf_det["source_tile"].str.startswith(map_name)]

        n_ref_scoped += len(ref_scope)

        if det_scope.empty and ref_scope.empty:
            continue
        if det_scope.empty:
            fn += len(ref_scope)
            continue
        if ref_scope.empty:
            fp += len(det_scope)
            continue

        det_geoms = list(det_scope.geometry)
        ref_geoms = list(ref_scope.geometry)
        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, buffer_r)
        )
        tp += len(matched_det)
        fp += len(unmatched_det)
        fn += len(unmatched_ref)

    return tp, fp, fn, n_ref_scoped


def bootstrap_tile_level_ci(
    gdf_det: gpd.GeoDataFrame,
    gdf_ext_gt: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_r: int,
    n_iterations: int,
    seed: int,
) -> dict[str, tuple[float, float]]:
    """Tile-level bootstrap CIs (95 %) for precision, recall, F1 at R.

    Delegates to ``lib_advanced_metrics.compute_per_tile_tp_fp_fn`` — the
    same function the production ``bootstrap_ci`` uses — so this matches
    the preregistered tile-resampling convention. Per-tile TP/FP/FN is
    computed *once* against the extended GT at R, then each bootstrap
    iteration resamples tiles with replacement and re-aggregates counts
    using a vectorised ``np.bincount`` dot product — ~50× faster than the
    ``aggregate_tile_metrics`` Python-loop helper at 8 500-tile scale.

    Args:
        gdf_det: Accepted detections.
        gdf_ext_gt: Extended GT (student + phantoms).
        gdf_bounds: Tile boundary polygons.
        buffer_r: Maximum matching distance in metres.
        n_iterations: Number of bootstrap iterations (e.g., 10 000).
        seed: Random seed for reproducibility.

    Returns:
        Dict keyed ``precision``, ``recall``, ``f1`` with 95 % (lo, hi) CI.
    """
    # Pre-compute per-tile counts ONCE at the extended GT for this R.
    tile_metrics = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ext_gt, gdf_bounds, buffer_metres=buffer_r,
    )

    # Align tile ordering to gdf_bounds' unique tile list so bootstrap
    # indices line up with the per-tile count arrays.
    tiles = gdf_bounds["tile_name"].unique()
    n_tiles = len(tiles)

    # Build index-aligned numpy arrays of per-tile TP, FP, FN counts.
    indexed = tile_metrics.set_index("tile_name")
    tp_arr = indexed.reindex(tiles)["tp"].fillna(0).to_numpy(dtype=np.int64)
    fp_arr = indexed.reindex(tiles)["fp"].fillna(0).to_numpy(dtype=np.int64)
    fn_arr = indexed.reindex(tiles)["fn"].fillna(0).to_numpy(dtype=np.int64)

    rng = np.random.default_rng(seed)

    p_samples = np.empty(n_iterations)
    r_samples = np.empty(n_iterations)
    f1_samples = np.empty(n_iterations)

    for i in range(n_iterations):
        # Draw tile-index sample with replacement; use bincount to get
        # per-tile multiplicities and dot-product with the count arrays
        # for an O(n_tiles) aggregation per iteration.
        sample_idx = rng.integers(0, n_tiles, size=n_tiles)
        mult = np.bincount(sample_idx, minlength=n_tiles)
        tp_total = int(mult @ tp_arr)
        fp_total = int(mult @ fp_arr)
        fn_total = int(mult @ fn_arr)

        p = tp_total / (tp_total + fp_total) if (tp_total + fp_total) > 0 else 0.0
        r = tp_total / (tp_total + fn_total) if (tp_total + fn_total) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

        p_samples[i] = p
        r_samples[i] = r
        f1_samples[i] = f1

    def pct_ci(arr: np.ndarray) -> tuple[float, float]:
        return (
            float(np.percentile(arr, 2.5)),
            float(np.percentile(arr, 97.5)),
        )

    return {
        "precision": pct_ci(p_samples),
        "recall": pct_ci(r_samples),
        "f1": pct_ci(f1_samples),
    }


def compute_at_buffer(
    gdf_det: gpd.GeoDataFrame,
    gdf_student: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    review_yesterday: pd.DataFrame,
    review_today: pd.DataFrame,
    buffer_r: int,
    n_bootstrap: int,
    seed: int,
    compute_mcc: bool = False,
) -> BufferResult:
    """Compute corrected-F1 point estimate and CIs at a single buffer R.

    Args:
        gdf_det: Accepted detections (already verifier-thresholded).
        gdf_student: Student ground truth (original, un-extended).
        gdf_bounds: Tile boundary polygons.
        review_yesterday: Yesterday's review DataFrame.
        review_today: Today's multi-buffer review DataFrame.
        buffer_r: Buffer radius in metres.
        n_bootstrap: Number of bootstrap iterations for CIs.
        seed: Random seed for bootstrap reproducibility.
        compute_mcc: If True, also compute tile-level MCC, sensitivity and
            specificity (with BCa bootstrap CIs) against the same per-buffer
            gated extended GT, via the shared ``calculate_tile_classification``
            engine that Track 1 uses — so only the GT differs between tracks.

    Returns:
        :class:`BufferResult` with point estimates, counts, and 95 % CIs.
    """
    print(f"\n--- Buffer R = {buffer_r} m ---")

    # 1. Phantom GT at R and scoped student GT baseline count
    gdf_phantoms = build_phantom_gdf(
        review_yesterday, review_today, buffer_r, crs=gdf_det.crs,
    )
    n_reviewer_promoted = len(gdf_phantoms)

    gdf_ext_gt = build_extended_gt(gdf_student, gdf_phantoms)

    # 2. Per-map Hungarian matching against extended GT
    tp, fp, fn, n_ref_extended_scoped = compute_counts_at_r(
        gdf_det, gdf_ext_gt, gdf_bounds, buffer_r,
    )

    # 3. Baseline scoped student GT count (for auditability)
    _, _, _, n_ref_student_only = compute_counts_at_r(
        gdf_det, gdf_student, gdf_bounds, buffer_r,
    )

    # 4. Point estimates
    p, r, f1 = compute_point_estimate(tp, fp, fn)
    print(
        f"R={buffer_r}m  TP={tp}  FP={fp}  FN={fn}  "
        f"n_ref_student={n_ref_student_only}  "
        f"n_reviewer_promoted={n_reviewer_promoted}  "
        f"n_ref_ext_scoped={n_ref_extended_scoped}"
    )
    print(f"  P={p:.4f}  R={r:.4f}  F1={f1:.4f}")

    # 5. Tile-level bootstrap CIs
    cis = bootstrap_tile_level_ci(
        gdf_det, gdf_ext_gt, gdf_bounds, buffer_r,
        n_iterations=n_bootstrap, seed=seed,
    )
    print(
        f"  95% CIs — P=[{cis['precision'][0]:.4f}, {cis['precision'][1]:.4f}] "
        f"R=[{cis['recall'][0]:.4f}, {cis['recall'][1]:.4f}] "
        f"F1=[{cis['f1'][0]:.4f}, {cis['f1'][1]:.4f}]"
    )

    # 6. Optional tile-level MCC against the SAME gated extended GT.
    mcc_kwargs: dict = {}
    if compute_mcc:
        tile_class = calculate_tile_classification(gdf_det, gdf_ext_gt, gdf_bounds)
        tile_ci = bootstrap_tile_classification_ci(
            gdf_det, gdf_ext_gt, gdf_bounds,
            n_iterations=n_bootstrap, random_seed=seed,
        )
        mcc_block = tile_ci.get("mcc", {}) if isinstance(tile_ci, dict) else {}
        mcc_ci = (
            (mcc_block.get("ci_lower"), mcc_block.get("ci_upper"))
            if mcc_block.get("ci_lower") is not None
            else None
        )
        mcc_kwargs = {
            "mcc": tile_class.get("mcc"),
            "mcc_ci": mcc_ci,
            "tile_tp": tile_class.get("tp"),
            "tile_tn": tile_class.get("tn"),
            "tile_fp": tile_class.get("fp"),
            "tile_fn": tile_class.get("fn"),
            "sensitivity": tile_class.get("sensitivity"),
            "specificity": tile_class.get("specificity"),
        }
        mcc_disp = tile_class.get("mcc")
        mcc_str = f"{mcc_disp:.4f}" if mcc_disp is not None else "n/a"
        print(
            f"  MCC={mcc_str}  "
            f"tiles TP/TN/FP/FN="
            f"{tile_class.get('tp')}/{tile_class.get('tn')}/"
            f"{tile_class.get('fp')}/{tile_class.get('fn')}"
        )

    return BufferResult(
        buffer_metres=buffer_r,
        tp=int(tp),
        fp=int(fp),
        fn=int(fn),
        n_ref_student_only=int(n_ref_student_only),
        n_reviewer_promoted=int(n_reviewer_promoted),
        n_ref_extended=int(n_ref_extended_scoped),
        precision=p,
        precision_ci=cis["precision"],
        recall=r,
        recall_ci=cis["recall"],
        f1=f1,
        f1_ci=cis["f1"],
        **mcc_kwargs,
    )


def git_commit_hash() -> str:
    """Return the current git HEAD commit hash, or 'unknown' on failure."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
        ).decode("ascii").strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def write_csv(results: list[BufferResult], out_path: Path) -> None:
    """Write the multi-buffer results table to CSV.

    MCC columns are appended only when the run was invoked with
    ``--compute-mcc`` (i.e. at least one row carries an MCC), so legacy
    F1-only output stays byte-identical.
    """
    has_mcc = any(r.mcc is not None for r in results)
    rows = []
    for r in results:
        row = {
            "R_m": r.buffer_metres,
            "TP": r.tp,
            "FP": r.fp,
            "FN": r.fn,
            "n_ref_student_only": r.n_ref_student_only,
            "n_reviewer_promoted_at_R": r.n_reviewer_promoted,
            "n_ref_extended": r.n_ref_extended,
            "precision": r.precision,
            "precision_CI_lo": r.precision_ci[0],
            "precision_CI_hi": r.precision_ci[1],
            "recall": r.recall,
            "recall_CI_lo": r.recall_ci[0],
            "recall_CI_hi": r.recall_ci[1],
            "F1": r.f1,
            "F1_CI_lo": r.f1_ci[0],
            "F1_CI_hi": r.f1_ci[1],
        }
        if has_mcc:
            row.update({
                "MCC": r.mcc,
                "MCC_CI_lo": r.mcc_ci[0] if r.mcc_ci else None,
                "MCC_CI_hi": r.mcc_ci[1] if r.mcc_ci else None,
                "tile_TP": r.tile_tp,
                "tile_TN": r.tile_tn,
                "tile_FP": r.tile_fp,
                "tile_FN": r.tile_fn,
                "sensitivity": r.sensitivity,
                "specificity": r.specificity,
            })
        rows.append(row)
    pd.DataFrame(rows).to_csv(out_path, index=False)


def write_summary_json(
    results: list[BufferResult],
    out_path: Path,
    *,
    seed: int,
    n_bootstrap: int,
    input_paths: dict[str, str],
    excluded_sentinel_count: int,
) -> None:
    """Serialise the full multi-buffer summary to JSON."""
    payload = {
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "methodology": "Approach B — extended-GT-at-R Hungarian matching",
        "metadata": {
            "seed": seed,
            "bootstrap_n": n_bootstrap,
            "git_commit": git_commit_hash(),
            "input_paths": input_paths,
        },
        "exclusions": {
            "sentinel_buffer_metres": SENTINEL_BUFFER_EXCLUDED,
            "n_excluded_candidates": excluded_sentinel_count,
            "note": (
                f"Today's review included {excluded_sentinel_count} "
                f"candidates labelled 'mound' at buffer_metres=200 — the "
                "'>150 m' sentinel shell. These are visible mounds inside "
                "the 286 m corners-plus-5 px circle but outside all review "
                "rings. They are EXCLUDED from every extended-GT build here; "
                "their detections appear as FP at every R ≤ 150 m, which is "
                "the correct behaviour under the 150 m practitioner cap."
            ),
        },
        "obs_272_reference": (
            "Obs 272 in docs/notes/reflections/working-notes.md shows the "
            "attractor-pull effect is statistically significant only through "
            "125 m — shells at (125, 150] and (150, 286] are indistinguishable "
            "from within-tile random placement. The 150 m row should be "
            "treated as an optimistic upper bound, not a practitioner-useful "
            "recall claim."
        ),
        "results": [
            _result_to_dict(r)
            for r in results
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2))


def _result_to_dict(r: BufferResult) -> dict:
    """Serialise one BufferResult; append the MCC block only when present."""
    d = {
        "R_m": r.buffer_metres,
        "TP": r.tp,
        "FP": r.fp,
        "FN": r.fn,
        "n_ref_student_only": r.n_ref_student_only,
        "n_reviewer_promoted_at_R": r.n_reviewer_promoted,
        "n_ref_extended": r.n_ref_extended,
        "precision": r.precision,
        "precision_CI": list(r.precision_ci),
        "recall": r.recall,
        "recall_CI": list(r.recall_ci),
        "F1": r.f1,
        "F1_CI": list(r.f1_ci),
    }
    if r.mcc is not None or r.tile_tp is not None:
        d["tile_classification"] = {
            "mcc": r.mcc,
            "mcc_CI": list(r.mcc_ci) if r.mcc_ci else None,
            "tp": r.tile_tp,
            "tn": r.tile_tn,
            "fp": r.tile_fp,
            "fn": r.tile_fn,
            "sensitivity": r.sensitivity,
            "specificity": r.specificity,
        }
    return d


def write_markdown_report(
    results: list[BufferResult],
    out_path: Path,
    *,
    seed: int,
    n_bootstrap: int,
    input_paths: dict[str, str],
    excluded_sentinel_count: int,
) -> None:
    """Write the narrative Markdown report comparing buffers and referencing Obs 272."""
    ts = datetime.now(timezone.utc).isoformat()
    row_lines = []
    for r in results:
        row_lines.append(
            f"| {r.buffer_metres} | {r.tp} | {r.fp} | {r.fn} | "
            f"{r.n_ref_student_only} | {r.n_reviewer_promoted} | "
            f"{r.n_ref_extended} | "
            f"{r.precision:.4f} [{r.precision_ci[0]:.4f}, "
            f"{r.precision_ci[1]:.4f}] | "
            f"{r.recall:.4f} [{r.recall_ci[0]:.4f}, "
            f"{r.recall_ci[1]:.4f}] | "
            f"**{r.f1:.4f}** [{r.f1_ci[0]:.4f}, {r.f1_ci[1]:.4f}] |"
        )

    rows_md = "\n".join(row_lines)

    # Lookup helpers by buffer radius so the report degrades gracefully if
    # the caller runs a custom subset of buffers.
    by_r = {r.buffer_metres: r for r in results}
    first_row = results[0]
    result_125 = by_r.get(125)
    practitioner_block = (
        (
            f"\n## Practitioner-useful cap: F1 at R = 125 m\n\n"
            f"Recommended single-number summary for downstream quotation:\n"
            f"**F1 = {result_125.f1:.4f}** at R = 125 m (95 % CI "
            f"[{result_125.f1_ci[0]:.4f}, {result_125.f1_ci[1]:.4f}]) —\n"
            f"the largest R where the attractor-pull contribution to recall "
            f"is\nstatistically distinguishable from within-tile random "
            f"placement.\n"
        )
        if result_125 is not None
        else (
            "\n## Practitioner-useful cap: F1 at R = 125 m\n\n"
            "(R = 125 m not computed in this run — re-run with R = 125 m "
            "included for the practitioner headline.)\n"
        )
    )

    md = f"""# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: {ts}
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: {n_bootstrap:,} iterations, seed {seed}, tile-level resampling
**Git commit**: `{git_commit_hash()}`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended \
| P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:\
|:-----------:|:-----------:|:------------:|
{rows_md}

## How to read this table

- **TP / FP / FN**: Hungarian-matching counts against the extended GT at R.
  Every reviewer-promoted phantom within R is added to the GT before matching.
- **n_ref_student**: Student GT points scoped to the evaluation tile bounds
  (the denominator without any human-review correction).
- **n_promoted@R**: Number of reviewer-promoted phantoms included in the
  extended GT at this R. Yesterday's 472 mound labels appear at every R ≥ 50.
  Today's shell-stratified mound labels accumulate as R rises: +2 @50 m,
  +121 @75 m, +47 @100 m, +19 @125 m, +11 @150 m.
- **n_ref_extended**: Scoped extended-GT count at R (student GT scoped ∪
  in-scope phantoms at R). This is the recall denominator.
- **F1 [95 % CI]**: Corrected F1 at R with tile-level bootstrap CI.

## Comparison to yesterday's 50 m result

Yesterday's single-buffer correction (``compute_corrected_f1_human_reviewed.py``)
produced **F1 = 0.8295** at R = 50 m via an analytic adjustment to measured
counts (moved 472 FPs into TP and added them to the GT denominator, without
re-running Hungarian). This script's R = {first_row.buffer_metres} m row
(**F1 = {first_row.f1:.4f}**) re-runs Hungarian over extended GT including
the 2 today-corrections at 50 m. Expected ΔF1 ≈ +0.003 versus yesterday's
number. The two numbers are methodologically close but not identical —
Approach B allows detections to rematch optimally against the extended GT,
which can free a detection previously bound to a distant student-GT point
to pair with a closer phantom.

## Obs 272 caveat — the 150 m row is an upper bound

Obs 272 in ``docs/notes/reflections/working-notes.md`` shows the
attractor-pull effect (reviewer confirmations concentrating closer to the
detection than a uniform within-tile null would predict) is statistically
significant only through 125 m. At the (125, 150] shell the shell-specific
mound-confirmation rate is indistinguishable from the within-tile random-
placement null, and the (150, 286] shell ("200 m" sentinel in today's CSV)
is completely indistinguishable.

**Implication for interpretation:**

- **R ≤ 125 m**: corrected F1 / P / R are practitioner-meaningful. The
  reviewer-promoted phantoms in these shells are confirming detections
  genuinely spatially associated with visible mound symbols.
- **R = 150 m**: corrected F1 at 150 m is an **upper bound on achievable
  practitioner recall**, not a practitioner-useful operating point.
  Including the 11 mounds in the (125, 150] shell inflates recall in a way
  the attractor-pull null cannot distinguish from coincidental alignment.
- **R > 150 m (excluded from this analysis)**: the 74 candidates at the
  ">150 m" sentinel (``buffer_metres=200``) are visible mounds inside the
  286 m corners-plus-5 px review circle but outside every review ring.
  They are **not** added as phantoms at any R in this analysis; their
  detections appear as FP at every R ≤ 150 m, which is the correct
  behaviour under the 150 m practitioner cap.

{practitioner_block}
## Sentinel exclusion

{excluded_sentinel_count} candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `{input_paths['detections']}`
  - Student GT: `{input_paths['student_gt']}`
  - Bounds: `{input_paths['bounds']}`
  - Review (yesterday): `{input_paths['review_yesterday']}`
  - Review (today): `{input_paths['review_today']}`
- **Bootstrap**: {n_bootstrap:,} iterations, seed {seed}, tile-level resampling
- **Git commit**: `{git_commit_hash()}`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
"""

    out_path.write_text(md)


def run(
    *,
    verified_detections: Path,
    student_gt: Path,
    bounds: Path,
    review_yesterday: Path,
    review_today: Path,
    output_dir: Path,
    buffers: Iterable[int],
    n_bootstrap: int,
    seed: int,
    compute_mcc: bool = False,
) -> None:
    """End-to-end driver: load data, compute per-R, write outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading inputs...")
    gdf_det = gpd.read_file(verified_detections)
    gdf_student = gpd.read_file(student_gt)
    gdf_bounds = gpd.read_file(bounds)

    for gdf, name in (
        (gdf_det, "detections"),
        (gdf_student, "student_gt"),
        (gdf_bounds, "bounds"),
    ):
        if gdf.crs is None:
            print(f"  WARN: {name} had no CRS; assuming {DEFAULT_CRS}")
            gdf.set_crs(DEFAULT_CRS, inplace=True)
        elif str(gdf.crs) != DEFAULT_CRS:
            print(f"  Reprojecting {name} from {gdf.crs} to {DEFAULT_CRS}")
            gdf.to_crs(DEFAULT_CRS, inplace=True)

    print(f"  detections: {len(gdf_det):,}")
    print(f"  student GT: {len(gdf_student):,}")
    print(f"  bounds tiles: {len(gdf_bounds):,}")

    review_y = pd.read_csv(review_yesterday)
    review_t = pd.read_csv(review_today)
    print(f"  review (yesterday): {len(review_y):,}")
    print(f"  review (today):     {len(review_t):,}")

    # Excluded sentinel count (for report/JSON)
    excluded = int(
        (
            (review_t["human_label"] == "mound")
            & (review_t["buffer_metres"] == SENTINEL_BUFFER_EXCLUDED)
        ).sum()
    )
    print(
        f"  excluded sentinels (>150 m shell, buffer_metres=200): {excluded}"
    )

    results: list[BufferResult] = []
    for r in buffers:
        results.append(
            compute_at_buffer(
                gdf_det=gdf_det,
                gdf_student=gdf_student,
                gdf_bounds=gdf_bounds,
                review_yesterday=review_y,
                review_today=review_t,
                buffer_r=r,
                n_bootstrap=n_bootstrap,
                seed=seed,
                compute_mcc=compute_mcc,
            )
        )

    # Outputs
    input_paths = {
        "detections": str(verified_detections),
        "student_gt": str(student_gt),
        "bounds": str(bounds),
        "review_yesterday": str(review_yesterday),
        "review_today": str(review_today),
    }

    csv_path = output_dir / "corrected-f1.csv"
    json_path = output_dir / "summary.json"
    # Session 76 guardrail: hand-authored report.md is the paper-citation
    # source. Script writes to report_autogen.md sibling (Session 75 G6).
    md_path = output_dir / "report_autogen.md"

    write_csv(results, csv_path)
    print(f"\nWrote {csv_path}")

    write_summary_json(
        results, json_path,
        seed=seed, n_bootstrap=n_bootstrap,
        input_paths=input_paths, excluded_sentinel_count=excluded,
    )
    print(f"Wrote {json_path}")

    write_markdown_report(
        results, md_path,
        seed=seed, n_bootstrap=n_bootstrap,
        input_paths=input_paths, excluded_sentinel_count=excluded,
    )
    print(f"Wrote {md_path}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--verified-detections", type=Path, required=True)
    p.add_argument("--student-gt", type=Path, required=True)
    p.add_argument("--bounds", type=Path, required=True)
    p.add_argument("--review-yesterday", type=Path, required=True)
    p.add_argument("--review-today", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument(
        "--buffers", nargs="+", type=int, default=list(DEFAULT_BUFFERS),
        help=f"Buffer radii in metres (default: {list(DEFAULT_BUFFERS)})",
    )
    p.add_argument(
        "--n-bootstrap", type=int, default=10_000,
        help="Bootstrap iterations per buffer (default: 10000).",
    )
    p.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for bootstrap reproducibility (default: 42).",
    )
    p.add_argument(
        "--compute-mcc", action="store_true",
        help=(
            "Also compute tile-level MCC, sensitivity and specificity (with "
            "BCa bootstrap CIs) against the same per-buffer gated extended GT, "
            "using the shared calculate_tile_classification engine. Off by "
            "default so legacy F1-only output is byte-identical."
        ),
    )
    return p.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    run(
        verified_detections=args.verified_detections,
        student_gt=args.student_gt,
        bounds=args.bounds,
        review_yesterday=args.review_yesterday,
        review_today=args.review_today,
        output_dir=args.output_dir,
        buffers=tuple(args.buffers),
        n_bootstrap=args.n_bootstrap,
        seed=args.seed,
        compute_mcc=args.compute_mcc,
    )


if __name__ == "__main__":
    main()
