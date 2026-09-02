"""The AB+ entry data contract.

One schema, three consumers:

* the **proposer** LLM is forced to emit JSON matching ``ENTRY_SCHEMA`` (via the
  Workflow ``agent({schema})`` mechanism);
* the **checker** reads that JSON and verifies every quote against the source;
* the **renderer** turns it into the per-source markdown deliverable.

Keeping the schema in one place means the proposer prompt, the deterministic
check, and the output format can never silently drift apart.

The schema was locked with Shawn on 2026-06-10 after co-designing the first
entry by hand (``ab-plus/huang2023large.md``). The verifiability gradient is
encoded in *which* fields exist: quotes are structurally checkable; paraphrase,
summary, positioning, and relevance are interpretive (advisory verification
only).
"""

from __future__ import annotations

from typing import Any

from .config import KEY_POINT_MAX, KEY_POINT_MIN, SUMMARY_WORDS_MAX, SUMMARY_WORDS_MIN

# Allowed stances a key point can take toward the paper's argument.
RELEVANCE_STANCES: tuple[str, ...] = ("supports", "complicates", "extends")

# Verifier verdict vocabulary (per-point shape, map-reader-llm pilot 2026-08-30;
# enforced at render since 2026-09-03 — one tail verifier filed a fourth value
# and the renderer accepted it silently). NOT CHECKABLE is legal for a claim
# resting on external knowledge (verifier brief step 4(g)); it must carry a
# note and is never counted as SUPPORTED.
PER_POINT_VERDICTS: tuple[str, ...] = ("SUPPORTED", "OVERREACH", "UNSUPPORTED", "NOT CHECKABLE")
OVERALL_VERDICTS: tuple[str, ...] = ("PASS", "PASS-WITH-EDITS", "FAIL")

POSITIONING_MAX_SENTENCES: int = 3
"""Drafter-brief target for the positioning field. Advisory since the PI's
2026-09-03 ruling (Trier 2019: six sentences accepted because the verifier's
lead correction split into two claims): exceed it only when a verified
nuance would otherwise be lost, and say so in the agent report."""

# Overflow sidecar (2026-09-03, PI decision on the tail report): verified
# secondary material that did not fit the summary band. The COMPLETE copy —
# paraphrase paired with its verbatim span — stays in the gitignored working
# directory so paraphrase accuracy can be checked against the text; the
# renderer emits the paraphrase and its page anchor only, which is what the
# public repository carries.
OVERFLOW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["citekey", "items"],
    "properties": {
        "citekey": {"type": "string"},
        "generated": {"type": "string", "description": "ISO date the sidecar was structured."},
        "model": {"type": "string", "description": "Model ID requested for the structurer."},
        "source_notes": {
            "type": "string",
            "description": "Path of the free-form notes the items were structured from, if any.",
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paraphrase", "quote", "page_index"],
                "properties": {
                    "topic": {"type": "string", "description": "Short heading, optional."},
                    "paraphrase": {
                        "type": "string",
                        "description": "Our words; the only text the public entry carries.",
                    },
                    "quote": {
                        "type": "string",
                        "description": (
                            "VERBATIM span the paraphrase rests on; byte-checked like a "
                            "key-point quote; never rendered."
                        ),
                    },
                    "page_index": {"type": "integer", "minimum": 0},
                    "section": {"type": "string"},
                },
            },
        },
    },
}

# JSON Schema for the proposer's structured output. additionalProperties is
# False everywhere so the proposer cannot smuggle in unvalidated fields.
ENTRY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "citekey",
        "summary",
        "positioning",
        "key_points",
    ],
    "properties": {
        "citekey": {
            "type": "string",
            "description": "BibTeX citekey, exactly as in the .bib (e.g. Huang2023large).",
        },
        "register": {
            "type": "string",
            "description": (
                "Disciplinary register tag, e.g. 'Borrowed (NLP/ML)' or "
                "'IS-native (IP&M)'. Seeded from the synthesis doc."
            ),
        },
        "primary_gap": {
            "type": "string",
            "description": "The single best-fit gap theme, e.g. 'Gap 2 — self-correction limits'.",
        },
        "also_touches": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Other gap themes the source speaks to (may be empty).",
        },
        "summary": {
            "type": "string",
            "description": (
                "Advisory whole-paper synthesis, 300-500 words, in Claude's "
                "voice, with project intersections woven in (not padded). "
                "Interpretive: the verifier flags only claims the source "
                "contradicts."
            ),
        },
        "positioning": {
            "type": "string",
            "description": (
                "2-3 sentence interpretive annotation: where this source sits "
                "for the paper-in-progress."
            ),
        },
        "key_points": {
            "type": "array",
            "minItems": KEY_POINT_MIN,
            "maxItems": KEY_POINT_MAX,
            "description": (
                "Salience-ranked key points, capped by salience to the paper "
                "(not by what the source covers)."
            ),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "quote",
                    "page_index",
                    "paraphrase",
                    "relevance_gap",
                    "relevance_section",
                    "relevance_stance",
                ],
                "properties": {
                    "quote": {
                        "type": "string",
                        "description": (
                            "VERBATIM span copied from the extracted page text "
                            "(not from memory). Must pass the deterministic "
                            "checker. Keep it tight — the shortest span that "
                            "carries the point."
                        ),
                    },
                    "page_index": {
                        "type": "integer",
                        "minimum": 0,
                        "description": (
                            "0-based page index the quote is from (authoritative once verified)."
                        ),
                    },
                    "section": {
                        "type": "string",
                        "description": (
                            "Advisory section locator (e.g. '§3.3 Why does the performance...')."
                        ),
                    },
                    "paraphrase": {
                        "type": "string",
                        "description": (
                            "Faithful restatement of the quote in our words (verifier-checked)."
                        ),
                    },
                    "relevance_gap": {
                        "type": "string",
                        "description": "Which gap theme this point serves.",
                    },
                    "relevance_section": {
                        "type": "string",
                        "description": (
                            "Which paper section it feeds (e.g. '§2', '§5 design principles')."
                        ),
                    },
                    "relevance_stance": {
                        "type": "string",
                        "enum": list(RELEVANCE_STANCES),
                        "description": "How it bears on the argument.",
                    },
                },
            },
        },
        "framing_hook": {
            "type": ["object", "null"],
            "additionalProperties": False,
            "description": (
                "Optional single quote useful as rhetorical framing for the "
                "paragraph; NOT counted in the salience cap. null if none."
            ),
            "required": ["quote", "page_index", "note"],
            "properties": {
                "quote": {"type": "string"},
                "page_index": {"type": "integer", "minimum": 0},
                "section": {"type": "string"},
                "note": {"type": "string", "description": "Why it is a useful hook."},
            },
        },
    },
}


def iter_quotes(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Yield every quote-bearing element of an entry, uniformly.

    Returns a flat list of dicts, each with the keys ``role`` ('key_point' or
    'framing_hook'), ``index`` (position within its group), ``quote`` and
    ``page_index``. The checker iterates this so it never has to special-case
    the optional framing hook.

    Args:
        entry: A parsed AB+ entry conforming to :data:`ENTRY_SCHEMA`.

    Returns:
        List of quote descriptors in document order (key points, then hook).
    """
    quotes: list[dict[str, Any]] = []
    for i, kp in enumerate(entry.get("key_points", []) or []):
        quotes.append(
            {
                "role": "key_point",
                "index": i,
                "quote": kp.get("quote", ""),
                "page_index": kp.get("page_index"),
            }
        )
    hook = entry.get("framing_hook")
    if hook:
        quotes.append(
            {
                "role": "framing_hook",
                "index": 0,
                "quote": hook.get("quote", ""),
                "page_index": hook.get("page_index"),
            }
        )
    return quotes


_ABBREVIATIONS: frozenset[str] = frozenset(
    {"p", "pp", "e.g", "i.e", "cf", "vs", "al", "fig", "no", "vol", "ch", "sec", "eq", "approx"}
)


def _sentence_count(text: str) -> int:
    """Count sentence terminators, ignoring common abbreviations ("p. 171", "et al.").

    A terminator counts when followed by whitespace or end of text and the
    token before it is not a single letter or a listed abbreviation.
    """
    import re

    count = 0
    for m in re.finditer(r"(\S*?)([.!?])[\"'”’)\]]*(?:\s+|$)", text.strip()):
        token = m.group(1).rstrip(".").lower().lstrip("(\"'“‘[")
        if m.group(2) == "." and (len(token) == 1 or token in _ABBREVIATIONS):
            continue
        count += 1
    return count


def entry_warnings(entry: dict[str, Any]) -> list[str]:
    """Advisory checks that do not fail the deterministic path.

    Added 2026-09-03 (PI ruling): the summary word band and the positioning
    sentence target are targets, not gates — an entry may exceed them when a
    verified nuance would otherwise be lost — so they surface here as
    warnings the orchestrator reads, never as errors that block a render.

    Args:
        entry: A parsed AB+ entry.

    Returns:
        Human-readable warning strings; empty when the entry is in band.
    """
    warnings: list[str] = []
    words = len(str(entry.get("summary", "")).split())
    if words and not (SUMMARY_WORDS_MIN <= words <= SUMMARY_WORDS_MAX):
        warnings.append(
            f"summary is {words} words; band is {SUMMARY_WORDS_MIN}–{SUMMARY_WORDS_MAX} "
            "(exceed only where a verified nuance would otherwise be lost)"
        )
    sentences = _sentence_count(str(entry.get("positioning", "")))
    if sentences > POSITIONING_MAX_SENTENCES:
        warnings.append(
            f"positioning runs to {sentences} sentences; target is "
            f"{POSITIONING_MAX_SENTENCES} (accepted when nuance requires — say so in the "
            "report)"
        )
    return warnings


def validate_verdict(verdict: dict[str, Any]) -> list[str]:
    """Structural validation of a verifier verdict before it is rendered.

    Enforces the vocabulary in :data:`PER_POINT_VERDICTS` and
    :data:`OVERALL_VERDICTS` for the per-point shape. The vendored paper-b
    flag-list shape (``paraphrase_flags`` …) is accepted as-is. Returns
    problems rather than raising so the CLI can list them all.

    Args:
        verdict: The parsed verdict JSON.

    Returns:
        A list of problem strings; empty if the verdict is well formed.
    """
    problems: list[str] = []
    overall = verdict.get("overall")
    if overall is not None and overall not in OVERALL_VERDICTS:
        problems.append(f"overall {overall!r} not in {OVERALL_VERDICTS}")
    if "per_point" not in verdict:
        return problems
    points = verdict.get("per_point") or []
    if not isinstance(points, list):
        return problems + ["per_point is not a list"]
    for i, pp in enumerate(points):
        if not isinstance(pp, dict):
            problems.append(f"per_point[{i}] is not an object")
            continue
        v = pp.get("verdict")
        if v not in PER_POINT_VERDICTS:
            problems.append(f"per_point[{i}]: verdict {v!r} not in {PER_POINT_VERDICTS}")
        if v == "NOT CHECKABLE" and not str(pp.get("note", "")).strip():
            problems.append(f"per_point[{i}]: NOT CHECKABLE requires a note")
        idx = pp.get("index")
        if not (isinstance(idx, int) or isinstance(idx, str)):
            problems.append(f"per_point[{i}]: index must be an int or a field label")
    edits = verdict.get("edits")
    if edits is not None and not isinstance(edits, list):
        problems.append("edits is not a list")
    return problems


def validate_overflow(overflow: dict[str, Any]) -> list[str]:
    """Structural validation of an overflow sidecar (see :data:`OVERFLOW_SCHEMA`)."""
    problems: list[str] = []
    if not overflow.get("citekey"):
        problems.append("missing citekey")
    items = overflow.get("items")
    if not isinstance(items, list):
        return problems + ["items must be a list"]
    for i, it in enumerate(items):
        for fld in ("paraphrase", "quote"):
            if not str(it.get(fld, "")).strip():
                problems.append(f"items[{i}]: empty {fld}")
        if not isinstance(it.get("page_index"), int):
            problems.append(f"items[{i}]: page_index must be an int")
    return problems


def validate_entry(entry: dict[str, Any]) -> list[str]:
    """Lightweight structural validation for the deterministic (non-LLM) path.

    The proposer's output is already schema-enforced by the agent harness; this
    catches hand-authored or malformed entries before checking/rendering, and
    returns human-readable problems rather than raising, so the CLI can report
    them all at once.

    Args:
        entry: A parsed AB+ entry.

    Returns:
        A list of problem strings; empty if the entry is structurally sound.
    """
    problems: list[str] = []
    for field in ("citekey", "summary", "positioning", "key_points"):
        if not entry.get(field):
            problems.append(f"missing or empty required field: {field!r}")

    key_points = entry.get("key_points") or []
    n = len(key_points)
    if n and not (KEY_POINT_MIN <= n <= KEY_POINT_MAX):
        problems.append(
            f"key_points count {n} outside [{KEY_POINT_MIN}, {KEY_POINT_MAX}]"
        )

    for i, kp in enumerate(key_points):
        if not kp.get("quote"):
            problems.append(f"key_point[{i}]: empty quote")
        if kp.get("page_index") is None:
            problems.append(f"key_point[{i}]: missing page_index")
        stance = kp.get("relevance_stance")
        if stance and stance not in RELEVANCE_STANCES:
            problems.append(
                f"key_point[{i}]: relevance_stance {stance!r} not in {RELEVANCE_STANCES}"
            )
    return problems
