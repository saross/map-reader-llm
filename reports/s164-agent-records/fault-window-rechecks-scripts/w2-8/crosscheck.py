#!/usr/bin/env python3
"""W2-8 cross-checks on the regenerated E70 bootstrap-interval store.

1. Byte test: copy the committed ``recomputed_at`` and ``elapsed_seconds``
   into the regenerated store, serialise as ``write_store`` does
   (``json.dumps(indent=2)``, no trailing newline) and compare bytes with the
   committed blob.
2. Re-derive the figures ``results/ci-metadata-registry.md`` and the commit
   body of ``8c89ccebb`` quote: entries re-run, run families, the largest
   family, median and maximum |ΔF1 mean|, the count below 0.005, and how
   many fell and rose.

Usage: w2_8_crosscheck.py <repo> <regenerated store>
"""

from __future__ import annotations

import json
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path

GEN = "8c89ccebb"
PATH = "results/all-bootstrap-cis.json"


def main() -> int:
    """Run both checks and print a JSON summary."""
    repo, regenerated = Path(sys.argv[1]), Path(sys.argv[2])
    blob = subprocess.run(["git", "-C", str(repo), "show", f"{GEN}:{PATH}"],
                          capture_output=True, check=True).stdout
    committed = json.loads(blob)
    regen = json.loads(regenerated.read_text(encoding="utf-8"))
    for key, entry in regen["results"].items():
        for field in ("recomputed_at", "elapsed_seconds"):
            if field in entry:
                entry[field] = committed["results"][key][field]
    substituted_equal = json.dumps(regen, indent=2).encode() == blob

    rerun = {k: e for k, e in regen["results"].items() if "pre_e70" in e}
    deltas = {k: e["f1"]["mean"] - e["pre_e70"]["f1_mean"] for k, e in rerun.items()}
    # Run family = phase/track, the grouping the registry changelog uses.
    families = Counter("/".join(k.split(":", 1)[1].split("/")[:2]) for k in rerun)
    worst = max(deltas, key=lambda k: abs(deltas[k]))
    summary = {
        "bytes_equal_after_substituting_two_fields": substituted_equal,
        "entries_rerun": len(rerun),
        "run_families": len(families),
        "largest_family": families.most_common(1)[0],
        "median_abs_delta_f1_mean": round(statistics.median(abs(d) for d in deltas.values()), 6),
        "max_abs_delta": {"key": worst, "delta": round(deltas[worst], 6),
                          "n_before": rerun[worst]["pre_e70"]["n_detections"],
                          "n_after": rerun[worst]["n_detections"]},
        "below_0_005": sum(abs(d) < 0.005 for d in deltas.values()),
        "fell": sum(d < 0 for d in deltas.values()),
        "rose": sum(d > 0 for d in deltas.values()),
        "rerun_note": regen.get("_rerun", {}).get("reran_entries"),
    }
    print(json.dumps(summary, indent=2))
    return 0 if substituted_equal else 1


if __name__ == "__main__":
    sys.exit(main())
