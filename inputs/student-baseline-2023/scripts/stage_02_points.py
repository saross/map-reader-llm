#!/usr/bin/env python3
"""
Stage 2 — build the anonymised master point layer.

Source: raw/MapMounds17_18withnas.csv (10,827 rows, the unfiltered superset).
Output: staged/mounds-attributed.geojson — student codes only, no personal names.

Also emits a per-code / per-year count table and a FeatureTimestamp-vs-createdAtGMT
offset diagnostic to stdout (numbers only, no names).

Usage:
    .venv/bin/python stage_02_points.py
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path("/home/shawn/Code/map-reader-llm/inputs/student-baseline-2023")
RAW = ROOT / "raw"
STAGED = ROOT / "staged"

# Every column in the source export that can carry a personal name.
NAME_BEARING = ["createdBy", "modifiedBy", "FeatureAuthor"]


def norm(text: str) -> str:
    """Normalise a name token for lookup against the mapping's normalised keys."""
    return " ".join(unicodedata.normalize("NFKD", str(text)).casefold().split())


def load_lookup() -> dict[str, str]:
    """Load the normalised name-form -> student-code lookup from raw/."""
    data = json.loads((RAW / "code-mapping.json").read_text(encoding="utf-8"))
    return data["lookup_normalised"]


def main() -> None:
    STAGED.mkdir(parents=True, exist_ok=True)
    lookup = load_lookup()

    df = pd.read_csv(RAW / "MapMounds17_18withnas.csv", low_memory=False)
    assert len(df) == 10_827, f"expected 10,827 source rows, got {len(df):,}"
    assert df["identifier"].is_unique, "identifier is not unique in the source export"

    # --- membership flags against the two filtered variants ---
    allgood = set(pd.read_csv(RAW / "MapMounds17_18allgood.csv", low_memory=False)["identifier"])
    negood = set(pd.read_csv(RAW / "MapMounds17_18NEgood.csv", low_memory=False)["identifier"])

    # --- attribution -> code ---
    codes = df["createdBy"].map(lambda v: lookup.get(norm(v)) if pd.notna(v) else None)
    unresolved = df.loc[codes.isna(), "createdBy"]
    assert unresolved.empty, f"{len(unresolved)} rows have an unresolvable createdBy"

    # Cross-check: createdBy vs FeatureAuthor should agree row-by-row.
    author_codes = df["FeatureAuthor"].map(
        lambda v: lookup.get(norm(v)) if pd.notna(v) else None
    )
    author_disagree = int((codes != author_codes).sum())

    # --- timestamps ---
    created = pd.to_datetime(
        df["createdAtGMT"].str.replace(" GMT", "", regex=False), errors="coerce", utc=True
    )
    modified = pd.to_datetime(
        df["modifiedAtGMT"].str.replace(" GMT", "", regex=False), errors="coerce", utc=True
    )
    feature_ts = pd.to_datetime(df["FeatureTimestamp"], errors="coerce", utc=True)

    # FeatureTimestamp quirk diagnostic: offset from createdAtGMT, in hours.
    offset_h = (created - feature_ts).dt.total_seconds() / 3600.0

    year = created.dt.year

    out = gpd.GeoDataFrame(
        {
            "identifier": df["identifier"].astype("int64"),
            "student_code": codes,
            "created_at_gmt": created.dt.strftime("%Y-%m-%dT%H:%M:%S.%f").str[:-3] + "Z",
            "modified_at_gmt": modified.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "feature_type": df["FeatureType"],
            "map_symbol": df["MapSymbol"],
            "year": year.astype("int64"),
            "in_allgood": df["identifier"].isin(allgood),
            "in_negood": df["identifier"].isin(negood),
        },
        geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
        crs="EPSG:4326",
    )
    # Rows with no coordinates get a null geometry rather than a (0, 0) point.
    missing_xy = df["Latitude"].isna() | df["Longitude"].isna()
    out.loc[missing_xy, "geometry"] = None

    out.to_file(STAGED / "mounds-attributed.geojson", driver="GeoJSON")

    # --- reporting (counts only) ---
    print(f"rows written: {len(out):,}   null geometry: {int(missing_xy.sum()):,}")
    print(f"in_allgood True: {int(out.in_allgood.sum()):,}   "
          f"in_negood True: {int(out.in_negood.sum()):,}")
    print(f"createdBy vs FeatureAuthor code disagreements: {author_disagree}")
    print()
    tab = pd.crosstab(out.student_code, out.year, margins=True, margins_name="Total")
    print("features per student_code per year:")
    print(tab.to_string())
    print()
    print("FeatureTimestamp offset from createdAtGMT (hours):")
    print(offset_h.describe().to_string())
    print("offset value counts (rounded to nearest hour):")
    print(offset_h.round().value_counts().sort_index().to_string())
    print()
    print("null-geometry rows per student_code:")
    print(out.loc[missing_xy, "student_code"].value_counts().sort_index().to_string())
    print()
    print("feature_type counts:")
    print(out.feature_type.value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
