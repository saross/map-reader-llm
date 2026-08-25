# ISPRS Journal of Photogrammetry and Remote Sensing — requirements and observed practice

> **Last revised**: 2026-08-25 (original publication: policy extraction +
> 17-paper corpus survey, two verified agent reports). See
> [§ Changelog](#changelog) for revision history.

**Decision context**: the PI selected this journal on 2026-08-25 and
will publish open access, expecting the CAUL–Elsevier read-and-publish
agreement (Macquarie, honorary affiliation) to waive the APC.

**Provenance**: two agent extractions, both provenance-labelled.
*Policy* comes from a 2024-04-18 archived capture of the official
ScienceDirect Guide for Authors (live page bot-blocked) cross-checked
against **live** Elsevier policy pages (AI policy, artwork, CAUL —
fetched 2026-08-25); items needing a live re-check are flagged.
*Practice* comes from 17 publisher-typeset open-access Versions of
Record (16 from 2024–2026 + Wu 2023 as the nearest topical
neighbour), enumerated via Crossref/OpenAlex/Unpaywall and read as
PDFs from institutional repositories.

## 1. Stated policy (the binding layer)

- **Article type**: "Papers" (full research). **No word/page limit
  stated** for Papers (verified absent; only Perspective Papers cap
  at 4,000 words).
- **Abstract**: required; no stated length. **Keywords: max 6, in
  American spelling** (the only place US spelling is mandated; body
  may be consistently British — "American or British usage… not a
  mixture").
- **Structure**: numbered sections (1, 1.1, 1.1.1); no strict initial
  formatting ("Your Paper Your Way": single PDF, any layout, figures
  good enough to referee). Methods must "provide sufficient details to
  allow the work to be reproduced by an independent researcher".
- **Required back matter**: Declaration of competing interest (even if
  none; Elsevier .docx template uploaded separately), CRediT author
  contributions, AI declaration if applicable (below). Data statement
  *encouraged* (a claimed mandate traced to a different journal —
  unverified). Graphical abstract optional (if used: 1328 × 531 px,
  ≥300 dpi, **no general-purpose AI image tools**). Highlights only at
  final-files stage (3–5 bullets ≤85 chars).
- **Figures**: EPS/PDF vector or TIFF/JPG raster at 300 dpi (halftone)
  / 500 (combination) / 1000 (line art); RGB; state 1/1.5/2-column fit
  per figure; caption below, title not on the figure; individual files
  >10 MB separate. **Colour free online, charged in print** — choose
  online-only. Colour-blind-safe palettes recommended.
- **Tables**: editable text, never images; no vertical rules or
  shading; notes below the body.
- **References**: any consistent style at submission; DOIs "highly
  encouraged"; journal applies its author–date style at proof
  (first-alphabetical-then-chronological grouping; "et al." from three
  authors). Data citations: `[dataset]` prefix + repository, version,
  persistent identifier. LaTeX: `elsarticle.cls` + BibTeX. Remove
  reference-manager field codes.
- **AI policy** (live Elsevier policy, 2026-08-25 — supersedes the
  2024 guide text): TWO SEPARATE HOMES.
  1. **AI in the research** → the **Methods** section, "described in a
     reproducible manner… the name of the model or tool, the version
     used, and the developer". Code written/edited with AI: "declare
     this in detail in the Methods section"; same validity and
     reproducibility standards as human-written code.
  2. **AI in manuscript preparation** → a titled declaration
     immediately **before the References** (template: "During the
     preparation of this work, the author(s) used [TOOL] in order to
     [REASON]. After using this tool/service, the author(s) reviewed
     and edited the content as needed and take(s) full responsibility
     …"). Basic grammar/spelling checks need no declaration;
     substantive structural editing does.
  - Authors must keep records ("retaining logs… saving prompts and
    generated outputs") and produce them "if requested by editors" —
    the project's transcript/repo apparatus is exactly this.
  - Hard bans relevant to us: AI as author or cited author; AI
    creating/altering images representing research data;
    general-purpose AI image tools for graphical abstracts.
- **Review model**: **single-anonymised** — authors not blinded; OSF
  preregistration, the public repository, and self-citations may
  appear openly. Suggested reviewers requested at submission. Proof
  corrections due within two days.
- **Conference-extension rule**: submissions based on prior conference
  papers must be "significantly extended"; the author must describe
  the differences explicitly.
- **Open access**: hybrid; APC **USD 3,800** (rose from 3,310 in
  Jan 2026); licences CC BY or CC BY-NC-ND; subscription route free
  with a 24-month green embargo.

### Four re-check items — ALL VERIFIED by the PI on the live guide (2026-08-25)

1. **AI declaration title (current)**: "Declaration of generative AI
   and AI-assisted technologies in the **manuscript preparation
   process**" — the live-policy wording, superseding the 2024
   "writing process" title. Additional live-guide specifics: "**If
   you have nothing to disclose, you do not need to add a
   statement**"; basic grammar/spelling/reference tools exempt;
   disability-related assistive technology exempt; authors
   accountable for verifying AI output (including that "AI-generated
   references can be incorrect or fabricated") and for IP/privacy
   terms of any tool used. The journal also bars editors and
   reviewers from uploading unpublished manuscripts into generative
   AI tools.
2. **Data statement**: still "we **encourage** you" — NOT mandatory.
   We supply one anyway (differentiator, § 3).
3. **Highlights**: no requirement found anywhere on the live pages —
   likely surfaced only inside the submission system at final files.
4. **Preprints**: standard Elsevier wording, no society carve-out —
   preprints citable (marked as such, DOI given); formal publication
   preferred once it exists.

### CAUL/APC — CONFIRMED (PI, 2026-08-25)

**ISPRS JPRS is on the CAUL 2026 title list** (Elsevier, Hybrid,
Macquarie University selected — verified by the PI on the CAUL
LibGuide title list). The APC waiver applies. One operational
requirement from the CAUL page, in red: **authors must use their
institutional email address** at submission for the agreement to be
recognised — submit with the Macquarie address, not a personal one.
Page/colour fees remain excluded from the agreement (we use
online-only colour, which is free anyway).

## 2. Observed practice (17 Versions of Record, 2024–2026 + Wu 2023)

| Property | Observed | Notes |
|---|---|---|
| Printed pages | 7–18, **median 14** | 7 pp = a perspective; 18 pp/107 refs published fine |
| Body words | ~4,500–13,500, **median ~8,500** | ±5–10 % extraction tolerance |
| Abstract | 170–362 words, **median 237** | Unstructured single paragraph in 16/16; 362 was published |
| Keywords | 3–7, **median 6** | Never >7 |
| Figures | 4–19, **median 9** | Colour routine in every paper (RGB, ~300 ppi) |
| Tables | 0–15, **median 5.5** | |
| References | 39–107, **median 63** | Dataset/benchmark papers run high |

**Modal skeleton**: 1. Introduction → 2. Related work → 3. Method →
4. Experiments → [Results] → [Discussion] → Conclusion(s). Variants:
domain-science spine (Intro / Data / Methods / Results / Discussion /
Conclusions) in 3/16; a single Experiments section usually absorbs
Results (both appear in only 2/17); **a dataset/benchmark contribution
conventionally gets its own top-level section** (5/16) — relevant to
our corpus + ground truth. One paper ends at Discussion with no
Conclusion.

**Declarations observed** (n = 16): competing interest **16/16**;
CRediT **15/16** (absent only in the single-author paper);
acknowledgements 14/16 (funding usually inside them); **data
availability only 3/16**; code availability 2/16; external
supplementary 3/16; in-article appendices 4/16.

**AI disclosure in practice**: **2/16**, both verbatim Elsevier
boilerplate disclosing ChatGPT for readability only; heading wording
inconsistent between them; in one (Hou 2025) the AI and
competing-interest **headings are swapped relative to their bodies in
the published VoR** — back matter is template-driven and lightly
proofed, so we must place and check our own statements. **No paper in
the sample discloses AI as a research instrument** — we would be
setting the venue's precedent, squarely inside the live policy's
Methods-reporting provisions.

## 3. What this means for our preparation

**Targets** (practice-calibrated, none policy-capped): ~14–16 pages /
~8,500–10,000 words; abstract ~240 words, unstructured; 6 keywords
(US spelling); ~9–12 colour figures (online-only colour); ~6 tables;
~65–80 references with DOIs; CRediT + competing-interest always; **a
data AND code availability statement — only 3/16 papers have one, so
ours reads as a differentiator, and it is where the OSF/Zenodo/repo
apparatus naturally lands.**

**Structure mapping**: our outline translates cleanly — Introduction;
Related work (VLM remote sensing + historical-map extraction + the
O'Hara/GMFS cluster); a top-level corpus/ground-truth section (venue
convention for dataset contributions); Methods (the pipeline, with the
AI-as-instrument reporting per the live policy: model names, versions,
developer, the assistant's role in code per "declare in detail");
Experiments/Results; Discussion; Conclusions. The
**collaboration material goes operationalised into Methods, with the
meta-level reflection in supplementary material** — observed practice
offers no slot for a standalone reflexive section, and the nearest
successful shape is Vollmer 2025's head-to-head evaluation framing.

**Fit strategy**: precedent is solid for the *object*: **Wu,
Schindler, Heitzler & Hurni 2023 (vol. 197) — deep-learning
segmentation of historical maps — is in this exact venue**, and a
dense VLM cluster (SkyEyeGPT, RSGPT, LHRS-Bot-Nova…) is current. But
archaeology is essentially absent (one paper, 1994) — frame the
problem as **hard small-object detection on degraded scanned
cartography**, state the archaeological payoff without assuming domain
priors, and lean on the scope hooks "machine and deep learning for EO
data analysis", "innovative applications, particularly in new fields",
"interdisciplinary". A pre-submission enquiry to the EiC is a live
option; the fully-OA sister title (*ISPRS Open Journal of P&RS*, APC
~USD 1,800) is the named fallback.

## Changelog

### 2026-08-25 — Original publication

S142. Two agent extractions (policy: archived official guide +
live Elsevier pages; practice: 17 verified VoR PDFs via
Crossref/OpenAlex/Unpaywall). Both full reports are in the session
transcript; per-paper table and source URLs preserved there. The four
live-guide re-checks and the CAUL title-list confirmation are open PI
actions.
