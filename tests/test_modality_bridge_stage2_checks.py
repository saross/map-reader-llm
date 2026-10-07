"""
Tests for ``scripts/modality_bridge_stage2_checks.py`` — Stage 2 audit fixes A2, A5, A6.

- **A5** (pass metas): every pass file's ``.meta.json`` must record the arm's
  model, temperature, thinking level and cached share; a fragment counts
  like a main pass.
- **A6** (review band): a union outside ±15 % of its guide is flagged by
  ``estimate`` and refused by ``band`` (the launcher's ``verify`` gate)
  until the operator sets ``BAND_OK=1``.
- **A2** (parse repair): the two rows the audit found booked as 0.0 in a
  committed batch leg (``verify_k5_arm1_replicate-batch-2026-09-20``,
  ``candidate_06537`` and ``candidate_08272``: valid JSON followed by a
  stray ``}``) are recovered by the real-time path's repair as 0.2 and 0.05;
  the leg directory is left untouched and the repaired leg is written beside
  it with a record of what changed.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import modality_bridge_stage2_checks as c2  # noqa: E402

pytestmark = pytest.mark.tier1

#: The audit's two examples, verbatim from the committed leg's
#: batch_results.jsonl (outputs/gemini37-image-55map-2026-09-13/verifier/
#: g384_ov192_55map_g37img/verify_k5_arm1_replicate-batch-2026-09-20).
TEXT_06537 = (
    '{\n    "best_alternative": "A contour feature or natural micro-relief.",\n'
    '    "alternative_evidence": "The orange-brown mark is located directly on a steep '
    'slope between the 500m contour line and a higher ridge. It lacks a distinct central '
    'circle or geometric survey marker (triangle/square).",\n    "reasoning": "While there '
    'is a small orange-brown cluster, it does not exhibit the clear, symmetrical '
    '\'sunburst\' pattern of outward-radiating rays typical of a burial mound. Its '
    'placement on a steep slope is also less common for kurgans, which are typically '
    'situated on prominent ridges or flat plateaus. The mark is more likely a minor '
    'topographic detail or a printing artifact related to the contour lines.",\n'
    '    "mound_probability": 0.2\n}\n}')
TEXT_08272 = (
    '{\n    "best_alternative": "A combination of contour line features and text/numbering '
    'artefacts.",\n    "alternative_evidence": "The central area contains brown/orange '
    'markings that resemble the Cyrillic letters \'Гл\' or \'Гп\' and the number \'10\'. '
    'These are situated within a complex set of contour lines and hachures (slope '
    'indicators) associated with a nearby road embankment and natural terrain.",\n'
    '    "reasoning": "The symbol lacks the characteristic \'sunburst\' or \'gear\' pattern '
    'of outward-radiating rays. Instead, the brown marks appear to be alphanumeric labels '
    'or elevation indicators (\'10\') placed near a contour line. The presence of hachures '
    'pointing toward the road below further explains the linear marks in the vicinity as '
    'slope indicators rather than a burial mound.",\n    "mound_probability": 0.05\n}\n}')


# ---------------------------------------------------------------------------
# A2: parse repair
# ---------------------------------------------------------------------------


def test_plain_json_fails_on_the_audit_examples() -> None:
    """The batch parser's json.loads fails on both (why they were booked 0.0)."""
    for text in (TEXT_06537, TEXT_08272):
        with pytest.raises(json.JSONDecodeError, match="Extra data"):
            json.loads(text)


def test_repair_recovers_the_audit_examples() -> None:
    assert c2.repair_text(TEXT_06537)["mound_probability"] == 0.2
    assert c2.repair_text(TEXT_08272)["mound_probability"] == 0.05
    assert c2.repair_text("```json\n" + TEXT_06537 + "\n```")["mound_probability"] == 0.2


def _row(key: str, text: str) -> dict:
    return {"key": key, "response": {"candidates": [{"content": {"parts": [{"text": text}]}}]}}


def _leg(tmp_path: Path) -> Path:
    leg = tmp_path / "verify_g3"
    leg.mkdir()
    err = {"mound_probability": 0.0, "reasoning": "PARSE_ERROR: Extra data",
           "best_alternative": "", "alternative_evidence": ""}
    results = {
        "candidate_00000": {"mound_probability": 0.9, "reasoning": "fine",
                            "best_alternative": "", "alternative_evidence": ""},
        "candidate_00001": dict(err),
        "candidate_00002": dict(err),
        "candidate_00003": dict(err),
    }
    (leg / "probabilities.json").write_text(json.dumps(
        {"version": "1.0", "mode": "batch", "iterations": 1, "results": results}))
    rows = [_row("candidate_00000", '{"mound_probability": 0.9}'),
            _row("candidate_00001", TEXT_06537), _row("candidate_00002", TEXT_08272),
            _row("candidate_00003", "this is not JSON at all")]
    (leg / "batch_results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return leg


def test_repair_leg_writes_beside_the_leg_and_records_every_row(tmp_path: Path) -> None:
    leg = _leg(tmp_path)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in leg.iterdir()}
    rec = c2.repair_leg(leg)
    # The leg directory is never written.
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in leg.iterdir()} == before
    out = tmp_path / "verify_g3_repaired"
    probs = json.loads((out / "probabilities.json").read_text())["results"]
    assert probs["candidate_00001"]["mound_probability"] == 0.2
    assert probs["candidate_00002"]["mound_probability"] == 0.05
    # An unrecoverable row is removed, so it is a missing candidate (scoring
    # refuses until it is re-verified) rather than a silent 0.0.
    assert "candidate_00003" not in probs
    assert probs["candidate_00000"]["mound_probability"] == 0.9
    assert rec["n_parse_error_rows"] == 3 and rec["n_results_written"] == 3
    assert [(c["key"], c["before"], c["after"]) for c in rec["changed"]] == [
        ("candidate_00001", 0.0, 0.2), ("candidate_00002", 0.0, 0.05)]
    assert [u["key"] for u in rec["unrecovered"]] == ["candidate_00003"]
    record = json.loads((out / "parse_repair.json").read_text())
    assert record["source_probabilities_sha256"] == before["probabilities.json"]
    assert record["source_batch_results_sha256"] == before["batch_results.jsonl"]
    # The CLI exits 1 while a row stays unrecovered.
    assert c2.main(["repair", str(leg), "--out-dir", str(tmp_path / "again")]) == 1


def test_an_unescaped_quote_is_not_repaired() -> None:
    """The committed legs' seven unrepairable rows: a bare quote inside a string."""
    bad = ('{\n "reasoning": "small vegetation marks (\'"\'), but no mound",\n'
           ' "mound_probability": 0.0\n}')
    with pytest.raises(json.JSONDecodeError):
        json.loads(bad)
    with pytest.raises(ValueError):
        c2.repair_text(bad)


def test_repair_leg_with_no_parse_errors_changes_nothing(tmp_path: Path) -> None:
    leg = tmp_path / "verify_g37"
    leg.mkdir()
    results = {"candidate_00000": {"mound_probability": 0.4, "reasoning": "ok"}}
    (leg / "probabilities.json").write_text(json.dumps({"results": results}))
    (leg / "batch_results.jsonl").write_text(json.dumps(_row("candidate_00000", "{}")) + "\n")
    rec = c2.repair_leg(leg)
    assert rec["changed"] == [] and rec["unrecovered"] == []
    out = json.loads((tmp_path / "verify_g37_repaired" / "probabilities.json").read_text())
    assert out["results"] == results
    assert c2.main(["repair", str(leg), "--out-dir", str(tmp_path / "x")]) == 0


# ---------------------------------------------------------------------------
# A5: pass metas
# ---------------------------------------------------------------------------


def _meta(model: str, temperature: float, thinking: str, inp: int, cached: int) -> dict:
    return {"configuration": {"model": model, "temperature": temperature,
                              "thinking_level": thinking},
            "usage_stats": {"total_input_tokens": inp, "total_cached_tokens": cached,
                            "cached_share": cached / inp if inp else 0.0}}


def _arm(out: Path, arm: str, meta: dict, fragment_meta: dict | None = None) -> None:
    """Lay out an arm's passes (one fragment on pass 1) with metas."""
    spec = c2.ARMS[arm]
    for n in range(1, spec.k + 1):
        name = f"detections_{spec.version}_run{n:02d}"
        d = out / arm / spec.version / f"run_{n}"
        d.mkdir(parents=True)
        (d / f"{name}.geojson").write_text('{"features": [], "processed_tiles": []}')
        (d / f"{name}.meta.json").write_text(json.dumps(meta))
    fd = out / arm / "recovery_rd1" / spec.version / "run_1"
    fd.mkdir(parents=True)
    name = f"detections_{spec.version}_run01"
    (fd / f"{name}.geojson").write_text('{"features": [], "processed_tiles": []}')
    (fd / f"{name}.meta.json").write_text(json.dumps(fragment_meta or meta))


G3_CACHED = _meta(c2.G3_MODEL, 0.7, "minimal", 27987960, 26434782)  # a landed g3-image pass


def test_metas_pass_for_what_each_arm_sends(tmp_path: Path) -> None:
    _arm(tmp_path, "g3-image", G3_CACHED)
    _arm(tmp_path, "g3-image-temp1", _meta(c2.G3_MODEL, 1.0, "minimal", 1000, 944))
    _arm(tmp_path, "g37-image", _meta(c2.G37_MODEL, 0.7, "low", 1000, 807))
    _arm(tmp_path, "g37-text", _meta(c2.G37_MODEL, 0.7, "low", 1000, 0))
    for arm in ("g3-image", "g3-image-temp1", "g37-image", "g37-text"):
        res = c2.check_metas(arm, tmp_path)
        assert res["ok"], (arm, res["problems"])


@pytest.mark.parametrize("bad, fragment, needle", [
    (_meta("gemini-3.7-flash", 0.7, "minimal", 1000, 944), False, "model"),
    (_meta(c2.G3_MODEL, 1.0, "minimal", 1000, 944), False, "temperature"),
    (_meta(c2.G3_MODEL, 0.7, "low", 1000, 944), False, "thinking level"),
    (_meta(c2.G3_MODEL, 0.7, "minimal", 1000, 0), False, "cached share"),
    (_meta(c2.G3_MODEL, 0.7, "minimal", 1000, 0), True, "cached share"),
])
def test_metas_refuse_a_mismatch(tmp_path: Path, bad: dict, fragment: bool,
                                 needle: str) -> None:
    """Main pass or recovery fragment: a cache fallback, a wrong model or T."""
    if fragment:
        _arm(tmp_path, "g3-image", G3_CACHED, fragment_meta=bad)
    else:
        _arm(tmp_path, "g3-image", bad)
    res = c2.check_metas("g3-image", tmp_path)
    assert not res["ok"] and any(needle in p for p in res["problems"]), res["problems"]


def test_temp1_arm_refuses_a_pass_sent_at_0_7(tmp_path: Path) -> None:
    _arm(tmp_path, "g3-text-temp1", _meta(c2.G3_MODEL, 0.7, "minimal", 1000, 0))
    res = c2.check_metas("g3-text-temp1", tmp_path)
    assert not res["ok"] and all("temperature" in p for p in res["problems"])


def test_implicit_share_gate_and_its_override(tmp_path: Path) -> None:
    _arm(tmp_path, "g37-image", _meta(c2.G37_MODEL, 0.7, "low", 1000, 300))
    assert not c2.check_metas("g37-image", tmp_path)["ok"]
    assert c2.check_metas("g37-image", tmp_path, allow_low_implicit=True)["ok"]
    assert c2.main(["metas", "g37-image", "--out", str(tmp_path)]) == 1
    assert c2.main(["metas", "g37-image", "--out", str(tmp_path),
                    "--allow-low-implicit-share"]) == 0


def test_missing_meta_is_refused(tmp_path: Path) -> None:
    _arm(tmp_path, "g37-text", _meta(c2.G37_MODEL, 0.7, "low", 1000, 0))
    next((tmp_path / "g37-text").rglob("run_3/*.meta.json")).unlink()
    res = c2.check_metas("g37-text", tmp_path)
    assert not res["ok"] and any("no meta" in p for p in res["problems"])


# ---------------------------------------------------------------------------
# A6: review band
# ---------------------------------------------------------------------------


def _union(out: Path, arm: str, n: int) -> None:
    spec = c2.ARMS[arm]
    d = out / arm / "verifier" / spec.version
    d.mkdir(parents=True)
    (d / f"union_k{spec.k}.build.json").write_text(json.dumps({"union_features": n}))


def test_band_bounds() -> None:
    assert c2.band_for("g3-text") == (2821, 3817)
    assert c2.band_for("g3-image") == (3455, 4675)
    assert c2.band_for("g37-text") == (672, 910)
    assert c2.band_for("g37-image") == (573, 775)
    assert c2.in_band("g37-image", 573) and c2.in_band("g37-image", 775)
    assert not c2.in_band("g37-image", 572) and not c2.in_band("g37-image", 776)


def test_band_refuses_out_of_band_and_names_the_override(tmp_path: Path, capsys) -> None:
    _union(tmp_path, "g37-text", 950)
    assert c2.main(["band", "g37-text:g3", "--out", str(tmp_path)]) == 1
    assert "BAND_OK=1" in capsys.readouterr().out
    _union(tmp_path, "g37-image", 700)
    assert c2.main(["band", "g37-image:g37", "--out", str(tmp_path)]) == 0


def test_estimate_flags_and_refuses_until_band_ok(tmp_path: Path, capsys) -> None:
    assert c2.main(["estimate", "--out", str(tmp_path)]) == 0  # guides only
    _union(tmp_path, "g3-image", 5000)
    assert c2.main(["estimate", "--out", str(tmp_path)]) == 1
    printed = capsys.readouterr().out
    assert "OUT OF BAND" in printed and "BAND_OK=1" in printed
    assert c2.main(["estimate", "--out", str(tmp_path), "--band-ok"]) == 0
    est = c2.estimate(tmp_path)
    row = next(r for r in est["rows"] if r["leg"] == "g3-image:g3")
    assert row["n"] == 5000 and row["source"] == "union" and row["out_of_band"]


def test_estimate_at_guide_sizes_matches_the_card() -> None:
    lo, hi = c2.estimate(Path("/nonexistent"))["total"]
    assert (round(lo, 2), round(hi, 2)) == (12.62, 13.01)


def test_arm_table_agrees_with_the_launcher() -> None:
    text = (PROJECT_ROOT / "scripts" / "modality-bridge-2026-10-07-stage2.sh").read_text()
    for arm, spec in c2.ARMS.items():
        assert arm in text
    legs = text.split('LEGS="', 1)[1].split('"', 1)[0].split()
    legs += text.split('LEGS="$LEGS ', 1)[1].split('"', 1)[0].split()
    assert tuple(legs) == c2.LEGS
