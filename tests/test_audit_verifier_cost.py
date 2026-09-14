"""
Tier-1 gate tests for ``scripts/audit_verifier_cost.py``.

The auditor's whole purpose is that a verifier arm's cost is the SUM over its
main pass and every cleanup pass, so these tests gate it against costs that
are already committed elsewhere in the repository rather than against figures
it computes for itself:

- **The Gold Standard (GS) calibration leg**, whose two arms are recorded as
  US$0.4417 and US$0.6804 in ``planning/gemini37-image-55map-2026-09-13.md``
  line 112 and ``reports/gemini37-image-55map-deltas-2026-09-13.md`` line 43.
  Both arm metas are committed under ``outputs/gemini37-image-gs-2026-09-01/``.
- **The flex correction**: each arm's own ``cost_estimate`` prints exactly
  twice the audited figure, because ``run_pv.py verify`` bills at flex while
  the meta prices at list
  (``outputs/gemini37-image-55map-2026-09-13/post_run_report.md`` section 3.1).
- **The S144 3.8 swap arm**, a real legacy two-file stage: its
  ``run.meta.json`` holds a one-candidate cleanup and
  ``run.meta.main-2026-09-04.json`` the 790-candidate main pass, so reading
  the meta alone understates the arm by more than two orders of magnitude.
- **The campaign's K = 1 arm 2**, US$7.6875 + US$0.0153 = US$7.7028, which is
  the case the fix was written for. That stage ran on sapphire and its
  ``outputs/`` tree is not in this checkout, so the test skips with the path
  it wanted rather than asserting on absent data; it becomes live the moment
  the steward syncs the campaign.

No API calls are made and no file is written outside ``tmp_path``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.audit_proposer_cost import (  # noqa: E402
    LONG_PROMPT_RATE_CARDS,
    RATE_CARDS,
    rates,
)
from scripts.audit_verifier_cost import (  # noqa: E402
    RECOVERY_REGISTER_SCHEMA,
    audit_files,
    audit_stage,
    count_results,
    load_recovery_register,
    sweep,
)
from scripts.lib_llm_metadata import merge_cleanup_meta  # noqa: E402

pytestmark = pytest.mark.tier1

#: The committed GS calibration arms, and the costs the project records.
GS_LEG = (
    PROJECT_ROOT
    / "outputs/gemini37-image-gs-2026-09-01/verifier/g384_ov192_g37img"
)
GS_ARM_COSTS: dict[str, float] = {
    "verify_k3_arm1": 0.4417,
    "verify_k3_arm2": 0.6804,
}

#: The S144 Gemini 3.8 swap arm — a legacy two-file stage.
SWAP38 = (
    PROJECT_ROOT
    / "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap38"
)

#: The campaign arm the fix was written for, if its tree has been synced.
CAMPAIGN_K1_ARM2 = (
    PROJECT_ROOT
    / "outputs/gemini37-image-55map-2026-09-13/verifier"
    / "g384_ov192_55map_g37img/verify_k1_arm2"
)


def _read(path: Path) -> dict[str, Any]:
    """Read a JSON object from *path*."""
    with open(path) as handle:
        return json.load(handle)


def _write_stage(
    directory: Path,
    meta: dict[str, Any],
    *,
    results: int,
    extra_files: dict[str, dict[str, Any]] | None = None,
) -> Path:
    """Write a synthetic verifier stage with *results* result keys."""
    directory.mkdir(parents=True, exist_ok=True)
    with open(directory / "run.meta.json", "w") as handle:
        json.dump(meta, handle, indent=2)
    with open(directory / "probabilities.json", "w") as handle:
        json.dump(
            {
                "mode": "realtime",
                "results": {
                    f"candidate_{i:05d}": {"mound_probability": 0.5}
                    for i in range(results)
                },
            },
            handle,
        )
    for name, payload in (extra_files or {}).items():
        with open(directory / name, "w") as handle:
            json.dump(payload, handle, indent=2)
    return directory


# ─────────────────────────────────────────────────────────────────────
# 1. The GS calibration gate — committed costs, reproduced exactly
# ─────────────────────────────────────────────────────────────────────


class TestGoldStandardGate:
    """The auditor must reproduce the committed arm costs to four places."""

    @pytest.mark.parametrize(("arm", "expected"), sorted(GS_ARM_COSTS.items()))
    def test_arm_audited_cost_is_exact(self, arm: str, expected: float) -> None:
        """Each arm reproduces the cost the project recorded for it."""
        audit = audit_stage(GS_LEG / arm)
        assert round(audit.audited_usd, 4) == expected
        assert audit.results == 622
        assert audit.items_covered == 622
        assert audit.complete is True
        assert audit.shortfall == 0

    def test_leg_total_matches_the_recorded_figure(self) -> None:
        """The leg is US$1.1221 — the audited actual in the campaign card."""
        total = sum(
            audit_stage(GS_LEG / arm).audited_usd for arm in GS_ARM_COSTS
        )
        assert round(total, 4) == 1.1221

    def test_each_arm_meta_prints_twice_the_audited_figure(self) -> None:
        """The flex correction: the meta prices at list, the run billed flex."""
        for arm in GS_ARM_COSTS:
            audit = audit_stage(GS_LEG / arm)
            assert audit.meta_only_usd is not None
            assert audit.meta_only_usd == pytest.approx(
                2 * audit.audited_usd, rel=1e-4,
            )

    def test_standard_tier_doubles_the_flex_figure(self) -> None:
        """``--tier standard`` prices at list, so it is twice flex."""
        flex = audit_stage(GS_LEG / "verify_k3_arm1").audited_usd
        standard = audit_stage(
            GS_LEG / "verify_k3_arm1", tier="standard",
        ).audited_usd
        assert standard == pytest.approx(2 * flex, rel=1e-9)

    def test_per_candidate_rates_match_the_campaign_projection(self) -> None:
        """0.000710 and 0.001094 per candidate, as section 3.1 records."""
        rates = {
            arm: audit_stage(GS_LEG / arm).audited_usd_per_candidate
            for arm in GS_ARM_COSTS
        }
        assert round(rates["verify_k3_arm1"], 6) == 0.000710
        assert round(rates["verify_k3_arm2"], 6) == 0.001094


# ─────────────────────────────────────────────────────────────────────
# 2. Two files, one arm
# ─────────────────────────────────────────────────────────────────────


class TestTwoFileStages:
    """A stage split across two files is audited from both of them."""

    def test_legacy_backup_is_summed_with_the_primary(self) -> None:
        """The S144 3.8 swap arm: 1-candidate cleanup + 790-candidate main."""
        audit = audit_stage(SWAP38)
        assert audit.format == "legacy-summed"
        assert audit.results == 791
        assert audit.items_covered == 791
        assert audit.complete is True
        sources = {p.source: p for p in audit.passes}
        assert sources["run.meta.json"].items == 1
        assert sources["run.meta.main-2026-09-04.json"].items == 790
        # Reading the meta alone understates the arm by two orders of
        # magnitude — the trap this auditor exists to close.
        assert audit.meta_only_usd is not None
        assert audit.audited_usd > 100 * audit.meta_only_usd

    def test_fixed_format_reports_the_main_and_cleanup_split(
        self, tmp_path: Path,
    ) -> None:
        """A merged meta is priced once, and its blocks give the split.

        Built from the two REAL GS arm metas so the arithmetic is gated on
        recorded token loads: arm 1 stands in for the main pass and arm 2 for
        a cleanup, whose sum is the leg's US$1.1221.
        """
        main = _read(GS_LEG / "verify_k3_arm1" / "run.meta.json")
        cleanup = _read(GS_LEG / "verify_k3_arm2" / "run.meta.json")
        merged = merge_cleanup_meta(main, cleanup)
        stage = _write_stage(tmp_path / "verify_merged", merged, results=1244)

        audit = audit_stage(stage)
        assert audit.format == "fixed"
        assert round(audit.audited_usd, 4) == 1.1221
        assert audit.items_covered == 1244
        assert audit.complete is True
        by_kind = {p.kind: p for p in audit.passes}
        assert round(by_kind["main"].audited_usd, 4) == 0.4417
        assert round(by_kind["cleanup"].audited_usd, 4) == 0.6804
        # The merged total is priced once, not once per block.
        assert len([p for p in audit.passes if p.kind == "merged-total"]) == 1

    def test_merge_sidecars_are_not_double_counted(
        self, tmp_path: Path,
    ) -> None:
        """An earlier merged state beside the primary must not be added in."""
        main = _read(GS_LEG / "verify_k3_arm1" / "run.meta.json")
        cleanup = _read(GS_LEG / "verify_k3_arm2" / "run.meta.json")
        merged = merge_cleanup_meta(main, cleanup)
        stage = _write_stage(
            tmp_path / "verify_merged",
            merged,
            results=1244,
            extra_files={"run.meta.pre-cleanup-1.json": main},
        )
        assert round(audit_stage(stage).audited_usd, 4) == 1.1221

    def test_campaign_k1_arm2_sums_main_and_cleanup(self) -> None:
        """US$7.6875 + US$0.0153 = US$7.7028, read from both files.

        The case that prompted the fix. Skipped while the campaign's
        ``outputs/`` tree is only on sapphire.
        """
        if not (CAMPAIGN_K1_ARM2 / "run.meta.json").exists():
            pytest.skip(
                "campaign arm not synced to this checkout: "
                f"{CAMPAIGN_K1_ARM2}",
            )
        audit = audit_stage(CAMPAIGN_K1_ARM2)
        assert round(audit.audited_usd, 4) == 7.7028
        by_items = sorted(audit.passes, key=lambda p: -p.items)
        assert round(by_items[0].audited_usd, 4) == 7.6875
        assert round(by_items[-1].audited_usd, 4) == 0.0153
        assert audit.items_covered == 6985
        assert audit.complete is True


# ─────────────────────────────────────────────────────────────────────
# 3. The unrecoverable shape
# ─────────────────────────────────────────────────────────────────────


class TestShortfall:
    """A stage whose passes do not cover its results is a lower bound."""

    def test_shortfall_is_reported_and_flagged(self, tmp_path: Path) -> None:
        """The fourth cell's shape: one small meta against a large result set."""
        meta = {
            "configuration": {"model": "gemini-3.7-flash"},
            "execution_stats": {"items_processed": 29},
            "usage_stats": {
                "total_input_tokens": 60_000,
                "total_output_tokens": 2_000,
                "total_thoughts_tokens": 500,
                "total_cached_tokens": 0,
            },
            "cost_estimate": {"total_cost_usd": 0.0375},
        }
        stage = _write_stage(tmp_path / "verify_37", meta, results=5_000)
        audit = audit_stage(stage)
        assert audit.format == "single-meta"
        assert audit.items_covered == 29
        assert audit.shortfall == 4_971
        assert audit.complete is False
        assert any("LOWER BOUND" in note for note in audit.notes)

    def test_count_results_returns_none_without_a_results_file(
        self, tmp_path: Path,
    ) -> None:
        """A stage with no results file reports no candidate population."""
        stage = tmp_path / "verify_bare"
        stage.mkdir()
        assert count_results(stage) is None

    def test_absent_meta_raises(self, tmp_path: Path) -> None:
        """A stage with no meta cannot be audited at all."""
        stage = tmp_path / "verify_empty"
        stage.mkdir()
        with pytest.raises(FileNotFoundError):
            audit_stage(stage)


# ─────────────────────────────────────────────────────────────────────
# 4. The retrospective sweep
# ─────────────────────────────────────────────────────────────────────


class TestSweep:
    """The sweep finds the signature and classifies recoverability."""

    def _tree(self, tmp_path: Path) -> Path:
        """Build a tree with one recoverable, one unrecoverable, one clean."""
        root = tmp_path / "outputs"
        usage = {
            "total_input_tokens": 100_000,
            "total_output_tokens": 4_000,
            "total_thoughts_tokens": 1_000,
            "total_cached_tokens": 0,
        }
        small = {
            "configuration": {"model": "gemini-3.7-flash"},
            "execution_stats": {"items_processed": 5},
            "usage_stats": usage,
            "cost_estimate": {"total_cost_usd": 0.01},
        }
        big = {
            "configuration": {"model": "gemini-3.7-flash"},
            "execution_stats": {"items_processed": 995},
            "usage_stats": usage,
            "cost_estimate": {"total_cost_usd": 1.0},
        }
        _write_stage(
            root / "recoverable",
            small,
            results=1_000,
            extra_files={
                "run.meta.json.pre-cleanup-20260913T225915.backup": big,
            },
        )
        _write_stage(root / "unrecoverable", small, results=1_000)
        _write_stage(root / "clean", big | {
            "execution_stats": {"items_processed": 1_000},
        }, results=1_000)
        _write_stage(
            root / "batch_stage",
            big | {"execution_stats": {"items_processed": 0}},
            results=1_000,
        )
        return root

    def test_classification(self, tmp_path: Path) -> None:
        """Recoverable when a prior meta survives; unrecoverable otherwise."""
        found = {
            Path(s.stage).name: s for s in sweep(self._tree(tmp_path))
        }
        assert set(found) == {"recoverable", "unrecoverable"}
        assert found["recoverable"].classification == "RECOVERABLE"
        assert found["recoverable"].prior_meta_files == [
            "run.meta.json.pre-cleanup-20260913T225915.backup",
        ]
        assert found["unrecoverable"].classification == "UNRECOVERABLE"
        assert found["unrecoverable"].shortfall == 995

    def test_complete_and_batch_stages_are_not_reported(
        self, tmp_path: Path,
    ) -> None:
        """A complete stage, and a batch stage recording zero, are excluded.

        The Batch API returns no per-response metadata, so a batch stage
        legitimately records ``items_processed: 0`` and had nothing in the
        meta to lose.
        """
        names = {Path(s.stage).name for s in sweep(self._tree(tmp_path))}
        assert "clean" not in names
        assert "batch_stage" not in names

    def test_min_shortfall_filters(self, tmp_path: Path) -> None:
        """A large threshold suppresses the small gaps."""
        assert sweep(self._tree(tmp_path), min_shortfall=10_000) == []

    def test_merged_stage_is_classified_merged(self, tmp_path: Path) -> None:
        """A stage already carrying the fixed format needs no recovery."""
        main = _read(GS_LEG / "verify_k3_arm1" / "run.meta.json")
        cleanup = _read(GS_LEG / "verify_k3_arm2" / "run.meta.json")
        root = tmp_path / "outputs"
        _write_stage(
            root / "merged",
            merge_cleanup_meta(main, cleanup),
            results=2_000,
        )
        found = sweep(root)
        assert [s.classification for s in found] == ["MERGED"]

    def test_unknown_rate_card_keeps_the_stage_in_the_sweep(
        self, tmp_path: Path,
    ) -> None:
        """A stage the auditor cannot price is reported, never dropped."""
        root = tmp_path / "outputs"
        _write_stage(
            root / "unpriceable",
            {
                "configuration": {"model": "gemini-9-flash"},
                "execution_stats": {"items_processed": 5},
                "usage_stats": {"total_input_tokens": 10},
            },
            results=1_000,
        )
        found = sweep(root)
        assert len(found) == 1
        assert found[0].audited_usd is None
        assert "gemini-9-flash" in (found[0].audit_error or "")
        assert found[0].classification == "UNRECOVERABLE"

    def test_main_pass_coverage_is_read_from_cleanup_history(
        self, tmp_path: Path,
    ) -> None:
        """``cleanup_history`` recovers the count the main pass covered."""
        root = tmp_path / "outputs"
        stage = _write_stage(
            root / "with_history",
            {
                "configuration": {"model": "gemini-3.7-flash"},
                "execution_stats": {"items_processed": 6},
                "usage_stats": {"total_input_tokens": 10_000},
            },
            results=1_000,
        )
        probs = _read(stage / "probabilities.json")
        probs["cleanup_history"] = [
            {"initial_missing": 6, "recovered": 6, "still_missing": 0},
        ]
        with open(stage / "probabilities.json", "w") as handle:
            json.dump(probs, handle)
        found = sweep(root)
        assert found[0].cleanup_history == 1
        assert found[0].main_pass_covered == 994


# ─────────────────────────────────────────────────────────────────────
# 6. The recovery register — the third source of passes
# ─────────────────────────────────────────────────────────────────────


def _register(stage: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Wrap one stage entry in a register of the current schema."""
    return {"schema": RECOVERY_REGISTER_SCHEMA, "stages": {stage: entry}}


def _recovered_pass(
    *,
    run_id: str = "main-pass-run-id",
    items: int = 900,
    input_tokens: int = 1_800_000,
    output_tokens: int = 90_000,
) -> dict[str, Any]:
    """One ``recovered_passes`` entry as the register records it."""
    return {
        "source": "git-blob:0123456789abcdef",
        "kind": "main",
        "commit": "abcdef1234567890",
        "commit_date": "2026-04-17T00:00:00+00:00",
        "run_id": run_id,
        "configuration": {"model": "gemini-3-flash-preview"},
        "execution_stats": {"items_processed": items},
        "usage_stats": {
            "total_input_tokens": input_tokens,
            "total_cached_tokens": 0,
            "total_output_tokens": output_tokens,
            "total_thoughts_tokens": 0,
        },
    }


class TestRecoveryRegister:
    """A register pass is counted, traced to its blob, and never doubled."""

    def test_register_pass_closes_the_shortfall_and_is_counted(
        self, tmp_path: Path,
    ) -> None:
        """The recovered main pass is summed with the surviving cleanup."""
        stage = _write_stage(
            tmp_path / "verified",
            {
                "run_id": "cleanup-run-id",
                "configuration": {"model": "gemini-3-flash-preview"},
                "execution_stats": {"items_processed": 100},
                "usage_stats": {
                    "total_input_tokens": 200_000,
                    "total_output_tokens": 10_000,
                },
            },
            results=1_000,
        )
        register = _register(str(stage), {
            "verdict": "RECOVERED-FROM-GIT",
            "recovered_passes": [_recovered_pass()],
        })
        audit = audit_stage(stage, register=register["stages"])
        assert audit.format == "register-recovered"
        assert audit.items_covered == 1_000
        assert audit.shortfall == 0
        assert audit.complete is True
        # flex: input 0.25/1M, output 1.50/1M over both passes.
        expected = (
            (200_000 + 1_800_000) * 0.25 / 1e6
            + (10_000 + 90_000) * 1.50 / 1e6
        )
        assert audit.audited_usd == pytest.approx(expected)
        sources = [entry.source for entry in audit.passes]
        assert "register:git-blob:0123456789abcdef" in sources
        assert any(
            "recovered from git history" in note for note in audit.notes
        )

    def test_a_pass_already_counted_on_disc_is_not_doubled(
        self, tmp_path: Path,
    ) -> None:
        """A register pass whose ``run_id`` is on disc is skipped."""
        stage = _write_stage(
            tmp_path / "verified",
            {
                "run_id": "main-pass-run-id",
                "configuration": {"model": "gemini-3-flash-preview"},
                "execution_stats": {"items_processed": 900},
                "usage_stats": {
                    "total_input_tokens": 1_800_000,
                    "total_output_tokens": 90_000,
                },
            },
            results=1_000,
        )
        register = _register(str(stage), {
            "verdict": "RECOVERED-FROM-GIT",
            "recovered_passes": [_recovered_pass()],
        })
        audit = audit_stage(stage, register=register["stages"])
        assert audit.items_covered == 900
        assert audit.format == "single-meta"
        assert any("already counted" in note for note in audit.notes)

    def test_residual_estimate_is_noted_but_never_counted(
        self, tmp_path: Path,
    ) -> None:
        """An estimate must not reach the audited total."""
        stage = _write_stage(
            tmp_path / "verified",
            {
                "configuration": {"model": "gemini-3-flash-preview"},
                "execution_stats": {"items_processed": 100},
                "usage_stats": {
                    "total_input_tokens": 200_000,
                    "total_output_tokens": 10_000,
                },
            },
            results=1_000,
        )
        register = _register(str(stage), {
            "verdict": "NOT-IN-HISTORY",
            "recovered_passes": [],
            "residual_estimate": {
                "is_estimate": True,
                "missing_candidates": 900,
                "usage_stats": {"total_input_tokens": 1_800_000},
            },
        })
        audit = audit_stage(stage, register=register["stages"])
        expected = 200_000 * 0.25 / 1e6 + 10_000 * 1.50 / 1e6
        assert audit.audited_usd == pytest.approx(expected)
        assert audit.shortfall == 900
        assert audit.complete is False
        assert any("ESTIMATE" in note for note in audit.notes)

    def test_a_register_of_an_unknown_schema_is_ignored(
        self, tmp_path: Path,
    ) -> None:
        """A future contract must not be mis-read as the current one."""
        path = tmp_path / "register.json"
        path.write_text(json.dumps({
            "schema": "verifier-meta-recovery/99",
            "stages": {"outputs/whatever": {"recovered_passes": []}},
        }))
        assert load_recovery_register(path) == {}

    def test_an_absent_register_is_not_an_error(self, tmp_path: Path) -> None:
        """The auditor works with no register on the machine."""
        assert load_recovery_register(tmp_path / "nope.json") == {}
        assert load_recovery_register(None) == {}

    def test_sweep_classifies_a_registered_stage_as_recovered(
        self, tmp_path: Path,
    ) -> None:
        """The census must show git recovery as its own class."""
        root = tmp_path / "outputs"
        stage = _write_stage(
            root / "verified",
            {
                "run_id": "cleanup-run-id",
                "configuration": {"model": "gemini-3-flash-preview"},
                "execution_stats": {"items_processed": 100},
                "usage_stats": {
                    "total_input_tokens": 200_000,
                    "total_output_tokens": 10_000,
                },
            },
            results=1_000,
        )
        register = _register(str(stage), {
            "verdict": "RECOVERED-FROM-GIT",
            "recovered_passes": [_recovered_pass()],
        })
        found = sweep(root, register=register["stages"])
        assert len(found) == 1
        assert found[0].classification == "RECOVERED-FROM-GIT"
        assert found[0].audited_usd is not None

    def test_the_committed_register_is_readable_and_self_consistent(
        self,
    ) -> None:
        """The register this session wrote must parse under its own schema."""
        path = PROJECT_ROOT / "outputs/verifier-meta-recovery-2026-09-14.json"
        if not path.exists():
            pytest.skip(f"register not in this checkout: {path}")
        stages = load_recovery_register(path)
        assert stages, "the register records no stages"
        for stage, entry in stages.items():
            assert entry["verdict"] in {
                "RECOVERED-FROM-GIT", "PARTIALLY-RECOVERED", "NOT-IN-HISTORY",
            }, stage
            for recovered in entry.get("recovered_passes") or []:
                # Every counted pass must be traceable to a blob and carry the
                # usage the audit will price.
                assert recovered["source"].startswith("git-blob:"), stage
                assert recovered["usage_stats"]["total_input_tokens"] > 0
                assert recovered["execution_stats"]["items_processed"] > 0
            if entry["verdict"] == "NOT-IN-HISTORY":
                assert not entry.get("recovered_passes")


# ─────────────────────────────────────────────────────────────────────
# 7. Explicit file pairs
# ─────────────────────────────────────────────────────────────────────


class TestExplicitFiles:
    """``--pass-file`` prices files that are not a stage on disc."""

    def test_the_swap38_pair_sums_to_the_committed_figure(self) -> None:
        """The S144 arm's two files, named explicitly, give US$0.8469."""
        main = SWAP38 / "run.meta.main-2026-09-04.json"
        cleanup = SWAP38 / "run.meta.json"
        if not main.exists():
            pytest.skip(f"stage not in this checkout: {SWAP38}")
        audit = audit_files([main, cleanup])
        assert audit.audited_usd == pytest.approx(0.8469, abs=5e-5)
        assert audit.items_covered == 791
        assert audit.format == "explicit-files"

    def test_a_missing_file_is_an_error_not_a_zero(
        self, tmp_path: Path,
    ) -> None:
        """Pricing a file that is not there must fail loudly."""
        with pytest.raises(FileNotFoundError):
            audit_files([tmp_path / "absent.json"])


# ─────────────────────────────────────────────────────────────────────
# 8. The Gemini 3.1 Pro rate card
# ─────────────────────────────────────────────────────────────────────


class TestProRateCard:
    """The Pro card pins the rates read from Google's pricing page."""

    def test_standard_tier_rates_are_the_published_ones(self) -> None:
        """US$2.00 input, US$12.00 output, US$0.20 cache read, per 1M."""
        card = RATE_CARDS["gemini-3.1-pro-preview"]
        assert card == {"input": 2.00, "output": 12.00, "cache": 0.20}
        rate = rates("gemini-3.1-pro-preview", "standard")
        assert rate["input"] == pytest.approx(2.00 / 1e6)
        assert rate["output"] == pytest.approx(12.00 / 1e6)
        assert rate["cache"] == pytest.approx(0.20 / 1e6)

    def test_flex_halves_input_and_output_but_not_the_cache_read(self) -> None:
        """Batch and flex are half of standard; caching is not discounted."""
        rate = rates("gemini-3.1-pro-preview", "flex")
        assert rate["input"] == pytest.approx(1.00 / 1e6)
        assert rate["output"] == pytest.approx(6.00 / 1e6)
        assert rate["cache"] == pytest.approx(0.20 / 1e6)

    def test_the_long_prompt_tier_is_recorded(self) -> None:
        """Prompts over 200K tokens bill at 4.00 / 18.00 / 0.40."""
        assert LONG_PROMPT_RATE_CARDS["gemini-3.1-pro-preview"] == {
            "input": 4.00, "output": 18.00, "cache": 0.40,
        }

    @pytest.mark.parametrize(
        ("stage_name", "expected_usd"),
        [
            ("text-baseline-pro-verifier", 0.106662),
            ("pro-high-image-1of5-pro-verifier", 0.038726),
            ("pro-medium-image-baseline-pro-verifier", 0.051040),
        ],
    )
    def test_the_three_pro_stages_now_price(
        self, stage_name: str, expected_usd: float,
    ) -> None:
        """Each Pro verifier stage's surviving pass prices at flex rates."""
        stage = PROJECT_ROOT / "outputs/h11/pv-diag-384/verified" / stage_name
        if not stage.exists():
            pytest.skip(f"stage not in this checkout: {stage}")
        audit = audit_stage(stage)
        assert audit.audited_usd == pytest.approx(expected_usd, abs=5e-6)
        # Thinking tokens are billed as output, which the meta's own
        # cost_estimate omitted — so the audit exceeds it despite flex.
        assert audit.meta_only_usd is not None
