"""Tier-1 tests for ``scripts/build_archive_ledger.py`` (PI rulings D38-D39).

The archive ledger prices the archive's billed executions for the project
total. Each test builds a throwaway git repository (an archive, a
classification, a register and empty tier evidence) so the generator's rules
are pinned without the real archive:

- every usage-bearing archive meta must be classified, and only those;
- a duplicate or snapshot names a tracked twin and carries no cost;
- a REAL meta must be cited by the register row it names;
- a superseded meta is priced from its own usage; a partial one is a floor;
- zero-usage metas are counted by subtree for D39's invoice residual.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.build_archive_ledger import LedgerError, build, records_usage, render
from scripts.lib_pass_cost import PassCoster

pytestmark = pytest.mark.tier1

#: 1 M input (none cached), 100 k output, 200 k thinking on gemini-3-flash-preview:
#: standard US$1.40, flex US$0.70.
USAGE = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
         "total_output_tokens": 100_000, "total_thoughts_tokens": 200_000,
         "total_tokens": 1_300_000, "n_responses_with_usage": 10}
ZERO = {"total_input_tokens": 0, "total_output_tokens": 0, "total_tokens": 0}


def _write(root: Path, rel: str, doc: dict) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding="utf-8")
    return rel


def _meta(root: Path, rel: str, usage: dict = USAGE) -> str:
    return _write(root, rel, {"configuration": {"model": "gemini-3-flash-preview"},
                              "usage_stats": usage,
                              "timestamp": {"start": "2026-05-20T10:00:00+00:00",
                                            "end": "2026-05-20T11:00:00+00:00",
                                            "duration_seconds": 3600.0}})


@pytest.fixture
def repo(tmp_path: Path):
    """A git repository with empty evidence; returns (root, coster factory)."""
    ev = tmp_path / "ev"
    for name, doc in (("billing.json", {"months_covered": [], "intervals": {}, "days": {}}),
                      ("logs.json", {"directories": {}}),
                      ("att.json", {"attestations": []}),
                      ("pub.json", {"entries": {}})):
        _write(ev, name, doc)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    _write(tmp_path, "results/run-registry.json", {"registry": []})

    def coster() -> PassCoster:
        return PassCoster(billing_path=ev / "billing.json", logs_path=ev / "logs.json",
                          attestations_path=ev / "att.json", overrides_path=ev / "pub.json")

    return tmp_path, coster


def _commit(root: Path, entries: list[dict], rows: list[dict] | None = None) -> None:
    _write(root, "data/pricing/archive-classification.json",
           {"schema": "archive-classification/1", "entries": entries})
    _write(root, "results/passes-manifest.json",
           {"generated_at": "t", "generator_version": "v", "schema_version": "1.0",
            "passes": rows or []})
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)


def test_records_usage_is_d38s_filter() -> None:
    assert records_usage({"usage_stats": USAGE})
    assert not records_usage({"usage_stats": ZERO})
    assert records_usage({"usage_stats": ZERO, "cost_estimate": {"total_cost_usd": 0.2}})


def test_a_superseded_meta_is_priced_and_a_partial_one_is_a_floor(repo) -> None:
    root, coster = repo
    whole = _meta(root, "archive/old/run_1/a.meta.json")
    part = _meta(root, "archive/old/run_2/a.meta.json")
    _meta(root, "archive/old/run_3/batch.meta.json", usage=ZERO)
    _commit(root, [{"meta": whole, "class": "SUPERSEDED", "reason": "r"},
                   {"meta": part, "class": "SUPERSEDED", "partial": True, "reason": "r"}])
    doc = build(root, coster=coster())
    by = {e["meta"]: e for e in doc["entries"]}
    # No tier evidence at all: both real-time tiers stay possible, so the
    # whole meta publishes the higher (standard) and the partial one its floor.
    assert by[whole]["cost_basis"] == "audited-upper-bound"
    assert by[whole]["cost_usd"] == pytest.approx(1.4)
    assert by[part]["cost_basis"] == "audited-lower-bound"
    assert by[part]["cost_usd"] < by[whole]["cost_usd"]
    assert doc["totals"]["SUPERSEDED"]["metas"] == 2
    assert doc["totals"]["SUPERSEDED"]["partial"] == 1
    assert doc["zero_usage_metas_by_subtree"] == {"archive/old": 1}
    assert render(doc) == render(build(root, coster=coster()))  # deterministic


def test_an_unclassified_or_misclassified_meta_stops_the_build(repo) -> None:
    root, coster = repo
    a = _meta(root, "archive/old/run_1/a.meta.json")
    b = _meta(root, "archive/old/run_2/b.meta.json")
    z = _meta(root, "archive/old/run_3/z.meta.json", usage=ZERO)
    _commit(root, [{"meta": a, "class": "SUPERSEDED", "reason": "r"}])
    with pytest.raises(LedgerError, match="1 usage-bearing meta"):
        build(root, coster=coster())
    _commit(root, [{"meta": a, "class": "SUPERSEDED", "reason": "r"},
                   {"meta": b, "class": "SUPERSEDED", "reason": "r"},
                   {"meta": z, "class": "SUPERSEDED", "reason": "r"}])
    with pytest.raises(LedgerError, match="not usage-bearing"):
        build(root, coster=coster())


def test_a_duplicate_needs_a_tracked_twin_and_costs_nothing(repo) -> None:
    root, coster = repo
    copy = _meta(root, "archive/old/run_1/a.meta.json")
    twin = _meta(root, "outputs/live/run_1/a.meta.json")
    _commit(root, [{"meta": copy, "class": "DUPLICATE", "twin": twin, "reason": "r"}])
    entry = build(root, coster=coster())["entries"][0]
    assert entry["cost_usd"] is None and entry["cost_basis"] == "not-separate-spend"
    _commit(root, [{"meta": copy, "class": "DUPLICATE", "twin": "outputs/gone.meta.json",
                    "reason": "r"}])
    with pytest.raises(LedgerError, match="twin"):
        build(root, coster=coster())


def test_a_real_meta_must_be_cited_by_its_register_row(repo) -> None:
    root, coster = repo
    meta = _meta(root, "archive/calib/pool/run_1/a.meta.json")
    row = {"pass_id": "r::pool::run1", "cost_usd": 1.4, "cost_basis": "audited",
           "provenance": {"source_files": [meta]}}
    _commit(root, [{"meta": meta, "class": "REAL", "register_pass_id": "r::pool::run1",
                    "reason": "r"}], rows=[row])
    entry = build(root, coster=coster())["entries"][0]
    assert entry["cost_basis"] == "in-register" and entry["register_cost_usd"] == 1.4
    _commit(root, [{"meta": meta, "class": "REAL", "register_pass_id": "r::pool::run1",
                    "reason": "r"}], rows=[{**row, "provenance": {"source_files": []}}])
    with pytest.raises(LedgerError, match="does not cite it"):
        build(root, coster=coster())
