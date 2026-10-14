#!/usr/bin/env python3
"""
Structured diff of a repaired probabilities file: generating commit vs head.

Fault-window re-check (2026-10-14), row W1-8. Run B's ``verify_*_repaired/
probabilities.json`` files were later extended in place by the D62 (1)
wrong-sheet re-verification (f2256f7c7, 2026-10-13). This shows, per file,
which result keys changed between the generating commit and the head, which
top-level keys were added, and whether the changed keys are exactly the rows
the re-verification record (``reverify-wrong-sheet-2026-10-13.json``) names.

Usage: python later_change_diff.py REPO HEAD OUT_JSON PATH=COMMIT [...]

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def show(repo: str, commit: str, path: str) -> dict | None:
    """Parsed JSON of ``commit:path`` or None."""
    r = subprocess.run(["git", "-C", repo, "show", f"{commit}:{path}"],
                       capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def keys_named(record: dict | None) -> set[str]:
    """Every ``candidate_NNNNN`` string anywhere in a re-verification record."""
    found: set[str] = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(k, str) and k.startswith("candidate_"):
                    found.add(k)
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and x.startswith("candidate_"):
            found.add(x)
    walk(record)
    return found


def main() -> int:
    """Diff each file and write the summary."""
    repo, head, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    rows = []
    for spec in sys.argv[4:]:
        path, commit = spec.split("=")
        a, b = show(repo, commit, path), show(repo, head, path)
        ra, rb = a["results"], b["results"]
        changed = sorted(k for k in set(ra) | set(rb) if ra.get(k) != rb.get(k))
        rec = show(repo, head, str(Path(path).parent / "reverify-wrong-sheet-2026-10-13.json"))
        named = keys_named(rec)
        changed_fields = sorted({f for k in changed for f in set(ra.get(k, {})) | set(rb.get(k, {}))
                                 if (ra.get(k) or {}).get(f) != (rb.get(k) or {}).get(f)})
        log = subprocess.run(["git", "-C", repo, "log", "--format=%h %s", f"{commit}..{head}",
                              "--", path], capture_output=True, text=True).stdout.splitlines()
        rows.append({
            "path": path, "generating": commit, "changed_by": log,
            "n_results_generating": len(ra), "n_results_head": len(rb),
            "n_changed_results": len(changed),
            "changed_fields": changed_fields,
            "top_level_added": sorted(set(b) - set(a)),
            "top_level_removed": sorted(set(a) - set(b)),
            "top_level_changed": sorted(k for k in set(a) & set(b)
                                        if k != "results" and a[k] != b[k]),
            "reverify_record_present": rec is not None,
            "changed_subset_of_reverify_named": set(changed) <= named,
            "n_named_in_reverify_record": len(named & set(rb)),
        })
        r = rows[-1]
        print(f"{path.split('/')[2]}/{path.split('/')[-2]}: {r['n_changed_results']} rows "
              f"changed ({r['changed_fields']}); all named by the re-verify record: "
              f"{r['changed_subset_of_reverify_named']}; added top-level "
              f"{r['top_level_added']}; by {r['changed_by']}")
    out.write_text(json.dumps(rows, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
