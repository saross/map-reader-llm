"""Shared helpers for the D57 (4) re-score, Phases 0 and 2 (2026-10-09, Session 163).

Purpose
-------
The D57 (4) re-score regenerates every committed cell whose numbers the D50
scorer (PR #26 plus PR #27, ``8988f3f17``) moves, in a detached worktree, and
checks each regenerated cell against the expected values measured on
2026-10-08 (``rescore_b.jsonl``). The plan card is
``planning/d57-4-rescore-plan-2026-10-09.md``; the rulings are D58 in
``planning/pi-decisions-2026-09-20.md``.

This module holds what the census, replay, and check scripts share:

* the cell classification of ``summarise_new.py`` (scorer-frames report),
  reproduced exactly so the moved set and the sub-0.001 pairing twins can be
  re-derived from the jsonl rather than copied;
* reading a committed ``evaluation.json`` from ``HEAD`` (never from the
  working tree, which a replay overwrites);
* resolving a cell's recorded detection inputs and counting their features.

Nothing here writes a file. The repository root is always passed in by the
caller (a CLI argument), never hard-coded.

Usage (library)::

    import d57_common as dc
    rows = dc.load_jsonl(Path("rescore_b.jsonl"))
    classes = dc.classify(rows)
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

#: The metrics compared at every buffer.
METRICS: tuple[str, ...] = ("f1", "precision", "recall")

#: Equality tolerance for full-precision values (plan § 1, stop rule).
EPS = 1e-9

#: Tolerance against four-decimal committed values (as in the input-drift trace).
TOL_4DP = 1e-4

#: Moved-cell threshold of ``summarise_new.py``.
MOVED_THRESHOLD = 0.001

#: Plan § 3.1 groups held for Phase 6 (ladder drivers).
LADDER_PREFIXES: tuple[str, ...] = (
    "results/k-ladder-2026-09-12/phase2/cells/",
    "results/k-ladder-2026-09-12/tier-e/cells/",
    "results/k-ladder-2026-09-12/recovery-fix-2026-09-13/reproduced-k5-evaluation/",
)

#: The null-exemplar twins' home.
NULL_EX_PREFIX = "results/null-exemplar-sensitivity-2026-09-13/cells/"

#: The ``detection_scope`` keys every regenerated evaluation must carry
#: (``evaluate_detections._DETECTION_SCOPE_COUNTS`` at ``8988f3f17``; the replay
#: script re-reads the tuple from the scorer itself and checks it equals this).
SCOPE_COUNT_KEYS: tuple[str, ...] = (
    "n_detections", "n_in_scope", "n_out_of_frame", "n_out_of_frame_cross_sheet",
    "n_origin_restored", "n_origin_switched", "n_origin_only", "n_origin_unrecognised",
    "n_unattributed", "n_unattributed_in_frame",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSON-lines file.

    Args:
        path: The file.

    Returns:
        One dict per non-empty line.
    """
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def max_abs_delta(a: dict[str, Any] | None, b: dict[str, Any] | None) -> float | None:
    """Largest |a − b| over buffers and metrics, plus MCC when both are defined.

    Reproduces ``summarise_new.max_abs_delta`` exactly.

    Args:
        a: A point block (``per_buffer``, ``mcc``).
        b: Another.

    Returns:
        The largest absolute difference, or ``None`` when either block is absent.
    """
    if not a or not b:
        return None
    worst = 0.0
    for buf, vals in (a.get("per_buffer") or {}).items():
        other = (b.get("per_buffer") or {}).get(buf)
        if not other:
            continue
        for m in METRICS:
            worst = max(worst, abs(vals[m] - other[m]))
    if isinstance(a.get("mcc"), (int, float)) and isinstance(b.get("mcc"), (int, float)):
        worst = max(worst, abs(a["mcc"] - b["mcc"]))
    return worst


def mcc_state(block: dict[str, Any] | None) -> str:
    """Return 'refused', a four-decimal number, or '—' (``summarise_new.mcc_state``)."""
    if not block:
        return "—"
    if block.get("mcc") is None:
        return "refused" if block.get("mcc_refused") else "—"
    return f"{block['mcc']:.4f}"


def classify(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Classify every jsonl row as ``summarise_new.py`` did.

    Args:
        rows: The ``rescore_b.jsonl`` rows.

    Returns:
        ``eval`` → ``{"class", "moved", "d_off", "d_on", "mcc_flip", "row"}``.
    """
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        rec: dict[str, Any] = {"row": row, "moved": False, "d_off": None, "d_on": None,
                               "mcc_flip": False}
        if row.get("new_status") == "error":
            rec["class"] = "error"
        elif row.get("new_status") != "scored":
            rec["class"] = f"not scored ({row.get('new_status')})"
        else:
            d_off = max_abs_delta(row["new"], row["blast_off"])
            d_on = max_abs_delta(row["new"], row["blast_on"])
            mcc_flip = ((mcc_state(row["new"]) in ("refused", "—"))
                        != (mcc_state(row["blast_off"]) in ("refused", "—")))
            scope = row.get("new_scope") or {}
            if d_off is not None and d_off <= EPS and not mcc_flip:
                cls = "unchanged"
            elif d_on is not None and d_on <= EPS:
                cls = "as-predicted"
            elif scope.get("n_origin_restored"):
                cls = "origin-restored"
            else:
                cls = "other"
            rec.update({"class": cls, "d_off": d_off, "d_on": d_on, "mcc_flip": mcc_flip,
                        "moved": (d_off or 0) >= MOVED_THRESHOLD or mcc_flip})
        out[row["eval"]] = rec
    return out


def git(repo: Path, *args: str) -> str:
    """Run a read-only git command in ``repo`` and return stripped stdout ('' on error)."""
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                         check=False)
    return res.stdout.strip() if res.returncode == 0 else ""


def git_show_bytes(repo: Path, rev: str, rel: str) -> bytes | None:
    """Return ``<rev>:<rel>`` as bytes, or ``None`` when absent."""
    res = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{rel}"],
                         capture_output=True, check=False)
    return res.stdout if res.returncode == 0 else None


def committed_eval(repo: Path, rel: str, rev: str = "HEAD") -> dict[str, Any] | None:
    """Read a committed ``evaluation.json`` from git (never the working tree).

    Args:
        repo: Repository root.
        rel: Repository-relative path.
        rev: Revision (default ``HEAD``).

    Returns:
        The parsed document, or ``None`` when it is not in ``rev``.
    """
    blob = git_show_bytes(repo, rev, rel)
    return None if blob is None else json.loads(blob)


def strip_frozen(path: str) -> str:
    """Drop an E82 frozen-replay prefix (``…/frozen/<rel>`` → ``<rel>``)."""
    return path.split("/frozen/", 1)[1] if "/frozen/" in path else path


def to_repo_relative(repo: Path, path: str) -> tuple[str, str | None]:
    """Normalise a recorded path to repository-relative where it lies in a checkout.

    A recorded absolute path into ANY checkout of this repository
    (``…/map-reader-llm/<rel>``) is re-rooted at ``repo`` so a replay never
    reads from, or writes to, the shared checkout.

    Args:
        repo: The repository root the replay runs in.
        path: The recorded path.

    Returns:
        ``(path, note)``: the path to use and a note when it was rewritten.
    """
    original = path
    path = strip_frozen(path)
    note = None if path == original else f"frozen prefix stripped from {original}"
    p = Path(path)
    if not p.is_absolute():
        return path, note
    try:
        return str(p.resolve().relative_to(repo.resolve())), note
    except ValueError:
        pass
    marker = "/map-reader-llm/"
    if marker in path:
        rel = path.split(marker, 1)[1]
        return rel, f"absolute checkout path re-rooted: {original}"
    return path, note


def committed_counts(ev: dict[str, Any]) -> list[int | None]:
    """The committed feature counts: one per run for a multi-run cell, else one."""
    per_run = ev.get("per_run")
    if per_run:
        return [r.get("n_detections") for r in per_run]
    return [(ev.get("summary") or {}).get("n_detections")]


def feature_count(path: Path) -> int:
    """Count a GeoJSON's features by parsing the JSON (no geometry library)."""
    return len(json.loads(path.read_text()).get("features") or [])


def per_buffer_committed(ev: dict[str, Any]) -> dict[str, dict[str, float]]:
    """The committed (four-decimal) F1, P and R per buffer from a summary."""
    out: dict[str, dict[str, float]] = {}
    for b in (ev.get("summary") or {}).get("buffers") or []:
        out[str(b["buffer_metres"])] = {"f1": b.get("f1"), "precision": b.get("precision"),
                                        "recall": b.get("recall")}
    return out


def committed_mcc(ev: dict[str, Any]) -> float | None:
    """The committed tile-MCC point (summary ``tile_classification.mcc.point``), if any."""
    tc = (ev.get("summary") or {}).get("tile_classification") or {}
    mcc = tc.get("mcc")
    if isinstance(mcc, dict):
        return mcc.get("point")
    return mcc if isinstance(mcc, (int, float)) else None


def group_of(rel: str, *, mismatch: bool, pinned: bool, twin: bool) -> str:
    """Assign a cell to its plan § 3.1 group.

    Args:
        rel: The evaluation path.
        mismatch: The feature-count check failed (input drift).
        pinned: The cell carries ``_metadata.e82_input_vintage``.
        twin: The cell is a sub-0.001 pairing twin (not in ``moved_new.csv``).

    Returns:
        One of ``archive``, ``ladder``, ``null-exemplar``, ``pinned``,
        ``drift-unpinned``, ``twin``, ``replayable``.
    """
    if rel.startswith("archive/"):
        return "archive"
    if rel.startswith(LADDER_PREFIXES):
        return "ladder"
    if rel.startswith(NULL_EX_PREFIX):
        return "null-exemplar"
    if mismatch:
        return "pinned" if pinned else "drift-unpinned"
    if twin:
        return "twin"
    return "replayable"
