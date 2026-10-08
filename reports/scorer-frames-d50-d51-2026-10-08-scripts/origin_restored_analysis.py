"""Characterise the cells D50's origin attribution moves, and check two claims.

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only
post-processing of ``rescore_new.py`` rows joined to the blast radius's rows.

For every cell in class ``origin-restored`` (``summarise_new.py``) it records:

* the direction and size of the move at 20 m (NEW − OFF, F1, P and R);
* whether the cell's ``source_tile`` was SYNTHESISED by the evaluator's spatial
  join (the blast radius's ``diag_runs[*].source_tile_synthesised``) or read
  from the file — the mechanism test: a synthesised ``source_tile`` is the
  first frame tile in join order, which in a sheet-edge overlap can lie on a
  sheet none of the cluster's members was seen on;
* which origin column the file carries.

It also checks two claims. (1) The frames report's census
(``frames-blast-radius-2026-10-07-scripts/sheet_attribution_census.py``,
``as_list``) parses list, tuple and string values but not the NumPy arrays
geopandas returns for JSON-array properties; the census's cross-sheet count
for such files is therefore 0 by construction. (2) How many cells the
rejected first-origin rule moved DIFFERENTLY from the any-member rule, from the
two runs' rows (``--first-origin-rows``).

Usage::

    python origin_restored_analysis.py --new out/new_evaluations.jsonl \
        --blast BLAST/out/evaluations.jsonl BLAST/out/evaluations_rerun.jsonl \
                BLAST/out/evaluations_nx.jsonl \
        --first-origin-rows out/superseded-6b25cb9cf-array-parse/new_evaluations.jsonl \
        --out out/origin_restored_analysis.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


def census_as_list(value: Any) -> list[str]:
    """The census's own parser, copied verbatim (sheet_attribution_census.as_list)."""
    if value is None:
        return []
    if isinstance(value, float) and value != value:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if v]
    text = str(value).strip()
    if text.startswith("["):
        try:
            return [str(v) for v in json.loads(text) if v]
        except json.JSONDecodeError:
            return [text]
    return [t.strip() for t in text.split(";") if t.strip()]


def f1(block: dict[str, Any] | None, buf: str = "20") -> dict[str, float] | None:
    """The per-buffer metrics at one buffer."""
    return ((block or {}).get("per_buffer") or {}).get(buf)


def load(path: Path) -> dict[str, dict[str, Any]]:
    """Rows keyed by evaluation path."""
    out = {}
    for line in path.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["eval"]] = r
    return out


def main() -> int:
    """Analyse and write the record."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--new", type=Path, required=True)
    ap.add_argument("--blast", type=Path, nargs="+", required=True)
    ap.add_argument("--first-origin-rows", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    new = load(args.new)
    blast: dict[str, dict[str, Any]] = {}
    for p in args.blast:
        blast.update(load(p))
    first = load(args.first_origin_rows)

    rows = []
    for ev, r in new.items():
        if r.get("new_status") != "scored" or not (r.get("new_scope") or {}).get(
                "n_origin_restored"):
            continue
        n20, o20 = f1(r["new"]), f1(r["blast_off"])
        if n20 is None or o20 is None:
            continue
        d = {m: n20[m] - o20[m] for m in ("f1", "precision", "recall")}
        if max(abs(v) for v in d.values()) < 0.001:
            continue
        diag = (blast.get(ev) or {}).get("diag_runs") or []
        rows.append({
            "eval": ev, "family": r.get("family"),
            "n_origin_restored": r["new_scope"]["n_origin_restored"],
            "n_detections": r["new_scope"]["n_detections"],
            "origin_columns": r.get("new_scope_origin_columns"),
            "source_tile_synthesised": bool(diag) and all(
                x.get("source_tile_synthesised") for x in diag),
            "delta_20": d,
        })
    deltas = np.array([x["delta_20"]["f1"] for x in rows])
    synth = Counter(x["source_tile_synthesised"] for x in rows)
    cols = Counter(tuple(x["origin_columns"] or []) for x in rows)

    # Claim (1): the census parser on a NumPy array of names.
    sample = np.array(["K-35-052-4_32635_x0_y0.png", "K-35-053-3_Elenovo_x0_y0.png"])
    census_parse = census_as_list(sample)

    # Claim (2): first-origin vs any-member, cell by cell (F1@20, scored in both).
    differ = []
    for ev, r in new.items():
        q = first.get(ev)
        if not q or r.get("new_status") != "scored" or q.get("new_status") != "scored":
            continue
        a, b = f1(r["new"]), f1(q["new"])
        if a and b and abs(a["f1"] - b["f1"]) >= 0.001:
            differ.append(ev)

    out = {
        "n_origin_restored_moved": len(rows),
        "f1_delta_20": {
            "n_positive": int((deltas > 0).sum()), "n_negative": int((deltas < 0).sum()),
            "n_zero": int((deltas == 0).sum()),
            "median": float(np.median(deltas)) if len(deltas) else None,
            "min": float(deltas.min()) if len(deltas) else None,
            "max": float(deltas.max()) if len(deltas) else None,
            "n_abs_ge_0.01": int((np.abs(deltas) >= 0.01).sum()),
        },
        "source_tile_synthesised": {str(k): v for k, v in synth.items()},
        "origin_columns": {"|".join(k) or "-": v for k, v in cols.items()},
        "census_parser_on_numpy_array": census_parse,
        "first_origin_vs_any_member_cells_differing_ge_0.001": len(differ),
        "first_origin_vs_any_member_examples": differ[:20],
        "rows": rows,
    }
    args.out.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows",)}, indent=1,
                     default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
