#!/usr/bin/env python3
"""Generate the C2 verification ledger (execution claims).

Two row families (charter § 6 schema, append-only):

1. One row per commitment status determination — the claim "this
   registered obligation was executed / waived / remains open", verified
   against manifests (discharged), the errata register (waived), or
   recorded as the truthful open default.
2. One row per licence-census pair — the claim "this executed factor
   level is licensed", VERIFIED (registration and/or erratum) or FLAGGED
   (UNLICENSED — erratum candidate pending GATE 1).

Deterministic given the ledger and census; append-only on claim_id.

Usage::

    python3 scripts/generate_c2_ledger.py [--out reports/verification/ledgers/c2-execution.jsonl]
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / "results" / "commitments.json"
CENSUS = REPO_ROOT / "reports" / "verification" / "c2-census" / "licence-census.json"
DEFAULT_OUT = REPO_ROOT / "reports" / "verification" / "ledgers" / "c2-execution.jsonl"

CHECKER = {
    "model": "claude-fable-5 (orchestration/spot-audit) + claude-opus-5 agents "
             "(discharge mapping x8, licence triage x1)",
    "request_id": None,
    "harness": "claude-session",
}


def build_rows(run_date: str) -> list[dict]:
    """Build C2 rows from commitment statuses and the licence census."""
    rows: list[dict] = []
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    for i, cmt in enumerate(ledger["commitments"], start=1):
        status = cmt["status"]
        if status == "discharged":
            db = cmt["discharged_by"] or {}
            ids = (db.get("runs") or []) + (db.get("conditions") or []) \
                + (db.get("analyses") or [])
            evidence = "; ".join(filter(None, [
                f"manifest ids: {', '.join(ids)}" if ids else None,
                db.get("evidence")])) or "(no evidence recorded)"
            verdict, method = "VERIFIED", "manifest-evidence"
        elif status == "waived":
            evidence = f"waived by erratum {cmt['waiver']} (errata licence register)"
            verdict, method = "VERIFIED", "erratum-waiver"
        else:
            evidence = ("no execution evidence and no waiver found; remains open "
                        "and warns at every manifest build (open-commitment guard)")
            verdict, method = "FLAGGED", "open-default"
        rows.append({
            "claim_id": f"c2-{i:04d}",
            "class": "C2",
            "source": {"file": "results/commitments.json", "line": None},
            "claim_text": cmt["statement"],
            "anchor": {"file": "results/commitments.json",
                       "path": f"$.commitments[?(@.commitment_id=="
                               f"'{cmt['commitment_id']}')].status"},
            "method": method,
            "verdict": verdict,
            "evidence": f"status={status}: {evidence}",
            "checker": {**CHECKER, "date": run_date},
            "disposition": None,
        })

    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    for j, pair in enumerate(census["pairs"], start=1):
        unlicensed = pair["verdict"] == "UNLICENSED"
        rows.append({
            "claim_id": f"c2-census-{j:04d}",
            "class": "C2",
            "source": {"file": "results/run-conditions.json", "line": None},
            "claim_text": pair["pair"],
            "anchor": {"file": "reports/verification/c2-census/licence-census.json",
                       "path": f"$.pairs[?(@.pair=='{pair['pair']}')]"},
            "method": "licence-census",
            "verdict": "FLAGGED" if unlicensed else "VERIFIED",
            "evidence": f"{pair['verdict']}: {pair['evidence'][:400]}",
            "checker": {**CHECKER, "date": run_date},
            "disposition": "erratum candidate (GATE 1)" if unlicensed else None,
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    """Append any not-yet-present rows to the JSONL ledger."""
    parser = argparse.ArgumentParser(description="Generate the C2 ledger.")
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
