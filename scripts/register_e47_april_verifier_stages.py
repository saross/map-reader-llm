#!/usr/bin/env python3
"""Register the two April e47 verifier stages as ``verifier_passes`` inventory rows.

PI ruling 2026-09-08 (Session 151, "yes, register"): the two verifier-stage
directories under ``outputs/h11/e47-propose-brief/verified/`` that the manifest
generator's draft decomposition proposes but the register never carried become
inventory rows beside the refreshed stage
(``scripts/register_verifier_stage_refresh.py``):

* ``verified/flash-high-text-1of5`` — the April (pre-recovery) text-only
  adversarial v1 verification of the pool's 1-of-5 union, 4,358 candidates,
  verified 2026-04-09 (``52b0215a6``) with a 57-crop gap closed by the
  2026-05-06 cleanup (``6683952ac``, whose 57-crop ``run.meta.json`` overwrote
  the original). Complete; never swept in place (the S151 like-for-like sweep
  lives under ``results/recovery-reeval-2026-09-08/e47-propose-brief/``).
* ``verified/text-baseline`` — the same verifier applied 2026-04-08
  (``42f07bc3b``) to the 1,180 detections of the N=1 ``propose_brief`` single
  pass (the registered ``baseline-single-pass`` condition's detections).

The ``2of5``–``5of5`` sibling directories are CPU-derived vote-threshold subsets
of the 1-of-5 probabilities (``derive_vote_threshold_results.py``), not verifier
runs, and stay unregistered. Neither row is cited by a condition or analysis;
nothing in the paper moves.

Usage
-----
    python scripts/register_e47_april_verifier_stages.py --dry-run
    python scripts/register_e47_april_verifier_stages.py
    python scripts/generate_post_run_report.py --all --write

Idempotent; reuses the refresh registrar's disk checks and plan/apply.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:  # the repo's sibling-import convention
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.register_verifier_stage_refresh import (  # noqa: E402
    RUN_CONDITIONS,
    apply,
    check_stage_on_disk,
    plan,
    write_register,
)

RULING_DATE = "2026-09-08"

#: The two rows (keys and paths as the generator's draft proposes). ``has_sweep``
#: False: these stages were never swept in place, so the disk check does not
#: demand a ``sweep_2d.json``.
STAGES: tuple[dict[str, Any], ...] = (
    {
        "run_id": "e47-propose-brief",
        "key": "verified-flash-high-text-1of5",
        "modality": "text",
        "path": "verified/flash-high-text-1of5",
        "n_candidates": 4358,
        "beside": "verified-flash-high-text-1of5-recovery-2026-09-08",
        "has_sweep": False,
    },
    {
        "run_id": "e47-propose-brief",
        "key": "verified-text-baseline",
        "modality": "text",
        "path": "verified/text-baseline",
        "n_candidates": 1180,
        "beside": None,
        "has_sweep": False,
    },
)

NOTES: dict[str, str] = {
    "e47-propose-brief": (
        f"PI ruling {RULING_DATE} (S151, 'yes, register'): the April stages "
        "verified/flash-high-text-1of5 (4,358 of 4,358, complete after the "
        "2026-05-06 cleanup; the pre-recovery record of the refreshed stage) and "
        "verified/text-baseline (the same text-only adversarial v1 verifier on the "
        "N=1 propose_brief pass's 1,180 detections, 2026-04-08) are registered as "
        "inventory rows. The 2of5-5of5 directories are CPU-derived vote-threshold "
        "subsets of the 1of5 probabilities, not verifier runs, and stay "
        "unregistered. No condition cites either. Like-for-like sweep of the April "
        "1of5 stage: results/recovery-reeval-2026-09-08/e47-propose-brief/."
    ),
}


def main(argv: list[str] | None = None) -> int:
    """CLI entry point; returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Report the planned edits and disk checks; write nothing.")
    args = parser.parse_args(argv)

    problems = [p for stage in STAGES for p in check_stage_on_disk(stage)]
    if problems:
        print("STOP — stage directories disagree with this script:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 2

    rc = json.loads(RUN_CONDITIONS.read_text(encoding="utf-8"))
    actions = plan(rc, stages=STAGES, notes=NOTES)
    if not actions:
        print("nothing to do — the two April stages are already registered")
        return 0
    for action in actions:
        if action["kind"] == "row":
            print(f"row   {action['run_id']}::{action['key']} -> {action['path']}")
        else:
            print(f"note  {action['run_id']}: {action['note'][:70]}…")
    if args.dry_run:
        print("dry run — nothing written")
        return 0
    apply(rc, actions)
    write_register(rc)
    print("wrote results/run-conditions.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
