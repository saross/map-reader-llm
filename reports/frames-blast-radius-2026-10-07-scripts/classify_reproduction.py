"""Classify gate (i) reproduction failures: scorer change, input drift, or unexplained.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only.

For each committed evaluation whose OFF re-score (the project's scorer, unmodified) does not
reproduce the committed values to 1e-4, this script asks why, in order:

1. ``mcc-refused-now`` — only the tile Matthews correlation coefficient (MCC) differs, and
   today's library refuses it under the tile-join invariant (added 2026-09-13) where the
   committed artefact, written earlier, printed a number. F1, precision and recall reproduce.
2. ``input-drift-blob`` — the evaluation recorded git blob hashes of its inputs
   (``_metadata.input_git_state.blob_hashes``) and a current file hashes differently.
3. ``input-drift-count`` — the committed ``n_detections`` (or, for a multi-run cell, the
   per-run counts) differs from the feature count loaded today.
4. ``input-newer-than-eval`` — an input file's last git commit post-dates the evaluation's
   ``generated_at_utc``.
5. ``unexplained`` — none of the above.

Usage::

    python classify_reproduction.py --repo ~/Code/map-reader-llm \
        --cells out/summary/cells.csv --rows out/evaluations.jsonl out/evaluations_rerun.jsonl \
        --out out/summary/reproduction_failures.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


def git(repo: Path, *args: str) -> str:
    """Run a read-only git command in the checkout and return stdout (empty on failure)."""
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                         check=False)
    return res.stdout.strip()


def classify(repo: Path, cell: dict[str, str], row: dict[str, Any]) -> tuple[str, str]:
    """Return (category, evidence) for one non-reproduced cell."""
    notes = cell["repro_notes"]
    parts = [p.strip() for p in notes.split("|") if p.strip()]
    if parts and all(p.startswith("mcc:") for p in parts) and "None" in notes:
        return "mcc-refused-now", notes
    e = json.loads((repo / row["eval"]).read_text())
    md = e.get("_metadata") or {}
    blobs = ((md.get("input_git_state") or {}).get("blob_hashes")) or {}
    changed = []
    for path, h in blobs.items():
        p = path.split("/frozen/", 1)[1] if "/frozen/" in path else path
        if (repo / p).is_file() and h:
            now = git(repo, "hash-object", p)
            if now and now != h:
                changed.append(p)
    if changed:
        return "input-drift-blob", "; ".join(changed)
    committed_n = row.get("committed_n_detections")
    loaded = row.get("n_detections_loaded") or []
    if isinstance(committed_n, (int, float)) and len(loaded) == 1 and loaded[0] != committed_n:
        return "input-drift-count", f"committed n {committed_n}, loaded {loaded[0]}"
    per_run = e.get("per_run") or []
    if per_run and loaded:
        committed_runs = [r.get("n_detections") for r in per_run]
        if committed_runs != list(loaded):
            return "input-drift-count", (f"multi-run: committed per-run n {committed_runs}, "
                                         f"loaded {list(loaded)}")
    gen = md.get("generated_at_utc") or e.get("timestamp")
    if gen:
        try:
            t_eval = datetime.fromisoformat(str(gen).replace("Z", "+00:00"))
        except ValueError:
            t_eval = None
        if t_eval is not None:
            newer = []
            for p in (row.get("detections") or []) + [row.get("ground_truth"),
                                                      row.get("bounds")]:
                if not p:
                    continue
                stamp = git(repo, "log", "-1", "--format=%cI", "--", p)
                if stamp and datetime.fromisoformat(stamp) > t_eval:
                    newer.append(f"{p} ({stamp[:10]})")
            if newer:
                return "input-newer-than-eval", "; ".join(newer)
    return "unexplained", notes


def main() -> int:
    """Classify every non-reproduced cell and write a CSV."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--cells", type=Path, required=True)
    ap.add_argument("--rows", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    rows: dict[str, dict[str, Any]] = {}
    for path in args.rows:
        for line in path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                rows[r["eval"]] = r
    cells = [c for c in csv.DictReader(args.cells.open()) if c["reproduced"] == "False"]
    out = []
    for c in cells:
        cat, ev = classify(repo, c, rows[c["eval"]])
        out.append({"eval": c["eval"], "family": c["family"],
                    "n_out_of_frame": c["n_out_of_frame"], "category": cat,
                    "evidence": ev[:400], "notes": c["repro_notes"][:400]})
    with args.out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    from collections import Counter  # noqa: PLC0415

    print(Counter(o["category"] for o in out))
    print(Counter((o["family"], o["category"]) for o in out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
