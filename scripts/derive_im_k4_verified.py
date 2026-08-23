#!/usr/bin/env python3
"""Derive the genuine IM-k4 verified detection set (PI ruling 2026-08-23).

The image generalisation run's production pipeline built its consensus at
vote_threshold = 3 (``consensus-3of5.geojson``) and verified THAT set, so —
unlike the three text runs — no 4-of-5 cell ever existed for the image
track. Because the verifier's verdicts already cover every 3-of-5
candidate and each verified detection carries its ``vote_count``, the
4-of-5 set is a pure filter over the verified detections: keep
``vote_count >= 4``. Zero Application Programming Interface (API) spend;
no re-verification.

Gates (the script refuses to write on any failure):

* every output ``candidate_id`` exists in the input (strict subset);
* every output row has ``vote_count >= 4``;
* the output count equals the input's vote-histogram mass at >= 4;
* the input is the expected k3 population (4,680 rows — the registered
  IM-k3 cell's ``n_detections``), so a changed upstream file cannot be
  filtered silently.

Context: the Session 138 "IM-k4 gap cell" scored the k3 set under a k4
label and is archived at ``archive/superseded-mislabelled-im-k4/``; this
script mints the real thing. Scoring happens separately with
``evaluate_detections.py`` against the standardised (best-available)
reference, mirroring the IM-k3 sibling's parameters.

Usage::

    python scripts/derive_im_k4_verified.py            # dry run, gates only
    python scripts/derive_im_k4_verified.py --write

$0 API. Trivial compute; any machine.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE = (PROJECT_ROOT
          / "outputs/55maps-image-generalisation/verified/"
            "verified_detections.geojson")
DEST = (PROJECT_ROOT
        / "results/55maps-standardised-ref-2026-08-14/IM-k4/"
          "k4_verified_detections.geojson")
EXPECTED_K3_COUNT = 4680  # registered IM-k3 n_detections
VOTE_THRESHOLD = 4


def filter_k4(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Return the ``vote_count >= 4`` subset of a verified detection set.

    Args:
        gdf: Verified detections carrying a ``vote_count`` column.

    Returns:
        The filtered GeoDataFrame (original row order preserved).

    Raises:
        ValueError: if ``vote_count`` is missing.
    """
    if "vote_count" not in gdf.columns:
        raise ValueError("input carries no vote_count column")
    return gdf[gdf["vote_count"] >= VOTE_THRESHOLD]


def main() -> int:
    """Derive, gate, and (with ``--write``) materialise the k4 set."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="Write the k4 GeoJSON after the gates pass.")
    args = ap.parse_args()

    gdf = gpd.read_file(SOURCE)
    if len(gdf) != EXPECTED_K3_COUNT:
        print(f"GATE FAIL: input has {len(gdf)} rows, expected "
              f"{EXPECTED_K3_COUNT} (the registered IM-k3 population)")
        return 1
    k4 = filter_k4(gdf)

    hist_mass = int((gdf["vote_count"] >= VOTE_THRESHOLD).sum())
    subset_ok = set(k4["candidate_id"]).issubset(set(gdf["candidate_id"]))
    votes_ok = bool((k4["vote_count"] >= VOTE_THRESHOLD).all())
    count_ok = len(k4) == hist_mass
    print(f"input (k3 verified): {len(gdf)}")
    print(f"k4 (vote_count >= {VOTE_THRESHOLD}): {len(k4)}")
    print(f"gates: subset={subset_ok} votes={votes_ok} count={count_ok}")
    if not (subset_ok and votes_ok and count_ok):
        print("GATE FAIL: refusing to write")
        return 1
    if args.write:
        DEST.parent.mkdir(parents=True, exist_ok=True)
        k4.to_file(DEST, driver="GeoJSON")
        print(f"wrote {DEST.relative_to(PROJECT_ROOT)}")
    else:
        print("dry run — pass --write to materialise")
    return 0


if __name__ == "__main__":
    sys.exit(main())
