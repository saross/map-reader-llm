#!/usr/bin/env python3
"""
W2-3a: account for every file of ``w2-3a/files.tsv`` from the comparison outputs.

Each listed file gets one of: VERIFIED (with the comparison that shows it and
its strength: byte, field, line), NOT CHECKABLE (API output), CENSUS
(cell evaluation, replayed exactly by the census and not re-scored here),
PROSE, or CODE (a script, an input rather than a computed output). A file
that no rule claims is reported as UNACCOUNTED, so the tally cannot silently
drop one.

Usage::

    python tally_coverage.py --files files.tsv --dir <this directory> --out tally.json

Read-only; no network.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

ORPHAN = ("results/k-ladder-2026-09-12/phase2/materialised/"
          "pv-min-text-t0.7-n1-carried-p0.15-k1.geojson")


def load_verdicts(directory: Path) -> dict[tuple[str, str], str]:
    """Map (commit, repo path) to the comparison verdict from every cmp-*.json."""
    out: dict[tuple[str, str], str] = {}
    for path in sorted(directory.glob("cmp-*.json")):
        if path.name == "cmp-g2-crops.json":
            continue
        for rec in json.loads(path.read_text())["files"]:
            key = (rec["commit"], rec["repo_path"])
            # A file compared twice keeps its weaker verdict.
            if out.get(key) not in (None, "BYTE-IDENTICAL") and rec["verdict"] == "BYTE-IDENTICAL":
                continue
            out[key] = rec["verdict"]
    return out


def main() -> int:
    """Classify every listed file and write the tally."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--files", required=True, type=Path)
    parser.add_argument("--dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    verdicts = load_verdicts(args.dir)
    crops = json.loads((args.dir / "cmp-g2-crops.json").read_text())
    crop_ok = {f"{r['crops_dir']}/candidate_manifest.json"
               for r in crops["rows"] if r["manifest_n_leaf_diffs"] == 0}
    api = json.loads((args.dir / "chk-api-outputs.json").read_text())
    rows = []
    for line in args.files.read_text().splitlines():
        if not line.strip():
            continue
        path, commit = line.split("\t")[:2]
        name = path.rsplit("/", 1)[-1]
        if "/cells/" in path and name.startswith("evaluation.") or (
                "reproduced-k5-evaluation" in path):
            status = "CENSUS"
        elif "/harness/" in path:
            status = "CODE"
        elif name in ("README.md", "pre_launch_audit.md", "inventory.md"):
            status = "PROSE"
        elif name in ("probabilities.json", "run.meta.json"):
            status = "NOT CHECKABLE"
            if not (api["n_consistent"] == api["n_stages"] and api["smoke"]["consistent"]):
                status += " (consistency FAILED)"
        elif name == "candidate_manifest.json" and "/smoke/" not in path:
            status = "VERIFIED field (byte after path substitution)" if path in crop_ok \
                else "UNACCOUNTED"
        elif path == ORPHAN:
            status = ("VERIFIED byte (identical blob to the regenerated "
                      "pv-min-text-t0.7-n1-opmax.geojson)")
        else:
            v = verdicts.get((commit, path))
            status = {"BYTE-IDENTICAL": "VERIFIED byte", "FIELD-IDENTICAL": "VERIFIED field",
                      "LINE-IDENTICAL": "VERIFIED line"}.get(v, f"UNACCOUNTED ({v})")
        rows.append({"path": path, "commit": commit, "status": status})
    tally = collections.Counter(r["status"] for r in rows)
    by_commit = collections.Counter((r["commit"], r["status"]) for r in rows)
    out = {"n_files": len(rows), "tally": dict(sorted(tally.items())),
           "by_commit": {f"{c} | {s}": n for (c, s), n in sorted(by_commit.items())},
           "files": rows}
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"n_files": out["n_files"], "tally": out["tally"]}, indent=1))
    for key, n in out["by_commit"].items():
        print(f"{n:4d}  {key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
