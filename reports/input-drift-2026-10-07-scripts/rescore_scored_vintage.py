"""Re-score each input-drift cell on the input vintage its committed numbers came from.

Input-drift provenance trace, 2026-10-07. Read-only with respect to the repository: every
historical input is read with ``git show`` into ``--scratch`` (outside the checkout), and
the only file written is ``--out``. No API is called.

``trace_input_drift.py`` names, for every frames blast-radius input-drift row, the commits
whose detection file has the feature count the committed evaluation records. That is a
count match, not proof. This script closes the loop: it rebuilds each cell's inputs at the
vintage the evaluation scored and re-runs the frames blast-radius OFF scorer
(``blast_lib.score_point``, the project's ``calculate_f1_internal`` and
``calculate_tile_classification`` unchanged) at every committed buffer, then compares with
the committed F1, precision, recall and MCC at a 1e-4 tolerance (four-decimal committed
values). It also runs the frames diagnostic (``blast_lib.geometric_detection_scope``) on
the scored vintage, which the frames report could not do for these cells (its § 7: "the
input-drift cells are measured on today's inputs").

Vintage rule, per input:

- **detections**: the evaluation's own ``_metadata.e82_input_vintage`` pin when it names
  the file or its directory; otherwise the newest commit whose feature count equals the
  committed count (from the trace);
- **references and bounds**: the E82 pin when present; otherwise the last commit touching
  the path at or before the evaluation's ``generated_at_utc``.

Usage (on sapphire; the frames scripts provide the scorer wrappers)::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python rescore_scored_vintage.py \\
        --repo ~/Code/map-reader-llm \\
        --frames-scripts ~/Code/map-reader-llm/reports/frames-blast-radius-2026-10-07-scripts \\
        --trace out/trace.json --scratch ~/scratch/input-drift-2026-10-07/blobs \\
        --out out/scored_vintage.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

#: Tolerance against four-decimal committed values (as in the frames gate (i)).
TOL = 1e-4


def git(repo: Path, *args: str, binary: bool = False) -> Any:
    """Run a read-only git command; return stdout (bytes or stripped text), empty on error."""
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if res.returncode != 0:
        return b"" if binary else ""
    return res.stdout if binary else res.stdout.decode().strip()


def materialise(repo: Path, scratch: Path, commit: str, rel: str) -> Path:
    """Write ``<commit>:<rel>`` under ``scratch/<commit>/<rel>`` and return that path."""
    out = scratch / commit / rel
    if not out.is_file():
        blob = git(repo, "show", f"{commit}:{rel}", binary=True)
        if not blob:
            raise FileNotFoundError(f"{commit}:{rel}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(blob)
    return out


def pinned(vintage: dict[str, str], rel: str) -> str | None:
    """Return the E82 pin covering ``rel`` (file key or a parent-directory key), if any."""
    for key, commit in (vintage or {}).items():
        if rel == key or rel.startswith(key.rstrip("/") + "/"):
            return commit
    return None


def as_of(repo: Path, rel: str, when: str | None) -> str:
    """Return the last commit touching ``rel`` at or before ``when`` (HEAD's if no date)."""
    args = ["log", "-1", "--format=%h"]
    if when:
        args.append(f"--before={when}")
    return git(repo, *args, "--", rel) or git(repo, "log", "-1", "--format=%h", "--", rel)


def compare(committed: dict[str, Any], got: dict[str, Any],
            committed_mcc: Any, got_mcc: Any) -> tuple[bool, list[str]]:
    """Compare committed and re-scored values; return (all within TOL, list of misses)."""
    misses = []
    for b, vals in committed.items():
        for k in ("f1", "precision", "recall"):
            c = (vals or {}).get(k)
            g = got["per_buffer"][b][k]
            if c is not None and abs(c - g) > TOL:
                misses.append(f"{k}@{b}: committed {c} vintage {g:.4f}")
    if isinstance(committed_mcc, (int, float)):
        if got_mcc is None or abs(committed_mcc - got_mcc) > TOL:
            misses.append(f"mcc: committed {committed_mcc} vintage {got_mcc}")
    return not misses, misses


def main() -> int:
    """Rebuild each drift cell's scored inputs, re-score OFF, and diagnose the frame scope."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--frames-scripts", type=Path, required=True)
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    sys.path.insert(0, str(args.frames_scripts.expanduser().resolve()))
    import blast_lib as bl  # noqa: PLC0415
    import rescore_evaluations as rs  # noqa: PLC0415

    bl.add_repo_to_path(repo)
    trace = json.loads(args.trace.read_text())
    results = []
    for row in trace["rows"]:
        spec = rs.parse_eval(repo, row["eval"])
        vintage = row.get("e82_input_vintage") or {}
        when = row.get("generated_at_utc")
        rec: dict[str, Any] = {"eval": row["eval"], "inputs": {}}
        try:
            gt_rel = os.path.relpath(spec["ground_truth"], repo) \
                if os.path.isabs(spec["ground_truth"]) else spec["ground_truth"]
            bd_rel = os.path.relpath(spec["bounds"], repo) \
                if os.path.isabs(spec["bounds"]) else spec["bounds"]
            gt_c = pinned(vintage, gt_rel) or as_of(repo, gt_rel, when)
            bd_c = pinned(vintage, bd_rel) or as_of(repo, bd_rel, when)
            rec["inputs"]["ground_truth"] = {"path": gt_rel, "commit": gt_c,
                                             "head_commit": as_of(repo, gt_rel, None)}
            rec["inputs"]["bounds"] = {"path": bd_rel, "commit": bd_c,
                                       "head_commit": as_of(repo, bd_rel, None)}
            bounds = bl.load_geojson(materialise(repo, args.scratch, bd_c, bd_rel))
            ref = bl.load_geojson(materialise(repo, args.scratch, gt_c, gt_rel))
            dets = []
            for f in row["files"]:
                commit = pinned(vintage, f["path"]) or (f["matching_commits"] or [None])[0]
                if commit is None:
                    raise LookupError(f"no scored vintage found for {f['path']}")
                det = bl.load_detections(materialise(repo, args.scratch, commit, f["path"]),
                                         bounds)
                scoped, diag = bl.geometric_detection_scope(det, bounds)
                dets.append((det, scoped, diag))
                rec["inputs"].setdefault("detections", []).append(
                    {"path": f["path"], "commit": commit, "n_features": len(det),
                     "committed_n": f["committed_n"], "n_out_of_frame": diag["n_out_of_frame"],
                     "n_null_source_tile": diag["n_null_source_tile"]})
            buffers = sorted(int(b) for b in spec["committed"]) or [20]
            want_mcc = isinstance(spec["committed_mcc"], (int, float))
            off = rs.mean_runs([bl.score_point(d[0], ref, bounds, buffers, want_mcc=want_mcc,
                                               tile_join=spec["tile_join"]) for d in dets],
                               buffers)
            off["per_buffer"] = {str(b): v for b, v in off["per_buffer"].items()}
            ok, misses = compare(spec["committed"], off, spec["committed_mcc"], off["mcc"])
            rec.update({
                "status": "scored", "buffers": buffers, "reproduced": ok, "misses": misses,
                "n_out_of_frame_total": sum(d[2]["n_out_of_frame"] for d in dets),
                "vintage_off": off,
            })
        except Exception as exc:  # noqa: BLE001 - record and continue
            rec.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
        results.append(rec)
        print(f"{rec.get('status')} reproduced={rec.get('reproduced')} "
              f"oof={rec.get('n_out_of_frame_total')} {row['eval']}", flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    n_ok = sum(1 for r in results if r.get("reproduced"))
    args.out.write_text(json.dumps({"repo_head": git(repo, "rev-parse", "--short=9", "HEAD"),
                                    "n_rows": len(results), "n_reproduced": n_ok,
                                    "rows": results}, indent=1, default=str))
    print(f"{n_ok}/{len(results)} reproduced on the scored vintage -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
