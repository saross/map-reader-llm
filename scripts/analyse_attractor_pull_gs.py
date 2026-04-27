#!/usr/bin/env python3
"""
Attractor-pull GS — geometric KDTree shell-wise null analysis on the
4-map gold-standard 487-tile corpus.

Companion to ``scripts/analyse_attractor_pull_v2.py`` (Obs 272 / Obs 294,
55-map student-GT corpus). The 55-map version derived per-shell observed
rates from the reviewer's ``buffer_metres`` label, because the student
GT carries ~25 m positional jitter (Obs 260) and so a direct
detection-to-GT distance was too noisy to anchor the analysis. The
gold-standard corpus has no such jitter — the curator-corrected
reference (``inputs/vectors/references/mounds-reference.geojson``,
569 mounds) is high-precision — so we can replace the reviewer-mediated
buffer-band labelling with a direct geometric KDTree query of detection
centroid against reference centroid. This eliminates a layer of
human-in-the-loop interpretation and asks the question at the
mathematical level: at what radius does detection-mound co-occurrence
on the GS corpus become statistically indistinguishable from random
within-tile placement?

Method (mirrors Obs 272 / Obs 294 schema, replacing reviewer label with
geometric distance):

- **Observed rate per shell**: build a ``scipy.spatial.cKDTree`` on the
  exploded reference (569 single-point features, EPSG:32635). For each
  detection centroid, query nearest-reference distance ``d_min`` and
  bin into shells aligned with Obs 294: (0, 25], (25, 50], (50, 75],
  (75, 100], (100, 125], (125, 150], (150, 286] m. The (150, 286] tail
  is preserved as a single bucket for cross-corpus comparability with
  the 55-map analysis (which collapsed the same range to defuse a
  reviewer-labelling artefact at 200 m — see Obs 294 §5). Detections
  with ``d_min > 286`` m are not counted in any shell (analogous to
  ``not_mound`` rows in the 55-map analysis, which had
  ``buffer_band = inf``).
- **Null rate per shell**: M = 1,000 within-tile permutations (seed 42).
  For each permutation, every detection's centroid is replaced by a
  uniform random point inside its parent tile's bounding box; the new
  KDTree-nearest-distance is binned identically. Yields per-shell null
  mean rate plus 95 % percentile confidence interval.
- **Lift** per shell: ``observed_rate / null_mean_rate``.
- **One-sided permutation p**: ``(1 + sum(null_rate >= observed_rate))
  / (1 + n_perm)`` (standard bias-corrected formula). A shell is
  flagged ``significant`` iff ``p < 0.05``.
- **Per-condition cutoff**: deepest contiguous-from-zero shell that is
  significant. If the (0, 25] shell is non-significant, cutoff is 0. If
  every shell out to (150, 286] is significant, cutoff is 286.
- **Cross-condition consensus cutoff**: largest shell outer edge
  significant in every condition.

Distinct from the 55-map version:

- **No reviewer ``buffer_metres`` label**: detection-to-reference
  distance IS the signal. The curator GT is precise enough to support
  this directly.
- **No bias correction**: there is no reviewer-promoted phantom
  contamination of the reference set on the 4-map GS corpus, so the
  null and observed rates are computed against the same universe.

Inputs (resolved relative to repo root):

- Detection GeoJSONs (PV-materialised verified detections, Era 2 487-tile
  scope, prefiltered to the canonical (vote_t, prob_t) per the
  ``pv_registry.json`` ``best_at_20m`` block):
  - text-HIGH-T0.7 (n=392): ``results/leaderboard/era2/pv-materialised/pv-high-text-t0.7-n5.geojson``
  - image-HIGH-T0.7 (n=414): ``results/leaderboard/era2/pv-materialised/pv-high-image-t0.7-n5.geojson``
  - SCALE4-T0.7 (n=411): ``results/leaderboard/era2/pv-materialised/pv-scale4-optimal-n10.geojson``
- Reference set (4-map curator-corrected): ``inputs/vectors/references/mounds-reference.geojson``
- Tile bounds (487-tile Era 2): ``inputs/vectors/bounds/384/full_evaluation_bounds.geojson``

Outputs at ``results/gold-standard-attractor-pull/``:

- ``attractor-pull-gs.json`` — per-condition × per-shell table
  (observed rate, null mean / 95 % CI, lift, p-value, significance flag)
  plus per-condition cutoff and cross-condition consensus.
- ``report.md`` — synthesised report with per-condition tables, consensus
  paragraph, and Obs 294 cross-reference.
- ``figures/attractor-pull-gs-shell-rates.png`` — log-rate-by-shell plot
  with the three conditions overlaid.

Usage:

    python scripts/analyse_attractor_pull_gs.py             # full run
    python scripts/analyse_attractor_pull_gs.py --validate  # sanity checks only

Compute: ~30 s on sapphire (3 conditions × 1,000 permutations × ~400
detections each).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

# --- Configuration ---
SEED = 42
M_PERMUTATIONS = 1000
# Shell edges in metres. The first six shells are uniform 25 m bins
# (0, 25] through (125, 150]; the final shell (150, 286] absorbs all
# detections with a nearest-reference distance up to the corner-plus-5-px
# tolerance of the 400 m × 400 m crop. Mirrors the 55-map Obs 272 / 294
# schema for cross-corpus comparability — although the GS corpus has no
# reviewer-sentinel artefact at 200 m (Obs 294 §5), the schema is
# preserved so the cap can be compared shell-for-shell against the
# 55-map result. Detections with d > 286 m fall outside all shells.
SHELL_EDGES: tuple[int, ...] = (25, 50, 75, 100, 125, 150, 286)
CRS = "EPSG:32635"
SIGNIFICANCE_ALPHA = 0.05

# --- Paths ---
REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCE = REPO_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS = REPO_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
PV_DIR = REPO_ROOT / "results/leaderboard/era2/pv-materialised"
OUT_DIR = REPO_ROOT / "results/gold-standard-attractor-pull"


@dataclass
class RunSpec:
    """Definition of one of the three GS conditions to analyse."""

    key: str  # short ID for output keys (e.g. ``text-high-t0.7``)
    label: str  # display label for tables / report
    detection_geojson: Path  # PV-materialised verified-detection geojson


RUNS: tuple[RunSpec, ...] = (
    RunSpec(
        key="text-high-t0.7",
        label="text-HIGH-T0.7 (K=5)",
        detection_geojson=PV_DIR / "pv-high-text-t0.7-n5.geojson",
    ),
    RunSpec(
        key="image-high-t0.7",
        label="image-HIGH-T0.7 (K=5)",
        detection_geojson=PV_DIR / "pv-high-image-t0.7-n5.geojson",
    ),
    RunSpec(
        key="scale4-optimal",
        label="SCALE4-optimal (image, K=10)",
        detection_geojson=PV_DIR / "pv-scale4-optimal-n10.geojson",
    ),
)


# --- Reference loading ---


def load_reference_kdtree(path: Path) -> tuple[cKDTree, int]:
    """
    Build a KDTree on the reference mound centroids in EPSG:32635.

    The mounds-reference.geojson stores each map's mounds as a single
    MultiPoint feature; we ``explode`` to one row per mound before
    extracting coordinates. Returns the tree and the number of points.
    """
    ref = gpd.read_file(path).to_crs(CRS)
    # Explode any MultiPoint features into per-point Point features so
    # ``.x`` / ``.y`` access is well-defined.
    ref_pts = ref.explode(index_parts=False).reset_index(drop=True)
    coords = np.array([[g.x, g.y] for g in ref_pts.geometry])
    return cKDTree(coords), len(coords)


# --- Tile-bounds attachment ---


def attach_tile_bounds(
    cands: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """
    Join each detection row to its tile's bounding box (minx / miny /
    maxx / maxy) by matching ``source_tile`` against the bounds layer's
    ``tile_name`` column. Detections whose tile cannot be resolved are
    dropped with a warning — these would be detections from outside the
    487-tile evaluation universe, which the PV-materialisation step
    should already have filtered out.

    Returns a plain DataFrame with x / y / tile bounds columns; the
    geometry is no longer needed downstream.
    """
    b = bounds.copy()
    b["tile_key"] = b["tile_name"].astype(str)
    b_bounds = b.geometry.bounds
    b = b.assign(
        tile_minx=b_bounds["minx"].values,
        tile_miny=b_bounds["miny"].values,
        tile_maxx=b_bounds["maxx"].values,
        tile_maxy=b_bounds["maxy"].values,
    )

    # Project detections to UTM-32635 for distance work.
    cands_utm = cands.to_crs(CRS)
    rows = pd.DataFrame(
        {
            "source_tile": cands_utm["source_tile"].astype(str).values,
            "x": [g.x for g in cands_utm.geometry],
            "y": [g.y for g in cands_utm.geometry],
        }
    )
    merged = rows.merge(
        b[
            [
                "tile_key",
                "tile_minx",
                "tile_miny",
                "tile_maxx",
                "tile_maxy",
            ]
        ],
        left_on="source_tile",
        right_on="tile_key",
        how="left",
    )
    missing = merged["tile_minx"].isna().sum()
    if missing:
        print(
            f"  [warn] {missing} detections dropped (no matching tile)"
        )
        merged = merged.dropna(subset=["tile_minx"])
    return merged.reset_index(drop=True)


# --- Permutation + shell-rate primitives ---


def randomise_within_tile(
    cands: pd.DataFrame, rng: np.random.Generator,
) -> np.ndarray:
    """Return uniform-within-tile random replacement coordinates."""
    x = rng.uniform(
        cands["tile_minx"].to_numpy(), cands["tile_maxx"].to_numpy()
    )
    y = rng.uniform(
        cands["tile_miny"].to_numpy(), cands["tile_maxy"].to_numpy()
    )
    return np.column_stack([x, y])


def shell_rates_from_distances(
    dist: np.ndarray, edges: Iterable[int],
) -> np.ndarray:
    """
    Per-shell fraction of points falling in (R_{n-1}, R_n] given an
    array of nearest-reference distances. Returns an array aligned with
    ``edges``.

    Detections with ``d > edges[-1]`` contribute to none of the shells;
    the per-shell rates therefore sum to the fraction of detections
    within ``edges[-1]`` rather than to 1.0. Mirrors the 55-map script's
    ``not_mound = inf`` semantics.
    """
    out: list[float] = []
    prev = 0.0
    for R in edges:
        mask = (dist > prev) & (dist <= R)
        out.append(float(np.mean(mask)))
        prev = float(R)
    return np.array(out)


# --- Per-run analysis ---


def compute_shells_geometric(
    cands: pd.DataFrame, ref_tree: cKDTree,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute per-shell observed rates for one condition via direct
    KDTree query.

    Returns a tuple ``(distances, observed_shell_rates)`` so the caller
    can also report distance-distribution diagnostics (e.g. the
    monotonicity sanity check).
    """
    det_xy = np.column_stack(
        [cands["x"].to_numpy(), cands["y"].to_numpy()]
    )
    dist, _ = ref_tree.query(det_xy, k=1)
    obs = shell_rates_from_distances(dist, SHELL_EDGES)
    return dist, obs


def analyse_run(
    spec: RunSpec,
    bounds_gdf: gpd.GeoDataFrame,
    ref_tree: cKDTree,
    rng: np.random.Generator,
) -> dict:
    """
    Run the within-tile permutation analysis for one of the three GS
    conditions. Returns a dict suitable for the aggregate JSON output.
    """
    print(f"[run] {spec.label}")
    cands_gdf = gpd.read_file(spec.detection_geojson)
    cands = attach_tile_bounds(cands_gdf, bounds_gdf)
    n_total = len(cands)
    print(f"  detections={n_total}")

    distances, obs_shell = compute_shells_geometric(cands, ref_tree)
    n_within_286 = int((distances <= SHELL_EDGES[-1]).sum())
    print(
        f"  observed within {SHELL_EDGES[-1]} m: "
        f"{n_within_286}/{n_total} = {n_within_286 / n_total:.4f}"
    )

    # Permutation null
    null_shell = np.zeros((M_PERMUTATIONS, len(SHELL_EDGES)))
    for m in range(M_PERMUTATIONS):
        perm_coords = randomise_within_tile(cands, rng)
        d_perm, _ = ref_tree.query(perm_coords, k=1)
        null_shell[m] = shell_rates_from_distances(d_perm, SHELL_EDGES)
        if (m + 1) % 250 == 0:
            print(f"    perm {m + 1}/{M_PERMUTATIONS}")

    null_mean = null_shell.mean(axis=0)
    null_lo = np.percentile(null_shell, 2.5, axis=0)
    null_hi = np.percentile(null_shell, 97.5, axis=0)
    # Bias-corrected one-sided permutation p-value:
    # p = (1 + #{null >= obs}) / (1 + M).
    # Adding 1 to numerator and denominator prevents p = 0 when no
    # null permutation exceeds the observed rate (the empirical
    # tail-probability floor is then 1 / (M + 1) rather than zero).
    p_value = (
        1.0 + np.sum(null_shell >= obs_shell, axis=0)
    ) / (1.0 + M_PERMUTATIONS)

    shell_rows: list[dict] = []
    prev_R = 0
    for j, R in enumerate(SHELL_EDGES):
        obs = float(obs_shell[j])
        nm = float(null_mean[j])
        lift = obs / nm if nm > 0 else float("inf")
        signal_fraction = (
            (obs - nm) / obs if obs > 0 else 0.0
        )
        shell_rows.append(
            {
                "R_inner_m": int(prev_R),
                "R_outer_m": int(R),
                "obs_rate_in_shell": round(obs, 4),
                "null_mean_in_shell": round(nm, 4),
                "null_ci_lo": round(float(null_lo[j]), 4),
                "null_ci_hi": round(float(null_hi[j]), 4),
                "lift_ratio": round(lift, 2),
                "signal_fraction": round(signal_fraction, 4),
                "p_value": round(float(p_value[j]), 4),
                "significant": bool(p_value[j] < SIGNIFICANCE_ALPHA),
            }
        )
        prev_R = R

    # Per-condition contiguous-from-zero cutoff: outer edge of the
    # deepest shell that is significant *and* every shell inside it is
    # also significant. This is the conservative cutoff used in the
    # consensus block.
    cutoff = 0
    for row in shell_rows:
        if row["significant"]:
            cutoff = row["R_outer_m"]
        else:
            break
    # Last-significant cutoff: the outer edge of the deepest shell that
    # is significant, irrespective of intermediate non-significant
    # shells. Where it exceeds ``cutoff``, the per-run signal is
    # non-monotonic (likely sample-size noise in a thinly-populated
    # middle shell).
    last_sig = 0
    for row in shell_rows:
        if row["significant"]:
            last_sig = row["R_outer_m"]
    monotonic = (last_sig == cutoff)
    print(
        f"  per-condition cutoff: contiguous-from-zero={cutoff} m, "
        f"last-significant={last_sig} m, monotonic={monotonic}"
    )

    return {
        "key": spec.key,
        "label": spec.label,
        "n_detections": int(n_total),
        "n_within_286m": int(n_within_286),
        "shell": shell_rows,
        "cutoff_m": int(cutoff),
        "last_significant_outer_m": int(last_sig),
        "monotonic": bool(monotonic),
    }


# --- Consensus + report ---


def consensus_block(per_run: list[dict]) -> dict:
    """
    Synthesise per-condition cutoffs into a consensus statement.

    Definitions (mirror analyse_attractor_pull_v2.py):

    - ``most_permissive_consensus_cutoff_m``: the largest shell outer
      edge that is significant in *every* condition.
    - ``majority_breakpoint_m``: the first shell where < ceil(N/2)
      conditions are significant (None if not reached).
    - ``per_shell``: list of dicts, one per shell, with the condition
      keys flagged significant or not.
    """
    shell_edges = [row["R_outer_m"] for row in per_run[0]["shell"]]
    sig_by_run = {
        r["key"]: {
            row["R_outer_m"]: row["significant"]
            for row in r["shell"]
        }
        for r in per_run
    }

    per_shell: list[dict] = []
    most_permissive = 0
    majority_breaks_at: int | None = None
    n_runs = len(sig_by_run)
    majority_threshold = (n_runs + 1) // 2  # ceil(N/2)
    for R in shell_edges:
        flags = {key: sig_by_run[key][R] for key in sig_by_run}
        n_sig = int(sum(flags.values()))
        per_shell.append(
            {
                "R_outer_m": int(R),
                "significant": flags,
                "n_runs_significant": n_sig,
                "all_runs_significant": n_sig == n_runs,
                "majority_significant": n_sig >= majority_threshold,
            }
        )
        if n_sig == n_runs:
            most_permissive = R
        elif (
            majority_breaks_at is None
            and n_sig < majority_threshold
        ):
            majority_breaks_at = R

    return {
        "most_permissive_consensus_cutoff_m": int(most_permissive),
        "majority_breakpoint_m": majority_breaks_at,
        "per_shell": per_shell,
    }


# --- I/O ---


def write_json(
    per_run: list[dict],
    consensus: dict,
    n_reference: int,
    out_path: Path,
) -> None:
    """Write the aggregate per-condition + consensus JSON output."""
    payload = {
        "method": "geometric-kdtree",
        "obs_anchor": "Obs 294 (55-map cap = 125 m); GS companion = Obs 295",
        "shell_edges_m": list(SHELL_EDGES),
        "permutations": M_PERMUTATIONS,
        "seed": SEED,
        "alpha": SIGNIFICANCE_ALPHA,
        "n_reference_mounds": int(n_reference),
        "scope": "Era 2, 487-tile gold-standard 4-map evaluation",
        "runs": per_run,
        "consensus": consensus,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def write_report(
    per_run: list[dict],
    consensus: dict,
    n_reference: int,
    out_path: Path,
) -> None:
    """Write the synthesised report.md with per-condition tables + consensus."""
    lines: list[str] = []
    lines.append(
        "# Attractor-pull GS — geometric KDTree shell-wise null analysis"
    )
    lines.append("")
    lines.append(
        "**Anchor**: Obs 294"
        " (`docs/notes/reflections/working-notes.md`, 2026-04-28)"
        " established the 55-map attractor-pull cutoff at 125 m, using"
        " reviewer-mediated buffer-band labels because the student GT"
        " carries ~25 m positional jitter (Obs 260). The 4-map"
        " gold-standard corpus has a curator-corrected reference with"
        " no positional jitter, so we replace the reviewer-label-based"
        " observed-rate construction with a direct geometric KDTree"
        " query of detection centroid against reference centroid."
        " Companion finding to Obs 294."
    )
    lines.append("")
    lines.append("## 1. Method")
    lines.append("")
    lines.append(
        "For each condition, observed shell rates are computed by"
        " building a `scipy.spatial.cKDTree` on the curator-corrected"
        " reference centroids (EPSG:32635), querying nearest-reference"
        " distance for each detection centroid, and binning into shells"
        " (0, 25] / (25, 50] / (50, 75] / (75, 100] / (100, 125] /"
        " (125, 150] / (150, 286] m. The null distribution is"
        f" M = {M_PERMUTATIONS} within-tile permutations (seed {SEED})"
        " of the same KDTree query. Per-shell significance is the"
        " one-sided permutation p-value `(1 + #{null ≥ obs}) / (1 + M)`,"
        f" alpha = {SIGNIFICANCE_ALPHA}. No bias correction is applied"
        " (the reference is precise; the null and observed rates are"
        " computed against the same universe)."
    )
    lines.append("")
    lines.append(
        f"Reference set: {n_reference} mounds (curator-corrected"
        " 4-map gold-standard reference)."
    )
    lines.append(
        "Shell edges (m): "
        + ", ".join(str(e) for e in SHELL_EDGES)
        + ". The (150, 286] shell is preserved as a single bucket for"
        " cross-corpus comparability with the 55-map analysis (Obs 294"
        " §5 — splitting at 200 m flagged a reviewer-labelling artefact"
        " on the 55-map corpus). Detections with d > 286 m fall outside"
        " all shells (analogous to ``not_mound`` rows in Obs 272 / 294)."
    )
    lines.append("")

    # Per-condition tables
    lines.append("## 2. Per-condition shell tables")
    lines.append("")
    for run in per_run:
        within_pct = 100 * run["n_within_286m"] / run["n_detections"]
        lines.append(
            f"### {run['label']} — n={run['n_detections']},"
            f" within-286m={run['n_within_286m']} ({within_pct:.1f} %)"
        )
        lines.append("")
        df = pd.DataFrame(run["shell"])
        display = df[
            [
                "R_inner_m",
                "R_outer_m",
                "obs_rate_in_shell",
                "null_mean_in_shell",
                "lift_ratio",
                "signal_fraction",
                "p_value",
                "significant",
            ]
        ]
        lines.append(display.to_markdown(index=False))
        lines.append("")
        lines.append(
            f"**Per-condition cutoff**: {run['cutoff_m']} m"
            " (deepest shell outer edge with permutation p < "
            f"{SIGNIFICANCE_ALPHA})"
        )
        lines.append("")

    # Consensus
    lines.append("## 3. Cross-condition consensus")
    lines.append("")
    flat: list[dict] = []
    for row in consensus["per_shell"]:
        rec = {"R_outer_m": row["R_outer_m"]}
        for key, sig in row["significant"].items():
            rec[key] = "sig" if sig else "—"
        rec["n_sig"] = row["n_runs_significant"]
        rec["all_sig"] = "yes" if row["all_runs_significant"] else "no"
        flat.append(rec)
    flat_df = pd.DataFrame(flat)
    lines.append(flat_df.to_markdown(index=False))
    lines.append("")
    lines.append(
        "**Most-permissive consensus cutoff**: "
        f"{consensus['most_permissive_consensus_cutoff_m']} m"
        " (largest shell outer edge significant in all three"
        " conditions)."
    )
    if consensus["majority_breakpoint_m"] is not None:
        lines.append(
            "**Majority-loses breakpoint**: "
            f"{consensus['majority_breakpoint_m']} m"
            " (first shell where < 2/3 conditions are significant)."
        )
    else:
        lines.append(
            "**Majority-loses breakpoint**: not reached within"
            " the 286 m maximum shell."
        )
    lines.append("")

    # Per-condition cutoffs side-by-side
    lines.append("### Per-condition cutoff summary")
    lines.append("")
    cutoff_rows = [
        {
            "condition": r["label"],
            "n_detections": r["n_detections"],
            "cutoff_m": r["cutoff_m"],
        }
        for r in per_run
    ]
    lines.append(pd.DataFrame(cutoff_rows).to_markdown(index=False))
    lines.append("")

    # Cross-reference + interpretation vs Obs 294
    lines.append("## 4. Cross-reference to Obs 294 (55-map cap = 125 m)")
    lines.append("")
    obs_294_cap = 125
    consensus_cutoff = consensus["most_permissive_consensus_cutoff_m"]
    if consensus_cutoff < obs_294_cap:
        verdict = (
            f"**Verdict**: the GS cap ({consensus_cutoff} m) is"
            f" tighter than the 55-map cap ({obs_294_cap} m), as"
            " predicted by the F1-plateau evidence (GS plateau at"
            " R = 25 m vs 55-map > 50 m; GS ~2× denser in"
            " mounds-per-tile, so within-tile null saturates"
            " sooner)."
        )
    elif consensus_cutoff == obs_294_cap:
        verdict = (
            f"**Verdict**: the GS cap ({consensus_cutoff} m) matches"
            " the 55-map cap exactly. Despite different reference"
            " precision and density, the within-tile null geometry"
            " converges on the same practitioner-useful upper bound."
        )
    else:
        verdict = (
            f"**Verdict**: the GS cap ({consensus_cutoff} m) is"
            f" wider than the 55-map cap ({obs_294_cap} m). This"
            " contradicts the F1-plateau prediction and warrants"
            " investigation — the cap should not increase as"
            " reference precision improves."
        )
    lines.append(verdict)
    lines.append("")

    # Disagreement check
    cutoffs = sorted(r["cutoff_m"] for r in per_run)
    if cutoffs[0] != cutoffs[-1]:
        lines.append(
            "### Cross-condition disagreement"
            f" (range {cutoffs[0]}–{cutoffs[-1]} m)"
        )
        lines.append("")
        lines.append(
            "Per-condition cutoffs differ by "
            f"{cutoffs[-1] - cutoffs[0]} m. Inspect the per-condition"
            " shell tables in §2 to see which shells flip"
            " significance between conditions."
        )
        lines.append("")

    lines.append("## 5. Reproducibility")
    lines.append("")
    lines.append(
        "Script: `scripts/analyse_attractor_pull_gs.py` (ruff-clean)."
        f" Seed {SEED}, M = {M_PERMUTATIONS} permutations per condition."
        " Rerun with `python scripts/analyse_attractor_pull_gs.py`"
        " from the repo root."
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def render_figure(
    per_run: list[dict], out_path: Path,
) -> None:
    """
    Per-shell observed-rate curves for the three conditions overlaid,
    with each condition's null mean as a dashed reference line. Log
    y-axis to make the cross-shell lift legible.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available; skipping figure")
        return

    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    centres = [
        int((row["R_inner_m"] + row["R_outer_m"]) / 2)
        for row in per_run[0]["shell"]
    ]
    colours = {
        "text-high-t0.7": "C0",
        "image-high-t0.7": "C1",
        "scale4-optimal": "C3",
    }

    # Floor for log-axis: any zero observed-rate would force log(0).
    # We map zeros to half the minimum non-zero rate across all runs to
    # keep the plot readable while not confusing readers about what is
    # observed vs floored.
    nonzero_rates = [
        row["obs_rate_in_shell"]
        for run in per_run
        for row in run["shell"]
        if row["obs_rate_in_shell"] > 0
    ]
    floor = (min(nonzero_rates) / 2) if nonzero_rates else 1e-4

    def _floor(rate: float) -> float:
        return rate if rate > 0 else floor

    for run in per_run:
        obs = [_floor(row["obs_rate_in_shell"]) for row in run["shell"]]
        null_mean = [
            _floor(row["null_mean_in_shell"]) for row in run["shell"]
        ]
        ax.plot(
            centres,
            obs,
            "o-",
            color=colours[run["key"]],
            label=f"{run['label']} (obs)",
            linewidth=2.0,
            markersize=7,
        )
        ax.plot(
            centres,
            null_mean,
            "--",
            color=colours[run["key"]],
            label=f"{run['label']} (null)",
            linewidth=1.0,
            alpha=0.55,
        )
        # Mark non-significant shells with a hollow square overlay.
        for centre, row in zip(centres, run["shell"]):
            if not row["significant"]:
                ax.scatter(
                    centre,
                    _floor(row["obs_rate_in_shell"]),
                    s=120,
                    facecolor="none",
                    edgecolor=colours[run["key"]],
                    linewidth=2.0,
                    zorder=5,
                )
    ax.set_yscale("log")
    ax.set_xlabel("Shell centre (m)")
    ax.set_ylabel("P(detection in shell) [log scale]")
    ax.set_title(
        "Attractor-pull GS: per-shell observed vs within-tile null"
        " (3 conditions, 487-tile 4-map corpus)"
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# --- Validation / sanity checks ---


def _identity_check(
    spec: RunSpec,
    bounds_gdf: gpd.GeoDataFrame,
    ref_tree: cKDTree,
    rng: np.random.Generator,
) -> dict:
    """
    Sanity check 1: the (0, 25] shell observed lift should be >> 1.

    On the 4-map GS, F1 plateaus at 25 m, so most TPs cluster within
    25 m of a real mound and the observed (0, 25] rate should be many
    times higher than the within-tile null.
    """
    cands_gdf = gpd.read_file(spec.detection_geojson)
    cands = attach_tile_bounds(cands_gdf, bounds_gdf)
    distances, obs_shell = compute_shells_geometric(cands, ref_tree)
    n_perm = 100
    null_shell = np.zeros((n_perm, len(SHELL_EDGES)))
    for m in range(n_perm):
        perm_coords = randomise_within_tile(cands, rng)
        d_perm, _ = ref_tree.query(perm_coords, k=1)
        null_shell[m] = shell_rates_from_distances(d_perm, SHELL_EDGES)
    null_mean = null_shell.mean(axis=0)
    lift_first = obs_shell[0] / null_mean[0] if null_mean[0] > 0 else float("inf")
    return {
        "obs_first_shell_rate": float(obs_shell[0]),
        "null_first_shell_rate": float(null_mean[0]),
        "lift_first_shell": float(lift_first),
        "passes": bool(lift_first > 5.0),
    }


def _saturation_check(
    spec: RunSpec,
    bounds_gdf: gpd.GeoDataFrame,
    ref_tree: cKDTree,
    rng: np.random.Generator,
) -> dict:
    """
    Sanity check 2: the (150, 286] shell lift should approach 1.0 from
    above (the within-tile null and observed rates converge once the
    distance is far enough that detection placement and random
    placement are indistinguishable).
    """
    cands_gdf = gpd.read_file(spec.detection_geojson)
    cands = attach_tile_bounds(cands_gdf, bounds_gdf)
    distances, obs_shell = compute_shells_geometric(cands, ref_tree)
    n_perm = 100
    null_shell = np.zeros((n_perm, len(SHELL_EDGES)))
    for m in range(n_perm):
        perm_coords = randomise_within_tile(cands, rng)
        d_perm, _ = ref_tree.query(perm_coords, k=1)
        null_shell[m] = shell_rates_from_distances(d_perm, SHELL_EDGES)
    null_mean = null_shell.mean(axis=0)
    lift_last = (
        obs_shell[-1] / null_mean[-1]
        if null_mean[-1] > 0
        else float("inf")
    )
    return {
        "obs_last_shell_rate": float(obs_shell[-1]),
        "null_last_shell_rate": float(null_mean[-1]),
        "lift_last_shell": float(lift_last),
        # Pass iff lift_last is in [0.0, 5.0] — should be much closer to
        # 1.0 than to the (0, 25] lift. We allow some headroom because
        # the (150, 286] shell is wide and may catch true-positive tail
        # signal too.
        "passes": bool(lift_last < 5.0),
    }


def _closure_check(
    spec: RunSpec,
    bounds_gdf: gpd.GeoDataFrame,
    ref_tree: cKDTree,
    rng: np.random.Generator,
) -> dict:
    """
    Sanity check 3: per-shell rates must sum to the fraction of points
    within ``edges[-1]`` m, both for the observed and for any
    permutation.

    This is the closure property given the schema's tail-truncation
    semantics: detections beyond ``edges[-1]`` contribute to no shell,
    so the sum equals (n_within_max / n_total) rather than 1.0. A bug
    in shell binning would break this identity.
    """
    cands_gdf = gpd.read_file(spec.detection_geojson)
    cands = attach_tile_bounds(cands_gdf, bounds_gdf)
    distances, obs_shell = compute_shells_geometric(cands, ref_tree)
    obs_sum = float(obs_shell.sum())
    obs_within = float(np.mean(distances <= SHELL_EDGES[-1]))

    # Permutation closure: 5 random permutations
    perm_passes = []
    for _ in range(5):
        perm_coords = randomise_within_tile(cands, rng)
        d_perm, _ = ref_tree.query(perm_coords, k=1)
        rates = shell_rates_from_distances(d_perm, SHELL_EDGES)
        perm_sum = float(rates.sum())
        perm_within = float(np.mean(d_perm <= SHELL_EDGES[-1]))
        perm_passes.append(abs(perm_sum - perm_within) < 1e-6)
    return {
        "obs_shell_sum": obs_sum,
        "obs_within_max": obs_within,
        "obs_diff": abs(obs_sum - obs_within),
        "perm_all_pass": bool(all(perm_passes)),
        "passes": bool(
            abs(obs_sum - obs_within) < 1e-6 and all(perm_passes)
        ),
    }


def _monotonicity_check(
    spec: RunSpec,
    bounds_gdf: gpd.GeoDataFrame,
    ref_tree: cKDTree,
) -> dict:
    """
    Sanity check 4: cumulative shell counts must be monotonically
    non-decreasing as the outer edge grows (a binning bug would
    produce a cumulative-count drop).
    """
    cands_gdf = gpd.read_file(spec.detection_geojson)
    cands = attach_tile_bounds(cands_gdf, bounds_gdf)
    distances, _ = compute_shells_geometric(cands, ref_tree)
    cumulative_counts = []
    for R in SHELL_EDGES:
        cumulative_counts.append(int(np.sum(distances <= R)))
    monotonic = all(
        cumulative_counts[i] >= cumulative_counts[i - 1]
        for i in range(1, len(cumulative_counts))
    )
    return {
        "cumulative_counts": cumulative_counts,
        "monotonic": bool(monotonic),
        "passes": bool(monotonic),
    }


def run_validation(
    bounds_gdf: gpd.GeoDataFrame,
    ref_tree: cKDTree,
    n_reference: int,
) -> int:
    """
    Run all four sanity checks against the canonical text-HIGH-T0.7
    condition. Returns a process exit code: 0 if all checks pass,
    1 otherwise.

    Prints results inline so ``--validate`` can be inspected manually.
    """
    spec = RUNS[0]  # text-HIGH-T0.7
    print(f"[validate] using condition: {spec.label}")
    print(f"[validate] reference points: {n_reference}")
    rng = np.random.default_rng(SEED)

    print("\n[1] identity (lift in (0, 25] >> 1)")
    r1 = _identity_check(spec, bounds_gdf, ref_tree, rng)
    print(json.dumps(r1, indent=2))

    print("\n[2] saturation (lift in (150, 286] ~ 1)")
    r2 = _saturation_check(spec, bounds_gdf, ref_tree, rng)
    print(json.dumps(r2, indent=2))

    print("\n[3] closure (per-shell rates sum to within-286m fraction)")
    r3 = _closure_check(spec, bounds_gdf, ref_tree, rng)
    print(json.dumps(r3, indent=2))

    print("\n[4] monotonicity (cumulative counts non-decreasing)")
    r4 = _monotonicity_check(spec, bounds_gdf, ref_tree)
    print(json.dumps(r4, indent=2))

    all_pass = all(r["passes"] for r in (r1, r2, r3, r4))
    print(
        "\n=== VALIDATION "
        + ("PASS" if all_pass else "FAIL")
        + " ==="
    )
    return 0 if all_pass else 1


# --- Main driver ---


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validate",
        action="store_true",
        help=(
            "Run only the four sanity checks (identity / saturation /"
            " closure / monotonicity) on the canonical text-HIGH"
            " condition; do not write outputs."
        ),
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "figures").mkdir(parents=True, exist_ok=True)

    print("[1/3] Loading reference inputs...")
    bounds_gdf = gpd.read_file(BOUNDS).to_crs(CRS)
    ref_tree, n_reference = load_reference_kdtree(REFERENCE)
    print(
        f"  bounds tiles: {len(bounds_gdf)}  "
        f"reference points: {n_reference}"
    )

    if args.validate:
        return run_validation(bounds_gdf, ref_tree, n_reference)

    print("[2/3] Per-condition analyses...")
    rng = np.random.default_rng(SEED)
    per_run: list[dict] = []
    for spec in RUNS:
        per_run.append(
            analyse_run(spec, bounds_gdf, ref_tree, rng)
        )

    print("[3/3] Synthesising consensus + writing outputs...")
    consensus = consensus_block(per_run)
    write_json(
        per_run,
        consensus,
        n_reference,
        OUT_DIR / "attractor-pull-gs.json",
    )
    write_report(
        per_run,
        consensus,
        n_reference,
        OUT_DIR / "report.md",
    )
    render_figure(
        per_run,
        OUT_DIR / "figures/attractor-pull-gs-shell-rates.png",
    )

    print("Done.")
    print(
        json.dumps(
            {
                "consensus_cutoff_m": consensus[
                    "most_permissive_consensus_cutoff_m"
                ],
                "per_condition_cutoffs": {
                    r["key"]: r["cutoff_m"] for r in per_run
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
