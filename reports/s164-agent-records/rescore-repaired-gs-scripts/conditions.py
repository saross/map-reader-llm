#!/usr/bin/env python3
"""
Re-materialise and re-evaluate the registered verified conditions in one copy.

Part of the S164 re-score (``reports/s164-agent-records/rescore-repaired-gs.md``).
``chain.sh`` regenerates every analysis the 14 signed analyses read; this step
regenerates the registered CONDITIONS those analyses compare, whose
``evaluation.json`` the register, the Era-2 board, and the uplift tables read:

1. the five stride K = 10 cells (``results/stride-2026-08-25/conditions-verified/
   <cell>/``), at each cell's best point on the regenerated stride board;
2. the three exact winner-ladder rungs (``g384_ov128-ladder-n{1,3,5}``), at
   the regenerated ``winner_ladder_exact`` best points;
3. the nine ``best-eval/`` evaluations of the ``verified_best_20m.geojson``
   sets ``image_b_analysis.py`` wrote (Image-B MINIMAL and HIGH, the Gemini 3.7
   screen K = 5, K = 10 and swap37, Arm V, the fourth cell, and the two 3.7
   image arms), each with its committed command-line arguments.

Each set is read under the leg rule in force (``MAP_READER_VERIFY_DIRS``),
written in the D16 pattern (``grid_verifier_analysis.materialise_condition``:
candidate id, origin-sheet tile, and member tiles), and scored by
``evaluate_detections.py`` with the committed recipe (bootstrap 10,000,
seed 42). A summary of every condition is written to
``<copy>/rescore-conditions.json``.

Usage: python conditions.py <copy_dir>

Zero API. Run inside a disposable copy on sapphire, never the shared checkout.

Author: Shawn Ross, Claude Code (S164)
Licence: Apache 2.0
"""

from __future__ import annotations

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

#: The registered best-eval sets: results dir -> (the committed evaluation's
#: directory, read for its cli_args before it is overwritten).
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


def main() -> int:
    bounds = gpd.read_file(COMMON_BOUNDS)
    summary: dict[str, Any] = {"stride_k10": {}, "winner_ladder": {}, "best_eval": {}}

    # 1. Stride K = 10 cells at the regenerated board's best points.
    board = json.loads((STRIDE / "stride_verifier_analysis.json").read_text())["boards"]
    for cell in ("g512_ov176", "g384_ov128", "g256_ov064", "g512_ov320", "g384_ov240"):
        b = board[cell]
        gdf = load_stride_union_on_origin(cell, bounds)
        point = {"prob_t": b["prob_t"], "min_votes": b["min_votes"]}
        det = CV / cell / "detections.geojson"
        n = materialise_condition(gdf, point, det, bounds)
        ev = evaluate(det, CV / cell / "eval", [20], None)
        summary["stride_k10"][cell] = {"point": [b["prob_t"], b["min_votes"]], "n": n,
                                       "sweep_f1": b["f1"], **ev,
                                       "verifier_probabilities":
                                           gdf.attrs["verifier_probabilities"]}

    # 2. The exact winner-ladder rungs.
    exact = json.loads((STRIDE / "plateau_analyses.json").read_text())["winner_ladder_exact"]
    for n_str, row in exact["N"].items():
        n = int(n_str)
        best = row["best"]
        gdf = load_stride_union_on_origin("g384_ov128", bounds,
                                          union_name=f"union_k{n}.geojson",
                                          verify_dir=f"verify_k{n}", n_passes=n)
        sub = verified_subset(gdf, best["prob_t"], best["min_votes"])
        dest = CV / f"g384_ov128-ladder-n{n}"
        det = dest / "detections.geojson"
        k = materialise_condition(gdf, best, det, bounds)
        assert k == len(sub)
        ev = evaluate(det, dest / "eval", [20], None)
        summary["winner_ladder"][f"N{n}"] = {"point": [best["prob_t"], best["min_votes"]],
                                             "n": k, "sweep_f1": best["f1"], **ev,
                                             "verifier_probabilities":
                                                 gdf.attrs["verifier_probabilities"]}

    # 3. The registered best-eval sets, each with its committed arguments.
    for rel in BEST_EVAL_DIRS:
        d = COPY / rel
        meta = json.loads((d / "best-eval/evaluation.json").read_text())["_metadata"]
        args = meta["cli_args"]
        ev = evaluate(d / "verified_best_20m.geojson", d / "best-eval", args["buffers"],
                      args.get("label"), args["bounds"])
        summary["best_eval"][rel] = ev

    (COPY / "rescore-conditions.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: {c: v.get("f1") for c, v in s.items()} for k, s in summary.items()},
                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
