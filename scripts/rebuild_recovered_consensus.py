#!/usr/bin/env python3
"""Rebuild a pool's greedy consensus sweep from its RECOVERED passes.

The E71 dead-tile recovery (``99ae28ec4``, 2026-07-30) rewrote fifteen
passes' detection files in place, but re-materialised consensus only for the
two live ``pv-diag-384`` cells (``f6116cba0``). Every other consensus sweep
built from a recovered pass — ``n1-outstanding-384``'s two ``pro-*-high-t0``
pools (the H6 comparator), ``e47-propose-brief``, ``h12-v2``'s
``r3-hp-heavy``, ``flash35-pv-2x2``'s ``flash35-min-text-1of10`` — still
votes over the PRE-recovery detections. This driver applies the E71
post-recovery recipe to a pool:

1. gate: every base pass file must post-date the recovery commit and the
   pool's consensus directory must be git-tracked (verify before moving);
2. archive: ``git mv`` the current sweep to
   ``archive/pre-recovery-2026-09-08/<run>__<pool>__consensus`` (the
   2026-07-30 naming; archive, never delete);
3. rebuild: ``merge_passes.py --sweep`` over the pool's ``run_*`` passes at
   the original protocol (greedy star clustering, 20 m, all passes);
4. report: cluster counts per threshold before and after.

Dry-run by default; ``--write`` performs steps 2-3. Re-scoring is a separate
step (``scripts/recovery_reeval.py``) because ``--require-clean-inputs``
needs the rebuilt sweep committed first.

Usage::

    python scripts/rebuild_recovered_consensus.py --run n1-outstanding-384 \\
        --pool pro-image-high-t0 --pool pro-text-high-t0            # plan
    python scripts/rebuild_recovered_consensus.py ... --write

Zero API. Seconds per pool.

Created: 2026-09-08 (Session 150)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RECOVERY_COMMIT = "99ae28ec4"
ARCHIVE_ROOT = REPO / "archive/pre-recovery-2026-09-08"


def git(*args: str) -> str:
    """Run git in the repo and return stdout."""
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                          check=True).stdout.strip()


def run_directory(run_id: str) -> Path:
    """The run's directory from the registry."""
    reg = json.loads((REPO / "results/run-registry.json").read_text())["registry"]
    entry = next((e for e in reg if e["run_id"] == run_id), None)
    if entry is None:
        sys.exit(f"{run_id}: not in results/run-registry.json")
    return REPO / entry["directory_path"]


def pool_dir_for(run_id: str, pool: str) -> Path:
    """The pool directory: the register's ``path`` under the run, else the pool name."""
    rc = json.loads((REPO / "results/run-conditions.json").read_text())["decomposition"]
    spec = (rc.get(run_id) or {}).get("proposer_pools", {}).get(pool)
    rel = spec.get("path") if isinstance(spec, dict) and spec.get("path") else None
    base = run_directory(run_id)
    for cand in ([base / rel] if rel else []) + [base / pool, base / "proposer" / pool]:
        if cand.is_dir():
            return cand
    sys.exit(f"{run_id}::{pool}: no pool directory found under {base}")


def pass_files(pool_dir: Path) -> list[tuple[str, list[Path]]]:
    """The base pass files per ``run_N`` directory (chunked passes hold several)."""
    dirs = sorted((d for d in pool_dir.glob("run_*") if d.name[4:].isdigit()),
                  key=lambda d: int(d.name[4:]))
    out = []
    for d in dirs:
        gj = sorted(d.glob("*.geojson"))
        if not gj:
            sys.exit(f"{d}: no detections geojson")
        out.append((d.name, gj))
    return out


def recovered_passes() -> set[str]:
    """``run_id::pool::runN`` ids the E71 rerun rewrote (its own results file)."""
    doc = json.loads((REPO / "reports/verification/recovery-rerun-results.json").read_text())
    return {r["pass_id"] for r in doc["results"]}


def is_post_recovery(path: Path) -> bool:
    """True when the file's last commit is the recovery commit or later."""
    last = git("log", "-1", "--format=%H", "--", str(path.relative_to(REPO)))
    if not last:
        return False
    # ancestor test: recovery commit reachable from the file's last commit
    return subprocess.run(["git", "merge-base", "--is-ancestor", RECOVERY_COMMIT, last],
                          cwd=REPO).returncode == 0


def summary(consensus_dir: Path) -> dict | None:
    p = consensus_dir / "voting_summary.json"
    return json.loads(p.read_text()) if p.exists() else None


def process(run_id: str, pool: str, write: bool) -> None:
    pool_dir = pool_dir_for(run_id, pool)
    consensus = pool_dir / "consensus"
    passes = pass_files(pool_dir)
    rewritten = recovered_passes()
    print(f"== {run_id}::{pool}  pool {pool_dir.relative_to(REPO)}  passes {len(passes)}")
    # Gate: a pass the rerun rewrote must be committed at or after the
    # recovery; a pass it never touched was never dead and is complete as is.
    stale = [(d, f) for d, files in passes for f in files
             if f"{run_id}::{pool}::{d.replace('_', '')}" in rewritten
             and not is_post_recovery(f)]
    n_rewritten = sum(1 for d, _ in passes
                      if f"{run_id}::{pool}::{d.replace('_', '')}" in rewritten)
    print(f"  passes the E71 rerun rewrote: {n_rewritten}")
    if stale:
        sys.exit("  rewritten passes NOT at post-recovery vintage: "
                 + ", ".join(str(f.relative_to(REPO)) for _, f in stale))
    if n_rewritten == 0:
        sys.exit("  no pass of this pool was in the recovery population — nothing to rebuild")
    if not consensus.is_dir():
        sys.exit(f"  no consensus directory at {consensus}")
    tracked = git("ls-files", str(consensus.relative_to(REPO))).splitlines()
    if not tracked:
        sys.exit(f"  {consensus.relative_to(REPO)} is not git-tracked — refusing to move it")
    before = summary(consensus)
    print(f"  before: {before}")
    dest = ARCHIVE_ROOT / f"{run_id}__{pool}__consensus"
    if not write:
        print(f"  would git mv {consensus.relative_to(REPO)} -> {dest.relative_to(REPO)}")
        print(f"  would run merge_passes.py --sweep --input-dir {pool_dir.relative_to(REPO)}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    git("mv", str(consensus.relative_to(REPO)), str(dest.relative_to(REPO)))
    subprocess.run([sys.executable, str(REPO / "scripts/merge_passes.py"), "--sweep",
                    "--input-dir", str(pool_dir), "--output-dir", str(consensus)],
                   cwd=REPO, check=True)
    after = summary(consensus)
    print(f"  after:  {after}")
    print(f"  archived pre-recovery sweep at {dest.relative_to(REPO)}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--pool", action="append", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    for pool in args.pool:
        process(args.run, pool, args.write)
    return 0


if __name__ == "__main__":
    sys.exit(main())
