#!/usr/bin/env python3
"""H6's three registered $0 analyses on the existing genuine-Pro data.

S134 walk ruling (Group E): the three registered H6 analysis
components run first, on the Pro data that exists, before the ~US$48
Phase-4 re-run decision. The three components (identifiers per
`reports/d17-inventory/unexecuted-register.md`):

- **A-06** — the Phase 2 decision rule: "If alternative outperforms
  Flash-optimal by >=0.03 F1, flag factor for adjustment"
  (`docs/methodology/preregistration/osf/preregistration.md:677`,
  registered WITHOUT a CI condition).
- **A-07** — the Phase 3 voting-threshold comparison: "Compare Pro
  optimal threshold to Flash optimal threshold; Note any differences
  >10% relative" (`…/preregistration.md:679-683`).
- **A-09** — the scope-limitation gate: "Full per-model optimisation
  only if Pro demonstrates substantially superior cost-effectiveness
  (>=20% higher F1 at comparable cost, OR comparable F1 at <=50%
  cost)" (`…/preregistration.md:691`).

**A-08** (the three-way transfer verdict, `…/preregistration.md:
693-699`) is NOT computed: the existing Pro data vary none of the
four registered Phase-2 factors cleanly, so "all factors within
0.03" is unevaluable — stated explicitly per block-plan hardening 7.

Data provenance (S135 audit BLOCKER-1): genuine Pro =
`outputs/h11/n1-pro-rerun-384` (`gemini-3.1-pro-preview`, 4 corners
x 3 runs); the `n1-outstanding-384` "pro-*" pools are the E57
mis-dispatch (billed and dispatched as `gemini-3-flash-preview`) and
serve here as the **matched-N, matched-configuration Flash
comparator** (preserve-and-compare). A model-provenance gate asserts
both facts from `results/passes-manifest.json` before anything runs.

Stages:
  0. Model-provenance gate (halts on any mismatch).
  1. Materialise genuine-Pro N=3 consensus (k = 1, 2, 3) for the two
     high-t0.0 corners via `merge_passes` (mirrors the E57 pools'
     `consensus/consensus_tK.geojson` layout).
  2. Evaluate all consensus sets at F1@20 m (Hungarian per map, the
     canonical `compute_per_tile_tp_fp_fn`); comparator gate
     re-derives the six E57-pool consensus F1s from disk against the
     conditions manifest (4 dp).
  3. A-07 matched-N comparison (registered form declared
     not-computable-as-registered across N=3 vs N=30 pools).
  4. A-06 registered rule on the only available contrast (the
     temperature-and-thinking corner pair, per modality; E40-class
     confound disclosed), with a paired tile-bootstrap **delta** CI
     as the operational augmentation (never the per-condition F1 CI).
  5. A-09 cost gate on audited per-pass `cost_usd` (both sides), with
     the all-Flash `pareto_v2.json` frontier as the Flash-optimal
     yardstick.

Usage (run on sapphire; a few minutes)::

    .venv/bin/python scripts/h6_registered_analyses.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from e45_bootstrap_pairings import micro_f1, paired_bootstrap  # noqa: E402
from lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from lib_phase4_transfer import (  # noqa: E402
    evaluate_factor_sensitivity,
    evaluate_voting_threshold_transfer,
)
from merge_passes import merge_passes  # noqa: E402
from n1_baseline_leaderboard_tiering import (  # noqa: E402
    TARGET_CRS,
    pass_averaged_per_tile,
)
from pairwise_permutation_test import assign_source_tiles  # noqa: E402

PRO_RUN = "n1-pro-rerun-384"
FLASH_COMPARATOR_RUN = "n1-outstanding-384"
PRO_DIR = BASE_DIR / "outputs/h11/n1-pro-rerun-384"
FLASH_DIR = BASE_DIR / "outputs/h11/n1-outstanding-384"
OUT_DIR = BASE_DIR / "results/h6-registered-analyses"
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
GROUND_TRUTH = BASE_DIR / "inputs/vectors/references/mounds-reference.geojson"
PASSES_MANIFEST = BASE_DIR / "results/passes-manifest.json"
CONDITIONS_MANIFEST = BASE_DIR / "results/conditions-manifest.json"
PARETO_V2 = BASE_DIR / "results/verifier-robustness/pareto/pareto_v2.json"

BUFFER_M = 20
SEED = 42
B_DELTA_CI = 1_000  # registered bootstrap convention (Decision 10)
COMPARATOR_GATE_TOL = 5e-5  # manifest F1s stored at 4 dp
HIGH_CORNERS = ("pro-text-high-t0", "pro-image-high-t0")
ALL_CORNERS = ("pro-text-high-t0", "pro-text-medium-t07",
               "pro-image-high-t0", "pro-image-medium-t07")

A08_STATEMENT = (
    "A-08 (the registered three-way transfer verdict, preregistration.md:"
    "693-699) is not computed: the registered Phase 2 varies four factors "
    "(M/E, H5, T, O) one at a time on Pro, and the existing Pro data vary "
    "none of them cleanly — the only available contrast moves temperature "
    "and thinking level together (E40-class confound), so 'all factors "
    "within 0.03 of Flash-optimal' is unevaluable. Computing a verdict "
    "from one confounded factor would misrepresent the registered "
    "criterion; the honest disposition is not-computable-as-registered."
)


def gate_model_provenance() -> dict:
    """Assert the model-of-record for both runs (audit BLOCKER-1).

    Returns:
        Gate record with per-run model tallies.

    Raises:
        SystemExit: If any pass's model contradicts the expectation.
    """
    manifest = json.loads(PASSES_MANIFEST.read_text())
    passes = manifest["passes"] if "passes" in manifest else manifest
    if isinstance(passes, dict):
        passes = list(passes.values())
    record, failures = {}, []
    expectations = {
        (PRO_RUN, "gemini-3.1-pro-preview"): ALL_CORNERS,
        (FLASH_COMPARATOR_RUN, "gemini-3-flash-preview"): ALL_CORNERS,
    }
    for (run_id, expected_model), pools in expectations.items():
        for pool in pools:
            models = sorted({
                p.get("model_used") for p in passes
                if p.get("run_id") == run_id
                and p.get("proposer_pool") == pool})
            record[f"{run_id}::{pool}"] = models
            if models and models != [expected_model]:
                failures.append(
                    f"{run_id}::{pool}: model_used {models}, "
                    f"expected [{expected_model}]")
            if not models:
                failures.append(f"{run_id}::{pool}: no passes found")
    if failures:
        sys.exit("MODEL-PROVENANCE GATE FAIL (halting; audit BLOCKER-1):\n  "
                 + "\n  ".join(failures))
    print(f"  model-provenance gate: {len(record)} pools verified", flush=True)
    return record


def materialise_pro_consensus() -> dict[str, dict[int, Path]]:
    """Build genuine-Pro N=3 consensus sets for the high-t0.0 corners.

    Returns:
        Mapping pool -> {k: consensus geojson path}.
    """
    built: dict[str, dict[int, Path]] = {}
    for pool in HIGH_CORNERS:
        pool_dir = PRO_DIR / pool
        out_dir = pool_dir / "consensus"
        out_dir.mkdir(exist_ok=True)
        built[pool] = {}
        for k in (1, 2, 3):
            out = out_dir / f"consensus_t{k}.geojson"
            merge_passes(pool_dir, out, threshold=k)
            built[pool][k] = out
    return built


def f1_at_20m(geojson: Path, gdf_ref: gpd.GeoDataFrame,
              gdf_bounds: gpd.GeoDataFrame) -> float:
    """Micro-F1 @ 20 m for one detection set via the canonical scorer.

    Args:
        geojson: Detection GeoJSON path.
        gdf_ref: Ground truth (TARGET_CRS).
        gdf_bounds: Tile bounds (TARGET_CRS).

    Returns:
        Micro-averaged F1 at the 20 m buffer.
    """
    gdf = gpd.read_file(geojson)
    if len(gdf) == 0:
        return 0.0
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    gdf = gdf.to_crs(TARGET_CRS)
    gdf = assign_source_tiles(gdf, gdf_bounds)
    tile_metrics = compute_per_tile_tp_fp_fn(
        gdf, gdf_ref, gdf_bounds, buffer_metres=BUFFER_M)
    return micro_f1(float(tile_metrics["tp"].sum()),
                    float(tile_metrics["fp"].sum()),
                    float(tile_metrics["fn"].sum()))


def committed_f1(conditions: list[dict], run_id: str, cid_contains: str) -> float:
    """Fetch a committed F1@20 from the conditions manifest.

    Args:
        conditions: Parsed conditions list.
        run_id: Run identifier.
        cid_contains: Substring identifying the condition.

    Returns:
        The manifest's per_buffer["20"].f1.
    """
    for c in conditions:
        if (c.get("run_id") == run_id
                and cid_contains in c.get("condition_id", "")):
            return float(c["metrics"]["per_buffer"]["20"]["f1"])
    raise KeyError(f"{run_id} / *{cid_contains}* not in conditions manifest")


def main() -> int:
    """Run stages 0-5 and write the three analysis artefacts."""
    at = datetime.now(timezone.utc).isoformat()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Stage 0: model-provenance gate ...", flush=True)
    provenance_gate = gate_model_provenance()

    print("Stage 1: materialising genuine-Pro N=3 consensus ...", flush=True)
    built = materialise_pro_consensus()

    print("Stage 2: evaluating consensus sets at F1@20 m ...", flush=True)
    gdf_ref = gpd.read_file(GROUND_TRUTH).to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file(BOUNDS).to_crs(TARGET_CRS)
    tile_order = list(gdf_bounds["tile_name"].unique())

    pro_curves: dict[str, dict[int, float]] = {}
    for pool, paths in built.items():
        pro_curves[pool] = {
            k: round(f1_at_20m(p, gdf_ref, gdf_bounds), 6)
            for k, p in paths.items()}
        print(f"  {pool}: " + ", ".join(
            f"k={k} F1={v:.4f}" for k, v in pro_curves[pool].items()),
            flush=True)

    conditions_doc = json.loads(CONDITIONS_MANIFEST.read_text())
    conditions = conditions_doc.get("conditions", conditions_doc)
    if isinstance(conditions, dict):
        conditions = list(conditions.values())

    # Comparator gate: re-derive the six E57-pool consensus F1s from disk.
    flash_curves: dict[str, dict[int, float]] = {}
    comparator_gate, failures = {}, []
    for pool in HIGH_CORNERS:
        flash_curves[pool] = {}
        for k in (1, 2, 3):
            path = FLASH_DIR / pool / "consensus" / f"consensus_t{k}.geojson"
            ours = round(f1_at_20m(path, gdf_ref, gdf_bounds), 6)
            theirs = committed_f1(
                conditions, FLASH_COMPARATOR_RUN, f"{pool}-consensus-{k}of3")
            ok = abs(ours - theirs) <= COMPARATOR_GATE_TOL
            comparator_gate[f"{pool}-k{k}"] = {
                "recomputed": ours, "committed": theirs, "pass": ok}
            flash_curves[pool][k] = theirs
            if not ok:
                failures.append(f"{pool} k={k}: {ours} vs {theirs}")
    if failures:
        sys.exit("COMPARATOR GATE FAIL (halting):\n  " + "\n  ".join(failures))
    print(f"  comparator gate: {len(comparator_gate)}/6 reproduced "
          f"(tol {COMPARATOR_GATE_TOL})", flush=True)

    print("Stage 3: A-07 voting-threshold comparison ...", flush=True)
    a07_results = {}
    for pool in HIGH_CORNERS:
        modality = "text" if "text" in pool else "image"
        pro_k = max(pro_curves[pool], key=pro_curves[pool].get)
        flash_k = max(flash_curves[pool], key=flash_curves[pool].get)
        matched = evaluate_voting_threshold_transfer(
            flash_optimal_n=3, flash_optimal_threshold=flash_k,
            pro_optimal_n=3, pro_optimal_threshold=pro_k)
        a07_results[modality] = {
            "pro_curve_f1_at_20m": pro_curves[pool],
            "flash_curve_f1_at_20m (E57 mis-dispatch pools)":
                flash_curves[pool],
            "pro_optimal_k": pro_k,
            "flash_optimal_k": flash_k,
            "matched_n3_comparison": asdict(matched),
        }
    a07 = {
        "_README": (
            "A-07 (registered: preregistration.md:679-683) computed in the "
            "only commensurable form the data support: matched-N (N=3) "
            "Pro-vs-Flash voting curves at matched configuration and "
            "corpus. The REGISTERED form — Pro optimal threshold vs the "
            "Flash production optimum (26-of-30, an N=30 pool) — is "
            "NOT-COMPUTABLE-AS-REGISTERED: a raw vote-count comparison "
            "across N=3 and N=30 pools is data-independent (any k in 1..3 "
            "differs from 26 by >88% relative), so the >10%-relative rule "
            "presupposes matched N. Fraction-form (k/N) reported "
            "descriptively below, carrying no registered verdict."),
        "generated_at": at,
        "scope_caveats": [
            "384 px / 487 tiles (Era 2), not the registered Phase-4 scope",
            "Pro pools exist only at N=3 (three runs per corner)",
            "Flash comparator = the E57 mis-dispatch pools (Flash executing "
            "the Pro-corner configuration) — matched config, matched N",
            "the registered >20% extended-test trigger cannot fire an N=30 "
            "Pro run inside this $0 block",
        ],
        "results": a07_results,
        "fraction_form_descriptive": {
            "flash_production_optimum": "26-of-30 (0.867)",
            "pro_text_optimal_fraction":
                str(a07_results["text"]["pro_optimal_k"]) + "-of-3",
        },
        "model_provenance_gate": provenance_gate,
        "comparator_gate": comparator_gate,
    }

    print("Stage 4: A-06 decision rule ...", flush=True)
    a06_contrasts = {}
    for modality in ("text", "image"):
        carried = f"pro-{modality}-medium-t07"   # Flash carry-forward T=0.7
        alt = f"pro-{modality}-high-t0"          # the alternative corner
        f1_carried = committed_f1(
            conditions, PRO_RUN,
            f"baseline-pro-{modality}-medium-t-0-7")
        f1_alt = committed_f1(
            conditions, PRO_RUN, f"baseline-pro-{modality}-high-t-0-0")
        # Paired delta CI from pass-averaged per-tile arrays (the
        # operational augmentation; the registered rule is delta alone).
        tp_c, fp_c, fn_c, n_c = pass_averaged_per_tile(
            (PRO_DIR / carried).relative_to(BASE_DIR), gdf_ref, gdf_bounds,
            tile_order)
        tp_a, fp_a, fn_a, n_a = pass_averaged_per_tile(
            (PRO_DIR / alt).relative_to(BASE_DIR), gdf_ref, gdf_bounds,
            tile_order)
        boot = paired_bootstrap(tp_a, fp_a, fn_a, tp_c, fp_c, fn_c,
                                n_iterations=B_DELTA_CI, seed=SEED)
        sens = evaluate_factor_sensitivity(
            factor_name=(
                f"temperature+thinking ({modality}; E40-class confound)"),
            flash_optimal_level=f"{carried} (carried T=0.7, MEDIUM)",
            baseline_f1=f1_carried,
            alternatives=[{
                "level": f"{alt} (T=0.0, HIGH)",
                "f1": f1_alt,
                # Delta CI bounds (audit HIGH-6): the CI of the F1
                # DIFFERENCE, not the per-condition F1 CI.
                "ci_lower": boot["ci95"]["lower"],
                "ci_upper": boot["ci95"]["upper"],
            }])
        a06_contrasts[modality] = {
            "carried_level_f1": f1_carried,
            "alternative_level_f1": f1_alt,
            "delta": round(f1_alt - f1_carried, 6),
            "registered_rule_fires (delta >= 0.03)":
                (f1_alt - f1_carried) >= 0.03,
            "delta_ci95_paired_bootstrap": boot["ci95"],
            "delta_bootstrap": boot,
            "library_result_with_ci_augmentation": asdict(sens),
            "n_passes": {"carried": n_c, "alternative": n_a},
        }
    a06 = {
        "_README": (
            "A-06 (registered: preregistration.md:677 — 'If alternative "
            "outperforms Flash-optimal by >=0.03 F1, flag factor for "
            "adjustment', registered WITHOUT a CI condition). None of the "
            "four registered Phase-2 factors (M/E, H5, T, O) is cleanly "
            "evaluable from existing Pro data: the only available contrast "
            "moves temperature AND thinking level together (the corners "
            "design; E40-class confound). The registered rule's arithmetic "
            "is reported on that confounded contrast, per modality, with "
            "the confound named. The delta CI is the operational "
            "augmentation documented in lib_phase4_transfer.py:22-27 and "
            "is fed a real paired tile-bootstrap CI of the DIFFERENCE "
            "(B=1,000, seed 42), never a per-condition F1 CI."),
        "generated_at": at,
        "registered_prediction": (
            "H6: 'The Flash-optimal configuration will perform well on "
            "Pro, with at most minor factor adjustments needed' "
            "(preregistration.md, H6 Prediction)."),
        "contrasts": a06_contrasts,
        "a08_statement": A08_STATEMENT,
    }

    print("Stage 5: A-09 cost-effectiveness gate ...", flush=True)
    passes_doc = json.loads(PASSES_MANIFEST.read_text())
    passes = passes_doc["passes"] if "passes" in passes_doc else passes_doc
    if isinstance(passes, dict):
        passes = list(passes.values())

    def mean_cost(run_id: str, pool: str) -> float:
        vals = [p["cost_usd"] for p in passes
                if p.get("run_id") == run_id
                and p.get("proposer_pool") == pool
                and isinstance(p.get("cost_usd"), (int, float))]
        return round(sum(vals) / len(vals), 4) if vals else float("nan")

    pareto = json.loads(PARETO_V2.read_text()) if PARETO_V2.exists() else None
    matched_config = {}
    for pool in HIGH_CORNERS:
        modality = "text" if "text" in pool else "image"
        pro_cost = mean_cost(PRO_RUN, pool)
        flash_cost = mean_cost(FLASH_COMPARATOR_RUN, pool)
        pro_f1 = committed_f1(
            conditions, PRO_RUN,
            f"baseline-pro-{modality}-high-t-0-0")
        flash_single_f1 = committed_f1(
            conditions, FLASH_COMPARATOR_RUN,
            f"baseline-pro-{modality}-high-t-0-0")
        flash_n3_best = max(flash_curves[pool].values())
        matched_config[modality] = {
            "pro_single_pass": {"f1_at_20m": pro_f1, "cost_per_pass_usd":
                                pro_cost},
            "flash_same_config_single_pass": {
                "f1_at_20m": flash_single_f1,
                "cost_per_pass_usd": flash_cost},
            "flash_same_config_n3_consensus_best": {
                "f1_at_20m": flash_n3_best,
                "cost_usd": round(3 * flash_cost, 4)},
            "limb1_matched_config": {
                "comparison": ("Pro 1 pass vs Flash-same-config 3-pass "
                               "consensus (costs within ~5%)"),
                "f1_ratio": round(pro_f1 / flash_n3_best, 4),
                "fires (>=1.20 at comparable cost)":
                    bool(pro_f1 / flash_n3_best >= 1.20),
            },
        }
    a09 = {
        "_README": (
            "A-09 (registered: preregistration.md:691). Cost basis per the "
            "S135 audit (HIGH-7): audited per-pass cost_usd from "
            "results/passes-manifest.json on BOTH sides for the "
            "matched-configuration comparison; the all-Flash audited "
            "pareto_v2 frontier (results/verifier-robustness/pareto/, "
            "flex-tier audited dollars, same corpus and buffer) is the "
            "Flash-OPTIMAL yardstick the registered gate implies. "
            "Comparability windows are operational choices, stated "
            "inline, not registered."),
        "generated_at": at,
        "matched_configuration_comparison": matched_config,
        "flash_optimal_frontier": {
            "source": str(PARETO_V2.relative_to(BASE_DIR)),
            "note": ("verdict against the frontier computed in the "
                     "findings doc from the pareto artefact's efficient "
                     "set; the artefact is committed and cited rather "
                     "than re-derived here"),
            "efficient_set_present": bool(pareto),
        },
        "a08_statement": A08_STATEMENT,
    }

    for name, doc in (("a06_decision_rule", a06),
                      ("a07_voting_thresholds", a07),
                      ("a09_cost_gate", a09)):
        path = OUT_DIR / f"{name}.json"
        path.write_text(json.dumps(doc, indent=1))
        print(f"Wrote {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
