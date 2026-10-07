# Manipulation-gate coverage: binding derived products to their stages

Date: 2026-10-06. Branch `gate-coverage-2026-10-06` (from `origin/main` at
`51b49deca`, PR #24 merged).

## 1. Inventory (baseline, before any code change)

Baseline sweep: `python3 scripts/check_manipulation.py --all --report --json`
run on sapphire from a read-only copy of `origin/main`'s `scripts/` and
`results/` under `/tmp/gate-coverage/base/` (outputs, archive, prompts,
inputs and reports symlinked read-only to `~/Code/map-reader-llm`; git read
through `GIT_DIR`). Result: **71 analyses: 30 PASS, 5 REFUSE (all KNOWN),
36 UNVERIFIABLE**, exit 3. Of the 36: 21 are unverifiable only through
pairs whose verifier half is DECLARED, 7 only through arms with no proposer
meta, 8 through both.

628 distinct registered arms are judged. Two populations cannot be resolved:

### 1.1 Arms with no proposer meta: 43 (cause: the register's pool key reaches no pass)

| Cause | Arms | Conditions |
| --- | ---: | --- |
| Pool key is a derived union/consensus key, not a registered pool (`image-1of10`, `flash-high-text-1of10`, `flash-high-text-consensus-16of30`, `flash-minimal-text-t07-1of5`, `text-min-t07-true-1of5`, `flash-high-text-t03-1of5`) | 12 | `pv-diag-384::verified-adv-*` (6 cells and their `-era2b` twins) |
| Same, in a run that registers no proposer pool (`text-1of5`, `flash-high-text-consensus-16of30`) | 4 | `verifier-robustness::verified-256-*`, `verified-384-16of30-*` |
| Pool's registered path is a consensus FILE, not a pass directory (`f3-min-text-1of10`) | 2 | `flash35-pv-2x2::f3prop-f35vf-6of10[-era2b]` |
| Prompt-level key spanning four geometry pools (`brief-text`; deliberately not name-matched) | 6 | `grid-2026-08-18::g384-ov192-*` (k-ladder and verified37 cells) |
| Run registers no proposer pool at all | 4 | `pv-diag-256::{text-baseline,text-consensus-5of5,verified-adv-text-consensus-5of5}`, `proposer-verifier-512::verified-adversarial-text` |
| Arm absent from the run's pools (only arms B and C registered) | 2 | `h13::arm-a-{native,overlap}-12-5` |
| Era-1 stage-D re-use of retest passes under another key | 4 | `retest-phase2b::verified-adv-{image,text}-t0.0`, `retest-phase3a::verified-adv-image-t0.7-n30-18of30`, `retest-phase3a-high::verified-adv-text-high-t1.0-n30-23of30` |
| Diversity union of five registered pools | 9 | `retest-phase3c::{image,text}-h9-*-diversity-*` |

### 1.2 Arms whose verifier half is only DECLARED: 298 (cause: derived detections)

Every one has the same gate reason: "no registered stage contains the
condition's detections or prefixes its label". The detections are derived
products outside every stage directory. By product family:

| Product family (registered `detections`) | Arms | Derivation kind |
| --- | ---: | --- |
| `results/k-ladder-2026-09-12/phase2/materialised/*` | 46 | K-ladder rungs / operating points materialised from verified probabilities |
| `results/verifier-robustness/{sweep,condition,matrix,min-thinking,opmax}-sets/*`, `pareto/*` | 70 | thresholded verified sets (vote x probability) |
| `results/55map-final-board{,-r2}-*/cells/*` | 41 | oracle / carried operating-point cells, re-scored against standardised and r2 references |
| `results/gemini37-image-55map-2026-09-13/cells/*`, `results/gemini3-image-55map-2026-09-16/cells/*` | 36 | carried / F1-oracle / MCC-oracle cells per arm and K |
| `archive/superseded-leaderboards/leaderboard/era2/pv-materialised/*` | 34 | archived Era-2 opmax materialisations |
| `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/**` | 11 | Era-2 board opmax materialisations (incl. a staleness current-vintage set) |
| `results/{stride-2026-08-25,grid-2026-08-18}/conditions-verified/*` | 13 | per-geometry verified sets at the sweep argmax |
| `results/k-ladder-2026-09-12/tier-e/materialised/*` | 4 | tier-E rungs of the grid's g384_ov192 ladder |
| GS `verified_best_20m.geojson` products (`gemini37-screen`, `gemini38-screen/armV`, `gemini37-image-gs`, `image-b-gs`, `gemini37-fourth-cell/gs-leg`) | 18 | best operating point of a stage's sweep |
| 55-map `primary/` and `oracle/verified_detections.geojson` (`stride55-2026-08-27`, `gemini37-55map-2026-08-31`, `gemini37-fourth-cell/55map`) | 10 | carried / oracle products of a stage |
| `results/flash35-2x2/best-op-sets/*` | 6 | best operating point per proposer x verifier cell |
| `outputs/era1-pv-stage-d/*` accepted sets | 4 | Era-1 stage-D accepted sets beside `pass_N/verified` |
| `results/55map-leaderboard/min11-uplift-5of10-pt0.15.geojson` | 3 | one product re-scored against three references |
| `outputs/verifier-t-pilot/T0.0/materialised/*` | 2 | T0.0 leg of the verifier-temperature pilot (no T0.0 stage registered) |

### 1.3 Other causes the brief named

- **Non-meta files cited as metas.** The passes manifest cites
  `results/run-conditions.json` for 21 passes (12 `n1-pro-rerun-384`, 8
  `n1-outstanding-384`, 1 `retest-phase2b`) and `run.log` for 2
  (`verifier-t-pilot` T0.5, T1.0). The gate read the register as a proposer
  meta and added an all-empty signature entry to 30 arms (no verdict
  effect); `run.log` was already rejected. Fixed (section 3).
- **Gzipped / sidecar / archived metas.** No arm failed on these at
  baseline: the gzipped meta is read since PR #24 (finding 6), and every
  registered stage resolves through the W4.4 resolver (247 of 248 stages
  have passes-manifest source files).

## 2. What was resolved, and how

**PR:** <https://github.com/saross/map-reader-llm/pull/25>, branch
`gate-coverage-2026-10-06`, open and not merged. The branch has three
commits on `51b49deca`.

1. **`32178f74a` `feat(scripts)`: follow reviewed bindings in the gate.**
   - `scripts/check_manipulation.py` loads
     `results/manipulation-gate-bindings.json` (`BINDINGS`, schema
     `manipulation-gate-bindings/1`). It consults an entry **only** where
     the register's own routes leave a half unresolved. The register's
     routes are passes manifest, pool directory, `source_run`, detections
     path, sole pool, the stage's detections path, and its label.
   - Sources are followed mechanically:
     - `verifier_metas_for_source`: first the registered stage whose
       candidate directory contains the source (`stages_containing`;
       longest match; any run). Its metas come from `stage_metas`, which
       is the passes manifest, then W4.4's
       `dcm.resolve_verifier_stage`. Failing that, the verify metas in an
       existing source directory, or beside an existing file. A missing
       path is never widened to its parent. Last, `dcm.git_renamed_to`.
     - `proposer_metas_for_source`: the passes-manifest source metas under
       the path (excluding `verified/` and `crops/` subtrees and verifier
       metas), then the proposer metas on disk, then a git rename.
   - W4.4's resolver is reused (`stage_path_candidates`,
     `resolve_verifier_stage`, `_metas_under`, `git_renamed_to`,
     `read_meta`), not duplicated.
   - `validate_bindings` names every problem:
     - schema;
     - unregistered condition;
     - a condition bound twice;
     - a condition's registered detections not among the entry's
       `detections` (drift guard);
     - no sources;
     - non-relative paths;
     - no derivation, or no script or document;
     - verifier sources on a single-pass condition.

     Any problem raises `BindingError`, and `main` exits 1.
   - Reporting: each arm carries `binding`, `binding_notes`, and the route
     strings `binding:<id>:...`. The text report adds a "resolved through
     reviewed bindings" note and a `BINDING GAP` line for any dead source.
   - With no bindings file, all 71 verdicts and all signatures are
     identical to baseline (checked on sapphire).
2. **`5b8acdcaa` `fix(scripts)`: stop reading non-metas as pass metas.**
   - `lib_manipulation_signature.harvest_meta` records
     `has_configuration`.
   - `check_manipulation.meta_record` marks a document with no
     `configuration` block unreadable ("no configuration block: not a pass
     meta").
   - Effect: 30 arms lose an all-empty signature entry; no verdict
     changes.
3. **`8cc5b3078` `feat(results)`: bind 314 derived arms to their stages.**
   This is the bindings file (section 3) plus a tier-2 test that pins it to
   the register.

**Resolution by provenance.** Six read-only investigations (Opus
subagents, one per family of products) traced each product's documented
derivation: the builder script lines, logs, commit history, and sapphire
outputs. They were told that a label resembling a stage key is not
evidence. Most also reproduced the binding against the data:

- **Stream B:** all 36 image cells were reproduced feature by feature from
  the bound stage.
- **Stream A:** products carrying `candidate_id` match the bound stage's
  probabilities at 100 %, against about 6 % for the sibling stage.
- **Stream C:** each product was re-thresholded or joined against its
  named stage, with a control stage that fails.
- **Stream D:**
  - Phase-2 rungs were bound from `operating-points.json`.
  - The archived April products are bound by the committed registry and a
    count match.
- **Stream E:** sweep-set feature counts equal the recorded `n_accepted`.
  Vote-band copies are value-identical to their source stage (3,736 of
  3,736 values).
- **Stream F:** the phase 3c products record `contributing_passes`. The
  pv-diag-256 unions reproduce exactly from the archived passes.

I mechanically checked every entry:

- every condition registered, needing the bound half, and bound once;
- registered detections listed;
- each verifier source mapping to a registered stage, and that stage equal
  to the one the investigation named;
- each product commit present in `git log --follow` of the product: all
  match, with archived products showing their move commit `b69d8af4b`.

On sapphire, every source resolves to metas, with no `BINDING GAP`. A
crude size check (product features ≤ stage dispatch) flagged only stages
whose surviving meta covers a cleanup leg (section 6), plus the two
Stage-D per-pass directories, whose candidate ids repeat across passes.

Normalisations made when assembling the file:

- A proposer source given as a pass's `detections*.geojson` became its
  pass directory.
- A text annotation on one source path moved to that entry's caveats.
- Where the derivation read a derived copy of another stage (a vote-band
  or duplicate-format directory, with no meta of its own), the binding
  names the stage that SENT the requests and records the read path in
  `evidence.read_path`. There are three such entries:
  `cset-medium-vf-4of5`, `matrix-high-T0.0` and
  `stage-d-384-headline-16of30`.
- Only the half a condition lacked at baseline is bound; the register's
  own routes outrank any binding.
- One investigation could not bind the proposer of the two
  `verifier-robustness` 256 px conditions. Another found their passes:
  `archive/outputs-non-production-tile-sizes/text-n5/text-t0.7/run_1..5`,
  moved by `276e4ca80`. An exact in-memory reproduction gives
  2558/1909/1645/1423/1165 clusters, matching the feature counts of
  `text-1of5` … `text-5of5` (`text-ge3of5` = 1,645). I bound them with
  that evidence, recorded in `evidence.proposer_binding`.

## 3. The bindings file

`results/manipulation-gate-bindings.json`: **181 entries, 314 conditions**
(298 verifier halves, 42 proposer halves, 26 conditions both). Fields per
entry:

- `id`, `conditions`, `detections`;
- `verifier_sources` with `resolves_to`, and/or `proposer_sources`;
- `evidence`: `derivation`, `script` (file:lines), `product_commit`,
  `documents`, and optionally `chain`, `read_path` and
  `proposer_binding`;
- `meta_beside_source` and `caveats`.

Every verifier source lies in a registered stage; none needed
`unregistered_stage`. The appendix lists every entry with its stage, its
first script reference and its product commit. The full evidence is in the
file.

Proposer bindings added (42 conditions):

| Family | Conditions | Proposer sources (passes) | Key evidence |
| --- | ---: | --- | --- |
| retest-phase3c diversity unions | 9 | `outputs/retest/phase3c/track{1-image,2-text}/h9-<L>-*` (5 sub-condition pools; run_k of each) | `scripts/materialise_phase3c_consensus.py:124-151`; study YAML `consensus_design`; products' `contributing_passes`; `fca7f888b` |
| h13 arm A | 2 | `outputs/retest/phase2a/brief-text/run_{1,2,3}` | `scripts/prepare_h13_scoring.py:120-131, 459-474`; `faff43dd4` |
| Era-1 stage D (phase2b, 3a, 3a-high, 256) | 5 | `track{1-image,2-text}/T0.0/run_{1..3}`; all 30 passes of `track1-image/T0.7` and `track2-text/T1.0`; the archived 256 px N = 5 passes | `scripts/run_era1_pv_stage_d.py`, `planning/era1-pv-stage-d-cells.json`, `full-run.log`; `7d6c46672` |
| pv-diag-256 unions and baseline | 2 | archived `text-n5/text-t0.7/run_1..5`; `text-baseline/text-t0.0/run_1` | sha256 identity (baseline); exact union reproduction; `276e4ca80` |
| grid g384_ov192 k-ladder and verified37 | 6 | `outputs/grid-2026-08-18/g384_ov192/run_1..K` (K = 1, 3, 5); all ten passes plus the three recovery fragments (verified37) | `run_k_ladder_tier_e.py` (`consensus-nK/voting_summary.json`); `grid_prepare_scoring`. Tier-E K = 5 excludes `run_4_recovery`, as the product did |
| pv-diag-384 union arms | 12 | `image-n5/image-t0.7/run_1..10`, `flash-high-text-n5/text-t0.7/run_1..10` and `run_1..30`, `flash-minimal-text-n30-t07/text-t0.7/run_1..5`, `text-n10/text-t0.7/run_1..5`, `flash-high-text-n5/text-t0.3/run_1..5` | 4 by recorded command; 8 documentary only (no committed merge command for the March unions; bound through the sweep registry, the session-59 plan and the unions' `contributing_passes`) |
| verifier-robustness 256 and 16of30 | 4 | archived 256 px N = 5 passes; `flash-high-text-n5/text-t0.7/run_1..30` | as above |
| flash35 f3 proposer | 2 | `outputs/h11/pv-diag-384/text-n10/text-t0.7/run_1..10` | `finish_flash35_tranche.sh:24,48-55` (`merge_passes.py`); `tranche-full.log:8783-8790` |

## 4. Before and after

Full register, sapphire, complete outputs. Before is `origin/main`
`51b49deca`; after is this branch. Both ran from read-only copies under
`/tmp/gate-coverage/{base,after}`.

| | PASS | REFUSE, all pairs KNOWN | REFUSE with a NEW pair | UNVERIFIABLE | `--all` exit |
| --- | ---: | ---: | ---: | ---: | ---: |
| Before | 30 | 5 | 0 | 36 | 3 |
| After | 66 | 2 | 3 | 0 | 2 |

**Verdict transitions:**

- UNVERIFIABLE → PASS: 36.
- PASS → PASS: 30.
- REFUSE → REFUSE: 5. The KNOWN pairs are unchanged. Three of these
  analyses gained NEW pairs: `era1-leaderboard` 16 → 22 null pairs,
  `null-exemplar-sensitivity-2026-09-13` 16 → 22, and
  `uplift-supplement-flatten` 23 → 29.
- No previously unverifiable analysis became a refusal.

**Arms** (628 distinct registered arms):

- 359 proposer-verifier arms, all with a TRANSMITTED verifier half;
  DECLARED halves went from 298 to 0.
- Arms with no proposer meta went from 43 to 1.
- 314 arms are resolved through bindings.

**False-PASS check.** Could a partial meta create a false PASS? No pair
with a bound arm is separated only by its `verifier-inputs` fingerprint.
The 18 pairs separated only by inputs fingerprints are all cross-tile-size
comparisons: 384 px Era-2 or 256 px against 512 px Era-1. There the
proposer inputs genuinely differ, and tile size is unrecorded (W7.2).

## 5. NEW refusals (in full; not allow-listed)

The same six NEW null pairs appear in each of `era1-leaderboard`,
`null-exemplar-sensitivity-2026-09-13` and `uplift-supplement-flatten`.
One side of every pair is `retest-phase3c::text-h9-a-diversity-4of5`
(binding `phase3c-text-a-diversity-union`: 25 metas, `h9-A-p1..p5` ×
`run_1..5`). The other side is one of:

1. `retest-phase3a-high::text-high-t0.7-n5-4of5`
2. `retest-phase3a-high::text-high-t0.7-n10-7of10`
3. `retest-phase3a-high::text-high-t0.7-n30-22of30`
4. `retest-phase3a-replication::text-high-t0.7-n5-4of5`
5. `retest-phase3a-replication::text-high-t0.7-n10-8of10`
6. `retest-phase3a-replication::text-high-t0.7-n30-21of30`

The 3a arms have 30 metas each, bound through the passes manifest.

**Configuration fields that differ:** `instruction_file` and `version`.

| | `instruction_file` | `version` |
| --- | --- | --- |
| Phase 3c H9-A arm | `detect_brief-text-image.md` | `phase3c-t2-h9A` |
| Phase 3a arms | `detect_brief-text.md` | `detect_brief-text-high` |

**Shared transmitted signature (identical on both sides):**

```text
{"stage": "proposer", "model": "gemini-3-flash-preview", "temperature_eff": 0.7,
 "thinking": "high", "sys_hash": "e169b7237b85", "examples_sent": "none",
 "tile_size": null, "max_output_tokens": 8192}
{"stage": "proposer-inputs", "inputs": "5e34ccde33ff/340"}
```

Every field matched: stage, model, effective temperature, thinking,
system-instruction hash, examples sent (none), tile size (unrecorded on
both), output budget, and the 340 dispatched tiles.

**Why.**

- `prompts/system-instructions/detect_brief-text.md` and
  `detect_brief-text-image.md` are byte-identical (both sha256
  `e169b7237b853eea…`).
- `prompts/configs/phase3c-t2-h9A.json` is the brief-text configuration
  under another name: T 0.7, HIGH, `include_example_images: false`.
- The study YAML defines H9-A as the identical-pass baseline carried
  forward from the Phase 3a optimum ("brief-text", T 0.7, high;
  `studies/phase3c-h9-diversity-track2.yaml` `carried_forward`, condition
  A).

The text-track H9-A arm is therefore a replicate of the Phase 3a text-high
T 0.7 configuration (and of its replication run), and these three
analyses rank them as separate arms. Pair 1 (and pair 4) put a 4-of-5 vote
over five passes on both sides, so the two arms are literally two
independent draws of one configuration.
`reports/manipulation-check-2026-10-05.md` § B.3 documents that the five
H9-A passes are identical *by design*. No document records this cross-run
identity. Left NEW for the PI; not allow-listed.

## 6. Still unresolved, and caveats

**Unresolved (1 arm):**
`proposer-verifier-512::verified-adversarial-text`, proposer half.

- `outputs/h11/proposer-verifier-512/proposer/detections.geojson` (140
  detections) has no meta.
- Its byte-identical original,
  `archive/outputs-pre-retest-60-tile/phase2b/track2-text/T0.0/run_1/`,
  carries a meta recording a 1-tile, 3-detection invocation, not this
  pass.
- No meta anywhere describes these requests, so the arm stays
  UNVERIFIABLE.
- It appears only in `verifier-uplift-pairing`, which refuses on its KNOWN
  pair (it would otherwise be UNVERIFIABLE).

**Caveats a reviewer must weigh:**

- **Cleanup-only metas.** The investigations name 23 stages whose
  surviving `run.meta.json` covers only a cleanup or recovery leg; the
  main leg's meta was overwritten or gitignored. They are:
  - stride A `verify` (6 items) and `verify_37` (29);
  - G37-image K1 and K3 arm 2 (13 and 1);
  - `verify_swap37` (2) and grid `verify_37` (1);
  - 11 pv-diag-384 Era-2 stages (pv-high-image t0.3/t0.7/t1.0-n5,
    scale4-n10, six session-78 `*-text`, session-78-image-checklist);
  - `verified-f3vf`, `text-baseline-pro-verifier`,
    `pro-high-image-1of5-pro-verifier`,
    `pro-medium-image-baseline-pro-verifier`,
    `flash-high-text-1of5-flash-medium-verifier`, and gold-standard-v2
    `verified-v1`.

  For these, the transmitted signature is the surviving leg's
  configuration, which the post-run reports state is byte-identical to the
  main leg, and the verifier-inputs fingerprint covers only that leg. As
  section 4 shows, no verdict rests on that fingerprint.
- **March pv-diag-384 metas** record `items_processed 0`. They confirm the
  configuration but not request volume.
- **Verifier-robustness metas** record `temperature 0.0` in the T0.3 and
  T0.7 stages, with no `temperature_effective`. The gate's signatures for
  those stages may therefore under-separate by temperature. No pair
  refused on it: the stages differ in inputs or thinking.
- **Rungs read one union stage.** K-ladder N = 1/3/5 rungs on the 55-map
  boards are subsets of one union stage's verified probabilities. Their
  registered `n_passes` is the rung's proposer depth, not the verified
  depth.
- **Stale register notes and records found** (not edited; for the PI):
  - the `pv-diag-256` `_note`, `scripts/check_union_provenance.py:170-177`
    and the union-staleness retrospective say its passes do not exist;
    they do, in `archive/outputs-non-production-tile-sizes/`;
  - the `verifier-t-pilot` `_note` calls the T0.0 baseline an image
    verifier; it ran `verify_adversarial-text`;
  - the stride ladder notes say "over the full K=10 union"; each rung read
    its own `verify_k{1,3,5}`;
  - `results/k-ladder-2026-09-12/phase2/operating-points.json` still names
    `verify_k3` and 494 detections for the 3.7 K = 3 opmax cell, which now
    reads `verify_k3_recovery-fixed` (495);
  - the `pv-diag-384` note "No condition cites either" recovery stage is
    out of date;
  - the session-78 `*-text` register `instruction_file` names
    `verify_<x>-text.md`, which does not exist.

## 7. Tests

- **New: `tests/test_check_manipulation_bindings.py`** (17 tier-1 tests,
  synthetic repository in `tmp_path`). It covers:
  - a derived product followed to the stage holding its source;
  - the longest stage directory winning;
  - a source outside every stage read from its own directory, and a
    nonexistent source never widened;
  - proposer sources via the manifest, and via disk;
  - an unbound proposer bound by its sources;
  - the register outranking a binding;
  - a dead source named as a `BINDING GAP`;
  - seven validation rules;
  - a condition bound twice exiting 1;
  - **refusal still firing when two bound arms sent identical requests**:
    labelled NEW, and KNOWN when an allow-list group holds both pools;
  - bound arms whose requests differ passing.
- **`tests/test_lib_manipulation_signature.py`:** the parity test now
  expects `has_configuration`, plus a new test that a document without a
  configuration is not a meta.
- **`tests/test_check_manipulation.py`:** a new tier-2 test. The committed
  bindings validate, every verifier source lies in a registered stage, and
  `resolves_to` still matches.
- **Full tier-1 suite** (`python -m pytest -m tier1 -q -p
  no:cacheprovider`) on sapphire, in a git-backed scratch checkout of the
  branch: `3837 passed, 5 skipped, 52 deselected, 3 xfailed, 4 warnings in
  253.82s (0:04:13)`.
  - A first run in a copy without `.git` failed 13 tests that read git
    history (`test_lib_pass_cost`, `test_build_generated_file_registry`,
    `test_per_arch_md_ownership`, `test_verify_run_conditions`). The same
    four modules passed in the local git worktree (308 passed).
- **Tier-2 tests** on sapphire (gate, bindings, signature, modality):
  `8 passed, 84 deselected`.
- **Lint:** `ruff check` and `ruff check --select E501` are clean on every
  touched Python file.

## Appendix: every binding

Columns: binding id; conditions bound; the registered stage(s) its verifier sources resolve to; its proposer sources; the first deriving-script reference (full evidence in the file); and the product commit(s) recorded (for archived products, the original commit and the archive move `b69d8af4b`).

| Binding | Conds | Verifier stage(s) bound | Proposer sources | Deriving script (first ref) | Product commit |
| --- | ---: | --- | --- | --- | --- |
| `min11-uplift-5of10-pt0.15` | 3 | `55maps-text-min-n10-uplift/verified-3of10` | — | scripts/materialise_second_wave_sets.py:48 (UPLIFT root), 60-63 (SETS row: crops-3of10/can | `7aa28475b` |
| `stride-a-k10-primary-canonical` | 1 | `stride-55map-2026-08-25/g384_ov128_55map-union-k10-verify` | — | scripts/stride55_score.py:44-45 (VROOT outputs/stride-55map-2026-08-25/verifier, VERIFY_DI | `6ad5ac565` |
| `stride-a-k10-oracle-canonical` | 1 | `stride-55map-2026-08-25/g384_ov128_55map-union-k10-verify` | — | scripts/register_pass1_materialise.py:68-69 (SWEEP55 = sweep_oracle.json), 118-133 (load_c | `f34a96e0a, cc6ede6df` |
| `stride-a-final-board-cells` | 12 | `stride-55map-2026-08-25/g384_ov128_55map-union-k10-verify` | — | scripts/final_board_sweeps.py:11-13 (docstring: A/B rungs by gated first-N derivation with | `2b128ee68, 7894b5b5a` |
| `stride-a-n3-carried-posthoc` | 2 | `stride-55map-2026-08-25/g384_ov128_55map-union-k10-verify` | — | scripts/final_board_n3_carried.py:72-74 (POINT, EXPECTED, CELLS), 103-125 (load_candidates | `221031f95, 7894b5b5a` |
| `stride-b-k10-primary-canonical` | 1 | `stride-55map-2026-08-25/g384_ov192_55map-union-k10-verify` | — | scripts/stride55_score.py:44-45 (VROOT, VERIFY_DIR 'verify'), 57-58 (RUNS point), 103-106  | `6ad5ac565` |
| `stride-b-k10-oracle-canonical` | 1 | `stride-55map-2026-08-25/g384_ov192_55map-union-k10-verify` | — | scripts/register_pass1_materialise.py:68-69, 118-133 | `f34a96e0a` |
| `stride-b-final-board-cells` | 13 | `stride-55map-2026-08-25/g384_ov192_55map-union-k10-verify` | — | scripts/final_board_sweeps.py:11-13, 309-321 (A/B branch), 987-1006 (materialise) | `2b128ee68, 7894b5b5a` |
| `stride-b-n3-carried-posthoc` | 2 | `stride-55map-2026-08-25/g384_ov192_55map-union-k10-verify` | — | scripts/final_board_n3_carried.py:72-74, 103-125. The same logic is at 221031f95:scripts/f | `221031f95, 7894b5b5a` |
| `fourth-cell-k10-primary` | 2 | `stride-55map-2026-08-25/g384_ov192_55map-union-k10-verify37` | — | scripts/stride55_score.py:90-160 (materialise_primary; 103-106 read crops/candidate_manife | `a73d64346` |
| `fourth-r2-board-cells` | 4 | `stride-55map-2026-08-25/g384_ov192_55map-union-k10-verify37` | — | scripts/final_board_sweeps.py:209-225 (G37_IDENTITY, G37_COMMITTED, G37_FAMILY_OF_CELL), 3 | `7894b5b5a` |
| `arm1-k5-primary` | 2 | `gemini37-55map-2026-08-29/g384_ov192_55map_g37-union-k5-verify-arm1` | — | scripts/stride55_score.py:90-160 (materialise_primary; 103-106 read crops/candidate_manife | `bce396250` |
| `arm1-r2-board-cells` | 4 | `gemini37-55map-2026-08-29/g384_ov192_55map_g37-union-k5-verify-arm1` | — | scripts/final_board_sweeps.py:209-225, 327-373 (build_g37_families; arm passes at 349/356; | `7894b5b5a` |
| `arm2-k5-primary` | 2 | `gemini37-55map-2026-08-29/g384_ov192_55map_g37-union-k5-verify-arm2` | — | scripts/stride55_score.py:90-160, 216-245 (overrides, added in 56ad9ddc7) | `bce396250` |
| `arm2-r2-board-cells` | 4 | `gemini37-55map-2026-08-29/g384_ov192_55map_g37-union-k5-verify-arm2` | — | scripts/final_board_sweeps.py:209-225, 327-373, 987-1006 | `7894b5b5a` |
| `g37img-k1-arm1` | 3 | `gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img-union-k1-verify-arm1` | — | Current HEAD 51b49deca: scripts/gemini37_image_55map_r2.py:206-212 (G37 Campaign root outp | `e0f9a4d03, 2645e499c` |
| `g37img-k1-arm2` | 3 | `gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img-union-k1-verify-arm2` | — | scripts/gemini37_image_55map_r2.py:579-580 and :926-936 at HEAD; at e0f9a4d03 :399-400 and | `e0f9a4d03` |
| `g37img-k3-arm1` | 3 | `gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img-union-k3-verify-arm1` | — | scripts/gemini37_image_55map_r2.py:579-580 and :926-936 at HEAD; at e0f9a4d03 :399-400, :5 | `e0f9a4d03, 629b61cf, 2645e499c` |
| `g37img-k3-arm2` | 3 | `gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img-union-k3-verify-arm2` | — | scripts/gemini37_image_55map_r2.py:579-580 and :926-936 at HEAD; at e0f9a4d03 :399-400, :5 | `e0f9a4d03, 2645e499c, 912cbe3e` |
| `g37img-k5-arm1` | 3 | `gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img-union-k5-verify-arm1` | — | scripts/gemini37_image_55map_r2.py:579-580 and :926-936 at HEAD; at the product commit 8d8 | `8d800f2d6` |
| `g37img-k5-arm2` | 3 | `gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img-union-k5-verify-arm2` | — | scripts/gemini37_image_55map_r2.py:206-212 (carried ('arm2', 5): (0.90, 5)), :579-580, :92 | `8d800f2d6, 4900288ff` |
| `g3img-k1-arm1` | 3 | `gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img-union-k1-verify-arm1` | — | scripts/gemini37_image_55map_r2.py:238-244 (G3 Campaign root, cell g384_ov192_55map_g3img, | `8491f9c78` |
| `g3img-k1-arm2` | 3 | `gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img-union-k1-verify-arm2` | — | scripts/gemini37_image_55map_r2.py:238-244, :579-580, :926-936 at HEAD; at 8491f9c78 :216- | `8491f9c78, cda04a952` |
| `g3img-k3-arm1` | 3 | `gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img-union-k3-verify-arm1` | — | scripts/gemini37_image_55map_r2.py:238-244, :579-580, :926-936 at HEAD; at the product com | `5d106e1d5, 2645e499c, 443c9fe0` |
| `g3img-k3-arm2` | 3 | `gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img-union-k3-verify-arm2` | — | scripts/gemini37_image_55map_r2.py:238-244, :579-580, :926-936 at HEAD; at 5d106e1d5 :216- | `5d106e1d5, e21b5295a, 2645e499c` |
| `g3img-k5-arm1` | 3 | `gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img-union-k5-verify-arm1` | — | scripts/gemini37_image_55map_r2.py:238-244, :579-580, :926-936 at HEAD; at the product com | `983018037, 2645e499c, cee80574` |
| `g3img-k5-arm2` | 3 | `gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img-union-k5-verify-arm2` | — | scripts/gemini37_image_55map_r2.py:238-244 (carried ('arm2', 5): (0.95, 5)), :579-580, :92 | `983018037, 880c207f7, 2645e499c` |
| `g37-screen-k5-carried-verify` | 2 | `gemini37-screen-2026-08-28/g384_ov192_g37-union-k5-verify` | — | scripts/image_b_analysis.py:88-118 (load_image_union reads &lt;outputs-root&gt;/verifier/&lt;cell&gt;/ | `b19071e37` |
| `g37-screen-k10-carried-verify-k10` | 2 | `gemini37-screen-2026-08-28/g384_ov192_g37-union-k10-verify` | — | scripts/image_b_analysis.py:88-118 (load_image_union reads &lt;outputs-root&gt;/verifier/&lt;cell&gt;/ | `b9516c26f` |
| `g37-screen-k5-swap37` | 2 | `gemini37-screen-2026-08-28/g384_ov192_g37-union-k5-verify-swap37` | — | scripts/image_b_analysis.py:88-118 (load_image_union reads &lt;outputs-root&gt;/verifier/&lt;cell&gt;/ | `3039d3ac9` |
| `g37-screen-k5-swap38-armV` | 2 | `gemini37-screen-2026-08-28/g384_ov192_g37-union-k5-verify-swap38` | — | scripts/image_b_analysis.py:88-118 (load_image_union reads &lt;outputs-root&gt;/verifier/&lt;cell&gt;/ | `f04eb6f58` |
| `g37-image-arm1` | 2 | `gemini37-image-gs-2026-09-01/g384_ov192_g37img-union-k5-verify-arm1` | — | scripts/image_b_analysis.py:88-118 (load_image_union reads &lt;outputs-root&gt;/verifier/&lt;cell&gt;/ | `ada9822fe` |
| `g37-image-arm2` | 2 | `gemini37-image-gs-2026-09-01/g384_ov192_g37img-union-k5-verify-arm2` | — | scripts/image_b_analysis.py:88-118 (load_image_union reads &lt;outputs-root&gt;/verifier/&lt;cell&gt;/ | `ada9822fe` |
| `g37-kladder-k1-verify-k1` | 2 | `gemini37-screen-2026-08-28/g384_ov192_g37-union-k1-verify` | — | scripts/run_k_ladder_phase2_verifier.py:116-129 (STAGE_OVERRIDES K=1 -> verifier/g384_ov19 | `326181bcd` |
| `g37-kladder-k3-verify-k3-recovery-fixed` | 1 | `gemini37-screen-2026-08-28/g384_ov192_g37-union-k3-verify-recovery-fixed`; `gemini37-screen-2026-08-28/g384_ov192_g37-union-k3-verify` | — | results/k-ladder-2026-09-12/recovery-fix-2026-09-13/harness/rescore_recovery_fixed.py:173- | `326181bcd, 987534c03` |
| `grid-tier-e-k1` | 2 | `grid-2026-08-18/g384_ov192-k-ladder-k1-verify` | 1 dir(s) under `outputs/grid-2026-08-18/g384_ov192` | scripts/run_k_ladder_tier_e.py:146 (POOL_DIR outputs/grid-2026-08-18/g384_ov192), :150 (VE | `5167b9a5c` |
| `grid-tier-e-k3` | 1 | `grid-2026-08-18/g384_ov192-k-ladder-k3-verify` | 3 dir(s) under `outputs/grid-2026-08-18/g384_ov192` | scripts/run_k_ladder_tier_e.py:146 (POOL_DIR outputs/grid-2026-08-18/g384_ov192), :150 (VE | `5167b9a5c` |
| `grid-tier-e-k5` | 1 | `grid-2026-08-18/g384_ov192-k-ladder-k5-verify` | 5 dir(s) under `outputs/grid-2026-08-18/g384_ov192` | scripts/run_k_ladder_tier_e.py:146 (POOL_DIR outputs/grid-2026-08-18/g384_ov192), :150 (VE | `5167b9a5c` |
| `grid-g384ov192-k10-verify37-gs-leg` | 2 | `grid-2026-08-18/g384_ov192-union-k10-verify37` | 13 dir(s) under `outputs/grid-2026-08-18/g384_ov192` | scripts/image_b_analysis.py:88-118 (load_image_union reads &lt;outputs-root&gt;/verifier/&lt;cell&gt;/ | `bce396250` |
| `grid-g384ov048-k10-verify` | 1 | `grid-2026-08-18/g384_ov048-union-k10-verify` | — | scripts/grid_verifier_analysis.py:127 (VERIFIER_DIR outputs/grid-2026-08-18/verifier), :15 | `8d4ab3fd8, 0a6bde47f` |
| `grid-g384ov192-k10-verify` | 2 | `grid-2026-08-18/g384_ov192-union-k10-verify` | — | scripts/grid_verifier_analysis.py:127 (VERIFIER_DIR outputs/grid-2026-08-18/verifier), :15 | `8d4ab3fd8, 0a6bde47f` |
| `grid-g512ov064-k10-verify` | 1 | `grid-2026-08-18/g512_ov064-union-k10-verify` | — | scripts/grid_verifier_analysis.py:127 (VERIFIER_DIR outputs/grid-2026-08-18/verifier), :15 | `8d4ab3fd8, 0a6bde47f` |
| `grid-g512ov256-k10-verify` | 1 | `grid-2026-08-18/g512_ov256-union-k10-verify` | — | scripts/grid_verifier_analysis.py:127 (VERIFIER_DIR outputs/grid-2026-08-18/verifier), :15 | `8d4ab3fd8, 0a6bde47f` |
| `image-b-min-k10-verify` | 2 | `image-b-gs-2026-08-28/g384_ov192_image-union-k10-verify` | — | scripts/image_b_analysis.py:88-118 (load_image_union reads &lt;outputs-root&gt;/verifier/&lt;cell&gt;/ | `522fb5362` |
| `image-b-high-k10-verify` | 2 | `image-b-gs-2026-08-28/g384_ov192_image_high-union-k10-verify` | — | scripts/image_b_analysis.py:88-118 (load_image_union reads &lt;outputs-root&gt;/verifier/&lt;cell&gt;/ | `5112e9de4` |
| `stride-g256ov064-k10-verify` | 1 | `stride-phaseb-2026-08-25/g256_ov064-union-k10-verify` | — | scripts/stride_verifier_analysis.py:70-75 (STRIDE_CELLS roots), :108-133 (load_stride_unio | `69bdc18b3` |
| `stride-g384ov128-k10-verify` | 1 | `stride-phaseb-2026-08-25/g384_ov128-union-k10-verify` | — | scripts/stride_verifier_analysis.py:70-75 (STRIDE_CELLS roots), :108-133 (load_stride_unio | `69bdc18b3` |
| `stride-g512ov176-k10-verify` | 1 | `stride-phaseb-2026-08-25/g512_ov176-union-k10-verify` | — | scripts/stride_verifier_analysis.py:70-75 (STRIDE_CELLS roots), :108-133 (load_stride_unio | `69bdc18b3` |
| `stride-g512ov320-k10-verify` | 1 | `stride-phaseb-2026-08-25/g512_ov320-union-k10-verify` | — | scripts/stride_verifier_analysis.py:70-75 (STRIDE_CELLS roots), :108-133 (load_stride_unio | `69bdc18b3` |
| `stride-g384ov240-k10-verify` | 1 | `stride-phasec-2026-08-25/g384_ov240-union-k10-verify` | — | scripts/stride_verifier_analysis.py:70-75 (STRIDE_CELLS roots), :108-133 (load_stride_unio | `69bdc18b3` |
| `stride-g384ov128-ladder-n1` | 1 | `stride-phaseb-2026-08-25/g384_ov128-union-k1-verify` | — | scripts/register_pass1_materialise.py:63-64 (VROOT outputs/stride-phaseb-2026-08-25/verifi | `f34a96e0a` |
| `stride-g384ov128-ladder-n3` | 1 | `stride-phaseb-2026-08-25/g384_ov128-union-k3-verify` | — | scripts/register_pass1_materialise.py:63-64 (VROOT outputs/stride-phaseb-2026-08-25/verifi | `f34a96e0a` |
| `stride-g384ov128-ladder-n5` | 1 | `stride-phaseb-2026-08-25/g384_ov128-union-k5-verify` | — | scripts/register_pass1_materialise.py:63-64 (VROOT outputs/stride-phaseb-2026-08-25/verifi | `f34a96e0a` |
| `kl2-pv-min-text-t0.3-n1` | 1 | `pv-diag-384/flash-minimal-text-n30-t07-text-t0.3-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-text-t0.3-n3` | 2 | `pv-diag-384/flash-minimal-text-n30-t07-text-t0.3-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-text-t0.7-n1` | 1 | `pv-diag-384/flash-minimal-text-n30-t07-text-t0.7-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-text-t0.7-n3` | 2 | `pv-diag-384/flash-minimal-text-n30-t07-text-t0.7-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-text-t1.0-n1` | 2 | `pv-diag-384/flash-minimal-text-n30-t07-text-t1.0-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-text-t1.0-n3` | 2 | `pv-diag-384/flash-minimal-text-n30-t07-text-t1.0-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-text-t0.3-n1` | 2 | `pv-diag-384/flash-high-text-n5-text-t0.3-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-text-t0.3-n3` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.3-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-text-t0.7-n1` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-text-t0.7-n3` | 2 | `pv-diag-384/flash-high-text-n5-text-t0.7-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-text-t1.0-n1` | 2 | `pv-diag-384/flash-high-text-n5-text-t1.0-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-text-t1.0-n3` | 2 | `pv-diag-384/flash-high-text-n5-text-t1.0-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-image-t0.3-n1` | 2 | `pv-diag-384/image-n5-image-t0.3-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-image-t0.3-n3` | 1 | `pv-diag-384/image-n5-image-t0.3-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-image-t0.7-n1` | 1 | `pv-diag-384/image-n5-image-t0.7-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-image-t0.7-n3` | 2 | `pv-diag-384/image-n5-image-t0.7-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-image-t1.0-n1` | 1 | `pv-diag-384/image-n5-image-t1.0-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-min-image-t1.0-n3` | 2 | `pv-diag-384/image-n5-image-t1.0-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-image-t0.3-n1` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.3-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-image-t0.3-n3` | 2 | `pv-diag-384/flash-high-image-n5-image-t0.3-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-image-t0.7-n1` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-image-t0.7-n3` | 2 | `pv-diag-384/flash-high-image-n5-image-t0.7-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-image-t1.0-n1` | 2 | `pv-diag-384/flash-high-image-n5-image-t1.0-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-high-image-t1.0-n3` | 2 | `pv-diag-384/flash-high-image-n5-image-t1.0-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-scale4-optimal-n1` | 2 | `pv-diag-384/scale-4-optimal-487-verified-v1-n1` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `kl2-pv-scale4-optimal-n3` | 2 | `pv-diag-384/scale-4-optimal-487-verified-v1-n3` | — | scripts/score_k_ladder_phase2_rungs.py:257-264 (materialise command: --consensus {consensu | `326181bcd` |
| `opmax-rebuilt-pv-high-text-t0.3-n5` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.3-verified-v1-n5` | — | scripts/materialise_opmax_cells.py:93 (OUT_DIR opmax/materialised), :98 (PV_REGISTRY), :42 | `2c3132edc` |
| `s78-text-comparative` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-session-78-matrix-verified-comparative` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b69d8af4b` |
| `s78-text-adversarial` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-session-78-matrix-verified-adversarial` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b69d8af4b` |
| `pv-archived-pv-high-text-t1.0-n10` | 1 | `pv-diag-384/flash-high-text-n5-text-t1.0-verified-v1-n10` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `s78-text-checklist` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-session-78-matrix-verified-checklist` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b69d8af4b` |
| `pv-archived-pv-min-text-t0.3-n5` | 1 | `pv-diag-384/flash-minimal-text-n30-t07-text-t0.3-verified-v1-n5` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `opmax-rebuilt-pv-min-text-t1.0-n10` | 1 | `pv-diag-384/flash-minimal-text-n30-t07-text-t1.0-verified-v1-n10` | — | scripts/materialise_opmax_cells.py:93 (OUT_DIR opmax/materialised), :98 (PV_REGISTRY), :42 | `2c3132edc` |
| `s78-text-brief` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-session-78-matrix-verified-brief` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b69d8af4b` |
| `pv-archived-pv-high-text-t0.7-n10` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-verified-v1-n10` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `opmax-rebuilt-pv-min-text-t0.7-n5` | 1 | `pv-diag-384/flash-minimal-text-n30-t07-text-t0.7-verified-v1-n5` | — | scripts/materialise_opmax_cells.py:93 (OUT_DIR opmax/materialised), :98 (PV_REGISTRY), :42 | `2c3132edc` |
| `pv-archived-pv-min-text-t0.7-n10` | 1 | `pv-diag-384/flash-minimal-text-n30-t07-text-t0.7-verified-v1-n10` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `pv-archived-pv-high-text-t0.3-n10` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.3-verified-v1-n10` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `pv-archived-pv-min-text-t1.0-n5` | 1 | `pv-diag-384/flash-minimal-text-n30-t07-text-t1.0-verified-v1-n5` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `opmax-rebuilt-pv-min-text-t0.3-n10` | 1 | `pv-diag-384/flash-minimal-text-n30-t07-text-t0.3-verified-v1-n10` | — | scripts/materialise_opmax_cells.py:93 (OUT_DIR opmax/materialised), :98 (PV_REGISTRY), :42 | `2c3132edc` |
| `s78-text-checklist-text` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-session-78-matrix-verified-checklist-text` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b3ed509e6, 414ee8a4b` |
| `pv-archived-pv-high-text-t0.7-n5` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-verified-v1-n5` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `pv-archived-pv-min-text-t0.0-n3` | 1 | `pv-diag-384/flash-minimal-text-n30-t07-text-t0.0-verified-v1-n3` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `opmax-rebuilt-pv-high-text-t1.0-n5` | 1 | `pv-diag-384/flash-high-text-n5-text-t1.0-verified-v1-n5` | — | scripts/materialise_opmax_cells.py:93 (OUT_DIR opmax/materialised), :98 (PV_REGISTRY), :42 | `2c3132edc` |
| `s78-text-adversarial-text` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-session-78-matrix-verified-adversarial-text` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b3ed509e6, 414ee8a4b` |
| `s78-text-brief-text` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.7-session-78-matrix-verified-brief-text` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b3ed509e6, 414ee8a4b` |
| `pv-archived-pv-high-text-t0.0-n3` | 1 | `pv-diag-384/flash-high-text-n5-text-t0.0-verified-v1-n3` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `pv-archived-pv-min-image-t0.7-n10` | 1 | `pv-diag-384/image-n5-image-t0.7-verified-v1-n10` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `pv-archived-pv-high-image-t0.7-n5` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-verified-v1-n5` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, d6cdb648b, b69d8af4b` |
| `s78-image-adversarial` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-session-78-matrix-verified-adversarial` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b69d8af4b` |
| `s78-image-comparative` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-session-78-matrix-verified-comparative` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b69d8af4b` |
| `s78-image-checklist-text` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-session-78-matrix-verified-checklist-text` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b3ed509e6, 414ee8a4b` |
| `s78-image-brief` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-session-78-matrix-verified-brief` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b69d8af4b` |
| `s78-image-checklist` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-session-78-matrix-verified-checklist` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b69d8af4b` |
| `pv-archived-pv-min-image-t0.3-n10` | 1 | `pv-diag-384/image-n5-image-t0.3-verified-v1-n10` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `s78-image-brief-text` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-session-78-matrix-verified-brief-text` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b3ed509e6, 414ee8a4b` |
| `pv-archived-pv-min-image-t0.3-n5` | 1 | `pv-diag-384/image-n5-image-t0.3-verified-v1-n5` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `opmax-rebuilt-pv-high-image-t0.7-n10` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-verified-v1-n10` | — | scripts/materialise_opmax_cells.py:93 (OUT_DIR opmax/materialised), :98 (PV_REGISTRY), :42 | `2c3132edc` |
| `pv-archived-pv-min-image-t0.7-n5` | 1 | `pv-diag-384/image-n5-image-t0.7-verified-v1-n5` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `s78-image-adversarial-text` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.7-session-78-matrix-verified-adversarial-text` | — | scripts/materialise_session78_geojsons.py:63-66 (POOL_BASE: flash-high-image-n5/image-t0.7 | `f8d755790, b3ed509e6, 414ee8a4b` |
| `opmax-rebuilt-pv-high-image-t0.3-n10` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.3-verified-v1-n10` | — | scripts/materialise_opmax_cells.py:93 (OUT_DIR opmax/materialised), :98 (PV_REGISTRY), :42 | `2c3132edc` |
| `pv-archived-pv-scale4-optimal-n10` | 1 | `pv-diag-384/scale-4-optimal-487-verified-v1-n10` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, d6cdb648b, b69d8af4b` |
| `pv-archived-pv-n1-image-t0-n3` | 1 | `n1-outstanding-384/image-t0-verified-v1-n3` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `pv-archived-pv-high-image-t1.0-n10` | 1 | `pv-diag-384/flash-high-image-n5-image-t1.0-verified-v1-n10` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `opmax-rebuilt-pv-scale4-optimal-n5` | 1 | `pv-diag-384/scale-4-optimal-487-verified-v1-n5` | — | scripts/materialise_opmax_cells.py:93 (OUT_DIR opmax/materialised), :98 (PV_REGISTRY), :42 | `2c3132edc` |
| `pv-archived-pv-high-image-t0.3-n5` | 1 | `pv-diag-384/flash-high-image-n5-image-t0.3-verified-v1-n5` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, d6cdb648b, b69d8af4b` |
| `opmax-rebuilt-pv-min-image-t1.0-n10` | 1 | `pv-diag-384/image-n5-image-t1.0-verified-v1-n10` | — | scripts/materialise_opmax_cells.py:93 (OUT_DIR opmax/materialised), :98 (PV_REGISTRY), :42 | `2c3132edc` |
| `pv-archived-pv-min-image-t1.0-n5` | 1 | `pv-diag-384/image-n5-image-t1.0-verified-v1-n5` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, b69d8af4b` |
| `pv-archived-pv-high-image-t1.0-n5` | 1 | `pv-diag-384/flash-high-image-n5-image-t1.0-verified-v1-n5` | — | scripts/materialise_pv_geojson.py (filter CLI: --consensus / --probabilities / --vote-t /  | `bd24293d4, d6cdb648b, b69d8af4b` |
| `current-vintage-pv-high-text-t0.0-n3-recovery` | 2 | `pv-diag-384/flash-high-text-n5-text-t0.0-verified-v1-n3-recovery-2026-09-08` | — | scripts/check_pv_sweep_vintage.py:249-257 (materialise subcommand: --union, --probabilitie | `fe84765d8` |
| `sweep-image-min-3of5` | 2 | `pv-diag-384/verified-image-1of5` | — | scripts/materialise_sweep_cells.py:41-42,46-68,80-98 (read at 86-87) | `e76343057` |
| `sweep-image-min-6of10` | 2 | `pv-diag-384/verified-image-1of10` | 10 dir(s) under `outputs/h11/pv-diag-384/image-n5/image-t0.7` | scripts/materialise_sweep_cells.py:46-48,80-98 | `e76343057` |
| `sweep-image-baseline` | 2 | `pv-diag-384/verified-image-baseline` | — | scripts/materialise_sweep_cells.py:49,80-98 | `e76343057` |
| `sweep-image-baseline-medium-vf` | 2 | `pv-diag-384/verified-flash-minimal-image-medium-verifier` | — | scripts/materialise_sweep_cells.py:50-51,80-98 | `e76343057` |
| `sweep-image-baseline-pro-vf` | 2 | `pv-diag-384/verified-image-baseline-pro-verifier` | — | scripts/materialise_sweep_cells.py:52,80-98 | `e76343057` |
| `sweep-text-baseline` | 2 | `pv-diag-384/verified-text-baseline` | — | scripts/materialise_sweep_cells.py:53,80-98 | `e76343057` |
| `sweep-text-baseline-medium-vf` | 2 | `pv-diag-384/verified-flash-minimal-text-medium-verifier` | — | scripts/materialise_sweep_cells.py:54-55,80-98 | `e76343057` |
| `sweep-text-baseline-pro-vf` | 2 | `pv-diag-384/verified-text-baseline-pro-verifier` | — | scripts/materialise_sweep_cells.py:56,80-98 | `e76343057` |
| `sweep-pro-text-medium-vf-3of5` | 2 | `pv-diag-384/verified-pro-high-text-1of5` | — | scripts/materialise_sweep_cells.py:57-58,80-98 | `e76343057` |
| `sweep-pro-image-pro-vf-3of5` | 2 | `pv-diag-384/verified-pro-high-image-1of5-pro-verifier` | — | scripts/materialise_sweep_cells.py:59,80-98 | `e76343057` |
| `sweep-pro-text-baseline` | 2 | `pv-diag-384/verified-pro-text-minimal-verifier` | — | scripts/materialise_sweep_cells.py:60,80-98 | `e76343057` |
| `sweep-pro-text-baseline-medium-vf` | 2 | `pv-diag-384/verified-pro-text-medium-verifier` | — | scripts/materialise_sweep_cells.py:61-62,80-98 | `e76343057` |
| `sweep-pro-text-baseline-pro-vf` | 2 | `pv-diag-384/verified-pro-medium-text-baseline-pro-verifier` | — | scripts/materialise_sweep_cells.py:63,80-98 | `e76343057` |
| `sweep-pro-image-baseline` | 2 | `pv-diag-384/verified-pro-image-minimal-verifier` | — | scripts/materialise_sweep_cells.py:64,80-98 | `e76343057` |
| `sweep-pro-image-baseline-medium-vf` | 2 | `pv-diag-384/verified-pro-image-medium-verifier` | — | scripts/materialise_sweep_cells.py:65-66,80-98 | `e76343057` |
| `sweep-pro-image-baseline-pro-vf` | 2 | `pv-diag-384/verified-pro-medium-image-baseline-pro-verifier` | — | scripts/materialise_sweep_cells.py:67,80-98 | `e76343057` |
| `cset-image-3of5` | 2 | `pv-diag-384/verified-flash-high-image-1of5` | — | scripts/materialise_second_wave_sets.py:47,51-59,67-88 | `7aa28475b` |
| `cset-t03-4of5` | 2 | `pv-diag-384/verified-flash-high-text-t03-1of5` | 5 dir(s) under `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3` | scripts/run_t03_gs_verifier.sh:33-35,39-47,55-59 | `7aa28475b` |
| `cset-medium-vf-4of5` | 2 | `pv-diag-384/verified-flash-high-text-1of5-flash-medium-verifier` | — | scripts/materialise_vr_condition_sets.py:52,70-73,153-155 | `17c7e87ac` |
| `cset-pro-flash-vf-3of5` | 2 | `pv-diag-384/verified-pro-high-text-1of5-flash-minimal-verifier` | — | scripts/materialise_vr_condition_sets.py:52-53,75-78,85-108,157-159 | `17c7e87ac` |
| `cset-pro-pro-vf-3of5` | 2 | `pv-diag-384/verified-pro-high-text-1of5-pro-verifier` | — | scripts/materialise_vr_condition_sets.py:52-53,79-81,85-108,157-159 | `17c7e87ac` |
| `cset-vr-256-union-t0-0` | 1 | `verifier-robustness/256-union-t0-0` | 5 dir(s) under `archive/outputs-non-production-tile-sizes/text-n5/text-t0.7` | scripts/materialise_vr_condition_sets.py:51,62-65,153-155 | `17c7e87ac` |
| `cset-vr-256-ge3of5-t0-3` | 1 | `verifier-robustness/256-ge3of5-t0-3` | 5 dir(s) under `archive/outputs-non-production-tile-sizes/text-n5/text-t0.7` | scripts/materialise_vr_condition_sets.py:51,66-69,153-155 | `17c7e87ac` |
| `matrix-min-T0.0` | 2 | `verifier-robustness/384-union-t0-0` | — | scripts/tier_verifier_matrix.py:49-53,57-58,108-113 | `88a49e077` |
| `matrix-min-T0.3` | 2 | `verifier-robustness/384-ge3of5-t0-3` | — | scripts/tier_verifier_matrix.py:49-53,59,108-113 | `88a49e077` |
| `matrix-min-T0.7` | 2 | `verifier-robustness/384-ge3of5-t0-7` | — | scripts/tier_verifier_matrix.py:49-53,60,108-113 | `88a49e077` |
| `matrix-high-T0.3` | 2 | `verifier-robustness/384-ge3of5-t0-3-high` | — | scripts/tier_verifier_matrix.py:49-53,62,108-113 | `88a49e077` |
| `matrix-high-T0.7` | 2 | `verifier-robustness/384-ge3of5-t0-7-high` | — | scripts/tier_verifier_matrix.py:49-53,63,108-113 | `88a49e077` |
| `matrix-high-T0.0` | 2 | `pv-diag-384/verified-flash-high-text-1of5-flash-high-verifier` | — | scripts/tier_verifier_matrix.py:51,61,108-113 | `88a49e077` |
| `pareto-cheap6` | 2 | `pv-diag-384/verified-flash-high-text-1of5` | — | scripts/build_pareto_leaderboard.py:65,69,107-145 (read at 122-124),240-242 | `60657fcf0` |
| `pareto-nof10` | 2 | `pv-diag-384/verified-flash-high-text-1of10` | 10 dir(s) under `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7` | scripts/build_pareto_leaderboard.py:81-82,163-174 (read at 165-167),249-251 | `60657fcf0` |
| `minthink-min11` | 2 | `pv-diag-384/verified-text-1of10` | — | scripts/score_min_thinking_pv.py:52-55,63-89,120-121,140-144 | `ffb441239` |
| `minthink-n30lineage` | 2 | `pv-diag-384/verified-flash-minimal-text-t07-1of5` | 5 dir(s) under `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7` | scripts/score_min_thinking_pv.py:15-18,120-121,145-150 | `ffb441239` |
| `minthink-true-min6` | 2 | `pv-diag-384/verified-text-min-t07-true-1of5` | 5 dir(s) under `outputs/h11/pv-diag-384/text-n10/text-t0.7` | planning/min6-makeup-run-plan-2026-06-10.md:39-54 (the commands); no committed script writ | `e7e613f1f` |
| `minthink-high6-pro-vf` | 2 | `pv-diag-384/verified-flash-high-text-1of5-pro-verifier` | — | scripts/sweep_unswept_pools.py:107-115 (cell registry: manifest flash-high-text-1of5, prob | `8f5a0dd35` |
| `opmax-16of30` | 2 | `verifier-robustness/384-16of30-t0-3` | 30 dir(s) under `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7` | scripts/permutation_opmax_vs_headline.py:69-78,93-127 | `929ef0ea8` |
| `stage-d-384-headline-16of30` | 2 | `pv-diag-384/verified-flash-high-text-1of30` | 30 dir(s) under `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7` | scripts/run_era1_pv_stage_d.py:117-148 (verified_pools shape),225-245 (build at 235-243) | `48b56fdd6` |
| `flash35-f35prop-f35vf` | 2 | `flash35-pv-2x2/verified-f35vf` | — | scripts/materialise_flash35_best_ops.py:38-40,44-57,60-83 | `e7e613f1f` |
| `flash35-f35prop-f3vf` | 2 | `flash35-pv-2x2/verified-f3vf` | — | scripts/materialise_flash35_best_ops.py:38-40,44-45,52-54,60-83 | `e7e613f1f` |
| `flash35-f3prop-f35vf` | 2 | `flash35-pv-2x2/min-f3-verified-f35vf` | 10 dir(s) under `outputs/h11/pv-diag-384/text-n10/text-t0.7` | scripts/finish_flash35_tranche.sh:21-24,48-64 | `e7e613f1f` |
| `vtpilot-t0-0` | 2 | `gold-standard-v2/verified-v1` | — | scripts/run_verifier_t_stage_b.py:69-75 (CONSENSUS_GEOJSON, PROBS_BY_T),174-191 (probs loo | `b9f73bbfb` |
| `phase3c-image-a-diversity-union` | 1 | — | 5 dir(s) under `outputs/retest/phase3c/track1-image` | scripts/materialise_phase3c_consensus.py:86-98 (TRACKS study_dir, DEFAULT_OUT), :124-151 ( | `fca7f888b` |
| `phase3c-image-b-diversity-union` | 1 | — | 5 dir(s) under `outputs/retest/phase3c/track1-image` | scripts/materialise_phase3c_consensus.py:86-98, :124-151, :191-205 | `fca7f888b` |
| `phase3c-image-c-diversity-union` | 1 | — | 5 dir(s) under `outputs/retest/phase3c/track1-image` | scripts/materialise_phase3c_consensus.py:86-98, :124-151, :191-205 | `fca7f888b` |
| `phase3c-image-d-diversity-union` | 1 | — | 5 dir(s) under `outputs/retest/phase3c/track1-image` | scripts/materialise_phase3c_consensus.py:86-98, :124-151, :191-205 | `fca7f888b` |
| `phase3c-image-e-diversity-union` | 1 | — | 5 dir(s) under `outputs/retest/phase3c/track1-image` | scripts/materialise_phase3c_consensus.py:86-98, :124-151, :191-205 | `fca7f888b` |
| `phase3c-text-a-diversity-union` | 1 | — | 5 dir(s) under `outputs/retest/phase3c/track2-text` | scripts/materialise_phase3c_consensus.py:86-98, :124-151, :191-205 | `fca7f888b` |
| `phase3c-text-b-diversity-union` | 1 | — | 5 dir(s) under `outputs/retest/phase3c/track2-text` | scripts/materialise_phase3c_consensus.py:86-98, :124-151, :191-205 | `fca7f888b` |
| `phase3c-text-d-diversity-union` | 1 | — | 5 dir(s) under `outputs/retest/phase3c/track2-text` | scripts/materialise_phase3c_consensus.py:86-98, :124-151, :191-205 | `fca7f888b` |
| `phase3c-text-e-diversity-union` | 1 | — | 5 dir(s) under `outputs/retest/phase3c/track2-text` | scripts/materialise_phase3c_consensus.py:86-98, :124-151, :191-205 | `fca7f888b` |
| `h13-arm-a-phase2a-brief-text` | 2 | — | 3 dir(s) under `outputs/retest/phase2a/brief-text` | scripts/prepare_h13_scoring.py:120-131 (ARMS['armA'] runs -> outputs/retest/phase2a/brief- | `faff43dd4` |
| `pv-diag-256-text-baseline` | 1 | — | 1 dir(s) under `archive/outputs-non-production-tile-sizes/text-baseline/text-t0.0` | none recorded (unscripted copy); identity verified by sha256 on sapphire | `3d22184d6, 276e4ca80, bd24293d4` |
| `pv-diag-256-text-5of5-union` | 1 | — | 5 dir(s) under `archive/outputs-non-production-tile-sizes/text-n5/text-t0.7` | builder not recorded; the plan names scripts/lib_consensus.py (archive/planning/h11-256-pv | `3d22184d6, 276e4ca80, bd24293d4` |
| `stage-d-256-consensus-text-5of5` | 1 | — | 5 dir(s) under `archive/outputs-non-production-tile-sizes/text-n5/text-t0.7` | scripts/run_era1_pv_stage_d.py:69-70 (cells file, output root), :117-146 (pass_dirs: propo | `7d6c46672` |
| `stage-d-512-single-text-t0.0` | 1 | `retest-phase2b/verified-adv-text-t0.0-pass1`; `retest-phase2b/verified-adv-text-t0.0-pass2`; `retest-phase2b/verified-adv-text-t0.0-pass3` | 3 dir(s) under `outputs/retest/phase2b/track2-text/T0.0` | scripts/run_era1_pv_stage_d.py:117-146 (pass_i <- proposers[i]), :184-195 (extract and ver | `7d6c46672` |
| `stage-d-512-single-image-t0.0` | 1 | `retest-phase2b/verified-adv-image-t0.0-pass1`; `retest-phase2b/verified-adv-image-t0.0-pass2`; `retest-phase2b/verified-adv-image-t0.0-pass3` | 3 dir(s) under `outputs/retest/phase2b/track1-image/T0.0` | scripts/run_era1_pv_stage_d.py:117-146, :184-195, :235-245, :269-274 | `7d6c46672` |
| `stage-d-512-consensus-text-high` | 1 | — | 1 dir(s) under `outputs/retest/phase3a-high/track2-text` | scripts/run_era1_pv_stage_d.py:117-146, :184-195, :235-245 | `7d6c46672` |
| `stage-d-512-consensus-image` | 1 | — | 1 dir(s) under `outputs/retest/phase3a/track1-image` | scripts/run_era1_pv_stage_d.py:117-146, :184-195, :235-245 | `7d6c46672` |
