# AB+ — Creating large, high-quality geospatial datasets from historical maps using novice volunteers

| field | value |
|---|---|
| **citekey** | `sobotkova_creating_2023` |
| **full cite** | Sobotkova, Adela et al. (2023) *Creating large, high-quality geospatial datasets from historical maps using novice volunteers.* Applied geography. DOI: 10.1016/j.apgeog.2023.102967 |
| **register** | Discipline-native (landscape archaeology / applied geography) |
| **primary gap** | Historical-map extraction lineage — the cost-quantified manual baseline |
| **also touches** | Ground-truth epistemics; Annotation budgets; Cost/accuracy trade-space; Area-segmentation to point-symbol difficulty ladder; Consensus and verification architecture |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

The immediate antecedent of the present study, not adjacent prior art: same Soviet 1:50,000 military topographic series, same south-east Bulgarian study area, same burial-mound symbol family, same TRAP ecosystem. Novice volunteers on a FAIMS Mobile customisation digitised 10,827 point features — 'mostly burial and settlement mounds' — from 58 map tiles, for 241 person-hours (44 pre-fieldwork setup, 36 of them outsourced; 184 volunteer; 7 in-field support; 6 quality assurance), 44.9 features per person-hour. The paper does not reconcile with itself: §3.2 totals 189.4 student-hours (Tables 1-2: 125.8 + 63.6) against the 184 used in abstract, discussion and conclusion — on which the campaign costs 246.4 person-hours at 43.9 features/hour. Cite 184/241 as the paper's arithmetic, discrepancy noted.

The error anatomy matters most, and the preregistration sharpens why: it records that this study builds on the source and that the four maps audited in §3.5.2 are the present gold-standard corpus (preregistration.md lines 19, 260) — the human operating point sits on precisely the tiles the VLM is evaluated on. Staff scored 49 errors against a true count of 834: recall about 95% (792 of 834) at 99.1% precision, seven of 799 records being invalid — six duplicate marks of one map section, one a misidentified symbol (a false positive in Table 3, a classification error in the prose; label contradicted, count of one stable). Failure is overwhelmingly omission, not fabrication, and spatially clustered: 35 of the 49 total errors came from one volunteer — 29 of the 42 false negatives plus all 6 double-marks — whose exclusion halves the cumulative rate from 5.9% to 2.8%. The prose's '35 of the 49 false negatives' is garbled; Table 3A's columns reproduce its cumulative row exactly, so anchor on the table. Two consequences: report precision and recall separately, since human and model fail in opposite directions; and treat the human ceiling as a distribution — 1.3% to 10.6% across four audited volunteers of nine digitisers, over 799 of 10,827 features (7.4%).

It is also the clearest statement of the gap our cost measurements fill — ML papers rarely quantify time-on-task — but its thresholds need their conditions carried. Crowdsourcing pays off above about 4,500 features against staff desktop GIS and 10,000 against volunteer desktop GIS only on the most conservative costing, charging all invested time; on in-field staff time alone Table 4 gives 420-525 and 910-1,260. The 60,000-record ML threshold assumes zero marginal personnel cost for model-found features, mound symbols no harder than road segments, and discounts the benchmark project's unreported QA; since 1,250 of its 1,300 hours are manual training-set digitisation, a zero- or few-shot VLM pipeline needing no training set does not sit on that curve at all — cite it as the manual-era benchmark this study displaces, not a threshold to clear. It also anticipates our architecture in human form — redundant independent digitisation plus peer review, checking cheaper than digitising from scratch — but as a proposal only, never implemented or measured, its cost claim an unquantified impression.

## Positioning annotation (interpretive)

Not adjacent prior art but the direct upstream antecedent: the manual, cost-quantified baseline on the same Soviet map series, the same Bulgarian study area, and the same burial-mound symbol family, produced by the project ecosystem this study belongs to. The link is tighter than corpus similarity — the citing study's preregistration records that it builds on this source and that the four maps audited in its §3.5.2 are the present gold-standard corpus (preregistration.md lines 19, 260), so the novice-human operating point (about 95% recall at 99.1% precision, failure dominated by clustered omission) is measured on the very tiles the VLM is evaluated on. Its conclusion proposes the crowdsourcing-versus-automation comparison this study performs, though it envisaged training a model on the crowdsourced dataset rather than prompting a pretrained VLM; cite it as this study's own baseline and stated next step, not as an external competitor to be beaten.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "found 49 errors from a true count of 834 features, a 5.87% error rate (see Table 3). Forty-two of these errors were false negatives (symbols missed by students). Six were double-marked (Student C digitised a section of a map twice). Students made only one classification error (a similar symbol mistaken for a benchmark), and no outright false positives."
- **Locator:** page_index 8 · p.9 · §3.5.2 Digitisation errors
- **Paraphrase:** A staff audit of four randomly selected maps scored 49 errors against a true count of 834 features (5.87%), of which 42 were missed symbols, 6 were duplicate marks of one map section by a single volunteer, and one was a symbol misidentified as a benchmark. Table 3 records that single error the other way round — one false positive (Student D, 1.6%; cumulative 0.1%) and zero classification errors for every student — so the source disagrees with itself about the label, though the count of one is stable either way. Taking duplicate marks as precision-side errors, seven of the 799 recorded features were invalid, giving 99.1% precision against 94.96% recall.
- **Relevance:** § methods — gold standard; § results — human baseline · Ground-truth epistemics · **supports**

### KP2
- **Quote (verbatim):** "digitising mounds from over 20,000 sq km of Soviet military 1:50,000 topographic maps covering southeast Bulgaria, followed by ground-truthing (which continued through 2022)"
- **Locator:** page_index 1 · p.2 · §1.1 The Tundzha Regional Archaeology Project
- **Paraphrase:** The mound dataset was digitised from more than 20,000 sq km of Soviet 1:50,000 military topographic sheets covering south-east Bulgaria, and was subsequently ground-truthed in a verification campaign that ran until 2022. The source reports no ground-truthing outcomes, referring them to Valchev & Sobotkova (2019) and Sobotkova & Weissova (2020), so nothing about field-verification results can be sourced to this article.
- **Relevance:** § introduction; § data · Historical-map extraction lineage · **supports**

### KP3
- **Quote (verbatim):** "We wished to extract symbols from them that might represent burial or settlement mounds in our study area (see Fig. 2). Such symbols occurred at a high density, averaging about 200 per tile (0.5 per sq km), with counts per tile ranging from about 50 to 400. The mound symbols were moderately obtrusive; some aspects of shape or colour were shared with other map symbols."
- **Locator:** page_index 3 · p.4 · §2.1 Archaeological features in Soviet topographic maps
- **Paraphrase:** The extraction target is a symbol that may denote a burial or settlement mound, not a confirmed mound; the symbols are dense — about 200 per sheet, ranging from roughly 50 to 400, or 0.5 per sq km across tiles of about 400 sq km — and only moderately distinctive, sharing shape or colour attributes with other symbols in the map's legend.
- **Relevance:** § task definition; § error analysis · Area-segmentation to point-symbol difficulty ladder · **complicates**

### KP4
- **Quote (verbatim):** "FAIMS Mobile was used to digitise 10,827 mound features from Soviet military topographic maps. This digitisation required 241 person-hours (57 from staff; 184 from novice volunteers), with an error rate under 6%."
- **Locator:** page_index 0 · p.1 · Abstract
- **Paraphrase:** 10,827 mound features were digitised from Soviet military topographic maps for a total human cost of 241 person-hours, split 57 staff to 184 novice-volunteer hours, at an error rate below 6%. The 184 figure is the paper's own arithmetic but is not reconciled with §3.2, which totals 189.4 student-hours; on the latter the campaign costs 246.4 person-hours at 43.9 rather than 44.9 features per person-hour.
- **Relevance:** § cost analysis; § discussion · Annotation budgets · **supports**

### KP5
- **Quote (verbatim):** "a crowdsourcing approach like ours is most suitable for datasets numbering perhaps 10,000–60,000 records"
- **Locator:** page_index 9 · p.10 · §4.1.2 Machine learning versus crowdsourcing
- **Paraphrase:** The authors place the efficient operating window for novice-volunteer crowdsourcing at roughly 10,000 to 60,000 records: below which desktop GIS approaches should be considered — though they note their system can still pay off for datasets below 1,000 features where staff time is at a premium — and above which ML should be contemplated, but only where the requisite expertise is available.
- **Relevance:** § cost analysis; § discussion · Cost/accuracy trade-space · **extends**

### KP6
- **Quote (verbatim):** "Simple expedients, such as assigning multiple students to digitise the same map tiles independently or assigning one student to review work by another, would likely eliminate most errors. Even using staff time, it was much faster to check volunteer work than digitise from scratch."
- **Locator:** page_index 8 · p.9 · §3.5.2 Digitisation errors
- **Paraphrase:** The proposed remedy for the observed error profile is redundancy plus review — several annotators over the same tile, or one annotator auditing another — justified on the grounds that checking existing work costs far less than producing it afresh. Both are prospective: neither redundant digitisation nor peer review was implemented or measured in this study, and the checking-versus-digitising cost claim is an unquantified staff impression with no reported control, the only checking cost given being the 6 hours of re-examination across four maps.
- **Relevance:** § architecture rationale; § discussion · Consensus and verification architecture · **extends**

### KP7
- **Quote (verbatim):** "ML papers rarely quantify time-on-task"
- **Locator:** page_index 9 · p.10 · §4.1.2 Machine learning versus crowdsourcing
- **Paraphrase:** The machine-learning literature on map extraction seldom reports the human time its pipelines consume, which is what makes automation-versus-manual thresholds hard to establish.
- **Relevance:** § related work; § contribution statement · Cost/accuracy trade-space · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "More projects - whether they use manual or automated approaches - need to track and publish the expert and volunteer time required for setup, training, support, and quality assurance related to map digitisation, as well as digitisation speed, error rates and types"
- **Locator:** page_index 10 · p.11
- **Why:** The source's closing call is the cleanest possible warrant for reporting a measured cost/accuracy trade-space rather than accuracy alone — and because the citing study's preregistration records that it builds on this source (preregistration.md line 19), the paper can frame its cost accounting as answering a standing request from its own lineage instead of as an optional extra. The omitted tail ('the characteristics of the features being digitised, and the complexity of information extracted') would only strengthen the hook, since difficulty-ladder reporting is one of the study's contributions.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
