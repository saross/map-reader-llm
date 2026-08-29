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
from pathlib import Path

import pytest

from scripts.lib_uplift_supplement import (
    COLUMN_EXTENSIONS,
    NOTATION_KEY_PATH,
    REFERENCE_N_MOUNDS,
    CrossStratumAggregationError,
    NotationKey,
    StratumKey,
    UnknownColumnError,
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
        term, path, basis = resolve_reference(meta, "verified-k4", "student")
        assert (term, basis) == ("standardised", "eval-ground-truth")
        assert path.endswith("best-available-gt-55maps.geojson")

    def test_frozen_replay_copies_resolve_by_basename(self) -> None:
        """Replays under a scratch 'frozen' tree name the same reference file."""
        meta = {"cli_args": {
            "ground_truth": "/home/x/cc-scratch/tmp/tmpabc/frozen/inputs/vectors/"
                            "references/mounds-reference.geojson"
        }}
        term, _path, basis = resolve_reference(meta, "consensus-4of5", "curator")
        assert (term, basis) == ("curator", "eval-ground-truth")

    @pytest.mark.parametrize(
        ("label", "expected"),
        [("verified-k3-canonical-gt", "canonical"),
         ("verified-k4-standardised-gt", "standardised")],
    )
    def test_label_suffix_is_the_fallback(self, label: str, expected: str) -> None:
        """The explicit suffixes resolve when the evaluation records nothing."""
        term, _path, basis = resolve_reference(None, label, "combined")
        assert (term, basis) == (expected, "label-suffix")

    @pytest.mark.parametrize(
        "label", ["greedy-canonical", "wbf-canonical", "canonical-first",
                  "image-canonical", "text-canonical"],
    )
    def test_config_labels_using_the_word_canonical_are_not_caught(
        self, label: str
    ) -> None:
        """These name a CONFIG, not a reference; the run's facts must win."""
        term, _path, basis = resolve_reference(None, label, "curator")
        assert (term, basis) == ("curator", "run-facts")

    def test_combined_schema_class_maps_to_canonical(self) -> None:
        """The manifest's 'combined' is the notation key's canonical extended GT."""
        term, _path, basis = resolve_reference(None, "verified", "combined")
        assert (term, basis) == ("canonical", "run-facts")

    def test_unresolvable_reference_is_none_not_a_guess(self) -> None:
        """No rule firing yields None and says so."""
        term, _path, basis = resolve_reference(None, "verified", None)
        assert term is None
        assert basis == "unresolved"

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
