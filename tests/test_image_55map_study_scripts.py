"""
Tier-1 tests for the 55-map image study scripts kept beside their results.

Three drivers live under ``results/`` rather than ``scripts/`` (the 3.7 K = 5
replicates of arm 1 and arm 2, and the inheritance ladder), and one under
``reports/`` (the W2.7 subset replicates). Two changes of 2026-10-09 are
pinned here:

* the three ``results/`` drivers derive the repository root from their own
  location. It was hard-coded to ``/home/shawn/Code/map-reader-llm``, so a
  scratch copy read its inputs from, and wrote six tracked files into,
  sapphire's shared checkout (``planning/paper-writeup-continuity.md``);
* the arm 1 replicate reads each leg's ``_repaired`` copy where one holds
  ``probabilities.json`` (D55 Q4, D58 Q8; ``scripts/lib_verify_dirs.py``), and
  the W2.7 pass cache can be moved off ``/tmp`` (``W27_CACHE``), so a scratch
  run writes only inside its own tree.

The modules are imported from their files, as their own command lines run
them. Nothing here reads the repository's data.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.tier1

STUDY_SCRIPTS = {
    "replicate_k5_arm1": "results/gemini37-image-55map-2026-09-13/"
                         "replicate-k5-arm1-batch-2026-09-20/replicate_k5_arm1.py",
    "replicate_k5_arm2": "results/gemini37-image-55map-2026-09-13/"
                         "replicate-k5-arm2-batch-2026-09-20/replicate_k5_arm2.py",
    "inheritance_ladder": "results/gemini37-image-55map-2026-09-13/"
                          "inheritance-2026-09-20/inheritance_ladder.py",
    "w27_55map_subset_replicates": "reports/w27-replicate-floors-2026-10-06-scripts/"
                                   "w27_55map_subset_replicates.py",
}


def _load(name: str, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Import one study script from its file under a private module name."""
    spec = importlib.util.spec_from_file_location(f"_study_{name}",
                                                  PROJECT_ROOT / STUDY_SCRIPTS[name])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # A dataclass needs its module registered while the class body runs.
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("name", ["replicate_k5_arm1", "replicate_k5_arm2",
                                  "inheritance_ladder"])
def test_the_repository_root_is_this_tree(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load(name, monkeypatch)
    assert module.PROJECT_ROOT == PROJECT_ROOT
    assert (module.PROJECT_ROOT / "scripts" / "gemini37_image_55map_r2.py").is_file()


@pytest.mark.parametrize("name", ["replicate_k5_arm1", "replicate_k5_arm2",
                                  "inheritance_ladder"])
def test_no_study_script_hard_codes_a_home_directory(name: str) -> None:
    source = (PROJECT_ROOT / STUDY_SCRIPTS[name]).read_text()
    assert 'Path("/home/' not in source


def test_the_arm1_replicate_reads_a_repaired_copy_where_one_exists(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load("replicate_k5_arm1", monkeypatch)
    leg = tmp_path / "verify_k5_arm1_replicate-batch-2026-09-20"
    for vdir, p in ((leg, 0.0), (tmp_path / f"{leg.name}_repaired", 0.2)):
        vdir.mkdir()
        (vdir / "probabilities.json").write_text(json.dumps(
            {"results": {"candidate_00000": {"mound_probability": p}}}))
    monkeypatch.delenv("MAP_READER_VERIFY_DIRS", raising=False)
    assert module.leg_dir(leg) == tmp_path / f"{leg.name}_repaired"
    assert module._probs(module.leg_dir(leg)) == {"candidate_00000": 0.2}
    monkeypatch.setenv("MAP_READER_VERIFY_DIRS", "fixed")
    assert module.leg_dir(leg) == leg
    assert module._probs(module.leg_dir(leg)) == {"candidate_00000": 0.0}


def test_the_w27_pass_cache_can_be_moved(tmp_path: Path,
                                         monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("W27_CACHE", raising=False)
    assert _load("w27_55map_subset_replicates", monkeypatch).CACHE == Path("/tmp/w27/passes")
    monkeypatch.setenv("W27_CACHE", str(tmp_path / "passes"))
    assert _load("w27_55map_subset_replicates", monkeypatch).CACHE == tmp_path / "passes"
