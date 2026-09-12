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
    **Re-materialisation (2026-09-10)**: nine cells' 2026-04-19 detection
    files did NOT hold the point the registry registered
    (``registry_vs_archived`` = ``differs …``). They were rebuilt from their
    registered stage by ``scripts/materialise_opmax_cells.py`` into
    ``<board>/opmax/materialised/``; where a rebuilt file exists, the member's
    ``detections`` points at it, ``registry_vs_archived`` becomes
    ``resolved …``, the superseded path is kept as ``archived_detections``,
    and ``archived_n`` / ``archived_f1_20`` stay as history. A resolved row's
    EXPECTED score in ``gates`` is then the REGISTRY's F1 and count, not the
    archived board's.
``jobs [--only-resolved]``
    ``<board>/opmax/score-commands.sh``: per cell, the archived geojson scored
    on the Era-2 frame (``384/full_evaluation_bounds.geojson``, the frame the
    archived board used; 200-draw bootstrap; the G2-analogue reproduction of
    the archived F1) into ``<board>/opmax/g2/<slug>/``, and on the board frame
    (10,000-draw bootstrap, 14 buffers, MCC) into ``<board>/cells/<slug>/``.
    K < 5 cells get one full Era-2-frame evaluation only (their row's record).
    ``--only-resolved`` restricts the sweep to the re-materialised rows and
    additionally writes ``rescore-jobs.txt``, one command per line, for
    ``xargs -P`` on sapphire.
``gates``
    G2-analogue: the Era-2-frame re-score reproduces the archived F1@20 to
    1e-6 and the archived detection count — except the one cell the G1 bisect
    explained (``pv-high-image-t0.3-n5``: archived 0.7460 from a 372-feature
    blob; the surviving 373-feature file scores 0.7475), whose expected value
    is the bisect's; G3 every board evaluation names the board frame; G4 the
    count; G6 the per-cell frame delta. Writes ``<board>/opmax/gates.json``.
``notes [--write]``
    Narrow amendment path (2026-09-11): append the vintage sentence to any
    registered ``-opmax`` row whose membership entry carries
    ``vintage.verdict`` = ``union-rebuilt`` — the union at its
    ``consensus_path`` was re-materialised after its verifier ran, so the
    index join that defines the cell cannot be re-run against today's file.
    Touches ``_note`` and nothing else: no new rows, no waivers, and no write
    to the board's analysis row, which is signed. Idempotent.
``register --write``
    Idempotently repoint any already-registered row whose member is now
    ``resolved`` at its re-materialised file, dropping the superseded
    "registry differs" sentence from ``_note`` and recording the replacement
    (counts before -> after). Otherwise, mint one ``<label>-opmax`` row per cell into its parent run
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
    python scripts/build_gs_era2_board_opmax.py register [--write] [--no-analysis-row]
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
from materialise_opmax_cells import (  # noqa: E402
    classify_vintage,
    sweep_universe,
)
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
#: Smallest proposer pool the board admits. 1 since 2026-09-12 (PI ruling
#: R3 of the K-ladder review): every verified cell on the frame joins,
#: whatever its pass count, so the three K = 3 sweep optima that were
#: registered off-board now join it.
MIN_K = 1
OPMAX_DIR = f"{BOARD_DIR}/opmax"
# Cells re-materialised from their registered stage because the 2026-04-19
# materialisation did not hold the registered point (scripts/materialise_opmax_cells.py).
RESOLVED_DIR = f"{OPMAX_DIR}/materialised"
RESOLVED_ON = "2026-09-10"
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
    """The archived board's cells: F1@20, detection count, tier.

    ``archived_n`` is the FEATURE COUNT OF THE FILE THE ROW NAMES, counted here,
    not a number read from the archived label-keyed evaluation cache.

    The cache was the previous source (via a fallback, because the archived board
    JSON records no ``n_detections`` for any of its 44 cells), and
    ``reports/name-keyed-cache-audit-2026-09-12.md`` Finding 2 showed why that is
    wrong: the cache is keyed by label with no content key, so for
    ``pv-high-image-t0.3-n5`` it still serves the 372 features the file held at
    ``bd24293d4`` although the file was re-materialised to 373 at ``d6cdb648b``.
    Because the registry's count for that cell is also 372, the stale value
    *agreed* with it and suppressed the ``differs`` verdict — and
    ``registry_vs_archived`` is what decides whether the row is re-pointed at a
    re-materialised file (``derive_membership``). A count taken from the file
    cannot go stale that way. The cache's value is still recorded, as
    ``archived_cache_n``, so the discrepancy is visible rather than erased.

    Returns:
        Per archived label: the archived F1@20, the counted ``archived_n``, the
        cache's value and whether the two agree, the archived tier, the track,
        and the YAML ``k``.

    Raises:
        FileNotFoundError: If a cell's materialised detection file is absent —
            a count cannot be inferred, and inferring one is the defect this
            change removes.
    """
    doc = _load(ARCHIVED_BOARD)
    out: dict[str, dict[str, Any]] = {}
    for tier in doc["tiers"]:
        for c in tier["conditions"]:
            e = c["evaluations"]["20"]
            detections = REPO_ROOT / MATERIALISED / f"{c['label']}.geojson"
            if not detections.is_file():
                raise FileNotFoundError(
                    f"{c['label']}: no materialised detection file at "
                    f"{detections.relative_to(REPO_ROOT)}; archived_n must be "
                    "counted from the file the row names, never inferred")
            n = len(json.loads(detections.read_text(encoding="utf-8")).get("features") or [])
            cache_n = e.get("n_detections")
            if cache_n is None:
                cache = (REPO_ROOT / ARCHIVE / "per-architecture/era2/pv/.cache/evaluations"
                         / c["label"].replace(".", "-") / "t1_20m.json")
                if cache.is_file():
                    cache_n = json.loads(cache.read_text(encoding="utf-8")).get("n_detections")
            out[c["label"]] = {"archived_f1_20": float(e["f1"]), "archived_n": int(n),
                               "archived_n_basis": f"counted from {MATERIALISED}/{c['label']}.geojson",
                               "archived_cache_n": None if cache_n is None else int(cache_n),
                               "archived_cache_agrees": None if cache_n is None else int(cache_n) == int(n),
                               "archived_tier": tier["tier"],
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
        # The registries' sweep best point (sweep_2d.json) versus the file the
        # archived board scored: nine pv cells differ (the S151 sweep-staleness
        # class inside the archived board's own registry). The row IS the file.
        reg_f1, reg_n = row.get("registry_f1_20"), row.get("registry_n")
        row["registry_vs_archived"] = (
            "n/a" if reg_f1 is None else
            "match" if abs(reg_f1 - arch["archived_f1_20"]) < 5e-5 and reg_n == arch["archived_n"] else
            f"differs: registry F1 {reg_f1} n {reg_n} vs archived board F1 {arch['archived_f1_20']} n {arch['archived_n']}")
        row["detections"] = f"{MATERIALISED}/{label}.geojson"
        # Resolution (2026-09-10): where the archived file did NOT hold the
        # registered point, the cell was rebuilt from its stage at that point
        # (scripts/materialise_opmax_cells.py; Gate A: the rebuilt count equals
        # the registry's). The row then IS the registered point, and its
        # expected score becomes the REGISTRY's, not the archived board's.
        # ``archived_n`` / ``archived_f1_20`` stay as history.
        rebuilt = f"{RESOLVED_DIR}/{label}.geojson"
        if row["registry_vs_archived"].startswith("differs") and (REPO_ROOT / rebuilt).is_file():
            row["archived_detections"] = row["detections"]
            row["detections"] = rebuilt
            row["resolved_at"] = RESOLVED_ON
            row["registry_vs_archived"] = (
                f"resolved {RESOLVED_ON}: the 2026-04-19 materialisation (bd24293d4) held F1 "
                f"{arch['archived_f1_20']} n {arch['archived_n']}, not the registered point; re-materialised "
                f"from stage {row['stage_id']} at (vote_t {row['vote_threshold']}, prob_t "
                f"{row['prob_threshold']}) to n {reg_n}, the registry's count, expected F1@20 {reg_f1} "
                f"(scripts/materialise_opmax_cells.py; superseded file kept at archived_detections)")
        # Vintage guard (2026-09-11): record whether the union at this cell's
        # consensus_path is still the set its verifier cropped. A rebuilt union
        # makes the index join — and so any count derived from it today —
        # meaningless, and the row must be read on its own vintage.
        if label in pv and "consensus_path" in pv[label]:
            e = pv[label]
            n_union = len(_load(e["consensus_path"]).get("features", []))
            n_prob = len(_load(e["probabilities_path"]).get("results", {}))
            verdict, why = classify_vintage(n_union, n_prob,
                                            sweep_universe(e.get("sweep_path")))
            row["vintage"] = {"verdict": verdict, "why": why, "n_union": n_union,
                              "n_probabilities": n_prob,
                              "n_sweep": sweep_universe(e.get("sweep_path")),
                              "union": e["consensus_path"],
                              "probabilities": e["probabilities_path"],
                              "sweep": e.get("sweep_path")}
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


def write_jobs(membership: dict[str, Any], only_resolved: bool = False) -> Path:
    """Write the scoring jobs for the ``-opmax`` rows.

    Args:
        membership: The parsed ``opmax/membership.json``.
        only_resolved: Emit jobs for the re-materialised rows only, into
            ``opmax/rescore-commands.sh`` plus a one-command-per-line
            ``opmax/rescore-jobs.txt`` for ``xargs -P``. The full sweep goes
            to ``opmax/score-commands.sh`` as before.

    Returns:
        Path of the shell script written.
    """
    members = [m for m in membership["members"] if m.get("resolved_at")] if only_resolved \
        else membership["members"]
    what = "re-materialised rows only" if only_resolved else "all rows"
    lines = ["#!/usr/bin/env bash",
             f"# GS Era-2 board symmetry fix — {SUFFIX} rows scoring jobs ({what}). "
             "GENERATED by scripts/build_gs_era2_board_opmax.py.",
             "# Run on sapphire from the repository root. Each job is independent; failures are collected.",
             "set -uo pipefail", "FAILED=()",
             'run() { echo "+ ${*:1:6} …"; if ! "$@"; then echo "FAILED: $1 $2 $3 $4" >&2; FAILED+=("$4"); fi; }', ""]
    bare: list[str] = []
    n = 0
    for m in members:
        s = slug(m["condition_id"])
        lines.append(f"# {m['condition_id']}")
        if m["on_board"]:
            jobs = [_cmd(m["detections"], ERA2_FRAME, f"{OPMAX_DIR}/g2/{s}", G2_BOOTSTRAP, f"{s}-g2"),
                    _cmd(m["detections"], FRAME, f"{BOARD_DIR}/cells/{s}", BOARD_BOOTSTRAP, s)]
        else:
            jobs = [_cmd(m["detections"], ERA2_FRAME, f"{OPMAX_DIR}/era2/{s}", BOARD_BOOTSTRAP, s)]
        lines += ["run " + j for j in jobs]
        bare += jobs
        n += len(jobs)
        lines.append("")
    lines += ['if [ ${#FAILED[@]} -gt 0 ]; then echo "FAILED jobs: ${FAILED[*]}" >&2; exit 1; fi',
              'echo "ALL DONE $(date -u +%FT%TZ)"']
    name = "rescore-commands.sh" if only_resolved else "score-commands.sh"
    path = REPO_ROOT / OPMAX_DIR / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)
    print(f"wrote {path.relative_to(REPO_ROOT)} ({n} jobs, {len(members)} rows)")
    if only_resolved:
        # One command per line, for `xargs -P4 -I{} bash -c '{}'` on sapphire.
        bare_path = REPO_ROOT / OPMAX_DIR / "rescore-jobs.txt"
        bare_path.write_text("\n".join(bare) + "\n", encoding="utf-8")
        print(f"wrote {bare_path.relative_to(REPO_ROOT)}")
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
        # A resolved row is the REGISTERED point, so the G2-analogue reproduces
        # the materialisation registry's F1 and count, not the archived board's
        # (which came from a file that never held that point).
        if m.get("resolved_at"):
            exp_f1, exp_n = m["registry_f1_20"], m["registry_n"]
            note = (f"re-materialised {m['resolved_at']}: expected value is the registry's "
                    f"({m['registry_f1_20']} / n {m['registry_n']}), not the archived board's "
                    f"({m['archived_f1_20']} / n {m['archived_n']}) — see {m['registry_vs_archived']}")
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
            "passed": g2_fail == 0 and g3_fail == 0 and g4_ok, "bisected": BISECTED,
            "resolved": {m["label"]: {"resolved_at": m["resolved_at"], "detections": m["detections"],
                                      "superseded_detections": m.get("archived_detections"),
                                      "expected_f1_20": m["registry_f1_20"], "expected_n": m["registry_n"],
                                      "archived_f1_20": m["archived_f1_20"], "archived_n": m["archived_n"]}
                         for m in membership["members"] if m.get("resolved_at")},
            "cells": rows}


def _promote_existing_row(row: dict[str, Any], m: dict[str, Any], cell_slug: str) -> int:
    """Repoint a row that has newly become a board member at the board frame.

    Three ``-opmax`` rows were registered off-board under the old K >= 5 rule and
    so carry the Era-2-frame evaluation (``opmax/era2/<slug>/``) and no scope
    override. Under PI ruling R3 (2026-09-12) they are board members, and a
    member's row records the BOARD-frame score — the same convention the other
    forty follow. The off-board sentence in ``_note`` is replaced rather than
    deleted, so the row still says what it used to be.

    Args:
        row: The condition row in ``results/run-conditions.json``.
        m: Its ``opmax/membership.json`` member.
        cell_slug: The member's slug, for the board-frame evaluation path.

    Returns:
        1 if the row was changed, else 0 (so the call is idempotent).
    """
    if not m.get("on_board"):
        return 0
    board_eval = f"{BOARD_DIR}/cells/{cell_slug}/evaluation.json"
    if row.get("eval_path") == board_eval:
        return 0
    old_eval = row.get("eval_path")
    row["eval_path"] = board_eval
    row["scope_override"] = {"test_set_id": FRAME_ID, "bounds_path": FRAME,
                             "n_test_tiles": FRAME_TILES,
                             "calibration_set_id": None, "n_calibration_tiles": None}
    note = str(row.get("_note", ""))
    stale = f"K = {m['k']} < 5 (card § 3 rule); registered, not a member; the row's evaluation is the Era-2-frame score."
    replacement = (
        f"ADMITTED TO THE BOARD 2026-09-12 (PI ruling R3, "
        f"planning/k-ladder-review-2026-09-11.md § 4): the board takes every "
        f"verified cell on its frame regardless of K, so this K = {m['k']} cell is "
        f"a member. Its evaluation is now the board-frame score ({FRAME_ID}); the "
        f"Era-2-frame score it carried while off-board is kept at {old_eval} and "
        f"is the waived opmax/g2 evaluation.")
    note = note.replace(stale, replacement) if stale in note else note.rstrip() + " " + replacement
    row["_note"] = note
    print(f"  {row['label']}: promoted to board member; eval_path -> {board_eval}")
    return 1


def _resolve_existing_row(row: dict[str, Any], m: dict[str, Any]) -> int:
    """Point an already-registered ``-opmax`` row at its re-materialised file.

    Idempotent: returns 1 the first time it rewrites ``row``, 0 thereafter and
    0 for rows that were never mis-materialised. The old "registry differs"
    sentence is dropped from ``_note`` (it described a discrepancy that no
    longer exists) and replaced with the resolution record.

    Args:
        row: The condition row in ``results/run-conditions.json``.
        m: The matching ``opmax/membership.json`` member.

    Returns:
        1 if the row was changed, else 0.
    """
    if not m.get("resolved_at") or row.get("detections") == m["detections"]:
        return 0
    old_n, new_n = m["archived_n"], m["registry_n"]
    row["detections"] = m["detections"]
    note = str(row.get("_note", ""))
    # Drop the superseded discrepancy sentence: register() appends it last, so
    # everything from the marker onwards goes.
    marker = " NOTE: the materialisation registry's sweep best point differs"
    idx = note.find(marker)
    if idx != -1:
        note = note[:idx]
    # The waiver sentence named the archived F1 as the value the g2 evaluation
    # reproduces; it now reproduces the registered one.
    note = note.replace(f"reproduction of the archived F1 ({m['archived_f1_20']})",
                        f"reproduction of the registered F1 ({m['registry_f1_20']})")
    row["_note"] = note.rstrip() + (
        f" RE-MATERIALISED {m['resolved_at']}: the detection file this row pointed at "
        f"({m['archived_detections']}, materialised 2026-04-19 at bd24293d4) did not hold the operating point the "
        f"materialisation registry registered — it held {old_n} features scoring F1@20 {m['archived_f1_20']}, while "
        f"re-applying the registry's own filter (union feature i <-> probabilities key candidate_i, "
        f"vote_count >= {m['vote_threshold']} AND mound_probability >= {m['prob_threshold']}) to stage "
        f"{m['stage_id']} yields {new_n} features, the registry's count, at F1@20 {m['registry_f1_20']}. The union, "
        f"the probabilities and the sweep are unchanged since 2026-04-17/18, so the 2026-04-19 materialisation was "
        f"the defective side. Replaced from the registered stage by scripts/materialise_opmax_cells.py "
        f"(counts {old_n} -> {new_n}); provenance sidecar beside the file; the superseded file and this row's "
        f"superseded evaluations are archived under "
        f"archive/superseded-leaderboards/gs-era2-verified-board-2026-09-10-opmax-stale-materialisation/.")
    return 1


#: Marker that makes the vintage sentence idempotent in a row's ``_note``.
VINTAGE_MARKER = " VINTAGE 2026-09-11:"
#: The comparison built for the one ``union-rebuilt`` cell (S153, 2026-09-11).
VINTAGE_COMPARISON = f"{OPMAX_DIR}/staleness-2026-09-11"


def _vintage_sentence(m: dict[str, Any]) -> str | None:
    """The ``_note`` sentence recording a rebuilt union, or ``None``.

    Only the ``union-rebuilt`` class needs one: the union at the cell's
    ``consensus_path`` no longer holds the set its verifier cropped, so the
    index join that defines the cell cannot be re-run against today's file and
    a reader must not take a count derived from it at face value.

    Args:
        m: A member row from ``opmax/membership.json``.

    Returns:
        The sentence to append, or ``None`` when the cell's inputs are still
        the vintage its verifier saw.
    """
    vintage = m.get("vintage") or {}
    if vintage.get("verdict") != "union-rebuilt":
        return None
    return (
        f"{VINTAGE_MARKER} the proposer union at {vintage['union']} was re-materialised on "
        f"2026-07-30 (f6116cba0, 77bb342b4) from {vintage['n_probabilities']} features to "
        f"{vintage['n_union']}, in a different order, so this row's stage probabilities — the "
        f"{vintage['n_probabilities']} the verifier actually returned — can no longer be joined to "
        "it by candidate index. An index join against today's file yields a plausible but "
        "meaningless count; it is not an operating point. THE ROW IS UNCHANGED AND CORRECT ON ITS "
        "OWN VINTAGE: sweeping the union blob at 09fe46a7f against this stage's own probabilities "
        f"reproduces the committed {vintage['sweep']} in all 240 rows, its 20 m argmax is the "
        f"registered (vote_t {m['vote_threshold']}, prob_t {m['prob_threshold']}) at n "
        f"{m['registry_n']}, and re-applying the registry filter to that blob yields exactly the "
        f"{m['archived_n']} features this row's detection file holds. For comparison, the same "
        "operating point applied to the union as committed today, against the complete 2026-09-08 "
        "re-verification of that union (stage verified-v1-n3-recovery-2026-09-08, 43516df9a), "
        f"gives a different cell — see {VINTAGE_COMPARISON}/ for both sweeps, the comparison cell "
        "and its Era-2-frame score. Whether this row should be repointed at that vintage is the "
        "PI's call: it would change the row from the archived board's cell to a September "
        "re-verification. No repoint has been made.")


def sync_notes(membership: dict[str, Any], write: bool) -> int:
    """Append the vintage sentence to any registered ``-opmax`` row that needs it.

    Deliberately narrow: it touches ``_note`` on existing condition rows and
    nothing else — no new rows, no waivers, and above all no write to the
    board's analysis row, which is signed. Idempotent via
    :data:`VINTAGE_MARKER`.

    Args:
        membership: The parsed ``opmax/membership.json``.
        write: Persist to ``results/run-conditions.json``.

    Returns:
        The number of rows changed.
    """
    rc = _load(RUN_CONDITIONS.relative_to(REPO_ROOT).as_posix())
    dec = rc["decomposition"]
    changed = 0
    for m in membership["members"]:
        sentence = _vintage_sentence(m)
        if sentence is None:
            continue
        label = m["label"] + SUFFIX
        run = dec.get(m["run_id"])
        row = next((c for c in (run or {}).get("conditions", []) if c["label"] == label), None)
        if row is None:
            print(f"  {label}: not registered — skipped")
            continue
        if VINTAGE_MARKER in str(row.get("_note", "")):
            continue
        row["_note"] = str(row.get("_note", "")).rstrip() + sentence
        changed += 1
        print(f"  {label}: vintage sentence appended ({m['vintage']['verdict']})")
    if write and changed:
        RUN_CONDITIONS.write_text(json.dumps(rc, indent=1, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
    print(f"{'wrote' if write else 'would write'} {changed} row note(s)")
    return changed


def register(membership: dict[str, Any], write: bool,
             skip_analysis_row: bool = False) -> list[str]:
    rc = _load(RUN_CONDITIONS.relative_to(REPO_ROOT).as_posix())
    ra = _load(RUN_ANALYSES.relative_to(REPO_ROOT).as_posix())
    dec = rc["decomposition"]
    added = waived = resolved = promoted = 0
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
        existing = next((c for c in run["conditions"] if c["label"] == new_label), None)
        if existing is not None:
            resolved += _resolve_existing_row(existing, m)
            promoted += _promote_existing_row(existing, m, s)
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
        if str(m.get("registry_vs_archived", "")).startswith("differs"):
            note += (f" NOTE: the materialisation registry's sweep best point {m['registry_vs_archived']} — the "
                     "sweep_2d.json predates or differs from the materialised file (sweep-staleness class, Obs 461); "
                     "the row is the file the archived board scored.")
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
    if skip_analysis_row:
        if write:
            RUN_CONDITIONS.write_text(json.dumps(rc, indent=1, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
        print(f"{'wrote' if write else 'would write'} {added} new {SUFFIX} rows, "
              f"{resolved} re-materialised rows repointed, {promoted} rows promoted to "
              f"board members and {waived} g2 waivers; the board's analysis row was NOT "
              f"touched (--no-analysis-row): it is PI-SIGNED, and its conditions_compared "
              f"would have gone to {len(board_ids)} members")
        return board_ids
    rows = ra["analyses"] if isinstance(ra, dict) else ra
    arow = next(r for r in rows if r["analysis_id"] == BOARD_ID)
    before = len(arow["conditions_compared"])
    for cid in board_ids:
        if cid not in arow["conditions_compared"]:
            arow["conditions_compared"].append(cid)
    # Count the '-era2b' rows from the list itself: on a re-run ``before``
    # already includes the opmax rows and would double-count them.
    n_era2b = sum(1 for cid in arow["conditions_compared"] if not cid.endswith(SUFFIX))
    arow["_conditions_note"] = (
        f"{n_era2b} '-era2b' rows (the registered cells re-scored on the board frame; the committed rows remain the "
        f"members' records) plus {len(board_ids)} '{SUFFIX}' rows (the archived Era-2 PV board's sweep-optimal Gemini 3 "
        f"cells, in-sample optima of the E56 class, registered 2026-09-10 for the symmetry fix; three K = 3 archived "
        f"cells are registered but off-board by the K >= {MIN_K} rule). Both families at both levels: committed "
        "operating points and sweep optima.")
    arow["outcome"] = "PENDING: re-tier after the symmetry fix (filled by build_gs_era2_board finalise)"
    if write:
        RUN_CONDITIONS.write_text(json.dumps(rc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        RUN_ANALYSES.write_text(json.dumps(ra, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{'wrote' if write else 'would write'} {added} new {SUFFIX} rows, {resolved} re-materialised rows "
          f"repointed and {waived} g2 waivers; analysis row "
          f"{BOARD_ID} conditions_compared {before} -> {len(arow['conditions_compared'])}")
    return board_ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["membership", "jobs", "gates", "register", "notes"])
    parser.add_argument("--write", action="store_true", help="register: persist to the register files")
    parser.add_argument("--no-analysis-row", action="store_true",
                        help=("register: mint and repoint condition rows but do "
                              "NOT write to the board's analysis row. That row "
                              "is PI-signed; amending its membership, note or "
                              "outcome is the PI's call. The tiering instrument "
                              "is then given a board-local copy of the analyses "
                              "file carrying the full membership."))
    parser.add_argument("--only-resolved", action="store_true",
                        help="jobs: emit only the re-materialised rows' jobs (rescore-commands.sh + "
                             "rescore-jobs.txt for xargs -P)")
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
        write_jobs(membership, only_resolved=args.only_resolved)
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
    if args.command == "notes":
        sync_notes(membership, args.write)
        return 0
    register(membership, args.write, skip_analysis_row=args.no_analysis_row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
