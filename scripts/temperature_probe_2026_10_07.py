#!/usr/bin/env python3
"""Temperature probe, 2026-10-07: does Gemini 3.7 Flash ignore ``temperature``?

Google's notice of 2026-10-07 ("[Action Required] Update thinking_budget and
sampling parameters") states that since Gemini 3.6 Flash "sampling parameters
have been set to default values, so custom values have had no effect on model
output". This script supports a small paired probe of that claim on the
project's own verifier requests (card: ``planning/temperature-probe-2026-10-07.md``).

Design: the same 300 gold-standard candidates are verified three times by each
model on one day through the Batch API — at T 0.0, at T 0.0 again, and at the
model's maximum temperature. If a model honours temperature, its T 0.0 / T max
agreement falls well below its T 0.0 / T 0.0 agreement. Gemini 3 Flash
(``gemini-3-flash-preview``), which predates 3.6, is the positive control.

Subcommands:
    prepare   Build the probe crops directory: a seeded random subset of an
              existing crop manifest, with the crop PNGs copied beside it.
              Offline.
    models    Read each model's default sampling fields with ``models.get``
              (no tokens, no charge; an API call all the same) and save them.
    analyse   Compare the legs' ``probabilities.json`` files: exact agreement,
              chance-corrected agreement, mean |Δp|, decision flips, and a
              paired bootstrap of (T0/T0 agreement − T0/Tmax agreement).
              Offline.
    followup  Gemini 3.7 only: add a third T 0.0 leg and a second T max leg
              (lodged together) and test whether the exploratory mean |Δp|
              residual of the card's § 7 replicates (card § 8). Offline.

Usage (from the repository root on sapphire):
    .venv/bin/python scripts/temperature_probe_2026_10_07.py prepare \\
        --source-crops outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops \\
        --out outputs/temperature-probe-2026-10-07/crops --n 300 --seed 42
    .venv/bin/python scripts/temperature_probe_2026_10_07.py models \\
        --out outputs/temperature-probe-2026-10-07/models-get.json
    .venv/bin/python scripts/temperature_probe_2026_10_07.py analyse \\
        --root outputs/temperature-probe-2026-10-07 \\
        --out outputs/temperature-probe-2026-10-07/analysis.json
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Legs per model: two T 0.0 replicates and one at the model's maximum.
MODELS: dict[str, str] = {
    "g3": "gemini-3-flash-preview",
    "g37": "gemini-3.7-flash",
}
LEGS: tuple[str, ...] = ("t0a", "t0b", "tmax")
# Decision thresholds at which flips are counted: 0.5 plus each verifier's
# carried operating point on the 791-candidate screen (G3 0.10, 3.7 0.80;
# planning/modality-bridge-2026-10-07.md § 2.2).
FLIP_THRESHOLDS: tuple[float, ...] = (0.10, 0.50, 0.80)


def prepare(source_crops: Path, out: Path, n: int, seed: int) -> None:
    """Write a seeded random subset of a crop manifest, copying its crops.

    Args:
        source_crops: Directory holding ``candidate_manifest.json`` and
            ``crops/``.
        out: Destination directory (must not exist yet).
        n: Number of candidates to draw.
        seed: Random seed for the draw.

    Raises:
        FileExistsError: If ``out`` already exists (never overwrite a probe).
        ValueError: If the manifest holds fewer than ``n`` candidates.
    """
    if out.exists():
        raise FileExistsError(f"{out} exists; refusing to overwrite a probe")
    manifest = json.loads((source_crops / "candidate_manifest.json").read_text())
    candidates: list[dict[str, Any]] = manifest["candidates"]
    if len(candidates) < n:
        raise ValueError(f"manifest holds {len(candidates)} candidates, need {n}")

    # Sort by id first so the draw depends on the seed alone, not file order.
    pool = sorted(candidates, key=lambda c: c["candidate_id"])
    chosen = sorted(random.Random(seed).sample(pool, n), key=lambda c: c["candidate_id"])

    (out / "crops").mkdir(parents=True)
    for cand in chosen:
        shutil.copy2(source_crops / cand["crop_file"], out / cand["crop_file"])

    subset = dict(manifest)
    subset["candidates"] = chosen
    subset["total_detections"] = n
    subset["successful_extractions"] = n
    # Recorded so the provenance guard's disagreement is explained in the
    # artefact itself: this manifest is a deliberate subset of its union.
    subset["probe_subset"] = {
        "purpose": "temperature probe 2026-10-07",
        "source_manifest": str(source_crops / "candidate_manifest.json"),
        "n_source": len(candidates),
        "n": n,
        "seed": seed,
        "candidate_ids": [c["candidate_id"] for c in chosen],
    }
    (out / "candidate_manifest.json").write_text(json.dumps(subset, indent=2) + "\n")
    print(f"wrote {n} of {len(candidates)} candidates to {out}")


def models(out: Path) -> None:
    """Save each probe model's default sampling fields from ``models.get``.

    Args:
        out: JSON file to write.
    """
    from google import genai

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from config import GOOGLE_API_KEY  # noqa: E402  (repository-root config)

    client = genai.Client(api_key=GOOGLE_API_KEY)
    record: dict[str, Any] = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "models": {},
    }
    for name in (*MODELS.values(), "gemini-3.8-flash"):
        try:
            m = client.models.get(model=name)
            record["models"][name] = {
                field: getattr(m, field, None)
                for field in (
                    "name", "version", "temperature", "max_temperature",
                    "top_p", "top_k", "thinking", "input_token_limit",
                    "output_token_limit",
                )
            }
        except Exception as exc:  # recorded, not raised: one miss is a finding
            record["models"][name] = {"error": repr(exc)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2, default=str) + "\n")
    print(json.dumps(record, indent=2, default=str))


def _load_probs(path: Path) -> dict[str, float]:
    """Read ``candidate id → mound_probability`` from a probabilities file.

    Args:
        path: A ``probabilities.json`` written by ``run_pv.py verify``.

    Returns:
        Mapping of candidate key to probability (failed items omitted).
    """
    data = json.loads(path.read_text())
    results = data["results"]
    items = results.items() if isinstance(results, dict) else results
    return {
        str(k): float(v["mound_probability"])
        for k, v in items
        if isinstance(v, dict) and v.get("mound_probability") is not None
    }


def _agreement(a: list[float], b: list[float]) -> dict[str, float]:
    """Agreement statistics between two paired probability vectors.

    Exact agreement is compared against the chance rate implied by the two
    marginal distributions of probability values (the project's convention,
    ``results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/
    findings.md``), giving a kappa-style statistic.

    Args:
        a: Probabilities from one leg.
        b: Probabilities from the other leg, same candidate order.

    Returns:
        Dictionary of agreement statistics.
    """
    n = len(a)
    exact = sum(x == y for x, y in zip(a, b)) / n
    values = set(a) | set(b)
    chance = sum((a.count(v) / n) * (b.count(v) / n) for v in values)
    kappa = (exact - chance) / (1 - chance) if chance < 1 else float("nan")
    stats: dict[str, float] = {
        "n": n,
        "exact": exact,
        "chance": chance,
        "kappa": kappa,
        "mean_abs_diff": sum(abs(x - y) for x, y in zip(a, b)) / n,
        "share_abs_diff_gt_0.5": sum(abs(x - y) > 0.5 for x, y in zip(a, b)) / n,
    }
    for t in FLIP_THRESHOLDS:
        stats[f"flips_at_{t:.2f}"] = sum((x >= t) != (y >= t) for x, y in zip(a, b)) / n
    return stats


def _bootstrap_drop(
    t0a: list[float], t0b: list[float], tmax: list[float], reps: int, seed: int,
) -> dict[str, float]:
    """Paired bootstrap of the agreement drop from T0/T0 to T0/Tmax.

    The drop is ``exact(t0a, t0b) − mean(exact(t0a, tmax), exact(t0b, tmax))``,
    resampling candidates with replacement.

    Args:
        t0a: First T 0.0 leg.
        t0b: Second T 0.0 leg.
        tmax: Maximum-temperature leg.
        reps: Bootstrap replicates.
        seed: Random seed.

    Returns:
        Point estimate and percentile 95 % interval of the drop.
    """
    n = len(t0a)
    same = [float(x == y) for x, y in zip(t0a, t0b)]
    cross = [((x == z) + (y == z)) / 2 for x, y, z in zip(t0a, t0b, tmax)]
    point = sum(same) / n - sum(cross) / n
    rng = random.Random(seed)
    draws = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        draws.append(sum(same[i] - cross[i] for i in idx) / n)
    draws.sort()
    return {
        "drop": point,
        "ci_low": draws[int(0.025 * reps)],
        "ci_high": draws[int(0.975 * reps) - 1],
        "reps": reps,
    }


def analyse(root: Path, out: Path, reps: int = 10000, seed: int = 42) -> None:
    """Compare every model's three legs and write the probe's statistics.

    Args:
        root: Probe root holding ``<model>-<leg>/probabilities.json``.
        out: JSON file to write.
        reps: Bootstrap replicates.
        seed: Bootstrap seed.
    """
    record: dict[str, Any] = {"root": str(root), "models": {}}
    for key, model in MODELS.items():
        legs = {leg: _load_probs(root / f"{key}-{leg}" / "probabilities.json") for leg in LEGS}
        common = sorted(set.intersection(*(set(v) for v in legs.values())))
        vec = {leg: [legs[leg][c] for c in common] for leg in LEGS}
        record["models"][model] = {
            "n_per_leg": {leg: len(v) for leg, v in legs.items()},
            "n_common": len(common),
            "mean_probability": {leg: sum(v) / len(v) for leg, v in vec.items()},
            "t0a_vs_t0b": _agreement(vec["t0a"], vec["t0b"]),
            "t0a_vs_tmax": _agreement(vec["t0a"], vec["tmax"]),
            "t0b_vs_tmax": _agreement(vec["t0b"], vec["tmax"]),
            "agreement_drop": _bootstrap_drop(vec["t0a"], vec["t0b"], vec["tmax"], reps, seed),
        }
    out.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


# Follow-up (card § 8): a third T 0.0 leg and a second T max leg for Gemini 3.7,
# lodged together, to test the exploratory mean |Δp| residual of § 7.
FOLLOWUP_T0: tuple[str, ...] = ("t0a", "t0b", "t0c")
FOLLOWUP_TMAX: tuple[str, ...] = ("tmax", "tmax2")


def _abs_diffs(a: list[float], b: list[float]) -> list[float]:
    """Per-candidate absolute probability difference between two legs."""
    return [abs(x - y) for x, y in zip(a, b)]


def _bootstrap_contrast(
    minuend: list[list[float]], subtrahend: list[list[float]], reps: int, seed: int,
) -> dict[str, float]:
    """Paired bootstrap of a difference between two families of leg pairs.

    Each family is a list of per-candidate vectors (one vector per leg pair,
    e.g. |Δp| between T 0.0 and T max). For every candidate the family mean is
    taken first, then the subtrahend's mean is subtracted from the minuend's;
    candidates are resampled with replacement.

    Args:
        minuend: Per-candidate vectors for the pairs expected to differ more.
        subtrahend: Per-candidate vectors for the baseline pairs.
        reps: Bootstrap replicates.
        seed: Random seed.

    Returns:
        Point estimate and percentile 95 % interval of the contrast.
    """
    n = len(minuend[0])
    per_cand = [
        sum(v[i] for v in minuend) / len(minuend)
        - sum(v[i] for v in subtrahend) / len(subtrahend)
        for i in range(n)
    ]
    rng = random.Random(seed)
    draws = sorted(
        sum(per_cand[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)
    )
    return {
        "contrast": sum(per_cand) / n,
        "ci_low": draws[int(0.025 * reps)],
        "ci_high": draws[int(0.975 * reps) - 1],
        "reps": reps,
    }


def _followup_verdict(primary: dict[str, float], pooled: dict[str, float]) -> str:
    """Apply the follow-up decision rule fixed before launch (card § 8.2).

    Args:
        primary: Same-time contrast, |Δp|(t0c, tmax2) − |Δp|(t0a, t0b).
        pooled: All T 0.0 × T max pairs against all T 0.0 × T 0.0 pairs.

    Returns:
        ``"residual effect"``, ``"no residual effect"`` or ``"inconclusive"``.
    """
    def excludes_zero_above(stat: dict[str, float]) -> bool:
        return stat["ci_low"] > 0

    def includes_zero(stat: dict[str, float]) -> bool:
        return stat["ci_low"] <= 0 <= stat["ci_high"]

    if excludes_zero_above(primary) and excludes_zero_above(pooled):
        return "residual effect"
    if includes_zero(primary) and includes_zero(pooled):
        return "no residual effect"
    return "inconclusive"


def followup(root: Path, out: Path, reps: int = 10000, seed: int = 42) -> None:
    """Analyse the Gemini 3.7 follow-up legs against the original three.

    Args:
        root: Probe root holding ``g37-<leg>/probabilities.json`` for the
            legs in ``FOLLOWUP_T0`` and ``FOLLOWUP_TMAX``.
        out: JSON file to write.
        reps: Bootstrap replicates.
        seed: Bootstrap seed.
    """
    names = (*FOLLOWUP_T0, *FOLLOWUP_TMAX)
    legs = {leg: _load_probs(root / f"g37-{leg}" / "probabilities.json") for leg in names}
    common = sorted(set.intersection(*(set(v) for v in legs.values())))
    vec = {leg: [legs[leg][c] for c in common] for leg in names}

    # Every pair's descriptive agreement, so the full matrix is on record.
    pairs = {
        f"{a}_vs_{b}": _agreement(vec[a], vec[b])
        for i, a in enumerate(names) for b in names[i + 1:]
    }
    t0_t0 = [(a, b) for i, a in enumerate(FOLLOWUP_T0) for b in FOLLOWUP_T0[i + 1:]]
    t0_tmax = [(a, b) for a in FOLLOWUP_T0 for b in FOLLOWUP_TMAX]

    def diffs(pair_list: list[tuple[str, str]]) -> list[list[float]]:
        return [_abs_diffs(vec[a], vec[b]) for a, b in pair_list]

    def disagree(pair_list: list[tuple[str, str]]) -> list[list[float]]:
        return [[float(x != y) for x, y in zip(vec[a], vec[b])] for a, b in pair_list]

    primary = _bootstrap_contrast(diffs([("t0c", "tmax2")]), diffs([("t0a", "t0b")]), reps, seed)
    pooled = _bootstrap_contrast(diffs(t0_tmax), diffs(t0_t0), reps, seed)
    record: dict[str, Any] = {
        "root": str(root),
        "model": MODELS["g37"],
        "n_per_leg": {leg: len(v) for leg, v in legs.items()},
        "n_common": len(common),
        "pairs": pairs,
        "primary_mad_contrast_same_time": primary,
        "pooled_mad_contrast": pooled,
        "pooled_disagreement_contrast": _bootstrap_contrast(
            disagree(t0_tmax), disagree(t0_t0), reps, seed,
        ),
        "tmax_vs_tmax2_minus_t0_pairs_mad": _bootstrap_contrast(
            diffs([("tmax", "tmax2")]), diffs(t0_t0), reps, seed,
        ),
        "verdict": _followup_verdict(primary, pooled),
    }
    out.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


def main() -> None:
    """Parse arguments and dispatch the subcommand."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--source-crops", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--n", type=int, default=300)
    p.add_argument("--seed", type=int, default=42)
    m = sub.add_parser("models")
    m.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("analyse")
    a.add_argument("--root", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    a.add_argument("--reps", type=int, default=10000)
    f = sub.add_parser("followup")
    f.add_argument("--root", type=Path, required=True)
    f.add_argument("--out", type=Path, required=True)
    f.add_argument("--reps", type=int, default=10000)
    args = parser.parse_args()

    if args.cmd == "prepare":
        prepare(args.source_crops, args.out, args.n, args.seed)
    elif args.cmd == "models":
        models(args.out)
    elif args.cmd == "followup":
        followup(args.root, args.out, args.reps)
    else:
        analyse(args.root, args.out, args.reps)


if __name__ == "__main__":
    main()
