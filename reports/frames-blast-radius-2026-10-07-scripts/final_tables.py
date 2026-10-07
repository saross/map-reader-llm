"""Headline counts, the gate (i) table, and the grouped moved-cell table for the report.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only; reads the summary
CSVs written by ``summarise_evaluations.py`` and ``classify_reproduction.py`` plus the
registers, writes ``final.json`` and ``moved_grouped.csv``.

Register status of a cell: ``registered`` (a ``results/conditions-manifest.json``
condition's source file), ``waived`` (listed under ``_ignored_evals`` in
``results/run-conditions.json``), ``archive`` (under ``archive/``), or ``other``.

Usage::

    python final_tables.py --repo ~/Code/map-reader-llm --summary out/summary
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

#: Moved-cell groups, matched on the evaluation path (first match wins).
GROUPS = (
    ("archive/", "archived copies"),
    ("results/null-exemplar-sensitivity-2026-09-13/", "null-exemplar reduced-frame re-scores"),
    ("results/k-ladder-2026-09-12/phase2/cells/gemini37-screen", "3.7 GS K-ladder rungs"),
    ("results/pairwise/tile-size-30m/", "512 px cells scored on the 384 px Era-2 frame"),
    ("results/uplift-supplement/k1-gapfill/stride-55map", "55-map stride K = 1 gap-fill"),
    ("results/uplift-supplement/verifier-pairing/stride-55map", "55-map stride pairing twins"),
    ("results/uplift-supplement/k1-gapfill/", "GS grid-common K = 1 gap-fill"),
)


def group_of(path: str) -> str:
    """Name the moved-cell group of an evaluation path."""
    return next((g for prefix, g in GROUPS if path.startswith(prefix)), "other")


def main() -> int:
    """Build the final tables."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    cm = json.loads((repo / "results/conditions-manifest.json").read_text())
    registered = {s for c in cm["conditions"] for s in c["provenance"]["source_files"]}
    rc = json.loads((repo / "results/run-conditions.json").read_text())["decomposition"]
    waived = {e for v in rc.values() for e in (v.get("_ignored_evals") or [])
              if isinstance(e, str)}
    waived |= {e.get("eval_path") or e.get("path") for v in rc.values()
               for e in (v.get("_ignored_evals") or [])
               if isinstance(e, dict)}

    def status(path: str) -> str:
        if path.startswith("archive/"):
            return "archive"
        if path in registered:
            return "registered"
        if path in waived:
            return "waived"
        return "other"

    cells = list(csv.DictReader((args.summary / "cells.csv").open()))
    moved = list(csv.DictReader((args.summary / "moved.csv").open()))
    fails = {r["eval"]: r for r in csv.DictReader(
        (args.summary / "reproduction_failures.csv").open())}

    scored = [c for c in cells if c["status"] == "scored"]
    diag = [c for c in cells if c["n_out_of_frame"] not in ("", None)]
    oof = [c for c in diag if int(c["n_out_of_frame"] or 0) > 0]
    null = [c for c in diag if int(c["n_null_source_tile"] or 0) > 0]

    def delta(c: dict[str, str]) -> float:
        return float(c["max_abs_delta"] or 0)

    headline: dict[str, Any] = {
        "evaluations_committed": len(cells),
        "status": dict(Counter(c["status"] for c in cells)),
        "cells_scored_off_and_on": len(scored),
        "cells_with_out_of_frame_diagnostics": len(diag),
        "cells_with_any_out_of_frame": len(oof),
        "cells_with_any_out_of_frame_by_status": dict(Counter(status(c["eval"]) for c in oof)),
        "cells_with_null_source_tile": len(null),
        "cells_with_null_in_frame": sum(1 for c in diag if int(c["n_null_in_frame"] or 0) > 0),
        "moved": {str(t): sum(1 for c in scored if delta(c) >= t) for t in (0.001, 0.005, 0.01)},
        "moved_by_status": {str(t): dict(Counter(status(c["eval"]) for c in scored
                                                 if delta(c) >= t))
                            for t in (0.001, 0.005, 0.01)},
        "registered_cells_scored": sum(1 for c in scored if status(c["eval"]) == "registered"),
        "registered_cells_with_out_of_frame": sum(1 for c in oof
                                                  if status(c["eval"]) == "registered"),
    }

    # Gate (i): F1/P/R reproduction and MCC reproduction, by family.
    gate: dict[str, Counter] = defaultdict(Counter)
    for c in scored:
        fam = c["family"]
        gate[fam]["scored"] += 1
        rep = c["reproduced"]
        if rep == "True":
            gate[fam]["all_reproduced"] += 1
            continue
        if rep in ("", "None"):
            gate[fam]["no_committed_values"] += 1
            continue
        cat = fails.get(c["eval"], {}).get("category", "unclassified")
        if cat == "mcc-refused-now":
            gate[fam]["f1pr_reproduced_mcc_refused_now"] += 1
        else:
            gate[fam][f"not_reproduced:{cat}"] += 1
    headline["gate_i_by_family"] = {k: dict(v) for k, v in sorted(gate.items())}
    totals: dict[str, Counter] = {"live": Counter(), "archive": Counter()}
    for fam, counts in gate.items():
        side = "archive" if fam.startswith("[archive]") else "live"
        totals[side].update(counts)
    for side, counts in totals.items():
        counts["f1pr_reproduced_total"] = (counts["all_reproduced"]
                                           + counts["f1pr_reproduced_mcc_refused_now"])
    headline["gate_i_totals"] = {k: dict(v) for k, v in totals.items()}
    headline["gate_i_named_cells"] = [
        {k: c[k] for k in ("eval", "committed_f1_20", "off_f1_20", "committed_mcc", "off_mcc",
                           "reproduced", "repro_notes")}
        for c in scored if "gemini37-screen-2026-08-28__g37-text-k" in c["eval"]
        and c["eval"].startswith("results/k-ladder-2026-09-12/phase2/")
    ]

    out_rows = []
    for m in moved:
        out_rows.append({"group": group_of(m["eval"]), "register_status": status(m["eval"]),
                         **m})
    out_rows.sort(key=lambda r: (r["group"], -float(r["max_abs_delta"])))
    with (args.summary / "moved_grouped.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    grp: dict[str, dict[str, Any]] = {}
    for r in out_rows:
        g = grp.setdefault(r["group"], {"n": 0, "registered": 0, "waived": 0, "archive": 0,
                                        "other": 0, "max_abs_delta": 0.0, "min_abs_delta": 9.0,
                                        "oof_range": [10**9, 0]})
        g["n"] += 1
        g[r["register_status"]] += 1
        d = float(r["max_abs_delta"])
        g["max_abs_delta"] = max(g["max_abs_delta"], d)
        g["min_abs_delta"] = min(g["min_abs_delta"], d)
        o = int(r["n_out_of_frame"])
        g["oof_range"] = [min(g["oof_range"][0], o), max(g["oof_range"][1], o)]
    headline["moved_groups"] = grp
    # Cells with out-of-frame detections that do NOT move by 0.001.
    headline["oof_but_not_moved"] = sum(1 for c in oof if c["status"] == "scored"
                                        and delta(c) < 0.001)
    (args.summary / "final.json").write_text(json.dumps(headline, indent=1))
    print(json.dumps(headline, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
