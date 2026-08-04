"""Tier-1 tests for the ``--at-era`` mode of ``scripts/validate_c4_extraction.py``.

The C4 extraction corpus is validated against source documents that the
verification programme itself keeps rewriting: ruling 1 adds dated-snapshot
banners, ruling 17 refreshes living documents in place, and every repair wave
edits mine documents *after* their claims were extracted. In working-tree mode
the validator then reports a ``git_blob`` mismatch and a verbatim failure for
every claim in the file, even though the extraction faithfully quoted the body
it was given.

``--at-era`` resolves the source body from each file's recorded ``git_blob``,
so verbatim spans are checked against the text the extractor actually read.
These tests pin both behaviours: the default must keep failing on drift (it is
the only signal that a document moved), and era mode must pass the same file
while reporting the move as a note.
"""

from __future__ import annotations

import json
import subprocess

import pytest

import scripts.validate_c4_extraction as vce


DOC_V1 = "\n".join([
    "# Findings",
    "",
    "The corpus contains 487 tiles at 384 px.",
    "",
])

DOC_V2 = "\n".join([
    "# Findings",
    "",
    "> **Last revised**: 2026-08-04 (banner added by a repair pass).",
    "",
    "The corpus contains 487 tiles at 384 px.",
    "",
])


def make_extraction(blob: str, *, lines: tuple[int, int]) -> dict:
    """An extraction file quoting DOC_V1's claim span at ``lines``."""
    return {
        "schema_version": "1.1",
        "extracted_at": "2026-08-04T00:00:00Z",
        "source_document": {
            "file": "results/findings.md",
            "git_blob": blob,
            "stratum": "hand-written",
        },
        "extractor": {"model": "claude-opus-5", "instrument_version": "1.2"},
        "claims": [
            {
                "claim_id": None,
                "source": {"lines": list(lines), "section": "Findings"},
                "claim_text": "The corpus contains 487 tiles at 384 px.",
                "values": [
                    {
                        "quantity": "tile count, Era 2 corpus",
                        "value_verbatim": "487",
                        "value_parsed": 487,
                        "unit": None,
                        "kind": "count",
                        "path": "len:$.features",
                        "method": "read",
                    }
                ],
                "anchor": {"file": "results/bounds.geojson", "path": None},
                "method": "read",
                "notes": None,
            }
        ],
    }


@pytest.fixture()
def drifted_repo(tmp_path, monkeypatch):
    """A tmp git repo whose source document moved after extraction.

    Returns ``(extraction_path, blob_v1)``. The document body is DOC_V2 in the
    working tree; the extraction file pins DOC_V1's blob and quotes DOC_V1's
    line numbers, exactly the shape a post-repair document produces.
    """
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    results = tmp_path / "results"
    results.mkdir()
    (results / "bounds.geojson").write_text(json.dumps({"features": [1] * 487}))

    doc = results / "findings.md"
    doc.write_text(DOC_V1, encoding="utf-8")
    blob_v1 = subprocess.run(
        ["git", "hash-object", "-w", "results/findings.md"],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    ).stdout.strip()

    # The repair pass: a banner is inserted, shifting the claim span down.
    doc.write_text(DOC_V2, encoding="utf-8")

    extraction = tmp_path / "extraction.json"
    extraction.write_text(json.dumps(make_extraction(blob_v1, lines=(3, 3))))

    monkeypatch.setattr(vce, "REPO_ROOT", tmp_path)
    return extraction, blob_v1


@pytest.mark.tier1
def test_working_tree_mode_still_fails_on_drift(drifted_repo):
    """The default must keep flagging drift — it is the only signal a doc moved."""
    extraction, blob_v1 = drifted_repo
    errors, notes = vce.validate_file(extraction, vce.build_validator())

    assert notes == []
    assert any("git_blob" in e for e in errors)
    assert any("not verbatim" in e for e in errors)
    assert blob_v1[:7] in " ".join(errors)


@pytest.mark.tier1
def test_at_era_mode_validates_the_extracted_body(drifted_repo):
    """The same file is clean when checked against the blob it was extracted from."""
    extraction, _ = drifted_repo
    errors, notes = vce.validate_file(extraction, vce.build_validator(), at_era=True)

    assert errors == []
    assert len(notes) == 1
    assert "source moved since extraction" in notes[0]


@pytest.mark.tier1
def test_at_era_rejects_an_unresolvable_blob(drifted_repo, tmp_path):
    """A blob missing from the object store is an error, not a silent pass."""
    extraction, _ = drifted_repo
    data = json.loads(extraction.read_text())
    data["source_document"]["git_blob"] = "0" * 40
    extraction.write_text(json.dumps(data))

    errors, _ = vce.validate_file(extraction, vce.build_validator(), at_era=True)

    assert len(errors) == 1
    assert "unresolvable" in errors[0]


@pytest.mark.tier1
def test_at_era_still_catches_a_genuine_verbatim_defect(drifted_repo):
    """Era mode relaxes *which* body is authoritative, never the verbatim rule."""
    extraction, _ = drifted_repo
    data = json.loads(extraction.read_text())
    data["claims"][0]["claim_text"] = "The corpus contains 999 tiles at 384 px."
    data["claims"][0]["values"][0]["value_verbatim"] = "999"
    extraction.write_text(json.dumps(data))

    errors, _ = vce.validate_file(extraction, vce.build_validator(), at_era=True)

    assert any("not verbatim" in e for e in errors)


@pytest.mark.tier1
def test_undrifted_file_passes_both_modes_without_notes(tmp_path, monkeypatch):
    """A stationary document behaves identically in both modes."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    results = tmp_path / "results"
    results.mkdir()
    (results / "bounds.geojson").write_text(json.dumps({"features": [1] * 487}))
    (results / "findings.md").write_text(DOC_V1, encoding="utf-8")
    blob = subprocess.run(
        ["git", "hash-object", "-w", "results/findings.md"],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    ).stdout.strip()

    extraction = tmp_path / "extraction.json"
    extraction.write_text(json.dumps(make_extraction(blob, lines=(3, 3))))
    monkeypatch.setattr(vce, "REPO_ROOT", tmp_path)

    for at_era in (False, True):
        errors, notes = vce.validate_file(extraction, vce.build_validator(),
                                          at_era=at_era)
        assert errors == [], f"at_era={at_era}: {errors}"
        assert notes == [], f"at_era={at_era}: {notes}"
