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

import math
import re
from dataclasses import dataclass

# Verbatim numeric token: optional sign/approx/currency, digits with
# thousands separators, optional decimal part, optional %/unit suffix.
_VALUE_RE = re.compile(
    r"^\s*(?P<approx>[~≈]|approx\.?\s*)?"
    r"(?P<sign>[-+−])?\s*"
    r"(?P<currency>(?:US)?\$|€|£)?\s*"
    r"(?P<digits>\d{1,3}(?:,\d{3})+|\d+)"
    r"(?P<frac>\.\d+)?"
    r"\s*(?P<pct>%)?\s*$"
)


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
    match = _VALUE_RE.match(verbatim)
    if not match:
        return None
    digits = match.group("digits").replace(",", "")
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
    if quoted.approx:
        return {"match": False, "mode": "approx", "actual": actual, "abs_error": abs_error}
    return {"match": False, "mode": "mismatch", "actual": actual, "abs_error": abs_error}


_PATH_TOKEN = re.compile(
    r"\.(?P<name>[A-Za-z_][\w-]*)"      # .name
    r"|\[(?P<index>-?\d+)\]"            # [3] / [-1]
    r"|\[(?P<q>['\"])(?P<key>.*?)(?P=q)\]"  # ['key'] / [\"key\"]
)


def resolve_path(obj, path: str):
    """Resolve a minimal JSONPath-ish locator against loaded JSON.

    Supports ``$`` root, dotted names, integer indices, and quoted
    string keys — the forms the extraction instrument allows (e.g.
    ``$.results['20m'].f1``, ``$.tiers[0].conditions[2].f1_at_20m``).

    Args:
        obj: Parsed JSON object.
        path: Locator beginning with ``$``.

    Returns:
        The resolved value.

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
