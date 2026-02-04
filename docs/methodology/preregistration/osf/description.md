# VLM-Based Extraction of Burial Mound Symbols from Historical Soviet Topographic Maps

This project evaluates vision-language model (VLM) prompting strategies
for extracting cartographic symbols from historical maps. We use frontier
VLMs (Gemini 3 Flash/Pro, with cross-model validation on Claude 4.5 and
GPT-5.x) to detect burial mound symbols on Soviet 1:50,000 topographic
maps of Bulgaria — the same corpus used in Sobotkova et al. (2023),
which achieved approximately 6% error rates (predominantly false
negatives) using crowdsourced volunteers.

**Objectives:**

1. Determine whether few-shot VLM prompting can match crowdsourcing
   accuracy with less human effort, and match properly-validated
   traditional ML approaches (YOLO, U-Net, Faster R-CNN) with
   substantially smaller training datasets
2. Identify which prompting strategies optimise detection performance
   for specialised cartographic tasks
3. Test whether established VLM prompting recommendations generalise to
   novel detection domains

**Preregistered hypotheses:**

We test eight confirmatory hypotheses (FDR-corrected at q = 0.05) using
symbol-level F1 as the primary outcome measure. These address: text
versus image modality and elaboration level (H1); two-stage pipeline
architectures (H2); consensus voting (H3); few-shot example ordering
(H4); negative example text treatment (H5); cross-model transfer from
Flash to Pro (H6); temperature (H7); and library composition and
scaling (H8). Seven additional exploratory hypotheses examine diversity
mechanisms, training pool size, and related factors.

Preliminary development found that several commonly recommended
strategies — text minimisation, two-stage proposer–verifier pipelines —
had little effect or actively degraded performance, while consensus
voting substantially improved F1. This preregistration provides
confirmatory tests of these observations using a two-stage trial
framework: Stage 1 screens promising techniques on a 60-tile holdout
set; Stage 2 (future work) validates findings on a larger reserve
corpus.

All materials — preregistration document, prompt configurations, tile
selection manifests, analysis code, and results — will be deposited here
to support reproducibility.

**Keywords:** vision-language models, cartographic symbol detection,
historical maps, burial mounds, few-shot learning, archaeological
remote sensing, Bulgaria
