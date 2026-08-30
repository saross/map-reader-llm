# AB+ — Adaptive detection of equipment components in MEP construction drawings via graph-enhanced siamese vision

| field | value |
|---|---|
| **citekey** | `yin_adaptive_2025` |
| **full cite** | Yin, Mengtian et al. (2025) *Adaptive detection of equipment components in MEP construction drawings via graph-enhanced siamese vision.* Journal of Building Engineering. DOI: 10.1016/j.jobe.2025.114526 |
| **register** | Borrowed (construction informatics / engineering-drawing symbol detection — Journal of Building Engineering) |
| **primary gap** | Symbol-on-technical-drawing analogue |
| **also touches** | Cost/accuracy trade-space; Calibration transfer / transfer taxes; Ground-truth epistemics — seen/unseen class bookkeeping; Metric hygiene — class-relative vs aggregate reporting; Annotation budgets; Difficulty ladder (area segmentation → point symbols) |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Yin, Duan, and colleagues tackle our task's closest industrial analogue: finding one nominated symbol family in a cluttered technical drawing that every firm draws differently. Their Graph-enhanced Self-supervised Siamese Vision (GSSV) framework pairs a bespoke Graph Manhattan Matching Distance screen over graph-encoded candidate regions with a DINO-pretrained ResNet-50 Siamese network trained on 14,799 synthetic tensor pairs built from 13 templates. No human ever draws a bounding box — though a human must still supply one query exemplar per class (§3: thirteen classes 'each with a sample instance') and select the working layer (§6.2(d)). It reports 88.6%/89.5%/F1 0.89 on 192 instances across 13 trained types in 28 drawings, and 98.9%/90.9%/F1 0.95 on 99 instances across five nominally unseen types.

Three things earn it a place in §2 and §5. First, the architecture rhymes with ours: a false-positive-free cheap screen (Table 5: GMMD FP = 0 on both sets) feeding an expensive stage that recovers recall. Deleting the Siamese branch lifts precision to 100% while recall collapses to 51.3%, saving 11.60 s to 9.62 s of second-stage time, or 11.5% end to end once Table 2's 5.57 s graph generation counts.

Second, the enabling condition is what a scanned Soviet-era sheet denies: GSSV works on DXF vector primitives, layers, and topology, and cannot handle raster images — a present boundary the authors propose to cross by vectorisation, not a permanent one.

Third, its reporting exhibits traps we have committed to avoiding. The 0.89 aggregate conceals a class at 0.00 (flushing water pump: 3 instances, 4 FPs). Table 1 carries TN = 0 in every row, so MCC is undefined (eight rows with FP = FN = 0 give a zero denominator) or degenerate where formable at all (the Total row yields -0.11): a protocol with no enumerable negative class. Its per-class precision column reads 100% for all four classes with non-zero false positives — jockey pump (FP 10, recomputes to 61.5%), fire service pump (73.3%), potable water pump (76.9%), fan (92.3%) — and the per-class F1 column inherits the error, while the aggregate row reproduces exactly (172/194, 172/192, F1 0.891), as does every cell of Table 6. Nor is the unseen set cleanly unseen: 26 of its 99 instances are a trained class re-styled and 10 the water-cooled chiller §5.1 lists as trained, leaving 63 unambiguously novel. Recomputed on those 63 the figure barely moves — precision 100%, recall 88.9%, F1 0.94 against the reported 98.9%, 90.9%, 0.95 — so the contamination does not inflate the headline; what it damages is the bookkeeping, and with it any claim to know what the number is a number about. The unseen-above-seen gap is a composition effect: the confusable pump families carrying almost all seen-set errors have no unseen counterpart. And the 99 unseen instances come 'from the same sets of collected drawings' (§5.1) — no new drawing, corpus, or region — while §6.2(f) concedes 'geographic bias' from 'the lack of cross-regional drawings'. Cite the architecture warmly; quote its numbers only with class scope attached.

## Positioning annotation (interpretive)

The symbol-on-technical-drawing analogue in its strongest 2025 form, and the paper a reviewer will reach for when asking whether map symbols are just Piping and Instrumentation Diagram symbols with contour lines behind them. Cite it in §2 for the architectural convergence — a false-positive-free cheap screen feeding an expensive visual verifier, with an ablation that prices the trade — and in §5 for the disanalogy that matters: GSSV's accuracy rests on vector primitives, layers, and topology that a scanned sheet does not carry. Its seen/unseen class inventories contradict each other, so the scope of its headline generalisation number is unrecoverable from the paper — though recomputing on the uncontaminated rows leaves the number essentially unchanged, which makes it a ground-truth-epistemics example rather than a challenge to its score. Its per-class table is also a working example of why we report class-scoped F1 with MCC beside it, since the 0.89 aggregate contains a class at 0.00 and TN = 0 throughout leaves MCC undefined or degenerate on their protocol.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "However, fire service pumps and potable water pumps showed relatively lower recall rates, and flushing water pumps had the poorest performance with no correct detections."
- **Locator:** page_index 13 · p.14 · §5.3.1 Overall performance
- **Paraphrase:** Beneath the 0.89 aggregate the per-class picture is very uneven: two pump types recall poorly and one — flushing water pump, 3 instances in Table 1 — is never detected correctly, scoring precision 0%, recall 0%, F1 0.00. The prose names only these low-recall cases; the largest single source of false positives, fire service jockey pump with 10, goes unremarked.
- **Relevance:** §2 related work; §5 discussion — why we report per-symbol-family F1 with MCC beside it · Metric hygiene — class-relative vs aggregate reporting · **complicates**

### KP2
- **Quote (verbatim):** "it cannot directly handle raster images of engineering drawings, as these images cannot be directly converted into graph-based representations"
- **Locator:** page_index 19 · p.20 · §6.2 Limitations and future work — (b)
- **Paraphrase:** The framework is confined to vectorised CAD/DXF input; raster scans of the same drawings cannot be fed to it, because there is no graph to build from pixels. The authors treat this as a present boundary rather than an in-principle one, proposing raster-to-DXF vectorisation (Potrace, AutoTrace, DeepSVG) as future work.
- **Relevance:** §2 related work; §5 discussion — the area-segmentation → point-symbol difficulty ladder · Difficulty ladder — the substrate that makes the analogue an easier rung than ours · **complicates**

### KP3
- **Quote (verbatim):** "the average processing time per drawing decreased from 11.60 s to 9.62 s, showing a 17.1% reduction in computational cost. However, this efficiency gain comes at a significant performance cost. While the precision increased to 100%, indicating that all detected targets were correct, recall dropped substantially from 90.4% to 51.3%."
- **Locator:** page_index 17 · p.18 · §5.3.4 Ablation study — (b) Impact of Siamese Network
- **Paraphrase:** Deleting the expensive visual verification stage makes precision perfect but almost halves recall — the cheap graph screen alone is high-precision and low-recall. Two denominator caveats attach to the saving. The 17.1% is against second-stage time only: with Table 2's 5.57 s first-stage graph generation added, the Siamese stage costs 1.98 s of 17.17 s, or 11.5% end to end. And Table 2 prices Siamese detection at 4.54 s, yet deleting it saves only 1.98 s. Note too that the ablation prose takes the intact baseline recall as 90.4%, where Table 4's own original-method row gives 89.5%.
- **Relevance:** §5 cost/accuracy trade-space — what the verifier stage buys, priced end to end · Cost/accuracy trade-space · **supports**

### KP4
- **Quote (verbatim):** "These results highlight a critical finding: successful detection of ECs in MEP drawings cannot be achieved by relying solely on either pixel-level similarity or structural graph matching"
- **Locator:** page_index 16 · p.17 · §5.3.3 Comparison with baselines
- **Paraphrase:** Neither of the two single-modality unsupervised baselines is adequate on its own: pixel template matching bought 100% precision at 22.8% recall (F1 0.37), graph pattern matching reached only 0.62, and the authors read the pair as showing that one modality alone cannot do the job. Both baselines are the authors' own reimplementations with hand-set parameters (template threshold 0.9, scale range 0.5-2), and no supervised method was compared, by explicit design.
- **Relevance:** §2 related work; §5 design rationale — why a single-pass, single-signal detector is not the design · Symbol-on-technical-drawing analogue — architecture · **supports**

### KP5
- **Quote (verbatim):** "Achieving 98.9% precision and 90.9% recall on completely unknown device types strongly demonstrates the excellent generalization ability of our method."
- **Locator:** page_index 17 · p.18 · §5.3.5 Analysis of method generalization
- **Paraphrase:** The authors read the unseen-type scores — 98.9% precision, 90.9% recall, F1 0.95 — as strong evidence of generalisation to novel equipment classes, scores that exceed their own seen-class result of 88.6%, 89.5%, F1 0.89. The inversion has a composition explanation rather than a suspicious one: 21 of the 22 seen-set false positives and 19 of the 20 false negatives fall in four visually confusable pump families for which the unseen set has no counterpart, and §5.3.1 attributes an error directly to shape resemblance. The paper's own Conclusion offers the weaker formulation, that unseen performance is 'comparable to that on the seen dataset'.
- **Relevance:** §5 discussion — transfer taxes; why an unseen-set score above the seen-set score wants a composition check before a contamination one · Calibration transfer / transfer taxes · **complicates**

### KP6
- **Quote (verbatim):** "192 target objects across the following 13 object classes: chilled water pump, fire service pump, fire service jockey pump, flushing water pump, condensing water pump, potable water pump, secondary chilled water pump, air handling unit, staircase pressurization fan, exhaust air fan, fan, fuel transfer pump, and water-cooled chiller"
- **Locator:** page_index 12 · p.13 · §5.1 Experimental design
- **Paraphrase:** This enumeration of the 13 trained classes includes the water-cooled chiller and the secondary chilled water pump. Table 6 nevertheless counts 10 water-cooled chiller instances and 26 'Secondary Chilled Water Pump (new style)' instances among its 99 'untrained equipment types', and Table 1's own 13 rows list ventilation fan where this list has water-cooled chiller, so the two class inventories disagree in exactly one slot. Recomputing on the 63 instances that are unambiguously novel (fan coil unit 6, variable air volume 55, cooling tower 2) gives precision 100%, recall 88.9%, F1 0.94 against the reported 0.95: the contamination damages the bookkeeping, not the score.
- **Relevance:** §3 methods — gold-standard construction; §5 discussion — what 'held out' has to mean before a transfer number means anything · Ground-truth epistemics — seen/unseen class bookkeeping · **complicates**

### KP7
- **Quote (verbatim):** "practitioners might recalibrate thresholds when applying the method to new sets of real-world drawings"
- **Locator:** page_index 19 · p.20 · §6.2 Limitations and future work — (e)
- **Paraphrase:** The authors flag that the operating points controlling their pipeline — the Graph Manhattan Matching Distance threshold and the Siamese similarity cutoff — may need recalibration on a new corpus, since the thresholds depend on drawing conventions, standards, CAD noise levels, and layout complexity; they name automated threshold calibration as future work, while §4.1 claims the graph-matching parameters already adapt automatically to the query object.
- **Relevance:** §5 discussion — carried vs oracle operating points. Both operating points were chosen by sweeping on the evaluation corpus itself: §5.3.2 reports the GMMD coefficient k = 50 and the 1.5x bounding-box factor as optimal at precisely the headline 88.6% / 89.5%, with no held-out tuning set — direct oracle-threshold evidence, stronger than this future-work hedge. · Calibration transfer / transfer taxes · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "More advanced CV architectures, such as vision–language models, may also be employed to replace the current Siamese network."
- **Locator:** page_index 19 · p.20
- **Why:** A 2025 construction-informatics paper floating vision–language models, in one clause of a four-item future-work list, as a possible replacement for its hand-built similarity stage — a one-line warrant, from outside our field, for the substitution our study actually performs.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
