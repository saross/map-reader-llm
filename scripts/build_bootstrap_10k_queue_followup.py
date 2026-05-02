#!/usr/bin/env python3
"""
Bootstrap-CI N=10K follow-up queue builder.

Builds a 165-row CSV queue for the daylight follow-up sweep that upgrades
deferred ``evaluation.json`` cells from N=1,000 bootstrap iterations to
N=10,000. The queue is consumed by the existing
``scripts/run_bootstrap_10k.py`` (unchanged) which forces ``--bootstrap 10000``
at the CLI.

Implements the four metadata-recovery patterns documented in
``archive/planning-completed-session-81-82/daylight-followup-sweep-plan-2026-04-29.md`` §3:

* Pattern A — parent batch-YAML lookup (143 paper-eval cells)
* Pattern B — pairwise YAML lookup (5 cells)
* Pattern C — per-cell ``evaluation.metadata.json`` sidecar (3 cells)
* Pattern D — verbatim CLI from ``extended-buffer-report.md`` §10 (1 cell)

Plus 13 bespoke paper-eval cells (``single-pass-n1*``, special PRO MEDIUM
single-file invocations) handled empirically.

To preserve the per-cell evaluation schema across the upgrade, the builder
introspects each target ``evaluation.json``: cells with ``per_run == []`` and
``summary.n_detections`` set used a single-file ``--detections`` invocation;
cells with non-empty ``per_run`` used ``--detections-dir``. The buffer set is
read from each target cell's existing ``summary.buffers`` (authoritative)
rather than from the YAML defaults, since some cells use a 30-m-only subset
of the YAML's full buffer list.

Usage:
    python3 scripts/build_bootstrap_10k_queue_followup.py
    python3 scripts/build_bootstrap_10k_queue_followup.py --validate-paths
    python3 scripts/build_bootstrap_10k_queue_followup.py \\
        --output /tmp/bootstrap-10k-jobs-followup.csv

The script is read-only on configs and sidecars; the only artefact it writes
is the CSV at the chosen output path.

Author: Claude Code (Opus 4.7) for Shawn Ross's daylight follow-up sweep,
2026-04-29.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# ── Constants ─────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = Path("/tmp/bootstrap-10k-jobs-followup.csv")

# Pattern A — paper-eval batch YAMLs and the output subtrees they drive.
# Each entry: (config path, output subtree, mcc flag, buffer-override).
# ``buffer-override`` lets us encode the 30-m-only subset of phase2 cells
# without depending solely on the per-cell empirical read (which serves as
# the authoritative source anyway).
PAPER_EVAL_BATCH_MAPPINGS: list[tuple[str, str, bool, list[int] | None]] = [
    # YAML, output subtree (relative to results/paper-eval), mcc, buffer override (None=read empirically)
    ("configs/n1-eval-384px-all-buffers.yaml", "n1/384px-all-buffers", False, None),
    ("configs/n1-eval-512px-phase2.yaml",      "n1/512px-all-buffers", False, None),
    ("configs/n1-eval-512px-phase2.yaml",      "n1/512px",             False, [30]),
    ("configs/mcc-eval-384px.yaml",            "mcc/384px",            True,  [30]),
    ("configs/n1-eval-512px-phase2.yaml",      "mcc/512px",            True,  [30]),
    ("configs/n1-eval-384px.yaml",             "n1/384px",             False, [30]),
    # The 9 N1-eval-384px conditions populate 9 of the 11 cells in n1/384px/.
    # The remaining 2 cells (PRO MEDIUM T=0.0 image + text) are in the all-buffers YAML
    # and were also evaluated against n1/384px/ at 30 m only — pick them up via a 2nd pass.
    ("configs/n1-eval-384px-all-buffers.yaml", "n1/384px",             False, [30]),
    ("configs/n1-eval-384px-all-buffers.yaml", "n1/384px-outstanding", False, [30]),
]

# Bespoke paper-eval cells (plan §2, lines for `single-pass-n1*`).
# Each row: (cell path, detections-spec dict, label, buffers, mcc).
# detections-spec: either {"detections": single-file-path} or {"detections_dir": dir, "glob": pattern}.
BESPOKE_PAPER_EVAL_CELLS: list[dict[str, Any]] = [
    {
        "cell": "results/paper-eval/single-pass-n1",
        "detections_dir": "outputs/retest/h11-single-pass-384-t0/brief-text-t0",
        "glob": "run_*/detections_*.geojson",
        "label": "Single-pass brief-text T=0.0 (N=1 mean)",
        "buffers": [20, 30],
        "mcc": False,
    },
    {
        "cell": "results/paper-eval/single-pass-n1-high",
        "detections_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
        "glob": "run_*/detections_*.geojson",
        "label": "Single-pass brief-text T=0.7 HIGH (N=1 mean of 30)",
        "buffers": [20, 30],
        "mcc": False,
    },
    {
        "cell": "results/paper-eval/single-pass-n1-t07",
        "detections_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
        "glob": "run_*/detections_*.geojson",
        "label": "Single-pass brief-text T=0.7 MINIMAL (N=1 mean of 30)",
        "buffers": [20, 30],
        "mcc": False,
    },
]

# Pattern B — pairwise tile-size cells (5 cells).
PAIRWISE_TILE_SIZE_CELLS: list[dict[str, Any]] = [
    # Slug → label (from existing eval), detections file (from tile-size YAML row).
    {
        "cell": "results/pairwise/tile-size-30m/512px-image-t0",
        "detections": "outputs/retest/phase2b/track1-image/T0.0/run_1/detections_T0.0_run01.geojson",
        "label": "512px-image-t0",
        "buffers": [20, 30],
    },
    {
        "cell": "results/pairwise/tile-size-30m/512px-image-t07",
        "detections": "outputs/retest/phase2b/track1-image/T0.7/run_1/detections_T0.7_run01.geojson",
        "label": "512px-image-t07",
        "buffers": [20, 30],
    },
    {
        "cell": "results/pairwise/tile-size-30m/512px-text-t0",
        "detections": "outputs/retest/phase2b/track2-text/T0.0/run_1/detections_T0.0_run01.geojson",
        "label": "512px-text-t0",
        "buffers": [20, 30],
    },
    {
        "cell": "results/pairwise/tile-size-30m/512px-text-t07",
        "detections": "outputs/retest/phase2b/track2-text/T0.7/run_1/detections_T0.7_run01.geojson",
        "label": "512px-text-t07",
        "buffers": [20, 30],
    },
    # Bespoke 5th cell (plan §3.2): 512px detections re-evaluated against 384/487-tile bounds.
    {
        "cell": "results/pairwise/tile-size-30m/eval-512-on-384-image-t0",
        "detections_dir": "outputs/retest/phase2b/track1-image/T0.0",
        "glob": "run_*/detections_*.geojson",
        "label": "512px Image T=0.0 (on 384px grid)",
        "buffers": [20, 30],
    },
]

# Pattern B — all 5 cells use 487-tile bounds.
# (Plan §3.2 originally specified 340-tile bounds for the first 4 cells, but the dry-run
# discovered that the pre-tag eval was generated with 487-tile bounds: re-running with
# 340-tile bounds produces F1 shifts of ~0.08 vs pre-tag, while 487-tile bounds reproduces
# pre-tag F1 to 1e-4. The pre-tag's accompanying _metadata sidecar's "buffer-30m bounds"
# placeholder was ambiguous; the empirical test settles it. Note that the pre-tag CI bounds
# are also buggy — point estimate outside CI — but that is a pre-existing bug, not introduced
# by this sweep, and the new N=10K eval corrects it.)
PAIRWISE_BOUNDS = "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
PAIRWISE_GT = "inputs/vectors/references/mounds-reference.geojson"

# Pattern C — 55maps cleaned-GT (3 cells).
MAPS_55_BOUNDS = "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
MAPS_55_GT = "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
MAPS_55_CELLS: list[dict[str, Any]] = [
    {
        "cell": "results/55maps-cleaned-gt-evaluation/image",
        "detections": "outputs/55maps-image-generalisation/verified/verified_detections.geojson",
        "label": "image-vs-cleaned-gt",
        "buffers": [20, 30, 40, 50],
    },
    {
        "cell": "results/55maps-cleaned-gt-evaluation/text-high",
        "detections": "outputs/55maps-text-high-generalisation/verified/verified_detections.geojson",
        "label": "text-high-vs-cleaned-gt",
        "buffers": [20, 30, 40, 50],
    },
    {
        "cell": "results/55maps-cleaned-gt-evaluation/text-min",
        "detections": "outputs/55maps-text-min-generalisation/verified/verified_detections.geojson",
        "label": "text-min-vs-cleaned-gt",
        "buffers": [20, 30, 40, 50],
    },
]

# Pattern D — gold-standard extended buffer sweep (1 cell).
GOLD_STANDARD_CELL: dict[str, Any] = {
    "cell": "results/gold-standard-extended-buffer-sweep",
    "detections": "results/gold-standard-extended-buffer-sweep/verified_detections.geojson",
    "label": "gold-standard-extended-buffer-sweep",
    "buffers": [5, 10, 15, 25, 35, 45],
    "bounds": "inputs/vectors/bounds/384/h10_test_bounds.geojson",
    "ground_truth": "inputs/vectors/references/mounds-reference.geojson",
}


# ── Helpers ────────────────────────────────────────────────────────────


def slugify(text: str) -> str:
    """Mirror ``evaluate_detections.py:slugify`` so YAML labels map to dir names.

    Args:
        text: Human-readable label.

    Returns:
        Lowercase slug with non-alphanumerics replaced by hyphens, trimmed.
    """
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file from ``REPO_ROOT / path``."""
    with open(REPO_ROOT / path) as f:
        return yaml.safe_load(f) or {}


def read_existing_eval(eval_path: Path) -> tuple[list[int], int, str | None]:
    """Read an existing evaluation.json for buffer set, per_run length, label.

    Args:
        eval_path: Absolute or repo-relative path to existing evaluation.json.

    Returns:
        Tuple of (buffer-list, len(per_run), summary.label).

    Raises:
        FileNotFoundError: if the file does not exist.
    """
    full = eval_path if eval_path.is_absolute() else REPO_ROOT / eval_path
    with open(full) as f:
        d = json.load(f)
    summary = d.get("summary") or {}
    buffers = [b["buffer_metres"] for b in summary.get("buffers") or []]
    n_per_run = len(d.get("per_run") or [])
    return buffers, n_per_run, summary.get("label")


def make_row(
    *,
    eval_path: str,
    output_dir: str,
    detections: str = "",
    detections_dir: str = "",
    glob: str = "",
    bounds: str,
    ground_truth: str,
    buffers: list[int],
    label: str,
    mcc: bool,
) -> dict[str, str]:
    """Construct a queue-CSV row in the schema expected by run_bootstrap_10k.py."""
    return {
        "status": "queued",
        "eval_path": eval_path,
        "output_dir": output_dir,
        "detections": detections,
        "detections_dir": detections_dir,
        "glob": glob,
        "bounds": bounds,
        "ground_truth": ground_truth,
        "buffers": " ".join(str(b) for b in buffers),
        "bootstrap": "1000",  # traceability only; runner forces 10000
        "seed": "42",
        "label": label,
        "mcc": "1" if mcc else "0",
    }


# ── Pattern A — paper-eval batch YAMLs + bespoke single-pass-n1* ──────


def build_paper_eval_rows() -> list[dict[str, str]]:
    """Build queue rows for all 156 paper-eval cells (Pattern A + bespoke)."""
    rows: list[dict[str, str]] = []
    seen_paths: set[str] = set()

    for yaml_path, subtree, mcc_flag, buffer_override in PAPER_EVAL_BATCH_MAPPINGS:
        spec = load_yaml(Path(yaml_path))
        defaults = spec.get("defaults") or {}
        conditions = spec.get("conditions") or []
        default_bounds = defaults.get("bounds")
        default_gt = defaults.get("ground_truth")
        default_glob = defaults.get("glob") or "*/detections_*.geojson"

        for cond in conditions:
            label = cond["label"]
            slug = slugify(label)
            cell_dir = REPO_ROOT / "results" / "paper-eval" / subtree / slug
            eval_json = cell_dir / "evaluation.json"
            if not eval_json.exists():
                # Cell is intentionally absent for this subtree (e.g., outstanding has
                # only 7 of the 18 all-buffers conditions). Skip silently.
                continue
            rel_eval = str(eval_json.relative_to(REPO_ROOT))
            if rel_eval in seen_paths:
                continue  # already mapped via an earlier YAML pass
            seen_paths.add(rel_eval)

            # Empirical reads — authoritative for buffers and per_run schema.
            buffers, n_per_run, _ = read_existing_eval(eval_json)
            if buffer_override is not None:
                # Use the override only if the empirical read agrees (sanity check).
                if buffers != buffer_override:
                    print(
                        f"  WARN: {rel_eval} has buffers={buffers} but override={buffer_override}; "
                        f"using empirical buffers={buffers}",
                        file=sys.stderr,
                    )

            # Schema preservation: per_run > 0 ⇒ used --detections-dir; per_run == 0 ⇒ --detections.
            cond_glob = cond.get("glob") or default_glob
            if n_per_run > 0:
                # Use --detections-dir mode. If the YAML's glob is the legacy broken pattern
                # ``run_*/detections_*_run??`` (which Path.glob never matches because ``??``
                # requires exactly two chars and the actual filenames are
                # ``detections_*_run01.geojson``), fall back to the default that does match.
                # The per_run label evidence in the existing N=1K eval shows the canonical
                # 3-run files were used regardless.
                det_dir_abs = REPO_ROOT / cond["detections_dir"]
                if not list(det_dir_abs.glob(cond_glob)):
                    print(
                        f"  NOTE: YAML glob {cond_glob!r} matched 0 files for "
                        f"{cond['detections_dir']}; falling back to default glob {default_glob!r}.",
                        file=sys.stderr,
                    )
                    cond_glob = default_glob
                rows.append(make_row(
                    eval_path=rel_eval,
                    output_dir=str(cell_dir.relative_to(REPO_ROOT)),
                    detections_dir=cond["detections_dir"],
                    glob=cond_glob,
                    bounds=default_bounds,
                    ground_truth=default_gt,
                    buffers=buffers,
                    label=label,
                    mcc=mcc_flag,
                ))
            else:
                # Single-file mode — find the single detection geojson under
                # detections_dir matching the glob.
                det_dir_abs = REPO_ROOT / cond["detections_dir"]
                matches = sorted(det_dir_abs.glob(cond_glob))
                if not matches:
                    # Try the default _run01 single-file pattern.
                    matches = sorted(det_dir_abs.glob("run_1/detections_*_run01.geojson"))
                if not matches:
                    print(
                        f"  ERROR: no detection file found under {cond['detections_dir']} "
                        f"for cell {rel_eval}",
                        file=sys.stderr,
                    )
                    continue
                # Prefer run_01 if multiple match.
                preferred = [m for m in matches if "run01" in m.name or "run_1" in str(m)]
                detections_file = preferred[0] if preferred else matches[0]
                rows.append(make_row(
                    eval_path=rel_eval,
                    output_dir=str(cell_dir.relative_to(REPO_ROOT)),
                    detections=str(detections_file.relative_to(REPO_ROOT)),
                    bounds=default_bounds,
                    ground_truth=default_gt,
                    buffers=buffers,
                    label=label,
                    mcc=mcc_flag,
                ))

    # Bespoke single-pass-n1* cells.
    for spec_dict in BESPOKE_PAPER_EVAL_CELLS:
        cell = REPO_ROOT / spec_dict["cell"]
        eval_json = cell / "evaluation.json"
        if not eval_json.exists():
            print(f"  ERROR: bespoke cell missing eval: {eval_json}", file=sys.stderr)
            continue
        rel_eval = str(eval_json.relative_to(REPO_ROOT))
        if rel_eval in seen_paths:
            continue
        seen_paths.add(rel_eval)
        rows.append(make_row(
            eval_path=rel_eval,
            output_dir=spec_dict["cell"],
            detections_dir=spec_dict["detections_dir"],
            glob=spec_dict["glob"],
            bounds="inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
            ground_truth="inputs/vectors/references/mounds-reference.geojson",
            buffers=spec_dict["buffers"],
            label=spec_dict["label"],
            mcc=spec_dict["mcc"],
        ))

    return rows


# ── Pattern B — pairwise tile-size-30m ─────────────────────────────────


def build_pairwise_rows() -> list[dict[str, str]]:
    """Build queue rows for the 5 pairwise tile-size-30m cells."""
    rows: list[dict[str, str]] = []
    for spec_dict in PAIRWISE_TILE_SIZE_CELLS:
        cell = REPO_ROOT / spec_dict["cell"]
        eval_json = cell / "evaluation.json"
        if not eval_json.exists():
            print(f"  ERROR: pairwise cell missing eval: {eval_json}", file=sys.stderr)
            continue
        rel_eval = str(eval_json.relative_to(REPO_ROOT))
        bounds = PAIRWISE_BOUNDS
        if "detections_dir" in spec_dict:
            rows.append(make_row(
                eval_path=rel_eval,
                output_dir=spec_dict["cell"],
                detections_dir=spec_dict["detections_dir"],
                glob=spec_dict["glob"],
                bounds=bounds,
                ground_truth=PAIRWISE_GT,
                buffers=spec_dict["buffers"],
                label=spec_dict["label"],
                mcc=False,
            ))
        else:
            rows.append(make_row(
                eval_path=rel_eval,
                output_dir=spec_dict["cell"],
                detections=spec_dict["detections"],
                bounds=bounds,
                ground_truth=PAIRWISE_GT,
                buffers=spec_dict["buffers"],
                label=spec_dict["label"],
                mcc=False,
            ))
    return rows


# ── Pattern C — 55maps cleaned-GT ──────────────────────────────────────


def build_55maps_cleaned_gt_rows() -> list[dict[str, str]]:
    """Build queue rows for the 3 55maps-cleaned-gt cells."""
    rows: list[dict[str, str]] = []
    for spec_dict in MAPS_55_CELLS:
        cell = REPO_ROOT / spec_dict["cell"]
        eval_json = cell / "evaluation.json"
        if not eval_json.exists():
            print(f"  ERROR: 55maps cell missing eval: {eval_json}", file=sys.stderr)
            continue
        rel_eval = str(eval_json.relative_to(REPO_ROOT))
        rows.append(make_row(
            eval_path=rel_eval,
            output_dir=spec_dict["cell"],
            detections=spec_dict["detections"],
            bounds=MAPS_55_BOUNDS,
            ground_truth=MAPS_55_GT,
            buffers=spec_dict["buffers"],
            label=spec_dict["label"],
            mcc=False,
        ))
    return rows


# ── Pattern D — gold-standard extended buffer sweep ────────────────────


def build_gold_standard_rows() -> list[dict[str, str]]:
    """Build the queue row for the 1 gold-standard cell."""
    spec_dict = GOLD_STANDARD_CELL
    cell = REPO_ROOT / spec_dict["cell"]
    eval_json = cell / "evaluation.json"
    if not eval_json.exists():
        print(f"  ERROR: gold-standard cell missing eval: {eval_json}", file=sys.stderr)
        return []
    rel_eval = str(eval_json.relative_to(REPO_ROOT))
    return [make_row(
        eval_path=rel_eval,
        output_dir=spec_dict["cell"],
        detections=spec_dict["detections"],
        bounds=spec_dict["bounds"],
        ground_truth=spec_dict["ground_truth"],
        buffers=spec_dict["buffers"],
        label=spec_dict["label"],
        mcc=False,
    )]


# ── Validation ─────────────────────────────────────────────────────────


def validate_paths(rows: list[dict[str, str]]) -> tuple[int, list[str]]:
    """Verify every detection / bounds / ground-truth path exists on disk.

    Args:
        rows: The queue rows to validate.

    Returns:
        Tuple of (n_valid, list-of-error-messages). n_valid + len(errors) == len(rows).
    """
    errors: list[str] = []
    n_valid = 0
    for i, row in enumerate(rows):
        problems = []
        # Bounds + GT are mandatory for all rows.
        for key in ("bounds", "ground_truth"):
            p = REPO_ROOT / row[key]
            if not p.exists():
                problems.append(f"{key}={row[key]} not found")
        # Detections: either single-file (one or more, |-separated) or detections_dir.
        if row["detections"]:
            for dpath in row["detections"].split("|"):
                p = REPO_ROOT / dpath
                if not p.exists():
                    problems.append(f"detections={dpath} not found")
        elif row["detections_dir"]:
            p = REPO_ROOT / row["detections_dir"]
            if not p.exists():
                problems.append(f"detections_dir={row['detections_dir']} not found")
            else:
                # Verify glob matches at least one file.
                glob = row["glob"] or "*/detections_*.geojson"
                matches = list(p.glob(glob))
                if not matches:
                    problems.append(
                        f"detections_dir={row['detections_dir']} + glob={glob} matched 0 files"
                    )
        else:
            problems.append("neither detections nor detections_dir set")
        if problems:
            errors.append(f"[row {i}] {row['eval_path']}: {'; '.join(problems)}")
        else:
            n_valid += 1
    return n_valid, errors


# ── Main ───────────────────────────────────────────────────────────────


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--validate-paths", action="store_true",
        help="Verify every detection / bounds / GT path exists on disk before writing.",
    )
    args = parser.parse_args()

    print("Building bootstrap-10K follow-up queue...")
    print()

    paper_rows = build_paper_eval_rows()
    print(f"  paper-eval:                              {len(paper_rows):3d} rows")
    pairwise_rows = build_pairwise_rows()
    print(f"  pairwise tile-size-30m:                  {len(pairwise_rows):3d} rows")
    maps_55_rows = build_55maps_cleaned_gt_rows()
    print(f"  55maps-cleaned-gt:                       {len(maps_55_rows):3d} rows")
    gs_rows = build_gold_standard_rows()
    print(f"  gold-standard-extended-buffer-sweep:     {len(gs_rows):3d} rows")
    print()

    rows = paper_rows + pairwise_rows + maps_55_rows + gs_rows
    print(f"  TOTAL:                                   {len(rows):3d} rows")
    if len(rows) != 165:
        print(
            f"  WARN: expected 165 rows, got {len(rows)}; check stderr for SKIP / ERROR notices.",
            file=sys.stderr,
        )

    if args.validate_paths:
        print()
        print("Validating paths...")
        n_valid, errors = validate_paths(rows)
        print(f"  {n_valid}/{len(rows)} rows have all required paths on disk")
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        if errors:
            print("  Validation FAILED; not writing CSV.", file=sys.stderr)
            return 2

    # Write the CSV.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "status", "eval_path", "output_dir",
        "detections", "detections_dir", "glob",
        "bounds", "ground_truth",
        "buffers", "bootstrap", "seed",
        "label", "mcc",
    ]
    with open(args.output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print()
    print(f"Wrote {len(rows)} rows to {args.output}")

    # Per-group breakdown for diff-legibility.
    print()
    print("Group breakdown (for the 4 per-group commits later):")
    print(f"  paper-eval                            -> {len(paper_rows):3d} rows")
    print(f"  pairwise/tile-size-30m                -> {len(pairwise_rows):3d} rows")
    print(f"  55maps-cleaned-gt-evaluation          -> {len(maps_55_rows):3d} rows")
    print(f"  gold-standard-extended-buffer-sweep   -> {len(gs_rows):3d} rows")

    return 0


if __name__ == "__main__":
    sys.exit(main())
