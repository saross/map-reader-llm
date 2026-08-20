"""
Tests for ``scripts/analyse_obs280_shared_reference.py`` (Session 132,
queue item 4).

Tier 1: the rank helper (the only non-trivial pure logic — a reversed
sort would silently invert every rank claim in the artefact) and the
``--out`` default, which is the whole point of defect D38.

Tier 2: the real committed artefacts still produce the registered
finding shape (divergence survives; four carried cells ranked on both
metrics) — committed-state insurance in the marking-campaign-gates
style.

Defect D38 (Session 137 audit, finding F17e): the tier-2 test used to
call ``main()`` with no argument, and ``main()`` wrote straight into the
tracked results directory — so every tier-2 run mutated a committed
artefact, and a stale-generator artefact made the comparison flaky. The
script now takes ``--out`` (defaulting to the committed path so a bare
run still reproduces the registered file), and the test below writes to
``tmp_path`` and COMPARES against the committed artefact instead of
overwriting it. Running the tier-2 suite must leave ``git status``
clean.
"""

import json
from pathlib import Path

import pytest

import scripts.analyse_obs280_shared_reference as mod


@pytest.mark.tier1
def test_rank_orders_best_first():
    """rank() must sort best-first; a reversed sort inverts every claim."""
    values = {"a": 0.1, "b": 0.9, "c": 0.5}
    assert mod.rank(values) == ["b", "c", "a"]


@pytest.mark.tier1
def test_default_out_is_the_committed_artefact():
    """A bare invocation must still reproduce the registered file.

    The D38 fix must not silently relocate the artefact: the default
    stays the committed path, and only an explicit ``--out`` moves it.
    """
    assert mod.DEFAULT_OUT == mod.STD_BASE / "obs280-shared-reference.json"
    assert mod.build_arg_parser().parse_args([]).out == mod.DEFAULT_OUT


@pytest.mark.tier1
def test_out_override_is_honoured_by_the_parser(tmp_path: Path):
    """``--out`` is what keeps a test run off the tracked tree."""
    target = tmp_path / "elsewhere" / "obs280.json"
    assert mod.build_arg_parser().parse_args(["--out", str(target)]).out == (
        target
    )


@pytest.mark.tier2
def test_real_artefacts_reproduce_registered_finding(tmp_path: Path):
    """Running against the committed board reproduces the item-4 result:
    the F1 and MCC leaders differ on the shared reference.

    Writes to ``tmp_path`` and compares against the committed artefact —
    the committed file is READ, never written (D38).
    """
    committed_path = mod.DEFAULT_OUT
    assert committed_path.is_file(), (
        f"committed artefact missing at {committed_path}"
    )
    committed_before = committed_path.read_text(encoding="utf-8")

    out_path = tmp_path / "obs280-shared-reference.json"
    mod.main(["--out", str(out_path)])

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["comparison"]["divergence_survives"] is True
    assert payload["comparison"]["f1_leader_standardised"] == "T03-k4"
    assert payload["comparison"]["mcc_leader_standardised"] == "IM-k3"
    assert len(payload["comparison"]["f1_rank_standardised"]) == 4

    # The committed artefact is current: a regeneration reproduces it
    # byte-for-byte. A mismatch means the committed file is a generator
    # vintage behind (the D38 staleness), not that the finding moved.
    assert out_path.read_text(encoding="utf-8") == committed_before, (
        "regenerating obs280-shared-reference.json no longer reproduces "
        "the committed artefact — re-run "
        "scripts/analyse_obs280_shared_reference.py and review the diff"
    )

    # And the run left the tracked tree untouched.
    assert committed_path.read_text(encoding="utf-8") == committed_before
