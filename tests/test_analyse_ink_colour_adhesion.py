"""
Tier 1 tests for ``scripts.analyse_ink_colour_adhesion``.

Background
----------
Obs 407 hypothesises that displaced marks adhere to attractors of
matching ink colour. The analysis script contrasts displacement
magnitudes between black-element and plain symbol classes per cohort
(model phantoms, random student jitter sample, condition-selected
student rows), with seeded label-permutation tests.

Three properties must hold for the output to be trustworthy:

1. **The permutation behaves like a two-sample label test.** Identical
   groups must give p ≈ 1; extreme disjoint groups must give the
   smallest achievable p; the seed makes reruns byte-stable.
2. **The a-priori filters are enforced.** not_a_mound, extra_point,
   skipped, and displacement-free rows never reach a cohort, and an
   unmapped symbol type raises rather than silently guessing a colour.
3. **Cohort assignment follows the block plan.** jitter_sample rows go
   to student_random, other corrected_student rows to student_hard,
   promoted phantoms to model.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.analyse_ink_colour_adhesion import (
    analyse,
    assign_cohort,
    load_records,
    permutation_test,
)

pytestmark = pytest.mark.tier1


def _write_csv(path: Path, rows: list[dict]) -> Path:
    """Write a minimal marked-centres fixture with only the read columns."""
    fields = ["source_layer", "item_type", "symbol_type", "skipped", "displacement_m"]
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _row(**overrides) -> dict:
    row = {
        "source_layer": "promoted_phantom",
        "item_type": "phantom",
        "symbol_type": "burial_mound",
        "skipped": "False",
        "displacement_m": "10.0",
    }
    row.update(overrides)
    return row


class TestPermutationTest:
    def test_identical_groups_null(self):
        values = [10.0, 11.0, 9.0, 10.5, 9.5] * 4
        result = permutation_test(values, list(values), "mean", n_permutations=500)
        assert result["observed_black_minus_plain_m"] == 0.0
        assert result["p_two_sided"] > 0.5

    def test_disjoint_groups_significant(self):
        # Continuous, non-overlapping samples: two-valued fixtures are
        # degenerate for the median statistic (every permutation flips
        # the whole ±delta), so spread the values within each group.
        black = [float(v) for v in range(1, 16)]
        plain = [float(v) for v in range(101, 116)]
        result = permutation_test(black, plain, "median", n_permutations=2000)
        assert result["observed_black_minus_plain_m"] == -100.0
        assert result["p_two_sided"] < 0.01

    def test_seed_makes_reruns_stable(self):
        black = [5.0, 7.0, 9.0, 11.0, 13.0]
        plain = [6.0, 8.0, 10.0, 12.0, 14.0]
        first = permutation_test(black, plain, "mean", n_permutations=1000)
        second = permutation_test(black, plain, "mean", n_permutations=1000)
        assert first == second


class TestLoadFilters:
    def test_a_priori_exclusions(self, tmp_path):
        path = _write_csv(
            tmp_path / "marked.csv",
            [
                _row(),
                _row(symbol_type="not_a_mound"),
                _row(source_layer="extra_point"),
                _row(skipped="True"),
                _row(displacement_m=""),
            ],
        )
        records = load_records(path)
        assert len(records) == 1
        assert records[0]["colour_class"] == "plain"

    def test_unmapped_symbol_raises(self, tmp_path):
        path = _write_csv(tmp_path / "marked.csv", [_row(symbol_type="mystery")])
        with pytest.raises(ValueError, match="mystery"):
            load_records(path)

    def test_colour_classes(self, tmp_path):
        path = _write_csv(
            tmp_path / "marked.csv",
            [
                _row(symbol_type="trig_point_on_mound"),
                _row(symbol_type="bench_mark_on_mound"),
                _row(symbol_type="settlement_mound"),
            ],
        )
        classes = [r["colour_class"] for r in load_records(path)]
        assert classes == ["black", "black", "plain"]


class TestCohorts:
    def test_assignment_follows_block_plan(self):
        assert assign_cohort({"source_layer": "promoted_phantom",
                              "item_type": "phantom"}) == "model"
        assert assign_cohort({"source_layer": "corrected_student",
                              "item_type": "jitter_sample"}) == "student_random"
        assert assign_cohort({"source_layer": "corrected_student",
                              "item_type": "merge_site"}) == "student_hard"

    def test_analyse_census_and_shape(self, tmp_path):
        rows = (
            [_row(displacement_m="40.0")] * 6
            + [_row(symbol_type="trig_point_on_mound", displacement_m="12.0")] * 6
            + [_row(source_layer="corrected_student", item_type="jitter_sample")] * 3
            + [_row(source_layer="corrected_student", item_type="jitter_sample",
                    symbol_type="bench_mark_on_mound")] * 3
        )
        records = load_records(_write_csv(tmp_path / "marked.csv", rows))
        results = analyse(records, n_permutations=200)
        assert results["census"]["records_retained"] == 18
        assert results["census"]["records_in_cohorts"] == 18
        assert set(results["cohorts"]) == {"model", "student_random"}
        model = results["cohorts"]["model"]
        assert model["black"]["n"] == 6 and model["plain"]["n"] == 6
        assert model["tests"][0]["statistic"] == "mean"
        assert model["tests"][1]["statistic"] == "median"
