#!/usr/bin/env python3
"""Build the GS Era-2 verified board (card ``planning/gs-era2-verified-board-2026-09-08.md``).

PI ruling 2026-09-09: frame (a), the Era-2 carrier tiles clipped to the B
tiling's union (``inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson``,
``test_set_id`` ``era2-b-487``). This script is the board's deterministic
front end and back end; the statistics run in the project's canonical
register-driven chain (``scripts/era1_leaderboard_tiering.py``) and the MCB
tool (``scripts/selection_aware_intervals.py --board``), both keyed on the
analysis row this script mints.

Subcommands (run in this order)
-------------------------------
``membership``
    Derive the members from the register by the card's § 3 rule and write
    ``<board>/membership.json`` plus a human listing (the card's "dry-run
    listing"). Nothing else is written.
``jobs``
    Write ``<board>/score-commands.sh``: per member, (G2) the committed
    evaluation reproduced on its OWN frame with the committed recipe and a
    200-draw bootstrap into ``<board>/g2/<slug>/``, and (board) the same
    recipe with only the bounds swapped to the board frame into
    ``<board>/cells/<slug>/``. Bootstrap-heavy: run on sapphire.
``gates``
    After scoring: G2 (point F1 at 20 m reproduces the committed evaluation
    to 1e-6 and the feature count matches), G3 (every cell's evaluation
    names the board frame), G4 (cell count equals the membership), G6 (the
    per-cell committed-frame → board-frame delta table). Writes
    ``<board>/gates.json`` and ``<board>/frame-deltas.md``; exits non-zero
    on a failed gate.
``register``
    Mint one ``<label>-era2b`` condition row per member (a copy of the
    member's row whose ``eval_path`` is the board-frame evaluation and whose
    ``scope_override`` names ``era2-b-487``) and the analysis row
    ``gs-era2-verified-board-2026-09-10`` (unsigned — the PI signs) into
    ``results/run-conditions.json`` / ``results/run-analyses.json``.
    Idempotent. Then regenerate the manifests.
``finalise``
    After the tiering chain and the MCB tool have written into the board
    directory: fill the analysis row's ``outcome`` from ``tiering_20m.json``
    and the MCB admissible set, write ``<board>/provenance.json`` (frame,
    membership, gates G1-G6, instruments, commits) and ``<board>/README.md``
    (the board table with tiers, MCB membership, and the G6 frame delta per
    cell).

The membership rule (card § 3, restated under the frame rule of § 2)
-------------------------------------------------------------------
A registered condition joins when all of these hold:

* ``aggregation`` is ``verified``;
* its run is a 4-map-GS, 384 px, curator-reference run, or it is a
  B-geometry (``g384-ov192``) cell of the grid campaign;
* its proposer pool has K >= 5 passes (read from the label — ``kofN``,
  ``-nN``, ``kN`` — falling back to the row's ``n_passes``), which excludes
  the single-pass + verifier cells (``*baseline*`` and the whole
  ``proposer-verifier-384`` run);
* its committed evaluation is scored on the Era-2 frame or on grid-common
  (the B tiling's frame) — which excludes the Era-3 327-tile cells, the 256 px
  scope-override cells, and any row without a readable evaluation;
* grid / stride cells must be the B geometry (other geometries' tilings fall
  short of the frame; they stay on the grid and stride boards).

Every exclusion is listed with its reason in ``membership.json``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_CONDITIONS = REPO_ROOT / "results/run-conditions.json"
RUN_ANALYSES = REPO_ROOT / "results/run-analyses.json"
RUN_FACTS = REPO_ROOT / "results/run-facts.json"
FRAME = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
FRAME_ID = "era2-b-487"
FRAME_TILES = 487
BOARD_ID = "gs-era2-verified-board-2026-09-10"
BOARD_DIR = "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"
CARD = "planning/gs-era2-verified-board-2026-09-08.md"
SUFFIX = "-era2b"
ERA2_FRAME = "full_evaluation_bounds.geojson"
B_FRAME = "grid_common_bounds.geojson"
B_GEOMETRY = "g384-ov192"
GRID_RUNS = ("grid-2026-08-18", "stride-phaseb-2026-08-25", "stride-phasec-2026-08-25", "stride-55map-2026-08-25")
SINGLE_PASS_PV_RUN = "proposer-verifier-384"
G2_BOOTSTRAP = 200


def slug(condition_id: str) -> str:
    return condition_id.replace("::", "__").replace(".", "_")


def pool_k(label: str, n_passes: int | None) -> int | None:
    """Proposer pool size from the label, else the row's ``n_passes``."""
    m = re.search(r"\d+of(\d+)", label)
    if m:
        return int(m.group(1))
    m = re.search(r"-k(\d+)-verified", label)  # grid / 3.7 labels: g384-ov192-k10-verified…, g37-text-k5-verified…
    if m:
        return int(m.group(1))
    m = re.search(r"-n(\d+)(?:-|$)", label)  # verifier-robustness …-n5
    if m:
        return int(m.group(1))
    return int(n_passes) if n_passes else None


def _eval_meta(eval_path: str) -> dict[str, Any] | None:
    p = REPO_ROOT / eval_path
    if not eval_path or not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def f1_at(doc: dict[str, Any] | None, buffer_m: int = 20) -> float | None:
    if not doc:
        return None
    for b in doc.get("summary", {}).get("buffers", []):
        if b.get("buffer_metres") == buffer_m or b.get("buffer_m") == buffer_m:
            return float(b["f1"])
    return None


def derive_membership() -> dict[str, Any]:
    """Apply the § 3 rule to the register; return members and exclusions."""
    dec = json.loads(RUN_CONDITIONS.read_text(encoding="utf-8"))["decomposition"]
    facts = json.loads(RUN_FACTS.read_text(encoding="utf-8"))["facts"]
    members: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for run_id, entry in dec.items():
        f = facts.get(run_id) or {}
        gs_run = f.get("corpus") == "4-map-gs" and f.get("tile_size_px") == 384
        grid_run = run_id in GRID_RUNS
        if not (gs_run or grid_run):
            continue
        for cond in entry.get("conditions", []):
            if cond.get("aggregation") != "verified":
                continue
            cid = f"{run_id}::{cond['label']}"
            label = cond["label"]

            def out(reason: str) -> None:
                excluded.append({"condition_id": cid, "reason": reason})

            if run_id == SINGLE_PASS_PV_RUN or "baseline" in label:
                out("single-pass proposer + verifier (K = 1)")
                continue
            if grid_run and B_GEOMETRY not in label:
                out("grid/stride cell on a geometry other than B (its tiling falls short of the frame)")
                continue
            if grid_run and "55map" in label:
                out("55-map corpus cell")
                continue
            k = pool_k(label, cond.get("n_passes"))
            if k is None or k < 5:
                out(f"proposer pool K = {k} < 5")
                continue
            doc = _eval_meta(cond.get("eval_path") or "")
            if doc is None:
                out("no readable committed evaluation")
                continue
            cli = dict(doc.get("_metadata", {}).get("cli_args") or {})
            bounds = os.path.basename(cli.get("bounds") or "")
            if bounds not in (ERA2_FRAME, B_FRAME):
                out(f"committed evaluation on {bounds or 'an unknown frame'}, neither the Era-2 frame nor grid-common")
                continue
            if cond.get("scope_override"):
                out(f"scope override {cond['scope_override'].get('test_set_id')}")
                continue
            det = cond.get("detections") or ""
            if not (REPO_ROOT / det).exists():
                out("detections file missing on disk")
                continue
            members.append({
                "condition_id": cid, "run_id": run_id, "label": label, "k": k,
                "detections": det, "eval_path": cond["eval_path"],
                "committed_bounds": cli.get("bounds"), "committed_f1_20": f1_at(doc),
                "recipe": {kk: cli.get(kk) for kk in ("ground_truth", "buffers", "bootstrap", "seed")},
                "track": "image" if "image" in label else "text",
            })
    members.sort(key=lambda m: m["condition_id"])
    return {
        "board_id": BOARD_ID, "frame": FRAME, "frame_id": FRAME_ID, "card": CARD,
        "derived_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_members": len(members), "members": members, "excluded": excluded,
    }


def render_listing(membership: dict[str, Any]) -> str:
    lines = [f"{membership['n_members']} members ({membership['frame_id']}):"]
    for m in membership["members"]:
        lines.append(f"  {m['condition_id']:75s} K={m['k']:>2} F1@20={m['committed_f1_20']:.4f} on {os.path.basename(m['committed_bounds'])}")
    from collections import Counter
    reasons = Counter(e["reason"].split(" (")[0] for e in membership["excluded"])
    lines.append(f"{len(membership['excluded'])} excluded: " + "; ".join(f"{n} × {r}" for r, n in reasons.most_common()))
    return "\n".join(lines)


def _eval_command(m: dict[str, Any], bounds: str, out_dir: str, bootstrap: int, label: str) -> str:
    r = m["recipe"]
    parts = ["python", "scripts/evaluate_detections.py",
             "--detections", m["detections"],
             "--ground-truth", r["ground_truth"],
             "--bounds", bounds,
             "--buffers", *[str(b) for b in r["buffers"]],
             "--bootstrap", str(bootstrap),
             "--seed", str(r.get("seed") or 42),
             "--mcc",
             "--output-dir", out_dir,
             "--label", label]
    return " ".join(shlex.quote(p) for p in parts)


def write_jobs(board: Path, membership: dict[str, Any]) -> Path:
    lines = ["#!/usr/bin/env bash",
             f"# GS Era-2 verified board scoring jobs — {CARD}. GENERATED by scripts/build_gs_era2_board.py.",
             "# Run on sapphire from the repository root. Each job is independent; failures are collected.",
             "set -uo pipefail", "FAILED=()",
             'run() { echo "+ ${*:1:6} …"; if ! "$@"; then echo "FAILED: $1 $2 $3 $4" >&2; FAILED+=("$4"); fi; }', ""]
    for m in membership["members"]:
        s = slug(m["condition_id"])
        lines.append(f"# {m['condition_id']}")
        lines.append("run " + _eval_command(m, m["committed_bounds"], f"{BOARD_DIR}/g2/{s}", G2_BOOTSTRAP, f"{s}-g2"))
        lines.append("run " + _eval_command(m, FRAME, f"{BOARD_DIR}/cells/{s}", int(m["recipe"].get("bootstrap") or 10000), s))
        lines.append("")
    lines += ['if [ ${#FAILED[@]} -gt 0 ]; then echo "FAILED jobs: ${FAILED[*]}" >&2; exit 1; fi', 'echo "ALL DONE $(date -u +%FT%TZ)"']
    path = board / "score-commands.sh"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def run_gates(board: Path, membership: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """G2, G3, G4, G6 over the scored cells."""
    rows = []
    g2_fail = g3_fail = missing = 0
    for m in membership["members"]:
        s = slug(m["condition_id"])
        g2 = _eval_meta(f"{BOARD_DIR}/g2/{s}/evaluation.json")
        cell = _eval_meta(f"{BOARD_DIR}/cells/{s}/evaluation.json")
        committed = _eval_meta(m["eval_path"])
        if g2 is None or cell is None:
            missing += 1
            rows.append({"condition_id": m["condition_id"], "status": "missing"})
            continue
        g2_f1, com_f1, cell_f1 = f1_at(g2), f1_at(committed), f1_at(cell)
        n_geo = len(json.loads((REPO_ROOT / m["detections"]).read_text(encoding="utf-8")).get("features", []))
        n_g2 = g2.get("summary", {}).get("n_detections")
        n_com = (committed or {}).get("summary", {}).get("n_detections")
        g2_ok = g2_f1 is not None and com_f1 is not None and abs(g2_f1 - com_f1) < 1e-6 and (n_g2 == n_com)
        cell_bounds = os.path.basename((cell.get("_metadata", {}).get("cli_args") or {}).get("bounds") or "")
        g3_ok = cell_bounds == os.path.basename(FRAME)
        g2_fail += not g2_ok
        g3_fail += not g3_ok
        rows.append({"condition_id": m["condition_id"], "status": "ok" if (g2_ok and g3_ok) else "FAIL",
                     "committed_f1_20": com_f1, "g2_f1_20": g2_f1, "board_f1_20": cell_f1,
                     "delta_board_minus_committed": None if (cell_f1 is None or com_f1 is None) else round(cell_f1 - com_f1, 4),
                     "n_features": n_geo, "n_detections_committed": n_com, "n_detections_g2": n_g2,
                     "n_detections_board": cell.get("summary", {}).get("n_detections"),
                     "committed_bounds": os.path.basename(m["committed_bounds"]), "board_bounds": cell_bounds,
                     "g2_ok": g2_ok, "g3_ok": g3_ok})
    n_cells = sum(1 for r in rows if r["status"] != "missing")
    g4_ok = n_cells == membership["n_members"] and missing == 0
    report = {"board_id": BOARD_ID, "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "G2_reproduction_failures": g2_fail, "G3_frame_failures": g3_fail,
              "G4_cells": n_cells, "G4_members": membership["n_members"], "G4_ok": g4_ok,
              "missing": missing, "passed": g2_fail == 0 and g3_fail == 0 and g4_ok, "cells": rows}
    return report, report["passed"]


def render_deltas(report: dict[str, Any]) -> str:
    lines = [f"# G6 — committed-frame versus board-frame F1 at 20 m ({BOARD_ID})", "",
             f"> Generated {report['checked_at_utc']} by `scripts/build_gs_era2_board.py gates`. "
             f"G2: {report['G2_reproduction_failures']} reproduction failures; G3: {report['G3_frame_failures']} frame failures; "
             f"G4: {report['G4_cells']} cells of {report['G4_members']} members.", "",
             "| condition | committed frame | committed F1@20 | board F1@20 | Δ (board − committed) | n features | n det. committed | n det. board |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in sorted((r for r in report["cells"] if r["status"] != "missing"), key=lambda r: -(r["board_f1_20"] or 0)):
        lines.append(f"| `{r['condition_id']}` | {r['committed_bounds']} | {r['committed_f1_20']:.4f} | {r['board_f1_20']:.4f} | "
                     f"{r['delta_board_minus_committed']:+.4f} | {r['n_features']} | {r['n_detections_committed']} | {r['n_detections_board']} |")
    return "\n".join(lines) + "\n"


def register(membership: dict[str, Any], write: bool) -> list[str]:
    """Mint the -era2b rows and the analysis row; return the new condition ids."""
    rc = json.loads(RUN_CONDITIONS.read_text(encoding="utf-8"))
    ra = json.loads(RUN_ANALYSES.read_text(encoding="utf-8"))
    dec = rc["decomposition"]
    new_ids: list[str] = []
    added = 0
    for m in membership["members"]:
        run = dec[m["run_id"]]
        src = next(c for c in run["conditions"] if c["label"] == m["label"])
        new_label = m["label"] + SUFFIX
        new_ids.append(f"{m['run_id']}::{new_label}")
        if any(c["label"] == new_label for c in run["conditions"]):
            continue
        row = {k: v for k, v in src.items() if k not in ("eval_path", "_note", "input_vintage", "_pre_recovery_eval_path")}
        row["label"] = new_label
        row["eval_path"] = f"{BOARD_DIR}/cells/{slug(m['condition_id'])}/evaluation.json"
        row["scope_override"] = {"test_set_id": FRAME_ID, "bounds_path": FRAME, "n_test_tiles": FRAME_TILES,
                                 "calibration_set_id": None, "n_calibration_tiles": None}
        row["_note"] = (f"GS Era-2 verified board cell ({CARD}, PI frame ruling 2026-09-09): the "
                        f"registered cell {m['label']} re-scored with its committed recipe on the "
                        f"Era-2 ∩ B-union frame ({FRAME_ID}); the committed evaluation on "
                        f"{os.path.basename(m['committed_bounds'])} stays the row's record.")
        run["conditions"].append(row)
        added += 1
    # The G2 reproduction evaluations are gate artefacts, not conditions: waive
    # them in each run's _ignored_evals so the register verifier reads them as
    # disclosed rather than unclaimed.
    waived = 0
    for m in membership["members"]:
        run = dec[m["run_id"]]
        g2_path = f"{BOARD_DIR}/g2/{slug(m['condition_id'])}/evaluation.json"
        ignored = run.setdefault("_ignored_evals", [])
        if any((e.get("eval_path") if isinstance(e, dict) else e) == g2_path for e in ignored):
            continue
        ignored.append({"eval_path": g2_path,
                        "reason": (f"GS Era-2 board gate G2 ({CARD}): {m['label']}'s committed recipe re-run on "
                                   "its committed frame with a 200-draw bootstrap to prove the evaluator reproduces "
                                   "the committed evaluation; a gate artefact, not a condition.")})
        waived += 1
    rows = ra["analyses"] if isinstance(ra, dict) else ra
    if not any(r["analysis_id"] == BOARD_ID for r in rows):
        rows.append({
            "analysis_id": BOARD_ID, "type": "leaderboard",
            "_note": (f"The GS Era-2 verified board on one frame ({FRAME_ID}: the Era-2 carrier tiles clipped to the B "
                      f"tiling's union, 487 tiles, 435 reference mounds; {CARD}). Members: every registered verified "
                      "4-map-GS 384 px cell with K >= 5 dispatched on the Era-2 or B tiling — the Gemini 3 incumbents "
                      "of § R4/R5 and the Gemini 3.7, 3.8, image-B and grid-B cells — each re-scored on the frame as its "
                      f"'{SUFFIX}' row. Tiered by scripts/era1_leaderboard_tiering.py (round-robin tile-swap micro-F1 "
                      "permutation 10,000, seed 42, BH q = 0.05, greedy clique) at 20 m; Tier-1 membership reported as "
                      "the MCB admissible set (scripts/selection_aware_intervals.py --board). Gates G1-G6 in the board "
                      "directory's gates.json and frame-deltas.md."),
            "conditions_compared": list(new_ids), "hypothesis_refs": ["H2", "H1"],
            "outcome": "PENDING: tiering not yet run (filled by build_gs_era2_board finalise)",
            "paper_section": "Results", "output_path": f"{BOARD_DIR}/tiering_20m.json",
            "working_notes_obs": [], "preregistered": "post-hoc", "deviations": [],
            "_prereg_rationale": ("Post-hoc: the preregistration fixed the model family; this board extends § R4's GS "
                                  "instrument to the Gemini 3.7 / 3.8 cells on one frame. Split out of the r2 chain by PI "
                                  "ruling (S149); card signed 2026-09-09."),
            "_conditions_note": "all members are -era2b rows scored on the board frame; the committed rows remain the members' records",
        })
    if write:
        RUN_CONDITIONS.write_text(json.dumps(rc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        RUN_ANALYSES.write_text(json.dumps(ra, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{'wrote' if write else 'would write'} {added} new condition rows and {waived} G2 waivers; analysis row {BOARD_ID} "
          f"{'present' if not write else 'ensured'} with {len(new_ids)} conditions_compared")
    return new_ids


def _mcb_admissible(board: Path) -> tuple[list[str], str | None]:
    """The Hsu-constrained MCB admissible set from selection_aware_intervals --board.

    The tool writes ``hsu_not_ruled_out`` (and the two-sided ``mcb_not_ruled_out``)
    as indices into ``candidates``; E83 reports Tier-1 membership as the Hsu set.
    """
    for path in sorted((board / "mcb").glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        cands = doc.get("candidates") or []
        idx = doc.get("hsu_not_ruled_out")
        if isinstance(idx, list) and cands:
            return [str(cands[i]["ref"]) for i in idx if i < len(cands)], str(path.relative_to(REPO_ROOT))
    return [], None


def finalise(board: Path, membership: dict[str, Any]) -> None:
    tiering = json.loads((board / "tiering_20m.json").read_text(encoding="utf-8"))
    gates = json.loads((board / "gates.json").read_text(encoding="utf-8"))
    g1 = _eval_meta(f"{BOARD_DIR}/g1-regression.json") or {}
    deltas = {r["condition_id"]: r for r in gates["cells"]}
    # The symmetry fix's -opmax members (build_gs_era2_board_opmax.py) carry
    # their Era-2-frame reproduction as committed_f1_20 in opmax/gates.json.
    opmax_gates = _eval_meta(f"{BOARD_DIR}/opmax/gates.json") or {}
    for r in opmax_gates.get("cells", []):
        if r.get("on_board"):
            deltas[r["condition_id"]] = {**r, "committed_f1_20": r.get("g2_f1_20")}
    n_opmax = sum(1 for r in opmax_gates.get("cells", []) if r.get("on_board"))
    admissible, mcb_path = _mcb_admissible(board)
    ranking = tiering["ranking"]
    n_sig = sum(1 for r in tiering["pairwise"] if r["significant"])
    top = ranking[0]
    tiers = tiering["tiers"]
    outcome = (
        f"{n_sig}/{len(tiering['pairwise'])} pairs significant at BH q = 0.05, {len(tiers)} tiers on the "
        f"{FRAME_ID} frame ({tiering['n_tiles']} tiles, 435 reference mounds). Tier 1 (greedy clique) = "
        f"{len(tiers[0]['members'])} cell(s); MCB admissible set = {len(admissible) if admissible else 'not computed'}. "
        f"Top: {top['label']} F1@20 {top['eval_f1']:.4f}. "
        + "; ".join(f"{r['label']} {r['eval_f1']:.4f} (T{r['tier']})" for r in ranking[1:5])
        + ". Gates: G1 " + ("PASS" if g1.get("passed") else "see provenance") + f", G2 {gates['G2_reproduction_failures']} failures, "
        f"G3 {gates['G3_frame_failures']} failures, G4 {gates['G4_cells']}/{gates['G4_members']}; G6 max |delta| "
        f"{max(abs(r['delta_board_minus_committed']) for r in gates['cells'] if r.get('delta_board_minus_committed') is not None):.4f}."
    )
    ra = json.loads(RUN_ANALYSES.read_text(encoding="utf-8"))
    rows = ra["analyses"] if isinstance(ra, dict) else ra
    row = next(r for r in rows if r["analysis_id"] == BOARD_ID)
    row["outcome"] = outcome
    row["output_path"] = f"{BOARD_DIR}/tiering_20m.json"
    RUN_ANALYSES.write_text(json.dumps(ra, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    provenance = {
        "board_id": BOARD_ID, "card": CARD, "frame": FRAME, "frame_id": FRAME_ID,
        "frame_provenance": "inputs/vectors/bounds/384/era2_b_intersection_bounds.provenance.json",
        "membership": {"n": membership["n_members"] + n_opmax,
                       "rule": "card § 3 under the § 2 frame rule; see membership.json",
                       "n_era2b": membership["n_members"], "n_opmax": n_opmax,
                       "opmax": "the archived Era-2 PV board's sweep-optimal cells (opmax/membership.json)" if n_opmax else None},
        "gates_opmax": {k: v for k, v in opmax_gates.items() if k != "cells"} if opmax_gates else None,
        "instruments": {"per_cell_scoring": "scripts/evaluate_detections.py (each member's committed recipe, bounds swapped)",
                        "tiering": "scripts/era1_leaderboard_tiering.py (round-robin tile-swap micro-F1 permutation, BH q = 0.05, greedy clique, 20 m)",
                        "mcb": mcb_path or "scripts/selection_aware_intervals.py --board (not found in board/mcb)"},
        "gates": {"G1": g1, "G2_G3_G4_G6": {k: v for k, v in gates.items() if k != "cells"}},
        "tiering": {"n_pairs": len(tiering["pairwise"]), "n_significant": n_sig, "n_tiers": len(tiers),
                    "tie_set": tiers[0]["members"], "mcb_admissible_hsu": admissible,
                    "mcb_two_sided_band_n": (lambda d: len(d.get("mcb_not_ruled_out") or []))(
                        json.loads((REPO_ROOT / mcb_path).read_text(encoding="utf-8")) if mcb_path else {}),
                    "git_commit": tiering.get("git_commit"), "generated_at_utc": tiering.get("generated_at_utc")},
        "finalised_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (board / "provenance.json").write_text(json.dumps(provenance, indent=1) + "\n", encoding="utf-8")
    lines = [f"# The GS Era-2 verified board on one frame — `{BOARD_ID}`", "",
             f"> **Last revised**: {provenance['finalised_at_utc'][:10]} (original publication). Card: `{CARD}`. "
             f"Frame: `{FRAME}` (`{FRAME_ID}`; the Era-2 carrier tiles clipped to the B tiling's union, 487 tiles, "
             f"1,402.4 km², 435 curator reference mounds). Instrument: {provenance['instruments']['tiering']}; "
             f"Tier-1 membership is the MCB admissible set (E83). See [§ Changelog](#changelog).", "",
             f"{len(ranking)} cells; {n_sig}/{len(tiering['pairwise'])} pairs significant; {len(tiers)} tiers; "
             f"tie set {len(tiers[0]['members'])}; MCB admissible {len(admissible) if admissible else 'n/a'}.", "",
             "| rank | cell | tier | MCB | F1@20 (board frame) | committed F1@20 | Δ frame | tile-MCC |",
             "|---:|---|---:|:---:|---:|---:|---:|---:|"]
    for r in ranking:
        src = r["ref"].replace(SUFFIX, "")
        d = deltas.get(src) or deltas.get(r["ref"]) or {}
        lines.append(f"| {r['rank']} | `{src}` | {r['tier']} | {'●' if r['ref'] in admissible else ''} | {r['eval_f1']:.4f} | "
                     f"{d.get('committed_f1_20', float('nan')):.4f} | {d.get('delta_board_minus_committed', 0.0):+.4f} | "
                     f"{r['mcc'] if r['mcc'] is not None else '—'} |")
    lines += ["", "Δ frame = board-frame F1 minus the committed evaluation's F1 (gate G6; the committed frame is the Era-2 "
              "frame for the incumbents and grid-common for the B-geometry cells; for the `-opmax` rows it is the "
              "Era-2-frame reproduction of the archived board's score). Full pairwise table: `tiering_20m.json`; "
              "gates: `gates.json`, `opmax/gates.json`, `g1-regression.json`, `frame-deltas.md`; per-cell evaluations: "
              "`cells/`; reproduction evaluations: `g2/`, `opmax/g2/`.", ""]
    # Keep an existing changelog across rebuilds: the body is regenerated, the
    # revision trail is not (document revision policy, docs/agent-guidance.md).
    old_readme = (board / "README.md").read_text(encoding="utf-8") if (board / "README.md").exists() else ""
    marker = "## Changelog"
    if marker in old_readme:
        lines += [old_readme[old_readme.index(marker):].rstrip("\n")]
    else:
        lines += [marker, "", f"### {provenance['finalised_at_utc'][:10]} — Original publication", "",
                  "Built on sapphire per the card; all gates recorded in `provenance.json`."]
    (board / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(outcome)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["membership", "jobs", "gates", "register", "finalise"])
    parser.add_argument("--write", action="store_true", help="register: persist to the register files")
    args = parser.parse_args(argv)
    board = REPO_ROOT / BOARD_DIR
    board.mkdir(parents=True, exist_ok=True)
    mpath = board / "membership.json"

    if args.command == "membership":
        membership = derive_membership()
        mpath.write_text(json.dumps(membership, indent=1) + "\n", encoding="utf-8")
        (board / "membership.txt").write_text(render_listing(membership) + "\n", encoding="utf-8")
        print(render_listing(membership))
        return 0
    membership = json.loads(mpath.read_text(encoding="utf-8"))
    if args.command == "jobs":
        path = write_jobs(board, membership)
        print(f"wrote {path.relative_to(REPO_ROOT)} ({2 * membership['n_members']} jobs)")
        return 0
    if args.command == "gates":
        report, ok = run_gates(board, membership)
        (board / "gates.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        (board / "frame-deltas.md").write_text(render_deltas(report), encoding="utf-8")
        print(json.dumps({k: v for k, v in report.items() if k != "cells"}, indent=1))
        return 0 if ok else 2
    if args.command == "register":
        register(membership, args.write)
        return 0
    if args.command == "finalise":
        finalise(board, membership)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
