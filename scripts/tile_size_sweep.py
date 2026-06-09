#!/usr/bin/env python3
# ============================================================================
# tile_size_sweep.py
# ----------------------------------------------------------------------------
# Stage C of the Era-1 leaderboard plan (planning/era1-leaderboard-plan-
# 2026-06-08.md): characterise the effect of TILE SIZE (256 / 384 / 512 px) on
# matched configurations, F1@20 m-led, so the "give-us-your-map" pipeline can
# trade tile size against speed/cost.
#
# WHAT THIS PRODUCES
# ------------------
# Two complementary tabulations over already-scored conditions (no heavy
# compute -- this reads F1@20 m + tile-MCC straight from each cell's
# evaluation.json, so it is $0 and runs anywhere):
#
#   VIEW 1 -- clean tile-size isolation. Hold architecture x modality x
#   thinking x temperature CONSTANT and vary ONLY tile size, reading each
#   size's best-F1@20 m operating point (best over the available N x vote;
#   the optimal vote threshold scales with tile size -- Obs 179's "Goldilocks
#   zone shifts" -- so re-optimising vote per size is correct, while N is held
#   to keep the comparison clean). This isolates the tile-size effect within a
#   fixed configuration.
#
#   VIEW 2 -- best-achievable ceiling per (size x architecture x modality).
#   For each tile size, the single best single-pass cell and the single best
#   consensus cell, with MCC. This is the "what does each tile size buy you"
#   ceiling, and is where the architecture-dependent direction shows up.
#
# THE FINDING THIS CHARACTERISES (Obs 351, Obs 179, Obs 171)
# ----------------------------------------------------------
# The optimal tile size depends on the false-positive-filtering strength of the
# architecture: with no filter (single-pass) the larger tile wins (cleaner
# proposals); as the filter strengthens (HIGH-thinking diversity + high vote
# threshold; or consensus+verifier, Obs 179) the optimum shifts to the smaller
# 384 px tile, whose higher recall can be realised once its denser FP pool is
# pruned. 256 px falls under every architecture tested so far.
#
# METRIC + COMPARABILITY
# ----------------------
# F1@20 m is the cross-size-comparable headline: the three tile sizes are
# different tilings of the SAME four Gold-Standard maps + the SAME curator
# ground-truth mounds, so mound-level localisation F1 is as comparable as
# differently-sized tiles can be (user-confirmed: there is no more principled
# tile-size test). Tile-MCC is reported PER SIZE but NOT differenced -- it
# depends on the tile count (1032 / 487 / 340 -> different true-negative base),
# so cross-size MCC deltas are not meaningful.
#
# PROVENANCE CAVEATS (surfaced in the output)
# -------------------------------------------
#  * The 256 px anchor (pv-diag-256) is TEXT-ONLY with thin proposer provenance
#    (temperature + thinking level not materialised; 1032-tile scope), so its
#    cells are flagged and not force-matched to a specific temperature row.
#  * The 256 px consensus+verifier cell IS now tested (Stage-D, Obs 352, View 3:
#    F1 0.856) -- but its proposer is the PLAIN text 5-of-5 (N=5) family, whereas
#    384/512 share the HIGH-text N=30 lineage (HIGH-text was not run at 256), so
#    the 256 PV cell is its own thin-provenance anchor.
#  * image HIGH-thinking consensus exists at 384 but NOT at 512 (the
#    phase3a-high image track never ran), so that row is 384-only.
#
# Usage:
#     python scripts/tile_size_sweep.py \
#         --output-dir results/tile-size-sweep
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-06-08
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONDITIONS = BASE_DIR / "results" / "run-conditions.json"
DEFAULT_OUTPUT = BASE_DIR / "results" / "tile-size-sweep"
HEADLINE_BUFFER_M = 20

# Tile size per decomposed run (the same maps + curator GT at three tilings).
RUN_SIZE = {
    "pv-diag-256": 256,
    "pv-diag-384": 384,
    "retest-phase2a": 512, "retest-phase2b": 512, "retest-phase2c": 512,
    "retest-phase2d": 512, "retest-phase2e": 512,
    "retest-phase3a": 512, "retest-phase3a-high": 512,
    "retest-phase3a-replication": 512, "retest-phase3c": 512,
}
TILE_COUNT = {256: 1032, 384: 487, 512: 340}

# Thinking level per run (the label does not always carry it). phase2/phase3a
# are MINIMAL; phase3a-high + phase3c are HIGH; phase3a-replication is per-label;
# pv-diag-256's is unknown (thin provenance).
RUN_THINKING = {
    "retest-phase2a": "minimal", "retest-phase2b": "minimal",
    "retest-phase2c": "minimal", "retest-phase2d": "minimal",
    "retest-phase2e": "minimal",
    "retest-phase3a": "minimal", "retest-phase3a-high": "high",
    "retest-phase3c": "high",
}

# --- VIEW 1 matched single-pass cells (explicit + auditable). flash minimal. --
# Each entry: (modality, temperature) -> {size: "<run>::<label>"}.
SINGLE_PASS_MATCHED = {
    ("text", "0.0"): {
        256: "pv-diag-256::text-baseline",
        384: "pv-diag-384::baseline-flash-text-minimal-t-0-0-pv-baseline",
        512: "retest-phase2b::text-t0.0",
    },
    ("text", "0.7"): {
        384: "pv-diag-384::baseline-flash-text-minimal-t-0-7",
        512: "retest-phase2b::text-t0.7",
    },
    ("image", "0.0"): {
        384: "pv-diag-384::baseline-flash-image-minimal-t-0-0",
        512: "retest-phase2b::image-t0.0",
    },
    ("image", "0.7"): {
        384: "pv-diag-384::baseline-flash-image-minimal-t-0-7",
        512: "retest-phase2b::image-t0.7",
    },
}

# Note: the 256 text-baseline temperature/thinking are not materialised; it is
# placed in the text-T0.0 row as the project baseline but flagged thin-provenance.
THIN_PROVENANCE_REFS = {"pv-diag-256::text-baseline", "pv-diag-256::text-consensus-5of5"}

# --- VIEW 3 matched consensus+PV cells (the clean Stage-D head-to-head). -------
# Each entry: {size: "<run>::<label>"}. These are the consensus champions VERIFIED
# with the production carry-forward adversarial verifier (gemini-3-flash,
# verify_adversarial-text, T=0.0, minimal, n=1), scored at 14-buffer + tile-MCC,
# best-F1@20 m operating point per size. This is the consensus+PV analogue of
# SINGLE_PASS_MATCHED. The 384 ref (pv-diag-384::verified-adv-text-consensus-
# 16of30) is registered by a FOREGROUND session; until it lands in
# run-conditions.json, by_ref.get() returns None and build_pv_view() renders an
# em-dash for that size + drops fully-empty rows, so this view NO-OPS GRACEFULLY
# rather than erroring before the registration is applied.
PV_MATCHED = {
    ("text", "consensus+PV"): {
        256: "pv-diag-256::verified-adv-text-consensus-5of5",
        384: "pv-diag-384::verified-adv-text-consensus-16of30",
        512: "retest-phase3a-high::verified-adv-text-high-t1.0-n30-23of30",
    },
}


def git_commit() -> str:
    """Return the short HEAD commit hash, or ``"unknown"`` on failure."""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE_DIR)
            .decode().strip()
        )
    except Exception:  # pragma: no cover - provenance best-effort only
        return "unknown"


def f1_at_20m(eval_path: Path) -> float | None:
    """Read F1@20 m from a cell's evaluation.json, or None on absence."""
    try:
        s = json.loads(eval_path.read_text())["summary"]
        return float(next(b["f1"] for b in s["buffers"]
                          if b["buffer_metres"] == HEADLINE_BUFFER_M))
    except Exception:
        return None


def tile_mcc(eval_path: Path) -> float | None:
    """Read the tile-level MCC point estimate, or None on absence."""
    try:
        s = json.loads(eval_path.read_text())["summary"]
        return s.get("tile_classification", {}).get("mcc", {}).get("point")
    except Exception:
        return None


def parse_modality_temp(label: str, pool: str) -> tuple[str, str | None]:
    """Infer (modality, temperature) from a condition label/proposer pool.

    Args:
        label: The condition label.
        pool: The condition's proposer_pool string (may be empty).

    Returns:
        ``(modality, temperature)`` where modality is "text"/"image" and
        temperature is e.g. "0.7" or None if not encoded in the label.
    """
    s = f"{label} {pool}".lower()
    if "image" in s and "text" not in s:
        modality = "image"
    elif "text" in s and "image" not in s:
        modality = "text"
    else:
        modality = "image" if "image" in s else "text"
    m = re.search(r"t([01]\.\d)", s)
    return modality, (m.group(1) if m else None)


def load_cells(conditions_path: Path) -> list[dict]:
    """Load every decomposed cell with size + parsed attributes + F1/MCC.

    Args:
        conditions_path: Path to results/run-conditions.json.

    Returns:
        List of cell dicts (ref, run, size, architecture, modality, thinking,
        temperature, n_passes, vote, f1, mcc, thin_provenance).
    """
    decomposition = json.loads(conditions_path.read_text())["decomposition"]
    cells: list[dict] = []
    for run, size in RUN_SIZE.items():
        for c in decomposition.get(run, {}).get("conditions", []):
            ref = f"{run}::{c['label']}"
            modality, temp = parse_modality_temp(c["label"], c.get("proposer_pool") or "")
            thinking = RUN_THINKING.get(run)
            if thinking is None:  # per-label (replication) or unknown (256)
                low = c["label"].lower()
                thinking = "high" if "high" in low else ("minimal" if "minimal" in low else None)
            eval_path = BASE_DIR / c["eval_path"]
            # Model: only pv-diag-384 ran genuine Gemini-3 Pro (label carries
            # "pro"); everything else is gemini-3-flash. Tracked so the
            # tile-size ceilings can be model-MATCHED (a Pro-vs-Flash mix would
            # confound model with tile size).
            model = "pro" if "pro" in c["label"].lower() else "flash"
            cells.append({
                "ref": ref, "run": run, "label": c["label"], "size": size,
                "architecture": c.get("architecture"), "model": model,
                "modality": modality, "thinking": thinking, "temperature": temp,
                "n_passes": c.get("n_passes"), "vote": c.get("vote_threshold"),
                "f1": f1_at_20m(eval_path), "mcc": tile_mcc(eval_path),
                "thin_provenance": ref in THIN_PROVENANCE_REFS,
            })
    return cells


def best_consensus_per_size(
    cells: list[dict], modality: str, thinking: str, temperature: str
) -> dict[int, dict]:
    """Best-F1@20 m consensus cell per size for a fixed (modality,thinking,temp).

    Holds architecture=consensus, modality, thinking and temperature constant
    and, at each size, returns the cell with the highest F1@20 m (best over the
    available N x vote -- the optimal vote scales with tile size).

    Args:
        cells: All loaded cells.
        modality: "text" or "image".
        thinking: "minimal" or "high".
        temperature: e.g. "0.7".

    Returns:
        Map ``size -> best cell dict`` (only sizes where a match exists).
    """
    out: dict[int, dict] = {}
    for c in cells:
        if (c["architecture"] == "consensus" and c["modality"] == modality
                and c["thinking"] == thinking and c["temperature"] == temperature
                and c["f1"] is not None):
            if c["size"] not in out or c["f1"] > out[c["size"]]["f1"]:
                out[c["size"]] = c
    return out


def best_per_size_architecture(cells: list[dict]) -> dict:
    """Best-F1@20 m FLASH cell per (size, architecture, modality), + a Pro note.

    Restricted to ``model == "flash"`` so the per-size ceilings are MODEL-MATCHED
    across tile sizes (genuine Pro ran only at 384 px, so including it would
    confound model with tile size). The best Pro single-pass cells are returned
    separately as ``pro_note`` for transparency.

    Args:
        cells: All loaded cells.

    Returns:
        Dict with ``by_arch_modality`` (size -> "arch/modality" -> best FLASH
        cell) and ``pro_note`` (the best Pro single-pass cells, 384-only).
    """
    by_arch_mod: dict[int, dict[str, dict]] = {}
    pro: dict[str, dict] = {}
    for c in cells:
        if c["f1"] is None or c["architecture"] is None:
            continue
        if c["model"] == "pro":
            key = f"{c['size']}/{c['architecture']}/{c['modality']}"
            if key not in pro or c["f1"] > pro[key]["f1"]:
                pro[key] = c
            continue
        key = f"{c['architecture']}/{c['modality']}"
        am = by_arch_mod.setdefault(c["size"], {})
        if key not in am or c["f1"] > am[key]["f1"]:
            am[key] = c
    return {"by_arch_modality": by_arch_mod, "pro_note": pro}


def _direction(by_size: dict[int, float]) -> str:
    """Annotate the tile-size direction from the per-size F1 values."""
    have = {s: f for s, f in by_size.items() if f is not None}
    if len(have) < 2:
        return "single-size"
    lo, hi = min(have), max(have)
    delta = have[hi] - have[lo]
    best_size = max(have, key=have.get)
    if abs(delta) < 0.015:
        return f"flat ({lo}≈{hi})"
    return f"best={best_size}px (Δ{delta:+.3f} over {lo}→{hi})"


def build_views(cells: list[dict]) -> dict:
    """Assemble VIEW 1 (clean isolation) and VIEW 2 (best-per-size) tables."""
    by_ref = {c["ref"]: c for c in cells}

    # --- VIEW 1a: single-pass clean isolation ---
    sp_rows = []
    for (modality, temp), size_refs in SINGLE_PASS_MATCHED.items():
        per_size = {}
        for size, ref in size_refs.items():
            c = by_ref.get(ref)
            per_size[size] = {
                "ref": ref,
                "f1": c["f1"] if c else None,
                "mcc": c["mcc"] if c else None,
                "thin_provenance": c["thin_provenance"] if c else None,
            } if c else None
        sp_rows.append({
            "architecture": "single-pass", "modality": modality, "thinking": "minimal",
            "temperature": temp,
            "by_size": {s: (v["f1"] if v else None) for s, v in per_size.items()},
            "cells": per_size,
            "direction": _direction({s: (v["f1"] if v else None) for s, v in per_size.items()}),
        })

    # --- VIEW 1b: consensus clean isolation (fully-provenanced temps) ---
    con_rows = []
    consensus_configs = [
        ("text", "minimal", "0.3"), ("text", "minimal", "0.7"), ("text", "minimal", "1.0"),
        ("text", "high", "0.3"), ("text", "high", "0.7"), ("text", "high", "1.0"),
        ("image", "minimal", "0.3"), ("image", "minimal", "0.7"), ("image", "minimal", "1.0"),
        ("image", "high", "0.3"), ("image", "high", "0.7"), ("image", "high", "1.0"),
    ]
    for modality, thinking, temp in consensus_configs:
        best = best_consensus_per_size(cells, modality, thinking, temp)
        if not best:
            continue
        cells_by_size = {
            s: {"ref": c["ref"], "f1": c["f1"], "mcc": c["mcc"],
                "n": c["n_passes"], "vote": c["vote"]}
            for s, c in best.items()
        }
        con_rows.append({
            "architecture": "consensus", "modality": modality, "thinking": thinking,
            "temperature": temp,
            "by_size": {s: c["f1"] for s, c in best.items()},
            "cells": cells_by_size,
            "direction": _direction({s: c["f1"] for s, c in best.items()}),
        })

    # --- VIEW 3: consensus+PV matched (Stage-D head-to-head) ---
    pv_rows = build_pv_view(by_ref)

    view2 = best_per_size_architecture(cells)
    return {"single_pass_isolation": sp_rows, "consensus_isolation": con_rows,
            "pv_matched": pv_rows, "best_per_size": view2}


def build_pv_view(by_ref: dict[str, dict]) -> list[dict]:
    """Build the matched consensus+PV rows from PV_MATCHED.

    Resolves each size's registered condition via ``by_ref``. A ref that is not
    (yet) in run-conditions.json resolves to ``None`` -> the size renders as an
    em-dash, so this view degrades gracefully before the foreground registers
    the new PV condition(s). Rows where NO size resolves are dropped entirely, so
    the table is empty (not erroring) until at least one PV cell is registered.

    Args:
        by_ref: Map of ``"<run>::<label>"`` -> loaded cell dict.

    Returns:
        List of row dicts (one per PV_MATCHED entry that has >=1 resolved size),
        each with ``by_size`` (F1@20 m), ``cells`` (full per-size detail) and a
        tile-size ``direction`` annotation.
    """
    rows = []
    for (modality, arch), size_refs in PV_MATCHED.items():
        per_size = {}
        for size, ref in size_refs.items():
            c = by_ref.get(ref)
            per_size[size] = ({
                "ref": ref, "f1": c["f1"], "mcc": c["mcc"],
                "n": c["n_passes"], "vote": c["vote"],
            } if c else None)
        # Drop the row only if NOTHING resolved (keeps the view a no-op until at
        # least one PV cell is in the manifest).
        if not any(per_size.values()):
            continue
        by_size = {s: (v["f1"] if v else None) for s, v in per_size.items()}
        rows.append({
            "architecture": arch, "modality": modality,
            "by_size": by_size, "cells": per_size,
            "direction": _direction(by_size),
        })
    return rows


def main() -> int:
    """CLI entry point: load cells, build views, write JSON + Markdown."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conditions", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    cells = load_cells(args.conditions)
    views = build_views(cells)

    result = {
        "analysis_id": "tile-size-sweep",
        "metric": "f1",
        "buffer_metres": HEADLINE_BUFFER_M,
        "tile_counts": TILE_COUNT,
        "comparability_note": (
            "F1@20 m is cross-size comparable (same 4 GS maps + curator GT, three "
            "tilings). Tile-MCC reported per size, NOT differenced (tile-count base "
            "differs: 1032/487/340)."
        ),
        "provenance_caveats": [
            "256 px anchor (pv-diag-256) is text-only, thin proposer provenance "
            "(temp/thinking not materialised; 1032-tile scope).",
            "256 px consensus+verifier IS now tested (Stage-D, Obs 352, View 3: "
            "F1 0.856); its proposer is the plain text 5-of-5 (N=5) family, whereas "
            "384/512 share the HIGH-text N=30 lineage (HIGH-text was not run at 256), "
            "so the 256 PV cell is its own thin-provenance anchor.",
            "image HIGH-thinking consensus exists at 384 but not 512 (phase3a-high "
            "image track never ran).",
        ],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        **views,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "tile_size_sweep.json"
    json_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {json_path}", flush=True)

    _write_markdown(args.output_dir / "tile_size_sweep.md", result)
    print(f"Wrote {args.output_dir / 'tile_size_sweep.md'}", flush=True)
    return 0


def _fmt(v: float | None) -> str:
    """Format an F1/MCC value or an em-dash for None."""
    return f"{v:.3f}" if isinstance(v, (int, float)) else "—"


def _write_markdown(md_path: Path, result: dict) -> None:
    """Write the human-readable tile-size sweep Markdown."""
    tc = result["tile_counts"]
    lines = [
        "# Tile-size sweep — 256 / 384 / 512 px (F1@20 m) — `tile-size-sweep`",
        "",
        f"- **Metric**: micro-average F1 @ {result['buffer_metres']} m "
        "(cross-size comparable); MCC per size (NOT differenced).",
        f"- **Tile counts**: 256→{tc[256]}, 384→{tc[384]}, 512→{tc[512]} "
        "(different tilings of the same 4 GS maps + curator GT).",
        "- **Caveats**: " + " ".join(result["provenance_caveats"]),
        "",
        "## View 1a — single-pass clean isolation (flash minimal; vary only tile size)",
        "",
        "| modality | temp | 256 | 384 | 512 | direction |",
        "|---|---|---:|---:|---:|---|",
    ]
    for r in result["single_pass_isolation"]:
        bs = r["by_size"]
        lines.append(
            f"| {r['modality']} | {r['temperature']} | {_fmt(bs.get(256))} | "
            f"{_fmt(bs.get(384))} | {_fmt(bs.get(512))} | {r['direction']} |"
        )
    lines += [
        "",
        "## View 1b — consensus clean isolation (best-F1 op-point per size; vote scales with size)",
        "",
        "| modality | thinking | temp | 256 | 384 | 512 | direction |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for r in result["consensus_isolation"]:
        bs = r["by_size"]
        lines.append(
            f"| {r['modality']} | {r['thinking']} | {r['temperature']} | "
            f"{_fmt(bs.get(256))} | {_fmt(bs.get(384))} | {_fmt(bs.get(512))} | "
            f"{r['direction']} |"
        )
    pv_rows = result.get("pv_matched", [])
    if pv_rows:
        lines += [
            "",
            "## View 3 — consensus+PV matched (Stage-D head-to-head; carry-forward verifier)",
            "",
            "Consensus champion VERIFIED with the production adversarial verifier "
            "(gemini-3-flash, verify_adversarial-text, T=0.0, minimal, n=1), scored at "
            "14-buffer + tile-MCC, best-F1@20 m operating point per size.",
            "",
            "| modality | arch | 256 | 384 | 512 | direction |",
            "|---|---|---:|---:|---:|---|",
        ]
        for r in pv_rows:
            bs = r["by_size"]
            lines.append(
                f"| {r['modality']} | {r['architecture']} | {_fmt(bs.get(256))} | "
                f"{_fmt(bs.get(384))} | {_fmt(bs.get(512))} | {r['direction']} |"
            )
    lines += [
        "",
        "## View 2 — best-achievable FLASH ceiling per (size × architecture × modality)",
        "",
        "Model-matched (gemini-3-flash) so the ceilings compare tile size, not model.",
        "",
        "| size | architecture/modality | best cell | F1@20m | MCC |",
        "|---:|---|---|---:|---:|",
    ]
    bam = result["best_per_size"]["by_arch_modality"]
    for size in sorted(bam, reverse=True):
        for key in sorted(bam[size]):
            c = bam[size][key]
            lines.append(
                f"| {size} | {key} | `{c['label']}` | {_fmt(c['f1'])} | {_fmt(c['mcc'])} |"
            )
    pro = result["best_per_size"]["pro_note"]
    if pro:
        lines += [
            "",
            "**Pro note** (genuine Gemini-3 Pro ran ONLY at 384 px — shown for "
            "context, not a tile-size comparison):",
            "",
            "| size/arch/modality | cell | F1@20m | MCC |",
            "|---|---|---:|---:|",
        ]
        for key in sorted(pro):
            c = pro[key]
            lines.append(
                f"| {key} | `{c['label']}` | {_fmt(c['f1'])} | {_fmt(c['mcc'])} |"
            )
    md_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
