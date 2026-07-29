#!/usr/bin/env python3
"""Generate the C3 verification ledger (manifest provenance).

One charter § 6 row per manifest row (per-claim-family granularity):
the claim "this manifest row's field values match its cited raw
sources", verified by the independent re-derivation
(``rederivation-report.json``) plus the Opus triage adjudications
(``c3-triage-config.json``, ``c3-triage-tiles.json``).

Per-row verdict rules:

- any field adjudicated SOURCE_CORRECT or GENUINE_DISCREPANCY → FLAGGED
  (disposition: Phase 2 correction queue);
- else all mismatches adjudicated MANIFEST_CORRECT and ≥1 field checked
  → VERIFIED (silent fields counted in evidence);
- else every non-structural field SOURCE_SILENT → DEFERRED (recorder
  gap: blocked, reason stated).

Deterministic; append-only on claim_id.

Usage::

    python3 scripts/generate_c3_ledger.py [--out reports/verification/ledgers/c3-provenance.jsonl]
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RDIR = REPO_ROOT / "reports" / "verification" / "c3-rederivation"
DEFAULT_OUT = REPO_ROOT / "reports" / "verification" / "ledgers" / "c3-provenance.jsonl"

CHECKER = {
    "model": "script (rederive_manifest_fields.py, sapphire) + claude-opus-5 "
             "triage x2 + claude-fable-5 adjudication",
    "request_id": None,
    "harness": "script",
}


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def triage_lookup() -> dict[tuple[str, str], dict]:
    """Map (pass_id, field) -> triage ruling, expanding sibling groups."""
    look: dict[tuple[str, str], dict] = {}
    for name in ("c3-triage-config.json", "c3-triage-tiles.json"):
        for row in load(RDIR / name):
            ids = [row["pass_id"]] + list(row.get("siblings") or [])
            for pid in ids:
                look[(pid, row["field"])] = row
    return look


def build_rows(run_date: str) -> list[dict]:
    report = load(RDIR / "rederivation-report.json")
    triage = triage_lookup()
    rows: list[dict] = []

    def emit(idx: int, row_id: str, manifest: str, fields: list[dict],
             error: str | None = None) -> None:
        if error:
            verdict, evidence, dispo = "FLAGGED", f"{error}", "Phase 2 correction queue"
        else:
            counts = {"MATCH": 0, "SOURCE_SILENT": 0, "STRUCTURAL": 0}
            bad: list[str] = []
            vindicated: list[str] = []
            for f in fields:
                v = f["verdict"]
                if v == "MISMATCH":
                    t = triage.get((row_id, f["field"]))
                    ruling = t["ruling"] if t else "UNTRIAGED"
                    if ruling == "MANIFEST_CORRECT":
                        vindicated.append(f["field"])
                    else:
                        bad.append(f"{f['field']}:{ruling}")
                else:
                    counts[v] = counts.get(v, 0) + 1
            checkable = counts["MATCH"] + len(vindicated) + len(bad)
            if bad:
                verdict = "FLAGGED"
                dispo = "Phase 2 correction queue"
                evidence = (f"{counts['MATCH']} fields match; adjudicated "
                            f"discrepancies: {', '.join(bad)}; "
                            f"{counts['SOURCE_SILENT']} silent")
            elif checkable == 0:
                verdict, dispo = "DEFERRED", None
                evidence = (f"all {counts['SOURCE_SILENT']} non-structural "
                            f"fields SOURCE_SILENT (recorder gap era)")
            else:
                verdict, dispo = "VERIFIED", None
                evidence = (f"{counts['MATCH']} fields match"
                            + (f"; {len(vindicated)} mismatches adjudicated "
                               f"MANIFEST_CORRECT ({', '.join(vindicated)})"
                               if vindicated else "")
                            + (f"; {counts['SOURCE_SILENT']} silent "
                               f"(recorder gaps)" if counts["SOURCE_SILENT"]
                               else ""))
        rows.append({
            "claim_id": f"c3-{idx:04d}",
            "class": "C3",
            "source": {"file": manifest, "line": None},
            "claim_text": row_id,
            "anchor": {"file": "reports/verification/c3-rederivation/"
                               "rederivation-report.json",
                       "path": f"$..[?(@.pass_id=='{row_id}' || "
                               f"@.condition_id=='{row_id}' || "
                               f"@.row=='{row_id}')]"},
            "method": "independent-rederivation+triage",
            "verdict": verdict,
            "evidence": evidence,
            "checker": {**CHECKER, "date": run_date},
            "disposition": dispo,
        })

    i = 0
    for r in report["passes"]:
        i += 1
        emit(i, r.get("pass_id", "?"), "results/passes-manifest.json",
             r.get("fields", []), r.get("error"))
    for r in report["conditions"]:
        i += 1
        emit(i, r.get("condition_id", "?"), "results/conditions-manifest.json",
             r.get("fields", []))
    for r in report["simple"]:
        i += 1
        manifest = ("results/run-registry.json" if r["row"].startswith("registry")
                    else "results/runs-manifest.json" if r["row"].startswith("runs")
                    else "results/analyses-manifest.json")
        rows.append({
            "claim_id": f"c3-{i:04d}", "class": "C3",
            "source": {"file": manifest, "line": None},
            "claim_text": r["row"],
            "anchor": {"file": "reports/verification/c3-rederivation/"
                               "rederivation-report.json",
                       "path": f"$.simple[?(@.row=='{r['row']}')]"},
            "method": "existence+consistency",
            "verdict": "VERIFIED" if r["verdict"] == "MATCH" else "FLAGGED",
            "evidence": r.get("detail", ""),
            "checker": {**CHECKER, "date": run_date},
            "disposition": None if r["verdict"] == "MATCH"
                           else "Phase 2 correction queue",
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the C3 ledger.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    rows = build_rows(datetime.date.today().isoformat())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    existing: set[str] = set()
    if args.out.exists():
        with args.out.open(encoding="utf-8") as fh:
            existing = {json.loads(line)["claim_id"] for line in fh if line.strip()}
    appended = 0
    with args.out.open("a", encoding="utf-8") as fh:
        for row in rows:
            if row["claim_id"] not in existing:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                appended += 1
    verdicts: dict[str, int] = {}
    for row in rows:
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
    print(f"OK {appended} row(s) appended ({len(rows)} total; {verdicts})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
