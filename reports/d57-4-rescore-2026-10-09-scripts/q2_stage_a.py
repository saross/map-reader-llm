"""D58 Q2 Stage A: score the drifted or pinned cells' inputs AS SCORED, under OLD and NEW.

D57 (4) re-score, 2026-10-09 (Session 163). Ruling D58 Q2: the 25 live cells
whose detection inputs changed after they were scored are re-scored in two
stages where the inputs as scored can be recovered — first the new scorer on
those inputs (isolating D50), then today's inputs (isolating the drift). This
script runs Stage A only; Stage B is NOT run (the brief), only reported.

Vintage rule per input (as ``reports/input-drift-2026-10-07-scripts/
rescore_scored_vintage.py`` does):

* detections: the cell's ``_metadata.e82_input_vintage`` pin when it names the
  file (or a parent directory); otherwise the NEWEST commit whose tracked file
  has the committed feature count (searched here over ``git log`` and
  cross-checked against the input-drift trace's first matching commit);
* references and bounds: the E82 pin when present; otherwise the last commit
  touching the path at or before the evaluation's ``generated_at_utc``.

Each input is materialised with ``git show`` into ``--scratch/blobs`` (outside
both trees). The cell's recipe (buffers, bootstrap, seed, label, MCC, tile join,
workers) is replayed with ``evaluate_detections.py`` from the OLD tree
(``git archive b3c52591d``) and from the NEW worktree, each into scratch. OLD
must reproduce the committed cell: every four-decimal F1, P, R and interval
bound at every buffer, the tile-MCC block, and ``n_detections``. NEW − OLD is
the D50 effect alone.

Read-only with respect to both trees (outputs go to ``--scratch``).

Usage (on sapphire)::

    .venv/bin/python q2_stage_a.py --new-repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --old-tree ~/scratch/d57-4-rescore-2026-10-09/old \\
        --census ~/scratch/d57-4-rescore-2026-10-09/out/census.json \\
        --scratch ~/scratch/d57-4-rescore-2026-10-09/q2 --workers 12
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d57_common as dc  # noqa: E402
from replay_cell import build_argv  # noqa: E402
from run_replays import THREAD_ENV, slug  # noqa: E402

#: Tracked input-drift trace (cross-check for the unpinned vintage search).
TRACE = "reports/input-drift-2026-10-07-scripts/out/trace.json"

#: The summary keys whose four-decimal values OLD must reproduce, per buffer.
BUFFER_KEYS = ("f1", "f1_ci_lower", "f1_ci_upper", "precision", "p_ci_lower", "p_ci_upper",
               "recall", "r_ci_lower", "r_ci_upper")


def pinned(vintage: dict[str, str] | None, rel: str) -> str | None:
    """The E82 pin covering ``rel`` (file key or parent-directory key), if any."""
    for key, commit in (vintage or {}).items():
        if rel == key or rel.startswith(key.rstrip("/") + "/"):
            return commit
    return None


def as_of(repo: Path, rel: str, when: str | None) -> str:
    """Last commit touching ``rel`` at or before ``when``."""
    args = ["log", "-1", "--format=%h"] + ([f"--before={when}"] if when else [])
    return dc.git(repo, *args, "--", rel) or dc.git(repo, "log", "-1", "--format=%h", "--", rel)


def newest_matching(repo: Path, rel: str, n: int) -> tuple[str | None, int]:
    """Newest commit whose ``rel`` has exactly ``n`` features; also commits examined."""
    commits = dc.git(repo, "log", "--format=%h", "--", rel).split()
    for i, c in enumerate(commits, 1):
        blob = dc.git_show_bytes(repo, c, rel)
        if blob and len(json.loads(blob).get("features") or []) == n:
            return c, i
    return None, len(commits)


def materialise(repo: Path, root: Path, commit: str, rel: str) -> Path:
    """Write ``<commit>:<rel>`` under ``root/<commit>/<rel>``; return the path."""
    out = root / commit / rel
    if not out.is_file():
        blob = dc.git_show_bytes(repo, commit, rel)
        if blob is None:
            raise FileNotFoundError(f"{commit}:{rel}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(blob)
    return out


def score(tree: Path, argv: list[str], log: Path) -> int:
    """Run one tree's ``evaluate_detections.py`` with ``argv`` from ``tree``."""
    with log.open("w") as fh:
        proc = subprocess.run([sys.executable, str(tree / "scripts/evaluate_detections.py"),
                               *argv], cwd=tree, stdout=fh, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, env={**os.environ, **THREAD_ENV},
                              check=False)
    return proc.returncode


def compare(committed: dict[str, Any], got: dict[str, Any]) -> list[str]:
    """Every four-decimal value OLD must reproduce; return the misses."""
    misses = []
    cb = {b["buffer_metres"]: b for b in committed["summary"]["buffers"]}
    gb = {b["buffer_metres"]: b for b in got["summary"]["buffers"]}
    if set(cb) != set(gb):
        misses.append(f"buffers {sorted(cb)} vs {sorted(gb)}")
    for buf in sorted(set(cb) & set(gb)):
        for k in BUFFER_KEYS:
            if cb[buf].get(k) != gb[buf].get(k):
                misses.append(f"{k}@{buf}: committed {cb[buf].get(k)} got {gb[buf].get(k)}")
    ctc = committed["summary"].get("tile_classification") or {}
    gtc = got["summary"].get("tile_classification") or {}
    for m in ("mcc", "sensitivity", "specificity"):
        for k in ("point", "ci_lower", "ci_upper"):
            c = (ctc.get(m) or {}).get(k) if isinstance(ctc.get(m), dict) else None
            g = (gtc.get(m) or {}).get(k) if isinstance(gtc.get(m), dict) else None
            if c != g:
                misses.append(f"{m}.{k}: committed {c} got {g}")
    if ctc.get("confusion") != gtc.get("confusion"):
        misses.append(f"confusion {ctc.get('confusion')} vs {gtc.get('confusion')}")
    if dc.committed_counts(committed) != dc.committed_counts(got):
        misses.append("n_detections")
    return misses


def prepare(new_repo: Path, cell: dict[str, Any], trace: dict[str, Any],
            blobs: Path) -> dict[str, Any]:
    """Recover one cell's inputs as scored; return its vintage record."""
    rel = cell["eval"]
    ev = dc.committed_eval(new_repo, rel)
    meta = ev["_metadata"]
    cli = meta["cli_args"]
    vintage = meta.get("e82_input_vintage")
    when = meta.get("generated_at_utc")
    det_rel = dc.strip_frozen(cli["detections"][0])
    n = dc.committed_counts(ev)[0]
    rec: dict[str, Any] = {"eval": rel, "group": cell["group"], "pinned": bool(vintage),
                           "committed_n": n, "today_n": cell["feature_count"]["files"][0]["n"]}
    if vintage:
        det_c = pinned(vintage, det_rel)
        rec["vintage_rule"] = "e82_input_vintage pin"
        blob = dc.git_show_bytes(new_repo, det_c, det_rel) if det_c else None
        rec["pin_feature_count"] = (len(json.loads(blob).get("features") or [])
                                    if blob else None)
        rec["recoverable"] = bool(det_c) and rec["pin_feature_count"] == n
    else:
        det_c, examined = newest_matching(new_repo, det_rel, n)
        rec["vintage_rule"] = f"newest commit with {n} features ({examined} examined)"
        trace_first = ((trace.get(rel) or {}).get("files") or [{}])[0].get(
            "matching_commits", [None])
        rec["trace_first_match"] = trace_first[0] if trace_first else None
        rec["agrees_with_trace"] = bool(det_c and rec["trace_first_match"]
                                        and (det_c.startswith(rec["trace_first_match"])
                                             or rec["trace_first_match"].startswith(det_c)))
        rec["recoverable"] = det_c is not None
    gt_rel = dc.strip_frozen(cli["ground_truth"])
    bd_rel = dc.strip_frozen(cli["bounds"])
    gt_c = pinned(vintage, gt_rel) or as_of(new_repo, gt_rel, when)
    bd_c = pinned(vintage, bd_rel) or as_of(new_repo, bd_rel, when)
    rec["vintage"] = {"detections": [det_rel, det_c], "ground_truth": [gt_rel, gt_c],
                      "bounds": [bd_rel, bd_c],
                      "head_detections": dc.git(new_repo, "log", "-1", "--format=%h", "--",
                                                det_rel)}
    if not rec["recoverable"]:
        return rec
    local = {"detections": [str(materialise(new_repo, blobs, det_c, det_rel))],
             "ground_truth": str(materialise(new_repo, blobs, gt_c, gt_rel)),
             "bounds": str(materialise(new_repo, blobs, bd_c, bd_rel))}
    rec["cli"] = {**cli, **local, "detections_dir": None, "glob": None}
    return rec


def run_cell(rec: dict[str, Any], new_repo: Path, old_tree: Path,
             scratch: Path) -> dict[str, Any]:
    """Score one recovered cell under OLD and NEW; compare."""
    rel = rec["eval"]
    s = slug(rel)
    committed = dc.committed_eval(new_repo, rel)
    for tag, tree in (("old", old_tree), ("new", new_repo)):
        out = scratch / tag / s
        argv, _ = build_argv(tree, rec["cli"], str(out), add_require_clean=False)
        rec[f"rc_{tag}"] = score(tree, argv, scratch / "logs" / f"{tag}__{s}.log")
        rec[f"argv_{tag}"] = argv
    if rec["rc_old"] == 0:
        old = json.loads((scratch / "old" / s / "evaluation.json").read_text())
        rec["old_misses"] = compare(committed, old)
        rec["old_reproduces"] = not rec["old_misses"]
    if rec["rc_old"] == 0 and rec["rc_new"] == 0:
        new = json.loads((scratch / "new" / s / "evaluation.json").read_text())
        ob = {str(b["buffer_metres"]): b for b in old["summary"]["buffers"]}
        nb = {str(b["buffer_metres"]): b for b in new["summary"]["buffers"]}
        rec["stage_a"] = {b: {"old_f1": ob[b]["f1"], "new_f1": nb[b]["f1"],
                              "delta_f1": round(nb[b]["f1"] - ob[b]["f1"], 4)}
                          for b in ob if b in nb}
        rec["stage_a_mcc"] = {"old": dc.committed_mcc(old), "new": dc.committed_mcc(new)}
        rec["new_scope"] = new["summary"].get("detection_scope")
    return rec


def main() -> int:
    """Recover, score under OLD and NEW, and write ``q2_stage_a.json``."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--new-repo", type=Path, required=True)
    ap.add_argument("--old-tree", type=Path, required=True)
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    if args.workers > 20:
        sys.exit("at most 20 workers on sapphire")
    new_repo = args.new_repo.expanduser().resolve()
    old_tree = args.old_tree.expanduser().resolve()
    scratch = args.scratch.expanduser().resolve()
    (scratch / "logs").mkdir(parents=True, exist_ok=True)
    (scratch / "q2.pid").write_text(f"{os.getpid()}\n")
    census = json.loads(args.census.read_text())
    cells = [c for c in census["cells"] if c["group"] in ("pinned", "drift-unpinned")]
    trace = {r["eval"]: r for r in json.loads((new_repo / TRACE).read_text())["rows"]}
    recs = [prepare(new_repo, c, trace, scratch / "blobs") for c in cells]
    print(f"prepared {len(recs)}; recoverable {sum(r['recoverable'] for r in recs)}",
          flush=True)
    todo = [r for r in recs if r["recoverable"]]
    with ThreadPoolExecutor(max_workers=max(1, args.workers // 2)) as pool:
        done = list(pool.map(lambda r: run_cell(r, new_repo, old_tree, scratch), todo))
    by_eval = {r["eval"]: r for r in done}
    recs = [by_eval.get(r["eval"], r) for r in recs]
    for r in recs:
        r.pop("cli", None)
        print(f"{r['group'][:8]:8s} rec={r['recoverable']} old={r.get('rc_old')}/"
              f"{r.get('rc_new')} reproduces={r.get('old_reproduces')} {r['eval']}",
              flush=True)
    (scratch / "q2_stage_a.json").write_text(json.dumps(recs, indent=1, default=str) + "\n")
    ok = all(r.get("old_reproduces") for r in recs if r["recoverable"])
    print(("DONE" if ok else "PARTIAL") + f" {len(recs)} cells -> {scratch / 'q2_stage_a.json'}",
          flush=True)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
