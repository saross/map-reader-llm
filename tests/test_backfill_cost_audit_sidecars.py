"""Tier-1 tests for ``scripts/backfill_cost_audit_sidecars.py`` (WP4 § A, PI rulings D14, D28).

The sidecar back-fill writes one ``cost_audit.json`` beside every historical
meta that recorded usage, copying the passes register's figure (D28) and
never touching the meta itself (D14). Every case builds its own repository
in ``tmp_path`` (synthetic metas, a fixture register and run registry, and
empty tier evidence), so nothing here reads the real ``outputs/``. Only the
committed rate card is read, through :func:`scripts.lib_cost.price_usage`.

Red sentinels:

- the naming rule, including several metas in one directory;
- a register row whose figure moved after the sidecars were written
  (``--check`` must turn red until the sidecars are refreshed);
- a meta must never be written, and a foreign file never overwritten.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.backfill_cost_audit_sidecars import (
    SCHEMA,
    BackfillError,
    Plan,
    build_plan,
    main,
    render,
    sidecar_path,
    write_plan,
)
from scripts.lib_pass_cost import PassCoster

pytestmark = pytest.mark.tier1

#: One meta's usage: 1 M input (none cached), 100 k output, 200 k thinking.
USAGE = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
         "total_output_tokens": 100_000, "total_thoughts_tokens": 200_000,
         "total_tokens": 1_300_000, "n_responses_with_usage": 10}
#: Its price on gemini-3-flash-preview: standard 0.50 + 0.90 = 1.40; flex and batch 0.70.
STANDARD_USD, DISCOUNT_USD = 1.4, 0.7
#: A usage block of zeros with no responses: unrecorded (D12).
UNRECORDED = {"total_input_tokens": 0, "total_output_tokens": 0, "total_thoughts_tokens": 0}
#: Zeros with responses: a genuine zero.
ZERO = {**UNRECORDED, "n_responses_with_usage": 4}

RUN = "outputs/run-a"
GENERATED_AT = "2026-10-03T12:35:34Z"


# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------


def _write(path: Path, doc: dict) -> Path:
    """Write *doc* as JSON, creating parents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def _meta(root: Path, rel: str, usage: dict | None = None, **extra) -> Path:
    """Write a minimal meta at ``root/rel`` and return its path."""
    meta = {"configuration": {"model": "gemini-3-flash-preview"},
            "usage_stats": USAGE if usage is None else usage,
            "timestamp": {"start": "2026-05-20T10:00:00+00:00",
                          "end": "2026-05-20T11:00:00+00:00", "duration_seconds": 3600.0},
            **extra}
    return _write(root / rel, meta)


def _fragment(meta_rel: str, cost: float, tier: str = "flex") -> dict:
    """A register fragment record in the shape ``PassCoster.cost_fragment`` writes."""
    return {"meta": meta_rel, "model_recorded": "gemini-3-flash-preview",
            "priced_at": "2026-05-20", "model": "gemini-3-flash-preview", "tier": tier,
            "tier_method": "billing-day",
            "evidence": [f"billing-day: gemini-3-flash-preview: 2026-05-20 {tier} -> {tier}"],
            "cost_usd": cost}


def _row(pass_id: str, fragments: list[dict], cost: float | None = None,
         basis: str = "audited", sources: list[str] | None = None) -> dict:
    """A register row citing *fragments* (its cost the fragments' sum by default)."""
    total = round(sum(f["cost_usd"] for f in fragments), 6) if cost is None else cost
    return {"pass_id": pass_id, "cost_usd": total, "cost_basis": basis,
            "cost_source": {"rate_card": {"path": "data/pricing/gemini-rate-card.json",
                                          "version": "test", "sha256": "0" * 64},
                            "fragments": fragments},
            "provenance": {"source_files": sources or [f["meta"] for f in fragments],
                           "last_extracted_at": "2026-10-03T07:57:28Z",
                           "extractor_version": "0.8.0"}}


def _register(root: Path, rows: list[dict]) -> Path:
    """Write the fixture passes register."""
    return _write(root / "results" / "passes-manifest.json",
                  {"schema_version": "1.0", "generated_at": GENERATED_AT,
                   "generator_version": "0.8.0", "passes": rows})


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """An empty repository: a run registry naming one run, and an empty register."""
    root = tmp_path / "repo"
    _write(root / "results" / "run-registry.json",
           {"registry": [{"run_id": "run-a", "directory_path": RUN}]})
    _register(root, [])
    (root / "outputs").mkdir(parents=True)
    return root


@pytest.fixture
def coster(tmp_path: Path) -> PassCoster:
    """The register's coster over EMPTY tier evidence (no logs, billing, or attestations)."""
    ev = tmp_path / "evidence"
    return PassCoster(
        billing_path=_write(ev / "billing.json", {"months_covered": [], "intervals": {},
                                                  "days": {}}),
        logs_path=_write(ev / "logs.json", {"directories": {}}),
        attestations_path=_write(ev / "att.json", {"attestations": []}),
        overrides_path=_write(ev / "pub.json", {"entries": {}}))


def _sidecar(root: Path, meta_rel: str) -> dict:
    """The planned sidecar for one meta, parsed."""
    return json.loads((sidecar_path(root / meta_rel)).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Naming.
# ---------------------------------------------------------------------------


def test_sidecar_name_rule() -> None:
    """``run.meta.json`` -> ``cost_audit.json``; ``<stem>.meta.json`` -> ``<stem>.cost_audit.json``."""
    assert sidecar_path(Path("a/b/run.meta.json")) == Path("a/b/cost_audit.json")
    assert sidecar_path(Path("a/detections-x-2026-04-09.meta.json")) == Path(
        "a/detections-x-2026-04-09.cost_audit.json")
    assert sidecar_path(Path("a/verified-brief-text-v2.meta.json")) == Path(
        "a/verified-brief-text-v2.cost_audit.json")
    # A file named only by a stem of ``run`` with a further dot is not run.meta.json.
    assert sidecar_path(Path("a/run.x.meta.json")) == Path("a/run.x.cost_audit.json")
    with pytest.raises(BackfillError):
        sidecar_path(Path("a/run.meta.json.gz"))


def test_several_metas_in_one_directory_do_not_collide(repo: Path, coster: PassCoster) -> None:
    """Five directories hold more than one meta: each meta gets its own sidecar."""
    names = ["run.meta.json", "verified-brief-text-v2.meta.json",
             "detections_run01_chunk0.meta.json", "detections_run01_chunk1.meta.json"]
    for name in names:
        _meta(repo, f"{RUN}/shared/{name}")
    plan = build_plan(repo, coster=coster)
    targets = sorted(p.name for p in plan.sidecars)
    assert targets == sorted(["cost_audit.json", "verified-brief-text-v2.cost_audit.json",
                              "detections_run01_chunk0.cost_audit.json",
                              "detections_run01_chunk1.cost_audit.json"])
    # Each sidecar names its own meta, and none is itself a *.meta.json.
    for target, text in plan.sidecars.items():
        doc = json.loads(text)
        assert sidecar_path(repo / doc["meta"]) == target
        assert not target.name.endswith(".meta.json")


# ---------------------------------------------------------------------------
# Contents.
# ---------------------------------------------------------------------------


def test_register_fragment_copies_the_register(repo: Path, coster: PassCoster) -> None:
    """A register fragment's sidecar carries the row and its fragment record verbatim."""
    primary = f"{RUN}/pool/run_1/detections-p.meta.json"
    recovery = f"{RUN}/pool/run_1_recovery/detections-p.meta.json"
    _meta(repo, primary)
    _meta(repo, recovery)
    frags = [_fragment(primary, 0.7), _fragment(recovery, 1.4, tier="standard")]
    _register(repo, [_row("run-a::pool::run1", frags)])
    assert main(["--write", "--repo-root", str(repo)], coster=coster) == 0

    doc = _sidecar(repo, recovery)
    assert doc["schema"] == SCHEMA
    assert doc["in_register"] is True
    assert doc["meta"] == recovery
    assert doc["register"] == {"path": "results/passes-manifest.json",
                               "generated_at": GENERATED_AT, "generator_version": "0.8.0",
                               "schema_version": "1.0"}
    [row] = doc["rows"]
    assert row["pass_id"] == "run-a::pool::run1"
    assert row["cost_usd"] == 2.1           # the ROW's figure, both fragments
    assert row["cost_basis"] == "audited"
    assert row["matched_by"] == "cost_source.fragments"
    assert row["fragment"] == frags[1]      # copied, not re-priced
    assert row["row_fragment_metas"] == [primary, recovery]
    assert "fragments" not in row["row_cost_source"]
    assert row["row_provenance"]["extractor_version"] == "0.8.0"
    # The primary's sidecar carries its own fragment record.
    assert _sidecar(repo, primary)["rows"][0]["fragment"] == frags[0]


def test_published_row_is_matched_through_its_source_files(repo: Path,
                                                           coster: PassCoster) -> None:
    """A row published from a report (no fragments) still owns its meta (D13, D28)."""
    leg = f"{RUN}/verifier/leg/run.meta.json"
    _meta(repo, leg)
    row = _row("run-a::leg::run1", [], cost=7.7028, basis="published", sources=[leg])
    row["cost_source"]["published"] = "outputs/run-a/post_run_report.md (verifier figure)"
    _register(repo, [row])
    plan = build_plan(repo, coster=coster)
    doc = json.loads(plan.sidecars[repo / RUN / "verifier/leg/cost_audit.json"])
    assert doc["in_register"] is True
    [entry] = doc["rows"]
    assert entry["matched_by"] == "provenance.source_files"
    assert entry["fragment"] is None
    assert entry["cost_usd"] == 7.7028 and entry["cost_basis"] == "published"
    assert entry["row_cost_source"]["published"].startswith("outputs/run-a/post_run_report.md")


def test_meta_outside_the_register_is_priced_by_the_register_method(
        repo: Path, coster: PassCoster) -> None:
    """No evidence: priced at every tier, published at the highest, candidates beside it."""
    smoke = f"{RUN}/smoke/detections-s.meta.json"
    _meta(repo, smoke)
    batch = f"{RUN}/staging/run_1/detections-b.meta.json"
    _meta(repo, batch, batch_api={"execution_mode": "batch"})
    plan = build_plan(repo, coster=coster)
    assert plan.stats["sidecars not in register"] == 2

    doc = json.loads(plan.sidecars[sidecar_path(repo / smoke)])
    assert doc["in_register"] is False
    assert "no row of the passes register cites this meta" in doc["reason"]
    assert "run-a is in results/run-registry.json" in doc["reason"]
    assert doc["cost_basis"] == "audited-upper-bound"
    assert doc["cost_usd"] == STANDARD_USD
    assert doc["fragment"]["tier"] is None
    assert doc["fragment"]["tier_method"] == "unresolved"
    assert doc["fragment"]["candidates"] == {"standard": STANDARD_USD, "flex": DISCOUNT_USD,
                                             "batch": DISCOUNT_USD}
    assert doc["fragment"]["bounds_usd"] == {"low": DISCOUNT_USD, "high": STANDARD_USD}
    assert doc["resolution_context"] == {
        "run_id": "run-a", "run_dir": RUN, "run_registered": True, "pool": "smoke",
        "stage": "proposer", "model": "gemini-3-flash-preview",
        "model_source": "configuration.model"}

    # A batch marker in the meta pins the tier, as it does for a register fragment.
    doc = json.loads(plan.sidecars[sidecar_path(repo / batch)])
    assert doc["cost_basis"] == "audited"
    assert doc["fragment"]["tier"] == "batch"
    assert doc["fragment"]["tier_method"] == "batch-marker"
    assert doc["cost_usd"] == DISCOUNT_USD


def test_outside_meta_in_an_unregistered_directory(repo: Path, coster: PassCoster) -> None:
    """A meta outside every registered run says so, and is a verifier by its name."""
    leg = "outputs/probe-x/verify/run.meta.json"
    _meta(repo, leg)
    doc = json.loads(build_plan(repo, coster=coster).sidecars[sidecar_path(repo / leg)])
    assert "outputs/probe-x is not a run in results/run-registry.json" in doc["reason"]
    assert doc["resolution_context"]["run_registered"] is False
    assert doc["resolution_context"]["stage"] == "verifier"


def test_metas_under_results_get_sidecars_and_archive_does_not(repo: Path,
                                                                coster: PassCoster) -> None:
    """The default scope is outputs/ and results/ (the vote-3 increments live
    under results/); archive/ is superseded and gets none."""
    vote3 = "results/deployment-oracle/vote3-verify/text-high/verified/run.meta.json"
    archived = "archive/old-run/verify/run.meta.json"
    _meta(repo, vote3)
    _meta(repo, archived)
    plan = build_plan(repo, coster=coster)
    assert sidecar_path(repo / vote3) in plan.sidecars
    assert sidecar_path(repo / archived) not in plan.sidecars
    assert json.loads(plan.sidecars[sidecar_path(repo / vote3)])["in_register"] is False


def test_zero_and_unrecorded_usage_get_no_sidecar(repo: Path, coster: PassCoster) -> None:
    """Plan § 4.5: a zero-usage or unrecorded meta stays without a sidecar."""
    unrec = f"{RUN}/pool/run_1/detections-u.meta.json"
    zero = f"{RUN}/pool/run_2/detections-z.meta.json"
    _meta(repo, unrec, usage=UNRECORDED)
    _meta(repo, zero, usage=ZERO)
    _meta(repo, f"{RUN}/pool/run_3/detections-n.meta.json", usage={})
    # Even a register fragment gets none when its usage is unrecorded.
    _register(repo, [_row("run-a::pool::run1", [_fragment(unrec, 0.0)], cost=None)])
    plan = build_plan(repo, coster=coster)
    assert plan.sidecars == {}
    assert plan.stats["usage unrecorded"] == 2 and plan.stats["usage zero"] == 1


def test_chunks_already_merged_into_a_register_meta_say_so(repo: Path,
                                                           coster: PassCoster) -> None:
    """Staging chunks whose sum the register prices are pointed at it: do not add."""
    names = ["detections_run01_chunk0.meta.json", "detections_run01_chunk1.meta.json"]
    halves = [{**USAGE, "total_output_tokens": 40_000}, {**USAGE, "total_output_tokens": 60_000}]
    for staging, usages in (("staging-run4", halves), ("staging-run5", [USAGE, USAGE])):
        for name, usage in zip(names, usages, strict=True):
            _meta(repo, f"{RUN}/{staging}/run_1/{name}", usage=usage)
    merged = f"{RUN}/pool/run_4/detections-m.meta.json"
    summed = {k: halves[0][k] + halves[1][k] for k in USAGE}
    _meta(repo, merged, usage=summed, chunked_run={"n_chunks": 2, "chunk_metas": names})
    _register(repo, [_row("run-a::pool::run4", [_fragment(merged, 1.0)])])
    plan = build_plan(repo, coster=coster)
    assert len(plan.merged) == 2
    linked = json.loads(plan.sidecars[repo / RUN / "staging-run4/run_1/"
                                      "detections_run01_chunk0.cost_audit.json"])
    assert linked["merged_into"]["meta"] == merged
    assert linked["merged_into"]["pass_ids"] == ["run-a::pool::run4"]
    assert "ALREADY inside that row" in linked["reason"]
    # The same names in another staging directory whose sum differs are not linked.
    other = json.loads(plan.sidecars[repo / RUN / "staging-run5/run_1/"
                                     "detections_run01_chunk0.cost_audit.json"])
    assert "merged_into" not in other


# ---------------------------------------------------------------------------
# Determinism, drift, and safety.
# ---------------------------------------------------------------------------


def test_output_is_byte_stable_sorted_and_relative(repo: Path, coster: PassCoster,
                                                   tmp_path: Path) -> None:
    """Two plans agree byte for byte; text is sorted JSON with a newline; no absolute path."""
    _meta(repo, f"{RUN}/smoke/detections-s.meta.json")
    first = build_plan(repo, coster=coster).sidecars
    second = build_plan(repo, coster=coster).sidecars
    assert first == second
    for text in first.values():
        assert text.endswith("}\n")
        assert render(json.loads(text)) == text
        assert str(tmp_path) not in text


def test_check_turns_red_when_a_register_row_moves(repo: Path, coster: PassCoster,
                                                   capsys: pytest.CaptureFixture) -> None:
    """Red sentinel: a regenerated register without a sidecar refresh fails ``--check``."""
    meta = f"{RUN}/pool/run_1/detections-p.meta.json"
    _meta(repo, meta)
    rows = [_row("run-a::pool::run1", [_fragment(meta, 0.7)])]
    _register(repo, rows)
    args = ["--repo-root", str(repo)]
    assert main(["--check", *args], coster=coster) == 1      # missing
    assert main(["--write", *args], coster=coster) == 0
    assert main(["--check", *args], coster=coster) == 0
    capsys.readouterr()

    moved = copy.deepcopy(rows)
    moved[0]["cost_usd"] = 1.4
    moved[0]["cost_source"]["fragments"][0].update(tier="standard", cost_usd=1.4)
    _register(repo, moved)
    assert main(["--check", *args], coster=coster) == 1
    out = capsys.readouterr().out
    assert f"differs: {RUN}/pool/run_1/detections-p.cost_audit.json" in out

    assert main(["--write", *args], coster=coster) == 0
    assert main(["--check", *args], coster=coster) == 0
    assert _sidecar(repo, meta)["rows"][0]["cost_usd"] == 1.4


def test_check_reports_a_stale_sidecar_and_write_keeps_it(repo: Path,
                                                          coster: PassCoster) -> None:
    """A sidecar whose meta no longer has usage is stale: reported, never deleted."""
    meta = f"{RUN}/pool/run_1/detections-p.meta.json"
    path = _meta(repo, meta)
    args = ["--repo-root", str(repo)]
    assert main(["--write", *args], coster=coster) == 0
    _meta(repo, meta, usage=UNRECORDED)
    assert path.exists()
    assert main(["--check", *args], coster=coster) == 1
    assert main(["--write", *args], coster=coster) == 0
    assert sidecar_path(repo / meta).exists()


def _digest(paths: list[Path]) -> dict[Path, tuple[str, int]]:
    """Content hash and modification time of each file."""
    return {p: (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in paths}


def test_metas_are_never_written(repo: Path, coster: PassCoster) -> None:
    """D14: the back-fill leaves every meta byte- and time-identical."""
    fragment = f"{RUN}/pool/run_1/detections-p.meta.json"
    _meta(repo, fragment)
    _meta(repo, f"{RUN}/smoke/detections-s.meta.json")
    _meta(repo, f"{RUN}/verifier/leg/run.meta.json")
    _meta(repo, f"{RUN}/pool/run_2/detections-u.meta.json", usage=UNRECORDED)
    _register(repo, [_row("run-a::pool::run1", [_fragment(fragment, 0.7)])])
    metas = sorted((repo / "outputs").rglob("*.meta.json"))
    before = _digest(metas)
    assert main(["--write", "--repo-root", str(repo)], coster=coster) == 0
    assert main(["--write", "--repo-root", str(repo)], coster=coster) == 0
    assert _digest(metas) == before
    assert sorted((repo / "outputs").rglob("*.meta.json")) == metas


def test_writer_refuses_a_meta_target_and_a_foreign_file(repo: Path,
                                                         coster: PassCoster) -> None:
    """The writer refuses to write a meta, and to overwrite a file that is not its own."""
    meta = repo / RUN / "pool/run_1/detections-p.meta.json"
    _meta(repo, f"{RUN}/pool/run_1/detections-p.meta.json")
    with pytest.raises(BackfillError, match="refusing to write a meta"):
        write_plan(Plan(sidecars={meta: "{}\n"}))

    foreign = sidecar_path(meta)
    foreign.write_text('{"something": "else"}\n', encoding="utf-8")
    assert main(["--write", "--repo-root", str(repo)], coster=coster) == 2
    assert foreign.read_text(encoding="utf-8") == '{"something": "else"}\n'
