"""Merge Task A's tilings and Task B's pools into the declarations file.

Reads ``out/t07_tilings.json`` (``declarations``: one ``pass_tilings`` entry
per T 0.7 cell) and ``out/rebuild_pools.json`` (``declarations``: one pool
declaration per K = 5 / K = 10 consensus a rebuild reproduced), and writes
them into ``inputs/provenance/assessed-area-declarations.json`` beside the
three declarations PR #26 made, which are kept unchanged. Re-running
replaces entries with the same key (pool path; tiling label), so the file
is reproducible from the two outputs.

Usage (any machine; small JSON only)::

    python write_declarations.py --repo . \
        --tilings out/t07_tilings.json --pools out/rebuild_pools.json

Created: 2026-10-08 (D57 (3), Session 163 follow-up)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

TARGET = "inputs/provenance/assessed-area-declarations.json"
PURPOSE = (
    "Assessed-area provenance DECLARED after the fact for legacy artefacts whose "
    "builders recorded too little. Read by scripts/lib_assessed_area. "
    "'declarations' are legacy candidate pools: either a footprint and clip (the "
    "three of 2026-10-07, method 'declared', every candidate checked to lie inside "
    "the declared area), or the pass_provenance a pre-2026-09-12 merge_passes "
    "consensus did not record, declared only where a rebuild from those passes "
    "reproduced the committed directory (2026-10-08, PI ruling D57 (3)). "
    "'pass_tilings' name the tile manifest of passes whose meta records none "
    "(2026-10-08, D57 (3)); the passes' own processed_tiles still define what they "
    "assessed. Every declared file is anchored to its git blob hash: a file "
    "rewritten after its declaration makes the area undetermined. A pool built "
    "after 2026-10-07 by a builder that calls write_area_record carries its own "
    "record beside the union and needs no entry here. Each entry cites the "
    "evidence it was reconstructed from; none is inferred from a path or a naming "
    "convention alone."
)


def main() -> int:
    """Merge and write the declarations file."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--tilings", type=Path, required=True)
    ap.add_argument("--pools", type=Path, required=True)
    args = ap.parse_args()
    target = args.repo / TARGET
    payload = json.loads(target.read_text(encoding="utf-8"))
    tilings = json.loads(args.tilings.read_text())["declarations"]
    pools = json.loads(args.pools.read_text())["declarations"]
    new_pools = {entry["pool"] for entry in pools}
    kept = [d for d in payload.get("declarations", []) if d["pool"] not in new_pools]
    new_labels = {entry["label"] for entry in tilings}
    kept_tilings = [t for t in payload.get("pass_tilings", [])
                    if t.get("label") not in new_labels]
    out = {
        "schema": "assessed-area-declarations/1",
        "created": payload.get("created", "2026-10-07"),
        "revised": "2026-10-08 (PI ruling D57 (3): pass_tilings and pool pass_provenance)",
        "ruling": "D51, D57 (planning/pi-decisions-2026-09-20.md)",
        "purpose": PURPOSE,
        "declarations": kept + sorted(pools, key=lambda e: e["pool"]),
        "pass_tilings": kept_tilings + tilings,
    }
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{target}: {len(out['declarations'])} declarations "
          f"({len(pools)} new), {len(out['pass_tilings'])} pass tilings "
          f"({sum(len(t['passes']) for t in out['pass_tilings'])} passes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
