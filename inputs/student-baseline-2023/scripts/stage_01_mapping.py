#!/usr/bin/env python3
"""
Stage 1 — build the de-anonymisation key for the 2023 participatory-GIS baseline.

Reads the Student-coding-sheet CSVs (which carry the paper's Student A…I codes
against volunteer personal names) plus every other raw file that carries a name
form, and writes a single reconciled mapping.

The mapping is written ONLY to the gitignored raw/ directory. It is the one
artefact in this staging run that is permitted to contain personal names.

Usage:
    .venv/bin/python stage_01_mapping.py
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import pandas as pd

RAW = Path("/home/shawn/Code/map-reader-llm/inputs/student-baseline-2023/raw")
OUT = RAW / "code-mapping.json"


def norm(text: str) -> str:
    """Normalise a name token for matching: NFKD, casefold, collapse whitespace."""
    text = unicodedata.normalize("NFKD", str(text))
    return " ".join(text.casefold().split())


def main() -> None:
    # --- authoritative code -> person, from the coding sheet's student-data tab ---
    sd = pd.read_csv(RAW / "Student-coding-sheet__student-data.csv", skiprows=5)
    sd = sd.dropna(subset=["Code"])
    sd = sd[sd["Code"].str.startswith("Student", na=False)]

    # canonical short codes: "Student A" -> "A"
    records: dict[str, dict] = {}
    for _, row in sd.iterrows():
        code = row["Code"].split()[-1].strip()
        surname = str(row["Surname"]).strip()
        given = str(row["Given name"]).strip()
        records[code] = {
            "code": code,
            "paper_label": row["Code"].strip(),
            "season": int(row["Year"]),
            "role": "volunteer",
            "canonical_name": f"{given} {surname}",
            "surname": surname,
            "given_name": given,
            "name_forms": set(),
        }

    # --- gather every observed name form from every raw file ---
    def add(code: str, form: str) -> None:
        if isinstance(form, str) and form.strip():
            records[code]["name_forms"].add(form.strip())

    # Index by normalised surname / given name / full name for fuzzy reconciliation.
    # Rebuilt after the staff record is added.
    by_full: dict[str, str] = {}
    by_surname: dict[str, str] = {}
    by_given: dict[str, str] = {}

    def reindex() -> None:
        by_full.clear()
        by_surname.clear()
        by_given.clear()
        by_full.update({norm(r["canonical_name"]): c for c, r in records.items()})
        by_surname.update({norm(r["surname"]): c for c, r in records.items()})
        by_given.update({norm(r["given_name"]): c for c, r in records.items()})

    reindex()

    # Hand-declared variants that normalisation alone cannot bridge (nicknames,
    # abbreviations, initials, and role labels).
    manual = {
        "steph": "A",
        "sam": "B",
        "lach": "C",
        "zac": "E",        # diminutive of the given name recorded for Student E
        "as": "TESTER-1",  # initials, used in the RecordingProgress hours tabs
        "staff tester": "TESTER-1",
        "tester": "TESTER-1",
    }
    # Non-name boilerplate that appears in the same spreadsheet columns as names
    # (markdown separators, block sub-headers, roll-up labels).
    boilerplate = {
        ":-:", "cumulative", "overall", "volunteer", "total", "totals",
        "map digitisation rate (maps per hour)", "time per feature (seconds)",
        "error rate", "student", "missed partial rows", "features identified",
        "notes", "nan",
    }
    fuzzy_bridged: list[tuple[str, str]] = []

    def resolve(form: str) -> str | None:
        """Best-effort resolution of an arbitrary name form to a code."""
        n = norm(form)
        if not n:
            return None
        if n in by_full:
            return by_full[n]
        if n in manual:
            return manual[n]
        # the paper's own labels, e.g. "Student A"
        for code, rec in records.items():
            if n == norm(rec["paper_label"]) and rec["role"] == "volunteer":
                return code
        toks = n.replace(",", " ").replace("(", " ").replace(")", " ").split()
        # trailing-digit forms such as "<full name><count>" in the Volunteers tab
        stripped = n.rstrip("0123456789").strip()
        if stripped and stripped in by_full:
            return by_full[stripped]
        # surname match (all surnames in this cohort are unique)
        for t in toks:
            if t in by_surname:
                return by_surname[t]
        # given-name match
        for t in toks:
            if t in by_given:
                return by_given[t]
        # near-miss on surname or given name (single-character substitution) —
        # catches spelling variants between the coding sheet and the point data
        for t in toks:
            if len(t) < 4:
                continue
            for table in (by_surname, by_given):
                for key, code in table.items():
                    if len(key) == len(t) and sum(a != b for a, b in zip(key, t)) == 1:
                        fuzzy_bridged.append((form, code))
                        return code
        return None

    unmatched: list[tuple[str, str]] = []

    def is_name_like(form: str) -> bool:
        """Reject numeric cells and known non-name boilerplate before matching."""
        s = form.strip()
        if not s or norm(s) in boilerplate:
            return False
        if not any(ch.isalpha() for ch in s):
            return False
        try:
            float(s.replace(",", ""))
            return False
        except ValueError:
            return True

    def harvest(label: str, forms) -> None:
        for form in forms:
            if not isinstance(form, str) or not is_name_like(form):
                continue
            code = resolve(form)
            if code is None:
                unmatched.append((label, form))
            else:
                add(code, form)

    # --- staff tester(s) ---
    # The coding sheet lists "Staff Tester" (2017) and "tester" (2018) as separate
    # rows, but the point data shows a single staff account behind both (11 + 21 =
    # 32 features, matching the paper's 32 staff-tester features). One person, so
    # one code.
    master = pd.read_csv(RAW / "MapMounds17_18withnas.csv", low_memory=False)
    staff = sorted(
        {n for n in master["createdBy"].dropna().unique() if resolve(n) is None}
    )
    fuzzy_bridged.clear()  # discard probes made while classifying staff
    for i, name in enumerate(staff, start=1):
        parts = name.split()
        records[f"TESTER-{i}"] = {
            "code": f"TESTER-{i}",
            "paper_label": "Staff Tester",
            "season": 0,  # active in both seasons
            "role": "staff",
            "canonical_name": name,
            "surname": parts[-1],
            "given_name": parts[0],
            "name_forms": set(),
        }
    reindex()

    # coding sheets (the codes themselves)
    for code, rec in records.items():
        add(code, rec["canonical_name"])

    # master point CSV + the three raw entity exports
    for col in ("createdBy", "modifiedBy", "FeatureAuthor"):
        harvest(f"MapMounds17_18withnas.csv:{col}", master[col].dropna().unique())
    for fname in (
        "rawdata/Entity-20180912.csv",
        "rawdata/Entity-20180927.csv",
        "rawdata/Entity-20180928.csv",
        "rawdata/MapDig_ALLfixedNE.csv",
    ):
        d = pd.read_csv(RAW / fname, low_memory=False)
        for col in ("createdBy", "modifiedBy", "FeatureAuthor"):
            if col in d.columns:
                harvest(f"{fname}:{col}", d[col].dropna().unique())

    # shapefiles carrying names
    import geopandas as gpd

    for shp, col in (
        ("Analysis-areas-by-student", "Student"),
        ("Mound-count-by-student", "Student"),
        ("Error-count-by-student", "Student"),
        ("QA-errors-SAR", "Recorder"),
    ):
        g = gpd.read_file(RAW / f"{shp}.shp")
        harvest(f"{shp}.shp:{col}", g[col].dropna().unique())

    # workbook tabs
    md = pd.read_csv(RAW / "MapDigitisation__Sheet1.csv", skiprows=2, engine="python")
    harvest("MapDigitisation__Sheet1.csv:Firstname", md["Firstname"].dropna().unique())

    for f in ("RecordingProgress__hours17.csv", "RecordingProgress__hours18.csv"):
        d = pd.read_csv(RAW / f, skiprows=2, engine="python", on_bad_lines="skip")
        harvest(f"{f}:student", d["student"].dropna().unique())

    vol = pd.read_csv(RAW / "RecordingProgress__Volunteers.csv", skiprows=2, engine="python")
    for col in ("SummaryFromOR", "Fullname", "Lastname", "Firstname"):
        if col in vol.columns:
            harvest(f"RecordingProgress__Volunteers.csv:{col}", vol[col].dropna().unique())

    res = pd.read_csv(RAW / "QA-time-on-task__Results.csv")
    cand = pd.concat([res["Student"].dropna(), res["Tile"].dropna()])
    harvest(
        "QA-time-on-task__Results.csv",
        [f for f in cand.unique() if isinstance(f, str) and not f.startswith("K-35")],
    )

    # --- serialise ---
    out = {
        "_comment": (
            "SENSITIVE de-anonymisation key for the 2023 participatory-GIS baseline. "
            "Lives only in the gitignored raw/ directory. Never copy any value from "
            "'canonical_name', 'surname', 'given_name', or 'name_forms' into staged/ "
            "or into any committed artefact."
        ),
        "generated_by": "inputs/student-baseline-2023/raw/code-mapping.json (stage_01_mapping.py)",
        "source_of_truth": "Student-coding-sheet__student-data.csv (tab 'student data')",
        "codes": {},
        "lookup_normalised": {},
        "unmatched_name_forms": [{"source": s, "form": f} for s, f in sorted(set(unmatched))],
        "fuzzy_bridged_count": len({f for f, _ in fuzzy_bridged}),
    }
    for code in sorted(records, key=lambda c: (records[c]["role"] != "volunteer", c)):
        rec = dict(records[code])
        rec["name_forms"] = sorted(rec["name_forms"])
        out["codes"][code] = rec
        for form in rec["name_forms"]:
            out["lookup_normalised"][norm(form)] = code

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # --- console summary (NO NAMES) ---
    print(f"wrote {OUT}")
    print(f"codes: {len(out['codes'])}  "
          f"({sum(1 for r in records.values() if r['role'] == 'volunteer')} volunteer, "
          f"{sum(1 for r in records.values() if r['role'] == 'staff')} staff)")
    for code in out["codes"]:
        print(f"  {code}: season={out['codes'][code]['season']} "
              f"forms={len(out['codes'][code]['name_forms'])}")
    print(f"unmatched name forms: {len(out['unmatched_name_forms'])}")
    for u in out["unmatched_name_forms"]:
        print(f"  UNMATCHED from {u['source']}  (form withheld)")
    print("fuzzy-bridged form count:", out["fuzzy_bridged_count"])


if __name__ == "__main__":
    main()
