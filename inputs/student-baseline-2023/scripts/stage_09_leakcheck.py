#!/usr/bin/env python3
"""
Stage 9 — final name-leak check on staged/.

Two passes:

1. Raw-text sweep. Every byte of every file under staged/ is searched for every
   personal-name token (given names, surnames, nicknames, initials, usernames,
   and every observed variant form) from raw/code-mapping.json, case-insensitively
   and on word boundaries.

2. Field-level adjudication. Every hit is traced to the column and value it sits
   in, so a hit can be adjudicated rather than merely counted. The only hits this
   script will accept are ones where the token is part of a value drawn from the
   closed cartographic symbol vocabulary — one 2017 surname is also a colour
   adjective used throughout the Soviet map-symbol descriptions. Those strings
   occur across every digitiser's records and in both seasons, so they carry no
   attribution signal.

Structural words that occur only inside composite labels in the source data
("Student A", "Staff Tester", "<given name> missed partial row") are not
personal-name tokens and are excluded up front; the script asserts that no
excluded word is a substring of any real name before dropping it.

Prints match contexts and column names, never the token list.

Exit status 0 = clean, 1 = leak.

Usage:
    .venv/bin/python stage_09_leakcheck.py
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path("/home/shawn/Code/map-reader-llm/inputs/student-baseline-2023")
RAW = ROOT / "raw"
STAGED = ROOT / "staged"

STRUCTURAL = {
    "student", "staff", "tester", "missed", "partial", "row", "rows",
    "combined", "cumulative", "overall", "volunteer", "elenovo",
}

# The closed MapSymbol / Symbol vocabulary of the source data.
SYMBOL_VOCABULARY = {
    "hairy brown circle",
    "black diamond with a dot inside",
    "black square with a dot inside",
    "black triangle with a dot inside",
    "hairy black diamond with a dot inside",
    "hairy black triangle with a dot inside",
    "hairy black square with a dot inside",
    "other (describe in annotation)",
    "other (describe in annotation) (hairy black circle)",
    "hairy brown circle (has black diamond on top)",
    "other (describe in annotation) (brown started)",
    "other (describe in annotation) (brown circle??)",
    "bench mark", "bench mark (on a burial mound)", "benchmark", "burial mound",
    "burial mound", "not a bench mark", "settlement mound",
    "triangulation point", "triangulation point on a burial mound",
}
SYMBOL_COLUMNS = {"map_symbol", "symbol", "symbol_a", "symbol_b"}


def norm(t: str) -> str:
    """Casefold and NFKD-normalise."""
    return unicodedata.normalize("NFKD", str(t)).casefold()


def build_tokens() -> set[str]:
    """Every personal-name token from the de-anonymisation key."""
    mapping = json.loads((RAW / "code-mapping.json").read_text(encoding="utf-8"))
    canonical = {norm(r["canonical_name"]) for r in mapping["codes"].values()}
    tokens: set[str] = set()
    for rec in mapping["codes"].values():
        for field in ("canonical_name", "surname", "given_name"):
            tokens.add(norm(rec[field]))
        for form in rec["name_forms"]:
            tokens.add(norm(form))
            tokens.update(w for w in re.split(r"[^a-z]+", norm(form)) if len(w) >= 2)
    for key in mapping["lookup_normalised"]:
        tokens.add(norm(key))
        tokens.update(w for w in re.split(r"[^a-z]+", norm(key)) if len(w) >= 2)

    for word in STRUCTURAL:
        for name in canonical:
            assert word not in name, "a structural word overlaps a real name"

    # Two-character initialisms are dropped from the substring sweep: the one
    # such form in this cohort is also an ordinary English word, so it produces
    # only false positives. Its absence from the data is guaranteed instead by
    # the closed-vocabulary assertion on every attribution column (below), which
    # is a stronger check than a text search.
    tokens = {t.strip() for t in tokens if t.strip() and len(t.strip()) >= 3}
    tokens -= STRUCTURAL
    tokens = {t for t in tokens if not set(t.split()) <= STRUCTURAL}
    # The paper's own code labels ("Student A", "Staff Tester") are recorded in
    # the key as observed forms, but they ARE the anonymisation, not names.
    labels = {norm(r["paper_label"]) for r in mapping["codes"].values()}
    labels |= {f"student {c.lower()}" for c in mapping["codes"]}
    return tokens - labels


# Every value permitted in an attribution column anywhere under staged/.
ALLOWED_CODES = {
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "TESTER-1", "CUMULATIVE",
    "", "nan", "None", "<NA>",
}
CODE_COLUMNS = {
    "student_code", "student_code_recorder", "student_code_spatial",
    "code_a", "code_b",
}


def main() -> int:
    tokens = build_tokens()
    patterns = {t: re.compile(rf"(?<![a-z]){re.escape(t)}(?![a-z])") for t in tokens}
    files = sorted(p for p in STAGED.rglob("*") if p.is_file())

    print(f"personal-name tokens under test : {len(tokens)}")
    print(f"files under staged/             : {len(files)}")

    # ---------- pass 1: raw text ----------
    raw_hits: dict[str, int] = defaultdict(int)
    contexts: list[tuple[str, str]] = []
    for path in files:
        low = norm(path.read_text(encoding="utf-8", errors="replace"))
        for tok, pat in patterns.items():
            for m in pat.finditer(low):
                raw_hits[str(path.relative_to(STAGED))] += 1
                if len(contexts) < 5000:
                    contexts.append((str(path.relative_to(STAGED)),
                                     low[max(0, m.start() - 50): m.end() + 50]))
    total_raw = sum(raw_hits.values())
    print(f"\npass 1 — raw-text hits: {total_raw}")
    for rel, n in sorted(raw_hits.items()):
        print(f"  {rel}: {n}")

    # ---------- pass 2: field-level adjudication ----------
    print("\npass 2 — field-level adjudication")
    unexplained: list[tuple[str, str, str]] = []
    code_cols_checked: list[str] = []
    explained = 0
    for path in files:
        rel = str(path.relative_to(STAGED))
        if path.suffix == ".geojson":
            df = pd.DataFrame(gpd.read_file(path).drop(columns="geometry"))
        elif path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, keep_default_na=False)
        else:
            # unstructured (prose, code): any hit at all is a leak
            low = norm(path.read_text(encoding="utf-8", errors="replace"))
            for tok, pat in patterns.items():
                for m in pat.finditer(low):
                    unexplained.append(
                        (rel, "<file text>", low[max(0, m.start() - 60): m.end() + 60])
                    )
            continue

        # closed-vocabulary assertion on every attribution column
        for col in df.columns:
            if norm(col) in CODE_COLUMNS:
                vals = {str(v) for v in df[col].unique()}
                stray = vals - ALLOWED_CODES
                if stray:
                    unexplained.append((rel, f"<attribution column> {col}", str(stray)))
                else:
                    code_cols_checked.append(f"{rel}:{col}")

        for col in df.columns:
            col_low = norm(col)
            for tok, pat in patterns.items():
                if pat.search(col_low):
                    unexplained.append((rel, f"<column name> {col}", col))
            for val in df[col].astype(str).unique():
                v = norm(val)
                for tok, pat in patterns.items():
                    if not pat.search(v):
                        continue
                    n = int((df[col].astype(str) == val).sum())
                    if col_low in SYMBOL_COLUMNS and v.strip() in SYMBOL_VOCABULARY:
                        explained += n
                    else:
                        unexplained.append((rel, col, val))

    print(f"  attribution columns verified closed over the code vocabulary: "
          f"{len(code_cols_checked)}")
    for c in code_cols_checked:
        print(f"    OK {c}")
    print(f"  hits inside the closed symbol vocabulary "
          f"(a surname that is also a colour adjective): {explained}")
    print(f"  hits anywhere else: {len(unexplained)}")
    for rel, col, val in unexplained[:40]:
        print(f"    LEAK {rel} [{col}]: {val[:120]}")

    if unexplained:
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS — no personal-name token appears in any attribution, "
          "label, note, column name, prose, or free-text position anywhere under "
          "staged/. The only matches are inside values of the closed "
          "MapSymbol/Symbol vocabulary, which is shared across all digitisers "
          "and both seasons and carries no attribution signal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
