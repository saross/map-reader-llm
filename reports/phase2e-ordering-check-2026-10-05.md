# W3 findings: did Phase 2e's example ordering reach the model?

> **Last revised**: 2026-10-05 (original publication, Session 160). See
> [§ Changelog](#changelog) for revision history.

**Status**: workstream W3 of `planning/text-track-transmission-2026-10-05.md`
(claim C-17), by a read-only Opus subagent of Session 160. The decisive
output comparison was spot-checked in session from the committed
detections (per-tile counts: Phase 2c `plus-hp` and Phase 2e
`canonical-first` equal on 338 of 338 tiles; against the other three arms
271-293 of 339-340). The scratch paths below are the investigation's own;
its drivers, replay output and comparison are kept as provenance in
`phase2e-ordering-check-2026-10-05-scripts/` (the `git archive` snapshot and
the transcripts are not: both are reproducible from commit `5a57f586e` and
the session archive).

Read-only investigation, 2026-10-05, for workstream W3 / claim C-17 of
`planning/text-track-transmission-2026-10-05.md`. Repository
`map-reader-llm`, branch `register-repair`. HEAD was `97d2afaf1` at the
start. Other sessions committed `9d9d2579f`..`3f144777e` locally and
pulled `eb6d797e0` on sapphire during this run; none of those commits
touches anything cited here. Nothing in either checkout was written,
staged or committed. No API call was made: the offline replay used a stub
client that refuses all I/O, and the proxy variables pointed at a dead
port.

Scratch artefacts are all in this directory:

- `code5a57/`: `git show` copies at `5a57f586e`.
- `sim/root/`: a `git archive` snapshot of `5a57f586e`, holding scripts,
  config, prompts, study YAMLs, example images and tiles.
- `sim/harness.py` and `sim/harness2.py`: the offline drivers.
- `sim/harness-output.txt`: the replay's printed output.
- `sim/replay-summary.json`: the decoded request bodies.
- `compare_outputs.py` and `compare-outputs.json`: the output comparison.
- `sessions/`: decompressed transcripts.

## Summary

1. **No record of what the March jobs sent survives.** All three copies
   of the requests were deleted: the local request JSONL (2026-03-18),
   the remote Files-API copies (deleted by the runner on completion), and
   the printed run logs (in `/tmp`, now gone). The metas cannot show
   ordering, by construction (W3.1).
2. **The offline replay of the recorded commit's own batch path produces
   four request bodies that differ only in example order** (W3.2). No
   skip condition applies to these configs. Two discrepancies:
   - **`canonical-last` order.** It was sent as `[null×3, HP×4, C+×4,
     C−×2]`, not the study YAML's `[HP, null, C+, C−]`.
   - **Phase 2c `plus-hp` image.** The retest's Phase 2c `plus-hp` image
     arm ran in canonical-first order, through a fixed-section setting
     that the batch runner had honoured since `ead94aa81`.
3. **The outputs corroborate transmission strongly** (W3.3):
   - **Identical requests at T = 0.** 36 pairs; 91–99 % of tiles have
     byte-identical detection sets.
   - **The six Phase 2e ordering pairs.** Only 0.6–5 % of tiles agree,
     the same as pairs with different example libraries.
   - **The one confirmed prediction.** The code says Phase 2c's image
     `plus-hp` request is byte-identical to Phase 2e's `canonical-first`.
     Those two outputs agree on 99.7 % of tiles and have identical
     board F1 (permutation p = 1.0, null SD 0).
   - **Against `config-default`.** `plus-hp` agrees with it on only 5 %
     of tiles. The report's § B.5 group 19 pairs `plus-hp` with
     `config-default`, so it has the wrong partner.
4. **Recommendation** (W3.4):
   - "Transmitted" is defensible and should cite the output evidence, not
     only "inferred from code".
   - The exact per-arm orders remain code-inferred.
   - A verification run is not needed for transmission. An optional
     fingerprint run (about $0.67) could pin the exact orders, if the
     model has not drifted.

## W3.1 Surviving records of what the batch jobs sent

| Source | Where | What it shows | Status |
|---|---|---|---|
| Request JSONL (the requests themselves) | Written on amd-tower to `outputs/retest/phase2e/<arm>/run_1/batch_working/detections_<arm>_run01.jsonl` (`5a57f586e:scripts/lib_batch_api.py:1291-1302`). Gitignored (`.gitignore:26`, `:65`) | Would show the order directly | **Deleted 2026-03-18 11:39:11 UTC** by `find outputs/retest/phase2e -name "batch_working" -type d -exec rm -rf {} +`. Source: session `2026-03-16T10-03_optimise-robust-tile-retry-and-design-batch`, cwd `/home/shawn/Code/map-reader-llm` (part of a cleanup of Phases 2a–2e and 3a). A second sweep on 2026-03-27 01:21 UTC deleted 319 `batch_working` dirs (session `2026-03-26T06-38_…`). Not present locally or on sapphire (only five unrelated `h11/pv-diag-384` dirs exist on each). rpi-server holds no repo copy at depth ≤ 5 under `/opt/encrypted/workspace`, `/mnt/qnap` and `/mnt/vantec`; a full-depth search timed out, so that machine is **partly unverified**. zbook was unreachable (no route to host): **unverified** |
| Files-API input and output files | Gemini Files API | Same content as above | Deleted by the runner after each job completed (`5a57f586e:scripts/run_phase2.py:1629-1655`). Any copy deletion missed would have auto-expired after 48 h. Batch job objects may persist server-side, but they no longer have a source file, and querying them would be an API call (not done) |
| `batch_jobs.json` | — | — | Did not exist in this era. The first references in the repo are September 2026 cost audits. Job names were held only in `checkpoint["batch_pending"]` and popped on completion (`run_phase2.py:1672`) |
| `outputs/retest/phase2e/checkpoint.json` (tracked) | repo | `completed` in the order canonical-first, config-default, canonical-last, random. `batch_pending: {}`, `last_updated` 2026-03-15T11:40:06 UTC | No ordering or job names |
| `outputs/retest/phase2e/study_manifest.json` (tracked) | repo | `generated` 11:19:03 UTC (overwritten by the `--resume` invocation). Lists all four conditions; `execution_order` is `["random/run_1"]` | No ordering field. Confirms random was a separate invocation |
| Four metas | `outputs/retest/phase2e/*/run_1/*.meta.json` | `script` `lib_batch_api.py` 1.4.0, `git_commit` `5a57f586e`. Meta write times 11:02:17 (canonical-first), 11:06:33 (config-default), 11:18:48 (canonical-last), 11:40:04 (random) UTC. Same `system_instruction_hash` `e169b7237b`, `library_hash` `3f7f028c2e…`, T 0.0, `minimal`; zero usage. `completed_items` iteration order is shared by the first three and different for random, consistent with two Python processes | **Cannot show ordering by construction.** `prepare_batch_unit` reloads the config file (`lib_batch_api.py:1281`), and the meta is written from that unreordered dict (`config=ctx.prompt_config`, `:1514`). The batch writer has no `ordering_override` field. Only the real-time path records one (`4_detect_mounds_batch.py:774`) |
| Run logs (stdout) | Claude Code background-task files `/tmp/claude-1000/-home-shawn-Code-map-reader-llm/f9bfb828-…/tasks/bey41htxo.output` (launch, 10:26:19 UTC, exit 2) and `bnm2f1aff.output` (resume, 11:19:02 UTC, exit 0) | Would contain `[i/4] <arm>/run_1 (ordering=…)` and `Reordered examples: …` lines | **Gone.** The session read only `grep -c "OK$"` → 3 and a 429 count → 1 from the first, and `tail -4` ("Failed: 0 units") from the second |
| Session transcripts | `~/cc-archives/map-reader-llm/2026-03-15T05-54_transition-map-reader-llm-study-to-340-tile/` (= `…/vlm-burial-mound-detection/2026-03-15T05-54_f9bfb828`, same 1,982,708-byte gz) | Launch command at 10:26:19 UTC (`run_phase2.py studies/retest/phase2e-h4-ordering.yaml --mode batch`). Random hit 429 at submission; "3/4 done, 1 rate-limited" at 11:19:01; resume at 11:19:02; "4/4" at 11:40:20. Phase 2e dry run at 07:15:10 (`tail -10` only). The same day's live output shows units carrying `ordering=canonical-first` into the batch preparation loop (2c-exploratory `pure-positive-2hp`, 2d `verbose`; lines ~1342, ~1356) | Strings `Overriding example ordering` (real-time path only): 0 hits. The `Reordered examples` and `_reorder_examples_for_batch` hits are code views, not run output. The reorder was written in session `2026-03-14T21-50_…` (02:31:27 UTC, commit `ead94aa81` at 02:33:11). It was dry-run there only for thinking-level propagation, never for ordering |
| Was the code on disk the recorded commit? | git and all archived sessions | No commit between `5a57f586e` (10:21:42 UTC) and the next script commit on 2026-03-16 (`aa099ad4f`). The only edit to the pipeline scripts after `ead94aa81` was 07:15:04 UTC (`fixed = config.get("fixed") or {}`), committed in `f06afb7ac`. `git diff ead94aa81 5a57f586e -- scripts/run_phase2.py` is exactly that plus E34's one line | Code at launch = `5a57f586e`. Edits made outside Claude Code would not appear in the archives: **unverified**, low risk |
| Study YAML | `studies/retest/phase2e-h4-ordering.yaml` (created `f06afb7ac`, unchanged since) | Factor `ordering`; level values `config-default` / `canonical-first` / `canonical-last` / `random`; `fixed: null`; `execution.random_seed_base: 42` | Matches the function's literals exactly |

## W3.2 The code path, run offline

**Method.**

- `sim/harness.py` imports the `5a57f586e` copy of `run_phase2.py` and
  calls the real `run_phase2(study, mode="batch", dry_run=True, limit=5)`.
- `google.genai.Client` is replaced by a stub. Its `models.list()` raises,
  which the runner catches (`run_phase2.py` ~1330). Every other attribute
  raises too.
- So the real Phase 1 loop runs and returns at `if dry_run or not
  contexts` (`:1508`), before any submission. That loop covers config
  load (`:1401`), examples (`:1449`), reorder (`:1454-1461`) and
  `prepare_batch_unit` → `build_jsonl_file` (`:1463`).
- **Inputs, all from `git archive 5a57f586e`:** the study YAML,
  `prompts/configs/library_plus-hp.json`, the system instructions,
  `inputs/examples/` (the `neutral-naming/` files are symlinks into
  `legend-positive/`, `hard-positive/`, `legend-negative/` and
  `null-tiles/`) and `inputs/tiles/`.

**Result.** The real code printed `Reordered examples: canonical-first`,
`… canonical-last` and `… random (seed=42)`; `config-default` is
correctly not reordered. It built four JSONLs. Decoded request bodies:

| Arm | Order of the 13 examples as sent | Categories |
|---|---|---|
| config-default | 01 02 03 04 05 06 07 08 09 10 15 16 17 | C+×4, HP×4, C−×2, null×3 |
| canonical-first | 01 02 03 04 09 10 05 06 07 08 15 16 17 | C+×4, C−×2, HP×4, null×3 |
| canonical-last | 15 16 17 05 06 07 08 01 02 03 04 09 10 | **null×3, HP×4**, C+×4, C−×2 |
| random (seed 42) | 08 07 03 10 17 06 16 09 04 05 01 02 15 | HP HP C+ C− null HP null C− C+ HP C+ C+ null |

The following hold across the four arms:

- **What is the same.** The multiset of 13 images and each image's label
  are identical, as are the system instruction (`e169b7237b`, matching
  the metas), the `generation_config` (T 0.0, `max_output_tokens` 8192,
  JSON, `thinking_level MINIMAL`) and the tile keys.
- **What differs.** Four distinct reference blocks.
- **Within each file.** All lines carry the same reference block.
- **So the bodies differ only in example order.** Token counts cannot
  show this, because a permutation has the same count.

**Skip conditions checked.** None applies to these four configs:

- **Reorder guard.** Ordering is skipped only if it is falsy, equals
  `config-default`, or the example list is empty (`:1454`). None applies.
- **Key and value mismatch.** The YAML factor is `ordering` and levels
  use `value` (`:244-247`). The four values equal the function's literals,
  and an unknown value would silently return the original order. No
  mismatch.
- **`fixed: null`.** This crashed the runner before 07:15 UTC
  (AttributeError, a crash not a skip). It was fixed by `or {}` (`:238`)
  before launch.
- **Unrecognised categories.** The batch mirror, unlike the real-time
  function, has no length check, so these would be silently dropped. All
  13 categories are recognised, and the replay sends 13 in every arm.
- **Missing example image.** This is silently skipped with a warning
  (`lib_batch_api.py:316-330`). It would affect all arms equally, not the
  order. All 13 files and their symlink targets exist at the commit.
  Whether any was missing on amd-tower on the day is unverified (zero
  usage recorded).
- **Exceptions.** None is swallowed around the reorder. A failure would
  have crashed the unit, not skipped the reorder.
- **Random seed.** It comes from `execution.random_seed_base` (`:875`) +
  (run − 1) = 42. The `--resume` that ran random regenerates the units
  from the YAML, so the seed is 42 again.
- **Retries.** Parse-failure sync retries use `ctx.examples`, the
  reordered list.

**Two discrepancies the replay exposes.**

1. **`canonical-last` order.**
   - **The batch mirror.** It returns `null + hard + canonical`
     (`run_phase2.py:103-109`).
   - **The real-time function.** It returns `non_canonical + canonical`,
     with hard and null in config order (`4_detect_mounds_batch.py:212-223`).
   - **The study YAML.** It describes the level as `[HP, null, C+, C−]`.
   - **What was sent.** The arm as sent put the three null tiles first.
   - **The registration.** `osf/preregistration.md:534-566` and
     `:1554-1558` fix only the canonical placement ("hard examples in
     initial positions, legend-derived symbols last"), and that placement
     holds (canonical at positions 8–13 vs 1–6).
   - This is a labelling point.
2. **The retest's prior phases ran in canonical-first order, not config
   order.**
   - **The YAMLs.** `studies/retest/phase2b-h7-temperature.yaml:48-49`,
     `phase2c-h8-library.yaml:89-90`,
     `phase2c-exploratory-pure-positive-hp.yaml:56-57` and
     `phase2d-h5-negtext.yaml:51-52` all set `fixed: ordering:
     canonical-first`, per `execution-plan.md:266-337`.
   - **The code.** `ead94aa81` made the runner honour `fixed.ordering`
     (`run_phase2.py:244-247`).
   - **The replay.** Of `phase2c-h8-library.yaml` (`plus-hp`), it prints
     `Reordered examples: canonical-first` and builds request bodies
     byte-identical to Phase 2e `canonical-first` (SHA-256 prefix
     `79c9eb3c027faf0f` for both, over five tiles).
   - **The February 60-tile programme.** It ran on the real-time path,
     whose metas record `ordering_override` when one is set. Its 2b, 2c
     and 2d metas carry none, so it ran in config order. Its 2e metas
     carry `canonical-first` etc.
   - **Consequences.** Phase 2e's "config-default … baseline used in all
     prior phases" held in February but not in the retest. "reused from
     Phase 2c" is wrong twice: 2e was re-run, and 2c used canonical-first.
     No erratum records the change: E34 (`protocol-errata.md:864-893`)
     covers only `thinking_level`, and I searched only `protocol-errata.md`
     and `decisions-log.md`.
   - **Status.** Outside W3's scope; flagged for W1.

## W3.3 Corroboration from outputs

The statistic is per-tile output identity: the share of commonly
processed tiles whose detection sets (box coordinates rounded to 0.1 m,
sorted) are byte-identical. I also report box overlap, the share of boxes
shared exactly. Source GeoJSONs are under `outputs/retest/`; the script is
`compare_outputs.py`.

| Pair set | Pairs | Exact-tile agreement | Box overlap |
|---|---:|---|---|
| Identical requests, image, 17 ex (2b T0.0 runs 1–3 + 2c scale-8) | 6 | 0.932–0.994 | 0.954–0.995 |
| Identical requests, image, 7 ex (2c vs exploratory pure-positive-canon) | 1 | 0.991 | 0.986 |
| Identical requests, text (2b text T0.0 runs 1–3 + five 2c text arms) | 28 | 0.914–0.938 | 0.892–0.945 |
| **2c image `plus-hp` vs 2e `canonical-first`** (identical under the code) | 1 | **0.997** | **0.991** |
| 2c image `plus-hp` vs 2e `config-default` (the report's § B.5 group 19) | 1 | 0.050 | 0.071 |
| **Phase 2e ordering arms, all pairs** | 6 | **0.006–0.050** | **0.010–0.071** |
| Different libraries, same order rule (2c image) | 4 | 0.018–0.033 | 0.026–0.050 |

**Timing does not explain the pattern.** 2e `canonical-first` (meta
11:02 UTC) and 2c `plus-hp` (11:16) agree almost perfectly. 2e
`config-default` (11:06), between them in time, agrees with neither.
Replicates up to 50 minutes apart agree at ≥ 0.93.

**Era-1 board** (`results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.json`):

- **The replicate pair.** `retest-phase2c::image-plus-hp` and
  `retest-phase2e::canonical-first` have identical F1 (0.598473) and MCC
  (0.0942), with permutation p = 1.0 and null SD 0, so identical per-tile
  scores.
- **The T = 0 image replicates.** Their F1 differ by ≤ 0.002 (scale-8
  0.5867 vs 2b T0.0 0.5862; pure-positive-canon 0.5699 vs 0.5678).
- **The ordering arms.** They span 0.5706–0.6314.

**What this can show.**

- **The four 2e requests were not identical.**
  - **Calibrated against replicates.** At T = 0 this pipeline is
    near-deterministic: ≥ 0.914 exact-tile agreement across 36
    identical-request pairs. The arms sit 20–150× below that, inside the
    different-library range.
  - **Rules out the null.** The hypothesis "no ordering reached the
    model" predicts all five plus-hp runs (four 2e arms and 2c plus-hp)
    to be mutual replicates. It is refuted.
  - **A specific prediction confirmed.** The code predicted the single
    match (2c plus-hp ≡ 2e canonical-first), and it is observed.
  - **Only the order can explain it.** The replay shows nothing else
    differs between the arms (instruction, generation config, images,
    labels and tiles).
- **The fixed-section reorder ran live on 2026-03-15.** It goes through
  the same function and loop as the factor-level reorder.

**What it cannot show.**

- **The exact order in each arm.** Outputs fingerprint a request but do
  not decode it. In particular they cannot show that canonical-last was
  `[null, HP, C+, C−]` or that random used the seed-42 shuffle. Those
  rest on the code replay.
- **That a reorder is the only possible cause in general.** Different
  outputs alone cannot prove different inputs; the argument rests on the
  T = 0 replicate calibration, which comes from the same day, model,
  path and corpus.
- **Anything about the size or reality of an ordering effect.** That is
  W2's and the H4 test's question.

## W3.4 Recommendation (for the PI to decide)

1. **The claim of transmission is defensible.** I would strengthen it,
   not hedge it. Basis:
   - **Code.** The recorded commit was on disk at launch.
   - **Replay.** It reproduces four distinct bodies.
   - **Outputs.** They fingerprint four distinct requests, with one
     predicted replicate confirmed.
   - **Remaining uncertainty.** The exact order per arm (code-inferred).
     Whether anything differed from the commit in the working tree
     outside Claude Code is unverified, but nothing indicates it.
2. **Suggested paper wording.**
   - **Methods or provenance note:** "The ordering manipulation is not
     recorded in the run metadata (the batch path recorded the configuration
     file, not the reordered list). Replaying the recorded commit's request
     builder offline gives four requests that differ only in example order,
     and the four arms' outputs differ from one another as much as runs with
     different example libraries do (≤ 5 % of tiles identical, against ≥ 91 %
     for identical requests at T = 0); the canonical-first arm reproduces,
     tile for tile, a Phase 2c run whose request the replay shows to be
     byte-identical."
   - **`results-draft.md:194-196`.** The sentence can stand
     ("`canonical-last`, F1 0.631" leads numerically on the board's own
     permutation instrument). Make it single-run and Tier-1-shared, and
     describe canonical-last as sent: "null examples, then hard positives,
     then canonical examples last".
   - **R2-02.** The claims-inventory row's evidence pointer could add this
     W3 note.
   - **Retest summary.** Drop "baseline used in all prior phases" and
     "reused from Phase 2c" (§ W3.2 discrepancy 2).
3. **H4 numbers from the retest-era pairwise bootstrap** (W2 owns them;
   `results/retest/pairwise-bootstrap-comparisons.json`):

   | `comparisons[i]` | Contrast | p | Where it appears |
   |---|---|---:|---|
   | `[55]` | canonical-first vs canonical-last | 0.124 | H4's confirmatory input (`family-bh-fdr-confirmatory` → `results/family-fdr/family_fdr.json`; `reports/verification/family-fdr-registration.md` § 5.4); `retest-production-summary.md:145` |
   | `[56]` | canonical-first vs config-default | 0.678 | — |
   | `[57]` | canonical-first vs random | 0.138 | — |
   | `[58]` | canonical-last vs config-default | 0.158 | `retest-production-summary.md:145` |
   | `[59]` | canonical-last > random | 0.002 | `retest-production-summary.md:25`, `:145`, `:250`, `:300` |
   | `[60]` | config-default > random | 0.046 ("significant") | `retest-production-summary.md:145`, `:251` |

   - **The CI [0.587, 0.672].** It is in `retest-production-summary.md:25`,
     `:140`, `:320` and `:337`, and comes from the retest-era analysis; its method
     was not checked here (unverified).
   - **For W2 only, read from the committed board artefact, not
     recomputed.** The board's paired permutation gives 0.1366, 0.6401,
     0.1218, 0.1857, 0.0019 and 0.0563 for the same six pairs. H4's
     primary is null on both instruments.
   - **Not robust: `config-default > random`.** It is not significant on
     the board (0.0563, BH 0.136).
   - **The `results-draft.md:194-196` sentence.** Its numbers (F1 0.631,
     MCC 0.213, 227/630) come from the board, not from the retest
     bootstrap.
4. **Corrections the report needs** (`reports/manipulation-check-2026-10-05.md`):
   - **§ B.2.** Status "Unverified from metas" → "transmitted: code replay
     and output fingerprint (W3)".
   - **§ B.5 group 19.** It should read `retest-phase2c::track1-image-plus-hp
     ≡ retest-phase2e::canonical-first`, not `::config-default`.
   - **The Era-1 counts.** The 26 distinct configurations, and 9 in
     Tier 1, are unchanged, because the duplicate swaps partner within
     Tier 1. The "23 (7) if Phase 2e's orderings did not transmit"
     alternative is refuted.
   - **C-04's parenthetical** in the tracker likewise.
5. **A GS verification run is not needed for transmission.** A new run
   cannot attest to what the March jobs sent. Only one design adds
   information, a **fingerprint replay**, which would pin the exact orders
   (chiefly canonical-last's):
   - **Requests.** Submit the offline-rebuilt `5a57f586e` JSONLs (this
     harness, without `--limit` trimming) for the four arms on a subset of
     the **same Era-1 340 tiles**. Another GS tile set breaks the
     fingerprint.
   - **Settings.** Batch API, T = 0, the March model (`gemini-3-flash`,
     resolved to `-preview`; whether it is still served unchanged is
     unverified).
   - **Expected result.** ≥ 0.91 exact-tile agreement with the matching
     March arm and ≤ 0.05 with the others.
   - **Drift risk.** It is uninformative if the model has drifted since
     March, since the replicate baseline is same-day only. If no arm
     matches, read that as drift, not as non-transmission.
   - **Minimal design.**
     - **Size.** 4 arms × 40 tiles = 160 requests (four batch jobs).
     - **Tokens.** About 2.51 M input (15,659 per request, report § A
       token law) plus about 24 k output (about 150 per request at
       MINIMAL; estimate).
     - **Cost.** About **$0.67** at the batch rates in
       `data/pricing/gemini-rate-card.json` ($0.25 per M input, $1.50
       per M output).
   - **Full 340 tiles.** 1,360 requests, about 21.3 M input tokens, about
     **$5.6**.
   - **Gate.** Either needs the PI's approval under the API gate, and D10
     applies. My recommendation is that it is optional, and worth it only
     if the paper names canonical-last's exact sequence.

## Noticed, not investigated

- **Tile-level MCC collisions on the board.** canonical-last and
  config-default share 0.2132; 0.0942 recurs across five cells. This is
  plausible for a coarse presence-level MCC. Not checked.
- **"Perfectly deterministic" at T = 0.** E31 and E32 (`protocol-errata.md:792-823`)
  say T = 0 is perfectly deterministic. On the March batch path,
  identical requests agree on 91–99 % of tiles, not 100 %.

## Changelog

### 2026-10-05 — Original publication (Session 160)

Commissioned to settle whether the H4 ordering manipulation reached the model
(the manipulation check had found it unrecorded in every meta).
