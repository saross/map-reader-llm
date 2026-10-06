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


def test_fair_384_skips_the_annotation_note_on_a_re_run(tmp_path, monkeypatch) -> None:
    """Once annotated, ``fair-384-vs-512.json`` carries a top-level
    ``d42_annotation`` string beside its comparisons; a re-run (the dry run
    included) died on it with a KeyError instead of re-checking the rows."""
    result = {"f1_difference": {"p_value": 0.2, "mean": 0.01, "ci_lower": -0.01,
                                "ci_upper": 0.03},
              "precision_difference": {"p_value": 0.3},
              "recall_difference": {"p_value": 0.4}}
    row = {"f1_384": 0.7, "f1_512": 0.69, "det_384": 10, "det_512_raw": 11,
           "det_512_clipped": 10, "result": result}
    rerun = {"I4:deterministic": {**row, "result": dict(result)}}
    (tmp_path / "fair-384-vs-512-march-sweep.json").write_text(acp.json.dumps(rerun))
    (tmp_path / "fair-384-vs-512-e39-sweep.json").write_text(acp.json.dumps(rerun))
    monkeypatch.setattr(acp, "RE", tmp_path)
    data = {"I4:deterministic": {**row, "result": dict(result)},
            "d42_annotation": acp.NOTE}
    log = acp.fair_384(data)
    assert log[0] == "I4:deterministic: F1 p 0.2 -> 0.2"
    assert data["I4:deterministic"]["result"]["permutation_retest"]["f1_p"] == 0.2
    assert data["d42_annotation"] == acp.NOTE
