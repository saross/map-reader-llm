"""Tests for ``scripts.regen_e43_board`` on the restated in-place-and-beside layout.

The S164 restatement pass regenerated ``results/pairwise/`` in place, but left
the per-pair files that read the two drifted single-pass arms at their paths as
dated March records, with today's runs beside them under
``results/rescore-2026-10-15/pairwise/`` (rulings D58 Q2 and D61 (2)). The PI's
specification for adapting the E72 board regeneration (D69 Q15): gates A and C
accept the dated records beside today's runs, gate B takes its significance
count from today's run, and the renderers keep the revision banner. These tests
pin each of those changes on small synthetic trees under ``tmp_path``.

Each test builds real files (no symlinks) and points the module's ``BASE_DIR``
at the temporary tree with ``monkeypatch``, so the code resolves every path the
way it does in the repository.

Red sentinel: run against the 2026-08-02 script (``git show
2f3ef020a:scripts/regen_e43_board.py``), the layout, Gate B and banner tests
fail on behaviour — the old loader reads the March record and Gate A or Gate C
refuses it, the old Gate B expects the March count, and the old renderers write
the 2026-08-02 banner — and the tests of new functions fail on the missing name.
The record of that run is ``reports/s166-agent-records/e72-group7.md``.

Tier 1 (synthetic, hermetic):
  1. The loader reads today's run beside a dated record; Gate A then matches
     today's manifest and Gate C sees one vintage.
  2. A dated record is accepted only when the run beside it names the same test
     and is newer; a beside file with no record next to it is refused.
  3. A March-dated file with no run beside it is current and read in place.
  4. Gate B takes the count from the board's own BH artefact and refuses a
     disagreeing count or tier number.
  5. The renderers keep the revision trail; the original revision renders its
     2026-08-02 banner verbatim; a revision refuses the wrong input layout.
  6. The before -> after record and its changelog tables.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import scripts.regen_e43_board as regen  # noqa: E402

pytestmark = pytest.mark.tier1

MARCH = "2026-03-29T10:52:14.708233+00:00"
TODAY = "2026-10-15T11:02:20.547945+00:00"
BOARD = "leaderboard-20m"


# --------------------------------------------------------------------------- #
# Synthetic tree builders
# --------------------------------------------------------------------------- #


def arm(label: str, f1: float, n_detections: int = 100) -> dict[str, Any]:
    """Return one condition arm as a per-pair JSON records it.

    Args:
        label: Condition label.
        f1: The arm's F1; precision and recall are set equal to it.
        n_detections: Detection count.

    Returns:
        The ``condition_{a,b}`` mapping.
    """
    return {
        "label": label,
        "source": {"mode": "consensus", "study_dir": f"outputs/synthetic/{label}"},
        "f1": f1,
        "precision": f1,
        "recall": f1,
        "n_detections": n_detections,
        "tp": 1,
        "fp": 1,
        "fn": 1,
    }


def write_pair(
    path: Path,
    arm_a: dict[str, Any],
    arm_b: dict[str, Any],
    p_value: float,
    timestamp: str,
    *,
    group: int = 8,
    question: str = "Leaderboard distinguishability",
) -> None:
    """Write one per-pair permutation-test JSON.

    Args:
        path: Destination (parents are created).
        arm_a: Condition A (from :func:`arm`).
        arm_b: Condition B.
        p_value: Raw permutation p-value.
        timestamp: ``metadata.timestamp``.
        group: ``metadata.group``.
        question: ``metadata.question``.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "metadata": {
            "timestamp": timestamp,
            "script": "run_pairwise_tests.py",
            "version": "1.0.0",
            "group": group,
            "question": question,
            "family": "leaderboard",
            "buffer_metres": 20,
            "n_permutations": 10000,
            "seed": 42,
        },
        "condition_a": arm_a,
        "condition_b": arm_b,
        "permutation_test": {
            "observed_f1_diff": round(arm_a["f1"] - arm_b["f1"], 6),
            "p_value": p_value,
        },
    }
    path.write_text(json.dumps(doc))


def write_run_files(run_dir: Path, pairs: list[tuple[dict, dict, float]]) -> None:
    """Write a run's ``run_manifest.json`` and ``fdr/pairwise_results_fdr.json``.

    The adjusted values are computed with the project's BH implementation, as
    ``apply_fdr_correction.py`` would write them for the complete run.

    Args:
        run_dir: The board's run directory.
        pairs: Today's (arm A, arm B, raw p) for every pair of the run.
    """
    adjusted = regen.apply_bh_correction([p for _a, _b, p in pairs])
    comparisons = [
        {
            "label_a": a["label"],
            "label_b": b["label"],
            "delta_f1": round(a["f1"] - b["f1"], 6),
            "p_value": p,
        }
        for a, b, p in pairs
    ]
    (run_dir / "run_manifest.json").write_text(
        json.dumps({"metadata": {"n_comparisons": len(pairs)}, "comparisons": comparisons})
    )
    (run_dir / "fdr").mkdir(parents=True, exist_ok=True)
    (run_dir / "fdr" / "pairwise_results_fdr.json").write_text(
        json.dumps(
            {
                "metadata": {"n_comparisons": len(pairs)},
                "comparisons": [
                    {**entry, "p_value_raw": entry["p_value"], "p_value_adj": round(q, 6)}
                    for entry, q in zip(comparisons, adjusted)
                ],
            }
        )
    )


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the module at an empty synthetic repository root.

    Args:
        tmp_path: pytest's per-test directory.
        monkeypatch: pytest's monkeypatch fixture.

    Returns:
        The synthetic repository root.
    """
    monkeypatch.setattr(regen, "BASE_DIR", tmp_path)
    return tmp_path


def in_place(root: Path, name: str) -> Path:
    """Path of a per-pair file in the board's group directory."""
    return root / "results" / "pairwise" / BOARD / "group_8" / name


def beside(root: Path, name: str) -> Path:
    """Path of today's run beside a dated record."""
    return root / "results" / "rescore-2026-10-15" / "pairwise" / BOARD / "group_8" / name


def build_mixed_board(root: Path) -> None:
    """Build a three-condition board in the restated layout.

    ``x`` and ``y`` moved in the restatement (their March F1s differ from
    today's); ``s`` is the drifted single-pass arm. The ``x``-``y`` pair is
    regenerated in place; the two pairs with ``s`` stay as March records with
    today's runs beside them. The manifest and BH artefact are today's run.

    Args:
        root: The synthetic repository root.
    """
    x_old, y_old, s_old = arm("x", 0.80), arm("y", 0.70), arm("s", 0.50, 951)
    x_new, y_new, s_new = arm("x", 0.81), arm("y", 0.71), arm("s", 0.52, 954)
    write_pair(in_place(root, "x-y.json"), x_new, y_new, 0.04, TODAY)
    write_pair(in_place(root, "x-s.json"), x_old, s_old, 0.0001, MARCH)
    write_pair(in_place(root, "y-s.json"), y_old, s_old, 0.03, MARCH)
    write_pair(beside(root, "x-s.json"), x_new, s_new, 0.0002, TODAY)
    write_pair(beside(root, "y-s.json"), y_new, s_new, 0.02, TODAY)
    write_run_files(
        root / "results" / "pairwise" / BOARD,
        [(x_new, y_new, 0.04), (x_new, s_new, 0.0002), (y_new, s_new, 0.02)],
    )


# --------------------------------------------------------------------------- #
# 1. Gates A and C accept the dated records beside today's runs
# --------------------------------------------------------------------------- #


def test_loader_reads_todays_run_beside_a_dated_record(tree: Path) -> None:
    """Gate A: with the beside runs read, the tests equal today's manifest."""
    build_mixed_board(tree)
    run_dir = tree / "results" / "pairwise" / BOARD
    tests = regen.load_pair_tests(run_dir / "group_8")

    regen.check_against_manifest(tests, run_dir / "run_manifest.json")
    sources = {test.key: test.source_file for test in tests}
    assert sources[frozenset({"x", "s"})] == (
        "results/rescore-2026-10-15/pairwise/leaderboard-20m/group_8/x-s.json"
    )
    assert sources[frozenset({"x", "y"})] == "results/pairwise/leaderboard-20m/group_8/x-y.json"


def test_gate_c_sees_one_vintage(tree: Path) -> None:
    """Gate C: each condition is scored one way once the March records are set aside."""
    build_mixed_board(tree)
    tests = regen.load_pair_tests(tree / "results" / "pairwise" / BOARD / "group_8")

    metrics = regen.condition_metrics(tests)
    assert metrics["x"]["f1"] == pytest.approx(0.81)
    assert metrics["s"]["n_detections"] == 954


def test_resolve_group_files_lists_each_dated_record(tree: Path) -> None:
    """The accepted dated records name the March file and the run read in its place."""
    build_mixed_board(tree)
    current, dated = regen.resolve_group_files(tree / "results" / "pairwise" / BOARD / "group_8")

    assert len(current) == 3
    assert [(d.record_file, d.current_file) for d in dated] == [
        (
            f"results/pairwise/{BOARD}/group_8/x-s.json",
            f"results/rescore-2026-10-15/pairwise/{BOARD}/group_8/x-s.json",
        ),
        (
            f"results/pairwise/{BOARD}/group_8/y-s.json",
            f"results/rescore-2026-10-15/pairwise/{BOARD}/group_8/y-s.json",
        ),
    ]
    assert all(d.record_timestamp == MARCH and d.current_timestamp == TODAY for d in dated)


# --------------------------------------------------------------------------- #
# 2. A dated record is accepted only with a genuine successor beside it
# --------------------------------------------------------------------------- #


def test_dated_record_must_name_the_same_test(tree: Path) -> None:
    """A beside file for a different pair is refused, not silently read."""
    build_mixed_board(tree)
    write_pair(beside(tree, "x-s.json"), arm("x", 0.81), arm("z", 0.52), 0.0002, TODAY)

    with pytest.raises(AssertionError, match="different condition_b labels"):
        regen.load_pair_tests(tree / "results" / "pairwise" / BOARD / "group_8")


def test_dated_record_must_be_older_than_the_run_beside_it(tree: Path) -> None:
    """A "record" newer than the run beside it is not a dated record."""
    build_mixed_board(tree)
    write_pair(beside(tree, "x-s.json"), arm("x", 0.81), arm("s", 0.52), 0.0002, MARCH)
    write_pair(in_place(tree, "x-s.json"), arm("x", 0.80), arm("s", 0.50), 0.0001, TODAY)

    with pytest.raises(AssertionError, match="is not older"):
        regen.load_pair_tests(tree / "results" / "pairwise" / BOARD / "group_8")


def test_orphan_beside_file_is_refused(tree: Path) -> None:
    """A beside file with no record next to it would add a pair; it is refused."""
    build_mixed_board(tree)
    write_pair(beside(tree, "x-w.json"), arm("x", 0.81), arm("w", 0.4), 0.0, TODAY)

    with pytest.raises(AssertionError, match="no dated record"):
        regen.load_pair_tests(tree / "results" / "pairwise" / BOARD / "group_8")


def test_march_dated_file_without_a_run_beside_it_is_current(tree: Path) -> None:
    """Unmoved pairs kept their March files; the timestamp alone marks nothing."""
    unmoved = in_place(tree, "u-v.json")
    write_pair(unmoved, arm("u", 0.6), arm("v", 0.5), 0.2, MARCH)

    current, dated = regen.resolve_group_files(unmoved.parent)
    assert current == [unmoved]
    assert dated == []


def test_family_p_values_must_equal_the_per_test_files(tree: Path) -> None:
    """Gate A (families): the family artefact's raw p must equal today's per-test file."""
    family_dir = tree / "results" / "pairwise" / "20m"
    x_old, s_old = arm("x", 0.80), arm("s", 0.50)
    x_new, s_new = arm("x", 0.81), arm("s", 0.52)
    record = family_dir / "group_1_architecture" / "x-s.json"
    write_pair(record, x_old, s_old, 0.0001, MARCH, group=1, question="q")
    beside_root = tree / "results" / "rescore-2026-10-15" / "pairwise" / "20m"
    write_pair(
        beside_root / record.parent.name / record.name,
        x_new,
        s_new,
        0.0002,
        TODAY,
        group=1,
        question="q",
    )
    entry = {"group": 1, "question": "q", "label_a": "x", "label_b": "s", "family": "f"}
    fdr = family_dir / "fdr" / "pairwise_results_fdr.json"
    fdr.parent.mkdir(parents=True)

    today = {**entry, "p_value": 0.0002, "p_value_adj": 0.0002}
    fdr.write_text(json.dumps({"comparisons": [today]}))
    assert regen.load_pairwise_family(family_dir)[0]["confounded"] is False

    march = {**entry, "p_value": 0.0001, "p_value_adj": 0.0001}
    fdr.write_text(json.dumps({"comparisons": [march]}))
    with pytest.raises(AssertionError, match="differs from its per-test JSON"):
        regen.load_pairwise_family(family_dir)


# --------------------------------------------------------------------------- #
# 3. Gate B takes the count from today's run
# --------------------------------------------------------------------------- #


def build_chain_board(root: Path, name: str, n: int = 9) -> Path:
    """Build an ``n``-condition board in which every pair is significant.

    Every pair has p = 0, so all C(n, 2) pairs are BH-significant and the
    greedy clique opens one tier per condition: ``n`` tiers.

    Args:
        root: The synthetic repository root.
        name: Board directory name.
        n: Number of conditions.

    Returns:
        The board's run directory.
    """
    run_dir = root / "results" / "pairwise" / name
    arms = [arm(f"c{i}", 0.9 - 0.05 * i) for i in range(n)]
    pairs = [(arms[i], arms[j], 0.0) for i in range(n) for j in range(i + 1, n)]
    for a, b, p in pairs:
        write_pair(run_dir / "group_8" / f"{a['label']}-{b['label']}.json", a, b, p, TODAY)
    write_run_files(run_dir, pairs)
    return run_dir


def test_gate_b_takes_the_count_from_the_boards_own_run(tree: Path) -> None:
    """The 30 m gate passes on the run's own count, not the March 243."""
    run_dir = build_chain_board(tree, "leaderboard-30m")

    result = regen.process_board("leaderboard-30m", run_dir, "group_8")
    assert result["n_significant_full"] == 36
    assert result["n_tiers_full"] == 9


def test_gate_b_refuses_a_count_the_run_does_not_hold(tree: Path) -> None:
    """A recomputation that disagrees with the run's BH artefact stops the script."""
    run_dir = build_chain_board(tree, "leaderboard-30m")
    fdr = run_dir / "fdr" / "pairwise_results_fdr.json"
    doc = json.loads(fdr.read_text())
    doc["comparisons"][0]["p_value_adj"] = 0.2
    fdr.write_text(json.dumps(doc))

    with pytest.raises(AssertionError, match="Gate B"):
        regen.process_board("leaderboard-30m", run_dir, "group_8")


def test_gate_b_refuses_a_tier_count_other_than_published(tree: Path) -> None:
    """The tier count stays pinned to the published snapshot's nine."""
    run_dir = build_chain_board(tree, "leaderboard-30m", n=4)
    tests = regen.load_pair_tests(run_dir / "group_8")
    board = regen.build_board("leaderboard-30m", tests)

    with pytest.raises(AssertionError, match="4 tiers, published snapshot says 9"):
        regen.check_full_board_gate("leaderboard-30m", board, run_dir)


# --------------------------------------------------------------------------- #
# 4. The renderers keep the revision trail
# --------------------------------------------------------------------------- #


def small_board() -> regen.Board:
    """Return a three-condition board with one significant pair."""
    tests = [
        regen.PairTest("a", "b", 0.9, 0.8, 0.9, 0.8, 0.9, 0.8, 90, 80, 0.1, 0.001, False, "f1"),
        regen.PairTest("a", "c", 0.9, 0.7, 0.9, 0.7, 0.9, 0.7, 90, 70, 0.2, 0.0001, False, "f2"),
        regen.PairTest("b", "c", 0.8, 0.7, 0.8, 0.7, 0.8, 0.7, 80, 70, 0.1, 0.4, False, "f3"),
    ]
    return regen.build_board("leaderboard-20m", tests)


ORIGINAL_BANNER = "> **Last revised**: 2026-08-02 (original publication — E72 remediation)"


def test_renderers_keep_the_revision_banner() -> None:
    """The latest revision names itself and its predecessor, and keeps a changelog."""
    for text in (
        regen.render_leaderboard_md(small_board(), 20, ["d"]),
        regen.render_tiers_md(small_board(), 20, ["d"]),
        regen.render_families_md({"families": []}),
    ):
        assert "> **Last revised**: 2026-10-30 (" in text
        assert "Prior: 2026-08-02 (original publication — E72 remediation)" in text
        assert ORIGINAL_BANNER not in text
        changelog = text[text.index("## Changelog") :]
        assert changelog.index("### 2026-10-30 —") < changelog.index(
            "### 2026-08-02 — Original publication"
        )


def test_original_revision_renders_its_banner_verbatim() -> None:
    """``--revision 2026-08-02`` reproduces the original banner and adds no changelog."""
    original = regen.REVISIONS[0]
    leaderboard = regen.render_leaderboard_md(small_board(), 20, ["d"], original)
    assert leaderboard.splitlines()[2] == (
        f"{ORIGINAL_BANNER}. Regenerated from the March round-robin with the "
        "coverage-confounded cells dropped."
    )
    assert "## Changelog" not in leaderboard
    assert "remains valid for these rows" in leaderboard
    tiers = regen.render_tiers_md(small_board(), 20, ["d"], original)
    assert tiers.splitlines()[2] == f"{ORIGINAL_BANNER}."
    assert "## Changelog" not in tiers


def test_latest_revision_does_not_assert_the_march_mcc_column() -> None:
    """After the restatement the March snapshot's MCC column is not claimed current."""
    text = regen.render_leaderboard_md(small_board(), 20, ["d"])
    assert "remains valid for these rows" not in text
    assert "it is not asserted current for these rows" in text


def test_each_revision_refuses_the_wrong_input_layout() -> None:
    """The original renders only March inputs; the latest only the restated layout."""
    original, latest = regen.REVISIONS[0], regen.LATEST_REVISION
    regen.check_revision_layout(original, 0)
    regen.check_revision_layout(latest, 100)
    with pytest.raises(ValueError, match="March layout"):
        regen.check_revision_layout(original, 1)
    with pytest.raises(ValueError, match="restated layout"):
        regen.check_revision_layout(latest, 0)


def test_manifest_records_the_dated_records_for_later_revisions() -> None:
    """Later revisions name every dated record and the run read in its place."""
    board = small_board()
    record = regen.DatedRecord("results/pairwise/r.json", "results/rescore/r.json", MARCH, TODAY)
    latest = regen.board_manifest(board, board, 20, "src", ["d"], 2, dated_records=[record])
    provenance = latest["metadata"]["provenance"]
    assert latest["metadata"]["version"] == "1.1.0"
    assert provenance["revision"]["n_dated_records"] == 1
    assert provenance["revision"]["dated_records"] == [
        {"record": "results/pairwise/r.json", "read_in_its_place": "results/rescore/r.json"}
    ]
    original = regen.board_manifest(board, board, 20, "src", ["d"], 2, regen.REVISIONS[0])
    assert original["metadata"]["version"] == "1.0.0"
    assert "revision" not in original["metadata"]["provenance"]


def test_ordering_paragraph_reproduces_the_original_text() -> None:
    """§ 3.1's computed paragraph equals the 2026-08-02 literal on the March figures."""
    facts = {
        "moved": "flash-high-image-3-of-5--flash-min-vf (t=0.15)",
        "moved_rank": 10,
        "moved_f1": 0.777778,
        "n_higher_later": 2,
        "clique_span": "0.814",
        "opener": "flash-high-text N=10 N=10, 9-of-10",
        "opener_f1": 0.796767,
        "boundary_member": "flash-high-text N=30 N=30, 26-of-30",
        "boundary_q": 0.0463403,
        "other_inversions": [],
    }
    assert regen.ordering_paragraph(facts) == (
        "Greedy-clique tiering is order-dependent, and the published 20 m "
        "snapshot (`results/paper-tables/leaderboard_tiers_20m.md`) ranks "
        "one condition out of F1 order: `flash-high-image-3-of-5--flash-min-vf "
        "(t=0.15)` (F1 0.778) sits at rank 10, ahead of two higher-F1 "
        "conditions. Processed there it joins the 0.814 clique; processed in "
        "strict F1 order it is reached only after `flash-high-text N=10` "
        "(F1 0.797) has already opened the next tier — and that boundary "
        "rests on a single borderline pair (`FH text 26/30` versus "
        "`FH text 9/10`, q = 0.046)."
    )


# --------------------------------------------------------------------------- #
# 5. Before -> after against the previous revision's outputs
# --------------------------------------------------------------------------- #


def fake_baseline_reader(files: dict[str, str]):
    """Return a ``(ref, path) -> text`` reader over an in-memory file map."""

    def reader(ref: str, rel_path: str) -> str:
        assert ref == "base"
        return files[rel_path]

    return reader


def test_revision_diff_reports_moves_and_verdict_flips() -> None:
    """A pair that loses significance and a family member that gains it are both listed."""
    board = small_board()  # a-b and a-c significant; b-c not
    manifest = {
        "metadata": {
            "n_comparisons": 3,
            "n_conditions": 3,
            "fdr_correction": {"n_significant": 1},
            "tiering": {"n_tiers": 3},
            "provenance": {"source_n_comparisons": 3, "source_n_significant": 1},
        },
        "comparisons": [
            {"label_a": "a", "label_b": "b", "p_value_raw": 0.06, "p_value_adj": 0.09,
             "significant": False},
            {"label_a": "a", "label_b": "c", "p_value_raw": 0.0001, "p_value_adj": 0.0003,
             "significant": True},
            {"label_a": "b", "label_b": "c", "p_value_raw": 0.4, "p_value_adj": 0.4,
             "significant": False},
        ],
    }
    csv_text = "rank,condition,tier,f1\n1,a,1,0.9\n2,b,1,0.79\n3,c,2,0.7\n"
    member = {"group": 7, "question": "N=30 vs N=10", "label_a": "m", "label_b": "n"}
    families = {
        "families": [
            {
                "artefact": "results/pairwise/20m",
                "family": "confirmatory",
                "n_retained": 1,
                "significant_recomputed": 0,
                "members": [{**member, "p_raw": 0.0375, "q_recomputed": 0.050735}],
            }
        ]
    }
    files = {"results/e43-board-regen/bh-families/families_recomputed.json": json.dumps(families)}
    for name in regen.BOARDS:
        files[f"results/e43-board-regen/{name}/run_manifest.json"] = json.dumps(manifest)
        files[f"results/e43-board-regen/{name}/leaderboard.csv"] = csv_text
    baseline = regen.read_baseline("base", fake_baseline_reader(files))

    board_result = {"new_board": board, "n_significant_full": 2, "n_pairs_full": 3}
    family_result = {
        "artefact": "results/pairwise/20m",
        "family": "confirmatory",
        "n_retained": 1,
        "significant_recomputed": 1,
        "members": [{**member, "p_raw": 0.0357, "q_recomputed": 0.0483}],
    }
    diff = regen.revision_diff(baseline, {BOARD: board_result}, [family_result])

    moved = diff["boards"][BOARD]
    assert [(c["condition_a"], c["condition_b"]) for c in moved["verdict_changes"]] == [("a", "b")]
    assert moved["significant_before"] == 1 and moved["significant_after"] == 2
    # Only b moves: F1 0.79 -> 0.80 and tier 1 -> 2; a and c keep both.
    assert [c["condition"] for c in moved["condition_moves"]] == ["b"]
    flip = diff["families"][0]["verdict_changes"][0]
    assert (flip["q_before"], flip["q_after"], flip["significant_after"]) == (
        0.050735,
        0.0483,
        True,
    )

    changelog = "\n".join(regen.board_changelog_lines(regen.LATEST_REVISION, diff, BOARD, 4))
    assert "| b | 0.790000 | 0.800000 | 1 | 2 |" in changelog
    families_md = regen.render_families_md({"families": [], "diff": diff, "n_dated": 4})
    assert "| 0.0375 → 0.0357 | 0.050735 → 0.048300 | ns → significant |" in families_md


def test_revision_diff_refuses_a_membership_change() -> None:
    """The regeneration changes values, never which pairs are on the board."""
    board = small_board()
    baseline = {
        "ref": "base",
        "boards": {
            BOARD: {
                "pairs": {frozenset({"a", "b"}): {}},
                "conditions": {},
                "source_n_significant": 0,
                "n_significant": 0,
                "n_tiers": 0,
            }
        },
        "families": {},
    }
    with pytest.raises(AssertionError, match="retained pair set changed"):
        regen.revision_diff(baseline, {BOARD: {"new_board": board}}, [])
