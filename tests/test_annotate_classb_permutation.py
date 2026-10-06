"""
Tests for ``scripts/annotate_classb_permutation.py`` (D42 class B annotation).

The script annotates committed artefacts in place, so it must write each one
back in the layout it was committed in; :func:`write_like` (factored out of
two duplicated blocks, PR #24 review finding 12) owns that. The annotation
itself was verified by re-running the script on the pre-annotation inputs
(``e7b32de0b^``) in a scratch tree: its writes equal the committed files
byte for byte.

Tier 1: synthetic files in ``tmp_path``; no committed data is read.
"""

from __future__ import annotations

import pytest

from scripts import annotate_classb_permutation as acp

pytestmark = pytest.mark.tier1


@pytest.mark.parametrize("raw", [
    '{\n  "a": 1\n}\n',   # indent 2, trailing newline
    '{\n "a": 1\n}',      # indent 1, none
    '{"a": 1}\n',         # compact
])
def test_write_like_keeps_the_committed_layout(tmp_path, raw) -> None:
    """Re-writing the unchanged value reproduces the committed text exactly."""
    path = tmp_path / "artefact.json"
    path.write_text(raw, encoding="utf-8")
    acp.write_like(path, raw, acp.load(path))
    assert path.read_text(encoding="utf-8") == raw


def test_write_like_adds_only_the_annotation(tmp_path) -> None:
    """An added key is the only difference from the committed text."""
    raw = '{\n "a": 1\n}\n'
    path = tmp_path / "artefact.json"
    path.write_text(raw, encoding="utf-8")
    data = acp.load(path)
    data["d42_annotation"] = "note"
    acp.write_like(path, raw, data)
    assert path.read_text(encoding="utf-8") == '{\n "a": 1,\n "d42_annotation": "note"\n}\n'
