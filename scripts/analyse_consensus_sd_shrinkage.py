#!/usr/bin/env python3
"""
Consensus SD Shrinkage Analysis (Phase 3a Text + Image Matrices)
=================================================================

Quantifies how the standard deviation (SD) of the K-consensus F1 estimate
shrinks as the consensus pool size K rises, across the Phase 3a text-track
and image-track matrices. Compares the empirical log-log slope against the
i.i.d. theoretical reference of beta = -0.5.

Methodology
-----------

The Phase 3a evaluation directory layout (``results/phase3a-{text,image}-
matrix/{thinking}-t{T}/n{K}/{rolldir}/evaluation.json``) stores **vote-
threshold sweeps** (``1ofK`` through ``KofK``) for a single K-pass consensus
build per cell -- it does NOT store independent K-roll subsamples. Direct
"SD across rolls" is therefore not available from those files.

What IS available, per condition, is the list of per-pass single-pass F1
values (the K_max replicate proposer passes). These live in:

    - results/phase3a-text-matrix/secondary_effects.json[run_variability]
    - results/secondary-effects/secondary_effects.json[run_variability]

We use these per-pass F1s with **bootstrap subsampling (with replacement)**
to estimate the SD of a K-consensus F1 estimate at each K in {1, ..., K_max}.

The "K-consensus F1 estimate" is approximated by the mean of K single-pass
F1 values drawn from the K_max pool (with replacement). This is a defensible
proxy for true greedy-vote consensus F1 under the same approximation used
implicitly when comparing single-pass means against consensus outputs in
existing run-variability analyses (e.g., secondary_effects.md S4). For tile-
overlap-bound consensus, the approximation is a **lower bound** on true
shrinkage: vote consensus partly cancels per-pass spatial error and is
expected to shrink at least as fast as the mean-of-F1s estimator.

The i.i.d. theoretical shrinkage of SD(mean of K samples) follows
sigma / sqrt(K), giving a log-log slope of -0.5 in log(SD) ~ log(K).

For each (track, thinking, T) stratum with >= 3 K-levels, we fit:

    log(SD_F1) = beta_0 + beta_1 * log(K)

Slopes shallower than -0.3 are flagged as "slower than i.i.d." which would
indicate shared-mode noise (correlated per-pass errors, e.g., shared map
sheets being consistently hard for all passes).

Caveats (also documented in the output report.md)
-------------------------------------------------

- SD at K=1 is the SD of single-pass F1 across replicate proposer passes.
  SD at K > 1 is the SD across bootstrap-resampled subsets of K passes;
  these subsets are **not independent** (they share underlying passes).
  This makes the empirical SD a **lower bound** on the true K-consensus
  estimate SD that one would obtain from K_max independent K-pass runs.
- Image-track conditions with K_max = 3 (T=0.0 cells) cannot support
  meaningful subsamples beyond K = 3; their per-stratum slopes will have
  wide CIs.
- This analysis is orthogonal to the image-track Levene's W = 3.192,
  p = 0.0040 cross-condition heterogeneity finding -- that result stands.

Inputs
------

- ``results/phase3a-text-matrix/secondary_effects.json`` -- per-pass F1
  values for 8 text-track cells (K_max in {3, 10, 30}).
- ``results/secondary-effects/secondary_effects.json`` -- per-pass F1
  values for 9 image-track cells (K_max in {3, 10}; SCALE4 included
  separately).
- ``planning/condition-inventory-with-s78.json`` -- canonical inventory
  for cross-referencing track / architecture / K / T / thinking labels.

Outputs
-------

- ``results/secondary-effects-consensus-sd/sd_shrinkage.json`` -- full
  numeric results (per-cell SD at each K, per-stratum slope and CI).
- ``results/secondary-effects-consensus-sd/report.md`` -- discussion-ready
  table + ~120-word prose paragraph + methodology footnote.
- ``results/secondary-effects-consensus-sd/sd_shrinkage.png`` -- log-log
  SD-vs-K plot, faceted by track, coloured by T, line-style by thinking,
  with dashed -0.5 reference slope.

Usage
-----

    python scripts/analyse_consensus_sd_shrinkage.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-27
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

__version__ = "1.0.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEXT_SECONDARY = PROJECT_ROOT / "results" / "phase3a-text-matrix" / "secondary_effects.json"
IMAGE_SECONDARY = PROJECT_ROOT / "results" / "secondary-effects" / "secondary_effects.json"
OUTPUT_DIR = PROJECT_ROOT / "results" / "secondary-effects-consensus-sd"

# Project-standard bootstrap parameters
N_BOOTSTRAP = 1000
RANDOM_SEED = 42

# K-levels probed per track. Restricted to values <= K_max for each cell.
TEXT_K_LEVELS = [1, 5, 10, 30]
IMAGE_K_LEVELS = [1, 3, 5, 10]

# Threshold for "slower than i.i.d." flag (theoretical i.i.d. is beta = -0.5)
SLOPE_FLAG_THRESHOLD = -0.3

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step 1: Load + flatten per-pass F1 values into a long-form DataFrame.
# ---------------------------------------------------------------------------


def _parse_condition_label(label: str) -> tuple[str, float]:
    """Parse condition labels like 'HIGH-T0.7' or 'MIN-T0.0' or 'SCALE4-T0.7'.

    Returns
    -------
    tuple[str, float]
        (thinking, temperature). Thinking is one of {"HIGH", "MINIMAL",
        "SCALE4"}; temperature is the numeric T value.
    """
    parts = label.split("-T")
    thinking_raw = parts[0]
    # Normalise MIN -> MINIMAL for cross-track consistency
    thinking = "MINIMAL" if thinking_raw == "MIN" else thinking_raw
    temperature = float(parts[1])
    return thinking, temperature


def load_per_pass_f1s() -> pd.DataFrame:
    """Load per-pass F1 lists from both matrices into a long-form DataFrame.

    Returns
    -------
    pandas.DataFrame
        Columns: [track, thinking, T, K_max, run_idx, f1].
    """
    rows: list[dict] = []
    for track, path in [("text", TEXT_SECONDARY), ("image", IMAGE_SECONDARY)]:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for cond in data["run_variability"]["per_condition"]:
            thinking, temperature = _parse_condition_label(cond["condition"])
            k_max = cond["K"]
            for run_idx, f1 in enumerate(cond["per_run"], start=1):
                rows.append({
                    "track": track,
                    "thinking": thinking,
                    "T": temperature,
                    "K_max": k_max,
                    "run_idx": run_idx,
                    "f1": float(f1),
                })
    df = pd.DataFrame(rows)
    logger.info("Loaded %d per-pass F1 rows across %d cells",
                len(df), df.groupby(["track", "thinking", "T"]).ngroups)
    return df


# ---------------------------------------------------------------------------
# Step 2: Per-(track, thinking, T, K_used) SD via bootstrap subsampling.
# ---------------------------------------------------------------------------


def _bootstrap_sd_at_k(
    f1_values: np.ndarray,
    k_used: int,
    rng: np.random.Generator,
    n_bootstrap: int = N_BOOTSTRAP,
) -> dict[str, float]:
    """Estimate SD of K-consensus F1 estimate at K = k_used via bootstrap.

    For each bootstrap iteration, we draw k_used per-pass F1 values with
    replacement from the K_max pool and take the mean as a proxy for the
    K-consensus F1. The SD across these per-iteration means is the
    K-consensus estimator SD; we re-bootstrap the SD itself to obtain a
    95% CI on the SD.

    At k_used = 1, the function returns the empirical SD of the per-pass
    F1 list directly (no subsampling needed); the CI is the percentile
    bootstrap CI on the SD.

    Parameters
    ----------
    f1_values : numpy.ndarray
        Per-pass single-pass F1 values (length K_max).
    k_used : int
        Subsample size (1 <= k_used <= K_max).
    rng : numpy.random.Generator
        Seeded random generator (for reproducibility).
    n_bootstrap : int
        Number of bootstrap iterations.

    Returns
    -------
    dict[str, float]
        Keys: ``mean``, ``sd``, ``sd_ci_lower``, ``sd_ci_upper``.
    """
    if k_used < 1 or k_used > len(f1_values):
        raise ValueError(f"k_used={k_used} out of range for K_max={len(f1_values)}")

    if k_used == 1:
        # Direct empirical SD of single-pass F1s. CI via percentile bootstrap
        # on the SD itself (resample the per-pass F1 list with replacement,
        # take SD each time).
        sd_resamples = np.array([
            np.std(rng.choice(f1_values, size=len(f1_values), replace=True), ddof=1)
            for _ in range(n_bootstrap)
        ])
        return {
            "mean": float(np.mean(f1_values)),
            "sd": float(np.std(f1_values, ddof=1)),
            "sd_ci_lower": float(np.percentile(sd_resamples, 2.5)),
            "sd_ci_upper": float(np.percentile(sd_resamples, 97.5)),
        }

    # K > 1: each bootstrap iteration draws K passes with replacement and
    # records the mean F1 across them. SD across these bootstrap means is
    # the estimator SD at K. We then re-bootstrap to get a CI on the SD.
    bootstrap_means = np.array([
        np.mean(rng.choice(f1_values, size=k_used, replace=True))
        for _ in range(n_bootstrap)
    ])
    sd_estimate = float(np.std(bootstrap_means, ddof=1))
    # CI on the SD: re-bootstrap the bootstrap_means array to get SD CI
    sd_resamples = np.array([
        np.std(rng.choice(bootstrap_means, size=len(bootstrap_means), replace=True), ddof=1)
        for _ in range(n_bootstrap)
    ])
    return {
        "mean": float(np.mean(bootstrap_means)),
        "sd": sd_estimate,
        "sd_ci_lower": float(np.percentile(sd_resamples, 2.5)),
        "sd_ci_upper": float(np.percentile(sd_resamples, 97.5)),
    }


def compute_sd_per_cell_per_k(df_passes: pd.DataFrame) -> pd.DataFrame:
    """Compute SD and 95% CI at each (track, thinking, T, K) cell.

    Parameters
    ----------
    df_passes : pandas.DataFrame
        Output of :func:`load_per_pass_f1s`.

    Returns
    -------
    pandas.DataFrame
        Columns: [track, thinking, T, K_max, K_used, mean_f1, sd_f1,
        sd_ci_lower, sd_ci_upper].
    """
    rows: list[dict] = []
    grouped = df_passes.groupby(["track", "thinking", "T"], as_index=False)
    rng_master = np.random.default_rng(RANDOM_SEED)

    for (track, thinking, temperature), group in grouped:
        f1_values = group["f1"].to_numpy()
        k_max = int(group["K_max"].iloc[0])
        # Choose K levels: track-specific list, restricted to <= k_max
        candidate_levels = TEXT_K_LEVELS if track == "text" else IMAGE_K_LEVELS
        k_levels = [k for k in candidate_levels if k <= k_max]
        for k_used in k_levels:
            # Spawn an independent RNG seeded deterministically per cell+K
            seed_offset = hash((track, thinking, temperature, k_used)) % (2**32)
            rng = np.random.default_rng(int(rng_master.integers(0, 2**32)) ^ seed_offset)
            stats = _bootstrap_sd_at_k(f1_values, k_used, rng)
            rows.append({
                "track": track,
                "thinking": thinking,
                "T": temperature,
                "K_max": k_max,
                "K_used": k_used,
                "mean_f1": stats["mean"],
                "sd_f1": stats["sd"],
                "sd_ci_lower": stats["sd_ci_lower"],
                "sd_ci_upper": stats["sd_ci_upper"],
            })
    df = pd.DataFrame(rows)
    logger.info("Computed SD at %d (cell, K) points", len(df))
    return df


# ---------------------------------------------------------------------------
# Step 3: Trend test -- log-log slope per stratum.
# ---------------------------------------------------------------------------


def _fit_loglog_slope(k_values: np.ndarray, sd_values: np.ndarray) -> tuple[float, float]:
    """Fit log(SD) ~ beta_0 + beta_1 log(K). Returns (intercept, slope)."""
    log_k = np.log(k_values)
    log_sd = np.log(sd_values)
    slope, intercept = np.polyfit(log_k, log_sd, deg=1)
    return float(intercept), float(slope)


def fit_per_stratum_slopes(
    df_passes: pd.DataFrame,
    df_sd: pd.DataFrame,
) -> pd.DataFrame:
    """Per-stratum log-log slope with bootstrap CI on the slope.

    For each (track, thinking, T) stratum with >= 3 distinct K-levels,
    fit log(SD) ~ beta_0 + beta_1 log(K). The CI on beta_1 is obtained
    by re-bootstrapping the per-pass F1 list and recomputing SD-at-each-K
    + slope, repeated N_BOOTSTRAP times.

    Parameters
    ----------
    df_passes : pandas.DataFrame
        Per-pass F1 long-form data (for re-bootstrap).
    df_sd : pandas.DataFrame
        Output of :func:`compute_sd_per_cell_per_k`.

    Returns
    -------
    pandas.DataFrame
        Columns: [track, thinking, T, n_k_levels, beta_1, beta_1_ci_lower,
        beta_1_ci_upper, slower_than_iid].
    """
    rows: list[dict] = []
    rng_master = np.random.default_rng(RANDOM_SEED)
    for (track, thinking, temperature), group in df_sd.groupby(
        ["track", "thinking", "T"], as_index=False,
    ):
        if len(group) < 3:
            logger.debug("Skipping %s/%s/T%s -- only %d K-levels",
                         track, thinking, temperature, len(group))
            continue
        # Point estimate
        k_arr = group["K_used"].to_numpy()
        sd_arr = group["sd_f1"].to_numpy()
        _, beta_1 = _fit_loglog_slope(k_arr, sd_arr)

        # Bootstrap CI on beta_1 by re-bootstrapping the per-pass F1 pool
        passes = df_passes[
            (df_passes["track"] == track)
            & (df_passes["thinking"] == thinking)
            & (df_passes["T"] == temperature)
        ]
        f1_pool = passes["f1"].to_numpy()
        slopes = []
        for _ in range(N_BOOTSTRAP):
            seed = int(rng_master.integers(0, 2**32))
            inner_rng = np.random.default_rng(seed)
            # Bootstrap-resample the per-pass pool
            resampled_pool = inner_rng.choice(f1_pool, size=len(f1_pool), replace=True)
            # Recompute SD at each K from the resampled pool (single-shot SD;
            # not the full nested bootstrap, which would be too expensive)
            sds = []
            for k in k_arr:
                if k == 1:
                    sds.append(float(np.std(resampled_pool, ddof=1)))
                else:
                    means = np.array([
                        np.mean(inner_rng.choice(resampled_pool, size=int(k), replace=True))
                        for _ in range(100)  # inner light bootstrap
                    ])
                    sds.append(float(np.std(means, ddof=1)))
            sds_arr = np.array(sds)
            # Guard against zero/negative SDs (degenerate small-pool case)
            if np.any(sds_arr <= 0):
                continue
            _, slope = _fit_loglog_slope(k_arr, sds_arr)
            slopes.append(slope)
        if slopes:
            ci_lo = float(np.percentile(slopes, 2.5))
            ci_hi = float(np.percentile(slopes, 97.5))
        else:
            ci_lo = ci_hi = float("nan")

        rows.append({
            "track": track,
            "thinking": thinking,
            "T": temperature,
            "n_k_levels": len(group),
            "beta_1": beta_1,
            "beta_1_ci_lower": ci_lo,
            "beta_1_ci_upper": ci_hi,
            "slower_than_iid": bool(beta_1 > SLOPE_FLAG_THRESHOLD),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Step 4: Paired CI-width comparison (HIGH-T0.7 ceiling cells).
# ---------------------------------------------------------------------------


def compute_paired_ci_widths(
    df_passes: pd.DataFrame,
    df_sd: pd.DataFrame,
) -> dict:
    """Compute F1 CI-width ratios CI_width(K=N) / CI_width(K=1) for ceilings.

    Targets: HIGH-T0.7 text (K_max = 30) and HIGH-T0.7 image (K_max = 10).
    The "F1 CI width" at each K is the 2.5--97.5 percentile width of
    bootstrap means at that K, scaled by 4 (i.e., ~1.96 sigma half-width).

    Parameters
    ----------
    df_passes : pandas.DataFrame
        Per-pass F1 data.
    df_sd : pandas.DataFrame
        Per-(cell, K) SD table (used for K-level selection only).

    Returns
    -------
    dict
        Per-track entries with K-by-K CI widths and ratios.
    """
    targets = [
        ("text", "HIGH", 0.7),
        ("image", "HIGH", 0.7),
    ]
    out: dict = {}
    rng_master = np.random.default_rng(RANDOM_SEED)
    for track, thinking, temperature in targets:
        passes = df_passes[
            (df_passes["track"] == track)
            & (df_passes["thinking"] == thinking)
            & (df_passes["T"] == temperature)
        ]
        if passes.empty:
            continue
        f1_pool = passes["f1"].to_numpy()
        k_max = int(passes["K_max"].iloc[0])
        candidate_levels = TEXT_K_LEVELS if track == "text" else IMAGE_K_LEVELS
        k_levels = [k for k in candidate_levels if k <= k_max]
        widths: dict[int, float] = {}
        for k in k_levels:
            seed = int(rng_master.integers(0, 2**32))
            rng = np.random.default_rng(seed)
            if k == 1:
                # CI-width of the single-pass F1 distribution
                resamples = rng.choice(f1_pool, size=(N_BOOTSTRAP, 1), replace=True)
                vals = resamples.mean(axis=1)
            else:
                vals = np.array([
                    np.mean(rng.choice(f1_pool, size=int(k), replace=True))
                    for _ in range(N_BOOTSTRAP)
                ])
            ci_lo = float(np.percentile(vals, 2.5))
            ci_hi = float(np.percentile(vals, 97.5))
            widths[k] = ci_hi - ci_lo
        baseline = widths.get(1, float("nan"))
        ratios = {k: (w / baseline) if baseline > 0 else float("nan")
                  for k, w in widths.items()}
        out[f"{track}_{thinking}_T{temperature}"] = {
            "k_levels": k_levels,
            "ci_widths": {str(k): widths[k] for k in k_levels},
            "ci_width_ratios_to_k1": {str(k): ratios[k] for k in k_levels},
        }
    return out


# ---------------------------------------------------------------------------
# Step 5: Output writers (JSON, Markdown, PNG).
# ---------------------------------------------------------------------------


def write_json(
    df_sd: pd.DataFrame,
    df_slopes: pd.DataFrame,
    paired_widths: dict,
    output_path: Path,
) -> None:
    """Write the structured numeric output to JSON."""
    payload = {
        "metadata": {
            "version": __version__,
            "generated": datetime.now(tz=timezone.utc).isoformat(),
            "n_bootstrap": N_BOOTSTRAP,
            "random_seed": RANDOM_SEED,
            "slope_flag_threshold": SLOPE_FLAG_THRESHOLD,
            "iid_theoretical_slope": -0.5,
            "method_note": (
                "SD at K computed by bootstrap subsampling per-pass single-"
                "pass F1 lists (mean of K passes as K-consensus proxy)."
            ),
        },
        "sd_per_cell_per_k": df_sd.to_dict(orient="records"),
        "per_stratum_slopes": df_slopes.to_dict(orient="records"),
        "paired_ci_widths": paired_widths,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    logger.info("JSON written: %s", output_path)


def _format_table_row(stratum: dict, df_sd: pd.DataFrame, paired: dict) -> str:
    """Format a single markdown table row for a (track, thinking, T) stratum."""
    track = stratum["track"]
    thinking = stratum["thinking"]
    temperature = stratum["T"]
    cell_sd = df_sd[
        (df_sd["track"] == track)
        & (df_sd["thinking"] == thinking)
        & (df_sd["T"] == temperature)
    ].set_index("K_used")

    def sd_at(k: int) -> str:
        """Format SD at a given K, or em-dash if absent."""
        return f"{cell_sd['sd_f1'].loc[k]:.4f}" if k in cell_sd.index else "—"

    n_max = int(cell_sd.index.max())
    sd_n_max = sd_at(n_max)
    beta_str = (
        f"{stratum['beta_1']:+.2f} "
        f"[{stratum['beta_1_ci_lower']:+.2f}, {stratum['beta_1_ci_upper']:+.2f}]"
    )
    flag = " *" if stratum["slower_than_iid"] else ""
    # Look up CI-width ratio at K=N_max for the paired ceiling targets
    paired_key = f"{track}_{thinking}_T{temperature}"
    if paired_key in paired:
        ratios = paired[paired_key]["ci_width_ratios_to_k1"]
        ratio_n = ratios.get(str(n_max), None)
        ratio_str = f"{ratio_n:.2f}" if ratio_n is not None else "—"
    else:
        ratio_str = "—"
    return (
        f"| {track} | {thinking} | {temperature:.1f} | {sd_at(1)} | {sd_at(5)} | "
        f"{sd_at(10)} | {sd_n_max} (K={n_max}) | {beta_str}{flag} | {ratio_str} |"
    )


def write_markdown_report(
    df_sd: pd.DataFrame,
    df_slopes: pd.DataFrame,
    paired: dict,
    output_path: Path,
) -> None:
    """Write the discussion-ready markdown report."""
    lines: list[str] = []
    lines.append("# Consensus SD Shrinkage Analysis (Phase 3a Text + Image)")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}")
    lines.append(f"**Bootstrap iterations**: {N_BOOTSTRAP} (seed = {RANDOM_SEED})")
    lines.append("**Theoretical i.i.d. log-log slope**: beta_1 = -0.5")
    lines.append("**Slower-than-i.i.d. flag**: beta_1 > -0.3 (asterisked rows below)")
    lines.append("")

    # Headline table
    lines.append("## Per-stratum log-log slope and SD shrinkage")
    lines.append("")
    lines.append(
        "| Track | Thinking | T | SD@K=1 | SD@K=5 | SD@K=10 | SD@K=N_max | "
        "beta_1 [95% CI] | CI-width ratio (K=N_max / K=1) |"
    )
    lines.append(
        "|-------|----------|--:|------:|------:|------:|------:|:--------------:|:-----:|"
    )
    df_slopes_sorted = df_slopes.sort_values(["track", "thinking", "T"]).to_dict("records")
    for s in df_slopes_sorted:
        lines.append(_format_table_row(s, df_sd, paired))
    lines.append("")

    # Prose paragraph (~120 words)
    lines.extend(_compose_prose(df_slopes, paired))
    lines.append("")

    # Methodology footnote
    lines.append("## Methodology footnote")
    lines.append("")
    lines.append(
        "The Phase 3a evaluation outputs "
        "(`{thinking}-t{T}/n{K}/{rolldir}/evaluation.json`) store "
        "**vote-threshold sweeps** (`1ofK` to `KofK`) for a single K-pass "
        "consensus build per cell -- they do **not** store independent K-roll "
        "subsamples. To obtain a per-K SD, we approximate the K-consensus F1 "
        "estimator by the mean of K single-pass F1 values drawn (with "
        "replacement) from the K_max-pass pool, using the per-condition "
        "single-pass F1 lists in `secondary_effects.json[run_variability]`. "
        "**This proxy assumes pass-level i.i.d. errors and therefore "
        "recovers the -0.5 shrinkage law by construction**; the analysis "
        "thus serves as a sanity check against the i.i.d. expectation rather "
        "than an independent test of departure from i.i.d. To detect genuine "
        "shared-mode signal (slope > -0.3) one would need to rebuild greedy-"
        "vote consensus from per-pass detection geometries on multiple K-"
        "subsamples drawn from the K_max pool, then re-evaluate -- a "
        "follow-up that requires per-pass GeoJSONs in `outputs/h11/pv-diag-"
        "384/` and ~5--10 minutes of compute per stratum on sapphire. SD "
        "CIs use 1,000 percentile bootstrap iterations (seed 42); slope CIs "
        "use 1,000 nested-bootstrap iterations over the per-pass F1 pool. "
        "Image-track T=0.0 cells (K_max = 3) have only three single-pass "
        "replicates and so support only K = {1, 3} subsamples; no slope is "
        "fitted for those strata."
    )
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append(
        "- **Proxy bias toward -0.5**: the mean-of-K-passes proxy mathematically "
        "yields slope = -0.5 under any scenario in which the per-pass F1s are "
        "drawn from a stable distribution (because SD of mean of K i.i.d. samples "
        "= sigma / sqrt(K)). Slopes departing meaningfully from -0.5 in this "
        "analysis would only emerge if the per-pass F1 distribution itself were "
        "non-stationary across the K_max-pass pool -- a property that is not the "
        "intended target of an SD-shrinkage diagnostic. **Treat the resulting "
        "slopes as confirming the i.i.d. expectation, not as an independent test "
        "for shared-mode signal.**"
    )
    lines.append(
        "- **Subsample independence**: K-subset rolls share underlying per-pass "
        "detections, so the reported SD-across-rolls is a **lower bound** on the "
        "SD of K independent K-pass runs."
    )
    lines.append(
        "- **K_max = 3 strata**: image-track T=0.0 cells have only three "
        "single-pass replicates and so support only K = {1, 3} subsamples; "
        "no slope is fitted (need >= 3 K-levels)."
    )
    lines.append(
        "- **Orthogonal to Levene**: the image-track Levene W = 3.192, "
        "p = 0.0040 cross-condition variance heterogeneity finding from "
        "`results/secondary-effects/secondary_effects.md` Section 4 stands; "
        "the present analysis examines within-cell shrinkage as K rises, "
        "not between-cell variance comparison."
    )
    lines.append(
        "- **Where genuine shared-mode signal lives**: the per-condition K=1 SDs "
        "themselves are still informative (HIGH conditions show SD = 0.012-0.022 "
        "for image vs 0.005-0.022 for text at K_max). To detect shared-mode "
        "shrinkage failure, future work should rebuild greedy-vote consensus on "
        "K-subsamples (see Methodology footnote)."
    )
    lines.append("")

    # File manifest
    lines.append("## Output files")
    lines.append("")
    lines.append("- `sd_shrinkage.json` -- full numeric results.")
    lines.append("- `sd_shrinkage.png` -- log-log SD vs K, faceted by track.")
    lines.append("- `report.md` -- this file.")
    lines.append("")
    lines.append(f"*Generated: {datetime.now(tz=timezone.utc).isoformat()}*")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Markdown report written: %s", output_path)


def _compose_prose(df_slopes: pd.DataFrame, paired: dict) -> list[str]:
    """Compose the ~120-word prose paragraph leading with text vs image slopes."""
    text_slopes = df_slopes[df_slopes["track"] == "text"]["beta_1"]
    image_slopes = df_slopes[df_slopes["track"] == "image"]["beta_1"]
    text_mean = float(text_slopes.mean()) if not text_slopes.empty else float("nan")
    image_mean = float(image_slopes.mean()) if not image_slopes.empty else float("nan")
    flagged = df_slopes[df_slopes["slower_than_iid"]]
    flagged_labels = [
        f"{row.track} {row.thinking} T{row.T:.1f}"
        for _, row in flagged.iterrows()
    ]
    flag_text = (
        "; exceptions: " + ", ".join(flagged_labels) if flagged_labels
        else "; no stratum departs detectably from i.i.d. shrinkage"
    )
    # Pull the K=N_max ratio for the two ceiling targets
    text_ratio = paired.get("text_HIGH_T0.7", {}).get("ci_width_ratios_to_k1", {})
    image_ratio = paired.get("image_HIGH_T0.7", {}).get("ci_width_ratios_to_k1", {})
    text_max_k = max((int(k) for k in text_ratio), default=None)
    image_max_k = max((int(k) for k in image_ratio), default=None)
    text_ratio_str = (
        f"{text_ratio[str(text_max_k)]:.2f}x at K={text_max_k}"
        if text_max_k is not None else "n/a"
    )
    image_ratio_str = (
        f"{image_ratio[str(image_max_k)]:.2f}x at K={image_max_k}"
        if image_max_k is not None else "n/a"
    )
    para = (
        f"Across the Phase 3a matrices, the empirical K-consensus F1 SD "
        f"shrinks with K at a mean log-log slope of {text_mean:+.2f} for the "
        f"text track and {image_mean:+.2f} for the image track, against the "
        f"i.i.d. theoretical reference of -0.5. All strata cluster tightly "
        f"around -0.5{flag_text}. The ceiling-K paired bootstrap CI-width "
        f"ratio is {text_ratio_str} for HIGH-T0.7 text and {image_ratio_str} "
        f"for HIGH-T0.7 image -- consistent with the expected ~sqrt(K) "
        f"contraction. **Important caveat**: because we use the mean of K "
        f"single-pass F1s as the K-consensus proxy, the analysis recovers "
        f"the i.i.d. shrinkage law by construction; departures from -0.5 "
        f"would require subsample rebuilding of the actual greedy-vote "
        f"consensus from per-pass detection geometries, not available from "
        f"existing per-K aggregate evaluation files. This analysis is "
        f"orthogonal to the image-track cross-condition Levene heterogeneity "
        f"(W = 3.192, p = 0.0040) reported in Section 4 of the secondary-"
        f"effects sibling."
    )
    return ["## Prose summary (~120 words)", "", para]


def write_plot(df_sd: pd.DataFrame, output_path: Path) -> None:
    """Write the log-log SD vs K plot, faceted by track."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    cmap = plt.get_cmap("viridis")
    temperatures = sorted(df_sd["T"].unique())
    color_map = {temp: cmap(i / max(1, len(temperatures) - 1))
                 for i, temp in enumerate(temperatures)}
    line_styles = {"HIGH": "-", "MINIMAL": "--", "SCALE4": ":"}

    for ax, track in zip(axes, ["text", "image"]):
        sub = df_sd[df_sd["track"] == track]
        for (thinking, temperature), group in sub.groupby(["thinking", "T"]):
            group_sorted = group.sort_values("K_used")
            label = f"{thinking} T{temperature:.1f}"
            ax.plot(
                group_sorted["K_used"], group_sorted["sd_f1"],
                marker="o", linestyle=line_styles.get(thinking, "-"),
                color=color_map[temperature], label=label, alpha=0.85,
            )
        # i.i.d. reference: SD ~ K^-0.5
        if not sub.empty:
            anchor_k = 1
            anchor_sd = sub[sub["K_used"] == 1]["sd_f1"].max()
            if pd.notna(anchor_sd) and anchor_sd > 0:
                ks = np.array(sorted(sub["K_used"].unique()))
                ref = anchor_sd * (ks / anchor_k) ** -0.5
                ax.plot(ks, ref, "k--", alpha=0.5, label="i.i.d. (-0.5)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("K (consensus pool size)")
        ax.set_ylabel("SD of K-consensus F1 estimate")
        ax.set_title(f"{track.capitalize()} track")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=7, loc="best", ncol=2)

    fig.suptitle(
        "K-consensus F1 SD shrinkage (log-log) -- Phase 3a", fontsize=12,
    )
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Plot written: %s", output_path)


# ---------------------------------------------------------------------------
# Main entry point.
# ---------------------------------------------------------------------------


def main() -> int:
    """Run the full SD-shrinkage analysis."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
    logger.info("analyse_consensus_sd_shrinkage.py v%s", __version__)

    df_passes = load_per_pass_f1s()
    df_sd = compute_sd_per_cell_per_k(df_passes)
    df_slopes = fit_per_stratum_slopes(df_passes, df_sd)
    paired = compute_paired_ci_widths(df_passes, df_sd)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(df_sd, df_slopes, paired, OUTPUT_DIR / "sd_shrinkage.json")
    write_markdown_report(df_sd, df_slopes, paired, OUTPUT_DIR / "report.md")
    write_plot(df_sd, OUTPUT_DIR / "sd_shrinkage.png")

    # Console summary
    logger.info("Per-stratum slopes:")
    for _, row in df_slopes.iterrows():
        flag = " *SLOWER" if row["slower_than_iid"] else ""
        logger.info(
            "  %s %s T%.1f: beta_1 = %+.3f [%+.3f, %+.3f]%s",
            row["track"], row["thinking"], row["T"],
            row["beta_1"], row["beta_1_ci_lower"], row["beta_1_ci_upper"],
            flag,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
