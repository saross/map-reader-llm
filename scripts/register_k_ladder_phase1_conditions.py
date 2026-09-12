#!/usr/bin/env python3
"""
Author the conditions the K-ladder Phase-1 run adds to the register.

Two independent groups, selected with ``--rows``:

``recovery-vintage`` (step 3; PI ruling B2 / R4)
    One row, ``pv-diag-384::pv-high-text-t0.0-n3-recovery-2026-09-08-opmax``:
    the September re-verification of the rebuilt ``flash-high-text-n5``
    ``text-t0.0`` union, at the same operating point (vote_t 3, prob_t 0.15) as
    the April cell. Under the PI's "keep history, present the best available"
    principle this cell is that configuration's representative on ladders and
    boards; the April row ``pv-high-text-t0.0-n3-opmax`` stays registered and
    unchanged as the archived board's cell. All of its inputs were produced and
    committed in Session 153 (``results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/staleness-2026-09-11/current-vintage/``);
    nothing is recomputed here and no API call is made.

``first-n-twins`` (step 2; PI ruling B3)
    The pre-verifier twins of the 27 blocked pairing rows, materialised by
    ``scripts/materialise_first_n_ladder_twin.py`` and scored on each verified
    cell's own recipe. Nine distinct rungs serve the 27 rows, because rows
    sharing a (pool, N, k) share one twin.

The ``-recovery-<date>`` label suffix is a sanctioned notation extension
(``docs/methodology/notation-key.md`` § 7.2): the same configuration
re-verified on a rebuilt candidate union, where the date is the
re-verification stage's.

Gates — the script refuses to write if any fails
------------------------------------------------
1. No label collides with an existing condition of the same run.
2. Every ``eval_path`` and ``detections`` path exists on disk.
3. Each row's evaluation reproduces the F1 the row claims at its gate buffer,
   to 1e-6.
4. Each evaluation's ``summary.n_detections`` equals its GeoJSON feature count
   (the Session-77 cross-check rule, ``feedback_feature_count_crosscheck``).
5. No PI signature field is touched: this script writes only to
   ``results/run-conditions.json``, never to ``results/run-analyses.json``.

Dry run by default. After writing::

    python scripts/generate_post_run_report.py --all --write

Usage::

    python scripts/register_k_ladder_phase1_conditions.py --rows recovery-vintage
    python scripts/register_k_ladder_phase1_conditions.py --rows recovery-vintage --write

Created: 2026-09-12 (Session 154, K-ladder Phase 1 steps 2 and 3)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_CONDITIONS = PROJECT_ROOT / "results/run-conditions.json"

STALENESS_DIR = (
    "results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/"
    "staleness-2026-09-11/current-vintage")

#: The one row of the ``recovery-vintage`` group, with the F1 its evaluation
#: must reproduce at the gate buffer and the feature count it must match.
RECOVERY_ROWS: list[dict[str, Any]] = [
    {
        "run_id": "pv-diag-384",
        "gate_buffer_m": 20,
        "gate_f1": 0.8508,
        "gate_n_detections": 423,
        "row": {
            "label": "pv-high-text-t0.0-n3-recovery-2026-09-08-opmax",
            "architecture": "proposer-verifier",
            "aggregation": "verified",
            "proposer_pool": "flash-high-text-n5-text-t0.0",
            "n_passes": 3,
            "vote_threshold": 3,
            "prob_threshold": 0.15,
            "verifier_config": {
                "variant": "v1",
                "instruction_file": "verify_adversarial.md",
                "model": "gemini-3-flash-preview",
                "thinking_level": "minimal",
                "temperature": 0.0,
                "iterations": 1,
            },
            "eval_path": f"{STALENESS_DIR}/era2-eval/evaluation.json",
            "detections": (
                f"{STALENESS_DIR}/pv-high-text-t0.0-n3-current-vintage.geojson"),
            "_note": (
                "CURRENT-VINTAGE PAIR of pv-high-text-t0.0-n3 (PI rulings B2 and "
                "R4, 2026-09-12; planning/k-ladder-review-2026-09-11.md § 4). The "
                "same configuration and the same operating point (vote_t 3, "
                "prob_t 0.15) as pv-diag-384::pv-high-text-t0.0-n3-opmax, applied "
                "to the proposer union as committed today (1,319 features, "
                "re-materialised 2026-07-30 at f6116cba0 / 77bb342b4) against the "
                "COMPLETE 2026-09-08 re-verification of that union — stage "
                "flash-high-text-n5-text-t0.0-verified-v1-n3-recovery-2026-09-08 "
                "(43516df9a, US$1.82 already spent, same verifier config and "
                "system-instruction hash 2518d529). n 423, Era-2-frame F1@20 "
                "0.8508, tile-MCC 0.7857, against the April cell's 403 / 0.8234 / "
                "0.7750. The argmax does not move between vintages: both sweeps "
                "put it at (3, 0.15), and each reproduces its committed "
                "sweep_2d.json in all 240 rows "
                "(results/leaderboard/era2/gs-era2-verified-board-2026-09-10/"
                "opmax/staleness-2026-09-11/README.md). Under the PI's 'keep "
                "history, present the best available' principle THIS row is the "
                "configuration's representative on ladders and boards; the April "
                "row pv-high-text-t0.0-n3-opmax REMAINS the archived "
                "per-architecture Era-2 PV board's cell, registered and "
                "unchanged, and is correct on its own vintage. The "
                "'-recovery-<date>' suffix is the sanctioned notation for a "
                "configuration re-verified on a rebuilt union "
                "(docs/methodology/notation-key.md § 7.2); the date is the "
                "re-verification stage's, not this registration's. Zero API "
                "spend in this registration."),
        },
    },
]


class RegistrationGateError(RuntimeError):
    """A gate failed, so nothing was written."""


def f1_at(doc: dict[str, Any], buffer_m: int) -> float | None:
    """The point F1 an evaluation records at one buffer."""
    for band in (doc.get("summary") or {}).get("buffers", []):
        if band.get("buffer_metres") == buffer_m or band.get("buffer_m") == buffer_m:
            return float(band["f1"])
    return None


def check_row(spec: dict[str, Any], existing: dict[str, list[str]]) -> None:
    """Run every gate against one row spec.

    Args:
        spec: A row spec with ``run_id``, ``row`` and the gate values.
        existing: Labels already registered, per run id.

    Raises:
        RegistrationGateError: On the first gate that fails.
    """
    run_id, row = spec["run_id"], spec["row"]
    if row["label"] in existing.get(run_id, []):
        raise RegistrationGateError(
            f"{run_id}::{row['label']} is already registered; refusing to "
            "author a duplicate")
    for field in ("eval_path", "detections"):
        path = PROJECT_ROOT / row[field]
        if not path.exists():
            raise RegistrationGateError(
                f"{run_id}::{row['label']}: {field} {row[field]} does not exist")
    doc = json.loads((PROJECT_ROOT / row["eval_path"]).read_text(encoding="utf-8"))
    got_f1 = f1_at(doc, spec["gate_buffer_m"])
    if got_f1 is None or abs(got_f1 - spec["gate_f1"]) > 1e-6:
        raise RegistrationGateError(
            f"{run_id}::{row['label']}: evaluation records F1@"
            f"{spec['gate_buffer_m']} = {got_f1}, the row claims "
            f"{spec['gate_f1']}")
    got_n = (doc.get("summary") or {}).get("n_detections")
    if got_n != spec["gate_n_detections"]:
        raise RegistrationGateError(
            f"{run_id}::{row['label']}: evaluation records n_detections "
            f"{got_n}, the row claims {spec['gate_n_detections']}")
    geo = json.loads((PROJECT_ROOT / row["detections"]).read_text(encoding="utf-8"))
    n_features = len(geo.get("features") or [])
    if n_features != got_n:
        raise RegistrationGateError(
            f"{run_id}::{row['label']}: the detection GeoJSON holds "
            f"{n_features} features but the evaluation scored {got_n} — the "
            "Session-77 wrong-source class; refusing to register")


def main(argv: list[str] | None = None) -> int:
    """Check the selected rows and, with ``--write``, author them."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--rows", default="recovery-vintage",
                        choices=("recovery-vintage",),
                        help="Which group of rows to author. The first-n-twins "
                             "group is authored by the same flow once the twins "
                             "are materialised and scored.")
    parser.add_argument("--write", action="store_true",
                        help="Author the rows. Without it, gates run and "
                             "nothing is written.")
    args = parser.parse_args(argv)

    specs = RECOVERY_ROWS
    doc = json.loads(RUN_CONDITIONS.read_text(encoding="utf-8"))
    dec = doc["decomposition"]
    existing = {run_id: [c["label"] for c in entry.get("conditions", [])]
                for run_id, entry in dec.items()}

    try:
        for spec in specs:
            check_row(spec, existing)
    except RegistrationGateError as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2

    for spec in specs:
        print(f"GATES PASS  {spec['run_id']}::{spec['row']['label']}  "
              f"F1@{spec['gate_buffer_m']} {spec['gate_f1']}  "
              f"n {spec['gate_n_detections']}")

    if not args.write:
        print("\nDry run. Pass --write to author, then run "
              "`python scripts/generate_post_run_report.py --all --write`.")
        return 0

    for spec in specs:
        dec[spec["run_id"]]["conditions"].append(spec["row"])
    # indent=1 with ensure_ascii=False round-trips the committed file
    # byte-for-byte, so the diff is the added rows and nothing else.
    RUN_CONDITIONS.write_text(
        json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nauthored {len(specs)} condition row(s) into "
          f"{RUN_CONDITIONS.relative_to(PROJECT_ROOT)}")
    print("Next: python scripts/generate_post_run_report.py --all --write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
