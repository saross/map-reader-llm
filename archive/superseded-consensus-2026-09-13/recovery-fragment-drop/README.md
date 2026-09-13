# Superseded consensus unions — the recovery-fragment drop (2026-09-13)

> **Last revised**: 2026-09-13 (original publication).
> See [§ Changelog](#changelog) for revision history.

These are the **pre-fix** copies of every committed `merge_passes.py` consensus
union that the recovery-fragment drop touched. They are preserved here, browsable
in the working tree, because the active paths under `outputs/` were rebuilt in
place with the fixed builder. Nothing here is live; nothing here should be read
by an analysis.

## The defect

`scripts/merge_passes.py`'s `resolve_pass_files` derived a pass directory's
number by stripping the `run_`/`pass_` prefix and casting the remainder to `int`.
`int("2_recovery")` raises `ValueError`, and the `except ValueError: continue`
swallowed it **silently**, so a storm-recovery fragment directory
(`run_<N>_recovery`, `run_<N>_recovery2`) never reached the loader. Two
consequences:

1. The fragment's detections never entered the union.
2. `total_passes` was computed as `len(raw_passes)` over the loader's output, so
   a pass whose *main* file held an empty FeatureCollection vanished entirely
   and every vote threshold was divided by the wrong denominator.

Full measurement, enumeration of all 28 committed unions in recovery-bearing
pools, and the classification (0 MATERIAL, 5 NEGLIGIBLE, 23 UNAFFECTED):
`reports/recovery-fragment-drop-2026-09-13.md`.

## The fix

Commit **`75d7c8d4cd55b6ec8d2a40abff70a31f62b67725`** — *"fix(merge_passes): fold
run_N_recovery fragments into their pass"* (2026-09-13). It groups pass
directories by the number matched from
`^(?:pass|run)_(?P<num>\d+)(?P<suffix>.*)$` (`scripts/merge_passes.py:413`),
appends each fragment's files **after** the main directory's so within-pass
deduplication still prefers the main feature, keeps the main directory's name as
the pass id, and leaves the pass **count** unchanged — a fragment joins an
existing pass and never creates one.

The rebuild that superseded these files, the four verifier calls it required, and
the four cell re-scores are reported in
`reports/recovery-drop-fix-2026-09-13.md`.

## What is archived here

The PI's ruling names **five** defective files. The complete pre-fix contents of
each affected `consensus-n*` directory are archived, because `merge_passes.py
--sweep` rewrites *every* `consensus_t*.geojson` in its output directory — so the
unaffected thresholds were overwritten too, and preserving only the five would
have left the rest unrecoverable from the working tree.

| archived path | features | defective? |
|---|---:|---|
| `gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n1/consensus_t1.geojson` | 640 | **yes** — count held at 640, one candidate swapped |
| `gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n3/consensus_t1.geojson` | 757 | **yes** — rebuilds to 759 |
| `gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n3/consensus_t2.geojson` | 608 | **yes** — rebuilds to 609 |
| `gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n3/consensus_t3.geojson` | 529 | **yes** — rebuilds to 530 |
| `grid-2026-08-18__g384_ov192/consensus-n5/consensus_t5.geojson` | 1,168 | **yes** — rebuilds to 1,169 |
| `grid-2026-08-18__g384_ov192/consensus-n5/consensus_t{1,2,3,4}.geojson` | 2,932 / 2,025 / 1,650 / 1,396 | no — unchanged in count *and* membership; archived because the sweep rewrote them |
| each directory's `voting_summary.json` | — | its `pass_provenance` block lists only the **main** pass files, with no recovery fragment |

All five defective files are NEGLIGIBLE on the report's classification (< 0.5 % of
features; largest delta +2 on 757, +0.264 %). No MATERIAL union exists anywhere
in the repository.

`experiment_intent.md` is not archived: `merge_passes.py` does not write it (its
wrapper scripts `build_k_ladder_phase2_unions.py` and `run_k_ladder_tier_e.py`
do), so the committed copies were not touched by the rebuild.

## SHA-256 of the archived bytes

```text
c7e0fdb5866b886186f15800054409745c54c836b5f7642a1a3425c8029f8775  gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n1/consensus_t1.geojson
ffa29b9b5b8e2b5e25748ce811ef5868900fd3db28aba52fae3b8e6d649fb816  gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n1/voting_summary.json
adeda297c92a2a58fe1daae10cb3dd936f1974247a6a078381923f467c86d4d0  gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n3/consensus_t1.geojson
e6674eb8e87ffb7efb49bad075d953bdaffa924d49a2af91a39f1dfa1f01d4df  gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n3/consensus_t2.geojson
72294e5adf2712968ab23fc0ef92f51c5621050508e7bb415cf49f018ee142dd  gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n3/consensus_t3.geojson
404f987fb2c321b46d38a98e2ebed492fb168217b76bf55420de89bb544e6db0  gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n3/voting_summary.json
7401f2bd97f13353d17a2c15158d9e3e507b3c060c7e720879d1bb574499b538  grid-2026-08-18__g384_ov192/consensus-n5/consensus_t1.geojson
c228662574a9c76d9ba80f3c5e9aef576e91d8135650d306be4f6ace33266195  grid-2026-08-18__g384_ov192/consensus-n5/consensus_t2.geojson
ee9e3012c4ddb3f1e389fd527929f0c116bbb9a7feb360506572ee9b5f4dc0d3  grid-2026-08-18__g384_ov192/consensus-n5/consensus_t3.geojson
1d70bc45c6ff3cfdec0649902f3a0d5e89b981523e6a0153c24605691bf35b78  grid-2026-08-18__g384_ov192/consensus-n5/consensus_t4.geojson
f8367b44be0b56f228de76d0773bf4fac5886f3533d3c8f20b40ecb12061c8df  grid-2026-08-18__g384_ov192/consensus-n5/consensus_t5.geojson
26d30e6a494dd123c7d83359adc6d1caf739668c2f96d07461c8baa5949ef072  grid-2026-08-18__g384_ov192/consensus-n5/voting_summary.json
```

## Where the live files now are

| archived directory | live directory |
|---|---|
| `gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n1/` | `outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n1/` |
| `gemini37-screen-2026-08-28__g384_ov192_g37/consensus-n3/` | `outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n3/` |
| `grid-2026-08-18__g384_ov192/consensus-n5/` | `outputs/grid-2026-08-18/g384_ov192/consensus-n5/` |

## Changelog

### 2026-09-13 — Original publication

Archived the pre-fix copies of the three affected `consensus-n*` directories
ahead of the rebuild ordered by the PI's "fix properly" ruling of 2026-09-13.
Twelve files: the five defective unions the ruling names, the four unaffected
`grid` thresholds the `--sweep` rebuild would otherwise have overwritten without
trace, and the three `voting_summary.json` files whose `pass_provenance` blocks
predate fragment folding. SHA-256 recorded for every archived byte stream.
