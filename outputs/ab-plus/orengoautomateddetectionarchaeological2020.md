# AB+ — Automated detection of archaeological mounds using machine-learning classification of multisensor and multitemporal satellite data

| field | value |
|---|---|
| **citekey** | `orengoAutomatedDetectionArchaeological2020` |
| **full cite** | Orengo, Hector A. et al. (2020) *Automated detection of archaeological mounds using machine-learning classification of multisensor and multitemporal satellite data.* PROCEEDINGS OF THE NATIONAL ACADEMY OF SCIENCES OF THE UNITED STATES OF AMERICA. DOI: 10.1073/pnas.2005583117 |
| **register** | Archaeological prospection (remote sensing / PNAS) |
| **primary gap** | Archaeological prospection prior art — machine-learning mound detection |
| **also touches** | Ground-truth epistemics and gold-standard construction; Annotation budgets and human-in-the-loop; Calibration and operating-point transfer; Metric hygiene and reporting comparability; Difficulty ladder: area segmentation to point symbols; Historical-map extraction lineage |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Orengo and colleagues detect archaeological mounds across ca. 36,000 km2 of the Cholistan Desert in Pakistan with a random-forest classifier, run in Google Earth Engine over a 14-band composite fusing 1,500 Sentinel-1 radar and 3,112 Sentinel-2 multispectral images. Thresholding the probability field at >0.55 yields 337 clusters proposed as mound soil surfaces, of which only 71 could be tied to sites in the Mughal-team legacy record. It is archaeology's flagship machine-learning mound-detection paper, and our nearest object-level prior art.

Orengo's mound is a continuous spectral and textural signature tens of pixels across; a minimum diameter of around 100 m is what makes 10 and 20 m/px imagery workable. Its output is a raster a human then vectorises by photointerpretation — a delineation pass that prunes nothing, since 337 thresholded clusters are still 337 mounds when area estimates are reported. Ours is a drawn glyph, one symbol family among dozens on a Soviet sheet, with no spectral signature and no human pass at scale. The bridge between the two is Orengo's citation of Green et al., who found that in the plains of Haryana mound features visible on historical maps tend to be protohistoric or Bronze Age settlements when checked on the ground — the clearest statement in this literature that the map substrate can carry real archaeological signal, albeit for settlement mounds on a different map series from ours.

Three things transfer. First, annotation budget: the entire positive-class supervision is 25 legacy mound sites, five for training and twenty for validation (the non-mound training class is never quantified in the main text, and two of the three development iterations went on tuning non-mound pixels). Second, calibration. The 0.55 operating point was set by close inspection of the training data, described qualitatively as a compromise between detection capacity and false positives, with validation and quality assessment deferred to the SI Appendix; no precision, recall, F1, confusion matrix, or kappa appears in the eleven pages of the main article, though the abstract and Significance statement still call the output accurate: the absence is of measurement, not of accuracy claims. The reported success is that all 25 known mounds were recovered — a recall statement on sites selected precisely because they were large, well-preserved, and clearly identifiable in high-resolution imagery, and on twenty mounds first inspected after iteration one of three, with two tuning iterations following. That is our easy-positive gold standard and our carried-versus-oracle problem, arising in a paper that does not reach for the vocabulary of either.

Third, ground-truth epistemics. The legacy reference data mix settlements with campsites and industrial sites, and coordinates are often inaccurate and duplicated; the other 266 detections (337 minus 71, our arithmetic) therefore carry no independent verdict: all 337 were photointerpreted by the authors, but against no external reference, so they are neither confirmed discoveries nor confirmed false positives. Precision here is not unreported but uncomputable. Our gold-standard design — small, adjudicated, explicit about what a negative means — answers the condition this paper documents.

## Positioning annotation (interpretive)

The closest object-level prior art in the corpus — automated detection of the same archaeological object — and therefore the source whose differences from our task most need stating rather than assuming. It is the area-segmentation end of the difficulty ladder in a different modality: a spectral signature tens of pixels across, thresholded into a probability field and finished by human photointerpretation, where ours is a drawn point symbol adjudicated automatically. Its principal use to us is as an attested picture of what counts as evaluation in archaeological prospection — 25 legacy mound sites as the whole positive-class supervision, an operating point set by eye on the training data, no classification metric in the main text, and 266 of 337 detections with no ground-truth verdict — which is the condition our preregistered gold standard, our MCC-alongside-F1 reporting, and our carried-versus-oracle operating points are designed to escape. It is lineage and motivation, not a benchmark we can be measured against.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "This set includes the 25 mounds selected from Mughal's surveys (26) used as training (n = 5) and validation (n = 20) data, which were all successfully identified by the algorithm."
- **Locator:** page_index 4 · p.5 · Results — RF Probability Field
- **Paraphrase:** The whole mound-class supervision budget is 25 legacy sites, five used for training and twenty for validation, and the headline validation result is that the algorithm recovered all of them. That is a recall statement on twenty positives with no paired precision figure. It is also weaker than a clean held-out result: the same twenty were inspected after the first of three development iterations, with two further tuning iterations following, and the paper calls them validation data in one place and test data in another.
- **Relevance:** §2 related work — archaeological prospection prior art · Annotation budgets and human-in-the-loop · **supports**

### KP2
- **Quote (verbatim):** "Despite the quality problems in Mughal's data, we selected those sites that could be clearly identified and accurately located in high-resolution imagery available in GEE. These corresponded to large and well-preserved sites."
- **Locator:** page_index 4 · p.5 · Materials and Methods — Machine-Learning Algorithm
- **Paraphrase:** The training and validation sites were chosen for being legible and locatable in high-resolution imagery, which selected for large, well-preserved mounds. The evaluation set is therefore biased toward the easiest positives in the population the method is meant to find — a bias the Conclusion concedes when it claims detection of all previously known mounds for which accurate locations could be gathered.
- **Relevance:** §3 methods — gold-standard construction and easy-positive bias · Ground-truth epistemics and gold-standard construction · **supports**

### KP3
- **Quote (verbatim):** "In order to produce a map of archaeological mounds, a >0.55 RF probability threshold for mound values was selected after close inspection of the training data on the high-resolution imagery, which produced a raster map of clusters ("mounds") on a background of "no mound." A higher threshold resulted in the better delineation of big and clear mounds, but many small clusters of pixels corresponding to partially covered or small mounds were lost. We considered the >0.55 threshold a good compromise between a high mound detection capacity and a minimal inclusion of false-positive pixels (mainly scattered, isolated pixels). The algorithm's validation and quality assessment methods are outlined in SI Appendix, Figs. S3 and S4."
- **Locator:** page_index 4 · p.5 · Materials and Methods — Machine-Learning Algorithm
- **Paraphrase:** The deployment operating point was fixed at 0.55 by visual inspection of the training data, and the trade-off it encodes — recovering small or partly covered mounds against admitting false-positive pixels — is stated qualitatively, with the validation and quality-assessment procedure placed in the supplementary appendix rather than the article. The claim this licenses is about the main text only: the SI was not read, so it must never be restated as the paper reporting no metrics anywhere.
- **Relevance:** §5 discussion — carried versus oracle operating points · Calibration and operating-point transfer · **supports**

### KP4
- **Quote (verbatim):** "Out of a total of 337 clusters of high-probability pixels identified as archaeological mounds by the algorithm, only 71 (including the 25 employed to train and test the algorithm) could be linked with reasonable certainty to sites previously recorded."
- **Locator:** page_index 5 · p.6 · Results — matching detections to legacy data
- **Paraphrase:** Of 337 detections, only 71 could be matched with confidence to previously recorded sites, and those 71 include the 25 already used for training and testing. The remainder are unadjudicated against any external reference — they did pass the authors' own photointerpretation — so precision cannot be computed against a reference set that is neither complete nor reliably located.
- **Relevance:** §5 discussion — what a false positive means without a complete reference set · Ground-truth epistemics and gold-standard construction · **complicates**

### KP5
- **Quote (verbatim):** "Moreover, Mughal's data (table 11 in ref. 26) include both mounded locations and other types of short-term occupation, such as industrial sites or campsites, and therefore many sites do not correspond to long-term mounded settlements. In addition, reported coordinates are often inaccurate and duplicated."
- **Locator:** page_index 2 · p.3 · Research Background — Old Limitations, Novel Approaches
- **Paraphrase:** The legacy survey serving as ground truth is class-impure — it mixes long-term mounded settlements with campsites and industrial locations — and its coordinates are frequently wrong or duplicated. The reference data are a noisy label set, not a gold standard.
- **Relevance:** §3 methods — why a small adjudicated gold standard beats a large legacy one · Ground-truth epistemics and gold-standard construction · **supports**

### KP6
- **Quote (verbatim):** "For example, in the plains of Haryana in northwest India, Green et al. (14) have highlighted that mound features visible on historical maps tend to be protohistoric or Bronze Age settlements when surveyed or validated on the ground, whereas Early Historic and Medieval settlements appear to be more frequently associated with modern settlement locations"
- **Locator:** page_index 7 · p.8 · Discussion — Indus Settlement Trends
- **Paraphrase:** In the plains of Haryana, Green et al. found that mound features depicted on historical maps tend to be protohistoric or Bronze Age settlements when checked on the ground, while later settlements are more often collocated with modern villages. Map-depicted mound symbols can therefore index real archaeological features, with a period skew — though for settlement mounds, on a different map series and in a different region from ours, and reaching us second-hand through Orengo's citation.
- **Relevance:** §1 introduction — why mound symbols on historical maps are worth extracting; cite Green et al. (Remote Sens. 11, 2089, 2019) directly if the claim is to carry weight · Historical-map extraction lineage — map-depicted mound symbols index real features (settlement mounds, second-hand) · **supports**

### KP7
- **Quote (verbatim):** "The resulting clusters of high-RF-probability pixels representing mounds were vectorized to reconstruct the areas of the mounds currently covered by sand dunes or desert shrubs. Photointerpretation used high-resolution satellite imagery provided by several map services (including Google Earth and Bing Maps) and a limited collection of available WorldView-2 and -3 imagery."
- **Locator:** page_index 4 · p.5 · Materials and Methods — Integration of Complementary Data, Area Estimates, and GIS Database
- **Paraphrase:** The classifier is a candidate generator whose high-probability clusters are then vectorised, evaluated, and delineated by a human working across several high-resolution imagery sources. That pass appears to reject nothing — the 337 thresholded clusters are still 337 mounds when area estimates are reported — so it fixes extents rather than accepting or rejecting candidates, which is precisely the function our verifier stage adds.
- **Relevance:** §4 architecture — the verifier stage and what it replaces · Annotation budgets and human-in-the-loop · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "The detection of anthropic signatures, such as those that characterize mounded sites, across a very large area, remains seldom attempted, presumably due to the large computational resources, coding expertise, and large amount of satellite data required."
- **Locator:** page_index 0 · p.1
- **Why:** A 2020 statement of the barrier to landscape-scale automated mound detection in the archaeologists' own terms — compute, coding expertise, and data volume. It sets up our cost/accuracy trade-space as the successor question: the barrier has moved from acquiring imagery and writing classifiers to paying per inference and deciding how many passes a detection is worth.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
