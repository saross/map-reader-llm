#!/usr/bin/env python3
"""Ruling 3a (PI, 2026-09-07): register the post-E71 re-scores BESIDE the pinned record.

Nine legacy conditions (``n1-outstanding-384`` x 8, ``e47-propose-brief``
``single-pass-run_4``) carry evaluations the E82 replay (2026-08-21) scored
against VINTAGE-FROZEN inputs — the detections as committed before the E71
dead-tile recovery (``99ae28ec4``, 2026-07-30) rewrote them on disk. The
register's numbers are therefore the pre-recovery record (D40: a pinned cell
"honestly records scoring against the then-current input, but does not
reproduce from current inputs"). Session 149 re-scored all nine against the
recovered files into ``results/rescore-2026-09-07/`` (``26cc430ad``): none
reproduces, and pro-image-high-t0 moves +0.03 F1 through recall.

The PI's ruling follows D40's own precedent (2026-08-20: re-scores to current
inputs land as NEW conditions beside the historical ones):

1. the pinned row stays the record and is STAMPED with ``input_vintage`` —
   the commit its detections were frozen at, read from the evaluation's own
   ``_metadata.e82_input_vintage`` — so ``verify_run_conditions.py`` can check
   it against that vintage (a reproduction gate) instead of the working tree
   (a currency gate) and report it as disclosed rather than broken;
2. a ``<label>-post-e71`` clone registers the re-score, pointing at the
   rescore home and the SAME (now recovered) detections path.

Nothing is swapped; no analysis row moves. Dry-run by default; ``--write``
persists idempotently (a row already stamped or already cloned is skipped),
preserving the file's serialisation (indent 1, trailing newline). Then run
``verify_run_conditions.py`` — the two runs should read PARTIAL, not FAIL.

Usage::

    python scripts/register_post_e71_conditions.py          # plan (no write)
    python scripts/register_post_e71_conditions.py --write

Zero API. Seconds.

Created: 2026-09-07 (Session 150)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
RUN_CONDITIONS = REPO / "results/run-conditions.json"
RESCORE_HOME = REPO / "results/rescore-2026-09-07"
SUFFIX = "-post-e71"
RECOVERY_COMMIT = "99ae28ec4"
ERRATUM = "E71"

#: The nine the ruling names. Discovery from the rescore home must reproduce
#: this set exactly; anything else is a stop state, not a silent extension.
EXPECTED = frozenset({
    ("n1-outstanding-384", "pro-image-high-t0-single-pass-run_1"),
    ("n1-outstanding-384", "pro-image-high-t0-single-pass-run_2"),
    ("n1-outstanding-384", "pro-image-high-t0-single-pass-run_3"),
    ("n1-outstanding-384", "pro-text-high-t0-single-pass-run_1"),
    ("n1-outstanding-384", "pro-text-high-t0-single-pass-run_2"),
    ("n1-outstanding-384", "pro-text-high-t0-single-pass-run_3"),
    ("n1-outstanding-384", "baseline-pro-image-high-t-0-0"),
    ("n1-outstanding-384", "baseline-pro-text-high-t-0-0"),
    ("e47-propose-brief", "single-pass-run_4"),
})


def discover_rescores(home: Path = RESCORE_HOME) -> dict[tuple[str, str], Path]:
    """Map ``(run_id, label)`` to the re-scored ``evaluation.json`` under ``home``."""
    found: dict[tuple[str, str], Path] = {}
    for run_dir in sorted(p for p in home.iterdir() if p.is_dir()):
        for cond_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
            ev = cond_dir / "evaluation.json"
            if ev.exists():
                found[(run_dir.name, cond_dir.name)] = ev
    return found


def pinned_commit(spec: dict[str, Any]) -> str:
    """The commit the pinned evaluation froze this row's detections at.

    Read from the evaluation's own ``_metadata.e82_input_vintage`` (the E82
    replay's record of each input's commit at the cell's scoring timestamp),
    keyed by the row's registered ``detections`` path.

    Raises:
        SystemExit: if the evaluation does not pin exactly that path.
    """
    meta = json.loads((REPO / spec["eval_path"]).read_text(encoding="utf-8"))["_metadata"]
    vintage = meta.get("e82_input_vintage") or {}
    commit = vintage.get(spec["detections"])
    if not commit:
        sys.exit(f"{spec['label']}: e82_input_vintage does not pin {spec['detections']!r} "
                 f"(keys: {sorted(vintage)})")
    return str(commit)


def stamp_for(spec: dict[str, Any], commit: str) -> dict[str, Any]:
    """The ``input_vintage`` object written onto a pinned row."""
    return {
        "pinned": "pre-e71",
        "detections_commit": commit,
        "recovery_commit": RECOVERY_COMMIT,
        "basis": (
            "E82 vintage-frozen replay (D40): the evaluation scored the detections as "
            f"committed at {commit}; the E71 dead-tile recovery ({RECOVERY_COMMIT}, "
            "2026-07-30) rewrote the file on disk afterwards, so this row reproduces "
            "against its vintage, not against the working tree"
        ),
        "superseded_measurement": spec["label"] + SUFFIX,
        "erratum": ERRATUM,
        "ruling": "3a (PI, 2026-09-07): the pinned evaluation stays the record; "
                  "the post-recovery re-score registers beside it",
    }


def clone_for(spec: dict[str, Any], eval_rel: str) -> dict[str, Any]:
    """The ``-post-e71`` row: the same condition, scored on the recovered detections."""
    clone = {k: copy.deepcopy(v) for k, v in spec.items()
             if k not in ("eval_path", "notes", "input_vintage")}
    clone["label"] = spec["label"] + SUFFIX
    clone["eval_path"] = eval_rel
    clone["notes"] = (
        f"Post-E71 re-score (S149, 2026-09-07, 26cc430ad) of the pinned row "
        f"'{spec['label']}' against the recovered detections (IM-k4 recipe, GS reference, "
        "14 buffers, BCa 10,000/42). Registered BESIDE the pinned record under D40's "
        "'new conditions beside the historical ones' ruling (PI 2026-08-20) and ruling 3a "
        "(PI 2026-09-07). Same detections path; the pinned row's input_vintage names the "
        "commit it scored."
    )
    return clone


def plan(rc: dict[str, Any], rescores: dict[tuple[str, str], Path]) -> list[dict[str, Any]]:
    """Compute the actions (stamps and clones) the register still needs.

    Args:
        rc: The loaded ``run-conditions.json`` document.
        rescores: Output of :func:`discover_rescores`.

    Returns:
        Action dicts ``{"kind": "stamp"|"clone", "run_id", "label", ...}``, in
        register order. Empty when the ruling is fully applied (idempotence).

    Raises:
        SystemExit: if the discovered set is not exactly the nine the ruling names,
            or a named row is missing from the register.
    """
    if set(rescores) != EXPECTED:
        sys.exit("rescore home does not hold exactly the nine ruled conditions:\n"
                 f"  unexpected: {sorted(set(rescores) - EXPECTED)}\n"
                 f"  missing:    {sorted(EXPECTED - set(rescores))}")
    actions: list[dict[str, Any]] = []
    for (run_id, label), ev in sorted(rescores.items()):
        conds = rc["decomposition"][run_id]["conditions"]
        by_label = {c["label"]: c for c in conds}
        if label not in by_label:
            sys.exit(f"{run_id}::{label} is not a registered condition")
        spec = by_label[label]
        if "input_vintage" not in spec:
            actions.append({"kind": "stamp", "run_id": run_id, "label": label,
                            "input_vintage": stamp_for(spec, pinned_commit(spec))})
        if label + SUFFIX not in by_label:
            actions.append({"kind": "clone", "run_id": run_id, "label": label,
                            "row": clone_for(spec, str(ev.relative_to(REPO)))})
    return actions


def apply(rc: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    """Apply the planned actions in place; a clone is inserted right after its row."""
    for act in actions:
        conds = rc["decomposition"][act["run_id"]]["conditions"]
        idx = next(i for i, c in enumerate(conds) if c["label"] == act["label"])
        if act["kind"] == "stamp":
            conds[idx]["input_vintage"] = act["input_vintage"]
        else:
            conds.insert(idx + 1, act["row"])


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--write", action="store_true", help="persist (default: plan only)")
    args = ap.parse_args(argv)

    raw = RUN_CONDITIONS.read_text(encoding="utf-8")
    trailing = "\n" if raw.endswith("\n") else ""
    rc = json.loads(raw)
    actions = plan(rc, discover_rescores())
    for act in actions:
        if act["kind"] == "stamp":
            print(f"  stamp   {act['run_id']}::{act['label']}  "
                  f"input_vintage.detections_commit={act['input_vintage']['detections_commit']}")
        else:
            print(f"  clone   {act['run_id']}::{act['row']['label']}  -> {act['row']['eval_path']}")
    n_stamp = sum(a["kind"] == "stamp" for a in actions)
    n_clone = sum(a["kind"] == "clone" for a in actions)
    if not actions:
        print("nothing to do — ruling 3a is fully applied")
        return 0
    if not args.write:
        print(f"{n_stamp} stamp(s), {n_clone} clone(s) — dry run; pass --write to persist")
        return 0
    apply(rc, actions)
    RUN_CONDITIONS.write_text(json.dumps(rc, indent=1, ensure_ascii=False) + trailing,
                              encoding="utf-8")
    print(f"wrote {n_stamp} stamp(s) and {n_clone} clone(s) to {RUN_CONDITIONS.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
