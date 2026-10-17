#!/usr/bin/env python3
"""POST HOC (not in the pre-specified plan): the temperature x thinking interaction.

Added after the pre-specified analysis showed, in image only, a thinking
contrast at T 0.0 that reaches 0.03 and rejects (plan P11's declared
surprise). The question it answers is descriptive: does the temperature
effect differ between the two thinking levels, i.e. is the image 2 x 2 an
interaction rather than two main effects? Statistic: (F1(HIGH, T 0.0) -
F1(HIGH, T 0.7)) - (F1(MEDIUM, T 0.0) - F1(MEDIUM, T 0.7)) on the
pass-averaged per-tile counts A-06 uses; p from the library's paired
interaction permutation test (10,000, seed 42); interval from a paired
tile bootstrap of the same statistic (B = 1,000, seed 42, the A-06
convention). No BH family; it decides nothing in the record.

Usage (reads a run directory written by d64_a06_replication.py)::

    python posthoc_interaction.py <run_dir>

Writes ``<run_dir>/posthoc_interaction.json``.

Author: Shawn Ross & Claude (Anthropic), Session 164, 2026-10-14
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from e45_bootstrap_pairings import micro_f1  # noqa: E402
from lib_permutation import paired_interaction_permutation  # noqa: E402

B, SEED = 1_000, 42


def pass_mean(stack: np.ndarray) -> np.ndarray:
    """Per-tile mean over passes (sequential sum, one division)."""
    total = np.zeros(stack.shape[1:], dtype=float)
    for k in range(stack.shape[0]):
        total += stack[k]
    return total / stack.shape[0]


def f1_of(arm: np.ndarray, take: np.ndarray | None = None) -> float:
    """Micro-F1 of an arm's (3, n_tiles) counts, optionally resampled."""
    a = arm if take is None else arm[:, take]
    return micro_f1(float(a[0].sum()), float(a[1].sum()), float(a[2].sum()))


def main() -> int:
    """Compute the interaction per modality and write the JSON."""
    run_dir = Path(sys.argv[1])
    data = np.load(run_dir / "d64_per_pass_counts.npz")
    out = {"_README": __doc__.split("\n\n")[0] + " See the module docstring."}
    for modality in ("text", "image"):
        arms = [pass_mean(data[f"{modality}-{t}"]) for t in
                ("high-t0.0", "high-t0.7", "medium-t0.0", "medium-t0.7")]
        perm = paired_interaction_permutation(
            *({"tp": x[0], "fp": x[1], "fn": x[2]} for x in arms))
        n = arms[0].shape[1]
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, n, size=(B, n))
        draws = np.empty(B)
        for i in range(B):
            f = [f1_of(x, idx[i]) for x in arms]
            draws[i] = (f[0] - f[1]) - (f[2] - f[3])
        f = [f1_of(x) for x in arms]
        out[modality] = {
            "T_effect_at_HIGH": round(f[0] - f[1], 6),
            "T_effect_at_MEDIUM": round(f[2] - f[3], 6),
            "interaction (HIGH minus MEDIUM T effect)": round(perm["observed"], 6),
            "ci95_paired_bootstrap": {
                "lower": round(float(np.percentile(draws, 2.5)), 6),
                "upper": round(float(np.percentile(draws, 97.5)), 6)},
            "p_interaction_permutation": perm["p_value"],
            "n_tiles": n, "n_permutations": perm["n_permutations"], "seed": SEED,
        }
    (run_dir / "posthoc_interaction.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
