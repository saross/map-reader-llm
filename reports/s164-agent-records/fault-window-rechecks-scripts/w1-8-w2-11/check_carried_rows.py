#!/usr/bin/env python3
"""
Check a carried verifier stage's rows against the carry harness's output.

Fault-window re-check (2026-10-14), row W2-11, commit f8e0eb600. The carry
harness seeds ``probabilities.json`` with the results re-keyed from the old
stage; ``run_pv.py verify`` (real time) then called the API for the
uncovered candidates only and rewrote the file. So the committed rows split
into (a) carried rows, which must equal the harness's seeded rows exactly,
and (b) the newly called rows, which are API outputs and not re-checkable,
and must be exactly the keys the carry record lists as uncovered.

Usage: python check_carried_rows.py REPO OUT_JSON KEY=SEEDED_JSON=COMMITTED_PATH [...]

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

C = "f8e0eb600"


def main() -> int:
    """Compare and write the summary."""
    repo, out = sys.argv[1], Path(sys.argv[2])
    rows = []
    for spec in sys.argv[3:]:
        key, seeded_path, committed_path = spec.split("=")
        seeded = json.loads(Path(seeded_path).read_text())["results"]
        committed = json.loads(subprocess.run(
            ["git", "-C", repo, "show", f"{C}:{committed_path}"],
            capture_output=True, check=True).stdout)["results"]
        prov = json.loads(subprocess.run(
            ["git", "-C", repo, "show",
             f"{C}:{str(Path(committed_path).parent / 'carry_provenance.json')}"],
            capture_output=True, check=True).stdout)
        uncovered = sorted(u["new_key"] for u in prov.get("uncovered_detail", []))
        carried_equal = [k for k in seeded if committed.get(k) == seeded[k]]
        carried_diff = [k for k in seeded if committed.get(k) != seeded[k]]
        new_rows = sorted(set(committed) - set(seeded))
        rows.append({"key": key, "n_seeded": len(seeded), "n_committed": len(committed),
                     "carried_rows_equal": len(carried_equal),
                     "carried_rows_differing": carried_diff[:10],
                     "new_rows": new_rows, "uncovered_in_record": uncovered,
                     "new_rows_are_exactly_uncovered": new_rows == uncovered})
        print(f"{key}: {len(carried_equal)}/{len(seeded)} carried rows equal; "
              f"{len(carried_diff)} differ; new rows {new_rows} == uncovered "
              f"{new_rows == uncovered}")
    out.write_text(json.dumps(rows, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
