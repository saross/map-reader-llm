#!/usr/bin/env python3
# ============================================================================
# author_sweep_promotions.py
# ----------------------------------------------------------------------------
# Session 113 ($0): promote the 16 promotable completeness-sweep cells to
# first-class pv-diag-384 conditions (Shawn, 2026-06-12: "make everything
# that can be first-class first-class"). Sweep cells 1-2 are excluded —
# #1's optimum IS the registered headline condition and #2 was minted
# earlier this session.
#
# DATA-DRIVEN from the committed sweep record
# (results/verifier-robustness/unswept_pools_sweep.json) plus the
# cell -> condition-label mapping in scripts/materialise_sweep_cells.py,
# so the three artefact layers (sweep record, materialised set, condition)
# cannot drift apart by transcription.
#
# Also updates the SIGNED unswept-pools-completeness analysis to record
# the promotion decision (conditions_compared extended; _note rewritten;
# manually_verified_at refreshed to the supplied timestamp — the decision
# was made interactively by Shawn in the same session).
#
# VALIDATION GATES (per the S111 pattern; the script refuses to write on
# any failure): artefacts exist; eval F1@20m reproduces the sweep record
# to 4 d.p.; n_detections == geojson feature count; no label collisions.
#
# DRY-RUN BY DEFAULT — pass --execute to write. After executing:
# generate_post_run_report.py --all --write, then the drift-check.
#
# Usage:
#   .venv/bin/python scripts/author_sweep_promotions.py
#   .venv/bin/python scripts/author_sweep_promotions.py --execute --signed-at <ISO8601>
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-12 | Apache 2.0
# ============================================================================
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.materialise_sweep_cells import CONDITION_LABELS  # noqa: E402

SWEEP = BASE_DIR / "results/verifier-robustness/unswept_pools_sweep.json"
CONDS = BASE_DIR / "results" / "run-conditions.json"
ANALYSES = BASE_DIR / "results" / "run-analyses.json"
VR = "results/verifier-robustness"

FLASH_VF = {"variant": "v1", "instruction_file": "verify_adversarial.md",
            "model": "gemini-3-flash-preview"}
PRO_VF = {"variant": "v1", "instruction_file": "verify_adversarial.md",
          "model": "gemini-3.1-pro-preview"}


def vconf_for(verifier_desc: str) -> dict:
    """Map a sweep cell's verifier description to a verifier_config."""
    if "gemini-3.1-pro" in verifier_desc:
        base, thinking = PRO_VF, "medium"
    elif "medium" in verifier_desc:
        base, thinking = FLASH_VF, "medium"
    else:
        base, thinking = FLASH_VF, "minimal"
    return {**base, "thinking_level": thinking, "temperature": 0.0,
            "iterations": 1}


def build_conditions() -> list[tuple[dict, float]]:
    """Assemble the 16 condition entries (each with its expected F1)."""
    cells = {c["label"]: c
             for c in json.loads(SWEEP.read_text())["cells"]}
    out = []
    for sweep_label, cond_label in CONDITION_LABELS.items():
        cell = cells[sweep_label]
        m = re.fullmatch(r"(\d+)of(\d+)/pt([0-9.]+)", cell["best_op"])
        if not m:
            sys.exit(f"cannot parse best_op {cell['best_op']!r}")
        vote_t, n_passes, prob_t = int(m.group(1)), int(m.group(2)), float(m.group(3))
        # Pool name = the crops directory in the sweep record's manifest path.
        pool = Path(cell["manifest"]).parent.name
        cond = {
            "label": cond_label,
            "architecture": "proposer-verifier",
            "aggregation": "verified",
            "proposer_pool": pool,
            "n_passes": n_passes,
            "vote_threshold": vote_t,
            "prob_threshold": prob_t,
            "verifier_config": vconf_for(cell["verifier"]),
            "eval_path": f"{VR}/evals/{cond_label}/evaluation.json",
            "detections": f"{VR}/sweep-sets/{cond_label}.geojson",
            "_note": (f"Completeness-sweep promotion (Shawn, 2026-06-12: "
                      f"everything first-class). Sweep cell: {sweep_label!r} "
                      f"(unswept_pools_sweep.json; Obs 363)."),
        }
        out.append((cond, cell["f1_20m"]))
    return out


def gate(cond: dict, expect_f1: float) -> list[str]:
    """Validate one condition's artefacts; return a list of failures."""
    fails = []
    det = BASE_DIR / cond["detections"]
    ev = BASE_DIR / cond["eval_path"]
    if not det.exists():
        return [f"{cond['label']}: detections MISSING"]
    if not ev.exists():
        return [f"{cond['label']}: evaluation MISSING"]
    n_feat = len(json.loads(det.read_text())["features"])
    summary = json.loads(ev.read_text())["summary"]
    b20 = next(b for b in summary["buffers"] if b["buffer_metres"] == 20)
    if round(b20["f1"], 4) != round(expect_f1, 4):
        fails.append(f"{cond['label']}: eval F1@20m {b20['f1']:.4f} != "
                     f"sweep {expect_f1}")
    if summary["n_detections"] != n_feat:
        fails.append(f"{cond['label']}: n_detections {summary['n_detections']}"
                     f" != geojson features {n_feat}")
    return fails


def main() -> int:
    """Validate, then author conditions + the analysis update."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", action="store_true",
                    help="Write the sidecar files (default: dry-run).")
    ap.add_argument("--signed-at", type=str, default=None,
                    help="ISO8601 timestamp for re-signing the updated "
                         "unswept-pools-completeness analysis (required "
                         "with --execute).")
    args = ap.parse_args()
    if args.execute and not args.signed_at:
        sys.exit("--execute requires --signed-at (Shawn's re-sign timestamp).")

    conds = json.loads(CONDS.read_text())
    analyses = json.loads(ANALYSES.read_text())
    new_conds = build_conditions()

    failures = []
    existing = {c["label"]
                for c in conds["decomposition"]["pv-diag-384"]["conditions"]}
    for cond, f1 in new_conds:
        failures.extend(gate(cond, f1))
        if cond["label"] in existing:
            failures.append(f"pv-diag-384 already has '{cond['label']}'")
    entry = next(a for a in analyses["analyses"]
                 if a["analysis_id"] == "unswept-pools-completeness")
    if failures:
        print("VALIDATION FAILURES:", flush=True)
        for f in failures:
            print(f"  - {f}", flush=True)
        return 1

    print(f"All gates pass: {len(new_conds)} pv-diag-384 promotions.",
          flush=True)
    if not args.execute:
        print("\nDRY-RUN (no files written). Re-run with --execute to author.",
              flush=True)
        return 0

    # -- write -----------------------------------------------------------
    conds["decomposition"]["pv-diag-384"]["conditions"].extend(
        c for c, _ in new_conds)
    new_ids = [f"pv-diag-384::{c['label']}" for c, _ in new_conds]
    entry["conditions_compared"] = sorted(
        set(entry["conditions_compared"]) | set(new_ids))
    entry["_note"] = (
        "Completeness sweep (S112-113 / Obs 363): all 18 never-PV-swept "
        "proposer pools under outputs/h11/pv-diag-384 scored at their best "
        "(proposer-k x prob_t) operating points "
        "(scripts/sweep_unswept_pools.py; "
        "results/verifier-robustness/unswept_pools_sweep.json, "
        "pro_vf_permutations.json). DISPOSITION (Shawn, 2026-06-12: make "
        "everything that can be first-class first-class): 17 of the 18 "
        "sweep cells are now first-class pv-diag-384 conditions — cell #2 "
        "minted in the morning wave (verified-adv-text-pro-vf-4of5), the "
        "other 16 in this promotion "
        "(scripts/author_sweep_promotions.py); cell #1 is NOT separately "
        "minted because its optimum IS the registered headline "
        "(verified-adv-text-consensus-16of30 — promotion would duplicate "
        "it). Like pv-diag-384-consensus-calibration, this registers "
        "completeness material, not a finding board.")
    entry["manually_verified_at"] = args.signed_at

    CONDS.write_text(json.dumps(conds, indent=2) + "\n")
    ANALYSES.write_text(json.dumps(analyses, indent=2) + "\n")
    print(f"Wrote run-conditions.json (+16 conditions) and "
          f"run-analyses.json (analysis updated, re-signed {args.signed_at})."
          "\nNext: generate_post_run_report.py --all --write, then the "
          "drift-check.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
