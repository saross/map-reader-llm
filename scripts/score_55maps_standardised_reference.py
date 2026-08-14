#!/usr/bin/env python3
"""Score the eight 55-map board cells against the ruling-21 standardised reference.

Queue items 2 and 3 of
``reports/verification/reference-standardisation-queue.md`` (execution
contract § Execution contract; PI go 2026-08-14): give the T=0.3 run its
full-buffer evaluation (item 2) and unify F1 and tile-level MCC onto a
single shared reference across the eight board cells (item 3). The T=0.3
cells are scored ONCE here and registered under both items.

Legs, following the item-1 A/B/C vintage-decomposition template
(Dawid–Skene report § 6.3):

- **Leg A — reproduction gate + corrected legacy baseline.** Two
  sub-legs per cell, both against the LEGACY reference (reviewed student
  GT 4,746 + ring-gated ``canonical-review.csv`` phantoms) at R = 50 m:

  - **A0** runs with ``dedup_tolerance_m = 0`` — the exact configuration
    that produced the committed Track-2 values
    (``results/55maps-extended-gt-2026-06-07/``, 2026-06-07, which
    PRE-DATE the W6-E9 channel-duplicate fix ``1de559119``). A0 must
    reproduce the committed F1 within 1e-6. "Reproduce before you vary"
    — a red gate is a contract stop state, never absorbed.
  - **A1** runs with the current default (5 m de-duplication) and is the
    corrected legacy baseline for the decomposition. A1 − A0 is the
    W6-E9 fix itself: the canonical review's one true twin (0.98 m,
    ruling 20c) stops double-counting, removing one spurious FN —
    a uniform ≈ +8.7e-05 across all cells. The driver asserts exactly
    one drop per cell.

- **Leg B — diagnostic decomposition.** Standardised STUDENT layer +
  legacy ring-gated phantoms at R = 50 m. B − A1 isolates the
  student-layer standardisation (including its knock-on de-duplication
  changes); C − B isolates the extension-layer overhaul (ring-gated
  detection positions → 279 marked centres, included whole at every R).
  Diagnostic only, not citable (item-1 precedent: B fits uncommitted).

- **Leg C — publication scoring.** Standardised student layer +
  standardised extension layer, full 14-buffer sweep, tile MCC on the
  SAME reference, 10,000-iteration bootstrap. F1 and MCC now share one
  reference — item 3's completion gate. Post-run hard checks: every row
  of every cell must show 0 duplicate drops and all 279 extension
  records admitted.

Reference-consumption semantics (read at source per the S132 start
instruction): the standardised extension layer carries marked centres
(±2.5 m), so the legacy localisation gate (``build_phantom_gdf``'s
``buffer_metres <= R``; Obs 371) is dissolved and the layer enters the
extended GT whole at every buffer — see
``compute_corrected_f1_multi_buffer.load_standardised_extension``.

Contract mechanics enforced here:

- Feature-count crosscheck of each cell's detection GeoJSON against the
  documented n_detections BEFORE any scoring (Session 77 wrong-source
  class); mismatch is a hard stop.
- The A0 gate runs and passes BEFORE legs B/C execute. Running B or C
  without leg A in the same invocation requires a prior
  ``validation-gate.json`` in the output base showing a PASS for every
  requested cell.
- ``validation-gate.json`` is written immediately after the gate is
  evaluated, so a later crash cannot destroy the gate evidence.

Pure deterministic re-scoring of committed artefacts; NO API, US$0.
Compute on sapphire (project rule); use ``--jobs 8`` there for
cell-level parallelism (the engine itself is single-threaded).

Usage::

    # Pre-flight smoke (fast): checks + leg A + C at R=[20,50], one cell
    python scripts/score_55maps_standardised_reference.py --smoke

    # Full run (sapphire):
    python scripts/score_55maps_standardised_reference.py \\
        --legs A B C --jobs 8

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import contextlib
import csv
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
STUDENT_LEGACY = (
    REPO / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
)
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
# summary.json, PRE-W6-E9 — reproduced by sub-leg A0 with dedup disabled).
CELLS = [
    {
        "label": "TH7-k4", "config": "text-high-T0.7", "k": 4,
        "role": "carry-forward",
        "det": ("outputs/55maps-text-high-generalisation/"
                "verified/verified_detections.geojson"),
        "n_det": 4164, "gate_legacy_50m": 0.8152278820375335,
    },
    {
        "label": "TH7-k3", "config": "text-high-T0.7", "k": 3,
        "role": "threshold",
        "det": ("results/deployment-oracle-2026-06-06/k3-scoring/"
                "55maps-text-high-generalisation/k3_verified.geojson"),
        "n_det": 4786, "gate_legacy_50m": 0.8424650648436715,
    },
    {
        "label": "T03-k4", "config": "text-high-T0.3", "k": 4,
        "role": "config (item 2: the t0.3 run)",
        "det": ("outputs/55maps-text-high-t0.3-generalisation/"
                "verified/verified_detections.geojson"),
        "n_det": 4350, "gate_legacy_50m": 0.8358742508674167,
    },
    {
        "label": "T03-k3", "config": "text-high-T0.3", "k": 3,
        "role": "ORACLE (item 2: the t0.3 run)",
        "det": ("results/deployment-oracle-2026-06-06/k3-scoring/"
                "55maps-text-high-t0.3-generalisation/k3_verified.geojson"),
        "n_det": 4905, "gate_legacy_50m": 0.8476058017087225,
    },
    {
        "label": "TM-k4", "config": "text-min", "k": 4, "role": "config",
        "det": ("outputs/55maps-text-min-generalisation/"
                "verified/verified_detections.geojson"),
        "n_det": 3865, "gate_legacy_50m": 0.7830711278528694,
    },
    {
        "label": "TM-k3", "config": "text-min", "k": 3, "role": "threshold",
        "det": ("results/deployment-oracle-2026-06-06/k3-scoring/"
                "55maps-text-min-generalisation/k3_verified.geojson"),
        "n_det": 4279, "gate_legacy_50m": 0.8127118644067797,
    },
    {
        "label": "IM-k3", "config": "image", "k": 3,
        "role": "config (carried)",
        "det": ("outputs/55maps-image-generalisation/"
                "verified/verified_detections.geojson"),
        "n_det": 4680, "gate_legacy_50m": 0.7986993191748807,
    },
    {
        "label": "TM-n10-k5", "config": "text-min-n10", "k": 5,
        "role": "uplift",
        "det": "results/55map-leaderboard/min11-uplift-5of10-pt0.15.geojson",
        "n_det": 4361, "gate_legacy_50m": 0.8290275152278933,
    },
]

# A0 reproduces the committed numbers under their own configuration, so the
# tolerance is float-path noise only (S105 observed ~2e-7), not a band that
# could absorb a real engine change.
GATE_TOL = 1e-6
# Expected channel-duplicate drops in A1: the canonical review's single true
# twin vs the legacy student layer (0.98 m, ruling 20c).
A1_EXPECTED_DROPS = 1
SMOKE_CELL = "TH7-k4"
SMOKE_BUFFERS = [20, 50]


def preflight_paths(cells: list[dict]) -> None:
    """Hard-stop if any fixed input or detection file is missing."""
    fixed = {
        "standardised student layer": STUDENT_STD,
        "standardised extension layer": EXTENSION_STD,
        "legacy student layer": STUDENT_LEGACY,
        "canonical review": CANONICAL_REVIEW,
        "bounds": BOUNDS,
    }
    missing = [f"{name}: {path}" for name, path in fixed.items()
               if not path.exists()]
    missing += [f"{c['label']} detections: {c['det']}" for c in cells
                if not (REPO / c["det"]).exists()]
    if missing:
        raise SystemExit(
            "missing input file(s) — stop state:\n  " + "\n  ".join(missing)
        )
    print(f"  paths OK: {len(fixed)} fixed inputs, {len(cells)} cell inputs")


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
        f"min nearest_student_m pinned at {min_d} m"
    )


def ensure_empty_yesterday(output_base: Path) -> Path:
    """Header-only review CSV for legacy-mode legs (single-source pattern)."""
    output_base.mkdir(parents=True, exist_ok=True)
    path = output_base / "empty-yesterday-review.csv"
    path.write_text("candidate_id,human_label,buffer_metres,x,y,map_name\n")
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
            dedup_tolerance_m=job["dedup_tolerance_m"],
        )
    with open(out_dir / "summary.json", encoding="utf-8") as fh:
        summary = json.load(fh)
    return {"label": job["label"], "leg": job["leg"], "summary": summary}


def row_at(summary: dict | None, r_m: int) -> dict | None:
    """The result row at buffer R from a cell summary (None if absent)."""
    if summary is None:
        return None
    for row in summary.get("results", []):
        if row.get("R_m") == r_m:
            return row
    return None


def f1_at(summary: dict | None, r_m: int) -> float | None:
    """Corrected-F1 point estimate at buffer R (None if absent)."""
    row = row_at(summary, r_m)
    return row.get("F1") if row else None


def mcc_at(summary: dict | None, r_m: int) -> float | None:
    """Tile MCC at buffer R (None if absent)."""
    row = row_at(summary, r_m)
    return (row.get("tile_classification") or {}).get("mcc") if row else None


def build_jobs(
    cells: list[dict], legs: list[str], output_base: Path,
    n_bootstrap: int, seed: int, empty_yesterday: Path,
    buffers_c: list[int],
) -> list[dict]:
    """Expand cells × legs into worker job dicts.

    Leg "A" expands into sub-legs A0 (dedup disabled — the exact
    reproduction of the pre-W6-E9 committed numbers) and A1 (current
    engine — the corrected legacy baseline).
    """
    jobs = []
    for cell in cells:
        det = str(REPO / cell["det"])
        legacy = {
            "det": det, "student_gt": str(STUDENT_LEGACY),
            "review_yesterday": str(empty_yesterday),
            "review_today": str(CANONICAL_REVIEW),
            "buffers": [50], "n_bootstrap": 200, "seed": seed,
            "compute_mcc": False,
        }
        if "A" in legs:
            jobs.append({
                **legacy, "label": cell["label"], "leg": "A0",
                "out_dir": str(output_base / "repro-gate" / cell["label"]),
                "dedup_tolerance_m": 0.0,
            })
            jobs.append({
                **legacy, "label": cell["label"], "leg": "A1",
                "out_dir": str(
                    output_base / "legacy-baseline" / cell["label"]
                ),
                "dedup_tolerance_m": 5.0,
            })
        if "B" in legs:
            jobs.append({
                **legacy, "label": cell["label"], "leg": "B",
                "student_gt": str(STUDENT_STD),
                "out_dir": str(output_base / "b-diagnostic" / cell["label"]),
                "dedup_tolerance_m": 5.0,
            })
        if "C" in legs:
            jobs.append({
                "label": cell["label"], "leg": "C", "det": det,
                "student_gt": str(STUDENT_STD),
                "extension_csv": str(EXTENSION_STD),
                "out_dir": str(output_base / cell["label"]),
                "buffers": buffers_c, "n_bootstrap": n_bootstrap,
                "seed": seed, "compute_mcc": True,
                "dedup_tolerance_m": 5.0,
            })
    return jobs


def evaluate_gate(
    cells: list[dict], results: dict[tuple[str, str], dict],
) -> tuple[bool, list[dict]]:
    """A0 reproduction gate plus A1 baseline checks.

    Every cell must carry an A0 summary whose F1 @ 50 m matches the
    committed value within GATE_TOL, and an A1 summary whose duplicate
    drop count is exactly A1_EXPECTED_DROPS. A missing summary is a
    FAIL, never a skip; an empty cell list cannot pass.
    """
    rows = []
    all_pass = bool(cells)
    for cell in cells:
        a0 = row_at(results.get((cell["label"], "A0")), 50)
        a1 = row_at(results.get((cell["label"], "A1")), 50)
        if a0 is None or a1 is None:
            all_pass = False
            rows.append({
                "label": cell["label"], "target": cell["gate_legacy_50m"],
                "got": None, "delta": None, "tol": GATE_TOL,
                "verdict": "FAIL (missing A0/A1 summary)",
            })
            print(f"  gate {cell['label']:10s} FAIL — missing A0/A1 summary")
            continue
        got = a0["F1"]
        delta = got - cell["gate_legacy_50m"]
        drops = a1.get("n_phantom_duplicates_dropped")
        ok = abs(delta) <= GATE_TOL and drops == A1_EXPECTED_DROPS
        all_pass &= ok
        rows.append({
            "label": cell["label"], "target": cell["gate_legacy_50m"],
            "got": got, "delta": delta, "tol": GATE_TOL,
            "a1_f1": a1["F1"], "a1_minus_a0_dedup_fix": a1["F1"] - got,
            "a1_drops": drops, "a1_expected_drops": A1_EXPECTED_DROPS,
            "verdict": "PASS" if ok else "FAIL",
        })
        print(
            f"  gate {cell['label']:10s} "
            f"target={cell['gate_legacy_50m']:.7f} got={got:.7f} "
            f"delta={delta:+.2e}  A1-A0={a1['F1'] - got:+.2e} "
            f"drops={drops}  {'PASS' if ok else 'FAIL'}"
        )
    return all_pass, rows


def check_c_leg(
    cells: list[dict], results: dict[tuple[str, str], dict],
    expected_buffers: list[int],
) -> list[dict]:
    """Post-C hard checks: whole extension layer admitted, zero drops.

    Guards against silent truncation of the reference between load and
    scoring (audit finding S1) AND against a buffer-truncated sweep
    (re-audit M2): every C summary must carry exactly the expected
    buffer rows, each showing all N_EXTENSION_STD records admitted and
    0 duplicate drops. An empty result list can never pass.
    """
    rows = []
    failures = []
    for cell in cells:
        summary = results.get((cell["label"], "C"))
        if summary is None:
            failures.append(f"{cell['label']}: no C summary")
            continue
        result_rows = summary.get("results", [])
        got_buffers = sorted(r.get("R_m") for r in result_rows)
        if got_buffers != sorted(expected_buffers):
            failures.append(
                f"{cell['label']}: buffers {got_buffers} != expected "
                f"{sorted(expected_buffers)}"
            )
            continue
        cell_ok = True
        for row in result_rows:
            if (row.get("n_reviewer_promoted_at_R") != N_EXTENSION_STD
                    or row.get("n_phantom_duplicates_dropped") != 0):
                cell_ok = False
                failures.append(
                    f"{cell['label']} R={row.get('R_m')}: "
                    f"admitted={row.get('n_reviewer_promoted_at_R')} "
                    f"drops={row.get('n_phantom_duplicates_dropped')}"
                )
        if cell_ok:
            rows.append({
                "label": cell["label"],
                "n_extension_admitted": N_EXTENSION_STD,
                "n_drops": 0,
                "n_buffers": len(got_buffers),
                "verdict": "OK",
            })
    if failures:
        raise SystemExit(
            "C-leg extension census FAILED — stop state:\n  "
            + "\n  ".join(failures)
        )
    print(f"  C-leg extension census OK for {len(rows)} cell(s): "
          f"{N_EXTENSION_STD} admitted, 0 drops, every buffer")
    return rows


def require_prior_gate(cells: list[dict], gate_path: Path) -> dict:
    """B/C without leg A: demand a prior PASS gate covering these cells.

    Returns the prior gate payload so the caller can carry its
    certification forward into any rewritten gate file (never clobber a
    PASS with ``null``).
    """
    if not gate_path.exists():
        raise SystemExit(
            "legs B/C requested without leg A, and no prior "
            f"validation-gate.json at {gate_path} — the reproduction gate "
            "must pass before anything varies (contract stop state)"
        )
    with open(gate_path, encoding="utf-8") as fh:
        gate = json.load(fh)
    # Freshness binding (re-audit C1): a prior gate certifies THIS engine
    # only if it was produced at the current commit with the current
    # tolerance and carries the A0/A1 schema. Anything else — an older
    # engine, a looser tolerance, a pre-A0-redesign gate — must be
    # re-earned by re-running leg A, never inherited.
    current_commit = engine.git_commit_hash()
    stale = []
    if gate.get("git_commit") != current_commit:
        stale.append(
            f"git_commit {gate.get('git_commit')} != current "
            f"{current_commit}"
        )
    if gate.get("gate_tolerance") != GATE_TOL:
        stale.append(
            f"gate_tolerance {gate.get('gate_tolerance')} != {GATE_TOL}"
        )
    if stale:
        raise SystemExit(
            f"prior gate at {gate_path} is STALE ({'; '.join(stale)}) — "
            "re-run leg A against the current engine"
        )
    passed_labels = {
        r["label"] for r in gate.get("gate_rows", [])
        if r.get("verdict") == "PASS"
        and r.get("a1_drops") is not None
        and r.get("a1_drops") == r.get("a1_expected_drops")
    }
    missing = [c["label"] for c in cells if c["label"] not in passed_labels]
    if gate.get("gate_passed") is not True or missing:
        raise SystemExit(
            f"prior gate at {gate_path} does not certify cell(s) "
            f"{missing or '(gate not passed)'} — re-run leg A first"
        )
    print(f"  prior gate OK: {gate_path} certifies "
          f"{len(cells)} requested cell(s)")
    return gate


def write_consolidated(
    output_base: Path, cells: list[dict],
    results: dict[tuple[str, str], dict], legs: list[str],
) -> None:
    """Consolidated per-cell CSV + decomposition table at 50 m."""
    if "C" in legs:
        path = output_base / "consolidated-standardised.csv"
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
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
                for row in summary.get("results", []):
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

    # A0/A1/B/C decomposition at the 50 m headline
    decomp = []
    for cell in cells:
        entry = {
            "cell": cell["label"],
            "A0_committed": cell["gate_legacy_50m"],
        }
        for leg in ("A0", "A1", "B", "C"):
            entry[leg] = f1_at(results.get((cell["label"], leg)), 50)
        if entry.get("C") is not None:
            entry["mcc_C"] = mcc_at(results.get((cell["label"], "C")), 50)
        if entry.get("A0") is not None and entry.get("A1") is not None:
            entry["A1_minus_A0_dedup_fix"] = entry["A1"] - entry["A0"]
        if entry.get("A1") is not None and entry.get("B") is not None:
            entry["B_minus_A1_student_layer"] = entry["B"] - entry["A1"]
        if entry.get("B") is not None and entry.get("C") is not None:
            entry["C_minus_B_extension_layer"] = entry["C"] - entry["B"]
        decomp.append(entry)
    path = output_base / "abc-decomposition-50m.json"
    # Merge-on-write (re-audit M1): a partial invocation must refresh
    # only the cells and legs it computed, never null out fields an
    # earlier fuller run established.
    if path.exists():
        with open(path, encoding="utf-8") as fh:
            existing = {
                e["cell"]: e
                for e in json.load(fh).get("cells", [])
            }
        for entry in decomp:
            prior_entry = existing.get(entry["cell"], {})
            for key, value in prior_entry.items():
                if entry.get(key) is None and value is not None:
                    entry[key] = value
        for cell_label, prior_entry in existing.items():
            if cell_label not in {e["cell"] for e in decomp}:
                decomp.append(prior_entry)
    # Recompute derived deltas after the merge — a partial run may have
    # supplied the missing half of a pair (idempotent on full runs).
    for entry in decomp:
        pairs = [
            ("A1_minus_A0_dedup_fix", "A1", "A0"),
            ("B_minus_A1_student_layer", "B", "A1"),
            ("C_minus_B_extension_layer", "C", "B"),
        ]
        for key, hi, lo in pairs:
            if entry.get(hi) is not None and entry.get(lo) is not None:
                entry[key] = entry[hi] - entry[lo]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": engine.git_commit_hash(),
        "note": (
            "F1 @ 50 m. A0 = exact reproduction of the committed "
            "(pre-W6-E9) legacy numbers with de-duplication disabled — "
            "the gate. A1 = legacy reference on the current engine "
            "(5 m de-dup); A1-A0 is the W6-E9 fix (the canonical "
            "review's one 0.98 m twin, ruling 20c). B = standardised "
            "student + legacy ring-gated phantoms (diagnostic, NOT "
            "citable); B-A1 isolates the student-layer move, and "
            "absorbs the layer's knock-on de-dup changes (the marked "
            "student positions sit closer to some phantom records). "
            "C = standardised reference (publication); C-B isolates "
            "the extension-layer move."
        ),
        "cells": decomp,
    }
    path.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {path}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--legs", nargs="+", choices=["A", "B", "C"],
        default=["A", "B", "C"],
        help=(
            "Which legs to run (default: all). B/C without A require a "
            "prior PASS validation-gate.json in the output base. "
            "--smoke overrides this to A + C."
        ),
    )
    p.add_argument(
        "--cells", nargs="+", default=None,
        help="Subset of cell labels (default: all 8). "
             "Not combinable with --smoke.",
    )
    p.add_argument(
        "--output-base", type=Path,
        default=REPO / "results/55maps-standardised-ref-2026-08-14",
        help="Output directory root (default: the dated results dir).",
    )
    p.add_argument(
        "--n-bootstrap", type=int, default=10_000,
        help="Bootstrap iterations for leg C (default: 10000).",
    )
    p.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for bootstrap reproducibility (default: 42).",
    )
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
            f"Fast pre-flight: checks + legs A and C on the {SMOKE_CELL} "
            f"cell only, C at R={SMOKE_BUFFERS} with 200 bootstrap. "
            "Not combinable with --cells."
        ),
    )
    return p.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    if args.smoke and args.cells:
        raise SystemExit("--smoke and --cells are mutually exclusive")

    output_base = args.output_base
    if args.smoke:
        # Smoke runs are pre-flight throwaways: quarantine them in their
        # own subdirectory so they can never clobber a full run's gate,
        # decomposition, or consolidated CSV (re-audit M1).
        output_base = output_base / "smoke"
    output_base.mkdir(parents=True, exist_ok=True)

    cells = CELLS
    if args.smoke:
        cells = [c for c in CELLS if c["label"] == SMOKE_CELL]
    elif args.cells:
        cells = [c for c in CELLS if c["label"] in args.cells]
        missing = set(args.cells) - {c["label"] for c in cells}
        if missing:
            raise SystemExit(f"unknown cell label(s): {sorted(missing)}")
    if not cells:
        raise SystemExit("cell selection is empty — nothing to score")

    legs = ["A", "C"] if args.smoke else args.legs
    n_bootstrap = 200 if args.smoke else args.n_bootstrap
    buffers_c = SMOKE_BUFFERS if args.smoke else BUFFERS

    print("Pre-flight checks...")
    preflight_paths(cells)
    census_checks()
    crosscheck_rows = crosscheck_feature_counts(cells)

    empty_yesterday = ensure_empty_yesterday(output_base)
    gate_path = output_base / "validation-gate.json"

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

    results: dict[tuple[str, str], dict] = {}

    # Leg A runs — and gates — BEFORE anything varies (contract:
    # "reproduce before you vary"). A red gate halts here; B/C never run.
    gate_passed = None
    gate_rows: list[dict] = []
    c_rows: list[dict] = []

    def write_gate() -> None:
        gate_path.write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "git_commit": engine.git_commit_hash(),
            "feature_count_crosscheck": crosscheck_rows,
            "gate_tolerance": GATE_TOL,
            "gate_passed": gate_passed,
            "gate_rows": gate_rows,
            "c_leg_extension_census": c_rows,
        }, indent=2))
        print(f"Wrote {gate_path}")

    if "A" in legs:
        a_jobs = build_jobs(
            cells, ["A"], output_base, n_bootstrap, args.seed,
            empty_yesterday, buffers_c,
        )
        print(f"\nLeg A (A0 reproduction gate + A1 baseline): "
              f"{len(a_jobs)} job(s), jobs={args.jobs}...")
        run_jobs(a_jobs, results)
        print("\nLeg-A reproduction gate:")
        gate_passed, gate_rows = evaluate_gate(cells, results)
        # Persist the gate evidence IMMEDIATELY — a later B/C crash must
        # not destroy it (audit finding 5).
        write_gate()
        if not gate_passed:
            raise SystemExit(
                "leg-A reproduction gate FAILED — contract stop state: "
                "halt and escalate; legs B/C were NOT run"
            )
    else:
        prior = require_prior_gate(cells, gate_path)
        # Carry the prior certification forward so the end-of-run gate
        # rewrite preserves it rather than clobbering PASS with null —
        # including the C-leg census when C is not re-run this
        # invocation (re-audit M1).
        gate_passed = prior.get("gate_passed")
        gate_rows = prior.get("gate_rows", [])
        c_rows = prior.get("c_leg_extension_census", [])
        crosscheck_rows = prior.get(
            "feature_count_crosscheck", crosscheck_rows,
        )

    bc_legs = [leg for leg in legs if leg in ("B", "C")]
    if bc_legs:
        bc_jobs = build_jobs(
            cells, bc_legs, output_base, n_bootstrap, args.seed,
            empty_yesterday, buffers_c,
        )
        print(f"\nLegs {bc_legs}: {len(bc_jobs)} job(s), jobs={args.jobs}...")
        run_jobs(bc_jobs, results)
        if "C" in bc_legs:
            fresh_c = check_c_leg(cells, results, expected_buffers=buffers_c)
            # Merge by label so a subset re-run refreshes its own cells
            # without discarding other cells' carried census rows.
            merged = {r["label"]: r for r in c_rows}
            merged.update({r["label"]: r for r in fresh_c})
            c_rows = list(merged.values())
        write_gate()
    write_consolidated(output_base, cells, results, legs)
    print("\nAll requested legs complete.")


if __name__ == "__main__":
    main()
