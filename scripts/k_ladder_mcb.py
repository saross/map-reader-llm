#!/usr/bin/env python3
# ============================================================================
# k_ladder_mcb.py
# ----------------------------------------------------------------------------
# The per-family Hsu multiple-comparisons-with-the-best (MCB) admissible set
# for every K ladder of `results/k-ladder-2026-09-12/findings.md`.
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# § 6.1 and § 7.5 of the K-ladder findings record one outstanding requirement
# of the review's run card: a Hsu MCB admissible set per family, at simultaneous
# 95 %, so that "which rungs cannot be ruled out as the best rung of this
# ladder" is answered by the canonical simultaneous instrument rather than by
# the ad hoc pairwise-permutation-plus-Benjamini-Hochberg-plus-greedy-clique
# tie set. The Principal Investigator (PI) ruled on 2026-09-13 to "wait for the
# sets", then sign the review's analysis row. This driver supplies them.
#
# WHAT IT DOES NOT REIMPLEMENT, AND WHY
# -------------------------------------
# Nothing statistical. The instrument is the Era-2 board's own MCB tool,
# `scripts/selection_aware_intervals.py --board`, invoked exactly as the board
# invokes it (10,000 bootstrap resamples of TILES, seed 42, m-out-of-n fraction
# 1.0, the candidate set read from an analyses file by condition id, each cell
# resolved through `era1_leaderboard_tiering.load_cells` so the candidate scored
# here is the candidate that cell's committed evaluation scored). See the board
# README's 2026-09-13 and 2026-09-12 entries
# (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md`) for
# the board's own use of the same tool, and the tool's module docstring for the
# Hsu (1984) / Edwards & Hsu (1983) construction and the bootstrap critical
# value that replaces Dunnett's tabulated one.
#
# This driver only:
#
#   1. holds the registry of ladders, each with the analyses file, conditions
#      file, bounds override and headline buffer that its COMMITTED tiering
#      used, so the admissible set is computed on the ladder's own frame and
#      reference rather than on a single global frame;
#   2. runs the tool once per ladder per metric — F1 at the ladder's headline
#      buffer, and tile-level Matthews Correlation Coefficient (MCC) wherever
#      the ladder has an interpretable per-tile table;
#   3. GATES each run by reproducing the committed tiering's own per-rung
#      statistic (see THE GATE);
#   4. collates the admissible sets, expressed in pass counts K, into one
#      summary artefact and one Markdown table for § 6.1 of the findings.
#
# THE GATE
# --------
# For every ladder and every metric, the MCB's rebuilt per-candidate statistic
# must equal the number the committed artefact already publishes:
#
#   * F1 — each rung's `f1` in the committed `tiering_<buffer>m.json` ranking,
#     to 1e-4 (the precision the ranking records);
#   * MCC — each rung's `tile_mcc` in the ladder inventory, to 1e-4.
#
# The candidate LABEL SET must also equal the committed tiering's ranking
# labels exactly. Together these prove the admissible set was computed over the
# same cells, on the same frame, at the same operating points that the
# committed tiering ranked — not over a set that merely resembles it.
#
# WITHHELD CELLS STAY WITHHELD
# ----------------------------
# The three Gemini 3.7 gold-standard text rungs whose `source_tile` vocabulary
# is not the board frame's are refused by the tile-join invariant: their
# per-tile true-positive / false-positive / false-negative table is
# unavailable on this frame, so they enter no permutation family and no
# admissible set (the board README's 2026-09-13 entry; findings § 7.3). Because
# the invariant refuses the F1 arm as well as the MCC arm, that family is left
# with two sound rungs of four — below the review's three-rung bar — so it has
# NO admissible set on either metric. It is listed rather than silently
# dropped.
#
# Usage (sapphire, from an isolated worktree):
#   .venv/bin/python scripts/k_ladder_mcb.py \
#       --output-dir results/k-ladder-2026-09-12/mcb
#   .venv/bin/python scripts/k_ladder_mcb.py --only gs-stride-a --bootstrap 200
#
# Zero Application Programming Interface (API) calls. All computation is local.
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-09-13 | Apache 2.0
# ============================================================================
"""Compute the Hsu MCB admissible set for every K ladder, on its own frame."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

#: The Era-2 board frame. The gold-standard and tier E ladders are tiered on it
#: by override (their committed evaluations name a different frame), so their
#: MCB must carry the same override or it would answer a different question.
BOARD_BOUNDS = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"

#: Instrument constants, matching the board's own MCB invocation.
BOOTSTRAP = 10000
M_FRAC = 1.0
SEED = 42
SIMULTANEOUS_CONFIDENCE = 0.95

K_LADDER_DIR = Path("results/k-ladder-2026-09-12")
PHASE1_INVENTORY = K_LADDER_DIR / "ladders.json"
PHASE2_INVENTORY = K_LADDER_DIR / "phase2" / "ladders-compat.json"
TIER_E_INVENTORY = K_LADDER_DIR / "tier-e" / "ladder.json"

#: Gate tolerances. The committed tiering ranking records F1 to 4 decimal
#: places and the inventories record tile-MCC to 4, so the gate is set at a
#: unit in the last place: an exact reproduction to the recorded precision.
F1_GATE_TOL = 1e-4
MCC_GATE_TOL = 1e-4

#: The thirteen Phase 2 `pv-diag-384` ladders, by the slug their committed
#: tiering directory uses. Every one is on the board frame at 20 m and reads
#: its cell set from a scratch analyses sidecar plus the register's conditions.
PHASE2_SLUGS = (
    "phase2-flash-minimal-text-n30-t07-text-t0-3",
    "phase2-flash-minimal-text-n30-t07-text-t0-7",
    "phase2-flash-minimal-text-n30-t07-text-t1-0",
    "phase2-flash-high-text-n5-text-t0-3",
    "phase2-flash-high-text-n5-text-t0-7",
    "phase2-flash-high-text-n5-text-t1-0",
    "phase2-image-n5-image-t0-3",
    "phase2-image-n5-image-t0-7",
    "phase2-image-n5-image-t1-0",
    "phase2-flash-high-image-n5-image-t0-3",
    "phase2-flash-high-image-n5-image-t0-7",
    "phase2-flash-high-image-n5-image-t1-0",
    "phase2-scale-4-optimal-487",
)

#: Display names for the ladders whose slug is not self-describing. The Phase 2
#: families take their name from `phase2/ladders-compat.json` instead, so the
#: table's row labels match the names `phase2/ladder-tables.md` already uses.
DISPLAY_NAMES = {
    "gs-stride-a": "GS stride A, exact re-verification (board frame)",
    "tier-e": "Grid 384 px / 50 % MINIMAL text, verified (tier E)",
    "55map-stride-a-r2": "55-map stride A, r2",
    "55map-stride-a-standardised": "55-map stride A, standardised",
    "55map-stride-b-r2": "55-map stride B, r2",
    "55map-stride-b-standardised": "55-map stride B, standardised",
    "55map-stride-b-g37vf-r2": "55-map stride B, 3.7 verifier",
    "37arm1-r2": "3.7 arm 1",
    "37arm2-r2": "3.7 arm 2",
}

#: The seven 55-map deployment ladders, by committed tiering slug. Each carries
#: its own reference (r2 or standardised) inside its cells' evaluations, so no
#: bounds or ground-truth override is passed — exactly as their committed
#: tiering ran (`scripts/k_ladder_mcc_test.py`, whose `--bounds` default is
#: None for every ladder but the gold standard).
DEPLOYMENT_SLUGS = (
    "55map-stride-a-r2",
    "55map-stride-a-standardised",
    "55map-stride-b-r2",
    "55map-stride-b-standardised",
    "55map-stride-b-g37vf-r2",
    "37arm1-r2",
    "37arm2-r2",
)

#: The one family with no admissible set, and why. Stated as data so the
#: summary artefact and the findings table can both read it from one place.
WITHHELD: dict[str, Any] = {
    "family": "Gemini 3.7 text, GS B geometry (the 3.7 gold-standard text screen)",
    "proposer_pool": "g384_ov192_g37",
    "n_rungs": 4,
    "n_rungs_withheld": 2,
    "cells_withheld": [
        "gemini37-screen-2026-08-28::g37-text-k1-verified-opmax",
        "gemini37-screen-2026-08-28::g37-text-k1-verified-carried-p0.10-k1",
        "gemini37-screen-2026-08-28::g37-text-k3-verified-opmax",
    ],
    "why": (
        "The tile-join invariant refuses these cells' per-tile TP/FP/FN table "
        "on the board frame: their proposer ran on the ov192 tiling, whose "
        "source_tile vocabulary is absent from the frame's 336-stride "
        "vocabulary, so 20-22 of 467-526 in-frame detections are credited to "
        "a tile. The refusal falls on the F1 arm as well as the MCC arm, so "
        "neither an F1 nor an MCC admissible set can be computed. With K = 1 "
        "and K = 3 withheld the family retains two sound rungs of four, below "
        "the review's three-rung bar."
    ),
    "anchors": [
        "results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md"
        " (2026-09-13 entry, 'Admitted but WITHHELD')",
        "results/k-ladder-2026-09-12/findings.md § 7.3",
        "reports/tile-mcc-geometric-join-2026-09-12.md",
    ],
    "lifted_by": (
        "the corpus-wide tile-join decision (board close-out question 4), "
        "still open with the PI"
    ),
}


def display_names() -> dict[str, str]:
    """Return every ladder slug's human-readable family name.

    Returns:
        Slug to display name, the Phase 2 families read from their committed
        compatibility inventory so the names never drift from the tables.
    """
    names = dict(DISPLAY_NAMES)
    data = json.loads((BASE_DIR / PHASE2_INVENTORY).read_text(encoding="utf-8"))
    for ladder in data["ladders"]:
        names[ladder["slug"]] = ladder.get("family_base") or ladder["family"]
    return names


def ladder_registry() -> list[dict[str, Any]]:
    """Build the registry of ladders whose admissible set is to be computed.

    Each entry names the analysis id, the analyses and conditions files, the
    bounds override and the headline buffer that the ladder's COMMITTED tiering
    used. Keeping them in one table rather than deriving them per call site is
    what makes "on each ladder's own frame and reference" auditable.

    Returns:
        One dict per ladder, in report order: gold standard, tier E, the
        thirteen Phase 2 families, the seven 55-map deployment ladders.
    """
    entries: list[dict[str, Any]] = [
        {
            "slug": "gs-stride-a",
            "analysis_id": "k-ladder-gs-stride-a-2026-09-12",
            "analyses": K_LADDER_DIR / "tiering-input/gs-stride-a/run-analyses.json",
            "conditions": K_LADDER_DIR / "tiering-input/gs-stride-a/run-conditions.json",
            "bounds": BOARD_BOUNDS,
            "buffer_m": 20,
            "tiering": K_LADDER_DIR / "mcc-test/tiering/gs-stride-a/tiering_20m.json",
            "group": "gold standard",
        },
        {
            "slug": "tier-e",
            "analysis_id": "k-ladder-tier-e-2026-09-12",
            "analyses": K_LADDER_DIR / "tier-e/tiering-input/run-analyses.json",
            "conditions": K_LADDER_DIR / "tier-e/tiering-input/run-conditions.json",
            "bounds": BOARD_BOUNDS,
            "buffer_m": 20,
            "tiering": K_LADDER_DIR / "tier-e/tiering/tiering_20m.json",
            "group": "tier E",
        },
    ]
    for slug in PHASE2_SLUGS:
        entries.append({
            "slug": slug,
            "analysis_id": f"k-ladder-mcc-{slug}-2026-09-12",
            "analyses": (K_LADDER_DIR / "phase2/mcc-test/tiering-input" / slug
                         / "run-analyses.json"),
            "conditions": None,
            "bounds": None,
            "buffer_m": 20,
            "tiering": (K_LADDER_DIR / "phase2/mcc-test/tiering" / slug
                        / "tiering_20m.json"),
            "group": "Phase 2 (pv-diag-384)",
        })
    for slug in DEPLOYMENT_SLUGS:
        entries.append({
            "slug": slug,
            "analysis_id": f"k-ladder-mcc-{slug}-2026-09-12",
            "analyses": (K_LADDER_DIR / "mcc-test/tiering-input" / slug
                         / "run-analyses.json"),
            "conditions": None,
            "bounds": None,
            "buffer_m": 50,
            "tiering": (K_LADDER_DIR / "mcc-test/tiering" / slug
                        / "tiering_50m.json"),
            "group": "55-map deployment",
        })
    return entries


def label_to_k() -> dict[str, int]:
    """Map every ladder rung's cell LABEL to its pass count K.

    The admissible set is only useful as a statement about K, and the MCB tool
    reports candidates by label, so the two have to be joined. The join is read
    from the three committed ladder inventories rather than parsed out of the
    label text, because a label such as ``…-n10-oracle-p0.15-k7-r2-gt`` carries
    two integers and only one of them is K.

    Returns:
        Label (the part of a condition id after ``::``) to pass count.

    Raises:
        ValueError: if two inventories disagree on a label's K.
    """
    mapping: dict[str, int] = {}

    def put(label: str, k: int) -> None:
        if mapping.get(label, k) != k:
            raise ValueError(
                f"inventories disagree on K for {label!r}: "
                f"{mapping[label]} and {k}")
        mapping[label] = k

    for rel in (PHASE1_INVENTORY, PHASE2_INVENTORY):
        data = json.loads((BASE_DIR / rel).read_text(encoding="utf-8"))
        for ladder in data["ladders"]:
            for rung in ladder["rungs"]:
                put(rung["condition_id"].split("::", 1)[-1], int(rung["K"]))

    tier_e = json.loads((BASE_DIR / TIER_E_INVENTORY).read_text(encoding="utf-8"))
    for rung in tier_e["rungs"]:
        put(rung["label"], int(rung["n_passes"]))

    return mapping


def inventory_tile_mcc() -> dict[str, float]:
    """Map every rung label to its committed tile-MCC, for the MCC gate.

    Returns:
        Label to committed tile-MCC, omitting rungs whose tile-MCC is withheld
        or absent.
    """
    out: dict[str, float] = {}
    for rel in (PHASE1_INVENTORY, PHASE2_INVENTORY):
        data = json.loads((BASE_DIR / rel).read_text(encoding="utf-8"))
        for ladder in data["ladders"]:
            for rung in ladder["rungs"]:
                if rung.get("tile_mcc") is not None:
                    out[rung["condition_id"].split("::", 1)[-1]] = float(
                        rung["tile_mcc"])
    tier_e = json.loads((BASE_DIR / TIER_E_INVENTORY).read_text(encoding="utf-8"))
    for rung in tier_e["rungs"]:
        if rung.get("tile_mcc") is not None:
            out[rung["label"]] = float(rung["tile_mcc"])
    return out


def committed_ranking(tiering_path: Path) -> dict[str, float]:
    """Read a committed tiering's per-rung F1, keyed by label.

    Args:
        tiering_path: Repo-relative path to a ``tiering_<buffer>m.json``.

    Returns:
        Label to the F1 the committed ranking records.
    """
    data = json.loads((BASE_DIR / tiering_path).read_text(encoding="utf-8"))
    out: dict[str, float] = {}
    for row in data["ranking"]:
        label = row.get("label") or str(row.get("ref"))
        for key in ("f1", "eval_f1", "f1_headline"):
            if row.get(key) is not None:
                out[label] = float(row[key])
                break
    return out


def recover_statistics(result: dict[str, Any]) -> list[float]:
    """Recover every candidate's full-data statistic from the MCB output.

    The tool publishes ``apparent_f1`` (the winner's statistic) and
    ``mcb_theta`` (``theta_i = stat_i - max_{j != i} stat_j``), which together
    determine every candidate's statistic: for a non-winner
    ``stat_i = theta_i + best``, and the winner is ``apparent_f1`` itself. This
    is what the gate compares against the committed artefacts, so the gate
    reads the tool's own published numbers rather than a re-derivation.

    Args:
        result: One parsed MCB artefact.

    Returns:
        Per-candidate statistic, in the tool's candidate order.
    """
    best = float(result["apparent_f1"])
    k_star = int(result["selected_index"])
    stats: list[float] = []
    for i, theta in enumerate(result["mcb_theta"]):
        stats.append(best if i == k_star else best + float(theta))
    return stats


def run_mcb(entry: dict[str, Any], metric: str, out_dir: Path,
            bootstrap: int) -> tuple[Path, dict[str, Any]]:
    """Invoke the board's MCB tool for one ladder and one metric.

    Args:
        entry: A registry entry from :func:`ladder_registry`.
        metric: ``f1`` or ``mcc``.
        out_dir: Directory the tool writes its artefact into.
        bootstrap: Bootstrap resamples (10,000 for a reportable run).

    Returns:
        ``(artefact_path, parsed_artefact)``.

    Raises:
        subprocess.CalledProcessError: if the tool exits non-zero.
        FileNotFoundError: if the expected artefact is absent afterwards.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(BASE_DIR / "scripts/selection_aware_intervals.py"),
        "--board", entry["analysis_id"],
        "--analyses", str(BASE_DIR / entry["analyses"]),
        "--metric", metric,
        "--buffer", str(entry["buffer_m"]),
        "--bootstrap", str(bootstrap),
        "--m-frac", str(M_FRAC),
        "--out", str(out_dir),
    ]
    if entry.get("conditions"):
        cmd += ["--conditions", str(BASE_DIR / entry["conditions"])]
    if entry.get("bounds"):
        cmd += ["--bounds", str(BASE_DIR / entry["bounds"])]
    subprocess.run(cmd, check=True, cwd=BASE_DIR)

    suffix = "" if metric == "f1" else f"_{metric}"
    name = f"{entry['analysis_id']}{suffix}_b{entry['buffer_m']}_m{M_FRAC:g}.json"
    path = out_dir / name
    if not path.exists():
        raise FileNotFoundError(f"MCB tool wrote no {path}")
    return path, json.loads(path.read_text(encoding="utf-8"))


def gate(entry: dict[str, Any], metric: str, result: dict[str, Any],
         committed_f1: dict[str, float],
         committed_mcc: dict[str, float]) -> dict[str, Any]:
    """Gate one MCB run against the committed artefacts.

    Args:
        entry: The registry entry.
        metric: ``f1`` or ``mcc``.
        result: The parsed MCB artefact.
        committed_f1: Label to committed tiering F1 for this ladder.
        committed_mcc: Label to committed inventory tile-MCC.

    Returns:
        A gate record with one row per candidate.

    Raises:
        ValueError: if the label set differs from the committed tiering's, or
            any candidate's statistic misses its committed value.
    """
    kept = result["kept_indices"]
    labels = [result["candidates"][i]["label"] for i in kept]
    if set(labels) != set(committed_f1):
        raise ValueError(
            f"{entry['slug']} {metric}: candidate labels {sorted(labels)} do "
            f"not match the committed tiering's {sorted(committed_f1)}")

    reference = committed_f1 if metric == "f1" else committed_mcc
    tolerance = F1_GATE_TOL if metric == "f1" else MCC_GATE_TOL
    stats = recover_statistics(result)
    rows: list[dict[str, Any]] = []
    for label, value in zip(labels, stats, strict=True):
        expected = reference.get(label)
        if expected is None:
            raise ValueError(
                f"{entry['slug']} {metric}: no committed {metric} for {label}")
        delta = abs(value - expected)
        rows.append({"label": label, "committed": round(expected, 6),
                     "reproduced": round(value, 6), "abs_delta": round(delta, 8)})
        if delta > tolerance:
            raise ValueError(
                f"{entry['slug']} {metric}: {label} reproduced {value:.6f} "
                f"against committed {expected:.6f} (tolerance {tolerance})")
    return {"metric": metric, "tolerance": tolerance, "passed": True,
            "n_candidates_gated": len(rows), "candidates": rows}


def summarise(entry: dict[str, Any], result: dict[str, Any],
              k_of: dict[str, int]) -> dict[str, Any]:
    """Express one MCB run's admissible set in pass counts K.

    Args:
        entry: The registry entry.
        result: The parsed MCB artefact.
        k_of: Label to pass count.

    Returns:
        A per-metric summary block.
    """
    kept = result["kept_indices"]
    labels = [result["candidates"][i]["label"] for i in kept]
    ks = [k_of[label] for label in labels]
    admissible = sorted({ks[i] for i in result["hsu_not_ruled_out"]})
    band = sorted({ks[i] for i in result["mcb_not_ruled_out"]})
    stats = recover_statistics(result)
    return {
        "metric": result["metric"],
        "n_candidates": result["n_candidates"],
        "n_tiles": result["n_tiles"],
        "best_K": ks[int(result["selected_index"])],
        "best_statistic": round(float(result["apparent_f1"]), 6),
        "hsu_admissible_K": admissible,
        "hsu_w_upper": result["hsu_w_upper"],
        "hsu_w_lower": result["hsu_w_lower"],
        "two_sided_band_K": band,
        "two_sided_critical_width": result["mcb_critical_width"],
        "theta_by_K": {str(k): round(float(t), 6)
                       for k, t in zip(ks, result["mcb_theta"], strict=True)},
        "statistic_by_K": {str(k): round(float(s), 6)
                           for k, s in zip(ks, stats, strict=True)},
        "contains_K3": 3 in admissible,
        "excludes_K10": 10 in ks and 10 not in admissible,
        "whole_ladder": len(admissible) == len(ks),
    }


def markdown_table(ladders: list[dict[str, Any]]) -> str:
    """Render the § 6.1 admissible-set table.

    Args:
        ladders: The collated per-ladder summaries.

    Returns:
        A Markdown table as a single string.
    """
    lines = [
        "| ladder | rungs (K) | F1-admissible set | tile-MCC-admissible set "
        "| w_upper (F1 / MCC) |",
        "|---|---|---|---|---|",
    ]
    for lad in ladders:
        rungs = ", ".join(str(k) for k in lad["rungs"])
        f1_block = lad.get("f1") or {}
        mcc_block = lad.get("mcc") or {}
        f1_set = ", ".join(f"**{k}**" for k in f1_block.get("hsu_admissible_K", []))
        mcc_set = ", ".join(f"**{k}**" for k in mcc_block.get("hsu_admissible_K", []))
        widths = (f"{f1_block.get('hsu_w_upper', float('nan')):.4f} / "
                  f"{mcc_block.get('hsu_w_upper', float('nan')):.4f}")
        lines.append(
            f"| {lad['family']} | {rungs} | {f1_set or '—'} | "
            f"{mcc_set or '—'} | {widths} |")
    return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hsu MCB admissible sets for every K ladder.")
    parser.add_argument("--output-dir", type=Path,
                        default=BASE_DIR / K_LADDER_DIR / "mcb",
                        help="Where the per-ladder artefacts and the summary go.")
    parser.add_argument("--bootstrap", type=int, default=BOOTSTRAP,
                        help="Bootstrap resamples; 10,000 for a reportable run.")
    parser.add_argument("--only", action="append", default=None,
                        help="Restrict to these ladder slugs (repeatable).")
    parser.add_argument("--metrics", nargs="+", default=["f1", "mcc"],
                        choices=("f1", "mcc"),
                        help="Metrics to compute; both by default.")
    args = parser.parse_args()

    registry = ladder_registry()
    if args.only:
        wanted = set(args.only)
        registry = [e for e in registry if e["slug"] in wanted]
        missing = wanted - {e["slug"] for e in registry}
        if missing:
            parser.error(f"unknown ladder slug(s): {sorted(missing)}")

    k_of = label_to_k()
    committed_mcc = inventory_tile_mcc()
    names = display_names()
    out_root = args.output_dir
    out_root.mkdir(parents=True, exist_ok=True)

    collated: list[dict[str, Any]] = []
    for entry in registry:
        print(f"\n=== MCB {entry['slug']} "
              f"@ {entry['buffer_m']} m ===", flush=True)
        committed_f1 = committed_ranking(entry["tiering"])
        record: dict[str, Any] = {
            "slug": entry["slug"],
            "group": entry["group"],
            "analysis_id": entry["analysis_id"],
            "headline_buffer_m": entry["buffer_m"],
            "analyses": str(entry["analyses"]),
            "conditions": str(entry["conditions"]) if entry["conditions"]
                          else "results/run-conditions.json (the register)",
            "bounds_override": entry["bounds"],
            "committed_tiering": str(entry["tiering"]),
            "gates": [],
        }
        for metric in args.metrics:
            path, result = run_mcb(entry, metric, out_root / entry["slug"],
                                   args.bootstrap)
            record["gates"].append(
                gate(entry, metric, result, committed_f1, committed_mcc))
            block = summarise(entry, result, k_of)
            block["artefact"] = str(path.relative_to(BASE_DIR))
            record[metric] = block
        first = record.get("f1") or record.get("mcc") or {}
        record["rungs"] = sorted(int(k) for k in first.get("theta_by_K", {}))
        record["family"] = names.get(entry["slug"], entry["slug"])
        record["n_rungs"] = len(committed_f1)
        collated.append(record)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/k_ladder_mcb.py",
        "instrument": {
            "tool": "scripts/selection_aware_intervals.py --board",
            "construction": (
                "Hsu (1984) / Edwards & Hsu (1983) constrained one-sided MCB "
                "on theta_i = stat_i - max_{j != i} stat_j, with the critical "
                "value bootstrapped over TILES rather than taken from "
                "Dunnett's table; a rung is ruled out as best only when its "
                "simultaneous upper bound falls at or below zero"),
            "simultaneous_confidence": SIMULTANEOUS_CONFIDENCE,
            "bootstrap": args.bootstrap,
            "m_frac": M_FRAC,
            "seed": SEED,
            "resampling_unit": "tile (Decision 10)",
            "same_as": (
                "the Era-2 board's own MCB step — "
                "results/leaderboard/era2/gs-era2-verified-board-2026-09-10/"
                "mcb/ and that board's README 2026-09-12 and 2026-09-13 "
                "entries"),
        },
        "n_ladders": len(collated),
        "gate_all_passed": all(g["passed"] for lad in collated
                               for g in lad["gates"]),
        "roll_up": {
            "ladders_whose_F1_admissible_set_contains_K3": [
                lad["slug"] for lad in collated
                if (lad.get("f1") or {}).get("contains_K3")],
            "ladders_whose_F1_admissible_set_excludes_K10": [
                lad["slug"] for lad in collated
                if (lad.get("f1") or {}).get("excludes_K10")],
            "ladders_whose_F1_admissible_set_is_the_whole_ladder": [
                lad["slug"] for lad in collated
                if (lad.get("f1") or {}).get("whole_ladder")],
            "ladders_whose_MCC_admissible_set_is_the_whole_ladder": [
                lad["slug"] for lad in collated
                if (lad.get("mcc") or {}).get("whole_ladder")],
            "ladders_whose_MCC_admissible_set_contains_K1": [
                lad["slug"] for lad in collated
                if 1 in ((lad.get("mcc") or {}).get("hsu_admissible_K") or [])],
        },
        "withheld": WITHHELD,
        "ladders": collated,
    }
    (out_root / "summary.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out_root / "table.md").write_text(
        markdown_table(collated) + "\n", encoding="utf-8")
    print(f"\nwrote {out_root / 'summary.json'} and {out_root / 'table.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
