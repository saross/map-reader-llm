#!/usr/bin/env python3
"""
Author manifest conditions for the four Era-1 phase3 runs (Session 106).
========================================================================

Reads the 14-buffer + MCC re-score outputs (``results/rescore-2026-06-07/``)
produced from the phase3 consensus / diversity-pool GeoJSONs, selects each
configuration's **best-F1 @ 20 m** vote-threshold operating point, and writes the
``proposer_pools`` / ``verifier_passes`` / ``conditions`` blocks for the four
runs into ``results/run-conditions.json``.

This follows the Session-102 ``pv-diag-384-consensus-calibration`` template and
the decomposition rule (``/remember`` 2026-06-05): **one citable condition per
config at best-F1@20m**; the non-headline thresholds stay unclaimed (deferred to
the ``_ignored_evals`` close-out).

Configs
-------
* ``retest-phase3a`` / ``-high`` / ``-replication``: one condition per
  (cell × N) where N ∈ {5, 10, 30}; cell = (track × temperature) for phase3a /
  -high, or (thinking-level) for -replication. Pool = the physical 30-run cell.
* ``retest-phase3c``: one condition per (track × H9 condition) diversity pool
  (N=5, the cross-variant pool). Passes = the 45 physical pass-variant dirs;
  the condition's ``proposer_pool`` names the diversity grouping (which is not a
  single physical pool — a benign ``pool-unresolved`` signal, GAP-6).

Usage
-----
    # Print the operating-point table + condition_ids (writes nothing)
    python scripts/author_phase3_conditions.py

    # Merge the four runs' blocks into results/run-conditions.json
    python scripts/author_phase3_conditions.py --write

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-06-07
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_post_run_report as g  # noqa: E402

RESCORE = REPO_ROOT / "results" / "rescore-2026-06-07"
CONDITIONS_JSON = REPO_ROOT / "results" / "run-conditions.json"

# (run_id, directory_path, [(cell_rel_path, modality, temp_or_thinking)]).
PHASE3A_RUNS = {
    "retest-phase3a": [
        ("track1-image/T0.3", "image", "t0.3"),
        ("track1-image/T0.7", "image", "t0.7"),
        ("track1-image/T1.0", "image", "t1.0"),
        ("track2-text/T0.3", "text", "t0.3"),
        ("track2-text/T0.7", "text", "t0.7"),
        ("track2-text/T1.0", "text", "t1.0"),
    ],
    "retest-phase3a-high": [
        ("track2-text/T0.3", "text", "high-t0.3"),
        ("track2-text/T0.7", "text", "high-t0.7"),
        ("track2-text/T1.0", "text", "high-t1.0"),
    ],
    "retest-phase3a-replication": [
        ("high", "text", "high-t0.7"),
        ("minimal", "text", "minimal-t0.7"),
    ],
}
N_SUBDIR = {5: "consensus-n5", 10: "consensus-n10", 30: "consensus"}

PHASE3C_CONDITIONS = {
    "track1-image": ("image", ["A", "B", "C", "D", "E"]),
    "track2-text": ("text", ["A", "B", "D", "E"]),
}


def _cell_slug(run_dir: str, cell_rel: str) -> str:
    """`phase3a` + `track2-text/T0.3` -> `phase3a__track2-text__T0.3`."""
    base = run_dir.replace("outputs/retest/", "")
    return f"{base}__{cell_rel}".replace("/", "__")


def read_f1_mcc(eval_dir: Path) -> tuple[float, dict] | None:
    """Return (F1@20m point, MCC dict) from a re-score eval dir, or None."""
    ev = eval_dir / "evaluation.json"
    if not ev.exists():
        return None
    d = json.loads(ev.read_text())
    buffers = d.get("summary", {}).get("buffers", [])
    b20 = next(
        (b for b in buffers if b.get("buffer_metres") == 20), None
    )
    if b20 is None:
        return None
    f1 = b20.get("f1_point")
    # Guard None / NaN: an evaluator emits NaN F1 in degenerate zero-detection
    # cases. Returning it would let it win _best_threshold's first-set branch
    # (NaN > x and x > NaN are both False, so it could never be beaten), silently
    # selecting a NaN operating point. Treat as "no usable score" instead.
    if f1 is None or math.isnan(f1):
        return None
    mcc = d.get("summary", {}).get("tile_classification", {}).get("mcc", {})
    return f1, mcc


def _best_threshold(eval_glob_dir: Path, label_prefix: str, n: int):
    """Pick the threshold (1..n) with the highest F1@20m for one config.

    Returns (best_t, best_f1, mcc_point) or None if no evals found.
    """
    best = None
    for t in range(1, n + 1):
        res = read_f1_mcc(eval_glob_dir / f"{label_prefix}__t{t}")
        if res is None:
            continue
        f1, mcc = res
        if best is None or f1 > best[1]:
            best = (t, f1, (mcc.get("point") if isinstance(mcc, dict) else mcc))
    return best


def build_phase3a(run_id: str, run_dir: str, cells) -> tuple[dict, list, list]:
    """Build (proposer_pools, conditions, rows) for one phase3a-family run."""
    pools: dict[str, dict] = {}
    conditions: list[dict] = []
    rows: list[str] = []
    for cell_rel, modality, tag in cells:
        # Labels feed condition_id / pass_id, which the manifest schema
        # constrains to [a-z0-9._-]; lowercase the label, keep the real-case path.
        pool_label = cell_rel.replace("/", "-").lower()
        pools[pool_label] = {"modality": modality, "path": cell_rel}
        for n, subdir in sorted(N_SUBDIR.items()):
            slug = _cell_slug(run_dir, cell_rel)
            best = _best_threshold(RESCORE / "phase3", f"{slug}__n{n}", n)
            if best is None:
                rows.append(f"  MISSING {slug} n{n}")
                continue
            t, f1, mcc = best
            label = f"{modality}-{tag}-n{n}-{t}of{n}"
            cons_subdir = subdir
            detections = f"{run_dir}/{cell_rel}/{cons_subdir}/consensus_t{t}.geojson"
            eval_path = (
                f"results/rescore-2026-06-07/phase3/{slug}__n{n}__t{t}/"
                "evaluation.json"
            )
            conditions.append({
                "label": label,
                "architecture": "consensus",
                "aggregation": "consensus",
                "proposer_pool": pool_label,
                "n_passes": n,
                "vote_threshold": t,
                "prob_threshold": None,
                "verifier_config": None,
                "eval_path": eval_path,
                "detections": detections,
            })
            rows.append(
                f"  {run_id}::{label}  best t{t}/{n}  F1@20m={f1:.4f}  "
                f"MCC={mcc:.4f}" if mcc is not None else
                f"  {run_id}::{label}  best t{t}/{n}  F1@20m={f1:.4f}  MCC=NA"
            )
    return pools, conditions, rows


def build_phase3c() -> tuple[dict, list, list]:
    """Build (proposer_pools, conditions, rows) for retest-phase3c."""
    pools: dict[str, dict] = {}
    conditions: list[dict] = []
    rows: list[str] = []
    # Register the 45 physical pass-variant pools (the 225 passes).
    for track, (modality, conds) in PHASE3C_CONDITIONS.items():
        for cond in conds:
            for variant in _sub_conditions(track, cond):
                # lowercase the label (schema), keep the real-case dir path
                plabel = f"{track}-{variant}".lower()
                pools[plabel] = {
                    "modality": modality, "path": f"{track}/{variant}",
                }
    # One diversity condition per (track × H9 condition).
    for track, (modality, conds) in PHASE3C_CONDITIONS.items():
        for cond in conds:
            best = _best_threshold(
                RESCORE / "phase3c", f"phase3c__{track}__{cond}", 5
            )
            if best is None:
                rows.append(f"  MISSING phase3c {track} {cond}")
                continue
            t, f1, mcc = best
            label = f"{modality}-h9-{cond}-diversity-{t}of5".lower()
            eval_path = (
                f"results/rescore-2026-06-07/phase3c/"
                f"phase3c__{track}__{cond}__t{t}/evaluation.json"
            )
            conditions.append({
                "label": label,
                "architecture": "consensus",
                "aggregation": "consensus",
                "proposer_pool": f"{track}-h9-{cond}-diversity".lower(),
                "n_passes": 5,
                "vote_threshold": t,
                "prob_threshold": None,
                "verifier_config": None,
                "eval_path": eval_path,
                "detections": (
                    f"outputs/retest/phase3c/diversity-consensus/{track}/{cond}"
                ),
            })
            rows.append(
                f"  retest-phase3c::{label}  best t{t}/5  F1@20m={f1:.4f}  "
                + (f"MCC={mcc:.4f}" if mcc is not None else "MCC=NA")
            )
    return pools, conditions, rows


def _sub_conditions(track: str, cond: str) -> list[str]:
    """The 5 pass-variant dir names for one H9 condition (from the study YAML)."""
    import yaml
    track_num = "track1" if "image" in track else "track2"
    yaml_path = REPO_ROOT / "studies" / f"phase3c-h9-diversity-{track_num}.yaml"
    study = yaml.safe_load(yaml_path.read_text())
    return study["consensus_design"]["conditions"][cond]["sub_conditions"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Author phase3 manifest conditions (dry-run by default)."
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Merge the four runs' blocks into results/run-conditions.json.",
    )
    args = parser.parse_args(argv)

    blocks: dict[str, dict] = {}
    all_rows: list[str] = []
    cond_ids: dict[str, list[str]] = {}

    # Authoritative run directory from the registry (not string-derived), so the
    # detections paths the conditions reference match what the verifier resolves.
    registry = {
        e["run_id"]: e
        for e in g.load_run_registry().get("registry", [])
    }

    for run_id, cells in PHASE3A_RUNS.items():
        run_dir = registry[run_id]["directory_path"].rstrip("/")
        pools, conditions, rows = build_phase3a(run_id, run_dir, cells)
        blocks[run_id] = {"proposer_pools": pools, "conditions": conditions}
        all_rows += [f"\n=== {run_id} ==="] + rows
        cond_ids[run_id] = [f"{run_id}::{c['label']}" for c in conditions]

    pools, conditions, rows = build_phase3c()
    blocks["retest-phase3c"] = {
        "proposer_pools": pools, "conditions": conditions,
    }
    all_rows += ["\n=== retest-phase3c ==="] + rows
    cond_ids["retest-phase3c"] = [
        f"retest-phase3c::{c['label']}" for c in conditions
    ]

    print("OPERATING POINTS (best-F1@20m per config):")
    print("\n".join(all_rows))
    n_cond = sum(len(b["conditions"]) for b in blocks.values())
    n_pool = sum(len(b["proposer_pools"]) for b in blocks.values())
    print(f"\nTotal: {n_cond} conditions, {n_pool} proposer_pools "
          f"across {len(blocks)} runs.")
    print("\nCondition IDs (for analysis authoring):")
    print(json.dumps(cond_ids, indent=2))

    if not args.write:
        print("\nDRY-RUN — run-conditions.json not modified. Use --write.")
        return 0

    doc = json.loads(CONDITIONS_JSON.read_text())
    notes = {
        "retest-phase3a": "H3 consensus vote-threshold x N sweep, MINIMAL "
        "thinking (the original phase3a accidentally ran minimal — see "
        "retest-phase3a-replication). 2 tracks x 3 temps; N in {5,10,30} (first-N "
        "sub-pools). One citable condition per (cell x N) at best-F1@20m; "
        "non-headline thresholds -> deferred _ignored_evals. 14-buf+MCC re-score, "
        "Era-1 340-tile, curator GT, gemini-3-flash.",
        "retest-phase3a-high": "H3 consensus sweep, HIGH thinking, text track "
        "only (image track never ran). 3 temps; N in {5,10,30}. One condition "
        "per (cell x N) at best-F1@20m. 14-buf+MCC, Era-1 340, curator GT.",
        "retest-phase3a-replication": "H3 clean HIGH-vs-MINIMAL thinking "
        "replication at T0.7 text (built because the original phase3a HIGH/min "
        "both used minimal). 2 cells (high, minimal); N in {5,10,30}. One "
        "condition per (cell x N) at best-F1@20m. 14-buf+MCC, Era-1 340.",
        "retest-phase3c": "H9 diversity study (REJECTED — no diversity mechanism "
        "gives a significant gain). One condition per (track x H9 condition) "
        "cross-variant diversity pool (N=5, replicate-mean over 5 replications). "
        "45 physical pass-variant pools registered as passes; the condition's "
        "proposer_pool names the diversity grouping (GAP-6: not a single physical "
        "pool -> benign pool-unresolved). 14-buf+MCC, Era-1 340, curator GT.",
    }
    had_ignored = False
    for run_id, block in blocks.items():
        existing = doc["decomposition"].get(run_id, {})
        new_block = {
            "_note": notes[run_id],
            "proposer_pools": block["proposer_pools"],
            "verifier_passes": {},
            "conditions": block["conditions"],
        }
        # Preserve a sibling _ignored_evals close-out (author_ignored_evals.py)
        # rather than silently dropping it by wholesale block replacement. NB if
        # the conditions/operating-points changed, the preserved set may be stale
        # -> re-run author_ignored_evals.py to recompute (see reminder below).
        if "_ignored_evals" in existing:
            new_block["_ignored_evals"] = existing["_ignored_evals"]
            had_ignored = True
        doc["decomposition"][run_id] = new_block
    CONDITIONS_JSON.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"\nWROTE {len(blocks)} run blocks to {CONDITIONS_JSON.relative_to(REPO_ROOT)}")
    if had_ignored:
        print("NOTE: preserved existing _ignored_evals. If operating points "
              "changed, re-run scripts/author_ignored_evals.py --write to "
              "recompute the waiver set.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
