"""List what the re-score changed in the NEW worktree, and check nothing forbidden moved.

D57 (4) re-score, 2026-10-09 (Session 163); plan § 7 row 2 (b). Read-only;
writes ``--out`` (JSON) and ``--out`` with a ``.txt`` suffix (one path per line:
the files that would be copied into the tracked tree).

From ``git status --porcelain --untracked-files=all`` in the worktree:

* every changed path is classified (cell trio, stride sweep, manifest, registry,
  this step's own scripts, other);
* the forbidden classes of plan § 7 row 2 (b) must be absent: any detection
  GeoJSON, union, ``detections_dedup``, crop manifest, or ``probabilities.json``;
* every Phase 2 cell must show its ``evaluation.json`` and ``evaluation.md`` as
  modified (``evaluation.csv`` changes only where a four-decimal value moved);
* anything else is reported as unexpected.

The copy list excludes this step's own scripts directory (it is reported
separately, as a candidate for committing alongside the outputs).

Usage::

    .venv/bin/python copy_list.py --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --cells ~/scratch/d57-4-rescore-2026-10-09/out/phase2_cells.json \\
        --out ~/scratch/d57-4-rescore-2026-10-09/out/copy_list.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

SCRIPTS_DIR = "reports/d57-4-rescore-2026-10-09-scripts/"
FORBIDDEN = re.compile(r"(detections[^/]*\.geojson$|union[^/]*\.geojson$|detections_dedup|"
                       r"candidate_manifest\.json$|probabilities\.json$|"
                       r"/consensus[^/]*\.geojson$|verified[^/]*\.geojson$)")
EXPECTED_OTHER = {
    "results/conditions-manifest.json", "results/conditions-manifest.md",
    "results/runs-manifest.md", "results/passes-manifest.md",
    "results/analyses-manifest.md", "results/run-registry.md",
    "reports/verification/generated-file-registry.json",
    "results/stride55-2026-08-27/g384_ov128_55map/sweep_50m.csv",
    "results/stride55-2026-08-27/g384_ov192_55map/sweep_50m.csv",
    "results/stride55-2026-08-27/g384_ov128_55map/ladder_sweep_50m.csv",
    "results/stride55-2026-08-27/g384_ov192_55map/ladder_sweep_50m.csv",
    "results/stride55-2026-08-27/sweep_oracle.json",
    "results/stride55-2026-08-27/ladder.json",
}


def main() -> int:
    """Classify the worktree's changes and write the copy list."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--cells", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    porcelain = subprocess.run(["git", "-C", str(repo), "status", "--porcelain",
                                "--untracked-files=all"], capture_output=True, text=True,
                               check=True).stdout.splitlines()
    entries = [(line[:2], line[3:]) for line in porcelain]
    cells = {str(Path(c["eval"]).parent) for c in json.loads(args.cells.read_text())}
    classes: dict[str, list[str]] = {"cell": [], "other-expected": [], "scripts": [],
                                     "forbidden": [], "unexpected": []}
    for status, path in entries:
        if path.startswith(SCRIPTS_DIR):
            classes["scripts"].append(path)
        elif FORBIDDEN.search(path):
            classes["forbidden"].append(f"{status} {path}")
        elif status.strip() == "M" and str(Path(path).parent) in cells and \
                Path(path).name in ("evaluation.json", "evaluation.csv", "evaluation.md"):
            classes["cell"].append(path)
        elif status.strip() == "M" and path in EXPECTED_OTHER:
            classes["other-expected"].append(path)
        else:
            classes["unexpected"].append(f"{status} {path}")
    changed_by_cell = Counter(str(Path(p).parent) for p in classes["cell"])
    names = Counter(Path(p).name for p in classes["cell"])
    missing_json_md = sorted(
        c for c in cells
        if not {f"{c}/evaluation.json", f"{c}/evaluation.md"} <= set(classes["cell"]))
    copy = sorted(classes["cell"] + classes["other-expected"])
    top = Counter("/".join(p.split("/")[:2]) for p in copy)
    report = {"n_status_lines": len(entries), "counts": {k: len(v) for k, v in classes.items()},
              "cell_files_by_name": dict(names), "cells_with_changes": len(changed_by_cell),
              "cells_missing_json_or_md": missing_json_md,
              "copy_count": len(copy), "copy_by_top_directory": dict(sorted(top.items())),
              "forbidden": classes["forbidden"], "unexpected": classes["unexpected"],
              "other_expected": classes["other-expected"], "scripts": classes["scripts"]}
    args.out.write_text(json.dumps(report, indent=1) + "\n")
    args.out.with_suffix(".txt").write_text("\n".join(copy) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "scripts"}, indent=1)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
