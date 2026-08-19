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
CRS = "EPSG:32635"

#: Columns carried on every record, whichever layer it came from, so a consumer
#: can filter by provenance or positional quality without rejoining the sources.
COMMON = ["gt_id", "layer", "source_id", "map_name", "symbol_type",
          "confidence_grade", "position_source", "provenance"]


def load_student() -> gpd.GeoDataFrame:
    """Load the standardised student layer, normalised to the common columns."""
    g = gpd.read_file(STUDENT).to_crs(CRS).reset_index(drop=True)
    # `uuid` is NOT unique in this layer and must not be used as a key: 4,731
    # records carry 836 distinct values, one of them 1,149 times. The duplication
    # is upstream — the original reviewed layer has 4,746 records over 839
    # uuids — and the geometries are all distinct, so these are genuine separate
    # features whose identifier field simply does not identify them. The key here
    # is therefore positional, with `uuid` retained as an attribute so nothing is
    # lost and nobody is misled.
    out = gpd.GeoDataFrame({
        "gt_id": [f"student:{i:05d}" for i in range(len(g))],
        "layer": "student_standardised",
        "source_id": g["uuid"].astype(str),
        "map_name": g["source_map"],
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
        "source_id": [r["candidate_id"] for r in rows],
        "map_name": [r["map_name"] for r in rows],
        "symbol_type": [r.get("symbol_type") for r in rows],
        "confidence_grade": [r.get("confidence_grade") for r in rows],
        "position_source": [r.get("position_source") for r in rows],
        "provenance": [r.get("provenance") for r in rows],
    }, geometry=[Point(float(r["x"]), float(r["y"])) for r in rows], crs=CRS)


def main() -> int:
    """Merge the two layers and write the GeoJSON and CSV.

    Returns:
        Process exit status; non-zero if the record count does not reconcile.
    """
    ap = argparse.ArgumentParser(description="Merge the 55-map best-available GT.")
    ap.add_argument("--out-dir", type=Path,
                    default=PROJECT_ROOT / "inputs/vectors/references")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    student, extension = load_student(), load_extension()
    merged = gpd.GeoDataFrame(
        pd.concat([student, extension], ignore_index=True),
        geometry="geometry", crs=CRS,
    )

    if len(merged) != len(student) + len(extension):
        logger.error("record count does not reconcile")
        return 1
    if merged["gt_id"].duplicated().any():
        logger.error("duplicate gt_id in the merged reference")
        return 1

    geo = args.out_dir / "best-available-gt-55maps.geojson"
    merged.to_file(geo, driver="GeoJSON")

    table = args.out_dir / "best-available-gt-55maps.csv"
    with table.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([*COMMON, "x", "y"])
        for row in merged.itertuples():
            w.writerow([row.gt_id, row.layer, row.source_id, row.map_name,
                        row.symbol_type, row.confidence_grade,
                        row.position_source, row.provenance,
                        f"{row.geometry.x:.3f}", f"{row.geometry.y:.3f}"])

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
