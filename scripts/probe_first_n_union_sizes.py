#!/usr/bin/env python3
"""
Measure the candidate-universe size of a first-N sub-pool, for Phase-2 costing.

Why this exists
---------------
A verifier's cost is per candidate, so costing a missing K rung needs the size of
the candidate universe that rung's verifier pass would see — the vote >= 1 union
over ``passes[:N]``. `results/k-ladder-2026-09-12/inventory.md` § 4 shows that no
such union is committed for any of the 30 gaps, and that it is not a subset of a
longer committed one, so the number cannot be read off an existing artefact. It
CAN be measured at US$0, because the passes are committed: this script builds the
union with the project's canonical consensus chain
(``scripts/merge_passes.py`` — ``deduplicate_within_pass`` then
``cluster_across_passes``) and reports the cluster count and vote distribution
WITHOUT writing a consensus file, so nothing in ``outputs/`` moves.

The number it reports is exactly what
``merge_passes.py --sweep --passes 1,..,N`` would produce at vote >= 1, because
it calls the same two functions on the same inputs in the same order.

Usage::

    python scripts/probe_first_n_union_sizes.py \\
        --pool outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3 \\
        --label "Gemini 3 MINIMAL text 384 px, T 0.3" \\
        --n 1 --n 3 \\
        --out results/k-ladder-2026-09-12/first-n-union-sizes.json

Repeat ``--pool``/``--label`` for more pools; every pool's measurements land in
one JSON. Zero API. Clustering is quadratic in the pooled detection count, so
run it on sapphire.

Created: 2026-09-12 (Session 154, K-ladder Phase 1 step 6)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.merge_passes import (  # noqa: E402
    cluster_across_passes,
    deduplicate_within_pass,
    load_pass_detections,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def union_size(pool_dir: Path, n: int) -> dict[str, Any]:
    """The vote >= 1 union over the pool's first ``n`` passes.

    Args:
        pool_dir: A pool directory holding ``run_1`` … ``run_K`` subdirectories.
        n: How many leading passes to pool (the preregistered first-N rule).

    Returns:
        The raw, deduplicated and clustered counts, plus the vote distribution.

    Raises:
        ValueError: If the pool does not hold ``n`` passes, because a rung that
            cannot be built must not be costed as though it could.
    """
    raw = load_pass_detections(pool_dir, pass_filter=list(range(1, n + 1)))
    if len(raw) != n:
        raise ValueError(
            f"{pool_dir}: loaded {len(raw)} pass(es) of the {n} requested "
            f"({sorted(raw)}); the rung cannot be built from this pool")
    deduped = {pass_id: deduplicate_within_pass(features)
               for pass_id, features in raw.items()}
    clusters = cluster_across_passes(deduped)
    votes = Counter(c["vote_count"] for c in clusters)
    return {
        "n_passes": n,
        "pass_ids": sorted(raw),
        "n_raw_detections": sum(len(v) for v in raw.values()),
        "n_deduped_detections": sum(len(v) for v in deduped.values()),
        "n_union_candidates": len(clusters),
        "vote_distribution": {str(k): v for k, v in sorted(votes.items())},
    }


def main(argv: list[str] | None = None) -> int:
    """Measure every requested (pool, N) union and write one JSON report."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--pool", action="append", required=True, type=Path,
                        help="Pool directory holding run_1..run_K. Repeatable.")
    parser.add_argument("--label", action="append", default=[],
                        help="Human label for the matching --pool. Repeatable.")
    parser.add_argument("--n", action="append", type=int, required=True,
                        help="Rung pass count to measure. Repeatable; applied "
                             "to every pool.")
    parser.add_argument("--out", type=Path, required=True,
                        help="Destination JSON.")
    args = parser.parse_args(argv)

    pools = []
    for index, pool_dir in enumerate(args.pool):
        label = args.label[index] if index < len(args.label) else str(pool_dir)
        entry: dict[str, Any] = {
            "label": label,
            "pool_dir": str(pool_dir),
            "rungs": [],
            "refusals": [],
        }
        for n in args.n:
            try:
                measured = union_size(pool_dir, n)
            except ValueError as error:
                entry["refusals"].append(str(error))
                logger.warning("%s", error)
                continue
            entry["rungs"].append(measured)
            logger.info("%s N=%d: %d candidates (raw %d, deduped %d)",
                        label, n, measured["n_union_candidates"],
                        measured["n_raw_detections"],
                        measured["n_deduped_detections"])
        pools.append(entry)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": ("merge_passes.load_pass_detections(pass_filter=1..N) then "
                   "deduplicate_within_pass then cluster_across_passes — the "
                   "canonical consensus chain, at vote >= 1, with no consensus "
                   "file written"),
        "n_pools": len(pools),
        "pools": pools,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
