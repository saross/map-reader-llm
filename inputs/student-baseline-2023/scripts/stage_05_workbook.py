#!/usr/bin/env python3
"""
Stage 5 — anonymised staging of the "QA time on task" workbook.

Outputs:
    staged/qa-time-on-task.csv               — the error/error-rate tables,
                                               names replaced by student codes
    staged/qa-time-on-task-activity-log.csv  — the staff QA session log
                                               (carries no personal names)

Usage:
    .venv/bin/python stage_05_workbook.py
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path("/home/shawn/Code/map-reader-llm/inputs/student-baseline-2023")
RAW = ROOT / "raw"
STAGED = ROOT / "staged"

METRICS = [
    "features_identified", "false_positive", "double_marked", "false_negative",
    "classification_error", "total_errors", "true_positives", "true_feature_count",
    "false_positive_rate", "double_marking_rate", "false_negative_rate",
    "total_error_rate",
]

# Row blocks in the Results tab, keyed by the 1-based CSV line where each block's
# data starts and ends (the tab stacks five presentations of the same audit).
BLOCKS = {
    "by_tile": (1, 5),
    "by_student_split": (7, 13),
    "by_student_combined": (15, 20),
    "excluding_student_c": (23, 28),
    "published_table_3": (35, 40),
}


def norm(t) -> str:
    """Normalise a name token for lookup."""
    return " ".join(unicodedata.normalize("NFKD", str(t)).casefold().split())


def main() -> None:
    STAGED.mkdir(parents=True, exist_ok=True)
    lookup = json.loads((RAW / "code-mapping.json").read_text(encoding="utf-8"))[
        "lookup_normalised"
    ]

    raw = pd.read_csv(RAW / "QA-time-on-task__Results.csv", header=None, dtype=str)

    rows = []
    for block, (lo, hi) in BLOCKS.items():
        for i in range(lo, hi + 1):
            if i >= len(raw):
                continue
            r = raw.iloc[i]
            label = r[1] if isinstance(r[1], str) and r[1].strip() else r[14]
            if not isinstance(label, str) or not label.strip():
                continue
            label = label.strip()
            if norm(label) in {"features identified", "volunteer", "tile", "ord"}:
                continue

            sheet_id, code, qualifier = None, None, None
            if label.startswith("K-35"):
                sheet_id = label
                # the by_tile block names the digitiser in the trailing Student column
                code = lookup.get(norm(r[14])) if isinstance(r[14], str) else None
            elif norm(label) == "cumulative":
                code = "CUMULATIVE"
            else:
                base = label
                if "(" in label:
                    base, qualifier = label.split("(", 1)
                    qualifier = qualifier.rstrip(") ").strip()
                code = lookup.get(norm(base))
                if code is None:
                    continue

            vals = {}
            for k, col in zip(METRICS, range(2, 14)):
                v = r[col]
                try:
                    vals[k] = float(v) if isinstance(v, str) and v.strip() else None
                except ValueError:
                    vals[k] = None
            rows.append({
                "block": block, "sheet_id": sheet_id, "student_code": code,
                "qualifier": qualifier, **vals,
                "notes": r[15] if isinstance(r[15], str) and r[15].strip() else None,
            })

    out = pd.DataFrame(rows)
    # integer-like columns back to integers where they are whole
    for c in METRICS[:8]:
        out[c] = out[c].astype("Int64")
    out.to_csv(STAGED / "qa-time-on-task.csv", index=False)

    # --- activity log (no names present in the source tab) ---
    tot = pd.read_csv(RAW / "QA-time-on-task__ToT.csv", header=None, dtype=str)
    log = tot.iloc[2:9, 0:6].copy()
    log.columns = ["activity", "date", "start", "minutes", "errors_found", "notes"]
    log["date"] = log["date"].str.slice(0, 10)
    log = log[log.activity.notna()]
    log["minutes"] = pd.to_numeric(log["minutes"], errors="coerce").astype("Int64")
    log["errors_found"] = pd.to_numeric(log["errors_found"], errors="coerce").astype("Int64")
    log.to_csv(STAGED / "qa-time-on-task-activity-log.csv", index=False)

    print(f"qa-time-on-task.csv: {len(out)} rows, blocks {sorted(out.block.unique())}")
    print(out.to_string(index=False))
    print(f"\nqa-time-on-task-activity-log.csv: {len(log)} rows, "
          f"{int(log.minutes.sum())} minutes logged, "
          f"{int(log.errors_found.sum())} errors found in-session")
    print(log.to_string(index=False))


if __name__ == "__main__":
    main()
