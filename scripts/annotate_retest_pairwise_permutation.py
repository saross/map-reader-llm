#!/usr/bin/env python3
"""
Annotate the March retest pairwise file with its permutation re-test (D42).

Why this script exists
----------------------
``results/retest/pairwise-bootstrap-comparisons.json`` holds the Era-1
retest's 70 pairwise contrasts with p-values read off a bootstrap
(2 x the minority tail, floored at 1/B). PI ruling D42 (2026-10-05)
retires that p: every contrast is tested by the paired tile-swap
permutation test with Benjamini-Hochberg (BH) correction. The file has no
committed producer (inline session code made it; W2.1), so it cannot be
regenerated; the PI ruled to ANNOTATE it instead (Session 161).

This script adds, to each comparison, a ``permutation_retest`` block from
W2's re-test of the same inputs
(``reports/retest-bootstrap-check-2026-10-05-scripts/retest70.json``): F1,
precision and recall permutation p-values, the observed F1 difference, the
number of discordant tiles, and the within-phase BH-adjusted F1 p. The
original bootstrap fields stay as written (archive, never delete) and the
metadata says which fields are authoritative. Re-running is idempotent.

Usage::

    python scripts/annotate_retest_pairwise_permutation.py          # dry run
    python scripts/annotate_retest_pairwise_permutation.py --write

Zero API, seconds of compute.

Created: 2026-10-05 (Session 161, D42)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from lib_permutation import bh_adjust  # noqa: E402

TARGET = PROJECT_ROOT / "results/retest/pairwise-bootstrap-comparisons.json"
RETEST = (PROJECT_ROOT / "reports/retest-bootstrap-check-2026-10-05-scripts/"
          "retest70.json")
REPORT = "reports/retest-bootstrap-check-2026-10-05.md"
FDR_Q = 0.05

ANNOTATION_NOTE = (
    "PI ruling D42 (2026-10-05): no p-value is read from a bootstrap. The "
    "fields f1_p_value, precision_p, recall_p and significant_raw in each "
    "comparison are the RETIRED bootstrap values (2 x minority tail, floor "
    "1/B), kept as published. The authoritative test is each comparison's "
    "permutation_retest block: the paired tile-swap permutation test (10,000 "
    "permutations, seed 42, 20 m) on the same March inputs, with BH within "
    f"each phase at q = {FDR_Q}. Source: {REPORT} § W2.4, "
    "retest70.json. Bootstrap CIs (f1_ci_lower/upper) remain in use."
)


def build_annotations(comparisons: list[dict], retest: list[dict]) -> list[dict]:
    """Return one ``permutation_retest`` block per comparison, in order.

    Asserts the re-test rows align with the comparisons (same phase, arms
    and committed bootstrap p) before anything is built.

    Args:
        comparisons: The file's ``comparisons`` list.
        retest: W2's ``retest70.json`` rows.

    Returns:
        The blocks, aligned with ``comparisons``.
    """
    if len(comparisons) != len(retest):
        raise SystemExit(f"{len(comparisons)} comparisons vs {len(retest)} re-test rows")
    by_i = {r["i"]: r for r in retest}
    for i, c in enumerate(comparisons):
        r = by_i[i]
        if (c["phase"], c["condition_a"], c["condition_b"]) != (r["phase"], r["a"], r["b"]):
            raise SystemExit(f"row {i}: re-test row does not match the comparison")
        if c["f1_p_value"] != r["committed_f1_p"]:
            raise SystemExit(f"row {i}: committed bootstrap p differs from the re-test's record")

    # BH within each phase, as the boards and the W2 re-test do.
    phases: dict[str, list[int]] = defaultdict(list)
    for i, c in enumerate(comparisons):
        phases[c["phase"]].append(i)
    bh = {}
    for idx in phases.values():
        bh.update(zip(idx, bh_adjust([by_i[i]["perm_p_f1"] for i in idx])))

    blocks = []
    for i in range(len(comparisons)):
        r = by_i[i]
        blocks.append({
            "f1_p": r["perm_p_f1"],
            "precision_p": r["perm_p_prec"],
            "recall_p": r["perm_p_rec"],
            "f1_bh_within_phase": round(bh[i], 6),
            "significant_raw": r["perm_p_f1"] < FDR_Q,
            "significant_bh_within_phase": bh[i] <= FDR_Q,
            "observed_f1_diff": r["obs_diff"],
            "n_discordant_tiles": r["k_discordant"],
            "method": "paired tile-swap permutation, 10,000, seed 42, 20 m (D42)",
            "source": "reports/retest-bootstrap-check-2026-10-05-scripts/retest70.json",
        })
    return blocks


def main(argv: list[str] | None = None) -> int:
    """Dry-run by default; ``--write`` rewrites the target in place."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    retest = json.loads(RETEST.read_text(encoding="utf-8"))
    blocks = build_annotations(data["comparisons"], retest)

    flips = [i for i, (c, b) in enumerate(zip(data["comparisons"], blocks))
             if c["significant_raw"] != b["significant_raw"]]
    print(f"{len(blocks)} comparisons annotated; raw-alpha flips: {flips}")
    print("BH-significant within phase:",
          [i for i, b in enumerate(blocks) if b["significant_bh_within_phase"]])

    for c, b in zip(data["comparisons"], blocks):
        c["permutation_retest"] = b
    data["metadata"]["d42_annotation"] = ANNOTATION_NOTE
    if args.write:
        # indent=2, ASCII escapes, no trailing newline: the file's own format.
        TARGET.write_text(json.dumps(data, indent=2),
                          encoding="utf-8")
        print(f"wrote {TARGET.relative_to(PROJECT_ROOT)}")
    else:
        print("(dry run: nothing written; --write applies it)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
