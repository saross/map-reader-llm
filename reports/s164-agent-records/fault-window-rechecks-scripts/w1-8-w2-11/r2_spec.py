#!/usr/bin/env python3
"""
Write the comparison spec for the regenerated r2 board home (7894b5b5a).

Fault-window re-check (2026-10-14), row W2-11. Pairs every file 7894b5b5a
committed under results/55map-final-board-r2-2026-09-06/ (31 cell
materialisations, cells_manifest.json, 22 sweep CSVs, sweeps.json) with the
file of the same relative path in the regenerated home, for compare_files.py.
No ignores are declared.

Usage: python r2_spec.py REPO REGEN_HOME SPEC_JSON

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

C = "7894b5b5a"
HOME = "results/55map-final-board-r2-2026-09-06"


def main() -> int:
    """Build the spec from the commit's own file list."""
    repo, regen, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    files = subprocess.run(["git", "-C", repo, "show", "--name-only", "--format=", C, "--", HOME],
                           capture_output=True, text=True, check=True).stdout.split()
    spec = [{"label": f"r2 {f[len(HOME) + 1:]}", "regen": str(regen / f[len(HOME) + 1:]),
             "commit": C, "path": f} for f in sorted(files)]
    out.write_text(json.dumps(spec, indent=1) + "\n")
    print(f"{len(spec)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
