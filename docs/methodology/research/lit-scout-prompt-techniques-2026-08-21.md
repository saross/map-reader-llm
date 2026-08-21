# Lit-scout draft: prompting and inference-time techniques for VLM/LLM detection pipelines (D.2, Seed 9)

⚠ **VERIFICATION PENDING** — this is a draft from the proposer
(lit-scout). The `/lit-scout` slash command runs the
`lit-scout-verifier` serial agent against this draft before
returning the final output. If you are reading this marker in
final output, verification failed — see the banner at top of the
document.

## TL;DR

The seven empirical findings map onto four mature literatures (sample-and-vote scaling,
in-context learning position bias, multimodal in-context learning mechanics, and
vision-language model (VLM) confidence calibration) and one fast-moving 2025 literature
that has only just caught up with finding 6 — extended reasoning degrading rather than
sharpening visual discrimination. The three must-reads are Bertini Baldassini et al.
(2024) `10.48550/arXiv.2404.15736`, which independently establishes that multimodal
in-context learning is text-driven with "little to no influence" from the image modality
(finding 1); Liu & Hu (2025) `10.48550/arXiv.2509.09958`, whose per-candidate binary
true/false verification is a near-exact architectural analogue of the propose→verify stage
(finding 5); and Liu et al. (2025) `10.48550/arXiv.2505.21523`, which documents longer
reasoning chains amplifying multimodal hallucination via attention drift away from visual
tokens (finding 6). The biggest gap: **finding 4 (example ordering null) has no supporting
literature and three strong contradicting works** — the in-context learning bias canon
(Lu et al., Zhao et al., UniBias) predicts large order effects, so the null needs an
explicit defence, most plausibly via the many-shot literature's observation that ordering
sensitivity attenuates as shot count rises.

**Two named candidates in the internal report do not survive resolution.** "VisRAG" is
vision-based retrieval-augmented generation over *document corpora*, not few-shot example
selection — the internal report's "20–40% gains from dynamic retrieval" claim is a
mis-transfer and should not be cited for example selection. And the RICES endorsement is
directly undercut by Bertini Baldassini et al., who find RICES no better than majority
voting over context examples.

## Findings table

| # | Fit | Cites | Authors (Year) | Title | DOI | Chain | Chains | Cluster | Status |
|---|-----|-------|----------------|-------|-----|-------|--------|---------|--------|
| 1 | HIGH | 1 | Bertini Baldassini et al. (2024) | What Makes Multimodal In-Context Learning Work? | 10.48550/arXiv.2404.15736 | seed (WebSearch) + cited-by #2 | 2 | Multimodal ICL mechanics | NEW |
| 2 | HIGH | 5 | Chen et al. (2023) | Can Multimodal Large Language Models Truly Perform Multimodal In-Context Learning? | 10.48550/arXiv.2311.18021 | seed (arXiv, resolves "MMICES") | 1 | Multimodal ICL mechanics | NEW |
| 3 | MEDIUM | 12 | Chen et al. (2025) | True Multimodal In-Context Learning Needs Attention to the Visual Context | 10.48550/arXiv.2507.15807 | refs-of #2 (same group) | 1 | Multimodal ICL mechanics | NEW |
| 4 | MEDIUM | 258 | Yang et al. (2022) | An Empirical Study of GPT-3 for Few-Shot Knowledge-Based VQA | 10.1609/aaai.v36i3.20215 | seed (WebSearch, resolves "RICES") | 1 | Multimodal ICL mechanics | NEW |
| 5 | HIGH | 711 | Wang et al. (2022) | Self-Consistency Improves Chain of Thought Reasoning in Language Models | 10.48550/arXiv.2203.11171 | seed (Zotero + OpenAlex) | 2 | Sample-and-vote scaling | [IN ZOTERO] |
| 6 | HIGH | 912 | Brown et al. (2024) | Large Language Monkeys: Scaling Inference Compute with Repeated Sampling | 10.48550/arXiv.2407.21787 | seed (arXiv) | 1 | Sample-and-vote scaling | NEW |
| 7 | HIGH | 21 | Li et al. (2024) | More Agents Is All You Need | 10.48550/arXiv.2402.05120 | seed (arXiv) | 1 | Sample-and-vote scaling | NEW |
| 8 | HIGH | 107 | Chen et al. (2024) | Are More LLM Calls All You Need? Towards Scaling Laws of Compound Inference Systems | 10.48550/arXiv.2403.02419 | seed (arXiv) | 1 | Sample-and-vote scaling | NEW |
| 9 | MEDIUM | 20 | Snell et al. (2024) | Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters | 10.48550/arXiv.2408.03314 | seed (arXiv) | 1 | Sample-and-vote scaling | NEW |
| 10 | MEDIUM | 1 | Taubenfeld et al. (2025) | Confidence Improves Self-Consistency in LLMs | 10.48550/arXiv.2502.06233 | seed (arXiv, "CISC") | 1 | Agreement-as-confidence | NEW |
| 11 | MEDIUM | 9 | Wan et al. (2025) | Reasoning Aware Self-Consistency: Leveraging Reasoning Paths for Efficient LLM Sampling | 10.18653/v1/2025.naacl-long.184 | seed (arXiv, resolves "RASC"); upgraded to published NAACL 2025 record | 1 | Sample-and-vote scaling | NEW |
| 12 | HIGH | 0 | Zhang et al. (2025) | Consensus Entropy: Harnessing Multi-VLM Agreement for Self-Verifying and Self-Improving OCR | 10.48550/arXiv.2504.11101 | seed (arXiv, resolves "Consensus Entropy") | 1 | Agreement-as-confidence | NEW |
| 13 | HIGH | 21 | Naik et al. (2023) | Diversity of Thought Improves Reasoning Abilities of Large Language Models | 10.48550/arXiv.2310.07088 | seed (arXiv) | 2 | Ensemble diversity theory | NEW |
| 14 | MEDIUM | 0 | Kim (2026) | Are Diversity Metrics Measuring Diversity? A Capability-Controlled Audit of Majority-Vote Gain in LLM Ensembles | 10.48550/arXiv.2607.20768 | seed (WebSearch) | 1 | Ensemble diversity theory | NEW |
| 15 | HIGH | 358 | Lu et al. (2022) | Fantastically Ordered Prompts and Where to Find Them: Overcoming Few-Shot Prompt Order Sensitivity | 10.18653/v1/2022.acl-long.556 | seed (CrossRef) | 2 | ICL position/order bias | NEW |
| 16 | HIGH | 72 | Zhao et al. (2021) | Calibrate Before Use: Improving Few-Shot Performance of Language Models | 10.48550/arXiv.2102.09690 | seed (arXiv) | 1 | ICL position/order bias | NEW |
| 17 | MEDIUM | 1 | Zhou et al. (2024) | UniBias: Unveiling and Mitigating LLM Bias through Internal Attention and FFN Manipulation | 10.48550/arXiv.2405.20612 | seed (arXiv, resolves "UniBias") | 1 | ICL position/order bias | NEW |
| 18 | MEDIUM | 262 | Agarwal et al. (2024) | Many-Shot In-Context Learning | 10.48550/arXiv.2404.11018 | seed (arXiv, resolves NeurIPS 2024 spotlight) | 1 | ICL position/order bias | NEW |
| 19 | HIGH | 68 | Jiang et al. (2024) | Many-Shot In-Context Learning in Multimodal Foundation Models | 10.48550/arXiv.2405.09798 | seed (arXiv) | 2 | ICL position/order bias | NEW |
| 20 | HIGH | 0 | Liu & Hu (2025) | Zero-Shot Referring Expression Comprehension via Visual-Language True/False Verification | 10.48550/arXiv.2509.09958 | seed (WebSearch) | 1 | Propose→verify architectures | NEW |
| 21 | HIGH | 38 | Huang et al. (2023) | Large Language Models Cannot Self-Correct Reasoning Yet | 10.48550/arXiv.2310.01798 | seed (arXiv + Zotero) | 2 | Propose→verify architectures | [IN ZOTERO] |
| 22 | MEDIUM | 1 | Wu & Xie (2023) | V*: Guided Visual Search as a Core Mechanism in Multimodal LLMs | 10.48550/arXiv.2312.14135 | seed (arXiv) | 1 | Propose→verify architectures | NEW |
| 23 | HIGH | 0 | Liu et al. (2025) | More Thinking, Less Seeing? Assessing Amplified Hallucination in Multimodal Reasoning Models | 10.48550/arXiv.2505.21523 | seed (arXiv + WebSearch) | 2 | Reasoning budget vs perception | NEW |
| 24 | HIGH | 26 | Tian et al. (2025) | More Thought, Less Accuracy? On the Dual Nature of Reasoning in Vision-Language Models | 10.48550/arXiv.2509.25848 | seed (WebSearch) | 1 | Reasoning budget vs perception | NEW |
| 25 | MEDIUM | 1 | Li et al. (2025) | Unleashing Perception-Time Scaling to Multimodal Reasoning Models | 10.48550/arXiv.2510.08964 | seed (WebSearch) | 1 | Reasoning budget vs perception | NEW |
| 26 | HIGH | 13 | Groot & Valdenegro-Toro (2024) | Overconfidence is Key: Verbalized Uncertainty Evaluation in Large Language and Vision-Language Models | 10.18653/v1/2024.trustnlp-1.13 | seed (CrossRef) | 1 | VLM confidence calibration | NEW |
| 27 | HIGH | 4 | Xuan et al. (2025) | Seeing is Believing, but How Much? A Comprehensive Analysis of Verbalized Calibration in Vision-Language Models | 10.18653/v1/2025.emnlp-main.74 | seed (CrossRef) | 1 | VLM confidence calibration | NEW |
| 28 | MEDIUM | 5 | Tian et al. (2023) | Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback | 10.48550/arXiv.2305.14975 | seed (arXiv) | 1 | VLM confidence calibration | NEW |
| 29 | LOW | 6 | Yu et al. (2024) | VisRAG: Vision-based Retrieval-augmented Generation on Multi-modality Documents | 10.48550/arXiv.2410.10594 | seed (arXiv, resolves "VisRAG") | 1 | Visual retrieval-augmentation | NEW |

## Proposer self-check

Three rows were re-queried at random with a fresh `lit-search.py metadata` call after the
table was compiled: **row 15** (`10.18653/v1/2022.acl-long.556`) returned `authors[0]="Lu,
Yao"`, 5 authors, year 2022, 358 cites — matches, and 5 authors licenses "et al."; **row
19** (`10.48550/arXiv.2405.09798`) returned `authors[0]="Yixing Jiang"`, 6 authors, year
2024, 68 cites — matches, "et al." licensed; **row 26**
(`10.18653/v1/2024.trustnlp-1.13`) returned `authors[0]="Groot, Tobias"`, **2 authors**,
year 2024, 13 cites — matches, and the two-author count correctly renders as "Groot &
Valdenegro-Toro" rather than "et al." No mismatches; no rebuild required.

**Anomalies pre-flagged for the verifier** (these are real metadata artefacts, not
proposer errors):

1. **Row 14 author-name encoding.** OpenAlex returns the author of
   `10.48550/arXiv.2607.20768` in Hangul as `김동환`; the arXiv API returns the Latin
   transliteration `Donghwan Kim`. Both denote the same person and the same surname
   (김 = Kim). Rendered as bare `Kim (2026)` per the single-author rule. A verifier
   re-running `metadata` will see the Hangul form — this is a script-encoding difference,
   not a misattribution.
2. **Row 29 first-author name order.** OpenAlex returns `Yu Shi`; arXiv returns `Shi Yu`.
   The surname is *Yu* (the arXiv form is the author's self-declared order), so the
   rendering is `Yu et al. (2024)`. OpenAlex has reversed given/family here.
3. **Citation counts on arXiv rows are systematic undercounts.** OpenAlex splits preprint
   and published records, so several rows carry implausibly low counts for their actual
   influence — most conspicuously row 1 (Bertini Baldassini et al., 1 cite, but a CVPR
   Workshops 2024 paper), row 22 (Wu & Xie, `V*`, 1 cite, but a CVPR 2024 paper with
   wide uptake), and row 17 (UniBias, 1 cite, a NeurIPS 2024 paper). Semantic Scholar
   would give better numbers but returned HTTP 429 persistently from this host across two
   attempts (a slow-paced background retry also failed). **The values in the Cites column
   are exactly what `lit-search.py metadata` returns today**, which is the reproducible
   and verifier-checkable figure — but they should not be read as impact measures in the
   paper. Where a published-venue DOI exists it would give a truer count; resolving those
   is the top deferred task.
4. **Two titles differ between arXiv and the metadata chain.** Row 20's arXiv v3 title
   contains a typo ("Vison-Language"); the metadata chain returns the corrected
   "Visual-Language", which is what the table uses. Row 13's arXiv title reads
   "...Abilities of LLMs" while the metadata chain returns the expanded "...Abilities of
   Large Language Models"; the table uses the metadata form.
5. **Row 11 was upgraded mid-sweep to its published record.** A slow-paced Semantic
   Scholar retry that completed late in the sweep revealed that RASC has been published at
   NAACL 2025 under `10.18653/v1/2025.naacl-long.184`. That DOI was independently
   re-verified with a fresh `lit-search.py metadata` call (CrossRef source: 4 authors,
   year 2025, 9 cites) and now replaces the arXiv preprint form in row 11 and in the claims
   block. The published record is preferable on three counts — archival venue, CrossRef
   indexing (so `lit-search.py bibtex` will accept it), and a truer citation count.
6. **The same late retry corroborated the undercount diagnosis in item 3.** Semantic
   Scholar reports 43 citations for row 17 (UniBias) against OpenAlex's 1, and confirms the
   venue as NeurIPS. It also reports 10 authors for row 12 (Consensus Entropy) where both
   arXiv and OpenAlex report 8 — immaterial to rendering, since all three counts are ≥3 and
   yield "Zhang et al.", but worth knowing if the author list is ever quoted in full.
7. **Row 18 author count differs by source.** arXiv lists 15 authors, the metadata chain
   14 (omitting Luis Rosias). Immaterial to rendering — both are ≥3, so "et al." holds.

**Injection watch:** no prompt-injection attempts were observed in any WebSearch result,
fetched page, or API payload during this sweep. All retrieved content was treated as data.

**Tooling note.** The Scholar Gateway MCP tool
(`mcp__claude_ai_Scholar_Gateway__semanticSearch`) and the Hugging Face MCP tools were
**not available** in this session ("No such tool available"), so the prescribed semantic
seed phase could not run. Compensation: seeds were drawn from arXiv full-text/title search
(via `urllib` — `curl` to `export.arxiv.org` is blocked in this sandbox while `urllib`
succeeds), CrossRef/OpenAlex via `lit-search.py search`, and three WebSearch passes. The
practical consequence is that this sweep has *no* Wiley/Hindawi bias to correct, but it is
correspondingly weighted toward arXiv/ACL-Anthology venues — appropriate for this
literature, which is overwhelmingly preprint-first, but it means any relevant work in
remote-sensing or cartography journals may be under-sampled. See Gaps.

## Landscape

The literature relevant to D.2 divides into two populations with very different maturities.

**The mature half is text-only and pre-dates VLM detection work.** Self-consistency (row
5), prompt order sensitivity (row 15), and ICL calibration bias (row 16) are all
2021–2022 text-classification and reasoning results with hundreds of citations. They
supply the vocabulary the paper will use — "sample-and-vote", "recency bias", "majority
label bias" — but every one of them was established on tasks where the answer is a short
string, not a set of spatial detections. This matters for findings 2 and 4: the paper is
importing a framework whose empirical base is one modality and one output type away from
its own. That is defensible, and it is also precisely where our contradicting result
(finding 4's null) becomes interesting rather than embarrassing.

**The immature half is multimodal and almost entirely 2024–2025.** The strongest analogues
for findings 1, 5, 6, and 7 are all preprints from the last twenty-four months, several
with near-zero citation counts. Consensus Entropy (row 12) applies multi-VLM agreement to
optical character recognition; Liu & Hu (row 20) apply per-candidate binary verification to
referring-expression comprehension; the "More Thinking, Less Seeing" / "More Thought, Less
Accuracy" pair (rows 23–24) document reasoning-budget harm to perception. None of these
concerns archaeological symbol detection or historical maps, but structurally they are
doing the same thing this paper is doing, and they are converging on the same conclusions
independently. The Discussion can therefore make a genuinely strong claim: the run
configuration reported here is not an idiosyncratic local optimum but an instance of a
pattern being found simultaneously across OCR, referring expressions, and visual question
answering.

The most important asymmetry for the paper's rhetoric: **findings 1, 2, 5, 6, and 7 are
each corroborated by independent published work, while findings 3 and 4 sit against the
grain.** Those two should get the more careful and more extended literature engagement,
because they are where the paper is saying something the literature does not already
predict.

## Per-finding mapping

### Finding 1 — text specification beats few-shot image examples

| Work | Direction | What it licenses the paper to say |
|---|---|---|
| Bertini Baldassini et al. (2024), row 1 | **Predicts** | The load-bearing citation. Establishes that multimodal ICL "primarily relies on text-driven mechanisms, showing little to no influence from the image modality" across IDEFICS and OpenFlamingo. Also finds advanced example selection (RICES) no better than simple majority voting over context examples — a second, independent hit. |
| Chen et al. (2023), row 2 | **Predicts** | The actual source of the internal report's "textual information plays a more significant role than visual" claim (this is the MMICES paper; MMICES is its proposed *method*, not its finding). Verified: the claim is real and correctly attributed. |
| Chen et al. (2025), row 3 | **Complicates** | Same research group, two years on: argues the text-dominance is a *deficiency* to be repaired (models under-attend the visual context), not a property to exploit. The paper should cite this to avoid appearing to endorse text-dominance as desirable — our result is "text spec works better *given current models*", not "images are useless in principle". |
| Yang et al. (2022), row 4 | **Context** | Origin of RICES. Cite only if the paper discusses retrieval-based example selection as a road not taken. |

Suggested framing: *consistent with* Bertini Baldassini et al. and Chen et al., with
Chen et al. (2025) as the forward-looking caveat.

### Finding 2 — consensus voting; permissive-to-mid thresholds beat unanimity

| Work | Direction | What it licenses |
|---|---|---|
| Wang et al. (2022), row 5 | **Predicts** | Canonical anchor for sample-and-vote. Already in Zotero. |
| Brown et al. (2024), row 6 | **Predicts** | Coverage rises log-linearly with sample count — the scaling-law grounding for "large gains from k-of-N". |
| Li et al. (2024), row 7 | **Predicts** | Sampling-and-voting gains scale with ensemble size and are largest on harder tasks. |
| Chen et al. (2024), row 8 | **Predicts (specifically the threshold shape)** | The best citation for *permissive-beats-unanimous*: shows performance in compound inference systems is **non-monotone** in the number of calls, rising then falling. Strict unanimity is the high-call-count regime where the curve turns down. |
| Taubenfeld et al. (2025), row 10 | **Predicts** | Confidence-weighted voting beats plain self-consistency at equal or lower sample budget — supports the paper's use of recorded acceptance probabilities rather than hard votes. |
| Wan et al. (2025), row 11 | **Adjacent** | RASC: early-stopping when agreement is high, ~80% sample reduction. Cost-efficiency angle, not an accuracy claim. |
| Zhang et al. (2025), row 12 | **Predicts, and in vision** | Correct VLM predictions converge in output space while errors diverge. The closest *visual*-task analogue to the k-of-N result. |
| Snell et al. (2024), row 9 | **Context** | Test-time compute allocation framing; cite if the paper positions voting as a compute-allocation choice. |

### Finding 3 — temperature/reasoning-budget diversity useful, prompt-variant diversity not

| Work | Direction | What it licenses |
|---|---|---|
| Naik et al. (2023), row 13 | **Contradicts** | Explicitly claims approach-level prompt diversity ("diversity of thought") improves over vanilla self-consistency. Our parametric-diversity null runs against this. The honest engagement is a one-sentence "contra Naik et al., prompt-variant diversity produced correlated errors in our setting" — with the modality difference (spatial detection vs reasoning benchmarks) as the proposed reconciliation. |
| Kim (2026), row 14 | **Supports** | Capability-controlled audit finding that diversity metrics weakly and inconsistently predict majority-vote gain. Useful cover for the null, though it is a single-author 2026 preprint with no citations — cite as corroboration, not as authority. |

This is the thinnest of the seven. See Gaps.

### Finding 4 — example ordering had no effect (H4 null)

| Work | Direction | What it licenses |
|---|---|---|
| Lu et al. (2022), row 15 | **Contradicts** | The canonical order-sensitivity result: accuracy swings from near-chance to state-of-the-art on permutation alone. 358 citations. Must be addressed. |
| Zhao et al. (2021), row 16 | **Contradicts** | Majority-label, recency, and common-token bias in few-shot prompts; the origin of the "recency bias" framing in the internal report. |
| Zhou et al. (2024), row 17 | **Contradicts (mechanistically)** | UniBias — resolved and real. Identifies biased attention heads and feed-forward vectors driving ICL bias. Note: it is a *mitigation* method paper, so the internal report's "reduced bias by 17%" figure should be re-checked against the paper before quoting. |
| Agarwal et al. (2024), row 18 | **Explains the null** | The reconciliation candidate. Many-shot ICL shows the sensitivity to individual demonstration choice and arrangement attenuates as shot count rises — a many-shot regime can wash out ordering effects that dominate in the 4–8-shot regime where Lu et al. and Zhao et al. worked. |
| Jiang et al. (2024), row 19 | **Explains the null, in the right modality** | Multimodal many-shot ICL on Gemini 1.5 Pro and GPT-4o specifically — the closest model family to ours. Best single citation for "our shot count sits in a regime where ordering no longer bites". |

Recommended two-sentence treatment: acknowledge Lu et al. and Zhao et al., then attribute
the null to regime (many-shot, multimodal, spatial output) via Jiang et al. This turns a
bare null into a positive claim about where order effects live.

### Finding 5 — propose→verify is the largest structural gain; coarse-to-fine cropping failed

| Work | Direction | What it licenses |
|---|---|---|
| Liu & Hu (2025), row 20 | **Predicts, near-exactly** | Decomposes referring-expression comprehension into per-candidate binary true/false verification; reports that isolating a single highlighted region "reduces cross-box interference" and concentrates reasoning, especially when the proposer emits many candidates. This is the same mechanism the project attributed to its adversarial verifier. Strongest single citation for finding 5. |
| Huang et al. (2023), row 21 | **Sharpens the claim** | LLMs cannot reliably self-correct without external feedback. Supports the reading that the gain comes from *architectural separation* — an independent verifier call with a fresh context — not from self-critique. Already in Zotero. |
| Wu & Xie (2023), row 22 | **Contradicts the cropping failure** | `V*` shows guided visual search with iterative cropping *does* work for small targets in high-resolution images. The paper should not claim coarse-to-fine fails in general; the honest claim is that it failed *here*, and `V*` suggests why — `V*` crops under LLM guidance toward a specific queried target, whereas an unguided coarse-to-fine sweep discards the surrounding cartographic context that disambiguates mound symbols. |

### Finding 6 — extended reasoning liberalises acceptance

| Work | Direction | What it licenses |
|---|---|---|
| Liu et al. (2025), row 23 | **Predicts** | Longer reasoning chains amplify multimodal hallucination; attention drifts from visual tokens toward the language prior as the chain extends. This is a mechanistic account of exactly the observed liberalisation — the verifier stops looking at the tile and starts reasoning from its prior. |
| Tian et al. (2025), row 24 | **Predicts** | The "dual nature" framing: reasoning helps some VLM tasks while degrading others. Useful for stating the effect is a known trade-off rather than a project-specific artefact. |
| Li et al. (2025), row 25 | **Predicts, plus remedy** | Argues test-time scaling should be directed at *perception* rather than reasoning in multimodal models. Cite if the Discussion gestures at what would have worked instead. |

This is the best-supported of the seven findings and the one where the paper's independent
replication in a new domain (historical-map symbol detection) has the most external value.

### Finding 7 — VLM confidence calibration supports downstream thresholding

| Work | Direction | What it licenses |
|---|---|---|
| Groot & Valdenegro-Toro (2024), row 26 | **Cautions** | VLMs are markedly overconfident in verbalised uncertainty. The paper should not claim its acceptance probabilities are *calibrated* — only that they are *monotone enough to threshold on*, which is a weaker and defensible claim. |
| Xuan et al. (2025), row 27 | **Cautions, comprehensively** | Systematic analysis of verbalised calibration across VLMs. The current best single reference for the state of the art. |
| Tian et al. (2023), row 28 | **Supports the method** | Verbalised confidence outperforms model-internal conditional probabilities for RLHF-tuned models — justifies eliciting probabilities from the model rather than reading logits. |

Note the productive tension with finding 2: rows 26–27 say verbalised confidence is poorly
calibrated, while row 12 (Consensus Entropy) says *agreement across passes* is a better
uncertainty signal than any single verbalised number. Since the pipeline has both, the
Discussion can note that the consensus signal and the verbalised probability are
complementary — which is a small original contribution rather than just a citation.

## Thematic clusters

| Cluster | Members | Rows | Reading |
|---|---|---|---|
| Multimodal ICL mechanics | 4 | 1–4 | Dense and convergent. Text dominance is a replicated finding, not a one-off. |
| Sample-and-vote scaling | 6 | 5–9, 11 | The densest cluster and the most canonical. Findings 2 is on very safe ground. |
| Agreement-as-confidence | 2 | 10, 12 | Small but the bridge between findings 2 and 7. |
| Ensemble diversity theory | 2 | 13–14 | Sparse and internally split — mirrors the field's unsettled state on finding 3. |
| ICL position/order bias | 5 | 15–19 | Dense, but split between the order-sensitivity canon (15–17) and the many-shot attenuation account (18–19). The split *is* the argument for finding 4. |
| Propose→verify architectures | 3 | 20–22 | Structurally central despite low counts; row 20 is the key analogue and row 22 the key counter-case. |
| Reasoning budget vs perception | 3 | 23–25 | Tight, recent, unanimous. Best support of any finding. |
| VLM confidence calibration | 3 | 26–28 | Coherent; all three caution against over-claiming calibration. |
| Visual retrieval-augmentation | 1 | 29 | Topical outlier — resolved to correct the internal report, not to cite. |

## Suggested reading (tiered)

**Tier 1 — read before drafting D.2 (5 papers).** Rows 1, 20, 23, 8, 19. These are the
papers that change what the subsection can claim: text dominance in multimodal ICL, the
per-candidate verification analogue, the reasoning-degrades-perception mechanism, the
non-monotone voting curve that explains why permissive thresholds win, and the multimodal
many-shot result that rescues the H4 null.

**Tier 2 — read to write specific sentences (7 papers).** Rows 2, 5, 12, 15, 21, 24, 26.
Canonical anchors and the primary contradiction (Lu et al.) that must be engaged.

**Tier 3 — cite without deep reading (9 papers).** Rows 3, 6, 7, 10, 16, 17, 18, 25, 27.
Supporting and contextual.

**Tier 4 — resolved for correction, probably not cited (4 papers).** Rows 4, 9, 11, 14,
plus row 29. Row 29 (VisRAG) in particular exists in this table to document that the
internal report's retrieval claim does not transfer.

## Gaps noticed

1. **Finding 3 is under-supported and the sole direct contradiction (Naik et al.) is
   unrebutted.** There is no published work I could find testing prompt-variant versus
   temperature-variant diversity as *competing* sources of ensemble diversity in a
   detection task. Targeted searches for "prompt variations AND self-consistency AND
   diversity" and "prompt AND ensemble AND correlated errors" on arXiv returned nothing
   relevant. This may be a genuinely novel contribution of the paper — worth flagging as
   such rather than as a gap in the search.
2. **Finding 4 has no supporting citation, only an explanation.** The many-shot
   attenuation account (rows 18–19) is inferential: neither paper directly tests ordering
   effects as a function of shot count in a detection setting. If the paper wants to state
   the reconciliation as fact rather than conjecture, that ordering-by-shot-count
   interaction would need its own targeted search or an internal ablation.
3. **No archaeological, remote-sensing, or cartographic venue appears anywhere in this
   table.** Every row is a machine-learning venue. This is partly correct (the techniques
   are ML techniques) but means the paper is the bridge, and there may be domain-side work
   on inference-time technique in remote sensing that this sweep's arXiv/ACL-weighted
   seeding missed. The unavailability of Scholar Gateway (see self-check) makes this more
   likely than usual.
4. **Published-venue DOIs are unresolved for the arXiv rows.** Several rows are known
   conference papers (row 1 CVPR-W 2024, row 17 NeurIPS 2024, row 18 NeurIPS 2024, row 22
   CVPR 2024) whose published DOIs would give both a citable venue and a realistic citation
   count. Resolving these is a mechanical follow-up worth doing before the bibliography is
   finalised.
5. **Finding 5's coarse-to-fine failure has one counter-case (V*) and no supporting
   case.** I found no published report of a coarse-to-fine VLM cropping pipeline
   *failing*. Negative results are under-published here, so absence of evidence is weak,
   but the paper should phrase the cropping failure as a local observation rather than a
   general finding.
6. **Two internal-report figures remain unverified against their sources**: the "17% bias
   reduction" attributed to UniBias, and the "1.2–1.5 point drop" from removing images
   from demonstrations attributed to MMICES. Both papers are now correctly identified
   (rows 17 and 2), but I verified only their *existence and general claims*, not these
   specific numbers. Do not quote either figure without opening the paper — the internal
   report has already proven unreliable on VisRAG and RICES.

## Venue analysis

No target venues were named for this task, so this section is not applicable. One
observation worth carrying forward: of the 29 rows, 25 are arXiv-primary and 4 are
ACL-Anthology or AAAI. If the target journal expects archival citations, rows 1, 17, 18,
and 22 should be re-cited to their conference proceedings (see Gaps item 4).

## Zotero actions

Two rows are already held: **row 5** (Wang et al., self-consistency) as key `2TD9BNU8` and
**row 21** (Huang et al., self-correction) as key `HM9B3Q9G`, both in the
`2025-MQ-LLM-DH-software-longevity` library rather than a map-reader collection. Worth
noting they will need adding to this project's collection even though no new item is
required.

**27 rows are NEW.** Recommended import priority, matching the reading tiers: rows 1, 8,
19, 20, 23 first (Tier 1 minus the already-held); then rows 2, 12, 15, 24, 26; then the
remainder. Rows 4, 9, 11, 14, and 29 can be imported or skipped at the user's discretion —
they are resolution artefacts more than reading targets.

All 29 rows carry DOIs, so the staging importer's DOI-based deduplication will handle the
two existing items automatically. Note that `lit-search.py bibtex` declines `10.48550`
DOIs, so the 25 arXiv rows will need the DataCite path or arXiv-ID import rather than a
BibTeX export.

## Deeper chaining candidates

Forward and backward chaining was shallow in this sweep because OpenAlex `cited-by`
coverage for 2024–2025 arXiv preprints is very sparse (the cited-by call on row 2 returned
5 items; on row 1, a single item), and Semantic Scholar — which has far better preprint
citation graphs — returned HTTP 429 throughout. The following are worth chasing if the
user approves and if Semantic Scholar access can be restored:

```text
DEEPER CHAINING CANDIDATES (go/no-go required):
1. FORWARD L2: Chase citations of Liu & Hu (2025), row 20, arXiv 2509.09958 — the
   closest architectural analogue to the propose→verify result and only 11 months old.
   Its citing set is the most likely place to find other per-candidate verification
   pipelines, which is where finding 5's strongest support would live.
2. FORWARD L2: Chase citations of Liu et al. (2025), row 23, arXiv 2505.21523 — the
   reasoning-degrades-perception literature is moving fast and this paper is its hub;
   a forward chain would likely surface the 2026 layer that this sweep did not reach.
3. BACKWARD L3: Chase references of Bertini Baldassini et al. (2024), row 1 — the only
   paper systematically ablating text versus image in multimodal demonstrations; its
   reference list is the best route to any earlier text-dominance evidence.
4. TARGETED: Re-resolve published-venue DOIs for rows 1, 17, 18, 22 (CVPR-W 2024,
   NeurIPS 2024, NeurIPS 2024, CVPR 2024) to obtain realistic citation counts.
5. SKIP: Wang et al. (2022), row 5 — 711+ citations, forward chain would explode and
   return general reasoning work with no bearing on detection pipelines.
6. SKIP: Yu et al. (2024), row 29 (VisRAG) — resolved and shown not to transfer;
   chaining would lead into document-retrieval literature outside scope.
```

## Machine-readable claims (for orchestrator extraction)

<!-- BEGIN claims.jsonl -->
```jsonl
{"claim_id":"10.48550-arxiv.2404.15736-authors","doi":"10.48550/arXiv.2404.15736","category":"authors","description":"Authors for row 1","value":"Bertini Baldassini et al. (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 1"}
{"claim_id":"10.48550-arxiv.2404.15736-year","doi":"10.48550/arXiv.2404.15736","category":"year","description":"Publication year for row 1","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 1"}
{"claim_id":"10.48550-arxiv.2404.15736-title","doi":"10.48550/arXiv.2404.15736","category":"title","description":"Title for row 1","value":"What Makes Multimodal In-Context Learning Work?","source_method":"lit-search.py metadata","source_file":"Findings table row 1"}
{"claim_id":"10.48550-arxiv.2404.15736-citation_count","doi":"10.48550/arXiv.2404.15736","category":"citation_count","description":"Citation count for row 1","value":1,"source_method":"lit-search.py metadata","source_file":"Findings table row 1"}
{"claim_id":"10.48550-arxiv.2404.15736-doi_resolves","doi":"10.48550/arXiv.2404.15736","category":"doi_resolves","description":"DOI resolves to expected paper for row 1","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 1"}
{"claim_id":"10.48550-arxiv.2311.18021-authors","doi":"10.48550/arXiv.2311.18021","category":"authors","description":"Authors for row 2","value":"Chen et al. (2023)","source_method":"lit-search.py metadata","source_file":"Findings table row 2"}
{"claim_id":"10.48550-arxiv.2311.18021-year","doi":"10.48550/arXiv.2311.18021","category":"year","description":"Publication year for row 2","value":2023,"source_method":"lit-search.py metadata","source_file":"Findings table row 2"}
{"claim_id":"10.48550-arxiv.2311.18021-title","doi":"10.48550/arXiv.2311.18021","category":"title","description":"Title for row 2","value":"Can Multimodal Large Language Models Truly Perform Multimodal In-Context Learning?","source_method":"lit-search.py metadata","source_file":"Findings table row 2"}
{"claim_id":"10.48550-arxiv.2311.18021-citation_count","doi":"10.48550/arXiv.2311.18021","category":"citation_count","description":"Citation count for row 2","value":5,"source_method":"lit-search.py metadata","source_file":"Findings table row 2"}
{"claim_id":"10.48550-arxiv.2311.18021-doi_resolves","doi":"10.48550/arXiv.2311.18021","category":"doi_resolves","description":"DOI resolves to expected paper for row 2","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 2"}
{"claim_id":"10.48550-arxiv.2507.15807-authors","doi":"10.48550/arXiv.2507.15807","category":"authors","description":"Authors for row 3","value":"Chen et al. (2025)","source_method":"lit-search.py metadata","source_file":"Findings table row 3"}
{"claim_id":"10.48550-arxiv.2507.15807-year","doi":"10.48550/arXiv.2507.15807","category":"year","description":"Publication year for row 3","value":2025,"source_method":"lit-search.py metadata","source_file":"Findings table row 3"}
{"claim_id":"10.48550-arxiv.2507.15807-title","doi":"10.48550/arXiv.2507.15807","category":"title","description":"Title for row 3","value":"True Multimodal In-Context Learning Needs Attention to the Visual Context","source_method":"lit-search.py metadata","source_file":"Findings table row 3"}
{"claim_id":"10.48550-arxiv.2507.15807-citation_count","doi":"10.48550/arXiv.2507.15807","category":"citation_count","description":"Citation count for row 3","value":12,"source_method":"lit-search.py metadata","source_file":"Findings table row 3"}
{"claim_id":"10.48550-arxiv.2507.15807-doi_resolves","doi":"10.48550/arXiv.2507.15807","category":"doi_resolves","description":"DOI resolves to expected paper for row 3","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 3"}
{"claim_id":"10.1609-aaai.v36i3.20215-authors","doi":"10.1609/aaai.v36i3.20215","category":"authors","description":"Authors for row 4","value":"Yang et al. (2022)","source_method":"lit-search.py metadata","source_file":"Findings table row 4"}
{"claim_id":"10.1609-aaai.v36i3.20215-year","doi":"10.1609/aaai.v36i3.20215","category":"year","description":"Publication year for row 4","value":2022,"source_method":"lit-search.py metadata","source_file":"Findings table row 4"}
{"claim_id":"10.1609-aaai.v36i3.20215-title","doi":"10.1609/aaai.v36i3.20215","category":"title","description":"Title for row 4","value":"An Empirical Study of GPT-3 for Few-Shot Knowledge-Based VQA","source_method":"lit-search.py metadata","source_file":"Findings table row 4"}
{"claim_id":"10.1609-aaai.v36i3.20215-citation_count","doi":"10.1609/aaai.v36i3.20215","category":"citation_count","description":"Citation count for row 4","value":258,"source_method":"lit-search.py metadata","source_file":"Findings table row 4"}
{"claim_id":"10.1609-aaai.v36i3.20215-doi_resolves","doi":"10.1609/aaai.v36i3.20215","category":"doi_resolves","description":"DOI resolves to expected paper for row 4","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 4"}
{"claim_id":"10.48550-arxiv.2203.11171-authors","doi":"10.48550/arXiv.2203.11171","category":"authors","description":"Authors for row 5","value":"Wang et al. (2022)","source_method":"lit-search.py metadata","source_file":"Findings table row 5"}
{"claim_id":"10.48550-arxiv.2203.11171-year","doi":"10.48550/arXiv.2203.11171","category":"year","description":"Publication year for row 5","value":2022,"source_method":"lit-search.py metadata","source_file":"Findings table row 5"}
{"claim_id":"10.48550-arxiv.2203.11171-title","doi":"10.48550/arXiv.2203.11171","category":"title","description":"Title for row 5","value":"Self-Consistency Improves Chain of Thought Reasoning in Language Models","source_method":"lit-search.py metadata","source_file":"Findings table row 5"}
{"claim_id":"10.48550-arxiv.2203.11171-citation_count","doi":"10.48550/arXiv.2203.11171","category":"citation_count","description":"Citation count for row 5","value":711,"source_method":"lit-search.py metadata","source_file":"Findings table row 5"}
{"claim_id":"10.48550-arxiv.2203.11171-doi_resolves","doi":"10.48550/arXiv.2203.11171","category":"doi_resolves","description":"DOI resolves to expected paper for row 5","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 5"}
{"claim_id":"10.48550-arxiv.2407.21787-authors","doi":"10.48550/arXiv.2407.21787","category":"authors","description":"Authors for row 6","value":"Brown et al. (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 6"}
{"claim_id":"10.48550-arxiv.2407.21787-year","doi":"10.48550/arXiv.2407.21787","category":"year","description":"Publication year for row 6","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 6"}
{"claim_id":"10.48550-arxiv.2407.21787-title","doi":"10.48550/arXiv.2407.21787","category":"title","description":"Title for row 6","value":"Large Language Monkeys: Scaling Inference Compute with Repeated Sampling","source_method":"lit-search.py metadata","source_file":"Findings table row 6"}
{"claim_id":"10.48550-arxiv.2407.21787-citation_count","doi":"10.48550/arXiv.2407.21787","category":"citation_count","description":"Citation count for row 6","value":912,"source_method":"lit-search.py metadata","source_file":"Findings table row 6"}
{"claim_id":"10.48550-arxiv.2407.21787-doi_resolves","doi":"10.48550/arXiv.2407.21787","category":"doi_resolves","description":"DOI resolves to expected paper for row 6","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 6"}
{"claim_id":"10.48550-arxiv.2402.05120-authors","doi":"10.48550/arXiv.2402.05120","category":"authors","description":"Authors for row 7","value":"Li et al. (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 7"}
{"claim_id":"10.48550-arxiv.2402.05120-year","doi":"10.48550/arXiv.2402.05120","category":"year","description":"Publication year for row 7","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 7"}
{"claim_id":"10.48550-arxiv.2402.05120-title","doi":"10.48550/arXiv.2402.05120","category":"title","description":"Title for row 7","value":"More Agents Is All You Need","source_method":"lit-search.py metadata","source_file":"Findings table row 7"}
{"claim_id":"10.48550-arxiv.2402.05120-citation_count","doi":"10.48550/arXiv.2402.05120","category":"citation_count","description":"Citation count for row 7","value":21,"source_method":"lit-search.py metadata","source_file":"Findings table row 7"}
{"claim_id":"10.48550-arxiv.2402.05120-doi_resolves","doi":"10.48550/arXiv.2402.05120","category":"doi_resolves","description":"DOI resolves to expected paper for row 7","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 7"}
{"claim_id":"10.48550-arxiv.2403.02419-authors","doi":"10.48550/arXiv.2403.02419","category":"authors","description":"Authors for row 8","value":"Chen et al. (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 8"}
{"claim_id":"10.48550-arxiv.2403.02419-year","doi":"10.48550/arXiv.2403.02419","category":"year","description":"Publication year for row 8","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 8"}
{"claim_id":"10.48550-arxiv.2403.02419-title","doi":"10.48550/arXiv.2403.02419","category":"title","description":"Title for row 8","value":"Are More LLM Calls All You Need? Towards Scaling Laws of Compound Inference Systems","source_method":"lit-search.py metadata","source_file":"Findings table row 8"}
{"claim_id":"10.48550-arxiv.2403.02419-citation_count","doi":"10.48550/arXiv.2403.02419","category":"citation_count","description":"Citation count for row 8","value":107,"source_method":"lit-search.py metadata","source_file":"Findings table row 8"}
{"claim_id":"10.48550-arxiv.2403.02419-doi_resolves","doi":"10.48550/arXiv.2403.02419","category":"doi_resolves","description":"DOI resolves to expected paper for row 8","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 8"}
{"claim_id":"10.48550-arxiv.2408.03314-authors","doi":"10.48550/arXiv.2408.03314","category":"authors","description":"Authors for row 9","value":"Snell et al. (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 9"}
{"claim_id":"10.48550-arxiv.2408.03314-year","doi":"10.48550/arXiv.2408.03314","category":"year","description":"Publication year for row 9","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 9"}
{"claim_id":"10.48550-arxiv.2408.03314-title","doi":"10.48550/arXiv.2408.03314","category":"title","description":"Title for row 9","value":"Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters","source_method":"lit-search.py metadata","source_file":"Findings table row 9"}
{"claim_id":"10.48550-arxiv.2408.03314-citation_count","doi":"10.48550/arXiv.2408.03314","category":"citation_count","description":"Citation count for row 9","value":20,"source_method":"lit-search.py metadata","source_file":"Findings table row 9"}
{"claim_id":"10.48550-arxiv.2408.03314-doi_resolves","doi":"10.48550/arXiv.2408.03314","category":"doi_resolves","description":"DOI resolves to expected paper for row 9","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 9"}
{"claim_id":"10.48550-arxiv.2502.06233-authors","doi":"10.48550/arXiv.2502.06233","category":"authors","description":"Authors for row 10","value":"Taubenfeld et al. (2025)","source_method":"lit-search.py metadata","source_file":"Findings table row 10"}
{"claim_id":"10.48550-arxiv.2502.06233-year","doi":"10.48550/arXiv.2502.06233","category":"year","description":"Publication year for row 10","value":2025,"source_method":"lit-search.py metadata","source_file":"Findings table row 10"}
{"claim_id":"10.48550-arxiv.2502.06233-title","doi":"10.48550/arXiv.2502.06233","category":"title","description":"Title for row 10","value":"Confidence Improves Self-Consistency in LLMs","source_method":"lit-search.py metadata","source_file":"Findings table row 10"}
{"claim_id":"10.48550-arxiv.2502.06233-citation_count","doi":"10.48550/arXiv.2502.06233","category":"citation_count","description":"Citation count for row 10","value":1,"source_method":"lit-search.py metadata","source_file":"Findings table row 10"}
{"claim_id":"10.48550-arxiv.2502.06233-doi_resolves","doi":"10.48550/arXiv.2502.06233","category":"doi_resolves","description":"DOI resolves to expected paper for row 10","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 10"}
{"claim_id":"10.18653-v1-2025.naacl-long.184-authors","doi":"10.18653/v1/2025.naacl-long.184","category":"authors","description":"Authors for row 11","value":"Wan et al. (2025)","source_method":"lit-search.py metadata","source_file":"Findings table row 11"}
{"claim_id":"10.18653-v1-2025.naacl-long.184-year","doi":"10.18653/v1/2025.naacl-long.184","category":"year","description":"Publication year for row 11","value":2025,"source_method":"lit-search.py metadata","source_file":"Findings table row 11"}
{"claim_id":"10.18653-v1-2025.naacl-long.184-title","doi":"10.18653/v1/2025.naacl-long.184","category":"title","description":"Title for row 11","value":"Reasoning Aware Self-Consistency: Leveraging Reasoning Paths for Efficient LLM Sampling","source_method":"lit-search.py metadata","source_file":"Findings table row 11"}
{"claim_id":"10.18653-v1-2025.naacl-long.184-citation_count","doi":"10.18653/v1/2025.naacl-long.184","category":"citation_count","description":"Citation count for row 11","value":9,"source_method":"lit-search.py metadata","source_file":"Findings table row 11"}
{"claim_id":"10.18653-v1-2025.naacl-long.184-doi_resolves","doi":"10.18653/v1/2025.naacl-long.184","category":"doi_resolves","description":"DOI resolves to expected paper for row 11","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 11"}
{"claim_id":"10.48550-arxiv.2504.11101-authors","doi":"10.48550/arXiv.2504.11101","category":"authors","description":"Authors for row 12","value":"Zhang et al. (2025)","source_method":"lit-search.py metadata","source_file":"Findings table row 12"}
{"claim_id":"10.48550-arxiv.2504.11101-year","doi":"10.48550/arXiv.2504.11101","category":"year","description":"Publication year for row 12","value":2025,"source_method":"lit-search.py metadata","source_file":"Findings table row 12"}
{"claim_id":"10.48550-arxiv.2504.11101-title","doi":"10.48550/arXiv.2504.11101","category":"title","description":"Title for row 12","value":"Consensus Entropy: Harnessing Multi-VLM Agreement for Self-Verifying and Self-Improving OCR","source_method":"lit-search.py metadata","source_file":"Findings table row 12"}
{"claim_id":"10.48550-arxiv.2504.11101-citation_count","doi":"10.48550/arXiv.2504.11101","category":"citation_count","description":"Citation count for row 12","value":0,"source_method":"lit-search.py metadata","source_file":"Findings table row 12"}
{"claim_id":"10.48550-arxiv.2504.11101-doi_resolves","doi":"10.48550/arXiv.2504.11101","category":"doi_resolves","description":"DOI resolves to expected paper for row 12","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 12"}
{"claim_id":"10.48550-arxiv.2310.07088-authors","doi":"10.48550/arXiv.2310.07088","category":"authors","description":"Authors for row 13","value":"Naik et al. (2023)","source_method":"lit-search.py metadata","source_file":"Findings table row 13"}
{"claim_id":"10.48550-arxiv.2310.07088-year","doi":"10.48550/arXiv.2310.07088","category":"year","description":"Publication year for row 13","value":2023,"source_method":"lit-search.py metadata","source_file":"Findings table row 13"}
{"claim_id":"10.48550-arxiv.2310.07088-title","doi":"10.48550/arXiv.2310.07088","category":"title","description":"Title for row 13","value":"Diversity of Thought Improves Reasoning Abilities of Large Language Models","source_method":"lit-search.py metadata","source_file":"Findings table row 13"}
{"claim_id":"10.48550-arxiv.2310.07088-citation_count","doi":"10.48550/arXiv.2310.07088","category":"citation_count","description":"Citation count for row 13","value":21,"source_method":"lit-search.py metadata","source_file":"Findings table row 13"}
{"claim_id":"10.48550-arxiv.2310.07088-doi_resolves","doi":"10.48550/arXiv.2310.07088","category":"doi_resolves","description":"DOI resolves to expected paper for row 13","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 13"}
{"claim_id":"10.48550-arxiv.2607.20768-authors","doi":"10.48550/arXiv.2607.20768","category":"authors","description":"Authors for row 14 (single author; OpenAlex returns the Hangul form 김동환, arXiv the Latin transliteration Donghwan Kim)","value":"Kim (2026)","source_method":"lit-search.py metadata","source_file":"Findings table row 14"}
{"claim_id":"10.48550-arxiv.2607.20768-year","doi":"10.48550/arXiv.2607.20768","category":"year","description":"Publication year for row 14","value":2026,"source_method":"lit-search.py metadata","source_file":"Findings table row 14"}
{"claim_id":"10.48550-arxiv.2607.20768-title","doi":"10.48550/arXiv.2607.20768","category":"title","description":"Title for row 14","value":"Are Diversity Metrics Measuring Diversity? A Capability-Controlled Audit of Majority-Vote Gain in LLM Ensembles","source_method":"lit-search.py metadata","source_file":"Findings table row 14"}
{"claim_id":"10.48550-arxiv.2607.20768-citation_count","doi":"10.48550/arXiv.2607.20768","category":"citation_count","description":"Citation count for row 14","value":0,"source_method":"lit-search.py metadata","source_file":"Findings table row 14"}
{"claim_id":"10.48550-arxiv.2607.20768-doi_resolves","doi":"10.48550/arXiv.2607.20768","category":"doi_resolves","description":"DOI resolves to expected paper for row 14","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 14"}
{"claim_id":"10.18653-v1-2022.acl-long.556-authors","doi":"10.18653/v1/2022.acl-long.556","category":"authors","description":"Authors for row 15","value":"Lu et al. (2022)","source_method":"lit-search.py metadata","source_file":"Findings table row 15"}
{"claim_id":"10.18653-v1-2022.acl-long.556-year","doi":"10.18653/v1/2022.acl-long.556","category":"year","description":"Publication year for row 15","value":2022,"source_method":"lit-search.py metadata","source_file":"Findings table row 15"}
{"claim_id":"10.18653-v1-2022.acl-long.556-title","doi":"10.18653/v1/2022.acl-long.556","category":"title","description":"Title for row 15","value":"Fantastically Ordered Prompts and Where to Find Them: Overcoming Few-Shot Prompt Order Sensitivity","source_method":"lit-search.py metadata","source_file":"Findings table row 15"}
{"claim_id":"10.18653-v1-2022.acl-long.556-citation_count","doi":"10.18653/v1/2022.acl-long.556","category":"citation_count","description":"Citation count for row 15","value":358,"source_method":"lit-search.py metadata","source_file":"Findings table row 15"}
{"claim_id":"10.18653-v1-2022.acl-long.556-doi_resolves","doi":"10.18653/v1/2022.acl-long.556","category":"doi_resolves","description":"DOI resolves to expected paper for row 15","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 15"}
{"claim_id":"10.48550-arxiv.2102.09690-authors","doi":"10.48550/arXiv.2102.09690","category":"authors","description":"Authors for row 16","value":"Zhao et al. (2021)","source_method":"lit-search.py metadata","source_file":"Findings table row 16"}
{"claim_id":"10.48550-arxiv.2102.09690-year","doi":"10.48550/arXiv.2102.09690","category":"year","description":"Publication year for row 16","value":2021,"source_method":"lit-search.py metadata","source_file":"Findings table row 16"}
{"claim_id":"10.48550-arxiv.2102.09690-title","doi":"10.48550/arXiv.2102.09690","category":"title","description":"Title for row 16","value":"Calibrate Before Use: Improving Few-Shot Performance of Language Models","source_method":"lit-search.py metadata","source_file":"Findings table row 16"}
{"claim_id":"10.48550-arxiv.2102.09690-citation_count","doi":"10.48550/arXiv.2102.09690","category":"citation_count","description":"Citation count for row 16","value":72,"source_method":"lit-search.py metadata","source_file":"Findings table row 16"}
{"claim_id":"10.48550-arxiv.2102.09690-doi_resolves","doi":"10.48550/arXiv.2102.09690","category":"doi_resolves","description":"DOI resolves to expected paper for row 16","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 16"}
{"claim_id":"10.48550-arxiv.2405.20612-authors","doi":"10.48550/arXiv.2405.20612","category":"authors","description":"Authors for row 17","value":"Zhou et al. (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 17"}
{"claim_id":"10.48550-arxiv.2405.20612-year","doi":"10.48550/arXiv.2405.20612","category":"year","description":"Publication year for row 17","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 17"}
{"claim_id":"10.48550-arxiv.2405.20612-title","doi":"10.48550/arXiv.2405.20612","category":"title","description":"Title for row 17","value":"UniBias: Unveiling and Mitigating LLM Bias through Internal Attention and FFN Manipulation","source_method":"lit-search.py metadata","source_file":"Findings table row 17"}
{"claim_id":"10.48550-arxiv.2405.20612-citation_count","doi":"10.48550/arXiv.2405.20612","category":"citation_count","description":"Citation count for row 17","value":1,"source_method":"lit-search.py metadata","source_file":"Findings table row 17"}
{"claim_id":"10.48550-arxiv.2405.20612-doi_resolves","doi":"10.48550/arXiv.2405.20612","category":"doi_resolves","description":"DOI resolves to expected paper for row 17","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 17"}
{"claim_id":"10.48550-arxiv.2404.11018-authors","doi":"10.48550/arXiv.2404.11018","category":"authors","description":"Authors for row 18","value":"Agarwal et al. (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 18"}
{"claim_id":"10.48550-arxiv.2404.11018-year","doi":"10.48550/arXiv.2404.11018","category":"year","description":"Publication year for row 18","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 18"}
{"claim_id":"10.48550-arxiv.2404.11018-title","doi":"10.48550/arXiv.2404.11018","category":"title","description":"Title for row 18","value":"Many-Shot In-Context Learning","source_method":"lit-search.py metadata","source_file":"Findings table row 18"}
{"claim_id":"10.48550-arxiv.2404.11018-citation_count","doi":"10.48550/arXiv.2404.11018","category":"citation_count","description":"Citation count for row 18","value":262,"source_method":"lit-search.py metadata","source_file":"Findings table row 18"}
{"claim_id":"10.48550-arxiv.2404.11018-doi_resolves","doi":"10.48550/arXiv.2404.11018","category":"doi_resolves","description":"DOI resolves to expected paper for row 18","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 18"}
{"claim_id":"10.48550-arxiv.2405.09798-authors","doi":"10.48550/arXiv.2405.09798","category":"authors","description":"Authors for row 19","value":"Jiang et al. (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 19"}
{"claim_id":"10.48550-arxiv.2405.09798-year","doi":"10.48550/arXiv.2405.09798","category":"year","description":"Publication year for row 19","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 19"}
{"claim_id":"10.48550-arxiv.2405.09798-title","doi":"10.48550/arXiv.2405.09798","category":"title","description":"Title for row 19","value":"Many-Shot In-Context Learning in Multimodal Foundation Models","source_method":"lit-search.py metadata","source_file":"Findings table row 19"}
{"claim_id":"10.48550-arxiv.2405.09798-citation_count","doi":"10.48550/arXiv.2405.09798","category":"citation_count","description":"Citation count for row 19","value":68,"source_method":"lit-search.py metadata","source_file":"Findings table row 19"}
{"claim_id":"10.48550-arxiv.2405.09798-doi_resolves","doi":"10.48550/arXiv.2405.09798","category":"doi_resolves","description":"DOI resolves to expected paper for row 19","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 19"}
{"claim_id":"10.48550-arxiv.2509.09958-authors","doi":"10.48550/arXiv.2509.09958","category":"authors","description":"Authors for row 20 (two authors, so both surnames rendered)","value":"Liu & Hu (2025)","source_method":"lit-search.py metadata","source_file":"Findings table row 20"}
{"claim_id":"10.48550-arxiv.2509.09958-year","doi":"10.48550/arXiv.2509.09958","category":"year","description":"Publication year for row 20","value":2025,"source_method":"lit-search.py metadata","source_file":"Findings table row 20"}
{"claim_id":"10.48550-arxiv.2509.09958-title","doi":"10.48550/arXiv.2509.09958","category":"title","description":"Title for row 20 (arXiv v3 carries the typo 'Vison-Language'; metadata chain returns the corrected form)","value":"Zero-Shot Referring Expression Comprehension via Visual-Language True/False Verification","source_method":"lit-search.py metadata","source_file":"Findings table row 20"}
{"claim_id":"10.48550-arxiv.2509.09958-citation_count","doi":"10.48550/arXiv.2509.09958","category":"citation_count","description":"Citation count for row 20","value":0,"source_method":"lit-search.py metadata","source_file":"Findings table row 20"}
{"claim_id":"10.48550-arxiv.2509.09958-doi_resolves","doi":"10.48550/arXiv.2509.09958","category":"doi_resolves","description":"DOI resolves to expected paper for row 20","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 20"}
{"claim_id":"10.48550-arxiv.2310.01798-authors","doi":"10.48550/arXiv.2310.01798","category":"authors","description":"Authors for row 21","value":"Huang et al. (2023)","source_method":"lit-search.py metadata","source_file":"Findings table row 21"}
{"claim_id":"10.48550-arxiv.2310.01798-year","doi":"10.48550/arXiv.2310.01798","category":"year","description":"Publication year for row 21","value":2023,"source_method":"lit-search.py metadata","source_file":"Findings table row 21"}
{"claim_id":"10.48550-arxiv.2310.01798-title","doi":"10.48550/arXiv.2310.01798","category":"title","description":"Title for row 21","value":"Large Language Models Cannot Self-Correct Reasoning Yet","source_method":"lit-search.py metadata","source_file":"Findings table row 21"}
{"claim_id":"10.48550-arxiv.2310.01798-citation_count","doi":"10.48550/arXiv.2310.01798","category":"citation_count","description":"Citation count for row 21","value":38,"source_method":"lit-search.py metadata","source_file":"Findings table row 21"}
{"claim_id":"10.48550-arxiv.2310.01798-doi_resolves","doi":"10.48550/arXiv.2310.01798","category":"doi_resolves","description":"DOI resolves to expected paper for row 21","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 21"}
{"claim_id":"10.48550-arxiv.2312.14135-authors","doi":"10.48550/arXiv.2312.14135","category":"authors","description":"Authors for row 22 (two authors, so both surnames rendered)","value":"Wu & Xie (2023)","source_method":"lit-search.py metadata","source_file":"Findings table row 22"}
{"claim_id":"10.48550-arxiv.2312.14135-year","doi":"10.48550/arXiv.2312.14135","category":"year","description":"Publication year for row 22","value":2023,"source_method":"lit-search.py metadata","source_file":"Findings table row 22"}
{"claim_id":"10.48550-arxiv.2312.14135-title","doi":"10.48550/arXiv.2312.14135","category":"title","description":"Title for row 22","value":"V*: Guided Visual Search as a Core Mechanism in Multimodal LLMs","source_method":"lit-search.py metadata","source_file":"Findings table row 22"}
{"claim_id":"10.48550-arxiv.2312.14135-citation_count","doi":"10.48550/arXiv.2312.14135","category":"citation_count","description":"Citation count for row 22","value":1,"source_method":"lit-search.py metadata","source_file":"Findings table row 22"}
{"claim_id":"10.48550-arxiv.2312.14135-doi_resolves","doi":"10.48550/arXiv.2312.14135","category":"doi_resolves","description":"DOI resolves to expected paper for row 22","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 22"}
{"claim_id":"10.48550-arxiv.2505.21523-authors","doi":"10.48550/arXiv.2505.21523","category":"authors","description":"Authors for row 23","value":"Liu et al. (2025)","source_method":"lit-search.py metadata","source_file":"Findings table row 23"}
{"claim_id":"10.48550-arxiv.2505.21523-year","doi":"10.48550/arXiv.2505.21523","category":"year","description":"Publication year for row 23","value":2025,"source_method":"lit-search.py metadata","source_file":"Findings table row 23"}
{"claim_id":"10.48550-arxiv.2505.21523-title","doi":"10.48550/arXiv.2505.21523","category":"title","description":"Title for row 23","value":"More Thinking, Less Seeing? Assessing Amplified Hallucination in Multimodal Reasoning Models","source_method":"lit-search.py metadata","source_file":"Findings table row 23"}
{"claim_id":"10.48550-arxiv.2505.21523-citation_count","doi":"10.48550/arXiv.2505.21523","category":"citation_count","description":"Citation count for row 23","value":0,"source_method":"lit-search.py metadata","source_file":"Findings table row 23"}
{"claim_id":"10.48550-arxiv.2505.21523-doi_resolves","doi":"10.48550/arXiv.2505.21523","category":"doi_resolves","description":"DOI resolves to expected paper for row 23","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 23"}
{"claim_id":"10.48550-arxiv.2509.25848-authors","doi":"10.48550/arXiv.2509.25848","category":"authors","description":"Authors for row 24","value":"Tian et al. (2025)","source_method":"lit-search.py metadata","source_file":"Findings table row 24"}
{"claim_id":"10.48550-arxiv.2509.25848-year","doi":"10.48550/arXiv.2509.25848","category":"year","description":"Publication year for row 24","value":2025,"source_method":"lit-search.py metadata","source_file":"Findings table row 24"}
{"claim_id":"10.48550-arxiv.2509.25848-title","doi":"10.48550/arXiv.2509.25848","category":"title","description":"Title for row 24","value":"More Thought, Less Accuracy? On the Dual Nature of Reasoning in Vision-Language Models","source_method":"lit-search.py metadata","source_file":"Findings table row 24"}
{"claim_id":"10.48550-arxiv.2509.25848-citation_count","doi":"10.48550/arXiv.2509.25848","category":"citation_count","description":"Citation count for row 24","value":26,"source_method":"lit-search.py metadata","source_file":"Findings table row 24"}
{"claim_id":"10.48550-arxiv.2509.25848-doi_resolves","doi":"10.48550/arXiv.2509.25848","category":"doi_resolves","description":"DOI resolves to expected paper for row 24","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 24"}
{"claim_id":"10.48550-arxiv.2510.08964-authors","doi":"10.48550/arXiv.2510.08964","category":"authors","description":"Authors for row 25","value":"Li et al. (2025)","source_method":"lit-search.py metadata","source_file":"Findings table row 25"}
{"claim_id":"10.48550-arxiv.2510.08964-year","doi":"10.48550/arXiv.2510.08964","category":"year","description":"Publication year for row 25","value":2025,"source_method":"lit-search.py metadata","source_file":"Findings table row 25"}
{"claim_id":"10.48550-arxiv.2510.08964-title","doi":"10.48550/arXiv.2510.08964","category":"title","description":"Title for row 25","value":"Unleashing Perception-Time Scaling to Multimodal Reasoning Models","source_method":"lit-search.py metadata","source_file":"Findings table row 25"}
{"claim_id":"10.48550-arxiv.2510.08964-citation_count","doi":"10.48550/arXiv.2510.08964","category":"citation_count","description":"Citation count for row 25","value":1,"source_method":"lit-search.py metadata","source_file":"Findings table row 25"}
{"claim_id":"10.48550-arxiv.2510.08964-doi_resolves","doi":"10.48550/arXiv.2510.08964","category":"doi_resolves","description":"DOI resolves to expected paper for row 25","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 25"}
{"claim_id":"10.18653-v1-2024.trustnlp-1.13-authors","doi":"10.18653/v1/2024.trustnlp-1.13","category":"authors","description":"Authors for row 26 (two authors, so both surnames rendered)","value":"Groot & Valdenegro-Toro (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 26"}
{"claim_id":"10.18653-v1-2024.trustnlp-1.13-year","doi":"10.18653/v1/2024.trustnlp-1.13","category":"year","description":"Publication year for row 26","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 26"}
{"claim_id":"10.18653-v1-2024.trustnlp-1.13-title","doi":"10.18653/v1/2024.trustnlp-1.13","category":"title","description":"Title for row 26","value":"Overconfidence is Key: Verbalized Uncertainty Evaluation in Large Language and Vision-Language Models","source_method":"lit-search.py metadata","source_file":"Findings table row 26"}
{"claim_id":"10.18653-v1-2024.trustnlp-1.13-citation_count","doi":"10.18653/v1/2024.trustnlp-1.13","category":"citation_count","description":"Citation count for row 26","value":13,"source_method":"lit-search.py metadata","source_file":"Findings table row 26"}
{"claim_id":"10.18653-v1-2024.trustnlp-1.13-doi_resolves","doi":"10.18653/v1/2024.trustnlp-1.13","category":"doi_resolves","description":"DOI resolves to expected paper for row 26","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 26"}
{"claim_id":"10.18653-v1-2025.emnlp-main.74-authors","doi":"10.18653/v1/2025.emnlp-main.74","category":"authors","description":"Authors for row 27","value":"Xuan et al. (2025)","source_method":"lit-search.py metadata","source_file":"Findings table row 27"}
{"claim_id":"10.18653-v1-2025.emnlp-main.74-year","doi":"10.18653/v1/2025.emnlp-main.74","category":"year","description":"Publication year for row 27","value":2025,"source_method":"lit-search.py metadata","source_file":"Findings table row 27"}
{"claim_id":"10.18653-v1-2025.emnlp-main.74-title","doi":"10.18653/v1/2025.emnlp-main.74","category":"title","description":"Title for row 27","value":"Seeing is Believing, but How Much? A Comprehensive Analysis of Verbalized Calibration in Vision-Language Models","source_method":"lit-search.py metadata","source_file":"Findings table row 27"}
{"claim_id":"10.18653-v1-2025.emnlp-main.74-citation_count","doi":"10.18653/v1/2025.emnlp-main.74","category":"citation_count","description":"Citation count for row 27","value":4,"source_method":"lit-search.py metadata","source_file":"Findings table row 27"}
{"claim_id":"10.18653-v1-2025.emnlp-main.74-doi_resolves","doi":"10.18653/v1/2025.emnlp-main.74","category":"doi_resolves","description":"DOI resolves to expected paper for row 27","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 27"}
{"claim_id":"10.48550-arxiv.2305.14975-authors","doi":"10.48550/arXiv.2305.14975","category":"authors","description":"Authors for row 28","value":"Tian et al. (2023)","source_method":"lit-search.py metadata","source_file":"Findings table row 28"}
{"claim_id":"10.48550-arxiv.2305.14975-year","doi":"10.48550/arXiv.2305.14975","category":"year","description":"Publication year for row 28","value":2023,"source_method":"lit-search.py metadata","source_file":"Findings table row 28"}
{"claim_id":"10.48550-arxiv.2305.14975-title","doi":"10.48550/arXiv.2305.14975","category":"title","description":"Title for row 28","value":"Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback","source_method":"lit-search.py metadata","source_file":"Findings table row 28"}
{"claim_id":"10.48550-arxiv.2305.14975-citation_count","doi":"10.48550/arXiv.2305.14975","category":"citation_count","description":"Citation count for row 28","value":5,"source_method":"lit-search.py metadata","source_file":"Findings table row 28"}
{"claim_id":"10.48550-arxiv.2305.14975-doi_resolves","doi":"10.48550/arXiv.2305.14975","category":"doi_resolves","description":"DOI resolves to expected paper for row 28","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 28"}
{"claim_id":"10.48550-arxiv.2410.10594-authors","doi":"10.48550/arXiv.2410.10594","category":"authors","description":"Authors for row 29 (OpenAlex reverses the first author to 'Yu Shi'; arXiv gives 'Shi Yu', so the surname is Yu)","value":"Yu et al. (2024)","source_method":"lit-search.py metadata","source_file":"Findings table row 29"}
{"claim_id":"10.48550-arxiv.2410.10594-year","doi":"10.48550/arXiv.2410.10594","category":"year","description":"Publication year for row 29","value":2024,"source_method":"lit-search.py metadata","source_file":"Findings table row 29"}
{"claim_id":"10.48550-arxiv.2410.10594-title","doi":"10.48550/arXiv.2410.10594","category":"title","description":"Title for row 29","value":"VisRAG: Vision-based Retrieval-augmented Generation on Multi-modality Documents","source_method":"lit-search.py metadata","source_file":"Findings table row 29"}
{"claim_id":"10.48550-arxiv.2410.10594-citation_count","doi":"10.48550/arXiv.2410.10594","category":"citation_count","description":"Citation count for row 29","value":6,"source_method":"lit-search.py metadata","source_file":"Findings table row 29"}
{"claim_id":"10.48550-arxiv.2410.10594-doi_resolves","doi":"10.48550/arXiv.2410.10594","category":"doi_resolves","description":"DOI resolves to expected paper for row 29","value":true,"source_method":"lit-search.py metadata","source_file":"Findings table row 29"}
```
<!-- END claims.jsonl -->
