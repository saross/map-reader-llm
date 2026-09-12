# Experiment intent — K-ladder Phase 2, rung 11 of 28

> **Last revised**: 2026-09-12 (original publication — K-ladder Phase 2 step 1,
> the US$0 union build). Controlling card:
> `planning/k-ladder-review-2026-09-11.md`; costing
> `reports/k-ladder-phase2-costing-2026-09-12.md` section 3, row
> 11. See [section Changelog](#changelog).

## What this directory is

The **first-N consensus union** for one rung of the K-ladder review's
Phase 2 gap-fill: family *Gemini 3 HIGH text 384 px, T 1.0* at **K = 1**.
It is the candidate universe a single Gemini 3 verifier pass is then run over
(ruling R1: the carried verifier at every rung, no swaps).

## The pass list, recorded explicitly

`pass_provenance` is not yet on `main` (PR #14 is unmerged), so the pass list
is recorded here by hand rather than read back from a property of the
consensus file:

| field | value |
|---|---|
| proposer pool | `outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0` |
| passes included | `run_1` |
| K (number of passes) | 1 |
| `merge_passes.py --passes` | `1` |
| first-N rule | passes 1..1, in run order, no selection |
| register run | `pv-diag-384` |
| register proposer-pool slug | `flash-high-text-n5-text-t1.0` |
| planned verifier stage | `flash-high-text-n5-text-t1.0-verified-v1-n1` |
| costing tier | B |

## How it was built

`scripts/build_k_ladder_phase2_unions.py` drove the canonical consensus chain
verbatim:

```bash
python scripts/merge_passes.py \
    --input-dir outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0 \
    --output-dir outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0/consensus-n1 \
    --sweep \
    --passes 1
```

`merge_passes.py` deduplicates within each pass at 20 m, clusters across
passes at 20 m, and writes one file per vote threshold. `consensus_t1.geojson`
is the union (vote >= 1) and is the verifier's input; the higher thresholds are
materialised so the vote axis of the operating-point sweep needs no rebuild.

Note that `run_*_recovery` directories are **not** passes:
`merge_passes.load_pass_detections` parses the integer after `run_`, and
`"1_recovery"` does not parse, so those directories are skipped
(`scripts/merge_passes.py:400-411`).

## Count check

1495 candidates at vote >= 1 (costing table: 1495; delta +0)

The union size was measured independently during Phase 1 by
`scripts/probe_first_n_union_sizes.py` (a key of
`results/k-ladder-2026-09-12/first-n-union-sizes.json`) and is what the costing
table priced. A disagreement of more than 2 % is a STOP for the rung: it is
not verified, and the mismatch is reported instead.

## No API call built this directory

Consensus building is local computation. The verifier pass over this union is
the API spend, and it is approved only under the Phase 2 gate: model
`gemini-3-flash` (resolved `gemini-3-flash-preview`), config
`prompts/configs/verify_adversarial-text.json`, T = 0.0, MINIMAL thinking,
n = 1, real-time flex tier.

## Changelog

### 2026-09-12 — Original publication

Written by `scripts/build_k_ladder_phase2_unions.py` as it built the union.
Sources: `results/k-ladder-2026-09-12/first-n-union-sizes.json` (the pool
directory, the pass ids and the expected candidate count) and
`reports/k-ladder-phase2-costing-2026-09-12.md` sections 3 and 5 (the row
number and the tier).
