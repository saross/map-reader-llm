"""Phase 0 census for the D57 (4) re-score: identities, groups, and feature counts.

D57 (4) re-score, 2026-10-09 (Session 163). Read-only with respect to the
repository: committed evaluations are read from ``HEAD`` with ``git show`` and
detection files from the working tree; the only files written are ``--out``'s.

What it does (plan § 3.1 and § 7 row 1):

1. Re-derives the moved set (cells moving by at least 0.001, or whose MCC state
   flips) and the sub-0.001 pairing twins (class ``as-predicted`` but not moved)
   from ``rescore_b.jsonl``, with ``summarise_new.py``'s rules, and checks the
   moved set against the tracked ``moved_new.csv``.
2. For every moved cell and twin, resolves its recorded detection inputs
   (``_metadata.cli_args``), counts each file's features, and compares with the
   committed ``n_detections`` (per run for a multi-run cell).
3. Assigns each cell to its plan § 3.1 group.
4. As a second, value-based drift check, compares each cell's committed
   four-decimal F1, P, R (and MCC) with the jsonl's OFF values (the old scorer
   on the inputs as they were on 2026-10-08), at 1e-4.

Usage (on sapphire, from anywhere)::

    .venv/bin/python reports/d57-4-rescore-2026-10-09-scripts/census.py \\
        --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --rescore-b ~/scratch/source-tile-gap-2026-10-08/out/rescore_b.jsonl \\
        --out ~/scratch/d57-4-rescore-2026-10-09/out/census.json
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d57_common as dc  # noqa: E402

#: Tracked summary of the moved cells (scorer-frames report).
MOVED_CSV = "reports/scorer-frames-d50-d51-2026-10-08-scripts/out/summary/moved_new.csv"

#: Tracked blast-radius register columns (conditions, analyses) for every cell.
CELLS_CSV = "reports/frames-blast-radius-2026-10-07-scripts/out/summary/cells.csv"

#: The null-exemplar filter manifest (rewritten by ``--stage filter``).
NX_MANIFEST = "results/null-exemplar-sensitivity-2026-09-13/detections_manifest.json"


def resolve_inputs(repo: Path, cli: dict[str, Any]) -> tuple[list[str], list[str], str]:
    """Resolve a cell's recorded detection files, repository-relative where possible.

    Args:
        repo: Repository root (the replay worktree).
        cli: The cell's ``_metadata.cli_args``.

    Returns:
        ``(files, notes, shape)`` — shape is ``list`` or ``dir``.
    """
    notes: list[str] = []
    if cli.get("detections"):
        dets = cli["detections"]
        dets = [dets] if isinstance(dets, str) else list(dets)
        files = []
        for d in dets:
            rel, note = dc.to_repo_relative(repo, str(d))
            files.append(rel)
            if note:
                notes.append(note)
        return files, notes, "list"
    if cli.get("detections_dir"):
        from scripts.evaluate_detections import find_detection_files  # noqa: PLC0415

        rel, note = dc.to_repo_relative(repo, str(cli["detections_dir"]))
        if note:
            notes.append(note)
        base = Path(rel) if Path(rel).is_absolute() else repo / rel
        if not base.is_dir():
            return [], notes + [f"detections_dir absent: {rel}"], "dir"
        try:
            found = find_detection_files(base, cli.get("glob"))
        except Exception as exc:  # noqa: BLE001 - record the resolver's refusal
            return [], notes + [f"resolver refused: {exc}"], "dir"
        out = []
        for f in found:
            try:
                out.append(str(Path(f).resolve().relative_to(repo.resolve())))
            except ValueError:
                out.append(str(f))
        return out, notes, "dir"
    return [], ["no detections recorded"], "none"


def count_check(repo: Path, files: list[str], committed: list[int | None],
                shape: str) -> dict[str, Any]:
    """Compare each detection file's feature count with the committed count.

    Args:
        repo: Repository root.
        files: Resolved detection files.
        committed: Committed counts (one per run).
        shape: ``list`` or ``dir``.

    Returns:
        A record with per-file counts and a status.
    """
    per_file = []
    absent = False
    for f in files:
        p = Path(f) if Path(f).is_absolute() else repo / f
        if not p.is_file():
            absent = True
            per_file.append({"path": f, "exists": False})
            continue
        per_file.append({"path": f, "exists": True, "n": dc.feature_count(p)})
    if not files or absent:
        status = "absent"
    else:
        got = [e["n"] for e in per_file]
        ok = got == list(committed)
        multi = len(files) > 1 or shape == "dir"
        status = ("multi-" if multi else "") + ("match" if ok else "mismatch")
    return {"files": per_file, "committed_counts": committed, "status": status}


def value_check(ev: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    """Compare committed four-decimal values with the jsonl's OFF values.

    Args:
        ev: The committed evaluation.
        row: The cell's jsonl row.

    Returns:
        ``{"reproduces": bool | None, "worst": float | None, "misses": [...]}``.
    """
    off = row.get("blast_off") or {}
    committed = dc.per_buffer_committed(ev)
    misses: list[str] = []
    worst = 0.0
    compared = 0
    for buf, vals in (off.get("per_buffer") or {}).items():
        c = committed.get(buf)
        if not c:
            continue
        for m in dc.METRICS:
            if c.get(m) is None:
                continue
            compared += 1
            d = abs(c[m] - vals[m])
            worst = max(worst, d)
            if d > dc.TOL_4DP:
                misses.append(f"{m}@{buf}: committed {c[m]} off {vals[m]:.6f}")
    cm = dc.committed_mcc(ev)
    if isinstance(cm, (int, float)) and isinstance(off.get("mcc"), (int, float)):
        compared += 1
        d = abs(cm - off["mcc"])
        worst = max(worst, d)
        if d > dc.TOL_4DP:
            misses.append(f"mcc: committed {cm} off {off['mcc']:.6f}")
    if not compared:
        return {"reproduces": None, "worst": None, "misses": []}
    return {"reproduces": not misses, "worst": worst, "misses": misses[:6]}


def main() -> int:
    """Build the census and write it as JSON and CSV."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True, help="The NEW worktree root.")
    ap.add_argument("--rescore-b", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    sys.path.insert(0, str(repo))
    os.chdir(repo)

    rows = dc.load_jsonl(args.rescore_b.expanduser())
    classes = dc.classify(rows)
    moved = {e for e, r in classes.items() if r["moved"]}
    twins = {e for e, r in classes.items()
             if r["class"] == "as-predicted" and not r["moved"]}
    moved_csv = {r["eval"]: r for r in csv.DictReader((repo / MOVED_CSV).open())}
    register = {r["eval"]: r for r in csv.DictReader((repo / CELLS_CSV).open())}
    nx_manifest: dict[str, int] = {}
    if (repo / NX_MANIFEST).is_file():
        for cell in json.loads((repo / NX_MANIFEST).read_text())["cells"]:
            for f in cell["files"]:
                nx_manifest[f["filtered"]] = f["n_kept"]

    records = []
    for rel in sorted(moved | twins):
        rec: dict[str, Any] = {"eval": rel, "twin": rel in twins,
                               "class": classes[rel]["class"],
                               "d_off": classes[rel]["d_off"],
                               "registered": bool(
                                   (moved_csv.get(rel) or register.get(rel) or {})
                                   .get("conditions")),
                               "conditions": (moved_csv.get(rel) or register.get(rel)
                                              or {}).get("conditions", "")}
        ev = dc.committed_eval(repo, rel)
        if ev is None:
            rec.update({"group": "MISSING-FROM-HEAD"})
            records.append(rec)
            continue
        meta = ev.get("_metadata") or {}
        cli = meta.get("cli_args") or {}
        files, notes, shape = resolve_inputs(repo, cli)
        fc = count_check(repo, files, dc.committed_counts(ev), shape)
        if rel.startswith(dc.NULL_EX_PREFIX) and nx_manifest:
            fc["manifest_counts"] = [nx_manifest.get(f) for f in files]
            fc["manifest_agrees"] = all(
                e.get("n") == nx_manifest.get(e["path"]) for e in fc["files"])
        pinned = bool(meta.get("e82_input_vintage"))
        mismatch = fc["status"] in ("mismatch", "multi-mismatch")
        rec.update({
            "group": dc.group_of(rel, mismatch=mismatch, pinned=pinned,
                                 twin=rel in twins),
            "script_path": meta.get("script_path"),
            "metadata_version": meta.get("metadata_version"),
            "generated_at_utc": meta.get("generated_at_utc"),
            "e82_input_vintage": meta.get("e82_input_vintage"),
            "cli_keys": sorted(cli),
            "bootstrap": cli.get("bootstrap"), "seed": cli.get("seed"),
            "method": (meta.get("bootstrap") or {}).get("method"),
            "shape": shape, "input_notes": notes, "feature_count": fc,
            "values": value_check(ev, classes[rel]["row"]),
            "new_scope": classes[rel]["row"].get("new_scope"),
        })
        records.append(rec)

    summary = {
        "n_jsonl_rows": len(rows),
        "classes": dict(Counter(r["class"] for r in classes.values())),
        "n_moved": len(moved), "n_twins": len(twins),
        "moved_equals_moved_new_csv": moved == set(moved_csv),
        "moved_not_in_csv": sorted(moved - set(moved_csv)),
        "csv_not_moved": sorted(set(moved_csv) - moved),
        "groups": dict(Counter(r["group"] for r in records)),
        "groups_registered": dict(Counter(r["group"] for r in records if r["registered"])),
        "feature_count_status_moved": dict(Counter(
            r["feature_count"]["status"] for r in records
            if not r["twin"] and "feature_count" in r)),
        "feature_count_status_twins": dict(Counter(
            r["feature_count"]["status"] for r in records
            if r["twin"] and "feature_count" in r)),
        "mismatches": sorted(r["eval"] for r in records if r.get("feature_count", {})
                             .get("status") in ("mismatch", "multi-mismatch")),
        "values_not_reproducing": sorted(
            r["eval"] for r in records if r.get("values", {}).get("reproduces") is False),
        "twins": sorted(twins),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"summary": summary, "cells": records}, indent=1,
                                   default=str) + "\n")
    with args.out.with_suffix(".csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["eval", "group", "twin", "registered", "class", "fc_status",
                    "pinned", "values_reproduce", "values_worst"])
        for r in records:
            w.writerow([r["eval"], r["group"], r["twin"], r["registered"], r["class"],
                        r.get("feature_count", {}).get("status"),
                        bool(r.get("e82_input_vintage")),
                        r.get("values", {}).get("reproduces"),
                        r.get("values", {}).get("worst")])
    print(json.dumps({k: v for k, v in summary.items() if k != "twins"}, indent=1,
                     default=str)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
