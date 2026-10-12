#!/usr/bin/env python3
"""
Floors v2: second, independent computation of the regenerated § 6 and § 6b cells.
=================================================================================

Sapphire has no error-correcting (ECC) memory, so a flipped bit in a statistic
would pass silently. After the 2026-10-12 regeneration (PI ruling D60 (4)) the
main session asked for a second, independent run, compared byte for byte with
the first:

* **§ 6, every cell**: ``w27_55map_subset_replicates.py`` is run a second time
  into another directory with a FRESH deduplicated-pass cache (``W27_CACHE``),
  in a new process. ``--w27-first`` and ``--w27-second`` name the two output
  directories; every file both hold is compared byte for byte (``.npz``
  archives member by member, since a zip's directory records write times).
* **§ 6b, a seeded random 10 %**: ``--fraction`` of the rows of the first run's
  ``subset_cells_all.csv`` (default 0.10), drawn without replacement with
  ``numpy.random.default_rng(--seed)`` (default 20261013), are recomputed here
  from the raw passes (fresh cache, new process: re-deduplicated, re-clustered,
  re-inherited, re-attributed by the library, re-scored) and each recomputed
  row, written by the same ``csv.DictWriter`` call, must equal the first run's
  line byte for byte.

A mismatch is reported cell by cell and fails the run (exit 1); the caller
recomputes those cells a third time as a tie-break and publishes none of them
until it is resolved.

Zero API. Run on sapphire (``REPO`` = this checkout; ``W27_CACHE`` = a new,
empty directory):
    REPO=<clone> W27_CACHE=<fresh dir> .venv/bin/python floors2_integrity_recheck.py \
        --workers 5 --cells-csv <run 1>/subset_cells_all.csv \
        --w27-first <w27 run 1> --w27-second <w27 run 2> --out <dir>

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-12 | Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import time
import zipfile
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np

REPO = Path(os.environ.get("REPO", str(Path.home() / "Code/map-reader-llm")))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "reports/w27-replicate-floors-2026-10-06-scripts"))
import w27_55map_subset_replicates as w27  # noqa: E402  (inserts REPO, REPO/scripts)

import floors2_55map as f2  # noqa: E402
import floors2_lib as L  # noqa: E402
from scripts.build_55map_leaderboard import BOUNDS, reference_gt  # noqa: E402

#: The fields of ``subset_cells_all.csv``, in ``floors2_55map.py``'s order.
FIELDS = ["family", "K", "prob_t", "k", "n_det", "tp", "fp", "fn", "f1", "subset"]


def compare_dirs(first: Path, second: Path) -> dict:
    """Compare every file two § 6 output directories both hold, byte for byte.

    Args:
        first: The first run's ``--out``.
        second: The second run's ``--out``.

    Returns:
        ``{"files": {name: verdict}, "only_in_one": [...], "pass": bool}``; an
        ``.npz`` is compared member by member (array bytes), its zip directory's
        write times being the one thing ignored.
    """
    a = {p.name for p in first.iterdir() if p.is_file()}
    b = {p.name for p in second.iterdir() if p.is_file()}
    out: dict = {"files": {}, "only_in_one": sorted(a ^ b)}
    for name in sorted(a & b):
        fa, fb = first / name, second / name
        if name.endswith(".npz"):
            with zipfile.ZipFile(fa) as za, zipfile.ZipFile(fb) as zb:
                na, nb = sorted(za.namelist()), sorted(zb.namelist())
                same = na == nb and all(za.read(m) == zb.read(m) for m in na)
            out["files"][name] = "identical members" if same else "DIFFERENT"
        else:
            same = fa.read_bytes() == fb.read_bytes()
            out["files"][name] = "identical bytes" if same else "DIFFERENT"
    out["pass"] = not out["only_in_one"] and all(
        not v.startswith("DIFF") for v in out["files"].values()
    )
    return out


def _job(job):
    """Recompute the listed cells of one (family, subset) frame from the raw passes."""
    (fam, s), wanted = job
    spec = f2._G["fam"][fam]
    gdf = w27.cluster_subset(spec["passes"], s, f2._G["index"])
    fa = f2.frame_arrays(w27.inherit(gdf, spec["union"]))
    out = []
    for p, k in wanted:
        m = (fa["prob"] >= p) & (fa["votes"] >= k)
        tp, fp, fn = f2._G["scorer"].totals(fa["prep"], m)
        out.append({
            "family": fam, "K": len(s), "prob_t": p, "k": k, "n_det": int(m.sum()),
            "tp": tp, "fp": fp, "fn": fn, "f1": L.f1_of(tp, fp, fn),
            "subset": "-".join(map(str, s)),
        })
    return out


def line_of(rec: dict) -> str:
    """The CSV line ``floors2_55map.py``'s DictWriter writes for one record."""
    buf = io.StringIO()
    csv.DictWriter(buf, fieldnames=FIELDS).writerow(rec)
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--cells-csv", type=Path, required=True)
    ap.add_argument("--fraction", type=float, default=0.10)
    ap.add_argument("--seed", type=int, default=20261013)
    ap.add_argument("--w27-first", type=Path, default=None)
    ap.add_argument("--w27-second", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    res: dict = {"w27_cache": str(w27.CACHE), "cache_was_empty": not any(w27.CACHE.glob("*"))}

    if args.w27_first and args.w27_second:
        res["sec6_second_run"] = compare_dirs(args.w27_first, args.w27_second)
        print(f"§ 6 second run: {res['sec6_second_run']}", flush=True)

    # The first run's lines, read as text: the comparison is byte for byte.
    raw = args.cells_csv.read_bytes().decode()
    lines = raw.splitlines(keepends=True)
    header, body = lines[0], lines[1:]
    if header != line_of({f: f for f in FIELDS}):
        print(f"header differs from floors2_55map.py's: {header!r}", flush=True)
        return 1
    rows = list(csv.DictReader(io.StringIO(raw)))
    n_pick = int(round(args.fraction * len(rows)))
    pick = sorted(np.random.default_rng(args.seed).choice(len(rows), n_pick, replace=False))
    wanted: dict[tuple, list] = {}
    for i in pick:
        r = rows[i]
        key = (r["family"], tuple(int(x) for x in r["subset"].split("-")))
        wanted.setdefault(key, []).append((float(r["prob_t"]), int(r["k"]), int(i)))

    fam = w27.build_families(gate_only=False)
    w27.cluster_votes = L.cluster_votes_fast  # gated equal in floors2_55map.py gate 1
    ref = reference_gt("r2")
    bounds = gpd.read_file(BOUNDS)
    bounds = (bounds.set_crs("EPSG:4326") if bounds.crs is None else bounds).to_crs("EPSG:32635")
    f2._G.update(
        scorer=L.FastScorer(ref, bounds, w27.BUFFER_M),
        index=next(iter(fam.values()))["index"],
        fam=fam,
    )
    jobs = [(key, [(p, k) for p, k, _ in v]) for key, v in wanted.items()]
    with Pool(args.workers) as pool:
        got = pool.map(_job, jobs, chunksize=1)
    bad = []
    for (key, v), recs in zip(wanted.items(), got):
        for (_p, _k, i), rec in zip(v, recs):
            new_line = line_of(rec)
            if new_line != body[i]:
                bad.append({"row": i, "first": body[i].rstrip(), "second": new_line.rstrip()})
    res["sec6b_sample"] = {
        "population": f"rows of {args.cells_csv.name}",
        "population_size": len(rows),
        "fraction": args.fraction,
        "n": n_pick,
        "seed": args.seed,
        "rng": "numpy.random.default_rng(seed).choice(population_size, n, replace=False)",
        "frames_rebuilt": len(jobs),
        "comparison": "the recomputed row's CSV line against the first run's, byte for byte",
        "mismatches": bad,
        "pass": not bad,
    }
    res["pass"] = bool(res["sec6b_sample"]["pass"]) and bool(
        res.get("sec6_second_run", {"pass": True})["pass"]
    )
    res["wall_seconds"] = round(time.time() - t0)
    (args.out / "integrity_recheck.json").write_text(json.dumps(res, indent=1) + "\n")
    print(
        f"§ 6b sample: {n_pick} rows (seed {args.seed}), {len(jobs)} frames, "
        f"{len(bad)} mismatches; overall pass {res['pass']}; {res['wall_seconds']}s",
        flush=True,
    )
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
