"""Tier-1 tests for the absence-refusal pairing rules (PI ruling 2026-09-11).

Seventy pairing rows were blocked with "no committed pre-verifier set was
found". That refusal conflated two different states: no consensus GeoJSON names
the cell's shell (true), and no candidate universe is recorded anywhere (mostly
false). These tests pin the four rules that separate them, and the two
materialiser modes they need — every one of which can silently pair a cell with
a universe its verifier never saw if its guard is dropped.
"""

from __future__ import annotations

import json

import pytest

from scripts import build_verifier_pairing_worklist as b
from scripts import materialise_pairing_twin as m

pytestmark = pytest.mark.tier1


def _manifest(path, votes, *, passes=None, tiles=True):
    """Write a candidate manifest with the given vote counts."""
    candidates = []
    for index, vote in enumerate(votes):
        props = {} if vote is None else {"vote_count": vote}
        if passes is not None:
            props["total_passes"] = passes
        candidates.append({
            "candidate_id": index,
            "source_tile": f"tile_{index}.png" if tiles else "",
            "centroid_x": 400000.0 + index, "centroid_y": 4700000.0 + index,
            "properties": props,
        })
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": "1.0", "source_geojson": "src.geojson",
                                "candidates": candidates}), encoding="utf-8")
    return path


class TestManifestShape:
    """The vote structure a rule reads before it accepts a manifest."""

    def test_reads_floor_ceiling_and_declared_basis(self, tmp_path):
        path = _manifest(tmp_path / "candidate_manifest.json", [1, 2, 5], passes=5)
        shape = b._manifest_shape(path)
        assert (shape["min_vote"], shape["max_vote"], shape["basis"]) == (1, 5, 5)
        assert shape["n_candidates"] == 3

    def test_basis_is_none_when_candidates_disagree(self, tmp_path):
        """A manifest whose candidates claim different N cannot vouch for one."""
        path = _manifest(tmp_path / "candidate_manifest.json", [1, 2])
        doc = json.loads(path.read_text())
        doc["candidates"][0]["properties"]["total_passes"] = 5
        doc["candidates"][1]["properties"]["total_passes"] = 10
        path.write_text(json.dumps(doc), encoding="utf-8")
        assert b._manifest_shape(path)["basis"] is None

    def test_a_vote_less_manifest_reports_no_votes(self, tmp_path):
        path = _manifest(tmp_path / "candidate_manifest.json", [None, None])
        shape = b._manifest_shape(path)
        assert shape["n_voted"] == 0 and shape["min_vote"] is None

    def test_shell_at_counts_the_nested_subset(self, tmp_path):
        path = _manifest(tmp_path / "candidate_manifest.json", [1, 3, 4, 5])
        assert (b._shell_at(path, 3), b._shell_at(path, 5)) == (3, 1)


class TestSinglePassRule:
    """N = 1, where the shell is the whole universe."""

    def test_accepts_a_vote_less_single_pass_manifest(self, tmp_path):
        _manifest(tmp_path / "crops" / "pool-a" / "candidate_manifest.json",
                  [None, None, None])
        path, shape, refusal = b._find_single_pass_manifest(
            tmp_path, "pool-a", 1, 1, tmp_path)
        assert refusal is None and shape["n_candidates"] == 3
        assert path.endswith("crops/pool-a/candidate_manifest.json")

    @pytest.mark.parametrize("n_passes, votes", [(5, 1), (1, 2), (3, 3)])
    def test_refuses_outside_n1_k1(self, tmp_path, n_passes, votes):
        _manifest(tmp_path / "crops" / "pool-a" / "candidate_manifest.json", [None])
        path, _shape, refusal = b._find_single_pass_manifest(
            tmp_path, "pool-a", n_passes, votes, tmp_path)
        assert path is None and "N = 1 and k = 1" in refusal

    def test_refuses_a_manifest_that_does_record_votes(self, tmp_path):
        """Votes present means shells exist; assuming one would be a guess."""
        _manifest(tmp_path / "crops" / "pool-a" / "candidate_manifest.json", [1, 2])
        path, _shape, refusal = b._find_single_pass_manifest(
            tmp_path, "pool-a", 1, 1, tmp_path)
        assert path is None and "DOES record vote counts" in refusal


class TestShellManifestsRule:
    """A universe recorded across a base manifest and a committed increment."""

    @pytest.fixture
    def repo(self, tmp_path, monkeypatch):
        run = tmp_path / "outputs" / "run-x"
        _manifest(run / "crops" / "candidate_manifest.json", [4, 4, 5])
        monkeypatch.setattr(b, "_INCREMENT_ROOTS", ("increments",))
        return tmp_path, run

    def test_joins_disjoint_adjacent_shells(self, repo):
        root, run = repo
        _manifest(root / "increments" / "run-x" / "crops" / "candidate_manifest.json",
                  [3, 3])
        paths, stats, refusal = b._find_shell_manifests(run, 3, 5, root)
        assert refusal is None and len(paths) == 2
        assert stats["n_candidates"] == 5 and stats["n_at_threshold"] == 5

    def test_refuses_overlapping_shells(self, repo):
        """Overlap means a candidate would be counted twice in the twin."""
        root, run = repo
        _manifest(root / "increments" / "run-x" / "crops" / "candidate_manifest.json",
                  [3, 4])
        paths, _stats, refusal = b._find_shell_manifests(run, 3, 5, root)
        assert not paths and "overlap" in refusal

    def test_refuses_a_gap_between_the_shells(self, repo):
        """A hole means the twin is missing candidates the verifier saw."""
        root, run = repo
        _manifest(root / "increments" / "run-x" / "crops" / "candidate_manifest.json",
                  [2, 2])
        paths, _stats, refusal = b._find_shell_manifests(run, 2, 5, root)
        assert not paths and "unbroken shell" in refusal

    def test_defers_when_the_base_already_reaches_k(self, repo):
        """No increment is needed, and the single-manifest rule is the right one."""
        root, run = repo
        paths, _stats, refusal = b._find_shell_manifests(run, 4, 5, root)
        assert not paths and "already reaches" in refusal

    def test_refuses_when_no_increment_is_committed(self, repo):
        root, run = repo
        paths, _stats, refusal = b._find_shell_manifests(run, 3, 5, root)
        assert not paths and "no committed increment" in refusal


class TestMaterialiserModes:
    """The two twin-building modes the new rules need."""

    def test_single_pass_keeps_every_candidate(self, tmp_path):
        path = _manifest(tmp_path / "candidate_manifest.json", [None, None])
        features, stats = m.build_twin(json.loads(path.read_text()), 1, single_pass=True)
        assert stats["n_kept"] == 2
        assert all(f["properties"]["vote_count"] == 1 for f in features)

    def test_single_pass_is_refused_above_k1(self, tmp_path):
        path = _manifest(tmp_path / "candidate_manifest.json", [None])
        with pytest.raises(m.TwinMaterialisationError, match="only at k = 1"):
            m.build_twin(json.loads(path.read_text()), 2, single_pass=True)

    def test_single_pass_is_refused_when_votes_exist(self, tmp_path):
        path = _manifest(tmp_path / "candidate_manifest.json", [1, 2])
        with pytest.raises(m.TwinMaterialisationError, match="DO record"):
            m.build_twin(json.loads(path.read_text()), 1, single_pass=True)

    def test_manifest_union_rekeys_candidate_ids(self, tmp_path):
        """Both files number from zero; the union must not emit duplicate ids."""
        base = _manifest(tmp_path / "a" / "candidate_manifest.json", [4, 5])
        inc = _manifest(tmp_path / "b" / "candidate_manifest.json", [3, 3])
        out = tmp_path / "twin.geojson"
        assert m.main(["--crop-manifest", str(base), "--crop-manifest", str(inc),
                       "--min-votes", "3", "--output", str(out)]) == 0
        doc = json.loads(out.read_text())
        ids = [f["properties"]["candidate_id"] for f in doc["features"]]
        assert ids == [0, 1, 2, 3]
        assert doc["_materialised"]["mode"] == "manifest-union"
        assert len(doc["_materialised"]["manifests"]) == 2

    def test_an_empty_shell_is_refused_not_written(self, tmp_path):
        base = _manifest(tmp_path / "a" / "candidate_manifest.json", [1, 2])
        out = tmp_path / "twin.geojson"
        assert m.main(["--crop-manifest", str(base), "--min-votes", "5",
                       "--output", str(out)]) == 2
        assert not out.exists()


class TestDeriveVoteShell:
    """The null-``vote_threshold`` derivation (PI ruling 2026-09-11, later).

    Sixteen verified cells recorded no vote threshold and were refused before
    any pairing rule ran. A null is written for two reasons and in both the
    shell is determined; anything else must stay refused.
    """

    def test_a_pool_that_names_its_shell_supplies_k_and_n(self):
        shell = b._derive_vote_shell("image-t0.7-n30-18of30", 1)
        assert shell is not None
        assert shell[0] == 18 and shell[1] == 30
        assert "names its own shell" in shell[2]

    def test_the_consensus_infix_is_stripped_from_the_lineage(self):
        """``<lineage>-consensus-<k>of<N>`` pools have sets named without it."""
        match = b._POOL_NAMED_SHELL_RE.match("flash-high-text-consensus-16of30")
        assert match is not None
        assert match.group("lineage") == "flash-high-text"
        assert (match.group("k"), match.group("n")) == ("16", "30")

    def test_a_named_shell_outranks_the_vacuous_one(self):
        """A pre-aggregated pool also registers N = 1; k = 1 would mispair it."""
        assert b._derive_vote_shell("text-consensus-5of5", 1)[:2] == (5, 5)

    def test_a_single_pass_cell_gets_the_vacuous_shell(self):
        shell = b._derive_vote_shell("detect_brief-text", 1)
        assert shell is not None and shell[:2] == (1, 1)
        assert "single proposer pass" in shell[2]

    @pytest.mark.parametrize("pool, n_passes", [
        ("track2-text-t0.7", 5),      # several passes, and no shell named
        ("flash-high-text-1of5", 5),  # a vote >= 1 pool, not a fused set
        ("", 3),
    ])
    def test_refuses_anything_else(self, pool, n_passes):
        assert b._derive_vote_shell(pool, n_passes) is None

    def test_refuses_an_impossible_shell(self):
        """``k > N`` is a shell of nothing; the vacuous rule must not rescue it."""
        assert b._derive_vote_shell("pool-7of5", 5) is None


class TestPoolNamedCondition:
    """The pool as the LABEL of the registered condition that fed the verifier."""

    @staticmethod
    def _sources(decomposition):
        """A stand-in carrying only the field the rule reads."""
        return type("Sources", (), {"decomposition": decomposition})()

    @staticmethod
    def _call(sources, spec, run_id, pool):
        return b._find_pool_named_condition(sources, spec, run_id, pool)

    def test_finds_the_condition_the_pool_names_in_the_source_run(self):
        sources = self._sources({"home": {"conditions": [
            {"label": "text-consensus-5of5", "aggregation": "consensus",
             "eval_path": "results/x/evaluation.json"},
        ]}})
        spec = {"proposer_pool": "text-consensus-5of5", "source_run": "home"}
        found, refusal = self._call(sources, spec, "other", "text-consensus-5of5")
        assert refusal == ""
        assert found[0] == "home::text-consensus-5of5"

    def test_falls_back_to_the_cells_own_run(self):
        sources = self._sources({"own": {"conditions": [
            {"label": "text-t0.0", "aggregation": "none",
             "eval_path": "results/x/evaluation.json"},
        ]}})
        found, _refusal = self._call(sources, {"proposer_pool": "text-t0.0"},
                                     "own", "text-t0.0")
        assert found[0] == "own::text-t0.0"

    def test_refuses_a_verified_condition_as_a_pre_verifier_twin(self):
        """Pairing a verified cell with a verified cell measures no verifier."""
        sources = self._sources({"own": {"conditions": [
            {"label": "p", "aggregation": "verified", "eval_path": "e.json"},
        ]}})
        found, refusal = self._call(sources, {"proposer_pool": "p"}, "own", "p")
        assert found is None and "itself a VERIFIED cell" in refusal

    def test_refuses_a_condition_with_no_evaluation(self):
        sources = self._sources({"own": {"conditions": [
            {"label": "p", "aggregation": "consensus", "eval_path": None},
        ]}})
        found, refusal = self._call(sources, {"proposer_pool": "p"}, "own", "p")
        assert found is None and "records no evaluation" in refusal

    def test_refuses_when_no_condition_carries_the_label(self):
        sources = self._sources({"own": {"conditions": [
            {"label": "q", "aggregation": "consensus", "eval_path": "e.json"},
        ]}})
        found, refusal = self._call(sources, {"proposer_pool": "p"}, "own", "p")
        assert found is None and "no registered condition is labelled" in refusal


class TestSinglePassRunLevelManifest:
    """The run-level fallback for a run whose one manifest names no pool."""

    @staticmethod
    def _run(tmp_path, votes):
        """A run holding ``candidates/candidate_manifest.json`` and its source."""
        run = tmp_path / "outputs" / "run-y"
        path = _manifest(run / "candidates" / "candidate_manifest.json", votes)
        document = json.loads(path.read_text())
        source = run / "proposer" / "detections.geojson"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('{"type": "FeatureCollection", "features": []}',
                          encoding="utf-8")
        document["source_geojson"] = str(source.relative_to(tmp_path))
        path.write_text(json.dumps(document), encoding="utf-8")
        return run

    def test_accepts_a_single_lineage_run(self, tmp_path):
        run = self._run(tmp_path, [None, None, None])
        path, shape, refusal = b._find_single_pass_manifest(
            run, "detect_brief-text", 1, 1, tmp_path, n_lineages=1)
        assert refusal is None and shape["n_candidates"] == 3
        assert path.endswith("candidates/candidate_manifest.json")

    @pytest.mark.parametrize("n_lineages", [0, 2, 41])
    def test_refuses_a_multi_lineage_run(self, tmp_path, n_lineages):
        """With a second pool the run's one manifest could belong to either."""
        run = self._run(tmp_path, [None])
        path, _shape, refusal = b._find_single_pass_manifest(
            run, "detect_brief-text", 1, 1, tmp_path, n_lineages=n_lineages)
        assert path is None and "single-lineage run" in refusal

    def test_refuses_when_the_source_geojson_is_absent(self, tmp_path):
        """An unreadable source leaves the twin's provenance uncheckable."""
        run = self._run(tmp_path, [None])
        path = run / "candidates" / "candidate_manifest.json"
        document = json.loads(path.read_text())
        document["source_geojson"] = "outputs/run-y/proposer/gone.geojson"
        path.write_text(json.dumps(document), encoding="utf-8")
        found, _shape, refusal = b._find_single_pass_manifest(
            run, "detect_brief-text", 1, 1, tmp_path, n_lineages=1)
        assert found is None and "readable file" in refusal

    def test_refuses_a_run_level_manifest_that_records_votes(self, tmp_path):
        run = self._run(tmp_path, [1, 2, 3])
        found, _shape, refusal = b._find_single_pass_manifest(
            run, "detect_brief-text", 1, 1, tmp_path, n_lineages=1)
        assert found is None and "DOES record vote counts" in refusal

    def test_a_pool_named_manifest_still_wins(self, tmp_path):
        """The run-level fallback must not override a pool-attributed manifest."""
        run = self._run(tmp_path, [None])
        _manifest(run / "crops" / "detect_brief-text" / "candidate_manifest.json",
                  [None, None])
        path, shape, refusal = b._find_single_pass_manifest(
            run, "detect_brief-text", 1, 1, tmp_path, n_lineages=1)
        assert refusal is None and shape["n_candidates"] == 2
        assert path.endswith("crops/detect_brief-text/candidate_manifest.json")
