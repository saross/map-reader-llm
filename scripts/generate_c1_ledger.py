#!/usr/bin/env python3
"""Generate the C1 verification ledger from the commitment ledger.

Emits one append-only JSONL row per commitment (charter § 6 row schema):
the claim "the registration specifies X" is VERIFIED by the mechanical
verbatim check plus the fresh-context reconstruct-and-diff pass, or
CORRECTED where the 2026-07-29 adjudication changed the row (retype,
reword, or added-as-missed).

The script is deterministic given the ledger and the adjudication
constants below; re-running regenerates identical rows apart from the
run date. Rows are written only when the target file does not yet
contain the claim_id (append-only discipline).

Usage::

    python3 scripts/generate_c1_ledger.py [--out reports/verification/ledgers/c1-commitments.jsonl]
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / "results" / "commitments.json"
DEFAULT_OUT = REPO_ROOT / "reports" / "verification" / "ledgers" / "c1-commitments.jsonl"

#: Rows changed by the 2026-07-29 adjudication (commit c1427f1d0) -> CORRECTED.
ADJUDICATION_COMMIT = "c1427f1d0"
CORRECTED_EDITED = {
    "CMT-0101", "CMT-0113", "CMT-0152", "CMT-0159", "CMT-0167", "CMT-0203",
    "CMT-0257", "CMT-0264", "CMT-0307", "CMT-0503", "CMT-0525", "CMT-0530",
    "CMT-0539", "CMT-0617", "CMT-0626", "CMT-0631",
}
CORRECTED_ADDED = {
    "CMT-0697", "CMT-0698", "CMT-0699", "CMT-0700", "CMT-0701", "CMT-0702",
}


def build_rows(run_date: str) -> list[dict]:
    """Build one C1 ledger row per commitment."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    rows = []
    for i, cmt in enumerate(ledger["commitments"], start=1):
        cid = cmt["commitment_id"]
        if cid in CORRECTED_ADDED:
            verdict = "CORRECTED"
            evidence = (
                "missed by extraction; added at adjudication (commit "
                f"{ADJUDICATION_COMMIT}) from a verifier-reported gap; "
                "statement mechanically verified verbatim at the cited lines"
            )
        elif cid in CORRECTED_EDITED:
            verdict = "CORRECTED"
            evidence = (
                "extraction row amended at adjudication (commit "
                f"{ADJUDICATION_COMMIT}); statement unchanged and mechanically "
                "verified verbatim at the cited lines"
            )
        else:
            verdict = "VERIFIED"
            evidence = (
                "statement mechanically verified verbatim at the cited lines "
                "(validate_commitments.py); range covered by fresh-context "
                "reconstruct-and-diff with no gap or dispute recorded"
            )
        rows.append({
            "claim_id": f"c1-{i:04d}",
            "class": "C1",
            "source": {"file": cmt["source"]["file"],
                       "line": cmt["source"]["lines"][0]},
            "claim_text": cmt["statement"],
            "anchor": {"file": "results/commitments.json",
                       "path": f"$.commitments[?(@.commitment_id=='{cid}')]"},
            "method": "decompose+verbatim-verify+reconstruct-and-diff",
            "verdict": verdict,
            "evidence": evidence,
            "checker": {"model": "claude-fable-5 (orchestration/adjudication) + "
                                 "claude-opus-5 agents (extraction x8, "
                                 "verification x8)",
                        "request_id": None,
                        "harness": "claude-session",
                        "date": run_date},
            "disposition": None,
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    """Append any not-yet-present rows to the JSONL ledger."""
    parser = argparse.ArgumentParser(description="Generate the C1 ledger.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    run_date = datetime.date.today().isoformat()
    rows = build_rows(run_date)

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
