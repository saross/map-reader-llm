#!/usr/bin/env python3
"""
Registration Pass 1: materialise the five missing condition artefacts.

PI-approved scope (2026-08-28): the winner-ladder exact rungs
(N ∈ {1, 3, 5}, cell g384_ov128) and the two 55-map canonical-GT
deployment oracles (A at (0.15, k7); B at (0.20, k9)). Every other
Pass-1 condition already has committed D16-pattern artefacts.

GATES (nothing written unless all pass):

- Rungs: join gates on each union_kN ↔ verify_kN pair; the subset at
  the registered best point must reproduce the committed
  `winner_ladder_exact` n_detections EXACTLY (411 / 380 / 394); after
  evaluation, F1@20 must sit within the 0.003 mechanism bound of the
  committed ladder F1 (0.8677 / 0.8911 / 0.8856).
- Oracles: subset counts must equal the committed sweep rows EXACTLY
  (A 4,639; B 4,639); the engine re-evaluation @50 m must reproduce
  the committed `sweep_oracle.json` oracle F1 to 1e-6
  (A 0.836237-class / B 0.850294-class — read from the JSON, not
  hard-coded).

Rung evaluations mirror the committed conditions-verified cli_args
(evaluate_detections, buffers 20, grid common bounds, curator GT,
BCa 10k seed 42, --mcc). Oracle evaluations use the 55-map engine
(`stride55_score.score`) exactly as the primaries did.

Usage::

    python scripts/register_pass1_materialise.py

Zero API. Run on sapphire (union/verify artefacts live there).

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.grid_analysis import CRS  # noqa: E402
from scripts.grid_verifier_analysis import JoinGateError  # noqa: E402
from scripts.stride55_sweep_oracle import (  # noqa: E402
    RUNS as STRIDE55_RUNS,
    load_candidates,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

VROOT = PROJECT_ROOT / "outputs/stride-phaseb-2026-08-25/verifier/g384_ov128"
CV = PROJECT_ROOT / "results/stride-2026-08-25/conditions-verified"
LADDER = json.loads((PROJECT_ROOT / "results/stride-2026-08-25"
                     / "plateau_analyses.json").read_text())
WL = LADDER["winner_ladder_exact"]["N"]
SWEEP55 = json.loads((PROJECT_ROOT / "results/stride55-2026-08-27"
                      / "sweep_oracle.json").read_text())
GRID_BOUNDS = ("outputs/grid-2026-08-18/scoring/bounds/"
               "grid_common_bounds.geojson")
GS_GT = "inputs/vectors/references/mounds-reference.geojson"


def rung(n: int) -> None:
    best = WL[str(n)]["best"]
    union = gpd.read_file(VROOT / f"union_k{n}.geojson").to_crs(CRS)
    probs = json.loads((VROOT / f"verify_k{n}" / "probabilities.json"
                        ).read_text())["results"]
    if len(probs) != len(union):
        raise JoinGateError(f"N={n}: {len(probs)} probs vs {len(union)}")
    if set(probs) != {f"candidate_{i:05d}" for i in range(len(union))}:
        raise JoinGateError(f"N={n}: keys not contiguous")
    union["mound_probability"] = [
        float(probs[f"candidate_{i:05d}"]["mound_probability"])
        for i in range(len(union))]
    sub = union[(union["mound_probability"] >= best["prob_t"])
                & (union["vote_count"] >= best["min_votes"])]
    if len(sub) != best["n_detections"]:
        raise JoinGateError(
            f"N={n}: subset {len(sub)} vs committed "
            f"{best['n_detections']}")
    dest = CV / f"g384_ov128-ladder-n{n}"
    dest.mkdir(parents=True, exist_ok=True)
    sub.to_crs("EPSG:4326").to_file(dest / "detections.geojson",
                                    driver="GeoJSON")
    r = subprocess.run(
        [".venv/bin/python", "scripts/evaluate_detections.py",
         "--detections", str((dest / "detections.geojson"
                              ).relative_to(PROJECT_ROOT)),
         "--buffers", "20", "--ground-truth", GS_GT,
         "--bounds", GRID_BOUNDS, "--bootstrap", "10000", "--seed", "42",
         "--mcc", "--output-dir",
         str((dest / "eval").relative_to(PROJECT_ROOT))],
        cwd=PROJECT_ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"N={n} eval failed: {r.stderr[-500:]}")
    ev = json.loads((dest / "eval/evaluation.json").read_text())["summary"]
    f1 = next(b for b in ev["buffers"] if b["buffer_metres"] == 20)["f1"]
    if abs(f1 - best["f1"]) > 0.003:
        raise RuntimeError(
            f"N={n}: eval {f1:.4f} vs ladder {best['f1']:.4f} "
            "outside the mechanism bound")
    logger.info("rung N=%d OK: n=%d, eval F1@20 %.4f (ladder %.4f)",
                n, len(sub), f1, best["f1"])


def oracle(cell: str) -> None:
    spec = STRIDE55_RUNS[cell]
    o = SWEEP55["runs"][cell]["oracle"]
    bounds = gpd.read_file(
        PROJECT_ROOT / "inputs/vectors/bounds/384/"
        "55maps_evaluation_bounds.geojson").to_crs(CRS)
    gdf = load_candidates(cell, spec, bounds)
    sub = gdf[(gdf["mound_probability"] >= o["prob_t"])
              & (gdf["vote_count"] >= o["min_votes"])]
    if len(sub) != o["n_detections"]:
        raise JoinGateError(
            f"{cell}: subset {len(sub)} vs committed {o['n_detections']}")
    dest = PROJECT_ROOT / "results/stride55-2026-08-27" / cell / "oracle"
    dest.mkdir(parents=True, exist_ok=True)
    det = dest / "verified_detections.geojson"
    sub.to_crs("EPSG:4326").to_file(det, driver="GeoJSON")
    # The engine invocation stride55_score.score uses, but into the
    # oracle's OWN eval dir (score() hardcodes the primary path and
    # would clobber the committed primary evaluation).
    from scripts.stride55_score import (
        BOUNDS as ENGINE_BOUNDS,
        CANONICAL_REVIEW as ENGINE_REVIEW,
        STUDENT_GT as ENGINE_GT,
        ensure_empty_yesterday,
    )
    cmd = [sys.executable,
           str(PROJECT_ROOT / "scripts/compute_corrected_f1_multi_buffer.py"),
           "--verified-detections", str(det),
           "--student-gt", str(ENGINE_GT),
           "--bounds", str(ENGINE_BOUNDS),
           "--review-yesterday", str(ensure_empty_yesterday()),
           "--review-today", str(ENGINE_REVIEW),
           "--output-dir", str(dest / "eval"),
           "--buffers", "20", "30", "50",
           "--n-bootstrap", "10000", "--seed", "42", "--compute-mcc"]
    r = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                       text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cell} oracle eval failed: {r.stderr[-500:]}")
    import csv
    f1_50 = None
    with (dest / "eval/corrected-f1.csv").open() as fh:
        for row in csv.DictReader(fh):
            if int(row["R_m"]) == 50:
                f1_50 = float(row["F1"])
    if f1_50 is None or abs(f1_50 - o["corrected_f1"]) > 1e-6:
        raise RuntimeError(
            f"{cell}: oracle eval {f1_50} vs sweep "
            f"{o['corrected_f1']:.6f}")
    logger.info("oracle %s OK: n=%d, corrected-F1@50 %.6f == sweep",
                cell, len(sub), f1_50)


def main() -> int:
    for n in (1, 3, 5):
        rung(n)
    for cell in ("g384_ov128_55map", "g384_ov192_55map"):
        oracle(cell)
    logger.info("PASS-1 MATERIALISATION COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
