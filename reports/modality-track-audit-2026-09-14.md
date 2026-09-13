# The modality-track audit: what the corpus records against what the model was sent

> **Last revised**: 2026-09-14 (original publication). See [§ Changelog](#changelog) for revision history.

Modality — few-shot exemplars transmitted as **images** against **text labels
only** — is a preregistered factor (H1, confirmatory, "modality and elaboration
level"). On 2026-09-13 the null-exemplar sensitivity job
(`results/null-exemplar-sensitivity-2026-09-13/findings.md`, § "The cells")
reported that **seven Era-2 board cells carry a `track` field that disagrees
with what their proposer actually transmitted**. The PI ruled on 2026-09-14:
characterise corpus-wide before correcting anything.

**The short answer, in five parts.**

1. **The mechanism is a substring test on the condition label**, and it fails in
   two distinct ways: a label may name the **verifier's** modality over a text
   proposer, and a label carrying **no** modality token at all falls through to
   `"text"`.
2. **Corpus-wide the error is small and confined.** Of 593 registered
   conditions, 591 are derivable and 547 from a transmitted configuration; no
   derivation route contradicts another. **Eight conditions and one proposer
   pool** carry a wrong recorded label, across **four artefacts**. The register
   itself (459 checkable entries), the passes manifest (447), the opmax
   membership (86) and the uplift supplement (357 + 357) are **clean**.
3. **Nothing preregistered moves.** H1's confirmatory contrast
   (`h1-cmt0106-pooled-modality`) groups the five phase-2a conditions, every one
   correctly labelled; the confirmatory family takes one *p* per hypothesis and
   none of them is recomputed. **No hypothesis-outcome row changes.**
4. **Two registered analysis outcomes quote a figure that moves**, both
   unsigned but both carrying a verification stamp:
   `era1-single-pass-baseline-matrix`'s "image cells span 0.094-0.291" and
   `tile-size-sweep`'s 512 px single-pass ceiling. Neither is amended here.
   The erratum draft is § 7.
5. **A larger, separate finding for the PI**: the register's
   `verifier_passes[...].modality` field is **ambiguous, not merely wrong** —
   it records the verifier's own exemplar modality in some runs and the track
   the pass belongs to in others, and one family is split across both
   conventions inside a single run (§ 6).

Everything below is derived by `scripts/derive_condition_modality.py` and
`scripts/compare_modality_recomputation.py`, run on sapphire; artefacts under
`results/modality-track-audit-2026-09-14/`. **US$0** — no cell was re-scored.
The cells' metrics are right; only their group membership moves.

## 1. The mechanism

The detection pipeline reads `include_example_images` from the proposer config.
When it is false it prints "Text-only modality: skipping example images" and
transmits no example pixels (`scripts/4_detect_mounds_batch.py:901`); when true
it attaches one `types.Part.from_bytes` per existing example image. The key
**defaults to true** (`:885`), so a config without it sent the images. The map
tile under test is always sent as an image — it is a vision task — so modality
is a property of the *exemplar library*, not of the tile. A condition is
therefore **image** when at least one of its proposer passes ran a configuration
with `include_example_images` true over a non-empty `examples` list, and **text**
otherwise.

`scripts/build_gs_era2_board.py` assigned, at what was line 307:

```python
"track": "image" if "image" in label else "text",
```

Two failure shapes follow, and **both occur on the board**:

| shape | example | what the label says | what was sent |
|---|---|---|---|
| the token names the **verifier** | `proposer-verifier-384::verified-brief-image` | image | proposer `detect_brief-text`, `include_example_images: false` — **text** |
| **no token**, so the test defaults | `pv-diag-384::pv-scale4-optimal-n1-opmax` | text (by fall-through) | proposer `detect_h8_scale-4_v2`, instruction `detect_brief-text-image.md`, `include_example_images: true`, 13 exemplars — **image** |

Three further scripts carried the same class of rule, found by this audit:
`scripts/characterise_gs_plateau.py` (`label + proposer_pool`, image checked
first, so the verifier token wins), `scripts/tile_size_sweep.py` (the same, with
a `"text"` fall-through), and
`scripts/register_k_ladder_phase2_conditions.py` (`"image" if "image" in
pool_slug else "text"`). A hand-authored constant in
`scripts/build_k_ladder_phase2_unions.py` recorded the scale-4 pool as `text`
while the sibling table in `scripts/build_k_ladder_phase2_tables.py` had it right
as `text+image`.

## 2. Derivation: how the ground truth was established

Five routes, three of which read the bytes that were sent; every route that can
speak is recorded, so a disagreement is visible rather than silently resolved.

| route | source | conditions decided |
|---|---|---:|
| `pass-metadata` | the `provenance.source_files` of every matching pass in `results/passes-manifest.json` | 447 |
| `run-metadata` | every `*.meta.json` under the proposer pool's output directory | 56 |
| `config-file` | `prompts/configs/<pool>.json` or `detect_<pool>.json` | 44 |
| `register` (assertion) | `run-conditions.json` `proposer_pools[...].modality` | 2 |
| `pool-name-token` (assertion) | an `image`/`text` token in the pool key | 42 |
| undeterminable | — | 2 |

**547 of 593 conditions rest on a transmitted configuration**, and **zero
conditions have two routes that disagree**. The 42 resting on a pool-name token
and the 2 undeterminable are disclosed in
`results/modality-track-audit-2026-09-14/derived-modality.csv`
(`from_transmitted_configuration`, `derivation_basis`).

`text+image` is treated as a **refinement** of image, not a third level: a
config that narrates the exemplars and also sends their pixels is image-bearing
under the binary preregistered factor.

## 3. The corpus-wide mismatch table

Every field in the corpus that records a per-condition or per-pool modality,
checked against the derivation. Counts from
`results/modality-track-audit-2026-09-14/artefact-summary.json`.

| artefact | field | records carrying a modality | checkable | **mismatched** |
|---|---|---:|---:|---:|
| `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/membership.json` | `track` | 110 | 110 | **7** |
| `results/working-precision/gs-plateau-characterisation.json` | `modality` | 263 | 263 | **3** |
| `results/tile-size-sweep/tile_size_sweep.json` | `modality` | 16 | 16 | **1** |
| `results/k-ladder-2026-09-12/phase2/unions.json` | `modality` | 14 pools | 14 | **1** |
| `results/run-conditions.json` | `proposer_pools[].modality` | 459 | 459 | 0 |
| `results/passes-manifest.json` | `passes[].modality` | 447 | 447 | 0 |
| `.../gs-era2-verified-board-2026-09-10/opmax/membership.json` | `track` + `modality` | 86 | 86 | 0 |
| `results/uplift-supplement/conditions.csv` | `modality` | 357 | 357 | 0 |
| `results/uplift-supplement/conditions-by-buffer.csv` | `modality` | 357 | 357 | 0 |
| `results/k-ladder-2026-09-12/phase2/ladders.json` | `modality` | 14 | 14 | 0 |
| `results/k-ladder-2026-09-12/tier-e/unions.json` | `modality` | 1 | 1 | 0 |

**Eight distinct conditions and one pool** are affected:

| condition / pool | recorded | derived | artefact | mechanism |
|---|---|---|---|---|
| `proposer-verifier-384::verified-adversarial-image` | image | **text** | board `membership.json`; plateau | the label's token names the image **verifier** over a `detect_brief-text` proposer |
| `proposer-verifier-384::verified-brief-image` | image | **text** | board `membership.json`; plateau | as above |
| `proposer-verifier-384::verified-checklist-image` | image | **text** | board `membership.json`; plateau | as above |
| `pv-diag-384::pv-scale4-optimal-n1-opmax` | text | **image** | board `membership.json` | no modality token in the label; the substring test fell through to `"text"` |
| `pv-diag-384::pv-scale4-optimal-n1-carried-p0.15-k1` | text | **image** | board `membership.json` | as above |
| `pv-diag-384::pv-scale4-optimal-n3-opmax` | text | **image** | board `membership.json` | as above |
| `pv-diag-384::pv-scale4-optimal-n3-carried-p0.15-k3` | text | **image** | board `membership.json` | as above |
| `retest-phase2e::canonical-last` | text | **image** | `tile_size_sweep.json` | pool `canonical-last` carries neither token; fell through to `"text"` |
| pool `pv-diag-384::scale-4-optimal-487` | text | **image** | `k-ladder .../phase2/unions.json` | hand-authored constant; the sibling family table had `text+image` |

Two of the four `pv-scale4-optimal` board cells sit in the new tile-MCC Tier 1,
as the sensitivity job reported.

**Checked and clean beyond the table.** Six further label-keyed artefacts were
hand-checked against the same derivation and carry the correct value:
`.../g1-confirmatory-rebuild-tiers_20m.json` (44 conditions; records
`pv-scale4-optimal-n5`/`n10` as **image**, correctly),
`.../opmax/staleness-2026-09-11/vintage-survey.json` (30 cells, same),
`results/diversity-dividend-384/tiering-{champions,with-deployable}/tiering_20m.json`,
`results/wbf-greedy-comparison/wbf_vs_greedy_full_20m.json` (18),
`results/proposer-vote-fraction/vote_fraction.json` (16),
`results/k-ladder-2026-09-12/tension/effect-sizes.json` (9). The
`results/verifier-calibration-matrix-pairwise/{text,image}/` boards carry `track`
as the matrix *leg's own name*, correct by construction.
`results/metric-leaderboards/*.json` carry one top-level `track` naming the
leaderboard, not a per-cell label.

**The three Era-1 boards, the 55-map boards and the metric leaderboards carry no
per-cell modality field at all** — their tiering artefacts have zero `track` /
`modality` occurrences — so there is nothing on them to be wrong. This is why
the error is confined to four artefacts despite the rule appearing in four
scripts.

## 4. The reach, classified

Every analysis row in `results/run-analyses.json` (68 rows) and in the board's
own `tiering-input/run-analyses.json` (67) whose `conditions_compared` holds an
affected cell. **Five UNAFFECTED, two LABEL-ONLY, two NUMBER-AT-RISK**, plus one
unregistered tabulation that is NUMBER-AT-RISK.

| analysis | H | prereg | signature | affected | verdict | why |
|---|---|---|---|---:|---|---|
| `h1-cmt0106-pooled-modality` | H1 | confirmatory-with-deviation | — | 0 | **UNAFFECTED** | groups the five phase-2a conditions; `brief-text-image` and `verbose-text-image` are in the image group, which is correct |
| `family-bh-fdr-confirmatory` | H1–H8 | confirmatory-with-deviation | — | 1 (+1 sibling) | **UNAFFECTED** | takes one *p* per hypothesis; H1's comes from the row above, and the phase-2e cells enter as H4's **ordering** contrast, where modality is constant across all four |
| `era1-leaderboard` | H1–H9 | post-hoc | — | 1 (+3) | **UNAFFECTED** | its tiering artefact carries no modality field, and the outcome's modality sentences name only correctly-labelled cells |
| `uplift-supplement-flatten` | — | post-hoc | **signed 2026-09-10** | 4 | **UNAFFECTED** | the `modality` column is **blank** for the three trio rows (among its 82 blanks) and correct for `canonical-last`; 0 of 357 populated rows mismatch |
| `verifier-uplift-pairing` | H2 | post-hoc | **signed 2026-09-12** | 3 | **UNAFFECTED** | `verifier-uplift.csv` has no modality column; strata are corpus × reference × buffer × frame |
| `gs-era2-verified-board-2026-09-10` | H2, H1 | post-hoc | **signed 2026-09-12** | 7 | **LABEL-ONLY** | `tiering_20m.json` has **zero** `track`/`modality` occurrences; `era1_leaderboard_tiering.py` and `selection_aware_intervals.py` never read `track`; no rendered board table has a track column. The F1 tiering, BH-FDR, both Hsu MCB sets and the tile-MCC family are per-cell and never grouped by modality |
| `k-ladder-2026-09-12` | H3, H13 | post-hoc | **signed 2026-09-13** | 4 (+pool) | **LABEL-ONLY** | the findings treat the scale-4 family **by name** throughout and never place it in a text or image track; the by-track statements (§ 7.1's "both HIGH tracks") name the six HIGH text/image families and exclude it. `ladders.json` (`text+image`) and `tension/effect-sizes.json` are right |
| `null-exemplar-sensitivity-2026-09-13` | — | post-hoc | UNSIGNED | 5 (+8) | **UNAFFECTED** | it derived exposure from run metadata itself and reported the divergence; its classification of all seven cells is the correct one (§ 8) |
| `era1-single-pass-baseline-matrix` | H1, H4, H5, H7, H8 | post-hoc | verified 2026-06-09 | 1 (+3) | **NUMBER-AT-RISK** | its outcome quotes "image cells span 0.094-0.291" and "undefined on 8 of the 14 phase-2 text cells… 0.0665 on the other 6" — a modality-**grouped** statistic (§ 5.1) |
| `tile-size-sweep` | H11 | registered-exploratory | verified 2026-06-09 | 1 | **NUMBER-AT-RISK** | View 2's `best_per_size.by_arch_modality` groups by modality; two legs move (§ 5.2) |
| `results/working-precision/gs-plateau-characterisation.json` | — | **unregistered** | — | 3 | **NUMBER-AT-RISK** | its `summary.by_modality` groups by modality (§ 5.3) |

**Paper-facing sentences and hypothesis rows.**

| location | claim | verdict |
|---|---|---|
| `docs/paper/results-draft.md:195-196` | "MCC 0.094–0.291 across the seventeen computable image-bearing cells" | **NUMBER-AT-RISK — moves** (§ 5.1) |
| `docs/paper/results-draft.md:1240` (2026-08-17 changelog) | "MCC 0.094–0.291 over the 17 computable image-bearing cells" | **NUMBER-AT-RISK — moves** |
| `docs/paper/results-claims-inventory-2026-09-12.md:350` (R2-06) | same figure, status VERIFIED, anchored to `tiering_20m.json` | **NUMBER-AT-RISK — moves**; needs DRIFTED, but see § 7 |
| `docs/paper/results-draft.md:1239` | "undefined on 8 of the 14 phase-2 text-only cells; 0.0665 on the other 6" | **UNAFFECTED — reproduces exactly** |
| `docs/paper/results-draft.md:188-190` | "text-modality prompts dominate image-only prompts at the bottom of the board" | **UNAFFECTED** — the board's Tier 4 is `image-t1.3` + `image-only`, both image; the four phase-2e cells sit in Tier 1 |
| `docs/paper/results-draft.md:182`, `:1244`; claims inventory R2-02 | `canonical-last` F1 0.631, MCC 0.213 | **UNAFFECTED** — it is the board's point-estimate leader whatever its modality |
| claims inventory R4-11 | single-pass isolation 0.342 < 0.520 < 0.606 | **UNAFFECTED** — View 1 holds modality fixed and is byte-identical |
| claims inventory R4-12, R4-13, R4-14; Obs 351, Obs 352 | consensus and View 3 legs, the 256 px verifier rescue | **UNAFFECTED** — Views 1 and 3 byte-identical |
| Obs 447 ("text beats image" is Gemini-3-specific) | rests on `gemini37-image-gs-2026-09-01`, `gemini37-screen-2026-08-28`, `image-b-gs-2026-08-28`, `grid-2026-08-18` | **UNAFFECTED** — every cell in that difference-in-differences is correctly labelled, including `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10`, whose label carries no token and which derives **text** |
| Obs 482 (two metrics, near-opposite orderings) | MCC Tier 1 "led by single-pass image proposer-verifier baselines" | **UNAFFECTED** — the named leaders (`verified-adv-image-baseline-pro-vf` and its twins) derive image; Obs 482 makes no by-track **count** of Tier 1 |
| `results/hypothesis-outcome-table/hypothesis-outcome-table.md` | H1 not rejected; H4 not rejected; H11 exploratory, not in family | **UNAFFECTED — no row changes** |
| `docs/paper/methods-draft.md:619` | H4 row naming `canonical-last` as the single-pass point-estimate leader | **UNAFFECTED** |

## 5. Recomputation, before → after

All three recomputations are US$0 tabulations from committed evaluations, run on
sapphire. **Both published tabulations predate register growth** — the plateau
one covers 306 conditions against today's 459 — so each was re-run **twice on
the register at this commit**, once under the retired name rule
(`--legacy-modality`) and once under the derivation, and the A/B below therefore
changes exactly one thing. Full tables:
`results/modality-track-audit-2026-09-14/recomputation.{json,md}`.

### 5.1 `era1-single-pass-baseline-matrix` — the metric-trade-off range **moves**

Recomputed from `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.json`
(36 cells) and cross-checked against the 36 per-cell evaluations under
`results/paper-eval/phase2/512px-14buf-mcc/`.

| group | before (legacy rule) | after (derived) |
|---|---|---|
| image-bearing cells | **18**, of which **17** have a defined tile MCC | **22**, of which **21** do |
| image-bearing tile-MCC range | **0.0942–0.2907** | **0.0665–0.2907** |
| text-only cells | 14, of which 6 have a defined tile MCC | 14, of which 6 do (**unchanged**) |
| text-only tile-MCC | all six at 0.0665 | all six at 0.0665 (**unchanged**) |
| cells in neither group | **4** (`retest-phase2e::{canonical-first,canonical-last,config-default,random}`) | **0** |
| text-only F1 range | 0.5016–0.6094 | 0.5016–0.6094 (**unchanged**) |

The legacy figures reproduce the published claim to the digit — 17 computable,
0.0942–0.2907, "MCC 0.094–0.291" — so the anchor was right about its own group
and the group was wrong. The four phase-2e **exemplar-ordering** cells are
image-bearing (their pool is an ordering variant of an image config) and sat in
neither group because their pool names neither modality.

**The direction of the contrast survives**: 20 of the 21 computable
image-bearing cells are strictly above every computable text-only cell's 0.0665,
and the twenty-first (`retest-phase2e::random`, MCC 0.0665) ties it. What moves
is the **count** (17 → 21) and the **lower bound** (0.094 → 0.0665). The upper
bound, the text side, and the "text-only cells reach F1 ≈ 0.60" clause are
untouched.

### 5.2 `tile-size-sweep` — two of fifteen modality legs **move**

| size | leg | before | after |
|---|---|---|---|
| 512 | `single-pass/image` | `retest-phase2d::image-terse` F1 0.6052 / MCC 0.2239 | `retest-phase2e::canonical-last` F1 **0.6314** / MCC 0.2132 |
| 512 | `single-pass/text` | `retest-phase2e::canonical-last` F1 0.6314 / MCC 0.2132 | `retest-phase2c::text-scale-4` F1 **0.6094** / MCC undefined |

The other thirteen legs are unchanged, and **Views 1 and 3 — the clean
tile-size isolation and the consensus+verifier head-to-head, which hold modality
fixed rather than grouping by it — are byte-identical**. So the analysis's
conclusion (the optimal tile size is architecture-dependent), Obs 351 and Obs
352 all stand.

One figure inside the registered outcome moves. The outcome reads "BEST-ACHIEVABLE
FLASH CEILING per size … single-pass 512 (0.631) > 384 (0.520) > 256 (0.342)".
Those three figures are the **`single-pass/text` leg** at all three sizes (the
overall 384 px single-pass ceiling is 0.5995, on the image leg), so read as the
text leg the 512 entry becomes **0.6094**, a move of **−0.0220**. The ordering
512 > 384 > 256 is preserved. Read instead as an overall per-size ceiling the
figure is unchanged at 0.6314 — the cell keeps its value and only changes group.
Which reading the outcome intends is a question for the PI; the erratum draft
states both.

### 5.3 `results/working-precision/gs-plateau-characterisation.json` — **nothing moves**

| group | before (legacy rule) | after (derived) |
|---|---|---|
| image | n = 155, onset median **75 m**, p90 **100**, max **150**, tail drift **+0.0064** | n = 163, **75 m**, **100**, **150**, **+0.0065** |
| text | n = 255, onset median **30 m**, p90 **75**, max **150**, tail drift **+0.0070** | n = 296, **30 m**, **75**, **150**, **+0.0072** |
| unknown | n = 49, onset median 40 m, p90 75, max 125, +0.0078 | **group empty** |

55 conditions change group: 49 leave the legacy rule's `unknown` bucket, which
the derivation empties entirely, and the three
`proposer-verifier-384::verified-*-image` conditions move image → text. **Every
group statistic holds** — the onset medians, p90s and maxima are identical and
the tail drifts move by 0.0001–0.0002 — and all five sibling summaries
(`overall`, `by_architecture`, `by_tile_size`, `by_thinking`, `by_temperature`)
are byte-identical. The tabulation is not registered, so it can simply be
regenerated once the PI has read this report.

## 6. A separate finding: the register's verifier-modality field is ambiguous

The brief asked for the verifier's modality "where relevant". It turns out to be
relevant in an unexpected way. Verifier configs split cleanly by the same rule
as proposers — `verify_{adversarial,brief,checklist,comparative}.json` carry six
exemplars, their `*-text` variants carry none — so a verifier stage's own
modality is derivable. Testing the register's 186 `verifier_passes[...].modality`
entries against **both** candidate readings:

| reading | agree | contradict |
|---|---:|---:|
| the **verifier's** own exemplar library | 119 | **55** |
| the **track** (the proposer pool beneath the stage) | 92 | **8** |

The field is therefore *mostly* the track, not the verifier — but not
consistently. The decisive case is one family, inside one run:

| stage | recorded | verify config run | verifier reading | track reading |
|---|---|---|---|---|
| `pv-diag-384::scale-4-optimal-487-verified-v1-n5` | image | `verify_adversarial-text` | text | image |
| `pv-diag-384::scale-4-optimal-487-verified-v1-n10` | image | `verify_adversarial-text` | text | image |
| `pv-diag-384::scale-4-optimal-487-verified-v1-n1` | **text** | `verify_adversarial-text` | text | image |
| `pv-diag-384::scale-4-optimal-487-verified-v1-n3` | **text** | `verify_adversarial-text` | text | image |

All four ran the identical verifier config. The n5/n10 entries were authored by
hand under the track convention; the n1/n3 entries were minted by
`register_k_ladder_phase2_conditions.modality`, whose substring test returned
`text` for a pool named `scale-4-optimal-487`. **Each pair is right under one
convention and wrong under the other**, so the family is split, and no single
value can be called correct until the field's meaning is settled. The same
question decides `gold-standard-v2::verified-v1`,
`proposer-verifier-384::verified-{adversarial,brief,checklist}-image`,
`proposer-verifier-384::verified-cascade-checklist-adversarial` and
`55maps-image-generalisation::verified` — the other six of the eight that
contradict the track reading.

**Not actioned.** No analysis in the corpus groups by this field, so nothing
numerical rests on it, and choosing what it means is the register owner's call.
The full table is
`results/modality-track-audit-2026-09-14/verifier-pass-modality.json`. The
`register_k_ladder_phase2_conditions` substring test **is** fixed, because it was
trying to compute the track and computing it wrongly.

## 7. What was corrected, what was not, and the erratum draft

### Corrected at the source

| file | change |
|---|---|
| `scripts/build_gs_era2_board.py` | `track` now derives from the pool's transmitted configuration; the field gains a `track_basis` sibling naming the route. The retired expression is guarded by a tier-1 regression test |
| `scripts/characterise_gs_plateau.py` | modality derived; thinking and temperature stay name-derived (not grouping variables this audit touched); gains `--out-dir` and `--legacy-modality` |
| `scripts/tile_size_sweep.py` | modality derived, with the name rule kept only as a fallback for a pool no route can read; gains `--legacy-modality` |
| `scripts/build_k_ladder_phase2_unions.py` | the scale-4 pool constant `text` → `text+image`, matching the sibling family table and the register |
| `scripts/register_k_ladder_phase2_conditions.py` | `modality()` derives the track instead of a substring test |

### NOT corrected, deliberately

- **The Era-2 board's seven `track` fields.** A rebuild is pending the PI's
  re-signature, and the brief is explicit: fix the source, not the artefact.
  **What the next rebuild will carry**: `verified-adversarial-image`,
  `verified-brief-image` and `verified-checklist-image` as **text**; the four
  `pv-scale4-optimal` cells as **image**; a new `track_basis` field on all 110
  members. No rank, tier, tie set, Hsu set or metric moves — the tiering never
  reads `track`. No signature field was touched.
- **`results/k-ladder-2026-09-12/phase2/unions.json`.** Regenerating it would
  rebuild the consensus unions and rewrite `experiment_intent.md` files inside a
  signed analysis. The source constant is fixed; the artefact's two scale-4
  rungs still read `text` and will correct at the next Phase 2 union rebuild.
- **The two registered analysis outcomes** (`era1-single-pass-baseline-matrix`,
  `tile-size-sweep`) and **the paper prose and claims-inventory row that quote
  them**. Editing the inventory to a figure the register does not yet carry would
  substitute one inconsistency for another, so R2-06 is left VERIFIED-as-anchored
  with this report as the flag.
- **`results/working-precision/gs-plateau-characterisation.{json,md}`.** Nothing
  in it moves; it can be regenerated whenever convenient.

### Erratum draft, for the PI — **E88** (next after E87)

> ### E88: Modality — a preregistered factor — was assigned by a substring test on the condition label in four scripts; eight conditions and one pool were mislabelled, and two registered outcomes quote an image-group range that moves
>
> | Field | Value |
> |-------|-------|
> | Date | 2026-09-14 (identified by the null-exemplar sensitivity job of 2026-09-13 for seven cells; characterised corpus-wide on the PI's ruling of 2026-09-14) |
> | Type | Correction of a derived factor label (no cell re-scored; group membership only) |
> | Commit | this entry's commit |
> | Files | `scripts/build_gs_era2_board.py` (the `track` assignment, was `:307`), `scripts/characterise_gs_plateau.py` (`derive_tags`), `scripts/tile_size_sweep.py` (`parse_modality_temp`), `scripts/register_k_ladder_phase2_conditions.py` (`modality`), `scripts/build_k_ladder_phase2_unions.py` (`POOL_REGISTRY`); artefacts `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/membership.json`, `results/working-precision/gs-plateau-characterisation.json`, `results/tile-size-sweep/tile_size_sweep.json`, `results/k-ladder-2026-09-12/phase2/unions.json`; outcomes `era1-single-pass-baseline-matrix` and `tile-size-sweep` in `results/run-analyses.json`; `docs/paper/results-draft.md:195-196` and `:1240`; `docs/paper/results-claims-inventory-2026-09-12.md` R2-06. New: `scripts/derive_condition_modality.py`, `scripts/compare_modality_recomputation.py`, `results/modality-track-audit-2026-09-14/`, `reports/modality-track-audit-2026-09-14.md` |
> | Impact | **Nil on every preregistered outcome.** H1's confirmatory contrast groups the five phase-2a conditions, all correctly labelled; the confirmatory family's per-hypothesis *p* values are unrecomputed; no hypothesis-outcome row changes. **Nil on the signed Era-2 board, the signed uplift supplement, the signed verifier-uplift pairing and the signed K-ladder analysis** — none of them groups by the field. **Two unsigned but verified registered outcomes quote a figure that moves**, and one paper sentence with them |
>
> **Description**. Modality — few-shot exemplars sent as images or as text
> labels only — is a preregistered factor (H1). Four scripts assigned it by
> testing the condition label or pool key for the substring `image`. That fails
> when a label names the **verifier's** modality over a text proposer, and again
> when a label carries no modality token at all and the test falls through to
> `text`. The ground truth is `include_example_images` over a non-empty exemplar
> list in the configuration the proposer transmitted
> (`scripts/4_detect_mounds_batch.py:885,901`), now derived corpus-wide by
> `scripts/derive_condition_modality.py`.
>
> Of 593 registered conditions, 591 are derivable and 547 from a transmitted
> configuration, with no route contradicting another. Eight conditions and one
> proposer pool carried a wrong recorded label across four artefacts; the
> register, the passes manifest, the opmax membership and the uplift supplement
> are clean.
>
> **The figures that move.**
>
> | claim | before | after |
> |---|---|---|
> | `era1-single-pass-baseline-matrix` outcome: "image cells span 0.094-0.291" | 17 computable image-bearing cells, MCC 0.0942–0.2907 | **21 of 22**, MCC **0.0665–0.2907** |
> | `docs/paper/results-draft.md:195-196` and `:1240`; claims inventory R2-06 | "MCC 0.094–0.291 across the seventeen computable image-bearing cells" | **0.0665–0.2907 across the twenty-one** |
> | `tile-size-sweep` outcome: single-pass ceiling ladder, 512 px entry (the `single-pass/text` leg) | 0.631 (`canonical-last`) | **0.6094** (`retest-phase2c::text-scale-4`); unchanged at 0.6314 if the figure is read as the overall per-size ceiling |
> | `tile_size_sweep.json` `by_arch_modality` 512 `single-pass/image` | `image-terse` 0.6052 / 0.2239 | **`canonical-last` 0.6314 / 0.2132** |
>
> **What does not move.** The direction of the metric trade-off (20 of the 21
> computable image-bearing cells are strictly above every computable text-only
> cell, the twenty-first ties it); the text-only side entirely (14 cells, 8
> undefined, 0.0665 on the other 6); the single-pass tile-size isolation
> (0.342 < 0.520 < 0.606) and the consensus+verifier head-to-head, both
> byte-identical; every plateau-tabulation group statistic; the Era-2 board's
> ranking, tiers, tie sets, Hsu sets and tile-MCC family; Obs 351, Obs 352,
> Obs 447 and Obs 482.
>
> **Open for the PI**: (i) which of the two readings the `tile-size-sweep`
> outcome's ceiling ladder intends; (ii) whether the register's
> `verifier_passes[...].modality` field means the verifier's own exemplar
> modality or the track the pass belongs to — it is used both ways, and one
> family is split across both conventions inside one run (§ 6 of
> `reports/modality-track-audit-2026-09-14.md`).
>
> Cross-references: **E86** (the null-exemplar overlap, whose sensitivity job
> found the first seven cells); **E81** (undefined tile MCC published as `0.0` —
> the same § R2 passage's prior correction, and the reason the text side is
> stated as undefined rather than near-zero); **E83** (the tie-set revision that
> the same two outcomes carry).

## 8. The sensitivity job's leak signature, re-read with corrected labels

**It needs no re-reading: it already used the corrected labels.**
`results/null-exemplar-sensitivity-2026-09-13/cell_inventory.json` decides each
cell's exposure from the proposer pool's own run metadata, cross-checks it
against the register and the config file, records every source's vote, and flags
`sources_disagree` — and reports the seven divergences from the board's `track`
explicitly rather than inheriting them. This audit's independent derivation
agrees with it on all seven, and on every other cell of all four boards.

So the leak signature stands as published: on the Era-2 board an image-bearing
cell's false-positive rate on the 20 exposed tiles is 0.561 times its rate on
the other 467, against 0.685 for a text control — mean log ratio −0.1433 against
−0.0552, difference −0.0881 at *p* < 0.0001, and −0.0773 at *p* < 0.0001
stratified within the single `pv-diag-384` run. The four `pv-scale4-optimal`
cells were counted as **image-bearing** there and the three
`verified-*-image` cells as **text controls**, which is what this audit
confirms. Had the board's `track` been used instead, three text controls would
have been counted as image-bearing and four image cells as controls — 7 of 150
cells, 4.7 % of the contrast, mislabelled in *both* directions.

## 9. Verification

- `scripts/derive_condition_modality.py --check` exits non-zero while any
  recorded label disagrees with a derivation; it currently reports the eight
  conditions and one pool above. Reproduced byte-identically on amd-tower and on
  sapphire.
- Tier-1 tests: `tests/test_derive_condition_modality.py` (32 tests over
  synthetic fixtures — the derivation rule, the gzip and default-key meta
  shapes, both failure-shape mechanisms, the pool-directory normalisation, both
  register shapes, the `text+image` refinement, the nested-record walk) and two
  new tests in `tests/test_build_gs_era2_board.py` pinning the derived `track`
  and guarding the retired expression against reappearing.
  `tests/test_tile_size_sweep.py` updated: its `parse_modality_temp` case for
  `canonical-last` previously **pinned the defect** as `"text"`.
- Tier-2: `test_derived_modality_agrees_with_the_register_for_every_condition`
  and `test_no_derivation_route_contradicts_another` assert the corpus-wide
  properties § 2 reports.

## 10. Observation candidate (for the PI to accept or decline)

> **A derived factor label is a measurement, and this corpus was deriving one by
> substring.** Modality is one of the study's preregistered factors, and in four
> independent scripts its value was computed by asking whether the string
> `image` appeared in a condition's label. The rule is right for most of the
> corpus precisely because the naming convention is good — which is what let it
> survive to a signed board. It fails in two shapes that the convention itself
> creates: a proposer–verifier label names *both* stages, so the verifier's
> modality can win; and a label that varies a *different* factor (exemplar
> ordering, exemplar scaling) names neither modality, so a fall-through default
> silently assigns one. The second shape is the more dangerous, because it is
> invisible — there is no wrong token to notice, only a missing one, and the
> cells it hits are exactly the cells that vary something else and therefore sit
> in the *other* arm's group. The corrective is not better naming but a
> different source: four of the five routes this audit uses read the
> configuration that was transmitted, and where two of them could both speak
> they never once disagreed across 593 conditions. The generalisable rule is
> that any field naming an experimental factor should be derived from the
> apparatus state that realised it, with the label kept as a cross-check that is
> allowed to fail loudly — and that a register which records the *same* field
> under two different meanings in two different runs (§ 6) will eventually be
> read under the wrong one.

## Changelog

### 2026-09-14 — Original publication

First corpus-wide characterisation of the modality-label error the
null-exemplar sensitivity job found on seven Era-2 board cells on 2026-09-13,
on the PI's ruling of 2026-09-14. Establishes the mechanism (a substring test on
the condition label, in four scripts, failing in two shapes); derives modality
for all 593 registered conditions from the transmitted configuration through
three independent routes; tabulates it against all eleven corpus fields that
record a modality; classifies the reach of every affected analysis; recomputes
the three modality-grouped statistics with corrected labels; drafts erratum E88;
and reports the register's verifier-modality field as ambiguous rather than
wrong. No prior revision to diff against.
