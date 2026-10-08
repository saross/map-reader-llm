# Run C: verifier re-invocation on Run B's unions — card

> **Last revised**: 2026-10-08 (the run record, § 9: all twenty legs landed,
> committed and audited; uploads deleted). See [§ Changelog](#changelog) for
> revision history.

**Status: DONE.** All twenty legs landed complete (34,332 of 34,332
candidates), were committed (`6c1e82014`, `9793307a5`) and audited at
US$25.32 (§ 9). Results: `results/modality-bridge-2026-10-07/findings.md`
§ 7a and `results/modality-bridge-2026-10-07/verifier-sd/`.

## 1. Why

Run B's floors (`results/modality-bridge-2026-10-07/findings.md` § 7) hold
the verifier fixed and add a borrowed verifier band of 0.001 per contrast.
The independent audit (`reports/s163-agent-records/run-b-floors-audit.md`,
finding 1) judged that band too small for the 487-tile frame. The Gemini 3
Flash verifier's re-invocation standard deviation (SD) was measured in June
on the same frame: single-run F1 SD 0.0025–0.0072 per cell, five
iterations, temperature (T) 0.0
(`results/verifier-robustness/verifier-robustness-findings.md` § 2). The
Gemini 3.7 verifier's has never been measured, and Gemini 3.7 samples at its
default T 1.0 whatever is sent (`planning/temperature-probe-2026-10-07.md`
§§ 7, 8.5), so it may be noisier.

The question that decides it: with the committed proposer SDs
(`results/modality-bridge-2026-10-07/floors/floors.json`), the primary
K = 10 gap change (−0.0529) reaches its floor when every cell's verifier SD
is about 0.0087. Above that it drops below its floor; the fully matched
contrasts survive any plausible value. Run C measures the verifier SD
directly, on Run B's own unions and crops.

## 2. Approval and hard limits

Approval: the Principal Investigator (PI), 2026-10-08, ruling D56
(`planning/pi-decisions-2026-09-20.md`): "I approve the 3.7 verifier
repeat-run noise run, full option, up to $50." The terms, as relayed in the
main session's brief and recorded in D56:

- **What:** two further verifications, replicates 2 and 3, of each of Run
  B's ten Stage 2 legs (the committed legs are replicate 1). Twenty legs.
- **Models:** `gemini-3-flash-preview` for the `:g3` legs;
  `gemini-3.7-flash --thinking-level low` for the `:g37` legs. Same
  verifier config (`prompts/configs/verify_adversarial-text.json`), the same
  `--temperature 0.0` as sent originally, the same crops, Batch API only
  (`--mode batch`).
- **Cost:** stop without lodging if the estimate's upper end exceeds US$45;
  stop if the running audited cost would pass US$50.
- **Nothing else spends.** No proposer pass, no real-time call, no other
  model. A leg's own recovery (`run_pv.py batch-recover` on its own recorded
  job) is allowed. **No leg is lodged twice** (no `FORCE=1`): a leg that
  needs re-lodging stops the run and goes back to the main session.

## 3. Legs

One call per candidate per leg. The brief's guide (about 36,500 calls) was
the Stage 2 card's guide sizes; the built unions are smaller, so the actual
count is **34,332** (17,166 per replicate).

| Leg | Candidates | Verifier | Replicate directories |
|---|---:|---|---|
| `g3-text:g3` | 3,258 | Gemini 3 | `g3-text/verifier/detect_brief-text/verify_g3_rep{2,3}` |
| `g3-image:g3` | 3,456 | Gemini 3 | `g3-image/verifier/detect_brief-text-image/verify_g3_rep{2,3}` |
| `g37-text:g3` | 789 | Gemini 3 | `g37-text/verifier/detect_brief-text/verify_g3_rep{2,3}` |
| `g37-text:g37` | 789 | Gemini 3.7 | `g37-text/verifier/detect_brief-text/verify_g37_rep{2,3}` |
| `g37-image:g3` | 661 | Gemini 3 | `g37-image/verifier/detect_brief-text-image/verify_g3_rep{2,3}` |
| `g37-image:g37` | 661 | Gemini 3.7 | `g37-image/verifier/detect_brief-text-image/verify_g37_rep{2,3}` |
| `g37-image-cache:g3` | 644 | Gemini 3 | `g37-image-cache/verifier/detect_brief-text-image/verify_g3_rep{2,3}` |
| `g37-image-cache:g37` | 644 | Gemini 3.7 | `g37-image-cache/verifier/detect_brief-text-image/verify_g37_rep{2,3}` |
| `g3-text-temp1:g3` | 3,179 | Gemini 3 | `g3-text-temp1/verifier/detect_brief-text/verify_g3_rep{2,3}` |
| `g3-image-temp1:g3` | 3,085 | Gemini 3 | `g3-image-temp1/verifier/detect_brief-text-image/verify_g3_rep{2,3}` |

Directories are under `outputs/modality-bridge-2026-10-07/`. Candidate
counts are the crop manifests' (`<arm>/verifier/<version>/crops/candidate_manifest.json`),
each equal to its union's build record.

## 4. Commands

From `~/Code/map-reader-llm` on sapphire. The launcher is
`scripts/modality-bridge-2026-10-07-stage2.sh` with `REP=<n>` (header;
`88103aef1`). Only `verify` spends.

```bash
REP=2 bash scripts/modality-bridge-2026-10-07-stage2.sh estimate
REP=2 bash scripts/modality-bridge-2026-10-07-stage2.sh rehearse all
REP=2 bash scripts/modality-bridge-2026-10-07-stage2.sh verify all   # spends
REP=2 bash scripts/modality-bridge-2026-10-07-stage2.sh status
REP=2 bash scripts/modality-bridge-2026-10-07-stage2.sh wait <arm>:<v>
REP=2 bash scripts/modality-bridge-2026-10-07-stage2.sh repair all
# the same with REP=3
```

`verify all` lodges the ten legs of one replicate one at a time; the next
leg starts only when every chunk of the previous one has logged `Submitted
batch job`. Each leg's verify command is the original's with
`--output-dir …/verify_<v>_rep<n>`: `run_pv.py verify --crops-dir … --verifier-config
prompts/configs/verify_adversarial-text.json --output-dir … --mode batch
--temperature 0.0` plus `--model gemini-3-flash-preview` or `--model
gemini-3.7-flash --thinking-level low`.

Launch hygiene (project rules). `verify all` itself runs detached:
`nohup bash -c 'echo $$ > <pidfile>; exec env REP=<n> bash scripts/… verify all' > <log> 2>&1 < /dev/null &`,
with nothing after it on the line. Each leg starts under the launcher's own
wrapper, which writes its pid and an `EXIT <status>` line. Liveness is read
from log staleness and `kill -0` on the pid, never `pgrep -f`. Failure lines
are matched case-insensitively (`error`, `failed`, `lost`, `partial`,
`Completeness gap`, `Traceback`). `wait` blocks on a terminal state, not a
success string.

## 5. Gates

Every Stage 2 gate holds per leg, unchanged: coverage and pass metas, a
current union, provenance `AGREES`, the review band, one request per
candidate with no client constructed, both pinned request signatures, the
lock, one leg lodged at a time, the File API storage preflight, and the
relaunch rules. Replicates add three:

1. **The original leg has landed** (`verify_<v>/probabilities.json`), or
   `verify` refuses.
2. **The request is the original's, line for line.** The rehearsal builds
   the replicate's request file API-free and compares it with the original
   leg's `verifier_requests.jsonl`; any differing line refuses. Record:
   `stage2/checks/request-identity-<leg>-rep<n>.json`.
3. **No committed record is rewritten.** Every log, pid, rehearsal,
   coverage, metas and provenance record carries `-rep<n>`.

## 6. Estimate and request identity (before the first lodge)

**Estimate** (the launcher's `estimate`, at the original legs' audited rates
per candidate, Stage 2 card § 3): US$12.60–12.99 per replicate, **US$25.20–25.98
for the twenty legs**, against the US$45 stop. Run B's ten legs audited at
US$12.6920 (`scripts/audit_verifier_cost.py` on the ten `verify_<v>`
directories), so the expected figure is about US$25.38.

**Request identity** (rehearsal, API-free, on sapphire at `88103aef1`): all
twenty replicates' request files equal the original legs'
`verifier_requests.jsonl`, **34,332 of 34,332 lines byte for byte**, and
each whole file's SHA-256 equals the original's. No field differs. The model
is not part of a request line (the batch job names it), so the model flags
were checked through the pinned signatures (`3b48d719…` Gemini 3,
`51567e8e…` Gemini 3.7) on every leg. Only the invocation differs. Records:
`outputs/modality-bridge-2026-10-07/stage2/checks/request-identity-<leg>-rep<n>.json`.

**File API before the first lodge:** 0 files, 0 bytes stored, no live batch
job (read-only listing, 2026-10-08T08:16:30Z). Every upload after this is
these legs', unless another session lodges concurrently; each leg's own
`batch_jobs.json` names its upload.

## 7. Analysis plan (written before any replicate result)

Script: an extension of the floors analysis, run on sapphire, zero API.

1. **Gate.** Replicate 1 (the committed legs) must reproduce every
   committed cell of findings §§ 2, 5 and 7 exactly: the same per-tile
   true positive (TP), false positive (FP) and false negative (FN) counts as
   the committed verified set, so the same F1. Nothing is written otherwise.
2. **Cells.** Every committed set (`verified_best_20m`, `verified_op_20m`,
   `verified_ladder_n5_20m`) at its own committed point (prob_t, k): F1 at
   20 m on the 487-tile frame for replicates 1, 2 and 3. The `op` and `best`
   sets apply the point to the union joined to each replicate's
   probabilities; the inherited K = 5 rung re-inherits each replicate's
   probabilities within 10 m (the K = 5 ladder's mechanism, as the floors).
   Each replicate is scored from its repaired copy (`_repaired`), as
   Stage 2 scored replicate 1.
3. **Flips.** Candidate-level accept/reject flips between replicates at each
   cell's point, among the candidates its vote gate admits: pairwise rates
   and the share split across the three.
4. **Verifier SD per cell.** The sample SD of the three F1s (n − 1 = 2),
   with its 95 % chi-square interval, s·√(2/χ²₀.₉₇₅,₂) to s·√(2/χ²₀.₀₂₅,₂),
   about 0.52 s to 6.3 s, and the range. Three replicates give a rough SD;
   it is reported as such. Sensitivity: a pooled SD per verifier family, from
   one set per leg (the `best` set), 14 degrees of freedom for Gemini 3 (seven
   legs) and 6 for Gemini 3.7 (three legs).
5. **Floors.** Findings § 7's gap and gap-change floors recomputed as
   1.96 · √(Σ proposer SD² + Σ verifier SD²), the measured per-cell verifier
   variance replacing the 0.001-per-contrast band; each contrast's ratio
   reported beside the committed one. The proposer SDs are the committed
   ones (`floors/floors.json`), read, not recomputed. Sensitivities: each
   cell's verifier SD at its chi-square upper bound, and the pooled SD. For
   each contrast, the break-even verifier SD (equal on every cell) at which
   the ratio is 1.
6. **June.** The Gemini 3 verifier's per-cell SDs set against June's
   0.0025–0.0072. Replicate 1 was verified on 2026-10-07 and replicates 2 and
   3 on 2026-10-08: a day apart, so the SD carries any day-to-day component;
   the replicate 1 minus mean-of-2-and-3 difference is reported per cell.

## 7a. Stop rules (operator)

- A leg that ends `FAILED`, `EXPIRED` or `CANCELLED`, or a chunk that never
  lodged: stop, report; do not re-lodge.
- A leg lost while polling: `run_pv.py batch-recover` on its own job named in
  its `batch_jobs.json` (Stage 2 card § 7, short legs). No new calls.
- A `PARSE_ERROR` that `repair` cannot recover: no real-time clean-up (not
  approved). Report it; the analysis states how the row is treated.
- Running audited cost: checked after each leg lands; stop before any lodge
  that could pass US$50.

## 8. After

Per leg, commit from sapphire what the original legs committed
(`probabilities.json`, `run.meta.json`, `batch_jobs.json`,
`batch_results.jsonl`, and the `_repaired/` copy), plus the logs and the
`-rep<n>` check records. Audited cost per leg with
`scripts/audit_verifier_cost.py`. Then delete the File API uploads these
legs created (named in each `batch_jobs.json`), never a file that is the
source of a non-terminal job, and record the deletions here.

## 9. Record

**Request identity:** § 6 (34,332 of 34,332 lines byte for byte).

**Lodging.** Replicate 2's `verify all` launched its first leg at 08:18:11
UTC and logged `LODGING DONE` at 08:37:02; replicate 3's first leg launched
at 08:38:34 and its `LODGING DONE` came at 08:57:26. Each ran
detached (launcher logs `stage2/logs/run-c-verify-rep<n>.log`), one leg at a
time, every gate passing again on every leg (band, rehearsal, signatures,
identity). One job per leg (every leg under 4,000 candidates). No leg was
lodged twice, no `FORCE=1`, no `batch-recover` was needed.

**Landing.** Every leg ended `EXIT 0` with `JOB_STATE_SUCCEEDED` and all its
candidates booked. The Gemini 3 legs took 5 to 14 minutes from submission;
the Gemini 3.7 legs 36 to 99 minutes (the last, replicate 3's 3.7 legs,
ended 10:19–10:27 UTC). Times per leg are in each
`stage2/logs/verify-<leg>-rep<n>.log`.

**Repairs.** One `PARSE_ERROR` in twenty legs: `g3-image-temp1`, replicate
3, `candidate_02479` ("Extra data", a stray closing brace), repaired to 0.0,
the value the batch parser booked. Its response text is byte-identical to
replicate 1's, which failed at the same position. Every other repaired copy
changed nothing.

**Audited cost** (`scripts/audit_verifier_cost.py`; record
`stage2/checks/run-c-cost-audit.json`): replicate 2 US$12.6573, replicate 3
US$12.6603, **US$25.3176** in all, against the estimate of US$25.20–25.98
and the US$50 cap. Per candidate: Gemini 3 US$0.000684–0.000710, Gemini 3.7
US$0.001072–0.001088.

**Uploads deleted** (2026-10-08, after both commits): the twenty request
files these legs uploaded, one per leg, each named in its leg's
`batch_jobs.json` and each the source of a `JOB_STATE_SUCCEEDED` job; none
was the source of a live job. The File API then held 0 files. Record:
`stage2/checks/run-c-uploads-deleted.json`.

**Not done here.** The original legs' untracked `verifier_requests.jsonl`
files on sapphire (about 1 GB) are left for the main session to delete
under D55 (Q3), as agreed. The replicates' own request files (the same
bytes, about 2 GB, untracked and gitignored) are also still on sapphire.

**Launch-hygiene notes.** (1) The first launch line, `cd … && nohup … &`,
backgrounded the whole `&&` list as a subshell that held ssh's descriptors,
so the ssh call blocked until its timeout; the driver had started once and
nothing followed the launch on the line. The second used `cd … || exit 1;
nohup … &` and returned at once. (2) One of my own waits printed "all twenty
exited" when its outer `timeout` expired, because the message followed the
loop with `;`; the status read before acting showed three legs still
polling, and the launcher's `wait` (terminal state) was used from then on.

## Changelog

### 2026-10-08 — The run record

§ 9 filled: lodging, landing, the one repair, the audited cost
(US$25.3176), the deleted uploads and two launch-hygiene notes. Status
READY TO LODGE → DONE. § 2 quotes the PI's approval from D56.

### 2026-10-08 — Original publication

Written before the first lodge: approval, legs, commands, gates, estimate
and the analysis plan.
