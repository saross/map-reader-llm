# D40: how to register the four archive groups, consistently with precedent

Investigated 2026-10-05 on branch `register-repair` at `4d3323305`. This was a
read-only pass: no file in the repository was modified, staged or committed.
Line numbers are as read at that commit. Unless a dollar figure is marked
"indicative", it is the meta's own `cost_estimate.total_cost_usd`.

## 0. Bottom line

| # | Group | Recommendation | Precedent it follows |
|---|---|---|---|
| 1 | Phase 1 library (5 metas) | **(i) A new run, `phase1-library`.** One proposer pool of 5 passes in the archive, with no condition. | D41 (`h10::coldstart-pool_160`: archived mining passes that built a library a registered run declares, registered as rows with no condition). The Era-1 register also has one run per execution-plan phase. |
| 2 | Experiment E (4 metas) | **(iii) Leave it out of the register.** Keep it in the archive ledger as project-total spend, but **not** under the label SUPERSEDED, because nothing replaced it. Close the paper's provenance gap separately (§ 3d). | No 60-tile or Phase 3d run is registered. Where a Phase 3d conclusion was still needed, it was **re-run** at a registered scope (`verifier-t-pilot` "revisits Phase 3d"). |
| 3 | Legacy PV (13 metas) | **(ii) Register them as verifier passes of the runs whose pools they verified**, through `repo_path`: 7 on `retest-phase2b`, 4 on `retest-phase3a`, 2 on `retest-phase3a-replication`. No conditions for now. | Era-1 Stage D legs on `retest-phase2b`, `-phase3a` and `-phase3a-high` (D31, `afe487f94`). D32's vote-3 increments. The WBF legs, registered on their source runs without conditions. |
| 4 | Obs 230 (12 metas) | **(iii) Keep them SUPERSEDED in the archive ledger** (D22). | No retracted or quarantined execution is registered (the h10 v1 probe, `v2-verifier-contamination`). No registered artefact uses Obs 230's data. |

## 1. How the register treats archived and pre-register work (precedents)

- **P1. The register was enumerated from the live `outputs/` tree only.** `planning/run-registry-draft-review.md:20-24` records "Primary source: the live `outputs/` tree". `archive/` was never enumerated. The only archived executions registered since then are passes of runs that already existed: D41 and D38's cleanup leg (P3, P4).
- **P2. Status vocabulary.**
  - The schema allows `planned | active | archived` (`docs/manifest-schemas/run-registry.schema.json:30-34`).
  - All 43 registry rows are `active`; `archived` has never been used.
  - The generator special-cases only `planned` (`scripts/generate_post_run_report.py:1553`, `1768`, `2166`, `2771`). An `archived` row would therefore be extracted like an `active` one. This is from reading the code; I did not run it.
- **P3. D41: library-construction (mining) passes become rows.**
  - Ruling: `planning/pi-decisions-2026-09-20.md:55`.
  - Executed in `4d3323305`. The entry is at `results/run-conditions.json:8158`:

    ```json
    "coldstart-pool_160": {"modality": "image",
      "repo_path": "archive/intermediate-calibration/h10-calibration-runs-v2",
      "path": "pool_160"}
    ```

  - It is a proposer pool of `h10`, and no condition uses it.
  - `h10`'s registry row (`run-registry.json:42`): status `active`, notes "one run (H10 library-pool-size study) … example-pools-v2 … and hard-cases-v2 … are diagnostics, not conditions". Its facts declare `calibration_set_id: "pool_160"` with 160 tiles.
  - D41 overruled `archive/ARCHIVE-MANIFEST.md`'s framing of those passes as "not needed for final leaderboard analysis" (the `intermediate-calibration/` section). Group 1 has exactly the same shape.
- **P4. D38: an archived cleanup leg becomes a row of its run.** `run-conditions.json:8911`:

  ```json
  "verified-cleanup-20260410": {"modality": "text",
    "repo_path": "archive/deprecated-staging/55maps-generalisation-verified-cleanup-20260410",
    "path": "."}
  ```

- **P5. Era-1 Stage D: verifier legs over Era-1 pools register on the source runs.**
  - Registered in `afe487f94` (D31); the conditions were minted in `734545beb` (2026-06-08).
  - Example: `retest-phase2b.verifier_passes["verified-adv-text-t0.0-pass1"] = {"modality": "text", "repo_path": "outputs/era1-pv-stage-d", "path": "512-single-text-t0.0/pass_1/verified"}` (`run-conditions.json:10078`).
  - Likewise on `retest-phase3a`, `retest-phase3a-high` and `pv-diag-256`. Each carries a condition with an `eval_path` scored on the 14-buffer plus MCC standard (`results/era1-pv-stage-d/`).
- **P6. D32: increment legs are rows of their parent runs** (`vote3-increment` at `run-conditions.json:9119`, `9296` and `9527`). No condition references them.
- **P7. The WBF verifier legs register on their source runs without conditions.**
  - The entries: `gold-standard-v2.wbf-verified-v1` (`run-conditions.json:13`), the two e47 `wbf-n5-*` entries (`:97`, `:102`), and the two pv-diag-384 `wbf-fh-*` entries (`:2356`, `:2361`).
  - None of these runs has a WBF condition. Registering passes without conditions is normal: passes carry spend and provenance, conditions carry metrics.
- **P8. Superseded but real legs that sit inside a registered run stay registered.**
  - `proposer-verifier-512` is "SIDELINED … superseded by the clean Era-1 Stage-D PV grid … Data kept" (`run-conditions.json:8861`, `8885`). It is still an `active` run with its verifier pass.
  - D22's ledger is for *re-executions or aborted attempts*. Its README says: "Executions whose results were superseded or that were aborted" (`data/pricing/superseded-executions.json`).
- **P9. A pilot that set a production default is registered as its own run.**
  - `verifier-t-pilot` (`run-registry.json:168`): "one run (verifier-temperature pilot, H2-exploratory …)".
  - Its decomposition note says it "revisits Phase 3d". In other words, the project re-ran the Phase 3d experiment at `era-2-487` rather than registering the 60-tile original.
- **P10. A deviation run is registered when live analyses use it.**
  - `consensus-384-t1-0` (E43; `historical_aliases` includes `consensus-384-UNINTENDED-T1.0`) is registered and used by analyses.
  - The E44 single-pass T = 1.0 sibling was archived, "not used in any published analysis" (`b9ec6b868`), and is not registered.
- **P11. Never registered:**
  - the retracted h10/h12 v1 probe;
  - `v2-verifier-contamination`;
  - `superseded-tests`;
  - the 60-tile H1–H9 runs (D38 class SUPERSEDED);
  - the Phase 3c pilot and the Phase 3d pilot, union, A–D and high-thinking experiments (no metas for their verifier legs; D39 residual);
  - `pilot-thinking`.

  A search of `run-registry.json`, `run-facts.json` and `run-analyses.json` for "retract", "quarantin", "pilot" and "superseded" finds nothing tying a run to any of them. In `run-conditions.json` the matches are rows about archived leaderboard files.
- **P12. An analysis row may compare zero conditions.** There are five `disposition` rows and `student-baseline-r2` (`run-analyses.json`).
- **Mechanics.**
  - The proposer extractor globs `run_*` only (`generate_post_run_report.py:666`).
  - A flat pool can declare `single_pass` (D31).
  - Both pools and verifier legs take `repo_path` (`_leg_root`, lines 565-604).
  - A verifier meta may be dir-form (`<path>/run.meta.json`) or a sidecar (lines 862-881).
  - A run with no conditions gets `run_type: null` (line 1406).

## 2. Group 1: `archive/outputs-pre-retest-60-tile/phase1-library/`

### 2a. What ran

- **Five image-only passes**, `pass_01` … `pass_05`, on 2026-02-01 from 05:55:20 to 06:03:13 UTC.
- **Model:** `gemini-3-flash-preview` (per-item `model_used`).
- **Runner:** `4_detect_mounds_batch.py` v5.0.1 at `d06eacd0e`.
- **Configuration:** `library_pure-positive-canon`, instruction `detect_image-only.md`, T = 1.0, thinking minimal. Seven examples: 4 Canon+ (01–04) and 3 null (15–17). Images were transmitted: 8,892 input tokens per tile.
- **Volume:** 20 tiles × 5 = 100 calls, with no failures.
- **Cost:** recorded US$0.096165; indicative standard US$0.4989 (survey `era1.json`).
- **The 20 tiles are the calibration set.** All 20 item ids in each pass are in `inputs/tiles/calibration_manifest.json` (20 entries). The bounds file is `inputs/vectors/bounds/calibration_bounds.geojson`, with 20 features.
- **It matches the registered protocol.** Prereg § 8.4.1 Step 1 (`docs/methodology/preregistration/osf/preregistration.md:1440-1447`) specifies an "Image-Only Baseline … 4 canonical positives + 3 null tiles … 5 × 20 training tiles = 100 API calls … T=1.0". The execution matches it exactly. `docs/methodology/preregistration/execution-checklist.md:108` records it as "Phase 1: Library + Text, 2026-02-01 → 02-03".
- **Its outputs:**
  - `merged_detections*.geojson`, `checkpoint.json` and `fp-fn-register.md`.
  - The FP/FN register was committed in `bc7ace196` and `3c835863d`; the passes in `92d3a95bc` ("F1 0.489 at vote 3 … Total cost: $0.096").
  - Archived in `276e4ca80` (2026-04-16). `archive/ARCHIVE-MANIFEST.md:71` says "→ superseded by `retest/phase2a`". That is wrong: nothing re-ran it.
- **What it selected** (`decisions-log.md` Decision 4, lines 113-197):
  - hard positives 05–08 (fids 399, 99, 15 and 105);
  - hard negatives 11–14;
  - in `6e772b55a`, the expanded hard-negative pool 18–29 used for H9-C rotation, taken "from the FP candidate pool".
  - The crops were extracted in `12898e947` and re-extracted at 128 × 128 in `f793ca7cb` (E8). They have not changed since `6e772b55a`, by `git log`.

### 2b. What depends on it today

- **The production libraries.**
  - All five `prompts/configs/library_plus-hp*.json` carry 05–08.
  - `detect_brief-text-image.json` (17 examples) carries 05–08 and 11–14.
  - The `phase3c-t1-h9C/E*` configs carry 18–29.
- **The runs that transmit them** (a sweep of live proposer metas by `version` and `include_example_images`):
  - `library_plus-hp` (image): `55maps-image-generalisation`, `pv-diag-384`, `n1-outstanding-384`, `n1-pro-rerun-384`, `retest-phase2c`, `-2e` and `-3a`.
  - `detect_brief-text-image`: `image-b-gs-2026-08-28`, `gemini37-image-gs-2026-09-01`, `gemini37-image-55map-2026-09-13` and `gemini3-image-55map-2026-09-16`.
  - Image H9 pools in `retest-phase3c`.
- **The text-only headline pipeline does not transmit them.** `detect_brief-text`, with `include_example_images: false`, transmits no examples (`scripts/4_detect_mounds_batch.py:943-945`). Its guideline 2 was nonetheless reworded from the hard-example analysis in `2d4631171` ("Change 1 — Occlusion", derived from HP 05–08).
- **Hypotheses.** H8's HP and HN are defined as "from Phase 1 image-only baseline" (`osf/preregistration.md:756-757`). H9-C rotates 18–29. H5 and H4 manipulate the HN and HP blocks.
- **The register.** Ten Era-1 runs plus `proposer-verifier-512` declare `calibration_set_id: "cal-20-512"` (`run-facts.json`). That is exactly the tile set these passes ran on, the analogue of `h10`'s `pool_160`.
- **The paper.**
  - `docs/paper/methods-draft.md:527-528`: "Examples are drawn from labelled calibration tiles in positive, negative, and null categories". It describes this step but cites no registered run.
  - Errata E2, E7, E8 and E15 document Phase 1.

### 2c. Closest precedents

- **P3, D41.** Archived mining passes, called "superseded or not needed" by the archive manifest, built a library a registered run uses. They were registered as a proposer pool through `repo_path`, with no condition.
- **P1, P5.** The Era-1 register has one run per execution-plan phase (`retest-phase2a` … `retest-phase3c`).

### 2d. Recommendation: (i) a new run `phase1-library`

The D41 test is met: the passes built hard examples that registered production runs still transmit, and nothing re-ran them. D41 hosted its mining passes in the one run that consumes them. Phase 1 has no single consumer: its library feeds every Era-1 run and every later image-modality run. It is also a registered protocol phase of its own. A dedicated run therefore follows both D41 and the phase-per-run shape.

**Registry entry:**

```json
{"run_id": "phase1-library",
 "directory_path": "archive/outputs-pre-retest-60-tile/phase1-library",
 "status": "active",
 "notes": "Registered library-construction step (prereg §8.4.1 Step 1; execution checklist 'Phase 1: Library + Text', 2026-02-01): image-only baseline (library_pure-positive-canon, 4 Canon+ + 3 null, detect_image-only.md, T=1.0, minimal), 5 passes x the 20 calibration tiles (cal-20-512) = 100 calls. Its FP/FN register (fp-fn-register.md) selected HP 05-08 and HN 11-14 (Decision 4) and the H9-C pool HN 18-29 (6e772b55a), which every image-modality library still transmits. Never re-run; archived in 276e4ca80 under a manifest line ('superseded by retest/phase2a') that D40 corrects. No condition: the calibration-set F1 is a selection diagnostic (D41 precedent). Passes are laid out pass_01..pass_05."}
```

On status: `active` matches all 43 rows. `h10` is also `active` although its mining pool is archived. Using `archived` would be the enum value's first use, so it is a convention for the PI to set rather than one to infer.

**Facts entry:**

```json
"phase1-library": {
 "primary_hypothesis": null,
 "also_informs": ["H8", "H9"],
 "purpose": "Library construction (prereg §8.4.1 Step 1): the image-only baseline whose calibration-tile failures were mined for the hard examples (HP 05-08, HN 11-14; HN 18-29 for H9-C) that the image-modality production libraries still carry.",
 "tile_size_px": 512,
 "corpus": "4-map-gs",
 "gt_reference": "curator",
 "scope": {"test_set_id": "cal-20-512",
           "bounds_path": "inputs/vectors/bounds/calibration_bounds.geojson",
           "n_test_tiles": 20, "calibration_set_id": null,
           "n_calibration_tiles": null},
 "headline_condition_id": null, "headline_rationale": null,
 "historical_aliases": ["Phase 1"],
 "_scope_confidence": "HIGH",
 "_scope_source": "empirical: each pass's 20 per_item_metadata item_ids = inputs/tiles/calibration_manifest.json (20/20); bounds file has 20 features",
 "_flags": ["construction run, not an evaluation: no condition; run_type stays null",
            "cal-20-512 used as a test_set_id for the first time: add a line to results/evaluation-scopes.md (§ 5.1 defines the set)"]
}
```

Two caveats on these fields:

- `gt_reference: "curator"` follows the 4-map convention. The reference vintage of 2026-02-01 predates the E87 standardisation (unverified).
- `also_informs` could instead be `[]`, with the consumers listed in `purpose`. The `library-design` programme names the Era-3 pool_160 axis, so it does not fit here.

**Decomposition entry.** The extractor globs `run_*`, so the pass directories need one of two forms:

- **Form A**, with no code change: five pools declared `single_pass` (`{"pass_01": {"modality": "image", "path": "pass_01", "single_pass": true}, …}`). This works, but it misrepresents one pool of five passes as five pools of one.
- **Form B**, recommended: a small extension in D41's style, with a test, letting a pool name its pass glob.

  ```json
  "phase1-library": {
   "_note": "Phase 1 library construction (prereg §8.4.1 Step 1). One image-only pool, 5 passes over the 20 calibration tiles; no condition (selection diagnostic only; D41 precedent). D40.",
   "proposer_pools": {"image-only-baseline": {"modality": "image", "path": ".", "pass_glob": "pass_*"}},
   "verifier_passes": {},
   "conditions": []
  }
  ```

  The existing suffix parse (`name.split("_",1)[1]`) turns `pass_01` into 1. The pass ids are `phase1-library::image-only-baseline::run1..5`.

**Alternative (ii):** a `repo_path` pool on `retest-phase2a`, the archive manifest's own pairing. I do not recommend it: `retest-phase2a`'s per-run cost would then carry the construction cost of every phase's library.

**Provenance gaps the registration closes or exposes:**

- The paper's methods sentence (`methods-draft.md:527`) gains a registered source.
- `decisions-log.md:115` and `:197` still cite `outputs/phase1-library/fp-fn-register.md`, a pre-archive path.
- `results/evaluation-scopes.md:91-94` says Phase 1 built "the canonical few-shot library (4 positive + 2 negative legend-derived examples, 3 null tiles)". It omits the hard examples, which are the step's actual product.

## 3. Group 2: Experiment E (`archive/outputs-pre-retest-60-tile/preliminary-results/`)

### 3a. What ran

- **Four text-only proposer passes**, one per configuration, each over the 60-tile holdout. The holdout bounds are `inputs/vectors/bounds/validation_bounds.geojson` (60 features), byte-identical to the archived copy.
- **When and how:** 2026-03-10, 11:04–12:07 UTC; `4_detect_mounds_batch.py` v6.0.0 at `866b9e0bb`; `gemini-3-flash-preview`.
- **The four arms:**

  | Arm | Config | Thinking | T | Examples in config | Thought tokens |
  |---|---|---|---:|---:|---:|
  | E1 | `detect_brief-text_high-recall` | HIGH | 0.7 | 10 | 220,534 |
  | E2 | `…_nulls` | HIGH | 0.7 | 13 | 228,484 |
  | E3 | `…_nulls-minimal` | minimal | 0.7 | 13 | 0 |
  | E4 | `…_nulls-minimal-t0` | minimal | 0.0 | 13 | 0 |

- **Cost:** recorded US$0.059171; indicative standard US$1.6905 (survey).
- **Commits:** `e252ef2f2` (2026-03-11, then under `outputs/results/`); archived in `276e4ca80`.
- **The verifier stage** was `scripts/run_experiment_e.py`, with `verify_adversarial.md` at T = 0.0.
  - Only the last run's outputs survive: `archive/outputs-pre-retest-60-tile/phase3d-experiment-e/`, holding E4's 151 candidates, `verifier_adversarial_probabilities.json` and `experiment_e_results.json`.
  - E1–E3's verifier outputs were overwritten (the results document lists the directory as "(last run)").
  - No verifier meta exists. The results document says "~US$3.00", and D39 already rules the Phase 3d verifier legs into the invoice residual.
- **The comparator is not registered either.** The "Baseline" (F1 0.796) is the Phase 3d pilot's text track: the 60-tile `phase2d/track2-text/minimal/run_1` proposer, with a verifier leg that left no meta. Both are unregistered.

### 3b. What depends on it today

- **The paper.**
  - `docs/paper/discussion-outline.md:293`: "Boundary: the recall ceiling is perceptual (Experiment E)".
  - `docs/paper/discussion-seeds.md:528-531` makes the same claim.
  - `:555-556` cites the "Obs 155 / Experiment E pattern" (reasoning as liberaliser).
- **Live files:** `results/phase3d-experiment-e-results.md` (hand-written; `reports/verification/apparatus/generator-map.json:61` `hw-phase3d`) and `docs/methodology/preregistration/hypothesis-tracking.md:97`.
- **Nothing else.** It is not in production configs, registered conditions or analyses, errata, or H-tests. Its conclusion was "keep the baseline".
- **Housekeeping:** the results document lists stale artefact paths (`outputs/results/…`) and carries no revision banner.

### 3c. Precedents

P9, P11 and P1:

- No 60-tile or Phase 3d experiment is registered.
- Where the project still needed a Phase 3d result, it ran it again at a registered scope. `verifier-t-pilot` is Phase 3d Experiment C again, at `era-2-487`. Stage D and the H11 PV runs did the same for the PV pilot.
- P8 does not apply: Experiment E was never part of a registered run.

### 3d. Recommendation: (iii) keep it out of the register

- **Keep the four metas in `data/pricing/archive-classification.json` as project-total spend, but do not label them SUPERSEDED.** By the D22 definition, SUPERSEDED means replaced or discarded, and nothing replaced Experiment E. A class such as `EXPLORATORY` ("unregistered exploratory execution; results cited in prose; not replaced") states the truth. Adding it needs a one-line change to the ledger README and to the builder's class list (not inspected).
- **Treat the paper citation as the real gap.** The discussion's "perceptual" boundary rests on one 60-tile run per arm, with no registered run behind it.
- **Options for the PI:**
  - (a) Re-run the prompt contrast at a registered scope as a new registered run, following the `verifier-t-pilot` precedent. This needs the phase gate and the API review gate, and has not been costed.
  - (b) Cite it as an unregistered 60-tile exploratory result, with archive pointers and an n = 1 caveat.
  - (c) Lean on registered evidence instead. R5-13 ("saturate Flash's recall ceiling", `results-draft.md:467`) is about pool saturation, not perception, so it does not replace the claim like for like.
- **Why registering it would not close the gap.** Registration would yield four single-pass pools (`single_pass`), at most one verified condition (E4, after an on-disk re-score that costs nothing), and no verifier row. The comparison the paper uses would still have an unregistered side, the Phase 3d pilot baseline.
- **Fallback (i), if the PI wants it registered anyway:**
  - `run_id` `phase3d-experiment-e`
  - `directory_path` `archive/outputs-pre-retest-60-tile/preliminary-results`
  - `status` `active`
  - new scope id `holdout-60-512`, bounds `inputs/vectors/bounds/validation_bounds.geojson`, 60 tiles
  - 4 pools, each `{"modality": "text", "path": "<config dir>", "single_pass": true}`
  - conditions only after a re-score; no verifier row (no meta).

### 3e. SURPRISE: Experiment E's example-count levers never reached the API

- **The evidence.**
  - All four metas record 100,320 input tokens, exactly 1,672 per tile, whether the configuration lists 10 or 13 examples.
  - The runner at `866b9e0bb` skips the example loop entirely for text-only configurations (`git show 866b9e0bb:scripts/4_detect_mounds_batch.py`, lines 752-753). This is Obs 235's mechanism again.
- **Two of the attributed effects are artefacts.**
  - "Restore null examples" (E1 → E2, +0.050 F1, 32 % of the attribution) is spurious.
  - "Restore hard negatives" (E4 → Baseline, +0.017) is spurious: that step changed only the prompt.
  - Finding 2 and Obs 156 ("null examples are structurally necessary") therefore rest on a manipulation that was never transmitted.
- **E1 and E2 form an accidental replicate.** They sent the same payload (same instruction, HIGH thinking, T = 0.7). Their verified F1 values, 0.640 and 0.690, differ by 0.050. That is larger than the HIGH → minimal step (+0.021) behind the discussion's "Obs 155 / Experiment E pattern".
- **Finding 4 survives**, but only as a single-run, 60-tile prompt contrast. E4 versus Baseline really is prompt-only.
- I found no paper citation of Finding 2.

## 4. Group 3: the legacy PV legs

### 4a. What ran

- **Seven PV Phase 1 legs** (2026-03-20; `run_pv.py`).
  - All verified the 882 candidates of `outputs/retest/phase2b/track2-text/T0.0/run_1` (`crops-150/text-n1-t0.0-minimal/candidate_manifest.json` `source_geojson`).
  - Crop size: 40, 75, 150 and 300 px, adversarial.
  - N = 5: adversarial 150, 4,410 requests.
  - Strategy: brief 150 and checklist 150.
  - Model `gemini-3-flash` (`gemini-3-flash-preview`), T = 0.0, minimal, `library_hash: no_examples`.
  - Recorded US$2.34444.
- **Six metered PV Phase 2 legs** (2026-03-21, real time).
  - Experiments 21–26 over 30-pass unions, recorded US$1.748148.
  - From the union file names: `3a-text-t0.7-{25,1}of30`, `3a-image-t0.7-{20,1}of30` and `3a-rep-high-{20,25}of30`. These map to `retest-phase3a` `track2-text-t0.7` and `track1-image-t0.7` (30 runs each) and to `retest-phase3a-replication` `high` (30 runs).
  - The mapping is inferred from names. The union GeoJSONs carry no source metadata (unverified).
- **Total for the 13 metered legs:** recorded US$4.092588. Archived in `276e4ca80`; `ARCHIVE-MANIFEST.md:99` says "superseded by `outputs/h11/proposer-verifier-384/`".
- **Experiments 02–20 ran on the Batch API.**
  - 19 job names in `archive/outputs-experimental-pilot/pv/results/phase2/batch_job_registry.json`.
  - Each `probabilities.json` has `"mode": "batch"`; 20,272 results in total.
  - No metas exist (see § 6).
  - Their crops are drawn from the `retest-phase2a`, `2b`, `2d`, `2e`, `3a`, `3a-high` and `3a-replication` pools.

### 4b. What depends on it today

- **`results/pv/`** is live and maintained: `phase1/pv-phase1-analysis.md` was revised on 2026-08-03 under E39. `results/ci-metadata-registry.md:105-106` lists the threshold sweeps.
- **Decisions.** `decisions-log.md` Decision 22 (evidence at `:1088`), Decision 23 (150 px crop, `:1113`), Decision 24 (single-pass verifier, `:1137`) and Decision 25 (moderate consensus, `:1163`).
- **Errata.** `protocol-errata.md:1097` E39, "Verifier strategy equivalence confirmed at production scale", whose Files field is `results/pv/phase1/*/threshold_sweep.json`.
- **The paper.** `methods-draft.md:370-376` describes the production verifier ("150 × 150 px crop … single pass … carried forward unchanged from its selection"). That selection is Decisions 23 and 24.
- **What was later re-tested on registered runs:**
  - strategy at 384 px (`pv-diag-384`);
  - n = 1 determinism (`verifier-robustness`);
  - six Era-1 PV cells (Stage D).
- **What was not:** the crop-size sweep. It exists only in these legs.

### 4c. Precedents

P5 (Stage D), P6 (D32), P7 (the WBF legs) and P8:

- Verifier legs over a registered run's pool register on that run through `repo_path`.
- A leg that was partly superseded stays registered when it is real spend within a registered scope (`proposer-verifier-512`).

### 4d. Recommendation: (ii) passes on the source runs

Add the following entries, all with `"modality": "text", "repo_path": "archive/outputs-experimental-pilot/pv/results"`:

- **On `retest-phase2b`:**

  ```json
  "legacy-pv-adv-text-crop40":   {"path": "adversarial-text-40/text-n1-t0.0-minimal"},
  "legacy-pv-adv-text-crop75":   {"path": "adversarial-text-75/text-n1-t0.0-minimal"},
  "legacy-pv-adv-text-crop150":  {"path": "adversarial-text-150/text-n1-t0.0-minimal"},
  "legacy-pv-adv-text-crop300":  {"path": "adversarial-text-300/text-n1-t0.0-minimal"},
  "legacy-pv-adv-text-crop150-n5-t0-7": {"path": "adversarial-text-150-n5-t0.7/text-n1-t0.0-minimal"},
  "legacy-pv-brief-text-crop150":     {"path": "brief-text-150/text-n1-t0.0-minimal"},
  "legacy-pv-checklist-text-crop150": {"path": "checklist-text-150/text-n1-t0.0-minimal"}
  ```

- **On `retest-phase3a`:**

  ```json
  "legacy-pv-text-t0-7-n30-25of30":  {"path": "phase2/21-text-25of30"},
  "legacy-pv-text-t0-7-n30-1of30":   {"path": "phase2/22-text-1of30"},
  "legacy-pv-image-t0-7-n30-20of30": {"path": "phase2/23-image-20of30"},
  "legacy-pv-image-t0-7-n30-1of30":  {"path": "phase2/24-image-1of30"}
  ```

- **On `retest-phase3a-replication`:**

  ```json
  "legacy-pv-high-n30-20of30": {"path": "phase2/25-high-20of30"},
  "legacy-pv-high-n30-25of30": {"path": "phase2/26-high-25of30"}
  ```

Notes:

- The metas are dir-form, so they resolve as `<path>/run.meta.json`.
- `modality: "text"` follows E88, because the exemplar list is empty.
- Reclassify the 13 ledger entries from SUPERSEDED to REAL, each with its `register_pass_id`.
- **No conditions now.** The sweeps sit on a 20 m-only instrument. Re-scoring Decisions 23–24 and E39 into registered conditions would cost nothing in API terms, but the bootstrap work must run on sapphire, so it is optional and for the PI to choose.

**Caveats for the extractor:**

- The N = 5 leg's meta records `configuration.temperature` 0.0. The directory name and `pv-phase1-analysis.md` say T = 0.7, and no `run.log` exists. This is E55-class: the leg needs `temperature_effective`, or the row will say 0.0.
- That meta's `completed_items` is empty, so its candidate count falls back to its request count, 4,410 (882 × 5).

## 5. Group 4: Obs 230 (`archive/h10-h12-v1-retracted-probe/`)

### 5a. What ran

- **Ten `pool_160_hp4hn4` proposer passes** (2026-04-11, 09:04–09:56 UTC; `detect_brief-text_pool_160_hp4hn4`, text-only, so the library was never sent). Recorded US$4.494243.
- **The hp4hn4 greedy-pipeline verifier** (`outputs/h10/verified/pool_160_hp4hn4/run.meta.json`, 2026-04-11). Recorded US$2.146406.
- **The variant-C WBF verifier** (`wbf/pool_160_hp4hn4_variant_c/verified/run.meta.json`). Its meta covers only a 1-candidate cleanup (US$0.001352). The main leg of 1,466 candidates left no meta, and D39 already places it in the residual.
- **The comparison:** `results/h10/wbf/variant_c_vs_greedy_hp4hn4.json`, which gives "+0.005, p = 0.602".
- **Twelve metas in all**, recorded US$6.642001. Moved to the archive in `524044767` (2026-04-23). The retraction is Obs 235 (`docs/notes/working-notes.md:9422`); Obs 230 is at `:8030`.

### 5b. What depends on it today

- **Decision 26 rationale 2** cites this data as its validation evidence (`decisions-log.md:1167-1190`).
- **`results/h10/analysis_summary.md:202-224`** keeps it "for archival record only".
- **`protocol-errata.md:1788-1789`** (E52) mentions "WBF variant C (Obs 228–230 parameters)".
- **The paper drafts do not use it.** `docs/paper/*.md` contains no mention of WBF or Obs 230; the skeleton reads "aggregation (greedy consensus primary)" (`manuscript-skeleton-isprs.md:50`). The archive README's claim that the result "is cited in the paper as Obs 230 evidence" is out of date.
- **The registered WBF conditions do not use its parameters.** In `h8-v2` and `h12-v2`, `wbf_diagnostics.json` records IoU 0.25, 60 m min-separation and no anchor. Obs 230's variant C was IoU 0.25, **30 m**, **anchor ≥ 6**, per the archive's `variant_c/wbf_diagnostics.json`.

### 5c. Precedents

P11 (the retracted probe as a whole: 56 SUPERSEDED metas; quarantined legs), P10, and D22's definition of superseded spend.

### 5d. Recommendation: (iii) keep the 12 metas SUPERSEDED in the archive ledger

- **Why:**
  - Registering them on `h10` would put a retracted, misconfigured study's spend into `h10`'s per-run cost, which D22 excludes.
  - No registered artefact or paper draft uses the data.
- **Gaps to note:**
  - Decision 26's validation evidence and E52's parameter attribution rest on retracted, unregistered data.
  - If the paper reinstates a greedy-versus-WBF robustness claim, it should cite a new registered comparison over the conditions that already exist: `h8-v2`'s seven greedy and WBF pairs, and `h12-v2`'s three. It should not cite Obs 230.
- **Fallback, only if the PI rules Obs 230 to be registered evidence:**
  - a new run, for example `h10-v1-probe-hp4hn4`, with `directory_path` `archive/h10-h12-v1-retracted-probe/outputs/h10`;
  - pool `{"modality": "text", "path": "evaluation/pool_160_hp4hn4"}`, with `run_1..10` dirs, which the extractor already handles;
  - verifier legs `verified/pool_160_hp4hn4` and `wbf/pool_160_hp4hn4_variant_c/verified`, both dir-form;
  - no condition unless re-scored.
  - There is no precedent for registering a retracted run.

## 6. Surprises and items for the caller

1. **Experiment E's example-count levers never reached the API** (§ 3e). The "null examples" finding (Obs 156) is an artefact. Its E1/E2 pair is an accidental replicate whose 0.050 spread exceeds the thinking effect the discussion seeds lean on.
2. **Phase 1 is a registered protocol step** (prereg § 8.4.1 Step 1, matched exactly), not a pilot. The archive manifest's "superseded by retest/phase2a" is wrong, and `evaluation-scopes.md` § 5.1 misdescribes what Phase 1 built.
3. **The legacy PV Batch legs 02–20 are unmetered spend that no ledger lists.** There are 19 jobs and 20,272 results from 2026-03-20/21, with no meta. Add them to D39's residual list. Meanwhile PV Phase 1, now classed SUPERSEDED, is the only evidence for the production crop size (Decision 23) and for E39.
4. **"WBF variant C" names two different parameter sets.** Obs 230's (30 m, anchor ≥ 6) is not the registered `h8-v2`/`h12-v2` variant C (60 m, unconditional merge). E52's "(Obs 228–230 parameters)" misdescribes the registered runs.
5. **The N = 5 legacy PV leg's meta says T = 0.0.** It actually ran at T = 0.7 (§ 4d).

## 7. Unverified

- That the legacy PV unions 21–26 come from `retest-phase3a` and `retest-phase3a-replication`. This is inferred from file names.
- The reference vintage behind `gt_reference` for Phase 1.
- How the generator treats `status: archived`. I read the code but did not run it.
- That nothing outside `docs/paper/` (for example a supplement held elsewhere) cites Obs 230. Only `docs/paper/` was searched.
- The ledger builder's class list, for adding `EXPLORATORY`. I did not inspect it.
- Indicative costs are the survey's figures and were not recomputed.
