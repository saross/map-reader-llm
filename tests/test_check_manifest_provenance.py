#!/usr/bin/env python3
"""
Tier-1 tests for ``scripts/check_manifest_provenance.py`` (E86 remediation 4).

Two kinds of test live here:

1. **Hermetic unit tests** over synthetic registries written into ``tmp_path``,
   covering the state machine (current / stale / missing), the two check modes,
   the schema guards, and ``--restamp``.
2. **One committed-registry test** that runs ``--check-expected`` over the real
   ``inputs/provenance/manifest-dependencies.json``. It reads only small JSON
   and Markdown manifests, so it stays tier-1: it is the gate that turns red
   when a source manifest is re-selected under an old declaration, which is the
   E86 defect class.

The committed registry is deliberately NOT asserted clean under bare
``--check``: E86's staleness is documented and will not be repaired, so
``--check`` is expected to exit 1 for exactly one dependency. That expectation
is itself asserted, so a silent repair (or a silent second instance) fails.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import check_manifest_provenance as cmp_mod  # noqa: E402

pytestmark = pytest.mark.tier1

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_manifest_provenance.py"
COMMITTED_REGISTRY = REPO_ROOT / "inputs" / "provenance" / "manifest-dependencies.json"


# ---------------------------------------------------------------------------
# Fixtures: a synthetic repository with one artefact and one source
# ---------------------------------------------------------------------------


def _write_registry(root: Path, dependencies: list[dict]) -> Path:
    """Write a schema-valid registry into *root* and return its path."""
    path = root / "registry.json"
    path.write_text(
        json.dumps({
            "schema": cmp_mod.REGISTRY_SCHEMA,
            "created": "2026-09-13",
            "dependencies": dependencies,
        }, indent=1),
        encoding="utf-8",
    )
    return path


@pytest.fixture()
def synthetic(tmp_path: Path) -> dict:
    """A synthetic tree: one artefact, one source, anchored to the source."""
    (tmp_path / "inputs").mkdir()
    artefact = tmp_path / "inputs" / "derived.json"
    source = tmp_path / "inputs" / "source.json"
    artefact.write_text('["a"]\n', encoding="utf-8")
    source.write_text('["s1"]\n', encoding="utf-8")
    source_blob = cmp_mod.git_blob_hash(source)
    dep = {
        "id": "derived-from-source",
        "artefact": "inputs/derived.json",
        "declares": "derived from source.json",
        "expect": "CURRENT",
        "sources": [{
            "path": "inputs/source.json",
            "declared_blob": source_blob,
            "anchor_basis": "declaration-time",
            "declared_at": "2026-09-13",
        }],
    }
    registry = _write_registry(tmp_path, [dep])
    return {
        "root": tmp_path, "registry": registry,
        "artefact": artefact, "source": source, "dep": dep,
    }


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------


def test_unchanged_source_is_current(synthetic: dict) -> None:
    """A source whose bytes match the anchor reports CURRENT."""
    registry = cmp_mod.load_registry(synthetic["registry"])
    results = cmp_mod.evaluate_registry(registry, synthetic["root"])
    assert [r["state"] for r in results] == [cmp_mod.CURRENT]
    assert results[0]["as_expected"] is True


def test_changed_source_is_stale(synthetic: dict) -> None:
    """Re-selecting the source under the same name reports STALE."""
    synthetic["source"].write_text('["s2"]\n', encoding="utf-8")
    registry = cmp_mod.load_registry(synthetic["registry"])
    results = cmp_mod.evaluate_registry(registry, synthetic["root"])
    assert results[0]["state"] == cmp_mod.STALE
    assert results[0]["as_expected"] is False
    assert results[0]["sources"][0]["observed_blob"] != \
        results[0]["sources"][0]["declared_blob"]


def test_missing_source_is_its_own_state(synthetic: dict) -> None:
    """A deleted source is SOURCE-MISSING, not silently folded into STALE."""
    synthetic["source"].unlink()
    registry = cmp_mod.load_registry(synthetic["registry"])
    results = cmp_mod.evaluate_registry(registry, synthetic["root"])
    assert results[0]["state"] == cmp_mod.SOURCE_MISSING
    assert results[0]["sources"][0]["observed_blob"] is None


def test_missing_artefact_is_reported(synthetic: dict) -> None:
    """A deleted artefact is ARTEFACT-MISSING even when the source is current."""
    synthetic["artefact"].unlink()
    registry = cmp_mod.load_registry(synthetic["registry"])
    results = cmp_mod.evaluate_registry(registry, synthetic["root"])
    assert results[0]["state"] == cmp_mod.ARTEFACT_MISSING


def test_missing_source_outranks_stale(tmp_path: Path) -> None:
    """With two sources, one changed and one gone, the missing state wins."""
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs" / "derived.json").write_text("[]\n", encoding="utf-8")
    changed = tmp_path / "inputs" / "a.json"
    changed.write_text("[1]\n", encoding="utf-8")
    dep = {
        "id": "two-sources",
        "artefact": "inputs/derived.json",
        "expect": "CURRENT",
        "sources": [
            {"path": "inputs/a.json", "declared_blob": "0" * 40},
            {"path": "inputs/gone.json", "declared_blob": "1" * 40},
        ],
    }
    registry = cmp_mod.load_registry(_write_registry(tmp_path, [dep]))
    results = cmp_mod.evaluate_registry(registry, tmp_path)
    assert results[0]["state"] == cmp_mod.SOURCE_MISSING


def test_all_sources_must_be_current(tmp_path: Path) -> None:
    """A dependency is CURRENT only when every one of its sources is."""
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs" / "derived.json").write_text("[]\n", encoding="utf-8")
    good = tmp_path / "inputs" / "good.json"
    bad = tmp_path / "inputs" / "bad.json"
    good.write_text("[1]\n", encoding="utf-8")
    bad.write_text("[2]\n", encoding="utf-8")
    dep = {
        "id": "mixed",
        "artefact": "inputs/derived.json",
        "expect": "CURRENT",
        "sources": [
            {"path": "inputs/good.json",
             "declared_blob": cmp_mod.git_blob_hash(good)},
            {"path": "inputs/bad.json", "declared_blob": "f" * 40},
        ],
    }
    registry = cmp_mod.load_registry(_write_registry(tmp_path, [dep]))
    results = cmp_mod.evaluate_registry(registry, tmp_path)
    assert results[0]["state"] == cmp_mod.STALE
    states = {s["path"]: s["state"] for s in results[0]["sources"]}
    assert states["inputs/good.json"] == cmp_mod.CURRENT
    assert states["inputs/bad.json"] == cmp_mod.STALE


# ---------------------------------------------------------------------------
# Check modes
# ---------------------------------------------------------------------------


def _run(registry: Path, root: Path, *flags: str) -> int:
    """Invoke the module's ``main`` with an explicit registry and root."""
    return cmp_mod.main([
        "--registry", str(registry), "--root", str(root), *flags,
    ])


def test_default_mode_always_exits_zero(synthetic: dict) -> None:
    """The report mode is informational: a stale row does not fail it."""
    synthetic["source"].write_text('["changed"]\n', encoding="utf-8")
    assert _run(synthetic["registry"], synthetic["root"]) == 0


def test_check_fails_on_any_staleness(synthetic: dict) -> None:
    """``--check`` is the raw guard: any non-current declaration exits 1."""
    assert _run(synthetic["registry"], synthetic["root"], "--check") == 0
    synthetic["source"].write_text('["changed"]\n', encoding="utf-8")
    assert _run(synthetic["registry"], synthetic["root"], "--check") == 1


def test_check_expected_tolerates_a_declared_staleness(tmp_path: Path) -> None:
    """A registered, erratum-bearing STALE row keeps ``--check-expected`` green."""
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs" / "derived.json").write_text("[]\n", encoding="utf-8")
    (tmp_path / "inputs" / "source.json").write_text("[1]\n", encoding="utf-8")
    dep = {
        "id": "known-stale",
        "artefact": "inputs/derived.json",
        "expect": "STALE",
        "erratum": "E86",
        "sources": [{"path": "inputs/source.json", "declared_blob": "a" * 40}],
    }
    registry = _write_registry(tmp_path, [dep])
    assert _run(registry, tmp_path, "--check") == 1
    assert _run(registry, tmp_path, "--check-expected") == 0


def test_check_expected_fails_on_an_undeclared_change(synthetic: dict) -> None:
    """A new staleness against an ``expect: CURRENT`` row exits 1."""
    synthetic["source"].write_text('["changed"]\n', encoding="utf-8")
    assert _run(synthetic["registry"], synthetic["root"],
                "--check-expected") == 1


def test_check_expected_fails_when_a_stale_row_is_repaired(
    tmp_path: Path,
) -> None:
    """A row declared STALE that is now CURRENT also disagrees, and fails.

    Silent repair is as much a provenance surprise as silent drift: the
    erratum's own text would no longer describe the tree.
    """
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs" / "derived.json").write_text("[]\n", encoding="utf-8")
    source = tmp_path / "inputs" / "source.json"
    source.write_text("[1]\n", encoding="utf-8")
    dep = {
        "id": "repaired",
        "artefact": "inputs/derived.json",
        "expect": "STALE",
        "erratum": "E86",
        "sources": [{"path": "inputs/source.json",
                     "declared_blob": cmp_mod.git_blob_hash(source)}],
    }
    registry = _write_registry(tmp_path, [dep])
    assert _run(registry, tmp_path, "--check-expected") == 1


def test_json_mode_emits_parseable_results(synthetic: dict, capsys) -> None:
    """``--json`` prints a parseable object carrying every dependency."""
    _run(synthetic["registry"], synthetic["root"], "--json")
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["results"]) == 1
    assert payload["results"][0]["id"] == "derived-from-source"


# ---------------------------------------------------------------------------
# Schema guards
# ---------------------------------------------------------------------------


def test_wrong_schema_tag_is_rejected(tmp_path: Path) -> None:
    """An unexpected schema tag exits rather than guessing the format."""
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"schema": "other/9", "dependencies": []}),
                    encoding="utf-8")
    with pytest.raises(SystemExit):
        cmp_mod.load_registry(path)


def test_stale_expectation_without_an_erratum_is_rejected(
    tmp_path: Path,
) -> None:
    """A tolerated divergence must name the erratum that documents it."""
    dep = {
        "id": "undocumented",
        "artefact": "inputs/derived.json",
        "expect": "STALE",
        "sources": [{"path": "inputs/source.json", "declared_blob": "a" * 40}],
    }
    with pytest.raises(SystemExit):
        cmp_mod.load_registry(_write_registry(tmp_path, [dep]))


def test_unknown_expectation_value_is_rejected(tmp_path: Path) -> None:
    """Only CURRENT and STALE may be expected."""
    dep = {
        "id": "weird", "artefact": "a", "expect": "MAYBE",
        "sources": [{"path": "b", "declared_blob": "a" * 40}],
    }
    with pytest.raises(SystemExit):
        cmp_mod.load_registry(_write_registry(tmp_path, [dep]))


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    """Two rows with the same id would make the report ambiguous."""
    dep = {
        "id": "dup", "artefact": "a", "expect": "CURRENT",
        "sources": [{"path": "b", "declared_blob": "a" * 40}],
    }
    with pytest.raises(SystemExit):
        cmp_mod.load_registry(_write_registry(tmp_path, [dep, dict(dep)]))


def test_dependency_without_sources_is_rejected(tmp_path: Path) -> None:
    """A dependency that names no source anchors nothing."""
    dep = {"id": "empty", "artefact": "a", "expect": "CURRENT", "sources": []}
    with pytest.raises(SystemExit):
        cmp_mod.load_registry(_write_registry(tmp_path, [dep]))


def test_missing_registry_exits(tmp_path: Path) -> None:
    """An absent registry is an error, not an empty pass."""
    with pytest.raises(SystemExit):
        cmp_mod.load_registry(tmp_path / "nope.json")


# ---------------------------------------------------------------------------
# --restamp
# ---------------------------------------------------------------------------


def test_restamp_records_the_current_source_hash(synthetic: dict) -> None:
    """``--restamp`` makes a deliberate rebuild's declaration true again."""
    synthetic["source"].write_text('["rebuilt"]\n', encoding="utf-8")
    assert _run(synthetic["registry"], synthetic["root"], "--check") == 1
    assert _run(synthetic["registry"], synthetic["root"],
                "--restamp", "derived-from-source") == 0
    assert _run(synthetic["registry"], synthetic["root"], "--check") == 0
    written = json.loads(synthetic["registry"].read_text(encoding="utf-8"))
    src = written["dependencies"][0]["sources"][0]
    assert src["anchor_basis"] == "restamped"
    assert src["declared_blob"] == cmp_mod.git_blob_hash(synthetic["source"])


def test_restamp_rejects_an_unknown_id(synthetic: dict) -> None:
    """Re-stamping a non-existent dependency exits 1 rather than doing nothing."""
    assert _run(synthetic["registry"], synthetic["root"],
                "--restamp", "no-such-id") == 1


# ---------------------------------------------------------------------------
# The committed registry
# ---------------------------------------------------------------------------


def test_committed_registry_loads_and_schema_checks() -> None:
    """The real registry satisfies its own schema rules."""
    registry = cmp_mod.load_registry(COMMITTED_REGISTRY)
    assert registry["dependencies"], "registry declares no dependencies"


def test_committed_registry_matches_its_expectations() -> None:
    """Every declared provenance is in the state the registry says it is in.

    This is the E86 gate. It fails when a source manifest is re-selected under
    an old declaration (the defect) and equally when a declared-stale row is
    silently repaired.
    """
    registry = cmp_mod.load_registry(COMMITTED_REGISTRY)
    results = cmp_mod.evaluate_registry(registry, REPO_ROOT)
    disagreements = [
        (r["id"], r["expect"], r["state"]) for r in results
        if not r["as_expected"]
    ]
    assert disagreements == [], f"provenance disagreements: {disagreements}"


def test_committed_registry_flags_exactly_the_null_tile_manifest() -> None:
    """``--check`` flags the E86 instance and nothing else."""
    registry = cmp_mod.load_registry(COMMITTED_REGISTRY)
    results = cmp_mod.evaluate_registry(registry, REPO_ROOT)
    stale = [r["id"] for r in results if r["state"] != cmp_mod.CURRENT]
    assert stale == ["null-tiles-from-calibration"]


def test_every_stale_row_names_an_erratum() -> None:
    """No tolerated divergence may be undocumented."""
    registry = cmp_mod.load_registry(COMMITTED_REGISTRY)
    for dep in registry["dependencies"]:
        if dep.get("expect") == cmp_mod.STALE:
            assert dep.get("erratum"), f"{dep['id']} tolerates staleness silently"


def test_cli_check_expected_exits_zero_as_a_subprocess() -> None:
    """The documented command-line gate works when invoked as a process."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--check-expected"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr
