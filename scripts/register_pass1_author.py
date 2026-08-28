#!/usr/bin/env python3
"""
Registration Pass 1: author the three run entries (PI-approved scope).

Adds to `results/run-registry.json` and `results/run-conditions.json`:

- `stride-phaseb-2026-08-25` — four geometry cells × 10 passes, their
  union-k10 verifications, the winner-ladder exact verifications
  (k1/k3/k5), 4 verified-best conditions + 3 ladder-rung conditions.
- `stride-phasec-2026-08-25` — ov240 × 10, its verification, 1
  verified-best condition.
- `stride-55map-2026-08-25` — deployment Runs A and B, the 96,195-call
  verifier, 4 conditions (two carried primaries, two canonical-GT
  deployment oracles).

Best operating points are read PROGRAMMATICALLY from the committed
boards (`results/stride-2026-08-25/stride_verifier_analysis.json`,
`plateau_analyses.json`, `results/stride55-2026-08-27/
sweep_oracle.json`) — nothing hand-typed. Every eval_path and
detections path is checked to exist before anything is written; the
script REFUSES to run if any target key already exists (idempotence
by refusal, per the hand-verified registry discipline). Sweep-interior
points are deliberately NOT registered (PI ruling 2026-08-28):
they remain governed by their analysis rows, promoted on citation.

Usage::

    python scripts/register_pass1_author.py           # dry run (prints)
    python scripts/register_pass1_author.py --write

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RC = REPO / "results/run-conditions.json"
RR = REPO / "results/run-registry.json"

VF_CONFIG = {
    "variant": "v1",
    "instruction_file": "verify_adversarial.md",
    "model": "gemini-3-flash-preview",
    "thinking_level": "minimal",
    "temperature": 0.0,
}
CARRY_NOTE = ("Carry-forward verifier (verify_adversarial-text, T=0.0, "
              "MINIMAL, n=1) over the full K=10 union.")


def cell_condition(cell: str, board: dict, k_total: int = 10) -> dict:
    b = board[cell]
    dashed = cell.replace("_", "-")
    return {
        "label": f"{dashed}-k{k_total}-verified-p{b['prob_t']:.2f}"
                 f"-k{b['min_votes']}",
        "architecture": "proposer-verifier",
        "aggregation": "verified",
        "proposer_pool": cell,
        "n_passes": k_total,
        "vote_threshold": b["min_votes"],
        "prob_threshold": b["prob_t"],
        "verifier_config": dict(VF_CONFIG),
        "eval_path": f"results/stride-2026-08-25/conditions-verified/"
                     f"{cell}/eval/evaluation.json",
        "detections": f"results/stride-2026-08-25/conditions-verified/"
                      f"{cell}/detections.geojson",
        "_note": (f"Stride-programme verified best point "
                  f"(13-cell board member, F1@20 {b['f1']:.4f}). "
                  + CARRY_NOTE),
    }


def build() -> tuple[list[dict], dict[str, dict]]:
    sva = json.loads((REPO / "results/stride-2026-08-25/"
                      "stride_verifier_analysis.json").read_text())
    boards = sva["boards"]
    wl = json.loads((REPO / "results/stride-2026-08-25/"
                     "plateau_analyses.json").read_text()
                    )["winner_ladder_exact"]["N"]
    sweep55 = json.loads((REPO / "results/stride55-2026-08-27/"
                          "sweep_oracle.json").read_text())["runs"]

    phaseb_cells = ["g512_ov176", "g384_ov128", "g256_ov064", "g512_ov320"]
    phaseb = {
        "_note": ("Stride programme Phase B (overnight 2026-08-25, "
                  "PI-approved): four iso-stride geometry cells, K=10 "
                  "brief-text MINIMAL T=0.7 flex. Winner-ladder exact "
                  "verifications (k1/k3/k5, ~$3.4, PI-approved) nest "
                  "here. Sweep interiors live under the "
                  "stride-plateau analyses (PI ruling 2026-08-28)."),
        "proposer_pools": {c: {"modality": "text", "path": c}
                           for c in phaseb_cells},
        "verifier_passes": {
            **{f"{c}-union-k10-verify":
               {"modality": "text", "path": f"verifier/{c}/verify"}
               for c in phaseb_cells},
            **{f"g384_ov128-union-k{n}-verify":
               {"modality": "text",
                "path": f"verifier/g384_ov128/verify_k{n}"}
               for n in (1, 3, 5)},
        },
        "conditions": [cell_condition(c, boards) for c in phaseb_cells],
    }
    for n in (1, 3, 5):
        b = wl[str(n)]["best"]
        phaseb["conditions"].append({
            "label": f"g384-ov128-ladder-n{n}-verified-"
                     f"p{b['prob_t']:.2f}-k{b['min_votes']}",
            "architecture": "proposer-verifier",
            "aggregation": "verified",
            "proposer_pool": "g384_ov128",
            "n_passes": n,
            "vote_threshold": b["min_votes"],
            "prob_threshold": b["prob_t"],
            "verifier_config": dict(VF_CONFIG),
            "eval_path": f"results/stride-2026-08-25/conditions-verified/"
                         f"g384_ov128-ladder-n{n}/eval/evaluation.json",
            "detections": f"results/stride-2026-08-25/conditions-verified/"
                          f"g384_ov128-ladder-n{n}/detections.geojson",
            "_note": (f"Winner-ladder exact rung (first-{n} passes, "
                      f"exact re-verification; F1@20 {b['f1']:.4f}, "
                      f"union {wl[str(n)]['union_n']}). " + CARRY_NOTE),
        })

    phasec = {
        "_note": ("Stride programme Phase C (2026-08-25): the 384/62.5% "
                  "rung-144 cell, K=10, same protocol as Phase B."),
        "proposer_pools": {"g384_ov240": {"modality": "text",
                                          "path": "g384_ov240"}},
        "verifier_passes": {"g384_ov240-union-k10-verify":
                            {"modality": "text",
                             "path": "verifier/g384_ov240/verify"}},
        "conditions": [cell_condition("g384_ov240", boards)],
    }

    s55_cells = {"g384_ov128_55map": "A", "g384_ov192_55map": "B"}
    s55 = {
        "_note": ("55-map deployment portfolio (card "
                  "planning/55map-portfolio-2026-08-25.md; predictions "
                  "P1-P8 registered by commit before launch). Runs A "
                  "(384/33.3%, 141,600 calls) and B (384/50%, 245,610) "
                  "+ the 96,195-call carry-forward verifier. Canonical "
                  "extended-GT evaluations; the standardised-reference "
                  "final-board cells register in Pass 2. Sweeps/ladders "
                  "live under their analyses (PI ruling 2026-08-28)."),
        "proposer_pools": {c: {"modality": "text", "path": c}
                           for c in s55_cells},
        "verifier_passes": {
            f"{c}-union-k10-verify":
            {"modality": "text", "path": f"verifier/{c}/verify"}
            for c in s55_cells},
        "conditions": [],
    }
    from scripts.stride55_sweep_oracle import RUNS as S55RUNS  # noqa: E402
    for cell, tag in s55_cells.items():
        pt, pk = S55RUNS[cell]["primary"]
        o = sweep55[cell]["oracle"]
        dashed = cell.replace("_", "-")
        s55["conditions"].append({
            "label": f"{dashed}-verified-carried-p{pt:.2f}-k{pk}"
                     "-canonical-gt",
            "architecture": "proposer-verifier",
            "aggregation": "verified",
            "proposer_pool": cell,
            "n_passes": 10,
            "vote_threshold": pk,
            "prob_threshold": pt,
            "verifier_config": dict(VF_CONFIG),
            "eval_path": f"results/stride55-2026-08-27/{cell}/primary/"
                         "eval/summary.json",
            "detections": f"results/stride55-2026-08-27/{cell}/primary/"
                          "verified_detections.geojson",
            "_note": (f"Run {tag} PRIMARY (the carried deployment "
                      "claim, committed before the sweep). Corrected-F1 "
                      "vs canonical extended GT. " + CARRY_NOTE),
        })
        s55["conditions"].append({
            "label": f"{dashed}-verified-oracle-p{o['prob_t']:.2f}"
                     f"-k{o['min_votes']}-canonical-gt",
            "architecture": "proposer-verifier",
            "aggregation": "verified",
            "proposer_pool": cell,
            "n_passes": 10,
            "vote_threshold": o["min_votes"],
            "prob_threshold": o["prob_t"],
            "verifier_config": dict(VF_CONFIG),
            "eval_path": f"results/stride55-2026-08-27/{cell}/oracle/"
                         "eval/summary.json",
            "detections": f"results/stride55-2026-08-27/{cell}/oracle/"
                          "verified_detections.geojson",
            "_note": (f"Run {tag} deployment ORACLE (sweep argmax @50m, "
                      f"corrected-F1 {o['corrected_f1']:.4f}; post-hoc "
                      "basis, labelled). " + CARRY_NOTE),
        })

    registry_rows = [
        {"run_id": "stride-phaseb-2026-08-25",
         "directory_path": "outputs/stride-phaseb-2026-08-25",
         "status": "active",
         "notes": ("Stride Phase B: 4 geometry cells x10 passes + "
                   "union verifications + winner-ladder exact "
                   "verifications. Registered S143 (Pass 1).")},
        {"run_id": "stride-phasec-2026-08-25",
         "directory_path": "outputs/stride-phasec-2026-08-25",
         "status": "active",
         "notes": ("Stride Phase C: g384_ov240 x10 + verification. "
                   "Registered S143 (Pass 1).")},
        {"run_id": "stride-55map-2026-08-25",
         "directory_path": "outputs/stride-55map-2026-08-25",
         "status": "active",
         "notes": ("55-map deployment portfolio Runs A/B + 96,195-call "
                   "verifier. Registered S143 (Pass 1).")},
    ]
    return registry_rows, {
        "stride-phaseb-2026-08-25": phaseb,
        "stride-phasec-2026-08-25": phasec,
        "stride-55map-2026-08-25": s55,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    sys.path.insert(0, str(REPO))

    rows, decs = build()
    rc = json.loads(RC.read_text())
    rr = json.loads(RR.read_text())
    for key in decs:
        if key in rc["decomposition"]:
            raise SystemExit(f"REFUSED: {key} already in run-conditions")
        if any(r["run_id"] == key for r in rr["registry"]):
            raise SystemExit(f"REFUSED: {key} already in run-registry")

    missing = []
    n_conds = 0
    for key, d in decs.items():
        for c in d["conditions"]:
            n_conds += 1
            for f in ("eval_path", "detections"):
                if not (REPO / c[f]).exists():
                    missing.append(c[f])
        run_dir = REPO / dict((r["run_id"], r["directory_path"])
                              for r in rows)[key]
        for pool, spec in {**d["proposer_pools"],
                           **d["verifier_passes"]}.items():
            p = run_dir / spec["path"]
            if not p.exists():
                missing.append(str(p.relative_to(REPO)))
    if missing:
        raise SystemExit("REFUSED — missing artefacts:\n  "
                         + "\n  ".join(missing))
    print(f"3 runs, {n_conds} conditions, all artefact paths verified.")
    for key, d in decs.items():
        print(f"  {key}: {len(d['conditions'])} conditions — "
              + ", ".join(c["label"] for c in d["conditions"]))
    if not args.write:
        print("dry run — re-run with --write")
        return 0
    rc["decomposition"].update(decs)
    rr["registry"].extend(rows)
    RC.write_text(json.dumps(rc, indent=1) + "\n")
    RR.write_text(json.dumps(rr, indent=1) + "\n")
    print("WRITTEN: run-conditions.json + run-registry.json "
          "(regenerate manifests next)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
