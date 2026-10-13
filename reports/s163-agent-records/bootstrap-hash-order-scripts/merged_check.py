#!/usr/bin/env python3
"""
Check the D63 results after merging ``main`` (PR #33) into the branch.

Writes a JSON record that answers three questions:

1. Does the function-level harness still find the three varying functions
   on merged ``main`` (``8ec0fa5e7``) and none on the merged branch, and do
   its two runs agree?
2. Do the merged branch's replays (hash seed 1, two runs) give the same
   outputs as the pre-merge branch's replays? If so, every impact number
   measured before the merge holds after it.
3. The pre-merge harness runs, for completeness.

Usage::

    python merged_check.py --work /tmp/d63-runs --out out/merged-check.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from impact_summary import norm_digest  # noqa: E402

RETEST = ("phase2a", "phase2b-track1", "phase2b-track2", "phase2c-exploratory",
          "phase2c-track1", "phase2c-track2", "phase2d-track1", "phase2d-track2", "phase2e")
CHECKS = [
    ("retest", "s1", [f"out/{p}-evaluation.json" for p in RETEST], "bootstrap-hash-order-s12"),
    ("interaction", "", ["out/image.json", "out/text.json"], "bootstrap-hash-order"),
    ("sd-v1", "", ["results/secondary-effects-consensus-sd/sd_shrinkage.json"],
     "bootstrap-hash-order"),
    ("fair384", "s1", ["out/fair-384-vs-512.json", "out/pairwise-384px.json"],
     "bootstrap-hash-order-s12"),
    ("pvpair", "", ["out/text-asis/comparison.json", "out/image-asis/comparison.json"],
     "bootstrap-hash-order"),
]


def harness(work: Path, label: str, run1: Path, run2: Path) -> dict:
    """Statuses of one harness pair and whether the two runs agree."""
    a, b = json.loads(run1.read_text()), json.loads(run2.read_text())
    return {"label": label,
            "runs_agree": all(a["cases"][c]["digests"] == b["cases"][c]["digests"]
                              for c in a["cases"]),
            "varies": sorted(c for c in a["cases"] if a["cases"][c]["status"] != "stable"),
            "n_cases": len(a["cases"])}


def main() -> int:
    """Write the merged-check record."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--premerge-main", type=Path, nargs=2, required=True)
    ap.add_argument("--premerge-fix", type=Path, nargs=2, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    w = args.work
    record = {"harness": [
        harness(w, "main 67a3f2795", *args.premerge_main),
        harness(w, "fix before merge", *args.premerge_fix),
        harness(w, "main 8ec0fa5e7 (after PR #33)", w / "harness-mergedmain-run1.json",
                w / "harness-mergedmain-run2.json"),
        harness(w, "fix after merge", w / "harness-mergedfix-run1.json",
                w / "harness-mergedfix-run2.json"),
    ], "replays": []}
    for name, stem, outs, pre in CHECKS:
        tags = {run: f"d63-merge-tmp-{stem}-{run}" if stem else f"d63-merge-tmp-{run}"
                for run in ("run1", "run2")}
        for rel in outs:
            m1 = norm_digest(w / name / tags["run1"] / "seed-1", rel)
            m2 = norm_digest(w / name / tags["run2"] / "seed-1", rel)
            p1 = norm_digest(w / name / f"{pre}-run1" / "seed-1", rel)
            record["replays"].append({"family": name, "output": rel, "merged_sha256": m1,
                                      "merged_runs_agree": m1 == m2,
                                      "equals_premerge_fix": m1 == p1})
    args.out.write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record["harness"], indent=1))
    print("replays equal to pre-merge fix:",
          sum(r["equals_premerge_fix"] for r in record["replays"]), "of", len(record["replays"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
