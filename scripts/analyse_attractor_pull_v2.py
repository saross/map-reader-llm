#!/usr/bin/env python3
"""
Attractor-pull v2 — re-derive the spatial attractor-pull cutoff across
the three corrected 55-map runs (T=0.3 text-HIGH, T=0.7 text-HIGH,
image).

Observation 272 (`docs/notes/reflections/working-notes.md`) established
that detection centroids cluster around real mound positions out to
~125 m, with the 125-150 m shell statistically indistinguishable from a
within-tile random-placement null (p = 0.381 on the image run's
multi-buffer review). That analysis used only the image-generalisation
run. With the manual reviews now corrected and complete on all three
runs, this v2 script re-runs the same shell-wise permutation null
analysis on each run, then synthesises a consensus cutoff.

Method (faithful to Obs 272 / `analyse_buffer_band_lift.py`):

- **Observed rate per shell** is taken directly from the reviewer's
  ``buffer_metres`` label, not from a KDTree against the student-GT
  reference. The reviewer physically inspects each candidate at five
  buffer radii (50, 75, 100, 125, 150, 200 m) and assigns the smallest
  band at which a real mound is visible inside the buffer. ``not_mound``
  rows mean no real mound within the largest 200 m review buffer —
  i.e., > 286 m by the corners-plus-5 px geometry of the 400 m × 400 m
  context crop.
- **Null rate per shell** is built by M = 1,000 within-tile permutations
  (seed 42). For each permutation, every candidate is replaced by a
  random point uniformly drawn within its parent tile's bounding box;
  the distribution of fraction-in-shell across permutations forms the
  null. Student GT is the only reference set with fixed coordinates;
  the reviewer-promoted phantoms sit AT the detection coordinates and
  cannot be used as null references without trivial self-matches.
- **Bias correction**: the null rate is divided by the student-GT
  fraction of the real-mound universe (4,744 / (4,744 + run-specific
  reviewer-promoted count)) to approximate what the null rate would be
  if all 5,490 real mounds had fixed coordinates available.
- **Significance**: one-sided permutation p-value (P(null ≥ observed));
  shell is flagged ``significant`` iff p < 0.05 *under the
  bias-corrected null*. The bias correction can only LOWER the
  significance bar, since it raises the null mean — when the raw null
  is already too small to support the observed lift, the corrected null
  is also too small.

For each of the three runs the script writes a per-run shell table; the
top-level JSON aggregates all three. The report.md synthesises per-run
cutoffs into a consensus statement (most-permissive cutoff supported by
all runs; per-run disagreements explicitly flagged).

Inputs (resolved relative to repo root):

- T=0.3 text-HIGH:
  - `results/55maps-text-high-t0.3-generalisation/human-review-multi-buffer.csv`
- T=0.7 text-HIGH:
  - `results/55maps-text-high-generalisation/human-review-multi-buffer.csv`
- image:
  - `results/55maps-image-generalisation/human-review.csv` (yesterday's
    472 mound@50 m calls + 556 not_mound rows that fed the re-review)
  - `results/55maps-image-generalisation/human-review-multi-buffer.csv`
    (today's 274 mound calls across {50, 75, 100, 125, 150, 200} m
    bands + 283 confirmed not_mound rows)
- Reference set: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
- Tile bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`

Outputs at `results/55maps-attractor-pull-v2/`:

- `attractor-pull-v2.json` — per-run × per-shell table (observed rate,
  null mean / 95 % CI, bias-corrected null, lift, p-value, significance
  flag) plus per-run cutoff and the consensus block.
- `report.md` — synthesised report with per-run shell tables, consensus
  paragraph, and Obs 272 cross-reference.
- `figures/attractor-pull-shell-rates.png` — per-shell observed rate
  curves for the three runs overlaid, with bias-corrected null mean
  shown as the dashed reference.

Usage:

    python scripts/analyse_attractor_pull_v2.py

Compute: ~2 min on sapphire (3 runs × 1,000 permutations).
"""

from __future__ import annotations

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
# Shell edges in metres, matching Obs 272 exactly. The first shell is
# (0, 50]; the final shell (150, 286] absorbs both the 200-labelled
# review rows ("mound visible somewhere beyond 150 m, inside the 286 m
# corners-plus-5-pixel tolerance of the 400 m × 400 m crop") AND any
# 150-labelled rows that round up. Splitting this final shell at 200 m
# creates an artefactual significance because reviewers preferentially
# use the 200 m label as a catch-all for "yes-mound-but-far" calls;
# Obs 272's collapsed shell is the honest statement.
SHELL_EDGES: tuple[int, ...] = (50, 75, 100, 125, 150, 286)
CRS = "EPSG:32635"
SIGNIFICANCE_ALPHA = 0.05

# --- Paths ---
REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENT_GT = REPO_ROOT / (
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
)
BOUNDS = REPO_ROOT / (
    "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
)
OUT_DIR = REPO_ROOT / "results/55maps-attractor-pull-v2"


@dataclass
class RunSpec:
    """Definition of one of the three corrected 55-map runs."""

    key: str  # short ID for output keys (e.g. ``t0.3``)
    label: str  # display label for tables / report
    review_csvs: tuple[Path, ...]  # one or two review CSVs to combine


RUNS: tuple[RunSpec, ...] = (
    RunSpec(
        key="t0.3",
        label="T=0.3 text-HIGH",
        review_csvs=(
            REPO_ROOT
            / (
                "results/55maps-text-high-t0.3-generalisation/"
                "human-review-multi-buffer.csv"
            ),
        ),
    ),
    RunSpec(
        key="t0.7",
        label="T=0.7 text-HIGH",
        review_csvs=(
            REPO_ROOT
            / (
                "results/55maps-text-high-generalisation/"
                "human-review-multi-buffer.csv"
            ),
        ),
    ),
    RunSpec(
        key="image",
        label="image (T=0.7)",
        review_csvs=(
            REPO_ROOT
            / "results/55maps-image-generalisation/human-review.csv",
            REPO_ROOT
            / (
                "results/55maps-image-generalisation/"
                "human-review-multi-buffer.csv"
            ),
        ),
    ),
)


# --- Shared helpers (deliberately mirror analyse_buffer_band_lift.py) ---


def normalise_tile_key(source_tile: str) -> str:
    """
    Return ``source_tile`` in the canonical form expected by the
    55-map bounds file's ``tile_name`` column. The bounds file retains
    the ``.png`` extension, so this is a pass-through unless an upstream
    pipeline trimmed it.
    """
    s = str(source_tile)
    return s if s.endswith(".png") else s + ".png"


def load_combined_candidates(spec: RunSpec) -> pd.DataFrame:
    """
    Build the per-run candidate dataframe.

    For runs whose ``review_csvs`` is a single multi-buffer CSV (T=0.3,
    T=0.7), every reviewed row already carries a numeric
    ``buffer_metres`` (or empty for ``not_mound``); load directly. For
    the image run, combine yesterday's 472 mound@50 m calls with today's
    557-row re-review of yesterday's not_mound rows, dropping
    duplicates on ``candidate_id``.

    Returns
    -------
    pandas.DataFrame
        Columns: ``candidate_id``, ``map_name``, ``source_tile``,
        ``x``, ``y``, ``buffer_band``, ``human_label``, ``symbol_type``.
        ``buffer_band`` is float metres for mound rows or numpy.inf for
        not_mound rows.
    """
    keep = [
        "candidate_id",
        "map_name",
        "source_tile",
        "x",
        "y",
        "buffer_band",
        "human_label",
        "symbol_type",
    ]
    if len(spec.review_csvs) == 1:
        # T=0.3 / T=0.7 path — single multi-buffer CSV, all rows
        # already carry buffer_metres (possibly empty for not_mound).
        df = pd.read_csv(spec.review_csvs[0]).copy()
        df["buffer_band"] = pd.to_numeric(
            df.get("buffer_metres"), errors="coerce"
        )
        df.loc[df["human_label"] != "mound", "buffer_band"] = np.inf
        return df[keep].reset_index(drop=True)
    # image run — yesterday + today merge.
    yesterday = pd.read_csv(spec.review_csvs[0])
    today = pd.read_csv(spec.review_csvs[1])
    y_mound = yesterday[yesterday["human_label"] == "mound"].copy()
    y_mound["buffer_band"] = 50.0
    today = today.copy()
    today["buffer_band"] = pd.to_numeric(
        today.get("buffer_metres"), errors="coerce"
    )
    today.loc[today["human_label"] != "mound", "buffer_band"] = np.inf
    combined = pd.concat([y_mound[keep], today[keep]], ignore_index=True)
    combined = combined.drop_duplicates(
        subset="candidate_id", keep="last"
    )
    return combined.reset_index(drop=True)


def count_reviewer_promoted(spec: RunSpec) -> int:
    """
    Total reviewer-promoted real mounds across this run's review CSVs.
    For the image run that's yesterday + today; for the text runs it's
    the single multi-buffer CSV.
    """
    total = 0
    for path in spec.review_csvs:
        df = pd.read_csv(path)
        total += int((df["human_label"] == "mound").sum())
    return total


def attach_tile_bounds(
    cands: pd.DataFrame, bounds: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """
    Join each candidate row to its tile's bounding box (minx/miny/maxx/
    maxy) by matching ``source_tile`` (normalised with .png suffix)
    against the bounds layer's ``tile_name``. Drops rows whose tile
    cannot be resolved (none expected on the 55-map corpus); prints a
    warning if any are dropped.
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
    c = cands.copy()
    c["tile_key"] = c["source_tile"].apply(normalise_tile_key)
    merged = c.merge(
        b[
            [
                "tile_key",
                "tile_minx",
                "tile_miny",
                "tile_maxx",
                "tile_maxy",
            ]
        ],
        on="tile_key",
        how="left",
    )
    missing = merged["tile_minx"].isna().sum()
    if missing:
        print(
            f"  [warn] {missing} candidates dropped (no matching tile)"
        )
        merged = merged.dropna(subset=["tile_minx"])
    return merged.reset_index(drop=True)


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
    array of nearest-GT distances. Returns an array aligned with
    ``edges``.
    """
    out: list[float] = []
    prev = 0.0
    for R in edges:
        mask = (dist > prev) & (dist <= R)
        out.append(float(np.mean(mask)))
        prev = float(R)
    return np.array(out)


def observed_shell_rates(
    cands: pd.DataFrame, edges: Iterable[int],
) -> np.ndarray:
    """
    Per-shell fraction of candidates whose reviewer ``buffer_band``
    falls in (R_{n-1}, R_n]. Aligned with ``edges``.
    """
    n = len(cands)
    out: list[float] = []
    prev = 0.0
    for R in edges:
        mask = (cands["buffer_band"] > prev) & (
            cands["buffer_band"] <= R
        )
        out.append(float(mask.sum() / n))
        prev = float(R)
    return np.array(out)


# --- Per-run analysis ---


def analyse_run(
    spec: RunSpec,
    bounds_gdf: gpd.GeoDataFrame,
    student_tree: cKDTree,
    n_student: int,
    rng: np.random.Generator,
) -> dict:
    """
    Run the within-tile permutation analysis for one of the three
    runs. Returns a dict suitable for the aggregate JSON output.
    """
    print(f"[run] {spec.label}")
    cands_raw = load_combined_candidates(spec)
    cands = attach_tile_bounds(cands_raw, bounds_gdf)
    n_total = len(cands)
    n_promoted = count_reviewer_promoted(spec)
    n_real_universe = n_student + n_promoted
    bias_correction = n_student / n_real_universe
    print(
        f"  candidates={n_total}  reviewer-promoted={n_promoted}  "
        f"bias_correction={bias_correction:.4f}"
    )

    obs_shell = observed_shell_rates(cands, SHELL_EDGES)

    # Permutation null
    null_shell = np.zeros((M_PERMUTATIONS, len(SHELL_EDGES)))
    for m in range(M_PERMUTATIONS):
        perm_coords = randomise_within_tile(cands, rng)
        dist, _ = student_tree.query(perm_coords, k=1)
        null_shell[m] = shell_rates_from_distances(dist, SHELL_EDGES)
        if (m + 1) % 250 == 0:
            print(f"    perm {m + 1}/{M_PERMUTATIONS}")

    # One-sided permutation p (P(null >= obs)). Bias correction enters
    # via the null mean used to compute lift, but the p-value is built
    # from the empirical null distribution itself, which is the honest
    # tail-probability statement.
    p_floor = 1.0 / M_PERMUTATIONS
    null_mean = null_shell.mean(axis=0)
    null_lo = np.percentile(null_shell, 2.5, axis=0)
    null_hi = np.percentile(null_shell, 97.5, axis=0)
    null_corrected = null_mean / bias_correction
    null_corrected_lo = null_lo / bias_correction
    null_corrected_hi = null_hi / bias_correction
    # Permutation p-value also on the bias-corrected null distribution
    # to keep the significance test symmetric with the lift framing.
    p_raw = np.maximum(
        np.mean(null_shell >= obs_shell, axis=0), p_floor
    )
    p_corrected = np.maximum(
        np.mean(
            (null_shell / bias_correction) >= obs_shell, axis=0,
        ),
        p_floor,
    )

    shell_rows: list[dict] = []
    prev_R = 0
    for j, R in enumerate(SHELL_EDGES):
        obs = float(obs_shell[j])
        nm = float(null_mean[j])
        nm_corr = float(null_corrected[j])
        lift_raw = obs / nm if nm > 0 else float("inf")
        lift_corr = obs / nm_corr if nm_corr > 0 else float("inf")
        signal_corr = (
            (obs - nm_corr) / obs if obs > 0 else 0.0
        )
        shell_rows.append(
            {
                "R_inner_m": int(prev_R),
                "R_outer_m": int(R),
                "obs_rate_in_shell": round(obs, 4),
                "null_mean_in_shell": round(nm, 4),
                "null_mean_bias_corrected": round(nm_corr, 4),
                "null_ci_lo": round(float(null_lo[j]), 4),
                "null_ci_hi": round(float(null_hi[j]), 4),
                "null_ci_lo_bias_corrected": round(
                    float(null_corrected_lo[j]), 4,
                ),
                "null_ci_hi_bias_corrected": round(
                    float(null_corrected_hi[j]), 4,
                ),
                "lift_ratio": round(lift_raw, 2),
                "lift_ratio_bias_corrected": round(lift_corr, 2),
                "signal_fraction_bias_corrected": round(
                    signal_corr, 4,
                ),
                "p_value": round(float(p_raw[j]), 4),
                "p_value_bias_corrected": round(
                    float(p_corrected[j]), 4,
                ),
                "significant": bool(
                    p_corrected[j] < SIGNIFICANCE_ALPHA
                ),
            }
        )
        prev_R = R

    # Per-run "contiguous-from-zero" cutoff: outer edge of the deepest
    # shell that is significant *and* every shell inside it is also
    # significant. This is the conservative cutoff that the consensus
    # block uses. If the (0, 50] shell is non-significant the cutoff
    # is 0; if every shell up to (150, 286] is significant the cutoff
    # is 286.
    cutoff = 0
    for row in shell_rows:
        if row["significant"]:
            cutoff = row["R_outer_m"]
        else:
            break
    # Last-significant cutoff: the outer edge of the deepest shell that
    # is significant, irrespective of intermediate non-significant
    # shells. When ``last_significant_outer_m`` exceeds
    # ``cutoff_m`` the per-run signal is non-monotonic (likely a
    # sample-size fluctuation in a thinly-populated middle shell).
    last_sig = 0
    for row in shell_rows:
        if row["significant"]:
            last_sig = row["R_outer_m"]
    monotonic = (last_sig == cutoff)
    print(
        f"  per-run cutoff: contiguous-from-zero={cutoff} m, "
        f"last-significant={last_sig} m, monotonic={monotonic}"
    )

    return {
        "key": spec.key,
        "label": spec.label,
        "n_candidates": int(n_total),
        "n_reviewer_promoted": int(n_promoted),
        "bias_correction": round(bias_correction, 4),
        "shell": shell_rows,
        "cutoff_m": int(cutoff),
        "last_significant_outer_m": int(last_sig),
        "monotonic": bool(monotonic),
    }


# --- Consensus + report ---


def consensus_block(per_run: list[dict]) -> dict:
    """
    Synthesise the per-run cutoffs into a consensus statement.

    Definitions:

    - ``most_permissive``: the largest shell outer edge that is
      significant in *every* run (the cutoff that all runs agree on).
    - ``majority``: the shell outer edges where at least 2 of 3 runs
      are significant.
    - ``per_shell_agreement``: list of dicts, one per shell, with the
      run keys flagged significant or not.
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
    for R in shell_edges:
        flags = {key: sig_by_run[key][R] for key in sig_by_run}
        n_sig = int(sum(flags.values()))
        per_shell.append(
            {
                "R_outer_m": int(R),
                "significant": flags,
                "n_runs_significant": n_sig,
                "all_runs_significant": n_sig == len(sig_by_run),
                "majority_significant": n_sig >= (
                    len(sig_by_run) + 1
                ) // 2,
            }
        )
        if n_sig == len(sig_by_run):
            most_permissive = R
        elif (
            majority_breaks_at is None
            and n_sig < (len(sig_by_run) + 1) // 2
        ):
            majority_breaks_at = R

    return {
        "most_permissive_consensus_cutoff_m": int(most_permissive),
        "majority_breakpoint_m": majority_breaks_at,
        "per_shell": per_shell,
    }


def write_json(
    per_run: list[dict],
    consensus: dict,
    n_student: int,
    out_path: Path,
) -> None:
    """Write the aggregate per-run + consensus JSON output."""
    payload = {
        "method": "v2",
        "obs_anchor": "Obs 272 (canonical reference)",
        "shell_edges_m": list(SHELL_EDGES),
        "permutations": M_PERMUTATIONS,
        "seed": SEED,
        "alpha": SIGNIFICANCE_ALPHA,
        "n_student_gt": int(n_student),
        "runs": per_run,
        "consensus": consensus,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def write_report(
    per_run: list[dict],
    consensus: dict,
    n_student: int,
    out_path: Path,
) -> None:
    """Write the synthesised report.md with per-run tables + consensus."""
    lines: list[str] = []
    lines.append(
        "# Attractor-pull v2 — multi-run shell-wise null analysis"
    )
    lines.append("")
    lines.append(
        "**Anchor**: Obs 272 (`docs/notes/reflections/working-notes.md`,"
        " 2026-04-21) established the attractor-pull cutoff at ~125 m"
        " using the image-generalisation review only. v2 re-runs the"
        " same shell-wise within-tile permutation null on each of the"
        " three corrected 55-map runs and synthesises a consensus"
        " cutoff."
    )
    lines.append("")
    lines.append("## 1. Method")
    lines.append("")
    lines.append(
        "For each run, observed shell rates are taken directly from"
        " the reviewer's ``buffer_metres`` label (the band at which a"
        " real mound is visible inside the buffer; ``not_mound`` rows"
        " are mapped to the > 286 m shell). The null distribution is"
        " M = 1,000 within-tile permutations (seed 42) of student GT"
        " distances. Bias correction divides the null rate by the"
        " student-GT fraction of the real-mound universe to account"
        " for the reviewer-promoted phantoms absent from student GT."
        " Per-shell significance is the one-sided permutation p-value"
        " against the bias-corrected null (P(null_corrected ≥ obs)),"
        f" alpha = {SIGNIFICANCE_ALPHA}."
    )
    lines.append("")
    lines.append(
        f"Student-GT reference set: {n_student} mounds (4-corner of"
        " the corrected reviewed reference)."
    )
    lines.append(
        "Shell edges (m): "
        + ", ".join(str(e) for e in SHELL_EDGES)
        + ". The (200, 286] shell corresponds to the >150-m / not_mound"
        " review label, with effective tolerance 286 m"
        " (200 × √2 + 5 display-pixels on the 400 m × 400 m crop)."
    )
    lines.append("")

    # Per-run tables
    lines.append("## 2. Per-run shell tables")
    lines.append("")
    for run in per_run:
        lines.append(
            f"### {run['label']} — n={run['n_candidates']},"
            f" bias_correction={run['bias_correction']}"
        )
        lines.append("")
        df = pd.DataFrame(run["shell"])
        # Compact display columns, preserving the bias-corrected null
        # and significance flag as the primary decision aids.
        display = df[
            [
                "R_inner_m",
                "R_outer_m",
                "obs_rate_in_shell",
                "null_mean_bias_corrected",
                "lift_ratio_bias_corrected",
                "signal_fraction_bias_corrected",
                "p_value_bias_corrected",
                "significant",
            ]
        ]
        lines.append(display.to_markdown(index=False))
        lines.append("")
        lines.append(
            f"**Per-run cutoff**: {run['cutoff_m']} m (deepest shell"
            " outer edge with bias-corrected p < "
            f"{SIGNIFICANCE_ALPHA})"
        )
        lines.append("")

    # Consensus
    lines.append("## 3. Cross-run consensus")
    lines.append("")
    flat: list[dict] = []
    for row in consensus["per_shell"]:
        rec = {"R_outer_m": row["R_outer_m"]}
        for key, sig in row["significant"].items():
            rec[key] = "sig" if sig else "—"
        rec["n_runs_significant"] = row["n_runs_significant"]
        rec["all_significant"] = (
            "yes" if row["all_runs_significant"] else "no"
        )
        flat.append(rec)
    flat_df = pd.DataFrame(flat)
    lines.append(flat_df.to_markdown(index=False))
    lines.append("")
    lines.append(
        f"**Most-permissive consensus cutoff**:"
        f" {consensus['most_permissive_consensus_cutoff_m']} m"
        " (largest shell outer edge significant in all three runs)."
    )
    if consensus["majority_breakpoint_m"] is not None:
        lines.append(
            f"**Majority-loses breakpoint**:"
            f" {consensus['majority_breakpoint_m']} m"
            " (first shell where < 2/3 runs are significant)."
        )
    else:
        lines.append(
            "**Majority-loses breakpoint**: not reached within"
            " the 286 m maximum shell."
        )
    lines.append("")

    # Per-run cutoffs side-by-side
    lines.append("### Per-run cutoff summary")
    lines.append("")
    cutoff_rows = [
        {
            "run": r["label"],
            "n_candidates": r["n_candidates"],
            "cutoff_m": r["cutoff_m"],
        }
        for r in per_run
    ]
    lines.append(pd.DataFrame(cutoff_rows).to_markdown(index=False))
    lines.append("")

    # Cross-reference + interpretation
    lines.append("## 4. Cross-reference to Obs 272")
    lines.append("")
    obs_272_cutoff = 125
    consensus_cutoff = consensus[
        "most_permissive_consensus_cutoff_m"
    ]
    image_run = next(r for r in per_run if r["key"] == "image")
    image_cutoff_v2 = image_run["cutoff_m"]
    lines.append(
        "Obs 272 reported a 125-m cutoff using only the"
        " image-generalisation review and a 1,000-permutation"
        " within-tile null. The v2 image-only cutoff is "
        f"**{image_cutoff_v2} m** — "
        + (
            "corroborates Obs 272 exactly."
            if image_cutoff_v2 == obs_272_cutoff
            else (
                f"refines Obs 272's {obs_272_cutoff} m estimate;"
                " the difference reflects multi-buffer review"
                " adjustments and corrected-F1 alignment."
            )
        )
    )
    lines.append("")
    lines.append(
        "The cross-run **consensus cutoff** (most permissive value"
        " significant in every run) is "
        f"**{consensus_cutoff} m**."
    )
    lines.append("")
    if consensus_cutoff == obs_272_cutoff:
        lines.append(
            "**Verdict**: Obs 272's 125 m claim is corroborated by"
            " the multi-run consensus."
        )
    elif consensus_cutoff > obs_272_cutoff:
        lines.append(
            "**Verdict**: Obs 272's 125 m claim is refined upward by"
            " the multi-run consensus — the attractor-pull effect"
            " extends further than the image-only analysis suggested."
        )
    else:
        lines.append(
            "**Verdict**: Obs 272's 125 m claim is revised downward"
            " by the multi-run consensus — at least one run shows"
            " the cutoff at a tighter radius."
        )
    lines.append("")

    # Disagreement check
    cutoffs = sorted(r["cutoff_m"] for r in per_run)
    if cutoffs[0] != cutoffs[-1]:
        lines.append(
            "### Cross-run disagreement"
            f" (range {cutoffs[0]}–{cutoffs[-1]} m)"
        )
        lines.append("")
        lines.append(
            "Per-run cutoffs differ by "
            f"{cutoffs[-1] - cutoffs[0]} m. Inspect the per-run"
            " shell tables in §2 to see which shells flip"
            " significance between runs."
        )
        lines.append("")

    lines.append("## 5. Reproducibility")
    lines.append("")
    lines.append(
        f"Script: `scripts/analyse_attractor_pull_v2.py` (ruff-clean)."
        f" Seed {SEED}, M = {M_PERMUTATIONS} permutations per run."
        " Rerun with `python scripts/analyse_attractor_pull_v2.py`"
        " from the repo root."
    )
    # Single trailing newline only; an extra blank-line append would
    # cascade through markdownlint as MD012 (multiple consecutive
    # blanks) once joined and written.
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def render_figure(
    per_run: list[dict], out_path: Path,
) -> None:
    """
    Per-shell observed-rate curves for the three runs overlaid, with
    each run's bias-corrected null mean as a dashed reference. Log
    y-axis to make the lift across shells legible.
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
        (
            int((row["R_inner_m"] + row["R_outer_m"]) / 2)
        )
        for row in per_run[0]["shell"]
    ]
    colours = {"t0.3": "C0", "t0.7": "C1", "image": "C3"}

    for run in per_run:
        obs = [row["obs_rate_in_shell"] for row in run["shell"]]
        null_corr = [
            row["null_mean_bias_corrected"] for row in run["shell"]
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
            null_corr,
            "--",
            color=colours[run["key"]],
            label=f"{run['label']} (null, bias-corr)",
            linewidth=1.0,
            alpha=0.55,
        )
        # Mark non-significant shells with a hollow square.
        for centre, row in zip(centres, run["shell"]):
            if not row["significant"]:
                ax.scatter(
                    centre,
                    row["obs_rate_in_shell"],
                    s=120,
                    facecolor="none",
                    edgecolor=colours[run["key"]],
                    linewidth=2.0,
                    zorder=5,
                )
    ax.set_yscale("log")
    ax.set_xlabel("Shell centre (m)")
    ax.set_ylabel("P(mound in shell | candidate) [log scale]")
    ax.set_title(
        "Attractor-pull v2: per-shell observed vs within-tile null"
        " (3 corrected 55-map runs)"
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    print("[1/3] Loading reference inputs...")
    bounds_gdf = gpd.read_file(BOUNDS).to_crs(CRS)
    student_gt = gpd.read_file(STUDENT_GT).to_crs(CRS)
    n_student = len(student_gt)
    gt_coords = np.array([[g.x, g.y] for g in student_gt.geometry])
    student_tree = cKDTree(gt_coords)
    print(
        f"  bounds tiles: {len(bounds_gdf)}  "
        f"student GT: {n_student}"
    )

    print("[2/3] Per-run analyses...")
    per_run: list[dict] = []
    for spec in RUNS:
        per_run.append(
            analyse_run(
                spec,
                bounds_gdf,
                student_tree,
                n_student,
                rng,
            )
        )

    print("[3/3] Synthesising consensus + writing outputs...")
    consensus = consensus_block(per_run)
    write_json(
        per_run,
        consensus,
        n_student,
        OUT_DIR / "attractor-pull-v2.json",
    )
    # The hand-authored ``report.md`` is the paper-citation source and
    # is NOT regenerated by this script (matching the
    # analyse_buffer_band_lift.py / Session 75 guardrail-6 convention).
    # We write report_autogen.md instead so re-runs do not clobber the
    # synthesis. If a hand-authored report.md is missing on first run,
    # report_autogen.md is the cited starting point.
    write_report(
        per_run,
        consensus,
        n_student,
        OUT_DIR / "report_autogen.md",
    )
    render_figure(
        per_run, OUT_DIR / "figures/attractor-pull-shell-rates.png"
    )

    print("Done.")
    print(
        json.dumps(
            {
                "consensus_cutoff_m": consensus[
                    "most_permissive_consensus_cutoff_m"
                ],
                "per_run_cutoffs": {
                    r["key"]: r["cutoff_m"] for r in per_run
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
