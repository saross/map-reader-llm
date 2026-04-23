#!/usr/bin/env python3
"""
Buffer-band lift analysis for VLM detection candidates.

Quantifies how much VLM detection centroids cluster around real mounds
relative to random placement. Combines yesterday's 1,028-candidate
single-buffer review (472 mound@50 m, 556 not_mound@50 m) with today's
557-candidate multi-buffer re-review (274 mound at various bands, 283
confirmed FPs).

For each target radius R ∈ {50, 75, 100, 125, 150, 286 m}, computes:

1. **Observed** P(real mound within R | candidate) — from the
   reviewer's ``buffer_band`` labels directly. This is the honest
   measure of "is there a real mound inside the R-circle" because
   it represents a physical assessment by the reviewer, not a
   KDTree lookup against an incomplete GT.
2. **Null** P(student-GT mound within R | random point in same tile)
   via M = 1,000 within-tile permutations. Student GT is the only
   mound set with fixed known coordinates; the 746 reviewer-promoted
   mounds sit AT the detection coordinates and cannot be used as
   null-space mounds without creating a trivial self-match.
3. Lift ratio, one-sided permutation p-value, and a "signal fraction"
   (fraction of mounds-within-R that are genuine pulls rather than
   coincidences).
4. Annular (shell) rates at each band with the same statistics.

Plus a companion spatial-statistic analysis: Ripley's cross-K_12
function on a fine r-grid, converted to the centred cross-L_12(r) − r
form, with a 95 % envelope from the same M = 1,000 within-tile
permutations. Uses student GT as type 2 for the same reason as above
(fixed known coordinates vs detection-coord-aliased phantoms).

**Bias note**: The 746 reviewer-promoted real mounds (~14 % of the
true-mound universe of 5,490) are absent from the student-GT null.
The null rate is therefore a slight under-estimate of the true
random-placement mound-hit rate, so the reported raw lift ratios are
slight over-estimates. The report emits a bias-corrected lift column
(raw × 0.864 ≈ 4744/5490) that approximates the true lift assuming
the 746 reviewer-promoted mounds are distributed in the same tile
pool as the detections.

The 286 m target radius derives from the ``>150 m`` review ("6")
label's effective tolerance: a circle that just touches the outer
corners of the 400 m × 400 m context crop (200 × √2 ≈ 282.8 m) plus
5 display-pixels (3.3 m) = 286.2 m.

Inputs:

- results/55maps-image-generalisation/human-review.csv
- results/55maps-image-generalisation/human-review-multi-buffer.csv
- inputs/vectors/references/student-mounds-55maps-reviewed.geojson
- inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson

Outputs at results/55maps-image-generalisation/buffer-band-lift/:

- cumulative.csv   : per-R cumulative lift table
- shell.csv        : per-annulus lift table
- ripley.csv       : per-r cross-L_12(r) − r with 95 % envelope
- summary.json     : headline numbers + input provenance
- lift_curve.png   : cumulative observed vs null curve
- ripley_plot.png  : cross-L_12(r) − r with envelope
- report_autogen.md: auto-generated tables + interpretation
                     (hand-authored `report.md` is the paper-citation source;
                     do NOT overwrite it — Session 75 guardrail 6)

The script is pure analysis — no API calls, no external I/O beyond the
files above. Compute runs in 1–2 min on sapphire.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

# --- Configuration ---
SEED = 42
M_PERMUTATIONS = 1000
R_VALUES: tuple[int, ...] = (50, 75, 100, 125, 150, 286)
# Finer grid for Ripley's K — capture curve shape between the review
# bands and a little past 286 m to see the decay into CSR.
R_GRID_RIPLEY: np.ndarray = np.linspace(10.0, 320.0, 32)
CRS = "EPSG:32635"

# --- Paths ---
REPO_ROOT = Path(__file__).resolve().parent.parent
REVIEW_YESTERDAY = REPO_ROOT / (
    "results/55maps-image-generalisation/human-review.csv"
)
REVIEW_TODAY = REPO_ROOT / (
    "results/55maps-image-generalisation/human-review-multi-buffer.csv"
)
STUDENT_GT = REPO_ROOT / (
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
)
BOUNDS = REPO_ROOT / (
    "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
)
OUT_DIR = REPO_ROOT / (
    "results/55maps-image-generalisation/buffer-band-lift"
)


def normalise_tile_key(source_tile: str) -> str:
    """
    Return ``source_tile`` in a canonical form for matching against
    the bounds file's ``tile_name`` column. The 55-map bounds file
    retains the ``.png`` extension, so this is a pass-through except
    when the input has been trimmed elsewhere in the pipeline.
    """
    s = str(source_tile)
    return s if s.endswith(".png") else s + ".png"


def load_candidates_combined() -> pd.DataFrame:
    """
    Combine yesterday's 472 mound@50 m calls with today's 557-row
    multi-buffer re-review into a single dataframe of 1,029 rows
    (modulo rounding — 472 + 557 = 1,029, with any duplicates dropped).

    Each row carries a ``buffer_band`` column: numeric value in
    {50, 75, 100, 125, 150, 200} for mound rows (200 = ``>150 m``),
    or np.inf for ``not_mound`` (no mound within 286 m).
    """
    yesterday = pd.read_csv(REVIEW_YESTERDAY)
    today = pd.read_csv(REVIEW_TODAY)

    # Yesterday's 472 candidates marked ``mound`` at the 50 m review.
    y_mound = yesterday[yesterday["human_label"] == "mound"].copy()
    y_mound["buffer_band"] = 50.0
    # Yesterday's 556 ``not_mound`` are not included here — those are
    # the re-review targets and appear in today's CSV with updated
    # buffer_band values.

    # Today's rows already carry the buffer_metres they were reviewed
    # at; convert to numeric, map to buffer_band for mound rows, use
    # np.inf for not_mound / uncertain rows.
    today = today.copy()
    today["buffer_band"] = pd.to_numeric(
        today.get("buffer_metres"), errors="coerce"
    )
    today.loc[today["human_label"] != "mound", "buffer_band"] = np.inf

    keep = ["candidate_id", "map_name", "source_tile", "x", "y",
            "buffer_band", "human_label", "symbol_type"]
    combined = pd.concat(
        [y_mound[keep], today[keep]], ignore_index=True
    )
    # Dedupe in case (shouldn't happen — yesterday's mounds were
    # excluded from today's queue by design). Prefer today's entry
    # if any collision.
    combined = combined.drop_duplicates(
        subset="candidate_id", keep="last",
    )
    return combined.reset_index(drop=True)


def load_student_gt() -> gpd.GeoDataFrame:
    """
    Load the student-digitised mound GT (4,744 features, already
    reviewed for duplicates). This is the only mound set with fixed
    known coordinates; reviewer-promoted phantoms cannot be used as
    the null-space reference set because they are aliased to detection
    coordinates.
    """
    student = gpd.read_file(STUDENT_GT).to_crs(CRS)
    return gpd.GeoDataFrame(
        student[["geometry"]].copy(), crs=CRS,
    )


def count_reviewer_promoted() -> int:
    """Return the total reviewer-promoted mound count (yesterday + today)."""
    y = pd.read_csv(REVIEW_YESTERDAY)
    t = pd.read_csv(REVIEW_TODAY)
    return int(
        (y["human_label"] == "mound").sum()
        + (t["human_label"] == "mound").sum()
    )


def attach_tile_bounds(
    cands: pd.DataFrame, bounds: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """
    Join each candidate to its tile's bounding box by matching the
    candidate's ``source_tile`` (minus ``.png``) against the bounds'
    ``tile_name`` column.

    Returns the input dataframe with ``tile_minx`` / ``tile_miny`` /
    ``tile_maxx`` / ``tile_maxy`` columns. Rows whose tile cannot be
    resolved are dropped and reported.
    """
    b = bounds.copy()
    b["tile_key"] = b["tile_name"].astype(str)
    b_bounds = b.geometry.bounds  # DataFrame: minx, miny, maxx, maxy
    b = b.assign(
        tile_minx=b_bounds["minx"].values,
        tile_miny=b_bounds["miny"].values,
        tile_maxx=b_bounds["maxx"].values,
        tile_maxy=b_bounds["maxy"].values,
    )
    c = cands.copy()
    c["tile_key"] = c["source_tile"].apply(normalise_tile_key)
    merged = c.merge(
        b[["tile_key", "tile_minx", "tile_miny", "tile_maxx",
           "tile_maxy"]],
        on="tile_key",
        how="left",
    )
    missing = merged["tile_minx"].isna().sum()
    if missing:
        print(
            f"[warn] {missing} candidates dropped (no matching tile "
            "in 55maps_evaluation_bounds.geojson)"
        )
        merged = merged.dropna(subset=["tile_minx"])
    return merged.reset_index(drop=True)


def randomise_within_tile(
    cands: pd.DataFrame, rng: np.random.Generator,
) -> np.ndarray:
    """Uniform random placement inside each candidate's tile bounding box."""
    x = rng.uniform(
        cands["tile_minx"].to_numpy(), cands["tile_maxx"].to_numpy()
    )
    y = rng.uniform(
        cands["tile_miny"].to_numpy(), cands["tile_maxy"].to_numpy()
    )
    return np.column_stack([x, y])


def nearest_distances(coords: np.ndarray, tree: cKDTree) -> np.ndarray:
    """Distance from each point in ``coords`` to its nearest GT."""
    dist, _ = tree.query(coords, k=1)
    return dist


def cumulative_within_r(
    dist: np.ndarray, r_values: tuple[int, ...],
) -> dict[int, float]:
    """Fraction of points with nearest-GT ≤ R, per R."""
    return {R: float(np.mean(dist <= R)) for R in r_values}


def shell_within_r(
    dist: np.ndarray, r_values: tuple[int, ...],
) -> dict[int, float]:
    """
    Fraction of points with nearest-GT in each (R_{n-1}, R_n] shell.
    The first shell is (0, R_0].
    """
    out: dict[int, float] = {}
    prev = 0.0
    for R in r_values:
        mask = (dist > prev) & (dist <= R)
        out[R] = float(np.mean(mask))
        prev = float(R)
    return out


def ripley_cross_k(
    coords: np.ndarray, tree: cKDTree, r_grid: np.ndarray,
    area: float, n_type1: int, n_type2: int,
) -> np.ndarray:
    """
    Cross-K_12(r) estimator without edge correction.

    K_12(r) = (A / (n1 × n2)) × Σ_i count_j(d(i,j) ≤ r)

    Edge correction is omitted because we compare observed K_12 to a
    Monte Carlo null (within-tile permutation) that shares the same
    edge behaviour; the edge bias cancels in the comparison.
    """
    K = np.empty(len(r_grid), dtype=float)
    for idx, r in enumerate(r_grid):
        neighbour_lists = tree.query_ball_point(coords, r=float(r))
        total = sum(len(nl) for nl in neighbour_lists)
        K[idx] = (area / (n_type1 * n_type2)) * total
    return K


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    print("[1/5] Loading data...")
    cands_raw = load_candidates_combined()
    student_gt = load_student_gt()
    n_reviewer_promoted = count_reviewer_promoted()
    bounds_gdf = gpd.read_file(BOUNDS).to_crs(CRS)

    cands = attach_tile_bounds(cands_raw, bounds_gdf)
    n_total = len(cands)
    n_student = len(student_gt)
    n_real_total = n_student + n_reviewer_promoted  # 4744 + 746 = 5490
    bias_correction = n_student / n_real_total  # ~0.864
    area_m2 = float(bounds_gdf.geometry.area.sum())
    n_yesterday_mound = int((cands["buffer_band"] == 50).sum())

    print(f"  candidates (combined): {n_total}")
    print(f"  student GT: {n_student}")
    print(f"  reviewer-promoted mounds: {n_reviewer_promoted}")
    print(
        f"  real-mound universe: {n_real_total} "
        f"(student-GT fraction = {bias_correction:.3f})"
    )
    print(f"  study area: {area_m2 / 1e6:.1f} km^2")

    # Observed cumulative and shell from REVIEWER LABELS (the honest
    # measure of "real mound within R per reviewer"). KDTree-based
    # observed would be artificially inflated because phantoms are
    # aliased to detection coordinates.
    obs_cum: dict[int, float] = {
        R: float((cands["buffer_band"] <= R).sum() / n_total)
        for R in R_VALUES
    }
    obs_shell_rates: dict[int, float] = {}
    prev_R = 0.0
    for R in R_VALUES:
        mask = (cands["buffer_band"] > prev_R) & (cands["buffer_band"] <= R)
        obs_shell_rates[R] = float(mask.sum() / n_total)
        prev_R = float(R)

    # Ripley's K uses student GT only (type 2) — the only mound set
    # with fixed known coordinates. Observed K_12 is computed from
    # actual detection positions × student GT.
    obs_coords = cands[["x", "y"]].to_numpy()
    gt_coords = np.array([[g.x, g.y] for g in student_gt.geometry])
    tree = cKDTree(gt_coords)

    obs_K = ripley_cross_k(
        obs_coords, tree, R_GRID_RIPLEY, area_m2, n_total, n_student,
    )
    obs_L = np.sqrt(obs_K / np.pi) - R_GRID_RIPLEY

    print("  observed cumulative (from reviewer buffer_band labels):")
    for R in R_VALUES:
        print(f"    R={R:>3d}: {obs_cum[R]:.4f}")

    # --- Permutation null ---
    print(f"[2/5] Running {M_PERMUTATIONS} within-tile permutations...")
    null_cum = np.zeros((M_PERMUTATIONS, len(R_VALUES)))
    null_shell = np.zeros((M_PERMUTATIONS, len(R_VALUES)))
    null_K = np.zeros((M_PERMUTATIONS, len(R_GRID_RIPLEY)))

    for m in range(M_PERMUTATIONS):
        perm_coords = randomise_within_tile(cands, rng)
        dist = nearest_distances(perm_coords, tree)
        cum = cumulative_within_r(dist, R_VALUES)
        shell = shell_within_r(dist, R_VALUES)
        for j, R in enumerate(R_VALUES):
            null_cum[m, j] = cum[R]
            null_shell[m, j] = shell[R]
        null_K[m] = ripley_cross_k(
            perm_coords, tree, R_GRID_RIPLEY,
            area_m2, n_total, n_student,
        )
        if (m + 1) % 200 == 0:
            print(f"    {m + 1}/{M_PERMUTATIONS}")
    null_L = np.sqrt(null_K / np.pi) - R_GRID_RIPLEY

    # One-sided permutation p-values: P(null ≥ observed).
    obs_cum_arr = np.array([obs_cum[R] for R in R_VALUES])
    obs_shell_arr = np.array([obs_shell_rates[R] for R in R_VALUES])
    p_cum = np.mean(null_cum >= obs_cum_arr, axis=0)
    p_shell = np.mean(null_shell >= obs_shell_arr, axis=0)

    # --- Assemble output tables ---
    print("[3/5] Building summary tables...")
    p_floor = 1.0 / M_PERMUTATIONS

    # Null rates from student GT are a slight under-estimate of the
    # true null (missing ~14% of reviewer-promoted real mounds). To
    # approximate the bias-corrected null, scale null by the inverse
    # of the student-GT fraction of the real-mound universe. This is
    # first-order correct under the assumption that reviewer-promoted
    # mounds have the same tile-pool distribution as student GT.
    cum_rows: list[dict] = []
    for j, R in enumerate(R_VALUES):
        null_mean = float(np.mean(null_cum[:, j]))
        null_corrected = null_mean / bias_correction
        null_lo = float(np.percentile(null_cum[:, j], 2.5))
        null_hi = float(np.percentile(null_cum[:, j], 97.5))
        obs = float(obs_cum[R])
        lift_raw = obs / null_mean if null_mean > 0 else float("inf")
        lift_corrected = (
            obs / null_corrected if null_corrected > 0 else float("inf")
        )
        signal_raw = (obs - null_mean) / obs if obs > 0 else 0.0
        signal_corrected = (
            (obs - null_corrected) / obs if obs > 0 else 0.0
        )
        p = max(float(p_cum[j]), p_floor)
        cum_rows.append({
            "R_m": int(R),
            "obs_rate": round(obs, 4),
            "null_mean": round(null_mean, 4),
            "null_mean_bias_corrected": round(null_corrected, 4),
            "null_ci_lo": round(null_lo, 4),
            "null_ci_hi": round(null_hi, 4),
            "lift_ratio": round(lift_raw, 2),
            "lift_ratio_bias_corrected": round(lift_corrected, 2),
            "signal_fraction": round(signal_raw, 4),
            "signal_fraction_bias_corrected": round(signal_corrected, 4),
            "p_value": round(p, 4),
        })
    cum_df = pd.DataFrame(cum_rows)
    cum_df.to_csv(OUT_DIR / "cumulative.csv", index=False)

    shell_rows: list[dict] = []
    prev_R = 0
    for j, R in enumerate(R_VALUES):
        null_mean = float(np.mean(null_shell[:, j]))
        null_corrected = null_mean / bias_correction
        null_lo = float(np.percentile(null_shell[:, j], 2.5))
        null_hi = float(np.percentile(null_shell[:, j], 97.5))
        obs = float(obs_shell_rates[R])
        lift_raw = obs / null_mean if null_mean > 0 else float("inf")
        lift_corrected = (
            obs / null_corrected if null_corrected > 0 else float("inf")
        )
        signal_raw = (obs - null_mean) / obs if obs > 0 else 0.0
        signal_corrected = (
            (obs - null_corrected) / obs if obs > 0 else 0.0
        )
        p = max(float(p_shell[j]), p_floor)
        shell_rows.append({
            "R_inner_m": int(prev_R),
            "R_outer_m": int(R),
            "obs_rate_in_shell": round(obs, 4),
            "null_mean_in_shell": round(null_mean, 4),
            "null_mean_bias_corrected": round(null_corrected, 4),
            "null_ci_lo": round(null_lo, 4),
            "null_ci_hi": round(null_hi, 4),
            "lift_ratio": round(lift_raw, 2),
            "lift_ratio_bias_corrected": round(lift_corrected, 2),
            "signal_fraction": round(signal_raw, 4),
            "signal_fraction_bias_corrected": round(signal_corrected, 4),
            "p_value": round(p, 4),
        })
        prev_R = R
    shell_df = pd.DataFrame(shell_rows)
    shell_df.to_csv(OUT_DIR / "shell.csv", index=False)

    ripley_rows: list[dict] = []
    null_L_lo = np.percentile(null_L, 2.5, axis=0)
    null_L_hi = np.percentile(null_L, 97.5, axis=0)
    null_L_mean = np.mean(null_L, axis=0)
    for j, r in enumerate(R_GRID_RIPLEY):
        ripley_rows.append({
            "r_m": round(float(r), 2),
            "L_minus_r_obs": round(float(obs_L[j]), 2),
            "L_minus_r_null_mean": round(float(null_L_mean[j]), 2),
            "L_minus_r_envelope_lo": round(float(null_L_lo[j]), 2),
            "L_minus_r_envelope_hi": round(float(null_L_hi[j]), 2),
            "outside_envelope": bool(
                obs_L[j] > null_L_hi[j] or obs_L[j] < null_L_lo[j]
            ),
        })
    ripley_df = pd.DataFrame(ripley_rows)
    ripley_df.to_csv(OUT_DIR / "ripley.csv", index=False)

    summary = {
        "date": "2026-04-21",
        "n_candidates_combined": n_total,
        "n_yesterday_mound_50m": n_yesterday_mound,
        "n_today_reviewed": int(len(cands) - n_yesterday_mound),
        "n_student_gt": n_student,
        "n_reviewer_promoted": n_reviewer_promoted,
        "n_real_mound_universe": n_real_total,
        "bias_correction_factor": round(bias_correction, 4),
        "study_area_km2": round(area_m2 / 1e6, 2),
        "student_gt_density_per_km2": round(
            n_student / (area_m2 / 1e6), 3,
        ),
        "real_mound_density_per_km2": round(
            n_real_total / (area_m2 / 1e6), 3,
        ),
        "permutations": M_PERMUTATIONS,
        "seed": SEED,
        "target_radii_m": list(R_VALUES),
        "cumulative": cum_rows,
        "shell": shell_rows,
    }
    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # --- Plots ---
    print("[4/5] Rendering plots...")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        Rs = list(R_VALUES)
        ax.plot(
            Rs, [obs_cum[R] for R in Rs], "o-", color="C3",
            label="Observed", linewidth=2.2, markersize=8,
        )
        null_means = [float(np.mean(null_cum[:, j])) for j in range(len(Rs))]
        ax.plot(
            Rs, null_means, "s--", color="C0",
            label="Null mean (within-tile permutation)",
            linewidth=1.6,
        )
        ax.fill_between(
            Rs,
            [float(np.percentile(null_cum[:, j], 2.5))
             for j in range(len(Rs))],
            [float(np.percentile(null_cum[:, j], 97.5))
             for j in range(len(Rs))],
            alpha=0.25, color="C0", label="Null 95 % envelope",
        )
        ax.set_xlabel("Buffer radius R (m)")
        ax.set_ylabel("P(mound within R | candidate)")
        ax.set_title(
            "Cumulative mound-within-R: VLM candidates vs "
            "within-tile null"
        )
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower right")
        fig.savefig(
            OUT_DIR / "lift_curve.png", dpi=150, bbox_inches="tight",
        )
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        ax.plot(
            R_GRID_RIPLEY, obs_L, "o-", color="C3",
            label=r"Observed $L_{12}(r) - r$",
            linewidth=2.2, markersize=4,
        )
        ax.plot(
            R_GRID_RIPLEY, null_L_mean, "--", color="C0",
            label="Null mean",
        )
        ax.fill_between(
            R_GRID_RIPLEY, null_L_lo, null_L_hi,
            alpha=0.25, color="C0", label="Null 95 % envelope",
        )
        ax.axhline(0, color="k", linewidth=0.6, alpha=0.5)
        ax.set_xlabel("r (m)")
        ax.set_ylabel(r"$L_{12}(r) - r$ (m)")
        ax.set_title(
            r"Ripley's cross-$L_{12}(r)-r$: VLM candidates × "
            "extended GT"
        )
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")
        fig.savefig(
            OUT_DIR / "ripley_plot.png", dpi=150, bbox_inches="tight",
        )
        plt.close(fig)
    except ImportError:
        print("  matplotlib not available; CSVs written without plots")

    # --- Narrative report ---
    print("[5/5] Writing report_autogen.md...")
    _write_report(summary, cum_df, shell_df, ripley_df)
    print("Done.")
    print(json.dumps(summary, indent=2))


def _write_report(
    summary: dict, cum_df: pd.DataFrame,
    shell_df: pd.DataFrame, ripley_df: pd.DataFrame,
) -> None:
    lines: list[str] = []
    lines.append(
        "# Buffer-band lift analysis — VLM candidates vs extended GT"
    )
    lines.append("")
    lines.append(f"**Date**: {summary['date']}")
    lines.append(
        f"**Candidates combined**: {summary['n_candidates_combined']} "
        f"(yesterday mound@50 m: {summary['n_yesterday_mound_50m']}, "
        f"today re-reviewed: {summary['n_today_reviewed']})"
    )
    lines.append(
        f"**Student GT (null reference)**: {summary['n_student_gt']} "
        f"at {summary['student_gt_density_per_km2']} per km²"
    )
    lines.append(
        f"**Reviewer-promoted real mounds**: "
        f"{summary['n_reviewer_promoted']}"
    )
    lines.append(
        f"**Total real-mound universe**: "
        f"{summary['n_real_mound_universe']} at "
        f"{summary['real_mound_density_per_km2']} per km² "
        f"(bias-correction factor "
        f"{summary['bias_correction_factor']})"
    )
    lines.append(
        f"**Study area**: {summary['study_area_km2']} km² "
        f"(55-map evaluation bounds, 8,541 tiles)"
    )
    lines.append(
        f"**Permutations**: {summary['permutations']}, seed "
        f"{summary['seed']}"
    )
    lines.append("")
    lines.append("## Cumulative lift — P(mound within R | candidate)")
    lines.append("")
    lines.append(cum_df.to_markdown(index=False))
    lines.append("")
    lines.append("## Annular (shell) lift — new mounds per band")
    lines.append("")
    lines.append(shell_df.to_markdown(index=False))
    lines.append("")
    lines.append("## Ripley's cross-L (centred at zero)")
    lines.append("")
    lines.append(
        "Observed $L_{12}(r) - r$ above the null envelope indicates "
        "attraction (clustering of detection centroids near mounds). "
        "Crossings into the envelope indicate the scale at which "
        "clustering becomes indistinguishable from within-tile null."
    )
    lines.append("")
    lines.append(ripley_df.to_markdown(index=False))
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- **Signal fraction** at each R tells you what share of "
        "``mound-within-R`` candidates are genuine attractor-pulls "
        "rather than coincidental mounds happening to fall near a "
        "random detection in the same tile. A value near 1 means the "
        "observed rate is almost entirely real clustering; near 0 "
        "means the rate is essentially what random placement would "
        "produce."
    )
    lines.append(
        "- **Lift ratio** is observed / null — how many times more "
        "often mounds appear within R than random placement would "
        "predict. Decays toward 1 as R grows and incidental mounds "
        "dominate."
    )
    lines.append(
        "- **Shell analysis** isolates the band-specific effect: the "
        "50 m shell is yesterday's TP pool (frozen); the 50-75 m and "
        "75-100 m shells capture the attractor-pull effect; shells "
        "beyond 150 m admit increasingly incidental mounds. A signal "
        "fraction per shell falling below ~50 % is the honest ceiling "
        "for practitioner-useful detection at that tolerance."
    )
    lines.append(
        "- **Ripley's cross-L** is a second-line confirmation. "
        "Observed above the envelope → detections attract mounds at "
        "that scale. The crossover into the envelope marks where the "
        "spatial relationship becomes statistically indistinguishable "
        "from tile-conditional randomness."
    )
    lines.append("")
    with open(OUT_DIR / "report_autogen.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
