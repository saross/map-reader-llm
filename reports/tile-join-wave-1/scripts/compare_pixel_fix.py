#!/usr/bin/env python3
"""
Every verdict the pixel-convention fix changed (tile-join Wave 1, seam audit).

Compares the outputs of the seam checks before and after commit 768cb2a9b,
which made ``sheet_check_55map.world_to_pixel`` return edge-indexed pixel
coordinates (the containing pixel is the floor; before, a centre-indexed
coordinate was floored). It lists, per reference file, every contact whose
verdict changed in the 55-map recipient check (from the full outputs, padding
included), every changed GS-frame verdict, and every own-sheet contact whose
own verdict, recipient verdict, class, or original-coordinate verdict changed,
with the class tallies before and after. Standard library only; reads JSON.

The full 55-map outputs are not committed (size); they are read from zbook
scratch: the pre-fix run ``~/scratch/wave1/w10/sheet-check/sheet_check_55map.json``
(at ``c1a7a23fd``) and the post-fix run
``~/scratch/wave1/seam2/pixfix/sheet_check_55map.json``. The other inputs are
the committed ``out/*-pre-pixel-fix.json`` and ``out/*.json`` files.

Usage (zbook)::

    ~/Code/map-reader-llm/.venv/bin/python \\
        reports/tile-join-wave-1/scripts/compare_pixel_fix.py \\
        > reports/tile-join-wave-1/scripts/out/compare_pixel_fix.txt

Created: 2026-11-19 (tile-join Wave 1, seam pixel-convention fix, zbook)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

OUT = Path(__file__).resolve().parent / "out"
FULL_BEFORE = Path("~/scratch/wave1/w10/sheet-check/sheet_check_55map.json")
FULL_AFTER = Path("~/scratch/wave1/seam2/pixfix/sheet_check_55map.json")
OWN_FIELDS = ("own_verdict", "recipient_verdict", "candidate_class",
              "original_own_verdict")


def load(path: Path) -> Any:
    """Read a JSON file (``~`` expanded)."""
    return json.loads(path.expanduser().read_text())


def compare_recipient() -> None:
    """Print every changed contact verdict of the 55-map recipient check."""
    print("== 55-map recipient check (full outputs, padding included)")
    before, after = load(FULL_BEFORE), load(FULL_AFTER)
    for ref, entry in before["references"].items():
        def keyed(contacts: list[dict]) -> dict[tuple, dict]:
            return {(c["ref_sheet"], c["ref_id"], c["x"], c["y"], c["tile"]): c
                    for c in contacts}
        old = keyed(entry["contacts"])
        new = keyed(after["references"][ref]["contacts"])
        if old.keys() != new.keys():
            raise SystemExit(f"contact sets differ for {ref}")
        changed = [k for k in old if old[k]["verdict"] != new[k]["verdict"]]
        print(f"{Path(ref).name}: {len(old)} contacts; before "
              f"{entry['verdicts']}; after {after['references'][ref]['verdicts']}; "
              f"changed {len(changed)}")
        for k in changed:
            fa = old[k]["pixels"]["window_near_black_fraction"]
            fb = new[k]["pixels"]["window_near_black_fraction"]
            print(f"    {k[1]} ({k[0]}) in {k[4]}: {old[k]['verdict']} "
                  f"(window {fa}) -> {new[k]['verdict']} (window {fb})")


def compare_gs() -> None:
    """Print every changed contact verdict of the GS-frames check."""
    print("== GS frames")

    def keyed(data: dict) -> dict[tuple, str | None]:
        return {(frame, c.get("fid"), c["tile"]): c.get("verdict")
                for frame, entry in data["frames"].items()
                for c in entry["contacts"]}
    old = keyed(load(OUT / "sheet_check_gs_frames-pre-pixel-fix.json"))
    new = keyed(load(OUT / "sheet_check_gs_frames.json"))
    if old.keys() != new.keys():
        raise SystemExit("GS contact sets differ")
    print(f"{len(old)} contacts; before {dict(Counter(old.values()))}; "
          f"after {dict(Counter(new.values()))}")
    for k in old:
        if old[k] != new[k]:
            print(f"    {k}: {old[k]} -> {new[k]}")


def compare_own_sheet() -> None:
    """Print every changed own-sheet contact and the class tallies."""
    print("== own sheet")
    before = load(OUT / "seam_own_sheet-pre-pixel-fix.json")
    after = load(OUT / "seam_own_sheet.json")
    for ref, o in before["references"].items():
        n = after["references"][ref]

        def keyed(records: list[dict]) -> dict[tuple, tuple]:
            return {(r["ref_id"], r["feature_key"], r["recipient_tile"]):
                    tuple(r[f] for f in OWN_FIELDS) for r in records}
        old, new = keyed(o["contact_records"]), keyed(n["contact_records"])
        print(f"{Path(ref).name}: contacts {len(old)} -> {len(new)}; pairs "
              f"{o['n_pairs']} -> {n['n_pairs']}  (fields: {', '.join(OWN_FIELDS)})")
        for k in sorted(set(old) | set(new)):
            if old.get(k) != new.get(k):
                print(f"    {k}: {old.get(k)} -> {new.get(k)}")
        for level in ("pair_rows", "contact_records"):
            cb = dict(Counter(r["candidate_class"] for r in o[level]))
            ca = dict(Counter(r["candidate_class"] for r in n[level]))
            print(f"    {level} classes: before {cb}; after {ca}")
        print(f"    after, features by own / recipient: "
              f"{n['features_by_own_and_recipient']}")
        print(f"    after, original by final own: {n['original_own_by_final_own']}")


def main() -> None:
    """Run the three comparisons."""
    compare_recipient()
    compare_gs()
    compare_own_sheet()


if __name__ == "__main__":
    main()
