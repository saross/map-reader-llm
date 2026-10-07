"""Carry the moved cells into the committed analyses that consume them.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only; reads the re-score rows
and committed artefacts, writes one JSON record.

Three consumers are recomputed, each from its own committed table with only the moved
cells' values replaced by their geometrically scoped (ON) values:

1. The Gemini 3.7 gold-standard (GS) K-ladder (``results/k-ladder-2026-09-12/phase2/
   ladders.json``): F1@20 per rung, the K = 1 -> K = 10 gain, and the best rung.
2. The null-exemplar sensitivity (``results/null-exemplar-sensitivity-2026-09-13/
   analysis.json`` ``per_cell``): the Era-2 board's per-group F1@20 change distribution,
   with each moved cell's before and after both taken ON.
3. The verifier-uplift supplement (``results/uplift-supplement/verifier-uplift.csv`` and
   ``-mcc.csv``): every pair whose unverified (or verified) side is a moved evaluation.

Usage::

    python downstream.py --repo ~/Code/map-reader-llm \
        --rows out/evaluations.jsonl out/evaluations_rerun.jsonl out/evaluations_nx.jsonl \
        --out out/downstream.json
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path
from typing import Any

NX_CELLS = "results/null-exemplar-sensitivity-2026-09-13/cells"


def load_rows(paths: list[Path]) -> dict[str, dict[str, Any]]:
    """Merge re-score rows by evaluation path (later files win)."""
    rows: dict[str, dict[str, Any]] = {}
    for p in paths:
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                rows[r["eval"]] = r
    return rows


def metric(row: dict[str, Any], side: str, buffer_m: int, name: str) -> float | None:
    """One metric from a row's OFF or ON block (``mcc`` is buffer-free)."""
    block = row.get(side) or {}
    if name == "mcc":
        return block.get("mcc")
    vals = (block.get("per_buffer") or {}).get(str(buffer_m)) or {}
    return vals.get(name)


def ladder(repo: Path, rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The 3.7 GS ladder, committed and ON."""
    data = json.loads((repo / "results/k-ladder-2026-09-12/phase2/ladders.json").read_text())
    lad = next(x for x in data["ladders"] if x["run_id"] == "gemini37-screen-2026-08-28")
    rungs = []
    for rg in lad["rungs"]:
        ev = rg["opmax"]["eval_path"]
        row = rows.get(ev, {})
        rungs.append({
            "K": rg["K"], "eval_path": ev, "ladder_f1_20": rg["opmax"]["f1_20"],
            "off_f1_20": metric(row, "off", 20, "f1"), "on_f1_20": metric(row, "on", 20, "f1"),
            "n_out_of_frame": row.get("n_out_of_frame"),
        })
    on = {r["K"]: r["on_f1_20"] for r in rungs}
    committed = {r["K"]: r["ladder_f1_20"] for r in rungs}
    best_on = max(on, key=lambda k: on[k])
    return {
        "family": lad["family"], "rungs": rungs,
        "committed_gain_k1_k10": committed[10] - committed[1],
        "on_gain_k1_k10": on[10] - on[1],
        "on_best_rung": best_on, "on_gain_k1_best": on[best_on] - on[1],
        "committed_best_rung": max(committed, key=lambda k: committed[k]),
    }


def null_exemplar(repo: Path, rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Era-2 board per-group F1@20 deltas with the moved cells' deltas taken ON."""
    data = json.loads(
        (repo / "results/null-exemplar-sensitivity-2026-09-13/analysis.json").read_text())
    board = next(b for b in data["per_cell"] if b["frame_id"] == "era2-b-487")
    # Map each moved full-frame cell to its reduced-frame twin by condition id.
    cm = json.loads((repo / "results/conditions-manifest.json").read_text())
    eval_of = {c["condition_id"]: c["provenance"]["source_files"][0]
               for c in cm["conditions"]}
    changed = []
    by_group: dict[str, list[float]] = {"image": [], "text": []}
    by_group_committed: dict[str, list[float]] = {"image": [], "text": []}
    for cell in board["cells"]:
        ref = cell["ref"]
        # The findings table's groups: image-bearing (exposed) cells vs text controls.
        group = "image" if cell.get("exposed") else "text"
        d = cell.get("delta_f1")
        if d is None:
            continue
        by_group_committed[group].append(d)
        full = rows.get(eval_of.get(ref, ""), {})
        slug = ref.replace("::", "__")
        reduced = rows.get(f"{NX_CELLS}/era2-b-487/{slug}/evaluation.json", {})
        if full.get("n_out_of_frame", 0) > 0 or reduced.get("n_out_of_frame", 0) > 0:
            before = metric(full, "on", 20, "f1")
            after = metric(reduced, "on", 20, "f1")
            if before is not None and after is not None:
                new = round(after, 4) - round(before, 4)
                changed.append({"ref": ref, "group": group, "committed_delta": d,
                                "on_before": before, "on_after": after,
                                "on_delta": new,
                                "oof_full": full.get("n_out_of_frame"),
                                "oof_reduced": reduced.get("n_out_of_frame")})
                d = new
        by_group[group].append(d)

    def stats(vals: list[float]) -> dict[str, Any]:
        """Distribution summary in the findings table's shape."""
        if not vals:
            return {}
        big = max(vals, key=abs)
        return {"n": len(vals), "mean": statistics.fmean(vals),
                "median": statistics.median(vals), "min": min(vals), "max": max(vals),
                "largest_absolute": big}

    return {"changed_cells": changed,
            "committed": {g: stats(v) for g, v in by_group_committed.items()},
            "on": {g: stats(v) for g, v in by_group.items()},
            "image_minus_text_mean_committed": (
                statistics.fmean(by_group_committed["image"])
                - statistics.fmean(by_group_committed["text"])),
            "image_minus_text_mean_on": (statistics.fmean(by_group["image"])
                                         - statistics.fmean(by_group["text"]))}


def uplift(repo: Path, rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Verifier-uplift pairs whose sides are moved evaluations."""
    moved = {k for k, r in rows.items() if r.get("n_out_of_frame", 0) > 0}
    out = []
    for name in ("verifier-uplift.csv", "verifier-uplift-mcc.csv"):
        path = repo / "results/uplift-supplement" / name
        for rec in csv.DictReader(path.open()):
            notes = rec["notes"]
            for side in ("unverified", "verified"):
                marker = f"{side} from "
                if marker not in notes:
                    continue
                src = notes.split(marker, 1)[1].split(",")[0].strip()
                if src not in moved:
                    continue
                b = int(rec["buffer_m"])
                m = "mcc" if rec["uplift_metric"] == "MCC" else "f1"
                row = rows[src]
                off_v, on_v = metric(row, "off", b, m), metric(row, "on", b, m)
                committed_side = float(rec[f"{side}_value"])
                delta_side = (on_v - off_v) if (on_v is not None and off_v is not None) else None
                new_uplift = None
                if delta_side is not None:
                    sign = -1 if side == "unverified" else 1
                    new_uplift = float(rec["uplift"]) + sign * delta_side
                out.append({"csv": name, "pair_id": rec["pair_id"], "side": side,
                            "source": src, "buffer_m": b, "metric": rec["uplift_metric"],
                            "committed_side_value": committed_side, "off": off_v, "on": on_v,
                            "committed_uplift": float(rec["uplift"]),
                            "on_uplift": new_uplift, "n_out_of_frame": row["n_out_of_frame"]})
    return out


def main() -> int:
    """Compute the three downstream recomputations and write them."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rows", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    rows = load_rows(args.rows)
    rec = {"ladder_37_gs": ladder(repo, rows), "null_exemplar_era2": null_exemplar(repo, rows),
           "verifier_uplift": uplift(repo, rows)}
    args.out.write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
