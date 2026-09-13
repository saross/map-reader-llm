# The cleanup metadata overwrite: mechanism, fix, and retrospective

> **Last revised**: 2026-09-14 (original publication — the PI's "fix
> permanently" ruling on checklist item 14). See [§ Changelog](#changelog)
> for revision history.

**Scope.** Why a verifier stage's `run.meta.json` could report a hundredth of
the arm's true cost, what now prevents it, a tool that audits such a stage
correctly, and a census of every stage in `outputs/**` already carrying the
damage. Every numeric claim below names the file it was read from; the
retrospective table is reproducible with one command.

## 1. The mechanism

A verifier stage is one directory: `probabilities.json` holds the per-candidate
results and `run.meta.json` the pass's token usage, execution counts, and
configuration. Two code paths write a *second* pass into an existing stage:

- **`run_pv.py cleanup`** retries the candidates the main pass failed to score.
- **`run_pv.py verify` re-invoked over the same output directory** resumes:
  `_verify_realtime` loads the existing `probabilities.json` and skips every
  candidate already scored.

Both merged the *results* correctly and neither merged the *metadata*. The
second pass's tracker produced a meta describing only itself, and
`_write_verification_outputs` wrote it over the file. Nothing in the stage
then recorded the main pass's token load — no sum, no sidecar, no marker.

The consequences, in the project's own artefacts:

| Claim | Anchor |
|---|---|
| The fourth cell's verifier stage records `items_processed: 29` against a 57,482-candidate load, and its directory holds only `probabilities.json` and that meta | `reports/r7-gaps-deltas-2026-09-11.md` § 2.5 (line 189); re-verified here — `outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/verify_37/` |
| Its Gold Standard (GS) calibration leg is the same story at `items_processed: 1` | § 2.5; re-verified — `outputs/grid-2026-08-18/verifier/g384_ov192/verify_37/`, 1 of 3,319 |
| The campaign's K = 1 arm 2 costs US$7.6875 (main) + US$0.0153 (cleanup) = US$7.7028, and an audit reading `run.meta.json` alone understates it by three orders of magnitude | `outputs/gemini37-image-55map-2026-09-13/post_run_report.md` § 3.1, on branch `gemini37-image-55map-2026-09-13` |
| The one saving grace there was an operator-era backup, `run.meta.json.pre-cleanup-20260913T225915.backup` | § 3.1's file table |

### 1.1 A correction to the item's framing

Checklist item 14 attributes the fourth cell's loss to `run_pv.py cleanup`.
The evidence does not support pinning it on that subcommand. `cmd_cleanup`
appends a `cleanup_history` entry to `probabilities.json` on every run that
had anything to recover, and the fourth cell's `probabilities.json` carries
**no `cleanup_history` at all**. Two readings survive:

1. the second pass was a **`verify` resume**, which had no backup discipline
   whatever — the ad-hoc meta copy existed only inside `cmd_cleanup`, added
   2026-08-31 in commit `2ce4536ea`, five weeks after the run; or
2. it was a cleanup whose history a later resume **erased**, because both
   writers of `probabilities.json` rebuilt the file from scratch and dropped
   the key.

Reading 2 is a second defect in the same family, and it is now fixed
(`3e0cc9d8d`): `_carry_cleanup_history` carries the record across every
rewrite, including the mid-pass incremental writer that runs every 100
completions. `scripts/audit_verifier_completeness.py` reads
`cleanup_history` to surface residual gaps, so the erasure had been
degrading a live audit tool as well as the provenance record.

The practical consequence for the fix is nil — both paths are closed — but
the attribution matters for the retrospective: a stage with a shortfall and
no history is not evidence that cleanup was never run there.

### 1.2 What was already safe

`scripts/4_detect_mounds_batch.py` merges on resume
(`merge_meta_into_existing(meta_file, meta)`, line 1349), and so does the
Batch API path in `scripts/lib_batch_api.py` (line 1413). The proposer stage
never had this defect; the verifier stage was the gap.

## 2. The fix

`94bc5c7d9` (the merge and the gate), `3e0cc9d8d` (the history carry).

### 2.1 The merged meta schema

`scripts/lib_llm_metadata.py` gained `merge_cleanup_meta` (line 1782) and
`write_merged_pass_meta` (line 1891), layered on the existing `merge_meta`
so the field-by-field arithmetic is the already-tested one. A stage that has
seen a second pass now carries, in addition to every key it carried before:

```text
run.meta.json
  usage_stats        }  the SUM over the main pass and every later pass
  execution_stats    }  (merge_meta's arithmetic: tokens and counts summed,
  cost_estimate      }   completed_items deduplicated)
  configuration         UNCHANGED — still the main pass's block, as every
                        downstream reader expects
  meta_merge_schema     "cleanup-merge/1"
  main_pass             the original pass verbatim: run_id, timestamp,
                        execution_stats, usage_stats, cost_estimate, and its
                        configuration fingerprint. Written once on the first
                        merge and never rewritten.
  cleanup_passes[]      one entry per later pass, in order:
                          pass_index, kind ("cleanup" | "resume" | "rerun")
                          timestamp, run_id
                          candidates_attempted / _verified / _failed
                          usage_stats          this pass's own block
                          cost_estimate        this pass's own figure
                          configuration        this pass's fingerprint
                          configuration_differs_from_main_pass
                          changed_configuration_fields[]
                          previous_meta_sidecar
                          verifier_config_file, verifier_config_sha256
                          instruction_file, instruction_file_sha256
                          cli_overrides{}, configuration_gate,
                          configuration_change_allowed,
                          configuration_differences{}
                          cleanup_attempt, candidates_missing_at_attempt,
                          safe_mode_applied
```

Beside it, `run.meta.pre-<kind>-<N>.json` holds the bytes of the meta as it
stood before that merge. The index advances and an existing sidecar is never
overwritten, so every state the file has held survives. The operator's
ad-hoc convention has become the tool's own, and the redundant copy
`cmd_cleanup` used to make is gone. The meta write is now atomic (tmp +
rename), because a truncated meta would now lose running totals rather than
one pass's.

Batch mode is the one path that does **not** sum: it rebuilds the request
set for the whole manifest, so its results file describes only itself and
summing would over-count. Its predecessor is preserved to a
`run.meta.pre-rerun-N.json` sidecar instead.

### 2.2 The configuration gate

Recovering candidates under a changed configuration makes a stage a mixture
of conditions while the merged meta reports one set of totals. Before any API
call, `_cleanup_configuration_gate` (`scripts/run_pv.py` line 295) compares
the cleanup's effective configuration with the main pass's as recorded in the
stage's meta, and returns a refusal (exit 1, nothing written) on any
difference. `--allow-config-change` downgrades the refusal to a warning and
records the difference on the pass entry.

The comparison is over `CLEANUP_GATE_FIELDS`
(`scripts/lib_llm_metadata.py` line 1959): `model`, `version`,
`instruction_file`, `system_instruction_hash`, `temperature`,
`max_output_tokens`, `thinking_level`, `library_hash`. Three design notes,
each a deliberate departure from a literal byte-hash of the config file:

- **The effective configuration, not the file's bytes.** The hazard is the
  command line — `--model`, `--thinking-level`, `--safe-mode-tokens` change
  what the API is asked to do without touching a byte of the config. The
  gate does record `verifier_config_sha256` and `instruction_file_sha256` as
  evidence on the pass entry, and `system_instruction_hash` *is* the
  instruction file's content digest, so that half of the byte-hash request
  is covered by the blocking set itself.
- **`--safe-mode-tokens` is a declared configuration change** and now needs
  `--allow-config-change`. One in-repo caller passes it:
  `planning/run-phase3a-recovery.sh` line 228 (`--safe-mode-tokens 2048`), a
  May-2026 runbook that has already run. It is left unmodified; a re-run
  will be refused with a message naming the flag to add, which is the right
  failure mode for a campaign whose parameter control matters.
- **A field the main pass never recorded does not block.** Legacy metas
  cannot be held to a comparison they predate; those fields are skipped, and
  a stage with no meta at all, or none with a configuration block, is warned
  about and allowed.

`model` comparison tolerates a `-preview` suffix on one side: a meta records
the name the SDK resolved (`gemini-3-flash-preview`) while the operator
types the short one, and `run_pv.py` resolves it only after a client exists.

**Known blind spot, recorded not fixed.** A `--temperature` override is not
reflected in a meta's `configuration.temperature` on either side of the
comparison — `build_generation_config` takes it as a separate argument — so
the gate cannot see a temperature change. It is recorded verbatim under
`cleanup_passes[].cli_overrides`. Injecting the override into the config dict
before the tracker is built would fix it and would change the meta content of
every future `--temperature` run; that is a separate, deliberate change and
is left for the PI.

## 3. The auditor

`scripts/audit_verifier_cost.py` (`dc5cf5656`) is the steward's ad-hoc method
promoted to a tool: it imports `rates()` and `audited_cost()` from
`scripts/audit_proposer_cost.py` and applies them to a verifier stage, which
has no `run_*` fragments for the proposer auditor to walk. It never reads one
file. A stage's total is summed over every pass on disc, in whichever
convention is present — the fixed format's `main_pass` + `cleanup_passes`
(each priced at *its own* rate card, since a cleanup may legitimately have
run under another model), the legacy backup files, or neither, in which case
the figure is labelled a **lower bound** and the tool exits non-zero.

Gate, in `tests/test_audit_verifier_cost.py` (19 tier-1 tests):

| Gate | Expected | Source of the expectation |
|---|---|---|
| GS calibration arm 1 (`gemini-3-flash-preview`, MINIMAL) | US$0.4417 over 622 | `planning/gemini37-image-55map-2026-09-13.md` line 112 |
| GS calibration arm 2 (`gemini-3.7-flash`, low) | US$0.6804 over 622 | same line; `reports/gemini37-image-55map-deltas-2026-09-13.md` line 43 |
| The leg | US$1.1221 | same |
| Per-candidate rates | 0.000710 / 0.001094 | campaign `post_run_report.md` § 3.1's GS-derived projection |
| The flex correction | each meta prints exactly 2× the audited figure | § 3.1 |
| S144 3.8 swap arm, from BOTH files | US$0.0019 + US$0.8450 = US$0.8469, where the meta alone reads US$0.0039 — **219× low** | computed here over committed metas |
| Campaign K = 1 arm 2, from BOTH files | US$7.6875 + US$0.0153 = US$7.7028 | § 3.1 |

All reproduce exactly. The campaign arm's test **skips**, naming the path it
wanted: that stage ran on sapphire and its `outputs/` tree is not in this
checkout. It becomes a live gate the moment the steward syncs the campaign,
and nothing about it was asserted from absent data.

One addition was needed to audit the S144 arm at all: `gemini-3.8-flash` in
`RATE_CARDS` at 0.75 / 3.75, the rates the project's own pricing table
records as "verified 2026-09-04 against ai.google.dev/gemini-api/docs/pricing"
and which `reports/r7-gaps-deltas-2026-09-11.md` line 35 states
independently. No Pro card was added — see § 4.3.

## 4. Retrospective: every stage carrying the damage

```bash
python scripts/audit_verifier_cost.py --sweep outputs
```

**29 stages** in `outputs/**` have a `run.meta.json` whose `items_processed`
is positive but below the number of results the stage's `probabilities.json`
holds. `items_processed == 0` is excluded: the Batch API returns no
per-response metadata, so a batch stage legitimately records zero and never
had the tokens in its meta to lose.

Columns: **results** = keys in `probabilities.json` (candidate × iteration);
**meta n** = what the surviving meta covers; **short** = the difference;
**main?** = what the main pass covered according to `cleanup_history`'s first
`initial_missing`, where one is recorded; **audited** = the audited flex
figure for what *is* on disc — a lower bound wherever the class is
UNRECOVERABLE.

| Stage (under `outputs/`) | results | meta n | short | main? | audited US$ | Class |
|---|---:|---:|---:|---:|---:|---|
| `stride-55map-2026-08-25/verifier/g384_ov192_55map/verify_37` | 57,482 | 29 | 57,453 | — | 0.0349 | UNRECOVERABLE |
| `stride-55map-2026-08-25/verifier/g384_ov128_55map/verify` | 38,713 | 6 | 38,707 | 38,707 | 0.0041 | UNRECOVERABLE |
| `55maps-generalisation/verified-v2` | 8,942 | 3 | 8,939 | 8,939 | 0.0022 | UNRECOVERABLE |
| `h11/e47-propose-brief/verified/flash-high-text-1of5` | 4,358 | 57 | 4,301 | — | 0.0389 | UNRECOVERABLE |
| `h11/pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier` | 3,736 | 1 | 3,735 | 3,735 | 0.0036 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist-text` | 3,736 | 21 | 3,715 | 3,715 | 0.0150 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief-text` | 3,736 | 27 | 3,709 | 3,709 | 0.0135 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text` | 3,736 | 41 | 3,695 | 3,695 | 0.0280 | UNRECOVERABLE |
| `h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10` | 3,601 | 1 | 3,600 | 3,600 | 0.0007 | UNRECOVERABLE |
| `grid-2026-08-18/verifier/g384_ov192/verify_37` | 3,319 | 1 | 3,318 | 3,318 | 0.0012 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5` | 2,840 | 1 | 2,839 | 2,839 | 0.0007 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5` | 2,190 | 11 | 2,179 | 2,179 | 0.0078 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist` | 2,017 | 1 | 2,016 | 2,016 | 0.0023 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5` | 2,017 | 1 | 2,016 | 2,016 | 0.0008 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief-text` | 2,017 | 19 | 1,998 | 1,998 | 0.0094 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist-text` | 2,017 | 19 | 1,998 | 1,998 | 0.0135 | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text` | 2,017 | 26 | 1,991 | 1,991 | 0.0182 | UNRECOVERABLE |
| `verifier-robustness/384-flash-high-text-ge3of5/T0.3/verified` | 4,275 | 2,775 | 1,500 | — | 1.9116 | UNRECOVERABLE |
| `flash35-pv-2x2/verified-f3vf` | 1,132 | 1 | 1,131 | 1,131 | 0.0007 | UNRECOVERABLE |
| `h8-v2/wbf/scale-4/verified` | 1,114 | 15 | 1,099 | 1,099 | 0.0109 | UNRECOVERABLE |
| `h11/pv-diag-384/verified/text-baseline-pro-verifier` | 1,047 | 21 | 1,026 | 1,026 | not priced | UNRECOVERABLE |
| `h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier` | 841 | 8 | 833 | 833 | not priced | UNRECOVERABLE |
| `gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap38` | 791 | 1 | 790 | 790 | **0.8469** | **RECOVERABLE** (in-directory) |
| `gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap37` | 791 | 2 | 789 | 789 | 0.0021 | UNRECOVERABLE |
| `gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k3_recovery-fixed` | 759 | 3 | 756 | — | **0.5349** | **RECOVERABLE** (sibling) |
| `gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k1_recovery-fixed` | 640 | 1 | 639 | — | **0.4529** | **RECOVERABLE** (sibling) |
| `h11/proposer-verifier-384/verified-adversarial-text-v1-prompt` | 572 | 1 | 571 | 571 | 0.0006 | UNRECOVERABLE |
| `h11/pv-diag-384/verified/pro-medium-image-baseline-pro-verifier` | 519 | 10 | 509 | 509 | not priced | UNRECOVERABLE |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10` | 802 | 460 | 342 | 342 | 0.3246 | UNRECOVERABLE |

**Counts: 3 RECOVERABLE, 26 UNRECOVERABLE.** The fourth cell and its GS
calibration leg are both in the unrecoverable set, exactly as § 2.5 reported;
this sweep adds 24 more stages of the same shape that no prior audit had
enumerated.

### 4.1 The three recoveries

- **`verify_swap38`** — the only stage with a prior meta in its own
  directory, `run.meta.main-2026-09-04.json`. The tool sums it: US$0.0019
  (1 candidate) + US$0.8450 (790) = **US$0.8469** over 791, US$0.001071 per
  candidate. `run.meta.json` alone reads US$0.0039 — **219× low**.
- **`verify_k1_recovery-fixed`** — a copy of sibling `verify_k1`, adjudicated
  by result keys: 640 of 640 shared, none on either side alone, same model
  and `system_instruction_hash`. Reconstructed: US$0.4521 (`verify_k1`, 640)
  + US$0.0008 (1) = **US$0.4529**.
- **`verify_k3_recovery-fixed`** — a copy of sibling `verify_k3`: 757 of its
  759 keys shared, the 2 extras being what the recovery added, same model and
  hash. Reconstructed: US$0.5329 (`verify_k3`, 757) + US$0.0020 (3) =
  **US$0.5349**.

The sibling adjudication is deliberately manual. The sweep offers sibling
*candidates* on matching model and instruction hash, and only comparing the
two stages' result keys settles whether a sibling is the stage's earlier self
or an unrelated re-run. One candidate was rejected on exactly that test:
`image-t0.0/verified-v1-n10`'s sibling `verified-v1-n10-recovery-2026-09-08`
holds 889 results (a superset, 87 extra) and covers all 889 in its own meta —
a later, complete re-verification, not this stage's main pass. Its 342-candidate
main pass stays unrecoverable. `verify_swap37` was likewise rejected: its 791
keys match sibling `verify`'s exactly, but `verify` ran
`gemini-3-flash-preview` and swap37 ran `gemini-3.7-flash`, so `verify`'s
meta is not its main pass.

### 4.2 The largest losses

By candidates: the fourth cell (57,453), the `g384_ov128` stride leg
(38,707), and `55maps-generalisation/verified-v2` (8,939). By money, the
worst is different: `verifier-robustness/384-flash-high-text-ge3of5/T0.3`
records **US$1.9116 for 2,775 of 4,275** results — a resume that kept nearly
two thirds of the pass, so its meta looks plausible and understates by about
half. That is the more dangerous shape: a 1-of-3,601 meta announces itself,
a 2,775-of-4,275 meta does not.

### 4.3 What the sweep cannot price

Three Pro-verifier stages return "not priced": `audit_proposer_cost.RATE_CARDS`
has no `gemini-3.1-pro-preview` entry. The project's pricing table records
2.00 / 12.00 for it, but no source there gives the Pro **cache-read** rate,
and the auditor's contract is to fail rather than guess a rate card — that
guess is how the meta's own figure went wrong. Their cache share is in any
case 0.000 (every crop is a distinct image), so a Pro card added with a
verified cache rate would price them immediately. Their shortfalls are
reported; only the money is missing.

## 5. What did NOT change

- **No committed `run.meta.json` was rewritten.** The retrospective
  reconstructs sums *into this report*; every stage directory in `outputs/`
  is byte-for-byte as it was. The sweep and the auditor are read-only.
- **No probabilities, detections, evaluations, or board cell moved.** Nothing
  here touches a result.
- **A stage that never sees a second pass writes exactly what it wrote
  before**: no `main_pass`, no `cleanup_passes`, no `meta_merge_schema`, no
  sidecar, the same key set and the same `indent=2` formatting. That is a
  tier-1 regression test, not an assurance.
- **`configuration` in a merged meta is still the main pass's block**, as
  `merge_meta` has always left it, because every downstream reader treats it
  as the pass's configuration.
- **`planning/run-phase3a-recovery.sh` is unmodified**, including its
  `--safe-mode-tokens 2048`. A re-run will now be refused until
  `--allow-config-change` is added; the refusal message says so.
- **Nothing on sapphire was touched**, and no file under
  `outputs/gemini37-image-55map-2026-09-13/` or on the campaign branch was
  modified — both belong to the image-campaign steward.

## 6. Tests

| Module | Tier-1 tests | Covers |
|---|---:|---|
| `tests/test_cleanup_meta_merge.py` | 24 | merge arithmetic (usage, counts, cost); the verbatim `main_pass`; the indexed sidecar and its never-overwritten index; a second cleanup extending rather than rewriting; a batch rerun preserving without summing; the `cleanup_history` carry in both writers; the gate's refusal, override, safe-mode case, resolved-model tolerance and missing-meta case; that `cmd_cleanup` refuses before `_verify_realtime` is reached; and the no-second-pass byte-identity regression |
| `tests/test_audit_verifier_cost.py` | 19 | the GS gate (both arms, the leg, per-candidate rates, the flex correction, the standard-tier doubling); two-file stages in both conventions; sidecars not double-counted; the lower-bound shape; sweep classification, batch exclusion, threshold, `cleanup_history` reading, and that an unpriceable stage is reported rather than dropped |
| `tests/test_run_pv.py` | 1 amended | `test_cleanup_leaves_the_main_meta_untouched` replaces `test_cleanup_backs_up_run_meta`, which asserted the ad-hoc backup this change removed |

## Changelog

### 2026-09-14 — Original publication

Written for the PI's "fix permanently" ruling on item 14 of
`planning/documentation-foundation-checklist-2026-09-13.md`. Records the
overwrite mechanism and the correction to its attribution (§ 1.1), the merged
meta schema and the configuration gate (`94bc5c7d9`), the `cleanup_history`
carry (`3e0cc9d8d`), the promoted auditor (`dc5cf5656`), the `pgrep -f`
process note (`1a8bebc0e`), and the first census of the damage: 29 stages,
3 recoverable, 26 unrecoverable. No prior numerical claims were revised —
the two figures this report inherits, § 2.5's fourth-cell counts and the
campaign's US$7.7028, are reproduced unchanged.
