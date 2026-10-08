"""Task B of D57 (3): rebuild legacy consensus pools and compare them exactly.

The K = 5 and K = 10 pools of the pv-diag-384 K-ladders are
``merge_passes.py --sweep`` consensus directories committed on 2026-04-17,
whose ``voting_summary.json`` records only ``total_passes`` and the
per-threshold counts — no pass list, so the D51 gate cannot determine their
assessed area (``reports/scorer-frames-d50-d51-2026-10-08.md`` § 5.6). This
script rebuilds each one from its presumed passes and compares the result
with the committed directory, so a pool's pass list can be DECLARED where,
and only where, a rebuild reproduces it.

Presumed passes. ``consensus-n<N>/`` = ``--passes 1,..,N`` (the first-N rule:
``scripts/run_phase3a_image_analysis.sh`` at ``1415e704e`` passes the literal
``"1,2,3,4,5"``; ``reports/union-staleness-retrospective-2026-09-12.md`` § 2);
``consensus/`` = every ``run_*`` directory of the cell (the same script passes
no filter), checked to be exactly ten.

Mergers. The order passes are read in matters (greedy clustering):

* ``april`` — ``scripts/merge_passes.py`` as of ``362f1a305`` (2026-04-17
  00:20:32 +1000), the version in force when every one of these directories
  was committed (``2e8cc6481``, ``09fe46a7f``, ``c3e8e0701``, all 2026-04-17).
  It reads ``sorted(glob("run_*"))``: name order, run_1, run_10, run_2 … .
* ``current`` — the branch's ``scripts/merge_passes.py`` (numeric order since
  ``75d7c8d4c``, 2026-09-13). For first-5 sub-pools both orders coincide.

Comparison, per threshold file ``consensus_t<t>.geojson``: the rebuilt and
committed files' parsed JSON must be identical (every feature's coordinates
and properties, in order), and the rebuilt ``voting_summary.json`` must
agree on ``total_passes`` and every threshold count. That is EXACT. Anything
else is reported with its size: feature counts, features identical as a
multiset, and the largest nearest-neighbour offset (metres, EPSG:32635).

Validation: the same procedure on the K = 1 and K = 3 pools (``consensus-n1``,
``consensus-n3``, written 2026-09-12 with pass provenance) must reproduce
them and name the passes their ``voting_summary.json`` records.

Outputs: ``--out`` (JSON, one row per pool and merger, plus the declaration
entries for every EXACT pool), and the rebuilt directories under
``--scratch`` (large; kept on sapphire).

Usage (sapphire)::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python rebuild_pools.py \
        --code ~/worktrees/map-reader-llm/claude-d51-ladder-provenance \
        --scratch ~/scratch/d51-ladder-provenance-2026-10-08/rebuilds \
        --out out/rebuild_pools.json --workers 20

Created: 2026-10-08 (D57 (3), Session 163 follow-up)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

APRIL_COMMIT = "362f1a305"
OPERATING_POINTS = "results/k-ladder-2026-09-12/phase2/operating-points.json"
MEMBERSHIP = "results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/membership.json"
#: The thirteen pv-diag-384 ladders (the 3.7 GS ladder's pools are declared already).
POOLS = [
    "flash-minimal-text-n30-t07-text-t0.3", "flash-minimal-text-n30-t07-text-t0.7",
    "flash-minimal-text-n30-t07-text-t1.0", "flash-high-text-n5-text-t0.3",
    "flash-high-text-n5-text-t0.7", "flash-high-text-n5-text-t1.0",
    "image-n5-image-t0.3", "image-n5-image-t0.7", "image-n5-image-t1.0",
    "flash-high-image-n5-image-t0.3", "flash-high-image-n5-image-t0.7",
    "flash-high-image-n5-image-t1.0", "scale-4-optimal-487",
]


def blob(path: Path) -> str:
    """Git blob hash of a file (identical to ``git hash-object``)."""
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_merger(code: Path, which: str, scratch: Path) -> Any:
    """Import a merge_passes module: the branch's, or the April one from git."""
    if which == "current":
        path = code / "scripts" / "merge_passes.py"
    else:
        path = scratch / f"merge_passes_{APRIL_COMMIT}.py"
        if not path.exists():
            source = subprocess.run(
                ["git", "-C", str(code), "show", f"{APRIL_COMMIT}:scripts/merge_passes.py"],
                check=True, capture_output=True, text=True).stdout
            path.write_text(source)
    spec = importlib.util.spec_from_file_location(f"merge_passes_{which}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def jobs(code: Path) -> list[dict[str, Any]]:
    """Every pool to rebuild: K = 5 / 10 (targets) and K = 1 / 3 (validation)."""
    members = json.loads((code / MEMBERSHIP).read_text())["members"]
    points = json.loads((code / OPERATING_POINTS).read_text())["rungs"]
    out = []
    for pool in POOLS:
        for k in (5, 10):
            member = next(
                m for m in members
                if m["proposer_pool"] == pool and m["k"] == k
                and (m.get("verifier_config") or {}).get("variant") == "v1"
                and (m.get("verifier_config") or {}).get("instruction_file")
                == "verify_adversarial.md")
            out.append({"pool": pool, "K": k, "role": "target",
                        "union": member["vintage"]["union"]})
        for k in (1, 3):
            rung = next(r for r in points if r["pool_slug"] == pool and r["n_passes"] == k)
            out.append({"pool": pool, "K": k, "role": "validation", "union": rung["union"]})
    return out


def presumed_filter(code: Path, union: str, k: int) -> tuple[Path, list[int] | None, str]:
    """The cell and pass filter a consensus directory's name and rung declare."""
    cons = (code / union).parent
    cell = cons.parent
    if cons.name == f"consensus-n{k}":
        return cell, list(range(1, k + 1)), f"--passes {','.join(map(str, range(1, k + 1)))}"
    if cons.name == "consensus":
        runs = sorted(p.name for p in cell.glob("run_*") if p.is_dir())
        if len(runs) != k:
            raise SystemExit(f"{cons}: {len(runs)} run directories, expected {k}")
        return cell, None, "no --passes (every run_* of the cell)"
    raise SystemExit(f"{cons}: unrecognised consensus directory for K = {k}")


def _utm(xy: list[float]) -> tuple[float, float]:
    """WGS84 lon/lat to EPSG:32635 metres (for offsets only)."""
    from pyproj import Transformer  # noqa: PLC0415

    t = _utm.transformer = getattr(_utm, "transformer", None) or Transformer.from_crs(
        "EPSG:4326", "EPSG:32635", always_xy=True)
    return t.transform(xy[0], xy[1])


def compare_file(committed: Path, rebuilt: Path) -> dict[str, Any]:
    """Compare two consensus GeoJSONs: identical, else how far apart."""
    a = json.loads(committed.read_text())
    b = json.loads(rebuilt.read_text())
    row: dict[str, Any] = {
        "file": committed.name,
        "bytes_identical": committed.read_bytes() == rebuilt.read_bytes(),
        "json_identical": a == b,
        "n_committed": len(a.get("features", [])), "n_rebuilt": len(b.get("features", [])),
    }
    if row["json_identical"]:
        return row
    key = lambda f: json.dumps(f, sort_keys=True)  # noqa: E731
    ka = sorted(key(f) for f in a.get("features", []))
    kb = sorted(key(f) for f in b.get("features", []))
    row["features_identical_as_multiset"] = ka == kb
    row["top_level_keys"] = [sorted(a.keys()), sorted(b.keys())]
    # Largest nearest-neighbour offset, both ways (metres).
    from scipy.spatial import cKDTree  # noqa: PLC0415

    pa = [_utm(f["geometry"]["coordinates"]) for f in a.get("features", [])]
    pb = [_utm(f["geometry"]["coordinates"]) for f in b.get("features", [])]
    if pa and pb:
        da, _ = cKDTree(pb).query(pa)
        db, _ = cKDTree(pa).query(pb)
        row["max_nn_offset_m"] = round(float(max(da.max(), db.max())), 3)
        row["unmatched_at_1m"] = [int((da > 1).sum()), int((db > 1).sum())]
    return row


def run_job(args: tuple[str, str, dict[str, Any], str]) -> dict[str, Any]:
    """Rebuild one pool with one merger and compare it with the committed one."""
    code_s, scratch_s, job, which = args
    code, scratch = Path(code_s), Path(scratch_s)
    module = load_merger(code, which, scratch)
    cell, pass_filter, how = presumed_filter(code, job["union"], job["K"])
    committed_dir = (code / job["union"]).parent
    out_dir = scratch / which / committed_dir.relative_to(code)
    out_dir.mkdir(parents=True, exist_ok=True)
    module.threshold_sweep(cell, out_dir, pass_filter=pass_filter)
    # Which files the merger read, in the order it read them.
    if hasattr(module, "resolve_pass_files"):
        read = [str(p.relative_to(code)) for files in
                module.resolve_pass_files(cell, pass_filter).values() for p in files]
    else:  # April merger: sorted(glob) of run_*, filtered, one file per run here
        read = []
        for d in sorted(cell.glob("run_*")):
            num = int(d.name.replace("run_", ""))
            if pass_filter and num not in pass_filter:
                continue
            read += [str(p.relative_to(code)) for p in d.glob("*.geojson")
                     if ".meta" not in p.name]
    files = sorted(p.name for p in committed_dir.glob("consensus_t*.geojson"))
    rebuilt = sorted(p.name for p in out_dir.glob("consensus_t*.geojson"))
    rows = [compare_file(committed_dir / f, out_dir / f) for f in files if f in rebuilt]
    s_c = json.loads((committed_dir / "voting_summary.json").read_text())
    s_r = json.loads((out_dir / "voting_summary.json").read_text())
    summary_agrees = (s_c.get("total_passes") == s_r.get("total_passes")
                      and {str(k): v for k, v in s_c["thresholds"].items()}
                      == {str(k): v for k, v in s_r["thresholds"].items()})
    exact = (files == rebuilt and summary_agrees and all(r["json_identical"] for r in rows))
    result = {
        **job, "merger": which, "cell": str(cell.relative_to(code)), "presumed": how,
        "read_order": read, "files_committed": files, "files_rebuilt": rebuilt,
        "summary_committed": {"total_passes": s_c.get("total_passes"),
                              "thresholds": s_c.get("thresholds")},
        "summary_agrees": summary_agrees, "exact": exact,
        "n_files_json_identical": sum(r["json_identical"] for r in rows),
        "n_files_bytes_identical": sum(r["bytes_identical"] for r in rows),
        "differences": [r for r in rows if not r["json_identical"]],
        "rebuilt_dir": str(out_dir),
    }
    if "pass_provenance" in s_c:
        recorded = sorted((e["path"], e["git_blob_hash"]) for e in s_c["pass_provenance"])
        result["recorded_provenance_agrees"] = recorded == sorted(
            (p, blob(code / p)) for p in read)
    print(job["pool"], job["K"], which, "EXACT" if exact else "DIFFERS", flush=True)
    return result


def declaration(code: Path, row: dict[str, Any], others: list[dict[str, Any]]) -> dict:
    """The pool declaration an EXACT rebuild supports."""
    entries = sorted(({"pass_id": Path(p).parent.name, "path": p,
                       "git_blob_hash": blob(code / p)} for p in row["read_order"]),
                     key=lambda e: (e["pass_id"], e["path"]))
    verdicts = {o["merger"]: ("EXACT" if o["exact"] else "differs") for o in others}
    commit = subprocess.run(
        ["git", "-C", str(code), "log", "--format=%h %ad", "--date=short", "--",
         str(Path(row["union"]).parent)], check=True, capture_output=True,
        text=True).stdout.split("\n")[0]
    return {
        "schema": "assessed-area/1",
        "pool": row["union"],
        "status": "declared-retrospectively",
        "declared": "2026-10-08 (PI ruling D57 (3))",
        "builder": f"scripts/merge_passes.py --input-dir {row['cell']} --output-dir "
                   f"{Path(row['union']).parent} --sweep, {row['presumed']}",
        "pass_provenance": entries,
        "clip": None,
        "evidence": [
            f"committed in {commit}; its voting_summary.json records total_passes "
            f"{row['summary_committed']['total_passes']} and the threshold counts only",
            f"rebuild: merge_passes.py at {APRIL_COMMIT} (the version in force on "
            f"2026-04-17, name order) from exactly these files reproduces all "
            f"{len(row['files_committed'])} consensus_t*.geojson of the directory "
            + ("byte for byte" if row["n_files_bytes_identical"] == len(row["files_committed"])
               else "feature for feature (parsed JSON identical)")
            + " and every threshold count in its voting_summary.json",
            f"merger verdicts: {json.dumps(verdicts, sort_keys=True)} (numeric order "
            f"since 75d7c8d4c)",
            "reports/d51-ladder-provenance-2026-10-08-scripts/rebuild_pools.py; "
            "out/rebuild_pools.json",
        ],
    }


def main() -> int:
    """Rebuild every pool under both mergers, in parallel, and summarise."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    code = args.code.expanduser().resolve()
    scratch = args.scratch.expanduser().resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    load_merger(code, "april", scratch)  # extract once before the workers start
    work = [(str(code), str(scratch), job, which)
            for job in jobs(code) for which in ("april", "current")]
    # Largest pools first so the slowest jobs start early.
    work.sort(key=lambda w: -w[2]["K"])
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(run_job, work))
    by_pool: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in rows:
        by_pool.setdefault((row["pool"], row["K"]), []).append(row)
    declarations = []
    for (pool_name, k), pair in sorted(by_pool.items()):
        april = next(r for r in pair if r["merger"] == "april")
        if april["role"] == "target" and april["exact"]:
            declarations.append(declaration(code, april, pair))
    table = [{"pool": p, "K": k, "role": pair[0]["role"],
              **{r["merger"]: r["exact"] for r in pair},
              "recorded_provenance_agrees": pair[0].get("recorded_provenance_agrees")}
             for (p, k), pair in sorted(by_pool.items())]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"table": table, "declarations": declarations,
                                    "rows": rows}, indent=1) + "\n")
    print(json.dumps(table, indent=0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
