"""Tier-1 tests for the uplift-supplement dataset builders.

Covers the three mechanisms the card's heterogeneity design rests on:

* **the refusal** — a derived aggregate spanning strata must raise rather than
  produce a number (``refuse_cross_stratum``);
* **stratum-key construction** — the composite key must build, render, and
  round-trip, and must reject malformed ids (``StratumKey``);
* **notation-key validation** — a column the canonical key does not sanction and
  the extension table does not declare must fail loudly (``NotationKey``,
  ``write_csv``).

Plus the resolvers those three lean on: geometry, reference, and basis, each of
which decides a stratum component or a factor column from committed evidence.

All tests are hermetic: synthetic fixtures and ``tmp_path``, except the two that
read the committed notation key itself (which is the authority under test).

Created: 2026-08-29 (uplift-supplement card, Build order steps 1-3)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from scripts.compute_verifier_uplift import (
    _metric_from_eval,
    _metric_from_summary,
    _value_for,
)
from scripts.lib_uplift_supplement import (
    COLUMN_EXTENSIONS,
    NOTATION_KEY_PATH,
    REFERENCE_N_MOUNDS,
    REFERENCE_PATH,
    CrossStratumAggregationError,
    NotationKey,
    StratumKey,
    UnknownColumnError,
    VerifierManifest,
    collect_verifier_manifests,
    match_verifier_manifest,
    read_scoring_recipe,
    refuse_cross_stratum,
    resolve_basis,
    resolve_geometry,
    resolve_reference,
    write_csv,
)

pytestmark = pytest.mark.tier1

PROJECT_ROOT = Path(__file__).resolve().parents[1]

NOTATION_KEY_FIXTURE = """# Fixture key

## 6. Corpora and evaluation frames

| Frame id | Tiles | Corpus | Typical buffer |
|---|---:|---|---|
| era-1-340 | 340 | GS 4 maps | 20 m |
| stratum_id | — | Composite key | — |

## 7. Standard dataset column names

Sweep CSVs: `cell`, `N`, `prob_t`, `min_votes`, `n_detections`, `tp`, `fp`,
`fn`, `precision`, `recall`, `corrected_f1`.

Corrected-F1 evaluations (`corrected-f1.csv`): `R_m`, `precision`/`recall`/`F1`
with `_CI_lo`/`_CI_hi`, `MCC` + CI, `tile_TP`, `sensitivity`, `specificity`.

Board JSONs (`final_board_50m.json`): `label`, `basis`, `mcc`, `cost_usd`,
`n_tiles`, `null_std`.

Registry ids: conditions are `run_id::label`; passes are `run_id::pool::runN`.

## 8. Cost vocabulary

| Term | Meaning |
|---|---|
| flex | the discounted tier |
"""


@pytest.fixture
def fixture_key(tmp_path: Path) -> NotationKey:
    """Return a NotationKey parsed from a miniature stand-in document."""
    path = tmp_path / "notation-key.md"
    path.write_text(NOTATION_KEY_FIXTURE, encoding="utf-8")
    return NotationKey(path)


def _row(stratum_id: str, **extra: object) -> dict[str, object]:
    """Build a minimal dataset row carrying a stratum id."""
    return {"stratum_id": stratum_id, **extra}


# --------------------------------------------------------------------------- #
# The refusal
# --------------------------------------------------------------------------- #


class TestRefuseCrossStratum:
    """The machine-enforced half of the card's heterogeneity design."""

    def test_single_stratum_returns_its_id(self) -> None:
        """Rows from one stratum aggregate freely and name their stratum."""
        rows = [_row("4-map-gs|curator|20m|era-2-487") for _ in range(3)]
        assert refuse_cross_stratum(rows) == "4-map-gs|curator|20m|era-2-487"

    def test_spanning_strata_raises_without_transfer(self) -> None:
        """Two strata without the flag is a refusal, not a number."""
        rows = [
            _row("4-map-gs|curator|20m|era-2-487"),
            _row("55-map|standardised|50m|55maps-8541"),
        ]
        with pytest.raises(CrossStratumAggregationError) as excinfo:
            refuse_cross_stratum(rows, what="mean F1")
        message = str(excinfo.value)
        assert "mean F1" in message
        assert "2 strata" in message
        assert "transfer pair" in message

    def test_transfer_flag_licenses_and_labels_the_span(self) -> None:
        """With the flag the span is permitted and named in the return value."""
        rows = [
            _row("4-map-gs|curator|20m|era-2-487"),
            _row("55-map|standardised|50m|55maps-8541"),
        ]
        result = refuse_cross_stratum(rows, transfer=True)
        assert "4-map-gs|curator|20m|era-2-487" in result
        assert "55-map|standardised|50m|55maps-8541" in result
        assert "|+|" in result

    def test_buffer_alone_makes_a_different_stratum(self) -> None:
        """The buffer is part of the key: 20 m and 50 m do not aggregate."""
        rows = [
            _row("4-map-gs|curator|20m|era-2-487"),
            _row("4-map-gs|curator|50m|era-2-487"),
        ]
        with pytest.raises(CrossStratumAggregationError):
            refuse_cross_stratum(rows)

    def test_reference_alone_makes_a_different_stratum(self) -> None:
        """So is the reference: canonical and standardised do not aggregate."""
        rows = [
            _row("55-map|canonical|50m|55maps-8541"),
            _row("55-map|standardised|50m|55maps-8541"),
        ]
        with pytest.raises(CrossStratumAggregationError):
            refuse_cross_stratum(rows)

    def test_missing_stratum_id_raises(self) -> None:
        """A row without the mandatory key stops the aggregate."""
        rows = [_row("4-map-gs|curator|20m|era-2-487"), {"F1": 0.5}]
        with pytest.raises(CrossStratumAggregationError, match="no stratum_id"):
            refuse_cross_stratum(rows)

    def test_empty_input_raises_rather_than_returning_nothing(self) -> None:
        """An empty aggregate has no stratum, so it cannot be labelled."""
        with pytest.raises(CrossStratumAggregationError, match="no rows"):
            refuse_cross_stratum([])

    def test_empty_string_stratum_id_counts_as_missing(self) -> None:
        """An empty key is absent, not a stratum named "".

        A CSV round-trip turns a null into ``""``, so a builder that dropped
        the key would otherwise sail through the guard on every row.
        """
        rows = [_row("4-map-gs|curator|20m|era-2-487"), {"stratum_id": ""}]
        with pytest.raises(CrossStratumAggregationError, match="no stratum_id"):
            refuse_cross_stratum(rows)

    def test_all_rows_empty_string_raises(self) -> None:
        """Uniformly empty keys must not aggregate as one anonymous stratum."""
        with pytest.raises(CrossStratumAggregationError, match="no stratum_id"):
            refuse_cross_stratum([{"stratum_id": ""}, {"stratum_id": ""}])

    def test_transfer_flag_does_not_excuse_a_missing_key(self) -> None:
        """`transfer=True` licenses a span, not an unkeyed row."""
        with pytest.raises(CrossStratumAggregationError, match="no stratum_id"):
            refuse_cross_stratum([{"F1": 0.5}], transfer=True)


# --------------------------------------------------------------------------- #
# Stratum keys
# --------------------------------------------------------------------------- #


class TestStratumKey:
    """Construction, rendering, and round-tripping of the composite key."""

    def test_renders_all_four_components(self) -> None:
        """The id names corpus, reference, buffer, and frame, in that order."""
        key = StratumKey("4-map-gs", "curator", 20, "era-2-487")
        assert key.stratum_id == "4-map-gs|curator|20m|era-2-487"

    def test_round_trips_through_parse(self) -> None:
        """parse(stratum_id) reconstructs the key exactly."""
        key = StratumKey("55-map", "standardised", 50, "55maps-8541")
        assert StratumKey.parse(key.stratum_id) == key

    def test_buffer_is_an_integer_after_parsing(self) -> None:
        """The buffer survives as a number, not the '50m' token."""
        assert StratumKey.parse("55-map|student|50m|55maps-8541").buffer_m == 50

    @pytest.mark.parametrize(
        "bad",
        [
            "4-map-gs|curator|20m",
            "4-map-gs|curator|20m|era-2-487|extra",
            "",
        ],
    )
    def test_wrong_component_count_raises(self, bad: str) -> None:
        """Anything but four components is malformed."""
        with pytest.raises(ValueError, match="components"):
            StratumKey.parse(bad)

    @pytest.mark.parametrize(
        "bad",
        [
            "4-map-gs|curator|20|era-2-487",
            "4-map-gs|curator|twenty-m|era-2-487",
        ],
    )
    def test_malformed_buffer_raises(self, bad: str) -> None:
        """The buffer component must look like '20m'."""
        with pytest.raises(ValueError, match="buffer component"):
            StratumKey.parse(bad)

    def test_keys_are_hashable_and_comparable(self) -> None:
        """Frozen dataclass semantics — the key is usable as a dict key."""
        first = StratumKey("4-map-gs", "curator", 20, "era-1-340")
        second = StratumKey("4-map-gs", "curator", 20, "era-1-340")
        assert {first: 1}[second] == 1


# --------------------------------------------------------------------------- #
# Notation-key validation
# --------------------------------------------------------------------------- #


class TestNotationKeyValidation:
    """Columns must be sanctioned by the key or declared as extensions."""

    def test_harvests_backticked_column_names(self, fixture_key: NotationKey) -> None:
        """Identifiers the key writes in backticks are sanctioned."""
        for name in ("cell", "prob_t", "min_votes", "precision", "cost_usd"):
            assert name in fixture_key.sanctioned

    def test_harvests_frame_ids_and_stratum_id_from_the_section_6_table(
        self, fixture_key: NotationKey
    ) -> None:
        """The § 6 table's first column is vocabulary too, though unbackticked."""
        assert "stratum_id" in fixture_key.sanctioned
        assert "era-1-340" in fixture_key.sanctioned

    def test_expands_the_compositional_ci_naming(
        self, fixture_key: NotationKey
    ) -> None:
        """'precision/recall/F1 with _CI_lo/_CI_hi' becomes six real names."""
        for name in ("F1_CI_lo", "F1_CI_hi", "precision_CI_lo", "recall_CI_hi"):
            assert name in fixture_key.sanctioned

    def test_drops_filenames_globs_and_id_composites(
        self, fixture_key: NotationKey
    ) -> None:
        """Backticked tokens that are plainly not column names are excluded."""
        for token in ("corrected-f1.csv", "final_board_50m.json", "run_id::label"):
            assert token not in fixture_key.sanctioned

    def test_sanctioned_columns_pass(self, fixture_key: NotationKey) -> None:
        """A list drawn entirely from the key validates silently."""
        fixture_key.validate(["cell", "N", "prob_t", "F1", "MCC", "stratum_id"])

    def test_declared_extension_passes(self, fixture_key: NotationKey) -> None:
        """A column absent from the key but declared in the table is allowed."""
        assert "geometry_basis" in COLUMN_EXTENSIONS
        fixture_key.validate(["F1", "geometry_basis"])

    def test_undeclared_column_raises(self, fixture_key: NotationKey) -> None:
        """An ad-hoc name fails loudly, naming itself and the remedy."""
        with pytest.raises(UnknownColumnError) as excinfo:
            fixture_key.validate(["F1", "made_up_column"])
        message = str(excinfo.value)
        assert "made_up_column" in message
        assert "Extend the notation key" in message

    def test_error_lists_every_offender_not_just_the_first(
        self, fixture_key: NotationKey
    ) -> None:
        """One run surfaces the whole problem."""
        with pytest.raises(UnknownColumnError) as excinfo:
            fixture_key.validate(["nope_one", "nope_two", "F1"])
        message = str(excinfo.value)
        assert "nope_one" in message and "nope_two" in message
        assert "2 column(s)" in message

    def test_missing_key_file_raises_rather_than_falling_back(
        self, tmp_path: Path
    ) -> None:
        """No hard-coded vocabulary stands in for an absent authority."""
        with pytest.raises(FileNotFoundError):
            NotationKey(tmp_path / "absent.md")

    def test_key_without_sections_6_to_7_raises(self, tmp_path: Path) -> None:
        """A restructured key must be noticed, not silently half-harvested."""
        path = tmp_path / "notation-key.md"
        path.write_text("# Key\n\n## 1. Symbols\n\n`K`\n", encoding="utf-8")
        with pytest.raises(ValueError, match=r"locate §§ 6-7"):
            NotationKey(path)

    def test_committed_key_sanctions_the_columns_the_dataset_publishes(self) -> None:
        """Guard against the canonical key and the extension table drifting.

        Every column any builder writes must be sanctioned by the real
        ``docs/methodology/notation-key.md`` or declared in
        ``COLUMN_EXTENSIONS``. This test reads the committed key, so it fails if
        the key is edited in a way that strands a published column.
        """
        from scripts.build_k1_gapfill_worklist import (
            WORKLIST_COLUMNS as K1_COLUMNS,
        )
        from scripts.build_uplift_supplement import (
            CONDITION_COLUMNS,
            STRATUM_COLUMNS,
            TRANSFER_PAIR_COLUMNS,
        )
        from scripts.build_verifier_pairing_worklist import (
            WORKLIST_COLUMNS as PAIR_COLUMNS,
        )
        from scripts.compute_verifier_uplift import UPLIFT_COLUMNS

        key = NotationKey(PROJECT_ROOT / NOTATION_KEY_PATH)
        for columns in (CONDITION_COLUMNS, STRATUM_COLUMNS, TRANSFER_PAIR_COLUMNS,
                        K1_COLUMNS, PAIR_COLUMNS, UPLIFT_COLUMNS):
            key.validate(columns)

    def test_no_extension_duplicates_a_sanctioned_name(self) -> None:
        """An extension that shadows the key is a sign the key already has it."""
        key = NotationKey(PROJECT_ROOT / NOTATION_KEY_PATH)
        overlap = sorted(set(COLUMN_EXTENSIONS) & key.sanctioned)
        assert overlap == [], (
            f"these columns are declared as extensions but the canonical key "
            f"already sanctions them: {overlap}"
        )

    def test_every_extension_states_its_warrant(self) -> None:
        """A declared extension without a rationale is an undocumented column."""
        for name, extension in COLUMN_EXTENSIONS.items():
            assert extension.column == name
            assert extension.derives_from.strip()
            assert len(extension.rationale.strip()) > 20


class TestWriteCsvValidates:
    """The write path validates before it opens a file."""

    def test_valid_columns_are_written(
        self, tmp_path: Path, fixture_key: NotationKey
    ) -> None:
        """A sanctioned header round-trips through the writer."""
        destination = tmp_path / "out.csv"
        write_csv(destination, [{"F1": 0.5, "stratum_id": "a|b|20m|c"}],
                  ["stratum_id", "F1"], fixture_key)
        with destination.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        assert rows == [{"stratum_id": "a|b|20m|c", "F1": "0.5"}]

    def test_unknown_column_leaves_no_file_behind(
        self, tmp_path: Path, fixture_key: NotationKey
    ) -> None:
        """Validation runs first, so a rejected write is not half-done."""
        destination = tmp_path / "out.csv"
        with pytest.raises(UnknownColumnError):
            write_csv(destination, [{"F1": 0.5}], ["F1", "bogus"], fixture_key)
        assert not destination.exists()

    def test_none_becomes_empty_and_bools_become_lower_case(
        self, tmp_path: Path, fixture_key: NotationKey
    ) -> None:
        """Missing is empty (never zero); booleans read the same everywhere."""
        destination = tmp_path / "out.csv"
        write_csv(destination, [{"F1": None, "basis": True}],
                  ["F1", "basis"], fixture_key)
        with destination.open(encoding="utf-8") as handle:
            row = next(csv.DictReader(handle))
        assert row == {"F1": "", "basis": "true"}


# --------------------------------------------------------------------------- #
# Resolvers feeding the stratum key and the factor columns
# --------------------------------------------------------------------------- #


class TestResolveReference:
    """The reference component of the stratum key."""

    def test_evaluation_ground_truth_wins(self) -> None:
        """What the evaluation consumed outranks label and run facts."""
        meta = {"input_files": {
            "ground_truth": "inputs/vectors/references/best-available-gt-55maps.geojson"
        }}
        resolved = resolve_reference(meta, "verified-k4", "student")
        assert resolved.term == "standardised"
        assert resolved.basis == "eval-ground-truth"
        assert resolved.path.endswith("best-available-gt-55maps.geojson")
        assert resolved.consumed_path is None

    def test_frozen_replay_copies_resolve_by_basename(self) -> None:
        """Replays under a scratch 'frozen' tree name the same reference file."""
        consumed = ("/home/x/cc-scratch/tmp/tmpabc/frozen/inputs/vectors/"
                    "references/mounds-reference.geojson")
        resolved = resolve_reference(
            {"cli_args": {"ground_truth": consumed}}, "consensus-4of5", "curator"
        )
        assert resolved.term == "curator"
        assert resolved.basis == "eval-ground-truth"

    def test_replay_copy_never_becomes_the_published_anchor(self) -> None:
        """`reference_path` is documented as re-verifiable, so it must resolve.

        Nine committed evaluations ran against a frozen scratch copy that no
        longer exists. Publishing that path as the anchor hands a reader a dead
        link; the canonical in-repo file is the anchor and the consumed path is
        preserved separately.
        """
        consumed = ("/home/x/cc-scratch/tmp/tmpabc/frozen/inputs/vectors/"
                    "references/mounds-reference.geojson")
        resolved = resolve_reference(
            {"cli_args": {"ground_truth": consumed}}, "consensus-4of5", "curator"
        )
        assert resolved.path == "inputs/vectors/references/mounds-reference.geojson"
        assert resolved.consumed_path == consumed

    @pytest.mark.parametrize(
        ("label", "expected"),
        [("verified-k3-canonical-gt", "canonical"),
         ("verified-k4-standardised-gt", "standardised")],
    )
    def test_label_suffix_is_the_fallback(self, label: str, expected: str) -> None:
        """The explicit suffixes resolve when the evaluation records nothing."""
        resolved = resolve_reference(None, label, "combined")
        assert (resolved.term, resolved.basis) == (expected, "label-suffix")

    @pytest.mark.parametrize(
        "label", ["greedy-canonical", "wbf-canonical", "canonical-first",
                  "image-canonical", "text-canonical"],
    )
    def test_config_labels_using_the_word_canonical_are_not_caught(
        self, label: str
    ) -> None:
        """These name a CONFIG, not a reference; the run's facts must win."""
        resolved = resolve_reference(None, label, "curator")
        assert (resolved.term, resolved.basis) == ("curator", "run-facts")

    def test_combined_schema_class_maps_to_canonical(self) -> None:
        """The manifest's 'combined' is the notation key's canonical extended GT."""
        resolved = resolve_reference(None, "verified", "combined")
        assert (resolved.term, resolved.basis) == ("canonical", "run-facts")

    def test_unresolvable_reference_is_none_not_a_guess(self) -> None:
        """No rule firing yields None and says so."""
        resolved = resolve_reference(None, "verified", None)
        assert resolved.term is None
        assert resolved.basis == "unresolved"

    @pytest.mark.parametrize("unknown", ["lidar", "combined-v2", "reviewer"])
    def test_unrecognised_run_reference_does_not_become_a_stratum_component(
        self, unknown: str
    ) -> None:
        """An unknown vocabulary term must surface, not be welded into a key.

        Documented behaviour: a `gt_reference` the § 4 vocabulary does not
        recognise resolves to `None` with basis `unresolved`. The flatten then
        writes `unknown` into the stratum id, which is legible as a gap. Passing
        the raw value through would mint a stratum nobody can interpret and that
        no MDE or reference count could ever join to.
        """
        resolved = resolve_reference(None, "verified", unknown)
        assert resolved.term is None
        assert resolved.basis == "unresolved"
        assert resolved.path is None

    def test_every_reference_term_has_a_committed_mound_count(self) -> None:
        """The strata table's n_refs is defined for every vocabulary term."""
        from scripts.lib_uplift_supplement import REFERENCE_BY_FILENAME

        assert set(REFERENCE_BY_FILENAME.values()) == set(REFERENCE_N_MOUNDS)


class TestResolveGeometry:
    """Tile size, overlap, and stride, each with the rule that produced it."""

    def test_pool_name_encoding_wins(self) -> None:
        """The stride and deployment pools carry the geometry in their name."""
        result = resolve_geometry("g384_ov192_55map", "some-label", 512)
        assert result["geometry"] == "g384_ov192"
        assert result["tile_px"] == 384
        assert result["overlap_px"] == 192
        assert result["stride_px"] == 192
        assert result["geometry_basis"] == "pool-name"

    def test_label_encoding_is_used_when_the_pool_is_generic(self) -> None:
        """The grid campaign's four geometries share one pool name."""
        result = resolve_geometry("brief-text", "g512-ov064-k10-c1-k8", 512)
        assert result["geometry"] == "g512_ov064"
        assert result["geometry_basis"] == "label"

    def test_overlap_percentage_labels_convert_against_the_recorded_tile_size(
        self,
    ) -> None:
        """H13's arms record a percentage; 12.5 % of 512 px is 64 px (stride 448)."""
        result = resolve_geometry("armb", "arm-a-overlap-12-5", 512)
        assert result["overlap_px"] == 64
        assert result["stride_px"] == 448
        assert result["geometry_basis"] == "label-overlap-percent"

    def test_tile_size_only_leaves_overlap_null(self) -> None:
        """Overlap is not machine-recorded for the pre-geometry runs."""
        result = resolve_geometry("detect_brief-text", "consensus-4of5", 384)
        assert result["tile_px"] == 384
        assert result["overlap_px"] is None
        assert result["geometry"] is None
        assert result["geometry_basis"] == "run-facts-tile-size"

    def test_nothing_recorded_is_unresolved(self) -> None:
        """No tile size and no encoding yields an explicit 'unresolved'."""
        result = resolve_geometry("brief-text", "consensus-4of5", None)
        assert result["geometry_basis"] == "unresolved"
        assert result["tile_px"] is None


class TestResolveBasis:
    """The basis vocabulary (notation key § 3) as encoded in labels."""

    @pytest.mark.parametrize(
        ("label", "expected"),
        [
            ("g384-ov128-55map-verified-carried-p0.15-k8", "carried"),
            ("g384-ov128-55map-n3-carried-posthoc-p0.15-k3", "carried (post-hoc)"),
            ("g384-ov192-55map-n5-oracle-p0.20-k5", "oracle"),
        ],
    )
    def test_encoded_terms_are_recovered(self, label: str, expected: str) -> None:
        """Labels that state their basis resolve to the § 3 term."""
        assert resolve_basis(label) == expected

    def test_posthoc_is_tested_before_plain_carried(self) -> None:
        """Rule order matters: 'carried-posthoc' must not read as 'carried'."""
        assert resolve_basis("x-carried-posthoc-y") == "carried (post-hoc)"

    def test_unencoded_label_returns_none(self) -> None:
        """as-shipped and comparability are editorial, not in label text."""
        assert resolve_basis("consensus-4of5") is None


# --------------------------------------------------------------------------- #
# Scoring-recipe recovery
# --------------------------------------------------------------------------- #


class TestReadScoringRecipe:
    """Recovering how a committed evaluation was produced."""

    def test_direct_cli_args_shape(self, tmp_path: Path) -> None:
        """An evaluate_detections artefact yields its own invocation."""
        document = {
            "summary": {"buffers": [{"buffer_metres": 20}, {"buffer_metres": 50}]},
            "_metadata": {
                "cli_args": {
                    "buffers": [20, 50], "bootstrap": 10000, "seed": 42,
                    "ground_truth": "inputs/vectors/references/mounds-reference.geojson",
                    "bounds": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
                },
                "bootstrap": {"n_iterations": 10000, "seed": 42},
            },
        }
        recipe, problem = read_scoring_recipe(tmp_path, "results/x/evaluation.json",
                                              document)
        assert problem is None
        assert recipe.engine == "evaluate_detections"
        assert recipe.buffers == (20, 50)
        assert recipe.bootstrap == 10000 and recipe.seed == 42
        assert recipe.ground_truth.endswith("mounds-reference.geojson")
        assert recipe.recovered_from == "results/x/evaluation.json"

    def test_seed_zero_survives(self, tmp_path: Path) -> None:
        """A recorded seed of 0 must not be replaced by the project default.

        An `or` chain treats 0 as absent, which silently reruns a different
        experiment. The value is checked against None, so 0 comes through.
        """
        document = {
            "summary": {"buffers": [{"buffer_metres": 20}]},
            "_metadata": {"cli_args": {"seed": 0, "bootstrap": 0, "buffers": [20]}},
        }
        recipe, _ = read_scoring_recipe(tmp_path, None, document)
        assert recipe.seed == 0
        assert recipe.bootstrap == 0

    def test_adapted_summary_shape(self, tmp_path: Path) -> None:
        """An adapter's output is followed one hop to the engine summary."""
        summary = tmp_path / "results" / "x" / "summary.json"
        summary.parent.mkdir(parents=True)
        summary.write_text(json.dumps({"metadata": {
            "seed": 42, "bootstrap_n": 10000,
            "input_paths": {
                "student_gt": "/somewhere/else/inputs/vectors/references/"
                              "student-mounds-55maps-reviewed.geojson",
                "bounds": "/somewhere/else/inputs/vectors/bounds/384/"
                          "55maps_evaluation_bounds.geojson",
                "review_today": "/somewhere/else/results/canon/review.csv",
            },
        }}), encoding="utf-8")
        document = {
            "summary": {"buffers": [{"buffer_metres": 50}]},
            "_metadata": {"source": "results/x/summary.json"},
        }
        recipe, problem = read_scoring_recipe(tmp_path, "results/x/evaluation.json",
                                              document)
        assert problem is None
        assert recipe.engine == "corrected_f1_multi_buffer"
        assert recipe.bootstrap == 10000 and recipe.seed == 42
        assert recipe.extra["review_today"] == "results/canon/review.csv"

    def test_absolute_paths_are_re_relativised_from_any_checkout(
        self, tmp_path: Path
    ) -> None:
        """The anchor is the project directory segment, not the repo's name.

        Splitting on the repository DIRECTORY NAME works in the main checkout
        and fails in a worktree, whose directory is named for the branch — the
        defect fixed in 59e688185. `tmp_path` here is named nothing like the
        repo, which is exactly the condition that used to break it.
        """
        summary = tmp_path / "summary.json"
        summary.write_text(json.dumps({"metadata": {"input_paths": {
            "student_gt": "/home/someone/Code/anything/inputs/vectors/"
                          "references/student-mounds-55maps-reviewed.geojson",
            "bounds": "/home/someone/Code/anything/inputs/vectors/bounds/"
                      "384/55maps_evaluation_bounds.geojson",
        }}}), encoding="utf-8")
        document = {"summary": {"buffers": []},
                    "_metadata": {"source_summary": "summary.json"}}
        recipe, _ = read_scoring_recipe(tmp_path, None, document)
        assert recipe.ground_truth == (
            "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
        )
        assert recipe.bounds == (
            "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
        )

    def test_missing_document_is_reported_not_guessed(self, tmp_path: Path) -> None:
        """No artefact, no recipe — and a reason a reader can act on."""
        recipe, problem = read_scoring_recipe(tmp_path, None, None)
        assert recipe is None
        assert "no readable evaluation artefact" in problem

    def test_no_recipe_anywhere_is_reported(self, tmp_path: Path) -> None:
        """An evaluation with neither CLI args nor a summary pointer blocks."""
        recipe, problem = read_scoring_recipe(
            tmp_path, None, {"summary": {"buffers": []}, "_metadata": {}}
        )
        assert recipe is None
        assert "cannot be reproduced" in problem

    def test_named_summary_missing_on_disk_is_reported(self, tmp_path: Path) -> None:
        """A dangling pointer names the file it could not find."""
        recipe, problem = read_scoring_recipe(
            tmp_path, None,
            {"summary": {"buffers": []}, "_metadata": {"source": "nope.json"}},
        )
        assert recipe is None
        assert "nope.json" in problem


# --------------------------------------------------------------------------- #
# Metric lifting for the uplift column
# --------------------------------------------------------------------------- #


class TestMetricFromEval:
    """Lifting one metric at one buffer out of an evaluation document."""

    @staticmethod
    def _document(mcc: object) -> dict:
        """Build a document whose tile MCC takes the given shape."""
        return {"summary": {
            "buffers": [
                {"buffer_metres": 20, "f1": 0.8, "precision": 0.7, "recall": 0.9},
                {"buffer_metres": 50, "f1": 0.85, "precision": 0.75, "recall": 0.95},
            ],
            "tile_classification": {"mcc": mcc},
        }}

    @pytest.mark.parametrize(
        ("metric", "expected"), [("F1", 0.8), ("precision", 0.7), ("recall", 0.9)]
    )
    def test_buffer_metrics_are_read_at_the_requested_buffer(
        self, metric: str, expected: float
    ) -> None:
        """The buffer selects the row; 20 m and 50 m are different numbers."""
        assert _metric_from_eval(self._document(0.5), metric, 20) == expected

    def test_a_different_buffer_gives_a_different_value(self) -> None:
        """Guards against the reader ignoring its buffer argument."""
        assert _metric_from_eval(self._document(0.5), "F1", 50) == 0.85

    def test_absent_buffer_returns_none(self) -> None:
        """A buffer the evaluation never reported is missing, not zero."""
        assert _metric_from_eval(self._document(0.5), "F1", 999) is None

    def test_scalar_mcc(self) -> None:
        """The common shape: a bare number."""
        assert _metric_from_eval(self._document(0.42), "MCC", 20) == 0.42

    def test_dict_mcc_unwraps_its_point_estimate(self) -> None:
        """Some evaluations wrap MCC with its CI; the point estimate is wanted."""
        wrapped = {"point": 0.42, "ci": [0.3, 0.5], "n_runs": 5}
        assert _metric_from_eval(self._document(wrapped), "MCC", 20) == 0.42

    def test_null_mcc_stays_none(self) -> None:
        """An undefined MCC is null, never 0.0 (erratum E81)."""
        assert _metric_from_eval(self._document(None), "MCC", 20) is None

    def test_mcc_ignores_the_buffer(self) -> None:
        """Tile MCC is buffer-agnostic, so both buffers give the same value."""
        document = self._document(0.42)
        assert (_metric_from_eval(document, "MCC", 20)
                == _metric_from_eval(document, "MCC", 50))


class TestMetricFromSummary:
    """Lifting a metric out of a corrected-F1 engine ``summary.json``.

    The two engines write different files: ``evaluate_detections.py`` writes
    ``evaluation.json``, ``compute_corrected_f1_multi_buffer.py`` writes
    ``summary.json``. Reading only the first left every corrected-F1 twin
    scored on sapphire stuck at ``pending`` with nothing to say why.
    """

    @staticmethod
    def _document() -> dict:
        """Build a two-buffer corrected-F1 summary."""
        return {"results": [
            {"R_m": 20, "F1": 0.66, "precision": 0.68, "recall": 0.64,
             "tile_classification": {"mcc": 0.67}},
            {"R_m": 50, "F1": 0.83, "precision": 0.89, "recall": 0.77,
             "tile_classification": {"mcc": 0.69}},
        ]}

    @pytest.mark.parametrize(
        ("metric", "buffer_m", "expected"),
        [("F1", 20, 0.66), ("F1", 50, 0.83), ("precision", 20, 0.68),
         ("recall", 50, 0.77), ("MCC", 20, 0.67), ("MCC", 50, 0.69)],
    )
    def test_reads_each_metric_at_each_buffer(
        self, metric: str, buffer_m: int, expected: float
    ) -> None:
        """The capitalised corrected-F1 field names map to the shared vocabulary."""
        assert _metric_from_summary(self._document(), metric, buffer_m) == expected

    def test_absent_buffer_is_none(self) -> None:
        """A buffer the engine did not report is missing, not zero."""
        assert _metric_from_summary(self._document(), "F1", 999) is None

    def test_empty_document_is_none(self) -> None:
        """A summary with no results yields nothing rather than raising."""
        assert _metric_from_summary({}, "F1", 20) is None


class TestValueFor:
    """Resolving one side of a pair to a metric value."""

    def test_prefers_the_flatten(self, tmp_path: Path) -> None:
        """A registered condition's value comes from conditions.csv."""
        conditions = {"a::b": {"F1": "0.61", "MCC": "0.4"}}
        value, source = _value_for(tmp_path, conditions, "a::b", None, "F1", 20)
        assert value == pytest.approx(0.61)
        assert source == "conditions.csv"

    def test_falls_back_to_a_freshly_scored_evaluation(self, tmp_path: Path) -> None:
        """A twin scored from the worklist has no row yet, but has an artefact."""
        out = tmp_path / "job"
        out.mkdir()
        (out / "evaluation.json").write_text(json.dumps({"summary": {
            "buffers": [{"buffer_metres": 20, "f1": 0.55}],
        }}), encoding="utf-8")
        value, source = _value_for(tmp_path, {}, None, "job", "F1", 20)
        assert value == pytest.approx(0.55)
        assert source == "job/evaluation.json"

    def test_falls_back_to_a_corrected_f1_summary(self, tmp_path: Path) -> None:
        """A corrected-F1 twin writes summary.json, not evaluation.json.

        Without this the eight 55-map twin jobs would score on sapphire and
        still read ``pending`` for ever.
        """
        out = tmp_path / "job"
        out.mkdir()
        (out / "summary.json").write_text(json.dumps({"results": [
            {"R_m": 50, "F1": 0.71, "tile_classification": {"mcc": 0.6}},
        ]}), encoding="utf-8")
        value, source = _value_for(tmp_path, {}, None, "job", "F1", 50)
        assert value == pytest.approx(0.71)
        assert source == "job/summary.json"

    def test_evaluation_json_is_preferred_when_both_exist(
        self, tmp_path: Path
    ) -> None:
        """A directory holding both shapes resolves deterministically."""
        out = tmp_path / "job"
        out.mkdir()
        (out / "evaluation.json").write_text(json.dumps({"summary": {
            "buffers": [{"buffer_metres": 50, "f1": 0.60}]}}), encoding="utf-8")
        (out / "summary.json").write_text(json.dumps({"results": [
            {"R_m": 50, "F1": 0.71}]}), encoding="utf-8")
        value, source = _value_for(tmp_path, {}, None, "job", "F1", 50)
        assert value == pytest.approx(0.60)
        assert source.endswith("evaluation.json")

    def test_missing_on_both_routes(self, tmp_path: Path) -> None:
        """Absent is reported as missing, never as a default."""
        assert _value_for(tmp_path, {}, None, None, "F1", 20) == (None, "missing")

    def test_blank_csv_cell_is_missing_not_zero(self, tmp_path: Path) -> None:
        """An empty CSV cell means the metric was not computed."""
        conditions = {"a::b": {"F1": ""}}
        assert _value_for(tmp_path, conditions, "a::b", None, "F1", 20) == (
            None, "missing"
        )


# --------------------------------------------------------------------------- #
# The committed reference constants
# --------------------------------------------------------------------------- #


class TestReferenceCounts:
    """`REFERENCE_N_MOUNDS` must match the committed reference files."""

    @pytest.mark.parametrize(
        ("term", "expected"),
        [("curator", 569), ("student", 4746), ("canonical", 5161),
         ("standardised", 5010)],
    )
    def test_recounts_the_committed_geojson(self, term: str, expected: int) -> None:
        """Recount the file rather than trusting the constant.

        `n_refs` is published in `strata.csv` and read as a fact about the
        reference. A reference that is re-materialised without the constant
        being updated would publish a stale count with no warning; this test is
        the warning. Skipped rather than failed where a reference is not
        present in the checkout, since the constants are the thing under test,
        not the availability of large committed data.
        """
        path = PROJECT_ROOT / REFERENCE_PATH[term]
        if not path.exists():  # pragma: no cover - depends on checkout contents
            pytest.skip(f"{path} is not present in this checkout")
        counted = len(json.loads(path.read_text(encoding="utf-8"))["features"])
        assert counted == expected == REFERENCE_N_MOUNDS[term]


# --------------------------------------------------------------------------- #
# Verifier-stage matching
# --------------------------------------------------------------------------- #


def _manifest(path: str, source: str, min_vote: int) -> VerifierManifest:
    """Build a VerifierManifest for the matcher tests."""
    return VerifierManifest(
        path=path, source_basename=source, min_vote=min_vote,
        max_vote=min_vote + 4, n_candidates=100,
    )


class TestMatchVerifierManifest:
    """Matching a verified cell to the candidate manifest of ITS stage."""

    def test_no_manifests(self) -> None:
        """A run with no verifier stage cannot be measured."""
        assert match_verifier_manifest([], "verified-v1", "pool", None, 5) == (
            None, "no-manifest"
        )

    def test_sole_manifest_is_taken(self) -> None:
        """One stage, nothing to confuse it with."""
        only = _manifest("outputs/r/crops/candidate_manifest.json",
                         "consensus-4of5.geojson", 4)
        assert match_verifier_manifest([only], "verified-v1", "pool", None, 5) == (
            only, "sole-manifest"
        )

    def test_union_shell_matches_on_exact_n(self) -> None:
        """union_k1 must not match a cell at N = 10, nor the reverse.

        Substring matching would: "union_k1" is a prefix of "union_k10".
        """
        k1 = _manifest("outputs/r/v/p/crops_k1/candidate_manifest.json",
                       "union_k1.geojson", 1)
        k10 = _manifest("outputs/r/v/p/crops/candidate_manifest.json",
                        "union_k10.geojson", 1)
        assert match_verifier_manifest([k1, k10], "ladder-n1", "p", None, 1)[0] is k1
        assert match_verifier_manifest([k1, k10], "k10-cell", "p", None, 10)[0] is k10

    def test_consensus_shell_separates_stages_sharing_a_pool(self) -> None:
        """verifier-robustness verified a union stage and a ge3of5 stage."""
        union = _manifest("outputs/r/384-text-1of5-union/crops/candidate_manifest.json",
                          "flash-high-text-1of5.geojson", 1)
        ge3 = _manifest("outputs/r/384-text-ge3of5/crops/candidate_manifest.json",
                        "flash-high-text-ge3of5.geojson", 3)
        matched, basis = match_verifier_manifest(
            [union, ge3], "verified-384-ge3of5-t0-3-n5", "flash-high-text-1of5",
            None, 5,
        )
        assert matched is ge3 and matched.min_vote == 3
        assert basis.startswith("matched-")

    def test_fusion_family_is_applied_symmetrically(self) -> None:
        """A greedy cell must NOT land on the WBF stage, and vice versa."""
        greedy = _manifest("outputs/h8/scale-4/crops/candidate_manifest.json",
                           "consensus_t1.geojson", 1)
        wbf = _manifest("outputs/h8/wbf/scale-4/crops/candidate_manifest.json",
                        "wbf_candidates.geojson", 1)
        assert match_verifier_manifest(
            [greedy, wbf], "verified-scale-4", "scale-4", None, 5)[0] is greedy
        assert match_verifier_manifest(
            [greedy, wbf], "verified-wbf-scale-4", "scale-4", None, 5)[0] is wbf

    def test_nested_pool_names_do_not_collide(self) -> None:
        """`g384_ov192_image` is a substring of `g384_ov192_image_high`.

        Any containment-based score ties the two stages. Matching whole path
        segments separates them, and each cell keeps its own.
        """
        plain = _manifest(
            "outputs/ib/verifier/g384_ov192_image/crops/candidate_manifest.json",
            "union_k10.geojson", 1)
        high = _manifest(
            "outputs/ib/verifier/g384_ov192_image_high/crops/candidate_manifest.json",
            "union_k10.geojson", 1)
        matched, basis = match_verifier_manifest(
            [plain, high], "g384-ov192-image-min-k10-verified", "g384_ov192_image",
            "g384_ov192", 10,
        )
        assert matched is plain
        assert basis == "matched-lineage"
        other, _basis = match_verifier_manifest(
            [plain, high], "g384-ov192-image-high-k10-verified",
            "g384_ov192_image_high", "g384_ov192", 10,
        )
        assert other is high

    def test_a_pool_may_not_match_a_longer_pool_ending_the_same_way(self) -> None:
        """`text-1of10` must not claim the stage of `flash-high-text-1of10`.

        The original substring failure, in its exact corpus shape: pv-diag-384
        holds both pools, and unbounded containment let the shorter one cite the
        longer one's manifest as its evidence. Boundary matching separates them.
        """
        stage = _manifest(
            "outputs/h11/pv-diag-384/verified/flash-high-text-6of10/"
            "candidate_manifest.json",
            "flash-high-text-1of10.geojson", 6)
        other = _manifest(
            "outputs/h11/pv-diag-384/verified/image-6of10/candidate_manifest.json",
            "image-1of10.geojson", 6)
        matched, basis = match_verifier_manifest(
            [stage, other], "verified-adv-text-min-6of10", "text-1of10", None, 10
        )
        assert matched is None
        assert basis == "ambiguous-lineage"

    def test_the_owning_pool_still_matches_its_own_stage(self) -> None:
        """The negative above must not cost the true match its resolution."""
        stage = _manifest(
            "outputs/h11/pv-diag-384/verified/flash-high-text-6of10/"
            "candidate_manifest.json",
            "flash-high-text-1of10.geojson", 6)
        other = _manifest(
            "outputs/h11/pv-diag-384/verified/image-6of10/candidate_manifest.json",
            "image-1of10.geojson", 6)
        matched, _basis = match_verifier_manifest(
            [stage, other], "verified-adv-text-6of10", "flash-high-text-1of10",
            None, 10,
        )
        assert matched is stage

    def test_sole_manifest_of_another_lineage_is_refused(self) -> None:
        """n1-outstanding-384 has seven pools and one image verifier stage.

        The short circuit handed that stage to text cells as their evidence.
        """
        only = _manifest(
            "outputs/h11/n1-outstanding-384/image-t0/verified-v1-n3/crops/"
            "candidate_manifest.json",
            "consensus_t1.geojson", 1)
        siblings = [("image-t0", None), ("brief-text-t03", None)]
        matched, basis = match_verifier_manifest(
            [only], "baseline-flash-text-minimal-t-0-3", "brief-text-t03", None,
            1, siblings=siblings,
        )
        assert matched is None
        assert basis == "sole-manifest-lineage-mismatch"

    def test_sole_manifest_of_the_own_lineage_is_accepted(self) -> None:
        """The image cell of that same run keeps its stage."""
        only = _manifest(
            "outputs/h11/n1-outstanding-384/image-t0/verified-v1-n3/crops/"
            "candidate_manifest.json",
            "consensus_t1.geojson", 1)
        siblings = [("image-t0", None), ("brief-text-t03", None)]
        matched, basis = match_verifier_manifest(
            [only], "baseline-flash-image-minimal-t-0-0", "image-t0", None, 3,
            siblings=siblings,
        )
        assert matched is only
        assert basis == "sole-manifest"

    def test_sole_manifest_naming_no_lineage_is_accepted(self) -> None:
        """gold-standard-v2 crops at run level from an unnamed consensus set.

        The check is contradiction, not confirmation: a stage that names no
        lineage contradicts nothing, and requiring positive confirmation would
        reject every correct single-pool match in the corpus.
        """
        only = _manifest(
            "outputs/gs/gold-standard-v2/crops/candidate_manifest.json",
            "consensus-4of5.geojson", 4)
        matched, basis = match_verifier_manifest(
            [only], "verified-v1", "detect_brief-text", None, 5,
            siblings=[("detect_brief-text", None)],
        )
        assert matched is only
        assert basis == "sole-manifest"

    def test_union_shell_narrows_rather_than_terminating(self) -> None:
        """A rung with no union of its own N still reaches lineage matching.

        stride-55map cropped only the ten-pass union, and an early return
        discarded its eight N = 3 / N = 5 rungs before their lineage
        directories could identify them.
        """
        mine = _manifest(
            "outputs/s/verifier/g384_ov128_55map/crops/candidate_manifest.json",
            "union_k10.geojson", 1)
        other = _manifest(
            "outputs/s/verifier/g384_ov192_55map/crops/candidate_manifest.json",
            "union_k10.geojson", 1)
        matched, basis = match_verifier_manifest(
            [mine, other], "g384-ov128-55map-n3-oracle", "g384_ov128_55map",
            "g384_ov128", 3,
        )
        assert matched is mine
        assert basis.endswith("-via-union_k10-superset")

    def test_shell_tokens_match_only_at_delimiters(self) -> None:
        """`3of5` must not match `ge3of5`; they are different vote shells."""
        ge3 = _manifest("outputs/r/a-ge3of5/crops/candidate_manifest.json",
                        "a-ge3of5.geojson", 3)
        three = _manifest("outputs/r/a-3of5/crops/candidate_manifest.json",
                          "a-3of5.geojson", 3)
        matched, _basis = match_verifier_manifest(
            [ge3, three], "verified-x-3of5", "nowhere", None, 5
        )
        assert matched is three

    def test_pool_subtree_stages_beat_run_level_ones(self) -> None:
        """A pool that verified in its own subtree owns those stages.

        The pv-diag-384 shape: `verified/image-6of10` cropped the run-level
        `consensus/image-1of10.geojson`, while the `flash-high-image-n5`
        pool cropped its own `image-t1.0/consensus/consensus_t1.geojson`. Both
        are image and both carry the shell, so tokens alone tie them; only
        containment in the pool directory separates them.
        """
        run_level = _manifest(
            "outputs/h11/pv-diag-384/verified/image-6of10/candidate_manifest.json",
            "image-1of10.geojson", 6)
        in_pool = _manifest(
            "outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/"
            "verified-v1-n5/crops/candidate_manifest.json",
            "consensus_t1.geojson", 1)
        matched, basis = match_verifier_manifest(
            [run_level, in_pool], "flash-high-image-n5-image-t1.0-verified-6of10",
            "flash-high-image-n5-image-t1.0", None, 5,
            pool_dir="outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0",
        )
        assert matched is in_pool
        assert basis == "matched-pool-subtree"

    def test_fusion_family_outranks_the_pool_subtree(self) -> None:
        """h8-v2's WBF stage sits OUTSIDE the proposer pool directory.

        Determined from the recorded sources, not the names: the WBF stage
        cropped `wbf_candidates.geojson` and the in-pool stage cropped
        `consensus_t1.geojson`, so a WBF-verified cell belongs to the former.
        Ordering the subtree rule first would drag it back onto the greedy
        stage, which is why fusion is filtered first.
        """
        greedy = _manifest("outputs/h8-v2/scale-4/crops/candidate_manifest.json",
                           "consensus_t1.geojson", 1)
        wbf = _manifest("outputs/h8-v2/wbf/scale-4/crops/candidate_manifest.json",
                        "wbf_candidates.geojson", 1)
        matched, _basis = match_verifier_manifest(
            [greedy, wbf], "verified-wbf-scale-4", "scale-4", None, 5,
            pool_dir="outputs/h8-v2/scale-4",
        )
        assert matched is wbf
        other, _basis = match_verifier_manifest(
            [greedy, wbf], "verified-scale-4", "scale-4", None, 5,
            pool_dir="outputs/h8-v2/scale-4",
        )
        assert other is greedy

    def test_pool_subtree_filter_is_a_no_op_when_the_pool_has_no_stages(
        self,
    ) -> None:
        """A pool that never verified in its own tree must not lose its match."""
        only = _manifest("outputs/r/verified/a-3of5/candidate_manifest.json",
                         "a-1of5.geojson", 3)
        other = _manifest("outputs/r/verified/b-3of5/candidate_manifest.json",
                          "b-1of5.geojson", 3)
        matched, _basis = match_verifier_manifest(
            [only, other], "verified-a-3of5", "a-1of5", None, 5,
            pool_dir="outputs/r/a-1of5",
        )
        assert matched is only

    def test_unmatchable_lineage_is_disclosed_not_defaulted(self) -> None:
        """Two indistinguishable stages give no verdict, not the run minimum."""
        first = _manifest("outputs/r/a/crops/candidate_manifest.json", "x.geojson", 1)
        second = _manifest("outputs/r/b/crops/candidate_manifest.json", "y.geojson", 4)
        matched, basis = match_verifier_manifest(
            [first, second], "verified-adv", "nowhere", None, 5
        )
        assert matched is None
        assert basis == "ambiguous-lineage"


class TestCollectVerifierManifests:
    """Surveying a run's candidate manifests."""

    @pytest.mark.parametrize(
        "smoke_segment", ["_smoke", "smoke-384", "smoke-512", "smoke-armB",
                          "smoke-anything-new"],
    )
    def test_smoke_prefix_rule_covers_unlisted_trees(
        self, tmp_path: Path, smoke_segment: str
    ) -> None:
        """A prefix rule, not an allowlist.

        The previous version enumerated the smoke directories that existed on
        the day it was written, so the next one would have been counted as a
        real stage until somebody noticed.
        """
        real = tmp_path / "stage" / "crops" / "candidate_manifest.json"
        smoke = tmp_path / smoke_segment / "crops" / "candidate_manifest.json"
        for path, votes in ((real, [3, 4, 5]), (smoke, [1, 5])):
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({
                "source_geojson": "s.geojson",
                "candidates": [{"properties": {"vote_count": v}} for v in votes],
            }), encoding="utf-8")
        manifests, skipped = collect_verifier_manifests(tmp_path, tmp_path)
        assert [m.min_vote for m in manifests] == [3]
        assert len(skipped) == 1

    def test_smoke_trees_are_excluded_and_reported(self, tmp_path: Path) -> None:
        """A 12-candidate rehearsal must not set a campaign's coverage floor."""
        real = tmp_path / "stage" / "crops" / "candidate_manifest.json"
        smoke = tmp_path / "_smoke" / "stage" / "crops" / "candidate_manifest.json"
        for path, votes in ((real, [3, 4, 5]), (smoke, [1, 5])):
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({
                "source_geojson": "s.geojson",
                "candidates": [{"properties": {"vote_count": v}} for v in votes],
            }), encoding="utf-8")

        manifests, skipped = collect_verifier_manifests(tmp_path, tmp_path)
        assert [m.min_vote for m in manifests] == [3]
        assert len(skipped) == 1
        assert "smoke-test tree" in skipped[0]

    def test_proposer_votes_is_read_as_a_vote_count(self, tmp_path: Path) -> None:
        """Two key vocabularies exist; reading one excluded eight real stages.

        The e47-propose-brief ladder records `proposer_votes`, and every one of
        its stages was dropped under a reason that was not true of it.
        """
        path = tmp_path / "stage" / "crops" / "candidate_manifest.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({
            "source_geojson": "flash-high-text-1of5.geojson",
            "candidates": [
                {"properties": {"proposer_votes": v, "cluster_size": v}}
                for v in (3, 4, 5)
            ],
        }), encoding="utf-8")
        manifests, skipped = collect_verifier_manifests(tmp_path, tmp_path)
        assert skipped == []
        assert manifests[0].min_vote == 3
        assert manifests[0].max_vote == 5

    def test_manifests_without_vote_counts_are_reported_diagnostically(
        self, tmp_path: Path
    ) -> None:
        """The exclusion reason must describe THIS manifest, not a stock story.

        The previous reason asserted "a single-pass verifier stage crops from a
        raw pass" of every exclusion, which was false of the eight stages that
        merely used a different key.
        """
        path = tmp_path / "stage" / "crops" / "candidate_manifest.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({
            "source_geojson": "s.geojson",
            "candidates": [{"properties": {"confidence": 1.0, "subtype": "x"}}],
        }), encoding="utf-8")
        manifests, skipped = collect_verifier_manifests(tmp_path, tmp_path)
        assert manifests == []
        assert "vote_count, proposer_votes" in skipped[0]
        assert "confidence" in skipped[0] and "subtype" in skipped[0]
        assert "single-pass verifier stage" not in skipped[0]

    def test_unreadable_manifest_is_reported_not_swallowed(
        self, tmp_path: Path
    ) -> None:
        """Dropping a manifest silently can raise a floor and flip a verdict."""
        path = tmp_path / "stage" / "crops" / "candidate_manifest.json"
        path.parent.mkdir(parents=True)
        path.write_text("{not json", encoding="utf-8")
        manifests, skipped = collect_verifier_manifests(tmp_path, tmp_path)
        assert manifests == []
        assert "unreadable" in skipped[0]

    def test_paths_are_recorded_relative_to_the_repository(
        self, tmp_path: Path
    ) -> None:
        """Published evidence must not bake in a machine-local absolute path."""
        path = tmp_path / "run" / "stage" / "crops" / "candidate_manifest.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({
            "source_geojson": "s.geojson",
            "candidates": [{"properties": {"vote_count": 2}}],
        }), encoding="utf-8")
        manifests, _ = collect_verifier_manifests(tmp_path / "run", tmp_path)
        assert manifests[0].path == "run/stage/crops/candidate_manifest.json"
