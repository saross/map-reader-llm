#!/usr/bin/env python3
# ============================================================================
# run_era1_pv_stage_d.py
# ----------------------------------------------------------------------------
# Stage D of the Era-1 leaderboard plan (planning/era1-leaderboard-plan-
# 2026-06-08.md): run the production adversarial verifier over already-generated
# proposer/consensus outputs to build a CLEAN proposer-verifier (PV) grid —
# tile size (256/384/512) x {consensus, single-pass} x {text, image} — within
# one model (gemini-3-flash), so the three-size consensus+PV row is internally
# consistent rather than spliced across eras.
#
# This is a GATED API run (Shawn approved: maximal cells, flex tier, ~$5 flex /
# ~$10 standard for 7,113 candidates). It wraps the canonical PV machinery
# (scripts/run_pv.py extract|verify; build_post_verifier_geojson.py;
# scripts/evaluate_detections.py) — it adds no new API surface, only orchestration
# + a probability-threshold sweep + 14-buffer+MCC scoring.
#
# THE FIVE CELLS (9 verifier passes, 7,113 candidates)
# ----------------------------------------------------
#   256-consensus-text-5of5     consensus     1,165   (the Obs-351 missing cell)
#   512-consensus-text-high     consensus       442   (Tier-1 text champion)
#   512-consensus-image         consensus       535   (best image consensus)
#   512-single-text-t0.0        single-pass   2,654   (K=3 passes; grid corner)
#   512-single-image-t0.0       single-pass   2,317   (K=3 passes; grid corner)
# Cells are read from planning/era1-pv-stage-d-cells.json. The 384 leg of the
# three-size row is the EXISTING proposer-verifier-384 (no new spend here).
#
# VERIFIER CONFIG (the production carry-forward)
# ----------------------------------------------
# prompts/configs/verify_adversarial-text.json: gemini-3-flash, adversarial,
# text-only labels, T=0.0, minimal thinking, n=1 (iterations=1). Realtime + flex
# (50% discount). Identical to the Era-2 proposer-verifier-384 verifier.
#
# MODES
# -----
#   --dry-run : `run_pv.py extract --dry-run` per proposer (validates rasters +
#               geojson resolve; NO API). Plus the cost summary.
#   --smoke   : subset each cell's first proposer to ~1 tile's worth of
#               candidates (--smoke-n, default 12), extract + verify (flex), and
#               report the probability distribution — a tiny end-to-end API check
#               (~60 calls total, ~$0.02) before the full launch.
#   --full    : extract + verify EVERY pass of every cell (flex).
#   --score   : materialise each pass at the prob_t sweep + score at 14-buffer +
#               MCC (consensus = single set; single-pass = replicate-mean over
#               the K passes), and report best-F1@20 m per cell.
#
# COMPUTE: extract/score are local ($0); verify is the Gemini API. Run on zbook.
#
# Usage:
#     python scripts/run_era1_pv_stage_d.py --dry-run
#     python scripts/run_era1_pv_stage_d.py --smoke --workers 12
#     python scripts/run_era1_pv_stage_d.py --full --workers 20
#     python scripts/run_era1_pv_stage_d.py --score
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-06-08
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CELLS = BASE_DIR / "planning" / "era1-pv-stage-d-cells.json"
DEFAULT_OUTROOT = BASE_DIR / "outputs" / "era1-pv-stage-d"
VERIFIER_CONFIG = BASE_DIR / "prompts" / "configs" / "verify_adversarial-text.json"
GROUND_TRUTH = BASE_DIR / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
# Each cell's evaluation bounds depend on its tile size (256 vs 512).
BOUNDS_BY_SIZE = {
    256: BASE_DIR / "inputs" / "vectors" / "bounds" / "256" / "full_evaluation_bounds.geojson",
    512: BASE_DIR / "inputs" / "vectors" / "bounds" / "full_evaluation_bounds.geojson",
}
BUFFERS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]
PADDING = 75  # 150 px crops, the carry-forward
RUN_PV = BASE_DIR / "scripts" / "run_pv.py"
BUILD_PV = BASE_DIR / "scripts" / "build_post_verifier_geojson.py"
EVAL = BASE_DIR / "scripts" / "evaluate_detections.py"


def cell_size(cell: dict) -> int:
    """Return a cell's tile size (parsed from its name prefix '256-'/'512-')."""
    return int(cell["name"].split("-", 1)[0])


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """Run a subprocess, echoing the command; raise on non-zero exit."""
    print("  $ " + " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=True, cwd=BASE_DIR, **kw)


def subset_geojson(src: Path, dst: Path, n: int) -> int:
    """Write the first ``n`` features of ``src`` to ``dst`` (smoke subset).

    Args:
        src: Source proposer GeoJSON.
        dst: Destination subset GeoJSON.
        n: Number of leading features to keep.

    Returns:
        The number of features written.
    """
    fc = json.loads(src.read_text())
    fc["features"] = fc["features"][:n]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(fc))
    return len(fc["features"])


def pass_dirs(cell: dict, outroot: Path) -> list[tuple[Path, Path, Path]]:
    """Return (proposer, crops_dir, verified_dir) per pass for a cell."""
    out = []
    for i, prop in enumerate(cell["proposers"], 1):
        base = outroot / cell["name"] / f"pass_{i}"
        out.append((BASE_DIR / prop, base / "crops", base / "verified"))
    return out


def do_dry_run(cells: list[dict], outroot: Path) -> None:
    """Validate every proposer extracts cleanly (no API) + print the cost table."""
    total = 0
    print("=== DRY RUN — extract --dry-run per proposer (no API) ===", flush=True)
    for cell in cells:
        print(f"\n--- {cell['name']} ({cell['kind']}, {cell['n']} candidates) ---", flush=True)
        total += cell["n"]
        for prop, crops, _verified in pass_dirs(cell, outroot):
            run([sys.executable, str(RUN_PV), "extract", "--proposer", str(prop),
                 "--output-dir", str(crops), "--padding", str(PADDING), "--dry-run"])
    flex = total * 0.000697
    print(f"\n=== {total} candidates total — est ${flex:.2f} flex / ${flex * 2:.2f} standard ===",
          flush=True)


def do_smoke(cells: list[dict], outroot: Path, n: int, workers: int) -> None:
    """Subset each cell to ~1 tile, extract + verify (flex), report probabilities."""
    print(f"=== SMOKE TEST — first {n} candidates per cell, flex verify ===", flush=True)
    for cell in cells:
        prop = BASE_DIR / cell["proposers"][0]
        base = outroot / "_smoke" / cell["name"]
        subset = base / "subset.geojson"
        k = subset_geojson(prop, subset, n)
        crops, verified = base / "crops", base / "verified"
        print(f"\n--- {cell['name']}: {k} candidates ---", flush=True)
        run([sys.executable, str(RUN_PV), "extract", "--proposer", str(subset),
             "--output-dir", str(crops), "--padding", str(PADDING)])
        run([sys.executable, str(RUN_PV), "verify", "--crops-dir", str(crops),
             "--verifier-config", str(VERIFIER_CONFIG), "--output-dir", str(verified),
             "--mode", "realtime", "--service-tier", "flex",
             "--workers", str(workers), "--iterations", "1"])
        _report_probabilities(verified / "probabilities.json")


def do_full(cells: list[dict], outroot: Path, workers: int) -> None:
    """Extract + verify (flex) every pass of every cell."""
    print("=== FULL RUN — extract + verify (realtime flex) ===", flush=True)
    for cell in cells:
        print(f"\n########## {cell['name']} ({cell['kind']}) ##########", flush=True)
        for prop, crops, verified in pass_dirs(cell, outroot):
            run([sys.executable, str(RUN_PV), "extract", "--proposer", str(prop),
                 "--output-dir", str(crops), "--padding", str(PADDING)])
            run([sys.executable, str(RUN_PV), "verify", "--crops-dir", str(crops),
                 "--verifier-config", str(VERIFIER_CONFIG), "--output-dir", str(verified),
                 "--mode", "realtime", "--service-tier", "flex",
                 "--workers", str(workers), "--iterations", "1"])
            _report_probabilities(verified / "probabilities.json")


def _report_probabilities(probs_path: Path) -> None:
    """Print a short sanity summary of a verifier probabilities.json."""
    if not probs_path.exists():
        print(f"  WARNING: no probabilities at {probs_path}", flush=True)
        return
    # Structure: {source, derived_from, vote_threshold, results: {cand_id: {...}}}.
    results = json.loads(probs_path.read_text()).get("results", {})
    probs = [v.get("mound_probability") for v in results.values()
             if isinstance(v, dict) and isinstance(v.get("mound_probability"), (int, float))]
    if not probs:
        print(f"  probabilities.json present but no mound_probability parsed "
              f"(inspect {probs_path})", flush=True)
        return
    n = len(probs)
    acc = sum(1 for p in probs if p >= 0.2)
    print(f"  probabilities: n={n}, mean={sum(probs)/n:.3f}, "
          f">=0.2 accepted={acc} ({100*acc/n:.0f}%), "
          f"min={min(probs):.3f} max={max(probs):.3f}", flush=True)


def do_score(cells: list[dict], outroot: Path, prob_sweep: list[float]) -> None:
    """Materialise each pass at the prob_t sweep + score at 14-buf+MCC."""
    print("=== SCORE — materialise (prob_t sweep) + 14-buffer+MCC ===", flush=True)
    summary = {}
    for cell in cells:
        size = cell_size(cell)
        bounds = BOUNDS_BY_SIZE[size]
        best = {"f1": -1.0}
        for prob_t in prob_sweep:
            accepted_paths = []
            for i, (prop, crops, verified) in enumerate(pass_dirs(cell, outroot), 1):
                manifest = crops / "candidate_manifest.json"
                probs = verified / "probabilities.json"
                acc = outroot / cell["name"] / f"pass_{i}" / f"accepted_t{prob_t}.geojson"
                run([sys.executable, str(BUILD_PV), "--manifest", str(manifest),
                     "--probabilities", str(probs), "--threshold", str(prob_t),
                     "--output", str(acc)])
                accepted_paths.append(acc)
            f1, mcc = _score(cell, accepted_paths, bounds, prob_t, outroot)
            print(f"  {cell['name']} prob_t={prob_t}: F1@20m={f1:.4f} MCC={mcc}", flush=True)
            if f1 > best["f1"]:
                best = {"f1": f1, "mcc": mcc, "prob_t": prob_t}
        summary[cell["name"]] = best
        print(f"  >>> {cell['name']} BEST: prob_t={best['prob_t']} "
              f"F1@20m={best['f1']:.4f} MCC={best['mcc']}", flush=True)
    out = outroot / "stage_d_score_summary.json"
    out.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote {out}", flush=True)


def _score(cell: dict, accepted: list[Path], bounds: Path, prob_t: float,
           outroot: Path) -> tuple[float, float | None]:
    """Score a cell's accepted geojson(s); return (F1@20m, MCC).

    Consensus cells: one accepted set. Single-pass cells: replicate-mean over the
    K accepted passes (evaluate_detections.py --detections-dir).
    """
    out_dir = outroot / cell["name"] / f"eval_t{prob_t}"
    if cell["kind"] == "single-pass":
        # Gather the K accepted passes into one dir for replicate-mean scoring.
        rep_dir = outroot / cell["name"] / f"accepted_t{prob_t}_passes"
        rep_dir.mkdir(parents=True, exist_ok=True)
        for i, p in enumerate(accepted, 1):
            (rep_dir / f"accepted_run{i}.geojson").write_text(p.read_text())
        cmd = [sys.executable, str(EVAL), "--detections-dir", str(rep_dir),
               "--glob", "accepted_run*.geojson"]
    else:
        cmd = [sys.executable, str(EVAL), "--detections", str(accepted[0])]
    cmd += ["--ground-truth", str(GROUND_TRUTH), "--bounds", str(bounds),
            "--buffers", *[str(b) for b in BUFFERS], "--mcc",
            "--output-dir", str(out_dir)]
    run(cmd)
    summary = json.loads((out_dir / "evaluation.json").read_text())["summary"]
    f1 = next(b["f1"] for b in summary["buffers"] if b["buffer_metres"] == 20)
    mcc = summary.get("tile_classification", {}).get("mcc", {}).get("point")
    return float(f1), mcc


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cells", type=Path, default=DEFAULT_CELLS)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTROOT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--score", action="store_true")
    parser.add_argument("--smoke-n", type=int, default=12)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    spec = json.loads(args.cells.read_text())
    cells = spec["cells"]
    prob_sweep = spec.get("prob_t_sweep", [0.1, 0.15, 0.2, 0.3, 0.5])

    if not any([args.dry_run, args.smoke, args.full, args.score]):
        parser.error("pick one of --dry-run / --smoke / --full / --score")

    if args.dry_run:
        do_dry_run(cells, args.output_root)
    if args.smoke:
        do_smoke(cells, args.output_root, args.smoke_n, args.workers)
    if args.full:
        do_full(cells, args.output_root, args.workers)
    if args.score:
        do_score(cells, args.output_root, prob_sweep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
