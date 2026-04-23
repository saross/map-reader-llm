#!/usr/bin/env python3
"""
Collect all factor analysis p-values and apply FDR within families.

Merges results from:
1. New factor-analysis comparisons (14 tests at 384px + 2 at 512px)
2. Reused hypothesis-driven comparisons (from 20m pairwise results)
3. Ad-hoc modality comparisons (Pro text vs image, baseline PV)
4. Prompt engineering comparisons (28 from 512px)

Applies Benjamini-Hochberg FDR correction within each of 5 families:
architecture, thinking, temperature, modality, prompt_engineering.

Outputs consolidated tables for the paper.

Run:
    python scripts/collect-factor-analysis.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

import numpy as np
from scipy.stats import false_discovery_control

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

PROJECT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT / "results" / "factor-analysis"


def _extract_raw_p(comp: dict) -> float:
    """Return the raw p-value from a comparison dict, tolerating schema drift.

    Input JSONs from different upstream pairwise-test scripts use different
    key names: the 384 px factor-analysis manifest and the prompt-engineering
    batch use ``p_value``; the 20 m pairwise FDR file uses ``p_value_raw``.
    Prefer ``p_value_raw`` (the post-FDR canonical name we normalise to)
    and fall back to ``p_value``; raise if neither is present so a schema
    change fails loudly rather than silently defaulting to 1.0.
    """
    if "p_value_raw" in comp:
        return comp["p_value_raw"]
    if "p_value" in comp:
        return comp["p_value"]
    raise KeyError(
        f"Neither 'p_value_raw' nor 'p_value' present in comparison: "
        f"{sorted(comp.keys())}"
    )


def load_new_results() -> list[dict]:
    """Load new factor-analysis comparison results."""
    results = []

    # 384px batch results
    manifest_path = (
        PROJECT / "results" / "pairwise" / "factor-analysis-20m"
        / "run_manifest.json"
    )
    if manifest_path.exists():
        with open(manifest_path) as f:
            data = json.load(f)
        for comp in data["comparisons"]:
            results.append({
                "family": comp.get("family", "unknown"),
                "group": comp.get("group", 0),
                "question": comp.get("question", ""),
                "label_a": comp["label_a"],
                "label_b": comp["label_b"],
                "f1_a": comp["f1_a"],
                "f1_b": comp["f1_b"],
                "delta_f1": comp["delta_f1"],
                "p_value_raw": _extract_raw_p(comp),
                "precision_a": comp.get("precision_a"),
                "precision_b": comp.get("precision_b"),
                "recall_a": comp.get("recall_a"),
                "recall_b": comp.get("recall_b"),
                "n_detections_a": comp.get("n_detections_a"),
                "n_detections_b": comp.get("n_detections_b"),
                "n_tiles": comp.get("n_tiles"),
                "source": "factor-analysis-384px",
            })
        log.info("Loaded %d results from 384px batch", len(results))

    # Phase 2b retest N=1 temperature results
    #
    # Schema note (2026-04-24): these pairwise_permutation_result.json files
    # use `condition_a`/`condition_b` as the top-level per-condition blocks,
    # not `global_a`/`global_b`. The original implementation of this block
    # only read `global_a`/`global_b`, silently zeroing labels and per-
    # condition metrics for these two rows (discovered and corrected
    # Session 75). Prefer `condition_a`/`condition_b`; fall back to
    # `global_a`/`global_b` for forward compatibility with any future
    # pairwise output that uses the older key names.
    #
    # Scope note: the subdirs are named `temp-512px-*` for historical
    # reasons but the data underneath resolves to
    # `outputs/retest/phase2b/track{1-image,2-text}/T*/run_1/`, i.e.
    # Phase 2b retest at 384 px N=1 (per protocol-errata E41 production
    # lock-in). The output labels reflect the actual source.
    for subdir, track_label in [
        ("temp-512px-text", "Phase 2b text"),
        ("temp-512px-image", "Phase 2b image"),
    ]:
        result_path = (
            PROJECT / "results" / "pairwise" / "factor-analysis-20m"
            / subdir / "pairwise_permutation_result.json"
        )
        if not result_path.exists():
            log.warning("Missing factor-analysis pairwise file: %s", result_path)
            continue
        with open(result_path) as f:
            data = json.load(f)

        # Prefer `condition_a`/`condition_b` (the current pairwise script
        # schema); fall back to `global_a`/`global_b` only when the
        # preferred key is absent. Using `key in data` guards against the
        # `or`-chain edge case where a present-but-empty dict would
        # incorrectly fall through to the legacy key name.
        ca = (
            data["condition_a"] if "condition_a" in data
            else data.get("global_a", {})
        )
        cb = (
            data["condition_b"] if "condition_b" in data
            else data.get("global_b", {})
        )
        pt = data.get("permutation_test", {})

        if not ca or not cb:
            log.warning(
                "Factor-analysis row %s has empty condition blocks; labels and "
                "per-condition metrics will be missing in the aggregated output",
                subdir,
            )

        results.append({
            "family": "temperature",
            "group": 12,
            "question": f"T=0.7 vs T=1.0 (N=1, {track_label})",
            "label_a": ca.get("label", ""),
            "label_b": cb.get("label", ""),
            "f1_a": ca.get("f1", 0),
            "f1_b": cb.get("f1", 0),
            "delta_f1": pt.get("observed_f1_diff", 0),
            "p_value_raw": pt.get("p_value", 1.0),
            "precision_a": ca.get("precision"),
            "precision_b": cb.get("precision"),
            "recall_a": ca.get("recall"),
            "recall_b": cb.get("recall"),
            "n_detections_a": ca.get("n_detections"),
            "n_detections_b": cb.get("n_detections"),
            "n_tiles": pt.get("n_tiles"),
            "source": "factor-analysis-phase2b-retest-n1",
        })
        log.info("Loaded factor-analysis row from %s", subdir)

    return results


def load_reused_results() -> list[dict]:
    """Load reused results from hypothesis-driven pairwise tests."""
    results = []

    # Map original question labels to factor families
    group_family_map = {
        # Group 1: PV vs consensus → architecture family
        "PV vs consensus": "architecture",
        "PV vs consensus (image)": "architecture",
        "PV vs consensus (Pro)": "architecture",
        "PV verifier thinking": "architecture",
        "PV on single-pass text": "architecture",
        "PV on single-pass image": "architecture",
        # Group 2: text vs image → modality family
        "Text vs image": "modality",
        "Text vs image (N=10)": "modality",
        "Text vs image (MINIMAL)": "modality",
        "Text vs image (PV)": "modality",
        # Group 3: HIGH vs MINIMAL → thinking family
        "HIGH vs MINIMAL (text N=5)": "thinking",
        "HIGH vs MINIMAL (text N=10)": "thinking",
        "HIGH vs MINIMAL (text N=30)": "thinking",
        "HIGH vs MINIMAL (image N=5)": "thinking",
        # Group 4: temperature → temperature family
        "T=0.7 vs T=1.0 (N=5)": "temperature",
        "T=0.7 vs T=1.0 (N=10)": "temperature",
        "T=0.7 vs T=1.0 (N=30)": "temperature",
    }

    # Load from the original 20m pairwise FDR results
    fdr_path = (
        PROJECT / "results" / "pairwise" / "20m" / "fdr"
        / "pairwise_results_fdr.json"
    )
    if not fdr_path.exists():
        log.error(
            "Required reused-hypothesis FDR file is missing: %s "
            "(run the 20 m pairwise FDR pipeline before re-running this aggregator)",
            fdr_path,
        )
        return results

    with open(fdr_path) as f:
        data = json.load(f)

    for comp in data["comparisons"]:
        question = comp.get("question", "")
        family = group_family_map.get(question)
        if family:
            results.append({
                "family": family,
                "group": comp.get("group", 0),
                "question": question,
                "label_a": comp["label_a"],
                "label_b": comp["label_b"],
                "f1_a": comp["f1_a"],
                "f1_b": comp["f1_b"],
                "delta_f1": comp["delta_f1"],
                "p_value_raw": _extract_raw_p(comp),
                "precision_a": comp.get("precision_a"),
                "precision_b": comp.get("precision_b"),
                "recall_a": comp.get("recall_a"),
                "recall_b": comp.get("recall_b"),
                "n_detections_a": comp.get("n_detections_a"),
                "n_detections_b": comp.get("n_detections_b"),
                "n_tiles": comp.get("n_tiles"),
                "source": "reused-hypothesis-20m",
            })

    log.info("Loaded %d reused results", len(results))
    return results


def load_prompt_engineering_results() -> list[dict]:
    """Load prompt engineering results (512px)."""
    results = []
    pe_path = (
        PROJECT / "results" / "pairwise" / "prompt-engineering-20m"
        / "prompt_engineering_pairwise.json"
    )
    if not pe_path.exists():
        log.error(
            "Required prompt-engineering pairwise file is missing: %s "
            "(run the prompt-engineering pairwise pipeline before re-running this aggregator)",
            pe_path,
        )
        return results

    with open(pe_path) as f:
        data = json.load(f)

    for comp in data["comparisons"]:
        group_name = comp.get("group", "")
        # Only include library, treatment, ordering — not modality or temp
        if group_name in [
            "Library composition (text)",
            "Library composition (image)",
            "Text treatment (text)",
            "Text treatment (image)",
            "Example ordering",
        ]:
            results.append({
                "family": "prompt_engineering",
                "group": 14,
                "question": group_name,
                "label_a": comp["label_a"],
                "label_b": comp["label_b"],
                "f1_a": comp["f1_a"],
                "f1_b": comp["f1_b"],
                "delta_f1": comp["delta_f1"],
                "p_value_raw": _extract_raw_p(comp),
                "n_tiles": comp.get("n_tiles"),
                "source": "prompt-engineering-512px",
            })

    log.info(
        "Loaded %d prompt engineering results",
        len(results),
    )
    return results


def apply_fdr(results: list[dict]) -> list[dict]:
    """Apply BH FDR correction within each family."""
    families = {}
    for r in results:
        fam = r["family"]
        if fam not in families:
            families[fam] = []
        families[fam].append(r)

    all_corrected = []
    for fam_name, fam_results in sorted(families.items()):
        # Defensive: a row missing `p_value_raw` would silently crash BH
        # correction downstream. Drop any such row with an explicit
        # warning so the input pipeline surfaces the issue.
        valid_rows = [r for r in fam_results if r.get("p_value_raw") is not None]
        n_dropped = len(fam_results) - len(valid_rows)
        if n_dropped:
            log.warning(
                "Family '%s': dropped %d row(s) with missing p_value_raw "
                "before BH-FDR correction",
                fam_name,
                n_dropped,
            )
        fam_results = valid_rows
        if not fam_results:
            continue

        p_values = np.array([r["p_value_raw"] for r in fam_results])
        # BH correction
        adjusted = false_discovery_control(p_values, method="bh")

        n_sig = sum(1 for p in adjusted if p < 0.05)
        log.info(
            "Family '%s': %d comparisons, %d/%d significant",
            fam_name,
            len(fam_results),
            n_sig,
            len(fam_results),
        )

        for r, adj_p in zip(fam_results, adjusted):
            r["p_value_adj"] = round(float(adj_p), 4)
            if adj_p < 0.001:
                r["significant"] = "***"
            elif adj_p < 0.01:
                r["significant"] = "**"
            elif adj_p < 0.05:
                r["significant"] = "*"
            else:
                r["significant"] = "ns"
            all_corrected.append(r)

    return all_corrected


def write_outputs(results: list[dict]) -> None:
    """Write consolidated outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # JSON
    with open(OUTPUT_DIR / "factor_analysis_results.json", "w") as f:
        json.dump({"comparisons": results}, f, indent=2)

    # CSV — deliberate column list for paper-table readers. Kept in
    # lockstep with the result-dict schema written by the three loaders
    # above; any new per-condition metric added to the dict should also
    # be added here so CSV and JSON stay at parity.
    fieldnames = [
        "family",
        "question",
        "label_a",
        "label_b",
        "f1_a",
        "f1_b",
        "delta_f1",
        "p_value_raw",
        "p_value_adj",
        "significant",
        "source",
        "precision_a",
        "precision_b",
        "recall_a",
        "recall_b",
        "n_detections_a",
        "n_detections_b",
        "n_tiles",
    ]
    with open(OUTPUT_DIR / "factor_analysis_results.csv", "w",
              newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(results)

    # Per-family Markdown tables
    families = {}
    for r in results:
        fam = r["family"]
        if fam not in families:
            families[fam] = []
        families[fam].append(r)

    md_lines = [
        "# Factor Analysis: Pairwise Permutation Test Results",
        "",
        "FDR-corrected (Benjamini-Hochberg, q=0.05) within each "
        "factor family.",
        "Buffer: 20m | Permutations: 10,000 | Seed: 42",
        "",
    ]

    for fam_name in [
        "architecture",
        "thinking",
        "temperature",
        "modality",
        "prompt_engineering",
    ]:
        fam_results = families.get(fam_name, [])
        n_sig = sum(1 for r in fam_results if r["significant"] != "ns")
        md_lines.append(
            f"## {fam_name.replace('_', ' ').title()} "
            f"({n_sig}/{len(fam_results)} significant)",
        )
        md_lines.append("")
        md_lines.append(
            "| Question | Condition A | Condition B | F1_A | F1_B "
            "| ΔF1 | p (raw) | p (adj) | Sig |",
        )
        md_lines.append("|---|---|---|---|---|---|---|---|---|")

        for r in sorted(
            fam_results,
            key=lambda x: abs(x["delta_f1"]),
            reverse=True,
        ):
            md_lines.append(
                f"| {r['question']} "
                f"| {r['label_a'][:35]} "
                f"| {r['label_b'][:35]} "
                f"| {r['f1_a']:.3f} "
                f"| {r['f1_b']:.3f} "
                f"| {r['delta_f1']:+.3f} "
                f"| {r['p_value_raw']:.4f} "
                f"| {r['p_value_adj']:.4f} "
                f"| {r['significant']} |",
            )
        md_lines.append("")

    # Auto-generated tables-only MD for script-driven consumers. The
    # hand-authored narrative level-up lives at `factor_analysis_results.md`
    # (the paper-citation target) and must NOT be overwritten by this
    # script — it includes an executive summary, methods block, and
    # per-family interpretation paragraphs that are derived from the
    # tables but not re-derivable. The auto file below mirrors the
    # script's view and is safe to regenerate.
    with open(OUTPUT_DIR / "factor_analysis_results_autogen.md", "w") as f:
        f.write("\n".join(md_lines) + "\n")

    log.info("Outputs written to %s", OUTPUT_DIR)


def main() -> None:
    """Collect and correct all factor analysis results."""
    new = load_new_results()
    reused = load_reused_results()
    prompt = load_prompt_engineering_results()

    all_results = new + reused + prompt
    log.info("Total comparisons: %d", len(all_results))

    # Count by family
    families = {}
    for r in all_results:
        fam = r["family"]
        families[fam] = families.get(fam, 0) + 1
    for fam, n in sorted(families.items()):
        log.info("  %s: %d comparisons", fam, n)

    corrected = apply_fdr(all_results)
    write_outputs(corrected)

    # Print summary
    print("\n" + "=" * 60)
    print("FACTOR ANALYSIS SUMMARY")
    print("=" * 60)
    fam_groups = {}
    for r in corrected:
        fam = r["family"]
        if fam not in fam_groups:
            fam_groups[fam] = []
        fam_groups[fam].append(r)

    for fam in [
        "architecture",
        "thinking",
        "temperature",
        "modality",
        "prompt_engineering",
    ]:
        fam_results = fam_groups.get(fam, [])
        n_sig = sum(
            1 for r in fam_results if r["significant"] != "ns"
        )
        print(f"\n{fam}: {n_sig}/{len(fam_results)} significant")
        for r in sorted(
            fam_results,
            key=lambda x: abs(x["delta_f1"]),
            reverse=True,
        ):
            print(
                f"  {r['label_a'][:35]:<35} vs "
                f"{r['label_b'][:35]:<35} "
                f"ΔF1={r['delta_f1']:>+.3f} "
                f"p_adj={r['p_value_adj']:.4f} "
                f"{r['significant']}",
            )


if __name__ == "__main__":
    main()
