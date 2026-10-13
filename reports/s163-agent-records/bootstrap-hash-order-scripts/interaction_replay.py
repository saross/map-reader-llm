#!/usr/bin/env python3
"""
Replay the thinking x temperature interaction test of the secondary-effects
scripts (ruling D63).

``analyse_secondary_effects.py`` (image) and ``analyse_secondary_effects_text.py``
(text) each run a dozen analyses; only "Analysis 8"
(``analyse_thinking_temp_interaction``) calls ``bootstrap_interaction_ci``,
whose tile order followed the string-hash seed. This replay runs exactly the
steps ``main()`` runs for that analysis — load the references and bounds,
pick each condition's optimal consensus threshold, then call
``analyse_thinking_temp_interaction`` with the default seed — and writes its
result as JSON. Run it with the working directory and ``PYTHONPATH`` set to
the code tree under test (``script_replay.py`` does both).

Usage::

    python interaction_replay.py --module analyse_secondary_effects --out out/image.json
    python interaction_replay.py --module analyse_secondary_effects_text --out out/text.json
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path


def _plain(obj):
    """Make numpy scalars and tuple keys JSON-serialisable, exactly."""
    import numpy as np

    if isinstance(obj, dict):
        return {str(k): _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    if isinstance(obj, np.generic):
        return obj.item()
    return obj


def main() -> int:
    """Run Analysis 8 of the named module and write its JSON."""
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--module", required=True,
                   choices=["analyse_secondary_effects", "analyse_secondary_effects_text"])
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    tree = Path.cwd()
    sys.path.insert(0, str(tree / "scripts"))
    mod = importlib.import_module(args.module)
    assert Path(mod.PROJECT_ROOT).resolve() == tree.resolve(), mod.PROJECT_ROOT

    gdf_ref = mod.load_geojson(mod.DEFAULT_GT)
    gdf_bounds = mod.load_geojson(mod.DEFAULT_BOUNDS)
    conditions = mod.CONDITION_REGISTRY
    optimal = {}
    for cid, cfg in conditions.items():
        t, _f1 = mod.find_optimal_threshold(mod.PROJECT_ROOT / cfg["consensus_dir"],
                                            gdf_ref, gdf_bounds)
        optimal[cid] = t
    result = mod.analyse_thinking_temp_interaction(
        conditions, optimal, gdf_ref, gdf_bounds, seed=mod.DEFAULT_SEED)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(_plain({"optimal_thresholds": optimal, **result}),
                                   indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
