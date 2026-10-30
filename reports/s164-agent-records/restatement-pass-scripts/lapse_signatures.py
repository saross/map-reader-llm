#!/usr/bin/env python3
"""
Lapse the signatures of the register rows the restatement pass moved.

Part of the S164 restatement pass (``reports/s164-agent-records/
restatement-pass.md`` § 8). Under ``docs/methodology/signature-policy.md`` a
signature attests the row's text, and lapses when a number or verdict that
text quotes moves. For each row named in the notes file this does exactly
what the A-06, A-07 and A-09 lapses did (``results/run-analyses.json``,
``h6-a07-voting-thresholds`` → ``signature.history``, 2026-10-14):

- ``signature.status`` → ``re-sign-pending`` and ``signed_at`` → null;
- a ``history`` entry with ``noted_at``, ``kind``, ``prior_status``,
  ``prior_signed_at``, ``prior_attests`` and ``prior_presentation``;
- the drafted D9-pattern note appended to ``attests`` (marked "drafted by
  Claude for the PI and NOT YET APPROVED" in its own text);
- ``presentation`` → where the walkthrough material is.

The ``outcome`` field is never touched; the script refuses a row that is not
currently ``signed`` and refuses a note that does not carry the not-approved
marker. The file keeps its serialisation (indent 1, UTF-8 unescaped).

Usage: python lapse_signatures.py <repo_root> <notes.json> <noted_at>

``notes.json`` maps ``analysis_id`` → ``{"kind": str, "note": str,
"presentation": str}``.

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
NOTES = json.loads(Path(sys.argv[2]).read_text())
NOTED_AT = sys.argv[3]
MARKER = "drafted by Claude for the PI and NOT YET APPROVED"

path = ROOT / "results/run-analyses.json"
text = path.read_text(encoding="utf-8")
doc = json.loads(text)
rows = {r["analysis_id"]: r for r in doc["analyses"]}
outcomes_before = {k: r.get("outcome") for k, r in rows.items()}
for aid, spec in NOTES.items():
    row = rows[aid]
    sig = row["signature"]
    if sig.get("status") != "signed":
        raise SystemExit(f"{aid}: status is {sig.get('status')!r}, not 'signed'")
    if MARKER not in spec["note"]:
        raise SystemExit(f"{aid}: the note lacks the not-approved marker")
    history = list(sig.get("history") or [])
    history.append({
        "noted_at": NOTED_AT,
        "kind": spec["kind"],
        "prior_status": sig["status"],
        "prior_signed_at": sig.get("signed_at"),
        "prior_attests": sig.get("attests"),
        "prior_presentation": sig.get("presentation"),
    })
    sig["status"] = "re-sign-pending"
    sig["signed_at"] = None
    sig["attests"] = (sig.get("attests") or "") + "\n\n" + spec["note"]
    sig["presentation"] = spec["presentation"]
    sig["history"] = history
    print(f"lapsed {aid} (history entries: {len(history)})")
assert {k: r.get("outcome") for k, r in rows.items()} == outcomes_before, "outcome touched"
path.write_text(json.dumps(doc, indent=1, ensure_ascii=False)
                + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
