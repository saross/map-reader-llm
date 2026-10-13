"""Merge Task A's tilings and Task B's pools into the declarations file, pinned.

Reads ``out/t07_tilings.json`` (``declarations``: one ``pass_tilings`` entry
per T 0.7 cell) and ``out/rebuild_pools.json`` (``declarations``: one pool
declaration per K = 5 / K = 10 consensus a rebuild reproduced), and writes
them into ``inputs/provenance/assessed-area-declarations.json`` beside the
three declarations PR #26 made, whose content is kept. Re-running
replaces entries with the same key (pool path; tiling label), so the file
is reproducible from the two outputs and the committed files.

**Pins (2026-10-10, Astra's review of 2026-10-09, P2).** Every entry is
then pinned through ``scripts/lib_assessed_area.pin_declaration``: a pool
declaration records the git blob hash of its consensus
(``pool_git_blob_hash``), and every entry pins each other file its area is
read from (``inputs``: pass metas, tile manifests and polygons, footprint
and clip polygons). The library refuses a declaration once any of them
changes. Each pinned hash, the pass hashes included, is checked against
``git hash-object`` and against the blob committed at ``HEAD``, and the
check is written to ``--pins-out``; any disagreement refuses the write.
A pool declaration that already records a consensus hash (a rebuild run
after 2026-10-10) must still match its consensus, or the write refuses.

Usage (any machine; small JSON and blob hashes only; run from a clean
checkout so ``HEAD`` holds the files pinned)::

    python write_declarations.py --repo . \
        --tilings out/t07_tilings.json --pools out/rebuild_pools.json \
        --pins-out out/declaration_pins.json

Created: 2026-10-08 (D57 (3), Session 163 follow-up); pins 2026-10-10
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TARGET = "inputs/provenance/assessed-area-declarations.json"
PURPOSE = (
    "Assessed-area provenance DECLARED after the fact for legacy artefacts whose "
    "builders recorded too little. Read by scripts/lib_assessed_area. "
    "'declarations' are legacy candidate pools: either a footprint and clip (the "
    "three of 2026-10-07, method 'declared', every candidate checked to lie inside "
    "the declared area), or the pass_provenance a pre-2026-09-12 merge_passes "
    "consensus did not record, declared only where a rebuild from those passes "
    "reproduced the committed directory (2026-10-08, PI ruling D57 (3)). "
    "'pass_tilings' name the tile manifest of passes whose meta records none "
    "(2026-10-08, D57 (3)); the passes' own processed_tiles still define what they "
    "assessed. Every declared file is anchored to its git blob hash: a file "
    "rewritten after its declaration makes the area undetermined. Since "
    "2026-10-10 (Astra's review of 2026-10-09, P2) each pool declaration also "
    "records the blob hash of the consensus it was checked against "
    "(pool_git_blob_hash), and every entry pins each other file its area is read "
    "from (inputs: pass metas, tile manifests and polygons, footprint and clip "
    "polygons), so a pool or a tiling rewritten in place makes the area "
    "undetermined too. A pool built after 2026-10-07 by a builder that calls "
    "write_area_record carries its own record beside the union and needs no entry "
    "here. Each entry cites the evidence it was reconstructed from; none is "
    "inferred from a path or a naming convention alone."
)
REVISED = ("2026-10-10 (Astra's review of 2026-10-09, P2: consensus and input pins); "
           "2026-10-08 (PI ruling D57 (3): pass_tilings and pool pass_provenance)")


def pinned_paths(out: dict[str, Any]) -> dict[str, str]:
    """Every path the file pins, with the hash it pins it to."""
    pins: dict[str, str] = {}

    def add(path: str, digest: str | None) -> None:
        if digest is None:
            raise SystemExit(f"{path}: pinned with no hash")
        if pins.get(path, digest) != digest:
            raise SystemExit(f"{path}: pinned to two hashes ({pins[path]}, {digest})")
        pins[path] = digest

    for entry in out["declarations"]:
        add(entry["pool"], entry.get("pool_git_blob_hash"))
        for item in entry.get("pass_provenance") or []:
            add(item["path"], item["git_blob_hash"])
        for item in entry.get("inputs", []):
            add(item["path"], item["git_blob_hash"])
    for entry in out["pass_tilings"]:
        for item in entry["passes"]:
            add(item["path"], item["git_blob_hash"])
        for item in entry.get("inputs", []):
            add(item["path"], item["git_blob_hash"])
    return pins


def check_against_git(repo: Path, pins: dict[str, str]) -> list[dict[str, Any]]:
    """Each pin against ``git hash-object`` and the blob committed at HEAD."""
    paths = sorted(pins)
    hashed = subprocess.run(
        ["git", "-C", str(repo), "hash-object", "--stdin-paths"],
        input="\n".join(paths) + "\n", capture_output=True, text=True, check=True,
    ).stdout.split()
    tree = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "HEAD", "--", *paths],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    head = {line.split("\t", 1)[1]: line.split()[2] for line in tree}
    rows = []
    for path, object_id in zip(paths, hashed, strict=True):
        rows.append({"path": path, "pinned": pins[path], "git_hash_object": object_id,
                     "head_blob": head.get(path),
                     "equal": pins[path] == object_id == head.get(path)})
    return rows


def main() -> int:
    """Merge, pin, check against git, and write the declarations file."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--tilings", type=Path, required=True)
    ap.add_argument("--pools", type=Path, required=True)
    ap.add_argument("--pins-out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo))
    from scripts import lib_assessed_area as laa  # noqa: PLC0415

    target = repo / TARGET
    original = target.read_text(encoding="utf-8")
    try:
        return merge_and_pin(args, repo, target, laa)
    except BaseException:
        # A refused or failed write leaves the committed file as it was.
        target.write_text(original, encoding="utf-8")
        raise


def merge_and_pin(args: argparse.Namespace, repo: Path, target: Path, laa: Any) -> int:
    """The body of :func:`main`: merge, pin, check against git, and write."""
    payload = json.loads(target.read_text(encoding="utf-8"))
    tilings = json.loads(args.tilings.read_text())["declarations"]
    pools = json.loads(args.pools.read_text())["declarations"]
    new_pools = {entry["pool"] for entry in pools}
    kept = [d for d in payload.get("declarations", []) if d["pool"] not in new_pools]
    new_labels = {entry["label"] for entry in tilings}
    kept_tilings = [t for t in payload.get("pass_tilings", [])
                    if t.get("label") not in new_labels]
    out = {
        "schema": "assessed-area-declarations/1",
        "created": payload.get("created", "2026-10-07"),
        "revised": REVISED,
        "ruling": "D51, D57 (planning/pi-decisions-2026-09-20.md)",
        "purpose": PURPOSE,
        "declarations": kept + sorted(pools, key=lambda e: e["pool"]),
        "pass_tilings": kept_tilings + tilings,
    }

    def write() -> None:
        target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        laa.clear_declaration_caches()

    # Tilings first: a pool's pins resolve its passes' manifests through them.
    out["pass_tilings"] = [laa.pin_declaration(t) for t in out["pass_tilings"]]
    write()
    pinned = []
    for entry in out["declarations"]:
        recorded = entry.get(laa.POOL_HASH_KEY)
        entry = laa.pin_declaration(entry)
        if recorded and recorded != entry[laa.POOL_HASH_KEY]:
            raise SystemExit(f"{entry['pool']}: the consensus changed since its "
                             f"rebuild ({entry[laa.POOL_HASH_KEY]} != {recorded})")
        pinned.append(entry)
    out["declarations"] = pinned

    rows = check_against_git(repo, pinned_paths(out))
    args.pins_out.write_text(json.dumps({
        "check": "every pinned git blob hash equals git hash-object and the blob at HEAD",
        "head": subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                               capture_output=True, text=True, check=True).stdout.strip(),
        "n_pinned": len(rows), "n_equal": sum(row["equal"] for row in rows),
        "rows": rows,
    }, indent=1) + "\n")
    bad = [row["path"] for row in rows if not row["equal"]]
    if bad:
        raise SystemExit(f"{len(bad)} pin(s) differ from git: {bad[:3]}")
    write()
    print(f"{target}: {len(out['declarations'])} declarations "
          f"({len(pools)} new), {len(out['pass_tilings'])} pass tilings "
          f"({sum(len(t['passes']) for t in out['pass_tilings'])} passes); "
          f"{len(rows)} pinned files, all equal to git hash-object and HEAD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
