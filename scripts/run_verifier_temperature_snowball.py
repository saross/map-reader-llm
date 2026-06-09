#!/usr/bin/env python3
# ============================================================================
# run_verifier_temperature_snowball.py
# ----------------------------------------------------------------------------
# Session 109 Stage-2: a self-contained, unattended GREEDY temperature snowball
# for the higher-T *consensus* verifier test.
#
# THE QUESTION. At T=0.0 a 5-run consensus verifier gave no benefit over n=1
# (Stage 1 / Obs 354) — five near-identical passes carry no diversity. A higher
# verifier temperature decorrelates the passes; the hypothesis is that a higher-T
# CONSENSUS verifier mirrors the proposer-side diversity dividend. This script
# climbs the temperature ladder while it keeps helping, and stops when it doesn't.
#
# THE LADDER (Shawn-approved, Session 109). Verify the >=3-of-5 proposer band of
# the two GS cells (the productive band; the 1of5 union was the worst input in
# Stage 1) at N=5, climbing 0.0 -> 0.3 -> 0.7 -> 1.0:
#   - run T; analyse; take the best CONSENSUS/mean operating point F1@20 m per
#     cell over the band (consensus_vt x prob_t).
#   - advance to the next temperature ONLY IF the better cell improves over the
#     PREVIOUS temperature by more than --margin (default 0.005, the determinism
#     noise floor from Stage 1) — otherwise stop. This snowballs while a real
#     diversity dividend exists and refuses to chase noise.
#
# HELD CONSTANT (only temperature changes): model (gemini-3-flash), thinking
# (minimal, from the config), proposer band (>=3of5), N=5, text-only verifier,
# realtime flex. The T=0.0 baseline comes from Stage 1 (no re-run).
#
# COST. Each temperature = 2,500 band candidates x 5 = 12,500 calls ~= $8.71
# flex; worst case (all three temperatures fire) ~= $26.14 flex. The snowball
# stops early when a temperature does not beat the previous by > margin.
#
# It REUSES the audited per-temperature machinery via subprocess — no new API
# surface:
#   scripts/run_verifier_robustness.py --full --temperature T --cells <stage2>
#   scripts/analyse_verifier_robustness.py --temperature T --cells <stage2>
# and reads each analysis summary's best_operating_point (already restricted to
# reproducible consensus/mean rules) to decide continuation.
#
# MODES
#   --dry-run : print the ladder, per-temperature cost, the decision rule and
#               the held-constant config (incl. the verifier thinking level) —
#               NO API.
#   --run     : execute the snowball (gated API; run on zbook).
#
# Usage:
#   python scripts/run_verifier_temperature_snowball.py --dry-run
#   python scripts/run_verifier_temperature_snowball.py --run --workers 20
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
DEFAULT_CELLS = BASE_DIR / "planning" / "verifier-robustness-stage2-cells.json"
DEFAULT_OUTROOT = BASE_DIR / "outputs" / "verifier-robustness"
DEFAULT_RESULTS = BASE_DIR / "results" / "verifier-robustness"
VERIFIER_CONFIG = BASE_DIR / "prompts" / "configs" / "verify_adversarial-text.json"
DRIVER = BASE_DIR / "scripts" / "run_verifier_robustness.py"
ANALYSER = BASE_DIR / "scripts" / "analyse_verifier_robustness.py"
FLEX_PER_CALL = 0.000697


def run(cmd: list[str]) -> None:
    """Run a subprocess, echoing the command; raise on non-zero exit."""
    print("  $ " + " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=BASE_DIR)


def best_consensus_f1(results_dir: Path, temperature: float) -> dict[str, float]:
    """Read the analysis summary for one temperature; return {cell: best F1@20m}.

    ``best_operating_point`` is already restricted to reproducible consensus/mean
    rules by the analyser, so this is the best CONSENSUS operating point per cell.
    """
    summ = json.loads((results_dir / f"robustness_summary_T{temperature}.json").read_text())
    out = {}
    for s in summ["summaries"]:
        bop = s.get("best_operating_point")
        out[s["cell"]] = bop["f1_20m"] if bop else 0.0
    return out


def baseline_t0(cells: list[dict]) -> dict[str, float]:
    """T=0.0 baseline best-consensus F1 per Stage-2 cell, from the spec.

    The Stage-1 T=0.0 best operating point for each GS cell fell inside the
    >=3of5 band (384 at 4of5, 256 at 5of5), so the recorded
    ``stage1_T0.0_best_consensus_f1`` (taken from the Stage-1 grid) IS the band
    baseline — no Stage-1 re-run needed.
    """
    return {c["name"]: float(c["stage1_T0.0_best_consensus_f1"]) for c in cells}


def do_dry_run(cells: list[dict], ladder: list[float], margin: float,
               iterations: int) -> None:
    """Print the ladder, cost, decision rule and held-constant config (no API)."""
    cfg = json.loads(VERIFIER_CONFIG.read_text())
    band = sum(c["n_union"] for c in cells)
    per_temp_calls = band * iterations
    per_temp_flex = per_temp_calls * FLEX_PER_CALL
    print("=== DRY RUN — verifier temperature snowball ===", flush=True)
    print(f"HELD CONSTANT: model={cfg.get('model')}, thinking={cfg.get('thinking_level')} "
          f"(verifier config {VERIFIER_CONFIG.name}), N={iterations}, text-only, flex.",
          flush=True)
    print(f"ONLY temperature varies. Ladder: {ladder}", flush=True)
    print(f"\nBand candidates (>=3of5, both cells): {band}", flush=True)
    for c in cells:
        print(f"  {c['name']}: {c['n_union']} cands, "
              f"T=0.0 baseline best-consensus F1={c['stage1_T0.0_best_consensus_f1']}", flush=True)
    print(f"\nPer temperature: {per_temp_calls:,} calls ~= ${per_temp_flex:.2f} flex", flush=True)
    print(f"Worst case (all {len(ladder)} temperatures fire): "
          f"{per_temp_calls * len(ladder):,} calls ~= ${per_temp_flex * len(ladder):.2f} flex",
          flush=True)
    print(f"\nDECISION RULE: advance to the next temperature only if the better "
          f"cell's best-consensus F1@20m improves over the PREVIOUS temperature "
          f"by > {margin}. Stop otherwise.", flush=True)


def do_run(cells: list[dict], ladder: list[float], margin: float, iterations: int,
           workers: int, cells_path: Path, outroot: Path, results_dir: Path) -> dict:
    """Execute the snowball; return the trajectory record (also written to disk)."""
    cfg = json.loads(VERIFIER_CONFIG.read_text())
    print(f"=== SNOWBALL — held constant: model={cfg.get('model')}, "
          f"thinking={cfg.get('thinking_level')}, N={iterations}, flex; "
          f"only temperature varies ===", flush=True)

    prev = baseline_t0(cells)
    print(f"T=0.0 baseline (best-consensus F1@20m per cell): {prev}", flush=True)

    trajectory = [{"temperature": 0.0, "best_consensus_f1": prev, "source": "stage1"}]
    for t in ladder:
        print(f"\n########## TEMPERATURE {t} ##########", flush=True)
        run([sys.executable, str(DRIVER), "--full", "--temperature", str(t),
             "--cells", str(cells_path), "--output-root", str(outroot),
             "--workers", str(workers)])
        run([sys.executable, str(ANALYSER), "--temperature", str(t),
             "--cells", str(cells_path), "--output-root", str(outroot),
             "--out-dir", str(results_dir)])
        cur = best_consensus_f1(results_dir, t)
        deltas = {cell: round(cur[cell] - prev.get(cell, 0.0), 4) for cell in cur}
        best_delta = max(deltas.values()) if deltas else 0.0
        advance = best_delta > margin
        within_noise = 0.0 < best_delta <= margin
        rec = {"temperature": t, "best_consensus_f1": cur, "delta_vs_prev": deltas,
               "best_delta": best_delta, "advanced": advance,
               "within_noise_floor": within_noise}
        trajectory.append(rec)
        print(f"  T={t}: best-consensus F1={cur}", flush=True)
        print(f"  delta vs previous: {deltas} "
              f"(best {best_delta:+.4f}, margin {margin})", flush=True)
        # Write incrementally so a mid-ladder crash preserves the trajectory
        # so far (API spend is already checkpointed per temperature by run_pv).
        (results_dir / "snowball_summary.json").write_text(json.dumps(
            {"ladder": ladder, "margin": margin, "iterations": iterations,
             "trajectory": trajectory}, indent=2))
        if not advance:
            reason = ("within the noise floor" if within_noise
                      else "no improvement")
            print(f"  STOP — best delta {best_delta:+.4f} is {reason}; "
                  f"higher temperature not pursued.", flush=True)
            break
        print(f"  ADVANCE — best delta {best_delta:+.4f} > {margin}; continuing.", flush=True)
        prev = cur

    out = {"ladder": ladder, "margin": margin, "iterations": iterations,
           "trajectory": trajectory}
    (results_dir / "snowball_summary.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote {results_dir / 'snowball_summary.json'}", flush=True)
    return out


def main() -> int:
    """CLI entry point."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cells", type=Path, default=DEFAULT_CELLS)
    p.add_argument("--output-root", type=Path, default=DEFAULT_OUTROOT)
    p.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--run", action="store_true")
    p.add_argument("--workers", type=int, default=20)
    p.add_argument("--margin", type=float, default=None,
                   help="Min improvement over the previous temperature to advance "
                        "(default: from the cells spec, else 0.005)")
    args = p.parse_args()

    spec = json.loads(args.cells.read_text())
    cells = spec["cells"]
    ladder = spec["temperature_ladder"]
    iterations = spec["iterations"]
    margin = args.margin if args.margin is not None else spec.get("snowball_margin", 0.005)

    if not (args.dry_run or args.run):
        p.error("pick --dry-run or --run")
    if args.dry_run:
        do_dry_run(cells, ladder, margin, iterations)
    if args.run:
        do_run(cells, ladder, margin, iterations, args.workers,
               args.cells, args.output_root, args.results_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
