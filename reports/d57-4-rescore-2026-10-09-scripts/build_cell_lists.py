"""Build the replay cell lists for Phase 2 and for the byte-diff check (a).

D57 (4) re-score, 2026-10-09 (Session 163). Reads the census
(``census.py``) and ``rescore_b.jsonl``; writes two JSON lists that
``run_replays.py`` consumes. Writes nothing in the repository.

* ``phase2_cells.json`` — the 737 Phase 2 cells (plan § 3.1): the 673
  replayable, the 49 null-exemplar twins, and the 15 sub-0.001 pairing twins,
  regenerated IN PLACE. ``--require-clean-inputs`` is added except for the
  null-exemplar twins, whose inputs are gitignored (plan § 3.1).
* ``bytediff_cells.json`` — plan § 7 row 2 (a): every cell where the D50 scope
  restored a detection but nothing moved, plus 50 cells drawn at random
  (``random.Random(seed).sample`` over the sorted eligible list) from the
  ``unchanged`` class with no restoration, whose committed values reproduce
  from the jsonl's OFF values at 1e-4. Replayed into SCRATCH (``--bytediff-root``)
  with their recipes exactly as recorded (no flag added).

Usage (on sapphire)::

    .venv/bin/python build_cell_lists.py --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --rescore-b ~/scratch/source-tile-gap-2026-10-08/out/rescore_b.jsonl \\
        --census ~/scratch/d57-4-rescore-2026-10-09/out/census.json \\
        --bytediff-root ~/scratch/d57-4-rescore-2026-10-09/bytediff \\
        --out-dir ~/scratch/d57-4-rescore-2026-10-09/out
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d57_common as dc  # noqa: E402

#: The plan § 3.1 groups regenerated in Phase 2.
PHASE2_GROUPS = ("replayable", "null-exemplar", "twin")


def reproduces(repo: Path, rel: str, row: dict[str, Any]) -> bool:
    """True when the committed four-decimal values match the jsonl OFF values at 1e-4."""
    ev = dc.committed_eval(repo, rel)
    if ev is None:
        return False
    committed = dc.per_buffer_committed(ev)
    compared = 0
    for buf, vals in ((row.get("blast_off") or {}).get("per_buffer") or {}).items():
        c = committed.get(buf)
        if not c:
            continue
        for m in dc.METRICS:
            if c.get(m) is None:
                continue
            compared += 1
            if abs(c[m] - vals[m]) > dc.TOL_4DP:
                return False
    return compared > 0


def main() -> int:
    """Write the two cell lists."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rescore-b", type=Path, required=True)
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--bytediff-root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--n-random", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    census = json.loads(args.census.read_text())
    phase2 = [{"eval": c["eval"], "group": c["group"], "registered": c["registered"],
               "add_require_clean": c["group"] != "null-exemplar"}
              for c in census["cells"] if c["group"] in PHASE2_GROUPS]

    classes = dc.classify(dc.load_jsonl(args.rescore_b.expanduser()))
    restored = sorted(e for e, r in classes.items()
                      if (r["row"].get("new_scope") or {}).get("n_origin_restored")
                      and not r["moved"])
    eligible = sorted(
        e for e, r in classes.items()
        if r["class"] == "unchanged"
        and not (r["row"].get("new_scope") or {}).get("n_origin_restored")
        and r["row"].get("script") == "scripts/evaluate_detections.py")
    eligible = [e for e in eligible if reproduces(repo, e, classes[e]["row"])]
    drawn = sorted(random.Random(args.seed).sample(eligible, args.n_random))
    root = args.bytediff_root.expanduser().resolve()
    bytediff = ([{"eval": e, "kind": "restored-unmoved"} for e in restored]
                + [{"eval": e, "kind": "random-unchanged"} for e in drawn])
    for cell in bytediff:
        cell["output_dir"] = str(root / Path(cell["eval"]).parent)
        cell["add_require_clean"] = False
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "phase2_cells.json").write_text(json.dumps(phase2, indent=1) + "\n")
    (args.out_dir / "bytediff_cells.json").write_text(json.dumps(bytediff, indent=1) + "\n")
    print(json.dumps({"phase2": len(phase2), "restored_unmoved": len(restored),
                      "eligible_unchanged": len(eligible), "random_drawn": len(drawn),
                      "seed": args.seed}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
