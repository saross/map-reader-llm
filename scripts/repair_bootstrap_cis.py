#!/usr/bin/env python3
"""Repair the dead source paths in the bootstrap CI store and re-run stale entries.

Why
---
``results/all-bootstrap-cis.json`` (and its byte-identical duplicate
``results/pv/all-bootstrap-cis.json``) holds 496 bootstrap confidence-interval
(CI) entries. Two defects, both established by
``reports/name-keyed-cache-audit-2026-09-12.md`` § 4 Finding 1 and reproduced by
``scripts/check_bootstrap_cis.py``:

1. **Every** ``source_file`` names a ``data/**`` tree that has never existed in
   this repository. 456 entries remap to ``outputs/retest/**`` and 16 to
   ``archive/outputs-experimental-pilot/pv/consensus-proposers/**``; the
   remaining 24 are ``consensus:<label>`` pseudo-paths, not paths at all.
2. **85 of the 472 resolvable entries** were computed from a pass file that the
   March 2026 E70 tile-recovery campaign
   (``docs/methodology/preregistration/protocol-errata.md:3154-3199``) later
   grew in place. Their CIs are pre-recovery numbers serving under a
   post-recovery file's name.

The Principal Investigator's ruling (2026-09-12) is that the store be made
*wholly current* rather than annotated as partly uncitable: re-run the stale
entries on their present source files, preserving the superseded values so the
history is not lost.

Method fidelity — the point that matters
----------------------------------------
The 387 entries that already match must not be touched, so the re-run must use
the **same estimator they were computed with**. That is *not* today's
``lib_advanced_metrics.bootstrap_ci``: on 2026-04-29 that function moved from
the percentile method to Bias-Corrected and Accelerated (BCa) intervals. The
committed store is percentile-era (``results/ci-metadata-registry.md`` records
"bootstrap percentile"), so :func:`bootstrap_ci_percentile` below vendors the
March-2026 implementation verbatim (``git show 2de117096:scripts/
lib_advanced_metrics.py``, ``bootstrap_ci`` at lines 554-632): 1,000 tile-level
resamples with replacement, mean of the resample distribution as the point
value, and the 2.5th / 97.5th percentiles as the bounds.

The per-tile true/false positive machinery is *imported* from the current
library rather than vendored, because its only change since March is the
addition of ``source_map`` column auto-detection — inert for
``mounds-reference.geojson``, which carries ``Map``. The ``gate`` subcommand
exists to prove that claim empirically before anything is written.

Parameters, all taken from the store and the registry (not guessed):
``n_iterations`` 1000 and ``random_seed`` 42 (``_metadata`` of the store),
tile-level resampling unit and 20 m matching buffer (library defaults, recorded
in ``results/ci-metadata-registry.md:97``), reference
``inputs/vectors/references/mounds-reference.geojson`` (569 points) and bounds
``inputs/vectors/bounds/full_evaluation_bounds.geojson`` (340 tiles — the
four-map retest corpus, not the 487-tile 384 px frame).

Subcommands
-----------
``repair-paths``
    Rewrite every resolvable ``source_file`` to the path that exists today,
    preserving the original string in ``source_file_original``, marking the
    unresolvable entries ``"source_status": "unresolved"``, and recording a
    top-level ``_path_repair`` note. Idempotent.

``gate``
    Recompute N entries that already MATCH their source and compare against the
    committed values. This is the go / no-go test for the re-run: if the
    committed numbers do not reproduce, the estimator has not been identified
    and nothing should be rewritten.

``rerun``
    Recompute the mismatching entries on their present source files, write the
    new ``f1`` / ``precision`` / ``recall`` and ``n_detections`` in place, and
    move the superseded values into a ``pre_e70`` sub-object
    (``{n_detections, f1_mean, ci_low, ci_high, computed_at}``).

Usage
-----
Repair the paths in both stores (writes; archive the originals first)::

    python scripts/repair_bootstrap_cis.py repair-paths \\
        results/all-bootstrap-cis.json results/pv/all-bootstrap-cis.json

The gate — five already-matching entries, on sapphire::

    python scripts/repair_bootstrap_cis.py gate --n 5 --workers 5 \\
        results/all-bootstrap-cis.json

The re-run, once the gate has passed::

    python scripts/repair_bootstrap_cis.py rerun --workers 16 \\
        results/all-bootstrap-cis.json

Compute location: the bootstrap is CPU-bound (~10 s per entry per core), so
both ``gate`` and ``rerun`` must run on sapphire per the project's compute-
location rule. No Application Programming Interface (API) call is made.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import geopandas as gpd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_bootstrap_cis import (  # noqa: E402
    REMAPS,
    STATUS_MISMATCH,
    check_entries,
    count_geojson_features,
)
from lib_advanced_metrics import (  # noqa: E402
    aggregate_tile_metrics,
    compute_per_tile_tp_fp_fn,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Evaluation frame. Anchors for each value are given in the module docstring.
DEFAULT_REFERENCE = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
DEFAULT_BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/full_evaluation_bounds.geojson"
TARGET_CRS = "EPSG:32635"
DEFAULT_BUFFER_METRES = 20
DEFAULT_ITERATIONS = 1000
DEFAULT_SEED = 42

# The audit report whose Finding 1 this script repairs, and its commit.
AUDIT_REPORT = "reports/name-keyed-cache-audit-2026-09-12.md"
AUDIT_COMMIT = "2fabf4e1d"

# Tolerance for the gate: the store records full float64 repr, so a faithful
# reproduction should agree to far better than this.
GATE_TOLERANCE = 1e-9


def bootstrap_ci_percentile(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_iterations: int = DEFAULT_ITERATIONS,
    random_seed: int | None = DEFAULT_SEED,
    buffer_metres: int = DEFAULT_BUFFER_METRES,
) -> dict[str, Any]:
    """Percentile-method tile-level bootstrap, pinned to the March 2026 estimator.

    Vendored verbatim from ``git show 2de117096:scripts/lib_advanced_metrics.py``
    (``bootstrap_ci``, lines 554-632) because the library function of that name
    was replaced by a BCa implementation on 2026-04-29 and would no longer
    reproduce the committed store. Resampling unit is the tile (Decision 10,
    ``docs/methodology/preregistration/decisions-log.md:337``); per-tile
    TP/FP/FN are computed once and resampled, which is the errata E26 fix.

    Args:
        gdf_det: Detections.
        gdf_ref: Ground-truth reference points.
        gdf_bounds: Tile boundaries; ``tile_name`` defines the resampling units.
        n_iterations: Bootstrap resamples (default 1000).
        random_seed: Seed for ``numpy.random.default_rng`` (default 42).
        buffer_metres: Spatial matching tolerance in metres (default 20).

    Returns:
        ``{"f1": {...}, "precision": {...}, "recall": {...},
        "n_iterations": int}`` where each metric block carries ``mean``,
        ``ci_lower`` and ``ci_upper``. Empty dict when the bounds hold no tiles.
    """
    tiles = gdf_bounds["tile_name"].unique()
    n_tiles = len(tiles)
    if n_tiles == 0:
        return {}

    rng = np.random.default_rng(random_seed)
    tile_metrics = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )

    precision_scores: list[float] = []
    recall_scores: list[float] = []
    f1_scores: list[float] = []
    for _i in range(n_iterations):
        sample_tiles = rng.choice(tiles, n_tiles, replace=True)
        precision, recall, f1 = aggregate_tile_metrics(tile_metrics, sample_tiles)
        precision_scores.append(precision)
        recall_scores.append(recall)
        f1_scores.append(f1)

    def _block(scores: list[float]) -> dict[str, float]:
        """Reduce a resample distribution to the stored three-field block."""
        return {
            "mean": float(np.mean(scores)),
            "ci_lower": float(np.percentile(scores, 2.5)),
            "ci_upper": float(np.percentile(scores, 97.5)),
        }

    return {
        "f1": _block(f1_scores),
        "precision": _block(precision_scores),
        "recall": _block(recall_scores),
        "n_iterations": n_iterations,
    }


def load_frame(
    reference: Path = DEFAULT_REFERENCE,
    bounds: Path = DEFAULT_BOUNDS,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Load the reference and bounds layers, reprojected to the metric CRS.

    Args:
        reference: Ground-truth reference GeoJSON.
        bounds: Tile-bounds GeoJSON defining the evaluation frame.

    Returns:
        A ``(gdf_ref, gdf_bounds)`` pair, both in :data:`TARGET_CRS`.
    """
    gdf_ref = gpd.read_file(reference)
    gdf_bounds = gpd.read_file(bounds)
    if gdf_ref.crs is not None and gdf_ref.crs.to_string() != TARGET_CRS:
        gdf_ref = gdf_ref.to_crs(TARGET_CRS)
    if gdf_bounds.crs is not None and gdf_bounds.crs.to_string() != TARGET_CRS:
        gdf_bounds = gdf_bounds.to_crs(TARGET_CRS)
    return gdf_ref, gdf_bounds


def recompute_entry(job: tuple[str, str, int, int]) -> dict[str, Any]:
    """Recompute one entry's CIs from its source file.

    Written as a single-tuple-argument function so it can be handed straight to
    :meth:`concurrent.futures.ProcessPoolExecutor.map`. The reference and bounds
    are re-read per worker process; that costs well under a second against the
    ~10 s bootstrap, and avoids pickling GeoDataFrames.

    Args:
        job: ``(key, source_path, n_iterations, random_seed)``.

    Returns:
        ``{"key", "n_detections", "f1", "precision", "recall", "n_iterations",
        "elapsed_seconds"}``, or ``{"key", "error"}`` on failure.
    """
    key, source_path, n_iterations, random_seed = job
    started = perf_counter()
    try:
        path = Path(source_path)
        gdf_ref, gdf_bounds = load_frame()
        gdf_det = gpd.read_file(path)
        if gdf_det.crs is not None and gdf_det.crs.to_string() != TARGET_CRS:
            gdf_det = gdf_det.to_crs(TARGET_CRS)
        result = bootstrap_ci_percentile(
            gdf_det,
            gdf_ref,
            gdf_bounds,
            n_iterations=n_iterations,
            random_seed=random_seed,
        )
        return {
            "key": key,
            "n_detections": count_geojson_features(path),
            "f1": result["f1"],
            "precision": result["precision"],
            "recall": result["recall"],
            "n_iterations": result["n_iterations"],
            "elapsed_seconds": round(perf_counter() - started, 1),
        }
    except Exception as exc:  # noqa: BLE001 — one bad entry must not kill the run
        return {"key": key, "error": f"{type(exc).__name__}: {exc}"}


def run_jobs(jobs: list[tuple[str, str, int, int]], workers: int) -> list[dict[str, Any]]:
    """Execute recompute jobs, in parallel when more than one worker is asked for.

    Args:
        jobs: Job tuples for :func:`recompute_entry`.
        workers: Process count; 1 runs in-process.

    Returns:
        One result dict per job, in job order.
    """
    if workers <= 1:
        return [recompute_entry(job) for job in jobs]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(recompute_entry, jobs))


def load_store(path: Path) -> dict[str, Any]:
    """Read a CI store JSON.

    Args:
        path: Path to an ``all-bootstrap-cis.json``.

    Returns:
        The parsed object.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def write_store(path: Path, payload: dict[str, Any]) -> None:
    """Write a CI store JSON in the committed formatting.

    The committed files are ``json.dumps(..., indent=2)`` with **no** trailing
    newline; a no-op round trip is byte-identical, which was verified before the
    first write (2026-09-12). Preserving that keeps the diff to the fields that
    actually changed.

    Args:
        path: Destination path.
        payload: The object to serialise.
    """
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def remap_source(source_file: str) -> str | None:
    """Apply the documented prefix remaps and return the path if it exists.

    Args:
        source_file: A recorded ``source_file`` string.

    Returns:
        The repository-relative path that exists today, or ``None`` when the
        string is a pseudo-path or nothing resolves.
    """
    if source_file.startswith("consensus:"):
        return None
    candidate = source_file
    for prefix, replacement in REMAPS:
        if candidate.startswith(prefix):
            candidate = replacement + candidate[len(prefix):]
            break
    return candidate if (PROJECT_ROOT / candidate).exists() else None


def repair_paths(store_paths: list[Path], dry_run: bool = False) -> dict[str, int]:
    """Rewrite dead ``source_file`` paths in one or more stores.

    Args:
        store_paths: The CI stores to repair.
        dry_run: Report what would change without writing.

    Returns:
        Counts: ``repaired``, ``already_current``, ``unresolved``.
    """
    counts = {"repaired": 0, "already_current": 0, "unresolved": 0}
    for store_path in store_paths:
        payload = load_store(store_path)
        repaired = 0
        unresolved = 0
        already = 0
        for entry in payload.get("results", {}).values():
            source_file = entry.get("source_file", "")
            resolved = remap_source(source_file)
            if resolved is None:
                entry["source_status"] = "unresolved"
                unresolved += 1
                continue
            entry.pop("source_status", None)
            if resolved == source_file:
                already += 1
                continue
            # Rebuild the entry so ``source_file_original`` sits immediately
            # after ``source_file`` and every other key keeps its position.
            rebuilt: dict[str, Any] = {}
            for field, value in list(entry.items()):
                if field == "source_file":
                    rebuilt["source_file"] = resolved
                    rebuilt["source_file_original"] = source_file
                elif field != "source_file_original":
                    rebuilt[field] = value
            entry.clear()
            entry.update(rebuilt)
            repaired += 1

        # A re-run must not overwrite the original repair's provenance with
        # zeros, so the note is written once and then left alone. This keeps the
        # subcommand byte-idempotent, not merely semantically idempotent.
        if repaired or "_path_repair" not in payload:
            payload["_path_repair"] = {
                "date": "2026-09-12",
                "repaired_entries": repaired,
                "unresolved_entries": unresolved,
                "already_current": already,
                "remaps": [{"from": a, "to": b} for a, b in REMAPS],
                "note": (
                    "Every source_file as first committed named a data/** tree "
                    "that has never existed in this repository. Paths rewritten "
                    "to the files that exist today; the original string is "
                    "preserved per entry in source_file_original. Entries whose "
                    "source could not be located carry "
                    "source_status=unresolved."
                ),
                "audit_report": AUDIT_REPORT,
                "audit_report_commit": AUDIT_COMMIT,
            }
        # Keep ``_path_repair`` beside ``_metadata`` at the head of the file.
        ordered = {"_metadata": payload["_metadata"], "_path_repair": payload["_path_repair"]}
        ordered.update({k: v for k, v in payload.items() if k not in ordered})

        print(
            f"{store_path}: repaired {repaired}, already current {already}, "
            f"unresolved {unresolved}"
        )
        if not dry_run:
            write_store(store_path, ordered)
        counts["repaired"] += repaired
        counts["already_current"] += already
        counts["unresolved"] += unresolved
    return counts


def _committed_triple(entry: dict[str, Any], metric: str) -> tuple[float, float, float]:
    """Return an entry's ``(mean, ci_lower, ci_upper)`` for one metric."""
    block = entry[metric]
    return block["mean"], block["ci_lower"], block["ci_upper"]


def run_gate(
    store_path: Path,
    n: int,
    workers: int,
    iterations: int,
    seed: int,
) -> int:
    """Recompute already-matching entries and compare against the committed values.

    Args:
        store_path: The CI store to test against.
        n: How many matching entries to test.
        workers: Process count.
        iterations: Bootstrap iterations.
        seed: Bootstrap seed.

    Returns:
        0 when every tested entry reproduces within :data:`GATE_TOLERANCE`,
        1 otherwise.
    """
    payload = load_store(store_path)
    results = check_entries(payload, repo_root=PROJECT_ROOT, remap=True)
    matching = [r for r in results if r.status == "match" and r.resolved_path is not None]
    if len(matching) < n:
        print(f"Only {len(matching)} matching entries available; asked for {n}.")
        return 1
    # Deterministic selection: evenly spaced through the store's key order, so
    # the gate spans phases rather than testing five neighbours.
    step = max(1, len(matching) // n)
    chosen = matching[::step][:n]

    jobs = [(r.key, str(r.resolved_path), iterations, seed) for r in chosen]
    started = perf_counter()
    outcomes = run_jobs(jobs, workers)
    elapsed = perf_counter() - started

    print(f"Gate: {len(jobs)} already-matching entries, {iterations} iterations, seed {seed}")
    print(f"Frame: reference {DEFAULT_REFERENCE.name}, bounds {DEFAULT_BOUNDS.name}, "
          f"buffer {DEFAULT_BUFFER_METRES} m, percentile method")
    print("")
    failures = 0
    for outcome in outcomes:
        key = outcome["key"]
        entry = payload["results"][key]
        if "error" in outcome:
            print(f"  {key}: ERROR {outcome['error']}")
            failures += 1
            continue
        worst = 0.0
        detail = []
        for metric in ("f1", "precision", "recall"):
            want = _committed_triple(entry, metric)
            got = (
                outcome[metric]["mean"],
                outcome[metric]["ci_lower"],
                outcome[metric]["ci_upper"],
            )
            diffs = [abs(a - b) for a, b in zip(want, got, strict=True)]
            worst = max(worst, *diffs)
            detail.append(f"{metric} max|Δ|={max(diffs):.3e}")
        verdict = "REPRODUCES" if worst <= GATE_TOLERANCE else "DIVERGES"
        if worst > GATE_TOLERANCE:
            failures += 1
        print(f"  {key}: {verdict} ({'; '.join(detail)})")
        if worst > GATE_TOLERANCE:
            for metric in ("f1", "precision", "recall"):
                want = _committed_triple(entry, metric)
                got = (
                    outcome[metric]["mean"],
                    outcome[metric]["ci_lower"],
                    outcome[metric]["ci_upper"],
                )
                print(f"      {metric} committed {want}")
                print(f"      {metric} recomputed {got}")

    print("")
    print(f"Wall time {elapsed:.1f} s on {workers} worker(s).")
    if failures:
        print(f"GATE FAILED: {failures}/{len(jobs)} entries did not reproduce. "
              "Do not re-run the divergent entries — the estimator is not identified.")
        return 1
    print(f"GATE PASSED: {len(jobs)}/{len(jobs)} entries reproduce to "
          f"<= {GATE_TOLERANCE:g}.")
    return 0


def run_rerun(
    store_paths: list[Path],
    workers: int,
    iterations: int,
    seed: int,
    dry_run: bool = False,
) -> int:
    """Recompute every mismatching entry and write the new values in place.

    The superseded values move into a ``pre_e70`` sub-object so the pre-recovery
    numbers remain readable beside the current ones.

    Args:
        store_paths: The CI stores to update (all get the same new values).
        workers: Process count.
        iterations: Bootstrap iterations.
        seed: Bootstrap seed.
        dry_run: Compute and report without writing.

    Returns:
        0 on success, 1 if any entry errored.
    """
    primary = load_store(store_paths[0])
    results = check_entries(primary, repo_root=PROJECT_ROOT, remap=True)
    stale = [r for r in results if r.status == STATUS_MISMATCH and r.resolved_path]
    print(f"Re-running {len(stale)} mismatching entries "
          f"({iterations} iterations, seed {seed}, {workers} workers)")

    jobs = [(r.key, str(r.resolved_path), iterations, seed) for r in stale]
    started = perf_counter()
    outcomes = run_jobs(jobs, workers)
    elapsed = perf_counter() - started
    print(f"Wall time {elapsed:.1f} s on {workers} worker(s).")

    errors = [o for o in outcomes if "error" in o]
    for outcome in errors:
        print(f"  ERROR {outcome['key']}: {outcome['error']}")
    good = [o for o in outcomes if "error" not in o]

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    shifts: list[tuple[str, float, float, int, int]] = []
    for store_path in store_paths:
        payload = primary if store_path == store_paths[0] else load_store(store_path)
        for outcome in good:
            entry = payload["results"][outcome["key"]]
            if "pre_e70" not in entry:
                entry["pre_e70"] = {
                    "n_detections": entry["n_detections"],
                    "f1_mean": entry["f1"]["mean"],
                    "ci_low": entry["f1"]["ci_lower"],
                    "ci_high": entry["f1"]["ci_upper"],
                    "computed_at": "2026-03-21",
                }
            if store_path == store_paths[0]:
                shifts.append((
                    outcome["key"],
                    entry["f1"]["mean"],
                    outcome["f1"]["mean"],
                    entry["n_detections"],
                    outcome["n_detections"],
                ))
            entry["f1"] = outcome["f1"]
            entry["precision"] = outcome["precision"]
            entry["recall"] = outcome["recall"]
            entry["n_detections"] = outcome["n_detections"]
            entry["n_iterations"] = outcome["n_iterations"]
            entry["elapsed_seconds"] = outcome["elapsed_seconds"]
            entry["recomputed_at"] = timestamp
        payload.setdefault("_rerun", {})
        payload["_rerun"] = {
            "date": "2026-09-12",
            "reran_entries": len(good),
            "errors": len(errors),
            "n_iterations": iterations,
            "random_seed": seed,
            "buffer_metres": DEFAULT_BUFFER_METRES,
            "method": "percentile (March 2026 estimator, pinned)",
            "estimator_source": "git show 2de117096:scripts/lib_advanced_metrics.py",
            "reference": str(DEFAULT_REFERENCE.relative_to(PROJECT_ROOT)),
            "bounds": str(DEFAULT_BOUNDS.relative_to(PROJECT_ROOT)),
            "script": "scripts/repair_bootstrap_cis.py",
            "note": (
                "Entries whose source pass file grew under the E70 recovery "
                "campaign after their CI was computed, re-run on the present "
                "file. Superseded values preserved per entry in pre_e70."
            ),
            "audit_report": AUDIT_REPORT,
        }
        if not dry_run:
            write_store(store_path, payload)
            print(f"  wrote {store_path}")

    shifts.sort(key=lambda s: -abs(s[2] - s[1]))
    print("")
    print("Largest F1-mean shifts (before -> after):")
    for key, before, after, n_before, n_after in shifts[:10]:
        print(f"  {key:<56} {before:.6f} -> {after:.6f} "
              f"({after - before:+.6f}); n {n_before} -> {n_after}")
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Repair and refresh the bootstrap CI store.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    repair = sub.add_parser("repair-paths", help="Rewrite dead source_file paths.")
    repair.add_argument("stores", nargs="+", type=Path)
    repair.add_argument("--dry-run", action="store_true")

    gate = sub.add_parser("gate", help="Prove the estimator reproduces matching entries.")
    gate.add_argument("store", type=Path)
    gate.add_argument("--n", type=int, default=5)
    gate.add_argument("--workers", type=int, default=5)
    gate.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    gate.add_argument("--seed", type=int, default=DEFAULT_SEED)

    rerun = sub.add_parser("rerun", help="Recompute the mismatching entries in place.")
    rerun.add_argument("stores", nargs="+", type=Path)
    rerun.add_argument("--workers", type=int, default=8)
    rerun.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    rerun.add_argument("--seed", type=int, default=DEFAULT_SEED)
    rerun.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Argument vector (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit status.
    """
    args = build_parser().parse_args(argv)
    if args.command == "repair-paths":
        repair_paths(args.stores, dry_run=args.dry_run)
        return 0
    if args.command == "gate":
        return run_gate(args.store, args.n, args.workers, args.iterations, args.seed)
    return run_rerun(args.stores, args.workers, args.iterations, args.seed, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
