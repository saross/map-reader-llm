#!/usr/bin/env python3
"""
Per-tile tables of the diversity arms whose attribution the fix changes.

D62 (1) workstream ``origin-gap-h13-copies`` (2026-10-13), step 2. For the
``analyse_diversity`` arms that ``measure_copies.py`` found with a changed
scope (some rows matched on another sheet), this rebuilds each arm and
compares the shared library's per-tile TP/FP/FN table
(``compute_per_tile_tp_fp_fn``, which ``bootstrap_ci`` resamples) with and
without the ``source_tiles`` column. Equal tables and equal totals mean the
committed point estimates, intervals, and replicate permutation tests built
from that arm cannot move.

Usage::

    python pertile_diversity.py --code <tree> --data <clone>
        --summary <copies-summary.json> --out <json>

Author: Claude Code (Opus 5.5) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import geopandas as gpd


def table_sig(tm) -> tuple[str, list[int]]:
    """A hash of a per-tile table and its TP/FP/FN totals.

    Args:
        tm: DataFrame with ``tile_name``, ``tp``, ``fp``, ``fn``.

    Returns:
        ``(sha256 prefix, [tp, fp, fn])``.
    """
    rows = sorted((str(r.tile_name), int(r.tp), int(r.fp), int(r.fn)) for r in tm.itertuples())
    sig = hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:16]
    return sig, [sum(r[i] for r in rows) for i in (1, 2, 3)]


def main() -> int:
    """Compare the tables for every moved arm.

    Returns:
        Process exit status (0 on success).
    """
    ap = argparse.ArgumentParser(description="Per-tile tables of moved diversity arms.")
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    code = args.code.resolve()
    sys.path.insert(0, str(code))
    sys.path.insert(0, str(code / "scripts"))
    import analyse_diversity as ad  # noqa: E402
    import lib_advanced_metrics as lam  # noqa: E402

    assert Path(ad.__file__).resolve().is_relative_to(code)
    summary = json.loads(args.summary.read_text())
    out: dict = {}
    for track, section in (("track1-image", "diversity-track1"),
                           ("track2-text", "diversity-track2")):
        moved = [m["arm"] for m in summary[section]["moved"]]
        meta = json.loads((args.data / "results/phase3c-diversity" / track
                           / "diversity-analysis-report.json").read_text())["metadata"]
        design = ad.extract_consensus_design(ad.load_study_yaml(args.data / meta["study_yaml"]))
        ref = gpd.read_file(args.data / meta["ground_truth"]).to_crs(ad.TARGET_CRS)
        bounds = gpd.read_file(args.data / meta["bounds"]).to_crs(ad.TARGET_CRS)
        by_rep: dict = {}
        for key in moved:
            label, rep, t = key.split("|")
            by_rep.setdefault((label, int(rep[3:])), []).append(int(t[1:]))
        for (label, rep), thresholds in sorted(by_rep.items()):
            passes = ad.load_replication_passes(args.data / meta["study_dir"], design[label], rep)
            clusters = ad.cluster_across_passes(passes)
            for x in thresholds:
                gdf = ad.consensus_to_gdf(ad.apply_threshold(clusters, x, len(design[label])),
                                          bounds)
                with_list = table_sig(lam.compute_per_tile_tp_fp_fn(
                    gdf, ref, bounds, buffer_metres=meta["buffer_metres"]))
                without = table_sig(lam.compute_per_tile_tp_fp_fn(
                    gdf.drop(columns="source_tiles"), ref, bounds,
                    buffer_metres=meta["buffer_metres"]))
                out[f"{track}|{label}|rep{rep}|t{x}"] = {
                    "with_list": with_list, "without": without,
                    "table_equal": with_list == without,
                }
                print(track, label, rep, x, with_list == without, flush=True)
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True))
    print("ALL EQUAL", all(v["table_equal"] for v in out.values()), len(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
