"""Tier-1 tests for the per-architecture leaderboard-markdown ownership guard.

Covers the two halves of defect **D35** (Session 137 audit, finding F11):

1. ``scripts/build_tiered_leaderboard.write_leaderboard_markdown`` must refuse
   to write the per-architecture ``leaderboard_tiers_<buffer>m.md`` boards,
   which belong to ``scripts/enrich_per_arch_markdown.py``. Before the guard,
   both generators wrote those seven paths and the last one to run won.
2. ``scripts/regenerate_per_arch_md_from_json.py --verify`` must render into a
   temporary directory and compare, **writing nothing**. Before the fix it fell
   through to the write loop and then compared the files it had just written
   against the JSON it had just rendered — a check structurally unable to fail,
   which overwrote 140 tracked files each time it ran.

Also covers the markdown timestamp stabilisation added to the owner, so a no-op
regeneration is byte-identical rather than re-stamping every board.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.build_tiered_leaderboard import (
    PER_ARCH_OWNER,
    PerArchitectureOwnershipError,
    SelectedCondition,
    is_per_architecture_owned_markdown,
    write_leaderboard_markdown,
)
from scripts.enrich_per_arch_markdown import (
    _strip_md_timestamp,
    stabilise_markdown,
)
from scripts.regenerate_per_arch_md_from_json import (
    committed_git_commit,
    normalise_for_compare,
    stratum_era_arch,
    verify_targets,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _condition(label: str = "cond-a", f1: float = 0.75) -> SelectedCondition:
    """Build a minimal SelectedCondition the markdown writer accepts."""
    return SelectedCondition(
        label=label,
        geojson_path=Path("outputs/x.geojson"),
        best_threshold=1,
        era=2,
        track="text",
        category="single-pass",
        k=1,
        evaluations={
            20: {
                "buffer_metres": 20,
                "f1": f1,
                "f1_ci_lower": f1 - 0.03,
                "f1_ci_upper": f1 + 0.03,
                "precision": 0.8,
                "recall": 0.7,
            }
        },
        condition_id="",
        tile_mcc=0.5,
    )


def _tier_json(
    path: Path, label: str = "cond-a", f1: float = 0.75, metric: str = "f1"
) -> Path:
    """Write a minimal tier JSON of the shape the renderers consume."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {"metric": metric, "fdr_q": 0.05, "bounds": "inputs/b.geojson"},
        "tiers": [
            {
                "tier": 1,
                "conditions": [
                    {
                        "label": label,
                        "geojson": "outputs/x.geojson",
                        "best_threshold": 1,
                        "era": 2,
                        "track": "text",
                        "category": "single-pass",
                        "k": 1,
                        "tile_mcc": 0.5,
                        "evaluations": {
                            "20": {
                                "buffer_metres": 20,
                                "f1": f1,
                                "f1_ci_lower": f1 - 0.03,
                                "f1_ci_upper": f1 + 0.03,
                                "precision": 0.8,
                                "recall": 0.7,
                            }
                        },
                    }
                ],
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# Ownership guard
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
@pytest.mark.parametrize(
    "relpath,owned",
    [
        ("results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_20m.md", True),
        ("results/leaderboard/per-architecture/era1/consensus/leaderboard_tiers_100m.md", True),
        # The owner renders neither the MCC nor the q=0.01 variants.
        ("results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_mcc_20m.md", False),
        ("results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_q01_20m.md", False),
        # Same basename, different tree — the era boards are not the owner's.
        ("results/leaderboard/era2/leaderboard_tiers_20m.md", False),
        ("results/leaderboard/combined/era1/leaderboard_tiers_20m.md", False),
    ],
)
def test_ownership_predicate_matches_only_the_owners_boards(relpath, owned):
    assert is_per_architecture_owned_markdown(PROJECT_ROOT / relpath) is owned


@pytest.mark.tier1
def test_write_leaderboard_markdown_refuses_an_owned_board(tmp_path):
    """The bare writer must refuse, and must not create the file."""
    target = (
        tmp_path
        / "results" / "leaderboard" / "per-architecture" / "era2" / "pv"
        / "leaderboard_tiers_20m.md"
    )
    target.parent.mkdir(parents=True)
    with pytest.raises(PerArchitectureOwnershipError) as exc:
        write_leaderboard_markdown(
            tiers=[[_condition()]],
            buffer_metres=20,
            output_path=target,
            metadata={"metric": "f1", "fdr_q": 0.05},
        )
    assert PER_ARCH_OWNER in str(exc.value)
    assert not target.exists()


@pytest.mark.tier1
def test_write_leaderboard_markdown_allows_unowned_siblings(tmp_path):
    """The MCC board in the same directory stays this writer's to produce."""
    target = (
        tmp_path
        / "results" / "leaderboard" / "per-architecture" / "era2" / "pv"
        / "leaderboard_tiers_mcc_20m.md"
    )
    target.parent.mkdir(parents=True)
    write_leaderboard_markdown(
        tiers=[[_condition()]],
        buffer_metres=20,
        output_path=target,
        metadata={"metric": "mcc", "fdr_q": 0.05},
    )
    assert target.is_file()
    assert "cond-a" in target.read_text(encoding="utf-8")


@pytest.mark.tier1
def test_ownership_guard_has_a_documented_override(tmp_path):
    """``allow_per_architecture`` exists for a deliberate migration only."""
    target = (
        tmp_path
        / "results" / "leaderboard" / "per-architecture" / "era3" / "consensus"
        / "leaderboard_tiers_50m.md"
    )
    target.parent.mkdir(parents=True)
    write_leaderboard_markdown(
        tiers=[[_condition()]],
        buffer_metres=20,
        output_path=target,
        metadata={"metric": "f1", "fdr_q": 0.05},
        allow_per_architecture=True,
    )
    assert target.is_file()


# --------------------------------------------------------------------------- #
# --verify writes nothing and can fail
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_verify_reports_a_match_without_touching_the_file(tmp_path):
    """A board that matches its JSON verifies OK and is left byte-identical."""
    stratum = tmp_path / "era2" / "single-pass"
    json_path = _tier_json(stratum / "leaderboard_tiers_mcc_20m.json", metric="mcc")
    md_path = stratum / "leaderboard_tiers_mcc_20m.md"
    write_leaderboard_markdown(
        tiers=[[_condition()]],
        buffer_metres=20,
        output_path=md_path,
        metadata={"metric": "mcc", "fdr_q": 0.05, "bounds": "inputs/b.geojson"},
    )
    before = md_path.read_bytes()
    mtime = md_path.stat().st_mtime_ns

    n_ok, n_mismatch, n_missing, _ = verify_targets([(json_path, md_path, 20)])

    assert (n_ok, n_mismatch, n_missing) == (1, 0, 0)
    assert md_path.read_bytes() == before
    assert md_path.stat().st_mtime_ns == mtime


@pytest.mark.tier1
def test_verify_fails_on_a_doctored_copy_and_does_not_repair_it(tmp_path):
    """The regression the fix exists for: verify must be able to fail.

    The old ``--verify`` wrote the file first, so drift was unobservable. Here
    the committed board is doctored; verify must report the mismatch and must
    leave the doctored bytes exactly as they were.
    """
    stratum = tmp_path / "era2" / "single-pass"
    json_path = _tier_json(stratum / "leaderboard_tiers_mcc_20m.json", metric="mcc")
    md_path = stratum / "leaderboard_tiers_mcc_20m.md"
    write_leaderboard_markdown(
        tiers=[[_condition()]],
        buffer_metres=20,
        output_path=md_path,
        metadata={"metric": "mcc", "fdr_q": 0.05, "bounds": "inputs/b.geojson"},
    )
    doctored = md_path.read_text(encoding="utf-8").replace("0.750", "0.999")
    md_path.write_text(doctored, encoding="utf-8")

    n_ok, n_mismatch, n_missing, report = verify_targets([(json_path, md_path, 20)])

    assert (n_ok, n_mismatch, n_missing) == (0, 1, 0)
    assert any("MISMATCH" in line for line in report)
    assert md_path.read_text(encoding="utf-8") == doctored


@pytest.mark.tier1
def test_verify_reports_a_missing_board_rather_than_creating_it(tmp_path):
    stratum = tmp_path / "era2" / "single-pass"
    json_path = _tier_json(stratum / "leaderboard_tiers_mcc_20m.json", metric="mcc")
    md_path = stratum / "leaderboard_tiers_mcc_20m.md"

    n_ok, n_mismatch, n_missing, _ = verify_targets([(json_path, md_path, 20)])

    assert (n_ok, n_mismatch, n_missing) == (0, 0, 1)
    assert not md_path.exists()


@pytest.mark.tier1
def test_verify_run_leaves_the_working_tree_clean():
    """End-to-end: ``--verify`` against the real corpus must write nothing."""
    before = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    ).stdout
    subprocess.run(
        [".venv/bin/python", "scripts/regenerate_per_arch_md_from_json.py", "--verify"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=False,
    )
    after = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    ).stdout
    assert after == before


@pytest.mark.tier1
def test_write_mode_refuses_the_owners_boards():
    """``--write`` must not be a back door around the ownership decision."""
    from scripts.regenerate_per_arch_md_from_json import PER_ARCH_ROOT, write_targets

    owned = PER_ARCH_ROOT / "era2" / "pv" / "leaderboard_tiers_20m.md"
    before = owned.read_bytes() if owned.is_file() else None

    n_written, n_refused, report = write_targets(
        [(owned.with_suffix(".json"), owned, 20)]
    )

    assert (n_written, n_refused) == (0, 1)
    assert any("REFUSED" in line and PER_ARCH_OWNER in line for line in report)
    if before is not None:
        assert owned.read_bytes() == before


# --------------------------------------------------------------------------- #
# Comparison helpers
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_normalise_for_compare_ignores_only_provenance():
    a = "# T\n\n**Generated**: 2026-01-01T00:00:00+00:00\n**Git commit**: `aaa`\nrow 0.750\n"
    b = "# T\n\n**Generated**: 2026-08-20T06:00:00+00:00\n**Git commit**: `bbb`\nrow 0.750\n"
    c = "# T\n\n**Generated**: 2026-08-20T06:00:00+00:00\n**Git commit**: `bbb`\nrow 0.999\n"
    assert normalise_for_compare(a, "z") == normalise_for_compare(b, "z")
    assert normalise_for_compare(a, "z") != normalise_for_compare(c, "z")


@pytest.mark.tier1
def test_committed_git_commit_reads_the_boards_own_value(tmp_path):
    board = tmp_path / "leaderboard_tiers_30m.md"
    board.write_text(
        "# T\n\n**Generated**: x\n**Git commit**: `ef3ec4fe`\n", encoding="utf-8"
    )
    assert committed_git_commit(board) == "ef3ec4fe"
    assert committed_git_commit(tmp_path / "absent.md") == "(uncommitted)"


@pytest.mark.tier1
def test_stratum_era_arch_parses_the_path():
    p = Path("results/leaderboard/per-architecture/era2/single-pass+PV/leaderboard_tiers_40m.md")
    assert stratum_era_arch(p) == (2, "single-pass+PV")
    with pytest.raises(ValueError):
        stratum_era_arch(Path("results/leaderboard/era2/leaderboard_tiers_40m.md"))


# --------------------------------------------------------------------------- #
# Timestamp stabilisation in the owner
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_stabilise_markdown_carries_an_unchanged_boards_stamp_forward(tmp_path):
    board = tmp_path / "leaderboard_tiers_20m.md"
    body_template = "# T\n\n**Generated**: {}\n\n| a |\n"
    board.write_text(body_template.format("2026-05-06T00:00:00+00:00"), encoding="utf-8")

    rendered = _strip_md_timestamp(body_template.format("ignored"))
    out = stabilise_markdown(rendered, board, "2026-08-20T06:00:00+00:00")

    assert "2026-05-06T00:00:00+00:00" in out
    assert "2026-08-20" not in out


@pytest.mark.tier1
def test_stabilise_markdown_restamps_when_content_changed(tmp_path):
    board = tmp_path / "leaderboard_tiers_20m.md"
    board.write_text(
        "# T\n\n**Generated**: 2026-05-06T00:00:00+00:00\n\n| a |\n", encoding="utf-8"
    )

    rendered = _strip_md_timestamp("# T\n\n**Generated**: x\n\n| b |\n")
    out = stabilise_markdown(rendered, board, "2026-08-20T06:00:00+00:00")

    assert "2026-08-20T06:00:00+00:00" in out


@pytest.mark.tier1
def test_stabilise_markdown_can_be_switched_off(tmp_path):
    board = tmp_path / "leaderboard_tiers_20m.md"
    board.write_text(
        "# T\n\n**Generated**: 2026-05-06T00:00:00+00:00\n\n| a |\n", encoding="utf-8"
    )
    rendered = _strip_md_timestamp("# T\n\n**Generated**: x\n\n| a |\n")
    out = stabilise_markdown(
        rendered, board, "2026-08-20T06:00:00+00:00", stabilise=False
    )
    assert "2026-08-20T06:00:00+00:00" in out
