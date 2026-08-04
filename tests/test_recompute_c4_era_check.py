"""Tier-1 tests for the redesigned per-claim ``era_check`` (ruling 14).

Three wave-7 blind passes independently indicted the previous design, which
resolved anchors at the source document's FILE era:

* P1 — because extraction runs at HEAD, the recorded blob is usually the
  current blob, so the "era" commit is effectively HEAD and every anchor
  re-resolves to today. It stamped ``faithful: false`` on all 75 rows of a
  partition whose true defect count was zero.
* P2 — where a later edit (a banner) last touched the file, the file era lands
  on that edit, which sat *inside* the campaign that moved the very artefacts
  being checked. Sixteen false stamps.
* P4 — the check was gated on a dated FILENAME, so it fired on none of its 24
  rows while 22 verdicts turned on era-faithfulness established by hand.

The redesign blames the claim's own line range and resolves at the commit that
last wrote that span. These tests pin the behaviours that were wrong.
"""

from __future__ import annotations

import json
import subprocess

import pytest

import scripts.recompute_c4_claims as rc


def git(tmp_path, *args):
    return subprocess.run(["git", *args], cwd=tmp_path, capture_output=True,
                          text=True, check=True).stdout.strip()


@pytest.fixture()
def two_era_repo(tmp_path, monkeypatch):
    """A document whose BODY and BANNER were written in different eras.

    Era 1 writes the body quoting an artefact value of 0.771 and commits both.
    Era 2 moves the artefact to 0.7745 (a recovery campaign). Era 3 prepends a
    banner, so the file's newest commit — and therefore its blob era — is era 3,
    while the body span still belongs to era 1.
    """
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    results = tmp_path / "results"
    results.mkdir()
    art = results / "evaluation.json"
    doc = results / "findings-2026-04-21.md"

    art.write_text(json.dumps({"f1": 0.771}))
    doc.write_text("# Findings\n\nHeadline F1 is 0.771 at 50 m.\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "era1: body written")
    era1 = git(tmp_path, "rev-parse", "HEAD")

    art.write_text(json.dumps({"f1": 0.7745}))
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "era2: recovery moves the artefact")

    doc.write_text("> **Superseded**: see the recovery.\n\n"
                   "# Findings\n\nHeadline F1 is 0.771 at 50 m.\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "era3: banner added")
    era3 = git(tmp_path, "rev-parse", "HEAD")

    blob = git(tmp_path, "rev-parse", "HEAD:results/findings-2026-04-21.md")
    monkeypatch.setattr(rc, "REPO_ROOT", tmp_path)
    rc._era_commit_cache.clear()
    rc._era_tree_cache.clear()
    rc._claim_era_cache.clear()
    rc._json_cache.clear()
    return tmp_path, blob, era1, era3


def body_claim() -> dict:
    """The body span, which sits at line 5 once the banner is prepended."""
    return {
        "claim_id": None,
        "source": {"lines": [5, 5], "section": "Findings"},
        "claim_text": "Headline F1 is 0.771 at 50 m.",
        "values": [{"quantity": "headline F1 at 50 m", "value_verbatim": "0.771",
                    "value_parsed": 0.771, "unit": None, "kind": "metric",
                    "path": "$.f1", "method": "read"}],
        "anchor": {"file": "results/evaluation.json", "path": "$.f1"},
        "method": "read",
        "notes": None,
    }


@pytest.mark.tier1
def test_era_check_resolves_at_the_claim_span_not_the_file_blob(two_era_repo):
    """The body was faithful when written; the artefact moved afterwards."""
    tmp_path, blob, era1, era3 = two_era_repo
    era = {"doc": "results/findings-2026-04-21.md", "blob": blob,
           "snapshot": True}

    (row,) = rc.process_claim("b", 0, body_claim(), era=era)

    assert row["status"] == "MISMATCH"          # against today's artefact
    assert row["era_check"]["faithful"] is True  # but faithful at its own era
    assert row["era_check"]["era_basis"] == "claim-span"
    assert era1.startswith(row["era_check"]["commit"])


@pytest.mark.tier1
def test_era_check_reports_disagreement_with_the_file_era(two_era_repo):
    """The file era is era 3; the claim era is era 1. That gap is signal."""
    tmp_path, blob, era1, era3 = two_era_repo
    era = {"doc": "results/findings-2026-04-21.md", "blob": blob,
           "snapshot": True}

    (row,) = rc.process_claim("b", 0, body_claim(), era=era)
    check = row["era_check"]

    assert check["era_disagreement"] is True
    assert era3.startswith(check["file_era"])
    assert check["file_era"] != check["commit"]


@pytest.mark.tier1
def test_file_era_alone_would_have_called_the_claim_unfaithful(two_era_repo):
    """Pin the old defect: at the FILE era the artefact already had moved.

    This is the P1/P2 failure reproduced directly — resolving at the file's
    blob era yields today's value and would stamp a faithful claim as a
    document defect.
    """
    tmp_path, blob, era1, era3 = two_era_repo

    at_file_era, _ = rc.era_resolve(era3, "results/evaluation.json", "$.f1")
    at_claim_era, _ = rc.era_resolve(era1, "results/evaluation.json", "$.f1")

    assert at_file_era == 0.7745   # the moved value — a false defect
    assert at_claim_era == 0.771   # what the document actually quoted


@pytest.mark.tier1
def test_era_check_runs_on_undated_documents(two_era_repo):
    """Ruling 14: presentation class is advisory, not a gate.

    P4's partition had the check fire on zero rows because the filenames
    carried no date.
    """
    tmp_path, blob, era1, era3 = two_era_repo
    git(tmp_path, "mv", "results/findings-2026-04-21.md", "results/report.md")
    git(tmp_path, "commit", "-q", "-m", "rename to an undated filename")
    new_blob = git(tmp_path, "rev-parse", "HEAD:results/report.md")
    rc._era_commit_cache.clear()
    rc._claim_era_cache.clear()

    assert rc.is_snapshot_doc("results/report.md") is False
    era = {"doc": "results/report.md", "blob": new_blob, "snapshot": False}
    (row,) = rc.process_claim("b", 0, body_claim(), era=era)

    assert "era_check" in row, "the check must not be gated on a dated filename"
    assert row["era_check"]["presentation_class"] == "undated"


@pytest.mark.tier1
def test_anchor_absent_at_era_is_distinguished_from_disagreement(two_era_repo):
    """An artefact created after the span was written is not a doc defect.

    The anchor must exist TODAY (or the primary status is UNRESOLVED and the
    check never runs) but not at the claim's era. Collapsing that into a plain
    error is what let a not-yet-existent artefact read as a document defect.
    """
    tmp_path, blob, era1, era3 = two_era_repo
    late = tmp_path / "results" / "late.json"
    late.write_text(json.dumps({"f1": 0.999}))
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "era4: a later artefact appears")
    rc._era_commit_cache.clear()
    rc._era_tree_cache.clear()
    rc._claim_era_cache.clear()
    rc._json_cache.clear()

    claim = body_claim()
    claim["anchor"] = {"file": "results/late.json", "path": "$.f1"}
    era = {"doc": "results/findings-2026-04-21.md", "blob": blob,
           "snapshot": True}

    (row,) = rc.process_claim("b", 0, claim, era=era)

    assert row["status"] == "MISMATCH"      # 0.771 quoted vs 0.999 today
    assert row["era_check"]["status"] == "ANCHOR-ABSENT-AT-ERA"
    assert "faithful" not in row["era_check"]
