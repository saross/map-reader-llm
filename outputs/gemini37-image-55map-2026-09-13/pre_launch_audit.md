# Pre-launch audit — Gemini 3.7 image at 55-map scale, K = 3

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

Audit of the run specified by `planning/gemini37-image-55map-2026-09-13.md`
against the `/audit-config` protocol (`~/.claude/skills/audit-config/SKILL.md`),
conducted before any Application Programming Interface (API) call. Every
figure below was read from the file or artefact cited, on 2026-09-13, at
worktree commit `dd5baf771`. No API call was made in the course of this audit;
the only compute was local dry-run validation and arithmetic over committed
metadata.

**OVERALL VERDICT: BLOCKED** — on B1 (approval provenance) and B2 (the union
builder silently drops recovery fragments), with B3 and B4 (two gate
definitions that would misfire as written) to be corrected in the card before
launch. Items 1–14 of the transmission and alignment checks all PASS; the
configuration itself is sound and byte-identical to the Gold Standard (GS)
run, and the card's cost basis reproduces exactly.

## 1. Blockers

### B1 — No first-party record of the API-gate approval; the committed record says the opposite

The card's own banner still reads "awaiting the PI's API-gate approval"
(`planning/gemini37-image-55map-2026-09-13.md`, lines 3–6). The only committed
record of a Principal Investigator (PI) decision on a 55-map 3.7 image run is
a **decline**:

| Record | What it says | Anchor |
|---|---|---|
| S152 close-out, item (4) | "55-map 3.7 image run **COSTED AND DECLINED** (PI: too dear, trigger not met)" | `planning/paper-writeup-continuity.md` § "STATE AFTER S152" |
| GS 3.7 image screen, escalation section | "There is **no resolvable new F1 high**, so the pre-agreed trigger for considering the expensive 55-map image extension is **NOT met**." Also: "Arm 2's image MCC 0.8322 likewise does not approach the committed GS MCC crown." | `results/gemini37-image-gs-2026-09-01/findings.md` § "The escalation question (PI economics rule)" |

The card advances a genuinely new argument — a tile-level Matthews
correlation coefficient (MCC) case rather than an F1 case, at K = 3 rather
than K = 5, at US$276 rather than US$395 — and that argument may well have
carried with the PI. But the pre-agreed escalation trigger recorded in the GS
findings is an **F1** trigger and is recorded as not met, and the GS findings
explicitly anticipate and dismiss the MCC route in the same sentence. A
US$261–276 campaign of roughly 102,000 calls therefore cannot start on a
relayed assertion of approval while the repository's own record reads
"declined" and the card reads "awaiting".

**To clear**: the PI's ruling recorded in the card (banner, § 6, changelog) in
the form used for the `gs-era2-verified-board-2026-09-10` sign-off, or a
direct confirmation to the executing session. Approval must also state which
cost basis the stop rule is measured on (B3).

### B2 — `merge_passes.py` silently drops every `run_N_recovery` fragment

`resolve_pass_files` derives the pass number with
`int(pass_name.replace("run_", ""))`
(`scripts/merge_passes.py`, lines 408–471). For `run_1_recovery` that raises
`ValueError` and the directory is skipped by the `except ValueError: continue`
branch. Recovery fragments are therefore invisible to the union builder.

On the GS 3.7 image passes this is not a corner case — it is where nearly all
the data lives:

| Fragment | Tiles | Features |
|---|---:|---:|
| `run_1` | 1,292 | 1,588 |
| `run_1_recovery` | 106 | 65 |
| `run_2` | **4** | **7** |
| `run_2_recovery` | 1,394 | 1,652 |
| `run_3` | **1** | **0** |
| `run_3_recovery` | 1,397 | 1,663 |
| `run_4` | 132 | 85 |
| `run_4_recovery` | 1,266 | 1,569 |
| `run_5` | 1,273 | 1,508 |
| `run_5_recovery` | 125 | 160 |

(Read from the `*.tiles.json` `completed` lists and the GeoJSON feature counts
under `outputs/gemini37-image-gs-2026-09-01/g384_ov192_g37img/` on sapphire.
All five passes are complete at 1,398/1,398 once recovery is counted.)

**Demonstrated live**: `merge_passes.py --passes 1,2,3,4,5 --threshold 1` over
that directory returns **650 features** against the committed
`union_k5.geojson`'s **674**. The failure is 3.6 % low — close enough to look
right, and it would survive any plausibility check on the count alone. What is
actually wrong is worse than the count: `total_passes` is set to the number of
pass *directories* loaded, so the vote denominator reads 5 while two of the
five passes contributed 7 and 0 detections. Every `vote_count` and every
`vote_t` operating point derived from such a union is wrong.

The card's step 2 (the GS calibration leg) is the first thing that would hit
this, and the 55-map passes will certainly need recovery fragments, because
the flex-storm window guarantees residue (§ 4.4).

**To clear**: fix `resolve_pass_files` to fold `run_N*` fragments into pass N
(and add a tier-1 test), or consolidate fragments into single pass
directories before building any union. Either way, re-derive the GS K = 3
union afterwards and check it against the committed K = 5 union of 674.

**Related, same file**: the single-merge CLI path (`--output`) computes
`pass_provenance` into its returned `stats` and then **discards it** — `main()`
ignores the return value. Only `threshold_sweep` (`--sweep --output-dir`)
writes it, into `voting_summary.json`. The brief requires `pass_provenance`
from the union builder, so the sweep path must be used and
`consensus_t1.geojson` taken as the union. The test union built above carried
only `type` and `features`.

## 2. Gate definitions that would misfire as written

### B3 — The pass-1 stop rule is basis-ambiguous, and the run's own artefact reads on the wrong side of it

The card sets a hard stop: "abort the proposer if pass 1 exceeds US$110 on the
audited basis". Three different per-tile-pass figures are in circulation for
the same GS metas:

| Basis | Rule | USD / tile-pass | Pass 1 (24,561 tiles) |
|---|---|---:|---:|
| **Audited** (`reports/token-load-audit-2026-06-12.md` § 2, on the correct 3.7 rate card) | fresh input × 0.375/1M + cached × 0.075/1M + (output + thinking) × 1.875/1M | **0.00322** | **US$79** |
| Invoice-derived | `reports/billing-reconciliation-2026-09-11.md` § 3.2 | 0.00245 | US$60 |
| **What `run.meta.json` prints** | its own `cost_estimate.total_cost_usd` | **0.00512** | **US$126 — over the stop** |

An operator or driver that checks the stop against the figure the run itself
stamps will abort a pass that is, on the card's own basis, US$31 inside
budget. The meta is wrong in three compounding ways, all confirmed at source:

1. it prices Gemini 3.7 at **Gemini 3** rates — `pricing_used` reads
   `input_per_1m: 0.5, output_per_1m: 3.0` for `model: gemini-3.7-flash`,
   where 3.7 lists at 0.75 / 3.75 (a 1.5 × understatement;
   `reports/billing-reconciliation-2026-09-11.md` § 3.2 conclusion identifies
   this same error as one of the two candidate origins of the discredited
   "0.6 × the token basis" expectation);
2. it prices cached input at the full input rate (an overstatement — here the
   dominant one, at 79 % cached);
3. it omits thinking tokens, which Gemini bills at the output rate (an
   understatement).

**Verification that the audited basis is the card's basis.** Applying rule 1
above to all ten GS fragments reproduces the card's figure exactly:
**US$22.5004 over 6,990 tile-passes = US$0.00322 per tile-pass**, against the
card's "22.50 / (5 × 1,398) = US$0.00322"
(`reports/gemini37-image-55map-costing-2026-09-10.md` § "Arithmetic"). The
card's central cost basis is therefore **correct and reproducible**; it is the
meta that is wrong.

**To clear**: pin the basis in the card, and compute it with a fixed script
rather than by reading the meta. A verified implementation is staged at
`scripts/audit_proposer_cost.py` (§ 5) — it reproduces US$22.5004 on the GS
passes.

### B4 — The ≥ 70 % cache gate cannot be met by a 5-tile smoke, by construction

The brief makes "cached share ≥ 70 % on the smoke **and** on pass 1" a gate.
Implicit prefix caching warms with volume, and the GS run measured exactly
that:

| Probe | Tiles | Cached / input | Anchor |
|---|---:|---:|---|
| Parallel probe | 5 | **16.3 %** | `outputs/gemini37-image-gs-2026-09-01/probe` meta |
| Sequential probe | 15 | **54.2 %** | `.../probe-seq15` meta |
| Full passes (8 substantive fragments) | 106–1,397 | **75.1–80.6 %** | the ten fragment metas |

The GS findings record the same shape as verdict I5: "**INFORMATIVE FAILURE** —
79.5 % at scale (probe 16 % parallel-cold / 54 % sequential)"
(`results/gemini37-image-gs-2026-09-01/findings.md`). Applying a 70 % gate to a
5-tile smoke would stop the campaign at the smoke, on a reading that is
expected and harmless.

**To clear**: the smoke's gate is mechanism-only — model, thinking level,
temperature and service tier stamped in the meta, `include_example_images`
true, 17 examples transmitted, tile size 384. The ≥ 70 % cache gate applies at
**pass scale only**, where the GS floor is 75.1 %.

## 3. What passed

### 3.1 Byte-identity with the GS image run (card § 2's central claim)

Git blob hashes at the GS run's commit `7187e81354582ba2ddd09a5a5207977a0c0c605a`
versus worktree `HEAD` = `dd5baf771`:

| File | Blob | Identical? |
|---|---|---|
| `prompts/configs/detect_brief-text-image.json` | `9fbc28e1f48f0c905590b028f18147650a0a3618` | YES |
| `prompts/system-instructions/detect_brief-text-image.md` | `274c48f47010a87a73ff205554a1b9adf22305b6` | YES |
| `prompts/configs/verify_adversarial-text.json` | `512537fb4f6b5f2ffc912814122f6bd91bdd02b7` | YES |
| `prompts/system-instructions/verify_adversarial.md` | `d5cf85ec025707a0b1735ff9eee4939d23a3d07f` | YES |

`git diff --name-only` between those two commits over `inputs/examples`,
`prompts/configs` and `prompts/system-instructions` returns **nothing**: the
17-example library is unchanged. The dry run reproduces the GS run's payload
fingerprint, `instruction_file_sha256` =
`e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12`, identical
to `configuration.system_instruction_hash` in the GS `run_1` meta. Byte
identity is CONFIRMED at the payload level.

### 3.2 Transmission check (skill step 3)

| Error mode | Finding | Verdict |
|---|---|---|
| Image flag off | `include_example_images` explicitly `true` in the config; dry-run intent preview prints "**true**" and "The varied factor is expected to reach the API payload" | PASS |
| Temperature shadowed | config 1.0, CLI `--temperature 0.7`; meta and intent preview both record 0.7 — the CLI override is the operative value, as on the GS run | PASS |
| Thinking level dropped | config `minimal`, CLI `--thinking-level low`; intent preview records `low`, matching the GS run and the card | PASS |
| Model version drift | config `gemini-3-flash`, CLI `--model gemini-3.7-flash`; intent preview and dry run record `gemini-3.7-flash` | PASS |
| Tile size mismatch | "Tile size: 384 (measured from tiles; config default was 512)" — measured from the tiles, not assumed | PASS |
| Wrong tile set | `inputs/tiles_384_ov192_55maps` with `inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json`; **24,561 of 24,561 tiles found**, matching the card and the stride-B / 3.7-text 55-map geometry | PASS |
| Wrong instruction file | `detect_brief-text-image.md` — the image track | PASS |
| Example paths broken | all 17 `inputs/examples/neutral-naming/example_01..17.png` symlinks resolve to real files; "Examples loaded: 17"; no "Reference image not found" warnings | PASS |
| Caching invocation | no `--use-cache` on the command line (flag is `store_true`, default `False`), so implicit prefix caching operates exactly as on the GS run | PASS |
| Agent model unpinned | not applicable — no agent-spawning workflow in this path | N/A |

### 3.3 Verifier arms (card § 2)

Read from the GS arm metas
(`outputs/gemini37-image-gs-2026-09-01/verifier/g384_ov192_g37img/verify_arm{1,2}/run.meta.json`):

| Arm | Config | Model recorded | T | Thinking | Items | Failures |
|---|---|---|---:|---|---:|---:|
| 1 (carried) | `verify_adversarial-text` | `gemini-3-flash-preview` | 0.0 | `minimal` | 674 | 0 |
| 2 | `verify_adversarial-text` | `gemini-3.7-flash` | 0.0 | `low` | 674 | 0 |

Matches the card exactly. `--iterations` defaults to 1 (n = 1, per Decision
24). `--service-tier` on `run_pv.py verify` defaults to `flex`.

### 3.4 GS calibration leg inputs

All five GS image passes are complete at **1,398/1,398** tiles once recovery
fragments are counted; the committed `union_k5.geojson` holds **674**
features, as the card states. The K = 3 first-N union is therefore buildable —
**subject to B2**, without which it would be built from run_1 alone.

### 3.5 Scoring and evaluation scope (skill step 6)

Read from `results/55map-final-board-r2-2026-09-06/cells/ARM2-N3-oracle/score.log`:

- ground truth `inputs/vectors/references/best-available-gt-55maps-r2.geojson`
  — **5,018 mounds**;
- bounds `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` —
  **8,541 evaluation tiles**;
- engine reports corrected F1 at 14 buffers plus MCC, sensitivity and
  specificity; `scripts/compute_corrected_f1_multi_buffer.py` carries
  `--compute-mcc`.

The 8,541-tile corpus is corroborated independently by the MCC tiering board,
whose confusion matrix for IM-k3 sums to 2,486 + 178 + 1,043 + 4,834 = **8,541**
(`results/metric-leaderboards/55map-mcc-tiering-r2.md`). Both files are present
in the worktree. `scripts/generate_post_run_report.py` carries `--all` and a
`drift_check`.

### 3.6 Card § 1 anchors, re-read

| Card claim | Re-read value | Source | Verdict |
|---|---|---|---|
| Top nine GS cells by tile-MCC all image; top three 0.877–0.889 | ranks 1–9 all image; top three 0.8887, 0.8848, 0.8766; rank 10 is text | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md` | CONFIRMED (see W1) |
| GS rank 1, both metrics: F1 0.9233, MCC 0.8264 | 0.9233 / 0.9308 screen / MCC 0.8264 | same, row 1 | CONFIRMED |
| All-3.7 text: F1 0.9190, MCC 0.7937 | 0.9190 / 0.9265 screen / MCC 0.7937 | same, row 2 | CONFIRMED |
| IM-k3 0.7110 | 0.7110, tier 1, CI [0.696, 0.725] | `results/metric-leaderboards/55map-mcc-tiering-r2.md` row 1 | CONFIRMED (see W2) |
| FOURTH-N1-oracle MCC 0.7471, F1 0.8352 | mcc 0.7471, f1_50 0.8352, P 0.8102, R 0.8617, n 5,337, point (0.96, k1) | `results/55map-final-board-r2-2026-09-06/final_board_50m.json` | CONFIRMED |
| ARM2-N5-oracle MCC 0.7147, F1 0.8871 | mcc 0.7147, f1_50 0.8871, n 4,924, point (0.95, k5) | same | CONFIRMED |
| P3 reference: 3.7 text arm 2 at N = 3, F1 0.8848 | f1_50 0.8848, mcc 0.7163, point (0.95, k3) | same | CONFIRMED |
| Instrument resolves ΔMCC ≈ 0.01: arm 1 K1→K5 −0.0099, p = 0.017 | −0.0099, p 0.0168 | `reports/k-ladder-mcc-test-2026-09-12.md` line 102 | CONFIRMED |

The card's assertion that "every figure below was re-read from the file cited
on 2026-09-13" holds for all eight anchors checked.

## 4. Warnings

**W1 — the MCC evidence for the modality case comes from F1-poor cells.** The
nine top-MCC GS cells are all image, but they carry F1 0.7112–0.7767 and sit
in tiers 6–8: `verified-adv-image-baseline-pro-vf` is MCC 0.8887 at F1 0.7309,
tier 7. They are tight, high-specificity single-pass cells, and their MCC rank
is largely a precision artefact. The card's chosen configuration — K = 3 under
a verifier — is not of that kind, and the card's own rank-1 cell (MCC 0.8264)
sits outside that top nine. P1's mechanism story is weaker than § 1's framing
implies. This does not undercut the run; it bears on how a P1 pass should be
interpreted.

**W2 — P1's two comparators have never been co-tiered.** IM-k3 (0.7110) is one
of the eight cells on the MCC tiering board; FOURTH-N1-oracle (0.7471) is on
the 35-cell F1 board and is **absent** from the MCC tiering. The card's § 1
calls IM-k3 the "sole MCC Tier 1" and 0.7471 "the 55-map MCC leader today" in
adjacent rows — two different populations, so "significantly above every text
cell" and "the leader is 0.7471" are not statements about one board. The
brief's step 7 tests against both, which handles it, but the findings document
should say so plainly.

**W3 — wall clock: this is a multi-day campaign, and the card has no
schedule.** Clean-window throughput at `--workers 150` was **3,884–4,608
tiles/h** (`run_2_recovery` 4,608, `run_3_recovery` 4,561, `run_4_recovery`
3,884), which puts one 24,561-tile pass at **5.3–6.3 h**. Inside the daily
flex-storm window it collapsed to **0.5–60 tiles/h** (`run_2`: 4 tiles in
1.83 h against 20,932 retries; `run_3`: 1 tile in 1.95 h against 20,896). Three
passes, crop extraction over the unions, four verifier arms and the scoring
and permutation work is on the order of 24–48 h of wall clock even with clean
windows, plus storm avoidance (≈ 13:00–19:00 UTC) and the daily quota reset at
19:00 AEDT. The run cannot be completed inside one session; it needs a
storm-resilient driver on the GS pattern plus an explicit handover.

**W4 — `library_hash` is no longer comparable with the GS run's value.** The
field changed from a filename hash to a content hash on 2026-09-12
(`scripts/lib_llm_metadata.py::_compute_library_hash` docstring, citing
finding 5 of `reports/name-keyed-cache-audit-2026-09-12.md`). A new run will
not reproduce the GS `library_hash` `8580ecb2258b64a0fdbcee707714bc9dd8f8e698a29d304e3980dac18a831cb4`
even though the images are identical. Argue byte-identity from
`system_instruction_hash` and the unchanged blobs (§ 3.1), and read
`configuration.library_hash_basis` before comparing.

**W5 — the verifier metas do not stamp `service_tier`.** Both GS arm metas
record `service_tier = None` and `cost_basis: "list"` with `discount 1.0`,
confirming the card's note. The flex correction is therefore not
self-evidencing from the artefact; the command line must be preserved in the
run log. Arm 2's stamped cost additionally carries the Gemini-3-rate error of
B3 (1.5 ×). Corrected verifier rates, flex: arm 1 ≈ US$0.00071 per candidate,
arm 2 ≈ US$0.00095. Against the card's ≈ 8,500 (K = 3) and ≈ 5,500 (K = 1)
unions the four arms come to ≈ **US$23**, against the card's US$37.4 on the
list basis — the card is conservative here. Corrected all-in estimate ≈
**US$261** against the card's US$276.

**W6 — no errata or decision entry covers the Gemini 3.7 family.** Neither
`protocol-errata.md` (E1–E85) nor `decisions-log.md` (Decisions 1–26) mentions
`gemini-3.7`. This is pre-existing and consistent: the 3.7 text 55-map run and
both 3.7 GS screens ran under run cards and the analysis register rather than
an erratum. Recorded so that it is not mistaken for a new deviation
introduced here, not as a blocker on this run.

**W7 — the audited basis may under-record storm spend.** `run_2` recorded
20,932 retries and a cache share of 0.000 while processing 4 tiles at a
recorded cost of US$0.032. Failed and aborted calls do not appear in
`usage_stats`, so a storm-heavy pass will be cheaper on the audited basis than
on the invoice. This is the mechanism the billing reconciliation identifies:
"Billed spend slightly exceeds the audited token basis, as it should when
aborted runs are unrecorded" (§ 3.2 conclusion; reconciliation within 2 % in
USD). Treat the audited figure as a floor when a pass has run inside a storm.

## 5. Mechanism staged on sapphire

An isolated worktree is in place at
`/home/shawn/worktrees/map-reader-llm/claude-image55` on branch
`claude-image55` at `dd5baf771`. A fresh worktree lacks three things the run
needs, all untracked in the main checkout, so they are symlinked rather than
copied (the tile set alone is 6.0 G):

| Link | Target |
|---|---|
| `.venv` | `/home/shawn/Code/map-reader-llm/.venv` (Python 3.13.3) |
| `.env` | `/home/shawn/Code/map-reader-llm/.env` (holds `GOOGLE_API_KEY`) |
| `inputs/tiles_384_ov192_55maps` | the main checkout's tile set |

Sapphire has 391 G free. The sibling worktree `claude-admission` was not
touched. The dry run below was executed from the isolated worktree and passed.

The verified cost script staged for B3 lives at
`/tmp/audited_cost.py` on sapphire during this audit; it should land in the
repository as `scripts/audit_proposer_cost.py` when the run is cleared.

### 5.1 Dry run (skill step 5) — PASS

```text
Manifest loaded. Found 24561 of 24561 tiles (24561 remaining to process).
Tile size: 384 (measured from tiles; config default was 512)
Examples loaded: 17
Model: gemini-3.7-flash
System instruction: detect_brief-text-image.md
Validation PASSED. Ready to run without --dry-run.
```

Intent preview: `include_example_images` **true**, temperature 0.7, thinking
`low`, `max_output_tokens` 8192, git commit `dd5baf771`. No warnings.

### 5.2 The invocation, replicating the GS run exactly

Flags taken from `outputs/gemini37-image-gs-2026-09-01/image-gs-recovery-driver.sh`,
lines 64–71, with only the manifest, tiles directory and output directory
changed:

```bash
.venv/bin/python scripts/4_detect_mounds_batch.py \
  --config prompts/configs/detect_brief-text-image.json \
  --manifest inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json \
  --tiles-dir inputs/tiles_384_ov192_55maps \
  --output-dir outputs/gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img/run_1 \
  --mode realtime --service-tier flex --temperature 0.7 \
  --model gemini-3.7-flash --thinking-level low --workers 150
```

`ulimit -n 8192` is required before launch and the 150-worker cap must be
respected: image mode at 400 workers exhausted the file-descriptor limit and
killed GS passes in fd/SSL storms (GS findings, "Operational notes"). Workers
are passed on the command line, never in a study YAML.

## 6. Completeness (skill step 7)

Checked and reported above: preregistration and errata cross-check (W6),
config diff and transmission (§ 3.2), byte-identity (§ 3.1), tile set and
manifest, examples, dry run (§ 5.1), evaluation scope (§ 3.5), verifier arms
(§ 3.3), cost bases (B3), cache behaviour (B4), union construction (B2), card
anchors (§ 3.6).

Not verified, and why:

- **Runtime-only**: actual cached share on a 55-map pass, actual per-pass
  throughput on the day, and whether the daily quota holds for three passes.
  These are the pass-1 gates, not pre-launch checks.
- **Example image dimensions** were not individually measured; the library is
  byte-identical to a run that passed (§ 3.1), which is the stronger check.
- **Verifier dry run** was not performed: `run_pv.py verify --dry-run` builds
  JSONL in batch mode only, and this run is real-time. The arms are instead
  verified against the GS arm metas (§ 3.3).
- **Holdout disjointness** is not applicable in the form the skill describes:
  the 55-map corpus is the deployment corpus and the operating points are
  carried from the GS calibration leg, which is a different corpus. The
  in-sample nature of swept operating points is the standing E56 caveat, and
  the card's carry-forward design is the response to it.

## 7. What must happen before launch

1. B1 — the PI's ruling recorded in the card, naming the cost basis.
2. B2 — `resolve_pass_files` fixed with a tier-1 test, or fragments
   consolidated; GS K = 3 union then checked against the K = 5 union of 674;
   unions built via `--sweep --output-dir` so `pass_provenance` is written.
3. B3 — stop-rule basis pinned in the card; `scripts/audit_proposer_cost.py`
   landed and used at the gate instead of the meta's `cost_estimate`.
4. B4 — the card's smoke gate rewritten as mechanism-only; the ≥ 70 % cache
   gate scoped to pass 1 and later.
5. W3 — a schedule and a storm-resilient driver, with the handover named.

Nothing in §§ 3 or 5 stands in the way. The configuration is correct, the
geometry and corpus are correct, the cost basis is correct and reproducible,
and the mechanism runs from an isolated worktree. The blockers are governance
and tooling, not experimental design.

## Changelog

### 2026-09-13 — Original publication

Audit conducted before any API call, at worktree `dd5baf771`, against
`planning/gemini37-image-55map-2026-09-13.md`. Verdict BLOCKED on four items:
approval provenance (B1), the union builder's recovery-fragment blind spot
demonstrated live at 650 against 674 (B2), a stop-rule basis under which the
run's own metadata reads US$126 where the audited basis reads US$79 (B3), and
a cache gate that a 5-tile smoke cannot pass at 16.3 % (B4). The card's cost
basis was reproduced exactly at US$22.5004 over 6,990 GS tile-passes once the
Gemini 3.7 rate card (0.75 / 3.75 list) replaces the Gemini 3 rates the metas
stamp. All ten transmission checks, the byte-identity comparison, the dry run
and all eight card anchors passed.
