#!/usr/bin/env python3
"""
Stage 3 — assignment/audit-area polygons, the QA error layer, and the
sheet <-> student verification.

Outputs (all anonymised, student codes only):
    staged/assignment-areas.geojson
    staged/qa-errors.geojson

Task 6 (the overlap census) lives in stage_04_census.py, which uses a true
Soviet-nomenclature graticule rather than the overlapping raster footprints.

Usage:
    .venv/bin/python stage_03_spatial.py
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheetgrid  # noqa: E402

REPO = Path("/home/shawn/Code/map-reader-llm")
ROOT = REPO / "inputs/student-baseline-2023"
RAW = ROOT / "raw"
STAGED = ROOT / "staged"
METRIC = "EPSG:32635"   # WGS 84 / UTM zone 35N — the project's metric CRS


def norm(text: str) -> str:
    """Normalise a name token for lookup against the mapping's normalised keys."""
    return " ".join(unicodedata.normalize("NFKD", str(text)).casefold().split())


def code_of(value, lookup: dict[str, str]) -> str | None:
    """Map an arbitrary name form to a student code, or None."""
    return lookup.get(norm(value)) if isinstance(value, str) else None


def rule(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def main() -> None:
    STAGED.mkdir(parents=True, exist_ok=True)
    lookup = json.loads((RAW / "code-mapping.json").read_text(encoding="utf-8"))[
        "lookup_normalised"
    ]

    pts = gpd.read_file(STAGED / "mounds-attributed.geojson")
    pts_m = pts[~pts.geometry.isna()].to_crs(METRIC)

    # ==================================================================
    # TASK 3 — assignment / audit-area polygons
    # ==================================================================
    rule("TASK 3 — Analysis-areas-by-student.shp")
    areas = gpd.read_file(RAW / "Analysis-areas-by-student.shp")
    areas["student_code"] = areas["Student"].map(lambda v: code_of(v, lookup))
    assert areas["student_code"].notna().all(), "unmapped Student value in the area layer"
    # The Student label distinguishes full audit areas from three sub-polygons
    # that mark contiguous sections a student failed to digitise.
    areas["area_role"] = [
        "missed_swath" if "missed" in norm(s) else "audit_area" for s in areas["Student"]
    ]
    areas_m = areas.to_crs(METRIC)
    areas["area_km2"] = (areas_m.area / 1e6).round(3)

    gs = gpd.read_file(REPO / "inputs/vectors/bounds/gs-4maps-sheet-bounds.geojson").to_crs(METRIC)
    best_sheet, best_share = [], []
    for geom in areas_m.geometry:
        top, top_a = None, 0.0
        for _, s in gs.iterrows():
            a = geom.intersection(s.geometry).area
            if a > top_a:
                top, top_a = s.sheet_id, a
        best_sheet.append(top)
        best_share.append(round(top_a / geom.area, 4) if geom.area else 0.0)
    areas["sheet_id"] = best_sheet
    areas["share_of_polygon_in_sheet"] = best_share

    out_areas = areas[
        ["id", "student_code", "area_role", "sheet_id", "share_of_polygon_in_sheet",
         "area_km2", "geometry"]
    ].copy()
    out_areas.to_file(STAGED / "assignment-areas.geojson", driver="GeoJSON")
    print(out_areas.drop(columns="geometry").to_string(index=False))
    print(f"\npolygons: {len(areas)}   distinct student codes: "
          f"{sorted(areas.student_code.unique())}")
    print("codes in the cohort with NO polygon: "
          f"{sorted(set(pts.student_code.unique()) - set(areas.student_code))}")

    rule("TASK 3 — inside-fraction cross-check")
    union_by_code = areas_m.dissolve(by="student_code").geometry
    rows = []
    for code, geom in union_by_code.items():
        own = pts_m[pts_m.student_code == code]
        inside_own = int(own.within(geom).sum())
        allin = pts_m[pts_m.within(geom)]
        rows.append({
            "student_code": code,
            "polygon_km2": round(geom.area / 1e6, 1),
            "own_points_total": len(own),
            "own_points_inside": inside_own,
            "frac_own_inside": round(inside_own / len(own), 4) if len(own) else None,
            "all_points_inside": len(allin),
            "of_which_own": int((allin.student_code == code).sum()),
            "purity": round((allin.student_code == code).mean(), 4) if len(allin) else None,
            "other_codes_present": sorted(set(allin.student_code) - {code}),
        })
    print(pd.DataFrame(rows).to_string(index=False))

    # audit-area purity restricted to the audit_area role (excludes nested swaths)
    print("\npurity of each individual audit polygon:")
    for _, a in areas_m.iterrows():
        inside = pts_m[pts_m.within(a.geometry)]
        vc = dict(sorted(inside.student_code.value_counts().items()))
        print(f"  id={a.id:<4} code={a.student_code:<9} role={a.area_role:<13} "
              f"n={len(inside):<5} by_code={vc}")

    # ==================================================================
    # TASK 4 — QA error layer
    # ==================================================================
    rule("TASK 4 — QA-errors-SAR CRS determination and staging")
    qa = gpd.read_file(RAW / "QA-errors-SAR.shp")
    b = qa.total_bounds
    print(f"declared CRS: {qa.crs}")
    print(f"coordinate ranges: x {b[0]:.5f} .. {b[2]:.5f}   y {b[1]:.5f} .. {b[3]:.5f}")
    assert -180 <= b[0] <= 180 and -90 <= b[1] <= 90, "coordinates are not degrees"
    qa = qa.set_crs("EPSG:4326", allow_override=True)
    print("assigned CRS: EPSG:4326 — the values are decimal degrees inside the "
          "Bulgarian envelope (lon 24-27 E, lat 41-43 N); EPSG:32635 for the same "
          "ground would read ~380000-480000 E / ~4650000-4770000 N.")

    qa["student_code_recorder"] = qa["Recorder"].map(lambda v: code_of(v, lookup))
    assert qa["student_code_recorder"].notna().all(), "unmapped Recorder value"
    sheet_norm = {
        "k-35-053-3_elenovo": "K-35-053-3_Elenovo",
        "n-35-053-3_elenovo": "K-35-053-3_Elenovo",   # leading N- for K-
        "k-35-053-3_elhovo": "K-35-053-3_Elenovo",    # wrong settlement suffix
        "k-35-052-4_32635": "K-35-052-4_32635",
        "k-35-062-2_rakovski": "K-35-062-2_Rakovski",
        "k-35-078-1_lesovo": "K-35-078-1_Lesovo",
    }
    qa["sheet_id"] = qa["Map"].map(lambda v: sheet_norm[norm(v)])
    qa["map_label_corrected"] = qa["Map"] != qa["sheet_id"]
    qa["year_recorded_raw"] = qa["Year"]

    # Spatial re-attribution against the audit polygons — authoritative where it
    # disagrees with the Recorder attribute (see STAGING.md).
    qa_m = qa.to_crs(METRIC)
    spatial = []
    for geom in qa_m.geometry:
        hit = None
        for _, a in areas_m.iterrows():
            if a.area_role == "audit_area" and geom.within(a.geometry):
                hit = a.student_code
                break
        spatial.append(hit)
    qa["student_code_spatial"] = spatial
    qa["student_code"] = qa["student_code_spatial"].fillna(qa["student_code_recorder"])

    qa_out = qa[[
        "AUTO", "Symbol", "ErrorType", "student_code", "student_code_recorder",
        "student_code_spatial", "sheet_id", "map_label_corrected",
        "year_recorded_raw", "Note", "geometry",
    ]].rename(columns={
        "AUTO": "error_id", "Symbol": "symbol", "ErrorType": "error_type", "Note": "note",
    })
    qa_out["error_id"] = qa_out["error_id"].astype("int64")
    qa_out.to_file(STAGED / "qa-errors.geojson", driver="GeoJSON")

    print(f"\nstaged {len(qa_out)} QA error points")
    print("\nstaged attribute schema:")
    for c, d in qa_out.dtypes.items():
        print(f"  {c}: {d}")
    print("\nerror_type x sheet_id:")
    print(pd.crosstab(qa_out.error_type, qa_out.sheet_id, margins=True).to_string())
    print("\nRecorder-attribute code x sheet_id:")
    print(pd.crosstab(qa_out.student_code_recorder, qa_out.sheet_id, margins=True).to_string())
    print("\nspatial (audit-polygon) code x sheet_id:")
    print(pd.crosstab(qa_out.student_code_spatial, qa_out.sheet_id, margins=True).to_string())
    print("\nRecorder attribute vs spatial attribution:")
    print(pd.crosstab(qa_out.student_code_recorder, qa_out.student_code_spatial).to_string())
    print("\nsymbol counts:")
    print(qa_out.symbol.value_counts().to_string())
    print(f"\nMap labels needing normalisation: {int(qa_out.map_label_corrected.sum())}")
    print(f"Year values as recorded: {sorted(qa_out.year_recorded_raw.unique())}")

    # ==================================================================
    # TASK 5 — sheet <-> student verification
    # ==================================================================
    rule("TASK 5a — MapDigitisation log, sheets per student code")
    log = pd.read_csv(RAW / "MapDigitisation__Sheet1.csv", skiprows=2, engine="python")
    log = log.dropna(subset=["Firstname"]).copy()
    log["student_code"] = log["Firstname"].map(lambda v: code_of(v, lookup))
    assert log["student_code"].notna().all(), "unmapped Firstname in the log"
    log["sheet_label"] = log["MapJKey"].fillna(log["MapName"])
    log["Start#"] = log["Start#"].astype("int64")
    log["End#"] = log["End#"].astype("int64")

    # Resolve each log batch to a graticule cell via its identifier range.
    grid = sheetgrid.build()
    pj = gpd.sjoin(pts[~pts.geometry.isna()], grid, how="left", predicate="within")
    ident_to_cell = dict(zip(pj.identifier, pj.sheet))
    modal, found = [], []
    for _, r in log.iterrows():
        sub = [ident_to_cell.get(i) for i in range(r["Start#"], r["End#"] + 1)]
        sub = [s for s in sub if isinstance(s, str)]
        found.append(len(sub))
        modal.append(pd.Series(sub).mode().iloc[0] if sub else None)
    log["cell"] = modal
    log["points_found"] = found

    print(f"log rows (excluding the trailing totals row): {len(log)}")
    print(f"distinct sheet labels in the log: {log.sheet_label.nunique()}")
    print(f"distinct graticule cells the log resolves to: {log.cell.nunique()}")
    print(f"log Points# sum: {int(log['Points#'].sum()):,}")
    print(f"identifier span of the log: {log['Start#'].min()}..{log['End#'].max()}")
    print(f"seasons represented in the log: "
          f"{sorted(pts[pts.identifier.isin(range(log['Start#'].min(), log['End#'].max() + 1))].year.unique())}")
    print("\nsheets per student code (from the log):")
    print(log.groupby("student_code").agg(
        log_rows=("sheet_label", "size"),
        distinct_labels=("sheet_label", "nunique"),
        distinct_cells=("cell", "nunique"),
        logged_points=("Points#", "sum"),
    ).to_string())
    print("\nsheet cell -> codes (log):")
    for cell, grp in log.groupby("cell"):
        codes = sorted(set(grp.student_code))
        labels = sorted(set(grp.sheet_label))
        flag = "   <-- MULTI-CODE" if len(codes) > 1 else ""
        print(f"  {cell:<12} codes={codes} labels={labels}{flag}")

    print("\nlog labels that resolve to more than one cell (label/cell slips):")
    for label, grp in log.groupby("sheet_label"):
        cells = sorted(set(grp.cell.dropna()))
        if len(cells) > 1:
            print(f"  '{label}' -> {cells}")

    rule("TASK 5b — the four audited GS sheets")
    audit = areas[areas.area_role == "audit_area"]
    for sheet_id in sorted(gs.sheet_id):
        poly = gs[gs.sheet_id == sheet_id].geometry.iloc[0]
        inside = pts_m[pts_m.within(poly)]
        by_code = dict(sorted(inside.student_code.value_counts().items()))
        pol = audit[audit.sheet_id == sheet_id]
        print(f"\n{sheet_id}")
        print(f"  points inside the sheet footprint : {len(inside)}  by_code={by_code}")
        print(f"  audit polygons on this sheet      : "
              f"{[(int(r.id), r.student_code, r.area_km2) for _, r in pol.iterrows()]}")
        qs = qa_out[qa_out.sheet_id == sheet_id]
        print(f"  QA errors                         : {len(qs)}  "
              f"recorder={dict(sorted(qs.student_code_recorder.value_counts().items()))}  "
              f"spatial={dict(sorted(qs.student_code_spatial.value_counts().items()))}")
        lg = log[log.cell == sheet_id.split('_')[0]]
        print(f"  MapDigitisation log rows          : "
              f"{[(r.sheet_label, r.student_code, int(r['Points#'])) for _, r in lg.iterrows()]}")

    rule("TASK 5 — log identifier ranges vs createdBy attribution")
    idmap: dict[int, tuple[str, str]] = {}
    conflicts = 0
    for _, r in log.iterrows():
        for ident in range(r["Start#"], r["End#"] + 1):
            if ident in idmap and idmap[ident][1] != r["student_code"]:
                conflicts += 1
            idmap[ident] = (r["sheet_label"], r["student_code"])
    p2 = pts.copy()
    p2["log_code"] = p2.identifier.map(lambda i: idmap.get(i, (None, None))[1])
    cov = p2.log_code.notna()
    agree = p2.loc[cov, "log_code"] == p2.loc[cov, "student_code"]
    print(f"points covered by a log identifier range: {int(cov.sum()):,} / {len(p2):,}")
    print(f"log code agrees with createdBy code: {int(agree.sum()):,} ({agree.mean():.3%})")
    print(f"disagreements: {int((~agree).sum()):,}")
    print(f"identifiers claimed by two log rows with different codes: {conflicts}")
    dis = p2.loc[cov][~agree.reindex(p2.loc[cov].index, fill_value=True)]
    if len(dis):
        print("\ndisagreement pattern (log code -> createdBy code):")
        print(pd.crosstab(dis.log_code, dis.student_code).to_string())


if __name__ == "__main__":
    main()
