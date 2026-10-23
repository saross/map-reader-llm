#!/usr/bin/env python3
"""
Materialise and score the registered GS verified conditions in one copy.

Part of the S164 restatement pass (``reports/s164-agent-records/
restatement-pass.md`` § 1.2), adapted from the 2026-10-13 re-score's
``conditions.py`` (``rescore-repaired-gs-scripts/``). After ``gs_chain.sh``
has regenerated the analyses, this regenerates the registered CONDITIONS
those analyses compare, whose ``evaluation.json`` the register, the Era-2
board, and the uplift tables read:

1. the five stride K = 10 cells (``results/stride-2026-08-25/
   conditions-verified/<cell>/``), each at its REGISTERED operating point
   (read from its label in ``results/run-conditions.json``), gated on the
   stride sweep's row at that point; the regenerated board's best point is
   recorded beside it (PI ruling D65 (3): a registered condition keeps its
   point; 512 px / 34.4 % is the one whose best point moved), and
   ``stride_verified_conditions.json`` is rewritten;
2. the three exact winner-ladder rungs (``g384_ov128-ladder-n{1,3,5}``),
   at their registered points (each equals the regenerated exact ladder's
   best point in the REPAIRED re-score; a difference is recorded, not
   hidden);
3. the nine ``best-eval/`` evaluations of the ``verified_best_20m.geojson``
   sets ``image_b_analysis.py`` wrote, each with its committed command-line
   arguments, after checking that the register condition reading the set
   is registered at the analysis's best point; where it is not (the 3.7
   image carried arm, registered (0.10, k5), best (0.05, k5)), the
   registered set ``verified_op_20m.geojson`` (written by ``--operating-
   point``) is scored into ``op-eval/`` with the same arguments.

Each set is read under the leg rule in force (``MAP_READER_VERIFY_DIRS``
unset: the re-verified rows), written in the D16 pattern
(``grid_verifier_analysis.materialise_condition``), and scored by
``evaluate_detections.py`` (bootstrap 10,000, seed 42). A summary goes to
``<copy>/restatement-conditions.json`` (not committed; read by the
extractor). Exit status 1 if any gate fails; nothing is skipped silently.

Usage: python gs_conditions.py <copy_dir>

Zero API. Run inside a disposable copy on sapphire, never the shared
checkout.

Author: Shawn Ross, Claude Code (S164)
Licence: Apache 2.0
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

COPY = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(COPY))

import geopandas as gpd  # noqa: E402

from scripts.grid_verifier_analysis import (  # noqa: E402
    materialise_condition,
    verified_subset,
)
from scripts.stride_verifier_analysis import (  # noqa: E402
    COMMON_BOUNDS,
    load_stride_union_on_origin,
)

PY = str(Path.home() / "Code/map-reader-llm/.venv/bin/python")
GT = "inputs/vectors/references/mounds-reference.geojson"
GRID_BOUNDS = "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson"
STRIDE = COPY / "results/stride-2026-08-25"
CV = STRIDE / "conditions-verified"
REGISTER = json.loads((COPY / "results/run-conditions.json").read_text())["decomposition"]

#: Stride K = 10 cells, in the committed stride_verified_conditions.json
#: order, with the register run each condition sits under.
STRIDE_CELLS = [
    ("g512_ov176", "stride-phaseb-2026-08-25"),
    ("g384_ov128", "stride-phaseb-2026-08-25"),
    ("g256_ov064", "stride-phaseb-2026-08-25"),
    ("g512_ov320", "stride-phaseb-2026-08-25"),
    ("g384_ov240", "stride-phasec-2026-08-25"),
]

#: The registered best-eval sets (results dirs).
BEST_EVAL_DIRS = [
    "results/image-b-gs-2026-08-28",
    "results/image-b-gs-2026-08-28/high",
    "results/gemini37-screen-2026-08-28",
    "results/gemini37-screen-2026-08-28/k10",
    "results/gemini37-screen-2026-08-28/swap37",
    "results/gemini38-screen-2026-09-04/armV",
    "results/gemini37-fourth-cell/gs-leg",
    "results/gemini37-image-gs-2026-09-01/arm1",
    "results/gemini37-image-gs-2026-09-01/arm2",
]

#: Reproduction gate: a materialised set re-scored by evaluate_detections.py
#: must equal its sweep row to this F1 (grid_verifier_analysis's bound).
GATE_TOL = 5e-4

FAILURES: list[str] = []


def registered(run: str, prefix: str) -> dict[str, Any]:
    """Return the one register condition under ``run`` whose label starts with ``prefix``."""
    hits = [c for c in REGISTER[run]["conditions"]
            if c["label"].startswith(prefix) and c.get("aggregation") == "verified"]
    if len(hits) != 1:
        raise SystemExit(f"{run}: {len(hits)} verified conditions start {prefix!r}")
    return hits[0]


def evaluate(det: Path, out_dir: Path, buffers: list[int], label: str | None,
             bounds: str = GRID_BOUNDS) -> dict[str, Any]:
    """Score one set with evaluate_detections.py; return its 20 m row and MCC."""
    cmd = [PY, "scripts/evaluate_detections.py", "--detections", str(det.relative_to(COPY)),
           "--buffers", *[str(b) for b in buffers], "--ground-truth", GT,
           "--bounds", bounds, "--bootstrap", "10000", "--seed", "42", "--mcc",
           "--output-dir", str(out_dir.relative_to(COPY))]
    if label:
        cmd += ["--label", label]
    r = subprocess.run(cmd, cwd=COPY, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"evaluate_detections failed on {det}: {r.stderr[-1500:]}")
    doc = json.loads((out_dir / "evaluation.json").read_text())
    row = next(b for b in doc["summary"]["buffers"] if b["buffer_metres"] == 20)
    tc = doc["summary"].get("tile_classification", {})
    mcc = tc.get("mcc") if not isinstance(tc.get("mcc"), dict) else tc["mcc"].get("point")
    return {"f1": row["f1"], "precision": row["precision"], "recall": row["recall"],
            "f1_ci": [row.get("f1_ci_lower"), row.get("f1_ci_upper")], "tile_mcc": mcc,
            "n_detections": doc["summary"].get("n_detections")}


def sweep_row(rows: list[dict[str, str]], cell: str, prob_t: float, k: int) -> dict[str, str]:
    """The stride sweep's row for one cell at one point (exactly one, or exit)."""
    hit = [r for r in rows if r["cell"] == cell and int(r["min_votes"]) == k
           and abs(float(r["prob_t"]) - prob_t) < 1e-9]
    if len(hit) != 1:
        raise SystemExit(f"{cell}: {len(hit)} stride sweep rows at ({prob_t}, k{k})")
    return hit[0]


def gate(name: str, ok: bool, detail: str) -> None:
    """Record a gate outcome; failures are collected and fail the run."""
    print(("OK   " if ok else "FAIL ") + name + ": " + detail)
    if not ok:
        FAILURES.append(f"{name}: {detail}")


def main() -> int:
    bounds = gpd.read_file(COMMON_BOUNDS)
    summary: dict[str, Any] = {"stride_k10": {}, "winner_ladder": {}, "best_eval": {},
                               "op_eval": {}}

    # 1. Stride K = 10 cells at their registered points.
    analysis = json.loads((STRIDE / "stride_verifier_analysis.json").read_text())
    board = analysis["boards"]
    with (STRIDE / "stride_verifier_sweep.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    cells_out = []
    for cell, run in STRIDE_CELLS:
        cond = registered(run, f"{cell.replace('_', '-')}-k10-verified-p")
        point = {"prob_t": float(cond["prob_threshold"]), "min_votes": int(cond["vote_threshold"])}
        srow = sweep_row(rows, cell, point["prob_t"], point["min_votes"])
        gdf = load_stride_union_on_origin(cell, bounds)
        det = CV / cell / "detections.geojson"
        n = materialise_condition(gdf, point, det, bounds)
        ev = evaluate(det, CV / cell / "eval", [20], None)
        gate(f"stride {cell}", n == int(srow["n_detections"])
             and abs(ev["f1"] - float(srow["f1"])) < GATE_TOL,
             f"n {n} vs sweep {srow['n_detections']}; F1 {ev['f1']} vs sweep {srow['f1']}")
        b = board[cell]
        best = {"prob_t": b["prob_t"], "min_votes": b["min_votes"],
                "n_detections": b["n_detections"], "sweep_f1_at_20m": b["f1"]}
        is_best = (point["prob_t"], point["min_votes"]) == (b["prob_t"], b["min_votes"])
        cells_out.append({
            "cell": cell, "condition_label": cond["label"],
            "point": [point["prob_t"], point["min_votes"]],
            "n": n, "sweep_f1": float(srow["f1"]), "rescored_f1": ev["f1"],
            "ci": ev["f1_ci"], "reproduces": abs(ev["f1"] - float(srow["f1"])) < GATE_TOL,
            "registered_point_is_best": is_best, "best_point": best,
            "verifier_probabilities": gdf.attrs["verifier_probabilities"]})
        summary["stride_k10"][cell] = {"point": [point["prob_t"], point["min_votes"]], "n": n,
                                       "sweep_f1": float(srow["f1"]), **ev,
                                       "registered_point_is_best": is_best, "best_point": best}
    (CV / "stride_verified_conditions.json").write_text(json.dumps({
        "bootstrap": {"n_iterations": 10000, "seed": 42},
        "note": ("Each stride K = 10 condition at its REGISTERED operating point (its "
                 "register label), with the regenerated board's best point beside it. "
                 "Regenerated 2026-10-15 by the S164 restatement pass with the D62 (1) "
                 "re-verified rows; a registered condition keeps its point when the best "
                 "point moves (PI ruling D65 (3)). Driver: reports/s164-agent-records/"
                 "restatement-pass-scripts/gs_conditions.py."),
        "cells": cells_out}, indent=2) + "\n")

    # 2. The exact winner-ladder rungs at their registered points.
    exact = json.loads((STRIDE / "plateau_analyses.json").read_text())["winner_ladder_exact"]
    for n_str, row in exact["N"].items():
        n_passes = int(n_str)
        best = row["best"]
        cond = registered("stride-phaseb-2026-08-25", f"g384-ov128-ladder-n{n_passes}-verified-p")
        point = {"prob_t": float(cond["prob_threshold"]), "min_votes": int(cond["vote_threshold"])}
        is_best = (point["prob_t"], point["min_votes"]) == (best["prob_t"], best["min_votes"])
        gdf = load_stride_union_on_origin("g384_ov128", bounds,
                                          union_name=f"union_k{n_passes}.geojson",
                                          verify_dir=f"verify_k{n_passes}", n_passes=n_passes)
        sub = verified_subset(gdf, point["prob_t"], point["min_votes"])
        dest = CV / f"g384_ov128-ladder-n{n_passes}"
        det = dest / "detections.geojson"
        k = materialise_condition(gdf, point, det, bounds)
        ev = evaluate(det, dest / "eval", [20], None)
        if is_best:
            gate(f"ladder N{n_passes}", k == len(sub) == best["n_detections"]
                 and abs(ev["f1"] - best["f1"]) < GATE_TOL,
                 f"n {k} vs best {best['n_detections']}; F1 {ev['f1']} vs best {best['f1']}")
        else:
            gate(f"ladder N{n_passes}", k == len(sub),
                 f"registered {point} is not the best point {best['prob_t'], best['min_votes']}"
                 f" (recorded, not hidden); n {k}")
        summary["winner_ladder"][f"N{n_passes}"] = {
            "point": [point["prob_t"], point["min_votes"]], "n": k, "sweep_f1": best["f1"],
            **ev, "registered_point_is_best": is_best,
            "best_point": [best["prob_t"], best["min_votes"]]}

    # 3. The registered best-eval sets, each with its committed arguments.
    for rel in BEST_EVAL_DIRS:
        d = COPY / rel
        det_rel = f"{rel}/verified_best_20m.geojson"
        conds = [(run, c) for run, v in REGISTER.items() for c in v["conditions"]
                 if c.get("detections") == det_rel]
        best = json.loads((d / "analysis.json").read_text())["image_best"]
        best_pt = (best["prob_t"], best["min_votes"])
        args = json.loads((d / "best-eval/evaluation.json").read_text())["_metadata"]["cli_args"]
        ev = evaluate(d / "verified_best_20m.geojson", d / "best-eval", args["buffers"],
                      args.get("label"), args["bounds"])
        summary["best_eval"][rel] = {**ev, "best_point": list(best_pt)}
        gate(f"best-eval {rel}", abs(ev["f1"] - best["f1"]) < GATE_TOL,
             f"F1 {ev['f1']} vs analysis best {best['f1']}")
        gate(f"register {rel}", bool(conds), f"{len(conds)} condition(s) read {det_rel}")
        off_best: dict[tuple[float, int], list[str]] = {}
        for run, c in conds:
            reg_pt = (float(c["prob_threshold"]), int(c["vote_threshold"]))
            if reg_pt == best_pt:
                gate(f"registered {run}::{c['label']}", True, f"at the best point {best_pt}")
            else:
                off_best.setdefault(reg_pt, []).append(f"{run}::{c['label']}")
        for reg_pt, labels in off_best.items():
            # Registered off the best point: the registered set must have been
            # written by --operating-point at exactly that point.
            op = json.loads((d / "analysis.json").read_text()).get("operating_point")
            ok = op is not None and (op["prob_t"], op["min_votes"]) == reg_pt
            gate(f"registered {', '.join(labels)}", ok,
                 f"registered {reg_pt}, best {best_pt}; operating_point "
                 f"{None if op is None else (op['prob_t'], op['min_votes'])}")
            if not ok:
                continue
            op_label = f"{args['label']}-registered" if args.get("label") else None
            ev_op = evaluate(d / "verified_op_20m.geojson", d / "op-eval", args["buffers"],
                             op_label, args["bounds"])
            gate(f"op-eval {rel}", abs(ev_op["f1"] - op["f1"]) < GATE_TOL
                 and ev_op["n_detections"] == op["n_detections"],
                 f"F1 {ev_op['f1']} vs operating point {op['f1']}; "
                 f"n {ev_op['n_detections']} vs {op['n_detections']}")
            summary["op_eval"][rel] = {**ev_op, "registered_point": list(reg_pt),
                                       "conditions": labels}

    summary["failures"] = FAILURES
    (COPY / "restatement-conditions.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: {c: v.get("f1") for c, v in s.items()}
                      for k, s in summary.items() if isinstance(s, dict)}, indent=1))
    if FAILURES:
        print(f"{len(FAILURES)} gate(s) FAILED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
