"""Place D58 Q2 Stage A evaluations into their cell directories, recipe repaired.

D57 (4) re-score, 2026-10-09 (Session 163); PI ruling D58 Q2 ("Yes, commit stage
A and don't run stage B"). ``q2_stage_a.py`` scored each drifted or pinned cell
with the NEW scorer on the inputs AS SCORED, recovered from git with ``git show``
into scratch. Its outputs therefore record scratch paths in
``_metadata.cli_args``. This script copies each Stage A trio
(``evaluation.{json,csv,md}``) over the committed cell and repairs only the JSON's
recipe, so that the committed artefact names the repository inputs it logically
scored and the commit each one was read at — the E82 precedent
(``scripts/rerun_bca_corpus.py`` ``_accept``):

* ``cli_args.detections``, ``ground_truth`` and ``bounds`` take the committed
  cell's own repository-relative values (each asserted to be the path the
  Stage A vintage materialised), and ``cli_args.output_dir`` the cell
  directory;
* ``input_files`` and ``input_git_state`` are left exactly as the scorer wrote
  them: they record what was actually read (the scratch materialisation) and
  its git blob hash, the content anchor that binds the cell to the vintage;
* a **pinned** cell carries its committed ``_metadata.e82_input_vintage``
  forward unchanged, after asserting it equals the Stage A vintage for all
  three inputs.

Unpinned cells are refused unless ``--unpinned-key`` names the ``_metadata``
key their vintage is to be written under: the only key the repository's tools
read is ``e82_input_vintage`` (``scripts/verify_run_conditions.py``,
``scripts/register_post_e71_conditions.py``), and writing it for a cell E82
never pinned would mislabel the cell. That choice is the PI's.

The ``.csv`` and ``.md`` are copied byte for byte (neither records a path). A
JSON is rewritten only after a load/dump round trip of the scorer's output is
proved byte-identical, so nothing but the repaired keys can change.

Usage (on sapphire)::

    ~/Code/map-reader-llm/.venv/bin/python place_stage_a.py \\
        --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --stage-a ~/scratch/d57-4-rescore-2026-10-09/q2 --groups pinned
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

#: The three recipe inputs whose vintage Stage A recovered.
INPUT_KEYS = ("detections", "ground_truth", "bounds")


def dump(doc: dict[str, Any]) -> str:
    """Serialise as ``scripts/evaluate_detections.py`` does (indent 2, no newline)."""
    return json.dumps(doc, indent=2)


def repaired(stage_a_text: str, committed: dict[str, Any], row: dict[str, Any],
             cell: str, unpinned_key: str | None) -> str:
    """Return the Stage A JSON with its recipe repaired; refuse on any mismatch.

    Args:
        stage_a_text: The Stage A ``evaluation.json`` exactly as the scorer wrote it.
        committed: The committed cell's ``evaluation.json`` (parsed).
        row: The cell's ``q2_stage_a.json`` record (``vintage``, ``pinned``).
        cell: The cell directory, repository-relative.
        unpinned_key: ``_metadata`` key for an unpinned cell's vintage, or ``None``.

    Returns:
        The repaired JSON text.

    Raises:
        SystemExit: On a failed round trip, a path or vintage mismatch, or an
            unpinned cell with no key named.
    """
    doc = json.loads(stage_a_text)
    if dump(doc) != stage_a_text:
        sys.exit(f"{cell}: Stage A JSON does not round-trip byte for byte")
    meta = doc["_metadata"]
    cli = meta["cli_args"]
    ccli = committed["_metadata"]["cli_args"]
    vintage = {row["vintage"][k][0]: row["vintage"][k][1] for k in INPUT_KEYS}
    for key in INPUT_KEYS:
        rel, commit = row["vintage"][key]
        want = ccli[key]
        got = cli[key]
        # detections is a one-element list in both recipes; the others are strings
        want_rel = want[0] if isinstance(want, list) else want
        got_path = got[0] if isinstance(got, list) else got
        if want_rel != rel:
            sys.exit(f"{cell}: committed {key} {want_rel!r} is not the vintage path {rel!r}")
        if not got_path.endswith(f"/{commit}/{rel}"):
            sys.exit(f"{cell}: Stage A {key} {got_path!r} is not {commit}:{rel}")
        cli[key] = want
    cli["output_dir"] = cell
    if row["pinned"]:
        pin = committed["_metadata"].get("e82_input_vintage") or {}
        if {k: v[:9] for k, v in pin.items()} != {k: v[:9] for k, v in vintage.items()}:
            sys.exit(f"{cell}: committed e82_input_vintage {pin} != Stage A vintage {vintage}")
        meta["e82_input_vintage"] = pin
    elif unpinned_key:
        meta[unpinned_key] = vintage
    else:
        sys.exit(f"{cell}: unpinned; refusing without --unpinned-key (see the docstring)")
    return dump(doc)


def main() -> int:
    """Place every Stage A cell of the requested groups; print one line per cell."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True, help="The worktree to write into.")
    ap.add_argument("--stage-a", type=Path, required=True,
                    help="q2_stage_a.py's --scratch (holds q2_stage_a.json and new/).")
    ap.add_argument("--groups", choices=("pinned", "unpinned", "all"), required=True)
    ap.add_argument("--unpinned-key", default=None,
                    help="_metadata key for an unpinned cell's vintage (PI's choice).")
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    stage_a = args.stage_a.expanduser().resolve()
    rows = json.loads((stage_a / "q2_stage_a.json").read_text())
    want_pinned = {"pinned": {True}, "unpinned": {False}, "all": {True, False}}[args.groups]
    placed = 0
    for row in rows:
        if row["pinned"] not in want_pinned:
            continue
        if not (row["recoverable"] and row["old_reproduces"]):
            sys.exit(f"{row['eval']}: not recoverable or OLD did not reproduce")
        cell = str(Path(row["eval"]).parent)
        src = stage_a / "new" / cell.replace("/", "__")
        committed = json.loads((repo / cell / "evaluation.json").read_text())
        text = repaired((src / "evaluation.json").read_text(), committed, row, cell,
                        args.unpinned_key)
        for name in ("evaluation.csv", "evaluation.md"):
            shutil.copyfile(src / name, repo / cell / name)
        (repo / cell / "evaluation.json").write_text(text)
        placed += 1
        print(f"placed {'pinned  ' if row['pinned'] else 'unpinned'} {cell}")
    print(f"{placed} cell(s) placed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
