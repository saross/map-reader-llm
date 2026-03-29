#!/usr/bin/env python3
"""
Test prompt engineering effects via pairwise permutation tests.

Runs tile-swap permutation tests on Phase 2 (512px, 340-tile) conditions
to formally test whether prompt engineering variables (library composition,
text treatment, example ordering) produce significant F1 differences.

Tests are grouped by factor, with each comparison holding all other
variables constant. This is the statistical evidence for the claim that
"within a fixed architecture, prompt details make little difference."

Run on sapphire:
    python scripts/test-prompt-engineering-effects.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from lib_advanced_metrics import compute_per_tile_tp_fp_fn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────

PROJECT = Path(__file__).parent.parent
GROUND_TRUTH = PROJECT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS_512 = PROJECT / "inputs/vectors/bounds/full_evaluation_bounds.geojson"
RETEST_DIR = PROJECT / "outputs/retest"
OUTPUT_DIR = PROJECT / "results/pairwise/prompt-engineering-20m"

BUFFER = 20
N_PERMUTATIONS = 10_000
SEED = 42


# ── Permutation test (adapted from pairwise_permutation_test.py) ────


def run_permutation_test(
    gdf_a: gpd.GeoDataFrame,
    gdf_b: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int,
    n_permutations: int = 10_000,
    seed: int = 42,
) -> dict:
    """Run tile-swap permutation test between two conditions."""
    # Compute per-tile metrics for each condition
    tiles_a = compute_per_tile_tp_fp_fn(
        gdf_a, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )
    tiles_b = compute_per_tile_tp_fp_fn(
        gdf_b, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )

    # Align on common tiles
    common = sorted(
        set(tiles_a["tile_name"]) & set(tiles_b["tile_name"]),
    )
    ta = tiles_a.set_index("tile_name").loc[common]
    tb = tiles_b.set_index("tile_name").loc[common]

    def micro_f1(df):
        """Compute micro-average F1 from per-tile TP/FP/FN."""
        tp = df["tp"].sum()
        fp = df["fp"].sum()
        fn = df["fn"].sum()
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0
        return 2 * p * r / (p + r) if (p + r) > 0 else 0

    f1_a = micro_f1(ta)
    f1_b = micro_f1(tb)
    observed_diff = f1_a - f1_b

    # Permutation test: swap tiles between conditions
    rng = np.random.default_rng(seed)
    n_tiles = len(common)
    count_extreme = 0

    for _ in range(n_permutations):
        swap = rng.random(n_tiles) < 0.5
        perm_a = ta.copy()
        perm_b = tb.copy()
        for col in ["tp", "fp", "fn"]:
            perm_a.loc[swap, col] = tb.loc[swap, col].values
            perm_b.loc[swap, col] = ta.loc[swap, col].values

        perm_diff = micro_f1(perm_a) - micro_f1(perm_b)
        if abs(perm_diff) >= abs(observed_diff):
            count_extreme += 1

    p_value = count_extreme / n_permutations

    return {
        "f1_a": round(f1_a, 4),
        "f1_b": round(f1_b, 4),
        "delta_f1": round(observed_diff, 4),
        "p_value": round(p_value, 4),
        "n_tiles": n_tiles,
        "n_permutations": n_permutations,
    }


# ── Condition loading ────────────────────────────────────────────────


def load_condition(
    phase_dir: Path,
    track: str | None,
    condition: str,
) -> gpd.GeoDataFrame:
    """Load averaged detections for a condition (all runs merged)."""
    if track:
        cond_dir = phase_dir / track / condition
    else:
        cond_dir = phase_dir / condition

    geojsons = sorted(cond_dir.rglob("detections_*.geojson"))
    if not geojsons:
        raise FileNotFoundError(
            f"No GeoJSON found in {cond_dir}",
        )

    gdfs = [gpd.read_file(g) for g in geojsons]
    # For multi-run conditions, concatenate and use all detections
    combined = gpd.GeoDataFrame(
        __import__("pandas").concat(gdfs, ignore_index=True),
        crs=gdfs[0].crs,
    )
    return combined


# ── Comparison definitions ───────────────────────────────────────────


def define_comparisons() -> list[dict]:
    """Define all within-factor pairwise comparisons."""
    comparisons = []

    # Phase 2c: Library composition — text track (5 conditions, all pairs)
    p2c_text = ["canonical", "plus-hp", "pure-positive-canon", "scale-4", "scale-8"]
    for a, b in combinations(p2c_text, 2):
        comparisons.append({
            "group": "Library composition (text)",
            "label_a": f"P2c Text {a}",
            "label_b": f"P2c Text {b}",
            "phase": "phase2c",
            "track": "track2-text",
            "cond_a": a,
            "cond_b": b,
        })

    # Phase 2c: Library composition — image track (5 conditions)
    p2c_image = ["canonical", "plus-hp", "pure-positive-canon", "scale-4", "scale-8"]
    for a, b in combinations(p2c_image, 2):
        comparisons.append({
            "group": "Library composition (image)",
            "label_a": f"P2c Image {a}",
            "label_b": f"P2c Image {b}",
            "phase": "phase2c",
            "track": "track1-image",
            "cond_a": a,
            "cond_b": b,
        })

    # Phase 2d: Text treatment — 2 comparisons (terse vs verbose)
    for track, track_label in [
        ("track1-image", "image"),
        ("track2-text", "text"),
    ]:
        comparisons.append({
            "group": f"Text treatment ({track_label})",
            "label_a": f"P2d {track_label.capitalize()} terse",
            "label_b": f"P2d {track_label.capitalize()} verbose",
            "phase": "phase2d",
            "track": track,
            "cond_a": "terse",
            "cond_b": "verbose",
        })

    # Phase 2e: Example ordering (4 conditions, all pairs)
    p2e = ["canonical-first", "canonical-last", "config-default", "random"]
    for a, b in combinations(p2e, 2):
        comparisons.append({
            "group": "Example ordering",
            "label_a": f"P2e {a}",
            "label_b": f"P2e {b}",
            "phase": "phase2e",
            "track": None,
            "cond_a": a,
            "cond_b": b,
        })

    # Phase 2a: Modality (5 conditions, all pairs) — expect significant
    p2a = [
        "brief-text", "verbose-text", "brief-text-image",
        "verbose-text-image", "image-only",
    ]
    for a, b in combinations(p2a, 2):
        comparisons.append({
            "group": "Modality/elaboration",
            "label_a": f"P2a {a}",
            "label_b": f"P2a {b}",
            "phase": "phase2a",
            "track": None,
            "cond_a": a,
            "cond_b": b,
        })

    # Phase 2b: Temperature — text track (5 temps, all pairs)
    p2b_temps = ["T0.0", "T0.3", "T0.7", "T1.0", "T1.3"]
    for a, b in combinations(p2b_temps, 2):
        comparisons.append({
            "group": "Temperature (text)",
            "label_a": f"P2b Text {a}",
            "label_b": f"P2b Text {b}",
            "phase": "phase2b",
            "track": "track2-text",
            "cond_a": a,
            "cond_b": b,
        })

    # Phase 2b: Temperature — image track
    for a, b in combinations(p2b_temps, 2):
        comparisons.append({
            "group": "Temperature (image)",
            "label_a": f"P2b Image {a}",
            "label_b": f"P2b Image {b}",
            "phase": "phase2b",
            "track": "track1-image",
            "cond_a": a,
            "cond_b": b,
        })

    return comparisons


# ── Main ─────────────────────────────────────────────────────────────


def main() -> None:
    """Run all prompt engineering pairwise comparisons."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log.info("Loading ground truth: %s", GROUND_TRUTH)
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    log.info("Loading bounds (512px): %s", BOUNDS_512)
    gdf_bounds = gpd.read_file(BOUNDS_512)

    target_crs = gdf_bounds.crs
    if gdf_ref.crs != target_crs:
        gdf_ref = gdf_ref.to_crs(target_crs)

    log.info(
        "Reference: %d mounds, %d tiles",
        len(gdf_ref),
        len(gdf_bounds),
    )

    comparisons = define_comparisons()
    log.info("Defined %d comparisons", len(comparisons))

    # Cache loaded conditions
    cache: dict[str, gpd.GeoDataFrame] = {}

    results = []
    for i, comp in enumerate(comparisons, 1):
        key_a = f"{comp['phase']}/{comp['track']}/{comp['cond_a']}"
        key_b = f"{comp['phase']}/{comp['track']}/{comp['cond_b']}"

        # Load conditions (with caching)
        for key, phase, track, cond in [
            (key_a, comp["phase"], comp["track"], comp["cond_a"]),
            (key_b, comp["phase"], comp["track"], comp["cond_b"]),
        ]:
            if key not in cache:
                phase_dir = RETEST_DIR / phase
                gdf = load_condition(phase_dir, track, cond)
                if gdf.crs != target_crs:
                    gdf = gdf.to_crs(target_crs)
                cache[key] = gdf

        gdf_a = cache[key_a]
        gdf_b = cache[key_b]

        log.info(
            "[%d/%d] %s: %s vs %s",
            i,
            len(comparisons),
            comp["group"],
            comp["label_a"],
            comp["label_b"],
        )

        result = run_permutation_test(
            gdf_a,
            gdf_b,
            gdf_ref,
            gdf_bounds,
            buffer_metres=BUFFER,
            n_permutations=N_PERMUTATIONS,
            seed=SEED,
        )

        result.update({
            "group": comp["group"],
            "label_a": comp["label_a"],
            "label_b": comp["label_b"],
        })
        results.append(result)

        sig = "***" if result["p_value"] < 0.001 else (
            "**" if result["p_value"] < 0.01 else (
                "*" if result["p_value"] < 0.05 else "ns"
            )
        )
        log.info(
            "  ΔF1=%+.4f, p=%.4f %s",
            result["delta_f1"],
            result["p_value"],
            sig,
        )

    # Group results and summarise
    groups = {}
    for r in results:
        g = r["group"]
        if g not in groups:
            groups[g] = []
        groups[g].append(r)

    print("\n" + "=" * 70)
    print("PROMPT ENGINEERING PERMUTATION TEST RESULTS (20m, 512px)")
    print("=" * 70)

    for group_name, group_results in groups.items():
        n_sig = sum(
            1 for r in group_results if r["p_value"] < 0.05
        )
        print(f"\n{group_name}: {n_sig}/{len(group_results)} significant")
        for r in sorted(
            group_results,
            key=lambda x: abs(x["delta_f1"]),
            reverse=True,
        ):
            sig = "***" if r["p_value"] < 0.001 else (
                "**" if r["p_value"] < 0.01 else (
                    "*" if r["p_value"] < 0.05 else "ns"
                )
            )
            print(
                f"  {r['label_a']:<25} vs {r['label_b']:<25} "
                f"ΔF1={r['delta_f1']:>+.4f}  p={r['p_value']:.4f} {sig}",
            )

    # Write results
    output_json = OUTPUT_DIR / "prompt_engineering_pairwise.json"
    with open(output_json, "w") as f:
        json.dump(
            {
                "metadata": {
                    "timestamp": datetime.now(
                        timezone.utc,
                    ).isoformat(),
                    "buffer_metres": BUFFER,
                    "n_permutations": N_PERMUTATIONS,
                    "seed": SEED,
                    "tile_size": 512,
                    "n_tiles": len(gdf_bounds),
                    "n_comparisons": len(results),
                },
                "comparisons": results,
            },
            f,
            indent=2,
        )
    log.info("Results written to %s", output_json)

    # Write CSV
    output_csv = OUTPUT_DIR / "prompt_engineering_pairwise.csv"
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "group",
                "label_a",
                "label_b",
                "f1_a",
                "f1_b",
                "delta_f1",
                "p_value",
                "n_tiles",
                "n_permutations",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    log.info("CSV written to %s", output_csv)


if __name__ == "__main__":
    main()
