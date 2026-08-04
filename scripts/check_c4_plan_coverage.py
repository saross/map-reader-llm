#!/usr/bin/env python3
"""Whole-plan coverage and drift check for the C4 extraction programme.

Answers one question the per-wave validation cannot: **does the batch plan
still cover every line of every document it claims to cover?**

Per-wave validation only ever looks at its own wave, which is precisely why
the corpus drifted under the plan for six waves before anyone noticed
(escalations W7-E1/E2/E3, ruling 18). Documents grow after their batches are
extracted, and a rule-14 re-extraction updates the *extraction's* line anchors
while leaving the *plan's* ranges untouched — so a repair can silently open a
tail gap. This script is the backstop ruling 18 point 4 asks GATE 3 to carry.

Three checks:

1. **Coverage** — for each document in the plan, every line from 1 to the
   document's current length falls inside some batch unit. Reports interior
   gaps and tail gaps separately; tails are the common case, because documents
   grow at the end.
2. **Claim containment** — every extracted claim's line span falls inside a
   plan unit for its own document. A claim outside the plan means the
   extraction surveyed lines the plan does not know about.
3. **Missing files** — a plan unit naming a document that is no longer on
   disk (archived or renamed without the plan following).

Exit status is 0 when clean and 1 when any check fails, so it can gate a
commit or a CI step.

Usage:
    python3 scripts/check_c4_plan_coverage.py
    python3 scripts/check_c4_plan_coverage.py --json          # machine-readable
    python3 scripts/check_c4_plan_coverage.py --extracted-only # ignore pending

Example:
    $ python3 scripts/check_c4_plan_coverage.py
    17 documents with unassigned lines (1,142 total)
      108 TAIL   results/55maps-ds-summary-v2/report.md (771 lines, last b074)
    ...
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = REPO_ROOT / "reports" / "verification" / "apparatus" / "c4-batch-plan.json"
EXTRACTION_DIR = REPO_ROOT / "reports" / "verification" / "c4-extraction"


def count_lines(path: Path) -> int:
    """Return the number of lines in a text file, tolerating odd encodings.

    Args:
        path: File to measure.

    Returns:
        Line count, matching what ``wc -l`` reports for a newline-terminated
        file.
    """
    with path.open(encoding="utf-8", errors="ignore") as handle:
        return sum(1 for _ in handle)


def load_plan(plan_path: Path, extracted_only: bool) -> tuple[dict, list]:
    """Load the batch plan and index its units by document.

    Args:
        plan_path: Path to ``c4-batch-plan.json``.
        extracted_only: When True, skip batches whose status is ``pending``.

    Returns:
        A ``(units_by_document, missing_files)`` pair. ``units_by_document``
        maps a repo-relative document path to a list of
        ``(start, end, batch_id, status)`` tuples.
    """
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    units: dict[str, list] = defaultdict(list)
    missing: list[tuple[str, str]] = []

    for batch in plan["batches"]:
        status = batch.get("status", "")
        if extracted_only and status.startswith("pending"):
            continue
        for unit in batch["units"]:
            doc = unit["file"]
            if not (REPO_ROOT / doc).exists():
                missing.append((doc, batch["batch_id"]))
                continue
            units[doc].append((unit["start"], unit["end"], batch["batch_id"], status))

    return units, missing


def find_gaps(segments: list, n_lines: int) -> list[tuple[int, int, str]]:
    """Find lines of a document not covered by any plan unit.

    Args:
        segments: ``(start, end, batch_id, status)`` tuples for one document.
        n_lines: Current length of that document.

    Returns:
        ``(start, end, kind)`` tuples where ``kind`` is ``"interior"`` or
        ``"TAIL"``. Overlapping segments are handled — coverage is the union,
        not the sum.
    """
    gaps: list[tuple[int, int, str]] = []
    cursor = 1
    for start, end, _batch, _status in sorted(segments):
        if start > cursor:
            gaps.append((cursor, start - 1, "interior"))
        cursor = max(cursor, end + 1)
    if cursor <= n_lines:
        gaps.append((cursor, n_lines, "TAIL"))
    return gaps


def check_claim_containment(units: dict[str, list]) -> list[dict]:
    """Find extracted claims whose line spans fall outside the plan.

    A claim outside every plan unit for its document means the extraction
    surveyed lines the plan does not account for — the inverse of a coverage
    gap, and just as much a drift signal.

    Args:
        units: Plan units indexed by document, as returned by :func:`load_plan`.

    Returns:
        One record per offending extraction file, with the count and the
        widest offending span.
    """
    offenders: list[dict] = []
    for extraction_path in sorted(EXTRACTION_DIR.glob("*.json")):
        data = json.loads(extraction_path.read_text(encoding="utf-8"))
        doc = data.get("source_document", {}).get("file")
        if not doc or doc not in units:
            continue
        covered = [(s, e) for s, e, _b, _st in units[doc]]
        outside = []
        for claim in data.get("claims", []):
            start, end = claim["source"]["lines"]
            if not any(s <= start and end <= e for s, e in covered):
                outside.append((start, end))
        if outside:
            offenders.append(
                {
                    "extraction": extraction_path.name,
                    "document": doc,
                    "claims_outside_plan": len(outside),
                    "widest_span": [min(s for s, _ in outside), max(e for _, e in outside)],
                }
            )
    return offenders


def main() -> int:
    """Run all three checks and report. Returns a process exit status."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--extracted-only",
        action="store_true",
        help="ignore batches still marked pending",
    )
    args = parser.parse_args()

    units, missing = load_plan(PLAN_PATH, args.extracted_only)

    gap_records = []
    for doc, segments in sorted(units.items()):
        n_lines = count_lines(REPO_ROOT / doc)
        gaps = find_gaps(segments, n_lines)
        if gaps:
            last = max(segments, key=lambda seg: seg[1])
            gap_records.append(
                {
                    "document": doc,
                    "doc_lines": n_lines,
                    "unassigned": sum(end - start + 1 for start, end, _ in gaps),
                    "gaps": [
                        {"start": s, "end": e, "kind": k} for s, e, k in gaps
                    ],
                    "last_batch": last[2],
                    "last_batch_pending": last[3].startswith("pending"),
                }
            )
    gap_records.sort(key=lambda rec: -rec["unassigned"])

    offenders = check_claim_containment(units)

    total_unassigned = sum(rec["unassigned"] for rec in gap_records)
    clean = not gap_records and not offenders and not missing

    if args.json:
        print(
            json.dumps(
                {
                    "clean": clean,
                    "documents_in_plan": len(units),
                    "documents_with_gaps": len(gap_records),
                    "total_unassigned_lines": total_unassigned,
                    "gaps": gap_records,
                    "claims_outside_plan": offenders,
                    "missing_files": [
                        {"document": doc, "batch": batch} for doc, batch in missing
                    ],
                },
                indent=1,
            )
        )
        return 0 if clean else 1

    print(f"documents in plan: {len(units)}")
    if missing:
        print(f"\nMISSING FROM DISK ({len(missing)}):")
        for doc, batch in missing:
            print(f"  {batch}  {doc}")

    if gap_records:
        print(
            f"\n{len(gap_records)} documents with unassigned lines "
            f"({total_unassigned:,} total):"
        )
        for rec in gap_records:
            kinds = ",".join(sorted({g["kind"] for g in rec["gaps"]}))
            state = "pending" if rec["last_batch_pending"] else "EXTRACTED"
            print(
                f"  {rec['unassigned']:5d} {kinds:8s} {rec['document']} "
                f"({rec['doc_lines']} lines, last {rec['last_batch']} [{state}])"
            )
    else:
        print("\ncoverage: every planned document fully assigned")

    if offenders:
        print(f"\n{len(offenders)} extractions with claims outside the plan:")
        for rec in offenders:
            print(
                f"  {rec['extraction']:28s} {rec['claims_outside_plan']:3d} claims, "
                f"widest {rec['widest_span']}  {rec['document']}"
            )
    else:
        print("claim containment: every extracted claim falls inside a plan unit")

    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
