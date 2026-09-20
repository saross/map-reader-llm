"""
Tests for ``scripts/audit_proposer_cost.py``.

The script exists because a run's own ``cost_estimate`` cannot be used at a
budget gate, so these tests pin the three things that made that figure wrong:
the Gemini 3.7 rate card, the cache read's exemption from the tier discount,
and the inclusion of thinking tokens at the output rate.

The headline guard is :func:`test_reproduces_committed_gs_figure`, which
reproduces the committed Gold Standard (GS) leg total of US$22.50 from its
recorded token aggregates — the figure in
``reports/gemini37-image-55map-costing-2026-09-10.md`` and
``results/gemini37-image-gs-2026-09-01/findings.md``. It uses the aggregates as
literals rather than reading the run directory, so it stays tier-1 hermetic.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.tier1

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_module():
    """Import the script by path, since ``scripts/`` is not a package."""
    path = BASE_DIR / "scripts" / "audit_proposer_cost.py"
    spec = importlib.util.spec_from_file_location("audit_proposer_cost", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_proposer_cost"] = module
    spec.loader.exec_module(module)
    return module


apc = _load_module()


#: Token aggregates summed over the ten committed fragments of
#: ``outputs/gemini37-image-gs-2026-09-01/g384_ov192_g37img`` (five passes plus
#: their recovery fragments), read 2026-09-13.
GS_USAGE = {
    "total_input_tokens": 139_925_820,
    "total_cached_tokens": 111_214_884,
    "total_output_tokens": 557_418,
    "total_thoughts_tokens": 1_252_014,
}
GS_TILE_PASSES = 6_990


class TestRateCard:
    """The rate card and the tier discount."""

    def test_gemini_37_lists_higher_than_gemini_3(self):
        """3.7 lists at 0.75 / 3.75, not the 0.50 / 3.00 the metas stamp."""
        assert apc.RATE_CARDS["gemini-3.7-flash"]["input"] == 0.75
        assert apc.RATE_CARDS["gemini-3.7-flash"]["output"] == 3.75
        assert apc.RATE_CARDS["gemini-3-flash"]["input"] == 0.50
        assert apc.RATE_CARDS["gemini-3-flash"]["output"] == 3.00

    def test_flex_halves_input_and_output(self):
        """Flex bills at half of list on the input and output axes."""
        rate = apc.rates("gemini-3.7-flash", "flex")
        assert rate["input"] == pytest.approx(0.375 / 1e6)
        assert rate["output"] == pytest.approx(1.875 / 1e6)

    def test_cache_read_is_not_tier_discounted(self):
        """Context caching costs the same at every tier (token-load audit s2).

        Discounting it understates a cache-heavy image leg by about 19 per
        cent, which is how a first implementation of this script returned
        US$18.33 where the committed figure is US$22.50.
        """
        flex = apc.rates("gemini-3.7-flash", "flex")
        standard = apc.rates("gemini-3.7-flash", "standard")
        assert flex["cache"] == standard["cache"]
        assert flex["cache"] == pytest.approx(0.075 / 1e6)

    def test_unknown_model_raises_rather_than_guessing(self):
        """Guessing a rate card is the error this script exists to correct."""
        with pytest.raises(apc.RateCardError):
            apc.rates("gemini-9-flash", "flex")


class TestAuditedCost:
    """The costing rule itself."""

    def test_reproduces_committed_gs_figure(self):
        """The GS leg totals US$22.50, or US$0.00322 per tile-pass."""
        rate = apc.rates("gemini-3.7-flash", "flex")
        total = apc.audited_cost(GS_USAGE, rate)
        assert total == pytest.approx(22.50, abs=0.01)
        assert total / GS_TILE_PASSES == pytest.approx(0.00322, abs=1e-5)

    def test_thinking_tokens_are_billed_at_the_output_rate(self):
        """Omitting thinking is one of the meta's three errors."""
        rate = apc.rates("gemini-3.7-flash", "flex")
        without = dict(GS_USAGE, total_thoughts_tokens=0)
        delta = apc.audited_cost(GS_USAGE, rate) - apc.audited_cost(without, rate)
        assert delta == pytest.approx(
            GS_USAGE["total_thoughts_tokens"] * rate["output"]
        )

    def test_cached_input_is_cheaper_than_fresh_input(self):
        """Cache-blind pricing is the meta's dominant error at 79 % cached."""
        rate = apc.rates("gemini-3.7-flash", "flex")
        all_fresh = dict(GS_USAGE, total_cached_tokens=0)
        assert apc.audited_cost(GS_USAGE, rate) < apc.audited_cost(all_fresh, rate)

    def test_missing_thinking_key_is_tolerated(self):
        """Older metas predate ``total_thoughts_tokens``; treat it as zero."""
        rate = apc.rates("gemini-3-flash", "flex")
        usage = {
            "total_input_tokens": 1_000_000,
            "total_cached_tokens": 0,
            "total_output_tokens": 1_000_000,
        }
        expected = 1_000_000 * rate["input"] + 1_000_000 * rate["output"]
        assert apc.audited_cost(usage, rate) == pytest.approx(expected)


# ─────────────────────────────────────────────────────────────────────
# Which model a fragment is priced at (audit 2026-09-20)
# ─────────────────────────────────────────────────────────────────────

#: The token aggregates every synthetic fragment below carries. Small, round
#: and cache-free, so a per-model cost is checkable by hand.
_USAGE = {
    "total_input_tokens": 1_000_000,
    "total_cached_tokens": 0,
    "total_output_tokens": 100_000,
    "total_thoughts_tokens": 0,
}


def _write_fragment(root: Path, name: str, model: str | None,
                    items: int = 100) -> Path:
    """Write one ``run_*`` fragment with a meta recording *model*.

    ``model=None`` writes a meta with no ``configuration.model``, which is
    the shape the auditor must refuse to price rather than guess at.
    """
    frag = root / name
    frag.mkdir(parents=True, exist_ok=True)
    configuration: dict = {"version": "test"}
    if model is not None:
        configuration["model"] = model
    (frag / "detections-test.meta.json").write_text(json.dumps({
        "configuration": configuration,
        "execution_stats": {"items_processed": items},
        "usage_stats": dict(_USAGE),
        "cost_estimate": {"total_cost_usd": 9.99},
    }))
    return frag


class TestFragmentModel:
    """``configuration.model`` is the field the metas actually use."""

    def test_reads_the_field_the_metas_record(self):
        meta = {"configuration": {"model": "gemini-3-flash-preview"}}
        assert apc.fragment_model(meta) == "gemini-3-flash-preview"

    def test_a_meta_with_no_model_reports_none(self):
        assert apc.fragment_model({"configuration": {"version": "x"}}) is None
        assert apc.fragment_model({}) is None

    def test_the_pricing_used_block_is_not_consulted(self):
        """``cost_estimate.pricing_used`` is part of the figure being replaced.

        It records the Gemini 3 rates even on a 3.7 run — the first of the
        three compounding errors in the module docstring — so reading the
        model from it would reintroduce the defect by another route.
        """
        meta = {
            "configuration": {"model": "gemini-3.7-flash"},
            "cost_estimate": {"pricing_used": {"model": "gemini-3-flash"}},
        }
        assert apc.fragment_model(meta) == "gemini-3.7-flash"


class TestReadFragments:
    """Each fragment carries its own model out of the reader."""

    def test_each_fragment_reports_its_own_model(self, tmp_path):
        _write_fragment(tmp_path, "run_1", "gemini-3-flash-preview")
        _write_fragment(tmp_path, "run_2", "gemini-3.7-flash")
        frags = apc.read_fragments(str(tmp_path))
        assert [f["model"] for f in frags] == [
            "gemini-3-flash-preview", "gemini-3.7-flash",
        ]


class TestPricingPerFragment:
    """The defect itself: a pool priced at one default model."""

    def test_a_pool_is_priced_at_each_fragments_own_card(
        self, tmp_path, monkeypatch, capsys,
    ):
        """Two models in one pool, each at its own rate.

        This is the shape that made the Gemini 3 image pool read US$345.90
        against its own card's US$233.63 — 48 per cent high, at a budget
        gate.
        """
        _write_fragment(tmp_path, "run_1", "gemini-3-flash")
        _write_fragment(tmp_path, "run_2", "gemini-3.7-flash")
        monkeypatch.setattr(
            sys, "argv",
            ["audit_proposer_cost.py", "--json", str(tmp_path)],
        )

        assert apc.main() == 0

        out = json.loads(capsys.readouterr().out)
        expected = (
            apc.audited_cost(_USAGE, apc.rates("gemini-3-flash", "flex"))
            + apc.audited_cost(_USAGE, apc.rates("gemini-3.7-flash", "flex"))
        )
        assert out["audited_usd"] == pytest.approx(round(expected, 4))
        assert out["models"] == ["gemini-3-flash", "gemini-3.7-flash"]

    def test_pricing_the_pool_at_one_model_would_differ(self, tmp_path,
                                                        monkeypatch, capsys):
        """The guard against a fix that only looks right.

        If both fragments were priced at the 3.7 card — the old default —
        the total would be strictly higher, because 3.7 lists at 1.5x
        Gemini 3. Asserting the totals differ is what makes the previous
        test bite.
        """
        _write_fragment(tmp_path, "run_1", "gemini-3-flash")
        _write_fragment(tmp_path, "run_2", "gemini-3.7-flash")
        monkeypatch.setattr(
            sys, "argv",
            ["audit_proposer_cost.py", "--json", str(tmp_path)],
        )
        apc.main()
        out = json.loads(capsys.readouterr().out)

        all_at_37 = 2 * apc.audited_cost(
            _USAGE, apc.rates("gemini-3.7-flash", "flex"),
        )
        assert out["audited_usd"] < all_at_37


class TestModelProvenance:
    """No model, an override, and a disagreement."""

    def test_a_meta_with_no_model_is_refused(self, tmp_path, monkeypatch,
                                             capsys):
        """Guessing a rate card is the error this script exists to correct."""
        _write_fragment(tmp_path, "run_1", None)
        monkeypatch.setattr(
            sys, "argv", ["audit_proposer_cost.py", str(tmp_path)],
        )

        assert apc.main() == 2

        err = capsys.readouterr().err
        assert "records no configuration.model" in err
        assert "--model" in err

    def test_an_explicit_model_prices_a_meta_that_records_none(
        self, tmp_path, monkeypatch, capsys,
    ):
        """The escape hatch, and it must say it was used."""
        _write_fragment(tmp_path, "run_1", None)
        monkeypatch.setattr(sys, "argv", [
            "audit_proposer_cost.py", "--json",
            "--model", "gemini-3-flash", str(tmp_path),
        ])

        assert apc.main() == 0

        captured = capsys.readouterr()
        assert "note:" in captured.err
        assert "gemini-3-flash" in captured.err
        out = json.loads(captured.out)
        assert out["models"] == ["gemini-3-flash"]
        assert out["audited_usd"] == pytest.approx(round(apc.audited_cost(
            _USAGE, apc.rates("gemini-3-flash", "flex"),
        ), 4))

    def test_a_disagreeing_model_warns_and_does_not_win(
        self, tmp_path, monkeypatch, capsys,
    ):
        """The meta knows what it ran on; the flag does not."""
        _write_fragment(tmp_path, "run_1", "gemini-3-flash-preview")
        monkeypatch.setattr(sys, "argv", [
            "audit_proposer_cost.py", "--json",
            "--model", "gemini-3.7-flash", str(tmp_path),
        ])

        assert apc.main() == 0

        captured = capsys.readouterr()
        assert "warning:" in captured.err
        assert "gemini-3-flash-preview" in captured.err
        out = json.loads(captured.out)
        assert out["models"] == ["gemini-3-flash-preview"]
        assert out["audited_usd"] == pytest.approx(round(apc.audited_cost(
            _USAGE, apc.rates("gemini-3-flash-preview", "flex"),
        ), 4))

    def test_an_agreeing_model_does_not_warn(self, tmp_path, monkeypatch,
                                             capsys):
        """The note must be a signal, not noise on every ordinary run."""
        _write_fragment(tmp_path, "run_1", "gemini-3.7-flash")
        monkeypatch.setattr(sys, "argv", [
            "audit_proposer_cost.py", "--json",
            "--model", "gemini-3.7-flash", str(tmp_path),
        ])
        apc.main()
        assert capsys.readouterr().err == ""

    def test_an_unknown_override_is_rejected_before_any_reading(
        self, tmp_path, monkeypatch, capsys,
    ):
        _write_fragment(tmp_path, "run_1", "gemini-3-flash")
        monkeypatch.setattr(sys, "argv", [
            "audit_proposer_cost.py", "--model", "gemini-9-flash",
            str(tmp_path),
        ])

        assert apc.main() == 2
        assert "no rate card for 'gemini-9-flash'" in capsys.readouterr().err

    def test_a_meta_whose_recorded_model_has_no_card_is_refused(
        self, tmp_path, monkeypatch, capsys,
    ):
        """A recorded model is used, so an unknown one must stop the audit."""
        _write_fragment(tmp_path, "run_1", "gemini-9-flash")
        monkeypatch.setattr(
            sys, "argv", ["audit_proposer_cost.py", str(tmp_path)],
        )

        assert apc.main() == 2
        assert "no rate card for 'gemini-9-flash'" in capsys.readouterr().err
