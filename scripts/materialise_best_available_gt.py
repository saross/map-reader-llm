#!/usr/bin/env python3
"""
Materialise the 55-map best-available ground truth as ONE artefact, in both formats.

The standardised 55-map reference already exists, but as two layers in two
formats: `student-mounds-55maps-standardised.geojson` (4,731 student records,
corrected against the review campaign) and `extension-mounds-standardised.csv`
(279 confirmed mounds the students missed). Nothing merges them.

That split has a concrete cost. Every consumer has to union the layers itself,
and `evaluate_detections.py --ground-truth` takes a single path, so the 55-map
boards cannot be scored through the generic path at all. It is why those four
boards could not be re-tiered under erratum E83 and had to be disclosed as
carrying a superseded instrument.

This script emits the union once, with provenance kept per record so nothing is
lost in the merge:

* `best-available-gt-55maps.geojson` — point geometries in EPSG:32635, ready for
  `--ground-truth`.
* `best-available-gt-55maps.csv` — the same records as a flat table.

**This is a best-possible reference, not a gold standard** (ruling 21b). Mounds
that both the students and every model missed are absent from it, because
recovering them needs a fresh survey. Its known biases travel in both directions
and are documented in the source README; they apply unchanged to this union.

Unlike the earlier `canonical-gt` extended reference, this one is
**buffer-invariant**: the standardised layers are marked centres with no ring
gate, so the same record set is correct at every matching radius. That is what
makes a single static artefact possible.

Usage::

    python scripts/materialise_best_available_gt.py

Notes:
    - Zero API spend; a pure merge of two committed layers.
    - Deterministic: re-running overwrites with identical bytes.

Created: 2026-08-19 (Session 137)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SRC = PROJECT_ROOT / "results/deployment-oracle-2026-06-06/canonical-gt/standardised"
STUDENT = SRC / "student-mounds-55maps-standardised.geojson"
EXTENSION = SRC / "extension-mounds-standardised.csv"

#: The superseded CANONICAL vintage, retained because two registered boards
#: (`55map-canonical-leaderboard-50m` and its MCC sibling) are scored against it
#: and cannot be re-tiered without a scorable copy. Unlike the standardised
#: layers this reference is buffer-GATED: a phantom enters only at radii at or
#: above the shell where the reviewer saw it. It is therefore materialised at one
#: stated radius, not as a buffer-invariant artefact, and both boards are 50 m
#: boards so 50 m is the radius that matters.
CANON_STUDENT = PROJECT_ROOT / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
CANON_REVIEW = PROJECT_ROOT / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv"
SENTINEL_BUFFER = 200
CRS = "EPSG:32635"

#: Columns carried on every record, whichever layer it came from, so a consumer
#: can filter by provenance or positional quality without rejoining the sources.
#: `source_map` rather than `map_name`: `lib_advanced_metrics.calculate_f1_internal`
#: scopes references per map sheet and requires a `Map` or `source_map` column,
#: raising otherwise. Naming it what the scorer expects is what makes this
#: artefact usable through `evaluate_detections.py --ground-truth` at all, which
#: is the whole point of merging the layers.
COMMON = ["gt_id", "layer", "source_id_lossy", "source_map", "symbol_type",
          "confidence_grade", "position_source", "provenance"]


def load_student() -> gpd.GeoDataFrame:
    """Load the standardised student layer, normalised to the common columns."""
    g = gpd.read_file(STUDENT).to_crs(CRS).reset_index(drop=True)
    # The upstream field named `uuid` holds the digitisation's RECORD
    # IDENTIFIERS after float64 precision loss, not a symbol code. The Session
    # 137 audit falsified the symbol-code diagnosis this comment previously
    # carried (audit report F5; defect D29): of 2,054 intact 19-digit uuids in
    # the raw `MapMoundsDigitised` exports, 421 round-trip through float64
    # exactly onto the values published here; the five largest buckets are
    # float rounding tiers, each spanning several distinct `MapSymbol` values
    # (the actual symbol field, 6 distinct values); and one upstream export
    # carries uuid = 1.00E+18 on every row while its sibling `ID` column is
    # fully unique. `build_student_mounds_gs4.py` had the correct diagnosis
    # all along ("uuid in the raw shapefile is float64 … lost precision").
    #
    # The field is emitted as `source_id_lossy`, which is what it is: a lossy
    # trace back towards the upstream record, unusable as a key (4,731 records
    # over 836 distinct values) but sometimes recoverable via the intact
    # upstream identifiers should provenance ever need it. `gt_id` is the
    # actual key; the 2026-08-04 census ruling stands — match on coordinates.
    out = gpd.GeoDataFrame({
        "gt_id": [f"student:{i:05d}" for i in range(len(g))],
        "layer": "student_standardised",
        "source_id_lossy": g["uuid"].astype(str),
        "source_map": g["source_map"],
        "symbol_type": g.get("std_symbol_type", g.get("FeatureType")),
        "confidence_grade": g.get("std_confidence_grade"),
        "position_source": g.get("std_position_source"),
        "provenance": g.get("std_provenance"),
    }, geometry=g.geometry, crs=CRS)
    return out


def load_extension() -> gpd.GeoDataFrame:
    """Load the extension layer, normalised to the common columns."""
    rows = list(csv.DictReader(EXTENSION.open(encoding="utf-8")))
    return gpd.GeoDataFrame({
        "gt_id": [f"extension:{r['candidate_id']}" for r in rows],
        "layer": "extension_standardised",
        # The extension layer has no upstream identifier; its candidate_id IS unique.
        "source_id_lossy": [None for _ in rows],
        "source_map": [r["map_name"] for r in rows],
        "symbol_type": [r.get("symbol_type") for r in rows],
        "confidence_grade": [r.get("confidence_grade") for r in rows],
        "position_source": [r.get("position_source") for r in rows],
        "provenance": [r.get("provenance") for r in rows],
    }, geometry=[Point(float(r["x"]), float(r["y"])) for r in rows], crs=CRS)


def load_canonical(radius: int) -> gpd.GeoDataFrame:
    """Build the canonical-vintage reference at one matching radius.

    Student layer as reviewed (4,746, pre-standardisation) plus every phantom
    whose review shell is at or below ``radius``, excluding the 200 m
    visible-but-out-of-range sentinels.

    Args:
        radius: Matching radius in metres.

    Returns:
        Point reference in the project CRS with the common columns.
    """
    g = gpd.read_file(CANON_STUDENT).to_crs(CRS).reset_index(drop=True)
    student = gpd.GeoDataFrame({
        "gt_id": [f"student:{i:05d}" for i in range(len(g))],
        "layer": "student_reviewed",
        "source_id_lossy": g["uuid"].astype(str),
        "source_map": g["source_map"],
        "symbol_type": g.get("FeatureType"),
        "confidence_grade": "as_digitised",
        "position_source": "as_digitised",
        "provenance": "student_digitised",
    }, geometry=g.geometry, crs=CRS)

    # `buffer_metres` is mixed-format in the source CSV — both "50" and "50.0"
    # occur — so parse through float before comparing. Reading it as an int
    # directly raises on the decimal rows and would silently lose them if caught.
    rows = [r for r in csv.DictReader(CANON_REVIEW.open(encoding="utf-8"))
            if r["human_label"] == "mound"
            and float(r["buffer_metres"]) != SENTINEL_BUFFER
            and float(r["buffer_metres"]) <= radius]
    phantom = gpd.GeoDataFrame({
        "gt_id": [f"phantom:{r['candidate_id']}" for r in rows],
        "layer": "phantom_canonical",
        "source_id_lossy": [None for _ in rows],
        "source_map": [r["map_name"] for r in rows],
        "symbol_type": [None for _ in rows],
        "confidence_grade": "directly_reviewed",
        "position_source": "detection_centroid",
        "provenance": [f"canonical_review_r{float(r['buffer_metres']):.0f}"
                       for r in rows],
    }, geometry=[Point(float(r["x"]), float(r["y"])) for r in rows], crs=CRS)
    return pd.concat([student, phantom], ignore_index=True)


def main() -> int:
    """Merge the two layers and write the GeoJSON and CSV.

    Returns:
        Process exit status; non-zero if the record count does not reconcile.
    """
    ap = argparse.ArgumentParser(description="Merge the 55-map best-available GT.")
    ap.add_argument("--out-dir", type=Path,
                    default=PROJECT_ROOT / "inputs/vectors/references")
    ap.add_argument("--vintage", choices=("standardised", "canonical"),
                    default="standardised")
    ap.add_argument("--radius", type=int, default=50,
                    help="Matching radius for the buffer-gated canonical vintage.")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.vintage == "canonical":
        merged = gpd.GeoDataFrame(load_canonical(args.radius), geometry="geometry",
                                  crs=CRS)
        stem = f"canonical-gt-55maps-r{args.radius}"
        student = extension = None
    else:
        student, extension = load_student(), load_extension()
        merged = gpd.GeoDataFrame(
            pd.concat([student, extension], ignore_index=True),
            geometry="geometry", crs=CRS,
        )
        stem = "best-available-gt-55maps"
        if len(merged) != len(student) + len(extension):
            logger.error("record count does not reconcile")
            return 1
    if merged["gt_id"].duplicated().any():
        logger.error("duplicate gt_id in the merged reference")
        return 1

    geo = args.out_dir / f"{stem}.geojson"
    merged.to_file(geo, driver="GeoJSON")

    table = args.out_dir / f"{stem}.csv"
    with table.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([*COMMON, "x", "y"])
        for row in merged.itertuples():
            w.writerow([row.gt_id, row.layer, row.source_id_lossy, row.source_map,
                        row.symbol_type, row.confidence_grade,
                        row.position_source, row.provenance,
                        f"{row.geometry.x:.3f}", f"{row.geometry.y:.3f}"])

    if student is not None:
        logger.info("student layer   : %d", len(student))
        logger.info("extension layer : %d", len(extension))
    logger.info("merged          : %d", len(merged))
    logger.info("wrote %s", geo.relative_to(PROJECT_ROOT))
    logger.info("wrote %s", table.relative_to(PROJECT_ROOT))

    counts = merged.groupby(["layer", "confidence_grade"], dropna=False).size()
    for (layer, grade), n in counts.items():
        logger.info("  %-24s %-20s %5d", layer, grade, n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
