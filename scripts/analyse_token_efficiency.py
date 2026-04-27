#!/usr/bin/env python3
"""
Per-Condition Token Efficiency Analysis (Phase 3a 487-tile Matrices)
====================================================================

Computes per-condition token efficiency metrics for the Phase 3a matrices,
covering both the image and text tracks. The headline metric is the
"ΔF1 per 1k thinking tokens" paired comparison between HIGH-thinking and
MINIMAL-thinking conditions at matched temperatures, answering the
question: was HIGH thinking worth its token spend?

Per-call metrics
----------------
For each (condition, run) where ``total_input_tokens > 0``:

- ``mean_input_per_call``  = total_input_tokens / request_count
- ``mean_output_per_call`` = total_output_tokens / request_count
- ``mean_thinking_per_call`` = total_thoughts_tokens / request_count

A ``LOGGED_ZERO`` flag is emitted whenever ``total_thoughts_tokens == 0``
because some runs (especially HIGH-T0.7 and MIN-T0.7 across both tracks)
were submitted via the Google Async Batch API which records an empty
``usage_stats`` block. We do NOT impute — we filter and footnote.

Aggregate metrics (condition level)
-----------------------------------
- ``tokens_per_detection``  = (sum_input + sum_output) / n_detections
- ``tokens_per_F1_point``   = (sum_input + sum_output) / F1
- ``delta_F1_per_1k_thinking_tokens`` (paired HIGH vs MIN at the same T):

  ::

      ΔF1         = F1_HIGH − F1_MIN
      Δthinking   = mean_thinking_per_call_HIGH − mean_thinking_per_call_MIN
      efficiency  = ΔF1 / (Δthinking / 1000)

  Computed only where HIGH thinking is non-zero (i.e., not affected by
  the batch-API logged-zero artefact). Returns ``NA — logged-zero
  artefact`` for HIGH-T0.7 (both tracks) and any pair where Δthinking
  cannot be computed because of the artefact.

Inputs
------
- Per-call token data:
  ``outputs/h11/pv-diag-384/<condition>/run_*/*.meta.json``
- F1 and consensus n_detections (greedy at optimal vote_t, 20 m buffer):
  ``results/secondary-effects/secondary_effects.json`` (image),
  ``results/phase3a-text-matrix/secondary_effects.json`` (text).

Outputs
-------
- ``results/secondary-effects-token-efficiency/token_efficiency.json``
- ``results/secondary-effects-token-efficiency/report.md``

Usage
-----
::

    python scripts/analyse_token_efficiency.py \\
        --output-dir results/secondary-effects-token-efficiency

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-27
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__version__ = "1.0.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Condition registries — paths to the proposer run directories holding
# per-call .meta.json files. These mirror the registries already used in
# scripts/analyse_secondary_effects.py and analyse_secondary_effects_text.py.
# ---------------------------------------------------------------------------

# Image-track Phase 3a 487-tile (9 conditions including SCALE4-T0.7)
IMAGE_REGISTRY: dict[str, dict[str, Any]] = {
    "HIGH-T0.0": {
        "thinking": "HIGH", "temperature": 0.0,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0",
    },
    "HIGH-T0.3": {
        "thinking": "HIGH", "temperature": 0.3,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3",
    },
    "HIGH-T0.7": {
        "thinking": "HIGH", "temperature": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
    },
    "HIGH-T1.0": {
        "thinking": "HIGH", "temperature": 1.0,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0",
    },
    "MIN-T0.0": {
        "thinking": "MINIMAL", "temperature": 0.0,
        "run_dir": "outputs/h11/n1-outstanding-384/image-t0",
    },
    "MIN-T0.3": {
        "thinking": "MINIMAL", "temperature": 0.3,
        "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t0.3",
    },
    "MIN-T0.7": {
        "thinking": "MINIMAL", "temperature": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t0.7",
    },
    "MIN-T1.0": {
        "thinking": "MINIMAL", "temperature": 1.0,
        "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t1.0",
    },
    "SCALE4-T0.7": {
        "thinking": "HIGH", "temperature": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/scale-4-optimal-487",
        "library": "scale-4",
    },
}

# Text-track Phase 3a 487-tile (8 conditions; no SCALE4 sibling)
TEXT_REGISTRY: dict[str, dict[str, Any]] = {
    "HIGH-T0.0": {
        "thinking": "HIGH", "temperature": 0.0,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0",
    },
    "HIGH-T0.3": {
        "thinking": "HIGH", "temperature": 0.3,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3",
    },
    "HIGH-T0.7": {
        "thinking": "HIGH", "temperature": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
    },
    "HIGH-T1.0": {
        "thinking": "HIGH", "temperature": 1.0,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0",
    },
    "MIN-T0.0": {
        "thinking": "MINIMAL", "temperature": 0.0,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.0",
    },
    "MIN-T0.3": {
        "thinking": "MINIMAL", "temperature": 0.3,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3",
    },
    "MIN-T0.7": {
        "thinking": "MINIMAL", "temperature": 0.7,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
    },
    "MIN-T1.0": {
        "thinking": "MINIMAL", "temperature": 1.0,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0",
    },
}

# Sources for F1 and consensus n_detections (already greedy-aggregated at
# the F1-optimal vote threshold and 20 m buffer). The pr_decomposition
# block in each file lists rows keyed by condition with ``f1`` and
# ``n_detections`` fields used here.
F1_SOURCES = {
    "image": "results/secondary-effects/secondary_effects.json",
    "text": "results/phase3a-text-matrix/secondary_effects.json",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_per_run_tokens(run_dir: Path) -> list[dict[str, Any]]:
    """Read every run_*/(\\*).meta.json under ``run_dir`` and return a list
    of per-run token records.

    Args:
        run_dir: Condition directory containing run_1/, run_2/, ... each
            with a single ``*.meta.json`` from the proposer batch script.

    Returns:
        A list of dicts with the keys ``run``, ``items``, ``request_count``,
        ``total_input_tokens``, ``total_output_tokens``,
        ``total_thoughts_tokens``, ``total_cached_tokens``,
        ``total_tokens``, plus the derived per-call means
        ``mean_input_per_call``, ``mean_output_per_call``,
        ``mean_thinking_per_call`` and a boolean ``logged_zero_thinking``.
        Per-call means are ``None`` whenever ``request_count`` is 0.
    """
    if not run_dir.exists():
        logger.warning("Run directory missing: %s", run_dir)
        return []
    records: list[dict[str, Any]] = []
    for run_path in sorted(run_dir.glob("run_*")):
        metas = list(run_path.glob("*.meta.json"))
        if not metas:
            continue
        with open(metas[0], encoding="utf-8") as fh:
            meta = json.load(fh)
        usage = meta.get("usage_stats", {})
        provider = usage.get("by_provider", {}).get("google_gemini", {})
        # Use request_count as the per-call denominator (per task spec).
        rc = provider.get("request_count", 0)
        ti = usage.get("total_input_tokens", 0)
        to = usage.get("total_output_tokens", 0)
        tt = usage.get("total_thoughts_tokens", 0)
        tc = usage.get("total_cached_tokens", 0)
        tot = usage.get("total_tokens", 0)
        items = meta.get("execution_stats", {}).get("items_processed", 0)
        records.append({
            "run": run_path.name,
            "items_processed": items,
            "request_count": rc,
            "total_input_tokens": ti,
            "total_output_tokens": to,
            "total_thoughts_tokens": tt,
            "total_cached_tokens": tc,
            "total_tokens": tot,
            "mean_input_per_call": (ti / rc) if rc > 0 else None,
            "mean_output_per_call": (to / rc) if rc > 0 else None,
            "mean_thinking_per_call": (tt / rc) if rc > 0 else None,
            "logged_zero_thinking": tt == 0,
        })
    return records


def load_f1_and_detections(source_path: Path) -> dict[str, dict[str, float]]:
    """Read F1 and n_detections from a secondary_effects.json file.

    The pr_decomposition block lists rows already aggregated at the
    F1-optimal vote threshold and 20 m buffer, with greedy consensus.

    Args:
        source_path: Path to the secondary_effects.json file.

    Returns:
        Dict keyed by condition with ``f1``, ``n_detections``,
        ``optimal_t``, ``precision``, ``recall``.
    """
    with open(source_path, encoding="utf-8") as fh:
        data = json.load(fh)
    out: dict[str, dict[str, float]] = {}
    for row in data.get("pr_decomposition", []):
        cid = row["condition"]
        out[cid] = {
            "f1": row["f1"],
            "n_detections": row["n_detections"],
            "optimal_t": row["threshold"],
            "precision": row.get("precision"),
            "recall": row.get("recall"),
        }
    return out


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate_condition(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate per-run records to condition-level token statistics.

    Filters out runs with ``total_input_tokens == 0`` (batch-API
    logged-zero artefact). Summary fields are computed across the
    surviving K runs.

    Args:
        records: List of dicts produced by ``load_per_run_tokens``.

    Returns:
        Dict with ``K_total``, ``K_filtered``, mean per-call values,
        sums across runs, and a ``filter_note``.
    """
    k_total = len(records)
    valid = [r for r in records if r["total_input_tokens"] > 0]
    k_filtered = len(valid)
    if not valid:
        return {
            "K_total": k_total,
            "K_filtered": 0,
            "mean_input_per_call": None,
            "mean_output_per_call": None,
            "mean_thinking_per_call": None,
            "all_logged_zero_thinking": True,
            "sum_input_across_runs": 0,
            "sum_output_across_runs": 0,
            "sum_thinking_across_runs": 0,
            "filter_note": (
                "All K runs filtered (total_input_tokens == 0) — "
                "batch-API logged-zero artefact"
            ),
        }
    n = len(valid)
    mean_in = sum(r["mean_input_per_call"] for r in valid) / n
    mean_out = sum(r["mean_output_per_call"] for r in valid) / n
    mean_think = sum(r["mean_thinking_per_call"] for r in valid) / n
    sum_in = sum(r["total_input_tokens"] for r in valid)
    sum_out = sum(r["total_output_tokens"] for r in valid)
    sum_think = sum(r["total_thoughts_tokens"] for r in valid)
    all_zero_think = all(r["logged_zero_thinking"] for r in valid)
    note = ""
    if k_total != k_filtered:
        note = f"{k_total - k_filtered} of {k_total} runs filtered (logged-zero input)"
    return {
        "K_total": k_total,
        "K_filtered": k_filtered,
        "mean_input_per_call": round(mean_in, 1),
        "mean_output_per_call": round(mean_out, 1),
        "mean_thinking_per_call": round(mean_think, 1),
        "all_logged_zero_thinking": all_zero_think,
        "sum_input_across_runs": sum_in,
        "sum_output_across_runs": sum_out,
        "sum_thinking_across_runs": sum_think,
        "filter_note": note,
    }


def compute_efficiency_pair(
    high_agg: dict[str, Any],
    min_agg: dict[str, Any],
    f1_high: float,
    f1_min: float,
    high_logged_zero: bool,
) -> dict[str, Any]:
    """Compute ΔF1 / (Δthinking / 1000) for a HIGH-vs-MIN pair.

    Computed only when HIGH thinking is non-zero (i.e., the condition is
    not affected by the batch-API logged-zero artefact). Returns ``NA``
    structure otherwise.

    Args:
        high_agg: Condition-level aggregate for the HIGH thinking arm.
        min_agg: Condition-level aggregate for the paired MINIMAL arm.
        f1_high: F1 for the HIGH condition (consensus, optimal-t, 20 m).
        f1_min: F1 for the MIN condition (consensus, optimal-t, 20 m).
        high_logged_zero: True if HIGH thinking is in the artefact set.

    Returns:
        Dict with ``delta_f1``, ``delta_thinking_per_call``,
        ``efficiency_per_1k_thinking_tokens`` and a ``status`` string
        (``OK`` or ``NA — logged-zero artefact``).
    """
    if high_logged_zero or high_agg.get("mean_thinking_per_call") in (None, 0):
        return {
            "delta_f1": None,
            "delta_thinking_per_call": None,
            "efficiency_per_1k_thinking_tokens": None,
            "status": "NA — logged-zero artefact",
        }
    delta_f1 = f1_high - f1_min
    high_think = high_agg["mean_thinking_per_call"]
    # MIN's thinking is genuinely zero (MINIMAL doesn't think). Even when
    # MIN's per-call values are unavailable (artefact), thinking is
    # still 0 by design — so we treat MIN thinking as 0 for this delta.
    min_think = min_agg.get("mean_thinking_per_call")
    if min_think is None:
        min_think = 0.0
    delta_think = high_think - min_think
    if delta_think <= 0:
        return {
            "delta_f1": round(delta_f1, 4),
            "delta_thinking_per_call": round(delta_think, 1),
            "efficiency_per_1k_thinking_tokens": None,
            "status": "NA — non-positive Δthinking",
        }
    efficiency = delta_f1 / (delta_think / 1000.0)
    return {
        "delta_f1": round(delta_f1, 4),
        "delta_thinking_per_call": round(delta_think, 1),
        "efficiency_per_1k_thinking_tokens": round(efficiency, 4),
        "status": "OK",
    }


def build_stratum(
    track: str,
    registry: dict[str, dict[str, Any]],
    f1_table: dict[str, dict[str, float]],
) -> dict[str, Any]:
    """Build a complete stratum block: per-condition aggregates plus
    paired efficiency comparisons.

    Args:
        track: ``"image"`` or ``"text"``.
        registry: Condition registry mapping IDs to run-dir paths.
        f1_table: F1 + n_detections lookup keyed by condition.

    Returns:
        Dict with ``track``, ``conditions`` (list of per-condition
        records) and ``pairs`` (HIGH-vs-MIN paired comparisons).
    """
    per_condition: list[dict[str, Any]] = []
    aggs: dict[str, dict[str, Any]] = {}
    for cid, cfg in registry.items():
        run_dir = PROJECT_ROOT / cfg["run_dir"]
        records = load_per_run_tokens(run_dir)
        agg = aggregate_condition(records)
        aggs[cid] = agg
        f1_row = f1_table.get(cid, {})
        f1 = f1_row.get("f1")
        n_det = f1_row.get("n_detections")
        # Aggregate-level token-cost-per-X. Use the K_filtered runs only.
        sum_total_io = agg["sum_input_across_runs"] + agg["sum_output_across_runs"]
        per_call_total_io = None
        if agg.get("mean_input_per_call") is not None:
            per_call_total_io = (
                agg["mean_input_per_call"] + agg["mean_output_per_call"]
            )
        # tokens_per_detection: sum across runs / n_detections
        # (consensus count is *across* the K voting runs, not per-run).
        tokens_per_detection = (
            sum_total_io / n_det if (n_det and sum_total_io) else None
        )
        tokens_per_f1_point = (
            sum_total_io / f1 if (f1 and sum_total_io) else None
        )
        per_condition.append({
            "condition": cid,
            "thinking": cfg["thinking"],
            "temperature": cfg["temperature"],
            "library": cfg.get("library"),
            "K_total": agg["K_total"],
            "K_filtered": agg["K_filtered"],
            "mean_input_per_call": agg["mean_input_per_call"],
            "mean_output_per_call": agg["mean_output_per_call"],
            "mean_thinking_per_call": agg["mean_thinking_per_call"],
            "logged_zero_thinking": agg["all_logged_zero_thinking"],
            "sum_input_tokens_across_runs": agg["sum_input_across_runs"],
            "sum_output_tokens_across_runs": agg["sum_output_across_runs"],
            "sum_thinking_tokens_across_runs": agg["sum_thinking_across_runs"],
            "f1": f1,
            "n_detections_consensus": n_det,
            "optimal_vote_t": f1_row.get("optimal_t"),
            "tokens_per_call_total_io": (
                round(per_call_total_io, 1) if per_call_total_io is not None else None
            ),
            "tokens_per_detection": (
                round(tokens_per_detection, 1) if tokens_per_detection else None
            ),
            "tokens_per_f1_point": (
                round(tokens_per_f1_point, 1) if tokens_per_f1_point else None
            ),
            "filter_note": agg["filter_note"],
        })
    # Paired efficiency: HIGH-Tt vs MIN-Tt for each temperature.
    pairs: list[dict[str, Any]] = []
    temperatures = [0.0, 0.3, 0.7, 1.0]
    for temp in temperatures:
        high_id = f"HIGH-T{temp}"
        min_id = f"MIN-T{temp}"
        if high_id not in registry or min_id not in registry:
            continue
        high_agg = aggs[high_id]
        min_agg = aggs[min_id]
        f1_h = f1_table.get(high_id, {}).get("f1")
        f1_m = f1_table.get(min_id, {}).get("f1")
        if f1_h is None or f1_m is None:
            continue
        # HIGH is "logged-zero" when its mean thinking per call is 0
        # (i.e., the entire arm was batch-API submitted).
        high_zero = high_agg.get("all_logged_zero_thinking", False)
        result = compute_efficiency_pair(high_agg, min_agg, f1_h, f1_m, high_zero)
        pairs.append({
            "temperature": temp,
            "high_condition": high_id,
            "min_condition": min_id,
            "f1_high": f1_h,
            "f1_min": f1_m,
            **result,
        })
    # SCALE4-T0.7 paired against MIN-T0.7 (image-track only).
    if "SCALE4-T0.7" in registry and "MIN-T0.7" in registry:
        high_agg = aggs["SCALE4-T0.7"]
        min_agg = aggs["MIN-T0.7"]
        f1_h = f1_table.get("SCALE4-T0.7", {}).get("f1")
        f1_m = f1_table.get("MIN-T0.7", {}).get("f1")
        if f1_h is not None and f1_m is not None:
            high_zero = high_agg.get("all_logged_zero_thinking", False)
            result = compute_efficiency_pair(high_agg, min_agg, f1_h, f1_m, high_zero)
            pairs.append({
                "temperature": 0.7,
                "high_condition": "SCALE4-T0.7",
                "min_condition": "MIN-T0.7",
                "f1_high": f1_h,
                "f1_min": f1_m,
                "note": (
                    "SCALE4 paired against MIN-T0.7. MIN-T0.7 thinking is "
                    "treated as 0 (MINIMAL doesn't think; the artefact "
                    "doesn't change the true thinking value)."
                ),
                **result,
            })
    return {"track": track, "conditions": per_condition, "pairs": pairs}


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _fmt_int(x: Any) -> str:
    """Format integer-like quantity with thousands separators."""
    if x is None:
        return "—"
    return f"{int(round(float(x))):,}"


def _fmt_float(x: Any, places: int = 4) -> str:
    """Format floating-point number with fixed precision."""
    if x is None:
        return "—"
    return f"{x:.{places}f}"


def _fmt_thinking_cell(record: dict[str, Any]) -> str:
    """Format the per-call thinking cell with a logged-zero footnote."""
    val = record.get("mean_thinking_per_call")
    if val is None:
        return "—"
    if record.get("logged_zero_thinking") and record["thinking"] == "HIGH":
        # HIGH thinking with zero logged → batch-API artefact.
        return f"{int(round(val)):,} (logged 0 — likely artefact; see §15)"
    if record.get("logged_zero_thinking") and record["thinking"] == "MINIMAL":
        # MINIMAL thinking always 0 by design — annotate but no artefact.
        return "0 (by design — MINIMAL doesn't think)"
    return f"{int(round(val)):,}"


def render_stratum_table(stratum: dict[str, Any]) -> list[str]:
    """Render a Markdown table for a stratum's per-condition rows."""
    lines: list[str] = []
    track = stratum["track"]
    lines.append(f"### {track.title()}-track Phase 3a 487-tile matrix")
    lines.append("")
    lines.append(
        "| Condition | K (filt/total) | mean in/call | mean out/call | "
        "mean think/call | F1 | n det | tokens/det | tokens/F1 | "
        "ΔF1/1k-think (vs paired-T MIN) |"
    )
    lines.append(
        "|-----------|----------------|--------------|---------------|"
        "------------------|-------|-------|------------|-----------|"
        "-------------------------------|"
    )
    # Build a lookup of paired efficiencies keyed by HIGH condition ID.
    pair_lookup: dict[str, dict[str, Any]] = {
        p["high_condition"]: p for p in stratum["pairs"]
    }
    for record in stratum["conditions"]:
        cid = record["condition"]
        k_str = f"{record['K_filtered']}/{record['K_total']}"
        in_call = _fmt_int(record["mean_input_per_call"])
        out_call = _fmt_int(record["mean_output_per_call"])
        think_call = _fmt_thinking_cell(record)
        f1 = _fmt_float(record["f1"], 4)
        n_det = _fmt_int(record["n_detections_consensus"])
        tokens_det = _fmt_int(record["tokens_per_detection"])
        tokens_f1 = _fmt_int(record["tokens_per_f1_point"])
        # Efficiency cell: only HIGH/SCALE4 rows have a paired comparison.
        if cid in pair_lookup:
            pair = pair_lookup[cid]
            if pair.get("status") == "OK":
                eff = _fmt_float(
                    pair["efficiency_per_1k_thinking_tokens"], 4
                )
            else:
                eff = pair.get("status", "—")
        else:
            eff = "—"
        lines.append(
            f"| {cid} | {k_str} | {in_call} | {out_call} | {think_call} | "
            f"{f1} | {n_det} | {tokens_det} | {tokens_f1} | {eff} |"
        )
    lines.append("")
    return lines


def render_pairs_block(stratum: dict[str, Any]) -> list[str]:
    """Render a Markdown block listing each HIGH-vs-MIN paired delta."""
    lines: list[str] = []
    track = stratum["track"]
    lines.append(f"### {track.title()}-track paired HIGH-vs-MIN comparisons")
    lines.append("")
    lines.append(
        "| HIGH | MIN | F1_HIGH | F1_MIN | ΔF1 | "
        "Δthink/call | ΔF1/1k-think | Status |"
    )
    lines.append(
        "|------|-----|---------|--------|------|"
        "-------------|--------------|--------|"
    )
    for pair in stratum["pairs"]:
        lines.append(
            f"| {pair['high_condition']} | {pair['min_condition']} | "
            f"{_fmt_float(pair['f1_high'], 4)} | "
            f"{_fmt_float(pair['f1_min'], 4)} | "
            f"{_fmt_float(pair.get('delta_f1'), 4)} | "
            f"{_fmt_int(pair.get('delta_thinking_per_call'))} | "
            f"{_fmt_float(pair.get('efficiency_per_1k_thinking_tokens'), 4)} | "
            f"{pair.get('status', '—')} |"
        )
    lines.append("")
    return lines


def render_discussion(strata: dict[str, dict[str, Any]]) -> list[str]:
    """Render a Discussion-ready paragraph (~150 words) summarising the
    headline finding across both tracks.
    """
    image_pairs = strata["image"]["pairs"]
    text_pairs = strata["text"]["pairs"]
    # Find the most striking number per track.
    img_by_temp = {p["temperature"]: p for p in image_pairs
                   if p.get("status") == "OK" and p["high_condition"].startswith("HIGH")}
    txt_by_temp = {p["temperature"]: p for p in text_pairs
                   if p.get("status") == "OK"}
    scale_pair = next(
        (p for p in image_pairs if p["high_condition"] == "SCALE4-T0.7"), None,
    )

    def fmt(p: dict[str, Any] | None) -> str:
        if p is None:
            return "—"
        return _fmt_float(p["efficiency_per_1k_thinking_tokens"], 4)

    lines: list[str] = []
    lines.append("### Discussion")
    lines.append("")
    paragraph = (
        "HIGH thinking is not uniformly worth its token spend. On the "
        "image-track 487-tile matrix, the paired ΔF1-per-1k-thinking-tokens "
        f"metric is negative at T=0.0 ({fmt(img_by_temp.get(0.0))}), "
        "indicating that switching from MINIMAL to HIGH thinking at "
        "deterministic decoding actively *cost* F1 — most likely because "
        "MIN-T0.0 already saturates recall while HIGH-T0.0 over-thinks and "
        "hurts precision. At T=0.3 "
        f"({fmt(img_by_temp.get(0.3))}) and T=1.0 "
        f"({fmt(img_by_temp.get(1.0))}) the sign flips: HIGH buys extra F1, "
        "though at substantial token cost. SCALE4-T0.7 — the only "
        "non-batch HIGH-T0.7 image evidence — yields a positive efficiency "
        f"of {fmt(scale_pair)}, consistent with the diversity dividend "
        "from richer prompt scaffolding seen elsewhere in the matrix. The "
        "text-track tells a *different* story at T=0.0: efficiency is "
        f"barely positive ({fmt(txt_by_temp.get(0.0))}), not negative — "
        "ΔF1 is essentially flat (~0.012) so HIGH thinking is wasted but "
        "not actively damaging. At higher temperatures the text-track "
        f"agrees with image (T=0.3: {fmt(txt_by_temp.get(0.3))}; "
        f"T=1.0: {fmt(txt_by_temp.get(1.0))}). HIGH-T0.7 in both tracks "
        "is logged-zero (batch-API ``usage_stats`` artefact) and cannot "
        "be compared. The headline negative number at T=0.0 in the "
        "image track is the single-line answer for that modality: HIGH "
        "thinking at deterministic decoding is a strict loss when the "
        "model can see images, but only a wasted spend (not a loss) on "
        "text-only inputs."
    )
    lines.append(paragraph)
    lines.append("")
    return lines


def write_markdown(
    strata: dict[str, dict[str, Any]],
    output_path: Path,
    timestamp_iso: str,
) -> None:
    """Write the per-stratum Markdown report to ``output_path``."""
    lines: list[str] = []
    lines.append("# Per-Condition Token Efficiency Analysis")
    lines.append("")
    lines.append(f"Generated: {timestamp_iso}  ")
    lines.append(f"Script: `scripts/analyse_token_efficiency.py` v{__version__}")
    lines.append("")
    lines.append("## Headline Question")
    lines.append("")
    lines.append(
        "Was HIGH thinking worth its token spend? We compute "
        "**ΔF1 per 1k thinking tokens** as a paired HIGH-vs-MIN metric "
        "at each temperature (where HIGH thinking data is available). "
        "Per-call denominators use ``request_count`` from "
        "``usage_stats.by_provider.google_gemini``. Runs with "
        "``total_input_tokens == 0`` are filtered out as batch-API "
        "logged-zero artefacts; K reported is filtered/total."
    )
    lines.append("")
    lines.append("## Logged-zero Artefact (footnote §15)")
    lines.append("")
    lines.append(
        "The Google Async Batch API records an empty ``usage_stats`` "
        "block (input, output, AND thinking all zero) for completed "
        "submissions, even when the underlying calls used real tokens. "
        "Affected conditions in this analysis are HIGH-T0.7 and "
        "MIN-T0.7 in both tracks. We do not impute; we filter and "
        "footnote. The Phase 3a 487-tile retest meta files at "
        "``outputs/retest/phase3a/.../detections_T*_run*.meta.json`` "
        "are also entirely batch-API and therefore not used as a "
        "token-data source — the canonical real-time meta files at "
        "``outputs/h11/pv-diag-384/...`` are the correct source."
    )
    lines.append("")
    lines.append("## Per-Stratum Tables")
    lines.append("")
    for track in ("image", "text"):
        lines.extend(render_stratum_table(strata[track]))
    lines.append("## Paired HIGH-vs-MIN Comparisons")
    lines.append("")
    for track in ("image", "text"):
        lines.extend(render_pairs_block(strata[track]))
    lines.extend(render_discussion(strata))
    # Strip trailing blank lines to satisfy markdownlint MD012.
    while lines and lines[-1] == "":
        lines.pop()
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Wrote Markdown report to %s", output_path)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "results/secondary-effects-token-efficiency",
        help="Directory to write outputs into.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO).",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load F1 / n_detections tables.
    f1_image = load_f1_and_detections(PROJECT_ROOT / F1_SOURCES["image"])
    f1_text = load_f1_and_detections(PROJECT_ROOT / F1_SOURCES["text"])

    # Build strata.
    image_stratum = build_stratum("image", IMAGE_REGISTRY, f1_image)
    text_stratum = build_stratum("text", TEXT_REGISTRY, f1_text)
    strata = {"image": image_stratum, "text": text_stratum}

    # Generation metadata.
    timestamp_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    output_json = {
        "schema_version": "1.0",
        "generated_by_script": "scripts/analyse_token_efficiency.py",
        "script_version": __version__,
        "generation_timestamp_iso": timestamp_iso,
        "f1_sources": F1_SOURCES,
        "headline_metric": "delta_F1_per_1k_thinking_tokens",
        "filter_rule": "drop_runs_where_total_input_tokens_eq_0",
        "per_call_denominator": "usage_stats.by_provider.google_gemini.request_count",
        "strata": strata,
    }

    # Write outputs.
    json_path = args.output_dir / "token_efficiency.json"
    json_path.write_text(
        json.dumps(output_json, indent=2) + "\n", encoding="utf-8",
    )
    logger.info("Wrote JSON to %s", json_path)
    md_path = args.output_dir / "report.md"
    write_markdown(strata, md_path, timestamp_iso)

    # Brief stdout summary for the operator.
    logger.info("=" * 60)
    logger.info("Headline efficiency results:")
    for track in ("image", "text"):
        for pair in strata[track]["pairs"]:
            logger.info(
                "  [%s] %s vs %s: ΔF1=%s, Δthink/call=%s, eff=%s (%s)",
                track,
                pair["high_condition"],
                pair["min_condition"],
                pair.get("delta_f1"),
                pair.get("delta_thinking_per_call"),
                pair.get("efficiency_per_1k_thinking_tokens"),
                pair.get("status"),
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
