# Manipulation check: did each arm's manipulation reach the model?

> **Last revised**: 2026-10-05 (original publication, Session 160). See
> [§ Changelog](#changelog) for revision history.

**Status**: evidence base for `planning/text-track-transmission-2026-10-05.md`,
which tracks the work it leads to. Produced by a read-only Opus subagent of
Session 160 at the PI's request; its three heaviest claims (the Phase 2c
text arms, the retest summary's p = 0.001, the methods draft's wording)
and its correction of the Phase 3c premise were re-checked at source in
session before publication. Per-arm signatures:
[`manipulation-check-2026-10-05-arms.json`](manipulation-check-2026-10-05-arms.json).

Read-only check, 2026-10-05, repository `map-reader-llm` at `1d6f29db3`
(branch `register-repair`). Nothing in either checkout was written. Metas
were harvested on sapphire (`/tmp/manip/`). The scratch scripts that did it
are kept as provenance in `manipulation-check-2026-10-05-scripts/`
(`harvest.py`, `arms.py`; written for one run, not yet a maintained tool),
and the per-arm table is `manipulation-check-2026-10-05-arms.json`.

## A. Method and coverage

**What counts as transmitted.** Taken from the code that built the requests,
at the commits the metas record:

- **Proposer, real-time path**: `scripts/4_detect_mounds_batch.py:925-960`
  (current). This is unchanged in effect since `4ecaf06d4` (2026-02-06, E25).
  An image configuration sends, for each example, a text label and then the
  image. A text-only configuration (`include_example_images: false`) sends
  **nothing** from the example list: no images, no labels.
- **Proposer, batch path**: `scripts/lib_batch_api.py`
  `_build_reference_parts`, which returns `[]` when images are off. It is
  verified at the retest commit `5a57f586e` (`lib_batch_api.py:312`).
- **What every proposer request sends**: the system instruction, then
  "Here are the Reference Symbols you must find:", then the example parts
  (if any), then "Now, find detection instances that visually match ANY of
  the above Reference Examples in the Target Map Tile below:", then the tile.
  Sources: `5a57f586e:scripts/lib_batch_api.py:407-415` and
  `866b9e0bb:scripts/4_detect_mounds_batch.py:314-321`. So a text-only
  request points at "the above Reference Examples" when there are none.
- **Verifier**: `scripts/lib_verifier.py:358-382`. It never reads
  `include_example_images`. If `text_only_labels` is present it sends one text
  block, "Reference examples (text descriptions only): - Positive: …" (six
  labels). Otherwise it sends every listed example as a labelled image. The
  `verify_{adversarial,brief,checklist,comparative}.json` configs list six
  images; the `-text` configs list six labels and no images. This matches
  ruling E88's convention.

**Coverage.**

- **Registered runs**: all 44 (`results/run-registry.json`). That gives 426
  arms from `results/run-conditions.json`: 178 proposer pools and 248
  verifier legs.
- **Mapping arms to metas**: 424 arms were mapped through
  `results/passes-manifest.json` `provenance.source_files`, and 2 by
  directory. Together they draw on 1,238 distinct metas.
- **All metas read**: 2,867 (2,861 under `outputs/` and `archive/`, plus 6
  under `results/`). This includes every arm directory under
  `outputs/retest/**`, which are all registered pools of the nine `retest-*`
  runs.
- **Signature per arm**: model of record, effective temperature, thinking
  level, system-instruction hash, examples actually sent (fingerprint and
  count), and input tokens. The model of record is the per-item
  `model_version`, else `pricing_used.model`, else `configuration.model`
  (E57's precedence). Effective temperature is `temperature_effective` where
  present (E55). Input tokens are taken per request where the meta records
  them. All of it is in `arms.json`.

| Evidence class | Pools | Verifier legs | Total |
|---|---:|---:|---:|
| Per-request input tokens (`per_item_metadata`) | 74 | 15 | 89 |
| Aggregate tokens only (`usage_stats` total ÷ requests) | 0 | 188 | 188 |
| Configuration fields and code at the recorded commit only | 104 | 45 | 149 |

**Config-only arms.**

- **Whole runs**: `retest-phase2a`, `-2c`, `-2d`, `-2e`, `-3c` and
  `retest-h11-single-pass-384-t0`.
- **Pools only**: the pools of `retest-phase2b`, `-3a`, `-3a-high`,
  `-3a-replication` and `consensus-384-t1-0`, plus some `pv-diag-384` pools.
- **Why**: these are Batch-API metas with `total_input_tokens = 0`, which
  the register books as `cost_basis: unrecorded`.

Two arms resolved to no meta and are **unverified**:

- `pv-diag-384::verified-text-1of5`: its `verified/text-1of5` directory does
  not exist.
- `flash35-pv-2x2::f3-min-text-1of10`: its path is a consensus GeoJSON.

**The token law that makes the check decisive.** The check covers 1,042
proposer metas that record per-request tokens.

- **Text-only metas** (486): with Gemini 3 Flash on the shared instruction
  `e169b723…`, a text-only request costs exactly **1,502** input tokens.
- **Image metas**: each transmitted example adds about 1,090 tokens:
  - 7 examples: 9,119
  - 9 examples: 11,299
  - 13 examples: 15,659
  - 17 examples: 20,010–20,019
  - 25 examples: 28,739
  - 41 examples: 46,179
- **Fit**: no `e169` Flash meta departs from this by more than 15 tokens.
- **Listed examples are inert**: all 486 text-only metas **list** 7–41
  examples, and none transmits any. Their tokens sit at the instruction-only
  level for their instruction:
  - 1,502: `e169`
  - 1,528: `d26e`, propose
  - 1,651 and 2,052: `56aa` and `599e`, terse and verbose
  - 1,672: `d85c`, Experiment E
- **No contradictions**: no arm's recorded input tokens contradict its
  `include_example_images` × example count.

**Comparisons searched.**

- **Within each run**: arms whose configurations differ but whose
  transmitted signatures are identical.
- **Across runs**: the same test, on the same test set and tile grid.
- **Registered analyses**: every pair inside each of the 71 analyses in
  `results/run-analyses.json`, plus the H-series family inputs
  (`family-bh-fdr-confirmatory`).
- **Unregistered metas**: a scan of all 2,867 metas for text-only sets that
  list different libraries.

## B. Null manipulations found

### B.1 Null manipulations (config differs in an example field; transmitted request identical)

| # | Run (registered?) | Arms | Intended manipulation | What was sent | Evidence |
|---|---|---|---|---|---|
| 1 | `retest-phase2c` (registered; Era-1 340 tiles, 2026-03-15) | `track2-text-{canonical, plus-hp, pure-positive-canon, scale-4, scale-8}` | H8 library composition on the text track: 9/13/7/13/17 listed examples, five library hashes (`e68431cd1e`, `3f7f028c2e`, `2f594dbbd0`, `f955230f7f`, `8580ecb225`) | Five identical requests: instruction `e169b723…`, T = 0.0, MINIMAL, `gemini-3-flash`, no examples. These are also identical to `retest-phase2b::track2-text-t0.0`, so six executions of one configuration | **Config fields and code only.** `include_example_images: false` in all five snapshots; commit `5a57f586e` (`lib_batch_api.py:312` returns `[]`); usage unrecorded. The token law above holds for every text meta that does record usage. The outputs differ (881–897 detections, distinct coordinate hashes), so their F1 spread (0.5969–0.6094) is run-to-run variance |
| 2 | Experiment E (`archive/outputs-pre-retest-60-tile/preliminary-results/`; unregistered, D40) | E1 → E2 ("restore null examples") | 10 vs 13 listed examples | Identical: instruction `d85c8439…`, HIGH, T = 0.7 | **Per-request tokens**: 1,672 on every tile of all four passes (Obs 496, re-confirmed here) |
| 3 | H10/H12 v1 probe (`archive/h10-h12-v1-retracted-probe/`; unregistered, retracted by Obs 235) | Five `detect_brief-text_pool_160_*` configs, 50 metas | Pool and HP:HN library (17/17/17/25/41 listed) | Identical text-only requests | **Per-request tokens**: 1,502 on all 50 metas |

The archive scan found no other text-only set with differing libraries.

### B.2 Not null, but the manipulation is not recorded in the metas

| Run | Arms | Intended | Recorded in metas | Status |
|---|---|---|---|---|
| `retest-phase2e` (registered, H4, image) | `config-default`, `canonical-first`, `canonical-last`, `random` | Example ordering of the 13-image `library_plus-hp` | All four snapshots show the same order (examples 01–10, 15–17), the same `library_hash` `3f7f028c2e`, no `ordering_override`, and zero usage | **Unverified from metas.** The batch reorder `_reorder_examples_for_batch` (added `ead94aa81`, 2026-03-15 02:33 UTC) is present at the recorded commit `5a57f586e` (`run_phase2.py:74`, called `:1455`, passed to the JSONL builder `:1469`). The runs ran at 11:02–11:40 UTC. Transmission is inferred from code, not shown by artefact; a permutation cannot be seen in token counts |

### B.3 The brief's Phase 3c premise does not hold

`retest-phase3c::track2-text-h9-a-p1..p5` were **designed** as identical
passes. They were not permutations.

- **Study definition**: `studies/retest/phase3c-h9-diversity-track2.yaml:41-55`
  ("Baseline — identical pass 1 … 5").
- **Config**: `prompts/configs/phase3c-t2-h9A.json` ("Baseline: identical
  passes … Images are listed for config consistency but not sent to the
  model").
- **Report**: `results/phase3c-diversity/phase3c-comprehensive-results-report.md`
  § 1.1 ("All 5 passes use identical config").

Their identical signatures are therefore intended and are **not a null
manipulation**. Track 2 C is documented as degenerate, and Track 2 E as
"text + temperature" (same report, § 1.1). The only within-design collapse
is `h9-E-p3` ≡ `h9-B-v3`, since E-p3 runs at T = 0.7, the base temperature.

### B.4 The converse: a "replicate" that was not one

The `proposer-verifier-384` note in `results/run-conditions.json` calls the
`-v2` and `v1-prompt` legs "identical T=0.0 config re-runs". The tokens say
otherwise:

| Leg | Exemplars sent | Tokens per request |
|---|---|---:|
| v1 adversarial-text | none | 1,727 |
| `-v2` adversarial-text | 6 labels | 1,792 |
| v1 adversarial-image | 9 images | 11,602 |
| `-v2` adversarial-image | 6 images | 8,305 |

The same holds for `proposer-verifier-512`. `reports/register-repair-2026-10-05.md:22`
repeats "`-v2` re-runs".

### B.5 Accidental replicates (identical transmitted signature, same test set, different arms)

There are 23 groups, all listed in `arms.json` `flags`. Those whose
configuration names differ:

| Group | Arms | Note |
|---|---|---|
| 16 | `retest-phase2b::track2-text-t0.0` ≡ the five 2c text arms | Null manipulation #1 |
| 15 | `retest-phase2b::track1-image-t0.0` (`detect_brief-text-image`) ≡ `retest-phase2c::track1-image-scale-8` (`library_scale-8`) | Same 17 examples |
| 19 | `retest-phase2c::track1-image-plus-hp` ≡ `retest-phase2e::config-default` | Study says "reused from Phase 2c" but it was re-run |
| 20 | `retest-phase2c::track1-image-pure-positive-canon` ≡ `…exploratory-pure-positive-canon` | Same config, run twice |
| 10 | `h8-v2::scale-8` ≡ `h10::pool_160_hp4hn4` | Same library hash `f7458f0cfc`. Separate executions (run_ids differ; 11:31–11:40 vs 04:39–04:50 UTC, 2026-04-15), as `results/h8-v2/analysis_summary.md:245-267` says. But E51 (`protocol-errata.md:1629-1636`) says it was "not re-launched" |
| 5, 6 | `n1-outstanding-384::pro-{image,text}-high-t0` ≡ `pv-diag-384` Flash arms | Known (E57): intended Pro, dispatched Flash |
| 21, 22, 23, 24 | Phase 3c A / D-t3 / D-t5 / E-p3 ≡ Phase 3a-high or 3c B-v3 | By design |

The other groups are documented reproductions of one configuration, for
example `gold-standard-v2` ≡ `pv-diag-384::flash-high-text-n5-text-t0.7`, and
`55maps-generalisation` ≡ `55maps-text-high-generalisation` (the
"reproduction sanity test", `docs/notes/working-notes.md:11632`).

**Effect on the Era-1 board.** `era1-single-pass-baseline-matrix` has 36
cells but only **26 distinct transmitted configurations** (23 if Phase 2e's
orderings did not transmit). Its 15-cell Tier-1 set holds **9** (7). Six
Tier-1 cells are one text configuration.

## C. Claims affected

**Rule.** "Direction" means the claim's substantive conclusion is void or
must be withdrawn. "Labelling" means the conclusion survives but the
description of what was manipulated or sent is wrong.

### C.1 Null manipulation #1 (Phase 2c text track)

| Source | Claim | Affected |
|---|---|---|
| `docs/paper/results-draft.md:192-200` | "the Tier-1 admissible set spans 15 of the 36 single-pass cells … example-library composition (H8) … all land inside or near that tie" | **Labelling**: 15 cells are 9 transmitted configurations; on the Era-1 board H8 is an image-only test |
| `docs/paper/results-draft.md:206-215` | "eight of the fourteen [text-only cells] returned at least one detection on every one of the 340 evaluation tiles" | **Labelling**: six of the fourteen text cells are one configuration |
| `docs/paper/results-claims-inventory-2026-09-12.md:360` (R2-01), `:363` (R2-04), `:366` (R2-07) | Same counts | **Labelling** |
| `results/retest/retest-production-summary.md:23` | "no significant library-composition differences on either track. Single-track significant: scale-4 > plus-hp on text (ΔF1 = +0.013, p = 0.001)" | **Direction**: the text half is not a test, and the significant text contrast is between identical requests. Withdraw it |
| same, `:94-104` (§ 5.2) | "Minimal sensitivity to library composition on the text track … plus-hp vs scale-4 … p = 0.001" | **Direction**: void as a library result; it is five replicates |
| same, `:240-244` (§ 11.4) | "Phase 2c T2 — H8 Library, Text (1 significant)" | **Direction**: false positive between replicates |
| same, `:30`, `:302`, `:316`, `:320` | "Library composition … no significant effect"; "null on either track"; suggested paper text "H8 library composition … null on both tracks" | **Labelling**: the image track carries the null; drop "both tracks" |
| `results/retest/pairwise-bootstrap-comparisons.json` `comparisons[40-49]` | Ten "Phase 2c T2: H8 Library (Text)" contrasts; `[45]` has `f1_p_value` 0.001 and `significant_raw: true` | **Direction** for `[45]`. The ten are replicate contrasts |
| `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.{md,json}`; analyses `era1-single-pass-baseline-matrix` and `era1-leaderboard` in `results/run-analyses.json` | Five 2c text cells ranked as distinct configurations, all five in Tier 1 | **Labelling**. On this instrument none of the 20 replicate pairs is significant (smallest p 0.0588, BH ≥ 0.14), so no tier is driven by a replicate difference |
| `docs/methodology/preregistration/protocol-errata.md:4262-4275` (E81 table) | Five 2c text conditions listed separately | **Labelling** only; the undefined MCC is correct |

What is **not** affected:

- **H8's registered outcome.** `family-bh-fdr-confirmatory` takes H8 from
  `h8-v2` plus-hp vs scale-4, an image contrast, and from no 2c text row.
- **The image-track Phase 2c null.**

The project had already judged this test meaningless:

- Decision 16, `docs/methodology/preregistration/decisions-log.md:737-738`:
  "With `include_example_images: false`, the test is meaningless."
- `results/phase2c-carry-forward-parameters.md:14-19`: the 2026-02 programme
  skipped Track 2 after a pre-flight check found identical counts.
- Obs 129, `docs/notes/working-notes.md:2122`.

The 2026-03-15 retest nonetheless ran Track 2
(`studies/retest/phase2c-h8-library-text-only.yaml`) and reported it as a
library test.

### C.2 Null manipulation #2 (Experiment E): already ruled in Obs 496 and D40, two citations not yet annotated

| Source | Affected |
|---|---|
| `results/phase3d-experiment-e-results.md:101`, `:122` (Finding 2) | **Direction**: void |
| Obs 156 (`docs/notes/working-notes.md:2839`) | **Direction**: void (Obs 496 corrects it) |
| Obs 155 (`:2757`) and Obs 157 (`:2877`) | **Direction unsupported**: real manipulations, but each is one 60-tile run inside a 0.050 replicate spread |
| Obs 158 (`:2917`) | **Weakened** (strength only) |
| `docs/paper/discussion-outline.md:293-297` | Already carries the dated D40 note |
| `docs/paper/discussion-seeds.md:528-531` ("Experiment E showed the missed mounds are invisible to the model") | **Strength**: rests on Finding 4 alone. **No dated note yet** |
| `docs/paper/discussion-seeds.md:553-556` ("give the Obs 155 / Experiment E pattern a published mechanism") | **Direction unsupported**. **No dated note yet** |

### C.3 Null manipulation #3 (H10/H12 v1)

Obs 227 (`working-notes.md:7464`) and Obs 234 (`:9199`) are retracted by
Obs 235 (`:9422`). No paper draft cites them.

A related citation error runs the other way.
`docs/paper/discussion-seeds.md:499-501` says the H10/H12 manipulations
"were not executed as intended (E48)". E48 is an unrelated correction of the
HN count (`protocol-errata.md:1523`), and the v2 runs **did** transmit
(§ D). This is a **labelling** error.

### C.4 Phase 2e (ordering not recorded)

The ordering transmitted by code but is unverified from the metas. The
direction of each claim survives if the code ran as committed; its
evidence base should say "inferred from the code at the recorded commit".

- `docs/paper/results-draft.md:194-196` ("led numerically by a
  few-shot-ordering variant (`canonical-last`, F1 0.631)") and R2-02
  (`results-claims-inventory-2026-09-12.md:361`).
- `results/retest/retest-production-summary.md:25`, `:145`, `:250-251`,
  `:300`, `:320`.
- The H4 confirmatory input (canonical-first vs canonical-last, p = 0.124,
  `family-bh-fdr-confirmatory`).

Separately, Obs 280's table (`working-notes.md:13683`) labels
`h4-canonical-last` "text". It transmits 13 images; this is a
**labelling** error of the E88 kind.

### C.5 Wrong descriptions of what a text-only configuration sends

Each of these says text-only configurations send "labels". They send nothing
from the example list. The conclusion each draws (text cells never saw the
null pixels) stands, so all are **labelling**:

- `protocol-errata.md:5351`, `:5367` (E86: "only the labels travel")
- `protocol-errata.md:5640` (E88: "sent as images or as text labels only")
- `docs/methodology/preregistration/osf/errata-pointers.md:76` (OSF-facing:
  "carry the nulls as labels only")
- `results/null-exemplar-sensitivity-2026-09-13/findings.md:43-44` ("sent the
  labels only")
- `results/phase2c-carry-forward-parameters.md:16` ("receive only example
  labels")
- `reports/null-exemplar-errata-2026-09-13.md:98`
- `reports/modality-track-audit-2026-09-14.md:367`
- `decisions-log.md:1159` (Decision 25: "Works with text-only examples")
- `docs/paper/methods-draft.md:499-500`, `:529`, `:756` (quoted in § E)

### C.6 Other register labels

- **`gold-standard-v2::verified-v1`** is registered `"image"`, but it
  transmitted six text labels (`verify_adversarial-text`, 1,792 tokens per
  request, `outputs/gs/gold-standard-v2/verified-v1/run.meta.json`).
  `derive_condition_modality.py --check` cannot catch it: its `POOL_ROOTS`
  never resolve `outputs/gs/…`. **Labelling**.
- **`retest-production-summary.md:320`** says "Gemini 2.0 Flash"; every
  retest meta records `gemini-3-flash`. **Labelling**, incidental.

## D. Not affected (manipulations that did reach the model)

| Manipulation | Evidence |
|---|---|
| **H8 v2 library** (image, `h8-v2`) | Per-request tokens: pure-positive-canon 9,119; canonical 11,299; plus-hp 15,659; scale-4 15,659; scale-8 20,019; scale-16 28,739; scale-32 46,179. Explicit-cache sizes in `data/pricing/run-log-tiers.json` `explicit_cache_sizes`: 8,009 / 10,189 / 14,549 / 14,549 / 18,909 / 27,629 / 45,069. Plus-hp and scale-4 match in size but send different crops: 4 hard positives vs 2 hard positives + 2 hard negatives, distinct SHA-256 |
| **H10 v2 pool size** (`h10`) | 20,010–20,019 tokens per request, and the hard crops differ by SHA-256. pool_020 vs pool_160: 7 of 8 differ. pool_040 vs pool_080: 2 of 8 differ, so the manipulation is partial for that pair. The crops were committed in `50927dc4d` before the runs (`54f27d6e1`), and only new files were added afterwards (`e575a57d7`) |
| **H12 v2 HP:HN** (`h12-v2`) | r1 2 HP + 6 HN vs r3 6 HP + 2 HN; distinct crops; 20,019 tokens per request |
| **H9-C image rotation** (`retest-phase3c` track 1) | Config only (no usage). Each of img1–img5 sends a different hard-negative set (`example_11/18/22/26`, `12/19/23/27`, …), with distinct file hashes |
| **Phase 2c image track** | Config only. Five distinct listed libraries with images on |
| **Modality campaigns**: image-B, Gemini 3.7 image (GS and 55-map), Gemini 3 image 55-map, `55maps-image-generalisation`, `n1-*` image cells | Image proposers send 20,018–20,019 (17 examples) or 15,659 (13) tokens per request; text proposers send 1,502 |
| **Verifier modality** | Image vs text tokens per request: adversarial 8,310 vs 1,792; brief 8,085 vs 1,567; checklist 8,452 vs 1,934; comparative 8,294 (`pv-diag-384` Session-78 matrix). Registered verifier modality matches transmission in 246 of 247 resolved legs (§ C.6) |
| **Temperature** | Effective temperature differs as intended in every T-sweep arm: Phase 2b; H7 escalation 1.6/2.0; Phase 3c D 0.4–1.0; `consensus-384-t1-0` = 1.0 (E43). The verifier T pilot carries 0.5/1.0 in `temperature_effective`, with `configuration.temperature` at 0.0 (E55). Temperature leaves no token trace, so this is config evidence only |
| **Thinking** (Flash) | Thought tokens per request: HIGH median 1,999 (170 metas) vs MINIMAL 0 (251 metas); Gemini 3.7 LOW median 275 |
| **Instruction wording** | System-instruction hashes differ as intended: Phase 2a `e169`/`522f`/`f3ae`; Phase 2d `56aa` terse / `599e` verbose; Phase 3c B v1–v5 `7c40`/`fc2e`/`6382`/`1db4`/`2491`; E47 `d26e` (1,528 vs 1,502 tokens) |
| **Model** | Model of record matches intent everywhere except E57's known `n1-outstanding-384` Pro→Flash cells. The four `pv-diag-384` "Pro" pools carry `configuration.model = gemini-3-flash` but price and per-item model as `gemini-3.1-pro-preview` (E57) |

**Unverified: thinking on Pro.** Thinking on Gemini 3.1 Pro could not be
confirmed from usage.

- All six Pro HIGH metas with usage record **0** thought tokens. These are
  the `n1-pro-rerun-384` `pro-{text,image}-high-t0` pools.
- The Pro MEDIUM metas record 6–43 per request.
- Thought counts this low are implausible for Pro, so this looks like a
  usage-reporting gap. It may not be a dispatch failure. **Unverified.**

## E. The paper's description of the text condition

**Quote 1.** `docs/paper/methods-draft.md:524-530`:

> Each request assembles a system instruction (task definition,
> target-symbol description, and output-format specification), a
> configurable library of few-shot examples, and the target tile … Examples
> are drawn from labelled calibration tiles in positive, negative, and null
> categories, and are presented as images, text descriptions, or both,
> according to the modality condition.

**Wrong:**

- No condition presents examples as text descriptions alone.
- Image conditions send each example as a label string ("Positive" /
  "Negative") followed by its image.
- Text-only conditions send no example at all. Their requests are the
  instruction, the two fixed sentences, and the tile, a zero-shot request.
  The second sentence still asks the model to match "the above Reference
  Examples".
- "Text descriptions" of examples is what the **verifier's** `-text` configs
  send: "Reference examples (text descriptions only)", six labels.
- The registration defines Brief-text as "Text-only with concise symbol
  descriptions", with no images (`osf/preregistration.md:415`), so the
  pipeline did what was registered. Only the paper's description is wrong.

**Correction:**

> "… a system instruction (task definition, verbal target-symbol
> description, output format), an optional few-shot library and the target
> tile. In image-bearing conditions each example is sent as a short label
> followed by its image; in text-only conditions no example is sent, neither
> image nor label, so the symbol is specified by the instruction's
> description alone (zero-shot) — the registration's Brief-text level. The
> verifier's text variant, by contrast, sends six example labels as text."

**Quote 2.** `docs/paper/methods-draft.md:497-502`, and again in the
changelog at `:756`:

> of the forty-one configurations that transmit example images, thirty-seven
> include the nulls, while the twenty-two text-only configurations carry
> them as labels alone

**Wrong:** "carry them as labels alone" should read "transmit no exemplar at
all". The conclusion, that text cells were unexposed to the null pixels,
stands.

**Quote 3.** `docs/paper/methods-draft.md:577-588`:

> Phases 2c (library composition) and 2e (example ordering) are undefined,
> since both factors operate on image examples … Track 2 (`brief-text`) ran
> temperature testing and passed directly to the Phase 3a voting study, the
> image-dependent phases being inapplicable rather than skipped.

**Wrong:**

- This holds for the 2026-02 programme. The Era-1 retest that supplies the
  paper's single-pass board (`results-draft.md:192-215`) did run Track 2
  through Phase 2c (five inert library arms) and Phase 2d (text terse and
  verbose).
- The methods should either say so, and present the five 2c text cells as
  replicates of the T = 0.0 text configuration, or drop those cells from
  the board.

**Quote 4.** `docs/paper/discussion-seeds.md:466-475`:

> few-shot foundation-model extraction … with the TEXT-ONLY variant as the
> distinctive result

**Wrong:** the text-only variant is zero-shot, so this framing mislabels
it.

**Quote 5.** `docs/paper/discussion-seeds.md:492-501`:

> Text specification beats few-shot image examples

This is **correct as worded**: instruction alone vs instruction plus images.
Its boundary sentence citing E48 is wrong (§ C.3).

## Changelog

### 2026-10-05 — Original publication (Session 160)

Commissioned after Obs 496 (Experiment E's example levers never reached the
model) to establish how far the text-only transmission gap reaches across
every registered run. No figures moved; this is a first publication.
