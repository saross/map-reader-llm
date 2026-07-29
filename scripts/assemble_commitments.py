#!/usr/bin/env python3
"""Assemble results/commitments.json from per-chunk extraction outputs.

Phase 1 C1 assembly (audit-charter § 7): merges the extraction agents'
chunk JSON arrays, orders rows by source document and line, assigns
sequential ``CMT-NNNN`` ids, pins the three lodged documents by git
blob, and runs the full validator. Optionally repairs line locators
mechanically: when a statement is not found in its cited window but IS
found verbatim exactly once elsewhere in the cited file, the locator
(and only the locator) is corrected — the statement itself is never
edited, so a fabricated "quote" can never be repaired into existence.

Usage::

    python3 scripts/assemble_commitments.py --chunks-dir <dir> \
        [--out results/commitments.json] [--repair-locators]
"""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "results" / "commitments.json"

#: Lodged documents in canonical order, with their schema roles.
SOURCE_DOCS = [
    ("docs/methodology/preregistration/osf/preregistration.md", "primary"),
    ("docs/methodology/preregistration/osf/preregistration-appendix-prompts.md",
     "appendix-prompts"),
    ("docs/methodology/preregistration/osf/preregistration-coverage.md", "coverage"),
]


def git_blob(path: str) -> str:
    """Return the abbreviated git blob hash of a working-tree file."""
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), "hash-object", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()[:12]


def load_chunks(chunks_dir: Path) -> list[dict]:
    """Load and concatenate all chunk-*.json arrays in filename order."""
    rows: list[dict] = []
    for chunk_path in sorted(chunks_dir.glob("chunk-*.json"),
                             key=lambda p: int(p.stem.split("-")[1])):
        with chunk_path.open(encoding="utf-8") as fh:
            chunk = json.load(fh)
        if not isinstance(chunk, list):
            raise ValueError(f"{chunk_path.name}: expected a JSON array")
        for row in chunk:
            row.setdefault("_chunk", chunk_path.name)
        rows.extend(chunk)
    return rows


def repair_locator(row: dict, file_lines: dict[str, list[str]]) -> str | None:
    """Fix a row's line locator if its statement is found verbatim elsewhere.

    Returns a message describing the repair, or None if no repair was
    made (either the locator was already correct, or the statement is
    absent / ambiguous — those surface as validator failures).
    """
    path = row["source"]["file"]
    lines = file_lines[path]
    lo, hi = row["source"]["lines"]
    if 1 <= lo <= hi <= len(lines):
        window = "\n".join(lines[lo - 1: hi])
        if row["statement"] in window:
            return None  # locator already correct

    statement_first_line = row["statement"].split("\n", 1)[0]
    hits = [i + 1 for i, line in enumerate(lines) if statement_first_line in line]
    full_text = "\n".join(lines)
    if len(hits) == 1 and row["statement"] in full_text:
        start = hits[0]
        end = start + row["statement"].count("\n")
        old = row["source"]["lines"]
        row["source"]["lines"] = [start, end]
        return (f"{row.get('commitment_id', row.get('_chunk'))}: "
                f"locator {old} -> [{start}, {end}]")
    return None


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: assemble, optionally repair, write, validate."""
    parser = argparse.ArgumentParser(description="Assemble the commitment ledger.")
    parser.add_argument("--chunks-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--repair-locators", action="store_true")
    args = parser.parse_args(argv)

    rows = load_chunks(args.chunks_dir)

    doc_order = {path: i for i, (path, _) in enumerate(SOURCE_DOCS)}
    rows.sort(key=lambda r: (doc_order.get(r["source"]["file"], 99),
                             r["source"]["lines"][0]))
    for i, row in enumerate(rows, start=1):
        row["commitment_id"] = f"CMT-{i:04d}"
        chunk = row.pop("_chunk", None)
        if chunk and not (row.get("notes") or "").startswith("[chunk"):
            row["notes"] = f"[{chunk}] {row['notes']}" if row.get("notes") else f"[{chunk}]"
        # Key order per schema for readable diffs.
        ordered = {k: row.get(k) for k in (
            "commitment_id", "source", "kind", "statement",
            "normalised_obligation", "hypothesis", "decision_statistic",
            "uncertainty_treatment", "trigger", "status", "discharged_by",
            "waiver", "notes")}
        rows[i - 1] = ordered

    if args.repair_locators:
        file_lines = {
            path: (REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
            for path, _ in SOURCE_DOCS
        }
        n_repaired = 0
        for row in rows:
            msg = repair_locator(row, file_lines)
            if msg:
                n_repaired += 1
                print(f"REPAIRED {msg}")
        print(f"{n_repaired} locator(s) repaired")

    ledger = {
        "schema_version": "1.0",
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_documents": [
            {"file": path, "git_blob": git_blob(path), "role": role}
            for path, role in SOURCE_DOCS
        ],
        "commitments": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"Wrote {len(rows)} commitments -> {args.out}")

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import validate_commitments  # noqa: E402  (repo-local import by design)

    return validate_commitments.main(["--ledger", str(args.out)])


if __name__ == "__main__":
    sys.exit(main())
