"""Tier-1 end-to-end tests for the uplift-supplement builder entry points.

The companion module ``test_uplift_supplement.py`` covers the library in
isolation. This one drives the four ``main()`` entry points over a miniature
committed corpus built under ``tmp_path``, which is the only way to pin the
behaviours that emerge from the builders wiring the library together:

* the master table is written, one row per registered spec, every row keyed;
* the exact column contract of ``conditions.csv`` (so deleting a column —
  ``stratum_id`` above all — goes red rather than silently shipping);
* ``--execute`` is refused by both worklist builders, and writes nothing;
* a cross-stratum pair RAISES out of the uplift computer (the guard was
  tautological until the worklist carried two separately derived strata);
* the with-verifier disclosure blocks on a floor > 1 stage and stays derivable
  on a floor == 1 stage — pinned in both directions, because a rule that only
  ever says "blocked" would pass a one-sided test;
* the uplift's sign and magnitude on a known pair.

The fixture corpus has three runs: ``alpha`` and ``beta`` share a stratum
(4-map-gs / curator / 20 m / era-1-340) and ``gamma`` sits in another
(55-map / student / 50 m / 55maps-8541), so cross-stratum behaviour is
exercisable without touching the real corpus.

Created: 2026-08-29 (uplift-supplement card, audit fix pass)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pytest

from scripts.build_k1_gapfill_worklist import main as k1_main
from scripts.build_uplift_supplement import CONDITION_COLUMNS
from scripts.build_uplift_supplement import main as flatten_main
from scripts.build_verifier_pairing_worklist import main as pairing_main
from scripts.compute_verifier_uplift import compute_uplift
from scripts.compute_verifier_uplift import main as uplift_main
from scripts.lib_uplift_supplement import (
    NOTATION_KEY_PATH,
    CrossStratumAggregationError,
)

pytestmark = pytest.mark.tier1

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: The published column contract of ``conditions.csv``. Duplicated here
#: DELIBERATELY rather than imported for comparison alone: a test that reads the
#: same tuple it asserts against cannot catch a deletion. Any change here is a
#: change to a published dataset's schema and should be a deliberate edit.
EXPECTED_CONDITION_COLUMNS = (
    "condition_id", "run_id", "label",
    "stratum_id", "corpus", "reference", "buffer_m", "frame_id", "n_tiles",
    "n_refs", "is_primary_buffer",
    "geometry", "tile_px", "overlap_px", "stride_px", "geometry_basis",
    "modality", "thinking", "temperature", "model_used",
    "architecture", "aggregation", "proposer_pool", "K", "N",
    "prob_t", "min_votes", "verified", "verifier_variant", "basis",
    "F1", "F1_CI_lo", "F1_CI_hi", "ci_method", "ci_unreliable",
    "precision", "recall",
    "MCC", "sensitivity", "specificity",
    "tile_TP", "tile_TN", "tile_FP", "tile_FN",
    "n_detections", "cost_usd", "cost_basis",
    "metrics_source", "eval_path", "detections_path", "reference_path",
    "reference_basis", "reference_consumed_path", "notes",
)


# --------------------------------------------------------------------------- #
# Fixture corpus
# --------------------------------------------------------------------------- #


def _write_json(path: Path, payload: Any) -> None:
    """Write a JSON document, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _evaluation(f1: float, buffer_m: int, gt: str, n_detections: int) -> dict:
    """Build an ``evaluate_detections`` evaluation document.

    Args:
        f1: F1 at the single reported buffer (precision and recall track it).
        buffer_m: The buffer radius reported.
        gt: Repo-relative ground-truth path the run consumed.
        n_detections: Detections scored.

    Returns:
        The document, complete with the ``cli_args`` recipe the worklist
        builders reproduce.
    """
    return {
        "version": "1.0",
        "timestamp": "2026-08-01T00:00:00Z",
        "summary": {
            "n_detections": n_detections,
            "buffers": [{
                "buffer_metres": buffer_m,
                "f1": f1, "precision": f1, "recall": f1,
                "f1_ci_lower": round(f1 - 0.05, 4),
                "f1_ci_upper": round(f1 + 0.05, 4),
                "f1_ci_method": "BCa",
                "ci_unreliable": False,
            }],
            "tile_classification": {
                "mcc": 0.5, "sensitivity": 0.6, "specificity": 0.7,
                "confusion": {"tp": 10, "tn": 20, "fp": 3, "fn": 4},
            },
        },
        "_metadata": {
            "cli_args": {
                "buffers": [buffer_m],
                "ground_truth": gt,
                "bounds": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
                "bootstrap": 10000,
                "seed": 42,
            },
            "bootstrap": {
                "n_iterations": 10000, "seed": 42, "resampling_unit": "tile_level",
            },
            "input_files": {"ground_truth": gt},
        },
    }


def _candidate_manifest(source: str, votes: list[int]) -> dict:
    """Build a verifier candidate manifest with the given vote counts."""
    return {
        "version": "1.0",
        "source_geojson": source,
        "total_detections": len(votes),
        "candidates": [
            {"candidate_id": i, "properties": {"vote_count": v}}
            for i, v in enumerate(votes)
        ],
    }


CURATOR = "inputs/vectors/references/mounds-reference.geojson"
STUDENT = "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    """Build a miniature committed corpus and return its repository root.

    Three runs. ``alpha`` and ``beta`` share a stratum and differ only in their
    verifier's coverage floor (1 vs 2), which is what makes the with-verifier
    disclosure testable in both directions. ``gamma`` sits in a different
    stratum so cross-stratum machinery has something to refuse.
    """
    root = tmp_path / "repo"
    (root / "docs" / "methodology").mkdir(parents=True)
    (root / "docs" / "methodology" / "notation-key.md").write_text(
        (PROJECT_ROOT / NOTATION_KEY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    runs = {
        "alpha": ("4-map-gs", "curator", "era-1-340", 340, CURATOR, 20, [1, 2, 3]),
        "beta": ("4-map-gs", "curator", "era-1-340", 340, CURATOR, 20, [2, 3]),
        "gamma": ("55-map", "student", "55maps-8541", 8541, STUDENT, 50, [1, 2]),
    }

    registry, facts, decomposition, passes = [], {}, {}, []
    for run_id, (corpus_id, _ref, frame, tiles, gt, buffer_m, votes) in runs.items():
        pool = f"text-{run_id}"
        run_dir = root / "outputs" / run_id
        registry.append({
            "run_id": run_id,
            "directory_path": f"outputs/{run_id}",
            "status": "active",
        })
        facts[run_id] = {
            "purpose": f"fixture run {run_id}",
            "tile_size_px": 384,
            "corpus": corpus_id,
            "gt_reference": "student" if corpus_id == "55-map" else "curator",
            "scope": {
                "test_set_id": frame,
                "bounds_path": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
                "n_test_tiles": tiles,
            },
        }

        # Three committed passes. Their manifest rows are written OUT of
        # pass_n order on purpose: the first-N rule depends on the loader
        # sorting them, and an unsorted bucket would silently consume the
        # wrong pass.
        for pass_n in (3, 1, 2):
            name = f"detections_{pool}_run0{pass_n}.geojson"
            _write_json(run_dir / pool / f"run_{pass_n}" / name,
                        {"type": "FeatureCollection", "features": []})
            _write_json(
                run_dir / pool / f"run_{pass_n}" / f"detections_{pool}_run0{pass_n}.meta.json",
                {"configuration": {
                    "model": "gemini-3-flash-preview", "temperature": 0.7,
                    "thinking_level": "minimal", "include_example_images": False,
                }},
            )
            passes.append({
                "pass_id": f"{run_id}::{pool}::run{pass_n}",
                "run_id": run_id, "proposer_pool": pool, "pass_n": pass_n,
                "model_used": "gemini-3-flash-preview", "modality": "text",
                "thinking_level": "minimal", "temperature": 0.7,
                "status": "ok", "n_tiles_processed": tiles,
                "cost_usd": float(pass_n),
                "provenance": {"source_files": [], "extractor_version": "test"},
            })

        _write_json(run_dir / pool / "consensus" / "consensus-2of3.geojson",
                    {"type": "FeatureCollection", "features": []})
        _write_json(run_dir / "crops" / "candidate_manifest.json",
                    _candidate_manifest(
                        f"outputs/{run_id}/{pool}/consensus/consensus-2of3.geojson",
                        votes,
                    ))
        # A smoke rehearsal in every run: 12 candidates, one of them a
        # singleton. Excluding it is what keeps beta's floor at 2, so the
        # exclusion is load-bearing rather than cosmetic.
        _write_json(run_dir / "_smoke" / "crops" / "candidate_manifest.json",
                    _candidate_manifest("subset.geojson", [1, 5]))

        _write_json(root / "results" / run_id / "consensus" / "evaluation.json",
                    _evaluation(0.60, buffer_m, gt, 100))
        _write_json(root / "results" / run_id / "verified" / "evaluation.json",
                    _evaluation(0.75, buffer_m, gt, 80))

        decomposition[run_id] = {
            "proposer_pools": {pool: {"modality": "text", "path": pool}},
            "verifier_passes": {},
            "conditions": [
                {
                    "label": "consensus-2of3", "architecture": "consensus",
                    "aggregation": "consensus", "proposer_pool": pool,
                    "n_passes": 3, "vote_threshold": 2, "prob_threshold": None,
                    "verifier_config": None,
                    "detections": f"outputs/{run_id}/{pool}/consensus/consensus-2of3.geojson",
                    "eval_path": f"results/{run_id}/consensus/evaluation.json",
                },
                {
                    "label": "verified-2of3", "architecture": "proposer-verifier",
                    "aggregation": "verified", "proposer_pool": pool,
                    "n_passes": 3, "vote_threshold": 2, "prob_threshold": 0.2,
                    "verifier_config": {"variant": "v1"},
                    "detections": f"outputs/{run_id}/verified/verified.geojson",
                    "eval_path": f"results/{run_id}/verified/evaluation.json",
                },
            ],
        }

    # ---- `delta`: one run, four verifier stages -------------------------- #
    # The three runs above have a single stage each, so every match short
    # circuits on `sole-manifest` and the matcher proper is never reached. This
    # run exercises it: two pools (text and image) so a lineage crossing is
    # possible, a union_k5 stage the N = 3 narrowing must drop, and a ge2of3
    # stage only the consensus-shell rule can separate from the union stage.
    delta = root / "outputs" / "delta"
    registry.append({"run_id": "delta", "directory_path": "outputs/delta",
                     "status": "active"})
    facts["delta"] = {
        "purpose": "fixture run with several verifier stages",
        "tile_size_px": 384, "corpus": "4-map-gs", "gt_reference": "curator",
        "scope": {
            "test_set_id": "era-1-340",
            "bounds_path": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
            "n_test_tiles": 340,
        },
    }
    for pool in ("text-delta", "image-delta"):
        for pass_n in (1, 2, 3):
            name = f"detections_{pool}_run0{pass_n}.geojson"
            _write_json(delta / pool / f"run_{pass_n}" / name,
                        {"type": "FeatureCollection", "features": []})
            passes.append({
                "pass_id": f"delta::{pool}::run{pass_n}", "run_id": "delta",
                "proposer_pool": pool, "pass_n": pass_n,
                "model_used": "gemini-3-flash-preview",
                "modality": "image" if pool.startswith("image") else "text",
                "thinking_level": "minimal", "temperature": 0.7,
                "status": "ok", "n_tiles_processed": 340, "cost_usd": 1.0,
                "provenance": {"source_files": [], "extractor_version": "test"},
            })

    for relative, source, votes in (
        ("verifier/text-delta/crops", "union_k3.geojson", [1, 2, 3]),
        ("verifier/text-delta/crops_k5", "union_k5.geojson", [3, 4, 5]),
        ("verifier/text-delta/crops_ge2of3", "text-delta-ge2of3.geojson", [2, 3]),
        ("verifier/image-delta/crops", "union_k3.geojson", [2, 3]),
    ):
        _write_json(delta / relative / "candidate_manifest.json",
                    _candidate_manifest(source, votes))

    delta_conditions = []
    for label, pool in (
        ("text-delta-union-2of3", "text-delta"),
        ("image-delta-union-2of3", "image-delta"),
        ("text-delta-ge2of3", "text-delta"),
    ):
        _write_json(root / "results" / "delta" / label / "evaluation.json",
                    _evaluation(0.70, 20, CURATOR, 90))
        delta_conditions.append({
            "label": label, "architecture": "proposer-verifier",
            "aggregation": "verified", "proposer_pool": pool,
            "n_passes": 3, "vote_threshold": 2, "prob_threshold": 0.2,
            "verifier_config": {"variant": "v1"},
            "detections": f"outputs/delta/{label}.geojson",
            "eval_path": f"results/delta/{label}/evaluation.json",
        })
    decomposition["delta"] = {
        "proposer_pools": {
            "text-delta": {"modality": "text", "path": "text-delta"},
            "image-delta": {"modality": "image", "path": "image-delta"},
        },
        "verifier_passes": {},
        "conditions": delta_conditions,
    }

    _write_json(root / "results" / "run-registry.json",
                {"schema_version": "1.0", "generated_at": "2026-08-01T00:00:00Z",
                 "registry": registry})
    _write_json(root / "results" / "run-facts.json",
                {"_README": "fixture", "schema_version": "1.0", "facts": facts})
    _write_json(root / "results" / "run-conditions.json",
                {"_README": "fixture", "schema_version": "1.0",
                 "decomposition": decomposition})
    _write_json(root / "results" / "conditions-manifest.json",
                {"schema_version": "1.0", "generated_at": "2026-08-01T00:00:00Z",
                 "generator_version": "0.0.1", "conditions": []})
    _write_json(root / "results" / "passes-manifest.json",
                {"schema_version": "1.0", "generated_at": "2026-08-01T00:00:00Z",
                 "generator_version": "0.0.1", "passes": passes})
    _write_json(
        root / "results" / "sensitivity-mde-2026-08-28" / "sensitivity.json",
        {"mde_table": [{
            "instrument": "fixture 340-tile tile-swap (20 m)",
            "n_tiles": 340, "n_comparisons": 3,
            "null_sd_median": 0.02, "null_sd_range": [0.01, 0.03],
            "mde_50pc_power": 0.039, "mde_80pc_power": 0.056,
            "source": "results/fixture/analysis.json",
        }]},
    )
    return root


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV into a list of row dicts."""
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


# --------------------------------------------------------------------------- #
# The flatten
# --------------------------------------------------------------------------- #


class TestFlattenEndToEnd:
    """``build_uplift_supplement.main`` over the fixture corpus."""

    def test_writes_every_table(self, corpus: Path, tmp_path: Path) -> None:
        """All six artefacts land, and the exit code is success."""
        out = tmp_path / "out"
        assert flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)]) == 0
        for name in ("conditions.csv", "conditions-by-buffer.csv", "strata.csv",
                     "transfer-pairs.csv", "column-spec.json", "build-report.md",
                     "notation-extension-proposal.md"):
            assert (out / name).exists(), name

    def test_one_row_per_registered_spec(self, corpus: Path, tmp_path: Path) -> None:
        """Nine specs in, nine rows out — no condition silently dropped."""
        out = tmp_path / "out"
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        rows = _read_csv(out / "conditions.csv")
        assert len(rows) == 9
        assert {r["condition_id"] for r in rows} >= {
            "alpha::consensus-2of3", "alpha::verified-2of3",
            "beta::consensus-2of3", "beta::verified-2of3",
            "gamma::consensus-2of3", "gamma::verified-2of3",
        }

    def test_every_row_carries_a_stratum_id(self, corpus: Path, tmp_path: Path) -> None:
        """The key is mandatory; an empty one would slip past the guard."""
        out = tmp_path / "out"
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        for row in _read_csv(out / "conditions.csv"):
            assert row["stratum_id"], row["condition_id"]
            assert row["stratum_id"].count("|") == 3

    def test_strata_are_what_the_fixture_declares(
        self, corpus: Path, tmp_path: Path
    ) -> None:
        """alpha and beta share a stratum; gamma sits in its own."""
        out = tmp_path / "out"
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        strata = {r["condition_id"]: r["stratum_id"]
                  for r in _read_csv(out / "conditions.csv")}
        assert strata["alpha::consensus-2of3"] == "4-map-gs|curator|20m|era-1-340"
        assert strata["beta::consensus-2of3"] == strata["alpha::consensus-2of3"]
        assert strata["gamma::consensus-2of3"] == "55-map|student|50m|55maps-8541"

    def test_column_contract_is_exact(self, corpus: Path, tmp_path: Path) -> None:
        """The written header matches the published contract, in order.

        Pinned both ways: the module constant must equal the expectation, AND
        the file's header must equal it. Deleting `stratum_id` from either one
        fails here.
        """
        out = tmp_path / "out"
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        with (out / "conditions.csv").open(encoding="utf-8") as handle:
            header = tuple(next(csv.reader(handle)))
        assert CONDITION_COLUMNS == EXPECTED_CONDITION_COLUMNS
        assert header == EXPECTED_CONDITION_COLUMNS
        assert "stratum_id" in header

    def test_metrics_come_from_the_evaluation_artefacts(
        self, corpus: Path, tmp_path: Path
    ) -> None:
        """With an empty conditions manifest, every row falls back to its eval."""
        out = tmp_path / "out"
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        rows = {r["condition_id"]: r for r in _read_csv(out / "conditions.csv")}
        assert rows["alpha::verified-2of3"]["metrics_source"] == "evaluation-json"
        assert rows["alpha::verified-2of3"]["F1"] == "0.75"
        assert rows["alpha::consensus-2of3"]["F1"] == "0.6"

    def test_passes_are_consumed_in_pass_n_order(
        self, corpus: Path, tmp_path: Path
    ) -> None:
        """The first-N rule depends on the loader sorting the pass bucket.

        The fixture writes each pool's manifest rows as pass 3, 1, 2 with costs
        3.0, 1.0, 2.0. K is 3 either way, but an unsorted bucket would consume
        pass 3 first — so the ordering is pinned through a value that changes
        with it.
        """
        out = tmp_path / "out"
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        row = next(r for r in _read_csv(out / "conditions.csv")
                   if r["condition_id"] == "alpha::consensus-2of3")
        assert row["K"] == "3"
        assert float(row["cost_usd"]) == pytest.approx(6.0)

    def test_original_publication_date_is_stable_across_rebuilds(
        self, corpus: Path, tmp_path: Path
    ) -> None:
        """The revision-policy baseline must not move when the build re-runs."""
        out = tmp_path / "out"
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        first = (out / "build-report.md").read_text(encoding="utf-8")
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        second = (out / "build-report.md").read_text(encoding="utf-8")

        def _changelog(text: str) -> str:
            return text.split("## Changelog", 1)[1]

        assert _changelog(first) == _changelog(second)
        assert "Original publication" in _changelog(first)

    def test_reference_path_is_the_in_repo_anchor(
        self, corpus: Path, tmp_path: Path
    ) -> None:
        """Never a machine-local replay copy: the column is a re-verify anchor."""
        out = tmp_path / "out"
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        for row in _read_csv(out / "conditions.csv"):
            assert row["reference_path"].startswith("inputs/vectors/references/")


# --------------------------------------------------------------------------- #
# The worklist builders refuse to score
# --------------------------------------------------------------------------- #


class TestExecuteIsRefused:
    """Neither worklist builder will run a scoring job."""

    @pytest.mark.parametrize("entry_point", [k1_main, pairing_main])
    def test_execute_returns_two_and_writes_nothing(
        self, entry_point: Any, corpus: Path, tmp_path: Path
    ) -> None:
        """``--execute`` exits 2 and leaves the output directory untouched."""
        out = tmp_path / "out"
        code = entry_point(
            ["--repo-root", str(corpus), "--out-dir", str(out), "--execute"]
        )
        assert code == 2
        assert not out.exists()


# --------------------------------------------------------------------------- #
# K = 1 gap-fill
# --------------------------------------------------------------------------- #


class TestK1GapFillEndToEnd:
    """``build_k1_gapfill_worklist.main`` over the fixture corpus."""

    @pytest.fixture
    def rows(self, corpus: Path, tmp_path: Path) -> dict[str, dict[str, str]]:
        """Build the worklist and return its rows by source condition."""
        out = tmp_path / "out"
        assert k1_main(["--repo-root", str(corpus), "--out-dir", str(out)]) == 0
        return {r["source_condition"]: r
                for r in _read_csv(out / "k1-gapfill-worklist.csv")}

    def test_covers_every_multi_pass_cell(self, rows: dict) -> None:
        """All nine N = 3 cells need an anchor; none is skipped."""
        assert len(rows) == 9

    def test_ready_jobs_point_at_the_first_committed_pass(self, rows: dict) -> None:
        """The N = 1 rung scores run_1, per the preregistered first-N rule."""
        row = rows["alpha::consensus-2of3"]
        assert row["status"] == "ready"
        assert row["detections_path"].endswith("run_1/detections_text-alpha_run01.geojson")
        assert "evaluate_detections.py" in row["command"]

    def test_floor_one_stage_stays_derivable(self, rows: dict) -> None:
        """alpha's verifier saw vote 1, so a K = 1 PV anchor IS derivable."""
        row = rows["alpha::verified-2of3"]
        assert row["k1_with_verifier"] == "derivable"
        assert row["verifier_min_vote_seen"] == "1"
        assert row["verifier_crop_manifest"] == "outputs/alpha/crops/candidate_manifest.json"

    def test_floor_above_one_stage_is_blocked_and_disclosed(self, rows: dict) -> None:
        """beta's verifier never saw a singleton, so the PV anchor is blocked.

        The negative direction of the same rule. Without this the disclosure
        could be hard-coded to "blocked" and still pass.
        """
        row = rows["beta::verified-2of3"]
        assert row["k1_with_verifier"] == "blocked"
        assert row["verifier_min_vote_seen"] == "2"
        assert "vote_count >= 2" in row["k1_with_verifier_reason"]
        assert "DISCLOSED, not approximated" in row["k1_with_verifier_reason"]

    def test_consensus_cells_are_not_asked_about_the_pv_anchor(
        self, rows: dict
    ) -> None:
        """A cell with no verifier has no with-verifier verdict to give."""
        assert rows["alpha::consensus-2of3"]["k1_with_verifier"] == "not-applicable"

    def test_verifier_evidence_is_a_repo_relative_path(self, rows: dict) -> None:
        """A published anchor must not bake in a machine-local absolute path."""
        for row in rows.values():
            assert not (row["verifier_crop_manifest"] or "").startswith("/")

    def test_disclosure_reports_a_nonzero_skipped_count(
        self, corpus: Path, tmp_path: Path
    ) -> None:
        """Exclusions are published: a dropped manifest can move a floor.

        Every fixture run carries a smoke rehearsal, so the count is NONZERO —
        a test that passed on "0 manifests were excluded" would not notice the
        exclusion machinery being removed.
        """
        out = tmp_path / "out"
        k1_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        text = (out / "k1-gapfill-disclosure.md").read_text(encoding="utf-8")
        assert "candidate manifest(s) were excluded" in text
        assert "**0 candidate manifest(s) were excluded" not in text
        assert "smoke-test tree" in text
        assert "_smoke" in text

    def test_smoke_rehearsal_does_not_lower_a_measured_floor(
        self, rows: dict
    ) -> None:
        """beta's smoke tree holds a vote-1 candidate; its floor stays 2.

        This is why the exclusion exists: without it the rehearsal would drag
        the run to floor 1 and flip a blocked verdict to derivable.
        """
        assert rows["beta::verified-2of3"]["verifier_min_vote_seen"] == "2"
        assert rows["beta::verified-2of3"]["k1_with_verifier"] == "blocked"

    def test_multi_stage_run_matches_each_cell_to_its_own_stage(
        self, rows: dict
    ) -> None:
        """The `delta` run has four stages; each cell must find its own.

        Text and image pools verified at different floors, so a crossing shows
        up as a wrong verdict rather than merely a wrong citation.
        """
        text_cell = rows["delta::text-delta-union-2of3"]
        image_cell = rows["delta::image-delta-union-2of3"]
        assert text_cell["verifier_crop_manifest"] == (
            "outputs/delta/verifier/text-delta/crops/candidate_manifest.json"
        )
        assert text_cell["verifier_min_vote_seen"] == "1"
        assert text_cell["k1_with_verifier"] == "derivable"
        assert image_cell["verifier_crop_manifest"] == (
            "outputs/delta/verifier/image-delta/crops/candidate_manifest.json"
        )
        assert image_cell["verifier_min_vote_seen"] == "2"
        assert image_cell["k1_with_verifier"] == "blocked"

    def test_union_shell_narrowing_drops_the_wrong_rung(self, rows: dict) -> None:
        """delta has a union_k5 stage; an N = 3 cell must not land on it."""
        row = rows["delta::text-delta-union-2of3"]
        assert "crops_k5" not in row["verifier_crop_manifest"]

    def test_consensus_shell_separates_stages_of_one_pool(
        self, rows: dict
    ) -> None:
        """text-delta has both a union stage and a ge2of3 stage."""
        row = rows["delta::text-delta-ge2of3"]
        assert row["verifier_crop_manifest"].endswith(
            "verifier/text-delta/crops_ge2of3/candidate_manifest.json"
        )
        assert row["verifier_floor_basis"].startswith("matched-consensus-shell")
        assert row["verifier_min_vote_seen"] == "2"

    def test_cells_without_a_verifier_cite_nothing(self, rows: dict) -> None:
        """A consensus cell has no verifier stage, so it can cite none.

        Forty-one such citations were published, every one pointing at another
        lineage's stage — a false evidence path even where the floor happened
        to be right.
        """
        for row in rows.values():
            if row["verified"] == "true":
                continue
            assert row["verifier_crop_manifest"] == "", row["source_condition"]
            assert row["verifier_min_vote_seen"] == "", row["source_condition"]
            assert row["verifier_floor_basis"] == "not-applicable"

    def test_pool_subtree_stages_win_over_run_level_stages(
        self, corpus: Path, tmp_path: Path
    ) -> None:
        """End-to-end: a pool with its own stages must cite from its own tree.

        The `delta` run's `text-delta` pool verifies under
        `verifier/text-delta/`, and a decoy run-level stage carrying the same
        modality and shell sits alongside it. Token scoring alone cannot
        separate them.
        """
        decoy = corpus / "outputs" / "delta" / "verified" / "text-2of3"
        _write_json(decoy / "candidate_manifest.json",
                    _candidate_manifest("text-1of3.geojson", [2, 3]))
        out = tmp_path / "out"
        k1_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        rows = {r["source_condition"]: r
                for r in _read_csv(out / "k1-gapfill-worklist.csv")}
        row = rows["delta::text-delta-union-2of3"]
        assert row["verifier_crop_manifest"].startswith(
            "outputs/delta/verifier/text-delta/"
        )
        assert "verified/text-2of3" not in row["verifier_crop_manifest"]

    def test_no_citation_crosses_modality(self, rows: dict) -> None:
        """A text cell must never cite an image stage's manifest, or vice versa.

        The failure this pins is a false EVIDENCE path — the floor can be
        coincidentally right while the manifest belongs to another condition.
        """
        for row in rows.values():
            manifest = row["verifier_crop_manifest"]
            if not manifest:
                continue
            pool = row["proposer_pool"]
            if pool.startswith("image"):
                assert "/text-" not in manifest, row["source_condition"]
            if pool.startswith("text"):
                assert "/image-" not in manifest, row["source_condition"]


# --------------------------------------------------------------------------- #
# Pairing and uplift
# --------------------------------------------------------------------------- #


class TestPairingAndUpliftEndToEnd:
    """The pairing worklist and the uplift column it feeds."""

    @pytest.fixture
    def built(self, corpus: Path, tmp_path: Path) -> Path:
        """Run the flatten and the pairing builder; return the output dir."""
        out = tmp_path / "out"
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(out)])
        assert pairing_main(["--repo-root", str(corpus), "--out-dir", str(out)]) == 0
        return out

    def test_each_verified_cell_gets_a_row(self, built: Path) -> None:
        """Six verified cells, six pairing rows."""
        assert len(_read_csv(built / "verifier-pairing-worklist.csv")) == 6

    def test_twin_is_the_registered_consensus_cell(self, built: Path) -> None:
        """The pre-verifier twin is already scored, so nothing needs running."""
        rows = {r["verified_condition_id"]: r
                for r in _read_csv(built / "verifier-pairing-worklist.csv")}
        row = rows["alpha::verified-2of3"]
        assert row["status"] == "already-registered"
        assert row["unverified_condition_id"] == "alpha::consensus-2of3"
        assert row["pairing_basis"] == "registered"

    def test_both_strata_are_carried_and_derived_independently(
        self, built: Path
    ) -> None:
        """The guard needs two ids; a registered twin's comes from its own cell."""
        row = next(r for r in _read_csv(built / "verifier-pairing-worklist.csv")
                   if r["verified_condition_id"] == "alpha::verified-2of3")
        assert row["verified_stratum_id"] == "4-map-gs|curator|20m|era-1-340"
        assert row["unverified_stratum_id"] == "4-map-gs|curator|20m|era-1-340"
        assert row["unverified_stratum_basis"] == "derived-from-twin-cell"

    def test_uplift_sign_and_magnitude(self, corpus: Path, built: Path) -> None:
        """verified minus unverified: 0.75 - 0.60 = +0.15 on a known pair."""
        assert uplift_main(
            ["--repo-root", str(corpus), "--out-dir", str(built)]
        ) == 0
        rows = {r["pair_id"]: r for r in _read_csv(built / "verifier-uplift.csv")}
        row = rows["pair::alpha::verified-2of3"]
        assert row["status"] == "computed"
        assert float(row["verified_value"]) == pytest.approx(0.75)
        assert float(row["unverified_value"]) == pytest.approx(0.60)
        assert float(row["uplift"]) == pytest.approx(0.15)

    def test_uplift_is_negative_when_the_verifier_costs_f1(
        self, corpus: Path, built: Path
    ) -> None:
        """The sign is real arithmetic, not a hard-coded direction."""
        evaluation = corpus / "results" / "alpha" / "verified" / "evaluation.json"
        document = json.loads(evaluation.read_text(encoding="utf-8"))
        document["summary"]["buffers"][0]["f1"] = 0.50
        evaluation.write_text(json.dumps(document), encoding="utf-8")
        flatten_main(["--repo-root", str(corpus), "--out-dir", str(built)])
        uplift_main(["--repo-root", str(corpus), "--out-dir", str(built)])
        row = next(r for r in _read_csv(built / "verifier-uplift.csv")
                   if r["pair_id"] == "pair::alpha::verified-2of3")
        assert float(row["uplift"]) == pytest.approx(-0.10)

    def test_cross_stratum_pair_raises(self, corpus: Path, built: Path) -> None:
        """A pair whose two sides sit in different strata must STOP the build.

        This is the test the guard failed before the fix: the worklist carried
        one stratum id and the computer passed it to itself, so no input could
        make the check fire. Corrupting one side of a real worklist row is now
        detected.
        """
        worklist = built / "verifier-pairing-worklist.csv"
        rows = _read_csv(worklist)
        for row in rows:
            if row["verified_condition_id"] == "alpha::verified-2of3":
                row["unverified_stratum_id"] = "55-map|student|50m|55maps-8541"
        with worklist.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

        with pytest.raises(CrossStratumAggregationError) as excinfo:
            compute_uplift(corpus, built, "F1")
        message = str(excinfo.value)
        assert "alpha::verified-2of3" in message
        assert "4-map-gs|curator|20m|era-1-340" in message
        assert "55-map|student|50m|55maps-8541" in message
