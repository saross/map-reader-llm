# Forensic audit — what the preregistration says about proposer–verifier (PV), and whether erratum E37 is accurate

**Audit date**: 2026-07-27
**Repository**: `/home/shawn/Code/map-reader-llm` (branch `main`, HEAD **`38a5e598f`** — "docs(prereg):
D17 per-hypothesis inventory + outline correction"; working tree clean throughout)
**Scope**: read-only. No repository file was modified.

> **Note on HEAD**: the session-start environment snapshot reported `c8b679eb3` as the tip. That
> snapshot was stale — the actual tip at audit time was `38a5e598f`, five commits later. I verified
> that none of the intervening commits (`98fa79aa7`, `45d0148cd`, `3d605ee37`, `a65888c40`,
> `38a5e598f`) touched `docs/methodology/preregistration/`, and re-confirmed at the true HEAD that
> all three registered documents remain byte-identical to commit `f037a9d`. All quotations in this
> audit were read from the clean working tree, i.e. from `38a5e598f`.
**Subject**: `docs/methodology/preregistration/protocol-errata.md` § E37 (line 894)

---

## 0. Bottom line

**Verdict (a), with high confidence.** The coarse-to-fine proposer–verifier (PV) architecture was
preregistered — by name, as hypothesis H2 Condition B, with a registered directional prediction, a
registered stopping rule, a registered gated-optimisation contingency, and *verbatim registered
proposer and verifier prompts and configuration files*. The repo copy of the registration has **not
drifted** from the version cited by the OSF posting. E37's central assertion is false as written and
should be corrected.

The production PV pipeline nevertheless **does** exceed the registered specification in several
specific, enumerable ways (§6). E37 was right that *something* was new; it was wrong about *what*.

---

## 1. Method and anchors

Every specific below was re-verified at its source within this audit. Anchors are given as
`path:line` for text and as full or abbreviated commit hashes for git facts.

Commands used for the git archaeology (all read-only):

- `git log --follow -- <path>`
- `git log --all -S"proposer-verifier"`, `-S"Coarse-to-fine"`, `-S"Liberal proposer"`
- `git rev-parse <commit>:<path>` (blob-hash identity comparison)
- `git show <commit>:<path>` (historical file content)

---

## 2. The full current registered text on two-stage / PV

Canonical document: `docs/methodology/preregistration/osf/preregistration.md` (2,417 lines,
version **v4.7**, dated **2026-01-31**; version confirmed at
`docs/methodology/preregistration/protocol-errata.md:5` — "**Associated preregistration**:
`preregistration.md` v4.7 (2026-01-31)" — and at
`docs/methodology/preregistration/osf/README.md:22`).

### 2.1 § 1 Study Overview

`preregistration.md:24` (§ 1.1 Background, list of preliminary findings):

> 2. **Two-stage proposer-verifier was actively harmful**: This architecture degraded performance rather than improving precision-recall tradeoffs.

`preregistration.md:33` (§ 1.2 Research Questions, RQ 3):

> 3. Do two-stage proposer-verifier pipelines improve precision-recall tradeoffs for VLM detection?

Note: PV is one of the study's **eight registered research questions**. This alone is fatal to E37's
"the preregistration did not include a two-stage Proposer-Verifier pipeline".

### 2.2 § 5 Confirmatory Hypotheses — H2 (the core registration)

Section 5 begins at `preregistration.md:398`. H2 occupies lines 451–493.

`:451` heading:

> ### H2: Two-Stage Pipelines Do Not Improve Detection

`:453`:

> **Status**: Confirmatory (architectural)

`:455–459` background:

> **Background**: Two-stage pipelines are recommended in general ML but lack VLM-specific evidence. Two directions are possible:
>
> 1. **Coarse-to-fine (proposer-verifier)**: Liberal first pass identifies candidates; strict second pass verifies. Preliminary testing found this degraded performance, likely due to context loss when cropping candidate regions.
>
> 2. **Fine-to-coarse (context expansion)**: Standard detection first; uncertain cases re-queried with larger tile for additional context.

`:461` the registered directional prediction:

> **Prediction**: Neither two-stage architecture will improve F1 over single-stage detection with voting.

`:463–469` the registered conditions table:

> **Test**: Compare at optimal single-stage configuration:
>
> | Condition | Architecture | Description |
> |-----------|--------------|-------------|
> | A (baseline) | Single-stage | Optimal config with consensus voting |
> | B | Coarse-to-fine | Liberal proposer → strict verifier |
> | C | Fine-to-coarse | Standard detection → context-expanded re-query for uncertain cases |

`:471–476` the registered Condition B implementation:

> **Coarse-to-fine implementation (Condition B)**:
>
> - Stage 1: Detection with lower confidence threshold
> - Stage 2: Crop candidate regions, verify with focused prompt
>
> *Implementation note: The proposer classifies detections into subtypes (burial mound, settlement mound, triangulation point on mound, benchmark on mound) based on visual characteristics. This classification is for diagnostic purposes and quality assessment; all subtypes are treated as positive detections for F1 calculation.*

`:486–489` the registered analysis:

> **Analysis**:
>
> - One-tailed tests: H0: two-stage ≥ single-stage; H1: two-stage < single-stage
> - Prediction is that H0 will not be rejected for either architecture

`:491` the registered stopping rule:

> **Stopping rule**: Two-stage architectures will only be pursued further if either demonstrates F1 at least 0.05 higher than single-stage. Given the inherent cost (~2× API calls) and complexity overhead, parity or marginal improvement would not justify adoption.

`:493`:

> **Advance to Stage 2 if**: Either two-stage approach shows F1 improvement of at least 0.05 over single-stage (would contradict preliminary findings).

**Internal tension worth noting (minor, and not load-bearing).** The headline prediction at `:461`
is *"neither will improve"*. The analysis text at `:488–489` sets the one-tailed alternative in the
*opposite* direction (H1: two-stage **<** single-stage) and predicts H0 will **not** be rejected —
i.e. predicts two-stage is not significantly *worse*. The two sentences are not perfectly
consistent with one another. For the present question this does not matter: under either reading, a
**+0.05 or greater improvement** contradicts the registered expectation and trips the stopping rule
at `:491` and `:493`. The paper should quote `:461` (the explicit "Prediction" line) as the
registered directional claim, and may note the `:488` phrasing as a drafting artefact.

### 2.3 § 7 Summary Table

`preregistration.md:1153`:

> | H2 (two-stage) | Neither architecture improves over single-stage | Compare F1 | Either direction shows ≥0.05 F1 improvement |

### 2.4 § 8 Implementation Details

`preregistration.md:1220` (§ 8.2 API Parameters — the API/implementation section named in the brief):

> **Large tile handling (Gemini)**: For tiles ≥1024px (used in H2 fine-to-coarse testing), the Gemini API uses `media_resolution=MEDIA_RESOLUTION_HIGH` (1,120 tokens) to prevent internal tiling of large images. […]

(This anchors H2 Condition C, not B, but confirms H2 was carried through into the API section.)

`preregistration.md:1990` (§ 8.7.1 hypothesis implementation-readiness table):

> | H2 | Two-stage pipelines | ✅ Ready | Separate pipelines (coarse-to-fine, fine-to-coarse) |

`preregistration.md:2015` (§ 8.7.2 Configuration File Mapping — the config inventory named in the brief):

> | H2 | `propose_*.json` + `verify_*.json` (coarse-to-fine); `detect_*.json` + `expand_*.json` (fine-to-coarse) | Corresponding `.md` files |

`preregistration.md:2028` (§ 8.7.3 Script Mapping):

> | H2 | `4_detect_mounds_batch.py` (2× sequential) | `7_analyze_consensus.py`, `8_analyze_proposer_consensus.py` |

### 2.5 § 9 Implementation Priority

`preregistration.md:2167`:

> - **H2** (two-stage) — preliminary evidence suggests degradation

### 2.6 § 18 Version History (internal changelog)

`preregistration.md:2402` (v4.0 entry, extract):

> - v4.0: Major simplification — Hypotheses renumbered H1-H15 (8 confirmatory, 7 exploratory); H1+H2 merged (M/E level with planned contrasts); **H3+H10 merged (two-stage pipelines, both directions)**; […]

`preregistration.md:2417` (v2.0 entry):

> - v2.0: Merged hypotheses document; added two-stage trial framework, FDR rationale, tile-level MCC, H5-H10, implementation priority, checklist

The v4.0 entry is the key to the numbering: coarse-to-fine PV was **old H3**, fine-to-coarse was
**old H10**, and they were merged into **current H2**. This is why searching the current document
for "H3 proposer-verifier" finds nothing — the content was renumbered, not removed.

### 2.7 Registered companion document — `preregistration-coverage.md`

This is one of the three documents comprising the registration
(`osf/README.md:7–11`). It is **decisive on the gated-optimisation question**.

`osf/preregistration-coverage.md:162` (§ 5, factor table):

> | Pipeline architecture | P | 2 (single-stage, two-stage) | H2 |

`osf/preregistration-coverage.md:187` (§ 6.2 "Gated by Stopping Rules"):

> | P × {anything} (pipeline × other factors) | Two-stage architecture must exceed single-stage by ≥0.05 F1 to justify ~2× cost overhead; exhaustive optimisation only if this threshold is met |

`osf/preregistration-coverage.md:227` (§ 8, "Not Supported (Explicitly Out of Scope)"):

> - "Two-stage architecture can be optimised to match single-stage" — only tested if competitive

**Interpretation.** The registration did not merely register PV as a condition. It registered a
**conditional authorisation to optimise it**: pipeline × everything interactions are excluded
*unless* the ≥ 0.05 F1 threshold is met, and are in scope if it is. The threshold was met (§ 5.2).
The subsequent optimisation campaign therefore executes a **registered contingency**, not an
unregistered improvisation. This is materially stronger ground than the brief assumed.

### 2.8 Registered companion document — `preregistration-appendix-prompts.md`

This is the single most under-appreciated piece of evidence. The registration includes the
**verbatim proposer and verifier prompts and their JSON configs**.

`osf/preregistration-appendix-prompts.md:30`:

> - **2 two-stage pipeline instruction files**: propose_brief.md, verify_brief.md

`:1088` § 1.6.2 registers the verifier system instruction in full. Extract:

> # Two-Stage Detection: Verifier
>
> Classify whether the candidate symbol at the centre of this crop is a burial mound.

…with a registered output schema:

> Return JSON:
>
> {
>     "reasoning": "Brief description of visual features observed.",
>     "mound_probability": 0.0
> }

…and a registered scoring guide (`0.9-1.0` … `0.0-0.2`).

`:1042` § 1.6.1 registers the proposer instruction `propose_brief.md` in full, including
"This is Stage 1 of a two-stage pipeline; a verifier will filter false positives."

`:1584` registers the H2 execution protocol:

> **H2 protocol**: Each of the K=10 runs is independent (one proposer pass → one verifier pass). The verifier returns raw `mound_probability` scores used directly for evaluation — no binary thresholding or voting within the verification step.

`:1586` and `:1622` register `propose_brief.json` and `verify_brief.json` in full, including
model (`gemini-3-flash`), `thinking_level` (`minimal`), temperature, and the nine-example library.

**Conclusion of § 2.** The registration specifies the PV architecture down to the prompt text and
the JSON config. E37's claim that "the preregistration did not include a two-stage
Proposer-Verifier pipeline" is not a defensible reading of any part of the registered corpus.

---

## 3. Version history of the claim

### 3.1 Was PV present from the first version?

**Yes — from the very first commit of the preregistration.**

The document has **28 revisions** (`git log --follow`, count verified). The earliest is
`98236dd74` ("docs: Add preregistration and update pipeline documentation", 2025-12-31 12:54:02
+1100), which created `docs/methodology/preregistration/preregistration.md`.

At `98236dd74` the content existed as **H3**:

> `:336` ### H3: Coarse-to-Fine Two-Stage Pipeline Degrades Performance
> `:338` **Background**: Two-stage pipelines are recommended in general ML but lack VLM-specific evidence. Preliminary testing found coarse-to-fine (proposer-verifier) degraded performance, likely due to context loss when cropping candidate regions.
> `:340` **Prediction**: Two-stage coarse-to-fine (proposer-verifier) detection will produce lower F1 than single-stage detection.
> `:345` * Condition B: Two-stage proposer-verifier pipeline (liberal proposer → strict verifier)

(Line numbers are within the file **as it existed at that commit**, retrieved via
`git show 98236dd74:docs/methodology/preregistration/preregistration.md`.)

### 3.2 Presence across every revision

I checked all 28 revisions for the strings `proposer-verifier` and `coarse-to-fine`
(case-insensitive). **Every single revision contains both.** Occurrence counts:

| Revision range | Date range | `proposer-verifier` | `coarse-to-fine` |
|---|---|---|---|
| `98236dd74` – `b91d76884` | 2025-12-31 – 2026-01-01 | 5 | 6 |
| `e6a6228e5` – `a8686fe95` | 2026-01-01 | 5 | 7 |
| `e50674927` – `58a5ce467` | 2026-01-03 – 2026-01-04 | 6 | 7 |
| `b497608e5` – `fbca6b454` | 2026-01-06 – 2026-01-07 | 7 | 5 |
| `af486fa56` – `bd65c007f` | 2026-01-08 – 2026-01-31 | 3 | 5 |

**There is no revision in which PV content is absent.** It was never added late and never removed.

### 3.3 Was any PV content removed or weakened?

**Consolidated, not weakened.** The drop from 7 → 3 occurrences of "proposer-verifier" between
`fbca6b454` (2026-01-07, v3.7) and `af486fa56` (2026-01-08, v4.2) is the v4.0 restructure described
at `preregistration.md:2402`: two separate hypotheses (old H3 coarse-to-fine, old H10 fine-to-coarse)
were merged into a single H2 covering both directions. Fewer mentions, same substance, plus a
consolidated conditions table.

One clause **was** dropped in that restructure. At `fbca6b454` the document carried, at its line 477:

> **Scope limitation**: Exhaustive optimisation of proposer-verifier configurations (e.g., varying proposer/verifier thresholds, prompt variants for each stage) is beyond the scope of this study. Such investigation would be warranted only if initial testing shows the architecture exceeds single-stage performance by at least 0.05 F1.

That exact sentence does **not** appear in v4.7 (`grep -n -i "exhaustive optimisation"` on the
current file returns no match in the H2 section; the only "Scope limitation" in v4.7 is at `:691`
and concerns H6 per-model optimisation). However, its substance survives in two registered places:
the H2 stopping rule at `preregistration.md:491` and — near-verbatim — at
`osf/preregistration-coverage.md:187` ("exhaustive optimisation only if this threshold is met").
So the gated-optimisation contingency remained registered; only its location moved. This is a
*strengthening* of the PI's position, not a weakening: the registration retains an explicit,
threshold-gated licence to optimise the PV architecture.

Also note that "liberal proposer → strict verifier" was **not** newly introduced at v4.2 — it is
present at `fbca6b454` (v3.7) line 471 as "Condition B: Two-stage proposer-verifier pipeline
(liberal proposer → strict verifier)". (I initially suspected it was added at v4.2 because
`git log -S"Liberal proposer"` flagged that commit; direct inspection of both revisions shows the
count is 1 in each — the `-S` hit reflects surrounding line changes, not an insertion. Corrected.)

### 3.4 **Repo copy vs OSF-posted registration — the drift question**

This was flagged in the brief as potentially "the single most important thing you can find".
**There is no drift.**

Evidence chain:

1. **The OSF posting is dated and timestamped.** `docs/methodology/preregistration/execution-checklist.md:59–61`:

   > | OSF Registration URL | <https://osf.io/tybgq/overview> |
   > | OSF Project URL | <https://osf.io/h9x4g> |
   > | Registration timestamp | 2026-01-31 23:54 UTC |

   and `:44–47`:

   > - [x] Submit to OSF Registries (2026-01-31)
   >   - Uploaded `preregistration.md` and companion documents
   >   - No embargo set

2. **The OSF posting names a repository commit.** `osf/README.md:26–29`:

   > - **Repository**: https://github.com/saross/map-reader-llm
   > - **Commit**: `f037a9d`

   `f037a9d` = `f037a9d8d3a092de10972114eede4edea2f0f60d`, "docs(preregistration): Bump
   version/date to v4.7 / 2026-01-31 across osf/ files", committed **2026-01-31 12:37:38 UTC**
   (= 23:37:38 +1100). This is **11 h 16 min before** the 23:54 UTC registration timestamp —
   correct ordering: the commit precedes the posting.

3. **The last edit to `preregistration.md` predates the posting.** The most recent commit touching
   it is `bd65c007f` ("docs(preregistration): Update date to 2026-01-31 for registration"),
   **2026-01-31 12:34:27 UTC**. `git log --all --since=2026-02-01 -- <path>` returns **nothing**:
   there has been **no commit to the preregistration document on any ref since 2026-01-31**.

4. **Blob-level identity.** All three registered documents are byte-identical between `f037a9d`
   and `HEAD`:

   | Document | blob at `f037a9d` | blob at `HEAD` | identical? |
   |---|---|---|---|
   | `osf/preregistration.md` | `fa221b30f395feb7ef0c9425c36eae0b94e917ba` | same | ✅ |
   | `osf/preregistration-coverage.md` | `da6f107f09ddc0817dc9311eb80e6972c1ef18ba` | same | ✅ |
   | `osf/preregistration-appendix-prompts.md` | `5bf2261fab0994f71f4fa9a7da7e133cebe66714` | same | ✅ |

   `git status --porcelain docs/methodology/preregistration/osf/` is empty (working tree clean).

5. **`f037a9d` did not touch the preregistration itself.** Its file list is
   `osf/analysis-summary.md`, `osf/execution-checklist.md`, `osf/preregistration-coverage.md`.
   Erratum **E1** (`protocol-errata.md:22–34`) independently corroborates this, describing `f037a9d`
   as a version-alignment commit and noting: "These are companion metadata files, not the
   preregistration document itself."

   (The `f037a9d → HEAD` diff over the whole `osf/` directory is non-empty, but only because
   `analysis-summary.md`, `execution-checklist.md` and `hypothesis-tracking.md` were later **moved
   up one directory level**, and `README.md`, `description.md`, `narrative-summary.md`,
   `phase1-errata-and-decisions.md` were added. None of the three *registered* documents changed.)

**Residual uncertainty (stated honestly).** The chain above proves the *repository* copy is
unchanged since before the posting. It does not, by itself, prove that the *file uploaded to OSF*
was identical to the repository file at upload time — that would require fetching
<https://osf.io/tybgq/> and diffing the posted artefact. **UNVERIFIED — would need a fetch of the
OSF registration itself (or the downloaded registration PDF/attachments) to close this last link.**
I recommend doing this once before submission, because it is cheap and it converts a
strong inference into a direct observation. Every indirect indicator points the same way: the
version string (v4.7 / 2026-01-31) matches, the cited commit matches, the timestamps order
correctly, and nothing has been committed since.

---

## 4. Reconciling E37

### 4.1 E37 as written

`protocol-errata.md:894`:

> ### E37: Proposer-Verifier (PV) pipeline introduced as post-hoc extension

`:896–902` metadata table:

> | Date | 2026-03-15 |
> | Type | Deviation |
> | Commit | `f9d40e0` (library), `5d72593` (orchestrator) |
> | Files | `scripts/lib_verifier.py`, `scripts/run_pv.py`, `scripts/evaluate_pv_results.py` |
> | Impact | New two-stage detection architecture; achieves F1=0.831, surpassing all preregistered approaches |

`:904` (the disputed sentence):

> **Description**: The preregistration did not include a two-stage Proposer-Verifier pipeline. The PV approach was developed after observing that single-stage detection produced many false positives that a second-stage verifier could filter. […]

`:908`:

> **Protocol impact**: The PV pipeline is an extension beyond the preregistered design, not a replacement. All preregistered analyses (H1–H9) are evaluated independently of PV. The PV results are reported as an additional finding demonstrating that two-stage architectures can substantially improve VLM detection accuracy.

### 4.2 What E37 gets wrong

| # | E37 claim | Status | Evidence |
|---|---|---|---|
| 1 | "The preregistration did not include a two-stage Proposer-Verifier pipeline" | **False** | `preregistration.md:451–493` (H2, Condition B); `:33` (RQ 3); `:1153`; `:2015`; registered prompts at `appendix-prompts.md:1042, 1088`; registered configs at `:1586, 1622` |
| 2 | Framing as a **Deviation** requiring justification | **Mis-typed** | Registered condition + registered stopping rule fired + registered gated-optimisation contingency (`coverage.md:187`). The architecture is registered; only the *elaborations* in § 6 are deviations |
| 3 | Title "introduced as post-hoc extension" | **Misleading** | The *pipeline* is registered. Some *implementation choices* are post-hoc |
| 4 | "All preregistered analyses (H1–H9) are evaluated independently of PV" | **Incoherent for H2** | H2 *is* the two-stage hypothesis. PV results **are** the H2 Condition B result |
| 5 | "achieves F1=0.831" | **Stale** | Headline is now **F1 0.890 / MCC 0.790** — `results/conditions-manifest.md:172` (`pv-diag-384::verified-adv-text-consensus-16of30`, F1 `0.8902`, MCC `0.7903`, n=412); `reports/key-findings-summary-2026-06-23.md:97` |
| 6 | `Date | 2026-03-15` | **Internally inconsistent** | Its own cited commits are **later**: `f9d40e0` = 2026-03-19, `5d72593` = 2026-03-20 (both verified to exist) |
| 7 | `Commit: f9d40e0 (library)` → `Files: scripts/lib_verifier.py` | **Mis-attributed** | `f9d40e0` (2026-03-19) added `scripts/lib_batch_verifier.py`. `scripts/lib_verifier.py` and `scripts/run_pv.py` first appear at `5d7259303` (2026-03-20) |

### 4.3 What E37 gets right

E37 is right that the **production PV pipeline is not identical to registered Condition B**, and
right that it needed documenting. Its error is one of *scope*, not of *instinct*: it declared the
whole architecture unregistered when only its elaborations were.

---

## 5. Did the registered stopping rule fire?

**Yes**, and the project's own tracking document says so — in direct contradiction of E37.

`docs/methodology/preregistration/hypothesis-tracking.md:61–64`:

> **Status (2026-03-11)**: Complete. The preregistered null prediction (two-stage
> will not improve) was **contradicted** with large effect size. Phase 3c pilot
> exceeded the GO criterion (ΔF1 ≥ 0.05) by a 2× margin, achieving +0.09 to
> +0.14 F1 improvement with proposer-verifier architecture.

`hypothesis-tracking.md:14` lists H2 as **Complete**, dated 2026-03-11 — i.e. **four days before
E37's own stated date of 2026-03-15**. The project knew H2 had been tested and refuted *before*
E37 declared PV unregistered.

Corroborating magnitude, `decisions-log.md:1072`:

> 1. The 60-tile pilot demonstrated +0.14 F1 improvement (0.605 → 0.796) from adding a verifier stage (Obs 150)

So: registered prediction at `preregistration.md:461` **refuted**; registered stopping rule at
`:491` (≥ 0.05 F1) **fired**; registered "Advance to Stage 2" criterion at `:493` **met**; registered
gated-optimisation exclusion at `coverage.md:187` **lifted by its own terms**.

---

## 6. What the production PV pipeline genuinely does exceed

Being fair to E37 requires precision here. The following are **real** departures from, or
elaborations beyond, the registered specification. They are the legitimate content of a corrected
erratum.

### 6.1 Departures from registered protocol (substantive — true deviations)

1. **Proposer is a consensus pool, not a single liberal pass.**
   Registered (`preregistration.md:473`): "Stage 1: Detection with lower confidence threshold" —
   and (`appendix-prompts.md:1584`) "Each of the K=10 runs is independent (one proposer pass → one
   verifier pass)". Production headline is a **16-of-30 consensus vote** feeding the verifier
   (`results/conditions-manifest.md:172`, condition id
   `pv-diag-384::verified-adv-text-consensus-16of30`). This fuses H2 with H3 (consensus voting),
   which the registration treats as separate hypotheses — and is precisely the `P × N` interaction
   that `coverage.md:187` excluded *unless* the ≥ 0.05 threshold was met. It was met, so this is a
   registered-contingent extension rather than an unauthorised one; but it is not what
   Condition B literally specified, and should be stated as such.

2. **Verifier applied as a binary accept/reject verdict, not raw `mound_probability`.**
   Registered (`appendix-prompts.md:1584`): "The verifier returns raw `mound_probability` scores
   used directly for evaluation — **no binary thresholding or voting within the verification
   step**." Production headline uses a binary verdict with `prob_threshold = null` — confirmed by
   erratum **E56** (`protocol-errata.md:1755`). This is a deviation *from* the registered protocol,
   though in the conservative direction (no tuning).

3. **Probability-threshold operating points in the diagnostics.** Registered protocol forbade
   thresholding; the pv-diag / verifier-calibration-matrix work sweeps `(vote_t, prob_t)`. E56
   already documents this and correctly flags the operating points as **in-sample**
   (`protocol-errata.md:1757`). Not a new problem — but it belongs in the corrected E37's
   cross-references.

### 6.2 Elaborations not specified either way (registration was silent)

4. **Adversarial verifier prompt framing.** The registered verifier
   (`appendix-prompts.md:1088`, `verify_brief.md`) opens "Classify whether the candidate symbol at
   the centre of this crop is a burial mound" and lists neutral diagnostic criteria. Production
   default is `prompts/system-instructions/verify_adversarial.md`, which opens:

   > A detection system has identified the symbol at the centre of this crop as a
   > possible burial mound. Your task is to **find reasons it is NOT a burial mound**.

   The word "adversarial" appears **nowhere** in any of the three registered documents (verified by
   grep across all three — zero matches). This is a genuine post-registration development. The
   checklist / brief / comparative verifier variants
   (`prompts/system-instructions/verify_checklist.md`, `verify_comparative.md`) are likewise
   unregistered — though **E39** (`protocol-errata.md:928–940`) establishes that strategy choice is
   not load-bearing (all three statistically indistinguishable at 340-tile scale), which materially
   limits the researcher-degrees-of-freedom concern.

5. **Crop-size optimisation (40–300 px; 150 px / padding 75 default).** The registration says only
   "Stage 2: Crop candidate regions" (`preregistration.md:474`) — no size specified. Optimisation
   documented at `decisions-log.md:1084–1088` (Decision 23) and E37 itself.

6. **Verifier consensus N=1 vs N=5.** Not specified in the registration; N=1 selected
   (`decisions-log.md:1109–1113`, Decision 24).

7. **Crop extraction source (tiles vs source rasters).** An implementation bug and its fix, already
   documented as **E33** (`protocol-errata.md:768`).

### 6.3 Implementation-only (no experimental consequence)

8. **Dual-mode Batch / real-time API execution** — **E38** (`protocol-errata.md:912–924`), which
   itself states "Both modes produce identical prompts and results".
9. **New script surface** (`scripts/lib_verifier.py`, `scripts/run_pv.py`,
   `scripts/evaluate_pv_results.py`) replacing the registered
   `4_detect_mounds_batch.py (2× sequential)` route at `preregistration.md:2028`.

**Summary of the gap.** Registered: the architecture, both directions, the conditions table, the
prediction, the analysis, the stopping rule, the gated-optimisation contingency, the proposer and
verifier prompts verbatim, and both JSON configs. Not registered: adversarial framing, crop
geometry, verifier-consensus size, the consensus-pool proposer, and the binary-verdict /
probability-threshold handling. The gap is real but **narrow and enumerable** — it is the
optimisation layer, not the architecture.

---

## 7. Other errata bearing on this

| E-# | Line | Title | Relation to E37 |
|---|---|---|---|
| **E33** | `:768` | Verifier crop extraction reads from tiles instead of source rasters | **Neutral / implicitly contradicts.** Dated **2026-03-12** — *three days before* E37 — and already treats PV as an established experimental line ("All Phase 3d **proposer-verifier** results", `:781`). Documents a real bug, remediated with results archived to `archive/phase3d-pre-e33/` (`:791`) |
| **E37** | `:894` | PV pipeline introduced as post-hoc extension | **The error under audit** |
| **E38** | `:912` | Dual-mode API architecture (batch and real-time) | **Compounds mildly.** Inherits E37's post-hoc framing but is correctly typed *Clarification* with "Protocol impact: None" |
| **E39** | `:928` | Verifier strategy equivalence confirmed at production scale | **Mitigates.** Establishes that verifier-strategy choice is not load-bearing (adversarial 0.770 / checklist 0.769 / brief 0.752, CIs overlap, Obs 169) — so the one genuinely unregistered *prompt* choice cannot have driven the result |
| **E55** | `:1711` | Verifier-t-pilot T0.5/T1.0 metadata under-recorded the swept temperature | **Unrelated to registration status** (metadata provenance bug) |
| **E56** | `:1746` | Verifier probability-threshold operating points are in-sample | **Directly contradicts E37.** At `:1766` it instructs: "Report the headline proposer-verifier result at the **binary verdict** (`prob_t = null`), per gs-v2 **and the preregistered design**." E56 (2026-06-02) treats the PV headline as governed *by* the preregistered design — irreconcilable with E37's "the preregistration did not include a two-stage Proposer-Verifier pipeline" |

E56 is the strongest internal witness against E37: a later erratum, written by the project itself,
appeals to "the preregistered design" to justify how the PV headline is reported.

---

## 8. Cross-document consistency

### 8.1 Documents consistent with the registration (PV = registered)

| Document | Line | Quote | Verdict |
|---|---|---|---|
| `osf/description.md` | 26–27 | "These address: text versus image modality and elaboration level (H1); **two-stage pipeline architectures (H2)**;" — under the heading "**Preregistered hypotheses:**" | ✅ Consistent |
| `osf/description.md` | 34 | "strategies — text minimisation, **two-stage proposer–verifier pipelines** — had little effect or actively degraded performance" | ✅ Consistent |
| `osf/narrative-summary.md` | 5 | "Eight confirmatory hypotheses (H1–H8) testing modality and text elaboration, **two-stage pipeline architectures**, consensus voting, …" | ✅ Consistent |
| `osf/preregistration-coverage.md` | 162, 187, 227 | see § 2.7 | ✅ Consistent — and the strongest support for the optimisation campaign |
| `analysis-summary.md` | 78–82 | "### H2: Two-Stage Pipeline / - **Design**: 3 conditions (single-stage baseline, coarse-to-fine, fine-to-coarse)" | ✅ Consistent |
| `execution-plan.md` | 557–600 | "### Phase 3d: H2 Two-Stage Pipeline"; ":590 - Condition B: Proposer → Verifier pipeline"; ":600 **Stopping rule**: Two-stage must exceed single-stage by ≥0.05 F1 to justify ~2× cost overhead (see preregistration H2)." | ✅ Consistent — PV had a **named execution phase** in the plan |
| `hypothesis-tracking.md` | 14, 57–86 | H2 **Complete** 2026-03-11; "The preregistered null prediction (two-stage will not improve) was **contradicted**" | ✅ Consistent — and directly refutes E37 |
| `decisions-log.md` | 101 | "**Implementation**: H2 remains in preregistration to formally test the null hypothesis (two-stage ≤ single-stage)." | ✅ Consistent — Decision 3 (December 2025) explicitly *retains* H2 in the registration |

### 8.2 Documents inconsistent with the registration

| Document | Line | Quote | Problem |
|---|---|---|---|
| `protocol-errata.md` | 904 | "The preregistration did not include a two-stage Proposer-Verifier pipeline." | ❌ **False** — the error under audit |
| `decisions-log.md` | 1062 | "**Decision**: Introduce a two-stage Proposer-Verifier (PV) pipeline as a **post-hoc extension to the preregistered single-stage detection approach**." (Decision 22, dated 2026-03-19) | ❌ **Propagates E37's error**, and mischaracterises the registration as "single-stage" when H2 registers both. `:1078` cross-references "See E37 in protocol errata" — a citation loop between the two erroneous documents. **Needs the same correction as E37** |

`osf/phase1-errata-and-decisions.md` contains **no** PV/verifier/two-stage/proposer mentions
(grep returned zero hits) — so it neither helps nor hurts.

### 8.3 Internal inconsistency inside `decisions-log.md`

Decision 3 (`:70–101`, December 2025) and Decision 22 (`:1058–1080`, 2026-03-19) contradict each
other on whether PV was registered. Decision 3 says H2 *remains in the preregistration*; Decision 22
calls PV a post-hoc extension to a "preregistered single-stage detection approach". Decision 22 is
the later and the wrong one. A corrective note on Decision 22 pointing to Decision 3 and to the
corrected E37 would resolve it.

### 8.4 Wider-repository sweep — E37's error has propagated

A separate read-only sweep of the repository *outside* `docs/methodology/preregistration/` found the
project is **split** on this question, and the split is traceable to E37. I re-verified every claim
below at source.

**Documents that say PV was preregistered (agreeing with this audit):**

- `reports/d17-inventory/d17-inventory-h1-h4.md:567–577` — an **independent prior rebuttal of E37**,
  reached without this audit's git evidence:

  > I think that framing is **too modest and partly wrong**: `preregistration.md:468` registers
  > Condition B as *"Coarse-to-fine | Liberal proposer → strict verifier"*, and `:471–474` registers
  > the implementation as *"Stage 1: Detection with lower confidence threshold; Stage 2: Crop
  > candidate regions, verify with focused prompt"* — which is precisely the PV pipeline. What was
  > post hoc is the adversarial prompt framing, the probability-score output, and the tuning
  > programme; not the architecture or the hypothesis.

  This is **convergent with § 6 of this audit**, arrived at independently. It also proposes the same
  split (architectural contrast registered; verifier optimisation exploratory).
- `docs/paper/results-outline.md:461–462` — lists H2 (Condition B only) among "Executed and
  registered"; `:471–472` flags Condition C as "dropped without an erratum"; `:474–479` traces the
  spurious "exploratory" label to `analysis-summary.md:82`.
- `prompts/configs/propose_brief-text.json:3` — describes `propose_brief.md` as the
  "(preregistered proposer prompt)". A config file in the production tree calls the proposer prompt
  preregistered.

**Documents that repeat E37's error:**

- `reports/d17-inventory/d17-errata-census.md:138` —

  > **Yes — this is the single largest scope deviation.** The study's headline architecture is not preregistered.

- `reports/d17-inventory/d17-inventory-h9-h12.md:508`, `:537–539`
- `docs/notes/working-notes.md:16721` — "The proposer-verifier pipeline was introduced via erratum
  E37 after registration closed"; asserted as "firm", and reached by an "unprimed
  preregistration-check agent" (`:16699`) that evidently never opened §5 H2.
- `planning/paper-writeup-continuity.md:959`; `docs/notes/reflections/session-log.md:6229`
- `results/analyses-manifest.json` — **all 18** analysis rows carry `"preregistered": "exploratory"`
  (verified: `grep -o '"preregistered": "[a-z-]*"' | sort | uniq -c` → `18 exploratory`). This is a
  **blanket** label, not a PV-specific judgement, but it means no analysis in the machine-readable
  manifest is currently tagged as bearing on a registered hypothesis.

**The most serious propagation — `reports/experimental-progression.md`.** At `:150–155` it places PV
under the heading "### Pipeline development (post-registration)" (`:140`). At `:264–266` it goes
**further than E37 itself**:

> The result — that none of those variables matter — redirected the investigation toward architectural innovations (consensus, PV) that the preregistration **could not have anticipated because they did not yet exist in the VLM feature detection literature**.

This is falsified twice over: the registration *did* anticipate PV (`preregistration.md:451–493`),
and `:455` explicitly grounds it in prior literature — "Two-stage pipelines are **recommended in
general ML** but lack VLM-specific evidence". If this sentence reaches a reviewer, it will read as
the authors not having read their own preregistration. **Highest-priority correction after E37
itself.**

**The sharpest single self-contradiction — `docs/methods-outline.md:122–123`**, one bullet:

> - Tested as exploratory hypothesis; preregistered as expected null
>   (single-stage ≥ two-stage)

Says both things at once. Must be resolved before the Methods section is drafted.

**A disclosure gap — `docs/paper/results-draft.md`.** § R4 ("## R4. The proposer–verifier
architecture is the best architecture on every tile size", `:133`) is the actual manuscript prose for
the PV headline. The string `E37` does not appear anywhere in that file, and § R4 makes **no
registration-status statement in either direction**. So the current draft neither commits the error
nor makes the (correct, and favourable) preregistration claim. This is the cheapest place to get it
right first time.

---

## 9. Verdict, with confidence

**(a) is true.** Specifically:

- PV **was preregistered** as H2 Condition B — as concept, as condition, as research question, and
  down to the verbatim verifier prompt and JSON config. **Confidence: very high.** Basis: nine
  independent anchors in the canonical document (`:24, :33, :451–493, :1153, :1220, :1990, :2015,
  :2028, :2167`), plus both registered companion documents.
- The registered directional prediction (`:461`, "Neither two-stage architecture will improve F1
  over single-stage detection with voting") **was refuted**. **Confidence: very high.** Basis:
  `hypothesis-tracking.md:61–64` and `decisions-log.md:1072`.
- The registered stopping rule (`:491`, ≥ 0.05 F1) **fired**, by roughly a 2× margin.
  **Confidence: very high.** Same basis.
- The registered gated-optimisation contingency (`coverage.md:187`) **was thereby activated**,
  which authorises the optimisation campaign that followed. **Confidence: high.** Basis:
  `coverage.md:187` + `:227` read against the fired stopping rule. This is an inference from the
  registered text, but a tight one.
- The production pipeline is **an elaboration beyond the registered specification** in the five
  enumerable respects at § 6.1–6.2. **Confidence: high.**
- **E37 is wrong and should be corrected.** **Confidence: very high.**

**(b) is false.** The repo copy has **not** drifted from the OSF-posted registration.
**Confidence: high** (not "very high" only because the OSF-side artefact was not fetched — see the
residual-uncertainty note at § 3.4). Basis: identical blob hashes at `f037a9d` and `HEAD` for all
three registered documents; no commit to the preregistration on any ref since 2026-01-31; commit
timestamps ordered correctly before the 23:54 UTC posting.

**Single most decisive piece of evidence**: the registered prompt appendix. The verifier's system
instruction and its JSON config — including the `mound_probability` output schema — are printed
verbatim in `osf/preregistration-appendix-prompts.md:1088` and `:1622`, in a document that is
byte-identical (blob `5bf2261fab0994f71f4fa9a7da7e133cebe66714`) to the version cited by the OSF
posting. A study that prints its verifier's prompt in the registration cannot be said not to have
registered a verifier.

---

## 10. Proposed corrected wording for E37

Retaining the E-number (errata should be corrected in place with a revision trail, per the project's
Document Revision Policy), and re-typing from *Deviation* to *Correction to a prior erratum*:

> ### E37: Proposer–Verifier (PV) pipeline — production elaboration of preregistered H2 Condition B
>
> | Field | Value |
> |-------|-------|
> | Date | 2026-03-19 (original) · corrected 2026-07-27 |
> | Type | Correction (supersedes the original "Deviation" classification) |
> | Commit | `f9d40e0` (batch verifier library, 2026-03-19), `5d72593` (dual-mode orchestrator + `lib_verifier.py`/`run_pv.py`, 2026-03-20) |
> | Files | `scripts/lib_batch_verifier.py`, `scripts/lib_verifier.py`, `scripts/run_pv.py`, `scripts/evaluate_pv_results.py` |
> | Impact | Production two-stage architecture; headline F1 0.890 / MCC 0.790 at 20 m on the gold-standard corpus |
>
> **Correction notice (2026-07-27)**: The original text of this erratum stated that "the
> preregistration did not include a two-stage Proposer-Verifier pipeline". **That statement was
> incorrect and is withdrawn.** The coarse-to-fine proposer–verifier architecture was preregistered
> as **H2 Condition B** (`osf/preregistration.md:451–493`), was one of the study's eight registered
> research questions (`:33`), and was specified down to the verifier's system instruction and JSON
> configuration in the registered prompt appendix
> (`osf/preregistration-appendix-prompts.md:1088`, `:1622`). It was present in every one of the 28
> revisions of the preregistration, beginning with the first (`98236dd74`, 2025-12-31, then numbered
> H3), and the registered documents are byte-identical to the version cited by the OSF posting
> (`f037a9d`; registration timestamped 2026-01-31 23:54 UTC).
>
> **What actually happened**: The registered prediction — "Neither two-stage architecture will
> improve F1 over single-stage detection with voting" (`osf/preregistration.md:461`) — was
> **refuted**. The registered stopping rule — "Two-stage architectures will only be pursued further
> if either demonstrates F1 at least 0.05 higher than single-stage" (`:491`) — **fired**, by
> approximately a 2× margin (+0.09 to +0.14 F1; `hypothesis-tracking.md:61–64`, Obs 150). This in
> turn activated the registered gated-optimisation contingency at
> `osf/preregistration-coverage.md:187`, which excludes pipeline × other-factor interactions
> "…exhaustive optimisation only if this threshold is met". The subsequent PV optimisation campaign
> therefore executes a **registered contingency**.
>
> **What genuinely exceeds the registration**: the production pipeline elaborates registered
> Condition B in five respects, none of which were specified in the registration —
> (1) the proposer is a **16-of-30 consensus pool** rather than the registered single "detection
> with lower confidence threshold" pass, fusing H2 with H3 (the `P × N` interaction that
> `coverage.md:187` gates on the stopping rule);
> (2) the verifier is applied as a **binary accept/reject verdict** rather than returning "raw
> `mound_probability` scores used directly for evaluation" as specified at
> `osf/preregistration-appendix-prompts.md:1584` — a deviation in the conservative direction, since
> nothing is tuned (see **E56**);
> (3) the default verifier uses an **adversarial prompt framing**
> (`prompts/system-instructions/verify_adversarial.md`) rather than the registered neutral
> `verify_brief.md` — the word "adversarial" appears nowhere in the registered documents, though
> **E39** establishes that strategy choice is not load-bearing;
> (4) **crop geometry** (sweep 40–300 px; default 150 px, padding 75) was optimised, the
> registration having specified only "Crop candidate regions" (`osf/preregistration.md:474`) — see
> Decision 23;
> (5) **verifier consensus size** (N=1 vs N=5; N=1 selected) was not specified — see Decision 24.
> Dual-mode Batch/real-time execution (**E38**) and the crop-source fix (**E33**) are
> implementation matters without experimental consequence.
>
> **Protocol impact**: The PV architecture is **preregistered**, and the PV result **is** the H2
> Condition B result — it should be reported as a preregistered confirmatory test whose directional
> prediction was refuted, not as an unregistered post-hoc finding. The optimisation layer built on
> top of it is a registered-contingent elaboration and should be reported as exploratory, with the
> five items above declared. Note also that H2 Condition C (fine-to-coarse context expansion) was
> **not tested** (`hypothesis-tracking.md:86`) and must be declared as a registered-but-unexecuted
> condition.
>
> **Consequential amendments**: `decisions-log.md` Decision 22 (`:1062`) carries the same error
> ("post-hoc extension to the preregistered single-stage detection approach") and requires the same
> correction; it also conflicts with Decision 3 (`:101`, "H2 remains in preregistration to formally
> test the null hypothesis"). The original E37's stated date (2026-03-15) preceded its own cited
> commits (2026-03-19/20) and its "F1=0.831" figure is superseded by the 0.890 headline
> (`results/conditions-manifest.md:172`).

---

## 11. Recommended follow-up actions (for the PI — none taken by this audit)

**Tier 1 — correctness of the record**

1. **Correct E37 in place** with the wording at § 10 plus a changelog entry, per the project's
   Document Revision Policy.
2. **Correct `reports/experimental-progression.md`** — `:140` (heading), `:150–155`, `:254`, and
   above all `:264–266` ("could not have anticipated"). This is the most damaging single sentence in
   the repository and is falsified by `preregistration.md:455` on its own terms.
3. **Correct `decisions-log.md` Decision 22** (`:1062`) and cross-reference Decision 3 (`:101`).
4. **Resolve `docs/methods-outline.md:122–123`**, which asserts both positions in one bullet.

**Tier 2 — closing the evidential loop**

5. **Fetch and diff the OSF-posted registration** at <https://osf.io/tybgq/> against
   `osf/preregistration.md` (blob `fa221b30f395feb7ef0c9425c36eae0b94e917ba`) to close the one
   remaining unverified link (§ 3.4). Cheap, and converts a strong inference into an observation.

**Tier 3 — paper-facing**

6. **Write the disclosure into `docs/paper/results-draft.md` § R4** (`:133`), which currently makes
   no registration-status claim at all — the cheapest place to get it right first time.
7. **Declare H2 Condition C as registered-but-unexecuted** in the deviations section
   (`hypothesis-tracking.md:86`: "Fine-to-coarse (H2-C) was not tested";
   `docs/paper/results-outline.md:471–472` notes it was "dropped without an erratum" — so a *new*
   erratum is owed).
8. **Resolve the `:461` vs `:488` drafting tension** by quoting `:461` as the registered directional
   prediction, with a footnote.
9. **Re-tag `results/analyses-manifest.json`**, where all 18 rows are blanket-`exploratory`. Per
   `d17-inventory-h1-h4.md:579–585`, the registered H2 contrast lives in `era1-leaderboard` (and
   `tile-size-sweep`), which need `"H2"` in `hypothesis_refs` before any row can be re-tagged.
10. Consider citing `hypothesis-tracking.md:61–64` — which had it right on 2026-03-11 — in the paper
    as the contemporaneous record that the stopping rule fired.

---

## 12. Items explicitly NOT verified

- **The content of the OSF-posted artefact itself.** UNVERIFIED — would need a fetch of
  <https://osf.io/tybgq/> or the downloaded registration package.
- **Whether a DOI was assigned.** `execution-checklist.md:62` leaves the DOI field blank.
- **Obs numbers cited inside errata** (Obs 150, 161, 163, 166, 167, 169, 170, 179, 269, 277, 347,
  351, 352, 359, 362). Quoted as they appear in the source documents; the working-notes register was
  not independently opened in this audit.
- **The F1 figures inside E39 and Decision 3** (0.770/0.769/0.752; 0.86/0.80/0.75). Quoted verbatim
  from the errata and decisions log; not re-derived from results artefacts.
- **`archive/` superseded preregistration copies.** `archive/preregistration/document-revisions/`
  contains ~25 editing-instruction and review files. These are *instructions to edit* the
  preregistration, not superseded registration snapshots; the authoritative version history is the
  git history of `preregistration.md` itself, which was traced exhaustively (all 28 revisions).
