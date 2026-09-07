#!/usr/bin/env python3
"""
Pin the identity and order of a cell's detection passes, and verify it.

The first-N rungs (N = 1 / 3 / 5 for the stride and 3.7 cells) are derived
by ``cluster_first_n(passes, n)`` over passes loaded from ``run_1 .. run_K``
in directory order. Nothing on disk said WHICH pass sat at each position:
a re-run into ``run_3``, a renamed directory, or a stray ``run_11`` would
change a rung silently, and the union gate (exact count + votes at N = K)
cannot see a swap — swapping ``run_1`` and ``run_3`` leaves the K-union
identical and changes the N = 1 and N = 3 rungs. Session 149 verified from
each pass's ``meta.json`` that directory order equals execution order on
stride A, stride B and the 3.7 arm; this module turns that verified fact
into a committed, checked one (PI ruling, Session 149, adjudicating
MINOR 14 of the r2-chain audit).

Two entry points:

* ``pin``  — write ``<cell>_passes.json`` from the current tree: for each
  position 1..K the run directory, the pass's ``run_id`` (UUID from its
  ``meta.json``), start/end timestamps, every detection file it contributes
  (main file plus additive ``run_<i>_recovery*`` fragments) with SHA-256,
  and the list of any ``run_<j>`` directories beyond K (recorded, so a
  stray extra pass is visible rather than silently ignored).
* ``verify`` — the gate the loaders call: every position's ``run_id`` and
  every file hash must match the pin, and no unpinned ``run_<j>`` may exist
  beyond K. A mismatch raises; it never "fixes" the pin.

Pins live under ``inputs/`` beside the tile manifests they complement
(committed; ``outputs/`` is gitignored).

Usage::

    python scripts/pin_pass_provenance.py pin --cell stride:g384_ov128_55map
    python scripts/pin_pass_provenance.py pin --all
    python scripts/pin_pass_provenance.py verify --all

Zero API. Reads the pass trees; hashing the ~40 GeoJSONs takes seconds.

Created: 2026-09-07 (Session 149)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.stride55_prepare_and_union import (  # noqa: E402
    resolve_pass_paths,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The pinned cells: tag -> (pass root, K, pin path). K is the campaign's
#: pass count: the stride cells ran ten passes, the 3.7 arm five. The
#: fourth 3.7 cell re-verifies stride B's passes, so it shares B's pin.
PINNED_CELLS: dict[str, dict] = {
    "stride:g384_ov128_55map": {
        "cell_dir": PROJECT_ROOT / "outputs/stride-55map-2026-08-25/g384_ov128_55map",
        "k": 10,
        "pin": PROJECT_ROOT / "inputs/stride-55map-2026-08-25/g384_ov128_55map_passes.json",
    },
    "stride:g384_ov192_55map": {
        "cell_dir": PROJECT_ROOT / "outputs/stride-55map-2026-08-25/g384_ov192_55map",
        "k": 10,
        "pin": PROJECT_ROOT / "inputs/stride-55map-2026-08-25/g384_ov192_55map_passes.json",
    },
    "g37:g384_ov192_55map_g37": {
        "cell_dir": PROJECT_ROOT
        / "outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37",
        "k": 5,
        "pin": PROJECT_ROOT
        / "inputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37_passes.json",
    },
}

_NUMERIC_RUN_RE = re.compile(r"^run_(\d+)$")


@dataclass
class PinnedFile:
    """One detection GeoJSON contributing to a pass."""

    path: str  # repo-relative
    sha256: str
    role: str  # "main" | "recovery"


@dataclass
class PinnedPass:
    """One pass at one position of the first-N order."""

    position: int
    run_dir: str  # repo-relative
    run_id: str | None
    start: str | None
    end: str | None
    files: list[PinnedFile]


class PassPinError(RuntimeError):
    """The tree does not match its committed pin."""


def sha256_of(path: Path) -> str:
    """Streaming SHA-256 of a file (the GeoJSONs run to tens of MB)."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_meta(detections: Path) -> dict | None:
    """The pass ``meta.json`` beside a detections file, gzipped or not.

    The detection pipeline writes ``<stem>.meta.json``; one 3.7 pass has
    its meta gzipped (``run_3``), which the loaders never read but this
    pin must.
    """
    stem = detections.name.removesuffix(".geojson")
    for cand in (detections.with_name(f"{stem}.meta.json"),
                 detections.with_name(f"{stem}.meta.json.gz")):
        if cand.exists():
            opener = gzip.open if cand.suffix == ".gz" else open
            with opener(cand, "rt", encoding="utf-8") as fh:
                return json.load(fh)
    return None


def rel(path: Path) -> str:
    """Repo-relative POSIX path."""
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def build_pin(tag: str, spec: dict) -> dict:
    """Read the tree and describe positions 1..K plus any extra passes."""
    cell_dir: Path = spec["cell_dir"]
    k: int = spec["k"]
    passes: list[PinnedPass] = []
    for i in range(1, k + 1):
        run = f"run_{i}"
        paths = resolve_pass_paths(cell_dir, run)  # main + recovery*
        main = paths[0]
        meta = read_meta(main)
        files = [PinnedFile(rel(main), sha256_of(main), "main")]
        files += [PinnedFile(rel(p), sha256_of(p), "recovery") for p in paths[1:]]
        ts = (meta or {}).get("timestamp") or {}
        passes.append(PinnedPass(
            position=i, run_dir=rel(cell_dir / run),
            run_id=(meta or {}).get("run_id"),
            start=ts.get("start"), end=ts.get("end"), files=files,
        ))
        if meta is None:
            logger.warning("%s/%s: no meta.json — run_id/timestamps unpinned", tag, run)

    extra = sorted(
        d.name for d in cell_dir.glob("run_*")
        if d.is_dir() and (m := _NUMERIC_RUN_RE.match(d.name)) and int(m.group(1)) > k
    )
    if extra:
        logger.warning("%s: pass directories beyond K=%d exist: %s", tag, k, extra)

    starts = [p.start for p in passes if p.start]
    return {
        "_README": (
            "Pass-provenance pin (scripts/pin_pass_provenance.py). Positions are "
            "the first-N order the rung derivations use; run_id and sha256 are "
            "the identity the loaders verify. Regenerate only by a deliberate "
            "`pin` run, and record why in the commit."
        ),
        "tag": tag,
        "cell_dir": rel(cell_dir),
        "k": k,
        "pinned_at_utc": datetime.now(UTC).isoformat(),
        "order_rule": "directory index run_<i>, i = 1..K",
        "start_times_monotone": bool(all(a <= b for a, b in zip(starts, starts[1:]))),
        "passes": [asdict(p) for p in passes],
        "extra_run_dirs_beyond_k": extra,
    }


def verify_pin(tag: str, spec: dict, *, check_hashes: bool = True) -> dict:
    """Gate: the tree matches its pin. Raises :class:`PassPinError`.

    Args:
        tag: Key of :data:`PINNED_CELLS`.
        spec: Its entry.
        check_hashes: Hash every file (default). ``False`` checks run_ids
            and file names only — for callers that hash elsewhere.

    Returns:
        The pin that was verified against.
    """
    pin_path: Path = spec["pin"]
    if not pin_path.exists():
        raise PassPinError(
            f"{tag}: no pass pin at {rel(pin_path)} — run "
            f"`pin_pass_provenance.py pin --cell {tag}` and commit it before "
            f"deriving rungs")
    pin = json.loads(pin_path.read_text())
    cell_dir: Path = spec["cell_dir"]
    k: int = spec["k"]
    if pin["k"] != k or pin["cell_dir"] != rel(cell_dir):
        raise PassPinError(f"{tag}: pin describes {pin['cell_dir']} K={pin['k']}, "
                           f"loader expects {rel(cell_dir)} K={k}")
    problems: list[str] = []
    for entry in pin["passes"]:
        i = entry["position"]
        run = f"run_{i}"
        try:
            paths = resolve_pass_paths(cell_dir, run)
        except FileNotFoundError as exc:
            problems.append(str(exc))
            continue
        meta = read_meta(paths[0])
        run_id = (meta or {}).get("run_id")
        if entry["run_id"] and run_id != entry["run_id"]:
            problems.append(f"{run}: run_id {run_id} != pinned {entry['run_id']}")
        have = {rel(p): p for p in paths}
        want = {f["path"]: f["sha256"] for f in entry["files"]}
        if set(have) != set(want):
            problems.append(f"{run}: files {sorted(have)} != pinned {sorted(want)}")
            continue
        if check_hashes:
            for p_rel, p in have.items():
                if sha256_of(p) != want[p_rel]:
                    problems.append(f"{run}: sha256 mismatch on {p_rel}")
    extra = sorted(
        d.name for d in cell_dir.glob("run_*")
        if d.is_dir() and (m := _NUMERIC_RUN_RE.match(d.name)) and int(m.group(1)) > k
    )
    if extra != pin.get("extra_run_dirs_beyond_k", []):
        problems.append(f"pass directories beyond K changed: {extra} vs pinned "
                        f"{pin.get('extra_run_dirs_beyond_k', [])}")
    if problems:
        raise PassPinError(f"{tag}: pass tree does not match its pin —\n  "
                           + "\n  ".join(problems))
    logger.info("pass pin OK %s (K=%d, %d files)", tag, k,
                sum(len(e["files"]) for e in pin["passes"]))
    return pin


def tag_for_cell_dir(cell_dir: Path) -> str:
    """Resolve the :data:`PINNED_CELLS` tag for a loader's cell directory."""
    target = cell_dir.resolve()
    for tag, spec in PINNED_CELLS.items():
        if spec["cell_dir"].resolve() == target:
            return tag
    raise PassPinError(f"{cell_dir}: no pass pin is defined for this cell")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=("pin", "verify"))
    ap.add_argument("--cell", action="append", default=[],
                    help=f"One of {sorted(PINNED_CELLS)} (repeatable).")
    ap.add_argument("--all", action="store_true", help="Every pinned cell.")
    args = ap.parse_args()
    tags = sorted(PINNED_CELLS) if args.all else args.cell
    if not tags:
        ap.error("give --cell TAG (repeatable) or --all")
    rc = 0
    for tag in tags:
        spec = PINNED_CELLS[tag]
        if args.action == "pin":
            pin = build_pin(tag, spec)
            spec["pin"].parent.mkdir(parents=True, exist_ok=True)
            spec["pin"].write_text(json.dumps(pin, indent=2) + "\n")
            logger.info("pinned %s -> %s (K=%d, monotone start times: %s)", tag,
                        rel(spec["pin"]), pin["k"], pin["start_times_monotone"])
        else:
            try:
                verify_pin(tag, spec)
            except PassPinError as exc:
                logger.error("%s", exc)
                rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
