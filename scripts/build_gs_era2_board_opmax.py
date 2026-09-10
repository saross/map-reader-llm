#!/usr/bin/env python3
"""The GS Era-2 verified board's symmetry fix: register the archived board's sweep-optimal cells.

Why
---
The 3.7 / 3.8 cells on the GS Era-2 verified board
(``planning/gs-era2-verified-board-2026-09-08.md``) are the screens' sweep-best
operating points — in-sample optima of the E56 class — while the Gemini 3
incumbents are committed operating points (only the 16of30 opmax is a sweep
optimum). That asymmetry favours the newer family by the optimism of a sweep.
The PI's fix (2026-09-10): register the archived per-architecture Era-2 PV
board's sweep-optimal Gemini 3 cells (44 cells, retired instrument, archived
under ``archive/superseded-leaderboards/leaderboard/era2/pv-materialised/``)
as ``-opmax`` condition rows with an in-sample-optimum note, score them on the
board frame, and re-tier with both families at both levels.

What it does (subcommands, in order)
------------------------------------
``membership``
    Read the archived board (its tiers JSON, F1@20 and detection count per
    cell) and the two materialisation registries (``pv_registry.json`` — the
    30 ``pv-*`` cells, each with its source stage, K, and the sweep-best
    ``(vote_t, prob_t)``; ``session-78-matrix-registry.json`` — the 14
    verifier-variant cells). Exclude the one cell that IS a registered
    condition (``pv-flash-high-text-16of30`` == ``pv-diag-384::
    verified-adv-text-consensus-16of30``, 412 of 412 points identical; the
    other two (F1, n) coincidences share fewer than 60 points and are NOT
    twins). Apply the card's K >= 5 rule for board membership (the three
    K = 3 cells are registered but stay off the board). Write
    ``<board>/opmax/membership.json``.
``jobs``
    ``<board>/opmax/score-commands.sh``: per cell, the archived geojson scored
    on the Era-2 frame (``384/full_evaluation_bounds.geojson``, the frame the
    archived board used; 200-draw bootstrap; the G2-analogue reproduction of
    the archived F1) into ``<board>/opmax/g2/<slug>/``, and on the board frame
    (10,000-draw bootstrap, 14 buffers, MCC) into ``<board>/cells/<slug>/``.
    K < 5 cells get one full Era-2-frame evaluation only (their row's record).
``gates``
    G2-analogue: the Era-2-frame re-score reproduces the archived F1@20 to
    1e-6 and the archived detection count — except the one cell the G1 bisect
    explained (``pv-high-image-t0.3-n5``: archived 0.7460 from a 372-feature
    blob; the surviving 373-feature file scores 0.7475), whose expected value
    is the bisect's; G3 every board evaluation names the board frame; G4 the
    count; G6 the per-cell frame delta. Writes ``<board>/opmax/gates.json``.
``register --write``
    Mint one ``<label>-opmax`` row per cell into its parent run
    (``pv-diag-384``; ``n1-outstanding-384`` for the n1 cell), waive the
    G2-analogue evaluations, and extend the board analysis row's
    ``conditions_compared`` with the K >= 5 rows. Idempotent. Then run
    ``generate_post_run_report.py --all --write`` and
    ``verify_run_conditions.py`` by hand.

After ``register``: archive the 39-cell artefacts (done once, S152), re-tier
with ``scripts/era1_leaderboard_tiering.py --analysis-id <board>``, run the
MCB LAST (``scripts/selection_aware_intervals.py --board <board>``; PI rule
2026-09-10: the admissible set is a property of the candidate set, recomputed
after every membership change and only the final one cited), then
``scripts/build_gs_era2_board.py finalise``.

Usage::

    python scripts/build_gs_era2_board_opmax.py membership
    python scripts/build_gs_era2_board_opmax.py jobs        # then run on sapphire
    python scripts/build_gs_era2_board_opmax.py gates
    python scripts/build_gs_era2_board_opmax.py register [--write]
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from build_gs_era2_board import (  # noqa: E402
    BOARD_DIR,
    BOARD_ID,
    CARD,
    FRAME,
    FRAME_ID,
    FRAME_TILES,
    RUN_ANALYSES,
    RUN_CONDITIONS,
    _eval_meta,
    f1_at,
    slug,
)

ARCHIVE = "archive/superseded-leaderboards/leaderboard"
ARCHIVED_BOARD = f"{ARCHIVE}/per-architecture/era2/pv/leaderboard_tiers_20m.json"
MATERIALISED = f"{ARCHIVE}/era2/pv-materialised"
PV_REGISTRY = f"{MATERIALISED}/pv_registry.json"
S78_REGISTRY = f"{MATERIALISED}/session-78-matrix-registry.json"
ARCHIVED_COMMIT = "005e6c71"
ERA2_FRAME = "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
GROUND_TRUTH = "inputs/vectors/references/mounds-reference.geojson"
BUFFERS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]
BOARD_BOOTSTRAP = 10000
G2_BOOTSTRAP = 200
SEED = 42
SUFFIX = "-opmax"
MIN_K = 5
OPMAX_DIR = f"{BOARD_DIR}/opmax"
# The one archived cell that is a registered condition (coordinate-identical).
TWINS = {"pv-flash-high-text-16of30": "pv-diag-384::verified-adv-text-consensus-16of30"}
# The one cell whose archived F1 came from a stale cache (G1 bisect, 2026-09-10).
BISECTED = {"pv-high-image-t0.3-n5": {"archived_f1_20": 0.746, "expected_f1_20": 0.7475,
                                      "archived_n": 372, "expected_n": 373,
                                      "why": "g1-regression.json bisect: archived cache from blob 456dd9bf (372), "
                                             "file re-materialised to 373 features at d6cdb648b"}}
V1_CONFIG = {"variant": "v1", "instruction_file": "verify_adversarial.md", "model": "gemini-3-flash-preview",
             "thinking_level": "minimal", "temperature": 0.0, "iterations": 1}
S78_VARIANT_FILES = {"adversarial": "verify_adversarial.md", "adversarial-text": "verify_adversarial-text.md",
                     "brief": "verify_brief.md", "brief-text": "verify_brief-text.md",
                     "checklist": "verify_checklist.md", "checklist-text": "verify_checklist-text.md",
                     "comparative": "verify_comparative.md"}
S78_POOLS = {"text": ("flash-high-text-n5-text-t0.7", "flash-high-text-n5-text-t0.7-session-78-matrix-verified-"),
             "image": ("flash-high-image-n5-image-t0.7", "flash-high-image-n5-image-t0.7-session-78-matrix-verified-")}


def _load(rel: str) -> Any:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def archived_cells() -> dict[str, dict[str, Any]]:
    """The archived board's cells: F1@20, detection count, tier."""
    doc = _load(ARCHIVED_BOARD)
    out: dict[str, dict[str, Any]] = {}
    for tier in doc["tiers"]:
        for c in tier["conditions"]:
            e = c["evaluations"]["20"]
            n = e.get("n_detections")
            if n is None:
                cache = (REPO_ROOT / ARCHIVE / "per-architecture/era2/pv/.cache/evaluations"
                         / c["label"].replace(".", "-") / "t1_20m.json")
                n = json.loads(cache.read_text(encoding="utf-8"))["n_detections"]
            out[c["label"]] = {"archived_f1_20": float(e["f1"]), "archived_n": int(n), "archived_tier": tier["tier"],
                               "track": c["track"], "k_yaml": c.get("k")}
    return out


def _pv_stage(entry: dict[str, Any]) -> tuple[str, str, str]:
    """(run_id, pool_id, stage_id) for a ``pv_registry`` entry from its probabilities path."""
    p = Path(entry["probabilities_path"])          # outputs/h11/<run>/<pool…>/<stage>/probabilities.json
    parts = p.parts
    run_id = parts[2]
    rel = parts[3:-1]                               # pool dirs + stage dir
    stage_id = "-".join(rel)
    pool_id = "-".join(rel[:-1])
    return run_id, pool_id, stage_id


def derive_membership() -> dict[str, Any]:
    cells = archived_cells()
    pv = {e["id"]: e for e in _load(PV_REGISTRY)}
    s78 = _load(S78_REGISTRY)["cells"]
    members: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    registry_of: dict[str, dict[str, Any]] = {}
    for label, arch in cells.items():
        if label in TWINS:
            excluded.append({"label": label, "reason": f"registered twin: {TWINS[label]} (coordinate-identical)"})
            continue
        if label in pv:
            e = pv[label]
            run_id, pool_id, stage_id = _pv_stage(e)
            best = e["best_at_20m"]
            k = int(e["K"])
            row = {"label": label, "run_id": run_id, "proposer_pool": pool_id, "stage_id": stage_id, "k": k,
                   "vote_threshold": int(best["vote_t"]), "prob_threshold": float(best["prob_t"]),
                   "registry_f1_20": float(best["f1"]), "registry_n": int(best["n"]),
                   "verifier_config": dict(V1_CONFIG), "modality": e["track"],
                   "sweep_path": e.get("sweep_path"), "probabilities_path": e["probabilities_path"],
                   "source": "pv_registry.json"}
        else:
            s = next((c for c in s78 if Path(c["output_geojson"]).stem == label), None)
            if s is None:
                excluded.append({"label": label, "reason": "no registry entry"})
                continue
            pool_id, stage_prefix = S78_POOLS[s["pool"]]
            row = {"label": label, "run_id": "pv-diag-384", "proposer_pool": pool_id,
                   "stage_id": stage_prefix + s["variant"], "k": 5,
                   "vote_threshold": int(s["vote_t"]), "prob_threshold": float(s["prob_t"]),
                   "registry_f1_20": None, "registry_n": int(s["candidates_kept"]),
                   "verifier_config": {"variant": f"session-78-{s['variant']}",
                                       "instruction_file": S78_VARIANT_FILES[s["variant"]],
                                       "model": "gemini-3-flash-preview", "thinking_level": "minimal",
                                       "temperature": 0.0, "iterations": 1},
                   "modality": s["pool"], "sweep_path": None,
                   "probabilities_path": f"outputs/h11/pv-diag-384/{pool_id.replace('-n5-', '-n5/')}/session-78-matrix/verified-{s['variant']}/probabilities.json",
                   "n_candidates": int(s["candidates_input_total"]), "source": "session-78-matrix-registry.json"}
        row.update(arch)
        row["detections"] = f"{MATERIALISED}/{label}.geojson"
        row["condition_id"] = f"{row['run_id']}::{label}{SUFFIX}"
        row["on_board"] = row["k"] >= MIN_K
        if not row["on_board"]:
            row["off_board_reason"] = f"K = {row['k']} < {MIN_K} (card § 3 rule); registered, not a member"
        registry_of[label] = row
        members.append(row)
    on = [m for m in members if m["on_board"]]
    return {"board_id": BOARD_ID, "card": CARD, "frame": FRAME, "frame_id": FRAME_ID,
            "archived_board": ARCHIVED_BOARD, "archived_git_commit": ARCHIVED_COMMIT,
            "derived_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "n_archived": len(cells), "n_rows": len(members), "n_members": len(on),
            "rule": (f"every archived cell that is not a registered condition gets a {SUFFIX} row; "
                     f"rows with K >= {MIN_K} join the board (card § 3)"),
            "members": members, "excluded": excluded}


def _cmd(detections: str, bounds: str, out_dir: str, bootstrap: int, label: str) -> str:
    parts = ["python", "scripts/evaluate_detections.py", "--detections", detections,
             "--ground-truth", GROUND_TRUTH, "--bounds", bounds,
             "--buffers", *[str(b) for b in BUFFERS], "--bootstrap", str(bootstrap), "--seed", str(SEED),
             "--mcc", "--output-dir", out_dir, "--label", label]
    return " ".join(shlex.quote(p) for p in parts)


def write_jobs(membership: dict[str, Any]) -> Path:
    lines = ["#!/usr/bin/env bash",
             f"# GS Era-2 board symmetry fix — {SUFFIX} rows scoring jobs. GENERATED by scripts/build_gs_era2_board_opmax.py.",
             "# Run on sapphire from the repository root. Each job is independent; failures are collected.",
             "set -uo pipefail", "FAILED=()",
             'run() { echo "+ ${*:1:6} …"; if ! "$@"; then echo "FAILED: $1 $2 $3 $4" >&2; FAILED+=("$4"); fi; }', ""]
    n = 0
    for m in membership["members"]:
        s = slug(m["condition_id"])
        lines.append(f"# {m['condition_id']}")
        if m["on_board"]:
            lines.append("run " + _cmd(m["detections"], ERA2_FRAME, f"{OPMAX_DIR}/g2/{s}", G2_BOOTSTRAP, f"{s}-g2"))
            lines.append("run " + _cmd(m["detections"], FRAME, f"{BOARD_DIR}/cells/{s}", BOARD_BOOTSTRAP, s))
            n += 2
        else:
            lines.append("run " + _cmd(m["detections"], ERA2_FRAME, f"{OPMAX_DIR}/era2/{s}", BOARD_BOOTSTRAP, s))
            n += 1
        lines.append("")
    lines += ['if [ ${#FAILED[@]} -gt 0 ]; then echo "FAILED jobs: ${FAILED[*]}" >&2; exit 1; fi',
              'echo "ALL DONE $(date -u +%FT%TZ)"']
    path = REPO_ROOT / OPMAX_DIR / "score-commands.sh"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)
    print(f"wrote {path.relative_to(REPO_ROOT)} ({n} jobs)")
    return path


def run_gates(membership: dict[str, Any]) -> dict[str, Any]:
    rows = []
    g2_fail = g3_fail = missing = 0
    for m in membership["members"]:
        s = slug(m["condition_id"])
        n_geo = len(_load(m["detections"]).get("features", []))
        if not m["on_board"]:
            ev = _eval_meta(f"{OPMAX_DIR}/era2/{s}/evaluation.json")
            if ev is None:
                missing += 1
                rows.append({"condition_id": m["condition_id"], "status": "missing"})
                continue
            f1, n_ev = f1_at(ev), ev.get("summary", {}).get("n_detections")
            ok = abs(f1 - m["archived_f1_20"]) < 1e-6 and n_ev == m["archived_n"] == n_geo
            g2_fail += not ok
            rows.append({"condition_id": m["condition_id"], "status": "ok" if ok else "FAIL", "on_board": False,
                         "archived_f1_20": m["archived_f1_20"], "era2_f1_20": f1, "n_features": n_geo,
                         "n_detections_archived": m["archived_n"], "n_detections_era2": n_ev, "g2_ok": ok})
            continue
        g2 = _eval_meta(f"{OPMAX_DIR}/g2/{s}/evaluation.json")
        cell = _eval_meta(f"{BOARD_DIR}/cells/{s}/evaluation.json")
        if g2 is None or cell is None:
            missing += 1
            rows.append({"condition_id": m["condition_id"], "status": "missing"})
            continue
        exp_f1, exp_n = m["archived_f1_20"], m["archived_n"]
        note = None
        if m["label"] in BISECTED:
            b = BISECTED[m["label"]]
            exp_f1, exp_n, note = b["expected_f1_20"], b["expected_n"], b["why"]
        g2_f1, cell_f1 = f1_at(g2), f1_at(cell)
        n_g2, n_cell = g2.get("summary", {}).get("n_detections"), cell.get("summary", {}).get("n_detections")
        g2_ok = g2_f1 is not None and abs(g2_f1 - exp_f1) < 1e-6 and n_g2 == exp_n == n_geo
        cell_bounds = Path((cell.get("_metadata", {}).get("cli_args") or {}).get("bounds") or "").name
        g3_ok = cell_bounds == Path(FRAME).name
        g2_fail += not g2_ok
        g3_fail += not g3_ok
        rows.append({"condition_id": m["condition_id"], "status": "ok" if (g2_ok and g3_ok) else "FAIL", "on_board": True,
                     "archived_f1_20": m["archived_f1_20"], "expected_f1_20": exp_f1, "g2_f1_20": g2_f1,
                     "board_f1_20": cell_f1,
                     "delta_board_minus_committed": None if (cell_f1 is None or g2_f1 is None) else round(cell_f1 - g2_f1, 4),
                     "n_features": n_geo, "n_detections_archived": m["archived_n"], "n_detections_expected": exp_n,
                     "n_detections_g2": n_g2, "n_detections_board": n_cell,
                     "board_bounds": cell_bounds, "g2_ok": g2_ok, "g3_ok": g3_ok, "note": note})
    n_cells = sum(1 for r in rows if r["status"] != "missing" and r.get("on_board"))
    g4_ok = n_cells == membership["n_members"] and missing == 0
    return {"board_id": BOARD_ID, "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "G2_reproduction_failures": g2_fail, "G3_frame_failures": g3_fail,
            "G4_cells": n_cells, "G4_members": membership["n_members"], "G4_ok": g4_ok, "missing": missing,
            "passed": g2_fail == 0 and g3_fail == 0 and g4_ok, "bisected": BISECTED, "cells": rows}


def register(membership: dict[str, Any], write: bool) -> list[str]:
    rc = _load(RUN_CONDITIONS.relative_to(REPO_ROOT).as_posix())
    ra = _load(RUN_ANALYSES.relative_to(REPO_ROOT).as_posix())
    dec = rc["decomposition"]
    added = waived = 0
    board_ids: list[str] = []
    for m in membership["members"]:
        run = dec[m["run_id"]]
        new_label = m["label"] + SUFFIX
        s = slug(m["condition_id"])
        if m["on_board"]:
            board_ids.append(m["condition_id"])
        # The row's verifier stage must be a registered stage of its run; the n1
        # image-t0 verified-v1-n3 stage never was (that run has no stages).
        stages = run.setdefault("verifier_passes", {})
        if m["stage_id"] not in stages:
            stages[m["stage_id"]] = {"modality": m["modality"],
                                     "path": "/".join(Path(m["probabilities_path"]).parts[3:-1])}
        if any(c["label"] == new_label for c in run["conditions"]):
            continue
        note = (f"IN-SAMPLE OPTIMUM (E56 class): the archived per-architecture Era-2 PV board's sweep-optimal cell "
                f"{m['label']} (archived at {ARCHIVED_COMMIT}, retired instrument build_tiered_leaderboard.py; "
                f"{ARCHIVED_BOARD}; materialised from stage {m['stage_id']} at the F1@20-argmax (vote_t {m['vote_threshold']}, "
                f"prob_t {m['prob_threshold']}) of its sweep on the evaluation set). Registered 2026-09-10 for the GS Era-2 "
                f"board's symmetry fix ({CARD}, changelog 2026-09-10 later): the Gemini 3 family at its sweep-optimal level, "
                f"beside the 3.7 / 3.8 screen cells which are sweep-best points too. ")
        if m["on_board"]:
            note += (f"The row's evaluation is the board-frame score ({FRAME_ID}); its Era-2-frame reproduction of the "
                     f"archived F1 ({m['archived_f1_20']}) is the waived opmax/g2 evaluation.")
            eval_path = f"{BOARD_DIR}/cells/{s}/evaluation.json"
        else:
            note += m["off_board_reason"] + "; the row's evaluation is the Era-2-frame score."
            eval_path = f"{OPMAX_DIR}/era2/{s}/evaluation.json"
        if m["label"] in BISECTED:
            note += f" NOTE: {BISECTED[m['label']]['why']}; the archived 0.7460 is not this file's score (G1 bisect)."
        row: dict[str, Any] = {
            "label": new_label, "architecture": "proposer-verifier", "aggregation": "verified",
            "proposer_pool": m["proposer_pool"], "n_passes": m["k"],
            "vote_threshold": m["vote_threshold"], "prob_threshold": m["prob_threshold"],
            "verifier_config": m["verifier_config"], "eval_path": eval_path, "detections": m["detections"],
            "_note": note,
        }
        if m.get("n_candidates"):
            row["n_candidates"] = m["n_candidates"]
        if m["on_board"]:
            row["scope_override"] = {"test_set_id": FRAME_ID, "bounds_path": FRAME, "n_test_tiles": FRAME_TILES,
                                     "calibration_set_id": None, "n_calibration_tiles": None}
        run["conditions"].append(row)
        added += 1
    for m in membership["members"]:
        if not m["on_board"]:
            continue
        run = dec[m["run_id"]]
        g2_path = f"{OPMAX_DIR}/g2/{slug(m['condition_id'])}/evaluation.json"
        ignored = run.setdefault("_ignored_evals", [])
        if any((e.get("eval_path") if isinstance(e, dict) else e) == g2_path for e in ignored):
            continue
        ignored.append({"eval_path": g2_path,
                        "reason": (f"GS Era-2 board symmetry fix ({CARD}): {m['label']}{SUFFIX}'s archived geojson re-scored on "
                                   "the Era-2 frame with a 200-draw bootstrap to prove the archived F1 reproduces; a gate "
                                   "artefact, not a condition.")})
        waived += 1
    rows = ra["analyses"] if isinstance(ra, dict) else ra
    arow = next(r for r in rows if r["analysis_id"] == BOARD_ID)
    before = len(arow["conditions_compared"])
    for cid in board_ids:
        if cid not in arow["conditions_compared"]:
            arow["conditions_compared"].append(cid)
    arow["_conditions_note"] = (
        f"{before} '-era2b' rows (the registered cells re-scored on the board frame; the committed rows remain the "
        f"members' records) plus {len(board_ids)} '{SUFFIX}' rows (the archived Era-2 PV board's sweep-optimal Gemini 3 "
        f"cells, in-sample optima of the E56 class, registered 2026-09-10 for the symmetry fix; three K = 3 archived "
        f"cells are registered but off-board by the K >= {MIN_K} rule). Both families at both levels: committed "
        "operating points and sweep optima.")
    arow["outcome"] = "PENDING: re-tier after the symmetry fix (filled by build_gs_era2_board finalise)"
    if write:
        RUN_CONDITIONS.write_text(json.dumps(rc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        RUN_ANALYSES.write_text(json.dumps(ra, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{'wrote' if write else 'would write'} {added} new {SUFFIX} rows and {waived} g2 waivers; analysis row "
          f"{BOARD_ID} conditions_compared {before} -> {len(arow['conditions_compared'])}")
    return board_ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["membership", "jobs", "gates", "register"])
    parser.add_argument("--write", action="store_true", help="register: persist to the register files")
    args = parser.parse_args(argv)
    opmax = REPO_ROOT / OPMAX_DIR
    opmax.mkdir(parents=True, exist_ok=True)
    mpath = opmax / "membership.json"
    if args.command == "membership":
        membership = derive_membership()
        mpath.write_text(json.dumps(membership, indent=1) + "\n", encoding="utf-8")
        on = [m for m in membership["members"] if m["on_board"]]
        print(f"{membership['n_archived']} archived cells; {len(membership['excluded'])} excluded "
              f"({'; '.join(e['reason'] for e in membership['excluded'])}); {membership['n_rows']} {SUFFIX} rows; "
              f"{len(on)} board members (K >= {MIN_K}); off-board: "
              f"{[m['label'] for m in membership['members'] if not m['on_board']]}")
        return 0
    membership = json.loads(mpath.read_text(encoding="utf-8"))
    if args.command == "jobs":
        write_jobs(membership)
        return 0
    if args.command == "gates":
        report = run_gates(membership)
        (opmax / "gates.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        print(f"G2 {report['G2_reproduction_failures']} failures, G3 {report['G3_frame_failures']}, "
              f"G4 {report['G4_cells']}/{report['G4_members']}, missing {report['missing']} -> "
              f"{'PASS' if report['passed'] else 'FAIL'}")
        for r in report["cells"]:
            if r["status"] != "ok":
                print("  ", r)
        return 0 if report["passed"] else 1
    register(membership, args.write)
    return 0


if __name__ == "__main__":
    sys.exit(main())
