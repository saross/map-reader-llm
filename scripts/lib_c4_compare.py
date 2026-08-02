#!/usr/bin/env python3
"""Deterministic value-comparison core for the C4 recompute harness.

Phase 3 (``planning/audit-charter.md`` § 7): quoted values in mine
documents are compared against recomputed/read source values **at the
precision the document quotes** — the charter § 6 evidence convention
("recomputed 0.8902 == quoted 0.890 (2 d.p. rounding)"). This module
owns that arithmetic: verbatim-value parsing (thousands separators,
percentages, currency, approximation markers, signs) and the
match-at-quoted-precision rule, plus the minimal JSONPath-ish resolver
used to read anchored values out of committed artefacts.

Pure functions only — no I/O beyond ``resolve_path``'s dict walking; the
harness script owns file loading and report writing.
"""

from __future__ import annotations

import decimal
import math
import re
from dataclasses import dataclass

# Verbatim numeric token: optional sign/approx/currency, digits with
# thousands separators, optional decimal part, optional %/unit suffix.
_VALUE_RE = re.compile(
    r"^\s*(?P<approx>[~≈]|approx\.?\s*)?"
    r"(?P<sign>[-+−])?\s*"
    r"(?P<currency>(?:US)?\$|€|£)?\s*"
    r"(?P<digits>\d{1,3}(?:[,   ]\d{3})+|\d+)"
    r"(?P<frac>\.\d+)?"
    r"\s*(?P<pct>%)?"
    r"(?P<unit>\s*[A-Za-z×]{1,12})?\s*$"
)

# Label prefixes the corpus quotes verbatim ("N=5", "T=0.3", "K=30"):
# the label carries no numeric content — strip before parsing.
_LABEL_PREFIX_RE = re.compile(r"^\s*[A-Za-z]{1,4}\s*=\s*")

# Spelled-out counts appear in prose claims ("eight cells"); the map is
# closed and unambiguous, so parsing them stays mechanical.
_NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12,
    # Count-negation vocabulary (wave-3 hygiene): documents quote
    # "No"/"none" as the answer to a count question ("No entries point
    # at gold-standard-v2") — numerically zero.
    "no": 0, "none": 0,
}

# Bare magnitude suffixes ("10k", "1.2 K", "3M") are multipliers, not
# units — comparing the mantissa alone would produce a false MISMATCH,
# so these spans are rejected (stay UNRESOLVED for triage).
_MULTIPLIER_SUFFIXES = {"k", "K", "M", "B"}


@dataclass(frozen=True)
class ParsedValue:
    """A verbatim quoted value decomposed for precision-aware comparison.

    Attributes:
        value: The signed numeric value (per cent values stay on the
            quoted scale, e.g. "92.0 %" → 92.0).
        decimal_places: Digits quoted after the decimal point (0 for
            integers) — the precision the document commits to.
        approx: True when the span marks the value approximate (~, ≈).
        is_percentage: True when the span carries a per cent sign.
        currency: The currency marker, if any.
    """

    value: float
    decimal_places: int
    approx: bool
    is_percentage: bool
    currency: str | None


def parse_value(verbatim: str) -> ParsedValue | None:
    """Parse a verbatim numeric span into a :class:`ParsedValue`.

    Args:
        verbatim: The value exactly as quoted (e.g. "0.890", "16,484",
            "~$34.5", "+0.032", "92.0 %", "−0.095").

    Returns:
        ParsedValue, or None when the span is not a single numeric value.
    """
    word = _NUMBER_WORDS.get(verbatim.strip().lower())
    if word is not None:
        return ParsedValue(value=float(word), decimal_places=0, approx=False,
                           is_percentage=False, currency=None)
    match = _VALUE_RE.match(_LABEL_PREFIX_RE.sub("", verbatim))
    if not match:
        return None
    unit = (match.group("unit") or "").strip()
    if unit in _MULTIPLIER_SUFFIXES:
        return None
    # Group separators: comma, plain space, NBSP, narrow NBSP — the
    # corpus quotes "16,484" and "44 220" alike (wave-2 finding: the
    # space-separated form left 15+ quotes unparseable).
    digits = re.sub(r"[,   ]", "", match.group("digits"))
    frac = match.group("frac") or ""
    value = float(digits + frac)
    if match.group("sign") in ("-", "−"):
        value = -value
    return ParsedValue(
        value=value,
        decimal_places=max(len(frac) - 1, 0),
        approx=match.group("approx") is not None,
        is_percentage=match.group("pct") is not None,
        currency=match.group("currency"),
    )


def match_at_quoted_precision(quoted: ParsedValue, actual: float) -> dict:
    """Compare a source value against a quoted one at quoted precision.

    A quote matches when rounding OR truncating the actual value to the
    quoted number of decimal places reproduces it (both conventions
    appear in this corpus; the verdict records which applied). Approx
    quotes ("~$60") never hard-fail here — the harness routes them to
    triage with the computed relative error.

    Args:
        quoted: Parsed verbatim value from the document.
        actual: The recomputed/read source value, on the same scale.

    Returns:
        Dict with keys ``match`` (bool), ``mode`` ("exact" | "round" |
        "truncate" | "approx" | "mismatch"), ``actual`` (float), and
        ``abs_error`` (float).
    """
    if not math.isfinite(actual):
        return {"match": False, "mode": "mismatch", "actual": actual,
                "abs_error": math.inf}
    dp = quoted.decimal_places
    abs_error = abs(actual - quoted.value)
    if actual == quoted.value:
        return {"match": True, "mode": "exact", "actual": actual, "abs_error": 0.0}
    rounded = round(actual, dp)
    # round() banker's-rounding artefacts are irrelevant at corpus
    # precisions; compare via string formatting to dodge float repr.
    if f"{rounded:.{dp}f}" == f"{quoted.value:.{dp}f}":
        return {"match": True, "mode": "round", "actual": actual, "abs_error": abs_error}
    truncated = math.trunc(actual * 10**dp) / 10**dp
    if f"{truncated:.{dp}f}" == f"{quoted.value:.{dp}f}":
        return {"match": True, "mode": "truncate", "actual": actual, "abs_error": abs_error}
    # Decimal-midpoint half-up ("0.9195" quoted as "0.920"): float
    # round() resolves the binary representation downward, but half-up
    # on the shortest decimal repr is a legitimate corpus convention.
    half_up = decimal.Decimal(repr(actual)).quantize(
        decimal.Decimal(1).scaleb(-dp), rounding=decimal.ROUND_HALF_UP
    )
    if f"{half_up:.{dp}f}" == f"{quoted.value:.{dp}f}":
        return {"match": True, "mode": "round-half-up", "actual": actual,
                "abs_error": abs_error}
    if quoted.approx:
        return {"match": False, "mode": "approx", "actual": actual, "abs_error": abs_error}
    return {"match": False, "mode": "mismatch", "actual": actual, "abs_error": abs_error}


_PATH_TOKEN = re.compile(
    r"\.(?P<name>[A-Za-z_][\w-]*)"      # .name
    r"|\[(?P<index>-?\d+)\]"            # [3] / [-1]
    r"|\[(?P<q>['\"])(?P<key>.*?)(?P=q)\]"  # ['key'] / [\"key\"]
    r"|\[\?\(@\.(?P<fkey>[\w-]+)\s*==\s*"   # [?(@.key == literal)]
    r"(?P<fq>['\"])?(?P<fval>(?(fq)[^'\"]*|[^)\]]+))(?(fq)(?P=fq))\)\]"
    r"|\[(?P<star>\*)\]"                # [*]
)

# Extraction agents spell "count this collection" four ways beyond the
# harness's native ``len:`` prefix; normalise rather than re-extract.
_LEN_WRAPPER_RE = re.compile(r"^\s*(?:len|count)\(\s*(?P<inner>\$.*?)\s*\)\s*$")
_LEN_SUFFIX_RE = re.compile(r"^(?P<stem>\$.*?)\.length(?:\(\))?\s*$")
_ANNOTATION_RE = re.compile(
    r"^(?P<stem>\$.*?)\s+\((?P<op>array length|distinct count)\)\s*$"
)


def normalise_path(path: str) -> tuple[str, str | None]:
    """Rewrite corpus length/count spellings onto a canonical form.

    Recognised, in order: a ``len:`` prefix (native), ``len($.x)`` /
    ``count($.x)`` wrappers, an ``$.x.length`` / ``$.x.length()``
    suffix, and trailing ``(array length)`` / ``(distinct count)``
    annotations.

    Args:
        path: A raw locator as extracted.

    Returns:
        ``(clean_path, collection_op)`` where ``collection_op`` is
        ``None``, ``"len"``, or ``"distinct"``.
    """
    if path.startswith("len:"):
        return path[4:], "len"
    match = _LEN_WRAPPER_RE.match(path)
    if match:
        return match.group("inner"), "len"
    match = _ANNOTATION_RE.match(path)
    if match:
        op = "distinct" if match.group("op") == "distinct count" else "len"
        return match.group("stem"), op
    match = _LEN_SUFFIX_RE.match(path)
    if match:
        return match.group("stem"), "len"
    return path, None


_FILTER_LITERALS = {"true": True, "false": False, "null": None}


def _parse_filter_literal(raw: str, quoted: bool):
    """Parse the right-hand side of a ``[?(@.key == …)]`` filter."""
    if quoted:
        return raw
    token = raw.strip()
    if token in _FILTER_LITERALS:
        return _FILTER_LITERALS[token]
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token


def resolve_path(obj, path: str):
    """Resolve a minimal JSONPath-ish locator against loaded JSON.

    Supports ``$`` root, dotted names, integer indices, quoted string
    keys, single-key equality filters (``$.cells[?(@.name=='TH7-k3')]``,
    exactly one element must match), and the ``[*]`` wildcard (the rest
    of the path maps over every element and a plain ``list`` of results
    is returned — the caller owns any collapse rule).

    Args:
        obj: Parsed JSON object.
        path: Locator beginning with ``$``.

    Returns:
        The resolved value (a list when the path contains ``[*]``).

    Raises:
        KeyError: When the path does not start with ``$``, has trailing
            junk, or any step fails to resolve (message names the step).
    """
    if not path or not path.startswith("$"):
        raise KeyError(f"path must start with $: {path!r}")
    pos = 1
    current = obj
    while pos < len(path):
        match = _PATH_TOKEN.match(path, pos)
        if not match:
            raise KeyError(f"unparseable path segment at {path[pos:]!r} in {path!r}")
        pos = match.end()
        if match.group("star") is not None:
            if not isinstance(current, list):
                raise KeyError(f"[*] applied to non-list in {path!r}")
            rest = path[pos:]
            if not rest:
                return list(current)
            return [resolve_path(element, "$" + rest) for element in current]
        if match.group("fkey") is not None:
            if not isinstance(current, list):
                raise KeyError(f"filter applied to non-list in {path!r}")
            fkey = match.group("fkey")
            fval = _parse_filter_literal(match.group("fval"),
                                         match.group("fq") is not None)
            hits = [element for element in current
                    if isinstance(element, dict) and element.get(fkey) == fval]
            if len(hits) != 1:
                raise KeyError(
                    f"filter @.{fkey}=={fval!r} matched {len(hits)} elements "
                    f"(need exactly 1) in {path!r}")
            current = hits[0]
            continue
        if match.group("name") is not None:
            key = match.group("name")
        elif match.group("index") is not None:
            key = int(match.group("index"))
        else:
            key = match.group("key")
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError) as exc:
            raise KeyError(f"step {key!r} failed in {path!r}: {exc}") from exc
    return current
