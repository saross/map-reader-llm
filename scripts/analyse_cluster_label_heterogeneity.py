#!/usr/bin/env python3
"""
Cluster label-heterogeneity analysis for erratum E64 sub-item (iii).

Purpose
-------
The lodged registration's voting step 4 (`osf/preregistration.md:1882`)
says clusters form on distance AND matching label (reading A), while the
same section's consensus output specification (`:1892`) makes the label a
post-hoc majority vote (reading B), and evaluation (Section 4.1.2) is
label-blind. The executed pipeline clusters spatially only. The two
readings diverge only where detections within the 20 m tolerance carry
DIFFERENT subtypes. Previous materiality figures (17.2 % / ~21 %
non-`burial_mound` subtype shares) are loose upper bounds; this script
computes the TRUE materiality quantity, ruled required by the Principal
Investigator (PI) on 2026-07-30 before E64 lands
(`reports/verification/phase2-rulings-2026-07-30.md` Section 1c):

1. the fraction of spatial clusters whose members disagree on subtype
   ("label-heterogeneous clusters"); and
2. for every vote threshold t, how many clusters that pass at t would
   FAIL if clustering were label-gated — approximated by splitting each
   cluster by label and asking whether the best single-label vote count
   still reaches t.

Fidelity
--------
Loading, coordinate handling, within-pass deduplication, and the greedy
star clustering replicate the executed pipeline exactly, by importing
from ``merge_passes.py`` and ``analyse_diversity.py`` (the same route
``materialise_phase3c_consensus.py`` takes). The only difference is that
the across-pass clustering here retains member labels instead of
collapsing them to the majority label.

Corpora analysed
----------------
- Era 1 (340 tiles, 512 px): the 45 phase3c H9 diversity pools —
  track1-image conditions A–E x replications 1–5, track2-text conditions
  A, B, D, E x replications 1–5 (condition C is image-diversity and is
  degenerate for the text track).
- Era 2 (487 tiles, 384 px): the ``pv-diag-384`` flash-high-text pool at
  N=30 (the 0.890 headline's proposer pool) and its first-5 sub-pool
  (N=5, the preregistered first-N rule).

Usage
-----
    python scripts/analyse_cluster_label_heterogeneity.py \
        --output-dir reports/verification/apparatus

Zero API cost; pure recomputation over committed detection GeoJSONs.
Run on sapphire per the project compute rule.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Make sibling scripts importable (same pattern as
# materialise_phase3c_consensus.py).
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from analyse_diversity import load_replication_passes  # noqa: E402
from merge_passes import (  # noqa: E402
    DISTANCE_THRESHOLD_METRES,
    deduplicate_within_pass,
    euclidean_distance,
    load_pass_detections,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = SCRIPTS_DIR.parent

# Era 1: the 45 phase3c H9 diversity pools (S106 materialisation layout).
PHASE3C_TRACKS = {
    "track1-image": ["h9-A", "h9-B", "h9-C", "h9-D", "h9-E"],
    "track2-text": ["h9-A", "h9-B", "h9-D", "h9-E"],
}
PHASE3C_BASE = REPO_ROOT / "outputs/retest/phase3c"
PHASE3C_REPLICATIONS = [1, 2, 3, 4, 5]

# Era 2: the headline proposer pool.
ERA2_POOL_DIR = REPO_ROOT / "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7"


def cluster_across_passes_with_labels(
    pass_detections: dict[str, list[dict]],
    distance_thresh: float = DISTANCE_THRESHOLD_METRES,
) -> list[dict]:
    """
    Replicate ``merge_passes.cluster_across_passes`` greedy star
    clustering, retaining per-member labels and per-label vote counts.

    The pooling order, seeding order, and absorption rule are identical
    to the executed pipeline; only the returned statistics differ.

    Args:
        pass_detections: Dict mapping pass_id to deduplicated detection
            dicts (as produced by ``deduplicate_within_pass``).
        distance_thresh: Maximum distance (metres) for clustering.

    Returns:
        List of cluster dicts with vote_count, label composition, and
        per-label distinct-pass vote counts.
    """
    pool: list[dict] = []
    for pass_id, detections in pass_detections.items():
        for det in detections:
            pool.append(
                {
                    "centroid": det["centroid"],
                    "label": det["label"],
                    "pass_id": pass_id,
                }
            )

    if not pool:
        return []

    clusters: list[list[dict]] = []
    used: set[int] = set()

    for i, det in enumerate(pool):
        if i in used:
            continue
        cluster = [det]
        used.add(i)
        for j, candidate in enumerate(pool):
            if j in used:
                continue
            if euclidean_distance(det["centroid"], candidate["centroid"]) <= distance_thresh:
                cluster.append(candidate)
                used.add(j)
        clusters.append(cluster)

    result = []
    for cluster in clusters:
        vote_count = len({d["pass_id"] for d in cluster})
        label_counts = Counter(d["label"] for d in cluster)
        # Votes per label: distinct passes contributing that label.
        label_votes = {
            label: len({d["pass_id"] for d in cluster if d["label"] == label})
            for label in label_counts
        }
        result.append(
            {
                "vote_count": vote_count,
                "n_members": len(cluster),
                "label_counts": dict(label_counts),
                "label_votes": label_votes,
                "max_label_votes": max(label_votes.values()),
                "heterogeneous": len(label_counts) > 1,
            }
        )
    return result


def summarise_pool(
    clusters: list[dict],
    total_passes: int,
) -> dict:
    """
    Compute heterogeneity and threshold-impact statistics for one pool.

    Args:
        clusters: Output of ``cluster_across_passes_with_labels``.
        total_passes: Number of passes in the pool (N).

    Returns:
        Summary dict: cluster counts, heterogeneous share, and per-
        threshold affected counts (clusters passing spatially at t whose
        best single-label vote count falls below t).
    """
    n_clusters = len(clusters)
    het = [c for c in clusters if c["heterogeneous"]]
    per_threshold = {}
    for t in range(1, total_passes + 1):
        passing = [c for c in clusters if c["vote_count"] >= t]
        affected = [c for c in passing if c["max_label_votes"] < t]
        per_threshold[t] = {
            "passing": len(passing),
            "affected_by_label_gate": len(affected),
        }
    return {
        "n_clusters": n_clusters,
        "n_heterogeneous": len(het),
        "heterogeneous_share": (len(het) / n_clusters) if n_clusters else 0.0,
        "per_threshold": per_threshold,
    }


def analyse_phase3c() -> list[dict]:
    """Analyse the 45 Era-1 phase3c H9 diversity pools."""
    rows = []
    for track, conditions in PHASE3C_TRACKS.items():
        study_dir = PHASE3C_BASE / track
        for cond in conditions:
            # Sub-variant suffixes are condition-specific (A: p1-p5,
            # B: v1-v5, C: img1-img5, D: t1-t5, E: p1-p5) — discover
            # them from disk rather than assuming a naming scheme.
            sub_conditions = sorted(
                d.name for d in study_dir.glob(f"{cond}-*") if d.is_dir()
            )
            if len(sub_conditions) != 5:
                logger.warning(
                    "Expected 5 sub-conditions for %s/%s, found %d: %s",
                    track, cond, len(sub_conditions), sub_conditions,
                )
            for k in PHASE3C_REPLICATIONS:
                pass_detections = load_replication_passes(study_dir, sub_conditions, k)
                if not any(pass_detections.values()):
                    logger.warning("Empty pool: %s %s rep %d", track, cond, k)
                    continue
                clusters = cluster_across_passes_with_labels(pass_detections)
                summary = summarise_pool(clusters, total_passes=len(sub_conditions))
                rows.append(
                    {
                        "corpus": "era1-phase3c",
                        "pool": f"{track}/{cond}/rep{k}",
                        "n_passes": len(sub_conditions),
                        **summary,
                    }
                )
                logger.info(
                    "%s/%s rep%d: %d clusters, %d heterogeneous (%.2f%%)",
                    track, cond, k, summary["n_clusters"], summary["n_heterogeneous"],
                    100 * summary["heterogeneous_share"],
                )
    return rows


def analyse_era2() -> list[dict]:
    """Analyse the Era-2 flash-high-text pool at N=30 and N=5 (first 5)."""
    rows = []
    for label, pass_filter in [("n30", None), ("n5-first5", [1, 2, 3, 4, 5])]:
        raw = load_pass_detections(ERA2_POOL_DIR, pass_filter=pass_filter)
        if not raw:
            logger.warning("No Era-2 passes loaded for %s", label)
            continue
        deduped = {pid: deduplicate_within_pass(feats) for pid, feats in raw.items()}
        clusters = cluster_across_passes_with_labels(deduped)
        summary = summarise_pool(clusters, total_passes=len(deduped))
        rows.append(
            {
                "corpus": "era2-pv-diag-384",
                "pool": f"flash-high-text/{label}",
                "n_passes": len(deduped),
                **summary,
            }
        )
        logger.info(
            "era2 %s: %d clusters, %d heterogeneous (%.2f%%)",
            label, summary["n_clusters"], summary["n_heterogeneous"],
            100 * summary["heterogeneous_share"],
        )
    return rows


def aggregate(rows: list[dict]) -> dict:
    """Aggregate heterogeneity counts across pools, per corpus and overall."""
    out = {}
    for scope in ("era1-phase3c", "era2-pv-diag-384", "all"):
        sel = [r for r in rows if scope == "all" or r["corpus"] == scope]
        total = sum(r["n_clusters"] for r in sel)
        het = sum(r["n_heterogeneous"] for r in sel)
        out[scope] = {
            "n_pools": len(sel),
            "total_clusters": total,
            "heterogeneous_clusters": het,
            "heterogeneous_share": (het / total) if total else 0.0,
        }
    return out


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cluster label-heterogeneity analysis (E64 iii materiality)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "reports/verification/apparatus",
        help="Directory for the JSON output",
    )
    args = parser.parse_args()

    rows = analyse_phase3c() + analyse_era2()
    agg = aggregate(rows)

    result = {
        "_README": (
            "Cluster label-heterogeneity analysis for erratum E64 sub-item (iii). "
            "Replicates the executed spatial-only greedy clustering "
            "(merge_passes.cluster_across_passes semantics) while retaining member "
            "labels. 'affected_by_label_gate' at threshold t counts clusters that "
            "pass spatially at t but whose best single-label distinct-pass vote "
            "count falls below t — the approximation of the registration's "
            "reading A (label-gated clustering) by label-splitting. PI ruling "
            "2026-07-30: reports/verification/phase2-rulings-2026-07-30.md S 1c."
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "distance_threshold_metres": DISTANCE_THRESHOLD_METRES,
        "aggregate": agg,
        "pools": rows,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / "cluster-label-heterogeneity-2026-07-30.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=1)
    logger.info("Wrote %s", out_path)

    print("\n=== AGGREGATE ===")
    for scope, a in agg.items():
        print(
            f"{scope}: {a['heterogeneous_clusters']}/{a['total_clusters']} "
            f"clusters heterogeneous ({100 * a['heterogeneous_share']:.2f}%) "
            f"across {a['n_pools']} pools"
        )


if __name__ == "__main__":
    main()
