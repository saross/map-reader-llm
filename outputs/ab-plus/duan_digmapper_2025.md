# AB+ — DIGMAPPER: A Modular System for Automated Geologic Map Digitization

| field | value |
|---|---|
| **citekey** | `duan_digmapper_2025` |
| **full cite** | Duan, Weiwei et al. (2025) *DIGMAPPER: A Modular System for Automated Geologic Map Digitization.* Proceedings of the 33rd ACM International Conference on Advances in Geographic Information Systems. DOI: 10.1145/3748636.3764602 |
| **register** | Borrowed (GIS/CS — SIGSPATIAL '25 industrial track) |
| **primary gap** | Historical-map extraction lineage — the point-symbol comparator |
| **also touches** | Annotation budgets; Ground-truth epistemics; Difficulty ladder (area segmentation → point symbols); Calibration transfer / carried vs oracle operating points; Metric hygiene (aggregate vs class-relative F1) |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Duan and colleagues describe DIGMAPPER, built for the DARPA/USGS CriticalMAAS programme and since transitioned to the USGS. A fine-tuned LayoutLMv3 separates map content from legend and GPT-4o pairs legend items with descriptions by in-context learning; three extraction modules — TOPAZ for polygons, LDTR for lines, a YOLO-v8 detector for point symbols — occupy one branch of a Dockerised pipeline orchestrated by a directed acyclic graph, whose other branch is a text- and vision-based georeferencer. Evaluation uses the DARPA-USGS dataset: 48 annotated maps for feature extraction, 63 for georeferencing. Its value to us is the shape of its evaluation, not the architecture.

Three things matter. First, the difficulty ladder is visible once tiers are compared like for like. Within each module's top tier, polygons reach a median pixel-level F1 of 0.98 (two maps), fault lines 0.88 correctness and 0.95 completeness (an F1-equivalent of about 0.91), and point symbols an instance-level F1 of 0.89 (three maps). The three metrics are not strictly commensurable, but the ordering survives at every tier, and the honest top-tier gap is 0.98 to 0.89, not 0.98 to 0.82. The point protocol resembles ours — instance-level precision, recall, and F1, a detection correct if its centre falls within two ten-thousandths of the map diagonal — but reports no Matthews correlation coefficient (MCC) and no Intersection-over-Union (IoU) matching.

Second, the headline point figure needs care. The 0.82 is an instance-weighted aggregate over five symbol types on ten maps, carried largely by one abundant class: inclined bedding contributes 1,665 of 2,404 evaluation instances (69 per cent) at F1 0.91, while the four rarer types score 0.69, 0.41, 0.14, and 0.13. The 0.89 alongside it is a different quantity — the map-level F1 of the top three maps in a ten-map ranking the authors bin by F1, not by scan quality, against 0.56 for the middle five and 0.05 for the bottom two. Read as a range, "0.82/0.89" badly understates the spread; a detector averaging 0.82 spans 0.89 to 0.05 across ten individual sheets. For the scan-quality claim proper, cite Tables 2 and 3, whose tiers use the paper's independent visual criteria: polygon median F1 0.98 / 0.77 / 0.28, fault-line correctness 0.88 / 0.73 / 0.40.

Third, the annotation budget is large: annotations from 100 USGS geologic maps plus about 10,000 synthetic patches — 12,910 human-labelled training instances across the five reported types alone, with the other seven trained but never scored. Synthetic data buys three points overall, and nineteen and thirteen on two starved classes (overturned bedding, lineation) — but not on inclined foliation igneous, scarcer at 127 training instances than overturned bedding's 214. Any near-parity claim at a twenty-tile budget should be framed against this, and against DIGMAPPER's ground-truth economics: seven of twelve target symbols dropped for lacking reliable ground truth, maps with incorrect annotations excluded outright. The authors' quality tiering of the polygon and line modules, and their conclusion that human-in-the-loop review remains essential for degraded scans, are the operational cousins of our carried-versus-oracle operating points.

## Positioning annotation (interpretive)

The anchor source for the geologic-map digitisation lineage: a deployed, production-grade pipeline whose point-symbol module is — on our own survey of the literature, not on any claim this paper makes — the closest published comparator to our detector. Its state-of-the-art claims are narrower than the framing suggests: integration into an end-to-end production system, and a DARPA Geological Map Feature Extraction Challenge win for the line module (LDTR) specifically, on geologic rather than topographic maps; its own §4 points at nearer neighbours for point symbols on topographic sheets (Huang et al. 2023, ref. [31]; Smith et al. 2025, ref. [58]). Commensurability likewise needs stating rather than asserting: DIGMAPPER matches detections by centre-distance inside a 2 × 10⁻⁴ map-diagonal buffer and reports precision, recall, and F1 only — no MCC, no IoU-based matching — so any side-by-side table must say so. It remains the strongest external evidence for our area-to-point difficulty ladder and the source most in need of careful metric handling, because its two circulating point figures (0.82 and 0.89) are different quantities on different slices rather than the ends of a range. Its accuracy is stratified by symbol frequency (Table 5) and, in the polygon and line modules, by scan quality assessed against independent visual criteria (Tables 2 and 3); the point module's own tiers are defined by F1 and cannot carry that half of the transfer-tax argument.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "the overall performance is computed by treating all test instances equally across symbol types. Overall, our model achieves an F1 score of 0.82 across 10 maps."
- **Locator:** page_index 6 · p.7 · §2.4.2 Point Extraction — Evaluation (Table 5)
- **Paraphrase:** DIGMAPPER's headline point-symbol figure, F1 0.82, is an instance-weighted aggregate computed over ten maps: every evaluation instance counts equally, so abundant symbol types dominate the score regardless of how many symbol types there are.
- **Relevance:** §2 related work; results comparison table · Metric hygiene — aggregate vs class-relative F1 · **supports**

### KP2
- **Quote (verbatim):** "Excellent 3 0.90 0.88 0.89 Good 5 0.58 0.55 0.56 Fair 2 0.25 0.03 0.05"
- **Locator:** page_index 6 · p.7 · §2.4.2 Point Extraction — Table 4 (map-level performance by F1-defined performance tier)
- **Paraphrase:** Table 4's map-level breakdown of the same point detector: three Excellent maps reach precision 0.90, recall 0.88, F1 0.89; five Good maps 0.58/0.55/0.56; two Fair maps 0.25/0.03/0.05. The 0.89 is therefore the score of the three best-performing maps, not a scan-quality-conditioned result: the paper bins the ten maps into "three performance levels ... based on their F1 scores", then observes post hoc that the Excellent-category maps "typically exhibit high visual clarity" while the Fair-category maps "contain mostly blurred, distorted, and underrepresented point symbols". Table 4 therefore measures the spread of per-map F1 — 0.89 at the top, 0.05 at the bottom — with an associated rather than demonstrated link to scan quality, and the authors name symbol underrepresentation alongside blur as a Fair-category characteristic. Tables 2 and 3, whose tiers come from the independent visual criteria of §2, are the right evidence for a quality-response claim.
- **Relevance:** §5 discussion — transfer taxes and carried operating points · Calibration transfer — per-map accuracy is highly dispersed; a single headline F1 hides an 0.89-to-0.05 range · **complicates**

### KP3
- **Quote (verbatim):** "inclined foliation metamorphic ranks second with an F1 score of 0.69, likely due to a significantly smaller number of human-labeled training samples than inclined bedding (10,635 vs. 1,887)"
- **Locator:** page_index 6 · p.7 · §2.4.2 Point Extraction — Evaluation (discussion of Table 5)
- **Paraphrase:** Per-symbol performance tracks per-symbol label counts: the second-best symbol type reaches only 0.69, which the authors attribute, tentatively ("likely due to"), to having far fewer human-labelled training instances than the best-resourced class. The association is monotonic across all five reported types (#Train 10,625 / 1,887 / 214 / 127 / 57 against F1 0.91 / 0.69 / 0.41 / 0.14 / 0.13), though the authors also name varying shapes and colours for lineation and dark or densely textured backgrounds for inclined foliation igneous, so label count is the dominant but not the sole driver. (The body text's 10,635 conflicts with Table 5's 10,625 for the same cell — a typographical inconsistency internal to the source.)
- **Relevance:** §5 discussion — why a single-family detector is the hard case · Annotation budgets — per-class label counts drive per-class F1 · **supports**

### KP4
- **Quote (verbatim):** "In total, we generate 10,000 synthetic patches, with approximately 3,000 patches per symbol class for training. In addition to synthetic data, we incorporate human annotations from 100 USGS geologic maps"
- **Locator:** page_index 5 · p.6 · §2.4.1 Point Extraction — Method Overview (synthetic data generation)
- **Paraphrase:** The training budget behind the point detector: roughly 10,000 synthetic patches, about 3,000 per symbol class, combined with human annotations drawn from 100 USGS geologic maps. The ablation attached to that budget states its gains as percentages ("improves the overall F1 score by 3%"); Table 5's two overall rows confirm the percentage-point reading (0.79 human-only against 0.82 with synthetic data), but the per-class 19% and 13% gains cannot be checked against any published baseline column.
- **Relevance:** §2 related work; §5 cost/accuracy trade-space · Annotation budgets — the cost baseline a low-budget result is measured against · **complicates**

### KP5
- **Quote (verbatim):** "we exclude maps lacking human-annotated symbols or containing incorrect annotations. The other seven symbol types, while present in training, lack reliable ground truth and are omitted."
- **Locator:** page_index 6 · p.7 · §2.4.2 Point Extraction — Evaluation (evaluation-set curation)
- **Paraphrase:** The evaluation set is curated twice over: maps without symbol annotations or carrying erroneous ones are excluded, and seven of the twelve target symbol types are dropped from reporting altogether because their ground truth is not reliable enough to score against.
- **Relevance:** §3 methods — gold-standard construction; §5 discussion · Ground-truth epistemics — reported accuracy is conditioned on which ground truth was trusted · **complicates**

### KP6
- **Quote (verbatim):** "our approach demonstrates good accuracy in raster and vector metrics, achieving an F1 score of 0.98 and an Ex-gt ratio of 0.99"
- **Locator:** page_index 4 · p.5 · §2.2.2 Polygon Extraction — Evaluation (Table 2)
- **Paraphrase:** For the excellent and good map categories the polygon module is reported at F1 0.98 with an extraction-to-ground-truth ratio of 0.99, putting area segmentation at the easy end of the same system's difficulty ladder. (Table 2 shows 0.98 is the excellent tier's median F1, on just two maps, and 0.99 the good tier's ex-gt ratio, so the sentence pairs best-case cells drawn from different rows.) This is also where the quality-conditioned evidence properly lives: Table 2's tiers come from the reproducible visual criteria defined in §2, not from the outcome, and its median F1 column runs 0.98 (2 maps) / 0.77 (5) / 0.28 (4) across excellent / good / fair, with Table 3's fault-line correctness running 0.88 / 0.73 / 0.40 on the same criteria. Cite these, not the point module's F1-defined Table 4, for the claim that accuracy degrades with source condition.
- **Relevance:** §2 related work; §5 discussion — why point symbols are the hard rung, and transfer taxes · Difficulty ladder — area segmentation vs point symbols; and the independently tiered quality-response evidence that carries the transfer-tax argument · **supports**

### KP7
- **Quote (verbatim):** "In production, we find that human-in-the-loop review remains essential for degraded scans and certain feature types, underscoring the need for quality indicators and correction workflows."
- **Locator:** page_index 9 · p.10 · §5 Conclusion
- **Paraphrase:** Even in a system deployed at the USGS, the authors report that human review cannot be removed for degraded scans and for some feature types, and they call for quality indicators that signal where automated output is unreliable.
- **Relevance:** §5 discussion — deployment operating points and verifier design · Calibration transfer — carried vs oracle operating points · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "Evaluations on over 100 annotated maps from the DARPA-USGS dataset demonstrate high accuracy across polygon, line, and point feature extraction"
- **Locator:** page_index 0 · p.1
- **Why:** The abstract's headline — "over 100 annotated maps" and "high accuracy" across all three feature classes — set against a point-symbol evaluation that actually runs on ten maps and five of twelve symbol types (the "over 100" is the whole DARPA-USGS annotated set — 48 maps for feature extraction plus 63 for georeferencing — and the abstract sentence covers georeferencing too, which genuinely is evaluated on 63 maps; the sharper and non-straw-man form of the contrast is that no feature-extraction module is evaluated on more than eleven maps: 11 for polygons, 10 for lines, 10 for points). A crisp epigraph for the move that aggregate accuracy claims on historical maps conceal per-class and per-condition structure, and that a symbol-family detector must be judged on the class-relative numbers.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
