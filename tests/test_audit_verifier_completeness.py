"""Tier-1 unit tests for `scripts/audit_verifier_completeness.py`.

Covers:

- Multi-iteration `_iterK` suffix stripping in candidate counting.
- Zero-gap PASS verdict.
- Positive-gap FAIL verdict.
- Surplus-results edge case (more results than candidates).
- Sibling manifest missing → REVIEW.
- Read-error on probabilities.json → REVIEW.
- Non-empty `cleanup_history` with residual `still_missing` → REVIEW.
- Path exemptions (archive/**, *.backup).
- End-to-end audit_repo on a synthetic tree.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.audit_verifier_completeness import (
    CellAudit,
    audit_one,
    audit_repo,
    count_unique_candidates,
    find_manifest,
    is_exempt,
)


# ----------------------------------------------------------------------------
# Helpers — synthetic cell-directory builders
# ----------------------------------------------------------------------------


def make_cell(
    cell_dir: Path,
    n_candidates: int,
    n_results: int,
    *,
    iterations: int = 1,
    cleanup_history: list[dict] | None = None,
    omit_manifest: bool = False,
    omit_results_key: bool = False,
    surplus_results: int = 0,
) -> Path:
    """Materialise a synthetic verifier-output cell on disk.

    Returns the path to the cell's `probabilities.json`.
    """
    cell_dir.mkdir(parents=True, exist_ok=True)

    if not omit_manifest:
        manifest = {
            "version": "test",
            "candidates": [
                {"candidate_id": i, "crop_file": f"crops/candidate_{i:05d}.png"}
                for i in range(n_candidates)
            ],
        }
        (cell_dir / "candidate_manifest.json").write_text(json.dumps(manifest))

    results: dict[str, dict] = {}
    for i in range(n_results):
        cand_id = f"candidate_{i:05d}"
        for k in range(iterations):
            key = cand_id if iterations == 1 else f"{cand_id}_iter{k}"
            results[key] = {"score": 0.5}

    # Optional surplus results — keys with no matching manifest candidate.
    for j in range(surplus_results):
        cand_id = f"candidate_{n_candidates + j:05d}"
        results[cand_id] = {"score": 0.5}

    prob: dict = {"version": "test"}
    if not omit_results_key:
        prob["results"] = results
    if cleanup_history is not None:
        prob["cleanup_history"] = cleanup_history

    prob_path = cell_dir / "probabilities.json"
    prob_path.write_text(json.dumps(prob))
    return prob_path


# ----------------------------------------------------------------------------
# count_unique_candidates
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestCountUniqueCandidates:
    """The `_iterK` deduplication logic."""

    def test_single_pass_returns_len(self) -> None:
        results = {f"candidate_{i:05d}": {} for i in range(7)}
        assert count_unique_candidates(results) == 7

    def test_multi_iter_dedupes_to_base(self) -> None:
        results = {
            f"candidate_{i:05d}_iter{k}": {}
            for i in range(5)
            for k in range(3)
        }
        # 5 unique base IDs across 3 iterations each → 15 keys → 5 unique.
        assert len(results) == 15
        assert count_unique_candidates(results) == 5

    def test_mixed_iter_and_single(self) -> None:
        results = {
            "candidate_00001": {},
            "candidate_00002_iter0": {},
            "candidate_00002_iter1": {},
            "candidate_00003_iter5": {},
        }
        assert count_unique_candidates(results) == 3

    def test_none_returns_zero(self) -> None:
        assert count_unique_candidates(None) == 0

    def test_non_dict_returns_zero(self) -> None:
        assert count_unique_candidates([1, 2, 3]) == 0  # type: ignore[arg-type]


# ----------------------------------------------------------------------------
# is_exempt — exemption rules
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestIsExempt:
    """Silent exemptions: archive/** and *.backup."""

    def test_archive_top_level(self) -> None:
        assert is_exempt(Path("archive/old/probabilities.json"))

    def test_archive_nested(self) -> None:
        assert is_exempt(Path("foo/archive/bar/probabilities.json"))

    def test_backup_suffix(self) -> None:
        assert is_exempt(Path("outputs/foo/probabilities.json.pre-cleanup-X.backup"))

    def test_normal_path_not_exempt(self) -> None:
        assert not is_exempt(Path("outputs/h11/foo/probabilities.json"))

    def test_archive_only_exact_dir_name(self) -> None:
        # 'archives' (with trailing s) is not exempt.
        assert not is_exempt(Path("archives/foo/probabilities.json"))


# ----------------------------------------------------------------------------
# audit_one — per-cell verdict
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestAuditOne:
    """The full per-cell audit for each verdict bucket."""

    def test_pass_zero_gap(self, tmp_path: Path) -> None:
        prob = make_cell(tmp_path / "cell-a", n_candidates=10, n_results=10)
        audit = audit_one(prob, tmp_path)
        assert audit.verdict == "PASS"
        assert audit.expected == 10
        assert audit.actual == 10
        assert audit.gap == 0
        assert audit.review_reasons == []

    def test_fail_positive_gap(self, tmp_path: Path) -> None:
        prob = make_cell(tmp_path / "cell-b", n_candidates=10, n_results=7)
        audit = audit_one(prob, tmp_path)
        assert audit.verdict == "FAIL"
        assert audit.gap == 3

    def test_review_no_manifest(self, tmp_path: Path) -> None:
        prob = make_cell(
            tmp_path / "cell-c", n_candidates=5, n_results=5, omit_manifest=True
        )
        audit = audit_one(prob, tmp_path)
        assert audit.verdict == "REVIEW"
        assert "no_manifest_or_matching_consensus_found" in audit.review_reasons
        assert audit.expected is None
        assert audit.actual == 5

    def test_pass_via_consensus_fallback(self, tmp_path: Path) -> None:
        # Cell with no manifest, but a sibling consensus dir whose
        # consensus_t1.geojson feature count matches the result count.
        parent = tmp_path / "campaign"
        cell = parent / "verified-v1-n5"
        cell.mkdir(parents=True)
        # Build a probabilities.json with 7 results, no manifest sibling.
        prob_data = {
            "results": {f"candidate_{i:05d}": {"score": 0.5} for i in range(7)}
        }
        prob = cell / "probabilities.json"
        prob.write_text(json.dumps(prob_data))
        # Build a consensus-n5 sibling with 7 features.
        consensus_dir = parent / "consensus-n5"
        consensus_dir.mkdir()
        features = [{"type": "Feature", "properties": {}, "geometry": None} for _ in range(7)]
        (consensus_dir / "consensus_t1.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": features})
        )
        audit = audit_one(prob, tmp_path)
        assert audit.verdict == "PASS"
        assert audit.actual == 7
        assert audit.expected == 7
        assert audit.gap == 0

    def test_review_when_consensus_count_mismatches(self, tmp_path: Path) -> None:
        # No manifest AND no consensus dir whose feature count matches.
        parent = tmp_path / "campaign"
        cell = parent / "verified-v1-n5"
        cell.mkdir(parents=True)
        prob_data = {
            "results": {f"candidate_{i:05d}": {"score": 0.5} for i in range(7)}
        }
        prob = cell / "probabilities.json"
        prob.write_text(json.dumps(prob_data))
        # Sibling consensus dir but with WRONG feature count (5, not 7).
        consensus_dir = parent / "consensus-n5"
        consensus_dir.mkdir()
        features = [{"type": "Feature", "properties": {}, "geometry": None} for _ in range(5)]
        (consensus_dir / "consensus_t1.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": features})
        )
        audit = audit_one(prob, tmp_path)
        assert audit.verdict == "REVIEW"
        assert "no_manifest_or_matching_consensus_found" in audit.review_reasons

    def test_review_surplus_results(self, tmp_path: Path) -> None:
        prob = make_cell(
            tmp_path / "cell-d", n_candidates=3, n_results=3, surplus_results=2
        )
        audit = audit_one(prob, tmp_path)
        assert audit.verdict == "REVIEW"
        assert audit.gap == -2
        assert any("surplus_results" in r for r in audit.review_reasons)

    def test_review_partial_cleanup_history(self, tmp_path: Path) -> None:
        prob = make_cell(
            tmp_path / "cell-e",
            n_candidates=10,
            n_results=10,
            cleanup_history=[
                {"recovered": 2, "still_missing": 1, "timestamp": "2026-05-01T00:00:00Z"}
            ],
        )
        audit = audit_one(prob, tmp_path)
        assert audit.verdict == "REVIEW"
        assert any("cleanup_history_still_missing=1" in r for r in audit.review_reasons)

    def test_review_clean_history_zero_residual(self, tmp_path: Path) -> None:
        # cleanup_history with still_missing=0 should NOT flip to REVIEW —
        # that's the normal post-cleanup state.
        prob = make_cell(
            tmp_path / "cell-f",
            n_candidates=10,
            n_results=10,
            cleanup_history=[{"recovered": 3, "still_missing": 0}],
        )
        audit = audit_one(prob, tmp_path)
        assert audit.verdict == "PASS"
        assert audit.review_reasons == []

    def test_review_missing_results_key(self, tmp_path: Path) -> None:
        prob = make_cell(
            tmp_path / "cell-g", n_candidates=5, n_results=0, omit_results_key=True
        )
        audit = audit_one(prob, tmp_path)
        assert audit.verdict in ("FAIL", "REVIEW")
        assert "missing_results_key" in audit.review_reasons

    def test_review_unreadable_probabilities(self, tmp_path: Path) -> None:
        cell = tmp_path / "cell-h"
        cell.mkdir()
        (cell / "candidate_manifest.json").write_text(
            json.dumps({"candidates": [{"candidate_id": 0, "crop_file": "x"}]})
        )
        (cell / "probabilities.json").write_text("{not valid json")
        audit = audit_one(cell / "probabilities.json", tmp_path)
        assert audit.verdict == "REVIEW"
        assert any("probabilities_read_error" in r for r in audit.review_reasons)

    def test_multi_iteration_pass(self, tmp_path: Path) -> None:
        prob = make_cell(
            tmp_path / "cell-i", n_candidates=4, n_results=4, iterations=3
        )
        audit = audit_one(prob, tmp_path)
        assert audit.verdict == "PASS"
        assert audit.actual == 4  # 4 unique base IDs after stripping _iterK


# ----------------------------------------------------------------------------
# find_manifest — five project-conventional manifest locations
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestFindManifest:
    """The manifest lookup walker covers five project-conventional layouts."""

    def _write_manifest(self, p: Path, n: int) -> Path:
        p.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "candidates": [
                {"candidate_id": i, "crop_file": f"crops/candidate_{i:05d}.png"}
                for i in range(n)
            ]
        }
        p.write_text(json.dumps(manifest))
        return p

    def test_pattern1_same_dir(self, tmp_path: Path) -> None:
        # <cell>/candidate_manifest.json
        cell = tmp_path / "cell-A"
        cell.mkdir()
        prob = cell / "probabilities.json"
        prob.write_text("{}")
        m = self._write_manifest(cell / "candidate_manifest.json", 3)
        assert find_manifest(prob) == m

    def test_pattern2_crops_subdir(self, tmp_path: Path) -> None:
        # <cell>/crops/candidate_manifest.json
        cell = tmp_path / "cell-B"
        cell.mkdir()
        prob = cell / "probabilities.json"
        prob.write_text("{}")
        m = self._write_manifest(cell / "crops" / "candidate_manifest.json", 5)
        assert find_manifest(prob) == m

    def test_pattern3_parent_crops(self, tmp_path: Path) -> None:
        # <parent>/crops/candidate_manifest.json (55maps-like)
        parent = tmp_path / "campaign"
        cell = parent / "verified-v2"
        cell.mkdir(parents=True)
        prob = cell / "probabilities.json"
        prob.write_text("{}")
        m = self._write_manifest(parent / "crops" / "candidate_manifest.json", 7)
        assert find_manifest(prob) == m

    def test_pattern4_parent_candidates(self, tmp_path: Path) -> None:
        # <parent>/candidates/candidate_manifest.json (proposer-verifier-384)
        parent = tmp_path / "proposer-verifier"
        cell = parent / "verified-adversarial-text-v1-prompt"
        cell.mkdir(parents=True)
        prob = cell / "probabilities.json"
        prob.write_text("{}")
        m = self._write_manifest(parent / "candidates" / "candidate_manifest.json", 9)
        assert find_manifest(prob) == m

    def test_pattern5_parent_shared_crops(self, tmp_path: Path) -> None:
        # <parent>/shared-crops/candidate_manifest.json (session-78 matrix)
        parent = tmp_path / "session-78-matrix"
        cell = parent / "verified-adversarial-text"
        cell.mkdir(parents=True)
        prob = cell / "probabilities.json"
        prob.write_text("{}")
        m = self._write_manifest(
            parent / "shared-crops" / "candidate_manifest.json", 11
        )
        assert find_manifest(prob) == m

    def test_pattern6_parent_crops_basename(self, tmp_path: Path) -> None:
        # <parent>/crops/<basename>/candidate_manifest.json (e47-style)
        parent = tmp_path / "e47-propose-brief"
        cell = parent / "verified" / "flash-high-text-1of5"
        cell.mkdir(parents=True)
        prob = cell / "probabilities.json"
        prob.write_text("{}")
        m = self._write_manifest(
            parent / "verified" / "crops" / "flash-high-text-1of5" / "candidate_manifest.json",
            13,
        )
        assert find_manifest(prob) == m

    def test_no_manifest_returns_none(self, tmp_path: Path) -> None:
        cell = tmp_path / "cell-empty"
        cell.mkdir()
        prob = cell / "probabilities.json"
        prob.write_text("{}")
        assert find_manifest(prob) is None

    def test_same_dir_takes_precedence(self, tmp_path: Path) -> None:
        # If multiple patterns match, the same-dir candidate wins (most specific).
        parent = tmp_path / "p"
        cell = parent / "verified"
        cell.mkdir(parents=True)
        prob = cell / "probabilities.json"
        prob.write_text("{}")
        same = self._write_manifest(cell / "candidate_manifest.json", 1)
        self._write_manifest(parent / "shared-crops" / "candidate_manifest.json", 99)
        assert find_manifest(prob) == same


# ----------------------------------------------------------------------------
# audit_repo — end-to-end on a synthetic tree
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestAuditRepo:
    """End-to-end: walk a synthetic root and aggregate per-cell verdicts."""

    def test_mixed_synthetic_tree(self, tmp_path: Path) -> None:
        # 1 PASS + 1 FAIL + 1 REVIEW, plus an exempt archive entry that
        # MUST NOT appear in audits.
        make_cell(tmp_path / "outputs/cell-pass", n_candidates=5, n_results=5)
        make_cell(tmp_path / "outputs/cell-fail", n_candidates=10, n_results=8)
        make_cell(
            tmp_path / "outputs/cell-review",
            n_candidates=3,
            n_results=3,
            omit_manifest=True,
        )
        make_cell(tmp_path / "archive/cell-old", n_candidates=99, n_results=1)
        # A backup file that should also be exempt.
        backup = tmp_path / "outputs/cell-pass/probabilities.json.pre-cleanup-X.backup"
        backup.write_text("{\"results\": {}}")

        audits = audit_repo(tmp_path)

        verdicts = {a.verdict for a in audits}
        assert verdicts == {"PASS", "FAIL", "REVIEW"}
        assert len(audits) == 3, (
            "archive/** and *.backup files must be exempt from auditing; "
            f"got {len(audits)} audits with paths {[a.path for a in audits]}"
        )

    def test_empty_tree_returns_empty(self, tmp_path: Path) -> None:
        assert audit_repo(tmp_path) == []


# ----------------------------------------------------------------------------
# CellAudit dataclass smoke
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestCellAuditDataclass:
    def test_default_review_reasons_is_empty_list(self) -> None:
        a = CellAudit(
            path="x",
            verdict="PASS",
            expected=1,
            actual=1,
            gap=0,
            cleanup_history_entries=0,
        )
        assert a.review_reasons == []
