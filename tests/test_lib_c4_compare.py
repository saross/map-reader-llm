"""Tier-1 tests for ``scripts/lib_c4_compare.py`` (C4 comparison core).

Pins the corpus's real quoting conventions: the charter § 6 example
(0.8902 quoted as 0.890), thousands separators, approx-marked costs,
signed deltas, percentages, and the minimal JSONPath resolver.
"""

from __future__ import annotations

import pytest

from scripts.lib_c4_compare import match_at_quoted_precision, parse_value, resolve_path


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
