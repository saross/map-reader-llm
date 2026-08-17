#!/usr/bin/env python3
"""E45 bootstrap pairings for the H2 and H3 family-FDR primary contrasts.

The family-level Benjamini-Hochberg correction (results/family-fdr/)
consumed permutation p-values for H2 and H3. Erratum E45 discloses the
permutation method as unregistered; the registered inference is
bootstrap estimation (95 % CIs, tile-level resampling, percentile
method, 1,000 iterations — parameters fixed pre-lodgement in
Decision 10, `decisions-log.md:337`; E54 documents the 10,000-iteration
convention for post-hoc narrow-effect analyses). This script computes
the registered bootstrap construction for exactly the two contrasts the
family correction consumed, so Methods can report the registered
instrument alongside the permutation result wherever a confirmatory
claim rests on one (S135 analysis block, items 1-2;
`planning/s135-analysis-block-2026-08-17.md`).

Contrasts (from `reports/verification/family-fdr-registration.md` § 6):

- **H2**: Flash HIGH text 16-of-30 + PV vs Flash HIGH text 26-of-30.
  Per-tile tables come from a non-quiet re-run of
  `run_pairwise_tests.py` (same code path, seed, and inputs as the
  committed artefact, which was written with `--quiet` and so carries
  no per_tile block).
- **H3**: consensus-flash-high-text-26of30 vs
  `pv-diag-384::baseline-flash-text-high-t-0-7`. Per-tile tables are
  rebuilt with `consensus_vs_baseline_tiering`'s own cell loaders
  (consensus: single aggregated set, integer counts; single-pass:
  pass-averaged float counts) — the exact arrays the committed
  permutation consumed.

Reproduction gates (block-plan hardening 1) run BEFORE any bootstrap:
each contrast must reproduce the committed micro-F1 point estimates and
difference to within 1e-6. The bootstrap then resamples 487 evaluation
tiles with replacement, recomputing the paired micro-F1 difference:
B = 1,000 (registered-convention primary) and B = 10,000 (E54
narrow-effect sensitivity), seed 42, percentile CI95, two-sided
p = max(2 * min tail, 1/B) — conventions copied from the family-FDR H1
leg (`compute_family_fdr.py`) for cross-artefact comparability.

Usage (run on sapphire; ~seconds)::

    .venv/bin/python scripts/e45_bootstrap_pairings.py \
        --h2-rerun-json results/e45-bootstrap-pairings/h2-rerun/group_1_architecture/pv-vs-consensus-flash-high-text-16-of-30-pv-vs-flash-high-text-26-of-30.json

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

SEED = 42
B_PRIMARY = 1_000       # registered convention (Decision 10, E54)
B_SENSITIVITY = 10_000  # E54 post-hoc narrow-effect convention
GATE_TOL = 1e-6

COMMITTED_H2 = (BASE_DIR / "results/pairwise/20m/group_1_architecture/"
                "pv-vs-consensus-flash-high-text-16-of-30-pv-vs-"
                "flash-high-text-26-of-30.json")
COMMITTED_H3_TIERING = (BASE_DIR / "results/diversity-dividend-384/"
                        "tiering-champions/tiering_20m.json")
DD_SPEC = BASE_DIR / "planning/diversity-dividend-cells-2026-06-06.json"
H3_REF_A = "consensus-flash-high-text-26of30"
H3_REF_B = "pv-diag-384::baseline-flash-text-high-t-0-7"


def micro_f1(tp: float, fp: float, fn: float) -> float:
    """Micro-averaged F1 from summed tile counts.

    Args:
        tp: Summed true positives.
        fp: Summed false positives.
        fn: Summed false negatives.

    Returns:
        F1, or 0.0 where the denominator is zero.
    """
    denom = 2 * tp + fp + fn
    return (2 * tp / denom) if denom > 0 else 0.0


def paired_bootstrap(tp_a: np.ndarray, fp_a: np.ndarray, fn_a: np.ndarray,
                     tp_b: np.ndarray, fp_b: np.ndarray, fn_b: np.ndarray,
                     n_iterations: int, seed: int) -> dict:
    """Paired tile-resampling bootstrap of a micro-F1 difference.

    The same resampled tile index set is applied to both arms (paired
    design), micro-F1 is recomputed per arm, and the difference
    distribution yields the percentile CI and the two-sided p per the
    family-FDR H1 conventions (2 * min tail, floored at 1/B).

    Args:
        tp_a: Per-tile true positives, arm A (length = n tiles).
        fp_a: Per-tile false positives, arm A.
        fn_a: Per-tile false negatives, arm A.
        tp_b: Per-tile true positives, arm B.
        fp_b: Per-tile false positives, arm B.
        fn_b: Per-tile false negatives, arm B.
        n_iterations: Bootstrap iterations (B).
        seed: RNG seed.

    Returns:
        Dict with the observed delta, CI95 bounds, tail proportions,
        p-value, and floor flag.
    """
    lengths = {len(a) for a in (tp_a, fp_a, fn_a, tp_b, fp_b, fn_b)}
    if len(lengths) != 1:
        raise ValueError(f"per-tile arrays differ in length: {lengths} — "
                         "a paired bootstrap requires aligned arms")
    n = len(tp_a)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_iterations, n))
    deltas = np.empty(n_iterations)
    for i in range(n_iterations):
        take = idx[i]
        deltas[i] = (micro_f1(tp_a[take].sum(), fp_a[take].sum(),
                              fn_a[take].sum())
                     - micro_f1(tp_b[take].sum(), fp_b[take].sum(),
                                fn_b[take].sum()))
    prop_le = float(np.mean(deltas <= 0))
    prop_gt = float(np.mean(deltas > 0))
    p_value = max(2.0 * min(prop_le, prop_gt), 1.0 / n_iterations)
    observed = micro_f1(tp_a.sum(), fp_a.sum(), fn_a.sum()) - micro_f1(
        tp_b.sum(), fp_b.sum(), fn_b.sum())
    ci_lower = round(float(np.percentile(deltas, 2.5)), 6)
    ci_upper = round(float(np.percentile(deltas, 97.5)), 6)
    return {
        "n_iterations": n_iterations,
        "seed": seed,
        "observed_delta": round(float(observed), 6),
        "bootstrap_delta_mean": round(float(np.mean(deltas)), 6),
        "ci95": {"lower": ci_lower, "upper": ci_upper},
        "prop_le_zero": prop_le,
        "prop_gt_zero": prop_gt,
        "p_value": p_value,
        "p_at_floor": p_value <= 2.0 / n_iterations,
        # Derived from the same rounded bounds reported above, so the
        # flag can never disagree with the artefact's own CI (audit L-4).
        "ci_excludes_zero": bool(ci_lower > 0 or ci_upper < 0),
    }


def load_h2_per_tile(rerun_json: Path) -> tuple[dict, dict]:
    """Load per-tile arrays for the H2 contrast from the non-quiet re-run.

    Args:
        rerun_json: Path to the re-run comparison JSON (with per_tile).

    Returns:
        (arrays dict with tp_a..fn_b as np.ndarray, gate dict).

    Raises:
        SystemExit: If a reproduction gate fails.
    """
    rerun = json.loads(rerun_json.read_text())
    committed = json.loads(COMMITTED_H2.read_text())
    per_tile = rerun.get("per_tile")
    if not per_tile:
        sys.exit(f"GATE FAIL (H2): {rerun_json} carries no per_tile block")

    arrays = {k: np.array([float(t[k]) for t in per_tile])
              for k in ("tp_a", "fp_a", "fn_a", "tp_b", "fp_b", "fn_b")}
    checks = {
        "n_tiles": (len(per_tile),
                    committed["permutation_test"]["n_tiles"]),
        "f1_a": (micro_f1(arrays["tp_a"].sum(), arrays["fp_a"].sum(),
                          arrays["fn_a"].sum()),
                 committed["condition_a"]["f1"]),
        "f1_b": (micro_f1(arrays["tp_b"].sum(), arrays["fp_b"].sum(),
                          arrays["fn_b"].sum()),
                 committed["condition_b"]["f1"]),
        "observed_f1_diff": (rerun["permutation_test"]["observed_f1_diff"],
                             committed["permutation_test"]["observed_f1_diff"]),
        "p_value": (rerun["permutation_test"]["p_value"],
                    committed["permutation_test"]["p_value"]),
        # Exact permutation fingerprint (audit L-2): the win/loss/tie
        # split discriminates where the floored p-value cannot.
        "wins_a": (rerun["permutation_test"]["wins_a"],
                   committed["permutation_test"]["wins_a"]),
        "losses_a": (rerun["permutation_test"]["losses_a"],
                     committed["permutation_test"]["losses_a"]),
    }
    gate = _run_gate("H2", checks)
    return arrays, gate


def load_h3_per_tile() -> tuple[dict, dict]:
    """Rebuild per-tile arrays for the H3 contrast via the tiering loaders.

    Returns:
        (arrays dict, gate dict).

    Raises:
        SystemExit: If a reproduction gate fails.
    """
    import geopandas as gpd

    import consensus_vs_baseline_tiering as cvb

    spec = json.loads(DD_SPEC.read_text())
    gdf_ref = gpd.read_file(
        BASE_DIR / spec["ground_truth"]).to_crs(cvb.TARGET_CRS)
    gdf_bounds = gpd.read_file(
        BASE_DIR / spec["bounds"]).to_crs(cvb.TARGET_CRS)
    tile_order = list(gdf_bounds["tile_name"].unique())

    consensus = cvb.load_consensus_cells_with_stats(
        spec, {"champion"}, gdf_ref, gdf_bounds, tile_order)
    board = cvb.load_board_cells_with_stats(gdf_ref, gdf_bounds, tile_order)
    cell_a = next(c for c in consensus if c["label"] == H3_REF_A)
    cell_b = next(c for c in board if c["ref"] == H3_REF_B)

    committed = json.loads(COMMITTED_H3_TIERING.read_text())
    pair = next(
        r for r in committed["pairwise"]
        if {r["ref_a"], r["ref_b"]} == {H3_REF_A, H3_REF_B})
    # Orient the committed entry so "a" is the consensus cell.
    flip = pair["ref_a"] != H3_REF_A
    committed_a = pair["f1_b"] if flip else pair["f1_a"]
    committed_b = pair["f1_a"] if flip else pair["f1_b"]
    committed_diff = -pair["observed_diff"] if flip else pair["observed_diff"]

    arrays = {
        "tp_a": cell_a["tp"], "fp_a": cell_a["fp"], "fn_a": cell_a["fn"],
        "tp_b": cell_b["tp"], "fp_b": cell_b["fp"], "fn_b": cell_b["fn"],
    }
    checks = {
        "n_tiles": (len(tile_order), pair["n_tiles"]),
        "f1_a": (cell_a["observed_micro_f1"], committed_a),
        "f1_b": (cell_b["observed_micro_f1"], committed_b),
        "observed_f1_diff": (
            cell_a["observed_micro_f1"] - cell_b["observed_micro_f1"],
            committed_diff),
    }
    gate = _run_gate("H3", checks)
    return arrays, gate


def _run_gate(name: str, checks: dict) -> dict:
    """Compare recomputed values with committed values at GATE_TOL.

    Args:
        name: Contrast name for messages.
        checks: Mapping of field -> (recomputed, committed).

    Returns:
        Gate record dict (all fields, both values, pass flags).

    Raises:
        SystemExit: On any mismatch beyond GATE_TOL.
    """
    record = {}
    failures = []
    for field, (ours, theirs) in checks.items():
        ok = abs(float(ours) - float(theirs)) <= GATE_TOL
        record[field] = {"recomputed": float(ours), "committed": float(theirs),
                         "pass": ok}
        if not ok:
            failures.append(f"{name}.{field}: {ours} != {theirs}")
    if failures:
        sys.exit("GATE FAIL — halting before bootstrap (block-plan stop "
                 "state):\n  " + "\n  ".join(failures))
    print(f"  gate {name}: {len(checks)}/{len(checks)} reproduced "
          f"(tol {GATE_TOL})", flush=True)
    return record


def main() -> int:
    """Run both pairings end to end and write the artefact."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--h2-rerun-json", type=Path, required=True,
        help="Non-quiet re-run comparison JSON carrying per_tile")
    parser.add_argument(
        "--output-dir", type=Path,
        default=BASE_DIR / "results" / "e45-bootstrap-pairings",
        help="Output directory (default: results/e45-bootstrap-pairings)")
    args = parser.parse_args()

    print("H2: loading per-tile tables from the non-quiet re-run ...",
          flush=True)
    h2_arrays, h2_gate = load_h2_per_tile(args.h2_rerun_json)
    print("H3: rebuilding per-tile tables via the tiering loaders ...",
          flush=True)
    h3_arrays, h3_gate = load_h3_per_tile()

    results = {}
    for name, arrays, gate in (("H2", h2_arrays, h2_gate),
                               ("H3", h3_arrays, h3_gate)):
        runs = {}
        for tag, b in (("registered_b1000", B_PRIMARY),
                       ("e54_sensitivity_b10000", B_SENSITIVITY)):
            print(f"  {name} bootstrap B={b} ...", flush=True)
            runs[tag] = paired_bootstrap(
                arrays["tp_a"], arrays["fp_a"], arrays["fn_a"],
                arrays["tp_b"], arrays["fp_b"], arrays["fn_b"],
                n_iterations=b, seed=SEED)
        results[name] = {"reproduction_gate": gate, "bootstrap": runs}

    out = {
        "_README": (
            "E45 bootstrap pairings: the registered bootstrap construction "
            "computed for the two family-FDR primary contrasts that "
            "entered the family on permutation floors (H2, H3; H8's "
            "family input is also permutation-sourced but is a Simes "
            "minimum over seven contrasts, for which a paired delta is "
            "not defined). REGISTERED quantities: the percentile CI95 "
            "from tile-level resampling and the CI-excludes-zero "
            "significance reading (Decision 10, decisions-log.md:335-345; "
            "B=1,000 registered, B=10,000 per E54). The 2*min-tail "
            "p-value is NOT registered — it is carried for comparability "
            "with the family-FDR H1 leg's convention only (audit M-9). "
            "The permutation p remains the family input; this artefact "
            "is the paired disclosure, not a replacement."),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registration_anchors": {
            "registered_inference": (
                "docs/methodology/preregistration/osf/preregistration.md:293 "
                "(95% bootstrapped CIs); parameters Decision 10, "
                "docs/methodology/preregistration/decisions-log.md:335-345 "
                "(parameter row :345)"),
            "family_construction": (
                "reports/verification/family-fdr-registration.md § 6 "
                "(H2, H3 primary rows)"),
            "errata": ["E45", "E54"],
        },
        "contrasts": {
            "H2": {"a": "Flash HIGH text 16-of-30 + PV",
                   "b": "Flash HIGH text 26-of-30",
                   "committed_artefact": str(
                       COMMITTED_H2.relative_to(BASE_DIR)),
                   "h2_rerun_json": str(
                       args.h2_rerun_json.resolve().relative_to(BASE_DIR)
                       if args.h2_rerun_json.resolve().is_relative_to(
                           BASE_DIR) else args.h2_rerun_json)},
            "H3": {"a": H3_REF_A, "b": H3_REF_B,
                   "committed_artefact": str(
                       COMMITTED_H3_TIERING.relative_to(BASE_DIR)),
                   "statistic_note": (
                       "single-pass arm uses pass-averaged per-tile counts "
                       "— identical to the committed permutation's inputs; "
                       "the tiering artefact's headline f1_b 0.3871 is the "
                       "eval mean-of-runs vintage (<=0.0005 apart)")},
        },
        "method": ("paired tile bootstrap of the micro-F1 difference; "
                   "percentile CI95; two-sided p = 2*min tail, floor 1/B; "
                   "seed 42; conventions per compute_family_fdr.py H1 leg"),
        "results": results,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / "e45_bootstrap_pairings.json"
    out_path.write_text(json.dumps(out, indent=1))
    print(f"Wrote {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
