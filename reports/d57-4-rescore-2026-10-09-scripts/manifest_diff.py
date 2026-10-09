"""Scripted diff of the register manifests: what ``--all --write`` would change, and did.

D57 (4) re-score, 2026-10-09 (Session 163); plan § 3.3 and § 7 row 2 (c).
Read-only; writes ``--out``.

Two modes:

* ``--dry-run-output FILE`` — parse the JSON row arrays that
  ``generate_post_run_report.py --all --dry-run`` prints (``--- runs ---``,
  ``--- conditions ---``, ``--- passes ---``, ``--- analyses ---``) and compare
  each row with the committed manifest's row of the same id, timestamps
  blanked by the generator's own ``_strip_ts``. This is what ``--write`` would
  change.
* ``--after-write`` — compare the working tree's written manifests with
  ``HEAD``: rows whose content changed, and whether every other row is
  byte-identical (its serialised JSON, timestamps included).

In both modes the changed condition ids are compared with the expected set:
the condition ids of the Phase 2 registered cells (the ``conditions`` column of
``moved_new.csv`` for cells in the Phase 2 list).

Usage (on sapphire, from the NEW worktree)::

    .venv/bin/python manifest_diff.py --repo . --cells …/phase2_cells.json \\
        --dry-run-output …/manifest_dry_run.txt --out …/manifest_dry_diff.json
    .venv/bin/python manifest_diff.py --repo . --cells …/phase2_cells.json \\
        --after-write --out …/manifest_written_diff.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d57_common as dc  # noqa: E402

MANIFESTS = {"runs": ("results/runs-manifest.json", "runs", "run_id"),
             "conditions": ("results/conditions-manifest.json", "conditions", "condition_id"),
             "passes": ("results/passes-manifest.json", "passes", "pass_id"),
             "analyses": ("results/analyses-manifest.json", "analyses", "analysis_id")}
MOVED_CSV = "reports/scorer-frames-d50-d51-2026-10-08-scripts/out/summary/moved_new.csv"


def parse_dry_run(text: str) -> dict[str, list[dict[str, Any]]]:
    """Extract the four row arrays from ``--dry-run`` output."""
    out: dict[str, list[dict[str, Any]]] = {}
    dec = json.JSONDecoder()
    for name in MANIFESTS:
        marker = f"\n--- {name} ---\n"
        i = text.find(marker)
        if i < 0:
            raise ValueError(f"no '{marker.strip()}' section")
        out[name], _ = dec.raw_decode(text, i + len(marker))
    return out


def field_diffs(new: dict[str, Any], old: dict[str, Any], strip: Any) -> list[str]:
    """Top-level fields (and metric buffers) whose stripped content differs."""
    keys = []
    for k in sorted(set(new) | set(old)):
        if strip(new.get(k)) == strip(old.get(k)):
            continue
        if k == "metrics" and isinstance(new.get(k), dict) and isinstance(old.get(k), dict):
            npb = (new[k].get("per_buffer") or {})
            opb = (old[k].get("per_buffer") or {})
            bufs = [b for b in sorted(set(npb) | set(opb), key=lambda s: int(s))
                    if strip(npb.get(b)) != strip(opb.get(b))]
            other = [m for m in sorted(set(new[k]) | set(old[k]))
                     if m != "per_buffer" and strip(new[k].get(m)) != strip(old[k].get(m))]
            keys.append(f"metrics(buffers={','.join(bufs)};{','.join(other)})")
        else:
            keys.append(k)
    return keys


def main() -> int:
    """Compare manifests and write the diff record."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--cells", type=Path, required=True)
    ap.add_argument("--dry-run-output", type=Path, default=None)
    ap.add_argument("--after-write", action="store_true")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    sys.path.insert(0, str(repo))
    from scripts.generate_post_run_report import _strip_ts  # noqa: PLC0415

    phase2 = {c["eval"] for c in json.loads(args.cells.read_text())}
    expected: set[str] = set()
    for r in csv.DictReader((repo / MOVED_CSV).open()):
        if r["eval"] in phase2 and r["conditions"]:
            expected |= {c for c in r["conditions"].split(";") if c}
    if args.dry_run_output:
        new_rows = parse_dry_run(args.dry_run_output.read_text())
    elif args.after_write:
        new_rows = {name: json.loads((repo / rel).read_text())[key]
                    for name, (rel, key, _) in MANIFESTS.items()}
    else:
        sys.exit("give --dry-run-output or --after-write")
    report: dict[str, Any] = {"expected_condition_ids": sorted(expected), "manifests": {}}
    for name, (rel, key, idf) in MANIFESTS.items():
        old = {r[idf]: r for r in json.loads(dc.git_show_bytes(repo, "HEAD", rel))[key]}
        new = {r[idf]: r for r in new_rows[name]}
        changed = {i: field_diffs(new[i], old[i], _strip_ts) for i in sorted(set(new) & set(old))
                   if _strip_ts(new[i]) != _strip_ts(old[i])}
        rec: dict[str, Any] = {"n_old": len(old), "n_new": len(new),
                               "added": sorted(set(new) - set(old)),
                               "removed": sorted(set(old) - set(new)),
                               "changed": changed}
        if args.after_write:
            rec["unchanged_rows_not_byte_identical"] = sorted(
                i for i in set(new) & set(old) if i not in changed
                and json.dumps(new[i], sort_keys=True) != json.dumps(old[i], sort_keys=True))
        report["manifests"][name] = rec
    cond = set(report["manifests"]["conditions"]["changed"])
    report["conditions_changed_not_expected"] = sorted(cond - expected)
    report["conditions_expected_not_changed"] = sorted(expected - cond)
    args.out.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({
        "expected": len(expected),
        **{n: {"changed": len(r["changed"]), "added": len(r["added"]),
               "removed": len(r["removed"]),
               **({"unchanged_not_identical": len(r["unchanged_rows_not_byte_identical"])}
                  if args.after_write else {})}
           for n, r in report["manifests"].items()},
        "changed_not_expected": report["conditions_changed_not_expected"],
        "expected_not_changed": report["conditions_expected_not_changed"],
        "non_condition_changes": {n: sorted(r["changed"])[:20]
                                  for n, r in report["manifests"].items()
                                  if n != "conditions" and r["changed"]},
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
