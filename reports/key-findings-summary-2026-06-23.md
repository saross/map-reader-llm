# Detecting burial mounds on historical maps with vision-language models — key findings summary

**Date:** 2026-06-23 **Status:** DRAFT for Shawn's review before circulation to colleagues.
**Audience:** archaeologists — no machine-learning or statistical background assumed; technical terms
are glossed in plain language on first use. Every number traces to a registered analysis or to a
section of the working Results draft (`docs/paper/results-draft.md`), all re-read at source for this
summary. Dollar figures are on the audited cost basis (per-request token metadata at June 2026
"flex" batch rates; `reports/token-load-audit-2026-06-12.md`).

---

## 1. The approach, in brief

We tested whether a **vision-language model (VLM)** — a general-purpose AI that takes an image plus a
text instruction and answers in words — can find **burial-mound symbols** (the Soviet sunburst-with-
hachures convention) on **four Soviet 1:50,000 topographic sheets of the Thracian Plain, Bulgaria**
(~5 m/pixel; 569 expert-verified mound symbols, originally digitised by students in FAIMS). The model
throughout is **Gemini 3 Flash**, chosen for free-tier access and low cost at scale.

The study is **preregistered** (OSF) and runs on **two deliberately different instruments**, a
distinction that governs everything below:

- a **gold-standard (GS) set** — the four curator-checked maps (≈ 487 image tiles) — which *characterises*
  how well a configuration localises mounds against trusted ground truth; and
- a **55-map deployment set** — 8,541 tiles with an extended ground truth of 4,746 reviewed student
  digitisations plus 773 adjudicated additional mounds — which measures what a configuration calibrated
  on the four maps actually *delivers* on a large, diverse, unseen corpus.

Performance is reported as the **F1 score** (the balance of precision and recall — 1.0 is perfect, 0 is
useless; a detection counts as correct if it falls within a tolerance distance of a true mound) and,
alongside it, **tile-level MCC** (Matthews correlation coefficient — how well the model calls each map
tile "has a mound / is empty", regardless of exact placement). Comparisons use permutation tests with
multiple-comparison correction, which sort configurations into **statistical tiers**: "Tier 1" means
"cannot be told apart from the board leader by this instrument".

The pipeline that performs best has two ideas stacked on a single VLM:

1. **Consensus voting** — run the model *N* times and keep a detection only if enough passes agree.
2. **Proposer–verifier** — a first "proposer" pass proposes candidate mounds; an independent "verifier"
   pass re-examines a crop around each candidate and accepts or rejects it.

---

## 2. What influences performance — and what doesn't

**What does *not* matter** (a useful negative result — it means practitioners need not agonise over these):

- On a single pass, the preregistered prompt-engineering factors are statistically indistinguishable:
  **prompt elaboration, few-shot example ordering, negative-example wording, and example-library
  composition** all land inside one broad 20-configuration tie (F1 ≈ 0.58–0.63; §R2). Single-pass
  detection tops out around **F1 0.63** no matter how the prompt is tuned.
- **Deliberately engineered diversity** adds nothing: mixing prompts, modalities, and temperatures across
  the voting pool gives no gain over simply repeating one configuration (the H9 test; §R3).
- **A more expensive model does not help.** Neither Gemini Pro 3.1 nor Flash 3.5 wins any role; the cheap
  Flash verifier at minimal settings is as good as anything dearer on the GS maps (§R5).

**What does matter:**

- **Architecture, by far.** Consensus voting lifts the text pipeline from ~0.63 to ~0.69–0.77; adding the
  **proposer–verifier stage is the single biggest move in the study** and yields the headline result
  (§§R3–R4).
- **Modality (text vs image) — but as a *trade*, not a winner.** Text prompts localise more precisely
  (their accuracy plateaus at a ~30 m tolerance vs ~75 m for image prompts), so text wins on F1; image
  prompts are the **better tile-level detector** (best MCC). Which is "best" depends on whether you want
  coordinates or a present/absent screen (§§R1, R7).
- **Temperature** (the model's randomness dial): low temperature (T = 0) beats high (T = 0.7) on a single
  pass, but the difference washes out once consensus and a verifier are in place (§§R2, R5).
- **"Thinking level"** (how much internal reasoning the model does): inert — even mildly harmful — on a
  single pass, but the *source* of the consensus gain (the "diversity dividend": high-thinking passes
  disagree more, and disagreement is what voting exploits). Its value then changes again at deployment
  (§3).

The unifying mechanism: **the verifier shifts the binding constraint from precision to recall.** Once a
verifier prunes false positives, the only thing limiting F1 is whether the proposer pool *contains* the
mound at all — and cheap temperature-driven variety is the most economical way to widen that pool (§R5).

---

## 3. The cost–performance frontier — and the deployment twist

**On the gold-standard maps, cheap wins.** Pricing every configuration in dollars (audited batch rates)
and plotting cost against F1 gives a **Pareto frontier** — the set of configurations for which nothing is
both cheaper *and* better. Crucially, **all seven rungs are one statistical tier** on the GS maps (the
487-tile instrument cannot resolve differences below ~0.03 F1), so the cheapest efficient rung is the
rational choice (analysis `pass-budget-pareto-v2`; §R6):

| Configuration | F1@20 m (GS) | GS run cost | 55-map production cost | Frontier |
|---|---:|---:|---:|---|
| min6 — 5 minimal passes + verifier | 0.8784 | **$2.43** | ~$43 | efficient (cheapest) |
| min11 — 10 minimal passes + verifier | 0.8835 | $4.00 | ~$70 | efficient |
| high6 — 5 high-thinking + verifier | 0.8641 | $14.04 | ~$246 | dominated |
| high5+5vf — 5 high-thinking + 5-pass verifier | 0.8739 | $14.41 | ~$253 | dominated |
| high11 — 10 high-thinking + verifier | 0.8769 | $26.97 | ~$473 | dominated |
| high31 — **headline** (30 high-thinking, vote ≥ 16, + verifier) | **0.8902** | $69.21 | ~$1,214 | efficient |
| high35 — high31 + 5-pass verifier | 0.8951 | $71.23 | ~$1,249 | efficient |

The **headline result is F1 0.890 / MCC 0.790** on the GS maps. But read the table naively and it says
"buy minimal thinking; the whole high-thinking ladder is dominated" — and that conclusion **reverses at
deployment.**

**On the 55-map deployment set, the ranking flips.** The 8,541-tile instrument *can* resolve ~0.03 F1, and
it reveals that configurations which tied on the GS maps in fact degrade *unequally* when carried to unseen
maps (every configuration drops; the cheap minimal one drops most). The deployment board (canonical ground
truth, 50 m tolerance, eight configurations → five tiers; analysis `55map-canonical-leaderboard-50m`):

| Rank | Configuration | F1@50 m | Tier | Tile-MCC |
|---:|---|---:|---:|---:|
| 1 | text, high-thinking T0.3, vote 3-of-5 (*best achievable*) | 0.8476 | 1 | 0.690 |
| 2 | text, high-thinking T0.7, vote 3-of-5 | 0.8425 | 1 | 0.680 |
| 3 | text, high-thinking T0.3, vote 4-of-5 | 0.8359 | 2 | 0.671 |
| 4 | text, minimal, 10 passes, vote 5-of-10 ("buy-back") | 0.8290 | 2 | 0.672 |
| 5 | text, high-thinking T0.7, vote 4-of-5 (*as deployed*) | 0.8152 | 3 | 0.667 |
| 6 | text, minimal, vote 3-of-5 (the GS Pareto winner) | 0.8127 | 3 | 0.658 |
| 7 | **image**, vote 3-of-5 | 0.7987 | 4 | **0.710** |
| 8 | text, minimal, vote 4-of-5 | 0.7831 | 5 | 0.641 |

Three things this table shows that the GS Pareto frontier hides:

- **The cheap minimal configuration that is Pareto-optimal on the GS maps drops to Tier 3 at deployment**,
  two tiers below the high-thinking equivalent (0.8127 vs 0.8425). So *high thinking earns its cost on
  real maps* even though it looked wasteful on the test maps. The "take the cheaper option on a tie"
  rule is therefore **scope-qualified**: it holds only where the test instrument could actually have
  detected a difference that matters.
- **The gap is partly buyable without high thinking:** doubling the minimal pass count (the "buy-back" row)
  recovers about half of it (0.8290), turning the thinking-level decision into a priced trade — roughly
  **$58 for 0.829 vs $207 for 0.843** at deployment scale — rather than a tie.
- **The image pipeline is the best tile-level detector** (MCC 0.710, statistically the sole Tier-1 cell on
  that metric; analysis `55map-canonical-leaderboard-mcc-50m`) despite ranking 7th on F1. For a survey
  workflow that just needs "which map tiles deserve a look", a two-call image+verifier stack is the right
  — and cheapest — instrument, even though it is nowhere near the F1 frontier.

**Selecting a configuration with no ground truth.** Because real deployment corpora have no reference
data, we also validated a way to pick the best run *from the runs alone* — ranking configurations by how
well each agrees with a consensus of the others. It recovers the true ranking at a rank-correlation of
**ρ = +0.88** without any ground truth, with cost breaking the final tie (analysis
`gtfree-selection`; §R9).

---

## 4. Headline takeaways

1. **A general VLM, with the right scaffolding, reaches F1 ≈ 0.89 on curated maps and ≈ 0.85 on a large
   unseen corpus** for a niche cartographic symbol — competitive utility from an off-the-shelf model with
   no fine-tuning.
2. **Architecture beats prompt-tuning.** Consensus voting and an adversarial verifier deliver the gains;
   the preregistered prompt factors (elaboration, ordering, negative wording, library) do not separate.
3. **A bigger model doesn't help; a second cheap pass does.** Gemini Pro and Flash 3.5 win no role; the
   verifier and extra proposer passes are what move the needle.
4. **What is optimal on the test maps is not optimal on deployment.** The cheap minimal configuration is
   Pareto-efficient on the four GS maps but two tiers down on the 55-map set; high thinking earns its keep
   only where the instrument can resolve it. This calibrate-then-deploy gap is itself a central finding.
5. **Pick your metric for your use-case.** Text+verifier for coordinates (F1); image+verifier for a cheap
   present/absent tile screen (MCC). The modality "loser" on F1 is the winner for survey triage.

---

## 5. What we can and cannot claim — honest caveats

- **The GS maps cannot resolve fine differences.** With only ~487 tiles, configurations differing by less
  than ~0.03 F1 are statistically tied there; the deployment set's 8,541 tiles are what expose the real
  ordering. Read GS ties as "below this instrument's resolution", not "identical".
- **Recall is a measured upper bound.** Mounds that *every* configuration misses are invisible to a
  detection-led review, so reported recall is mildly optimistic (we carry a +3–5 % sensitivity band);
  precision, by contrast, survived a full human review of the deployment detections and is robust (§R8).
- **Everything is model-conditional.** Results hold for Gemini 3 Flash and this prompt family on this
  Soviet symbol convention; transfer to other map series or symbols is untested.
- **The no-ground-truth selector is a validated proposal, not a proven method** — a retrodiction on one
  corpus and eight configurations, awaiting a prospective test (§R9).

---

*All figures re-read at source on 2026-06-23 against the registered conditions/analyses manifests
(`results/analyses-manifest.md`) and the Results working draft. Full statistical detail, anchors, and the
preregistration linkage live in `docs/paper/results-draft.md` and the manifests.*
