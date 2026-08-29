#!/usr/bin/env python3
"""Pair every verified cell with its pre-verifier twin (card step 3).

Build order step 3 of ``planning/uplift-supplement-2026-08-28.md``. Verifier
uplift is the difference a verifier makes *holding everything else fixed*: same
passes, same vote threshold, same reference, same buffer, same frame. So for
every verified cell the supplement needs the consensus set that went INTO the
verifier at the same vote threshold — and then the difference between their
scores.

This script locates that pre-verifier twin from the committed artefacts and
emits the pairing worklist. It computes nothing and scores nothing: the uplift
column is produced by ``scripts/compute_verifier_uplift.py`` once the twins have
scores, and the scoring itself runs on sapphire.

How a twin is located
---------------------
Four rules, in descending order of authority, each recorded in ``pairing_basis``:

``registered``
    A sibling condition already in the registry with the same run, pool, N, and
    vote threshold, and no verifier. Nothing to score — it already has metrics.
``consensus-file``
    A committed consensus GeoJSON at that vote threshold under the pool
    (``consensus_t<k>.geojson`` or ``consensus-<k>of<N>.geojson``). Accepted only
    when the pool's committed pass count equals N, because the sweep's
    denominator is implicit in the filename.
``union``
    The committed vote >= 1 union over the N passes. The paired shell has to be
    filtered out of it first; ``materialise_filter`` records the predicate.
``unresolved``
    Nothing committed matches. Recorded as blocked with the reason, never
    substituted.

Outputs (under ``results/uplift-supplement/``)
----------------------------------------------
``verifier-pairing-worklist.csv``  — one row per verified cell.
``verifier-pairing-commands.sh``   — scoring invocations for the ready pairs.
``verifier-pairing-report.md``     — resolution counts and what stays blocked.

Zero API. Reads committed artefacts only.

Usage::

    python scripts/build_verifier_pairing_worklist.py
    python scripts/build_verifier_pairing_worklist.py --out-dir /tmp/preview

Created: 2026-08-29 (uplift-supplement card, Build order step 3)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_detection_paths import (  # noqa: E402
    AmbiguousPassError,
    PassCountMismatch,
    resolve_pool_passes,
)
from scripts.lib_uplift_supplement import (  # noqa: E402
    PRIMARY_BUFFER_BY_CORPUS,
    CorpusSources,
    ScoringRecipe,
    StratumKey,
    iter_condition_specs,
    read_scoring_recipe,
    resolve_geometry,
    resolve_reference,
    write_csv,
)

DEFAULT_OUT_DIR = Path("results/uplift-supplement")

WORKLIST_COLUMNS: tuple[str, ...] = (
    "job_id", "verified_condition_id", "run_id", "proposer_pool",
    "stratum_id", "corpus", "reference", "buffer_m", "frame_id",
    "N", "min_votes", "prob_t",
    "status", "pairing_basis", "blocked_reason",
    "unverified_condition_id", "unverified_detections_path",
    "unverified_eval_path", "union_path", "materialise_filter",
    "reference_path", "bounds_path", "engine", "output_dir", "command",
    "notes",
)


def _find_consensus_file(
    pool_dir: Path | None,
    run_dir: Path | None,
    votes: int,
    n_passes: int,
    discriminators: Sequence[str] = (),
) -> tuple[Path | None, str | None]:
    """Locate a committed consensus GeoJSON at a given vote threshold.

    Two naming conventions are in the corpus.

    * **Explicit** — ``<name>-<k>of<N>.geojson``. The denominator is in the
      filename, so a match is unambiguous. Searched under the pool directory and
      under the run directory, because the consensus tree sits at pool level in
      some campaigns and at run level in others.
    * **Sweep** — ``consensus_t<k>.geojson``, written by the threshold sweep.
      This form does NOT name its denominator, so it is trustworthy only when
      the pool holds exactly N committed passes. Otherwise ``consensus_t4`` of a
      K = 10 pool would be read as a 4-of-5 set, and the resulting "uplift"
      would compare two different aggregations.

    Args:
        pool_dir: The proposer pool's output directory, if resolvable.
        run_dir: The run's output directory, if resolvable.
        votes: The vote threshold k.
        n_passes: N, the passes the verified cell consumed.
        discriminators: Tokens identifying the cell (geometry, pool), used to
            choose between several explicit matches under one root.

    Returns:
        ``(path, rejection_reason)``. The reason is populated only when a
        candidate was found and deliberately refused.
    """
    roots = [d for d in (pool_dir, run_dir) if d is not None and d.is_dir()]
    for root in roots:
        explicit = sorted(
            {
                *root.glob(f"consensus/*-{votes}of{n_passes}.geojson"),
                *root.glob(f"*/consensus/*-{votes}of{n_passes}.geojson"),
            }
        )
        if len(explicit) == 1:
            return explicit[0], None
        if explicit:
            for token in discriminators:
                narrowed = [p for p in explicit if token and token in str(p)]
                if len(narrowed) == 1:
                    return narrowed[0], None
            return None, (
                f"{len(explicit)} committed {votes}-of-{n_passes} consensus sets "
                f"sit under {root}, and none of the cell's identifying tokens "
                "picks exactly one. Refused rather than guessed"
            )

    if pool_dir is None or not pool_dir.is_dir():
        return None, None
    sweep = pool_dir / "consensus" / f"consensus_t{votes}.geojson"
    if not sweep.exists():
        return None, None
    try:
        committed = len(resolve_pool_passes(pool_dir, allow_multiple=False))
    except (AmbiguousPassError, PassCountMismatch):
        committed = -1
    if committed == n_passes:
        return sweep, None
    return None, (
        f"the only candidate pre-verifier set is the sweep file {sweep.name}, "
        f"whose denominator is implicit; the pool holds {committed} committed "
        f"pass(es) but the cell consumed N = {n_passes}, so the file is a "
        f"{votes}-of-{committed} set and pairing it would compare two different "
        "aggregations. Refused rather than approximated"
    )


def _find_union(
    run_dir: Path, discriminators: Sequence[str], n_passes: int
) -> Path | None:
    """Locate the committed vote >= 1 union over a pool's first N passes.

    A run can hold several unions — the grid campaign has one per geometry, all
    drawing on a pool named ``brief-text`` — so the pool name alone does not
    always discriminate. The caller supplies every token that identifies the
    cell (pool name, geometry cell); a union is accepted only when one of them
    appears in its path, or when the run holds exactly one union at that N.

    Args:
        run_dir: The run's output directory.
        discriminators: Tokens identifying the cell, most specific first.
        n_passes: N.

    Returns:
        The union file, or ``None`` when no unambiguous match exists.
    """
    candidates = sorted(run_dir.rglob(f"union_k{n_passes}.geojson"))
    if not candidates:
        return None
    for token in discriminators:
        if not token:
            continue
        matches = [c for c in candidates if token in str(c)]
        if len(matches) == 1:
            return matches[0]
    return candidates[0] if len(candidates) == 1 else None


def _render_command(
    recipe: ScoringRecipe, detections: str, output_dir: str, label: str
) -> str:
    """Render the scoring invocation for one pairing job.

    Reproduces the verified cell's own recipe so the pair differs in exactly one
    thing — the verifier.

    Args:
        recipe: The recipe recovered from the verified cell's evaluation.
        detections: Repo-relative path of the unverified detection set.
        output_dir: Where the evaluation should be written.
        label: Human-readable label.

    Returns:
        A single-line shell command.
    """
    if recipe.engine == "evaluate_detections":
        parts = [
            "python", "scripts/evaluate_detections.py",
            "--detections", detections,
            "--ground-truth", recipe.ground_truth or "",
            "--bounds", recipe.bounds or "",
            "--buffers", *[str(b) for b in recipe.buffers],
            "--bootstrap", str(recipe.bootstrap or 10000),
            "--seed", str(recipe.seed or 42),
            "--mcc",
            "--output-dir", output_dir,
            "--label", label,
        ]
    else:
        parts = [
            "python", "scripts/compute_corrected_f1_multi_buffer.py",
            "--verified-detections", detections,
            "--student-gt", recipe.ground_truth or "",
            "--bounds", recipe.bounds or "",
            "--buffers", *[str(b) for b in recipe.buffers],
            "--n-bootstrap", str(recipe.bootstrap or 10000),
            "--seed", str(recipe.seed or 42),
            "--compute-mcc",
            "--output-dir", output_dir,
        ]
        for name, value in recipe.extra.items():
            parts += [f"--{name.replace('_', '-')}", value]
    return " ".join(shlex.quote(p) for p in parts)


def build_worklist(sources: CorpusSources) -> list[dict[str, Any]]:
    """Pair every verified cell with its pre-verifier twin.

    Args:
        sources: Loaded corpus sources.

    Returns:
        One row per verified condition in the registry.
    """
    specs = list(iter_condition_specs(sources))

    def _pair_key(run: str, spec: dict[str, Any]) -> tuple[Any, ...]:
        """Build the identity a verified cell and its twin must share.

        Pool + N + vote threshold is not enough on its own. The grid campaign's
        four geometries all draw on a pool named ``brief-text``, so without the
        geometry a 384/50 % verified cell pairs happily with a 384/12.5 %
        consensus cell — a mis-pairing that yields a plausible, wrong uplift.
        The fusion family matters for the same reason: h8-v2 registers greedy
        and WBF aggregations of the same passes, and a WBF-verified cell must be
        paired with the WBF consensus, not the greedy one.
        """
        facts = sources.facts.get(run, {})
        geometry = resolve_geometry(
            spec.get("proposer_pool"), spec["label"], facts.get("tile_size_px")
        )["geometry"]
        return (
            run,
            spec.get("proposer_pool") or "",
            geometry,
            "wbf" if "wbf" in spec["label"] else "greedy",
            int(spec["n_passes"]),
            spec.get("vote_threshold"),
        )

    registered: dict[tuple[Any, ...], tuple[str, dict[str, Any]]] = {}
    for run_id, condition_id, spec in specs:
        if spec.get("aggregation") in {"consensus", "greedy", "wbf"}:
            registered.setdefault(_pair_key(run_id, spec), (condition_id, spec))

    rows: list[dict[str, Any]] = []
    for run_id, condition_id, spec in specs:
        if spec.get("aggregation") != "verified":
            continue

        facts = sources.facts.get(run_id, {})
        pool = spec.get("proposer_pool") or ""
        n_passes = int(spec["n_passes"])
        votes = spec.get("vote_threshold")

        eval_path = spec.get("eval_path")
        document = None
        if eval_path and (sources.repo_root / eval_path).exists():
            document = json.loads(
                (sources.repo_root / eval_path).read_text(encoding="utf-8")
            )
        reference, reference_path, _ = resolve_reference(
            (document or {}).get("_metadata"), spec["label"], facts.get("gt_reference")
        )
        scope = facts.get("scope") or {}
        corpus = facts.get("corpus")
        buffer_m = PRIMARY_BUFFER_BY_CORPUS.get(corpus or "", 0)
        stratum = StratumKey(
            corpus=corpus or "unknown", reference=reference or "unknown",
            buffer_m=buffer_m, frame_id=scope.get("test_set_id") or "unknown",
        )
        recipe, recipe_problem = read_scoring_recipe(
            sources.repo_root, eval_path, document
        )

        entry = sources.registry.get(run_id)
        run_dir = sources.repo_root / entry["directory_path"] if entry else None
        pool_dir = sources.pool_directory(run_id, pool)

        basis = "unresolved"
        status = "blocked"
        blocked: str | None = None
        twin_id = twin_detections = twin_eval = union_path = None
        materialise_filter = None
        notes: list[str] = []

        geometry = resolve_geometry(
            pool, spec["label"], facts.get("tile_size_px")
        )["geometry"]
        sibling = registered.get(_pair_key(run_id, spec))
        if votes is None:
            blocked = (
                "the verified cell records no vote threshold, so there is no "
                "'same vote threshold' pre-verifier set to pair it with"
            )
        elif sibling is not None:
            basis, status = "registered", "already-registered"
            twin_id, twin_spec = sibling
            twin_detections = twin_spec.get("detections")
            twin_eval = twin_spec.get("eval_path")
            notes.append("the pre-verifier twin is already scored and registered")
        else:
            found, refusal = _find_consensus_file(
                pool_dir, run_dir, int(votes), n_passes, (geometry or "", pool)
            )
            if found is not None:
                basis = "consensus-file"
                twin_detections = str(found.relative_to(sources.repo_root))
            elif run_dir is not None and run_dir.is_dir():
                union = _find_union(
                    run_dir, (geometry or "", pool), n_passes
                )
                if union is not None:
                    basis = "union"
                    union_path = str(union.relative_to(sources.repo_root))
                    materialise_filter = f"vote_count >= {int(votes)}"
                    notes.append(
                        "the paired shell must be filtered out of the union "
                        "before scoring; no API spend, no re-aggregation"
                    )

            if basis == "unresolved":
                blocked = refusal or (
                    "no committed pre-verifier set was found for "
                    f"(run={run_id}, pool={pool!r}, N={n_passes}, k={votes}): "
                    "the registry holds no consensus sibling, no consensus "
                    "GeoJSON names that threshold under the pool or run tree, "
                    "and the run holds no vote >= 1 union over N passes"
                )
            elif recipe is None:
                status, blocked = "blocked", recipe_problem
            else:
                status = "ready" if basis == "consensus-file" else "ready-after-materialise"

        slug = condition_id.replace("::", "__").replace(".", "_")
        output_dir = f"results/uplift-supplement/verifier-pairing/{slug}"
        scoreable = twin_detections if basis == "consensus-file" else None
        rows.append({
            "job_id": f"pair::{condition_id}",
            "verified_condition_id": condition_id,
            "run_id": run_id,
            "proposer_pool": pool,
            "stratum_id": stratum.stratum_id,
            "corpus": corpus,
            "reference": reference,
            "buffer_m": buffer_m,
            "frame_id": scope.get("test_set_id"),
            "N": n_passes,
            "min_votes": votes,
            "prob_t": spec.get("prob_threshold"),
            "status": status,
            "pairing_basis": basis,
            "blocked_reason": blocked,
            "unverified_condition_id": twin_id,
            "unverified_detections_path": twin_detections,
            "unverified_eval_path": twin_eval,
            "union_path": union_path,
            "materialise_filter": materialise_filter,
            "reference_path": (recipe.ground_truth if recipe else None) or reference_path,
            "bounds_path": recipe.bounds if recipe else None,
            "engine": recipe.engine if recipe else None,
            "output_dir": output_dir if status.startswith("ready") else None,
            "command": (
                _render_command(recipe, scoreable, output_dir, f"{slug}-unverified")
                if status == "ready" and recipe and scoreable else None
            ),
            "notes": "; ".join(notes) or None,
        })
    return rows


def render_report(rows: list[dict[str, Any]]) -> str:
    """Render the pairing report.

    Args:
        rows: The worklist rows.

    Returns:
        The Markdown document.
    """
    today = datetime.now(timezone.utc).date().isoformat()
    status_counts = Counter(r["status"] for r in rows)
    basis_counts = Counter(r["pairing_basis"] for r in rows)
    lines = [
        "# With/without-verifier pairing — worklist",
        "",
        f"> **Last revised**: {today} (original publication; generated by "
        "`scripts/build_verifier_pairing_worklist.py`).",
        "> See [§ Changelog](#changelog) for revision history.",
        "",
        "Build order step 3 of `planning/uplift-supplement-2026-08-28.md`. No",
        "scoring has been run: this document and its worklist are the plan.",
        "",
        "Verifier uplift is the difference a verifier makes holding everything",
        "else fixed. Each row pairs one verified cell with the consensus set that",
        "went INTO its verifier at the same vote threshold — same passes, same",
        "reference, same buffer, same frame, so the pair sits in one stratum by",
        "construction and the uplift is a within-stratum difference.",
        "",
        f"{len(rows)} verified cell(s) in the registry.",
        "",
        "## Status",
        "",
        "| Status | Cells |",
        "|---|---:|",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| `{status}` | {count} |")

    lines += [
        "",
        "`already-registered` pairs need nothing: the twin is scored. `ready`",
        "pairs have a committed consensus GeoJSON and one scoring invocation.",
        "`ready-after-materialise` pairs need the vote shell filtered out of the",
        "committed union first — a local geometry filter, no API spend and no",
        "re-aggregation — and the row records the exact predicate in",
        "`materialise_filter`.",
        "",
        "## How the twin was located",
        "",
        "| `pairing_basis` | Cells |",
        "|---|---:|",
    ]
    for basis, count in sorted(basis_counts.items()):
        lines.append(f"| `{basis}` | {count} |")

    blocked = [r for r in rows if r["status"] == "blocked"]
    lines += [
        "",
        "## Blocked pairs",
        "",
        f"{len(blocked)} verified cell(s) have no locatable pre-verifier twin.",
        "They are recorded with the reason and left empty in the uplift column;",
        "no substitute set is constructed.",
        "",
    ]
    if blocked:
        lines += ["| Verified cell | Reason |", "|---|---|"]
        for row in blocked:
            reason = (row["blocked_reason"] or "").replace("\n", " ")
            lines.append(f"| `{row['verified_condition_id']}` | {reason} |")

    lines += [
        "",
        "## Producing the uplift column",
        "",
        "Once the twins have scores, `scripts/compute_verifier_uplift.py` joins",
        "them and writes `verifier-uplift.csv`. It refuses any pair whose two",
        "cells do not share a `stratum_id`, so a mis-paired row fails loudly",
        "rather than producing a plausible number.",
        "",
        "## Changelog",
        "",
        f"### {today} — Original publication",
        "",
        "Generated with the first build of the verifier-pairing worklist.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Build the with/without-verifier pairing worklist.

    Args:
        argv: Command-line arguments.

    Returns:
        Process exit code: 0 on success, 2 if ``--execute`` was passed.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument(
        "--execute", action="store_true",
        help=(
            "Refused by design. This builder plans; scoring is bootstrap-heavy "
            "and belongs on sapphire, run deliberately from the emitted script."
        ),
    )
    args = parser.parse_args(argv)

    if args.execute:
        print(
            "refusing --execute: this builder plans, it does not score. Run "
            "results/uplift-supplement/verifier-pairing-commands.sh on sapphire.",
            file=sys.stderr,
        )
        return 2

    repo_root = args.repo_root.resolve()
    out_dir = (args.out_dir or (repo_root / DEFAULT_OUT_DIR)).resolve()
    sources = CorpusSources.load(repo_root)
    rows = build_worklist(sources)

    write_csv(out_dir / "verifier-pairing-worklist.csv", rows, WORKLIST_COLUMNS,
              sources.notation)

    script = [
        "#!/usr/bin/env bash",
        "# With/without-verifier pairing scoring jobs — uplift supplement, step 3.",
        "# GENERATED by scripts/build_verifier_pairing_worklist.py. Do not edit.",
        "# Bootstrap-heavy: run on sapphire, from the repository root.",
        "# Rows with status 'ready-after-materialise' are NOT here: their vote",
        "# shell must first be filtered out of the committed union named in the",
        "# worklist's union_path, using the materialise_filter predicate.",
        "set -euo pipefail",
        "",
    ]
    for row in rows:
        if row["status"] == "ready" and row["command"]:
            script += [f"# {row['job_id']}", row["command"], ""]
    (out_dir / "verifier-pairing-commands.sh").write_text(
        "\n".join(script), encoding="utf-8"
    )
    (out_dir / "verifier-pairing-commands.sh").chmod(0o755)
    (out_dir / "verifier-pairing-report.md").write_text(
        render_report(rows), encoding="utf-8"
    )

    counts = Counter(r["status"] for r in rows)
    print(f"verifier-pairing-worklist.csv   {len(rows):>4} rows")
    for status, count in sorted(counts.items()):
        print(f"  {status:<26} {count:>4}")
    print(f"written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
