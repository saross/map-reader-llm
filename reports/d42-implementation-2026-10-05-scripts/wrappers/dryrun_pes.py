"""Regenerate pairwise-effect-sizes-v2.json from the relocated March inputs
under PI ruling D42, without symlinks and without writing into the repository.

Run on sapphire from the repository root:
    cd ~/Code/map-reader-llm && PYTHONHASHSEED=0 .venv/bin/python regen_pes_v2.py \
        --data-dir outputs/ --pv-dir archive/outputs-experimental-pilot/pv \
        --output /tmp/regen-b/pairwise-effect-sizes-v2.json --workers 20
(--data-dir outputs/ is still used for the two on-the-fly N=30 consensus
conditions: outputs/retest/phase3a/track2-text/T0.7/run_*.)
"""
import importlib.util
import sys
from pathlib import Path

REPO = Path.cwd()
sys.path.insert(0, str(REPO))
spec = importlib.util.spec_from_file_location("cpes", REPO / "scripts/compute-pairwise-effect-sizes.py")
m = importlib.util.module_from_spec(spec)
sys.modules["cpes"] = m
spec.loader.exec_module(m)
from scripts import lib_consensus  # noqa: E402

ARCH = REPO / "archive/outputs-experimental-pilot/pv"
SCR = Path("/tmp/regen-b/march-sweeps")  # the one sweep E39 (01c84b841) regenerated
I4 = "phase1/adversarial-text-150/text-n1-t0.0-minimal"
SCR = Path.home() / "cc-scratch/bootstrap-cis/pv-data/sweeps"

# March v2 layout (symlinks of 2026-03-22) -> current location; first match wins
TABLE = [
    ("/DATA/consensus-proposers", ARCH / "consensus-proposers"),
    ("/DATA/retest", REPO / "outputs/retest"),
    ("/PV/results", ARCH / "results"),
    ("/PV/crops", ARCH / "crops-150"),
    ("/PV/sweeps/phase1/adversarial-text-150", SCR / "phase1/adversarial-text-150"),
    ("/PV/sweeps", REPO / "results/pv"),
]


def remap(value):
    """Map a March-layout path onto its current location."""
    if not isinstance(value, Path):
        return value
    text = str(value)
    for old, new in TABLE:
        if text == old or text.startswith(old + "/"):
            return Path(str(new) + text[len(old):])
    return value


_define = m.define_all_comparisons


def define(_data_dir, _pv_dir):
    """The producer's own 52 comparisons, with every input path remapped."""
    comps = _define(Path("/DATA"), Path("/PV"))
    for comp in comps:
        for side in ("condition_a", "condition_b"):
            comp[side] = {k: remap(v) for k, v in comp[side].items()}
    return comps


m.define_all_comparisons = define
# March: outputs/references -> inputs/vectors/references, outputs/bounds -> inputs/vectors/bounds
m.load_shared_data = lambda _d: lib_consensus.load_shared_data(REPO / "inputs/vectors")
comps = m.define_all_comparisons(None, None)
errs = m.validate_paths(comps)
print("comparisons", len(comps), "validation errors", len(errs))
import json
sw = comps[0]["condition_a"]["sweep"] / "threshold_sweep.json"
print(comps[0]["name"], sw, json.loads(sw.read_text())["optimal"]["threshold"])

