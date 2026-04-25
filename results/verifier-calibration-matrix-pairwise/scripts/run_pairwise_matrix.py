#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# run_pairwise_matrix.py
# ---------------------------------------------------------------------------
#
# Purpose
# -------
# Run pairwise paired-permutation tests across the Session 78 verifier
# calibration matrix (7 variants × 2 tracks × 4 buffers), apply
# Benjamini-Hochberg FDR correction within each (track, buffer) family of
# C(7,2) = 21 tests, and assign variants to statistically distinguishable
# tiers via greedy clique construction.
#
# Variants (7):
#   - adversarial
#   - adversarial-text (CANONICAL)
#   - brief
#   - brief-text
#   - checklist
#   - checklist-text
#   - comparative
#
# Tracks (2): image, text
# Buffers (4): 20, 30, 40, 50 metres
# Permutations: 10,000 per test, seed 42
# FDR: Benjamini-Hochberg step-up at q = 0.05, within each (track, buffer)
#
# Data provenance
# ---------------
# Input geojsons live at
#   results/verifier-calibration-matrix/{track}-{variant}-opt-20m.geojson
# These were materialised in Session 78 at each variant's 20m-buffer
# optimum (vote_t, prob_t). For 13 of 14 variants the per-buffer optima
# (20/30/40/50 m) are identical, so evaluating the 20m-optimum geojson at
# 30/40/50 m is equivalent to evaluating at each buffer's own optimum.
# For text-adversarial at 50 m the 50m optimum differs marginally — see
# README data-quality note.
#
# Ground truth: inputs/vectors/references/mounds-reference.geojson
# Scope      : inputs/vectors/bounds/384/full_evaluation_bounds.geojson
#              (487-tile Era 2 evaluation scope)
#
# Outputs
# -------
# results/verifier-calibration-matrix-pairwise/
#   image/
#     permutation_tiers_20m.json
#     permutation_tiers_20m.md
#     permutation_tiers_30m.json
#     permutation_tiers_30m.md
#     permutation_tiers_40m.json
#     permutation_tiers_40m.md
#     permutation_tiers_50m.json
#     permutation_tiers_50m.md
#   text/
#     ...same layout...
#
# Usage
# -----
#   .venv/bin/python results/verifier-calibration-matrix-pairwise/scripts/run_pairwise_matrix.py
#
# Run on sapphire per project convention (CPU-bound, parallelised).
# Language: UK/Australian English throughout.
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import numpy as np

# Ensure scripts/ is on the path for reuse of helpers.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from apply_fdr_correction import apply_bh_correction  # noqa: E402
from lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from pairwise_permutation_test import (  # noqa: E402
    load_geojson_detections,
    run_permutation_test,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VARIANTS = [
    "adversarial",
    "adversarial-text",  # canonical
    "brief",
    "brief-text",
    "checklist",
    "checklist-text",
    "comparative",
]
CANONICAL = "adversarial-text"

TRACKS = ["image", "text"]
BUFFERS = [20, 30, 40, 50]

N_PERMUTATIONS = 10_000
PERM_SEED = 42
BOOTSTRAP_N = 10_000
BOOTSTRAP_SEED = 42
FDR_Q = 0.05

GEO_DIR = REPO_ROOT / "results/verifier-calibration-matrix"
OUT_ROOT = REPO_ROOT / "results/verifier-calibration-matrix-pairwise"

REF_PATH = REPO_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS_PATH = REPO_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
TARGET_CRS = "EPSG:32635"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_git_commit() -> str:
    """Return short git commit hash, or ``'(unknown)'`` on failure."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=str(REPO_ROOT),
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "(unknown)"


def load_ref_and_bounds() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Load reference mounds and evaluation bounds, reprojecting to EPSG:32635.

    Returns:
        (gdf_ref, gdf_bounds) — both in EPSG:32635, with exploded multipoints
        so reference is one Point per feature.
    """
    gdf_ref = gpd.read_file(REF_PATH)
    if gdf_ref.crs is None:
        gdf_ref = gdf_ref.set_crs(TARGET_CRS)
    elif gdf_ref.crs.to_epsg() != 32635:
        gdf_ref = gdf_ref.to_crs(TARGET_CRS)
    # Explode any MultiPoint geometries so one row = one Point.
    gdf_ref = gdf_ref.explode(index_parts=False).reset_index(drop=True)
    # Need a ``Map`` column for compute_per_tile_tp_fp_fn per-map matching.
    if "Map" not in gdf_ref.columns:
        # Derive from tile name on the reference if present, else from
        # nearest tile spatial join. The project convention: `Map` is the
        # sheet prefix (e.g. "K-35-052-4").
        raise RuntimeError("reference lacks 'Map' column")

    gdf_bounds = gpd.read_file(BOUNDS_PATH)
    if gdf_bounds.crs is None:
        gdf_bounds = gdf_bounds.set_crs(TARGET_CRS)
    elif gdf_bounds.crs.to_epsg() != 32635:
        gdf_bounds = gdf_bounds.to_crs(TARGET_CRS)
    return gdf_ref, gdf_bounds


def geojson_path_for(track: str, variant: str) -> Path:
    """Return the path to the materialised 20m-optimum geojson for a cell."""
    return GEO_DIR / f"{track}-{variant}-opt-20m.geojson"


def greedy_clique_tiers(
    variants_by_f1: list[tuple[str, float]],
    sig_lookup: dict[tuple[str, str], bool],
) -> list[list[str]]:
    """Greedy clique-based tier construction.

    Sort variants by F1 descending (already done in input). Start tier 1
    with the top-ranked variant; add each subsequent variant if it is
    statistically indistinguishable from EVERY current tier member. When a
    variant is significantly different from any member, close the tier and
    start a new one with that variant.

    Args:
        variants_by_f1: list of (variant_name, f1) sorted by f1 desc.
        sig_lookup: dict mapping (variant_a, variant_b) tuple (sorted) to
            boolean "significant after FDR".

    Returns:
        list of tiers, each tier a list of variant names in F1-desc order.
    """
    tiers: list[list[str]] = []
    current: list[str] = []
    for variant, _f1 in variants_by_f1:
        if not current:
            current.append(variant)
            continue
        ok = True
        for member in current:
            key = tuple(sorted([variant, member]))
            if sig_lookup.get(key, False):
                ok = False
                break
        if ok:
            current.append(variant)
        else:
            tiers.append(current)
            current = [variant]
    if current:
        tiers.append(current)
    return tiers


# ---------------------------------------------------------------------------
# F1 + CI computation per variant at a given buffer
# ---------------------------------------------------------------------------


def compute_f1_ci(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int,
    n_boot: int = BOOTSTRAP_N,
    seed: int = BOOTSTRAP_SEED,
) -> dict:
    """Compute point F1 + 95% percentile bootstrap CI via tile-level resample.

    Bootstrap resamples tiles with replacement (paired tile design), then
    aggregates micro-average F1 within each resample. This mirrors the
    existing evaluate_detections.py approach.

    Args:
        gdf_det: detections with ``source_tile``.
        gdf_ref: reference mounds.
        gdf_bounds: evaluation bounds with ``tile_name``.
        buffer_metres: matching tolerance in metres.
        n_boot: bootstrap iterations.
        seed: RNG seed.

    Returns:
        dict with keys ``f1``, ``precision``, ``recall``, ``f1_ci_lower``,
        ``f1_ci_upper``, ``tp``, ``fp``, ``fn``, ``n_detections``.
    """
    tm = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )
    tiles = gdf_bounds["tile_name"].unique()
    n_tiles = len(tiles)

    # Align tile counts.
    tp_arr = np.zeros(n_tiles, dtype=int)
    fp_arr = np.zeros(n_tiles, dtype=int)
    fn_arr = np.zeros(n_tiles, dtype=int)
    tm_idx = tm.set_index("tile_name")
    for i, t in enumerate(tiles):
        if t in tm_idx.index:
            row = tm_idx.loc[t]
            tp_arr[i] = int(row["tp"])
            fp_arr[i] = int(row["fp"])
            fn_arr[i] = int(row["fn"])

    total_tp = int(tp_arr.sum())
    total_fp = int(fp_arr.sum())
    total_fn = int(fn_arr.sum())

    def _f1(tp: int, fp: int, fn: int) -> float:
        if tp == 0:
            return 0.0
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        if p + r == 0:
            return 0.0
        return 2 * p * r / (p + r)

    precision_pt = (
        total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    )
    recall_pt = (
        total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    )
    f1_pt = _f1(total_tp, total_fp, total_fn)

    rng = np.random.default_rng(seed)
    f1_boot = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n_tiles, size=n_tiles)
        f1_boot[b] = _f1(
            int(tp_arr[idx].sum()),
            int(fp_arr[idx].sum()),
            int(fn_arr[idx].sum()),
        )

    return {
        "f1": round(f1_pt, 6),
        "precision": round(precision_pt, 6),
        "recall": round(recall_pt, 6),
        "f1_ci_lower": round(float(np.percentile(f1_boot, 2.5)), 6),
        "f1_ci_upper": round(float(np.percentile(f1_boot, 97.5)), 6),
        "tp": total_tp,
        "fp": total_fp,
        "fn": total_fn,
        "n_detections": int(len(gdf_det)),
    }


# ---------------------------------------------------------------------------
# Worker function for parallel permutation testing
# ---------------------------------------------------------------------------


def _test_worker(args: tuple) -> dict:
    """ProcessPool worker for one pairwise permutation test."""
    (
        track,
        buffer_m,
        variant_a,
        variant_b,
        geojson_a,
        geojson_b,
        ref_path,
        bounds_path,
        n_perm,
        seed,
    ) = args
    gdf_a = load_geojson_detections(Path(geojson_a))
    gdf_b = load_geojson_detections(Path(geojson_b))
    gdf_ref = gpd.read_file(ref_path)
    if gdf_ref.crs is None:
        gdf_ref = gdf_ref.set_crs(TARGET_CRS)
    elif gdf_ref.crs.to_epsg() != 32635:
        gdf_ref = gdf_ref.to_crs(TARGET_CRS)
    gdf_ref = gdf_ref.explode(index_parts=False).reset_index(drop=True)

    gdf_bounds = gpd.read_file(bounds_path)
    if gdf_bounds.crs is None:
        gdf_bounds = gdf_bounds.set_crs(TARGET_CRS)
    elif gdf_bounds.crs.to_epsg() != 32635:
        gdf_bounds = gdf_bounds.to_crs(TARGET_CRS)

    result = run_permutation_test(
        gdf_a, gdf_b, gdf_ref, gdf_bounds,
        buffer_metres=buffer_m,
        n_permutations=n_perm,
        seed=seed,
    )
    return {
        "track": track,
        "buffer_m": buffer_m,
        "variant_a": variant_a,
        "variant_b": variant_b,
        "f1_a": result["global_a"]["f1"],
        "f1_b": result["global_b"]["f1"],
        "precision_a": result["global_a"]["precision"],
        "precision_b": result["global_b"]["precision"],
        "recall_a": result["global_a"]["recall"],
        "recall_b": result["global_b"]["recall"],
        "tp_a": result["global_a"]["tp"],
        "fp_a": result["global_a"]["fp"],
        "fn_a": result["global_a"]["fn"],
        "tp_b": result["global_b"]["tp"],
        "fp_b": result["global_b"]["fp"],
        "fn_b": result["global_b"]["fn"],
        "observed_f1_diff": result["permutation_test"]["observed_f1_diff"],
        "p_value": result["permutation_test"]["p_value"],
        "n_permutations": result["permutation_test"]["n_permutations"],
        "n_tiles": result["permutation_test"]["n_tiles"],
        "wins_a": result["permutation_test"]["wins_a"],
        "losses_a": result["permutation_test"]["losses_a"],
        "ties": result["permutation_test"]["ties"],
        "null_mean": result["permutation_test"]["null_distribution"]["mean"],
        "null_std": result["permutation_test"]["null_distribution"]["std"],
    }


# ---------------------------------------------------------------------------
# Per-(track, buffer) tier builder
# ---------------------------------------------------------------------------


def build_tier_for_cell(
    track: str,
    buffer_m: int,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    pair_results: list[dict],
) -> dict:
    """Given already-computed pairwise results for one (track, buffer),
    compute per-variant F1+CI (via bootstrap) and perform FDR + tiering.

    Args:
        track: 'image' or 'text'.
        buffer_m: buffer in metres.
        gdf_ref: reference gdf (EPSG:32635, exploded).
        gdf_bounds: bounds gdf (EPSG:32635).
        pair_results: list of 21 pairwise result dicts for this
            (track, buffer) family.

    Returns:
        dict with per-variant metrics, FDR-adjusted p-values, tier list,
        plus provenance.
    """
    # Compute per-variant F1+CI (bootstrap tiles) — one per variant.
    variant_metrics: dict[str, dict] = {}
    for variant in VARIANTS:
        gdf = load_geojson_detections(geojson_path_for(track, variant))
        m = compute_f1_ci(
            gdf, gdf_ref, gdf_bounds,
            buffer_metres=buffer_m,
            n_boot=BOOTSTRAP_N,
            seed=BOOTSTRAP_SEED,
        )
        variant_metrics[variant] = m

    # Apply BH-FDR within this family.
    raw_p = [r["p_value"] for r in pair_results]
    adj_p = apply_bh_correction(raw_p, q=FDR_Q)

    annotated = []
    for r, ap in zip(pair_results, adj_p):
        annotated.append({
            **r,
            "bh_adjusted_p": round(float(ap), 6),
            "significant_fdr_q05": bool(ap < FDR_Q),
        })

    # Sort variants by F1 descending.
    variants_by_f1 = sorted(
        [(v, variant_metrics[v]["f1"]) for v in VARIANTS],
        key=lambda kv: kv[1], reverse=True,
    )

    # Build lookup: (sorted(a,b)) -> significant
    sig_lookup: dict[tuple[str, str], bool] = {}
    for r in annotated:
        key = tuple(sorted([r["variant_a"], r["variant_b"]]))
        sig_lookup[key] = r["significant_fdr_q05"]

    tiers_names = greedy_clique_tiers(variants_by_f1, sig_lookup)

    # Tier assignment per variant.
    tier_of: dict[str, int] = {}
    for i, tier in enumerate(tiers_names, 1):
        for v in tier:
            tier_of[v] = i

    # Canonical-vs-each-alternative row.
    canonical_f1 = variant_metrics[CANONICAL]["f1"]
    canonical_vs_each = []
    for r in annotated:
        if CANONICAL not in (r["variant_a"], r["variant_b"]):
            continue
        other = r["variant_a"] if r["variant_b"] == CANONICAL else r["variant_b"]
        other_f1 = variant_metrics[other]["f1"]
        canonical_vs_each.append({
            "alternative": other,
            "f1_canonical": canonical_f1,
            "f1_alternative": other_f1,
            "delta_f1": round(other_f1 - canonical_f1, 6),
            "raw_p": r["p_value"],
            "bh_adjusted_p": r["bh_adjusted_p"],
            "significant_fdr_q05": r["significant_fdr_q05"],
            "tier_canonical": tier_of[CANONICAL],
            "tier_alternative": tier_of[other],
            "same_tier": tier_of[other] == tier_of[CANONICAL],
        })
    canonical_vs_each.sort(key=lambda x: x["alternative"])

    result = {
        "_metadata": {
            "script": "run_pairwise_matrix.py",
            "script_version": "1.0.0",
            "run_timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
            "git_commit": get_git_commit(),
            "track": track,
            "buffer_m": buffer_m,
            "n_variants": len(VARIANTS),
            "n_pairwise_tests": len(annotated),
            "n_permutations_per_test": N_PERMUTATIONS,
            "permutation_seed": PERM_SEED,
            "bootstrap_n": BOOTSTRAP_N,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "fdr_method": "Benjamini-Hochberg step-up",
            "fdr_q": FDR_Q,
            "tier_method": "greedy clique (F1 descending)",
            "input_files": {
                "reference": str(REF_PATH.relative_to(REPO_ROOT)),
                "bounds": str(BOUNDS_PATH.relative_to(REPO_ROOT)),
                "geojsons": {
                    v: str(geojson_path_for(track, v).relative_to(REPO_ROOT))
                    for v in VARIANTS
                },
            },
            "canonical_variant": CANONICAL,
        },
        "variant_metrics": variant_metrics,
        "variants_by_f1_desc": [
            {"variant": v, "f1": variant_metrics[v]["f1"]}
            for v, _ in variants_by_f1
        ],
        "tiers": [
            {
                "tier": i + 1,
                "variants": [
                    {
                        "variant": v,
                        "f1": variant_metrics[v]["f1"],
                        "precision": variant_metrics[v]["precision"],
                        "recall": variant_metrics[v]["recall"],
                        "f1_ci_lower": variant_metrics[v]["f1_ci_lower"],
                        "f1_ci_upper": variant_metrics[v]["f1_ci_upper"],
                        "tp": variant_metrics[v]["tp"],
                        "fp": variant_metrics[v]["fp"],
                        "fn": variant_metrics[v]["fn"],
                        "n_detections": variant_metrics[v]["n_detections"],
                    }
                    for v in tier
                ],
            }
            for i, tier in enumerate(tiers_names)
        ],
        "pairwise_tests": annotated,
        "canonical_vs_each": canonical_vs_each,
    }
    return result


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------


def write_markdown(result: dict, output_path: Path) -> None:
    """Write a human-readable tier table for one (track, buffer) cell."""
    meta = result["_metadata"]
    track = meta["track"]
    buffer_m = meta["buffer_m"]

    lines: list[str] = []
    lines.append(
        f"# Permutation Tiers — {track} track, {buffer_m} m buffer"
    )
    lines.append("")
    lines.append(f"**Generated**: {meta['run_timestamp_utc']}")
    lines.append(f"**Git commit**: {meta['git_commit']}")
    lines.append(
        f"**N permutations**: {meta['n_permutations_per_test']:,}, "
        f"seed {meta['permutation_seed']}"
    )
    lines.append(
        f"**Bootstrap CI**: {meta['bootstrap_n']:,} iterations, "
        f"seed {meta['bootstrap_seed']}"
    )
    lines.append(f"**FDR**: {meta['fdr_method']} at q = {meta['fdr_q']}")
    lines.append(f"**Family size**: {meta['n_pairwise_tests']} pairs")
    lines.append("")

    # Tier table.
    lines.append("## Tiers")
    lines.append("")
    for tier_block in result["tiers"]:
        tier = tier_block["tier"]
        variants_in_tier = tier_block["variants"]
        f1s = [v["f1"] for v in variants_in_tier]
        f1_min = min(f1s)
        f1_max = max(f1s)
        lines.append(
            f"### Tier {tier} — F1 range {f1_min:.4f}–{f1_max:.4f}"
        )
        lines.append("")
        lines.append(
            "| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |"
        )
        lines.append("|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|")
        for i, v in enumerate(variants_in_tier, 1):
            marker = " (canonical)" if v["variant"] == CANONICAL else ""
            lines.append(
                f"| {i} | `{v['variant']}`{marker} | "
                f"{v['f1']:.4f} | "
                f"[{v['f1_ci_lower']:.4f}, {v['f1_ci_upper']:.4f}] | "
                f"{v['precision']:.4f} | "
                f"{v['recall']:.4f} | "
                f"{v['tp']} | {v['fp']} | {v['fn']} | {v['n_detections']} |"
            )
        lines.append("")

    # Canonical vs each alternative.
    lines.append("## Canonical `adversarial-text` vs each alternative")
    lines.append("")
    lines.append(
        "| alternative | F1 canonical | F1 alt | Δ F1 (alt − canonical) | "
        "raw p | BH-adj p | significant @ FDR q=0.05 | same tier? |"
    )
    lines.append("|-------------|-------------:|-------:|----------------------:|------:|---------:|:---------------:|:----------:|")
    for row in result["canonical_vs_each"]:
        sig = "YES" if row["significant_fdr_q05"] else "no"
        same = "YES" if row["same_tier"] else "no"
        lines.append(
            f"| `{row['alternative']}` | "
            f"{row['f1_canonical']:.4f} | "
            f"{row['f1_alternative']:.4f} | "
            f"{row['delta_f1']:+.4f} | "
            f"{row['raw_p']:.4f} | "
            f"{row['bh_adjusted_p']:.4f} | {sig} | {same} |"
        )
    lines.append("")

    # All 21 pairs.
    lines.append("## All pairwise permutation tests")
    lines.append("")
    lines.append(
        "| variant A | variant B | F1 A | F1 B | Δ F1 | raw p | BH-adj p | sig? |"
    )
    lines.append("|-----------|-----------|-----:|-----:|-----:|------:|---------:|:----:|")
    for r in sorted(
        result["pairwise_tests"],
        key=lambda x: (x["variant_a"], x["variant_b"]),
    ):
        sig = "YES" if r["significant_fdr_q05"] else "no"
        lines.append(
            f"| `{r['variant_a']}` | `{r['variant_b']}` | "
            f"{r['f1_a']:.4f} | {r['f1_b']:.4f} | "
            f"{r['observed_f1_diff']:+.4f} | "
            f"{r['p_value']:.4f} | {r['bh_adjusted_p']:.4f} | {sig} |"
        )
    lines.append("")

    # Method block.
    lines.append("## Method")
    lines.append("")
    lines.append(
        "- **Detection source**: each variant's geojson materialised at the "
        "20 m-buffer optimum (vote_t, prob_t) pair. For 13 of 14 cells the "
        "per-buffer optima at 20/30/40/50 m are identical to the 20 m "
        "optimum; for `text-adversarial` at 50 m the 50 m-optimum differs "
        "by F1 = 0.0002 (negligible)."
    )
    lines.append(
        "- **Test statistic**: micro-average F1 difference (observed F1 "
        "A − F1 B) at the target buffer, computed from tile-level TP/FP/FN "
        "counts with per-map Hungarian matching at tolerance = buffer_m."
    )
    lines.append(
        "- **Permutation test**: paired tile-swap — for each permutation, "
        "independently swap per-tile (TP, FP, FN) counts between the two "
        "variants with probability 0.5, re-aggregate micro-average F1, "
        "compute the new difference. The p-value is the two-sided tail "
        "proportion |null diff| >= |observed diff|."
    )
    lines.append(
        f"- **Permutations**: {meta['n_permutations_per_test']:,} iterations, "
        f"seed {meta['permutation_seed']}."
    )
    lines.append(
        "- **FDR correction**: Benjamini-Hochberg step-up procedure applied "
        f"WITHIN each (track, buffer) family of "
        f"{meta['n_pairwise_tests']} pairs at q = {meta['fdr_q']}."
    )
    lines.append(
        "- **Tiering**: greedy clique. Rank variants by F1 descending; a "
        "variant joins the current tier iff its paired test against every "
        "existing tier member is non-significant after FDR. Otherwise open "
        "a new tier."
    )
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print(f"REPO_ROOT = {REPO_ROOT}")
    print(f"OUT_ROOT  = {OUT_ROOT}")
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for track in TRACKS:
        (OUT_ROOT / track).mkdir(parents=True, exist_ok=True)

    # Load reference and bounds once.
    print("Loading reference + bounds...")
    gdf_ref, gdf_bounds = load_ref_and_bounds()
    print(f"  reference points: {len(gdf_ref)}")
    print(f"  bounds tiles    : {len(gdf_bounds)}")

    # Build the full set of pairwise tasks: 2 tracks × 4 buffers × 21 pairs.
    tasks: list[tuple] = []
    for track in TRACKS:
        for buffer_m in BUFFERS:
            for variant_a, variant_b in combinations(VARIANTS, 2):
                tasks.append((
                    track,
                    buffer_m,
                    variant_a,
                    variant_b,
                    str(geojson_path_for(track, variant_a)),
                    str(geojson_path_for(track, variant_b)),
                    str(REF_PATH),
                    str(BOUNDS_PATH),
                    N_PERMUTATIONS,
                    PERM_SEED,
                ))
    print(f"Total pairwise tasks: {len(tasks)}")
    assert len(tasks) == 2 * 4 * 21, f"expected 168, got {len(tasks)}"

    # Parallel execution — use multiple processes for independent permutation
    # tests. Avoid over-subscribing: leave some CPU head-room for the
    # parallel per-architecture agent also running on sapphire.
    max_workers = 8
    print(f"Running with max_workers={max_workers}...")
    t0 = time.time()

    results_by_cell: dict[tuple[str, int], list[dict]] = {}
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(_test_worker, t) for t in tasks]
        n_done = 0
        for fut in as_completed(futures):
            r = fut.result()
            key = (r["track"], r["buffer_m"])
            results_by_cell.setdefault(key, []).append(r)
            n_done += 1
            if n_done % 10 == 0 or n_done == len(tasks):
                elapsed = time.time() - t0
                print(
                    f"  [{n_done}/{len(tasks)}] elapsed {elapsed:.1f}s "
                    f"| last: {r['track']} @{r['buffer_m']}m "
                    f"{r['variant_a']} vs {r['variant_b']} "
                    f"p={r['p_value']:.4f}"
                )

    print(f"All pairwise tests done in {time.time() - t0:.1f}s")

    # For each (track, buffer): compute variant metrics + FDR + tiers.
    print("Building per-(track, buffer) tier tables...")
    for track in TRACKS:
        for buffer_m in BUFFERS:
            key = (track, buffer_m)
            pair_results = results_by_cell[key]
            assert len(pair_results) == 21, (
                f"expected 21 pairs for {key}, got {len(pair_results)}"
            )
            result = build_tier_for_cell(
                track, buffer_m, gdf_ref, gdf_bounds, pair_results,
            )
            json_path = OUT_ROOT / track / f"permutation_tiers_{buffer_m}m.json"
            md_path = OUT_ROOT / track / f"permutation_tiers_{buffer_m}m.md"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            write_markdown(result, md_path)
            print(
                f"  wrote {json_path.relative_to(REPO_ROOT)} "
                f"({len(result['tiers'])} tiers)"
            )
            print(
                f"  wrote {md_path.relative_to(REPO_ROOT)}"
            )

    print()
    print("All per-(track, buffer) artefacts written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
