"""
Tier-1 tests for the 55-map image study scripts kept beside their results.

Three drivers live under ``results/`` rather than ``scripts/`` (the 3.7 K = 5
replicates of arm 1 and arm 2, and the inheritance ladder). Since 2026-10-09
they derive the repository root from their own location. It was hard-coded to
``/home/shawn/Code/map-reader-llm``, so a scratch copy read its inputs from,
and wrote six tracked files into, sapphire's shared checkout
(``planning/paper-writeup-continuity.md``).

The modules are imported from their files, as their own command lines run
them. Nothing here reads the repository's data.
"""

from __future__ import annotations

import importlib.util
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
