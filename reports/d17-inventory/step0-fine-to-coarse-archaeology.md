# H2 Condition C (fine-to-coarse) — data archaeology

**Date**: 2026-07-27
**Scope**: Was there ever a principled, recorded decision not to run H2 Condition C?
**Method**: repo grep + `git log --all`/`git blame`, `~/cc-archives` indexed session search
(`~/personal-assistant/scripts/search-sessions.py`, PostgreSQL `session_chunks`).
**Constraint**: read-only. Every specific below carries a file+line, commit hash, or
`archive_dir:turn` handle.

---

## 1. Verdict

**No principled decision was ever made by the PI. What exists is (a) a silent
structural omission dating from 2026-01-01, (b) an explicit request for
confirmation that the PI never answered, and (c) a post-hoc rationalisation
written 2026-03-15 that gives a *different* reason from the one in the
execution plan.**

Three distinct things must be kept apart:

### 1a. The structural omission (durable, verifiable, 2026-01-01)

`docs/methodology/preregistration/execution-plan.md:587-590` — the Phase 3d
"Design" section reads, in full:

> Compare:
>
> - Condition A: Single-stage detection (optimal from Phase 2)
> - Condition B: Proposer → Verifier pipeline

`git blame` on those lines:

- line 590 (`Condition B`) — `b91d76884`, **2026-01-01**
- line 589 (`Condition A`) — `855a11275`, 2026-01-04

The preregistration's three-condition table (A/B/C) was written **later**, at
`af486fa56` (**2026-01-08**), `osf/preregistration.md:465-469`. So the
execution plan never contained Condition C at any point in its history — not
because it was removed, but because the operational plan and the registered
design were drafted on separate tracks and never reconciled. **There is no
commit that removes Condition C, and no commit message anywhere in
`git log --all` that explains its absence.**

### 1b. The unanswered question (2026-03-07) — the decisive evidence

Session `2026-03-07T05-59_c634c7c3` (project `map-reader-llm`). The assistant
raised Condition C **twice**, both times as an open question:

- **turn #3568**: *"4. **Condition C (fine-to-coarse)** — confirm dropped?"*
- **turn #3509**, in a turn explicitly headed *"Here's my assessment of Phase 3d
  readiness, with several design decisions that need your input"*:

  > **4. Condition C (fine-to-coarse)**
  >
  > The preregistration specifies 3 conditions (A: single-stage, B:
  > coarse-to-fine, C: fine-to-coarse). The execution plan drops C based on poor
  > pilot results (37% recall at 1024px). Confirm C stays dropped?

  and in the recommendation table of the same turn:

  > | Condition C | Drop (confirm) | Poor pilot, execution plan already excluded it |

**Shawn never answered.** His three substantive replies in that exchange —
turns **#3573**, **#3598**, **#3601** — address Phase 2e, the 1+1 vs consensus
question, verifier prompt granularity, and dual-track, and are **silent on
Condition C**. Verified by retrieving all 75 indexed user turns for that
session; user turns as short as 14 characters are indexed (`min(char_len)=14`
for `role='user'`), so the index is not filtering out a short "yes".

> **Caveat (volatility)**: the `session_chunks` index holds 361 of 4,198 turns
> for this session. User-turn coverage appears complete for the window
> 3500–3720 (7 user turns, including a 14-char one and an interruption
> marker), but I cannot *prove* no user turn is missing without decompressing
> the archive, which the search tooling explicitly forbids at query time. The
> claim "Shawn never answered" is therefore **strong but not absolutely
> certain**. It has **no durable corroboration** — no session-log entry, no
> Observation, no commit records this exchange.

Note a trap: turn #3598 discusses *"For C"* and *"For D"* — these are **verifier
prompt variants C and D of the H2 pilot**, not H2 Condition C. Do not read that
turn as a Condition C decision.

### 1c. The post-hoc rationalisation (2026-03-15)

`docs/methodology/preregistration/hypothesis-tracking.md:86-87`:

> **Note**: Fine-to-coarse (H2-C) was not tested — the coarse-to-fine results
> were strong enough that context expansion was deprioritised.

`git blame` → commit `7fb1d0b47`, **2026-03-15 12:55:14 +1100**, subject
*"docs: update hypothesis tracking to reflect current completion status"*, body:
*"The tracking matrix was last updated 2026-02-11, before H2-H5, H9, and H11
were completed… This addresses repeated misreadings of H2 as incomplete."*
Co-authored by Claude Opus 4.6.

This is **documentation catch-up written four days after H2 was marked complete
(2026-03-11)**, not a decision record. Critically, **it gives a different reason
from the execution plan's**:

| Source | Date | Stated reason for no C |
|---|---|---|
| execution-plan.md:587-590 | 2026-01-01 | *(none — C simply absent)* |
| 2026-03-07 turn #3509 (assistant) | 2026-03-07 | "poor pilot results (37% recall at 1024px)" |
| hypothesis-tracking.md:86-87 | 2026-03-15 | "coarse-to-fine results were strong enough" |

The 2026-03-15 rationale ("B was good enough") is **logically incompatible with
the preregistration's own framing**, which predicted *neither* architecture
would help and treated C as a confirmatory test in its own right
(`osf/preregistration.md:453` — *"**Status**: Confirmatory (architectural)"*).
B succeeding is not a reason to skip C; under the registered design it is a
reason to *run* C.

### 1d. Silence in the durable record

- **`protocol-errata.md`**: **57 errata (E1–E57), none mentions** fine-to-coarse,
  "fine to coarse", "Condition C", "H2-C", "context expansion", or
  "context-expanded". Verified by grep, exit status 1. **A registered
  confirmatory condition was dropped without an erratum.** (E37, 2026-03-15,
  `protocol-errata.md:894-908`, documents PV/Condition B as a *post-hoc
  extension* and never mentions that a registered sibling condition went
  unrun.)
- **`docs/notes/reflections/session-log.md`** (7,409 lines): **zero** matches for
  fine-to-coarse / fine to coarse / context expansion / H2-C.
- **`docs/notes/working-notes.md`** (371 Observations): **zero** matches for the
  same terms. **No Observation number covers this.**
- **`decisions-log.md`**: zero relevant matches.
- **`git log --all -S"fine-to-coarse"`**: after `4cd80e7da` (2026-01-20), the next
  commit touching the string is `38a5e598f` (**2026-07-27**, today's D17
  inventory) — a **five-month silence**.
- **No branch, stash, or tag** relates to fine-to-coarse. Branches present:
  `main`, `origin/feat/parallel-batch-eval`, `origin/fix/diversity-crs-mislabel`,
  two `worktree-agent-*` branches (2026-05-03, 2026-06-08) — all unrelated.

---

## 2. The H11 question: conflation of *mechanism*, but the substance is right

**Answer: the PI is remembering a real experiment and a real finding, but it is
not H11. It is the January 2026 tile-size calibration pilot. H11-as-run could
not possibly have informed the Condition C decision, because H11 never tested a
tile larger than 512 px.**

### What H11 actually tested

`osf/preregistration.md:955-958` registers H11 as **two** conditions:

| Condition | Tile Size |
|---|---|
| A | 512×512 (baseline) |
| B | 384×384 |

`hypothesis-tracking.md:30` — *"H11 | Tile Size Effects | … | Complete (384
pathway closed) | 2026-03-15"*. H11 as-run explored 512/384 (and 256 in
`outputs/h11/pv-diag-256/`). **It never ran 1024 px.** So no H11 result could
supply the "larger tile ⇒ fewer hits" evidence.

### What actually produced that evidence

`archive/pilot-tile-size/` — a **multi-scale calibration pilot dated
2026-01-07** (`archive/pilot-tile-size/results/multiscale-pilot-results.md:3`),
19 ground-truth mounds across 10 stratified regions, testing **256 / 512 /
1024 px** at 5-pass voting. Its 1024 px table
(`multiscale-pilot-results.md:64-72`):

| Threshold | Precision | Recall | F1 |
|---|---|---|---|
| 2/5 | 0.292 | **0.368** | 0.326 |
| 3/5 | 0.556 | 0.263 | 0.357 |

with the verdict at `:72` — *"**Character**: Higher precision but unacceptably
low recall (37% at 2/5)."*

**This single pilot is the common ancestor of both memories.** It feeds:

- the H2 Condition C pilot note, `osf/preregistration.md:484`: *"Calibration
  testing found 1024px tiles achieve only 37% recall at 2/5 threshold, limiting
  confirmation value."*
- the H11 tile-size rationale, `osf/preregistration.md:963`: *"Pilot testing at
  1024px confirmed higher precision (0.28) but unacceptably low recall (0.37) at
  2/5 consensus voting threshold, missing ~63% of mounds, suggesting larger
  tiles under-detect."*

Both notes entered the preregistration in the **same commit**, `af486fa56`
(2026-01-08, *"Update to v4.2 with pilot context and pooling methodology"*).

### So: conflation or causal link?

**Both, precisely delimited:**

- **The PI's *reasoning* is genuinely attested and predates the drop.** "As tile
  size grows, hits fall, so a 1024 px re-query would mostly reject candidates
  and be uninformative" is exactly what `multiscale-pilot-results.md:128` says:
  *"**Key limitation**: With 1024px recall at only 37%, the large-tile context
  cannot confirm most true positives. The fine-to-coarse approach requires a
  context scale with reasonable recall, which 1024px lacks in this
  configuration."* This is **not** post-hoc reconstruction.
- **The attribution to H11 is a conflation.** The evidence came from a
  pre-registration calibration pilot (2026-01-07), not from the registered H11
  experiment (completed 2026-03-15, 512 vs 384 only). The two are linked only
  because the same pilot wrote both prereg notes.
- **Was any of it ever *used* as a stated reason to drop C?** Only once, and by
  the assistant, not the PI: turn #3509 (2026-03-07) cites *"poor pilot results
  (37% recall at 1024px)"*. That is the assistant reading
  `osf/preregistration.md:484` back to Shawn — **the chain the coordinator asked
  me to confirm is confirmed**. It is a characterisation offered in a question,
  which went unanswered, and it never made it into any durable artefact. The
  durable artefact that *does* exist (hypothesis-tracking.md:86-87) gives the
  *other*, weaker reason.

---

## 3. Was anything built in the fine-to-coarse lane?

**Yes — more than expected, though nothing that ever called the API in
Condition C form.** Three artefacts:

### 3a. A working fine-to-coarse simulator that RAN (January 2026)

`archive/pilot-tile-size/scripts/analyze_multiscale_voting.py:675` —
`def strategy_fine_to_coarse(...)`, documented at `:685` as *"Strategy 10:
Fine-to-Coarse Pipeline Simulation"*, with promotion/rejection tracking
(`:1216-1270`) and a reporting block (`:1366-1383`).

**It produced results.** `archive/pilot-tile-size/outputs/multiscale_full_sweep.csv`
contains 7 `fine_to_coarse` rows:

| config | P | R | F1 |
|---|---|---|---|
| medium_large_conf5_unc2-4 | 0.4615 | 0.6316 | **0.5333** |
| medium_large_conf4_unc2-3 | 0.3714 | 0.6842 | 0.4815 |
| small_large_conf5_unc2-4 | 0.3333 | 0.8947 | 0.4857 |
| small_medium_conf5_unc2-4 | 0.2133 | 0.8421 | 0.3404 |
| (+3 more) | | | |

Also present in `archive/pilot-tile-size/outputs/multiscale_analysis.json` under
`/multiscale_results/fine_to_coarse`, and written up at
`archive/pilot-tile-size/results/multiscale-pilot-results.md:117-128`
("Fine-to-Coarse Performance", with a promotion-rate column: 10–26%).

**Important qualification** — this is a *simulation*, and the design doc says so
at `archive/pilot-tile-size/results/multiscale-voting-analysis.md:690-692`:
*"Caveat: Real pipeline would centre large tile on candidate and use
verification prompt. This approximation uses fixed large tiles with detection
prompt."* So it approximates Condition C using pre-existing fixed-grid
multi-scale detections; it does **not** centre a crop on a candidate, and it
uses a detection prompt rather than a verification prompt. **It is evidence
about Condition C, not an execution of it.**

### 3b. A drafted verification prompt that never became a file

`docs/methodology/preregistration/osf/preregistration-appendix-prompts.md:1129-1160`
— §1.7 *"Fine-to-Coarse Verification Prompt (H2 Context Expansion)"*, §1.7.1
`verify_context-expanded.md`, marked *"**Status**: Confirmatory — prompt to be
used in H2 fine-to-coarse direction testing"*, with full prompt body.

**The file `verify_context-expanded.md` was never created.** `git log --all`
over `*context-expanded*` returns nothing; no commit in history adds it. Its
absence was noticed and explicitly waved through on **2026-01-17**
(`2026-01-17T12-38_d40e04c4` turn #681, duplicated in
`2026-01-17T03-43_49cb5c21` turn #1272):

> **3. verify_context-expanded.md: Confirmed TBD**
> This is for H2 fine-to-coarse (Condition C). The preregistration explicitly
> states it will be "refined based on Stage 1 results" - so it's correctly
> absent at this stage.
> …
> **No action** needed for verify_context-expanded.md (correctly TBD)

That is the last moment Condition C was treated as live. It was deferred as
"correctly TBD", and never revisited.

**Flag — an internal inconsistency in the registered spec**: the preregistration
body says the Stage 2 crop is **~1024×1024** (`osf/preregistration.md:482`)
while the appendix prompt tells the model it is looking at **~896×896**
(`preregistration-appendix-prompts.md:1144`). A faithful replication must pick
one and note the deviation.

### 3c. No config, ever

`prompts/configs/` contains no `expand_*.json`; `prompts/system-instructions/`
contains no `expand_*.md` or `verify_context-expanded.md` (verified by directory
listing). The registered implementation mapping at `osf/preregistration.md:2015`
requires `detect_*.json` + `expand_*.json` for fine-to-coarse. `git log --all
--diff-filter=A` shows neither was ever added. **Both prior checks in the brief
are confirmed: no `expand_*.json` exists, and no erratum mentions Condition C.**

### 3d. Prehistory (pre-v4.0 numbering)

Fine-to-coarse was **H10** before the v4.0 restructure. Earliest trace:
`2025-12-22T03-05_6c7214f9` turn #1800 — *"**Alternative to two-stage**:
'Fine-to-coarse validation' — run full detection, then verify uncertain cases
with expanded context"*. The ≥0.05 F1 stopping rule was cascaded to it at
`2026-01-03T04-45_a76fa1a1` turns #760/#780 (*"Same threshold applies to H10
(fine-to-coarse)"*). Merged into H2 at v4.0: `2026-01-06T22-04_f4cb3541` turn
#394 (*"…fine-to-coarse validation) has been merged into H2. Both two-stage
directions are now tested together."*). A later doc-consistency fix removed a
stale label — `execution-plan.md:814`: *"fixed H10 description (training pool
size, not fine-to-coarse)"*. **No pilot code or outputs exist under the old H10
identifier beyond the Strategy 10 simulator in §3a.**

---

## 4. Timeline: when did Condition C stop being live?

| Date | Event | Anchor |
|---|---|---|
| 2025-12-22 | Fine-to-coarse first proposed (as "H10") | `2025-12-22T03-05_6c7214f9` turn 1800 |
| 2026-01-01 | Execution plan Phase 3d drafted with **A and B only** | `git blame` → `b91d76884`, `execution-plan.md:590` |
| 2026-01-06/07 | H10 merged into H2 as Condition C | `2026-01-06T22-04_f4cb3541` turn 394 |
| **2026-01-07** | **Multi-scale pilot runs; fine-to-coarse simulated; 1024 px = 37% recall** | `multiscale-pilot-results.md:3,67,128`; `multiscale_full_sweep.csv` |
| 2026-01-08 | Both the A/B/C table and the discouraging pilot note enter the prereg **in the same commit** | `af486fa56`; `osf/preregistration.md:465-469,484,963` |
| **2026-01-17** | `verify_context-expanded.md` absence noticed, ruled *"correctly TBD"*, **no action** — last moment C is treated as live | `2026-01-17T12-38_d40e04c4` turn 681 |
| 2026-01-20 | Last commit to touch the string "fine-to-coarse" until July | `4cd80e7da` |
| 2026-03-07 | Assistant asks twice to *"confirm dropped"*; **PI does not respond** | `2026-03-07T05-59_c634c7c3` turns 3509, 3568; replies 3573/3598/3601 |
| 2026-03-11 | H2 marked Complete | `hypothesis-tracking.md:14` |
| **2026-03-15** | E37 (PV as post-hoc extension) **and** the retrospective "deprioritised" note land the same day | `protocol-errata.md:894-908`; `hypothesis-tracking.md:86-87` (`7fb1d0b47`) |
| 2026-07-27 | D17 inventory documents C as NOT executed | `reports/d17-inventory/d17-inventory-h1-h4.md:429-448` |

**Correlation with Condition B's take-off**: erratum E37 is dated 2026-03-15,
the *same day* as the retrospective note. But B's real take-off is 2026-03-07 —
the session where the H2 pilot was built and run and produced *"remarkably
strong"* results (turn #3803). Condition C's fate was sealed in that same
session: it was raised as a question at the top of the turn, the conversation
moved to building B's pilot, and it was never mentioned again. **The 2026-03-15
note is the paperwork; the 2026-03-07 non-answer is the event.** The deeper
cause is older still — C was absent from the operational plan from 2026-01-01,
so no one was ever going to run it by following the checklist.

---

## 5. Feasibility of running Condition C now

**Verdict: highly feasible. Most of the infrastructure exists; the gap is one
prompt file, one config, and one orchestration script (~1–1.5 days).** A
faithful replication is possible with one unavoidable deviation (§5d).

### 5a. Stage 1 — 512 px 5-pass consensus pools: EXIST

`outputs/retest/phase3a/` is the 512 px corpus. Verified empirically:
`outputs/retest/phase3a/track1-image/T0.7/run_1/detections_T0.7_run01.geojson`
references **330 distinct source tiles**, all present in `inputs/tiles/`
(360 tiles, confirmed 512×512 via PIL), with x-offsets `0, 448, 896, 1344, …` —
**stride 448 = 512 − 64 overlap**, inconsistent with 384 (320) and 256 (192).
Structure: `track1-image` and `track2-text`, each at T0.3/T0.7/T1.0, with
**30 runs** per cell (`ls -d …/T0.7/run_* | wc -l` → 30).

- Registered Stage 1 is **5-pass**. With 30 passes available, a 5-run subpool is
  a strict subset — and `scripts/build_phase3_subpool_consensus.py` already
  exists to build exactly this.
- Consensus GeoJSONs carry the needed fields: `scripts/lib_consensus.py:238`
  emits `vote_count`, alongside `total_passes`, `contributing_passes`,
  `source_tiles`, `cluster_size` (confirmed on a live file,
  `outputs/55maps-generalisation/consensus/consensus-4of5.geojson`).

**⇒ The 2/5–3/5 uncertain-candidate set is directly derivable**: filter
`vote_count in (2, 3)` on a 5-pass consensus built at threshold 1. No new
analysis code required.

> Note: the 4-map gold-standard pool `outputs/gs/gold-standard-v2/` is **384 px**
> (`…/proposer/detect_brief-text/run_1/*.meta.json` →
> `"manifest_path": "inputs/tiles_384/full_evaluation_manifest.json"`), so it is
> *not* the right Stage 1 source for a faithful C. Use `outputs/retest/phase3a/`.

### 5b. Stage 2 — 1024 px candidate-centred crops: SUPPORTED, no new code

`scripts/extract_candidates.py` already does precisely what Condition C Stage 2
needs:

- crops **from source GeoTIFF rasters**, not tile PNGs, with `boundless=True`
  (per its header, the E33 fix: *"This prevents edge-truncated crops when
  detections fall near tile boundaries"*) — so a candidate near a tile edge
  still yields a full, centred 1024 px window;
- crop size is `padding * 2` (`extract_candidates.py:188`), so **`--padding 512`
  yields exactly 1024×1024**;
- rasters are present: `inputs/rasters/` holds the 4 GS sheets
  (`K-35-052-4_32635.tif`, `K-35-053-3_Elenovo.tif`, `K-35-062-2_Rakovski.tif`,
  `K-35-078-1_Lesovo.tif`) plus the `Russian1981_32635/` collection.
- it consumes a proposer GeoJSON with a `source_tile` property — which the
  consensus output provides.

### 5c. What must be newly built

| Item | Effort | Note |
|---|---|---|
| `prompts/system-instructions/verify_context-expanded.md` | ~1 h | Body already drafted verbatim at `preregistration-appendix-prompts.md:1136-1160` — transcribe, resolve the 896/1024 wording |
| `prompts/configs/expand_*.json` | ~1 h | Registered name (`osf/preregistration.md:2015`); model on `verify_*.json` |
| Orchestration (Stage 1 subpool → filter 2/5–3/5 → crop at padding 512 → verify) | ~4–6 h | Glue only; `run_pv.py` / `lib_verifier.py` / `5_verify_crops.py` supply the calling machinery. `lib_verifier.py:364 build_candidate_content()` takes crops from a manifest, which `extract_candidates.py` emits |
| Evaluation | ~1–2 h | `evaluate_pv_results.py` + existing threshold-sweep tooling apply unchanged |
| Erratum + hypothesis-tracking correction | ~1 h | Needed regardless — see §6 |

**Total: ~1–1.5 days of work, no new dependencies, no schema change.**

### 5d. What makes a *fully* faithful replication impossible — flag

1. **Prompt-size ambiguity (resolvable, must be declared).** Body says
   ~1024×1024 (`:482`), appendix prompt says ~896×896 (`:1144`). Whichever is
   chosen is a documented deviation from the other.
2. **Model drift — the serious one.** The registered design assumed the
   2026-01 model. `protocol-errata.md` E37 and Observation 163 already record
   model drift affecting H2 Condition B (`hypothesis-tracking.md:75-77`:
   F1=0.796 → 0.732 after config audit). A Condition C run in July 2026 is a
   **different model** from the one the January pilot characterised, so the
   "37% recall at 1024 px" premise is itself stale and would need re-measuring
   before it could be treated as the reason C is uninformative. **This is a
   reason to run C, not a barrier.**
3. **Stage-1 provenance.** The registered Stage 1 is "optimal config, 5-pass".
   `outputs/retest/phase3a` is the 340→330-tile retest corpus, not the original
   60-tile holdout the prereg envisaged (see E-series on the corpus expansion,
   `protocol-errata.md:888`). This is the *better* choice statistically but is a
   scope deviation to declare.
4. **The pilot's own caveat stands.** If 1024 px recall really is ~37%, the test
   will be *uninformative in the direction the PI predicts* — most uncertain
   candidates rejected. That is a **finding worth reporting**, and it discharges
   a registered confirmatory condition. It is not a reason to skip it a second
   time.

### 5e. Cost — NOT estimated

Per the brief, I will not estimate API cost without anchoring it. The audited
basis (`reports/token-load-audit-2026-06-12.md:117-118`) gives a verifier-call
figure of **$0.000684/call** (flex tier; 16,482 calls, input exactly
1,792/call → flex $11.27). **That anchor is for 384 px PV crops, not 1024 px
context-expanded crops**, whose input-token load would be materially higher
(≈7× the pixel area) and which the audit at `:21-23` warns is systematically
under-priced in the manifests (standard vs flex rates; thinking tokens omitted
from `cost_usd`). **A defensible figure requires measuring input tokens on a
handful of real 1024 px crops first.** The candidate count itself is cheap to
determine exactly — build the 5-pass consensus and count `vote_count in (2,3)`.

---

## 6. Bottom line for the paper

Condition C is a **registered confirmatory condition** (`osf:453`) that was
**never run**, with:

- **no erratum** among 57 (the only omission of this kind found),
- **no Observation** among 371,
- **no session-log entry**,
- **no commit** explaining it,
- **no PI decision** — only an assistant's twice-asked, never-answered "confirm
  dropped?",
- and a **retrospective note whose stated reason ("B was strong enough")
  contradicts the registered logic**, which predicted neither architecture would
  help and required both to be tested.

The honest characterisation for the paper is **not** "we deprioritised C because
B succeeded". It is: *C fell out of the operational plan at drafting time
(2026-01-01), a January pilot supplied a genuine but never-formalised reason to
doubt it (1024 px, 37% recall at 2/5), and the omission was never ratified.*
The PI's recollected reasoning is real and attested — it simply lives in
`archive/pilot-tile-size/`, not in H11, and it was never converted into a
decision.

**Minimum remedial action** (independent of whether C is run): file an erratum,
and correct `hypothesis-tracking.md:86-87` to state the actual reason and its
evidence base.
