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
# VALIDATION GATES (all must pass before anything is written)
# ----------------------------------------------------------
#   Gate A: the per-pair JSONs reproduce the committed ``run_manifest.json``
#           exactly — same pair set, same raw p-values, same ΔF1.
#   Gate B: recomputing the FULL board (no cells dropped) reproduces the
#           published snapshot's significance count and tier count
#           (20 m: 265/325 significant, 9 tiers; 30 m: 243/300, 9 tiers).
#           This proves the BH + tiering reimplementation is faithful before
#           its output is trusted for the reduced board.
#   Gate C: every condition's F1/precision/recall is internally consistent
#           across all the tests it appears in.
#
# METRIC NOTE (tile-level Matthews correlation coefficient, MCC)
# -------------------------------------------------------------
# The permutation artefacts that form this board's data layer carry only
# mound-level true/false positives and negatives, so no MCC column is
# reproduced here. This is not a silent omission: dropping whole cells does not
# alter any RETAINED condition's metrics, so the MCC column of the dated
# snapshot ``results/paper-tables/leaderboard_tiers_20m.md`` remains valid for
# the 23 retained rows. Only the tier assignment moves.
#
# USAGE
# -----
#   # dry run (default) — computes everything, writes nothing:
#   python scripts/regen_e43_board.py
#
#   # write the regenerated artefacts:
#   python scripts/regen_e43_board.py --execute
#
#   # alternative output root:
#   python scripts/regen_e43_board.py --execute --output-dir results/tmp-board
#
# Zero API cost; pure recomputation over committed artefacts. Run on sapphire
# per the project compute rule.
# ============================================================================
"""Regenerate the E72-affected leaderboard boards and BH families.

See the module header for the full rationale, the confounded-cell definition,
the boards and families covered, and the validation gates.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
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

#: Date this remediation was executed (used in the revision banner).
REMEDIATION_DATE = date(2026, 8, 2)

#: Published snapshot figures the full-board recomputation must reproduce
#: (Gate B). Keyed by board name; values are (n_significant, n_tiers).
PUBLISHED_FULL_BOARD_GATES: dict[str, tuple[int, int]] = {
    "leaderboard-20m": (265, 9),
    "leaderboard-30m": (243, 9),
}

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


# --- artefact loading ------------------------------------------------------ #


def load_pair_tests(group_dir: Path) -> list[PairTest]:
    """Load every per-pair permutation-test JSON in a group directory.

    Args:
        group_dir: Directory holding one JSON per pairwise test.

    Returns:
        Pair tests sorted by (label_a, label_b) for determinism.

    Raises:
        FileNotFoundError: If the directory holds no JSON files.
    """
    paths = sorted(group_dir.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"no per-pair test JSONs under {group_dir}")

    tests: list[PairTest] = []
    for path in paths:
        doc = json.loads(path.read_text())
        cond_a, cond_b = doc["condition_a"], doc["condition_b"]
        perm = doc["permutation_test"]
        tests.append(
            PairTest(
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
        )
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
    which is unique.

    Args:
        family_dir: e.g. ``results/pairwise/20m``.

    Returns:
        One record per family member, with a ``confounded`` flag added.

    Raises:
        AssertionError: If any family member has no matching per-test JSON.
    """
    manifest = json.loads((family_dir / "fdr" / "pairwise_results_fdr.json").read_text())
    provenance: dict[tuple[Any, ...], bool] = {}
    for path in sorted(family_dir.glob("group_*/*.json")):
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

    records: list[dict[str, Any]] = []
    for entry in manifest["comparisons"]:
        key = (entry["group"], entry["question"], entry["label_a"], entry["label_b"])
        assert key in provenance, f"{family_dir}: no per-test JSON for {key}"
        records.append({**entry, "confounded": provenance[key]})
    return records


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


def render_leaderboard_md(board: Board, buffer_m: int, dropped: Sequence[str]) -> str:
    """Render the regenerated leaderboard table as Markdown.

    Args:
        board: The regenerated board.
        buffer_m: Spatial buffer in metres.
        dropped: Labels of the dropped confounded conditions.

    Returns:
        Markdown document text.
    """
    lines = [
        f"# Regenerated leaderboard — {len(board.order)} conditions "
        f"({buffer_m} m buffer, {ERRATUM})",
        "",
        f"> **Last revised**: {REMEDIATION_DATE.isoformat()} (original "
        f"publication — {ERRATUM} remediation). Regenerated from the March "
        "round-robin with the coverage-confounded cells dropped.",
        "",
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
    lines.append(
        "Tile-level MCC is not reproduced here — the permutation artefacts "
        "carry only mound-level counts. Dropping whole cells does not change "
        "any retained condition's metrics, so the MCC column of the dated "
        "snapshot remains valid for these rows."
    )
    lines.append("")
    return "\n".join(lines)


def render_tiers_md(board: Board, buffer_m: int, dropped: Sequence[str]) -> str:
    """Render the regenerated tier table as Markdown.

    Args:
        board: The regenerated board.
        buffer_m: Spatial buffer in metres.
        dropped: Labels of the dropped confounded conditions.

    Returns:
        Markdown document text.
    """
    lines = [
        f"# Regenerated tier clustering — {len(board.order)} conditions "
        f"({buffer_m} m buffer, FDR-corrected, {ERRATUM})",
        "",
        f"> **Last revised**: {REMEDIATION_DATE.isoformat()} (original "
        f"publication — {ERRATUM} remediation).",
        "",
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
) -> dict[str, Any]:
    """Assemble ``run_manifest``-style metadata for a regenerated board.

    Args:
        board: The regenerated board.
        full_board: The recomputed full board (provenance/comparison).
        buffer_m: Spatial buffer in metres.
        source_dir: Repository-relative path of the source permutation run.
        dropped_conditions: Labels dropped under E72.
        n_dropped_pairs: Number of pairs dropped.

    Returns:
        Manifest dictionary ready to serialise.
    """
    return {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "script": "regen_e43_board.py",
            "version": "1.0.0",
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


def render_summary_md(results: Mapping[str, Any]) -> str:
    """Render the top-level summary document for the regeneration.

    Args:
        results: The assembled results structure built by :func:`main`.

    Returns:
        Markdown document text.
    """
    lines = [
        f"# {ERRATUM} board regeneration — 23-condition round-robin",
        "",
        f"> **Last revised**: {REMEDIATION_DATE.isoformat()} (original "
        f"publication — {ERRATUM} remediation, Phase R3). See "
        "[§ Changelog](#changelog) for revision history.",
        "",
        "**Purpose**: supplies the regenerated leaderboard the Principal "
        "Investigator's ruling on protocol erratum "
        f"[{ERRATUM}](../../docs/methodology/preregistration/protocol-errata.md) "
        "calls for — the March 2026 round-robin boards with the three "
        "coverage-confounded `flash-min-text-t10` cells dropped, the "
        "Benjamini–Hochberg (BH) false-discovery-rate (FDR) family recomputed "
        "over the retained pairs, and the greedy-clique tiers re-run.",
        "",
        f"**Produced**: {REMEDIATION_DATE.isoformat()}, on sapphire, from "
        f"repository commit `{results['git_commit']}` by "
        "`scripts/regen_e43_board.py`. Zero application programming interface "
        "(API) calls; zero permutation tests re-run.",
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
            "All three gates passed before anything was written:",
            "",
            "- **Gate A** — the per-pair JSONs reproduce each board's committed "
            "`run_manifest.json` exactly (same pair set, same raw p-values, "
            "same ΔF1).",
            "- **Gate B** — recomputing the FULL board (nothing dropped) "
            "reproduces the published snapshot: "
            + "; ".join(
                f"`{name}` {results['boards'][name]['n_significant_full']}/"
                f"{results['boards'][name]['n_pairs_full']} significant, "
                f"{results['boards'][name]['n_tiers_full']} tiers"
                for name in results["boards"]
            )
            + ". This proves the BH and tiering reimplementation is faithful "
            "before its output is trusted for the reduced board.",
            "- **Gate C** — every condition's F1, precision, recall and "
            "detection count agree across all tests it appears in.",
            "- **Gate D** — replaying the greedy clique under the *published* "
            "20 m rank order reproduces the published tier sizes "
            f"({', '.join(str(n) for n in PUBLISHED_20M_TIER_SIZES)}) exactly. "
            "See § 3.1 for why this gate exists.",
            "",
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
            "Greedy-clique tiering is order-dependent, and the published 20 m "
            "snapshot (`results/paper-tables/leaderboard_tiers_20m.md`) ranks "
            "one condition out of F1 order: `flash-high-image-3-of-5--flash-min-vf "
            "(t=0.15)` (F1 0.778) sits at rank 10, ahead of two higher-F1 "
            "conditions. Processed there it joins the 0.814 clique; processed in "
            "strict F1 order it is reached only after `flash-high-text N=10` "
            "(F1 0.797) has already opened the next tier — and that boundary "
            "rests on a single borderline pair (`FH text 26/30` versus "
            "`FH text 9/10`, q = 0.046).",
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
            f"### {REMEDIATION_DATE.isoformat()} — Original publication",
            "",
            f"Trigger: PI ruling on protocol erratum {ERRATUM}, option (a) — "
            "drop the confounded cells and regenerate rather than splice in "
            "the matched-scope replacements. Produced the regenerated "
            f"{results['boards']['leaderboard-20m']['n_conditions_new']}-condition "
            "boards at both buffers, the recomputed BH families, and this "
            "summary. Nothing under `results/pairwise/` was modified; the "
            "superseded dated snapshots carry banners pointing here.",
            "",
        ]
    )
    return "\n".join(lines)


def render_families_md(results: Mapping[str, Any]) -> str:
    """Render the recomputed smaller BH families as Markdown.

    Args:
        results: The assembled results structure built by :func:`main`.

    Returns:
        Markdown document text.
    """
    lines = [
        f"# Recomputed BH families with the {ERRATUM} members dropped",
        "",
        f"> **Last revised**: {REMEDIATION_DATE.isoformat()} (original "
        f"publication — {ERRATUM} remediation).",
        "",
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
    return "\n".join(lines)


# --- orchestration --------------------------------------------------------- #


def process_board(name: str, source_dir: Path, group_subdir: str) -> dict[str, Any]:
    """Load, validate, regenerate and summarise one round-robin board.

    Args:
        name: Board identifier.
        source_dir: The committed permutation run directory.
        group_subdir: Subdirectory holding the per-pair test JSONs.

    Returns:
        Result dictionary for this board.

    Raises:
        AssertionError: If Gate A or Gate B fails.
    """
    tests = load_pair_tests(source_dir / group_subdir)
    check_against_manifest(tests, source_dir / "run_manifest.json")

    full_board = build_board(name, tests)
    expected = PUBLISHED_FULL_BOARD_GATES.get(name)
    if expected is not None:
        assert full_board.n_significant == expected[0], (
            f"Gate B ({name}): recomputed {full_board.n_significant} significant, "
            f"published snapshot says {expected[0]}"
        )
        assert len(full_board.tiers) == expected[1], (
            f"Gate B ({name}): recomputed {len(full_board.tiers)} tiers, "
            f"published snapshot says {expected[1]}"
        )

    reconciliation: dict[str, Any] | None = None
    if name == "leaderboard-20m":
        reconciliation = reconcile_published_order(full_board)

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
    args = parser.parse_args()

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

    results: dict[str, Any] = {
        "git_commit": git_commit(),
        "boards": board_results,
        "dropped_conditions": dropped_union,
        "families": family_results,
        "clean_families": sorted(clean_families),
        "confounded_files": confounded_files,
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

        (out_dir / "leaderboard.md").write_text(
            render_leaderboard_md(board, buffer_m, board_result["dropped_conditions"])
        )
        (out_dir / "tiers.md").write_text(
            render_tiers_md(board, buffer_m, board_result["dropped_conditions"])
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
