#!/usr/bin/env python3
"""
Stage 4 — per-sheet census and cross-student overlap analysis on a TRUE
(non-overlapping) 1:50,000 Soviet-nomenclature sheet grid.

Supersedes the raster-footprint sheet assignment used in the first pass: the
local GeoTIFFs are axis-aligned bounding boxes in EPSG:32635 and overlap their
neighbours by ~15 %, which mis-attributes every sheet-edge feature.

Outputs:
    staged/sheet-student-census.csv
    staged/cross-student-proximity-pairs.csv
    staged/double-surveyed-zones.csv

Usage:
    .venv/bin/python stage_04_census.py
"""

from __future__ import annotations

import glob
import itertools
import os
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheetgrid  # noqa: E402

REPO = Path("/home/shawn/Code/map-reader-llm")
ROOT = REPO / "inputs/student-baseline-2023"
RAW = ROOT / "raw"
STAGED = ROOT / "staged"
METRIC = "EPSG:32635"
PROX_M = 50.0
COVER_BUFFER_M = 250.0   # per-student coverage footprint radius


def rule(t: str) -> None:
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def main() -> None:
    pts = gpd.read_file(STAGED / "mounds-attributed.geojson")
    pts = pts[~pts.geometry.isna()].copy()

    # ---- sheet grid, restricted to cells that actually contain data ----
    grid = sheetgrid.build()
    # settlement aliases from the local raster filenames, where available
    alias = {}
    for p in glob.glob(str(REPO / "inputs/rasters/Russian1981_32635/*.tif")):
        stem = os.path.basename(p)[:-4]
        parts = stem.split("_")
        if len(parts) > 1 and not parts[1].isdigit():
            alias[parts[0]] = parts[1]
    for p in glob.glob(str(REPO / "inputs/rasters/*.tif")):
        stem = os.path.basename(p)[:-4]
        parts = stem.split("_")
        if len(parts) > 1 and not parts[1].isdigit():
            alias[parts[0]] = parts[1]

    j = gpd.sjoin(pts, grid, how="left", predicate="within")
    assert len(j) == len(pts), "a point matched more than one grid cell"
    unassigned = int(j.sheet.isna().sum())
    pts["sheet"] = j["sheet"].values
    pts["sheet_alias"] = pts["sheet"].map(lambda s: alias.get(s, ""))
    pts_m = pts.to_crs(METRIC)

    rule("TASK 5c / 6b — sheet coverage on the true 1:50k graticule")
    print(f"points with geometry: {len(pts):,}   unassigned to any K-35 cell: {unassigned}")
    print(f"distinct 1:50k sheets containing at least one point: {pts.sheet.nunique()}")
    for thresh in (1, 2, 3, 5, 10, 20, 50):
        n = int((pts.sheet.value_counts() >= thresh).sum())
        print(f"  sheets with >= {thresh:>3} points: {n}")
    print("\nsheets with fewer than 10 points (likely edge bleed / stray records):")
    small = pts.sheet.value_counts()
    small = small[small < 10]
    for s, n in small.items():
        codes = sorted(pts.loc[pts.sheet == s, "student_code"].unique())
        print(f"  {s:<14} {n:>4}  codes={codes}")
    print("\ndistinct sheets by season:")
    for y in (2017, 2018):
        sub = pts[pts.year == y]
        vc = sub.sheet.value_counts()
        print(f"  {y}: {sub.sheet.nunique()} sheets with >=1 point; "
              f"{int((vc >= 10).sum())} with >=10 points")
    print(f"  sheets worked in BOTH seasons: "
          f"{len(set(pts[pts.year == 2017].sheet) & set(pts[pts.year == 2018].sheet))}")

    # ---- census ----
    rule("TASK 6b — per-sheet feature counts by student code")
    census = pts.groupby(["sheet", "student_code"]).size().unstack(fill_value=0)
    census.insert(0, "sheet_alias", [alias.get(s, "") for s in census.index])
    code_cols = [c for c in census.columns if c != "sheet_alias"]
    census["total"] = census[code_cols].sum(axis=1)
    census["n_codes"] = (census[code_cols] > 0).sum(axis=1)
    # a "substantive" contribution: at least 5 features on the sheet
    census["n_codes_ge5"] = (census[code_cols] >= 5).sum(axis=1)
    census["n_codes_ge20"] = (census[code_cols] >= 20).sum(axis=1)
    census = census.sort_values("total", ascending=False)
    census.to_csv(STAGED / "sheet-student-census.csv")

    print(f"sheets touched by 2+ codes (any count):     "
          f"{int((census.n_codes >= 2).sum())}")
    print(f"sheets with 2+ codes each contributing >=5:  "
          f"{int((census.n_codes_ge5 >= 2).sum())}")
    print(f"sheets with 2+ codes each contributing >=20: "
          f"{int((census.n_codes_ge20 >= 2).sum())}")
    print("\nsheets where two or more codes each contributed >= 20 features:")
    sub = census[census.n_codes_ge20 >= 2]
    print(sub.loc[:, ["sheet_alias"] + code_cols + ["total", "n_codes"]]
          .loc[:, lambda d: (d != 0).any(axis=0)].to_string())
    print("\nsheets where two or more codes each contributed >= 5 features:")
    sub5 = census[(census.n_codes_ge5 >= 2)]
    print(sub5.loc[:, ["sheet_alias"] + code_cols + ["total", "n_codes"]]
          .loc[:, lambda d: (d != 0).any(axis=0)].to_string())

    # ---- proximity ----
    rule(f"TASK 6c — cross-student point pairs within {PROX_M:.0f} m")
    idx = pts_m.sindex
    arr = pts_m.reset_index(drop=True)
    seen: set[tuple[int, int]] = set()
    rows = []
    for pos, row in enumerate(arr.itertuples(index=False)):
        for other in idx.query(row.geometry.buffer(PROX_M), predicate="intersects"):
            if other == pos:
                continue
            o = arr.iloc[other]
            if o.student_code == row.student_code:
                continue
            key = tuple(sorted((int(row.identifier), int(o.identifier))))
            if key in seen:
                continue
            seen.add(key)
            a, b = (row, o) if int(row.identifier) == key[0] else (o, row)
            rows.append({
                "identifier_a": key[0], "identifier_b": key[1],
                "code_a": a.student_code, "code_b": b.student_code,
                "distance_m": round(row.geometry.distance(o.geometry), 2),
                "sheet": row.sheet if pd.notna(row.sheet) else o.sheet,
                "sheet_alias": alias.get(row.sheet, ""),
                "year_a": int(a.year), "year_b": int(b.year),
                "symbol_a": a.map_symbol, "symbol_b": b.map_symbol,
            })
    px = pd.DataFrame(rows)
    px["pair"] = [f"{min(a, b)}-{max(a, b)}" for a, b in zip(px.code_a, px.code_b)]
    px = px.sort_values(["sheet", "distance_m"])
    px.to_csv(STAGED / "cross-student-proximity-pairs.csv", index=False)

    print(f"cross-student pairs within {PROX_M:.0f} m: {len(px):,}")
    print(f"distinct points involved: {len(set(px.identifier_a) | set(px.identifier_b)):,}")
    print("\nper student-code pair:")
    print(px.pair.value_counts().to_string())
    print("\nper sheet:")
    print(px.groupby(["sheet", "sheet_alias"]).size().to_string())
    print("\ndistance bands (m):")
    print(pd.cut(px.distance_m, [0, 5, 10, 15, 20, 30, 40, 50], include_lowest=True)
          .value_counts().sort_index().to_string())
    print("\nsame-symbol vs different-symbol within pairs:")
    print((px.symbol_a == px.symbol_b).value_counts().to_string())

    # wider thresholds, for context
    print("\ncross-student pair counts at wider thresholds:")
    for t in (25, 50, 100, 200, 500, 1000):
        n = 0
        seen2: set[tuple[int, int]] = set()
        for pos, row in enumerate(arr.itertuples(index=False)):
            for other in idx.query(row.geometry.buffer(t), predicate="intersects"):
                if other == pos:
                    continue
                o = arr.iloc[other]
                if o.student_code == row.student_code:
                    continue
                key = tuple(sorted((int(row.identifier), int(o.identifier))))
                if key in seen2:
                    continue
                seen2.add(key)
                n += 1
        print(f"  <= {t:>5} m: {n:,} pairs")

    # ---- double-surveyed zones ----
    rule("TASK 6c — genuinely double-surveyed zones "
         f"({COVER_BUFFER_M:.0f} m coverage footprints)")
    zrows = []
    for sheet, grp in pts_m.groupby("sheet"):
        codes = sorted(grp.student_code.unique())
        if len(codes) < 2:
            continue
        foot = {c: grp[grp.student_code == c].buffer(COVER_BUFFER_M).union_all()
                for c in codes}
        for ca, cb in itertools.combinations(codes, 2):
            g = foot[ca].intersection(foot[cb])
            if g.is_empty or g.area <= 0:
                continue
            inzone = grp[grp.within(g)]
            zrows.append({
                "sheet": sheet,
                "sheet_alias": alias.get(sheet, ""),
                "code_a": ca, "code_b": cb,
                "n_a_on_sheet": int((grp.student_code == ca).sum()),
                "n_b_on_sheet": int((grp.student_code == cb).sum()),
                "zone_km2": round(g.area / 1e6, 3),
                "points_in_zone": len(inzone),
                "points_in_zone_a": int((inzone.student_code == ca).sum()),
                "points_in_zone_b": int((inzone.student_code == cb).sum()),
            })
    z = pd.DataFrame(zrows).sort_values("zone_km2", ascending=False)
    z.to_csv(STAGED / "double-surveyed-zones.csv", index=False)
    print(f"code-pair x sheet combinations with a non-empty overlap zone: {len(z)}")
    print(f"total double-surveyed area: {z.zone_km2.sum():.1f} sq km")
    print(f"total features sitting inside a double-surveyed zone: "
          f"{int(z.points_in_zone.sum())}")
    print("\ntop 25 zones by area:")
    print(z.head(25).to_string(index=False))
    print("\nzone area by code pair:")
    print(z.groupby(z.apply(lambda r: f"{r.code_a}-{r.code_b}", axis=1))
          .agg(sheets=("sheet", "nunique"), zone_km2=("zone_km2", "sum"),
               points=("points_in_zone", "sum")).sort_values("zone_km2", ascending=False)
          .to_string())

    # ---- within-student near-duplicates, for comparison ----
    # The paper reports 6 "double-marked" features, all from one student on one
    # sheet. Those are WITHIN-student duplicates, a different phenomenon from the
    # cross-student overlap above; recomputing them here validates the pipeline.
    rule(f"Comparison — WITHIN-student point pairs within {PROX_M:.0f} m")
    seen3: set[tuple[int, int]] = set()
    same = []
    for pos, row in enumerate(arr.itertuples(index=False)):
        for other in idx.query(row.geometry.buffer(PROX_M), predicate="intersects"):
            if other == pos:
                continue
            o = arr.iloc[other]
            if o.student_code != row.student_code:
                continue
            key = tuple(sorted((int(row.identifier), int(o.identifier))))
            if key in seen3:
                continue
            seen3.add(key)
            same.append({
                "identifier_a": key[0], "identifier_b": key[1],
                "student_code": row.student_code,
                "distance_m": round(row.geometry.distance(o.geometry), 2),
                "sheet": row.sheet, "sheet_alias": alias.get(row.sheet, ""),
                "same_symbol": row.map_symbol == o.map_symbol,
            })
    sm = pd.DataFrame(same).sort_values(["student_code", "distance_m"])
    sm.to_csv(STAGED / "within-student-proximity-pairs.csv", index=False)
    print(f"within-student pairs within {PROX_M:.0f} m: {len(sm)}")
    print(sm.student_code.value_counts().to_string())
    print("\non the audited Rakovski sheet (K-35-062-2):")
    print(sm[sm.sheet == "K-35-062-2"].groupby("student_code").size().to_string())


if __name__ == "__main__":
    main()
