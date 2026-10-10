"""Prove the D57 (3) declaration tests bite: break each rule once, expect red.

Builds a REAL copy of the branch head with ``git archive`` (no symlinks, so
no test module resolves its imports back into the worktree — the failure
mode of the 2026-09-20 mutation harness), runs ``tests/test_assessed_area.py``
green, then applies one mutation at a time to the copy's
``scripts/lib_assessed_area.py`` (each must match its source text exactly
once), runs the file again, and restores the original. Every mutation must
turn the named test(s) red; the ladder-builder wiring tests are deselected
in the copy, as in PR #26's harness, because the builder computes the passes
register at import from per-pass artefacts the copy does not carry.

Usage (sapphire)::

    ~/Code/map-reader-llm/.venv/bin/python red_sentinel.py \
        --worktree ~/worktrees/map-reader-llm/claude-d51-ladder-provenance \
        --scratch ~/scratch/d51-ladder-provenance-2026-10-08 --out out/red_sentinel.json

Created: 2026-10-08 (D57 (3), Session 163 follow-up)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

PY = str(Path.home() / "Code/map-reader-llm/.venv/bin/python")
LIB = "scripts/lib_assessed_area.py"

#: (name, source text, replacement, tests that must turn red)
MUTATIONS = [
    ("declared tilings never consulted",
     "    declared = _declared_pass_tilings().get(rel)\n",
     "    declared = None  # RED SENTINEL\n",
     ["test_a_declared_tiling_resolves_a_pass_whose_meta_records_none"]),
    ("processed tiles outside the manifest accepted",
     "        if not processed <= set(_manifest_names(manifest)):\n",
     "        if False:  # RED SENTINEL\n",
     ["test_a_declared_tiling_naming_a_tile_outside_its_manifest_refuses"]),
    ("blob anchor not checked",
     "    if actual != declared_hash:\n",
     "    if False:  # RED SENTINEL\n",
     ["test_a_pass_rewritten_after_its_tiling_was_declared_is_undetermined",
      "test_declared_pass_provenance_refuses_a_rewritten_pass"]),
    ("meta and declaration may disagree",
     '    if recorded is not None and recorded != declared["manifest"]:\n',
     "    if False:  # RED SENTINEL\n",
     ["test_a_declared_tiling_that_contradicts_the_meta_is_undetermined"]),
    ("a pass may be declared twice",
     '            if item["path"] in out:\n',
     "            if False:  # RED SENTINEL\n",
     ["test_a_pass_declared_twice_is_undetermined"]),
    ("a declaration may name two routes",
     '            if declared.get("footprint") or declared.get("clip"):\n',
     "            if False:  # RED SENTINEL\n",
     ["test_a_declaration_naming_two_routes_is_refused"]),
]


def run(copy: Path) -> dict:
    """Run the assessed-area tests in the copy; return pass/fail by test name."""
    proc = subprocess.run(
        [PY, "-m", "pytest", "-p", "no:cacheprovider", "-q", "-rf",
         "-k", "not ladder_builder", "tests/test_assessed_area.py"],
        cwd=copy, capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    failed = sorted({line.split("::")[1].split(" ")[0] for line in proc.stdout.splitlines()
                     if line.startswith("FAILED")})
    tail = [line for line in proc.stdout.splitlines() if "passed" in line or "failed" in line]
    return {"returncode": proc.returncode, "failed": failed, "summary": tail[-1:]}


def main() -> int:
    """Build the copy, run green, run each mutation, write the record."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--worktree", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    copy = args.scratch.expanduser() / "sentinel"
    shutil.rmtree(copy, ignore_errors=True)
    copy.mkdir(parents=True)
    head = subprocess.run(["git", "-C", str(args.worktree), "rev-parse", "--short", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()
    archive = subprocess.run(["git", "-C", str(args.worktree), "archive", "HEAD", "scripts",
                              "tests", "pytest.ini", "data", "config.py"],
                             check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", str(copy)], input=archive, check=True)
    links = sum(1 for p in copy.rglob("*") if p.is_symlink())
    record = {"head": head, "symlinks_in_copy": links, "green": run(copy), "mutations": []}
    original = (copy / LIB).read_text()
    for name, source, replacement, expected in MUTATIONS:
        if original.count(source) != 1:
            raise SystemExit(f"{name}: source text found {original.count(source)} times")
        (copy / LIB).write_text(original.replace(source, replacement))
        result = run(copy)
        (copy / LIB).write_text(original)
        result.update({"mutation": name, "expected_red": expected,
                       "bites": all(t in result["failed"] for t in expected)})
        record["mutations"].append(result)
        print(name, "BITES" if result["bites"] else "DOES NOT BITE", result["failed"],
              flush=True)
    record["restored"] = run(copy)
    record["all_bite"] = all(m["bites"] for m in record["mutations"])
    args.out.write_text(json.dumps(record, indent=1) + "\n")
    print("green", record["green"]["summary"], "restored", record["restored"]["summary"])
    return 0 if record["all_bite"] and record["green"]["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
