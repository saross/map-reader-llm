#!/usr/bin/env python3
"""
Step 7a of the r2 recompute chain: register every ``-r2-gt`` condition row.

Reference revision r2 (``planning/reference-revision-2026-09-06.md``)
re-scores every 55-map board cell against the revised reference. The
boards resolve their cells -- and read their NUMBERS -- through registered
condition rows (``build_55map_leaderboard.py`` takes F1, CI, MCC and
``n_detections`` from each row's ``eval_path``), so registration is part
of the chain, not paperwork after it.

On r1 the ``-standardised-gt`` rows were written by THREE scripts
(``register_standardised_gt_conditions.py`` for the eight leaderboard
cells, ``register_pass2_author.py`` for the final-board cells,
``register_gemini37_author.py`` for the 3.7 campaign). r2 needs the same
rows again with new suffix, new homes and, for every oracle and rung, a
new operating point. This single registrar does both halves (PI ruling,
Session 149 -- one command for 7a, one place to audit):

**7a-i, clone** (runs after step 3, before the r2 leaderboard): every
``-standardised-gt`` row whose ``eval_path`` lies in the r1 SCORING home
(``results/55maps-standardised-ref-2026-08-14/``) is cloned to ``-r2-gt``
with ``eval_path`` retargeted to the r2 scoring home. Detections are the
same files -- a reference revision changes the scoring, not the
detections.

**7a-ii, author** (runs after step 4's sweep and stage-2 scoring): every
materialised cell in the r2 board manifest gets a row whose operating
point comes from the r2 sweep, ``eval_path`` and ``detections`` from the
r2 board home. Label schemes follow the r1 registrars per family, so the
r1 and r2 rows for one cell sort together. Coincident oracles (an r2
argmax that landed on a committed set) are skipped exactly as
``register_pass2_author.py`` skipped them on r1 -- the clone of the
committed row IS their registration.

Dry-run by default: prints every row it would add. ``--write`` persists,
idempotently (existing labels are skipped), preserving the file's
serialisation. Then run ``verify_run_conditions.py``.

Usage::

    python scripts/register_r2_conditions.py            # plan (no write)
    python scripts/register_r2_conditions.py --write    # 7a-i + 7a-ii
    python scripts/register_r2_conditions.py --write --only clone

Zero API. Seconds.

Created: 2026-09-07 (Session 149)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.register_pass2_author import (  # noqa: E402
    AB_CELL,
    VF_CONFIG,
    parse_point,
)

RUN_CONDITIONS = REPO / "results/run-conditions.json"
R1_SCORING = "results/55maps-standardised-ref-2026-08-14"
R2_SCORING = "results/55maps-r2-ref-2026-09-06"
R2_BOARD = REPO / "results/55map-final-board-r2-2026-09-06"
SUFFIX_R1 = "-standardised-gt"
SUFFIX_R2 = "-r2-gt"

R2_NOTE = (
    "Reference-revision-r2 evaluation (card planning/reference-revision-"
    "2026-09-06.md): the standardised reference with the PI's cluster- and "
    "empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked "
    "centres, included whole at every R). Scored by evaluate_detections.py "
    "(14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for "
    "the whole r2 chain."
)
CROSSREF_NOTE = (
    "Reference-revision-r2 track (Session 149): the -r2-gt conditions score "
    "the same detection sets against reference revision r2 and supersede the "
    "-standardised-gt cells as the paper reference; see "
    "results/55maps-r2-ref-2026-09-06/, results/55map-final-board-r2-"
    "2026-09-06/ and planning/reference-revision-2026-09-06.md."
)

#: Board-cell families -> (run id, template selector, n_passes) for the
#: authored rows. ``template`` is a label prefix in that run whose
#: architecture / aggregation / verifier_config the new row copies; None
#: means "build from VF_CONFIG" (the carry-forward Gemini-3 verifier).
INCUMBENT_RUN = {
    "TH7": ("55maps-text-high-generalisation", 5),
    "T03": ("55maps-text-high-t0-3-generalisation", 5),
    "TM": ("55maps-text-min-generalisation", 5),
    "IM": ("55maps-image-generalisation", 5),
    "UPL": ("55maps-text-min-n10-uplift", 10),
}
G37_RUN = "gemini37-55map-2026-08-29"
STRIDE_RUN = "stride-55map-2026-08-25"
G37_TEMPLATE = {"ARM1": "arm1-n5-carried", "ARM2": "arm2-n5-carried"}
FOURTH_TEMPLATE = "g384-ov192-55map-k10-verified37"

#: Committed r1 operating points of the oracle cells that coincided with a
#: committed detection set on r1 (mirrors final_board_build.COINCIDENT_POINTS).
COINCIDENT_POINTS = {"TH7-oracle": (0.15, 3), "IM-oracle": (0.15, 3),
                     "UPL-oracle": (0.15, 5)}

_CELL_RE = re.compile(r"^(?P<fam>[A-Z0-9]+)(?:-N(?P<n>\d+))?-(?P<basis>oracle|carried)$")


def clone_scoring_rows(dec: dict) -> list[tuple[str, dict, str]]:
    """7a-i: clone the r1 scoring-home rows to r2.

    Args:
        dec: ``decomposition`` block of run-conditions.json (not mutated).

    Returns:
        (run id, new row, status) per candidate; status ``add`` or ``skip``.
    """
    plan = []
    for run_id, run in dec.items():
        labels = {c.get("label") for c in run["conditions"]}
        for cond in run["conditions"]:
            label = cond.get("label", "")
            if not label.endswith(SUFFIX_R1):
                continue
            if not str(cond.get("eval_path", "")).startswith(R1_SCORING):
                continue  # board-home rows are authored in 7a-ii instead
            new = copy.deepcopy(cond)
            new["label"] = label[: -len(SUFFIX_R1)] + SUFFIX_R2
            new["eval_path"] = cond["eval_path"].replace(R1_SCORING, R2_SCORING, 1)
            cell = Path(cond["eval_path"]).parent.name
            new["_note"] = f"{cell} {R2_NOTE}"
            status = "skip" if new["label"] in labels else "add"
            plan.append((run_id, new, status))
    return plan


def _template(dec: dict, run_id: str, prefix: str) -> dict:
    """The r1 row whose label starts with ``prefix`` (fields to copy)."""
    for c in dec[run_id]["conditions"]:
        if c.get("label", "").startswith(prefix):
            return c
    raise KeyError(f"{run_id}: no template row starting {prefix!r}")


def author_board_rows(dec: dict, manifest: list[dict],
                      board: dict | None) -> list[tuple[str, dict, str]]:
    """7a-ii: author a row for every materialised r2 board cell.

    Args:
        dec: ``decomposition`` block (not mutated).
        manifest: ``cells`` of the r2 board's ``cells_manifest.json``.
        board: The r2 ``final_board_50m.json`` if built (its F1 goes into
            the note), else None.

    Returns:
        (run id, new row, status) per cell.
    """
    f1_of = {c["label"]: c["f1_50"] for c in (board or {}).get("cells", [])}
    plan = []
    for m in manifest:
        label = m["label"]
        if m.get("committed_eval"):
            continue  # the four incumbents: covered by the 7a-i clones
        pt, pk = parse_point(m["point"])
        if label in COINCIDENT_POINTS and (pt, pk) == COINCIDENT_POINTS[label]:
            plan.append((None, {"label": label}, "coincident"))
            continue
        mm = _CELL_RE.match(label)
        if not mm:
            raise ValueError(f"unrecognised board cell label {label!r}")
        fam, n, basis = mm.group("fam"), mm.group("n"), mm.group("basis")
        posthoc = "posthoc-" if "post-hoc" in m.get("basis", "") else ""
        f1_txt = f", F1@50 {f1_of[label]:.4f}" if label in f1_of else ""
        common = {
            "architecture": "proposer-verifier",
            "aggregation": "verified",
            "vote_threshold": pk,
            "prob_threshold": pt,
            "eval_path": f"{R2_BOARD.relative_to(REPO)}/cells/{label}/evaluation.json",
            "detections": m["det"],
            "_note": (f"r2 board cell {label} ({m.get('basis', basis)}{f1_txt}, "
                      f"tier via final_board_50m.json). {R2_NOTE}"),
        }
        if fam in AB_CELL:  # stride A/B and their rungs
            run_id = STRIDE_RUN
            row = {"label": (f"{AB_CELL[fam].replace('_', '-')}-n{n}-{basis}-"
                             f"{posthoc}p{pt:.2f}-k{pk}{SUFFIX_R2}"),
                   "proposer_pool": AB_CELL[fam], "n_passes": int(n),
                   "verifier_config": dict(VF_CONFIG), **common}
        elif fam in INCUMBENT_RUN:  # the five incumbent oracles
            run_id, n_passes = INCUMBENT_RUN[fam]
            row = {"label": f"verified-oracle-p{pt:.2f}-k{pk}{SUFFIX_R2}",
                   "proposer_pool": None, "n_passes": n_passes,
                   "verifier_config": dict(VF_CONFIG), **common}
        elif fam in G37_TEMPLATE:  # 3.7 arms and their rungs
            run_id = G37_RUN
            tpl = _template(dec, run_id, G37_TEMPLATE[fam])
            row = {"label": f"{fam.lower()}-n{n}-{basis}-p{pt:.2f}-k{pk}{SUFFIX_R2}",
                   "proposer_pool": tpl["proposer_pool"], "n_passes": int(n),
                   "verifier_config": copy.deepcopy(tpl["verifier_config"]),
                   "n_candidates": tpl.get("n_candidates"), **common}
        elif fam == "FOURTH":  # B K=10 union + 3.7 verifier, and its rungs
            run_id = STRIDE_RUN
            tpl = _template(dec, run_id, FOURTH_TEMPLATE)
            row = {"label": (f"g384-ov192-55map-n{n}-verified37-{basis}-"
                             f"p{pt:.2f}-k{pk}{SUFFIX_R2}"),
                   "proposer_pool": tpl.get("proposer_pool", "g384_ov192_55map"),
                   "n_passes": int(n),
                   "verifier_config": copy.deepcopy(tpl["verifier_config"]),
                   "n_candidates": tpl.get("n_candidates"), **common}
        else:
            raise ValueError(f"no registration scheme for family {fam!r} ({label})")
        labels = {c.get("label") for c in dec[run_id]["conditions"]}
        plan.append((run_id, row, "skip" if row["label"] in labels else "add"))
    return plan


def apply(dec: dict, plan: list[tuple[str, dict, str]]) -> int:
    """Append the ``add`` rows (and the crossref note once per run)."""
    n = 0
    for run_id, row, status in plan:
        if status != "add":
            continue
        run = dec[run_id]
        run["conditions"].append(row)
        note = run.get("_note", "")
        if "Reference-revision-r2 track" not in note:
            run["_note"] = (note + " " + CROSSREF_NOTE).strip()
        n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="Persist (default: plan only).")
    ap.add_argument("--only", choices=("clone", "author"), default=None,
                    help="Run one half only (7a-i clone, 7a-ii author).")
    args = ap.parse_args()

    rc = json.loads(RUN_CONDITIONS.read_text())
    dec = rc["decomposition"]
    plan: list[tuple[str, dict, str]] = []
    if args.only in (None, "clone"):
        plan += clone_scoring_rows(dec)
    if args.only in (None, "author"):
        manifest_path = R2_BOARD / "cells_manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())["cells"]
            board_path = R2_BOARD / "final_board_50m.json"
            board = json.loads(board_path.read_text()) if board_path.exists() else None
            plan += author_board_rows(dec, manifest, board)
        else:
            print(f"7a-ii: no r2 board manifest at {manifest_path.relative_to(REPO)} "
                  f"yet (step 4 has not run) -- nothing to author.")

    for run_id, row, status in plan:
        print(f"  {status:<10} {run_id or '-'}::{row['label']}"
              + (f"  -> {row['eval_path']}" if status == "add" else ""))
    n_add = sum(1 for _r, _row, s in plan if s == "add")
    print(f"{n_add} row(s) to add, {sum(1 for p in plan if p[2] == 'skip')} present, "
          f"{sum(1 for p in plan if p[2] == 'coincident')} coincident (skipped by design)")
    if not args.write:
        print("dry run -- pass --write to persist")
        return 0
    n = apply(dec, plan)
    existing = RUN_CONDITIONS.read_text()
    trailing = "\n" if existing.endswith("\n") else ""
    RUN_CONDITIONS.write_text(json.dumps(rc, indent=1, ensure_ascii=False) + trailing)
    print(f"wrote {n} row(s) -> {RUN_CONDITIONS.relative_to(REPO)}; "
          f"now run scripts/verify_run_conditions.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
