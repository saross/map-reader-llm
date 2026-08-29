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
that on trust: it measures the floor from the committed
``candidate_manifest.json`` files, recording the lowest ``vote_count`` the
verifier actually processed together with the manifest that proves it.

The measurement is **per verifier stage, not per run**. A run can hold several
stages at different shells — ``verifier-robustness`` verified a vote >= 1 union
alongside three vote >= 3 stages and one vote >= 16 stage — so a run-wide
minimum would declare a K = 1 PV anchor derivable for cells whose verifier
never saw a candidate below vote 3, and would cite a manifest belonging to a
different condition. Each cell is matched to its own stage by union shell,
consensus shell, and lineage tokens; ``verifier_floor_basis`` records which
rule matched, and a cell that cannot be matched is disclosed as unmeasurable
rather than handed the run minimum.

Smoke-test trees are excluded by construction: their 12-candidate rehearsals
include vote-1 candidates that would drag a real stage's floor to 1 and flip a
blocked verdict. Every excluded manifest is listed in the disclosure with its
ground, because a silently dropped manifest can move a floor either way.

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
from dataclasses import dataclass
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
    ORIGINAL_PUBLICATION_DATE,
    CorpusSources,
    ScoringRecipe,
    VerifierManifest,
    collect_verifier_manifests,
    condition_stratum,
    generated_doc_banner,
    iter_condition_specs,
    match_verifier_manifest,
    read_scoring_recipe,
    resolve_geometry,
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
    "k1_with_verifier", "k1_with_verifier_reason", "verifier_floor_basis",
    "verifier_min_vote_seen", "verifier_crop_manifest", "notes",
)


@dataclass(frozen=True)
class RunCoverage:
    """One run's verifier-coverage survey.

    Attributes:
        manifests: Every real candidate manifest under the run, summarised.
        skipped: Manifests excluded from the measurement, each with its ground.
            Published rather than swallowed: dropping a manifest can raise a
            measured floor and flip a with-verifier verdict.
    """

    manifests: list[VerifierManifest]
    skipped: list[str]


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
            "--bootstrap", str(10000 if recipe.bootstrap is None else recipe.bootstrap),
            "--seed", str(42 if recipe.seed is None else recipe.seed),
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
            "--n-bootstrap",
            str(10000 if recipe.bootstrap is None else recipe.bootstrap),
            "--seed", str(42 if recipe.seed is None else recipe.seed),
            "--compute-mcc",
            "--output-dir", output_dir,
        ]
        for name, value in recipe.extra.items():
            parts += [f"--{name.replace('_', '-')}", value]
    return " ".join(shlex.quote(p) for p in parts)


def build_worklist(
    sources: CorpusSources,
) -> tuple[list[dict[str, Any]], dict[str, RunCoverage]]:
    """Identify every K >= 3 consensus cell's missing N = 1 anchor.

    An anchor is *not* missing when the registry already holds a single-pass,
    no-verifier condition drawing on the same run, pool, and geometry — the
    modern runs' N = 1 rungs. Where it is missing, the job scores the pool's
    first committed pass (``run_1``), which is the preregistered first-N rule
    at N = 1.

    Args:
        sources: Loaded corpus sources.

    Returns:
        ``(rows, coverage)`` — the worklist (one row per K >= 3 consensus or
        verified cell) and the per-run verifier-coverage survey the disclosure
        document renders.
    """
    specs = list(iter_condition_specs(sources))

    def _anchor_key(run: str, spec: dict[str, Any]) -> tuple[str, str, str | None]:
        """Identity an N = 1 anchor must share with the cell it anchors.

        Pool alone is not enough for the same reason it is not enough in the
        pairing worklist: the grid campaign's four geometries all draw on a pool
        named ``brief-text``, so a (run, pool) key would let one geometry's
        single-pass rung stand in as another's anchor.
        """
        facts = sources.facts.get(run, {})
        return (
            run,
            spec.get("proposer_pool") or "",
            resolve_geometry(
                spec.get("proposer_pool"), spec["label"], facts.get("tile_size_px")
            )["geometry"],
        )

    existing: dict[tuple[str, str, str | None], str] = {}
    lineages: dict[str, set[tuple[str, str | None]]] = {}
    for run_id, condition_id, spec in specs:
        _run, pool_name, geometry_cell = _anchor_key(run_id, spec)
        lineages.setdefault(run_id, set()).add((pool_name, geometry_cell))
        if spec.get("aggregation") == "none" and int(spec["n_passes"]) == 1:
            existing.setdefault(_anchor_key(run_id, spec), condition_id)

    coverage: dict[str, RunCoverage] = {}
    rows: list[dict[str, Any]] = []

    for run_id, condition_id, spec in specs:
        if spec.get("aggregation") not in {"consensus", "verified"}:
            continue
        n_passes = int(spec["n_passes"])
        if n_passes < MIN_CONSENSUS_N:
            continue

        facts = sources.facts.get(run_id, {})
        pool = spec.get("proposer_pool") or ""
        document = None
        eval_path = spec.get("eval_path")
        if eval_path and (sources.repo_root / eval_path).exists():
            document = json.loads(
                (sources.repo_root / eval_path).read_text(encoding="utf-8")
            )
        stratum, reference, scope = condition_stratum(
            sources, run_id, condition_id, spec, (document or {}).get("_metadata")
        )
        corpus = facts.get("corpus")
        geometry = resolve_geometry(
            pool, spec["label"], facts.get("tile_size_px")
        )["geometry"]

        if run_id not in coverage:
            entry = sources.registry.get(run_id)
            run_dir = sources.repo_root / entry["directory_path"] if entry else None
            if run_dir is not None and run_dir.is_dir():
                manifests, skipped = collect_verifier_manifests(
                    run_dir, sources.repo_root
                )
            else:
                manifests, skipped = [], []
            coverage[run_id] = RunCoverage(manifests=manifests, skipped=skipped)

        is_verified = spec.get("aggregation") == "verified"
        pool_dir = sources.pool_directory(run_id, pool)
        pool_rel = (
            str(pool_dir.relative_to(sources.repo_root)) if pool_dir else None
        )

        # Verifier coverage is a property of a verifier STAGE, not of a run.
        # The run's other lineages go in so a lone stage belonging to one of
        # them cannot be cited as this cell's evidence, and the pool directory
        # so a pool that verified in its own subtree is not handed another
        # lineage's run-level stage.
        #
        # Only VERIFIED cells get a citation at all. A consensus cell has no
        # verifier stage, so any manifest attributed to it is a false evidence
        # path — fifteen such rows were published, all of them pointing at
        # another lineage's stage.
        if is_verified:
            matched, floor_basis = match_verifier_manifest(
                coverage[run_id].manifests, spec["label"], pool, geometry,
                n_passes,
                siblings=sorted(lineages.get(run_id, set())),
                pool_dir=pool_rel,
            )
        else:
            matched, floor_basis = None, "not-applicable"

        recipe, recipe_problem = read_scoring_recipe(
            sources.repo_root, eval_path, document
        )
        detections = None
        if pool_dir is not None:
            # Where the passes manifest knows this pool's K, assert it against
            # the disk: a divergence between the two is exactly the undercount
            # resolve_pool_passes exists to surface, and it would otherwise
            # silently choose the wrong run_1.
            manifest_k = len(sources.passes.get((run_id, pool)) or [])
            try:
                passes = resolve_pool_passes(
                    pool_dir,
                    expected_passes=manifest_k or None,
                    allow_multiple=False,
                )
            except (AmbiguousPassError, PassCountMismatch):
                passes = []
            if passes:
                detections = str(passes[0].relative_to(sources.repo_root))

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
        elif matched is None:
            with_verifier = "blocked"
            with_verifier_reason = (
                f"unmeasurable ({floor_basis}): this cell's verifier stage could "
                "not be matched to a candidate manifest, so the vote shell its "
                "verifier actually saw is unknown. A run-wide minimum is NOT "
                "substituted — it would describe a different verifier stage. "
                "DISCLOSED, not approximated."
            )
        elif matched.min_vote > 1:
            with_verifier = "blocked"
            with_verifier_reason = (
                "this cell's own verifier stage processed candidates down to "
                f"vote_count >= {matched.min_vote} only, so singletons were "
                "never verified and no K = 1 WITH-verifier cell can be derived. "
                f"Measured from {matched.path} ({floor_basis}). DISCLOSED, not "
                "approximated."
            )
        else:
            with_verifier = "derivable"
            with_verifier_reason = (
                "this cell's own verifier stage processed the full vote >= 1 "
                f"union (measured from {matched.path}, {floor_basis}), so a "
                "K = 1 WITH-verifier cell is derivable from the committed "
                "probabilities without new API spend."
            )

        anchor = _anchor_key(run_id, spec)
        if anchor in existing:
            status, blocked = "already-registered", None
            notes.append(
                f"registry already holds the N = 1 rung {existing[anchor]}"
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
            "reference": reference.term,
            "buffer_m": stratum.buffer_m,
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
            "reference_path": reference.path,
            "bounds_path": recipe.bounds if recipe else None,
            "engine": recipe.engine if recipe else None,
            "output_dir": output_dir if status == "ready" else None,
            "command": (
                _render_command(recipe, detections, output_dir, f"{slug}-n1")
                if status == "ready" and recipe and detections else None
            ),
            "k1_with_verifier": with_verifier,
            "k1_with_verifier_reason": with_verifier_reason,
            "verifier_floor_basis": floor_basis,
            "verifier_min_vote_seen": matched.min_vote if matched else None,
            "verifier_crop_manifest": matched.path if matched else None,
            "notes": "; ".join(notes) or None,
        })
    return rows, coverage


def render_disclosure(
    rows: list[dict[str, Any]], coverage: dict[str, RunCoverage]
) -> str:
    """Render the verifier-coverage disclosure.

    Args:
        rows: The worklist rows.
        coverage: Per-run verifier-manifest surveys.

    Returns:
        The Markdown document.
    """
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
        *generated_doc_banner(
            "original publication; the K = 1 plan and its disclosure",
            "scripts/build_k1_gapfill_worklist.py",
        ),
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
        "The minimum in THAT stage's manifest is the floor of coverage for the",
        "cells it produced.",
        "",
        "**Only verified cells carry a citation.** A consensus cell has no",
        "verifier stage, so any manifest attributed to it is a false evidence",
        "path. Forty-one such rows were published before this was noticed, every",
        "one of them pointing at some other lineage's stage.",
        "",
        "**A pool that verified in its own subtree owns those stages.** Run-level",
        "stages belong to whichever lineage built them. In `pv-diag-384` they",
        "belong to different pools entirely: `verified/image-6of10` cropped",
        "`consensus/image-1of10.geojson`, while the",
        "`flash-high-image-n5/image-t1.0` pool cropped its own",
        "`image-t1.0/consensus/consensus_t1.geojson`. Both are image, both carry",
        "the shell, so token scoring cannot separate them; containment in the",
        "pool directory decides it.",
        "",
        "One apparent exception was checked and is not one. `h8-v2`'s",
        "WBF-verified cells cite `outputs/h8-v2/wbf/scale-4/crops/`, outside the",
        "`scale-4` proposer-pool directory. The recorded sources settle it: that",
        "stage cropped `wbf_candidates.geojson` while the in-pool stage cropped",
        "`consensus_t1.geojson`, so the WBF stage IS the right one for a",
        "WBF-verified cell. The pool-subtree rule therefore runs after the",
        "fusion-family filter, never before it.",
        "",
        "**Coverage is a property of a verifier STAGE, not of a run.** An earlier",
        "build of this worklist took the minimum across every manifest in a run",
        "and published it per condition. That is wrong wherever a run verified",
        "several shells: `verifier-robustness` ran a vote >= 1 union stage",
        "alongside three vote >= 3 stages and one vote >= 16 stage, so the",
        "run-wide minimum of 1 declared a K = 1 PV anchor derivable for cells",
        "whose verifier never saw a candidate below vote 3, citing as evidence a",
        "manifest belonging to a different condition. Each cell is now matched to",
        "its own stage, and `verifier_floor_basis` names the rule that matched",
        "it; a cell that cannot be matched is disclosed as unmeasurable rather",
        "than given the run minimum.",
        "",
        "The `Manifest` column is the evidence path: thirty-one stages share a",
        "source-set name, so the source alone does not identify which stage a",
        "floor was measured on.",
        "",
        "| Run | Manifest | Source set | Floor (`vote_count` >=) | Cropped |",
        "|---|---|---|---:|---:|",
    ]
    for run_id in sorted(coverage):
        for manifest in coverage[run_id].manifests:
            lines.append(
                f"| `{run_id}` | `{manifest.path}` "
                f"| `{manifest.source_basename or '—'}` "
                f"| {manifest.min_vote} | {manifest.n_candidates} |"
            )

    skipped_total = sum(len(c.skipped) for c in coverage.values())
    lines += [
        "",
        f"**{skipped_total} candidate manifest(s) were excluded from the",
        "measurement.** A silently dropped manifest can RAISE a measured floor",
        "and flip a verdict, so every exclusion is listed with its ground:",
        "",
    ]
    if skipped_total:
        lines += ["| Manifest | Ground |", "|---|---|"]
        for run_id in sorted(coverage):
            for entry in coverage[run_id].skipped:
                path, _, ground = entry.partition(": ")
                lines.append(f"| `{path}` | {ground} |")
    else:
        lines.append("None — every manifest under every run was read.")

    lines += [
        "",
        f"**{len(blocked_by_verifier)} verified cell(s) have no derivable",
        "with-verifier N = 1 anchor.** They are disclosed, not approximated: no",
        "substitute is computed, and the supplement's verified-cell uplift column",
        "is left empty rather than filled with a number the corpus cannot",
        "support. Their no-verifier N = 1 jobs still run, and carry the",
        "consensus-uplift signal for those pools.",
        "",
        "A floor of 1 means that stage processed the full vote >= 1 union, so a",
        "K = 1 WITH-verifier cell IS derivable from it — the modern stride, grid,",
        "and image campaigns, whose ladder rungs are in several cases already",
        "registered.",
        "",
        "**Refinement on the card.** The card records the block as a",
        "\"vote >= 3 shells\" phenomenon. Measured per stage, the floors are not",
        "uniform:",
        "",
        "| Measured floor | Verifier stages |",
        "|---:|---:|",
        *[
            f"| vote_count >= {value} | {count} |"
            for value, count in sorted(
                Counter(
                    manifest.min_vote
                    for entry in coverage.values()
                    for manifest in entry.manifests
                ).items()
            )
        ],
        "",
        "The per-stage numbers in the table above are the ones to quote; a single",
        "corpus-wide threshold would be wrong for some stages in both directions.",
        "",
        "## A judgement call: K-pass union floors cited for lower rungs",
        "",
        "Eight stride-55map ladder rungs at N = 3 and N = 5 have no verifier",
        "stage of their own: the campaign cropped the vote >= 1 union of all ten",
        "passes once, and the lower rungs were derived from those probabilities.",
        "Their `verifier_floor_basis` therefore ends `-via-union_k10-superset`.",
        "",
        "The inference this licenses, stated so a reader can reject it: every",
        "candidate in the first-N union also appears in the K-pass union, since",
        "appearing in at least one of N passes implies appearing in at least one",
        "of K >= N. The K-pass crop set is therefore a SUPERSET of the rung's, so",
        "a floor of 1 there means the verifier did see every candidate the rung",
        "could contain. What it does NOT give is a vote count expressed out of N:",
        "the recorded counts are out of K, and no rung-level shell was measured.",
        "The rows carry the basis string so this can be filtered out of any",
        "analysis that wants only directly measured stages.",
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
        f"### {ORIGINAL_PUBLICATION_DATE} — Original publication",
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
    rows, coverage = build_worklist(sources)

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
        render_disclosure(rows, coverage), encoding="utf-8"
    )

    counts = Counter(r["status"] for r in rows)
    print(f"k1-gapfill-worklist.csv   {len(rows):>4} rows")
    for status, count in sorted(counts.items()):
        print(f"  {status:<20} {count:>4}")
    print(f"written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
