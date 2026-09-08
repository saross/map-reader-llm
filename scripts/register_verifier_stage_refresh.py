#!/usr/bin/env python3
"""Register the three refreshed verifier stages as ``verifier_passes`` inventory rows.

Card step 5.1 of ``planning/verifier-stage-refresh-2026-09-08.md`` (Session 151).
The recovery-consistency audit (``reports/recovery-consistency-audit-2026-09-08.md``
§ 3) found three text-only adversarial verifier stages whose candidate sets were
built from passes the E71 recovery later rewrote. They were re-run on
2026-09-08 (sapphire, commit ``43516df9a``) on candidate sets rebuilt from the
recovered passes, into NEW dated stage directories beside the originals. This
script registers those directories in ``results/run-conditions.json`` as
``verifier_passes`` inventory rows — the register's third input, from which the
manifest generator lifts pass rows — and appends a dated ``_note`` to each
affected run's decomposition.

The rows are inventory only: no registered condition or analysis cites the
refreshed stages, so nothing in the paper moves (card § 5). The originals keep
their rows as the pre-recovery record (archive, never delete).

Row keys and paths follow the generator's own draft
(``generate_post_run_report.py --draft-run <run_id>``), so a later draft/verify
pass finds the register and the disk in agreement.

Usage
-----
    python scripts/register_verifier_stage_refresh.py --dry-run   # report only
    python scripts/register_verifier_stage_refresh.py             # write

Then regenerate the manifests::

    python scripts/generate_post_run_report.py --all --write
    python scripts/verify_run_conditions.py

Idempotent: a second run reports "nothing to do". A key that already exists
with a DIFFERENT path is an error, never silently overwritten.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_CONDITIONS = REPO_ROOT / "results" / "run-conditions.json"
OUTPUTS = REPO_ROOT / "outputs" / "h11"

#: The card that controls this block (§ 1 table lists the three stages).
CARD = "planning/verifier-stage-refresh-2026-09-08.md"

#: Date stamp shared by the three stage directories and the ``_note`` entries.
REFRESH_DATE = "2026-09-08"

#: One entry per refreshed stage: (run_id, row key, modality, path relative to the
#: run's output directory, expected candidate count from the card § 1 table, key of
#: the pre-recovery stage it sits beside — None where the original was never
#: registered).
STAGES: tuple[dict[str, Any], ...] = (
    {
        "run_id": "pv-diag-384",
        "key": "flash-high-image-n5-image-t0.0-verified-v1-n10-recovery-2026-09-08",
        "modality": "image",
        "path": "flash-high-image-n5/image-t0.0/verified-v1-n10-recovery-2026-09-08",
        "n_candidates": 889,
        "beside": "flash-high-image-n5-image-t0.0-verified-v1-n10",
    },
    {
        "run_id": "pv-diag-384",
        "key": "flash-high-text-n5-text-t0.0-verified-v1-n3-recovery-2026-09-08",
        "modality": "text",
        "path": "flash-high-text-n5/text-t0.0/verified-v1-n3-recovery-2026-09-08",
        "n_candidates": 1319,
        "beside": "flash-high-text-n5-text-t0.0-verified-v1-n3",
    },
    {
        "run_id": "e47-propose-brief",
        "key": "verified-flash-high-text-1of5-recovery-2026-09-08",
        "modality": "text",
        "path": "verified/flash-high-text-1of5-recovery-2026-09-08",
        "n_candidates": 4149,
        "beside": None,
    },
)

#: Appended to each affected run's ``_note`` (pipe-separated, matching the
#: register's existing convention for later additions).
NOTES: dict[str, str] = {
    "pv-diag-384": (
        f"Verifier-stage refresh ({REFRESH_DATE}, S151; card {CARD}): the two "
        "text-only adversarial v1 stages on the t0.0 pools "
        "(image verified-v1-n10, text verified-v1-n3) were re-run on candidate "
        "sets rebuilt from the E71-recovered passes (889 and 1,319 candidates) "
        "into the '-recovery-2026-09-08' directories registered here as "
        "inventory rows beside the originals, which stay as the pre-recovery "
        "record. No condition cites either. Comparison: "
        "reports/recovery-consistency-audit-2026-09-08.md § 6.1."
    ),
    "e47-propose-brief": (
        f"Verifier-stage refresh ({REFRESH_DATE}, S151; card {CARD}): first "
        "verifier_passes row. The text-only adversarial v1 stage on the pool's "
        "rebuilt vote>=1 consensus (4,149 candidates) at "
        "verified/flash-high-text-1of5-recovery-2026-09-08 is complete; the "
        "pre-recovery verified/flash-high-text-1of5 attempt (57 of 4,358 "
        "verified, crops gone) stays unregistered as an abandoned stage. No "
        "condition cites it. Comparison: "
        "reports/recovery-consistency-audit-2026-09-08.md § 6.1."
    ),
}


def check_stage_on_disk(stage: dict[str, Any], outputs: Path = OUTPUTS) -> list[str]:
    """Return the problems (empty if none) with a stage directory on disk.

    Checks the three files the sweep pipeline leaves behind exist and that
    ``probabilities.json`` holds exactly the card's candidate count — a count that
    disagrees with the card is a stop state (card § 4), not a row to register.

    Args:
        stage: One entry of :data:`STAGES`.
        outputs: The ``outputs/h11`` root (overridable for tests).

    Returns:
        A list of human-readable problems; an empty list means the stage is sound.
    """
    problems: list[str] = []
    stage_dir = outputs / stage["run_id"] / stage["path"]
    if not stage_dir.is_dir():
        return [f"{stage['key']}: directory missing: {stage_dir}"]
    for name in ("run.meta.json", "probabilities.json", "sweep_2d.json"):
        if not (stage_dir / name).is_file():
            problems.append(f"{stage['key']}: {name} missing")
    probs = stage_dir / "probabilities.json"
    if probs.is_file():
        data = json.loads(probs.read_text(encoding="utf-8"))
        n_results = len(data.get("results", {}))
        if n_results != stage["n_candidates"]:
            problems.append(
                f"{stage['key']}: probabilities.json holds {n_results} results, "
                f"card says {stage['n_candidates']}")
        missing = [k for k, v in data.get("results", {}).items()
                   if v.get("mound_probability") is None]
        if missing:
            problems.append(
                f"{stage['key']}: {len(missing)} candidates without a probability")
    return problems


def plan(rc: dict[str, Any]) -> list[dict[str, Any]]:
    """Compute the register edits still needed; empty when already applied.

    Args:
        rc: The parsed ``results/run-conditions.json``.

    Returns:
        A list of actions, each ``{"kind": "row"|"note", "run_id": ..., ...}``.

    Raises:
        ValueError: A row key already exists with a different path (a collision
            is never silently overwritten).
    """
    actions: list[dict[str, Any]] = []
    for stage in STAGES:
        run = rc["decomposition"][stage["run_id"]]
        existing = run.setdefault("verifier_passes", {}).get(stage["key"])
        if existing is None:
            actions.append({"kind": "row", **stage})
        elif existing.get("path") != stage["path"]:
            raise ValueError(
                f"{stage['run_id']}::{stage['key']} already registered with path "
                f"{existing.get('path')!r}, expected {stage['path']!r}")
    for run_id, note in NOTES.items():
        current = rc["decomposition"][run_id].get("_note") or ""
        if note not in current:
            actions.append({"kind": "note", "run_id": run_id, "note": note})
    return actions


def apply(rc: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    """Apply :func:`plan`'s actions to the register in place."""
    for action in actions:
        run = rc["decomposition"][action["run_id"]]
        if action["kind"] == "row":
            run["verifier_passes"][action["key"]] = {
                "modality": action["modality"], "path": action["path"]}
        elif action["kind"] == "note":
            current = run.get("_note") or ""
            run["_note"] = f"{current} | {action['note']}" if current else action["note"]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point; returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Report the planned edits and disk checks; write nothing.")
    args = parser.parse_args(argv)

    problems = [p for stage in STAGES for p in check_stage_on_disk(stage)]
    if problems:
        print("STOP — stage directories disagree with the card:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 2

    rc = json.loads(RUN_CONDITIONS.read_text(encoding="utf-8"))
    actions = plan(rc)
    if not actions:
        print("nothing to do — the three stages are already registered")
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
    # ensure_ascii=False keeps the register's existing em-dashes literal (no escape churn).
    RUN_CONDITIONS.write_text(
        json.dumps(rc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {RUN_CONDITIONS.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
