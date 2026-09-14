"""Tier-1 drift guards for the three 55-map leaderboard renderings.

``results/55map-leaderboard/55map-leaderboard-50m{,-standardised,-r2}.md``
are generated projections of the committed board JSONs, and the 2026-09-13
re-score scored the class ✗ on every structural criterion and found it in
neither compliance regime (``planning/interim-docs-review.md`` § 11.3–11.4).
This module is the guard half of closing that (checklist item 11b).

``gs-vs-55map-transfer.md`` is deliberately NOT covered here: the generator
map files it hand-written (rule ``hw-gs-55map-transfer``), it has no sidecar
JSON, and it therefore owes regime 1 — a banner and a changelog — which it
now carries.

The guard renders from the committed JSON in memory: no permutation test,
no Hungarian assignment, no detection file.
"""

from __future__ import annotations

import json

import pytest

from scripts.build_55map_leaderboard import (
    OUT_DIR,
    REFERENCES,
    RENDER_STAMP_RE,
    check_renderings,
    json_name_for,
    md_name_for,
    render_md,
)

pytestmark = pytest.mark.tier1

HEAD_LINES = 15


def _committed(reference: str) -> tuple[dict, str]:
    """Return (board JSON, board Markdown) for a reference."""
    payload = json.loads((OUT_DIR / json_name_for(reference)).read_text())
    text = (OUT_DIR / md_name_for(reference)).read_text()
    return payload, text


def _present() -> list[str]:
    """The references whose board JSON is committed."""
    return [r for r in REFERENCES if (OUT_DIR / json_name_for(r)).exists()]


def test_all_three_references_are_committed():
    """The audit counted four tables here; three are generated boards."""
    assert _present() == ["canonical", "standardised", "r2"]


def test_committed_renderings_have_no_drift():
    """``--check``: every committed .md equals a rendering of its JSON."""
    assert check_renderings() == 0


def test_each_rendering_carries_banner_generator_and_stamp():
    for reference in _present():
        _, text = _committed(reference)
        head = "\n".join(text.splitlines()[:HEAD_LINES])
        assert "GENERATED FILE" in head, reference
        assert "scripts/build_55map_leaderboard.py" in head, reference
        assert json_name_for(reference) in head, reference
        assert RENDER_STAMP_RE.search(head), reference
        assert "--check" in head, reference


def test_render_stamp_is_neutralised_but_a_moved_f1_is_not():
    payload, _ = _committed("canonical")
    at_a = render_md(payload, "aaaaaaaaa")
    at_b = render_md(payload, "bbbbbbbbb")
    assert at_a != at_b
    assert RENDER_STAMP_RE.sub("", at_a) == RENDER_STAMP_RE.sub("", at_b)

    tampered = json.loads(json.dumps(payload))
    tampered["cells"][0]["f1_50"] = 0.1234
    assert RENDER_STAMP_RE.sub("", render_md(tampered, "aaaaaaaaa")) != \
        RENDER_STAMP_RE.sub("", at_a)


def test_rendering_has_one_row_per_board_cell():
    """A rank table must not silently lose or gain a cell."""
    for reference in _present():
        payload, text = _committed(reference)
        rows = [ln for ln in text.splitlines() if ln.startswith("| ")]
        assert len(rows) - 1 == len(payload["cells"]), reference


def test_reference_is_named_in_the_title_not_inferred():
    """Three boards, three references: a swapped title would misattribute."""
    titles = {r: _committed(r)[1].splitlines()[0] for r in _present()}
    assert titles["canonical"].endswith("canonical GT @ 50 m")
    assert titles["standardised"].endswith("standardised reference @ 50 m")
    assert titles["r2"].endswith("reference r2 @ 50 m")


def test_hand_written_transfer_table_carries_a_revision_banner():
    """The fourth table in the directory owes regime 1, and has it."""
    text = (OUT_DIR / "gs-vs-55map-transfer.md").read_text()
    head = "\n".join(text.splitlines()[:HEAD_LINES])
    assert "**Last revised**" in head
    assert "## Changelog" in text
    assert "GENERATED FILE" not in text
