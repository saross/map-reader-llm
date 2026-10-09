"""
Tier-1 tests for ``scripts/lib_verify_dirs.py``: which verify directory a leg is read from.

The rule (PI decisions D55 Q4 and D58 Q8): a leg's probabilities are read from
``<leg>_repaired/`` when that directory holds ``probabilities.json``, and from
``<leg>/`` otherwise; ``MAP_READER_VERIFY_DIRS=fixed`` reads the leg as before.
These tests pin the three cases the rule distinguishes (repaired copy present,
absent, present but without probabilities), the before/after switch, and the
provenance record every caller writes beside what it derived. All synthetic;
nothing is read from the repository's data.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.lib_verify_dirs import (
    POLICY_ENV,
    repaired_sibling,
    resolve_leg,
    resolve_verify_dir,
    verify_dir_policy,
    verify_dir_provenance,
)

pytestmark = pytest.mark.tier1


def _write_probs(vdir: Path, probs: dict[str, float]) -> Path:
    """A minimal ``probabilities.json`` in ``vdir``; returns its path."""
    vdir.mkdir(parents=True, exist_ok=True)
    path = vdir / "probabilities.json"
    path.write_text(json.dumps({"results": {k: {"mound_probability": v}
                                            for k, v in probs.items()}}))
    return path


@pytest.fixture(autouse=True)
def _default_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test starts from the default policy, whatever the shell exports."""
    monkeypatch.delenv(POLICY_ENV, raising=False)


@pytest.fixture
def vroot(tmp_path: Path) -> Path:
    """A verifier cell holding one leg, ``verify_k5_arm2``."""
    _write_probs(tmp_path / "verify_k5_arm2", {"candidate_00000": 0.0})
    return tmp_path


def test_a_repaired_copy_with_probabilities_is_read(vroot: Path) -> None:
    _write_probs(vroot / "verify_k5_arm2_repaired", {"candidate_00000": 0.05})
    assert resolve_verify_dir(vroot, "verify_k5_arm2") == vroot / "verify_k5_arm2_repaired"


def test_without_a_repaired_copy_the_leg_is_read(vroot: Path) -> None:
    assert resolve_verify_dir(vroot, "verify_k5_arm2") == vroot / "verify_k5_arm2"


def test_a_repaired_copy_without_probabilities_is_not_read(vroot: Path) -> None:
    # SENTINEL: a half-written copy (its repair record, no probabilities) must
    # never be chosen over the leg it would replace.
    repaired = vroot / "verify_k5_arm2_repaired"
    repaired.mkdir()
    (repaired / "parse_repair.json").write_text("{}")
    assert resolve_verify_dir(vroot, "verify_k5_arm2") == vroot / "verify_k5_arm2"


def test_the_fixed_policy_reads_the_leg_even_beside_a_repaired_copy(
        vroot: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_probs(vroot / "verify_k5_arm2_repaired", {"candidate_00000": 0.05})
    assert resolve_verify_dir(vroot, "verify_k5_arm2", "fixed") == vroot / "verify_k5_arm2"
    monkeypatch.setenv(POLICY_ENV, "fixed")
    assert resolve_verify_dir(vroot, "verify_k5_arm2") == vroot / "verify_k5_arm2"
    monkeypatch.setenv(POLICY_ENV, "repaired")
    assert resolve_verify_dir(vroot, "verify_k5_arm2") == vroot / "verify_k5_arm2_repaired"


def test_an_unknown_policy_is_an_error_not_a_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(POLICY_ENV, "repiared")
    with pytest.raises(ValueError, match="repiared"):
        verify_dir_policy()
    assert verify_dir_policy("fixed") == "fixed"


def test_a_name_already_repaired_is_taken_as_given(vroot: Path) -> None:
    _write_probs(vroot / "verify_g3_rep2_repaired", {"candidate_00000": 0.5})
    assert (resolve_verify_dir(vroot, "verify_g3_rep2_repaired")
            == vroot / "verify_g3_rep2_repaired")


def test_resolve_leg_takes_one_path(vroot: Path) -> None:
    _write_probs(vroot / "verify_k5_arm2_repaired", {"candidate_00000": 0.05})
    leg = vroot / "verify_k5_arm2"
    assert resolve_leg(leg) == repaired_sibling(leg) == vroot / "verify_k5_arm2_repaired"


def test_provenance_of_a_plain_leg_has_no_repair_counts(vroot: Path) -> None:
    prov = verify_dir_provenance(vroot / "verify_k5_arm2", vroot)
    path = vroot / "verify_k5_arm2" / "probabilities.json"
    assert prov["dir"] == "verify_k5_arm2"
    assert prov["policy"] == "repaired"
    assert prov["probabilities_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert prov["n_results"] == 1
    for key in ("parse_error_rows", "repaired", "unrecovered", "reverified", "reverify_usd"):
        assert prov[key] is None, key
    assert prov["reverify_records"] == []


def test_provenance_of_a_repaired_copy_counts_repairs_and_reverification(
        vroot: Path) -> None:
    repaired = vroot / "verify_k5_arm2_repaired"
    _write_probs(repaired, {"candidate_00000": 0.01, "candidate_00001": 0.2})
    (repaired / "parse_repair.json").write_text(json.dumps({
        "n_parse_error_rows": 3,
        "changed": [{"key": "candidate_00001"}],
        "unrecovered": [{"key": "candidate_00000"}, {"key": "candidate_00002"}],
    }))
    (repaired / "reverify-2026-10-08.json").write_text(json.dumps({"rows": [
        {"key": "candidate_00000", "cost_usd": 0.001129},
        {"key": "candidate_00002", "cost_usd": 0.0011},
    ]}))
    prov = verify_dir_provenance(repaired, vroot)
    assert prov["dir"] == "verify_k5_arm2_repaired"
    assert (prov["parse_error_rows"], prov["repaired"], prov["unrecovered"]) == (3, 1, 2)
    assert prov["reverified"] == 2
    assert prov["reverify_usd"] == pytest.approx(0.002229)
    assert prov["reverify_records"] == ["verify_k5_arm2_repaired/reverify-2026-10-08.json"]


def test_provenance_outside_the_root_keeps_the_path(vroot: Path, tmp_path: Path) -> None:
    prov = verify_dir_provenance(vroot / "verify_k5_arm2", tmp_path / "elsewhere")
    assert prov["dir"] == str(vroot / "verify_k5_arm2")
