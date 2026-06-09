#!/usr/bin/env python3
# ============================================================================
# run_verifier_robustness.py
# ----------------------------------------------------------------------------
# Session 109 — verifier-robustness orchestration.
#
# Two open questions about the production adversarial verifier, both of which
# bear on EVERY n=1 verified cell in the paper (the Stage-D grid, the 55-map
# deployment oracle, all proposer-verifier cells):
#
#   1. DETERMINISM. Every verified cell to date is n=1, on the assumption that
#      T=0.0 is deterministic. It is NOT: two independent T=0.0 runs of the
#      identical config on the same crops disagree on ~3% of candidates
#      (outputs/wbf/e47-propose-brief-n5/verified-v1 vs -v2). This script runs
#      the verifier at N iterations so we can compare the spread of N single
#      runs against an N-run *consensus* verifier.
#
#   2. PROPOSER INPUT. What proposer pool should we feed the verifier? We verify
#      the 1-of-5 *union* (the broadest pool — every candidate proposed by >=1
#      of 5 passes) ONCE, then derive every proposer-vote input level
#      (1of5..5of5) as a free post-hoc subset, because the union geojson carries
#      `vote_count` per feature. This finds the optimal *input* to the verifier
#      (max-recall flood the verifier prunes, vs a pre-filtered strict pool).
#
# DESIGN (Shawn-approved, Session 109)
# ------------------------------------
# Verify the 1-of-5 union of the two GS consensus+PV proposers — the leading
# 384 (flash-high-text) and the 256 rescue cell (text) — at N=5 iterations.
# Stage 1 runs T=0.0 ONLY (determinism + proposer-input sweep at the production
# temperature). Later stages add the verifier temperature 0.3 / 0.7 / 1.0 one
# notch at a time (the hypothesis: a higher-T *consensus* verifier mirrors the
# proposer-side diversity dividend, even though higher T was worse at n=1).
#
# This script ONLY does extract + verify (the gated API spend). Scoring and the
# determinism / proposer-input analysis live in a separate $0 script written
# after the data lands (analyse_verifier_robustness.py).
#
# The verify step REUSES the canonical machinery (scripts/run_pv.py verify) with
# --iterations N --temperature T --service-tier flex; it adds NO new API surface,
# only orchestration. Crops are extracted once per cell (temperature-independent)
# and reused across temperatures.
#
# MODES
# -----
#   --dry-run : `run_pv.py extract --dry-run` per cell (validates rasters +
#               geojson resolve; NO API) + the cost table for the chosen
#               (temperature, iterations).
#   --smoke   : subset each cell to --smoke-n candidates, extract + verify
#               (N iterations, flex), and report the per-iteration probability
#               spread — a tiny end-to-end API check (~N x smoke-n x ncells
#               calls) before the full launch.
#   --full    : extract (idempotent) + verify EVERY union candidate (flex).
#
# COMPUTE: extract is local ($0); verify is the Gemini API (flex, 50%-off). Run
# on zbook (sapphire may be shared; amd-tower is compute-forbidden).
#
# Usage:
#     python scripts/run_verifier_robustness.py --dry-run --temperature 0.0
#     python scripts/run_verifier_robustness.py --smoke --temperature 0.0 --workers 12
#     python scripts/run_verifier_robustness.py --full  --temperature 0.0 --workers 16
#     # Stage 2+ (after reviewing Stage 1): re-run --full at the next notch
#     python scripts/run_verifier_robustness.py --full  --temperature 0.3 --workers 16
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-06-09
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CELLS = BASE_DIR / "planning" / "verifier-robustness-cells.json"
DEFAULT_OUTROOT = BASE_DIR / "outputs" / "verifier-robustness"
VERIFIER_CONFIG = BASE_DIR / "prompts" / "configs" / "verify_adversarial-text.json"
RUN_PV = BASE_DIR / "scripts" / "run_pv.py"
PADDING = 75  # 150 px crops — the carry-forward, identical to Stage-D
FLEX_PER_CALL = 0.000697  # calibrated to the Session-107 actuals (7,113 -> $4.96)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """Run a subprocess, echoing the command; raise on non-zero exit."""
    print("  $ " + " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=True, cwd=BASE_DIR, **kw)


def crops_dir(cell: dict, outroot: Path) -> Path:
    """Crops live once per cell (temperature-independent)."""
    return outroot / cell["name"] / "crops"


def verified_dir(cell: dict, outroot: Path, temperature: float) -> Path:
    """Verified outputs are namespaced by verifier temperature."""
    return outroot / cell["name"] / f"T{temperature}" / "verified"


def subset_geojson(src: Path, dst: Path, n: int) -> int:
    """Write the first ``n`` features of ``src`` to ``dst`` (smoke subset).

    Args:
        src: Source proposer union GeoJSON.
        dst: Destination subset GeoJSON.
        n: Number of leading features to keep.

    Returns:
        The number of features actually written.
    """
    fc = json.loads(src.read_text())
    fc["features"] = fc["features"][:n]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(fc))
    return len(fc["features"])


def extract(proposer: Path, out_crops: Path, dry_run: bool = False) -> None:
    """Extract crops for a proposer GeoJSON via run_pv.py (local, no API)."""
    cmd = [sys.executable, str(RUN_PV), "extract", "--proposer", str(proposer),
           "--output-dir", str(out_crops), "--padding", str(PADDING)]
    if dry_run:
        cmd.append("--dry-run")
    run(cmd)


def verify(out_crops: Path, out_verified: Path, iterations: int,
           temperature: float, workers: int) -> None:
    """Verify crops at N iterations and a fixed temperature (realtime flex)."""
    run([sys.executable, str(RUN_PV), "verify",
         "--crops-dir", str(out_crops),
         "--verifier-config", str(VERIFIER_CONFIG),
         "--output-dir", str(out_verified),
         "--mode", "realtime", "--service-tier", "flex",
         "--iterations", str(iterations), "--temperature", str(temperature),
         "--workers", str(workers)])


def report_probabilities(probs_path: Path, iterations: int) -> None:
    """Print a short per-iteration sanity summary of a probabilities.json.

    For a consensus run the results dict is keyed ``candidate_NNNNN_iterK``; we
    group by candidate to show how many of the N iterations accept, which is the
    determinism signal in miniature.
    """
    if not probs_path.exists():
        print(f"  WARNING: no probabilities at {probs_path}", flush=True)
        return
    results = json.loads(probs_path.read_text()).get("results", {})
    # Group probabilities by base candidate id (strip the _iterK suffix).
    by_cand: dict[str, list[float]] = {}
    for key, val in results.items():
        if not isinstance(val, dict):
            continue
        p = val.get("mound_probability")
        if not isinstance(p, (int, float)):
            continue
        base = key.rsplit("_iter", 1)[0]
        by_cand.setdefault(base, []).append(float(p))
    if not by_cand:
        print(f"  probabilities.json present but no mound_probability parsed "
              f"(inspect {probs_path})", flush=True)
        return
    n_cand = len(by_cand)
    # Per-candidate: a candidate is unanimous if ALL of ITS iterations agree
    # (0 accepts or all-of-len accepts). Using len(ps) per candidate — not the
    # global ``iterations`` — keeps the SPLIT% honest if a candidate is missing
    # an iteration (the global-count version would miscount it as SPLIT).
    unanimous = sum(1 for ps in by_cand.values()
                    if sum(1 for p in ps if p >= 0.2) in (0, len(ps)))
    split = n_cand - unanimous
    mean_p = sum(p for ps in by_cand.values() for p in ps) / sum(len(ps) for ps in by_cand.values())
    print(f"  candidates={n_cand}, mean_prob={mean_p:.3f}, "
          f"unanimous(0 or {iterations} accepts)={unanimous} ({100*unanimous/n_cand:.0f}%), "
          f"SPLIT across iterations={split} ({100*split/n_cand:.1f}%)", flush=True)


def do_dry_run(cells: list[dict], outroot: Path, iterations: int,
               temperature: float) -> None:
    """Validate every union extracts cleanly (no API) + print the cost table."""
    total_cands = 0
    print(f"=== DRY RUN — extract --dry-run per cell (no API); "
          f"iterations={iterations}, temperature={temperature}, tier=flex ===",
          flush=True)
    for cell in cells:
        n = cell["n_union"]
        total_cands += n
        print(f"\n--- {cell['name']} ({n} union candidates) ---", flush=True)
        extract(BASE_DIR / cell["proposer"], crops_dir(cell, outroot), dry_run=True)
    calls = total_cands * iterations
    flex = calls * FLEX_PER_CALL
    print(f"\n=== {total_cands} union candidates x {iterations} iterations "
          f"= {calls:,} calls — est ${flex:.2f} flex / ${flex * 2:.2f} standard "
          f"(this temperature only) ===", flush=True)


def do_smoke(cells: list[dict], outroot: Path, n: int, iterations: int,
             temperature: float, workers: int) -> None:
    """Subset each cell to ~n candidates, extract + verify, report iteration spread."""
    print(f"=== SMOKE — first {n} candidates per cell, N={iterations} @ T={temperature}, "
          f"flex verify ===", flush=True)
    for cell in cells:
        prop = BASE_DIR / cell["proposer"]
        base = outroot / "_smoke" / cell["name"]
        subset = base / "subset.geojson"
        k = subset_geojson(prop, subset, n)
        crops = base / "crops"
        verified = base / f"T{temperature}" / "verified"
        print(f"\n--- {cell['name']}: {k} candidates ---", flush=True)
        extract(subset, crops)
        verify(crops, verified, iterations, temperature, workers)
        report_probabilities(verified / "probabilities.json", iterations)


def do_full(cells: list[dict], outroot: Path, iterations: int,
            temperature: float, workers: int) -> None:
    """Extract (idempotent) + verify every union candidate at N iterations."""
    print(f"=== FULL RUN — extract + verify N={iterations} @ T={temperature} "
          f"(realtime flex) ===", flush=True)
    for cell in cells:
        print(f"\n########## {cell['name']} ({cell['n_union']} candidates) ##########",
              flush=True)
        crops = crops_dir(cell, outroot)
        # Idempotent extract: skip if the manifest already exists (crops are
        # temperature-independent, so a later-temperature run reuses them).
        if (crops / "candidate_manifest.json").exists():
            print(f"  crops already extracted at {crops} — reusing", flush=True)
        else:
            extract(BASE_DIR / cell["proposer"], crops)
        verify(crops, verified_dir(cell, outroot, temperature), iterations,
               temperature, workers)
        report_probabilities(verified_dir(cell, outroot, temperature) / "probabilities.json",
                             iterations)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cells", type=Path, default=DEFAULT_CELLS)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTROOT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--temperature", type=float, required=True,
                        help="Verifier temperature for this run (Stage 1 = 0.0)")
    parser.add_argument("--iterations", type=int, default=None,
                        help="Verifier iterations (default: from the cells spec)")
    parser.add_argument("--smoke-n", type=int, default=12)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    spec = json.loads(args.cells.read_text())
    cells = spec["cells"]
    iterations = args.iterations if args.iterations is not None else spec["iterations"]

    if not any([args.dry_run, args.smoke, args.full]):
        parser.error("pick one of --dry-run / --smoke / --full")

    if args.dry_run:
        do_dry_run(cells, args.output_root, iterations, args.temperature)
    if args.smoke:
        do_smoke(cells, args.output_root, args.smoke_n, iterations,
                 args.temperature, args.workers)
    if args.full:
        do_full(cells, args.output_root, iterations, args.temperature, args.workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
