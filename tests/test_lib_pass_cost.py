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
from scripts.lib_pass_cost import (
    PassCoster,
    fragment_usage,
    is_continuous,
    pacific_days,
    verifier_coverage,
)

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
                                        "verifier_tiers": ["flex"],
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

LOG_ENTRY = {"explicit_cache": False, "verifier_tiers": [],
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
@pytest.mark.parametrize(("verifier_tiers", "tier"), [([], None), (["flex"], "flex")])
def test_an_inherited_log_pins_a_verifier_only_with_a_verifier_tier(evidence, tmp_path,
                                                                    verifier_tiers, tier):
    # The proposer's launch line ("tiers") never pins a verifier leg beneath a
    # run-level log; only a tier recorded FOR a verifier stage does.
    run = tmp_path / "run"
    logs = {_rel(run): {**LOG_ENTRY, "tiers": ["flex"], "verifier_tiers": verifier_tiers}}
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
def test_an_unrecorded_fragment_beside_an_unresolved_one_is_a_floor_at_the_lowest(evidence,
                                                                                  tmp_path):
    # The sum of each priced fragment's LOWEST candidate is a valid floor
    # whatever the unresolved tier was (re-audit L4: null threw it away).
    run = tmp_path / "run"
    metas = [_meta(run / "p" / "run_1" / "a.meta.json"),
             _meta(run / "p" / "run_1_recovery" / "b.meta.json", usage={k: 0 for k in USAGE})]
    out = _cost(evidence(), metas, run)
    assert (out["cost_basis"], out["cost_usd"]) == ("audited-lower-bound",
                                                   pytest.approx(FLEX_USD))
    assert out["cost_source"]["note"] == ("LOWER bound: a fragment of this pass recorded "
                                          "no usage")


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


# ---------------------------------------------------------------------------
# Audit round 2 (re-audit, 2026-10-03): the surviving mutations and new rules.
# ---------------------------------------------------------------------------


def _c3(row: dict) -> dict:
    """C3's verdicts for a row, with the decomposition production C3 passes."""
    from scripts.rederive_manifest_fields import rederive_pass
    decomposition = json.loads((REPO / "results/run-conditions.json").read_text())
    decomposition = decomposition.get("decomposition", decomposition)
    return {f["field"]: f for f in rederive_pass(row, decomposition)["fields"]}


def _first_row_with(basis: str) -> dict:
    rows = json.loads((REPO / "results/passes-manifest.json").read_text())["passes"]
    return next(r for r in rows if r["cost_basis"] == basis)


@pytest.mark.tier1
def test_c3_refuses_a_model_that_is_neither_the_row_nor_the_meta_own():
    row = _committed_pass("h8-v2", "canonical", 1)
    frags = [{**f, "model_recorded": "gemini-3.7-flash"} for f in row["cost_source"]["fragments"]]
    bad = {**row, "cost_source": {**row["cost_source"], "fragments": frags}}
    assert _c3(bad)["cost_source.fragments.stamps"]["verdict"] == "MISMATCH"


@pytest.mark.tier1
def test_c3_refuses_a_published_row_the_overrides_do_not_list():
    row = {**_committed_pass("h8-v2", "canonical", 1), "cost_basis": "published",
           "cost_usd": 1.0, "cost_source": {"published": "x", "rate_card": {}}}
    assert _c3(row)["cost_usd"]["verdict"] == "MISMATCH"
    good = _first_row_with("published")
    assert _c3(good)["cost_usd"]["verdict"] == "MATCH"


@pytest.mark.tier1
def test_c3_refuses_a_priceable_pass_published_as_unpriceable():
    row = {**_committed_pass("h8-v2", "canonical", 1), "cost_basis": "unpriceable",
           "cost_usd": None}
    assert _c3(row)["cost_usd"]["verdict"] == "MISMATCH"
    unknown = {**row, "model_used": "gemini-9-imaginary"}
    assert _c3(unknown)["cost_usd"]["verdict"] == "MATCH"


@pytest.mark.tier1
def test_c3_checks_the_high_bound_and_the_lower_bound_label():
    row = _first_row_with("audited-upper-bound")
    bounds = {**row["cost_source"]["bounds_usd"], "high": 999.0}
    bad = {**row, "cost_source": {**row["cost_source"], "bounds_usd": bounds}}
    assert _c3(bad)["cost_source.bounds_usd.high"]["verdict"] == "MISMATCH"
    whole = {**_committed_pass("h8-v2", "canonical", 1), "cost_basis": "audited-lower-bound"}
    assert _c3(whole)["cost_basis"]["verdict"] == "MISMATCH"


@pytest.mark.tier1
def test_batch_path_wording_also_rules_out_the_cached_path(evidence, tmp_path):
    pdir = tmp_path / "run" / "p" / "run_1"
    coster = evidence(logs={_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"],
                                         "explicit_cache": True}})
    meta = _meta(pdir / "a.meta.json",
                 cost_estimate={"pricing_used": {"discount_reason": BATCH_WORDING}})
    frag = _cost(coster, [meta], tmp_path / "run")["cost_source"]["fragments"][0]
    assert frag["tier"] == "batch"
    assert not any(e.startswith("cached-path") for e in frag["evidence"])


@pytest.mark.tier1
def test_a_batch_api_source_with_a_non_batch_tier_is_not_a_record(evidence, tmp_path):
    frag = _cost(evidence(), [_meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json",
                                    **_cost2("flex", "Batch API path"))],
                 tmp_path / "r")["cost_source"]["fragments"][0]
    assert not any("runner-record" in e for e in frag["evidence"])


@pytest.mark.tier1
def test_two_run_level_records_that_disagree_are_a_conflict(evidence, tmp_path):
    run = tmp_path / "run"
    (run / "p" / "run_1").mkdir(parents=True)
    (run / "launch_manifest.json").write_text(json.dumps({"service_tier": "standard"}))
    logs = {_rel(run): {**LOG_ENTRY, "tiers": ["flex"]}}
    frag = _cost(evidence(logs=logs), [_meta(run / "p" / "run_1" / "a.meta.json")], run)[
        "cost_source"]["fragments"][0]
    # The run log is the closer record of execution and ranks first; the
    # disagreement between two run-level records is not "overruled by own".
    assert (frag["tier"], frag["tier_method"]) == ("flex", "run-log-inherited")
    assert any("pins disagree" in c for c in frag["conflicts"])


@pytest.mark.tier1
@pytest.mark.parametrize(("stage", "tier"), [("verifier", "standard"), ("proposer", "flex")])
def test_a_launch_manifest_gives_each_stage_its_own_tier(evidence, tmp_path, stage, tier):
    run = tmp_path / "run"
    leg = run / ("v" if stage == "verifier" else "p/run_1")
    leg.mkdir(parents=True)
    (run / "launch_manifest.json").write_text(json.dumps({
        "service_tier": "flex",
        "resolved_config": {"proposer": {}, "verify": {"service_tier": "standard"}}}))
    frag = _cost(evidence(), [_meta(leg / "a.meta.json")], run, stage=stage)[
        "cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == (tier, "launch-manifest-inherited")


@pytest.mark.tier1
def test_sibling_metas_exclude_chunks_and_rewrites_of_the_same_run(tmp_path):
    from scripts.generate_post_run_report import _sibling_metas
    def write(name, run_id):
        path = tmp_path / name
        path.write_text(json.dumps({"run_id": run_id}))
        return path
    others = [write("a_chunk0.meta.json", "X"), write("b.meta.json", "P"),
              write("c.meta.json", "X"), write("d.meta.json", None), write("e.meta.json", "X")]
    # chunk, same run as the primary, no run_id, and a second rewrite of X: none priced
    assert _sibling_metas({"run_id": "P"}, others) == [others[2]]


@pytest.mark.tier1
def test_the_sibling_meta_is_cited_and_certified():
    row = _committed_pass("flash35-pv-2x2", "flash35-min-text-1of10", 3)
    assert sum("/run_3/" in s for s in row["provenance"]["source_files"]) == 2
    verdicts = _c3(row)
    assert verdicts["cost_source.fragments"]["verdict"] == "MATCH"
    assert verdicts["cost_usd"]["verdict"] == "MATCH"


@pytest.mark.tier1
def test_parse_log_reads_only_verifier_stage_tiers_as_verifier_evidence():
    from scripts.derive_tier_evidence import parse_log
    proposer_only = "Service tier: flex\n... 9,910 candidates to verify later\n"
    assert parse_log(proposer_only) == {"tiers": ["flex"], "unknown": [], "tier_lines": 1,
                                        "explicit_cache_lines": 0, "verifier_tiers": []}
    staged = "Service tier: flex\nrun_pv.py verify --c d\nService tier: standard\n"
    assert parse_log(staged)["verifier_tiers"] == ["standard"]
    banner = "Service tier: flex\n=== Stage V: verifier ===\nService tier: standard\n"
    assert parse_log(banner)["verifier_tiers"] == []  # a banner is not a verifier command
    command = "python3 scripts/run_pv.py verify --crops-dir c --service-tier flex\n"
    assert parse_log(command)["verifier_tiers"] == ["flex"]
    assert parse_log("Service tier: priority\n")["unknown"] == ["priority"]
    assert parse_log("Context cache created: x\nService tier: flex\n")[
        "explicit_cache_lines"] == 1


@pytest.mark.tier1
def test_run_report_sums_each_basis_apart():
    from scripts.generate_run_reports import _basis_sums
    passes = ([{"cost_basis": "audited", "cost_usd": 1.0}] * 3
              + [{"cost_basis": "unrecorded", "cost_usd": None}, {}])
    # A basis with no priced pass has no sum: null, not zero (D12).
    assert _basis_sums(passes) == ("audited US$3.0000 (3); none recorded no figure (1); "
                                   "unrecorded no figure (1)")


@pytest.mark.tier1
def test_an_overwritten_verifier_meta_is_detected_as_a_floor():
    # Re-audit M3: verified-f3vf's meta is the 1-request cleanup leg; its
    # probabilities.json holds 1,132 results. T03's verifier meta (10,539
    # requests against 9,910 results) is whole and stays audited.
    f3vf = _committed_pass("flash35-pv-2x2", "verified-f3vf", 1)
    assert f3vf["cost_basis"] == "audited-lower-bound"
    assert "1,132 results" in f3vf["cost_source"]["note"]
    t03 = _committed_pass("55maps-text-high-t0-3-generalisation", "verified", 1)
    assert t03["cost_basis"] == "audited"
    meta_path = REPO / t03["cost_source"]["fragments"][0]["meta"]
    accounted, results = verifier_coverage([(json.loads(meta_path.read_text()), meta_path)])
    assert results == 9_910 and accounted >= results


# ---------------------------------------------------------------------------
# Audit round 3 (second re-audit, 2026-10-03).
# ---------------------------------------------------------------------------


@pytest.mark.tier1
@pytest.mark.parametrize(("log", "verifier_tiers"), [
    ("python 4_detect_mounds_batch.py --service-tier standard\n", []),
    ("Service tier: flex\nwriting outputs/verifier-t-pilot/x\nService tier: flex\n", []),
    ("Service tier: flex\n12 unverified tiles\nService tier: standard\n", []),
    ("4_detect --service-tier standard && run_pv.py verify --service-tier flex\n", ["flex"]),
    ("Service tier: flex\nrun_pv.py verify --c d\nService tier: standard\n", ["standard"]),
])
def test_verifier_tiers_need_a_verifier_command(log, verifier_tiers):
    from scripts.derive_tier_evidence import parse_log
    assert parse_log(log)["verifier_tiers"] == verifier_tiers


def _leg(tmp_path: Path, results: int, **meta_extra) -> tuple[dict, Path]:
    leg = tmp_path / "run" / "v"
    meta = _meta(leg / "run.meta.json", **meta_extra)
    (leg / "probabilities.json").write_text(json.dumps(
        {"results": {f"c{i}": 0.5 for i in range(results)}, "iterations": 1}))
    return meta


@pytest.mark.tier1
@pytest.mark.parametrize(("done", "partial"), [(89, True), (91, False)])
def test_coverage_floor_is_ninety_percent(evidence, tmp_path, done, partial):
    meta = _leg(tmp_path, 100, execution_stats={"completed_items": [f"c{i}" for i in range(done)]})
    out = _cost(evidence(), [meta], tmp_path / "run", stage="verifier")
    assert (out["cost_basis"] == "audited-lower-bound") is partial


@pytest.mark.tier1
def test_coverage_reads_processed_items_and_scales_requests_by_iterations(tmp_path):
    meta, path = _leg(tmp_path, 100, execution_stats={"items_processed": 100})
    assert verifier_coverage([(meta, path)]) == (100, 100)
    (path.parent / "probabilities.json").write_text(json.dumps(
        {"results": {f"c{i}": 0.5 for i in range(100)}, "iterations": 3}))
    calls = {**meta, "execution_stats": {},
             "usage_stats": {**USAGE, "by_provider": {"google_gemini": {"request_count": 150}}}}
    assert verifier_coverage([(calls, path)]) == (50, 100)  # 150 calls over 3 rounds


@pytest.mark.tier1
def test_gemini3_batch_verifier_legs_are_whole():
    # They record only processed items; dropping that count would make all
    # three floors (re-audit round 2, surviving mutation 2).
    from scripts.generate_post_run_report import extract_passes, extraction_context
    rows = [r for r in extract_passes(extraction_context("gemini3-image-55map-2026-09-16"))
            if "verify" in r["proposer_pool"] and "arm2" in r["proposer_pool"]]
    assert rows and all(r["cost_basis"] == "audited" for r in rows)


@pytest.mark.tier1
def test_own_directory_reads_the_stage_own_record(evidence, tmp_path):
    run = tmp_path / "run"
    leg = run / "v"
    logs = {_rel(leg): {**LOG_ENTRY, "tiers": ["flex"], "verifier_tiers": ["standard"]}}
    v = _cost(evidence(logs=logs), [_meta(leg / "run.meta.json")], run, stage="verifier")
    assert v["cost_source"]["fragments"][0]["tier"] == "standard"
    pdir = run / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": [], "verifier_tiers": ["standard"]}}
    p = _cost(evidence(logs=logs), [_meta(pdir / "a.meta.json")], run)
    assert p["cost_source"]["fragments"][0]["tier"] is None  # not the verifier's tier


@pytest.mark.tier1
def test_a_verifier_never_takes_the_run_level_manifest_tier(evidence, tmp_path):
    run = tmp_path / "run"
    (run / "v").mkdir(parents=True)
    (run / "launch_manifest.json").write_text(json.dumps({"service_tier": "flex"}))
    frag = _cost(evidence(), [_meta(run / "v" / "run.meta.json")], run, stage="verifier")[
        "cost_source"]["fragments"][0]
    assert frag["tier"] is None


@pytest.mark.tier1
def test_a_floor_note_keeps_every_reason(evidence, tmp_path):
    run = tmp_path / "run"
    coster = evidence(published={"r::p::run1": {"basis": "audited-lower-bound",
                                                "source": "cleanup overwrote it"}})
    metas = [_meta(run / "p" / "run_1" / "a.meta.json"),
             _meta(run / "p" / "run_1_recovery" / "b.meta.json", usage={k: 0 for k in USAGE})]
    note = _cost(coster, metas, run)["cost_source"]["note"]
    assert "cleanup overwrote it" in note and "recorded no usage" in note


@pytest.mark.tier1
def test_a_preserved_main_leg_is_priced_with_its_cleanup():
    # Re-audit round 2, M6: swap38's run.meta.json is a 1-request cleanup; the
    # tracked run.meta.main-2026-09-04.json holds the 790-candidate main leg.
    row = _committed_pass("gemini37-screen-2026-08-28", "g384_ov192_g37-union-k5-verify-swap38",
                          1)
    metas = [f["meta"] for f in row["cost_source"]["fragments"]]
    assert any(m.endswith("run.meta.main-2026-09-04.json") for m in metas)
    assert row["cost_basis"] != "audited-lower-bound" and row["cost_usd"] > 0.8
    assert row["n_candidates_verified"] >= 790


@pytest.mark.tier1
def test_c3_refuses_an_upper_bound_relabelled_audited():
    row = _first_row_with("audited-upper-bound")
    src = {k: v for k, v in row["cost_source"].items() if k != "bounds_usd"}
    assert _c3({**row, "cost_basis": "audited", "cost_source": src})["cost_basis"][
        "verdict"] == "MISMATCH"


@pytest.mark.tier1
def test_c3_refuses_a_fragment_falsely_claiming_no_usage():
    row = _committed_pass("flash35-pv-2x2", "flash35-min-text-1of10", 3)
    frags = [dict(f) for f in row["cost_source"]["fragments"]]
    frags[1].update(tier=None, tier_method="not-needed: no usage recorded")
    frags[1].pop("candidates", None)
    bad = {**row, "cost_usd": round(row["cost_usd"] - frags[1]["cost_usd"], 6),
           "cost_source": {**row["cost_source"], "fragments": frags}}
    assert _c3(bad)["cost_source.fragments.stamps"]["verdict"] == "MISMATCH"


@pytest.mark.tier1
def test_c3_refuses_an_overwritten_leg_labelled_audited():
    row = _committed_pass("flash35-pv-2x2", "verified-f3vf", 1)
    assert _c3(row)["cost_basis"]["verdict"] == "MATCH"
    assert _c3({**row, "cost_basis": "audited"})["cost_basis"]["verdict"] == "MISMATCH"


@pytest.mark.tier1
def test_c3_derives_a_partial_pass_at_its_floor(monkeypatch):
    import scripts.rederive_manifest_fields as c3
    row = _first_row_with("audited-upper-bound")
    low = row["cost_source"]["bounds_usd"]["low"]
    monkeypatch.setattr(c3, "_overrides", lambda: {row["pass_id"]: {
        "basis": "audited-lower-bound", "source": "test"}})
    floor = {**row, "cost_basis": "audited-lower-bound", "cost_usd": low}
    assert _c3(floor)["cost_usd"]["verdict"] == "MATCH"
    assert _c3(floor)["cost_basis"]["verdict"] == "MATCH"
    assert _c3({**floor, "cost_usd": row["cost_usd"]})["cost_usd"]["verdict"] == "MISMATCH"


@pytest.mark.tier1
def test_c3_partial_and_unpriceable_reasons_are_derived_from_the_metas():
    from scripts.rederive_manifest_fields import _partial_reasons, _unpriceable_reason
    used = {"usage_stats": USAGE, "timestamp": {"end": "2026-05-20T00:00:00+00:00"}}
    empty = {"usage_stats": {k: 0 for k in USAGE}}
    row = {"pass_id": "x::y::run1", "model_used": "gemini-3-flash-preview",
           "n_tiles_processed": 5}
    assert _partial_reasons(row, [used, empty], []) == ["unrecorded fragment"]
    assert _partial_reasons(row, [used], []) == []
    assert _unpriceable_reason(row, [used]) is None
    assert "no timestamp" in _unpriceable_reason(row, [{"usage_stats": USAGE}])
    own = {**used, "per_item_metadata": [{"model_used": "gemini-9-imaginary"}]}
    assert "gemini-9-imaginary" in _unpriceable_reason(row, [own])
    early = {"usage_stats": USAGE, "timestamp": {"end": "2025-01-01T00:00:00+00:00"}}
    assert "no rate card row" in _unpriceable_reason(row, [early])


# ---------------------------------------------------------------------------
# Audit round 4 (third re-audit, 2026-10-03).
# ---------------------------------------------------------------------------


@pytest.mark.tier1
@pytest.mark.parametrize(("log", "verifier_tiers"), [
    ("run_pv.py verify --x y --service-tier flex && 4_detect --service-tier standard\n", ["flex"]),
    ("run_pv.py verify --x y --service-tier flex & 4_detect --service-tier standard\n", ["flex"]),
    ("python scripts/run_pv.py extract --service-tier flex\n", []),
])
def test_a_verifier_switch_is_read_from_its_own_command_only(log, verifier_tiers):
    from scripts.derive_tier_evidence import parse_log
    assert parse_log(log)["verifier_tiers"] == verifier_tiers


@pytest.mark.tier1
def test_preserved_main_legs_are_main_files_with_a_new_run_id(tmp_path):
    from scripts.generate_post_run_report import _preserved_main_legs
    leg = tmp_path / "v"
    leg.mkdir()
    primary = {"run_id": "C"}
    for name, run_id in (("run.meta.json", "C"), ("run.meta.main-2026-09-04.json", "M"),
                         ("run.meta.main-2026-09-05.json", "M"),
                         ("run.meta.main-2026-09-06.json", "C"),
                         ("run.meta.pre-rerun-1.json", "R"), ("run.meta.pre-cleanup-1.json", "C")):
        (leg / name).write_text(json.dumps({"run_id": run_id}))
    got = _preserved_main_legs(primary, leg / "run.meta.json")
    assert [g.name for g in got] == ["run.meta.main-2026-09-04.json"]
    assert _preserved_main_legs(primary, leg / "verified-x.meta.json") == []


@pytest.mark.tier1
def test_superseded_reruns_are_not_priced():
    from scripts.generate_post_run_report import extract_passes, extraction_context
    rows = extract_passes(extraction_context("gemini3-image-55map-2026-09-16"))
    for r in rows:
        assert not any("pre-rerun" in f["meta"] for f in r["cost_source"].get("fragments", []))


@pytest.mark.tier1
def test_the_swap38_leg_with_its_main_meta_certifies_in_every_field():
    # Re-audit round 3, M1-M3: fragments, status, wall clock, start time and
    # retries all derive across the main leg and its cleanup.
    row = _committed_pass("gemini37-screen-2026-08-28",
                          "g384_ov192_g37-union-k5-verify-swap38", 1)
    assert any("run.meta.main-" in s for s in row["provenance"]["source_files"])
    assert row["tokens"]["total"] > 1_500_000 and row["n_candidates_verified"] == 791
    verdicts = {k: v["verdict"] for k, v in _c3(row).items()}
    for field in ("cost_source.fragments", "cost_usd", "cost_basis", "status", "wall_clock_s",
                  "timestamps.start", "timestamps.end", "retries", "n_candidates_verified",
                  "tokens.total"):
        assert verdicts[field] == "MATCH", (field, verdicts[field])


@pytest.mark.tier1
@pytest.mark.parametrize(("done", "expected"), [((50, 45), (95, 100)), ((10,), (10, 100))])
def test_coverage_sums_the_leg_and_counts_completions_first(tmp_path, done, expected):
    leg = tmp_path / "v"
    leg.mkdir()
    (leg / "probabilities.json").write_text(json.dumps(
        {"results": {f"c{i}": 0.5 for i in range(100)}, "iterations": 1}))
    metas = []
    for n, k in enumerate(done):
        usage = {**USAGE, "by_provider": {"google_gemini": {"request_count": 300}}}
        metas.append(({"execution_stats": {"completed_items": [f"m{n}-{i}" for i in range(k)]},
                       "usage_stats": usage}, leg / f"run.meta{n}.json"))
    assert verifier_coverage(metas) == expected


@pytest.mark.tier1
def test_c3_reads_the_spread_of_every_fragment():
    # An upper bound decided by an EARLIER fragment must still certify.
    rows = json.loads((REPO / "results/passes-manifest.json").read_text())["passes"]
    cases = [r for r in rows if r["cost_basis"] == "audited-upper-bound"
             and len(r["cost_source"]["fragments"]) > 1
             and "candidates" not in r["cost_source"]["fragments"][-1]]
    assert cases, "no committed upper bound whose last fragment is pinned"
    assert _c3(cases[0])["cost_basis"]["verdict"] == "MATCH"


@pytest.mark.tier1
def test_an_unrecorded_pass_leaves_the_run_total_without_a_ceiling():
    from scripts.generate_run_reports import _total_range
    passes = [{"cost_basis": "audited", "cost_usd": 1.0},
              {"cost_basis": "unrecorded", "cost_usd": None}]
    assert _total_range(passes) == "at least US$1.0000; no ceiling (1 unrecorded pass(es))"


@pytest.mark.tier1
def test_log_evidence_cites_only_the_logs_that_supplied_the_tier(evidence, tmp_path):
    pdir = tmp_path / "run" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"], "logs": [
        {"path": "x/launch.log", "tiers": ["flex"], "verifier_tiers": []},
        {"path": "x/notes.log", "tiers": [], "verifier_tiers": ["standard"]}]}}
    frag = _cost(evidence(logs=logs), [_meta(pdir / "a.meta.json")], tmp_path / "run")[
        "cost_source"]["fragments"][0]
    ref = next(e for e in frag["evidence"] if e.startswith("run-log"))
    assert "launch.log" in ref and "notes.log" not in ref


# ---------------------------------------------------------------------------
# Audit round 5 (fourth re-audit, 2026-10-03): the helpers it found untested.
# ---------------------------------------------------------------------------


@pytest.mark.tier1
@pytest.mark.parametrize(("log", "verifier_tiers"), [
    ("run_pv.py verify --x y 2>&1 --service-tier flex\n", ["flex"]),
    ("run_pv.py verify --x y &>log --service-tier flex\n", ["flex"]),
    ("run_pv.py verify --url 'h?a=1&b=2' --service-tier flex\n", ["flex"]),
    ("Run `run_pv.py cleanup` to retry\nService tier: standard\n", []),
])
def test_redirects_and_quoted_hints_do_not_break_a_verifier_command(log, verifier_tiers):
    from scripts.derive_tier_evidence import parse_log
    assert parse_log(log)["verifier_tiers"] == verifier_tiers


@pytest.mark.tier1
def test_span_compares_instants_not_strings():
    from scripts.generate_post_run_report import _span
    a = {"start": "2026-09-04T14:00:00+10:00", "end": "2026-09-04T14:39:16+10:00"}
    b = {"start": "2026-09-04T04:40:40+00:00", "end": "2026-09-04T04:41:00+00:00"}
    # 14:00+10:00 is 04:00 UTC, before 04:40 UTC; a string comparison gets both wrong.
    assert _span([a, b]) == {"start": a["start"], "end": b["end"]}
    assert _span([None, b]) == b
    assert _span([None]) is None


@pytest.mark.tier1
def test_sum_or_none_keeps_null_when_nothing_was_recorded():
    from scripts.generate_post_run_report import _sum_or_none
    assert _sum_or_none([None, None]) is None
    assert _sum_or_none([2.5, None, 1.0]) == 3.5


@pytest.mark.tier1
def test_verifier_candidates_count_over_every_meta():
    from scripts.generate_post_run_report import _verifier_candidates
    p = Path("x")
    done = [({"execution_stats": {"completed_items": ["a", "b"]}}, p),
            ({"execution_stats": {"completed_items": ["b", "c"]}}, p)]
    assert _verifier_candidates(done) == 3  # a union, not a sum
    processed = [({"execution_stats": {"items_processed": 5}}, p),
                 ({"execution_stats": {"items_processed": 2}}, p)]
    assert _verifier_candidates(processed) == 7
    calls = [({"usage_stats": {"by_provider": {"google_gemini": {"request_count": 4}}}}, p),
             ({"usage_stats": {"by_provider": {"google_gemini": {"request_count": 1}}}}, p)]
    assert _verifier_candidates(calls) == 5


@pytest.mark.tier1
@pytest.mark.parametrize(("source", "is_meta"), [
    ("outputs/r/p/run_1/detections-x.meta.json", True),
    ("outputs/r/p/run_1/detections-x.meta.json.gz", True),
    ("outputs/r/v/run.meta.json", True),
    ("outputs/r/v/run.meta.main-2026-09-04.json", True),
    ("outputs/r/v/run.meta.json.pre-recovery-20260502T235106.backup", True),
    ("outputs/r/v/run.meta.json.tmp", False),
    ("outputs/r/p/run_1/detections-x.meta.json.tmp", False),
    ("results/run-conditions.json", False),
    ("outputs/r/v/run.log", False),
    ("outputs/r/v/probabilities.json", False),
])
def test_c3_knows_which_cited_sources_are_metas(source, is_meta):
    from scripts.rederive_manifest_fields import _is_meta
    assert _is_meta(source) is is_meta


@pytest.mark.tier1
def test_a_basis_priced_at_zero_still_has_a_figure():
    from scripts.generate_run_reports import _basis_sums
    assert _basis_sums([{"cost_basis": "audited", "cost_usd": 0.0}]) == "audited US$0.0000 (1)"


# ---------------------------------------------------------------------------
# Round-5 re-audit: each half of the command splitter and C3's instants.
# ---------------------------------------------------------------------------


@pytest.mark.tier1
@pytest.mark.parametrize(("log", "verifier_tiers"), [
    ("run_pv.py verify --x y >& log --service-tier flex\n", ["flex"]),   # lookbehind '>'
    ("run_pv.py verify --x 'h?a=x&b=y' --service-tier flex\n", ["flex"]),  # lookahead word
    ("Run `5_verify_crops --x` to retry\nService tier: standard\n", []),  # quoted hint
])
def test_each_half_of_the_command_splitter_holds(log, verifier_tiers):
    from scripts.derive_tier_evidence import parse_log
    assert parse_log(log)["verifier_tiers"] == verifier_tiers


@pytest.mark.tier1
def test_c3_compares_timestamps_as_instants(tmp_path, monkeypatch):
    # Two cited metas stamped in different offsets: 14:00+10:00 (04:00 UTC)
    # starts before 04:40+00:00, which a string comparison gets backwards.
    import scripts.rederive_manifest_fields as c3
    monkeypatch.setattr(c3, "REPO_ROOT", tmp_path)
    stamps = [("a.meta.json", "2026-09-04T14:00:00+10:00", "2026-09-04T14:30:00+10:00"),
              ("b.meta.json", "2026-09-04T04:40:00+00:00", "2026-09-04T04:41:00+00:00")]
    for name, start, end in stamps:
        _write(tmp_path / "outputs" / "r" / name,
               {"usage_stats": {}, "timestamp": {"start": start, "end": end,
                                                 "duration_seconds": 60}})
    row = {"pass_id": "r::p::run1", "run_id": "r", "proposer_pool": "p", "pass_n": 1,
           "model_used": "gemini-3-flash-preview", "status": "ok", "n_tiles_processed": 1,
           "tokens": None, "cost_usd": None, "cost_basis": "unrecorded",
           "cost_source": {"rate_card": {}, "fragments": []},
           "timestamps": {"start": stamps[0][1], "end": stamps[1][2]},
           "provenance": {"source_files": [f"outputs/r/{n}" for n, _, _ in stamps]}}
    verdicts = {f["field"]: f["verdict"] for f in c3.rederive_pass(row)["fields"]}
    assert verdicts["timestamps.start"] == "MATCH"
    assert verdicts["timestamps.end"] == "MATCH"


# ---------------------------------------------------------------------------
# The applied-tier header (2026-10-03): the API's own record of the billed tier.
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_an_applied_header_outranks_every_request_record(evidence, tmp_path):
    pdir = tmp_path / "run" / "p" / "run_1"
    # A launch line and an explicit cache both say otherwise; the API said flex.
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["standard"], "explicit_cache": True}}
    meta = _meta(pdir / "a.meta.json",
                 per_item_metadata=[{"service_tier_applied": "flex"}] * 3)
    frag = _cost(evidence(logs=logs), [meta], tmp_path / "run")["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("flex", "applied-header")


@pytest.mark.tier1
def test_mixed_applied_tiers_bound_rather_than_pin(evidence, tmp_path):
    meta = _meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json",
                 per_item_metadata=[{"service_tier_applied": "flex"},
                                    {"service_tier_applied": "standard"}])
    out = _cost(evidence(), [meta], tmp_path / "r")
    assert out["cost_basis"] == "audited-upper-bound"
    assert set(out["cost_source"]["fragments"][0]["candidates"]) == {"flex", "standard"}


@pytest.mark.tier1
def test_the_tracker_records_the_applied_tier_from_the_header():
    from datetime import datetime, timezone

    from scripts.lib_llm_metadata import applied_service_tier, extract_gemini_metadata

    class Headers:
        headers = {"X-Gemini-Service-Tier": "flex"}

    class Response:
        sdk_http_response = Headers()
        usage_metadata = None

    assert applied_service_tier(Response()) == "flex"
    record = extract_gemini_metadata(Response(), datetime.now(timezone.utc)).to_dict()
    assert record["service_tier_applied"] == "flex"


# ---------------------------------------------------------------------------
# PI rulings D20-D22 (2026-10-03).
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_an_attestation_can_pin_one_fragment_of_a_pass(evidence, tmp_path):
    run = tmp_path / "run"
    leg = run / "v"
    att = [{"id": "A1", "run_id": "r", "pool": "*", "meta": _rel(leg / "run.meta.main-x.json"),
            "tier": "flex", "attested_by": "PI", "attested_on": "2026-10-03", "evidence": "x"}]
    main = _meta(leg / "run.meta.main-x.json")
    cleanup = _meta(leg / "run.meta.json")
    coster = evidence(attestations=att)  # after the metas: the glob must match a file
    frags = _cost(coster, [cleanup, main], run, stage="verifier")["cost_source"]["fragments"]
    by_name = {f["meta"].rsplit("/", 1)[-1]: f for f in frags}
    assert by_name["run.meta.main-x.json"]["tier_method"] == "attestation"
    assert by_name["run.meta.json"]["tier_method"] != "attestation"


@pytest.mark.tier1
def test_th7_verifier_is_priced_from_its_force_added_backup():
    # D20: the gitignored main leg, committed and named in cost-overrides.
    row = _committed_pass("55maps-text-high-generalisation", "verified", 1)
    names = [f["meta"].rsplit("/", 1)[-1] for f in row["cost_source"]["fragments"]]
    assert "run.meta.json.pre-recovery-20260502T235106.backup" in names
    assert row["cost_basis"] == "audited" and row["cost_usd"] == pytest.approx(6.420148)
    assert row["n_candidates_verified"] == 9_205
    assert _c3(row)["cost_source.fragments"]["verdict"] == "MATCH"


@pytest.mark.tier1
def test_swap38_is_attested_per_its_notes():
    # D21: main leg flex, cleanup standard (planning/gemini38-screen-2026-09-04.md).
    row = _committed_pass("gemini37-screen-2026-08-28",
                          "g384_ov192_g37-union-k5-verify-swap38", 1)
    tiers = {f["meta"].rsplit("/", 1)[-1]: (f["tier"], f["tier_method"])
             for f in row["cost_source"]["fragments"]}
    assert tiers["run.meta.main-2026-09-04.json"] == ("flex", "attestation")
    assert tiers["run.meta.json"] == ("standard", "attestation")
    assert row["cost_basis"] == "audited"


@pytest.mark.tier1
def test_the_superseded_ledger_is_consistent_and_never_priced_in_the_register():
    # D22: superseded spend is in the project total, never in a pass's cost.
    import subprocess
    doc = json.loads((REPO / "data/pricing/superseded-executions.json").read_text())
    priced = [e for e in doc["executions"] if e["cost_usd"] is not None]
    assert doc["priced_total_usd"] == pytest.approx(sum(e["cost_usd"] for e in priced))
    rows = json.loads((REPO / "results/passes-manifest.json").read_text())["passes"]
    cited = {s for r in rows for s in r["provenance"]["source_files"]}
    for e in priced:
        assert (REPO / e["meta"]).exists()
        assert subprocess.run(["git", "ls-files", "--error-unmatch", e["meta"]], cwd=REPO,
                              capture_output=True).returncode == 0
        assert e["meta"] not in cited


# ---------------------------------------------------------------------------
# Round 7 (2026-10-03): the served tier at run level, its coverage, and the
# cached-path rule's end at the fix.
# ---------------------------------------------------------------------------

#: Commits either side of the cached-path fix (2df65047e), for the ancestry test.
BEFORE_FIX = "2ce4536ea"        # 2026-08-31, live at swap38's launch
FIX_PARENT = "50bfec432"        # the commit just before the fix
MAIN_AT_BRANCH = "e10d50dd0"    # main when this branch left it: no fix
FIX_COMMIT = "2df65047e"
AFTER_FIX = "651a2eb90"         # header capture, which the probe runs used
AFTER_FIX_FULL = "651a2eb902228d1202ff8389ad824588fdc06c62"


def _counted(counts: dict, requests: int) -> dict:
    """Usage with run-level served-tier counts and the provider's request count."""
    return {**USAGE, "served_tier_counts": counts,
            "by_provider": {"google_gemini": {"request_count": requests}}}


@pytest.mark.tier1
def test_served_tiers_read_run_level_counts_before_per_item_records():
    from scripts.lib_pass_cost import served_tiers
    # merge_meta sums the counts with the tokens but deduplicates per-item
    # records, so the run-level count is the one that matches the usage.
    meta = {"usage_stats": _counted({"flex": 4}, 4),
            "per_item_metadata": [{"service_tier_applied": "standard"}]}
    assert served_tiers(meta) == ({"flex": 4}, 4)
    assert served_tiers({"usage_stats": _counted({"Flex": 2, "FLEX": 1}, 3)}) == ({"flex": 3}, 3)
    assert served_tiers({"usage_stats": _counted({"unreported": 3}, 3)}) is None


@pytest.mark.tier1
@pytest.mark.parametrize("header", ["flex", "Flex", "FLEX"])
def test_a_full_header_pins_whatever_its_case(evidence, tmp_path, header):
    meta = _meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json",
                 per_item_metadata=[{"service_tier_applied": header}] * 2)
    frag = _cost(evidence(), [meta], tmp_path / "r")["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("flex", "applied-header")


@pytest.mark.tier1
def test_a_verifier_leg_is_pinned_by_run_level_counts_alone(evidence, tmp_path):
    # run_pv verify finalises without per-item records; the run-level count
    # is the only place its served tier survives.
    leg = tmp_path / "r" / "verified"
    meta = _meta(leg / "run.meta.json", usage=_counted({"flex": 10}, 10))
    out = _cost(evidence(), [meta], tmp_path / "r", stage="verifier")
    frag = out["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("flex", "applied-header")
    assert out["cost_usd"] == pytest.approx(FLEX_USD) and out["cost_basis"] == "audited"


@pytest.mark.tier1
def test_a_partial_header_widens_the_records_rather_than_narrowing(evidence, tmp_path):
    # Two of three responses reported standard; the launch line asked for
    # flex. The third may have run at either, so both are candidates.
    pdir = tmp_path / "r" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"]}}
    meta = _meta(pdir / "a.meta.json", usage=_counted({"standard": 2, "unreported": 1}, 3))
    out = _cost(evidence(logs=logs), [meta], tmp_path / "r")
    frag = out["cost_source"]["fragments"][0]
    assert out["cost_basis"] == "audited-upper-bound"
    assert set(frag["candidates"]) == {"flex", "standard"}
    assert (frag["tier"], frag["tier_method"]) == (None, "unresolved")
    assert any("widens flex" in n for n in frag["notes"])
    assert any(e.startswith("applied-header-partial") for e in frag["evidence"])
    assert "conflicts" not in frag  # a partial record is never set against a pin


@pytest.mark.tier1
def test_a_partial_header_agreeing_with_the_pin_keeps_it(evidence, tmp_path):
    # Negative: a partial header that names only the pinned tier changes nothing.
    pdir = tmp_path / "r" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"]}}
    meta = _meta(pdir / "a.meta.json", usage=_counted({"flex": 2, "unreported": 1}, 3))
    frag = _cost(evidence(logs=logs), [meta], tmp_path / "r")["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("flex", "run-log")
    assert "notes" not in frag and "conflicts" not in frag


@pytest.mark.tier1
def test_a_header_short_of_the_request_count_is_partial(evidence, tmp_path):
    # A meta that merged a pre-header leg: three counted responses of five.
    pdir = tmp_path / "r" / "p" / "run_1"
    meta = _meta(pdir / "a.meta.json", usage=_counted({"standard": 3}, 5))
    out = _cost(evidence(), [meta], tmp_path / "r")
    frag = out["cost_source"]["fragments"][0]
    # Nothing else speaks for the two unreported responses: every tier stays
    # a candidate, so the partial record neither pins nor narrows.
    assert (frag["tier"], frag["tier_method"]) == (None, "unresolved")
    assert set(frag["candidates"]) == {"standard", "flex", "batch"}
    assert out["cost_basis"] == "audited-upper-bound"
    assert any(e.startswith("applied-header-partial") for e in frag["evidence"])
    assert "conflicts" not in frag


@pytest.mark.tier1
@pytest.mark.parametrize("usage", [
    _counted({"flex": 3, "unreported": 97}, 100),              # run-level counts
    {**USAGE},                                                 # per-item records below
])
def test_a_partial_header_alone_never_lowers_the_price(evidence, tmp_path, usage):
    # SENTINEL for the understatement round 7 forbids: three of a hundred
    # responses said flex; read as a pin or a narrowing, the pass would be
    # priced at flex. It is priced at the dearest candidate.
    items = [{"service_tier_applied": "flex"}, {}] if "served_tier_counts" not in usage else []
    meta = _meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json", usage=usage,
                 per_item_metadata=items)
    out = _cost(evidence(), [meta], tmp_path / "r")
    assert out["cost_usd"] == pytest.approx(STANDARD_USD)
    assert out["cost_basis"] == "audited-upper-bound"


@pytest.mark.tier1
@pytest.mark.parametrize("counts", [{"flex": 2, "priority": 1}, {"priority": 3}])
def test_a_tier_the_card_does_not_price_makes_the_fragment_unpriceable(evidence, tmp_path,
                                                                        counts):
    # The API says it served some responses at a tier the rate card does not
    # know; any card tier, the requested one included, could understate them.
    pdir = tmp_path / "r" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"]}}
    meta = _meta(pdir / "a.meta.json", usage=_counted(counts, 3))
    out = _cost(evidence(logs=logs), [meta], tmp_path / "r")
    frag = out["cost_source"]["fragments"][0]
    assert out["cost_usd"] is None and out["cost_basis"] == "unpriceable"
    assert f"priority ({counts['priority']} of 3 responses)" in frag["unpriceable"]


@pytest.mark.tier1
def test_a_partial_header_against_the_invoice_is_a_conflict(evidence, tmp_path):
    # Two responses said standard on a day the invoice billed only flex: the
    # widening stands (no understatement), and the contradiction is reported.
    day = {"2026-05-20": {"project_filter": "unverified", "models": {
        "gemini-3-flash-preview": {"tiers": {"flex": {"output": 9_000_000}}}}}}
    meta = _meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json",
                 usage=_counted({"standard": 2, "unreported": 1}, 3))
    frag = _cost(evidence(billing={"days": day}), [meta],
                 tmp_path / "r")["cost_source"]["fragments"][0]
    assert set(frag["candidates"]) == {"standard", "flex"}
    assert any(c.startswith("applied-header-partial served standard but billing-day")
               for c in frag["conflicts"])


@pytest.mark.tier1
def test_a_mixed_full_header_overrules_a_request_pin_as_a_note(evidence, tmp_path):
    pdir = tmp_path / "r" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"]}}
    meta = _meta(pdir / "a.meta.json", usage=_counted({"flex": 2, "standard": 1}, 3))
    out = _cost(evidence(logs=logs), [meta], tmp_path / "r")
    frag = out["cost_source"]["fragments"][0]
    assert out["cost_basis"] == "audited-upper-bound"
    assert set(frag["candidates"]) == {"flex", "standard"}
    assert (frag["tier"], frag["tier_method"]) == (None, "unresolved")
    assert out["cost_usd"] == pytest.approx(STANDARD_USD)
    assert "conflicts" not in frag
    assert any("REQUESTED" in n and "served standard|flex" in n for n in frag["notes"])


@pytest.mark.tier1
def test_a_mixed_full_header_against_a_batch_marker_is_a_conflict(evidence, tmp_path):
    pdir = tmp_path / "r" / "p" / "run_1"
    meta = _meta(pdir / "a.meta.json", usage=_counted({"flex": 2, "standard": 1}, 3),
                 batch_api={"job": "x"})
    frag = _cost(evidence(), [meta], tmp_path / "r")["cost_source"]["fragments"][0]
    assert any("applied-header served" in c and "batch" in c for c in frag["conflicts"])
    assert (frag["tier"], frag["tier_method"]) == (None, "unresolved")


@pytest.mark.tier1
def test_a_mixed_full_header_against_the_invoice_is_a_conflict(evidence, tmp_path):
    # The billing day says only flex ran; the API says some responses were
    # standard. That is a contradiction to report, not a request to note.
    day = {"2026-05-20": {"project_filter": "unverified", "models": {
        "gemini-3-flash-preview": {"tiers": {"flex": {"output": 9_000_000}}}}}}
    meta = _meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json",
                 usage=_counted({"flex": 2, "standard": 1}, 3))
    frag = _cost(evidence(billing={"days": day}), [meta],
                 tmp_path / "r")["cost_source"]["fragments"][0]
    assert any("applied-header served" in c and "billing-day" in c for c in frag["conflicts"])


@pytest.mark.tier1
def test_a_single_tier_header_against_a_request_record_is_a_note(evidence, tmp_path):
    pdir = tmp_path / "r" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"]}}
    meta = _meta(pdir / "a.meta.json", usage=_counted({"standard": 3}, 3))
    frag = _cost(evidence(logs=logs), [meta], tmp_path / "r")["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("standard", "applied-header")
    assert "conflicts" not in frag
    assert any("REQUESTED" in n and "served standard" in n for n in frag["notes"])


@pytest.mark.tier1
@pytest.mark.parametrize(("commit", "subject"), [
    (BEFORE_FIX, True), (FIX_PARENT, True), (MAIN_AT_BRANCH, True),
    (FIX_COMMIT, False), (AFTER_FIX, False), (AFTER_FIX_FULL, False),
    ("0" * 40, True),          # a commit this clone does not hold: the rule stays
    (None, True),              # no commit recorded: the rule stays
    ("unknown", True),         # what the tracker writes when git is unavailable
])
def test_the_cached_path_rule_follows_the_code_a_run_executed(evidence, tmp_path, commit,
                                                              subject):
    # The rule is about the code, not the date: a run launched after the fix
    # from a checkout without it (main, before this branch merged) still
    # dropped its tier on the cached call.
    pdir = tmp_path / "r" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"], "explicit_cache": True}}
    meta = _meta(pdir / "a.meta.json", start="2026-10-04T10:00:00+00:00",
                 end="2026-10-04T11:00:00+00:00", environment={"git_commit": commit})
    frag = _cost(evidence(logs=logs), [meta], tmp_path / "r")["cost_source"]["fragments"][0]
    if subject:
        assert (frag["tier"], frag["tier_method"]) == ("standard", "cached-path")
    else:
        assert (frag["tier"], frag["tier_method"]) == ("flex", "run-log")
        assert not any(e.startswith("cached-path") for e in frag["evidence"])
        assert "conflicts" not in frag


@pytest.mark.tier1
def test_a_full_header_retires_the_cached_path_rule(evidence, tmp_path):
    # Before the fix, but every response said flex: the API's statement wins
    # and the rule is not even raised, so there is nothing to conflict.
    pdir = tmp_path / "r" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"], "explicit_cache": True}}
    meta = _meta(pdir / "a.meta.json", usage=_counted({"flex": 3}, 3))
    frag = _cost(evidence(logs=logs), [meta], tmp_path / "r")["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("flex", "applied-header")
    assert not any(e.startswith("cached-path") for e in frag["evidence"])
    assert "conflicts" not in frag


@pytest.mark.tier1
def test_a_partial_header_keeps_the_cached_path_rule_and_widens_it(evidence, tmp_path):
    # Before the fix, some responses reported flex: the cached path pins
    # standard for the rest, and flex is added, so the pass is bounded.
    pdir = tmp_path / "r" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"], "explicit_cache": True}}
    meta = _meta(pdir / "a.meta.json", usage=_counted({"flex": 1, "unreported": 2}, 3))
    out = _cost(evidence(logs=logs), [meta], tmp_path / "r")
    frag = out["cost_source"]["fragments"][0]
    assert set(frag["candidates"]) == {"flex", "standard"}
    assert (frag["tier"], frag["tier_method"]) == (None, "unresolved")
    assert out["cost_basis"] == "audited-upper-bound"
    assert "conflicts" not in frag


@pytest.mark.tier1
def test_the_live_probe_runs_resolve_by_their_served_tier():
    # The four adjacent runs of 2026-10-03, one per combination of the two
    # levers, through the real coster and the committed evidence.
    coster = PassCoster()
    run = REPO / "outputs" / "tier-cache-probe-2026-10-03"
    expected = {"run_A_flex_cache": "flex", "run_B_flex_nocache": "flex",
                "run_C_standard_cache": "standard", "run_D_standard_nocache": "standard"}
    for name, tier in expected.items():
        (path,) = (run / name).glob("*.meta.json")
        meta = json.loads(path.read_text())
        frag = coster.cost_fragment(meta=meta, meta_path=path, run_id=run.name, pool=name,
                                    run_dir=run, model="gemini-3-flash-preview")
        assert (frag["tier"], frag["tier_method"]) == (tier, "applied-header"), name
        assert "conflicts" not in frag, name


@pytest.mark.tier1
def test_the_tracker_counts_served_tiers_and_merges_sum_them():
    from scripts.lib_llm_metadata import (
        LLMMetadataTracker,
        LLMResponseMetadata,
        merge_cleanup_meta,
    )

    def tracked(tiers):
        tracker = LLMMetadataTracker({"model": "gemini-3-flash-preview"}, "x")
        for i, tier in enumerate(tiers):
            md = LLMResponseMetadata(provider="google_gemini",
                                     model_requested="gemini-3-flash-preview")
            md.service_tier_applied = tier
            tracker.log_response(f"c{i}", md)
        return tracker.finalise(include_per_item=False)

    main = tracked(["flex", "flex", None])
    assert main["usage_stats"]["served_tier_counts"] == {"flex": 2, "unreported": 1}
    assert "per_item_metadata" not in main  # the run_pv verify shape
    merged = merge_cleanup_meta(main, tracked(["standard"]))
    assert merged["usage_stats"]["served_tier_counts"] == {
        "flex": 2, "unreported": 1, "standard": 1}
    assert merged["main_pass"]["usage_stats"]["served_tier_counts"] == {
        "flex": 2, "unreported": 1}


@pytest.mark.tier1
def test_an_attestation_whose_meta_glob_matches_nothing_is_refused(evidence, tmp_path):
    leg = tmp_path / "run" / "v"
    _meta(leg / "run.meta.main-x.json")
    good = {"id": "A1", "run_id": "r", "pool": "*", "tier": "flex", "attested_by": "PI",
            "attested_on": "2026-10-03", "evidence": "x"}
    evidence(attestations=[{**good, "meta": _rel(leg / "run.meta.main-*.json")}])
    for bad, reason in ((_rel(leg / "run.meta.main-y.json"), "matches no file"),
                        (_rel(leg / "nope" / "*.json"), "matches no file"),
                        ("../x", "climbs out"), ("", "non-empty string"), (None, "non-empty")):
        with pytest.raises(ValueError, match=reason):
            evidence(attestations=[{**good, "meta": bad}])


@pytest.mark.tier1
def test_named_and_globbed_main_legs_are_deduplicated_together(tmp_path):
    from scripts.generate_post_run_report import _preserved_main_legs
    leg = tmp_path / "v"
    leg.mkdir()
    primary = {"run_id": "C"}
    for name, run_id in (("run.meta.json", "C"), ("run.meta.main-2026-09-04.json", "M"),
                         ("run.meta.json.pre-recovery-1.backup", "M"),
                         ("run.meta.json.pre-recovery-2.backup", "N"),
                         ("run.meta.json.pre-recovery-3.backup", "C")):
        (leg / name).write_text(json.dumps({"run_id": run_id}))
    named = str(leg / "run.meta.json.pre-recovery-2.backup")
    got = _preserved_main_legs(primary, leg / "run.meta.json", [named])
    assert [g.name for g in got] == ["run.meta.main-2026-09-04.json",
                                     "run.meta.json.pre-recovery-2.backup"]
    # Naming the globbed file again is not a second execution.
    again = _preserved_main_legs(primary, leg / "run.meta.json",
                                 [str(leg / "run.meta.main-2026-09-04.json")])
    assert [g.name for g in again] == ["run.meta.main-2026-09-04.json"]
    # A named file that would not be priced is an error, never a silent drop:
    # the globbed leg's run_id again, the primary's, or a missing file.
    for bad in ("run.meta.json.pre-recovery-1.backup", "run.meta.json.pre-recovery-3.backup"):
        with pytest.raises(ValueError, match="would not be priced"):
            _preserved_main_legs(primary, leg / "run.meta.json", [str(leg / bad)])
    with pytest.raises(ValueError, match="missing"):
        _preserved_main_legs(primary, leg / "run.meta.json", [str(leg / "absent.json")])
    # A mis-keyed entry naming another leg's file is refused, not priced here.
    other = tmp_path / "elsewhere" / "v"  # the same leg name under another pool
    other.mkdir(parents=True)
    (other / "run.meta.json.pre-recovery-9.backup").write_text(json.dumps({"run_id": "Z"}))
    with pytest.raises(ValueError, match="do not sit beside"):
        _preserved_main_legs(primary, leg / "run.meta.json",
                             [str(other / "run.meta.json.pre-recovery-9.backup")])


@pytest.mark.tier1
def test_every_override_and_named_leg_is_keyed_to_a_register_pass():
    # A key that matches no pass is never read, so its figure or leg would
    # silently not apply (re-audit A, L7).
    doc = json.loads((REPO / "data/pricing/cost-overrides.json").read_text())
    ids = {r["pass_id"] for r in json.loads(
        (REPO / "results/passes-manifest.json").read_text())["passes"]}
    for section in ("entries", "preserved_main_legs"):
        for key in doc.get(section, {}):
            assert key in ids, f"{section}: {key}"


# ---------------------------------------------------------------------------
# Round-7 re-audit (lens B): end to end, executed doctests, the ledger.
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_a_verifier_meta_written_by_the_tracker_is_priced_at_its_served_tier(evidence,
                                                                             tmp_path):
    # End to end on the run_pv verify shape: the real tracker, finalised
    # WITHOUT per-item records, written to disc, read back and priced.
    from scripts.lib_llm_metadata import LLMMetadataTracker, LLMResponseMetadata, TokenUsage
    tracker = LLMMetadataTracker({"model": "gemini-3-flash-preview"}, "x")
    for i in range(4):
        md = LLMResponseMetadata(provider="google_gemini",
                                 model_requested="gemini-3-flash-preview",
                                 tokens=TokenUsage(input_tokens=250_000, output_tokens=25_000,
                                                   thoughts_tokens=50_000,
                                                   total_tokens=325_000))
        md.service_tier_applied = "flex"
        tracker.log_response(f"candidate_{i:05d}", md)
    meta = tracker.finalise(include_per_item=False)
    assert "per_item_metadata" not in meta
    meta["timestamp"] = {"start": "2026-05-20T10:00:00+00:00",
                         "end": "2026-05-20T11:00:00+00:00", "duration_seconds": 3600.0}
    path = _write(tmp_path / "r" / "verified" / "run.meta.json", meta)
    loaded = json.loads(path.read_text())
    out = _cost(evidence(), [(loaded, path)], tmp_path / "r", stage="verifier")
    frag = out["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("flex", "applied-header")
    assert out["cost_basis"] == "audited"
    assert out["cost_usd"] == pytest.approx(FLEX_USD)


@pytest.mark.tier1
def test_the_live_probe_runs_retire_the_cached_path_rule(evidence):
    # The committed probe metas beneath a log recording an explicit cache and
    # both tiers (as the probe's own logs do): each run is priced at the tier
    # the API served, and the cached-path rule is not raised against any.
    run = REPO / "outputs" / "tier-cache-probe-2026-10-03"
    coster = evidence(logs={_rel(run): {**LOG_ENTRY, "tiers": ["flex", "standard"],
                                        "explicit_cache": True}})
    for name, tier in (("run_A_flex_cache", "flex"), ("run_C_standard_cache", "standard")):
        (path,) = (run / name).glob("*.meta.json")
        frag = coster.cost_fragment(meta=json.loads(path.read_text()), meta_path=path,
                                    run_id=run.name, pool=name, run_dir=run,
                                    model="gemini-3-flash-preview")
        assert (frag["tier"], frag["tier_method"]) == (tier, "applied-header"), name
        assert not any(e.startswith("cached-path") for e in frag["evidence"]), name
        assert "conflicts" not in frag, name


@pytest.mark.tier1
@pytest.mark.parametrize("module", ["scripts.lib_pass_cost", "scripts.lib_llm_metadata"])
def test_the_docstring_examples_run(module):
    # pytest.ini does not collect doctests, so the examples are run here.
    import doctest
    import importlib
    result = doctest.testmod(importlib.import_module(module))
    assert result.attempted > 0 and result.failed == 0


@pytest.mark.tier1
@pytest.mark.parametrize(("pattern", "reason"), [
    ("*/run.meta.json", "too broad"),
    ("outputs/*/run.meta.json", "too broad"),
    ("x.json", "matches no file"),
    (str(REPO / "data/pricing/tier-attestations.json"), "repository-relative"),
])
def test_an_attestation_glob_that_could_never_apply_says_why(pattern, reason):
    from scripts.lib_pass_cost import attestation_glob_problem
    assert reason in attestation_glob_problem(pattern)
    # The same file, written repository-relative, is accepted.
    assert attestation_glob_problem("data/pricing/tier-attestations.json") is None


@pytest.mark.tier1
def test_the_superseded_ledger_reprices_and_points_at_real_passes():
    # Every entry with a meta: the file is tracked, uncited by any pass, and
    # (where priced) re-prices exactly at its tier and end date; every
    # superseded_by names a register pass.
    import subprocess

    from scripts.lib_cost import price_usage
    doc = json.loads((REPO / "data/pricing/superseded-executions.json").read_text())
    rows = json.loads((REPO / "results/passes-manifest.json").read_text())["passes"]
    ids = {r["pass_id"] for r in rows}
    cited = {s for r in rows for s in r["provenance"]["source_files"]}
    for e in doc["executions"]:
        if e.get("superseded_by"):
            assert e["superseded_by"] in ids, e["superseded_by"]
        if not e.get("meta"):
            assert e["cost_usd"] is None
            continue
        assert subprocess.run(["git", "ls-files", "--error-unmatch", e["meta"]], cwd=REPO,
                              capture_output=True).returncode == 0, e["meta"]
        assert e["meta"] not in cited
        meta = json.loads((REPO / e["meta"]).read_text())
        if e["cost_usd"] is None:
            assert not (meta.get("usage_stats") or {}).get("total_input_tokens")
            continue
        assert e["model"] == meta["configuration"]["model"], e["meta"]  # not the entry's say-so
        tier = "flex" if e["tier"].startswith("flex") else e["tier"]
        priced = price_usage(meta["usage_stats"], e["model"], tier,
                             at=meta["timestamp"]["end"][:10])["total_cost_usd"]
        assert priced == pytest.approx(e["cost_usd"], abs=5e-7), e["meta"]


@pytest.mark.tier1
def test_a_withdrawn_ledger_entry_is_inside_its_live_meta():
    # SENTINEL for the US$27.85 double count found before merge: a batch
    # leg's pre-rerun sidecar is a snapshot of the jobs its live meta already
    # prices, so it must never return to the priced executions.
    doc = json.loads((REPO / "data/pricing/superseded-executions.json").read_text())
    listed = {e.get("meta") for e in doc["executions"]}
    assert len(doc["withdrawn"]) == 2
    for w in doc["withdrawn"]:
        assert w["meta"] not in listed and w["reason"]
        sidecar = json.loads((REPO / w["meta"]).read_text())
        live = json.loads((REPO / w["meta"]).with_name("run.meta.json").read_text())
        for section, key in (("execution_stats", "items_processed"),
                             ("usage_stats", "total_input_tokens"),
                             ("usage_stats", "total_output_tokens")):
            assert live[section][key] > sidecar[section][key], (w["meta"], key)
        # Containment, not just size: the sidecar recorded itself as an
        # INCOMPLETE snapshot of the leg the live meta completes, and the live
        # meta was rebuilt by batch-recover from the leg's jobs.
        gap = sidecar["results_summary"]["completeness_gap"]
        assert gap["expected"] == live["execution_stats"]["items_processed"], w["meta"]
        assert gap["actual"] == sidecar["execution_stats"]["items_processed"], w["meta"]
        assert live["results_summary"]["batch_recover"]["recovered_rows"] >= gap["missing_count"]
        results = (REPO / w["meta"]).with_name("batch_results.jsonl")
        with results.open(encoding="utf-8") as fh:
            assert sum(1 for _ in fh) == live["execution_stats"]["items_processed"]


# ---------------------------------------------------------------------------
# Round 8 (2026-10-03): the fix commit pinned, C3's counterpart, negatives.
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_the_fix_commit_is_the_runner_fix():
    # The constant names exactly the commit that fixed the cached path; a
    # constant anywhere in the 1,235 commits before it would exempt runs from
    # main (round-8 audit).
    import subprocess

    from scripts.lib_pass_cost import CACHED_PATH_FIX_COMMIT
    head = subprocess.run(["git", "rev-parse", FIX_COMMIT], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout.strip()
    assert CACHED_PATH_FIX_COMMIT == head
    subject = subprocess.run(["git", "log", "-1", "--format=%s", CACHED_PATH_FIX_COMMIT],
                             cwd=REPO, capture_output=True, text=True, check=True).stdout
    assert subject.startswith("fix(runner): cache and service tier are independent levers")


@pytest.mark.tier1
@pytest.mark.parametrize("commit", [["a", "list"], {"a": 1}, 7])
def test_an_unhashable_or_odd_commit_keeps_the_rule(commit):
    from scripts.lib_pass_cost import has_cached_path_fix
    assert has_cached_path_fix(commit) is False


@pytest.mark.tier1
def test_the_tracker_records_the_commit_it_launched_with(monkeypatch):
    # A pull during a long run must not change the recorded commit: the code
    # that ran is the code loaded at launch.
    from scripts.lib_llm_metadata import LLMMetadataTracker
    monkeypatch.setattr(LLMMetadataTracker, "get_git_revision", staticmethod(lambda: "launch"))
    tracker = LLMMetadataTracker({"model": "gemini-3-flash-preview"}, "x")
    monkeypatch.setattr(LLMMetadataTracker, "get_git_revision", staticmethod(lambda: "later"))
    assert tracker.finalise()["environment"]["git_commit"] == "launch"


@pytest.mark.tier1
def test_a_post_fix_run_with_a_partial_header_is_not_on_the_cached_path(evidence, tmp_path):
    # The commit lifts the rule whatever the header says: a partial header
    # agreeing with the launch line leaves the pass audited at flex.
    pdir = tmp_path / "r" / "p" / "run_1"
    logs = {_rel(pdir): {**LOG_ENTRY, "tiers": ["flex"], "explicit_cache": True}}
    meta = _meta(pdir / "a.meta.json", usage=_counted({"flex": 1, "unreported": 2}, 3),
                 environment={"git_commit": AFTER_FIX})
    out = _cost(evidence(logs=logs), [meta], tmp_path / "r")
    frag = out["cost_source"]["fragments"][0]
    assert (frag["tier"], frag["tier_method"]) == ("flex", "run-log")
    assert out["cost_basis"] == "audited"
    assert not any(e.startswith("cached-path") for e in frag["evidence"])


@pytest.mark.tier1
def test_a_partial_header_the_evidence_allows_is_no_conflict(evidence, tmp_path):
    # Negative: the invoice billed flex AND standard that day; two responses
    # said standard. Nothing contradicts the API, so nothing is reported.
    day = {"2026-05-20": {"project_filter": "unverified", "models": {
        "gemini-3-flash-preview": {"tiers": {"flex": {"output": 9_000_000},
                                             "standard": {"output": 9_000_000}}}}}}
    meta = _meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json",
                 usage=_counted({"standard": 2, "unreported": 1}, 3))
    frag = _cost(evidence(billing={"days": day}), [meta],
                 tmp_path / "r")["cost_source"]["fragments"][0]
    assert "conflicts" not in frag


@pytest.mark.tier1
def test_a_partial_header_against_a_batch_marker_is_a_conflict(evidence, tmp_path):
    meta = _meta(tmp_path / "r" / "p" / "run_1" / "a.meta.json",
                 usage=_counted({"flex": 2, "unreported": 1}, 3), batch_api={"job": "x"})
    frag = _cost(evidence(), [meta], tmp_path / "r")["cost_source"]["fragments"][0]
    assert any(c.startswith("applied-header-partial served flex but batch-marker")
               for c in frag["conflicts"])


@pytest.mark.tier1
def test_c3_certifies_a_foreign_served_tier_as_unpriceable(evidence, tmp_path, monkeypatch):
    # The coster nulls a fragment served at a tier the card does not price;
    # C3 must re-derive the same reason independently, or the row would read
    # as a priceable pass wrongly nulled.
    import scripts.rederive_manifest_fields as c3
    monkeypatch.setattr(c3, "REPO_ROOT", tmp_path)
    pdir = tmp_path / "outputs" / "r" / "p" / "run_1"
    meta, path = _meta(pdir / "a.meta.json", usage=_counted({"priority": 2}, 2))
    out = _cost(evidence(), [(meta, path)], tmp_path / "outputs" / "r")
    assert out["cost_basis"] == "unpriceable"
    row = {"pass_id": "r::p::run1", "run_id": "r", "proposer_pool": "p", "pass_n": 1,
           "model_used": "gemini-3-flash-preview", "status": "ok", "n_tiles_processed": 1,
           "tokens": None, "cost_usd": out["cost_usd"], "cost_basis": out["cost_basis"],
           "cost_source": out["cost_source"],
           "timestamps": {"start": meta["timestamp"]["start"], "end": meta["timestamp"]["end"]},
           "provenance": {"source_files": ["outputs/r/p/run_1/a.meta.json"]}}
    verdicts = {f["field"]: f for f in c3.rederive_pass(row)["fields"]}
    assert verdicts["cost_usd"]["verdict"] == "MATCH"
    assert "priority" in verdicts["cost_usd"]["note"]
