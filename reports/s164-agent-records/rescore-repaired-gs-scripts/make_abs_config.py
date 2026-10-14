#!/usr/bin/env python3
"""Rewrite a pairwise-comparisons YAML with every path made absolute.

Lets the OLD code tree (a ``git archive`` of scripts/ only) read exactly
the same input files as the NEW clone. Usage:
    python make_abs_config.py <in.yaml> <repo root> <out.yaml>
"""
import sys
from pathlib import Path

import yaml

src, root, dst = Path(sys.argv[1]), Path(sys.argv[2]).resolve(), Path(sys.argv[3])
data = yaml.safe_load(src.read_text(encoding="utf-8"))
keys = ("bounds", "ground_truth", "probabilities_a", "probabilities_b", "manifest_a",
        "manifest_b", "study_dir_a", "study_dir_b", "geojson_a", "geojson_b")
for block in [data.get("defaults", {})] + data["comparisons"]:
    for k in keys:
        if k in block and not Path(block[k]).is_absolute():
            block[k] = str(root / block[k])
dst.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
print(f"{len(data['comparisons'])} comparisons -> {dst}")
