#!/usr/bin/env python3
"""Compute the verifier-uplift column once the paired cells have scores.

The second half of Build order step 3 of
``planning/uplift-supplement-2026-08-28.md``. The pairing worklist
(``scripts/build_verifier_pairing_worklist.py``) says which pre-verifier set
belongs to which verified cell; this script joins the two scores and writes the
uplift.

Uplift is ``verified - unverified`` on one metric, both cells in the SAME
stratum. The worklist carries the two sides' separately derived stratum ids and
both are handed to
:func:`~scripts.lib_uplift_supplement.refuse_cross_stratum`, so a pair whose two
cells were scored against different references, buffers, or frames raises rather
than producing a plausible number.

That check is a **tripwire, not an independent verification**. A ``stratum_id``
is corpus x reference x buffer x frame; the pairing key already forces both
sides to agree on all four before a row is emitted, so on an unedited worklist
the guard cannot fire. What it catches is an externally edited worklist, or a
future change that lets the pairing key and the stratum key drift apart. It can
NEVER catch a cross-lineage mispair — two cells of one run at different
geometries share a stratum — and the protection against that lives in
``build_verifier_pairing_worklist``'s lineage matching.

Cross-stratum comparisons belong in ``transfer-pairs.csv``, with a delta and a
named tax.

Where an unverified score does not exist yet the row is written with a null
uplift and a status saying which side is missing. Running this before the
scoring jobs is therefore useful, not an error: it tells you what the column
will look like and what is still outstanding.

Score sources, in order
-----------------------
1. ``results/uplift-supplement/conditions.csv`` — the flatten, for both cells
   where both are registered conditions.
2. A freshly written score under the job's ``output_dir``: ``evaluation.json``
   from ``evaluate_detections.py``, or ``summary.json`` from
   ``compute_corrected_f1_multi_buffer.py``. Both shapes are read, because a
   twin is scored with whichever engine its verified pair used.

Zero API. The join and arithmetic are trivial; the bootstrap that produced the
inputs is what belongs on sapphire.

Usage::

    python scripts/compute_verifier_uplift.py
    python scripts/compute_verifier_uplift.py --metric MCC

Created: 2026-08-29 (uplift-supplement card, Build order step 3)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_uplift_supplement import (  # noqa: E402
    NOTATION_KEY_PATH,
    NotationKey,
    refuse_cross_stratum,
    write_csv,
)

DEFAULT_OUT_DIR = Path("results/uplift-supplement")

#: Metrics the uplift may be computed on. Each names a column of
#: ``conditions.csv`` and a field of an ``evaluation.json`` buffer block.
SUPPORTED_METRICS: dict[str, str] = {
    "F1": "f1",
    "precision": "precision",
    "recall": "recall",
    "MCC": "mcc",
}

UPLIFT_COLUMNS: tuple[str, ...] = (
    "pair_id", "verified_condition_id", "unverified_condition_id",
    "stratum_id", "corpus", "reference", "buffer_m", "frame_id",
    "N", "min_votes", "prob_t",
    "uplift_metric", "verified_value", "unverified_value", "uplift",
    "status", "notes",
)


def _read_conditions(path: Path) -> dict[str, dict[str, str]]:
    """Load the flatten's master table, keyed by ``condition_id``.

    Args:
        path: Path to ``conditions.csv``.

    Returns:
        The rows by condition id, or an empty mapping if the file is absent.
    """
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return {row["condition_id"]: row for row in csv.DictReader(handle)}


def _metric_from_summary(
    document: dict[str, Any], metric: str, buffer_m: int
) -> float | None:
    """Lift one metric out of a corrected-F1 engine ``summary.json``.

    The two engines write different files. ``evaluate_detections.py`` writes
    ``evaluation.json``; ``compute_corrected_f1_multi_buffer.py`` writes
    ``summary.json`` with a ``results`` list keyed by ``R_m`` and capitalised
    metric names. Reading only the first meant every corrected-F1 twin scored on
    sapphire stayed ``pending`` for ever, with nothing to say why.

    Args:
        document: The parsed ``summary.json``.
        metric: A key of :data:`SUPPORTED_METRICS`.
        buffer_m: Buffer radius in metres.

    Returns:
        The value, or ``None`` if this summary does not report it.
    """
    for row in document.get("results") or []:
        if int(row.get("R_m", -1)) != buffer_m:
            continue
        if metric == "MCC":
            return (row.get("tile_classification") or {}).get("mcc")
        return row.get({"F1": "F1", "precision": "precision",
                        "recall": "recall"}[metric])
    return None


def _metric_from_eval(
    document: dict[str, Any], metric: str, buffer_m: int
) -> float | None:
    """Lift one metric at one buffer out of an evaluation document.

    Args:
        document: The parsed ``evaluation.json``.
        metric: A key of :data:`SUPPORTED_METRICS`.
        buffer_m: Buffer radius in metres.

    Returns:
        The value, or ``None`` if the evaluation does not report it.
    """
    summary = document.get("summary") or {}
    if metric == "MCC":
        tile = summary.get("tile_classification") or {}
        value = tile.get("mcc")
        return value.get("point") if isinstance(value, dict) else value
    field = SUPPORTED_METRICS[metric]
    for block in summary.get("buffers", []):
        if int(block["buffer_metres"]) == buffer_m:
            return block.get(field)
    return None


def _value_for(
    repo_root: Path,
    conditions: dict[str, dict[str, str]],
    condition_id: str | None,
    output_dir: str | None,
    metric: str,
    buffer_m: int,
) -> tuple[float | None, str]:
    """Resolve one side of a pair to a metric value.

    Args:
        repo_root: Repository root.
        conditions: The flatten's rows by condition id.
        condition_id: The registered condition, where the side has one.
        output_dir: A worklist job's output directory, for freshly scored twins.
        metric: A key of :data:`SUPPORTED_METRICS`.
        buffer_m: Buffer radius in metres.

    Returns:
        ``(value, source)``. ``source`` is ``conditions.csv``, the path of the
        score that was read, or ``missing``.
    """
    if condition_id and condition_id in conditions:
        raw = conditions[condition_id].get(metric)
        if raw:
            return float(raw), "conditions.csv"
    if output_dir:
        # Both engines' output shapes, because a twin is scored with whichever
        # engine its verified pair used.
        for filename, reader in (
            ("evaluation.json", _metric_from_eval),
            ("summary.json", _metric_from_summary),
        ):
            candidate = repo_root / output_dir / filename
            if not candidate.exists():
                continue
            document = json.loads(candidate.read_text(encoding="utf-8"))
            value = reader(document, metric, buffer_m)
            if value is not None:
                return float(value), str(candidate.relative_to(repo_root))
    return None, "missing"


def compute_uplift(
    repo_root: Path, out_dir: Path, metric: str
) -> list[dict[str, Any]]:
    """Join the pairing worklist to the available scores and compute uplift.

    Args:
        repo_root: Repository root.
        out_dir: Directory holding ``verifier-pairing-worklist.csv`` and
            ``conditions.csv``.
        metric: A key of :data:`SUPPORTED_METRICS`.

    Returns:
        One row per pair.

    Raises:
        FileNotFoundError: If the pairing worklist has not been built.
        CrossStratumAggregationError: If a pair's two cells do not share a
            stratum — a mis-pairing, which must fail rather than produce a
            number.
    """
    worklist_path = out_dir / "verifier-pairing-worklist.csv"
    if not worklist_path.exists():
        raise FileNotFoundError(
            f"{worklist_path} not found. Run "
            "scripts/build_verifier_pairing_worklist.py first."
        )
    conditions = _read_conditions(out_dir / "conditions.csv")
    with worklist_path.open(encoding="utf-8") as handle:
        pairs = list(csv.DictReader(handle))

    rows: list[dict[str, Any]] = []
    for pair in pairs:
        buffer_m = int(pair["buffer_m"] or 0)
        verified_value, verified_source = _value_for(
            repo_root, conditions, pair["verified_condition_id"], None,
            metric, buffer_m,
        )
        unverified_value, unverified_source = _value_for(
            repo_root, conditions, pair["unverified_condition_id"] or None,
            pair["output_dir"] or None, metric, buffer_m,
        )

        # The two sides' separately derived ids, not one id passed twice (an
        # earlier build did that, making the check unfailable on any input).
        # This is a tripwire against external edits and future key drift, not an
        # independent check of the pairing — see the module docstring.
        stratum_id = refuse_cross_stratum(
            [
                {"stratum_id": pair["verified_stratum_id"]},
                {"stratum_id": pair["unverified_stratum_id"]},
            ],
            what=(
                f"verifier uplift for {pair['verified_condition_id']} "
                f"against {pair['unverified_condition_id'] or 'its derived twin'}"
            ),
        )

        notes: list[str] = []
        if verified_value is None:
            notes.append("verified side has no score")
        if unverified_value is None:
            notes.append(
                f"unverified side has no score ({pair['status']}"
                + (f"; {pair['pairing_basis']}" if pair["pairing_basis"] else "")
                + ")"
            )
        if verified_value is not None and unverified_value is not None:
            status = "computed"
            notes.append(
                f"verified from {verified_source}, unverified from {unverified_source}"
            )
        else:
            status = "pending"

        rows.append({
            "pair_id": pair["job_id"],
            "verified_condition_id": pair["verified_condition_id"],
            "unverified_condition_id": pair["unverified_condition_id"] or None,
            "stratum_id": stratum_id,
            "corpus": pair["corpus"], "reference": pair["reference"],
            "buffer_m": buffer_m, "frame_id": pair["frame_id"],
            "N": pair["N"], "min_votes": pair["min_votes"],
            "prob_t": pair["prob_t"],
            "uplift_metric": metric,
            "verified_value": verified_value,
            "unverified_value": unverified_value,
            "uplift": (
                round(verified_value - unverified_value, 6)
                if verified_value is not None and unverified_value is not None
                else None
            ),
            "status": status,
            "notes": "; ".join(notes) or None,
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    """Write ``verifier-uplift.csv``.

    Args:
        argv: Command-line arguments.

    Returns:
        Process exit code: 0 on success.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument(
        "--metric", choices=sorted(SUPPORTED_METRICS), default="F1",
        help="Metric the uplift is computed on (default: F1).",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    out_dir = (args.out_dir or (repo_root / DEFAULT_OUT_DIR)).resolve()
    notation = NotationKey(repo_root / NOTATION_KEY_PATH)

    rows = compute_uplift(repo_root, out_dir, args.metric)
    suffix = "" if args.metric == "F1" else f"-{args.metric.lower()}"
    destination = out_dir / f"verifier-uplift{suffix}.csv"
    write_csv(destination, rows, UPLIFT_COLUMNS, notation)

    counts = Counter(r["status"] for r in rows)
    print(f"{destination.name}   {len(rows):>4} rows (metric {args.metric})")
    for status, count in sorted(counts.items()):
        print(f"  {status:<12} {count:>4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
