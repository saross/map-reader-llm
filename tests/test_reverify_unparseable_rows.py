"""
Tests for ``scripts/reverify_unparseable_rows.py`` (PI decision D55, Q4).

The script re-sends a few unparseable batch verifier rows, spread over
several legs, as ONE batch job, and books the answers into each leg's
``<leg>_repaired/`` copy. These tests build synthetic legs on disk and fake
the API lifecycle, so they make no call:

- **build** selects only the rows no repair parses, copies each one's
  original request line byte for byte, and refuses on a wrong count, a line
  that disagrees with the leg's ``run.meta.json``, a key shared by two legs,
  two models, or an estimate over the ceiling.
- **lodge** refuses a second batch and a model that resolves to another
  name, prints the ``wait_for_run.py`` markers, and does not re-send after a
  failed job.
- **book** merges a parseable answer into the repaired copy (leaving the leg
  untouched), refuses without a repaired copy, and does not book an answer
  that is again unparseable.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import reverify_unparseable_rows as rv  # noqa: E402
from scripts.modality_bridge_stage2_checks import repair_leg  # noqa: E402

pytestmark = pytest.mark.tier1

SYSTEM = "You are a verifier."
MODEL = "gemini-3.7-flash"

#: candidate_24301 of verify_k3_arm2, verbatim: an unescaped double quote
#: inside a string, which no repair tier parses.
UNPARSEABLE = (
    '{\n    "best_alternative": "Natural shoreline / terrain contour with text and '
    'vegetation symbols",\n    "alternative_evidence": "The center contains blue '
    "elevation text '166,6', brown contour lines, a stream/lake shoreline, and small "
    "vegetation marks ('\"'), but no central mound symbol with outward radiating "
    'sunburst rays.",\n    "reasoning": "There is no mound symbol (kurgan) present at '
    'the centre of this crop.",\n    "mound_probability": 0.0\n}')
#: Valid JSON followed by a stray brace: the real-time repair recovers it.
REPAIRABLE = '{"mound_probability": 0.2, "reasoning": "r"}\n}'
GOOD = ('{"best_alternative": "a", "alternative_evidence": "e", "reasoning": "r", '
        '"mound_probability": 0.03}')


def _gen(temperature: float = 0.0) -> dict:
    return {"temperature": temperature, "max_output_tokens": 8192,
            "response_mime_type": "application/json",
            "thinking_config": {"thinking_level": "LOW"}}


def _row(key: str, text: str, usage: dict | None = None) -> dict:
    return {"key": key, "response": {
        "candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": "STOP"}],
        "usageMetadata": usage or {"promptTokenCount": 1792, "candidatesTokenCount": 120,
                                   "thoughtsTokenCount": 100, "totalTokenCount": 2012}}}


def make_leg(root: Path, name: str, rows: dict[str, str], model: str = MODEL,
             line_temperature: float = 0.0) -> Path:
    """A leg directory with probabilities, raw results, meta and request file.

    Args:
        root: Parent directory.
        name: Leg directory name.
        rows: ``key -> response text``; a text plain ``json.loads`` rejects is
            booked as the batch parser books it, 0.0 with PARSE_ERROR.
        model: The model the meta records.
        line_temperature: The temperature written into the request lines.
    """
    leg = root / name
    leg.mkdir(parents=True)
    results, raw, lines = {}, [], []
    for key, text in rows.items():
        try:
            prob = json.loads(text)["mound_probability"]
            booked = {"mound_probability": prob, "reasoning": "ok",
                      "best_alternative": "", "alternative_evidence": ""}
        except json.JSONDecodeError as exc:
            booked = {"mound_probability": 0.0, "reasoning": f"PARSE_ERROR: {exc}",
                      "best_alternative": "", "alternative_evidence": ""}
        results[key] = booked
        raw.append(_row(key, text))
        lines.append({"key": key, "request": {
            "contents": [{"parts": [{"text": f"crop {key}"}], "role": "user"}],
            "system_instruction": {"parts": [{"text": SYSTEM}]},
            "generation_config": _gen(line_temperature)}})
    (leg / "probabilities.json").write_text(json.dumps(
        {"version": "v", "mode": "batch", "iterations": 1, "results": results,
         "total_results": len(results)}, indent=2))
    (leg / "batch_results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in raw))
    (leg / "verifier_requests_chunk0.jsonl").write_text(
        "".join(json.dumps(line) + "\n" for line in lines))
    (leg / "run.meta.json").write_text(json.dumps({"configuration": {
        "model": model, "temperature": 0.0, "max_output_tokens": 8192,
        "thinking_level": "low",
        "system_instruction_hash": hashlib.sha256(SYSTEM.encode()).hexdigest()},
        "usage_stats": {"total_input_tokens": 1792 * len(rows),
                        "total_output_tokens": 120 * len(rows),
                        "total_thoughts_tokens": 100 * len(rows),
                        "total_cached_tokens": 0}}))
    return leg


@pytest.fixture
def two_legs(tmp_path: Path) -> tuple[Path, Path]:
    """Leg A: one good, one repairable, one unparseable row; leg B: one unparseable."""
    a = make_leg(tmp_path, "verify_k1_arm2", {"candidate_00001": GOOD,
                                              "candidate_00002": REPAIRABLE,
                                              "candidate_00003": UNPARSEABLE})
    b = make_leg(tmp_path, "verify_k3_arm2", {"candidate_00010": GOOD,
                                              "candidate_00011": UNPARSEABLE})
    return a, b


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def test_build_sends_only_unrepairable_rows_byte_for_byte(two_legs, tmp_path):
    a, b = two_legs
    out = tmp_path / "run"
    rec = rv.build([(a, None), (b, None)], out, expect=2, max_cost_usd=0.05,
                   at="2026-10-08")
    assert [r["key"] for r in rec["rows"]] == ["candidate_00003", "candidate_00011"]
    assert rec["repairable_not_sent"] == [
        {"leg": str(a), "key": "candidate_00002", "repairs_to": 0.2}]
    originals = []
    for leg, key in ((a, "candidate_00003"), (b, "candidate_00011")):
        for line in (leg / "verifier_requests_chunk0.jsonl").read_bytes().splitlines():
            if json.loads(line)["key"] == key:
                originals.append(line + b"\n")
    assert (out / "requests.jsonl").read_bytes() == b"".join(originals)
    assert rec["model"] == MODEL and rec["tier"] == "batch"
    assert 0 < rec["estimate"]["total_cost_usd"] < 0.05


def test_build_refuses_a_count_other_than_expected(two_legs, tmp_path):
    a, b = two_legs
    with pytest.raises(rv.Refused, match="--expect 3"):
        rv.build([(a, None), (b, None)], tmp_path / "run", expect=3, max_cost_usd=0.05)
    assert not (tmp_path / "run").exists()


def test_build_refuses_a_line_that_disagrees_with_the_meta(tmp_path):
    leg = make_leg(tmp_path, "leg", {"candidate_00001": UNPARSEABLE},
                   line_temperature=0.7)
    with pytest.raises(rv.Refused, match="temperature"):
        rv.build([(leg, None)], tmp_path / "run", expect=1, max_cost_usd=0.05)


def test_build_refuses_a_key_shared_by_two_legs(tmp_path):
    a = make_leg(tmp_path, "a", {"candidate_00001": UNPARSEABLE})
    b = make_leg(tmp_path, "b", {"candidate_00001": UNPARSEABLE})
    with pytest.raises(rv.Refused, match="unique across the legs"):
        rv.build([(a, None), (b, None)], tmp_path / "run", expect=2, max_cost_usd=0.05)


def test_build_refuses_two_models(tmp_path):
    a = make_leg(tmp_path, "a", {"candidate_00001": UNPARSEABLE})
    b = make_leg(tmp_path, "b", {"candidate_00002": UNPARSEABLE},
                 model="gemini-3-flash-preview")
    with pytest.raises(rv.Refused, match="one model"):
        rv.build([(a, None), (b, None)], tmp_path / "run", expect=2, max_cost_usd=0.05)


def test_build_refuses_an_estimate_over_the_ceiling(two_legs, tmp_path):
    a, b = two_legs
    with pytest.raises(rv.Refused, match="ceiling"):
        rv.build([(a, None), (b, None)], tmp_path / "run", expect=2, max_cost_usd=1e-9)


# ---------------------------------------------------------------------------
# lodge
# ---------------------------------------------------------------------------


class FakeApi:
    """The batch lifecycle, recorded rather than called."""

    def __init__(self, rows: list[dict], state: str = "JOB_STATE_SUCCEEDED",
                 resolved: str = MODEL) -> None:
        self.rows, self.state, self.resolved = rows, state, resolved
        self.uploads: list[Path] = []
        self.submits: list[tuple] = []

    def kwargs(self) -> dict:
        return {"resolve_model": lambda c, m: self.resolved,
                "preflight": lambda c, paths, log=None, sweep=None: 1,
                "upload": self.upload, "submit": self.submit, "poll": self.poll,
                "retrieve": lambda c, job: self.rows, "state_name": lambda s: s}

    def upload(self, client, path, name):
        self.uploads.append(path)
        return "files/in1"

    def submit(self, client, model, file, name):
        self.submits.append((model, file))
        return SimpleNamespace(name="batches/j1")

    def poll(self, client, name):
        dest = SimpleNamespace(file_name="files/out1") if self.rows else None
        return SimpleNamespace(state=self.state, dest=dest)


@pytest.fixture
def built(two_legs, tmp_path) -> Path:
    a, b = two_legs
    out = tmp_path / "run"
    rv.build([(a, None), (b, None)], out, expect=2, max_cost_usd=0.05, at="2026-10-08")
    return out


def test_lodge_success_writes_results_and_the_complete_marker(built, capsys):
    api = FakeApi([_row("candidate_00003", GOOD), _row("candidate_00011", GOOD)])
    assert rv.lodge(built, None, 0.05, **api.kwargs()) == 0
    assert api.submits == [(MODEL, "files/in1")]
    jobs = json.loads((built / "batch_jobs.json").read_text())
    assert jobs["state"] == "JOB_STATE_SUCCEEDED" and jobs["job"] == "batches/j1"
    assert len((built / "batch_results.jsonl").read_text().splitlines()) == 2
    assert any(line.startswith(rv.MARKER_COMPLETE)
               for line in capsys.readouterr().out.splitlines())


def test_lodge_refuses_a_second_batch(built):
    (built / "batch_jobs.json").write_text("{}")
    api = FakeApi([])
    with pytest.raises(rv.Refused, match="second batch"):
        rv.lodge(built, None, 0.05, **api.kwargs())
    assert api.uploads == []


def test_lodge_refuses_a_model_that_resolves_elsewhere(built):
    api = FakeApi([], resolved="gemini-3.7-flash-preview")
    with pytest.raises(rv.Refused, match="resolves to"):
        rv.lodge(built, None, 0.05, **api.kwargs())
    assert api.uploads == [] and not (built / "batch_jobs.json").exists()


def test_lodge_failed_job_is_partial_and_not_resent(built, capsys):
    api = FakeApi([], state="JOB_STATE_FAILED")
    assert rv.lodge(built, None, 0.05, **api.kwargs()) == 2
    assert len(api.submits) == 1
    assert any(line.startswith(rv.MARKER_PARTIAL)
               for line in capsys.readouterr().out.splitlines())


def test_lodge_missing_row_is_partial(built):
    api = FakeApi([_row("candidate_00003", GOOD)])
    assert rv.lodge(built, None, 0.05, **api.kwargs()) == 2
    jobs = json.loads((built / "batch_jobs.json").read_text())
    assert jobs["missing_or_errored"] == ["candidate_00011"]


# ---------------------------------------------------------------------------
# book
# ---------------------------------------------------------------------------


def _landed(built: Path, texts: dict[str, str]) -> Path:
    api = FakeApi([_row(k, t) for k, t in texts.items()])
    rv.lodge(built, None, 0.05, **api.kwargs())
    return built


def test_book_merges_into_the_repaired_copy_and_leaves_the_leg(two_legs, built):
    a, b = two_legs
    for leg in (a, b):
        repair_leg(leg)  # removes the unparseable row, recovers the repairable one
    digests = {p: hashlib.sha256(p.read_bytes()).hexdigest()
               for leg in (a, b) for p in leg.iterdir()}
    _landed(built, {"candidate_00003": GOOD, "candidate_00011": GOOD})
    assert rv.book(built) == 0
    for leg, key in ((a, "candidate_00003"), (b, "candidate_00011")):
        rep = json.loads((leg.with_name(leg.name + "_repaired")
                          / "probabilities.json").read_text())
        assert rep["results"][key]["mound_probability"] == 0.03
        assert rep["total_results"] == len(rep["results"])
        assert rep["reverify"]["keys"] == [key]
    rep_a = json.loads((a.with_name(a.name + "_repaired") / "probabilities.json").read_text())
    assert rep_a["results"]["candidate_00002"]["mound_probability"] == 0.2
    assert digests == {p: hashlib.sha256(p.read_bytes()).hexdigest()
                       for leg in (a, b) for p in leg.iterdir()}
    record = json.loads((built / "record.json").read_text())
    assert record["n_booked"] == 2 and record["total_cost_usd"] > 0
    assert {r["new_probability"] for r in record["rows"]} == {0.03}


def test_book_refuses_without_a_repaired_copy(built):
    _landed(built, {"candidate_00003": GOOD, "candidate_00011": GOOD})
    with pytest.raises(rv.Refused, match="repair on the leg first"):
        rv.book(built)


def test_book_does_not_book_an_answer_that_is_unparseable_again(two_legs, built):
    a, b = two_legs
    for leg in (a, b):
        repair_leg(leg)
    _landed(built, {"candidate_00003": UNPARSEABLE, "candidate_00011": GOOD})
    assert rv.book(built) == 1
    rep_a = json.loads((a.with_name(a.name + "_repaired") / "probabilities.json").read_text())
    assert "candidate_00003" not in rep_a["results"]
    assert rep_a["reverify"]["not_booked"] == ["candidate_00003"]
    record = json.loads((built / "record.json").read_text())
    assert record["n_unparseable_again"] == 1


def test_parse_new_response_needs_a_probability():
    with pytest.raises(ValueError):
        rv.parse_new_response('{"reasoning": "no probability"}')
    verdict, method = rv.parse_new_response(REPAIRABLE)
    assert verdict["mound_probability"] == 0.2 and method == "parse_response_with_repair"
    verdict, method = rv.parse_new_response(GOOD)
    assert verdict["mound_probability"] == 0.03 and method == "json.loads"
