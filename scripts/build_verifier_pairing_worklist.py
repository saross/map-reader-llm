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
Nine rules, in descending order of authority, each recorded in
``pairing_basis``:

``registered``
    A sibling condition already in the registry sharing the verified cell's run,
    pool, geometry, reference, frame, fusion family, N, and vote threshold, with
    no verifier. Nothing to score — it already has metrics. Its stratum is then
    keyed from ITS OWN evidence, not inherited, so the cross-stratum guard
    downstream has two independently derived ids to compare.
``consensus-file``
    A committed consensus GeoJSON at that vote threshold under the pool
    (``consensus_t<k>.geojson`` or ``consensus-<k>of<N>.geojson``). Accepted only
    when the pool's committed pass count equals N, because the sweep's
    denominator is implicit in the filename.
``union``
    The committed vote >= 1 union over the N passes. The paired shell has to be
    filtered out of it first; ``materialise_filter`` records the predicate.
``crop-manifest``
    The candidate universe the cell's verifier actually cropped, recorded by
    the run under a directory named for the cell's own registered
    ``proposer_pool``. Used only when the consensus-file route was AMBIGUOUS —
    several committed consensus sets at that vote threshold sit under a run
    tree serving many lineages and none carries the cell's tokens — because in
    that case the run's consensus files cannot be attributed but the pool's
    crop manifest can: the pool is named for its vote >= 1 shell
    (``<lineage>-1of<N>``) and the manifest under that exact name is that
    lineage's candidate universe, not a guess about which consensus file
    belongs to whom. The twin is the shell ``vote_count >= k`` of it, built by
    ``scripts/materialise_pairing_twin.py --crop-manifest``. Ranked BELOW a
    registered twin and below an unambiguous consensus file, and never used to
    override either. PI ruling 2026-09-10.
The next four fire only on the ABSENCE refusal — nothing under the run names
the cell's shell — and are ranked below every rule above them (PI ruling
2026-09-11). "No consensus GeoJSON at that threshold" is not the same as "no
recorded candidate universe", and each of these reads an attribution the corpus
already made rather than inferring one:

``source-run-consensus`` / ``source-run-union``
    The condition row itself names another run as its proposer's home
    (``source_run``), so the consensus-file and union searches run under THAT
    run's tree. The attribution is the register's.
``stage-manifest``
    The candidate universe the cell's OWN verifier stage cropped, located by
    the same lineage matcher the union rule cross-checks with, or — when token
    matching is ambiguous — by the manifest's recorded ``source_geojson``
    naming the cell's pool. Accepted only when the manifest counts votes over
    the cell's N and starts at or below the cell's k: vote shells NEST, so its
    ``vote_count >= k`` subset then IS the pre-verifier shell rather than an
    approximation of it.
``shell-manifests``
    The universe is recorded across two files — a base manifest and a committed
    increment that cropped and verified the shell below it (the S104 vote-3
    increment, ``_INCREMENT_ROOTS``). Accepted only when the two shells are
    disjoint and join into an unbroken range reaching k; the twin is their
    union. ``scripts/final_board_sweeps.py`` makes and gates the same join.
``single-pass-manifest``
    ``N = 1``, where the pool ran one proposer pass and so recorded no
    ``vote_count`` at all. The shell at ``k = 1`` is the whole universe, and
    the twin differs from its verified pair in the probability filter alone.
    Fires at ``N = 1, k = 1`` only.

``unresolved``
    Nothing committed matches. Recorded as blocked with the reason, never
    substituted. Every rule's refusal is joined into that reason, so a reader
    sees what was tried.

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
import re
import shlex
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_detection_paths import (  # noqa: E402
    AmbiguousPassError,
    PassCountMismatch,
    resolve_pool_passes,
)
from scripts.lib_uplift_supplement import (
    is_board_frame_condition,  # noqa: E402
    ORIGINAL_PUBLICATION_DATE,
    SHELL_EPILOGUE,
    SHELL_PREAMBLE,
    CorpusSources,
    ScoringRecipe,
    VerifierManifest,
    collect_verifier_manifests,
    condition_stratum,
    generated_doc_banner,
    iter_condition_specs,
    match_verifier_manifest,
    path_matches_lineage,
    read_scoring_recipe,
    resolve_geometry,
    resolve_reference,
    resolve_scope,
    write_csv,
)

DEFAULT_OUT_DIR = Path("results/uplift-supplement")

#: Bases whose twin is a committed GeoJSON scoreable as it stands.
_CONSENSUS_FILE_BASES = ("consensus-file", "source-run-consensus")
#: Bases whose twin is the vote shell of one or more candidate manifests.
_MANIFEST_BASES = ("crop-manifest", "stage-manifest", "shell-manifests",
                   "single-pass-manifest")

WORKLIST_COLUMNS: tuple[str, ...] = (
    "job_id", "verified_condition_id", "run_id", "proposer_pool",
    "verified_stratum_id", "unverified_stratum_id", "unverified_stratum_basis",
    "corpus", "reference", "buffer_m", "frame_id",
    "N", "min_votes", "prob_t",
    "status", "pairing_basis", "blocked_reason",
    "unverified_condition_id", "unverified_detections_path",
    "unverified_eval_path", "union_path", "crop_manifest_path", "materialise_filter",
    "reference_path", "bounds_path", "engine", "output_dir",
    "materialise_command", "command",
    "notes",
)


def _find_consensus_file(
    pool_dir: Path | None,
    run_dir: Path | None,
    votes: int,
    n_passes: int,
    discriminators: Sequence[str] = (),
    n_lineages: int = 1,
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
        n_lineages: How many distinct (pool, geometry) lineages the run
            registers. A lone glob hit is unambiguous only when the run has one
            lineage for it to belong to; where the run has several, the hit must
            positively carry this cell's tokens.

    Returns:
        ``(path, rejection_reason)``. The reason is populated only when a
        candidate was found and deliberately refused.
    """
    tokens = [t for t in discriminators if t]
    for root, scope in ((pool_dir, "pool"), (run_dir, "run")):
        if root is None or not root.is_dir():
            continue
        explicit = sorted(
            {
                *root.glob(f"consensus/*-{votes}of{n_passes}.geojson"),
                *root.glob(f"*/consensus/*-{votes}of{n_passes}.geojson"),
            }
        )
        if not explicit:
            continue
        # A single glob hit is self-evident only in a single-lineage run. In a
        # multi-lineage run it is merely the only file with that vote SHAPE
        # anywhere in the tree, which is how three pv-diag-384 cells — text,
        # image, and text-min, on three different pools — all resolved to one
        # text consensus set and were emitted as ready scoring jobs. The pool
        # tree gets no exemption: a pool directory can serve several
        # geometries, so "under the pool" is not by itself proof of lineage.
        if len(explicit) == 1 and n_lineages <= 1:
            return explicit[0], None
        # Lineage matching is boundary-anchored (whole path segment or stem,
        # each also shell-stripped). Bare containment both invents matches —
        # `text-1of10` inside `flash-high-text-1of10` — and misses real ones,
        # because a pool is named for the shell it was BUILT at while its
        # consensus set is named for the shell it was AGGREGATED at.
        matched = [p for p in explicit if path_matches_lineage(str(p), tokens)]
        if len(matched) == 1:
            return matched[0], None
        if not matched:
            return None, (
                f"{len(explicit)} committed {votes}-of-{n_passes} consensus "
                f"set(s) sit under the {scope} tree, which serves "
                f"{n_lineages} distinct pool/geometry lineages, and none "
                f"carries this cell's tokens "
                f"({', '.join(tokens) or 'no tokens resolved'}). None can be "
                "shown to be the set its verifier consumed; refused rather "
                "than guessed"
            )
        return None, (
            f"{len(matched)} committed {votes}-of-{n_passes} consensus sets "
            f"under the {scope} tree carry this cell's lineage, and no token "
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
    run_dir: Path,
    discriminators: Sequence[str],
    n_passes: int,
    n_lineages: int = 1,
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
        n_lineages: How many distinct (pool, geometry) lineages the run
            registers.

    Returns:
        The union file, or ``None`` when no unambiguous match exists.
    """
    candidates = sorted(run_dir.rglob(f"union_k{n_passes}.geojson"))
    if not candidates:
        return None
    tokens = [t for t in discriminators if t]
    matched = [c for c in candidates if path_matches_lineage(str(c), tokens)]
    if len(matched) == 1:
        return matched[0]
    # A lone union is accepted only when the run has one lineage for it to
    # belong to. "It was the only file" is not, by itself, evidence that it is
    # the RIGHT file.
    if len(candidates) == 1 and n_lineages <= 1:
        return candidates[0]
    return None


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


def _projected_without_crs(path: Path) -> bool:
    """Whether a GeoJSON has no crs member and coordinates outside the degree range.

    Such a file is read as WGS84 by RFC 7946 readers, so projected metre
    coordinates land in the wrong hemisphere and every match fails.
    """
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if document.get("crs"):
        return False
    for feature in document.get("features") or []:
        coords = (feature.get("geometry") or {}).get("coordinates")
        while isinstance(coords, list) and coords and isinstance(coords[0], list):
            coords = coords[0]
        if isinstance(coords, list) and len(coords) >= 2:
            return abs(float(coords[0])) > 180 or abs(float(coords[1])) > 90
    return False


#: Directories, in order of preference, under a run tree that hold one
#: candidate manifest per proposer-pool lineage.
_POOL_MANIFEST_DIRS: tuple[str, ...] = ("crops", "verified")
_POOL_SHELL_RE = re.compile(r"^(?P<stem>.+)-(?P<k>\d+)of(?P<n>\d+)$")


def _find_pool_crop_manifest(
    run_dir: Path | None, pool: str, n_passes: int, votes: int, repo_root: Path
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """Locate the candidate universe the cell's own verifier lineage cropped.

    The consensus-file route asks "which committed consensus set at vote >= k
    belongs to this cell?" and refuses when a run tree serving many lineages
    offers several and none carries the cell's tokens. This route asks a
    different, answerable question: the cell's REGISTERED ``proposer_pool``
    names its lineage at the vote >= 1 shell (``<lineage>-1of<N>``), and the
    run records one candidate manifest per lineage under a directory of exactly
    that name. That is an attribution the registry already made, not one this
    script infers, so it resolves the ambiguity without guessing.

    Only a vote >= 1 pool qualifies. A pool named for a higher shell has
    already had the vote filter applied, so filtering it again at k would
    silently compare two different universes; and N must equal the cell's, or
    the manifest belongs to a different rung of the ladder.

    Args:
        run_dir: The run's output directory, if the registry records one.
        pool: The cell's registered ``proposer_pool``.
        n_passes: The cell's N.
        votes: The cell's vote threshold k.
        repo_root: Repository root, so the path is recorded relative.

    Returns:
        ``(path, stats, refusal)``. ``path`` is the repo-relative manifest and
        ``stats`` summarises it (``n_candidates``, ``n_at_threshold``,
        ``min_vote``, ``max_vote``); on failure both are ``None`` and
        ``refusal`` says why.
    """
    if run_dir is None or not run_dir.is_dir() or not pool:
        return None, None, "the registry records no output directory for this run"
    shell = _POOL_SHELL_RE.match(pool)
    if shell is None or int(shell.group("k")) != 1:
        return None, None, (
            f"the pool {pool!r} does not name a vote >= 1 shell, so its crop manifest "
            "is already vote-filtered and cannot be filtered again at this cell's k"
        )
    if int(shell.group("n")) != n_passes:
        return None, None, (
            f"the pool {pool!r} names an N of {shell.group('n')} but the cell records "
            f"{n_passes}; they are different rungs of the pass ladder"
        )
    for sub in _POOL_MANIFEST_DIRS:
        path = run_dir / sub / pool / "candidate_manifest.json"
        if not path.is_file():
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            return None, None, f"{path} is unreadable ({type(error).__name__})"
        candidates = document.get("candidates") or []
        vote_counts = [
            (c.get("properties") or {}).get("vote_count") for c in candidates
        ]
        vote_counts = [v for v in vote_counts if isinstance(v, int)]
        if not vote_counts:
            return None, None, f"{path} records no integer vote_count"
        at_threshold = sum(1 for v in vote_counts if v >= votes)
        if not at_threshold:
            return None, None, (
                f"no candidate in {path} reaches vote_count >= {votes}; the shell is empty"
            )
        return (
            str(path.relative_to(repo_root)),
            {"n_candidates": len(candidates), "n_at_threshold": at_threshold,
             "min_vote": min(vote_counts), "max_vote": max(vote_counts)},
            None,
        )
    tried = ", ".join(f"{sub}/{pool}/candidate_manifest.json" for sub in _POOL_MANIFEST_DIRS)
    return None, None, f"the run records no crop manifest for this pool (tried {tried})"


#: Roots under which a run's committed candidate universe is recorded in a
#: SECOND file. The S104 vote-3 increment cropped and verified the vote == 3
#: shell of three 55-map generalisation runs after their vote >= 4 verification
#: had been committed, so a k = 3 cell of those runs was drawn from the union of
#: the two manifests. ``scripts/final_board_sweeps.py`` (``build_families``)
#: makes exactly that join, gates it on the vote structure, and reproduces the
#: committed k3 cells' detection counts EXACTLY from it — so the attribution is
#: the corpus's, not this script's guess. Keyed by the run's directory basename.
_INCREMENT_ROOTS: tuple[str, ...] = (
    "results/deployment-oracle-2026-06-06/vote3-verify",
)


def _manifest_shape(path: Path) -> dict[str, Any] | None:
    """Read a candidate manifest and summarise its vote structure.

    Args:
        path: A ``candidate_manifest.json``.

    Returns:
        ``{n_candidates, min_vote, max_vote, n_voted, basis, source}`` where
        ``basis`` is the manifest's declared ``total_passes`` when every
        candidate agrees on one, else ``None``. ``None`` is returned when the
        file is unreadable or lists no candidates.
    """
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    candidates = document.get("candidates") or []
    if not candidates:
        return None
    props = [(c.get("properties") or {}) for c in candidates]
    votes = [p.get("vote_count") for p in props]
    votes = [v for v in votes if isinstance(v, int)]
    passes = {p.get("total_passes") for p in props}
    passes = {p for p in passes if isinstance(p, int)}
    return {
        "n_candidates": len(candidates),
        "min_vote": min(votes) if votes else None,
        "max_vote": max(votes) if votes else None,
        "n_voted": len(votes),
        "basis": passes.pop() if len(passes) == 1 else None,
        "source": document.get("source_geojson"),
    }


def _shell_at(path: Path, votes: int) -> int:
    """How many of a manifest's candidates reach ``vote_count >= votes``."""
    document = json.loads(path.read_text(encoding="utf-8"))
    return sum(
        1 for c in (document.get("candidates") or [])
        if isinstance((c.get("properties") or {}).get("vote_count"), int)
        and c["properties"]["vote_count"] >= votes
    )


def _find_single_pass_manifest(
    run_dir: Path | None, pool: str, n_passes: int, votes: int, repo_root: Path
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """Locate the candidate universe of a ONE-pass proposer pool.

    A single-pass pool has no votes to record — every candidate was seen by the
    one pass — so its crop manifest carries no ``vote_count`` at all and every
    vote-shell rule refuses it. At ``N = 1, k = 1`` the shell is nevertheless
    exactly determined: it is the whole universe, and the pair differs from the
    verified cell in the probability filter alone, which is what an uplift
    number needs. This rule fires only in that case; anything else is a shell
    of a universe that does not record shells, and stays refused.

    Args:
        run_dir: The run's output directory.
        pool: The cell's registered ``proposer_pool`` — the manifest lives in a
            directory of exactly that name, an attribution the run recorded.
        n_passes: The cell's N; must be 1.
        votes: The cell's k; must be 1.
        repo_root: Repository root, so the path is recorded relative.

    Returns:
        ``(path, shape, refusal)`` as for :func:`_find_pool_crop_manifest`.
    """
    if n_passes != 1 or votes != 1:
        return None, None, (
            f"the vacuous-shell rule needs N = 1 and k = 1; this cell is "
            f"N = {n_passes}, k = {votes}")
    if run_dir is None or not run_dir.is_dir() or not pool:
        return None, None, "the registry records no output directory for this run"
    for sub in _POOL_MANIFEST_DIRS:
        path = run_dir / sub / pool / "candidate_manifest.json"
        if not path.is_file():
            continue
        shape = _manifest_shape(path)
        if shape is None:
            return None, None, f"{path} lists no candidates"
        if shape["n_voted"]:
            return None, None, (
                f"{path} DOES record vote counts ({shape['min_vote']}-"
                f"{shape['max_vote']}), so it is not a single-pass universe and "
                "the vacuous-shell rule does not apply")
        return str(path.relative_to(repo_root)), shape, None
    tried = ", ".join(f"{sub}/{pool}/candidate_manifest.json" for sub in _POOL_MANIFEST_DIRS)
    return None, None, f"the run records no crop manifest for this pool (tried {tried})"


def _find_shell_manifests(
    run_dir: Path | None, votes: int, n_passes: int, repo_root: Path
) -> tuple[list[str], dict[str, Any] | None, str | None]:
    """Locate a base manifest plus the committed increment that completes it.

    Where a run's committed manifest starts ABOVE the cell's k, the cell was not
    drawn from it alone: a later increment cropped and verified the missing
    shell, and the cell's universe is the union of the two. This rule accepts
    that union only when the shells are DISJOINT and together cover
    ``[k, N]`` — anything else would double-count a candidate or leave a hole,
    and either way the twin would not be the set the verifier saw.

    Args:
        run_dir: The run's output directory.
        votes: The cell's k.
        n_passes: The cell's N.
        repo_root: Repository root.

    Returns:
        ``(paths, stats, refusal)``. ``paths`` is ordered base-then-increment.
    """
    if run_dir is None or not run_dir.is_dir():
        return [], None, "the registry records no output directory for this run"
    base = run_dir / "crops" / "candidate_manifest.json"
    if not base.is_file():
        return [], None, f"the run records no base crop manifest at {base}"
    base_shape = _manifest_shape(base)
    if base_shape is None or base_shape["min_vote"] is None:
        return [], None, f"{base} records no integer vote_count"
    if base_shape["min_vote"] <= votes:
        return [], None, (
            f"{base} already reaches vote_count >= {votes} (floor "
            f"{base_shape['min_vote']}); no increment is needed and the "
            "single-manifest rule applies")
    for root in _INCREMENT_ROOTS:
        increment = repo_root / root / run_dir.name / "crops" / "candidate_manifest.json"
        if not increment.is_file():
            continue
        inc_shape = _manifest_shape(increment)
        if inc_shape is None or inc_shape["min_vote"] is None:
            return [], None, f"{increment} records no integer vote_count"
        if inc_shape["max_vote"] >= base_shape["min_vote"]:
            return [], None, (
                f"the increment {increment} covers votes {inc_shape['min_vote']}-"
                f"{inc_shape['max_vote']} and the base covers "
                f"{base_shape['min_vote']}-{base_shape['max_vote']}; the shells "
                "overlap, so their union would double-count candidates")
        if inc_shape["min_vote"] > votes or inc_shape["max_vote"] + 1 != base_shape["min_vote"]:
            return [], None, (
                f"the increment {increment} covers votes {inc_shape['min_vote']}-"
                f"{inc_shape['max_vote']}, which does not join the base's floor "
                f"{base_shape['min_vote']} into an unbroken shell reaching this "
                f"cell's k = {votes}")
        return (
            [str(base.relative_to(repo_root)), str(increment.relative_to(repo_root))],
            {"n_base": base_shape["n_candidates"], "n_increment": inc_shape["n_candidates"],
             "n_candidates": base_shape["n_candidates"] + inc_shape["n_candidates"],
             "base_votes": [base_shape["min_vote"], base_shape["max_vote"]],
             "increment_votes": [inc_shape["min_vote"], inc_shape["max_vote"]],
             "n_at_threshold": _shell_at(base, votes) + _shell_at(increment, votes)},
            None,
        )
    tried = ", ".join(f"{r}/{run_dir.name}/crops/candidate_manifest.json"
                      for r in _INCREMENT_ROOTS)
    return [], None, (
        f"{base} starts at vote_count >= {base_shape['min_vote']}, above this "
        f"cell's k = {votes}, and no committed increment supplies the missing "
        f"shell (tried {tried})")


@dataclass
class RecordedUniverse:
    """One resolution of the absence refusal.

    Attributes:
        basis: The ``pairing_basis`` to record, or ``""`` when unresolved.
        manifests: Candidate manifests forming the universe, base first.
        union: A committed union GeoJSON, when that is the universe.
        consensus: A committed consensus GeoJSON scoreable as-is.
        materialise_filter: The predicate recorded in the worklist.
        notes: Lines appended to the row's ``notes``.
        refusal: Why nothing resolved, when ``basis`` is empty — every rule's
            reason, joined, so a reader can see what was tried.
    """

    basis: str = ""
    manifests: list[str] = field(default_factory=list)
    union: str | None = None
    consensus: str | None = None
    materialise_filter: str | None = None
    notes: list[str] = field(default_factory=list)
    refusal: str = ""


def _find_stage_manifest(
    sources: CorpusSources,
    spec: Mapping[str, Any],
    run_id: str,
    pool: str,
    geometry: str | None,
    n_passes: int,
    votes: int,
    lineages: Mapping[str, set],
    coverage: dict[str, list[VerifierManifest]],
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """The candidate universe the cell's OWN verifier stage cropped.

    Vote shells nest: a universe counted over N passes and recorded from its
    ``j of N`` floor contains every candidate at ``vote_count >= k`` for any
    ``k >= j``, and nothing else. So when the cell's own stage manifest is
    counted over the cell's N and starts at or below the cell's k, its
    ``vote_count >= k`` subset IS the pre-verifier shell — not an approximation
    of it. Both conditions are checked, because a manifest counted over a
    different N is a different rung of the ladder and one that starts above k
    cannot reach the shell at all.

    Args:
        sources: Loaded corpus sources.
        spec: The verified condition's registered row.
        run_id: Its run.
        pool: Its proposer pool.
        geometry: Its geometry cell, where resolved.
        n_passes: N.
        votes: k.
        lineages: Every run's registered (pool, geometry) lineages.
        coverage: Per-run manifest survey cache.

    Returns:
        ``(path, stats, refusal)``.
    """
    stage, stage_basis = match_verifier_manifest(
        _run_manifests(sources, run_id, coverage),
        spec["label"], pool, geometry, n_passes,
        siblings=sorted(lineages.get(run_id, set())),
        pool_dir=None,
    )
    if stage is None:
        # Second attribution, used only when token matching is ambiguous: a
        # manifest RECORDS the set it cropped in ``source_geojson``, and where
        # exactly one of the run's manifests names this cell's pool there, the
        # run itself has said which universe belongs to the lineage. That is
        # the same argument the crop-manifest rule makes about directory names,
        # read off the manifest's own field instead of its path.
        named = [
            m for m in _run_manifests(sources, run_id, coverage)
            if Path(m.source_basename).stem == pool
            or Path(m.source_basename).stem.startswith(f"{pool}-")
        ]
        if len(named) != 1:
            return None, None, (
                f"no verifier stage could be matched to this cell ({stage_basis}), "
                f"and {len(named)} of the run's manifests record a source_geojson "
                f"naming the pool {pool!r}, so no manifest can be shown to be the "
                "universe its verifier saw")
        stage, stage_basis = named[0], "matched-manifest-source-geojson"
    shape = _manifest_shape(sources.repo_root / stage.path)
    if shape is None or shape["min_vote"] is None:
        return None, None, f"{stage.path} records no integer vote_count"
    basis = shape["basis"] if shape["basis"] is not None else shape["max_vote"]
    if basis != n_passes:
        return None, None, (
            f"{stage.path} counts votes over {basis} pass(es) but the cell "
            f"consumed N = {n_passes}; they are different rungs of the pass "
            "ladder, so its shell at k is a different universe")
    if shape["min_vote"] > votes:
        return None, None, (
            f"{stage.path} starts at vote_count >= {shape['min_vote']}, above "
            f"this cell's k = {votes}: the shell it would yield is the "
            "manifest's own floor, not the cell's")
    stats = dict(shape)
    stats["match_basis"] = stage_basis
    stats["n_at_threshold"] = _shell_at(sources.repo_root / stage.path, votes)
    return stage.path, stats, None


def _find_recorded_universe(
    sources: CorpusSources,
    spec: Mapping[str, Any],
    run_id: str,
    pool: str,
    geometry: str | None,
    n_passes: int,
    votes: int,
    lineages: Mapping[str, set],
    coverage: dict[str, list[VerifierManifest]],
) -> RecordedUniverse:
    """Resolve the absence refusal, or say what every rule refused.

    Ordered by the strength of the attribution: a run the REGISTRY names as the
    proposer's home first, then the cell's own verifier stage, then a universe
    recorded across two files, then the vacuous single-pass shell.

    Args:
        sources: Loaded corpus sources.
        spec: The verified condition's registered row.
        run_id: Its run.
        pool: Its proposer pool.
        geometry: Its geometry cell, where resolved.
        n_passes: N.
        votes: k.
        lineages: Every run's registered (pool, geometry) lineages.
        coverage: Per-run manifest survey cache.

    Returns:
        A :class:`RecordedUniverse`.
    """
    refusals: list[str] = []

    source_run = spec.get("source_run")
    if source_run:
        entry = sources.registry.get(source_run)
        other_dir = sources.repo_root / entry["directory_path"] if entry else None
        if other_dir is None or not other_dir.is_dir():
            refusals.append(
                f"source-run: the row names {source_run!r} as its proposer's home "
                "but the registry records no readable directory for it")
        else:
            other_pool = sources.pool_directory(source_run, pool)
            found, why = _find_consensus_file(
                other_pool, other_dir, votes, n_passes,
                (geometry or "", pool), len(lineages.get(source_run, {("", None)})),
            )
            if found is not None:
                return RecordedUniverse(
                    basis="source-run-consensus",
                    consensus=str(found.relative_to(sources.repo_root)),
                    notes=[
                        f"the row records source_run {source_run!r}, so the "
                        "pre-verifier set was looked for under THAT run — the "
                        "attribution is the register's, not this script's",
                        f"twin is the committed {votes}-of-{n_passes} consensus "
                        f"set {found.relative_to(sources.repo_root)}",
                    ],
                )
            union = _find_union(other_dir, (geometry or "", pool), n_passes,
                                len(lineages.get(source_run, {("", None)})))
            if union is not None:
                return RecordedUniverse(
                    basis="source-run-union",
                    union=str(union.relative_to(sources.repo_root)),
                    materialise_filter=f"vote_count >= {votes}",
                    notes=[f"the row records source_run {source_run!r}; the twin is "
                           f"the vote >= {votes} shell of that run's committed union"],
                )
            refusals.append(
                f"source-run: nothing under {source_run} names a "
                f"{votes}-of-{n_passes} set either ({why or 'no candidate found'})")

    path, stats, why = _find_stage_manifest(
        sources, spec, run_id, pool, geometry, n_passes, votes, lineages, coverage)
    if path is not None:
        return RecordedUniverse(
            basis="stage-manifest",
            manifests=[path],
            materialise_filter=f"vote_count >= {votes}",
            notes=[
                "no committed consensus set names this cell's shell, so the twin "
                f"is the vote >= {votes} shell of the candidate universe its own "
                f"verifier stage cropped ({path}: {stats['n_candidates']} "
                f"candidates over {n_passes} pass(es), votes "
                f"{stats['min_vote']}-{stats['max_vote']}, "
                f"{stats['n_at_threshold']} at vote >= {votes}; matched "
                f"{stats['match_basis']}). Vote shells nest, so this subset IS "
                "the shell, not an approximation of it",
            ],
        )
    refusals.append(f"stage-manifest: {why}")

    paths, stats, why = _find_shell_manifests(
        sources.repo_root / sources.registry[run_id]["directory_path"]
        if run_id in sources.registry else None,
        votes, n_passes, sources.repo_root)
    if paths:
        return RecordedUniverse(
            basis="shell-manifests",
            manifests=paths,
            materialise_filter=f"vote_count >= {votes}",
            notes=[
                f"the run's candidate universe is recorded in two files: the base "
                f"manifest at votes {stats['base_votes'][0]}-{stats['base_votes'][1]} "
                f"({stats['n_base']}) and the committed increment at votes "
                f"{stats['increment_votes'][0]}-{stats['increment_votes'][1]} "
                f"({stats['n_increment']}). The shells are disjoint and join into "
                f"an unbroken range reaching k = {votes}, so the twin is their "
                f"union at vote >= {votes} ({stats['n_at_threshold']} candidates)",
                "the same join scripts/final_board_sweeps.py makes and gates for "
                "this run's sweep space",
            ],
        )
    refusals.append(f"shell-manifests: {why}")

    path, shape, why = _find_single_pass_manifest(
        sources.repo_root / sources.registry[run_id]["directory_path"]
        if run_id in sources.registry else None,
        pool, n_passes, votes, sources.repo_root)
    if path is not None:
        return RecordedUniverse(
            basis="single-pass-manifest",
            manifests=[path],
            materialise_filter="none (N = 1: every candidate has the one vote)",
            notes=[
                f"the pool ran a single proposer pass, so its manifest records no "
                f"vote_count and the shell at k = 1 is the whole universe "
                f"({path}: {shape['n_candidates']} candidates). The twin differs "
                "from its verified pair in the probability filter alone",
            ],
        )
    refusals.append(f"single-pass: {why}")

    return RecordedUniverse(refusal="; ".join(refusals))


def _has_source_tile(path: Path) -> bool:
    """Whether a detection GeoJSON carries a singular per-feature ``source_tile``.

    The corrected-F1 engine scopes detections per map sheet with
    ``gdf_det["source_tile"].str.startswith(map_name)``, so the column's absence
    is a hard failure rather than a degraded result. Checked by reading the
    file, because the committed corpus mixes both shapes: verified sets carry
    ``source_tile`` and consensus sets carry ``source_tiles``.

    Args:
        path: The detection GeoJSON.

    Returns:
        True when the first feature carries the singular key.
    """
    if not path.exists():
        return False
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    features = document.get("features") or []
    if not features:
        return False
    return "source_tile" in (features[0].get("properties") or {})


def _run_manifests(
    sources: CorpusSources, run_id: str, cache: dict[str, list[VerifierManifest]]
) -> list[VerifierManifest]:
    """Return a run's verifier manifests, surveying it at most once.

    Args:
        sources: Loaded corpus sources.
        run_id: The run.
        cache: Per-run survey cache, mutated in place.

    Returns:
        The run's real candidate manifests.
    """
    if run_id not in cache:
        entry = sources.registry.get(run_id)
        run_dir = sources.repo_root / entry["directory_path"] if entry else None
        if run_dir is not None and run_dir.is_dir():
            cache[run_id] = collect_verifier_manifests(run_dir, sources.repo_root)[0]
        else:
            cache[run_id] = []
    return cache[run_id]


def _eval_metadata(
    sources: CorpusSources, spec: Mapping[str, Any]
) -> dict[str, Any] | None:
    """Read a condition's evaluation ``_metadata`` block, if it has one.

    Args:
        sources: Loaded corpus sources.
        spec: The condition spec.

    Returns:
        The ``_metadata`` block, or ``None`` when no evaluation is readable.
    """
    eval_path = spec.get("eval_path")
    if not eval_path:
        return None
    path = sources.repo_root / str(eval_path)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("_metadata")


def build_worklist(sources: CorpusSources) -> list[dict[str, Any]]:
    """Pair every verified cell with its pre-verifier twin.

    Args:
        sources: Loaded corpus sources.

    Returns:
        One row per verified condition in the registry.
    """
    specs = list(iter_condition_specs(sources))
    # Board-frame rows (the GS Era-2 board's -era2b and -opmax rows) are board
    # artefacts, not measurements of their own: excluded by rule, both as
    # verified cells to pair and as candidate registered twins.
    sources.excluded_board_frame = [
        condition_id for _, condition_id, spec in specs if is_board_frame_condition(spec)
    ]
    specs = [s for s in specs if not is_board_frame_condition(s[2])]

    def _pair_key(
        run: str, condition: str, spec: dict[str, Any]
    ) -> tuple[Any, ...]:
        """Build the identity a verified cell and its twin must share.

        Pool + N + vote threshold is not enough on its own. The grid campaign's
        four geometries all draw on a pool named ``brief-text``, so without the
        geometry a 384/50 % verified cell pairs happily with a 384/12.5 %
        consensus cell — a mis-pairing that yields a plausible, wrong uplift.
        The fusion family matters for the same reason: h8-v2 registers greedy
        and WBF aggregations of the same passes, and a WBF-verified cell must be
        paired with the WBF consensus, not the greedy one.

        The REFERENCE is in the key too. Several 55-map cells are registered
        once per reference — ``-canonical-gt`` and ``-standardised-gt`` variants
        of the same detections — and pairing across those compares two
        different ground truths while calling the difference a verifier effect.
        """
        facts = sources.facts.get(run, {})
        geometry = resolve_geometry(
            spec.get("proposer_pool"), spec["label"], facts.get("tile_size_px")
        )["geometry"]
        reference = resolve_reference(
            _eval_metadata(sources, spec), spec["label"], facts.get("gt_reference")
        )
        return (
            run,
            spec.get("proposer_pool") or "",
            geometry,
            reference.term,
            resolve_scope(sources, run, condition).get("test_set_id"),
            "wbf" if "wbf" in spec["label"] else "greedy",
            int(spec["n_passes"]),
            spec.get("vote_threshold"),
        )

    registered: dict[tuple[Any, ...], tuple[str, dict[str, Any]]] = {}
    lineages: dict[str, set[tuple[str, str | None]]] = {}
    for run_id, condition_id, spec in specs:
        facts = sources.facts.get(run_id, {})
        lineages.setdefault(run_id, set()).add((
            spec.get("proposer_pool") or "",
            resolve_geometry(
                spec.get("proposer_pool"), spec["label"], facts.get("tile_size_px")
            )["geometry"],
        ))
        if spec.get("aggregation") in {"consensus", "greedy", "wbf"}:
            registered.setdefault(
                _pair_key(run_id, condition_id, spec), (condition_id, spec)
            )

    coverage: dict[str, list[VerifierManifest]] = {}
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
        stratum, reference, scope = condition_stratum(
            sources, run_id, condition_id, spec, (document or {}).get("_metadata")
        )
        corpus = facts.get("corpus")
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
        matched_stage = None
        crop_manifest_path: str | None = None
        extra_manifests: list[str] = []
        notes: list[str] = []

        # The twin's stratum is keyed INDEPENDENTLY, so the cross-stratum guard
        # downstream has two separately derived ids to compare. Passing the
        # verified cell's id twice — which an earlier build did — makes the
        # guard tautological: it can never fire, on any input.
        twin_stratum = stratum
        twin_stratum_basis = (
            "same-recipe-by-construction: the twin is scored with the verified "
            "cell's own recorded recipe, so its reference, buffer, and frame "
            "are that cell's by construction"
        )

        geometry = resolve_geometry(
            pool, spec["label"], facts.get("tile_size_px")
        )["geometry"]
        sibling = registered.get(_pair_key(run_id, condition_id, spec))
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
            # A registered twin is a condition in its own right, so its stratum
            # is derived from ITS evidence — its own evaluation's ground truth
            # and its own scope override — not inherited from the verified cell.
            twin_stratum, _twin_reference, _twin_scope = condition_stratum(
                sources, twin_id.split("::", 1)[0], twin_id, twin_spec,
                _eval_metadata(sources, twin_spec),
            )
            twin_stratum_basis = "derived-from-twin-cell"
            notes.append("the pre-verifier twin is already scored and registered")
        else:
            n_lineages = len(lineages.get(run_id, {("", None)}))
            found, refusal = _find_consensus_file(
                pool_dir, run_dir, int(votes), n_passes,
                (geometry or "", pool), n_lineages,
            )
            if found is not None:
                basis = "consensus-file"
                twin_detections = str(found.relative_to(sources.repo_root))
            elif run_dir is not None and run_dir.is_dir():
                union = _find_union(
                    run_dir, (geometry or "", pool), n_passes, n_lineages
                )
                if union is not None:
                    # The union must be the SAME set the verifier consumed, or
                    # the "pair" differs in two things at once. The verifier
                    # stage records what it cropped in its candidate manifest,
                    # so the claim is checkable rather than asserted.
                    matched_stage, _stage_basis = match_verifier_manifest(
                        _run_manifests(sources, run_id, coverage),
                        spec["label"], pool, geometry, n_passes,
                    )
                    recorded = matched_stage.source_basename if matched_stage else None
                    if recorded and recorded != union.name:
                        blocked = (
                            f"the committed union {union.name} is not the set "
                            f"this cell's verifier consumed: its stage "
                            f"({matched_stage.path}) records "
                            f"source_geojson {recorded}. Pairing them would "
                            "differ in the candidate set as well as the "
                            "verifier. Refused rather than assumed"
                        )
                    else:
                        basis = "union"
                        union_path = str(union.relative_to(sources.repo_root))
                        materialise_filter = f"vote_count >= {int(votes)}"
                        notes.append(
                            "the paired shell must be filtered out of the union "
                            "before scoring; no API spend, no re-aggregation"
                        )
                        notes.append(
                            f"union cross-checked against {matched_stage.path}"
                            if matched_stage
                            else "no verifier stage matched, so the union could "
                                 "not be cross-checked against a recorded source"
                        )

            if basis == "unresolved" and refusal:
                # The consensus-file route was AMBIGUOUS, not empty: committed
                # sets at this vote threshold exist but cannot be attributed to
                # this cell. The pool's own crop manifest can be, so ask that
                # instead of blocking (PI ruling 2026-09-10). Only for an
                # ambiguity — where nothing was found at all, the run has no
                # pre-verifier set and blocking is still the right answer.
                crop_path, crop_stats, crop_refusal = _find_pool_crop_manifest(
                    run_dir, pool, n_passes, int(votes), sources.repo_root,
                )
                if crop_path is not None:
                    basis = "crop-manifest"
                    crop_manifest_path = crop_path
                    materialise_filter = f"vote_count >= {int(votes)}"
                    notes.append(
                        "consensus-file route ambiguous, so the twin is the vote shell of "
                        f"the candidate universe this cell's own pool cropped ({crop_path}: "
                        f"{crop_stats['n_candidates']} candidates, votes "
                        f"{crop_stats['min_vote']}-{crop_stats['max_vote']}, "
                        f"{crop_stats['n_at_threshold']} at vote >= {int(votes)})"
                    )
                    notes.append(f"consensus-file route refused because: {refusal}")
                else:
                    blocked = f"{refusal} — and {crop_refusal}"

            if basis == "unresolved" and blocked is None:
                # The ABSENCE refusal (PI ruling 2026-09-11). Nothing under the
                # run names the cell's shell — but "no consensus GeoJSON at that
                # threshold" is not the same as "no recorded candidate
                # universe". Three further places the corpus records one, each
                # an attribution the corpus already made:
                #
                #   source-run       the row names another run as its proposer's
                #                    home, so the search runs THERE;
                #   stage-manifest   the cell's own verifier stage cropped a
                #                    manifest whose vote basis is N — the shell
                #                    at k is exactly its `vote_count >= k`
                #                    subset, because vote shells nest;
                #   shell-manifests  the universe is recorded in two files, a
                #                    base and a committed increment;
                #   single-pass      N = 1, so the shell is the whole universe.
                #
                # All rank BELOW a registered twin, a consensus file and a
                # union, and never override one.
                found = _find_recorded_universe(
                    sources, spec, run_id, pool, geometry, n_passes, int(votes),
                    lineages, coverage,
                )
                if found.basis:
                    basis = found.basis
                    twin_detections = found.consensus
                    union_path = found.union
                    crop_manifest_path = found.manifests[0] if found.manifests else None
                    extra_manifests = found.manifests[1:]
                    materialise_filter = found.materialise_filter
                    notes += found.notes
                else:
                    blocked = (
                        "no committed pre-verifier set was found for "
                        f"(run={run_id}, pool={pool!r}, N={n_passes}, k={votes}): "
                        "the registry holds no consensus sibling, no consensus "
                        "GeoJSON names that threshold under the pool or run tree, "
                        "and the run holds no vote >= 1 union over N passes"
                        f" — and {found.refusal}"
                    )

            if basis == "unresolved":
                blocked = blocked or refusal or (
                    "no committed pre-verifier set was found for "
                    f"(run={run_id}, pool={pool!r}, N={n_passes}, k={votes}): "
                    "the registry holds no consensus sibling, no consensus "
                    "GeoJSON names that threshold under the pool or run tree, "
                    "and the run holds no vote >= 1 union over N passes"
                )
            elif recipe is None:
                status, blocked = "blocked", recipe_problem
            else:
                status = ("ready" if basis in _CONSENSUS_FILE_BASES
                          else "ready-after-materialise")

        slug = condition_id.replace("::", "__").replace(".", "_")
        output_dir = f"results/uplift-supplement/verifier-pairing/{slug}"
        scoreable = twin_detections if basis in _CONSENSUS_FILE_BASES else None

        # The corrected-F1 engine scopes per map sheet with
        # `source_tile.str.startswith(...)`, so a detection set without that
        # column raises KeyError at the first buffer. Committed consensus sets
        # do not have it: a consensus candidate is a CLUSTER, so they carry
        # `source_tiles` (plural) instead. The verified side got its singular
        # value from the verifier's crop manifest, so the twin is materialised
        # from that same manifest — same candidates, same tiles, differing only
        # in the probability filter.
        materialise_command = None
        if (
            basis in _CONSENSUS_FILE_BASES and recipe is not None and scoreable
            and recipe.engine == "evaluate_detections"
            and _projected_without_crs(sources.repo_root / scoreable)
        ):
            # S151-c: a committed consensus file with projected (metre)
            # coordinates and no crs member is read as WGS84 by RFC 7946
            # readers and scores F1 = 0 (the 55maps-generalisation
            # consensus-4of5 twin, 2026-08-29). Copy it with the CRS declared.
            materialised = f"{output_dir}/twin-{int(votes)}of{n_passes}-crs32635.geojson"
            materialise_command = " ".join(shlex.quote(part) for part in [
                "python", "scripts/materialise_pairing_twin.py",
                "--consensus", scoreable,
                "--declare-crs", "EPSG:32635",
                "--output", materialised,
            ])
            notes.append(
                "committed consensus file carries projected coordinates and no "
                "crs member; twin copied with EPSG:32635 declared"
            )
            scoreable = materialised  # status stays "ready": the prelude runs first
        if basis in ("union", "source-run-union") and recipe is not None and union_path:
            # S151: the union mode of the materialiser. The twin is the vote
            # shell of the committed union (which already carries source_tile
            # and vote_count per feature), gated on the candidate universe
            # against the stage's crop manifest when one was matched.
            materialised = f"{output_dir}/twin-{int(votes)}of{n_passes}.geojson"
            parts = [
                "python", "scripts/materialise_pairing_twin.py",
                "--union", union_path,
                "--min-votes", str(int(votes)),
            ]
            if matched_stage is not None:
                parts += ["--expect-manifest", matched_stage.path]
            parts += ["--output", materialised]
            materialise_command = " ".join(shlex.quote(part) for part in parts)
            scoreable = materialised
        if basis in _MANIFEST_BASES and recipe is not None and crop_manifest_path:
            # The twin is the vote shell of the pool's own crop manifest. The
            # materialiser's manifest mode copies each candidate's recorded
            # source_tile and centroid verbatim, so the twin shares the verified
            # side's candidate universe exactly and differs from it in the
            # probability filter alone.
            materialised = f"{output_dir}/twin-{int(votes)}of{n_passes}.geojson"
            parts = ["python", "scripts/materialise_pairing_twin.py",
                     "--crop-manifest", crop_manifest_path]
            # A universe recorded across two files is passed as two manifests;
            # the materialiser unions them and re-checks that their shells are
            # disjoint, so the join is gated on both sides.
            for extra in extra_manifests:
                parts += ["--crop-manifest", extra]
            if basis == "single-pass-manifest":
                # N = 1: the manifest records no vote_count because there were
                # no votes to record. The flag says so explicitly rather than
                # letting a missing column be read as zero votes.
                parts += ["--single-pass"]
            parts += ["--min-votes", str(int(votes)), "--output", materialised]
            materialise_command = " ".join(shlex.quote(part) for part in parts)
            scoreable = materialised
        if (
            scoreable
            and recipe is not None
            and recipe.engine == "corrected_f1_multi_buffer"
            and basis not in _MANIFEST_BASES
            and not _has_source_tile(sources.repo_root / scoreable)
        ):
            stage, _stage_basis = match_verifier_manifest(
                _run_manifests(sources, run_id, coverage),
                spec["label"], pool, geometry, n_passes,
                siblings=sorted(lineages.get(run_id, set())),
                pool_dir=(
                    str(pool_dir.relative_to(sources.repo_root))
                    if pool_dir else None
                ),
            )
            if stage is None:
                status, blocked = "blocked", (
                    f"{Path(scoreable).name} carries no per-feature source_tile "
                    "(consensus sets record source_tiles, plural), and no "
                    "verifier stage could be matched to supply one. Scoring it "
                    "with the corrected-F1 engine raises KeyError: 'source_tile'"
                )
                scoreable = None
            else:
                materialised = f"{output_dir}/twin-{int(votes)}of{n_passes}.geojson"
                materialise_command = " ".join(shlex.quote(part) for part in [
                    "python", "scripts/materialise_pairing_twin.py",
                    "--crop-manifest", stage.path,
                    "--min-votes", str(int(votes)),
                    "--expect-consensus", scoreable,
                    "--output", materialised,
                ])
                notes.append(
                    "twin materialised from the verifier stage's own crop "
                    f"manifest ({stage.path}) to carry source_tile"
                )
                scoreable = materialised
        rows.append({
            "job_id": f"pair::{condition_id}",
            "verified_condition_id": condition_id,
            "run_id": run_id,
            "proposer_pool": pool,
            "verified_stratum_id": stratum.stratum_id,
            "unverified_stratum_id": twin_stratum.stratum_id,
            "unverified_stratum_basis": twin_stratum_basis,
            "corpus": corpus,
            "reference": reference.term,
            "buffer_m": stratum.buffer_m,
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
            "crop_manifest_path": crop_manifest_path,
            "materialise_filter": materialise_filter,
            "reference_path": reference.path,
            "bounds_path": recipe.bounds if recipe else None,
            "engine": recipe.engine if recipe else None,
            "output_dir": output_dir if status.startswith("ready") else None,
            "materialise_command": (
                materialise_command if status.startswith("ready") else None
            ),
            "command": (
                _render_command(recipe, scoreable, output_dir, f"{slug}-unverified")
                if status.startswith("ready") and recipe and scoreable else None
            ),
            "notes": "; ".join(notes) or None,
        })
    return rows


def render_report(rows: list[dict[str, Any]], excluded: Sequence[str] = ()) -> str:
    """Render the pairing report.

    Args:
        rows: The worklist rows.

    Returns:
        The Markdown document.
    """
    status_counts: Counter[str] = Counter(r["status"] for r in rows)
    basis_counts = Counter(r["pairing_basis"] for r in rows)
    lines = [
        "# With/without-verifier pairing — worklist",
        "",
        *generated_doc_banner(
            "original publication; the with/without-verifier pairing plan",
            "scripts/build_verifier_pairing_worklist.py",
        ),
        "",
        "Build order step 3 of `planning/uplift-supplement-2026-08-28.md`. No",
        "scoring has been run: this document and its worklist are the plan.",
        "",
        "Verifier uplift is the difference a verifier makes holding everything",
        "else fixed. Each row pairs one verified cell with the consensus set that",
        "went INTO its verifier at the same vote threshold — same passes, same",
        "reference, same buffer, same frame.",
        "",
        "The two sides carry SEPARATE stratum ids (`verified_stratum_id` and",
        "`unverified_stratum_id`), and `scripts/compute_verifier_uplift.py`",
        "passes both to the cross-stratum guard.",
        "",
        "**What that guard is and is not.** A `stratum_id` is",
        "corpus × reference × buffer × frame. Pool, geometry, and fusion family",
        "are NOT in it — they are in the pairing key, which already forces the",
        "two sides to agree on all four stratum components before a pair is",
        "emitted. The guard is therefore a consistency TRIPWIRE: it catches an",
        "externally edited worklist, or a future change that lets the key and the",
        "stratum drift apart. It cannot catch a cross-LINEAGE mispair, because",
        "two cells of the same run at different geometries share a stratum. What",
        "protects against that is the lineage matching in this builder, not the",
        "guard downstream.",
        "",
        f"{len(rows)} verified cell(s) in the registry.",
        "",
        f"{len(excluded)} board-frame row(s) excluded by rule (PI, 2026-09-10): rows whose",
        "`scope_override.test_set_id` names a leaderboard scoring frame are board",
        "artefacts (the GS Era-2 board's `-era2b` and `-opmax` rows), not",
        "measurements of their own, and are neither paired nor offered as twins",
        "(`lib_uplift_supplement.is_board_frame_condition`).",
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
        "### How many pairs can be computed",
        "",
        "A pair is computable when BOTH sides have a score. Where each status",
        "stands:",
        "",
        "| Status | Pairs | Computable | Why |",
        "|---|---:|---:|---|",
        f"| `already-registered` | {status_counts['already-registered']} "
        f"| {status_counts['already-registered']} | Both sides are registered "
        "conditions, so both are already in `conditions.csv`. No scoring needed. |",
        f"| `ready` | {status_counts['ready']} | {status_counts['ready']} "
        "| Once the emitted job writes its score. |",
        f"| `ready-after-materialise` | {status_counts['ready-after-materialise']} "
        "| 0 | The vote shell has to be filtered out of the committed union "
        "first, and no job is emitted for that yet. |",
        f"| `blocked` | {status_counts['blocked']} | 0 | No twin located. |",
        "",
        f"So the ceiling after a clean run of `verifier-pairing-commands.sh` is "
        f"**{status_counts['already-registered'] + status_counts['ready']} "
        f"computed, {len(rows) - status_counts['already-registered'] - status_counts['ready']} "
        "pending**.",
        "",
        "The 2026-08-29 run produced 8, which is the 6 already-registered pairs",
        "plus 2 scored twins. Two defects, both now fixed, account for the gap:",
        "",
        "1. **The script aborted at the first failure.** `set -e` stopped the",
        "   batch at the third command, so twelve jobs that would have succeeded",
        "   never ran. The two that had already completed are the two scores.",
        "2. **Corrected-F1 scores were unreadable anyway.** Eight of the fifteen",
        "   jobs use `compute_corrected_f1_multi_buffer.py`, which writes",
        "   `summary.json`; the uplift computer only looked for",
        "   `evaluation.json`. Even a fully successful batch would have capped",
        "   at 6 + 7 = 13, with the eight corrected-F1 pairs stuck at `pending`",
        "   and nothing to say why.",
        "",
        "## Changelog",
        "",
        f"### {ORIGINAL_PUBLICATION_DATE} — Original publication",
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
        "# Rows with status 'ready-after-materialise' run two commands: the",
        "# materialiser filters the paired vote shell out of the committed union",
        "# (union_path, materialise_filter), then the score runs on the twin.",
        "#",
        "# Jobs are INDEPENDENT and the script does not stop at the first",
        "# failure. It did once: `set -e` aborted the 2026-08-29 run at the",
        "# third command, so twelve jobs that would have succeeded never ran and",
        "# one crash looked like a partial success. Failures are collected and",
        "# reported at the end, and the exit code still reflects them.",
        *SHELL_PREAMBLE,
        "",
    ]
    for row in rows:
        if not row["status"].startswith("ready") or not row["command"]:
            continue
        script.append(f"# {row['job_id']}")
        if row["materialise_command"]:
            script.append(f"run {row['materialise_command']}")
        script += [f"run {row['command']}", ""]
    script += list(SHELL_EPILOGUE)
    (out_dir / "verifier-pairing-commands.sh").write_text(
        "\n".join(script), encoding="utf-8"
    )
    (out_dir / "verifier-pairing-commands.sh").chmod(0o755)
    (out_dir / "verifier-pairing-report.md").write_text(
        render_report(rows, sources.excluded_board_frame), encoding="utf-8"
    )

    counts = Counter(r["status"] for r in rows)
    print(f"verifier-pairing-worklist.csv   {len(rows):>4} rows")
    for status, count in sorted(counts.items()):
        print(f"  {status:<26} {count:>4}")
    print(f"written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
