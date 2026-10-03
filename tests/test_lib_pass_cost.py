"""Tier-1 tests for ``scripts/lib_pass_cost.py`` and ``scripts/derive_tier_evidence.py``.

The passes register's cost (WP3 of ``planning/cost-accounting-fix-plan-2026-09-21.md``)
is the pass's own tokens priced at the tier the evidence supports. These tests pin
each evidence rule with a red sentinel for the defect it exists to prevent, then
check the rules against committed legs whose answer is known from the invoice:

- the real-time flex ``discount_reason`` is a constant, not evidence (it once read
  every real-time pass as batch through a substring match);
- the explicit-cache path drops ``service_tier`` (h8-v2: flex requested, standard
  billed — 23.25 M output on 2026-04-15 Pacific against 0.60 M flex billed);
- a resumed pass is held to its first and last billing days, united;
- a tier whose whole day's billed output is below the fragment's is ruled out;
- an unresolved pass publishes its highest candidate with both bounds;
- the register equals the cost auditor on a committed leg (US$233.6295, WP1).

Unit cases build their own evidence files in ``tmp_path``; integration cases read
the committed evidence and outputs.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from scripts.derive_tier_evidence import (
    merge_intervals,
    read_day_exports,
    sku_class,
    sku_model,
    sku_tier,
)
from scripts.lib_pass_cost import PassCoster, fragment_usage, is_continuous, pacific_days

REPO = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------

FLEX_CONSTANT = "Gemini real-time flex (50 % of list, as per Batch API)"
BATCH_WORDING = "Google async Batch API (50 % of list)"

#: One fragment's usage: 1 M input (none cached), 100 k output, 200 k thinking.
USAGE = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
         "total_output_tokens": 100_000, "total_thoughts_tokens": 200_000,
         "total_tokens": 1_300_000, "n_responses_with_usage": 10}

#: Its price on gemini-3-flash-preview: standard 0.50 + 0.90 = 1.40; flex/batch 0.70.
STANDARD_USD, FLEX_USD = 1.4, 0.7


def _write(path: Path, doc: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def _meta(path: Path, *, start: str = "2026-05-20T10:00:00+00:00",
          end: str = "2026-05-20T11:00:00+00:00", duration: float | None = 3600.0,
          usage: dict | None = None, **extra) -> tuple[dict, Path]:
    """Write a minimal meta and return ``(meta, path)``."""
    meta = {"configuration": {"model": "gemini-3-flash-preview"},
            "usage_stats": USAGE if usage is None else usage,
            "timestamp": {"start": start, "end": end, "duration_seconds": duration},
            **extra}
    _write(path, meta)
    return meta, path


@pytest.fixture
def evidence(tmp_path):
    """Write empty evidence files; return a factory for a coster over them."""
    paths = {
        "billing": _write(tmp_path / "ev" / "billing.json",
                          {"months_covered": [], "intervals": {}, "days": {}}),
        "logs": _write(tmp_path / "ev" / "logs.json", {"directories": {}}),
        "att": _write(tmp_path / "ev" / "att.json", {"attestations": []}),
        "pub": _write(tmp_path / "ev" / "pub.json", {"entries": {}}),
    }

    def make(billing: dict | None = None, logs: dict | None = None,
             attestations: list | None = None, published: dict | None = None) -> PassCoster:
        if billing is not None:
            _write(paths["billing"], {"months_covered": [], "intervals": {}, "days": {},
                                      **billing})
        if logs is not None:
            _write(paths["logs"], {"directories": logs})
        if attestations is not None:
            _write(paths["att"], {"attestations": attestations})
        if published is not None:
            _write(paths["pub"], {"entries": published})
        return PassCoster(billing_path=paths["billing"], logs_path=paths["logs"],
                          attestations_path=paths["att"], overrides_path=paths["pub"])

    return make


def _rel(p: Path) -> str:
    """How the coster keys a directory: repository-relative, else absolute."""
    try:
        return p.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return p.resolve().as_posix()


def _cost(coster: PassCoster, metas: list[tuple[dict, Path]], run_dir: Path,
          stage: str = "proposer", pass_id: str = "r::p::run1") -> dict:
    return coster.cost_pass(pass_id=pass_id, fragments=metas, run_id="r", pool="p",
                            run_dir=run_dir, model="gemini-3-flash-preview", stage=stage)


# ---------------------------------------------------------------------------
# Small pure helpers.
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_pacific_days_shift_utc_mornings_to_the_previous_day():
    # Cloud Billing dates usage in Pacific time; 03:00 UTC is the evening before.
    assert pacific_days("2026-04-18T00:15:00+00:00", "2026-04-18T03:59:00+00:00") == [
        "2026-04-17"]


@pytest.mark.tier1
def test_continuity_tells_a_resumed_meta_from_a_long_run():
    assert is_continuous("2026-04-16T01:00:00+00:00", "2026-04-17T02:00:00+00:00", 90000)
    assert not is_continuous("2026-03-26T01:00:00+00:00", "2026-07-30T05:00:00+00:00", 20000)


@pytest.mark.tier1
@pytest.mark.parametrize(("sku", "model", "tier", "cls"), [
    ("Generate content output token count gemini 3 flash text flex",
     "gemini-3-flash-preview", "flex", "output"),
    ("Generate_content text output token count for gemini 3 flash batch",
     "gemini-3-flash-preview", "batch", "output"),
    ("Generate_content image input token count for gemini 3 flash",
     "gemini-3-flash-preview", "standard", "input"),
    ("Generate_content cached image input token count for gemini 3 flash",
     "gemini-3-flash-preview", None, "input"),
    ("Generate content input token count gemini 3.1 flash lite preview text",
     "gemini-3.1-flash-lite-preview", "standard", "input"),
    ("Generate_content image output token count for Gemini 3 Pro Image",
     "gemini-3-pro-image", "standard", "output"),
    ("Generate_content_cached_input_token_count_gemini_3_pro_short_image",
     "gemini-3.1-pro-preview", None, "input"),
    ("Generate content input token count gemini 3.7 flash image flex caching",
     "gemini-3.7-flash", "flex", "input"),
])
def test_sku_table_reads_model_tier_and_class(sku, model, tier, cls):
    # 'gemini 3 flash' must not swallow 3.1 Flash Lite; '3 Pro Image' is an
    # image-GENERATION model, not the 3.1 Pro the project ran.
    assert (sku_model(sku), sku_tier(sku), sku_class(sku)) == (model, tier, cls)


@pytest.mark.tier1
def test_merge_intervals_joins_adjacent_days():
    assert merge_intervals([("2026-04-08", "2026-04-17"), ("2026-04-18", "2026-04-20")]) == [
        ["2026-04-08", "2026-04-20"]]


@pytest.mark.tier1
def test_day_export_with_a_foreign_sku_is_classed_contaminated(tmp_path):
    header = ("Service description,Service ID,SKU description,SKU ID,Usage amount,Usage unit,"
              "List cost ($),Unrounded subtotal ($),Subtotal ($)\n")
    own = "Gemini API,X,Generate content output token count gemini 3 flash text flex,Y,\"10\",count,1,1,1\n"
    foreign = "Gemini API,X,Generate content output token count gemini 3.5 flash text flex,Y,\"5\",count,1,1,1\n"
    (tmp_path / "A_Reports, 2026-08-28 — 2026-08-28.csv").write_text(header + own)
    (tmp_path / "A_Reports, 2026-08-28 — 2026-08-28 (1).csv").write_text(header + own + foreign)
    skus = {"2026-08": {"Generate content output token count gemini 3 flash text flex"}}
    best = read_day_exports(tmp_path, skus)
    # The clean export wins the day; the other is counted as an alternative.
    assert best["2026-08-28"]["project_filter"] == "unverified"
    assert best["2026-08-28"]["alternatives"] == 1
    only_foreign = read_day_exports(tmp_path, {"2026-08": set()})
    assert only_foreign["2026-08-28"]["project_filter"] == "contaminated"


# ---------------------------------------------------------------------------
# Evidence rules (unit, with red sentinels).
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_flex_constant_is_not_tier_evidence(evidence, tmp_path):
    # SENTINEL: the real-time writer stamped this string whatever tier ran
    # (d0a709059), and a substring test for "batch api" once read it as batch.
    coster = evidence()
    meta = _meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json",
                 cost_estimate={"pricing_used": {"discount_reason": FLEX_CONSTANT}})
    out = _cost(coster, [meta], tmp_path / "run")
    frag = out["cost_source"]["fragments"][0]
    assert frag["tier"] is None and frag["tier_method"] == "unresolved"
    assert not any("batch-path-pricing" in e for e in frag["evidence"])
    assert out["cost_basis"] == "audited-upper-bound"
    assert out["cost_usd"] == pytest.approx(STANDARD_USD)


@pytest.mark.tier1
def test_batch_path_wording_pins_batch(evidence, tmp_path):
    coster = evidence()
    meta = _meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json",
                 cost_estimate={"pricing_used": {"discount_reason": BATCH_WORDING}})
    out = _cost(coster, [meta], tmp_path / "run")
    frag = out["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"], out["cost_basis"]) == (
        "batch", "batch-path-pricing", "audited")
    assert out["cost_usd"] == pytest.approx(FLEX_USD)


@pytest.mark.tier1
def test_own_run_log_pins_and_inherited_log_yields_to_a_batch_marker(evidence, tmp_path):
    run = tmp_path / "run"
    leg = run / "verifier" / "v1"
    coster = evidence(logs={_rel(run): {"tiers": ["flex"], "explicit_cache": False,
                                        "covers_verifier": True,
                                        "logs": [{"path": "x/pass1.log"}]}})
    meta = _meta(leg / "run.meta.json")
    (leg / "batch_jobs.json").write_text("{}")
    out = _cost(coster, [meta], run, stage="verifier")
    frag = out["cost_source"]["fragments"][0]
    assert frag["tier"] == "batch"
    # Different launches, not a contradiction: a note, never a conflict.
    assert "conflicts" not in frag
    assert any("overruled" in n for n in frag["notes"])


@pytest.mark.tier1
def test_cached_path_bills_standard_for_a_proposer_only(evidence, tmp_path):
    # SENTINEL: the explicit-cache request config omits service_tier, so a
    # run printing "Service tier: flex" is billed at standard.
    run = tmp_path / "run"
    pdir = run / "p" / "run_1"
    logs = {_rel(pdir): {"tiers": ["flex"], "explicit_cache": True,
                         "logs": [{"path": "x/launch.log"}]},
            _rel(run / "verified"): {"tiers": ["flex"], "explicit_cache": True,
                                     "logs": [{"path": "x/run.log"}]}}
    coster = evidence(logs=logs)
    proposer = _cost(coster, [_meta(pdir / "a.meta.json")], run)
    frag = proposer["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("standard", "cached-path")
    assert any("REQUESTED" in n for n in frag["notes"]) and "conflicts" not in frag
    assert proposer["cost_usd"] == pytest.approx(STANDARD_USD)
    # A verifier leg is not the detection runner's cached path.
    verifier = _cost(coster, [_meta(run / "verified" / "run.meta.json")], run,
                     stage="verifier")
    assert verifier["cost_source"]["fragments"][0]["tier"] == "flex"


@pytest.mark.tier1
def test_volume_rule_excludes_a_tier_the_day_could_not_hold(evidence, tmp_path):
    day = {"2026-05-20": {"project_filter": "unverified", "models": {
        "gemini-3-flash-preview": {"tiers": {"flex": {"output": 250_000},
                                             "standard": {"output": 9_000_000}}}}}}
    coster = evidence(billing={"days": day})
    out = _cost(coster, [_meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json")],
                tmp_path / "run")
    frag = out["cost_source"]["fragments"][0]
    # 300 k output + thinking exceeds the day's 250 k flex: it cannot be flex.
    assert (frag["tier"], frag["tier_method"]) == ("standard", "billing-day")
    assert any("not flex" in e for e in frag["evidence"])


@pytest.mark.tier1
def test_volume_rule_contradicting_a_pin_is_a_conflict(evidence, tmp_path):
    pdir = tmp_path / "run" / "p" / "run_1"
    day = {"2026-05-20": {"project_filter": "unverified", "models": {
        "gemini-3-flash-preview": {"tiers": {"flex": {"output": 250_000},
                                             "standard": {"output": 9_000_000}}}}}}
    coster = evidence(billing={"days": day},
                      logs={_rel(pdir): {"tiers": ["flex"], "explicit_cache": False,
                                         "logs": [{"path": "x/launch.log"}]}})
    frag = _cost(coster, [_meta(pdir / "a.meta.json")], tmp_path / "run")[
        "cost_source"]["fragments"][0]
    assert frag["tier"] == "flex"  # the pin stands; the disagreement is reported
    assert any("pins flex but billing-day" in c for c in frag["conflicts"])


@pytest.mark.tier1
def test_resumed_fragment_is_held_to_its_end_days_united(evidence, tmp_path):
    billing = {"months_covered": ["2026-03", "2026-04", "2026-05", "2026-06", "2026-07"],
               "intervals": {"gemini-3-flash-preview": {
                   "standard": [["2026-03-01", "2026-03-31"]],
                   "flex": [["2026-07-01", "2026-07-31"]]}}}
    coster = evidence(billing=billing)
    meta = _meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json",
                 start="2026-03-26T01:00:00+00:00", end="2026-07-30T05:00:00+00:00",
                 duration=20000)
    out = _cost(coster, [meta], tmp_path / "run")
    frag = out["cost_source"]["fragments"][0]
    # Intersecting March (standard) with July (flex) would exclude every
    # tier; united, the pass may be either, and is published at the higher.
    assert "conflicts" not in frag
    assert set(frag["candidates"]) == {"flex", "standard"}
    assert out["cost_basis"] == "audited-upper-bound"
    assert out["cost_source"]["bounds_usd"] == {"low": pytest.approx(FLEX_USD),
                                                "high": pytest.approx(STANDARD_USD)}


@pytest.mark.tier1
def test_candidates_that_price_alike_are_audited(evidence, tmp_path):
    # Gemini 3 Flash prices batch and flex identically: the tier is unknown,
    # the cost is not.
    day = {"2026-05-20": {"project_filter": "unverified", "models": {
        "gemini-3-flash-preview": {"tiers": {"flex": {"output": 9e9},
                                             "batch": {"output": 9e9}}}}}}
    out = _cost(evidence(billing={"days": day}),
                [_meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json")], tmp_path / "run")
    assert out["cost_basis"] == "audited"
    assert out["cost_source"]["fragments"][0]["tier_method"].startswith("tier-indifferent")


@pytest.mark.tier1
def test_no_usage_is_null_not_zero(evidence, tmp_path):
    empty = {k: 0 for k in USAGE}
    out = _cost(evidence(), [_meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json",
                                   usage=empty)], tmp_path / "run")
    assert (out["cost_usd"], out["cost_basis"]) == (None, "unrecorded")


@pytest.mark.tier1
def test_unknown_model_is_unpriceable(evidence, tmp_path):
    coster = evidence()
    meta = _meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json")
    out = coster.cost_pass(pass_id="r::p::run1", fragments=[meta], run_id="r", pool="p",
                           run_dir=tmp_path / "run", model="gemini-9-imaginary")
    assert (out["cost_usd"], out["cost_basis"]) == (None, "unpriceable")


@pytest.mark.tier1
def test_attestation_pins_and_a_machine_record_outranks_it(evidence, tmp_path):
    att = [{"id": "A1", "run_id": "r", "pool": "*", "tier": "flex", "attested_by": "PI",
            "attested_on": "2026-10-03", "evidence": "test"}]
    alone = _cost(evidence(attestations=att),
                  [_meta(tmp_path / "a" / "p" / "run_1" / "a.meta.json")], tmp_path / "a")
    assert alone["cost_source"]["fragments"][0]["tier_method"] == "attestation"
    pdir = tmp_path / "b" / "p" / "run_1"
    logs = {_rel(pdir): {"tiers": ["standard"], "explicit_cache": False,
                         "logs": [{"path": "x/launch.log"}]}}
    frag = _cost(evidence(attestations=att, logs=logs), [_meta(pdir / "a.meta.json")],
                 tmp_path / "b")["cost_source"]["fragments"][0]
    assert frag["tier"] == "standard"
    assert any("pins disagree" in c for c in frag["conflicts"])


@pytest.mark.tier1
@pytest.mark.parametrize("bad", [
    [{"id": "A1", "run_id": "r", "pool": "*", "tier": "flexible", "attested_by": "PI",
      "attested_on": "2026-10-03", "evidence": "x"}],
    [{"id": "A1", "run_id": "r", "pool": "*", "tier": "flex", "attested_by": "PI",
      "attested_on": "2026-10-03", "evidence": "x"}] * 2,
    [{"id": "A1", "run_id": "r", "pool": "*", "tier": "flex"}],
])
def test_attestation_file_refuses_what_it_cannot_apply(evidence, bad):
    with pytest.raises(ValueError):
        evidence(attestations=bad)


@pytest.mark.tier1
def test_published_figure_overrides_with_its_source(evidence, tmp_path):
    coster = evidence(published={"r::p::run1": {"basis": "published", "cost_usd": 12.5,
                                                "source": "post_run_report.md § 4"}})
    out = _cost(coster, [_meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json")],
                tmp_path / "run")
    assert (out["cost_usd"], out["cost_basis"]) == (12.5, "published")
    assert out["cost_source"]["published"] == "post_run_report.md § 4"


@pytest.mark.tier1
def test_overwritten_meta_without_a_figure_is_a_lower_bound(evidence, tmp_path):
    pdir = tmp_path / "run" / "p" / "run_1"
    logs = {_rel(pdir): {"tiers": ["flex"], "explicit_cache": False,
                         "logs": [{"path": "x/launch.log"}]}}
    coster = evidence(logs=logs, published={"r::p::run1": {
        "basis": "audited-lower-bound", "source": "cleanup overwrote run.meta.json"}})
    out = _cost(coster, [_meta(pdir / "a.meta.json")], tmp_path / "run")
    assert (out["cost_basis"], out["cost_usd"]) == ("audited-lower-bound", pytest.approx(FLEX_USD))
    assert out["cost_source"]["note"].startswith("LOWER bound")


@pytest.mark.tier1
def test_override_file_refuses_a_published_entry_without_a_figure(evidence):
    with pytest.raises(ValueError):
        evidence(published={"r::p::run1": {"basis": "published", "source": "x"}})


@pytest.mark.tier1
def test_recovery_fragment_is_priced_at_its_own_tier_and_summed(evidence, tmp_path):
    run = tmp_path / "run"
    primary = _meta(run / "p" / "run_1" / "a.meta.json")
    recovery = _meta(run / "p" / "run_1_recovery" / "b.meta.json",
                     cost_estimate={"pricing_used": {"discount_reason": BATCH_WORDING}})
    logs = {_rel(run / "p" / "run_1"): {"tiers": ["standard"], "explicit_cache": False,
                                        "logs": [{"path": "x/launch.log"}]}}
    out = _cost(evidence(logs=logs), [primary, recovery], run)
    tiers = [f["tier"] for f in out["cost_source"]["fragments"]]
    assert tiers == ["standard", "batch"]
    assert out["cost_usd"] == pytest.approx(STANDARD_USD + FLEX_USD)
    assert out["cost_basis"] == "audited"


# ---------------------------------------------------------------------------
# Committed legs (integration).
# ---------------------------------------------------------------------------


def _committed_pass(run_id: str, pool: str, n: int) -> dict:
    from scripts.generate_post_run_report import extract_passes, extraction_context
    rows = extract_passes(extraction_context(run_id))
    return next(r for r in rows if r["pass_id"] == f"{run_id}::{pool}::run{n}")


@pytest.mark.tier1
def test_h8_v2_requested_flex_and_was_billed_standard():
    row = _committed_pass("h8-v2", "canonical", 1)
    frag = row["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("standard", "cached-path")
    assert any("REQUESTED" in n for n in frag["notes"])
    assert "conflicts" not in frag  # the billing day agrees: 0.60 M flex all day


@pytest.mark.tier1
def test_register_equals_the_auditor_on_the_gemini3_image_pool():
    # WP1 acceptance: audit_proposer_cost.py at flex prices this pool, recovery
    # fragments included, at US$233.6295. The register must say the same.
    from scripts.generate_post_run_report import extract_passes, extraction_context
    rows = [r for r in extract_passes(extraction_context("gemini3-image-55map-2026-09-16"))
            if r["proposer_pool"] == "g384_ov192_55map_g3img"]
    assert len(rows) == 5
    assert all(r["cost_basis"] == "audited" for r in rows)
    assert sum(r["cost_usd"] for r in rows) == pytest.approx(233.6295, abs=5e-4)


@pytest.mark.tier1
def test_register_tokens_include_recovery_fragments():
    row = _committed_pass("gemini3-image-55map-2026-09-16", "g384_ov192_55map_g3img", 3)
    metas = [m for m in row["provenance"]["source_files"] if m.endswith(".meta.json")]
    assert len(metas) == 3  # run_3 plus two recovery rounds
    total = sum(json.loads((REPO / m).read_text())["usage_stats"]["total_output_tokens"]
                for m in metas)
    assert row["tokens"]["output"] == total


# ---------------------------------------------------------------------------
# The C3 ledger's cost claim (rederive_manifest_fields.rederive_cost).
# ---------------------------------------------------------------------------


def _verdicts(row: dict) -> dict:
    from scripts.rederive_manifest_fields import rederive_cost
    sources = row["provenance"]["source_files"]
    from scripts.rederive_manifest_fields import _load_meta
    metas = [_load_meta(s) if s.endswith((".meta.json", ".meta.json.gz")) else {}
             for s in sources]
    return {f["field"]: f for f in rederive_cost(row, sources, metas)}


@pytest.mark.tier1
@pytest.mark.parametrize(("run_id", "pool", "n"), [
    ("gemini3-image-55map-2026-09-16", "g384_ov192_55map_g3img", 3),  # recovery fragments
    ("h8-v2", "canonical", 1),                                         # cached path
    ("pv-diag-384", "flash-high-text-n5-text-t0.7", 1),                # unrecorded
])
def test_c3_certifies_the_audited_figure(run_id, pool, n):
    v = _verdicts(_committed_pass(run_id, pool, n))
    assert v["cost_usd"]["verdict"] == "MATCH"
    if "cost_source.fragments" in v:
        assert v["cost_source.fragments"]["verdict"] == "MATCH"


@pytest.mark.tier1
def test_c3_refuses_a_figure_the_function_does_not_give():
    # SENTINEL: the old claim certified the meta's block; a register that
    # copied it again would be MISMATCH under the new claim.
    row = _committed_pass("h8-v2", "canonical", 1)
    v = _verdicts(row)
    meta_block = v["cost_usd.meta_block"]
    assert meta_block["verdict"] == "STRUCTURAL" and "never certified" in meta_block["note"]
    copied = {**row, "cost_usd": meta_block["derived"]}
    assert _verdicts(copied)["cost_usd"]["verdict"] == "MISMATCH"


@pytest.mark.tier1
def test_c3_refuses_a_fragment_list_that_is_not_the_cited_metas():
    row = _committed_pass("gemini3-image-55map-2026-09-16", "g384_ov192_55map_g3img", 3)
    src = {**row["cost_source"], "fragments": row["cost_source"]["fragments"][:1]}
    v = _verdicts({**row, "cost_source": src})
    assert v["cost_source.fragments"]["verdict"] == "MISMATCH"


@pytest.mark.tier1
def test_recovery_merged_meta_is_priced_from_per_item_sums():
    # SENTINEL: the 2026-05-02 recovery merge doubled every token class in
    # the TH7 and IM metas (token-load-audit-2026-06-12 §§ 3.2, 3.4). The
    # register must read the per-item sums the June audit called clean.
    th7 = _committed_pass("55maps-text-high-generalisation", "detect_brief-text", 1)
    assert th7["tokens"]["input_billed"] == 12_828_582  # not 25,694,714
    assert "recovery merge" in th7["cost_source"]["fragments"][0]["usage_source"]
    # The June audit's clean flex cost per TH7 pass: US$39.92 to US$40.45.
    assert 39.9 < th7["cost_usd"] < 40.5
    im = _committed_pass("55maps-image-generalisation", "library_plus-hp", 1)
    assert im["tokens"]["input_cached"] < 130_000_000  # clean ~124 M, not ~248 M


# ---------------------------------------------------------------------------
# Audit round 1 (lenses A and B, 2026-10-03): one test per surviving mutation.
# ---------------------------------------------------------------------------

LOG_ENTRY = {"explicit_cache": False, "covers_verifier": False,
             "logs": [{"path": "x/launch.log"}]}


def _cost2(tier: str, source: str) -> dict:
    return {"cost_estimate": {"schema": "cost/2",
                              "pricing_used": {"tier": tier, "tier_source": source}}}


@pytest.mark.tier1
def test_continuous_fragment_intersects_interval_only_days(evidence, tmp_path):
    # SENTINEL for `allowed &= tiers`: with no day exports, the invoice line
    # windows allow flex|standard on 05-20 and flex only on 05-21; a fragment
    # running across both in one sitting can only have been flex.
    billing = {"months_covered": ["2026-05"], "intervals": {"gemini-3-flash-preview": {
        "flex": [["2026-05-01", "2026-05-31"]], "standard": [["2026-05-20", "2026-05-20"]]}}}
    meta = _meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json",
                 start="2026-05-20T20:00:00+00:00", end="2026-05-21T20:00:00+00:00",
                 duration=86400)
    frag = _cost(evidence(billing=billing), [meta], tmp_path / "run")[
        "cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("flex", "billing-day")


@pytest.mark.tier1
def test_cli_runner_record_is_a_request_the_cached_path_overrules(evidence, tmp_path):
    # SENTINEL (lenses A and B): a WP2 cost/2 block records the CLI switch even
    # when the cached call dropped it, so it must rank below the cached path.
    pdir = tmp_path / "run" / "p" / "run_1"
    coster = evidence(logs={_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"],
                                         "explicit_cache": True}})
    out = _cost(coster, [_meta(pdir / "a.meta.json", **_cost2("flex", "cli --service-tier"))],
                tmp_path / "run")
    frag = out["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("standard", "cached-path")
    assert "conflicts" not in frag
    assert any(n.startswith("runner-record") and "REQUESTED" in n for n in frag["notes"])
    assert out["cost_usd"] == pytest.approx(STANDARD_USD)


@pytest.mark.tier1
def test_batch_runner_record_is_structural_and_rules_out_the_cached_path(evidence, tmp_path):
    pdir = tmp_path / "run" / "p" / "run_1"
    coster = evidence(logs={_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"],
                                         "explicit_cache": True}})
    frag = _cost(coster, [_meta(pdir / "a.meta.json", **_cost2("batch", "Batch API path"))],
                 tmp_path / "run")["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("batch", "runner-record-batch")
    assert not any(e.startswith("cached-path") for e in frag["evidence"])


@pytest.mark.tier1
def test_a_cost2_tier_from_an_inference_is_not_a_record(evidence, tmp_path):
    frag = _cost(evidence(), [_meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json",
                                    **_cost2("flex", "inferred from side evidence"))],
                 tmp_path / "r")["cost_source"]["fragments"][0]
    assert frag["tier"] is None and not any("runner-record" in e for e in frag["evidence"])


@pytest.mark.tier1
@pytest.mark.parametrize("marker", ["probabilities", "batch_api"])
def test_batch_markers_pin_batch(evidence, tmp_path, marker):
    leg = tmp_path / "run" / "v"
    extra = {"batch_api": {"job": "x"}} if marker == "batch_api" else {}
    meta = _meta(leg / "run.meta.json", **extra)
    if marker == "probabilities":
        (leg / "probabilities.json").write_text(json.dumps({"mode": "batch"}))
    frag = _cost(evidence(), [meta], tmp_path / "run", stage="verifier")[
        "cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("batch", "batch-marker")


@pytest.mark.tier1
def test_realtime_verifier_mode_rules_out_batch(evidence, tmp_path):
    leg = tmp_path / "run" / "v"
    meta = _meta(leg / "run.meta.json")
    (leg / "probabilities.json").write_text(json.dumps({"mode": "realtime"}))
    day = {"2026-05-20": {"project_filter": "unverified", "models": {
        "gemini-3-flash-preview": {"tiers": {"flex": {"output": 9e9},
                                             "batch": {"output": 9e9}}}}}}
    frag = _cost(evidence(billing={"days": day}), [meta], tmp_path / "run",
                 stage="verifier")["cost_source"]["fragments"][0]
    assert frag["tier"] == "flex" and "verifier-mode" in frag["tier_method"]


@pytest.mark.tier1
def test_launch_manifest_pins_and_an_inherited_one_ranks_lowest(evidence, tmp_path):
    run = tmp_path / "run"
    pdir = run / "p" / "run_1"
    pdir.mkdir(parents=True)
    (pdir / "launch_manifest.json").write_text(json.dumps({"service_tier": "flex"}))
    own = _cost(evidence(), [_meta(pdir / "a.meta.json")], run)["cost_source"]["fragments"][0]
    assert (own["tier"], own["tier_method"]) == ("flex", "launch-manifest")
    run2 = tmp_path / "run2"
    pdir2 = run2 / "p" / "run_1"
    pdir2.mkdir(parents=True)
    (run2 / "launch_manifest.json").write_text(json.dumps({"service_tier": "flex"}))
    logs = {_rel(pdir2): {**LOG_ENTRY, "tiers": ["standard"]}}
    frag = _cost(evidence(logs=logs), [_meta(pdir2 / "a.meta.json")], run2)[
        "cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("standard", "run-log")
    assert "conflicts" not in frag and any("overruled" in n for n in frag["notes"])


@pytest.mark.tier1
@pytest.mark.parametrize(("covers", "tier"), [(False, None), (True, "flex")])
def test_an_inherited_log_pins_a_verifier_only_if_it_covers_one(evidence, tmp_path, covers,
                                                                 tier):
    run = tmp_path / "run"
    logs = {_rel(run): {**LOG_ENTRY, "tiers": ["flex"], "covers_verifier": covers}}
    frag = _cost(evidence(logs=logs), [_meta(run / "verifier" / "v" / "run.meta.json")], run,
                 stage="verifier")["cost_source"]["fragments"][0]
    assert frag["tier"] == tier


@pytest.mark.tier1
def test_resumed_fragment_with_an_uninformative_end_day_stays_open(evidence, tmp_path):
    # SENTINEL (lens A): one informative end day must not narrow a resumed
    # fragment whose other session fell on a month not yet invoiced.
    billing = {"months_covered": ["2026-04"], "intervals": {"gemini-3-flash-preview": {
        "flex": [["2026-04-08", "2026-04-30"]]}}}
    meta = _meta(tmp_path / "run" / "p" / "run_1" / "a.meta.json",
                 start="2026-04-09T20:00:00+00:00", end="2026-10-20T20:00:00+00:00",
                 duration=20000)
    out = _cost(evidence(billing=billing), [meta], tmp_path / "run")
    frag = out["cost_source"]["fragments"][0]
    assert frag["tier"] is None and set(frag["candidates"]) == {"standard", "flex", "batch"}


@pytest.mark.tier1
@pytest.mark.parametrize(("input_tokens", "basis"), [(16_000, "audited"),
                                                     (24_000, "audited-upper-bound")])
def test_tier_indifference_threshold_is_half_a_cent(evidence, tmp_path, input_tokens, basis):
    # Standard minus flex on fresh input is 0.25 US$/M: 16 k tokens differ by
    # US$0.004 (one cost), 24 k by US$0.006 (a range).
    usage = {**{k: 0 for k in USAGE}, "total_input_tokens": input_tokens,
             "total_tokens": input_tokens, "n_responses_with_usage": 1}
    out = _cost(evidence(), [_meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json",
                                   usage=usage)], tmp_path / "r")
    assert out["cost_basis"] == basis


@pytest.mark.tier1
@pytest.mark.parametrize(("output", "excluded"), [(1_000_500, False), (1_002_000, True)])
def test_volume_rule_slack_is_a_tenth_of_a_percent(evidence, tmp_path, output, excluded):
    day = {"2026-05-20": {"project_filter": "unverified", "models": {
        "gemini-3-flash-preview": {"tiers": {"flex": {"output": 1_000_000},
                                             "standard": {"output": 9e9}}}}}}
    usage = {**USAGE, "total_output_tokens": output, "total_thoughts_tokens": 0}
    frag = _cost(evidence(billing={"days": day}),
                 [_meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json", usage=usage)],
                 tmp_path / "r")["cost_source"]["fragments"][0]
    assert any("not flex" in e for e in frag["evidence"]) is excluded


@pytest.mark.tier1
@pytest.mark.parametrize(("gap_h", "continuous"), [(5, True), (7, False)])
def test_resume_gap_is_six_hours(gap_h, continuous):
    start, run_s = "2026-05-20T00:00:00+00:00", 3600
    end = (datetime.fromisoformat(start) + timedelta(seconds=run_s + gap_h * 3600)).isoformat()
    assert is_continuous(start, end, run_s) is continuous


@pytest.mark.tier1
def test_continuity_without_a_run_time_uses_a_36_hour_span():
    assert is_continuous("2026-05-20T00:00:00+00:00", "2026-05-21T11:00:00+00:00", None)
    assert not is_continuous("2026-05-20T00:00:00+00:00", "2026-05-21T13:00:00+00:00", None)


@pytest.mark.tier1
def test_merge_intervals_keeps_a_span_that_contains_the_next():
    assert merge_intervals([("2026-04-01", "2026-04-30"), ("2026-04-05", "2026-04-10")]) == [
        ["2026-04-01", "2026-04-30"]]


@pytest.mark.tier1
def test_a_clean_meta_with_recovery_history_is_not_rebuilt():
    # NEGATIVE: T03's metas carry recovery_history but were not double-counted
    # (items_processed equals completed), so their usage_stats stand.
    meta = json.loads((REPO / "outputs/55maps-text-high-t0.3-generalisation/proposer/"
                       "detect_brief-text/run_1/detections-detect_brief-text-3-flash-"
                       "2026-04-26.meta.json").read_text())
    assert meta.get("recovery_history")
    usage, note = fragment_usage(meta)
    assert note is None and usage is meta["usage_stats"]


@pytest.mark.tier1
def test_part_unpriceable_pass_publishes_no_figure(evidence, tmp_path):
    run = tmp_path / "run"
    metas = [_meta(run / "p" / "run_1" / "a.meta.json"),
             _meta(run / "p" / "run_1_recovery" / "b.meta.json")]
    out = evidence().cost_pass(pass_id="r::p::run1", fragments=metas, run_id="r", pool="p",
                               run_dir=run, model="gemini-3-flash-preview",
                               fragment_models=["gemini-3-flash-preview", "gemini-9-unknown"])
    assert (out["cost_usd"], out["cost_basis"]) == (None, "unpriceable")


@pytest.mark.tier1
def test_an_unrecorded_fragment_makes_the_pass_a_floor(evidence, tmp_path):
    run = tmp_path / "run"
    logs = {_rel(run / "p" / "run_1"): {**LOG_ENTRY, "tiers": ["flex"]}}
    metas = [_meta(run / "p" / "run_1" / "a.meta.json"),
             _meta(run / "p" / "run_1_recovery" / "b.meta.json", usage={k: 0 for k in USAGE})]
    out = _cost(evidence(logs=logs), metas, run)
    assert (out["cost_basis"], out["cost_usd"]) == ("audited-lower-bound",
                                                   pytest.approx(FLEX_USD))


@pytest.mark.tier1
def test_an_unrecorded_fragment_beside_an_unresolved_one_has_no_bound(evidence, tmp_path):
    run = tmp_path / "run"
    metas = [_meta(run / "p" / "run_1" / "a.meta.json"),
             _meta(run / "p" / "run_1_recovery" / "b.meta.json", usage={k: 0 for k in USAGE})]
    out = _cost(evidence(), metas, run)
    assert (out["cost_usd"], out["cost_basis"]) == (None, "unpriceable")
    assert "neither" in out["cost_source"]["note"]


@pytest.mark.tier1
def test_an_undated_fragment_is_not_priced_at_today(evidence, tmp_path):
    meta = _meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json", start=None, end=None)
    out = _cost(evidence(), [meta], tmp_path / "r")
    assert (out["cost_usd"], out["cost_basis"]) == (None, "unpriceable")


@pytest.mark.tier1
def test_fragment_model_prefers_the_fragment_own_record_then_model_of_record():
    from scripts.generate_post_run_report import _fragment_model
    meta = {"per_item_metadata": [{"model_used": "gemini-3.7-flash"}]}
    assert _fragment_model(meta, "gemini-3-flash-preview", None) == "gemini-3.7-flash"
    assert _fragment_model({}, "gemini-3-flash-preview", None) == "gemini-3-flash-preview"
    assert _fragment_model(meta, "x", "gemini-3.1-pro-preview") == "gemini-3.1-pro-preview"


@pytest.mark.tier1
def test_attestation_matches_on_pool_glob_and_billing_days(evidence, tmp_path):
    att = [{"id": "A1", "run_id": "r", "pool": "flash-*", "pacific_days": ["2026-05-20"],
            "tier": "flex", "attested_by": "PI", "attested_on": "2026-10-03", "evidence": "x"}]
    coster = evidence(attestations=att)
    days = ["2026-05-20"]
    assert coster.attestation("r", "flash-high", days) is not None
    assert coster.attestation("r", "pro-high", days) is None          # pool glob
    assert coster.attestation("r", "flash-high", ["2026-05-21"]) is None  # day filter
    assert coster.attestation("other", "flash-high", days) is None


@pytest.mark.tier1
@pytest.mark.parametrize("bad", [{"basis": "audited-lower-bound"},
                                 {"basis": "guessed", "source": "x"}])
def test_override_file_refuses_an_entry_without_source_or_known_basis(evidence, bad):
    with pytest.raises(ValueError):
        evidence(published={"r::p::run1": bad})


@pytest.mark.tier1
@pytest.mark.parametrize(("sku", "model"), [
    ("Generate content input token count gemini 3.5 flash text flex", "gemini-3.5-flash"),
    ("Generate content input token count gemini 3.6 flash text", "gemini-3.6-flash"),
    ("Generate content output token count gemini 3.8 flash text flex", "gemini-3.8-flash"),
])
def test_sku_table_reads_the_later_flash_models(sku, model):
    assert sku_model(sku) == model


@pytest.mark.tier1
@pytest.mark.parametrize("tamper", ["basis", "fragment"])
def test_schema_refuses_an_unknown_basis_or_a_fragment_without_its_keys(tamper):
    from scripts.generate_post_run_report import load_schema_registry, validate_row
    reg, _ = load_schema_registry()
    row = _committed_pass("h8-v2", "canonical", 1)
    assert validate_row("passes", row, reg) == []
    if tamper == "basis":
        bad = {**row, "cost_basis": "guessed"}
    else:
        frags = [{k: v for k, v in f.items() if k != "tier"}
                 for f in row["cost_source"]["fragments"]]
        bad = {**row, "cost_source": {**row["cost_source"], "fragments": frags}}
    assert validate_row("passes", bad, reg) != []


# -- integration: wiring the lenses found untested ---------------------------


@pytest.mark.tier1
def test_c3_certifies_new_style_rows_through_rederive_pass():
    # Through the real entry point, on a cached-path row and a recovery-merged
    # row: cost, fragment stamps and the token claims all certify.
    from scripts.rederive_manifest_fields import rederive_pass
    for run_id, pool in (("h8-v2", "canonical"),
                         ("55maps-text-high-generalisation", "detect_brief-text")):
        result = rederive_pass(_committed_pass(run_id, pool, 1))
        verdicts = {f["field"]: f["verdict"] for f in result["fields"]}
        assert verdicts["cost_usd"] == "MATCH", (run_id, verdicts)
        assert verdicts["cost_source.fragments.stamps"] == "MATCH", run_id
        assert verdicts["tokens.input_billed"] == "MATCH", run_id


@pytest.mark.tier1
def test_c3_refuses_a_pricing_date_that_is_not_the_meta_own():
    from scripts.rederive_manifest_fields import rederive_pass
    row = _committed_pass("h8-v2", "canonical", 1)
    frags = [{**f, "priced_at": "2027-01-02"} for f in row["cost_source"]["fragments"]]
    bad = {**row, "cost_source": {**row["cost_source"], "fragments": frags}}
    verdicts = {f["field"]: f["verdict"] for f in rederive_pass(bad)["fields"]}
    assert verdicts["cost_source.fragments.stamps"] == "MISMATCH"


@pytest.mark.tier1
def test_verifier_legs_are_wired_as_verifiers():
    # IM's run log records an explicit cache, but its verifier leg is not on
    # the detection runner's cached path; and the Gemini 3 image row's proposer
    # pass logs say nothing of its verifier legs, so they do not pin them.
    im = _committed_pass("55maps-image-generalisation", "verified", 1)
    assert im["cost_source"]["fragments"][0]["tier_method"] != "cached-path"
    from scripts.generate_post_run_report import extract_passes, extraction_context
    rows = extract_passes(extraction_context("gemini3-image-55map-2026-09-16"))
    for r in rows:
        for f in r["cost_source"].get("fragments", []):
            if "verify" in r["proposer_pool"]:
                assert f["tier_method"] != "run-log-inherited", r["pass_id"]


@pytest.mark.tier1
def test_a_second_whole_meta_in_run_n_is_priced():
    # Lens A: flash35-pv-2x2 run 3 holds two dated metas; the second billed
    # 734,478 input tokens the register once missed.
    row = _committed_pass("flash35-pv-2x2", "flash35-min-text-1of10", 3)
    metas = [f["meta"] for f in row["cost_source"]["fragments"]]
    assert sum("/run_3/" in m for m in metas) == 2
    assert row["tokens"]["input_billed"] > 1_400_000


@pytest.mark.tier1
@pytest.mark.parametrize("run_id", ["h8-v2", "flash35-pv-2x2", "55maps-text-high-generalisation",
                                    "gemini37-55map-2026-08-29"])
def test_committed_register_is_current_for_sampled_runs(run_id):
    # Lens B M5: a rule change must not leave the committed register stale and
    # C3 certifying whatever was regenerated. Re-extract and compare.
    from scripts.generate_post_run_report import extract_passes, extraction_context
    committed = {r["pass_id"]: r for r in json.loads(
        (REPO / "results/passes-manifest.json").read_text())["passes"]
        if r["run_id"] == run_id}
    fresh = {r["pass_id"]: r for r in extract_passes(extraction_context(run_id))}
    assert set(fresh) == set(committed)
    for pid, r in fresh.items():
        for key in ("cost_usd", "cost_basis", "cost_source", "tokens"):
            assert r[key] == committed[pid][key], (pid, key)
