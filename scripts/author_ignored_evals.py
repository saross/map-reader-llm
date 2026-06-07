#!/usr/bin/env python3
"""
Close-out sweep: populate ``_ignored_evals`` for every decomposed run.
=====================================================================

After a run is decomposed (its headline operating points minted as conditions),
the remaining scored evaluations under that run — non-headline vote/prob
thresholds, superseded scope/aggregation siblings, replicate variants — are
**deliberate exclusions**, not omissions. Until they are explicitly waived,
``verify_run_conditions.py`` emits a benign ``unclaimed-eval`` WARN for each,
which drowns out any genuinely-new omission.

This sweep registers every currently-unclaimed scored eval in each run's
``_ignored_evals`` (the un-authored set IS the ignore set, per the agreed
close-out design). After it runs, the drift-check becomes a **sharp completeness
guard**: any NEW unclaimed eval added later is a real signal.

The unclaimed set is computed with the SAME logic as
``verify_run_conditions.verify_completeness`` (shared ``_build_eval_index`` +
identical claimed/auto-detections matching), so a write here drives the
``unclaimed-eval`` WARN count to zero without masking anything the verifier
would otherwise have flagged.

Usage
-----
    # Per-run counts + a sample of the evals that would be waived (writes nothing)
    python scripts/author_ignored_evals.py

    # Write _ignored_evals into results/run-conditions.json
    python scripts/author_ignored_evals.py --write

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-06-08
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_post_run_report as g  # noqa: E402

CONDITIONS_JSON = REPO_ROOT / "results" / "run-conditions.json"


def unclaimed_for_run(directory_path: str, conditions: list[dict],
                      index: dict) -> list[str]:
    """Return the sorted eval_rel paths under a run that no condition claims.

    Mirrors ``verify_run_conditions.verify_completeness`` exactly (with an empty
    starting ignore set) so the result is precisely the set the verifier would
    flag as ``unclaimed-eval``.

    Args:
        directory_path: The run's ``directory_path`` from the registry.
        conditions: The run's condition specs.
        index: The shared eval index (``_build_eval_index``).

    Returns:
        Sorted list of repo-relative ``evaluation.json`` paths to waive.
    """
    dir_prefix = g._normalise_detections_path(directory_path.rstrip("/") + "/")
    claimed = {s["eval_path"] for s in conditions if s.get("eval_path")}
    auto_dets = {
        g._normalise_detections_path(s["detections"])
        for s in conditions
        if not s.get("eval_path") and s.get("detections")
    }
    unclaimed: set[str] = set()
    for det_path, evals in index.items():
        if not det_path.startswith(dir_prefix):
            continue
        for eval_rel, _summary, _bounds in evals:
            if eval_rel in claimed or det_path in auto_dets:
                continue
            unclaimed.add(eval_rel)
    return sorted(unclaimed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Populate _ignored_evals for every decomposed run "
        "(dry-run by default)."
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Write _ignored_evals into results/run-conditions.json.",
    )
    args = parser.parse_args(argv)

    doc = json.loads(CONDITIONS_JSON.read_text())
    decomposition = doc["decomposition"]
    registry = {
        e["run_id"]: e
        for e in g.load_run_registry().get("registry", [])
    }
    index = g._build_eval_index()

    total = 0
    per_run: dict[str, list[str]] = {}
    for run_id, block in decomposition.items():
        entry = registry.get(run_id)
        if entry is None:
            continue
        unclaimed = unclaimed_for_run(
            entry["directory_path"], block.get("conditions", []), index
        )
        if unclaimed:
            per_run[run_id] = unclaimed
            total += len(unclaimed)

    print("UNCLAIMED EVALS TO WAIVE (per run):")
    for run_id in sorted(per_run, key=lambda r: -len(per_run[r])):
        evals = per_run[run_id]
        print(f"\n  {run_id}: {len(evals)}")
        for e in evals[:3]:
            print(f"      {e}")
        if len(evals) > 3:
            print(f"      … (+{len(evals) - 3} more)")
    print(f"\nTotal: {total} evals across {len(per_run)} runs.")

    if not args.write:
        print("\nDRY-RUN — run-conditions.json not modified. Use --write.")
        return 0

    for run_id, evals in per_run.items():
        decomposition[run_id]["_ignored_evals"] = evals
    CONDITIONS_JSON.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"\nWROTE _ignored_evals to {len(per_run)} runs "
          f"in {CONDITIONS_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
