"""Summarise the evaluation re-scoring: reproduction gate, blast-radius counts, moved cells.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only; reads the JSON lines
written by ``rescore_evaluations.py`` plus the registers in the checkout, writes CSV and JSON
summaries to ``--outdir``.

Outputs:

* ``cells.csv`` — one row per committed evaluation: family, scorer, register links,
  detection counts (out-of-frame, null ``source_tile``), committed / OFF / ON values at
  20 m and 50 m, MCC, and the reproduction verdict.
* ``moved.csv`` — every cell where ON differs from OFF by at least 0.001 in any metric at
  any scored buffer, with the per-metric deltas.
* ``summary.json`` — headline counts, gate (i) results by family, status counts.

Usage::

    python summarise_evaluations.py --repo ~/Code/map-reader-llm \
        --rows out/evaluations.jsonl out/evaluations_rerun.jsonl --outdir out/summary
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

#: Tolerance for gate (i): committed values are stored at four decimals.
TOL = 1e-4
METRICS = ("f1", "precision", "recall")


def load_registers(repo: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Map evaluation path -> condition ids, and condition id -> analysis ids."""
    cm = json.loads((repo / "results/conditions-manifest.json").read_text())
    by_eval: dict[str, list[str]] = defaultdict(list)
    for c in cm["conditions"]:
        for s in c["provenance"]["source_files"]:
            by_eval[s].append(c["condition_id"])
    ra = json.loads((repo / "results/run-analyses.json").read_text())
    by_cond: dict[str, list[str]] = defaultdict(list)
    for a in ra["analyses"]:
        for cid in a.get("conditions_compared") or []:
            by_cond[cid].append(a["analysis_id"])
    return by_eval, by_cond


def close(a: Any, b: Any) -> bool | None:
    """True when two metric values agree to :data:`TOL` (None when either is missing)."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return None
    return abs(round(float(a), 4) - float(b)) <= TOL + 1e-12


def reproduce(row: dict[str, Any]) -> tuple[bool | None, list[str]]:
    """Gate (i) for one scored row: does OFF reproduce every committed value it scored?"""
    notes: list[str] = []
    verdicts: list[bool] = []
    off = row.get("off") or {}
    for b, vals in (off.get("per_buffer") or {}).items():
        com = row["committed"].get(b)
        if not com:
            continue
        for m in METRICS:
            v = close(vals[m], com.get(m))
            if v is None:
                continue
            verdicts.append(v)
            if not v:
                notes.append(f"{m}@{b}: committed {com.get(m)} off {vals[m]:.4f}")
    cm = row.get("committed_mcc")
    if isinstance(cm, (int, float)):
        if off.get("mcc") is None:
            verdicts.append(False)
            notes.append(f"mcc: committed {cm} off None ({off.get('mcc_refused')})")
        else:
            v = bool(close(off["mcc"], cm))
            verdicts.append(v)
            if not v:
                notes.append(f"mcc: committed {cm} off {off['mcc']:.4f}")
    elif cm == "withheld":
        v = off.get("mcc") is None and off.get("mcc_refused") is not None
        verdicts.append(v)
        if not v:
            notes.append(f"mcc: committed withheld, off {off.get('mcc')}")
    if not verdicts:
        return None, notes
    return all(verdicts), notes


def deltas(row: dict[str, Any]) -> dict[str, float]:
    """ON minus OFF for every scored metric and buffer, plus MCC."""
    out: dict[str, float] = {}
    off, on = row.get("off") or {}, row.get("on") or {}
    for b, vals in (off.get("per_buffer") or {}).items():
        onv = (on.get("per_buffer") or {}).get(b)
        if not onv:
            continue
        for m in METRICS:
            out[f"{m}@{b}"] = onv[m] - vals[m]
    if isinstance(off.get("mcc"), (int, float)) and isinstance(on.get("mcc"), (int, float)):
        out["mcc"] = on["mcc"] - off["mcc"]
    return out


def fmt(v: Any) -> str:
    """Four-decimal string for numbers, empty for missing values."""
    return f"{v:.4f}" if isinstance(v, (int, float)) else ("" if v is None else str(v))


def main() -> int:
    """Read rows, compute the gate and blast-radius tables, and write the summaries."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rows", type=Path, nargs="+", required=True,
                    help="JSON-lines files; a later file's row replaces an earlier one's")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    by_eval, by_cond = load_registers(repo)
    merged: dict[str, dict[str, Any]] = {}
    for path in args.rows:
        for line in path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                merged[row["eval"]] = row
    rows = list(merged.values())
    args.outdir.mkdir(parents=True, exist_ok=True)

    status = Counter(r.get("status") for r in rows)
    fam_gate: dict[str, Counter] = defaultdict(Counter)
    fam_drop: dict[str, Counter] = defaultdict(Counter)
    cells_out = []
    moved_out = []
    for r in rows:
        fam = r.get("family", "?")
        conds = by_eval.get(r["eval"], [])
        analyses = sorted({a for c in conds for a in by_cond.get(c, [])})
        rep, notes = (reproduce(r) if r.get("status") == "scored" else (None, []))
        if r.get("status") == "scored":
            fam_gate[fam]["scored"] += 1
            fam_gate[fam]["reproduced" if rep else ("not-reproduced" if rep is False
                                                  else "no-committed-values")] += 1
        if "n_out_of_frame" in r:
            fam_drop[fam]["cells_with_diagnostics"] += 1
            if r["n_out_of_frame"] > 0:
                fam_drop[fam]["cells_with_out_of_frame"] += 1
            if r.get("n_null_source_tile", 0) > 0:
                fam_drop[fam]["cells_with_null_source_tile"] += 1
            if r.get("n_null_in_frame", 0) > 0:
                fam_drop[fam]["cells_with_null_in_frame"] += 1
        d = deltas(r) if r.get("status") == "scored" else {}
        max_abs = max((abs(v) for v in d.values()), default=0.0)
        off20 = ((r.get("off") or {}).get("per_buffer") or {}).get("20") or {}
        on20 = ((r.get("on") or {}).get("per_buffer") or {}).get("20") or {}
        off50 = ((r.get("off") or {}).get("per_buffer") or {}).get("50") or {}
        on50 = ((r.get("on") or {}).get("per_buffer") or {}).get("50") or {}
        com20 = r.get("committed", {}).get("20") or {}
        cell = {
            "eval": r["eval"], "family": fam, "status": r.get("status"),
            "script": r.get("script"), "conditions": ";".join(conds),
            "analyses": ";".join(analyses),
            "detections": ";".join(r.get("detections") or []),
            "bounds": r.get("bounds"), "ground_truth": r.get("ground_truth"),
            "n_detections": ";".join(str(x) for x in r.get("n_detections_loaded") or []),
            "n_out_of_frame": r.get("n_out_of_frame"),
            "n_null_source_tile": r.get("n_null_source_tile"),
            "n_null_in_frame": r.get("n_null_in_frame"),
            "n_unprefixed_in_frame": r.get("n_unprefixed_in_frame"),
            "committed_f1_20": com20.get("f1"), "off_f1_20": fmt(off20.get("f1")),
            "on_f1_20": fmt(on20.get("f1")),
            "off_p_20": fmt(off20.get("precision")), "on_p_20": fmt(on20.get("precision")),
            "off_r_20": fmt(off20.get("recall")), "on_r_20": fmt(on20.get("recall")),
            "off_f1_50": fmt(off50.get("f1")), "on_f1_50": fmt(on50.get("f1")),
            "committed_mcc": r.get("committed_mcc"),
            "off_mcc": fmt((r.get("off") or {}).get("mcc")),
            "on_mcc": fmt((r.get("on") or {}).get("mcc")),
            "max_abs_delta": fmt(max_abs),
            "reproduced": rep, "repro_notes": " | ".join(notes),
            "error": r.get("error") or ";".join(r.get("missing") or []),
        }
        cells_out.append(cell)
        if max_abs >= 0.001:
            moved_out.append({**{k: cell[k] for k in (
                "eval", "family", "conditions", "analyses", "n_detections", "n_out_of_frame",
                "committed_f1_20", "off_f1_20", "on_f1_20", "off_p_20", "on_p_20",
                "off_r_20", "on_r_20", "off_f1_50", "on_f1_50", "committed_mcc", "off_mcc",
                "on_mcc", "reproduced")},
                "d_f1_20": fmt(d.get("f1@20")), "d_p_20": fmt(d.get("precision@20")),
                "d_r_20": fmt(d.get("recall@20")), "d_f1_50": fmt(d.get("f1@50")),
                "d_mcc": fmt(d.get("mcc")), "max_abs_delta": fmt(max_abs),
                "max_metric": max(d, key=lambda k: abs(d[k])) if d else ""})

    for name, data in (("cells.csv", cells_out), ("moved.csv", moved_out)):
        with (args.outdir / name).open("w", newline="") as fh:
            if data:
                w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
                w.writeheader()
                w.writerows(data)

    scored = [c for c in cells_out if c["status"] == "scored"]
    thresholds = {t: sum(1 for c in scored if float(c["max_abs_delta"] or 0) >= t)
                  for t in (0.001, 0.005, 0.01)}
    summary = {
        "n_evaluations": len(rows),
        "status": dict(status),
        "n_scored": len(scored),
        "n_with_diagnostics": sum(1 for r in rows if "n_out_of_frame" in r),
        "n_cells_any_out_of_frame": sum(1 for r in rows if r.get("n_out_of_frame", 0) > 0),
        "n_cells_any_null_source_tile": sum(
            1 for r in rows if r.get("n_null_source_tile", 0) > 0),
        "n_cells_null_in_frame": sum(1 for r in rows if r.get("n_null_in_frame", 0) > 0),
        "n_moved_ge": {str(k): v for k, v in thresholds.items()},
        "gate_i_by_family": {k: dict(v) for k, v in sorted(fam_gate.items())},
        "drops_by_family": {k: dict(v) for k, v in sorted(fam_drop.items())},
    }
    (args.outdir / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
