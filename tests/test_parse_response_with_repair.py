"""
Tests for parse_response_with_repair
====================================

Exercises the three-tier malformed-JSON repair pipeline used by the
realtime proposer in ``scripts/4_detect_mounds_batch.py`` and shared
with the batch parser in ``scripts/lib_batch_api.py``.

The pipeline tiers are:
    1. Strip trailing commas, then strict ``json.loads``.
    2. Permissive ``json5.loads``.
    3. Linear longest-valid-prefix scan from the end of the text.

These tests use synthetic inputs covering each tier independently plus
a final-failure case that no tier can recover.

Background:
    Audit of three production runs (Sessions 80–83) lost 163 tiles to
    realtime JSON parse failures. ~92 % matched patterns this pipeline
    handles. See the commit message and observation log for the full
    breakdown.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import pytest

from scripts.lib_batch_api import parse_response_with_repair


# ── Tier 1: trailing-comma repair ────────────────────────────────────

class TestTier1TrailingComma:
    """
    Inputs that strict ``json.loads`` rejects only because of a trailing
    comma. The Tier 1 regex strip-and-retry should resolve all of these
    without needing to fall through to Tier 2 or Tier 3.
    """

    @pytest.mark.tier1
    def test_object_with_trailing_comma(self):
        """Trailing comma after the last key/value pair in an object."""
        result = parse_response_with_repair('{"a": 1,}')
        assert result == {"a": 1}

    @pytest.mark.tier1
    def test_array_with_trailing_comma(self):
        """Trailing comma after the last element in an inline array."""
        result = parse_response_with_repair('{"a": [1, 2,]}')
        assert result == {"a": [1, 2]}

    @pytest.mark.tier1
    def test_nested_trailing_commas(self):
        """Trailing commas inside nested array and outer object."""
        text = '{"detections": [{"box_2d": [0, 0, 100, 100,],},],}'
        result = parse_response_with_repair(text)
        assert result == {
            "detections": [{"box_2d": [0, 0, 100, 100]}],
        }

    @pytest.mark.tier1
    def test_trailing_comma_with_whitespace_before_brace(self):
        """Trailing comma followed by whitespace, then the closing brace."""
        result = parse_response_with_repair('{"a": 1,\n  }')
        assert result == {"a": 1}

    @pytest.mark.tier1
    def test_well_formed_json_passes_through_tier1(self):
        """Strict-valid input also parses cleanly via Tier 1's strict json."""
        result = parse_response_with_repair('{"detections": [1, 2, 3]}')
        assert result == {"detections": [1, 2, 3]}


# ── Tier 2: json5 permissive parser ──────────────────────────────────

class TestTier2Json5:
    """
    Inputs that strict ``json.loads`` rejects, that the Tier 1 trailing-
    comma regex does not fix, but that the permissive ``json5`` parser
    accepts. Common cases: unquoted keys, single-quoted strings, embedded
    comments — all valid in JSON5 but not in strict JSON.
    """

    @pytest.mark.tier1
    def test_unquoted_keys(self):
        """Unquoted object keys — JSON5-style identifiers."""
        result = parse_response_with_repair('{a: 1, b: 2}')
        assert result == {"a": 1, "b": 2}

    @pytest.mark.tier1
    def test_single_quoted_strings(self):
        """Single-quoted string values — invalid in strict JSON."""
        result = parse_response_with_repair("{'a': 'hello'}")
        assert result == {"a": "hello"}

    @pytest.mark.tier1
    def test_embedded_block_comment(self):
        """Block comments inside the JSON body — JSON5 strips them."""
        result = parse_response_with_repair('{"a": 1 /* note */}')
        assert result == {"a": 1}


# ── Tier 3: longest-valid-prefix scan ────────────────────────────────

class TestTier3LongestPrefix:
    """
    Inputs where a valid JSON object/array is followed by trailing
    garbage (free-form prose, code fences, a second concatenated
    object). Strict ``json.loads`` raises ``Extra data``; Tier 1 cannot
    fix it; Tier 2's ``json5`` likewise rejects extra data after the
    root value. The Tier 3 scan should return the first successfully
    parsed prefix.
    """

    @pytest.mark.tier1
    def test_object_with_trailing_garbage(self):
        """Valid object followed by free-form garbage on a new line."""
        result = parse_response_with_repair('{"a": 1}\nextra garbage')
        assert result == {"a": 1}

    @pytest.mark.tier1
    def test_two_concatenated_objects(self):
        """Two back-to-back top-level objects — keep the first."""
        result = parse_response_with_repair('{"a": 1}{"b": 2}')
        assert result == {"a": 1}

    @pytest.mark.tier1
    def test_array_followed_by_prose(self):
        """Valid top-level array trailed by an explanatory sentence."""
        result = parse_response_with_repair(
            '[1, 2, 3]\nThis was the list of detections.'
        )
        assert result == [1, 2, 3]

    @pytest.mark.tier1
    def test_object_followed_by_markdown_fence(self):
        """Valid object trailed by a closing markdown code fence."""
        result = parse_response_with_repair(
            '{"detections": []}\n```'
        )
        assert result == {"detections": []}


# ── Failure case: no tier can recover ────────────────────────────────

class TestUnrecoverableInput:
    """
    Inputs so malformed that no tier can produce a parseable result.
    The helper should raise ``ValueError`` mentioning all three tiers,
    chained from the last underlying parser exception.
    """

    @pytest.mark.tier1
    def test_completely_unparseable_raises_value_error(self):
        """Pure prose with no JSON-like structure raises ValueError."""
        with pytest.raises(ValueError, match="Tier 1.*Tier 2.*Tier 3"):
            parse_response_with_repair("this is not JSON at all")

    @pytest.mark.tier1
    def test_empty_string_raises_value_error(self):
        """Empty input is unparseable by all three tiers."""
        with pytest.raises(ValueError, match="Tier 1.*Tier 2.*Tier 3"):
            parse_response_with_repair("")

    @pytest.mark.tier1
    def test_unmatched_open_brace_raises_value_error(self):
        """Open brace with no closing structure cannot be repaired."""
        with pytest.raises(ValueError, match="Tier 1.*Tier 2.*Tier 3"):
            parse_response_with_repair('{"a":')
