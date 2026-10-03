"""Tier-1: merge_recovery_meta refuses a cumulative "recovery" meta.

The 2026-05-02 merge summed an already-cumulative meta into its backup and
doubled the TH7 and IM metas (token-load audit §§ 3.2, 3.4)."""

from __future__ import annotations

import json
import sys

import pytest

from scripts import merge_recovery_meta
from scripts.merge_recovery_meta import CUMULATIVE_OVERLAP, refuse_cumulative


def _meta(items, run_id=None, tokens=0):
    return {"run_id": run_id,
            "execution_stats": {"completed_items": list(items), "items_processed": 0},
            "usage_stats": {"total_input_tokens": tokens}}


@pytest.mark.tier1
def test_a_cumulative_meta_is_refused():
    original = _meta(f"t{i}" for i in range(100))
    cumulative = _meta(f"t{i}" for i in range(103))
    with pytest.raises(SystemExit, match="cumulative"):
        refuse_cumulative(original, cumulative)


@pytest.mark.tier1
def test_a_recovery_only_meta_passes():
    original = _meta(f"t{i}" for i in range(100))
    refuse_cumulative(original, _meta(["t100", "t101", "t102"]))
    refuse_cumulative(_meta([]), _meta(["t1"]))  # nothing to compare: allowed


@pytest.mark.tier1
def test_the_overlap_boundary_is_strictly_more_than_half():
    # Exactly half is allowed and one more is refused, so a mutation of ``>``
    # to ``>=`` or a change of the threshold turns this red.
    assert CUMULATIVE_OVERLAP == 0.5
    original = _meta(f"t{i}" for i in range(100))
    refuse_cumulative(original, _meta(f"t{i}" for i in range(50)))
    with pytest.raises(SystemExit, match="cumulative"):
        refuse_cumulative(original, _meta(f"t{i}" for i in range(51)))


@pytest.mark.tier1
def test_a_genuine_recovery_repeating_forty_percent_passes():
    # A recovery that re-sent a large minority of tiles is still a recovery.
    original = _meta(f"t{i}" for i in range(100))
    refuse_cumulative(original, _meta([f"t{i}" for i in range(40)] + ["t200"]))


@pytest.mark.tier1
def test_a_shared_run_id_is_refused_whatever_the_overlap():
    # The automatic resume merge keeps the original's run_id; a recovery-only
    # meta has its own. A cumulative meta whose original recorded no completed
    # items still shares the run_id.
    with pytest.raises(SystemExit, match="run_id"):
        refuse_cumulative(_meta([], run_id="r1"), _meta(["t1"], run_id="r1"))
    refuse_cumulative(_meta([], run_id="r1"), _meta(["t1"], run_id="r2"))
    refuse_cumulative(_meta([], run_id=None), _meta(["t1"], run_id=None))


@pytest.mark.tier1
@pytest.mark.parametrize("where", ["original", "recovery"])
def test_a_verifier_meta_is_refused(where):
    tiles, cands = _meta(["t1"]), _meta(["candidate_00001"])
    pair = (cands, tiles) if where == "original" else (tiles, cands)
    with pytest.raises(SystemExit, match="verifier"):
        refuse_cumulative(*pair)


def _run_main(tmp_path, monkeypatch, original, recovery):
    backup, rec, out = (tmp_path / n for n in ("backup.json", "rec.json", "out.json"))
    backup.write_text(json.dumps(original))
    rec.write_text(json.dumps(recovery))
    monkeypatch.setattr(sys, "argv", ["merge_recovery_meta.py", "--backup", str(backup),
                                      "--recovery", str(rec), "--output", str(out)])
    merge_recovery_meta.main()
    return out


@pytest.mark.tier1
def test_main_refuses_a_cumulative_meta_and_writes_nothing(tmp_path, monkeypatch):
    # The wiring: main() calls the guard BEFORE it merges or writes.
    original = _meta((f"t{i}" for i in range(10)), run_id="r1", tokens=100)
    cumulative = _meta((f"t{i}" for i in range(11)), run_id="r1", tokens=110)
    with pytest.raises(SystemExit, match="cumulative"):
        _run_main(tmp_path, monkeypatch, original, cumulative)
    assert not (tmp_path / "out.json").exists()
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.tier1
def test_main_merges_a_genuine_recovery(tmp_path, monkeypatch):
    original = _meta((f"t{i}" for i in range(10)), run_id="r1", tokens=100)
    recovery = _meta(["t10"], run_id="r2", tokens=7)
    out = _run_main(tmp_path, monkeypatch, original, recovery)
    merged = json.loads(out.read_text())
    assert merged["usage_stats"]["total_input_tokens"] == 107
