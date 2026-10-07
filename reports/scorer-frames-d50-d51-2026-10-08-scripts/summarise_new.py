"""Classify every re-scored cell against the blast radius's OFF and ON values.

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only; pure
post-processing of ``rescore_new.py``'s rows.

For every directly scored cell, at every buffer the blast radius scored and
for F1, precision and recall (plus tile MCC where committed), the NEW value is
compared with OFF (``main``'s scorer) and ON (the blast radius's geometric
wrapper). Each cell lands in one class:

* ``unchanged`` — NEW equals OFF (to 1e-9) and the scope rule did not fire;
* ``as-predicted`` — NEW equals ON and differs from OFF: the out-of-frame
  cells the frames report identified;
* ``origin-restored`` — NEW differs from ON because the D50 origin rule moved
  a re-keyed detection back to its own sheet (the wrapper did not do this);
* ``other`` — anything else (none expected; each is listed for inspection).

The register columns (conditions, analyses) come from the blast radius's
committed ``out/summary/cells.csv``. Writes ``summary_new.json`` and
``moved_new.csv`` (cells moving by at least 0.001 in any metric vs OFF).

Usage::

    python summarise_new.py --rows out/new_evaluations.jsonl \
        --cells BLAST/out/summary/cells.csv --outdir out/summary
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

METRICS = ("f1", "precision", "recall")
EPS = 1e-9


def max_abs_delta(a: dict[str, Any] | None, b: dict[str, Any] | None) -> float | None:
    """Largest |a − b| over buffers and metrics, plus MCC when both are defined."""
    if not a or not b:
        return None
    worst = 0.0
    for buf, vals in (a.get("per_buffer") or {}).items():
        other = (b.get("per_buffer") or {}).get(buf)
        if not other:
            continue
        for m in METRICS:
            worst = max(worst, abs(vals[m] - other[m]))
    if isinstance(a.get("mcc"), (int, float)) and isinstance(b.get("mcc"), (int, float)):
        worst = max(worst, abs(a["mcc"] - b["mcc"]))
    return worst


def mcc_state(block: dict[str, Any] | None) -> str:
    """'refused', a 4-decimal number, or '—'."""
    if not block:
        return "—"
    if block.get("mcc") is None:
        return "refused" if block.get("mcc_refused") else "—"
    return f"{block['mcc']:.4f}"


def headline(block: dict[str, Any] | None, buf: str) -> float | None:
    """F1 at one buffer, or None."""
    vals = ((block or {}).get("per_buffer") or {}).get(buf)
    return None if vals is None else vals["f1"]


def main() -> int:
    """Classify, summarise and write the moved-cells table."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--cells", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    register = {r["eval"]: r for r in csv.DictReader(args.cells.open())}
    rows = [json.loads(line) for line in args.rows.read_text().splitlines() if line.strip()]
    classes: Counter[str] = Counter()
    fired: Counter[str] = Counter()
    moved: list[dict[str, Any]] = []
    other: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for row in rows:
        scope = row.get("new_scope") or {}
        for k in ("n_out_of_frame", "n_out_of_frame_cross_sheet", "n_origin_restored",
                  "n_origin_only", "n_origin_unrecognised", "n_unattributed_in_frame"):
            if scope.get(k):
                fired[k] += 1
        if row.get("new_status") == "error":
            errors.append({"eval": row["eval"], "error": row.get("error")})
            continue
        if row.get("new_status") != "scored":
            classes[f"not scored ({row.get('new_status')})"] += 1
            continue
        d_off = max_abs_delta(row["new"], row["blast_off"])
        d_on = max_abs_delta(row["new"], row["blast_on"])
        # A flip is a change of STATE (refused vs printed vs absent); a change in
        # a printed MCC's value is already in max_abs_delta.
        mcc_flip = ((mcc_state(row["new"]) in ("refused", "—"))
                    != (mcc_state(row["blast_off"]) in ("refused", "—")))
        if d_off is not None and d_off <= EPS and not mcc_flip:
            cls = "unchanged"
        elif d_on is not None and d_on <= EPS:
            cls = "as-predicted"
        elif scope.get("n_origin_restored"):
            cls = "origin-restored"
        else:
            cls = "other"
        classes[cls] += 1
        reg = register.get(row["eval"], {})
        rec = {
            "eval": row["eval"], "family": row.get("family"), "class": cls,
            "conditions": reg.get("conditions", ""), "analyses": reg.get("analyses", ""),
            "n_detections": scope.get("n_detections"),
            "n_out_of_frame": scope.get("n_out_of_frame"),
            "n_out_of_frame_cross_sheet": scope.get("n_out_of_frame_cross_sheet"),
            "n_origin_restored": scope.get("n_origin_restored"),
            "off_f1_20": headline(row["blast_off"], "20"),
            "on_f1_20": headline(row["blast_on"], "20"),
            "new_f1_20": headline(row["new"], "20"),
            "off_f1_50": headline(row["blast_off"], "50"),
            "new_f1_50": headline(row["new"], "50"),
            "mcc_off": mcc_state(row["blast_off"]), "mcc_new": mcc_state(row["new"]),
            "max_abs_delta_vs_off": d_off, "max_abs_delta_vs_on": d_on,
        }
        if cls == "other":
            other.append(rec)
        if (d_off or 0) >= 0.001 or mcc_flip:
            moved.append(rec)
    moved.sort(key=lambda r: (r["class"], r["eval"]))
    summary = {
        "n_rows": len(rows), "classes": dict(classes), "scope_fired": dict(fired),
        "n_moved_ge_0.001": len(moved),
        "n_moved_by_class": dict(Counter(r["class"] for r in moved)),
        "registered_moved": [r["eval"] for r in moved if r["conditions"]],
        "analyses_moved": sorted({a for r in moved for a in r["analyses"].split(";") if a}),
        "other": other, "errors": errors,
    }
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "summary_new.json").write_text(json.dumps(summary, indent=1, default=str))
    with (args.outdir / "moved_new.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(moved[0]) if moved else ["eval"])
        writer.writeheader()
        writer.writerows(moved)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("other",)},
                     indent=1, default=str)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
