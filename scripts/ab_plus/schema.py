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

from .config import KEY_POINT_MAX, KEY_POINT_MIN

# Allowed stances a key point can take toward the paper's argument.
RELEVANCE_STANCES: tuple[str, ...] = ("supports", "complicates", "extends")

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
