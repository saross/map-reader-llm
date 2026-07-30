# Errata drafts — GATE 1 queue (drafted 2026-07-29)

**Status**: DRAFTS for orchestrator and Principal Investigator (PI) review. Nothing
in this file has been written to `docs/methodology/preregistration/protocol-errata.md`
or any other repository file. The last existing entry in the live errata document is
**E61**; these drafts claim **E62–E67** plus three append-style correction blocks
attached to existing entries E36, E16, and E20.

**Drafting authority**: `planning/audit-charter.md` § 10 item 7 (GATE 1 rulings, PI,
2026-07-29), in particular (b) the registration-contradiction errata policy and (e)
the erratum-queue amendments. Factual source: `reports/verification/apparatus/
defence-pass-adjudication-2026-07-29.md` per-finding rulings, and
`reports/verification/phase1-gate-package.md` §§ 2–3.

**Verification note**: every line reference, quoted span, count, and identifier below
was re-read at source during drafting on 2026-07-29. Where a source-level fact
diverged from the brief or from the gate package, the divergence is flagged in a
`> **Drafting note**` block rather than silently reconciled.

---

## Draft 1 — queue item 1: the three unlicensed study families + verifier-parameter levels

> **Drafting note (arithmetic)**: the brief and the gate package (§ 1 item 4, § 3
> item 1) both say "**four** verifier-parameter levels", then enumerate five —
> model `gemini-3.5-flash`, temperatures 0.3 and 0.7, thinking `medium` and `high`.
> `reports/verification/c2-census/licence-census.json` confirms **five** UNLICENSED
> `verifier_*` pairs (13 UNLICENSED total = 3 families + 5 verifier-parameter
> levels + 5 derivative `proposer_pool` slugs). The draft below covers five.
> **PI/orchestrator to confirm the count before this lands.**
>
> **Drafting note (scope surprise)**: `verifier_thinking_level=medium` has 13 observed
> sites and **none of them is in the three families** — all 13 are in `pv-diag-384`,
> which the census verdicts `registration+erratum` (ten errata attached, E37/E39/E40/
> E41/E42/E43/E53/E56/E57/E58). So the medium level is an unlicensed *parameter* inside
> an otherwise-licensed *family*. E62 as drafted says so explicitly; if the PI prefers
> the families erratum to stay strictly about the three families, the `medium` limb
> should be split into its own entry.
>
> **Drafting note (`purpose` field)**: the brief asks that each family's purpose be
> cited from `results/runs-manifest.json`. Two of the three carry a populated
> `purpose`; **`pv-diag-256`'s `purpose` is `null`**. The draft cites the manifest
> purpose verbatim where it exists and falls back to
> `results/run-conditions.json`'s `_note` for `pv-diag-256`, labelled as such.

### E62: Three unregistered proposer-verifier extension studies (`flash35-pv-2x2`, `pv-diag-256`, `verifier-robustness`) and five unregistered verifier-parameter levels — additional exploratory extensions of the registered PV contingency

| Field | Value |
|-------|-------|
| Date | 2026-07-29 (disclosure; executions 2026-04 to 2026-06) |
| Type | Deviation (unregistered exploratory extensions; no registered study altered) |
| Commit | — |
| Files | `results/runs-manifest.json`; `results/run-conditions.json`; `reports/verification/c2-census/licence-census.json`; `outputs/flash35-pv-2x2/`, `outputs/h11/pv-diag-256/`, `outputs/verifier-robustness/` |
| Impact | Low. No registered hypothesis test is conditioned on these runs; no reported registered result changes. The disclosure closes the last thirteen unlicensed factor=level pairs in the execution→errata inverse census |

**Framing (PI, 2026-07-29)**: E37 establishes that the proposer-verifier (PV)
architecture is *registered* — H2 Condition B — and that the production PV programme
is "that registered contingency, exercised"
(`docs/methodology/preregistration/protocol-errata.md:931-932`), the contingency
being the coverage document's "exhaustive optimisation only if this threshold is met"
(`osf/preregistration-coverage.md:187`) fired by the registered stopping rule at
`osf/preregistration.md:491`. The three families recorded here are **additional,
unregistered, serendipitous extensions of that same programme** — exploratory
additions built on top of a registered architecture. They are **not** deviations from
any registered study: none replaces, alters, or re-specifies a registered condition,
and no registered analysis draws on them. This erratum discloses them for
completeness, not because a registered commitment was departed from.

**How they surfaced**: the Phase 1 verification campaign's execution→errata inverse
census triaged all 213 observed factor=level pairs against the 702-obligation
commitment ledger and all 61 existing errata. 200 pairs were licensed (43 by the
registration, 14 by an erratum, 143 by both); 13 were UNLICENSED
(`reports/verification/c2-census/licence-census.json`, `summary`). Those 13 reduce to
three study families, five verifier-parameter levels, and five derivative
`proposer_pool` slugs that are licensed at run level and carry no independent content.

**The three families**:

| Family | Purpose (source) | Architectures executed | Scope |
|--------|------------------|------------------------|-------|
| `flash35-pv-2x2` | `runs-manifest.json`: "Model-role 2x2x2: is Flash 3.5 a better bare proposer, PV proposer, or verifier than Flash 3 at the minimal operating point? (The S110 parking note: bare proposer was the only angle a stronger model might win.)" | 1 × `consensus`, 3 × `proposer-verifier` (4 citable conditions) | era-2-487 (487 tiles, 384 px, 4-map gold standard, curator ground truth) |
| `pv-diag-256` | `runs-manifest.json` `purpose` is **`null`**. `run-conditions.json` `_note`: "256px H11 tile-size diagnostic (px256-1032 scope, 1032 tiles, curator GT) … 256px is the small-tile anchor for the tile-size comparison: F1@20m orders 256 < 512 < 384 (0.46 / 0.69 / 0.79)." | 1 × `single-pass`, 1 × `consensus`, 1 × `proposer-verifier` (3 citable conditions) | px256-1032 (1 032 tiles, 256 px, 4-map gold standard, curator ground truth) |
| `verifier-robustness` | `runs-manifest.json`: "Verifier-robustness programme: determinism (n=1 vindicated), proposer-input band, temperature/thinking matrix, model roles, compute allocation, operational maximum, pass-budget Pareto. Meta-rule: on a within-noise tie, take the cheaper config." | 8 × `proposer-verifier` (8 citable conditions) | era-2-487, with one condition scope-overridden to px256-1032 |

Architectures are as recorded in `results/run-conditions.json`, `decomposition.<family>.
conditions[].architecture`. Every condition in all three families is either a PV
condition or a proposer-side baseline built to be compared against one — which is the
factual basis for the "extension of the PV programme" framing rather than "new
unregistered studies".

**Why each is an extension rather than a registered study**:

1. **`flash35-pv-2x2`** asks a model-role question the registration does not pose. The
   lodged model set is closed at four values — "| Model | gemini-3-flash, gemini-3-pro,
   claude-4.5-sonnet, gpt-5.2-thinking | H6, H14 | Overrides config file value |"
   (CMT-0591) and "**Primary**: Gemini 3 Flash, Gemini 3 Pro" (CMT-0377) — and admits no
   3.5-generation model. E3's model-name resolution licence
   (`gemini-3-flash` → `gemini-3-flash-preview`) resolves a registered name to an API
   endpoint; it does not admit a later model generation. Executed 2026-06-10.
   The result is against the extension's own interest and is reported as such: Flash 3.5
   wins in no role (`runs-manifest.json` `headline_rationale`, verbatim: "Deliberately
   none — a model comparison, not a champion search: Flash 3.5 wins in NO role
   (bare-proposer numerical tie 0.6196 vs 0.6204; PV proposer -0.0355, p=0.035 targeted
   tile-swap — the one resolved role gap; verifier -0.012..-0.015, within-noise ties, at
   3x the price). The all-Flash-3 production stack stands").
2. **`pv-diag-256`** runs the registered H11 tile-size question at a third level.
   Registered H11 has exactly two conditions — "| A | 512×512 | 1× (baseline) | 1× |
   Lower |" (CMT-0310) and "| B | 384×384 | 0.56× | ~1.8× | Higher |" (CMT-0311). The
   registration discusses 256 px only as *prior pilot context*, not as a condition:
   "Pilot testing at 256px confirmed high recall (0.90) but very low precision (0.10) at
   2/5 consensus voting threshold, suggesting smaller tiles may over-detect"
   (`osf/preregistration.md:963`). The 256 px diagnostic re-runs that pilot question on
   the production corpus and anchors the low end of the tile-size curve. Its proposer
   passes were **not** materialised as `run_*` directories (only consensus outputs and
   crops survive), so no per-pass metadata exists; the six consensus GeoJSONs were first
   committed 2026-04-15 (`3d22184d6`), and the PV verification condition was executed
   2026-06-08 (`outputs/era1-pv-stage-d/256-consensus-text-5of5/`).
3. **`verifier-robustness`** sweeps verifier parameters the registration fixes at a
   single value. The lodged two-stage configs are templates pinned to one downstream
   optimum — "**Template status**: These configs are templates that will be finalised
   after earlier phases complete. Temperature will use the H7-optimal value from Phase
   2b. Library composition will use the H8-optimal from Phase 2c." (CMT-0583) — and the
   lodged verifier config fixes thinking at minimal: "| `thinking_level` | `minimal` |
   Calibrated via pilot; minimal achieves equivalent F1 to high at 1/3 latency (see
   §8.9) |" (CMT-0605). Executed 2026-06-09/10. Again the headline is deliberately
   negative (`runs-manifest.json`, verbatim): "Deliberately none — NO new champion. The
   carry-forward headline pv-diag-384::verified-adv-text-consensus-16of30 (0.890) stands:
   the operational maximum here (verified-384-16of30-t0-3-n5-opmax, 0.8951) is NOT
   significant over it (paired tile-swap permutation p=0.363, …), so per the cost
   meta-rule (Obs 357) it is a numerical high only."

**The five verifier-parameter levels**:

| Level | Observed sites | Carrying family/families | Nearest licence, and why it does not reach |
|-------|----------------|--------------------------|--------------------------------------------|
| `verifier_model=gemini-3.5-flash` | 2 | `flash35-pv-2x2` | E3 resolves a registered model *name* to its API endpoint; it does not admit a new model generation |
| `verifier_temperature=0.3` | 4 | `verifier-robustness` | CMT-0590 registers 0.3 as a runtime temperature level, but hooked to **H7 detection** temperature; no commitment extends the H7 sweep to the verifier stage |
| `verifier_temperature=0.7` | 2 | `verifier-robustness` | as above; E55 licenses a verifier-temperature sweep only at 0.5/1.0, in `verifier-t-pilot` |
| `verifier_thinking_level=high` | 3 | `verifier-robustness` (2), `pv-diag-384` (1) | E40 licenses HIGH only for `gemini-3.1-pro-preview` consensus runs; these sites run `gemini-3-flash-preview` |
| `verifier_thinking_level=medium` | 13 | **`pv-diag-384` only** | as above — E40's MEDIUM licence is for single-pass **Pro** experiments |

The five derivative `proposer_pool` slugs (`f3-min-text-1of10`,
`flash35-min-text-1of10`, `text`, `text-1of5`, `text-consensus-5of5`) are per-study
pool identifiers with no independent experimental content; they are licensed at run
level and are disclosed here only so the census's thirteen are fully accounted for.

**Post-facto acknowledgement**: this disclosure is written with results in hand, in
July 2026, for runs executed between April and June 2026. It was produced by a
systematic census rather than at execution time, and the fact that these families were
not erratum'd contemporaneously is itself part of what the census found.

**Protocol impact**: none on registered results. All three families are exploratory
extensions of the registered H2 Condition-B architecture; none is cited as evidence for
a registered hypothesis; two of the three report deliberately null headlines, and the
third (`pv-diag-256`) contributes only the low anchor of a tile-size curve whose two
registered levels (512 px, 384 px) are unaffected. Reporting requirement: the paper's
deviations table gains one row, and any use of these families in the text must be
labelled unregistered exploratory. Cross-references: E37 (PV as registered contingency
exercised), E39 (verifier strategy not load-bearing), E40 (Pro thinking levels), E41
(384 px / 487-tile evaluation scope), E55 (verifier-temperature pilot), E56 (in-sample
verifier operating points), E58 (registered proposer prompt never used).

---

## Draft 2 — queue item 2: HIGH thinking on `retest-phase3c` (H9)

### E63: `retest-phase3c` (H9 diversity) executed at HIGH thinking level — unregistered departure from the §8.9 `minimal` decision, configuration-verified but not token-corroborated

| Field | Value |
|-------|-------|
| Date | 2026-07-29 (disclosure; execution 2026-03-18 to 2026-03-25) |
| Type | Deviation (unregistered thinking level on an exploratory hypothesis) |
| Commit | — |
| Files | `studies/phase3c-h9-diversity-track1.yaml`, `studies/phase3c-h9-diversity-track2.yaml`; `prompts/configs/phase3c-t{1,2}-*.json` (22 configs); `outputs/retest/phase3c/**/*.meta.json` (225 files) |
| Impact | Medium-low on level, potentially higher on direction. The setting is constant across every compared H9 condition, so within-H9 contrasts are not confounded by it; but Obs 140 identifies HIGH thinking as itself a diversity mechanism, and H9 is a test *of* diversity mechanisms, so the setting may bias the H9 null's direction and not merely its level |

**The registered commitment**: §8.9 calibrates thinking level on a 20-tile, K=10 pilot
and concludes, verbatim, "**Decision:** Use `thinking_level=minimal` for main
experiment." (`osf/preregistration.md:2135`), with the appendix runtime table fixing
"| `thinking_level` | `minimal` | Calibrated via pilot; minimal achieves equivalent F1
to high at 1/3 latency (see §8.9) |" (CMT-0605). No erratum names `phase3c`.

**What was executed**: all 22 `phase3c` prompt configs and both study YAMLs set HIGH
thinking. Both YAMLs state, verbatim and identically, "All conditions use HIGH thinking
level. Temperature is fixed at T=0.7" (`studies/phase3c-h9-diversity-track1.yaml:40`;
`studies/phase3c-h9-diversity-track2.yaml:37`), and both carry
`optimal_thinking: "high"` in their `carried_forward` block (`:50` and `:47`
respectively). Configs and YAMLs were committed together on **2026-03-07**
(`ec00c2ae0`, "feat(phase3c): scaffold H9 diversity testing for both tracks"); the first
`phase3c` API execution timestamp is **2026-03-18** — the declaration therefore
pre-dates execution by 11 days and cannot be a post-hoc reconstruction. Execution ran
2026-03-18 to 2026-03-25 across 225 passes.

**Verification caveat (recorded at the PI's explicit mis-recording warning)**: all 225
`phase3c` meta files record `configuration.thinking_level: "high"` — a mechanical count,
225/225, zero exceptions. **But the retest-era pipeline left `usage_stats` wholesale
unpopulated**, so token-level corroboration is unavailable. Every one of the 225 metas
carries `usage_stats` with `total_tokens: 0`, `total_thoughts_tokens: 0`, and every
other counter at zero; the sibling `retest/phase3a` (180 metas, all `minimal`) and
`retest/phase3a-high` (90 metas, all `high`) directories are identically empty. The
distinction that matters: elsewhere in the project, **known-HIGH runs show millions of
thoughts tokens** (e.g. `outputs/55maps-text-high-generalisation/` passes record
45.7–46.4 M `total_thoughts_tokens`; `outputs/gs/` passes record 1.3–2.7 M) and
**known-minimal runs show zero thoughts tokens against a non-zero total** (e.g.
`outputs/gs/**/run.meta.json`: `total_thoughts_tokens: 0`, `total_tokens: 21633`).
`phase3c` shows **nothing** — not zero-thinking. The absence is an absence of accounting,
not evidence of minimal thinking. The wording of this erratum therefore rests on
configuration plus the pre-committed YAML declarations, and says so.

**What can be established structurally** (defence search, charter rule 13). Three
independent facts narrow the gap without closing it:

1. **No CLI override was in play.** `thinking_level` is set in the 22 config JSONs
   themselves (22/22 `"high"`), not passed as a runtime flag. E42's failure mode — meta
   recording the config default while a `--model`-style override changed the actual API
   call — structurally cannot arise where no override exists.
2. **The request builder and the metadata writer read the same key.**
   `scripts/lib_llm_metadata.py:531` writes `"thinking_level": self.config.get(
   "thinking_level")`, and the batch request builder at `scripts/lib_batch_api.py:509-513`
   constructs `generation_config["thinking_config"]` from the same
   `config.get("thinking_level")`. Within a single execution the two cannot diverge.
3. **The propagation bug was already fixed.** E34's fix — `"thinking_level":
   condition.get("thinking_level")` added to `generate_execution_units()` in
   `run_phase2.py` — landed 2026-03-15 (`5d7260335`), three days before `phase3c`
   execution began; and Decision 20 (2026-03-15) had just established the mitigation
   pattern `phase3c` uses, namely "separate config files … that differ only in the
   `thinking_level` field".

None of these is a runtime observation of thinking tokens. The honest statement is:
the configuration is verified, the declaration is pre-committed, the propagation path
is repaired and structurally coupled — and the response-side accounting that would close
the loop was not written to disk in this era.

**Aggravator, recorded against interest (Obs 140)**: HIGH thinking is not a neutral
efficiency setting in this project. Obs 140 (`docs/notes/working-notes.md:2239`)
established that HIGH thinking is itself an **unregistered diversity mechanism**:
"HIGH thinking consensus outperforms MINIMAL thinking consensus by +6.8 percentage
points on F1", by a mechanism Obs 140 names explicitly — "At N=30, HIGH thinking
produces 3–4× more detection clusters than MINIMAL" — and concludes "Thinking level
interacts with temperature and pool size in ways that make it an experimental factor
for consensus voting workflows, not merely an efficiency setting." H9 is the hypothesis
that tests whether *added* diversity across consensus passes improves detection. Running
every H9 condition — including the H9-A identical-passes baseline — at a thinking level
that is itself a diversity mechanism means the baseline already carries substantial
pass-to-pass diversity. If that raises the floor, the H9 contrasts have less headroom to
show a diversity effect, and the H9 null may be biased toward acceptance. **This
concerns the null's direction, not only its level**, and it should be stated in the
paper wherever the H9 result is reported.

**Mitigating scope**: the setting is **constant across every compared condition** within
H9 — both tracks, all five track-1 conditions (h9-A through h9-E) and all four track-2
conditions (h9-A, h9-B, h9-D, h9-E; h9-C image diversity is degenerate for the text-only
track), across all 225 passes. No H9 contrast is between a HIGH condition and a minimal
one. Separately, the
verification campaign's finding 9 records that of the 41 configs originally flagged for
unlicensed HIGH thinking, **17 were already licensed by name** (E49, E51, E52, E53,
Decision 20); the residue this erratum addresses is the **22 `phase3c` configs**.

**Post-facto acknowledgement**: this disclosure is written in July 2026 about a March
2026 execution, with the H9 result in hand. The thinking level was disclosed on the
study YAMLs at the time and was visible to anyone reading them; what was missing was an
erratum recognising that it departed from §8.9's registered `minimal` decision.

**Protocol impact**: H9 is exploratory (Tier A), so no confirmatory claim is affected.
The H9 result must be reported with two riders: (a) the runs were executed at HIGH
thinking, not the registered `minimal`; (b) HIGH thinking is itself a diversity
mechanism (Obs 140), so the H9 baseline is not a low-diversity baseline and the null
should be read accordingly. Cross-references: E34 (thinking-level propagation),
E42 (metadata field reliability; "Never trust a single metadata field for audit
purposes"), E53 (Phase 3a-HIGH track), Decision 20 (controlled thinking-level
replication), Obs 140 and Obs 141.

---

## Draft 3 — queue item 3: registration-internal-inconsistency reconciliation

> **Drafting note (policy)**: drafted under charter § 10 item 7 (b) — "file errata
> recognising each internal contradiction in the lodged text; adopt the reading that
> fits the spirit of the campaign; explain the reasoning; acknowledge openly that the
> choice is post facto, made with results in hand." Each of the five sub-items below
> therefore carries: both conflicting spans verbatim, the operative reading, the
> reasoning, and the post-facto acknowledgement.

### E64: Five internal contradictions in the lodged registration — operative readings adopted, reasoning stated, post-facto status acknowledged

| Field | Value |
|-------|-------|
| Date | 2026-07-29 (PI policy decision, GATE 1) |
| Type | Clarification (five reconciliations; no registered procedure altered) |
| Commit | — |
| Files | `osf/preregistration.md` (`:78`, `:269`, `:300`, `:442`, `:815`, `:936-938`, `:968`, `:1443`, `:1450-1451`, `:1882`, `:1892`, `:1898-1901`, `:1921`); `osf/preregistration-coverage.md:237` |
| Impact | None on executed procedure — in every case the execution followed one of the lodged readings. Impact is on interpretation and on the paper's Methods: five parameters are specified two or three ways in the lodged text, and this entry fixes which reading governs |

**Why one entry**: the Phase 1 verification campaign's meta-finding is that the single
most recurrent root cause across its twelve headline findings is **internal
inconsistency within the lodged registration itself** — the same parameter specified two
or three ways, with execution following one of them (findings 1, 2, 6, 7, 8, 11;
`reports/verification/apparatus/defence-pass-adjudication-2026-07-29.md` § "Meta-finding").
Filing five separate errata would obscure the pattern. This is a finding about
preregistration authoring, not misconduct, and it belongs in the paper's Discussion.

**Standing acknowledgement, applying to all five**: each operative reading below was
adopted in **July 2026, with the results in hand**. In every case the execution had
already committed to one reading long before the contradiction was catalogued; what is
post facto is the *recognition and justification*, not the choice of procedure. Where an
operative reading happens to be the conservative one, that is noted; where it is not,
that is noted too.

**Summary**:

| # | Parameter | Lodged reading A | Lodged reading B | Operative reading adopted |
|---|-----------|------------------|------------------|---------------------------|
| i | Hard-example mining K and filter | `:815` — K=10 baseline runs, any-run candidacy | `:1443` — 5 passes; `:1450-1451` — ≥3/5 filter | **The executed procedure**: K=5 passes, any-run HP candidacy (reading A's rule), ≥3-of-5 HN filter (reading B's rule) |
| ii | Corpus size and reserve | § 2.1 `:78` — 361 total, `:76` — 281 reserve | § 8.6 `:1921` — "~360 total"; coverage § 9 `:237` — "321 available" | **The 360 physical tiles** (§ 8.6) |
| iii | Voting cluster membership | § 8.5 step 4 `:1882` — cluster on distance **and matching label** | § 8.5 `:1892` — label is a post-hoc majority vote; § 4.1.2 — evaluation is label-blind | **Spatial clustering, then post-hoc majority label** |
| iv | Tile overlap at 384 px | H11 `:968` — "64px overlap" | H11 `:959` — "~1.8×" API-call multiplier | **Constant overlap fraction** — 48 px overlap, stride 336 at 384 px |
| v | Test tailedness | § 3.1 `:269` — one-tailed for directional predictions | H1 `:442` — two-tailed for modality; § 3.6 `:300` — power computed two-tailed | **Two-sided throughout** |

---

#### (i) Hard-example mining: K and the candidacy filter

**Reading A** (`osf/preregistration.md:815`, § H8 "Availability constraint"), verbatim:

> "The training set contains 36 mounds across 20 tiles. Hard examples are drawn from
> failures across K=10 baseline runs (a mound missed in any run is a candidate HP; any
> false detection is a candidate HN)."

**Reading B** (`osf/preregistration.md:1443`, § 8.4.1 Step 1), verbatim:

> "- Passes: 5 × 20 training tiles = 100 API calls"

and (`osf/preregistration.md:1450-1451`, § 8.4.1 Step 2), verbatim:

> "- **False Negatives (FNs)**: Ground truth mounds missed in ≥3/5 passes"
>
> "- **False Positives (FPs)**: Detections in ≥3/5 passes with no matching ground truth"

The two passages contradict each other twice over: K=10 versus five passes, and
*any-run* candidacy versus a *≥3-of-5* majority filter. Both are lodged.

**Operative reading**: the executed procedure — **K=5 passes; hard positives by the
any-run rule of reading A; hard negatives by the ≥3-of-5 filter of reading B.** This is
verifiable in the artefact: `outputs/h10/hard-cases-v2/pool_160/hard_cases_register.json`
records `k_passes: 5`, and its summary block reconciles exactly —
`borderline_tp: 82` (missed in at least one of five passes) + `consistent_fn: 26`
(missed in all five) = `hp_candidates: 108`, the any-run count; while
`consistent_fp: 57` = `hn_candidates: 57`, the majority-filtered count, out of
`total_fp_clusters: 720`.

**Reasoning**: the hybrid is not opportunistic. The pass count is settled by § 8.4.1,
which is the *operative procedure section* — the registration's own step-by-step
construction protocol — against a parenthetical inside an availability-constraint
paragraph in the H8 hypothesis section. The HP rule follows reading A because the
campaign's binding constraint was hard-positive scarcity, documented at the same line
815 ("If fewer than 16 distinct HPs or HNs are available, Scale-32 (and possibly
Scale-16) will be capped at the maximum available") and exercised in E11 and Decision 11;
a ≥3-of-5 filter on FNs would have deepened an exhaustion the registration already
anticipated. The HN rule follows reading B because false-positive clusters were
abundant (720 candidates), so the stricter filter costs nothing and buys quality. The
spirit of the campaign — build the strongest available hard-example library under a
1:1 ratio constraint — selects each rule on the side where it binds.

**Prior treatment and residue**: E15 already corrects the *appendix's* stale "≥3/10"
references to ≥3/5 and records "Phase 1 was executed with K=5 passes as specified by the
operative procedure". **No erratum has ever named line 815.** This sub-item is that
naming. E15, E49, and E51 license the K=5 substance downstream.

**Post facto**: adopted July 2026. The library built under this hybrid has been in
production since Phase 1; the reconciliation is a justification of a settled fact.

---

#### (ii) Corpus size and the reserve set

**Reading A** (`osf/preregistration.md:76,78`, § 2.1 Map Tile Corpus), verbatim:

> "| Reserve set | 281 | Confirmatory testing | **Untouched** |"

and, two lines later:

> "**Total**: 361 tiles from 4 annotated Soviet topographic map sheets. Maps were
> hand-annotated by students with comprehensive expert review."

**Reading B** (`osf/preregistration.md:1921`, § 8.6 Tile Selection Methodology),
verbatim:

> "- **Tiles**: 512×512 pixel tiles at native resolution (~90 tiles per map, ~360 total)"

**Reading C** (`osf/preregistration-coverage.md:237`, § 9 Stage 2 Design Principles),
verbatim:

> "2. Use **80-160 reserve tiles** (from 321 available)"

Three figures for one corpus: 361 total with a 281-tile reserve; ~360 total; and a
321-tile reserve.

**Operative reading**: **the 360 physical tiles.** `find inputs/tiles -name "*.png"`
returns **360**; `inputs/tiles/full_evaluation_manifest.json` contains **340** entries
(= 360 − 20 calibration tiles); `inputs/tiles/calibration_manifest.json` contains 20 and
`inputs/tiles/validation_manifest.json` contains 60. The reserve is therefore
360 − 20 − 60 = **280**, not 281 and not 321. § 8.6's "~360" is the accurate statement;
§ 2.1's 361 is off by one and its 281 inherits that off-by-one; coverage § 9's 321 is
reconcilable with neither and appears to be a residue of an earlier tile-selection draft.

**Reasoning**: § 8.6 is the methodology section that generated the tiles, and it is the
only one of the three that matches the artefacts on disk. The 361st tile never existed —
repository history contains no deletion of a tile file. Adopting the physical count is
not a choice between defensible alternatives; it is the correction of an arithmetic
slip in the lodged text, and it is adopted because every downstream artefact already
embodies it.

**Consequence, disclosed**: the reserve's status. § 2.1 marks the reserve
"**Untouched**"; E36 (2026-03-17) expanded the evaluation corpus to 340 tiles, which
absorbs the entire reserve. E36's own numbers disclose this; a dated correction block
attached to **E20** (Draft 4, block 3 below) records that E20's "The 281-tile reserve
remains unnamed/untouched" was falsified by that expansion.

**Post facto**: adopted July 2026. The 340-tile corpus has been the production
evaluation set since March 2026.

---

#### (iii) The voting step-4 label clause

**Reading A** (`osf/preregistration.md:1882`, § 8.5 Spatial Clustering Algorithm,
step 4), verbatim:

> "   - Greedy clustering: for each unclustered detection, find all others within 20m
> and matching label; group as cluster"

**Reading B** (`osf/preregistration.md:1892`, § 8.5 Consensus Detection Output),
verbatim:

> "- **Label**: Majority vote among constituent detection subtypes"

together with § 8.5's own alignment clause (`osf/preregistration.md:1898-1901`),
verbatim:

> "The 20m clustering threshold deliberately matches the spatial tolerance used in F1
> calculation (Section 4.1.1). This ensures that:
>
> - Detections considered "the same" during voting are also treated as matching the same
> reference during evaluation
> - No artificial precision loss from threshold misalignment"

and § 4.1.2's matching algorithm, which is purely spatial — steps 1–7 at
`osf/preregistration.md:362-368` compute pairwise centroid distances, threshold them at
20 m, and run the Hungarian assignment, with **no reference to labels or subtypes
anywhere**.

**Operative reading**: **spatial clustering, then a post-hoc majority label** — that is,
reading A's label gate is not applied.

**Reasoning**: reading A is self-defeating on the registration's own terms. If cluster
membership already requires matching labels, then every cluster is label-homogeneous by
construction and reading B's "Majority vote among constituent detection subtypes" is
vacuous — the registration would be specifying a majority vote over a set that can only
ever hold one value. Reading A also breaks the registration's own alignment clause:
evaluation (§ 4.1.2) matches on distance alone, so a label-gated voting step would split
into two clusters what evaluation will treat as one location, which is exactly the
"artificial precision loss from threshold misalignment" that § 8.5 says the design
exists to prevent. Only the spatial-only reading leaves both of § 8.5's other provisions
with work to do. This is a case where the registered text contains a clause that cannot
be executed without nullifying two neighbouring clauses in the same section.

**Materiality, bounded**: the difference only bites where two detections within 20 m
carry different subtypes. Most detections are `burial_mound`; a spot-check of the
`phase3c` track-1 H9-A run-1 pool (4 954 detections) gives 82.8 % `burial_mound`,
10.1 % `benchmark_mound`, 6.4 % `triangulation_mound`, 0.7 % `settlement_mound` —
i.e. ~17 % non-`burial_mound`, and the defence pass records ~21 % on its pool. The
materiality bound is therefore of order one detection in five *at most*, and lower in
practice since co-located differing-subtype pairs are rarer than differing subtypes
overall.

> **Drafting note**: the gate package § 2 finding 8 states "~21 % non-mound subtypes".
> My independent spot-check on a `phase3c` pool gives 17.2 %. Both are order-consistent;
> the draft above reports both rather than picking one. The orchestrator may wish to
> pin a single corpus-wide figure before this lands.

**Post facto**: adopted July 2026. The spatial-only implementation has been in the
voting code since the pipeline was built.

---

#### (iv) Tile overlap at 384 px

**Reading A** (`osf/preregistration.md:968`, § H11 Implementation), verbatim:

> "- Tiles generated from source maps with 64px overlap"

**Reading B** (`osf/preregistration.md:959`, § H11 condition table), verbatim:

> "| B | 384×384 | 0.56× | ~1.8× | Higher |"

**Operative reading**: **constant overlap fraction — 48 px overlap, stride 336, at
384 px.**

**Reasoning**: the registration's own cost arithmetic requires it. At the 512 px
baseline (§ 8.6 `:1921`), a 64 px overlap gives stride 448. Preserving that overlap
*fraction* (64/512 = 12.5 %) at 384 px gives overlap 48 and stride 336, and the tile
count scales as (448/336)² = **1.78× — the "~1.8×" the registration states**. Carrying
the 64 px overlap across *literally* gives stride 320 and (448/320)² = **1.96×**, which
the registration does not state. Reading A and reading B cannot both hold; reading B is
the one the registration used to justify the condition's cost, and it is the one that
matches the 0.56× area multiplier in the same row. Execution followed reading B: stride
336 is disclosed in E51's parameter table (`protocol-errata.md:1459`, "| Stride | 448 px
| 336 px |") and carried into E52 (`:1600`, "| Stride | 448 px | 336 px (E51) |"), and it
is hard-coded in the analysis pipeline (`scripts/evaluate_detections.py:1330`,
"stride=336 overlaps neighbours by 48 px"; `scripts/build_example_pool.py:243`).

**Residue, stated plainly**: E51 and E52 disclose the executed stride as a parameter of
their re-runs. **Neither addresses `osf/preregistration.md:968` on its own terms** — that
is, neither says "the registered 64 px overlap clause was not followed, and here is
why". This sub-item is that statement.

> **Drafting note**: the gate package § 2 finding 11 cites "E51/E52 and Obs 211" for
> the stride disclosure. Obs 211 (`docs/notes/working-notes.md:6336`) is a QGIS
> false-positive taxonomy and does not discuss stride. The draft cites E51 and E52 only.

**Post facto**: adopted July 2026. The 384 px corpus was generated at stride 336 in
early 2026 and every 384 px result in the project rests on it.

---

#### (v) Test tailedness

**Reading A** (`osf/preregistration.md:269`, § 3.1 Significance Testing), verbatim:

> "- **Direction**: One-tailed for directional predictions; two-tailed for equivalence
> tests (H1)"

**Reading B**, two lodged instances that contradict reading A. § H1 Analysis
(`osf/preregistration.md:442-443`), verbatim:

> "- Two-tailed tests for modality comparisons"
>
> "- One-tailed for elaboration: H0: verbose ≤ brief; H1: verbose > brief"

— i.e. H1 is *not* uniformly an equivalence test as § 3.1 asserts; it is split, with
directional elaboration contrasts run one-tailed and modality contrasts two-tailed. And
§ 3.6 Power Considerations (`osf/preregistration.md:300`), verbatim:

> "With 60 holdout tiles containing 79 mound symbols, statistical power is adequate for
> detecting moderate effects. Approximate detectable effect sizes (80% power, α = 0.05,
> two-tailed):"

— i.e. the registration's own power calculation, which underwrites the whole design, was
computed **two-tailed**, including for the directional hypotheses § 3.1 would run
one-tailed.

**Operative reading**: **two-sided tests throughout.**

**Reasoning**: two-sided is **strictly conservative** for a directional prediction — it
demands a larger effect to reach the same α, so no claim is strengthened by the choice
and any surviving claim would also have survived the one-tailed rule. It is also the
reading consistent with the registration's own power arithmetic (§ 3.6), so the design's
stated detectable effect sizes remain valid rather than being optimistic by construction.
The scope of the contradiction is narrow: the one-tailed rule bites H2, H3, H4, and one
H1 elaboration contrast only. It should be stated plainly that **no tailedness licence
exists anywhere in the errata**: the executed two-sided practice was never erratum'd
before now.

**Post facto**: adopted July 2026, with results in hand. Mitigating the post-facto
concern: because two-sided is the conservative direction, adopting it after seeing
results cannot have manufactured a significant finding — it can only have suppressed
one. Any hypothesis that would have been significant one-tailed but is not two-sided
should nonetheless be reported as such in the paper, so the reader can apply the
registered rule if they prefer it.

---

**Protocol impact (E64 as a whole)**: none on executed procedure. In all five cases
execution followed one of the lodged readings; nothing is being changed, only
adjudicated. Reporting requirements: (a) the paper's Methods states the operative
reading for each of the five parameters; (b) the Discussion carries the meta-finding —
that a registration can be internally inconsistent in five distinct places without any
single inconsistency being visible at authoring time, and that this is a hazard of long,
multiply-revised preregistrations rather than of this project in particular; (c) each
operative reading is flagged as adopted post facto. Cross-references: E11 and Decision 11
(HP pool exhaustion), E15 (appendix pass-count corrections), E20 and E36 (corpus and
reserve), E45 (unregistered inference method — the tailedness question compounds it),
E49/E51/E52 (K=5 substance and stride disclosure), E53.

---

## Draft 4 — queue item 4: dated correction blocks for existing entries

These follow the append-style pattern established by E37 ("**Withdrawal
(2026-07-28)**: …") and E45 ("**Correction (2026-07-28)**: …"): the entry's title and
`Date` field are amended to signal the revision, and a dated block is inserted
immediately below the field table, before the original Description. The original text is
retained and its erroneous span identified rather than deleted.

---

### Block 1 — attach to E36

**Amend the heading** to:

> ### E36: 340-tile production retest replaces 60-tile holdout evaluation (corrected 2026-07-29)

**Amend the `Date` field** to:

> | Date | 2026-03-17 (original); **corrected 2026-07-29** — see Correction |

**Insert immediately below the field table**:

**Correction (2026-07-29)**: this erratum's Description states that on the 60-tile
holdout "only 1 of 10 Phase 2a pairwise comparisons survived FDR correction (Obs 155)".
**The correct figure is zero.** `results/phase2a-analysis-report.json` — the artefact
this claim summarises, generated 2026-02-06 and committed 2026-02-08 (`57ec68c25`) —
records `n_comparisons: 10`, `n_initially_significant: 3`, and **`n_fdr_significant: 0`**,
with a `recommendation` field that says so in words: "No pairwise differences
significant after FDR correction (q=0.05)." Every committed version of that artefact
records 0; no version has ever recorded 1. The defence pass independently re-ran the
Benjamini–Hochberg routine and reproduced 0.

**Severity context, stated because it cuts against the reflex to minimise**:

1. **The error is self-adverse.** Zero surviving comparisons is a *stronger* rationale
   for the corpus expansion this erratum records than one surviving comparison. The
   mistake understated the case for the decision it justifies.
2. **It was inherited, and the source is worse than a mis-transcription.** The claim is
   attributed to Obs 155. **Obs 155 contains no FDR result at all.** Observation 155
   (`docs/notes/working-notes.md:2754`) is "Extended reasoning as liberaliser — more
   thinking, worse precision (2026-03-10)", an analysis of 44 verifier candidates under
   HIGH versus minimal thinking; a full-text scan of the entry returns zero occurrences
   of "FDR", "bootstrap", "holdout", or "pairwise". The citation does not merely
   mis-report a number in Obs 155; it points at an observation that never made the claim.
3. **It propagated to four documents.** `docs/methodology/preregistration/protocol-errata.md:890`
   (this entry); `reports/experimental-progression.md:83` ("only 1 of 10 Phase 2a pairwise
   comparisons survived FDR correction"); `reports/gs-tile-pool-mapping-2026-05-28.md:45`
   (quoting "only 1 of 10 / Phase 2a comparisons" surviving FDR correction);
   `docs/notes/working-notes.md:3397`, in the "Transition to Production Runs (Session 52)"
   block ("Only 1 of 10 Phase 2a comparisons / survived"). All four require the same
   correction to 0.
4. **It escaped the 2026-07-28 preregistration-integrity sweep** and was caught only by
   the Phase 1 execution census the following day.

**What does not change**: the corpus expansion decision, the 340-tile scope, the power
rationale, and every downstream result. The corrected figure strengthens the rationale
rather than undermining it. Identified by the Phase 1 verification campaign
(`reports/verification/phase1-gate-package.md` § 2 finding 5;
`reports/verification/apparatus/defence-pass-adjudication-2026-07-29.md` F5).

---

### Block 2 — attach to E16

**Amend the heading** to:

> ### E16: Prompt text shifted from cartographic naming to visual descriptions (corrected 2026-07-29)

**Amend the `Date` field** to:

> | Date | 2026-02-03 (original); **corrected 2026-07-29** — see Correction |

**Insert immediately below the field table**:

**Correction (2026-07-29)**: this erratum's "Scope of changes" states that "The prompt
structure (preamble, decision procedure, exclusion categories), factor design (H5
levels, M/E levels), and example library are unchanged", and its Protocol impact states
that "the set of features being described and the diagnostic logic (ray
presence/absence, direction of marks) are preserved". **The "unchanged" and "preserved"
claims are inaccurate as they stand.** Commit `2d46311`, which this erratum records, did
not only reword existing material: it **added three new exclusion sections**, enumerated
in the commit's own message:

| Commit-message change | New section added |
|-----------------------|-------------------|
| "Change 2B — Cyrillic text: New exclusion items (terse bullet + verbose subsection) flagging Cyrillic characters as a confound." | `### Cyrillic Map Text` |
| "Change 3 — Round shapes: New catch-all exclusion for round/ovoid shapes in mound-like colours without outward-radiating rays." | `### Other Round Shapes in Mound-Like Colours` |
| "Change 4B — Dense features: New "Symbols Amid Dense Features" subsection in verbose files." | `### Symbols Amid Dense Features` |

All three headings are verifiable as additions in `git show 2d46311 --
prompts/system-instructions`. The same commit also inserted a new diagnostic principle
("Opus P3b — Insert visual-diagnostic-principle in Core Diagnostic: 'Base all detections
on the visual sunburst diagnostic only.'").

**The correct characterisation** is therefore: the *exclusion categories were extended*,
not held constant, and *the set of features being described was enlarged* — Cyrillic map
text, round/ovoid shapes without rays, and dense-feature contexts were not described in
the lodged appendix text at all. What genuinely is unchanged is the **factor design**
(H5 levels, M/E levels) and the **example library**; and the core diagnostic logic (ray
presence/absence, outward versus inward direction) is genuinely preserved — the
additions sharpen and extend it rather than replacing it. The change remains conservative
in effect, and the changes were still applied uniformly across all H5 conditions, so no
condition contrast is confounded.

**Why this matters**: E16 is the register entry a reader consults to learn how far the
executed prompts diverge from the lodged appendix. An "unchanged" claim in that entry
understates the divergence. Identified by the Phase 1 verification campaign
(`reports/verification/phase1-gate-package.md` § 2 finding 4;
`reports/verification/apparatus/defence-pass-adjudication-2026-07-29.md` F4), whose
broader ruling was a **major downgrade** of the prompt-divergence concern: the lodged
appendix was byte-accurate at lodgement, all drift is post-lodgement across five commits
(2026-02-02 to 2026-02-11), four of them erratum'd within 24 hours, and the restructure
is licensed by E14. This correction and the `5e7601d77` entry (E65) are the residue.

---

### Block 3 — attach to E20

**Amend the heading** to:

> ### E20: Standardised "holdout" → "validation" naming across codebase (corrected 2026-07-29)

**Amend the `Date` field** to:

> | Date | 2026-02-05 (original); **corrected 2026-07-29** — see Correction |

**Insert immediately below the field table**:

**Correction (2026-07-29)**: this erratum's Rationale closes with "The 281-tile reserve
remains unnamed/untouched." **That statement was falsified 40 days later and was never
amended.** E20 is dated 2026-02-05; E36 is dated 2026-03-17 and records the expansion of
the evaluation corpus to 340 tiles — which is the full 360-tile physical corpus minus the
20 calibration tiles, and therefore absorbs the *entire* reserve. From 2026-03-17 the
reserve was neither unnamed (it is enumerated in
`inputs/tiles/full_evaluation_manifest.json`, 340 entries) nor untouched (every Phase 2a–3a
condition was re-run across it). E36's own numbers disclose the absorption; what was
missing was an amendment here, at the entry that asserts the opposite.

**Secondary correction**: the reserve's size. E20 says "281-tile"; the physical corpus is
**360** tiles (`find inputs/tiles -name "*.png"` → 360), of which 20 are calibration and
60 validation, leaving a reserve of **280**. The 281 figure inherits the off-by-one in
§ 2.1's "**Total**: 361 tiles" — see E64 sub-item (ii), which adopts § 8.6's "~360" as
the operative corpus count.

**What does not change**: the naming standardisation itself, which is what E20 exists to
record, and its "Protocol impact: None" assessment for that naming change. Identified by
the Phase 1 verification campaign
(`reports/verification/apparatus/defence-pass-adjudication-2026-07-29.md` F7, where the
defence raised it against its own interest).

---

## Draft 5 — queue item 5: small errata

> **Drafting note (house style)**: drafted as **three short entries** rather than one
> entry with three sub-items. The three items differ in `Type` (Deviation /
> Clarification / Correction) and in blast radius, and the errata document's prevailing
> style is one entry per discrete fact with a single Type in the field table (E1–E35 are
> almost uniformly of this shape). Bundling them would force a compound Type field. If
> the PI prefers a single bundled entry, the three bodies below merge without change
> under a shared heading, and E66/E67 renumber to sub-items.

### E65: Registered verifier prompt `verify_brief.md` edited post-lodgement (commit `5e7601d77`) — the one prompt-divergence commit with no contemporaneous erratum

| Field | Value |
|-------|-------|
| Date | 2026-07-29 (disclosure; commit 2026-02-03) |
| Type | Deviation (lodged prompt text altered post-lodgement; lodged appendix never amended) |
| Commit | `5e7601d77` |
| Files | `prompts/system-instructions/verify_brief.md`, `prompts/system-instructions/propose_brief.md`; lodged text at `osf/preregistration-appendix-prompts.md:1088-1128` |
| Impact | Low-medium. Affects the `verify_brief` verifier strategy arm only; E39 establishes verifier strategy is not load-bearing, and the production pipeline uses `verify_adversarial.md` |

**Description**: the Phase 1 verification campaign established that the lodged prompt
appendix was byte-accurate at lodgement and that all subsequent divergence occurred in
five post-lodgement commits between 2026-02-02 and 2026-02-11, **four of which were
erratum'd within 24 hours**. Commit `5e7601d77` (2026-02-03, "feat(prompts): Update
two-stage prompts per Opus review") is the fifth, and carries no contemporaneous
erratum. This entry supplies it.

**What changed in `verify_brief.md`** — the registered H2 Stage-2 verifier prompt, lodged
verbatim at `osf/preregistration-appendix-prompts.md:1088-1128` (§ 1.6.2, "**Used by**:
H2 (Stage 2)"). The commit:

1. **Rewrote key test 2.** Lodged: "2. Do rays point OUTWARD (mound) or INWARD
   (quarry/pit)? Inward → not a mound." Executed: "2. Do rays point OUTWARD (mound) or
   are there marks pointing INWARD (not a mound)? Inward marks may appear in orange-brown,
   the same colour family as mound symbols."
2. **Added key test 5** (not present in the lodged text): "5. Is the shape round or ovoid
   in mound-like colours but without outward-radiating rays? Dark marks within the shape
   rather than extending outward → not a mound."
3. **Added key test 6** (not present in the lodged text): "6. Does nearby Cyrillic text
   (e.g., "могила", "кург.") appear to confirm the candidate? Text does not confirm or
   deny — the ray pattern is the sole criterion."
4. **Extended the reference-example sentence.** Lodged: "If reference examples are
   provided, compare the candidate against them." Executed: the same sentence plus "Each
   reference image is centred on the feature being labelled."

The same commit made two smaller edits to `propose_brief.md` (occlusion language,
centre-pointing sentence); E58 already records that `propose_brief` was **never used** in
any PV experiment, and cites this commit as "prompt refinement, never invoked"
(`protocol-errata.md:1939`). The `verify_brief.md` half is different: `verify_brief.md`
**was** executed, as the "brief" arm of the verifier-strategy comparison
(`prompts/configs/verify_brief.json`, `verify_brief-text.json`;
`studies/phase3d-h2-twostage.yaml:68`; outputs under
`outputs/h11/proposer-verifier-384/verified-brief-*`).

**Rationale for the edits** (from the commit message): they apply the same hard-example
review outcomes recorded in E16 — Change 2A (marks/rays distinction), Change 3 (round
shapes), Change 2B (Cyrillic text) — to the two-stage prompts, "which were still in their
pre-hard-example state". The intent was consistency across the prompt suite, not a
change to the verifier's decision rule; the diagnostic criterion (outward-radiating rays)
is unchanged and the added tests operationalise exclusions already present elsewhere.

**Protocol impact**: the `verify_brief` verifier arm was executed against a prompt that
differs from the lodged appendix text in the four respects above; the lodged appendix was
never amended. Blast radius is bounded by E39, which found all three verifier strategies
statistically indistinguishable at 340-tile scale (adversarial 0.770, checklist 0.769,
brief 0.752, all CIs overlapping), and by the fact that the production pipeline uses
`verify_adversarial.md`, not `verify_brief.md`. Cross-references: E14, E16 (and its
2026-07-29 correction block), E39, E58.

---

### E66: `run_study.py` → `run_phase1.py` / `run_phase2.py` orchestration substitution — formalising Decision 15

| Field | Value |
|-------|-------|
| Date | 2026-07-29 (disclosure; substitution 2026-02-05) |
| Type | Clarification (orchestration layer substituted; batch engine unchanged) |
| Commit | `c64a7dceb` (adds `run_phase2.py`, archives `run_study.py`) |
| Files | `scripts/run_phase1.py`, `scripts/run_phase2.py`, `archive/deprecated-scripts/run_study.py`, `scripts/4_detect_mounds_batch.py`; lodged mapping at `osf/preregistration.md:2027-2032` |
| Impact | None on results. The script that issues API calls and records metadata is the one the registration names and is unchanged |

**Description**: § 8.7.3 of the registration maps hypotheses to scripts, naming
`run_study.py` in five of six rows — for example "| H1, H4, H5, H7 | `run_study.py`,
`4_detect_mounds_batch.py` | `lib_advanced_metrics.py` |"
(`osf/preregistration.md:2027`) and "| H9 | `run_study.py` (extended for diversity) |
`lib_advanced_metrics.py` |" (`:2032`). Execution did not use `run_study.py`. Phase 1
used `run_phase1.py`; Phases 2a–2e and the retest phases used `run_phase2.py`;
`run_study.py` was archived to `archive/deprecated-scripts/`.

**Decision and documentation**: the substitution is Decision 15 in
`docs/methodology/preregistration/decisions-log.md:671` ("Replace run_study.py with
run_phase2.py for Phase 2 Execution", dated 2026-02-05), which records four structural
incompatibilities between `run_study.py` and the one-factor-at-a-time (OFAT) YAML
structure: hard-coded factorial factor names, a `defaults` versus `fixed` schema
mismatch, no runs loop, and no `{condition}/run_{K}/` output hierarchy. It is also logged
in the execution-checklist deviation table
(`docs/methodology/preregistration/execution-checklist.md:92`: "| 2026-02-05 | D15:
run_phase2.py replaces run_study.py | New OFAT runner for Phase 2; run_study.py archived
to archive/deprecated-scripts/ |"). What was missing was an erratum. This entry supplies
it, formalising Decision 15 as a protocol deviation record.

**Precision on what is and is not post-lodgement**:

- `scripts/run_phase1.py` was **first committed 2026-01-21** (`fa5d53ede`) — ten days
  **before** lodgement (2026-01-31). It is not a post-lodgement substitution; the
  registration simply did not name it. E2 already refers to it by name.
- `scripts/run_phase2.py` was first committed **2026-02-05** (`c64a7dceb`), the same
  commit that archived `run_study.py`. This is the genuinely post-lodgement limb.
- `scripts/4_detect_mounds_batch.py` — the **batch engine named in the same lodged
  rows** — was first committed 2025-12-18 (`88545c84a`) and was not replaced. It remains
  the component that constructs prompts, issues API calls, and writes detection
  metadata.

**Protocol impact**: none on results. The substitution replaced an orchestration wrapper
— condition enumeration, run looping, checkpointing, output-directory layout — while
leaving the execution engine the registration names in place. No prompt, model,
temperature, thinking level, library, or evaluation parameter changed as a consequence.
The disclosure is owed because the registration names a specific script and that script
was not the one used. Cross-references: E2 (`run_phase1.py` config self-containment),
E34 (`run_phase2.py` thinking-level propagation), Decision 15.

---

### E67: Stale version header in the lodged preregistration — "Document version: 4.6" against a v4.7 changelog

| Field | Value |
|-------|-------|
| Date | 2026-07-29 |
| Type | Correction (documentation metadata; no protocol content affected) |
| Commit | — |
| Files | `osf/preregistration.md:2388` |
| Impact | None on protocol. Cosmetic, but it is the version string a reader of the lodged document sees |

**Description**: the lodged preregistration's footer reads, verbatim
(`osf/preregistration.md:2388-2390`):

> *Document version: 4.6*
> *Created: 2025-12-22*
> *Updated: 2026-01-31*

while the changelog immediately below it opens with a **v4.7** entry
(`osf/preregistration.md:2394`): "- v4.7: Statistical methodology reconciliation — All
per-hypothesis ANOVA references updated to bootstrap CI + FDR, aligning Sections 5–6
with the statistical analysis plan (Section 3) and Decision 10 … no change to
hypotheses, predictions, or experimental design". The v4.7 revision was applied to the
document body — §§ 5–6 do specify pairwise bootstrap comparisons — but the version
string in the footer was not incremented with it. The `Updated:` date (2026-01-31) is
correct and matches the lodgement date.

**Corroboration that v4.7 is the operative version**: the errata document's own header
states "**Associated preregistration**: `preregistration.md` v4.7 (2026-01-31)"
(`protocol-errata.md:5`), and E61 relies on the v4.7 reconciliation as the explanation
for a surviving drafting residue ("'Main effect' is analysis-of-variance vocabulary
surviving from the pre-v4.7 draft; the v4.7 statistical reconciliation replaced
per-hypothesis ANOVA with pairwise bootstrap comparisons").

**Protocol impact**: none. The document content is v4.7; only the footer string is stale.
Because the repository copy has been verified byte-identical to the OSF-posted artefact
(verification recorded in E37's 2026-07-28 withdrawal block), **the stale string is
present in the lodged artefact and cannot be silently repaired** — it is disclosed here
rather than edited. Any paper text or companion document citing the preregistration
should cite **v4.7 (2026-01-31)**. Cross-references: E1 (the same class of
version/date drift in the OSF companion README), E61.

---

## Consolidated drafting notes for the orchestrator / PI

1. **Count discrepancy (E62)**: "four verifier-parameter levels" in the brief and gate
   package; the census and the enumeration both give **five**. Confirm before landing.
2. **Scope surprise (E62)**: `verifier_thinking_level=medium` sits entirely within
   `pv-diag-384`, a licensed family — not within the three unlicensed families. Confirm
   whether it belongs in this entry or its own.
3. **Null field (E62)**: `pv-diag-256`'s `purpose` in `results/runs-manifest.json` is
   `null`. The draft falls back to `run-conditions.json`'s `_note` and says so. Consider
   populating the manifest field.
4. **Figure to pin (E64 iii)**: gate package says ~21 % non-mound subtypes; my
   `phase3c` spot-check gives 17.2 %. The draft reports both.
5. **Citation to drop (E64 iv)**: gate package finding 11 cites Obs 211 for the stride
   disclosure; Obs 211 is a QGIS false-positive taxonomy and does not discuss stride.
   The draft cites E51:1459 and E52:1600 instead.
6. **Numbering**: these drafts claim E62–E67 contiguously after the live document's last
   entry, E61. If queue item 6 (the CMT-0109 rider retiring the academic-baseline
   designation, recommended at gate package § 3 item 6) is also approved, it should take
   E68 — it is not drafted here, being outside this brief.
7. **Correction blocks**: all three are drop-in — each specifies the amended heading, the
   amended `Date` field, and the block text to insert below the field table. Original
   Descriptions are left intact per the E37/E45 pattern.
