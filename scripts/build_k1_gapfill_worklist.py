#!/usr/bin/env python3
"""Build the K = 1 gap-fill worklist for the uplift supplement (card step 2).

Build order step 2 of ``planning/uplift-supplement-2026-08-28.md``. Consensus
uplift is the difference between a multi-pass cell and the single pass it was
built from, so every K ≥ 3 consensus cell needs an N = 1 anchor. Modern runs
already carry N = 1 rungs; the older incumbents do not, and their anchors have
to be scored from the committed per-pass detections.

This script identifies which anchors are missing, resolves the exact committed
per-pass detection file each one would score, and reproduces the parent cell's
own scoring recipe with only the detections path and output directory swapped.
It emits a worklist and a shell script of invocations.

**It never scores anything.** Scoring is a bootstrap-heavy job that belongs on
sapphire; ``--execute`` exists only to say so and exit non-zero.

The blocked half, disclosed and never approximated
--------------------------------------------------
The card records that K = 1 **with** verifier is blocked for the incumbents
because the verifier never saw singleton candidates. This script does not take
that on trust: it measures the floor, reading every ``candidate_manifest.json``
under each run's output tree and recording the lowest ``vote_count`` the
verifier actually processed, together with the manifest that proves it. A
verified cell whose run has a floor above 1 gets ``status = blocked`` and a
reason naming the measurement — never an approximated number.

Outputs (under ``results/uplift-supplement/``)
----------------------------------------------
``k1-gapfill-worklist.csv``   — one row per candidate anchor.
``k1-gapfill-commands.sh``    — the ready jobs as runnable invocations.
``k1-gapfill-disclosure.md``  — the verifier-coverage measurement and what it
                                blocks, for the supplement's methods text.

Zero API. Reads committed artefacts only.

Usage::

    python scripts/build_k1_gapfill_worklist.py
    python scripts/build_k1_gapfill_worklist.py --out-dir /tmp/preview

Created: 2026-08-29 (uplift-supplement card, Build order step 2)
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
from typing import Any

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
    resolve_reference,
    write_csv,
)

DEFAULT_OUT_DIR = Path("results/uplift-supplement")

#: The lowest N that counts as a consensus cell needing an anchor. The card
#: says "for every K >= 3 consensus cell"; N is the passes actually consumed.
MIN_CONSENSUS_N = 3

WORKLIST_COLUMNS: tuple[str, ...] = (
    "job_id", "source_condition", "run_id", "proposer_pool", "rung",
    "stratum_id", "corpus", "reference", "buffer_m", "frame_id",
    "architecture", "aggregation", "N", "min_votes", "prob_t", "verified",
    "status", "blocked_reason",
    "detections_path", "reference_path", "bounds_path",
    "engine", "output_dir", "command",
    "k1_with_verifier", "k1_with_verifier_reason",
    "verifier_min_vote_seen", "verifier_crop_manifest", "notes",
)


def measure_verifier_floor(
    run_dir: Path, repo_root: Path
) -> tuple[int | None, str | None, int]:
    """Measure the lowest vote shell a run's verifier actually processed.

    Every verifier stage writes a ``candidate_manifest.json`` recording the
    candidates it cropped, each carrying the ``vote_count`` it arrived with. The
    minimum across a run's manifests is therefore the empirical floor of
    verifier coverage: a candidate below it was never seen by the verifier, so
    no verified cell can be derived at that vote threshold.

    Args:
        run_dir: The run's output directory.
        repo_root: Repository root, so the evidence path is recorded relative.

    Returns:
        ``(floor, manifest_path, n_manifests)``. ``floor`` is ``None`` when the
        run has no manifest recording vote counts (single-pass verifier stages
        crop from a raw pass, whose features carry no vote count at all).
    """
    floor: int | None = None
    winner: str | None = None
    manifests = sorted(run_dir.rglob("candidate_manifest.json"))
    for path in manifests:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        votes = [
            candidate.get("properties", {}).get("vote_count")
            for candidate in document.get("candidates", [])
        ]
        votes = [v for v in votes if isinstance(v, int)]
        if not votes:
            continue
        local = min(votes)
        if floor is None or local < floor:
            floor, winner = local, str(path.relative_to(repo_root))
    return floor, winner, len(manifests)


def _render_command(
    recipe: ScoringRecipe, detections: str, output_dir: str, label: str
) -> str:
    """Render the scoring invocation for one gap-fill job.

    Reproduces the parent cell's recipe verbatim, swapping only the detections
    path, the output directory, and the label.

    Args:
        recipe: The recovered recipe.
        detections: Repo-relative path of the per-pass detection set to score.
        output_dir: Where the evaluation should be written.
        label: Human-readable label for the new cell.

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


def build_worklist(
    sources: CorpusSources,
) -> tuple[list[dict[str, Any]], dict[str, tuple[int | None, str | None, int]]]:
    """Identify every K >= 3 consensus cell's missing N = 1 anchor.

    An anchor is *not* missing when the registry already holds a single-pass,
    no-verifier condition drawing on the same run and pool — the modern runs'
    N = 1 rungs. Where it is missing, the job scores the pool's first committed
    pass (``run_1``), which is the preregistered first-N rule at N = 1.

    Args:
        sources: Loaded corpus sources.

    Returns:
        ``(rows, floors)`` — the worklist (one row per K >= 3 consensus or
        verified cell) and the per-run verifier-coverage measurements that the
        disclosure document renders.
    """
    specs = list(iter_condition_specs(sources))

    # Existing single-pass, no-verifier rungs, keyed by (run, pool).
    existing: dict[tuple[str, str], str] = {}
    for run_id, condition_id, spec in specs:
        if spec.get("aggregation") == "none" and int(spec["n_passes"]) == 1:
            existing.setdefault((run_id, spec.get("proposer_pool") or ""), condition_id)

    floors: dict[str, tuple[int | None, str | None, int]] = {}
    rows: list[dict[str, Any]] = []

    for run_id, condition_id, spec in specs:
        if spec.get("aggregation") not in {"consensus", "verified"}:
            continue
        if int(spec["n_passes"]) < MIN_CONSENSUS_N:
            continue

        facts = sources.facts.get(run_id, {})
        pool = spec.get("proposer_pool") or ""
        document = None
        eval_path = spec.get("eval_path")
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

        if run_id not in floors:
            entry = sources.registry.get(run_id)
            run_dir = sources.repo_root / entry["directory_path"] if entry else None
            floors[run_id] = (
                measure_verifier_floor(run_dir, sources.repo_root)
                if run_dir and run_dir.is_dir() else (None, None, 0)
            )
        floor, floor_manifest, _ = floors[run_id]

        recipe, recipe_problem = read_scoring_recipe(
            sources.repo_root, eval_path, document
        )
        detections = None
        pool_dir = sources.pool_directory(run_id, pool)
        if pool_dir is not None:
            try:
                passes = resolve_pool_passes(pool_dir, allow_multiple=False)
            except (AmbiguousPassError, PassCountMismatch):
                passes = []
            if passes:
                detections = str(passes[0].relative_to(sources.repo_root))

        is_verified = spec.get("aggregation") == "verified"
        job_id = f"k1::{condition_id}"
        slug = condition_id.replace("::", "__").replace(".", "_")
        output_dir = f"results/uplift-supplement/k1-gapfill/{slug}"
        notes: list[str] = []

        # The card's two anchors are tracked separately. `status` is the
        # readiness of the NO-verifier N = 1 job this worklist emits;
        # `k1_with_verifier` is the disclosed verdict on the PV anchor, which
        # no job can supply when the verifier never saw singletons.
        if not is_verified:
            with_verifier, with_verifier_reason = "not-applicable", None
        elif floor is None:
            with_verifier = "blocked"
            with_verifier_reason = (
                "unmeasurable: this run's output tree holds no candidate "
                "manifest recording vote counts, so verifier coverage cannot be "
                "established. DISCLOSED, not approximated."
            )
        elif floor > 1:
            with_verifier = "blocked"
            with_verifier_reason = (
                "the verifier's measured coverage floor for this run is "
                f"vote_count >= {floor}, so singleton candidates were never "
                "verified and no K = 1 WITH-verifier cell can be derived. "
                "DISCLOSED, not approximated."
            )
        else:
            with_verifier = "derivable"
            with_verifier_reason = (
                "the verifier processed the full vote >= 1 union for this run "
                f"(measured floor vote_count >= {floor}), so a K = 1 "
                "WITH-verifier cell is derivable from the committed "
                "probabilities without new API spend."
            )

        if (run_id, pool) in existing:
            status, blocked = "already-registered", None
            notes.append(
                f"registry already holds the N = 1 rung {existing[(run_id, pool)]}"
            )
        elif detections is None:
            status, blocked = "blocked", (
                "no committed per-pass detection file could be resolved for pool "
                f"{pool!r} of run {run_id!r} under any conventional layout"
            )
        elif recipe is None:
            status, blocked = "blocked", recipe_problem
        else:
            status, blocked = "ready", None

        rows.append({
            "job_id": job_id,
            "source_condition": condition_id,
            "run_id": run_id,
            "proposer_pool": pool,
            "rung": 1,
            "stratum_id": stratum.stratum_id,
            "corpus": corpus,
            "reference": reference,
            "buffer_m": buffer_m,
            "frame_id": scope.get("test_set_id"),
            "architecture": spec.get("architecture"),
            "aggregation": spec.get("aggregation"),
            "N": spec.get("n_passes"),
            "min_votes": spec.get("vote_threshold"),
            "prob_t": spec.get("prob_threshold"),
            "verified": is_verified,
            "status": status,
            "blocked_reason": blocked,
            "detections_path": detections,
            "reference_path": (recipe.ground_truth if recipe else None) or reference_path,
            "bounds_path": recipe.bounds if recipe else None,
            "engine": recipe.engine if recipe else None,
            "output_dir": output_dir if status == "ready" else None,
            "command": (
                _render_command(recipe, detections, output_dir, f"{slug}-n1")
                if status == "ready" and recipe and detections else None
            ),
            "k1_with_verifier": with_verifier,
            "k1_with_verifier_reason": with_verifier_reason,
            "verifier_min_vote_seen": floor,
            "verifier_crop_manifest": floor_manifest,
            "notes": "; ".join(notes) or None,
        })
    return rows, floors


def render_disclosure(
    rows: list[dict[str, Any]],
    floors: dict[str, tuple[int | None, str | None, int]],
) -> str:
    """Render the verifier-coverage disclosure.

    Args:
        rows: The worklist rows.
        floors: Per-run ``(floor, manifest, n_manifests)`` measurements.

    Returns:
        The Markdown document.
    """
    today = datetime.now(timezone.utc).date().isoformat()
    status_counts = Counter(r["status"] for r in rows)
    with_verifier_counts = Counter(
        r["k1_with_verifier"] for r in rows if r["verified"]
    )
    blocked_by_verifier = [
        r for r in rows if r["verified"] and r["k1_with_verifier"] == "blocked"
    ]
    lines = [
        "# K = 1 gap-fill — worklist and verifier-coverage disclosure",
        "",
        f"> **Last revised**: {today} (original publication; generated by "
        "`scripts/build_k1_gapfill_worklist.py`).",
        "> See [§ Changelog](#changelog) for revision history.",
        "",
        "Build order step 2 of `planning/uplift-supplement-2026-08-28.md`. No",
        "scoring has been run: this document and its worklist are the plan.",
        "",
        "The worklist tracks two anchors separately, because they have different",
        "availability. `status` is the readiness of the **no-verifier** N = 1",
        "job — the anchor consensus uplift needs, scored from a committed raw",
        "pass. `k1_with_verifier` is the verdict on the **with-verifier** N = 1",
        "anchor, which no job can supply where the verifier never saw singleton",
        "candidates.",
        "",
        "## No-verifier N = 1 jobs",
        "",
        "| Status | Cells |",
        "|---|---:|",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| `{status}` | {count} |")

    lines += [
        "",
        "## With-verifier N = 1 anchors",
        "",
        "| Verdict | Verified cells |",
        "|---|---:|",
    ]
    for verdict, count in sorted(with_verifier_counts.items()):
        lines.append(f"| `{verdict}` | {count} |")

    lines += [
        "",
        "## The disclosure: K = 1 WITH verifier",
        "",
        "Consensus uplift needs an N = 1 anchor. For a *verified* cell the",
        "honest anchor would be a single pass put through the same verifier —",
        "and for most of the corpus that cell cannot exist, because the verifier",
        "never saw singleton candidates. The card records this; the numbers below",
        "are measured rather than assumed.",
        "",
        "Each verifier stage writes a `candidate_manifest.json` listing the",
        "candidates it cropped, each carrying the `vote_count` it arrived with.",
        "The minimum across a run's manifests is the floor of verifier coverage.",
        "",
        "| Run | Verifier floor (`vote_count` >=) | Manifests | Evidence |",
        "|---|---:|---:|---|",
    ]
    for run_id in sorted(floors):
        floor, manifest, count = floors[run_id]
        if count == 0:
            continue
        lines.append(
            f"| `{run_id}` | {floor if floor is not None else '—'} | {count} "
            f"| `{manifest or '—'}` |"
        )

    lines += [
        "",
        f"**{len(blocked_by_verifier)} verified cell(s) have no derivable",
        "with-verifier N = 1 anchor.** They are disclosed, not approximated: no",
        "substitute is computed, and the supplement's verified-cell uplift column",
        "is left empty rather than filled with a number the corpus cannot",
        "support. Their no-verifier N = 1 jobs still run, and carry the",
        "consensus-uplift signal for those pools.",
        "",
        "A floor of 1 means the run's verifier processed the full vote >= 1",
        "union, so a K = 1 WITH-verifier cell IS derivable there — the modern",
        "stride, grid, and image campaigns, whose ladder rungs are in several",
        "cases already registered.",
        "",
        "**Refinement on the card.** The card records the block as a",
        "\"vote >= 3 shells\" phenomenon. Measured, the floors are not uniform —",
        "the distribution across runs with a measurable floor is:",
        "",
        "| Measured floor | Runs |",
        "|---:|---:|",
        *[
            f"| vote_count >= {value} | {count} |"
            for value, count in sorted(
                Counter(
                    floor for floor, _manifest, n in floors.values()
                    if n and floor is not None
                ).items()
            )
        ],
        "",
        "The per-run numbers in the table above are the ones to quote; a single",
        "corpus-wide threshold would be wrong for some runs in both directions.",
        "",
        "## How a ready job is scored",
        "",
        "Each ready job reproduces its parent cell's own recipe, recovered from",
        "the parent's committed evaluation artefact (`_metadata.cli_args`, or the",
        "engine summary an adapter names), with only the detections path, output",
        "directory, and label swapped. Scoring the anchor a different way would",
        "make the uplift a measurement of the scorer.",
        "",
        "The invocations are in `k1-gapfill-commands.sh`. They are",
        "bootstrap-heavy; run them on sapphire.",
        "",
        "## Changelog",
        "",
        f"### {today} — Original publication",
        "",
        "Generated with the first build of the K = 1 gap-fill worklist.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Build the K = 1 gap-fill worklist.

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
            "Refused by design. This builder never scores: the jobs are "
            "bootstrap-heavy and belong on sapphire, run deliberately by an "
            "operator from the emitted shell script."
        ),
    )
    args = parser.parse_args(argv)

    if args.execute:
        print(
            "refusing --execute: this builder plans, it does not score. Run "
            "results/uplift-supplement/k1-gapfill-commands.sh on sapphire.",
            file=sys.stderr,
        )
        return 2

    repo_root = args.repo_root.resolve()
    out_dir = (args.out_dir or (repo_root / DEFAULT_OUT_DIR)).resolve()
    sources = CorpusSources.load(repo_root)
    rows, floors = build_worklist(sources)

    write_csv(out_dir / "k1-gapfill-worklist.csv", rows, WORKLIST_COLUMNS,
              sources.notation)

    ready = [r for r in rows if r["status"] == "ready"]
    script = [
        "#!/usr/bin/env bash",
        "# K = 1 gap-fill scoring jobs — uplift supplement, card step 2.",
        "# GENERATED by scripts/build_k1_gapfill_worklist.py. Do not edit.",
        "# Bootstrap-heavy: run on sapphire, from the repository root.",
        "set -euo pipefail",
        "",
    ]
    for row in ready:
        script += [f"# {row['job_id']}", row["command"], ""]
    (out_dir / "k1-gapfill-commands.sh").write_text("\n".join(script), encoding="utf-8")
    (out_dir / "k1-gapfill-commands.sh").chmod(0o755)
    (out_dir / "k1-gapfill-disclosure.md").write_text(
        render_disclosure(rows, floors), encoding="utf-8"
    )

    counts = Counter(r["status"] for r in rows)
    print(f"k1-gapfill-worklist.csv   {len(rows):>4} rows")
    for status, count in sorted(counts.items()):
        print(f"  {status:<20} {count:>4}")
    print(f"written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
