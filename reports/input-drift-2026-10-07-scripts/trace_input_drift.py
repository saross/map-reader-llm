"""Trace the frames blast-radius gate (i) input-drift rows to the commits that caused them.

Input-drift provenance trace, 2026-10-07. Read-only: reads the repository checkout and the
frames blast-radius outputs, and writes one JSON file to ``--out``. No detection or
evaluation file is opened for writing, and no API is called.

The frames blast-radius measurement (``reports/frames-blast-radius-2026-10-07.md`` § 3.1)
re-scored every committed ``evaluation.json`` against the detection files in today's
working tree and classified 54 cells whose committed feature count, blob hash or input
date no longer matches (``classify_reproduction.py``; categories ``input-drift-count``,
``input-drift-blob`` and ``input-newer-than-eval``). For every one of those rows this
script records:

1. the detection files the re-score read (taken verbatim from the re-score's own row,
   ``detections``, so the resolution is exactly the one ``rescore_evaluations.py`` used);
2. for each file: whether git tracks it, its size, modification time and feature count
   on disk, whether the working tree matches ``HEAD``, and its full ``git log --follow``
   history with the feature count at every commit (``git show <hash>:<path-at-commit>``);
3. the commits whose feature count equals the count the committed evaluation records
   (per run for multi-run cells), and the vintage the evaluation itself pins, if any
   (``_metadata.e82_input_vintage``), with the feature count at that pin;
4. the evaluation's own ``git log --follow`` and its ``generated_at_utc``;
5. the committed and today's (OFF) F1, precision and recall at every buffer the
   re-score evaluated, from the re-score row;
6. every register row that names the evaluation: ``results/conditions-manifest.json``
   (``provenance.source_files``), ``results/run-conditions.json`` (``eval_path`` and
   ``_ignored_evals``), and the analyses in ``results/run-analyses.json`` that compare a
   condition sourced from it, with each analysis's signature status.

Usage (on sapphire, where the re-score rows live)::

    FR=~/Code/map-reader-llm/reports/frames-blast-radius-2026-10-07-scripts
    python3 trace_input_drift.py --repo ~/Code/map-reader-llm \\
        --failures "$FR/out/summary/reproduction_failures.csv" \\
        --rows ~/scratch/frames-blast-radius-2026-10-07/out/evaluations.jsonl \\
               ~/scratch/frames-blast-radius-2026-10-07/out/evaluations_rerun.jsonl \\
        --out out/trace.json

Only the standard library is used; feature counts parse each GeoJSON with ``json``.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

#: Categories of ``reproduction_failures.csv`` that this trace covers.
DRIFT_CATEGORIES = ("input-drift-count", "input-drift-blob", "input-newer-than-eval")


def git(repo: Path, *args: str, binary: bool = False) -> Any:
    """Run a read-only git command in the checkout.

    Args:
        repo: Repository root.
        *args: Git arguments.
        binary: Return raw bytes instead of stripped text.

    Returns:
        Stdout (bytes or stripped text); empty on a non-zero exit.
    """
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if res.returncode != 0:
        return b"" if binary else ""
    return res.stdout if binary else res.stdout.decode().strip()


def count_features(raw: bytes) -> int | None:
    """Return ``len(features)`` of a GeoJSON FeatureCollection, or None if unparseable."""
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        return None
    feats = data.get("features") if isinstance(data, dict) else None
    return len(feats) if isinstance(feats, list) else None


def file_history(repo: Path, rel: str) -> list[dict[str, Any]]:
    """Return the ``git log --follow`` history of one path with feature counts.

    Each entry carries the abbreviated hash, the author date (ISO), the subject, the path
    the file had at that commit (renames are followed), and the feature count of the blob
    at that commit (None when the commit deletes the path or the blob is not GeoJSON).
    """
    out = git(repo, "log", "--follow", "--format=@@%h|%ad|%s", "--date=iso",
              "--name-only", "--", rel)
    hist: list[dict[str, Any]] = []
    cur: dict[str, Any] | None = None
    for line in out.splitlines():
        if line.startswith("@@"):
            h, date, subj = line[2:].split("|", 2)
            cur = {"hash": h, "date": date, "subject": subj, "path": None}
            hist.append(cur)
        elif line.strip() and cur is not None and cur["path"] is None:
            cur["path"] = line.strip()
    for entry in hist:
        p = entry["path"] or rel
        blob = git(repo, "show", f"{entry['hash']}:{p}", binary=True)
        entry["n_features"] = count_features(blob) if blob else None
    return hist


def disk_state(repo: Path, rel: str) -> dict[str, Any]:
    """Describe the working-tree copy of a path: tracked, size, mtime, count, clean."""
    path = repo / rel
    state: dict[str, Any] = {
        "path": rel,
        "tracked": bool(git(repo, "ls-files", "--", rel)),
        "ignored": bool(git(repo, "check-ignore", "--", rel)),
        "exists": path.is_file(),
    }
    if path.is_file():
        st = path.stat()
        state["size_bytes"] = st.st_size
        state["mtime_utc"] = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
        state["n_features_disk"] = count_features(path.read_bytes())
        head_blob = git(repo, "rev-parse", f"HEAD:{rel}")
        state["matches_head"] = bool(head_blob) and git(repo, "hash-object", rel) == head_blob
    return state


def committed_counts(e: dict[str, Any]) -> list[Any]:
    """Return the committed per-run feature counts (one entry for a single-run cell)."""
    per_run = e.get("per_run") or []
    if per_run:
        return [r.get("n_detections") for r in per_run]
    return [(e.get("summary") or {}).get("n_detections")]


def pin_for(vintage: dict[str, str], rel: str) -> tuple[str | None, str | None]:
    """Find the E82 vintage pin that covers a detection file (file key or parent dir key)."""
    for key, commit in vintage.items():
        if rel == key or rel.startswith(key.rstrip("/") + "/"):
            return key, commit
    return None, None


def metrics_table(row: dict[str, Any]) -> dict[str, Any]:
    """Pair committed and OFF F1/P/R per buffer from a re-score row."""
    off = ((row.get("off") or {}).get("per_buffer")) or {}
    committed = row.get("committed") or {}
    table = {}
    for b in sorted(off, key=int):
        table[b] = {"committed": committed.get(b), "off": off[b]}
    return {"per_buffer": table, "committed_mcc": row.get("committed_mcc"),
            "off_mcc": (row.get("off") or {}).get("mcc")}


def register_hits(repo: Path, evals: set[str]) -> dict[str, dict[str, Any]]:
    """Map each evaluation path to the register rows and analyses that name it."""
    hits: dict[str, dict[str, Any]] = {e: {"conditions": [], "run_conditions": [],
                                           "ignored_in": [], "analyses": []} for e in evals}
    manifest = json.loads((repo / "results/conditions-manifest.json").read_text())
    cond_of_eval: dict[str, list[str]] = {}
    for c in manifest["conditions"]:
        for s in (c.get("provenance") or {}).get("source_files") or []:
            if s in hits:
                hits[s]["conditions"].append({
                    "condition_id": c["condition_id"], "n_detections": c.get("n_detections"),
                    "f1_20": ((c["metrics"]["per_buffer"].get("20")) or {}).get("f1"),
                    "f1_50": ((c["metrics"]["per_buffer"].get("50")) or {}).get("f1"),
                    "mcc": (c["metrics"].get("tile_classification") or {}).get("mcc"),
                })
                cond_of_eval.setdefault(s, []).append(c["condition_id"])
    rc = json.loads((repo / "results/run-conditions.json").read_text())
    for run_id, run in rc["decomposition"].items():
        for cond in run.get("conditions") or []:
            if cond.get("eval_path") in hits:
                hits[cond["eval_path"]]["run_conditions"].append({
                    "run_id": run_id, "label": cond.get("label"),
                    "input_vintage": cond.get("input_vintage"),
                })
        for ign in run.get("_ignored_evals") or []:
            p = ign.get("eval_path") if isinstance(ign, dict) else ign
            if p in hits:
                hits[p]["ignored_in"].append(run_id)
    ra = json.loads((repo / "results/run-analyses.json").read_text())
    for a in ra["analyses"]:
        compared = set(a.get("conditions_compared") or [])
        for ev, conds in cond_of_eval.items():
            used = sorted(compared.intersection(conds))
            if used:
                hits[ev]["analyses"].append({
                    "analysis_id": a["analysis_id"], "conditions": used,
                    "signature_status": (a.get("signature") or {}).get("status"),
                })
    return hits


def main() -> int:
    """Trace every drift row and write the JSON record."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--failures", type=Path, required=True)
    ap.add_argument("--rows", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()

    drift = [r for r in csv.DictReader(args.failures.open())
             if r["category"] in DRIFT_CATEGORIES]
    rows: dict[str, dict[str, Any]] = {}
    for path in args.rows:  # later files (the re-run) override earlier rows
        for line in path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                rows[r["eval"]] = r
    hits = register_hits(repo, {r["eval"] for r in drift})
    history_cache: dict[str, list[dict[str, Any]]] = {}
    records = []
    for fr in drift:
        ev = fr["eval"]
        row = rows[ev]
        e = json.loads((repo / ev).read_text())
        md = e.get("_metadata") or {}
        vintage = md.get("e82_input_vintage") or {}
        committed = committed_counts(e)
        files = []
        for i, d in enumerate(row.get("detections") or []):
            rel = os.path.relpath(d, repo) if os.path.isabs(d) else d
            if rel not in history_cache:
                history_cache[rel] = file_history(repo, rel)
            hist = history_cache[rel]
            want = committed[i] if i < len(committed) else None
            pin_key, pin_commit = pin_for(vintage, rel)
            pin_count = None
            if pin_commit:
                pin_count = count_features(git(repo, "show", f"{pin_commit}:{rel}",
                                               binary=True) or b"")
            files.append({
                **disk_state(repo, rel),
                "committed_n": want,
                "loaded_n": (row.get("n_detections_loaded") or [None] * (i + 1))[i],
                "matching_commits": [h["hash"] for h in hist if h["n_features"] == want],
                "e82_pin_key": pin_key, "e82_pin_commit": pin_commit,
                "n_features_at_pin": pin_count,
                "history": hist,
            })
        records.append({
            "eval": ev, "category": fr["category"], "family": fr["family"],
            "evidence": fr["evidence"],
            "generated_at_utc": md.get("generated_at_utc") or e.get("timestamp"),
            "script_git_commit": md.get("script_git_commit"),
            "e82_input_vintage": vintage or None,
            "eval_history": [dict(zip(("hash", "date", "subject"), ln.split("|", 2)))
                             for ln in git(repo, "log", "--follow",
                                           "--format=%h|%ad|%s", "--date=iso", "--",
                                           ev).splitlines()],
            "committed_counts": committed,
            "metrics": metrics_table(row),
            "files": files,
            "register": hits[ev],
        })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"repo_head": git(repo, "rev-parse", "--short=9", "HEAD"),
                                    "n_rows": len(records), "rows": records}, indent=1))
    print(f"{len(records)} rows -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
