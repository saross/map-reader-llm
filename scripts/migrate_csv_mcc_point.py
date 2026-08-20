#!/usr/bin/env python3
"""Migrate the committed CSV/Markdown layer to the OBSERVED tile metrics (D30).

The evaluation JSONs keep two different quantities for each tile-level
metric: ``point`` — Matthews Correlation Coefficient (MCC), sensitivity,
or specificity computed on the observed tile confusion matrix — and
``mean``, the mean of the bootstrap resample distribution. The CSV and
Markdown writers in ``evaluate_detections.py`` published ``mean`` under
the bare names ``mcc`` / ``sensitivity`` / ``specificity``, so every
committed ``evaluation.csv``, ``batch_summary.csv``, and
``evaluation.md`` carries a resample artefact under a header that names
the statistic itself (Session 137 audit, finding F6; defect D30). The
JSON layer was always right; only the human-facing layer was wrong.

The consequence is visible in the record: in the D17 commit
(``60f83e571``) the re-run evaluations' ``mcc`` / ``sensitivity`` /
``specificity`` columns MOVED while F1, precision, and recall held to the
digit — because a bootstrap mean is not invariant to iteration count and
the observed statistic is. The Principal Investigator ruled on 2026-08-20
to migrate the corpus rather than annotate it.

What this does, for every git-tracked ``evaluation.csv``,
``batch_summary.csv``, and ``evaluation.md`` outside ``archive/**``:

* read the observed triple from the row's OWN committed evaluation JSON —
  ``tile_classification.{mcc,sensitivity,specificity}.point`` where the
  block carries a ``point`` key, otherwise recomputed from that block's
  own committed ``confusion`` counts;
* replace ONLY the three metric cells, in place. No header is rewritten,
  no column is added, no other cell is touched, and the file is
  re-serialised through a round-trip that must reproduce the original
  bytes before any edit is applied;
* leave an undefined metric as an empty CSV cell / the word ``undefined``
  in Markdown — never ``0`` (errata E81).

A file is migrated only if EVERY non-empty metric cell in it currently
equals the resample mean of its own JSON (tolerance 5e-5). A file that
fails that gate is skipped with a recorded reason: it is not a
mean-under-the-wrong-name file but something else — most often a summary
whose per-condition JSONs were re-emitted without refreshing it — and
overwriting its cells would silently import a different vintage's
numbers alongside stale neighbours.

The new ``*_boot_mean`` columns the writer fix adds are for FUTURE files
only: adding columns to committed CSVs is not a surgical value
replacement, and the resample mean remains available in the JSON.

A machine-readable inventory is written to
``reports/csv-mcc-point-migration-2026-08-20.json``.

Usage::

    python scripts/migrate_csv_mcc_point.py --dry-run   # count, write nothing
    python scripts/migrate_csv_mcc_point.py --write

$0 API; local. Created 2026-08-20 (Session 138, audit remediation Phase 5).
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent

REPORT_PATH = PROJECT_ROOT / "reports/csv-mcc-point-migration-2026-08-20.json"

#: The three tile-level metrics, in the order the writers emit them.
METRICS = ("mcc", "sensitivity", "specificity")

#: Tolerance for "this committed cell IS the JSON resample mean". The cells
#: are rounded to 4 decimal places, so half a unit in the last place is the
#: widest an honest match can be.
MEAN_TOLERANCE = 5e-5

#: Markdown table header emitted by ``evaluate_detections.write_outputs``
#: whenever a tile-classification block is present. Migration of a Markdown
#: file is attempted only when its table header is exactly this string.
MD_HEADER = (
    "| Buffer | F1 | F1 CI | P | P CI | R | R CI "
    "| MCC | MCC CI | Sens | Spec |"
)

#: Column index of each metric within ``line.split("|")`` of an MD table row.
#: A body row splits into 13 fields: a leading empty string, eleven cells,
#: and a trailing empty string.
MD_CELL_INDEX = {"mcc": 8, "sensitivity": 10, "specificity": 11}
MD_ROW_FIELDS = 13

#: Rendered in an MD cell whose metric is undefined (errata E81); matches
#: ``evaluate_detections.UNDEFINED_DISPLAY``.
UNDEFINED_DISPLAY = "undefined"


# ── The observed statistics ───────────────────────────────────────────

def metrics_from_confusion(conf: dict[str, Any]) -> dict[str, float | None]:
    """Recompute the observed tile metrics from a 2 x 2 confusion matrix.

    Used for the committed blocks that predate the ``point`` key: the
    counts are in the artefact, so the observed statistic is recoverable
    without re-running anything.

    Args:
        conf: The block's ``confusion`` dict with ``tp`` / ``tn`` / ``fp``
            / ``fn`` counts.

    Returns:
        ``{"mcc": …, "sensitivity": …, "specificity": …}``, each rounded
        to 4 decimal places to match the JSON convention, and each
        ``None`` when its denominator vanishes — errata E81: an undefined
        metric is not zero.

    Examples:
        >>> metrics_from_confusion({"tp": 225, "tn": 153, "fp": 105, "fn": 4})
        {'mcc': 0.6146, 'sensitivity': 0.9825, 'specificity': 0.593}
        >>> metrics_from_confusion({"tp": 0, "tn": 0, "fp": 0, "fn": 5})
        {'mcc': None, 'sensitivity': 0.0, 'specificity': None}
    """
    tp = int(conf["tp"])
    tn = int(conf["tn"])
    fp = int(conf["fp"])
    fn = int(conf["fn"])
    denominator = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    mcc = (
        None if denominator == 0
        else round((tp * tn - fp * fn) / math.sqrt(denominator), 4)
    )
    sensitivity = None if (tp + fn) == 0 else round(tp / (tp + fn), 4)
    specificity = None if (tn + fp) == 0 else round(tn / (tn + fp), 4)
    return {"mcc": mcc, "sensitivity": sensitivity, "specificity": specificity}


def observed_triple(
    tile_classification: dict[str, Any],
) -> tuple[dict[str, float | None], str] | None:
    """Read the observed metric triple out of a ``tile_classification`` block.

    Args:
        tile_classification: The block as committed in ``evaluation.json``.

    Returns:
        ``(triple, source)`` where ``triple`` maps each metric name to its
        observed value (``None`` when undefined) and ``source`` is
        ``"point"`` (read straight off the block) or ``"confusion"`` (the
        block carries no ``point`` key, so the triple was recomputed from
        the committed counts). ``None`` when neither route is available.

    Examples:
        >>> observed_triple({"mcc": {"point": 0.5, "mean": 0.51},
        ...                  "sensitivity": {"point": 0.6, "mean": 0.6},
        ...                  "specificity": {"point": 0.7, "mean": 0.7}})[1]
        'point'
    """
    if not isinstance(tile_classification, dict) or not tile_classification:
        return None
    blocks = {m: tile_classification.get(m) for m in METRICS}
    if all(isinstance(b, dict) and "point" in b for b in blocks.values()):
        return {m: blocks[m]["point"] for m in METRICS}, "point"
    conf = tile_classification.get("confusion")
    if isinstance(conf, dict) and all(k in conf for k in ("tp", "tn", "fp", "fn")):
        return metrics_from_confusion(conf), "confusion"
    return None


def resample_means(
    tile_classification: dict[str, Any],
) -> dict[str, float | None]:
    """Read the bootstrap resample means — the values the writers published.

    Args:
        tile_classification: The block as committed in ``evaluation.json``.

    Returns:
        Metric name → resample mean, or ``None`` where the block records
        none. A bare float (a legacy adapter shape) IS the published
        value and is returned as such.
    """
    out: dict[str, float | None] = {}
    for metric in METRICS:
        block = tile_classification.get(metric)
        if isinstance(block, dict):
            out[metric] = block.get("mean")
        elif isinstance(block, (int, float)):
            out[metric] = float(block)
        else:
            out[metric] = None
    return out


def render_cell(value: float | None) -> str:
    """Render an observed metric for a CSV cell.

    Args:
        value: The observed statistic, or ``None`` when undefined.

    Returns:
        The value as ``str(float)`` renders it — which is how the
        ``csv`` module wrote the numbers being replaced — or the empty
        string for ``None`` (errata E81: never ``0``).

    Examples:
        >>> render_cell(0.6924)
        '0.6924'
        >>> render_cell(None)
        ''
    """
    return "" if value is None else str(float(value))


def render_md_cell(value: float | None) -> str:
    """Render an observed metric for a Markdown table cell (3 d.p.).

    Args:
        value: The observed statistic, or ``None`` when undefined.

    Returns:
        The value at three decimal places, or ``undefined`` — matching
        ``evaluate_detections._fmt_metric``.

    Examples:
        >>> render_md_cell(0.6924)
        '0.692'
        >>> render_md_cell(None)
        'undefined'
    """
    return UNDEFINED_DISPLAY if value is None else f"{value:.3f}"


def cell_is_migratable(
    cell: str, mean: float | None, point: float | None,
) -> bool:
    """Is this committed CSV cell safe to replace with the observed value?

    The cell must be recognisable as one of the two values the JSON can
    account for: the resample mean the writer published (the defect), or
    the observed point (already migrated — which is what makes the
    migration idempotent). Anything else means the cell came from
    somewhere this JSON cannot explain — a stale roll-up, a hand edit —
    and the file is left alone rather than half-corrected.

    Args:
        cell: The cell as committed (``""`` for an undefined metric).
        mean: The resample mean from the sibling JSON.
        point: The observed statistic this migration would write.

    Returns:
        ``True`` when the cell is empty (nothing was published) or is
        numerically the mean or the point within :data:`MEAN_TOLERANCE`.

    Examples:
        >>> cell_is_migratable("0.6925", 0.6925, 0.6924)
        True
        >>> cell_is_migratable("0.6924", 0.6925, 0.6924)
        True
        >>> cell_is_migratable("0.7457", 0.7467, 0.7466)
        False
    """
    if cell.strip() == "":
        return True
    try:
        value = float(cell)
    except ValueError:
        return False
    return any(
        candidate is not None
        and math.isclose(value, float(candidate), rel_tol=0.0,
                         abs_tol=MEAN_TOLERANCE)
        for candidate in (mean, point)
    )


# ── CSV migration ─────────────────────────────────────────────────────

def _parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text into rows without newline translation."""
    return list(csv.reader(io.StringIO(text, newline="")))


def _render_csv(rows: list[list[str]]) -> str:
    """Serialise rows with the ``csv`` module's default dialect (CRLF)."""
    buffer = io.StringIO(newline="")
    csv.writer(buffer).writerows(rows)
    return buffer.getvalue()


def migrate_csv_text(
    text: str,
    triple_for: dict[str, dict[str, float | None]],
    means_for: dict[str, dict[str, float | None]],
    label_column: str | None,
) -> tuple[str, int, str | None]:
    """Replace the three metric cells of every row of one CSV.

    Args:
        text: The file as committed.
        triple_for: Row key → observed triple. The key is the row's
            ``label`` when ``label_column`` is given, else ``""``.
        means_for: Row key → resample means, for the pre-state gate.
        label_column: Column name holding the row key, or ``None`` when
            the whole file maps to a single key.

    Returns:
        ``(new_text, n_cells_changed, skip_reason)``. ``skip_reason`` is
        ``None`` on success; when it is set the text is returned
        unchanged and nothing should be written.
    """
    rows = _parse_csv(text)
    if _render_csv(rows) != text:
        return text, 0, "csv_round_trip_not_byte_identical"
    if not rows:
        return text, 0, "empty_file"
    header = rows[0]
    if not all(m in header for m in METRICS):
        return text, 0, "no_metric_columns"
    index = {m: header.index(m) for m in METRICS}
    label_index = header.index(label_column) if label_column else None
    widest = max([*index.values(), label_index or 0])

    changed = 0
    for row in rows[1:]:
        if not row:
            continue
        if len(row) <= widest:
            return text, 0, "short_data_row"
        key = row[label_index] if label_index is not None else ""
        if key not in triple_for:
            return text, 0, f"no_evaluation_json_for_row:{key}"
        triple, means = triple_for[key], means_for[key]
        for metric in METRICS:
            if not cell_is_migratable(
                row[index[metric]], means[metric], triple[metric],
            ):
                return text, 0, f"cell_is_neither_mean_nor_point:{metric}"
        for metric in METRICS:
            new_cell = render_cell(triple[metric])
            if row[index[metric]] != new_cell:
                row[index[metric]] = new_cell
                changed += 1
    return _render_csv(rows), changed, None


# ── Markdown migration ────────────────────────────────────────────────

def migrate_md_text(
    text: str,
    triple: dict[str, float | None],
    means: dict[str, float | None],
) -> tuple[str, int, str | None]:
    """Replace the MCC / Sens / Spec cells of one ``evaluation.md`` table.

    Only the three value cells move; the pipes, padding, and every other
    character of the line are preserved by rebuilding the line from its
    own ``split("|")`` fields.

    Args:
        text: The file as committed.
        triple: The observed triple for this evaluation.
        means: The resample means, for the pre-state gate.

    Returns:
        ``(new_text, n_cells_changed, skip_reason)`` — as
        :func:`migrate_csv_text`.
    """
    lines = text.split("\n")
    header_positions = [
        i for i, line in enumerate(lines) if line.strip() == MD_HEADER
    ]
    if not header_positions:
        return text, 0, "no_mcc_table_header"
    if len(header_positions) > 1:
        return text, 0, "multiple_mcc_tables"

    changed = 0
    start = header_positions[0] + 2  # skip the header and its rule row
    for i in range(start, len(lines)):
        line = lines[i]
        if not line.startswith("| "):
            break
        fields = line.split("|")
        if len(fields) != MD_ROW_FIELDS:
            return text, 0, "unexpected_table_row_shape"
        for metric, position in MD_CELL_INDEX.items():
            committed = fields[position].strip()
            if committed not in (
                render_md_cell(means[metric]), render_md_cell(triple[metric]),
            ):
                return text, 0, f"cell_is_neither_mean_nor_point:{metric}"
        for metric, position in MD_CELL_INDEX.items():
            new_cell = f" {render_md_cell(triple[metric])} "
            if fields[position] != new_cell:
                fields[position] = new_cell
                changed += 1
        lines[i] = "|".join(fields)
    return "\n".join(lines), changed, None


# ── Corpus walk ───────────────────────────────────────────────────────

def tracked_files(pattern: str) -> list[str]:
    """Git-tracked paths matching ``pattern``, excluding ``archive/**``.

    ``archive/**`` is deliberately out of scope, matching erratum E82's
    re-emission scope and the Phase 2 ``ci_unreliable`` migration:
    archived artefacts are superseded historical snapshots, and
    rewriting them would blur what "archived" means.
    """
    out = subprocess.run(
        ["git", "ls-files", pattern],
        capture_output=True, text=True, check=True, cwd=PROJECT_ROOT,
    ).stdout.split()
    return [rel for rel in out if not rel.startswith("archive/")]


def _load_tile_classification(path: Path) -> dict[str, Any] | None:
    """Read ``summary.tile_classification`` from an evaluation JSON."""
    try:
        doc = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    block = (doc.get("summary") or {}).get("tile_classification")
    return block if isinstance(block, dict) else None


def _sibling_maps(
    json_path: Path,
) -> tuple[dict[str, dict], dict[str, dict], str | None]:
    """Build the single-key maps for a file scored by one evaluation."""
    tile = _load_tile_classification(json_path)
    if tile is None:
        return {}, {}, "no_tile_classification_in_sibling_json"
    resolved = observed_triple(tile)
    if resolved is None:
        return {}, {}, "no_point_and_no_confusion"
    triple, source = resolved
    return {"": triple}, {"": resample_means(tile)}, f"source:{source}"


def _batch_maps(
    csv_path: Path,
) -> tuple[dict[str, dict], dict[str, dict], str | None]:
    """Build label-keyed maps from the immediate sub-directories' evaluations."""
    triples: dict[str, dict] = {}
    means: dict[str, dict] = {}
    sources: set[str] = set()
    for child in sorted(csv_path.parent.iterdir()):
        json_path = child / "evaluation.json"
        if not (child.is_dir() and json_path.exists()):
            continue
        doc = json.loads(json_path.read_text())
        label = (doc.get("summary") or {}).get("label")
        tile = (doc.get("summary") or {}).get("tile_classification")
        if label is None or not isinstance(tile, dict):
            continue
        if label in triples:
            return {}, {}, f"duplicate_condition_label:{label}"
        resolved = observed_triple(tile)
        if resolved is None:
            continue
        triples[label], source = resolved
        means[label] = resample_means(tile)
        sources.add(source)
    if not triples:
        return {}, {}, "no_condition_evaluations_in_subdirectories"
    return triples, means, "source:" + "+".join(sorted(sources))


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true",
                      help="Report what would change; write nothing.")
    mode.add_argument("--write", action="store_true",
                      help="Apply the migration and write the inventory.")
    args = parser.parse_args()

    changed_files: list[dict] = []
    skipped: list[dict] = []
    not_applicable: list[dict] = []
    recomputed: set[str] = set()
    n_cells = 0
    max_delta = 0.0
    max_delta_file = ""
    n_scanned = 0
    n_cells_over_0_001 = 0

    # Reasons that mean "this file has nothing of ours in it", as opposed to
    # "this file looks like ours but failed a safety gate". Only the latter
    # is a skip a reader needs to act on.
    inapplicable = {
        "no_metric_columns", "no_mcc_table_header",
        "no_tile_classification_in_sibling_json",
    }

    jobs: list[tuple[str, str]] = (
        [(rel, "evaluation_csv") for rel in tracked_files("*evaluation.csv")]
        + [(rel, "batch_csv") for rel in tracked_files("*batch_summary.csv")]
        + [(rel, "evaluation_md") for rel in tracked_files("*evaluation.md")]
    )

    for rel, kind in jobs:
        n_scanned += 1
        path = PROJECT_ROOT / rel
        with open(path, newline="", encoding="utf-8") as handle:
            original = handle.read()

        # Cheap applicability check first: a file with no tile-metric
        # columns at all is not a D30 artefact, and reading its
        # evaluation JSON to discover that would be wasted work.
        if kind == "evaluation_md":
            if MD_HEADER not in original:
                not_applicable.append({"file": rel,
                                       "reason": "no_mcc_table_header"})
                continue
        else:
            head = _parse_csv(original)
            if not head or not all(m in head[0] for m in METRICS):
                not_applicable.append({"file": rel,
                                       "reason": "no_metric_columns"})
                continue

        if kind == "batch_csv":
            triples, means, note = _batch_maps(path)
            label_column: str | None = "label"
        else:
            triples, means, note = _sibling_maps(path.parent / "evaluation.json")
            label_column = None
        if not triples:
            bucket = not_applicable if note in inapplicable else skipped
            bucket.append({"file": rel, "reason": note})
            continue
        if note and "confusion" in note:
            recomputed.add(rel)

        if kind == "evaluation_md":
            new_text, cells, reason = migrate_md_text(
                original, triples[""], means[""],
            )
        else:
            new_text, cells, reason = migrate_csv_text(
                original, triples, means, label_column,
            )
        if reason is not None:
            bucket = not_applicable if reason in inapplicable else skipped
            bucket.append({"file": rel, "reason": reason})
            continue

        # Per-cell delta census over the CSV layer — one count per data row
        # per metric, i.e. the cells a reader actually meets. Computed
        # whether or not the cell moved, so the census does not depend on
        # rounding.
        if kind != "evaluation_md":
            rows = _parse_csv(original)
            header = rows[0]
            label_index = header.index(label_column) if label_column else None
            for row in rows[1:]:
                if not row:
                    continue
                key = row[label_index] if label_index is not None else ""
                for metric in METRICS:
                    point, mean = triples[key][metric], means[key][metric]
                    if point is None or mean is None:
                        continue
                    delta = abs(float(point) - float(mean))
                    if delta > max_delta:
                        max_delta, max_delta_file = delta, rel
                    if delta > 0.001:
                        n_cells_over_0_001 += 1
        if cells == 0:
            continue
        changed_files.append({"file": rel, "kind": kind, "n_cells": cells})
        n_cells += cells
        if args.write:
            with open(path, "w", newline="", encoding="utf-8") as handle:
                handle.write(new_text)

    print(f"files scanned            : {n_scanned}")
    print(f"files changed            : {len(changed_files)}")
    print(f"metric cells changed     : {n_cells}")
    print(f"files skipped (gated)    : {len(skipped)}")
    print(f"files not applicable     : {len(not_applicable)}")
    n_evaluations_recomputed = len({str(Path(r).parent) for r in recomputed})
    print(f"point recomputed (files) : {len(recomputed)} "
          f"({n_evaluations_recomputed} evaluation(s))")
    print(f"max |mean - point|       : {max_delta:.4f} ({max_delta_file})")
    print(f"CSV cells |delta| >0.001 : {n_cells_over_0_001}")
    for row in skipped[:20]:
        print(f"  SKIPPED: {row['file']} — {row['reason']}")

    if args.write:
        REPORT_PATH.write_text(json.dumps({
            "migrated_at": "2026-08-20",
            "defect": "D30",
            "rule": (
                "publish tile_classification.<metric>.point (or the value "
                "recomputed from the committed confusion counts) under the "
                "columns named mcc / sensitivity / specificity; the resample "
                "mean stays in the JSON"
            ),
            "scope": "git-tracked, archive/** excluded",
            "n_files_scanned": n_scanned,
            "n_files_changed": len(changed_files),
            "n_cells_changed": n_cells,
            "max_abs_mean_minus_point": round(max_delta, 6),
            "max_abs_mean_minus_point_file": max_delta_file,
            "n_csv_cells_delta_over_0_001": n_cells_over_0_001,
            "n_evaluations_point_recomputed_from_confusion":
                n_evaluations_recomputed,
            "files_point_recomputed_from_confusion": sorted(recomputed),
            "files_skipped": skipped,
            "files_not_applicable": not_applicable,
            "files": changed_files,
        }, indent=2) + "\n")
        print(f"inventory -> {REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
