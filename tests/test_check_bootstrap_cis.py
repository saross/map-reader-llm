"""Tier-1 tests for the bootstrap CI source re-count gate.

``scripts/check_bootstrap_cis.py`` exists because a confidence-interval (CI)
entry keyed by a path-string carries no binding to its source file's *content*:
the March 2026 E70 recovery campaign grew 85 pass files in place and 85 CIs
went on serving pre-recovery numbers under post-recovery names, silently, for
six months (``reports/name-keyed-cache-audit-2026-09-12.md`` § 4 Finding 1).

The tests come in two halves:

* **Synthetic** — a tiny hand-built store and three-feature GeoJSONs exercise
  every verdict the checker can reach (match, mismatch, unresolved, the prefix
  remap, the annotated-unresolved path) plus the exit-status contract. These are
  hermetic and fast.
* **Committed store** — one test runs the gate against the real
  ``results/all-bootstrap-cis.json``. It asserts zero mismatches, so any future
  re-materialisation under an existing ``source_file`` fails tier-1 rather than
  surfacing in a paper six months later. It reads two committed GeoJSON trees,
  which is why it is capped: see the note on its marker below.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.check_bootstrap_cis as cbc

pytestmark = pytest.mark.tier1

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def write_geojson(path: Path, n_features: int) -> None:
    """Write a minimal point FeatureCollection with ``n_features`` features.

    Args:
        path: Destination file (parent directories are created).
        n_features: How many point features to emit.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"label": f"mound_{i}"},
                "geometry": {"type": "Point", "coordinates": [float(i), float(i)]},
            }
            for i in range(n_features)
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def entry(n_detections: int, source_file: str, **extra: object) -> dict:
    """Build a store entry shaped like the real ones.

    Args:
        n_detections: The ``n_detections`` the entry claims.
        source_file: The ``source_file`` string.
        **extra: Additional fields (e.g. ``source_status``).

    Returns:
        One entry mapping.
    """
    block = {"mean": 0.5, "ci_lower": 0.4, "ci_upper": 0.6}
    return {
        "f1": dict(block),
        "precision": dict(block),
        "recall": dict(block),
        "n_iterations": 1000,
        "n_detections": n_detections,
        "source_file": source_file,
        **extra,
    }


@pytest.fixture()
def synthetic_store(tmp_path: Path) -> Path:
    """A four-entry store over synthetic GeoJSONs covering every verdict.

    Layout mirrors the real defect: sources are recorded under a ``data/``
    prefix that does not exist, and resolve only under ``outputs/``.

    * ``ok`` — 3 recorded, 3 on disk: MATCH.
    * ``grown`` — 3 recorded, 5 on disk (with a ``patched`` sidecar): MISMATCH.
    * ``gone`` — names a file that exists under neither prefix: UNRESOLVED.
    * ``label`` — a ``consensus:`` pseudo-path, annotated: UNRESOLVED, known.

    Returns:
        Path to the store JSON. The repo root for resolution is ``tmp_path``.
    """
    write_geojson(tmp_path / "outputs/retest/ok/detections_ok.geojson", 3)
    write_geojson(tmp_path / "outputs/retest/grown/detections_grown.geojson", 5)
    sidecar = tmp_path / "outputs/retest/grown/detections_grown.tiles.json"
    sidecar.write_text(
        json.dumps({"total_tiles": 4, "patched": ["tile_a.png", "tile_b.png"]}),
        encoding="utf-8",
    )

    store = {
        "_metadata": {"n_bootstrap": 1000, "random_seed": 42},
        "results": {
            "single:ok": entry(3, "data/retest/ok/detections_ok.geojson"),
            "single:grown": entry(3, "data/retest/grown/detections_grown.geojson"),
            "single:gone": entry(7, "data/retest/gone/detections_gone.geojson"),
            "consensus-n30:label": entry(
                11, "consensus:consensus-n30:high/25of30", source_status="unresolved"
            ),
        },
    }
    path = tmp_path / "store.json"
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")
    return path


def verdicts(store: Path, repo_root: Path, remap: bool) -> dict[str, cbc.EntryResult]:
    """Run the checker and index the results by entry key."""
    payload = json.loads(store.read_text(encoding="utf-8"))
    results = cbc.check_entries(payload, repo_root=repo_root, remap=remap)
    return {r.key: r for r in results}


class TestSyntheticVerdicts:
    """Every verdict the checker can reach, over synthetic fixtures."""

    def test_remap_resolves_and_counts(self, synthetic_store: Path) -> None:
        """With ``--remap`` the matching entry resolves and its count agrees."""
        got = verdicts(synthetic_store, synthetic_store.parent, remap=True)
        assert got["single:ok"].status == cbc.STATUS_MATCH
        assert got["single:ok"].counted == 3
        assert got["single:ok"].delta == 0
        assert got["single:ok"].resolved_path is not None
        assert "outputs/retest/ok" in str(got["single:ok"].resolved_path)

    def test_without_remap_nothing_resolves(self, synthetic_store: Path) -> None:
        """The un-remapped ``data/`` paths resolve to nothing at all.

        This is the pre-repair state of the real store: 100 % unresolved, which
        is why the audit's remap was a necessary inference rather than a
        convenience.
        """
        got = verdicts(synthetic_store, synthetic_store.parent, remap=False)
        assert all(r.status == cbc.STATUS_UNRESOLVED for r in got.values())

    def test_grown_source_is_a_mismatch_with_patched_count(
        self, synthetic_store: Path
    ) -> None:
        """A file that gained features mismatches, and the sidecar is reported.

        ``patched`` is a *list* of recovered tile names in the real sidecars, so
        the checker reports its length — the bug this pins was reading the list
        as a scalar and reporting ``None`` for all 85 entries.
        """
        got = verdicts(synthetic_store, synthetic_store.parent, remap=True)
        grown = got["single:grown"]
        assert grown.status == cbc.STATUS_MISMATCH
        assert (grown.recorded, grown.counted, grown.delta) == (3, 5, 2)
        assert grown.patched == 2

    def test_missing_file_is_unresolved_and_unannotated(
        self, synthetic_store: Path
    ) -> None:
        """A source that exists under no prefix is unresolved and NOT known."""
        got = verdicts(synthetic_store, synthetic_store.parent, remap=True)
        gone = got["single:gone"]
        assert gone.status == cbc.STATUS_UNRESOLVED
        assert gone.annotated is False
        assert gone.counted is None
        assert "gone" in gone.reason

    def test_annotated_pseudo_path_is_known(self, synthetic_store: Path) -> None:
        """A ``consensus:`` label marked ``source_status`` is unresolved-but-known."""
        got = verdicts(synthetic_store, synthetic_store.parent, remap=True)
        label = got["consensus-n30:label"]
        assert label.status == cbc.STATUS_UNRESOLVED
        assert label.annotated is True
        assert "not a file path" in label.reason


class TestSummaryAndExitStatus:
    """The counts and the exit-status contract the tier-1 gate depends on."""

    def test_summary_counts(self, synthetic_store: Path) -> None:
        """Resolved / unresolved / match / mismatch split the entries exactly."""
        payload = json.loads(synthetic_store.read_text(encoding="utf-8"))
        results = cbc.check_entries(
            payload, repo_root=synthetic_store.parent, remap=True
        )
        counts = cbc.summarise(results)
        assert counts["total"] == 4
        assert counts["resolved"] == 2
        assert counts["unresolved"] == 2
        assert counts["match"] == 1
        assert counts["mismatch"] == 1
        assert counts["unresolved_annotated"] == 1
        assert counts["unresolved_new"] == 1

    def test_exit_non_zero_on_any_failure(self, synthetic_store: Path) -> None:
        """Strict mode fails on the mismatch and on both unresolved entries."""
        payload = json.loads(synthetic_store.read_text(encoding="utf-8"))
        results = cbc.check_entries(
            payload, repo_root=synthetic_store.parent, remap=True
        )
        assert cbc.exit_code(results, allow_annotated=False) == 1
        # The annotated pseudo-path is forgiven; the missing file and the
        # mismatch are not.
        assert cbc.exit_code(results, allow_annotated=True) == 1

    def test_allow_annotated_never_forgives_a_mismatch(self, tmp_path: Path) -> None:
        """A mismatch fails even with ``--allow-annotated`` and a ``pre_e70`` block.

        Under the PI's 2026-09-12 ruling the stale entries were re-run, not
        annotated as uncitable, so ``pre_e70`` is history rather than an
        exemption. If this test ever passes with exit 0, the checker has
        regressed to the annotate-and-move-on design.
        """
        write_geojson(tmp_path / "outputs/retest/grown/detections_grown.geojson", 9)
        store = {
            "_metadata": {},
            "results": {
                "single:grown": entry(
                    3,
                    "data/retest/grown/detections_grown.geojson",
                    pre_e70={"n_detections": 3, "f1_mean": 0.5},
                )
            },
        }
        path = tmp_path / "store.json"
        path.write_text(json.dumps(store), encoding="utf-8")
        payload = json.loads(path.read_text(encoding="utf-8"))
        results = cbc.check_entries(payload, repo_root=tmp_path, remap=True)
        assert results[0].status == cbc.STATUS_MISMATCH
        assert results[0].annotated is False
        assert cbc.exit_code(results, allow_annotated=True) == 1

    def test_only_annotated_unresolved_passes(self, tmp_path: Path) -> None:
        """A store whose only failures are annotated-unresolved exits 0."""
        write_geojson(tmp_path / "outputs/retest/ok/detections_ok.geojson", 2)
        store = {
            "_metadata": {},
            "results": {
                "single:ok": entry(2, "data/retest/ok/detections_ok.geojson"),
                "consensus-n30:label": entry(
                    4, "consensus:consensus-n30:text/5of30", source_status="unresolved"
                ),
            },
        }
        path = tmp_path / "store.json"
        path.write_text(json.dumps(store), encoding="utf-8")
        payload = json.loads(path.read_text(encoding="utf-8"))
        results = cbc.check_entries(payload, repo_root=tmp_path, remap=True)
        assert cbc.exit_code(results, allow_annotated=True) == 0
        assert cbc.exit_code(results, allow_annotated=False) == 1

    def test_report_names_the_mismatch(self, synthetic_store: Path) -> None:
        """The text report lists the mismatch with both counts and the delta."""
        payload = json.loads(synthetic_store.read_text(encoding="utf-8"))
        results = cbc.check_entries(
            payload, repo_root=synthetic_store.parent, remap=True
        )
        report = cbc.format_report(results, synthetic_store, allow_annotated=False)
        assert "single:grown" in report
        assert "+2" in report
        assert report.rstrip().endswith("entries.")


class TestMainEntryPoint:
    """The command-line surface, since the tier-1 gate is invoked as a command."""

    def test_main_requires_check(self, synthetic_store: Path) -> None:
        """Calling with no mode is a usage error, not a silent success."""
        with pytest.raises(SystemExit) as excinfo:
            cbc.main([str(synthetic_store)])
        assert excinfo.value.code == 2

    def test_main_json_output(self, synthetic_store: Path, capsys) -> None:
        """``--json`` emits parseable counts and omits the matching entries."""
        status = cbc.main([
            "--check", "--remap", "--json",
            "--repo-root", str(synthetic_store.parent),
            str(synthetic_store),
        ])
        payload = json.loads(capsys.readouterr().out)
        assert status == 1
        assert payload["counts"]["mismatch"] == 1
        assert {e["key"] for e in payload["entries"]} == {
            "single:grown", "single:gone", "consensus-n30:label",
        }


class TestCommittedStore:
    """The drift gate over the real, committed CI store.

    This is the test that would have caught the E70 divergence in March 2026.
    It reads 472 committed GeoJSONs, so it is the slowest thing in this module;
    it stays tier-1 because it is the whole point of the script, and because
    counting features is cheap next to the ~8 s bootstrap that produced each
    entry.
    """

    @pytest.mark.parametrize(
        "store_name", ["all-bootstrap-cis.json", "pv/all-bootstrap-cis.json"]
    )
    def test_committed_store_has_no_drift(self, store_name: str) -> None:
        """Every resolvable entry still matches its source's feature count."""
        store = PROJECT_ROOT / "results" / store_name
        payload = json.loads(store.read_text(encoding="utf-8"))
        results = cbc.check_entries(payload, repo_root=PROJECT_ROOT, remap=False)
        counts = cbc.summarise(results)

        mismatches = [
            f"{r.key}: recorded {r.recorded}, counted {r.counted}"
            for r in results
            if r.status == cbc.STATUS_MISMATCH
        ]
        assert not mismatches, (
            f"{store_name} has drifted from its sources — a pass file changed "
            f"under an existing source_file. Re-run the affected entries with "
            f"scripts/repair_bootstrap_cis.py rather than editing the store:\n"
            + "\n".join(mismatches)
        )
        # Every unresolved entry must be an annotated one; a NEW unresolved
        # entry means a source file moved or was deleted.
        assert counts["unresolved_new"] == 0
        assert cbc.exit_code(results, allow_annotated=True) == 0

    def test_committed_store_paths_need_no_remap(self) -> None:
        """The 2026-09-12 repair left no ``data/**`` path behind.

        Pins the repair itself: before it, all 496 ``source_file`` values named
        a tree that has never existed here.
        """
        store = PROJECT_ROOT / "results" / "all-bootstrap-cis.json"
        payload = json.loads(store.read_text(encoding="utf-8"))
        entries = payload["results"].values()
        assert not [e for e in entries if e["source_file"].startswith("data/")]
        # The originals are preserved rather than discarded.
        repaired = [e for e in entries if "source_file_original" in e]
        assert len(repaired) == 472
        assert all(e["source_file_original"].startswith("data/") for e in repaired)
        assert payload["_path_repair"]["repaired_entries"] == 472

    def test_reran_entries_keep_their_superseded_values(self) -> None:
        """Each re-run entry preserves its pre-E70 numbers and moved its count."""
        store = PROJECT_ROOT / "results" / "all-bootstrap-cis.json"
        payload = json.loads(store.read_text(encoding="utf-8"))
        reran = {k: v for k, v in payload["results"].items() if "pre_e70" in v}
        assert len(reran) == 85
        assert payload["_rerun"]["reran_entries"] == 85
        assert payload["_rerun"]["errors"] == 0
        for key, value in reran.items():
            pre = value["pre_e70"]
            assert set(pre) == {
                "n_detections", "f1_mean", "ci_low", "ci_high", "computed_at",
            }, key
            # Every one of the 85 grew: that is what made it stale.
            assert value["n_detections"] > pre["n_detections"], key
            assert value["f1"]["mean"] != pre["f1_mean"], key
