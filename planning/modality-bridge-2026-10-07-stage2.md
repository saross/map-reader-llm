# Run B Stage 2: unions, crops and verifier legs — commands, gates, validation

> **Last revised**: 2026-10-08 (original publication; Session 163). See
> [§ Changelog](#changelog) for revision history.

**Status: READY, NOT LAUNCHED.** Everything Stage 2 needs that can be
built and checked without an Application Programming Interface (API) call is
built and checked. Launch waits on two things: Stage 1 landing to exact
coverage (Stage 1 card `planning/modality-bridge-2026-10-07.md` § 4.7), and
the Principal Investigator's (PI's) go for the verifier spend (§ 7 item 9).
No API call was made to prepare this card. The verifier rehearsal ran under a
stub client with network sockets blocked, and no API key was reachable from
the worktree it ran in. Launcher:
`scripts/modality-bridge-2026-10-07-stage2.sh`. Validation record:
`planning/modality-bridge-2026-10-07-stage2-rehearsal.json`.

## 1. What Stage 2 does

Stage 1 lodges 45 proposer passes over seven arms (Stage 1 card §§ 4.2,
4.8). Stage 2 turns each arm's passes into one union, cuts a crop per
candidate, and verifies the crops on the Batch API, exactly as the original
legs did (Stage 1 card § 2.2), with the serving mode the only intended
difference:

| Arm | K | Config version | Union | Verifier legs |
|---|---:|---|---|---|
| `g3-text` | 10 | `detect_brief-text` | `union_k10` | Gemini 3 |
| `g3-image` | 10 | `detect_brief-text-image` | `union_k10` | Gemini 3 |
| `g37-text` | 5 | `detect_brief-text` | `union_k5` | Gemini 3, Gemini 3.7 |
| `g37-image` | 5 | `detect_brief-text-image` | `union_k5` | Gemini 3, Gemini 3.7 |
| `g37-image-cache` | 5 | `detect_brief-text-image` | `union_k5` | Gemini 3, Gemini 3.7 |
| `g3-text-temp1` | 5 | `detect_brief-text` | `union_k5` | Gemini 3 |
| `g3-image-temp1` | 5 | `detect_brief-text-image` | `union_k5` | Gemini 3 |

Ten verifier legs: the six of the Stage 1 card's § 5 table, and the four of
its § 4.8. The Gemini 3 K = 5 rung is inherited from the K = 10 legs (PI
ruling D2, confirmed for Run B by D52): no K = 5 union of `g3-text` or
`g3-image` is verified.

The chain, per arm:

1. **Coverage gate.** The arm must hold exactly `run_1` .. `run_K`, each
   with its merged pass file. Each pass, with every recovery fragment, must
   cover exactly the 1,398 pinned tiles, and no tile may be processed twice.
   No Stage 1 process of the arm may be alive, and no residual file may be
   outstanding.
2. **Union.** The originals' chain: E80 20 m within-pass deduplication, E72
   exact coverage with additive recovery merge, carrier clip to
   `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson`, a
   c = 1 union with `vote_count`, and passes in numeric order. It runs
   through `scripts/modality_bridge_union.py`, whose layout adapter reads
   the batch layout: the merged file only, never the chunk files, and every
   `recovery_rd<R>` fragment in round order. A build record with each pass
   file's SHA-256 lands beside the union.
3. **Crops.** `run_pv.py extract` (150 × 150, padding 75), with the
   originals' `--tiles-dir inputs/tiles_384_ov192 --rasters-dir
   inputs/rasters`.
4. **Provenance.** `scripts/check_union_provenance.py` must classify the
   crop manifest `AGREES`. The check exits 0 on `UNRESOLVED` and
   `NOT-APPLICABLE` too, so the launcher reads the classification rather
   than the exit status.
5. **Rehearsal.** `run_pv.py verify --mode batch --dry-run` runs under the
   API-free harness. It must produce one request per candidate, construct no
   client, and match the tile-elided request signature rehearsed against the
   original legs (§ 4.3).
6. **Verify** (spends): `run_pv.py verify --mode batch --temperature 0.0
   --verifier-config prompts/configs/verify_adversarial-text.json`, with
   `--model gemini-3-flash-preview` (Gemini 3) or `--model gemini-3.7-flash
   --thinking-level low` (Gemini 3.7).

## 2. Commands

From `~/Code/map-reader-llm` on sapphire, after `git pull`. Only `verify`
spends.

| Subcommand | Does | API |
|---|---|---|
| `plan` | prints every union, extract, provenance and verify command | none |
| `validate-chain` | rebuilds the four original unions both ways and compares them with the committed unions (§ 4.1) | none |
| `anchor-gate` | reproduces the six original cells and three gaps (§ 4.4) | none |
| `check ARM\|all` | the coverage gate | none |
| `prepare ARM\|all` | check, union, extract, provenance (skips steps already done; re-checks the union's build record) | none |
| `rehearse ARM:V\|all` | the leg's batch request built API-free and checked | none |
| `estimate` | candidates and cost per leg (the union where built, else the guide size) | none |
| `verify ARM:V\|all` | gates (via `rehearse`), then lodges legs one at a time | **spends** |
| `status` | per leg: process, log age, exit, chunks submitted, results, failure lines | none |
| `wait ARM:V` | blocks until the leg is terminal (`wait_for_run.py` exit codes) | none |

`V` is `g3` or `g37`. Legs: `g3-text:g3 g3-image:g3 g37-text:g3 g37-text:g37
g37-image:g3 g37-image:g37 g37-image-cache:g3 g37-image-cache:g37
g3-text-temp1:g3 g3-image-temp1:g3`.

Per leg, the verify command is (`plan` prints all ten):

```bash
.venv/bin/python scripts/run_pv.py verify \
  --crops-dir outputs/modality-bridge-2026-10-07/<arm>/verifier/<version>/crops \
  --verifier-config prompts/configs/verify_adversarial-text.json \
  --output-dir outputs/modality-bridge-2026-10-07/<arm>/verifier/<version>/verify_<g3|g37> \
  --mode batch --temperature 0.0 \
  --model gemini-3-flash-preview          # g3
  --model gemini-3.7-flash --thinking-level low   # g37
```

**Layout.** Union, crops and legs sit under `<arm>/verifier/<version>/`, and
the deduplicated passes under `<arm>/scoring/common/<version>/run_<N>/`. That
is the shape `image_b_analysis.py` reads with `--outputs-root
outputs/modality-bridge-2026-10-07/<arm> --cell <version>`. Logs, pid files
and check records go under `outputs/modality-bridge-2026-10-07/stage2/`,
never `…/logs/`, because the Stage 1 launcher's `status` parses every
`logs/*.log` name as `<arm>-run<N>` and would fail on a Stage 2 name.

**Launch hygiene.** A leg starts detached under a wrapper shell. The wrapper
writes its own pid (from inside the job), runs the leg with all three
descriptors redirected and `PYTHONUNBUFFERED=1`, and appends `=== <time>
EXIT <status>`. The status is captured before the timestamp: `$?` read after
`$(date)` in the same string is `date`'s status, which would record every leg
as `EXIT 0`; this was caught by a direct test. Nothing follows a launch on
its line. Legs lodge one at a time; the next starts only after every chunk
of the previous one (4,000 candidates per job) has logged `Submitted batch
job`, so each storage preflight sees the earlier uploads.

A polling verifier writes **nothing** between submission and its job's end:
`lib_batch_api.poll_batch_job` logs only at a terminal state or on an error.
The pid (`kill -0`) is therefore the liveness signal, not log age, and the
poll's own 25-hour cap bounds a hang. `wait` uses a 25-hour staleness window
and the `EXIT` line. Never kill a polling leg: its job keeps running, and
the leg's `batch_jobs.json` names it for `run_pv.py batch-recover`. `verify`
refuses a leg that has `batch_jobs.json` but no `probabilities.json`.

## 3. Candidates and cost

**Rates.** These are the original legs' audited cost per candidate (each
leg's `cost_audit.json`, from the passes register
`results/passes-manifest.json`). Batch and flex carry the same rates (D19
note).

| Verifier | Original leg | Audited cost / candidates | Per 1,000 |
|---|---|---|---:|
| Gemini 3 | `g3-text` | US$2.271158 / 3,319 | US$0.6843 |
| Gemini 3 | `g3-image` | US$2.796604 / 4,065 | US$0.6880 |
| Gemini 3 | `g37-text` | US$0.555459 / 791 | US$0.7022 |
| Gemini 3 | `g37-image` arm 1 | US$0.478101 / 674 | US$0.7093 |
| Gemini 3.7 | `g37-image` arm 2 | US$0.737004 / 674 | US$1.0935 |
| Gemini 3.7 | `g37-text` swap | US$0.87 / 791 (the Stage 1 card's token basis; the register row is a lower bound) | US$1.0999 |

**Formula.** A leg costs N × r, where N is its union's feature count (known
once `prepare` has run; `estimate` prints it). r is US$0.000684–0.000709 per
candidate for the Gemini 3 verifier and US$0.001093–0.001100 for Gemini 3.7.

**Guide sizes and expected range.** Until Stage 1 lands, the guide is the
original union for the four D49 arms. For an added arm, it is its twin's
union through this chain. Within one execution, a K = 5 union's size moves
by at most 3.1 % between disjoint pass sets (passes 1–5 against 6–10 through
this chain: Gemini 3 text 2,714 against 2,687; Gemini 3 image 2,788 against
2,875; 3.7 text 791 against 773). The date component (Stage 1 card § 1:
0.04–0.06 F1 across 20 days) can add to that. **Review band: ±15 % of the
guide.** A D49 union outside it is a surprising finding to raise with the PI
before verifying (the project's calibration rule); the spend at that size is
no problem. The `temp1` arms run at T 1.0, where only T 0.7 guides exist,
and a larger union is plausible there, so outside the band is reported, not
stopped.

| Leg | Guide N | Source of the guide | Cost at guide | Review band (N) |
|---|---:|---|---:|---|
| `g3-text:g3` | 3,319 | original `union_k10` | US$2.27–2.35 | 2,821–3,817 |
| `g3-image:g3` | 4,065 | original `union_k10` | US$2.78–2.88 | 3,455–4,675 |
| `g37-text:g3` | 791 | original `union_k5` | US$0.54–0.56 | 672–910 |
| `g37-text:g37` | 791 | same union | US$0.86–0.87 | same |
| `g37-image:g3` | 674 | original `union_k5` | US$0.46–0.48 | 573–775 |
| `g37-image:g37` | 674 | same union | US$0.74 | same |
| `g37-image-cache:g3` | 674 | twin `g37-image` | US$0.46–0.48 | 573–775 |
| `g37-image-cache:g37` | 674 | same union | US$0.74 | same |
| `g3-text-temp1:g3` | 2,714 | Gemini 3 text passes 1–5 at T 0.7 | US$1.86–1.93 | reported only |
| `g3-image-temp1:g3` | 2,788 | Gemini 3 image passes 1–5 at T 0.7 | US$1.91–1.98 | reported only |
| **Ten legs** | **17,164** | | **US$12.62–13.01** | |

Against the PI's ceilings: the six D49 legs come to US$7.66–7.89 here
against the Stage 1 card's US$7.72. The four added legs come to
US$4.96–5.12 against its "about US$1.2" (fifth leg) plus "about US$3.93"
(the pair), both inside the PI's approvals (Stage 1 card § 4.8).

**A correction to the Stage 1 card's guide (flag).** § 4.8 and § 5 of that
card price the pair at "the T 0.7 K = 5 unions' 2,932 and 2,788". The 2,788
is the image cell's `union_k5.geojson`, which this chain rebuilds byte for
byte (§ 4.5). The 2,932 is a different artefact:
`outputs/grid-2026-08-18/g384_ov192/consensus-n5/consensus_t1.geojson` (the
crop manifest of the `k-ladder/k5` leg names it), a `merge_passes` consensus
not clipped to the common footprint. Of its 2,932 features, 218 lie outside
the footprint. The 2,714 inside equal, in count, this chain's union of the
same passes 1–5, so the clip accounts for the whole difference. The cost
effect is about US$0.15. The lesson is that the two Gemini 3 K = 5 numbers on
the register were not built alike: one is clipped, the other is not.

**File API.** A verifier request is 57.5–60.6 KB per candidate (rehearsal
file sizes), so the ten legs at guide size need about 1.04 GB of uploads,
well inside the 19.47 GB preflight budget once Stage 1's request files are
released (Stage 1 card §§ 4.7 item 6, 4.9 F1). The preflight still refuses
before uploading if Stage 1's uploads have not been freed.

## 4. Validation (no API)

### 4.1 The union chain rebuilds the original unions byte for byte

`scripts/modality_bridge_union.py --validate-originals` (launcher
`validate-chain`) rebuilds each original union twice: from the cell's own
real-time layout, and from a batch-layout replica. The replica holds real
copies, recovery fragments as `recovery_rd<j>`, and three decoy chunk files
beside every merged pass, so an adapter that read the chunks would double
every detection. Each rebuild was compared with the committed union, feature
by feature.

| Original | K | Committed | Legacy rebuild | Batch-replica rebuild | Files per pass (batch) |
|---|---:|---:|---|---|---|
| Gemini 3 text (`grid-2026-08-18/g384_ov192`) | 10 | 3,319 | byte-identical | byte-identical | 1,1,1,2,1,1,1,2,1,2 |
| Gemini 3 image (`image-b-gs-2026-08-28`) | 10 | 4,065 | byte-identical | byte-identical | 2,1,2,1,1,2,1,2,2,1 |
| 3.7 text (`gemini37-screen-2026-08-28`) | 5 | 791 | byte-identical | byte-identical | 2,2,2,2,1 |
| 3.7 image (`gemini37-image-gs-2026-09-01`) | 5 | 674 | byte-identical | byte-identical | 2,2,2,2,2 |

The results held at `5d868f032`, again through the launcher at
`2956c4250`, and again at `dadf935b4`, after the adapter moved to the
project's pass resolver (`lib_detection_paths.find_pass_geojsons`). Every pass of every original covers exactly 1,398 tiles, and no
main pass overlaps its fragment. The Gemini 3 text union, built in 2026-08 by
a different script (`materialise_grid_unions.py` over
`grid_prepare_scoring.py`'s passes), also reproduces, so the two chains agree
on this cell.

### 4.2 Crops and provenance

`run_pv.py extract` at HEAD, run on each committed union, reproduced every
original crop: 3,319, 4,065, 791 and 674 candidates, identical candidate
lists, and zero crop PNG byte differences. The one manifest difference was
`rasters_dir` recorded as an absolute path. The originals passed
`--rasters-dir inputs/rasters` explicitly, and with that flag the
re-extracted manifest equals the original's exactly, so the launcher passes
it. `check_union_provenance.py` classified all four re-extracted manifests
`AGREES` ("Every vote_count agrees").

### 4.3 The batch verifier request against the original real-time request

**The dry run is API-free.** This was checked in the code before relying on
it: `run_pv._verify_batch` returns at `if dry_run:` after building the
request files and before `from google import genai` / `genai.Client(...)`.
`cmd_verify` before it only reads the manifest, runs the vote gate and loads
the config. It was then checked by execution. `scripts/verifier_dryrun_harness.py`
runs the dry run with sockets blocked and `genai.Client` replaced by a stub
that records any construction. Every batch dry run recorded **0** stub
constructions and 0 breaches. The real-time capture records 1, so the
counter works.

For each original leg, the Stage 2 batch request was built at HEAD on the
full original crop manifest, with the Stage 2 flags. The original real-time
request was captured from the original leg's own commit, in a sparse
worktree, on candidates 0–2 of the original crops. The verifier config and
instruction are byte-identical at all five commits and at HEAD (sha256
`357d8a87…`, `2518d529…`).

| Leg | Original commit | Batch requests (files) | Model sent (real-time) | Content differences | Representation only |
|---|---|---|---|---|---|
| Gemini 3 text, G3 verifier | `7f13952ac` | 3,319 (1) | `gemini-3-flash-preview` | safety settings, service tier | roles, request keys |
| Gemini 3 image, G3 | `2ccf1b334` | 4,065 (2: 4,000 + 65) | `gemini-3-flash-preview` | same | same |
| 3.7 text, G3 | `b8e130fd3` | 791 (1) | `gemini-3-flash-preview` | same | same |
| 3.7 text, 3.7 | `5bd514542` | 791 (1) | `gemini-3.7-flash` | same | same |
| 3.7 image, G3 | `1c46243d2` | 674 (1) | `gemini-3-flash-preview` | same | same |
| 3.7 image, 3.7 | `1c46243d2` | 674 (1) | `gemini-3.7-flash` | same | same |

The following are the **same** on every leg and candidate: the parts
(text-only labels, crop label, the crop image by SHA-256), the system
instruction (SHA-256 `2518d529…`, as every original meta's
`system_instruction_hash`), temperature 0.0, thinking `MINIMAL` (Gemini 3)
or `LOW` (3.7), 8,192 output tokens, `application/json`, and no cached
content. Two things **differ**. The real-time call sends four safety
categories at `OFF`, and the batch request sends none (the Batch API rejects
them; `lib_verifier.build_generation_config`). The real-time call also names
tier `flex`. These are the same two differences the PI acknowledged for
Stage 1's proposer requests (D52). They are recorded here for Stage 2's own
acknowledgement (§ 7 item 9).

The model is not part of a batch request line: it is the job's model,
`--model`, resolved at submission. The originals sent `gemini-3-flash-preview`
(the config's `gemini-3-flash` resolved by `_resolve_model_name`) and
`gemini-3.7-flash`; Stage 2 pins the same names. Gemini 3.7 ignores the
0.0 it is sent and samples at 1.0 (`planning/temperature-probe-2026-10-07.md`
§ 7). The original 3.7 verifier legs were sent 0.0 too, so the request
matches.

Every batch line of a leg has one tile-elided signature, the same across
unions for a verifier: Gemini 3 `3b48d7193dcf0165…`, Gemini 3.7
`51567e8e54f8fa3c…`. The launcher's `rehearse` refuses a leg whose built
requests do not carry exactly that signature.

### 4.4 The anchor gate reproduces the six original cells

`scripts/modality_bridge_anchors.py` (launcher `anchor-gate`) re-runs
`image_b_analysis.py`'s path on the committed unions and probabilities: the
join gates, carrier reassignment, the full (prob_t × k) sweep at 20 m, and
the per-tile micro-F1 of the best set. It raises unless every F1 is within
1e-3 of its registered value through both instruments and every best point
is exact. On sapphire it ran in 3 min 15 s, and in 7 min 24 s through
the launcher at `2956c4250` with the machine under load:

| Cell | Registered | Reproduced (sweep) | Best point |
|---|---:|---:|---|
| Gemini 3 text | 0.8961 | 0.8961 | (0.15, k10) |
| Gemini 3 image | 0.8412 | 0.8412 | (0.15, k9) |
| 3.7 text, G3 verifier | 0.9139 | 0.9139 | (0.10, k5) |
| 3.7 text, 3.7 verifier | 0.9265 | 0.9265 | (0.80, k5) |
| 3.7 image, G3 verifier | 0.9254 | 0.9254 | (0.10, k5) |
| 3.7 image, 3.7 verifier | 0.9308 | 0.9308 | (0.90, k5) |

The three original gaps, text − image at 20 m, re-derived through the gap
test's permutation (10,000, seed 42): +0.0549 (p 0.0010), −0.0115 (p 0.2533)
and −0.0043 (p 0.6767), as registered.

**The entry points.** `image_b_analysis.py` and
`gemini37_image_gap_test.py` now take `main(argv)`, with defaults that
reproduce the original behaviour:

- `--anchor-set` / `--anchor-f1` replace the hard-coded text-B anchor.
- `--operating-point PROB_T,K` scores a fixed point and writes
  `verified_op_20m.geojson` (§ 9 item 2 of the Stage 1 card).
- `--write-rung-sets` keeps the inherited ladder rungs, for the K-matched
  gaps of § 9 item 5.
- `--pair LABEL TEXT_DIR IMAGE_DIR`, `--set-name` and `--reference-pair`
  replace the hard-coded pairs and the committed Gemini 3 gap.
- `--six-cell-gate` refuses to write until the gate passes.

Both were rerun on the original data. The gap test reproduced every pair
record of `results/gemini37-image-gs-2026-09-01/gap_test.json` exactly,
both with no flags and through `--pair`. `image_b_analysis.py` on the
Gemini 3 image cell reproduced every key of
`results/image-b-gs-2026-08-28/analysis.json` that today's code writes,
both with no new flag and with all of them (`--six-cell-gate
--operating-point 0.15,9 --write-rung-sets --anchor-set … --anchor-f1
0.8961`). The operating point gave F1 0.8412, P 0.8741, R 0.8107 and MCC
0.7985, the card's values, and the inherited K = 5 rung gave best F1 0.8382
at (0.15, k5) over 2,788 candidates. Two pre-existing points: the default
invocation on that cell now needs `--union-name union_k10.geojson`, because
the directory has since gained `union_k3` and `union_k5`; and the committed
`analysis.json` carries a `saturation_N3_vs_N10` block that today's code no
longer writes.

### 4.5 The launcher, on stand-in passes

A stand-in Stage 1 tree was laid out in the batch layout from the original
passes, with decoy chunks. `g37-image-cache` used the 3.7 image passes, and
the `temp1` arms used Gemini 3 passes 1–5. The launcher then ran from a
disposable sapphire worktree at `1421f3dc0` with `OUT` pointed at the
stand-in tree. The log is in the record's `launcher_tests`.

- `prepare all`: seven arms; coverage, union, crops (0 failed, 0 tile
  fallback) and provenance `AGREES`. The unions came to 3,319, 4,065, 791,
  674, 674, 2,714 and 2,788. The first four, and the 2,788, are
  byte-identical to the committed unions.
- `rehearse all`: ten legs, requests equal to candidates, 0 clients, the
  rehearsed signature on each.
- Refusals, each tested: a live Stage 1 pid for the arm; an outstanding
  residual file; a missing fragment (short coverage); an unmerged chunked
  pass; a pass rewritten after the union (stale build record); a leg holding
  `batch_jobs.json` without `probabilities.json` (no launch log written); an
  unplanned leg (`g3-text:g37`); an unknown arm.
- Launch mechanics: a test double replaced the interpreter for a live
  `run_pv.py verify` only, so no API was reachable. The wrapper wrote its
  own pid. A two-chunk leg waited for both submissions. A leg that died
  before submitting stopped the lodging. `wait` returned 0 on `EXIT 0` and 2
  on `EXIT 1`, and re-lodging a lodged leg was refused.

## 5. The Stage 1 card's § 8 gate checks, as implemented

| § 8 item | Where | Evidence |
|---|---|---|
| 1. Layout adapter (exclude `_chunk`, fold every fragment) | `modality_bridge_union.resolve_batch_pass_paths` | 25 tier-1 tests; red sentinels in a real copy (no chunk exclusion: 4 red at `db21944eb`, 5 at `dadf935b4`; lexicographic rounds: 1 red); § 4.1 batch replica |
| 2. Unions (E80, E72, clip, c = 1, `vote_count`, numeric order) | `modality_bridge_union.build_union` | § 4.1 byte-identical |
| 3. Crops | `run_pv.py extract … --rasters-dir inputs/rasters` | § 4.2 byte-identical |
| 4. Provenance guard | `provenance` (requires `AGREES`) | § 4.2 |
| 5. Verifier legs and request rehearsal | `rehearse`, `verify` | § 4.3 |
| 6. Analysis entry points and anchor gate | `modality_bridge_anchors.py`, `--six-cell-gate` | § 4.4 |

## 6. Scoring after Stage 2 (Stage 1 card § 9)

Per cell (example: the Gemini 3 image bridge cell under its original point):

```bash
.venv/bin/python scripts/image_b_analysis.py --six-cell-gate \
  --outputs-root outputs/modality-bridge-2026-10-07/g3-image \
  --cell detect_brief-text-image --k 10 --union-name union_k10.geojson \
  --verify-dir verify_g3 --operating-point 0.15,9 --write-rung-sets \
  --out-dir results/modality-bridge-2026-10-07/g3-image-g3v
```

Original points (Stage 1 card § 9 item 2):

| Cell | Point |
|---|---|
| `g3-text` | `0.15,10` |
| `g3-image` | `0.15,9` |
| `g37-text` G3 | `0.10,5` |
| `g37-text` 3.7 | `0.80,5` |
| `g37-image` G3 | `0.10,5` |
| `g37-image` 3.7 | `0.90,5` |

K = 5 cells take `--k 5 --no-ladder`. The ladder, which reads the dedup
passes the union step wrote, runs only on the two K = 10 arms; their
`verified_ladder_n5_20m.geojson` is the inherited K = 5 rung. With no
`--anchor-set`, the built-in head-to-head pairs the cell against the
ORIGINAL Gemini 3 text set. For the bridge `g3-text` cell that is the
bridge-minus-original difference of § 9 item 6, not a modality gap. The
gaps then come from:

```bash
.venv/bin/python scripts/gemini37_image_gap_test.py --six-cell-gate \
  --pair g3 results/modality-bridge-2026-10-07/g3-text-g3v results/modality-bridge-2026-10-07/g3-image-g3v \
  --pair carried-verifier results/modality-bridge-2026-10-07/g37-text-g3v results/modality-bridge-2026-10-07/g37-image-g3v \
  --pair all-3.7 results/modality-bridge-2026-10-07/g37-text-g37v results/modality-bridge-2026-10-07/g37-image-g37v \
  --reference-pair g3 --out-dir results/modality-bridge-2026-10-07
```

The K-matched Gemini 3 gap (§ 9 item 5) pairs the two inherited K = 5
rungs, each with the F1 its own `analysis.json` records. Give it its own
`--out-dir`, because a run writes `gap_test.json` and would replace the
K = 10 one:

```bash
.venv/bin/python scripts/gemini37_image_gap_test.py --six-cell-gate \
  --set-name verified_ladder_n5_20m \
  --pair g3-k5 results/modality-bridge-2026-10-07/g3-text-g3v results/modality-bridge-2026-10-07/g3-image-g3v \
  --out-dir results/modality-bridge-2026-10-07/k5
```

**Not built here:**

- **§ 9 item 4**, the tile-level interaction permutation for the gap change.
  `gap_change` is reported descriptively, as the original was.
- **§ 9 item 7**, the floors (D45, D46).

## 7. Go/no-go checklist (operator, when Stage 1 has landed)

Run in order from `~/Code/map-reader-llm` on sapphire. Any "no" stops
Stage 2.

1. **Stage 1 is complete.** The Stage 1 card's § 4.7 checks are done:
   - 1,398/1,398 per pass with fragments;
   - cached share and thinking tokens as expected;
   - finish reasons and safety blocks read;
   - audited cost;
   - pass outputs committed;
   - Stage 1's File API uploads deleted;
   - the launcher's `status` shows every pass gone, with no live recovery
     fragment.
2. **The code is current.** Run `git pull`. HEAD must include `e1795c1a1`
   (the launcher, the newest of the Stage 2 commits); check with
   `git merge-base --is-ancestor e1795c1a1 HEAD`.
3. **`bash scripts/modality-bridge-2026-10-07-stage2.sh validate-chain`**
   exits 0, with all four originals EQUAL. A failure means the chain or its
   inputs changed: stop.
4. **`… anchor-gate`** exits 0: six cells and three gaps within 1e-3, about
   3 min. If the D50 scorer change (`scorer-frames-d50-d51`; not on main at
   the time of writing) has merged and moved an anchor, stop. The bridge
   must be scored by the path that reproduces the originals, or the
   originals re-registered first.
5. **`… prepare all`** exits 0. Every arm reports `coverage OK — K passes x
   1398 tiles`, a union, crops with 0 failed, and provenance `AGREES`.
6. **`… estimate`.** Read every union size against § 3's review band. A D49
   arm outside ±15 % of its guide is a surprising finding: raise it with the
   PI before verifying. A `temp1` arm outside it is reported.
7. **`… rehearse all`** exits 0: ten legs, requests equal to candidates, 0
   clients, the rehearsed signature on each.
8. **File API headroom.** No other leg is lodged. Stage 1's uploads are
   released (the preflight still guards).
9. **The PI's go for Stage 2.** D49 returns Stage 2 to the PI "with their
   final configurations and audit verdict". D52 delegated "launch any runs
   that pass checks" for the night of 2026-10-07; whether that covers Stage
   2 is not recorded, so confirm it. The go also needs:
   - the cost from `estimate`;
   - acknowledgement that the batch verifier requests, like Stage 1's, omit
     the four `OFF` safety settings and run on the batch tier (§ 4.3);
   - the § 3 correction to the 2,932 guide.
10. **`… verify all`.** Legs lodge one at a time; the command prints
    `LODGING DONE`. Any refusal or lodging failure stops it. Re-running
    `verify all` skips finished and running legs.
11. **Watch.** Use `… status` and `… wait <leg>` per leg (0 success, 2
    exited non-zero, 5 stopped). A leg is done when it reaches `EXIT 0`, its
    results equal its candidates, and it has no failure lines.
12. **After.** For each leg:
    - audited cost (`scripts/audit_verifier_cost.py`);
    - commit the union, its build record, `scoring/`, the crop manifest,
      `probabilities.json`, `run.meta.json`, `batch_jobs.json` and the
      logs;
    - delete the leg's File API uploads.

    Then score per § 6.

## 8. Flags

- **The D49/D52 boundary for Stage 2** (§ 7 item 9). This is not settled by
  any record found.
- **The pending D50/D51 scorer change** (§ 7 item 4). The anchor gate exists
  to catch it.
- **The Stage 1 card's 2,932 guide** is a different artefact (§ 3).
- **`check_union_provenance.py` exits 0 on `UNRESOLVED`, and so does
  `run_pv.py verify`'s own vote gate,** which proceeds with a warning when
  the union cannot be resolved. A bare `verify` run outside the launcher
  could therefore spend on an unchecked manifest. The launcher requires
  `AGREES`.
- **A polling verifier is silent** (§ 2). Any watcher keyed on log age would
  call a healthy leg dead.
- **The tier-1 suite is red on main, not from Stage 2.**
  `test_no_bare_convention_a_glob_outside_this_module` flags
  `scripts/delete_landed_caches.py:161`, a bare `detections_*` glob added
  by `580c7c494` (the Stage 1 cache-deletion tool, live tonight). It wants a
  one-line move to `lib_detection_paths.find_pass_geojsons`, by its owner.
  It was left alone here because the tool runs beside live passes. Stage 2's
  own adapter had the same glob, and it was moved in `dadf935b4`.
- **The sapphire scratch** (worktrees, stand-in tree, request files) was
  removed after this card's evidence was copied into the record.

## Changelog

### 2026-10-08 — Original publication (Session 163)

Written for Stage 2 of Run B before Stage 1 landed:

- the layout adapter and union chain (`scripts/modality_bridge_union.py`,
  `db21944eb`, `5d868f032`, `ad6cd464e`, `dadf935b4`);
- the verifier rehearsal harness (`scripts/verifier_dryrun_harness.py`,
  `06e15d304`);
- the anchor gate and parameterised entry points
  (`scripts/modality_bridge_anchors.py`, `image_b_analysis.py`,
  `gemini37_image_gap_test.py`, `2956c4250`, `1421f3dc0`);
- the launcher (`scripts/modality-bridge-2026-10-07-stage2.sh`) and the
  validation record (`planning/modality-bridge-2026-10-07-stage2-rehearsal.json`),
  `e1795c1a1`.

No API call was made. Nothing was submitted.
