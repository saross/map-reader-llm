#!/usr/bin/env python3
"""
Re-apply c053f5a41's documented meta correction and compare with the commit.

Fault-window re-check (2026-10-14), row W2-11. c053f5a41 (2026-09-08) rebuilt
h12-v2::r3-hp-heavy::run_3's ``completed_items`` from its GeoJSON's
``processed_tiles`` (the recovered tile never reached the GeoJSON), moved
the tile to ``failed_items``, set items_processed/items_failed, added an
``execution_stats._correction`` block, and repaired the tiles sidecar. No
script was committed for it, so this applies the rule as the commit body
states it to the pre-commit files and checks (a) the parsed result equals
the committed meta exactly, (b) the tiles sidecar's completed list equals
the GeoJSON's processed tiles, (c) whether a plain re-serialisation
(indent 2, ensure_ascii False) gives the committed bytes.

Usage: python check_c053f5a41.py REPO OUT_JSON

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

C = "c053f5a41"
DIR = "outputs/h12-v2/r3-hp-heavy/run_3"
STEM = "detections-detect_h12_r3-hp-heavy_v2-3-flash-2026-04-15"


def show(repo: str, rev: str, path: str) -> bytes:
    """Bytes of rev:path."""
    return subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                          capture_output=True, check=True).stdout


def main() -> int:
    """Apply, compare, report."""
    repo, out = sys.argv[1], Path(sys.argv[2])
    before = json.loads(show(repo, f"{C}^", f"{DIR}/{STEM}.meta.json"))
    after_b = show(repo, C, f"{DIR}/{STEM}.meta.json")
    after = json.loads(after_b)
    gj = json.loads(show(repo, C, f"{DIR}/{STEM}.geojson"))
    gj_before = (show(repo, f"{C}^", f"{DIR}/{STEM}.geojson")
                 == show(repo, C, f"{DIR}/{STEM}.geojson"))
    tiles_after = json.loads(show(repo, C, f"{DIR}/{STEM}.tiles.json"))
    processed = set(gj["processed_tiles"])
    es = before["execution_stats"]
    lost = [t for t in es["completed_items"] if t not in processed]
    rebuilt = copy.deepcopy(before)
    res = rebuilt["execution_stats"]
    res["completed_items"] = [t for t in es["completed_items"] if t in processed]
    res["items_processed"] = len(res["completed_items"])
    res["items_failed"] = len(lost)
    res["failed_items"] = [dict(item=t,
                                 reason=after["execution_stats"]["failed_items"][i]["reason"])
                           for i, t in enumerate(lost)]
    # the _correction block's prose is the commit's own; its numbers are checked
    corr = after["execution_stats"]["_correction"]
    res["_correction"] = corr
    numbers_ok = (corr["completed_before"] == len(es["completed_items"])
                  and corr["completed_after"] == len(res["completed_items"]))
    # key order as committed: _correction last in execution_stats
    res = {k: res[k] for k in after["execution_stats"]}
    rebuilt["execution_stats"] = res
    reser = (json.dumps(rebuilt, indent=2, ensure_ascii=False)).encode()
    result = {
        "geojson_unchanged_by_commit": gj_before,
        "geojson_processed_tiles": len(processed),
        "completed_before": len(es["completed_items"]),
        "tiles_removed": lost,
        "parsed_meta_equal": rebuilt == after,
        "correction_numbers_consistent": numbers_ok,
        "reserialised_bytes_equal": reser == after_b,
        "reserialised_bytes_equal_ignoring_final_newline": (reser.rstrip(b"\n")
                                                             == after_b.rstrip(b"\n")),
        "tiles_sidecar_completed_equals_geojson": set(tiles_after["completed"]) == processed,
        "tiles_sidecar_counts": [len(tiles_after["completed"]), tiles_after.get("total_tiles")],
    }
    out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
