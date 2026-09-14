"""Tier-1 drift guard for the five rendered register views.

``results/{runs,conditions,passes,analyses}-manifest.md`` and
``results/run-registry.md`` are generated projections of the committed
manifest JSONs, so under the PI ruling of 2026-09-11
(``docs/methodology/output-directory-standard.md`` § "Documents in
Revision Policy Scope") they owe a ``GENERATED FILE`` banner, a
source-commit stamp, and a ``--check`` drift guard exercised by a test —
not a hand changelog. This module is that test (checklist item 11b).

The rendering is a pure function of the committed JSON plus the stamp, so
the guard reads five JSON files and renders in memory: it recomputes no
metric, reads nothing under ``outputs/``, and cannot alter a register.
"""

from __future__ import annotations

import json

import pytest

from scripts.generate_post_run_report import (
    MANIFEST_FILES,
    REPO_ROOT,
    _STAMP_RE,
    _array_key,
    check_renderings,
    manifest_md_path,
    render_committed_manifests,
    render_manifest,
)

pytestmark = pytest.mark.tier1

HEAD_LINES = 15


def _head(manifest: str) -> str:
    """Return the first :data:`HEAD_LINES` lines of a committed rendering."""
    text = manifest_md_path(manifest).read_text(encoding="utf-8")
    return "\n".join(text.splitlines()[:HEAD_LINES])


def test_committed_renderings_have_no_drift():
    """Every committed .md equals a rendering of its committed JSON.

    Fails when a manifest JSON is rebuilt without its .md view being
    re-rendered, or when someone hand-edits a rendering.
    """
    drifted, missing = check_renderings()
    assert missing == []
    assert drifted == []


def test_every_register_has_a_rendering():
    assert set(render_committed_manifests("stub").keys()) == set(MANIFEST_FILES)
    for manifest in MANIFEST_FILES:
        assert manifest_md_path(manifest).exists()


def test_drift_check_ignores_the_source_commit_stamp():
    """A regeneration at a new commit is not drift.

    Without the neutralisation the guard would fire on every commit,
    which trains people to ignore it.
    """
    at_a = render_committed_manifests("aaaaaaaaa")
    at_b = render_committed_manifests("bbbbbbbbb")
    for manifest in MANIFEST_FILES:
        assert at_a[manifest] != at_b[manifest], "the stamp must actually be in the document"
        assert _STAMP_RE.sub("", at_a[manifest]) == _STAMP_RE.sub("", at_b[manifest])


def test_rendering_carries_banner_generator_and_source_commit():
    """The ruling's three document-side marks, per rendering."""
    for manifest, json_rel in MANIFEST_FILES.items():
        head = _head(manifest)
        assert "GENERATED FILE" in head
        assert "scripts/generate_post_run_report.py" in head
        assert json_rel in head
        assert _STAMP_RE.search(head), f"{manifest}: no source-commit stamp in the head"
        assert "--check-renderings" in head, f"{manifest}: banner does not name the guard"


def test_drift_check_catches_a_changed_row():
    """A content change must survive the stamp neutralisation.

    Mutates a copy of the runs manifest in memory — the committed files
    are never touched — and shows the neutralised renderings differ.
    """
    json_rel = MANIFEST_FILES["runs"]
    obj = json.loads((REPO_ROOT / json_rel).read_text(encoding="utf-8"))
    before = render_manifest("runs", obj, json_rel, "aaaaaaaaa")
    rows = obj[_array_key("runs")]
    assert rows, "the runs manifest must not be empty"
    rows[0] = dict(rows[0], corpus="tampered")
    after = render_manifest("runs", obj, json_rel, "aaaaaaaaa")
    assert _STAMP_RE.sub("", before) != _STAMP_RE.sub("", after)


def test_rendering_has_one_table_row_per_register_row():
    """A silent truncation is drift the banner cannot describe away."""
    for manifest, json_rel in MANIFEST_FILES.items():
        obj = json.loads((REPO_ROOT / json_rel).read_text(encoding="utf-8"))
        n_rows = len(obj[_array_key(manifest)])
        text = manifest_md_path(manifest).read_text(encoding="utf-8")
        # The label row starts "| " like a data row; the alignment row
        # ("|---|…") does not, so exactly one header line is counted.
        body = [ln for ln in text.splitlines() if ln.startswith("| ")]
        assert len(body) - 1 == n_rows, manifest
        assert f"{n_rows} row(s)" in text
