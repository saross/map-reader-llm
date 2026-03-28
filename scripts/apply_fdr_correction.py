#!/usr/bin/env python3
"""Apply Benjamini-Hochberg FDR correction to pairwise test results.

Reads a run manifest from ``run_pairwise_tests.py``, separates
comparisons into FDR families (confirmatory, exploratory, leaderboard),
applies BH correction within each family, and outputs consolidated
paper tables.

Usage:

    python scripts/apply_fdr_correction.py \\
        --results-dir results/pairwise/30m \\
        --output-dir results/paper-tables/pairwise

Output files:
    - ``pairwise_results_fdr.json`` — full results with adjusted p-values
    - ``pairwise_results_fdr.csv`` — paper table format
    - ``pairwise_results_fdr.md`` — Markdown summary grouped by family

Created: 2026-03-28
Author: Shawn Ross & Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

__version__ = "1.0.0"


# ── FDR correction ──────────────────────────────────────────────────


def apply_bh_correction(
    p_values: list[float],
    q: float = 0.05,
) -> list[float]:
    """Apply Benjamini-Hochberg FDR correction.

    Uses the step-up procedure: sort p-values, compute adjusted values
    as p_i * m / rank, then enforce monotonicity by taking cumulative
    minimum from the largest rank downward.

    This implementation matches ``scipy.stats.false_discovery_control``
    with ``method='bh'`` but avoids the scipy dependency for this
    simple operation.

    Args:
        p_values: List of raw p-values.
        q: FDR threshold (not used in adjustment, but documented for
            clarity — the caller compares adjusted p to q).

    Returns:
        List of BH-adjusted p-values in the original order.
    """
    m = len(p_values)
    if m == 0:
        return []

    arr = np.array(p_values, dtype=float)
    # Sort indices
    order = np.argsort(arr)
    # Ranks (1-based)
    ranks = np.empty(m, dtype=float)
    ranks[order] = np.arange(1, m + 1, dtype=float)

    # Adjusted p-values: p_i * m / rank_i
    adjusted = arr * m / ranks
    # Enforce monotonicity: walk from largest rank down, take cummin
    sorted_adjusted = adjusted[order]
    cummin = np.minimum.accumulate(sorted_adjusted[::-1])[::-1]
    # Cap at 1.0
    cummin = np.minimum(cummin, 1.0)
    # Restore original order
    result = np.empty(m, dtype=float)
    result[order] = cummin

    return result.tolist()


def significance_marker(p: float) -> str:
    """Return significance marker for a p-value.

    Args:
        p: Adjusted p-value.

    Returns:
        '***', '**', '*', or 'ns'.
    """
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


# ── I/O ─────────────────────────────────────────────────────────────


def load_manifest(results_dir: Path) -> dict:
    """Load run_manifest.json from a results directory.

    Args:
        results_dir: Directory containing run_manifest.json.

    Returns:
        Parsed manifest dict.

    Raises:
        FileNotFoundError: If manifest is missing.
    """
    manifest_path = results_dir / "run_manifest.json"
    if not manifest_path.exists():
        msg = f"No run_manifest.json found in {results_dir}"
        raise FileNotFoundError(msg)

    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def write_json_output(
    comparisons: list[dict],
    metadata: dict,
    output_path: Path,
) -> None:
    """Write FDR-corrected results as JSON.

    Args:
        comparisons: List of comparison dicts with adjusted p-values.
        metadata: Run metadata dict.
        output_path: Output file path.
    """
    output = {
        "metadata": {
            **metadata,
            "fdr_correction": {
                "method": "Benjamini-Hochberg",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "script": "apply_fdr_correction.py",
                "version": __version__,
            },
        },
        "comparisons": comparisons,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logger.info("JSON written: %s", output_path)


def write_csv_output(
    comparisons: list[dict],
    output_path: Path,
) -> None:
    """Write FDR-corrected results as CSV for paper tables.

    Args:
        comparisons: List of comparison dicts with adjusted p-values.
        output_path: Output file path.
    """
    fieldnames = [
        "group", "question", "family",
        "label_a", "label_b",
        "f1_a", "f1_b", "delta_f1",
        "precision_a", "precision_b",
        "recall_a", "recall_b",
        "n_detections_a", "n_detections_b",
        "p_value_raw", "p_value_adj", "significant",
        "wins_a", "losses_a", "ties", "n_tiles",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for comp in comparisons:
            writer.writerow({
                "group": comp.get("group", ""),
                "question": comp.get("question", ""),
                "family": comp.get("family", ""),
                "label_a": comp["label_a"],
                "label_b": comp["label_b"],
                "f1_a": round(comp["f1_a"], 4),
                "f1_b": round(comp["f1_b"], 4),
                "delta_f1": round(comp["delta_f1"], 4),
                "precision_a": round(comp.get("precision_a", 0), 4),
                "precision_b": round(comp.get("precision_b", 0), 4),
                "recall_a": round(comp.get("recall_a", 0), 4),
                "recall_b": round(comp.get("recall_b", 0), 4),
                "n_detections_a": comp.get("n_detections_a", ""),
                "n_detections_b": comp.get("n_detections_b", ""),
                "p_value_raw": round(comp["p_value_raw"], 4),
                "p_value_adj": round(comp["p_value_adj"], 4),
                "significant": comp["significant"],
                "wins_a": comp.get("wins_a", ""),
                "losses_a": comp.get("losses_a", ""),
                "ties": comp.get("ties", ""),
                "n_tiles": comp.get("n_tiles", ""),
            })
    logger.info("CSV written: %s (%d rows)", output_path, len(comparisons))


def write_markdown_output(
    comparisons: list[dict],
    metadata: dict,
    output_path: Path,
) -> None:
    """Write FDR-corrected results as Markdown summary.

    Groups results by family, then by group within each family.

    Args:
        comparisons: List of comparison dicts with adjusted p-values.
        metadata: Run metadata dict.
        output_path: Output file path.
    """
    lines: list[str] = []
    lines.append("# Pairwise Permutation Test Results (FDR-Corrected)")
    lines.append("")
    lines.append(
        f"Buffer: {metadata.get('buffer_metres', '?')}m | "
        f"Permutations: {metadata.get('n_permutations', '?')} | "
        f"Seed: {metadata.get('seed', '?')}"
    )
    lines.append("")

    # Group by family
    families: dict[str, list[dict]] = {}
    for comp in comparisons:
        fam = comp.get("family", "unknown")
        families.setdefault(fam, []).append(comp)

    for family_name, family_comps in families.items():
        n_sig = sum(
            1 for c in family_comps if c["significant"] != "ns"
        )
        lines.append(f"## {family_name.title()} ({n_sig}/{len(family_comps)} significant)")
        lines.append("")

        # Sub-group by group number
        groups: dict[int, list[dict]] = {}
        for comp in family_comps:
            g = comp.get("group", 0)
            groups.setdefault(g, []).append(comp)

        for group_num in sorted(groups.keys()):
            group_comps = groups[group_num]
            question = group_comps[0].get("question", "")
            lines.append(f"### Group {group_num}: {question}")
            lines.append("")
            lines.append(
                "| Condition A | Condition B | F1_A | F1_B "
                "| ΔF1 | p (raw) | p (adj) | Sig |"
            )
            lines.append(
                "|---|---|---|---|---|---|---|---|"
            )
            for comp in group_comps:
                lines.append(
                    f"| {comp['label_a'][:40]} "
                    f"| {comp['label_b'][:40]} "
                    f"| {comp['f1_a']:.3f} | {comp['f1_b']:.3f} "
                    f"| {comp['delta_f1']:+.4f} "
                    f"| {comp['p_value_raw']:.4f} "
                    f"| {comp['p_value_adj']:.4f} "
                    f"| {comp['significant']} |"
                )
            lines.append("")

    # Overall summary
    total_sig = sum(
        1 for c in comparisons if c["significant"] != "ns"
    )
    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"- **Total comparisons:** {len(comparisons)}"
    )
    lines.append(
        f"- **Significant after FDR:** {total_sig}"
    )
    for fam_name, fam_comps in families.items():
        n_sig = sum(
            1 for c in fam_comps if c["significant"] != "ns"
        )
        lines.append(
            f"- **{fam_name.title()}:** {n_sig}/{len(fam_comps)} significant"
        )
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("Markdown written: %s", output_path)


# ── Main ─────────────────────────────────────────────────────────────


def main() -> None:
    """Apply FDR correction to pairwise permutation test results."""
    parser = argparse.ArgumentParser(
        description=(
            "Apply Benjamini-Hochberg FDR correction to pairwise "
            "permutation test results. Reads run_manifest.json, "
            "corrects by family, and outputs paper tables."
        ),
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--results-dir", type=Path, required=True,
        help="Directory containing run_manifest.json",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for corrected results",
    )
    parser.add_argument(
        "--q", type=float, default=0.05,
        help="FDR threshold q (default: 0.05)",
    )

    args = parser.parse_args()

    # Load manifest
    manifest = load_manifest(args.results_dir)
    metadata = manifest.get("metadata", {})
    raw_comparisons = manifest.get("comparisons", [])

    if not raw_comparisons:
        logger.error("No comparisons found in manifest.")
        sys.exit(1)

    logger.info(
        "Loaded %d comparisons from %s",
        len(raw_comparisons), args.results_dir,
    )

    # Separate into FDR families
    families: dict[str, list[tuple[int, dict]]] = {}
    for i, comp in enumerate(raw_comparisons):
        fam = comp.get("family", "confirmatory")
        families.setdefault(fam, []).append((i, comp))

    logger.info(
        "FDR families: %s",
        {k: len(v) for k, v in families.items()},
    )

    # Apply BH correction within each family
    adjusted_p: dict[int, float] = {}
    for fam_name, fam_entries in families.items():
        indices = [idx for idx, _ in fam_entries]
        raw_p = [comp["p_value"] for _, comp in fam_entries]
        adj_p = apply_bh_correction(raw_p, q=args.q)

        for idx, p_adj in zip(indices, adj_p):
            adjusted_p[idx] = p_adj

        n_sig = sum(1 for p in adj_p if p < args.q)
        logger.info(
            "  %s: %d comparisons, %d significant at q=%.2f",
            fam_name, len(fam_entries), n_sig, args.q,
        )

    # Build output comparison list with adjusted p-values
    output_comparisons: list[dict] = []
    for i, comp in enumerate(raw_comparisons):
        p_adj = adjusted_p.get(i, comp["p_value"])
        output_comparisons.append({
            **comp,
            "p_value_raw": comp["p_value"],
            "p_value_adj": round(p_adj, 6),
            "significant": significance_marker(p_adj),
        })

    # Write outputs
    write_json_output(
        output_comparisons, metadata,
        args.output_dir / "pairwise_results_fdr.json",
    )
    write_csv_output(
        output_comparisons,
        args.output_dir / "pairwise_results_fdr.csv",
    )
    write_markdown_output(
        output_comparisons, metadata,
        args.output_dir / "pairwise_results_fdr.md",
    )

    # Console summary
    print(f"\nFDR correction complete (q={args.q}):")
    for fam_name, fam_entries in families.items():
        indices = [idx for idx, _ in fam_entries]
        n_sig = sum(
            1 for idx in indices
            if adjusted_p[idx] < args.q
        )
        print(f"  {fam_name}: {n_sig}/{len(fam_entries)} significant")
    print(
        f"\nOutputs in {args.output_dir}:"
        f"\n  pairwise_results_fdr.json"
        f"\n  pairwise_results_fdr.csv"
        f"\n  pairwise_results_fdr.md"
    )


if __name__ == "__main__":
    main()
