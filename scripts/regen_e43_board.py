#!/usr/bin/env python3
# ============================================================================
# regen_e43_board.py
# ----------------------------------------------------------------------------
# Regenerate the March 2026 round-robin leaderboard boards, and the smaller
# Benjamini-Hochberg (BH) families that share their p-values, WITHOUT the three
# coverage-confounded `flash-min-text-t10` cells identified by protocol erratum
# E72.
#
# WHY THIS EXISTS
# ---------------
# The 2026-03-28/29 pairwise permutation campaign wired the study
# ``outputs/h11/consensus-384-UNINTENDED-T1.0/`` (240 tiles by design) into
# comparisons scored against the 487-tile evaluation bounds. Every mound in the
# 247 unprocessed tiles became an automatic false negative, so that arm's F1 is
# understated by roughly 0.17-0.19 (see
# ``reports/e43-coverage-confound-remediation-2026-08-02.md`` and
# ``docs/methodology/preregistration/protocol-errata.md`` § E72). The confound
# is a SCOPE defect in three board cells; it does not touch any other cell's
# metrics.
#
# The Principal Investigator's (PI) ruling, recorded in E72's remediation list,
# is option (a): DROP the confounded cells and regenerate the board, rather than
# splice in the matched-scope replacements (those are filed separately under
# ``results/e43-matched-temperature/``). Because the confound is confined to
# whole cells, every retained pair's observed statistic is still valid — the
# permutation test for, say, "Pro HIGH text 3-of-5 versus text baseline + PV"
# never touched the confounded study. So this script performs NO permutation
# testing and makes NO application programming interface (API) calls. It:
#
#   1. re-reads the retained pairs' observed ΔF1 and raw p-values from the
#      committed per-pair test JavaScript Object Notation (JSON) artefacts,
#   2. recomputes the BH false-discovery-rate (FDR) correction over the SMALLER
#      retained family (the only quantity that legitimately changes), and
#   3. re-runs the project-canonical greedy-clique tiering on the result.
#
# The permutation artefacts under ``results/pairwise/`` are DATA and are never
# modified by this script; it only reads them.
#
# WHAT COUNTS AS CONFOUNDED
# -------------------------
# Membership is derived from the artefacts, never from labels. The condition
# carries five aliases across the repository (``flash-min-text-t10``,
# ``FM text T=1.0``, ``Flash MIN text T=1.0``, ``consensus-384-t1-0``, bare
# ``384``), so label matching is unsafe. Instead each test JSON records the
# on-disk provenance of both arms under ``condition_{a,b}.source``; a pair is
# confounded if either arm's source references the study directory
# ``consensus-384-UNINTENDED-T1.0``. A repository-wide grep for that marker
# returns exactly 148 test files, matching the remediation report's inventory.
#
# BOARDS AND FAMILIES REGENERATED
# -------------------------------
# Round-robin boards (own BH family each, ``family: leaderboard``):
#   * ``results/pairwise/leaderboard-20m/`` — 26 conditions, C(26,2) = 325 tests;
#     3 conditions confounded, so 3 x 25 - 3 = 72 pairs drop, 253 retained.
#   * ``results/pairwise/leaderboard-30m/`` — 25 conditions, C(25,2) = 300 tests;
#     the same 3 conditions, so 3 x 24 - 3 = 69 pairs drop, 231 retained.
#     (The 30 m board is one condition smaller than the 20 m board and differs
#     in three consensus thresholds; both memberships are derived at runtime.)
#
# Smaller BH families that share the same confounded p-values:
#   * ``results/pairwise/20m/`` family ``confirmatory`` — 26 members, of which
#     group 4's three temperature tests are confounded -> 23 retained.
#   * ``results/pairwise/30m/`` family ``confirmatory`` — likewise 26 -> 23.
#   * ``results/factor-analysis/factor_analysis_results.json`` family
#     ``temperature`` — 6 members, of which group 4's three tests (reused from
#     the 20 m pairwise run) and group 12's 384 px N=1 test are confounded
#     -> 2 retained (both preregistered Phase 2b single-pass contrasts).
# The ``exploratory`` families (6 members per buffer) and the other four
# factor-analysis families contain no confounded member and are left alone;
# the script asserts this rather than assuming it.
#
# THE RESTATED LAYOUT (2026-10-30 revision; PI ruling D69 Q15)
# ------------------------------------------------------------
# The S164 restatement pass (``08af04cf3``; record
# ``reports/s164-agent-records/restatement-pass.md`` § 1.5) regenerated
# ``results/pairwise/`` IN PLACE on the consensus route of ruling D60 (3), with
# one exception (ruling D61 (2)). The per-pair files that read the two
# single-pass arms (``single-pass-t0`` 5-of-5 and 10-of-10, whose inputs
# drifted before tracking) stay at their paths as DATED MARCH RECORDS, and
# today's runs of those pairs go BESIDE them, at the same relative path under
# ``results/rescore-2026-10-15/pairwise/`` (``BESIDE_ROOT``). Each directory's
# ``run_manifest.json`` and ``fdr/`` belong to today's complete run, so they
# agree with the beside files, not with the March records. A March record is
# identified by having a beside counterpart — never by its timestamp: the
# pairs that did not move also kept their March files, and those are current.
#
# The first version of this script refused that layout: Gate A compared the
# March records with today's manifest, Gate C found the same condition scored
# two ways, Gate B pinned the March 30 m count (243), and the renderers wrote a
# 2026-08-02 "original publication" banner over any revision trail. The
# 2026-10-30 adaptation, as the PI specified it:
#
#   * Gates A and C accept the dated records: the loader reads today's run in
#     place of each dated record (after checking that the two name the same
#     pair and that the record is the older), and both gates then run over
#     today's runs only. A beside file with no record next to it is refused.
#   * Gate B takes each board's significance count from that board's own run
#     (``fdr/pairwise_results_fdr.json``): 240 of 300 at 30 m today, where the
#     March run gave the published 243.
#   * The renderers keep the revision trail: a ``Revision`` registry
#     (``REVISIONS``) drives every banner and ``## Changelog``, and the latest
#     revision's changelog gives the before -> after figures against the
#     previous revision's committed outputs (read with ``git show``).
#
# ``--revision 2026-08-02`` renders the original revision; on the inputs it was
# built from (commit ``bc45133b4``) it reproduces the committed 2026-08-02
# outputs exactly, apart from timestamps and the commit hash. Each revision
# declares the input layout it expects, and the script refuses a mismatch.
#
# VALIDATION GATES (all must pass before anything is written)
# ----------------------------------------------------------
#   Gate A: the per-pair JSONs (today's runs, read beside any dated record)
#           reproduce the committed ``run_manifest.json`` exactly — same pair
#           set, same raw p-values, same ΔF1 — and each hypothesis family's
#           raw p-values equal its per-test JSONs.
#   Gate B: recomputing the FULL board (no cells dropped) reproduces the run's
#           own BH artefact — the same significance count and the same
#           adjusted value for every pair — and the published tier count
#           (9 at both buffers, in March and after the restatement). This
#           proves the BH + tiering reimplementation is faithful before its
#           output is trusted for the reduced board.
#   Gate C: every condition's F1/precision/recall is internally consistent
#           across all the tests it appears in (today's runs only).
#   Gate D: replaying the published 20 m rank order reproduces the published
#           tier sizes (see ``reconcile_published_order``).
#
# METRIC NOTE (tile-level Matthews correlation coefficient, MCC)
# -------------------------------------------------------------
# The permutation artefacts that form this board's data layer carry only
# mound-level true/false positives and negatives, so no MCC column is
# reproduced here. Dropping whole cells does not alter any RETAINED condition's
# metrics, so within one vintage of inputs only the tier assignment moves. The
# MCC column of the dated snapshot ``results/paper-tables/leaderboard_tiers_20m.md``
# keeps its 2026-03-29 values, which predate the 2026-10-15 restatement of
# sixteen rows' mound-level metrics; the 2026-10-30 renderings therefore do not
# assert that column current.
#
# USAGE
# -----
#   # dry run (default) — computes everything, writes nothing:
#   python scripts/regen_e43_board.py
#
#   # write the regenerated artefacts (latest revision):
#   python scripts/regen_e43_board.py --execute
#
#   # alternative output root:
#   python scripts/regen_e43_board.py --execute --output-dir results/tmp-board
#
#   # render the original 2026-08-02 revision (March inputs only):
#   python scripts/regen_e43_board.py --execute --revision 2026-08-02 \
#       --output-dir <scratch>
#
# Zero API cost; pure recomputation over committed artefacts (a few
# seconds). The project compute rule sends work above ~30 s of CPU to sapphire.
# ============================================================================
"""Regenerate the E72-affected leaderboard boards and BH families.

See the module header for the full rationale, the confounded-cell definition,
the boards and families covered, and the validation gates.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from apply_fdr_correction import apply_bh_correction  # noqa: E402
from n1_baseline_leaderboard_tiering import greedy_clique_tiers  # noqa: E402

# --- constants ------------------------------------------------------------ #

#: Study directory whose runs cover 240 of the 487 evaluation tiles (E72).
CONFOUNDED_STUDY_MARKER = "consensus-384-UNINTENDED-T1.0"

#: Project-default false-discovery-rate threshold.
FDR_Q = 0.05

#: The erratum authorising this regeneration.
ERRATUM = "E72"

#: Date this remediation was executed (the original revision's date).
REMEDIATION_DATE = date(2026, 8, 2)

#: Root of the permutation artefacts, relative to the repository root.
PAIRWISE_ROOT = "results/pairwise"

#: Root of today's runs that stand BESIDE dated March records (S164 pass,
#: ruling D61 (2)). A file here at ``<board>/<group>/<name>.json`` is today's
#: run of the pair whose March record stays at the same path under
#: ``PAIRWISE_ROOT``. Absent on the March inputs.
BESIDE_ROOT = "results/rescore-2026-10-15/pairwise"

#: Published tier counts the full-board recomputation must reproduce (Gate B).
#: Both boards keep nine tiers in the March snapshot and in the restated runs
#: (``restatement-pass.md`` § 2.4). The significance count is NOT pinned here:
#: Gate B reads it from each board's own run (``fdr/pairwise_results_fdr.json``)
#: — 265 of 325 and 243 of 300 in March, 265 and 240 after the restatement.
PUBLISHED_FULL_BOARD_TIERS: dict[str, int] = {
    "leaderboard-20m": 9,
    "leaderboard-30m": 9,
}


@dataclass(frozen=True)
class Revision:
    """One dated revision of the regenerated board (Document Revision Policy).

    The renderers draw every banner and changelog from these records, so a
    regeneration adds a revision rather than overwriting the trail.

    Attributes:
        date: The revision's date (the banner's "Last revised").
        reason: Short reason, quoted in the banner.
        title: Changelog heading text after the date.
        layout: Input layout the revision expects: ``"march"`` (no dated
            records) or ``"restated"`` (dated records with runs beside them).
        host: Machine the revision was produced on.
        output_version: ``version`` written into the JSON manifests.
        baseline_ref: Commit holding the PREVIOUS revision's committed outputs,
            read for the before -> after figures; None for the original.
    """

    date: date
    reason: str
    title: str
    layout: str
    host: str
    output_version: str
    baseline_ref: str | None

    @property
    def is_original(self) -> bool:
        """True for the first publication, which has no baseline."""
        return self.baseline_ref is None


#: Every revision of ``results/e43-board-regen/``, oldest first.
REVISIONS: tuple[Revision, ...] = (
    Revision(
        date=REMEDIATION_DATE,
        reason=f"original publication — {ERRATUM} remediation",
        title="Original publication",
        layout="march",
        host="sapphire",
        output_version="1.0.0",
        baseline_ref=None,
    ),
    Revision(
        date=date(2026, 10, 30),
        reason="regenerated on the restated pairwise layout, PI ruling D69 Q15",
        title="Regenerated on the restated pairwise layout (Session 166)",
        layout="restated",
        host="zbook",
        output_version="1.1.0",
        baseline_ref="2f3ef020a",
    ),
)

#: The revision rendered by default.
LATEST_REVISION = REVISIONS[-1]

#: Commit that restated ``results/pairwise/`` in place (S164 pass, § 2.4).
RESTATEMENT_COMMIT = "08af04cf3"

#: The published 20 m snapshot's rank order, read off
#: ``results/paper-tables/leaderboard_tiers_20m.md`` (ranks 1-26) and mapped to
#: board labels by F1. It is F1-descending EXCEPT at rank 10, where
#: ``flash-high-image-3-of-5--flash-min-vf`` (F1 0.778) precedes two higher-F1
#: conditions. Greedy-clique tiering is order-dependent, so that transposition —
#: not the E72 confound — explains the one tier difference between the
#: published snapshot and this script's full-board recomputation. Gate D
#: replays the published order to prove it.
PUBLISHED_20M_RANK_ORDER: list[str] = [
    "flash-high-text-16-of-30--flash-min-vf (t=0.2)",
    "flash-high-text-4-of-5--flash-min-vf (t=0.15)",
    "flash-high-text-4-of-5--flash-medium-vf (t=0.95)",
    "flash-high-text-9-of-10--flash-min-vf (t=0.2)",
    "pro-high-text-3-of-5--flash-min-vf (t=0.15)",
    "pro-high-text N=5 N=5, 3-of-5",
    "pro-high-text N=10 N=10, 6-of-10",
    "text-baseline--flash-min-vf (t=0.15)",
    "flash-high-text N=30 N=30, 26-of-30",
    "flash-high-image-3-of-5--flash-min-vf (t=0.15)",
    "flash-high-text N=10 N=10, 9-of-10",
    "flash-high-text N=5 N=5, 5-of-5",
    "flash-high-image N=10 N=10, 7-of-10",
    "flash-high-image N=5 N=5, 3-of-5",
    "image-baseline--flash-min-vf (t=0.2)",
    "pro-high-image N=5 N=5, 3-of-5",
    "flash-min-image N=10 N=10, 8-of-10",
    "flash-min-image N=5 N=5, 4-of-5",
    "flash-min-text-t07 N=30 N=30, 29-of-30",
    "flash-min-text-t07 N=5 N=5, 5-of-5",
    "flash-min-text-t07 N=10 N=10, 10-of-10",
    "single-pass-t0 N=10 N=10, 10-of-10",
    "single-pass-t0 N=5 N=5, 5-of-5",
    "flash-min-text-t10 N=5 N=5, 5-of-5",
    "flash-min-text-t10 N=30 N=30, 22-of-30",
    "flash-min-text-t10 N=10 N=10, 9-of-10",
]

#: Tier sizes of the published 20 m snapshot (Tiers 1-9, in order).
PUBLISHED_20M_TIER_SIZES: list[int] = [1, 6, 3, 2, 4, 4, 1, 3, 2]

#: Round-robin boards to regenerate: name -> (source directory, group subdir).
BOARDS: dict[str, tuple[str, str]] = {
    "leaderboard-20m": ("results/pairwise/leaderboard-20m", "group_8"),
    "leaderboard-30m": ("results/pairwise/leaderboard-30m", "group_8"),
}

#: Smaller BH families sourced from a ``run_manifest.json`` plus per-test JSONs.
PAIRWISE_FAMILY_DIRS: dict[str, str] = {
    "pairwise-20m": "results/pairwise/20m",
    "pairwise-30m": "results/pairwise/30m",
}

#: The factor-analysis family artefact (BH applied within each factor family).
FACTOR_ANALYSIS_JSON = "results/factor-analysis/factor_analysis_results.json"

#: Default output root, relative to the repository root; the previous
#: revision's outputs are read from here at its ``baseline_ref``.
OUTPUT_ROOT = "results/e43-board-regen"


# --- data model ----------------------------------------------------------- #


@dataclass(frozen=True)
class PairTest:
    """One paired permutation test between two board conditions.

    Attributes:
        label_a: Condition A's board label, verbatim from the artefact.
        label_b: Condition B's board label.
        f1_a: Condition A's F1 at this board's buffer.
        f1_b: Condition B's F1 at this board's buffer.
        precision_a: Condition A's precision.
        precision_b: Condition B's precision.
        recall_a: Condition A's recall.
        recall_b: Condition B's recall.
        n_detections_a: Condition A's detection count.
        n_detections_b: Condition B's detection count.
        delta_f1: Observed F1 difference (A - B), as recorded by the test.
        p_value: Raw two-sided permutation p-value.
        confounded: True if either arm draws on the E72 study.
        source_file: Path of the per-pair JSON this record was read from.
    """

    label_a: str
    label_b: str
    f1_a: float
    f1_b: float
    precision_a: float
    precision_b: float
    recall_a: float
    recall_b: float
    n_detections_a: int
    n_detections_b: int
    delta_f1: float
    p_value: float
    confounded: bool
    source_file: str

    @property
    def key(self) -> frozenset:
        """Unordered condition pair, used as the significance-map key."""
        return frozenset({self.label_a, self.label_b})


@dataclass
class Board:
    """A tiered round-robin board over one condition set.

    Attributes:
        name: Board identifier (e.g. ``leaderboard-20m``).
        tests: The pair tests forming this board's BH family.
        adjusted: BH-adjusted p-values, index-aligned with ``tests``.
        significant: Map from unordered pair key to BH significance at q.
        order: Condition labels ranked by board F1, descending.
        tiers: Greedy-clique tiers, ``tiers[0]`` being the leader's clique.
        metrics: Per-condition metric dictionary.
    """

    name: str
    tests: list[PairTest]
    adjusted: list[float]
    significant: dict[frozenset, bool]
    order: list[str]
    tiers: list[list[str]]
    metrics: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def n_significant(self) -> int:
        """Number of BH-significant pairs in this board's family."""
        return sum(1 for p in self.adjusted if p < FDR_Q)

    def tier_of(self, label: str) -> int:
        """Return the 1-based tier number holding ``label``.

        Args:
            label: A condition label present on this board.

        Returns:
            The 1-based tier index.

        Raises:
            KeyError: If the label is not on this board.
        """
        for index, tier in enumerate(self.tiers, start=1):
            if label in tier:
                return index
        raise KeyError(label)


# --- provenance helper ----------------------------------------------------- #


def git_commit() -> str:
    """Return the short HEAD commit hash, or ``"unknown"`` on failure.

    Returns:
        Short commit hash string.
    """
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE_DIR)
            .decode()
            .strip()
        )
    except Exception:  # pragma: no cover - provenance is best-effort only
        return "unknown"


# --- confound detection ---------------------------------------------------- #


def source_is_confounded(source: Mapping[str, Any] | None) -> bool:
    """Report whether a test arm's recorded source is the E72 study.

    The check is on the recorded on-disk provenance rather than the display
    label, because the confounded condition carries five different labels
    across the repository. Any string value in the source mapping that mentions
    the confounded study directory marks the arm.

    Args:
        source: The ``condition_{a,b}.source`` mapping from a test JSON, or
            None when the artefact records no source.

    Returns:
        True if this arm draws on ``consensus-384-UNINTENDED-T1.0``.

    Examples:
        >>> source_is_confounded({"mode": "consensus",
        ...                       "study_dir": "outputs/h11/"
        ...                                    "consensus-384-UNINTENDED-T1.0"})
        True
        >>> source_is_confounded({"mode": "pv", "threshold": 0.15})
        False
        >>> source_is_confounded(None)
        False
    """
    if not source:
        return False
    return any(
        isinstance(value, str) and CONFOUNDED_STUDY_MARKER in value for value in source.values()
    )


# --- the in-place-and-beside layout --------------------------------------- #


@dataclass(frozen=True)
class DatedRecord:
    """A March per-pair record left in place, with today's run beside it.

    Attributes:
        record_file: Repository-relative path of the March record (in place).
        current_file: Repository-relative path of today's run (beside).
        record_timestamp: The record's ``metadata.timestamp``.
        current_timestamp: Today's run's ``metadata.timestamp``.
    """

    record_file: str
    current_file: str
    record_timestamp: str
    current_timestamp: str


#: Metadata fields that must agree between a dated record and the run beside
#: it: together with the two labels they identify the test that was run.
PAIR_IDENTITY_METADATA = ("group", "question", "family", "buffer_metres", "n_permutations", "seed")


def beside_counterpart(path: Path) -> Path | None:
    """Return where today's run of an in-place per-pair file would stand.

    Args:
        path: A per-pair JSON under ``BASE_DIR / PAIRWISE_ROOT``.

    Returns:
        The same relative path under ``BASE_DIR / BESIDE_ROOT``, or None when
        ``path`` does not lie under the pairwise root.

    Examples:
        >>> p = BASE_DIR / PAIRWISE_ROOT / "20m" / "group_1" / "x.json"
        >>> beside_counterpart(p).relative_to(BASE_DIR).as_posix()
        'results/rescore-2026-10-15/pairwise/20m/group_1/x.json'
    """
    try:
        relative = path.relative_to(BASE_DIR / PAIRWISE_ROOT)
    except ValueError:
        return None
    return BASE_DIR / BESIDE_ROOT / relative


def check_dated_record(record_path: Path, current_path: Path) -> DatedRecord:
    """Accept a dated March record only if the run beside it is its successor.

    The two files must name the same test — the same two labels in the same
    order and the same group, question, family, buffer, permutation count and
    seed — and the record must be the older of the two.

    Args:
        record_path: The March record (in place).
        current_path: Today's run (beside).

    Returns:
        The accepted :class:`DatedRecord`.

    Raises:
        AssertionError: If the two files are not the same test, or the record
            is not older than the run beside it.
    """
    record = json.loads(record_path.read_text())
    current = json.loads(current_path.read_text())
    for arm in ("condition_a", "condition_b"):
        assert record[arm]["label"] == current[arm]["label"], (
            f"dated record {record_path} and the run beside it name different "
            f"{arm} labels: {record[arm]['label']!r} vs {current[arm]['label']!r}"
        )
    for name in PAIR_IDENTITY_METADATA:
        assert record["metadata"].get(name) == current["metadata"].get(name), (
            f"dated record {record_path} and the run beside it differ in "
            f"metadata.{name}: {record['metadata'].get(name)!r} vs "
            f"{current['metadata'].get(name)!r}"
        )
    record_ts = str(record["metadata"]["timestamp"])
    current_ts = str(current["metadata"]["timestamp"])
    assert datetime.fromisoformat(record_ts) < datetime.fromisoformat(current_ts), (
        f"dated record {record_path} ({record_ts}) is not older than the run "
        f"beside it ({current_ts})"
    )
    return DatedRecord(
        record_file=str(record_path.relative_to(BASE_DIR)),
        current_file=str(current_path.relative_to(BASE_DIR)),
        record_timestamp=record_ts,
        current_timestamp=current_ts,
    )


def resolve_group_files(group_dir: Path) -> tuple[list[Path], list[DatedRecord]]:
    """Choose today's run for every test in a group directory.

    A file that has a beside counterpart is a dated March record: today's run
    beside it is read in its place. Every other file is read where it stands.
    A beside file with no record at the same relative path is refused, because
    it would add a pair the run's manifest does not hold here.

    Args:
        group_dir: Directory holding one JSON per pairwise test.

    Returns:
        Tuple of (the per-pair files to read, sorted by in-place path; the
        accepted dated records).

    Raises:
        FileNotFoundError: If the directory holds no JSON files.
        AssertionError: On an orphan beside file or a dated record that fails
            :func:`check_dated_record`.
    """
    paths = sorted(group_dir.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"no per-pair test JSONs under {group_dir}")

    beside_dir = beside_counterpart(group_dir)
    if beside_dir is not None and beside_dir.is_dir():
        in_place = {path.name for path in paths}
        orphans = sorted(p.name for p in beside_dir.glob("*.json") if p.name not in in_place)
        assert not orphans, f"beside files with no dated record under {group_dir}: {orphans}"

    current: list[Path] = []
    dated: list[DatedRecord] = []
    for path in paths:
        counterpart = beside_counterpart(path)
        if counterpart is not None and counterpart.is_file():
            dated.append(check_dated_record(path, counterpart))
            current.append(counterpart)
        else:
            current.append(path)
    return current, dated


# --- artefact loading ------------------------------------------------------ #


def pair_test_from_file(path: Path) -> PairTest:
    """Read one per-pair permutation-test JSON into a :class:`PairTest`.

    Args:
        path: The per-pair JSON.

    Returns:
        The populated record; ``source_file`` is repository-relative.
    """
    doc = json.loads(path.read_text())
    cond_a, cond_b = doc["condition_a"], doc["condition_b"]
    perm = doc["permutation_test"]
    return PairTest(
        label_a=cond_a["label"],
        label_b=cond_b["label"],
        f1_a=float(cond_a["f1"]),
        f1_b=float(cond_b["f1"]),
        precision_a=float(cond_a["precision"]),
        precision_b=float(cond_b["precision"]),
        recall_a=float(cond_a["recall"]),
        recall_b=float(cond_b["recall"]),
        n_detections_a=int(cond_a["n_detections"]),
        n_detections_b=int(cond_b["n_detections"]),
        delta_f1=float(perm["observed_f1_diff"]),
        p_value=float(perm["p_value"]),
        confounded=(
            source_is_confounded(cond_a.get("source"))
            or source_is_confounded(cond_b.get("source"))
        ),
        source_file=str(path.relative_to(BASE_DIR)),
    )


def load_pair_tests(group_dir: Path) -> list[PairTest]:
    """Load today's run of every per-pair permutation test in a group directory.

    Where a dated March record has today's run beside it, the run beside it is
    read instead (:func:`resolve_group_files`), so the returned set is one
    vintage — the one the directory's manifest and BH artefact belong to.

    Args:
        group_dir: Directory holding one JSON per pairwise test.

    Returns:
        Pair tests sorted by (label_a, label_b) for determinism.

    Raises:
        FileNotFoundError: If the directory holds no JSON files.
    """
    current, _dated = resolve_group_files(group_dir)
    tests = [pair_test_from_file(path) for path in current]
    return sorted(tests, key=lambda t: (t.label_a, t.label_b))


def check_against_manifest(tests: Sequence[PairTest], manifest_path: Path) -> None:
    """Gate A — assert the per-pair JSONs reproduce the committed manifest.

    Args:
        tests: Pair tests loaded from the per-pair JSONs.
        manifest_path: The board's ``run_manifest.json``.

    Raises:
        AssertionError: On any count, membership, p-value or ΔF1 mismatch.
    """
    manifest = json.loads(manifest_path.read_text())
    entries = manifest["comparisons"]
    declared = manifest["metadata"]["n_comparisons"]

    assert len(entries) == declared, f"{manifest_path}: manifest count {len(entries)} != {declared}"
    assert len(tests) == declared, f"{manifest_path}: {len(tests)} per-pair JSONs != {declared}"

    from_json = {t.key: t for t in tests}
    assert len(from_json) == len(tests), "duplicate condition pair among the per-pair JSONs"

    for entry in entries:
        key = frozenset({entry["label_a"], entry["label_b"]})
        assert key in from_json, f"manifest pair absent from per-pair JSONs: {sorted(key)}"
        test = from_json[key]
        assert abs(test.p_value - float(entry["p_value"])) < 1e-12, (
            f"p-value mismatch for {sorted(key)}: {test.p_value} vs {entry['p_value']}"
        )
        assert abs(abs(test.delta_f1) - abs(float(entry["delta_f1"]))) < 1e-6, (
            f"ΔF1 mismatch for {sorted(key)}: {test.delta_f1} vs {entry['delta_f1']}"
        )


def run_fdr_adjusted(source_dir: Path) -> dict[frozenset, float]:
    """Read a board run's own BH-adjusted p-values from its ``fdr/`` artefact.

    ``fdr/pairwise_results_fdr.json`` is written by ``apply_fdr_correction.py``
    over the complete run that the directory's manifest belongs to (today's
    run, after the restatement).

    Args:
        source_dir: The board's permutation run directory.

    Returns:
        Map from unordered pair key to the run's adjusted p-value.

    Raises:
        AssertionError: If the artefact lists a pair twice.
    """
    doc = json.loads((source_dir / "fdr" / "pairwise_results_fdr.json").read_text())
    adjusted = {
        frozenset({entry["label_a"], entry["label_b"]}): float(entry["p_value_adj"])
        for entry in doc["comparisons"]
    }
    assert len(adjusted) == len(doc["comparisons"]), (
        f"{source_dir}: duplicate pair in fdr/pairwise_results_fdr.json"
    )
    return adjusted


def check_full_board_gate(name: str, full_board: Board, source_dir: Path) -> int:
    """Gate B — the full-board recomputation reproduces the board's own run.

    The significance count is taken from the run itself (its ``fdr/``
    artefact), as the PI specified (D69 Q15): the restated 30 m run gives 240
    of 300 where the March run gave the published 243. Every pair's adjusted
    value must match too, and the tier count must equal the published one.

    Args:
        name: Board identifier (selects the published tier count).
        full_board: The recomputed FULL board (nothing dropped).
        source_dir: The board's permutation run directory.

    Returns:
        The run's significance count (which the recomputation reproduced).

    Raises:
        AssertionError: On a different pair set, any adjusted value differing
            by 1e-6 or more, a different significance count, or a tier count
            other than the published one.
    """
    adjusted = run_fdr_adjusted(source_dir)
    keys = {test.key for test in full_board.tests}
    assert set(adjusted) == keys, (
        f"Gate B ({name}): the run's BH artefact and the per-pair JSONs hold "
        f"different pair sets ({len(adjusted)} vs {len(keys)})"
    )
    for index, test in enumerate(full_board.tests):
        assert abs(full_board.adjusted[index] - adjusted[test.key]) < 1e-6, (
            f"Gate B ({name}): adjusted p for {sorted(test.key)} recomputes as "
            f"{full_board.adjusted[index]}, the run's BH artefact says {adjusted[test.key]}"
        )
    run_significant = sum(1 for value in adjusted.values() if value < FDR_Q)
    assert full_board.n_significant == run_significant, (
        f"Gate B ({name}): recomputed {full_board.n_significant} significant, "
        f"the run's own BH artefact says {run_significant}"
    )
    expected_tiers = PUBLISHED_FULL_BOARD_TIERS.get(name)
    if expected_tiers is not None:
        assert len(full_board.tiers) == expected_tiers, (
            f"Gate B ({name}): recomputed {len(full_board.tiers)} tiers, "
            f"published snapshot says {expected_tiers}"
        )
    return run_significant


def condition_metrics(tests: Iterable[PairTest]) -> dict[str, dict[str, float]]:
    """Gate C — collect per-condition metrics and check internal consistency.

    Every condition appears in many tests; each test records that condition's
    F1, precision, recall and detection count. Those must agree everywhere,
    otherwise the board is not scoring one condition consistently.

    Args:
        tests: The board's pair tests.

    Returns:
        Map from condition label to its metric dictionary.

    Raises:
        AssertionError: If a condition's metrics disagree between tests.
    """
    metrics: dict[str, dict[str, float]] = {}
    for test in tests:
        for label, values in (
            (
                test.label_a,
                {
                    "f1": test.f1_a,
                    "precision": test.precision_a,
                    "recall": test.recall_a,
                    "n_detections": float(test.n_detections_a),
                },
            ),
            (
                test.label_b,
                {
                    "f1": test.f1_b,
                    "precision": test.precision_b,
                    "recall": test.recall_b,
                    "n_detections": float(test.n_detections_b),
                },
            ),
        ):
            if label not in metrics:
                metrics[label] = values
                continue
            for name, value in values.items():
                assert abs(metrics[label][name] - value) < 1e-6, (
                    f"inconsistent {name} for {label!r}: "
                    f"{metrics[label][name]} vs {value} ({test.source_file})"
                )
    return metrics


# --- board construction ---------------------------------------------------- #


def rank_conditions(metrics: Mapping[str, Mapping[str, float]]) -> list[str]:
    """Rank condition labels by board F1, descending.

    Ties break on the label, so the ordering — and therefore the greedy-clique
    tiering that consumes it — is deterministic.

    Args:
        metrics: Per-condition metric dictionary.

    Returns:
        Condition labels, best F1 first.
    """
    return sorted(metrics, key=lambda label: (-metrics[label]["f1"], label))


def build_board(name: str, tests: Sequence[PairTest], q: float = FDR_Q) -> Board:
    """Apply BH-FDR to a family of pair tests and tier the resulting board.

    Args:
        name: Board identifier.
        tests: The pair tests forming this BH family.
        q: FDR threshold.

    Returns:
        The assembled :class:`Board`.
    """
    adjusted = apply_bh_correction([t.p_value for t in tests], q=q)
    significant = {t.key: adjusted[i] < q for i, t in enumerate(tests)}
    metrics = condition_metrics(tests)
    order = rank_conditions(metrics)
    tiers = greedy_clique_tiers(order, significant)
    return Board(
        name=name,
        tests=list(tests),
        adjusted=list(adjusted),
        significant=significant,
        order=order,
        tiers=tiers,
        metrics=metrics,
    )


def split_confounded(tests: Sequence[PairTest]) -> tuple[list[PairTest], list[PairTest]]:
    """Partition pair tests into retained and dropped (E72-confounded).

    Args:
        tests: All the board's pair tests.

    Returns:
        Tuple of (retained tests, dropped tests).
    """
    retained = [t for t in tests if not t.confounded]
    dropped = [t for t in tests if t.confounded]
    return retained, dropped


def confounded_labels(tests: Sequence[PairTest]) -> list[str]:
    """Return the labels of conditions whose source is the E72 study.

    A condition is confounded if it is the confounded arm of at least one test.
    Determined by checking, for each test that is flagged, which of its two arms
    carries the marker.

    Args:
        tests: Pair tests carrying full source provenance.

    Returns:
        Sorted list of confounded condition labels.
    """
    labels: set[str] = set()
    for test in tests:
        if not test.confounded:
            continue
        # Re-open the artefact so each ARM is attributed individually; the
        # PairTest flag is the disjunction over both arms.
        doc = json.loads((BASE_DIR / test.source_file).read_text())
        for arm, label in (("condition_a", test.label_a), ("condition_b", test.label_b)):
            if source_is_confounded(doc[arm].get("source")):
                labels.add(label)
    return sorted(labels)


def reconcile_published_order(board: Board) -> dict[str, Any]:
    """Gate D — explain the 20 m board's one difference from the snapshot.

    The published 2026-03-29 snapshot ranks one condition out of F1 order, and
    greedy-clique tiering is order-dependent, so its tier partition differs from
    a strictly F1-descending recomputation by exactly that condition. This
    function replays the tiering under the PUBLISHED order and checks it
    reproduces the published tier sizes — proving the difference is ordering,
    not statistics, and that no E72 effect is being mistaken for one.

    Args:
        board: The recomputed FULL 26-condition board.

    Returns:
        Reconciliation record: whether the replay matched, and the conditions
        whose tier differs between the two orderings.

    Raises:
        AssertionError: If the replay does not reproduce the published sizes.
    """
    assert set(PUBLISHED_20M_RANK_ORDER) == set(board.order), (
        "Gate D: the published rank order and the board membership disagree"
    )
    replay = greedy_clique_tiers(PUBLISHED_20M_RANK_ORDER, board.significant)
    sizes = [len(tier) for tier in replay]
    assert sizes == PUBLISHED_20M_TIER_SIZES, (
        f"Gate D: replaying the published order gives tier sizes {sizes}, "
        f"published snapshot has {PUBLISHED_20M_TIER_SIZES}"
    )

    replay_tier = {label: i for i, tier in enumerate(replay, start=1) for label in tier}
    differences = [
        {
            "condition": label,
            "tier_published": replay_tier[label],
            "tier_recomputed": board.tier_of(label),
        }
        for label in board.order
        if replay_tier[label] != board.tier_of(label)
    ]
    return {"replay_matches_published": True, "ordering_differences": differences}


def tier_movement(old: Board, new: Board) -> list[dict[str, Any]]:
    """Compare tier assignments between the full and the regenerated board.

    Args:
        old: The recomputed FULL board (all conditions).
        new: The regenerated board (confounded conditions dropped).

    Returns:
        One record per condition retained on the new board, with old and new
        tier numbers and the signed movement (negative = promoted upward).
    """
    movement: list[dict[str, Any]] = []
    for label in new.order:
        old_tier = old.tier_of(label)
        new_tier = new.tier_of(label)
        movement.append(
            {
                "condition": label,
                "f1": round(new.metrics[label]["f1"], 6),
                "tier_old": old_tier,
                "tier_new": new_tier,
                "delta_tier": new_tier - old_tier,
            }
        )
    return movement


def significance_changes(old: Board, new: Board) -> list[dict[str, Any]]:
    """List retained pairs whose BH significance changed with the family size.

    Args:
        old: The recomputed FULL board.
        new: The regenerated board.

    Returns:
        One record per retained pair whose significance verdict flipped.
    """
    old_adjusted = {t.key: old.adjusted[i] for i, t in enumerate(old.tests)}
    changes: list[dict[str, Any]] = []
    for index, test in enumerate(new.tests):
        was = old.significant[test.key]
        now = new.adjusted[index] < FDR_Q
        if was != now:
            changes.append(
                {
                    "condition_a": test.label_a,
                    "condition_b": test.label_b,
                    "p_raw": test.p_value,
                    "q_old": round(old_adjusted[test.key], 6),
                    "q_new": round(new.adjusted[index], 6),
                    "was_significant": was,
                    "is_significant": now,
                }
            )
    return changes


# --- smaller BH families --------------------------------------------------- #


def load_pairwise_family(family_dir: Path) -> list[dict[str, Any]]:
    """Load a hypothesis-family FDR artefact and flag its confounded members.

    ``fdr/pairwise_results_fdr.json`` is the published family artefact: it
    carries the family label, the raw p-value and the published BH-adjusted
    q-value for every test. The per-test JSONs under ``group_*/`` carry the
    source provenance. They are joined on (group, question, label_a, label_b),
    which is unique. Where a per-test file is a dated March record, today's
    run beside it is read instead (:func:`resolve_group_files`), and the
    artefact's raw p-value must equal that per-test file's (Gate A, families).

    Args:
        family_dir: e.g. ``results/pairwise/20m``.

    Returns:
        One record per family member, with a ``confounded`` flag added.

    Raises:
        AssertionError: If any family member has no matching per-test JSON, or
            its raw p-value differs from that JSON's.
    """
    manifest = json.loads((family_dir / "fdr" / "pairwise_results_fdr.json").read_text())
    provenance: dict[tuple[Any, ...], bool] = {}
    p_values: dict[tuple[Any, ...], float] = {}
    for group_dir in sorted(p for p in family_dir.glob("group_*") if p.is_dir()):
        current, _dated = resolve_group_files(group_dir)
        for path in current:
            doc = json.loads(path.read_text())
            key = (
                doc["metadata"]["group"],
                doc["metadata"]["question"],
                doc["condition_a"]["label"],
                doc["condition_b"]["label"],
            )
            provenance[key] = source_is_confounded(
                doc["condition_a"].get("source")
            ) or source_is_confounded(doc["condition_b"].get("source"))
            p_values[key] = float(doc["permutation_test"]["p_value"])

    records: list[dict[str, Any]] = []
    for entry in manifest["comparisons"]:
        key = (entry["group"], entry["question"], entry["label_a"], entry["label_b"])
        assert key in provenance, f"{family_dir}: no per-test JSON for {key}"
        raw = float(entry.get("p_value_raw", entry.get("p_value")))
        assert abs(raw - p_values[key]) < 1e-12, (
            f"Gate A ({family_dir}): family artefact p {raw} for {key} differs "
            f"from its per-test JSON's {p_values[key]}"
        )
        records.append({**entry, "confounded": provenance[key]})
    return records


def dated_record_inventory(directories: Iterable[Path]) -> list[DatedRecord]:
    """List every dated March record under the given run directories.

    Args:
        directories: Permutation run directories (each holding ``group_*/``).

    Returns:
        The accepted dated records, in path order.
    """
    records: list[DatedRecord] = []
    for directory in directories:
        for group_dir in sorted(p for p in directory.glob("group_*") if p.is_dir()):
            records.extend(resolve_group_files(group_dir)[1])
    return records


def check_revision_layout(revision: Revision, n_dated: int) -> None:
    """Refuse to render a revision over inputs of the wrong layout.

    Args:
        revision: The revision being rendered.
        n_dated: Number of dated March records found in the inputs.

    Raises:
        ValueError: If a ``"march"`` revision meets dated records, or a
            ``"restated"`` revision meets none.
    """
    if revision.layout == "march" and n_dated:
        raise ValueError(
            f"revision {revision.date} renders the March layout, but the inputs "
            f"hold {n_dated} dated records with runs beside them"
        )
    if revision.layout == "restated" and not n_dated:
        raise ValueError(
            f"revision {revision.date} renders the restated layout, but no dated "
            f"record with a run beside it was found under {BESIDE_ROOT}"
        )


def discover_confounded_tests(pairwise_root: Path) -> tuple[set[tuple[Any, ...]], list[str]]:
    """Walk every permutation artefact and identify the confounded tests.

    This is the inventory step: it visits every per-pair test JSON under
    ``results/pairwise/`` (the run manifests and FDR roll-ups are skipped) and
    flags those where either arm's recorded source is the E72 study. The result
    is the authoritative confounded-membership set, derived from provenance
    rather than from labels or from a hand-maintained list.

    Args:
        pairwise_root: ``results/pairwise``.

    Returns:
        Tuple of (set of (group, question, label_a, label_b) keys, sorted list
        of repository-relative paths of the flagged artefacts).
    """
    keys: set[tuple[Any, ...]] = set()
    files: list[str] = []
    for path in sorted(pairwise_root.rglob("*.json")):
        if path.name == "run_manifest.json":
            continue
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError:  # pragma: no cover - defensive
            continue
        if not isinstance(doc, dict) or "condition_a" not in doc:
            continue
        arm_a, arm_b = doc["condition_a"], doc["condition_b"]
        if source_is_confounded(arm_a.get("source")) or source_is_confounded(arm_b.get("source")):
            metadata = doc.get("metadata", {})
            keys.add(
                (
                    metadata.get("group"),
                    metadata.get("question"),
                    arm_a["label"],
                    arm_b["label"],
                )
            )
            files.append(str(path.relative_to(BASE_DIR)))
    return keys, files


def load_factor_analysis_family(
    path: Path, confounded_keys: set[tuple[Any, ...]]
) -> list[dict[str, Any]]:
    """Load the factor-analysis contrasts and flag the confounded members.

    ``factor_analysis_results.json`` is the analysis's authoritative data layer,
    but it records a coarse ``source`` string rather than per-arm file paths.
    Confounded membership is therefore imported from the on-disk permutation
    artefacts, keyed on (group, question, label_a, label_b) — the identity the
    factor analysis itself preserved when it reused those tests.

    Args:
        path: ``results/factor-analysis/factor_analysis_results.json``.
        confounded_keys: Keys established from the on-disk test artefacts by
            :func:`discover_confounded_tests`.

    Returns:
        One record per contrast, with a ``confounded`` flag added.
    """
    doc = json.loads(path.read_text())
    return [
        {
            **entry,
            "confounded": (
                entry["group"],
                entry["question"],
                entry["label_a"],
                entry["label_b"],
            )
            in confounded_keys,
        }
        for entry in doc["comparisons"]
    ]


def recompute_families(
    records: Sequence[Mapping[str, Any]], family_key: str = "family", q: float = FDR_Q
) -> list[dict[str, Any]]:
    """Recompute BH q-values family by family with confounded members dropped.

    Args:
        records: Contrast records carrying ``family``, ``p_value``/
            ``p_value_raw``, ``p_value_adj`` (the published value) and
            ``confounded``.
        family_key: The record key naming the BH family.
        q: FDR threshold.

    Returns:
        One summary record per family: membership before and after, the
        significance counts before and after, and the per-member q-values.
    """
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        grouped.setdefault(record[family_key], []).append(record)

    summaries: list[dict[str, Any]] = []
    for family, members in sorted(grouped.items()):
        retained = [m for m in members if not m["confounded"]]
        dropped = [m for m in members if m["confounded"]]
        raw = [float(m.get("p_value_raw", m.get("p_value"))) for m in retained]
        adjusted = apply_bh_correction(raw, q=q) if raw else []

        published_sig = sum(1 for m in members if float(m["p_value_adj"]) < q)
        published_sig_retained = sum(1 for m in retained if float(m["p_value_adj"]) < q)
        new_sig = sum(1 for value in adjusted if value < q)

        summaries.append(
            {
                "family": family,
                "n_published": len(members),
                "n_dropped": len(dropped),
                "n_retained": len(retained),
                "significant_published_all": published_sig,
                "significant_published_retained": published_sig_retained,
                "significant_recomputed": new_sig,
                "dropped_members": [
                    {"group": m["group"], "question": m["question"]} for m in dropped
                ],
                "members": [
                    {
                        "group": m["group"],
                        "question": m["question"],
                        "label_a": m["label_a"],
                        "label_b": m["label_b"],
                        "p_raw": float(m.get("p_value_raw", m.get("p_value"))),
                        "q_published": round(float(m["p_value_adj"]), 6),
                        "q_recomputed": round(adjusted[i], 6),
                        "status_changed": (float(m["p_value_adj"]) < q) != (adjusted[i] < q),
                    }
                    for i, m in enumerate(retained)
                ],
            }
        )
    return summaries


# --- the previous revision: before -> after ---------------------------------- #


def git_show_text(ref: str, rel_path: str) -> str:
    """Return a committed file's text at a commit (``git show ref:path``).

    Args:
        ref: Commit-ish.
        rel_path: Repository-relative path.

    Returns:
        The file's text.

    Raises:
        subprocess.CalledProcessError: If git cannot show the file.
    """
    return subprocess.check_output(["git", "show", f"{ref}:{rel_path}"], cwd=BASE_DIR).decode()


def read_baseline(
    ref: str, reader: Callable[[str, str], str] = git_show_text
) -> dict[str, Any]:
    """Read the previous revision's committed outputs, for before -> after.

    Args:
        ref: Commit holding the previous revision's outputs.
        reader: ``(ref, path) -> text``; injectable for tests.

    Returns:
        ``{"ref", "boards", "families"}``. Each board carries its counts, its
        pairs keyed by unordered label pair, and its conditions' F1 and tier;
        each family (keyed by (artefact, family)) its counts and members keyed
        by (group, question, label_a, label_b).
    """
    boards: dict[str, Any] = {}
    for name in BOARDS:
        manifest = json.loads(reader(ref, f"{OUTPUT_ROOT}/{name}/run_manifest.json"))
        metadata = manifest["metadata"]
        rows = csv.DictReader(io.StringIO(reader(ref, f"{OUTPUT_ROOT}/{name}/leaderboard.csv")))
        boards[name] = {
            "n_pairs": int(metadata["n_comparisons"]),
            "n_conditions": int(metadata["n_conditions"]),
            "n_significant": int(metadata["fdr_correction"]["n_significant"]),
            "n_tiers": int(metadata["tiering"]["n_tiers"]),
            "source_n_comparisons": int(metadata["provenance"]["source_n_comparisons"]),
            "source_n_significant": int(metadata["provenance"]["source_n_significant"]),
            "pairs": {
                frozenset({entry["label_a"], entry["label_b"]}): entry
                for entry in manifest["comparisons"]
            },
            "conditions": {
                row["condition"]: {"f1": float(row["f1"]), "tier": int(row["tier"])}
                for row in rows
            },
        }
    families_doc = json.loads(reader(ref, f"{OUTPUT_ROOT}/bh-families/families_recomputed.json"))
    families = {
        (family["artefact"], family["family"]): {
            "n_retained": int(family["n_retained"]),
            "significant_recomputed": int(family["significant_recomputed"]),
            "members": {
                (m["group"], m["question"], m["label_a"], m["label_b"]): m
                for m in family["members"]
            },
        }
        for family in families_doc["families"]
    }
    return {"ref": ref, "boards": boards, "families": families}


def revision_diff(
    baseline: Mapping[str, Any],
    board_results: Mapping[str, Mapping[str, Any]],
    family_results: Sequence[Mapping[str, Any]],
    q: float = FDR_Q,
) -> dict[str, Any]:
    """Compare this run's outputs with the previous revision's.

    Pairs and conditions are matched by label; a pair, condition or family
    member present in one revision but not the other is refused, because the
    regeneration must change values, never membership.

    Args:
        baseline: The previous revision, from :func:`read_baseline`.
        board_results: This run's per-board results (``process_board``).
        family_results: This run's affected-family summaries.
        q: FDR threshold.

    Returns:
        ``{"ref", "boards", "families"}`` holding before/after counts, every
        verdict that changed, every retained condition whose F1 or tier moved,
        and how many raw p-values moved.

    Raises:
        AssertionError: On any membership difference.
    """
    boards: dict[str, Any] = {}
    for name, result in board_results.items():
        before = baseline["boards"][name]
        board: Board = result["new_board"]
        after = {test.key: (test, board.adjusted[i]) for i, test in enumerate(board.tests)}
        assert set(after) == set(before["pairs"]), f"{name}: the retained pair set changed"
        assert set(board.order) == set(before["conditions"]), (
            f"{name}: the retained condition set changed"
        )

        verdicts: list[dict[str, Any]] = []
        p_moved = 0
        for key, (test, q_after) in sorted(after.items(), key=lambda item: sorted(item[0])):
            entry = before["pairs"][key]
            p_before = float(entry["p_value_raw"])
            p_moved += abs(p_before - test.p_value) > 1e-12
            sig_before, sig_after = bool(entry["significant"]), q_after < q
            if sig_before != sig_after:
                verdicts.append(
                    {
                        "condition_a": test.label_a,
                        "condition_b": test.label_b,
                        "p_before": p_before,
                        "p_after": test.p_value,
                        "q_before": float(entry["p_value_adj"]),
                        "q_after": round(q_after, 6),
                        "significant_before": sig_before,
                        "significant_after": sig_after,
                    }
                )

        conditions: list[dict[str, Any]] = []
        for label in board.order:
            old = before["conditions"][label]
            f1_after = round(board.metrics[label]["f1"], 6)
            tier_after = board.tier_of(label)
            if abs(old["f1"] - f1_after) > 5e-7 or old["tier"] != tier_after:
                conditions.append(
                    {
                        "condition": label,
                        "f1_before": old["f1"],
                        "f1_after": f1_after,
                        "tier_before": old["tier"],
                        "tier_after": tier_after,
                    }
                )

        boards[name] = {
            "n_pairs": len(board.tests),
            "n_conditions": len(board.order),
            "full_significant_before": before["source_n_significant"],
            "full_significant_after": result["n_significant_full"],
            "full_pairs": result["n_pairs_full"],
            "significant_before": before["n_significant"],
            "significant_after": board.n_significant,
            "tiers_before": before["n_tiers"],
            "tiers_after": len(board.tiers),
            "p_moved": p_moved,
            "verdict_changes": verdicts,
            "condition_moves": conditions,
        }

    families: list[dict[str, Any]] = []
    for family in family_results:
        before = baseline["families"][(family["artefact"], family["family"])]
        members = {
            (m["group"], m["question"], m["label_a"], m["label_b"]): m for m in family["members"]
        }
        assert set(members) == set(before["members"]), (
            f"{family['artefact']}:{family['family']}: the retained member set changed"
        )
        verdicts = []
        p_moved = 0
        for key, member in members.items():
            old = before["members"][key]
            p_moved += abs(float(old["p_raw"]) - member["p_raw"]) > 1e-12
            sig_before = float(old["q_recomputed"]) < q
            sig_after = member["q_recomputed"] < q
            if sig_before != sig_after:
                verdicts.append(
                    {
                        "group": member["group"],
                        "question": member["question"],
                        "condition_a": member["label_a"],
                        "condition_b": member["label_b"],
                        "p_before": float(old["p_raw"]),
                        "p_after": member["p_raw"],
                        "q_before": float(old["q_recomputed"]),
                        "q_after": member["q_recomputed"],
                        "significant_before": sig_before,
                        "significant_after": sig_after,
                    }
                )
        families.append(
            {
                "artefact": family["artefact"],
                "family": family["family"],
                "n_retained": family["n_retained"],
                "significant_before": before["significant_recomputed"],
                "significant_after": family["significant_recomputed"],
                "p_moved": p_moved,
                "verdict_changes": verdicts,
            }
        )
    return {"ref": baseline["ref"], "boards": boards, "families": families}


# --- rendering ------------------------------------------------------------- #


def _fmt(value: float, places: int = 3) -> str:
    """Format a float for a Markdown or comma-separated-values (CSV) cell.

    Args:
        value: The number to format.
        places: Decimal places.

    Returns:
        Fixed-point string.
    """
    return f"{value:.{places}f}"


# --- the revision trail ---------------------------------------------------- #

#: The 2026-08-02 summary's changelog entry, verbatim (history is not rewritten).
ORIGINAL_SUMMARY_ENTRY = (
    f"Trigger: PI ruling on protocol erratum {ERRATUM}, option (a) — "
    "drop the confounded cells and regenerate rather than splice in "
    "the matched-scope replacements. Produced the regenerated "
    "23-condition "
    "boards at both buffers, the recomputed BH families, and this "
    "summary. Nothing under `results/pairwise/` was modified; the "
    "superseded dated snapshots carry banners pointing here."
)

#: Original-publication stub for the documents that had no changelog.
ORIGINAL_STUB = (
    "First version, written by `scripts/regen_e43_board.py` at `bc45133b4` and "
    f"committed in `2f3ef020a` under protocol erratum {ERRATUM}, option (a): the "
    "March round-robin with the three coverage-confounded `flash-min-text-t10` "
    "cells dropped, BH recomputed over the retained family, and the greedy-clique "
    "tiers re-run. It carried a banner and no changelog."
)


def revision_history(revision: Revision) -> list[Revision]:
    """Return ``revision`` and every earlier revision, newest first.

    Args:
        revision: A member of :data:`REVISIONS`.

    Returns:
        The revisions up to and including ``revision``, newest first.
    """
    index = REVISIONS.index(revision)
    return list(reversed(REVISIONS[: index + 1]))


def banner_lines(revision: Revision, original_banner: str) -> list[str]:
    """Return a document's top-of-document banner for a revision.

    The original revision keeps its 2026-08-02 banner verbatim; every later
    revision names itself, its predecessor, and the changelog, so the trail is
    kept rather than overwritten.

    Args:
        revision: The revision being rendered.
        original_banner: The document's 2026-08-02 banner line, verbatim.

    Returns:
        The banner line followed by a blank line.
    """
    if revision.is_original:
        return [original_banner, ""]
    prior = revision_history(revision)[1]
    return [
        f"> **Last revised**: {revision.date.isoformat()} ({revision.reason}). "
        f"Prior: {prior.date.isoformat()} ({prior.reason}). See "
        "[§ Changelog](#changelog) for revision history.",
        "",
    ]


def _verdict(significant: bool) -> str:
    """Return the table word for a BH verdict."""
    return "significant" if significant else "ns"


def restated_trigger(n_dated: int) -> str:
    """Return the 2026-10-30 revision's trigger sentence.

    Args:
        n_dated: Number of dated March records read through the runs beside
            them.

    Returns:
        Markdown paragraph text.
    """
    return (
        "**Trigger**: the S164 restatement pass regenerated `results/pairwise/` in "
        f"place on the consensus route of PI ruling D60 (3) (`{RESTATEMENT_COMMIT}`; "
        "PR #52, merged as `0d195cac8`). The per-pair files that read the two "
        "drifted single-pass arms stay at their paths as dated March records, with "
        f"today's runs beside them under `{BESIDE_ROOT}/` (D61 (2)); this revision "
        f"reads those runs in place of the {n_dated} records the boards and families "
        "use. The PI queued the regeneration as D69 Q15. No permutation test was "
        "re-run."
    )


def board_changelog_lines(
    revision: Revision, diff: Mapping[str, Any] | None, name: str, n_dated: int
) -> list[str]:
    """Return a per-board document's ``## Changelog`` (later revisions only).

    Args:
        revision: The revision being rendered.
        diff: The before -> after record (:func:`revision_diff`), or None.
        name: Board identifier.
        n_dated: Number of dated records read through the runs beside them.

    Returns:
        Markdown lines; empty for the original revision, which had none.
    """
    if revision.is_original:
        return []
    lines = ["## Changelog", ""]
    for entry in revision_history(revision):
        lines.extend([f"### {entry.date.isoformat()} — {entry.title}", ""])
        if entry.is_original:
            lines.extend([ORIGINAL_STUB, ""])
            continue
        lines.extend(
            [
                restated_trigger(n_dated) + " The full entry is in "
                "[`../summary.md` § Changelog](../summary.md#changelog).",
                "",
            ]
        )
        if diff is None or entry is not revision:
            continue
        board = diff["boards"][name]
        before, after = REVISIONS[REVISIONS.index(entry) - 1].date, entry.date
        lines.extend(
            [
                f"| Figure | {before.isoformat()} | {after.isoformat()} |",
                "|---|--:|--:|",
                f"| BH-significant pairs | {board['significant_before']} of "
                f"{board['n_pairs']} | {board['significant_after']} of {board['n_pairs']} |",
                f"| Tiers | {board['tiers_before']} | {board['tiers_after']} |",
                f"| Retained pairs whose raw p moved | — | {board['p_moved']} of "
                f"{board['n_pairs']} |",
                f"| Retained conditions whose F1 or tier moved | — | "
                f"{len(board['condition_moves'])} of {board['n_conditions']} |",
                "",
            ]
        )
        if board["condition_moves"]:
            lines.extend(
                [
                    f"| Condition | F1 ({before.isoformat()}) | F1 ({after.isoformat()}) | "
                    f"Tier ({before.isoformat()}) | Tier ({after.isoformat()}) |",
                    "|---|:---:|:---:|--:|--:|",
                ]
            )
            for move in board["condition_moves"]:
                lines.append(
                    f"| {move['condition']} | {move['f1_before']:.6f} | "
                    f"{move['f1_after']:.6f} | {move['tier_before']} | {move['tier_after']} |"
                )
            lines.append("")
        changes = board["verdict_changes"]
        lines.extend(
            [
                f"BH verdicts that changed between the two revisions: {len(changes)}"
                + (" (see the summary's changelog)." if changes else "."),
                "",
                f"Not changed: the {board['n_conditions']} retained conditions and "
                f"{board['n_pairs']} retained pairs, the dropped cells, and the method.",
                "",
            ]
        )
    return lines


#: Short names § 3.1 uses for the conditions at the tier boundary it explains.
#: A boundary drawn between other conditions raises, so the paragraph is
#: rewritten by hand rather than mislabelled.
BOUNDARY_OPENER_SHORT = {"flash-high-text N=10 N=10, 9-of-10": "flash-high-text N=10"}
BOUNDARY_PAIR_SHORT = {
    "flash-high-text N=30 N=30, 26-of-30": "FH text 26/30",
    "flash-high-text N=10 N=10, 9-of-10": "FH text 9/10",
}

_NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def _f1_span(values: Sequence[float]) -> str:
    """Format a set of F1 values as one 3-place value, or a min–max span."""
    low, high = _fmt(min(values)), _fmt(max(values))
    return low if low == high else f"{low}–{high}"


def published_order_facts(full_board: Board, reconciliation: Mapping[str, Any]) -> dict[str, Any]:
    """Compute the figures summary § 3.1 quotes, from the full 20 m board.

    The 2026-08-02 renderer quoted them as literals (F1 0.778, the 0.814
    clique, F1 0.797, q = 0.046), which go stale when the inputs are restated;
    they are now computed, and the paragraph's structure is asserted.

    Args:
        full_board: The recomputed FULL 20 m board.
        reconciliation: :func:`reconcile_published_order`'s record.

    Returns:
        The transposed condition, its published rank, F1 and higher-F1 count;
        the F1 span of the clique it joins in the published order; the
        condition that opens its tier in F1 order, with that condition's F1;
        the single significant pair drawing the boundary, with its q; and every
        other published-order inversion, each with whether it moves a tier.

    Raises:
        AssertionError: If more or fewer than one condition changes tier, the
            boundary rests on other than exactly one significant pair, or
            another inversion straddles a tier boundary.
    """
    differences = reconciliation["ordering_differences"]
    assert len(differences) == 1, f"§ 3.1 expects one ordering difference, got {differences}"
    moved = differences[0]["condition"]
    order = PUBLISHED_20M_RANK_ORDER
    f1 = {label: full_board.metrics[label]["f1"] for label in order}
    rank = order.index(moved) + 1
    higher_later = [label for label in order[rank:] if f1[label] > f1[moved]]

    replay = greedy_clique_tiers(order, full_board.significant)
    replay_tier = next(tier for tier in replay if moved in tier)
    clique = [f1[label] for label in replay_tier if label != moved]

    own_index = next(i for i, tier in enumerate(full_board.tiers) if moved in tier)
    opener = full_board.tiers[own_index][0]
    previous = full_board.tiers[own_index - 1]
    adjusted = {test.key: full_board.adjusted[i] for i, test in enumerate(full_board.tests)}
    boundary = [m for m in previous if full_board.significant[frozenset({opener, m})]]
    assert len(boundary) == 1, f"§ 3.1 expects one boundary pair, got {boundary}"

    replay_index = {label: i for i, tier in enumerate(replay) for label in tier}
    own_tier = {label: i for i, tier in enumerate(full_board.tiers) for label in tier}
    others = []
    for i, first in enumerate(order):
        for second in order[i + 1 :]:
            if first == moved or second == moved or f1[first] >= f1[second]:
                continue
            same = (
                replay_index[first] == replay_index[second]
                and own_tier[first] == own_tier[second]
            )
            assert same, f"§ 3.1: inversion {first!r} / {second!r} straddles a tier boundary"
            others.append(
                {
                    "rank_a": i + 1,
                    "rank_b": order.index(second) + 1,
                    "label_a": first,
                    "label_b": second,
                    "f1_a": f1[first],
                    "f1_b": f1[second],
                }
            )
    return {
        "moved": moved,
        "moved_rank": rank,
        "moved_f1": f1[moved],
        "n_higher_later": len(higher_later),
        "clique_span": _f1_span(clique),
        "opener": opener,
        "opener_f1": f1[opener],
        "boundary_member": boundary[0],
        "boundary_q": adjusted[frozenset({opener, boundary[0]})],
        "other_inversions": others,
    }


def ordering_paragraph(facts: Mapping[str, Any]) -> str:
    """Render summary § 3.1's explanatory paragraph from computed facts.

    Args:
        facts: :func:`published_order_facts`'s record.

    Returns:
        Markdown paragraph text. On the March inputs it is the 2026-08-02
        paragraph exactly.

    Raises:
        KeyError: If the boundary is drawn between conditions other than the
            ones the paragraph names.
    """
    others = facts["other_inversions"]
    lead = "one condition out of F1 order" + (" in a way that moves a tier" if others else "")
    text = (
        "Greedy-clique tiering is order-dependent, and the published 20 m "
        f"snapshot (`results/paper-tables/leaderboard_tiers_20m.md`) ranks {lead}: "
        f"`{facts['moved']}` (F1 {_fmt(facts['moved_f1'])}) sits at rank "
        f"{facts['moved_rank']}, ahead of {_NUMBER_WORDS[facts['n_higher_later']]} "
        f"higher-F1 conditions. Processed there it joins the {facts['clique_span']} "
        "clique; processed in strict F1 order it is reached only after "
        f"`{BOUNDARY_OPENER_SHORT[facts['opener']]}` (F1 {_fmt(facts['opener_f1'])}) "
        "has already opened the next tier — and that boundary rests on a single "
        f"borderline pair (`{BOUNDARY_PAIR_SHORT[facts['boundary_member']]}` versus "
        f"`{BOUNDARY_PAIR_SHORT[facts['opener']]}`, q = {facts['boundary_q']:.3f})."
    )
    for other in others:
        text += (
            f" The published order also places rank {other['rank_a']} "
            f"(`{other['label_a']}`, F1 {_fmt(other['f1_a'])}) ahead of rank "
            f"{other['rank_b']} (`{other['label_b']}`, F1 {_fmt(other['f1_b'])}) on "
            "these inputs, but the two share a tier under either order, so that "
            "swap moves nothing."
        )
    return text


def gate_lines(
    results: Mapping[str, Any],
    revision: Revision,
    diff: Mapping[str, Any] | None,
    n_dated: int,
) -> list[str]:
    """Render summary § 2's gate list for a revision.

    Args:
        results: The assembled results structure built by :func:`main`.
        revision: The revision being rendered.
        diff: The before -> after record, or None.
        n_dated: Number of dated records read through the runs beside them.

    Returns:
        Markdown lines, ending with a blank line. The original revision's are
        its 2026-08-02 text verbatim.
    """
    boards = results["boards"]
    counts = "; ".join(
        f"`{name}` {boards[name]['n_significant_full']}/"
        f"{boards[name]['n_pairs_full']} significant, "
        f"{boards[name]['n_tiers_full']} tiers"
        for name in boards
    )
    gate_d = (
        "- **Gate D** — replaying the greedy clique under the *published* "
        "20 m rank order reproduces the published tier sizes "
        f"({', '.join(str(n) for n in PUBLISHED_20M_TIER_SIZES)}) exactly. "
        "See § 3.1 for why this gate exists."
    )
    if revision.is_original:
        return [
            "All three gates passed before anything was written:",
            "",
            "- **Gate A** — the per-pair JSONs reproduce each board's committed "
            "`run_manifest.json` exactly (same pair set, same raw p-values, "
            "same ΔF1).",
            "- **Gate B** — recomputing the FULL board (nothing dropped) "
            "reproduces the published snapshot: "
            + counts
            + ". This proves the BH and tiering reimplementation is faithful "
            "before its output is trusted for the reduced board.",
            "- **Gate C** — every condition's F1, precision, recall and "
            "detection count agree across all tests it appears in.",
            gate_d,
            "",
        ]
    superseded = ""
    if diff is not None:
        moved = [
            f"{board['full_significant_before']} at `{name}`"
            for name, board in diff["boards"].items()
            if board["full_significant_before"] != board["full_significant_after"]
        ]
        if moved:
            superseded = (
                "; the previous revision's " + ", ".join(moved) + " came from the "
                "superseded March run"
            )
    return [
        "All four gates passed before anything was written:",
        "",
        "- **Gate A** — the per-pair JSONs reproduce each board's committed "
        "`run_manifest.json` exactly (same pair set, same raw p-values, same ΔF1), "
        "and each hypothesis family's raw p-values equal its per-test JSONs. "
        f"Where a per-pair file is a dated March record ({n_dated} of them), "
        "today's run beside it is read in its place, after checking that the two "
        "name the same test and that the record is the older; a beside file with "
        "no record next to it is refused.",
        "- **Gate B** — recomputing the FULL board (nothing dropped) reproduces "
        "each board's own run as its BH artefact (`fdr/pairwise_results_fdr.json`) "
        f"records it: {counts}, with every pair's adjusted value equal to the "
        "run's. The significance count is the run's own, as the PI specified "
        f"(D69 Q15){superseded}; the tier count is the published snapshot's. This "
        "proves the BH and tiering reimplementation is faithful before its output "
        "is trusted for the reduced board.",
        "- **Gate C** — every condition's F1, precision, recall and detection "
        "count agree across all tests it appears in. The dated March records "
        "are a different vintage and are not mixed in.",
        gate_d,
        "",
    ]


def summary_changelog_entry(
    results: Mapping[str, Any],
    revision: Revision,
    diff: Mapping[str, Any] | None,
    n_dated: int,
) -> list[str]:
    """Render a later revision's entry in the summary's changelog.

    Args:
        results: The assembled results structure built by :func:`main`.
        revision: The revision whose entry this is.
        diff: The before -> after record (:func:`revision_diff`), or None.
        n_dated: Number of dated records read through the runs beside them.

    Returns:
        Markdown lines, ending with a blank line.
    """
    lines = [
        restated_trigger(n_dated),
        "",
        "**Script changes** (the PI's specification, D69 Q15): Gates A and C read "
        "today's run beside each dated record, after checking that the two name "
        "the same test and that the record is the older; Gate B takes each "
        "board's significance count from the board's own run and also matches "
        "every pair's adjusted value; the renderers keep this revision trail; "
        "and § 3.1's figures are computed rather than quoted.",
        "",
    ]
    if diff is None:
        return lines
    before = REVISIONS[REVISIONS.index(revision) - 1].date.isoformat()
    after = revision.date.isoformat()
    lines.extend(
        [
            "**Key figures**:",
            "",
            f"| Figure | {before} | {after} |",
            "|---|--:|--:|",
        ]
    )
    for name, board in diff["boards"].items():
        n_pairs, n_full = board["n_pairs"], board["full_pairs"]
        lines.extend(
            [
                f"| `{name}` full board: BH-significant | "
                f"{board['full_significant_before']} of {n_full} | "
                f"{board['full_significant_after']} of {n_full} |",
                f"| `{name}` regenerated board: BH-significant | "
                f"{board['significant_before']} of {n_pairs} | "
                f"{board['significant_after']} of {n_pairs} |",
                f"| `{name}` regenerated board: tiers | {board['tiers_before']} | "
                f"{board['tiers_after']} |",
                f"| `{name}`: retained pairs whose raw p moved | — | "
                f"{board['p_moved']} of {n_pairs} |",
                f"| `{name}`: retained conditions whose F1 or tier moved | — | "
                f"{len(board['condition_moves'])} of {board['n_conditions']} |",
            ]
        )
    for family in diff["families"]:
        n = family["n_retained"]
        lines.extend(
            [
                f"| `{family['artefact']}` `{family['family']}`: BH-significant "
                f"(retained) | {family['significant_before']} of {n} | "
                f"{family['significant_after']} of {n} |",
                f"| `{family['artefact']}` `{family['family']}`: members whose raw "
                f"p moved | — | {family['p_moved']} of {n} |",
            ]
        )
    lines.append("")

    rows: list[str] = []
    for name, board in diff["boards"].items():
        for change in board["verdict_changes"]:
            rows.append(
                f"| `{name}` | {change['condition_a']} | {change['condition_b']} | "
                f"{change['p_before']:.4f} → {change['p_after']:.4f} | "
                f"{change['q_before']:.6f} → {change['q_after']:.6f} | "
                f"{_verdict(change['significant_before'])} → "
                f"{_verdict(change['significant_after'])} |"
            )
    for family in diff["families"]:
        for change in family["verdict_changes"]:
            rows.append(
                f"| `{family['artefact']}` `{family['family']}`, group "
                f"{change['group']} — {change['question']} | {change['condition_a']} | "
                f"{change['condition_b']} | "
                f"{change['p_before']:.4f} → {change['p_after']:.4f} | "
                f"{change['q_before']:.6f} → {change['q_after']:.6f} | "
                f"{_verdict(change['significant_before'])} → "
                f"{_verdict(change['significant_after'])} |"
            )
    lines.append(
        f"**BH verdicts that changed** (the same retained pair or family member, "
        f"{before} → {after}): {len(rows)}."
    )
    lines.append("")
    if rows:
        lines.extend(
            [
                "| Artefact | Condition A | Condition B | p (raw) | q | Verdict |",
                "|---|---|---|---|---|---|",
                *rows,
                "",
            ]
        )

    tier_rows = [
        f"| `{name}` | {move['condition']} | {move['tier_before']} | {move['tier_after']} |"
        for name, board in diff["boards"].items()
        for move in board["condition_moves"]
        if move["tier_before"] != move["tier_after"]
    ]
    if tier_rows:
        lines.extend(
            [
                "**Tier changes on the regenerated boards**:",
                "",
                f"| Board | Condition | Tier ({before}) | Tier ({after}) |",
                "|---|---|--:|--:|",
                *tier_rows,
                "",
            ]
        )
    else:
        lines.extend(
            [
                "**Tier changes on the regenerated boards**: none; every retained "
                "condition keeps its tier number. The F1 moves are listed in each "
                "board's `leaderboard.md` changelog.",
                "",
            ]
        )
    lines.extend(
        [
            "**Not changed**: the dropped conditions and every retained pair, "
            "condition and family member (the membership is checked, not "
            "assumed); the provenance walk's inventory of "
            f"{len(results['confounded_files'])} confounded per-pair files under "
            "`results/pairwise/`; the method (BH within each declared family at "
            f"q = {FDR_Q}; greedy clique in F1-descending order). The previous "
            f"revision's outputs were read at `{diff['ref']}`.",
            "",
        ]
    )
    return lines


def render_leaderboard_md(
    board: Board,
    buffer_m: int,
    dropped: Sequence[str],
    revision: Revision = LATEST_REVISION,
    diff: Mapping[str, Any] | None = None,
    n_dated: int = 0,
) -> str:
    """Render the regenerated leaderboard table as Markdown.

    Args:
        board: The regenerated board.
        buffer_m: Spatial buffer in metres.
        dropped: Labels of the dropped confounded conditions.
        revision: The revision being rendered (default: the latest).
        diff: The before -> after record for the changelog, or None.
        n_dated: Number of dated records read through the runs beside them.

    Returns:
        Markdown document text.
    """
    name = f"leaderboard-{buffer_m}m"
    lines = [
        f"# Regenerated leaderboard — {len(board.order)} conditions "
        f"({buffer_m} m buffer, {ERRATUM})",
        "",
        *banner_lines(
            revision,
            f"> **Last revised**: {REMEDIATION_DATE.isoformat()} (original "
            f"publication — {ERRATUM} remediation). Regenerated from the March "
            "round-robin with the coverage-confounded cells dropped.",
        ),
        f"Dropped under {ERRATUM} (240-tile study scored against 487-tile "
        "bounds): " + ", ".join(f"`{label}`" for label in dropped) + ".",
        "",
        f"Retained pairs: **{len(board.tests)}**; BH-significant at "
        f"q = {FDR_Q}: **{board.n_significant}**; tiers: **{len(board.tiers)}**.",
        "",
        "| Rank | Condition | Tier | F1 | P | R | Detections |",
        "|--:|---|--:|:---:|:---:|:---:|--:|",
    ]
    for rank, label in enumerate(board.order, start=1):
        metric = board.metrics[label]
        lines.append(
            f"| {rank} | {label} | {board.tier_of(label)} | "
            f"{_fmt(metric['f1'])} | {_fmt(metric['precision'])} | "
            f"{_fmt(metric['recall'])} | {int(metric['n_detections'])} |"
        )
    lines.append("")
    if revision.is_original:
        lines.append(
            "Tile-level MCC is not reproduced here — the permutation artefacts "
            "carry only mound-level counts. Dropping whole cells does not change "
            "any retained condition's metrics, so the MCC column of the dated "
            "snapshot remains valid for these rows."
        )
    else:
        # After the 2026-10-15 restatement the retained rows' mound-level
        # metrics differ from the March snapshot's, and whether its tile-level
        # values moved with them is not established, so do not assert them.
        lines.append(
            "Tile-level MCC is not reproduced here — the permutation artefacts "
            "carry only mound-level counts. Dropping whole cells does not change "
            "any retained condition's metrics, but the MCC column of the dated "
            "March snapshot keeps its March 2026 values, which predate the "
            "2026-10-15 restatement of the mound-level metrics above; it is not "
            "asserted current for these rows."
        )
    lines.append("")
    lines.extend(board_changelog_lines(revision, diff, name, n_dated))
    return "\n".join(lines)


def render_tiers_md(
    board: Board,
    buffer_m: int,
    dropped: Sequence[str],
    revision: Revision = LATEST_REVISION,
    diff: Mapping[str, Any] | None = None,
    n_dated: int = 0,
) -> str:
    """Render the regenerated tier table as Markdown.

    Args:
        board: The regenerated board.
        buffer_m: Spatial buffer in metres.
        dropped: Labels of the dropped confounded conditions.
        revision: The revision being rendered (default: the latest).
        diff: The before -> after record for the changelog, or None.
        n_dated: Number of dated records read through the runs beside them.

    Returns:
        Markdown document text.
    """
    lines = [
        f"# Regenerated tier clustering — {len(board.order)} conditions "
        f"({buffer_m} m buffer, FDR-corrected, {ERRATUM})",
        "",
        *banner_lines(
            revision,
            f"> **Last revised**: {REMEDIATION_DATE.isoformat()} (original "
            f"publication — {ERRATUM} remediation).",
        ),
        "Conditions within a tier are statistically indistinguishable (all "
        f"pairwise BH-adjusted p-values >= {FDR_Q}). Based on "
        f"{len(board.tests)} retained permutation tests (10,000 permutations, "
        f"seed 42) among the {len(board.order)} retained conditions, "
        f"BH-corrected at q = {FDR_Q} over the retained family.",
        "",
        f"Dropped under {ERRATUM}: " + ", ".join(f"`{label}`" for label in dropped) + ".",
        "",
    ]
    for index, tier in enumerate(board.tiers, start=1):
        f1s = [board.metrics[label]["f1"] for label in tier]
        span = _fmt(min(f1s)) if len(tier) == 1 else f"{_fmt(min(f1s))}–{_fmt(max(f1s))}"
        lines.extend(
            [
                f"## Tier {index} (F1: {span})",
                "",
                "| # | Condition | F1 | P | R |",
                "|--:|---|:---:|:---:|:---:|",
            ]
        )
        for label in tier:
            rank = board.order.index(label) + 1
            metric = board.metrics[label]
            lines.append(
                f"| {rank} | {label} | {_fmt(metric['f1'])} | "
                f"{_fmt(metric['precision'])} | {_fmt(metric['recall'])} |"
            )
        lines.append("")
    lines.extend(board_changelog_lines(revision, diff, f"leaderboard-{buffer_m}m", n_dated))
    return "\n".join(lines)


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str]) -> None:
    """Write rows to a CSV file.

    Args:
        path: Destination path (parents are created).
        rows: Row mappings.
        fieldnames: Column order.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def board_manifest(
    board: Board,
    full_board: Board,
    buffer_m: int,
    source_dir: str,
    dropped_conditions: Sequence[str],
    n_dropped_pairs: int,
    revision: Revision = LATEST_REVISION,
    dated_records: Sequence[DatedRecord] = (),
) -> dict[str, Any]:
    """Assemble ``run_manifest``-style metadata for a regenerated board.

    Args:
        board: The regenerated board.
        full_board: The recomputed full board (provenance/comparison).
        buffer_m: Spatial buffer in metres.
        source_dir: Repository-relative path of the source permutation run.
        dropped_conditions: Labels dropped under E72.
        n_dropped_pairs: Number of pairs dropped.
        revision: The revision being rendered (default: the latest).
        dated_records: This board's dated March records, each read through
            today's run beside it.

    Returns:
        Manifest dictionary ready to serialise. Revisions after the original
        add ``metadata.provenance.revision``, naming the input layout and every
        dated record with the run read in its place.
    """
    manifest = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "script": "regen_e43_board.py",
            "version": revision.output_version,
            "git_commit": git_commit(),
            "buffer_metres": buffer_m,
            "n_permutations": 10000,
            "seed": 42,
            "n_comparisons": len(board.tests),
            "n_conditions": len(board.order),
            "fdr_correction": {
                "method": "Benjamini-Hochberg",
                "q": FDR_Q,
                "family_size": len(board.tests),
                "n_significant": board.n_significant,
            },
            "tiering": {
                "method": "greedy clique over BH-significant pairs",
                "implementation": "scripts/n1_baseline_leaderboard_tiering.greedy_clique_tiers",
                "n_tiers": len(board.tiers),
            },
            "provenance": {
                "erratum": ERRATUM,
                "source_run": source_dir,
                "source_n_comparisons": len(full_board.tests),
                "source_n_conditions": len(full_board.order),
                "source_n_significant": full_board.n_significant,
                "source_n_tiers": len(full_board.tiers),
                "dropped_conditions": list(dropped_conditions),
                "dropped_pairs": n_dropped_pairs,
                "confounded_study": f"outputs/h11/{CONFOUNDED_STUDY_MARKER}",
                "note": (
                    "Regenerated per protocol erratum E72: the dropped cells score a "
                    "240-tile study against 487-tile evaluation bounds, so every mound "
                    "in the 247 unprocessed tiles counts as an automatic false negative "
                    "and that arm's F1 is understated by roughly 0.17-0.19. No "
                    "permutation test was re-run; the retained pairs' observed statistics "
                    "are read verbatim from the committed per-pair artefacts and only the "
                    "BH family and the tier clustering are recomputed. Matched-scope "
                    "replacements are filed separately at results/e43-matched-temperature/ "
                    "and are deliberately NOT spliced into this board."
                ),
            },
        },
        "comparisons": [
            {
                "label_a": test.label_a,
                "label_b": test.label_b,
                "f1_a": test.f1_a,
                "f1_b": test.f1_b,
                "delta_f1": test.delta_f1,
                "p_value_raw": test.p_value,
                "p_value_adj": round(board.adjusted[index], 6),
                "significant": board.adjusted[index] < FDR_Q,
                "source_file": test.source_file,
            }
            for index, test in enumerate(board.tests)
        ],
    }
    if not revision.is_original:
        manifest["metadata"]["provenance"]["revision"] = revision_provenance(
            revision, dated_records
        )
    return manifest


def revision_provenance(
    revision: Revision, dated_records: Sequence[DatedRecord]
) -> dict[str, Any]:
    """Describe a later revision's inputs for a JSON manifest.

    Args:
        revision: The revision being rendered.
        dated_records: The dated March records read through the runs beside them.

    Returns:
        A JSON-ready mapping.
    """
    return {
        "date": revision.date.isoformat(),
        "reason": revision.reason,
        "previous_revision_outputs": revision.baseline_ref,
        "input_layout": (
            f"{PAIRWISE_ROOT}/ as restated in place by {RESTATEMENT_COMMIT} (S164 pass); "
            f"today's runs of the dated March records stand beside them under {BESIDE_ROOT}/"
        ),
        "n_dated_records": len(dated_records),
        "dated_records": [
            {"record": record.record_file, "read_in_its_place": record.current_file}
            for record in dated_records
        ],
    }


def render_summary_md(results: Mapping[str, Any]) -> str:
    """Render the top-level summary document for the regeneration.

    Args:
        results: The assembled results structure built by :func:`main`. Its
            optional ``revision`` (default: the latest), ``diff`` (the
            before -> after record) and ``n_dated`` (dated records read through
            the runs beside them) select and fill the revision trail.

    Returns:
        Markdown document text.
    """
    revision: Revision = results.get("revision", LATEST_REVISION)
    diff: Mapping[str, Any] | None = results.get("diff")
    n_dated = int(results.get("n_dated", 0))
    if revision.is_original:
        produced = (
            f"**Produced**: {REMEDIATION_DATE.isoformat()}, on sapphire, from "
            f"repository commit `{results['git_commit']}` by "
            "`scripts/regen_e43_board.py`. Zero application programming interface "
            "(API) calls; zero permutation tests re-run."
        )
    else:
        produced = (
            f"**Produced**: {revision.date.isoformat()}, on {revision.host}, from "
            f"repository commit `{results['git_commit']}` by "
            "`scripts/regen_e43_board.py`, over `results/pairwise/` as restated in "
            f"place by the S164 pass (`{RESTATEMENT_COMMIT}`), reading today's run "
            f"beside each of its {n_dated} dated March records (`{BESIDE_ROOT}/`). "
            "Zero application programming interface (API) calls; zero permutation "
            "tests re-run."
        )
    lines = [
        f"# {ERRATUM} board regeneration — 23-condition round-robin",
        "",
        *banner_lines(
            revision,
            f"> **Last revised**: {REMEDIATION_DATE.isoformat()} (original "
            f"publication — {ERRATUM} remediation, Phase R3). See "
            "[§ Changelog](#changelog) for revision history.",
        ),
        "**Purpose**: supplies the regenerated leaderboard the Principal "
        "Investigator's ruling on protocol erratum "
        f"[{ERRATUM}](../../docs/methodology/preregistration/protocol-errata.md) "
        "calls for — the March 2026 round-robin boards with the three "
        "coverage-confounded `flash-min-text-t10` cells dropped, the "
        "Benjamini–Hochberg (BH) false-discovery-rate (FDR) family recomputed "
        "over the retained pairs, and the greedy-clique tiers re-run.",
        "",
        produced,
        "",
        "## 1. What was dropped, and why",
        "",
        "The condition family `flash-min-text-t10` (five aliases across the "
        "repository; the underlying study is "
        f"`outputs/h11/{CONFOUNDED_STUDY_MARKER}/`) covers **240 of the 487** "
        "evaluation tiles by design, but the 2026-03-26 bounds standardisation "
        "scored it against the full 487-tile bounds. Every mound in the 247 "
        "unprocessed tiles became an automatic false negative, understating "
        "that arm's F1 by roughly 0.17–0.19. Membership was derived from each "
        "test artefact's recorded `condition_*.source` provenance, never from "
        "labels — the condition carries five aliases across the repository, so "
        "label matching is unsafe. A provenance walk of `results/pairwise/` "
        f"flags **{len(results['confounded_files'])}** test artefacts, matching "
        "the remediation report's inventory.",
        "",
        "| Board | Conditions before | Dropped | Conditions after | Pairs before | "
        "Pairs dropped | Pairs after |",
        "|---|--:|--:|--:|--:|--:|--:|",
    ]
    for name, board_result in results["boards"].items():
        lines.append(
            f"| `{name}` | {board_result['n_conditions_full']} | "
            f"{len(board_result['dropped_conditions'])} | "
            f"{board_result['n_conditions_new']} | {board_result['n_pairs_full']} | "
            f"{board_result['n_pairs_dropped']} | {board_result['n_pairs_new']} |"
        )
    lines.extend(
        [
            "",
            "The dropped conditions are identical on both boards: "
            + ", ".join(f"`{label}`" for label in results["dropped_conditions"])
            + ".",
            "",
            "The matched-scope replacements for these cells are filed as their "
            "own first-class analysis at `results/e43-matched-temperature/` and "
            "are deliberately **not** spliced into this board — the two "
            "analyses answer different questions and were run under different "
            "protocols.",
            "",
            "## 2. Validation gates",
            "",
            *gate_lines(results, revision, diff, n_dated),
            "## 3. Movement: which conditions changed tier",
            "",
            "Movement is measured against the **recomputed** 26-condition "
            "board, so the comparison isolates the E72 effect: both boards use "
            "the same code, the same p-values and the same F1-descending "
            "processing order, and differ only in which cells are present.",
            "",
        ]
    )
    for name, board_result in results["boards"].items():
        moved = [m for m in board_result["movement"] if m["delta_tier"] != 0]
        lines.extend(
            [
                f"### `{name}` — {board_result['n_tiers_full']} tiers → "
                f"{board_result['n_tiers_new']} tiers",
                "",
            ]
        )
        if not moved:
            lines.extend(
                [
                    "No retained condition changed tier number. The board loses "
                    "the tier(s) the dropped cells occupied and nothing else "
                    "moves.",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "| Condition | F1 | Tier (26-condition board) | "
                    "Tier (regenerated board) | Movement |",
                    "|---|:---:|--:|--:|:---|",
                ]
            )
            for record in moved:
                direction = "up" if record["delta_tier"] < 0 else "down"
                lines.append(
                    f"| {record['condition']} | {_fmt(record['f1'])} | "
                    f"{record['tier_old']} | {record['tier_new']} | "
                    f"{abs(record['delta_tier'])} {direction} |"
                )
            lines.append("")
        changes = board_result["significance_changes"]
        lines.extend(
            [
                f"**BH status changes among the {board_result['n_pairs_new']} "
                f"retained pairs**: {len(changes)}. "
                + (
                    "No retained pair changed significance verdict when the "
                    "family shrank."
                    if not changes
                    else "See the table below."
                ),
                "",
            ]
        )
        if changes:
            lines.extend(
                [
                    "| Condition A | Condition B | p (raw) | q (old family) | "
                    "q (new family) | Change |",
                    "|---|---|---:|---:|---:|:---|",
                ]
            )
            for change in changes:
                verdict = (
                    "ns → significant" if change["is_significant"] else "significant → ns"
                )
                lines.append(
                    f"| {change['condition_a']} | {change['condition_b']} | "
                    f"{change['p_raw']:.4f} | {change['q_old']:.4f} | "
                    f"{change['q_new']:.4f} | {verdict} |"
                )
            lines.append("")

    reconciliation = results["boards"]["leaderboard-20m"].get("reconciliation") or {}
    ordering_differences = reconciliation.get("ordering_differences", [])
    lines.extend(
        [
            "### 3.1 One difference from the published snapshot that is NOT E72",
            "",
            ordering_paragraph(reconciliation["facts"]),
            "",
            "This script uses the documented F1-descending order throughout, so "
            "the following condition sits one tier lower here than in the March "
            "snapshot **for reasons unrelated to the coverage confound**:",
            "",
        ]
    )
    if ordering_differences:
        lines.extend(
            [
                "| Condition | Tier (published snapshot) | Tier (F1-ordered recomputation) |",
                "|---|--:|--:|",
            ]
        )
        for difference in ordering_differences:
            lines.append(
                f"| {difference['condition']} | {difference['tier_published']} | "
                f"{difference['tier_recomputed']} |"
            )
        lines.append("")
    else:  # pragma: no cover - defensive
        lines.extend(["No such difference was found.", ""])
    lines.extend(
        [
            "Gate D proves the attribution: replaying the clique under the "
            "published rank order reproduces the published tier sizes exactly, "
            "so the difference is processing order, not statistics.",
            "",
            "## 4. The smaller BH families",
            "",
            "The same confounded p-values also entered three smaller BH "
            "families. Memberships below are derived from the family manifests "
            "themselves, not assumed. In this project BH is applied **within** "
            "each declared family, so only families containing a confounded "
            "member are affected; the script asserts the others are clean "
            "rather than trusting that.",
            "",
            "| Family artefact | Family | Members (published) | Dropped | "
            "Members (retained) | Significant (published, retained members) | "
            "Significant (recomputed) | Status changes |",
            "|---|---|--:|--:|--:|--:|--:|--:|",
        ]
    )
    for family_result in results["families"]:
        lines.append(
            f"| `{family_result['artefact']}` | `{family_result['family']}` | "
            f"{family_result['n_published']} | {family_result['n_dropped']} | "
            f"{family_result['n_retained']} | "
            f"{family_result['significant_published_retained']} | "
            f"{family_result['significant_recomputed']} | "
            f"{family_result['n_status_changes']} |"
        )
    lines.extend(
        [
            "",
            "Unaffected families (no confounded member; left untouched): "
            + ", ".join(f"`{n}`" for n in results["clean_families"])
            + ".",
            "",
            "## 5. What this does and does not change",
            "",
            "- **Unchanged**: every retained condition's F1, precision, recall, "
            "detection count and tile-level MCC. Dropping whole cells removes "
            "rows; it does not rescore the survivors.",
            "- **Unchanged**: every retained pair's observed ΔF1 and raw "
            "permutation p-value. No test was re-run.",
            "- **Changed**: the BH family size, hence the adjusted q-values, "
            "hence (potentially) the tier clustering.",
            "- **Not done here**: the matched-scope temperature evidence. That "
            "lives at `results/e43-matched-temperature/` and is cited, not "
            "merged.",
            "",
            "## 6. Files in this directory",
            "",
            "```text",
            "leaderboard-20m/   leaderboard.{md,csv}, tiers.{md,csv},",
            "                   pairwise_results_fdr.csv, run_manifest.json",
            "leaderboard-30m/   (as above, at the 30 m buffer)",
            "bh-families/       families_recomputed.{md,csv,json}",
            "summary.md         this document",
            "```",
            "",
            "## Changelog",
            "",
        ]
    )
    for entry in revision_history(revision):
        lines.extend([f"### {entry.date.isoformat()} — {entry.title}", ""])
        if entry.is_original:
            lines.extend([ORIGINAL_SUMMARY_ENTRY, ""])
        else:
            lines.extend(summary_changelog_entry(results, entry, diff, n_dated))
    return "\n".join(lines)


def render_families_md(results: Mapping[str, Any]) -> str:
    """Render the recomputed smaller BH families as Markdown.

    Args:
        results: The assembled results structure built by :func:`main`; its
            optional ``revision``, ``diff`` and ``n_dated`` fill the revision
            trail as in :func:`render_summary_md`.

    Returns:
        Markdown document text.
    """
    revision: Revision = results.get("revision", LATEST_REVISION)
    diff: Mapping[str, Any] | None = results.get("diff")
    n_dated = int(results.get("n_dated", 0))
    lines = [
        f"# Recomputed BH families with the {ERRATUM} members dropped",
        "",
        *banner_lines(
            revision,
            f"> **Last revised**: {REMEDIATION_DATE.isoformat()} (original "
            f"publication — {ERRATUM} remediation).",
        ),
        "Benjamini–Hochberg (BH) false-discovery-rate correction at "
        f"q = {FDR_Q}, applied within each declared family, with the "
        "coverage-confounded members removed. Raw p-values are read verbatim "
        "from the committed permutation artefacts; nothing was re-run.",
        "",
    ]
    for family_result in results["families"]:
        lines.extend(
            [
                f"## `{family_result['artefact']}` — family `{family_result['family']}`",
                "",
                f"Published family: {family_result['n_published']} members. "
                f"Dropped under {ERRATUM}: {family_result['n_dropped']}. "
                f"Retained: {family_result['n_retained']}. "
                f"BH-significant among the retained members — published "
                f"{family_result['significant_published_retained']}, recomputed "
                f"{family_result['significant_recomputed']}.",
                "",
                "Dropped members: "
                + (
                    ", ".join(
                        f"group {m['group']} — {m['question']}"
                        for m in family_result["dropped_members"]
                    )
                    or "none"
                )
                + ".",
                "",
                "| Group | Question | Condition A | Condition B | p (raw) | "
                "q (published) | q (recomputed) | Changed |",
                "|--:|---|---|---|---:|---:|---:|:--:|",
            ]
        )
        for member in family_result["members"]:
            lines.append(
                f"| {member['group']} | {member['question']} | "
                f"{member['label_a']} | {member['label_b']} | "
                f"{member['p_raw']:.4f} | {member['q_published']:.4f} | "
                f"{member['q_recomputed']:.4f} | "
                f"{'yes' if member['status_changed'] else 'no'} |"
            )
        lines.append("")
    lines.extend(families_changelog_lines(revision, diff, n_dated))
    return "\n".join(lines)


def families_changelog_lines(
    revision: Revision, diff: Mapping[str, Any] | None, n_dated: int
) -> list[str]:
    """Return the families document's ``## Changelog`` (later revisions only).

    Args:
        revision: The revision being rendered.
        diff: The before -> after record (:func:`revision_diff`), or None.
        n_dated: Number of dated records read through the runs beside them.

    Returns:
        Markdown lines; empty for the original revision, which had none.
    """
    if revision.is_original:
        return []
    lines = ["## Changelog", ""]
    for entry in revision_history(revision):
        lines.extend([f"### {entry.date.isoformat()} — {entry.title}", ""])
        if entry.is_original:
            lines.extend([ORIGINAL_STUB, ""])
            continue
        lines.extend(
            [
                restated_trigger(n_dated) + " The full entry is in "
                "[`../summary.md` § Changelog](../summary.md#changelog).",
                "",
            ]
        )
        if diff is None or entry is not revision:
            continue
        before = REVISIONS[REVISIONS.index(entry) - 1].date.isoformat()
        after = entry.date.isoformat()
        lines.extend(
            [
                f"| Family | BH-significant ({before}) | BH-significant ({after}) | "
                "Members whose raw p moved |",
                "|---|--:|--:|--:|",
            ]
        )
        changes: list[str] = []
        for family in diff["families"]:
            n = family["n_retained"]
            lines.append(
                f"| `{family['artefact']}` `{family['family']}` | "
                f"{family['significant_before']} of {n} | "
                f"{family['significant_after']} of {n} | {family['p_moved']} of {n} |"
            )
            for change in family["verdict_changes"]:
                changes.append(
                    f"| `{family['artefact']}` | {change['group']} | {change['question']} | "
                    f"{change['condition_a']} | {change['condition_b']} | "
                    f"{change['p_before']:.4f} → {change['p_after']:.4f} | "
                    f"{change['q_before']:.6f} → {change['q_after']:.6f} | "
                    f"{_verdict(change['significant_before'])} → "
                    f"{_verdict(change['significant_after'])} |"
                )
        lines.extend(["", f"BH verdicts that changed: {len(changes)}.", ""])
        if changes:
            lines.extend(
                [
                    "| Family artefact | Group | Question | Condition A | Condition B | "
                    "p (raw) | q (recomputed) | Verdict |",
                    "|---|--:|---|---|---|---|---|---|",
                    *changes,
                    "",
                ]
            )
        lines.extend(
            [
                "Not changed: the dropped members and the retained membership of "
                "every family.",
                "",
            ]
        )
    return lines


# --- orchestration --------------------------------------------------------- #


def process_board(name: str, source_dir: Path, group_subdir: str) -> dict[str, Any]:
    """Load, validate, regenerate and summarise one round-robin board.

    Args:
        name: Board identifier.
        source_dir: The committed permutation run directory.
        group_subdir: Subdirectory holding the per-pair test JSONs.

    Returns:
        Result dictionary for this board, including its accepted dated
        records (``dated_records``).

    Raises:
        AssertionError: If Gate A, B, C or D fails.
    """
    group_dir = source_dir / group_subdir
    _current, dated = resolve_group_files(group_dir)
    tests = load_pair_tests(group_dir)  # today's runs: dated records read beside
    check_against_manifest(tests, source_dir / "run_manifest.json")  # Gate A

    full_board = build_board(name, tests)  # Gate C runs inside condition_metrics
    check_full_board_gate(name, full_board, source_dir)  # Gate B

    reconciliation: dict[str, Any] | None = None
    if name == "leaderboard-20m":
        reconciliation = reconcile_published_order(full_board)  # Gate D
        reconciliation["facts"] = published_order_facts(full_board, reconciliation)

    retained, dropped = split_confounded(tests)
    dropped_conditions = confounded_labels(tests)
    new_board = build_board(name, retained)

    return {
        "reconciliation": reconciliation,
        "name": name,
        "source_dir": str(source_dir.relative_to(BASE_DIR)),
        "full_board": full_board,
        "new_board": new_board,
        "dropped_conditions": dropped_conditions,
        "n_conditions_full": len(full_board.order),
        "n_conditions_new": len(new_board.order),
        "n_pairs_full": len(full_board.tests),
        "n_pairs_dropped": len(dropped),
        "n_pairs_new": len(new_board.tests),
        "n_significant_full": full_board.n_significant,
        "n_significant_new": new_board.n_significant,
        "n_tiers_full": len(full_board.tiers),
        "n_tiers_new": len(new_board.tiers),
        "movement": tier_movement(full_board, new_board),
        "significance_changes": significance_changes(full_board, new_board),
        "dated_records": dated,
    }


def main() -> int:
    """CLI entry point: regenerate the boards and families.

    Returns:
        Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Write the regenerated artefacts (default is a dry run).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=BASE_DIR / "results" / "e43-board-regen",
        help="Destination directory for the regenerated artefacts.",
    )
    parser.add_argument("--fdr-q", type=float, default=FDR_Q, help="FDR threshold (default 0.05).")
    parser.add_argument(
        "--revision",
        choices=[revision.date.isoformat() for revision in REVISIONS],
        default=LATEST_REVISION.date.isoformat(),
        help=(
            "Revision to render (default: the latest). 2026-08-02 renders the "
            "original publication and accepts only the March input layout."
        ),
    )
    args = parser.parse_args()
    revision = next(r for r in REVISIONS if r.date.isoformat() == args.revision)

    # --- input layout: dated March records with today's runs beside them --- #
    family_dated = dated_record_inventory(BASE_DIR / rel for rel in PAIRWISE_FAMILY_DIRS.values())
    board_dated = dated_record_inventory(BASE_DIR / source for source, _ in BOARDS.values())
    n_dated = len(board_dated) + len(family_dated)
    print(
        f"Dated March records read through today's runs beside them: {n_dated} "
        f"(boards {len(board_dated)}, families {len(family_dated)})",
        flush=True,
    )
    check_revision_layout(revision, n_dated)

    buffers = {"leaderboard-20m": 20, "leaderboard-30m": 30}
    board_results: dict[str, dict[str, Any]] = {}
    for name, (source, group_subdir) in BOARDS.items():
        print(f"Processing board {name} ...", flush=True)
        board_results[name] = process_board(name, BASE_DIR / source, group_subdir)

    dropped_union = sorted(
        {label for r in board_results.values() for label in r["dropped_conditions"]}
    )

    # --- smaller BH families ---------------------------------------------- #
    family_results: list[dict[str, Any]] = []
    clean_families: list[str] = []
    confounded_keys, confounded_files = discover_confounded_tests(BASE_DIR / "results" / "pairwise")
    print(
        f"Confounded permutation artefacts found: {len(confounded_files)} "
        f"({len(confounded_keys)} distinct contrasts)",
        flush=True,
    )

    for artefact, rel in PAIRWISE_FAMILY_DIRS.items():
        records = load_pairwise_family(BASE_DIR / rel)
        for summary in recompute_families(records, q=args.fdr_q):
            if summary["n_dropped"] == 0:
                clean_families.append(f"{artefact}:{summary['family']}")
                continue
            summary["artefact"] = rel
            summary["n_status_changes"] = sum(1 for m in summary["members"] if m["status_changed"])
            family_results.append(summary)

    fa_records = load_factor_analysis_family(BASE_DIR / FACTOR_ANALYSIS_JSON, confounded_keys)
    for summary in recompute_families(fa_records, q=args.fdr_q):
        if summary["n_dropped"] == 0:
            clean_families.append(f"factor-analysis:{summary['family']}")
            continue
        summary["artefact"] = FACTOR_ANALYSIS_JSON
        summary["n_status_changes"] = sum(1 for m in summary["members"] if m["status_changed"])
        family_results.append(summary)

    # --- the previous revision: before -> after ------------------------------ #
    diff: dict[str, Any] | None = None
    if revision.baseline_ref is not None:
        diff = revision_diff(
            read_baseline(revision.baseline_ref), board_results, family_results, q=args.fdr_q
        )

    results: dict[str, Any] = {
        "git_commit": git_commit(),
        "boards": board_results,
        "dropped_conditions": dropped_union,
        "families": family_results,
        "clean_families": sorted(clean_families),
        "confounded_files": confounded_files,
        "revision": revision,
        "diff": diff,
        "n_dated": n_dated,
    }

    # --- console report ---------------------------------------------------- #
    for name, board_result in board_results.items():
        print(
            f"  {name}: {board_result['n_conditions_full']} -> "
            f"{board_result['n_conditions_new']} conditions; "
            f"{board_result['n_pairs_full']} -> {board_result['n_pairs_new']} pairs "
            f"({board_result['n_pairs_dropped']} dropped); "
            f"{board_result['n_significant_full']} -> "
            f"{board_result['n_significant_new']} significant; "
            f"{board_result['n_tiers_full']} -> {board_result['n_tiers_new']} tiers; "
            f"{sum(1 for m in board_result['movement'] if m['delta_tier'] != 0)} "
            f"conditions changed tier; "
            f"{len(board_result['significance_changes'])} BH status changes"
        )
    for family_result in family_results:
        print(
            f"  family {family_result['artefact']}:{family_result['family']}: "
            f"{family_result['n_published']} -> {family_result['n_retained']} members; "
            f"significant {family_result['significant_published_retained']} -> "
            f"{family_result['significant_recomputed']}; "
            f"{family_result['n_status_changes']} status changes"
        )
    if diff is not None:
        print(f"Against the previous revision's outputs ({diff['ref']}):")
        for name, board in diff["boards"].items():
            print(
                f"  {name}: significant {board['significant_before']} -> "
                f"{board['significant_after']}; tiers {board['tiers_before']} -> "
                f"{board['tiers_after']}; {len(board['verdict_changes'])} verdict changes; "
                f"{board['p_moved']} raw p moved"
            )
            for change in board["verdict_changes"]:
                print(f"    {change}")
        for family in diff["families"]:
            print(
                f"  family {family['artefact']}:{family['family']}: significant "
                f"{family['significant_before']} -> {family['significant_after']}; "
                f"{len(family['verdict_changes'])} verdict changes"
            )
            for change in family["verdict_changes"]:
                print(f"    {change}")

    if not args.execute:
        print("\nDry run — nothing written. Re-run with --execute to write.", flush=True)
        return 0

    # --- write ------------------------------------------------------------- #
    out_root: Path = args.output_dir
    out_root.mkdir(parents=True, exist_ok=True)

    for name, board_result in board_results.items():
        board: Board = board_result["new_board"]
        buffer_m = buffers[name]
        out_dir = out_root / name
        out_dir.mkdir(parents=True, exist_ok=True)

        dropped_here = board_result["dropped_conditions"]
        (out_dir / "leaderboard.md").write_text(
            render_leaderboard_md(board, buffer_m, dropped_here, revision, diff, n_dated)
        )
        (out_dir / "tiers.md").write_text(
            render_tiers_md(board, buffer_m, dropped_here, revision, diff, n_dated)
        )
        write_csv(
            out_dir / "leaderboard.csv",
            [
                {
                    "rank": rank,
                    "condition": label,
                    "tier": board.tier_of(label),
                    "f1": round(board.metrics[label]["f1"], 6),
                    "precision": round(board.metrics[label]["precision"], 6),
                    "recall": round(board.metrics[label]["recall"], 6),
                    "n_detections": int(board.metrics[label]["n_detections"]),
                }
                for rank, label in enumerate(board.order, start=1)
            ],
            ["rank", "condition", "tier", "f1", "precision", "recall", "n_detections"],
        )
        write_csv(
            out_dir / "tiers.csv",
            [
                {
                    "tier": index,
                    "rank": board.order.index(label) + 1,
                    "condition": label,
                    "f1": round(board.metrics[label]["f1"], 6),
                    "tier_f1_min": round(min(board.metrics[m]["f1"] for m in tier), 6),
                    "tier_f1_max": round(max(board.metrics[m]["f1"] for m in tier), 6),
                }
                for index, tier in enumerate(board.tiers, start=1)
                for label in tier
            ],
            ["tier", "rank", "condition", "f1", "tier_f1_min", "tier_f1_max"],
        )
        write_csv(
            out_dir / "pairwise_results_fdr.csv",
            [
                {
                    "label_a": test.label_a,
                    "label_b": test.label_b,
                    "f1_a": round(test.f1_a, 6),
                    "f1_b": round(test.f1_b, 6),
                    "delta_f1": round(test.delta_f1, 6),
                    "p_value_raw": test.p_value,
                    "p_value_adj": round(board.adjusted[index], 6),
                    "significant": "yes" if board.adjusted[index] < args.fdr_q else "no",
                    "source_file": test.source_file,
                }
                for index, test in enumerate(board.tests)
            ],
            [
                "label_a",
                "label_b",
                "f1_a",
                "f1_b",
                "delta_f1",
                "p_value_raw",
                "p_value_adj",
                "significant",
                "source_file",
            ],
        )
        (out_dir / "run_manifest.json").write_text(
            json.dumps(
                board_manifest(
                    board,
                    board_result["full_board"],
                    buffer_m,
                    board_result["source_dir"],
                    board_result["dropped_conditions"],
                    board_result["n_pairs_dropped"],
                    revision,
                    board_result["dated_records"],
                ),
                indent=2,
            )
            + "\n"
        )

    families_dir = out_root / "bh-families"
    families_dir.mkdir(parents=True, exist_ok=True)
    (families_dir / "families_recomputed.md").write_text(render_families_md(results))
    (families_dir / "families_recomputed.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "script": "regen_e43_board.py",
                    "git_commit": results["git_commit"],
                    "erratum": ERRATUM,
                    "q": args.fdr_q,
                    "method": "Benjamini-Hochberg, applied within each declared family",
                    "clean_families": results["clean_families"],
                    **(
                        {}
                        if revision.is_original
                        else {"revision": revision_provenance(revision, family_dated)}
                    ),
                },
                "families": family_results,
            },
            indent=2,
        )
        + "\n"
    )
    write_csv(
        families_dir / "families_recomputed.csv",
        [
            {
                "artefact": family_result["artefact"],
                "family": family_result["family"],
                "group": member["group"],
                "question": member["question"],
                "label_a": member["label_a"],
                "label_b": member["label_b"],
                "p_raw": member["p_raw"],
                "q_published": member["q_published"],
                "q_recomputed": member["q_recomputed"],
                "status_changed": "yes" if member["status_changed"] else "no",
            }
            for family_result in family_results
            for member in family_result["members"]
        ],
        [
            "artefact",
            "family",
            "group",
            "question",
            "label_a",
            "label_b",
            "p_raw",
            "q_published",
            "q_recomputed",
            "status_changed",
        ],
    )

    (out_root / "summary.md").write_text(render_summary_md(results))
    print(f"\nWrote regenerated artefacts to {out_root}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
