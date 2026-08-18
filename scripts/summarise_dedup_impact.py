#!/usr/bin/env python3
# ============================================================================
# summarise_dedup_impact.py
# ----------------------------------------------------------------------------
# Consolidate the Session 136 deduplication metric-impact campaign into one
# machine-readable summary beside the human-readable findings document.
#
# Reads the per-run outputs of ``scripts/dedup_metric_impact.py``,
# ``scripts/dedup_tiering_rerun.py`` and
# ``scripts/diagnose_consensus_dedup_exposure.py``, and emits a single JSON
# carrying: the per-cell F1 and Matthews Correlation Coefficient (MCC)
# movements, the ΔF1/ΔMCC distributions restricted to cells the deduplication
# actually changed, the count of cells where the two metrics move in OPPOSITE
# directions, the committed-versus-rebuilt tie sets for every tiering re-run,
# and the consensus-artefact mechanism counts.
#
# DEGENERATE MCC
# --------------
# ``lib_advanced_metrics.calculate_tile_classification`` returns ``None`` when
# the tile confusion matrix has a zero row or column sum (e.g. every tile in
# scope carries a detection, so TN + FP = 0), and ``evaluate_detections``
# stores that as 0.0. A cell in that state has no defined committed MCC, so a
# ΔMCC against it is meaningless. Such cells are counted and excluded from the
# distributions rather than silently averaged in.
#
# COST: US$0.00. Pure aggregation of committed JSON.
#
# Usage:
#     python scripts/summarise_dedup_impact.py \
#         --input-dir results/dedup-metric-impact-2026-08-18 \
#         --output results/dedup-metric-impact-2026-08-18/findings-summary.json
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-08-18 (Session 136)
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

#: Impact-run stem -> the board or family it measures.
IMPACT_RUNS = {
    "impact-diversity-dividend-384": "diversity-dividend-384",
    "impact-gs-era2-pv-family": "gs-era2-pv-family-30m",
    "impact-era1-single-pass-board": "era1-single-pass-baseline-matrix",
    "impact-consensus-exposed": "exposed-consensus-conditions",
}

#: Tiering-run stem -> a short description of what the run holds fixed.
TIERING_RUNS = {
    "tiering-dd384-control-none-evalf1":
        "control: no deduplication, ranked by evaluation.json F1 (must "
        "reproduce the committed tiering)",
    "tiering-dd384-control-none-microf1":
        "control: no deduplication, ranked by the per-tile micro-F1 (isolates "
        "the ranking-key change)",
    "tiering-dd384-dedup-singlepass":
        "treatment: deduplicate only the artefacts that never reached "
        "merge_passes",
    "tiering-dd384-dedup-all":
        "sensitivity: deduplicate the consensus champions too",
    "tiering-55map-mcc-canonical-control": "control: 55-map canonical tile-MCC board",
    "tiering-55map-mcc-canonical-dedup": "treatment: 55-map canonical tile-MCC board",
    "tiering-55map-mcc-standardised-control":
        "control: 55-map standardised tile-MCC board",
    "tiering-55map-mcc-standardised-dedup":
        "treatment: 55-map standardised tile-MCC board",
}


def summarise_cell(cell: dict[str, Any], board: str) -> dict[str, Any]:
    """Reduce one impact-run cell to its headline movements.

    Args:
        cell: One entry from a ``dedup_metric_impact.py`` output.
        board: The board or family the cell belongs to.

    Returns:
        Flat per-cell summary dict.
    """
    means = cell["mean_over_passes"]
    passes = cell["passes"]
    removed = [p["dedup_stats"]["n_removed"] for p in passes]
    fractions = [p["dedup_stats"]["removed_fraction"] for p in passes]
    mcc_defined = all(
        p["as_committed"]["tile_classification"]["mcc"] is not None for p in passes
    )
    check = cell.get("committed_check") or {}

    out: dict[str, Any] = {
        "name": cell["name"],
        "board": board,
        "n_passes": cell["n_passes"],
        "n_passes_expected": cell.get("n_passes_expected"),
        "pass_count_gate": cell.get("pass_count_gate"),
        "tile_source": cell["tile_source"],
        "n_removed_total": sum(removed),
        "removed_fraction_mean": round(sum(fractions) / len(fractions), 6),
        "changed_by_dedup": sum(removed) > 0,
        "committed_mcc_defined": mcc_defined,
        "mcc": means["mcc"],
        "delta_mcc": means["delta"],
        "buffers": {
            b: {
                "f1_committed": block["as_committed"]["f1"],
                "f1_deduplicated": block["deduplicated"]["f1"],
                "delta_f1": block["delta_f1"],
                "delta_precision": block["delta_precision"],
                "delta_recall": block["delta_recall"],
            }
            for b, block in means["buffers"].items()
        },
        "committed_check": {
            "f1_agree_4dp": {
                b: v["agree_4dp"] for b, v in (check.get("buffers") or {}).items()
            },
            "mcc_abs_diff": (check.get("mcc") or {}).get("abs_diff"),
        },
    }
    return out


def distribution(values: list[float]) -> dict[str, Any]:
    """Summary statistics for a list of movements.

    Args:
        values: Numeric movements.

    Returns:
        Dict with n, min, median, max, and the sign counts.
    """
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "min": round(min(values), 6),
        "median": round(statistics.median(values), 6),
        "max": round(max(values), 6),
        "n_positive": sum(1 for v in values if v > 0),
        "n_negative": sum(1 for v in values if v < 0),
        "n_zero": sum(1 for v in values if v == 0),
    }


def summarise_tiering(path: Path) -> dict[str, Any]:
    """Reduce one tiering re-run to its tier structure.

    Args:
        path: Path to a ``dedup_tiering_rerun.py`` output.

    Returns:
        Dict with the tie set, tier sizes, and the top of the ranking.
    """
    data = json.loads(path.read_text())
    return {
        "board": data["board"],
        "dedup_mode": data["dedup_mode"],
        "rank_by": data["rank_by"],
        "n_permutations": data["n_permutations"],
        "seed": data["seed"],
        "fdr_q": data["fdr_q"],
        "n_tiers": len(data["tiers"]),
        "tie_set": data["tie_set"],
        "tier_sizes": [len(t["members"]) for t in data["tiers"]],
        "top_5": [
            {
                "rank": r["rank"],
                "ref": r["ref"],
                "tier": r["tier"],
                "score": r.get("observed_micro_f1", r.get("mcc")),
                "eval_f1": r.get("eval_f1"),
                "mcc_committed": r.get("mcc_committed"),
                "mcc_deduplicated": r.get("mcc_deduplicated", r.get("mcc")),
            }
            for r in data["ranking"][:5]
        ],
    }


def main() -> int:
    """CLI entry point.

    Returns:
        Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cells: list[dict[str, Any]] = []
    for stem, board in IMPACT_RUNS.items():
        path = args.input_dir / f"{stem}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        cells.extend(summarise_cell(c, board) for c in data["cells"])

    changed = [c for c in cells if c["changed_by_dedup"]]
    scorable = [c for c in changed if c["committed_mcc_defined"]]
    delta_f1 = [c["buffers"]["20"]["delta_f1"] for c in scorable]
    delta_mcc = [c["delta_mcc"]["delta_mcc_first_source_tile"] for c in scorable]
    delta_mcc_nearest = [
        c["delta_mcc"]["delta_mcc_nearest_centroid"] for c in scorable
    ]
    delta_mcc_union = [
        c["delta_mcc"]["delta_mcc_union_contributing"] for c in scorable
    ]
    opposite = [
        c["name"] for c, f, m in zip(scorable, delta_f1, delta_mcc)
        if f > 0 > m or m > 0 > f
    ]

    tierings = {}
    for stem, note in TIERING_RUNS.items():
        path = args.input_dir / f"{stem}.json"
        if path.exists():
            tierings[stem] = {"note": note, **summarise_tiering(path)}

    consensus_path = args.input_dir / "consensus-mechanism.json"
    consensus: dict[str, Any] = {}
    if consensus_path.exists():
        data = json.loads(consensus_path.read_text())
        pairs = sharing_pass = sharing_tile = 0
        fingerprint_ok = True
        for cond in data["conditions"]:
            for art in cond["artefacts"]:
                report = art["pair_report"]
                pairs += report["n_pairs"]
                sharing_pass += report["n_pairs_sharing_a_contributing_pass"]
                sharing_tile += report["n_pairs_sharing_a_source_tile"]
                fingerprint_ok &= art["merge_passes_property_set_present"]
        consensus = {
            "n_conditions": len(data["conditions"]),
            "n_residual_pairs": pairs,
            "n_pairs_sharing_a_contributing_pass": sharing_pass,
            "n_pairs_sharing_a_source_tile": sharing_tile,
            "all_artefacts_carry_merge_passes_property_set": bool(fingerprint_ok),
        }

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(args.input_dir),
        "n_cells_measured": len(cells),
        "n_cells_changed_by_dedup": len(changed),
        "n_cells_excluded_undefined_committed_mcc": len(changed) - len(scorable),
        "distributions": {
            "delta_f1_at_20m": distribution(delta_f1),
            "delta_mcc_first_source_tile": distribution(delta_mcc),
            "delta_mcc_nearest_centroid": distribution(delta_mcc_nearest),
            "delta_mcc_union_contributing": distribution(delta_mcc_union),
        },
        "n_cells_with_opposite_signs": len(opposite),
        "cells_with_opposite_signs": sorted(opposite),
        "tierings": tierings,
        "consensus_mechanism": consensus,
        "cells": cells,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
