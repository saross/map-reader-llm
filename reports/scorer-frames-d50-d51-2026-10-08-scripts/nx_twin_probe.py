"""Is a null-exemplar twin's move real, or an artefact of its scratch rebuild?

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only diagnostic.

The null-exemplar reduced-frame inputs are gitignored; the blast radius rebuilt
them in scratch (``rebuild_null_exemplar.py``). For a reduced-frame cell that
D50's origin rule moves, this compares its rebuilt detection file with its
full-frame parent's committed-cell input: the columns each carries, whether
``source_tile`` is present (or synthesised at scoring time by the evaluator's
spatial join), and the D50 scope counts on the parent under the full frame.

Usage::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python nx_twin_probe.py \
        --code WORKTREE --data ~/Code/map-reader-llm --rows out/new_evaluations.jsonl \
        --blast BLAST/out/evaluations.jsonl BLAST/out/evaluations_nx.jsonl \
        --eval EVAL_PATH --out out/nx_twin_probe.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meas_lib as ml  # noqa: E402


def main() -> int:
    """Compare a moved twin with its parent."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--blast", type=Path, nargs="+", required=True)
    ap.add_argument("--eval", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    ml.setup(args.code)
    data = args.data.expanduser().resolve()
    import geopandas as gpd  # noqa: PLC0415

    blast: dict = {}
    for p in args.blast:
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                blast[r["eval"]] = r
    twin = blast[args.eval]
    cell = Path(args.eval).parent.name
    parent = next((r for k, r in blast.items()
                   if "null-exemplar" not in k and Path(k).parent.name == cell.split("__", 1)[-1]
                   and r.get("bounds") == "inputs/vectors/bounds/full_evaluation_bounds.geojson"),
                  None)
    out = {"twin": args.eval, "twin_detections": twin["detections"][:2],
           "parent": parent["eval"] if parent else None}
    tf = gpd.read_file(ml.resolve(data, twin["detections"][0]))
    out["twin_columns"] = sorted(c for c in tf.columns if c != "geometry")
    if parent:
        pf_path = ml.resolve(data, parent["detections"][0])
        pf = gpd.read_file(pf_path)
        out["parent_detections"] = parent["detections"][:2]
        out["parent_columns"] = sorted(c for c in pf.columns if c != "geometry")
        bounds = ml.load_geojson(ml.resolve(data, parent["bounds"]))
        det = ml.load_detections(pf_path, bounds)
        out["parent_scope"] = ml.LIB.scope_detections_to_frame(det, bounds).diagnostics
    print(json.dumps(out, indent=1, default=str))
    args.out.write_text(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
