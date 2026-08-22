#!/usr/bin/env python3
"""E82 corpus re-emission: replay every BCa-era evaluation at B = 10,000.

Executes the campaign specified in
``planning/e82-corpus-reemission-2026-08-20.md`` (pre-run-review contract,
PI-approved 2026-08-20, amended same day after the fresh-context pre-launch
audit). Every git-tracked, non-archive ``evaluation.json`` whose metadata
vintage is 1.1 or 1.2 — the BCa era, selected by VINTAGE rather than declared
method so the 22 method-silent register-backing cells are included without
assuming what they ran (the D17 principle) — is replayed from its own
recovered recipe with only the bootstrap effort standardised, through the
fixed wrapper (``122104b8a``) and the current writer. Re-emitted files land at
metadata 1.3, which is also the resume criterion.

**Input-vintage rule (audit blocker B1; PI ruling 2026-08-20).** ~324 cells
were scored against inputs that later changed (defect D40). The campaign's
invariant is that ONLY the bootstrap effort moves, so each cell is replayed
against current inputs first and, if the point gate fails, against a bounded
plan of committed input vintages ADJACENT to its own ``generated_at_utc`` —
the all-before baseline, then single-input flips to the first-after commit,
then all-after (cap 6) — materialised from git history. Evaluations are
sometimes scored against a working tree committed minutes later, so the
before-vintage alone is not always the consumed state (measured on the
pilot: a detections commit landed 2 minutes after its evals). A passing
replay has its recorded input paths normalised back to the repo-relative
originals, with the pinned commits recorded in
``_metadata.e82_input_vintage``. Reference-vintage reconciliation is a
separate, deliberately unbundled decision (the E81/E82 lesson).

Guards, per the amended contract:

* **Point gate** — F1/precision/recall per buffer, observed tile points, and
  confusion counts must reproduce exactly (1e-9) on whichever attempt is
  accepted; otherwise the committed file is untouched and the cell fails.
  Per-run tile points are compared by run LABEL, not list index (PI ruling
  C1, 2026-08-22), so pools the canonical resolver replays in a different
  order than the original batch glob consumed them (>= 10 runs) pass with
  zero tolerance loss and are counted in ``n_order_normalised`` (expected
  6 corpus-wide); the D41 re-aggregation exception (expected 19
  corpus-wide, cumulative) predicts the writer's mean with
  ``round(float(np.mean(vals)), 4)`` (PI ruling D).
* **Width tripwire** — on the widest buffer row carrying intervals in both
  vintages: a ratio below 0.8 or above 8, or a replay interval that collapses
  to zero/absent width where the committed one existed, is a failure. Cells
  with no committed interval anywhere are recorded ``no_ci``, never silently
  "ok".
* **Systematic-failure abort** — more than 5 failures stops submission; every
  already-dispatched worker is drained and RECORDED before the report is
  written (audit M2), and a worker exception becomes a failure row rather
  than destroying the record (audit M1).
* **Running-median guard** — once 200 ratio samples exist, a running median
  outside [1.05, 6] aborts (audit M4); the band is also checked at completion
  on full runs (pilots are too small and too skewed for a median claim).
* **Skip-list freeze** — the census must find exactly the expected number of
  no-recipe cells (default 13, named in the report); a different count means
  this checkout resolves different inputs (for instance sapphire retaining
  untracked leftovers) and the run refuses to start (audit M7).
* Pilots are a SEEDED RANDOM SAMPLE of the worklist (audit B2), optionally
  with forced includes for known-interesting cells.

Usage::

    python scripts/rerun_bca_corpus.py --dry-run
    python scripts/rerun_bca_corpus.py --pilot 12 \\
        --include outputs/55maps-image-generalisation/evaluation/evaluation.json
    python scripts/rerun_bca_corpus.py --workers 10

$0 API. Run on sapphire (contract § 3.4). Created 2026-08-20 (Session 138);
revised same day per the pre-launch audit adjudication.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_bca_migration_queue import (  # noqa: E402
    buffers_that_ran,
    recover_recipe,
)
from scripts.rerun_evals_at_10k import (  # noqa: E402
    TARGET_B,
    TOLERANCE,
    point_table,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPORT_PATH = PROJECT_ROOT / "results/e82-corpus-reemission-2026-08-20.json"
SELECT_VINTAGES = ("1.1", "1.2")
DONE_VINTAGE = "1.3"
MAX_FAILURES = 5
WIDTH_RATIO_BAND = (0.8, 8.0)
MEDIAN_BAND = (1.05, 6.0)
MEDIAN_GUARD_MIN_SAMPLES = 200
EXPECTED_SKIPS = 13
PILOT_SEED = 20260820
TILE_METRICS = ("mcc", "sensitivity", "specificity")
# Copy order is deliberate: the JSON carries the 1.3 vintage stamp that marks
# a cell complete, so it lands LAST — a kill mid-cell leaves the cell still
# selected on resume (audit m1). Each sibling is staged in the destination
# directory and os.replace()d, so no committed file is ever truncated.
SIBLINGS = ("evaluation.csv", "evaluation.md", "evaluation.json")


def select_targets(
    tracked: list[str],
) -> tuple[list[str], dict[str, int], list[str]]:
    """Partition tracked evaluations into worklist, census, and named skips."""
    worklist: list[str] = []
    skips: list[str] = []
    census: dict[str, int] = {"selected": 0, "done_1.3": 0, "other_vintage": 0,
                              "unparseable": 0, "no_recipe": 0}
    for rel in tracked:
        # Canonical basenames only: a dozen tracked files merely END in
        # "evaluation.json" ("phase2a-evaluation.json"); replaying one would
        # write a NEW evaluation.json beside it and never mark the source
        # done (audit m6). None is currently selectable; the filter makes
        # that a property of the code rather than of today's data.
        if rel.startswith("archive/") or Path(rel).name != "evaluation.json":
            continue
        try:
            doc = json.loads((PROJECT_ROOT / rel).read_text())
        except (json.JSONDecodeError, OSError):
            census["unparseable"] += 1
            continue
        ver = str((doc.get("_metadata") or {}).get("metadata_version", ""))
        if ver == DONE_VINTAGE:
            census["done_1.3"] += 1
            continue
        if ver not in SELECT_VINTAGES:
            census["other_vintage"] += 1
            continue
        if not _recipe_paths_exist(recover_recipe(doc)):
            census["no_recipe"] += 1
            skips.append(rel)
            continue
        census["selected"] += 1
        worklist.append(rel)
    return worklist, census, skips


def _recipe_paths_exist(recipe: dict[str, Any]) -> bool:
    """True when every input the recipe names exists on disk."""
    det = recipe.get("detections") or recipe.get("detections_dir")
    gt, bounds = recipe.get("ground_truth"), recipe.get("bounds")
    if not (det and gt and bounds):
        return False
    dets = det if isinstance(det, list) else [det]
    return (all((PROJECT_ROOT / d).exists() for d in dets)
            and (PROJECT_ROOT / str(gt)).exists()
            and (PROJECT_ROOT / str(bounds)).exists())


def _recipe_input_paths(recipe: dict[str, Any]) -> list[str]:
    """Every repo-relative input path a recipe names (dirs included)."""
    det = recipe.get("detections")
    paths = list(det) if isinstance(det, list) else ([det] if det else [])
    if recipe.get("detections_dir"):
        paths.append(recipe["detections_dir"])
    paths += [recipe["ground_truth"], recipe["bounds"]]
    return [str(p) for p in paths]


def adjacent_commits(path: str, as_of: str) -> list[str]:
    """The committed vintages an eval at ``as_of`` could have consumed.

    Returns up to two commits: the last at or before the timestamp, and the
    first after it. The second exists because evaluations are sometimes
    scored against a working tree committed minutes later — the pilot's two
    55-map image cells consumed a detections state committed 2 minutes
    after their own ``generated_at_utc`` ("propagate +1 candidate").
    """
    out: list[str] = []
    before = subprocess.run(
        ["git", "rev-list", "-1", f"--before={as_of}", "HEAD", "--", path],
        capture_output=True, text=True, cwd=PROJECT_ROOT).stdout.strip()
    if before:
        out.append(before)
    after = subprocess.run(
        ["git", "rev-list", f"--after={as_of}", "--reverse", "HEAD",
         "--", path],
        capture_output=True, text=True, cwd=PROJECT_ROOT).stdout.split()
    if after:
        out.append(after[0])
    return out


def vintage_assignments(
    recipe: dict[str, Any], as_of: str, cap: int = 6,
) -> list[dict[str, str]]:
    """Ordered per-input commit assignments to try, all-before first.

    Single-input flips to the after-vintage follow the all-before baseline;
    the all-after combination comes last. Bounded at ``cap`` assignments.
    """
    paths = _recipe_input_paths(recipe)
    cands = {p: adjacent_commits(p, as_of) for p in paths}
    if any(not c for c in cands.values()):
        return []
    base = {p: c[0] for p, c in cands.items()}
    flippable = [p for p, c in cands.items() if len(c) > 1]
    assignments = [dict(base)]
    for p in flippable:
        flipped = dict(base)
        flipped[p] = cands[p][1]
        assignments.append(flipped)
    if len(flippable) > 1:
        assignments.append({p: cands[p][-1] for p in paths})
    return assignments[:cap]


def freeze_inputs(
    recipe: dict[str, Any], assignment: dict[str, str], workdir: Path,
) -> tuple[dict[str, Any], dict[str, str]] | None:
    """Materialise the recipe's inputs at the assigned commits.

    Returns the rewritten recipe (paths under ``workdir``) plus a map of
    repo path → short commit, or ``None`` when materialisation fails.
    """
    frozen: dict[str, str] = {}
    out = dict(recipe)

    def commit_for(path: str) -> str | None:
        return assignment.get(str(path))

    def materialise(sha: str, path: str) -> Path | None:
        dest = workdir / "frozen" / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        blob = subprocess.run(["git", "show", f"{sha}:{path}"],
                              capture_output=True, cwd=PROJECT_ROOT)
        if blob.returncode != 0:
            return None
        dest.write_bytes(blob.stdout)
        return dest

    for key in ("ground_truth", "bounds"):
        sha = commit_for(str(recipe[key]))
        if sha is None:
            return None
        dest = materialise(sha, str(recipe[key]))
        if dest is None:
            return None
        frozen[str(recipe[key])] = sha[:9]
        out[key] = str(dest)

    if recipe.get("detections"):
        det = recipe["detections"]
        det_list = det if isinstance(det, list) else [det]
        new_list = []
        for p in det_list:
            sha = commit_for(str(p))
            if sha is None:
                return None
            dest = materialise(sha, str(p))
            if dest is None:
                return None
            frozen[str(p)] = sha[:9]
            new_list.append(str(dest))
        out["detections"] = new_list
    elif recipe.get("detections_dir"):
        d = str(recipe["detections_dir"])
        sha = commit_for(d)
        if sha is None:
            return None
        listing = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", sha, "--", d],
            capture_output=True, text=True, cwd=PROJECT_ROOT)
        files = [f for f in listing.stdout.split() if f]
        if not files:
            return None
        for f in files:
            if materialise(sha, f) is None:
                return None
        frozen[d] = sha[:9]
        out["detections_dir"] = str(workdir / "frozen" / d)
    return out, frozen


def build_command(doc: dict, recipe: dict[str, Any], workdir: Path) -> list[str]:
    """Assemble the replay invocation from measurements, not declarations."""
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts/evaluate_detections.py")]
    original_cli = (doc.get("_metadata") or {}).get("cli_args") or {}
    recovered = not (original_cli.get("detections")
                     or original_cli.get("detections_dir"))
    if recipe.get("detections"):
        det = recipe["detections"]
        cmd += ["--detections"] + (det if isinstance(det, list) else [det])
    else:
        cmd += ["--detections-dir", str(recipe["detections_dir"])]
        # A batch-vintage glob names only one filename convention and
        # under-reads mixed pools (D6); recovered rows use the canonical
        # resolver instead. A directly recorded glob is replayed verbatim.
        if recipe.get("glob") and not recovered:
            cmd += ["--glob", recipe["glob"]]
    cmd += ["--ground-truth", str(recipe["ground_truth"]),
            "--bounds", str(recipe["bounds"]),
            "--bootstrap", str(TARGET_B),
            "--seed", str(recipe.get("seed", 42)),
            "--output-dir", str(workdir / "out")]
    buffers = buffers_that_ran(doc, recipe)
    if buffers:
        cmd += ["--buffers"] + [str(b) for b in buffers]
    label = recipe.get("label") or (doc.get("summary") or {}).get("label")
    if label:
        cmd += ["--label", str(label)]
    if isinstance((doc.get("summary") or {}).get("tile_classification"), dict):
        cmd += ["--mcc"]
    return cmd


def tile_point_table(doc: dict) -> dict[str, Any]:
    """Observed tile points and confusion counts, for the extended gate."""
    tc = (doc.get("summary") or {}).get("tile_classification") or {}
    out: dict[str, Any] = {}
    for metric in TILE_METRICS:
        block = tc.get(metric)
        if isinstance(block, dict) and block.get("point") is not None:
            out[metric] = block["point"]
        elif isinstance(block, (int, float)):
            out[metric] = block
    conf = tc.get("confusion")
    if isinstance(conf, dict):
        out["confusion"] = {k: conf.get(k) for k in ("tp", "tn", "fp", "fn")}
    return out


def per_run_tile_points(doc: dict) -> list[dict[str, Any]]:
    """Each run's observed tile points — the actual measurements."""
    out = []
    for run in doc.get("per_run") or []:
        tc = (run or {}).get("tile_classification") or {}
        row = {}
        for metric in TILE_METRICS:
            block = tc.get(metric)
            if isinstance(block, dict) and block.get("point") is not None:
                row[metric] = block["point"]
            elif isinstance(block, (int, float)):
                row[metric] = block
        out.append(row)
    return out


def per_run_labels(doc: dict) -> list[Any]:
    """Each run's ``label`` (the source filename stem), in document order."""
    return [(run or {}).get("label") for run in doc.get("per_run") or []]


def _reaggregated_mean(doc: dict, metric: str) -> float | None:
    """The defined-pass mean of a document's per-run points (E81).

    Mirrors the writer's aggregation EXACTLY —
    ``aggregate_tile_classification`` in ``scripts/evaluate_detections.py``
    uses ``round(float(np.mean(vals)), 4)`` — because ``np.mean`` (pairwise
    summation) and a naive ``sum()/len()`` can land on opposite sides of a
    4 dp half-boundary (PI ruling D, 2026-08-22; two cells corpus-wide,
    enumerated in ``reports/e82-d41-widening-inspection-2026-08-22.md``
    § 1.5). The mean is order-sensitive at such a boundary, so callers pass
    the document whose aggregation they are predicting.
    """
    vals = [r[metric] for r in per_run_tile_points(doc) if metric in r]
    return round(float(np.mean(vals)), 4) if vals else None


def _per_run_buffer_table(doc: dict) -> list[dict[tuple, Any]]:
    """Each run's buffer-level f1/precision/recall, keyed ``(buffer, metric)``."""
    out = []
    for run in doc.get("per_run") or []:
        row: dict[tuple, Any] = {}
        for entry in (run or {}).get("buffers") or []:
            for metric in ("f1", "precision", "recall"):
                if metric in entry:
                    row[(entry.get("buffer_metres"), metric)] = entry[metric]
        out.append(row)
    return out


def _buffer_mean(doc: dict, key: tuple) -> float | None:
    """The writer's summary buffer aggregation over a document's run order.

    ``evaluate_multi_run_mean`` computes each summary buffer metric as
    ``round(float(np.mean(values)), 4)`` over the per-run values in
    consumption order — the same order-sensitive expression as the tile
    aggregation, and equally capable of flipping a 4 dp half-boundary when
    the replay consumes an order-permuted pool.
    """
    vals = [r[key] for r in _per_run_buffer_table(doc) if key in r]
    return round(float(np.mean(vals)), 4) if vals else None


def gate(
    before: dict, after: dict,
) -> tuple[dict[str, Any] | None, dict[str, Any], dict[str, Any]]:
    """Point-identity gate, anchored to the per-run measurements.

    Returns ``(failure_diagnostics_or_None, reaggregations,
    order_normalisations)``.

    Per-run tile points are compared by run LABEL when labels are present
    and unique on both sides, falling back to list index otherwise (PI
    ruling C1, 2026-08-22): the original batch glob consumed passes in
    lexicographic order while the canonical resolver replays them
    numerically, so at >= 10 runs the ``per_run`` blocks are permuted even
    though every measurement is identical. Label-keying compares each
    measurement to ITSELF rather than to whichever pass sits at the same
    index; a changed pool still fails as a label-set mismatch, and a
    genuinely moved measurement still fails on its own label. Cells that
    needed the normalisation are recorded, never silently passed.

    A summary tile point that moves is tolerated ONLY when every per-run
    tile point reproduces exactly AND the replayed summary equals the
    writer's aggregation of the replayed run order (``_reaggregated_mean``,
    mirroring ``aggregate_tile_classification``). Two forgivable cases,
    recorded separately:

    * **D41 re-aggregation** — the committed summary was NOT the mean of
      its own per-run points: 19 multi-run ``paper-eval/mcc`` cells
      committed run 1's point as the cell summary (a superseded
      aggregation; PI-accepted correction 2026-08-20).
    * **Order artefact** — committed and replayed summaries are BOTH
      correct writer aggregations of identical measurements, differing
      only through ``np.mean``'s pairwise summation order at a 4 dp
      rounding boundary. Reachable only on an order-permuted pool; filed
      under order_normalisations, not D41, so the contract's
      ``n_reaggregated = 19`` census stays exact.

    The same order-artefact forgiveness applies to the summary BUFFER
    table: ``evaluate_multi_run_mean`` aggregates each buffer's
    f1/precision/recall with the identical order-sensitive expression, so
    an order-permuted pool can flip a summary buffer value by one 4 dp
    step (observed live on 2026-08-22: four of the six order-permuted
    cells carry such boundaries — eight shifted values corpus-wide, fully
    enumerated). A moved buffer point is forgiven ONLY when the pool is
    order-permuted, every labelled per-run buffer measurement reproduces
    exactly, and both committed and replayed values equal the writer's
    aggregation over their own run order.

    Anything else fails.
    """
    run_b, run_a = per_run_tile_points(before), per_run_tile_points(after)
    lab_b, lab_a = per_run_labels(before), per_run_labels(after)
    runs_moved: dict[str, Any] = {}
    order_normalised: dict[str, Any] = {}
    label_keyed = (
        len(run_b) == len(run_a)
        and all(isinstance(lab, str) and lab for lab in lab_b + lab_a)
        and len(set(lab_b)) == len(lab_b)
        and len(set(lab_a)) == len(lab_a)
    )
    if len(run_b) != len(run_a):
        runs_moved["n_runs"] = (len(run_b), len(run_a))
    elif label_keyed and set(lab_b) != set(lab_a):
        # A differing label set means a different pool was scored — a real
        # failure, reported as such rather than as index-wise value noise.
        runs_moved["labels"] = (sorted(set(lab_b) - set(lab_a)),
                                sorted(set(lab_a) - set(lab_b)))
    elif label_keyed:
        by_label = dict(zip(lab_a, run_a))
        for label, rb in zip(lab_b, run_b):
            ra = by_label[label]
            for metric, v in rb.items():
                if ra.get(metric) != v:
                    runs_moved[f"{label}/{metric}"] = (v, ra.get(metric))
        if not runs_moved and lab_b != lab_a:
            order_normalised["per_run_labels"] = {
                "committed": lab_b, "replayed": lab_a}
    else:
        for i, (rb, ra) in enumerate(zip(run_b, run_a)):
            for metric, v in rb.items():
                if ra.get(metric) != v:
                    runs_moved[f"run{i}/{metric}"] = (v, ra.get(metric))

    pb, pa = point_table(before), point_table(after)
    moved_keys = {k: (pb[k], pa[k]) for k in pb
                  if k in pa and abs(pb[k] - pa[k]) > TOLERANCE}
    missing = sorted(f"{k[0]}m/{k[1]}" for k in set(pb) - set(pa))
    if (moved_keys and not runs_moved
            and order_normalised.get("per_run_labels")):
        # Buffer-mean order artefacts are forgivable only when every
        # labelled per-run buffer measurement reproduces exactly.
        by_label_a = dict(zip(lab_a, _per_run_buffer_table(after)))
        buffers_reproduce = all(
            by_label_a.get(lab) == rb
            for lab, rb in zip(lab_b, _per_run_buffer_table(before)))
        if buffers_reproduce:
            for k in list(moved_keys):
                if (pb[k] == _buffer_mean(before, k)
                        and pa[k] == _buffer_mean(after, k)):
                    order_normalised.setdefault("summary_buffer_points", {})[
                        f"{k[0]}m/{k[1]}"] = list(moved_keys.pop(k))
    moved = {f"{k[0]}m/{k[1]}": v for k, v in moved_keys.items()}

    tb, ta = tile_point_table(before), tile_point_table(after)
    tile_moved = {k: (tb[k], ta.get(k)) for k in tb if tb[k] != ta.get(k)}
    reaggregated: dict[str, Any] = {}
    if tile_moved and not runs_moved:
        for metric in list(tile_moved):
            if metric == "confusion":
                continue
            if ta.get(metric) != _reaggregated_mean(after, metric):
                continue  # not the writer's aggregate of the reproduced runs
            if (order_normalised.get("per_run_labels")
                    and tb[metric] == _reaggregated_mean(before, metric)):
                order_normalised.setdefault("summary_tile_point", {})[
                    metric] = list(tile_moved.pop(metric))
            else:
                reaggregated[metric] = list(tile_moved.pop(metric))

    if moved or missing or tile_moved or runs_moved:
        return ({"moved": {**moved, **tile_moved, **runs_moved},
                 "missing": missing}, {}, {})
    return None, reaggregated, order_normalised


def width_check(before: dict, after: dict) -> tuple[float | None, str | None]:
    """Width ratio on the widest common-interval buffer, plus a verdict.

    Returns ``(ratio, failure_reason)``; ratio ``None`` with no failure means
    the committed cell carries no interval anywhere (recorded ``no_ci``).
    """
    def widths(doc: dict) -> dict[int, float]:
        out = {}
        for b in (doc.get("summary") or {}).get("buffers", []):
            lo, hi = b.get("f1_ci_lower"), b.get("f1_ci_upper")
            if lo is not None and hi is not None:
                out[b["buffer_metres"]] = hi - lo
        return out

    wb, wa = widths(before), widths(after)
    if not wb:
        return None, None
    # The widest committed interval is the most informative comparator and
    # exists for every family, 20 m boards and 30 m-only boards alike
    # (audit M3: 91 cells have no 20 m row).
    buf = max(wb, key=lambda k: wb[k])
    if wb[buf] == 0:
        # Degenerate committed interval; nothing to ratio against. Recorded,
        # not silently passed.
        return None, None
    if buf not in wa or wa[buf] == 0:
        return None, (f"replay interval at {buf} m collapsed or vanished "
                      f"(committed width {wb[buf]:.4f})")
    ratio = wa[buf] / wb[buf]
    if not (WIDTH_RATIO_BAND[0] <= ratio <= WIDTH_RATIO_BAND[1]):
        return ratio, (f"width ratio {ratio:.3f} at {buf} m outside "
                       f"{WIDTH_RATIO_BAND}")
    return ratio, None


def _accept(work_out: Path, path: Path, recipe: dict[str, Any],
            frozen: dict[str, str] | None) -> None:
    """Stage-and-replace the siblings atomically, JSON (vintage stamp) last."""
    if frozen:
        doc = json.loads((work_out / "evaluation.json").read_text())
        cli = doc["_metadata"].get("cli_args") or {}
        # A frozen replay ran against temp materialisations; the committed
        # artefact must record the repo-relative inputs it logically scored,
        # with the vintage pinned separately (audit B1 / provenance).
        for key in ("ground_truth", "bounds", "detections", "detections_dir"):
            if recipe.get(key) is not None and key in cli:
                cli[key] = recipe[key]
        doc["_metadata"]["e82_input_vintage"] = frozen
        (work_out / "evaluation.json").write_text(
            json.dumps(doc, indent=2) + "\n")
    for name in SIBLINGS:
        src = work_out / name
        if not src.exists():
            continue
        staged = path.parent / f".{name}.e82tmp"
        shutil.copy2(src, staged)
        os.replace(staged, path.parent / name)


def process_one(rel: str) -> dict[str, Any]:
    """Replay one evaluation (current inputs, then frozen) and gate it."""
    path = PROJECT_ROOT / rel
    try:
        before = json.loads(path.read_text())
        recipe = recover_recipe(before)
        original_recipe = dict(recipe)
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            attempts: list[dict[str, Any]] = []
            as_of = (before.get("_metadata") or {}).get("generated_at_utc")
            plan: list[tuple[str, dict[str, str] | None]] = [("current", None)]
            if as_of:
                for i, asg in enumerate(
                        vintage_assignments(original_recipe, as_of)):
                    name = "frozen" if i == 0 else f"vintage-search-{i}"
                    plan.append((name, asg))
            for attempt, assignment in plan:
                frozen_map: dict[str, str] | None = None
                if assignment is not None:
                    shutil.rmtree(work / "out", ignore_errors=True)
                    shutil.rmtree(work / "frozen", ignore_errors=True)
                    frozen_result = freeze_inputs(
                        original_recipe, assignment, work)
                    if frozen_result is None:
                        attempts.append({"attempt": attempt,
                                         "reason": "vintage materialisation "
                                                   "failed"})
                        continue
                    recipe, frozen_map = frozen_result
                cmd = build_command(before, recipe, work)
                try:
                    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT,
                                   capture_output=True, text=True)
                except subprocess.CalledProcessError as exc:
                    attempts.append({"attempt": attempt,
                                     "reason": "replay error",
                                     "detail": (exc.stderr or "")[-400:]})
                    continue
                after = json.loads((work / "out/evaluation.json").read_text())
                diag, reaggregated, order_norm = gate(before, after)
                if diag is not None:
                    attempts.append({"attempt": attempt,
                                     "reason": "point estimates moved",
                                     **diag})
                    continue
                ratio, width_fail = width_check(before, after)
                if width_fail:
                    attempts.append({"attempt": attempt,
                                     "reason": width_fail,
                                     "width_ratio": ratio})
                    continue
                _accept(work / "out", path, original_recipe, frozen_map)
                return {"evaluation": rel, "status": "ok",
                        "attempt": attempt,
                        "input_vintage": frozen_map,
                        **({"summary_tile_point_reaggregated": reaggregated}
                           if reaggregated else {}),
                        **({"per_run_order_normalised": order_norm}
                           if order_norm else {}),
                        "bootstrap_before":
                            (before["_metadata"].get("bootstrap") or {})
                            .get("n_iterations"),
                        "bootstrap_after": TARGET_B,
                        "width_ratio": ratio,
                        "no_ci": ratio is None}
        # The FIRST attempt's reason is the substantive diagnosis (a gate or
        # width failure on current inputs); later entries usually explain why
        # the frozen fallback was unavailable.
        return {"evaluation": rel, "status": "failed",
                "reason": attempts[0]["reason"] if attempts else "unknown",
                "attempts": attempts}
    except Exception as exc:  # noqa: BLE001 — a worker must never lose the row
        return {"evaluation": rel, "status": "failed",
                "reason": f"worker exception: {type(exc).__name__}: {exc}"}


def running_median(ratios: list[float]) -> float | None:
    """Median of the collected ratios, once enough samples exist."""
    if len(ratios) < MEDIAN_GUARD_MIN_SAMPLES:
        return None
    s = sorted(ratios)
    return s[len(s) // 2]


def main() -> int:
    """Census, pilot, or full corpus run with the contract's tripwires."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", type=int, default=None,
                    help="Seeded RANDOM sample of N files (>= 1).")
    ap.add_argument("--include", action="append", default=[],
                    help="Force-include a file (repo-relative); repeatable.")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--expect-skips", type=int, default=EXPECTED_SKIPS,
                    help="Refuse to run unless the no-recipe census matches.")
    ap.add_argument("--report-out", type=Path, default=REPORT_PATH)
    args = ap.parse_args()
    if args.pilot is not None and args.pilot < 1:
        ap.error("--pilot must be >= 1")

    tracked = subprocess.run(["git", "ls-files", "*evaluation.json"],
                             capture_output=True, text=True, check=True,
                             cwd=PROJECT_ROOT).stdout.split()
    worklist, census, skips = select_targets(tracked)
    logger.info("census: %s", census)
    if census["no_recipe"] != args.expect_skips:
        logger.error(
            "no-recipe census %d != expected %d — this checkout resolves "
            "different inputs than the contract froze (contract § 4); "
            "refusing to run", census["no_recipe"], args.expect_skips)
        return 3
    if args.dry_run:
        for s in skips:
            logger.info("skip (no recipe): %s", s)
        return 0

    if args.pilot:
        rng = random.Random(PILOT_SEED)
        sample = rng.sample(sorted(worklist), min(args.pilot, len(worklist)))
        forced = [p for p in args.include if p in worklist]
        worklist = sorted(set(sample) | set(forced))
    logger.info("processing %d file(s) with %d worker(s)",
                len(worklist), args.workers)

    rows: list[dict[str, Any]] = []
    ratios: list[float] = []
    failures = 0
    aborted = abort_reason = None
    queue = list(worklist)
    try:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            pending: set = set()
            while queue or pending:
                while queue and len(pending) < args.workers * 2 and not aborted:
                    pending.add(pool.submit(process_one, queue.pop(0)))
                if not pending:
                    break
                done, pending = wait(pending, return_when=FIRST_COMPLETED)
                for fut in done:
                    try:
                        row = fut.result()
                    except Exception as exc:  # noqa: BLE001
                        row = {"evaluation": "unknown", "status": "failed",
                               "reason": f"future error: {exc}"}
                    rows.append(row)
                    if row["status"] == "failed":
                        failures += 1
                        logger.error("[%d] FAILED %s: %s", len(rows),
                                     row["evaluation"], row["reason"])
                        if failures > MAX_FAILURES and not aborted:
                            aborted = True
                            abort_reason = (f"> {MAX_FAILURES} failures "
                                            "(contract § 3.1)")
                            queue.clear()
                    else:
                        if row.get("width_ratio"):
                            ratios.append(row["width_ratio"])
                        if len(rows) % 25 == 0:
                            logger.info("[%d/%d] ok", len(rows),
                                        len(worklist))
                        med = running_median(ratios)
                        if (med is not None and not aborted
                                and not (MEDIAN_BAND[0] <= med
                                         <= MEDIAN_BAND[1])):
                            aborted = True
                            abort_reason = (f"running median {med:.3f} "
                                            f"outside {MEDIAN_BAND} "
                                            "(contract § 3.2)")
                            queue.clear()
            # The executor context drains dispatched workers; every drained
            # row is recorded above before the report writes (audit M2).
    finally:
        ok = [r for r in rows if r["status"] == "ok"]
        srt = sorted(ratios)
        median = srt[len(srt) // 2] if srt else None
        existing = (json.loads(args.report_out.read_text())
                    if args.report_out.exists() else {"runs": []})
        existing.setdefault(
            "contract", "planning/e82-corpus-reemission-2026-08-20.md")
        existing["census"] = census
        existing["skips_no_recipe"] = skips
        existing["runs"].append({
            "pilot": args.pilot, "workers": args.workers,
            "aborted": bool(aborted), "abort_reason": abort_reason,
            "n_ok": len(ok), "n_failed": failures,
            "n_pinned_vintage": sum(1 for r in ok
                                    if r.get("attempt") != "current"),
            "n_reaggregated": sum(
                1 for r in ok if r.get("summary_tile_point_reaggregated")),
            "n_order_normalised": sum(
                1 for r in ok if r.get("per_run_order_normalised")),
            "n_no_ci": sum(1 for r in ok if r.get("no_ci")),
            "width_ratio_median": median, "rows": rows,
        })
        args.report_out.write_text(json.dumps(existing, indent=2) + "\n")
        logger.info("ok %d / failed %d / pinned-vintage %d; report -> %s",
                    len(ok), failures,
                    sum(1 for r in ok if r.get("attempt") != "current"),
                    args.report_out)

    if aborted:
        logger.error("ABORTED: %s", abort_reason)
        return 1
    if (args.pilot is None and median is not None
            and not (MEDIAN_BAND[0] <= median <= MEDIAN_BAND[1])):
        logger.error("median width ratio %.3f outside %s (contract § 3.2)",
                     median, MEDIAN_BAND)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
