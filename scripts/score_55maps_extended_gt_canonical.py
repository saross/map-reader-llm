#!/usr/bin/env python3
"""
Track-2 driver: score the 55-map generalisation cells against the CANONICAL
extended ground truth (Session 105).
==========================================================================

**SUPERSEDED for new scoring (Session 132).** The ruling-21 standardised
reference replaced this driver's canonical-review pairing; new scoring
goes through ``score_55maps_standardised_reference.py``. This driver is
retained to reproduce the committed Session-105 artefacts — note that its
``--gate-tol`` default (1e-4) silently absorbs the post-hoc W6-E9
de-duplication fix (a uniform ≈ +8.7e-05 vs the committed anchors); the
successor driver's A0 sub-leg (``--dedup-tolerance-m 0``, tol 1e-6)
reproduces the committed numbers exactly.

Companion to the historical (Track-1) record, which scores the same cells
against the bare reviewed student GT (``results/rescore-2026-05-31/``). This
driver produces the *paper-reportable* reference: each cell scored against the
**canonical extended GT** = reviewed student GT + the 773-mound canonical,
deduplicated, adjudicated phantom set (``canonical-review.csv``), per-buffer
gated (a phantom enters the GT at radius R only if its min-ring
``buffer_metres <= R``; the 200 m ">150 m" sentinel shell is excluded at every R).

Both tracks share ONE trusted engine — this driver shells the proven
``compute_corrected_f1_multi_buffer.run`` (the script that produced findings §4b)
with ``--compute-mcc``, so the corrected F1 is byte-identical to §4b and the MCC
comes from the same ``calculate_tile_classification`` Track 1 uses. **Only the GT
differs between the two tracks** — clean experimental control.

The 7 cells (4 carried configs + the oracle + 2 threshold-completion k3s) support
all three paper axes against the single canonical GT: config axis, threshold axis
(4-of-5 vs 3-of-5 for the three text configs), and the joint oracle.

**Validation gate.** Five cells have a §4b canonical-GT corrected-F1 @ 50 m value
(read from ``canonical-rescore/*/summary.json``). The driver re-derives each and
asserts agreement to 4 d.p. (``--gate-tol`` = 1e-4). A FAIL aborts before any
results are trusted. The two new k3 cells (TH7-k3, TM-k3) have no §4b value — they
are sanity-checked against the §1 *per-run*-GT values (close-but-not-equal
expected, since the GT differs).

Compute: zbook (per the project compute-host rule). Per-cell parallelism via a
process pool; default 7 workers (one per cell) — well under the 14-core ceiling.
$0 — no API. All detection sets already exist.

Usage::

    python scripts/score_55maps_extended_gt_canonical.py \\
        --output-base results/55maps-extended-gt-2026-06-07 \\
        --workers 7

    # Validation-gate-only smoke (carry-forward cell, single buffer, fast):
    python scripts/score_55maps_extended_gt_canonical.py --gate-only

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Import the trusted single-cell scoring engine.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import compute_corrected_f1_multi_buffer as engine  # noqa: E402

REPO = SCRIPT_DIR.parent

# --- Fixed inputs -----------------------------------------------------------
STUDENT_GT = REPO / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
BOUNDS = REPO / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
CANONICAL_REVIEW = (
    REPO / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv"
)

# Full 14-buffer sweep — locked decision (compute the entire set always; headline
# at 50 m, jitter-matched to the ~25 m student digitisation error, Obs 260).
BUFFERS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]

# --- The 7 Track-2 cells ----------------------------------------------------
# label, detections (repo-relative), config, vote-k, role, §4b gate @50 m (or
# None for the two new k3 cells), §1 per-run sanity value (k3 cells only).
CELLS = [
    {
        "label": "TH7-k4", "config": "text-high-T0.7", "k": 4, "role": "carry-forward",
        "det": "outputs/55maps-text-high-generalisation/verified/verified_detections.geojson",
        "gate_50m": 0.815228, "sanity_per_run": None,
    },
    {
        "label": "TH7-k3", "config": "text-high-T0.7", "k": 3, "role": "threshold (new)",
        "det": ("results/deployment-oracle-2026-06-06/k3-scoring/"
                "55maps-text-high-generalisation/k3_verified.geojson"),
        "gate_50m": None, "sanity_per_run": 0.850,
    },
    {
        "label": "T03-k4", "config": "text-high-T0.3", "k": 4, "role": "config",
        "det": "outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson",
        "gate_50m": 0.835874, "sanity_per_run": None,
    },
    {
        "label": "T03-k3", "config": "text-high-T0.3", "k": 3, "role": "ORACLE",
        "det": ("results/deployment-oracle-2026-06-06/k3-scoring/"
                "55maps-text-high-t0.3-generalisation/k3_verified.geojson"),
        "gate_50m": 0.847606, "sanity_per_run": None,
    },
    {
        "label": "TM-k4", "config": "text-min", "k": 4, "role": "config",
        "det": "outputs/55maps-text-min-generalisation/verified/verified_detections.geojson",
        "gate_50m": 0.783071, "sanity_per_run": None,
    },
    {
        "label": "TM-k3", "config": "text-min", "k": 3, "role": "threshold (new)",
        "det": ("results/deployment-oracle-2026-06-06/k3-scoring/"
                "55maps-text-min-generalisation/k3_verified.geojson"),
        "gate_50m": None, "sanity_per_run": 0.822,
    },
    {
        "label": "IM-k3", "config": "image", "k": 3, "role": "config (carried)",
        "det": "outputs/55maps-image-generalisation/verified/verified_detections.geojson",
        "gate_50m": 0.798699, "sanity_per_run": None,
    },
]


def ensure_empty_yesterday(output_base: Path) -> Path:
    """Write a header-only review CSV to use as ``--review-yesterday``.

    The canonical review is the single deduplicated source — it is passed as
    ``review_today``. ``review_yesterday`` must be a valid (but empty) CSV with
    the review schema so ``build_phantom_gdf`` contributes nothing from it
    (matching how §4b ran: ``yesterday=0 today=773``).
    """
    output_base.mkdir(parents=True, exist_ok=True)
    path = output_base / "empty-yesterday-review.csv"
    with path.open("w", newline="") as fh:
        csv.writer(fh).writerow(
            ["candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"]
        )
    return path


def score_one_cell(
    *,
    label: str,
    det_path: Path,
    review_yesterday: Path,
    output_dir: Path,
    buffers: list[int],
    n_bootstrap: int,
    seed: int,
) -> str:
    """Run the trusted engine for one cell with MCC. Returns the label.

    Module-level (picklable) so it can run in a process-pool worker.
    """
    engine.run(
        verified_detections=det_path,
        student_gt=STUDENT_GT,
        bounds=BOUNDS,
        review_yesterday=review_yesterday,
        review_today=CANONICAL_REVIEW,
        output_dir=output_dir,
        buffers=tuple(buffers),
        n_bootstrap=n_bootstrap,
        seed=seed,
        compute_mcc=True,
    )
    return label


def f1_at(summary: dict, r_m: int) -> float | None:
    """Pull the corrected-F1 point estimate at buffer R from a cell summary."""
    for row in summary.get("results", []):
        if row["R_m"] == r_m:
            return row["F1"]
    return None


def mcc_at(summary: dict, r_m: int) -> float | None:
    """Pull the tile MCC at buffer R from a cell summary (None if absent)."""
    for row in summary.get("results", []):
        if row["R_m"] == r_m:
            return row.get("tile_classification", {}).get("mcc")
    return None


def run_validation_gate(
    summaries: dict[str, dict], tol: float
) -> tuple[bool, list[dict]]:
    """Compare each cell's canonical F1 @ 50 m to its §4b target.

    Returns (all_passed, rows) where rows carry the per-cell verdict. Cells
    without a §4b target are reported as informational sanity checks (vs the
    §1 per-run value) and never fail the gate.
    """
    rows = []
    all_passed = True
    for cell in CELLS:
        label = cell["label"]
        got = f1_at(summaries[label], 50) if label in summaries else None
        target = cell["gate_50m"]
        if target is not None:
            delta = None if got is None else abs(got - target)
            passed = got is not None and delta <= tol
            all_passed = all_passed and passed
            rows.append({
                "label": label, "kind": "GATE", "target": target,
                "got": got, "delta": delta, "tol": tol,
                "verdict": "PASS" if passed else "FAIL",
            })
        else:
            rows.append({
                "label": label, "kind": "sanity (per-run §1)",
                "target": cell["sanity_per_run"], "got": got,
                "delta": (None if got is None else got - cell["sanity_per_run"]),
                "tol": None, "verdict": "info",
            })
    return all_passed, rows


def write_consolidated(output_base: Path, summaries: dict[str, dict]) -> None:
    """Write the consolidated Track-2 table (CSV) over all cells × buffers."""
    out = output_base / "consolidated-track2.csv"
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "cell", "config", "k", "role", "R_m",
            "F1", "F1_CI_lo", "F1_CI_hi", "MCC", "MCC_CI_lo", "MCC_CI_hi",
            "precision", "recall", "sensitivity", "specificity",
        ])
        for cell in CELLS:
            s = summaries.get(cell["label"], {})
            for row in s.get("results", []):
                tc = row.get("tile_classification", {})
                mcc_ci = tc.get("mcc_CI") or [None, None]
                w.writerow([
                    cell["label"], cell["config"], cell["k"], cell["role"],
                    row["R_m"], row["F1"], row["F1_CI"][0], row["F1_CI"][1],
                    tc.get("mcc"), mcc_ci[0], mcc_ci[1],
                    row["precision"], row["recall"],
                    tc.get("sensitivity"), tc.get("specificity"),
                ])
    print(f"Wrote {out}")


def write_summary_md(
    output_base: Path, summaries: dict[str, dict], gate_rows: list[dict],
    gate_passed: bool,
) -> None:
    """Write the human-readable headline (@50 m) table + gate verdict."""
    out = output_base / "TRACK2-SUMMARY.md"
    lines = [
        "# 55-map canonical extended-GT re-score (Track 2) — headline @ 50 m",
        "",
        f"**Validation gate**: {'✅ PASS' if gate_passed else '❌ FAIL'} "
        "(corrected-F1 @ 50 m vs findings §4b, 4 d.p.)",
        "",
        "| cell | config | k | role | F1@50m | MCC@50m |",
        "|---|---|---:|---|---:|---:|",
    ]
    for cell in CELLS:
        s = summaries.get(cell["label"], {})
        f1 = f1_at(s, 50)
        mcc = mcc_at(s, 50)
        f1s = f"{f1:.4f}" if f1 is not None else "—"
        mccs = f"{mcc:.4f}" if mcc is not None else "—"
        lines.append(
            f"| {cell['label']} | {cell['config']} | {cell['k']} | "
            f"{cell['role']} | {f1s} | {mccs} |"
        )
    lines += ["", "## Validation gate detail", "",
              "| cell | kind | target | got | Δ | verdict |",
              "|---|---|---:|---:|---:|---|"]
    for g in gate_rows:
        t = f"{g['target']:.6f}" if g["target"] is not None else "—"
        got = f"{g['got']:.6f}" if g["got"] is not None else "—"
        d = f"{g['delta']:+.2e}" if g["delta"] is not None else "—"
        lines.append(
            f"| {g['label']} | {g['kind']} | {t} | {got} | {d} | {g['verdict']} |"
        )
    out.write_text("\n".join(lines) + "\n")
    print(f"Wrote {out}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output-base", type=Path,
        default=REPO / "results/55maps-extended-gt-2026-06-07",
    )
    p.add_argument(
        "--workers", type=int, default=7,
        help="Process-pool workers (one per cell; <=14 ceiling on zbook).",
    )
    p.add_argument("--n-bootstrap", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--gate-tol", type=float, default=1e-4)
    p.add_argument(
        "--gate-only", action="store_true",
        help=(
            "Fast pre-flight: score ONLY the carry-forward cell at buffer 50 m "
            "with 200 bootstrap iters, check the gate, and exit. For a quick "
            "go/no-go before the full sweep."
        ),
    )
    return p.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    output_base: Path = args.output_base
    review_yesterday = ensure_empty_yesterday(output_base)

    # Validate inputs exist up-front (fail fast, before any compute).
    for cell in CELLS:
        det = REPO / cell["det"]
        if not det.exists():
            raise FileNotFoundError(f"Missing detections for {cell['label']}: {det}")
    for required in (STUDENT_GT, BOUNDS, CANONICAL_REVIEW):
        if not required.exists():
            raise FileNotFoundError(f"Missing required input: {required}")

    if args.gate_only:
        cell = CELLS[0]  # carry-forward TH7-k4
        out_dir = output_base / "_gate-only" / cell["label"]
        print(f"[gate-only] scoring {cell['label']} @ 50 m, 200 bootstrap...")
        score_one_cell(
            label=cell["label"], det_path=REPO / cell["det"],
            review_yesterday=review_yesterday, output_dir=out_dir,
            buffers=[50], n_bootstrap=200, seed=args.seed,
        )
        summary = json.loads((out_dir / "summary.json").read_text())
        got = f1_at(summary, 50)
        target = cell["gate_50m"]
        delta = abs(got - target)
        ok = delta <= args.gate_tol
        print(
            f"[gate-only] {cell['label']} F1@50m: got={got:.6f} "
            f"target={target:.6f} Δ={delta:.2e} → "
            f"{'PASS' if ok else 'FAIL'}"
        )
        sys.exit(0 if ok else 1)

    # Full run: score all 7 cells in parallel.
    summaries: dict[str, dict] = {}
    workers = max(1, min(args.workers, len(CELLS)))
    print(f"Scoring {len(CELLS)} cells with {workers} workers...")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {
            ex.submit(
                score_one_cell,
                label=cell["label"], det_path=REPO / cell["det"],
                review_yesterday=review_yesterday,
                output_dir=output_base / cell["label"],
                buffers=BUFFERS, n_bootstrap=args.n_bootstrap, seed=args.seed,
            ): cell["label"]
            for cell in CELLS
        }
        for fut in as_completed(futures):
            label = fut.result()
            summary_path = output_base / label / "summary.json"
            summaries[label] = json.loads(summary_path.read_text())
            print(f"  ✓ {label}")

    # Validation gate.
    gate_passed, gate_rows = run_validation_gate(summaries, args.gate_tol)
    (output_base / "validation-gate.json").write_text(
        json.dumps({"passed": gate_passed, "rows": gate_rows}, indent=2)
    )
    write_consolidated(output_base, summaries)
    write_summary_md(output_base, summaries, gate_rows, gate_passed)

    print("\n=== VALIDATION GATE ===")
    for g in gate_rows:
        if g["kind"] == "GATE":
            print(
                f"  {g['label']:8s} target={g['target']:.6f} "
                f"got={g['got']:.6f} Δ={g['delta']:.2e} {g['verdict']}"
            )
    print(f"GATE {'PASSED' if gate_passed else 'FAILED'}")
    sys.exit(0 if gate_passed else 1)


if __name__ == "__main__":
    main()
