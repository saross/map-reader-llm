#!/usr/bin/env python3
"""
Derive Vote-Threshold PV Results from a Single Union Verifier Run
==================================================================

Description:
    Takes verifier probabilities from a 1-of-N consensus union run and
    derives separate probabilities + manifest files for each vote-count
    threshold (x-of-N). This avoids running the verifier N times when
    a single run on the union (superset) suffices.

    The union consensus GeoJSON contains ``vote_count`` per detection.
    Candidates with ``vote_count >= x`` form the x-of-N subset. Since
    the union is a superset of all threshold conditions, filtering by
    vote count produces identical candidate sets to running consensus
    at each threshold independently.

Usage::

    python scripts/derive_vote_threshold_results.py \\
        --consensus outputs/h11/pv-diag-384/consensus/image-1of10.geojson \\
        --probabilities outputs/h11/pv-diag-384/verified/image-1of10/probabilities.json \\
        --manifest outputs/h11/pv-diag-384/crops/image-1of10/candidate_manifest.json \\
        --pool-size 10 \\
        --output-dir outputs/h11/pv-diag-384/verified \\
        --prefix image

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd

__version__ = "1.0.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def derive_thresholds(
    consensus_path: Path,
    probabilities_path: Path,
    manifest_path: Path,
    pool_size: int,
    output_dir: Path,
    prefix: str,
) -> None:
    """Derive per-threshold probabilities and manifests from union data.

    Args:
        consensus_path: Path to 1-of-N consensus GeoJSON with vote_count.
        probabilities_path: Path to probabilities.json from verifier.
        manifest_path: Path to candidate_manifest.json from extraction.
        pool_size: Total number of runs (N) — thresholds go from 1 to N.
        output_dir: Base output directory for derived results.
        prefix: Name prefix for output subdirectories (e.g., "image").
    """
    # Load consensus GeoJSON to get vote counts
    gdf = gpd.read_file(consensus_path)
    if "vote_count" not in gdf.columns:
        logger.error("Consensus GeoJSON missing 'vote_count' column")
        sys.exit(1)

    vote_counts = gdf["vote_count"].tolist()
    if not vote_counts:
        logger.error("Consensus GeoJSON has no features")
        sys.exit(1)
    logger.info(
        "Loaded consensus: %d features, vote_count range %d–%d",
        len(gdf), min(vote_counts), max(vote_counts),
    )

    # Load probabilities
    with open(probabilities_path, encoding="utf-8") as f:
        prob_data = json.load(f)
    results = prob_data.get("results", {})
    logger.info("Loaded probabilities: %d results", len(results))

    # Load manifest
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    candidates = manifest.get("candidates", [])
    logger.info("Loaded manifest: %d candidates", len(candidates))

    # Validate alignment: candidate count should match consensus features
    if len(candidates) != len(vote_counts):
        logger.error(
            "Mismatch: %d candidates vs %d consensus features. "
            "These must be from the same extraction.",
            len(candidates), len(vote_counts),
        )
        sys.exit(1)

    # Validate candidate IDs are sequential 0..N-1 (as assigned by
    # extract_candidates.py). Non-sequential IDs would cause the
    # vote_count mapping to silently assign wrong counts.
    actual_ids = {c["candidate_id"] for c in candidates}
    expected_ids = set(range(len(candidates)))
    if actual_ids != expected_ids:
        logger.error(
            "Candidate IDs are not sequential 0..%d: "
            "unexpected IDs %s",
            len(candidates) - 1,
            sorted(actual_ids - expected_ids)[:5],
        )
        sys.exit(1)

    # Build candidate_id → vote_count mapping
    # extract_candidates assigns candidate_id = feature index (0-based)
    id_to_votes: dict[int, int] = {}
    for idx, vc in enumerate(vote_counts):
        id_to_votes[idx] = int(vc)

    # Derive per-threshold outputs
    for threshold in range(1, pool_size + 1):
        tag = f"{prefix}-{threshold}of{pool_size}"
        out_path = output_dir / tag
        out_path.mkdir(parents=True, exist_ok=True)

        # Filter candidates by vote count
        filtered_candidates = []
        filtered_keys: set[str] = set()
        for cand in candidates:
            cid = cand["candidate_id"]
            if id_to_votes.get(cid, 0) >= threshold:
                filtered_candidates.append(cand)
                filtered_keys.add(f"candidate_{cid:05d}")

        # Filter probabilities
        filtered_results = {
            k: v for k, v in results.items()
            if k in filtered_keys
        }

        # Write filtered probabilities
        filtered_prob = {
            "source": str(probabilities_path),
            "derived_from": f"1-of-{pool_size} union",
            "vote_threshold": threshold,
            "results": filtered_results,
        }
        prob_out = out_path / "probabilities.json"
        with open(prob_out, "w", encoding="utf-8") as f:
            json.dump(filtered_prob, f, indent=2)

        # Write filtered manifest
        filtered_manifest = {
            k: v for k, v in manifest.items()
            if k != "candidates"
        }
        filtered_manifest["candidates"] = filtered_candidates
        filtered_manifest["derived_from"] = f"1-of-{pool_size} union"
        filtered_manifest["vote_threshold"] = threshold
        filtered_manifest["total_detections"] = len(filtered_candidates)
        filtered_manifest["successful_extractions"] = len(filtered_candidates)
        manifest_out = out_path / "candidate_manifest.json"
        with open(manifest_out, "w", encoding="utf-8") as f:
            json.dump(filtered_manifest, f, indent=2)

        logger.info(
            "  %s: %d candidates, %d probabilities -> %s",
            tag, len(filtered_candidates), len(filtered_results), out_path,
        )


def main() -> None:
    """Parse arguments and run derivation."""
    parser = argparse.ArgumentParser(
        description="Derive vote-threshold PV results from union verifier run",
    )
    parser.add_argument(
        "--consensus", type=Path, required=True,
        help="Path to 1-of-N consensus GeoJSON with vote_count",
    )
    parser.add_argument(
        "--probabilities", type=Path, required=True,
        help="Path to probabilities.json from union verifier run",
    )
    parser.add_argument(
        "--manifest", type=Path, required=True,
        help="Path to candidate_manifest.json from union extraction",
    )
    parser.add_argument(
        "--pool-size", type=int, required=True,
        help="Total number of runs (N) — derives thresholds 1 to N",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Base output directory (creates {prefix}-{x}of{N}/ subdirs)",
    )
    parser.add_argument(
        "--prefix", type=str, required=True,
        help="Name prefix for output subdirectories (e.g., 'image', 'text')",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()
    derive_thresholds(
        consensus_path=args.consensus,
        probabilities_path=args.probabilities,
        manifest_path=args.manifest,
        pool_size=args.pool_size,
        output_dir=args.output_dir,
        prefix=args.prefix,
    )


if __name__ == "__main__":
    main()
