"""Tier-1 tests for ``scripts/lib_c4_compare.py`` (C4 comparison core).

Pins the corpus's real quoting conventions: the charter § 6 example
(0.8902 quoted as 0.890), thousands separators, approx-marked costs,
signed deltas, percentages, and the minimal JSONPath resolver.
"""

from __future__ import annotations

import pytest

from scripts.lib_c4_compare import (
    match_at_quoted_precision,
    normalise_path,
    parse_value,
    resolve_path,
)


@pytest.mark.tier1
@pytest.mark.parametrize(
    "verbatim,value,dp,approx,pct,currency",
    [
        ("0.890", 0.890, 3, False, False, None),
        ("16,484", 16484.0, 0, False, False, None),
        ("~$34.5", 34.5, 1, True, False, "$"),
        ("US$150", 150.0, 0, False, False, "US$"),
        ("+0.032", 0.032, 3, False, False, None),
        ("−0.095", -0.095, 3, False, False, None),  # Unicode minus
        ("92.0 %", 92.0, 1, False, True, None),
        ("487", 487.0, 0, False, False, None),
        ("≈ 12", 12.0, 0, True, False, None),
        ("44 220", 44220.0, 0, False, False, None),   # space thousands
        ("~44 220", 44220.0, 0, True, False, None),
        ("3 736", 3736.0, 0, False, False, None),
        ("10 000", 10000.0, 0, False, False, None),   # NBSP thousands
    ],
)
def test_parse_value_conventions(verbatim, value, dp, approx, pct, currency):
    parsed = parse_value(verbatim)
    assert parsed is not None, verbatim
    assert parsed.value == pytest.approx(value)
    assert parsed.decimal_places == dp
    assert parsed.approx is approx
    assert parsed.is_percentage is pct
    assert parsed.currency == currency


@pytest.mark.tier1
@pytest.mark.parametrize("bad", ["", "F1", "0.890 / 0.790", "p < 0.05", "3-of-5"])
def test_parse_value_rejects_non_single_values(bad):
    assert parse_value(bad) is None


@pytest.mark.tier1
def test_match_charter_example_rounding():
    # Charter § 6: recomputed 0.8902 == quoted 0.890.
    quoted = parse_value("0.890")
    result = match_at_quoted_precision(quoted, 0.8902)
    assert result["match"] is True
    assert result["mode"] == "round"


@pytest.mark.tier1
def test_match_truncation_convention():
    # 0.8968 quoted as 0.896 only matches under truncation.
    result = match_at_quoted_precision(parse_value("0.896"), 0.8968)
    assert result["match"] is True
    assert result["mode"] == "truncate"


@pytest.mark.tier1
def test_match_exact_and_mismatch_and_approx():
    assert match_at_quoted_precision(parse_value("487"), 487.0)["mode"] == "exact"
    hard = match_at_quoted_precision(parse_value("0.890"), 0.8853)
    assert hard["match"] is False and hard["mode"] == "mismatch"
    soft = match_at_quoted_precision(parse_value("~$60"), 34.5)
    assert soft["match"] is False and soft["mode"] == "approx"
    assert soft["abs_error"] == pytest.approx(25.5)


@pytest.mark.tier1
def test_match_nonfinite_actual_never_matches():
    import math

    result = match_at_quoted_precision(parse_value("0.890"), math.nan)
    assert result["match"] is False and result["abs_error"] == math.inf
    assert match_at_quoted_precision(parse_value("487"), math.inf)["match"] is False


@pytest.mark.tier1
def test_resolve_path_forms():
    doc = {
        "results": {"20m": {"f1": 0.8902}},
        "tiers": [{"conditions": ["a", "b"]}, {"f1_at_20m": 0.71}],
        "odd key": {"x": 1},
    }
    assert resolve_path(doc, "$.results['20m'].f1") == 0.8902
    assert resolve_path(doc, "$.tiers[0].conditions[1]") == "b"
    assert resolve_path(doc, "$.tiers[-1].f1_at_20m") == 0.71
    assert resolve_path(doc, '$["odd key"].x') == 1
    assert resolve_path(doc, "$") is doc


@pytest.mark.tier1
@pytest.mark.parametrize(
    "path", ["results.f1", "$.results['30m']", "$.tiers[9]", "$.results.f1!", ""]
)
def test_resolve_path_failures_name_the_step(path):
    doc = {"results": {"20m": {"f1": 1.0}}, "tiers": []}
    with pytest.raises(KeyError):
        resolve_path(doc, path)


# --- Session-123 extensions (mismatch-triage-2026-07-31 repairs) ---


@pytest.mark.tier1
@pytest.mark.parametrize(
    "verbatim,value,dp",
    [
        ("30m", 30.0, 0),        # unit suffix (metres)
        ("6 px", 6.0, 0),
        ("1.7×", 1.7, 1),        # multiplication sign suffix
        ("2.5x", 2.5, 1),
        ("N=5", 5.0, 0),         # label prefixes
        ("T=0.3", 0.3, 1),
        ("K=30", 30.0, 0),
        ("eight", 8.0, 0),       # spelled-out counts
        ("Zero", 0.0, 0),
    ],
)
def test_parse_value_units_prefixes_words(verbatim, value, dp):
    parsed = parse_value(verbatim)
    assert parsed is not None, verbatim
    assert parsed.value == pytest.approx(value)
    assert parsed.decimal_places == dp


@pytest.mark.tier1
@pytest.mark.parametrize("bad", ["10k", "1.2 K", "3M", "6–10", "thirteen"])
def test_parse_value_rejects_multipliers_and_ranges(bad):
    # Magnitude suffixes are multipliers, not units — a mantissa-only
    # parse would manufacture false MISMATCHes; ranges are not scalars.
    assert parse_value(bad) is None


@pytest.mark.tier1
def test_match_decimal_midpoint_half_up():
    # Triage row 050#10[0]: artefact 0.9195 legitimately quoted 0.920
    # (float round() resolves the binary repr down to 0.919).
    result = match_at_quoted_precision(parse_value("0.920"), 0.9195)
    assert result["match"] is True
    assert result["mode"] == "round-half-up"
    # A genuine mismatch stays a mismatch under the new mode.
    assert match_at_quoted_precision(parse_value("0.92"), 0.9149)["match"] is False


@pytest.mark.tier1
@pytest.mark.parametrize(
    "path,clean,op",
    [
        ("len:$.features", "$.features", "len"),
        ("len($.results)", "$.results", "len"),
        ("count($.pairwise)", "$.pairwise", "len"),
        ("$.candidates.length()", "$.candidates", "len"),
        ("$.features.length", "$.features", "len"),
        ("$.cells (array length)", "$.cells", "len"),
        ("$.features[*].properties.map_name (distinct count)",
         "$.features[*].properties.map_name", "distinct"),
        ("$.summary.f1", "$.summary.f1", None),
    ],
)
def test_normalise_path_length_spellings(path, clean, op):
    assert normalise_path(path) == (clean, op)


@pytest.mark.tier1
def test_resolve_path_filters_and_wildcard():
    doc = {
        "cells": [
            {"name": "TH7-k3", "f1_50": 0.8425, "tier": 1},
            {"name": "TM-k3", "f1_50": 0.8127, "tier": 3},
        ],
        "buffers": [{"n_tiles": 487}, {"n_tiles": 487}],
        "mixed": [{"v": 1}, {"v": 2}],
    }
    assert resolve_path(doc, "$.cells[?(@.name=='TH7-k3')].f1_50") == 0.8425
    assert resolve_path(doc, "$.cells[?(@.tier==1)].name") == "TH7-k3"
    assert resolve_path(doc, "$.buffers[*].n_tiles") == [487, 487]
    assert resolve_path(doc, "$.mixed[*].v") == [1, 2]
    with pytest.raises(KeyError):  # 0 filter hits
        resolve_path(doc, "$.cells[?(@.name=='absent')].f1_50")
    with pytest.raises(KeyError):  # ambiguous: two elements match
        resolve_path(doc, "$.buffers[?(@.n_tiles==487)]")


@pytest.mark.tier1
def test_resolve_path_filter_boolean_literal():
    doc = {"pairwise": [{"significant": True, "pair": "a-b"},
                        {"significant": False, "pair": "c-d"}]}
    assert resolve_path(doc, "$.pairwise[?(@.significant == true)].pair") == "a-b"
