#!/usr/bin/env python3
"""
Tier-1 tests for the K-ladder Phase 2 drivers
=============================================

Covers the pure, decision-bearing logic of the four Phase 2 scripts — the
parts where a silent mistake would corrupt an API-spend decision, a cost
figure, or an operating point:

* ``build_k_ladder_phase2_unions`` — the 28-rung worklist and its tier map,
  the first-N pass lists, and the count-mismatch STOP.
* ``run_k_ladder_phase2_verifier`` — the audited flex arithmetic (which must
  NOT trust the meta's own list-priced ``cost_estimate``), the separation of
  billed API requests from verified candidates, and the 3.7 family's stage
  path override.
* ``score_k_ladder_phase2_rungs`` — the F1@20 argmax and its documented
  tie-break, the cell-directory convention, and the condition labels.
* ``derive_k_ladder_committed_carried`` — that the two carried readings
  coincide at K = 1 and K = 3 and diverge above them, which is the premise
  the Phase 2 rungs rely on.

No network, no API, no large committed artefacts: every fixture is synthetic
except the committed ``first-n-union-sizes.json``, which is a few kilobytes
and is the file the worklist is derived from.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import build_k_ladder_phase2_tables as tables  # noqa: E402
from scripts import build_k_ladder_phase2_unions as unions  # noqa: E402
from scripts import derive_k_ladder_committed_carried as carried  # noqa: E402
from scripts import run_k_ladder_phase2_verifier as verifier  # noqa: E402
from scripts import score_k_ladder_phase2_rungs as score  # noqa: E402

pytestmark = pytest.mark.tier1


# --------------------------------------------------------------------------
# The 28-rung worklist
# --------------------------------------------------------------------------


def test_worklist_has_exactly_28_rungs() -> None:
    """The costing table's row count is derived, not transcribed."""
    rungs = unions.load_rungs()
    assert len(rungs) == 28
    assert [rung["row"] for rung in rungs] == list(range(1, 29))


def test_worklist_candidate_total_matches_the_approved_figure() -> None:
    """35,844 candidates is what the PI approved US$24.84 for."""
    rungs = unions.load_rungs()
    assert sum(rung["expected_candidates"] for rung in rungs) == 35_844


def test_tiers_partition_the_rungs_as_the_costing_says() -> None:
    """Tiers A-D partition the 28 rungs with the costing's candidate counts."""
    rungs = unions.load_rungs()
    by_tier: dict[str, int] = {}
    counts: dict[str, int] = {}
    for rung in rungs:
        by_tier[rung["tier"]] = by_tier.get(rung["tier"], 0) + 1
        counts[rung["tier"]] = (
            counts.get(rung["tier"], 0) + rung["expected_candidates"]
        )
    assert by_tier == {"A": 4, "B": 8, "C": 12, "D": 4}
    # reports/k-ladder-phase2-costing-2026-09-12.md § 5, candidates column.
    assert counts == {"A": 6_492, "B": 12_662, "C": 12_877, "D": 3_813}


def test_every_rung_uses_the_first_n_rule() -> None:
    """``--passes`` is always 1..N with no gaps and no selection."""
    for rung in unions.load_rungs():
        expected = ",".join(str(i) for i in range(1, rung["n_passes"] + 1))
        assert rung["pass_list"] == expected
        assert rung["pass_ids"] == [
            f"run_{i}" for i in range(1, rung["n_passes"] + 1)
        ]


def test_only_k1_and_k3_rungs_are_bought() -> None:
    """Phase 2 fills K = 1 and K = 3; K = 5 and K = 10 are committed."""
    assert {rung["n_passes"] for rung in unions.load_rungs()} == {1, 3}


def test_count_mismatch_beyond_tolerance_is_a_stop(tmp_path: Path) -> None:
    """A union more than 2 % from the costing's count must not be verified."""
    rung = {
        "row": 99,
        "tier": "A",
        "family": "synthetic",
        "n_passes": 1,
        "pool_dir": "outputs/synthetic",
        "expected_candidates": 1000,
        "consensus_dir": "outputs/synthetic/consensus-n1",
    }
    consensus = (
        unions.BASE_DIR / "outputs" / "synthetic" / "consensus-n1"
    )
    # Point the module at a temporary tree instead of touching the repo.
    original = unions.BASE_DIR
    try:
        unions.BASE_DIR = tmp_path
        consensus = tmp_path / "outputs" / "synthetic" / "consensus-n1"
        consensus.mkdir(parents=True)
        # 3 % short of the expected count.
        (consensus / "consensus_t1.geojson").write_text(
            json.dumps(
                {"type": "FeatureCollection", "features": [{}] * 970}
            )
        )
        result = unions.build_union(rung, check_only=True)
        assert result["verdict"] == "STOP-count-mismatch"
        assert result["measured_candidates"] == 970

        # Inside tolerance: 1 % short is fine.
        (consensus / "consensus_t1.geojson").write_text(
            json.dumps(
                {"type": "FeatureCollection", "features": [{}] * 990}
            )
        )
        result = unions.build_union(rung, check_only=True)
        assert result["verdict"] == "OK"
    finally:
        unions.BASE_DIR = original


def test_missing_union_is_a_stop_not_a_zero(tmp_path: Path) -> None:
    """An absent union must stop the rung, never score as zero candidates."""
    original = unions.BASE_DIR
    try:
        unions.BASE_DIR = tmp_path
        result = unions.build_union(
            {
                "row": 1,
                "tier": "A",
                "family": "synthetic",
                "n_passes": 1,
                "expected_candidates": 10,
                "consensus_dir": "nowhere",
            },
            check_only=True,
        )
        assert result["verdict"] == "STOP-union-missing"
        assert result["measured_candidates"] is None
    finally:
        unions.BASE_DIR = original


# --------------------------------------------------------------------------
# The audited flex arithmetic
# --------------------------------------------------------------------------


def _meta(
    *,
    input_tokens: int,
    output_tokens: int,
    thoughts: int = 0,
    list_total: float = 0.0,
    success: int = 0,
    errors: int = 0,
    requests: int | None = None,
) -> dict:
    """Build a minimal ``run.meta.json`` shaped like ``run_pv.py``'s."""
    return {
        "execution_stats": {
            "items_processed": success,
            "items_failed": 0,
            "finish_reason_counts": (
                {"success": success} | ({"error": errors} if errors else {})
            ),
            "retries_total": errors,
            "retries_server_error": errors,
            "retries_rate_limit": 0,
        },
        "usage_stats": {
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens,
            "total_thoughts_tokens": thoughts,
            "by_provider": {
                "google_gemini": {
                    "request_count": (
                        requests if requests is not None else success + errors
                    )
                }
            },
        },
        "cost_estimate": {
            "total_cost_usd": list_total,
            "cost_basis": "list",
            "pricing_used": {"discount": 1.0},
        },
    }


def test_flex_cost_is_half_of_list_not_the_recorded_total() -> None:
    """The meta's own total is list price; the audited figure is half of it.

    This is the whole reason the driver recomputes: ``run_pv.py`` stamps
    ``cost_basis: "list"`` with ``discount: 1.0`` even under ``--service-tier
    flex``, so trusting ``total_cost_usd`` would double every figure.
    """
    meta = _meta(
        input_tokens=1_000_000,
        output_tokens=100_000,
        list_total=0.80,  # 1.0M x 0.50 + 0.1M x 3.00
        success=500,
    )
    cost = verifier.audited_flex_usd(meta)
    # 1.0M x 0.25 + 0.1M x 1.50 = 0.25 + 0.15
    assert cost["flex_usd"] == pytest.approx(0.40)
    assert cost["list_usd_recorded"] == pytest.approx(0.80)
    assert cost["flex_usd"] == pytest.approx(cost["list_usd_recorded"] / 2)


def test_thinking_tokens_are_billed_at_the_output_rate() -> None:
    """Thinking tokens must not be dropped from the audited basis."""
    without = verifier.audited_flex_usd(
        _meta(input_tokens=0, output_tokens=1_000_000)
    )
    with_thinking = verifier.audited_flex_usd(
        _meta(input_tokens=0, output_tokens=0, thoughts=1_000_000)
    )
    assert without["flex_usd"] == pytest.approx(1.50)
    assert with_thinking["flex_usd"] == pytest.approx(1.50)


def test_requests_and_verified_candidates_are_kept_apart() -> None:
    """Retries make billed requests exceed verified candidates.

    Tier A row 10 verified 2,755 candidates in 2,898 requests after 143
    server-error retries; conflating them would misstate both the call count
    and the per-call cost.
    """
    cost = verifier.audited_flex_usd(
        _meta(
            input_tokens=1_000,
            output_tokens=1_000,
            success=2_755,
            errors=143,
            requests=2_898,
        )
    )
    assert cost["candidates_verified"] == 2_755
    assert cost["api_requests"] == 2_898
    assert cost["retries_server_error"] == 143


def test_hard_stop_is_above_the_approved_total() -> None:
    """The ceiling must leave headroom over the approved figure, not sit under it."""
    assert verifier.HARD_STOP_USD == 30.00
    assert verifier.HARD_STOP_USD > 24.84


def test_verifier_never_overrides_the_config() -> None:
    """R1: the module must not carry model/temperature/thinking overrides."""
    source = Path(verifier.__file__).read_text()
    for flag in ("--model", "--thinking-level", "--temperature"):
        assert f'"{flag}"' not in source, (
            f"{flag} must never be passed: it would shadow the carried "
            "verifier config and break ruling R1"
        )
    assert '"--service-tier"' in source
    assert '"flex"' in source


# --------------------------------------------------------------------------
# Stage-path resolution
# --------------------------------------------------------------------------


def test_pv_diag_rungs_verify_inside_their_pool() -> None:
    """The pv-diag-384 convention: ``<pool>/verified-v1-n<N>``."""
    paths = verifier.resolve_paths(
        {
            "pool_dir": "outputs/h11/pv-diag-384/image-n5/image-t0.7",
            "n_passes": 3,
            "verify_dir": (
                "outputs/h11/pv-diag-384/image-n5/image-t0.7/verified-v1-n3"
            ),
            "verifier_stage": "image-n5-image-t0.7-verified-v1-n3",
        }
    )
    assert paths["verify_dir"].endswith("verified-v1-n3")
    assert paths["crops_dir"].endswith("verified-v1-n3/crops")
    assert paths["tiles_dir"] == "inputs/tiles"


@pytest.mark.parametrize("k", [1, 3])
def test_g37_rungs_use_the_screens_own_verifier_tree(k: int) -> None:
    """The 3.7 screen keeps verify_kN and crops_kN as siblings, on ov192 tiles."""
    paths = verifier.resolve_paths(
        {
            "pool_dir": "outputs/gemini37-screen-2026-08-28/g384_ov192_g37",
            "n_passes": k,
            "verify_dir": "unused",
            "verifier_stage": "unused",
        }
    )
    assert paths["verify_dir"].endswith(f"g384_ov192_g37/verify_k{k}")
    assert paths["crops_dir"].endswith(f"g384_ov192_g37/crops_k{k}")
    assert paths["verifier_stage"] == f"g384_ov192_g37-union-k{k}-verify"
    assert paths["tiles_dir"] == "inputs/tiles_384_ov192"


# --------------------------------------------------------------------------
# Operating-point selection
# --------------------------------------------------------------------------


def _sweep(rows: list[tuple[int, float, float, int]]) -> list[dict]:
    """Build sweep rows from (vote_t, prob_t, f1, buffer_m) tuples."""
    return [
        {
            "config": "synthetic",
            "vote_t": vote_t,
            "prob_t": prob_t,
            "n": 100,
            "p": 0.9,
            "r": 0.9,
            "f1": f1,
            "buffer_m": buffer_m,
        }
        for vote_t, prob_t, f1, buffer_m in rows
    ]


def test_argmax_reads_only_the_headline_buffer(tmp_path: Path) -> None:
    """A better F1 at 50 m must not win the 20 m argmax."""
    path = tmp_path / "sweep.json"
    path.write_text(
        json.dumps(
            _sweep(
                [
                    (1, 0.15, 0.80, 20),
                    (2, 0.20, 0.85, 20),
                    (3, 0.25, 0.99, 50),
                ]
            )
        )
    )
    best = score.argmax_at_headline(path)
    assert (best["vote_t"], best["prob_t"]) == (2, 0.20)
    assert best["f1"] == 0.85


def test_argmax_tie_break_prefers_the_least_thresholded_point(
    tmp_path: Path,
) -> None:
    """Documented rule: highest F1, then lowest vote_t, then lowest prob_t."""
    path = tmp_path / "sweep.json"
    path.write_text(
        json.dumps(
            _sweep(
                [
                    (4, 0.30, 0.88, 20),
                    (1, 0.15, 0.88, 20),
                    (1, 0.25, 0.88, 20),
                    (2, 0.15, 0.88, 20),
                ]
            )
        )
    )
    best = score.argmax_at_headline(path)
    assert (best["vote_t"], best["prob_t"]) == (1, 0.15)
    assert best["n_ties"] == 3


def test_cell_directory_follows_the_board_convention() -> None:
    """``<run_id>__<label with dots as underscores>``."""
    assert (
        score.cell_dir_name("pv-diag-384", "pv-min-text-t0.7-n1-opmax")
        == "pv-diag-384__pv-min-text-t0_7-n1-opmax"
    )


def test_condition_labels_follow_each_familys_own_convention() -> None:
    """pv-diag-384 uses ``<stem>-n<K>-...``; the 3.7 screen uses ``k<K>``."""
    pv = score.condition_labels(
        {
            "n_passes": 3,
            "run_id": "pv-diag-384",
            "label_stem": "pv-min-text-t0.7",
        },
        0.15,
    )
    assert pv["opmax"] == "pv-min-text-t0.7-n3-opmax"
    assert pv["carried"] == "pv-min-text-t0.7-n3-carried-p0.15-k3"

    g37 = score.condition_labels(
        {
            "n_passes": 1,
            "run_id": "gemini37-screen-2026-08-28",
            "label_stem": "g37-text",
        },
        0.10,
    )
    assert g37["opmax"] == "g37-text-k1-verified-opmax"
    assert g37["carried"] == "g37-text-k1-verified-carried-p0.10-k1"


def test_carried_prob_is_the_familys_own_committed_threshold() -> None:
    """0.15 for the Gemini 3 pools, 0.10 for the 3.7 GS screen."""
    assert score.CARRIED_PROB_BY_RUN["pv-diag-384"] == 0.15
    assert score.CARRIED_PROB_BY_RUN["gemini37-screen-2026-08-28"] == 0.10


def test_board_frame_is_the_scoring_recipe() -> None:
    """R2 tiers on era2-b-487, with the project's standard GS recipe."""
    assert score.BOARD_BOUNDS.endswith("era2_b_intersection_bounds.geojson")
    assert score.ERA2_BOUNDS.endswith("full_evaluation_bounds.geojson")
    assert score.BOARD_BOUNDS != score.ERA2_BOUNDS
    assert len(score.BUFFERS) == 14
    assert score.HEADLINE_BUFFER == 20
    assert score.BOOTSTRAP == 10_000
    assert score.SEED == 42


# --------------------------------------------------------------------------
# The two carried readings
# --------------------------------------------------------------------------


@pytest.mark.parametrize("k", [1, 3])
def test_carried_readings_coincide_at_the_new_rungs(k: int) -> None:
    """Every Phase 2 rung is at K = 1 or K = 3, where the readings agree.

    This is why the ambiguity between ``k = K`` and the stride shell does not
    touch the rungs Phase 2 bought.
    """
    readings = carried.CARRIED_VOTE_READINGS
    assert readings["k-equals-K"][k] == readings["stride-shell"][k]


@pytest.mark.parametrize("k", [5, 10])
def test_carried_readings_diverge_above_k3(k: int) -> None:
    """At K = 5 and K = 10 the two readings are different operating points."""
    readings = carried.CARRIED_VOTE_READINGS
    assert readings["k-equals-K"][k] != readings["stride-shell"][k]
    assert readings["stride-shell"][k] < readings["k-equals-K"][k]


def test_stride_shell_matches_the_committed_gs_ladder() -> None:
    """1 / 3 / 4 / 8 at K = 1 / 3 / 5 / 10 — the inventory § 2 k column."""
    assert carried.CARRIED_VOTE_READINGS["stride-shell"] == {
        1: 1,
        3: 3,
        5: 4,
        10: 8,
    }


def test_r1_filter_excludes_swapped_verifier_cells() -> None:
    """Only the carried adversarial v1 verifier counts as a ladder rung."""
    source = Path(carried.__file__).read_text()
    assert 'variant") == "v1"' in source
    assert 'verify_adversarial.md"' in source


# --------------------------------------------------------------------------
# Cost model and table rendering
# --------------------------------------------------------------------------


def test_cost_constants_match_the_registered_pareto_model() -> None:
    """The Gemini 3 constants must equal build_pareto_v2.py's, not drift."""
    from scripts import build_pareto_v2

    assert tables.MIN_PASS_USD == build_pareto_v2.MIN_PASS_USD
    assert tables.HIGH_PASS_USD == build_pareto_v2.HIGH_PASS_USD
    assert tables.VF_CALL_USD == build_pareto_v2.VF_CALL_USD


def test_every_family_has_a_named_pass_anchor() -> None:
    """No family may carry an unexplained proposer cost."""
    for pool, meta in tables.FAMILIES.items():
        assert meta["pass_anchor"] in tables.PASS_ANCHORS, pool
        assert tables.PASS_ANCHORS[meta["pass_anchor"]].strip()


def test_fourteen_families_are_covered() -> None:
    """Thirteen pv-diag-384 pools plus the 3.7 GS screen."""
    assert len(tables.FAMILIES) == 14
    assert "g384_ov192_g37" in tables.FAMILIES


def test_families_cover_exactly_the_worklists_pools() -> None:
    """The table builder and the union builder must agree on the pool set."""
    worklist_pools = {rung["pool_slug"] for rung in unions.load_rungs()}
    assert worklist_pools == set(tables.FAMILIES)


def test_fmt_renders_missing_values_as_an_em_dash() -> None:
    """A missing metric must read as absent, never as zero."""
    assert tables.fmt(None) == "—"
    assert tables.fmt(0.8735) == "0.8735"
    assert tables.fmt(412, 0) == "412"
