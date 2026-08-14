#!/usr/bin/env python3
"""Score the eight 55-map board cells against the ruling-21 standardised reference.

Queue items 2 and 3 of
``reports/verification/reference-standardisation-queue.md`` (execution
contract § Execution contract; PI go 2026-08-14): give the T=0.3 run its
full-buffer evaluation (item 2) and unify F1 and tile-level MCC onto a
single shared reference across the eight board cells (item 3). The T=0.3
cells are scored ONCE here and registered under both items.

Three legs, following the item-1 A/B/C vintage-decomposition template
(Dawid–Skene report § 6.3):

- **Leg A — reproduction gate.** Re-score every cell with the LEGACY
  reference (reviewed student GT 4,746 + ring-gated
  ``canonical-review.csv`` phantoms) at R = 50 m and require the committed
  Track-2 F1 values (``results/55maps-extended-gt-2026-06-07/``) to
  reproduce within 1e-4. "Reproduce before you vary" — a red gate is a
  contract stop state, never absorbed.
- **Leg B — diagnostic decomposition.** Standardised STUDENT layer +
  legacy ring-gated phantoms at R = 50 m. B − A isolates the student-layer
  standardisation; C − B isolates the extension-layer overhaul (ring-gated
  detection positions → 279 marked centres, included whole at every R).
  Diagnostic only, not citable (item-1 precedent: B fits uncommitted).
- **Leg C — publication scoring.** Standardised student layer +
  standardised extension layer, full 14-buffer sweep, ``--compute-mcc``,
  10,000-iteration bootstrap. F1 and MCC now share one reference —
  item 3's completion gate.

Reference-consumption semantics (read at source per the S132 start
instruction): the standardised extension layer carries marked centres
(±2.5 m), so the legacy localisation gate (``build_phantom_gdf``'s
``buffer_metres <= R``; Obs 371) is dissolved and the layer enters the
extended GT whole at every buffer — see
``compute_corrected_f1_multi_buffer.load_standardised_extension``.

Feature-count crosscheck: each cell's detection GeoJSON is counted and
compared against the documented n_detections BEFORE any scoring
(Session 77 wrong-source class); mismatch is a hard stop.

Pure deterministic re-scoring of committed artefacts; NO API, US$0.
Compute on sapphire (project rule); use ``--jobs 8`` there for cell-level
parallelism (the engine itself is single-threaded per buffer).

Usage::

    # Pre-flight smoke (local, fast): crosscheck + A gate on one cell
    python scripts/score_55maps_standardised_reference.py --smoke

    # Full run (sapphire):
    python scripts/score_55maps_standardised_reference.py --legs A B C \
        --jobs 8

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import contextlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import compute_corrected_f1_multi_buffer as engine  # noqa: E402

REPO = SCRIPT_DIR.parent

# --- Fixed inputs -----------------------------------------------------------
STD_DIR = REPO / "results/deployment-oracle-2026-06-06/canonical-gt/standardised"
STUDENT_STD = STD_DIR / "student-mounds-55maps-standardised.geojson"
EXTENSION_STD = STD_DIR / "extension-mounds-standardised.csv"
STUDENT_LEGACY = REPO / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
CANONICAL_REVIEW = (
    REPO / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv"
)
BOUNDS = REPO / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"

# Census expectations (standardised README, materialised at ecc00f31f)
N_STUDENT_STD = 4731
N_EXTENSION_STD = 279
MIN_NEAREST_STUDENT_M = 10.32  # observed minimum; must exceed the 5 m dedup

# Full 14-buffer sweep — locked decision (headline at 50 m, Obs 260).
BUFFERS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]

# --- The 8 board cells ------------------------------------------------------
# n_det = documented feature count (crosschecked against the GeoJSON before
# scoring). gate_legacy_50m = committed Track-2 F1 @ 50 m against the LEGACY
# canonical extended GT (results/55maps-extended-gt-2026-06-07/<cell>/
# summary.json), the leg-A reproduction target.
CELLS = [
    {
        "label": "TH7-k4", "config": "text-high-T0.7", "k": 4,
        "role": "carry-forward",
        "det": "outputs/55maps-text-high-generalisation/verified/verified_detections.geojson",
        "n_det": 4164, "gate_legacy_50m": 0.8152278820375335,
    },
    {
        "label": "TH7-k3", "config": "text-high-T0.7", "k": 3,
        "role": "threshold",
        "det": "results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-high-generalisation/k3_verified.geojson",
        "n_det": 4786, "gate_legacy_50m": 0.8424650648436715,
    },
    {
        "label": "T03-k4", "config": "text-high-T0.3", "k": 4,
        "role": "config (item 2: the t0.3 run)",
        "det": "outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson",
        "n_det": 4350, "gate_legacy_50m": 0.8358742508674167,
    },
    {
        "label": "T03-k3", "config": "text-high-T0.3", "k": 3,
        "role": "ORACLE (item 2: the t0.3 run)",
        "det": "results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-high-t0.3-generalisation/k3_verified.geojson",
        "n_det": 4905, "gate_legacy_50m": 0.8476058017087225,
    },
    {
        "label": "TM-k4", "config": "text-min", "k": 4, "role": "config",
        "det": "outputs/55maps-text-min-generalisation/verified/verified_detections.geojson",
        "n_det": 3865, "gate_legacy_50m": 0.7830711278528694,
    },
    {
        "label": "TM-k3", "config": "text-min", "k": 3, "role": "threshold",
        "det": "results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-min-generalisation/k3_verified.geojson",
        "n_det": 4279, "gate_legacy_50m": 0.8127118644067797,
    },
    {
        "label": "IM-k3", "config": "image", "k": 3, "role": "config (carried)",
        "det": "outputs/55maps-image-generalisation/verified/verified_detections.geojson",
        "n_det": 4680, "gate_legacy_50m": 0.7986993191748807,
    },
    {
        "label": "TM-n10-k5", "config": "text-min-n10", "k": 5,
        "role": "uplift",
        "det": "results/55map-leaderboard/min11-uplift-5of10-pt0.15.geojson",
        "n_det": 4361, "gate_legacy_50m": 0.8290275152278933,
    },
]

GATE_TOL = 1e-4  # matches the S105 validation-gate tolerance


def crosscheck_feature_counts(cells: list[dict]) -> list[dict]:
    """Count features in each detection GeoJSON vs the documented n_det.

    Returns the per-cell crosscheck rows; raises SystemExit on any
    mismatch (hard stop — the Session 77 wrong-source failure class).
    """
    rows = []
    failures = []
    for cell in cells:
        path = REPO / cell["det"]
        with open(path, encoding="utf-8") as fh:
            n_actual = len(json.load(fh)["features"])
        ok = n_actual == cell["n_det"]
        rows.append({
            "label": cell["label"], "det": cell["det"],
            "n_documented": cell["n_det"], "n_actual": n_actual,
            "verdict": "OK" if ok else "MISMATCH",
        })
        if not ok:
            failures.append(cell["label"])
        print(
            f"  crosscheck {cell['label']:10s} documented={cell['n_det']} "
            f"actual={n_actual}  {'OK' if ok else 'MISMATCH'}"
        )
    if failures:
        raise SystemExit(
            f"feature-count crosscheck FAILED for {failures} — stop state; "
            "do not score against an unverified detection source"
        )
    return rows


def census_checks() -> None:
    """Assert the standardised layers match their published census."""
    with open(STUDENT_STD, encoding="utf-8") as fh:
        n_student = len(json.load(fh)["features"])
    if n_student != N_STUDENT_STD:
        raise SystemExit(
            f"standardised student layer has {n_student} features, "
            f"census says {N_STUDENT_STD} — stop state"
        )
    ext = engine.load_standardised_extension(EXTENSION_STD)
    if len(ext) != N_EXTENSION_STD:
        raise SystemExit(
            f"standardised extension layer has {len(ext)} records, "
            f"census says {N_EXTENSION_STD} — stop state"
        )
    min_d = float(ext["nearest_student_m"].min())
    if abs(min_d - MIN_NEAREST_STUDENT_M) > 0.005:
        raise SystemExit(
            f"extension min nearest_student_m is {min_d}, expected "
            f"{MIN_NEAREST_STUDENT_M} — layer changed underfoot; stop state"
        )
    print(
        f"  census OK: student {n_student}, extension {len(ext)}, "
        f"min nearest_student_m {min_d} m (> 5 m dedup tolerance)"
    )


def ensure_empty_yesterday(output_base: Path) -> Path:
    """Header-only review CSV for legacy-mode legs (single-source pattern)."""
    output_base.mkdir(parents=True, exist_ok=True)
    path = output_base / "empty-yesterday-review.csv"
    path.write_text(
        "candidate_id,human_label,buffer_metres,x,y,map_name\n"
    )
    return path


def _score_cell(job: dict) -> dict:
    """Worker: score one cell for one leg; stdout captured to score.log."""
    out_dir = Path(job["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "score.log"
    with open(log_path, "w", encoding="utf-8") as log, \
            contextlib.redirect_stdout(log):
        engine.run(
            verified_detections=Path(job["det"]),
            student_gt=Path(job["student_gt"]),
            bounds=BOUNDS,
            review_yesterday=(
                Path(job["review_yesterday"])
                if job.get("review_yesterday") else None
            ),
            review_today=(
                Path(job["review_today"]) if job.get("review_today") else None
            ),
            extension_csv=(
                Path(job["extension_csv"])
                if job.get("extension_csv") else None
            ),
            output_dir=out_dir,
            buffers=job["buffers"],
            n_bootstrap=job["n_bootstrap"],
            seed=job["seed"],
            compute_mcc=job["compute_mcc"],
        )
    with open(out_dir / "summary.json", encoding="utf-8") as fh:
        summary = json.load(fh)
    return {"label": job["label"], "leg": job["leg"], "summary": summary}


def f1_at(summary: dict, r_m: int) -> float | None:
    """Corrected-F1 point estimate at buffer R from a cell summary."""
    for row in summary["results"]:
        if row["R_m"] == r_m:
            return row["F1"]
    return None


def mcc_at(summary: dict, r_m: int) -> float | None:
    """Tile MCC at buffer R from a cell summary (None if absent)."""
    for row in summary["results"]:
        if row["R_m"] == r_m:
            return (row.get("tile_classification") or {}).get("mcc")
    return None


def build_jobs(
    cells: list[dict], legs: list[str], output_base: Path,
    n_bootstrap: int, seed: int, empty_yesterday: Path,
) -> list[dict]:
    """Expand cells × legs into worker job dicts."""
    jobs = []
    for cell in cells:
        det = str(REPO / cell["det"])
        if "A" in legs:
            jobs.append({
                "label": cell["label"], "leg": "A", "det": det,
                "student_gt": str(STUDENT_LEGACY),
                "review_yesterday": str(empty_yesterday),
                "review_today": str(CANONICAL_REVIEW),
                "out_dir": str(output_base / "repro-gate" / cell["label"]),
                "buffers": [50], "n_bootstrap": 200, "seed": seed,
                "compute_mcc": False,
            })
        if "B" in legs:
            jobs.append({
                "label": cell["label"], "leg": "B", "det": det,
                "student_gt": str(STUDENT_STD),
                "review_yesterday": str(empty_yesterday),
                "review_today": str(CANONICAL_REVIEW),
                "out_dir": str(output_base / "b-diagnostic" / cell["label"]),
                "buffers": [50], "n_bootstrap": 200, "seed": seed,
                "compute_mcc": False,
            })
        if "C" in legs:
            jobs.append({
                "label": cell["label"], "leg": "C", "det": det,
                "student_gt": str(STUDENT_STD),
                "extension_csv": str(EXTENSION_STD),
                "out_dir": str(output_base / cell["label"]),
                "buffers": BUFFERS, "n_bootstrap": n_bootstrap, "seed": seed,
                "compute_mcc": True,
            })
    return jobs


def evaluate_gate(
    cells: list[dict], results: dict[tuple[str, str], dict],
) -> tuple[bool, list[dict]]:
    """Leg-A reproduction gate: committed legacy F1 @ 50 m within GATE_TOL."""
    rows = []
    all_pass = True
    for cell in cells:
        summary = results.get((cell["label"], "A"))
        if summary is None:
            continue
        got = f1_at(summary, 50)
        delta = got - cell["gate_legacy_50m"]
        ok = abs(delta) <= GATE_TOL
        all_pass &= ok
        rows.append({
            "label": cell["label"], "target": cell["gate_legacy_50m"],
            "got": got, "delta": delta, "tol": GATE_TOL,
            "verdict": "PASS" if ok else "FAIL",
        })
        print(
            f"  gate {cell['label']:10s} target={cell['gate_legacy_50m']:.6f} "
            f"got={got:.6f} delta={delta:+.2e}  "
            f"{'PASS' if ok else 'FAIL'}"
        )
    return all_pass, rows


def write_consolidated(
    output_base: Path, cells: list[dict],
    results: dict[tuple[str, str], dict], legs: list[str],
) -> None:
    """Consolidated per-cell CSV + A/B/C decomposition table at 50 m."""
    import csv as csv_mod

    # Full C-leg sweep table
    if "C" in legs:
        path = output_base / "consolidated-standardised.csv"
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv_mod.writer(fh)
            writer.writerow([
                "cell", "config", "k", "R_m", "TP", "FP", "FN",
                "n_ref_student", "n_extension", "n_ref_extended",
                "precision", "recall", "F1", "F1_CI_lo", "F1_CI_hi",
                "MCC", "MCC_CI_lo", "MCC_CI_hi",
            ])
            for cell in cells:
                summary = results.get((cell["label"], "C"))
                if summary is None:
                    continue
                for row in summary["results"]:
                    tc = row.get("tile_classification") or {}
                    mcc_ci = tc.get("mcc_CI") or [None, None]
                    writer.writerow([
                        cell["label"], cell["config"], cell["k"],
                        row["R_m"], row["TP"], row["FP"], row["FN"],
                        row["n_ref_student_only"],
                        row["n_reviewer_promoted_at_R"],
                        row["n_ref_extended"],
                        row["precision"], row["recall"], row["F1"],
                        row["F1_CI"][0], row["F1_CI"][1],
                        tc.get("mcc"), mcc_ci[0], mcc_ci[1],
                    ])
        print(f"Wrote {path}")

    # A/B/C decomposition at the 50 m headline
    decomp = []
    for cell in cells:
        entry = {"cell": cell["label"], "A_committed": cell["gate_legacy_50m"]}
        for leg in ("A", "B", "C"):
            summary = results.get((cell["label"], leg))
            entry[leg] = f1_at(summary, 50) if summary else None
        if entry.get("C") is not None:
            entry["mcc_C"] = mcc_at(results[(cell["label"], "C")], 50)
        if entry.get("A") is not None and entry.get("B") is not None:
            entry["B_minus_A_student_layer"] = entry["B"] - entry["A"]
        if entry.get("B") is not None and entry.get("C") is not None:
            entry["C_minus_B_extension_layer"] = entry["C"] - entry["B"]
        decomp.append(entry)
    path = output_base / "abc-decomposition-50m.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": engine.git_commit_hash(),
        "note": (
            "F1 @ 50 m. A = legacy reference reproduction (gate); "
            "B = standardised student + legacy ring-gated phantoms "
            "(diagnostic, NOT citable); C = standardised reference "
            "(publication). B-A isolates the student-layer move; "
            "C-B isolates the extension-layer move."
        ),
        "cells": decomp,
    }
    path.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {path}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--legs", nargs="+", choices=["A", "B", "C"],
        default=["A", "B", "C"],
        help="Which legs to run (default: all three).",
    )
    p.add_argument(
        "--cells", nargs="+", default=None,
        help="Subset of cell labels (default: all 8).",
    )
    p.add_argument(
        "--output-base", type=Path,
        default=REPO / "results/55maps-standardised-ref-2026-08-14",
    )
    p.add_argument("--n-bootstrap", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--jobs", type=int, default=1,
        help=(
            "Cell-level parallel workers (default 1 = serial; use 8 on "
            "sapphire — the engine is single-threaded per buffer)."
        ),
    )
    p.add_argument(
        "--smoke", action="store_true",
        help=(
            "Fast pre-flight: crosscheck + census + leg A and C on the "
            "TH7-k4 cell only, C at R=[20, 50] with 200 bootstrap."
        ),
    )
    return p.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    output_base = args.output_base
    output_base.mkdir(parents=True, exist_ok=True)

    cells = CELLS
    if args.cells:
        cells = [c for c in CELLS if c["label"] in args.cells]
        missing = set(args.cells) - {c["label"] for c in cells}
        if missing:
            raise SystemExit(f"unknown cell label(s): {sorted(missing)}")

    print("Pre-flight checks...")
    census_checks()
    crosscheck_rows = crosscheck_feature_counts(cells)

    empty_yesterday = ensure_empty_yesterday(output_base)

    legs = ["A", "C"] if args.smoke else args.legs
    if args.smoke:
        cells = [c for c in cells if c["label"] == "TH7-k4"]

    def run_jobs(jobs: list[dict], results: dict) -> None:
        """Execute jobs (parallel when --jobs > 1) and collect summaries."""
        if args.jobs > 1:
            with ProcessPoolExecutor(max_workers=args.jobs) as pool:
                for res in pool.map(_score_cell, jobs):
                    results[(res["label"], res["leg"])] = res["summary"]
                    print(f"  done {res['label']} leg {res['leg']}")
        else:
            for job in jobs:
                res = _score_cell(job)
                results[(res["label"], res["leg"])] = res["summary"]
                print(f"  done {res['label']} leg {res['leg']}")

    n_bootstrap = 200 if args.smoke else args.n_bootstrap

    results: dict[tuple[str, str], dict] = {}

    # Leg A runs — and gates — BEFORE anything varies (contract:
    # "reproduce before you vary"). A red gate halts here; B/C never run.
    gate_passed = None
    gate_rows: list[dict] = []
    if "A" in legs:
        a_jobs = build_jobs(
            cells, ["A"], output_base, n_bootstrap, args.seed,
            empty_yesterday,
        )
        print(f"\nLeg A (reproduction gate): {len(a_jobs)} job(s), "
              f"jobs={args.jobs}...")
        run_jobs(a_jobs, results)
        print("\nLeg-A reproduction gate:")
        gate_passed, gate_rows = evaluate_gate(cells, results)

    gate_path = output_base / "validation-gate.json"

    def write_gate() -> None:
        gate_path.write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "git_commit": engine.git_commit_hash(),
            "feature_count_crosscheck": crosscheck_rows,
            "gate_tolerance": GATE_TOL,
            "gate_passed": gate_passed,
            "gate_rows": gate_rows,
        }, indent=2))
        print(f"Wrote {gate_path}")

    if gate_passed is False:
        write_gate()
        raise SystemExit(
            "leg-A reproduction gate FAILED — contract stop state: halt "
            "and escalate; legs B/C were NOT run"
        )

    bc_legs = [leg for leg in legs if leg in ("B", "C")]
    if bc_legs:
        bc_jobs = build_jobs(
            cells, bc_legs, output_base, n_bootstrap,
            args.seed, empty_yesterday,
        )
        if args.smoke:
            for j in bc_jobs:
                j["buffers"] = [20, 50]
        print(f"\nLegs {bc_legs}: {len(bc_jobs)} job(s), jobs={args.jobs}...")
        run_jobs(bc_jobs, results)

    write_gate()
    write_consolidated(output_base, cells, results, legs)
    print("\nAll requested legs complete.")


if __name__ == "__main__":
    main()
