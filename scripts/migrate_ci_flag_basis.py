#!/usr/bin/env python3
"""Migrate committed evaluations' ``ci_unreliable`` to the measured rule (D28).

Session 137 (commit ``6f8e31f97``) retired the sparse-coverage heuristic behind
``ci_unreliable`` — it detected a percentile-method pathology that the BCa
migration had already fixed — and replaced it with two measured grounds
(``assess_ci_reliability``): the interval excludes its own point estimate, or
coverage is partial (erratum E72). That commit deliberately re-emitted nothing,
so every committed artefact kept the superseded flag and none carried the
``ci_flag_basis`` vintage marker: the register still published 1,041 stale
``true`` flags across 91 of 337 conditions at the 20 m headline buffer,
including the paper's headline gold-standard cell (Session 137 audit,
finding F4; defect D28). The Principal Investigator ruled on 2026-08-20 to
migrate the corpus rather than keep it mixed-vintage.

What this does, for every git-tracked ``*evaluation.json``:

* recompute ``ci_unreliable`` per the measured rule from the row's OWN
  committed fields — ``excludes`` tests each of f1/precision/recall against
  its committed CI bounds (bounds absent → that metric is skipped, matching
  ``assess_ci_reliability``); ``partial`` is
  ``coverage_status == "partial_coverage"``;
* stamp ``ci_excludes_point``, ``sparse_coverage`` (descriptive, not a
  verdict), and ``ci_flag_basis`` — the standard
  ``"measured-exclusion-or-partial-coverage"`` where ``coverage_status`` is
  present, or ``"measured-exclusion-only"`` for adapter-written rows that
  carry no coverage information (there the E72 ground is unevaluable and the
  basis string must not claim it was evaluated);
* recompute every ``ci_unreliable_any_buffer`` rollup from its own buffers.

Both ``summary.buffers`` and every ``per_run[].buffers`` list are migrated.
Point estimates, CI bounds, coverage blocks, and every other field are
untouched; the script is idempotent (a second run changes nothing).

A machine-readable inventory of every changed file and flag flip is written to
``reports/ci-flag-migration-2026-08-20.json``.

Usage::

    python scripts/migrate_ci_flag_basis.py --dry-run   # count, write nothing
    python scripts/migrate_ci_flag_basis.py --write

$0 API; local. Created 2026-08-20 (Session 138, audit remediation Phase 2).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (  # noqa: E402
    CI_FLAG_BASIS_EXCLUSION_ONLY as BASIS_EXCLUSION_ONLY,
    CI_FLAG_BASIS_FULL as BASIS_FULL,
    CI_METRIC_BOUNDS as METRIC_BOUNDS,
    COVERAGE_STATUS_PARTIAL,
    COVERAGE_STATUS_SPARSE,
    measured_exclusion,
)

REPORT_PATH = PROJECT_ROOT / "reports/ci-flag-migration-2026-08-20.json"


def migrate_buffer_row(row: dict) -> dict | None:
    """Recompute the reliability block of one buffer row, in place.

    Returns a change record when anything moved, else ``None``. Rows carrying
    neither a flag nor any CI bound (nothing to assess) are left untouched.
    """
    has_any_bound = any(
        row.get(lo) is not None and row.get(hi) is not None
        for _, lo, hi in METRIC_BOUNDS
    )
    if "ci_unreliable" not in row and not has_any_bound:
        return None

    coverage_status = row.get("coverage_status")
    excludes = measured_exclusion(row)
    partial = coverage_status == COVERAGE_STATUS_PARTIAL
    new_flag = partial or excludes
    basis = BASIS_FULL if coverage_status is not None else BASIS_EXCLUSION_ONLY

    old_flag = row.get("ci_unreliable")
    changed = (
        old_flag != new_flag
        or row.get("ci_excludes_point") != excludes
        or row.get("ci_flag_basis") != basis
    )
    row["ci_unreliable"] = new_flag
    row["ci_excludes_point"] = excludes
    if coverage_status is not None:
        row["sparse_coverage"] = coverage_status == COVERAGE_STATUS_SPARSE
    row["ci_flag_basis"] = basis
    if not changed:
        return None
    return {
        "buffer_metres": row.get("buffer_metres"),
        "old_flag": old_flag,
        "new_flag": new_flag,
        "excludes": excludes,
        "partial_coverage": partial,
        "basis": basis,
    }


def migrate_doc(doc: dict) -> list[dict]:
    """Migrate every buffer list in one evaluation document, in place."""
    changes: list[dict] = []

    def do_block(block: dict, where: str) -> None:
        buffers = block.get("buffers")
        if not isinstance(buffers, list):
            return
        for row in buffers:
            if isinstance(row, dict):
                rec = migrate_buffer_row(row)
                if rec:
                    rec["where"] = where
                    changes.append(rec)
        if "ci_unreliable_any_buffer" in block:
            rollup = any(
                r.get("ci_unreliable", False)
                for r in buffers if isinstance(r, dict)
            )
            if block["ci_unreliable_any_buffer"] != rollup:
                changes.append({
                    "where": where,
                    "field": "ci_unreliable_any_buffer",
                    "old_flag": block["ci_unreliable_any_buffer"],
                    "new_flag": rollup,
                })
                block["ci_unreliable_any_buffer"] = rollup

    summary = doc.get("summary")
    if isinstance(summary, dict):
        do_block(summary, "summary")
    for i, run in enumerate(doc.get("per_run") or []):
        if isinstance(run, dict):
            do_block(run, f"per_run[{i}]")
    return changes


def main() -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true",
                       help="Report what would change; write nothing.")
    group.add_argument("--write", action="store_true",
                       help="Apply the migration and write the inventory.")
    args = ap.parse_args()

    tracked = [
        rel for rel in subprocess.run(
            ["git", "ls-files", "*evaluation.json"],
            capture_output=True, text=True, check=True, cwd=PROJECT_ROOT,
        ).stdout.split()
        # archive/** is deliberately excluded, matching erratum E82's
        # re-emission scope: archived artefacts are superseded historical
        # snapshots, and rewriting them would blur what "archived" means.
        if not rel.startswith("archive/")
    ]

    inventory: list[dict] = []
    stayed_flagged: list[dict] = []
    n_flag_flips = n_rows_touched = n_files_changed = 0
    for rel in tracked:
        path = PROJECT_ROOT / rel
        original = path.read_text()
        doc = json.loads(original)
        changes = migrate_doc(doc)
        # Census rows that remain flagged under the measured rule, from the
        # migrated in-memory document (correct in dry-run and write alike).
        # Each survivor is a genuine measured problem, not heuristic residue.
        for block in [doc.get("summary") or {}, *(doc.get("per_run") or [])]:
            for row in (block.get("buffers") or []):
                if isinstance(row, dict) and row.get("ci_unreliable") is True:
                    stayed_flagged.append({
                        "file": rel,
                        "buffer_metres": row.get("buffer_metres"),
                        "excludes": row.get("ci_excludes_point"),
                        "coverage_status": row.get("coverage_status"),
                    })
        if not changes:
            continue
        n_files_changed += 1
        n_rows_touched += len(changes)
        flips = [c for c in changes
                 if "old_flag" in c and c["old_flag"] != c["new_flag"]
                 and c.get("field") != "ci_unreliable_any_buffer"]
        n_flag_flips += len(flips)
        inventory.append({"file": rel, "n_changes": len(changes),
                          "flag_flips": flips})
        if args.write:
            trailing = "\n" if original.endswith("\n") else ""
            path.write_text(json.dumps(doc, indent=2) + trailing)

    print(f"tracked evaluations : {len(tracked)}")
    print(f"files changed       : {n_files_changed}")
    print(f"rows touched        : {n_rows_touched}")
    print(f"flag flips          : {n_flag_flips}")
    print(f"rows still flagged  : {len(stayed_flagged)}"
          f"{' (dry-run projection)' if args.dry_run else ''}")
    for row in stayed_flagged[:20]:
        print(f"  STILL FLAGGED: {row}")

    if args.write:
        REPORT_PATH.write_text(json.dumps({
            "migrated_at": "2026-08-20",
            "defect": "D28",
            "rule": "assess_ci_reliability (measured exclusion or partial "
                    "coverage); see scripts/evaluate_detections.py",
            "n_tracked": len(tracked),
            "n_files_changed": n_files_changed,
            "n_rows_touched": n_rows_touched,
            "n_flag_flips": n_flag_flips,
            "still_flagged": stayed_flagged,
            "files": inventory,
        }, indent=2) + "\n")
        print(f"inventory -> {REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
