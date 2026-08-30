# AB+ — ‘But I can't preregister my research’: Improving the reproducibility and transparency of ecology and conservation with adaptive preregistration for model‐based research

| field | value |
|---|---|
| **citekey** | `gould_but_2026` |
| **full cite** | Gould, Elliot et al. (2026) *‘But I can't preregister my research’: Improving the reproducibility and transparency of ecology and conservation with adaptive preregistration for model‐based research.* Methods in Ecology and Evolution. DOI: 10.1111/2041-210x.70311 |
| **register** | Borrowed (metascience / open-science methodology, ecology and conservation) |
| **primary gap** | D.9 naming and priority: prior art for analysis-grain, data-dependent registration |
| **also touches** | Registered decision rules as procedural commitments; Deviation reporting and preregistration checking; Registry and cyberinfrastructure limits; Calibration on a subset and leakage into evaluation; Open prerequisite: read Srivastava (2018) directly to settle term occupancy |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Gould and colleagues answer their title's complaint — that iterative model development cannot be preregistered — with a methodology rather than a new concept. Term occupancy is unsettled on this source alone: they use the name "sensu Srivastava, 2018" yet also present the methodology as one they propose and name themselves, so settling it needs Srivastava (2018) read directly. Two components carry it. Registered flexibility preregisters "plans to deploy flexible strategies" — heuristics whose execution depends on earlier outcomes, with a predefined-rule decision tree as their worked instance — under three stated requirements; interim preregistrations run in parallel with the modelling, marking key phases as parts of the data are observed. Data-dependence is not itself the violation; undisclosed result-chasing is. Evidence is one case study (environmental flows, riparian vegetation, Victoria) yielding three versions, two interim and one final.

Cross-domain application is invited but untested: the abstract's "could be applied" to model-based research in other scientific disciplines, the Conclusions' "many elements of the template are relevant across fields", and nothing outside ecology tried. That cuts in our favour — an executed non-ecological instance is a stronger contribution against an aspiration than against an established extension. Their definition of model-based research — any research that uses quantitative modelling to answer its research question — admits a VLM evaluation study by the letter of the definition, though the same paragraph scopes it with statistical-modelling categories (exploration, inference, prediction; phenomenological vs. mechanistic models) and the template is built around model-development decision-steps. They set a firm limit: Adaptive Preregistration is not offered as a replacement for static preregistration, and is recommended where research involves "legitimate sequential decision-making and/or high data-model uncertainty" (their and/or: either condition suffices). Their interims are explicitly phase-based, which leaves the per-analysis grain as a real, if narrow, contrast — narrower still than it looks, since Box 1 tip 4 contemplates "sequential analysis plans ... preregistered separately for the same study with metadata linking the chain of preregistrations", and the number of interims is unbounded: grain is a continuum they already span.

What they leave unfilled is checking and infrastructure. They concede they only partially achieved their preregistration-checking aim — for local implementation reasons, not because checking is infeasible or automation the remedy. Existing registries cannot accommodate the method, GitHub meets neither FAIR archiving nor preregistration requirements, and they call for new registries or cyberinfrastructure. No mention of language models, machine learning, or automated authoring or checking appears anywhere in the extracted text (verified by search; page_index 8 carries only a running head and footer, its Figure 3 in-image text unextracted). They do cite Hofman et al. (2023), Pre-registration for predictive modelling, so this paper shows only that Gould et al. themselves do not occupy the automation cell — not that the wider literature is empty. Their reported cost is human anticipation labour: a case-study lead expected about a month's delay and found it much longer, attributing the overrun to first-time use, to feeding information back into the method while applying it, and to an unusually complex analysis — and expects it "easier and faster the next time", against offsetting savings the same table records in model coding, back-and-forth adjustment, and report writing. That is the friction the LLM-support claim addresses — framed by them as a learning cost rather than a standing one.

One hygiene contrast: their Preliminary Analysis subset was deliberately not held out — the Main Analysis dataset comprised the full dataset, including the Preliminary Analysis dataset. They name the risk themselves, conceding that "Adaptive Preregistration may increase overfitting risk compared to static preregistration due to its greater flexibility". Defensible for their inferential aim; in our setting that pattern would be calibration leakage into an F1 and MCC evaluation.

## Positioning annotation (interpretive)

The near prior art that the D.9 naming ruling turns on, read at the level of what its authors actually claim. Gould et al. occupy the term Adaptive Preregistration — which they use sensu Srivastava (2018), while also presenting the methodology as one they propose and name themselves; whether Srivastava coined the phrase needs Srivastava (2018) read directly — define it as registered flexibility plus phase-based interim preregistrations, and explicitly invite its application beyond ecology to model-based research generally, without testing it there. What they leave unoccupied is the execution side: they report only partial success at preregistration checking, say existing registries cannot host the method, and say nothing about LLM- or automation-supported authoring — which leaves the paper's cleanest novelty claim standing against this source, though not, on this source alone, against the wider literature.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "We propose a methodology for implementing an expanded view of preregistration called 'Adaptive Preregistration' (sensu Srivastava, 2018)"
- **Locator:** page_index 2 · p.3 · §1 Introduction
- **Paraphrase:** They present a methodology for putting into practice an expanded conception of preregistration that they call Adaptive Preregistration, using the term in the sense of Srivastava (2018); the paper elsewhere describes the methodology as one "we call" Adaptive Preregistration, and credits Srivastava specifically with registered flexibility and interim preregistrations rather than with the phrase.
- **Relevance:** §D.9 preregistration retrospective — naming ruling · D.9 naming: term occupancy, unsettled on this source alone · **complicates**

### KP2
- **Quote (verbatim):** "The modeller follows an iterative process of preregistration in parallel with modelling, consisting of interim preregistrations that mark key phases of modelling and analysis as different parts of the data are observed"
- **Locator:** page_index 4 · p.5 · §2.4.2 Interim preregistrations
- **Paraphrase:** Interim preregistrations are written alongside the modelling as it proceeds, each one marking a key phase of the work as successive parts of the data come into view; the source sentence credits this component to Srivastava (2018), and sets no upper bound on the number of interims.
- **Relevance:** §D.9 — contrast between phase-based interims and per-analysis registrations · D.9 naming: granularity of the registration unit · **complicates**

### KP3
- **Quote (verbatim):** "a modeller can preregister a decision-tree that consists of predefined rules about when a particular modelling strategy or decision should be implemented"
- **Locator:** page_index 4 · p.5 · §2.4.1 Registered flexibility
- **Paraphrase:** Registered flexibility includes committing in advance to a decision tree whose predefined rules say which modelling strategy fires under which observed outcome; the tree is the worked example they give for the broader definition, preregistration of "plans to deploy flexible strategies".
- **Relevance:** §D.9 — the lean upfront layer of procedural rules · Registered decision rules as procedural commitments · **supports**

### KP4
- **Quote (verbatim):** "The key distinction is not whether decisions are data-dependent, but whether they are systematic (following preregistered decision rules) versus opportunistic"
- **Locator:** page_index 2 · p.3 · §1 Introduction
- **Paraphrase:** Whether a decision depends on the data is not what makes it a questionable practice; the line falls between decisions taken under preregistered rules and decisions that chase a result without disclosing it — the source glosses "opportunistic" as result-seeking without disclosure, so disclosure is part of what legitimates a data-dependent choice.
- **Relevance:** §D.9 — justification for outcome-blind rules governing data-dependent choices · Systematic versus opportunistic data-dependence · **supports**

### KP5
- **Quote (verbatim):** "Although we focus on ecology and conservation in this paper, the concept of Adaptive Preregistration, and the templates developed here, could be applied to model-based research in other scientific disciplines."
- **Locator:** page_index 0 · p.1 · Abstract, point 4
- **Paraphrase:** The authors state that the concept and templates "could be applied" to model-based research in other disciplines — a hedged possibility, not demonstrated: no non-ecological application is tested.
- **Relevance:** §D.9 — whether a computational-evaluation instance is a distinct contribution · Cross-domain applicability asserted but untested · **complicates**

### KP6
- **Quote (verbatim):** "We emphasise that Adaptive Preregistration is not intended to replace static preregistration for research that can be adequately served by existing static approaches."
- **Locator:** page_index 13 · p.14 · §4.1 When is Adaptive Preregistration useful?
- **Paraphrase:** Adaptive Preregistration is positioned as a supplement for cases static preregistration cannot serve, not as a general replacement for it.
- **Relevance:** §D.9 — the lean-upfront-plus-just-in-time recipe as a hybrid, not a rejection of static registration · Scope limit on when adaptive registration is warranted · **complicates**

### KP7
- **Quote (verbatim):** "Consequently, we only partially achieved our aim of facilitating preregistration checking."
- **Locator:** page_index 13 · p.14 · §4.2 Difficulties encountered using Adaptive Preregistration in our case study
- **Paraphrase:** By their own assessment the second of their two aims, making the preregistration checkable against what was actually done, was met only in part — a shortfall they attribute to local features of their own implementation, not to any claim that checking is intrinsically infeasible or that automation is the remedy.
- **Relevance:** §D.9 — where the LLM-supported execution claim sits relative to prior art · The open cell: checkable execution and LLM support · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "Any first attempt to implement Adaptive Preregistration is unlikely to work perfectly, there will be mistakes and details that are omitted. Being upfront about this in study reporting is still better than avoiding preregistration entirely."
- **Locator:** page_index 14 · p.15
- **Why:** An epigraph, from the incumbent's own guidance, for D.9's deviation-reporting stance: it licenses a candid retrospective on where our registration was underspecified without conceding that the registration was worthless.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
