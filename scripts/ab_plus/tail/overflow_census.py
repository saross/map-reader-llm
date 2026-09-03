"""Census of the overflow structuring batch (read-only).

Promoted 2026-09-03 from the S147 scratch driver. Prints the overflow
manifest's status counts, sidecar item statistics, and checks every
rendered entry for an Overflow section and for withheld items.

Usage (from the repo root)::

    python3 scripts/ab_plus/tail/overflow_census.py
"""

from __future__ import annotations

import json
import os
import re
import statistics
from collections import Counter

REPO = "/home/shawn/Code/map-reader-llm"
MANIFEST = f"{REPO}/outputs/ab-plus/manifests/overflow-2026-09-03.json"
WORK = f"{REPO}/outputs/ab-plus/_work"
DELIVERABLES = f"{REPO}/outputs/ab-plus"


def main() -> None:
    """Print the census."""
    rows = json.load(open(MANIFEST))["sources"]
    print("status:", dict(Counter(r["status"] for r in rows)))
    n_items: list[int] = []
    missing: list[str] = []
    no_appendix: list[str] = []
    withheld = 0
    for r in rows:
        key = r["citekey"]
        sidecar = f"{WORK}/{key}.overflow.json"
        if not os.path.exists(sidecar):
            missing.append(key)
            continue
        n_items.append(len(json.load(open(sidecar))["items"]))
        rendered = f"{DELIVERABLES}/{key.lower()}.md"
        text = open(rendered).read() if os.path.exists(rendered) else ""
        if "## Overflow" not in text:
            no_appendix.append(key)
        match = re.search(r"Overflow span check: \*\*(\d+)/(\d+) passed", text)
        if match and match.group(1) != match.group(2):
            withheld += int(match.group(2)) - int(match.group(1))
    if n_items:
        print(
            f"sidecars: {len(n_items)} items total: {sum(n_items)} "
            f"median: {statistics.median(n_items)} min: {min(n_items)} max: {max(n_items)} "
            f"at cap (12): {sum(1 for x in n_items if x == 12)}"
        )
    print("missing sidecar:", missing)
    print("rendered without Overflow section:", no_appendix)
    print("withheld items across corpus:", withheld)


if __name__ == "__main__":
    main()
