#!/usr/bin/env python3
"""
Stage B Verifier-Temperature Pilot Driver
==========================================

Materialises post-verifier detection GeoJSONs and evaluates them against the
canonical 4-map gold-standard ground truth at three verifier temperatures
(T = 0.0, 0.5, 1.0). Emits per-(T, prob_t) evaluation directories and a
machine-readable summary JSON suitable for the Stage B comparison report.

Pipeline per (T, prob_t):

1. Materialise: ``scripts/materialise_pv_geojson.py``-style call applied to
   the canonical 4-of-5 consensus GeoJSON and the per-T probabilities,
   filtering at ``vote_t = 4`` and the supplied ``prob_t``.
2. Evaluate: ``scripts/evaluate_detections.py``-style call against the
   canonical gold-standard reference and Era 2 487-tile bounds at the
   buffer set, with bootstrap and tile-level MCC enabled.

Canonical operating-point values (matching the per-architecture leaderboard
methodology — `results/leaderboard/per-architecture/README.md`):

- ``vote_t``: 4 (4-of-5 proposer consensus gate, already enforced by the
  consensus-4of5.geojson input — supplied here for explicit-config sake).
- ``prob_t`` sweep: ``[0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]``.
- Headline cell: ``(vote_t=4, prob_t=0.15, buffer=20m)``.
- Buffers: ``[20, 30, 40, 50, 100]`` m.
- Bootstrap: 1,000 iterations, seed=42.
- Bounds: ``inputs/vectors/bounds/384/full_evaluation_bounds.geojson``.
- Reference: ``inputs/vectors/references/mounds-reference.geojson``.

The driver imports ``scripts.materialise_pv_geojson.materialise`` and
``scripts.evaluate_detections._evaluate_condition`` directly so that the run
shares the same code path and serialised metadata format as the canonical
evaluations under ``results/gold-standard-extended-buffer-sweep-era2/``.

Usage::

    python scripts/run_verifier_t_stage_b.py \\
        --output-root results/verifier-t-pilot \\
        --geojson-root outputs/verifier-t-pilot

Author: Claude Code (Opus 4.7) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import geopandas as gpd

# Ensure ``scripts`` is on the import path when invoked from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.evaluate_detections import (  # noqa: E402
    _evaluate_condition,
)
from scripts.materialise_pv_geojson import materialise  # noqa: E402

# ── Canonical Stage B parameters ─────────────────────────────────────
CONSENSUS_GEOJSON = REPO_ROOT / (
    "outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson"
)
PROBS_BY_T: dict[str, Path] = {
    "T0.0": REPO_ROOT / "outputs/h11/gold-standard-v2/verified-v1/probabilities.json",
    "T0.5": REPO_ROOT / "outputs/verifier-t-pilot/T0.5/probabilities.json",
    "T1.0": REPO_ROOT / "outputs/verifier-t-pilot/T1.0/probabilities.json",
}
GROUND_TRUTH = REPO_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS = REPO_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

VOTE_T = 4
PROB_THRESHOLDS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
BUFFERS = [20, 30, 40, 50, 100]
BOOTSTRAP = 1000
SEED = 42


def _round(x: float | None, n: int = 4) -> float | None:
    """Round optional float to ``n`` decimal places (None-safe)."""
    if x is None:
        return None
    return round(float(x), n)


def _extract_summary(eval_result: dict[str, Any]) -> dict[str, Any]:
    """Pull the headline F1/MCC fields out of an evaluation result.

    Args:
        eval_result: Output of ``_evaluate_condition`` — the inner summary
            dict directly (no enclosing ``summary`` key); it has per-buffer
            F1/precision/recall in ``buffers`` and a ``tile_classification``
            block when MCC was requested.

    Returns:
        A flat dict of (buffer_m, f1, f1_ci, mcc, mcc_ci, ...).
    """
    summary = eval_result
    flat: dict[str, Any] = {
        "label": summary.get("label"),
        "n_detections": summary.get("n_detections"),
        "buffers": [],
    }
    for buf in summary.get("buffers", []):
        flat["buffers"].append(
            {
                "buffer_metres": buf.get("buffer_metres"),
                "f1": _round(buf.get("f1")),
                "f1_ci_lower": _round(buf.get("f1_ci_lower")),
                "f1_ci_upper": _round(buf.get("f1_ci_upper")),
                "precision": _round(buf.get("precision")),
                "p_ci_lower": _round(buf.get("p_ci_lower")),
                "p_ci_upper": _round(buf.get("p_ci_upper")),
                "recall": _round(buf.get("recall")),
                "r_ci_lower": _round(buf.get("r_ci_lower")),
                "r_ci_upper": _round(buf.get("r_ci_upper")),
            }
        )
    tc = summary.get("tile_classification", {})
    if tc:
        mcc = tc.get("mcc", {})
        sens = tc.get("sensitivity", {})
        spec = tc.get("specificity", {})
        flat["tile_classification"] = {
            "confusion": tc.get("confusion"),
            "mcc": {
                "mean": _round(mcc.get("mean")),
                "ci_lower": _round(mcc.get("ci_lower")),
                "ci_upper": _round(mcc.get("ci_upper")),
            },
            "sensitivity": {
                "mean": _round(sens.get("mean")),
                "ci_lower": _round(sens.get("ci_lower")),
                "ci_upper": _round(sens.get("ci_upper")),
            },
            "specificity": {
                "mean": _round(spec.get("mean")),
                "ci_lower": _round(spec.get("ci_lower")),
                "ci_upper": _round(spec.get("ci_upper")),
            },
        }
    return flat


def run_one(
    t_label: str,
    prob_t: float,
    geojson_root: Path,
    output_root: Path,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict[str, Any]:
    """Materialise + evaluate one (T, prob_t) cell.

    Args:
        t_label: One of ``"T0.0"``, ``"T0.5"``, ``"T1.0"``.
        prob_t: Verifier probability threshold (e.g. ``0.15``).
        geojson_root: Root for materialised geojsons (one subdir per T).
        output_root: Root for evaluation results (one subdir per T).
        gdf_ref: Pre-loaded reference GeoDataFrame.
        gdf_bounds: Pre-loaded bounds GeoDataFrame.

    Returns:
        Flat summary dict suitable for inclusion in the cross-T table.
    """
    probs_path = PROBS_BY_T[t_label]
    if not probs_path.is_file():
        raise FileNotFoundError(f"Probabilities file missing: {probs_path}")

    # 1. Materialise. Use 5dp prob_t formatter so 0.05 stays "0.05",
    #    0.10 stays "0.10", etc., and never collapses to "0.1".
    prob_str = f"{prob_t:.2f}"
    geojson_dir = geojson_root / t_label / "materialised"
    geojson_dir.mkdir(parents=True, exist_ok=True)
    geojson_path = geojson_dir / f"vote{VOTE_T}_prob{prob_str}.geojson"
    n_kept = materialise(
        consensus_geojson=CONSENSUS_GEOJSON,
        probabilities_json=probs_path,
        vote_t=VOTE_T,
        prob_t=prob_t,
        output=geojson_path,
        strict_indexing=True,
    )

    # 2. Evaluate against ground truth + bounds.
    eval_dir = output_root / t_label / f"eval-vote{VOTE_T}-prob{prob_str}"
    eval_dir.mkdir(parents=True, exist_ok=True)
    label = (
        f"verifier-t-pilot-{t_label}-vote{VOTE_T}-prob{prob_str}"
    )
    eval_result = _evaluate_condition(
        det_files=[geojson_path],
        gdf_ref=gdf_ref,
        gdf_bounds=gdf_bounds,
        buffers=BUFFERS,
        n_bootstrap=BOOTSTRAP,
        seed=SEED,
        label=label,
        output_dir=eval_dir,
        compute_mcc=True,
        metadata={
            "t_label": t_label,
            "vote_t": VOTE_T,
            "prob_t": prob_t,
            "consensus_geojson": str(CONSENSUS_GEOJSON.relative_to(REPO_ROOT)),
            "probabilities_json": str(probs_path.relative_to(REPO_ROOT)),
            "n_materialised": n_kept,
            "stage": "verifier-t-pilot-stage-b",
        },
    )
    summary = _extract_summary(eval_result)
    summary["t_label"] = t_label
    summary["prob_t"] = prob_t
    summary["vote_t"] = VOTE_T
    summary["n_materialised"] = n_kept
    # Use relative paths when the caller routes outputs inside the repo;
    # otherwise fall back to absolute paths (e.g. /tmp smoke tests).
    try:
        summary["geojson_path"] = str(geojson_path.relative_to(REPO_ROOT))
    except ValueError:
        summary["geojson_path"] = str(geojson_path)
    try:
        summary["eval_dir"] = str(eval_dir.relative_to(REPO_ROOT))
    except ValueError:
        summary["eval_dir"] = str(eval_dir)
    return summary


def main() -> int:
    """CLI entry point."""
    # Allow CLI override of the module-level BOOTSTRAP constant. Declared at
    # the top of ``main`` so the assignment below is unambiguously module-scope.
    global BOOTSTRAP
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output-root", type=Path,
        default=REPO_ROOT / "results/verifier-t-pilot",
        help="Root for evaluation results (default: %(default)s)",
    )
    p.add_argument(
        "--geojson-root", type=Path,
        default=REPO_ROOT / "outputs/verifier-t-pilot",
        help="Root for materialised geojsons (default: %(default)s)",
    )
    p.add_argument(
        "--temperatures", nargs="+", default=["T0.0", "T0.5", "T1.0"],
        help="Subset of temperatures to run (default: all three).",
    )
    p.add_argument(
        "--prob-thresholds", type=float, nargs="+", default=PROB_THRESHOLDS,
        help=f"Prob_t sweep (default: {PROB_THRESHOLDS}).",
    )
    p.add_argument(
        "--bootstrap", type=int, default=BOOTSTRAP,
        help=(
            f"Bootstrap iterations for CI computation (default: {BOOTSTRAP}). "
            f"Pass --bootstrap 10000 to upgrade pre-existing N=1000 cells."
        ),
    )
    args = p.parse_args()
    # Apply CLI override of the module-level BOOTSTRAP constant so the
    # value flows through to ``run_one`` without further plumbing.
    BOOTSTRAP = args.bootstrap

    # Sanity check inputs.
    for path in [CONSENSUS_GEOJSON, GROUND_TRUTH, BOUNDS]:
        if not path.is_file():
            print(f"ERROR: input missing: {path}", file=sys.stderr)
            return 2
    for t in args.temperatures:
        if t not in PROBS_BY_T:
            print(f"ERROR: unknown temperature label {t!r}", file=sys.stderr)
            return 2

    # Pre-load reference + bounds once, reused across cells.
    print("Loading reference + bounds geometries (one-time)...")
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    gdf_bounds = gpd.read_file(BOUNDS)
    print(
        f"  ground truth: {len(gdf_ref)} mounds | "
        f"bounds: {len(gdf_bounds)} tiles"
    )

    # Run the (T x prob_t) grid.
    rows: list[dict[str, Any]] = []
    n_total = len(args.temperatures) * len(args.prob_thresholds)
    i = 0
    t_start = time.time()
    for t_label in args.temperatures:
        for prob_t in args.prob_thresholds:
            i += 1
            elapsed = time.time() - t_start
            print(
                f"[{i}/{n_total}] T={t_label} prob_t={prob_t} "
                f"(elapsed {elapsed:.1f}s)"
            )
            row = run_one(
                t_label=t_label,
                prob_t=prob_t,
                geojson_root=args.geojson_root,
                output_root=args.output_root,
                gdf_ref=gdf_ref,
                gdf_bounds=gdf_bounds,
            )
            rows.append(row)
            print(f"  n_materialised={row['n_materialised']}")
            for buf in row["buffers"]:
                if buf["buffer_metres"] in (20, 30, 50, 100):
                    print(
                        f"    {buf['buffer_metres']}m  "
                        f"F1={buf['f1']} "
                        f"[{buf['f1_ci_lower']}, {buf['f1_ci_upper']}]"
                    )
            tc = row.get("tile_classification") or {}
            mcc = tc.get("mcc", {})
            if mcc:
                print(
                    f"    MCC={mcc['mean']} "
                    f"[{mcc['ci_lower']}, {mcc['ci_upper']}]"
                )

    # Write the summary JSON.
    args.output_root.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_root / "stage-b-summary.json"
    summary_doc = {
        "version": "1.0",
        "stage": "verifier-t-pilot-stage-b",
        "consensus_geojson": str(CONSENSUS_GEOJSON.relative_to(REPO_ROOT)),
        "ground_truth": str(GROUND_TRUTH.relative_to(REPO_ROOT)),
        "bounds": str(BOUNDS.relative_to(REPO_ROOT)),
        "vote_t": VOTE_T,
        "prob_thresholds": args.prob_thresholds,
        "buffers": BUFFERS,
        "bootstrap": BOOTSTRAP,
        "seed": SEED,
        "temperatures": args.temperatures,
        "rows": rows,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_doc, f, indent=2)
    print(f"Wrote summary -> {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
