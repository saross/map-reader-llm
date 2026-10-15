#!/usr/bin/env python3
"""Inventory every committed evaluation for the S9 staleness sweep (S164, 2026-10-14).

Purpose
-------
PI ruling D65 (2) asks for a sweep "for S9-type staleness (every evaluation
scored before D50 that feeds a signed analysis or claim, the K-ladder Phase 2
cells first)" before the single restatement pass. This script lists every
tracked ``evaluation.json`` outside ``archive/`` at the checkout's ``HEAD``
and records, per file:

* the commit that last wrote it, and the scorer commit and time it records;
* whether it was scored by the D50 scorer (``summary.detection_scope``, which
  only the D50 scorer writes) and whether its recipe can be replayed;
* whether its detection inputs carry origin lists (``source_tiles``,
  ``origin_tiles``, ``origin_source_tile``) and how many rows span two sheets;
* its D57 (4) census disposition (``census_cells.csv`` of 2026-10-10);
* its lineage: registered conditions (``conditions-manifest.json``
  ``provenance.source_files`` and ``run-conditions.json`` ``eval_path``), the
  registered analyses that compare them, their signature status, and the
  claim rows of ``docs/paper/results-claims-inventory-2026-09-12.md`` that
  name the analysis, the condition, or the evaluation's path or directory.

Nothing is written outside ``--out``. No model API is called.

Usage (on sapphire)::

    ~/Code/map-reader-llm/.venv/bin/python inventory.py \\
        --repo ~/scratch/s164-s9-sweep-2026-10-14/wt \\
        --census ~/scratch/d57-4-rescore-2026-10-09/census-old/out/census_cells.csv \\
        --out ~/scratch/s164-s9-sweep-2026-10-14/inventory

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

#: The Era-2 board whose members the brief names second.
ERA2_BOARD = "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"
ERA2_ID = "gs-era2-verified-board-2026-09-10"
#: The K-ladder review directory the brief names first.
K_LADDER = "results/k-ladder-2026-09-12/"
#: Origin columns the D50 scorer reads (``lib_advanced_metrics``).
ORIGIN_COLS = ("source_tiles", "origin_tiles", "origin_source_tile")
#: ``cli_args`` keys ``replay_cell.build_argv`` understands.
KNOWN_KEYS = {"detections", "detections_dir", "batch", "glob", "buffers", "ground_truth",
              "bounds", "bootstrap", "seed", "output_dir", "label", "mcc", "workers",
              "tile_join", "require_clean_inputs"}
CLAIMS = "docs/paper/results-claims-inventory-2026-09-12.md"
CLAIM_ROW = re.compile(r"^\|\s*(R[0-9.]+[a-z]?-\d+)\s*\|")


def git(repo: Path, *args: str) -> str:
    """Run a read-only git command and return stdout (raises on failure)."""
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=True).stdout


def last_commits(repo: Path) -> dict[str, tuple[str, str]]:
    """Map every evaluation path to the (hash, ISO date) of the commit that last wrote it.

    One ``git log`` pass over every ``evaluation.json`` path; the first commit a
    path appears in (newest first) is its last writer.
    """
    out: dict[str, tuple[str, str]] = {}
    cur: tuple[str, str] | None = None
    log = git(repo, "log", "--no-renames", "--format=@@%H %cI", "--name-only", "HEAD",
              "--", "*evaluation.json")
    for line in log.splitlines():
        if line.startswith("@@"):
            h, d = line[2:].split(" ", 1)
            cur = (h, d)
        elif line.strip() and cur is not None and line not in out:
            out[line] = cur
    return out


def origin_profile(path: Path, cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Count a detection file's rows and its origin columns.

    Args:
        path: A GeoJSON detection file.
        cache: Results keyed by path (files are shared between cells).

    Returns:
        ``{"exists", "n", "cols", "n_multi_sheet"}``: the origin columns present
        on any row, and the rows whose origin list names more than one sheet.
    """
    key = str(path)
    if key in cache:
        return cache[key]
    rec: dict[str, Any] = {"exists": path.is_file(), "n": None, "cols": [],
                           "n_multi_sheet": 0}
    if rec["exists"] and path.suffix in (".geojson", ".json"):
        try:
            feats = json.loads(path.read_text()).get("features") or []
        except (ValueError, OSError) as exc:
            rec["error"] = str(exc)
            feats = []
        rec["n"] = len(feats)
        cols: set[str] = set()
        multi = 0
        for f in feats:
            props = f.get("properties") or {}
            for c in ORIGIN_COLS:
                if props.get(c) not in (None, "", []):
                    cols.add(c)
            # A row counts once if any of its origin lists names two sheets.
            spans = False
            for c in ("source_tiles", "origin_tiles"):
                v = props.get(c)
                if isinstance(v, str):
                    v = [t for t in re.split(r"[;,|]", v) if t]
                if isinstance(v, list) and len({str(t).split("_x")[0] for t in v}) > 1:
                    spans = True
            multi += int(spans)
        rec["cols"] = sorted(cols)
        rec["n_multi_sheet"] = multi
    cache[key] = rec
    return rec


def committed_point(ev: dict[str, Any], buffer: int = 20) -> dict[str, Any]:
    """The committed F1, P, R at ``buffer`` and the tile-MCC point (summary)."""
    s = ev.get("summary") or {}
    out: dict[str, Any] = {"f1": None, "precision": None, "recall": None, "mcc": None}
    for b in s.get("buffers") or []:
        if b.get("buffer_metres") == buffer:
            out.update({k: b.get(k) for k in ("f1", "precision", "recall")})
    tc = s.get("tile_classification") or {}
    m = tc.get("mcc")
    out["mcc"] = m.get("point") if isinstance(m, dict) else m
    return out


def detection_paths(cli: dict[str, Any]) -> list[str]:
    """The recorded detection inputs (a list, a directory, or nothing)."""
    d = cli.get("detections")
    if d:
        return [d] if isinstance(d, str) else list(d)
    if cli.get("detections_dir"):
        return [str(cli["detections_dir"])]
    return []


def to_rel(path: str) -> str:
    """Re-root an absolute path into any checkout of this repository."""
    if "/frozen/" in path:
        path = path.split("/frozen/", 1)[1]
    marker = "/map-reader-llm/"
    if path.startswith("/") and marker in path:
        return path.split(marker, 1)[1]
    return path


def lineage(repo: Path) -> tuple[dict[str, set[str]], dict[str, list[dict[str, Any]]],
                                 dict[str, dict[str, Any]], list[tuple[str, str]]]:
    """Build evaluation → conditions, condition → analyses, analysis info, claim rows."""
    by_eval: dict[str, set[str]] = defaultdict(set)
    cm = json.loads((repo / "results/conditions-manifest.json").read_text())
    for c in cm["conditions"]:
        for s in (c.get("provenance") or {}).get("source_files") or []:
            by_eval[s].add(c["condition_id"])
    rc = json.loads((repo / "results/run-conditions.json").read_text())["decomposition"]
    for run, spec in rc.items():
        for c in spec.get("conditions") or []:
            for key in ("eval_path",):
                if c.get(key):
                    by_eval[c[key]].add(f"{run}::{c['label']}")
    ra = json.loads((repo / "results/run-analyses.json").read_text())["analyses"]
    by_cond: dict[str, list[dict[str, Any]]] = defaultdict(list)
    info: dict[str, dict[str, Any]] = {}
    for a in ra:
        sig = a.get("signature") or {}
        info[a["analysis_id"]] = {"signature": sig.get("status"),
                                  "signed_at": sig.get("signed_at"),
                                  "output_path": a.get("output_path"),
                                  "paper_section": a.get("paper_section")}
        for cid in a.get("conditions_compared") or []:
            by_cond[cid].append({"analysis_id": a["analysis_id"]})
    claims: list[tuple[str, str]] = []
    for ln in (repo / CLAIMS).read_text().splitlines():
        m = CLAIM_ROW.match(ln)
        if m:
            claims.append((m.group(1), ln))
    return by_eval, by_cond, info, claims


def analysis_dir(output_path: str | None) -> str:
    """The directory an analysis owns: its ``output_path``, or a file's parent.

    Only directories two or more levels below ``results/`` count, so a file
    such as ``results/k-ladder-2026-09-12/findings.md`` claims its review's
    directory while ``results/`` itself, ``reports/`` and ``docs/`` claim
    nothing. Lineage found this way is recorded as ``analyses_by_dir``,
    separately from the condition lineage.
    """
    p = (output_path or "").rstrip("/")
    if Path(p).suffix:
        p = str(Path(p).parent)
    return p if p.startswith("results/") and p.count("/") >= 1 else ""


def main() -> int:
    """Write ``inventory.json`` and ``inventory.csv``."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    head = git(repo, "rev-parse", "--short=9", "HEAD").strip()
    tracked = set(git(repo, "ls-files").splitlines())
    evals = sorted(p for p in tracked if p.endswith("evaluation.json")
                   and not p.startswith("archive/"))
    lastc = last_commits(repo)
    census = {r["eval"]: r for r in csv.DictReader(args.census.open())}
    by_eval, by_cond, ainfo, claims = lineage(repo)
    era2_rows = json.loads((repo / ERA2_BOARD / "tiering-input/run-analyses.json").read_text())
    era2_rows = era2_rows["analyses"] if isinstance(era2_rows, dict) else era2_rows
    era2_conds = set(next(r for r in era2_rows if r["analysis_id"] == ERA2_ID)
                     ["conditions_compared"])
    out_dirs = {aid: analysis_dir(i["output_path"]) for aid, i in ainfo.items()}
    cache: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for rel in evals:
        ev = json.loads((repo / rel).read_text())
        meta = ev.get("_metadata") or ev.get("metadata") or {}
        cli = meta.get("cli_args") or {}
        summ = ev.get("summary") or {}
        per_run = ev.get("per_run") or []
        d50 = "detection_scope" in summ or any("detection_scope" in (r or {})
                                               for r in per_run)
        dets = [to_rel(p) for p in detection_paths(cli)]
        prof = [origin_profile(repo / p, cache) | {"path": p, "tracked": p in tracked}
                for p in dets]
        conds = sorted(by_eval.get(rel, set()))
        ans = sorted({a["analysis_id"] for c in conds for a in by_cond.get(c, [])})
        if set(conds) & era2_conds and ERA2_ID not in ans:
            # The board's own tiering input lists 153 members; the register
            # row lists 103 (the other 50 are K-ladder identity cells).
            ans = sorted(set(ans) | {ERA2_ID})
        ans_dir = sorted(aid for aid, d in out_dirs.items()
                         if d and d.startswith("results/") and rel.startswith(d + "/")
                         and aid not in ans)
        cell_dir = str(Path(rel).parent)
        claim_hits: dict[str, list[str]] = defaultdict(list)
        for cid, ln in claims:
            for a in ans:
                if a in ln:
                    claim_hits[cid].append(f"analysis:{a}")
            for a in ans_dir:
                if a in ln:
                    claim_hits[cid].append(f"analysis-by-dir:{a}")
            for c in conds:
                if c in ln:
                    claim_hits[cid].append(f"condition:{c}")
            if rel in ln or f"`{cell_dir}`" in ln or f"{cell_dir}/" in ln:
                claim_hits[cid].append("path")
        c_row = census.get(rel) or {}
        replayable = bool(dets) and not cli.get("batch") and not (set(cli) - KNOWN_KEYS)
        rows.append({
            "eval": rel,
            "group": ("k-ladder" if rel.startswith(K_LADDER)
                      else "era2-member" if set(conds) & era2_conds else "other"),
            "era2_member": bool(set(conds) & era2_conds),
            "last_commit": lastc.get(rel, ("", ""))[0][:9],
            "last_commit_date": lastc.get(rel, ("", ""))[1],
            "script_path": meta.get("script_path"),
            "script_git_commit": meta.get("script_git_commit"),
            "generated_at_utc": meta.get("generated_at_utc"),
            "d50_scored": d50,
            "has_recipe": bool(cli),
            "replayable": replayable,
            "multi_run": bool(per_run),
            "n_runs": len(per_run) or 1,
            "detections": prof,
            "inputs_present": all(p["exists"] for p in prof) if prof else False,
            "origin_cols": sorted({c for p in prof for c in p["cols"]}),
            "n_multi_sheet": sum(p["n_multi_sheet"] for p in prof),
            "committed_20m": committed_point(ev),
            "census_disposition": c_row.get("disposition"),
            "census_phase2": c_row.get("phase2") == "True",
            "census_d57_group": c_row.get("d57_group"),
            "conditions": conds,
            "analyses": ans,
            "analyses_by_dir": ans_dir,
            "signed_analyses": sorted(a for a in ans + ans_dir
                                      if ainfo[a]["signature"] not in (None, "unsigned")),
            "signature_status": {a: ainfo[a]["signature"] for a in ans + ans_dir},
            "claim_rows": {k: sorted(set(v)) for k, v in sorted(claim_hits.items())},
        })
    args.out.mkdir(parents=True, exist_ok=True)
    doc = {"repo_head": head, "n": len(rows), "analyses": ainfo, "cells": rows}
    (args.out / "inventory.json").write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    cols = ["eval", "group", "last_commit", "last_commit_date", "script_git_commit",
            "generated_at_utc", "d50_scored", "replayable", "inputs_present", "multi_run",
            "origin_cols", "n_multi_sheet", "census_disposition", "census_phase2",
            "conditions", "analyses", "analyses_by_dir", "signed_analyses", "claim_rows"]
    with (args.out / "inventory.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([";".join(r[c]) if isinstance(r[c], list)
                        else ";".join(r[c]) if isinstance(r[c], dict) else r[c] for c in cols])
    print(f"head {head}: {len(rows)} evaluations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
