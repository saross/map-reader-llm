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
# Stage 1) at N=5, climbing 0.0 -> 0.3 -> 0.7 -> 1.0 — but PER CELL INDEPENDENTLY:
#   - at each temperature, run + analyse only the cells still "live"; take the
#     best CONSENSUS/mean operating point F1@20 m per cell over the band
#     (consensus_vt x prob_t).
#   - a cell ADVANCES to the next temperature iff ITS best-consensus F1 beats
#     ITS previous temperature by more than --margin (default 0.005, the
#     determinism noise floor from Stage 1); otherwise that cell STALLS and is
#     not re-verified at higher temperatures.
#   - so 256 can keep climbing while 384 has already peaked (and vice versa) —
#     each tile size finds its own optimal verifier temperature, with no wasted
#     spend on a stalled cell. The ladder ends when every cell has stalled.
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
    print(f"\nDECISION RULE (per-cell INDEPENDENT): each cell advances to the next "
          f"temperature iff ITS best-consensus F1@20m beats ITS previous "
          f"temperature by > {margin}; otherwise that cell stalls and is not "
          f"re-verified higher. 256 and 384 climb independently; the ladder ends "
          f"when every cell has stalled. Worst case (both climb all rungs) is the "
          f"full cost above.", flush=True)


def do_run(spec: dict, ladder: list[float], margin: float, iterations: int,
           workers: int, outroot: Path, results_dir: Path) -> dict:
    """Execute the per-cell-INDEPENDENT snowball; return the trajectory.

    Each cell climbs its OWN temperature ladder. At each rung only the cells
    still improving ("live") are verified, and a cell drops out the moment its
    best-consensus F1@20 m fails to beat ITS previous temperature by > margin.
    So 256 can advance to a higher temperature while 384 has already stalled —
    a peaked cell is never re-verified (no wasted spend), and the comparison is
    always against that cell's own previous temperature.
    """
    cells = spec["cells"]
    cfg = json.loads(VERIFIER_CONFIG.read_text())
    print(f"=== SNOWBALL (per-cell independent) — held constant: "
          f"model={cfg.get('model')}, thinking={cfg.get('thinking_level')}, "
          f"N={iterations}, flex; only temperature varies ===", flush=True)

    prev = baseline_t0(cells)                       # per-cell best-consensus F1
    live = {c["name"]: True for c in cells}         # which cells keep climbing
    stalled_at = {c["name"]: None for c in cells}   # temperature each cell stalled at
    print(f"T=0.0 baseline (best-consensus F1@20m per cell): {prev}", flush=True)

    trajectory = [{"temperature": 0.0, "best_consensus_f1": dict(prev),
                   "source": "stage1"}]
    for t in ladder:
        live_names = [c["name"] for c in cells if live[c["name"]]]
        if not live_names:
            print("\nAll cells have stalled — ladder complete.", flush=True)
            break
        print(f"\n########## TEMPERATURE {t} (live: {live_names}) ##########", flush=True)
        # Sub-spec with only the live cells, so the driver + analyser touch
        # (and spend on) ONLY those — a stalled cell is not re-verified.
        sub = dict(spec)
        sub["cells"] = [c for c in cells if live[c["name"]]]
        sub_path = results_dir / f"_snowball_subspec_T{t}.json"
        sub_path.write_text(json.dumps(sub))
        run([sys.executable, str(DRIVER), "--full", "--temperature", str(t),
             "--cells", str(sub_path), "--output-root", str(outroot),
             "--workers", str(workers)])
        run([sys.executable, str(ANALYSER), "--temperature", str(t),
             "--cells", str(sub_path), "--output-root", str(outroot),
             "--out-dir", str(results_dir)])
        cur = best_consensus_f1(results_dir, t)     # only the live cells present
        rec = {"temperature": t, "live_cells": live_names,
               "best_consensus_f1": cur, "delta_vs_prev": {}, "advanced": {}}
        for name in live_names:
            delta = round(cur.get(name, 0.0) - prev[name], 4)
            rec["delta_vs_prev"][name] = delta
            if delta > margin:
                rec["advanced"][name] = True
                prev[name] = cur[name]
                print(f"  {name}: F1={cur[name]:.4f} (delta {delta:+.4f} > {margin}) "
                      f"-> ADVANCE", flush=True)
            else:
                rec["advanced"][name] = False
                live[name] = False
                stalled_at[name] = t
                reason = "within noise floor" if delta > 0 else "no improvement"
                print(f"  {name}: F1={cur.get(name, 0.0):.4f} (delta {delta:+.4f}) "
                      f"-> STALL ({reason}); not pursued at higher T", flush=True)
        trajectory.append(rec)
        # Write incrementally so a mid-ladder crash preserves progress (API spend
        # is already checkpointed per temperature by run_pv).
        (results_dir / "snowball_summary.json").write_text(json.dumps(
            {"ladder": ladder, "margin": margin, "iterations": iterations,
             "baseline_T0.0": baseline_t0(cells), "stalled_at": stalled_at,
             "trajectory": trajectory}, indent=2))

    out = {"ladder": ladder, "margin": margin, "iterations": iterations,
           "baseline_T0.0": baseline_t0(cells), "stalled_at": stalled_at,
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
        do_run(spec, ladder, margin, iterations, args.workers,
               args.output_root, args.results_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
