#!/usr/bin/env python3
"""
Count the image campaigns' tracked files last changed in W2, by kind.

Fault-window re-check (2026-10-14), row W2-11. Takes every tracked file under
the two image-campaign output directories at HEAD, finds the commit that
last changed it, and keeps those whose committer date (UTC) falls in W2
(2026-09-05T06:58Z to 2026-10-05T04:14Z). Each is labelled with what this
re-check did with it, so the coverage figures are mechanical.

Usage: python count_image_w2.py REPO HEAD OUT_JSON

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DIRS = ("outputs/gemini37-image-55map-2026-09-13", "outputs/gemini3-image-55map-2026-09-16")
W2 = (datetime(2026, 9, 5, 6, 58, tzinfo=timezone.utc),
      datetime(2026, 10, 5, 4, 14, tzinfo=timezone.utc))
#: legs re-parsed from batch_results.jsonl (probabilities + run.meta checked)
REPARSED = ("verify_k5_arm1_replicate-batch-2026-09-20/",
            "verify_k5_arm2_replicate-batch-2026-09-20/",
            "probe-batch-vs-flex-2026-09-19/verify_batch/", "g3img/verify_k1_arm2/",
            "g3img/verify_k3_arm2/", "g3img/verify_k5_arm2/")


def kind(path: str) -> str:
    """What this re-check did with a file (by path pattern)."""
    name = path.rsplit("/", 1)[-1]
    if name.endswith((".log", ".nohup", ".md")):
        return "log or prose (not a computation)"
    if "/batch-staging-run" in path:
        return "chunk API output (NOT CHECKABLE; source of the re-merge)"
    if re.search(r"g37img/run_[45]/detections-.*2026-09-17\.(geojson|meta\.json|tiles\.json)$",
                 path):
        return "merged pass re-derived from chunks (checked)"
    if re.search(r"/union_k\d(_pass_provenance)?\.(geojson|json)$", path):
        return "union or provenance sidecar (checked)"
    if re.search(r"g37img/crops_k\d/candidate_manifest\.json$", path):
        return "crop manifest re-extracted (checked)"
    if any(r in path for r in REPARSED) and name in ("probabilities.json", "run.meta.json"):
        return "batch leg re-parsed (checked)"
    if name in ("batch_results.jsonl", "batch_jobs.json", "batch_jobs_relodged.json"):
        return "raw batch results or job record (NOT CHECKABLE)"
    if "/verify_" in path:
        return "flex leg or earlier-state sidecar (NOT CHECKABLE)"
    if re.search(r"/run_\d+(_recovery\w*)?/detections-", path) or "/smoke/" in path:
        return "proposer pass API output (NOT CHECKABLE)"
    return "other (not attempted)"


def main() -> int:
    """Count and write."""
    repo, head, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    files = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", head, *DIRS],
                           capture_output=True, text=True, check=True).stdout.split()
    rows = []
    for f in files:
        ct = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%h %ct", head, "--", f],
                            capture_output=True, text=True).stdout.split()
        when = datetime.fromtimestamp(int(ct[1]), tz=timezone.utc)
        if W2[0] <= when < W2[1]:
            rows.append({"path": f, "commit": ct[0], "when": when.isoformat(), "kind": kind(f)})
    counts = Counter(r["kind"] for r in rows)
    res = {"n_files_in_dirs": len(files), "n_last_changed_in_w2": len(rows),
           "by_kind": dict(sorted(counts.items())),
           "other": [r["path"] for r in rows if r["kind"].startswith("other")]}
    out.write_text(json.dumps({"summary": res, "rows": rows}, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
