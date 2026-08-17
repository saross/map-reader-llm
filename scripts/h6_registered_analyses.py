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
    "(M/E, H5, T, O) one at a time on Pro, and the existing Pro data "
    "cleanly vary exactly ONE of them — temperature, via the completed "
    "thinking x temperature 2x2 (S135 blind verification, HIGH-1; the "
    "earlier 'none cleanly' premise is superseded). M/E, H5, and O remain "
    "unvaried, so 'all factors within 0.03 of Flash-optimal' is "
    "unevaluable. Computing a three-way verdict from one factor would "
    "misrepresent the registered criterion; the honest disposition is "
    "not-computable-as-registered."
)


# Operational comparability windows for A-09 (declared, not registered):
# "comparable cost" = within +/-10 %; "comparable F1" = within 0.02.
COST_WINDOW = 0.10
F1_WINDOW = 0.02


def limbs(pro_f1: float, pro_cost: float,
          other_f1: float, other_cost: float) -> dict:
    """Evaluate both registered A-09 limbs with explicit preconditions.

    Registered gate (preregistration.md:691): ">=20% higher F1 at
    comparable cost, OR comparable F1 at <=50% cost". Both limbs are
    computed in code so the artefact and any prose verdict cannot
    diverge (audit H-1); the comparability windows are operational.

    Args:
        pro_f1: Pro operating point's F1.
        pro_cost: Pro operating point's cost (USD).
        other_f1: Comparator operating point's F1.
        other_cost: Comparator operating point's cost (USD).

    Returns:
        Dict with ratios, both comparability flags, and both limbs.
    """
    cost_ratio = round(pro_cost / other_cost, 4)
    cost_comparable = abs(cost_ratio - 1.0) <= COST_WINDOW
    f1_ratio = round(pro_f1 / other_f1, 4)
    limb1 = bool(f1_ratio >= 1.20 and cost_comparable)
    f1_comparable = abs(pro_f1 - other_f1) <= F1_WINDOW
    limb2 = bool(f1_comparable and cost_ratio <= 0.50)
    return {
        "f1_ratio_pro_over_other": f1_ratio,
        "cost_ratio_pro_over_other": cost_ratio,
        "cost_comparable_within_10pct": cost_comparable,
        "f1_comparable_within_0.02": f1_comparable,
        "limb1_fires (>=1.20 F1 at comparable cost)": limb1,
        "limb2_fires (comparable F1 at <=50% cost)": limb2,
    }


def argmax_with_margin(curve: dict[int, float]) -> tuple[int, float]:
    """Best threshold and its margin over the runner-up (audit M-3).

    Args:
        curve: Mapping vote threshold -> F1.

    Returns:
        (best threshold, margin to the second-best F1, 6 dp).
    """
    ordered = sorted(curve.items(), key=lambda kv: kv[1], reverse=True)
    margin = ordered[0][1] - ordered[1][1]
    return ordered[0][0], round(margin, 6)


def gate_model_provenance(passes: list | None = None) -> dict:
    """Assert the model-of-record for both runs (audit BLOCKER-1).

    Args:
        passes: Optional pre-parsed passes list (tests); defaults to
            reading results/passes-manifest.json.

    Returns:
        Gate record with per-run model tallies.

    Raises:
        SystemExit: If any pass's model contradicts the expectation.
    """
    if passes is None:
        manifest = json.loads(PASSES_MANIFEST.read_text())
        passes = manifest["passes"] if "passes" in manifest else manifest
        if isinstance(passes, dict):
            passes = list(passes.values())
    record, failures = {}, []
    expectations = {
        (PRO_RUN, "gemini-3.1-pro-preview"): ALL_CORNERS,
        (FLASH_COMPARATOR_RUN, "gemini-3-flash-preview"): ALL_CORNERS,
        # The pv-diag-384 corners completing the Pro 2x2 (A-06 v2).
        ("pv-diag-384", "gemini-3.1-pro-preview"): (
            "pro-high-text-n5-text-t0.7",
            "pro-high-image-n5-image-t0.7",
            "pro-medium-text-baseline-text-t0.0",
            "pro-medium-image-baseline-image-t0.0",
        ),
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
        summary = {}
        for k in (1, 2, 3):
            out = out_dir / f"consensus_t{k}.geojson"
            stats = merge_passes(pool_dir, out, threshold=k)
            # merge_passes signals failure by return value, and the
            # output path is stable and git-tracked, so a silent no-op
            # would score a stale committed file as fresh (audit H-2).
            if not isinstance(stats, dict) or stats.get("error"):
                sys.exit(f"MATERIALISATION FAIL {pool} k={k}: {stats}")
            if stats.get("total_passes") != 3:
                sys.exit(f"POOL-SIZE GATE FAIL {pool}: total_passes="
                         f"{stats.get('total_passes')}, expected 3 — the "
                         f"k-of-3 labels would be wrong (audit M-1)")
            n_features = len(json.loads(out.read_text()).get("features", []))
            retained = stats.get("retained_clusters")
            if retained is not None and n_features != retained:
                sys.exit(f"MATERIALISATION GATE FAIL {pool} k={k}: file "
                         f"has {n_features} features, merge retained "
                         f"{retained}")
            summary[f"t{k}"] = {kk: vv for kk, vv in stats.items()
                                if not isinstance(vv, (dict, list))}
            built[pool][k] = out
        # Keep the merge statistics beside the outputs, mirroring the
        # E57 pools' voting_summary.json (audit L-9).
        (out_dir / "voting_summary.json").write_text(
            json.dumps(summary, indent=1))
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
            # Store the 6-dp recomputed value so both curves carry the
            # same precision (audit M-4); the gate above still anchors
            # to the committed 4-dp manifest figure.
            flash_curves[pool][k] = ours
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
        pro_k, pro_margin = argmax_with_margin(pro_curves[pool])
        flash_k, flash_margin = argmax_with_margin(flash_curves[pool])
        matched = evaluate_voting_threshold_transfer(
            flash_optimal_n=3, flash_optimal_threshold=flash_k,
            pro_optimal_n=3, pro_optimal_threshold=pro_k)
        a07_results[modality] = {
            "pro_curve_f1_at_20m": pro_curves[pool],
            "flash_curve_f1_at_20m (E57 mis-dispatch pools)":
                flash_curves[pool],
            "pro_optimal_k": pro_k,
            "pro_optimal_margin_over_runner_up": pro_margin,
            "flash_optimal_k": flash_k,
            "flash_optimal_margin_over_runner_up": flash_margin,
            "optimum_fragile (margin < 0.005)": bool(
                pro_margin < 0.005 or flash_margin < 0.005),
            "matched_n3_comparison": asdict(matched),
            "_registration_status_note": (
                "the matched-N form is itself post-hoc (unregistered); "
                "the library's 'Run extended N=30 test' message is "
                "operational wording, not a registered trigger "
                "(audit M-7)"),
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
            "FRAGILITY (image): the Flash comparator image curve is nearly "
            "flat — k=3 beats k=1 by 0.0016 F1; had k=1 won, the relative "
            "difference would read 200% and the image verdict would flip "
            "from 'transfers' to flagged. The image 'transfers' verdict "
            "is not robust to that margin (S135 blind verification, "
            "MEDIUM-3).",
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

    print("Stage 4: A-06 decision rule (2x2 decomposition) ...", flush=True)
    # The full genuine-Pro thinking x temperature 2x2 exists per modality
    # (S135 blind verification, HIGH-1): the two n1-pro-rerun-384 corners
    # plus the two pv-diag-384 Pro baselines complete it on the same
    # Era-2 corpus with identical instruction/library hashes. The
    # registered factor T is therefore cleanly evaluable at matched
    # thinking; thinking level (NOT a registered Phase-2 factor) is the
    # decomposition context; M/E, H5, and O remain unvaried.
    corner_specs = {
        ("high", "0-0"): (PRO_RUN, "baseline-pro-{m}-high-t-0-0"),
        ("medium", "0-7"): (PRO_RUN, "baseline-pro-{m}-medium-t-0-7"),
        ("high", "0-7"): ("pv-diag-384", "baseline-pro-{m}-high-t-0-7"),
        ("medium", "0-0"): ("pv-diag-384", "baseline-pro-{m}-medium-t-0-0"),
    }
    baseline_specs = {
        f"{run}::{cid.format(m=m)}": None
        for (run, cid) in corner_specs.values() for m in ("text", "image")}
    from n1_baseline_leaderboard_tiering import load_baseline_cells
    for raw in load_baseline_cells(
            BASE_DIR / "results" / "run-conditions.json",
            BASE_DIR / "results" / "run-analyses.json"):
        if raw["ref"] in baseline_specs:
            baseline_specs[raw["ref"]] = raw["detections"]
    missing = [k for k, v in baseline_specs.items() if v is None]
    if missing:
        sys.exit(f"A-06 GATE FAIL: 2x2 corner detections not resolvable "
                 f"via the n1 board loader: {missing}")

    def corner(modality: str, think: str, temp: str) -> dict:
        run, cid_t = corner_specs[(think, temp)]
        cid = cid_t.format(m=modality)
        ref = f"{run}::{cid}"
        tp, fp, fn, n_passes = pass_averaged_per_tile(
            Path(baseline_specs[ref]), gdf_ref, gdf_bounds, tile_order)
        return {"ref": ref, "f1": committed_f1(conditions, run, cid),
                "tp": tp, "fp": fp, "fn": fn, "n_passes": n_passes}

    a06_factor_t, a06_thinking_ctx = {}, {}
    for modality in ("text", "image"):
        cells = {(th, tm): corner(modality, th, tm)
                 for th in ("high", "medium") for tm in ("0-0", "0-7")}
        # Registered factor T: alternative T=0.0 vs the carried T=0.7,
        # at matched thinking. Primary at HIGH (the carried production
        # thinking level); replication at MEDIUM.
        t_rows = {}
        for th in ("high", "medium"):
            base, alt = cells[(th, "0-7")], cells[(th, "0-0")]
            boot = paired_bootstrap(
                alt["tp"], alt["fp"], alt["fn"],
                base["tp"], base["fp"], base["fn"],
                n_iterations=B_DELTA_CI, seed=SEED)
            # Estimator reconciliation (audit M-5): the manifest F1s are
            # the eval mean-of-runs vintage; the bootstrap operates on
            # micro-F1 of pass-averaged counts. The registered rule is
            # applied to BOTH deltas and the verdicts must agree.
            delta_manifest = round(alt["f1"] - base["f1"], 6)
            delta_arrays = round(boot["observed_delta"], 6)
            if abs(delta_manifest - delta_arrays) > 0.002:
                sys.exit(f"A-06 ESTIMATOR GATE FAIL ({modality}/{th}): "
                         f"manifest delta {delta_manifest} vs array "
                         f"delta {delta_arrays}")
            fires_manifest = delta_manifest >= 0.03
            fires_arrays = delta_arrays >= 0.03
            if fires_manifest != fires_arrays:
                sys.exit(f"A-06 VERDICT SPLIT ({modality}/{th}): the two "
                         f"estimators disagree on the registered rule — "
                         f"escalate, do not pick one")
            sens = evaluate_factor_sensitivity(
                factor_name=f"T ({modality}, matched {th.upper()} thinking)",
                flash_optimal_level=f"T=0.7 ({base['ref']})",
                baseline_f1=base["f1"],
                alternatives=[{
                    "level": f"T=0.0 ({alt['ref']})",
                    "f1": alt["f1"],
                    # Delta CI (audit HIGH-6): CI of the DIFFERENCE.
                    "ci_lower": boot["ci95"]["lower"],
                    "ci_upper": boot["ci95"]["upper"],
                }])
            t_rows[th] = {
                "t07_f1": base["f1"], "t00_f1": alt["f1"],
                "delta (manifest eval vintage)": delta_manifest,
                "delta (pass-averaged micro vintage)": delta_arrays,
                "registered_rule_fires (delta >= 0.03)": fires_manifest,
                "delta_ci95_paired_bootstrap": boot["ci95"],
                "_ci_semantics": (
                    "CI of the F1 DIFFERENCE (T=0.0 minus T=0.7), not of "
                    "either condition's F1 — including inside "
                    "library_result_with_ci_augmentation.tested_levels, "
                    "whose schema labels it 'ci' (audit M-6)"),
                "delta_bootstrap": boot,
                "library_result_with_ci_augmentation": asdict(sens),
                "n_passes": {"t07": base["n_passes"],
                             "t00": alt["n_passes"]},
            }
        a06_factor_t[modality] = t_rows
        # Thinking decomposition context (NOT a registered Phase-2
        # factor): HIGH - MEDIUM at matched temperature, deltas + CIs.
        th_rows = {}
        for tm in ("0-0", "0-7"):
            hi, md = cells[("high", tm)], cells[("medium", tm)]
            boot = paired_bootstrap(
                hi["tp"], hi["fp"], hi["fn"], md["tp"], md["fp"], md["fn"],
                n_iterations=B_DELTA_CI, seed=SEED)
            th_rows[f"t{tm}"] = {
                "high_f1": hi["f1"], "medium_f1": md["f1"],
                "delta": round(hi["f1"] - md["f1"], 6),
                "reaches_0.03": abs(hi["f1"] - md["f1"]) >= 0.03,
                "delta_ci95_paired_bootstrap": boot["ci95"],
            }
        a06_thinking_ctx[modality] = th_rows

    a06 = {
        "_README": (
            "A-06 (registered: preregistration.md:677 — 'If alternative "
            "outperforms Flash-optimal by >=0.03 F1, flag factor for "
            "adjustment', registered WITHOUT a CI condition). REVISED "
            "after the S135 blind verification (HIGH-1): the full "
            "genuine-Pro thinking x temperature 2x2 exists per modality "
            "(n1-pro-rerun-384 + pv-diag-384 Pro baselines, same Era-2 "
            "corpus, identical instruction/library hashes), so the "
            "registered factor T IS cleanly evaluable at matched "
            "thinking — the earlier confounded-only framing is "
            "superseded. Thinking level is not a registered Phase-2 "
            "factor and is reported as decomposition context. M/E, H5, "
            "and O remain unvaried. The delta CI is the operational "
            "augmentation documented in lib_phase4_transfer.py:22-27, "
            "fed a paired tile-bootstrap CI of the DIFFERENCE (B=1,000, "
            "seed 42), never a per-condition F1 CI. Replicate-count "
            "caveat: the T=0.7 corners average 5-10 passes vs 3 for the "
            "others (same estimator, differing precision)."),
        "generated_at": at,
        "registered_prediction": (
            "H6: 'The Flash-optimal configuration will perform well on "
            "Pro, with at most minor factor adjustments needed' "
            "(preregistration.md, H6 Prediction)."),
        "registered_factor_T": a06_factor_t,
        "thinking_decomposition_context (not a registered factor)":
            a06_thinking_ctx,
        "superseded_confounded_contrast": {
            "note": (
                "The original S135 run reported only the corner contrast "
                "(T=0.0+HIGH vs T=0.7+MEDIUM: text +0.0490, dCI [+0.0267, "
                "+0.0703]; image +0.0708, dCI [+0.0369, +0.1016]) under a "
                "'confound cannot be resolved at $0' premise the blind "
                "verification falsified. Retained for the record "
                "(preserve, do not delete); superseded by "
                "registered_factor_T above.")},
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
        if not vals:
            sys.exit(f"A-09 COST GATE FAIL: no cost_usd rows for "
                     f"{run_id}::{pool} (audit L-5 — never emit NaN)")
        return round(sum(vals) / len(vals), 4)

    def coverage(run_id: str, pool: str) -> dict:
        """Status and tile-coverage summary for a pool (audit M-2)."""
        rows = [p for p in passes if p.get("run_id") == run_id
                and p.get("proposer_pool") == pool]
        return {
            "n_passes": len(rows),
            "statuses": sorted({str(p.get("status")) for p in rows}),
            "n_tiles_processed_range": [
                min(p.get("n_tiles_processed", -1) for p in rows),
                max(p.get("n_tiles_processed", -1) for p in rows)],
        }

    pareto = json.loads(PARETO_V2.read_text())
    rungs = {r["rung"]: r for r in pareto["rungs"]}
    matched_config = {}
    frontier_eval = {}
    any_limb_fires_vs_frontier = False
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
            "limbs_vs_flash_same_config_n3": limbs(
                pro_f1, pro_cost, flash_n3_best, 3 * flash_cost),
            "coverage_disclosure": {
                "pro": coverage(PRO_RUN, pool),
                "flash_comparator": coverage(FLASH_COMPARATOR_RUN, pool),
                "note": (
                    "the Flash comparator passes are status=partial "
                    "(485-486/487 tiles) while all Pro passes are ok at "
                    "487/487 — a one-sided gap that slightly depresses "
                    "Flash F1 and cost (audit M-2); the matched-config "
                    "limb results sit within that uncertainty where "
                    "margins are thin"),
            },
        }
        # The registered gate's yardstick: Flash as actually optimised
        # (the audited Pareto frontier, same corpus and buffer). Pro's
        # candidate points: single pass, and the N=3 union at 3x cost.
        per_rung = {}
        for rung_name in ("min6", "min11"):
            r = rungs[rung_name]
            for label, (pf1, pcost) in {
                "pro_single_pass": (pro_f1, pro_cost),
                "pro_n3_union": (max(pro_curves[pool].values()),
                                 3 * pro_cost),
            }.items():
                res = limbs(pf1, pcost, r["f1"], r["est_cost_usd"])
                per_rung[f"{label}_vs_{rung_name}"] = res
                if (res["limb1_fires (>=1.20 F1 at comparable cost)"]
                        or res["limb2_fires (comparable F1 at <=50% cost)"]):
                    any_limb_fires_vs_frontier = True
        frontier_eval[modality] = per_rung

    a09 = {
        "_README": (
            "A-09 (registered: preregistration.md:691). Cost bases: "
            "audited per-pass cost_usd from results/passes-manifest.json "
            "(per-pass extractor) on both sides of the matched-"
            "configuration comparison; the all-Flash pareto_v2 frontier "
            "(results/verifier-robustness/pareto/, modelled token-load-"
            "audit flex dollars) as the Flash-optimal yardstick. The two "
            "bases are not identically constructed (audit M-8); if the "
            "Pro passes were billed above flex rates the Pro side is "
            "over-costed, which makes the CLOSED verdict conservative. "
            "Comparability windows are operational choices declared in "
            "the limb blocks, not registered."),
        "generated_at": at,
        "registered_gate_verdict": (
            "OPEN" if any_limb_fires_vs_frontier else "CLOSED"),
        "verdict_basis": (
            "the Flash-optimal frontier (min6, min11) — the yardstick "
            "the registered scope limitation implies. The matched-"
            "configuration comparison measures the pure model effect at "
            "Pro's preferred corner (Flash never optimised there) and "
            "does not decide the gate."),
        "matched_configuration_comparison": matched_config,
        "flash_optimal_frontier_evaluation": {
            "source": str(PARETO_V2.relative_to(BASE_DIR)),
            "rungs_used": {n: {"f1": rungs[n]["f1"],
                               "est_cost_usd": rungs[n]["est_cost_usd"]}
                           for n in ("min6", "min11")},
            "per_modality": frontier_eval,
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
