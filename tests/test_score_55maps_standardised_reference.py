"""
Tests for ``scripts/score_55maps_standardised_reference.py`` (Session 132,
queue items 2–3).

Following ``tests/test_marking_campaign_gates.py``'s convention — a gate
that cannot fail is not a gate — every tier-1 case here manufactures the
defect its gate exists to catch:

- the feature-count crosscheck must hard-stop on an n_det mismatch;
- the A0 reproduction gate must fail on a tolerance breach, a wrong A1
  duplicate-drop count, a missing summary, or an empty cell list;
- the C-leg extension census must hard-stop on a truncated layer;
- legs B/C must be unreachable while the gate is red, and impossible
  without a prior PASS gate when leg A is not requested;
- the decomposition arithmetic must attribute the A0→A1→B→C deltas to
  the right layers.

The tier-2 case pins the real standardised layers (committed-state
insurance, ~1 s).
"""

import json
import sys

import pytest

import scripts.score_55maps_standardised_reference as driver

ANCHOR = driver.CELLS[0]["gate_legacy_50m"]  # TH7-k4


def _summary_row(f1, drops=1, promoted=414):
    """Fabricate one engine result row at R = 50 m."""
    return {
        "R_m": 50, "TP": 3801, "FP": 363, "FN": 1360,
        "n_ref_student_only": 4746,
        "n_reviewer_promoted_at_R": promoted,
        "n_phantom_duplicates_dropped": drops,
        "n_ref_extended": 5161,
        "precision": 0.91, "recall": 0.73, "F1": f1,
        "F1_CI": [f1 - 0.01, f1 + 0.01],
        "tile_classification": {
            "mcc": 0.67, "mcc_CI": [0.65, 0.69],
            "tp": 2300, "tn": 4800, "fp": 180, "fn": 1250,
            "sensitivity": 0.65, "specificity": 0.96,
        },
    }


def _summary(f1, drops=1, promoted=414, r_values=(50,)):
    rows = []
    for r in r_values:
        row = dict(_summary_row(f1, drops=drops, promoted=promoted))
        row["R_m"] = r
        rows.append(row)
    return {"results": rows}


# --------------------------------------------------------------------------- #
# Feature-count crosscheck (the Session 77 wrong-source class)
# --------------------------------------------------------------------------- #

def _tmp_cell(tmp_path, n_features, n_documented):
    det = tmp_path / "det.geojson"
    det.write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": None, "properties": {}}
        ] * n_features,
    }))
    return {
        "label": "FAKE", "config": "x", "k": 1, "role": "test",
        "det": str(det.relative_to(driver.REPO))
        if det.is_relative_to(driver.REPO) else str(det),
        "n_det": n_documented, "gate_legacy_50m": 0.5,
    }


@pytest.mark.tier1
def test_crosscheck_passes_on_match(tmp_path):
    """A matching count yields an OK row and no stop."""
    cell = _tmp_cell(tmp_path, 3, 3)
    cell["det"] = str(tmp_path / "det.geojson")
    rows = driver.crosscheck_feature_counts([cell])
    assert rows[0]["verdict"] == "OK"


@pytest.mark.tier1
def test_crosscheck_hard_stops_on_mismatch(tmp_path):
    """An off-by-one count is a stop state, never a warning."""
    cell = _tmp_cell(tmp_path, 3, 4)
    cell["det"] = str(tmp_path / "det.geojson")
    with pytest.raises(SystemExit, match="crosscheck FAILED"):
        driver.crosscheck_feature_counts([cell])


# --------------------------------------------------------------------------- #
# The A0 reproduction gate + A1 baseline checks
# --------------------------------------------------------------------------- #

def _one_cell():
    return [driver.CELLS[0]]


@pytest.mark.tier1
def test_gate_passes_on_exact_reproduction():
    """A0 at the committed value + A1 with one drop → PASS."""
    results = {
        ("TH7-k4", "A0"): _summary(ANCHOR, drops=0, promoted=415),
        ("TH7-k4", "A1"): _summary(ANCHOR + 8.7e-05, drops=1),
    }
    passed, rows = driver.evaluate_gate(_one_cell(), results)
    assert passed is True
    assert rows[0]["verdict"] == "PASS"
    assert rows[0]["a1_minus_a0_dedup_fix"] == pytest.approx(8.7e-05)


@pytest.mark.tier1
def test_gate_fails_beyond_tolerance():
    """A 5e-6 miss breaches the 1e-6 tolerance — the gate must go red
    rather than absorb it (the stale-anchor failure class)."""
    results = {
        ("TH7-k4", "A0"): _summary(ANCHOR + 5e-06, drops=0),
        ("TH7-k4", "A1"): _summary(ANCHOR + 9e-05, drops=1),
    }
    passed, rows = driver.evaluate_gate(_one_cell(), results)
    assert passed is False
    assert rows[0]["verdict"] == "FAIL"


@pytest.mark.tier1
def test_gate_fails_on_wrong_a1_drop_count():
    """A1 must drop exactly the one ruling-20c twin; 2 drops = drifted
    inputs."""
    results = {
        ("TH7-k4", "A0"): _summary(ANCHOR, drops=0),
        ("TH7-k4", "A1"): _summary(ANCHOR + 8.7e-05, drops=2),
    }
    passed, _ = driver.evaluate_gate(_one_cell(), results)
    assert passed is False


@pytest.mark.tier1
def test_gate_fails_on_missing_summary():
    """A cell with no A0/A1 summary is a FAIL, never a silent skip."""
    passed, rows = driver.evaluate_gate(_one_cell(), {})
    assert passed is False
    assert "missing" in rows[0]["verdict"]


@pytest.mark.tier1
def test_gate_cannot_pass_vacuously():
    """An empty cell list must not produce a PASS (the --smoke/--cells
    empty-intersection failure class)."""
    passed, rows = driver.evaluate_gate([], {})
    assert passed is False
    assert rows == []


# --------------------------------------------------------------------------- #
# C-leg extension census (silent-truncation guard, audit finding S1)
# --------------------------------------------------------------------------- #

@pytest.mark.tier1
def test_check_c_leg_passes_on_full_layer():
    results = {("TH7-k4", "C"): _summary(
        0.83, drops=0, promoted=driver.N_EXTENSION_STD, r_values=(20, 50),
    )}
    rows = driver.check_c_leg(
        _one_cell(), results, expected_buffers=[20, 50],
    )
    assert rows[0]["verdict"] == "OK"


@pytest.mark.tier1
def test_check_c_leg_stops_on_truncated_layer():
    """278 of 279 admitted at any buffer is a stop state."""
    good = _summary_row(0.83, drops=0, promoted=driver.N_EXTENSION_STD)
    bad = dict(good)
    bad["R_m"] = 20
    bad["n_reviewer_promoted_at_R"] = driver.N_EXTENSION_STD - 1
    results = {("TH7-k4", "C"): {"results": [bad, good]}}
    with pytest.raises(SystemExit, match="extension census FAILED"):
        driver.check_c_leg(_one_cell(), results, expected_buffers=[20, 50])


@pytest.mark.tier1
def test_check_c_leg_stops_on_missing_summary():
    with pytest.raises(SystemExit, match="no C summary"):
        driver.check_c_leg(_one_cell(), {}, expected_buffers=[50])


@pytest.mark.tier1
def test_check_c_leg_stops_on_empty_or_short_sweep():
    """An empty result list or a buffer-truncated sweep can never pass
    the census (re-audit M2)."""
    with pytest.raises(SystemExit, match="buffers"):
        driver.check_c_leg(
            _one_cell(), {("TH7-k4", "C"): {"results": []}},
            expected_buffers=[20, 50],
        )
    only_50 = _summary(
        0.83, drops=0, promoted=driver.N_EXTENSION_STD, r_values=(50,),
    )
    with pytest.raises(SystemExit, match="buffers"):
        driver.check_c_leg(
            _one_cell(), {("TH7-k4", "C"): only_50},
            expected_buffers=[20, 50],
        )


# --------------------------------------------------------------------------- #
# Prior-gate requirement for B/C-only invocations
# --------------------------------------------------------------------------- #

def _write_gate(path, gate_passed, labels, *, git_commit=None,
                tolerance=None, a1_fields=True):
    """Write a gate file; defaults mimic a CURRENT full A-leg gate."""
    rows = []
    for lb in labels:
        row = {"label": lb, "verdict": "PASS"}
        if a1_fields:
            row["a1_drops"] = driver.A1_EXPECTED_DROPS
            row["a1_expected_drops"] = driver.A1_EXPECTED_DROPS
        rows.append(row)
    path.write_text(json.dumps({
        "gate_passed": gate_passed,
        "git_commit": (
            git_commit if git_commit is not None
            else driver.engine.git_commit_hash()
        ),
        "gate_tolerance": (
            tolerance if tolerance is not None else driver.GATE_TOL
        ),
        "gate_rows": rows,
        "c_leg_extension_census": [],
    }))


@pytest.mark.tier1
def test_prior_gate_required_when_absent(tmp_path):
    with pytest.raises(SystemExit, match="no prior"):
        driver.require_prior_gate(_one_cell(), tmp_path / "missing.json")


@pytest.mark.tier1
def test_prior_gate_rejects_uncertified_cell(tmp_path):
    gate = tmp_path / "validation-gate.json"
    _write_gate(gate, True, ["TM-k4"])  # certifies a different cell
    with pytest.raises(SystemExit, match="does not certify"):
        driver.require_prior_gate(_one_cell(), gate)


@pytest.mark.tier1
def test_prior_gate_accepts_full_pass(tmp_path):
    gate = tmp_path / "validation-gate.json"
    _write_gate(gate, True, ["TH7-k4"])
    prior = driver.require_prior_gate(_one_cell(), gate)
    assert prior["gate_passed"] is True


@pytest.mark.tier1
def test_prior_gate_rejects_stale_commit(tmp_path):
    """A gate minted at a different engine commit certifies nothing —
    the re-audit C1 failure class (stale gate inherited silently)."""
    gate = tmp_path / "validation-gate.json"
    _write_gate(gate, True, ["TH7-k4"], git_commit="c951aa749deadbeef")
    with pytest.raises(SystemExit, match="STALE"):
        driver.require_prior_gate(_one_cell(), gate)


@pytest.mark.tier1
def test_prior_gate_rejects_looser_tolerance(tmp_path):
    """A gate earned under a looser tolerance (the pre-fix 1e-4) is not
    a certification under the current 1e-6 contract."""
    gate = tmp_path / "validation-gate.json"
    _write_gate(gate, True, ["TH7-k4"], tolerance=1e-4)
    with pytest.raises(SystemExit, match="STALE"):
        driver.require_prior_gate(_one_cell(), gate)


@pytest.mark.tier1
def test_prior_gate_rejects_pre_a0_schema(tmp_path):
    """A gate row without the A0/A1 fields predates the gate redesign
    and must be re-earned, not inherited."""
    gate = tmp_path / "validation-gate.json"
    _write_gate(gate, True, ["TH7-k4"], a1_fields=False)
    with pytest.raises(SystemExit, match="does not certify"):
        driver.require_prior_gate(_one_cell(), gate)


# --------------------------------------------------------------------------- #
# Gate-before-vary ordering through main() (audit findings S5/S6/S9)
# --------------------------------------------------------------------------- #

def _run_main(monkeypatch, tmp_path, fake_score, argv_extra):
    calls = []

    def recording_score(job):
        calls.append((job["label"], job["leg"]))
        return fake_score(job)

    monkeypatch.setattr(driver, "_score_cell", recording_score)
    monkeypatch.setattr(sys, "argv", [
        "score_55maps_standardised_reference.py",
        "--output-base", str(tmp_path / "out"),
        "--cells", "TH7-k4",
    ] + argv_extra)
    return calls


@pytest.mark.tier1
def test_red_gate_halts_before_b_and_c(monkeypatch, tmp_path):
    """A red A0 gate must stop the run with B/C never invoked, and the
    gate evidence must already be on disk."""
    def failing(job):
        return {"label": job["label"], "leg": job["leg"],
                "summary": _summary(ANCHOR + 1e-03, drops=1)}

    calls = _run_main(monkeypatch, tmp_path, failing, ["--legs", "A", "B", "C"])
    with pytest.raises(SystemExit, match="gate FAILED"):
        driver.main()
    assert {leg for _, leg in calls} == {"A0", "A1"}
    gate = json.loads(
        (tmp_path / "out" / "validation-gate.json").read_text()
    )
    assert gate["gate_passed"] is False


@pytest.mark.tier1
def test_green_gate_runs_all_legs_in_order(monkeypatch, tmp_path):
    """A green gate lets B/C run AFTER A, and the decomposition JSON
    attributes each delta to the right layer."""
    def scripted(job):
        f1 = {
            "A0": ANCHOR,
            "A1": ANCHOR + 8.7e-05,
            "B": ANCHOR + 2.0e-04,
            "C": ANCHOR + 5.0e-04,
        }[job["leg"]]
        drops = {"A0": 0, "A1": 1, "B": 3, "C": 0}[job["leg"]]
        promoted = (
            driver.N_EXTENSION_STD if job["leg"] == "C" else 414
        )
        r_values = (
            tuple(driver.BUFFERS) if job["leg"] == "C" else (50,)
        )
        return {"label": job["label"], "leg": job["leg"],
                "summary": _summary(
                    f1, drops=drops, promoted=promoted, r_values=r_values,
                )}

    calls = _run_main(
        monkeypatch, tmp_path, scripted, ["--legs", "A", "B", "C"],
    )
    driver.main()
    legs_in_order = [leg for _, leg in calls]
    assert legs_in_order.index("B") > legs_in_order.index("A1")
    assert legs_in_order.index("C") > legs_in_order.index("A0")
    decomp = json.loads(
        (tmp_path / "out" / "abc-decomposition-50m.json").read_text()
    )
    cell = decomp["cells"][0]
    assert cell["A1_minus_A0_dedup_fix"] == pytest.approx(8.7e-05)
    assert cell["B_minus_A1_student_layer"] == pytest.approx(1.13e-04)
    assert cell["C_minus_B_extension_layer"] == pytest.approx(3.0e-04)
    gate = json.loads(
        (tmp_path / "out" / "validation-gate.json").read_text()
    )
    assert gate["gate_passed"] is True
    assert gate["c_leg_extension_census"][0]["verdict"] == "OK"


@pytest.mark.tier1
def test_bc_without_a_demands_prior_gate(monkeypatch, tmp_path):
    """--legs C with no prior gate file is a stop state; nothing scores."""
    calls = _run_main(monkeypatch, tmp_path, lambda job: None, ["--legs", "C"])
    with pytest.raises(SystemExit, match="no prior"):
        driver.main()
    assert calls == []


@pytest.mark.tier1
def test_smoke_conflicts_with_cells(monkeypatch, tmp_path):
    """--smoke and --cells together are refused before any work."""
    calls = _run_main(
        monkeypatch, tmp_path, lambda job: None, ["--smoke"],
    )
    with pytest.raises(SystemExit, match="mutually exclusive"):
        driver.main()
    assert calls == []


@pytest.mark.tier1
def test_smoke_is_quarantined_from_production_output(monkeypatch, tmp_path):
    """A smoke run writes under <output-base>/smoke/, never over the
    production gate/decomposition/CSV (re-audit M1)."""
    def scripted(job):
        f1 = {"A0": ANCHOR, "A1": ANCHOR + 8.7e-05, "C": ANCHOR + 5e-04}
        drops = {"A0": 0, "A1": 1, "C": 0}
        promoted = (
            driver.N_EXTENSION_STD if job["leg"] == "C" else 414
        )
        return {
            "label": job["label"], "leg": job["leg"],
            "summary": _summary(
                f1[job["leg"]], drops=drops[job["leg"]],
                promoted=promoted, r_values=(20, 50),
            ),
        }

    calls = []

    def recording_score(job):
        calls.append((job["label"], job["leg"]))
        return scripted(job)

    monkeypatch.setattr(driver, "_score_cell", recording_score)
    monkeypatch.setattr(sys, "argv", [
        "score_55maps_standardised_reference.py",
        "--output-base", str(tmp_path / "out"),
        "--smoke",
    ])
    driver.main()
    assert (tmp_path / "out" / "smoke" / "validation-gate.json").exists()
    assert not (tmp_path / "out" / "validation-gate.json").exists()


# --------------------------------------------------------------------------- #
# Real standardised layers (tier 2 — committed-state insurance)
# --------------------------------------------------------------------------- #

@pytest.mark.tier2
def test_real_standardised_layers_census():
    """The committed layers match the census the driver pins: 279
    extension records, min nearest_student_m 10.32 m, and ZERO records
    lost to the 5 m channel-duplicate audit."""
    import geopandas as gpd

    from scripts.compute_corrected_f1_multi_buffer import (
        build_extended_gt,
        load_standardised_extension,
    )

    ext = load_standardised_extension(driver.EXTENSION_STD)
    assert len(ext) == driver.N_EXTENSION_STD
    assert float(ext["nearest_student_m"].min()) == pytest.approx(
        driver.MIN_NEAREST_STUDENT_M
    )
    student = gpd.read_file(driver.STUDENT_STD).to_crs(ext.crs)
    gt = build_extended_gt(student, ext)
    assert gt.attrs["n_phantom_duplicates_dropped"] == 0
    assert len(gt) == driver.N_STUDENT_STD + driver.N_EXTENSION_STD
