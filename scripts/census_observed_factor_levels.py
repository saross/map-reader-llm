#!/usr/bin/env python3
"""Census the factor levels actually executed, from run-conditions.json.

First half of the Phase 1 execution→errata inverse census
(audit-charter § 7 Phase 1): every factor level observed in the
decomposition either is licensed by the registration (a commitment) or
by an erratum, or it is flagged UNLICENSED. This script produces the
*observed* side deterministically; licence matching is a separate step
that consumes its output together with ``results/commitments.json`` and
the errata licence register.

Factors surveyed per condition: ``architecture``, ``aggregation``,
``proposer_pool`` (raw slug plus its declared modality),
``n_passes``, ``vote_threshold``, ``prob_threshold``, and the verifier
configuration fields (``variant``, ``instruction_file``, ``model``,
``thinking_level``, ``temperature``) prefixed ``verifier_*``. The study
family slug itself is recorded as factor ``family``.

Output: JSON mapping ``"<factor>=<level>"`` to the sorted list of
``"<family>/<condition-label>"`` sites carrying it, plus per-factor
level inventories. Deterministic: sorted keys, stable ordering.

Usage::

    python3 scripts/census_observed_factor_levels.py \
        [--run-conditions results/run-conditions.json] \
        [--out reports/verification/c2-census/observed-factor-levels.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RC = REPO_ROOT / "results" / "run-conditions.json"
DEFAULT_OUT = (
    REPO_ROOT / "reports" / "verification" / "c2-census"
    / "observed-factor-levels.json"
)

#: Condition-row fields treated as factors directly.
CONDITION_FACTORS = (
    "architecture",
    "aggregation",
    "proposer_pool",
    "n_passes",
    "vote_threshold",
    "prob_threshold",
)

#: Verifier-config fields, emitted with a ``verifier_`` prefix.
VERIFIER_FACTORS = (
    "variant",
    "instruction_file",
    "model",
    "thinking_level",
    "temperature",
)


def level_repr(value: object) -> str:
    """Render a factor level as a stable string key (None -> 'null')."""
    return "null" if value is None else str(value)


def census(run_conditions: dict) -> dict:
    """Walk the decomposition and collect observed factor levels.

    Args:
        run_conditions: parsed ``results/run-conditions.json``.

    Returns:
        Dict with ``observed`` (factor=level -> sites),
        ``factor_levels`` (factor -> sorted level list), and counters.
    """
    observed: dict[str, list[str]] = defaultdict(list)
    n_conditions = 0

    decomposition = run_conditions["decomposition"]
    for family, fam in sorted(decomposition.items()):
        pool_modalities = fam.get("proposer_pools", {})
        for cond in fam.get("conditions", []):
            n_conditions += 1
            site = f"{family}/{cond.get('label', '?')}"
            observed[f"family={family}"].append(site)
            for factor in CONDITION_FACTORS:
                observed[f"{factor}={level_repr(cond.get(factor))}"].append(site)
            pool = cond.get("proposer_pool")
            if pool is not None and pool in pool_modalities:
                # Pool declarations are either a bare modality string or a
                # {"modality": ..., "path": ...} object; census the modality.
                decl = pool_modalities[pool]
                modality = decl.get("modality") if isinstance(decl, dict) else decl
                observed[f"proposer_modality={level_repr(modality)}"].append(site)
            vc = cond.get("verifier_config")
            if vc is not None:
                for factor in VERIFIER_FACTORS:
                    observed[
                        f"verifier_{factor}={level_repr(vc.get(factor))}"
                    ].append(site)

    factor_levels: dict[str, list[str]] = defaultdict(list)
    for key in observed:
        factor, level = key.split("=", 1)
        factor_levels[factor].append(level)

    return {
        "n_families": len(decomposition),
        "n_conditions": n_conditions,
        "n_distinct_factor_levels": len(observed),
        "factor_levels": {f: sorted(set(ls)) for f, ls in sorted(factor_levels.items())},
        "observed": {k: sorted(v) for k, v in sorted(observed.items())},
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: run the census and write the JSON output."""
    parser = argparse.ArgumentParser(
        description="Census observed factor levels from run-conditions.json."
    )
    parser.add_argument("--run-conditions", type=Path, default=DEFAULT_RC)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    with args.run_conditions.open(encoding="utf-8") as fh:
        run_conditions = json.load(fh)

    result = census(run_conditions)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")

    print(
        f"OK {result['n_families']} families, {result['n_conditions']} conditions, "
        f"{result['n_distinct_factor_levels']} distinct factor=level pairs "
        f"-> {args.out.relative_to(REPO_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
