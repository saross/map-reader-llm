#!/usr/bin/env python3
"""
Execute the registered family-level BH-FDR correction (and its H1 input).

Implements `reports/verification/family-fdr-registration.md` (REGISTERED
2026-07-30, committed before this script ran):

1. **H1 primary — registered contrast CMT-0106, first execution**
   (§ 5.1.1): the pooled modality contrast, text-only conditions
   {brief-text, verbose-text} versus image-using conditions {image-only,
   brief-text-image, verbose-text-image}, on the Era-1 340-tile retest
   corpus. Per paired bootstrap tile-resample (B = 10 000, seed 42): each
   condition scores its mean F1 across runs (per-run evaluation per E22,
   per-tile TP/FP/FN precompute per E26, 20 m buffer); each group scores
   the unweighted mean of its conditions; the contrast is text-only minus
   image-using. Two-sided bootstrap p per the executed artefact's
   convention (2 x min tail proportion, floored at 1/B).

2. **The seven-hypothesis BH-FDR family** (§ 8): monotone step-up at
   q = 0.05 over the seven registered primaries (H6 never ran), with
   resolution floors recorded as inequalities and the fixed tie rule.
   Every registered p-value is re-read from its anchored artefact and
   asserted equal to the value quoted in the registration before use.

Validation gates (both must pass before anything is written):

- **Gate A**: per-condition full-set mean F1 reproduces the committed
  `results/retest/phase2a-evaluation.json` values.
- **Gate B**: the vectorised bootstrap scoring reproduces the library
  `aggregate_tile_metrics` path exactly on a 50-resample probe.

Outputs (all under ``results/family-fdr/``): the H1 artefact, the family
artefact, a human-readable report, and a metadata sidecar.

Zero API cost; pure recomputation over committed artefacts. Run on
sapphire per the project compute rule:

    python scripts/compute_family_fdr.py
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR.parent))

from analyse_phase2_results import load_condition_results  # noqa: E402
from lib_advanced_metrics import (  # noqa: E402
    aggregate_tile_metrics,
    compute_per_tile_tp_fp_fn,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = SCRIPTS_DIR.parent

# --- registration constants (family-fdr-registration.md § 5.1.1, § 8) ---
REGISTRATION = "reports/verification/family-fdr-registration.md"
PHASE2A_DIR = REPO_ROOT / "outputs/retest/phase2a"
GROUND_TRUTH = REPO_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS = REPO_ROOT / "inputs/vectors/bounds/full_evaluation_bounds.geojson"
TEXT_GROUP = ["brief-text", "verbose-text"]
IMAGE_GROUP = ["image-only", "brief-text-image", "verbose-text-image"]
ALL_CONDITIONS = TEXT_GROUP + IMAGE_GROUP
BUFFER_METRES = 20
B_ITERATIONS = 10_000
SEED = 42
FDR_Q = 0.05

#: The six fixed primaries: hypothesis -> (artefact, extractor, registered
#: quoted value, numeric stand-in for the step-up, floor note). H1 is
#: computed live. Extractors re-read each p from source (anti-confabulation:
#: the registration's quoted values are asserted, not trusted).
PERM_FLOOR = 1.0 / 10_001  # (b+1)/(B+1) convention, § 8.3


def _p_h2(root: Path) -> float:
    with open(root / "results/pairwise/20m/group_1_architecture/"
              "pv-vs-consensus-flash-high-text-16-of-30-pv-vs-flash-high-text-26-of-30.json") as f:
        return json.load(f)["permutation_test"]["p_value"]


def _p_h3(root: Path) -> float:
    with open(root / "results/diversity-dividend-384/tiering-champions/tiering_20m.json") as f:
        return json.load(f)["headline_contrasts"][2]["p_value"]


def _p_h4(root: Path) -> float:
    with open(root / "results/retest/pairwise-bootstrap-comparisons.json") as f:
        return json.load(f)["comparisons"][55]["f1_p_value"]


def _p_h5(root: Path) -> float:
    with open(root / "results/retest/pairwise-bootstrap-comparisons.json") as f:
        return json.load(f)["comparisons"][53]["precision_p"]


def _p_h7(root: Path) -> float:
    with open(root / "results/retest/pairwise-bootstrap-comparisons.json") as f:
        return json.load(f)["comparisons"][25]["f1_p_value"]


def _p_h8(root: Path) -> float:
    with open(root / "results/h8-v2/permutation-t4/fdr_summary.json") as f:
        return json.load(f)["contrasts"][3]["bh_adjusted_p"]


FIXED_PRIMARIES: list[dict] = [
    {"hypothesis": "H2", "reader": _p_h2, "registered_value": 0.0,
     "numeric_p": PERM_FLOOR, "report_as": "p < 1e-4 (permutation floor)"},
    {"hypothesis": "H3", "reader": _p_h3, "registered_value": 0.0,
     "numeric_p": PERM_FLOOR, "report_as": "p < 1e-4 (permutation floor)"},
    {"hypothesis": "H4", "reader": _p_h4, "registered_value": 0.124,
     "numeric_p": 0.124, "report_as": "p = 0.124"},
    {"hypothesis": "H5", "reader": _p_h5, "registered_value": 0.756,
     "numeric_p": 0.756, "report_as": "p = 0.756"},
    {"hypothesis": "H7", "reader": _p_h7, "registered_value": 0.001,
     "numeric_p": 0.001, "report_as": "p <= 0.001 (bootstrap floor, B=1000)"},
    {"hypothesis": "H8", "reader": _p_h8, "registered_value": 0.8344,
     "numeric_p": 0.8344, "report_as": "Simes p = 0.8344 (within-H8 BH minimum)"},
]

#: § 8.3 tie rule: presentational rank order for floor ties.
TIE_ORDER = ["H2", "H3", "H7", "H1"]


def f1_from_counts(tp: float, fp: float, fn: float) -> float:
    """F1 from summed TP/FP/FN counts (0.0 on an empty denominator)."""
    denom = 2 * tp + fp + fn
    return (2 * tp / denom) if denom > 0 else 0.0


def build_count_matrices(
    tile_names: list[str],
) -> tuple[dict[str, list], dict[str, np.ndarray]]:
    """
    Load detections and precompute per-run per-tile count matrices.

    Returns:
        (tile_metrics_by_condition, matrices_by_condition) where the
        matrices are float arrays of shape [n_runs, n_tiles, 3] holding
        TP/FP/FN aligned to ``tile_names``, and the tile_metrics are the
        raw ``compute_per_tile_tp_fp_fn`` frames (kept for Gate B).
    """
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    gdf_bounds = gpd.read_file(BOUNDS)
    tm_by_cond: dict[str, list] = {}
    mat_by_cond: dict[str, np.ndarray] = {}

    for cond in ALL_CONDITIONS:
        runs = load_condition_results(PHASE2A_DIR, cond)
        if len(runs) != 3:
            raise SystemExit(f"expected 3 runs for {cond}, found {len(runs)}")
        frames = []
        for _run_n, gdf_det in runs:
            frames.append(compute_per_tile_tp_fp_fn(
                gdf_det, gdf_ref, gdf_bounds, buffer_metres=BUFFER_METRES))
        tm_by_cond[cond] = frames

        mats = np.zeros((len(frames), len(tile_names), 3), dtype=float)
        for ri, tm in enumerate(frames):
            indexed = tm.set_index("tile_name")
            # A tile absent from the frame contributes zero counts.
            common = indexed.index.intersection(tile_names)
            pos = {t: i for i, t in enumerate(tile_names)}
            sub = indexed.loc[common, ["tp", "fp", "fn"]]
            # Collapse duplicate tile rows by summing, mirroring the
            # library's aggregate path.
            sub = sub.groupby(level=0).sum()
            for t, row in sub.iterrows():
                mats[ri, pos[t], 0] = row["tp"]
                mats[ri, pos[t], 1] = row["fp"]
                mats[ri, pos[t], 2] = row["fn"]
        mat_by_cond[cond] = mats
        logger.info("precomputed %s: %d runs x %d tiles", cond, len(frames), len(tile_names))

    return tm_by_cond, mat_by_cond


def condition_mean_f1(mats: np.ndarray, idx: np.ndarray) -> float:
    """Mean across runs of F1 on the (possibly resampled) tile index set."""
    sums = mats[:, idx, :].sum(axis=1)  # [n_runs, 3]
    f1s = [f1_from_counts(tp, fp, fn) for tp, fp, fn in sums]
    return float(np.mean(f1s))


def pooled_delta(mat_by_cond: dict[str, np.ndarray], idx: np.ndarray) -> float:
    """§ 5.1.1 statistic: unweighted group means of condition scores, text - image."""
    text = float(np.mean([condition_mean_f1(mat_by_cond[c], idx) for c in TEXT_GROUP]))
    image = float(np.mean([condition_mean_f1(mat_by_cond[c], idx) for c in IMAGE_GROUP]))
    return text - image


def gate_a(mat_by_cond: dict[str, np.ndarray], tile_names: list[str]) -> None:
    """Reproduce the committed per-condition mean F1s (tolerance 1e-6)."""
    with open(REPO_ROOT / "results/retest/phase2a-evaluation.json") as f:
        committed = json.load(f)["phase2a"]["conditions"]
    full_idx = np.arange(len(tile_names))
    for cond in ALL_CONDITIONS:
        mine = condition_mean_f1(mat_by_cond[cond], full_idx)
        theirs = committed[cond]["f1"]
        if abs(mine - theirs) > 1e-6:
            raise SystemExit(
                f"GATE A FAILED for {cond}: recomputed {mine:.10f} vs committed {theirs:.10f}")
        logger.info("Gate A ok: %s mean F1 %.6f == committed", cond, mine)


def gate_b(
    tm_by_cond: dict[str, list],
    mat_by_cond: dict[str, np.ndarray],
    tile_names: list[str],
) -> None:
    """50-resample equivalence: vectorised path == library aggregate path."""
    rng = np.random.default_rng(123)
    tiles_arr = np.array(tile_names)
    for _ in range(50):
        idx = rng.integers(0, len(tile_names), len(tile_names))
        sample_tiles = tiles_arr[idx]
        for cond in ALL_CONDITIONS:
            lib_f1s = [aggregate_tile_metrics(tm, sample_tiles)[2]
                       for tm in tm_by_cond[cond]]
            lib_mean = float(np.mean(lib_f1s))
            vec_mean = condition_mean_f1(mat_by_cond[cond], idx)
            if abs(lib_mean - vec_mean) > 1e-9:
                raise SystemExit(
                    f"GATE B FAILED for {cond}: lib {lib_mean:.12f} vs vec {vec_mean:.12f}")
    logger.info("Gate B ok: vectorised path == aggregate_tile_metrics on 50 probes")


def bh_step_up(inputs: list[dict], q: float) -> list[dict]:
    """
    Monotone Benjamini–Hochberg step-up with the § 8.3 tie rule.

    Args:
        inputs: dicts with ``hypothesis`` and ``numeric_p``.
        q: FDR level.

    Returns:
        The inputs, sorted by rank, each gaining ``rank``, ``bh_critical``,
        ``adjusted_p``, and ``rejected``.
    """
    m = len(inputs)
    order = sorted(inputs, key=lambda r: (r["numeric_p"], TIE_ORDER.index(r["hypothesis"])
                                          if r["hypothesis"] in TIE_ORDER else 99))
    # Adjusted p: monotone min over j >= k of (m/j) p_(j), clipped at 1.
    adj = [0.0] * m
    running = 1.0
    for j in range(m - 1, -1, -1):
        running = min(running, m * order[j]["numeric_p"] / (j + 1))
        adj[j] = min(running, 1.0)
    # Rejection: largest k with p_(k) <= (k/m) q; reject 1..k.
    k_max = 0
    for j in range(m):
        if order[j]["numeric_p"] <= (j + 1) / m * q:
            k_max = j + 1
    for j, row in enumerate(order):
        row["rank"] = j + 1
        row["bh_critical"] = (j + 1) / m * q
        row["adjusted_p"] = adj[j]
        row["rejected"] = (j + 1) <= k_max
    return order


def main() -> None:
    """Run the registered computation end to end and write the artefacts."""
    at = datetime.now(timezone.utc).isoformat()
    out_dir = REPO_ROOT / "results/family-fdr"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------- Part 1: H1 pooled modality contrast (CMT-0106) ----------
    gdf_bounds = gpd.read_file(BOUNDS)
    tile_names = list(gdf_bounds["tile_name"].unique())
    logger.info("%d evaluation tiles", len(tile_names))

    tm_by_cond, mat_by_cond = build_count_matrices(tile_names)
    gate_a(mat_by_cond, tile_names)
    gate_b(tm_by_cond, mat_by_cond, tile_names)

    full_idx = np.arange(len(tile_names))
    point_delta = pooled_delta(mat_by_cond, full_idx)
    point_groups = {
        "text_only": float(np.mean(
            [condition_mean_f1(mat_by_cond[c], full_idx) for c in TEXT_GROUP])),
        "image_using": float(np.mean(
            [condition_mean_f1(mat_by_cond[c], full_idx) for c in IMAGE_GROUP])),
    }

    rng = np.random.default_rng(SEED)
    deltas = np.empty(B_ITERATIONS)
    for i in range(B_ITERATIONS):
        idx = rng.integers(0, len(tile_names), len(tile_names))
        deltas[i] = pooled_delta(mat_by_cond, idx)
        if (i + 1) % 1000 == 0:
            logger.info("bootstrap %d/%d", i + 1, B_ITERATIONS)

    prop_le = float(np.mean(deltas <= 0))
    prop_gt = float(np.mean(deltas > 0))
    p_h1 = max(2.0 * min(prop_le, prop_gt), 1.0 / B_ITERATIONS)
    ci = (float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5)))
    at_floor = p_h1 <= 2.0 / B_ITERATIONS

    h1 = {
        "_README": (
            "First execution of registered contrast CMT-0106 (H1 pooled modality "
            "effect: text-only conditions vs image-using conditions), under the "
            "reconstruction rule registered BEFORE computation at "
            f"{REGISTRATION} S 5.1.1 (run-it-now policy, PI ruling 2026-07-30)."),
        "generated_at": at,
        "registration": REGISTRATION,
        "conditions": {"text_only": TEXT_GROUP, "image_using": IMAGE_GROUP},
        "corpus": {"tiles": len(tile_names), "bounds": str(BOUNDS.relative_to(REPO_ROOT)),
                   "ground_truth": str(GROUND_TRUTH.relative_to(REPO_ROOT)),
                   "buffer_metres": BUFFER_METRES},
        "method": ("paired tile bootstrap; per condition mean F1 across 3 runs; "
                   "unweighted group means; two-sided p = 2*min tail, floor 1/B"),
        "n_iterations": B_ITERATIONS,
        "seed": SEED,
        "point_estimate": {"group_f1": point_groups, "delta_text_minus_image": point_delta},
        "bootstrap": {"delta_mean": float(np.mean(deltas)),
                      "ci95": {"lower": ci[0], "upper": ci[1]},
                      "prop_le_zero": prop_le, "prop_gt_zero": prop_gt},
        "p_value": p_h1,
        "p_at_floor": at_floor,
        "validation_gates": {
            "gate_a": "per-condition mean F1 == results/retest/phase2a-evaluation.json (1e-6)",
            "gate_b": "vectorised scoring == lib aggregate_tile_metrics on 50 probes (1e-9)",
        },
    }
    with open(out_dir / "h1_cmt0106_pooled_modality.json", "w") as f:
        json.dump(h1, f, indent=1)
    logger.info("H1 pooled contrast: delta=%.4f  p=%.4g  (floor=%s)",
                point_delta, p_h1, at_floor)

    # ---------- Part 2: the seven-hypothesis BH family ----------
    family_inputs = []
    for spec in FIXED_PRIMARIES:
        observed = spec["reader"](REPO_ROOT)
        if abs(observed - spec["registered_value"]) > 1e-12:
            raise SystemExit(
                f"registered value mismatch for {spec['hypothesis']}: artefact "
                f"{observed} vs registration {spec['registered_value']}")
        family_inputs.append({
            "hypothesis": spec["hypothesis"],
            "numeric_p": spec["numeric_p"],
            "report_as": spec["report_as"],
            "source": "registered artefact (re-read and asserted)",
        })
    h1_report = (f"p <= {2.0 / B_ITERATIONS} (bootstrap floor, B={B_ITERATIONS})"
                 if at_floor else f"p = {p_h1:.4g}")
    family_inputs.append({
        "hypothesis": "H1", "numeric_p": p_h1, "report_as": h1_report,
        "source": "computed this run (h1_cmt0106_pooled_modality.json)",
    })

    ranked = bh_step_up(family_inputs, FDR_Q)
    rejected = [r["hypothesis"] for r in ranked if r["rejected"]]

    family = {
        "_README": (
            "The registered family-level Benjamini-Hochberg FDR correction "
            "(preregistration.md S 3.1) over the seven executable confirmatory "
            f"hypotheses, per the pre-execution registration at {REGISTRATION} "
            "(committed before this computation; PI rulings "
            "reports/verification/phase2-rulings-2026-07-30.md S 3)."),
        "generated_at": at,
        "registration": REGISTRATION,
        "q": FDR_Q,
        "family_size": len(ranked),
        "h6": "EXCLUDED - never run (registration S 5.6)",
        "inputs_ranked": ranked,
        "rejected_at_q": rejected,
        "sensitivity": {
            "artefact": "results/pairwise/20m/fdr/pairwise_results_fdr.json",
            "note": ("all-contrasts correction reported alongside per the PI decision; "
                     "26 confirmatory rows, 20 significant; complementary coverage, "
                     "not nested (registration S 8.4)"),
        },
    }
    with open(out_dir / "family_fdr.json", "w") as f:
        json.dump(family, f, indent=1)

    sidecar = {
        "generated_at": at,
        "script": "scripts/compute_family_fdr.py",
        "registration": REGISTRATION,
        "inputs": [
            "outputs/retest/phase2a/ (5 conditions x 3 runs)",
            str(GROUND_TRUTH.relative_to(REPO_ROOT)),
            str(BOUNDS.relative_to(REPO_ROOT)),
            "results/retest/pairwise-bootstrap-comparisons.json",
            "results/pairwise/20m/group_1_architecture/",
            "results/diversity-dividend-384/tiering-champions/tiering_20m.json",
            "results/h8-v2/permutation-t4/fdr_summary.json",
        ],
        "api_cost_usd": 0.0,
    }
    with open(out_dir / "family_fdr.metadata.json", "w") as f:
        json.dump(sidecar, f, indent=1)

    print("\n=== H1 (CMT-0106 pooled modality, first execution) ===")
    print(f"  text-only mean F1  : {point_groups['text_only']:.4f}")
    print(f"  image-using mean F1: {point_groups['image_using']:.4f}")
    print(f"  delta (text-image) : {point_delta:+.4f}  CI95 [{ci[0]:+.4f}, {ci[1]:+.4f}]")
    print(f"  two-sided p        : {h1_report}")
    print("\n=== Family BH-FDR (q=0.05, m=7) ===")
    for r in ranked:
        flag = "REJECTED" if r["rejected"] else "not rejected"
        print(f"  rank {r['rank']}: {r['hypothesis']:3} {r['report_as']:45} "
              f"adj={r['adjusted_p']:.4g}  {flag}")
    print(f"\n  Rejection set: {{{', '.join(rejected)}}}")


if __name__ == "__main__":
    main()
